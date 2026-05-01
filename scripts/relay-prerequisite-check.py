#!/usr/bin/env python3
"""
relay-prerequisite-check.py
Phase 0 prerequisite validation — runs before /relay:start allows Phase 1.

Checks:
    1. CLI tools: pac, az, dotnet, python, git, node, bash, jq, pwsh
  2. PAC auth: at least one active profile
  3. Azure CLI: logged in (az account show)
  4. Relay skills: all skills/*/SKILL.md present
  5. Copilot CLI plugins (if running in CLI): canvas-apps, model-apps,
     power-pages, code-apps-preview
  6. MCP servers: Dataverse MCP reachable (VS Code mcp.json or CLI mcp list)

Exit codes:
  0 = all prerequisites met
  1 = one or more prerequisites missing (prints remediation steps)

Usage:
  python scripts/relay-prerequisite-check.py
  python scripts/relay-prerequisite-check.py --fix          # attempt auto-install
  python scripts/relay-prerequisite-check.py --json         # machine-readable output
  python scripts/relay-prerequisite-check.py --skip-mcp     # skip MCP server check
  python scripts/relay-prerequisite-check.py --skip-plugins # skip plugin check
"""

import glob
import json
import os
import platform
import shutil
import subprocess
import sys
import argparse
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

REQUIRED_CLI_TOOLS = {
    "pac": {
        "min_version": "2.6",
        "install_hint": "https://learn.microsoft.com/en-us/power-platform/developer/cli/introduction#install-microsoft-power-platform-cli",
        "critical": True,
        "win_fallback_globs": [
            os.path.join(os.environ.get("LOCALAPPDATA", ""), "Microsoft", "PowerAppsCLI", "**", "pac.exe"),
        ],
    },
    "az": {
        "min_version": None,
        "install_hint": "https://learn.microsoft.com/en-us/cli/azure/install-azure-cli",
        "critical": True,
        "win_fallback_globs": [
            os.path.join(os.environ.get("PROGRAMFILES", ""), "Microsoft SDKs", "Azure", "CLI2", "wbin", "az.cmd"),
        ],
    },
    "dotnet": {
        "min_version": "6.0",
        "install_hint": "https://dotnet.microsoft.com/download",
        "critical": True,
        "win_fallback_globs": [],
    },
    "python": {
        "min_version": "3.8",
        "install_hint": "https://www.python.org/downloads/",
        "critical": True,
        "win_fallback_globs": [],
    },
    "git": {
        "min_version": None,
        "install_hint": "https://git-scm.com/downloads",
        "critical": False,
        "win_fallback_globs": [],
    },
    "node": {
        "min_version": None,
        "install_hint": "https://nodejs.org/",
        "critical": False,
        "win_fallback_globs": [],
    },
    "bash": {
        "min_version": None,
        "install_hint": "Install Git Bash or enable WSL on Windows",
        "critical": True,
        "win_fallback_globs": [
            os.path.join(os.environ.get("PROGRAMFILES", ""), "Git", "bin", "bash.exe"),
        ],
    },
    "jq": {
        "min_version": None,
        "install_hint": "winget install jqlang.jq",
        "critical": True,
        "win_fallback_globs": [],
    },
    "pwsh": {
        "min_version": "7.0",
        "install_hint": "https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell-on-windows",
        "critical": True,
        "win_fallback_globs": [
            os.path.join(os.environ.get("PROGRAMFILES", ""), "PowerShell", "**", "pwsh.exe"),
        ],
    },
}

REQUIRED_SKILLS = [
    "canvas-app-design-patterns",
    "canvas-app-design-reading",
    "canvas-app-enterprise-layout",
    "playwright-testing",
    "power-fx-patterns",
    "power-platform-alm",
    "power-platform-footgun-checklist",
    "power-platform-security-patterns",
    "relay-debugging",
    "relay-discovery",
    "relay-orchestration",
    "relay-parallel-agents",
    "relay-planning",
    "relay-verification",
    "relay-workflow",
]

REQUIRED_PLUGINS = [
    "canvas-apps",
    "model-apps",
    "power-pages",
    "code-apps-preview",
]

LOG_PATH = ".relay/execution-log.jsonl"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def run_cmd(cmd, timeout=15):
    """Run a command, return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=(platform.system() == "Windows"),
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except FileNotFoundError:
        return -1, "", "command not found"
    except subprocess.TimeoutExpired:
        return -2, "", "timed out"


def parse_version(version_str):
    """Extract (major, minor) tuple from a version string like '2.6.4' or 'Python 3.13.13'."""
    import re

    match = re.search(r"(\d+)\.(\d+)", version_str)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    return (0, 0)


def parse_min_version(version_str):
    """Parse a minimum version requirement like '3.8' or '2.6' into a tuple."""
    parts = version_str.split(".")
    return (int(parts[0]), int(parts[1]) if len(parts) > 1 else 0)


def log_event(event, details=None):
    """Append to execution log if .relay/ exists."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": "conductor",
        "event": event,
        "phase": "0",
    }
    if details:
        entry.update(details)
    log_dir = os.path.dirname(LOG_PATH)
    if os.path.isdir(log_dir):
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")


def load_json_file(path, description):
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {description} at line {e.lineno}, column {e.colno}: {e.msg}") from e
    except OSError as e:
        raise ValueError(f"Could not read {description}: {e}") from e


# ---------------------------------------------------------------------------
# Check functions
# ---------------------------------------------------------------------------


def check_cli_tools():
    """Check that required CLI tools are installed and meet minimum versions."""
    results = []
    for tool, spec in REQUIRED_CLI_TOOLS.items():
        path = shutil.which(tool)
        if not path:
            # On Windows, try common suffixes
            if platform.system() == "Windows":
                for suffix in [".exe", ".cmd", ".bat"]:
                    path = shutil.which(tool + suffix)
                    if path:
                        break
        if not path and platform.system() == "Windows":
            # Try well-known Windows install paths via glob
            for pattern in spec.get("win_fallback_globs", []):
                matches = glob.glob(pattern, recursive=True)
                if matches:
                    # Pick the newest (last sorted) match
                    path = sorted(matches)[-1]
                    break
        if not path:
            results.append({
                "check": f"cli:{tool}",
                "status": "FAIL",
                "message": f"`{tool}` not found on PATH",
                "remediation": spec["install_hint"],
                "critical": spec["critical"],
            })
            continue

        # Version check
        version_ok = True
        detected_version = ""
        if spec["min_version"]:
            rc, out, err = run_cmd([path, "--version"])
            version_text = out or err
            # Search all lines for version number (pac puts it on line 2)
            detected_version = ""
            ver = (0, 0)
            for line in (version_text or "").split("\n"):
                candidate = parse_version(line)
                if candidate > (0, 0):
                    detected_version = line.strip()
                    ver = candidate
                    break
            min_ver = parse_min_version(spec["min_version"])
            if ver < min_ver:
                version_ok = False

        if version_ok:
            results.append({
                "check": f"cli:{tool}",
                "status": "PASS",
                "message": f"`{tool}` found at {path}" + (f" ({detected_version})" if detected_version else ""),
                "critical": spec["critical"],
            })
        else:
            results.append({
                "check": f"cli:{tool}",
                "status": "FAIL",
                "message": f"`{tool}` version {detected_version} < required {spec['min_version']}",
                "remediation": spec["install_hint"],
                "critical": spec["critical"],
            })

    return results


def _find_tool(name):
    """Find a tool on PATH or in well-known Windows install paths."""
    path = shutil.which(name)
    if not path and platform.system() == "Windows":
        for suffix in [".exe", ".cmd", ".bat"]:
            path = shutil.which(name + suffix)
            if path:
                break
    if not path and platform.system() == "Windows":
        spec = REQUIRED_CLI_TOOLS.get(name, {})
        for pattern in spec.get("win_fallback_globs", []):
            matches = glob.glob(pattern, recursive=True)
            if matches:
                path = sorted(matches)[-1]
                break
    return path


def check_pac_auth():
    """Check that PAC has at least one active auth profile."""
    pac = _find_tool("pac")
    if not pac:
        return [{
            "check": "pac:auth",
            "status": "SKIP",
            "message": "pac not found — skipping auth check",
            "critical": True,
        }]

    rc, out, err = run_cmd([pac, "auth", "list"])
    if rc != 0:
        return [{
            "check": "pac:auth",
            "status": "FAIL",
            "message": f"pac auth list failed: {err}",
            "remediation": "Run `pac auth create --environment <url>` to authenticate",
            "critical": True,
        }]

    # Check for at least one line with an asterisk (*) indicating active profile
    lines = out.split("\n")
    active = [l for l in lines if "*" in l]
    if active:
        # Extract profile name from the active line
        profile_info = active[0].strip()
        return [{
            "check": "pac:auth",
            "status": "PASS",
            "message": f"Active PAC profile: {profile_info}",
            "critical": True,
        }]
    else:
        return [{
            "check": "pac:auth",
            "status": "FAIL",
            "message": "No active PAC auth profile found",
            "remediation": "Run `pac auth create --environment <url>` then `pac auth select --index <n>`",
            "critical": True,
        }]


def check_az_login():
    """Check Azure CLI is logged in."""
    az = _find_tool("az")
    if not az:
        return [{
            "check": "az:login",
            "status": "SKIP",
            "message": "az not found — skipping login check",
            "critical": True,
        }]

    rc, out, err = run_cmd([az, "account", "show", "--output", "json"])
    if rc != 0:
        return [{
            "check": "az:login",
            "status": "FAIL",
            "message": "Not logged in to Azure CLI",
            "remediation": "Run `az login` to authenticate",
            "critical": True,
        }]

    try:
        account = json.loads(out)
        tenant = account.get("tenantId", "unknown")
        user = account.get("user", {}).get("name", "unknown")
        return [{
            "check": "az:login",
            "status": "PASS",
            "message": f"Logged in as {user} (tenant {tenant})",
            "critical": True,
        }]
    except json.JSONDecodeError:
        return [{
            "check": "az:login",
            "status": "WARN",
            "message": "az account show returned non-JSON output",
            "critical": True,
        }]


def check_skills(relay_root=None):
    """Check that all required SKILL.md files exist."""
    results = []

    # Try to find the skills/ directory
    search_paths = []
    if relay_root:
        search_paths.append(Path(relay_root) / "skills")
    # Check common locations
    search_paths.append(Path("skills"))
    # Check parent if we're in a sandbox
    search_paths.append(Path("..") / "skills")
    search_paths.append(Path("../..") / "skills")

    skills_dir = None
    for p in search_paths:
        if p.is_dir():
            skills_dir = p.resolve()
            break

    if not skills_dir:
        return [{
            "check": "skills:directory",
            "status": "FAIL",
            "message": "skills/ directory not found",
            "remediation": "Ensure you are running from the Relay plugin root or a project within it",
            "critical": False,
        }]

    missing = []
    found = []
    for skill_name in REQUIRED_SKILLS:
        skill_file = skills_dir / skill_name / "SKILL.md"
        if skill_file.is_file():
            found.append(skill_name)
        else:
            missing.append(skill_name)

    if missing:
        results.append({
            "check": "skills:files",
            "status": "FAIL",
            "message": f"{len(missing)} skill(s) missing: {', '.join(missing)}",
            "remediation": "Re-clone the Relay plugin or restore missing skill folders",
            "critical": False,
        })
    else:
        results.append({
            "check": "skills:files",
            "status": "PASS",
            "message": f"All {len(found)} required skills present in {skills_dir}",
            "critical": False,
        })

    return results


def check_copilot_plugins():
    """Check Copilot CLI plugins (best-effort — only works in Copilot CLI context)."""
    results = []

    # Try `copilot plugin list`
    copilot = shutil.which("copilot") or shutil.which("copilot.exe")
    if not copilot:
        return [{
            "check": "plugins:copilot-cli",
            "status": "SKIP",
            "message": "copilot CLI not found — plugin check skipped (OK if running in VS Code)",
            "critical": False,
        }]

    rc, out, err = run_cmd([copilot, "plugin", "list"], timeout=30)
    if rc != 0:
        return [{
            "check": "plugins:copilot-cli",
            "status": "WARN",
            "message": f"copilot plugin list failed: {err[:200]}",
            "remediation": "Ensure Copilot CLI is authenticated and try again",
            "critical": False,
        }]

    # Parse output for required plugins
    out_lower = out.lower()
    missing = []
    found = []
    for plugin in REQUIRED_PLUGINS:
        if plugin.lower() in out_lower:
            found.append(plugin)
        else:
            missing.append(plugin)

    if missing:
        install_cmds = "\n".join(
            f"  copilot plugin install {p}@power-platform-skills" for p in missing
        )
        results.append({
            "check": "plugins:power-platform",
            "status": "FAIL",
            "message": f"Missing Copilot CLI plugins: {', '.join(missing)}",
            "remediation": (
                f"Run:\n  copilot plugin marketplace add microsoft/power-platform-skills\n{install_cmds}"
            ),
            "critical": False,
        })
    else:
        results.append({
            "check": "plugins:power-platform",
            "status": "PASS",
            "message": f"All {len(found)} Power Platform plugins installed",
            "critical": False,
        })

    # Check for relay plugin
    if "relay" in out_lower:
        results.append({
            "check": "plugins:relay",
            "status": "PASS",
            "message": "Relay plugin installed",
            "critical": False,
        })
    else:
        results.append({
            "check": "plugins:relay",
            "status": "WARN",
            "message": "Relay plugin not detected in copilot plugin list",
            "remediation": "Run: copilot plugin install relay",
            "critical": False,
        })

    return results


def check_mcp_servers(skip=False):
    """Check Dataverse MCP is configured (VS Code mcp.json and/or CLI mcp config)."""
    if skip:
        return [{
            "check": "mcp:dataverse",
            "status": "SKIP",
            "message": "MCP check skipped (--skip-mcp)",
            "critical": False,
        }]

    results = []
    found_any = False

    # Check VS Code mcp.json
    if platform.system() == "Windows":
        mcp_json_path = Path(os.environ.get("APPDATA", "")) / "Code" / "User" / "mcp.json"
    elif platform.system() == "Darwin":
        mcp_json_path = Path.home() / "Library" / "Application Support" / "Code" / "User" / "mcp.json"
    else:
        mcp_json_path = Path.home() / ".config" / "Code" / "User" / "mcp.json"

    if mcp_json_path.is_file():
        try:
            mcp_config = load_json_file(mcp_json_path, str(mcp_json_path))
            servers = mcp_config.get("servers", {})
            # Look for a Dataverse server (any key with crm*.dynamics.com or /api/mcp in URL)
            dv_servers = []
            for name, cfg in servers.items():
                url = cfg.get("url", "") if isinstance(cfg, dict) else ""
                if "dynamics.com" in url or "api/mcp" in url:
                    dv_servers.append(f"{name} → {url}")

            if dv_servers:
                found_any = True
                results.append({
                    "check": "mcp:vscode",
                    "status": "PASS",
                    "message": f"VS Code MCP Dataverse server(s): {'; '.join(dv_servers)}",
                    "critical": False,
                })
            else:
                results.append({
                    "check": "mcp:vscode",
                    "status": "FAIL",
                    "message": f"VS Code mcp.json exists at {mcp_json_path} but no Dataverse server found",
                    "remediation": (
                        'Add to mcp.json: { "servers": { "dataverse": '
                        '{ "type": "http", "url": "https://<org>.crm.dynamics.com/api/mcp" } } }'
                    ),
                    "critical": False,
                })
        except ValueError as e:
            results.append({
                "check": "mcp:vscode",
                "status": "WARN",
                "message": f"Could not parse {mcp_json_path}: {e}",
                "critical": False,
            })
    else:
        results.append({
            "check": "mcp:vscode",
            "status": "WARN",
            "message": f"VS Code mcp.json not found at {mcp_json_path}",
            "remediation": (
                'Create mcp.json with: { "servers": { "dataverse": '
                '{ "type": "http", "url": "https://<org>.crm.dynamics.com/api/mcp" } } }'
            ),
            "critical": False,
        })

    # Check Copilot CLI MCP config
    cli_mcp_path = Path.home() / ".copilot" / "mcp-config.json"
    if cli_mcp_path.is_file():
        try:
            cli_config = load_json_file(cli_mcp_path, str(cli_mcp_path))
            servers = cli_config.get("servers", cli_config.get("mcpServers", {}))
            dv_cli = []
            for name, cfg in servers.items():
                url = cfg.get("url", "") if isinstance(cfg, dict) else ""
                if "dynamics.com" in url or "api/mcp" in url:
                    dv_cli.append(f"{name} → {url}")
            if dv_cli:
                found_any = True
                results.append({
                    "check": "mcp:cli",
                    "status": "PASS",
                    "message": f"Copilot CLI MCP Dataverse server(s): {'; '.join(dv_cli)}",
                    "critical": False,
                })
            else:
                results.append({
                    "check": "mcp:cli",
                    "status": "WARN",
                    "message": f"CLI mcp-config.json exists but no Dataverse server found",
                    "remediation": "Run: copilot mcp add --transport http dataverse https://<org>.crm.dynamics.com/api/mcp",
                    "critical": False,
                })
        except ValueError as e:
            results.append({
                "check": "mcp:cli",
                "status": "WARN",
                "message": f"Could not parse {cli_mcp_path}: {e}",
                "critical": False,
            })

    if not found_any:
        results.append({
            "check": "mcp:dataverse",
            "status": "FAIL",
            "message": "No Dataverse MCP server configured in any surface",
            "remediation": (
                "For VS Code: add to %APPDATA%/Code/User/mcp.json\n"
                "For CLI: copilot mcp add --transport http dataverse https://<org>.crm.dynamics.com/api/mcp\n"
                "Prerequisite: enable 'Allow MCP clients' in PPAC > Environment > Settings > Features"
            ),
            "critical": False,
        })

    return results


def attempt_auto_fix(failures):
    """Attempt to auto-install missing prerequisites. Returns list of fix results."""
    fixes = []

    for item in failures:
        check = item["check"]

        if check == "plugins:power-platform":
            # Try to install missing plugins
            copilot = shutil.which("copilot") or shutil.which("copilot.exe")
            if not copilot:
                fixes.append({"check": check, "action": "skip", "message": "copilot not on PATH"})
                continue

            # First ensure marketplace is added
            run_cmd([copilot, "plugin", "marketplace", "add", "microsoft/power-platform-skills"], timeout=30)

            for plugin in REQUIRED_PLUGINS:
                if plugin.lower() in item["message"].lower():
                    rc, out, err = run_cmd(
                        [copilot, "plugin", "install", f"{plugin}@power-platform-skills"],
                        timeout=60,
                    )
                    if rc == 0:
                        fixes.append({"check": check, "action": f"installed {plugin}", "status": "OK"})
                    else:
                        fixes.append({"check": check, "action": f"install {plugin} failed", "message": err[:200]})

        elif check == "cli:dotnet":
            # Can't auto-install dotnet, just suggest
            fixes.append({
                "check": check,
                "action": "skip",
                "message": "dotnet must be installed manually: https://dotnet.microsoft.com/download",
            })

    return fixes


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Relay Phase 0 prerequisite check")
    parser.add_argument("--fix", action="store_true", help="Attempt auto-install of missing prerequisites")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--skip-mcp", action="store_true", help="Skip MCP server checks")
    parser.add_argument("--skip-plugins", action="store_true", help="Skip Copilot CLI plugin checks")
    parser.add_argument("--relay-root", default=None, help="Path to Relay plugin root (for skills check)")
    args = parser.parse_args()

    all_results = []

    # 1. CLI tools
    all_results.extend(check_cli_tools())

    # 2. PAC auth
    all_results.extend(check_pac_auth())

    # 3. Azure CLI login
    all_results.extend(check_az_login())

    # 4. Skills
    all_results.extend(check_skills(relay_root=args.relay_root))

    # 5. Copilot CLI plugins
    if not args.skip_plugins:
        all_results.extend(check_copilot_plugins())
    else:
        all_results.append({
            "check": "plugins",
            "status": "SKIP",
            "message": "Plugin check skipped (--skip-plugins)",
            "critical": False,
        })

    # 6. MCP servers
    all_results.extend(check_mcp_servers(skip=args.skip_mcp))

    # Classify results
    passes = [r for r in all_results if r["status"] == "PASS"]
    fails = [r for r in all_results if r["status"] == "FAIL"]
    warns = [r for r in all_results if r["status"] == "WARN"]
    skips = [r for r in all_results if r["status"] == "SKIP"]

    critical_fails = [r for r in fails if r.get("critical")]
    non_critical_fails = [r for r in fails if not r.get("critical")]

    # Auto-fix if requested
    fix_results = []
    if args.fix and fails:
        fix_results = attempt_auto_fix(fails)

    # Output
    if args.json:
        output = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "results": all_results,
            "summary": {
                "total": len(all_results),
                "pass": len(passes),
                "fail": len(fails),
                "warn": len(warns),
                "skip": len(skips),
                "critical_fail": len(critical_fails),
            },
            "gate": "PASS" if not critical_fails else "FAIL",
        }
        if fix_results:
            output["fix_results"] = fix_results
        print(json.dumps(output, indent=2))
    else:
        print("=" * 60)
        print("  RELAY PREREQUISITE CHECK  (Phase 0)")
        print("=" * 60)
        print()

        for r in all_results:
            icon = {"PASS": "✓", "FAIL": "✗", "WARN": "!", "SKIP": "-"}.get(r["status"], "?")
            crit = " [CRITICAL]" if r.get("critical") and r["status"] == "FAIL" else ""
            print(f"  [{icon}] {r['check']}: {r['message']}{crit}")
            if r.get("remediation") and r["status"] in ("FAIL", "WARN"):
                for line in r["remediation"].split("\n"):
                    print(f"      → {line}")
            print()

        if fix_results:
            print("-" * 60)
            print("  AUTO-FIX RESULTS")
            print("-" * 60)
            for fr in fix_results:
                print(f"  {fr['check']}: {fr.get('action', '')} — {fr.get('message', fr.get('status', ''))}")
            print()

        print("-" * 60)
        total = len(all_results)
        print(f"  PASS: {len(passes)}/{total}  |  FAIL: {len(fails)}  |  WARN: {len(warns)}  |  SKIP: {len(skips)}")

        if critical_fails:
            print()
            print(f"  *** GATE BLOCKED — {len(critical_fails)} critical failure(s) must be resolved ***")
            print()
            for cf in critical_fails:
                print(f"    • {cf['check']}: {cf['message']}")
                if cf.get("remediation"):
                    for line in cf["remediation"].split("\n"):
                        print(f"      → {line}")
            print()
            print("  Fix the critical issues above before running /relay:start.")
        elif non_critical_fails:
            print()
            print(f"  GATE PASSED with {len(non_critical_fails)} non-critical warning(s).")
            print("  Relay will work but some automation features may be limited.")
        else:
            print()
            print("  ✓ ALL PREREQUISITES MET — ready to start a Relay project.")

        print("=" * 60)

    # Log the result
    log_event("prerequisite_check", {
        "pass_count": len(passes),
        "fail_count": len(fails),
        "critical_fail_count": len(critical_fails),
        "gate": "PASS" if not critical_fails else "FAIL",
    })

    # Exit code
    if critical_fails:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

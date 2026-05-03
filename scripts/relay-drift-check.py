#!/usr/bin/env python3
"""
relay-drift-check.py
Compares plan-index.json (what was planned) against actual Dataverse artifacts (what was built).
Run by Sentinel during Phase 6 verification.

Requires:
  - .relay/plan-index.json
  - PAC CLI authenticated to the correct environment
  - Dataverse MCP or direct API access

Usage:
  python relay-drift-check.py --env https://<org>.crm.dynamics.com
"""

import json
import subprocess
import sys
import os
import argparse
import re
import tempfile
from datetime import datetime, timezone

PLAN_INDEX_PATH = ".relay/plan-index.json"
LOG_PATH = ".relay/execution-log.jsonl"
DRIFT_REPORT_PATH = "docs/drift-report.md"

ENV_URL_PATTERN = re.compile(r"https://[A-Za-z0-9][A-Za-z0-9.-]*")
IDENTIFIER_PATTERN = re.compile(r"[A-Za-z0-9_.-]+")


def load_plan_index():
    if not os.path.exists(PLAN_INDEX_PATH):
        print(f"ERROR: {PLAN_INDEX_PATH} not found")
        sys.exit(1)
    try:
        with open(PLAN_INDEX_PATH, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {PLAN_INDEX_PATH} at line {e.lineno}, column {e.colno}: {e.msg}")
        sys.exit(1)
    except OSError as e:
        print(f"Error: Could not read {PLAN_INDEX_PATH}: {e}")
        sys.exit(1)


def log_event(agent, event, details=None):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent,
        "event": event,
    }
    if details:
        entry.update(details)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def atomic_write_text(path, content):
    directory = os.path.dirname(path) or "."
    os.makedirs(directory, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile("w", delete=False, dir=directory, encoding="utf-8") as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        os.replace(temp_path, path)
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


def atomic_write_json(path, data):
    atomic_write_text(path, json.dumps(data, indent=2))


def quote_powershell_arg(value):
    return "'" + str(value).replace("'", "''") + "'"


def sanitize_env_url(env_url):
    if not ENV_URL_PATTERN.fullmatch(env_url):
        raise ValueError(f"Invalid environment URL: {env_url}")
    return env_url


def sanitize_identifier(value, field_name):
    if not value:
        raise ValueError(f"Missing {field_name}")
    if not IDENTIFIER_PATTERN.fullmatch(value):
        raise ValueError(f"Invalid {field_name}: {value}")
    return value


def run_pac(args):
    """Run a PAC CLI command via PowerShell and return output."""
    command = "pac " + " ".join(quote_powershell_arg(arg) for arg in args)
    result = subprocess.run(["pwsh", "-NoProfile", "-Command", command], capture_output=True, text=True, shell=False)
    return result.stdout.strip(), result.returncode


def get_actual_tables(env_url, solution):
    """Get tables actually deployed in the solution with column counts."""
    if not solution:
        return {}

    safe_env_url = sanitize_env_url(env_url)
    safe_solution = sanitize_identifier(solution, "solution name")
    stdout, code = run_pac(["dataverse", "table", "list", "--environment", safe_env_url, "--solution", safe_solution, "--json"])
    if code != 0:
        return {}
    try:
        data = json.loads(stdout)
        return {t.get("LogicalName", "").lower(): t for t in data}
    except Exception as e:
        print(f"Error: {e}")
        return {}


def get_actual_column_count(env_url, table_name):
    """Get the number of custom columns on a table (excludes system columns)."""
    safe_env_url = sanitize_env_url(env_url)
    safe_table_name = sanitize_identifier(table_name, "table name")
    stdout, code = run_pac(["dataverse", "column", "list", "--environment", safe_env_url, "--table", safe_table_name, "--json"])
    if code != 0:
        return None
    try:
        data = json.loads(stdout)
        # Count only custom columns (not system ones)
        custom_cols = [c for c in data if not c.get("IsManaged", True) or c.get("IsCustomAttribute", False)]
        return len(custom_cols)
    except Exception as e:
        print(f"Error: {e}")
        return None


def get_actual_flows(env_url):
    """Get cloud flows in the environment."""
    safe_env_url = sanitize_env_url(env_url)
    stdout, code = run_pac(["flow", "list", "--environment", safe_env_url, "--json"])
    if code != 0:
        return []
    try:
        data = json.loads(stdout)
        return [f.get("displayName", "").lower() for f in data]
    except Exception as e:
        print(f"Error: {e}")
        return []


def get_actual_security_roles(env_url):
    """Get custom security roles."""
    safe_env_url = sanitize_env_url(env_url)
    stdout, code = run_pac(["admin", "list-role", "--environment", safe_env_url])
    if code != 0:
        return []
    lines = stdout.split("\n")
    return [l.strip().lower() for l in lines if l.strip() and not l.startswith("Name")]


def drift_check(plan_index, env_url):
    drift_items = []
    passed_items = []

    solution = plan_index["project"].get("solution", "")
    components = plan_index["components"]

    # --- Tables (existence + column count) ---
    planned_tables = [t for t in components.get("tables", []) if "logical_name" in t]
    if planned_tables:
        actual_tables = get_actual_tables(env_url, solution)
        for table in planned_tables:
            table_name = table["logical_name"].lower()
            planned_cols = table.get("columns", 0)

            # Check 1: table exists
            if actual_tables and table_name not in actual_tables:
                drift_items.append({
                    "type": "table",
                    "name": table_name,
                    "issue": "planned but not found in Dataverse"
                })
                continue

            passed_items.append({"type": "table", "name": table_name, "status": "found"})

            # Check 2: column count (if plan specifies one)
            if planned_cols > 0:
                actual_cols = get_actual_column_count(env_url, table_name)
                if actual_cols is not None:
                    # Allow ±1 tolerance for auto-created system columns
                    if actual_cols < planned_cols - 1:
                        drift_items.append({
                            "type": "table_columns",
                            "name": table_name,
                            "issue": f"column count mismatch — planned: {planned_cols}, actual: {actual_cols} (missing {planned_cols - actual_cols} columns)"
                        })
                    else:
                        passed_items.append({
                            "type": "table_columns",
                            "name": table_name,
                            "status": f"columns ok ({actual_cols}/{planned_cols})"
                        })

    # --- Flows ---
    planned_flows = [f["name"].lower() for f in components.get("flows", []) if "name" in f]
    if planned_flows:
        actual_flows = get_actual_flows(env_url)
        for flow in planned_flows:
            if actual_flows and flow not in actual_flows:
                drift_items.append({"type": "flow", "name": flow, "issue": "planned but not found"})
            else:
                passed_items.append({"type": "flow", "name": flow, "status": "found"})

    # --- Security Roles ---
    planned_roles = [r["name"].lower() for r in components.get("security_roles", []) if "name" in r]
    if planned_roles:
        actual_roles = get_actual_security_roles(env_url)
        for role in planned_roles:
            if actual_roles and not any(role in r for r in actual_roles):
                drift_items.append({"type": "security_role", "name": role, "issue": "planned but not found"})
            else:
                passed_items.append({"type": "security_role", "name": role, "status": "found"})

    return drift_items, passed_items


def write_drift_report(drift_items, passed_items):
    lines = [f"# Drift Report\nGenerated: {datetime.now(timezone.utc).isoformat()}\n"]

    if not drift_items:
        lines.append("## [PASS] No drift detected\nAll planned components found in the built solution.\n")
    else:
        lines.append(f"## [BLOCK] Drift detected - {len(drift_items)} component(s) missing\n")
        lines.append("| Type | Name | Issue |\n|---|---|---|")
        for item in drift_items:
            lines.append(f"| {item['type']} | {item['name']} | {item['issue']} |")
        lines.append("")

    lines.append(f"## [PASS] Verified - {len(passed_items)} component(s) confirmed\n")
    lines.append("| Type | Name | Status |\n|---|---|---|")
    for item in passed_items:
        lines.append(f"| {item['type']} | {item['name']} | {item['status']} |")

    atomic_write_text(DRIFT_REPORT_PATH, "\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Relay drift detector")
    parser.add_argument("--env", required=True, help="Dataverse environment URL")
    args = parser.parse_args()

    pi = load_plan_index()
    print(f"\n[INFO] Running drift detection against {args.env}...")

    drift_items, passed_items = drift_check(pi, args.env)
    write_drift_report(drift_items, passed_items)

    # Update plan-index
    gate = pi["phase_gates"]["phase6_verify"]
    gate["drift_detected"] = len(drift_items) > 0
    gate["drift_items"] = [f"{d['type']}:{d['name']}" for d in drift_items]

    atomic_write_json(PLAN_INDEX_PATH, pi)

    if drift_items:
        print(f"\n[BLOCK] DRIFT DETECTED - {len(drift_items)} component(s) missing:")
        for d in drift_items:
            print(f"  [FAIL] {d['type']}: {d['name']} - {d['issue']}")
        log_event("sentinel", "drift_detected", {"items": drift_items})
        sys.exit(1)
    else:
        print(f"\n[PASS] NO DRIFT - {len(passed_items)} component(s) verified")
        log_event("sentinel", "drift_clear", {"verified": len(passed_items)})
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        log_event("sentinel", "drift_check_failed", {"error": str(e)})
        sys.exit(1)

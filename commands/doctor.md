---
description: |
  Pre-flight environment check. Validates all CLI tools, plugins, MCP servers,
  and auth profiles are properly configured. Run once after installing Relay,
  or any time you suspect a missing dependency. Supports --fix flag for
  auto-remediation of fixable issues.
trigger_keywords:
  - relay doctor
  - check setup
  - prerequisites
  - preflight
  - verify installation
---

# /relay:doctor

When the user invokes this command, run a full environment health check.
Conductor executes all steps directly — run the commands, capture output, show results.
Do NOT just tell the user what to run.

## Step 1 — Run tool version checks

Run each command, capture the output, and evaluate against minimum versions:

| Tool | Minimum | Check command | Severity |
|------|---------|---------------|----------|
| pac | 2.6+ | `pac --version` | ❌ (required) |
| az | any | `az --version` | ❌ (required) |
| python | 3.8+ | `python --version` | ❌ (required) |
| node | 22+ | `node --version` | ❌ (required) |
| git | any | `git --version` | ❌ (required) |
| bash | any | `bash --version` | ⚠️ (hooks depend on it) |
| jq | any | `jq --version` | ⚠️ (hooks depend on it) |
| pwsh | 7.0+ | `pwsh --version` | ⚠️ (scripts depend on it) |
| dotnet | 6.0+ | `dotnet --version` | ⚠️ (plugin build) |

For each tool:
- If found and meets minimum version: `✅ <tool> v<version>`
- If found but below minimum: `❌ <tool> v<version> — minimum <min> required`
- If not found: `❌ <tool> — not found`
  - bash (Windows): suggest "Install Git for Windows (includes Git Bash)"
  - jq: suggest `winget install jqlang.jq`
  - pwsh: suggest "Install PowerShell 7+ from https://aka.ms/powershell"
  - dotnet: suggest "Install .NET SDK 6.0+ from https://dot.net"

## Step 2 — Power Platform Skills plugin detection

Check if installed: `canvas-apps`, `model-apps`, `power-pages`, `code-apps-preview`

Detection method depends on platform:
- **Claude Code:** `claude plugin list` or check installed plugins
- **Copilot CLI:** `copilot plugin list`
- **VS Code:** Check `.vscode/settings.json` for `chat.plugins` entries

For each plugin:
- If detected: `✅ <plugin-name>`
- If not detected: `⚠️ <plugin-name> — not found`

If any missing, show install commands:
```
⚠️ Missing plugins detected. Install with:
/plugin install canvas-apps@power-platform-skills
/plugin install model-apps@power-platform-skills
/plugin install power-pages@power-platform-skills
/plugin install code-apps-preview@power-platform-skills
```

## Step 3 — Dataverse MCP detection

Check for Dataverse MCP configuration:

1. Look in `.vscode/settings.json` for MCP server entries with Dataverse URL
2. Look in `.vscode/mcp.json` for Dataverse MCP URL pattern (`*.crm*.dynamics.com/api/mcp`)
3. Check for local proxy: `dotnet tool list --global | Select-String "dataverse.mcp"`

- If found with valid URL: `✅ Dataverse MCP configured: <url>`
- If not found:
  ```
  ⚠️ Dataverse MCP not detected.
     Cloud: Enable in Power Platform Admin Center → Environment → Settings → Product → Features
     Local: dotnet tool install --global Microsoft.PowerPlatform.Dataverse.MCP
  ```

## Step 4 — Canvas Authoring MCP detection

Check `.vscode/mcp.json` for a canvas-authoring entry.

- If found: `✅ Canvas Authoring MCP configured`
- If not found:
  ```
  ⚠️ Canvas Authoring MCP not detected (optional — needed for forge-canvas).
     Configure via /configure-canvas-mcp after creating a Canvas App.
  ```

## Step 5 — PAC auth profiles

Run: `pac auth list`

Display the full output with guidance:
```
📋 PAC Auth Profiles:
<full pac auth list output>

The profile marked with ★ or [ACTIVE] is the one Relay will use.
If wrong, switch before running /relay:start:
  pac auth select --index <N>

To add a new environment:
  pac auth create --environment https://<org>.crm.dynamics.com
```

If `pac auth list` returns no profiles or errors:
```
❌ No PAC auth profiles found.
   Run: pac auth create --environment https://<your-org>.crm.dynamics.com
```

## Step 6 — Summary table

Print the consolidated results:

```
┌─────────────────────────────────┬────────┐
│ Check                           │ Status │
├─────────────────────────────────┼────────┤
│ PAC CLI 2.6+                    │ ✅/❌  │
│ Azure CLI                       │ ✅/❌  │
│ Python 3.8+                     │ ✅/❌  │
│ Node.js 22+                     │ ✅/❌  │
│ Git                             │ ✅/❌  │
│ Bash                            │ ✅/⚠️  │
│ jq                              │ ✅/⚠️  │
│ PowerShell 7+                   │ ✅/⚠️  │
│ .NET SDK 6.0+                   │ ✅/⚠️  │
│ Power Platform Skills plugins   │ ✅/⚠️  │
│ Dataverse MCP                   │ ✅/⚠️  │
│ Canvas Authoring MCP            │ ✅/⚠️  │
│ PAC Auth (active profile)       │ ✅/❌  │
└─────────────────────────────────┴────────┘
```

Legend:
- ❌ = must fix before using Relay
- ⚠️ = optional but recommended
- ✅ = ready

If all critical checks pass:
```
✅ Environment ready. Run /relay:start to begin a new project.
```

If any ❌:
```
❌ <N> critical issues found. Fix the ❌ items above, then re-run /relay:doctor.
```

Print next steps for each ❌ item (install command or link).

## --fix flag

If the user runs `/relay:doctor --fix`, attempt auto-remediation:

**Can fix automatically:**
- Missing Python packages: `pip install openpyxl --quiet`
- Missing jq (if winget available): `winget install jqlang.jq --accept-package-agreements --accept-source-agreements`

**Cannot fix automatically (tell user to install manually):**
- PAC CLI — `winget install Microsoft.PowerAppsCLI`
- Node.js — download from https://nodejs.org
- Python — download from https://python.org
- Azure CLI — `winget install Microsoft.AzureCLI`
- Git — `winget install Git.Git`
- .NET SDK — download from https://dot.net
- PowerShell 7+ — `winget install Microsoft.PowerShell`

After attempting fixes, re-run the checks and show updated summary:
```
🔧 Auto-fix results:
  ✅ jq installed successfully
  ⚠️ PAC CLI — cannot auto-install, run: winget install Microsoft.PowerAppsCLI

Re-running checks...
<updated summary table>
```

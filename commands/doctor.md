---
description: |
  Pre-flight environment check. Validates all CLI tools, plugins, MCP servers,
  and auth profiles are properly configured. Run once after installing Relay,
  or any time you suspect a missing dependency.
trigger_keywords:
  - relay doctor
  - check setup
  - prerequisites
  - preflight
  - verify installation
---

# /relay:doctor

When the user invokes this command, run a full environment health check.
This is a **one-time post-install verification** — not a per-project gate.

## Step 1 — Run the prerequisite check script

```powershell
$env:PYTHONUTF8 = "1"
python scripts/relay-prerequisite-check.py
```

If the script is not found (running from a project folder), try the plugin root:
```powershell
python "$PSScriptRoot/../scripts/relay-prerequisite-check.py"
```

Show the full output to the user. If exit code is 1, offer `--fix`:
```powershell
python scripts/relay-prerequisite-check.py --fix
```

## Step 2 — Check individual tool versions

Even if the script passes, confirm these minimum versions explicitly:

| Tool | Minimum | Check command |
|------|---------|---------------|
| pac | 2.6+ | `pac --version` |
| az | any | `az --version` |
| python | 3.8+ | `python --version` |
| node | 22+ | `node --version` |
| git | any | `git --version` |
| dotnet | 6.0+ | `dotnet --version` |

For each tool, show: ✅ `tool vX.Y.Z` or ❌ `tool — not found (install: <hint>)`

## Step 3 — Check Power Platform Skills plugins

Verify the 4 required plugins are available:

| Plugin | Purpose |
|--------|---------|
| canvas-apps | Canvas App authoring MCP |
| model-apps | /genpage — custom React pages in MDA |
| power-pages | /create-site — Power Pages portals |
| code-apps-preview | React/TypeScript code apps + connector automation |

Detection method depends on platform:
- **Claude Code:** `claude plugin list` or check installed plugins
- **Copilot CLI:** `copilot plugin list`
- **VS Code:** Check `settings.json` for `chat.plugins` entries

If plugins can't be detected programmatically, print a reminder:
```
⚠️  Could not detect plugins automatically.
    Ensure these are installed:
    /plugin install canvas-apps@power-platform-skills
    /plugin install model-apps@power-platform-skills
    /plugin install power-pages@power-platform-skills
    /plugin install code-apps-preview@power-platform-skills
```

## Step 4 — Check Dataverse MCP configuration

Check if Dataverse MCP is configured:

**Option A — Cloud MCP:**
Look for MCP server config pointing to `https://<org>.crm.dynamics.com/api/mcp`
in VS Code `mcp.json` or Copilot CLI MCP config.

**Option B — Local proxy:**
```powershell
dotnet tool list --global | Select-String "dataverse.mcp"
```

If neither is detected:
```
⚠️  Dataverse MCP not detected.
    Cloud: Enable in Power Platform Admin Center → Environment → Settings → MCP
    Local: dotnet tool install --global Microsoft.PowerPlatform.Dataverse.MCP
```

## Step 5 — Show PAC auth profiles

This is the most important step for multi-environment users.

```powershell
pac auth list
```

Display the output to the user with this guidance:

```
📋 PAC Auth Profiles:
<full pac auth list output>

The profile marked with ★ (or [ACTIVE]) is the one Relay will use.
If this is not the correct environment for your project, switch before
running /relay:start:

  pac auth select --index <N>

To add a new environment:
  pac auth create --environment https://<org>.crm.dynamics.com
```

**Important:** Do NOT validate deployment rights here. That happens in
Phase 5 Step 0 (`pac auth who` + `pac solution list`). Doctor only shows
what's available so the user can verify visually.

## Step 6 — Summary

Print a summary table:

```
┌─────────────────────────────────┬────────┐
│ Check                           │ Status │
├─────────────────────────────────┼────────┤
│ PAC CLI 2.6+                    │ ✅/❌  │
│ Azure CLI                       │ ✅/❌  │
│ Python 3.8+                     │ ✅/❌  │
│ Node.js 22+                     │ ✅/❌  │
│ Git                             │ ✅/❌  │
│ .NET SDK 6.0+                   │ ✅/❌  │
│ Power Platform Skills plugins   │ ✅/⚠️  │
│ Dataverse MCP                   │ ✅/⚠️  │
│ PAC Auth (active profile)       │ ✅/❌  │
└─────────────────────────────────┴────────┘
```

- ✅ = ready
- ⚠️ = could not verify (may still work)
- ❌ = missing or below minimum version

If all checks pass:
```
✅ Environment ready. Run /relay:start to begin a new project.
```

If any ❌:
```
❌ <N> issues found. Fix the items above, then re-run /relay:doctor.
```

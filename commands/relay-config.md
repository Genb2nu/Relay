---
description: View or edit Relay configuration — enforcement mode, model overrides, tool limits.
trigger_keywords:
  - relay config
  - relay settings
  - configure relay
---

# /relay:config

When the user invokes this command:

**View mode** (no arguments): Show current `.relay/state.json` config section plus global defaults.

**Edit mode** (with key=value): Update the specified config value.

Supported config keys:

| Key | Values | Default | Description |
|---|---|---|---|
| `enforcement_mode` | `advisory`, `strict` | `advisory` | Whether hooks advise or block |
| `conductor_model` | `opus`, `sonnet` | `opus` | Model for Conductor |
| `forge_model` | `opus`, `sonnet` | `sonnet` | Model for Forge specialists |
| `vault_model` | `opus`, `sonnet` | `sonnet` | Model for Vault |
| `scout_model` | `opus`, `sonnet` | `sonnet` | Model for Scout |
| `sentinel_model` | `opus`, `sonnet` | `sonnet` | Model for Sentinel |

Examples:
```
/relay:config                          # show all config
/relay:config enforcement_mode=strict  # enable strict hook enforcement
/relay:config forge_model=opus         # upgrade Forge specialists to Opus for complex work
```

Note: Auditor, Warden, and Critic are always Opus. These are non-configurable — review quality is non-negotiable.

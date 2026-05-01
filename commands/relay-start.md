---
description: Start a new Relay project. Scaffolds the project folder structure and begins discovery with Scout.
trigger_keywords:
  - relay start
  - new project
  - start relay
  - begin project
---

# /relay:start

When the user invokes this command:

0. **Run prerequisite check FIRST** — before checking for existing projects or creating files:
   ```powershell
   $env:PYTHONUTF8 = "1"
   python scripts/relay-prerequisite-check.py
   ```
   - If exit code 1 (critical failures): show output to user, offer `--fix`, do NOT proceed.
   - If exit code 0: show summary (especially warnings), then continue.
   - In VS Code mode, use `--skip-plugins` flag (Copilot CLI plugins not applicable).

1. Check if `.relay/state.json` already exists in the current directory.
   - If yes, refuse: "This folder already has an active Relay project at phase '<phase>'. Run `/relay:status` to see where you are, or delete `.relay/state.json` to start fresh."

2. Create the project folder structure:
   ```
   docs/
   src/
   .relay/
   ```

3. Write `.relay/state.json` with initial state:
   ```json
   {
     "project_name": "",
     "phase": "discovery",
     "last_updated": "<ISO timestamp>",
     "artifacts": {
       "requirements": null,
       "plan": null,
       "security_design": null,
       "critic_report": null,
       "test_report": null,
       "security_test_report": null
     },
     "approvals": {},
     "plan_checksum": null,
     "security_design_checksum": null,
     "config": {
       "enforcement_mode": "advisory"
     }
   }
   ```

4. Ask the user for a one-paragraph project brief. Explain:
   "Give me a one-paragraph brief describing what you want to build. Include: who will use it (personas), what they need to do, and any security-sensitive data. I'll hand this to Scout for discovery."

5. Once the user provides the brief, invoke Scout with the brief text.

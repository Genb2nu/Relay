---
description: |
  Map an existing Power Platform solution before making changes. Invokes Analyst
  to read the deployed solution via Dataverse MCP and PAC CLI and produce a
  complete inventory of what exists. Run this before /relay:change or
  /relay:bugfix on an existing solution.
trigger_keywords:
  - relay analyse
  - relay analyze
  - analyse existing
  - analyze existing
  - map existing solution
  - understand existing project
---

# /relay:analyse

When the user invokes this command:

1. Ask: "Which solution should I analyse? Please provide the solution name and
   confirm the PAC CLI is authenticated to the correct environment."

2. Once confirmed:
   - Create `docs/` folder if it doesn't exist
   - Update `.relay/state.json`:
     ```json
     {
       "mode": "change",
       "phase": "analysis",
       "existing_solution": "<solution name>"
     }
     ```

3. Invoke **Analyst** to map the existing solution.
   Analyst produces `docs/existing-solution.md`.

4. Once Analyst completes, show the user a summary:
   ```
   Analysis complete. Here's what I found in <solution name>:

   Tables: <N> custom tables
   Flows: <N> cloud flows (<N> active, <N> inactive)
   Apps: <N> (canvas: <N>, model-driven: <N>)
   Security roles: <N> custom roles
   Plugins: <N> registered steps

   Risk observations:
   🔴 Critical: <N> | 🟡 Major: <N> | 🔵 Minor: <N>

   Full map saved to docs/existing-solution.md
   ```

5. Tell the user:
   - "Run `/relay:change <description>` to add a feature or modify behaviour"
   - "Run `/relay:bugfix <description>` to fix a specific issue"
   - "Run `/relay:audit` for a full security and quality audit"

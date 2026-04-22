---
description: Package the solution for deployment. Exports managed solution and prepares for environment promotion.
trigger_keywords:
  - relay deploy
  - deploy solution
  - export solution
  - package solution
---

# /relay:deploy

When the user invokes this command:

1. Read `.relay/state.json`. Verify phase is `complete` (both Sentinel and Warden verification passed).

2. If phase is not `complete`, refuse: "Cannot deploy — verification is not complete. Run `/relay:status` to see what's pending."

3. Execute deployment steps:
   ```bash
   # Export managed solution
   pac solution export --path ./export --name <SolutionName> --managed

   # Export unmanaged for source control
   pac solution export --path ./export --name <SolutionName>
   ```

4. Summarise:
   - Solution name and version
   - Export path
   - Components included
   - Security roles included
   - Remind user to import to target environment and run smoke tests

5. If Courier agent is available (Phase 4), hand off to Courier for full ALM pipeline execution.

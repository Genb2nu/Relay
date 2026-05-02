---
description: Run Warden's security verification against the current build on demand, outside the normal workflow.
trigger_keywords:
  - relay security audit
  - security check
  - run warden
---

# /relay:security-audit

When the user invokes this command:

1. Read `.relay/state.json`. Verify a build exists (phase is `building`, `verification`, or `complete`).

2. Invoke Warden in Mode B (Security Verification).

3. Warden writes results to `docs/security-test-report.md` and returns summary.

4. If issues found, ask the user whether to route fixes to Forge specialist/Vault or to defer.

Use this when:
- You want to spot-check security mid-build
- After making manual changes to the solution
- Before a deployment to a higher environment

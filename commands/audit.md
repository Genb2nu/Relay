---
description: |
  Audit an existing Power Platform solution. Points Analyst + Auditor + Warden
  + Critic at a live deployed solution and produces a comprehensive audit report
  covering technical completeness, security gaps, footgun risks, and
  remediation recommendations. Use on any existing solution — not just ones
  built by Relay.
trigger_keywords:
  - relay audit
  - audit solution
  - review solution
  - solution health check
  - security audit
---

# /relay:audit

When the user invokes this command:

1. Ask the user: "Which solution do you want to audit? Tell me the solution
   name and confirm the PAC CLI is authenticated to the correct environment."

2. Once confirmed, create the audit project structure:
   ```
   docs/
   ├── existing-solution.md   ← Analyst writes this
   └── audit-report.md        ← Auditor + Warden + Critic write this
   ```
   Update `.relay/state.json` with `"mode": "audit"` and `"phase": "analysis"`.

3. **Phase: Analysis — invoke Analyst**
   Analyst reads the deployed solution via Dataverse MCP and PAC CLI and
   produces `docs/existing-solution.md` with a complete map of what exists.

4. **Phase: Review — invoke Auditor, Warden, Critic in sequence**

   **Auditor** reads `docs/existing-solution.md` and checks:
   - Does the solution follow Power Platform naming conventions?
   - Are all tables, columns, and relationships properly documented?
   - Are there missing components (env variables without values, inactive flows)?
   - Are there redundant or overlapping components?
   - Is the deployment pattern correct (managed vs unmanaged, solution layering)?

   **Warden** reads `docs/existing-solution.md` and checks (security only):
   - Security role privilege levels and scope (are they minimum necessary?)
   - FLS coverage on sensitive columns
   - UI-vs-actual-security traps (JS hide ≠ security, sitemap remove ≠ security)
   - Connection reference identity (maker vs invoking user)
   - DLP policy compliance
   - Missing security roles or overprivileged roles

   **Critic** reads `docs/existing-solution.md` and runs the full footgun
   checklist from `skills/power-platform-footgun-checklist/SKILL.md` against
   the live solution.

5. **Produce `docs/audit-report.md`** synthesising all findings:

   ```markdown
   # Audit Report — <Solution Name>
   Generated: <date> | Environment: <org url>

   ## Executive Summary
   <3-4 sentences: what the solution does, overall health, top concern>

   ## Risk Summary
   | Severity | Count |
   |---|---|
   | 🔴 Critical | <N> |
   | 🟡 Major | <N> |
   | 🔵 Minor | <N> |
   | ✅ Pass | <N> |

   ---

   ## Critical Issues (fix before production)

   ### [CRIT-001] <Issue title>
   - **Category**: Security | Technical | Functional | ALM
   - **Finding**: <what is wrong>
   - **Risk**: <what could go wrong if not fixed>
   - **Remediation**: <exact steps to fix>
   - **Effort**: <estimated hours>

   ---

   ## Major Issues (fix soon)

   ### [MAJ-001] <Issue title>
   ...

   ---

   ## Minor Issues / Recommendations

   ### [MIN-001] <Issue title>
   ...

   ---

   ## Checklist Results

   | # | Check | Result | Finding |
   |---|---|---|---|
   | 1 | Plugin execution order defined | ✅ PASS | |
   | 2 | Flow concurrency limits set | ❌ FAIL | Approval flow concurrent |
   | 3 | FLS on cr_status | ✅ PASS | |
   | ... | ... | ... | ... |

   ---

   ## What is working well
   <Acknowledge things done correctly — don't make it purely negative>

   ## Recommended remediation order
   1. <Most critical item first>
   2. ...

   ## Estimated remediation effort
   | Severity | Items | Estimated hours |
   |---|---|---|
   | Critical | <N> | <N> hrs |
   | Major | <N> | <N> hrs |
   | **Total** | | **<N> hrs** |
   ```

6. Tell the user the audit is complete and show the risk summary. Ask if they
   want to start a `change-plan` to address any of the critical issues.

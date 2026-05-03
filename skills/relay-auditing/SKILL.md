---
name: relay-auditing
description: |
  Auditor's knowledge base. 20-point completeness checklist for reviewing
  technical plans against requirements. Covers how to identify gaps, write
  issues with severity ratings, and make the approval decision.
trigger_keywords:
  - plan review
  - completeness check
  - auditor checklist
  - plan gap
  - plan quality
allowed_tools:
  - Read
---

# Relay Auditing — Auditor Knowledge Base

## 20-Point Completeness Checklist

Run this against `docs/plan.md` cross-referenced with `docs/requirements.md`:

### Requirements Coverage (5 items)
| # | Check | PASS criteria |
|---|---|---|
| 1 | Every persona has at least one user story | Count personas in req → each appears in plan |
| 2 | Every user story maps to a buildable component | No story left as "future phase" without user agreement |
| 3 | Non-functional requirements addressed | Performance, scalability, availability noted if present in req |
| 4 | Acceptance criteria are testable | Each story has clear pass/fail criteria |
| 5 | Out-of-scope items explicitly listed | Plan says what it does NOT do |

### Schema Completeness (5 items)
| # | Check | PASS criteria |
|---|---|---|
| 6 | Every entity has full column list | Data type, max length, required/optional, default value |
| 7 | All relationships defined with cascade | 1:N, N:1, N:N with cascade behaviour specified |
| 8 | Option set values are explicit | Integer values + display labels for every choice column |
| 9 | Table ownership type declared | User-owned or Org-owned per table with justification |
| 10 | Naming conventions consistent | All tables/columns use {prefix}_{name} pattern |

### Flow & Logic Completeness (5 items)
| # | Check | PASS criteria |
|---|---|---|
| 11 | Every flow has trigger + steps + error handling | No "TBD" in flow definitions |
| 12 | Flow triggers are specific | Not "when something happens" but exact trigger type + filter |
| 13 | Plugins have pre/post image requirements | Which fields, which stage, sync vs async |
| 14 | Business rules listed (or marked as N/A) | Even "no business rules needed" is acceptable |
| 15 | Environment variables for all configurable values | URLs, thresholds, email addresses not hardcoded |

### App Design Completeness (3 items)
| # | Check | PASS criteria |
|---|---|---|
| 16 | Every app screen is listed with purpose | Screen name + which persona uses it + what they do |
| 17 | Forms have field lists per tab/section | Not just "a form with fields" but explicit layout |
| 18 | Navigation between screens/apps defined | How users move between views/screens |

### Deployment & Testing (2 items)
| # | Check | PASS criteria |
|---|---|---|
| 19 | Solution strategy defined | Solution name, publisher, managed vs unmanaged |
| 20 | Test approach defined | How to verify each component works |

---

## Issue Severity Guide

| Severity | Definition | Action required |
|---|---|---|
| **critical** | Plan cannot be built as written. Forge specialist will be blocked or produce wrong output. | Drafter MUST fix before Phase 4. |
| **major** | Plan is ambiguous. Forge specialist will have to guess, likely incorrectly. | Drafter SHOULD fix. If not fixed, document the assumption. |
| **minor** | Plan is buildable but could be clearer. Style or completeness suggestion. | Drafter MAY defer. No re-review needed. |

---

## Writing Issues (template)

```
[CATEGORY] <one-line description of the gap>
  Severity: critical | major | minor
  Location: plan.md § <section name>
  What's missing: <specific information that Forge specialist would need>
  Why it matters: <consequence of not fixing>
```

Categories: COMPLETENESS, CLARITY, TECHNICAL, MISSING

---

## Approval Decision

- **Status: approved** — All 20 checks pass (or failures are minor-only). Plan is buildable.
- **Status: issues** — At least one critical or major item. Drafter must fix and re-submit.
- **Status: questions** — Need information from the user (not Drafter) to proceed.

**Never block for minor issues.** If the only findings are minor, approve with notes.

# Relay Review

Date: 2026-05-01

## Framing

Relay should be judged in the right context.

This is not a marketed product and it is not pretending to be a general-purpose enforcement platform for third parties. It is a personal delivery tool for Power Platform work. In that context, Relay is already useful. The VS Code pilots and the CLI smoke work show that it can produce real output, not just plans and prompts.

The practical value is already proven. The hardening work is still the right next step, but the reason is to strengthen the enforcement story and reduce drift, not because Relay is non-functional or empty.

My corrected summary is:

- Relay is already delivering real value.
- The current issues mostly weaken control guarantees, not the core delivery workflow.
- Hardening should be treated as the next maturity step, not as evidence that Relay is broken.

## Honest Opinion

Relay is a strong and useful internal tool with real Power Platform knowledge behind it. The project has a clear workflow, domain-specific depth, and enough operational detail to be genuinely productive in real delivery work.

The main gap is not usefulness. The main gap is that some of the repo language describes stronger enforcement guarantees than the implementation currently provides. That distinction matters:

- as a delivery tool, Relay is already useful
- as a strict enforcement boundary, Relay still needs hardening

That is a very different conclusion from saying the project is broken.

## What Relay Already Proves

Based on the repo evidence and your clarification:

- Relay has already produced genuinely useful build output in VS Code pilots.
- The CLI smoke exercise produced real deployed artifacts rather than only paperwork.
- The enforcement loopholes matter, but they did not erase the practical value of the generated schema, roles, profiles, and deployment steps.

The correct interpretation is: Relay is operationally helpful now, while still having important integrity and consistency gaps to close.

## Verified Hardening Findings

Severity below refers to enforcement integrity and future reliability, not to Relay's current usefulness as a personal tool.

### 1. High: write restrictions are enforced by basename, not by full path

File: `hooks/scripts/pre-tool-use.sh`

Relevant lines:

- `20` reads a path from tool input.
- `27-28` reduce it to `BASENAME=$(basename "$FILE_PATH")`.
- `66`, `74`, `83`, `93`, `102` compare only the basename.

Why it matters:

- The policy says certain agents may write only to specific files.
- The hook only checks filenames, not normalized paths.
- That weakens the role-boundary story because same-name files in other locations can pass.

Practical interpretation:

- This is a real loophole in the enforcement model.
- It does not mean Relay cannot produce useful output. It means the write-control layer is weaker than described.

### 2. High: Stylist and Analyst are documented as restricted but not enforced

Files:

- `AGENTS.md:84-85`
- `agents/stylist.agent.md:31`
- `agents/analyst.agent.md:27`
- `hooks/scripts/pre-tool-use.sh:58-130`

Why it matters:

- The docs and agent contracts define narrow write scopes for Stylist and Analyst.
- The hook script has no `stylist)` or `analyst)` case.
- Both fall through to the default allow path.

Practical interpretation:

- This is a policy/enforcement mismatch.
- It matters because the repo presents these controls as part of Relay's safety model.

### 3. High: missing agent identity collapses to conductor access

Files:

- `hooks/scripts/pre-tool-use.sh:53-55`
- `CLAUDE.md:205-207`

Why it matters:

- If `CLAUDE_AGENT` is missing, the hook assumes conductor context and allows everything.
- That makes the restriction model dependent on runtime identity propagation.

Practical interpretation:

- This is mainly a hardening concern.
- It weakens confidence in the isolation model across runtimes.

### 4. High: phase gate interception covers only part of the documented build surface

Files:

- `hooks/scripts/phase-gate-hook.sh:36-37`
- `hooks/scripts/phase-gate-hook.sh:56-57`
- `README.md:186-188`
- `README.md:218-220`
- `CLAUDE.md:443-445`

Why it matters:

- The hook watches only a narrow set of raw command strings.
- The docs describe a broader build surface, including imports, activation scripts, Dataverse API flows, and other build paths.

Practical interpretation:

- The gate is useful, but not comprehensive.
- The issue is overstated guarantee coverage, not total absence of value.

### 5. Medium: state and schema contracts drift across core files

Files:

- `CLAUDE.md:27-42`
- `CLAUDE.md:103-126`
- `commands/relay-start.md:36-51`
- `commands/start.md:53-84`
- `commands/start.md:128-143`
- `schemas/plan-index.schema.json:82-85`
- `agents/stylist.agent.md:325`

Why it matters:

- Different files define different `state.json` and `plan-index.json` expectations.
- Some agent instructions reference fields that are not in the shared schema.

Practical interpretation:

- This creates drift risk and maintenance cost.
- It does not remove the utility of the workflow, but it does make it easier for the workflow to diverge over time.

### 6. Medium: some tracked quality fields are not actually enforced by gates

Files:

- `schemas/plan-index.schema.json:31`
- `scripts/relay-gate-check.py:81-90`
- `schemas/plan-index.schema.json:59-64`
- `scripts/relay-gate-check.py:149-154`

Examples:

- `all_user_stories_have_test_case` exists in the schema but is not checked in phase 2.
- `stylist_complete` exists in the schema but is not checked in phase 5.

Practical interpretation:

- The tracking model is ahead of the enforcement model.
- That is a maturity gap, not a sign the workflow is useless.

### 7. Medium: plugin packaging/version drift exists

Files:

- `.claude-plugin/plugin.json:3`
- `.claude-plugin/marketplace.json:3,10,16`

Mismatch:

- `plugin.json` is `0.5.1`
- `marketplace.json` still says `0.4.0`

Practical interpretation:

- This is release hygiene drift.
- It matters for consistency, but it does not undermine Relay's internal delivery value.

### 8. Medium: the documented prerequisites understate the real runtime surface

Files:

- `README.md:34-40`
- `hooks/hooks.json:6,10,15`
- `hooks/scripts/pre-tool-use.sh:1,20,36,43`
- `hooks/scripts/phase-gate-hook.sh:1,18,39-40,59,75-77`
- `hooks/scripts/session-start.sh:1,19-20,29,49-50`
- `scripts/relay-drift-check.py:50`

Why it matters:

- The documented prerequisites do not fully reflect runtime dependence on `bash`, `jq`, and `pwsh`.
- That especially affects Windows clarity.

Practical interpretation:

- This is a documentation/runtime alignment issue.
- It should be fixed so the tool is easier to operate consistently.

## Correct Bottom Line

Relay is not broken.

The correct bottom line is:

- Relay is already a useful personal Power Platform delivery tool.
- The smoke and pilot results show it can produce real artifacts and real progress.
- The hook and contract issues matter because they weaken trust in the enforcement narrative.
- That makes hardening the right next step.

## Suggested Next Step

The next step should be hardening, but framed correctly:

1. Tighten the hook model so it matches the repo's stated guarantees.
2. Collapse contract drift between `CLAUDE.md`, commands, schema, and agent files.
3. Make runtime prerequisites explicit and self-checked.
4. Keep using Relay for delivery work while improving the integrity layer.

## Final Verdict

Relay is already useful enough to justify continued investment.

The current problems are best described as hardening and consistency work for a valuable personal tool, not as evidence that Relay failed to deliver practical results.
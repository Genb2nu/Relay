#!/usr/bin/env python3
"""
relay-score.py
Scores the plan against objective criteria.
Called by Conductor after Drafter completes (Phase 2) and after Phase 4 lock.

Outputs:
  - .relay/plan-index.json updated with scores
  - docs/plan-scores.md

Usage:
  python relay-score.py
"""

import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone

PLAN_INDEX_PATH = ".relay/plan-index.json"
REQUIREMENTS_PATH = "docs/requirements.md"
PLAN_PATH = "docs/plan.md"
SECURITY_DESIGN_PATH = "docs/security-design.md"
SCORES_PATH = "docs/plan-scores.md"
LOG_PATH = ".relay/execution-log.jsonl"


def log_event(agent, event, details=None):
    entry = {"timestamp": datetime.now(timezone.utc).isoformat(), "agent": agent, "event": event}
    if details:
        entry.update(details)
    os.makedirs(".relay", exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def atomic_write_text(path, content):
    directory = os.path.dirname(path) or "."
    os.makedirs(directory, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile("w", delete=False, dir=directory, encoding="utf-8") as temp_file:
            temp_file.write(content)
            temp_path = temp_file.name
        os.replace(temp_path, path)
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


def atomic_write_json(path, data):
    atomic_write_text(path, json.dumps(data, indent=2))


def read_file(path):
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read()


def load_plan_index():
    try:
        with open(PLAN_INDEX_PATH, encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {PLAN_INDEX_PATH} at line {e.lineno}, column {e.colno}: {e.msg}")
        sys.exit(1)
    except OSError as e:
        print(f"Error: Could not read {PLAN_INDEX_PATH}: {e}")
        sys.exit(1)


def score_completeness(plan_md, requirements_md, security_md):
    """Score plan completeness 0-100."""
    score = 0
    gaps = []

    checks = [
        (plan_md, "## ", "Plan has no sections", 5),
        (requirements_md, "## Personas", "No personas section", 10),
        (requirements_md, "## User Stories", "No user stories section", 10),
        (requirements_md, "## Entities", "No entities section", 10),
        (requirements_md, "## Out of Scope", "No out-of-scope section", 5),
        (plan_md, "## ", "Plan has section headers", 5),
        (plan_md, "Error", "No error handling mentioned in plan", 10),
        (plan_md, "Sequential", "No concurrency control mentioned", 5),
        (plan_md, "Environment Variable", "No environment variables", 5),
        (security_md, "## Security Role", "No security roles in security design", 15),
        (security_md, "FLS", "No FLS coverage in security design", 10),
        (security_md, "Threat", "No threat model", 10),
    ]

    for content, keyword, gap_msg, points in checks:
        if keyword.lower() in content.lower():
            score += points
        else:
            gaps.append(gap_msg)

    return min(score, 100), gaps


def score_security(security_md, plan_md):
    """Score security coverage 0-100."""
    score = 0
    gaps = []

    security_checks = [
        ("FLS", "No FLS coverage", 20),
        ("self-approval", "Self-approval risk not addressed", 15),
        ("connection reference", "Connection reference identity not specified", 10),
        ("minimum privilege", "Minimum privilege principle not mentioned", 15),
        ("UI-only", "UI-only security traps not addressed", 10),
        ("plugin", "No plugin for server-side enforcement", 10),
        ("DLP", "DLP considerations missing", 5),
        ("service account", "Service account privilege not specified", 10),
        ("Business Unit", "Business unit scope not specified", 5),
    ]

    for keyword, gap_msg, points in security_checks:
        if keyword.lower() in security_md.lower() or keyword.lower() in plan_md.lower():
            score += points
        else:
            gaps.append(gap_msg)

    return min(score, 100), gaps


def score_testability(requirements_md, plan_md):
    """Score testability 0-100."""
    score = 0
    gaps = []

    # Count user stories
    story_count = len(re.findall(r'as a .+, i (want|can|should)', requirements_md.lower()))
    # Count test cases mentioned in plan
    test_count = len(re.findall(r'test|verify|assert|check|validate', plan_md.lower()))

    if story_count > 0:
        score += 20
    else:
        gaps.append("No user stories found")

    if test_count > 5:
        score += 20
    elif test_count > 0:
        score += 10
        gaps.append(f"Only {test_count} test references in plan (suggest >5)")
    else:
        gaps.append("No test/verify references in plan")

    # Check for specific test scenarios
    testable_patterns = [
        ("employee", "Employee persona test cases missing", 15),
        ("manager", "Manager persona test cases missing", 15),
        ("admin", "Admin persona test cases missing", 10),
        ("security", "Security test cases missing", 10),
        ("error", "Error handling test cases missing", 10),
    ]

    for pattern, gap_msg, points in testable_patterns:
        if pattern.lower() in requirements_md.lower():
            score += points
        else:
            gaps.append(gap_msg)

    return min(score, 100), gaps


def main():
    plan_md = read_file(PLAN_PATH)
    requirements_md = read_file(REQUIREMENTS_PATH)
    security_md = read_file(SECURITY_DESIGN_PATH)

    if not plan_md and not requirements_md:
        print("Error: No plan or requirements files found. Score deferred.")
        sys.exit(1)

    if not os.path.exists(PLAN_INDEX_PATH):
        print(f"Error: {PLAN_INDEX_PATH} not found. Cannot persist scores.")
        sys.exit(1)

    c_score, c_gaps = score_completeness(plan_md, requirements_md, security_md)
    s_score, s_gaps = score_security(security_md, plan_md)
    t_score, t_gaps = score_testability(requirements_md, plan_md)
    overall = round((c_score * 0.4) + (s_score * 0.4) + (t_score * 0.2))

    # Update plan-index
    pi = load_plan_index()
    pi["scores"] = {
        "plan_completeness": c_score,
        "security_coverage": s_score,
        "testability": t_score,
        "overall": overall,
        "scored_at": datetime.now(timezone.utc).isoformat()
    }
    atomic_write_json(PLAN_INDEX_PATH, pi)

    # Write score report
    lines = [
        f"# Plan Quality Scores\nGenerated: {datetime.now(timezone.utc).isoformat()}\n",
        f"## Overall Score: {overall}/100\n",
        "| Dimension | Score | Weight |\n|---|---|---|",
        f"| Plan Completeness | {c_score}/100 | 40% |",
        f"| Security Coverage | {s_score}/100 | 40% |",
        f"| Testability | {t_score}/100 | 20% |",
    ]

    if c_gaps or s_gaps or t_gaps:
        lines.append("\n## Gaps Found\n")
        if c_gaps:
            lines.append("### Completeness Gaps")
            lines.extend(f"- {gap}" for gap in c_gaps)
        if s_gaps:
            lines.append("\n### Security Gaps")
            lines.extend(f"- {gap}" for gap in s_gaps)
        if t_gaps:
            lines.append("\n### Testability Gaps")
            lines.extend(f"- {gap}" for gap in t_gaps)

    atomic_write_text(SCORES_PATH, "\n".join(lines) + "\n")

    print(f"\n[SCORE] Plan Scores:")
    print(f"  Completeness: {c_score}/100")
    print(f"  Security:     {s_score}/100")
    print(f"  Testability:  {t_score}/100")
    print(f"  Overall:      {overall}/100")

    if c_gaps or s_gaps or t_gaps:
        all_gaps = c_gaps + s_gaps + t_gaps
        print(f"\n[WARN] {len(all_gaps)} gap(s) identified - see docs/plan-scores.md")

    log_event("conductor", "plan_scored", {
        "completeness": c_score,
        "security": s_score,
        "testability": t_score,
        "overall": overall
    })


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

#!/usr/bin/env python3
"""
relay-consistency-check.py
Cross-validates plan-index.json claims against actual markdown file content.
Catches the "lying agent" problem — where an agent writes optimistic values
to plan-index.json without them being true in plan.md.

Run as part of relay-gate-check.py Phase 2 validation.

Exit codes:
  0 = consistent
  1 = inconsistencies found
"""

import json
import os
import re
import sys
from datetime import datetime, timezone

PLAN_INDEX_PATH = ".relay/plan-index.json"
PLAN_PATH = "docs/plan.md"
SECURITY_PATH = "docs/security-design.md"
REQUIREMENTS_PATH = "docs/requirements.md"
LOG_PATH = ".relay/execution-log.jsonl"
WIREFRAMES_PATH = "docs/wireframes.html"


def log_event(event, details=None):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": "consistency-check",
        "event": event,
    }
    if details:
        entry.update(details)
    os.makedirs(".relay", exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def read_text(path):
    if not os.path.exists(path):
        return ""
    try:
        with open(path, encoding="utf-8", errors="replace") as handle:
            return handle.read().lower()
    except OSError as e:
        print(f"Error: Could not read {path}: {e}")
        return ""


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


def check_consistency(pi):
    issues = []
    plan = read_text(PLAN_PATH)
    security = read_text(SECURITY_PATH)
    requirements = read_text(REQUIREMENTS_PATH)
    phase2 = pi.get("phase_gates", {}).get("phase2_planning", {})
    components = pi.get("components", {})

    # --- Check 1: all_flows_have_error_handling ---
    if phase2.get("all_flows_have_error_handling") is True:
        error_patterns = ["configure run after", "error handling", "run after", "scope", "try/catch", "on failure"]
        found = any(p in plan for p in error_patterns)
        if not found:
            issues.append({
                "claim": "all_flows_have_error_handling: true",
                "check": "plan.md",
                "finding": "No error handling patterns found in plan.md ('Configure run after', 'Scope', 'try/catch')"
            })

    # --- Check 2: all_entities_have_columns ---
    if phase2.get("all_entities_have_columns") is True:
        tables = components.get("tables", [])
        if tables:
            # Check each planned table appears in plan.md with column definitions
            for table in tables:
                table_name = table.get("logical_name", "").lower()
                if table_name and table_name not in plan:
                    issues.append({
                        "claim": f"all_entities_have_columns: true for {table_name}",
                        "check": "plan.md",
                        "finding": f"Table '{table_name}' not found in plan.md"
                    })
                else:
                    # Check that table has column count in plan
                    planned_cols = table.get("columns", 0)
                    if planned_cols > 0:
                        # Simple check: table section in plan should have column rows
                        # Look for the table name followed by column-like content
                        pattern = rf"{re.escape(table_name)}.*?\|"
                        if not re.search(pattern, plan, re.DOTALL):
                            issues.append({
                                "claim": f"all_entities_have_columns: true (columns: {planned_cols})",
                                "check": "plan.md",
                                "finding": f"Column table not found for {table_name} in plan.md"
                            })

    # --- Check 3: security_design_md_exists claim vs actual content ---
    if phase2.get("security_design_md_exists") is True:
        if not os.path.exists(SECURITY_PATH):
            issues.append({
                "claim": "security_design_md_exists: true",
                "check": "filesystem",
                "finding": f"{SECURITY_PATH} does not exist"
            })
        elif len(security) < 200:
            issues.append({
                "claim": "security_design_md_exists: true",
                "check": "docs/security-design.md",
                "finding": f"security-design.md exists but is suspiciously short ({len(security)} chars) — may be a stub"
            })

    # --- Check 4: decision_needed_count ---
    actual_decisions = plan.count("decision needed") + security.count("decision needed")
    claimed_decisions = phase2.get("decision_needed_count", 0)
    if claimed_decisions == 0 and actual_decisions > 0:
        issues.append({
            "claim": f"decision_needed_count: 0",
            "check": "plan.md + security-design.md",
            "finding": f"Found {actual_decisions} 'DECISION NEEDED' occurrences in docs but plan-index claims 0"
        })

    # --- Check 4b: wireframes_complete claim vs actual file ---
    if phase2.get("wireframes_complete") is True and not os.path.exists(WIREFRAMES_PATH):
        issues.append({
            "claim": "wireframes_complete: true",
            "check": "filesystem",
            "finding": f"{WIREFRAMES_PATH} does not exist"
        })

    # --- Check 5: Warden approval vs actual security content ---
    phase3 = pi.get("phase_gates", {}).get("phase3_review", {})
    if phase3.get("warden_approved") is True:
        security_markers = ["fls", "field level", "minimum privilege", "self-approval", "connection reference"]
        found_markers = [m for m in security_markers if m in security]
        if len(found_markers) < 2:
            issues.append({
                "claim": "warden_approved: true",
                "check": "docs/security-design.md",
                "finding": f"Warden claims approved but security-design.md only contains {len(found_markers)}/5 expected security markers: {found_markers}"
            })

    # --- Check 6: Component counts vs plan.md ---
    planned_tables = components.get("tables", [])
    planned_flows = components.get("flows", [])
    if planned_tables:
        plan_text = plan
        for table in planned_tables:
            name = table.get("logical_name", "")
            if name and name not in plan_text.lower():
                issues.append({
                    "claim": f"component table: {name}",
                    "check": "plan.md",
                    "finding": f"Table '{name}' listed in plan-index.components but not found in plan.md"
                })

    return issues


def main():
    if not os.path.exists(PLAN_INDEX_PATH):
        print("No plan-index.json found — consistency check skipped")
        sys.exit(0)

    pi = load_plan_index()

    issues = check_consistency(pi)

    if issues:
        print(f"\n[WARN] CONSISTENCY ISSUES FOUND - {len(issues)} discrepancies between plan-index.json and docs:")
        for i, issue in enumerate(issues, 1):
            print(f"\n  [{i}] Claim: {issue['claim']}")
            print(f"       Checked: {issue['check']}")
            print(f"       Finding: {issue['finding']}")
        log_event("consistency_failed", {"issues": len(issues), "details": issues})
        sys.exit(1)
    else:
        print("[PASS] Consistency check passed - plan-index.json is consistent with docs")
        log_event("consistency_passed")
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

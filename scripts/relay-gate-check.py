#!/usr/bin/env python3
"""
relay-gate-check.py
Validates plan-index.json before a phase can advance.
Run by Conductor before invoking the next phase's agents.

Usage:
  python relay-gate-check.py --phase 1   # validate phase 1 requirements before phase 2
  python relay-gate-check.py --phase 2   # validate phase 2 requirements before phase 3
  python relay-gate-check.py --phase 3   # validate phase 3 requirements before phase 4
  python relay-gate-check.py --phase 4   # validate phase 4 requirements before phase 5
  python relay-gate-check.py --phase 5   # validate phase 5 requirements before phase 6
  python relay-gate-check.py --phase 6   # validate phase 6 requirements before ship

Exit codes:
  0 = gate passed, safe to advance
  1 = gate failed, block advancement
"""

import json
import sys
import os
import argparse
from datetime import datetime, timezone

PLAN_INDEX_PATH = ".relay/plan-index.json"
LOG_PATH = ".relay/execution-log.jsonl"


def load_plan_index():
    if not os.path.exists(PLAN_INDEX_PATH):
        print(f"ERROR: {PLAN_INDEX_PATH} not found. Has Conductor initialised this project?")
        sys.exit(1)
    with open(PLAN_INDEX_PATH) as f:
        return json.load(f)


def log_event(agent, event, phase, details=None):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent,
        "event": event,
        "phase": phase,
    }
    if details:
        entry.update(details)
    os.makedirs(".relay", exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


def save_plan_index(data):
    with open(PLAN_INDEX_PATH, "w") as f:
        json.dump(data, f, indent=2)


def check_phase1(pi):
    """Phase 1 gate: requirements.md must cover required sections."""
    gate = pi["phase_gates"]["phase1_discovery"]
    errors = []

    if gate["persona_count"] < 2:
        errors.append(f"Too few personas: {gate['persona_count']} (minimum 2)")
    if gate["user_story_count"] < 5:
        errors.append(f"Too few user stories: {gate['user_story_count']} (minimum 5)")
    if gate["entity_count"] < 1:
        errors.append(f"No entities identified")

    missing = gate.get("sections_missing", [])
    if missing:
        errors.append(f"Missing required sections: {missing}")

    return errors


def check_phase2(pi):
    """Phase 2 gate: plan.md and security-design.md must be complete and consistent."""
    gate = pi["phase_gates"]["phase2_planning"]
    errors = []

    if not gate["plan_md_exists"]:
        errors.append("docs/plan.md does not exist")
    if not gate["security_design_md_exists"]:
        errors.append("docs/security-design.md does not exist")
    if not gate["all_entities_have_columns"]:
        errors.append("Not all entities have column definitions")
    if not gate["all_flows_have_error_handling"]:
        errors.append("Not all flows have error handling specified")
    if gate["decision_needed_count"] > 0:
        errors.append(f"{gate['decision_needed_count']} DECISION NEEDED items unresolved — present to user before planning")

    # Run consistency check — catches lying agents
    import subprocess
    result = subprocess.run(
        ["python3", "scripts/relay-consistency-check.py"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        errors.append(f"plan-index.json inconsistent with docs — {result.stdout.strip()}")
        print(result.stdout)

    return errors


def check_phase3(pi):
    """Phase 3 gate: both Auditor AND Warden must approve."""
    gate = pi["phase_gates"]["phase3_review"]
    errors = []

    if not gate["auditor_approved"]:
        errors.append(f"Auditor has not approved. Issues found: {gate['auditor_issues_found']}, resolved: {gate['auditor_issues_resolved']}")
    if not gate["warden_approved"]:
        errors.append(f"Warden has not approved. Issues found: {gate['warden_issues_found']}, resolved: {gate['warden_issues_resolved']}")
    if gate["auditor_issues_found"] > gate["auditor_issues_resolved"]:
        errors.append(f"Auditor: {gate['auditor_issues_found'] - gate['auditor_issues_resolved']} issues not yet resolved")
    if gate["warden_issues_found"] > gate["warden_issues_resolved"]:
        errors.append(f"Warden: {gate['warden_issues_found'] - gate['warden_issues_resolved']} issues not yet resolved")

    return errors


def check_phase4(pi):
    """Phase 4 gate: Critic must approve, plan must be locked."""
    gate = pi["phase_gates"]["phase4_adversarial"]
    errors = []

    if not gate["critic_approved"]:
        errors.append("Critic has not approved")
    if gate["checklist_items_passed"] < gate["checklist_items_total"]:
        failed = gate["checklist_items_total"] - gate["checklist_items_passed"]
        errors.append(f"{failed} checklist items failed")
    if gate["blocking_issues_found"] > gate["blocking_issues_resolved"]:
        errors.append(f"{gate['blocking_issues_found'] - gate['blocking_issues_resolved']} blocking issues not resolved")
    if not gate["plan_locked"]:
        errors.append("Plan is not locked. Compute SHA256 checksums and set plan_locked: true")
    if not gate["plan_checksum"]:
        errors.append("plan.md checksum missing")
    if not gate["security_design_checksum"]:
        errors.append("security-design.md checksum missing")

    return errors


def check_phase5(pi):
    """Phase 5 gate: Vault and Forge must complete."""
    gate = pi["phase_gates"]["phase5_build"]
    errors = []

    if not gate["vault_complete"]:
        errors.append("Vault has not completed schema build")
    if not gate["forge_complete"]:
        errors.append("Forge has not completed app/flow build")
    if gate["components_blocked"]:
        errors.append(f"Components blocked: {gate['components_blocked']}")

    return errors


def check_phase6(pi):
    """Phase 6 gate: Sentinel AND Warden must pass, no drift."""
    gate = pi["phase_gates"]["phase6_verify"]
    errors = []

    if not gate["sentinel_approved"]:
        errors.append("Sentinel verification not passed")
    if not gate["warden_approved"]:
        errors.append("Warden security verification not passed")
    if gate["security_tests_failed"] > 0:
        errors.append(f"{gate['security_tests_failed']} security tests failed")
    if gate["drift_detected"]:
        errors.append(f"Build drift detected: {gate['drift_items']}")

    return errors


GATE_CHECKS = {
    1: check_phase1,
    2: check_phase2,
    3: check_phase3,
    4: check_phase4,
    5: check_phase5,
    6: check_phase6,
}

GATE_NAMES = {
    1: "phase1_discovery",
    2: "phase2_planning",
    3: "phase3_review",
    4: "phase4_adversarial",
    5: "phase5_build",
    6: "phase6_verify",
}


def main():
    parser = argparse.ArgumentParser(description="Relay phase gate validator")
    parser.add_argument("--phase", type=int, required=True, choices=[1,2,3,4,5,6],
                        help="Phase number to validate (checks completion of this phase)")
    args = parser.parse_args()

    pi = load_plan_index()
    phase = args.phase
    check_fn = GATE_CHECKS.get(phase)

    if not check_fn:
        print(f"No gate check for phase {phase}")
        sys.exit(0)

    errors = check_fn(pi)

    if errors:
        print(f"\n🔴 GATE FAILED — Phase {phase} is not complete. Cannot advance.")
        for e in errors:
            print(f"  ✗ {e}")
        log_event("conductor", "gate_failed", phase, {"errors": errors})
        # Update plan-index
        gate_key = GATE_NAMES.get(phase)
        if gate_key and gate_key in pi["phase_gates"]:
            pi["phase_gates"][gate_key]["passed"] = False
        save_plan_index(pi)
        sys.exit(1)
    else:
        print(f"\n✅ GATE PASSED — Phase {phase} complete. Safe to advance.")
        gate_key = GATE_NAMES.get(phase)
        if gate_key and gate_key in pi["phase_gates"]:
            pi["phase_gates"][gate_key]["passed"] = True
            pi["phase_gates"][gate_key]["validated_at"] = datetime.now(timezone.utc).isoformat()
        save_plan_index(pi)
        log_event("conductor", "gate_passed", phase)
        sys.exit(0)


if __name__ == "__main__":
    main()

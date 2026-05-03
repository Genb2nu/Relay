#!/usr/bin/env python3
"""
relay-gate-check.py
Validates plan-index.json before a phase can advance.
Run by Conductor before invoking the next phase's agents.

Usage:
    python relay-gate-check.py --phase 0   # validate state.json scaffold before discovery
  python relay-gate-check.py --phase 1   # validate phase 1 requirements before phase 2
  python relay-gate-check.py --phase 2   # validate phase 2 requirements before phase 3
  python relay-gate-check.py --phase 3   # validate phase 3 requirements before phase 4
  python relay-gate-check.py --phase 4   # validate phase 4 requirements before phase 5
  python relay-gate-check.py --phase 5   # validate phase 5 requirements before phase 6
    python relay-gate-check.py --phase 6   # validate phase 6 requirements before completion

Exit codes:
  0 = gate passed, safe to advance
  1 = gate failed, block advancement
"""

import json
import sys
import os
import argparse
import tempfile
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT = os.path.dirname(SCRIPT_DIR)

PLAN_INDEX_PATH = ".relay/plan-index.json"
STATE_PATH = ".relay/state.json"
STATE_SCHEMA_PATH = os.path.join(PLUGIN_ROOT, "schemas", "state.schema.json")
LOG_PATH = ".relay/execution-log.jsonl"
WIREFRAMES_PATH = "docs/wireframes.html"
CONSISTENCY_CHECK_PATH = os.path.join(SCRIPT_DIR, "relay-consistency-check.py")


def load_json_file(path, description):
    if not os.path.exists(path):
        print(f"ERROR: {path} not found. Has Conductor initialised this project?")
        sys.exit(1)

    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as exc:
        print(f"ERROR: Invalid {description} at {path}:{exc.lineno}:{exc.colno}: {exc.msg}")
        sys.exit(1)
    except OSError as exc:
        print(f"ERROR: Could not read {description} at {path}: {exc}")
        sys.exit(1)


def load_plan_index():
    return load_json_file(PLAN_INDEX_PATH, "plan-index.json")


def load_state():
    return load_json_file(STATE_PATH, "state.json")


def load_state_schema():
    return load_json_file(STATE_SCHEMA_PATH, "state schema")


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
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def atomic_write_json(path, data):
    directory = os.path.dirname(path) or "."
    os.makedirs(directory, exist_ok=True)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile("w", delete=False, dir=directory, encoding="utf-8") as temp_file:
            json.dump(data, temp_file, indent=2)
            temp_path = temp_file.name
        os.replace(temp_path, path)
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


def save_plan_index(data):
    atomic_write_json(PLAN_INDEX_PATH, data)


def _matches_type(value, expected_type):
    if expected_type == "object":
        return isinstance(value, dict)
    if expected_type == "string":
        return isinstance(value, str)
    if expected_type == "boolean":
        return isinstance(value, bool)
    if expected_type == "null":
        return value is None
    return True


def _format_expected_types(expected_types):
    if isinstance(expected_types, list):
        return " or ".join(expected_types)
    return str(expected_types)


def validate_schema(data, schema, path="$"):
    errors = []

    expected_types = schema.get("type")
    if expected_types is not None:
        allowed_types = expected_types if isinstance(expected_types, list) else [expected_types]
        if not any(_matches_type(data, expected_type) for expected_type in allowed_types):
            actual_type = type(data).__name__
            errors.append(f"{path}: expected {_format_expected_types(expected_types)}, found {actual_type}")
            return errors

    if "enum" in schema and data not in schema["enum"]:
        errors.append(f"{path}: expected one of {schema['enum']}, found {data!r}")

    if isinstance(data, dict):
        properties = schema.get("properties", {})
        required = schema.get("required", [])

        for field_name in required:
            if field_name not in data:
                errors.append(f"{path}.{field_name}: missing required field")

        for field_name, field_value in data.items():
            field_path = f"{path}.{field_name}"
            if field_name in properties:
                errors.extend(validate_schema(field_value, properties[field_name], field_path))
                continue

            additional = schema.get("additionalProperties", True)
            if additional is False:
                errors.append(f"{field_path}: unexpected field")
            elif isinstance(additional, dict):
                errors.extend(validate_schema(field_value, additional, field_path))

    return errors


def check_phase0():
    """Phase 0 gate: state.json must match the scaffold schema."""
    state = load_state()
    schema = load_state_schema()
    return validate_schema(state, schema)


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
    if not os.path.exists(WIREFRAMES_PATH):
        errors.append("docs/wireframes.html does not exist")
    if not gate.get("wireframes_approved", False):
        errors.append("Wireframes are not approved — Conductor must set phase2_planning.wireframes_approved = true after user confirmation")
    if not gate["all_entities_have_columns"]:
        errors.append("Not all entities have column definitions")
    if not gate["all_flows_have_error_handling"]:
        errors.append("Not all flows have error handling specified")
    if gate["decision_needed_count"] > 0:
        errors.append(f"{gate['decision_needed_count']} DECISION NEEDED items unresolved — present to user before planning")

    # Run consistency check — catches lying agents
    import subprocess
    result = subprocess.run(
        [sys.executable, CONSISTENCY_CHECK_PATH],
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
    """Phase 5 gate: Vault and any applicable build specialists must complete."""
    gate = pi["phase_gates"]["phase5_build"]
    errors = []
    components = pi.get("components", {})

    if not gate["vault_complete"]:
        errors.append("Vault has not completed schema build")
    if components.get("canvas_apps") and not gate.get("canvas_app_complete", False):
        errors.append("Canvas App in plan but forge-canvas has not completed")
    if components.get("model_driven_apps") and not gate.get("mda_complete", False):
        errors.append("Model-Driven App in plan but forge-mda has not completed")
    if components.get("flows") and not gate.get("flows_documented", False):
        errors.append("Flows in plan but forge-flow has not produced a build guide")
    if components.get("power_pages") and not gate.get("power_pages_complete", False):
        errors.append("Power Pages in plan but forge-pages has not completed")
    if gate["components_blocked"]:
        errors.append(f"Components blocked: {gate['components_blocked']}")

    # Content verification — check actual artifacts, not just flags
    # Check for plugin DLL if plugins are in the plan
    if components.get("plugins"):
        plugin_dlls = [f for f in _find_files("src/plugins", "*.dll")]
        if not plugin_dlls:
            errors.append("Plugins in plan but no .dll found in src/plugins/ — build may not have compiled")

    # Check for the current flow output: build guide now, JSON artifacts later
    if components.get("flows"):
        flow_files = _find_files("src/flows", "*.json")
        flow_guide_path = "docs/flow-build-guide.md"
        if flow_files:
            for ff in flow_files:
                try:
                    with open(ff, encoding="utf-8") as fh:
                        flow_data = json.load(fh)
                    if "triggers" not in flow_data and "properties" in flow_data:
                        errors.append(f"{ff} appears ARM-shaped (has 'properties' but no 'triggers') — must be Dataverse clientData format")
                except Exception as e:
                    print(f"Error: {e}")
                    errors.append(f"{ff} could not be parsed: {e}")
        elif not os.path.exists(flow_guide_path):
            errors.append("Flows in plan but neither src/flows/*.json nor docs/flow-build-guide.md exists")

    # Check for essential scripts
    essential_scripts = []
    if components.get("plugins"):
        essential_scripts.append("scripts/register-plugins.ps1")
    if components.get("tables"):
        essential_scripts.append("scripts/seed-test-data.ps1")

    for script in essential_scripts:
        if not os.path.exists(script):
            errors.append(f"Required script missing: {script}")

    # Check canvas_app_bootstrapped if canvas app in plan
    if components.get("canvas_apps"):
        state_path = ".relay/state.json"
        if os.path.exists(state_path):
            state = load_json_file(state_path, "state.json")
            if not state.get("canvas_app_bootstrapped"):
                errors.append("Canvas App in plan but state.json.canvas_app_bootstrapped is not true")

    return errors


def _find_files(directory, pattern):
    """Find files matching a glob pattern in a directory."""
    import glob
    if not os.path.exists(directory):
        return []
    return glob.glob(os.path.join(directory, "**", pattern), recursive=True)


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
    0: check_phase0,
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
    parser.add_argument("--phase", type=int, required=True, choices=[0,1,2,3,4,5,6],
                        help="Phase number to validate (0 validates state scaffold; 1-6 validate completion of that phase)")
    args = parser.parse_args()

    phase = args.phase
    check_fn = GATE_CHECKS.get(phase)

    if not check_fn:
        print(f"No gate check for phase {phase}")
        sys.exit(0)

    if phase == 0:
        errors = check_fn()
        if errors:
            print("\n[BLOCK] GATE FAILED - Phase 0 scaffold is invalid. Cannot proceed to discovery.")
            for e in errors:
                print(f"  [FAIL] {e}")
            log_event("conductor", "gate_failed", phase, {"errors": errors})
            sys.exit(1)

        print("\n[PASS] GATE PASSED - Phase 0 scaffold is valid. Safe to begin discovery.")
        log_event("conductor", "gate_passed", phase)
        sys.exit(0)

    pi = load_plan_index()
    errors = check_fn(pi)

    if errors:
        print(f"\n[BLOCK] GATE FAILED - Phase {phase} is not complete. Cannot advance.")
        for e in errors:
            print(f"  [FAIL] {e}")
        log_event("conductor", "gate_failed", phase, {"errors": errors})
        # Update plan-index
        gate_key = GATE_NAMES.get(phase)
        if gate_key and gate_key in pi["phase_gates"]:
            pi["phase_gates"][gate_key]["passed"] = False
        save_plan_index(pi)
        sys.exit(1)
    else:
        print(f"\n[PASS] GATE PASSED - Phase {phase} complete. Safe to advance.")
        gate_key = GATE_NAMES.get(phase)
        if gate_key and gate_key in pi["phase_gates"]:
            pi["phase_gates"][gate_key]["passed"] = True
            pi["phase_gates"][gate_key]["validated_at"] = datetime.now(timezone.utc).isoformat()
        save_plan_index(pi)
        log_event("conductor", "gate_passed", phase)
        sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

#!/usr/bin/env python3
"""Regression tests for Relay phase gate enforcement."""

from __future__ import annotations

import json
import locale
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
GATE_SCRIPT = ROOT_DIR / "scripts" / "relay-gate-check.py"
PLAN_INDEX_TEMPLATE = ROOT_DIR / "schemas" / "plan-index.schema.json"
STATE_SCHEMA = ROOT_DIR / "schemas" / "state.schema.json"


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def scaffold_state(schema: dict) -> object:
    if "enum" in schema:
        return schema["enum"][0]

    schema_type = schema.get("type")
    types = schema_type if isinstance(schema_type, list) else [schema_type] if schema_type else []

    if "null" in types:
        return None
    if "object" in types:
        return {name: scaffold_state(value) for name, value in schema.get("properties", {}).items()}
    if "array" in types:
        return []
    if "boolean" in types:
        return False
    return ""


def run_gate(workspace: Path, phase: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(GATE_SCRIPT), "--phase", str(phase)],
        cwd=workspace,
        capture_output=True,
        text=True,
        encoding=locale.getpreferredencoding(False),
        errors="replace",
    )


def assert_contains(text: str, needle: str) -> None:
    if needle not in text:
        raise AssertionError(f"Expected to find {needle!r} in output:\n{text}")


def make_workspace() -> Path:
    workspace = Path(tempfile.mkdtemp(prefix="relay-gates-"))
    (workspace / ".relay").mkdir(parents=True, exist_ok=True)
    return workspace


def load_plan_index() -> dict:
    return json.loads(PLAN_INDEX_TEMPLATE.read_text(encoding="utf-8"))


def load_state() -> dict:
    schema = json.loads(STATE_SCHEMA.read_text(encoding="utf-8"))
    return scaffold_state(schema)


def test_phase1_requires_requirements_artifact() -> None:
    workspace = make_workspace()
    try:
        plan_index = load_plan_index()
        plan_index["phase_gates"]["phase1_discovery"]["sections_found"] = [
            "personas",
            "user_stories",
            "entities",
            "out_of_scope",
            "open_questions",
        ]
        plan_index["phase_gates"]["phase1_discovery"]["sections_missing"] = []
        plan_index["phase_gates"]["phase1_discovery"]["persona_count"] = 2
        plan_index["phase_gates"]["phase1_discovery"]["user_story_count"] = 5
        plan_index["phase_gates"]["phase1_discovery"]["entity_count"] = 1
        write_json(workspace / ".relay" / "plan-index.json", plan_index)

        missing_result = run_gate(workspace, 1)
        if missing_result.returncode != 1:
            raise AssertionError(f"Phase 1 should fail without requirements.md:\n{missing_result.stdout}\n{missing_result.stderr}")
        assert_contains(missing_result.stdout, "docs/requirements.md does not exist")

        requirements_path = workspace / "docs" / "requirements.md"
        requirements_path.parent.mkdir(parents=True, exist_ok=True)
        requirements_path.write_text("# Requirements\n\nReady for phase 2.\n", encoding="utf-8")

        pass_result = run_gate(workspace, 1)
        if pass_result.returncode != 0:
            raise AssertionError(f"Phase 1 should pass with requirements.md present:\n{pass_result.stdout}\n{pass_result.stderr}")
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def test_phase2_requires_build_ready_contract() -> None:
    workspace = make_workspace()
    try:
        plan_index = load_plan_index()
        phase2 = plan_index["phase_gates"]["phase2_planning"]
        phase2["plan_md_exists"] = True
        phase2["security_design_md_exists"] = True
        phase2["wireframes_complete"] = True
        phase2["wireframes_approved"] = True
        phase2["all_entities_have_columns"] = True
        phase2["all_flows_have_error_handling"] = True
        phase2["build_ready_for_vault"] = False
        plan_index["components"]["tables"] = [{"logical_name": "ecms_request", "display_name": "Request", "columns": 4}]
        plan_index["components"]["flows"] = [{"name": "Notify Request Owner", "trigger": "row_added_or_modified", "has_error_handling": True}]
        write_json(workspace / ".relay" / "plan-index.json", plan_index)

        plan_path = workspace / "docs" / "plan.md"
        plan_path.parent.mkdir(parents=True, exist_ok=True)
        plan_path.write_text(
            """# Implementation Plan — Shadow Test

## 3. Dataverse Schema
### ecms_request — Request
Ownership: User-owned.
Primary name: ecms_requestnumber.

| Logical Name | Display Name | Type | Required | Default | Description |
|---|---|---|---|---|---|
| ecms_requestnumber | Request Number | Autonumber | Required | Auto-generated | Primary name |
| ecms_status | Status | Choice | Required | Draft | Request status |

Autonumber format: REQ-{SEQNUM:6}
Status uses a global choice with options: Draft=100000000, Submitted=100000001

## 9. Power Automate Flows
Flow concurrency: sequential, degree=1.
Scope plus Configure run after handles failures.

## 12. Deployment and Operations Runbook
Build order:
1. Create solution
2. Create schema
3. Create roles
""",
            encoding="utf-8",
        )

        security_path = workspace / "docs" / "security-design.md"
        security_path.write_text(
            """# Security Design — Shadow Test

## 1. Threat Model
- Protect request data.

## 2. Authentication & Authorisation
- Internal users authenticate with Entra ID.

## 3. Security Role Matrix
- Request table uses least privilege.

## 4. Field-Level Security
- None for this shadow test.

## 5. Connection Reference Identity
- Use a shared service identity.
""",
            encoding="utf-8",
        )

        wireframes_path = workspace / "docs" / "wireframes.html"
        wireframes_path.write_text("<html><body>Wireframes</body></html>\n", encoding="utf-8")

        blocked_result = run_gate(workspace, 2)
        if blocked_result.returncode != 1:
            raise AssertionError(f"Phase 2 should fail when build_ready_for_vault is false:\n{blocked_result.stdout}\n{blocked_result.stderr}")
        assert_contains(blocked_result.stdout, "Plan is not build-ready for Vault")

        plan_index["phase_gates"]["phase2_planning"]["build_ready_for_vault"] = True
        write_json(workspace / ".relay" / "plan-index.json", plan_index)

        pass_result = run_gate(workspace, 2)
        if pass_result.returncode != 0:
            raise AssertionError(f"Phase 2 should pass when build_ready_for_vault is true and the plan contains build markers:\n{pass_result.stdout}\n{pass_result.stderr}")
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def test_phase5_requires_canvas_and_mda_artifacts() -> None:
    workspace = make_workspace()
    try:
        plan_index = load_plan_index()
        plan_index["phase_gates"]["phase5_build"]["vault_complete"] = True
        plan_index["phase_gates"]["phase5_build"]["stylist_complete"] = True
        plan_index["phase_gates"]["phase5_build"]["solution_component_count"] = 3
        plan_index["phase_gates"]["phase5_build"]["forge_canvas_complete"] = True
        plan_index["phase_gates"]["phase5_build"]["forge_mda_complete"] = True
        plan_index["components"]["canvas_apps"] = [{"name": "Contract Intake"}]
        plan_index["components"]["model_driven_apps"] = [{"name": "Contract Admin"}]
        write_json(workspace / ".relay" / "plan-index.json", plan_index)

        state = load_state()
        state["project_name"] = "Shadow Test"
        state["publisher_prefix"] = "ecms"
        state["environment_url"] = "https://example.crm.dynamics.com"
        state["solution_name"] = "ShadowTest"
        state["phase"] = "build"
        state["canvas_app_bootstrapped"] = True
        write_json(workspace / ".relay" / "state.json", state)

        missing_result = run_gate(workspace, 5)
        if missing_result.returncode != 1:
            raise AssertionError(f"Phase 5 should fail without Canvas/MDA artifacts:\n{missing_result.stdout}\n{missing_result.stderr}")
        assert_contains(missing_result.stdout, "no .pa.yaml found in src/canvas-apps/")
        assert_contains(missing_result.stdout, "scripts/apply-mda-sitemap.ps1 is missing")

        canvas_path = workspace / "src" / "canvas-apps" / "contract-intake.pa.yaml"
        canvas_path.parent.mkdir(parents=True, exist_ok=True)
        canvas_path.write_text("App:\n  Name: Contract Intake\n", encoding="utf-8")

        sitemap_path = workspace / "src" / "mda" / "sitemap.xml"
        sitemap_path.parent.mkdir(parents=True, exist_ok=True)
        sitemap_path.write_text("<SiteMap />\n", encoding="utf-8")

        deploy_script = workspace / "scripts" / "apply-mda-sitemap.ps1"
        deploy_script.parent.mkdir(parents=True, exist_ok=True)
        deploy_script.write_text("Write-Host 'Apply sitemap'\n", encoding="utf-8")

        pass_result = run_gate(workspace, 5)
        if pass_result.returncode != 0:
            raise AssertionError(f"Phase 5 should pass with Canvas/MDA artifacts present:\n{pass_result.stdout}\n{pass_result.stderr}")
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def test_phase5_requires_forge_for_environment_variables() -> None:
    workspace = make_workspace()
    try:
        plan_index = load_plan_index()
        plan_index["phase_gates"]["phase5_build"]["vault_complete"] = True
        plan_index["phase_gates"]["phase5_build"]["stylist_complete"] = True
        plan_index["phase_gates"]["phase5_build"]["solution_component_count"] = 1
        plan_index["components"]["environment_variables"] = [{"name": "API_BASE_URL"}]
        write_json(workspace / ".relay" / "plan-index.json", plan_index)

        state = load_state()
        state["project_name"] = "Shadow Test"
        state["publisher_prefix"] = "ecms"
        state["environment_url"] = "https://example.crm.dynamics.com"
        state["solution_name"] = "ShadowTest"
        state["phase"] = "build"
        write_json(workspace / ".relay" / "state.json", state)

        missing_result = run_gate(workspace, 5)
        if missing_result.returncode != 1:
            raise AssertionError(f"Phase 5 should fail when Forge-owned env vars are planned but Forge has not completed:\n{missing_result.stdout}\n{missing_result.stderr}")
        assert_contains(missing_result.stdout, "Forge-owned artifacts are in plan but forge has not completed")

        plan_index["phase_gates"]["phase5_build"]["forge_complete"] = True
        write_json(workspace / ".relay" / "plan-index.json", plan_index)

        pass_result = run_gate(workspace, 5)
        if pass_result.returncode != 0:
            raise AssertionError(f"Phase 5 should pass when Forge completes env vars work:\n{pass_result.stdout}\n{pass_result.stderr}")
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def test_phase5_allows_flow_only_manual_builds_without_solution_components() -> None:
    workspace = make_workspace()
    try:
        plan_index = load_plan_index()
        plan_index["phase_gates"]["phase5_build"]["vault_complete"] = True
        plan_index["phase_gates"]["phase5_build"]["stylist_complete"] = True
        plan_index["phase_gates"]["phase5_build"]["forge_flow_complete"] = True
        plan_index["phase_gates"]["phase5_build"]["solution_component_count"] = 0
        plan_index["phase_gates"]["phase5_build"]["flow_count"] = 1
        plan_index["components"]["flows"] = [{"name": "Notify Manager"}]
        write_json(workspace / ".relay" / "plan-index.json", plan_index)

        state = load_state()
        state["project_name"] = "Shadow Test"
        state["publisher_prefix"] = "ecms"
        state["environment_url"] = "https://example.crm.dynamics.com"
        state["solution_name"] = "ShadowTest"
        state["phase"] = "build"
        write_json(workspace / ".relay" / "state.json", state)

        flow_guide = workspace / "docs" / "flow-build-guide.md"
        flow_guide.parent.mkdir(parents=True, exist_ok=True)
        flow_guide.write_text("# Flow Build Guide\n\n## Flow 1 — Notify Manager\n", encoding="utf-8")

        pass_result = run_gate(workspace, 5)
        if pass_result.returncode != 0:
            raise AssertionError(f"Flow-only/manual Phase 5 should pass without solution-backed artifacts:\n{pass_result.stdout}\n{pass_result.stderr}")
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def test_phase5_requires_power_pages_artifacts() -> None:
    workspace = make_workspace()
    try:
        plan_index = load_plan_index()
        plan_index["phase_gates"]["phase5_build"]["vault_complete"] = True
        plan_index["phase_gates"]["phase5_build"]["stylist_complete"] = True
        plan_index["phase_gates"]["phase5_build"]["forge_pages_complete"] = True
        plan_index["phase_gates"]["phase5_build"]["solution_component_count"] = 0
        plan_index["components"]["power_pages"] = [{"name": "Partner Portal"}]
        write_json(workspace / ".relay" / "plan-index.json", plan_index)

        state = load_state()
        state["project_name"] = "Shadow Test"
        state["publisher_prefix"] = "ecms"
        state["environment_url"] = "https://example.crm.dynamics.com"
        state["solution_name"] = "ShadowTest"
        state["phase"] = "build"
        write_json(workspace / ".relay" / "state.json", state)

        missing_result = run_gate(workspace, 5)
        if missing_result.returncode != 1:
            raise AssertionError(f"Phase 5 should fail when Power Pages output is missing:\n{missing_result.stdout}\n{missing_result.stderr}")
        assert_contains(missing_result.stdout, "no source artifacts found in src/pages/")

        empty_dir = workspace / "src" / "pages" / "emptydir"
        empty_dir.mkdir(parents=True, exist_ok=True)

        empty_dir_result = run_gate(workspace, 5)
        if empty_dir_result.returncode != 1:
            raise AssertionError(f"Phase 5 should still fail when src/pages only contains directories:\n{empty_dir_result.stdout}\n{empty_dir_result.stderr}")
        assert_contains(empty_dir_result.stdout, "no source artifacts found in src/pages/")

        page_path = workspace / "src" / "pages" / "index.html"
        page_path.parent.mkdir(parents=True, exist_ok=True)
        page_path.write_text("<html><body>Portal</body></html>\n", encoding="utf-8")

        pass_result = run_gate(workspace, 5)
        if pass_result.returncode != 0:
            raise AssertionError(f"Power Pages-only Phase 5 should pass once src/pages output exists:\n{pass_result.stdout}\n{pass_result.stderr}")
    finally:
        shutil.rmtree(workspace, ignore_errors=True)


def main() -> None:
    tests = [
        ("Phase 1 requires requirements artifact", test_phase1_requires_requirements_artifact),
        ("Phase 2 requires build-ready contract", test_phase2_requires_build_ready_contract),
        ("Phase 5 requires Canvas and MDA artifacts", test_phase5_requires_canvas_and_mda_artifacts),
        ("Phase 5 requires Forge for environment variables", test_phase5_requires_forge_for_environment_variables),
        ("Phase 5 allows flow-only manual builds", test_phase5_allows_flow_only_manual_builds_without_solution_components),
        ("Phase 5 requires Power Pages artifacts", test_phase5_requires_power_pages_artifacts),
    ]

    passed = 0
    for name, fn in tests:
        fn()
        print(f"PASS: {name}")
        passed += 1

    print(f"All {passed} gate regression tests passed.")


if __name__ == "__main__":
    main()

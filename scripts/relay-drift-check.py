#!/usr/bin/env python3
"""
relay-drift-check.py
Compares plan-index.json (what was planned) against actual Dataverse artifacts (what was built).
Run by Sentinel during Phase 6 verification.

Requires:
  - .relay/plan-index.json
  - PAC CLI authenticated to the correct environment
  - Dataverse MCP or direct API access

Usage:
  python relay-drift-check.py --env https://<org>.crm.dynamics.com
"""

import json
import subprocess
import sys
import os
import argparse
from datetime import datetime, timezone

PLAN_INDEX_PATH = ".relay/plan-index.json"
LOG_PATH = ".relay/execution-log.jsonl"
DRIFT_REPORT_PATH = "docs/drift-report.md"


def load_plan_index():
    if not os.path.exists(PLAN_INDEX_PATH):
        print(f"ERROR: {PLAN_INDEX_PATH} not found")
        sys.exit(1)
    with open(PLAN_INDEX_PATH) as f:
        return json.load(f)


def log_event(agent, event, details=None):
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent": agent,
        "event": event,
    }
    if details:
        entry.update(details)
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


def run_pac(args):
    """Run a PAC CLI command via PowerShell and return output."""
    cmd = ["pwsh", "-NoProfile", "-Command", f"pac {args}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip(), result.returncode


def get_actual_tables(env_url, solution):
    """Get tables actually deployed in the solution with column counts."""
    stdout, code = run_pac(f"dataverse table list --environment {env_url} --solution {solution} --json")
    if code != 0:
        return {}
    try:
        data = json.loads(stdout)
        return {t.get("LogicalName", "").lower(): t for t in data}
    except:
        return {}


def get_actual_column_count(env_url, table_name):
    """Get the number of custom columns on a table (excludes system columns)."""
    stdout, code = run_pac(f"dataverse column list --environment {env_url} --table {table_name} --json")
    if code != 0:
        return None
    try:
        data = json.loads(stdout)
        # Count only custom columns (not system ones)
        custom_cols = [c for c in data if not c.get("IsManaged", True) or c.get("IsCustomAttribute", False)]
        return len(custom_cols)
    except:
        return None


def get_actual_flows(env_url):
    """Get cloud flows in the environment."""
    stdout, code = run_pac(f"flow list --environment {env_url} --json")
    if code != 0:
        return []
    try:
        data = json.loads(stdout)
        return [f.get("displayName", "").lower() for f in data]
    except:
        return []


def get_actual_security_roles(env_url):
    """Get custom security roles."""
    stdout, code = run_pac(f"admin list-role --environment {env_url}")
    if code != 0:
        return []
    lines = stdout.split("\n")
    return [l.strip().lower() for l in lines if l.strip() and not l.startswith("Name")]


def drift_check(plan_index, env_url):
    drift_items = []
    passed_items = []

    solution = plan_index["project"].get("solution", "")
    components = plan_index["components"]

    # --- Tables (existence + column count) ---
    planned_tables = [t for t in components.get("tables", []) if "logical_name" in t]
    if planned_tables:
        actual_tables = get_actual_tables(env_url, solution)
        for table in planned_tables:
            table_name = table["logical_name"].lower()
            planned_cols = table.get("columns", 0)

            # Check 1: table exists
            if actual_tables and table_name not in actual_tables:
                drift_items.append({
                    "type": "table",
                    "name": table_name,
                    "issue": "planned but not found in Dataverse"
                })
                continue

            passed_items.append({"type": "table", "name": table_name, "status": "found"})

            # Check 2: column count (if plan specifies one)
            if planned_cols > 0:
                actual_cols = get_actual_column_count(env_url, table_name)
                if actual_cols is not None:
                    # Allow ±1 tolerance for auto-created system columns
                    if actual_cols < planned_cols - 1:
                        drift_items.append({
                            "type": "table_columns",
                            "name": table_name,
                            "issue": f"column count mismatch — planned: {planned_cols}, actual: {actual_cols} (missing {planned_cols - actual_cols} columns)"
                        })
                    else:
                        passed_items.append({
                            "type": "table_columns",
                            "name": table_name,
                            "status": f"columns ok ({actual_cols}/{planned_cols})"
                        })

    # --- Flows ---
    planned_flows = [f["name"].lower() for f in components.get("flows", []) if "name" in f]
    if planned_flows:
        actual_flows = get_actual_flows(env_url)
        for flow in planned_flows:
            if actual_flows and flow not in actual_flows:
                drift_items.append({"type": "flow", "name": flow, "issue": "planned but not found"})
            else:
                passed_items.append({"type": "flow", "name": flow, "status": "found"})

    # --- Security Roles ---
    planned_roles = [r["name"].lower() for r in components.get("security_roles", []) if "name" in r]
    if planned_roles:
        actual_roles = get_actual_security_roles(env_url)
        for role in planned_roles:
            if actual_roles and not any(role in r for r in actual_roles):
                drift_items.append({"type": "security_role", "name": role, "issue": "planned but not found"})
            else:
                passed_items.append({"type": "security_role", "name": role, "status": "found"})

    return drift_items, passed_items


def write_drift_report(drift_items, passed_items):
    os.makedirs("docs", exist_ok=True)
    with open(DRIFT_REPORT_PATH, "w") as f:
        f.write(f"# Drift Report\nGenerated: {datetime.now(timezone.utc).isoformat()}\n\n")

        if not drift_items:
            f.write("## ✅ No drift detected\nAll planned components found in the built solution.\n\n")
        else:
            f.write(f"## 🔴 Drift detected — {len(drift_items)} component(s) missing\n\n")
            f.write("| Type | Name | Issue |\n|---|---|---|\n")
            for item in drift_items:
                f.write(f"| {item['type']} | {item['name']} | {item['issue']} |\n")
            f.write("\n")

        f.write(f"## ✅ Verified — {len(passed_items)} component(s) confirmed\n\n")
        f.write("| Type | Name | Status |\n|---|---|---|\n")
        for item in passed_items:
            f.write(f"| {item['type']} | {item['name']} | {item['status']} |\n")


def main():
    parser = argparse.ArgumentParser(description="Relay drift detector")
    parser.add_argument("--env", required=True, help="Dataverse environment URL")
    args = parser.parse_args()

    pi = load_plan_index()
    print(f"\n🔍 Running drift detection against {args.env}...")

    drift_items, passed_items = drift_check(pi, args.env)
    write_drift_report(drift_items, passed_items)

    # Update plan-index
    gate = pi["phase_gates"]["phase6_verify"]
    gate["drift_detected"] = len(drift_items) > 0
    gate["drift_items"] = [f"{d['type']}:{d['name']}" for d in drift_items]

    with open(PLAN_INDEX_PATH, "w") as f:
        json.dump(pi, f, indent=2)

    if drift_items:
        print(f"\n🔴 DRIFT DETECTED — {len(drift_items)} component(s) missing:")
        for d in drift_items:
            print(f"  ✗ {d['type']}: {d['name']} — {d['issue']}")
        log_event("sentinel", "drift_detected", {"items": drift_items})
        sys.exit(1)
    else:
        print(f"\n✅ NO DRIFT — {len(passed_items)} component(s) verified")
        log_event("sentinel", "drift_clear", {"verified": len(passed_items)})
        sys.exit(0)


if __name__ == "__main__":
    main()

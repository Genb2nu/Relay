#!/usr/bin/env bash
# Phase gate hook for sn-plugin
# Runs after Write/Edit to enforce phase-gate conditions.
# Checks that required files exist before allowing phase advancement.

set -euo pipefail

STATE_FILE=".sn/state.json"

# Only run if this is a SimplifyNext project
if [[ ! -f "$STATE_FILE" ]]; then
  exit 0
fi

PHASE=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('phase','unknown'))" 2>/dev/null || echo "unknown")

run_gate() {
  local gate_phase="$1"
  local errors=()

  case "$gate_phase" in
    "discovery")
      [[ ! -f "docs/requirements.md" ]] && errors+=("MISSING: docs/requirements.md")
      ;;

    "planning")
      [[ ! -f "docs/plan.md" ]] && errors+=("MISSING: docs/plan.md")
      [[ ! -f "docs/security-design.md" ]] && errors+=("MISSING: docs/security-design.md")
      ;;

    "review")
      APPROVED=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(str(d.get('auditor_approved', False)).lower())" 2>/dev/null || echo "false")
      [[ "$APPROVED" != "true" ]] && errors+=("GATE FAIL: auditor_approved is not true")
      ;;

    "build")
      LOCKED=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(str(d.get('plan_locked', False)).lower())" 2>/dev/null || echo "false")
      [[ "$LOCKED" != "true" ]] && errors+=("GATE FAIL: plan_locked is not true — run /sn-plan-review")
      ;;

    "qa")
      BUILD_TS=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('build_completed_at',''))" 2>/dev/null || echo "")
      [[ -z "$BUILD_TS" ]] && errors+=("GATE FAIL: build_completed_at not set — run /sn-build first")
      ;;

    "complete")
      SENTINEL=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(str(d.get('sentinel_approved', False)).lower())" 2>/dev/null || echo "false")
      [[ "$SENTINEL" != "true" ]] && errors+=("GATE FAIL: sentinel_approved is not true — run /sn-qa first")
      ;;
  esac

  if [[ ${#errors[@]} -gt 0 ]]; then
    echo ""
    echo "=== sn-plugin Phase Gate: $gate_phase ==="
    for err in "${errors[@]}"; do
      echo "  ❌ $err"
    done
    echo ""
    echo "Fix the above issues before advancing to the next phase."
    echo ""
    return 1
  else
    return 0
  fi
}

# Run the gate for the current phase
run_gate "$PHASE" || true

# Additional consistency checks after plan files are written
if [[ -f "docs/plan.md" && -f "docs/requirements.md" ]]; then
  # Check that plan has at least one table defined
  if ! grep -q "logical_name\|LogicalName\|prefix" "docs/plan.md" 2>/dev/null; then
    echo "⚠️  Warning: docs/plan.md may be missing table definitions."
    echo "   Ensure all tables have logical names using the publisher prefix."
  fi
fi

exit 0

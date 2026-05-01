#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd -P)
PRE_TOOL_HOOK="$ROOT_DIR/hooks/scripts/pre-tool-use.sh"
PHASE_GATE_HOOK="$ROOT_DIR/hooks/scripts/phase-gate-hook.sh"

pass_count=0

pass() {
  echo "PASS: $1"
  pass_count=$((pass_count + 1))
}

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

run_pre_tool_case() {
  local agent="$1"
  local path="$2"
  local expected_exit="$3"
  local workspace
  local rc=0

  workspace=$(mktemp -d)
  mkdir -p "$workspace/.relay"

  if [ -n "$agent" ]; then
    export CLAUDE_AGENT="$agent"
  else
    unset CLAUDE_AGENT || true
  fi

  printf '{"params":{"path":"%s"}}' "$path" | (cd "$workspace" && bash "$PRE_TOOL_HOOK") >/dev/null 2>&1 || rc=$?

  unset CLAUDE_AGENT || true
  rm -rf "$workspace"

  if [ "$rc" -ne "$expected_exit" ]; then
    fail "pre-tool-use for agent='${agent:-unset}' path='$path' returned $rc, expected $expected_exit"
  fi
}

write_plan_index() {
  local workspace="$1"
  local plan_locked="$2"
  local phase4_passed="$3"

  mkdir -p "$workspace/.relay"
  cat > "$workspace/.relay/plan-index.json" <<EOF
{
  "phase_gates": {
    "phase4_adversarial": {
      "plan_locked": $plan_locked,
      "passed": $phase4_passed
    },
    "phase5_build": {
      "passed": false
    },
    "phase6_verify": {
      "passed": false,
      "sentinel_approved": false,
      "warden_approved": false
    }
  }
}
EOF
}

run_phase_gate_case() {
  local plan_locked="$1"
  local phase4_passed="$2"
  local expected_exit="$3"
  local workspace
  local rc=0

  workspace=$(mktemp -d)
  write_plan_index "$workspace" "$plan_locked" "$phase4_passed"

  printf '{"params":{"command":"pac solution import --path build.zip"}}' | (cd "$workspace" && bash "$PHASE_GATE_HOOK") >/dev/null 2>&1 || rc=$?

  rm -rf "$workspace"

  if [ "$rc" -ne "$expected_exit" ]; then
    fail "phase-gate-hook with plan_locked=$plan_locked phase4_passed=$phase4_passed returned $rc, expected $expected_exit"
  fi
}

run_pre_tool_case "" "docs/test-report.md" 2
pass "CLAUDE_AGENT unset denies writes"

run_pre_tool_case "stylist" "docs/test-report.md" 2
pass "Stylist is restricted to its allowed docs output"

run_pre_tool_case "conductor" "docs/test-report.md" 0
pass "Conductor retains write access"

run_phase_gate_case false false 2
pass "pac solution import is blocked before Phase 4 completion"

run_phase_gate_case true true 0
pass "pac solution import is allowed after Phase 4 completion"

echo "All ${pass_count} hook regression tests passed."
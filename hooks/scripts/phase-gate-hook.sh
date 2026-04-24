#!/bin/bash
# Relay — Phase Gate Hook
# Intercepts Bash tool calls that indicate phase advancement
# and runs relay-gate-check.py to validate current gate before proceeding.
#
# Phase advancement indicators:
#   Phase 4→5 (build start): pac solution create, pac dataverse table, pac auth select
#   Phase 5→6 (verify start): pac solution check, sentinel test commands
#   Phase 6→7 (ship):         pac solution export --managed
#
# Exit codes:
#   0 = allow
#   2 = block

set -e

TOOL_INPUT=$(cat)
COMMAND=$(echo "$TOOL_INPUT" | jq -r '.params.command // empty' 2>/dev/null)

if [ -z "$COMMAND" ]; then
  exit 0
fi

PLAN_INDEX=".relay/plan-index.json"
LOG=".relay/execution-log.jsonl"

log_event() {
  local event="$1"
  local reason="$2"
  if [ -d ".relay" ]; then
    echo "{\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",\"agent\":\"hook\",\"event\":\"$event\",\"reason\":\"$reason\"}" >> "$LOG" 2>/dev/null || true
  fi
}

# --- Gate: Phase 4 must be complete before build commands run ---
BUILD_PATTERNS="pac solution create|pac dataverse table|pac dataverse column|pac admin list-role"
if echo "$COMMAND" | grep -qE "$BUILD_PATTERNS"; then
  if [ -f "$PLAN_INDEX" ]; then
    PLAN_LOCKED=$(jq -r '.phase_gates.phase4_adversarial.plan_locked // false' "$PLAN_INDEX" 2>/dev/null)
    PHASE4_PASSED=$(jq -r '.phase_gates.phase4_adversarial.passed // false' "$PLAN_INDEX" 2>/dev/null)

    if [ "$PLAN_LOCKED" != "true" ] || [ "$PHASE4_PASSED" != "true" ]; then
      echo "" >&2
      echo "🔴 GATE BLOCKED: Build commands cannot run until Phase 4 is complete." >&2
      echo "   Plan locked: $PLAN_LOCKED | Phase 4 passed: $PHASE4_PASSED" >&2
      echo "   The plan must be approved by Auditor + Warden + Critic and locked" >&2
      echo "   before Vault or Forge can start building." >&2
      echo "   Run /relay:plan-review if the plan needs re-review." >&2
      log_event "gate_blocked" "build attempted before phase 4 complete"
      exit 2
    fi
  fi
fi

# --- Gate: Phase 5 must be complete before verification commands run ---
VERIFY_PATTERNS="relay-drift-check|security-tests.ps1|sentinel"
if echo "$COMMAND" | grep -qE "$VERIFY_PATTERNS"; then
  if [ -f "$PLAN_INDEX" ]; then
    PHASE5_PASSED=$(jq -r '.phase_gates.phase5_build.passed // false' "$PLAN_INDEX" 2>/dev/null)

    if [ "$PHASE5_PASSED" != "true" ]; then
      echo "" >&2
      echo "🔴 GATE BLOCKED: Verification cannot run until Phase 5 (Build) is complete." >&2
      echo "   Phase 5 passed: $PHASE5_PASSED" >&2
      echo "   Vault and Forge must complete before Sentinel and Warden verify." >&2
      log_event "gate_blocked" "verification attempted before phase 5 complete"
      exit 2
    fi
  fi
fi

# --- Gate: Phase 6 must be complete before managed solution export ---
if echo "$COMMAND" | grep -qE "pac solution export.*--managed|pac solution export.*-m "; then
  if [ -f "$PLAN_INDEX" ]; then
    PHASE6_PASSED=$(jq -r '.phase_gates.phase6_verify.passed // false' "$PLAN_INDEX" 2>/dev/null)
    SENTINEL=$(jq -r '.phase_gates.phase6_verify.sentinel_approved // false' "$PLAN_INDEX" 2>/dev/null)
    WARDEN=$(jq -r '.phase_gates.phase6_verify.warden_approved // false' "$PLAN_INDEX" 2>/dev/null)

    if [ "$PHASE6_PASSED" != "true" ]; then
      echo "" >&2
      echo "🔴 GATE BLOCKED: Cannot export managed solution until Phase 6 verification passes." >&2
      echo "   Sentinel approved: $SENTINEL | Warden approved: $WARDEN" >&2
      echo "   Both Sentinel and Warden must pass before the solution can ship." >&2
      log_event "gate_blocked" "export attempted before phase 6 complete"
      exit 2
    fi
  fi
fi

exit 0

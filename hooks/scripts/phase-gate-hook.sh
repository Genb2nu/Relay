#!/bin/bash
# Relay — Phase Gate Hook
# Intercepts Bash tool calls that indicate phase advancement
# and runs relay-gate-check.py to validate current gate before proceeding.
#
# Phase advancement indicators:
#   Phase 4→5 (build start): pac solution create/import, pac dataverse table/column,
#                             pac plugin push, activate-flows.ps1, dotnet build
#   Phase 5→6 (verify start): pac solution check, sentinel test commands
#   Phase 6→7 (complete):     pac solution export (all variants)
#
# Exit codes:
#   0 = allow
#   2 = block

set -e

json_python() {
  if command -v python3 >/dev/null 2>&1; then
    echo python3
    return 0
  fi

  if command -v python >/dev/null 2>&1; then
    echo python
    return 0
  fi

  return 1
}

json_get_from_text() {
  local json_input="$1"
  local path="$2"
  local default_value="$3"
  local pybin

  pybin=$(json_python) || {
    echo "$default_value"
    return 0
  }

  JSON_INPUT="$json_input" "$pybin" - "$path" "$default_value" <<'PY'
import json
import os
import sys

path = sys.argv[1]
default_value = sys.argv[2]

try:
    data = json.loads(os.environ.get("JSON_INPUT", ""))
except Exception:
    print(default_value)
    raise SystemExit(0)

current = data
for part in path.split("."):
    if not part:
        continue
    if isinstance(current, dict) and part in current:
        current = current[part]
    else:
        print(default_value)
        raise SystemExit(0)

if current is None:
    print(default_value)
elif isinstance(current, bool):
    print("true" if current else "false")
else:
    print(current)
PY
}

json_get_from_file() {
  local file_path="$1"
  local path="$2"
  local default_value="$3"
  local pybin

  pybin=$(json_python) || {
    echo "$default_value"
    return 0
  }

  "$pybin" - "$file_path" "$path" "$default_value" <<'PY'
import json
import sys

file_path, path, default_value = sys.argv[1:4]

try:
    with open(file_path, encoding="utf-8") as handle:
        data = json.load(handle)
except Exception:
    print(default_value)
    raise SystemExit(0)

current = data
for part in path.split("."):
    if not part:
        continue
    if isinstance(current, dict) and part in current:
        current = current[part]
    else:
        print(default_value)
        raise SystemExit(0)

if current is None:
    print(default_value)
elif isinstance(current, bool):
    print("true" if current else "false")
else:
    print(current)
PY
}

TOOL_INPUT=$(cat)
COMMAND=$(json_get_from_text "$TOOL_INPUT" "params.command" "")

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
BUILD_PATTERNS="pac solution create([[:space:]]|$)|pac solution import([[:space:]]|$)|pac dataverse table([[:space:]]|$)|pac dataverse column([[:space:]]|$)|pac admin list-role([[:space:]]|$)|pac plugin push([[:space:]]|$)|activate-flows\.ps1|dotnet build([[:space:]]|$)"
if echo "$COMMAND" | grep -qE "$BUILD_PATTERNS"; then
  if [ -f "$PLAN_INDEX" ]; then
    PLAN_LOCKED=$(json_get_from_file "$PLAN_INDEX" "phase_gates.phase4_adversarial.plan_locked" "false")
    PHASE4_PASSED=$(json_get_from_file "$PLAN_INDEX" "phase_gates.phase4_adversarial.passed" "false")

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
    PHASE5_PASSED=$(json_get_from_file "$PLAN_INDEX" "phase_gates.phase5_build.passed" "false")

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

# --- Gate: Phase 6 must be complete before any solution export ---
if echo "$COMMAND" | grep -qE "pac solution export([[:space:]]|$)"; then
  if [ -f "$PLAN_INDEX" ]; then
    PHASE6_PASSED=$(json_get_from_file "$PLAN_INDEX" "phase_gates.phase6_verify.passed" "false")
    SENTINEL=$(json_get_from_file "$PLAN_INDEX" "phase_gates.phase6_verify.sentinel_approved" "false")
    WARDEN=$(json_get_from_file "$PLAN_INDEX" "phase_gates.phase6_verify.warden_approved" "false")

    if [ "$PHASE6_PASSED" != "true" ]; then
      echo "" >&2
      echo "🔴 GATE BLOCKED: Cannot export managed solution until Phase 6 verification passes." >&2
      echo "   Sentinel approved: $SENTINEL | Warden approved: $WARDEN" >&2
      echo "   Both Sentinel and Warden must pass before the solution can be exported and the workflow can complete." >&2
      log_event "gate_blocked" "export attempted before phase 6 complete"
      exit 2
    fi
  fi
fi

exit 0

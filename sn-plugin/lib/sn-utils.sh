#!/usr/bin/env bash
# sn-utils.sh — Shared utility functions for sn-plugin scripts

set -euo pipefail

SN_STATE_FILE=".sn/state.json"
SN_LOG_FILE=".sn/execution-log.jsonl"

# ─────────────────────────────────────────────
# State management
# ─────────────────────────────────────────────

sn_read_state() {
  local key="$1"
  python3 -c "import json,sys; d=json.load(open('$SN_STATE_FILE')); print(d.get('$key',''))" 2>/dev/null || echo ""
}

sn_write_state() {
  local key="$1"
  local value="$2"
  python3 - <<EOF
import json
with open('$SN_STATE_FILE', 'r') as f:
    d = json.load(f)
d['$key'] = '$value'
with open('$SN_STATE_FILE', 'w') as f:
    json.dump(d, f, indent=2)
EOF
}

sn_state_exists() {
  [[ -f "$SN_STATE_FILE" ]]
}

sn_require_state() {
  if ! sn_state_exists; then
    echo "ERROR: No SimplifyNext project found. Run /sn-start to initialise."
    exit 1
  fi
}

# ─────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────

sn_log() {
  local agent="$1"
  local event="$2"
  local phase="${3:-$(sn_read_state phase)}"
  local extras="${4:-}"

  local timestamp
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

  local entry="{\"timestamp\": \"$timestamp\", \"agent\": \"$agent\", \"event\": \"$event\", \"phase\": \"$phase\""
  if [[ -n "$extras" ]]; then
    entry="$entry, $extras"
  fi
  entry="$entry}"

  mkdir -p "$(dirname "$SN_LOG_FILE")"
  echo "$entry" >> "$SN_LOG_FILE"
}

# ─────────────────────────────────────────────
# Validation helpers
# ─────────────────────────────────────────────

sn_validate_prefix() {
  local prefix="$1"
  if [[ ! "$prefix" =~ ^[a-z]{2,8}$ ]]; then
    echo "ERROR: Publisher prefix must be 2-8 lowercase letters. Got: '$prefix'"
    return 1
  fi
}

sn_validate_env_url() {
  local url="$1"
  if [[ ! "$url" =~ ^https://.*\.dynamics\.com ]]; then
    echo "WARNING: Environment URL should match https://<org>.dynamics.com. Got: '$url'"
    return 1
  fi
}

sn_validate_phase() {
  local required_phase="$1"
  local current_phase
  current_phase=$(sn_read_state phase)

  local -a valid_phases=("discovery" "planning" "review" "build" "qa" "complete")
  local required_idx=-1
  local current_idx=-1

  for i in "${!valid_phases[@]}"; do
    [[ "${valid_phases[$i]}" == "$required_phase" ]] && required_idx=$i
    [[ "${valid_phases[$i]}" == "$current_phase" ]] && current_idx=$i
  done

  if [[ $current_idx -lt $required_idx ]]; then
    echo "ERROR: Current phase is '$current_phase'. Required phase: '$required_phase' or later."
    return 1
  fi
}

# ─────────────────────────────────────────────
# Phase gate checks
# ─────────────────────────────────────────────

sn_check_gate() {
  local phase="$1"
  local errors=0

  case "$phase" in
    "planning")
      [[ ! -f "docs/plan.md" ]] && { echo "GATE FAIL: docs/plan.md missing"; errors=$((errors+1)); }
      [[ ! -f "docs/security-design.md" ]] && { echo "GATE FAIL: docs/security-design.md missing"; errors=$((errors+1)); }
      ;;
    "review")
      local approved
      approved=$(sn_read_state auditor_approved)
      [[ "$approved" != "true" ]] && { echo "GATE FAIL: auditor_approved is not true"; errors=$((errors+1)); }
      ;;
    "build")
      local locked
      locked=$(sn_read_state plan_locked)
      [[ "$locked" != "true" ]] && { echo "GATE FAIL: plan is not locked — run /sn-plan-review"; errors=$((errors+1)); }
      ;;
    "qa")
      local build_ts
      build_ts=$(sn_read_state build_completed_at)
      [[ -z "$build_ts" ]] && { echo "GATE FAIL: build not complete — run /sn-build first"; errors=$((errors+1)); }
      ;;
    "complete")
      local sentinel_ok
      sentinel_ok=$(sn_read_state sentinel_approved)
      [[ "$sentinel_ok" != "true" ]] && { echo "GATE FAIL: sentinel_approved is not true — run /sn-qa"; errors=$((errors+1)); }
      ;;
  esac

  return $errors
}

# ─────────────────────────────────────────────
# Output helpers
# ─────────────────────────────────────────────

sn_print_header() {
  local title="$1"
  echo ""
  echo "=== $title ==="
  echo ""
}

sn_print_success() {
  echo "✅ $1"
}

sn_print_error() {
  echo "❌ $1"
}

sn_print_warning() {
  echo "⚠️  $1"
}

sn_print_pending() {
  echo "⏳ $1"
}

# ─────────────────────────────────────────────
# Component GUID helpers
# ─────────────────────────────────────────────

sn_get_component_guid() {
  local type="$1"   # tables, flows, security_roles, etc.
  local name="$2"
  python3 -c "
import json
with open('$SN_STATE_FILE') as f:
    d = json.load(f)
print(d.get('components', {}).get('$type', {}).get('$name', ''))
" 2>/dev/null || echo ""
}

sn_set_component_guid() {
  local type="$1"
  local name="$2"
  local guid="$3"
  python3 - <<EOF
import json
with open('$SN_STATE_FILE', 'r') as f:
    d = json.load(f)
if 'components' not in d:
    d['components'] = {}
if '$type' not in d['components']:
    d['components']['$type'] = {}
d['components']['$type']['$name'] = '$guid'
with open('$SN_STATE_FILE', 'w') as f:
    json.dump(d, f, indent=2)
EOF
  sn_log "conductor" "component_guid_stored" "" "\"type\": \"$type\", \"name\": \"$name\", \"guid\": \"$guid\""
}

# ─────────────────────────────────────────────
# Directory setup
# ─────────────────────────────────────────────

sn_ensure_dirs() {
  local dirs=("docs" "scripts" "src/flows" "src/canvas-apps" "src/mda" "src/webresources" "src/plugins" "dist" ".sn")
  for d in "${dirs[@]}"; do
    mkdir -p "$d"
  done
}

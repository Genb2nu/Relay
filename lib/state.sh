#!/bin/bash
# Relay — State management utilities
# Source this file from other scripts: source "$(dirname "$0")/../lib/state.sh"

RELAY_STATE_FILE=".relay/state.json"

# Initialise a new project state
relay_init_state() {
  local project_name="$1"
  local timestamp
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

  mkdir -p .relay docs src

  cat > "$RELAY_STATE_FILE" << EOF
{
  "project_name": "$project_name",
  "phase": "discovery",
  "last_updated": "$timestamp",
  "artifacts": {
    "requirements": null,
    "plan": null,
    "security_design": null,
    "critic_report": null,
    "test_report": null,
    "security_test_report": null
  },
  "approvals": {
    "requirements": null,
    "auditor": null,
    "warden": null,
    "critic": null,
    "sentinel": null,
    "warden_verification": null
  },
  "plan_checksum": null,
  "security_design_checksum": null,
  "config": {
    "enforcement_mode": "advisory"
  }
}
EOF
}

# Update the current phase
relay_set_phase() {
  local phase="$1"
  local timestamp
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

  if [ ! -f "$RELAY_STATE_FILE" ]; then
    echo "Error: No state file found. Run relay_init_state first." >&2
    return 1
  fi

  local tmp
  tmp=$(mktemp)
  jq --arg phase "$phase" --arg ts "$timestamp" \
    '.phase = $phase | .last_updated = $ts' \
    "$RELAY_STATE_FILE" > "$tmp" && mv "$tmp" "$RELAY_STATE_FILE"
}

# Record an artifact path
relay_set_artifact() {
  local key="$1"
  local path="$2"

  local tmp
  tmp=$(mktemp)
  jq --arg key "$key" --arg path "$path" \
    '.artifacts[$key] = $path' \
    "$RELAY_STATE_FILE" > "$tmp" && mv "$tmp" "$RELAY_STATE_FILE"
}

# Record an approval
relay_set_approval() {
  local key="$1"
  local value="$2"
  local timestamp
  timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

  local tmp
  tmp=$(mktemp)
  jq --arg key "$key" --arg val "$value" --arg ts "$timestamp" \
    '.approvals[$key] = {"status": $val, "timestamp": $ts}' \
    "$RELAY_STATE_FILE" > "$tmp" && mv "$tmp" "$RELAY_STATE_FILE"
}

# Lock the plan (write checksums)
relay_lock_plan() {
  if [ ! -f "docs/plan.md" ] || [ ! -f "docs/security-design.md" ]; then
    echo "Error: plan.md or security-design.md not found." >&2
    return 1
  fi

  local plan_hash
  local sec_hash
  plan_hash=$(sha256sum docs/plan.md | cut -d' ' -f1)
  sec_hash=$(sha256sum docs/security-design.md | cut -d' ' -f1)

  local tmp
  tmp=$(mktemp)
  jq --arg ph "$plan_hash" --arg sh "$sec_hash" \
    '.plan_checksum = $ph | .security_design_checksum = $sh' \
    "$RELAY_STATE_FILE" > "$tmp" && mv "$tmp" "$RELAY_STATE_FILE"

  echo "Plan locked. Checksums written to state." >&2
}

# Unlock the plan (clear checksums and approvals)
relay_unlock_plan() {
  local tmp
  tmp=$(mktemp)
  jq '.plan_checksum = null | .security_design_checksum = null |
      .approvals.auditor = null | .approvals.warden = null | .approvals.critic = null |
      .phase = "plan_review"' \
    "$RELAY_STATE_FILE" > "$tmp" && mv "$tmp" "$RELAY_STATE_FILE"

  echo "Plan unlocked. Approvals cleared. Phase set to plan_review." >&2
}

# Read current phase
relay_get_phase() {
  jq -r '.phase // "unknown"' "$RELAY_STATE_FILE" 2>/dev/null
}

# Read project name
relay_get_project() {
  jq -r '.project_name // "unnamed"' "$RELAY_STATE_FILE" 2>/dev/null
}

# Check if plan is locked
relay_is_locked() {
  local checksum
  checksum=$(jq -r '.plan_checksum // empty' "$RELAY_STATE_FILE" 2>/dev/null)
  [ -n "$checksum" ]
}

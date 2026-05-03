#!/bin/bash
# Relay — Routing utilities
# Maps workflow phases to the correct agent invocations.
# Source this file: source "$(dirname "$0")/../lib/routing.sh"

# Determine which agent(s) should run next based on current phase
relay_next_agents() {
  local phase="$1"

  case "$phase" in
    init|discovery)
      echo "scout"
      ;;
    planning)
      echo "drafter"
      ;;
    plan_review)
      echo "auditor warden"
      ;;
    adversarial_pass)
      echo "critic"
      ;;
    building)
      echo "vault forge"
      ;;
    verification)
      echo "sentinel warden"
      ;;
    complete)
      echo "none"
      ;;
    *)
      echo "unknown"
      ;;
  esac
}

# Determine the next phase after current phase completes
relay_next_phase() {
  local current="$1"

  case "$current" in
    init)          echo "discovery" ;;
    discovery)     echo "planning" ;;
    planning)      echo "plan_review" ;;
    plan_review)   echo "adversarial_pass" ;;
    adversarial_pass) echo "building" ;;
    building)      echo "verification" ;;
    verification)  echo "complete" ;;
    complete)      echo "complete" ;;
    *)             echo "unknown" ;;
  esac
}

# Get human-readable phase description
relay_phase_description() {
  local phase="$1"

  case "$phase" in
    init)              echo "Project initialised, waiting for brief" ;;
    discovery)         echo "Scout is gathering requirements" ;;
    planning)          echo "Drafter is writing the technical plan" ;;
    plan_review)       echo "Auditor + Warden are reviewing the plan" ;;
    adversarial_pass)  echo "Critic is red-teaming the approved plan" ;;
    building)          echo "Vault + Forge are building the solution" ;;
    verification)      echo "Sentinel + Warden are verifying the build" ;;
    complete)          echo "Project complete" ;;
    *)                 echo "Unknown phase: $phase" ;;
  esac
}

# Get the model for a given agent
relay_agent_model() {
  local agent="$1"
  local state_file=".relay/state.json"

  # Check for model override in config
  if [ -f "$state_file" ]; then
    local override
    override=$(jq -r ".config.${agent}_model // empty" "$state_file" 2>/dev/null)
    if [ -n "$override" ]; then
      echo "$override"
      return
    fi
  fi

  # Default model assignments
  case "$agent" in
    conductor|drafter|auditor|warden|critic)
      echo "opus"
      ;;
    scout|vault|forge|sentinel)
      echo "sonnet"
      ;;
    *)
      echo "sonnet"
      ;;
  esac
}

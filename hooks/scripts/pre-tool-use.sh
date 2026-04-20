#!/bin/bash
# Relay — PreToolUse hook
# Enforces:
#   1. Plan lock: blocks writes to plan.md and security-design.md after approval
#   2. Critic read-only: blocks Critic from writing anywhere except critic-report.md
#   3. Auditor read-only: blocks Auditor from writing to any file
#   4. Sentinel write restriction: only test-report.md
#   5. Warden write restriction: only security-design.md and security-test-report.md
#
# Exit codes:
#   0 = allow
#   2 = block (Claude Code treats exit 2 as a rejection)

set -e

# Read tool input from stdin
TOOL_INPUT=$(cat)

# Extract the file path being written to
FILE_PATH=$(echo "$TOOL_INPUT" | jq -r '.params.file_path // .params.path // empty' 2>/dev/null)

# If no file path, this isn't a write operation we care about — allow
if [ -z "$FILE_PATH" ]; then
  exit 0
fi

# Normalise to basename for matching
BASENAME=$(basename "$FILE_PATH")

# --- Check 1: Plan Lock ---
STATE_FILE=".relay/state.json"

if [ -f "$STATE_FILE" ]; then
  case "$BASENAME" in
    plan.md)
      CHECKSUM=$(jq -r '.plan_checksum // empty' "$STATE_FILE" 2>/dev/null)
      if [ -n "$CHECKSUM" ]; then
        echo "BLOCKED: plan.md is locked (checksum: $CHECKSUM). Use /relay:plan-review to unlock and re-review." >&2
        exit 2
      fi
      ;;
    security-design.md)
      CHECKSUM=$(jq -r '.security_design_checksum // empty' "$STATE_FILE" 2>/dev/null)
      if [ -n "$CHECKSUM" ]; then
        echo "BLOCKED: security-design.md is locked (checksum: $CHECKSUM). Use /relay:plan-review to unlock and re-review." >&2
        exit 2
      fi
      ;;
  esac
fi

# --- Check 2: Agent-specific write restrictions ---
# The CLAUDE_AGENT variable is set by Claude Code when a subagent is active.
# If it's not set, we're in Conductor context — allow everything.
AGENT="${CLAUDE_AGENT:-conductor}"

case "$AGENT" in
  auditor)
    # Auditor cannot write to ANY file
    echo "BLOCKED: Auditor is read-only. Return review feedback to Conductor as text." >&2
    exit 2
    ;;

  critic)
    # Critic can only write to critic-report.md
    if [ "$BASENAME" != "critic-report.md" ]; then
      echo "BLOCKED: Critic can only write to docs/critic-report.md. Found: $FILE_PATH" >&2
      exit 2
    fi
    ;;

  sentinel)
    # Sentinel can only write to test-report.md
    if [ "$BASENAME" != "test-report.md" ]; then
      echo "BLOCKED: Sentinel can only write to docs/test-report.md. Found: $FILE_PATH" >&2
      exit 2
    fi
    ;;

  warden)
    # Warden can only write to security-design.md and security-test-report.md
    case "$BASENAME" in
      security-design.md|security-test-report.md) ;;
      *)
        echo "BLOCKED: Warden can only write to security-design.md or security-test-report.md. Found: $FILE_PATH" >&2
        exit 2
        ;;
    esac
    ;;

  scout)
    # Scout can only write to requirements.md
    if [ "$BASENAME" != "requirements.md" ]; then
      echo "BLOCKED: Scout can only write to docs/requirements.md. Found: $FILE_PATH" >&2
      exit 2
    fi
    ;;

  drafter)
    # Drafter can only write to plan.md and security-design.md (initial draft)
    case "$BASENAME" in
      plan.md|security-design.md) ;;
      *)
        echo "BLOCKED: Drafter can only write to plan.md or security-design.md. Found: $FILE_PATH" >&2
        exit 2
        ;;
    esac
    ;;

  forge)
    # Forge cannot write to plan.md or security-design.md
    case "$BASENAME" in
      plan.md|security-design.md)
        echo "BLOCKED: Forge cannot edit locked plan or security design. Report concerns to Conductor." >&2
        exit 2
        ;;
    esac
    ;;

  vault)
    # Vault cannot write to plan.md or security-design.md
    case "$BASENAME" in
      plan.md|security-design.md)
        echo "BLOCKED: Vault cannot edit locked plan or security design. Report concerns to Conductor." >&2
        exit 2
        ;;
    esac
    ;;

  conductor|*)
    # Conductor has full access — allow
    ;;
esac

# All checks passed — allow
exit 0

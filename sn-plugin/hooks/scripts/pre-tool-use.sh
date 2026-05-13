#!/usr/bin/env bash
# Pre-tool-use hook for sn-plugin
# Validates state before any tool execution in a SimplifyNext project.

set -euo pipefail

STATE_FILE=".sn/state.json"
LOG_FILE=".sn/execution-log.jsonl"

# Only run checks if this is a SimplifyNext project
if [[ ! -f "$STATE_FILE" ]]; then
  exit 0
fi

# Read current phase
PHASE=$(python3 -c "import json,sys; d=json.load(open('$STATE_FILE')); print(d.get('phase','unknown'))" 2>/dev/null || echo "unknown")
TOOL_NAME="${CLAUDE_TOOL_NAME:-unknown}"
TOOL_INPUT="${CLAUDE_TOOL_INPUT:-{}}"

# Block plan.md edits if plan is locked
if [[ "$TOOL_NAME" == "Write" || "$TOOL_NAME" == "Edit" ]]; then
  FILE_PATH=$(python3 -c "import json,sys; d=json.loads('$TOOL_INPUT'); print(d.get('file_path',''))" 2>/dev/null || echo "")

  if [[ "$FILE_PATH" == *"docs/plan.md"* || "$FILE_PATH" == *"docs/security-design.md"* ]]; then
    LOCKED=$(python3 -c "import json,sys; d=json.load(open('$STATE_FILE')); print(str(d.get('plan_locked', False)).lower())" 2>/dev/null || echo "false")

    if [[ "$LOCKED" == "true" ]]; then
      echo "ERROR: docs/plan.md and docs/security-design.md are locked."
      echo "The plan is locked (plan_locked=true in .sn/state.json)."
      echo "To unlock: run /sn-plan-review --unlock"
      exit 1
    fi
  fi
fi

# Warn if phase is advanced but auth hasn't been checked recently
if [[ "$PHASE" == "build" || "$PHASE" == "review" ]]; then
  if [[ "$TOOL_NAME" == "Bash" ]]; then
    COMMAND=$(python3 -c "import json,sys; d=json.loads('$TOOL_INPUT'); print(d.get('command',''))" 2>/dev/null || echo "")

    # Check for pac commands without auth
    if echo "$COMMAND" | grep -q "pac solution\|pac admin\|pac canvas"; then
      if ! pac auth who &>/dev/null 2>&1; then
        echo "WARNING: PAC CLI auth may not be configured."
        echo "If commands fail, run: pac auth select"
      fi
    fi
  fi
fi

# Log tool use for audit trail (non-blocking)
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
ENTRY="{\"timestamp\": \"$TIMESTAMP\", \"agent\": \"conductor\", \"event\": \"tool_use\", \"tool\": \"$TOOL_NAME\", \"phase\": \"$PHASE\"}"
echo "$ENTRY" >> "$LOG_FILE" 2>/dev/null || true

exit 0

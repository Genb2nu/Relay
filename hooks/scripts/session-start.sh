#!/bin/bash
# Relay — SessionStart hook
# Runs at the beginning of each Claude Code session.
# Checks for required tools and rehydrates project state.

set -e

# --- Run prerequisite check (lightweight) ---
# Find the relay-prerequisite-check.py script
PREREQ_SCRIPT=""
if [ -f "scripts/relay-prerequisite-check.py" ]; then
  PREREQ_SCRIPT="scripts/relay-prerequisite-check.py"
elif [ -f "../scripts/relay-prerequisite-check.py" ]; then
  PREREQ_SCRIPT="../scripts/relay-prerequisite-check.py"
elif [ -f "../../scripts/relay-prerequisite-check.py" ]; then
  PREREQ_SCRIPT="../../scripts/relay-prerequisite-check.py"
fi

if [ -n "$PREREQ_SCRIPT" ] && command -v python3 >/dev/null 2>&1; then
  PYTHONUTF8=1 python3 "$PREREQ_SCRIPT" --skip-plugins --skip-mcp 2>&1 || true
elif [ -n "$PREREQ_SCRIPT" ] && command -v python >/dev/null 2>&1; then
  PYTHONUTF8=1 python "$PREREQ_SCRIPT" --skip-plugins --skip-mcp 2>&1 || true
else
  # Fall back to legacy checks
  MISSING=""

  command -v pac >/dev/null 2>&1 || MISSING="$MISSING pac"
  command -v az >/dev/null 2>&1 || MISSING="$MISSING az"
  command -v jq >/dev/null 2>&1 || MISSING="$MISSING jq"
  command -v node >/dev/null 2>&1 || MISSING="$MISSING node"
  command -v git >/dev/null 2>&1 || MISSING="$MISSING git"

  if [ -n "$MISSING" ]; then
    echo "[Relay] Warning: Missing tools:$MISSING" >&2
    echo "[Relay] Some agents may not work correctly without these tools." >&2
  fi
fi

# --- Check PAC auth ---
if command -v pac >/dev/null 2>&1; then
  AUTH_COUNT=$(pac auth list 2>/dev/null | grep -c "Active" || echo "0")
  if [ "$AUTH_COUNT" = "0" ]; then
    echo "[Relay] Warning: No active PAC auth profile. Run 'pac auth create' to connect to a Dataverse environment." >&2
  fi
fi

# --- Rehydrate state ---
if [ -f ".relay/state.json" ]; then
  PROJECT=$(jq -r '.project_name // .project // "unnamed"' .relay/state.json 2>/dev/null)
  PHASE=$(jq -r '.phase // "unknown"' .relay/state.json 2>/dev/null)
  echo "[Relay] Project: $PROJECT | Phase: $PHASE" >&2
else
  echo "[Relay] No project found in this folder. Use /relay:start to begin." >&2
fi

exit 0

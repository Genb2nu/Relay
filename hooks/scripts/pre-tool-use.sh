#!/bin/bash
# Relay — PreToolUse hook
# Enforces:
#   1. Plan lock: blocks writes to plan.md and security-design.md after approval
#   2. Critic read-only: blocks Critic from writing anywhere except critic-report.md
#   3. Auditor read-only: blocks Auditor from writing to any file
#   4. Sentinel write restriction: only test-report.md
#   5. Warden write restriction: only security-design.md and security-test-report.md
#   6. Forge specialists restricted to their artifact paths plus Relay state files
#
# Exit codes:
#   0 = allow
#   2 = block (Claude Code treats exit 2 as a rejection)

set -e

WORKSPACE_ROOT=$(pwd -P)

canonicalize_path() {
  local raw_path="$1"
  local base_dir="$2"

  if command -v python3 >/dev/null 2>&1; then
    python3 - "$base_dir" "$raw_path" <<'PY'
import os
import sys

base_dir = os.path.realpath(sys.argv[1])
raw_path = sys.argv[2]
candidate = raw_path if os.path.isabs(raw_path) else os.path.join(base_dir, raw_path)
print(os.path.realpath(os.path.normpath(candidate)).replace("\\", "/"))
PY
    return
  fi

  if command -v python >/dev/null 2>&1; then
    python - "$base_dir" "$raw_path" <<'PY'
import os
import sys

base_dir = os.path.realpath(sys.argv[1])
raw_path = sys.argv[2]
candidate = raw_path if os.path.isabs(raw_path) else os.path.join(base_dir, raw_path)
print(os.path.realpath(os.path.normpath(candidate)).replace("\\", "/"))
PY
    return
  fi

  if command -v realpath >/dev/null 2>&1; then
    case "$raw_path" in
      /*) realpath -m "$raw_path" ;;
      *) realpath -m "$base_dir/$raw_path" ;;
    esac
    return
  fi

  echo "BLOCKED: Unable to canonicalize write path. Install python or realpath support for hooks." >&2
  exit 2
}

path_is() {
  [ "$1" = "$2" ]
}

path_under() {
  case "$1" in
    "$2"|"$2"/*) return 0 ;;
    *) return 1 ;;
  esac
}

path_is_ps1_in_dir() {
  case "$1" in
    "$2"/*.ps1) return 0 ;;
    *) return 1 ;;
  esac
}

# Read tool input from stdin
TOOL_INPUT=$(cat)

# Extract the file path being written to
FILE_PATH=$(echo "$TOOL_INPUT" | jq -r '.params.file_path // .params.path // empty' 2>/dev/null)

# If no file path, this isn't a write operation we care about — allow
if [ -z "$FILE_PATH" ]; then
  exit 0
fi

CANONICAL_PATH=$(canonicalize_path "$FILE_PATH" "$WORKSPACE_ROOT")
STATE_FILE=$(canonicalize_path ".relay/state.json" "$WORKSPACE_ROOT")
DOCS_DIR=$(canonicalize_path "docs" "$WORKSPACE_ROOT")
SCRIPTS_DIR=$(canonicalize_path "scripts" "$WORKSPACE_ROOT")
SRC_DIR=$(canonicalize_path "src" "$WORKSPACE_ROOT")
SRC_SOLUTION_DIR=$(canonicalize_path "src/solution" "$WORKSPACE_ROOT")
PLAN_PATH=$(canonicalize_path "docs/plan.md" "$WORKSPACE_ROOT")
SECURITY_DESIGN_PATH=$(canonicalize_path "docs/security-design.md" "$WORKSPACE_ROOT")
SECURITY_TEST_REPORT_PATH=$(canonicalize_path "docs/security-test-report.md" "$WORKSPACE_ROOT")
CRITIC_REPORT_PATH=$(canonicalize_path "docs/critic-report.md" "$WORKSPACE_ROOT")
TEST_REPORT_PATH=$(canonicalize_path "docs/test-report.md" "$WORKSPACE_ROOT")
DRIFT_REPORT_PATH=$(canonicalize_path "docs/drift-report.md" "$WORKSPACE_ROOT")
REQUIREMENTS_PATH=$(canonicalize_path "docs/requirements.md" "$WORKSPACE_ROOT")
DESIGN_SYSTEM_PATH=$(canonicalize_path "docs/design-system.md" "$WORKSPACE_ROOT")
DESIGN_REVIEW_PATH=$(canonicalize_path "docs/design-review.md" "$WORKSPACE_ROOT")
WIREFRAMES_PATH=$(canonicalize_path "docs/wireframes.html" "$WORKSPACE_ROOT")
EXISTING_SOLUTION_PATH=$(canonicalize_path "docs/existing-solution.md" "$WORKSPACE_ROOT")
CANVAS_APP_INSTRUCTIONS_PATH=$(canonicalize_path "docs/canvas-app-instructions.md" "$WORKSPACE_ROOT")
FLOW_BUILD_GUIDE_PATH=$(canonicalize_path "docs/flow-build-guide.md" "$WORKSPACE_ROOT")
PLAN_INDEX_PATH=$(canonicalize_path ".relay/plan-index.json" "$WORKSPACE_ROOT")
EXECUTION_LOG_PATH=$(canonicalize_path ".relay/execution-log.jsonl" "$WORKSPACE_ROOT")
CANVAS_APP_DIR=$(canonicalize_path "src/canvas-apps" "$WORKSPACE_ROOT")
MDA_DIR=$(canonicalize_path "src/mda" "$WORKSPACE_ROOT")
PAGES_DIR=$(canonicalize_path "src/pages" "$WORKSPACE_ROOT")
APPLY_MDA_SITEMAP_PATH=$(canonicalize_path "scripts/apply-mda-sitemap.ps1" "$WORKSPACE_ROOT")

# --- Check 1: Plan Lock ---
if [ -f "$STATE_FILE" ]; then
  if path_is "$CANONICAL_PATH" "$PLAN_PATH"; then
    CHECKSUM=$(jq -r '.plan_checksum // empty' "$STATE_FILE" 2>/dev/null)
    if [ -n "$CHECKSUM" ]; then
      echo "BLOCKED: docs/plan.md is locked (checksum: $CHECKSUM). Use /relay:plan-review to unlock and re-review." >&2
      exit 2
    fi
  fi

  if path_is "$CANONICAL_PATH" "$SECURITY_DESIGN_PATH"; then
    CHECKSUM=$(jq -r '.security_design_checksum // empty' "$STATE_FILE" 2>/dev/null)
    if [ -n "$CHECKSUM" ]; then
      echo "BLOCKED: docs/security-design.md is locked (checksum: $CHECKSUM). Use /relay:plan-review to unlock and re-review." >&2
      exit 2
    fi
  fi
fi

# --- Check 2: Agent-specific write restrictions ---
# The CLAUDE_AGENT variable must be present and known for any write.
AGENT="${CLAUDE_AGENT:-}"

if [ -z "$AGENT" ]; then
  echo "BLOCKED: CLAUDE_AGENT is unset. Writes are denied by default until an explicit agent identity is provided." >&2
  exit 2
fi

case "$AGENT" in
  conductor|auditor|critic|sentinel|warden|scout|drafter|stylist|analyst|forge|vault|forge-canvas|forge-mda|forge-flow|forge-pages) ;;
  *)
    echo "BLOCKED: Unknown agent '$AGENT'. Writes are denied by default." >&2
    exit 2
    ;;
esac

case "$AGENT" in
  auditor)
    # Auditor cannot write to ANY file
    echo "BLOCKED: Auditor is read-only. Return review feedback to Conductor as text." >&2
    exit 2
    ;;

  critic)
    # Critic can only write to critic-report.md
    if ! path_is "$CANONICAL_PATH" "$CRITIC_REPORT_PATH"; then
      echo "BLOCKED: Critic can only write to docs/critic-report.md. Found: $CANONICAL_PATH" >&2
      exit 2
    fi
    ;;

  sentinel)
    # Sentinel can only write to test-report.md and drift-report.md
    if ! path_is "$CANONICAL_PATH" "$TEST_REPORT_PATH" && ! path_is "$CANONICAL_PATH" "$DRIFT_REPORT_PATH"; then
      echo "BLOCKED: Sentinel can only write to docs/test-report.md or docs/drift-report.md. Found: $CANONICAL_PATH" >&2
      exit 2
    fi
    ;;

  warden)
    # Warden can only write to security-design.md and security-test-report.md
    if ! path_is "$CANONICAL_PATH" "$SECURITY_DESIGN_PATH" && ! path_is "$CANONICAL_PATH" "$SECURITY_TEST_REPORT_PATH"; then
      echo "BLOCKED: Warden can only write to docs/security-design.md or docs/security-test-report.md. Found: $CANONICAL_PATH" >&2
      exit 2
    fi
    ;;

  scout)
    # Scout can only write to requirements.md
    if ! path_is "$CANONICAL_PATH" "$REQUIREMENTS_PATH"; then
      echo "BLOCKED: Scout can only write to docs/requirements.md. Found: $CANONICAL_PATH" >&2
      exit 2
    fi
    ;;

  drafter)
    # Drafter can only write to plan.md and security-design.md (initial draft)
    if ! path_is "$CANONICAL_PATH" "$PLAN_PATH" && ! path_is "$CANONICAL_PATH" "$SECURITY_DESIGN_PATH"; then
      echo "BLOCKED: Drafter can only write to docs/plan.md or docs/security-design.md. Found: $CANONICAL_PATH" >&2
      exit 2
    fi
    ;;

  stylist)
    # Stylist can only write to approved design artifacts plus plan-index coordination state
    ALLOWED_FILES=("$DESIGN_SYSTEM_PATH" "$DESIGN_REVIEW_PATH" "$WIREFRAMES_PATH" "$PLAN_INDEX_PATH")
    allowed=false
    for allowed_file in "${ALLOWED_FILES[@]}"; do
      if path_is "$CANONICAL_PATH" "$allowed_file"; then
        allowed=true
        break
      fi
    done
    if [ "$allowed" != true ]; then
      echo "BLOCKED: Stylist can only write to docs/design-system.md, docs/design-review.md, docs/wireframes.html, or .relay/plan-index.json. Found: $CANONICAL_PATH" >&2
      exit 2
    fi
    ;;

  analyst)
    # Analyst can only write to existing-solution.md
    if ! path_is "$CANONICAL_PATH" "$EXISTING_SOLUTION_PATH"; then
      echo "BLOCKED: Analyst can only write to docs/existing-solution.md. Found: $CANONICAL_PATH" >&2
      exit 2
    fi
    ;;

  forge)
    # Forge can only write under src/ or scripts/
    if ! path_under "$CANONICAL_PATH" "$SRC_DIR" && ! path_under "$CANONICAL_PATH" "$SCRIPTS_DIR"; then
      echo "BLOCKED: Forge can only write under src/ or scripts/. Found: $CANONICAL_PATH" >&2
      exit 2
    fi
    ;;

  forge-canvas)
    # Forge-Canvas can only write Canvas App artifacts, fallback instructions, and Relay state files
    if ! path_under "$CANONICAL_PATH" "$CANVAS_APP_DIR" \
      && ! path_is "$CANONICAL_PATH" "$CANVAS_APP_INSTRUCTIONS_PATH" \
      && ! path_is "$CANONICAL_PATH" "$PLAN_INDEX_PATH" \
      && ! path_is "$CANONICAL_PATH" "$EXECUTION_LOG_PATH"; then
      echo "BLOCKED: Forge-Canvas can only write under src/canvas-apps/, docs/canvas-app-instructions.md, or Relay state files. Found: $CANONICAL_PATH" >&2
      exit 2
    fi
    ;;

  forge-mda)
    # Forge-MDA can only write MDA artifacts, the MDA deploy script, and Relay state files
    if ! path_under "$CANONICAL_PATH" "$MDA_DIR" \
      && ! path_is "$CANONICAL_PATH" "$APPLY_MDA_SITEMAP_PATH" \
      && ! path_is "$CANONICAL_PATH" "$PLAN_INDEX_PATH" \
      && ! path_is "$CANONICAL_PATH" "$EXECUTION_LOG_PATH"; then
      echo "BLOCKED: Forge-MDA can only write under src/mda/, scripts/apply-mda-sitemap.ps1, or Relay state files. Found: $CANONICAL_PATH" >&2
      exit 2
    fi
    ;;

  forge-flow)
    # Forge-Flow can only write the flow build guide and Relay state files
    if ! path_is "$CANONICAL_PATH" "$FLOW_BUILD_GUIDE_PATH" \
      && ! path_is "$CANONICAL_PATH" "$PLAN_INDEX_PATH" \
      && ! path_is "$CANONICAL_PATH" "$EXECUTION_LOG_PATH"; then
      echo "BLOCKED: Forge-Flow can only write docs/flow-build-guide.md or Relay state files. Found: $CANONICAL_PATH" >&2
      exit 2
    fi
    ;;

  forge-pages)
    # Forge-Pages can only write portal artifacts and Relay state files
    if ! path_under "$CANONICAL_PATH" "$PAGES_DIR" \
      && ! path_is "$CANONICAL_PATH" "$PLAN_INDEX_PATH" \
      && ! path_is "$CANONICAL_PATH" "$EXECUTION_LOG_PATH"; then
      echo "BLOCKED: Forge-Pages can only write under src/pages/ or Relay state files. Found: $CANONICAL_PATH" >&2
      exit 2
    fi
    ;;

  vault)
    # Vault can only write PowerShell scripts and src/solution/
    if ! path_under "$CANONICAL_PATH" "$SRC_SOLUTION_DIR" && ! path_is_ps1_in_dir "$CANONICAL_PATH" "$SCRIPTS_DIR"; then
      echo "BLOCKED: Vault can only write scripts/*.ps1 or files under src/solution/. Found: $CANONICAL_PATH" >&2
      exit 2
    fi
    ;;

  conductor)
    # Conductor has full access — allow
    ;;
esac

# All checks passed — allow
exit 0

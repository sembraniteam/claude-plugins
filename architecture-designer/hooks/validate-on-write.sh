#!/bin/bash
# PostToolUse hook: run the plugin's own validators immediately after
# diagrams.json or session.json is written or edited, instead of waiting for
# the skill to remember to run them before the next gate. The design/review
# skills already document these validators as run "automatically before
# preview" — this makes that automatic, not just instructed. A failure's
# stderr is fed straight back into the model's context via PostToolUse exit 2,
# so a Mermaid syntax error or a broken session.json structure is caught the
# moment it's written, not several steps later.
set -uo pipefail

command -v jq >/dev/null 2>&1 || exit 0

input=$(cat)
file_path=$(printf '%s' "$input" | jq -r '.tool_input.file_path // empty')
[ -z "$file_path" ] && exit 0

cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0

case "$file_path" in
  *docs/architecture-designer/diagrams.json)
    command -v node >/dev/null 2>&1 || exit 0
    output=$(node "${CLAUDE_PLUGIN_ROOT}/scripts/validate-diagrams.mjs" 2>&1)
    status=$?
    ;;
  *docs/architecture-designer/session.json)
    command -v python3 >/dev/null 2>&1 || exit 0
    output=$(python3 "${CLAUDE_PLUGIN_ROOT}/scripts/validate-session.py" 2>&1)
    status=$?
    ;;
  *)
    exit 0
    ;;
esac

if [ "$status" -ne 0 ]; then
  printf '%s\n' "$output" >&2
  exit 2
fi

exit 0

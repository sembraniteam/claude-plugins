#!/bin/bash
# PreToolUse gate for the Task tool spawning architecture-implementer.
#
# The agent's own frontmatter says it "refuses to run without a confirmed
# plan," but that's a promise in prompt text, not enforcement — a model that
# skips or misreads its own instructions can still spawn it. This hook makes
# the same rule mechanical: it blocks the Task call outright (exit 2) unless
# a plan file with `Status: In progress` actually exists on disk under
# docs/architecture-designer/plan/.
#
# If the spawning prompt names a specific plan file, that exact file's
# Status row is checked. Otherwise it falls back to checking whether ANY
# plan file in the directory is still `In progress`.
set -uo pipefail

command -v jq >/dev/null 2>&1 || exit 0

input=$(cat)
subagent_type=$(printf '%s' "$input" | jq -r '.tool_input.subagent_type // empty')

# Only gate calls that target architecture-implementer (with or without the
# "architecture-designer:" plugin-scope prefix). Everything else passes through.
case "$subagent_type" in
  *architecture-implementer) ;;
  *) exit 0 ;;
esac

cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0

plan_dir="docs/architecture-designer/plan"

is_in_progress() {
  grep -qE '^\|[[:space:]]*Status[[:space:]]*\|[[:space:]]*In progress' "$1" 2>/dev/null
}

prompt_text=$(printf '%s' "$input" | jq -r '.tool_input.prompt // empty')
referenced_plan=$(printf '%s' "$prompt_text" | grep -oE "${plan_dir}/[A-Za-z0-9._-]+\.md" | head -1 || true)

if [ -n "$referenced_plan" ]; then
  if [ -f "$referenced_plan" ] && is_in_progress "$referenced_plan"; then
    exit 0
  fi
  echo "BLOCKED: architecture-implementer is being spawned with plan '$referenced_plan', but that file is missing or its Status row is not 'In progress'. Run implementation-planner first and wait for it to report the plan was saved and confirmed before spawning architecture-implementer." >&2
  exit 2
fi

if [ -d "$plan_dir" ]; then
  for f in "$plan_dir"/*.md; do
    [ -e "$f" ] || continue
    if is_in_progress "$f"; then
      exit 0
    fi
  done
fi

echo "BLOCKED: no plan file under $plan_dir has 'Status: In progress'. architecture-implementer must not be spawned until implementation-planner has proposed a folder structure, gotten user confirmation, and saved the plan — run implementation-planner first." >&2
exit 2

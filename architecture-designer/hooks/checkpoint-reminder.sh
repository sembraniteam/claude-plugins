#!/bin/bash
# UserPromptSubmit hook — a more reliable backstop than the PreCompact prompt
# hook for reminding Claude to persist architecture-designer's mid-workflow
# checkpoint state (session.json's progress/lld/pending keys,
# docs/architecture-designer/last-review.md). UserPromptSubmit fires
# deterministically on every turn; prompt-based hooks are not confirmed
# fully reliable specifically on the PreCompact event (see README's
# "Mid-workflow persistence" section). This hook is a command hook, not a
# prompt hook, so the gating below is a real disk check, not an LLM guess —
# it only emits a reminder while session.json's own state shows a pipeline
# genuinely mid Stage 6a-Step 13, so it stays silent on every unrelated
# prompt and every project that isn't using this plugin's workflow at all.
set -uo pipefail

cat >/dev/null   # drain stdin; only session.json on disk is consulted below

command -v jq >/dev/null 2>&1 || exit 0

cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0

session_file="docs/architecture-designer/session.json"
[ -f "$session_file" ] || exit 0

last_step=$(jq -r '.progress.lastCompletedStep // empty' "$session_file" 2>/dev/null)
owner=$(jq -r '.progress.owner // empty' "$session_file" 2>/dev/null)

[ -z "$last_step" ] && exit 0
# step13 is the pipeline's natural end for design/review — stop reminding.
[ "$last_step" = "step13" ] && exit 0

owner_skill="${owner:-design}"

context="Active architecture-designer checkpoint: the '${owner_skill}' skill's pipeline last recorded progress at ${last_step} (mid Stage 6a-Step 13, per docs/architecture-designer/session.json). If this turn advances that pipeline — a reviewer/fixer cycle, an LLD group, a diagram edit — checkpoint session.json's progress/lld/pending keys and docs/architecture-designer/last-review.md incrementally as the work happens, per skills/design/references/session-schema.md. Do not defer persistence to the end of the workflow or to a PreCompact hook that may not fire."

jq -n --arg ctx "$context" '{hookSpecificOutput: {hookEventName: "UserPromptSubmit", additionalContext: $ctx}}'
exit 0


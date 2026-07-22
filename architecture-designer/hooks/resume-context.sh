#!/bin/bash
# SessionStart hook (matcher: resume) — surfaces an unfinished
# architecture-designer pipeline even when the resumed conversation never
# explicitly re-invokes /architecture-designer:design|review|implement.
# Without this, a session that died mid Stage 6a-Step 13 is only noticed if
# the user happens to call the skill again; casual follow-up chat after
# resume would otherwise skip right past it. Gated to the `resume` source so
# it never fires on a fresh `startup` or a `clear`.
set -uo pipefail

cat >/dev/null   # drain stdin; only session.json on disk is consulted below

command -v jq >/dev/null 2>&1 || exit 0

cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0

session_file="docs/architecture-designer/session.json"
[ -f "$session_file" ] || exit 0

last_step=$(jq -r '.progress.lastCompletedStep // empty' "$session_file" 2>/dev/null)
owner=$(jq -r '.progress.owner // empty' "$session_file" 2>/dev/null)
project=$(jq -r '.project // empty' "$session_file" 2>/dev/null)

[ -z "$last_step" ] && exit 0
# step13 ("implementation offered") is the pipeline's natural end from
# design/review's own perspective — nothing further for either skill to
# checkpoint, so stop reminding once it's reached.
[ "$last_step" = "step13" ] && exit 0

describe_step() {
  case "$1" in
    step6a) echo "Stage 6a — database design reviewed/passed" ;;
    step6d) echo "Stage 6d/6e — diagrams.json fully written" ;;
    step7)  echo "Step 7 — architecture review passed" ;;
    step8)  echo "Step 8 — browser preview opened" ;;
    step9)  echo "Step 9 — user confirmed the design" ;;
    step10) echo "Step 10 — all five LLD groups confirmed" ;;
    step11) echo "Step 11 — document saved" ;;
    step12) echo "Step 12 — document reviewed/approved" ;;
    *)      echo "$1" ;;
  esac
}

step_desc=$(describe_step "$last_step")
owner_skill="${owner:-design}"
project_label="${project:-this project}"

context="There is an unfinished architecture-designer pipeline for '${project_label}': docs/architecture-designer/session.json shows progress last recorded at ${last_step} (${step_desc}), owned by the '${owner_skill}' skill's pass. This was detected on session resume, independent of whether any architecture-designer skill was invoked this turn. If the user's next message doesn't obviously continue this work, mention that an in-progress architecture session exists at this step and ask whether to resume it with /architecture-designer:${owner_skill} before starting something unrelated."

jq -n --arg ctx "$context" '{hookSpecificOutput: {hookEventName: "SessionStart", additionalContext: $ctx}}'
exit 0

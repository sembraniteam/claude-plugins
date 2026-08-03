#!/bin/bash
# SubagentStop hook — re-verifies a self-reported implementation-completion
# claim against disk before letting the subagent stop, instead of trusting
# "Status: Complete" at face value.
#
# There is no confirmed subagent-type field on the SubagentStop event to
# matcher against directly (unlike PreToolUse's Task/tool_input.subagent_type
# combo used by check-implementer-plan.sh), so this script identifies a
# relevant run indirectly and safely: it greps this subagent's own
# transcript for any docs/architecture-designer/plan/*.md path it touched,
# then only acts if that plan's Status is *currently* Complete on disk — a
# state written by exactly two agents: architecture-implementer's own
# verification pass (see that agent's "Verification and output" step), and
# implementation-fixer's final step once its corrections are confirmed (see
# that agent's "Resuming, checkpointing, and the Status re-arm" section) —
# implementation-planner always saves Status: In progress, never Complete.
# Any other subagent stop — implementation-planner, implementation-reviewer
# (read-only), architecture-fixer, database-fixer, or anything that never
# touched a plan file — is a silent no-op.
#
# Known limitation: the stop_hook_active guard below (standard anti-infinite-
# loop idiom) means disk re-verification only runs on this stop attempt's
# *first* pass. If the first pass blocks and the agent tries to stop again
# without actually resolving the mismatch (e.g. it edits the plan text
# cosmetically instead of writing the missing file), stop_hook_active reads
# true on the second attempt and this hook exits 0 immediately — letting a
# still-inaccurate Status: Complete claim through unverified. This is an
# inherent trade-off against blocking forever, not a bug to fix here.
set -uo pipefail

command -v jq >/dev/null 2>&1 || exit 0

input=$(cat)

# stop_hook_active is true when this hook already fired once for this stop
# attempt and the agent is trying to stop again — bail to avoid blocking
# forever in a loop.
stop_hook_active=$(printf '%s' "$input" | jq -r '.stop_hook_active // false' 2>/dev/null)
[ "$stop_hook_active" = "true" ] && exit 0

transcript_path=$(printf '%s' "$input" | jq -r '.transcript_path // empty' 2>/dev/null)
[ -n "$transcript_path" ] && [ -f "$transcript_path" ] || exit 0

cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0

plan_files=$(jq -r '.. | objects | select(has("file_path")) | .file_path' "$transcript_path" 2>/dev/null \
  | grep -oE 'docs/architecture-designer/plan/[A-Za-z0-9._-]+\.md' | sort -u)
[ -z "$plan_files" ] && exit 0

report=$(mktemp)
trap 'rm -f "$report"' EXIT

while IFS= read -r plan; do
  [ -z "$plan" ] && continue
  [ -f "$plan" ] || continue

  status_line=$(grep -E '^\|[[:space:]]*Status[[:space:]]*\|' "$plan" | head -1)
  case "$status_line" in
    *Complete*) ;;
    *) continue ;;   # In progress / Superseded — not claiming completion, nothing to re-verify
  esac

  # Strip the "Setup and run commands" section — its entries are npm script
  # names, not filesystem paths, so `test -f` against them is meaningless
  # (architecture-implementer verifies those against package.json instead).
  body=$(awk '
    /^## / { insetup = ($0 ~ /^## +Setup and run commands/) ? 1 : 0; next }
    !insetup { print }
  ' "$plan")

  while IFS= read -r item_path; do
    [ -z "$item_path" ] && continue
    if [ ! -f "$item_path" ]; then
      echo "  - \`${item_path}\` — checked [x] in ${plan}, but missing on disk" >> "$report"
    fi
  done < <(printf '%s\n' "$body" | sed -n -E 's/^- \[x\] `([^`]+)`.*/\1/p')

  while IFS= read -r leftover; do
    [ -z "$leftover" ] && continue
    echo "  - unresolved checklist item in ${plan}: ${leftover}" >> "$report"
  done < <(printf '%s\n' "$body" | grep -E '^- \[ \] ' | grep -v 'FAIL')

done <<< "$plan_files"

if [ -s "$report" ]; then
  {
    echo "BLOCKED: an implementation plan reports Status: Complete, but re-verification against disk found a mismatch — do not report this run as finished:"
    echo
    cat "$report"
    echo
    echo "Go back: write each missing file, or demote it to \`[ ] FAIL: {reason}\` in the plan; resolve every unaccounted-for checklist item. Only stop once the plan's on-disk state actually matches its Status: Complete claim."
  } >&2
  exit 2
fi

exit 0

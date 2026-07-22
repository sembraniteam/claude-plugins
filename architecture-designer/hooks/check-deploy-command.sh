#!/bin/bash
# PreToolUse hook (matcher: Bash) — mechanically enforces architecture-implementer's
# own "Web3 no-execute rule" (see agents/architecture-implementer.md's "Rules for
# implementation") at the tool-call level, instead of resting entirely on that
# agent's prompt compliance. Blocks a Bash command that looks like a chain deploy
# or transaction broadcast (hardhat/truffle/foundry/anchor/solana/near/aptos/sui/
# cosmwasm/starknet/stellar-soroban CLIs, a scripts/deploy/* script, or an
# npm/yarn/pnpm "deploy" script) while an implementation plan on disk currently
# reads Status: In progress
# — the window during which architecture-implementer is (or was, if interrupted)
# actively writing this project's on-chain code.
#
# Scope and limitation: this checks disk state, not "is architecture-implementer
# specifically the caller right now" — it blocks any matching Bash command, from
# any caller, while ANY plan file under docs/architecture-designer/plan/ reads
# Status: In progress. This is deliberately cautious given the domain (a wrong
# deploy can mean irreversible fund loss), but it means a stale, never-resumed
# In-progress plan from an unrelated crashed run can also block an unrelated,
# fully legitimate deploy later — resolve by finishing or superseding that plan
# (see the plugin README's "Resuming implementation plans") if this ever blocks
# something it shouldn't. Pattern coverage is necessarily a heuristic, not an
# exhaustive list of every chain toolchain's deploy command.
set -uo pipefail

command -v jq >/dev/null 2>&1 || exit 0

input=$(cat)
command_str=$(printf '%s' "$input" | jq -r '.tool_input.command // empty' 2>/dev/null)
[ -z "$command_str" ] && exit 0

contains() {
  case "$command_str" in
    *"$1"*) return 0 ;;
    *) return 1 ;;
  esac
}

is_safe_network() {
  case "$1" in
    hardhat|localhost|local|development|ganache|test|"") return 0 ;;
    *) return 1 ;;
  esac
}

network_arg=$(printf '%s' "$command_str" | grep -oE -- '--network[= ]+[A-Za-z0-9_.-]+' | head -1 | sed -E 's/--network[= ]+//')

reason=""
if contains "scripts/deploy/"; then
  reason="invokes a script under scripts/deploy/"
elif contains "forge script" && contains "--broadcast"; then
  reason="forge script --broadcast"
elif contains "forge create"; then
  reason="forge create"
elif contains "cast send"; then
  reason="cast send"
elif contains "anchor deploy"; then
  reason="anchor deploy"
elif contains "solana program deploy"; then
  reason="solana program deploy"
elif contains "near deploy"; then
  reason="near deploy"
elif contains "aptos move publish"; then
  reason="aptos move publish"
elif contains "sui client publish"; then
  reason="sui client publish"
elif contains "mxpy contract deploy"; then
  reason="mxpy contract deploy"
elif contains "contract deploy"; then
  reason="stellar/soroban contract deploy"
elif contains "contract install" || contains "contract upload"; then
  reason="stellar/soroban contract install/upload"
elif contains "tx wasm store" || contains "tx wasm instantiate"; then
  reason="cosmwasm tx wasm store/instantiate"
elif contains "starknet deploy" || contains "sncast deploy"; then
  reason="starknet deploy"
elif contains "npm run deploy" || contains "yarn deploy" || contains "pnpm deploy"; then
  reason="npm/yarn/pnpm deploy script"
elif { contains "npm run" || contains "yarn " || contains "pnpm "; } && contains ":deploy"; then
  reason="npm/yarn/pnpm deploy script"
elif { contains "hardhat deploy" || contains "hardhat run"; } && ! is_safe_network "$network_arg"; then
  reason="hardhat deploy/run --network ${network_arg:-<unresolved>}"
elif contains "truffle migrate" && ! is_safe_network "$network_arg"; then
  reason="truffle migrate --network ${network_arg:-<unresolved>}"
fi

[ -z "$reason" ] && exit 0

cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0

plan_dir="docs/architecture-designer/plan"
[ -d "$plan_dir" ] || exit 0

for f in "$plan_dir"/*.md; do
  [ -e "$f" ] || continue
  if grep -qE '^\|[[:space:]]*Status[[:space:]]*\|[[:space:]]*In progress' "$f" 2>/dev/null; then
    echo "BLOCKED: this command ($reason) looks like a chain deploy or transaction broadcast, and $f currently reads 'Status: In progress' — architecture-implementer's Web3 no-execute rule forbids executing a deploy while a plan is still being implemented. If this is an intentional deploy by the user rather than architecture-implementer, finish or supersede that plan first (see 'Resuming implementation plans' in the plugin README), or run this command outside Claude Code." >&2
    exit 2
  fi
done

exit 0

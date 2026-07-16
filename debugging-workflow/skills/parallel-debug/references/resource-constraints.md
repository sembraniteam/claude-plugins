# Preflight Check and Degraded Mode

Both features exist for the same underlying reason: a parallel-debug session multiplies cost by
`hypothesis_count` before it produces a single piece of evidence — N worktrees, N dependency installs, N test
runs. That multiplication is invisible until it's already happened. The preflight check catches it before any
worktree exists; degraded mode reduces the multiplier itself for machines that can't absorb it.

---

## Preflight check (`SKILL.md` Step 0)

### Purpose

Distinguish two very different reasons a test run could go badly:
1. **The project's test environment is broken or too slow to multiply** — missing services, unset env vars,
   a suite that takes 10 minutes on a good day. This is worth stopping for, before it happens four times over.
2. **The test suite ran fine and reported ordinary failures** — including a failure related to the bug being
   chased. This is exactly the expected, useful state to start a debug session from. It must never trigger an
   abort — aborting here would make the preflight check reject the very bugs the plugin exists to investigate.

The check exists to catch case 1 without misfiring on case 2.

### Algorithm

1. Detect the project's install command and full-suite test command. Reuse the same per-language detection
   `hypothesis-investigator` Phase 1 step 1 uses for install commands (`../../../agents/hypothesis-investigator.md`);
   for the *full-suite* invocation (not a single targeted test), use the project's canonical command if one is
   discoverable (an npm/composer/etc. `test` script, a `Makefile` target, a CI config's test step) — this is more
   reliable than guessing, since projects frequently wrap the raw test runner in setup logic. Fall back to the
   bare runner only if none of those exist:

   | Language              | Fallback full-suite command |
   |------------------------|------------------------------|
   | Node/TypeScript        | `npm test` (or the declared `package.json` `scripts.test`) |
   | Dart/Flutter           | `dart test` / `flutter test` |
   | Python                 | `pytest` |
   | Rust                   | `cargo test` |
   | Go                     | `go test ./...` |
   | Java/Kotlin (Gradle)   | `./gradlew test` |
   | Java/Kotlin (Maven)    | `mvn test` |

   If no test command can be discovered at all (no test framework detected in the project), skip the preflight
   entirely and proceed to Step 1 — there is nothing to preflight, and this is a pre-existing constraint of the
   plugin (each investigator's Phase 1 will hit the same wall independently), not a new failure mode to guard
   against here.

2. Run the install step once, on the current branch, in the main working tree (not a worktree — there is none
   yet). If install fails outright (dependency resolution error, registry unreachable, auth failure), that is
   an environment failure — stop immediately, do not proceed to running tests.

3. Run the full-suite command wrapped in a wall-clock timeout of `preflight_max_minutes` (config field, default
   `5`): `timeout <preflight_max_minutes>m <test_command>` (or the platform equivalent). Record the wall-clock
   duration and exit behavior.

4. Classify the result:
   - **Timed out** (hit the `timeout` wrapper's limit without the command finishing) → environment/heaviness
     failure. Stop.
   - **Command could not execute at all** — "command not found," module resolution failure, connection refused
     to a database/service, missing config file, container not running, or any other error that prevented the
     test runner itself from starting and producing a normal pass/fail summary → environment failure. Stop.
   - **Command ran to completion and produced a normal test summary** (some number of tests passed, some
     failed, or even all failed) → this is a **pass** for preflight purposes, regardless of how many individual
     tests failed. A suite that runs to completion in under the time budget, even with failures, is exactly the
     state this workflow is designed to investigate. Proceed to Step 1.

### On stop

Report to the user plainly what happened (install failure, timeout at N minutes, or the specific "could not
execute" signal seen) and recommend direct/manual debugging instead: "The test suite [failed to install
dependencies / did not finish within N minutes / could not run — <specific error>]. Running this again across
4 isolated worktrees would multiply the same problem, not diagnose it. Recommend investigating directly instead
of starting a parallel-debug session." Do not create any session directory, worktree, or agent when stopping
here — this check runs before Step 0 item 1 has any lasting effect beyond the session directory itself, so
stopping cleanly here leaves nothing to clean up.

---

## Degraded mode (`degraded_mode: true`)

### When to use it

Low-RAM/low-disk machines, CI runners with tight resource caps, or any environment where running
`max_parallel_agents` concurrent dependency installs and test suites would thrash. Setting `max_parallel_agents: 1`
alone is *not* equivalent to degraded mode: Step 2's default behavior still creates one worktree per hypothesis
up front (via a loop over all hypothesis ids), so even with concurrency capped at 1, disk usage still scales
with `hypothesis_count` — `hypothesis_count` full source checkouts on disk at once, not one. Degraded mode
collapses that to a single worktree, which is the mode's one unconditional benefit regardless of language or
package manager. Whether it also saves *install time* across hypotheses varies — see the caveat at the end of
"Mechanics" below; don't assume it for every ecosystem.

### Mechanics

**Step 2 (worktree creation)**: create exactly one worktree instead of looping over hypothesis ids:

```bash
git worktree add .claude/debug-sessions/{session_id}/shared -b debug/{session_id}/shared {base_sha}
```

**Step 3 (spawn investigators)**: ignore `max_parallel_agents` — spawn investigators one at a time, strictly
sequentially, regardless of its configured value. Before each investigator except the first, reset the shared
worktree back to a clean `base_sha` state so the next hypothesis starts from the same baseline the first one
did, not from whatever the previous hypothesis left behind:

```bash
git -C .claude/debug-sessions/{session_id}/shared reset --hard {base_sha}
git -C .claude/debug-sessions/{session_id}/shared clean -fd
```

Use `reset --hard`, not `checkout -B`. `hypothesis-investigator` never commits inside its worktree, for any
outcome (see Phase 3 of `../../../agents/hypothesis-investigator.md`) — a confirmed fix is captured as text in
`fix_diff` via `git diff`, but the actual file modifications stay uncommitted in the working tree, exactly like
an exhausted, unconfirmed hypothesis's half-applied fix. In standard mode that's inert, since the worktree is
discarded afterward. In degraded mode the same worktree is reused, so those uncommitted modifications to tracked
files (a fix, a half-applied fix, or a lockfile Phase 1's install rewrote and left unstaged per
`side_effects_flagged`) are still sitting in the working tree when the next hypothesis starts. `checkout -B` is
a checkout operation and inherits checkout's
safety behavior: it can refuse ("local changes would be overwritten") or, depending on exactly what changed,
leave some of that dirty state in place — it does not guarantee a clean baseline. `reset --hard {base_sha}`
unconditionally discards all uncommitted modifications to tracked files and moves the branch tip back to
`base_sha` in the same step, with no refusal case; it is the only one of the two that actually delivers the
"same baseline every time" guarantee this mode depends on. This includes the intent-to-add markers Phase 3 leaves
behind for a brand-new test file (`git add -N`): git treats an intent-to-add path as tracked for reset purposes,
so `reset --hard` removes both the index entry and the file's on-disk content, not just a partial revert — this
is what actually prevents one hypothesis's new test file from leaking into the next hypothesis's `git status`.
`clean -fd` still runs afterward to remove untracked
files a failed attempt may have left behind, without `-x`, so gitignored directories (`node_modules/`, `.venv/`,
build output) are preserved on disk rather than deleted.

Whether that preserved directory actually saves install *time* on the next hypothesis depends on the
project's package manager — do not claim a uniform speedup in the plan, since `hypothesis-investigator`
Phase 1 step 1 always re-runs its install command regardless of what's already on disk:
- **Python/pip/poetry**: a real win — installing into an existing virtualenv is incremental, not a cold build.
- **Rust/Go/Gradle/Maven**: install/build caches for these already live outside the worktree (global module
  cache, `~/.cargo`, `~/.m2`, Gradle cache), so they are already shared across separate worktrees in standard
  mode too — preserving the worktree directory itself adds nothing beyond what standard mode already gets.
- **npm (`npm ci`)**: no win at all. `npm ci` deletes `node_modules/` before reinstalling by design, every
  time, specifically to guarantee a clean install — preserving it on disk between hypotheses does not skip
  this step.

The one benefit that holds unconditionally, in every ecosystem, is the disk-footprint reduction from Step 2
(one worktree instead of `hypothesis_count`) — that is the claim to make when recommending this mode, not a
blanket install-time saving.

Pass every investigator the same `worktree_path` (`.claude/debug-sessions/{session_id}/shared`). Each still
writes its own `hN.report.yaml` to its own sibling path, exactly as in standard mode — only the worktree is
shared, not the report.

**Step 7 (cleanup)**: remove the single shared worktree and its one branch instead of looping over `hN`:

```bash
git worktree remove .claude/debug-sessions/{session_id}/shared --force
git branch -D debug/{session_id}/shared
```

### Trade-offs to state to the user up front

- **No concurrency**: wall-clock time scales linearly with `hypothesis_count` instead of staying roughly
  constant — this is the whole point of the mode, but it means a 4-hypothesis session takes roughly 4x as long
  as it would with full parallelism, not the same time.
- **No audit-trail window to worry about**: because nothing is ever committed, `reset --hard` doesn't strand any
  git object that needs reflog protection — the fix only ever exists as working-tree changes, which `reset --hard`
  is about to discard on purpose. What has to survive is the *text* of `fix_diff`, and it already does: each
  investigator finishes Phase 4 (writing its `hN.report.yaml`, `fix_diff` included) before the orchestrator resets
  the shared worktree for the next hypothesis, per the ordering in `SKILL.md` Step 3. The report file lives one
  level up, outside the worktree the reset touches, so it's unaffected by any of this.

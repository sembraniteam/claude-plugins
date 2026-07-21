---
name: implement
description: This skill should be used when the user wants to turn an approved architecture document into working code, or wants to generate/scaffold a project after a design or review session — says "implement the architecture", "scaffold the project", "generate the code from my architecture", "create project files from the design", "turn my architecture into code", "create the folder structure", "start implementation", "let's start coding", or "generate the project skeleton".
allowed-tools: ["Read", "Glob", "Bash", "Agent"]
---

# Architecture Designer — Implementation Workflow

This skill turns an approved architecture document into a working project skeleton: data models, API stubs, configuration files, and infrastructure files. It always proposes a folder structure first and waits for the user's confirmation before writing any files.

**Scripts directory:** see "Path resolution" at the bottom of this file.

---

## Before starting — session completeness gate

Check for `docs/architecture-designer/session.json`:

- **If the file exists**: read it in full, then run `python3 <scripts_dir>/validate-session.py` and show its output — this is a hard gate; do not proceed to Step 1 until it reports `SESSION CHECK PASSED`. See `design/references/session-schema.md` section "Session completeness gate" for what the script checks, how to resolve a failure, and why this gate applies to `implement` even though its steps mostly work from the confirmed architecture document rather than the session stages directly. Reading it in full here (rather than only running the validator) is what makes its `stage5` object available as a cross-check for Step 3's "Technology stack" input — the architecture document itself is that input's primary source, not `stage5` (see Step 3 for why).
- **If the file does not exist**: this gate only applies when `session.json` exists — proceed without it. The architecture document confirmed in Step 1 is the authoritative source of truth for implementation in that case.

---

## Step 1 — Find the architecture document

Check for an architecture document path in this order:

1. **`docs/architecture-designer/session.json`** — if it exists and contains a `documents` array, use its last entry (the most recently saved document) — the authoritative location when this skill follows a design session in the same working directory. If that path doesn't resolve to an existing file (moved or deleted since), fall back to option 2, not directly to option 3 — a stale recorded path doesn't mean no path is available; the current conversation may still hold the correct one.
2. **Current conversation context** — if the user just completed a `/architecture-designer:design` or `/architecture-designer:review` session and the document path is visible in the conversation.
3. **Manual selection** — if neither above yields a path, proceed to list files as described below.

**If a document path is in context**: confirm with the user:
> "I'll implement from `{path}`. Is that the right document?"

**If no document is in context**: list all files in `docs/architecture-designer/architecture/`, sorted alphabetically ascending (which is also oldest-to-newest, since filenames are date-prefixed), then present the list reversed so the newest file appears first. Ask which one to use, or default to the newest.

If the directory is empty or doesn't exist, tell the user and suggest running `/architecture-designer:design` first.

**Verify the document is approved**: once the document is confirmed, read its metadata table on line 1 and check the `Status` column. If it reads anything other than `Approved` (e.g. `Draft`, meaning it may not have passed review), warn the user before proceeding:
> "This document's status is `{status}`, not `Approved` — it may not have been reviewed yet. Implementing from it anyway could bake in unresolved issues. Continue anyway, or run `/architecture-designer:review` first?"
Proceed only if the user confirms. If line 1 isn't a metadata table in the expected format at all (e.g. a hand-authored or legacy document), treat `Status` as unknown and use the same warning, substituting "an unrecognized or missing status" for `{status}`.

---

## Step 2 — Assess the existing project

Scan the current working directory for signs of an existing project, per `design/references/session-schema.md` section "Existing-project scan categories" (four categories: dependency manifests, source directories, configuration files, test directories).

**If the project looks empty** (none of the four categories found anything): tell the user the implementer will generate the full project from scratch. No question needed — proceed to Step 3.

**If any category found something**: summarise what was found and ask the question in `design/references/session-schema.md` section "Merge-strategy question" (this skill is the authoritative owner of that question's exact wording — the `design` and `review` skills point back here). Wait for the answer before proceeding.

---

## Step 3 — Spawn the implementation-planner agent

Resolve the applicable remediation plan per `design/references/session-schema.md` section "Finding the applicable remediation plan", using the document confirmed in Step 1.

Then run `design/references/session-schema.md` section "Resumable-plan detection procedure" (this skill is one of its three canonical call sites) using the document confirmed in Step 1 as `{document}` to produce the **Previous plan path**, if the user chooses to resume.

Then follow `design/references/session-schema.md` section "Implementation-planner → architecture-implementer spawn sequence" to spawn `implementation-planner` and, once its plan is confirmed, `architecture-implementer` (Step 4 below), passing these six inputs:

- **Architecture document path** — the file confirmed in Step 1
- **Existing project summary** — what was found in Step 2, translated into the agent's expected strategy label: `Fresh start (empty project)` if the project looked empty; `Merge` if the user chose (a); `Fresh start (existing project)` if the user chose (b); `User-described layout` if the user chose (c)
- **Technology stack** — read from the approved architecture document's Technology Decisions section (section 5); this is the current, authoritative stack regardless of whether a review revision changed it after `session.json`'s `stage5` was last written — only `design/SKILL.md` writes `stage5`, and a stack-changing revision doesn't update it (see `design/references/session-schema.md` section "Single writer per key"), so `stage5` can go stale relative to the document exactly when it matters most. If `docs/architecture-designer/session.json` was read at the gate above and contains a `stage5` object, or a prior design session is still in conversation context, use that only to cross-check or fill in detail the document's own section doesn't spell out (e.g. exact package versions) — never let it override what the document actually states.
- **Agent tools** (optional) — if `docs/architecture-designer/session.json` exists and contains a non-empty `"agentTools"` array, pass it along so the agent can note which MCP/Skill tools are available for later implementation steps
- **Remediation plan path** — resolved per `design/references/session-schema.md` section "Finding the applicable remediation plan" above. The strategy label above already reflects what Step 2's scan actually found — do not override it just because a remediation plan is present (see that same section).
- **Previous plan path** — the resumed plan's `path`, if the user chose to continue above (omit otherwise)

For reference, `implementation-planner` in turn: reads the document and surfaces any remaining ambiguities all at once, not one by one; if a **Previous plan path** was passed, carries forward its checklist items (done, pending, and failed) into the proposed structure before presenting it; proposes a full folder structure as an ASCII tree, annotating any files that already exist and asking how to handle collisions if fresh-starting into an existing project; waits for the user's confirmation or adjustments; saves the plan (split into `{yyyymmdd}-{topic}-part{n}-of-{N}.md` parts instead of one file for large projects — more than 40 checklist items — per its "Splitting large plans" step; marks a resumed previous plan `Superseded`); and reports back the plan file path(s).

---

## Step 4 — Spawn the architecture-implementer agent

`architecture-implementer` (spawned per the shared sequence above) reads the confirmed plan and the architecture document, then: implements every file — models from the ERD, route stubs from sequence diagrams, configuration files, Docker setup, infrastructure as code — checkpointing each file's checkbox to `[x]` (or `[ ] FAIL: {reason}`) immediately as it's written and verified, rather than batching updates until the end, so an interrupted run leaves the plan file an accurate resume point; once every group is done, a final verification pass re-checks the result against the document — confirming generated models/routes actually match the ERD/sequence diagrams and that named technologies weren't substituted, flagging any functional requirement with no corresponding file under "Requirements not yet reflected in code" — and sets `Status` to `Complete`; it also offers an optional smoke test that installs dependencies and verifies the project compiles or starts (requires the user's confirmation since it modifies the project directory).

No further guidance is needed once it's spawned — it has complete instructions. If it refuses to proceed (e.g. reports "No confirmed implementation plan found") or reports a mid-run blocker it cannot resolve on its own (something the plan doesn't cover), do not treat this as a normal completion — resolve the blocker with the user (which may mean re-spawning `implementation-planner` to update the plan) and re-spawn `architecture-implementer` once resolved, the same as Step 3's contingency for `implementation-planner`.

Proceed to Step 5 once the final part (or the only part, if the plan was not split) reports `Status: Complete`.

---

## Step 5 — Wrap up

**If the agent's summary included a "Requirements not yet reflected in code" section**: surface those gaps to the user explicitly and before the generic wrap-up list below — they represent requirements the plan never covered, not files that failed to write. Suggest running `/architecture-designer:review` to fold them into a remediation plan if the user wants them addressed.

Once the agent reports completion, remind the user:

1. Open the implementation plan file(s) in `docs/architecture-designer/plan/` — the name follows `{yyyymmdd}-{topic}.md`, or `{yyyymmdd}-{topic}-part{n}-of-{N}.md` per part if the plan was split for size; if implementation ran multiple times on the same day, the latest will have a `-2`, `-3` suffix
2. Copy `.env.example` → `.env` and fill in real credentials (database URL, secrets, API keys)
3. Run the setup command the agent provided (typically `npm install && npm run setup` or equivalent)
4. Start the dev server and verify the app boots without errors
5. Test the primary endpoint from the sequence diagram manually
6. Commit the skeleton as a clean baseline before adding business logic

Let the user know they can run `/architecture-designer:review` at any time to revise the architecture and re-run this skill to update the implementation.

---

## Path resolution

`<scripts_dir>` = the `scripts/` directory of the architecture-designer plugin, two levels above this file (`../../scripts/`). Resolve it from the absolute path of this SKILL.md at runtime.

`design/references/...` = the sibling `design/` skill's `references/` directory, one level up from this file then into `design/references/` (e.g. `../design/references/session-schema.md`). Resolve it the same way, from the absolute path of this SKILL.md at runtime.

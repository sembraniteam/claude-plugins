---
name: implement
description: This skill should be used when the user wants to turn an approved architecture document into working code, or wants to generate/scaffold a project after a design or review session — says "implement the architecture", "scaffold the project", "generate the code from my architecture", "create project files from the design", "turn my architecture into code", "create the folder structure", "start implementation", "let's start coding", or "generate the project skeleton".
allowed-tools: ["Read", "Edit", "Glob", "Bash", "Agent"]
---

# Architecture Designer — Implementation Workflow

This skill turns an approved architecture document into a working project skeleton: data models, API stubs, configuration files, and infrastructure files. It always proposes a folder structure first and waits for your confirmation before writing any files.

**Scripts directory:** see "Path resolution" at the bottom of this file.

---

## Before starting — session completeness gate

Check for `docs/architecture-designer/session.json`:

- **If the file exists**: run `python3 <scripts_dir>/validate-session.py` and show its output — this is a hard gate; do not proceed to Step 1 until it reports `SESSION CHECK PASSED`. See `design/references/session-schema.md` section "Session completeness gate" for what the script checks, how to resolve a failure, and why this gate applies to `implement` even though neither of its steps reads stage 1–5 data directly.
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

Spawn `architecture-designer:implementation-planner`. Pass it:

- **Architecture document path** — the file confirmed in Step 1
- **Existing project summary** — what was found in Step 2, translated into the agent's expected strategy label: `Fresh start (empty project)` if the project looked empty; `Merge` if the user chose (a); `Fresh start (existing project)` if the user chose (b); `User-described layout` if the user chose (c)
- **Technology stack** — if a prior design session is still in context, pass the technology stack from stage 5 directly so the agent doesn't have to re-infer it from the document
- **Agent tools** (optional) — if `docs/architecture-designer/session.json` exists and contains a non-empty `"agentTools"` array, pass it along so the agent can note which MCP/Skill tools are available for later implementation steps
- **Remediation plan path** — resolved per `design/references/session-schema.md` section "Finding the applicable remediation plan" above. The strategy label above already reflects what Step 2's scan actually found — do not override it just because a remediation plan is present (see that same section).
- **Previous plan path** — the resumed plan's `path`, if the user chose to continue above (omit otherwise)

The agent will:
1. Read the document and surface any remaining ambiguities (framework choice, ORM vs raw SQL, etc.) — all at once, not one by one
2. If a **Previous plan path** was passed, carry forward its checklist items (done, pending, and failed) into the proposed structure before presenting it — see implementation-planner's carry-over rules
3. Propose a full folder structure as an ASCII tree, annotating any files that already exist; if fresh-starting into an existing project, ask how to handle collisions before saving anything
4. Wait for your confirmation or adjustments before saving the plan
5. Save an implementation plan to `docs/architecture-designer/plan/{yyyymmdd}-{topic}.md` — a markdown checklist of every file to be created, grouped by category — and create one task per file group; if resumed, also mark the previous plan `Superseded`
6. Report back the plan file path once it's saved and confirmed

Wait for the agent to complete and confirm the plan was saved successfully before proceeding to Step 4. If it reports it could not save a confirmed plan (e.g., ambiguities were never resolved), do not proceed to Step 4 — resolve the blocker with the user and re-spawn it instead.

---

## Step 4 — Spawn the architecture-implementer agent

Spawn `architecture-designer:architecture-implementer`. Pass it:

- **Implementation plan path** — reported by implementation-planner in Step 3. This is required; do not spawn the agent without it.
- **Architecture document path** — the same file passed to the planner in Step 3
- **Existing project summary** — the same strategy label passed to the planner in Step 3
- **Technology stack** — the same value passed to the planner in Step 3, if any
- **Agent tools** — the same value passed to the planner in Step 3, if any
- **Remediation plan path** — the same value passed to the planner in Step 3, if any

The agent will:
1. Read the plan and confirm it's `In progress` — refuses to proceed otherwise
2. Read the architecture document for the technical detail needed to write each file
3. Implement every file — models from the ERD, route stubs from sequence diagrams, configuration files, Docker setup, infrastructure as code
4. Update the plan file: mark completed files `[x]`, skipped files `[~]`, failed files `[ ] FAIL: {reason}`, and set Status to Complete
5. Re-check the result against the document: confirm generated models/routes actually match the ERD/sequence diagrams and that named technologies weren't substituted, flagging any functional requirement with no corresponding file under "Requirements not yet reflected in code"
6. Offer an optional smoke test — installs dependencies and verifies the project compiles or starts (requires your confirmation since it modifies the project directory)

Wait for the agent to complete. You do not need to guide it further — it has complete instructions. If it refuses to proceed (e.g. reports "No confirmed implementation plan found") or reports a mid-run blocker it cannot resolve on its own (something the plan doesn't cover), do not treat this as a normal completion — resolve the blocker with the user (which may mean re-spawning `implementation-planner` to update the plan) and re-spawn `architecture-implementer` once resolved, the same as Step 3's contingency for `implementation-planner`.

---

## Step 5 — Wrap up

**If the agent's summary included a "Requirements not yet reflected in code" section**: surface those gaps to the user explicitly and before the generic wrap-up list below — they represent requirements the plan never covered, not files that failed to write. Suggest running `/architecture-designer:review` to fold them into a remediation plan if the user wants them addressed.

Once the agent reports completion, remind the user:

1. Open the implementation plan file in `docs/architecture-designer/plan/` — the name follows `{yyyymmdd}-{topic}.md`; if you ran implementation multiple times on the same day, the latest will have a `-2`, `-3` suffix
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

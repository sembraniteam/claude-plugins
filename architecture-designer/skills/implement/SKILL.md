---
name: implement
description: This skill should be used when the user wants to turn an approved architecture document into working code, or wants to generate/scaffold a project after a design or review session — says "implement the architecture", "scaffold the project", "generate the code from my architecture", "create project files from the design", "turn my architecture into code", "create the folder structure", "start implementation", "let's start coding", or "generate the project skeleton".
allowed-tools: ["Read", "Glob", "Bash", "Agent"]
---

# Architecture Designer — Implementation Workflow

This skill turns an approved architecture document into a working project skeleton: data models, API stubs, configuration files, and infrastructure files. It always proposes a folder structure first and waits for your confirmation before writing any files.

---

## Step 1 — Find the architecture document

Check for an architecture document path in this order:

1. **`docs/architecture-designer/session.json`** — if the file exists and contains a `documents` array, use its last entry (the most recently saved document). This is the authoritative location when this skill follows a design session in the same working directory. If that path does not resolve to an existing file (moved or deleted since the session was recorded), fall back to option 3 below instead of failing.
2. **Current conversation context** — if the user just completed a `/architecture-designer:design` or `/architecture-designer:review` session and the document path is visible in the conversation.
3. **Manual selection** — if neither above yields a path, proceed to list files as described below.

**If a document path is in context**: confirm with the user:
> "I'll implement from `{path}`. Is that the right document?"

**If no document is in context**: list all files in `docs/architecture-designer/architecture/` sorted newest-first (the `{yyyymmdd}` prefix sorts chronologically, so the last entry alphabetically is the newest). Present the list and ask which one to use, or default to the newest.

If the directory is empty or doesn't exist, tell the user and suggest running `/architecture-designer:design` first.

**Verify the document is approved**: once the document is confirmed, read its metadata table on line 1 and check the `Status` column. If it reads anything other than `Approved` (e.g. `Draft`, meaning it may not have passed review), warn the user before proceeding:
> "This document's status is `{status}`, not `Approved` — it may not have been reviewed yet. Implementing from it anyway could bake in unresolved issues. Continue anyway, or run `/architecture-designer:review` first?"
Proceed only if the user confirms.

---

## Step 2 — Assess the existing project

Scan the current working directory for signs of an existing project. Look for:

- Dependency manifests: `package.json`, `go.mod`, `Cargo.toml`, `requirements.txt`, `pyproject.toml`, `pom.xml`
- Source directories: `src/`, `app/`, `lib/`, `cmd/`, `internal/`
- Configuration: `Dockerfile`, `docker-compose.yml`, `.env`, `.env.example`
- Test directories: `tests/`, `test/`, `spec/`, `__tests__/`

**If the project looks empty** (no manifest, no source dirs): tell the user the implementer will generate the full project from scratch. No question needed — proceed to Step 3.

**If files already exist**: summarise what was found and ask the question in `design/references/session-schema.md` § "Merge-strategy question" (this skill is the canonical source of that text — the `design` and `review` skills point back here). Wait for the answer before proceeding.

---

## Step 3 — Spawn the implementation-planner agent

Before spawning, check `docs/architecture-designer/session.json` for a `"remediationPlans"` array. Find the entry whose `document` field equals the document confirmed in Step 1; if found and its `path` exists on disk, this is the remediation plan to pass along — unless `design/references/session-schema.md` § "Checking whether a remediation plan is fully resolved" rules it out.

Then run `design/references/session-schema.md` § "Resumable-plan detection procedure" (this skill is one of the three canonical call sites it describes) using the document confirmed in Step 1 as `{document}`. This produces the **Previous plan path** to pass below, if the user chooses to resume.

Spawn `architecture-designer:implementation-planner`. Pass it:

- **Architecture document path** — the file confirmed in Step 1
- **Existing project summary** — what was found in Step 2, translated into the agent's expected strategy label: `Fresh start (empty project)` if the project looked empty; `Merge` if the user chose (a); `Fresh start (existing project)` if the user chose (b); `User-described layout` if the user chose (c)
- **Technology stack** — if a prior design session is still in context, pass the technology stack from stage 5 directly so the agent doesn't have to re-infer it from the document
- **Remediation plan path** — the remediation plan resolved above (matched by `document`), if it exists on disk and the "Skip if already resolved" check didn't rule it out. The strategy label above already reflects what Step 2's scan actually found — do not override it just because a remediation plan is present; a plan does not by itself prove an existing codebase.
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
- **Remediation plan path** — the same value passed to the planner in Step 3, if any

The agent will:
1. Read the plan and confirm it's `In progress` — refuses to proceed otherwise
2. Read the architecture document for the technical detail needed to write each file
3. Implement every file — models from the ERD, route stubs from sequence diagrams, configuration files, Docker setup, infrastructure as code
4. Update the plan file: mark completed files `[x]`, skipped files `[~]`, failed files `[ ] FAIL: {reason}`, and set Status to Complete
5. Offer an optional smoke test — installs dependencies and verifies the project compiles or starts (requires your confirmation since it modifies the project directory)

Wait for the agent to complete. You do not need to guide it further — it has complete instructions.

---

## Step 5 — Wrap up

Once the agent reports completion, remind the user:

1. Open the implementation plan file in `docs/architecture-designer/plan/` — the name follows `{yyyymmdd}-{topic}.md`; if you ran implementation multiple times on the same day, the latest will have a `-2`, `-3` suffix
2. Copy `.env.example` → `.env` and fill in real credentials (database URL, secrets, API keys)
3. Run the setup command the agent provided (typically `npm install && npm run setup` or equivalent)
4. Start the dev server and verify the app boots without errors
5. Test the primary endpoint from the sequence diagram manually
6. Commit the skeleton as a clean baseline before adding business logic

Let the user know they can run `/architecture-designer:review` at any time to revise the architecture and re-run this skill to update the implementation.

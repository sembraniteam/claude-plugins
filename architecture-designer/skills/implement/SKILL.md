---
name: implement
description: Use this skill when the user wants to turn an approved architecture document into working code — says "implement the architecture", "scaffold the project", "generate the code from my architecture", "create project files from the design", "implement this design", "turn my architecture into code", "create the folder structure", "start implementation", or wants to generate code after an architecture design or review session. Trigger even when the user simply says "let's start coding", "now implement it", or "generate the project skeleton" after an architecture session.
---

# Architecture Designer — Implementation Workflow

This skill turns an approved architecture document into a working project skeleton: data models, API stubs, configuration files, and infrastructure files. It always proposes a folder structure first and waits for your confirmation before writing any files.

**Scripts directory:** `../../scripts/` relative to this SKILL.md.

---

## Step 1 — Find the architecture document

Check for an architecture document path in this order:

1. **`docs/architecture-designer/session.json`** — if the file exists and contains a `documentPath` key, use that value. This is the authoritative location when this skill follows a design session in the same working directory.
2. **Current conversation context** — if the user just completed a `/architecture-designer:design` or `/architecture-designer:review` session and the document path is visible in the conversation.
3. **Manual selection** — if neither above yields a path, proceed to list files as described below.

**If a document path is in context**: confirm with the user:
> "I'll implement from `{path}`. Is that the right document?"

**If no document is in context**: list all files in `docs/architecture-designer/architecture/` sorted newest-first (the `{yyyymmdd}` prefix sorts chronologically, so the last entry alphabetically is the newest). Present the list and ask which one to use, or default to the newest.

If the directory is empty or doesn't exist, tell the user and suggest running `/architecture-designer:design` first.

---

## Step 2 — Assess the existing project

Scan the current working directory for signs of an existing project. Look for:

- Dependency manifests: `package.json`, `go.mod`, `Cargo.toml`, `requirements.txt`, `pyproject.toml`, `pom.xml`
- Source directories: `src/`, `app/`, `lib/`, `cmd/`, `internal/`
- Configuration: `Dockerfile`, `docker-compose.yml`, `.env`, `.env.example`
- Test directories: `tests/`, `test/`, `spec/`, `__tests__/`

**If the project looks empty** (no manifest, no source dirs): tell the user the implementer will generate the full project from scratch. No question needed — proceed to Step 3.

**If files already exist**: summarise what was found and ask:

> "I found an existing project structure. How would you like to proceed?
> **(a) Merge** — add missing files from the architecture without overwriting existing code
> **(b) Fresh start** — generate the complete skeleton; any file that already exists will be flagged before being overwritten — you decide per collision
> **(c) Let me describe what to keep** — I'll describe my existing layout and we'll work around it"

Wait for the answer before proceeding.

---

## Step 3 — Spawn the architecture-implementer agent

Before spawning, check `docs/architecture-designer/session.json` for a `"remediationPlanPath"` key. If present and the file exists at that path, you will pass the path to the implementer so it can apply the confirmed code changes from the remediation plan.

Spawn `architecture-designer:architecture-implementer`. Pass it:

- **Architecture document path** — the file confirmed in Step 1
- **Existing project summary** — what was found in Step 2, and the user's chosen merge strategy (a/b/c or "fresh start" if empty)
- **Technology stack** — if a prior design session is still in context, pass the technology stack from stage 5 directly so the agent doesn't have to re-infer it from the document
- **Remediation plan path** — the path from `session.json → remediationPlanPath`, if it exists on disk (omit if absent). When a remediation plan is present, also pass **mode: merge** — a remediation plan implies an existing codebase, so the implementer must add or modify without overwriting.

The agent will:
1. Read the document and surface any remaining ambiguities (framework choice, ORM vs raw SQL, etc.) — all at once, not one by one
2. Propose a full folder structure as an ASCII tree, annotating any files that already exist; if fresh-starting into an existing project, ask how to handle collisions before writing anything
3. Wait for your confirmation or adjustments before writing anything
4. Save an implementation plan to `docs/architecture-designer/plan/{yyyymmdd}-{topic}.md` — a markdown checklist of every file to be created, grouped by category
5. Implement every file — models from the ERD, route stubs from sequence diagrams, configuration files, Docker setup, infrastructure as code
6. Update the plan file: mark completed files `[x]`, skipped files `[~]`, and set Status to Complete
7. Offer an optional smoke test — installs dependencies and verifies the project compiles or starts (requires your confirmation since it modifies the project directory)

Wait for the agent to complete. You do not need to guide it further — it has complete instructions.

---

## Step 4 — Wrap up

Once the agent reports completion, remind the user:

1. Open the implementation plan file in `docs/architecture-designer/plan/` — the name follows `{yyyymmdd}-{topic}.md`; if you ran implementation multiple times on the same day, the latest will have a `-2`, `-3` suffix
2. Copy `.env.example` → `.env` and fill in real credentials (database URL, secrets, API keys)
3. Run the setup command the agent provided (typically `npm install && npm run setup` or equivalent)
4. Start the dev server and verify the app boots without errors
5. Test the primary endpoint from the sequence diagram manually
6. Commit the skeleton as a clean baseline before adding business logic

Let the user know they can run `/architecture-designer:review` at any time to revise the architecture and re-run this skill to update the implementation.

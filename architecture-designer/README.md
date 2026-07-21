# architecture-designer

Guided architecture and infrastructure design workflow for Claude Code — from requirements gathering to code implementation, with interactive Mermaid diagrams, browser preview, and structured documentation.

## Skills

### `/architecture-designer:design`

Runs the full design process — six requirements/design stages followed by review, preview, and low-level design steps — highlights below:

- **Stage 1 — Requirements gathering** — application goals, stakeholders, business processes, success criteria
- **Stage 2 — Requirements analysis** — functional vs non-functional requirements (performance, security, scalability, availability)
- **Stage 3 — Feasibility study and constraints** — budget, timeline, regulations, team competencies, legacy integrations
- **Stage 4 — Capacity planning** — users, TPS, data volume, peak load, growth projections
- **Stage 5 — Technology selection** — stack, architecture pattern, database, infrastructure, observability strategy, DR approach, and error handling/resilience strategy (retry, circuit breaker, timeouts, graceful degradation); every choice justified against stages 1–4; optionally records which MCP servers/Skills available in the environment match the chosen stack, for use during implementation
- **Stage 6 — Architecture and infrastructure design** — Database schema (ERD, index plan, engine selection), IaC tool selection and module structure, CI/CD pipeline design (platform, stages, branching strategy, environment promotion), and Mermaid diagrams rendered in the browser with zoom/pan/download
- **Step 10 — Low-Level Design** — API contracts (per sequence diagram endpoint), business rules (pseudocode for non-trivial logic), DTOs, inter-service contracts (microservices/event-driven only), and error catalog (Steps 7–9 in between run architecture review, browser preview, and user confirmation)

Produced artifacts:
- Browser preview at `http://localhost:<port>` with zoomable, downloadable 2× resolution PNG diagrams
- Per-diagram collapsible **Details** and **Design Rationale** blocks in the preview
- ERD diagrams include an inline **Index Plan** table in the preview
- `docs/architecture-designer/architecture/{yyyymmdd}-{topic}.md` — complete, reviewed, and approved architecture document including IaC plan, CI/CD pipeline design, and LLD section

### `/architecture-designer:review`

Reviews and revises an existing architecture:
- Document-based review (reads `docs/architecture-designer/architecture/`)
- Codebase-based review (scans project structure, reconstructs actual architecture)
- Drift detection (compares document against codebase)
- Revision flow with new versioned document, preserving full history

### `/architecture-designer:implement`

Turns an approved architecture document into a working project skeleton. Can be invoked standalone (after a design session, or independently by picking a document from `docs/architecture-designer/architecture/`):

1. Locates the architecture document — from session context or lets you choose from saved documents
2. Scans the working directory for an existing project structure
3. Asks how to proceed: merge into existing code, fresh start, or work around a described layout
4. Spawns `implementation-planner` to propose a folder structure, wait for confirmation, and save an implementation plan to `docs/architecture-designer/plan/{yyyymmdd}-{topic}.md` — a markdown checklist of every file to be created, grouped by category (models, routes, config, infrastructure, scripts, tests). For large projects (more than 40 checklist items), the plan is split into a `{yyyymmdd}-{topic}-part{n}-of-{N}.md` sequence instead, each part linked to its neighbor via `Previous plan`/`Next plan` metadata rows
5. Spawns `architecture-implementer`, which reads the confirmed plan and generates all files; updates the plan checkboxes to `[x]` / `[~]` / `[ ] FAIL` when done

## Design workflow

```mermaid
flowchart TD
    A([/architecture-designer:design]) --> Stages["Stages 1–5<br/>requirements · analysis · feasibility · capacity · technology"]
    Stages --> DB["database-designer agent<br/>engine · schema · ERD · index plan · connection config"]
    DB --> DBR{database-reviewer agent}
    DBR -->|DATABASE REVIEW FAILED| DBF[database-fixer agent]
    DBF --> DBR
    DBR -->|DATABASE REVIEW PASSED| IaC["Stage 6b — IaC design<br/>tool · state backend · modules · environments · drift"]
    IaC --> CICD["Stage 6c — CI/CD pipeline design<br/>platform · stages · branching · promotion · secrets"]
    CICD --> Diag["Stage 6d — Diagram generation<br/>deployment · sequence · ERD · C4 · class · state · CI/CD"]
    Diag --> AR["architecture-reviewer agent<br/>correctness · consistency · requirements · risks · DR"]
    AR -->|Critical / Major findings| AF[architecture-fixer agent]
    AF --> AR
    AR -->|REVIEW PASSED| Preview["Browser preview — localhost:port<br/>zoom · pan · 2× PNG · collapsible Details / Rationale"]
    Preview -->|User confirms| LLD["Step 10 — Low-Level Design<br/>API contracts · business rules · DTOs · error catalog"]
    LLD --> Save["Step 11 — Save architecture document<br/>docs/.../architecture/{yyyymmdd}-{topic}.md"]
    Save --> DR{document-reviewer agent}
    DR -->|DOCUMENT REVIEW FAILED| DF[document-fixer agent]
    DF --> DR
    DR -->|DOCUMENT REVIEW PASSED| Approved([Document approved])
    Approved --> Scaffold{Scaffold project?}
    Scaffold -->|Yes| Plan["implementation-planner agent<br/>resolve ambiguities → propose structure → save plan"]
    Scaffold -->|No| Done([Done])
    Plan --> PlanFile["docs/.../plan/{yyyymmdd}-{topic}.md<br/>checkbox per file"]
    PlanFile --> Impl["architecture-implementer agent<br/>read plan → implement → verify"]
    Impl --> Done
```

The `/architecture-designer:review` skill follows the same reviewer → fixer loop for any diagrams or database changes, then saves a new versioned document through the same document-reviewer pass.

`/architecture-designer:implement` can be invoked standalone — it finds the architecture document, checks for an existing project structure, delegates to `implementation-planner` to confirm the folder layout and save the plan, then delegates to `architecture-implementer` to build it. `architecture-implementer` refuses to run without a confirmed plan from `implementation-planner`.

## Sub-agents

Each reviewer has a paired fixer agent. When a reviewer returns findings, the skill spawns the fixer to apply targeted corrections, then re-runs the reviewer. This loop runs until the reviewer passes — no manual editing required. Implementation follows a similar two-step split: `implementation-planner` produces and confirms the plan, then `architecture-implementer` executes it — the implementer never runs without a plan the planner has already saved.

| Agent                                            | Role                                                                                                                                                                                                                                                                    |
|--------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `architecture-designer:architecture-reviewer`    | Validates diagrams for technical correctness, cross-diagram consistency, requirements traceability, risks, observability, and DR; returns Critical / Major / Minor findings with REVIEW PASSED / CONDITIONALLY PASSED / FAILED verdict                                  |
| `architecture-designer:architecture-fixer`       | Applies targeted fixes to Mermaid diagrams based on reviewer findings; updates `diagrams.json` in place and returns a fix log                                                                                                                                           |
| `architecture-designer:database-designer`        | Designs schema, ERD, index plan, engine selection, and secure connection config for SQL and NoSQL                                                                                                                                                                       |
| `architecture-designer:database-reviewer`        | Audits database design: engine fit, schema/3NF, ERD accuracy, index completeness, security config; returns DATABASE REVIEW PASSED / FAILED                                                                                                                              |
| `architecture-designer:database-fixer`           | Corrects schema, ERD, index plan, and connection config; writes the corrected ERD and `indexPlan` directly into `diagrams.json` (same pattern as `architecture-fixer`), and returns the corrected schema, ERD, index plan, and connection config for document embedding |
| `architecture-designer:document-reviewer`        | Audits saved documents for format compliance (F1–F7) and content completeness (C1–C9, including IaC, CI/CD, and decentralized-architecture sections); returns DOCUMENT REVIEW PASSED / FAILED                                                                           |
| `architecture-designer:document-fixer`           | Fixes specific format and content failures in the document based on reviewer findings; overwrites the draft in place                                                                                                                                                    |
| `architecture-designer:implementation-planner`   | Resolves implementation ambiguities, proposes a folder structure, waits for confirmation, and saves the implementation plan; does not write application code                                                                                                            |
| `architecture-designer:architecture-implementer` | Reads the confirmed implementation plan and the approved document, then implements project skeleton, data models, routes, and infrastructure files; refuses to run without a confirmed plan                                                                             |

## Scripts

Most scripts are Node.js ESM (`.mjs`); `validate-session.py` is a standalone Python 3 script (stdlib only, no dependencies) invoked with `python3`. They run identically on Windows, macOS, and Linux, given both a Node.js and a Python 3 runtime on `PATH`. The preview server loads Mermaid v11 and the ELK layout engine from CDN — an internet connection is required while the browser preview is open.

`validate-diagrams.mjs` uses a two-tier strategy: the `mermaid` package (Jison parsers) for legacy types (flowchart, ERD, sequence, C4, class, state) and `@mermaid-js/parser` for new types (architecture-beta). If packages are missing it degrades gracefully to heuristics rather than crashing. Run `npm install` once in the `scripts/` directory before first use:

```bash
# Install validation dependency (once)
cd scripts && npm install

# Validate diagrams.json syntax before opening the preview (exits 0/1)
node scripts/validate-diagrams.mjs

# Check that session.json's required fields (schemaVersion, project, description)
# and stages 1-5 are complete before Stage 6
python3 scripts/validate-session.py

# Find a free port in 3000–9000
node scripts/find-port.mjs

# Start the preview server (opens browser automatically)
node scripts/preview-server.mjs <port>
```

The preview server reads `docs/architecture-designer/diagrams.json` on every request — reload the page to see diagram updates without restarting the server.

`validate-diagrams.mjs` catches real Mermaid syntax errors using the mermaid package for legacy types and `@mermaid-js/parser` for new types. Diagrams validated only by heuristics (when parsers are unavailable) are marked `✓ (heuristics only)` in the output. The design skill runs it automatically before launching the preview, but you can run it manually at any time. `validate-session.py` is run automatically at the start of Stage 6 to confirm all requirement stages are on disk before sub-agents are spawned. The review and implement skills also run it as a hard gate whenever `session.json` exists — a failed check blocks progression until the missing fields/stages are completed (a missing `session.json` entirely is unaffected, since both skills can still work from the document or codebase alone).

## `diagrams.json` schema

```json
{
  "title": "Project Title",
  "topic": "project-topic-kebab",
  "generatedAt": "2026-07-06T10:00:00.000Z",
  "diagrams": [
    {
      "id": "erd",
      "title": "Entity Relationship Diagram",
      "description": "One-sentence summary shown above the diagram.",
      "details": "Multi-paragraph explanation (paragraphs separated by \\n\\n). Rendered as a collapsible block.",
      "rationale": "Why this diagram type was chosen and what design decisions it encodes. Collapsible block.",
      "indexPlan": [
        { "name": "idx_users_email", "table": "users", "columns": "email", "type": "UNIQUE B-TREE", "reason": "Login lookup" }
      ],
      "code": "erDiagram\n  USERS { uuid id PK }\n..."
    }
  ]
}
```

`indexPlan` is optional and only used for `erDiagram` entries — it renders as an inline index plan table below the ERD. Every row must be an index (five keys: `name`, `table`, `columns`, `type`, `reason`) — `validate-diagrams.mjs` rejects rows that aren't. See `skills/design/references/diagrams-guide.md` for the field guide, including the deprecated `companionTable` legacy key.

## `session.json` schema

`docs/architecture-designer/session.json` is the requirements-and-history file every skill and agent reads and writes throughout a project's lifetime. It holds the confirmed answers from Stages 1–6c (`stage1`–`stage6c`), an optional `agentTools` list, an optional `web3` object (the Web3/decentralized track's confirmed dimension answers — see `skills/design/references/web3-guide.md` — present only when the application is decentralized), and three history arrays: `documents` (every saved architecture document, oldest first), `remediationPlans` (every saved remediation plan from a review session), and `implementationPlans` (every saved implementation plan). Each array entry is an object — `{ path, createdAt }` for documents, plus `document`/`remediationPlan`/`supersedes` link fields on the plan arrays that tie a plan back to the document it targets, the remediation plan it consumed, and (if it replaced an earlier plan) the plan it superseded. Files written before this schema (v1) may still have plain path strings instead of objects; every reader treats a bare string as `{ path: <string>, ...other fields: null }` rather than failing.

`agentTools` is optional and, unlike the history arrays above, is overwritten in full at each Stage 5 confirmation rather than appended to. It records MCP servers or Skills actually available in the current environment that match the confirmed stack — e.g. a Go language-server MCP for a Go backend — as `{ name, type, purpose }` entries, so `implementation-planner` and `architecture-implementer` can use them later instead of a generic `Read`/`Bash` approach. Selection rules and the category-to-tool mapping live in `skills/design/references/agent-tools.md`. An absent or empty list is the normal case and never blocks any step.

Full schema, the single-writer-per-key rule (each key has exactly one skill/agent that may mutate it — `documents` is the sole append-only exception, legitimately appended to by both `design` and `review` since neither ever touches the other's entries), and the no-CAS read-fresh-modify-write-whole discipline are documented in `skills/design/references/session-schema.md`.

## Resuming implementation plans

Implementation plans are checklists, not one-shot scripts — a run can be interrupted, or finish with some files marked `[ ] FAIL: {reason}`. Every time `/architecture-designer:design`, `/architecture-designer:review`, or `/architecture-designer:implement` is about to spawn `implementation-planner` for a document, it first checks whether an earlier plan for that same document is still actionable (`Status: In progress`, or `Status: Complete` with at least one `[ ] FAIL` item — `architecture-implementer` always finalizes a run as `Complete` even when some files failed). If one is found, you're offered the choice to resume it or start fresh.

Resuming carries the old plan's state forward: completed files become `[~]` (skip, already built — verified against disk before trusting it), pending files stay `[ ]`, and failed files stay `[ ]` with the failure reason embedded so the retry has context. The new plan supersedes the old one — the old plan file's `Status` is updated to `Superseded by {new plan path}` so it's never offered again. If the underlying architecture document itself gets revised in the meantime, any plan still tied to the prior revision is surfaced separately as an orphaned plan you can mark superseded manually, rather than being silently forgotten.

A remediation plan (`docs/architecture-designer/plan/{yyyymmdd}-{topic}-remediation.md`, produced by `/architecture-designer:review` step 4e — format documented in `skills/design/references/remediation-plan-guide.md`) can be resumed the same way, and can be in play at the same time as a resumed implementation plan; `implementation-planner` reconciles the two if they both touch the same file.

**Split plans for large projects**: once a plan's checklist exceeds 40 items (files plus setup/run commands), `implementation-planner` saves it as a sequence of parts instead of one file (`{yyyymmdd}-{topic}-part1-of-3.md`, `-part2-of-3.md`, ...), each with `Split` / `Previous plan` / `Next plan` metadata-table rows. The calling skill spawns `architecture-implementer` once per part, in order, using each part's `Next plan` row to find the next file until the final part reports `None — final part`.

## Document format

Architecture documents are saved to:
```
docs/architecture-designer/architecture/{yyyymmdd}-{topic}.md
```

`{yyyymmdd}` is the ISO-ordered date — year, then month, then day (e.g., `20260705` for 5 July 2026). This order ensures files sort chronologically when listed alphabetically.

Every document begins with a metadata table:

| Date        | Version | Status   | Reason | Previous Document |
|-------------|---------|----------|--------|-------------------|
| 05-Jul-2026 | 1.0     | Approved | -      | -                 |

Revisions create new files (never overwrite), with `Version` incremented, `Reason` filled, and `Previous Document` pointing to the revised file.

## Diagram types

| Diagram          | Mermaid type                       | When created                     |
|------------------|------------------------------------|----------------------------------|
| Use case         | `flowchart LR`                     | Multiple user roles              |
| Business process | `flowchart TD`                     | Complex multi-step workflows     |
| ERD              | `erDiagram`                        | SQL databases                    |
| Sequence         | `sequenceDiagram`                  | Auth flow + one per core feature |
| Class            | `classDiagram`                     | Rich domain model                |
| State            | `stateDiagram-v2`                  | Entities with status lifecycles  |
| C4 Context       | `C4Context`                        | External actors and integrations |
| C4 Container     | `C4Container`                      | Multiple deployable components   |
| Deployment       | `flowchart` or `architecture-beta` | Cloud/infrastructure layout      |
| CI/CD pipeline   | `flowchart TD`                     | 2+ deployment environments       |

All diagrams support zoom in/out/reset (mouse wheel, pinch, buttons) and 2× resolution PNG download.

## Reference files

Detailed, less-frequently-needed content lives under `skills/design/references/` rather than inline in the skill files, and is loaded only when a step needs it:

| File                           | Covers                                                                                                                                                                                                                                 |
|--------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `session-schema.md`            | Full `session.json` schema, array-of-objects shape, single-writer rule, resumable-plan and orphaned-plan detection procedures, plus the session-completeness gate and Proposed-Additions rejection handling shared by all three skills |
| `diagrams-guide.md`            | `diagrams.json` schema, Mermaid v11.16 compatibility rules, node-overlap prevention rules, per-diagram-type templates                                                                                                                  |
| `document-template.md`         | The 10-section architecture document body template (Step 11), plus an optional 11th decentralized-architecture section                                                                                                                 |
| `document-review-checklist.md` | The F1–F7 / C1–C9 document review item catalog and literal formats shared by `document-reviewer` and `document-fixer`                                                                                                                  |
| `remediation-plan-guide.md`    | The remediation plan markdown format and checkbox/suffix conventions                                                                                                                                                                   |
| `discovery-questions.md`       | The full Stage 1–4 requirements-gathering question banks                                                                                                                                                                               |
| `tech-stacks.md`               | Concrete technology stack recommendations by architecture pattern and scale                                                                                                                                                            |
| `agent-tools.md`               | Selection guide for the optional `agentTools` field — matching a confirmed stack against MCP servers/Skills actually available in the environment                                                                                      |
| `iac-guide.md`                 | Infrastructure-as-Code tool selection and module breakdown guidance                                                                                                                                                                    |
| `cicd-guide.md`                | CI/CD platform selection and pipeline stage guidance                                                                                                                                                                                   |
| `lld-guide.md`                 | Low-Level Design artifact formats (API contracts, business rules, DTOs, error catalog)                                                                                                                                                 |
| `web3-guide.md`                | Optional Web3/decentralized track — the seven invariant dimensions to ask about a target blockchain network, network-agnostic and never a source of network-specific facts                                                             |

---
name: review
description: Use this skill when the user wants to review or revise an existing architecture, says "review my architecture", "audit my architecture", "check my architecture", "my architecture needs review", "update my architecture document", "revise the architecture", "architecture drift", "compare design vs implementation", "architecture is outdated", "architecture inconsistency", "check if my code matches my design", or wants to compare their architecture document against their current codebase. Also trigger when the user mentions their architecture document needs updating after new features were added or requirements changed.
---

# Architecture Designer — Review and Revision Workflow

This skill reviews an existing architecture (from a document, the codebase, or both), presents findings, and guides the user through a structured revision process that creates a new versioned document.

**Scripts directory:** `../../scripts/` relative to this SKILL.md.

---

## Before starting — load and validate session context

Check for `docs/architecture-designer/session.json`:

- **If the file exists**: read it in full, then run `node <scripts_dir>/validate-session.mjs` and show its output. This shows which requirement stages are confirmed and reveals gaps before the review begins. If the check reports missing stages, proceed anyway — the review is still useful — but note the incomplete context. The session contents serve as the original requirements baseline for the architecture-reviewer and any revision agents.

- **If the file does not exist**: proceed without session context. Inform the user: "No session.json found — I won't have the original confirmed requirements on hand. The review will rely on the document and/or codebase alone. Sharing the original requirements now will improve the review quality."

**Check for an existing remediation plan**: if `session.json` contains a `"remediationPlanPaths"` array, read the file at its last entry (the most recently saved remediation plan). Then:

- **If the file no longer exists at the stored path**: note it and continue without loading it.
- **If the file exists and has `[ ]` (deferred) items**: surface them before Step 1:
  > "I found a previous remediation plan at `{path}` with **{N} deferred item(s)** not yet addressed. Here they are:
  > {list of [ ] items}
  > Would you like to include these in this review session?"
  If the user says yes, carry the deferred items forward into step 4a (revision scope) so they can be addressed or remain deferred.
- **If the file exists but every item is `[x] *(code aligned)*`** (nothing deferred, all complete): note it briefly to the user:
  > "Previous remediation plan at `{path}` is fully complete — all findings have been code-aligned. Starting fresh review."
  Then continue to Step 1.

---

## Step 1 — Determine review source

Ask the user:

> "What would you like me to review? I can:
> **(a)** Review your existing architecture document in `docs/architecture-designer/architecture/`
> **(b)** Scan your current codebase and reconstruct the actual architecture
> **(c)** Do both — compare the document against the codebase to find drift
>
> Which would you prefer?"

---

## Step 2a — Document-based review

If the user chose (a) or (c):

1. List all files in `docs/architecture-designer/architecture/` sorted by filename (newest date first). Present the list to the user and ask which document to review, or confirm using the latest.
2. Read the selected document.
3. Ask: **"What is your current goal for this review? Has anything changed since this document was written? (New requirements, new constraints, team changes, performance issues, etc.)"**
4. Spawn the `architecture-designer:architecture-reviewer` agent. Pass it:
   - The full contents of the architecture document
   - The original requirements context — the contents of `docs/architecture-designer/session.json` read above (stages 1–5). If session.json was absent or incomplete, use the document's own Requirements Summary section as the baseline instead.
   - The user's current context/goals
   - Any new requirements or constraints the user described
   Let the agent assess: quality, consistency, completeness, and fit with current needs.
5. Present the reviewer's findings to the user.

---

## Step 2b — Codebase-based review

If the user chose (b) or (c):

Scan the codebase to reconstruct the actual architecture:

1. **Project structure**: list top-level directories and key files (`package.json`, `go.mod`, `pom.xml`, `requirements.txt`, `Cargo.toml`, `docker-compose.yml`, `Dockerfile`, etc.)
2. **Services / modules**: identify separate services, modules, or components (in a monorepo, list packages; for a monolith, identify major layers or domains)
3. **Dependencies**: read dependency manifests to identify frameworks, databases, message queues, HTTP clients, and key libraries
4. **Entry points**: find route/controller files, worker entry points, or serverless function definitions
5. **Database connections**: find ORM configurations, migration files, or schema definitions to identify the actual database technology and schema
6. **Infrastructure**: check for `Dockerfile`, `docker-compose.yml`, Kubernetes manifests, Terraform files, CI/CD pipelines

Compose a **Reconstructed Architecture Summary**:
- Architecture pattern (detected from structure)
- Technology stack (frameworks, databases, caches, queues)
- Key components and their relationships
- Deployment configuration

If the user also has a document (option c): compare the reconstructed architecture against the document and produce a **Drift Report**:

**File path requirement**: Every claim in the Drift Report must cite its evidence source. For code-based claims, include the specific file path where the evidence was found (e.g., "`src/auth/middleware.ts` uses JWT but document § 5 specifies OAuth2"). For document-based claims, cite the document section (e.g., "§ 7 Database Design"). A claim without a source reference must not be written.

- Components in the document but absent from the code
- Components in the code but absent from the document
- Naming inconsistencies
- Technology substitutions (e.g., document says Redis, code uses Memcached)
- Structural differences (e.g., document shows microservices, code is a monolith)

---

## Step 3 — Present findings and ask for revision

Present the review findings (architecture review report, drift report, or both) to the user. Then ask:

> **"Based on these findings, would you like to revise the architecture? I can update the affected diagrams, create a new versioned document, and optionally regenerate the implementation skeleton."**

If the user does not want to revise: acknowledge the review is complete. They can run this skill again at any time.

---

## Step 4 — Revision process

If the user agrees to revise:

### 4a. Gather revision scope

Ask:
- Which findings should be addressed in this revision?
- Are there new requirements that should be incorporated?
- Is this a minor revision (1.1) or a major redesign (2.0)?

### 4b. Update diagrams

Based on the revision scope:
- For architecture changes: update the affected Mermaid diagrams (C4, sequence, deployment)
- For database changes: re-spawn the `architecture-designer:database-designer` agent with the updated requirements, then validate with `architecture-designer:database-reviewer`. If the reviewer returns `DATABASE REVIEW FAILED`, spawn `architecture-designer:database-fixer` with the review report, the database-designer output, the requirements summary, and the path to `docs/architecture-designer/diagrams.json`. The fixer writes the corrected ERD and indexPlan directly into `diagrams.json`. Re-run the reviewer after it completes. Repeat until `DATABASE REVIEW PASSED`, **up to a maximum of 3 reviewer–fixer cycles**. If it still returns `DATABASE REVIEW FAILED` after 3 cycles, stop the loop, present the remaining findings to the user verbatim, and ask for their guidance rather than cycling further.
- For new features: add new diagram elements as needed
- For removed components: remove the relevant elements

### 4c. Architecture re-review

Spawn the `architecture-designer:architecture-reviewer` agent with:
- The requirements summary — read from `docs/architecture-designer/session.json` (the original confirmed stages 1–5) plus any new requirements or constraints gathered in step 4a. If session.json is absent, use the previous document's Requirements Summary section.
- All updated diagrams

If Critical or Major findings are returned: spawn `architecture-designer:architecture-fixer` with the review report, `docs/architecture-designer/diagrams.json`, and the requirements summary. After the fixer updates `diagrams.json`:
- If the fix log contains a **"Proposed Additions"** section, present each item to the user for confirmation before continuing. Add confirmed items to `diagrams.json`; discard rejected ones.
- Re-run the reviewer.
- Repeat until `REVIEW PASSED` or `REVIEW CONDITIONALLY PASSED` with all Major items resolved, **up to a maximum of 3 reviewer–fixer cycles**. If issues persist after 3 cycles, stop the loop, present the remaining unresolved findings to the user verbatim, and ask for guidance rather than cycling further.

### 4d. Browser preview

1. Update `docs/architecture-designer/diagrams.json` with the revised diagrams (same JSON format as the design workflow, including `details`, `rationale`, and — for ERD diagrams — `indexPlan` rows; update all three to reflect what changed in the revision). Skip this for any diagram the database-fixer or architecture-fixer already wrote directly in 4b/4c — re-writing it here would just overwrite their fix with stale content.
2. **Validate diagrams**: run `node <scripts_dir>/validate-diagrams.mjs`. If it exits non-zero or prints `VALIDATION FAILED`, fix the flagged issues in `diagrams.json` before opening or refreshing the preview. Revised diagrams are written under longer-context pressure and are at least as likely to contain syntax errors as freshly generated ones — and since this check runs after every `diagrams.json` write in the revision flow (step 1 above, and the fixers in 4b/4c), one gate covers all of them.
3. If a preview server from a previous run is already running (the user will know the URL): tell them to refresh their browser.
4. If no server is running: run `node <scripts_dir>/find-port.mjs`, then `node <scripts_dir>/preview-server.mjs <port>` in the background.
5. Ask: **"Does this revised architecture look correct to you?"**

If further revisions are needed, repeat from step 4b.

### 4e. Save remediation plan

Once the user confirms the revised architecture looks correct, persist the confirmed findings as a living remediation plan.

Save to:
```
docs/architecture-designer/plan/{yyyymmdd}-{topic}-remediation.md
```

- `{yyyymmdd}` — today's date, generated with JavaScript `new Date()` (never a shell command).
- `{topic}` — the topic slug from the architecture document filename (e.g., `20260706-inventory-app.md` → `inventory-app`).
- **Collision avoidance**: if the file already exists, append `-2`, `-3`, etc. until the name is unique (`{yyyymmdd}-{topic}-remediation-2.md`).

Create the `docs/architecture-designer/plan/` directory if it doesn't exist.

**Plan format**:

```markdown
# Remediation Plan: {topic}

| Architecture document | `{document path}`                                    |
|-----------------------|------------------------------------------------------|
| Review source         | {drift report, architecture review, or both}         |
| Date                  | {dd-mmm-yyyy}                                        |
| Status                | In progress                                          |

## Findings

- [x] `src/auth/middleware.ts` — JWT used but document §5 specifies OAuth2 *(addressed in revision — code pending)*
- [ ] `src/payments/service.ts` — Payment service present in code but absent from architecture document *(deferred)*
```

Rules:
- **One checkbox per finding** from the drift report or architecture review report.
- **Source path is mandatory** on every item — the same file-path-citation rule that governs the drift report applies here. A finding without a file path (or a document section reference for document-only claims) must not be written.
- `[x]` for findings the user confirmed as addressed in this revision (the scope agreed in step 4a); `[ ]` for findings deferred.
- **Suffix progression** — use a two-phase suffix for `[x]` items so the document stays readable across sessions:
  - Write `*(addressed in revision — code pending)*` at this step — the diagram fix is done, but the code change will happen during implementation.
  - The implementer updates it to `*(code aligned)*` once the code change is verified. Only the suffix text changes; the `[x]` checkbox stays.
  - `[ ]` items always carry `*(deferred)*`.

This file is a **living document**: in future review sessions, re-open it, tick off deferred items (`[ ]` → `[x]`, with suffix `*(addressed in revision — code pending)*`), and update `Status` to `Complete` when every `[x]` item reads `*(code aligned)*` and no `[ ]` items remain.

After saving, update `docs/architecture-designer/session.json`: append the full absolute path of this file to the top-level `"remediationPlanPaths"` array (create it with this one entry if it doesn't exist yet). Note the path for use when passing it to the implementer in step 4h.

### 4f. Save the revised document

Once the user confirms the revision, save to:
```
docs/architecture-designer/architecture/{yyyymmdd}-{topic}.md
```

**Important**: never overwrite the previous document. Always create a new file. The history must remain intact.

The metadata table:
```markdown
| Date       | Version   | Status | Reason            | Previous Document   |
|------------|-----------|--------|-------------------|---------------------|
| {dd-mmm-y} | {version} | Draft  | {revision reason} | {previous filename} |
```

- `Version`: increment from the previous document. Use `1.1`, `1.2`, ... for minor changes; `2.0` for major redesigns. Ask the user if unsure.
- `Reason`: fill with the reason for this revision (e.g., "Added real-time notifications feature", "Migrated from monolith to microservices", "Performance improvements for 10× user growth")
- `Previous Document`: the filename of the document being revised (e.g., `20260705-inventory-app.md`)
- `Status`: always starts as `Draft`

Generate timestamps using JavaScript `Date`, not shell commands.

After saving, update `docs/architecture-designer/session.json`: append the full absolute path of the saved file to the top-level `"documentPaths"` array (create it with this one entry if it doesn't exist yet). This lets `/architecture-designer:implement` find the latest approved document — the last entry in the array — without asking.

The document body follows the same structure as the design workflow (all sections, all diagrams). This is a standalone document, not a diff — someone reading it without the previous version should have complete context.

### 4g. Document review

Spawn the `architecture-designer:document-reviewer` agent. Pass it:
- Path to the new document
- Requirements summary
- Expected filename

If DOCUMENT REVIEW FAILED: spawn `architecture-designer:document-fixer` with the document path, the review report, the requirements summary, and the path to `docs/architecture-designer/diagrams.json`. Re-run `architecture-designer:document-reviewer` after the fixer applies its corrections. If the fixer's log says the file must be renamed (F6), rename it first. Repeat until DOCUMENT REVIEW PASSED, **up to a maximum of 3 reviewer–fixer cycles**. If failures persist after 3 cycles, present the remaining FAIL items to the user and ask for their input rather than cycling again.

Then update `Status` to `Approved`.

### 4h. Implementation offer

After approval:

> **"The revised architecture document is approved. Would you like me to regenerate the project skeleton based on the updated architecture?"**

If yes: scan the working directory for signs of an existing project (look for `package.json`, `go.mod`, `Cargo.toml`, `requirements.txt`, `pyproject.toml`, `pom.xml`, and source directories `src/`, `app/`, `lib/`, `cmd/`, `internal/`).

**If files already exist**: summarize what was found and ask the same merge-strategy question `/architecture-designer:implement` uses:
> "I found an existing project structure. How would you like to proceed?
> **(a) Merge** — add missing files from the architecture without overwriting existing code
> **(b) Fresh start** — generate the complete skeleton; any file that already exists will be flagged before being overwritten — you decide per collision
> **(c) Let me describe what to keep** — I'll describe my existing layout and we'll work around it"
> Wait for the answer before proceeding.

**If the scan finds nothing**: no question needed — there is no existing codebase to merge into, so treat this as a fresh start into an empty project regardless of the remediation plan's existence.

Then spawn `architecture-designer:architecture-implementer`. Pass it:
- The path to the approved document
- **Existing project summary** — what was found in the scan, translated into the agent's expected strategy label: `Fresh start (empty project)` if the scan found nothing; `Merge` if the user chose (a); `Fresh start (existing project)` if the user chose (b); `User-described layout` if the user chose (c)
- **Technology stack** — from the architecture document's Technology Decisions section (section 5)
- **Remediation plan path** — the full path to the `{yyyymmdd}-{topic}-remediation.md` file saved in step 4e (always present in the review flow). A remediation plan does not by itself imply an existing codebase — the scan result above is what determines the actual strategy; trust the scan, not the plan's mere presence.

---

## Path resolution

`<scripts_dir>` = the `scripts/` directory of the architecture-designer plugin, two levels above this file (`../../scripts/`). Resolve it from the absolute path of this SKILL.md at runtime.

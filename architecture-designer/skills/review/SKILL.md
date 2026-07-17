---
name: review
description: This skill should be used when the user wants to review or revise an existing architecture, says "review my architecture", "audit my architecture", "check my architecture", "my architecture needs review", "update my architecture document", "revise the architecture", "architecture drift", "compare design vs implementation", "architecture is outdated", "architecture inconsistency", "check if my code matches my design", or wants to compare their architecture document against their current codebase. Also trigger when the user mentions their architecture document needs updating after new features were added or requirements changed.
allowed-tools: ["Read", "Write", "Edit", "Bash", "Agent"]
---

# Architecture Designer — Review and Revision Workflow

This skill reviews an existing architecture (from a document, the codebase, or both), presents findings, and guides the user through a structured revision process that creates a new versioned document.

**Scripts directory:** see "Path resolution" at the bottom of this file.

---

## Before starting — load and validate session context

Check for `docs/architecture-designer/session.json`:

- **If the file exists**: read it in full, then run `python3 <scripts_dir>/validate-session.py` and show its output — this is a hard gate; do not proceed to Step 1 until it reports `SESSION CHECK PASSED`. See `design/references/session-schema.md` section "Session completeness gate" for what the script checks and how to resolve a failure (e.g. running `/architecture-designer:design` to fill the gaps). The session contents serve as the original requirements baseline for the architecture-reviewer and any revision agents — reviewing against a known-incomplete baseline risks misjudging drift.

- **If the file does not exist**: this gate only applies when `session.json` exists — proceed without session context. Inform the user: "No session.json found — I won't have the original confirmed requirements on hand. The review will rely on the document and/or codebase alone. Sharing the original requirements now will improve the review quality."

**Check for an existing remediation plan**: if `session.json` contains a `"remediationPlans"` array, read the file at its last entry's `path` (the most recently saved remediation plan; entries are objects, or legacy bare-string paths in older files — see the schema and tolerant-read rule in `design/references/session-schema.md`). Then:

- **Cross-check against the implementation plan first**: apply `design/references/session-schema.md` section "Checking whether a remediation plan is fully resolved". If resolved, skip straight to the "fully complete" message below without re-parsing the remediation plan's own checkboxes. Otherwise, fall through to inspecting the remediation plan file directly, as below.
- **If the file no longer exists at the stored path**: note it and continue without loading it.
- **If the file exists and has `[ ]` (deferred) items**: surface them before Step 1:
  > "I found a previous remediation plan at `{path}` with **{N} deferred item(s)** not yet addressed. Here they are:
  > {list of [ ] items}
  > Would you like to include these in this review session?"
  If the user says yes, carry the deferred items forward into step 4a (revision scope) so they can be addressed or remain deferred, and remember this plan's path — if a new remediation plan is saved in step 4e as a result, it will supersede this one per `design/references/session-schema.md` section "Superseding a remediation plan".
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

1. List all files in `docs/architecture-designer/architecture/` sorted by filename (newest date first). If the directory doesn't exist or contains no files, tell the user no architecture document was found and offer to fall back to option (b) (codebase reconstruction) instead — do not proceed with an empty selection. Otherwise, present the list to the user and ask which document to review, or confirm using the latest.
2. Read the selected document.
3. Ask: **"What is your current goal for this review? Has anything changed since this document was written? (New requirements, new constraints, team changes, performance issues, etc.)"**
4. Spawn the `architecture-designer:architecture-reviewer` agent. Pass it:
   - The full contents of the architecture document
   - The original requirements context — the contents of `docs/architecture-designer/session.json` read above (stages 1–5, plus the top-level `description`). If session.json was absent (the only case reaching this step without it, since an incomplete file is blocked by the gate above), use the document's own Requirements Summary section as the baseline instead.
   - The user's current context/goals
   - Any new requirements or constraints the user described
   Let the agent assess: quality, consistency, completeness, and fit with current needs.
5. Present the reviewer's findings to the user (see Step 3 for how to flag Dimension 6 findings specifically).

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

**File path requirement**: Every claim in the Drift Report must cite its evidence source. For code-based claims, include the specific file path where the evidence was found (e.g., "`src/auth/middleware.ts` uses JWT but document section 5 specifies OAuth2"). For document-based claims, cite the document section (e.g., "section 7 Database Design"). A claim without a source reference must not be written.

- Components in the document but absent from the code
- Components in the code but absent from the document
- Naming inconsistencies
- Technology substitutions (e.g., document says Redis, code uses Memcached)
- Structural differences (e.g., document shows microservices, code is a monolith)

---

## Step 3 — Present findings and ask for revision

Present the review findings (architecture review report, drift report, or both) to the user. If the architecture review report includes a Dimension 6 ("Document and current-intent alignment") finding — one that treats the document as outdated relative to what the user described as their current goal — call it out distinctly from the ordinary diagram findings: it means the document's own prose, not just the diagrams, needs updating in step 4f, and it should factor into the revision scope discussed in step 4a. Then ask:

> **"Based on these findings, would you like to revise the architecture? I can update the affected diagrams, create a new versioned document, and optionally regenerate the implementation skeleton."**

If the user does not want to revise: acknowledge the review is complete. They can run this skill again at any time.

---

## Step 4 — Revision process

If the user agrees to revise:

### 4a. Gather revision scope

Ask:
- Which findings should be addressed in this revision? (Include any deferred items carried forward from the pre-Step-1 remediation-plan check, if the user opted in.)
- Are there new requirements that should be incorporated?
- Is this a minor revision (1.1) or a major redesign (2.0)? If no prior document exists (Step 1 option (b) alone, with nothing to revise), this question doesn't apply — see step 4f's no-prior-document fallback instead.
- Does this revision change whether the stack is decentralized/blockchain-based (adding, removing, or changing the target network)? If so, flag it for 4b — the Web3 track needs to be re-run or removed, mirroring `design/SKILL.md` Step 9's handling of a Stage 5 revision.

### 4b. Update diagrams

Based on the revision scope:
- For architecture changes: update the affected Mermaid diagrams (C4, sequence, deployment)
- For database changes: re-spawn the `architecture-designer:database-designer` agent with the same three inputs `design/SKILL.md` Stage 6a passes on first use — the updated requirements summary, the domain entities extracted from the (now updated) functional requirements, and the access patterns from the business processes — then validate with `architecture-designer:database-reviewer`. If the reviewer returns `DATABASE REVIEW FAILED`, follow `design/references/session-schema.md` section "Reviewer–fixer cycle procedure" (binary verdict — cycle until `DATABASE REVIEW PASSED`): the fixer receives the review report, the database-designer output, the requirements summary, and the path to `docs/architecture-designer/diagrams.json`. It writes the corrected ERD and indexPlan directly into `diagrams.json` **and returns the corrected schema, ERD, index plan, and connection config as text — replace the database-designer output held in context with this corrected text; it is what gets embedded in the revised document (step 4f), not the original.**
- For new features: add new diagram elements as needed
- For removed components: remove the relevant elements
- If 4a flagged a change in decentralization status: read `design/references/web3-guide.md`, work through its seven dimensions against the revised stack, and update `session.json`'s `web3` key accordingly — create it if the revision newly added a decentralized component, overwrite it in full if an existing dimension's answer changed, or delete it entirely if the decentralized component was removed. Update the architecture diagram's on-chain/off-chain boundary to match (dimension 3).

### 4c. Architecture re-review

Spawn the `architecture-designer:architecture-reviewer` agent with:
- The requirements summary — read from `docs/architecture-designer/session.json` (the original confirmed stages 1–5, the top-level `description`, and `agentTools`/`stage6b`/`stage6c`/`web3` when present — every relevant top-level key, not stages alone, and reflecting whatever 4b just wrote to `web3`). If session.json is absent, use the previous document's Requirements Summary section.
- The user's current context/goals and any new requirements or constraints gathered in step 4a — kept as its own item, separate from the requirements summary above, so the agent can tell it received current-intent context (its Dimension 6 input) rather than folding it into the original baseline.
- All updated diagrams

If Critical or Major findings are returned: follow `design/references/session-schema.md` section "Reviewer–fixer cycle procedure" (three-tier verdict): spawn `architecture-designer:architecture-fixer` with the review report, `docs/architecture-designer/diagrams.json`, and the requirements summary, then re-spawn the reviewer to verify per that section.

### 4d. Browser preview

1. Update `docs/architecture-designer/diagrams.json` with the revised diagrams (same JSON format as the design workflow, including `details`, `rationale`, and — for ERD diagrams — `indexPlan` rows). Skip any diagram the database-fixer or architecture-fixer already wrote directly in 4b/4c — re-writing it here would overwrite their fix with stale content.
2. **Validate diagrams**: run `node <scripts_dir>/validate-diagrams.mjs`. If it exits non-zero or prints `VALIDATION FAILED`, fix the flagged issues in `diagrams.json` before opening or refreshing the preview — revised diagrams are at least as likely to contain syntax errors as freshly generated ones. If `DEGRADED MODE` also appears, tell the user validation ran without the real syntax parser (some errors may not have been caught) and that `npm install` in the plugin's `scripts/` directory enables full coverage — proceed anyway, since the script still passed everything it could check.
3. If a preview server from a previous run is already running, tell the user to refresh their browser. Otherwise run `node <scripts_dir>/find-port.mjs`, then `node <scripts_dir>/preview-server.mjs <port>` in the background. Do NOT create a stop-server script — leave the server running.
4. Ask: **"Does this revised architecture look correct to you?"**

If further revisions are needed, repeat from step 4b.

### 4e. Save remediation plan

Once the user confirms the revised architecture looks correct, persist the confirmed findings as a living remediation plan.

Save to:
```
docs/architecture-designer/plan/{yyyymmdd}-{topic}-remediation.md
```

- `{yyyymmdd}` — today's date, generated with JavaScript `new Date()` (never a shell command).
- `{topic}` — the topic slug from the architecture document filename (e.g., `20260706-inventory-app.md` → `inventory-app`); if no prior document exists (Step 1 option (b) alone), use `session.json`'s `project` field instead, or ask the user for a slug if `session.json` doesn't exist either.
- **Collision avoidance**: if the file already exists, append `-2`, `-3`, etc. until the name is unique (`{yyyymmdd}-{topic}-remediation-2.md`).

Create the `docs/architecture-designer/plan/` directory if it doesn't exist.

**Plan format**: follow `design/references/remediation-plan-guide.md` exactly — the checkbox-per-finding rule, mandatory source path, and the two-phase suffix progression for `[x]` items.

After saving, append `{ "path": "<absolute path of this file>", "document": "<the architecture document path this remediation plan targets>", "supersedes": "<previous remediation plan path, if this plan carried its deferred items forward per the pre-Step-1 check — otherwise null>", "createdAt": "<current ISO timestamp>" }` to `session.json`'s top-level `"remediationPlans"` array (create it if absent). If `supersedes` is non-null, also make the terminal write described in `design/references/session-schema.md` section "Superseding a remediation plan" to close out the old plan file. Note the path for passing to the implementer in step 4h.

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

**If no prior document exists** (Step 1 option (b) alone, with no document ever reviewed in this session): this save is the *first* document for the project, not a revision — treat it the same as `design/SKILL.md` Step 11: `Version` is `1.0`, `Previous Document` is `-`, and `Reason` describes why this document is being created now (e.g., "Initial document generated from codebase reconstruction").

Otherwise (a prior document was reviewed in Step 2a):
- `Version`: increment from the previous document. Use `1.1`, `1.2`, ... for minor changes; `2.0` for major redesigns. Ask the user if unsure.
- `Reason`: fill with the reason for this revision (e.g., "Added real-time notifications feature", "Migrated from monolith to microservices", "Performance improvements for 10× user growth")
- `Previous Document`: the filename of the document being revised (e.g., `20260705-inventory-app.md`)
- `Status`: always starts as `Draft`

Generate timestamps using JavaScript `Date`, not shell commands.

After saving, append `{ "path": "<absolute path of the saved file>", "createdAt": "<current ISO timestamp>" }` to `session.json`'s top-level `"documents"` array (create it if absent). This lets `/architecture-designer:implement` find the latest approved document — the last entry's `path` — without asking.

The document body follows the same structure as the design workflow (all sections, all diagrams). This is a standalone document, not a diff — someone reading it without the previous version should have complete context.

### 4g. Document review

Spawn the `architecture-designer:document-reviewer` agent with the path to the new document, the requirements summary (same scope as 4c — every relevant `session.json` top-level key, including `web3` when present), and the expected filename.

If DOCUMENT REVIEW FAILED: spawn `architecture-designer:document-fixer` with the document path, the review report, the requirements summary, and the path to `docs/architecture-designer/diagrams.json`. Rename the file first if the fixer's log says it must be renamed (F6), then follow `design/references/session-schema.md` section "Reviewer–fixer cycle procedure" (binary verdict — cycle until DOCUMENT REVIEW PASSED) to re-spawn `document-reviewer` and verify.

Then update `Status` to `Approved`.

### 4h. Implementation offer

After approval:

> **"The revised architecture document is approved. Would you like me to regenerate the project skeleton based on the updated architecture?"**

If yes: scan the working directory for signs of an existing project, per `design/references/session-schema.md` section "Existing-project scan categories". **If files already exist**: summarize what was found and ask the question in `design/references/session-schema.md` section "Merge-strategy question". **If the scan finds nothing**: no question needed — treat this as a fresh start into an empty project regardless of the remediation plan's existence.

Run `design/references/session-schema.md` section "Resumable-plan detection procedure" using the approved document's path as `{document}` to produce the **Previous plan path**, if the user chooses to resume.

Spawn `architecture-designer:implementation-planner`. Pass it:
- The path to the approved document
- **Existing project summary** — translated into the agent's expected strategy label: `Fresh start (empty project)` if the scan found nothing; `Merge` if the user chose (a); `Fresh start (existing project)` if the user chose (b); `User-described layout` if the user chose (c)
- **Technology stack** — from the architecture document's Technology Decisions section (section 5)
- **Agent tools** (optional) — `session.json`'s `"agentTools"` array, if present and non-empty (this key is written once at Stage 5 during `/architecture-designer:design` and is not re-derived here, but still valid and worth passing through unless the revision replaced the entire stack)
- **Remediation plan path** — the full path to the `{yyyymmdd}-{topic}-remediation.md` file saved in step 4e (always present in the review flow) — see `design/references/session-schema.md` section "Finding the applicable remediation plan" for why its presence must not override the scan-based strategy label
- **Previous plan path** — the resumed plan's `path`, if the user chose to continue (omit otherwise)

Wait for it to report the plan was saved and confirmed. Then spawn `architecture-designer:architecture-implementer` with the implementation plan path from that report, plus the same document path, existing project summary, technology stack, agent tools, and remediation plan path. Do not spawn it if implementation-planner did not report a confirmed plan.

---

## Path resolution

`<scripts_dir>` = the `scripts/` directory of the architecture-designer plugin, two levels above this file (`../../scripts/`). Resolve it from the absolute path of this SKILL.md at runtime.

`design/references/...` = the sibling `design/` skill's `references/` directory, one level up from this file then into `design/references/` (e.g. `../design/references/session-schema.md`). Resolve it the same way, from the absolute path of this SKILL.md at runtime.

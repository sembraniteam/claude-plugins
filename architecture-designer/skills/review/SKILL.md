---
name: review
description: This skill should be used when the user wants to review or revise an existing architecture, says "review my architecture", "audit my architecture", "check my architecture", "my architecture needs review", "update my architecture document", "revise the architecture", "architecture drift", "compare design vs implementation", "architecture is outdated", "architecture inconsistency", "check if my code matches my design", or wants to compare their architecture document against their current codebase. Also trigger when the user mentions their architecture document needs updating after new features were added or requirements changed.
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Agent"]
---

# Architecture Designer — Review and Revision Workflow

This skill reviews an existing architecture (from a document, the codebase, or both), presents findings, and guides the user through a structured revision process that creates a new versioned document.

**Scripts directory:** see "Path resolution" at the bottom of this file.

---

## Before starting — load and validate session context

Check for `docs/architecture-designer/session.json`:

- **If the file exists**: read it in full, then run `python3 <scripts_dir>/validate-session.py` and show its output — this is a hard gate; do not proceed to Step 1 until it reports `SESSION CHECK PASSED`. See `design/references/session-schema.md` section "Session completeness gate" for what the script checks and how to resolve a failure (e.g. running `/architecture-designer:design` to fill the gaps). The session contents serve as the original requirements baseline for the architecture-reviewer and any revision agents — reviewing against a known-incomplete baseline risks misjudging drift.

- **Also check for an interrupted revision in progress**: if `session.json` contains a `progress` key whose `lastCompletedStep` is anything before `step11` (a document save) **and** its `owner` is `"review"`, a previous *revision* session died mid-pipeline. Apply `design/references/session-schema.md` section "Resuming Steps 6a–13 via `progress`" to resume Step 4's revision flow from where it left off instead of restarting Step 4a — including validating any recorded `reviewCycles` verdicts' hashes and checking `docs/architecture-designer/last-review.md` for an unresolved fixer cycle. If `progress.owner` is instead `"design"` (or absent) with `lastCompletedStep` before `step11`, this is an *original* design pipeline that never finished — not a review revision — since `review` never touches `progress` before step 4b and no revision document was ever produced to revise. Do not attempt to resume Step 4 from this state (there is no revision scope, no document to list in Step 2a). Instead tell the user: "It looks like a previous `/architecture-designer:design` session didn't finish (no architecture document was ever saved). Run `/architecture-designer:design` to complete it before reviewing." and stop here rather than proceeding to Step 1.

- **If the file does not exist**: this gate only applies when `session.json` exists — proceed without session context. Inform the user: "No session.json found — I won't have the original confirmed requirements on hand. The review will rely on the document and/or codebase alone. Sharing the original requirements now will improve the review quality."

**Check for an existing remediation plan**: if `session.json` contains a `"remediationPlans"` array, run `design/references/session-schema.md` section "Pre-review remediation-plan carry-forward check" — it scans every entry (not just the latest), may prompt to carry one plan's deferred items into this session's revision scope (step 4a), and reports back one of: nothing to carry forward, everything already resolved, or a specific plan's deferred items to fold in.

---

## Step 1 — Determine review source

Ask the user:

> "What would you like me to review? I can:
> **(a)** Review your existing architecture document in `docs/architecture-designer/architecture/`
> **(b)** Scan your current codebase and reconstruct the actual architecture — useful both for auditing a system you already understand and for producing a first architecture document for a project that was never formally documented
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

Present the review findings (architecture review report, drift report, or both) to the user. **For option (b) alone** (no document was ever reviewed in this session — Step 1 chose codebase reconstruction only): there is no architecture review report or drift report to present, since both require a document (per Steps 2a/2b); present the Reconstructed Architecture Summary directly instead, and ask whether the user wants to formalize it into a first architecture document (step 4f's no-prior-document path handles this).

Otherwise, if the architecture review report includes a Dimension 6 ("Document and current-intent alignment") finding — one that treats the document as outdated relative to what the user described as their current goal — call it out distinctly from the ordinary diagram findings: it means the document's own prose, not just the diagrams, needs updating in step 4f, and it should factor into the revision scope discussed in step 4a. Then ask:

> **"Based on these findings, would you like to revise the architecture? I can update the affected diagrams, create a new versioned document, and optionally regenerate the implementation skeleton."**

If the user does not want to revise (or, for option (b) alone, does not want to formalize the summary into a document): acknowledge the review is complete. They can run this skill again at any time.

---

## Step 4 — Revision process

If the user agrees to revise (or, for option (b) alone, agrees to formalize):

### 4a. Gather revision scope

**Checkpoint partial answers as you go**: after each individual answer the user gives below (not just once this step is fully confirmed), upsert `session.json`'s `pending` key per `design/references/session-schema.md` section "Mid-stage pending answers", using `"review-4a"` as the stage id. Delete `pending` once this step's scope is confirmed and 4b begins.

Ask:
- Which findings should be addressed in this revision? (Include any deferred items carried forward from the pre-Step-1 remediation-plan check, if the user opted in.) For option (b) alone, there are no findings yet — skip this question; the Reconstructed Architecture Summary from Step 2b is the starting point for 4b to diagram, not a set of findings to address.
- Are there new requirements that should be incorporated?
- Is this a minor revision (1.1) or a major redesign (2.0)? If no prior document exists (Step 1 option (b) alone, with nothing to revise), this question doesn't apply — see step 4f's no-prior-document fallback instead.
- Does this revision change whether the stack is decentralized/blockchain-based (adding, removing, or changing the target network)? If so, flag it for 4b — the Web3 track needs to be re-run or removed, mirroring `design/SKILL.md` Step 9's handling of a Stage 5 revision.
- Does this revision change the cloud/infrastructure provider, IaC tool, or CI/CD platform? If so, flag it for 4b — `session.json`'s `stage6b`/`stage6c` and the document's IaC/CI-CD sections need to be updated to match, the same way a Web3 status change updates `web3`.

### 4b. Update diagrams

**First touch of `progress` this revision pass**: if this is the first time this revision touches `session.json`'s `progress` key, set `progress.owner = "review"` (overwrite in full — this is a new pipeline pass, distinct from whatever `design` last left there) per `design/references/session-schema.md`'s `progress` paragraph and "Resuming Steps 6a–13 via `progress`".

**Write each updated diagram to `diagrams.json` as soon as it's finished, not batched at 4d** — read the file fresh, update or append that one diagram's entry, and write the whole file back (same incremental, read-fresh-modify-write-whole discipline `design/SKILL.md` Stage 6d uses — see `design/references/diagrams-guide.md` section "`diagrams.json` Schema"). A session that dies partway through a multi-diagram revision should not lose diagrams already finished.

**For option (b) alone** (formalizing a Reconstructed Architecture Summary into a first document, nothing to "update" yet): generate a fresh diagram set from that summary instead of editing an existing one — apply `design/SKILL.md` Stage 6d's diagram-type selection table and Stage 6a-6e's generation steps (database design, diagram rules, `diagrams.json` schema) as if this were a first design session, using the reconstructed architecture pattern, tech stack, and components as the input in place of stages 1–5. Then continue to 4c as normal.

Otherwise, based on the revision scope:
- For architecture changes: update the affected Mermaid diagrams (C4, sequence, deployment)
- For database changes: re-spawn the `architecture-designer:database-designer` agent with the same three inputs `design/SKILL.md` Stage 6a passes on first use — the updated requirements summary (every relevant top-level key, not stages alone, including `web3` when present — same scope and fallback as 4c below), the domain entities extracted from the (now updated) functional requirements, and the access patterns from the business processes — then validate with `architecture-designer:database-reviewer` (same requirements-summary scope). **Regardless of verdict**, apply `design/references/session-schema.md` section "Reviewer–fixer cycle procedure" step 0 as soon as the report is received (records the verdict/cycle/approved output into `progress.reviewCycles.database` and `docs/architecture-designer/last-review.md`; this runs even on a clean first-try pass, not only on failure). If the reviewer returns `DATABASE REVIEW FAILED`, continue with that section's steps 1–4 (binary verdict — cycle until `DATABASE REVIEW PASSED`): the fixer receives the review report, the database-designer output, the requirements summary (same scope), and the path to `docs/architecture-designer/diagrams.json`. It writes the corrected ERD and indexPlan directly into `diagrams.json` **and returns the corrected schema, ERD, index plan, and connection config as text — replace the database-designer output held in context with this corrected text; it is what gets embedded in the revised document (step 4f), not the original.**
- For new features: add new diagram elements as needed
- For removed components: remove the relevant elements
- If 4a flagged a change in decentralization status: read `design/references/web3-guide.md`, work through its seven dimensions against the revised stack, and update `session.json`'s `web3` key accordingly — create it if the revision newly added a decentralized component, overwrite it in full if an existing dimension's answer changed, or delete it entirely if the decentralized component was removed. Update the architecture diagram's on-chain/off-chain boundary to match (dimension 3).
- If 4a flagged a change in infrastructure provider, IaC tool, or CI/CD platform: read `design/references/iac-guide.md` and/or `design/references/cicd-guide.md` as applicable, work through the affected decision points against the revised stack, and overwrite `session.json`'s `stage6b`/`stage6c` in full to match (this skill is an authorized second writer of these keys for exactly this case — see `design/references/session-schema.md` section "Single writer per key"). Update the deployment/infrastructure and CI/CD pipeline diagrams, and note in 4f that the document's IaC (section 8) and CI/CD (section 9) sections need regenerating from the new decisions rather than carried over unchanged.

### 4c. Architecture re-review

Spawn the `architecture-designer:architecture-reviewer` agent with:
- The requirements summary — read from `docs/architecture-designer/session.json` (the original confirmed stages 1–5, the top-level `description`, and `agentTools`/`stage6b`/`stage6c`/`web3` when present — every relevant top-level key, not stages alone, and reflecting whatever 4b just wrote to `web3`). If session.json is absent, use the previous document's Requirements Summary section. If both are absent (option (b) alone with no session.json — nothing to fall back to), use the Reconstructed Architecture Summary from Step 2b as the requirements baseline instead.
- The user's current context/goals and any new requirements or constraints gathered in step 4a — kept as its own item, separate from the requirements summary above, so the agent can tell it received current-intent context (its Dimension 6 input) rather than folding it into the original baseline.
- All updated diagrams

**Regardless of verdict**, apply `design/references/session-schema.md` section "Reviewer–fixer cycle procedure" step 0 as soon as the report is received (records the verdict/cycle/`diagramsHash` into `progress.reviewCycles.architecture` and `docs/architecture-designer/last-review.md`; this runs even on a clean first-try pass, not only on Critical/Major findings).

If Critical or Major findings are returned: continue with that section's steps 1–4 (three-tier verdict): spawn `architecture-designer:architecture-fixer` with the review report, `docs/architecture-designer/diagrams.json`, and the requirements summary, then re-spawn the reviewer to verify per that section.

Once passed, record `progress.lastCompletedStep = "step7"` per `design/references/session-schema.md` section "Recording `progress.lastCompletedStep`".

### 4d. Browser preview

1. **Confirm `diagrams.json` is current** — every diagram touched in 4b/4c was already written incrementally (per 4b's note and the reviewer–fixer cycle), so this is a final integrity check, not a write: confirm every diagram in the revision scope has a corresponding entry and no entry is partial, same as `design/SKILL.md` Stage 6e.
2. **Validate diagrams**: run `node <scripts_dir>/validate-diagrams.mjs`. If it exits non-zero or prints `VALIDATION FAILED`, fix the flagged issues in `diagrams.json` before opening or refreshing the preview — revised diagrams are at least as likely to contain syntax errors as freshly generated ones. If `DEGRADED MODE` also appears, tell the user validation ran without the real syntax parser (some errors may not have been caught) and that `npm install` in the plugin's `scripts/` directory enables full coverage — proceed anyway, since the script still passed everything it could check.
3. If a preview server from a previous run is already running, tell the user to refresh their browser. Otherwise run `node <scripts_dir>/find-port.mjs`, then `node <scripts_dir>/preview-server.mjs <port>` in the background. Do NOT create a stop-server script — leave the server running. Record `progress.lastCompletedStep = "step8"` per `design/references/session-schema.md` section "Recording `progress.lastCompletedStep`".
4. Ask: **"Does this revised architecture look correct to you?"** Once confirmed, record `progress.lastCompletedStep = "step9"`.

If further revisions are needed, repeat from step 4b.

### 4e. Save remediation plan

**Skip this step entirely for option (b) alone**: there are no findings to remediate — a first-time formalization has nothing to reconcile against, so no remediation plan is created. Proceed straight to 4f.

Otherwise, once the user confirms the revised architecture looks correct, persist the confirmed findings as a living remediation plan.

**Determine the revised document's future path first — do not save the document yet (that is step 4f)**: this plan's `document` field must point at the *revised* document, not the pre-revision one read in Step 2a, since that is what `design/references/session-schema.md` section "Finding the applicable remediation plan" will match against in every future session. Work out the exact filename step 4f is about to save to — `docs/architecture-designer/architecture/{yyyymmdd}-{topic}.md`, applying the same `-2`/`-3` collision-avoidance check 4f uses — now, so this plan can reference it correctly. Step 4f must then save to this exact same filename rather than recomputing it independently, so the two never disagree.

Save the remediation plan to:
```
docs/architecture-designer/plan/{yyyymmdd}-{topic}-remediation.md
```

- `{yyyymmdd}` — today's date, generated with JavaScript `new Date()` (never a shell command).
- `{topic}` — the topic slug from the architecture document filename (e.g., `20260706-inventory-app.md` → `inventory-app`); if no prior document exists (Step 1 option (b) alone), use `session.json`'s `project` field instead, or ask the user for a slug if `session.json` doesn't exist either.
- **Collision avoidance**: if the file already exists, append `-2`, `-3`, etc. until the name is unique (`{yyyymmdd}-{topic}-remediation-2.md`).

Create the `docs/architecture-designer/plan/` directory if it doesn't exist.

**Plan format**: follow `design/references/remediation-plan-guide.md` exactly — the checkbox-per-finding rule, mandatory source path, and the two-phase suffix progression for `[x]` items. The "Architecture document" metadata-table row is the revised document's path determined above, not the pre-revision document.

After saving, append `{ "path": "<absolute path of this file>", "document": "<the revised document's path determined above — the one step 4f is about to save to>", "supersedes": "<previous remediation plan path, if this plan carried its deferred items forward per the pre-Step-1 check — otherwise null>", "createdAt": "<current ISO timestamp>" }` to `session.json`'s top-level `"remediationPlans"` array (create it if absent). If `supersedes` is non-null, also make the terminal write described in `design/references/session-schema.md` section "Superseding a remediation plan" to close out the old plan file. Note the path for passing to the implementer in step 4h.

### 4f. Save the revised document

Once the user confirms the revision, save to `docs/architecture-designer/architecture/{yyyymmdd}-{topic}.md`. **If step 4e ran** (every case except option (b) alone, which skips 4e entirely): use the exact filename 4e already determined and committed to in the remediation plan's `document` field — do not recompute the collision check independently here. **If step 4e was skipped** (option (b) alone): determine the filename here for the first time, applying the `-2`/`-3` collision-avoidance check directly, since there is no remediation plan to have pre-committed it.

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

Record `progress.lastCompletedStep = "step11"` per `design/references/session-schema.md` section "Recording `progress.lastCompletedStep`".

### 4g. Document review

Spawn the `architecture-designer:document-reviewer` agent with the path to the new document, the requirements summary (same scope as 4c — every relevant `session.json` top-level key, including `web3` when present), and the expected filename. **Regardless of verdict**, apply `design/references/session-schema.md` section "Reviewer–fixer cycle procedure" step 0 as soon as the verdict is received (records the verdict/cycle/`documentHash` into `progress.reviewCycles.document` and `docs/architecture-designer/last-review.md`; this runs even on a clean first-try pass, not only on failure).

If DOCUMENT REVIEW FAILED: continue with that section's steps 1–4: spawn `architecture-designer:document-fixer` with the document path, the review report, the requirements summary, and the path to `docs/architecture-designer/diagrams.json`. Rename the file first if the fixer's log says it must be renamed (F6), then re-spawn `document-reviewer` and verify (binary verdict — cycle until DOCUMENT REVIEW PASSED).

Then update `Status` to `Approved`. Record `progress.lastCompletedStep = "step12"` per `design/references/session-schema.md` section "Recording `progress.lastCompletedStep`".

### 4h. Implementation offer

After approval:

> **"The revised architecture document is approved. Would you like me to regenerate the project skeleton based on the updated architecture?"**

If yes: scan the working directory for signs of an existing project, per `design/references/session-schema.md` section "Existing-project scan categories". **If files already exist**: summarize what was found and ask the question in `design/references/session-schema.md` section "Merge-strategy question". **If the scan finds nothing**: no question needed — treat this as a fresh start into an empty project regardless of the remediation plan's existence.

Run `design/references/session-schema.md` section "Resumable-plan detection procedure" using the approved document's path as `{document}` to produce the **Previous plan path**, if the user chooses to resume.

Then follow `design/references/session-schema.md` section "Implementation-planner → architecture-implementer spawn sequence" to spawn `implementation-planner` and, once its plan is confirmed, `architecture-implementer`, passing these six inputs:
- The path to the approved document
- **Existing project summary** — translated into the agent's expected strategy label: `Fresh start (empty project)` if the scan found nothing; `Merge` if the user chose (a); `Fresh start (existing project)` if the user chose (b); `User-described layout` if the user chose (c)
- **Technology stack** — from the architecture document's Technology Decisions section (section 5)
- **Agent tools** (optional) — `session.json`'s `"agentTools"` array, if present and non-empty (this key is written once at Stage 5 during `/architecture-designer:design` and is not re-derived here, but still valid and worth passing through unless the revision replaced the entire stack)
- **Remediation plan path** — the full path to the `{yyyymmdd}-{topic}-remediation.md` file saved in step 4e (present whenever step 4e ran — i.e. every case except option (b) alone, which skips it entirely; omit this input for that case) — see `design/references/session-schema.md` section "Finding the applicable remediation plan" for why its presence must not override the scan-based strategy label
- **Previous plan path** — the resumed plan's `path`, if the user chose to continue (omit otherwise)

If the user says no: let them know they can run `/architecture-designer:implement` at any time to generate the skeleton from this approved document later.

Either way, record `progress.lastCompletedStep = "step13"` per `design/references/session-schema.md` section "Recording `progress.lastCompletedStep`" — this revision pipeline pass is complete.

---

## Path resolution

`<scripts_dir>` = the `scripts/` directory of the architecture-designer plugin, two levels above this file (`../../scripts/`). Resolve it from the absolute path of this SKILL.md at runtime.

`design/references/...` = the sibling `design/` skill's `references/` directory, one level up from this file then into `design/references/` (e.g. `../design/references/session-schema.md`). Resolve it the same way, from the absolute path of this SKILL.md at runtime.

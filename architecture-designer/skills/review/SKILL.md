---
name: review
description: This skill should be used when the user wants to review or revise an existing architecture — says "review my architecture", "audit my architecture", "update my architecture document", "revise the architecture", "architecture drift", "compare design vs implementation", or "check if my code matches my design", or wants to compare their architecture document against their current codebase. Also trigger when a new feature or requirement change means the architecture document needs updating — including adding/changing an API contract, endpoint, business rule, DTO, or other Low-Level Design artifact on a system that already has a document — or to produce a first architecture document for an existing, undocumented codebase (reconstructing from real code is this skill's job even with no document yet). Not for a brand-new system with no codebase yet — use the design skill for that.
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Agent", "WebSearch"]
---

# Architecture Designer — Review and Revision Workflow

This skill reviews an existing architecture (from a document, the codebase, or both), presents findings, and guides the
user through a structured revision process that creates a new versioned document.

**Scripts directory:** see "Path resolution" at the bottom of this file.

**References directory:** this skill has none of its own — every `design/references/...` pointer below resolves into the
sibling `design` skill's `references/` directory, per "Path resolution" at the bottom of this file.

---

## Before starting — load and validate session context

Check for `docs/architecture-designer/session.json`:

- **If the file exists**: read it in full, then run `python3 <scripts_dir>/validate-session.py` and show its output —
  this is a hard gate; do not proceed to Step 1 until it reports `SESSION CHECK PASSED`. See
  `design/references/session-schema.md` section "Session completeness gate" for what the script checks and how to
  resolve a failure (e.g. running `/architecture-designer:design` to fill the gaps). The session contents are the
  original requirements baseline the architecture-reviewer and any revision agents review against.

- **Also check for an interrupted revision in progress**: if `session.json` contains a `progress` key whose
  `lastCompletedStep` is anything before `step11` (a document save) **and** its `owner` is `"review"`, a previous
  *revision* session died mid-pipeline. Apply `design/references/session-schema.md` section "Resuming Steps 6a–13 via
  `progress`" to resume Step 4's revision flow from where it left off instead of restarting Step 4a — including
  validating any recorded `reviewCycles` verdicts' hashes and checking `docs/architecture-designer/last-review.md` for
  an unresolved fixer cycle. If `progress.owner` is instead `"design"` (or absent) with `lastCompletedStep` before
  `step11`, this is an *original* design pipeline that never finished — not a review revision — since `review` never
  touches `progress` before step 4b and no revision document was ever produced to revise. Do not attempt to resume Step
  4 from this state (there is no revision scope, no document to list in Step 2a). Instead tell the user: "It looks like
  a previous `/architecture-designer:design` session didn't finish (no architecture document was ever saved). Run
  `/architecture-designer:design` to complete it before reviewing." and stop here rather than proceeding to Step 1.

- **If the file does not exist**: this gate only applies when `session.json` exists — proceed without session context.
  Inform the user: "No session.json found — I won't have the original confirmed requirements on hand. The review will
  rely on the document and/or codebase alone. Sharing the original requirements now will improve the review quality."

**Check for an existing remediation plan**: if `session.json` contains a `"remediationPlans"` array, run
`design/references/session-schema.md` section "Pre-review remediation-plan carry-forward check" — it scans every entry
(not just the latest), may prompt to carry one plan's deferred items into this session's revision scope (step 4a), and
reports back one of: nothing to carry forward, everything already resolved, or a specific plan's deferred items to fold
in.

**Check for prior review history**: if `session.json` contains a `"reviewHistory"` array, briefly list its entries
(date, source, outcome, one-line summary) before Step 1's question — e.g. "A previous review on 2026-07-20 (codebase
scan) found drift in the payment service and was declined." This is context, not a gate: do not re-present the full old
report, and do not skip re-checking anything this session's own scan would otherwise cover.

---

## Step 1 — Determine review source

Ask the user:

> "What would you like me to review? I can:
> **(a)** Review your existing architecture document in `docs/architecture-designer/architecture/`
> **(b)** Scan your current codebase and reconstruct the actual architecture — useful both for auditing a system you
> already understand and for producing a first architecture document for a project that was never formally documented
> **(c)** Do both — compare the document against the codebase to find drift
>
> Which would you prefer?"

---

## Step 2a — Document-based review

If the user chose (a) or (c):

1. List all files in `docs/architecture-designer/architecture/` sorted by filename (newest date first). If the directory
   doesn't exist or contains no files, tell the user no architecture document was found and offer to fall back to option
   (b) (codebase reconstruction) instead — do not proceed with an empty selection. Otherwise, present the list to the
   user and ask which document to review, or confirm using the latest.
2. Read the selected document.
3. Ask: **"What is your current goal for this review? Has anything changed since this document was written? (New
   requirements, new constraints, team changes, performance issues, etc.)"**
4. Spawn the `architecture-designer:architecture-reviewer` agent. Pass it:
    - The full contents of the architecture document
    - The original requirements context — the contents of `docs/architecture-designer/session.json` read above, per
      `design/references/session-schema.md` section "Requirements-summary scope for sub-agent spawns" (so, among other
      things, a decentralized project's Web3 dimension can actually fire on this review pass rather than silently
      reading as not-applicable). If session.json was absent (the only case reaching this step without it, since an
      incomplete file is blocked by the gate above), use the document's own Requirements Summary section as the baseline
      instead.
    - The user's current context/goals
    - Any new requirements or constraints the user described Let the agent assess: quality, consistency, completeness,
      and fit with current needs.
5. Present the reviewer's findings to the user (see Step 3 for how to flag Dimension 6 findings specifically).

---

## Step 2b — Codebase-based review

If the user chose (b) or (c):

Spawn the `architecture-designer:codebase-reconstructor` agent with: the working directory, the user's current
context/goals from Step 1, and the requirements summary from `docs/architecture-designer/session.json` if it exists (per
`references/session-schema.md` section "Requirements-summary scope for sub-agent spawns"). It exhaustively scans project
structure, services/modules, dependencies, entry points/API surface, database schema, and infrastructure — read its own
"What to implement"-equivalent checklist in `agents/codebase-reconstructor.md` for the exact scope; this step does not
restate it. Wait for its **Reconstructed Architecture Summary**, including its "Ambiguities / low-confidence findings"
and "Unclassified files" sections — surface both to the user alongside the summary itself in Step 3 below, rather than
only the clean parts.

If the user also has a document (option c): compare the reconstructed summary against the document and produce a **Drift
Report**:

**File path requirement**: Every claim in the Drift Report must cite its evidence source. For code-based claims, include
the specific file path where the evidence was found (e.g., "`src/auth/middleware.ts` uses JWT but document section 6
specifies OAuth2"). For document-based claims, cite the document section (e.g., "section 8 Database Design"). A claim
without a source reference must not be written.

- Components in the document but absent from the code
- Components in the code but absent from the document
- Naming inconsistencies
- Technology substitutions (e.g., document says Redis, code uses Memcached)
- Structural differences (e.g., document shows microservices, code is a monolith)

This comparison is only as complete as its two inputs: the document review's 8 dimensions (Step 2a) and
`codebase-reconstructor`'s exhaustive scan (above) are both designed to be complete on their own side, so a drift
finding here reflects a genuine mismatch between them, not a gap in either input's own coverage.

---

## Step 3 — Present findings and ask for revision

Present the review findings (architecture review report, drift report, or both) to the user. **For option (b) alone**
(no document was ever reviewed in this session — Step 1 chose codebase reconstruction only): there is no architecture
review report or drift report to present, since both require a document (per Steps 2a/2b); present the Reconstructed
Architecture Summary directly instead, and ask whether the user wants to formalize it into a first architecture document
(step 4f's no-prior-document path handles this).

Otherwise, if the architecture review report includes a Dimension 6 ("Document and current-intent alignment") finding —
one that treats the document as outdated relative to what the user described as their current goal — call it out
distinctly from the ordinary diagram findings: it means the document's own prose, not just the diagrams, needs updating
in step 4f, and it should factor into the revision scope discussed in step 4a. Then ask:

> **"Based on these findings, would you like to revise the architecture? I can update the affected diagrams, create a
new versioned document, and optionally regenerate the implementation skeleton."**

**Persist this review to history (required, regardless of the answer)**: save whatever was presented above (the
architecture review report, the Drift Report, or the Reconstructed Architecture Summary for option (b) alone) to
`docs/architecture-designer/review/{yyyymmdd}-{topic}-review.md` (create the `review/` directory if it doesn't exist;
apply the same `-2`/`-3` collision-avoidance check as an architecture document). Then append
`{ "date": "<current ISO timestamp>", "source": "document" | "codebase" | "drift", "outcome": "declined" | "revised",
"summary": "<1-2 sentence summary of the key findings>", "path": "<absolute path of the saved file>" }` to
`session.json`'s top-level `"reviewHistory"` array (create it if absent) — `source` matches whichever of Step 1's
options (a)/ (b)/ (c) ran, and `outcome` is set once the user answers the question above. This is what lets a future
`/architecture-designer:review` session know a finding was already surfaced once, rather than re-discovering the same
drift from zero every time — see `design/references/session-schema.md`'s `reviewHistory` entry.

If the user does not want to revise (or, for option (b) alone, does not want to formalize the summary into a document):
acknowledge the review is complete. They can run this skill again at any time.

---

## Step 4 — Revision process

If the user agrees to revise (or, for option (b) alone, agrees to formalize):

### 4a. Gather revision scope

**Checkpoint partial answers incrementally**: after each individual answer the user gives below (not just once this step
is fully confirmed), upsert `session.json`'s `pending` key per `design/references/session-schema.md` section "Mid-stage
pending answers", using `"review-4a"` as the stage id. Delete `pending` once this step's scope is confirmed and 4b
begins.

**Read `design/references/revision-triggers.md` before asking below** — it is the canonical, shared trigger table (also
consulted by `design/SKILL.md` Step 9) mapping "if X changed, re-run Y" to the guide to read and the `session.json`
key (s) to update. Rows A–J apply here the same as in first-time design; rows K/L are specific to `review` since they
depend on Low-Level Design and Test Strategy already existing.

Ask:

- Which findings should be addressed in this revision? (Include any deferred items carried forward from the pre-Step-1
  remediation-plan check, if the user opted in.) For option (b) alone, there are no findings yet — skip this question;
  the Reconstructed Architecture Summary from Step 2b is the starting point for 4b to diagram, not a set of findings to
  address.
- Are there new requirements that should be incorporated?
- Is this a minor revision (1.1) or a major redesign (2.0)? If no prior document exists (Step 1 option (b) alone, with
  nothing to revise), this question doesn't apply — see step 4f's no-prior-document fallback instead.
- For each row A–J in `revision-triggers.md`, does this revision match its trigger? Flag every match for 4b.
- Row G's ADR consequence: if it matches, also flag it for 4f's "Update Architecture Decision Records" step below.
- Row K: does this revision add, change, or remove an API endpoint, business rule, DTO, inter-service contract, or error
  condition? If so, flag it for the "Update Low-Level Design" step (4d.5) below — a diagram-only revision (e.g.
  relabeling a component) does not require this, but any change visible in a sequence/class/business-process diagram
  usually does.
- Row L: does this revision change an NFR, a capacity number, a resilience/rate-limiting decision, or a core feature? If
  so, flag it for the "Update Test Strategy" step (4d.6) below — any of these change a load-test target, a chaos-test
  scenario, or a UAT scenario that step derives.

### 4b. Update diagrams

**First touch of `progress` this revision pass**: if this is the first time this revision touches `session.json`'s
`progress` key, set `progress.owner = "review"` (overwrite in full — this is a new pipeline pass, distinct from whatever
`design` last left there) per `design/references/session-schema.md`'s `progress` paragraph and "Resuming Steps 6a–13 via
`progress`".

**Write each updated diagram to `diagrams.json` as soon as it's finished, not batched at 4d** — read the file fresh,
update or append that one diagram's entry, and write the whole file back (same incremental,
read-fresh-modify-write-whole discipline `design/SKILL.md` Stage 6d uses — see `design/references/diagrams-guide.md`
section "`diagrams.json` Schema"). A session that dies partway through a multi-diagram revision should not lose diagrams
already finished.

**For option (b) alone** (formalizing a Reconstructed Architecture Summary into a first document, nothing to "update"
yet): generate a fresh diagram set from that summary instead of editing an existing one — apply `design/SKILL.md` Stage
6d's diagram-type selection table and Stage 6a-6e's generation steps (database design, diagram rules, `diagrams.json`
schema) as if this were a first design session, using the reconstructed architecture pattern, tech stack, and components
as the input in place of stages 1–5. Then continue to 4c as normal.

Otherwise, based on the revision scope:

- For architecture changes: update the affected Mermaid diagrams (C4, sequence, deployment) — including that diagram's
  `description`/`details`/`rationale` fields when the code change makes the existing prose stale, not just the `code`
  field; `validate-diagrams.mjs` only checks these are non-blank, not that they still match a revised diagram.
  - If a Class Diagram exists and is affected, apply `design/SKILL.md` Stage 6d's design-principle and GoF-pattern
    passes before writing it back — read `design/references/design-principles-guide.md` and check the revised classes
    against SOLID, DRY, YAGNI, Tell Don't Ask, the Hollywood Principle, and the Law of Demeter, and read
    `design/references/design-patterns-guide.md` Part 2 to check whether a revised or newly-added class matches a named
    GoF pattern's signal, same as a first-time design session.
  - If the revision changes item (1)'s architecture pattern (Stage 5), also re-check
    `design/references/design-patterns-guide.md` Part 1 for the applicable POSA architectural pattern (s) and update the
    Stage 5 justification accordingly.
- For database changes: re-spawn the `architecture-designer:database-designer` agent with the same three inputs
  `design/SKILL.md` Stage 6a passes on first use — the updated requirements summary (per
  `design/references/session-schema.md` section "Requirements-summary scope for sub-agent spawns" — same scope and
  fallback as 4c below), the domain entities extracted from the (now updated) functional requirements, and the access
  patterns from the business processes — then validate with `architecture-designer:database-reviewer` (same
  requirements-summary scope). Apply `design/references/session-schema.md` section "Reviewer–fixer cycle procedure"
  step 0 (its own header already makes it unconditional) as soon as the report is received — type `database`. If the
  reviewer returns `DATABASE REVIEW FAILED`, continue with that section's steps 1–4 (binary verdict — cycle until
  `DATABASE REVIEW PASSED`): the fixer receives the review report, the database-designer output, the requirements
  summary (same scope), and the path to
  `docs/architecture-designer/diagrams.json`. It writes the corrected ERD and indexPlan directly into `diagrams.json` —
  except under the "option (b) alone" branch above, where that file doesn't exist yet at this point; per
  `agents/database-fixer.md`'s own conditional, it skips the write there and 4b's fresh-diagram-set generation embeds
  the correction when it builds the file — **and always returns the corrected schema, ERD, index plan, transaction and
  concurrency strategy (when present), and connection config as text — replace the database-designer output held in
  context with this corrected text; it is what gets embedded in the revised document (step 4f), not the original.**
  Once `DATABASE REVIEW PASSED` is reached, record
  `progress.lastCompletedStep = "step6a"` per
  `design/references/session-schema.md` section "Recording `progress.lastCompletedStep`" — mirroring `design/SKILL.md`
  Stage 6a's own write for exactly this label.
- For new features: apply `design/SKILL.md` Stage 6d's **Core feature coverage requirement** — every new functional
  requirement that represents a distinct user-facing feature (not a minor CRUD sub-step of a feature already covered)
  gets its own dedicated sequence diagram showing that feature's primary flow, including its failure path (`alt` block),
  appended as a new entry to `diagrams.json` — not merely a box added to an existing C4/use-case diagram. Adding new
  diagram *elements* to existing diagrams (a participant in a sequence diagram, a container in C4) is still correct for
  a feature that extends an already-covered flow; a genuinely new feature needs the dedicated diagram itself, the same
  bar `architecture-reviewer`'s dimension 3 checks in 4c below — get it right here rather than relying on that check to
  catch it.
- For removed components: remove the relevant elements
- For every row A–J that 4a flagged as matching: apply that row's action from `design/references/revision-triggers.md`
  exactly (same guide, same `session.json` key, same write mode). This skill is an authorized second writer of every key
  in that table except `description`'s and `domainModel`'s first pass — see `design/references/session-schema.md`
  section "Single writer per key". Two rows need a review-specific addition beyond the table's own text: row E (Web3)
  also updates the architecture diagram's on-chain/off-chain boundary (dimension 3) to match; row F (offline-first) and
  row I (domain model) both re-spawn `architecture-designer:database-designer` per the database-changes bullet above, so
  the schema reflects the updated sync columns or aggregate boundaries respectively.

Once every diagram this step touches — including the option (b) alone path above — has been written to `diagrams.json`,
record `progress.lastCompletedStep = "step6d"` per `design/references/session-schema.md` section "Recording
`progress.lastCompletedStep`" — mirroring `design/SKILL.md` Stage 6e's final-integrity-check write for exactly this
label. This write matters beyond bookkeeping: it is what makes the "Before starting — load and validate session context"
gate's interrupted-revision detection reliable. Without it, a crash anywhere in 4a–4b leaves whatever
`lastCompletedStep` the *previous* pipeline pass left behind (often `step13`, well past `step11`) — and that gate's test
(`progress.owner == "review"` and `lastCompletedStep` before `step11`) would then read as "no revision in progress" and
silently fail to offer resume, even though 4b's diagram/database work is genuinely unfinished on disk.

### 4c. Architecture re-review

Spawn the `architecture-designer:architecture-reviewer` agent with:

- The requirements summary — read from `docs/architecture-designer/session.json` (per
  `design/references/session-schema.md` section "Requirements-summary scope for sub-agent spawns", reflecting whatever
  4b just wrote to `web3`/`offlineFirst`). If session.json is absent, use the previous document's Requirements Summary
  section. If both are absent (option (b) alone with no session.json — nothing to fall back to), use the Reconstructed
  Architecture Summary from Step 2b as the requirements baseline instead.
- The user's current context/goals and any new requirements or constraints gathered in step 4a — kept as its own item,
  separate from the requirements summary above, so the agent can tell it received current-intent context (its Dimension
  6 input) rather than folding it into the original baseline.
- All updated diagrams

Apply `design/references/session-schema.md` section "Reviewer–fixer cycle procedure" step 0 (its own header already
makes it unconditional) as soon as the report is received — type `architecture`.

If Critical or Major findings are returned: continue with that section's steps 1–4 (three-tier verdict): spawn
`architecture-designer:architecture-fixer` with the review report, `docs/architecture-designer/diagrams.json`, and the
requirements summary, then re-spawn the reviewer to verify per that section.

Once passed, record `progress.lastCompletedStep = "step7"` per `design/references/session-schema.md` section "Recording
`progress.lastCompletedStep`".

**Persona reviews (optional)**: mirrors `design/SKILL.md` Step 7b — ask the user whether they'd like an additional
Security-persona and/or Cost-persona pass, and if so spawn `architecture-designer:architecture-reviewer` again per
persona with the same augmented context that step defines. Same as the design flow: informational only, never gates
progress to 4d, and never written to `progress.reviewCycles`/`last-review.md`.

### 4d. Browser preview

1. **Confirm `diagrams.json` is current** — every diagram touched in 4b/4c was already written incrementally (per 4b's
   note and the reviewer–fixer cycle), so this is a final integrity check, not a write: confirm every diagram in the
   revision scope has a corresponding entry and no entry is partial, same as `design/SKILL.md` Stage 6e.
2. **Validate and preview**: follow `design/SKILL.md` Step 8 steps 2–4 exactly (`validate-diagrams.mjs` gate and
   `DEGRADED MODE` handling, then `find-port.py` and `preview-server.mjs`) — with one difference: if a preview server
   from a previous run in this session is already running, tell the user to refresh their browser instead of starting a
   new one. Record `progress.lastCompletedStep = "step8"` per `design/references/session-schema.md` section "Recording
   `progress.lastCompletedStep`".
3. **Visual rendering verification (optional, best-effort)**: follow `design/SKILL.md` Step 8.5 exactly (`SKIPPED` /
   `VISUAL CHECK PASSED` / `VISUAL CHECK FOUND OVERLAPS` handling) against the revised diagrams — same
   "informational, never blocking" treatment, not tracked in `progress`.
4. Ask: **"Does this revised architecture look correct to you?"** Once confirmed, record
   `progress.lastCompletedStep = "step9"`.

If further revisions are needed, repeat from step 4b.

### 4d.5. Update Low-Level Design

**Skip this step** if 4a found nothing that touches an API contract, business rule, DTO, inter-service contract, or
error condition — a revision scoped to diagrams, database, infrastructure, or NFRs alone leaves the existing `lld` key
valid as-is. **For option (b) alone** where `session.json` has no `lld` key yet: build it fresh instead of updating it,
by following `design/SKILL.md` Step 10 in full against the newly-formalized diagrams, then continue below.

Otherwise, once the revised diagrams are confirmed (end of 4d), read `design/references/lld-guide.md` and update the
affected Low-Level Design groups to match: new or changed endpoints visible in the revised sequence diagrams get
new/updated API contract entries; new or changed business rules, DTOs, inter-service contracts, and error-catalog
entries follow the same "derive from the diagrams, never invent" discipline as `design/SKILL.md` Step 10.

For new or changed business rules, also apply `design/SKILL.md` Step 10's checks, in order, and check the revised rule
against all of them before presenting it:

1. `design/references/critical-thinking-guide.md` section "Applying this to Step 10 group (2)" — name the invariant and
   business reason before refining how the rule is written; a changed rule with no traceable reason back to the revised
   requirement is a YAGNI candidate.
2. `design/references/design-principles-guide.md`'s DRY, YAGNI, and Tell-Don't-Ask sections.
3. `design/references/clean-code-guide.md`'s "Functional core, imperative shell" section.
4. `design/references/design-patterns-guide.md` Part 2 — naming a pattern only where a real signal is present.
5. For a rule whose `Post-conditions` list two or more writes, `design/references/transaction-guide.md` — stating the
   transaction boundary or rewriting the rule as a Saga per that guide's section 4.

If the revision changed which entities are high-contention (a new read-then-write path added, or
an existing one removed), also re-spawn `architecture-designer:database-designer`'s transaction-and-concurrency-strategy
check (per the database-changes bullet in 4b above) rather than leaving a stale strategy in place. Present the updated
groups, confirm, then write them into `session.json`'s `lld` key the same way Step 10 does
(read-fresh-modify-write-whole, adding any newly-confirmed group to `lld.confirmedGroups`) — do not touch groups 4a
didn't flag.

Record `progress.lastCompletedStep = "step10"` per `design/references/session-schema.md` section "Recording
`progress.lastCompletedStep`" once done.

### 4d.6. Update Test Strategy

**Skip this step** if 4a found no change to an NFR, a capacity number, a resilience/rate-limiting decision, or a core
feature — a revision scoped to diagrams, database, infrastructure, or a decision with no bearing on any of those leaves
the existing `testStrategy` key valid as-is. **For option (b) alone** where `session.json` has no `testStrategy` key
yet: build it fresh instead of updating it, by following `design/SKILL.md` Step 10b in full against the newly-formalized
design, then continue below.

Otherwise, read `design/references/test-strategy-guide.md` and update the affected parts to match: a changed
Performance/Scalability Quality Attribute Scenario or capacity number updates the load-test targets (part 2); a changed
resilience/rate-limiting decision updates the chaos-test scenarios (part 3) and/or security checklist (part 4); a
changed core feature updates the UAT scenario list (part 5) and the test-pyramid's end-to-end row (part 1). Present the
updated plan, confirm, then overwrite `session.json`'s `testStrategy` key in full (this skill is an authorized second
writer of this key for exactly this case, same pattern as `lld` above).

Record `progress.lastCompletedStep = "step10b"` per `design/references/session-schema.md` section "Recording
`progress.lastCompletedStep`" once done.

### 4e. Save remediation plan

**Skip this step entirely for option (b) alone**: there are no findings to remediate — a first-time formalization has
nothing to reconcile against, so no remediation plan is created. Proceed straight to 4f.

Otherwise, once the user confirms the revised architecture looks correct, persist the confirmed findings as a living
remediation plan.

**Determine the revised document's future path first — do not save the document yet (that is step 4f)**: this plan's
`document` field must point at the *revised* document, not the pre-revision one read in Step 2a, since that is what
`design/references/session-schema.md` section "Finding the applicable remediation plan" will match against in every
future session. Work out the exact filename step 4f is about to save to —
`docs/architecture-designer/architecture/{yyyymmdd}-{topic}.md`, applying the same `-2`/`-3` collision-avoidance check
4f uses — now, so this plan can reference it correctly. Step 4f must then save to this exact same filename rather than
recomputing it independently, so the two never disagree.

Save the remediation plan to:

```
docs/architecture-designer/plan/{yyyymmdd}-{topic}-remediation.md
```

- `{yyyymmdd}` — today's date, generated with JavaScript `new Date()` (never a shell command).
- `{topic}` — the topic slug from the architecture document filename (e.g., `20260706-inventory-app.md` →
  `inventory-app`); if no prior document exists (Step 1 option (b) alone), use `session.json`'s `project` field instead,
  or ask the user for a slug if `session.json` doesn't exist either.
- **Collision avoidance**: if the file already exists, append `-2`, `-3`, etc. until the name is unique
  (`{yyyymmdd}-{topic}-remediation-2.md`).

Create the `docs/architecture-designer/plan/` directory if it doesn't exist.

**Plan format**: follow `design/references/remediation-plan-guide.md` exactly — the checkbox-per-finding rule, mandatory
source path, and the two-phase suffix progression for `[x]` items. The "Architecture document" metadata-table row is the
revised document's path determined above, not the pre-revision document.

After saving, append
`{ "path": "<absolute path of this file>", "document": "<the revised document's path determined above — the one step 4f is about to save to>", "supersedes": "<previous remediation plan path, if this plan carried its deferred items forward per the pre-Step-1 check — otherwise null>", "createdAt": "<current ISO timestamp>" }`
to `session.json`'s top-level `"remediationPlans"` array (create it if absent). If `supersedes` is non-null, also make
the terminal write described in `design/references/session-schema.md` section "Superseding a remediation plan" to close
out the old plan file. Note the path for passing to the implementer in step 4h.

### 4f. Save the revised document

Once the user confirms the revision, save to `docs/architecture-designer/architecture/{yyyymmdd}-{topic}.md`. **If step
4e ran** (every case except option (b) alone, which skips 4e entirely): use the exact filename 4e already determined and
committed to in the remediation plan's `document` field — do not recompute the collision check independently here. **If
step 4e was skipped** (option (b) alone): determine the filename here for the first time, applying the `-2`/`-3`
collision-avoidance check directly, since there is no remediation plan to have pre-committed it.

**Important**: never overwrite the previous document. Always create a new file. The history must remain intact.

The metadata table:

```markdown
| Date       | Version   | Status | Reason            | Previous Document   |
|------------|-----------|--------|-------------------|---------------------|
| {dd-mmm-yyyy} | {version} | Draft  | {revision reason} | {previous filename} |
```

**If no prior document exists** (Step 1 option (b) alone, with no document ever reviewed in this session): this save is
the *first* document for the project, not a revision — treat it the same as `design/SKILL.md` Step 11: `Version` is
`1.0`, `Previous Document` is `-`, and `Reason` describes why this document is being created now (e.g., "Initial
document generated from codebase reconstruction").

Otherwise (a prior document was reviewed in Step 2a):

- `Version`: increment from the previous document. Use `1.1`, `1.2`, ... for minor changes; `2.0` for major redesigns.
  Ask the user if unsure.
- `Reason`: fill with the reason for this revision (e.g., "Added real-time notifications feature", "Migrated from
  monolith to microservices", "Performance improvements for 10× user growth")
- `Previous Document`: the filename of the document being revised (e.g., `20260705-inventory-app.md`)
- `Status`: always starts as `Draft`

Generate timestamps using JavaScript `Date`, not shell commands.

After saving, append `{ "path": "<absolute path of the saved file>", "createdAt": "<current ISO timestamp>" }` to
`session.json`'s top-level `"documents"` array (create it if absent; backfill `schemaVersion`/`project`/`description` at
the same time if the file predates them, per the tolerant-read rule in `design/references/session-schema.md`). This lets
`/architecture-designer:implement` find the latest approved document — the last entry's `path` — without asking.

The document body follows the same structure as the design workflow (all sections, all diagrams), including section 2
(Core Features — re-derive if 4a flagged a functional-requirement change, so a feature added or removed by this revision
is reflected), section 8 (Database Design) — same rule as `design/SKILL.md` Step 11: the prose (schema, index table,
connection config, migration strategy) comes from `progress.reviewCycles.database.approvedOutput`, but the `erDiagram`
block itself is copied verbatim from its entry in `diagrams.json` (already corrected by 4b, if a database revision ran),
never re-derived independently from `approvedOutput` — section 11 (Low-Level Design) pulled from `session.json`'s `lld`
key — the same key the "Update Low-Level Design" step above just confirmed is current, section 16 (Cost Estimation) from
`stage5.costEstimate`, section 17 (Test Strategy) from `testStrategy`, and section 18 (Architecture Decision Records)
from `adrs` — see `design/references/document-template.md`. This is a standalone document, not a diff — someone reading
it without the previous version should have complete context.

**Update Architecture Decision Records** (required immediately after saving, same as `design/SKILL.md` Step 11): read
`design/references/adr-guide.md`. For each decision this revision changed that already has an ADR (per 4a's scope):
write a new ADR file superseding the old one and make the terminal `Superseded by ADR-{NNNN}` write to the old file, per
that guide's "Revising ADRs" procedure. For each newly-qualifying decision with no prior ADR: write a fresh one, per
"Generating ADRs". Append every new entry to `session.json`'s top-level `adrs` array (this skill is an authorized second
appender for this key, mirroring the `documents` append pattern).

Record `progress.lastCompletedStep = "step11"` per `design/references/session-schema.md` section "Recording
`progress.lastCompletedStep`".

### 4g. Document review

Spawn the `architecture-designer:document-reviewer` agent with the path to the new document, the requirements summary
(same scope as 4c — every relevant `session.json` top-level key, including `web3` when present), and the expected
filename. Apply `design/references/session-schema.md` section "Reviewer–fixer cycle procedure" step 0 (its own header
already makes it unconditional) as soon as the verdict is received — type `document`.

If DOCUMENT REVIEW FAILED: continue with that section's steps 1–4: spawn `architecture-designer:document-fixer` with the
document path, the review report, the requirements summary, and the path to `docs/architecture-designer/diagrams.json`.
Rename the file first if the fixer's log says it must be renamed (F6), then re-spawn `document-reviewer` and verify
(binary verdict — cycle until DOCUMENT REVIEW PASSED).

Then update `Status` to `Approved`. Record `progress.lastCompletedStep = "step12"` per
`design/references/session-schema.md` section "Recording `progress.lastCompletedStep`".

### 4h. Implementation offer

After approval:

> **"The revised architecture document is approved. Would you like me to regenerate the project skeleton based on the
updated architecture?"**

If yes: scan the working directory for signs of an existing project, per `design/references/session-schema.md` section
"Existing-project scan categories". **If files already exist**: summarize what was found and ask the question in
`design/references/session-schema.md` section "Merge-strategy question". **If the scan finds nothing**: no question
needed — treat this as a fresh start into an empty project regardless of the remediation plan's existence.

Run `design/references/session-schema.md` section "Resumable-plan detection procedure" using the approved document's
path as `{document}` to produce the **Previous plan path**, if the user chooses to resume.

Then follow `design/references/session-schema.md` section "Implementation-planner → architecture-implementer spawn
sequence" to spawn `architecture-designer:implementation-planner` and, once its plan is confirmed,
`architecture-designer:architecture-implementer`, passing these six inputs:

- The path to the approved document
- **Existing project summary** — translated into the agent's expected strategy label: `Fresh start (empty project)` if
  the scan found nothing; `Merge` if the user chose (a); `Fresh start (existing project)` if the user chose (b);
  `User-described layout` if the user chose (c)
- **Technology stack** — from the architecture document's Technology Decisions section (section 6)
- **Agent tools** (optional) — if this revision touched the technology stack (per 4a's Stage-5-change question above),
  re-run `design/references/agent-tools.md`'s matching procedure against the revised stack now and pass that
  freshly-computed result to the agent for this spawn — do not pass through a stale match set from before the revision.
  `agentTools` in `session.json` is written only by `design/SKILL.md` (per `design/references/session-schema.md`
  section "Single writer per key"), so this fresh result is used for this spawn only and is not written back to
  `session.json`. If the stack was untouched this revision, pass through the existing `"agentTools"` array as-is (if
  present and non-empty).
- **Remediation plan path** — the full path to the `{yyyymmdd}-{topic}-remediation.md` file saved in step 4e (present
  whenever step 4e ran — i.e. every case except option (b) alone, which skips it entirely; omit this input for that
  case) — see `design/references/session-schema.md` section "Finding the applicable remediation plan" for why its
  presence must not override the scan-based strategy label
- **Previous plan path** — the resumed plan's `path`, if the user chose to continue (omit otherwise)

If the user says no: let them know they can run `/architecture-designer:implement` at any time to generate the skeleton
from this approved document later.

**If the user said yes**: the spawn sequence above includes its own step 5, which runs the
`implementation-reviewer`/`implementation-fixer` cycle — do not consider implementation finished, and do not tell the
user so, until that cycle's exit condition is met (`IMPLEMENTATION REVIEW PASSED`, or its 3-cycle cap reached).
`architecture-implementer` reporting `Status: Complete` is that agent's own self-report, not this cycle's exit
condition — see `design/references/session-schema.md` section "Implementation reviewer–fixer cycle" for what "done"
actually means here. Once that cycle's exit condition is met, give the user the same post-implementation wrap-up
`../implement/SKILL.md` Step 5 gives (opening the plan file, `.env` setup, running the setup command, starting the dev
server, testing the primary endpoint, committing the skeleton, and the Web3/offline-first pre-deployment reminders when
applicable) — this revision
pipeline reached the same finished state `implement/SKILL.md` reaches, and the user needs the same next steps regardless
of which skill got them there.

Either way, record `progress.lastCompletedStep = "step13"` per `design/references/session-schema.md` section "Recording
`progress.lastCompletedStep`" — this revision pipeline pass is complete.

---

## Path resolution

`<scripts_dir>` = the `scripts/` directory of the architecture-designer plugin, two levels above this file
(`../../scripts/`). Resolve it from the absolute path of this SKILL.md at runtime.

`design/references/...` = the sibling `design/` skill's `references/` directory, one level up from this file then into
`design/references/` (e.g. `../design/references/session-schema.md`). Resolve it the same way, from the absolute path of
this SKILL.md at runtime.

---
name: design
description: This skill should be used when the user wants to design a new application's architecture or infrastructure — says "design my architecture", "help me plan the architecture", "create architecture diagrams", "I need to plan a new system", or is starting a new project and needs a structured design process. Also trigger when the user mentions HLD, LLD, API contracts, or system design.
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Agent", "WebSearch"]
---

# Architecture Designer — Main Design Workflow

This skill guides the user through a six-stage design process plus seven post-design steps (architecture review, browser preview, user confirmation, low-level design, document save, document review, implementation offer), ending with browser-rendered Mermaid diagrams, low-level design artifacts, a reviewed and approved document, and an optional code skeleton.

Always use this skill for new architecture design, even if the user has already started describing their system in the conversation — do not skip straight to diagram generation or freeform advice.

**Scripts directory:** `../../scripts/` relative to this SKILL.md — referred to as `<scripts_dir>` throughout this file. Resolve it at runtime from this SKILL.md's absolute path.

---

## How to run this workflow

**Before starting — check for an existing session**: look for `docs/architecture-designer/session.json`. If it exists, read it and ask the user:

> "I found an existing design session for **[project name from the file, or 'a previous project' if unnamed]** — [description from the file, or omit this clause if unset]. Would you like to continue where we left off, or start a new design from scratch?"

If continuing: brief the user on where the previous session left off and resume from the first incomplete stage. Once stage1–5 are confirmed (the "Session completeness gate" precondition — stage6b/6c are not required, since Stage 6a can already have progressed before either is confirmed), also apply `references/session-schema.md` section "Resuming Steps 6a–13 via `progress`" — a session that died anywhere from Stage 6a through Step 13 should resume there, not restart the whole pipeline, and any `pending` key found means the previous session died mid-stage within 1–6c (same section covers this). If starting fresh: delete `docs/architecture-designer/session.json` (and `docs/architecture-designer/diagrams.json` and `docs/architecture-designer/last-review.md` if present) first.

**Checkpoint partial answers as you go**: within any of Stages 1–6c, after each individual answer the user gives (not just at the stage's final confirmation), upsert `session.json`'s `pending` key per `references/session-schema.md` section "Mid-stage pending answers" — this is what lets a session resume mid-stage instead of only at stage boundaries. Delete `pending` in the same write that records the stage's real confirmed key.

**Legacy-session backfill check**: run now, and again immediately before the Stage 6 gate below — see `references/session-schema.md` section "Legacy-session backfill check" for the exact trigger and procedure. Skipping this leaves the Stage 6 completeness gate permanently unpassable for that session.

Work through Stages 1–6 in order, then Steps 7–13. At the end of each stage, summarize the user's answers and ask:
> "Does this summary look correct? Shall we move to the next stage?"

Do not proceed until confirmed. After each confirmation, persist the stage summary to `docs/architecture-designer/session.json` (create `docs/architecture-designer/` if needed) — write the exact text the user confirmed, not a paraphrase, since sub-agents work from this file directly and cannot access conversation history.

**Read `references/session-schema.md` before writing to or reading anything beyond the stage keys below** — it is the canonical schema: fixed top-level keys, the array-of-objects shape for `documents`/`remediationPlans`/`implementationPlans`, which keys are guaranteed present, link resolution between arrays, and the single-writer-per-key / no-CAS write discipline every reader and writer must follow.

**`description` is required**: write `schemaVersion: 2`, `project`, and `description` together with `stage1` at the first session.json write below — see `references/session-schema.md` for its two valid sources (user-written vs. auto-generated) and `references/discovery-questions.md` Stage 1 for surfacing an auto-drafted version for approval. Do not proceed to Stage 2 with it empty.

---

## Stage 1 — Requirements Gathering

Goal: understand what the application must do and why it exists.

Ask the Stage 1 questions in `references/discovery-questions.md` (combine them into a conversational flow rather than a rigid checklist, but cover all of them), including the description question (write-your-own vs. auto-generate — see that reference for how to surface the drafted text). Summarize answers, confirm, then proceed.

Once confirmed, write the first `docs/architecture-designer/session.json`: `stage1`, plus the required top-level `schemaVersion: 2`, `project` (a short slug derived from the application name or purpose), and `description` (see "`description` is required" above). All three are written this once, at this point in the workflow — do not defer them to Step 11.

---

## Stage 2 — Requirements Analysis

Goal: separate functional from non-functional requirements.

Ask the Stage 2 questions in `references/discovery-questions.md`.

> **Compliance grounding rule**: When the user names a compliance framework, record it as a stated requirement — do not assert specific technical controls from memory (e.g., "GDPR requires X-day retention"). Regulatory specifics vary by jurisdiction and change over time; model-generated compliance claims are expensive to correct. Mark every compliance-specific control in the document with **"⚠ Needs legal/compliance validation"** and defer exact requirements to the user's legal team.

> **Web3 / decentralized detection**: if the application is described as decentralized, blockchain-based, or on-chain, note this now — Stage 5 will read `references/web3-guide.md` and work through its additional questions before the stack is finalized. The same applies if this isn't apparent until Stage 5 names a distributed-ledger platform directly.

Summarize as two lists (functional and non-functional), confirm, then proceed.

---

## Stage 3 — Feasibility Study and Constraints

Goal: identify real-world constraints that will shape technical decisions.

Ask the Stage 3 questions in `references/discovery-questions.md`. Summarize constraints, confirm, then proceed.

---

## Stage 4 — Capacity Planning

Goal: produce concrete numbers that will drive infrastructure sizing and technology choices.

Ask the Stage 4 questions in `references/discovery-questions.md`. Summarize with explicit numbers (estimates are fine — label them as estimates), confirm, then proceed.

**Number discipline**: Every figure in the confirmed capacity summary must originate from the user's answers or be explicitly derived from those answers — show the arithmetic (e.g., "10,000 daily active users ÷ 86,400 s × 3× peak factor ≈ 0.35 req/s baseline"). Do not cite database or infrastructure performance benchmarks from memory (e.g., "PostgreSQL handles 10,000 TPS") as justification — those figures are not grounded in this project's specific usage and create false precision. When the user cannot provide a number, derive a reasoned estimate together and label it **"estimate — validate at launch"**.

---

## Stage 5 — Technology and Architecture Pattern Selection

Goal: recommend a specific, justified technology stack.

**Read `references/tech-stacks.md` before making recommendations.** It contains concrete options organized by architecture pattern, scale tier, team size, cloud provider, database type, auth approach, and frontend, plus the citation pattern for tracing each choice back to stages 1–4 (section "How to justify recommendations in the architecture document") — use it to ground suggestions in real technology names rather than abstract categories.

Based on everything gathered in stages 1–4, propose and justify, in order: **(1) architecture pattern** (monolith/modular monolith/microservices/serverless/event-driven — a modular monolith is almost always right for small, early-stage teams); **(2) backend language and framework**, named specifically (e.g. "Fastify 5", not "Node.js"); **(3) frontend** framework and version, if applicable; **(4) database engine(s)** — a high-level call; the database-designer agent designs the full schema in Stage 6; **(5) infrastructure provider and key managed services**, named specifically (e.g. "AWS ECS Fargate", not "containers on AWS"); **(6) supporting services** (queue, cache, search, object storage) — only if the functional requirements need them; **(7) authentication approach**, justified by user roles, security requirements, and team capacity; **(8) observability strategy** — logging aggregator (e.g. ELK, Grafana Loki, Datadog, CloudWatch), metrics/dashboards, and distributed tracing (OpenTelemetry + Jaeger/Tempo) if multiple services or async flows are involved, scaled to what the system's actual operational maturity requires — a small monolith may need only structured logging and one dashboard; **(9) disaster recovery** — RPO/RTO derived from the Stage 2 availability NFR, backup strategy, failover approach; **(10) error handling and resilience strategy** — derived from the Stage 2 error-handling NFR: retry policy (backoff strategy, max attempts) for calls to external dependencies named in stages 1–4, a circuit breaker or equivalent for any dependency the NFR marked as must-not-fail-silently, timeout budgets for synchronous calls, and the graceful-degradation behavior (if any) for non-critical features when a dependency is down. Name a specific library/pattern per language (e.g. `opossum` for Node circuit breakers, `resilience4j` for Java, `Polly` for .NET) rather than describing the concept abstractly — scale to what the system actually needs: a monolith with no external dependencies may only need timeout budgets, not a full circuit breaker.

Every recommendation must cite a specific reason from stages 1–4. Present, discuss, adjust, confirm, then proceed.

**Version grounding**: every technology needs a specific version number. If WebSearch is available, verify the current stable release before writing it down; if not, write **"latest stable — verify at implementation time"** rather than a version from memory that may be stale. The same discipline applies to cloud managed-service names and compliance-specific *vendor/service* claims (e.g., whether a specific service holds a certification like SOC 2 or ISO 27001) — verify with WebSearch or label **"⚠ verify before relying"**. This is a distinct claim from the Stage 2 compliance-grounding rule above (which *regulatory controls* a framework requires, tagged **"⚠ Needs legal/compliance validation"**): a vendor certification is a checkable fact, a regulatory control is a legal interpretation — keep the two tags visually distinct rather than merging them.

**Optional — Web3 / decentralized track**: if Stage 1–2 flagged the application as decentralized/blockchain/on-chain, or a distributed-ledger platform is named as part of the stack above, read `references/web3-guide.md` in full before finalizing the stack — work through its seven invariant dimensions as additional questions, following its core rule on placeholders vs. asserted facts. Present the dimensions, discuss, confirm, then write the confirmed answers to `session.json`'s `"web3"` key (create it) at the same time as `"stage5"`. Skip this step entirely — do not create the key — for non-decentralized applications.

**Optional — agent tools for implementation**: independent of the Web3 track above and always worth checking, even for a decentralized stack (a matched tool answers "what's available," not "what was confirmed about the network" — see `references/agent-tools.md`'s core rule). Once the stack above is confirmed, read `references/agent-tools.md` and follow its procedure to check for MCP servers/Skills actually available in this environment that match the confirmed stack; propose any matches to the user as the `agentTools` addendum to the Stage 5 summary and let them drop any entry — this step never blocks Stage 5 confirmation. Write the confirmed list (or omit the key entirely if empty) to `session.json`'s `"agentTools"` at the same time as `"stage5"`.

---

## Stage 6 — Architecture and Infrastructure Design

**Session completeness gate**: re-run the legacy-session backfill check above once more here, immediately before this gate, in case stage1–5 only just became fully confirmed. Then run `python3 <scripts_dir>/validate-session.py` and show its output — this is a hard gate; do not proceed to 6a or any later step until it reports `SESSION CHECK PASSED`. See `references/session-schema.md` section "Session completeness gate" for what the script checks and how to resolve a failure. A missing top-level field on an otherwise-complete resumed session is the legacy-backfill case above, not a missing stage.

### 6a. Database design (delegate to sub-agent)

Spawn the `architecture-designer:database-designer` agent. Pass it the complete requirements summary (read from `docs/architecture-designer/session.json`, not from memory — per `references/session-schema.md` section "Requirements-summary scope for sub-agent spawns", so its Web3 step can fire when applicable, per `references/web3-guide.md`), the domain entities extracted from the functional requirements, and the access patterns from the business processes. Wait for it to return ERD, index plan, engine recommendation, and secure connection config.

Then spawn `architecture-designer:database-reviewer` with the full database-designer output and the requirements summary (same scope as above). **Regardless of verdict**, apply `references/session-schema.md` section "Reviewer–fixer cycle procedure" step 0 as soon as the report is received (records the verdict/cycle/approved output into `progress.reviewCycles.database` and `docs/architecture-designer/last-review.md`; this runs even on a clean first-try pass, not only on failure). If it returns `DATABASE REVIEW FAILED`, continue with that section's steps 1–4 (binary verdict — cycle until `DATABASE REVIEW PASSED`): spawn `architecture-designer:database-fixer`, which receives the review report, the database-designer output, the requirements summary (same scope), and the path to `docs/architecture-designer/diagrams.json`. It writes the corrected ERD and indexPlan directly into `diagrams.json` **and returns the corrected schema, ERD, index plan, and connection config as text** — replace the database-designer output held in context with this corrected text. Step 0 of the reviewer–fixer cycle procedure (triggered above) writes this same final text into `progress.reviewCycles.database.approvedOutput` — that key, not conversation memory, is the durable source Step 11 (section 7) and Stage 6d's ERD both read from.

**The database design embedded in the document (Step 11, section 7) and the diagram set must be the final approved version** — the fixer's corrected text if any cycle ran, otherwise the original output. Never fall back to the original after a fixer cycle has produced a correction; the two must never diverge.

The reviewer–fixer cycle procedure in `references/session-schema.md` records `progress.reviewCycles.database` and `docs/architecture-designer/last-review.md` unconditionally, on every report received — not only on a failing verdict; see that section's step 0. The first time this pass touches `progress` at all (i.e., before that first write), set `progress.owner = "design"` (overwrite in full — this is a new pipeline pass). Once `DATABASE REVIEW PASSED` is reached, record `progress.lastCompletedStep = "step6a"` per `references/session-schema.md` section "Recording `progress.lastCompletedStep`".

### 6b. Infrastructure as Code (IaC)

**Read `references/iac-guide.md` before making recommendations** — it has the decision tables, module structure, and the exact content to produce for each point below.

Based on the cloud provider chosen in Stage 5 and the infrastructure shape from the capacity plan, define and confirm, in order: **(1) tool selection** (Terraform, OpenTofu, Pulumi, AWS CDK, CloudFormation, or Bicep — never local state; see guide section 1 for decision rules); **(2) state backend**; **(3) module breakdown**, omitting modules for services not in scope; **(4) environment strategy** (default: directory-per-environment); **(5) drift detection**, matched to the team's operational maturity.

Present the plan, discuss open questions, adjust, and confirm before continuing.

After confirmation, append the confirmed decisions to `docs/architecture-designer/session.json` under `"stage6b"` (create or overwrite) — use the exact text the user confirmed, not a paraphrase.

---

### 6c. CI/CD Pipeline Design

**Read `references/cicd-guide.md` before making recommendations** — it has the decision tables, standard stage template, and the exact content to produce for each point below.

Based on where the code is hosted, the deployment target, and the architecture pattern, define and confirm, in order: **(1) platform selection** (see guide section 1 for decision rules; for Kubernetes targets, consider splitting CI platform for build and Argo CD/Flux for the CD leg); **(2) pipeline stages** with trigger and gate condition per stage, omitting what the project doesn't need; **(3) branching strategy** (default: GitHub Flow); **(4) environment promotion**, dev → staging → prod, with a manual approval gate on prod by default and a documented rollback procedure; **(5) secret injection** — prefer OIDC over long-lived keys, and confirm no secrets are hardcoded or committed; **(6) artifact management** — registry, tagging scheme (git SHA), retention policy.

Present the plan, discuss, adjust, and confirm before continuing.

After confirmation, append the confirmed decisions to `docs/architecture-designer/session.json` under `"stage6c"` (create or overwrite) — use the exact text the user confirmed, not a paraphrase.

---

### 6d. Diagram selection and generation

Select the Mermaid diagrams relevant to the project. **All diagrams are optional** — select only those that add clarity for this specific project.

**Write `docs/architecture-designer/diagrams.json`'s skeleton now**, before generating any diagram's code — `{ title, topic, generatedAt, diagrams: [] }` per `references/diagrams-guide.md` section "`diagrams.json` Schema". Then, for each selected diagram in turn: generate its code, apply the Mermaid compatibility and anti-overlap rules from that same reference immediately to this one diagram (not deferred to a later pass — see 6e below), then append its finished entry to `diagrams.json` and write the file (read-fresh-modify-append-write-whole). This way a session that dies partway through a large diagram set still has every diagram completed so far on disk, not just whatever fits in conversation context.

After generating, tell the user which were created and why, and which were skipped and why (e.g., "State diagram skipped — no entities with complex status lifecycles identified").

**Read `references/diagrams-guide.md` before generating any diagram** — it has the exact attribute format for ERD, full templates per diagram type, common mistakes, and anti-overlap rules. Don't rely on memory for Mermaid syntax.

**Available diagram types** (criteria for when to create each):

| Diagram          | Mermaid type                          | Create when                                  |
|------------------|---------------------------------------|----------------------------------------------|
| Use case         | `flowchart LR`                        | 2+ user roles with distinct feature sets     |
| Business process | `flowchart TD`                        | Complex workflow with 2+ decision branches   |
| ERD              | `erDiagram`                           | Any SQL database — always                    |
| Sequence         | `sequenceDiagram`                     | Always: auth flow + one per core feature (see requirement below) |
| Class            | `classDiagram`                        | Non-trivial domain model with business rules |
| State            | `stateDiagram-v2`                     | Any entity with 3+ lifecycle states          |
| C4 Context       | `C4Context`                           | Any external integration or 2+ user types    |
| C4 Container     | `C4Container`                         | 2+ deployable components                     |
| Deployment       | `flowchart TD` or `architecture-beta` | Cloud or multi-server deployment             |
| CI/CD pipeline   | `flowchart TD`                        | 2+ deployment environments or staged release |

**Core feature coverage requirement**: every functional requirement confirmed in Stage 2 that represents a distinct user-facing feature — not a minor CRUD sub-step of a feature already covered — must have its own dedicated sequence diagram showing that feature's primary flow, including its failure path (`alt` block). A single "primary transaction" diagram is not sufficient coverage once Stage 2 lists more than one distinct feature: cover them all, not just the most obvious one. Group trivial sub-actions of the same feature into that feature's one diagram rather than fragmenting into near-duplicate diagrams (e.g., "create order" and "cancel order" can share one diagram if both are simple branches of the same flow; "place order" and "process refund" cannot, since they are distinct features). `architecture-reviewer`'s requirements-traceability dimension raises a Major finding for any core feature with no dedicated diagram — see that agent's dimension 3.

**Production-ready requirement**: for any system targeting production workloads, the deployment/infrastructure diagram must show at least one observability sink (from Stage 5) and one DR component (replica, backup target, or cross-region failover) — `architecture-reviewer` raises a Major finding if either is absent.

**ERD special requirement**: mark indexed columns via `"idx"` attribute comments and include the index list table (from database-designer) immediately after the ERD block — see `references/diagrams-guide.md` for the exact format. Build the ERD from `session.json`'s `progress.reviewCycles.database.approvedOutput` (the final approved schema/ERD/index plan — see `references/session-schema.md` section "Persisting the database design output"), not from conversation memory — this is what makes Stage 6a's output durable if 6d runs in a resumed session where Stage 6a's conversation turn is gone.

### 6e. Mermaid compatibility and diagrams.json integrity check

`references/diagrams-guide.md` section "Mermaid v11.16 Compatibility Rules" and section "Preventing Node Overlap" (required syntax like `flowchart` not `graph`, `architecture-beta` icon slots, ELK layout, `align` directives, label length, C4 layout config) were already applied per-diagram in 6d as each one was generated and written. This step is a final integrity check, not a write: confirm every diagram selected in 6d has a corresponding entry in `docs/architecture-designer/diagrams.json` and that no entry is partial. This must be true before Step 7 — the architecture-fixer reads and updates the file in place during the review cycle and will fail if the file does not exist or is incomplete. Once confirmed, record `progress.lastCompletedStep = "step6d"` per `references/session-schema.md` section "Recording `progress.lastCompletedStep`".

---

## Step 7 — Architecture Review (BEFORE preview)

Spawn the `architecture-designer:architecture-reviewer` agent. Pass it:
- The full requirements summary — read from `docs/architecture-designer/session.json` (per `references/session-schema.md` section "Requirements-summary scope for sub-agent spawns", so the reviewer's Web3 dimension can actually fire on this first pass, not only on a later `/architecture-designer:review`). Do not rely solely on conversation memory.
- All generated Mermaid diagram code, labeled by type

Wait for the review report. **Regardless of verdict**, apply `references/session-schema.md` section "Reviewer–fixer cycle procedure" step 0 as soon as the report is received (records the verdict/cycle/`diagramsHash` into `progress.reviewCycles.architecture` and `docs/architecture-designer/last-review.md`; this runs even on a clean first-try pass, not only on Critical/Major findings).

**If the report contains CRITICAL or MAJOR items**: continue with that section's steps 1–4 (three-tier verdict): spawn `architecture-designer:architecture-fixer` with the review report, the path to `docs/architecture-designer/diagrams.json`, and the requirements summary, then re-spawn `architecture-designer:architecture-reviewer` to verify per that section.

**If the report contains only MINOR items**: note them for the user and proceed.

Do not open the browser preview until the exit condition in section "Reviewer–fixer cycle procedure" is met. Once met, record `progress.lastCompletedStep = "step7"` per `references/session-schema.md` section "Recording `progress.lastCompletedStep`" (the reviewer–fixer cycle procedure already handles `progress.reviewCycles.architecture` and `last-review.md`).

---

## Step 8 — Browser Preview

1. **Confirm `diagrams.json` is current** at `docs/architecture-designer/diagrams.json` — written incrementally through Stage 6d, possibly updated by architecture-fixer in Step 7. Must follow the schema in `references/diagrams-guide.md` section "`diagrams.json` Schema"; re-write it if step 2 flags issues.

2. **Validate diagrams**: run `node <scripts_dir>/validate-diagrams.mjs`. If it exits non-zero or prints `VALIDATION FAILED`, fix the flagged issues and re-write `diagrams.json` — do this regardless of `DEGRADED MODE`, which is not itself a pass/fail signal and can co-occur with a real failure. Do not proceed until it prints `VALIDATION PASSED`. If `DEGRADED MODE` still appears once passed, the real syntax parser was unavailable and some diagrams were only checked heuristically — proceed, but tell the user: "Diagram validation ran in degraded mode (parser dependencies not installed in `scripts/`) — some syntax errors may not have been caught. Run `npm install` in the plugin's `scripts/` directory for full validation coverage."

3. **Find a free port**: run `python3 <scripts_dir>/find-port.py`. Capture stdout; report the error if it exits non-zero.

4. **Start the preview server** in the background: `node <scripts_dir>/preview-server.mjs <port>`. It opens the browser automatically — tell the user the URL (e.g., `http://localhost:3000`).

5. **Do NOT create a stop-server script.** Leave the server running.

6. Record `progress.lastCompletedStep = "step8"` per `references/session-schema.md` section "Recording `progress.lastCompletedStep`".

---

## Step 9 — User Confirmation

After opening the browser, ask:

> **"Does this architecture design meet your needs, or is there anything you would like to revise?"**

If the user requests revisions:
- Identify the affected stage, return to it, ask the relevant questions again, update the answers
- **If Stage 1 is revised**: re-confirm `description` too — it can go stale once goal, stakeholders, or pain points change. Re-draft it (or accept the user's rewrite) the same way as the original confirmation.
- **If Stage 5 is revised**: re-run the `agentTools` check too — a changed stack changes which tools match. Overwrite `agentTools` in full with the new result (per `references/session-schema.md`), not merge with the old list. Also re-evaluate the Web3 track: if the revised stack now names a distributed-ledger platform where it didn't before, work through `references/web3-guide.md`'s dimensions and write the new `web3` key; if the revised stack dropped its decentralized component, delete the `web3` key entirely (do not leave a stale one behind); if it's still decentralized but the target network or a dimension's answer changed, re-run the dimensions and overwrite `web3` in full — same "overwrite, don't merge" rule as `agentTools`.
- Regenerate the affected diagrams and re-run the architecture reviewer (step 7) — this may spawn architecture-fixer, which writes `diagrams.json` directly
- Update `diagrams.json` with the revised diagrams (skip if the fixer already wrote it during the reviewer re-run)
- Re-run `node <scripts_dir>/validate-diagrams.mjs` — same gate as Step 8; fix flagged issues and re-validate before continuing. Do not tell the user to refresh until it passes.
- Tell the user to refresh their browser, then ask the confirmation question again

Repeat until the user confirms the design is correct. Once confirmed, record `progress.lastCompletedStep = "step9"` per `references/session-schema.md` section "Recording `progress.lastCompletedStep`".

---

## Step 10 — Low-Level Design

**Read `references/lld-guide.md`** before starting this stage — it has the exact format and rules for each artifact group below.

Derive the LLD directly from the confirmed HLD diagrams — do not invent endpoints or rules that are not visible in the sequence, class, or business-process diagrams.

**Resuming**: if `session.json`'s `lld` key already has a non-empty `confirmedGroups` list (a previous session died partway through this step), determine the applicable group list first — all five groups for microservices/event-driven architectures (per stage5's confirmed `architecturePattern`), or the four groups excluding `interServiceContracts` for a monolith/modular monolith, since that group is legitimately never confirmed (and never added to `confirmedGroups`) for those patterns. Then skip straight to the first *applicable* group not yet in `confirmedGroups`, in the fixed order below, rather than re-confirming groups already done. (Checking positional order 1–5 without this filter would wrongly treat a monolith's legitimately-skipped group 4 as "not yet reached" even when group 5 is already confirmed and the LLD is actually complete.)

Work through the five artifact groups in order, presenting each to the user and confirming (or revising) before moving to the next: **(1) API contracts** — one entry per endpoint visible in the sequence diagrams; **(2) business rules** — one entry per non-trivial operation, skipping simple CRUD; **(3) DTOs** — only for complex or shared bodies used by multiple endpoints; **(4) inter-service contracts** — only for microservices/event-driven architectures, omitted entirely for monoliths; **(5) error catalog** — derived from errors already referenced above, never invented fresh.

**Persist each group as soon as it's confirmed** — do not wait until all five are done. After each group is confirmed, write it into `session.json`'s `lld` key (create it if absent) and add that group's name to `lld.confirmedGroups` — read-fresh-modify-write-whole, same discipline as every other `session.json` write. For a monolith where group 4 is skipped entirely, do not add `interServiceContracts` to `confirmedGroups` and omit that field from `lld`.

After the user confirms all applicable groups, record `progress.lastCompletedStep = "step10"` per `references/session-schema.md` section "Recording `progress.lastCompletedStep`" — the complete LLD is now in `session.json`'s `lld` key, ready to include in the architecture document.

---

## Step 11 — Save Architecture Document

Once the user confirms, save the document to:
```
docs/architecture-designer/architecture/{yyyymmdd}-{topic}.md
```

- `{yyyymmdd}`: today's date as 8 digits in ISO order — use JavaScript `Date` to format: year (4-digit) + month (2-digit, zero-padded) + day (2-digit, zero-padded). Example: `20260705` for 5 July 2026. **Never use the shell `date` command.** This ISO-style order ensures files sort chronologically when listed alphabetically.
- `{topic}`: the project/application name in kebab-case (lowercase, hyphens, no spaces)
- If a file with this name already exists, append `-2`, `-3`, etc. until the filename is unique

After saving, append `{ "path": "<absolute path of the saved file>", "createdAt": "<current ISO timestamp>" }` to `session.json`'s top-level `"documents"` array (create it if absent; backfill `schemaVersion`/`project`/`description` at the same time if the file predates them, per the tolerant-read rule in `references/session-schema.md`). This lets `/architecture-designer:implement` find the latest document — the last entry's `path` — without asking.

**The document must begin with this metadata table on line 1:**

```markdown
| Date       | Version | Status | Reason | Previous Document |
|------------|---------|--------|--------|-------------------|
| {dd-mmm-y} | 1.0     | Draft  | -      | -                 |
```

- `dd-mmm-y` format: day is zero-padded (e.g., `05`), month is 3-letter capitalized abbreviation (`Jan`, `Feb`, `Mar`, `Apr`, `May`, `Jun`, `Jul`, `Aug`, `Sep`, `Oct`, `Nov`, `Dec`), year is 4 digits. Example: `05-Jul-2026`.

**Document body sections (in order)**: follow `references/document-template.md` — ten fixed sections from Project Overview through Low-Level Design, each pulling from the corresponding stage or sub-agent output (section 7 from `session.json`'s `progress.reviewCycles.database.approvedOutput`, section 10 from the `lld` key), plus an 11th conditional "Decentralized Architecture Considerations" section when the Web3 track was active.

Record `progress.lastCompletedStep = "step11"` per `references/session-schema.md` section "Recording `progress.lastCompletedStep`".

---

## Step 12 — Document Review

Spawn the `architecture-designer:document-reviewer` agent with the path to the saved document, the requirements summary (per `references/session-schema.md` section "Requirements-summary scope for sub-agent spawns"), and the expected filename. Wait for the verdict. (`document-reviewer`/`document-fixer` read `references/document-review-checklist.md` directly for the exact F1–F7/C1–C9 criteria — no need to read it here.) **Regardless of verdict**, apply `references/session-schema.md` section "Reviewer–fixer cycle procedure" step 0 as soon as the verdict is received (records the verdict/cycle/`documentHash` into `progress.reviewCycles.document` and `docs/architecture-designer/last-review.md`; this runs even on a clean first-try pass, not only on failure).

**If DOCUMENT REVIEW FAILED**: continue with that section's steps 1–4: spawn `architecture-designer:document-fixer` with the document path, the review report, the requirements summary, and the path to `docs/architecture-designer/diagrams.json`. After it overwrites the document, rename the file first if the fixer's log says it must be renamed (F6), then re-spawn `document-reviewer` and verify (binary verdict — cycle until DOCUMENT REVIEW PASSED).

**Once it passes**: update the `Status` column in the metadata table from `Draft` to `Approved`. The table should now read:

```
| {date} | 1.0 | Approved | - | - |
```

Record `progress.lastCompletedStep = "step12"` per `references/session-schema.md` section "Recording `progress.lastCompletedStep`".

---

## Step 13 — Implementation Offer

After the document is approved, ask:

> **"The architecture document is approved. Would you like me to proceed with implementation — generating the project skeleton, data models, and infrastructure files based on this document?"**

If yes: scan the working directory for signs of an existing project, per `references/session-schema.md` section "Existing-project scan categories".

**If files already exist**: summarize what was found and ask the question in `references/session-schema.md` section "Merge-strategy question". **If the scan finds nothing**: no question needed — proceed as a fresh start into an empty project.

Before spawning, resolve the applicable remediation plan per `references/session-schema.md` section "Finding the applicable remediation plan", using the approved document's path. Then run `references/session-schema.md` section "Resumable-plan detection procedure" using the approved document's path as `{document}` to produce the **Previous plan path**, if the user chooses to resume.

Then follow `references/session-schema.md` section "Implementation-planner → architecture-implementer spawn sequence" to spawn `implementation-planner` and, once its plan is confirmed, `architecture-implementer`, passing these six inputs:
- The path to the approved document
- **Existing project summary** — translated into the agent's expected strategy label: `Fresh start (empty project)` if nothing was found; `Merge` if the user chose (a); `Fresh start (existing project)` if the user chose (b); `User-described layout` if the user chose (c)
- The technology stack from stage 5
- **Agent tools** (optional) — `session.json`'s `"agentTools"` array, if present and non-empty
- **Remediation plan path** — resolved above, if it exists on disk and wasn't ruled out
- **Previous plan path** — the resumed plan's `path`, if the user chose to continue (omit otherwise)

If the user says no: let them know they can run `/architecture-designer:review` at any time to revisit and revise the architecture.

Either way, record `progress.lastCompletedStep = "step13"` per `references/session-schema.md` section "Recording `progress.lastCompletedStep`" — this pipeline pass is complete.

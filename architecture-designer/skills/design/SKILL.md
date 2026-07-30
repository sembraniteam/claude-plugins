---
name: design
description: This skill should be used when the user wants to design a new application's architecture or infrastructure — says "design my architecture", "help me plan the architecture", "create architecture diagrams", "I need to plan a new system", or is starting a new project and needs a structured design process. Also trigger when the user mentions HLD, LLD, API contracts, or system design for a system with no existing codebase and no existing architecture document yet. Not for adding/changing an API contract, endpoint, or LLD artifact on an already-documented system, or for generating code from an approved document — see the review and implement skills for those. Not for producing a first architecture document from a codebase that already exists — even if undocumented, that's the review skill's codebase-reconstruction path.
allowed-tools: ["Read", "Write", "Edit", "Bash", "Glob", "Agent", "WebSearch"]
---

# Architecture Designer — Main Design Workflow

This skill guides the user through a six-stage design process plus a sequence of post-design steps (architecture
review, optional persona reviews, browser preview, optional visual verification, user confirmation, low-level design,
test strategy, document save, document review, implementation offer), ending with browser-rendered Mermaid diagrams,
low-level design artifacts, a test strategy, a reviewed and approved document, and an optional code skeleton.

Always use this skill for new architecture design, even if the user has already started describing their system in the
conversation — do not skip straight to diagram generation or freeform advice.

**Scripts directory:** `../../scripts/` relative to this SKILL.md — referred to as `<scripts_dir>` throughout this file.
Resolve it at runtime from this SKILL.md's absolute path.

---

## How to run this workflow

**Before starting — check for an existing session**: look for `docs/architecture-designer/session.json`. If it exists,
read it and ask the user:

> "I found an existing design session for
>
**[project name from the file, or 'a previous project' if unnamed]** — [description from the file, or omit this clause if unset].
> Would you like to continue where we left off, or start a new design from scratch?"

If continuing: **first check `progress.owner`, if the key is present.** If it reads `"review"`, a
`/architecture-designer:review` revision died mid-pipeline, not this skill's own design pipeline — this skill's resume
logic below only covers the original design pass. Tell the user: "It looks like a previous
`/architecture-designer:review` revision didn't finish. Run `/architecture-designer:review` to resume it instead." and
stop here rather than proceeding into Stage resume. Otherwise (`progress.owner` is `"design"`, or the key is absent —
legacy sessions predating this key, or one that never reached Stage 6a): brief the user on where the previous session
left off and resume from the first incomplete stage. Once stage1–5 are confirmed (the "Session completeness gate"
precondition — stage6b/6c are not required, since Stage 6a can already have progressed before either is confirmed), also
apply `references/session-schema.md` section "Resuming Steps 6a–13 via `progress`" — a session that died anywhere from
Stage 6a through Step 13 should resume there, not restart the whole pipeline, and any `pending` key found means the
previous session died mid-stage within 1–6c (same section covers this). If starting fresh: delete
`docs/architecture-designer/session.json` (and
`docs/architecture-designer/diagrams.json` and `docs/architecture-designer/last-review.md` if present) first.

**Checkpoint partial answers incrementally**: within any of Stages 1–6c, after each individual answer the user gives
(not just at the stage's final confirmation), upsert `session.json`'s `pending` key per `references/session-schema.md`
section "Mid-stage pending answers" — this is what lets a session resume mid-stage instead of only at stage boundaries.
Delete `pending` in the same write that records the stage's real confirmed key.

**Legacy-session backfill check**: run now, and again immediately before the Stage 6 gate below — see
`references/session-schema.md` section "Legacy-session backfill check" for the exact trigger and procedure. Skipping
this leaves the Stage 6 completeness gate permanently unpassable for that session.

Work through Stages 1–6 in order, then Steps 7–13. At the end of each stage, summarize the user's answers and ask:
> "Does this summary look correct? Shall we move to the next stage?"

Do not proceed until confirmed. After each confirmation, persist the stage summary to
`docs/architecture-designer/session.json` (create `docs/architecture-designer/` if needed) — write the exact text the
user confirmed, not a paraphrase, since sub-agents work from this file directly and cannot access conversation history.

**Read `references/session-schema.md` before writing to or reading anything beyond the stage keys below** — it is the
canonical schema: fixed top-level keys, the array-of-objects shape for `documents`/`remediationPlans`/
`implementationPlans`, which keys are guaranteed present, link resolution between arrays, and the
single-writer-per-key / no-CAS write discipline every reader and writer must follow.

**`description` is required**: write `schemaVersion: 2`, `project`, and `description` together with `stage1` at the
first session.json write below — see `references/session-schema.md` for its two valid sources (user-written vs.
auto-generated) and `references/discovery-questions.md` Stage 1 for surfacing an auto-drafted version for approval. Do
not proceed to Stage 2 with it empty.

---

## Stage 1 — Requirements Gathering

Goal: understand what the application must do and why it exists.

Ask the Stage 1 questions in `references/discovery-questions.md` (combine them into a conversational flow rather than a
rigid checklist, but cover all of them), including the description question (write-your-own vs. auto-generate — see that
reference for how to surface the drafted text). Summarize answers, confirm, then proceed.

Once confirmed, write the first `docs/architecture-designer/session.json`: `stage1`, plus the required top-level
`schemaVersion: 2`, `project` (a short slug derived from the application name or purpose), and `description` (see "
`description` is required" above). All three are written this once, at this point in the workflow — do not defer them to
Step 11.

---

## Stage 2 — Requirements Analysis

Goal: separate functional from non-functional requirements.

Ask the Stage 2 questions in `references/discovery-questions.md`.

> **Compliance grounding rule**: When the user names a compliance framework, record it as a stated requirement — do not
> assert specific technical controls from memory (e.g., "GDPR requires X-day retention"). Regulatory specifics vary by
> jurisdiction and change over time; model-generated compliance claims are expensive to correct. Mark every
> compliance-specific control in the document with **"⚠ Needs legal/compliance validation"** and defer exact
> requirements
> to the user's legal team.

> **Web3 / decentralized detection**: if the application is described as decentralized, blockchain-based, or on-chain,
> note this now — Stage 5 will read `references/web3-guide.md` and work through its additional questions before the
> stack
> is finalized. The same applies if this isn't apparent until Stage 5 names a distributed-ledger platform directly.

> **Offline-first detection**: this track is not mandatory — most apps are correctly online-first even when mobile or
> occasionally offline. Note it now only if the application must let users **create or edit** data during a meaningfully
> long offline period (not just view previously-cached data, and not just a brief network blip a retry would cover) — a
> mobile app for poor-connectivity environments, a PWA with an explicit offline-write requirement, or collaborative
> editing where clients may diverge before reconciling. If so, Stage 5 will read `references/offline-first-guide.md`'s
> decision test and work through its additional questions before the stack is finalized. The same applies if this isn't
> apparent until Stage 5, but naming a client-side embedded database alone is not sufficient — see that guide's "This
> track is not mandatory" section for the full test.

**Domain edge-case elicitation (required, before the Stage 2 summary/confirmation)**: read
`references/domain-edge-cases-guide.md` and match the functional requirements just gathered against its domain
categories (authentication, payments, inventory/fulfillment, scheduling/booking, messaging/notifications,
multi-tenancy, file upload, search) — a category applies only when its stated signal is actually present; do not force
a category with no signal. This exists because a diagram or document can be syntactically correct and internally
consistent while still missing a domain nuance the user never thought to mention — every downstream check in this
plugin can only verify what was stated, not the absence of something nobody raised. Ask the matched categories'
targeted questions, folded into the same conversational flow as the rest of Stage 2 — not a separate rigid checklist. A
"no" or "out of scope" answer is a valid, complete answer; record it either way rather than treating an unmatched
category as something to force into scope.

Summarize as two lists (functional and non-functional) plus the matched domain edge-case questions and answers,
confirm, then proceed. Write the confirmed edge-case list to `session.json`'s `stage2.domainEdgeCases` at the same time
as `stage2`.

**Quality Attribute Scenarios**: before moving to Stage 3, read `references/quality-driven-design-guide.md` and
formalize the 3–8 non-functional requirements that have (or can be given) a concrete, testable target into Quality
Attribute Scenarios using its six-part format (source, stimulus, environment, artifact, response, response measure). Not
every NFR needs one — an NFR with no measurable stimulus/response stays as ordinary prose in the list above. Present the
scenarios, confirm, then write them to `session.json`'s `stage2.qualityAttributeScenarios` at the same time as
`stage2`.

---

## Stage 3 — Feasibility Study and Constraints

Goal: identify real-world constraints that will shape technical decisions.

Ask the Stage 3 questions in `references/discovery-questions.md`. Summarize constraints, confirm, then proceed.

---

## Stage 4 — Capacity Planning

Goal: produce concrete numbers that will drive infrastructure sizing and technology choices.

Ask the Stage 4 questions in `references/discovery-questions.md`. Summarize with explicit numbers (estimates are fine —
label them as estimates), confirm, then proceed.

**Number discipline**: Every figure in the confirmed capacity summary must originate from the user's answers or be
explicitly derived from those answers — show the arithmetic (e.g., "10,000 daily active users ÷ 86,400 s × 3× peak
factor ≈ 0.35 req/s baseline"). Do not cite database or infrastructure performance benchmarks from memory (e.g.,
"PostgreSQL handles 10,000 TPS") as justification — those figures are not grounded in this project's specific usage and
create false precision. When the user cannot provide a number, derive a reasoned estimate together and label it **"
estimate — validate at launch"**.

---

## Stage 5 — Technology and Architecture Pattern Selection

Goal: recommend a specific, justified technology stack.

**Architectural Drivers (required, before proposing any item below)**: read `references/quality-driven-design-guide.md`
and select 3–6 Architecturally Significant Requirements from the Stage 2 Quality Attribute Scenarios, Stage 3
constraints, and Stage 1 goals, per that guide's selection criteria (business-critical, pervasive across multiple Stage
5 items, or high technical risk). Present the ranked drivers, confirm, then write them to `session.json`'s top-level
`architecturalDrivers` at the same time as `stage5` below.

**Read `references/tech-stacks.md` before making recommendations.** It contains concrete options organized by
architecture pattern, scale tier, team size, cloud provider, database type, auth approach, and frontend, plus the
citation pattern for tracing each choice back to stages 1–4 (section "How to justify recommendations in the architecture
document") — use it to ground suggestions in real technology names rather than abstract categories.

Based on everything gathered in stages 1–4, propose and justify, in order: **(1) architecture pattern**
(monolith/modular monolith/microservices/serverless/event-driven — a modular monolith is almost always right for small,
early-stage teams). Once item (1) is chosen, read `references/design-patterns-guide.md` Part 1 and name the applicable
POSA architectural pattern (s) for the internal structure of each deployable unit and for inter-service communication —
Layers applies to nearly every system regardless of deployment topology; Broker, Pipes and Filters, MVC, and Microkernel
apply only when that pattern's specific signal is present in the requirements; **(2) backend language and framework**,
named specifically (e.g. "Fastify 5", not "Node.js"); **(3)
frontend** framework and version, if applicable; **(4) database engine (s)** — a high-level call; the database-designer
agent designs the full schema in Stage 6, applying `references/timezone-guide.md`'s UTC-storage rule to every datetime
column and to any scheduled/recurring feature (digests, reminders, cron jobs) surfaced in stages 1–4; **(5)
infrastructure provider and key managed services**, named specifically (e.g. "AWS ECS Fargate", not "containers on
AWS"); **(6) supporting services** (queue, cache, search, object storage) — only if the functional requirements need
them; **(7) authentication approach**, justified by user roles, security requirements, and team capacity; **(8)
observability strategy** — logging aggregator (e.g. ELK, Grafana Loki, Datadog, CloudWatch), metrics/dashboards, and
distributed tracing (OpenTelemetry + Jaeger/Tempo) if multiple services or async flows are involved, scaled to what the
system's actual operational maturity requires — a small monolith may need only structured logging and one dashboard;
**(9) disaster recovery** — RPO/RTO derived from the Stage 2 availability NFR, backup strategy, failover approach; **(10)
   error handling and resilience strategy** — derived from the Stage 2 error-handling NFR. Read
   `references/resilience-guide.md` before finalizing this and name, per its pattern table and library table: the
   backoff strategy and max attempts for retries against external dependencies named in stages 1–4, a circuit breaker or
   equivalent for any dependency the NFR marked as must-not-fail-silently, timeout budgets for synchronous calls, and
   the graceful-degradation behavior (if any) for non-critical features when a dependency is down. Name the specific
   library its "Library per stack" table gives for the confirmed language, rather than describing the concept
   abstractly — scale to what the system actually needs: a monolith with no external dependencies may only need timeout
   budgets, not a full circuit breaker; **(11) rate limiting strategy** — derived from the Stage 2
   rate-limiting/abuse-prevention NFR. Read
   `references/rate-limiting-guide.md`
   before finalizing this and name, per its tradeoff table and library table: the algorithm, the specific middleware
   library for the confirmed backend language, and which layer enforces it (API gateway, application middleware, or
   both) — plus the shared store (Redis) the limiter counters live in if the infrastructure decision above is
   horizontally scaled, rather than an in-process store that would silently multiply the real limit by instance count.
   Skip this only for a system with no public-facing or untrusted-client-reachable API, the same way item 10 is skipped
   for a monolith with no external dependencies — state that explicitly rather than omitting it silently.

Every recommendation must cite a specific reason from stages 1–4, plus the architectural driver ID (s) it satisfies from
`architecturalDrivers` above when one applies (e.g. "PostgreSQL with synchronous replication, satisfying AD-2 (99.9%
availability)") — a decision with no specific driver behind it is still fine for ordinary best-practice choices, but say
so plainly ("no specific driver; standard choice for this scale") rather than inventing a citation. Apply this
comprehensively here, at the point of writing the recommendations — `architecture-reviewer`'s dimension 3 only
spot-checks a few of the eleven items downstream, so it is not a backstop for skipping citations on the rest.

**Trade-off and Risk Analysis (required, after the eleven items are proposed and discussed, before final
confirmation)**:
per `references/quality-driven-design-guide.md`, walk through the proposed decisions once more looking for tension
between drivers — a decision that improves one driver while measurably worsening another. For each trade-off found,
record which drivers are in tension, the trade-off itself, any sensitivity parameter, the decision made, the rationale
for that decision, and the ID (s) of any risk register entries it creates (`relatedRisks`). For each risk found (from a
trade-off or independently), record its category, likelihood, impact, mitigation, related driver if any, and status. A
simple system with few competing drivers may honestly have only one or two entries in each — do not pad the lists.

This trade-off/risk pass is not a separate confirmation round-trip: fold it into the same presentation as the eleven
technology decisions — present all eleven items plus the trade-off/risk analysis together, discuss and adjust as one
unit, confirm once — then write everything to `session.json` together: `stage5` (including `tradeoffAnalysis`) and
top-level `riskRegister`, all at the same time.

**Cost Estimation (required, after the eleven items and the trade-off/risk analysis, before final confirmation)**: read
`references/cost-estimation-guide.md` and produce a concrete monthly/annual infrastructure cost breakdown — a dollar
figure per component (compute, database, cache, object storage, CDN/egress, queue, observability, metered third-party
APIs), each sized from the confirmed Stage 4 capacity numbers, never from a recalled benchmark. Price each component via
WebSearch against the confirmed cloud provider's current list pricing when WebSearch is available, citing the source and
check date; when it is not available, label the figure **"estimate — verify at implementation time"** — the identical
discipline this stage's "Version grounding" rule already applies to technology versions. Reconcile the rolled-up total
against Stage 3's budget constraint, if one was recorded, and flag a mismatch explicitly rather than silently presenting
a number the stated budget can't support. Fold this into the same single confirmation round-trip as the eleven items and
the trade-off/risk analysis above — present all three together, confirm once — then write the confirmed breakdown to
`session.json`'s `stage5.costEstimate` at the same time as `stage5`.

**Version grounding**: every technology needs a specific version number. If WebSearch is available, verify the current
stable release before writing it down; if not, write **"latest stable — verify at implementation time"** rather than a
version from memory that may be stale. The same discipline applies to cloud managed-service names and
compliance-specific *vendor/service* claims (e.g., whether a specific service holds a certification like SOC 2 or ISO

27001) — verify with WebSearch or label **"⚠ verify before relying"**. This is a distinct claim from the Stage 2
       compliance-grounding rule above (which *regulatory controls* a framework requires, tagged **"⚠ Needs
       legal/compliance validation"**): a vendor certification is a checkable fact, a regulatory control is a legal
       interpretation — keep the two tags visually distinct rather than merging them.

**Optional — Web3 / decentralized track**: if Stage 1–2 flagged the application as decentralized/blockchain/on-chain, or
a distributed-ledger platform is named as part of the stack above, read `references/web3-guide.md` in full before
finalizing the stack — work through its eight invariant dimensions as additional questions, following its core rule on
placeholders vs. asserted facts. Present the dimensions, discuss, confirm, then write the confirmed answers to
`session.json`'s `"web3"` key (create it) at the same time as `"stage5"`. Skip this step entirely — do not create the
key — for non-decentralized applications.

**Optional — Offline-first track**: not mandatory — apply only when Stage 1–2 flagged a genuine offline- *write*
requirement, or a client-side embedded database/sync engine named as part of the stack above is specifically for that
purpose. Before treating either signal as a trigger, check it against `references/offline-first-guide.md`'s "This track
is not mandatory" decision test — an app that only reads cached data offline, or one already covered by the Stage 5
error-handling/resilience strategy's retry policy, does not qualify. If the test is met, read the guide in full before
finalizing the stack — work through its local-storage choice, sync architecture, and conflict-resolution strategy
(including how divergent `updated_at` values are handled — see that guide's section 3) as additional questions. Present
the decisions, discuss, confirm, then write the confirmed answers to `session.json`'s `"offlineFirst"` key (create it)
at the same time as `"stage5"`. Skip this step entirely — do not create the key — for applications with no genuine
offline-write requirement.

**Optional — agent tools for implementation**: independent of the Web3 and offline-first tracks above and always worth
checking, even for a decentralized or offline-first stack (a matched tool answers "what's available," not "what was
confirmed about the network" — see `references/agent-tools.md`'s core rule). Once the stack above is confirmed, read
`references/agent-tools.md` and follow its procedure to check for MCP servers/Skills actually available in this
environment that match the confirmed stack; propose any matches to the user as the `agentTools` addendum to the Stage 5
summary and let them drop any entry — this step never blocks Stage 5 confirmation. Write the confirmed list (or omit the
key entirely if empty) to `session.json`'s `"agentTools"` at the same time as `"stage5"`.
`references/scaffolding-guide.md`
names the exact scaffolding command for the now-confirmed stack (e.g. `create-next-app`, `go mod init`) — implementer
uses it directly during Step 9's implementation planning, not here; nothing to do in Stage 5 beyond having the stack
confirmed.

---

## Stage 6 — Architecture and Infrastructure Design

**Session completeness gate**: re-run the legacy-session backfill check above once more here, immediately before this
gate, in case stage1–5 only just became fully confirmed. Then run `python3 <scripts_dir>/validate-session.py` and show
its output — this is a hard gate; do not proceed to 6a or any later step until it reports `SESSION CHECK PASSED`. See
`references/session-schema.md` section "Session completeness gate" for what the script checks and how to resolve a
failure. A missing top-level field on an otherwise-complete resumed session is the legacy-backfill case above, not a
missing stage.

### 6a. Domain modeling (DDD), then database design (delegate to sub-agent)

**Domain modeling (required, before spawning database-designer)**: read `references/ddd-guide.md` and identify bounded
contexts, their aggregates (root entity, member entities, invariants), and each context's ubiquitous language, derived
from Stage 1's business processes and Stage 2's functional requirements. This always produces a result — a small system
may honestly have a single bounded context with one or two aggregates; state that explicitly rather than omitting the
step. When 2 or more bounded contexts are identified, also name the integration pattern between every pair that actually
integrates (Partnership, Shared Kernel, Customer/Supplier, Conformist, Anticorruption Layer, Open Host Service,
Published Language, or Separate Ways) per that guide's Step 4 — this feeds the Context Map diagram in Stage 6d. Present
it, confirm, then write to `session.json`'s top-level `domainModel` (including `relationships` when applicable).

Spawn the `architecture-designer:database-designer` agent. Pass it three inputs: the complete requirements summary (read
from `docs/architecture-designer/session.json`, not from memory — per `references/session-schema.md` section
"Requirements-summary scope for sub-agent spawns", so its Web3 and offline-first steps can fire when applicable, per
`references/web3-guide.md` and `references/offline-first-guide.md` — this scope already includes the `domainModel` just
confirmed, so schema/table grouping respects aggregate boundaries per `references/ddd-guide.md`), the domain entities
extracted from the functional requirements, and the access patterns from the business processes. Wait for its full
output per `agents/database-designer.md`'s "Output format" — engine recommendation, schema design, ERD, index list,
transaction/concurrency strategy, secure connection configuration, migration strategy, and (when `agentTools` was
non-empty) an agent-tools usage note — and persist all of it, not just a subset.

Then spawn `architecture-designer:database-reviewer` with the full database-designer output and the requirements summary
(same scope as above). **Regardless of verdict**, apply `references/session-schema.md` section "Reviewer–fixer cycle
procedure" step 0 as soon as the report is received (records the verdict/cycle/approved output into
`progress.reviewCycles.database` and `docs/architecture-designer/last-review.md`; this runs even on a clean first-try
pass, not only on failure). If it returns `DATABASE REVIEW FAILED`, continue with that section's steps 1–4 (binary
verdict — cycle until `DATABASE REVIEW PASSED`): spawn `architecture-designer:database-fixer`, which receives the review
report, the database-designer output, the requirements summary (same scope), and the path to
`docs/architecture-designer/diagrams.json`. It writes the corrected ERD and indexPlan directly into `diagrams.json`
**and returns the corrected schema, ERD, index plan, transaction and concurrency strategy (when present), and connection
config as text** — replace the database-designer output held in context with this corrected text. Step 0 of the
reviewer–fixer cycle procedure (triggered above) writes this same final text into
`progress.reviewCycles.database.approvedOutput` — that key, not conversation memory, is the durable source Step 11
(section 8) and Stage 6d's ERD both read from.

**The database design embedded in the document (Step 11, section 8) and the diagram set must be the final approved
version** — the fixer's corrected text if any cycle ran, otherwise the original output. Never fall back to the original
after a fixer cycle has produced a correction; the two must never diverge.

The reviewer–fixer cycle procedure in `references/session-schema.md` records `progress.reviewCycles.database` and
`docs/architecture-designer/last-review.md` unconditionally, on every report received — not only on a failing verdict;
see that section's step 0. The first time this pass touches `progress` at all (i.e., before that first write), set
`progress.owner = "design"` (overwrite in full — this is a new pipeline pass). Once `DATABASE REVIEW PASSED` is reached,
record `progress.lastCompletedStep = "step6a"` per `references/session-schema.md` section "Recording
`progress.lastCompletedStep`".

### 6b. Infrastructure as Code (IaC)

**Skip this step** (do not create `stage6b`) only for a project with no deployment target at all — a library, CLI tool,
or local-only application with nothing to provision infrastructure for. Every project with a cloud or server deployment
target runs this step; this is the only legitimate case where `document-reviewer`'s C7 check is `N/A` rather than a
FAIL.

**Read `references/iac-guide.md` before making recommendations** — it has the decision tables, module structure, and the
exact content to produce for each point below.

Based on the cloud provider chosen in Stage 5 and the infrastructure shape from the capacity plan, define and confirm,
in order: **(1) tool selection** (Terraform, OpenTofu, Pulumi, AWS CDK, CloudFormation, or Bicep — never local state;
see guide section 1 for decision rules); **(2) state backend**; **(3) module breakdown**, omitting modules for services
not in scope; **(4) environment strategy** (default: directory-per-environment); **(5) drift detection**, matched to the
team's operational maturity.

Present the plan, discuss open questions, adjust, and confirm before continuing.

After confirmation, append the confirmed decisions to `docs/architecture-designer/session.json` under `"stage6b"`
(create or overwrite) — use the exact text the user confirmed, not a paraphrase.

---

### 6c. CI/CD Pipeline Design

**Skip this step** (do not create `stage6c`) only for the same no-deployment-target case 6b skips for — nothing to build
a deploy pipeline toward. This is the only legitimate case where `document-reviewer`'s C8 check is `N/A` rather than a
FAIL.

**Read `references/cicd-guide.md` before making recommendations** — it has the decision tables, standard stage template,
and the exact content to produce for each point below.

Based on where the code is hosted, the deployment target, and the architecture pattern, define and confirm, in order:
**(1) platform selection** (see guide section 1 for decision rules; for Kubernetes targets, consider splitting CI
platform for build and Argo CD/Flux for the CD leg); **(2) pipeline stages** with trigger and gate condition per stage,
omitting what the project doesn't need; **(3) branching strategy** (default: GitHub Flow); **(4) environment
promotion**, dev → staging → prod, with a manual approval gate on prod by default and a documented rollback procedure;
**(5) secret injection** — prefer OIDC over long-lived keys, and confirm no secrets are hardcoded or committed; **(6)
artifact management** — registry, tagging scheme (git SHA), retention policy.

Present the plan, discuss, adjust, and confirm before continuing.

After confirmation, append the confirmed decisions to `docs/architecture-designer/session.json` under `"stage6c"`
(create or overwrite) — use the exact text the user confirmed, not a paraphrase.

---

### 6d. Diagram selection and generation

Select the Mermaid diagrams relevant to the project. **All diagrams are optional** — select only those that add clarity
for this specific project.

**Write `docs/architecture-designer/diagrams.json`'s skeleton now**, before generating any diagram's code —
`{ title, topic, generatedAt, diagrams: [] }` per `references/diagrams-guide.md` section "`diagrams.json` Schema". Then,
for each selected diagram in turn: generate its code, apply the Mermaid compatibility and anti-overlap rules from that
same reference immediately to this one diagram (not deferred to a later pass — see 6e below), then append its finished
entry to `diagrams.json` and write the file (read-fresh-modify-append-write-whole). This way a session that dies partway
through a large diagram set still has every diagram completed so far on disk, not just whatever fits in conversation
context.

After generating, tell the user which were created and why, and which were skipped and why (e.g., "State diagram
skipped — no entities with complex status lifecycles identified").

**Read `references/diagrams-guide.md` before generating any diagram** — it has the exact attribute format for ERD, full
templates per diagram type, common mistakes, and anti-overlap rules. Don't rely on memory for Mermaid syntax.

**Available diagram types** (quick index only — `references/diagrams-guide.md`'s per-type "When to create" section is
the authoritative wording; this table is a pointer to it, not a second copy):

| Diagram          | Mermaid type                          | Create when                                                      |
|------------------|---------------------------------------|------------------------------------------------------------------|
| Use case         | `flowchart LR`                        | 2+ user roles with distinct feature sets                         |
| Business process | `flowchart TD`                        | Complex workflow with 2+ decision branches                       |
| ERD              | `erDiagram`                           | Any SQL database — always                                        |
| Sequence         | `sequenceDiagram`                     | Always: auth flow + one per core feature (see requirement below) |
| Class            | `classDiagram`                        | Non-trivial domain model with business rules                     |
| Context Map      | `flowchart LR`                        | 2+ bounded contexts in `domainModel`                             |
| State            | `stateDiagram-v2`                     | Any entity with 3+ lifecycle states                              |
| C4 Context       | `C4Context`                           | Any external integration or 2+ user types                        |
| C4 Container     | `C4Container`                         | 2+ deployable components                                         |
| Deployment       | `flowchart TD` or `architecture-beta` | Cloud or multi-server deployment                                 |
| CI/CD pipeline   | `flowchart TD`                        | 2+ deployment environments or staged release                     |

**Core feature coverage requirement**: every functional requirement confirmed in Stage 2 that represents a distinct
user-facing feature — not a minor CRUD sub-step of a feature already covered — must have its own dedicated sequence
diagram showing that feature's primary flow, including its failure path (`alt` block). A single "primary transaction"
diagram is not sufficient coverage once Stage 2 lists more than one distinct feature: cover them all, not just the most
obvious one. Group trivial sub-actions of the same feature into that feature's one diagram rather than fragmenting into
near-duplicate diagrams (e.g., "create order" and "cancel order" can share one diagram if both are simple branches of
the same flow; "place order" and "process refund" cannot, since they are distinct features). `architecture-reviewer`'s
requirements-traceability dimension raises a Major finding for any core feature with no dedicated diagram — see that
agent's dimension 3.

**Production-ready requirement**: for any system targeting production workloads, the deployment/infrastructure diagram
must show at least one observability sink (from Stage 5) and one DR component (replica, backup target, or cross-region
failover) — `architecture-reviewer` raises a Major finding if either is absent.

**ERD special requirement**: mark indexed columns via `"idx"` attribute comments and include the index list table (from
database-designer) immediately after the ERD block — see `references/diagrams-guide.md` for the exact format. Build the
ERD from `session.json`'s `progress.reviewCycles.database.approvedOutput` (the final approved schema/ERD/index plan —
see `references/session-schema.md` section "Persisting the database design output"), not from conversation memory — this
is what makes Stage 6a's output durable if 6d runs in a resumed session where Stage 6a's conversation turn is gone.

**Class diagram design-principle pass**: after drafting a Class Diagram, before appending it to `diagrams.json`, read
`references/design-principles-guide.md` and pass the draft once against its Quick Reference section (SOLID, DRY, YAGNI,
Tell Don't Ask, Hollywood Principle, Law of Demeter) — does each service have one responsibility, are variant-heavy
services modeled with an interface rather than a growing branch, are dependencies interface-typed rather than concrete,
and does any association chain reach more than one hop deep. Adjust the diagram in place; this is a lightweight pass on
the diagram already being built, not a separate confirmation round-trip.

**Class diagram GoF pattern pass**: in the same pass, read `references/design-patterns-guide.md` Part 2 and check the
draft against its signal column — a growing conditional chain (Strategy or Chain of Responsibility), a multi-step
optional-heavy construction (Builder), a third-party integration with no owned interface around it (Adapter), or
cross-cutting wrapped behavior (Decorator) are the most common matches. Name any pattern applied in the diagram's
`rationale`/`details` field (`references/diagrams-guide.md`) rather than leaving an unlabeled structure — do not force a
pattern onto a class where no signal is present.

### 6e. Mermaid compatibility and diagrams.json integrity check

`references/diagrams-guide.md` section "Mermaid v11.16 Compatibility Rules" and section "Preventing Node Overlap"
(required syntax like `flowchart` not `graph`, `architecture-beta` icon slots, ELK layout, `align` directives, label
length, C4 layout config) were already applied per-diagram in 6d as each one was generated and written. This step is a
final integrity check, not a write: confirm every diagram selected in 6d has a corresponding entry in
`docs/architecture-designer/diagrams.json` and that no entry is partial. This must be true before Step 7 — the
architecture-fixer reads and updates the file in place during the review cycle and will fail if the file does not exist
or is incomplete. Once confirmed, record `progress.lastCompletedStep = "step6d"` per `references/session-schema.md`
section "Recording `progress.lastCompletedStep`".

---

## Step 7 — Architecture Review (BEFORE preview)

Spawn the `architecture-designer:architecture-reviewer` agent. Pass it:

- The full requirements summary — read from `docs/architecture-designer/session.json` (per
  `references/session-schema.md` section "Requirements-summary scope for sub-agent spawns", so the reviewer's Web3
  dimension can actually fire on this first pass, not only on a later `/architecture-designer:review`). Do not rely
  solely on conversation memory.
- All generated Mermaid diagram code, labeled by type

Wait for the review report. **Regardless of verdict**, apply `references/session-schema.md` section "Reviewer–fixer
cycle procedure" step 0 as soon as the report is received (records the verdict/cycle/`diagramsHash` into
`progress.reviewCycles.architecture` and `docs/architecture-designer/last-review.md`; this runs even on a clean
first-try pass, not only on Critical/Major findings).

**If the report contains CRITICAL or MAJOR items**: continue with that section's steps 1–4 (three-tier verdict): spawn
`architecture-designer:architecture-fixer` with the review report, the path to
`docs/architecture-designer/diagrams.json`, and the requirements summary, then re-spawn
`architecture-designer:architecture-reviewer` to verify per that section.

**If the report contains only MINOR items**: note them for the user and proceed.

Do not open the browser preview until the exit condition in section "Reviewer–fixer cycle procedure" is met. Once met,
record `progress.lastCompletedStep = "step7"` per `references/session-schema.md` section "Recording
`progress.lastCompletedStep`" (the reviewer–fixer cycle procedure already handles `progress.reviewCycles.architecture`
and `last-review.md`).

---

## Step 7b — Persona Reviews (optional)

Ask the user: **"Would you like additional focused reviews from a Security persona and/or a Cost persona, alongside the
standard architecture review? These surface findings the general review may not emphasize — e.g. attack-surface gaps or
infrastructure spend inefficiencies."** This step is entirely optional and never blocks progress to Step 8 — decline and
move on if the user isn't interested.

If the user opts into one or both personas, spawn `architecture-designer:architecture-reviewer` again — once per chosen
persona — with the same inputs Step 7 already assembled (requirements summary, all diagram code), plus one additional
line of context:

- **Security persona**: "Additional focus: evaluate this design specifically from a Security persona's perspective —
  weight findings toward authentication/authorization gaps, data exposure, secrets handling, perimeter controls, and
  compliance-flagged items, even ones the standard review would rate Minor."
- **Cost persona**: "Additional focus: evaluate this design specifically from a Cost persona's perspective — weight
  findings toward over-provisioned tiers, redundant managed services, and infrastructure choices in tension with Stage
  3's budget constraint or `stage5.costEstimate`."

These persona passes are **informational, not gating**: present each persona's findings to the user alongside the Step 7
report, but do not spawn `architecture-fixer` or re-run the reviewer–fixer cycle procedure for them — a persona finding
the user wants acted on is folded into Step 9's revision flow like any other requested change, not auto-fixed here. Do
not write persona findings into `progress.reviewCycles` or `last-review.md` — those are reserved for the binding Step 7
cycle; note the persona findings in the conversation and, if the user asks to act on one, treat it as a Step 9 revision
request.

---

## Step 8 — Browser Preview

1. **Confirm `diagrams.json` is current** at `docs/architecture-designer/diagrams.json` — written incrementally through
   Stage 6d, possibly updated by architecture-fixer in Step 7. Must follow the schema in `references/diagrams-guide.md`
   section "`diagrams.json` Schema"; re-write it if step 2 flags issues.

2. **Validate diagrams**: run `node <scripts_dir>/validate-diagrams.mjs`. If it exits non-zero or prints
   `VALIDATION FAILED`, fix the flagged issues and re-write `diagrams.json` — do this regardless of `DEGRADED MODE`,
   which is not itself a pass/fail signal and can co-occur with a real failure. Do not proceed until it exits 0 with
   either `VALIDATION PASSED` (one or more diagrams, all structurally sound) or `WARNING: diagrams array is empty` (a
   legitimate outcome when Stage 6d's "all diagrams are optional" applies and none were selected — this is not a stuck
   gate). If `DEGRADED MODE` still appears once passed, the real syntax parser was unavailable and some diagrams were
   only checked heuristically — proceed, but tell the user: "Diagram validation ran in degraded mode (parser
   dependencies not installed in `scripts/`) — some syntax errors may not have been caught. Run `npm install` in the
   plugin's `scripts/` directory for full validation coverage."

3. **Find a free port**: run `python3 <scripts_dir>/find-port.py`. Capture stdout; report the error if it exits
   non-zero.

4. **Start the preview server** in the background: `node <scripts_dir>/preview-server.mjs <port>`. It opens the browser
   automatically — tell the user the URL (e.g., `http://localhost:3000`).

5. **Do NOT create a stop-server script.** Leave the server running.

6. Record `progress.lastCompletedStep = "step8"` per `references/session-schema.md` section "Recording
   `progress.lastCompletedStep`".

---

## Step 8.5 — Visual Rendering Verification (optional, best-effort)

`validate-diagrams.mjs` above only checks Mermaid *syntax* (via a real parser when available) plus text-based heuristics
for overlap risk (subgraph depth, node count, label length) — it cannot confirm whether nodes actually collide once
rendered, since Mermaid's real layout engine doesn't run under the script's jsdom environment. This step closes that gap
using an actual browser, when one is available — it never blocks progress to Step 9.

Spawn the `architecture-designer:visual-diagram-verifier` agent with the preview URL from Step 8 and the diagram list
(`id` + Mermaid type keyword) from `docs/architecture-designer/diagrams.json`. Do not ask the user before spawning it —
just run it and report the outcome.

- **If it reports `SKIPPED`** (neither chrome-devtools-mcp nor firefox-devtools-mcp installed): tell the user once,
  briefly — "Real rendered-overlap checking isn't available in this environment (no browser-automation plugin
  installed); relying on the syntax/heuristic checks above." — and proceed straight to Step 9. This is the expected
  outcome in most environments, not a failure.
- **If it reports `VISUAL CHECK PASSED`**: note it briefly and proceed to Step 9.
- **If it reports `VISUAL CHECK FOUND OVERLAPS`**: spawn `architecture-designer:architecture-fixer` with these findings
  reframed as Major findings (same shape as an ordinary architecture-reviewer finding: diagram ID, the two overlapping
  elements' labels, and the remediation suggestion already in the report), the path to
  `docs/architecture-designer/diagrams.json`, and the requirements summary. After it applies fixes, re-spawn
  `visual-diagram-verifier` **once** to confirm. If overlaps remain after that one re-check, note them to the user and
  proceed to Step 9 anyway — this check is informational, not a hard gate like the Step 7 reviewer–fixer cycle, so it
  does not apply that section's 3-cycle procedure or write to `progress.reviewCycles`/`last-review.md`.

This step is not tracked in `progress.lastCompletedStep` and is not resumed automatically — a session resuming past Step
8 skips straight to Step 9 without re-running it. Run it again manually at any time by asking for it, since it's a
point-in-time check against whatever `diagrams.json` currently contains, not a persisted pipeline gate.

---

## Step 9 — User Confirmation

**Maintenance note**: `review/SKILL.md` steps 4a/4b mirror this step's "if X changed, re-run Y" logic for the revision
case (same drivers, NFRs, domain edge cases, Web3/offline-first tracks, IaC/CI-CD, domain model, cost estimate) —
`review/SKILL.md` step
4d.5 covers the equivalent Low-Level Design re-run separately, and step 4d.6 covers the equivalent Test Strategy
re-run separately, since LLD (Step 10 below) and Test Strategy (Step 10b below) haven't happened yet at this point in
the first-time design flow and so have nothing to mirror here. The two are maintained as parallel prose rather than one
shared procedure — if a rule below changes (a new re-run trigger, a new track), apply the same change to
`review/SKILL.md`
steps 4a/4b, and vice versa.

After opening the browser, ask:

> **"Does this architecture design meet your needs, or is there anything you would like to revise?"**

If the user requests revisions:

- Identify the affected stage, return to it, ask the relevant questions again, update the answers
- **If Stage 1 is revised**: re-confirm `description` too — it can go stale once goal, stakeholders, or pain points
  change. Re-draft it (or accept the user's rewrite) the same way as the original confirmation.
- **If Stage 2 is revised** (an NFR changed, was added, or was removed): re-evaluate `stage2.qualityAttributeScenarios`
  for the changed set per `references/quality-driven-design-guide.md`, then re-evaluate `architecturalDrivers` against
  the updated scenarios — a driver citing a `QAS-n` ID that no longer exists must be dropped or re-pointed to its
  replacement. If `architecturalDrivers` changes as a result, also re-run the Trade-off and Risk Analysis pass (same
  procedure as the Stage 5 bullet below), since a Stage 5 decision may have been justified against a driver that no
  longer applies.
- **If a functional requirement added or changed by this revision matches a new `references/domain-edge-cases-guide.md`
  category not already covered**: read that guide and ask the newly-matched category's targeted questions, then append
  the answers to `session.json`'s `stage2.domainEdgeCases` — append, don't overwrite the whole array, since existing
  categories' answers are still valid and unrelated to this revision's scope.
- **If Stage 4 is revised** (a capacity number changed): re-run the Cost Estimation pass per
  `references/cost-estimation-guide.md` against the revised numbers, overwriting `stage5.costEstimate` in full — a
  changed user-count or data-volume figure changes the sizing basis for every component in the breakdown.
- **If Stage 5 is revised**: re-run the `agentTools` check too — a changed stack changes which tools match. Overwrite
  `agentTools` in full with the new result (per `references/session-schema.md`), not merge with the old list. Also
  re-evaluate the Web3 track: if the revised stack now names a distributed-ledger platform where it didn't before, work
  through `references/web3-guide.md`'s dimensions and write the new `web3` key; if the revised stack dropped its
  decentralized component, delete the `web3` key entirely (do not leave a stale one behind); if it's still decentralized
  but the target network or a dimension's answer changed, re-run the dimensions and overwrite `web3` in full — same
  "overwrite, don't merge" rule as `agentTools`. Apply the same three-way logic to the offline-first track and its
  `offlineFirst` key, using `references/offline-first-guide.md` — if the offline-first status changed (newly added,
  removed, or an existing answer changed), re-spawn `database-designer` so the offline-sync schema columns
  (`references/offline-first-guide.md` section 4) are added or removed to match. Also re-run the Trade-off and Risk Analysis pass per
  `references/quality-driven-design-guide.md` against the revised decisions, overwriting `tradeoffAnalysis` and
  `riskRegister` in full — same "overwrite, don't merge" rule. Also re-run the Cost Estimation pass per
  `references/cost-estimation-guide.md` against the revised decisions and/or capacity numbers, overwriting
  `stage5.costEstimate` in full — same "overwrite, don't merge" rule.
- **If Stage 6a's domain modeling is affected** (new bounded contexts, changed aggregate boundaries): re-run the
  domain-modeling step per `references/ddd-guide.md` and overwrite `domainModel` in full, then re-spawn
  `database-designer` so the schema reflects the updated aggregate boundaries.
- **If the cloud/infrastructure provider, IaC tool, or CI/CD platform changes** (whether directly requested or as a
  consequence of a Stage 5 stack revision): read `references/iac-guide.md` and/or `references/cicd-guide.md` as
  applicable and overwrite `session.json`'s `stage6b`/`stage6c` in full to match — the same "overwrite, don't merge"
  rule as `agentTools`/`web3`/`offlineFirst` above. Regenerate the deployment/infrastructure and CI/CD pipeline diagrams
  to match.
- Regenerate the affected diagrams and re-run the architecture reviewer (step 7) — this may spawn architecture-fixer,
  which writes `diagrams.json` directly
- Update `diagrams.json` with the revised diagrams (skip if the fixer already wrote it during the reviewer re-run)
- Re-run `node <scripts_dir>/validate-diagrams.mjs` — same gate as Step 8; fix flagged issues and re-validate before
  continuing. Do not tell the user to refresh until it passes.
- Optionally re-run Step 8.5 against the revised diagrams — the same "informational, never blocking" treatment applies
  on a revision as on the first pass.
- Tell the user to refresh their browser, then ask the confirmation question again

Repeat until the user confirms the design is correct. Once confirmed, record `progress.lastCompletedStep = "step9"` per
`references/session-schema.md` section "Recording `progress.lastCompletedStep`".

---

## Step 10 — Low-Level Design

**Read `references/lld-guide.md`** before starting this stage — it has the exact format and rules for each artifact
group below.

Derive the LLD directly from the confirmed HLD diagrams — do not invent endpoints or rules that are not visible in the
sequence, class, or business-process diagrams.

**Resuming**: if `session.json`'s `lld` key already has a non-empty `confirmedGroups` list (a previous session died
partway through this step), determine the applicable group list first — all five groups for microservices/event-driven
architectures (per stage5's confirmed `architecturePattern`), or the four groups excluding `interServiceContracts` for a
monolith/modular monolith, since that group is legitimately never confirmed (and never added to `confirmedGroups`) for
those patterns. Then skip straight to the first *applicable* group not yet in `confirmedGroups`, in the fixed order
below, rather than re-confirming groups already done. (Checking positional order 1–5 without this filter would wrongly
treat a monolith's legitimately-skipped group 4 as "not yet reached" even when group 5 is already confirmed and the LLD
is actually complete.)

Work through the five artifact groups in order, presenting each to the user and confirming (or revising) before moving
to the next: **(1) API contracts** — one entry per endpoint visible in the sequence diagrams; **(2) business rules** —
one entry per non-trivial operation, skipping simple CRUD; **(3) DTOs** — only for complex or shared bodies used by
multiple endpoints; **(4) inter-service contracts** — only for microservices/event-driven architectures, omitted
entirely for monoliths; **(5) error catalog** — derived from errors already referenced above, never invented fresh.

**Business rules design-principle check**: while writing group (2), read `references/design-principles-guide.md`'s DRY,
YAGNI, and Tell-Don't-Ask sections — a rule whose `Logic` duplicates steps already written for another rule should
extract a shared, named sub-rule instead of restating them (DRY); a rule that reads another object's state to make a
decision externally should delegate that decision to the owning object instead (Tell, Don't Ask); a rule that introduces
a configuration axis with no second confirmed variant behind it should model the concrete case directly (YAGNI).

**Business rules clean-code check**: in the same pass, read `references/clean-code-guide.md`'s "Functional core,
imperative shell" section — phrase each rule's `Logic` as pure, ordered steps with no persistence or I/O concern folded
in (persistence belongs in `Post-conditions`, already a separate section per `references/lld-guide.md`); a rule whose
steps read at inconsistent levels of abstraction, or that names more than a handful of steps, is a candidate to extract
a named sub-rule, mirroring group (2)'s DRY check above.

**Business rules GoF-pattern check**: also in the same pass, read `references/design-patterns-guide.md` Part 2 — a rule
whose `Logic` describes several related operations sharing the same overall sequence but differing in one step (Template
Method), or an action that must be queued, logged, or undone as a discrete unit (Command), or an ordered sequence of
independent handlers each deciding whether to act (Chain of Responsibility), should name the pattern explicitly in the
rule's description so `architecture-implementer` generates the matching class shape rather than a flat procedural
function. Most rules match no pattern at all — name one only when the signal is actually present, per that guide's
Why-this-matters section on misuse.

**Business rules transaction-boundary check**: also in the same pass, apply `references/lld-guide.md` section 2's
"Transaction boundary" rule — for a rule whose `Post-conditions` list two or more writes, read
`references/transaction-guide.md` and state whether they commit as one database transaction (naming the
concurrency-control strategy if `database-designer` flagged the entity high-contention) or, if the writes legitimately
span two aggregates/services, rewrite the rule as an explicit Saga (ordered steps, each with its own local transaction
and compensating transaction) per that guide's section 4.

**Persist each group as soon as it's confirmed** — do not wait until all five are done. After each group is confirmed,
write it into `session.json`'s `lld` key (create it if absent) and add that group's name to `lld.confirmedGroups` —
read-fresh-modify-write-whole, same discipline as every other `session.json` write. For a monolith where group 4 is
skipped entirely, do not add `interServiceContracts` to `confirmedGroups` and omit that field from `lld`.

After the user confirms all applicable groups, record `progress.lastCompletedStep = "step10"` per
`references/session-schema.md` section "Recording `progress.lastCompletedStep`" — the complete LLD is now in
`session.json`'s `lld` key, ready to include in the architecture document.

---

## Step 10b — Test Strategy

**Read `references/test-strategy-guide.md`** before starting — it has the exact derivation rules and format for each
part below.

Derive a test plan from data already confirmed, never inventing a target with no source: **(1) test pyramid** — unit,
integration, contract (microservices/event-driven only), and end-to-end scope, sized to the project; **(2) load and
performance testing** — targets taken directly from Stage 2's Performance/Scalability Quality Attribute Scenarios and
Stage 4's capacity numbers, plus a named tool for the confirmed stack; **(3) resilience and chaos testing** — one
scenario per resilience pattern actually named in Stage 5 item 10, omitted entirely for a monolith with no external
dependencies (the same skip condition `references/resilience-guide.md` itself uses); **(4) security testing** — a
verification checklist derived from the LLD error catalog's auth-related entries, Stage 5 item 11's rate-limiting rules,
and Stage 2's compliance-flagged NFRs — not a substitute for a full security audit; point the user at this plugin
ecosystem's `/audit`/`/audit-diff` tooling for that; **(5) UAT** — one Given/When/Then acceptance scenario per core
feature (the same set `document-template.md` section 2 lists).

Present the plan, discuss, adjust, and confirm before continuing. Once confirmed, write it to `session.json`'s top-level
`testStrategy` key (create it) — see `references/session-schema.md`. Record
`progress.lastCompletedStep = "step10b"` per that file's section "Recording `progress.lastCompletedStep`".

---

## Step 11 — Save Architecture Document

Once the user confirms, save the document to:

```
docs/architecture-designer/architecture/{yyyymmdd}-{topic}.md
```

- `{yyyymmdd}`: today's date as 8 digits in ISO order — use JavaScript `Date` to format: year (4-digit) + month
  (2-digit, zero-padded) + day (2-digit, zero-padded). Example: `20260705` for 5 July 2026. **Never use the shell `date`
  command.** This ISO-style order ensures files sort chronologically when listed alphabetically.
- `{topic}`: the project/application name in kebab-case (lowercase, hyphens, no spaces)
- If a file with this name already exists, append `-2`, `-3`, etc. until the filename is unique

After saving, append `{ "path": "<absolute path of the saved file>", "createdAt": "<current ISO timestamp>" }` to
`session.json`'s top-level `"documents"` array (create it if absent; backfill `schemaVersion`/`project`/`description` at
the same time if the file predates them, per the tolerant-read rule in `references/session-schema.md`). This lets
`/architecture-designer:implement` find the latest document — the last entry's `path` — without asking.

**The document must begin with this metadata table on line 1:**

```markdown
| Date       | Version | Status | Reason | Previous Document |
|------------|---------|--------|--------|-------------------|
| {dd-mmm-yyyy} | 1.0     | Draft  | -      | -                 |
```

- `dd-mmm-yyyy` format: day is zero-padded (e.g., `05`), month is 3-letter capitalized abbreviation (`Jan`, `Feb`,
  `Mar`,
  `Apr`, `May`, `Jun`, `Jul`, `Aug`, `Sep`, `Oct`, `Nov`, `Dec`), year is 4 digits. Example: `05-Jul-2026`.

**Document body sections (in order)**: follow `references/document-template.md` — eleven fixed sections from Project
Overview through Low-Level Design, each pulling from the corresponding stage or sub-agent output (section 2 "Core
Features" derived from the same Stage 2 functional requirements Stage 6d's "Core feature coverage requirement" already
treats as core features, cross-referenced against the dedicated sequence diagram each one already has in section 7;
section 8 from `session.json`'s `progress.reviewCycles.database.approvedOutput`; section 11 from the `lld` key), plus a
12th conditional "Decentralized Architecture Considerations" section when the Web3 track was active, a 13th conditional
"Offline-First Considerations" section when the offline-first track was active, a required 14th "Domain Model (DDD)"
section from the `domainModel` key, a required 15th "Trade-off and Risk Analysis" section from the
`stage5.tradeoffAnalysis` and `riskRegister` keys, a required 16th "Cost Estimation" section from `stage5.costEstimate`,
a required 17th "Test Strategy" section from the `testStrategy` key, and a required 18th "Architecture Decision Records"
section (a pointer table only — see below) from the `adrs` key.

**Generate Architecture Decision Records** (required, immediately after the document above is saved): read
`references/adr-guide.md` and, for each Stage 5 decision that guide's "Which decisions get an ADR" criteria selects,
write one ADR file to `docs/architecture-designer/adr/{NNNN}-{slug}.md` and append its entry to `session.json`'s
top-level `adrs` array (create it if absent) — per that guide's "Generating ADRs" procedure. Do this before Step 12, so
document-reviewer's ADR-pointer-table check has the `adrs` array populated to check the document's section 18 against.

Record `progress.lastCompletedStep = "step11"` per `references/session-schema.md` section "Recording
`progress.lastCompletedStep`".

---

## Step 12 — Document Review

Spawn the `architecture-designer:document-reviewer` agent with the path to the saved document, the requirements summary
(per `references/session-schema.md` section "Requirements-summary scope for sub-agent spawns"), and the expected
filename. Wait for the verdict. (`document-reviewer`/`document-fixer` read `references/document-review-checklist.md`
directly for the exact F1–F7/C1–C19 criteria — no need to read it here.) **Regardless of verdict**, apply
`references/session-schema.md` section "Reviewer–fixer cycle procedure" step 0 as soon as the verdict is received
(records the verdict/cycle/`documentHash` into `progress.reviewCycles.document` and
`docs/architecture-designer/last-review.md`; this runs even on a clean first-try pass, not only on failure).

**If DOCUMENT REVIEW FAILED**: continue with that section's steps 1–4: spawn `architecture-designer:document-fixer` with
the document path, the review report, the requirements summary, and the path to
`docs/architecture-designer/diagrams.json`. After it overwrites the document, rename the file first if the fixer's log
says it must be renamed (F6), then re-spawn `document-reviewer` and verify (binary verdict — cycle until DOCUMENT REVIEW
PASSED).

**Once it passes**: update the `Status` column in the metadata table from `Draft` to `Approved`. The table should now
read:

```
| {date} | 1.0 | Approved | - | - |
```

Record `progress.lastCompletedStep = "step12"` per `references/session-schema.md` section "Recording
`progress.lastCompletedStep`".

---

## Step 13 — Implementation Offer

After the document is approved, ask:

> **"The architecture document is approved. Would you like me to proceed with implementation — generating the project
skeleton, data models, and infrastructure files based on this document?"**

If yes: scan the working directory for signs of an existing project, per `references/session-schema.md` section
"Existing-project scan categories".

**If files already exist**: summarize what was found and ask the question in `references/session-schema.md` section
"Merge-strategy question". **If the scan finds nothing**: no question needed — proceed as a fresh start into an empty
project.

Before spawning, resolve the applicable remediation plan per `references/session-schema.md` section "Finding the
applicable remediation plan", using the approved document's path (its checkbox-per-finding format is defined in
`references/remediation-plan-guide.md` — a remediation plan is only ever written by the `review` skill's drift-fix
flow, never by this skill, so there is nothing to author here, only to locate and pass along). Then run
`references/session-schema.md` section
"Resumable-plan detection procedure" using the approved document's path as `{document}` to produce the **Previous plan
path**, if the user chooses to resume.

Then follow `references/session-schema.md` section "Implementation-planner → architecture-implementer spawn sequence" to
spawn `architecture-designer:implementation-planner` and, once its plan is confirmed, `architecture-designer:architecture-implementer`, passing these six inputs:

- The path to the approved document
- **Existing project summary** — translated into the agent's expected strategy label: `Fresh start (empty project)` if
  nothing was found; `Merge` if the user chose (a); `Fresh start (existing project)` if the user chose (b);
  `User-described layout` if the user chose (c)
- **Technology stack** — read from the approved architecture document's Technology Decisions section (section 6), the
  same source `implement/SKILL.md` Step 3 and `review/SKILL.md` step 4h use, rather than `stage5` directly — this is a
  first-time save with no revision in between, so the two agree here, but reading the document keeps this input
  consistent with the other two spawn sites
- **Agent tools** (optional) — `session.json`'s `"agentTools"` array, if present and non-empty
- **Remediation plan path** — resolved above, if it exists on disk and wasn't ruled out
- **Previous plan path** — the resumed plan's `path`, if the user chose to continue (omit otherwise)

If the user says no: let them know they can run `/architecture-designer:review` at any time to revisit and revise the
architecture.

Either way, record `progress.lastCompletedStep = "step13"` per `references/session-schema.md` section "Recording
`progress.lastCompletedStep`" — this pipeline pass is complete.

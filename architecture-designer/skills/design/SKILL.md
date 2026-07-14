---
name: design
description: This skill should be used when the user wants to design a new application's architecture or infrastructure — says "design my architecture", "help me plan the architecture", "create architecture diagrams", "I need to plan a new system", or is starting a new project and needs a structured design process. Also trigger when the user mentions HLD, LLD, API contracts, or system design. Guides from requirements gathering through capacity planning, technology selection, diagram generation, low-level design, document saving, and code skeleton implementation.
allowed-tools: ["Read", "Write", "Edit", "Bash", "Agent", "WebSearch"]
---

# Architecture Designer — Main Design Workflow

This skill guides the user through a six-stage design process plus seven post-design steps (review, preview, LLD, document save, implementation), ending with browser-rendered Mermaid diagrams, low-level design artifacts, a reviewed and approved document, and an optional code skeleton.

Always use this skill for new architecture design, even if the user has already started describing their system in the conversation — do not skip straight to diagram generation or freeform advice.

**Scripts live two levels up from this file:** `../../scripts/find-port.mjs` and `../../scripts/preview-server.mjs`. At runtime, resolve these paths by taking the absolute path of this SKILL.md and navigating up two directories to find `scripts/`.

---

## How to run this workflow

**Before starting — check for an existing session**: look for `docs/architecture-designer/session.json`. If the file already exists, read it and ask the user:

> "I found an existing design session for **[project name from the file, or 'a previous project' if unnamed]** — [description from the file, or omit this clause if unset]. Would you like to continue where we left off, or start a new design from scratch?"

If they choose to continue: read the completed stages from `session.json`, brief the user on where the previous session left off, and resume from the first incomplete stage. If they choose to start fresh: delete `docs/architecture-designer/session.json` (and `docs/architecture-designer/diagrams.json` if present) before proceeding.

**Legacy-session backfill check**: if resuming and `stage1`–`stage5` are already confirmed but `schemaVersion`, `project`, or `description` is missing (a v1 file, or a v2 file predating the `description` field), backfill the missing field(s) immediately here — do not wait for Step 11. Synthesize `description` from the existing `stage1` content per `references/session-schema.md`'s backfill rule and write it silently (no re-confirmation needed, same rationale as the Step 11 backfill). Resuming straight into Stage 6 or later without this backfill will otherwise fail the Session completeness gate with no instructed way to recover, since Stage 1 — the only other place `description` is normally written — has already been completed and won't run again.

Work through the six stages in order (Stages 1–6), then follow Steps 7–13. At the end of each stage, summarize the user's answers and ask:
> "Does this summary look correct? Shall we move to the next stage?"

Do not proceed until the user confirms. After each stage is confirmed, persist the stage summary to disk: write `docs/architecture-designer/session.json` (create the `docs/architecture-designer/` directory if it does not exist). The file is a JSON object with one key per completed stage, e.g. `{ "stage1": { ... }, "stage2": { ... }, ... }` — append each new stage's summary when the user confirms. Do not rely on working memory alone — it degrades over long sessions and is invisible to sub-agents, which must receive `session.json`'s contents directly rather than depend on conversation history they cannot access.

**session.json write discipline**: Write the exact text the user confirmed, not a fresh paraphrase — sub-agents must work from confirmed facts, not a re-interpretation that could silently diverge from intent.

**Canonical session.json schema**: read `references/session-schema.md` before writing to or reading anything beyond the stage keys below. It defines the fixed top-level keys, the array-of-objects shape for `documents`/`remediationPlans`/`implementationPlans` (each entry carries `path`, links like `document`/`remediationPlan`/`supersedes`, and `createdAt` — not a bare path string), which top-level keys (`schemaVersion`/`project`/`description`) are guaranteed present under this schema (v2) versus a legacy (v1) file, how to resolve links between the arrays instead of assuming array-position pairing, and the single-writer-per-key and no-CAS write discipline every reader/writer must follow.

**`description` is required**: at the first session.json write (Stage 1 confirmation, below), write `schemaVersion: 2`, `project`, and `description` together with `stage1` — see `references/session-schema.md` for what `description` must contain and its two valid sources (user-written vs. auto-generated), and `references/discovery-questions.md` Stage 1 for how to surface an auto-drafted description for approval. Do not proceed to Stage 2 with `description` empty or missing; if the Stage 1 answers are too thin to synthesize one and the user hasn't supplied their own, ask a brief follow-up first.

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

**Read `references/tech-stacks.md` before making recommendations.** It contains concrete options organized by architecture pattern, scale tier, team size, cloud provider, database type, auth approach, and frontend — use it to ground your suggestions in real technology names rather than abstract categories.

Based on everything gathered in stages 1–4, propose:

1. **Architecture pattern**: Monolith / Modular Monolith / Microservices / Serverless / Event-driven. Justify based on team size, complexity, and scale targets. Note: for small teams and early-stage projects, a modular monolith is almost always the right starting point.
2. **Backend language and framework**: Justify based on team competencies and NFRs. Name the specific framework (e.g., "Fastify 5", not just "Node.js").
3. **Frontend**: If applicable, framework recommendation with version.
4. **Database type(s)**: SQL vs NoSQL vs polyglot — specific engine recommendation. This is a high-level recommendation — the database-designer agent will design the full schema in stage 6.
5. **Infrastructure provider and key services**: cloud provider, compute option (containers vs VMs vs FaaS), CDN, load balancer. Name the specific managed services (e.g., "AWS ECS Fargate", not just "containers on AWS").
6. **Key supporting services**: message queue (if async needed), cache, search index, object storage — only recommend if required by the functional requirements. Name specific technologies with versions.
7. **Authentication approach**: library, managed service, or self-hosted identity provider — justify based on user roles, security requirements, and team capacity.
8. **Observability strategy**: Logging platform (structured logs → aggregator: ELK, Grafana Loki, Datadog, CloudWatch). Metrics and dashboards. Distributed tracing if multiple services or async flows are involved (OpenTelemetry + Jaeger/Tempo). Alerting destination and escalation path. Recommend only what the system's scale and operational maturity actually require — a monolith with a small team may need only structured logging and a single dashboard.
9. **Disaster recovery and resilience**: RPO (maximum acceptable data loss) and RTO (maximum acceptable downtime), derived from the availability NFR in stage 2. Backup strategy: automated snapshots, point-in-time recovery, or cross-region replication. Failover approach: manual, automated active-passive, or active-active.

Every recommendation must cite a specific reason from stages 1–4 (e.g., "PostgreSQL 16 because the team has 3 years of PostgreSQL experience [stage 3], the data is relational [stage 2], and the estimated 300 TPS write load is within its range with PgBouncer [stage 4]").

Present recommendations, discuss with the user, adjust if needed, confirm, then proceed.

**Version grounding**: Every recommended technology must include a specific version number. Before citing a version: (1) if WebSearch is available, verify the current stable release of each technology before writing it down; (2) if WebSearch is unavailable, write the version as **"latest stable — verify at implementation time"** rather than citing a version number from memory that may be stale.

**Cloud service and compliance grounding**: The same discipline applies to cloud managed-service names (service tiers, feature availability, regional presence) and to compliance-specific claims (which controls a standard requires, whether a managed service holds a certification). If WebSearch is available, verify before asserting. If not, label the claim **"⚠ verify before relying"** rather than stating it as established fact.

---

## Stage 6 — Architecture and Infrastructure Design

**Session completeness gate**: before spawning any sub-agent, run `node <scripts_dir>/validate-session.mjs`. It checks both the required top-level fields (`schemaVersion`, `project`, `description`) and stages 1–5. If the check fails, the listed fields and/or stages must be completed first — do not proceed to 6a or any later step until `SESSION CHECK PASSED`. A missing top-level field on an otherwise-complete resumed session is the legacy-backfill case above, not a missing stage.

### 6a. Database design (delegate to sub-agent)

Spawn the `architecture-designer:database-designer` agent. Pass it:
- The complete requirements summary — read this from `docs/architecture-designer/session.json` (the confirmed stages 1–5 data written to disk at each confirmation). Do not rely solely on conversation memory.
- The domain entities extracted from the functional requirements
- The access patterns (how data will be read and written, from the business processes)

Wait for the agent to return ERD, index plan, engine recommendation, and secure connection config.

Then spawn `architecture-designer:database-reviewer`. Pass it:
- The full database-designer output
- The requirements summary (stages 1–5)

If the reviewer returns `DATABASE REVIEW FAILED`: spawn `architecture-designer:database-fixer` with the review report, the database-designer output, the requirements summary, and the path to `docs/architecture-designer/diagrams.json`. The fixer writes the corrected ERD and indexPlan directly into `diagrams.json` **and returns the corrected schema, ERD, index plan, and connection config as text** — replace the database-designer output held in context with this corrected text; it is what gets embedded in Step 11, not the original. If the fix log contains a **"Proposed Additions"** section, present each item to the user for confirmation before continuing (same pattern as architecture-fixer's Proposed Additions in Step 7) — a rejected addition does not resolve the reviewer finding it addresses, so ask the user how to proceed on those before re-spawning the reviewer. After it completes, re-spawn `architecture-designer:database-reviewer` to verify. Repeat until `DATABASE REVIEW PASSED`, **up to a maximum of 3 reviewer–fixer cycles**. If it still returns `DATABASE REVIEW FAILED` after 3 cycles, stop the loop, present the remaining findings to the user verbatim, and ask for their guidance rather than cycling further.

**The database design incorporated into the document (Step 11, §7 per `references/document-template.md`) and the diagram set must be the final approved version — the database-fixer's corrected text if any fixer cycle ran, or the original database-designer output if it passed review with no fixes.** Never fall back to the original output after a fixer cycle has produced a corrected version; the two must never diverge.

### 6b. Infrastructure as Code (IaC)

**Read `references/iac-guide.md` before making recommendations.**

Based on the cloud provider chosen in Stage 5 and the infrastructure shape emerging from the capacity plan, define the IaC approach. Cover five points, in order:

1. **Tool selection** — Terraform, OpenTofu, Pulumi, AWS CDK, CloudFormation, or Bicep. Justify based on cloud provider, team language preference, and multi-cloud requirements. See `iac-guide.md` § 1 for decision rules.
2. **State backend** — remote backend type, bucket/container naming convention, locking mechanism. Never local state.
3. **Module breakdown** — list each module (network, compute, database, cache, storage, messaging, monitoring) and what it provisions. Note any environment-level size differences (e.g., prod uses Multi-AZ, dev uses single-AZ). Omit modules for services not in scope.
4. **Environment strategy** — workspace-per-env, directory-per-env, or separate repos. Default: directory-per-environment. Justify the choice.
5. **Drift detection** — CI plan runs on every PR, scheduled nightly scans, or managed drift detection (Terraform Cloud / HCP Terraform). Pick what matches the team's operational maturity.

Present the IaC plan, discuss any open questions (e.g., existing AWS account structure, Terraform Cloud subscription), adjust, and confirm before continuing.

After confirmation, append the confirmed IaC decisions to `docs/architecture-designer/session.json` under the `"stage6b"` key (create or overwrite). Use the exact text the user confirmed — do not paraphrase.

---

### 6c. CI/CD Pipeline Design

**Read `references/cicd-guide.md` before making recommendations.**

Based on where the code is hosted, the deployment target, and the architecture pattern (monolith vs microservices vs serverless), design the delivery pipeline. Cover six points:

1. **Platform selection** — GitHub Actions, GitLab CI, CircleCI, AWS CodePipeline, Argo CD, etc. Justify based on code host and deployment target. See `cicd-guide.md` § 1 for decision rules. For Kubernetes targets, consider a split: any CI platform for the build leg, Argo CD or Flux for the CD leg.
2. **Pipeline stages** — list each stage (lint, unit test, build, integration test, security scan, push artifact, deploy per environment) with its trigger and gate condition. Omit stages the project does not need. Use the standard template in `cicd-guide.md` § 2 as a starting point.
3. **Branching strategy** — trunk-based development, GitHub Flow, or GitFlow. Default: GitHub Flow. Justify based on team size and release cadence.
4. **Environment promotion** — trigger and gate for each environment (dev → staging → prod). Prod requires a manual approval gate by default. Document the rollback procedure.
5. **Secret injection** — how credentials reach the pipeline. Prefer OIDC over long-lived keys. Name the secret store (GitHub Secrets, AWS Secrets Manager, Vault, etc.) and the injection mechanism. Confirm no secrets are hardcoded in workflow files or committed to the repo.
6. **Artifact management** — container registry, image tagging scheme (git SHA for traceability), retention policy.

Present the CI/CD plan, discuss, adjust, and confirm before continuing.

After confirmation, append the confirmed CI/CD decisions to `docs/architecture-designer/session.json` under the `"stage6c"` key (create or overwrite). Use the exact text the user confirmed — do not paraphrase.

---

### 6d. Diagram selection and generation

Generate Mermaid diagrams relevant to the project. **All diagrams are optional** — select only those that add clarity for this specific project. After generating, tell the user:
- Which diagrams were created and why
- Which diagrams were skipped and why (e.g., "State diagram skipped — no entities with complex status lifecycles identified")

**Read `references/diagrams-guide.md` before generating any diagram.** It contains: the exact attribute format for ERD, full templates for each diagram type including CI/CD pipeline, common mistakes to avoid, real-world examples, and anti-overlap rules (ELK layout, label length, C4 config). Don't rely on memory for Mermaid syntax — check the guide.

**Available diagram types** (criteria for when to create each):

| Diagram          | Mermaid type                          | Create when                                  |
|------------------|---------------------------------------|----------------------------------------------|
| Use case         | `flowchart LR`                        | 2+ user roles with distinct feature sets     |
| Business process | `flowchart TD`                        | Complex workflow with 2+ decision branches   |
| ERD              | `erDiagram`                           | Any SQL database — always                    |
| Sequence         | `sequenceDiagram`                     | Always: auth flow + primary transaction      |
| Class            | `classDiagram`                        | Non-trivial domain model with business rules |
| State            | `stateDiagram-v2`                     | Any entity with 3+ lifecycle states          |
| C4 Context       | `C4Context`                           | Any external integration or 2+ user types    |
| C4 Container     | `C4Container`                         | 2+ deployable components                     |
| Deployment       | `flowchart TD` or `architecture-beta` | Cloud or multi-server deployment             |
| CI/CD pipeline   | `flowchart TD`                        | 2+ deployment environments or staged release |

**Production-ready requirement**: For any system targeting production workloads, the deployment / infrastructure diagram must show: (1) at least one observability sink (log aggregator, APM agent, or metrics exporter named in Stage 5); (2) at least one DR component (database replica, automated backup target, or cross-region failover). If either is absent the `architecture-reviewer` will raise it as a Major finding.

**ERD special requirement**: Since `erDiagram` has no native index notation, mark indexed columns via attribute comments (`"idx"`) and include an index list table (from the database-designer agent) as a markdown table immediately after the ERD mermaid block. See `references/diagrams-guide.md` for the exact format.

### 6e. Mermaid compatibility and diagrams.json

Read `references/diagrams-guide.md` § "Mermaid v11.16 Compatibility Rules" and § "Preventing Node Overlap" before finalizing diagram code — they cover required syntax (e.g. `flowchart` not `graph`, `architecture-beta` icon slots) and anti-overlap rules (ELK layout, `align` directives, label length, C4 layout config).

After applying those rules and finalizing all diagram code, **immediately write `docs/architecture-designer/diagrams.json`** following the schema in `references/diagrams-guide.md` § "`diagrams.json` Schema" (create `docs/architecture-designer/` if needed). This must happen before Step 7 — the architecture-fixer reads and updates the file in place during the review cycle and will fail if the file does not exist.

---

## Step 7 — Architecture Review (BEFORE preview)

Spawn the `architecture-designer:architecture-reviewer` agent. Pass it:
- The full requirements summary — read from `docs/architecture-designer/session.json` (confirmed stages 1–5, plus IaC decisions from stage6b and CI/CD decisions from stage6c if present). Do not rely solely on conversation memory.
- All generated Mermaid diagram code, labeled by type

Wait for the review report.

**If the report contains CRITICAL or MAJOR items**: spawn `architecture-designer:architecture-fixer`. Pass it:
- The review report
- The path to `docs/architecture-designer/diagrams.json`
- The requirements summary

After the fixer updates `diagrams.json`:
- If the fix log contains a **"Proposed Additions"** section, present each item to the user for confirmation before continuing. Add confirmed items to `diagrams.json`; discard rejected ones.
- **A rejected proposed addition does not resolve the finding that generated it.** Note which Critical/Major finding each rejected addition was tied to. Do not silently re-enter the reviewer–fixer loop expecting the same finding to disappear — the fixer cannot close it without the addition. Ask the user directly: accept the residual risk and note it in the document, or describe an alternative fix for the fixer to apply next cycle. Only re-spawn the reviewer once the user has chosen one of these for every rejected addition.
- Re-spawn `architecture-designer:architecture-reviewer` to verify.
- Repeat until the reviewer's verdict line reads `REVIEW PASSED` or `REVIEW CONDITIONALLY PASSED` with all Major items resolved — read the verdict line itself rather than re-deriving pass/fail from the findings list, **up to a maximum of 3 reviewer–fixer cycles**. If issues still persist after 3 cycles, stop the loop, present the remaining unresolved findings to the user verbatim, and ask for their guidance — do not continue cycling automatically.

**If the report contains only MINOR items**: note them for the user and proceed.

Do not open the browser preview until the reviewer reports `REVIEW PASSED` or `REVIEW CONDITIONALLY PASSED` with all Major items resolved.

---

## Step 8 — Browser Preview

1. **Confirm `diagrams.json` is current** at `docs/architecture-designer/diagrams.json`. The file was written at the end of Stage 6d and may have been updated by the architecture-fixer in Step 7 — if so it is already correct. It must follow the schema in `references/diagrams-guide.md` § "`diagrams.json` Schema". If validation in step 2 below flags issues, re-write the corrected diagram code into the file per that schema.

2. **Validate diagrams**: run `node <scripts_dir>/validate-diagrams.mjs`. If the script exits non-zero or prints `VALIDATION FAILED`, fix the flagged issues in the diagram code and re-write `docs/architecture-designer/diagrams.json` — do this regardless of whether `DEGRADED MODE` also appears in the same output, since `DEGRADED MODE` is not itself a pass/fail signal and can co-occur with a real `VALIDATION FAILED`. Do not proceed to step 3 until the run prints `VALIDATION PASSED`. **Only once it reads `VALIDATION PASSED`, if the output also contains `DEGRADED MODE`**: the script's real syntax parser was unavailable and some diagrams were only checked heuristically — validation still passed on what it could check, so proceed, but tell the user: "Diagram validation ran in degraded mode (parser dependencies not installed in `scripts/`) — some syntax errors may not have been caught. Run `npm install` in the plugin's `scripts/` directory for full validation coverage."

3. **Find a free port**: run `node <scripts_dir>/find-port.mjs`. Capture stdout (the port number). If it exits non-zero, report the error to the user.

4. **Start the preview server** in the background: `node <scripts_dir>/preview-server.mjs <port>`. The server opens the browser automatically. Tell the user the URL (e.g., `http://localhost:3000`).

`<scripts_dir>` is the `scripts/` directory of this plugin — two levels above this SKILL.md file.

5. **Do NOT create a stop-server script.** Leave the server running. Simply inform the user of the URL.

---

## Step 9 — User Confirmation

After opening the browser, ask:

> **"Does this architecture design meet your needs, or is there anything you would like to revise?"**

If the user requests revisions:
- Identify which stage the revision affects
- Return to that stage, ask the relevant questions again, update the answers
- **If Stage 1 is the revised stage**: re-confirm `description` along with the rest of the `stage1` answers — a description auto-drafted from the original answers can go stale once application goal, stakeholders, or pain points change. Re-draft it (or accept the user's own rewrite) and write the updated value back to `description`, the same way as the original Stage 1 confirmation.
- Regenerate the affected diagrams
- Re-run the architecture reviewer (step 7) — note this may spawn architecture-fixer, which writes `diagrams.json` directly
- Update `diagrams.json` with the revised diagrams (skip if the fixer already wrote it directly during the reviewer re-run above)
- Re-run `node <scripts_dir>/validate-diagrams.mjs` — the same gate as Step 8. If it exits non-zero or prints `VALIDATION FAILED`, fix the flagged issues in `diagrams.json` and re-validate before continuing. Do not tell the user to refresh until it passes; revised diagrams are at least as likely to contain syntax errors as first drafts. Placed here, after the last `diagrams.json` write in this loop, this one gate also catches anything the architecture-fixer changed during the reviewer re-run above.
- Tell the user to refresh their browser (the server reloads `diagrams.json` on page refresh)
- Ask the confirmation question again

Repeat until the user confirms the design is correct.

---

## Step 10 — Low-Level Design

**Read `references/lld-guide.md`** before starting this stage. It contains the exact format for every artifact type.

Derive the LLD directly from the confirmed HLD diagrams — do not invent endpoints or rules that are not visible in the sequence, class, or business-process diagrams.

Work through the five artifact groups in order, presenting each group to the user and asking for confirmation or revisions before moving to the next:

1. **API contracts** — one entry per endpoint visible in the sequence diagrams. Group by resource (auth, users, orders, …). For each: HTTP method + path, auth requirement, request schema (fields, types, validation), response schemas (success + every error code that can be returned).

2. **Business rules** — one entry per non-trivial operation (anything with conditional logic, aggregation, or side effects). Skip simple CRUD. For each: trigger, pre-conditions, step-by-step logic, post-conditions, edge cases with exact error codes.

3. **Data Transfer Objects (DTOs)** — only for complex or shared bodies used by multiple endpoints. Simple flat request/response bodies are documented inline in the API contract; they do not need a separate DTO entry.

4. **Inter-service contracts** — only for microservices or event-driven architectures. For each event/message: topic/queue name, producer, consumers with their SLAs and idempotency guarantees, payload schema. Omit this group entirely for monoliths.

5. **Error catalog** — a single table covering every error code referenced in the API contracts and business rules. Derived, not invented — no error should appear here that isn't referenced somewhere above.

After the user confirms all groups, the complete LLD is ready to include in the architecture document.

---

## Step 11 — Save Architecture Document

Once the user confirms, save the document to:
```
docs/architecture-designer/architecture/{yyyymmdd}-{topic}.md
```

- `{yyyymmdd}`: today's date as 8 digits in ISO order — use JavaScript `Date` to format: year (4-digit) + month (2-digit, zero-padded) + day (2-digit, zero-padded). Example: `20260705` for 5 July 2026. **Never use the shell `date` command.** This ISO-style order ensures files sort chronologically when listed alphabetically.
- `{topic}`: the project/application name in kebab-case (lowercase, hyphens, no spaces)
- If a file with this name already exists, append `-2`, `-3`, etc. until the filename is unique

After saving, update `docs/architecture-designer/session.json`: append `{ "path": "<absolute path of the saved file>", "createdAt": "<current ISO timestamp>" }` to the top-level `"documents"` array (create it with this one entry if it doesn't exist yet; create `schemaVersion: 2`, `project`, and `description` at the same time if the file predates them — synthesize `description` from `stage1` if it is missing, per the tolerant-read backfill rule in `references/session-schema.md`). This lets `/architecture-designer:implement` locate the latest document — the last entry's `path` — without asking.

**The document must begin with this metadata table on line 1:**

```markdown
| Date       | Version | Status | Reason | Previous Document |
|------------|---------|--------|--------|-------------------|
| {dd-mmm-y} | 1.0     | Draft  | -      | -                 |
```

- `dd-mmm-y` format: day is zero-padded (e.g., `05`), month is 3-letter capitalized abbreviation (`Jan`, `Feb`, `Mar`, `Apr`, `May`, `Jun`, `Jul`, `Aug`, `Sep`, `Oct`, `Nov`, `Dec`), year is 4 digits. Example: `05-Jul-2026`.

**Document body sections (in order)**: follow `references/document-template.md` — ten sections from Project Overview through Low-Level Design, each pulling from the corresponding stage or sub-agent output.

---

## Step 12 — Document Review

Spawn the `architecture-designer:document-reviewer` agent. Pass it:
- The path to the saved document
- The requirements summary — read from `docs/architecture-designer/session.json` (all confirmed stages)
- The expected filename

Wait for the review verdict.

**If DOCUMENT REVIEW FAILED**: spawn `architecture-designer:document-fixer`. Pass it:
- The document path
- The review report
- The requirements summary
- The path to `docs/architecture-designer/diagrams.json`

After the fixer overwrites the document, re-spawn `architecture-designer:document-reviewer` to verify. If the fixer's log says the file must be renamed (F6), rename it before re-running the reviewer. Repeat until DOCUMENT REVIEW PASSED, **up to a maximum of 3 reviewer–fixer cycles**. If failures persist after 3 cycles, present the remaining FAIL items to the user and ask for their input rather than cycling again.

**Once it passes**: update the `Status` column in the metadata table from `Draft` to `Approved`. The table should now read:

```
| {date} | 1.0 | Approved | - | - |
```

---

## Step 13 — Implementation Offer

After the document is approved, ask:

> **"The architecture document is approved. Would you like me to proceed with implementation — generating the project skeleton, data models, and infrastructure files based on this document?"**

If the user says yes: quickly scan the working directory for signs of an existing project — look for `package.json`, `go.mod`, `Cargo.toml`, `requirements.txt`, `pyproject.toml`, `pom.xml`, and source directories (`src/`, `app/`, `lib/`, `cmd/`, `internal/`).

**If files already exist**: summarize what was found and ask the question in `references/session-schema.md` § "Merge-strategy question".

**If the scan finds nothing**: no question needed — proceed as a fresh start into an empty project.

Before spawning, check `docs/architecture-designer/session.json` for a `"remediationPlans"` array. Find the entry whose `document` field equals the approved document's path; if found and its `path` exists on disk, this is the remediation plan to pass along — unless `references/session-schema.md` § "Checking whether a remediation plan is fully resolved" rules it out.

Then run `references/session-schema.md` § "Resumable-plan detection procedure" using the approved document's path as `{document}`. This produces the **Previous plan path** to pass below, if the user chooses to resume.

Then spawn the `architecture-designer:implementation-planner` agent. Pass it:
- The path to the approved document
- **Existing project summary** — what was found in the scan, translated into the agent's expected strategy label: `Fresh start (empty project)` if nothing was found; `Merge` if the user chose (a); `Fresh start (existing project)` if the user chose (b); `User-described layout` if the user chose (c)
- The technology stack from stage 5
- **Remediation plan path** — the remediation plan resolved above (matched by `document`), if it exists on disk and the "Skip if already resolved" check didn't rule it out
- **Previous plan path** — the resumed plan's `path`, if the user chose to continue above (omit otherwise)

Wait for it to report the plan was saved and confirmed. Then spawn `architecture-designer:architecture-implementer`, passing it the implementation plan path from that report plus the same document path, existing project summary, technology stack, and remediation plan path (if any was passed to the planner). Do not spawn architecture-implementer if implementation-planner did not report a confirmed plan.

If the user says no: congratulate them and let them know they can run `/architecture-designer:review` at any time to revisit and revise the architecture.

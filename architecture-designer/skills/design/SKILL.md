---
name: design
description: Use this skill when the user wants to design a new application's architecture or infrastructure — says "design my architecture", "help me plan the architecture", "create architecture diagrams", "I need to plan a new system", or is starting a new project and needs a structured design process. Also trigger when the user mentions HLD, LLD, API contracts, or system design. Guides from requirements gathering through capacity planning, technology selection, diagram generation, low-level design, document saving, and code skeleton implementation.
---

# Architecture Designer — Main Design Workflow

This skill guides the user through a six-stage architecture design process (with seven post-design steps for review, preview, LLD, document save, and implementation), ending with browser-rendered Mermaid diagrams, low-level design artifacts (API contracts, business rules, DTOs, error catalog), a reviewed and approved document, and an optional code skeleton.

Always use this skill for new architecture design, even if the user has already started describing their system in the conversation — do not skip straight to diagram generation or freeform advice.

**Scripts live two levels up from this file:** `../../scripts/find-port.mjs` and `../../scripts/preview-server.mjs`. At runtime, resolve these paths by taking the absolute path of this SKILL.md and navigating up two directories to find `scripts/`.

---

## How to run this workflow

**Before starting — check for an existing session**: look for `docs/architecture-designer/session.json`. If the file already exists, read it and ask the user:

> "I found an existing design session for **[project name from the file, or 'a previous project' if unnamed]**. Would you like to continue where we left off, or start a new design from scratch?"

If they choose to continue: read the completed stages from `session.json`, brief the user on where the previous session left off, and resume from the first incomplete stage. If they choose to start fresh: delete `docs/architecture-designer/session.json` (and `docs/architecture-designer/diagrams.json` if present) before proceeding.

Work through the six stages in order (Stages 1–6), then follow Steps 7–13. At the end of each stage, summarize the user's answers and ask:
> "Does this summary look correct? Shall we move to the next stage?"

Do not proceed until the user confirms. After each stage is confirmed, persist the stage summary to disk: write `docs/architecture-designer/session.json` (create the `docs/architecture-designer/` directory if it does not exist). The file is a JSON object with one key per completed stage, e.g. `{ "stage1": { ... }, "stage2": { ... }, ... }` — append each new stage's summary when the user confirms. Do not keep context only in working memory: working memory degrades over long sessions and is invisible to sub-agents. Sub-agents must be given the contents of `session.json` as part of their input so they do not depend on conversation history that they cannot access.

**session.json write discipline**: Write the exact text the user confirmed — do not produce a fresh paraphrase or condensed re-summary. The goal is to preserve what was actually agreed upon, so that sub-agents work from confirmed facts rather than a re-interpretation that may silently diverge from the user's intent.

**Canonical session.json schema** — the top-level keys are fixed; the field names inside each stage object are the user's confirmed answers and may vary:

```json
{
  "stage1": { "applicationGoal": "...", "stakeholders": "...", "businessProcesses": "...", "painPoints": "...", "successCriteria": "..." },
  "stage2": { "functionalRequirements": ["..."], "nonFunctionalRequirements": { "performance": "...", "security": "...", "compliance": "...", "scalability": "...", "availability": "..." } },
  "stage3": { "budget": "...", "timeline": "...", "regulations": "...", "teamCompetencies": "...", "legacySystems": "...", "cloudPreference": "..." },
  "stage4": { "registeredUsers": "...", "concurrentUsers": "...", "tps": "...", "dataVolume": "...", "readWriteRatio": "...", "peakPatterns": "...", "geography": "..." },
  "stage5": { "architecturePattern": "...", "backend": "...", "frontend": "...", "database": "...", "infrastructure": "...", "supportingServices": "...", "authentication": "...", "observability": "...", "disasterRecovery": "..." },
  "stage6b": { "tool": "...", "stateBackend": "...", "modules": "...", "envStrategy": "...", "driftDetection": "..." },
  "stage6c": { "platform": "...", "stages": "...", "branchingStrategy": "...", "envPromotion": "...", "secretInjection": "...", "artifactManagement": "..." },
  "documentPaths": ["/absolute/path/to/docs/architecture-designer/architecture/YYYYMMDD-topic.md"]
}
```

Sub-agents receive the full contents of this file as input and must read it tolerantly — inner field names are illustrative, not contractual. The only guaranteed top-level keys are `stage1`–`stage5` and (after Step 11) `documentPaths`. `stage6b` and `stage6c` are written after Stage 6b/6c confirmation and must be included when passing session context to sub-agents. `remediationPlanPaths` may also appear if the user has previously run `/architecture-designer:review` — it is written by the review skill, not this skill, and must be passed to the architecture-implementer when present.

**`documentPaths` and `remediationPlanPaths` are arrays, not single values.** Every time a workflow saves a new architecture document or remediation plan, it appends the new file's path to the relevant array instead of overwriting a previous entry — documents and plans are themselves never overwritten on disk (each revision is a new versioned file), so the array preserves that same history in `session.json`. Treat the last element of each array as the current one unless a step says otherwise.

---

## Stage 1 — Requirements Gathering

Goal: understand what the application must do and why it exists.

Ask these questions (you may combine them into a conversational flow rather than a numbered list, but cover all of them):

1. **Application goal**: What is the primary purpose of this application? What problem does it solve?
2. **Stakeholders**: Who are the main users? Are there multiple user roles (admin, end-user, partner, etc.)?
3. **Business processes**: What are the key workflows users will perform? Walk me through the most important one step by step.
4. **Pain points**: What problems or limitations exist in the current process (if any) that this application should fix?
5. **Success criteria**: How will you know the application has succeeded? What metrics or outcomes matter?

Summarize answers, confirm, then proceed.

---

## Stage 2 — Requirements Analysis

Goal: separate functional from non-functional requirements.

Ask:

**Functional requirements** (features):
- What are the core features the application must have at launch?
- Are there secondary features that are nice-to-have but not essential for v1?
- Are there any explicit non-goals (things the application will NOT do)?

**Non-functional requirements** (qualities):
- **Performance**: Are there response time targets? (e.g., "search results in under 500ms")
- **Security**: What data is sensitive? Are there compliance requirements (GDPR, HIPAA, PCI-DSS, SOC 2)?

> **Compliance grounding rule**: When the user names a compliance framework, record it as a stated requirement — do not assert specific technical controls from memory (e.g., "GDPR requires X-day retention"). Regulatory specifics vary by jurisdiction and change over time; model-generated compliance claims are expensive to correct. Mark every compliance-specific control in the document with **"⚠ Needs legal/compliance validation"** and defer exact requirements to the user's legal team.
- **Scalability**: Must the system scale horizontally? Is auto-scaling important?
- **Availability**: What is the acceptable downtime? (e.g., 99.9% SLA = ~8.7 hours/year)
- **Number of users**: How many concurrent users are expected at launch? At peak?

Summarize as two lists (functional and non-functional), confirm, then proceed.

---

## Stage 3 — Feasibility Study and Constraints

Goal: identify real-world constraints that will shape technical decisions.

Ask:

- **Budget**: Is there a rough infrastructure budget per month? (Helps choose cloud tier, managed vs self-hosted)
- **Timeline**: What is the target launch date? How long is the development runway?
- **Regulations**: Any specific regulations to comply with? (data residency, encryption at rest requirements, audit logging)
- **Team competencies**: What languages, frameworks, and platforms does your team know well?
- **Legacy systems**: Are there existing systems this application must integrate with? (databases, APIs, authentication providers, message brokers)
- **Preferred cloud / infrastructure**: Any preference between AWS, GCP, Azure, on-premise, or bare metal?

Summarize constraints, confirm, then proceed.

---

## Stage 4 — Capacity Planning

Goal: produce concrete numbers that will drive infrastructure sizing and technology choices.

Ask:

- **Users**: How many registered users are expected at launch? In 12 months? In 3 years?
- **Concurrent users**: At peak, how many users will be active simultaneously?
- **Transactions per second (TPS)**: Estimate the busiest operation (e.g., API requests, orders, messages). How many per second at peak?
- **Data volume**: How much data will be stored at launch? How fast does it grow per month?
- **Read/write ratio**: Is the workload read-heavy, write-heavy, or balanced?
- **Peak load patterns**: Are there predictable spikes? (e.g., end-of-month billing, flash sales, daily at 9 AM)
- **Geographic distribution**: Are users concentrated in one region or globally distributed?

Summarize with explicit numbers (estimates are fine — label them as estimates), confirm, then proceed.

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

**Session completeness gate**: before spawning any sub-agent, run `node <scripts_dir>/validate-session.mjs`. If the check fails, the listed stages must be completed first — do not proceed to 6a or any later step until `SESSION CHECK PASSED`.

### 6a. Database design (delegate to sub-agent)

Spawn the `architecture-designer:database-designer` agent. Pass it:
- The complete requirements summary — read this from `docs/architecture-designer/session.json` (the confirmed stages 1–5 data written to disk at each confirmation). Do not rely solely on conversation memory.
- The domain entities extracted from the functional requirements
- The access patterns (how data will be read and written, from the business processes)

Wait for the agent to return ERD, index plan, engine recommendation, and secure connection config.

Then spawn `architecture-designer:database-reviewer`. Pass it:
- The full database-designer output
- The requirements summary (stages 1–5)

If the reviewer returns `DATABASE REVIEW FAILED`: spawn `architecture-designer:database-fixer` with the review report, the database-designer output, the requirements summary, and the path to `docs/architecture-designer/diagrams.json`. The fixer writes the corrected ERD and indexPlan directly into `diagrams.json`. After it completes, re-spawn `architecture-designer:database-reviewer` to verify. Repeat until `DATABASE REVIEW PASSED`, **up to a maximum of 3 reviewer–fixer cycles**. If it still returns `DATABASE REVIEW FAILED` after 3 cycles, stop the loop, present the remaining findings to the user verbatim, and ask for their guidance rather than cycling further.

Incorporate the final approved database design into the diagram set and document.

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
- Re-spawn `architecture-designer:architecture-reviewer` to verify.
- Repeat until no Critical items remain and all Major items are resolved, **up to a maximum of 3 reviewer–fixer cycles**. If issues still persist after 3 cycles, stop the loop, present the remaining unresolved findings to the user verbatim, and ask for their guidance — do not continue cycling automatically.

**If the report contains only MINOR items**: note them for the user and proceed.

Do not open the browser preview until the reviewer reports `REVIEW PASSED` or `REVIEW CONDITIONALLY PASSED` with all Major items resolved.

---

## Step 8 — Browser Preview

1. **Confirm `diagrams.json` is current** at `docs/architecture-designer/diagrams.json`. The file was written at the end of Stage 6d and may have been updated by the architecture-fixer in Step 7 — if so it is already correct. It must follow the schema in `references/diagrams-guide.md` § "`diagrams.json` Schema". If validation in step 2 below flags issues, re-write the corrected diagram code into the file per that schema.

2. **Validate diagrams**: run `node <scripts_dir>/validate-diagrams.mjs`. If the script exits non-zero or prints `VALIDATION FAILED`, fix the flagged issues in the diagram code and re-write `docs/architecture-designer/diagrams.json`. Do not proceed to step 3 until validation passes.

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

After saving, update `docs/architecture-designer/session.json`: append the full absolute path of the saved file to the top-level `"documentPaths"` array (create it with this one entry if it doesn't exist yet). This lets `/architecture-designer:implement` locate the latest document — the last entry in the array — without asking.

**The document must begin with this metadata table on line 1:**

```markdown
| Date       | Version | Status | Reason | Previous Document |
|------------|---------|--------|--------|-------------------|
| {dd-mmm-y} | 1.0     | Draft  | -      | -                 |
```

- `dd-mmm-y` format: day is zero-padded (e.g., `05`), month is 3-letter capitalized abbreviation (`Jan`, `Feb`, `Mar`, `Apr`, `May`, `Jun`, `Jul`, `Aug`, `Sep`, `Oct`, `Nov`, `Dec`), year is 4 digits. Example: `05-Jul-2026`.

**Document body sections (in order):**

1. **Project Overview** — name, purpose, date, version
2. **Requirements Summary** — functional and non-functional requirements from stages 1–2
3. **Constraints and Feasibility** — from stage 3
4. **Capacity Planning** — from stage 4 with numeric estimates
5. **Technology Decisions** — stack, architecture pattern, database, infrastructure, observability strategy, and DR approach, with justifications from stages 1–4
6. **Architecture Diagrams** — every created diagram with: a heading, a paragraph description, then the mermaid code block. For the ERD, include the index list table immediately after the mermaid block.
7. **Database Design** — the full output from the database-designer agent (schema, ERD explanation, index plan, connection config)
8. **Infrastructure as Code** — IaC tool and justification, state backend config, module breakdown table (module name, what it provisions, environment-specific sizing), environment strategy, drift detection approach. Follow `references/iac-guide.md` § 6 for the exact format.
9. **CI/CD Pipeline** — platform and justification, pipeline stages table (stage, trigger, tool, gate), branching strategy, environment promotion rules, secret injection approach, artifact management. Follow `references/cicd-guide.md` § 7 for the exact format.
10. **Low-Level Design** — API contracts, business rules, DTOs (complex/shared only), inter-service contracts (microservices/event-driven only), and error catalog. Follow the section order and formatting from `references/lld-guide.md`.

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

**If files already exist**: summarize what was found and ask the same merge-strategy question `/architecture-designer:implement` uses:
> "I found an existing project structure. How would you like to proceed?
> **(a) Merge** — add missing files from the architecture without overwriting existing code
> **(b) Fresh start** — generate the complete skeleton; any file that already exists will be flagged before being overwritten — you decide per collision
> **(c) Let me describe what to keep** — I'll describe my existing layout and we'll work around it"
> Wait for the answer before proceeding.

**If the scan finds nothing**: no question needed — proceed as a fresh start into an empty project.

Then spawn the `architecture-designer:architecture-implementer` agent. Pass it:
- The path to the approved document
- **Existing project summary** — what was found in the scan, translated into the agent's expected strategy label: `Fresh start (empty project)` if nothing was found; `Merge` if the user chose (a); `Fresh start (existing project)` if the user chose (b); `User-described layout` if the user chose (c)
- The technology stack from stage 5

If the user says no: congratulate them and let them know they can run `/architecture-designer:review` at any time to revisit and revise the architecture.

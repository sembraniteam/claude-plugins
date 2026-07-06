---
name: architecture-designer:design
description: Use this skill when the user wants to design a new application's architecture or infrastructure, says "design my architecture", "help me plan the architecture", "create architecture diagrams", "I need to plan a new system", "design the infrastructure for my app", "architecture planning", "help me architect", "create Mermaid diagrams for my system", "I'm starting a new project and need architecture help", or begins a new software project and needs a structured design process. Always use this skill for new architecture design — it guides from requirements gathering through capacity planning, technology selection, diagram generation, document saving, and code skeleton implementation. Do not skip this skill just because the user has already started describing their system.
---

# Architecture Designer — Main Design Workflow

This skill guides the user through a six-stage architecture design process, ending with browser-rendered Mermaid diagrams, a reviewed and approved document, and an optional code skeleton.

**Scripts live two levels up from this file:** `../../scripts/find-port.mjs` and `../../scripts/preview-server.mjs`. At runtime, resolve these paths by taking the absolute path of this SKILL.md and navigating up two directories to find `scripts/`.

---

## How to run this workflow

Work through the six stages in order. At the end of each stage, summarize the user's answers and ask:
> "Does this summary look correct? Shall we move to the next stage?"

Do not proceed until the user confirms. Keep a running context object (in your working memory) with all answers gathered so far — you'll need it for later stages.

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

---

## Stage 6 — Architecture and Infrastructure Design

### 6a. Database design (delegate to sub-agent)

Spawn the `architecture-designer:database-designer` agent. Pass it:
- The complete requirements summary (stages 1–5)
- The domain entities extracted from the functional requirements
- The access patterns (how data will be read and written, from the business processes)

Wait for the agent to return ERD, index plan, engine recommendation, and secure connection config.

Then spawn `architecture-designer:database-reviewer`. Pass it:
- The full database-designer output
- The requirements summary (stages 1–5)

If the reviewer returns `DATABASE REVIEW FAILED`: spawn `architecture-designer:database-fixer` with the review report, the database-designer output, and the requirements summary. After the fixer returns corrected outputs, re-spawn `architecture-designer:database-reviewer` to verify. Repeat until `DATABASE REVIEW PASSED`.

Incorporate the final approved database design into the diagram set and document.

### 6b. Diagram selection and generation

Generate Mermaid diagrams relevant to the project. **All diagrams are optional** — select only those that add clarity for this specific project. After generating, tell the user:
- Which diagrams were created and why
- Which diagrams were skipped and why (e.g., "State diagram skipped — no entities with complex status lifecycles identified")

**Read `references/diagrams-guide.md` before generating any diagram.** It contains: the exact attribute format for ERD, full templates for each diagram type, common mistakes to avoid, and real-world examples. Don't rely on memory for Mermaid syntax — check the guide.

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

**Production-ready requirement**: For any system targeting production workloads, the deployment / infrastructure diagram must show: (1) at least one observability sink (log aggregator, APM agent, or metrics exporter named in Stage 5); (2) at least one DR component (database replica, automated backup target, or cross-region failover). If either is absent the `architecture-reviewer` will raise it as a Major finding.

**ERD special requirement**: Since `erDiagram` has no native index notation, mark indexed columns via attribute comments (`"idx"`) and include an index list table (from the database-designer agent) as a markdown table immediately after the ERD mermaid block. See `references/diagrams-guide.md` for the exact format.

### 6c. Mermaid v11.16 compatibility rules

- Use `flowchart` instead of `graph` for flowcharts (both work, `flowchart` is preferred)
- `stateDiagram-v2` not `stateDiagram`
- `C4Context` and `C4Container` require `securityLevel: 'loose'` — already set in the preview server
- For `architecture-beta`, use valid node types: `server`, `database`, `cloud`, `disk`, `internet`
- Avoid HTML tags inside node labels — use plain text only
- Do not use `%%` comments on the same line as syntax (put them on their own line)
- Keep node IDs alphanumeric with underscores — no spaces, hyphens in IDs
- For long labels, use quotes: `A["Long label text"]`

---

## Step 7 — Architecture Review (BEFORE preview)

Spawn the `architecture-designer:architecture-reviewer` agent. Pass it:
- The full requirements summary (all stages 1–5)
- All generated Mermaid diagram code, labeled by type

Wait for the review report.

**If the report contains CRITICAL or MAJOR items**: spawn `architecture-designer:architecture-fixer`. Pass it:
- The review report
- The path to `docs/architecture-designer/diagrams.json`
- The requirements summary

After the fixer updates `diagrams.json`, re-spawn `architecture-designer:architecture-reviewer` to verify. Repeat until no Critical items remain and all Major items are resolved.

**If the report contains only MINOR items**: note them for the user and proceed.

Do not open the browser preview until the reviewer reports `REVIEW PASSED`.

---

## Step 8 — Browser Preview

1. **Write `diagrams.json`** to `docs/architecture-designer/diagrams.json` (create the directory if needed):

```json
{
  "title": "<Project Title>",
  "topic": "<project-topic-kebab>",
  "generatedAt": "<ISO 8601 timestamp from JavaScript Date — never the shell date command>",
  "diagrams": [
    {
      "id": "<kebab-id>",
      "title": "<Human-readable title>",
      "description": "<One sentence describing what this diagram shows>",
      "details": "<Multi-paragraph explanation — see field guide below>",
      "rationale": "<Why this diagram was created — see field guide below>",
      "companionTable": [
        { "name": "<index name>", "table": "<table name>", "columns": "<column(s)>", "type": "<index type>", "reason": "<justification>" }
      ],
      "code": "<Raw Mermaid syntax — newlines as \\n>"
    }
  ]
}
```

`generatedAt`: use the JavaScript `new Date().toISOString()` equivalent — format as `YYYY-MM-DDTHH:MM:SS.mmmZ`. Never use shell commands.

**Field guide for `details`, `rationale`, and `companionTable`** — all three are rendered in the browser preview directly below the diagram:

- **`details`** (2–4 paragraphs): Explain what each major component or group represents, how data or control flows through the diagram, the key relationships and their significance, and what a developer needs to understand to implement based on this diagram. Separate paragraphs with `\n\n` in the JSON string. Rendered as a collapsible block.

- **`rationale`** (1–3 paragraphs): State why this specific diagram type was chosen for this concern, what design decisions are encoded in the diagram (e.g., why the ERD is normalized this way, why the sequence diagram shows this particular auth flow), what alternatives were considered and why they were not chosen, and which requirements or constraints from stages 1–5 drove the visible choices. Separate paragraphs with `\n\n` in the JSON string. Rendered as a collapsible block.

- **`companionTable`** (optional, ERD diagrams only): Copy the index plan rows from the database-designer output into this structured array. Each row maps to one index: `name` is the index identifier (e.g., `idx_users_email`), `table` is the table it belongs to, `columns` is the indexed column(s) as a string, `type` is the index type (e.g., `UNIQUE B-TREE`, `B-TREE`, `GIN`), and `reason` is the query it serves. Rendered as a visible HTML table immediately below the ERD — omit this field for all non-ERD diagrams.

2. **Find a free port**: run `node <scripts_dir>/find-port.mjs`. Capture stdout (the port number). If it exits non-zero, report the error to the user.

3. **Start the preview server** in the background: `node <scripts_dir>/preview-server.mjs <port>`. The server opens the browser automatically. Tell the user the URL (e.g., `http://localhost:3000`).

`<scripts_dir>` is the `scripts/` directory of this plugin — two levels above this SKILL.md file.

4. **Do NOT create a stop-server script.** Leave the server running. Simply inform the user of the URL.

---

## Step 9 — User Confirmation

After opening the browser, ask:

> **"Does this architecture design meet your needs, or is there anything you would like to revise?"**

If the user requests revisions:
- Identify which stage the revision affects
- Return to that stage, ask the relevant questions again, update the answers
- Regenerate the affected diagrams
- Re-run the architecture reviewer (step 7)
- Update `diagrams.json` (the server reloads it on page refresh — tell the user to refresh their browser)
- Ask the confirmation question again

Repeat until the user confirms the design is correct.

---

## Step 10 — Save Architecture Document

Once the user confirms, save the document to:
```
docs/architecture-designer/architecture/{yyyymmdd}-{topic}.md
```

- `{yyyymmdd}`: today's date as 8 digits in ISO order — use JavaScript `Date` to format: year (4-digit) + month (2-digit, zero-padded) + day (2-digit, zero-padded). Example: `20260705` for 5 July 2026. **Never use the shell `date` command.** This ISO-style order ensures files sort chronologically when listed alphabetically.
- `{topic}`: the project/application name in kebab-case (lowercase, hyphens, no spaces)
- If a file with this name already exists, append `-2`, `-3`, etc. until the filename is unique

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

---

## Step 11 — Document Review

Spawn the `architecture-designer:document-reviewer` agent. Pass it:
- The path to the saved document
- The requirements summary
- The expected filename

Wait for the review verdict.

**If DOCUMENT REVIEW FAILED**: spawn `architecture-designer:document-fixer`. Pass it:
- The document path
- The review report
- The requirements summary
- The path to `docs/architecture-designer/diagrams.json`

After the fixer overwrites the document, re-spawn `architecture-designer:document-reviewer` to verify. If the fixer's log says the file must be renamed (F6), rename it before re-running the reviewer. Repeat until DOCUMENT REVIEW PASSED.

**Once it passes**: update the `Status` column in the metadata table from `Draft` to `Approved`. The table should now read:

```
| {date} | 1.0 | Approved | - | - |
```

---

## Step 12 — Implementation Offer

After the document is approved, ask:

> **"The architecture document is approved. Would you like me to proceed with implementation — generating the project skeleton, data models, and infrastructure files based on this document?"**

If the user says yes: spawn the `architecture-designer:architecture-implementer` agent. Pass it:
- The path to the approved document
- The technology stack from stage 5

If the user says no: congratulate them and let them know they can run `/architecture-designer:review` at any time to revisit and revise the architecture.

---
name: design-architecture
description: This skill should be used when the user asks to "design an architecture", "design software architecture", "design system architecture", "what architecture should I use", "help me design my app", "plan the architecture for", "design a system for", "create an architecture for", "architect my project", "help me design a backend", "design a scalable system", or describes a software project they want to architect from scratch.
---

# Design Architecture

Act as a **Software Architect** who helps users design software architecture in a gradual, efficient, and easy-to-understand manner. Follow this workflow strictly — gather requirements first, present three options, wait for the user to select one, then write final documentation.

## Workflow

**Tools — create tasks and use structured questions throughout:**

At the very start, call **TaskCreate** to create one task per step:
1. Gather requirements — Batch 1 (System & Scale)
2. Gather requirements — Batch 2 (Technical & Operational)
3. Confirm requirements summary
4. Generate architecture options (3 options), ERD, and Recommendation
5. Write content.md and start viewer server
6. User selects option
7. Mark the selected option
8. Write final documentation sections
9. Save final docs and stop server

Mark each task `in_progress` when starting it and `completed` when done.

### 1. Gather Requirements (A/B/C/D Questions)

Before generating any architecture options, ask structured A/B/C/D questions in batches of 3–4. Use **AskUserQuestion** for each batch — map A/B/C/D options to the tool's `options` array (up to 4 per question). For questions that include "Other: describe briefly", the tool provides an automatic "Other" option. Wait for the user to answer each batch before asking the next.

**Batch 1 — System & Scale:**

1. What is the primary purpose of the system?
   - A) SaaS platform (multi-tenant, web-based)
   - B) Internal enterprise / back-office tool
   - C) Mobile application backend
   - D) Data processing / analytics platform
   - Other: Describe briefly

2. Expected user scale at launch and in 2 years?
   - A) Small: < 1,000 users
   - B) Medium: 1,000 – 100,000 users
   - C) Large: 100,000 – 1M users
   - D) Massive: 1M+ users

3. Expected transaction volume (requests per second at peak)?
   - A) Low: < 100 rps
   - B) Moderate: 100 – 1,000 rps
   - C) High: 1,000 – 10,000 rps
   - D) Very high: 10,000+ rps

4. Team size and technical expertise?
   - A) Solo / tiny team (1–3), generalists
   - B) Small team (4–10), mixed seniority
   - C) Medium team (10–30), specialized roles
   - D) Large engineering org (30+)

**Batch 2 — Technical & Operational:**

5. File and object storage requirements?
   - A) None
   - B) User uploads (images, documents — small to medium)
   - C) Media assets (video, audio — large files, CDN delivery)
   - D) Backups, archives, data lake, or static website assets

6. Deployment preference?
   - A) Managed cloud (AWS, GCP, Azure)
   - B) Self-hosted / on-premise
   - C) Hybrid (cloud + on-premise)
   - D) Fully serverless

7. Programming language / framework preference?
   - A) Java / Kotlin (Spring Boot, Quarkus)
   - B) Go (Gin, Echo, Fiber, standard library)
   - C) Node.js / TypeScript (NestJS, Express, Fastify)
   - D) Python (FastAPI, Django) or C# (.NET)
   - Other: Specify language and any frameworks

8. Compliance and security requirements?
   - A) Standard web security (OWASP Top 10)
   - B) SOC 2 Type II
   - C) GDPR / data privacy regulations
   - D) PCI DSS / HIPAA / financial or healthcare regulations

If the user has already provided sufficient context to answer most of these, proceed directly to Step 2 (confirmation).

### 2. Confirm Requirements Summary

After collecting all answers, display a structured summary **before** generating any architecture options. This lets the user verify that nothing was misunderstood.

Present the summary in this exact format, then wait for confirmation:

---

**Requirements Summary**

| Category           | Your Answer                    | Inferred from      |
|--------------------|--------------------------------|--------------------|
| System purpose     | {value from Q1}                | —                  |
| User scale         | {value from Q2}                | —                  |
| Transaction volume | {value from Q3}                | —                  |
| Team               | {value from Q4}                | —                  |
| Object storage     | {value from Q5}                | —                  |
| Deployment         | {value from Q6}                | —                  |
| Language           | {value from Q7}                | —                  |
| Compliance         | {value from Q8}                | —                  |
| Consistency model  | {strong / eventual / mixed}    | Q1 + Q3 (inferred) |
| Analytics tier     | {basic / moderate / heavy}     | Q1 (inferred)      |
| SLA target         | {best-effort / 99.9% / 99.99%} | Q2 + Q3 (inferred) |
| Observability tier | {basic / full / SRE-grade}     | Q2 + Q4 (inferred) |

**Key inferences:**
- {1–3 bullets summarizing constraints inferred from the combination of answers — e.g., "High volume + small team → Low Risk is the safest starting point", "SaaS + massive scale → strong consistency for transactions, eventual for feeds"}

> Does this accurately capture your requirements? Reply with any corrections, or say **"Yes, proceed"** to generate the architecture options.

---

Wait for the user to confirm or correct before proceeding to Step 3. If the user provides corrections, update the summary and re-confirm. Only proceed when the user explicitly approves.

### 3. Generate Three Architecture Options

After confirmation, analyze requirements and present **exactly 3 options**: Low Risk, Medium Risk, and High Risk.

For each option, cover all required sections (see "Required Sections Per Option" below). Do not skip any section.

#### Option 1: Low Risk
- Proven, well-understood patterns. Minimal infrastructure complexity.
- Typical: Monolith, Modular Monolith, Simple REST + Single DB.
- Best for MVPs, small teams, tight deadlines.

#### Option 2: Medium Risk
- Balanced between pragmatism and scalability. Some distributed elements where justified.
- Typical: Modular Monolith with service boundaries, BFF + separate services for key domains.
- Best for growing products with 6–18 month horizon.

#### Option 3: High Risk
- Full distributed architecture optimized for scale or flexibility.
- Typical: Microservices, Event-Driven + CQRS, Serverless-first, Hexagonal.
- Best for teams with operational maturity and long investment horizon.

### 4. Required Sections Per Option

Structure each option under the `## Architecture Diagram` document section using `### Option N:` subheadings. Use `####` for subsections within each option. The full blank scaffold is in `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/output-template.md` — **read it for structure only; never write to it**.

Required `####` subsections for each option — **every option must include three Mermaid diagrams**. Read `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/mermaid-guidelines.md` for syntax and per-tier guidance:

- **Infrastructure Layout** (`architecture-beta`) — cloud groups, services with icons, and physical deployment topology. **Required.** Derive service names and zone topology from the gathered requirements: use the **Infrastructure Mapping** section of `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/mermaid-guidelines.md` to map Q6 (deployment preference) → concrete service names (e.g., EKS, RDS, S3 for AWS), Q2–Q3 (scale) → zone/region count, and Q8 (compliance) → mandatory extra components (WAF, private subnets, HSM). Do not use generic placeholders like "Primary DB" — use the actual product name. **Follow each diagram with a 1–2 sentence description** of what it shows (key zones, traffic entry point, and data stores).
- **Request Flow** (`sequenceDiagram`) — the primary user-facing request end-to-end (e.g., "user places order", "user logs in"). **Required.** Cover: client → API → cache → DB → response. Label each arrow with the method or action. **Follow each diagram with a 1–2 sentence description** of the happy-path flow and any notable steps (cache hits, async branches).
- **Component Flow** (`flowchart TD`) — logical data flow between components and stores. **Required.** **Follow each diagram with a 1–2 sentence description** of the main data paths and how components hand off to each other.
- **Key Components** — bulleted list of main services/modules with one-line descriptions
- **Technology Stack** — table: Layer / Recommended / Alternatives / Reason
- **Data Layer Design** — all applicable store types; for each: what's stored, why not the primary DB, data flow. Cover: transactional store, cache, search, analytics/OLAP, message queue, object storage, graph (if core). See `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/database-selection-guide.md`.
- **Object Storage** — only if relevant to user's answers: solution (MinIO / S3 / GCS / R2), what's stored, bucket org, access control, encryption, self-hosted vs. managed trade-offs
- **Observability Strategy** — OTel-first; pillars: Instrumentation, Logs, Metrics, Distributed Traces, Alerting. Scale tooling to complexity. See `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/observability-guide.md`.
- **Technology Decision Rationale** — for each major choice: why chosen, better-than-alternatives, required skills, ecosystem longevity
- **Future Impact** — 6-month / 1-year / 3-year table + scalability ceiling, operational overhead, reversibility, vendor lock-in
- **Risks & Mitigations** — table: Risk / Likelihood / Impact / Mitigation
- **When to Choose This Option** — 2–3 bullets for the ideal scenario

Read `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/architecture-patterns.md`, `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/database-selection-guide.md`, and `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/observability-guide.md` when designing each option's respective sections.

### 5. ERD Section

After presenting all options, include a `## ERD` section with Mermaid `erDiagram` covering the primary data model (use the recommended option's schema or a composite if all options share similar entities).

Include table specifications for key entities (PK, columns, types, key indexes).

### 6. Add Recommendation

After all options, include a `## Recommendation` section with:

1. **Confidence Score table** — rate each option on four dimensions (0–10). The viewer automatically renders any `X/10` value in a table cell as a visual progress bar. Use this exact column structure:

```markdown
### Confidence Scores

| Option | Team Fit | Timeline | Scale | Cost | Overall |
|--------|----------|----------|-------|------|---------|
| Option 1 — Low Risk: {Name}     | 9/10 | 9/10 | 7/10 | 8/10 | **8.3/10** |
| Option 2 — Medium Risk: {Name}  | 7/10 | 6/10 | 8/10 | 7/10 | **7.0/10** |
| Option 3 — High Risk: {Name}    | 4/10 | 3/10 | 10/10 | 5/10 | **5.5/10** |
```

Score criteria:
- **Team Fit** — how well the option matches the team's current skills and size
- **Timeline** — how achievable within the stated deadline
- **Scale** — how well it handles the target scale (now and in 2 years)
- **Cost** — infra + operational cost vs. stated budget/constraints

2. **Narrative** — 4–6 sentences stating which option is recommended and why, referencing actual requirements (team size, timeline, scale). Cite the highest Overall score.

### 7. Write Content and Open Viewer

After presenting all 3 options, the ERD, and the Recommendation — **before asking the user to choose** — write the content and open the viewer so the user can compare options with rendered Mermaid diagrams:

1. Use the **Write tool** to save the full draft to `/tmp/archimind-viewer/content.md`. Follow the **Document Structure Convention** below. Do NOT include `## Final Documentation` at this stage.
2. Start the viewer server and open the browser — **run as a single command**:

```bash
open "$(bash "$CLAUDE_PLUGIN_ROOT/scripts/start-server.sh")"
```

Inform the user the viewer is open — use the **Architecture Diagram** nav to compare each option's diagrams side by side, and the **ERD** nav to view the data model. When ready, select the option they'd like to proceed with.

### 8. Option Selection

Use **AskUserQuestion** to ask the user to choose:

```
question: "Which architecture would you like to proceed with?"
header: "Select Option"
options:
  - label: "Option 1 — Low Risk"
    description: <one-line summary of Option 1 name/pattern>
  - label: "Option 2 — Medium Risk"
    description: <one-line summary of Option 2 name/pattern>
  - label: "Option 3 — High Risk"
    description: <one-line summary of Option 3 name/pattern>
```

Iterate freely if the user wants adjustments (e.g., "swap MongoDB for PostgreSQL in Option 2"). After each adjustment, update `/tmp/archimind-viewer/content.md` with the Write tool and re-present AskUserQuestion. The user can click **↺ Reload** in the viewer sidebar to see updated content. Do not proceed to Step 9 until the user makes an explicit choice.

### 9. Mark the Selected Option

1. Read the saved document
2. Insert decision header after the document title:
   ```markdown
   **Selected:** Option N — {Risk Level}: {Architecture Name}
   **Decision date:** {ISO date}
   ```
3. For **review workflows only**: populate `## Revision / ### After` with the selected option's proposed architecture diagrams. For fresh designs, omit or leave the Revision section empty.
4. Append a `## Decision Notes` section capturing user-requested adjustments, migration timing, and next steps

### 10. Write Final Documentation Sections

After selection is marked, append the final documentation using this trimmed structure. Each section should be substantive — do not leave placeholders:

```markdown
## Final Documentation

### Overview
### Architecture Decision
### Technology Stack
### Data Architecture
### Observability
### Security
### Trade-offs & Next Steps
```

Section content guide:
- **Overview** — what the system does, who uses it, key characteristics (2–4 sentences)
- **Architecture Decision** — which option was chosen and the core rationale; reference the diagrams already in the selected `### Option N:` heading above
- **Technology Stack** — single table: Layer / Technology / Reason. Include language, backend, frontend, DB, cache, messaging, infra, observability
- **Data Architecture** — DB choices and rationale; ERD (repeat the `erDiagram` from `## ERD` for standalone readability); migration strategy (schema versioning tool, rollback approach, zero-downtime considerations)
- **Observability** — all three pillars in one section: logs (tool + agent), metrics (tool + key dashboards), distributed tracing (tool + sampling). Alerting thresholds
- **Security** — authentication/authorization approach, data encryption at rest/in transit, secret management, compliance considerations
- **Trade-offs & Next Steps** — what the chosen option sacrifices (scalability ceiling, operational overhead, reversibility); first 3 implementation milestones; open questions

### 11. Save Final Documentation and Stop Server

After marking the selection and appending final documentation:

1. Update `/tmp/archimind-viewer/content.md` with the Write tool (now includes `## Final Documentation`). Inform the user: "The viewer is updated — click **↺ Reload** in the sidebar to see the final state."
2. Compute timestamp: `node -e 'process.stdout.write(String(Date.now()))'` (macOS) or `date +%s%3N` (Linux). Derive topic slug from the project name (e.g., `payment-platform`, `iot-dashboard`).
3. Save permanent technical documentation to the user's project:

```bash
mkdir -p docs/archimind/architecture
```

Then use the **Write tool** to write `docs/archimind/architecture/{timestamp_ms}-{topic}.md`. **This file must contain only the selected option** — not all three. Structure it as:

```markdown
# Architecture Design: {Topic}

**Generated:** {ISO date}
**Selected:** Option N — {Risk Level}: {Architecture Name}
**Decision date:** {ISO date}

## Project Overview
...

## Requirements Gathered
...

## Architecture Diagram

### Option N: {Risk Level} — {Architecture Name}

{Selected option's full content — all #### subsections}

## ERD
...

## Revision

{For review workflows: populate Before and After tabs. For fresh designs: omit this section entirely — do not write the ## Revision heading.}

## Recommendation

{Include the filled Confidence Scores table from Step 6 — Team Fit / Timeline / Scale / Cost / Overall — and the narrative recommendation.}

## Decision Notes
...

## Final Documentation
...
```

Omit Option 1, 2, and 3 sections that were not selected. The viewer re-opens this doc as a single-option view (no option tabs). To re-visualize later: `bash "$CLAUDE_PLUGIN_ROOT/scripts/open-doc.sh" docs/archimind/architecture/{timestamp_ms}-{topic}.md`.

4. Stop the viewer server:

```bash
bash "$CLAUDE_PLUGIN_ROOT/scripts/stop-server.sh"
```

## Document Structure Convention

The viewer parses these heading patterns from `content.md`:

- `## Architecture Diagram` + `### Option N:` subheadings → option tabs
- `## ERD` → ERD nav view
- `## Revision` + `### Before` / `### After` → Before/After tabs

**Critical**: Use `### Option N:` (level-3) within `## Architecture Diagram`, not `## Option N:` (level-2). The viewer splits on level-3 headings to create option tabs.

For the full document template (all required sections, headings, placeholder text), see `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/output-template.md` — **read-only; never write to it**.

## Mermaid Diagram Guidelines

Read `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/mermaid-guidelines.md` for diagram type selection, node limits, edge labeling, subgraph conventions, and syntax examples.

## Token Optimization

- Respond concisely; avoid repeating information already established
- If context becomes large, provide a brief summary before continuing
- Prioritize information relevant to architectural decision-making
- Scale observability tooling recommendations proportionally to architecture complexity
- Do not generate final documentation until the user has explicitly selected an architecture

## Additional Resources

- **`$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/architecture-patterns.md`** — Detailed patterns (Monolith, Microservices, Serverless, Event-Driven, CQRS, Hexagonal). Read when deciding which pattern fits each risk tier.
- **`$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/database-selection-guide.md`** — Comprehensive database selection guide (relational, document, key-value, column-family, time-series, graph, search, NewSQL, polyglot persistence). Read when choosing the data layer.
- **`$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/observability-guide.md`** — Observability stack guide (OpenTelemetry, Loki, Prometheus, Jaeger/Tempo, SigNoz, Uptrace, Grafana Stack, Datadog). Read when designing the observability strategy.
- **`$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/output-template.md`** — Full blank template for the output document. **Read-only — never write to this file.** Output always goes to `/tmp/archimind-viewer/content.md` (viewer) or `docs/archimind/architecture/{timestamp_ms}-{topic}.md` (final docs).
- **`$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/mermaid-guidelines.md`** — Diagram type selection, node limits, edge labeling, subgraph conventions, and syntax examples.

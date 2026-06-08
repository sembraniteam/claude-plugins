---
name: Design Architecture
description: This skill should be used when the user asks to "design an architecture", "design software architecture", "design system architecture", "what architecture should I use", "help me design my app", "plan the architecture for", "design a system for", "create an architecture for", "architect my project", "help me design a backend", "design a scalable system", or describes a software project they want to architect from scratch.
---

# Design Architecture

Act as a **Software Architect** who helps users design software architecture in a gradual, efficient, and easy-to-understand manner. Follow this workflow strictly — gather requirements first, present three options, wait for the user to select one, then write final documentation.

## Workflow

### 1. Gather Requirements (A/B/C/D Questions)

Before generating any architecture options, ask structured A/B/C/D questions in batches of 3–4. Wait for the user to answer each batch before asking the next. Add an "Other" option when the user may need to provide a custom answer.

**Batch 1 — System and Scale:**

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

**Batch 2 — Technical Requirements:**

5. Database consistency requirements?
   - A) Strong consistency required (financial, inventory, legal records)
   - B) Eventual consistency acceptable (social feeds, analytics)
   - C) Mixed: strong for core data, eventual for secondary
   - D) Not sure yet

6. Analytics and reporting needs?
   - A) None / basic (simple counts and filters)
   - B) Moderate (dashboards, periodic reports)
   - C) Heavy (real-time analytics, large aggregations)
   - D) Data lake / BI / data warehouse platform

7. File and object storage requirements?
   - A) None
   - B) User uploads (images, documents — small to medium)
   - C) Media assets (video, audio — large files, CDN delivery)
   - D) Backups, archives, data lake, or static website assets

8. Deployment preference?
   - A) Managed cloud (AWS, GCP, Azure)
   - B) Self-hosted / on-premise
   - C) Hybrid (cloud + on-premise)
   - D) Fully serverless

**Batch 3 — Operational Requirements:**

9. SLA / SLO expectations?
   - A) Best effort (no formal SLA)
   - B) Business hours (99% uptime)
   - C) High availability (99.9%, < 8.7 hours/year downtime)
   - D) Mission-critical (99.99%+, < 52 min/year downtime)

10. Observability and monitoring requirements?
    - A) Basic (error logs, simple uptime checks)
    - B) Moderate (structured logging, key metrics, basic alerting)
    - C) Full observability (metrics + logs + distributed traces, dashboards)
    - D) SRE-grade (SLI/SLO tracking, automated alerting, on-call runbooks)

11. Programming language / framework preference?
    - A) Java / Kotlin (Spring Boot, Quarkus)
    - B) Go (Gin, Echo, Fiber, standard library)
    - C) Node.js / TypeScript (NestJS, Express, Fastify)
    - D) Python (FastAPI, Django) or C# (.NET)
    - Other: Specify language and any frameworks

12. Compliance and security requirements?
    - A) Standard web security (OWASP Top 10)
    - B) SOC 2 Type II
    - C) GDPR / data privacy regulations
    - D) PCI DSS / HIPAA / financial or healthcare regulations

If the user has already provided sufficient context to answer most of these, proceed directly to Step 2.

### 2. Generate Three Architecture Options

After collecting answers, analyze requirements and present **exactly 3 options**: Low Risk, Medium Risk, and High Risk.

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

### 3. Required Sections Per Option

Structure each option under the `## Architecture Diagram` document section using `### Option N:` subheadings. Use `####` for subsections within each option. The full blank scaffold is in `references/output-template.md`.

Required `####` subsections for each option:
- **Key Components** — bulleted list of main services/modules with one-line descriptions
- **Technology Stack** — table: Layer / Recommended / Alternatives / Reason
- **Data Layer Design** — all applicable store types; for each: what's stored, why not the primary DB, data flow. Cover: transactional store, cache, search, analytics/OLAP, message queue, object storage, graph (if core). See `references/database-selection-guide.md`.
- **Object Storage** — only if relevant to user's answers: solution (MinIO / S3 / GCS / R2), what's stored, bucket org, access control, encryption, self-hosted vs. managed trade-offs
- **Observability Strategy** — OTel-first; pillars: Instrumentation, Logs, Metrics, Distributed Traces, Alerting. Scale tooling to complexity. See `references/observability-guide.md`.
- **Technology Decision Rationale** — for each major choice: why chosen, better-than-alternatives, required skills, ecosystem longevity
- **Future Impact** — 6-month / 1-year / 3-year table + scalability ceiling, operational overhead, reversibility, vendor lock-in
- **Deployment Strategy** — environments, CI/CD, containerization, orchestration, scaling, rollback, DR, observability deployment
- **Risks & Mitigations** — table: Risk / Likelihood / Impact / Mitigation
- **When to Choose This Option** — 2–3 bullets for the ideal scenario

Read `references/architecture-patterns.md`, `references/database-selection-guide.md`, and `references/observability-guide.md` when designing each option's respective sections.

### 4. ERD Section

After presenting all options, include a `## ERD` section with Mermaid `erDiagram` covering the primary data model (use the recommended option's schema or a composite if all options share similar entities).

Include table specifications for key entities (PK, columns, types, key indexes).

### 5. Add Recommendation

After all options, include a `## Recommendation` section: which option is recommended for the user's specific context, referencing their actual requirements (team size, timeline, scale). Keep to 4–6 sentences.

### 6. Do NOT Write Final Documentation Yet

**The work is not complete until the user selects one option.** After presenting options, prompt:

> "Which architecture would you like to proceed with — Option 1 (Low Risk), Option 2 (Medium Risk), or Option 3 (High Risk)? You can request modifications to any option before deciding."

Iterate freely if the user wants adjustments (e.g., "swap MongoDB for PostgreSQL in Option 2", "add Redis to Option 1"). Do not proceed to Step 7 until the user states an explicit choice.

### 7. Save the Design Document

Once the user selects one, compute the timestamp and save:

1. `node -e 'process.stdout.write(String(Date.now()))'` (macOS/Node) or `date +%s%3N` (Linux)
2. `mkdir -p docs/archimind/architecture/`
3. Topic slug from the project name (e.g., `payment-platform`, `iot-dashboard`)
4. Save to: `docs/archimind/architecture/{timestamp_ms}-{topic}-design.md`
5. Inform the user of the saved path

The saved document must follow the **Document Structure Convention** below.

### 8. Offer to Visualize

After saving, ask: "Would you like to open the architecture viewer to see the diagrams rendered? Use `/archimind:visualize` to start the server."

### 9. Mark the Selected Option

1. Read the saved document
2. Insert decision header after the document title:
   ```markdown
   **Selected:** Option N — {Risk Level}: {Architecture Name}
   **Decision date:** {ISO date}
   ```
3. Append `✅ SELECTED` to the chosen option's `### Option N:` heading
4. Append a `## Decision Notes` section capturing user-requested adjustments, migration timing, and next steps

### 10. Write Final Documentation Sections

After selection is marked, append the full documentation sections to the document:

```markdown
## Final Documentation

### Overview
### Goals
### Non-Goals
### Architecture Decision
### Technology Stack
### Programming Languages and Frameworks
### Database Architecture
### Object Storage Architecture
### Database Optimization Strategy
### Database Migration Strategy
### System Components
### Data Flow
### Security Considerations
### Scalability Strategy
### Deployment Strategy
### Infrastructure Design
### Observability
### Monitoring and Alerting Strategy
### Distributed Tracing Strategy
### Trade-offs
### Future Improvements
```

For the database migration strategy, include: schema versioning (Flyway / Liquibase / Prisma Migrate / Alembic / etc.), migration workflow, rollback strategy, zero-downtime considerations, data migration for large datasets, backward compatibility.

### 11. Stop the Viewer Server

After the choice is finalized, check if the viewer is running and offer to stop it:
```bash
[ -f .archimind.pid ]
bash "$CLAUDE_PLUGIN_ROOT/scripts/stop-server.sh"
```

## Document Structure Convention

The static site viewer parses sections by these exact heading patterns:

```markdown
# Architecture Design: {Topic}

## Architecture Diagram

### Option 1: Low Risk — {Name}
### Option 2: Medium Risk — {Name}
### Option 3: High Risk — {Name}

## ERD

## Revision

### Before
### After

## Recommendation

## Decision Notes

## Final Documentation
```

**Critical**: Use `### Option N:` (level-3) within `## Architecture Diagram`, not `## Option N:` (level-2) at top level. The viewer's "Architecture Diagram" nav renders these as option tabs. The "ERD" nav renders `## ERD`. The "Revision" nav renders `## Revision` with Before/After tabs.

## Mermaid Diagram Guidelines

- Use `flowchart TD` for system/service topology
- Use `erDiagram` in the `## ERD` section only
- Keep diagrams focused: 8–15 nodes maximum
- Label edges with action verbs ("calls", "publishes to", "reads from", "caches in")
- Group related nodes with subgraphs
- Show non-relational stores alongside relational ones

## Token Optimization

- Respond concisely; avoid repeating information already established
- If context becomes large, provide a brief summary before continuing
- Prioritize information relevant to architectural decision-making
- Scale observability tooling recommendations proportionally to architecture complexity
- Do not generate final documentation until the user has explicitly selected an architecture

## Additional Resources

- **`references/architecture-patterns.md`** — Detailed patterns (Monolith, Microservices, Serverless, Event-Driven, CQRS, Hexagonal). Read when deciding which pattern fits each risk tier.
- **`references/database-selection-guide.md`** — Comprehensive database selection guide (relational, document, key-value, column-family, time-series, graph, search, NewSQL, polyglot persistence). Read when choosing the data layer.
- **`references/observability-guide.md`** — Observability stack guide (OpenTelemetry, Loki, Prometheus, Jaeger/Tempo, SigNoz, Uptrace, Grafana Stack, Datadog). Read when designing the observability strategy.
- **`references/output-template.md`** — Full blank template for the output document.

---
name: design-architecture
description: This skill should be used when the user asks to "design an architecture", "design software architecture", "design system architecture", "what architecture should I use", "help me design my app architecture", "plan the architecture for", "design a system for", "create an architecture for", "architect my project", "help me design a backend", "design a scalable system", or describes a software project they want to architect from scratch.
---

# Design Architecture

Act as a **Software Architect and Senior Software Engineer** with 5+ years of production experience. Read and apply `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/engineering-principles.md` throughout this workflow.

Core behaviors:
- Analyze requirements critically before generating any option — the right architecture is driven by actual constraints (team, deadline, scale, budget, compliance), not trends
- Recommend the simplest option that satisfies all requirements; introduce complexity only when a specific requirement demands it
- Identify SPOFs, bottlenecks, security risks, and technical debt in every option
- Explain the technical rationale and risk level behind every decision

Follow the **Spec → Plan → Review → Ship** workflow strictly — gather requirements first, generate a direct recommendation and write it to content.md, present a compact summary for user confirmation, then open the visual viewer for review. **Never output the full architecture content in the chat response** — the viewer is the display surface. Keep chat responses brief status updates.

## Workflow

At the very start, call **TaskCreate** to create one task per step:
1. Spec — Identify and gather missing requirements
2. Spec — Confirm requirements summary
3. Plan — Generate architecture recommendation, ERD, and Design Rationale → write content.md
4. Review — Present recommendation summary, confirm or adjust
5. Ship — Open viewer, await confirmation
6. Ship — Write ADR and Final Documentation
7. Ship — Save permanent docs and stop server

Mark each task `in_progress` when starting it and `completed` when done.

---

### Stage 1: Spec — Gather Requirements

Analyze the user's initial message and any provided context (code snippets, files, prior conversation) to extract known information. Map what is found to the **8 required data points** in the catalog below — classify each as:
- **Known** — explicitly stated (e.g., "I'm building an API in Go on AWS")
- **Inferable** — derivable with high confidence (e.g., "early-stage startup" → small team; "MVP" → small scale; "IoT ingestion pipeline" → high volume, data processing)
- **Unknown** — cannot be determined without asking

Ask only about **Unknown** data points using **AskUserQuestion** — map A/B/C/D options from the catalog to the tool's `options` array (up to 4 per question). Group up to 4 unknown data points per call. If all points are Known or Inferable, skip to **Confirm Requirements Summary** immediately. Never ask about information already provided.

**Required Data Points**

Use the corresponding options when a data point is Unknown:

**1. System purpose**
- A) SaaS platform (multi-tenant, web-based)
- B) Internal enterprise / back-office tool
- C) Mobile application backend
- D) Data processing / analytics platform
- Other: Describe briefly

**2. User scale** (at launch and in 2 years)
- A) Small: < 1,000 users
- B) Medium: 1,000 – 100,000 users
- C) Large: 100,000 – 1M users
- D) Massive: 1M+ users

**3. Transaction volume** (requests per second at peak)
- A) Low: < 100 rps
- B) Moderate: 100 – 1,000 rps
- C) High: 1,000 – 10,000 rps
- D) Very high: 10,000+ rps

**4. Team size and expertise**
- A) Solo / tiny team (1–3), generalists
- B) Small team (4–10), mixed seniority
- C) Medium team (10–30), specialized roles
- D) Large engineering org (30+)

**5. File and object storage requirements**
- A) None
- B) User uploads (images, documents — small to medium)
- C) Media assets (video, audio — large files, CDN delivery)
- D) Backups, archives, data lake, or static website assets

**6. Deployment preference**
- A) Managed cloud (AWS, GCP, Azure)
- B) Self-hosted / on-premise
- C) Hybrid (cloud + on-premise)
- D) Fully serverless

**7. Programming language / framework preference**
- A) Java / Kotlin (Spring Boot, Quarkus)
- B) Go (Gin, Echo, Fiber, standard library)
- C) Node.js / TypeScript (NestJS, Express, Fastify)
- D) Python (FastAPI, Django) or C# (.NET)
- Other: Specify language and any frameworks

**8. Compliance and security requirements**
- A) Standard web security (OWASP Top 10)
- B) SOC 2 Type II
- C) GDPR / data privacy regulations
- D) PCI DSS / HIPAA / financial or healthcare regulations

**Confirm Requirements Summary**

After collecting all answers, display a structured summary **before** generating any architecture options. Present in this exact format, then wait for confirmation:

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
- {1–3 bullets summarizing constraints inferred from the combination of answers — e.g., "High volume + small team → a managed monolith is the safest starting point"}

> Does this accurately capture your requirements? Reply with any corrections, or say **"Yes, proceed"** to generate the architecture options.

---

Wait for the user to confirm or correct. If the user provides corrections, update the summary and re-confirm. Only proceed to Stage 2 when the user explicitly approves.

---

### Stage 2: Plan — Generate Architecture Recommendation

After confirmation, compose the full design document **directly into `/tmp/archimind-viewer/content.md`** using the Write tool. Print a short status line like "Planning…" while writing. **Do not open the viewer yet — that happens in Stage 4: Ship.**

**Choose and commit**: Map each stated requirement to the tier it demands (read `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/architecture-patterns.md` for tier definitions). Then commit to the architecture that satisfies all requirements with the minimum viable complexity. Don't hedge — a clear recommendation with honest trade-offs is more useful than a comparison. The user can push back in Stage 3 if they want something different.

**C4 Context diagram — write first**: Before the architecture, write the `## System Context` section with a C4 Level 1 diagram. Read `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/mermaid-guidelines.md` (C4 Context Diagram section) for format.

**Write the recommendation directly under `## Architecture Diagram`** — open with the pattern name (e.g., "Layered Monolith with PostgreSQL") in the intro paragraph. Use `####` for subsections. The scaffold is in `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/output-template.md` — read-only.

Required `####` subsections — **three Mermaid diagrams are mandatory**. Read `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/mermaid-guidelines.md` for syntax and per-pattern guidance:

- **Infrastructure Layout** (`architecture-beta`) — cloud groups, services with icons, physical deployment topology. Map Q6 → concrete service names (e.g., EKS, RDS, S3 for AWS). No generic placeholders. 1–2 sentence description after the diagram.
- **Request Flow** (`sequenceDiagram`) — primary user-facing request end-to-end: client → API → cache → DB → response. 1–2 sentence description.
- **Logical Architecture** (`flowchart TD` for single-service / layered; `flowchart LR` for multi-domain / event mesh) — structural view. 1–2 sentence description. See mermaid-guidelines.md for pattern-specific starters.
- **Key Components** — bulleted list of main services/modules with one-line descriptions
- **Technology Stack** — table: Layer / Recommended / Alternatives / Reason
- **Data Layer Design** — all applicable store types; for each: what's stored, why not the primary DB, data flow. See `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/database-selection-guide.md`.
- **Object Storage** — only if relevant: solution, what's stored, bucket org, access control, encryption, self-hosted vs. managed trade-offs
- **Observability Strategy** — OTel-first; pillars: Instrumentation, Logs, Metrics, Distributed Traces, Alerting. See `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/observability-guide.md`.
- **Technology Decision Rationale** — for each major choice: why chosen, better-than-alternatives, required skills, ecosystem longevity
- **SPOF Analysis** — every single point of failure: blast radius, detection time, and mitigation
- **Disaster Recovery** — RTO, RPO, backup strategy, failover approach, DR tier proportionate to stated scale and compliance
- **Future Impact** — 6-month / 1-year / 3-year table + scalability ceiling, operational overhead, reversibility, vendor lock-in
- **Risks & Mitigations** — table: Risk / Likelihood / Impact / Mitigation

#### ERD Section

After the option, add `## ERD` with a Mermaid `erDiagram` covering the primary data model. Include table specifications for key entities (PK, columns, types, key indexes).

#### Design Rationale Section

Add `## Design Rationale` — 4–6 sentences: why this specific architecture, what simpler or more complex alternatives were considered and ruled out, what the key trade-off is. Be specific: cite team size, scale targets, compliance requirements, timeline.

Save the complete document with the Write tool. **Do not call start-server.sh at this stage.**

---

### Stage 3: Review — Confirm Before Shipping

After writing content.md, present a compact **Recommendation Summary** in chat:

---

**Recommendation**

**Architecture**: {Name} — {1-sentence description of the pattern}
**Stack**: {key technologies in brief}
**Why**: {2–3 sentences citing the specific requirements that drove this choice and what alternatives were ruled out}

---

Use **AskUserQuestion** to ask the user what to do next:

```
question: "The architecture recommendation is ready. What would you like to do?"
header: "Next Step"
options:
  - label: "Ship — open the visual viewer"
    description: "Open the interactive viewer to review the full design"
  - label: "Adjust — I have suggestions"
    description: "Request changes to the architecture, tech stack, or rationale before viewing"
```

If the user chooses **Adjust**: apply the requested changes to `/tmp/archimind-viewer/content.md`, update the Recommendation Summary, and re-present Stage 3. Repeat until the user chooses **Ship**.

---

### Stage 4: Ship — Visual Review and Final Documentation

Open the viewer:

```bash
open "$(bash "$CLAUDE_PLUGIN_ROOT/scripts/start-server.sh")"
```

Post a brief chat message: "Viewer is open at http://localhost:PORT — review the full design in **Architecture Diagram** and the data model in **ERD**. Tell me when you're ready to finalize, or request any last adjustments."

**Review and Confirm**

Use **AskUserQuestion**:

```
question: "Ready to finalize this architecture?"
header: "Finalize"
options:
  - label: "Proceed — finalize this design"
    description: "Write the final documentation and save the permanent record"
  - label: "Adjust — one more change"
    description: "Request a change; I'll update the viewer and you can reload"
```

If the user adjusts: apply to `/tmp/archimind-viewer/content.md`, tell the user to click **↺ Reload** in the viewer sidebar, then re-present. Repeat until the user proceeds.

**Confirm and Write Final Documentation**

Once the user confirms, complete all the following in sequence — one continuous step:

1. Read the saved document
2. Insert decision header after the document title:
   ```markdown
   **Confirmed:** {Architecture Name}
   **Decision date:** {ISO date}
   ```
3. Write the `## Architecture Decision Record` section — read `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/adr-guide.md` for the required format. The ADR must include: Context (requirements active at decision time), Decision (what was chosen and why), Consequences (positive + trade-offs accepted + watch list), Rejected Alternatives (what simpler or more complex approaches were ruled out, with specific reasons), and a Review Trigger.

**Append Final Documentation** — each section must be substantive, no placeholders:

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

For field-level guidance on each section, read `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/output-template.md`.

For the `### Security` section:
- Read `$CLAUDE_PLUGIN_ROOT/skills/design-database/references/security-guide.md` for DB roles, TLS, connection pooling, secrets management, SQL injection prevention, audit logging, and compliance controls.
- **STRIDE threat model**: Include the STRIDE table (read `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/threat-model-guide.md`) when compliance requirement (Q8) is SOC 2, GDPR, PCI DSS, or HIPAA, **or** when the system is multi-tenant. For standard OWASP-only systems, write "STRIDE analysis not performed at this compliance tier — revisit if requirements change." and omit the table.

**Save Permanent Documentation and Stop Server**

1. Update `/tmp/archimind-viewer/content.md` with the Write tool (now includes `## Final Documentation`). Inform the user: "The viewer is updated — click **↺ Reload** in the sidebar to see the final state."
2. Compute timestamp: `node -e 'process.stdout.write(String(Date.now()))'` (macOS) or `date +%s%3N` (Linux). Derive topic slug from the project name (e.g., `payment-platform`, `iot-dashboard`).
3. Save permanent technical documentation to the user's project:

```bash
mkdir -p docs/archimind/architecture
```

Then use the **Write tool** to write `docs/archimind/architecture/{timestamp_ms}-{topic}.md`. Structure it using the scaffold in `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/output-template.md` — include the `## Architecture Diagram` section, ERD, Design Rationale, Architecture Decision Record, and Final Documentation. To re-visualize later: `bash "$CLAUDE_PLUGIN_ROOT/scripts/open-doc.sh" docs/archimind/architecture/{timestamp_ms}-{topic}.md`.

4. Stop the viewer server:

```bash
bash "$CLAUDE_PLUGIN_ROOT/scripts/stop-server.sh"
```

---

## Document Structure Convention

<!-- Keep in sync with review-architecture/SKILL.md and visualize/SKILL.md -->

The viewer parses these heading patterns from `content.md`:

- `## Architecture Diagram` → content renders directly as the main view (no tab bar)
- `## ERD` → ERD nav view
- `## Revision` + `### Before` / `### After` → Before/After tabs

**Fresh designs**: Omit the `## Revision` section — it is used only by review-architecture to show Before/After comparisons.

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

All reference paths are cited inline throughout the workflow — follow the `read` directives in each stage for the relevant file. The full reference set lives under `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/`:

- **`architecture-patterns.md`** — canonical pattern names and per-tier constraints
- **`engineering-principles.md`** — 10 guiding principles; read at session start
- **`database-selection-guide.md`** — read when selecting data stores
- **`observability-guide.md`** — read when writing observability strategy
- **`mermaid-guidelines.md`** — diagram type selection, node limits, C4 context diagram format
- **`output-template.md`** — full document scaffold; read-only
- **`adr-guide.md`** — ADR format; read during Stage 4 when writing the Architecture Decision Record
- **`threat-model-guide.md`** — STRIDE methodology; read during Stage 4 for compliance-sensitive systems
- **`$CLAUDE_PLUGIN_ROOT/skills/design-database/references/security-guide.md`** — DB-level security controls

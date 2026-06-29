---
name: review-architecture
description: This skill should be used when the user asks to "review architecture", "analyze my architecture", "audit the architecture", "review my system design", "improve my existing architecture", "refactor architecture", "redesign my system", "what's wrong with my architecture", "critique my design", "help me improve my existing system", "is my architecture good", "identify bottlenecks in my architecture", "help me migrate to microservices", "help me scale my existing system", "my system is too slow", or provides an existing architecture description, diagram, or codebase structure for evaluation.
---

# Review Architecture

Act as a **Senior Software Engineer** conducting a formal architecture review. Read and apply `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/engineering-principles.md` throughout this workflow.

Core behaviors:
- Prioritize evidence over intuition — verify pain points with metrics before proposing changes
- Identify SPOFs, technical debt, security gaps, scalability ceilings, and disaster recovery gaps systematically
- Recommend the least invasive change that delivers the most risk reduction
- Never propose a higher-complexity option unless the simpler option demonstrably fails to address the root causes

Follow the **Spec → Plan → Review → Ship** workflow strictly — collect and analyze the existing architecture first, generate a direct redesign recommendation and write it to content.md, present a compact summary for user confirmation, then open the visual viewer for final review. **Never output the full redesign content in the chat response** — the viewer is the display surface. Keep chat responses brief status updates.

## Workflow

At the very start, call **TaskCreate** to create one task per step:
1. Spec — Collect existing architecture information
2. Spec — Perform architecture analysis
3. Spec — Confirm analysis summary
4. Plan — Generate redesign recommendation → write content.md
5. Review — Present recommendation summary, confirm or adjust
6. Ship — Open viewer, await confirmation
7. Ship — Write ADR and finalize documentation
8. Ship — Save permanent docs and stop server

Mark each task `in_progress` when starting it and `completed` when done.

---

### Stage 1: Spec — Collect and Analyze

**Collect Existing Architecture Information**

Scan the user's initial message for context already provided (system type, pain points, constraints, deployment). Ask only about what's missing.

Use **AskUserQuestion** to gather context before the user provides free-form details. Ask up to 4 questions at once. These are **free-text questions** — do not attempt to map them to A/B/C/D options; pass them as open-ended `description` fields or use the `Other` option only:
- What type of system is it? (web app, backend API, data pipeline, mobile backend, etc.)
- What are the primary pain points that prompted this review?
- What constraints exist that cannot change? (legacy integrations, compliance, team skills)
- How is the system currently deployed? (cloud/on-premise, containerized, serverless, etc.)

Then ask the user to provide any relevant artifacts:
- **Description**: What the system does, how it's structured today
- **Tech stack**: Languages, frameworks, databases, infra currently used
- **Architecture diagram** or a textual description of services/components

Read any relevant files the user points to (e.g., `docker-compose.yml`, `package.json`, database migration files, service directories).

**Perform Architecture Analysis**

Before analyzing weaknesses, confirm the stated pain points are backed by observable data — not assumptions. Ask:
- Are there existing metrics? (p50/p95/p99 latencies, error rates, throughput, slow query logs)
- Which specific operations are slow or failing — exact endpoints, jobs, or queries?
- If no metrics exist, flag this explicitly: **"Lack of observability means the redesign is based on assumptions, not evidence."** Including an observability improvement in the recommendation is almost always warranted.

Evaluate the existing architecture against the checklist in `$CLAUDE_PLUGIN_ROOT/skills/review-architecture/references/review-checklist.md`. Produce an **Analysis Summary** covering:
- **Strengths**: What the current architecture does well
- **Weaknesses**: Specific identified problems (scalability, coupling, observability, data, security, operational)
- **Antipatterns found**: Reference `$CLAUDE_PLUGIN_ROOT/skills/review-architecture/references/anti-patterns.md` for canonical names
- **Root causes**: Why each weakness exists

Keep the analysis concise: 3–6 bullet points per category. Be specific ("single DB handles both OLTP and analytics queries, causing lock contention"), not vague.

**Confirm Analysis Summary**

After completing the analysis, display a summary to the user **before** generating redesign options. Present in this format, then wait for confirmation:

---

**Analysis Summary**

**Current Architecture:** {1–2 sentence description of what was understood}

| Category                    | Finding                                                               |
|-----------------------------|-----------------------------------------------------------------------|
| Tech stack                  | {languages, frameworks, databases identified}                         |
| Architecture style          | {monolith / modular monolith / microservices / etc.}                  |
| Strengths                   | {1–2 key positives}                                                   |
| Primary pain points         | {top 2–3 issues identified}                                           |
| Antipatterns detected       | {canonical names from anti-patterns.md, or "None identified"}         |
| Constraints (cannot change) | {legacy integrations, compliance, team skills, etc.}                  |

**Root cause hypothesis:** {1–2 sentences on why the main issues exist — e.g., "The system evolved from a monolith without service boundaries, resulting in tight coupling that now blocks independent scaling."}

> Does this accurately capture the current state and issues? Reply with any corrections, or say **"Yes, proceed"** to generate the redesign options.

---

Wait for the user to confirm or correct. If the user provides corrections, update the summary and re-confirm. Only proceed to Stage 2 when the user explicitly approves.

---

### Stage 2: Plan — Generate Redesign Recommendation

After confirmation, compose the review document directly into `/tmp/archimind-viewer/content.md` using the Write tool. Print "Planning…" while writing. **Do not open the viewer yet — that happens in Stage 4: Ship.**

Structure the document with `## Architecture Diagram`, `## ERD`, `## Revision`, and `## Design Rationale` top-level sections. The `## Revision` section must contain `### Before` and `### After` subsections — the viewer renders these as Before/After tabs.

For the complete document scaffold, read: `$CLAUDE_PLUGIN_ROOT/skills/review-architecture/references/output-template.md` — **read-only; never write to it.**

**Choose and commit**: The design space for architecture remediation runs from conservative (fix critical symptoms, minimal structural change, days to weeks) through moderate (decompose tight coupling, targeted store changes, weeks to months) to full overhaul (re-architect from scratch, Strangler Fig migration, months to quarters). Map the identified root causes to where intervention is actually needed — don't default to the middle. A conservative approach that doesn't fix the root cause is wasted effort; a full overhaul that isn't justified by the problems creates migration risk with no proportional benefit. The user can push back in Stage 3.

**Write the recommendation directly under `## Architecture Diagram`** — open with the approach name (e.g., "Add Caching Layer + Index Fixes", "Extract Auth + Read Replica", "Event-Driven Microservices Migration") in the intro paragraph. Use `####` for subsections.

Key structural rules:
- Content goes directly under `## Architecture Diagram` — no `### Option N:` subheading
- The `### After` diagram in `## Revision` shows the proposed state

**Required subsections** — three Mermaid diagrams mandatory. Read `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/mermaid-guidelines.md` for review-specific conventions (mark changed nodes `[NEW]`/`[UPDATED]`, problematic current-state nodes with `⚠`):

- **Infrastructure Layout** (`architecture-beta`) — proposed infrastructure topology
- **Request Flow** (`sequenceDiagram`) — proposed primary request path
- **Logical Architecture** (`flowchart TD`) — proposed structural view with `[NEW]`/`[UPDATED]` labels
- **What Changes** — current state → proposed state, component by component
- **Key Improvements** — how each identified weakness is addressed
- **Technology Changes** — table: Component / Current / Proposed / Reason
- **Data Layer Changes** — store migrations, new stores, removed stores
- **Observability Changes** — what observability gaps the redesign closes
- **Technology Decision Rationale** — for each major new technology: why chosen, better than alternatives, required skills, ecosystem
- **Future Impact** — 6-month / 1-year / 3-year table + scalability ceiling, operational overhead, reversibility, vendor lock-in
- **Migration Path** — phased steps, Strangler Fig or parallel-run approach (not big bang — see `$CLAUDE_PLUGIN_ROOT/skills/review-architecture/references/anti-patterns.md`), rollback strategy
- **Risks & Mitigations** — table: Risk / Likelihood / Impact / Mitigation

#### Design Rationale Section

Add `## Design Rationale` — 4–6 sentences: why this specific redesign, what pain points it addresses, what less invasive or more aggressive alternatives were considered and ruled out, what the key trade-off is. Be specific about the constraints that made more drastic change unwarranted (or necessary).

Save the complete document with the Write tool. **Do not call start-server.sh at this stage.**

---

### Stage 3: Review — Confirm Before Shipping

After writing content.md, present a compact **Recommendation Summary** in chat:

---

**Recommendation**

**Approach**: {Short Title} — {1-sentence description of what changes}
**Migration effort**: {Days to weeks / Weeks to months / Months to quarters}
**Why**: {2–3 sentences citing the specific root causes this addresses and what less invasive or more aggressive alternatives were ruled out}

---

Use **AskUserQuestion**:

```
question: "The architecture redesign recommendation is ready. What would you like to do?"
header: "Next Step"
options:
  - label: "Ship — open the visual viewer"
    description: "Open the interactive viewer to review the full redesign and Before/After comparison"
  - label: "Adjust — I have suggestions"
    description: "Request changes to the approach, tech choices, or migration path before viewing"
```

If **Adjust**: apply changes to `/tmp/archimind-viewer/content.md`, update summary, re-present Stage 3. Repeat until **Ship**.

---

### Stage 4: Ship — Visual Review and Final Documentation

Open the viewer:

```bash
open "$(bash "$CLAUDE_PLUGIN_ROOT/scripts/start-server.sh")"
```

Post: "Viewer is open at http://localhost:PORT — review the redesign in **Architecture Diagram** and the Before/After comparison in **Revision**. Tell me when you're ready to finalize, or request any last adjustments."

**Review and Confirm**

Use **AskUserQuestion**:

```
question: "Ready to finalize this architecture redesign?"
header: "Finalize"
options:
  - label: "Proceed — finalize this redesign"
    description: "Write the ADR and save the permanent record"
  - label: "Adjust — one more change"
    description: "Request a change; I'll update the viewer and you can reload"
```

If adjust: apply to `/tmp/archimind-viewer/content.md`, tell user to click **↺ Reload**, re-present. Repeat until proceed.

**Confirm and Write Final Documentation**

Once confirmed:

1. Read the saved document
2. Insert decision header after the title:
   ```markdown
   **Confirmed:** {Short Title}
   **Decision date:** {ISO date}
   ```
3. Update `### After` within `## Revision` with the recommendation's Infrastructure Layout diagram (if it was a placeholder)
4. Write the `## Architecture Decision Record` section — read `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/adr-guide.md` for the required format. Include: Context (the pain points and constraints that drove the review), Decision (what was chosen and why), Consequences (positive + trade-offs), Rejected Alternatives (less invasive and more aggressive approaches with specific reasons — future engineers will wonder why microservices weren't chosen; give them the answer), and Review Trigger.

**Save Permanent Documentation and Stop Server**

1. Update `/tmp/archimind-viewer/content.md` with the Write tool. Inform the user: "The viewer is updated — click **↺ Reload** in the sidebar to see the final state."
2. Compute timestamp: `node -e 'process.stdout.write(String(Date.now()))'` (macOS) or `date +%s%3N` (Linux). Derive topic slug from the system name (e.g., `payment-service`, `ecommerce-api`).
3. Save permanent technical documentation:

```bash
mkdir -p docs/archimind/architecture
```

Write `docs/archimind/architecture/{timestamp_ms}-{topic}-review.md`. Include: `## Architecture Diagram` section, ERD (if applicable), Design Rationale, Architecture Decision Record, Before/After Revision section. To re-visualize later: `bash "$CLAUDE_PLUGIN_ROOT/scripts/open-doc.sh" docs/archimind/architecture/{timestamp_ms}-{topic}-review.md`.

4. Stop the viewer server:

```bash
bash "$CLAUDE_PLUGIN_ROOT/scripts/stop-server.sh"
```

---

## Document Structure Convention

<!-- Keep in sync with design-architecture/SKILL.md and visualize/SKILL.md -->

The viewer parses these heading patterns from `content.md`:

- `## Architecture Diagram` → content renders directly as the main view (no tab bar)
- `## ERD` → ERD nav view
- `## Revision` + `### Before` / `### After` → Before/After tabs

## Mermaid Diagram Guidelines

Read `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/mermaid-guidelines.md` for common diagram rules. Review-specific conventions:

- Current state diagram goes in `## Revision / ### Before`
- Proposed state diagram goes in `## Revision / ### After` and within each option section
- Mark changed/new components with `[NEW]` or `[UPDATED]` in `flowchart` (Logical Architecture) node names only — **never inside `architecture-beta` labels** (causes parse errors; append text without brackets instead)
- Mark problematic current-state nodes with `⚠` in the label (`flowchart TD` / Before diagram only)

## Additional Resources

- **`$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/engineering-principles.md`** — 10 guiding principles for acting as a Senior Software Engineer. Read at the start of every review session.
- **`$CLAUDE_PLUGIN_ROOT/skills/review-architecture/references/review-checklist.md`** — Structured checklist (12 categories: scalability, coupling, data consistency, observability, security, operational complexity, distributed systems, SPOF, disaster recovery, technical debt, cost, API versioning). Read during Stage 1 analysis.
- **`$CLAUDE_PLUGIN_ROOT/skills/review-architecture/references/anti-patterns.md`** — Canonical antipattern names (God Service, Shared DB, Chatty Microservices, Big Bang Migration, etc.). Read when naming identified problems and specifying migration approach.
- **`$CLAUDE_PLUGIN_ROOT/skills/review-architecture/references/output-template.md`** — Full document scaffold for review output. **Read-only — never write to it.** Read during Stage 2 to understand required section structure.
- **`$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/adr-guide.md`** — ADR format. Read during Stage 4 when writing the Architecture Decision Record.
- **`$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/threat-model-guide.md`** — STRIDE methodology. Read when the existing system has compliance requirements (SOC 2, GDPR, PCI DSS, HIPAA) or when a security gap is identified in the review. Include a STRIDE table in the redesign's Final Documentation security section if the system handles sensitive data.
- **`$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/database-selection-guide.md`** — Comprehensive database selection guide. Read when proposing database changes.
- **`$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/observability-guide.md`** — Observability stack guide. Read when proposing observability improvements.
- **`$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/mermaid-guidelines.md`** — Diagram type selection, node limits, edge labeling, and review-specific node labeling conventions.

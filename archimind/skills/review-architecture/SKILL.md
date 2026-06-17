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

Follow the **Spec → Plan → Review → Ship** workflow strictly — collect and analyze the existing architecture first, generate three redesign options and write them to content.md, present a compact summary for user confirmation, then open the visual viewer for final selection. **Never output the full redesign options in the chat response** — the viewer is the display surface. Keep chat responses brief status updates.

## Workflow

At the very start, call **TaskCreate** to create one task per step:
1. Spec — Collect existing architecture information
2. Spec — Perform architecture analysis
3. Spec — Confirm analysis summary
4. Plan — Generate 3 redesign options and Recommendation → write content.md
5. Review — Present redesign summary, confirm or iterate
6. Ship — Open viewer and await option selection
7. Ship — Mark chosen option and write decision notes
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
- If no metrics exist, flag this explicitly: **"Lack of observability means the redesign is based on assumptions, not evidence."** Recommending an observability improvement as part of Option 1 is almost always warranted.

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

### Stage 2: Plan — Generate Redesign Options

After confirmation, scaffold the review document and compose three redesign options directly into `/tmp/archimind-viewer/content.md` using the Write tool. Print a brief status line like "Planning 3 redesign options…" while writing. **Do not open the viewer yet — that happens in Stage 4: Ship.**

Structure the document with `## Architecture Diagram`, `## ERD`, `## Revision`, and `## Recommendation` top-level sections. The `## Revision` section must contain `### Before` and `### After` subsections — the viewer renders these as Before/After tabs.

For the complete document scaffold (all required headings and placeholder text), read: `$CLAUDE_PLUGIN_ROOT/skills/review-architecture/references/output-template.md` — **read-only; never write to it.**

Key structural rules:
- Use `### Option N:` (level-3) within `## Architecture Diagram` — the viewer splits on these to create option tabs
- The `### After` diagram in `## Revision` is initially a placeholder — Stage 4 replaces it with the selected option's Infrastructure Layout diagram

#### Option 1: Conservative Refactor
- Minimal structural change. Fix the most critical pain points without re-architecture.
- Approach: Add caching, extract one overloaded component, fix query performance, improve observability.
- Migration effort: Days to weeks.

#### Option 2: Moderate Redesign
- Targeted structural changes to address systemic issues.
- Approach: Decompose tightly-coupled modules, introduce event bus for async workloads, add read replica, migrate one component to a better-fit database.
- Migration effort: Weeks to months.

#### Option 3: Full Overhaul
- Re-architect the system from scratch. Highest risk, highest reward.
- Approach: Adopt a fundamentally different architecture (microservices, event-driven, serverless).
- Migration effort: Months to quarters. Use Strangler Fig or parallel run — not big bang. See `$CLAUDE_PLUGIN_ROOT/skills/review-architecture/references/anti-patterns.md` for why.

#### Required Sections Per Option

Each `### Option N:` section must include **three Mermaid diagrams** and a standard set of subsections. Read `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/mermaid-guidelines.md` for review-specific diagram conventions (mark changed nodes with `[NEW]`, problematic nodes with `⚠`).

Each option must include the three Mermaid diagrams (**Infrastructure Layout**, **Request Flow**, **Logical Architecture**) and the following `####` subsections (full scaffold in `$CLAUDE_PLUGIN_ROOT/skills/review-architecture/references/output-template.md`):

- **What Changes** — current state → proposed state, component by component
- **Key Improvements** — how each identified weakness is addressed
- **Technology Changes** — table: Component / Current / Proposed / Reason
- **Data Layer Changes** — store migrations, new stores, removed stores
- **Observability Changes** — what observability gaps the redesign closes
- **Technology Decision Rationale** — for each major new technology: why chosen, better than alternatives, required skills, ecosystem
- **Future Impact** — 6-month / 1-year / 3-year table + scalability ceiling, operational overhead, reversibility, vendor lock-in
- **Migration Path** — phased steps, Strangler Fig or parallel-run approach, rollback strategy
- **Risks & Mitigations** — table: Risk / Likelihood / Impact / Mitigation
- **When to Choose This Option** — 2–3 bullets: team/timeline/budget scenarios

#### Recommendation Section

After all three options, add `## Recommendation` with a **Narrative** — 4–6 sentences stating which redesign is recommended and why, referencing the specific weaknesses it addresses and the team's constraints.

Save the complete document with the Write tool. **Do not call start-server.sh at this stage.**

---

### Stage 3: Review — Confirm Before Shipping

After writing content.md, present a compact **Plan Summary** in chat to let the user verify the direction before opening the viewer:

---

**Plan Summary**

| Option | Label                 | Short Title | Key Changes                                     |
|--------|-----------------------|-------------|-------------------------------------------------|
| 1      | Conservative Refactor | {Name}      | {e.g., Add Redis cache + query indexes}         |
| 2      | Moderate Redesign     | {Name}      | {e.g., Extract auth service + add read replica} |
| 3      | Full Overhaul         | {Name}      | {e.g., Microservices + Kafka + CQRS}            |

**Recommended:** Option N — {1–2 sentence rationale citing the specific weaknesses it addresses.}

---

Use **AskUserQuestion** to ask the user what to do next:

```
question: "Three redesign options are ready. What would you like to do?"
header: "Next Step"
options:
  - label: "Ship — open the visual viewer"
    description: "Open the interactive viewer to compare all three options side by side and make your final choice"
  - label: "Iterate — adjust before viewing"
    description: "Request changes to the options, tech choices, or migration approach before opening the viewer"
```

If the user chooses **Iterate**: apply the requested changes to `/tmp/archimind-viewer/content.md`, update the Plan Summary table, and re-present Stage 3. Repeat until the user chooses **Ship**.

---

### Stage 4: Ship — Visual Selection and Final Documentation

Open the viewer and invite the user to compare redesign options visually:

```bash
open "$(bash "$CLAUDE_PLUGIN_ROOT/scripts/start-server.sh")"
```

Post a brief chat message: "Viewer is open at http://localhost:PORT — use **Architecture Diagram** to compare redesign options and **Revision** to see the Before/After comparison. Select an option when ready."

**Option Selection**

Use **AskUserQuestion** to present the selection:

```
question: "Which redesign would you like to proceed with?"
header: "Select Option"
options:
  - label: "Option 1 — Conservative Refactor"
    description: <one-line summary of what this option changes>
  - label: "Option 2 — Moderate Redesign"
    description: <one-line summary of what this option changes>
  - label: "Option 3 — Full Overhaul"
    description: <one-line summary of what this option changes>
```

Allow iterations if the user wants adjustments. Re-present AskUserQuestion after each change. Do not proceed until the user makes an explicit choice.

**Mark the Chosen Option**

Update `/tmp/archimind-viewer/content.md` using the Write tool:
1. Insert decision header after the title:
   ```markdown
   **Selected:** Option N — {Label}: {Short Title}
   **Decision date:** {ISO date}
   ```
2. Replace the placeholder diagram in `### After` within `## Revision` with the selected option's Infrastructure Layout diagram
3. Append a `## Decision Notes` section with user-requested adjustments, migration timing, and next steps

**Save Permanent Documentation and Stop Server**

> **Note**: Review workflows do not produce a `## Final Documentation` section. The `## Decision Notes` block captures the rationale, adjustments, and next steps.

1. Inform the user: "The viewer is updated — click **↺ Reload** in the sidebar to see the final state."
2. Compute timestamp: `node -e 'process.stdout.write(String(Date.now()))'` (macOS) or `date +%s%3N` (Linux). Derive topic slug from the system name (e.g., `payment-service`, `ecommerce-api`).
3. Save permanent technical documentation:

```bash
mkdir -p docs/archimind/architecture
```

Write `docs/archimind/architecture/{timestamp_ms}-{topic}-review.md` containing **only the chosen redesign option** — not all three. Structure it as:

```markdown
# Architecture Review: {System Name}

**Generated:** {ISO date}
**Selected:** Option N — {Label}: {Short Title}
**Decision date:** {ISO date}

## Architecture Diagram

### Option N: {Label} — {Short Title}

{Selected option's full content — all subsections}

## ERD
...

## Revision

### Before
...

### After
{Selected option's proposed architecture}

## Recommendation

{4–6 sentence narrative: which option was chosen, why, citing the specific weaknesses it addresses and the constraints that drove the decision.}

## Decision Notes
...
```

Omit the two options that were not selected. To re-visualize later: `bash "$CLAUDE_PLUGIN_ROOT/scripts/open-doc.sh" docs/archimind/architecture/{timestamp_ms}-{topic}-review.md`.

4. Stop the viewer server:

```bash
bash "$CLAUDE_PLUGIN_ROOT/scripts/stop-server.sh"
```

---

## Document Structure Convention

<!-- Keep in sync with design-architecture/SKILL.md and visualize/SKILL.md -->

The viewer parses these heading patterns from `content.md`:

- `## Architecture Diagram` + `### Option N:` subheadings → option tabs
- `## ERD` → ERD nav view
- `## Revision` + `### Before` / `### After` → Before/After tabs

**Critical**: Use `### Option N:` (level-3) within `## Architecture Diagram`, not `## Option N:` (level-2). The viewer splits on level-3 headings to create option tabs.

Review option headings must follow this exact format within `## Architecture Diagram`:
```
### Option 1: Conservative Refactor — {Title}
### Option 2: Moderate Redesign — {Title}
### Option 3: Full Overhaul — {Title}
```

## Mermaid Diagram Guidelines

Read `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/mermaid-guidelines.md` for common diagram rules. Review-specific conventions:

- Current state diagram goes in `## Revision / ### Before`
- Proposed state diagram goes in `## Revision / ### After` and within each option section
- Mark changed/new components with `[NEW]` or `[UPDATED]` in `flowchart` (Logical Architecture) node names only — **never inside `architecture-beta` labels** (causes parse errors; append text without brackets instead)
- Mark problematic current-state nodes with `⚠` in the label (`flowchart TD` / Before diagram only)

## Additional Resources

- **`$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/engineering-principles.md`** — 10 guiding principles for acting as a Senior Software Engineer. Read at the start of every review session.
- **`$CLAUDE_PLUGIN_ROOT/skills/review-architecture/references/review-checklist.md`** — Structured checklist (12 categories: scalability, coupling, data consistency, observability, security, operational complexity, distributed systems, SPOF, disaster recovery, technical debt, cost, API versioning). Read during Stage 1 analysis.
- **`$CLAUDE_PLUGIN_ROOT/skills/review-architecture/references/anti-patterns.md`** — Canonical antipattern names (God Service, Shared DB, Chatty Microservices, Big Bang Migration, etc.). Read when naming identified problems and specifying Option 3 migration approach.
- **`$CLAUDE_PLUGIN_ROOT/skills/review-architecture/references/output-template.md`** — Full document scaffold for review output. **Read-only — never write to it.** Read during Stage 2 to understand required section structure.
- **`$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/database-selection-guide.md`** — Comprehensive database selection guide. Read when proposing database changes.
- **`$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/observability-guide.md`** — Observability stack guide. Read when proposing observability improvements.
- **`$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/mermaid-guidelines.md`** — Diagram type selection, node limits, edge labeling, and review-specific node labeling conventions.

---
name: review-architecture
description: This skill should be used when the user asks to "review architecture", "analyze my architecture", "audit the architecture", "review my system design", "improve my system", "refactor architecture", "redesign my system", "what's wrong with my architecture", "critique my design", "help me improve my existing system", "is my architecture good", "identify bottlenecks in my architecture", or provides an existing architecture description, diagram, or codebase structure for evaluation.
---

# Review Architecture

Act as a **Senior Software Engineer** conducting a formal architecture review. Read and apply `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/engineering-principles.md` throughout this workflow.

Core behaviors:
- Prioritize evidence over intuition — verify pain points with metrics before proposing changes
- Identify SPOFs, technical debt, security gaps, scalability ceilings, and disaster recovery gaps systematically
- Recommend the least invasive change that delivers the most risk reduction
- Never propose a higher-complexity option unless the simpler option demonstrably fails to address the root causes

Analyze an existing software architecture, identify weaknesses and opportunities for improvement, then propose three redesign options — **Conservative Refactor**, **Moderate Redesign**, and **Full Overhaul** — each with Mermaid diagrams, rationale, and migration path. Open a static HTML viewer so the user can compare options before selecting.

## Workflow

**Tools — create tasks and use structured questions throughout:**

At the very start, call **TaskCreate** to create one task per step:
1. Collect existing architecture information
2. Perform architecture analysis
3. Confirm analysis summary
4. Scaffold review document structure
5. Generate three redesign options
6. Add Recommendation section
7. Write content.md and start viewer server
8. User selects option
9. Mark the chosen option and write decision notes
10. Save final docs and stop server

Mark each task `in_progress` when starting it and `completed` when done.

### 1. Collect Existing Architecture Information

Use **AskUserQuestion** to gather context before the user provides free-form details. Ask up to 4 questions at once to understand:
- What type of system is it? (web app, backend API, data pipeline, mobile backend, etc.)
- What are the primary pain points that prompted this review?
- What constraints exist that cannot change? (legacy integrations, compliance, team skills)
- How is the system currently deployed? (cloud/on-premise, containerized, serverless, etc.)

Then ask the user to provide any relevant artefacts:

- **Description**: What the system does, how it's structured today
- **Tech stack**: Languages, frameworks, databases, infra currently used
- **Architecture diagram** or a textual description of services/components

Read any relevant files the user points to (e.g., `docker-compose.yml`, `package.json`, database migration files, service directories).

### 2. Perform Architecture Analysis

#### Measure Before Redesigning

Before analyzing weaknesses, confirm the stated pain points are backed by observable data — not assumptions. Ask:
- Are there existing metrics? (p50/p95/p99 latencies, error rates, throughput, slow query logs)
- Which specific operations are slow or failing — exact endpoints, jobs, or queries?
- If no metrics exist, flag this explicitly: **"Lack of observability means the redesign is based on assumptions, not evidence."** Recommending an observability improvement (structured logging, metrics endpoint) as part of Option 1 is almost always warranted.

Redesigning without measurement data risks solving the wrong problem. A query missing an index often outperforms a microservices migration.

Evaluate the existing architecture against the checklist in `$CLAUDE_PLUGIN_ROOT/skills/review-architecture/references/review-checklist.md`. Produce an **Analysis Summary** covering:

- **Strengths**: What the current architecture does well
- **Weaknesses**: Specific identified problems (scalability, coupling, observability, data, security, operational)
- **Antipatterns found**: Reference `$CLAUDE_PLUGIN_ROOT/skills/review-architecture/references/anti-patterns.md` for canonical names
- **Root causes**: Why each weakness exists

Keep the analysis concise: 3–6 bullet points per category. Be specific ("single DB handles both OLTP and analytics queries, causing lock contention"), not vague.

### 3. Confirm Analysis Summary

After completing the analysis, display a summary to the user **before** generating redesign options. This ensures the assessment is accurate.

Present the summary in this format, then wait for confirmation:

---

**Analysis Summary**

**Current Architecture:** {1–2 sentence description of what was understood}

| Category                    | Finding                                                                                                                   |
|-----------------------------|---------------------------------------------------------------------------------------------------------------------------|
| Tech stack                  | {languages, frameworks, databases identified}                                                                             |
| Architecture style          | {monolith / modular monolith / microservices / etc.}                                                                      |
| Strengths                   | {1–2 key positives}                                                                                                       |
| Primary pain points         | {top 2–3 issues identified}                                                                                               |
| Antipatterns detected       | {canonical names from `$CLAUDE_PLUGIN_ROOT/skills/review-architecture/references/anti-patterns.md`, or "None identified"} |
| Constraints (cannot change) | {legacy integrations, compliance, team skills, etc.}                                                                      |

**Root cause hypothesis:** {1–2 sentences on why the main issues exist — e.g., "The system evolved from a monolith without service boundaries, resulting in tight coupling that now blocks independent scaling."}

> Does this accurately capture the current state and issues? Reply with any corrections, or say **"Yes, proceed"** to generate the redesign options.

---

Wait for the user to confirm or correct before proceeding to Step 4. If the user provides corrections, update the summary and re-confirm.

### 4. Scaffold the Review Document Structure

Structure the review document with `## Architecture Diagram`, `## ERD`, `## Revision`, and `## Recommendation` top-level sections. The `## Revision` section must contain `### Before` and `### After` subsections — this is what the viewer renders as Before/After tabs.

**Viewer content path**: `/tmp/archimind-viewer/content.md`

For the complete document scaffold (all required headings, placeholder text, and subsection structure), read:
`$CLAUDE_PLUGIN_ROOT/skills/review-architecture/references/output-template.md` — **read-only; never write to it.**

Key structural rules:
- Use `### Option N:` (level-3) within `## Architecture Diagram` — the viewer splits on these to create option tabs
- The `## Recommendation` section in the draft (written in Step 7) uses blank `/10` placeholders; Step 6 fills actual scores before writing to disk
- The `### After` diagram in `## Revision` is initially a placeholder — Step 9 replaces it with the selected option's Infrastructure Layout diagram

### 5. Generate Three Redesign Options

Present three options within the `## Architecture Diagram` section using `### Option N:` sub-headings (the viewer renders these as tabs).

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

### 6. Add Recommendation

After generating all three options, write a `## Recommendation` section **with actual scores filled in** (not the blank `/10` scaffold from Step 4). This section is included in the `## Recommendation` block written to `/tmp/archimind-viewer/content.md` in Step 7 — it is written **before** the user is asked to select, so the viewer shows the Recommendation tab immediately.

1. **Confidence Scores table** — rate each option on four dimensions (0–10). The viewer renders `X/10` table cells as visual progress bars automatically. Use this column structure with FILLED SCORES:

```markdown
### Confidence Scores

| Option | Migration Effort | Risk Reduction | Team Fit | Cost | Overall |
|--------|-----------------|---------------|----------|------|---------|
| Option 1 — Conservative Refactor | 9/10 | 6/10 | 9/10 | 8/10 | **8.0/10** |
| Option 2 — Moderate Redesign      | 6/10 | 8/10 | 7/10 | 7/10 | **7.0/10** |
| Option 3 — Full Overhaul          | 3/10 | 9/10 | 5/10 | 5/10 | **5.5/10** |
```

Score criteria for review context:
- **Migration Effort** — how achievable the migration is (10 = easiest/lowest risk)
- **Risk Reduction** — how much this option addresses the identified weaknesses
- **Team Fit** — how well it matches the team's current skills and constraints
- **Cost** — relative infra + operational cost change vs. current state

2. **Narrative** — 4–6 sentences stating which redesign is recommended, why, citing the highest Overall score and referencing the specific weaknesses it addresses.

#### Required Sections Per Option

Each `### Option N:` section must include **three Mermaid diagrams** and the sections below. Read `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/mermaid-guidelines.md` for review-specific diagram conventions (mark changed nodes with `[NEW]`, problematic nodes with `⚠`).

```markdown
#### Infrastructure Layout (architecture-beta)
PROPOSED infrastructure topology with icons. Mark new/added services clearly.

#### Request Flow (sequenceDiagram)
Primary user request through the PROPOSED architecture.

#### Component Flow (flowchart TD)
Logical data flow between proposed components. Mark changed/new components with [NEW] labels.

#### What Changes
Bulleted list comparing current state vs. proposed state.

#### Key Improvements
How this option addresses each identified weakness.

#### Technology Changes
| Component | Current | Proposed | Reason |

#### Data Layer Changes
Which databases are added, removed, or replaced — and why.
Non-relational stores introduced (cache, search, analytics) and rationale.
Schema migration approach and data migration steps.

#### Object Storage Changes (if applicable)
Changes to file/blob storage strategy.

#### Observability Changes
OpenTelemetry-based instrumentation improvements.
New monitoring, tracing, alerting components.

#### Technology Decision Rationale
For each proposed change: why this replaces the current, alternatives considered, team skills required.

#### Future Impact
| Timeframe | Impact |
| 6 months  | ... |
| 1 year    | ... |
| 3 years   | ... |
Scalability improvement, operational overhead change, reversibility.

#### Migration Path
Step-by-step migration approach. Rollback strategy.
For Option 3: specify Strangler Fig, parallel run, or big bang and justify.

#### Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |

#### When to Choose This Option
2–3 bullets for ideal scenario.
```

### 7. Write Content and Open Viewer for Comparison

Write the draft and immediately open the viewer so the user can compare all three redesign options with their diagrams **before selecting**:

1. Use the **Write tool** to save the draft to `/tmp/archimind-viewer/content.md`.
2. Start the viewer server and open the browser — **run as a single command**:

```bash
open "$(bash "$CLAUDE_PLUGIN_ROOT/scripts/start-server.sh")"
```

Inform the user the viewer is open — use the **Architecture Diagram** nav to compare each redesign option's diagram, and the **Revision** nav to see the Before/After comparison. When ready, choose the option they'd like to proceed with.

### 8. Require Redesign Selection (mandatory)

**The work is not complete until the user has explicitly chosen one redesign option.** Use **AskUserQuestion** to present the selection:

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

Iterate if the user wants adjustments. Re-present the AskUserQuestion selection after adjustments. Do not proceed to Step 9 until the user states an explicit choice.

### 9. Mark the Chosen Option

1. Update `/tmp/archimind-viewer/content.md` (use the Write tool to overwrite):
   - Insert decision header after the title:
     ```markdown
     **Selected:** Option N — {Label}: {Short Title}
     **Decision date:** {ISO date}
     ```
   - Replace the placeholder diagram in `### After` within `## Revision` with the selected option's Infrastructure Layout diagram
   - Append a `## Decision Notes` section with user-requested adjustments, migration timing, and next steps

### 10. Save Final Documentation and Stop Server

> **Note**: Review workflows do not produce a `## Final Documentation` section. The `## Decision Notes` block serves that purpose — it captures the rationale, adjustments, and next steps that would otherwise go in Final Documentation.

After updating the content:

1. Inform the user: "The viewer is updated — click **↺ Reload** in the sidebar to see the final state."
2. Compute timestamp: `node -e 'process.stdout.write(String(Date.now()))'` (macOS) or `date +%s%3N` (Linux). Derive topic slug from the system name (e.g., `payment-service`, `ecommerce-api`).
3. Save permanent technical documentation to the user's project:

```bash
mkdir -p docs/archimind/architecture
```

Then use the **Write tool** to write `docs/archimind/architecture/{timestamp_ms}-{topic}-review.md`. **This file must contain only the chosen redesign option** — not all three. Structure it as:

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

### Confidence Scores

| Option | Migration Effort | Risk Reduction | Team Fit | Cost | Overall |
|--------|-----------------|---------------|----------|------|---------|
| Option 1 — Conservative Refactor | X/10 | X/10 | X/10 | X/10 | **X.X/10** |
| Option 2 — Moderate Redesign      | X/10 | X/10 | X/10 | X/10 | **X.X/10** |
| Option 3 — Full Overhaul          | X/10 | X/10 | X/10 | X/10 | **X.X/10** |

{Copy filled scores from Step 6. 4–6 sentences: which option was chosen, why, citing the highest Overall score and the weaknesses it addresses. Acknowledge the main trade-off.}

## Decision Notes
...
```

Omit the two options that were not selected. To re-visualize later: `bash "$CLAUDE_PLUGIN_ROOT/scripts/open-doc.sh" docs/archimind/architecture/{timestamp_ms}-{topic}-review.md`.

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
- Mark changed/new components with `[NEW]` or `[UPDATED]` node labels
- Mark problematic current-state nodes with `⚠` in the label (Before diagram only)

## Additional Resources

- **`$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/engineering-principles.md`** — 10 guiding principles for acting as a Senior Software Engineer. Read at the start of every review session.
- **`$CLAUDE_PLUGIN_ROOT/skills/review-architecture/references/review-checklist.md`** — Structured checklist (12 categories: scalability, coupling, data consistency, observability, security, operational complexity, distributed systems, SPOF, disaster recovery, technical debt, cost, API versioning). Read during Step 2 analysis.
- **`$CLAUDE_PLUGIN_ROOT/skills/review-architecture/references/anti-patterns.md`** — Canonical antipattern names (God Service, Shared DB, Chatty Microservices, Big Bang Migration, etc.). Read when naming identified problems and specifying Option 3 migration approach.
- **`$CLAUDE_PLUGIN_ROOT/skills/review-architecture/references/output-template.md`** — Full document scaffold for review output. **Read-only — never write to it.** Read during Step 4 to understand required section structure.
- **`$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/database-selection-guide.md`** — Comprehensive database selection guide. Read when proposing database changes.
- **`$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/observability-guide.md`** — Observability stack guide. Read when proposing observability improvements.
- **`$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/mermaid-guidelines.md`** — Diagram type selection, node limits, edge labeling, and review-specific node labeling conventions.

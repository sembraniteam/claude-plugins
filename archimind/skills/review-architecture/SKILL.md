---
name: Review Architecture
description: This skill should be used when the user asks to "review architecture", "analyze my architecture", "audit the architecture", "review my system design", "improve my system", "refactor architecture", "redesign my system", "what's wrong with my architecture", "critique my design", "help me improve my existing system", "is my architecture good", "identify bottlenecks in my architecture", or provides an existing architecture description, diagram, or codebase structure for evaluation.
---

# Review Architecture

Analyze an existing software architecture, identify weaknesses and opportunities for improvement, then propose three redesign options — **Conservative Refactor**, **Moderate Redesign**, and **Full Overhaul** — each with Mermaid diagrams, rationale, and migration path. Save the output as a timestamped markdown file in `docs/archimind/`.

## Workflow

### 1. Collect Existing Architecture Information

Ask the user to provide one or more of the following:

- **Description**: What the system does, how it's structured today
- **Tech stack**: Languages, frameworks, databases, infra currently used
- **Architecture diagram** or a textual description of services/components
- **Pain points**: What specific problems prompted this review (performance, scalability, maintainability, cost, team friction)?
- **Constraints**: What cannot change (legacy integrations, compliance, team skills)?

Read any relevant files the user points to (e.g., `docker-compose.yml`, `package.json`, database migration files, service directories).

### 2. Perform Architecture Analysis

Evaluate the existing architecture against the checklist in `references/review-checklist.md`. Produce an **Analysis Summary** covering:

- **Strengths**: What the current architecture does well (acknowledge positives)
- **Weaknesses**: Specific identified problems (use the checklist categories: scalability, coupling, observability, data, security, operational)
- **Anti-patterns found**: Reference `references/anti-patterns.md` for canonical names
- **Root causes**: Why each weakness exists (technical debt, premature optimization, changing requirements)

Keep the analysis concise: 3–6 bullet points per category. Avoid vague statements like "poor performance" — be specific ("single DB handles both OLTP and analytics queries, causing lock contention").

### 3. Document the Current State

Before generating redesign options, produce a "Current Architecture" section in the output document. This baseline must come first so options can reference it clearly.

````markdown
## Current Architecture

### Overview
{analysis summary — 2–4 sentences}

### Current Architecture Diagram
```mermaid
flowchart TD
  ...
```

### Identified Issues
- {Issue 1 — specific, cites anti-pattern name if applicable}
- {Issue 2}
````

The diagram should reflect the actual current topology (not the desired state). Use `flowchart TD`. Mark problematic components with a `[⚠ issue]` label.

### 4. Generate Three Redesign Options

Present three options based on the severity and nature of identified issues:

#### Option 1: Conservative Refactor
- **Profile**: Minimal structural change. Fix the most critical pain points without re-architecture. Lowest risk, quickest wins.
- **Approach**: Refactor within existing boundaries — introduce caching, extract a service for a single overloaded component, add connection pooling, improve query performance.
- **Migration effort**: Days to weeks.

#### Option 2: Moderate Redesign
- **Profile**: Targeted structural changes to address systemic issues. Introduce new patterns where justified.
- **Approach**: Decompose tightly-coupled modules, introduce an event bus for async workloads, add a read replica, migrate to a better-fit database for specific use cases.
- **Migration effort**: Weeks to months.

#### Option 3: Full Overhaul
- **Profile**: Re-architect the system from scratch with the lessons learned. Highest risk, highest reward.
- **Approach**: Adopt a fundamentally different architecture (microservices, event-driven, serverless) that solves structural root causes.
- **Migration effort**: Months to quarters. Prefer **Strangler Fig** or **parallel run** approach over big bang. See the Big Bang Migration entry in `references/anti-patterns.md` for why big bang is high-risk. Document rollback strategy at each phase boundary.

### 5. Required Sections Per Option

Each option must include all of these sections:

```
## Option N: {Label} — {Short Title}

### What Changes
Bulleted list comparing current state vs. proposed state.

### Architecture Diagram
Mermaid diagram of the proposed architecture (NOT the current state).

### Key Improvements
How this option addresses each identified weakness from Step 2.

### Technology Changes
| Component       | Current           | Proposed          | Reason                                      |
|-----------------|-------------------|-------------------|---------------------------------------------|
| Primary DB      | ...               | ...               | relational / document / key-value / ...     |
| Cache           | ...               | ...               | ...                                         |
| Search          | ...               | ...               | ...                                         |
| Backend         | ...               | ...               | ...                                         |
| Infra           | ...               | ...               | ...                                         |

(Include rows for all components that change. For databases, specify the category change:
e.g., "relational → document" or "single SQL → SQL + Redis + ClickHouse".)

### Data Layer Changes
Describe the data strategy changes in detail:
- Which databases are added, removed, or replaced — and why (not just the engine name, but the category rationale)
- Any non-relational stores introduced (cache, search, analytics, graph) and why they were not needed before
- Schema migration approach
- Data migration steps (if moving data between engines)

### Technology Decision Rationale
For each proposed technology change, explain:
- *Why this specific technology replaces the current one*: Specific technical reason tied to the identified issue
- *What the alternative would have been*: One or two other options considered and why they were ruled out
- *Team skills required*: New knowledge the team needs to operate this

### Future Impact
Describe the long-term consequences of this redesign option:

| Timeframe | Impact                                                                      |
|-----------|-----------------------------------------------------------------------------|
| 6 months  | Team ramp-up, what improves immediately, first new pain points              |
| 1 year    | First scaling or maintenance ceiling encountered                            |
| 3 years   | Total cost of ownership, evolution needed, hiring story                     |

Also address:
- **Scalability improvement**: How does this handle 10× the current load vs. the current system?
- **Operational overhead change**: More or less complex than today?
- **Reversibility**: How difficult is it to undo this change or migrate further?

### Migration Path
Step-by-step migration approach. Include rollback strategy.
For Option 3: specify Strangler Fig, parallel run, or big bang and justify the choice.

### Risks & Mitigations
| Risk                     | Likelihood | Impact | Mitigation              |
|--------------------------|------------|--------|-------------------------|

### When to Choose This Option
2–3 bullets for ideal scenario.
```

### 6. Save the Document

1. Compute timestamp in milliseconds via shell tool:
   - Linux: `date +%s%3N`
   - macOS: `node -e 'process.stdout.write(String(Date.now()))'`
2. Create `docs/archimind/` if needed
3. Determine topic slug from the system name (e.g., `payment-service`, `ecommerce-api`)
4. Save to: `docs/archimind/{timestamp_ms}_{topic}-architecture-review.md`
5. Inform user of saved path

### 7. Offer to Visualize

After saving, prompt: "Would you like to open the viewer to compare the redesign options? Use `/archimind:visualize` to launch the diagram server."

### 8. Require Redesign Selection (mandatory)

**The work is not complete until the user has explicitly chosen one redesign option.** After presenting the options and offering visualization, prompt:

> "Which redesign would you like to proceed with — Option 1 (Conservative Refactor), Option 2 (Moderate Redesign), or Option 3 (Full Overhaul)? Request modifications before deciding if needed."

Iterate if the user wants adjustments (e.g., "Option 2 but keep MySQL", "Option 3 with a phased rollout"). Re-save the document after each significant change. Do not proceed to Step 9 until the user states an explicit choice.

### 9. Mark the Chosen Option

Once a choice is confirmed:

1. Read the saved review document
2. Insert a decision header block right after the title:
   ```markdown
   **Selected:** Option N — {Label}: {Short Title}
   **Decision date:** {ISO date}
   ```
3. Append `✅ SELECTED` to the chosen option's heading:
   ```markdown
   ## Option 2: Moderate Redesign — Extract Analytics Service + Read Replicas ✅ SELECTED
   ```
4. Append a brief `## Decision Notes` section capturing user-requested adjustments, migration timing, and prioritized next steps.

### 10. Stop the Viewer Server

After the choice is finalized:

1. Check if the viewer is running: `[ -f .archimind.pid ]` in the user's project root
2. If running, ask: "Redesign finalized. Stop the diagram viewer now? (recommended)"
3. On confirmation, run: `bash "$CLAUDE_PLUGIN_ROOT/scripts/stop-server.sh"`
4. Report: "Decision saved to `{filepath}`. Viewer stopped." (or "Viewer was not running.")

This is the natural end of the workflow. The selected redesign document becomes the source of truth for the migration plan.

## Document Structure Convention

The static site viewer parses headings matching `## Option N:`. Use this exact format. **If the format is not followed, the tab navigation will not render — all options appear as a single document.**

```markdown
## Option 1: Conservative Refactor — Add Caching Layer + Query Optimization
## Option 2: Moderate Redesign — Extract Analytics Service + Read Replicas
## Option 3: Full Overhaul — Event-Driven Microservices with CQRS
```

## Mermaid Diagram Guidelines

- Show the **proposed** architecture in each option diagram (not current state)
- Current state diagram goes in the "Current Architecture" section (Step 3)
- Use `flowchart TD` for service topology
- Mark changed components with `[NEW]` on node labels or edges
- Use `sequenceDiagram` only when the before/after of a specific request lifecycle makes the improvement concrete (e.g., showing async vs. sync checkout flow); do not add sequence diagrams to every option

## Additional Resources

All paths below are relative to this skill file's directory (`skills/review-architecture/`).

- **`references/review-checklist.md`** — Structured checklist (scalability, coupling, observability, data, security, operational). Read during Step 2 analysis.
- **`references/anti-patterns.md`** — Canonical anti-pattern names and descriptions (God Service, Shared DB, Chatty Microservices, etc.). Reference when naming identified problems and when specifying Option 3 migration approach.
- **`../design-architecture/references/database-selection-guide.md`** — Comprehensive database selection guide (relational, document, key-value, column-family, time-series, graph, search, NewSQL). Read when proposing database changes in any redesign option.
- **`../design-architecture/references/observability-guide.md`** — Observability stack guide (OpenTelemetry, Loki, Prometheus, Jaeger/Tempo, SigNoz, Uptrace, Grafana Stack, Datadog). Read when proposing observability improvements in any redesign option.

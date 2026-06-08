---
name: Review Architecture
description: This skill should be used when the user asks to "review architecture", "analyze my architecture", "audit the architecture", "review my system design", "improve my system", "refactor architecture", "redesign my system", "what's wrong with my architecture", "critique my design", "help me improve my existing system", "is my architecture good", "identify bottlenecks in my architecture", or provides an existing architecture description, diagram, or codebase structure for evaluation.
---

# Review Architecture

Analyze an existing software architecture, identify weaknesses and opportunities for improvement, then propose three redesign options — **Conservative Refactor**, **Moderate Redesign**, and **Full Overhaul** — each with Mermaid diagrams, rationale, and migration path. Save the output as a timestamped Markdown file in `docs/archimind/architecture/`.

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

- **Strengths**: What the current architecture does well
- **Weaknesses**: Specific identified problems (scalability, coupling, observability, data, security, operational)
- **Antipatterns found**: Reference `references/anti-patterns.md` for canonical names
- **Root causes**: Why each weakness exists

Keep the analysis concise: 3–6 bullet points per category. Be specific ("single DB handles both OLTP and analytics queries, causing lock contention"), not vague.

### 3. Confirm Analysis Summary

After completing the analysis, display a summary to the user **before** generating redesign options. This ensures the assessment is accurate.

Present the summary in this format, then wait for confirmation:

---

**Analysis Summary**

**Current Architecture:** {1–2 sentence description of what was understood}

| Category | Finding |
|---|---|
| Tech stack | {languages, frameworks, databases identified} |
| Architecture style | {monolith / modular monolith / microservices / etc.} |
| Strengths | {1–2 key positives} |
| Primary pain points | {top 2–3 issues identified} |
| Antipatterns detected | {canonical names from references/anti-patterns.md, or "None identified"} |
| Constraints (cannot change) | {legacy integrations, compliance, team skills, etc.} |

**Root cause hypothesis:** {1–2 sentences on why the main issues exist — e.g., "The system evolved from a monolith without service boundaries, resulting in tight coupling that now blocks independent scaling."}

> Does this accurately capture the current state and issues? Reply with any corrections, or say **"Yes, proceed"** to generate the redesign options.

---

Wait for the user to confirm or correct before proceeding to Step 4. If the user provides corrections, update the summary and re-confirm.

### 4. Document the Revision in a Single Document

Save the review document with a `## Revision` section that contains both `### Before` and `### After` subsections. This is what the viewer renders as Before/After tabs.

**Document path**: `docs/archimind/architecture/{timestamp_ms}-{topic}-architecture-review.md`

Structure:
```markdown
# Architecture Review: {System Name}

## Architecture Diagram

### Option 1: Conservative Refactor — {Title}
{content}

### Option 2: Moderate Redesign — {Title}
{content}

### Option 3: Full Overhaul — {Title}
{content}

## ERD
{erDiagram if applicable}

## Revision

### Before

{2–4 sentence overview of current architecture}

```mermaid
flowchart TD
  (current state topology — mark problematic nodes with ⚠)
```

**Identified Issues:**
- {Issue 1 — specific, cites antipattern name if applicable}
- {Issue 2}

### After

{Overview of the recommended redesign option and what changes}

```mermaid
flowchart TD
  (proposed architecture topology — mark new/changed nodes with [NEW])
```

**Key Improvements:**
- {How identified weaknesses are addressed}

## Recommendation
```

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
- Migration effort: Months to quarters. Use Strangler Fig or parallel run — not big bang. See `references/anti-patterns.md` for why.

### 6. Required Sections Per Option

Each `### Option N:` section must include:

```
### What Changes
Bulleted list comparing current state vs. proposed state.

### Architecture Diagram
Mermaid flowchart of the PROPOSED architecture (not current state).
Mark changed/new components with [NEW] labels.

### Key Improvements
How this option addresses each identified weakness.

### Technology Changes
| Component | Current | Proposed | Reason |

### Data Layer Changes
Which databases are added, removed, or replaced — and why.
Non-relational stores introduced (cache, search, analytics) and rationale.
Schema migration approach and data migration steps.

### Object Storage Changes (if applicable)
Changes to file/blob storage strategy.

### Observability Changes
OpenTelemetry-based instrumentation improvements.
New monitoring, tracing, alerting components.

### Technology Decision Rationale
For each proposed change: why this replaces the current, alternatives considered, team skills required.

### Future Impact
| Timeframe | Impact |
| 6 months  | ... |
| 1 year    | ... |
| 3 years   | ... |
Scalability improvement, operational overhead change, reversibility.

### Migration Path
Step-by-step migration approach. Rollback strategy.
For Option 3: specify Strangler Fig, parallel run, or big bang and justify.

### Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |

### When to Choose This Option
2–3 bullets for ideal scenario.
```

### 7. Save the Document

1. `node -e 'process.stdout.write(String(Date.now()))'` (macOS/Node) or `date +%s%3N` (Linux)
2. `mkdir -p docs/archimind/architecture/`
3. Topic slug from the system name (e.g., `payment-service`, `ecommerce-api`)
4. Save to: `docs/archimind/architecture/{timestamp_ms}-{topic}-architecture-review.md`
5. Inform the user of the saved path

### 8. Offer to Visualize

Prompt: "Would you like to open the viewer to compare the redesign options? Use `/archimind:visualize` to launch the diagram server."

The viewer's **Architecture Diagram** nav shows the three option tabs. The **Revision** nav shows the Before/After comparison.

### 9. Require Redesign Selection (mandatory)

**The work is not complete until the user has explicitly chosen one redesign option.** After presenting options, prompt:

> "Which redesign would you like to proceed with — Option 1 (Conservative Refactor), Option 2 (Moderate Redesign), or Option 3 (Full Overhaul)? Request modifications before deciding if needed."

Iterate if the user wants adjustments. Do not proceed to Step 10 until the user states an explicit choice.

### 10. Mark the Chosen Option

1. Read the saved review document
2. Insert decision header after the title:
   ```markdown
   **Selected:** Option N — {Label}: {Short Title}
   **Decision date:** {ISO date}
   ```
3. Append `✅ SELECTED` to the chosen option's `### Option N:` heading
4. Update the `### After` section in `## Revision` to show the selected option's proposed architecture (if not already there)
5. Append a `## Decision Notes` section with user-requested adjustments, migration timing, and next steps

### 11. Stop the Viewer Server

After the choice is finalized, offer to stop the viewer:
```bash
bash "$CLAUDE_PLUGIN_ROOT/scripts/stop-server.sh"
```

## Document Structure Convention

The viewer parses these exact heading patterns:

- `## Architecture Diagram` + `### Option N:` subheadings → option tabs in Architecture Diagram nav
- `## ERD` → rendered in ERD nav
- `## Revision` + `### Before` / `### After` → Before/After tabs in Revision nav

**Critical**: Use `### Option N:` (level-3) within `## Architecture Diagram`, not `## Option N:` (level-2) at top level. The viewer splits the `## Architecture Diagram` section by `### ` subheadings to create option tabs.

Review document headings must follow this exact format within `## Architecture Diagram`:
```
### Option 1: Conservative Refactor — {Title}
### Option 2: Moderate Redesign — {Title}
### Option 3: Full Overhaul — {Title}
```

## Mermaid Diagram Guidelines

- Current state diagram goes in `## Revision / ### Before`
- Proposed state diagram goes in `## Revision / ### After` and within each option section
- Use `flowchart TD` for all topology diagrams
- Mark changed components with `[NEW]` or `[UPDATED]` node labels
- Current state: mark problematic nodes with `⚠` in the label

## Additional Resources

- **`references/review-checklist.md`** — Structured checklist (scalability, coupling, observability, data, security, operational). Read during Step 2 analysis.
- **`references/anti-patterns.md`** — Canonical antipattern names (God Service, Shared DB, Chatty Microservices, Big Bang Migration, etc.). Read when naming identified problems and specifying Option 3 migration approach.
- **`$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/database-selection-guide.md`** — Comprehensive database selection guide. Read when proposing database changes.
- **`$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/observability-guide.md`** — Observability stack guide. Read when proposing observability improvements.

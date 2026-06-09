---
name: review-architecture
description: This skill should be used when the user asks to "review architecture", "analyze my architecture", "audit the architecture", "review my system design", "improve my system", "refactor architecture", "redesign my system", "what's wrong with my architecture", "critique my design", "help me improve my existing system", "is my architecture good", "identify bottlenecks in my architecture", or provides an existing architecture description, diagram, or codebase structure for evaluation.
---

# Review Architecture

Analyze an existing software architecture, identify weaknesses and opportunities for improvement, then propose three redesign options — **Conservative Refactor**, **Moderate Redesign**, and **Full Overhaul** — each with Mermaid diagrams, rationale, and migration path. Open a static HTML viewer so the user can compare options before selecting.

## Workflow

**Tools — create tasks and use structured questions throughout:**

At the very start, call **TaskCreate** to create one task per step:
1. Collect existing architecture information
2. Perform architecture analysis
3. Confirm analysis summary
4. Generate three redesign options
5. Write content.md and start viewer server
6. User selects option
7. Mark selection and write decision notes
8. Save final docs and stop server

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

Structure the review document with a `## Revision` section that contains both `### Before` and `### After` subsections. This is what the viewer renders as Before/After tabs. The temp file is written in Step 7 after options are generated.

**Viewer content path**: `$CLAUDE_PLUGIN_ROOT/scripts/site/content.md`

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
<!-- populate this section after generating and presenting all options in Step 5 -->
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
- Migration effort: Months to quarters. Use Strangler Fig or parallel run — not big bang. See `$CLAUDE_PLUGIN_ROOT/skills/review-architecture/references/anti-patterns.md` for why.

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

### 7. Write Content and Open Viewer for Comparison

Write the draft and immediately open the viewer so the user can compare all three redesign options with their diagrams **before selecting**:

1. Use the **Write tool** to save the draft to `$CLAUDE_PLUGIN_ROOT/scripts/site/content.md`.
2. Start the viewer server and open the URL:

```bash
URL=$(bash "$CLAUDE_PLUGIN_ROOT/scripts/start-server.sh")
open "$URL"
```

Inform the user: "The viewer is open — use the **Architecture Diagram** nav to compare each redesign option's diagram, and the **Revision** nav to see the Before/After comparison. When ready, choose the option you'd like to proceed with."

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

1. Update `$CLAUDE_PLUGIN_ROOT/scripts/site/content.md` (use the Write tool to overwrite):
   - Insert decision header after the title:
     ```markdown
     **Selected:** Option N — {Label}: {Short Title}
     **Decision date:** {ISO date}
     ```
   - Append `✅ SELECTED` to the chosen option's `### Option N:` heading
   - Update the `### After` section in `## Revision` to show the selected option's proposed architecture (if not already there)
   - Append a `## Decision Notes` section with user-requested adjustments, migration timing, and next steps

### 10. Save Final Documentation and Stop Server

After updating the content:

1. Inform the user: "The viewer is updated — click **↺ Reload** in the sidebar to see the final state."
2. Compute timestamp: `node -e 'process.stdout.write(String(Date.now()))'` (macOS) or `date +%s%3N` (Linux). Derive topic slug from the system name (e.g., `payment-service`, `ecommerce-api`).
3. Save permanent technical documentation to the user's project:

```bash
mkdir -p docs/archimind/architecture
```

Then use the **Write tool** to write the full content to `docs/archimind/architecture/{timestamp_ms}-{topic}-review.md`.

4. Stop the viewer server:

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

- **`$CLAUDE_PLUGIN_ROOT/skills/review-architecture/references/review-checklist.md`** — Structured checklist (scalability, coupling, observability, data, security, operational). Read during Step 2 analysis.
- **`$CLAUDE_PLUGIN_ROOT/skills/review-architecture/references/anti-patterns.md`** — Canonical antipattern names (God Service, Shared DB, Chatty Microservices, Big Bang Migration, etc.). Read when naming identified problems and specifying Option 3 migration approach.
- **`$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/database-selection-guide.md`** — Comprehensive database selection guide. Read when proposing database changes.
- **`$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/observability-guide.md`** — Observability stack guide. Read when proposing observability improvements.

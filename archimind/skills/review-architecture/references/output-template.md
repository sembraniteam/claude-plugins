# Review Output Template

> **READ-ONLY REFERENCE — NEVER WRITE TO THIS FILE.**
> Output destinations:
> - Viewer draft → `/tmp/archimind-viewer/content.md`
> - Final saved doc → `docs/archimind/architecture/{timestamp_ms}-{topic}-review.md`

Use this template as a scaffold when generating the review document. Replace all placeholder text. Do not omit any section.

---

```markdown
# Architecture Review: {System Name}

**Generated:** {ISO date}

<!-- Fill in after user confirms: -->
<!-- **Confirmed:** {Short Title} -->
<!-- **Decision date:** {ISO date} -->

## Architecture Diagram

{One paragraph: the recommended redesign approach — what changes, what stays, and why this level of intervention is the right fit for the identified pain points and team constraints.}

#### Infrastructure Layout
```mermaid
architecture-beta
  (proposed infrastructure — mark new components without brackets in architecture-beta labels)
```

#### Request Flow
```mermaid
sequenceDiagram
  (proposed request flow)
```

#### Logical Architecture
```mermaid
flowchart TD
  (proposed structural view — mark [NEW] or [UPDATED] nodes for changed components)
```

#### What Changes
- {Current state → Proposed state, component by component}

#### Key Improvements
- {How each identified weakness is addressed}

#### Technology Changes
| Component | Current | Proposed | Reason |
|-----------|---------|----------|--------|

#### Data Layer Changes
{Which databases are added, removed, or replaced and why.}

#### Object Storage Changes (if applicable)
{Changes to file/blob storage strategy — only include if relevant.}

#### Observability Changes
{OpenTelemetry-based improvements, new monitoring/tracing/alerting.}

#### Technology Decision Rationale
{For each proposed change: why it replaces the current, alternatives considered, team skills required.}

#### Future Impact
| Timeframe | Impact |
|-----------|--------|
| 6 months  | ...    |
| 1 year    | ...    |
| 3 years   | ...    |

#### Migration Path
{Step-by-step approach — prefer Strangler Fig or parallel run over big bang. Rollback strategy.}

#### Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|

---

## ERD

{Optional — include erDiagram if schema changes are proposed}

## Revision

### Before

{2–4 sentence overview of the current architecture.}

```mermaid
flowchart TD
  (current state topology — mark problematic nodes with ⚠)
```

**Identified Issues:**
- {Issue 1 — specific, cites antipattern name if applicable}
- {Issue 2}

### After

{Overview of the recommended redesign option and what changes.}

```mermaid
flowchart TD
  (proposed architecture topology — mark new/changed nodes with [NEW])
```

**Key Improvements:**
- {How identified weaknesses are addressed}

## Design Rationale

{4–6 sentences: why this specific redesign was chosen — what pain points it addresses, what less invasive or more aggressive alternatives were considered and ruled out, and what the key trade-off is. Be specific about the constraints that made more drastic change unwarranted (or necessary).}

## Architecture Decision Record

<!-- Read $CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/adr-guide.md for format guidance. -->

**ADR ID:** {timestamp_ms}-{topic}-review
**Date:** {ISO date}
**Status:** Accepted

### Context
{What drove this review — the pain points, their root causes, and the constraints (team, compliance, timeline) that shaped the solution space.}

### Decision
**Chosen:** {Short Title}
{What was decided — the specific redesign approach and its key changes.}

### Consequences
**Positive:** {Pain points addressed, risks reduced}
**Trade-offs accepted:** {Migration effort, new operational burden}
**Watch list:** {When to revisit}

### Rejected Alternatives
| Alternative                          | Reason Rejected                                                   |
|--------------------------------------|-------------------------------------------------------------------|
| Less invasive (e.g., patch fixes)    | {Specific reason — why it wouldn't have addressed the root cause} |
| More aggressive (e.g., full rewrite) | {Specific reason — why the team/timeline/risk didn't justify it}  |

### Review Trigger
{Signal that should prompt revisiting this decision.}
```

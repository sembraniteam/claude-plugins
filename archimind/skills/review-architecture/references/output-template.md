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

<!-- Fill in after user selects: -->
<!-- **Selected:** Option N — {Label}: {Short Title} -->
<!-- **Decision date:** {ISO date} -->

## Architecture Diagram

### Option 1: Conservative Refactor — {Title}

{One paragraph describing the core approach and what minimal changes are made.}

#### Infrastructure Layout
```mermaid
architecture-beta
  (proposed infrastructure — mark new components)
```

#### Request Flow
```mermaid
sequenceDiagram
  (proposed request flow)
```

#### Component Flow
```mermaid
flowchart TD
  (proposed component topology — mark [NEW] or [UPDATED] nodes)
```

#### What Changes
- {Current state → Proposed state, component by component}

#### Key Improvements
- {How each identified weakness is addressed}

#### Technology Changes
| Component | Current | Proposed | Reason |

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
{Step-by-step approach. Rollback strategy.}

#### Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |

#### When to Choose This Option
- {Ideal scenario 1}
- {Ideal scenario 2}

---

### Option 2: Moderate Redesign — {Title}

{Same subsection structure as Option 1}

---

### Option 3: Full Overhaul — {Title}

{Same subsection structure as Option 1. Specify migration approach: Strangler Fig, parallel run, or big bang — and justify.}

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

## Recommendation

### Confidence Scores

| Option | Migration Effort | Risk Reduction | Team Fit | Cost | Overall |
|--------|-----------------|---------------|----------|------|---------|
| Option 1 — Conservative Refactor | X/10 | X/10 | X/10 | X/10 | **X.X/10** |
| Option 2 — Moderate Redesign     | X/10 | X/10 | X/10 | X/10 | **X.X/10** |
| Option 3 — Full Overhaul         | X/10 | X/10 | X/10 | X/10 | **X.X/10** |

{4–6 sentences: which option is recommended and why, citing the highest Overall score and specific weaknesses it addresses.}

## Decision Notes

{User-requested adjustments, migration timing, next steps.}
```

---

## Column Semantics (Review vs. Design)

Review uses **`Migration Effort | Risk Reduction | Team Fit | Cost | Overall`** — migration-centric scores:

| Column | Meaning |
|---|---|
| **Migration Effort** | How achievable is the migration? (10 = easiest/lowest risk) |
| **Risk Reduction** | How much does this option address the identified weaknesses? |
| **Team Fit** | How well does it match team skills and constraints? |
| **Cost** | Relative infra + operational cost change vs. current state |

This differs intentionally from `design-architecture` which uses `Team Fit | Timeline | Scale | Cost` — greenfield design prioritizes timeline and scale, reviews prioritize migration feasibility.

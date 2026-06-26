---
name: impact-matrix
description: This skill should be used when the user asks to prioritize performance issues, says "which fix should I do first", "rank these findings", "what's the highest impact change", "create a priority matrix", "complexity vs impact", "what should we focus on", "help us decide what to fix next sprint", "triage these issues", or provides a list of performance findings that need to be ranked. Applies a structured Complexity × Impact matrix and produces a prioritized action plan.
argument-hint: "[list of findings to prioritize]"
allowed-tools: Read
---

# Impact Matrix

## Complexity × Impact Prioritization Matrix

### Scoring Dimensions

Score each finding on two dimensions (1–3 scale):

**Impact** — user or business effect if fixed

| Score | Meaning                                               |
|-------|-------------------------------------------------------|
| 3     | Directly visible to users or causes SLO breach        |
| 2     | Measurable improvement but not directly user-facing   |
| 1     | Minor improvement; internal or technical benefit only |

**Complexity** — effort required to implement the fix

| Score | Meaning                                                                 |
|-------|-------------------------------------------------------------------------|
| 1     | <1 day: config change, add index, fix cache header                      |
| 2     | 1–5 days: refactor one component, add cache layer, pool objects         |
| 3     | >1 sprint: architectural change, data model migration, platform upgrade |

**Priority score = Impact ÷ Complexity** (higher = act sooner)

### Quadrant Map

```
         HIGH IMPACT (3)
              │
  Quick Wins  │  Strategic Projects
  Impact 3    │  Impact 3
  Complexity 1│  Complexity 3
  ────────────┼────────────────────
  LOW         │                HIGH
  COMPLEXITY  │           COMPLEXITY
  ────────────┼────────────────────
  Low-Hanging │  Avoid / Defer
  Fruit       │  Impact 1
  Impact 1-2  │  Complexity 3
  Complexity 1│
              │
         LOW IMPACT (1)
```

- **Quick Wins** → Ship immediately; highest ROI
- **Strategic Projects** → Schedule in roadmap; break into milestones
- **Low-Hanging Fruit** → Batch in a cleanup sprint
- **Avoid / Defer** → Do not prioritize; revisit if scale or impact changes

### Scoring Template

When given a list of findings, produce this prioritized table:

```
| # | Finding                        | Impact | Complexity | Score | Quadrant          |
|---|--------------------------------|--------|------------|-------|-------------------|
| 1 | Add index on orders.user_id    |   3    |     1      |  3.0  | Quick Win         |
| 2 | Migrate to async I/O           |   3    |     3      |  1.0  | Strategic Project |
| 3 | Enable gzip on API responses   |   2    |     1      |  2.0  | Low-Hanging Fruit |
| 4 | Rewrite ORM to raw SQL         |   1    |     3      |  0.3  | Avoid / Defer     |
```

Sort descending by Score. Explicitly call out all Quick Wins as immediate actions.

### Adjust presentation based on the target audience:

- **Developer**: Include file/function reference per finding; note PR size estimate
- **Perf Engineer**: Add "measurement required" column; flag items needing a benchmark before scoring
- **DevOps**: Flag items requiring infrastructure changes; note deployment risk per item
- **Leadership**: Replace complexity score with "Estimated effort in weeks"; replace impact score with a user impact statement

### Common Scoring Pitfalls

- **Don't let complexity dominate**: A 3-day fix with p99 latency impact beats a 1-hour fix with cosmetic gain
- **Re-score after dependencies**: If Fix A removes the cause of Fix B, score them as a unit
- **Decay findings over time**: Re-score as scale changes — an issue that was Impact 3 at 10k users may be Impact 2 at 1M
- **Validate with measurement**: Scores are estimates; build a benchmark before committing to large-complexity items
- **Avoid premature optimization**: Score 1/1 findings are fine to batch, but never let them crowd out higher-priority work

### Tiebreaker Rules

When two findings have the same score:
1. Prefer the one with lower **risk** (fewer systems touched, easier rollback)
2. Prefer the one that **unblocks** other fixes
3. Prefer the one with **existing test coverage** (safer to change)

After presenting the matrix, output: "Run `/perfmind:report [role]` to generate a role-specific report using these findings."

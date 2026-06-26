# Role-Specific Report Templates

Full markdown templates for each target audience. Use the template matching the detected role from Step 2.

---

## Developer Report

**Focus**: Actionable code-level fixes
**Tone**: Technical, specific, patch-sized

```markdown
## Performance Report — Developer

### Critical (fix this sprint)
- **[Issue]**: [Root cause in one sentence]
  Fix: [Specific code change, file:line reference if available]
  Evidence: [Metric or profiler callsite]

### High Priority
- **[Issue]**: [Root cause]
  Fix: [Approach]
  Evidence: [Supporting data]

### To Watch
- **[Issue]**: [Why it's worth monitoring but not acting on yet]

### Implementation Checklist
1. [ ] [Concrete step with tooling hint — e.g. "Add index on orders.user_id — run EXPLAIN ANALYZE first to confirm seq scan"]
2. [ ] [Next step]
3. [ ] [Benchmark or measure after each change to confirm improvement]
```

**Audience notes:**
- Include file path and function name per finding when available
- Estimate PR size (small/medium/large) to help with sprint planning
- Group "Critical" items by the sprint they should land in

---

## Perf Engineer Report

**Focus**: Methodology, data quality, regression prevention
**Tone**: Analytical, metric-first

```markdown
## Performance Report — Perf Engineer

### Baseline
| Metric             | Current | Target       | Delta   |
|--------------------|---------|--------------|---------|
| [e.g. p99 latency] | [value] | [SLO target] | [+/- %] |

### Root Cause Analysis
[Domain] → [evidence chain] → [confirmed hypothesis]

Example:
Database → N+1 queries on order_items (8–35 per request) → p99 variance proportional to order size

### Data Gaps
- Missing metrics: [e.g. "No heap allocation trace — add async_profiler before next investigation"]
- Recommended profiling additions: [e.g. "Enable slow query log threshold at 100ms"]

### Regression Prevention
- Perf budget thresholds: [e.g. "p99 API response <500ms; flag if exceeded in CI"]
- CI gate recommendations: [e.g. "Add k6 load test on critical path with threshold assertions"]
- Suggested benchmark: [command or tool to lock in the improvement]
```

**Audience notes:**
- Always cite the measurement method alongside the metric
- Flag any finding that lacks a before/after benchmark as "unverified"
- Include a "confidence" note (High/Medium/Low) per root cause

---

## DevOps Report

**Focus**: Infrastructure, scaling, configuration, SLOs
**Tone**: Operational, config-focused

```markdown
## Performance Report — DevOps

### SLO Status
| SLO            | Target | Actual  | Status     |
|----------------|--------|---------|------------|
| [e.g. API p99] | <500ms | 2,800ms | ❌ Breached |

### Infrastructure Actions
- **[Action]**: [Config change or scaling recommendation]
  - Risk: [Low / Medium / High]
  - Rollback: [How to revert if needed]

### Monitoring Gaps
- Missing alerts: [e.g. "No alert on p99 > 1s for /api/orders"]
- Recommended dashboards: [e.g. "Add slow-query dashboard; set threshold at 200ms"]

### Runbook Entry
**Symptom**: [Observable symptom in production — what an on-call engineer sees]
**Diagnosis**: [Steps to confirm root cause — commands, dashboards to check]
**Mitigation**: [Immediate action to reduce impact without a code deploy]
**Resolution**: [Permanent fix with owner and estimated timeline]
```

**Audience notes:**
- Flag items that require a deploy vs. config-only changes
- Note deployment risk (needs migration, requires downtime, zero-downtime capable)
- Prefer concrete kubectl/terraform/config snippets over abstract descriptions

---

## Leadership Report

**Focus**: Business impact, effort vs benefit, roadmap
**Tone**: Non-technical, outcome-focused (keep under 400 words total)

```markdown
## Performance Report — Executive Summary

### Business Impact
[One paragraph: translate technical findings into user or revenue terms.
Examples: "Users abandoning checkout due to 2.8s load times on order confirmation",
"SLA breach risk if p99 exceeds 3s — currently at 2.8s under normal load"]

### Prioritized Initiatives
| Initiative            | User Impact                           | Effort        | Timeline           |
|-----------------------|---------------------------------------|---------------|--------------------|
| [e.g. Database index] | [e.g. Cuts checkout time by ~60%]     | [e.g. 1 day]  | [e.g. This sprint] |
| [e.g. Query batching] | [e.g. Eliminates tail-latency spikes] | [e.g. 3 days] | [e.g. Next sprint] |

### Risk If Not Addressed
[What happens if no action is taken — user churn estimate, SLA penalty, cost increase,
or engineering debt that blocks future features]

### Recommended Next Step
[Single concrete action with a named owner and a target date.
Example: "Engineering team to deploy database index this week — estimated 30-minute deploy,
zero downtime, expected to resolve p99 latency breach immediately."]
```

**Audience notes:**
- Avoid all technical jargon (no "p99", "GC pause", "N+1" — translate to plain English)
- Keep the entire report under 400 words
- Lead with user impact, not technical root cause
- One recommended next step only — leadership should leave with a single clear action

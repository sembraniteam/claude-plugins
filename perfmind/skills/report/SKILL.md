---
name: report
description: This skill generates a role-tailored performance report when the user invokes /perfmind:report, says "generate a performance report", "write a summary for my manager", "create a performance write-up for leadership", "show me recommendations as a DevOps engineer", "give me actionable fixes as a developer", "write an analyst-level summary", "I need to share these findings with the team", or asks to document performance findings for a specific audience. Reads investigation findings from the conversation and auto-detects the target audience.
argument-hint: "[role]  e.g. developer | devops | leadership | perf-engineer"
allowed-tools: Read
---

## Role-Tailored Performance Report Generation

Generate a structured performance report adapted to the target audience.

### Step 1: Gather Findings

Read the performance findings from the current conversation context. If no `/perfmind:investigate` session has been run, prompt the user to share key findings first or invoke `/perfmind:investigate` before proceeding.

### Step 2: Detect Target Role

If the user passes a role argument, use it directly. Otherwise, infer from conversation context:

| Signal words                                                              | Role              |
|---------------------------------------------------------------------------|-------------------|
| "deploy", "infra", "Kubernetes", "scaling", "SRE", "runbook", "alert"     | **DevOps**        |
| "code fix", "PR", "refactor", "function", "file", "commit"                | **Developer**     |
| "flame graph", "profiler", "benchmark", "regression", "p99", "percentile" | **Perf Engineer** |
| "SLA", "user experience", "cost", "roadmap", "business impact", "budget"  | **Leadership**    |

If unclear, default to **Developer**.

### Step 3: Generate Role-Specific Report

Use the following structure for the detected role:

---

#### Developer Report

**Focus**: Actionable code-level fixes
**Tone**: Technical, specific, patch-sized

```
## Performance Report — Developer

### Critical (fix this sprint)
- **[Issue]**: [Root cause]
  Fix: [Specific code change or approach]
  Evidence: [metric or profiler callsite]

### High Priority
- ...

### To Watch
- ...

### Implementation Checklist
1. [ ] [Step with tooling hint, e.g. "Add index on users.email — run EXPLAIN ANALYZE first"]
2. [ ] ...
```

---

#### Perf Engineer Report

**Focus**: Methodology, data quality, regression prevention
**Tone**: Analytical, metric-first

```
## Performance Report — Perf Engineer

### Baseline
| Metric | Current | Target | Delta |
|--------|---------|--------|-------|

### Root Cause Analysis
[Domain] → [evidence chain] → [confirmed hypothesis]

### Data Gaps
- Missing metrics: ...
- Recommended profiling additions: ...

### Regression Prevention
- Suggested perf budget thresholds
- CI gate recommendations
```

---

#### DevOps Report

**Focus**: Infrastructure, scaling, configuration, SLOs
**Tone**: Operational, config-focused

```
## Performance Report — DevOps

### SLO Status
| SLO | Target | Actual | Status |
|-----|--------|--------|--------|

### Infrastructure Actions
- **[Action]**: [Config change or scaling recommendation]

### Monitoring Gaps
- Missing alerts: ...
- Recommended dashboards: ...

### Runbook Entry
**Symptom**: [observable symptom]
**Diagnosis**: [how to confirm]
**Mitigation**: [immediate fix]
**Resolution**: [permanent fix]
```

---

#### Leadership Report

**Focus**: Business impact, effort vs benefit, roadmap
**Tone**: Non-technical, outcome-focused (keep under 400 words)

```
## Performance Report — Executive Summary

### Business Impact
[One paragraph: effect on users, conversion, cost, or SLA compliance]

### Prioritized Initiatives
| Initiative | User Impact | Effort | Timeline |
|------------|-------------|--------|----------|

### Risk If Not Addressed
[What happens if we do nothing — user churn, SLA breach, cost increase]

### Recommended Next Step
[Single concrete action with owner and timeline]
```

---

After generating the report, output: "Share more evidence via `/perfmind:investigate` to refine these recommendations."

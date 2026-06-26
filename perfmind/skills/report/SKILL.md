---
name: report
description: This skill should be used when the user invokes /perfmind:report, says "generate a performance report", "write a summary for my manager", "create a performance write-up for leadership", "show me recommendations as a DevOps engineer", "give me actionable fixes as a developer", "write an analyst-level summary", "I need to share these findings with the team", "write a report for my team", "document these perf findings", "share findings with stakeholders", or asks to document performance findings for a specific audience. Reads investigation findings from the conversation and auto-detects the target audience.
argument-hint: "[role]  e.g. developer | devops | leadership | perf-engineer"
allowed-tools: Read
---

# Performance Report

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

Generate the report using the full template for the detected role from **`references/role-templates.md`**.

Key output principles per role:

| Role              | Focus                                                              | Tone                           | Length     |
|-------------------|--------------------------------------------------------------------|--------------------------------|------------|
| **Developer**     | Code-level fixes, file:line references, patch-sized items          | Technical, specific            | No limit   |
| **Perf Engineer** | Baseline metrics, evidence chain, data gaps, regression prevention | Analytical, metric-first       | No limit   |
| **DevOps**        | SLO status, infrastructure actions, runbook entry                  | Operational, config-focused    | No limit   |
| **Leadership**    | Business impact, effort vs. timeline, risk if not addressed        | Non-technical, outcome-focused | <400 words |

After generating the report, output: "Share more evidence via `/perfmind:investigate` to refine these recommendations."

## Additional Resources

- **`references/role-templates.md`** — Full markdown templates for all four roles with section-by-section guidance and audience notes

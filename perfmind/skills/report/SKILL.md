---
name: report
description: This skill should be used when the user directly and interactively asks to generate a report in the current conversation, says "generate a performance report", "create a performance write-up for leadership", "show me recommendations as a DevOps engineer", "give me actionable fixes as a developer", "write an analyst-level summary", "I need to share these findings with the team", or asks to document performance findings for a specific audience. Reads investigation findings from the conversation and auto-detects the target audience. Do NOT use for explicit agent delegation or autonomous background generation — invoke the `report-generator` agent for that instead.
argument-hint: "[role]  e.g. developer | devops | leadership | perf-engineer"
allowed-tools: Read
---

# Performance Report

## Role-Tailored Performance Report Generation

Generate a structured performance report adapted to the target audience.

### Step 1: Gather Findings

Read the performance findings from the current conversation context. If no `/perfmind:investigate` session has been run, prompt the user to share key findings first or invoke `/perfmind:investigate` before proceeding.

### Step 2: Detect Target Role

If the user passes a role argument, use it directly. Otherwise, detect the role using the signal-word table in **`references/role-templates.md`** — that file is the single source of truth for role detection; do not keep a separate copy of the table here.

### Step 3: Generate Role-Specific Report

Generate the report using the full template for the detected role from **`references/role-templates.md`**, including its stated focus, tone, and length constraints per role — that file is the single source of truth for these facts; do not restate or summarize them here.

Follow the Anti-Fabrication Rule in `references/role-templates.md` — every number must trace back to a finding actually stated in the conversation, with extra force for the Leadership template's numeric examples (illustrative placeholders only, never to be copied as-is).

After generating the report, output: "Share more evidence via `/perfmind:investigate` to refine these recommendations."

## Additional Resources

- **`references/role-templates.md`** — Single source of truth for role-detection signals and full markdown templates for all four roles, with section-by-section guidance and audience notes
- **`examples/developer-report.md`** — Complete worked example: findings from an investigation session rendered as a Developer report

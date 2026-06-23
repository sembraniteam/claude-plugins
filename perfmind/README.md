# perfmind

Performance investigation assistant for web, mobile, desktop, and API applications.

## Overview

perfmind guides structured performance investigations — from raw evidence (screenshots, profiler output, GC logs, metrics) to prioritized, role-tailored recommendations. It supports all application types and surfaces actionable findings for developers, perf engineers, DevOps teams, and leadership.

## Features

- Multi-domain analysis: response time, CPU, memory, GC, database, networking, battery/mobile
- Cross-platform: web (Core Web Vitals), Android, iOS, Flutter, desktop, API/backend
- Complexity × Impact prioritization matrix
- Role-tailored reports (developer / perf engineer / DevOps / leadership)
- Hypothesis-driven deep-dive agent for complex root-cause analysis

## Skills (Slash Commands)

### `/perfmind:investigate [app-type] [--focus <domain>]`

Starts a structured performance investigation session. Accepts profiler output, GC logs, screenshots, and metrics.

```
/perfmind:investigate
/perfmind:investigate mobile --focus memory
/perfmind:investigate api
/perfmind:investigate web
```

### `/perfmind:report [role]`

Generates a role-tailored performance report from findings in the current conversation.

```
/perfmind:report
/perfmind:report developer
/perfmind:report leadership
/perfmind:report devops
/perfmind:report perf-engineer
```

## Knowledge Skills (auto-activated)

| Skill                 | Activates when...                                                        |
|-----------------------|--------------------------------------------------------------------------|
| `profiler-analysis`   | User shares flame graphs, GC logs, allocation traces, or heap dumps      |
| `bottleneck-patterns` | User describes slow response times, high CPU, memory leaks, jank, or ANR |
| `impact-matrix`       | User asks to prioritize or rank findings                                 |

## Agents

### `performance-analyst`

Autonomous deep-dive for a single performance domain. Investigates hypotheses, cites evidence, and returns a structured findings report.

Triggers: "deep dive into memory", "analyze this profiler output", "investigate the database bottleneck"

### `report-generator`

Generates polished, role-tailored performance reports from investigation findings. Auto-detects target audience from conversation context.

Triggers: "write a performance report", "create an executive summary", "generate a DevOps runbook entry"

## Recommended Workflow

```
1. /perfmind:investigate   ← gather evidence, get findings
2. /perfmind:report        ← generate role-tailored report
```

For complex issues, substitute step 1 with the `performance-analyst` agent for hypothesis-driven analysis before generating the report.

## Installation

```bash
cc --plugin-dir /path/to/perfmind
```

Or copy the directory into `.claude-plugin/` in your project root.

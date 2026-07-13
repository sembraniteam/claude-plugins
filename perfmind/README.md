# perfmind

Performance investigation assistant for web, mobile, desktop, and API applications.

## Overview

perfmind guides structured performance investigations — from raw evidence (screenshots, profiler output, GC logs, metrics) to prioritized, role-tailored recommendations. It supports all application types and surfaces actionable findings for developers, perf engineers, DevOps teams, and leadership.

## Features

- Multi-domain analysis: response time, CPU, memory, GC, database, networking, battery/mobile
- Cross-platform: web (Core Web Vitals), Android, iOS, Flutter, desktop, API/backend
- Deterministic top-N extraction for `.cpuprofile`, `go tool pprof -top`, and PostgreSQL `EXPLAIN ANALYZE` JSON (`scripts/parse-profiler.py`) — the script computes, the skills interpret
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

| Skill                 | Activates when...                                                                                                                     |
|-----------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| `profiler-analysis`   | User shares flame graphs, GC logs, allocation traces, heap dumps, `.cpuprofile` files, `pprof -top` output, or `EXPLAIN ANALYZE` JSON |
| `bottleneck-patterns` | User describes slow response times, high CPU, memory leaks, jank, or ANR                                                              |
| `impact-matrix`       | User asks to prioritize or rank findings                                                                                              |

## Agents

### `performance-analyst`

Autonomous deep-dive for a single, already-identified performance domain. Investigates hypotheses, cites evidence, and returns a structured findings report.

Triggers: "deep dive into memory", "analyze this profiler output for me", "investigate the database bottleneck". Use `/perfmind:investigate` instead for a broad, multi-domain triage session when the domain isn't yet known.

### `report-generator`

Generates polished, role-tailored performance reports from investigation findings. Auto-detects target audience from conversation context. Scoped to explicit agent delegation or autonomous/background report generation outside the interactive conversation flow.

Triggers: explicitly naming the agent, or requesting report generation as a standalone/delegated task. Use `/perfmind:report` instead for a direct, interactive request to generate a report in the current conversation.

## Recommended Workflow

```
1. /perfmind:investigate   ← gather evidence, get findings
2. /perfmind:report        ← generate role-tailored report
```

For complex issues, substitute step 1 with the `performance-analyst` agent for hypothesis-driven analysis before generating the report.

## Installation

### Option 1: Install from this repo (marketplace)

```bash
# Add this repo as a marketplace source
/plugin marketplace add sembraniteam/claude-plugins

# Install the plugin
/plugin install perfmind@sembraniteam-claude-plugins
```

### Option 2: Local install (development)

```bash
# Clone the repo
git clone https://github.com/sembraniteam/claude-plugins.git

# Add the local repo as a marketplace
/plugin marketplace add /path/to/claude-plugins

# Install
/plugin install perfmind@sembraniteam-claude-plugins
```

---
name: investigate
description: This skill should be used when the user invokes /perfmind:investigate, says "investigate this performance issue", "help me debug slow response times", "why is my app slow", "investigate memory leak", "investigate CPU usage", "my latency jumped", "what's causing high memory usage", "profile my app", "where should I start investigating", "I don't know what's causing this slowness", or pastes profiler data, GC logs, or metric screenshots for broad, multi-domain triage when the root cause isn't yet known. Accepts evidence from multiple sources and produces structured findings with domain-specific analysis. Do NOT use for a hypothesis-driven deep dive into one already-identified domain (CPU, memory, GC, database, network) — invoke the `performance-analyst` agent for that instead.
argument-hint: "[app-type] [--focus <domain>]  e.g. mobile --focus memory | web | api | desktop"
allowed-tools: Read, Bash
---

# Performance Investigation

## Performance Investigation Workflow

Guide the user through a structured evidence-based performance investigation.

### Step 1: Gather Evidence

Request one or more of the following from the user:
- Screenshots or images of metrics dashboards
- Response time numbers or latency percentiles (p50, p95, p99)
- Profiler output (CPU flame graphs, allocation traces, call trees)
- GC logs (pause times, collection frequency, heap size)
- Code snippets from suspected hot paths
- Error logs or timeout traces
- Network HAR files or trace exports

If arguments are provided, interpret them to narrow scope:
- App type (`web`, `mobile`, `api`, `desktop`) — adjusts which domains to prioritize
- Focus domain (`--focus memory|cpu|network|database|gc`) — restricts analysis to one area

Use `Read` to read log or profiler files from the filesystem when the user provides a file path. Reserve `Bash` for commands that actually require a shell — e.g. `grep -c "Full GC" app.log` to count occurrences before reading, or `tail -n 500 huge.log` to trim a multi-GB log to a readable slice.

### Step 2: Triage by App Type

Classify the app type from context or the user's argument:

| App Type        | Primary concerns                                                              |
|-----------------|-------------------------------------------------------------------------------|
| **Web**         | FCP, LCP, TTI, bundle size, render blocking, API latency                      |
| **Mobile**      | ANR, battery drain, memory pressure, frame drops (jank), startup time         |
| **Desktop**     | CPU affinity, memory leaks, I/O blocking, UI thread stalls                    |
| **API/Backend** | p99 latency, throughput, DB query time, connection pool exhaustion, GC pauses |

### Step 3: Multi-Domain Analysis

For each piece of evidence, apply the relevant knowledge:
- For profiler output or GC logs: apply the interpretation rules in the `profiler-analysis` skill
- For response time or resource metrics: apply the pattern recognition in the `bottleneck-patterns` skill
- For prioritization of findings: apply the `impact-matrix` skill

Analyze across all applicable domains:

**Response Time**
- Break down latency: frontend render time, network RTT, server processing, DB query time
- Flag SLO violations (>200ms API response, >3s page load, etc.)
- Identify tail latency (p99 >> p50 signals an intermittent issue)

**CPU**
- Identify hot functions consuming >5% CPU in profiler output
- Flag busy-wait loops and unnecessary polling
- Note thread contention and lock hotspots

**Memory**
- Identify allocation hot paths and short-lived large objects
- Flag objects surviving unexpected GC generations
- Note monotonically growing heap (memory leak signal)

**GC**
- Flag GC pause times >50ms (web/mobile) or >200ms (server)
- Identify frequent full GC cycles
- Note premature object promotion

**Database**
- Flag N+1 query patterns
- Identify missing indexes from slow query logs
- Note long-running transactions blocking other queries

**Networking**
- Flag non-batched API calls and large uncompressed payloads
- Note missing HTTP/2, keep-alive, or compression
- Identify render-blocking resource fetches (web)

**Mobile (Battery & Jank)**
- Flag excessive wakelock usage and background work preventing deep sleep
- Identify excessive sensor/location polling
- Note UI thread work causing frame drops (>16ms per frame at 60fps)

### Step 4: Output

Produce the following after analysis:

1. **App type & scope** — one line confirming what was analyzed
2. **Summary** — one paragraph describing the primary bottleneck and its likely root cause
3. **Findings list** — each finding with: description, evidence cited, domain tag
4. **Next-step prompt** — output: "Run `/perfmind:report` to get role-specific recommendations, or ask the `performance-analyst` agent for a deep dive into one domain."

## Additional Resources

### Related Skills

Consult these skills during Step 3 analysis:
- **`bottleneck-patterns`** — Domain-specific pattern recognition and diagnostic guidance
- **`profiler-analysis`** — Expert interpretation of profiler output, flame graphs, and GC logs
- **`impact-matrix`** — Prioritization when multiple findings are present

### Example Output

- **`examples/api-latency-investigation.md`** — Complete Step 4 output for a Node.js backend latency investigation

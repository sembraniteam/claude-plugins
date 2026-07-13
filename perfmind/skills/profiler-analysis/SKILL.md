---
name: profiler-analysis
description: This skill should be used when the user shares profiler output, flame graphs, CPU traces, allocation traces, heap dumps, GC logs, call trees, asks "what does this GC log mean", "help me read this flame graph", "what's causing heap growth", "how do I interpret this allocation trace", "help me read this perf trace", "interpret this pprof output", "what does this OOM error mean", "analyze this heap dump", "parse this cpuprofile", "what's slow in this query plan", or pastes runtime diagnostic data for interpretation. Provides expert analysis of profiler artifacts across JVM/Android, Node.js/V8, Python, Go, Dart/Flutter, Swift/iOS, and browser DevTools, plus deterministic top-N extraction for Chrome/Node .cpuprofile, `go tool pprof -top`, and PostgreSQL EXPLAIN ANALYZE JSON.
allowed-tools: Read, Bash
---

# Profiler Analysis

## Deterministic Extraction (run this first when the format matches)

For the three formats a script can parse exactly, run `scripts/parse-profiler.py` before attempting any manual
interpretation. Computing percentages, aggregating recursive call sites, and walking a query plan tree by eye
is exactly the kind of arithmetic a script gets right every time and a model can get subtly wrong once — the
script computes, this skill interprets:

- Chrome DevTools / Node.js `--cpu-prof` output (`.cpuprofile` files — JSON with `nodes` + `samples`)
- `go tool pprof -top <profile>` text output (piped or saved to a file)
- PostgreSQL `EXPLAIN (ANALYZE, FORMAT JSON) <query>` output

```bash
python3 "$CLAUDE_PLUGIN_ROOT/scripts/parse-profiler.py" <path-or-'-'-for-stdin> [--format cpuprofile|pprof-top|pg-explain] [--top N]
```

Format auto-detects from content when `--format` is omitted. `--top` defaults to 15. The script exits non-zero
with a plain-language error on unreadable/malformed input or unrecognized format — when it fails, fall back to
the manual interpretation guidance below for whatever runtime the artifact came from, rather than guessing at
numbers the script refused to compute.

Every format returns the same JSON shape on stdout, so downstream reasoning is identical regardless of which
profiler produced the input:

```json
{
  "format": "cpuprofile | pprof-top | pg-explain",
  "summary": { "...format-specific totals, e.g. total_samples, duration_ms, execution_time_ms..." },
  "top": [
    {
      "rank": 1,
      "name": "function or plan-node name",
      "location": "file:line, relation/index name, or null",
      "self_pct": 34.39,
      "self_time_ms": 980.0,
      "total_pct": 34.39,
      "total_time_ms": 980.0,
      "extra": { "...format-specific fields, see below..." }
    }
  ]
}
```

- **`self_pct`/`self_time_ms`** — exclusive time/share for this function or plan node alone, not its callees.
  This is the primary sort key and the number to lead with when identifying "the" hotspot.
- **`total_pct`/`total_time_ms`** — inclusive of children (cumulative time for a function, or a plan node's
  time including its subtree). A node can rank low on `self_pct` but high on `total_pct` if it's a thin
  orchestration layer over expensive children — call this out explicitly rather than only reporting the
  self-time leaderboard, since both numbers matter for different fix strategies (optimize the node itself vs.
  optimize/parallelize what it calls).
- **`self_time_ms`/`total_time_ms` can be `null`** — this happens for `pprof-top` when the profile type isn't
  time-based (e.g. a heap/allocation profile using bytes or object counts instead of seconds). `self_pct`/
  `total_pct` are always populated regardless of unit; fall back to `extra.flat_raw`/`extra.cum_raw` (the
  original unit string) when the absolute numbers are null.
- **`extra`** carries format-specific detail worth surfacing in a finding, notably `pg-explain`'s
  `actual_vs_estimated_rows_ratio` — the planner's estimated rows vs. what actually came back. A ratio far from
  `1.0` (e.g. 40x under-estimated) is itself a root-cause finding: a bad plan usually traces back to a bad
  estimate, and `ANALYZE`-ing the underlying table's statistics is often the actual fix, not the query itself.

After running the script, apply the domain-specific interpretation guidance in the sections below to the
returned `top` list exactly as if reading it off a flame graph or `pprof` session by eye — the script only
replaces the arithmetic, not the judgment about what the numbers mean.

## Profiler & GC Log Analysis

### Reading Flame Graphs

Flame graphs visualize CPU time distribution across the call stack:
- **Width** = percentage of sampled CPU time (wider = more expensive)
- **Height** = call depth (leaf functions at top, entry points at bottom)
- **Hotspot identification**: Wide plateaus near the top are the actual CPU consumers
- **Tall thin towers**: Often I/O waits or lock contention — check if sampling is time-based or CPU-based

Key questions when reading a flame graph:
1. What is the widest function near the top? → Primary bottleneck
2. Is the hotspot in user code or in a framework/library?
3. Are unexpected platform functions present (GC, serialization, string copy)?

### JVM / Android GC Logs

```
GC pause signal → diagnosis:
- Minor GC >50ms     → Eden space too small; increase -Xmn or G1 region size
- Full GC >200ms     → Heap too small or memory leak; increase -Xmx or profile allocations
- G1GC region stalls → Mixed GC overload; tune -XX:G1MixedGCCountTarget
- Humongous objects  → Single object >50% region size; pool or break apart
- Frequent GC cycles → Allocation rate too high; reduce short-lived object creation
```

Diagnostic JVM flags to request if not present:
- JDK 11+: `-Xlog:gc*:file=gc.log:time,uptime:filecount=5,filesize=20m`
- JDK 8: `-XX:+PrintGCDetails -XX:+PrintGCDateStamps -XX:+PrintGCApplicationStoppedTime`

Android-specific: `GC_FOR_ALLOC` and `GC_CONCURRENT` are Dalvik-era logcat GC messages (pre-Android 5.0); the former indicates an allocation failure signaling memory pressure. ART (Android 5.0+, the runtime on all modern devices) doesn't emit GC events to logcat this way — use `adb shell dumpsys meminfo <package>`, Android Studio's Memory Profiler, or `am dumpheap` for heap/GC diagnostics instead.

### Node.js / V8

- Profile with `node --prof` + `node --prof-process isolate-*.log`, or Chrome DevTools > Performance tab
- `node --cpu-prof` writes a `.cpuprofile` file directly — parse it with `scripts/parse-profiler.py --format cpuprofile` instead of opening DevTools when only the ranked hotspot list is needed
- V8 GC types: **Scavenge** (minor, fast, <10ms) and **Mark-Compact** (major, stop-the-world)
- Use `--expose-gc` to call `global.gc()` explicitly in heap profiling tests
- Heap snapshot: `v8.writeHeapSnapshot()` or Chrome DevTools > Memory > Heap Snapshot

Common culprits: retained closures holding large objects, event listener leaks (check `process.listenerCount`), large `Buffer` copies.

### Python

- CPU: `cProfile` (built-in) or `py-spy` (sampling, attaches to running process without restart)
- Memory: `tracemalloc` (built-in) or `memray` (detailed allocation traces with flamegraph output)
- Hot path indicator: highest cumulative time in `cProfile`'s `tottime` column
- GIL contention: high CPU with flat parallelism → consider `asyncio`, `multiprocessing`, or C extensions

### Go

- `pprof` supports CPU, heap, goroutine, mutex, and block profiles
- View interactively: `go tool pprof -http=:8080 cpu.prof`, or run `go tool pprof -top cpu.prof` and pipe the text output straight into `scripts/parse-profiler.py --format pprof-top` for a structured ranked list instead of reading the columns by eye
- Goroutine leak check: growing count at `/debug/pprof/goroutine?debug=1`
- GC overhead: `GODEBUG=gctrace=1` → target <1% GC CPU time
- Allocation escape analysis: `go build -gcflags='-m'` to see what escapes to heap

### Flutter / Dart

- DevTools Timeline panel: flag frames >16ms (60fps) or >8ms (120fps)
- Custom tracing: `dart:developer` `Timeline.startSync` / `finishSync`
- Memory: DevTools > Memory tab; watch for ratcheting heap (leak signal)
- Shader compilation jank: first-time frame stutter — use `--bundle-sksl-path` and warm-up shaders at startup
- Isolate overhead: large objects crossing isolate boundaries via `SendPort` copy — minimize message size

### Swift / iOS

- CPU: Instruments Time Profiler — look for wide stacks in the main thread track
- Memory: Instruments Allocations instrument for growth over time; Xcode Memory Graph Debugger for retain-cycle detection (purple exclamation icons)
- Retain cycles: check `weak`/`unowned` capture in closures, especially delegate and completion-handler patterns
- Main thread stalls: Instruments Time Profiler + "Main Thread Only" filter; flag any I/O or heavy computation on the main run loop (it should be moved off)
- `leaks` command-line tool or Instruments Leaks template for a quick standalone leak scan

### Browser DevTools (Web)

- **Performance panel**: Record → Main thread flame chart → look for Long Tasks (red flag, >50ms)
- **Long Tasks >50ms** block the main thread and increase INP
- **Layout thrashing**: alternating DOM reads and writes in a loop → batch reads before writes
- **Memory panel**: Heap snapshot comparison (before/after action) to find leaked objects
- **Network panel**: Waterfall view for render-blocking requests; look for parser-blocking `<script>` tags

### PostgreSQL Query Plans (EXPLAIN ANALYZE)

Request `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) <query>` — `BUFFERS` adds shared/read block counts the script
below does not currently parse, so read `Shared Hit Blocks`/`Shared Read Blocks` directly from the raw JSON
when disk I/O rather than CPU time is suspected. Run the `ANALYZE` variant, never plain `EXPLAIN` — estimated
costs without actual execution stats cannot show where time was really spent.

Parse the output with `scripts/parse-profiler.py --format pg-explain` (see "Deterministic Extraction" above),
then read the ranked `top` list for these patterns:

1. **Highest `self_time_ms` node** → the actual bottleneck operation, not necessarily the top-level node (a
   `Hash Join` can show high `total_time_ms` while a `Seq Scan` two levels down owns most of the `self_time_ms`)
2. **`Seq Scan` ranking high on `self_time_ms` against a large table** → missing index candidate; check
   `extra.filter` for the column to index (cross-reference `bottleneck-patterns`' Database section for the fix)
3. **`extra.actual_vs_estimated_rows_ratio` far from `1.0`** → stale table statistics, not a query problem;
   the fix is usually `ANALYZE <table>`, not rewriting the query — a plan built on a bad row estimate can pick
   the wrong join strategy even when every individual operation is implemented efficiently
4. **`extra.rows_removed_by_filter` large relative to `extra.actual_rows`** → the filter runs after a scan
   that already did most of the expensive work; an index on the filtered column lets Postgres prune before
   scanning instead of after
5. **High `extra.actual_loops` on a node with moderate per-loop `self_time_ms`** → the loop count is the
   multiplier, not any single iteration; check the outer node's row estimate, since `Actual Total Time` in the
   raw plan is a per-loop average that the script already multiplies out into `self_time_ms`/`total_time_ms`

### Cross-Runtime: Interpreting Allocation Traces

When given allocation traces from any runtime, identify:
1. **Top allocator by size** → likely memory pressure source
2. **Short-lived large objects** → GC churn candidate; consider object pooling
3. **String/Array allocations inside hot loops** → pre-allocate buffers or reuse
4. **Retained paths** (shortest path from GC root to leaked object) → root cause of heap growth

Request a heap diff (snapshot before vs. after a user action) when a leak is suspected but not confirmed.

## Additional Resources

- **`scripts/parse-profiler.py`** — Deterministic top-N parser for `.cpuprofile`, `go tool pprof -top`, and PostgreSQL `EXPLAIN ANALYZE` JSON; see "Deterministic Extraction" above
- **`bottleneck-patterns`** — Apply after identifying profiler hotspots to match patterns and find fixes
- **`investigate`** — Use when profiler data is one of several evidence types in a broader investigation

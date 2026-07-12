---
name: profiler-analysis
description: This skill should be used when the user shares profiler output, flame graphs, CPU traces, allocation traces, heap dumps, GC logs, call trees, asks "what does this GC log mean", "help me read this flame graph", "what's causing heap growth", "how do I interpret this allocation trace", "help me read this perf trace", "interpret this pprof output", "what does this OOM error mean", "analyze this heap dump", or pastes runtime diagnostic data for interpretation. Provides expert analysis of profiler artifacts across JVM/Android, Node.js/V8, Python, Go, Dart/Flutter, Swift/iOS, and browser DevTools.
allowed-tools: Read
---

# Profiler Analysis

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
- View interactively: `go tool pprof -http=:8080 cpu.prof`
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

### Cross-Runtime: Interpreting Allocation Traces

When given allocation traces from any runtime, identify:
1. **Top allocator by size** → likely memory pressure source
2. **Short-lived large objects** → GC churn candidate; consider object pooling
3. **String/Array allocations inside hot loops** → pre-allocate buffers or reuse
4. **Retained paths** (shortest path from GC root to leaked object) → root cause of heap growth

Request a heap diff (snapshot before vs. after a user action) when a leak is suspected but not confirmed.

## Additional Resources

- **`bottleneck-patterns`** — Apply after identifying profiler hotspots to match patterns and find fixes
- **`investigate`** — Use when profiler data is one of several evidence types in a broader investigation

---
name: bottleneck-patterns
description: This skill should be used when the user describes slow response times, high CPU usage, memory pressure or leaks, database slowness, network issues, frame drops, ANR errors, battery drain, app jank, a performance regression after deploy, or app lagging under load; or asks "my database queries are taking forever", "why does my Flutter app stutter", "what's causing my API to slow down under load". Provides domain-specific bottleneck pattern recognition and diagnostic guidance for web, mobile (Android/iOS/Flutter), desktop, and API/backend applications.
allowed-tools: Read
---

# Bottleneck Patterns

## Performance Bottleneck Patterns

Identify which domain matches the symptom, then apply the corresponding pattern. For the full symptom → pattern → fix lookup tables, see `references/bottleneck-lookup.md`.

### Domain Quick Reference

**Response Time**: Tail latency (p99 >> p50), throughput ceiling, cold-path slowness, periodic spikes

**Web**: Render-blocking resources, large JS bundles, layout thrashing, missing CDN, high INP

**API/Backend**: N+1 queries, missing indexes, connection pool exhaustion, synchronous I/O, over-fetching

**Memory**: Monotonic heap growth (leak), burst allocation GC churn, premature promotion, unbounded cache

**CPU**: Busy-wait loops, hot codec (serialization), uncached regex, lock contention

**Mobile (Android)**: ANR on main thread, UI jank, overdraw, WakeLock abuse, battery drain from background work

**Mobile (iOS)**: Main thread I/O, deep autolayout graph, retain cycles, Core Data on main thread

**Mobile (Flutter)**: Expensive `build()` methods, shader compilation jank, large isolate messages, heavy list cells

**Networking**: Chatty API, missing compression, no connection reuse, oversized images, sequential loading

**Database**: Missing indexes (`EXPLAIN ANALYZE` first), SELECT *, missing composite index, ORM over-fetching

### Diagnostic Approach

1. Match the symptom to a domain from the quick reference above
2. Look up the specific pattern and fix in `references/bottleneck-lookup.md`
3. Confirm with data before implementing: run `EXPLAIN ANALYZE`, attach a profiler, or measure with a benchmark
4. Apply the `impact-matrix` skill to prioritize multiple findings

### Cross-Domain Signals

Some symptoms span multiple domains — check these cross-cutting patterns first:

- **Periodic latency spikes** → GC pause + background job + cache invalidation (all three at once)
- **Slow under load only** → thread/connection pool contention (not a code bug)
- **Fast p50, slow p99** → lock wait or GC stop-the-world on a fraction of requests
- **Memory growing then dropping** → burst allocation, not a leak; reduce short-lived object creation
- **First request slow, subsequent fast** → cold-path (JIT, DNS, connection init) — warm up or cache

## Additional Resources

- **`references/bottleneck-lookup.md`** — Full symptom → pattern → fix lookup tables by domain (response time, web, API/backend, memory, CPU, mobile, networking, database)
- **`impact-matrix`** — Apply after gathering multiple findings to prioritize which to fix first

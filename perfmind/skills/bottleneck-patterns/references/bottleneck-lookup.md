# Bottleneck Pattern Lookup Tables

Full symptom → pattern → fix reference by domain.

## Response Time Patterns

| Symptom                           | Pattern Name       | Likely Cause                                       |
|-----------------------------------|--------------------|----------------------------------------------------|
| p50 fast, p99 slow                | Tail latency       | GC pauses, lock contention, noisy neighbor         |
| Uniformly slow for all users      | Throughput ceiling | CPU saturation, I/O bound, thread pool exhausted   |
| Slow on first request, fast after | Cold path          | JIT compilation, cache miss, connection pool init  |
| Periodic spikes every N minutes   | Batch interference | Background jobs, GC full cycle, cache invalidation |
| Slow only under load              | Contention         | Thread lock, DB connection pool, rate limiter      |

## Web Application Patterns

**Core Web Vitals targets**: LCP <2.5s · INP <200ms · CLS <0.1

| Symptom                     | Pattern                   | Fix                                                                  |
|-----------------------------|---------------------------|----------------------------------------------------------------------|
| Slow page load              | Render-blocking resources | Move CSS/JS to `<body>` end or add `defer`/`async`                   |
| Large JS bundle             | Monolithic bundle         | Split by route; lazy-load non-critical chunks                        |
| Slow image load             | Unoptimized images        | Use WebP/AVIF; add `loading="lazy"`; specify dimensions              |
| High INP                    | Layout thrashing          | Batch DOM reads before writes; avoid forced reflow in event handlers |
| Repeated asset fetches      | Missing HTTP cache        | Add long-lived `Cache-Control` on static assets                      |
| High TTFB for distant users | No CDN                    | Serve static assets from CDN edge nodes                              |
| Slow hydration (SSR)        | Large JS payload          | Defer non-interactive hydration; use streaming SSR                   |

## API / Backend Patterns

| Symptom                        | Pattern                    | Fix                                                              |
|--------------------------------|----------------------------|------------------------------------------------------------------|
| N queries for N items          | N+1 query                  | Batch with `IN` clause or join; use dataloader pattern           |
| Full table scan                | Missing index              | `EXPLAIN ANALYZE` → add index on filtered/sorted column          |
| Requests queuing for DB        | Connection pool exhaustion | Increase pool size or reduce query hold time                     |
| Blocking I/O on request thread | Synchronous I/O            | Move to async/non-blocking I/O                                   |
| Unused fields in response      | Over-fetching              | Use sparse fieldsets, GraphQL, or projection                     |
| Repeated identical DB reads    | No caching                 | Add Redis/Memcached for hot read keys                            |
| Slow serialization             | Expensive codec            | Switch to binary format (protobuf, msgpack) or schema-based JSON |

## Memory Patterns

| Symptom                       | Pattern             | Fix                                                           |
|-------------------------------|---------------------|---------------------------------------------------------------|
| Heap grows indefinitely       | Memory leak         | Heap diff to find retained objects; check listeners/callbacks |
| Allocation spike then GC drop | Burst allocation    | Pool or reuse objects; pre-allocate buffers                   |
| High old-gen after GC         | Premature promotion | Tune survivor space ratio; reduce object lifetime             |
| String concatenation in loop  | O(n²) copies        | Replace with `StringBuilder` / `Buffer` / `join()`            |
| Cache grows without bound     | Unbounded cache     | Add LRU eviction and size cap                                 |

## CPU Patterns

| Symptom                        | Pattern                   | Fix                                                                         |
|--------------------------------|---------------------------|-----------------------------------------------------------------------------|
| 100% CPU, no useful work       | Busy-wait / spin loop     | Replace with condition variable, `await`, or sleep-backoff                  |
| Serialization on critical path | Hot codec                 | Cache serialized form; use binary format                                    |
| Regex recompiled per request   | Uncached regex            | Compile once at startup; store as constant                                  |
| Reflection in hot loop         | Dynamic dispatch overhead | Replace with static dispatch or code generation                             |
| Many threads, low throughput   | Lock contention           | Shard the lock; use lock-free data structures; reduce critical section size |

## Mobile-Specific Patterns

### Android

| Symptom                     | Pattern                 | Fix                                                               |
|-----------------------------|-------------------------|-------------------------------------------------------------------|
| App freezes ~5s             | ANR                     | Move work off main thread → `Coroutine`, `AsyncTask` replacement  |
| Dropped frames / jank       | UI thread overload      | Profile with Systrace; defer work with `View.post()` or coroutine |
| Multiple translucent layers | Overdraw                | Reduce view hierarchy depth; remove unnecessary backgrounds       |
| Device wakes too often      | WakeLock abuse          | Use `WorkManager` with constraints instead of `AlarmManager`      |
| Battery drain in background | Background work         | Consolidate with `WorkManager`; respect `Doze` and `App Standby`  |
| `onTrimMemory` ignored      | Memory pressure ignored | Release caches on `TRIM_MEMORY_RUNNING_CRITICAL`                  |

### iOS

| Symptom                       | Pattern                | Fix                                                       |
|-------------------------------|------------------------|-----------------------------------------------------------|
| UI freezes on data load       | Main thread I/O        | Dispatch `URLSession` work to background queue            |
| Complex layout slow to render | Deep autolayout graph  | Reduce constraint count; use manual layout for list cells |
| Retain cycle → memory leak    | Strong closure capture | Use `[weak self]` in `@escaping` closures                 |
| Core Data UI stutter          | Main thread fetch      | Use background `NSManagedObjectContext` with `perform {}` |
| Background task killed early  | BGTask timeout         | Prioritize critical work; split with `BGProcessingTask`   |

### Flutter (Cross-platform Mobile)

| Symptom                            | Pattern                 | Fix                                                                         |
|------------------------------------|-------------------------|-----------------------------------------------------------------------------|
| Full tree rebuilds on state change | Expensive `build()`     | Extract widgets; use `const`; add `RepaintBoundary`                         |
| First-frame stutter                | Shader compilation jank | Use `--bundle-sksl-path` and warm up shaders at app start                   |
| Isolate message lag                | Large isolate message   | Minimize data copied across isolate boundary; use `TransferableTypedData`   |
| Slow list scroll                   | Heavy cell build        | Use `ListView.builder`; cache complex widgets; avoid `Column` inside scroll |

## Networking Patterns

| Symptom                   | Pattern             | Fix                                                        |
|---------------------------|---------------------|------------------------------------------------------------|
| Many small requests       | Chatty API          | Batch or multiplex over HTTP/2                             |
| Large response payloads   | Missing compression | Enable `gzip`/`brotli` on server                           |
| New TCP per request       | No connection reuse | Enable HTTP keep-alive; use connection pool                |
| Slow DNS on first load    | No pre-resolve      | Add `<link rel="dns-prefetch">` (web) or DNS cache warming |
| Full-res images to mobile | No image resizing   | Serve responsive images via CDN transform or `srcset`      |
| Sequential resource load  | No HTTP/2           | Enable HTTP/2 on server; multiplex critical resources      |

## Database Query Patterns

Always run `EXPLAIN ANALYZE` before optimizing any query.

| Symptom                           | Pattern              | Fix                                                     |
|-----------------------------------|----------------------|---------------------------------------------------------|
| Seq scan on large table           | Missing index        | Add index on filtered or sorted column                  |
| `SELECT *` everywhere             | Column over-fetching | List only needed columns                                |
| Filter on A+B, no composite index | Partial index        | Add `(A, B)` composite index in query order             |
| High lock wait time on hot row    | Locking read         | Switch to optimistic locking; read without `FOR UPDATE` |
| Missing join condition            | Cartesian join       | Audit all joins; add explicit `ON` clause               |
| ORM `findAll()` with eager load   | ORM over-fetching    | Use lazy loading or explicit `select` with projection   |

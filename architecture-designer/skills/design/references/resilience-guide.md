# Error Handling and Resilience Strategy Guide

Use this guide when confirming Stage 5's error-handling/resilience strategy (Technology Decisions item 10) and when
`architecture-implementer` wires that strategy into calls to external dependencies. It follows the same discipline as
the rate-limiting strategy (item 11, `references/rate-limiting-guide.md`): name a specific pattern and a specific
library per language, not an abstract "add retries" note.

## Why this matters

- **Cascading failure prevention** — an unthrottled retry storm against an already-struggling dependency turns a partial
  outage into a total one; a caller with no timeout budget hangs indefinitely waiting on a dependency that will never
  respond.
- **Graceful degradation** — a non-critical feature failing shouldn't take the whole request down with it; a payment
  gateway blip shouldn't also break the product catalog page that happens to share a request.
- **Operational visibility** — a system that silently swallows every dependency failure is undebuggable; one that
  crashes on every transient blip is unusable. The point of a resilience strategy is choosing, deliberately, which
  failures are transient-and-retryable versus permanent-and-must-surface.

## When this applies

Any system that calls an external dependency (a third-party API, another internal service in a
microservices/event-driven pattern, a payment gateway, a message broker) needs a named resilience strategy — this is
already checked in `architecture-reviewer.md` dimension 5 (**Major** if a must-not-fail-silently dependency has no retry
policy and timeout budget named). A monolith with no external dependencies (only its own database, which has its own
connection-pool/retry semantics handled at the driver level) can skip this section — state that explicitly, the same way
item 11 is skipped for a system with no public API.

## Patterns and when each applies

| Pattern                                  | What it does                                                                                                                                                                                                                                        | When to use it                                                                                                                                                                                                               |
|------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Retry with backoff**                   | Re-attempt a failed call after a delay, growing the delay each attempt (exponential backoff), with random jitter added to avoid synchronized retry storms across many callers                                                                       | Any call to a dependency where transient failures (network blip, momentary overload) are expected and the call is safe to repeat (idempotent, or made idempotent via a request/mutation ID)                                  |
| **Circuit breaker**                      | Track a dependency's recent failure rate; once it crosses a threshold, stop calling it entirely for a cool-down period (open state) and fail fast instead, then cautiously allow a trial request through (half-open) before fully resuming (closed) | 3+ external dependencies, or any single dependency marked must-not-fail-silently (e.g. payment capture) — stops a struggling dependency from being hammered by retries from every caller while it's trying to recover        |
| **Timeout budget**                       | A hard upper bound on how long a synchronous call is allowed to take before the caller gives up, distinct from retry count                                                                                                                          | Every synchronous external call, always — a retry policy without a timeout budget can still hang forever on a single attempt before ever reaching the retry logic                                                            |
| **Bulkhead / connection-pool isolation** | Cap the concurrent connections/threads a single dependency can consume, so one slow dependency can't exhaust the resource pool shared by calls to other, healthy dependencies                                                                       | Systems with 3+ external dependencies sharing a connection pool or thread pool, where one dependency degrading shouldn't starve calls to the others                                                                          |
| **Graceful degradation / fallback**      | Return a degraded-but-usable response (cached data, a default value, a "feature temporarily unavailable" state) instead of failing the whole request when a non-critical dependency is down                                                         | Any feature where the Stage 2 error-handling NFR says a degraded response is acceptable — never for an operation the NFR marked must-not-fail-silently (e.g. never silently "degrade" a payment capture into a fake success) |

These patterns compose — a well-specified strategy for a must-not-fail-silently dependency typically names all of: retry
policy, circuit breaker, and timeout budget together, not just one in isolation.

## Retry policy specifics

A retry policy is underspecified until it names: **backoff strategy** (exponential is the default — fixed-interval
retries synchronize into their own retry storm under load), **jitter** (randomize the delay to spread retries out, not
just the base backoff), **max attempts** (an unbounded retry loop is not a retry policy, it's a hang), and **which
failures are retryable** (a 503/timeout is retryable; a 400/422 validation error is not — retrying a request that will
deterministically fail again just wastes time and load). State all four, not just "retry with backoff."

**Idempotency is a precondition for retrying anything that mutates state** — a payment-capture call retried without an
idempotency key can double-charge. Use the same client-generated mutation/idempotency ID discipline
`references/offline-first-guide.md` section 2 describes for sync mutations, applied here to any retried external write.

## Timeout budget specifics

Every synchronous external call needs an explicit timeout, sized to that specific dependency's expected latency (not one
blanket number for every call in the system). When a request chains multiple downstream calls, the timeout budget should
shrink as it propagates — a 5-second budget at the edge doesn't mean every downstream call independently gets 5 seconds;
each hop consumes part of the parent's budget so the total path can't exceed what the original caller is willing to
wait.

## Response/error contract

When a dependency call ultimately fails (retries exhausted, circuit open, or timeout hit), the caller's own response
must match `references/lld-guide.md`'s Error Catalog format — a `503`-class error with a distinguishable code (e.g.
`DEPENDENCY_UNAVAILABLE`), not a bare `500` that hides whether the failure was this service's own bug or a downstream
dependency's outage.

## Library per stack

| Stack         | Retry                                                                                                                                                        | Circuit breaker                                                                                                                                          | Timeout                                                        |
|---------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------|
| Node.js       | `axios-retry` (if using axios), `cockatiel` (retry + circuit breaker + bulkhead in one library)                                                              | `opossum`, or reuse `cockatiel`'s own circuit-breaker policy if already adopted for retry (they are separate, unrelated libraries — pick one, don't mix) | Native `AbortController` / per-client timeout config           |
| Python        | `tenacity`                                                                                                                                                   | `pybreaker` (or `circuitbreaker`)                                                                                                                        | `httpx`/`aiohttp` client-level timeout                         |
| Go            | `cenkalti/backoff` (or hand-rolled — the pattern is small in Go, but still use a maintained backoff/jitter implementation rather than hand-rolling the math) | `sony/gobreaker`                                                                                                                                         | `context.WithTimeout` propagated through the call chain        |
| Rust          | `backoff` crate (or `tokio-retry`)                                                                                                                           | no single dominant crate as of this writing — verify current ecosystem state; `failsafe-rs` is one option                                                | `tokio::time::timeout`                                         |
| Java / Spring | `resilience4j` (retry module)                                                                                                                                | `resilience4j` (circuit-breaker module — same library as retry, its main draw)                                                                           | `resilience4j` (timeout module) or client-level timeout config |
| .NET          | `Polly` (retry policy)                                                                                                                                       | `Polly` (circuit-breaker policy — same library)                                                                                                          | `Polly` (timeout policy) or `HttpClient.Timeout`               |
| Ruby / Rails  | `retriable`                                                                                                                                                  | `semian` (originally built at Shopify specifically for this)                                                                                             | Net::HTTP / Faraday client-level timeout                       |

Node's `cockatiel` and Java/.NET's `resilience4j`/`Polly` are notable for covering retry, circuit breaker, and timeout
in one library with a consistent policy-composition API — prefer one of those over stitching together three separate
single-purpose libraries when the ecosystem offers it.

## What not to hand-roll

Don't hand-write a custom retry loop with `sleep()` calls or a custom circuit-breaker state machine when a maintained
library exists for the stack — exponential backoff with correct jitter, and a circuit breaker's half-open trial-request
logic, are exactly the kind of concurrency-sensitive code that's easy to get subtly wrong (thundering herd from
synchronized retries, a circuit that never actually closes again). Hand-roll only when no library exists for a genuinely
niche stack, the same narrow exception `references/scaffolding-guide.md` and `references/rate-limiting-guide.md` each
carve out for their own domain.

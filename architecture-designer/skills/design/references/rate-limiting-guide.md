# Rate Limiting Middleware Strategy Guide

Use this guide when confirming Stage 5's rate-limiting strategy (Technology Decisions item 11) and when
`architecture-implementer` wires that strategy into route handlers. It follows the same discipline as the
error-handling/resilience strategy already required by Stage 5: name a specific algorithm and a specific library per
language, not an abstract "add rate limiting" note.

## Why rate limit

- **Abuse and scraping prevention** — stop a single client from monopolizing the API.
- **Fair use across tenants/users** — one noisy user shouldn't degrade service for everyone else.
- **Protecting downstream dependencies** — a database, a third-party API with its own rate limit, or a payment gateway
  can be overwhelmed by unthrottled upstream traffic just as easily as by a real outage.
- **Cost control** — every call to a metered external API (SMS, email, LLM inference, geocoding) has a marginal cost;
  unthrottled retries or abuse translate directly into a bill.

## When this applies

Any system with a public-facing API, or any internal API reachable by untrusted or semi-trusted clients (a mobile app, a
partner integration), needs a named rate-limiting strategy — this is already a **Major** finding in
`architecture-reviewer.md` dimension 5 when missing for a public API. A fully internal system with no untrusted caller
(e.g., a batch job calling another internal service inside a private network, already covered by mTLS/service-mesh
trust) can skip this section, the same way the resilience strategy is skipped for a monolith with no external
dependencies — state that explicitly rather than silently omitting it.

## Algorithms and tradeoffs

| Algorithm                           | How it works                                                                                             | Tradeoff                                                                                                                                                                                                               |
|-------------------------------------|----------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Fixed window**                    | Count requests in a fixed clock interval (e.g., per-minute bucket), reset at the boundary                | Cheapest to implement and reason about, but allows a burst of up to 2× the limit at the window boundary (e.g., 100 requests at 0:59 and 100 more at 1:00)                                                              |
| **Sliding window (log or counter)** | Track requests in a rolling window rather than a fixed boundary                                          | Smooths out the boundary-burst problem at the cost of slightly more memory (log) or a small approximation error (counter-based sliding window)                                                                         |
| **Token bucket**                    | Bucket refills at a steady rate; each request consumes one token; requests fail when the bucket is empty | Allows short bursts up to the bucket size while still enforcing an average rate — the best default for most public APIs, since real clients are bursty                                                                 |
| **Leaky bucket**                    | Requests queue and are processed (or dropped) at a fixed output rate                                     | Smooths *outgoing* rate rather than tolerating bursts — best when protecting a downstream with genuinely fixed capacity (e.g., a legacy system that cannot handle spikes at all), not for general API abuse prevention |

**Default recommendation**: token bucket for general-purpose public APIs (tolerates real client burstiness); sliding
window counter when strict fairness at the boundary matters more than burst tolerance; fixed window only for coarse,
low-stakes limits where implementation simplicity outweighs the boundary-burst risk; leaky bucket only when smoothing
throughput to a fixed downstream capacity is the actual goal.

## Where to enforce

- **Edge / API gateway** (Kong, AWS API Gateway usage plans, Cloudflare rate limiting rules, Nginx) — coarse, per-IP or
  per-API-key limits applied before a request reaches application code. This is what protects infrastructure from raw
  floods and is what `architecture-reviewer`'s existing perimeter-security check (dimension 5, under "Security controls
  at the perimeter") flags as **Major** when absent for a public API.
- **Application middleware** — business-specific limits the gateway cannot know about: per-user tiers (free vs. paid),
  per-endpoint sensitivity (a login endpoint needs a much tighter limit than a public listing endpoint), or limits keyed
  on an authenticated identity rather than a raw IP (which breaks down behind NAT/shared proxies).

These two layers are complementary, not redundant — a gateway limit alone cannot express "free-tier users get 100
requests/day," and application middleware alone leaves the infrastructure exposed to a flood before authentication even
runs. State both when both are architecturally relevant; a system with no API gateway (e.g., a small monolith behind a
load balancer with no gateway layer) enforces everything at the application middleware layer instead, and that's a
valid, complete answer — not a gap.

## Per-tier and per-endpoint limits

Tie limits to the confirmed user roles and plan tiers from Stages 1–2, and to endpoint sensitivity:

- **Authentication endpoints** (login, password reset, OTP verification) get the tightest limits of any endpoint group —
  these are the direct target of credential-stuffing and brute-force attacks. A common shape: a low per-account-plus-IP
  limit (e.g., 5 attempts/minute) distinct from the general per-IP limit, so a single attacker can't brute-force one
  account by rotating IPs, and a single IP can't be used to spray many accounts.
- **Write-heavy / expensive endpoints** (anything that triggers a paid external call, a heavy computation, or a bulk
  operation) get a tighter limit than simple reads.
- **Anonymous vs. authenticated vs. premium tiers** — if Stage 1–2 confirmed distinct user roles or plan tiers, the
  limit must vary by tier, not apply one blanket number to every caller.
- **WebSocket/streaming connections**: the algorithms and `429`/`Retry-After` contract above apply to discrete
  requests — a persistent connection needs its own limits instead: a max-concurrent-connections-per-account/IP cap, and
  a message-rate cap (messages/sec over the open connection) separate from the initial handshake's own rate limit.
- **GraphQL APIs**: a single request can be arbitrarily expensive regardless of request-count limits — pair the
  per-IP/per-account request-count limit above with a query-cost limit (assign each field/type a cost, cap total cost
  per request) or a query-depth/complexity limit, so one deeply-nested query can't bypass the rate limit's intent.

## Distributed enforcement

- **Single instance**: an in-process, in-memory counter (the library's default store) is sufficient — no shared state
  needed.
- **Horizontally scaled** (per the Stage 4/5 infrastructure decision, or a Stage 2 NFR requiring auto-scaling): an
  in-memory counter is wrong here — each instance would enforce the limit independently, effectively multiplying the
  real limit by the instance count. Counters must live in a shared store so the limit is enforced consistently across
  all instances. Redis is the standard choice — this is the same Redis instance `tech-stacks.md`'s cache/session-store
  table already names for this purpose; do not stand up a second store just for rate-limit counters if one is already
  provisioned for sessions/caching. Name the specific Redis-backed adapter for the chosen library (e.g.,
  `rate-limit-redis` for `express-rate-limit`, `rate-limiter-flexible`'s built-in Redis storage engine).

## Response contract

- **Status**: `429 Too Many Requests`.
- **`Retry-After` header**: seconds until the client may retry (standard HTTP header, respected by most HTTP clients
  automatically).
- **`X-RateLimit-Limit` / `X-RateLimit-Remaining` / `X-RateLimit-Reset` headers**: the informal-but-widely-adopted
  convention that lets well-behaved clients self-throttle before hitting the limit, rather than discovering it only via
  a 429.
- **Body**: must match `lld-guide.md`'s existing `RATE_LIMITED` error catalog entry
  (`{ error: "RATE_LIMITED", retryAfter: int }`) — do not invent a different response shape per endpoint.

## Library per stack

| Stack                              | Library                                                                                   | Distributed (Redis) support                                                                                                                       |
|------------------------------------|-------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| Node.js / Express                  | `express-rate-limit`                                                                      | `rate-limit-redis` store adapter                                                                                                                  |
| Node.js / Fastify                  | `@fastify/rate-limit`                                                                     | built-in Redis store option                                                                                                                       |
| Node.js / NestJS                   | `@nestjs/throttler`                                                                       | `ThrottlerStorageRedisService`                                                                                                                    |
| Python / FastAPI                   | `slowapi`                                                                                 | Redis-backed limiter via `limits` library's storage backend                                                                                       |
| Python / Django (DRF)              | DRF `throttling` classes (`UserRateThrottle`, `ScopedRateThrottle`) or `django-ratelimit` | Django cache backend set to Redis                                                                                                                 |
| Go                                 | `golang.org/x/time/rate` wrapped as middleware (single instance), or `ulule/limiter`      | `ulule/limiter`'s Redis store                                                                                                                     |
| Rust (Axum / Tower)                | `tower-governor` (built on the `governor` crate — token bucket)                           | no first-party Redis adapter — implement via Redis + a Lua script, or enforce distributed limits at the gateway layer instead                     |
| Rust (Actix-web)                   | `actix-governor` (same `governor` crate underneath)                                       | same as above — no first-party Redis adapter                                                                                                      |
| Java / Spring                      | `Bucket4j`                                                                                | `bucket4j-redis`                                                                                                                                  |
| Java / Spring (resilience-focused) | Resilience4j `RateLimiter`                                                                | in-process only — pair with `Bucket4j` + Redis for distributed enforcement                                                                        |
| .NET                               | Built-in `Microsoft.AspNetCore.RateLimiting` (.NET 7+)                                    | requires a custom distributed partition store; no first-party Redis adapter as of this writing — verify current ecosystem state before naming one |
| Ruby / Rails                       | `rack-attack`                                                                             | Redis-backed via `ActiveSupport::Cache::RedisCacheStore`                                                                                          |
| Any stack, gateway layer           | Kong's rate-limiting plugin, AWS API Gateway usage plans, Cloudflare rate limiting rules  | handled by the gateway/CDN itself, not the application                                                                                            |

This table is not exhaustive — for a confirmed stack not listed, check that ecosystem's standard library ecosystem
before falling back to a hand-rolled implementation, the same "verify, don't fabricate" discipline
`scaffolding-guide.md` applies to generator commands.

## What not to hand-roll

Don't hand-write a custom in-memory counter or sliding-window algorithm when a maintained library exists for the
confirmed stack — race conditions under concurrent requests and off-by-one boundary math are exactly the class of bug
these libraries have already solved and tested. Hand-roll only when no library exists for a genuinely niche stack — the
same narrow exception `scaffolding-guide.md`'s "When no generator exists" section carves out for project scaffolding,
applied here to middleware instead.

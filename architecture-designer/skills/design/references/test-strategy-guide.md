# Test Strategy Guide

Use this guide at Step 10b (`design/SKILL.md`), after Low-Level Design (Step 10) is confirmed and before the document is
saved (Step 11). It produces a **test plan as a document artifact** — what gets tested, at what level, against what
target, with which tool — derived from data already gathered in Stages 2, 4, and 5 and from the LLD's error catalog.

**Scope distinction**: this guide covers planning *what to test and to what target*, not *how the generated test code
itself is written*. `references/clean-code-guide.md`'s FIRST properties and Arrange-Act-Assert structure (its "FIRST
principles for unit tests" and "Arrange-Act-Assert (AAA)" sections) govern the code `architecture-implementer` generates
for each test file — this guide governs the plan that tells it which test files to generate and what they must verify.
Do not restate FIRST/AAA here; cross-reference them.

## Why this matters

A capacity plan with numeric targets (Stage 4) and Quality Attribute Scenarios with numeric response measures (Stage 2)
are unfalsifiable until something actually measures against them. Without a named load-test target and tool, "the system
should handle 500 concurrent users" stays an aspiration through implementation and is only ever checked, if at all, in
production under real load — the most expensive place to discover it's wrong.

## 1. Test pyramid

State the planned ratio and scope at each level, sized to the project — a small monolith may legitimately skip the
contract-test row entirely:

| Level       | Scope                                                                                                                                                                   | Ownership                                                                                                             |
|-------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| Unit        | One test file per business rule (Step 10 group 2) and per aggregate invariant (`domainModel`) — the majority of the suite                                               | `architecture-implementer`, per `references/session-schema.md`'s implementation task-group table ("Write test files") |
| Integration | One test per API contract group (Step 10 group 1), exercising the real database (or a test-container instance) rather than a mock                                       | Same                                                                                                                  |
| Contract    | Microservices/event-driven only — one per inter-service contract (Step 10 group 4), verifying the producer/consumer schema agreement named there                        | Same; omit entirely for a monolith, the same condition Step 10 group 4 itself omits                                   |
| End-to-end  | One per **core feature** (`references/document-template.md` section 2) — the primary flow only, not every branch; branch coverage belongs at the unit/integration level | Same, or a separate E2E suite if the confirmed stack names one (e.g. Playwright/Cypress)                              |

## 2. Load and performance testing

Derive targets directly from two already-confirmed sources — never invent a target that isn't traceable to one of them:

- **Quality Attribute Scenarios** (`stage2.qualityAttributeScenarios`) whose `qualityAttribute` is Performance or
  Scalability — its `responseMeasure` field *is* the test's pass/fail threshold (e.g. QAS-1's "95th percentile under
  500ms under peak load" becomes the load test's assertion, not a new number).
- **Stage 4 capacity numbers** — concurrent users, TPS, and peak-pattern multiplier size the load profile itself (steady
  state, spike, soak duration).

**Scenario types**: steady-state (sustained load at the Stage 4 baseline number), spike (sudden burst to the Stage 4
peak-factor number), and soak (steady-state sustained for an extended duration, to catch memory leaks/connection-pool
exhaustion the shorter scenarios wouldn't surface).

**Tool per stack** — name a specific tool, the same specificity discipline Stage 5 applies to every other technology
choice:

| Stack context                                                      | Tool                                |
|--------------------------------------------------------------------|-------------------------------------|
| HTTP APIs, scriptable in JS                                        | k6                                  |
| HTTP APIs, Java/JVM ecosystem already in the stack                 | Gatling                             |
| HTTP APIs, Python ecosystem already in the stack                   | Locust                              |
| Enterprise/legacy, existing JMeter expertise on the team (Stage 3) | JMeter                              |
| WebSocket/streaming connections                                    | k6 (native WS support) or Artillery |

Skip this section's tool selection only when Stage 2 recorded no Performance/Scalability Quality Attribute Scenario at
all — state that explicitly rather than inventing a target with no NFR behind it.

## 3. Resilience and chaos testing

One test scenario per resilience pattern actually named in Stage 5 item 10 (`references/resilience-guide.md`) — do not
invent a scenario for a pattern the stack doesn't use:

| Stage 5 pattern named                | Chaos scenario                                                                                                                                                                                                                  |
|--------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Retry with backoff                   | Inject transient failure (e.g. via a fault-injection proxy) on a dependency call; verify the retry policy's max-attempts and backoff timing match what was specified                                                            |
| Circuit breaker                      | Force a dependency's failure rate past the configured threshold; verify the breaker opens, fails fast (no hanging calls), and the response matches the `DEPENDENCY_UNAVAILABLE` error-catalog entry (`references/lld-guide.md`) |
| Timeout budget                       | Inject latency exceeding the configured budget on a dependency call; verify the caller aborts at the budget, not later                                                                                                          |
| Graceful degradation                 | Simulate the non-critical dependency being down; verify the degraded-but-usable response, not a full request failure                                                                                                            |
| Bulkhead / connection-pool isolation | Saturate one dependency's pool; verify calls to a different, healthy dependency are unaffected                                                                                                                                  |

Skip this section entirely for a monolith with no external dependencies — the same condition
`references/resilience-guide.md` itself uses to skip Stage 5 item 10.

## 4. Security testing

This is a **verification checklist for what the design already specified**, not a substitute for a full security audit —
for a comprehensive code-level security review, point the user at this plugin ecosystem's dedicated audit tooling
(`/audit`, `/audit-diff`) rather than duplicating that scope here. Derive each item from a specific NFR or LLD entry,
never a generic OWASP-list restatement disconnected from this project's actual design:

- One check per authentication/authorization error-catalog entry (`references/lld-guide.md`) — e.g. "expired token
  returns `TOKEN_EXPIRED`, not a silent 200," "cross-tenant access to another user's resource returns `FORBIDDEN`, not
  the data."
- One check per rate-limiting rule confirmed in Stage 5 item 11 (`references/rate-limiting-guide.md`) — e.g. "6th login
  attempt within the configured window returns `429` with `Retry-After`."
- One check per Stage 2 compliance/security NFR marked **"⚠ Needs legal/compliance validation"** (per `design/SKILL.md`
  Stage 2's compliance-grounding rule) — the test verifies the *technical control* is actually implemented as specified;
  it does not re-litigate whether the control satisfies the legal requirement, which stays the compliance team's call.

## 5. User Acceptance Testing (UAT)

One Given/When/Then acceptance scenario per **core feature** (`references/document-template.md` section 2 — the same set
Stage 6d's "Core feature coverage requirement" gives a dedicated sequence diagram) — the primary happy path only; edge
cases are already covered by the unit/integration levels above.

**Format**:

```markdown
| Feature | Scenario | Given | When | Then |
|---------|----------|-------|------|------|
| Place order | Successful checkout | Cart has 2 in-stock items | Customer submits payment | Order is created, confirmation email sent within 60s |
```

## Where this fits

Write the confirmed plan to `session.json`'s top-level `testStrategy` key (create it) at Step 10b, per
`references/session-schema.md`. It is embedded in the architecture document's **Test Strategy** section
(`references/document-template.md`). `review/SKILL.md`'s "Update Test Strategy" step (4d.6) re-runs this guide whenever
a revision changes an NFR, the capacity plan, the resilience/rate-limiting strategy, or a core feature — the same
trigger set that already re-runs the LLD update (4d.5), applied here since the targets above are sourced from exactly
those same inputs.

## Skip condition

None. Every project has at minimum a UAT checklist (core features always exist) and a test pyramid (unit tests always
apply, even to a system with no external dependencies and no public API). Load, resilience, and security sub-sections
may each be legitimately empty per their own skip conditions above — state that explicitly rather than omitting the
section heading.

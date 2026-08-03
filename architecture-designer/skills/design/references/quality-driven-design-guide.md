# Quality-Driven Design Guide (Quality Attribute Scenarios, Architectural Drivers, Trade-off/Risk Analysis)

Use this guide at the end of Stage 2 (Quality Attribute Scenarios), at the start of Stage 5 (Architectural Drivers), and
at the end of Stage 5 (Trade-off and Risk Analysis) per `design/SKILL.md`. It formalizes the SEI Attribute-Driven Design
(ADD) and Architecture Tradeoff Analysis Method (ATAM) practices a professional architect uses instead of choosing a
stack on intuition: turn vague non-functional requirements into testable scenarios, rank the few that actually shape the
architecture, cite them by ID when making each Stage 5 decision, then make explicit — rather than silently absorbed —
the trade-offs and risks those decisions create.

## Why this matters

- **Testability** — "the system should be fast" cannot be verified; "search results return in under 500ms at the 95th
  percentile under peak load" can. A scenario turns an opinion into a target the reviewer, the implementer, and a future
  incident review can all check against the same number.
- **Traceability** — when a Stage 5 decision cites the driver it satisfies, a later "why did we choose this?" question
  has a documented answer instead of a reconstructed guess, and a later "does this decision still make sense?" question
  (Step 9 revision, `/architecture-designer:review`) has something concrete to re-evaluate against.
- **Surfacing hidden trade-offs** — two quality attributes rarely both get the best possible answer from the same
  decision (strong consistency and low read latency pull in different directions; horizontal scalability and simple
  operational model pull in different directions). Naming the trade-off explicitly, at design time, is cheaper than
  discovering it as an incident.

## Quality Attribute Scenarios (end of Stage 2)

A Quality Attribute Scenario is a six-part, testable statement. Formalize the 3–8 non-functional requirements from Stage
2 that have (or can be given) a concrete target — not every NFR needs one; "the UI should look modern" has no measurable
stimulus/response and stays as ordinary prose in `stage2.nonFunctionalRequirements`.

| Part                 | Question it answers                                                                                             |
|----------------------|-----------------------------------------------------------------------------------------------------------------|
| **Source**           | Who or what triggers the scenario? (end user, admin, another system, an operator, a scheduled job)              |
| **Stimulus**         | What condition or event arrives?                                                                                |
| **Environment**      | Under what conditions? (normal operation, peak load, degraded/partial-failure state, startup)                   |
| **Artifact**         | What part of the system is stimulated? (a specific API, the whole system, a specific data store)                |
| **Response**         | What should happen?                                                                                             |
| **Response measure** | How is the response measured, with a number? (percentile latency, uptime percentage, recovery time, error rate) |

**Worked examples**, one per common quality attribute:

- **Performance**: Source: end user. Stimulus: submits a search query. Environment: peak load. Artifact: search API.
  Response: returns ranked results. Response measure: 95th percentile under 500ms.
- **Availability**: Source: any client. Stimulus: a single application-tier instance crashes. Environment: normal
  operation. Artifact: the whole system. Response: traffic is rerouted to healthy instances with no user-visible outage.
  Response measure: 99.9% monthly uptime, failover completes within 30s.
- **Security**: Source: an unauthenticated attacker. Stimulus: attempts 100 login requests in 10 seconds against one
  account. Environment: normal operation. Artifact: auth API. Response: requests beyond the threshold are rejected and
  the account is not locked out for the legitimate user. Response measure: rate-limited within 5 requests/min per
  account per `rate-limiting-guide.md`.
- **Scalability**: Source: marketing campaign traffic. Stimulus: request volume triples over 10 minutes. Environment:
  planned peak event. Artifact: the whole system. Response: the system scales out without manual intervention. Response
  measure: p95 latency stays within 2× baseline throughout the scale-out.
- **Modifiability**: Source: developer. Stimulus: adds a new notification channel (e.g. SMS alongside email). Artifact:
  notification subsystem. Response: the change is isolated to one module. Response measure: no changes required outside
  the notification subsystem's own files.

Write the confirmed set to `session.json`'s `stage2.qualityAttributeScenarios` (array), each with a stable ID (`QAS-1`,
`QAS-2`, ...) at the same time `stage2` is written — see `references/session-schema.md`.

## Architectural Drivers (start of Stage 5)

Not every scenario shapes the architecture equally. Before proposing any of Stage 5's eleven technology decisions,
select 3–6 **Architecturally Significant Requirements (ASRs)** — the drivers that will actually determine which patterns
and technologies are chosen — from three sources: the Quality Attribute Scenarios above, Stage 3's constraints (a hard
budget ceiling, a mandated cloud provider, a legacy integration), and Stage 1's stated goals (a core differentiator the
business is built around).

**Selection criteria** — a scenario or constraint qualifies as a driver when at least one is true:

- **Business-critical**: failing to meet it would be a launch-blocking or reputation-critical failure (payment
  processing, data-loss prevention, a named compliance requirement).
- **Pervasive**: it constrains multiple Stage 5 items at once, not just one isolated choice (an availability target
  shapes infrastructure, database replication, and observability all at once).
- **High technical risk**: the team has no prior experience meeting it, or it pushes against a well-known hard trade-off
  (strict consistency at high write throughput, sub-100ms global latency).

A scenario that doesn't meet any of these stays a normal requirement — satisfied incidentally, not specifically
engineered for — and does not need a driver ID.

These criteria are judgment calls, not a formula — full ATAM resolves this ambiguity with structured stakeholder voting
across a whole utility tree, which this single-pass procedure deliberately doesn't replicate (see "Why this matters"
above on scaling the practice down). When a candidate is borderline, use one tiebreaker question: **would getting this
decision wrong be expensive to reverse after launch** (a schema/protocol choice baked into client behavior, a
consistency model client code depends on) **or cheap to fix later** (a logging library, a caching layer)?
Expensive-to-reverse borderline cases count as drivers; cheap-to-reverse ones don't. Different people running the same
session may still land on a slightly different 3–6, and that's an acceptable range, not a defect — the goal is naming
the decisions that actually shape the architecture, not producing one canonical list.

Write the ranked list to `session.json`'s top-level `architecturalDrivers` (array), each entry: `id` (`AD-1`,
`AD-2`, ...), `description`, `source` (a `QAS-n` ID, `"stage3-constraint"`, or `"stage1-goal"`), and one line of
`rationale`
citing which selection criterion above applies. Write this at the same time as `stage5` (see
`references/session-schema.md`).

**Stage 5 citation rule**: every one of the eleven Stage 5 items' justifications must name the specific driver ID (s) it
satisfies, in addition to the existing "cite a reason from stages 1–4" rule — e.g. "PostgreSQL with synchronous
replication, satisfying AD-2 (99.9% availability)" rather than just "PostgreSQL, a solid relational default." A decision
with no driver behind it is still fine (most of the eleven items are satisfied by ordinary, undriven best practice) —
but state that plainly ("no specific driver; standard choice for this scale") rather than inventing a driver citation to
fill the slot.

## Trade-off and Risk Analysis (end of Stage 5, ATAM-style)

After the eleven items are proposed and discussed, before final Stage 5 confirmation, walk through the decisions once
more looking specifically for tension between drivers — this mirrors ADD's driver-satisfaction check and ATAM's
sensitivity/trade-off analysis, scaled down to fit inside a single design session rather than a multi-day external ATAM
engagement.

Use three ATAM concepts:

- **Sensitivity point**: an architectural decision whose achievement of *one* particular quality attribute is highly
  sensitive to a specific parameter — small changes to that parameter swing the outcome significantly, which is why it's
  worth calling out explicitly rather than treating it as one setting among many. ("If peak TPS grows past 5,000, the
  chosen read-replica lag becomes unacceptable for AD-1's latency target.") A sensitivity point that turns out to affect
  a second driver in the opposite direction is a trade-off point instead — see below.
- **Trade-off point**: a decision that affects two or more drivers in opposite directions — improving one measurably
  worsens another. ("Eventual consistency via read replicas improves AD-1's read-latency target but weakens AD-3's
  strong-consistency requirement for the inventory count.") Every trade-off point is also a sensitivity point (it is
  sensitive to at least two attributes at once, not just one).
- **Risk**: a decision or gap that could cause a driver to go unmet, independent of any trade-off. ("No named owner for
  rotating the database credentials — a security risk against AD-4, not a trade-off against another driver.") Full ATAM
  categorizes every identified sensitivity/trade-off point as either a **risk** or a **non-risk** (considered and found
  acceptable) — this scaled-down pass keeps that spirit implicitly: only record items serious enough to need mitigation
  in `riskRegister`; a considered-and-dismissed point doesn't need a "non-risk" entry of its own, unlike a full external
  ATAM engagement's formal risk/non-risk ledger.

For each trade-off point found, record: which drivers are in tension, the trade-off itself, the sensitivity parameter
(if any), the decision actually made, and the rationale for choosing that side of the trade-off. Write to
`session.json`'s `stage5.tradeoffAnalysis` (array), each entry with a stable ID (`TO-1`, `TO-2`, ...).

**Trade-off Analysis format**:

| ID   | Drivers in tension | Trade-off point                                                                                                 | Sensitivity point                                              | Decision                               | Rationale                                             |
|------|--------------------|-----------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------|----------------------------------------|-------------------------------------------------------|
| TO-1 | AD-1, AD-3         | Eventual consistency via read replicas improves read latency but weakens strong-consistency for inventory count | If peak TPS grows past 5,000, replica lag becomes unacceptable | Read replicas with 2s staleness budget | AD-1's latency target outweighs AD-3 at current scale |

For each risk found — whether or not it came from a trade-off — record: category (`Technical`, `Schedule`, `Cost`,
`Security`, `Operational`), description, likelihood (`Low`/`Medium`/`High`), impact (`Low`/`Medium`/`High`), mitigation,
the related driver ID if any, and status (`Open`, `Mitigated`, `Accepted`). Write to `session.json`'s top-level
`riskRegister` (array), each entry with a stable ID (`RISK-1`, `RISK-2`, ...).

When a trade-off point creates a risk (e.g. choosing eventual consistency to satisfy a latency driver creates a
staleness risk), record the risk's ID (s) in that trade-off entry's `relatedRisks` field — this is the link back from
the trade-off that caused the risk to the risk itself, distinct from a risk's own `relatedDriver` field (which links a
risk forward to the driver it threatens). A risk with no originating trade-off simply omits `relatedRisks` on any
trade-off entry.

**Risk Register format**:

| ID     | Category  | Description                                                               | Likelihood | Impact | Mitigation                                                                 | Related driver | Status |
|--------|-----------|---------------------------------------------------------------------------|------------|--------|----------------------------------------------------------------------------|----------------|--------|
| RISK-1 | Technical | Read-replica lag under peak write load may exceed the 2s staleness budget | Medium     | Medium | Monitor replica lag; alert and failover to primary reads if lag exceeds 2s | AD-1           | Open   |

Both `tradeoffAnalysis` and `riskRegister` are written at the same time as `stage5` (see
`references/session-schema.md`). Neither needs to be large — a small monolith with few competing drivers may honestly
have one or two trade-off entries and two or three risks; do not pad the lists to look thorough. A genuinely simple
system with no real tension between drivers should say so explicitly rather than inventing a trade-off.

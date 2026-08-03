# Cost Estimation Guide

Use this guide at the end of Stage 5, immediately after the Trade-off and Risk Analysis pass and before Stage 5 is
confirmed. It turns the confirmed technology stack (Stage 5) and the capacity numbers (Stage 4) into a concrete
monthly/annual infrastructure cost breakdown — a per-component figure, not just a tier name — so budget is a checked
number in the document, not only a Stage 3 constraint nobody re-verified against the actual stack chosen.

## Why this matters

A stack recommendation that never turns into a dollar figure leaves Stage 3's budget constraint unfalsifiable — "AWS ECS
Fargate" and "a self-managed Kubernetes cluster" can both sound reasonable in prose while differing by 5–10× in monthly
spend. Naming the actual figure, per component, is what lets the user catch a budget mismatch before implementation
rather than after the first invoice.

## Method

**1. Enumerate cost components** from the confirmed Stage 5 stack. Skip any row with no corresponding Stage 5 decision —
this list is a menu, not a mandatory checklist:

- Compute (application servers, containers, serverless invocations)
- Database (primary instance/cluster tier, storage, read replicas, backups)
- Cache / in-memory store (Redis, Memcached)
- Object storage (S3-equivalent, plus egress)
- CDN / bandwidth
- Message queue / event streaming
- Observability (logging aggregator, metrics/dashboards, tracing backend — from Stage 5 item 8)
- Third-party metered APIs named in Stages 1–4 (email, SMS, payment gateway fees, LLM inference, geocoding)
- Domain/TLS certificates
- CI/CD compute minutes (from Stage 6c, once confirmed — this section may run before 6c; revisit and add this row once
  6c is confirmed, per `design/SKILL.md` Stage 6c)

**2. Size each component from Stage 4's numbers.** Apply the same **number discipline** Stage 4 itself uses (per
`design/SKILL.md` Stage 4): every size figure must originate from the confirmed capacity numbers or be an explicitly
derived, arithmetic-shown estimate from them — concurrent users, TPS, data volume, growth projection, geography. Never
size a tier from a database/infra performance benchmark recalled from memory (e.g. "this instance size handles 10,000
TPS") — that figure isn't grounded in this project's actual usage. Example: "50GB initial data volume, growing ~5GB/mo
per Stage 4 → a 100GB provisioned-storage tier covers ~10 months before the next resize."

**3. Price each sized component.** This is the same discipline Stage 5's "Version grounding" rule already applies to
technology versions, applied here to prices instead:

- **If WebSearch is available**: search for the confirmed cloud provider's current list price for the specific
  service/tier/region named in Stage 5 (e.g. "AWS RDS db.t3.medium us-east-1 pricing 2026", "DigitalOcean App Platform
  pricing"). Cite the figure with the source and the date it was checked — list prices change and a stale citation with
  no date is indistinguishable from a guess.
- **If WebSearch is unavailable**, or a search returns nothing usable: write the figure as a reasoned estimate and label
  it **"estimate — verify at implementation time"** — the identical phrase Stage 5 uses for an unverifiable version
  number, for the identical reason: a confident-sounding but stale number is more expensive to correct later than an
  honest placeholder.

Never blend the two silently in one table — the **Source** column (format below) states which discipline produced each
row, so the reader knows which figures to re-check before committing budget.

**4. Roll up and check sensitivity.** Sum to a **Monthly total** and **Annual total** (monthly × 12, noting any annual
prepay discount separately if named). Then add one sentence per component that does not scale linearly with usage — a
tier ceiling that forces a step-change (e.g. single-AZ → Multi-AZ RDS once availability requirements tighten, or a
serverless-invocation cost that turns cheaper-then-suddenly-more-expensive past a specific request volume) — so the
estimate is legible at both current scale and roughly 10× current scale, mirroring how Stage 4 already labels its own
numbers "current" vs. "growth projection."

**5. Reconcile against Stage 3's budget.** If Stage 3 recorded a budget ceiling, state explicitly whether the rolled-up
total fits under it. A mismatch is a finding to surface to the user now, before Stage 6, not a silent gap — the same
transparency `architecturalDrivers`/`riskRegister` already apply to other tensions. Record a mismatch as a
`riskRegister`
entry (category `Cost`) if the user chooses to proceed anyway rather than revise the stack.

## Format

**Cost Breakdown table** (one row per component from step 1):

| Component | Service / Tier                            | Monthly Cost | Sizing Basis                       | Source                                   |
|-----------|-------------------------------------------|--------------|------------------------------------|------------------------------------------|
| Database  | AWS RDS PostgreSQL db.t3.medium, Multi-AZ | $140         | 50GB data, ~200 TPS peak (Stage 4) | WebSearch verified 29-Jul-2026           |
| Compute   | ECS Fargate, 2 tasks × 1 vCPU/2GB         | $60          | 500 concurrent users (Stage 4)     | estimate — verify at implementation time |

Followed by:

- **Monthly total**, **Annual total**
- **Scale sensitivity** — one line per component flagged in step 4
- **Budget reconciliation** — one line per step 5

## Where this fits

Write the confirmed breakdown to `session.json`'s `stage5.costEstimate` at the same time as `stage5` (see
`references/session-schema.md`) — same two-writer pattern as `stage5.tradeoffAnalysis`, with `review/SKILL.md` step 4b
as the authorized second writer when a revision changes the technology stack or the capacity plan. It is embedded in the
architecture document's **Cost Estimation** section (`references/document-template.md`).

## Skip condition

There is no legitimate "skip Stage 5 cost estimation" case the way Stage 6b/6c can be skipped for a
deployment-target-free project — even a library or CLI tool has a cost floor (CI minutes, a package registry, at minimum
"$0 — no hosting required"). For a genuinely zero-infrastructure-cost project, state that explicitly as the Cost
Breakdown table's only row rather than omitting the section.

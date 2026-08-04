# Architecture Document Body Template

The section order and content for the architecture document saved by `design/SKILL.md` Step 11, and revised by
`review/SKILL.md` step 4f, which follows the same structure.

1. **Project Overview** — name and purpose. Date and version are already recorded once in the metadata table (F1–F3 in
   `document-review-checklist.md`) — do not restate them here as separate prose values that could drift out of sync with
   that table.
2. **Core Features** — a concise, scannable bullet list of the system's primary user-facing capabilities: one line per
   feature (feature name + one-sentence description), derived from the same Stage 2 functional requirements
   `design/SKILL.md` Stage 6d's "Core feature coverage requirement" already uses to decide which features get a
   dedicated sequence diagram. Every feature listed here must have a corresponding dedicated sequence diagram in section
   7 (Architecture Diagrams) — name that diagram's title next to each bullet (e.g. "Place order — see *Order Placement
   Sequence*") so a reader can jump straight from the feature list to its detailed flow. This is a summary index, not a
   restatement of section 3's full requirements prose — keep each bullet to one line; a minor CRUD sub-step of a feature
   already listed does not get its own bullet, the same grouping rule Stage 6d applies to diagram coverage. Do not list
   a feature with no corresponding requirement in `stage2` — this section only summarizes confirmed functional
   requirements, never invents a capability.
3. **Requirements Summary** — functional and non-functional requirements from stages 1–2, including the Quality
   Attribute Scenarios table and the ranked Architectural Drivers list (`stage2.qualityAttributeScenarios` and
   `architecturalDrivers`) — see `quality-driven-design-guide.md` — plus a **Domain Edge Cases** sub-list (category,
   question, answer) from `stage2.domainEdgeCases`, when present, per `domain-edge-cases-guide.md`. This is elaboration
   on the requirements above, not a separate numbered section — an answer recorded as "out of scope" belongs here just
   as much as one that expanded a requirement, since the point is making the boundary of what was actually considered
   visible, not only the parts that became in-scope features.
4. **Constraints and Feasibility** — from stage 3
5. **Capacity Planning** — from stage 4 with numeric estimates
6. **Technology Decisions** — the eleven items from `design/SKILL.md` Stage 5, in that order: architecture pattern,
   backend language/framework, frontend, database engine (s), infrastructure provider, supporting services,
   authentication approach, observability strategy, disaster recovery, error handling/resilience strategy (retry policy,
   circuit breaker, timeout budgets, graceful degradation), and rate-limiting strategy (algorithm, enforcement layer,
   per-tier limits, distributed store if horizontally scaled) — with justifications from stages 1–4, plus the
   architectural driver ID (s) each item satisfies when one applies. Immediately after an item's justification, if
   `session.json`'s `stage5.alternativesConsidered` has an entry for that item (per `adr-guide.md`'s "Which decisions
   get an ADR" criteria — not every item qualifies), embed that entry's Alternatives Considered table verbatim (see
   `critical-thinking-guide.md`'s "Alternatives Considered format") — never re-derive or paraphrase it from the
   justification prose beside it, the same verbatim-copy discipline section 8's ERD block already follows. An item with
   no matching entry has no table here; that is expected, not a gap, for an undriven standard-choice pick.
7. **Architecture Diagrams** — every created diagram with: a heading, a paragraph description, then the mermaid code
   block. For the ERD, include the index list table immediately after the mermaid block.
8. **Database Design** — the full output from the database-designer agent per its "Output format" (engine
   recommendation, schema, ERD explanation, index plan, transaction and concurrency strategy for any high-contention
   entity — per `references/transaction-guide.md` — when present, connection config, migration strategy), or
   database-fixer's corrected version if a fixer cycle ran — never the pre-fix original once a fix has been applied
9. **Infrastructure as Code** — IaC tool and justification, state backend config, module breakdown table (module name,
   what it provisions, environment-specific sizing), environment strategy, drift detection approach. Follow
   `iac-guide.md` section 6 for the exact format.
10. **CI/CD Pipeline** — platform and justification, pipeline stages table (stage, trigger, tool, gate), branching
    strategy, environment promotion rules, secret injection approach, artifact management. Follow `cicd-guide.md`
    section 7 for the exact format.
11. **Low-Level Design** — API contracts, business rules, DTOs (complex/shared only), inter-service contracts
    (microservices/event-driven only), and error catalog. Follow the section order and formatting from `lld-guide.md`.
12. **Decentralized Architecture Considerations** (only when the Web3 track was active — see `web3-guide.md`) — the
    confirmed answers to `web3-guide.md`'s eight invariant dimensions (see that file for the canonical list). Every
    network-specific fact must appear as either a confirmed, sourced value or a `<VERIFY>` placeholder — never asserted
    from memory. Omit this section entirely when `session.json` has no `web3` key.
13. **Offline-First Considerations** (only when the offline-first track was active — see `offline-first-guide.md`) — the
    confirmed local-storage choice, sync architecture (outbox pattern, sync API shape), conflict-resolution strategy
    (including how divergent `updated_at` values are handled), and delete/tombstone handling (see that guide's section
    3, including section 3f) from `session.json`'s `offlineFirst` key, plus the pre-deployment verification checklist
    from that guide's section 6. Omit this section entirely when `session.json` has no `offlineFirst` key.
14. **Domain Model (DDD)** (required — every project runs this step, see `ddd-guide.md`) — the bounded contexts, their
    aggregates (root entity, member entities, invariants), and ubiquitous language from `session.json`'s `domainModel`
    key, plus a table of the confirmed relationships between contexts (integration pattern, direction) from
    `domainModel.relationships` when 2 or more bounded contexts exist. A small system may legitimately describe a single
    bounded context with one or two aggregates — state that explicitly rather than treating it as a gap. The Context Map
    diagram itself (when applicable) belongs in section 7 with the other diagrams, not duplicated here — this section
    covers the underlying decisions in prose/table form.
15. **Trade-off and Risk Analysis** (required — see `quality-driven-design-guide.md`) — the ATAM-style trade-off table
    (ID, drivers in tension, trade-off point, sensitivity point, decision made, rationale) from `session.json`'s
    `stage5.tradeoffAnalysis`, and the risk register table (ID, category, description, likelihood, impact, mitigation,
    related driver, status) from `riskRegister` — the exact column sets given in `quality-driven-design-guide.md`'s
    "Trade-off Analysis format" and "Risk Register format". `related driver` is blank for a risk register entry with no
    corresponding `architecturalDrivers` entry (`relatedDriver` is optional in the schema) — a blank cell there is
    valid, not a content gap. A simple system with few competing drivers may honestly have only a small number of
    entries in each — do not pad the lists to look thorough.
16. **Cost Estimation** (required — see `cost-estimation-guide.md`) — the Cost Breakdown table (component, service/tier,
    monthly cost, sizing basis, source) from `session.json`'s `stage5.costEstimate.breakdown`, followed by the monthly
    total, annual total, scale-sensitivity notes, and budget reconciliation from that same key's remaining fields. Every
    row's Source column must read either a WebSearch-verified citation with a date, or the literal **"estimate — verify
    at implementation time"** — never a bare number with no source. A genuinely zero-cost project (a library or CLI tool
    with no hosting need) states that explicitly as the table's only row.
17. **Test Strategy** (required — see `test-strategy-guide.md`) — the test pyramid table, the load/performance testing
    targets and tool selection, the resilience/chaos testing scenarios (omitted only for a system with no external
    dependencies, per `resilience-guide.md`'s own skip condition), the security testing checklist, and the UAT
    Given/When/Then table, from `session.json`'s `testStrategy` key. State explicitly when a sub-section is empty per
    its own skip condition (e.g. no resilience scenarios for a dependency-free monolith) rather than omitting the
    heading.
18. **Architecture Decision Records** (required — see `adr-guide.md`) — a pointer table only, never a duplicate of each
    ADR's own Context/Decision/Consequences prose:

    ```markdown
    | ID       | Title                          | Status                | File |
    |----------|---------------------------------|------------------------|------|
    | ADR-0001 | Database engine selection      | Accepted               | `docs/architecture-designer/adr/0001-database-engine-selection.md` |
    ```

    Populate from `session.json`'s top-level `adrs` array. A superseded ADR still appears in this table with its actual
    `Superseded by ADR-{NNNN}` status — never dropped from the list once generated.

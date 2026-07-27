# Architecture Document Body Template

The section order and content for the architecture document saved by `design/SKILL.md` Step 11, and revised by
`review/SKILL.md` step 4f, which follows the same structure.

1. **Project Overview** — name and purpose. Date and version are already recorded once in the metadata table (F1–F3 in
   `document-review-checklist.md`) — do not restate them here as separate prose values that could drift out of sync with
   that table.
2. **Requirements Summary** — functional and non-functional requirements from stages 1–2, including the Quality
   Attribute Scenarios table and the ranked Architectural Drivers list (`stage2.qualityAttributeScenarios` and
   `architecturalDrivers`) — see `quality-driven-design-guide.md`
3. **Constraints and Feasibility** — from stage 3
4. **Capacity Planning** — from stage 4 with numeric estimates
5. **Technology Decisions** — the eleven items from `design/SKILL.md` Stage 5, in that order: architecture pattern,
   backend language/framework, frontend, database engine (s), infrastructure provider, supporting services,
   authentication approach, observability strategy, disaster recovery, error handling/resilience strategy (retry policy,
   circuit breaker, timeout budgets, graceful degradation), and rate-limiting strategy (algorithm, enforcement layer,
   per-tier limits, distributed store if horizontally scaled) — with justifications from stages 1–4, plus the
   architectural driver ID (s) each item satisfies when one applies
6. **Architecture Diagrams** — every created diagram with: a heading, a paragraph description, then the mermaid code
   block. For the ERD, include the index list table immediately after the mermaid block.
7. **Database Design** — the full output from the database-designer agent (schema, ERD explanation, index plan,
   connection config, migration strategy), or database-fixer's corrected version if a fixer cycle ran — never the
   pre-fix original once a fix has been applied
8. **Infrastructure as Code** — IaC tool and justification, state backend config, module breakdown table (module name,
   what it provisions, environment-specific sizing), environment strategy, drift detection approach. Follow
   `iac-guide.md` section 6 for the exact format.
9. **CI/CD Pipeline** — platform and justification, pipeline stages table (stage, trigger, tool, gate), branching
   strategy, environment promotion rules, secret injection approach, artifact management. Follow `cicd-guide.md` section
   7 for the exact format.
10. **Low-Level Design** — API contracts, business rules, DTOs (complex/shared only), inter-service contracts
    (microservices/event-driven only), and error catalog. Follow the section order and formatting from `lld-guide.md`.
11. **Decentralized Architecture Considerations** (only when the Web3 track was active — see `web3-guide.md`) — the
    confirmed answers to `web3-guide.md`'s eight invariant dimensions (see that file for the canonical list). Every
    network-specific fact must appear as either a confirmed, sourced value or a `<VERIFY>` placeholder — never asserted
    from memory. Omit this section entirely when `session.json` has no `web3` key.
12. **Offline-First Considerations** (only when the offline-first track was active — see `offline-first-guide.md`) — the
    confirmed local-storage choice, sync architecture (outbox pattern, sync API shape), and conflict-resolution strategy
    (including how divergent `updated_at` values are handled — see that guide's section 3) from `session.json`'s
    `offlineFirst` key, plus the pre-deployment verification checklist from that guide's section 6. Omit this section
    entirely when `session.json` has no `offlineFirst` key.
13. **Domain Model (DDD)** (required — every project runs this step, see `ddd-guide.md`) — the bounded contexts, their
    aggregates (root entity, member entities, invariants), and ubiquitous language from `session.json`'s `domainModel`
    key, plus a table of the confirmed relationships between contexts (integration pattern, direction) from
    `domainModel.relationships` when 2 or more bounded contexts exist. A small system may legitimately describe a single
    bounded context with one or two aggregates — state that explicitly rather than treating it as a gap. The Context Map
    diagram itself (when applicable) belongs in section 6 with the other diagrams, not duplicated here — this section
    covers the underlying decisions in prose/table form.
14. **Trade-off and Risk Analysis** (required — see `quality-driven-design-guide.md`) — the ATAM-style trade-off table
    (ID, drivers in tension, trade-off point, sensitivity point, decision made, rationale) from `session.json`'s
    `stage5.tradeoffAnalysis`, and the risk register table (ID, category, description, likelihood, impact, mitigation,
    related driver, status) from `riskRegister` — the exact column sets given in `quality-driven-design-guide.md`'s
    "Trade-off Analysis format" and "Risk Register format". `related driver` is blank for a risk register entry with no
    corresponding `architecturalDrivers` entry (`relatedDriver` is optional in the schema) — a blank cell there is
    valid, not a content gap. A simple system with few competing drivers may honestly have only a small number of
    entries in each — do not pad the lists to look thorough.

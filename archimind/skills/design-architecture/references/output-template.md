# Output Document Template

<!-- Save to: docs/archimind/{timestamp_ms}_{topic}-architecture-design.md -->

Use this template as a scaffold when generating the design file. Replace all placeholder text. Do not omit any section. Save to `docs/archimind/` in the user's project root.

---

```markdown
# Architecture Design: {Project Name}

<!-- After user confirms their choice, fill in these two lines: -->
<!-- **Selected:** Option N — {Risk Level}: {Architecture Name} -->
<!-- **Decision date:** {ISO date} -->

**Generated:** {ISO date}
**Requested by:** User  
**Summary:** {One-sentence description of the system}

## Project Overview

{2–4 sentences describing what the system does, who uses it, and its key characteristics (scale, domain, integrations).}

## Requirements Gathered

- **Core features:** {bullet list}
- **Scale target:** {e.g., ~10,000 DAU, ~1M records}
- **Team size:** {e.g., 3 engineers}
- **Key constraints:** {deadline, compliance, existing stack}
- **Data characteristics:** {structured / semi-structured / time-series / graph / search-heavy?}
- **Critical queries / operations:** {e.g., real-time search, large file uploads, heavy aggregations}

---

## Option 1: Low Risk — {Architecture Name}

### Overview

{One paragraph describing the core approach and why it is appropriate for the conservative tier.}

### Architecture Diagram

```mermaid
flowchart TD
  ...
```

### Key Components

- **{Component}**: {One-line description}
- **{Component}**: {One-line description}

### Technology Stack

| Layer           | Recommended       | Alternatives      | Reason                                   |
|-----------------|-------------------|-------------------|------------------------------------------|
| Language        |                   |                   |                                          |
| Backend         |                   |                   |                                          |
| Frontend        |                   |                   |                                          |
| Primary DB      |                   |                   |                                          |
| Cache           |                   |                   |                                          |
| Search          | N/A               | —                 | Not needed at this scale                 |
| Analytics DB    | N/A               | —                 | Not needed at this scale                 |
| Infra/Deploy    |                   |                   |                                          |
| Observability   |                   |                   |                                          |

### Data Layer Design

- **Primary store**: {Engine} — {Category: relational / document / key-value / ...}. {Why this category for this project. What query patterns drive this choice.}
- **Cache**: {Redis/Memcached/none} — {What is cached, why}
- **Search**: {Engine or "Not needed — {reason}"}
- **Analytics**: {Engine or "Not needed — {reason}"}
- **Why NOT alternatives**: {e.g., MongoDB not chosen because schema is stable and joins are frequent; ClickHouse not needed at current scale}

### Observability Strategy

- **Instrumentation**: {OpenTelemetry SDK — specify language/framework; auto-instrumentation: yes/no}
- **Log management**: {Loki + Promtail / ELK / ClickHouse} — {why this choice; log shipping agent}
- **Metrics**: {Prometheus + Grafana / VictoriaMetrics} — {key dashboards: RED per service}
- **Distributed tracing**: {Grafana Tempo / Jaeger / N/A at this scale} — {sampling strategy}
- **Unified backend**: {Grafana / SigNoz / Uptrace / Datadog} — {self-hosted vs. managed justification, cost estimate}
- **Alerting**: {Alertmanager / Grafana Alerting / PagerDuty} — {minimum: error rate > 1% → Slack}

### Technology Decision Rationale

**{Backend Framework}**
- *Why chosen*: {Specific technical reason for this project}
- *Better than alternatives*: {Head-to-head for this use case}
- *Required skills*: {What team needs to operate}
- *Ecosystem*: {Maturity, community, longevity}

**{Primary Database}**
- *Why chosen*: {Specific technical reason}
- *Better than alternatives*: {Comparison for this use case}
- *Required skills*: {DBA knowledge needed}
- *Ecosystem*: {Maturity, managed options}

{Repeat for each major technology choice}

### Future Impact

| Timeframe | Impact                                                                      |
|-----------|-----------------------------------------------------------------------------|
| 6 months  | {Team ramp-up, what works great, first pain points}                         |
| 1 year    | {First scaling or maintenance wall}                                         |
| 3 years   | {Total cost of ownership, evolution needed, hiring story}                   |

- **Scalability ceiling**: {What breaks first at 10× load?}
- **Operational overhead**: {Ongoing maintenance burden}
- **Reversibility**: {How hard to migrate away from this stack?}
- **Vendor lock-in**: {Which components create lock-in, escape hatch}

### Risks & Mitigations

| Risk                     | Likelihood | Impact | Mitigation                      |
|--------------------------|------------|--------|---------------------------------|
|                          | Low        | Low    |                                 |
|                          | Medium     | Medium |                                 |

### When to Choose This Option

- {Bullet 1: team/timeline scenario}
- {Bullet 2: scale/budget scenario}
- {Bullet 3: specific use case}

---

## Option 2: Medium Risk — {Architecture Name}

### Overview

{One paragraph for the balanced tier.}

### Architecture Diagram

```mermaid
flowchart TD
  ...
```

### Key Components

- **{Component}**: {One-line description}

### Technology Stack

| Layer           | Recommended       | Alternatives      | Reason                                   |
|-----------------|-------------------|-------------------|------------------------------------------|
| Language        |                   |                   |                                          |
| Backend         |                   |                   |                                          |
| Frontend        |                   |                   |                                          |
| Primary DB      |                   |                   |                                          |
| Cache           |                   |                   |                                          |
| Search          |                   |                   |                                          |
| Analytics DB    |                   |                   |                                          |
| Message Queue   |                   |                   |                                          |
| Infra/Deploy    |                   |                   |                                          |

### Data Layer Design

- **Primary store**: {Engine + category + reasoning}
- **Cache**: {Redis or other — what's cached}
- **Search**: {Engine if added — why added at this risk tier}
- **Analytics**: {Engine if added}
- **Why NOT alternatives**: {Ruled-out options}

### Observability Strategy

- **Instrumentation**: {OpenTelemetry SDK — language + auto-instrumentation}
- **Log management**: {Loki / ELK — agent, why}
- **Metrics**: {Prometheus + Grafana / VictoriaMetrics — key dashboards}
- **Distributed tracing**: {Tempo / Jaeger — sampling strategy}
- **Unified backend**: {SigNoz / Grafana Stack / Datadog — self-hosted vs. managed}
- **Alerting**: {Alertmanager / Grafana — minimum error rate alert}

### Technology Decision Rationale

**{Technology}**
- *Why chosen*: ...
- *Better than alternatives*: ...
- *Required skills*: ...
- *Ecosystem*: ...

{Repeat for each major technology}

### Future Impact

| Timeframe | Impact                                                                      |
|-----------|-----------------------------------------------------------------------------|
| 6 months  | {Impact}                                                                    |
| 1 year    | {Impact}                                                                    |
| 3 years   | {Impact}                                                                    |

- **Scalability ceiling**: ...
- **Operational overhead**: ...
- **Reversibility**: ...
- **Vendor lock-in**: ...

### Risks & Mitigations

| Risk                     | Likelihood | Impact | Mitigation                      |
|--------------------------|------------|--------|---------------------------------|

### When to Choose This Option

- {Bullet 1}
- {Bullet 2}

---

## Option 3: High Risk — {Architecture Name}

### Overview

{One paragraph for the ambitious tier.}

### Architecture Diagram

```mermaid
flowchart TD
  ...
```

### Key Components

- **{Component}**: {One-line description}

### Technology Stack

| Layer              | Recommended       | Alternatives      | Reason                                   |
|--------------------|-------------------|-------------------|------------------------------------------|
| Language           |                   |                   |                                          |
| Backend            |                   |                   |                                          |
| Frontend           |                   |                   |                                          |
| Primary DB         |                   |                   |                                          |
| Cache              |                   |                   |                                          |
| Search             |                   |                   |                                          |
| Analytics DB       |                   |                   |                                          |
| Message Broker     |                   |                   |                                          |
| Service Mesh       |                   |                   |                                          |
| Observability      |                   |                   |                                          |
| Infra/Deploy       |                   |                   |                                          |

### Data Layer Design

- **Primary store**: {Engine + category + reasoning}
- **Cache**: {Redis — scope and TTL strategy}
- **Search**: {Search engine — why needed at this scale}
- **Analytics**: {OLAP engine — why ClickHouse/BigQuery over a simpler approach}
- **Other stores**: {Graph, time-series, object storage if applicable}
- **Polyglot persistence rationale**: {Justify each additional DB — why the primary DB cannot handle this workload}
- **Why NOT alternatives**: {Ruled-out options}

### Observability Strategy

- **Instrumentation**: OpenTelemetry SDK + OTel Collector — {tail-based or head-based sampling, ratio}
- **Log management**: {Loki / ELK / ClickHouse — high-volume choice, log shipping agent}
- **Metrics**: {VictoriaMetrics / Mimir — long-term storage, multi-service dashboards, RED per service}
- **Distributed tracing**: {Jaeger / Tempo — full trace sampling strategy for microservices}
- **Unified backend**: {SigNoz / Grafana Stack / Datadog — full justification: self-hosted vs. managed, cost at scale}
- **Alerting**: {Alertmanager + PagerDuty / Grafana Alerting — multi-channel incident response}
- **Profiling** (optional): {Pyroscope / Parca for continuous CPU/memory profiling in production}

### Technology Decision Rationale

**{Technology}**
- *Why chosen*: ...
- *Better than alternatives*: ...
- *Required skills*: ...
- *Ecosystem*: ...

{Repeat for EVERY major technology in the high-risk stack — this tier requires the most justification}

### Future Impact

| Timeframe | Impact                                                                      |
|-----------|-----------------------------------------------------------------------------|
| 6 months  | {Impact — high upfront investment}                                          |
| 1 year    | {First distributed systems pain points}                                     |
| 3 years   | {ROI realized (or not), evolution needed}                                   |

- **Scalability ceiling**: {Near-infinite if designed correctly — what are the remaining limits?}
- **Operational overhead**: {High — what team/tooling is required?}
- **Reversibility**: {Low — outline the cost of unwinding this}
- **Vendor lock-in**: {Multiple vendors — document each dependency and its escape hatch}

### Risks & Mitigations

| Risk                     | Likelihood | Impact | Mitigation                      |
|--------------------------|------------|--------|---------------------------------|
|                          | High       | High   |                                 |

### When to Choose This Option

- {Bullet 1}
- {Bullet 2}

---

## Recommendation

{4–6 sentences stating which option is recommended, why, referencing actual requirements (team size, scale, data characteristics). Acknowledge the main trade-off of the recommended choice.}

<!-- After user selects an option, append below: -->

<!--
## Decision Notes

- **Chosen option:** Option N — {Risk Level}: {Architecture Name}
- **User-requested adjustments:** {if any, e.g., "swap MongoDB for PostgreSQL", "add Redis cache"}
- **Prioritized next steps:** {first implementation milestones}
- **Open questions:** {anything to revisit during implementation}
-->
```

Also, when the user picks an option, append ` ✅ SELECTED` to that option's heading (e.g., `## Option 2: Medium Risk — Modular Monolith ✅ SELECTED`). The static viewer reads this marker to highlight the selected tab.

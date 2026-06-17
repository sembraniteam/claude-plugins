# Output Document Template

> **READ-ONLY REFERENCE — NEVER WRITE TO THIS FILE.**
> Output destinations:
> - Viewer draft → `/tmp/archimind-viewer/content.md`
> - Final saved doc → `docs/archimind/architecture/{timestamp_ms}-{topic}.md`
>
> Use this file only to read the scaffold structure. All writes go to the destinations above.

Use this template as a scaffold when generating the design file. Replace all placeholder text. Do not omit any section.

---

```markdown
# Architecture Design: {Project Name}

**Generated:** {ISO date}
**Summary:** {One-sentence description of the system}

<!-- Fill in after user selects: -->
<!-- **Selected:** Option N — {Tier}: {Architecture Name} -->
<!-- **Decision date:** {ISO date} -->

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

## Architecture Diagram

### Option 1: Lean — {Architecture Name}

{One paragraph describing the core approach and why it is appropriate for the conservative tier.}

#### Infrastructure Layout

```mermaid
architecture-beta
  group internet(cloud)[Public Zone]
    service client(internet)[Client Apps] in internet

  group api(server)[API Layer]
    service gateway(server)[API Gateway] in api

  group data(database)[Data Layer]
    service db(database)[Primary DB] in data
    service cache(database)[Cache] in data

  client:R --> L:gateway
  gateway:B --> T:db
  gateway:B --> T:cache
```

> {1–2 sentences: describe the zones, traffic entry point, and key data stores shown in this diagram.}

#### Request Flow

```mermaid
sequenceDiagram
  participant Client
  participant API
  participant DB
  Client->>API: {Primary request, e.g. POST /orders}
  API->>DB: {Query or write}
  DB-->>API: {Result}
  API-->>Client: {Response}
```

> {1–2 sentences: describe the happy-path request traced here and any notable steps such as cache checks or async branches.}

#### Logical Architecture

```mermaid
flowchart TD
  subgraph "Presentation"
    Handler[HTTP Handlers]
    MW[Auth Middleware]
  end
  subgraph "Application"
    Svc[Application Services]
  end
  subgraph "Domain"
    Entity[Domain Entities]
    Iface[Repository Interfaces]
  end
  subgraph "Infrastructure"
    Repo[Repo Implementations]
    DB[(Primary DB)]
    Cache[(Cache)]
  end
  MW --> Handler
  Handler --> Svc
  Svc --> Entity
  Svc --> Iface
  Iface --> Repo
  Repo --> DB
  Repo --> Cache
```

> {1–2 sentences: describe the layer structure — how the presentation layer delegates to application services, which call domain logic, which in turn use infrastructure implementations. Name the actual stores and frameworks used.}

#### Key Components

- **{Component}**: {One-line description}
- **{Component}**: {One-line description}

#### Technology Stack

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

#### Data Layer Design

- **Transactional store**: {Engine} — {category: relational / document / …}. {Why this category; what query patterns drive this choice.}
- **Cache**: {Redis / Memcached / none} — {what is cached, TTL strategy}
- **Search**: {Engine or "Not needed — {reason}"}
- **Analytics / OLAP**: {Engine or "Not needed — {reason}"}
- **Message queue**: {Engine or "Not needed — {reason}"}
- **Object storage**: {see Object Storage section or "Not needed"}
- **Why NOT alternatives**: {e.g., MongoDB not chosen because schema is stable and joins are frequent}

#### Object Storage

<!-- Omit this section if user answered "None" for file/object storage needs -->

- **Solution**: {MinIO / AWS S3 / GCS / Cloudflare R2 / Azure Blob / self-hosted}
- **What is stored**: {user uploads / media / backups / static assets / data lake}
- **Bucket organization**: {e.g., one bucket per env, prefixed by user-id}
- **Access control**: {signed URLs / public CDN / private IAM}
- **Encryption**: {server-side / client-side / KMS}
- **Lifecycle management**: {expiry rules, tiering}
- **Self-hosted vs. managed trade-off**: {why this choice}

#### Observability Strategy

- **Instrumentation**: {OpenTelemetry SDK — language/framework; auto-instrumentation: yes/no}
- **Logs**: {Loki + Promtail / ELK / ClickHouse} — {why; log shipping agent}
- **Metrics**: {Prometheus + Grafana / VictoriaMetrics} — {key dashboards: RED per service}
- **Distributed tracing**: {Grafana Tempo / Jaeger / N/A at this scale} — {sampling strategy}
- **Unified backend**: {Grafana Stack / SigNoz / Uptrace / Datadog} — {self-hosted vs. managed justification}
- **Alerting**: {Alertmanager / Grafana Alerting / PagerDuty} — {minimum: error rate > 1% → Slack}

#### Technology Decision Rationale

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

#### Future Impact

| Timeframe | Impact                                                                      |
|-----------|-----------------------------------------------------------------------------|
| 6 months  | {Team ramp-up, what works great, first pain points}                         |
| 1 year    | {First scaling or maintenance wall}                                         |
| 3 years   | {Total cost of ownership, evolution needed, hiring story}                   |

- **Scalability ceiling**: {What breaks first at 10× load?}
- **Operational overhead**: {Ongoing maintenance burden}
- **Reversibility**: {How hard to migrate away from this stack?}
- **Vendor lock-in**: {Which components create lock-in, escape hatch}

#### Risks & Mitigations

| Risk                     | Likelihood | Impact | Mitigation                      |
|--------------------------|------------|--------|---------------------------------|
|                          | Low        | Low    |                                 |

#### When to Choose This Option

- {Bullet 1: team/timeline scenario}
- {Bullet 2: scale/budget scenario}
- {Bullet 3: specific use case}

---

### Option 2: Standard — {Architecture Name}

{One paragraph for the balanced tier.}

#### Infrastructure Layout

```mermaid
architecture-beta
  group internet(cloud)[Public Zone]
    service client(internet)[Client Apps] in internet

  group api(server)[API Layer]
    service gateway(server)[API Gateway] in api

  group data(database)[Data Layer]
    service db(database)[Primary DB] in data
    service cache(database)[Cache] in data
    service queue(server)[Message Queue] in data

  client:R --> L:gateway
  gateway:B --> T:db
  gateway:B --> T:cache
  gateway:R --> L:queue
```

> {1–2 sentences: describe the zones, traffic entry point, and key data stores shown in this diagram.}

#### Request Flow

```mermaid
sequenceDiagram
  participant Client
  participant API
  participant DB
  Client->>API: {Primary request}
  API->>DB: {Query or write}
  DB-->>API: {Result}
  API-->>Client: {Response}
```

> {1–2 sentences: describe the happy-path request traced here and any notable steps such as cache checks or async branches.}

#### Logical Architecture

```mermaid
flowchart LR
  subgraph "Domain A"
    SvcA[Service A]
    DBA[(Store A)]
  end
  subgraph "Domain B"
    SvcB[Service B]
    DBB[(Store B)]
  end
  subgraph "Shared Infrastructure"
    Queue[Message Queue]
    Cache[(Shared Cache)]
  end
  SvcA --- DBA
  SvcB --- DBB
  SvcA -->|REST| SvcB
  SvcA -->|publishes DomainEvent| Queue
  Queue -->|consumed by| SvcB
  SvcA -->|reads from| Cache
```

> {1–2 sentences: describe the bounded context ownership — which domain owns which store, how cross-domain calls happen (REST or async events), and which data is shared via cache or queue. Replace domain names with the actual business domains of the project.}

#### Key Components

- **{Component}**: {One-line description}

#### Technology Stack

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
| Observability   |                   |                   |                                          |

#### Data Layer Design

- **Transactional store**: {Engine + category + reasoning}
- **Cache**: {Redis — what's cached, TTL}
- **Search**: {Engine if added — why at this tier}
- **Analytics / OLAP**: {Engine if added}
- **Message queue**: {Engine if added}
- **Object storage**: {see Object Storage section or "Not needed"}
- **Why NOT alternatives**: {Ruled-out options}

#### Object Storage

<!-- Omit if not needed -->
- **Solution**: ...
- **What is stored**: ...
- **Access control**: ...
- **Lifecycle**: ...

#### Observability Strategy

- **Instrumentation**: {OTel SDK — language + auto-instrumentation}
- **Logs**: {Loki / ELK — agent, why}
- **Metrics**: {Prometheus + Grafana / VictoriaMetrics}
- **Distributed tracing**: {Tempo / Jaeger — sampling strategy}
- **Unified backend**: {SigNoz / Grafana Stack / Datadog}
- **Alerting**: {Alertmanager / Grafana}

#### Technology Decision Rationale

**{Technology}**
- *Why chosen*: ...
- *Better than alternatives*: ...
- *Required skills*: ...
- *Ecosystem*: ...

{Repeat for each major technology}

#### Future Impact

| Timeframe | Impact |
|-----------|--------|
| 6 months  |        |
| 1 year    |        |
| 3 years   |        |

- **Scalability ceiling**: ...
- **Operational overhead**: ...
- **Reversibility**: ...
- **Vendor lock-in**: ...

#### Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|

#### When to Choose This Option

- {Bullet 1}
- {Bullet 2}

---

### Option 3: Advanced — {Architecture Name}

{One paragraph for the ambitious tier.}

#### Infrastructure Layout

```mermaid
architecture-beta
  group internet(cloud)[Public Zone]
    service client(internet)[Client Apps] in internet
    service cdn(disk)[CDN] in internet

  group gateway(server)[API Gateway Layer]
    service gw(server)[API Gateway] in gateway
    service mesh(server)[Service Mesh] in gateway

  group services(server)[Microservices]
    service svcA(server)[Service A] in services
    service svcB(server)[Service B] in services
    service worker(server)[Worker] in services

  group data(database)[Data Layer]
    service db(database)[Primary DB] in data
    service cache(database)[Cache] in data
    service queue(server)[Message Broker] in data
    service storage(disk)[Object Storage] in data

  client:R --> L:gw
  cdn:B --> T:client
  gw:R --> L:svcA
  gw:R --> L:svcB
  svcA:B --> T:db
  svcA:B --> T:cache
  svcA:R --> L:queue
  queue:R --> L:worker
```

> {1–2 sentences: describe the zones, traffic entry point, and key data stores shown in this diagram.}

#### Request Flow

```mermaid
sequenceDiagram
  participant Client
  participant Gateway
  participant ServiceA
  participant ServiceB
  participant DB
  Client->>Gateway: {Primary request}
  Gateway->>ServiceA: {Route}
  ServiceA->>DB: {Query}
  DB-->>ServiceA: {Result}
  ServiceA->>ServiceB: {Async event or call}
  ServiceA-->>Gateway: {Response}
  Gateway-->>Client: {Response}
```

> {1–2 sentences: describe the happy-path request traced here and any notable steps such as cache checks or async branches.}

#### Logical Architecture

```mermaid
flowchart LR
  subgraph "Commerce"
    OrderSvc[Order Service]
    PaySvc[Payment Service]
  end
  subgraph "Broker"
    MQ[Message Broker]
  end
  subgraph "Platform"
    NotifySvc[Notification Service]
    AnalyticsSvc[Analytics Service]
  end
  OrderSvc -->|OrderCreated| MQ
  PaySvc -->|PaymentProcessed| MQ
  MQ -->|OrderCreated| PaySvc
  MQ -->|PaymentProcessed| NotifySvc
  MQ -->|OrderCreated, PaymentProcessed| AnalyticsSvc
```

> {1–2 sentences: describe the event/service mesh — which services are upstream publishers, which events flow through the broker, and which downstream services consume them. Replace service and event names with those of the actual project.}

#### Key Components

- **{Component}**: {One-line description}

#### Technology Stack

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
| Object Storage     |                   |                   |                                          |
| Observability      |                   |                   |                                          |
| Infra/Deploy       |                   |                   |                                          |

#### Data Layer Design

- **Transactional store**: {Engine + category + reasoning}
- **Cache**: {Redis — scope and TTL strategy}
- **Search**: {Engine — why needed at this scale}
- **Analytics / OLAP**: {ClickHouse / BigQuery — why over simpler approach}
- **Message queue / stream**: {Kafka / Pulsar — why at this scale}
- **Object storage**: {see Object Storage section}
- **Graph store**: {Neo4j / Neptune or "Not needed"}
- **Polyglot persistence rationale**: {justify each additional DB — why the primary DB cannot handle this workload}
- **Why NOT alternatives**: {Ruled-out options}

#### Object Storage

- **Solution**: {MinIO / RustFS / Ceph / AWS S3 / GCS}
- **What is stored**: ...
- **Bucket organization**: ...
- **Access control**: ...
- **Encryption**: ...
- **Lifecycle management**: ...
- **Replication strategy**: ...
- **Self-hosted vs. managed trade-off**: {total cost, ops complexity}

#### Observability Strategy

- **Instrumentation**: OTel SDK + OTel Collector — {tail-based or head-based sampling, ratio}
- **Logs**: {Loki / ELK / ClickHouse — high-volume choice, log shipping agent}
- **Metrics**: {VictoriaMetrics / Mimir — long-term storage, multiservice dashboards}
- **Distributed tracing**: {Jaeger / Tempo — full trace sampling for microservices}
- **Unified backend**: {SigNoz / Grafana Stack / Datadog — self-hosted vs. managed, cost at scale}
- **Alerting**: {Alertmanager + PagerDuty — multichannel incident response}
- **Profiling** (optional): {Pyroscope / Parca for continuous CPU/memory profiling}

#### Technology Decision Rationale

**{Technology}**
- *Why chosen*: ...
- *Better than alternatives*: ...
- *Required skills*: ...
- *Ecosystem*: ...

{Repeat for EVERY major technology — this tier requires the most justification}

#### Future Impact

| Timeframe | Impact                                  |
|-----------|-----------------------------------------|
| 6 months  | {High upfront investment}               |
| 1 year    | {First distributed systems pain points} |
| 3 years   | {ROI realized or not, evolution needed} |

- **Scalability ceiling**: {Near-infinite if designed correctly — remaining limits?}
- **Operational overhead**: {High — team/tooling required?}
- **Reversibility**: {Low — outline cost of unwinding}
- **Vendor lock-in**: {Multiple vendors — each dependency and escape hatch}

#### Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
|      | High       | High   |            |

#### When to Choose This Option

- {Bullet 1}
- {Bullet 2}

---

## Recommendation

{4–6 sentences stating which option is recommended and why, referencing actual requirements (team size, scale, data characteristics). Acknowledge the main trade-off.}

---

## ERD

```mermaid
erDiagram
  ENTITY_A {
    bigint id PK
    varchar name
    timestamptz created_at
  }
  ENTITY_B {
    bigint id PK
    bigint entity_a_id FK
    text value
  }
  ENTITY_A ||--o{ ENTITY_B : "has"
```

### Table Specifications

#### `{table_name}`

| Column     | Type        | Constraints             | Description     |
|------------|-------------|-------------------------|-----------------|
| id         | BIGSERIAL   | PRIMARY KEY             | Surrogate PK    |
| created_at | TIMESTAMPTZ | NOT NULL, DEFAULT now() | Creation time   |

**Indexes:**
| Name                 | Type   | Columns    | Reason                        |
|----------------------|--------|------------|-------------------------------|
| idx_{table}_{col}    | B-tree | {col}      | {query pattern this supports} |

---

## Revision

<!-- For fresh designs: leave Before/After empty or omit this section. -->
<!-- For architecture reviews: populate Before with current state, After with the selected redesign. -->

### Before

{Description of the current architecture (used in review workflows).}

```mermaid
flowchart TD
  ...
```

**Identified Issues:**
- {Issue 1}

### After

{Description of the proposed architecture after the user selects an option.}

```mermaid
flowchart TD
  ...
```

**Key Improvements:**
- {How identified issues are resolved}

---

## Decision Notes

<!-- Fill in after user selects an option -->
- **Chosen option:** Option N — {Tier}: {Architecture Name}
- **User-requested adjustments:** {if any}
- **Prioritized next steps:** {first implementation milestones}
- **Open questions:** {anything to revisit during implementation}

---

## Final Documentation

### Overview

{2–4 sentences: what the system does, who uses it, and its key characteristics (scale, domain, integrations).}

### Architecture Decision

**Chosen:** Option N — {Tier}: {Architecture Name}
**Reason:** {2–3 sentences on why this option was selected over the alternatives, referencing actual requirements.}

> See the selected `### Option N:` heading above for the full Infrastructure Layout, Request Flow, and Logical Architecture diagrams.

### Technology Stack

| Layer          | Technology | Reason |
|----------------|------------|--------|
| Language       |            |        |
| Backend        |            |        |
| Frontend       |            |        |
| Primary DB     |            |        |
| Cache          |            |        |
| Message Queue  |            |        |
| Infra / Deploy |            |        |
| Observability  |            |        |

### Data Architecture

{DB choices and rationale — why the primary DB was chosen, what workloads each store handles.}

#### ERD

```mermaid
erDiagram
  {Repeat the erDiagram from the ## ERD section for standalone readability}
```

#### Migration Strategy

- **Schema versioning tool**: {Flyway / Liquibase / Prisma Migrate / Alembic / etc.}
- **Rollback approach**: {migration-level rollback or feature-flag toggle}
- **Zero-downtime**: {expand-contract pattern if schema changes affect production}

### Observability

- **Logs**: {tool + shipping agent — e.g., Loki + Promtail}
- **Metrics**: {tool + key dashboards — e.g., Prometheus + Grafana, RED metrics per service}
- **Tracing**: {tool + sampling strategy — e.g., Tempo with 10% tail sampling}
- **Alerting**: {tool + minimum thresholds — e.g., error rate > 1% → Slack}

### Security

#### Application Security
- **Authentication**: {mechanism — e.g., JWT / OAuth2 / OIDC / session-based}
- **Authorization**: {model — e.g., RBAC, ABAC, policy-as-code}
- **Secrets management**: {Vault / AWS Secrets Manager / GCP Secret Manager — never env vars in code}
- **OWASP coverage**: {input validation, XSS protection, CSRF tokens, rate limiting, dependency scanning}

#### Database Connectivity Security
- **DB users**: Separate roles — `app_rw` (application), `app_ro` (analytics), `migrator` (schema changes only), `backup_user`; superuser never used from application code
- **Credential storage**: {Vault dynamic secrets / Secrets Manager} — credentials fetched at runtime, not hardcoded or committed to version control
- **Credential rotation**: {Dynamic short-lived (Vault DB engine) / static rotation every 90 days}; connection pool `maxLifetime` set below rotation interval
- **TLS enforcement**: `sslmode=verify-full` (PostgreSQL) / `REQUIRE SSL` (MySQL) / `requireTLS` (MongoDB) on all connections; plaintext connections rejected at DB level
- **Network isolation**: DB in private subnet; security groups restrict DB port to app-server security group only; no public IP on DB instance
- **Connection pooling**: {PgBouncer / HikariCP / other} with TLS on both client↔pooler and pooler↔DB sides; pool auth via `scram-sha-256`

#### Data Protection
- **Encryption at rest**: {DB-level tablespace encryption / cloud-managed (RDS, Cloud SQL)} + backup encryption (AES-256, key stored separately)
- **Sensitive column encryption**: {application-layer encryption via pgcrypto / Vault Transit for PII and PCI fields; or "N/A"}
- **Encryption in transit**: TLS 1.2+ enforced on all DB connections and internal service-to-service calls
- **SQL injection prevention**: Parameterized queries or ORM used throughout; no string-concatenated SQL; dynamic `ORDER BY` validated against allowlist

#### Audit & Compliance
- **Audit logging**: {pgaudit / MySQL Audit Plugin} for DDL and write events; application-level `security_audit_log` table for sensitive data access
- **Compliance requirements**: {OWASP Top 10 / SOC 2 / GDPR / HIPAA / PCI DSS — applicable controls and how the design satisfies them}
- **GDPR erasure**: {PII scrubbing strategy on soft-delete or explicit erasure request; or "N/A"}
- **PCI DSS**: {CVV/CVC never stored; cardholder data encrypted at column level; or "N/A"}

### Trade-offs & Next Steps

**Trade-offs accepted:**
- {Scalability ceiling: what breaks first at 10× load}
- {Operational overhead: ongoing burden}
- {Reversibility: cost of switching away from this stack}

**First implementation milestones:**
1. {Milestone 1 — e.g., scaffold service + CI/CD}
2. {Milestone 2 — e.g., core data model + auth}
3. {Milestone 3 — e.g., first production deployment}

**Open questions:**
- {Anything to revisit during implementation}
```

---

After the user selects an option:
1. Fill in the `**Selected:**` and `**Decision date:**` lines in the header
2. Populate the `## Revision / ### After` section with the chosen architecture diagram
3. Fill in `## Decision Notes`
4. Write the `## Final Documentation` sections

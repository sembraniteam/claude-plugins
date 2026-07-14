# Technology Stack Recommendations

Concrete stack recommendations organized by architecture pattern, scale, and team context. Use this as a starting point for Stage 5 recommendations — always justify the final choice against the user's specific requirements, not just this guide.

## Contents

1. [Quick Decision Matrix](#quick-decision-matrix)
2. [Modular Monolith (Recommended Default)](#modular-monolith-recommended-default-for-most-projects)
   - [Node.js / TypeScript Stack](#nodejs--typescript-stack)
   - [Python Stack](#python-stack)
   - [Go Stack](#go-stack)
   - [Java / JVM Stack](#java--jvm-stack)
3. [Microservices Stack](#microservices-stack)
   - [Core Platform](#core-platform)
   - [Service Communication](#service-communication)
   - [Per-Service Stack](#per-service-stack)
   - [Observability](#observability-required-for-microservices)
4. [Serverless Stack](#serverless-stack)
   - [AWS Serverless](#aws-serverless)
   - [GCP Serverless](#gcp-serverless)
   - [Azure Serverless](#azure-serverless)
5. [Database Selection Guide](#database-selection-guide)
6. [Infrastructure by Cloud Provider](#infrastructure-by-cloud-provider)
   - [AWS](#aws-most-feature-rich-highest-ops-overhead)
   - [GCP](#gcp-best-for-mldata-workloads-strong-kubernetes)
   - [Azure](#azure-enterprisemicrosoft-ecosystem)
   - [Self-hosted / On-premise](#self-hosted--on-premise)
7. [Authentication and Authorization](#authentication-and-authorization)
8. [Frontend](#frontend)
9. [How to Justify Recommendations](#how-to-justify-recommendations-in-the-architecture-document)

---

## Quick Decision Matrix

Before recommending a stack, answer these four questions from the requirements you've gathered:

| Question    | Small / Startup | Medium / Growth | Large / Enterprise        |
|-------------|-----------------|-----------------|---------------------------|
| Team size   | 1–5 devs        | 5–25 devs       | 25+ devs / multiple teams |
| Peak TPS    | < 100           | 100–2,000       | > 2,000                   |
| Data volume | < 100 GB        | 100 GB – 5 TB   | > 5 TB                    |
| Budget      | Minimize cost   | Moderate        | Cost-optimized at scale   |

**Architecture pattern rule of thumb**:
- 1–5 devs, < 500 TPS → **Modular monolith** (default)
- 5–20 devs, need independent deploy cadence → **Microservices** (only if teams are ready for the ops overhead)
- Sporadic/event-driven workload, no persistent connections → **Serverless**
- Data-pipeline centric, batch processing → **Event-driven / streaming**

---

## Modular Monolith (Recommended Default for Most Projects)

### Node.js / TypeScript Stack
```
Backend:     Node.js 22 + Fastify 5 (or Express 5 if team prefers)
             TypeScript 5 + strict mode
ORM:         Prisma 6 (great DX, auto-migrations) or Drizzle ORM (lighter, closer to SQL)
Validation:  Zod (runtime + TypeScript type inference)
Auth:        jose (JWT) or Lucia (session-based)
Primary DB:  PostgreSQL 16 (managed: RDS, Cloud SQL, Supabase, Neon)
Cache:       Redis 7 (sessions, rate limiting, hot data) — managed: Upstash, ElastiCache
Queue:       BullMQ (built on Redis) for background jobs
Frontend:    Next.js 14 + React 18 (or Astro for content-heavy sites)
             Tailwind CSS + shadcn/ui
Testing:     Vitest (unit/integration) + Playwright (e2e)
Build:       Vite (frontend) + tsc (backend)
Deploy:      Docker + docker-compose (dev) → Fly.io / Railway / Render (small scale)
             → AWS ECS / GCP Cloud Run (medium scale)
```

**Best for**: SaaS products, internal tools, B2B/B2C web apps, API backends, teams comfortable with JS/TS.

**When to avoid**: CPU-bound workloads (video processing, ML inference), teams unfamiliar with async JavaScript.

---

### Python Stack
```
Backend:     Python 3.12 + FastAPI 0.115 (async, auto OpenAPI docs)
             or Django 5 + DRF (batteries-included, better for rapid CRUD)
ORM:         SQLAlchemy 2 + Alembic (mature, flexible) or Django ORM (if using Django)
Validation:  Pydantic v2 (FastAPI native) or marshmallow
Auth:        FastAPI-Users (session + JWT) or django-allauth
Primary DB:  PostgreSQL 16
Cache:       Redis 7 — redis-py with connection pooling
Queue:       Celery + Redis/RabbitMQ (battle-tested) or Dramatiq (lighter)
Frontend:    React + TypeScript (separate SPA) or Django templates (HTMX for interactivity)
Testing:     pytest + pytest-asyncio + httpx (API tests)
Deploy:      Docker → Fly.io / Railway → AWS ECS / GCP Cloud Run
```

**Best for**: Data-heavy apps, ML integration, scientific/analytical backends, teams with Python expertise.

**When to avoid**: Real-time features (WebSocket-heavy), teams with no Python experience.

---

### Go Stack
```
Backend:     Go 1.26 + net/http (stdlib) or Gin / Echo / Chi
             (Fiber if Express-like routing is preferred)
ORM:         sqlc (type-safe SQL codegen — preferred) or GORM (ORM-style)
Auth:        golang-jwt/jwt + bcrypt (stdlib)
Primary DB:  PostgreSQL 16 — pgx/v5 driver + pgxpool (connection pooling)
Cache:       Redis 7 — go-redis/v9
Queue:       Asynq (Redis-backed) or NATS JetStream (lightweight)
Frontend:    Separate React/Next.js SPA, or Go templates + HTMX
Testing:     Built-in testing + testify + httptest
Deploy:      Docker (single static binary, tiny images) → Kubernetes or bare metal
```

**Best for**: High-TPS APIs (>5,000 TPS on modest hardware), services with tight latency requirements, teams comfortable with Go's concurrency model.

**When to avoid**: Rapid prototyping (slower initial development), teams new to Go.

---

### Java / JVM Stack
```
Backend:     Java 21 (virtual threads / Loom) + Spring Boot 3.3
             or Quarkus 3 (faster startup, native compilation)
ORM:         Spring Data JPA + Hibernate 6, or jOOQ (type-safe SQL)
Validation:  Jakarta Bean Validation (Hibernate Validator)
Auth:        Spring Security 6 + OAuth2 Resource Server
Primary DB:  PostgreSQL 16 — HikariCP connection pool
Cache:       Redis 7 — Lettuce client (Spring Cache abstraction)
Queue:       Spring AMQP + RabbitMQ (simple) or Spring Kafka (high throughput)
Frontend:    Separate React SPA or Thymeleaf (server-side templates)
Testing:     JUnit 5 + Mockito + Spring Boot Test + Testcontainers
Build:       Maven or Gradle
Deploy:      Docker → Kubernetes (Helm) or AWS ECS
```

**Best for**: Enterprise environments, teams with Java expertise, projects requiring deep Spring ecosystem integration (Spring Batch, Spring Integration).

**When to avoid**: Startups that need rapid iteration (higher boilerplate), cost-sensitive small deployments (JVM memory footprint).

---

## Microservices Stack

Only recommend microservices when: teams are large enough to own individual services, deployment independence is a hard requirement, or services need genuinely different scaling profiles.

### Core Platform
```
Container runtime:   Docker 26
Orchestration:       Kubernetes 1.30 (EKS / GKE / AKS for managed; k3s for bare metal)
Service mesh:        Istio (>10 services) or Linkerd (lightweight, <10 services)
                     Skip service mesh for < 5 services — overkill
API gateway:         Kong (powerful, self-hosted) or AWS API Gateway / GCP Apigee (managed)
                     or Nginx with Lua for simple routing
Config management:   Kubernetes ConfigMaps + Sealed Secrets / External Secrets Operator
                     HashiCorp Vault (secrets management at scale)
```

### Service Communication
```
Sync (request-response):   gRPC (internal, typed) + REST/JSON (external-facing)
Async (event-driven):      Apache Kafka 3 (high throughput, durable, replay)
                            or RabbitMQ 3.13 (simpler, lower ops overhead)
                            or NATS JetStream (lightweight, built for cloud-native)
Schema registry:            Confluent Schema Registry (with Kafka) for Avro/Protobuf contracts
```

**Kafka vs RabbitMQ**:
- Kafka: event sourcing, audit trails, replay, > 10K msg/s, multiple consumer groups
- RabbitMQ: task queues, fan-out, < 10K msg/s, simpler ops, traditional message routing

### Per-Service Stack
Each service can use any language. Common choices:
- **API-heavy CRUD services**: Node.js/TypeScript + Fastify + Prisma
- **Compute-heavy services**: Go or Java/Kotlin
- **ML/data services**: Python + FastAPI
- **Event consumers/producers**: Go (low overhead) or Java (Spring Kafka)

### Observability (Required for Microservices)
```
Metrics:    Prometheus + Grafana (self-hosted) or Datadog / New Relic (managed)
Logging:    Loki + Grafana (self-hosted) or Elastic Stack (ELK) or Datadog Logs
Tracing:    OpenTelemetry SDK (in every service) + Jaeger or Tempo (backend)
Alerting:   Alertmanager (Prometheus) + PagerDuty / Opsgenie
```

---

## Serverless Stack

Best for: event-driven workloads, irregular traffic (pay-per-invocation), webhooks, data pipelines, scheduled jobs.

### AWS Serverless
```
Compute:      Lambda (Node.js 22, Python 3.12, Java 21, Go 1.22 runtimes)
API:          API Gateway (REST) or HTTP API (lower latency, cheaper)
              or ALB (for WebSocket and long-lived connections)
Database:     DynamoDB (primary key access, high throughput)
              Aurora Serverless v2 (relational, scales to zero)
              RDS Proxy (for connecting Lambda to RDS without connection exhaustion)
Cache:        ElastiCache Serverless (Redis-compatible)
Queue:        SQS (simple, Lambda trigger) + SNS (fan-out)
              EventBridge (event bus for complex routing)
Storage:      S3 (files, assets, data lake)
Auth:         Cognito User Pools (managed auth) + API Gateway Authorizer
IaC:          AWS CDK (TypeScript) or SAM or Terraform
```

### GCP Serverless
```
Compute:      Cloud Functions 2nd gen (Node.js, Python, Go, Java)
              Cloud Run (containerized, more control)
Database:     Firestore (document, real-time sync) or Cloud Spanner (global SQL)
              Cloud SQL (PostgreSQL/MySQL, managed)
Queue:        Cloud Pub/Sub + Cloud Tasks
Storage:      Cloud Storage (GCS)
Auth:         Firebase Authentication + Identity Platform
IaC:          Terraform + GCP provider or Pulumi
```

### Azure Serverless
```
Compute:      Azure Functions (Node.js, Python, C#, Java)
              Azure Container Apps (containerized, KEDA-based scaling)
Database:     Cosmos DB (multi-model, globally distributed)
              Azure SQL (managed SQL Server/PostgreSQL)
Queue:        Azure Service Bus + Event Grid
Storage:      Azure Blob Storage
Auth:         Azure AD B2C (consumer apps) or Azure AD (enterprise)
IaC:          Bicep or Terraform + Azure provider
```

---

## Database Selection Guide

### Primary relational store
| Requirement                       | Recommendation                                                     |
|-----------------------------------|--------------------------------------------------------------------|
| Default OLTP, complex queries     | **PostgreSQL 16** (preferred)                                      |
| Simple OLTP, wide hosting support | **MySQL 8** / MariaDB                                              |
| Embedded, single-file, local dev  | **SQLite 3.45**                                                    |
| Global distributed OLTP           | **CockroachDB** (PostgreSQL-compatible) or **PlanetScale** (MySQL) |
| Analytical queries (OLAP)         | **ClickHouse** or **DuckDB** (embedded analytics)                  |

### Cache / session store
| Requirement                        | Recommendation                            |
|------------------------------------|-------------------------------------------|
| Sessions, rate limiting, pub/sub   | **Redis 7** (Valkey 7 — open-source fork) |
| Simple key-value, multi-AZ managed | **AWS ElastiCache** (Redis-compatible)    |
| Serverless, pay-per-use            | **Upstash Redis**                         |

### NoSQL / document
| Requirement                         | Recommendation                                   |
|-------------------------------------|--------------------------------------------------|
| Flexible schema, nested documents   | **MongoDB 7** (Atlas managed)                    |
| Firebase ecosystem, real-time sync  | **Firestore**                                    |
| Extreme write throughput, key-value | **DynamoDB** (AWS) or **Cassandra 5**            |
| Embedded / edge key-value           | **SQLite** (WAL mode) or **SlateDB** (LSM-based) |

### Search
| Requirement                            | Recommendation                                              |
|----------------------------------------|-------------------------------------------------------------|
| Product search, facets, typo tolerance | **Typesense** (easy ops) or **Meilisearch** (self-hosted)   |
| Full-text + aggregations + analytics   | **Elasticsearch** / **OpenSearch**                          |
| Managed, Postgres-native               | **pg_vector + pg_trgm** (for simpler search on existing PG) |

### Time-series
| Requirement                    | Recommendation                                             |
|--------------------------------|------------------------------------------------------------|
| Metrics, IoT, financial data   | **TimescaleDB** (PostgreSQL extension — reuse existing PG) |
| Dedicated time-series at scale | **InfluxDB 3** or **VictoriaMetrics**                      |

---

## Infrastructure by Cloud Provider

### AWS (most feature-rich, highest ops overhead)
```
Compute:      ECS Fargate (containerized, no cluster management) — recommended default
              EKS (Kubernetes, >20 services or if Kubernetes expertise exists)
              EC2 (if GPU workloads or special instance types needed)
Database:     RDS PostgreSQL (managed, Multi-AZ for HA)
              Aurora PostgreSQL (auto-scaling storage, up to 15 read replicas)
Cache:        ElastiCache (Redis-compatible)
Storage:      S3 + CloudFront (CDN)
Load balancer: ALB (HTTP/HTTPS/WebSocket) + Route 53 (DNS)
Secrets:      AWS Secrets Manager + IAM roles (never access keys in code)
Monitoring:   CloudWatch + AWS X-Ray (or Datadog/Grafana if self-managed preferred)
IaC:          Terraform (multi-cloud portability) or AWS CDK (AWS-native TypeScript)
```

### GCP (best for ML/data workloads, strong Kubernetes)
```
Compute:      Cloud Run (preferred — serverless containers, scales to zero)
              GKE Autopilot (managed Kubernetes, pay-per-pod)
Database:     Cloud SQL (PostgreSQL/MySQL, managed)
              AlloyDB (PostgreSQL-compatible, 4× faster for OLTP)
Cache:        Memorystore (Redis-compatible)
Storage:      GCS + Cloud CDN
Load balancer: Cloud Load Balancing (global HTTP(S) LB)
Secrets:      Secret Manager + Workload Identity (avoid service account keys)
Monitoring:   Cloud Monitoring + Cloud Trace + Cloud Logging
IaC:          Terraform + Google provider
```

### Azure (enterprise/Microsoft ecosystem)
```
Compute:      Azure Container Apps (serverless containers, KEDA scaling) — recommended
              AKS (managed Kubernetes)
Database:     Azure Database for PostgreSQL Flexible Server
              Azure SQL (SQL Server, T-SQL)
Cache:        Azure Cache for Redis
Storage:      Azure Blob Storage + Azure Front Door (CDN + WAF)
Load balancer: Azure Application Gateway (WAF) + Azure Load Balancer
Secrets:      Azure Key Vault + Managed Identity
Monitoring:   Azure Monitor + Application Insights
IaC:          Bicep (Azure-native) or Terraform + Azure provider
```

### Self-hosted / On-premise
```
Virtualization: Proxmox VE (bare metal VM management)
Containers:     Docker Swarm (simple, <20 nodes) or K3s / RKE2 (Kubernetes-lite)
Database:       PostgreSQL (self-managed) + Barman/pgBackRest (backups)
Cache:          Redis or Valkey (self-hosted)
Storage:        MinIO (S3-compatible object storage)
Load balancer:  Nginx or Caddy (TLS termination, reverse proxy)
Secrets:        HashiCorp Vault (open-source) or Infisical
Monitoring:     Prometheus + Grafana + Loki (full Grafana Stack)
IaC:            Ansible (configuration management) + Terraform (if using cloud hybrid)
```

---

## Authentication and Authorization

### For user-facing web/mobile apps
| Scenario                    | Recommendation                                                   |
|-----------------------------|------------------------------------------------------------------|
| Full control, self-hosted   | **Keycloak 24** (OAuth2/OIDC, SSO, MFA, RBAC — enterprise-grade) |
| Self-hosted, simpler ops    | **Ory Kratos + Hydra** (modern, cloud-native)                    |
| Managed, pay-as-you-go      | **Auth0** (Okta) — great DX, generous free tier                  |
| Firebase ecosystem          | **Firebase Authentication**                                      |
| AWS ecosystem               | **Amazon Cognito**                                               |
| B2B SaaS, organization RBAC | **WorkOS** or **Clerk**                                          |

### For service-to-service authentication
- **mTLS** — mutual TLS via service mesh (Istio/Linkerd) for zero-trust internal auth
- **JWT with shared secret** — for simple internal APIs (avoid for sensitive services)
- **OAuth2 Client Credentials** — for API-to-API calls through an identity provider

---

## Frontend

| Use Case                        | Recommendation                                                                     |
|---------------------------------|------------------------------------------------------------------------------------|
| SPA / interactive web app       | **React 18 + TypeScript + Vite**                                                   |
| Full-stack with SSR/SSG         | **Next.js 14** (App Router + React Server Components)                              |
| Content-heavy site, fast static | **Astro 4** (island architecture, minimal JS)                                      |
| Admin dashboard                 | **Next.js + shadcn/ui** or **Remix**                                               |
| Mobile cross-platform           | **React Native + Expo** (or Flutter for truly native feel)                         |
| PWA / lightweight               | **Svelte 5 / SvelteKit**                                                           |
| HTMX + server-rendered          | **HTMX** + any backend template engine (simple interactivity without SPA overhead) |

**CSS / UI frameworks**:
- **Tailwind CSS 4** — utility-first, design system via CSS variables
- **shadcn/ui** — accessible, composable components (React + Tailwind)
- **Radix UI** — headless components (bring your own styles)
- **MUI / Ant Design** — opinionated, feature-rich (good for internal tools)

---

## How to justify recommendations in the architecture document

Every technology choice must cite at least one requirement from stages 1–4. Use this pattern:

> **PostgreSQL 16** was chosen as the primary database because:
> - The team has 3 years of PostgreSQL experience [Stage 3 — team competencies]
> - The data model is relational with complex joins and ACID transaction requirements [Stage 2 — NFR: strong consistency]
> - The estimated 500 TPS write workload is well within PostgreSQL's range with connection pooling [Stage 4 — capacity planning]
> - Budget allows for managed RDS (~$150/month for db.t4g.medium) [Stage 3 — budget]

If you cannot trace a recommendation back to a specific user requirement, either find the traceability or reconsider the recommendation.

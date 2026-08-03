# Technology Stack Recommendations

Concrete stack recommendations organized by architecture pattern, scale, and team context. Use this as a starting point
for Stage 5 recommendations — always justify the final choice against the user's specific requirements, not just this
guide.

## Contents

1. [Quick Decision Matrix](#quick-decision-matrix)
2. [Modular Monolith (Recommended Default)](#modular-monolith-recommended-default-for-small-early-stage-teams)
    - [Node.js / TypeScript Stack](#nodejs--typescript-stack)
    - [Python Stack](#python-stack)
    - [Go Stack](#go-stack)
    - [Rust Stack](#rust-stack)
    - [Java / JVM Stack](#java--jvm-stack)
    - [Ruby / Rails Stack](#ruby--rails-stack)
3. [Microservices Stack](#microservices-stack)
    - [Core Platform](#core-platform)
    - [Service Communication](#service-communication)
    - [Per-Service Stack](#per-service-stack)
    - [Observability](#observability-required-for-microservices)
4. [Serverless Stack](#serverless-stack)
    - [AWS Serverless](#aws-serverless)
    - [GCP Serverless](#gcp-serverless)
    - [Azure Serverless](#azure-serverless)
    - [Self-hosted / open-source Serverless](#self-hosted--open-source-serverless)
5. [Database Selection Guide](#database-selection-guide)
6. [Infrastructure by Cloud Provider](#infrastructure-by-cloud-provider)
    - [AWS](#aws-most-feature-rich-highest-ops-overhead)
    - [GCP](#gcp-best-for-mldata-workloads-strong-kubernetes)
    - [Azure](#azure-enterprisemicrosoft-ecosystem)
    - [Self-hosted / On-premise](#self-hosted--on-premise)
7. [Authentication and Authorization](#authentication-and-authorization)
8. [Rate Limiting](#rate-limiting)
9. [Frontend](#frontend)
10. [How to Justify Recommendations](#how-to-justify-recommendations-in-the-architecture-document)

---

## Quick Decision Matrix

Before recommending a stack, answer these four questions from the requirements you've gathered:

| Question    | Small / Startup | Medium / Growth | Large / Enterprise        |
|-------------|-----------------|-----------------|---------------------------|
| Team size   | 1–5 devs        | 5–25 devs       | 25+ devs / multiple teams |
| Peak TPS    | < 100           | 100–2,000       | > 2,000                   |
| Data volume | < 100 GB        | 100 GB – 5 TB   | > 5 TB                    |
| Budget      | Minimize cost   | Moderate        | Cost-optimized at scale   |

**Architecture pattern rule of thumb** — these thresholds are deliberately looser than the tier table above (a
well-optimized monolith often outperforms the "Small/Startup" TPS ceiling before microservices become necessary); use
the tier table above for sizing infrastructure/budget, and this rule of thumb only for the monolith-vs-microservices
pattern call:

- 1–5 devs, < 500 TPS → **Modular monolith** (default)
- 5–20 devs, need independent deploy cadence → **Microservices** (only if teams are ready for the ops overhead)
- Sporadic/event-driven workload, no persistent connections → **Serverless**
- Data-pipeline centric, batch processing → **Event-driven / streaming**

---

## Modular Monolith (Recommended Default for Small/Early-Stage Teams)

### Node.js / TypeScript Stack

```
Backend:     Node.js 24 + Fastify 5 (schema-based validation and lower request overhead than
             Express; pick Express 5 instead for its larger plugin ecosystem or team familiarity)
             TypeScript 5 + strict mode (catches null/undefined and implicit-any bugs at compile
             time — worth the friction on anything beyond a throwaway script)
ORM:         Prisma 6 (great DX, auto-migrations) or Drizzle ORM (lighter, closer to SQL)
             or TypeORM (decorator-based, mature, pairs well with NestJS) or Kysely (type-safe
             SQL query builder, no codegen)
Validation:  Zod (runtime + TypeScript type inference — one schema drives both request validation
             and compile-time types, no separate type-definition step to keep in sync)
Auth:        jose (JWT) or paseto (PASETO — see "Token format: JWT vs PASETO" below) + argon2
             (Argon2id password hashing) for a hand-rolled system, or Better Auth (session-based,
             full-featured — Lucia was deprecated by its maintainer in March 2025 and reframed as a
             learning resource, not an installable library as of this writing; confirm current status
             before committing, don't recommend it for a new project on memory alone)
Primary DB:  PostgreSQL 18 (default relational choice — see "Database Selection Guide" below for
             when another engine fits better; managed: RDS, Cloud SQL, Supabase, Neon)
Cache:       Redis 8, or Valkey/DragonflyDB/Garnet (Redis-compatible alternatives) — sessions, rate
             limiting, and hot-data caching all need the same fast key-value store, so one instance
             covers all three instead of provisioning separately; managed: Upstash, ElastiCache
Queue:       BullMQ (built on Redis) for background jobs — reuses the cache instance already
             provisioned above rather than adding a dedicated broker
Frontend:    Next.js 16 + React 19 (SSR/SSG plus the largest React ecosystem and hiring pool; use
             Astro instead for a mostly-static, content-heavy site where React's client JS is
             overhead rather than a need)
             Tailwind CSS + shadcn/ui (utility classes avoid maintaining a separate CSS-naming
             scheme; shadcn's copy-in components stay fully editable, unlike an installed package)
Testing:     Vitest (unit/integration — Vite-native config and transforms, faster startup than Jest
             in this stack) + Playwright (e2e — cross-browser, auto-waiting, less flaky than
             Selenium-based tools)
Build:       Vite (frontend — native-ESM dev server, near-instant HMR) + tsc (backend — a Node
             process needs type-checking and plain JS output, not bundling)
Deploy:      Docker + docker-compose (dev) → Coolify / Dokku (self-hosted, open-source PaaS —
             Heroku-like deploy UX without vendor lock-in) or Fly.io / Railway / Render (small
             scale — zero ops, deploy on push) → AWS ECS / GCP Cloud Run (medium scale — once
             traffic outgrows what a single-host PaaS can handle)
```

**Best for**: SaaS products, internal tools, B2B/B2C web apps, API backends, teams comfortable with JS/TS.

**When to avoid**: CPU-bound workloads (video processing, ML inference), teams unfamiliar with async JavaScript.

---

### Python Stack

```
Backend:     Python 3.14 + FastAPI (latest stable — verify current version; async, auto OpenAPI docs —
             the async-native choice when
             the API calls other network services concurrently) or Django 5 + DRF
             (batteries-included: auth, admin panel, and ORM migrations all ship together — better
             for rapid CRUD apps where that scaffolding saves real time)
ORM:         SQLAlchemy 2 + Alembic (mature, flexible — the safe default for any non-Django backend)
             or Django ORM (comes free with Django, tightly integrated with its admin and migrations
             — use it only once already committed to Django) or Tortoise ORM (async-first,
             Django-ORM-like API, pairs well with FastAPI's own async model)
Validation:  Pydantic v2 (FastAPI native — FastAPI generates its OpenAPI schema directly from
             Pydantic models, so there's no second schema to keep in sync) or marshmallow
             (framework-agnostic — the right choice outside FastAPI, where Pydantic's tight coupling
             to it doesn't apply)
Auth:        FastAPI-Users (session + JWT — in maintenance mode as of this writing: security/dependency
             fixes only, no new features, with a successor toolkit in progress; confirm current status
             before committing) or django-allauth (Django's de facto standard, integrates with its
             admin and permission system), or hand-rolled with PyJWT / pyseto (PASETO) +
             argon2-cffi (Argon2id password hashing)
Primary DB:  PostgreSQL 18 (default relational choice, same reasoning as the Node.js stack above —
             see "Database Selection Guide" below for when another engine fits better)
Cache:       Redis 8, or Valkey/DragonflyDB/Garnet (Redis-compatible alternatives) — redis-py with
             connection pooling; same one-store-for-sessions/rate-limiting/hot-data reasoning as the
             Node.js stack above
Queue:       Celery + Redis/RabbitMQ (battle-tested — the safest choice for a team's first
             production queue) or Dramatiq (lighter — smaller API surface once Celery's extra
             flexibility isn't actually being used)
Frontend:    React + TypeScript (separate SPA — needed once the frontend has real client-side
             interactivity or its own team) or Django templates + HTMX (interactivity without a SPA
             build step, when Django's server-rendered pages are otherwise sufficient)
Testing:     pytest (the ecosystem-standard test runner — fixtures and plugins cover nearly every
             case) + pytest-asyncio (required to exercise FastAPI's async routes at all) + httpx
             (API tests — an async-native client that mirrors FastAPI's own request handling)
Deploy:      Docker → Coolify / Dokku (self-hosted, open-source PaaS) or Fly.io / Railway
             → AWS ECS / GCP Cloud Run — same self-hosted → managed-PaaS → cloud-container
             progression as the Node.js stack above, scaled to traffic
```

**Best for**: Data-heavy apps, ML integration, scientific/analytical backends, teams with Python expertise.

**When to avoid**: Real-time features (WebSocket-heavy), teams with no Python experience.

---

### Go Stack

```
Backend:     Go 1.26 + net/http (stdlib — sufficient on its own since Go 1.22's routing
             improvements; reach for a router only when its extras are actually needed) or
             Gin / Echo / Chi (middleware ecosystem, request binding, and less boilerplate than
             raw net/http) (Fiber if an Express-like routing/API feel is preferred)
ORM:         sqlc (type-safe SQL codegen — preferred: generates Go structs/functions straight from
             hand-written SQL, so the query and its types can never drift apart) or GORM (ORM-style
             — familiar to teams coming from Prisma/ActiveRecord-style APIs) or Ent
             (graph-based, schema-as-code ORM created at Facebook, now a Linux Foundation project
             stewarded by Ariga — strongest fit for a heavily relational domain model with many
             entity-to-entity edges)
Auth:        golang-jwt/jwt or aidanwoods.dev/go-paseto (PASETO) + golang.org/x/crypto/argon2
             (Argon2id password hashing) — both from the official x/crypto extended package, not
             the core stdlib despite the common shorthand
Primary DB:  PostgreSQL 18 — pgx/v5 driver + pgxpool (connection pooling — pgx is faster and more
             feature-complete than database/sql's generic driver interface for Postgres specifically)
Cache:       Redis 8, or Valkey/DragonflyDB/Garnet (Redis-compatible alternatives) — go-redis/v9
             (the actively maintained client, full command coverage and cluster support)
Queue:       Asynq (Redis-backed — reuses the cache instance above, minimal ops for a first queue)
             or NATS JetStream (lightweight — pick this only if NATS is already in the stack for
             messaging, not worth adding solely for a queue)
Frontend:    Separate React/Next.js SPA (when the frontend needs its own team or rich client-side
             interactivity), or Go templates + HTMX (skips a separate frontend build/deploy
             entirely when the UI is mostly server-rendered)
Testing:     Built-in testing (no dependency needed for the basics) + testify (assertion helpers
             and mocks the stdlib package doesn't provide) + httptest (in-process HTTP testing
             without binding a real port)
Deploy:      Docker (single static binary, tiny images — Go's biggest deploy advantage over every
             other stack here) → Coolify / Dokku (self-hosted, open-source PaaS), Kubernetes, or
             bare metal (a static binary runs anywhere with no runtime installed)
```

**Best for**: High-TPS APIs, services with tight latency requirements, teams comfortable with Go's concurrency model —
size the actual TPS target from this project's own capacity planning (Stage 4), not a generic figure quoted from memory.

**When to avoid**: Rapid prototyping (slower initial development), teams new to Go.

---

### Rust Stack

Crate versions below (Axum/Actix-web/Rocket/SeaORM/Diesel/SQLx) move quickly — confirm the current major/minor before
committing, same as the other version-specific claims in this file.

```
Backend:     Rust (stable) + Axum 0.8 (Tokio-based, most popular choice for new services)
             or Actix-web 4 (mature, highest raw throughput) or Rocket 0.5 (batteries-included,
             most ergonomic)
ORM:         SeaORM 1 (async-first, ActiveRecord-style, best DX) or Diesel 2 (compile-time-checked
             query builder, most mature, sync-first with async support via diesel-async) or SQLx 0.8
             (not an ORM — compile-time-checked raw SQL, closest to Go's sqlc philosophy above)
Validation:  validator crate (derive-macro based, simplest for common cases) or garde (newer, more
             composable rules — pick this once validation needs to reference other fields or
             compose conditionally)
Auth:        jsonwebtoken crate (JWT) or rusty_paseto (PASETO) + argon2 crate (Argon2id password
             hashing)
Primary DB:  PostgreSQL 18 — deadpool-postgres (when using SQLx/raw queries directly) or the ORM's
             own connection pool (when using Diesel/SeaORM, which already manage pooling internally)
Cache:       Redis 8, or Valkey/DragonflyDB/Garnet (Redis-compatible alternatives) — deadpool-redis
             (async connection pooling, the standard pairing alongside deadpool-postgres above)
Queue:       Apalis (Rust-native, Redis/Postgres-backed — typed jobs, no separate broker needed if
             already on Postgres) or a Redis-backed queue (simpler when a queue-specific library
             isn't wanted)
Frontend:    Separate React/Next.js SPA (larger ecosystem and easier hiring — the default), or
             Leptos/Yew (full-Rust WASM frontend — worth it mainly when the team wants zero
             context-switching between backend and frontend languages)
Testing:     Built-in #[test] + tokio::test (async test support, no extra dependency), insta
             (snapshot testing — catches unintended output changes in serialized responses without
             hand-writing an assertion for every field)
Build:       Cargo (the standard build tool for the ecosystem — also handles dependency resolution,
             workspaces, and release profiles)
Deploy:      Docker (single static binary, smallest images of any stack here) → Coolify /
             Dokku (self-hosted, open-source PaaS), Kubernetes, or bare metal
```

**Choosing among Diesel / SeaORM / SQLx** — the three solve different problems, not the same problem three ways:

- **SQLx**: not an ORM — async, compile-time-checked raw SQL via macros that verify every query against the real
  database schema at compile time (`cargo sqlx prepare`). Pick this when the team wants full SQL control with
  compile-time safety — the same philosophy as Go's sqlc above.
- **Diesel**: a compile-time-checked query builder (a typed DSL, not raw SQL), the most mature of the three, with the
  strongest migration tooling. Historically sync-first; async support exists via `diesel-async`. Pick this for a team
  that wants the strongest compile-time guarantees and doesn't mind a steeper learning curve.
- **SeaORM**: async-first, ActiveRecord-style ORM (entities, relations, `sea-orm-cli` migrations) built on top of SQLx —
  closest in day-to-day ergonomics to Prisma/TypeORM. Pick this when developer velocity and a familiar ORM API matter
  more than Diesel's compile-time strictness.

**Best for**: high-throughput or latency-sensitive services, systems-level components, teams that value memory safety
without a garbage collector, and long-running services where a small binary and low memory footprint reduce operating
cost.

**When to avoid**: rapid prototyping under a tight deadline (steepest learning curve and slowest initial development of
any stack here), teams with no Rust experience and no runway to build it, projects that need a library ecosystem as
broad as Node/Python/Java's.

---

### Java / JVM Stack

```
Backend:     Java 21 or Java 25 (both LTS — 21 has the longer production track record; 25 is the newer
             LTS, current since September 2025 — virtual threads / Loom on either gives high-concurrency
             I/O-bound workloads without the reactive-programming complexity Project Reactor requires)
             + Spring Boot 4.1.0
             (the default: largest ecosystem and hiring pool, batteries-included auto-config)
             or Quarkus 3.37 (faster startup, native compilation — pick this over Spring Boot for
             serverless/container workloads where cold-start time and memory footprint matter more
             than ecosystem breadth)
ORM:         Spring Data JPA + Hibernate 7.4 (the default with Spring Boot — repository interfaces
             generate most CRUD code, minimal boilerplate), or jOOQ (type-safe SQL — for a team that
             wants to write SQL directly with compile-time safety instead of JPQL/HQL) or MyBatis
             (SQL-mapper style, common in enterprise migrations — fits teams already maintaining
             hand-written SQL that JPA's entity model doesn't map onto cleanly)
Validation:  Jakarta Bean Validation (Hibernate Validator — the standard annotation-based validation
             Spring Boot auto-configures, no separate integration work needed)
Auth:        Spring Security 7.1 + OAuth2 Resource Server (see "For fine-grained access
             control" below for authorization-library options, including Java's jCasbin), or
             paseto4j / jpaseto for PASETO — password hashing via Spring Security's built-in
             Argon2PasswordEncoder (requires the BouncyCastle dependency)
Primary DB:  PostgreSQL 18 — HikariCP connection pool (Spring Boot's own default pool — the fastest
             JVM connection pool in independent benchmarks, no extra configuration needed)
Cache:       Redis 8, or Valkey/DragonflyDB/Garnet (Redis-compatible alternatives) — Lettuce client
             (Spring Cache abstraction — async, thread-safe connections shareable across requests,
             unlike the older Jedis client)
Queue:       Spring AMQP + RabbitMQ (simple) or Spring Kafka (high throughput)
Frontend:    Separate React SPA (when the frontend needs its own team or rich interactivity) or
             Thymeleaf (server-side templates — skips a separate frontend build/deploy when pages
             are mostly server-rendered, same tradeoff as the Django/Go template options above)
Testing:     JUnit 6.1.2 + Mockito (unit tests, mocking dependencies) + Spring Boot Test (loads a
             real Spring context for integration tests) + Testcontainers (runs a real
             Postgres/Redis in Docker for tests instead of mocking the database — catches issues
             mocks would miss)
Build:       Maven (XML config, explicit and IDE-friendly) or Gradle (Groovy/Kotlin DSL, faster
             incremental builds — pick this for larger multi-module projects)
Deploy:      Docker → Kubernetes (Helm — the standard for JVM services already running in
             containers) or AWS ECS (simpler ops when full Kubernetes isn't needed)
```

**Best for**: Enterprise environments, teams with Java expertise, projects requiring deep Spring ecosystem integration
(Spring Batch, Spring Integration).

**When to avoid**: Startups that need rapid iteration (higher boilerplate), cost-sensitive small deployments (JVM memory
footprint).

---

### Ruby / Rails Stack

Ruby follows an annual December release cadence and Rails ships minor releases between majors — confirm the current
stable versions before committing, same as the other version-specific claims in this file.

```
Backend:     Ruby 3.4 + Rails 8 (batteries-included: ORM, background jobs, caching, and a deploy
             tool ship together, and its "Solid Trifecta" — Solid Queue, Solid Cache, Solid Cable —
             lets a small-to-medium app run entirely on the primary database with no separate Redis
             instance) or Sinatra (minimal, unopinionated — pick this only for a small API with no
             need for Rails' conventions/scaffolding)
ORM:         Active Record (Rails' built-in ORM — migrations, associations, and validations ship
             together, the default for any Rails app) or Sequel (framework-agnostic, more explicit
             query control — the right choice outside Rails, where Active Record's tight coupling to
             it doesn't apply)
Validation:  Active Record validations (declarative, built into the model layer — no separate schema
             to keep in sync with the database) or dry-validation (framework-agnostic, composable —
             outside Rails, or when validation logic needs to be decoupled from models)
Auth:        Rails 8's built-in `bin/rails generate authentication` (session-based, bcrypt via
             `has_secure_password` — no gem required for a standard username/password flow) or
             Devise (the long-standing, most feature-complete gem: registrations, confirmable,
             lockable, OmniAuth — reach for it once the built-in generator's scope isn't enough) or
             Rodauth (security-focused, more explicit configuration) — jwt gem (JWT) or paseto gem
             (PASETO) for token-based APIs
Primary DB:  PostgreSQL 18 (default relational choice, same reasoning as the other stacks above —
             see "Database Selection Guide" below for when another engine fits better)
Cache:       Rails 8's Solid Cache (database-backed — no separate cache store to provision for a
             small-to-medium app) or Redis 8 / Valkey / DragonflyDB / Garnet (once cache-hit latency
             or throughput outgrows what a database-backed cache can sustain)
Queue:       Solid Queue (Rails 8 default — database-backed, no separate broker) or Sidekiq
             (Redis-backed — the ecosystem standard for high-throughput background jobs once Solid
             Queue's database-backed model becomes the bottleneck) or good_job (Postgres-backed
             alternative to Sidekiq, no Redis dependency)
Frontend:    Hotwire (Turbo + Stimulus — Rails' own default: SPA-like interactivity from
             server-rendered HTML, no separate frontend build) or a separate React/Next.js SPA (once
             the frontend needs its own team or interactivity Hotwire can't express cleanly)
Testing:     RSpec (the ecosystem-standard test framework — most third-party gems document RSpec
             examples first) or Minitest (Rails' built-in default, lighter dependency footprint) +
             Capybara (browser-driven system tests) + FactoryBot (test data generation)
Build:       Bundler (dependency management, the standard for the ecosystem) + Propshaft (Rails 8's
             default asset pipeline) or Vite Ruby (once the frontend needs a modern JS build pipeline
             alongside Hotwire)
Deploy:      Kamal (Rails' own zero-downtime Docker deploy tool, the Rails 8 default — deploys to any
             VPS with no PaaS lock-in) or Coolify / Dokku (self-hosted, open-source PaaS) or Render /
             Fly.io / Heroku (zero ops, deploy on push)
```

**Best for**: Content-heavy and CRUD-centric web apps, teams that value convention-over-configuration and shipping
speed, startups validating a product where Rails' batteries-included defaults save real time.

**When to avoid**: CPU-bound workloads (MRI's Global VM Lock limits true in-process parallelism — scale via multiple
processes/dynos instead, not threads), teams with no Ruby experience and no runway to build it, services needing the raw
throughput ceiling Go/Rust/Java reach more easily.

---

## Microservices Stack

Only recommend microservices when: teams are large enough to own individual services, deployment independence is a hard
requirement, or services need genuinely different scaling profiles.

### Core Platform

```
Container runtime:   Docker 29 (the OCI image build/runtime every CI pipeline and orchestrator
                     below assumes)
Orchestration:       Kubernetes 1.36 (EKS / GKE / AKS for managed — offloads control-plane ops;
                     k3s for bare metal — same API surface, much smaller footprint)
Service mesh:        Istio (>10 services — full-featured mTLS, traffic-shaping, and observability)
                     or Linkerd (lightweight, <10 services — simpler ops, less mesh functionality)
                     Skip service mesh for < 5 services — overkill
API gateway:         Kong or APISIX or Traefik (all open-source, self-hosted — full control, no
                     per-request cost) or AWS API Gateway / GCP Apigee (managed — no gateway
                     infrastructure to run) or Nginx with Lua for simple routing
Config management:   Kubernetes ConfigMaps + Sealed Secrets / External Secrets Operator (keeps
                     secrets safe to commit and sync via GitOps) or HashiCorp Vault (secrets
                     management at scale — dynamic secrets, rotation, and audit logging that
                     ConfigMaps/Sealed Secrets don't provide)
Storage:             Rook (Ceph operator — Kubernetes-native block/file/object storage,
                     provisioned and managed in-cluster) or MinIO (S3-compatible object
                     storage only, simpler when block/file storage isn't needed)
```

### Service Communication

```
Sync (request-response):   gRPC (internal, typed — binary protocol with generated clients keeps
                            services in sync on the contract) + REST/JSON (external-facing —
                            consumable by browsers/third parties with no codegen step)
Async (event-driven):      Apache Kafka 4.3.1 (high throughput, durable, replay)
                            or RabbitMQ 4.3 (simpler, lower ops overhead)
                            or NATS JetStream (lightweight, built for cloud-native)
Schema registry:            Confluent Schema Registry (with Kafka — the standard pairing) or
                            Apicurio Registry (fully open-source alternative) for Avro/Protobuf
                            contracts — forces producers and consumers to agree on message shape
                            before a breaking change ships
```

**Kafka vs RabbitMQ**: the real differentiator is the messaging model, not a throughput ceiling — RabbitMQ comfortably
handles tens of thousands of msg/s on modest hardware (verify current benchmarks for the target config; do not use a
fixed msg/s number as the deciding factor), so pick based on the model actually needed:

- Kafka: an ordered, durable log with configurable retention — needed when consumers must replay history, multiple
  independent consumer groups read the same stream, or event sourcing/audit-trail semantics are required
- RabbitMQ: a routed queue with flexible exchange/binding topology — needed for task queues, fan-out, or traditional
  message routing (priority queues, delayed messages, per-consumer ack/retry) where replay isn't the goal

### Per-Service Stack

Each service can use any language. Common choices:

- **API-heavy CRUD services**: Node.js/TypeScript + Fastify + Prisma, or Ruby on Rails (API-only mode) for
  convention-over-configuration speed
- **Compute-heavy services**: Go, Rust, or Java/Kotlin
- **ML/data services**: Python + FastAPI
- **Event consumers/producers**: Go or Rust (lowest overhead, via `rdkafka`) or Java (Spring Kafka)

### Observability (Required for Microservices)

```
Metrics:    Prometheus + Grafana (self-hosted — free, the de facto standard, large dashboard/
            exporter ecosystem) or Datadog / New Relic (managed — no metrics infrastructure to
            run, worth the cost once ops time is scarcer than budget)
Logging:    Loki + Grafana (self-hosted — reuses the Grafana stack above; cheaper than
            Elasticsearch at scale since it indexes labels, not full log text) or OpenSearch
            (open-source Elasticsearch/Kibana fork — full-text search once Loki's label-based
            querying isn't enough) or Datadog Logs (managed)
Tracing:    OpenTelemetry SDK (in every service — vendor-neutral instrumentation, avoids locking
            traces to one backend) + Jaeger or Tempo (backend)
Alerting:   Alertmanager (Prometheus) + Grafana Cloud IRM (managed — Grafana Labs' own successor to
            Grafana OnCall, which entered maintenance mode in March 2025 and was fully archived in
            March 2026 as of this writing; confirm current status before committing, do not recommend
            self-hosted Grafana OnCall for a new project on memory alone) or
            PagerDuty / Opsgenie (managed — richer on-call scheduling/escalation, and vendor-neutral
            if staying off the Grafana Cloud stack matters)
```

---

## Serverless Stack

Best for: event-driven workloads, irregular traffic (pay-per-invocation), webhooks, data pipelines, scheduled jobs.

### AWS Serverless

```
Compute:      Lambda (Node.js 24, Python 3.14, Java 21, Go 1.26, or Rust — GA-supported with an SLA since
              November 2025; build/package with cargo-lambda either way) — pay-per-invocation with
              no idle cost, the reason to reach for serverless at all on spiky/low-traffic workloads
API:          API Gateway (REST) or HTTP API (lower latency, cheaper)
              or ALB (for WebSocket and long-lived connections)
Database:     DynamoDB (primary key access, high throughput — scales with Lambda's concurrency, no
              connection-pool ceiling to hit)
              Aurora Serverless v2 (relational, scales to zero — for a data model that needs real
              SQL/joins DynamoDB's key-value model can't express)
              RDS Proxy (for connecting Lambda to RDS without connection exhaustion — Lambda's
              per-invocation connections would otherwise overwhelm a fixed-size RDS pool)
Cache:        ElastiCache Serverless (Redis-compatible — pay-per-use, matching Lambda's own
              pay-per-invocation cost model)
Queue:        SQS (simple, Lambda trigger) + SNS (fan-out)
              EventBridge (event bus for complex routing — content-based routing rules instead of
              one queue per consumer)
Storage:      S3 (files, assets, data lake)
Auth:         Cognito User Pools (managed auth) + API Gateway Authorizer
IaC:          AWS CDK (TypeScript) or SAM or Terraform
```

### GCP Serverless

```
Compute:      Cloud Functions 2nd gen (Node.js, Python, Go, Java) — simplest for one function per
              event trigger
              Cloud Run (containerized, more control — any language via container, including Rust)
              — pick this once a function needs a custom runtime, more memory/CPU, or several
              routes in one deployable
Database:     Firestore (document, real-time sync) or Cloud Spanner (global SQL — horizontally
              scalable strong consistency across regions, at a cost premium)
              Cloud SQL (PostgreSQL/MySQL, managed)
Queue:        Cloud Pub/Sub + Cloud Tasks
Storage:      Cloud Storage (GCS)
Auth:         Firebase Authentication + Identity Platform
IaC:          Terraform + GCP provider or Pulumi
```

### Azure Serverless

```
Compute:      Azure Functions (Node.js, Python, C#, Java) — simplest for one function per event
              trigger
              Azure Container Apps (containerized, KEDA-based scaling — any language via
              container, including Rust) — pick this once a function needs a custom runtime or
              more control than the Functions runtime allows
Database:     Cosmos DB (multi-model, globally distributed)
              Azure SQL (managed SQL Server/PostgreSQL)
Queue:        Azure Service Bus + Event Grid
Storage:      Azure Blob Storage
Auth:         Azure AD B2C (consumer apps) or Azure AD (enterprise)
IaC:          Bicep or Terraform + Azure provider
```

### Self-hosted / open-source Serverless

```
Platform:     Knative (built on Kubernetes, closest to Cloud Run's developer experience —
              recommended default for self-hosted) or OpenFaaS (simpler, function-first,
              faster to stand up) or Apache OpenWhisk (mature, IBM-backed) — runs on any
              Kubernetes cluster, including the "Self-hosted / On-premise" table below
Compute:      Any language via container (Knative, OpenFaaS) — no runtime whitelist to work
              around, unlike the managed offerings above
Queue/events: NATS JetStream or Kafka (self-hosted, per the Microservices "Service
              Communication" table above) as the event source triggering functions
IaC:          Terraform (Kubernetes provider) or plain Helm charts
```

---

## Database Selection Guide

### Primary relational store

| Requirement                       | Recommendation                                                                                                                                                          |
|-----------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Default OLTP, complex queries     | **PostgreSQL 18** (preferred) — major version current as of this writing; PostgreSQL 19 is in beta targeting Sept/Oct 2026 GA, confirm current stable before committing |
| Simple OLTP, wide hosting support | **MySQL 9.7** / MariaDB                                                                                                                                                 |
| Embedded, single-file, local dev  | **SQLite 3.53**                                                                                                                                                         |
| Global distributed OLTP           | **CockroachDB** (PostgreSQL-compatible) or **PlanetScale** (MySQL)                                                                                                      |
| Analytical queries (OLAP)         | **ClickHouse** or **DuckDB** (embedded analytics)                                                                                                                       |

**CockroachDB license note**: as of November 2024, Cockroach Labs retired the open-source CockroachDB Core offering and
relicensed under the proprietary, source-available CockroachDB Software License (mandatory license keys, enforced
telemetry, benchmarking restrictions) — it is no longer OSI-approved open source, the same class of license change the
Cache/session-store section below discusses for Redis. Confirm this license fits the project's compliance requirements
before recommending it on an "open source" basis; PostgreSQL itself (see the row above) or a PostgreSQL-compatible
managed service without this restriction is the alternative when that matters.

### Cache / session store

| Requirement                        | Recommendation                                                                |
|------------------------------------|-------------------------------------------------------------------------------|
| Sessions, rate limiting, pub/sub   | **Redis 8** (Valkey, DragonflyDB, or Garnet — see licensing comparison below) |
| Simple key-value, multi-AZ managed | **AWS ElastiCache** (Redis-compatible)                                        |
| Serverless, pay-per-use            | **Upstash Redis**                                                             |

**Choosing among Redis / Valkey / DragonflyDB / Garnet** — all four speak the same Redis protocol (drop-in
client-compatible), but differ on license and architecture. Redis itself is tri-licensed as of Redis 8 — a user picks
one of RSALv2, SSPLv1, or AGPLv3 at adoption time; only AGPLv3 is OSI-approved open source, and its network-use copyleft
terms are stricter than Valkey's or Garnet's permissive licenses, so "just use Redis" doesn't automatically mean "use a
permissively-licensed option" the way it did before the 2024 relicense — confirm which of the three license choices fits
the project before treating "Redis" as a single, unambiguous license decision:

- **Valkey**: the Linux Foundation-governed fork created when Redis first relicensed away from open source (to SSPLv1,
  pre-AGPLv3). Fully OSI-approved open source (BSD), the safest default when license terms matter as much as the
  protocol and AGPLv3's copyleft obligations aren't acceptable.
- **DragonflyDB**: a from-scratch, multi-threaded rewrite — per the vendor's own published benchmarks, often
  substantially faster than single-threaded Redis on multi-core hardware; verify against an independent or
  workload-specific benchmark before sizing infrastructure around that figure, the same caution AlloyDB's vendor-sourced
  "~4× faster" claim below (see "Infrastructure by Cloud Provider" → GCP) warrants. Licensed under the Business Source
  License (BSL), which is source-available, not OSI-approved open source (it converts to a permissive license a few
  years after each release) — confirm this license fits the project's compliance requirements before treating it as
  equivalent to Valkey/Garnet.
- **Garnet**: Microsoft's Redis-protocol-compatible cache, MIT-licensed (fully permissive open source) and also
  multi-threaded for high throughput — the newest of the three alternatives, with a smaller production track record than
  Valkey.
- **Redis** itself: still the default recommendation for name recognition, ecosystem maturity, and managed-hosting
  availability (ElastiCache, Upstash, etc.) — reach for one of the three alternatives above specifically for license
  concerns (Valkey), raw throughput on multi-core hardware (DragonflyDB, Garnet), or to avoid Redis's own post-relicense
  terms.

### NoSQL / document

| Requirement                         | Recommendation                                                                                                                                                                                                                       |
|-------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Flexible schema, nested documents   | **MongoDB 8** (Atlas managed)                                                                                                                                                                                                        |
| Firebase ecosystem, real-time sync  | **Firestore**                                                                                                                                                                                                                        |
| Extreme write throughput, key-value | **DynamoDB** (AWS) or **Cassandra 5** or **ScyllaDB** (Cassandra-compatible; per ScyllaDB's own benchmarks, faster on the same hardware — verify against an independent or workload-specific benchmark before relying on the figure) |
| Embedded / edge key-value           | **SQLite** (WAL mode) or **SlateDB** (LSM-based)                                                                                                                                                                                     |

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
| Dedicated time-series at scale | **InfluxDB 3.10** or **VictoriaMetrics**                   |

---

## Infrastructure by Cloud Provider

### AWS (most feature-rich, highest ops overhead)

```
Compute:      ECS Fargate (containerized, no cluster management) — recommended default
              EKS (Kubernetes, >20 services or if Kubernetes expertise exists)
              EC2 (if GPU workloads or special instance types needed)
Database:     RDS PostgreSQL (managed, Multi-AZ for HA) — default choice, simplest ops
              Aurora PostgreSQL (auto-scaling storage, up to 15 read replicas) — pick this once
              read-heavy scaling or storage growth outpaces what a fixed RDS instance handles
Cache:        ElastiCache (Redis-compatible)
Storage:      S3 + CloudFront (CDN)
Load balancer: ALB (HTTP/HTTPS/WebSocket) + Route 53 (DNS)
Secrets:      AWS Secrets Manager + IAM roles (never access keys in code)
Monitoring:   CloudWatch + AWS X-Ray (or Datadog/Grafana if self-managed preferred — richer
              dashboards/alerting than CloudWatch's native UI)
IaC:          Terraform (multi-cloud portability) or AWS CDK (AWS-native TypeScript — real
              programming-language constructs instead of Terraform's HCL, at the cost of losing
              multi-cloud portability)
```

### GCP (best for ML/data workloads, strong Kubernetes)

```
Compute:      Cloud Run (preferred — serverless containers, scales to zero)
              GKE Autopilot (managed Kubernetes, pay-per-pod — pick this once the team needs
              Kubernetes-native APIs/operators Cloud Run doesn't expose)
Database:     Cloud SQL (PostgreSQL/MySQL, managed) — default choice, simplest ops
              AlloyDB (PostgreSQL-compatible, per Google's own published benchmark: ~4× faster for OLTP than
              standard PostgreSQL — verify against current independent benchmarks for the actual workload before
              treating this figure as guaranteed) — consider once Cloud SQL's throughput becomes the bottleneck
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
              AKS (managed Kubernetes — pick this once the team needs Kubernetes-native
              APIs/operators Container Apps doesn't expose)
Database:     Azure Database for PostgreSQL Flexible Server — default choice for a new Postgres app
              Azure SQL (SQL Server, T-SQL) — pick this only when already committed to SQL Server/
              T-SQL, e.g. migrating an existing .NET system
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
Containers:     Docker Swarm (simple, <20 nodes) or K3s / RKE2 (Kubernetes-lite — same API surface
                as managed Kubernetes above, worth it once approaching that node count or wanting
                Kubernetes-ecosystem tooling)
Database:       PostgreSQL (self-managed) + Barman/pgBackRest (backups)
Cache:          Redis, Valkey, DragonflyDB, or Garnet (self-hosted)
Storage:        MinIO (S3-compatible object storage, standalone or in-cluster, mature and widely deployed) or
                RustFS (same category, Rust-based — still Beta as of this writing, distributed mode not yet
                shipped; treat as staged-adoption territory, not a blind drop-in for MinIO) or Rook (Ceph
                operator — see the Core Platform table above for what it provides)
Load balancer:  Nginx or Caddy (TLS termination, reverse proxy)
Secrets:        HashiCorp Vault (open-source — the same tool named above for cloud/microservices
                secrets, dynamic secrets and rotation) or Infisical (simpler setup, dashboard-first
                UX — pick this for a smaller team that doesn't need Vault's full policy engine)
Monitoring:     Prometheus + Grafana + Loki (full Grafana Stack)
IaC:            Ansible (configuration management) + Terraform (if using cloud hybrid)
```

---

## Authentication and Authorization

### For user-facing web/mobile apps

| Scenario                    | Recommendation                                                                   |
|-----------------------------|----------------------------------------------------------------------------------|
| Full control, self-hosted   | **Keycloak 26** (OAuth2/OIDC, SSO, MFA, RBAC — enterprise-grade)                 |
| Self-hosted, simpler ops    | **Ory Kratos + Hydra** (modern, cloud-native)                                    |
| Self-hosted, lightweight    | **SuperTokens** or **Authentik** (open-source, faster to stand up than Keycloak) |
| Managed, pay-as-you-go      | **Auth0** (Okta) — great DX, generous free tier                                  |
| Firebase ecosystem          | **Firebase Authentication**                                                      |
| AWS ecosystem               | **Amazon Cognito**                                                               |
| B2B SaaS, organization RBAC | **WorkOS** or **Clerk**                                                          |

### For service-to-service authentication

- **mTLS** — mutual TLS via service mesh (Istio/Linkerd) for zero-trust internal auth
- **JWT with shared secret** — for simple internal APIs (avoid for sensitive services)
- **OAuth2 Client Credentials** — for API-to-API calls through an identity provider

### Token format: JWT vs PASETO

Both are stateless, signed/encrypted tokens carried by the client; the difference is how much room for misconfiguration
the format itself leaves:

- **JWT** — the default token format named for every language stack above; the broadest library and tooling support (API
  gateways, identity providers, debuggers) in every ecosystem. Its "algorithm agility" (the `alg` header names the
  algorithm per-token) is also its best-known footgun — an `alg:
  none` or algorithm-confusion attack is a verification-library bug, not a spec requirement, but variants of it have
  recurred across ecosystems over the years. Use a maintained library (named per language above) and pin the expected
  algorithm explicitly; never trust the token's own `alg` header.
- **PASETO** (Platform-Agnostic SEcurity TOkens) — designed specifically to remove that footgun: each version/purpose
  pair (e.g. `v4.local`, `v4.public`) fixes one specific, modern algorithm rather than letting the token declare it.
  Reach for it over JWT when eliminating that misconfiguration surface by construction matters more than JWT's wider
  tooling/gateway support — e.g. no existing API-gateway JWT validation to integrate with.

### Password hashing

**Argon2id** is OWASP's first-choice algorithm for password storage — winner of the 2015 Password Hashing Competition,
memory-hard (resists GPU/ASIC cracking better than bcrypt or PBKDF2). Use the per-language library named in the Auth
line of each stack above. bcrypt remains an acceptable fallback where an existing system already uses it, or a
language's Argon2 bindings aren't mature enough yet — but default to Argon2id for anything new.

### For fine-grained access control (authorization, not authentication)

The table above and the mTLS/JWT/OAuth2 bullets establish *who* a caller is; these libraries decide *what that caller is
allowed to do* — reach for one once role checks alone (a single `role` claim) stop being expressive enough (per-resource
ownership, multi-tenant isolation, attribute-based rules):

| Scenario                                        | Recommendation                                                                                                                                         |
|-------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| Cross-language, in-process policy library       | **Casbin** — RBAC/ABAC/ACL model files, SDKs per language (jCasbin, PyCasbin, node-casbin, casbin-rs)                                                  |
| Policy-as-code, centralized/microservice        | **Open Policy Agent (OPA)** — Rego policy language, sidecar or library, CNCF graduated                                                                 |
| Policy-as-code, dedicated authorization service | **Cerbos** — decouples policy from application code, policy tested independently                                                                       |
| Embedded in application code, typed policies    | **Oso** — Polar policy language, library-embedded rather than a separate service (open-source library now deprecated by the vendor — see caveat below) |

All four are open-source and self-hostable. Pick the in-process library (Casbin, Oso) for a monolith or single service;
pick the dedicated policy service (OPA, Cerbos) for microservices where multiple services need to enforce the same
authorization rules consistently. **Oso caveat**: the vendor has officially deprecated the open-source Oso library (not
end-of-lifed — Oso states it will keep providing support and critical bug fixes, and is discussing a possible future
open-source release) in favor of its commercial hosted product, Oso Cloud — confirm this is still an acceptable
long-term choice before committing to it over Casbin, which remains under active development across all its per-language
SDKs.

---

## Rate Limiting

See `rate-limiting-guide.md` for the full strategy — algorithm tradeoffs, per-tier/per-endpoint limits, the complete
per-stack library table, and the response contract. Enforce it against the same Redis instance already provisioned for
sessions/caching (see the "Cache / session store" table above) for distributed rate-limit counters — do not provision a
second store just for this.

---

## Frontend

| Use Case                        | Recommendation                                                                                                                                                                 |
|---------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| SPA / interactive web app       | **React 19 + TypeScript + Vite**                                                                                                                                               |
| Full-stack with SSR/SSG         | **Next.js 16** (App Router + React Server Components)                                                                                                                          |
| Content-heavy site, fast static | **Astro 7** (island architecture, minimal JS)                                                                                                                                  |
| Admin dashboard                 | **Next.js + shadcn/ui** or **React Router v7/v8** (Framework Mode — Remix merged into React Router in late 2024; there is no longer a standalone "Remix" package to recommend) |
| Mobile cross-platform           | **React Native + Expo** (or Flutter for truly native feel)                                                                                                                     |
| PWA / lightweight               | **Svelte 5 / SvelteKit**                                                                                                                                                       |
| HTMX + server-rendered          | **HTMX** + any backend template engine (simple interactivity without SPA overhead)                                                                                             |

**CSS / UI frameworks**:

- **Tailwind CSS 4** — utility-first, design system via CSS variables
- **shadcn/ui** — accessible, composable components (React + Tailwind)
- **Radix UI** — headless components (bring your own styles)
- **MUI / Ant Design** — opinionated, feature-rich (good for internal tools)

---

## How to justify recommendations in the architecture document

Every technology choice must cite at least one requirement from stages 1–4. Use this pattern (the `$150/month` figure
below is illustrative-only, not a live, verified quote — per `cost-estimation-guide.md`'s dating rule, cite an actual
figure with a WebSearch-verified date or the literal `"estimate — verify at implementation time"` tag when writing a
real document, never a bare unsourced number):

> **PostgreSQL 18** was chosen as the primary database because:
> - The team has 3 years of PostgreSQL experience [Stage 3 — team competencies]
> - The data model is relational with complex joins and ACID transaction
    requirements [Stage 2 — NFR: strong consistency]
> - The estimated 500 TPS write workload is well within PostgreSQL's range with connection
    pooling [Stage 4 — capacity planning]
> - Budget allows for managed RDS (~$150/month for db.t4g.medium) [Stage 3 — budget]

If you cannot trace a recommendation back to a specific user requirement, either find the traceability or reconsider the
recommendation.

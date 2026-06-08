# Architecture Anti-Patterns Reference

Canonical names and descriptions for common architecture anti-patterns. Reference these when naming identified problems in `review-architecture` Step 2 (Architecture Analysis).

---

## Service-Level Anti-Patterns

### God Service / God Object

**What it is**: A single service or class that does everything — authentication, business logic, data access, notifications, reporting, etc. All other parts of the system depend on it.

**Symptoms**: Service has 50+ endpoints; changes to any unrelated feature require touching this service; every other team's deploys are blocked by this service's release cycle.

**Fix**: Decompose by business domain. Apply Single Responsibility Principle at service level. Strangler Fig pattern to extract bounded contexts incrementally.

---

### Distributed Monolith

**What it is**: Architecture that looks like microservices (separate deployable units) but is actually a monolith in disguise — services are tightly coupled through synchronous calls, shared databases, or shared code libraries, making independent deployment impossible.

**Symptoms**: Deploying Service A requires deploying Services B, C, and D at the same time; a failure in one service cascades to all others; services share database tables.

**Fix**: Enforce bounded contexts. Services own their own data stores. Replace synchronous coupling with async events where appropriate.

---

### Shared Database (Integration Database)

**What it is**: Multiple services (or modules) read and write the same database tables. The database becomes the integration layer.

**Symptoms**: Cannot change a table schema without coordinating across multiple teams; one service's poorly optimized query degrades all others; no clear owner for a given table.

**Fix**: Each service owns its schema. Cross-service data access goes through the service's API, not direct DB queries. Consider event-driven sync for read models.

---

### Chatty Microservices

**What it is**: A single user request triggers a cascade of synchronous inter-service HTTP calls — Service A calls B, which calls C, D, E, each adding latency and failure risk.

**Symptoms**: p99 latency is the sum of all downstream service latencies; one slow service degrades the entire flow; circuit breakers trip frequently.

**Fix**: Aggregate calls in a BFF or API composition layer. Use async pre-fetching. Consider merging services whose data is always co-queried.

---

### Nano-Services

**What it is**: Decomposition taken too far — services with a single endpoint or 50 lines of code. The overhead of deployment, discovery, and network hops outweighs any benefit.

**Symptoms**: Dozens of tiny services with no independent scaling justification; every feature change spans 4+ service repos.

**Fix**: Merge services that are always co-deployed. Domain boundary ≠ microservice. A module within a modular monolith is often sufficient.

---

## Data Anti-Patterns

### Anemic Domain Model

**What it is**: Domain objects are plain data bags (getters/setters only). All business logic lives in service or "manager" classes. The object model doesn't reflect the domain.

**Symptoms**: `UserService.validate(user)`, `OrderManager.calculateTotal(order)` — logic is in the service, not the entity; entities are just DTOs.

**Fix**: Move business rules into domain entities/aggregates. Apply DDD tactical patterns (Entities, Value Objects, Aggregates).

---

### One Table to Rule Them All

**What it is**: A single generic table used for all entity types (e.g., a `properties` table with `entity_type`, `key`, `value` columns — Entity-Attribute-Value). Used to avoid schema migrations.

**Symptoms**: Complex queries required to retrieve a single entity; no foreign keys, no referential integrity; impossible to write typed queries.

**Fix**: Proper normalized schema per entity type. Use JSONB columns for truly variable attributes, not EAV.

---

### Missing Indexes on Foreign Keys

**What it is**: FK columns not indexed, causing full table scans on every JOIN.

**Symptoms**: Queries that join `orders.user_id → users.id` become slow as `orders` grows; `EXPLAIN` shows `Seq Scan` on the FK side.

**Fix**: Always index FK columns. Index any column appearing in `WHERE`, `JOIN ON`, or `ORDER BY` clauses in frequent queries.

---

### OLTP + OLAP on Same Database

**What it is**: Heavy analytics queries (aggregations, full table scans) run on the same database that serves live application traffic.

**Symptoms**: Analytics reports cause lock contention and spike response times for end users; autovacuum can't keep up; p99 latencies spike at report generation time.

**Fix**: Read replica for analytics; data warehouse (BigQuery, Redshift, ClickHouse) for complex reporting; materialized views for frequently-needed aggregations.

---

## Operational Anti-Patterns

### Hardcoded Configuration

**What it is**: Database URLs, API keys, feature flags, and environment-specific settings are hardcoded in source code or config files committed to version control.

**Symptoms**: Credentials in git history; different config for dev/prod requires code changes; rotating a secret requires a full redeploy.

**Fix**: Environment variables for all config. Secrets manager (AWS Secrets Manager, Vault) for sensitive values. Config validation at startup.

---

### Manual Deployments

**What it is**: Production deployments are performed manually via SSH, FTP, or running scripts by hand.

**Symptoms**: "Works on my machine" not caught until production; no audit trail of what was deployed when; high error rate in deployments.

**Fix**: Automated CI/CD pipeline. Infrastructure as Code (Terraform, Pulumi). Immutable deployments (containers).

---

### Missing Correlation IDs

**What it is**: Log lines across services don't share a common identifier, making it impossible to trace a single request through the system.

**Symptoms**: "The user reported an error at 2pm" requires manually correlating timestamps across 5 service log streams.

**Fix**: Generate a `correlation_id` (UUID) at the entry point (API gateway or first service). Pass it as an HTTP header (`X-Correlation-ID`) and include it in all log lines. Use structured (JSON) logging.

---

### Big Bang Migration

**What it is**: Schema changes that require taking the database offline, running a long migration, and bringing it back up — causing downtime.

**Symptoms**: Scheduled maintenance windows for DB migrations; single-point rollback is "restore from backup".

**Fix**: Expand-contract (parallel change) pattern. Add nullable column → backfill → add constraint → remove old column. Use `pt-online-schema-change` or `gh-ost` for large tables.

---

### No Timeout on Outbound Calls

**What it is**: HTTP calls to third-party services or internal services have no configured timeout. A single slow dependency hangs threads/goroutines and eventually exhausts connection pools.

**Symptoms**: Application becomes unresponsive when downstream service is slow (not even down); thread pool exhaustion under moderate load.

**Fix**: Always set timeouts on all outbound HTTP calls. Implement circuit breakers (Resilience4j, Polly, `hystrix`). Separate thread pools per downstream dependency (bulkhead pattern).

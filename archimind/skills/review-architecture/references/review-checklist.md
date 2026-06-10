# Architecture Review Checklist

Use this checklist during Step 2 (Architecture Analysis) of the `review-architecture` skill. Evaluate the existing system against each category. Note: not every item applies to every system — skip categories that are clearly irrelevant (e.g., "Distributed Systems" for a single-server app).

---

## 1. Scalability

- [ ] Can individual components scale independently, or must the whole system scale together?
- [ ] Is there a clear bottleneck that limits throughput (e.g., single DB writer, in-process queue)?
- [ ] Are stateless and stateful components clearly separated (enables horizontal scaling of stateless parts)?
- [ ] Are large, synchronous operations (report generation, bulk exports) handled async to avoid blocking?
- [ ] Is there a caching strategy for frequently read, rarely updated data?

**Common findings**: Single monolith that can only scale vertically; missing cache layer causing DB thrashing; synchronous calls to slow third-party APIs blocking request threads.

---

## 2. Coupling & Cohesion

- [ ] Do services or modules have clear, minimal interfaces? Or do they reach into each other's internals?
- [ ] Is there a "God Service" that does too much and is depended on by everything?
- [ ] Are there circular dependencies between modules/services?
- [ ] Is the shared database the integration point between components (shared DB antipattern)?
- [ ] Would changing one component's internal schema break other components?
- [ ] Are concerns properly separated (e.g., business logic in controllers, infrastructure in DAL)?

**Common findings**: Shared mutable database table accessed by 5+ services; business logic in routing layer; tight coupling between unrelated domains through shared models.

---

## 3. Data & Consistency

- [ ] Is the database normalized appropriately for its workload (OLTP vs. OLAP)?
- [ ] Are indexes in place for all high-frequency query patterns?
- [ ] Is there N+1 query behavior in ORM usage?
- [ ] Is the same data duplicated across multiple tables/services without a clear sync strategy?
- [ ] Are transactions used correctly, and is the isolation level appropriate?
- [ ] Is there a clear boundary between the write model (source of truth) and read model (projections)?
- [ ] Is time-series data stored in a relational DB when a time-series DB would be more appropriate?

**Common findings**: Missing indexes on FK columns; N+1 queries from lazy loading; analytics queries running on OLTP database causing lock contention.

---

## 4. Observability

- [ ] Is there structured logging (JSON logs with correlation IDs)?
- [ ] Is there distributed tracing across service boundaries?
- [ ] Are key business metrics tracked (not just infrastructure metrics)?
- [ ] Are error rates, p95/p99 latencies, and SLA thresholds monitored?
- [ ] Is there alerting for degraded states, not just outages?
- [ ] Can you trace a single user request end-to-end through logs?

**Common findings**: Printf-style logs with no structure; no correlation IDs making debugging impossible in production; only infrastructure metrics (CPU/RAM) without business-level alerts.

---

## 5. Security

- [ ] Are secrets (DB credentials, API keys) stored in environment variables or a secrets manager, not in code?
- [ ] Is authentication (AuthN) separated from authorization (AuthZ)?
- [ ] Is input validated and sanitized at all system boundaries?
- [ ] Is principle of least privilege applied to service-to-service calls?
- [ ] Are admin APIs protected separately from public APIs?
- [ ] Is data encrypted at rest and in transit?
- [ ] Are dependency vulnerabilities scanned regularly?

**Common findings**: Secrets hardcoded in config files checked into git; no rate limiting on auth endpoints; overly permissive service accounts.

---

## 6. Operational Complexity

- [ ] Can the system be deployed without downtime (rolling deployments, blue-green, canary)?
- [ ] Are database migrations safe to run on a live system?
- [ ] Is the local development environment representative of production?
- [ ] Are there runbooks for common failure scenarios?
- [ ] Is the deployment pipeline (CI/CD) automated and reliable?
- [ ] Are dependencies explicitly versioned (reproducible builds)?

**Common findings**: Deployments require maintenance windows; migrations that take exclusive locks on large tables; "works on my machine" issues from environment drift.

---

## 7. Distributed Systems (if applicable)

- [ ] Are network failures handled gracefully (retries with backoff, circuit breakers)?
- [ ] Is there a strategy for handling partial failures (saga pattern, compensating transactions)?
- [ ] Is eventual consistency acceptable everywhere it occurs, or are there hidden consistency requirements?
- [ ] Is the service mesh / API gateway properly configured for timeouts and load balancing?
- [ ] Are idempotency keys used for critical operations (payments, order creation)?

**Common findings**: No timeout on outbound HTTP calls (single slow downstream cascades to full outage); missing idempotency on payment endpoints; chatty inter-service communication on the hot path.

---

## Anti-Pattern Quick Reference

| Anti-Pattern            | Description                                                         |
|-------------------------|---------------------------------------------------------------------|
| God Service             | One service does everything; all others depend on it                |
| Shared Database         | Multiple services share the same DB schema and tables               |
| Chatty Microservices    | Services make dozens of sync calls per user request                 |
| Distributed Monolith    | Microservices but deployed together; tightly coupled via sync calls |
| Premature Microservices | Microservices before domain boundaries are understood               |
| Anemic Domain Model     | Business logic in services/controllers, not domain objects          |
| Magic Strings           | Domain state encoded as raw strings instead of enums/types          |
| Hardcoded Configuration | Environment-specific values in source code                          |
| Missing Correlation IDs | Logs across services cannot be linked to a single request           |
| Big Bang Migration      | Large schema change requiring downtime on production DB             |

Refer to these canonical names when writing the analysis summary to keep descriptions precise and searchable.

---

## 8. Single Points of Failure (SPOF)

- [ ] Is there any single component whose failure causes a full or partial system outage?
- [ ] Is the primary database a SPOF? (no read replica, no failover, no connection pooling)
- [ ] Is there a single load balancer, API gateway, or message broker with no HA configuration?
- [ ] Are background jobs or cron tasks running on a single server with no failover?
- [ ] Are external dependency calls (third-party APIs, payment gateways) handled with fallback behavior?
- [ ] Is there a "hero engineer" dependency — does the system require specific human intervention to recover?

For each SPOF identified: quantify **blast radius** (what fraction of users/features are affected?) and **detection time** (does monitoring alert within seconds, minutes, or after user complaints?).

**Common findings**: Primary DB with no replica — full outage on any DB failure; single Redis instance caching all sessions — cache failure logs everyone out; no circuit breaker on third-party payment API — one slow upstream causes request queue backup.

---

## 9. Disaster Recovery & Business Continuity

- [ ] Are RTO (Recovery Time Objective) and RPO (Recovery Point Objective) targets defined and documented?
- [ ] Is there an automated backup strategy with tested restore procedures?
- [ ] Is the last backup restore time known? (A backup that has never been tested is not a backup.)
- [ ] Is there a runbook for the most critical failure scenarios (DB corruption, cloud region outage, security breach)?
- [ ] Is data replicated across availability zones or regions proportionate to the stated SLA?
- [ ] Are deployments reversible? Is rollback documented and tested?
- [ ] Is there a documented incident response process, including on-call rotation?

**Common findings**: Backups exist but restore procedure has never been tested; RTO/RPO targets never defined ("we'll recover as fast as we can"); no multi-AZ for a product with 99.9% SLA commitment.

---

## 10. Technical Debt

- [ ] Are there known workarounds or "temporary" solutions that have become permanent?
- [ ] Is there undocumented logic that only specific team members understand?
- [ ] Are dependencies outdated or end-of-life? (language runtime, framework major versions, cloud service deprecations)
- [ ] Are there "god files" or modules that have grown beyond a manageable size?
- [ ] Is there duplicated business logic across services or layers?
- [ ] Have architectural decisions been documented (ADRs)? If not, is the rationale for current patterns known?
- [ ] Are integration tests missing for critical paths, creating risk in any change?

**Common findings**: 5-year-old "temporary" authentication workaround now handling all auth; Node.js 14 on end-of-life runtime; no ADRs — the team doesn't know why the current architecture was chosen, making refactoring politically impossible.

---

## 11. Cost & Infrastructure Efficiency

- [ ] Is infrastructure cost visible and tracked? (cloud cost dashboards, budget alerts)
- [ ] Are there obvious over-provisioned resources? (VMs with < 20% CPU, oversized RDS instances)
- [ ] Are ephemeral/batch workloads running on always-on infrastructure instead of spot instances or serverless?
- [ ] Is data egress optimized? (CDN for static assets, avoid cross-region traffic)
- [ ] Are unused resources cleaned up? (orphaned snapshots, idle instances, unused Elastic IPs)
- [ ] Is auto-scaling configured, or is the system permanently sized for peak load?

**Common findings**: Production DB instance sized for theoretical peak but averaging 5% CPU; no CDN for a media-heavy app paying per-GB egress; logs retained forever with no TTL policy.

---

## 12. API Design & Versioning

- [ ] Is there an API versioning strategy? (`/v1/`, `/v2/`, headers, or content negotiation)
- [ ] Are breaking changes to the API documented and communicated with a deprecation period?
- [ ] Is the API contract validated? (OpenAPI/Swagger spec, schema validation on input)
- [ ] Are API responses consistent in structure? (envelope pattern, error format)
- [ ] Is pagination implemented for list endpoints? (cursor-based preferred over offset for large datasets)
- [ ] Are internal service APIs versioned the same way as external-facing APIs?

**Common findings**: No versioning strategy — all clients break on the next API change; offset pagination on a 10M-row table timing out at page 500; inconsistent error response formats across endpoints.

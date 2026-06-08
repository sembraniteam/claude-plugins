# Database Selection Guide

A comprehensive reference for selecting the right database category and engine for a given architecture. Use this when filling out the "Data Layer Design" section of each architecture option.

---

## Quick Decision Framework

```
What is the shape of the data?
├── Structured, relationships, ACID transactions needed?
│   └── → Relational (PostgreSQL, MySQL, SQLite)
├── Flexible/evolving schema, nested objects, no complex joins?
│   └── → Document store (MongoDB, Firestore, Couchbase)
├── Simple key→value lookups, sessions, caching, leaderboards?
│   └── → Key-value store (Redis, DynamoDB, Memcached)
├── Write-heavy, wide rows, high cardinality, distributed first?
│   └── → Column-family (Cassandra, ScyllaDB, HBase)
├── Time-ordered events, metrics, IoT, aggregations over time?
│   └── → Time-series (InfluxDB, TimescaleDB, ClickHouse, QuestDB)
├── Relationships between entities, graph traversals?
│   └── → Graph (Neo4j, Amazon Neptune, ArangoDB)
├── Full-text search, faceted filtering, relevance ranking?
│   └── → Search engine (Elasticsearch, Meilisearch, Typesense, OpenSearch)
├── Large-scale analytics, data warehouse, OLAP queries?
│   └── → OLAP/Warehouse (ClickHouse, BigQuery, Redshift, DuckDB)
├── Global distribution, multi-region writes, SQL compatibility?
│   └── → NewSQL (CockroachDB, TiDB, PlanetScale, Spanner)
└── Files, media, blobs, large objects?
    └── → Object storage (S3, GCS, MinIO, Cloudflare R2)
```

---

## 1. Relational Databases

### PostgreSQL
**Best for**: OLTP, complex queries, JSON/JSONB hybrid data, time-series (via TimescaleDB extension), full-text search (via pg_trgm, tsvector), geospatial (PostGIS).

**Strengths**: ACID, mature ecosystem, rich extension system, excellent query planner, supports JSONB natively, active community.

**Weaknesses**: Vertical scaling only by default (Citus for horizontal), operational overhead compared to managed services.

**When to choose**: Default choice for most new applications. Excellent for e-commerce, SaaS, CMS, fintech, healthcare. Use PostgreSQL unless you have a specific reason not to.

**Future impact**: Scales to ~100k concurrent connections with connection poolers (PgBouncer, Pgpool). Horizontal scaling via Citus or Patroni. Very low risk of abandonment (25+ years, still actively developed).

---

### MySQL / MariaDB
**Best for**: Web applications, read-heavy workloads, simple OLTP.

**Strengths**: Widely understood, large talent pool, very mature, many hosted options.

**Weaknesses**: Historically weaker JSON support than PostgreSQL, fewer extensions, full-text search is basic.

**When to choose**: When the team has deep MySQL expertise, or when using a MySQL-specific managed service (PlanetScale, Amazon Aurora MySQL).

---

### SQLite
**Best for**: Local/embedded databases, mobile apps, desktop apps, single-user tools, testing.

**Strengths**: Zero configuration, single file, no server process, very fast for small workloads.

**Weaknesses**: Not suitable for multi-process write concurrency.

**When to choose**: Embedded use cases only. Also, excellent for prototypes and test environments.

---

## 2. Document Stores

### MongoDB
**Best for**: Flexible schemas, nested/hierarchical data, content management, product catalogs, user profiles, IoT device data.

**Strengths**: Schema flexibility, native JSON documents, rich aggregation pipeline, Atlas managed service, good geospatial support.

**Weaknesses**: No true ACID transactions across documents (added in v4.0 but with caveats), can lead to over-denormalization, operational complexity of replica sets.

**When to choose**:
- Data is naturally hierarchical (e.g., blog posts with embedded comments)
- Schema changes are frequent during development
- Team is JavaScript/Node.js oriented

**When NOT to choose**:
- Strong relational consistency required
- Complex multi-collection joins are frequent
- Small team — PostgreSQL with JSONB often suffices

**Future impact**: Scales horizontally via sharding. However, migration away from MongoDB later is painful if you have complex data. Consider whether JSONB in PostgreSQL meets your needs first.

---

### Firestore (Google)
**Best for**: Mobile/web apps needing real-time sync, serverless Firebase apps.

**Strengths**: Real-time listeners, offline support, scales automatically, no server management.

**Weaknesses**: Vendor lock-in (Google), complex pricing at scale, limited query expressiveness (no joins, no aggregations), single-region by default.

**When to choose**: Firebase apps, prototypes, consumer mobile apps needing offline sync.

---

## 3. Key-Value Stores

### Redis
**Best for**: Caching, sessions, rate limiting, leaderboards, pub/sub, queues (Redis Streams), distributed locks.

**Strengths**: In-memory (sub-millisecond latency), rich data structures (strings, hashes, sets, sorted sets, streams), Lua scripting, cluster support.

**Weaknesses**: Data must fit in RAM (though RDB/AOF persistence exists), not a primary database for complex queries.

**When to choose**: Almost always as a cache layer alongside a primary relational or document DB. Excellent for:
- Session storage
- Rate limiting (token bucket via sorted sets)
- Real-time leaderboards
- Job queues (Redis Streams or BullMQ)
- Pub/sub messaging
- Distributed lock management

**Future impact**: Low operational risk. Redis Ltd. maintains it. RedisCloud and Upstash are managed options. Adding Redis to an existing stack is low-risk and high-reward for latency reduction.

---

### DynamoDB (AWS)
**Best for**: Serverless apps on AWS, high-throughput key-value access, event sourcing stores at scale.

**Strengths**: Fully managed, auto-scaling, single-digit ms latency at any scale, DynamoDB Streams for CDC.

**Weaknesses**: Single-vendor lock-in (AWS), complex data modeling (everything via primary key + sort key), expensive at high throughput, queries outside the key pattern require expensive scans.

**When to choose**: AWS-native serverless architectures where query patterns are known and simple.

---

### Memcached
**Best for**: Simple in-memory caching only.

**Strengths**: Slightly faster than Redis for pure cache-get/set workloads, multithreaded.

**Weaknesses**: No persistence, no data structures beyond strings, no cluster coordination.

**When to choose**: Choose Redis unless raw cache throughput with zero data-structure features is the only requirement. Memcached is rarely the right choice for new projects.

---

## 4. Column-Family Stores

### Apache Cassandra / ScyllaDB
**Best for**: Write-heavy workloads, time-series data at IoT scale, globally distributed data, high availability with no single point of failure.

**Strengths**: Linear horizontal scaling, no single master, multi-datacenter replication, excellent write throughput.

**Weaknesses**: No ACID transactions (lightweight transactions only), no joins, data model must be designed around query patterns, steep learning curve, operational complexity.

**When to choose**:
- Hundreds of millions of writes per day
- Time-series events, activity logs, sensor data at IoT scale
- Multi-region, multi-datacenter writes required
- Team has Cassandra/CQL experience

**When NOT to choose**:
- Team is small (< 5 engineers) — operational overhead is high
- Query patterns are unknown — designing a Cassandra schema requires knowing queries upfront
- Strong consistency required — TimescaleDB or ClickHouse is often a better fit for time-series

**Future impact**: Once committed to Cassandra, migrating away is very costly. High operational overhead. ScyllaDB is a faster Cassandra-compatible alternative with lower JVM overhead.

---

## 5. Time-Series Databases

### InfluxDB
**Best for**: Infrastructure metrics, APM data, IoT sensor readings, financial tick data.

**Strengths**: Purpose-built for time-series, high write throughput, built-in retention policies and downsampling, Flux query language.

**Weaknesses**: Flux language has a learning curve, OSS version has limitations compared to Cloud.

---

### TimescaleDB
**Best for**: Time-series data with complex SQL queries, when PostgreSQL familiarity is valued.

**Strengths**: Built on PostgreSQL (full SQL support), automatic partitioning by time, compression, continuous aggregates, compatible with all PostgreSQL tooling.

**When to choose**: Time-series workloads when the team knows SQL and PostgreSQL. Often the best choice for IoT, monitoring, and financial data where InfluxDB's absolute write throughput ceiling is not required.

---

### ClickHouse
**Best for**: OLAP analytics, real-time dashboards, large-scale aggregation queries, log analysis, clickstream data.

**Strengths**: Extremely fast columnar storage, vectorized query execution, excellent compression, scales to petabytes, near real-time ingestion.

**Weaknesses**: Not suitable as a transactional (OLTP) database, limited UPDATE/DELETE support, eventual consistency in replicated mode.

**When to choose**:
- Analytical queries on hundreds of millions to billions of rows
- Real-time dashboards and reporting
- Log aggregation and analysis (alternative to Elasticsearch for analytics)
- Event-driven data pipelines with heavy aggregations

**Future impact**: ClickHouse is increasingly the standard for OLAP alongside BigQuery/Redshift. Excellent long-term bet. Managed services: ClickHouse Cloud, Altinity.

---

### QuestDB
**Best for**: Financial data, ultra-high frequency time-series (millions of events/second), tick data.

**Strengths**: Fastest write throughput in its class, SQL interface, low latency reads.

---

## 6. Graph Databases

### Neo4j
**Best for**: Social networks, recommendation engines, fraud detection, knowledge graphs, network topology, access control (RBAC hierarchies).

**Strengths**: Native graph storage, Cypher query language (intuitive for graph traversals), ACID, mature ecosystem.

**Weaknesses**: Not designed for high-volume OLTP, operational overhead, licensing (Enterprise is costly).

**When to choose**:
- The core value of your product depends on graph relationships (e.g., LinkedIn-style connections, fraud detection, recommendation systems)
- Recursive relationship queries are frequent and performance-critical

**When NOT to choose**:
- Relationships exist but aren't the primary query pattern — PostgreSQL with recursive CTEs suffices

---

### Amazon Neptune
**Best for**: Managed graph DB on AWS, supports both Gremlin (TinkerPop) and SPARQL (RDF).

**When to choose**: AWS-native architecture needing a managed graph DB.

---

## 7. Search Engines

### Elasticsearch / OpenSearch
**Best for**: Full-text search, log aggregation (ELK stack), faceted search, geospatial search.

**Strengths**: Powerful full-text search, distributed, scalable, rich query DSL, aggregations.

**Weaknesses**: Operational complexity (Java JVM, cluster management), expensive at scale, not a primary DB.

**When to choose**: When full-text search is a core feature and pg_trgm/tsvector in PostgreSQL is insufficient. Also, standard for log aggregation in the ELK/EFK stack.

---

### Meilisearch
**Best for**: Product search, e-commerce search, developer-friendly full-text search.

**Strengths**: Easy to set up, typo tolerance, instant search, excellent developer experience, open-source.

**Weaknesses**: Less mature than Elasticsearch, fewer analytics features.

**When to choose**: For product catalog search or content search where simplicity is valued over power. Good for small to medium scale.

---

### Typesense
**Best for**: Similar to Meilisearch — fast, typo-tolerant search with a simpler API.

---

## 8. NewSQL (Global Distributed SQL)

### CockroachDB
**Best for**: Multi-region applications needing SQL + strong consistency + horizontal scale + PostgreSQL wire-compatible.

**Strengths**: Distributed ACID, PostgreSQL wire protocol, geo-partitioning, auto-rebalancing.

**Weaknesses**: Higher latency than single-node PostgreSQL (due to consensus protocol), complex pricing, overkill for single-region apps.

**When to choose**:
- Multi-region active-active with strong consistency requirement
- Replacing PostgreSQL that has hit vertical scaling limits
- Global SaaS that needs data residency compliance

---

### PlanetScale
**Best for**: MySQL-compatible serverless database for web apps at scale (horizontal sharding via Vitess).

**Strengths**: Branch-based schema changes, no downtime migrations, excellent DX, scales horizontally.

**Weaknesses**: MySQL-based (no advanced PostgreSQL features), no foreign key constraints enforced at DB level.

---

## 9. Object Storage

### AWS S3 / Google Cloud Storage / MinIO / RustFS
**Best for**: Files, images, videos, backups, large blobs, static assets, data lake storage.

**Key principle**: Never store large files in a relational database. Store the file in object storage and keep only the URL/key in the database.

**MinIO**: Self-hosted S3-compatible object storage written in Go. Mature, widely deployed, large community. Use for on-premise or when avoiding cloud vendor lock-in.

**RustFS**: Self-hosted S3-compatible object storage written in Rust. Offers lower memory footprint and better memory safety than MinIO due to Rust's ownership model. Performant alternative for resource-constrained or security-sensitive on-premise deployments. Still maturing compared to MinIO but gaining adoption rapidly.

**When to choose RustFS over MinIO**:
- Running on constrained hardware (lower RAM usage)
- Security-sensitive environment (Rust eliminates whole classes of memory bugs)
- Team is Rust-native and wants a consistent language stack on the infrastructure layer
- Evaluating next-generation S3-compatible storage with a more modern codebase

---

## Polyglot Persistence: The Standard for Backend Applications

**Using a single database for an entire backend application is the exception, not the rule.** Each database category was designed to solve a specific class of access pattern. Forcing one DB to handle all patterns results in either poor performance, excessive complexity, or both.

A typical production backend uses **3–5 database engines** in combination:

```
Backend application → uses these stores simultaneously:

1. Relational DB      → durable, transactional data (users, orders, payments)
2. Redis              → cache, sessions, rate limits, queues, pub/sub
3. Search engine      → full-text search, faceted filtering (if search is a feature)
4. OLAP / Analytics   → reports, dashboards, aggregations (if analytics is needed)
5. Object storage     → files, images, user uploads (if file storage is needed)
```

### Why a Single Database Cannot Do Everything Well

| Access pattern              | Why the primary relational DB struggles             | Better fit                  |
|-----------------------------|-----------------------------------------------------|-----------------------------|
| Session / hot-key lookup    | Relational DBs have network + disk overhead for KV  | Redis (in-memory, <1ms)     |
| Full-text search            | B-tree indexes cannot do relevance ranking or typos | Meilisearch / Elasticsearch |
| Aggregations over 100M rows | OLTP row store is slow for column scans             | ClickHouse (columnar)       |
| File/blob storage           | Binary in DB wastes I/O, harms backup size          | S3 / MinIO / RustFS         |
| Async background jobs       | Polling a DB table is wasteful, hard to scale       | Redis Streams / Kafka / MQ  |
| Time-series events at scale | Relational tables with timestamps degrade quickly   | TimescaleDB / InfluxDB      |

### Standard Backend Data Stacks by Application Type

| Application Type   | Primary DB             | Cache | Search                      | Analytics  | Files   | Queue          |
|--------------------|------------------------|-------|-----------------------------|------------|---------|----------------|
| SaaS (basic)       | PostgreSQL             | Redis | Meilisearch                 | —          | S3      | Redis Streams  |
| SaaS (scaled)      | PostgreSQL             | Redis | Elasticsearch               | ClickHouse | S3      | Kafka          |
| E-commerce         | PostgreSQL             | Redis | Elasticsearch               | ClickHouse | S3      | RabbitMQ/Kafka |
| Social network     | PostgreSQL             | Redis | Elasticsearch               | BigQuery   | S3      | Kafka          |
| Content / media    | PostgreSQL             | Redis | Meilisearch / Elasticsearch | BigQuery   | S3 / R2 | Redis Streams  |
| Fintech            | PostgreSQL/CockroachDB | Redis | —                           | ClickHouse | S3      | Kafka          |
| IoT / telemetry    | TimescaleDB            | Redis | —                           | ClickHouse | S3      | Kafka          |
| Gaming             | PostgreSQL             | Redis | —                           | ClickHouse | S3      | Redis Streams  |
| Mobile backend     | PostgreSQL             | Redis | Meilisearch                 | —          | S3      | Redis Streams  |
| Analytics platform | PostgreSQL             | Redis | Elasticsearch               | ClickHouse | S3      | Kafka          |

### Operational Cost of Each Additional Store

Adding a new database type is not free — each adds:

| Store added   | Operational cost                                                   |
|---------------|--------------------------------------------------------------------|
| Redis         | Low — managed options (Upstash, Redis Cloud) keep overhead minimal |
| Meilisearch   | Low — single binary, simple ops                                    |
| Elasticsearch | Medium-High — JVM, cluster management, expensive at scale          |
| ClickHouse    | Medium — ClickHouse Cloud simplifies ops significantly             |
| Kafka         | High — ZooKeeper/KRaft, partition management, consumer group ops   |
| TimescaleDB   | Low — PostgreSQL extension, same ops as PostgreSQL                 |
| Neo4j         | Medium — graph-specific ops, separate backup strategy              |
| S3 / MinIO    | Low — object storage is operationally lightweight                  |

**Rule of thumb**: Add Redis almost always. Add Meilisearch/Search when search is a feature. Add ClickHouse when reporting/analytics requirements exist. Add Kafka when event volume, fan-out to multiple consumer groups, cross-service event retention, or replay requirements exceed what Redis Streams handles. Justify every other addition explicitly.

> **Social networks** may additionally need Neo4j for graph traversal (friends-of-friends, recommendations). See section 6 (Graph Databases) for details.

---

## Database Category Quick Reference

| Category       | Examples                              | Read  | Write | Scale  | Consistency | Use Case                              |
|----------------|---------------------------------------|-------|-------|--------|-------------|---------------------------------------|
| Relational     | PostgreSQL, MySQL                     | Fast  | Good  | Vert.  | Strong ACID | OLTP, SaaS, e-commerce                |
| Document       | MongoDB, Firestore                    | Fast  | Fast  | Horiz. | Eventual    | CMS, catalog, profiles                |
| Key-Value      | Redis, DynamoDB                       | ★★★★★ | ★★★★★ | Horiz. | Varies      | Cache, session, rate limit            |
| Column-Family  | Cassandra, ScyllaDB                   | Fast  | ★★★★★ | Horiz. | Tunable     | IoT logs, activity feeds              |
| Time-Series    | InfluxDB, TimescaleDB, ClickHouse     | Fast  | ★★★★★ | Horiz. | Eventual    | Metrics, sensors, analytics           |
| Graph          | Neo4j, Neptune                        | Fast  | Good  | Vert.  | Strong ACID | Social, fraud, recommendations        |
| Search         | Elasticsearch, Meilisearch            | Fast  | Good  | Horiz. | Eventual    | Full-text, faceted search             |
| OLAP/Warehouse | ClickHouse, BigQuery, Redshift        | Fast  | Batch | Horiz. | Eventual    | Reporting, aggregations               |
| NewSQL         | CockroachDB, TiDB                     | Fast  | Good  | Horiz. | Strong ACID | Multi-region OLTP                     |
| Object Storage | S3, GCS, MinIO                        | Fast  | Good  | Horiz. | Eventual    | Files, blobs, backups                 |

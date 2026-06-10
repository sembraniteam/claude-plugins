# Database Index Guide

A reference for selecting the correct index type and defining index strategy. Use during the Define Indexes step of database design.

---

## Index Selection Matrix

| Index Type    | Use Case                                                   | Engines                      | Notes                                                                 |
|---------------|------------------------------------------------------------|------------------------------|-----------------------------------------------------------------------|
| **B-tree**    | Equality, range, ORDER BY, most queries                    | All                          | Default. Use for 90% of cases.                                        |
| **Hash**      | Equality only (`=`), never range                           | PostgreSQL, MySQL            | Faster than B-tree for pure equality at scale                         |
| **GiST**      | Geometric, range types, full-text (tsvector)               | PostgreSQL                   | Extensible; enables custom index types                                |
| **GIN**       | Array containment (`@>`), JSONB keys, full-text            | PostgreSQL                   | Slower to build/update; fast multi-value queries                      |
| **BRIN**      | Sequential/correlated data (timestamps, serial IDs)        | PostgreSQL                   | Very small; good for time-series append-only                          |
| **Full-text** | Natural language search (`MATCH AGAINST`)                  | MySQL, PostgreSQL (tsvector) | Use GIN+tsvector in PG; FULLTEXT in MySQL                             |
| **Partial**   | Index a subset of rows (`WHERE is_active = true`)          | PostgreSQL, SQLite           | Smaller, faster for known predicates                                  |
| **Composite** | Multi-column queries (left-prefix rule applies)            | All                          | Column order critical (most selective first for equality; range last) |
| **Covering**  | Index includes all columns the query needs (no heap fetch) | PostgreSQL (INCLUDE), MySQL  | Use when same columns always fetched                                  |

---

## B-tree Index (Default)

The right choice for nearly everything:

```sql
-- Simple single-column
CREATE INDEX idx_users_email ON users(email);

-- Composite: equality on (status), then range on (created_at)
-- Correct order: equality columns first, range column last
CREATE INDEX idx_orders_status_created ON orders(status, created_at);
-- Supports: WHERE status = 'pending' ORDER BY created_at DESC
-- Does NOT support: WHERE created_at > ... (without status prefix)
```

**Left-prefix rule**: A composite index on `(a, b, c)` supports queries filtering on:
- `a` alone ✓
- `a, b` ✓
- `a, b, c` ✓
- `b` alone ✗ (cannot skip `a`)
- `b, c` alone ✗

---

## Partial Index

Index only rows that match a condition. Dramatically reduces index size when many rows won't be queried by that predicate:

```sql
-- Only index unprocessed jobs (most queries only look at unprocessed)
CREATE INDEX idx_jobs_unprocessed ON jobs(created_at)
WHERE status = 'pending';

-- Only index active users
CREATE INDEX idx_users_active_email ON users(email)
WHERE is_active = true;
```

**Use when**: A query always includes a fixed condition in WHERE that significantly filters the result set.

---

## GIN Index (PostgreSQL)

Best for JSONB queries and full-text search:

```sql
-- JSONB containment queries
CREATE INDEX idx_products_attrs ON products USING GIN(attributes);
-- Supports: WHERE attributes @> '{"color": "red"}'

-- Full-text search
ALTER TABLE articles ADD COLUMN search_vector tsvector;
UPDATE articles SET search_vector = to_tsvector('english', title || ' ' || body);
CREATE INDEX idx_articles_search ON articles USING GIN(search_vector);
-- Supports: WHERE search_vector @@ to_tsquery('architecture & design')
```

---

## BRIN Index (PostgreSQL)

Ultra-compact index for naturally ordered data. Does not store per-row data, only min/max per block range:

```sql
-- Time-series table where rows are always appended in chronological order
CREATE INDEX idx_events_created_brin ON events USING BRIN(created_at);
```

**When to use**: Append-only tables (logs, events, sensor data) where `created_at` or `id` is naturally correlated with physical row order. Size: ~1/1000 of a B-tree index for the same column.

**When NOT to use**: Random-order data, columns frequently updated, small tables.

---

## Covering Index (PostgreSQL `INCLUDE`)

Adds non-indexed columns to the index leaf pages. Queries that fetch only those columns skip the table heap entirely (index-only scan):

```sql
-- Query: SELECT email, name FROM users WHERE email = ?
-- Without INCLUDE: index lookup + heap fetch for 'name'
-- With INCLUDE: index-only scan, no heap fetch
CREATE INDEX idx_users_email_cover ON users(email) INCLUDE (name);
```

**Use when**: A high-frequency query always fetches the same small set of columns alongside the indexed column.

---

## Foreign Key Indexes

Always index FK columns. PostgreSQL does NOT create them automatically:

```sql
CREATE TABLE orders (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL REFERENCES users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Always add this:
CREATE INDEX idx_orders_user_id ON orders(user_id);
-- Supports: "SELECT * FROM orders WHERE user_id = ?" (user's order history)
-- Required for: DELETE FROM users CASCADE (without it: full table scan)
```

---

## Unique Index / Constraint

Unique constraints are implemented as unique indexes in most engines:

```sql
-- Single column unique
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);
-- Or equivalently:
ALTER TABLE users ADD CONSTRAINT uq_users_email UNIQUE (email);

-- Composite unique
CREATE UNIQUE INDEX idx_enrollments_user_course ON course_enrollments(user_id, course_id);
```

---

## Index Strategy by Query Pattern

| Query Pattern                          | Recommended Index                         |
|----------------------------------------|-------------------------------------------|
| `WHERE id = ?`                         | Primary key (automatic)                   |
| `WHERE email = ?`                      | B-tree on email                           |
| `WHERE status = ? ORDER BY created_at` | Composite B-tree (status, created_at)     |
| `WHERE created_at BETWEEN ? AND ?`     | B-tree on created_at; BRIN if append-only |
| `WHERE attrs @> '{"key": "val"}'`      | GIN on JSONB column                       |
| `WHERE search @@ to_tsquery(?)`        | GIN on tsvector column                    |
| `WHERE is_active = true` (selective)   | Partial index with WHERE clause           |
| `SELECT a, b WHERE c = ?` (hot query)  | Covering index: (c) INCLUDE (a, b)        |

---

## Table Partitioning

For tables projected to exceed **10–50M rows** or with heavy time-range queries, consider partitioning before the table grows — retrofitting partitioning onto a large live table requires downtime or complex online migration.

### Partition Types (PostgreSQL)

| Type    | Use case                           | Example                                       |
|---------|------------------------------------|-----------------------------------------------|
| `RANGE` | Time-series, date-based archiving  | Partition `events` by `created_at` month/year |
| `LIST`  | Discrete known values              | Partition `orders` by `region` or `status`    |
| `HASH`  | Uniform distribution across shards | Partition `user_data` by hash of `user_id`    |

```sql
-- RANGE partition on created_at (monthly)
CREATE TABLE events (
  id         BIGSERIAL,
  user_id    BIGINT NOT NULL,
  event_type VARCHAR(50),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
) PARTITION BY RANGE (created_at);

CREATE TABLE events_2025_01 PARTITION OF events
  FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
CREATE TABLE events_2025_02 PARTITION OF events
  FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
```

**Key rules:**
- Primary key must include the partition column (PostgreSQL requirement)
- Indexes are per-partition — create on parent, propagated automatically
- Use `pg_partman` extension to automate partition creation/maintenance
- Old partitions can be detached and archived without locking the live table

**When NOT to partition**: Tables under 10M rows — the overhead (query planner complexity, partition pruning) rarely pays off at small scale.

---

## Over-Indexing: What to Avoid

Indexes are not free:
- Each index consumes disk space
- Each `INSERT`, `UPDATE`, `DELETE` must update all indexes on the table
- Too many indexes slows write-heavy tables significantly

**Avoid**:
- Indexing every column "just in case"
- Duplicate indexes (`(a)` and `(a, b)` — the second makes the first redundant for equality on `a`)
- Indexing low-cardinality columns (`gender`, `boolean flags`) with B-tree — partial indexes or no index often better
- Indexing rarely-queried columns

**Check for unused indexes** (PostgreSQL):
```sql
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY tablename;
```

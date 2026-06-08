# Data Types Guide

Recommendations for choosing the right column data type. Engine-specific notes for PostgreSQL, MySQL, and SQLite.

---

## Core Principles

1. **Use the smallest type that fits**: `SMALLINT` over `BIGINT` for a 0–100 counter; `VARCHAR(50)` over `TEXT` in MySQL when length is enforced.
2. **Never use FLOAT/DOUBLE for money**: Binary floating-point cannot represent 0.10 exactly. Use `NUMERIC(p,s)` or `DECIMAL`.
3. **Store timestamps in UTC**: Always. Display in local time at the application layer.
4. **Prefer surrogate keys**: `BIGSERIAL`/`BIGINT AUTO_INCREMENT`/`UUID` over natural keys unless the natural key is truly stable and simple.

---

## Numeric Types

| Type                       | Range / Precision                   | Use For                                   | Notes                             |
|----------------------------|-------------------------------------|-------------------------------------------|-----------------------------------|
| `SMALLINT`                 | -32,768 to 32,767                   | Status codes, small counters, ratings     | 2 bytes                           |
| `INTEGER` / `INT`          | -2.1B to 2.1B                       | Most IDs, counters, quantities            | 4 bytes                           |
| `BIGINT`                   | -9.2 quintillion to 9.2 quintillion | Large IDs, high-volume counters           | 8 bytes                           |
| `SERIAL` / `BIGSERIAL`     | Auto-increment INTEGER / BIGINT     | Surrogate PKs (PostgreSQL)                | Alias for `INT DEFAULT nextval()` |
| `NUMERIC(p,s)` / `DECIMAL` | Arbitrary precision                 | Money, financial, scientific calculations | Exact; slower than int            |
| `REAL` / `FLOAT4`          | 6 decimal digits precision          | Scientific data (non-financial)           | NOT for money                     |
| `DOUBLE PRECISION`         | 15 decimal digits precision         | Scientific data (non-financial)           | NOT for money                     |
| `BOOLEAN`                  | true/false                          | Flags                                     | Use 0/1 in MySQL (no native bool) |

**Money example**:
```sql
price NUMERIC(12, 2)  -- up to 9,999,999,999.99
-- Or store in cents as BIGINT and convert at app layer (common pattern)
price_cents BIGINT NOT NULL  -- 1099 = $10.99
```

---

## String Types

| Type         | PostgreSQL                  | MySQL                         | Use For                                      |
|--------------|-----------------------------|-------------------------------|----------------------------------------------|
| `VARCHAR(n)` | Same as TEXT (no perf diff) | Fixed max length, faster at n | Email, names, codes when length enforced     |
| `TEXT`       | Unlimited, recommended      | Unlimited, stored separately  | Descriptions, content, unbound text          |
| `CHAR(n)`    | Padded to n characters      | Same                          | Fixed-length codes (e.g., ISO country codes) |
| `ENUM`       | Use `CHECK` or lookup table | Native ENUM type              | Status fields with known values              |

**PostgreSQL**: `TEXT` and `VARCHAR` have identical performance. Prefer `TEXT` to avoid arbitrary length limits, unless the length has business meaning (e.g., `VARCHAR(2)` for ISO country codes).

**MySQL**: `VARCHAR(255)` is common; use only as large as needed since row format matters for index efficiency.

**ENUM vs. CHECK constraint**:
```sql
-- PostgreSQL: Use CHECK constraint (easier to modify)
status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'active', 'cancelled'))

-- Or a lookup table for values that might change
CREATE TABLE order_statuses (
  code VARCHAR(20) PRIMARY KEY,
  label VARCHAR(100)
);
```

---

## Date and Time Types

| Type          | PostgreSQL                              | MySQL                               | Use For                 |
|---------------|-----------------------------------------|-------------------------------------|-------------------------|
| `DATE`        | Calendar date                           | Same                                | Birthdates, event dates |
| `TIME`        | Time of day (no timezone)               | Same                                | Daily schedules (rare)  |
| `TIMESTAMP`   | No timezone info                        | DATETIME                            | Avoid; use TIMESTAMPTZ  |
| `TIMESTAMPTZ` | Stores UTC, returns in session timezone | N/A (use DATETIME + UTC convention) | All timestamps          |
| `INTERVAL`    | Time duration                           | No native type                      | Duration calculations   |

**Best practice for timestamps** (PostgreSQL):
```sql
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

**MySQL**: MySQL's `DATETIME` does not store timezone; always insert in UTC at the application layer. `TIMESTAMP` stores UTC but has a range limit (up to 2038).

---

## Binary and Special Types

| Type    | PostgreSQL            | MySQL                      | Use For                                                       |
|---------|-----------------------|----------------------------|---------------------------------------------------------------|
| `UUID`  | Native `UUID` type    | `CHAR(36)` or `BINARY(16)` | Distributed PKs, external IDs                                 |
| `BYTEA` | Binary data           | `BLOB`                     | Small files, encrypted data (avoid storing large files in DB) |
| `JSONB` | Binary JSON (indexed) | `JSON`                     | Semi-structured, queryable data                               |
| `JSON`  | Text JSON (no index)  | `JSON`                     | Log storage only; prefer JSONB in PG                          |
| `ARRAY` | Native array type     | Not supported              | Simple tag lists, denormalized data                           |

**UUID as PK**:
```sql
-- PostgreSQL
id UUID PRIMARY KEY DEFAULT gen_random_uuid()

-- For high-insert-rate tables, consider UUIDv7 (time-ordered) to avoid B-tree index fragmentation
-- Or use BIGSERIAL for internal PKs and expose UUID externally
```

**JSONB vs. relational**:
- Use `JSONB` for truly variable structure (metadata, config, user preferences)
- Do NOT store core business data as JSONB if it needs to be queried, filtered, or joined
- Every JSONB query is slower and less type-safe than a proper column

---

## PostgreSQL-Specific Types

| Type         | Use For                                                  |
|--------------|----------------------------------------------------------|
| `INET`       | IPv4/IPv6 addresses with network operations              |
| `CIDR`       | Network address ranges                                   |
| `tsvector`   | Pre-processed full-text search vector                    |
| `HSTORE`     | Key-value store (prefer JSONB)                           |
| `pg_trgm`    | Trigram similarity for fuzzy text search                 |

---

## Quick Decision Guide

```
Is it a primary key?
  → Sequential: BIGSERIAL (internal) or UUIDv7 (distributed)
  → External-facing: UUID

Is it money?
  → NUMERIC(12, 2) or BIGINT (cents)

Is it a timestamp?
  → TIMESTAMPTZ (PostgreSQL) / DATETIME + UTC (MySQL)

Is it a status with known values?
  → VARCHAR(20) + CHECK constraint (PostgreSQL)

Is it a long string (descriptions, content)?
  → TEXT

Is it semi-structured / variable schema?
  → JSONB (PostgreSQL) — only if actually queried
  → TEXT/JSON if just stored and retrieved as-is

Is it a boolean flag?
  → BOOLEAN (PostgreSQL) / TINYINT(1) (MySQL)
```

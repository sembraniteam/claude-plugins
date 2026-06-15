# Database Normalization Guide

A reference for applying normal forms during database design. Use when analyzing existing schemas or designing new ones.

---

## Why Normalize?

Normalization eliminates data anomalies:

- **Update anomaly**: Changing a fact requires updating it in multiple rows
- **Insert anomaly**: Cannot record a fact without another unrelated fact
- **Delete anomaly**: Deleting one fact accidentally deletes another

Over-normalization (4NF, 5NF) adds JOIN overhead without proportional benefit in most OLTP systems. Target **3NF** as the default. Apply **BCNF** when a table has composite candidate keys with dependency issues.

---

## First Normal Form (1NF)

**Rule**: Every column contains atomic (indivisible) values, and every row is unique.

**Violations**:
- Comma-separated values in a single column: `tags = "python,django,rest"`
- Repeating column groups: `phone_1`, `phone_2`, `phone_3`
- Arrays stored as strings

**Fix — comma-separated values**:
```sql
-- Before (violates 1NF)
CREATE TABLE articles (
  id INT PRIMARY KEY,
  title VARCHAR(255),
  tags VARCHAR(500)  -- "python,django,rest"
);

-- After (1NF)
CREATE TABLE articles (
  id INT PRIMARY KEY,
  title VARCHAR(255)
);

CREATE TABLE article_tags (
  article_id INT REFERENCES articles(id),
  tag VARCHAR(100),
  PRIMARY KEY (article_id, tag)
);
```

**Fix — repeating columns**:
```sql
-- Before
CREATE TABLE users (
  id INT PRIMARY KEY,
  phone_1 VARCHAR(20),
  phone_2 VARCHAR(20),
  phone_3 VARCHAR(20)
);

-- After
CREATE TABLE user_phones (
  user_id INT REFERENCES users(id),
  phone VARCHAR(20),
  type VARCHAR(20),  -- 'mobile', 'home', 'work'
  PRIMARY KEY (user_id, phone)
);
```

---

## Second Normal Form (2NF)

**Rule**: In 1NF, AND every non-key attribute is fully dependent on the entire primary key (no partial dependencies).

**Applies to**: Tables with composite primary keys.

**Violation — partial dependency**:
```sql
-- Composite PK: (order_id, product_id)
-- product_name depends only on product_id, not the full PK
CREATE TABLE order_items (
  order_id INT,
  product_id INT,
  product_name VARCHAR(255),  -- partial dependency!
  quantity INT,
  unit_price NUMERIC(10,2),
  PRIMARY KEY (order_id, product_id)
);
```

**Fix**:
```sql
CREATE TABLE products (
  id INT PRIMARY KEY,
  name VARCHAR(255)
);

CREATE TABLE order_items (
  order_id INT REFERENCES orders(id),
  product_id INT REFERENCES products(id),
  quantity INT,
  unit_price NUMERIC(10,2),  -- snapshot price, not from products table
  PRIMARY KEY (order_id, product_id)
);
```

---

## Third Normal Form (3NF)

**Rule**: In 2NF, AND no non-key attribute depends on another non-key attribute (no transitive dependencies).

**Violation — transitive dependency**:
```sql
-- zip_code → city, state (transitive dependency through zip_code)
CREATE TABLE users (
  id INT PRIMARY KEY,
  name VARCHAR(100),
  zip_code VARCHAR(10),
  city VARCHAR(100),   -- depends on zip_code, not id
  state VARCHAR(50)    -- depends on zip_code, not id
);
```

**Fix**:
```sql
CREATE TABLE zip_codes (
  zip_code VARCHAR(10) PRIMARY KEY,
  city VARCHAR(100),
  state VARCHAR(50)
);

CREATE TABLE users (
  id INT PRIMARY KEY,
  name VARCHAR(100),
  zip_code VARCHAR(10) REFERENCES zip_codes(zip_code)
);
```

**Practical note**: For addresses, this is often over-normalized in practice. If zip→city data is large and rarely changes, a dedicated zip_codes reference table makes sense. For simple apps, denormalization here is acceptable.

---

## Boyce-Codd Normal Form (BCNF)

**Rule**: Every determinant is a candidate key. Stricter than 3NF; handles anomalies in tables with overlapping composite candidate keys.

**When to apply**: When a table has multiple overlapping candidate keys and there's a dependency that violates the above.

**This is rare** in most business applications. Apply when the analysis reveals a specific BCNF violation.

---

## Practical Normalization Workflow

For each table in an existing schema:

1. **Identify the primary key** (natural or surrogate)
2. **List all functional dependencies** (what determines what)
3. **Check 1NF**: Any multivalued columns? → Extract to junction table
4. **Check 2NF** (composite PKs only): Any partial dependency? → Move to separate table
5. **Check 3NF**: Any transitive dependency? → Extract to separate table
6. **Document what was changed** and why

---

## When NOT to Normalize

Controlled denormalization is sometimes correct:

| Scenario                                                     | Justification                                                          |
|--------------------------------------------------------------|------------------------------------------------------------------------|
| Audit/snapshot columns (e.g., `unit_price` on `order_items`) | Prices change; historical orders need the price at time of purchase    |
| Read-heavy reporting tables                                  | Pre-aggregated or pre-joined data avoids expensive query-time JOINs    |
| Caching/materialized views                                   | Denormalized copies for fast reads; source of truth remains normalized |
| Address fields on `invoices`                                 | Invoice address must not change if user updates their address          |

Always document why a column is intentionally denormalized.

---

## Many-to-Many Relationships

Always resolve M:N with a junction table:

```sql
-- Users can enroll in many courses; courses have many users
CREATE TABLE course_enrollments (
  user_id BIGINT REFERENCES users(id),
  course_id BIGINT REFERENCES courses(id),
  enrolled_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  PRIMARY KEY (user_id, course_id)
);
-- Index on course_id for "list all students in course" queries
CREATE INDEX idx_enrollments_course ON course_enrollments(course_id);
```

If the junction table has its own attributes (e.g., `grade`, `completed_at`), give it a surrogate PK:

```sql
CREATE TABLE course_enrollments (
  id BIGSERIAL PRIMARY KEY,
  user_id BIGINT REFERENCES users(id),
  course_id BIGINT REFERENCES courses(id),
  enrolled_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  grade NUMERIC(4,2),
  UNIQUE (user_id, course_id)
);
```

---

## Soft Delete Pattern

Use `deleted_at TIMESTAMPTZ` instead of hard-deleting rows. Required whenever data must be auditable, relationships reference the row, or undo functionality is needed.

```sql
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMPTZ;

-- Partial index for active-user lookups (most frequent query pattern)
CREATE INDEX idx_users_active_email ON users(email) WHERE deleted_at IS NULL;

-- Partial index for listing active users by creation date
CREATE INDEX idx_users_active_created ON users(created_at) WHERE deleted_at IS NULL;
```

**Query convention**: Always filter with `WHERE deleted_at IS NULL` for active records. Never omit this filter in application queries.

**Trade-off**: Soft-deleted rows accumulate over time. For tables with high churn, schedule periodic archival of old deleted rows to a separate archive table or cold storage.

---

## Audit Log Table Pattern

Capture who changed what and when, separately from the main table. Required for compliance (GDPR, PCI DSS) and debugging production incidents.

```sql
CREATE TABLE user_audit_log (
  id         BIGSERIAL PRIMARY KEY,
  user_id    BIGINT NOT NULL REFERENCES users(id),
  changed_by BIGINT REFERENCES users(id),
  action     VARCHAR(20) NOT NULL,  -- 'INSERT', 'UPDATE', 'DELETE'
  old_data   JSONB,
  new_data   JSONB,
  changed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index for looking up a user's history
CREATE INDEX idx_user_audit_user ON user_audit_log(user_id, changed_at DESC);
```

**Implementation options**:
- **Database triggers**: Automatic, no application code required. Use `pgaudit` (PostgreSQL) or an `AFTER INSERT OR UPDATE OR DELETE` trigger. Harder to test and debug.
- **Application-layer interceptors**: ORM hooks (e.g., SQLAlchemy events, Hibernate listeners). Easier to test, but requires discipline to apply consistently.

**GDPR note**: If a user requests erasure, scrub PII columns in `user_audit_log` (set to NULL or a placeholder) rather than deleting rows — the audit trail structure must be preserved for compliance.

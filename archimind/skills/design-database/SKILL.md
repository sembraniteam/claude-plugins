---
name: design-database
description: This skill should be used when the user asks to "design a database", "create a database schema", "normalize my database", "normalize my schema", "help me with database design", "design database tables", "what indexes should I add", "help me with my ER diagram", "design the data model", "optimize my database schema", "what data types should I use", "design a relational database", "review my SQL schema", "create an ERD", or pastes SQL DDL statements for normalization and improvement.
---

# Design Database

Act as a **Database Architect** with production experience across OLTP, analytical, and distributed systems. Read and apply `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/engineering-principles.md` throughout this workflow.

Core behaviors:
- Make every performance, scalability, and maintainability implication explicit for each design decision
- Identify potential bottlenecks proactively: missing indexes, N+1 patterns, lock contention, hot partitions
- Recommend the simplest schema that satisfies stated query patterns; avoid premature normalization or denormalization
- Explain rationale and trade-offs for every structural decision

Design a new database schema from requirements, or analyze and normalize an existing schema. Produce an Entity-Relationship Diagram (Mermaid), detailed table specifications (columns, data types, constraints, indexes), normalization analysis, and a concise rationale for every decision. Open a static HTML viewer so the user can see the ERD rendered with Mermaid JS.

## Workflow

**Tools — create tasks and use structured questions throughout:**

At the very start, call **TaskCreate** to create one task per step:
1. Clarify goal and database context
2. Design schema (or analyze existing schema)
3. Produce ER diagram
4. Produce table specifications
5. Apply security recommendations
6. Write content.md and open viewer
7. Save final docs and stop server

Mark each task `in_progress` when starting it and `completed` when done.

### 1. Clarify the Goal

Determine which mode applies:

- **Design from scratch**: User describes requirements (entities, relationships, expected queries)
- **Normalize existing schema**: User pastes SQL DDL (`CREATE TABLE` statements) or describes the existing tables

If the mode or context is unclear, use **AskUserQuestion** to ask (up to 4 questions at once):
- What is the target database engine? (PostgreSQL, MySQL, SQLite, MongoDB, etc.)
- Approximate data volume and read/write ratio?
- Most critical queries (search, reporting, real-time lookups)?
- Any existing data that needs migrating?

### 2A. Design from Scratch

#### Identify Entities and Relationships

From the user's requirements:
1. Extract nouns → candidate entities/tables
2. Identify verbs/relationships between entities (one-to-many, many-to-many)
3. Identify attributes of each entity
4. Determine natural vs. surrogate primary keys

#### Apply Normal Forms

Design directly to at least **3NF** (Third Normal Form). Apply BCNF where applicable. Do not over-normalize into 4NF/5NF unless there is a clear reason (multivalued dependencies, explicit analytics use case). Refer to `$CLAUDE_PLUGIN_ROOT/skills/design-database/references/normalization-guide.md` for rules and examples.

#### Choose Data Types

For each column, choose the most appropriate data type. Key principles:

- Use the **smallest type that fits** the domain (e.g., `SMALLINT` not `BIGINT` for a status flag)
- Use `ULID` or `UUID v7` for distributed PKs (ULID preferred — time-sortable, reduces B-tree fragmentation vs. random UUID); use `BIGSERIAL`/`BIGINT AUTO_INCREMENT` for single-node sequential PKs
- Use `TEXT` over `VARCHAR(n)` in PostgreSQL (no performance difference); use `VARCHAR(n)` in MySQL when length is meaningful
- Use `TIMESTAMPTZ` (PostgreSQL) or `DATETIME` + UTC convention for timestamps
- Use `NUMERIC(p,s)` or `DECIMAL` for money, never `FLOAT`/`DOUBLE`
- Use `JSONB` (PostgreSQL) for semi-structured data only when querying inside the JSON

Refer to `$CLAUDE_PLUGIN_ROOT/skills/design-database/references/data-types-guide.md` for engine-specific recommendations.

#### Define Indexes

After finalizing the schema, determine indexes based on query patterns:
1. Primary key indexes (automatic)
2. Foreign key indexes (always index FK columns)
3. Query-pattern indexes (columns in WHERE, JOIN ON, ORDER BY, GROUP BY)
4. Unique constraints (acts as unique index)

For each index, specify:
- Type (B-tree, Hash, GiST, GIN, BRIN, Full-text)
- Columns (single or composite — order matters for composites)
- Justification tied to a specific query pattern

Refer to `$CLAUDE_PLUGIN_ROOT/skills/design-database/references/index-guide.md` for index type selection rules.

#### Apply Common Design Patterns

Proactively apply these patterns where relevant — they are frequently needed but easy to miss in early design:

**Soft Delete** — Use `deleted_at TIMESTAMPTZ` instead of hard-deleting rows. Required whenever: data must be auditable, relationships reference the row, or undo functionality is needed.
```sql
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMPTZ;
-- Query: WHERE deleted_at IS NULL (add partial index on frequently-queried columns)
CREATE INDEX idx_users_active_email ON users(email) WHERE deleted_at IS NULL;
-- Or for listing active users by creation date:
CREATE INDEX idx_users_active_created ON users(created_at) WHERE deleted_at IS NULL;
```

**Audit Log Table** — Capture who changed what and when, separately from the main table. Required for compliance (GDPR, PCI DSS) and debugging production issues.
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
```
Implement via triggers or application-layer interceptors.

**Status Enum Table** — Avoid magic strings in status columns. Use a lookup/enum table or a PostgreSQL `ENUM` type.

**Optimistic Locking** — Add `version INTEGER NOT NULL DEFAULT 1` to tables with concurrent updates. Increment on every write; reject writes where `version` doesn't match.

### 2B. Normalize Existing Schema

#### Parse and Analyze

Read the provided DDL. For each table:
1. Identify the functional dependencies
2. Check violation of 1NF, 2NF, 3NF, BCNF (use `$CLAUDE_PLUGIN_ROOT/skills/design-database/references/normalization-guide.md`)
3. List repeating groups, partial dependencies, transitive dependencies

#### Produce Analysis Summary

```
### Normalization Analysis

#### {TableName}
- **Current normal form**: 1NF / 2NF / not normalized
- **Issues found**: [list violations with column names]
- **Proposed fix**: [specific restructuring action]
```

#### Apply Fixes

Propose the normalized schema. Show:
- Tables that need to be split
- Columns that should move
- Junction tables for M:N relationships
- New FK relationships introduced

#### Data Migration Notes

For each structural change, include a brief SQL migration hint:
```sql
-- Extract repeating group into separate table
CREATE TABLE order_items (...);
INSERT INTO order_items SELECT ... FROM orders;
ALTER TABLE orders DROP COLUMN ...;
```

### 3. Produce the ER Diagram

Generate a Mermaid `erDiagram` for the final (proposed) schema. Include:
- All tables
- All relationships with cardinality (`||--o{`, `}o--||`, etc.)
- Primary key and foreign key annotations

Example — include the ER diagram in the response using this syntax:

```mermaid
erDiagram
  USER {
    bigint id PK
    varchar email UK
    varchar name
    timestamptz created_at
  }
  ORDER {
    bigint id PK
    bigint user_id FK
    numeric total
    varchar status
    timestamptz created_at
  }
  ORDER_ITEM {
    bigint id PK
    bigint order_id FK
    bigint product_id FK
    int quantity
    numeric unit_price
  }
  USER ||--o{ ORDER : "places"
  ORDER ||--o{ ORDER_ITEM : "contains"
```

### 4. Produce Table Specifications

For each table, provide a spec block:

```markdown
### `{table_name}`

| Column         | Type              | Constraints                 | Description              |
|----------------|-------------------|-----------------------------|--------------------------|
| id             | BIGSERIAL         | PRIMARY KEY                 | Surrogate PK             |
| email          | VARCHAR(255)      | NOT NULL, UNIQUE            | User email               |
| created_at     | TIMESTAMPTZ       | NOT NULL, DEFAULT now()     | Record creation time     |

**Indexes:**
| Name                        | Type   | Columns           | Reason                                     |
|-----------------------------|--------|-------------------|--------------------------------------------|
| idx_users_email             | B-tree | email             | Login lookup, uniqueness enforcement       |
| idx_users_created_at        | BRIN   | created_at        | Range queries on large sequential data     |
```

### 5. Security Recommendations

After finalizing the schema and before writing the output document, apply security recommendations relevant to the design. Read `$CLAUDE_PLUGIN_ROOT/skills/design-database/references/security-guide.md` for the full reference. At minimum, address the following in the final document:

**Access control:**
- Define separate DB roles: `app_rw` (application), `app_ro` (analytics/replicas), `migrator` (migration runner), `backup_user`, `monitor_user`
- Never use the superuser account from application code
- For multi-tenant schemas: recommend Row-Level Security policies

**Secrets management:**
- Credentials must be stored in a secrets manager (Vault, AWS Secrets Manager, GCP Secret Manager) — never hardcoded or committed to version control
- Recommend dynamic short-lived credentials (Vault DB secrets engine) for production
- Note `maxLifetime` in connection pools must be less than the credential rotation interval

**Connection security:**
- Enforce TLS for all connections — `sslmode=verify-full` (PostgreSQL), `REQUIRE SSL` (MySQL), `requireTLS` (MongoDB)
- DB server must not be publicly accessible — private subnet only, firewall/security group restricts DB port to app servers

**Connection pooling:**
- Recommend PgBouncer (PostgreSQL) or HikariCP (JVM) with TLS on both client↔pooler and pooler↔DB sides
- Set `pool_mode = transaction` (PgBouncer) or equivalent for efficiency; document session-mode trade-offs if session-level features are used

**SQL injection prevention:**
- Mandate parameterized queries or ORM — never string-concatenated SQL
- If `ORDER BY` column names come from user input, enforce an allowlist

**Audit logging:**
- Enable `pgaudit` (PostgreSQL) or equivalent for DDL, write, and role-change events
- Recommend an application-level `security_audit_log` table for access to sensitive data

**Compliance:**
- GDPR: document the erasure flow (scrub PII columns, do not hard-delete referenced rows)
- PCI DSS: confirm CVV/CVC are never stored; recommend application-layer encryption for cardholder data
- HIPAA: confirm PHI is encrypted at rest (column-level for sensitive fields) and in transit

Include a `## Security` section in the output document using the structure below.

#### Security Section Structure

```markdown
## Security

### Access Control
- **DB users**: {list roles and their permissions}
- **Superuser policy**: Used only for DBA ops; not accessible from application code
- **Multi-tenant isolation**: {RLS policies if applicable, or "N/A"}

### Secrets Management
- **Credential storage**: {Vault / AWS Secrets Manager / GCP Secret Manager}
- **Rotation strategy**: {dynamic short-lived / 90-day static rotation}

### Connection Security
- **TLS**: {sslmode=verify-full / REQUIRE SSL / requireTLS} — enforced on all connections
- **Network**: DB in private subnet; {security group / firewall} restricts port {5432/3306/27017} to app servers only
- **Connection pool**: {PgBouncer / HikariCP / other} with TLS on both client and server sides

### Data Protection
- **Encryption at rest**: {DB-level / tablespace / cloud-managed}
- **Sensitive columns**: {list PII/PCI columns and encryption approach, or "N/A"}
- **Audit logging**: {pgaudit / MySQL Audit Plugin / application audit table}

### Compliance
- {GDPR / PCI DSS / HIPAA / SOC2 — applicable requirements and how the schema addresses them}
```

### 6. Write Content and Open Viewer

1. Use the **Write tool** to write the full design content to `/tmp/archimind-viewer/content.md`. Follow the **Document Structure for Database Design** below.
2. Start the viewer server and open the URL:

```bash
URL=$(bash "$CLAUDE_PLUGIN_ROOT/scripts/start-server.sh")
open "$URL"
```

Inform the user of the resolved URL, e.g.: "The viewer is open at http://localhost:3000 — the ERD is rendered with Mermaid JS. Click **↺ Reload** in the sidebar after any changes."

### 7. Save Final Docs and Stop Server

**Recommend a migration tool** in the final documentation. Every production schema needs versioned migrations — select based on the user's language/framework:

| Stack         | Recommended tool                                  | Notes                                           |
|---------------|---------------------------------------------------|-------------------------------------------------|
| Go            | `golang-migrate`                                  | CLI + library, supports PostgreSQL/MySQL/SQLite |
| Java / Kotlin | Flyway (simple) or Liquibase (XML/YAML, rollback) | Flyway integrates with Spring Boot by default   |
| Python        | Alembic (SQLAlchemy) or Django migrations         | Alembic for non-Django projects                 |
| Node.js       | Knex.js migrations or Prisma Migrate              | Prisma for type-safe ORM workflows              |
| Ruby          | ActiveRecord Migrations (Rails)                   | Built-in                                        |
| PHP           | Doctrine Migrations or Laravel Migrations         | Laravel has built-in migration support          |
| Any           | Flyway (standalone)                               | Works with any stack via CLI                    |

Include a `## Migration Strategy` section in the final document covering: tool choice, file naming convention (`V1__create_users.sql`), rollback approach, and zero-downtime migration notes for large tables.

1. Compute timestamp: `node -e 'process.stdout.write(String(Date.now()))'` (macOS) or `date +%s%3N` (Linux). Determine topic slug (e.g., `ecommerce`, `user-management`).
2. Save permanent technical documentation to the user's project:

```bash
mkdir -p docs/archimind/database
```

Then use the **Write tool** to write the full content to `docs/archimind/database/{timestamp_ms}-{topic}.md`. To re-visualize later: `bash "$CLAUDE_PLUGIN_ROOT/scripts/open-doc.sh" docs/archimind/database/{timestamp_ms}-{topic}.md`.

3. Stop the viewer server:

```bash
bash "$CLAUDE_PLUGIN_ROOT/scripts/stop-server.sh"
```

## Document Structure for Database Design

After completing Step 5, structure the database design document as follows. Database design docs do not use the 3-option tabbar format (single design output). The viewer renders the ERD and table specs as a single scrollable document. Structure the document clearly:

```markdown
# Database Design: {Topic}

## ERD
{mermaid erDiagram}

## Normalization Analysis (if normalizing existing schema)
...

## Table Specifications
...

## Index Strategy Summary
...

## Migration Strategy
- **Tool**: {recommended migration tool}
- **Naming convention**: `V{n}__{description}.sql` (Flyway) or `{timestamp}_{description}.py`
- **Rollback approach**: {expand-contract / snapshot / backup-and-restore}
- **Zero-downtime notes**: {add-nullable → backfill → add-constraint → drop-old}

## Migration Notes (if applicable — only for normalization mode)
...
```

## Additional Resources

- **`$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/engineering-principles.md`** — 10 guiding principles for acting as a Database Architect. Read at the start of every session.
- **`$CLAUDE_PLUGIN_ROOT/skills/design-database/references/normalization-guide.md`** — Complete 1NF → BCNF rules with SQL examples. Read when analyzing existing schemas.
- **`$CLAUDE_PLUGIN_ROOT/skills/design-database/references/index-guide.md`** — Index type matrix (B-tree, Hash, GiST, GIN, BRIN, Full-text) with use cases and when to avoid. Read when deciding index strategy.
- **`$CLAUDE_PLUGIN_ROOT/skills/design-database/references/data-types-guide.md`** — Data type recommendations for PostgreSQL, MySQL, and SQLite. Read when choosing column types.
- **`$CLAUDE_PLUGIN_ROOT/skills/design-database/references/security-guide.md`** — Security recommendations and best practices for application-to-database connectivity. Read during Step 5 (Security Recommendations) and whenever the user asks about DB security, credential management, TLS, connection pooling security, SQL injection prevention, audit logging, or compliance requirements.

---
name: design-database
description: This skill should be used when the user asks to "design a database", "create a database schema", "normalize my database", "normalize my schema", "help me with database design", "design database tables", "what indexes should I add", "help me with my ER diagram", "design the data model", "help me with data modeling", "optimize my database schema", "what data types should I use", "design a relational database", "review my SQL schema", "create an ERD", "what database engine should I use for my project", or pastes SQL DDL statements for normalization and improvement.
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
2A. Design schema from scratch (skip if normalizing existing schema)
2B. Normalize existing schema (skip if designing from scratch)
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

Extract as much context as possible from the initial message — engine, data volume, query patterns, and migration needs. Ask only about what remains unclear using **AskUserQuestion** (up to 4 questions at once):
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

Read `$CLAUDE_PLUGIN_ROOT/skills/design-database/references/data-types-guide.md` for per-engine type recommendations and key principles (PK strategies, TEXT vs VARCHAR, timestamp handling, NUMERIC for money, JSONB usage).

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

**Soft Delete** — Use `deleted_at TIMESTAMPTZ` instead of hard-deleting rows. Required whenever data must be auditable, relationships reference the row, or undo functionality is needed. See `$CLAUDE_PLUGIN_ROOT/skills/design-database/references/normalization-guide.md` for the DDL pattern and partial index strategy.

**Audit Log Table** — Capture who changed what and when, separately from the main table. Required for compliance (GDPR, PCI DSS) and debugging production issues. See `$CLAUDE_PLUGIN_ROOT/skills/design-database/references/normalization-guide.md` for the DDL template. Implement via triggers or application-layer interceptors.

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

Read `$CLAUDE_PLUGIN_ROOT/skills/design-database/references/security-guide.md` for the full requirements and examples. Apply its recommendations to the design, then include a `## Security` section in the output document with these five subsections:

- **Access Control** — DB roles (`app_rw`, `app_ro`, `migrator`, `backup_user`), superuser policy, multi-tenant Row-Level Security
- **Secrets Management** — credential storage (Vault / AWS Secrets Manager), rotation interval vs. pool `maxLifetime`
- **Connection Security** — TLS enforcement (`sslmode=verify-full`), private subnet isolation, PgBouncer / HikariCP configuration
- **Data Protection** — encryption at rest, sensitive column handling, audit logging (`pgaudit`, `security_audit_log`)
- **Compliance** — GDPR erasure flow, PCI DSS card data rules, HIPAA PHI encryption at rest and in transit

### 6. Write Content and Open Viewer

> **Note**: Database design produces a **single-design document** — not a 3-option tabbed view. The viewer renders it as a single scrollable page with the ERD and table specs. Do not use `### Option N:` headings.

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

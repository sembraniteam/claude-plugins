# Database Security & Application Connectivity Guide

Reference for the `design-database` and `design-architecture` skills. Apply these practices when designing a new schema, reviewing an existing one, or documenting the Security section of an architecture design.

---

## 1. Secrets Management — Never Hardcode Credentials

**Rule:** Database credentials must never appear in source code, config files committed to version control, or container images.

| Environment       | Recommended approach                                                                        |
|-------------------|---------------------------------------------------------------------------------------------|
| Production        | HashiCorp Vault (dynamic secrets), AWS Secrets Manager, GCP Secret Manager, Azure Key Vault |
| CI/CD pipelines   | Provider-native secret store (GitHub Actions secrets, GitLab CI variables)                  |
| Local development | `.env` file in `.gitignore` + `direnv`; never share across team in plaintext                |
| Kubernetes        | External Secrets Operator → Vault / Secrets Manager → `Secret` object                       |

**Dynamic secrets (recommended for production):**
```
App → Vault DB secrets engine → Vault generates short-lived credentials → App connects
Credentials expire in 1h (configurable) → Vault revokes on lease expiry
```

**Static credential rotation (if dynamic secrets are not used):**
- Rotate DB passwords every 90 days (PCI DSS) or 180 days (standard) via automation
- Use two-stage rotation: create new credential → update app → revoke old credential (avoid downtime)
- Store rotation scripts in Vault or Secrets Manager, not in repo

---

## 2. Principle of Least Privilege — Separate DB Users Per Role

Create a dedicated database user for each service or access tier. Never use the superuser/root account from application code.

| Role                 | Permissions                                                        | Notes                                        |
|----------------------|--------------------------------------------------------------------|----------------------------------------------|
| `app_rw`             | SELECT, INSERT, UPDATE, DELETE on app tables only                  | Used by the application service              |
| `app_ro`             | SELECT on app tables only                                          | Used by read replicas, analytics connectors  |
| `migrator`           | CREATE, ALTER, DROP on owned schema only                           | Used only by migration runner (Flyway etc.)  |
| `backup_user`        | SELECT + LOCK TABLES (MySQL) / pg_dump role (PostgreSQL)           | Used by backup jobs; no write access         |
| `monitor_user`       | SELECT on `pg_stat_*` / `information_schema` only                  | Used by observability agents                 |
| `superuser` / `root` | All privileges                                                     | Only for DBA ops; never used by application  |

**PostgreSQL example:**
```sql
-- Application user: only the tables it needs
CREATE ROLE app_rw LOGIN PASSWORD '${SECRET}';
GRANT CONNECT ON DATABASE myapp TO app_rw;
GRANT USAGE ON SCHEMA public TO app_rw;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_rw;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_rw;

-- Read-only user for analytics / replicas
CREATE ROLE app_ro LOGIN PASSWORD '${SECRET}';
GRANT CONNECT ON DATABASE myapp TO app_ro;
GRANT USAGE ON SCHEMA public TO app_ro;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_ro;
```

**Row-Level Security (PostgreSQL) — for multi-tenant schemas:**
```sql
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON orders
  USING (tenant_id = current_setting('app.tenant_id')::bigint);
-- App sets: SET LOCAL app.tenant_id = 42; before every query
```

---

## 3. Encryption in Transit — Always Use TLS

**Rule:** All connections between application and database must use TLS. Never allow plaintext connections in any environment beyond local dev.

### PostgreSQL
```bash
# postgresql.conf
ssl = on
ssl_cert_file = '/etc/ssl/certs/server.crt'
ssl_key_file  = '/etc/ssl/private/server.key'
ssl_ca_file   = '/etc/ssl/certs/ca.crt'       # mutual TLS: verify client cert

# pg_hba.conf — reject non-TLS connections
hostssl  all  all  0.0.0.0/0  scram-sha-256
host     all  all  0.0.0.0/0  reject          # deny plaintext
```

**Connection string (application side):**
```
postgresql://app_rw:${SECRET}@db.internal:5432/myapp?sslmode=verify-full&sslrootcert=/certs/ca.crt
```

`sslmode` levels (use `verify-full` in production):

| sslmode       | Encrypts | Verifies server cert | Verifies hostname |
|---------------|----------|----------------------|-------------------|
| `disable`     | No       | No                   | No                |
| `require`     | Yes      | No                   | No                |
| `verify-ca`   | Yes      | Yes                  | No                |
| `verify-full` | Yes      | Yes                  | Yes ✓ recommended |

### MySQL / MariaDB
```sql
-- my.cnf
[mysqld]
require_secure_transport = ON
ssl-cert = /etc/ssl/certs/server.crt
ssl-key  = /etc/ssl/private/server.key
ssl-ca   = /etc/ssl/certs/ca.crt

-- Create user that requires TLS
CREATE USER 'app_rw'@'%' REQUIRE SSL;
```

### MongoDB
```yaml
# mongod.conf
net:
  tls:
    mode: requireTLS
    certificateKeyFile: /etc/ssl/mongodb.pem
    CAFile: /etc/ssl/ca.pem
```

---

## 4. Encryption at Rest

| Layer             | Mechanism                                                                         |
|-------------------|-----------------------------------------------------------------------------------|
| DB data files     | PostgreSQL: `pg_tde` extension or transparent data encryption at OS/storage level |
| MySQL / MariaDB   | InnoDB tablespace encryption (`innodb_encrypt_tables = ON`)                       |
| Cloud managed DBs | Always-on by default (RDS, Cloud SQL, Azure Database) — verify key management     |
| Backups           | Encrypt backup files with AES-256; store encryption key separately from backup    |
| Object storage    | SSE-S3 / SSE-KMS (AWS), CMEK (GCP), customer-managed keys (Azure)                 |
| Sensitive columns | Application-layer encryption for PII/PCI fields (e.g., `pgcrypto`, Vault Transit) |

**Application-layer encryption for sensitive columns (PostgreSQL + pgcrypto):**
```sql
-- Encrypt at write time (key managed by app / Vault)
UPDATE users SET ssn = pgp_sym_encrypt('123-45-6789', '${COLUMN_KEY}') WHERE id = 1;

-- Decrypt at read time
SELECT pgp_sym_decrypt(ssn::bytea, '${COLUMN_KEY}') FROM users WHERE id = 1;
```

For compliance (PCI DSS, HIPAA): prefer **Vault Transit encryption** so column keys are never in the database process or application memory longer than necessary.

---

## 5. Network Security — Keep the Database Private

**Rule:** Database ports must never be directly exposed to the internet. All access must flow through the application layer.

### Network topology (recommended)
```
Internet
  └── Load Balancer (public subnet)
        └── Application Servers (private subnet)
              └── Database (isolated private subnet, no internet route)
                    └── Bastion Host / VPN (admin access only, not used by app)
```

### Security group / firewall rules
```
DB security group inbound rules:
  - Port 5432 (PostgreSQL): allow from app-server security group ONLY
  - Port 5432: deny all other sources (including 0.0.0.0/0)
  - No SSH / port 22 on DB server (manage via SSM Session Manager)

Admin access:
  - DBA connects via bastion host or AWS SSM / GCP IAP tunnel (no permanent open port)
```

### Cloud-specific isolation
| Cloud       | Service                              | Notes                                       |
|-------------|--------------------------------------|---------------------------------------------|
| AWS         | RDS in private subnet + VPC SG       | Enable `PubliclyAccessible: false`          |
| GCP         | Cloud SQL with Private IP            | Disable public IP; use Cloud SQL Auth Proxy |
| Azure       | Azure Database with private endpoint | Disable public network access               |
| Self-hosted | Docker network isolation             | Use named network; do not publish DB port   |

**Docker example:**
```yaml
services:
  app:
    networks: [backend]
  db:
    networks: [backend]
    # No "ports:" mapping — only accessible within the backend network
networks:
  backend:
    internal: true   # no external connectivity
```

---

## 6. Connection Pooling — Security Considerations

Connection poolers (PgBouncer, PgCat, HikariCP) sit between app and DB. They introduce their own security surface.

### PgBouncer (PostgreSQL)
```ini
# pgbouncer.ini
[databases]
myapp = host=db.internal port=5432 dbname=myapp

[pgbouncer]
listen_addr  = 127.0.0.1          # bind to loopback only, not 0.0.0.0
auth_type    = scram-sha-256       # never use trust or md5
auth_file    = /etc/pgbouncer/userlist.txt
server_tls_sslmode  = verify-full  # TLS to backend DB
server_tls_ca_file  = /etc/ssl/ca.crt
client_tls_sslmode  = require      # TLS from app to pooler

pool_mode    = transaction         # transaction mode: most efficient
max_client_conn = 500
default_pool_size = 20             # actual DB connections (keep low)
```

**Pool mode security trade-offs:**

| Mode          | DB connections      | Session-level features     | Compatibility       |
|---------------|---------------------|----------------------------|---------------------|
| `session`     | 1:1 with client     | Full (SET, prepared stmts) | Highest             |
| `transaction` | Shared              | Not available              | Most apps work      |
| `statement`   | Shared aggressively | Very limited               | Avoid unless needed |

### HikariCP (Java/Kotlin)
```java
HikariConfig config = new HikariConfig();
config.setJdbcUrl("jdbc:postgresql://db.internal:5432/myapp?sslmode=verify-full");
config.setUsername(secrets.get("DB_USER"));
config.setPassword(secrets.get("DB_PASSWORD"));
config.setMaximumPoolSize(20);
config.setMinimumIdle(5);
config.setConnectionTimeout(30_000);     // 30s — fail fast
config.setIdleTimeout(600_000);          // 10m
config.setMaxLifetime(1_800_000);        // 30m — force reconnect before Vault lease expires
config.addDataSourceProperty("ssl", "true");
config.addDataSourceProperty("sslmode", "verify-full");
```

**`maxLifetime` must be less than the DB credential rotation interval** when using dynamic secrets.

---

## 7. SQL Injection Prevention

**Rule:** Never construct SQL by concatenating user-supplied strings. Always use parameterized queries or a type-safe ORM.

| Approach             | Example                                                      | Safe? |
|----------------------|--------------------------------------------------------------|-------|
| String concatenation | `"SELECT * FROM users WHERE email = '" + email + "'"`        | No    |
| Parameterized query  | `db.query("SELECT * FROM users WHERE email = $1", [email])`  | Yes   |
| Prepared statement   | `stmt.setString(1, email); stmt.executeQuery()`              | Yes   |
| ORM (typed)          | `User.where(email: email)` (ActiveRecord, Prisma, GORM)      | Yes   |
| Dynamic `ORDER BY`   | Only allow a fixed allowlist of column names from user input | Yes   |

**Additional defenses:**
- Enable `pg_stat_statements` to audit slow / unusual queries
- Use a Web Application Firewall (WAF) with SQL injection rules as a defense-in-depth layer
- Set `search_path = "$user", public` to prevent schema injection

---

## 8. Connection String Security

**Rule:** Connection strings containing credentials must never appear in source code, logs, or error messages.

**Pattern: connection string from secrets manager at runtime**
```go
// Go example — fetch at startup, not hardcoded
dsn, err := secretsClient.GetSecretValue(ctx, "prod/myapp/db")
db, err := sql.Open("pgx", dsn)
```

**Redact credentials from logs:**
```
# Dangerous (credential in URL logged on startup)
DB_URL=postgres://app_rw:mysecret@db.internal/myapp

# Safe (separate host/user/pass from env)
DB_HOST=db.internal
DB_NAME=myapp
DB_USER=app_rw
DB_PASS=${from secrets manager}
```

**Log-safe DSN construction:**
- Build the DSN string at connection time from individual components
- Log only `host`, `port`, `dbname`, and `user` — never the password
- Mask or omit DSN from stack traces and error responses

---

## 9. Audit Logging

Capture all privileged operations and sensitive data access for compliance (GDPR, HIPAA, PCI DSS).

### PostgreSQL — `pgaudit` extension
```sql
-- postgresql.conf
shared_preload_libraries = 'pgaudit'
pgaudit.log = 'write, ddl, role'   -- log writes, schema changes, role grants
pgaudit.log_relation = on           -- log table name in every audit entry
pgaudit.log_parameter = on          -- log query parameters (caution: may contain PII)

-- Session-level: audit specific user activity
SET pgaudit.log = 'all';   -- use in DBA sessions only
```

### MySQL — General Query Log / Audit Plugin
```sql
-- Enable general query log (development/staging only — high I/O)
SET GLOBAL general_log = 'ON';

-- For production use MariaDB Audit Plugin or MySQL Enterprise Audit
INSTALL PLUGIN audit_log SONAME 'audit_log.so';
SET GLOBAL audit_log_policy = 'ALL';
```

### Application-layer audit table (supplement, not replace DB audit)
```sql
CREATE TABLE security_audit_log (
  id          BIGSERIAL PRIMARY KEY,
  actor_id    BIGINT,                  -- user or service performing action
  actor_type  VARCHAR(20) NOT NULL,    -- 'user', 'service', 'cron'
  action      VARCHAR(50) NOT NULL,    -- 'login', 'read_pii', 'export_data', 'delete_record'
  resource    VARCHAR(100),            -- table and/or record ID
  ip_address  INET,
  user_agent  TEXT,
  metadata    JSONB,                   -- additional context
  occurred_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_security_audit_actor   ON security_audit_log(actor_id, occurred_at);
CREATE INDEX idx_security_audit_action  ON security_audit_log(action, occurred_at);
CREATE INDEX idx_security_audit_time    ON security_audit_log(occurred_at DESC);
```

---

## 10. Compliance Quick Reference

| Regulation  | Key DB requirements                                                                                                                                              |
|-------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **GDPR**    | Right to erasure (soft-delete + hard-delete pipeline), data minimization, audit trail, encryption at rest and in transit, DPA with cloud providers               |
| **PCI DSS** | No storing CVV/CVC ever, encrypt cardholder data (AES-256), credential rotation every 90 days, audit logs retained 12 months, restrict DB access to need-to-know |
| **HIPAA**   | Encrypt PHI at rest and in transit, unique user IDs (no shared accounts), automatic logoff, audit controls, backup and DR testing                                |
| **SOC 2**   | Logical access controls, encryption, monitoring/alerting, change management, incident response                                                                   |

**PCI DSS — columns that must never be stored:**
- CVV/CVC (card verification value)
- Full magnetic stripe data
- PIN blocks

**GDPR — right-to-erasure implementation:**
```sql
-- Soft delete with PII scrubbing (preferred over hard delete for referential integrity)
UPDATE users
SET
  email       = 'deleted-' || id || '@erased.invalid',
  name        = 'Deleted User',
  phone       = NULL,
  address     = NULL,
  deleted_at  = now(),
  erased_at   = now()
WHERE id = $1;
```

---

## 11. Security Checklist for Database Design Review

Use during schema design review or architecture review:

- [ ] DB credentials stored in secrets manager, not in code or `.env` committed to git
- [ ] Separate DB users for app (rw), analytics (ro), migrations, backups, monitoring
- [ ] TLS enforced for all connections (`sslmode=verify-full` or equivalent)
- [ ] DB server not publicly accessible (private subnet, no public IP)
- [ ] Connection pooler configured with TLS on both client and server sides
- [ ] Parameterized queries or ORM used — no string-concatenated SQL
- [ ] Sensitive columns (PII, PCI fields) identified for application-layer encryption
- [ ] Audit logging enabled for privileged operations and sensitive data access
- [ ] Row-level security policies for multi-tenant schemas
- [ ] `maxLifetime` in connection pool set below credential rotation interval (dynamic secrets)
- [ ] Security groups / firewall rules limit DB port access to app servers only
- [ ] Compliance requirements identified: GDPR erasure flow / PCI storage restrictions / HIPAA PHI encryption

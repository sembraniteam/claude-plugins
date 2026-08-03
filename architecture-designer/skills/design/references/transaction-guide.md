# Database Transaction Guide

Use this guide at Stage 6a (database schema design, alongside `references/ddd-guide.md`'s aggregate-boundary step) and
at Step 10 (Business Rules whose `Post-conditions` touch more than one table), per `design/SKILL.md`. It covers how a
transaction is actually demarcated, isolated, and made safe under concurrent access — the mechanics behind the
transactional-consistency-boundary decision `references/ddd-guide.md` and `database-designer` already make when they
decide *which* tables may share a transaction. This guide decides *how* that shared transaction behaves: what isolation
level it runs at, how it handles two writers touching the same row, and what happens when a business rule's effects
legitimately need to cross an aggregate or a service boundary where one database transaction can no longer cover them.

## Why this matters

- **A transaction boundary with no stated isolation level or locking strategy is an unfinished decision, not a safe
  default.** Two concurrent requests decrementing the same inventory row under the wrong isolation level can both read
  the same starting quantity and both succeed, overselling stock that was never actually available — the schema and the
  transaction boundary were both correct; the concurrency behavior was the missing piece.
- **The failure is silent under normal testing and load, and shows up under production concurrency** — a single-user
  manual test never exercises two simultaneous writers racing for the same row, which is exactly the condition these
  bugs need to appear.
- **Forcing every cross-aggregate effect into one ACID transaction is the opposite failure** — the DDD aggregate
  boundary (`references/ddd-guide.md`) exists specifically because a transaction that spans two aggregates (or, worse,
  two microservices' separate databases) doesn't scale, creates lock contention across unrelated concerns, and is
  outright impossible once the two sides are different databases behind different services. The Saga/outbox patterns
  below are what makes "eventually consistent across aggregates, atomic within one" an intentional, correctly-modeled
  decision instead of a gap in the design.

## 1. ACID, briefly

A database transaction is expected to be **Atomic** (all its writes commit together or none do), **Consistent** (it
leaves the database satisfying every constraint/invariant), **Isolated** (concurrent transactions don't see each other's
uncommitted intermediate state), and **Durable** (once committed, it survives a crash). Every relational engine this
plugin recommends (`agents/database-designer.md` Step 1) provides all four for a single-database transaction — the
design work is not proving ACID exists, it's choosing the isolation level and concurrency-control strategy that use it
correctly for this specific aggregate's contention profile.

## 2. Transaction boundary = aggregate boundary

Nothing new to decide here beyond what `references/ddd-guide.md` already establishes: one transaction per aggregate
write, tables belonging to a different aggregate are never touched in the same transaction, and a business rule that
seems to need this crosses into section 4 (Saga/outbox) below instead. Restate the aggregate's transaction boundary in
this guide's terms only when it changes what follows — i.e., when the aggregate is one of the high-contention cases
section 3 covers.

## 3. Isolation levels and concurrency control

### Isolation levels and the anomalies each one prevents

| Level            | Dirty read | Non-repeatable read | Phantom read | Lost update | Typical engine default                                                                                                                      |
|------------------|:----------:|:-------------------:|:------------:|:-----------:|---------------------------------------------------------------------------------------------------------------------------------------------|
| Read Uncommitted |  possible  |      possible       |   possible   |  possible   | rarely a default anywhere — reached only via an explicit hint/setting (e.g. SQL Server's `NOLOCK`), never PostgreSQL/MySQL's actual default |
| Read Committed   | prevented  |      possible       |   possible   |  possible   | **PostgreSQL default**; also SQL Server's default (via locking, not MVCC)                                                                   |
| Repeatable Read  | prevented  |      prevented      |  possible*   |  possible*  | **MySQL/InnoDB default**                                                                                                                    |
| Serializable     | prevented  |      prevented      |  prevented   |  prevented  | strongest — highest contention cost                                                                                                         |

\* Both PostgreSQL and MySQL/InnoDB document stronger phantom/lost-update behavior at Repeatable Read than the bare SQL
standard requires, but by different mechanisms with different edge cases — do not assume the same isolation *name*
behaves identically across engines; verify against the specific engine's own documentation rather than treating
"Repeatable Read" as one universal behavior. PostgreSQL's Repeatable Read (MVCC snapshot isolation) prevents phantom
reads outright and detects lost-update conflicts by raising a serialization-failure error (`SQLSTATE 40001`) rather than
silently allowing them. MySQL/InnoDB's Repeatable Read prevents phantoms for locking reads via next-key locking (record
lock + gap lock), documented with caveats for scans that can't use an index efficiently — but an application-level
read-then-write (a separate `SELECT` followed by an `UPDATE` that recomputes the new value from client-side code, not a
single atomic `UPDATE table SET x = x - 1 WHERE id = ?`, which is safe under either engine) with no explicit locking
read beforehand can still silently lose an update, unlike PostgreSQL's hard failure. Treat InnoDB's Repeatable Read as
"phantom-safe for locking reads, not lost-update-safe by default" rather than assuming it matches PostgreSQL's stronger
guarantee.

**Default recommendation**: leave the engine's default isolation level (Read Committed for PostgreSQL, Repeatable Read
for MySQL/InnoDB) for ordinary CRUD aggregates with no real concurrent-write contention — raising isolation everywhere
adds lock contention and serialization-failure retries for aggregates that never actually race. Name an explicit,
stronger isolation level only for an aggregate section 3's "high-contention signal" below actually flags.

**High-contention signal**: an aggregate is a candidate for explicit isolation/locking treatment when its write path
does a read-then-write on a value multiple concurrent requests plausibly touch at once — a stock/inventory count, an
account balance, a limited-seat/limited-slot booking, a rate-limit counter (already covered separately by
`references/rate-limiting-guide.md`), or a uniqueness check with a race window (e.g. "is this username still available"
followed by an insert). An aggregate with no such read-then-write path (most CRUD entities: a user's profile fields, a
comment body) does not need this section's treatment beyond the engine default.

### Optimistic concurrency control

Add a `version` column (integer, incremented on every update) to the aggregate root, and make every write conditional on
the version it read: `UPDATE ... SET quantity = quantity - 1, version = version + 1 WHERE id = $1 AND version = $2`.
Zero rows affected means another writer won the race — the application retries by re-reading and re-attempting, or
surfaces a conflict to the caller. This is the same `version` column
`references/offline-first-guide.md` section 4 already adds for offline-sync conflict *detection* — where that guide uses
it to detect a stale client write arriving after the fact, this section uses the identical column and mechanism to
detect a stale write racing another write in real time; state in the schema notes when one `version` column is serving
both purposes rather than adding a second one.

**Use when**: contention is infrequent relative to total writes (most web-scale read-then-write paths) — the cost of an
occasional retry is cheaper than holding a lock for the duration of every write.

### Pessimistic concurrency control

Acquire a row lock before reading the value a write depends on — `SELECT ... FOR UPDATE` in the same transaction as the
subsequent write — so a second concurrent transaction touching the same row blocks until the first commits or rolls
back, rather than racing it.

**Use when**: contention is frequent enough that optimistic retries would themselves become a bottleneck (a
highly-contended single counter, a small fixed pool of limited slots where most requests during a peak window target the
same rows), or when the business rule cannot tolerate exposing a conflict back to the caller for a client-side retry (a
server-side batch process that must simply wait its turn).

**Deadlock avoidance**: when a business rule's transaction must lock more than one row (e.g. transferring a value
between two accounts), always acquire locks in the same fixed order across every code path that performs this kind of
transaction — e.g. by ascending primary key — never in caller-determined or request-payload-determined order. Two
transactions locking the same two rows in opposite order is the standard deadlock pattern; consistent ordering
eliminates it structurally rather than relying on the engine's deadlock detector plus a retry to paper over it.

**Retry on serialization failure / deadlock**: both a `SELECT ... FOR UPDATE` deadlock and an optimistic version
conflict (and PostgreSQL's Serializable-level serialization-failure error) are expected, recoverable conditions, not
application bugs — wrap the transaction in a bounded retry (a handful of attempts with a short backoff), the same
retry-policy discipline `references/resilience-guide.md` already applies to external-dependency calls, applied here to
the database's own concurrency-conflict errors specifically. Do not let a serialization failure surface to the caller as
a raw 500 on the first occurrence.

## 4. When one transaction isn't enough — cross-aggregate and cross-service consistency

A business rule whose effects genuinely span two aggregates (or two microservices' separate databases) cannot use a
single ACID transaction — per section 2, that would mean the aggregate boundary was drawn wrong, or the two
aggregates/services simply don't share a database at all. Model this as an explicit **eventually consistent** sequence
instead of forcing atomicity that doesn't exist:

### Saga pattern

A sequence of local transactions, each committing within one aggregate/service, where each step publishes an event or
sends a command that triggers the next step, and every step that has a meaningful failure mode defines a **compensating
transaction** that undoes its effect if a later step fails (e.g. "release the reserved inventory" compensates "reserve
inventory" if the payment step that follows it fails).

- **Choreography** — each service reacts to events from the others with no central coordinator; simpler to add a new
  participant, harder to see the overall flow in one place. Prefer for a short saga (2–3 steps) with stable
  participants.
- **Orchestration** — a central orchestrator (a dedicated saga/workflow component, or a workflow engine) explicitly
  calls each step and invokes compensations on failure; the flow is visible in one place at the cost of a coordinating
  component. Prefer for a longer or business-critical saga where the failure/compensation logic itself needs to be
  reviewable and testable as a unit.

Name the chosen style, list every step in order, and state each step's compensating transaction (or explicitly "no
compensation needed — this step is idempotent/harmless to leave applied" when that's true) in the LLD Business Rule's
`Logic` section (`references/lld-guide.md`) — a saga with an unstated compensation for a step that clearly needs one is
the most common gap to catch before implementation, not after an incident.

### Transactional outbox pattern

To reliably trigger the *next* saga step (or any cross-aggregate/cross-service event) from a step that just committed a
local transaction, write the outgoing event to an `outbox` table **in the same local transaction** as the state change
it describes, then have a separate relay process (a polling job, or the engine's change-data-capture/logical-replication
feed) read the outbox and publish to the message broker, marking each row published once delivery is confirmed. This
closes the classic gap where a service commits its own state change but then crashes (or the broker is briefly
unreachable) before the event actually publishes — the event is never lost, because it was committed atomically with the
state it describes, not sent as a separate, unguaranteed step immediately after.

**Do not confuse this with `references/offline-first-guide.md`'s client-side outbox** — that guide's outbox is a
client-to-server sync queue for an offline-capable client's local writes; this section's outbox is a server-side,
same-transaction mechanism for reliably publishing a domain event out of one service's database. The name and the core
idea (durably queue the thing that must eventually be sent, in the same transaction as the state it depends on)
are the same pattern applied at two different layers — cite this section for cross-service/cross-aggregate event
publishing, cite the offline-first guide for client sync.

### What to avoid

- **Two-Phase Commit (2PC) across service boundaries** — technically consistent, but it holds locks across a network
  round-trip and a coordinator failure can leave participants blocked indefinitely; almost no system this plugin designs
  for should reach for it. If a genuine strong-consistency-across-services requirement exists, treat it as a Critical
  trade-off to surface explicitly (per `references/quality-driven-design-guide.md`'s Trade-off and Risk Analysis) rather
  than defaulting to 2PC silently.
- **A cross-service HTTP call made *inside* an open database transaction** — holding a database transaction (and its
  locks) open while waiting on a network call to another service ties up a database connection and lock for the duration
  of that call's latency, and any retry of the network call now also means retrying (or leaving dangling) the open
  transaction. Commit the local transaction first, then trigger the next step via the outbox/event mechanism above —
  never hold a DB transaction open across a network boundary.

## 5. Idempotency

Every retried step above (a saga step re-delivered by the broker, a client retrying a request that may have already
succeeded server-side) must be safe to apply twice. Use an idempotency key — a client-generated or event-carried unique
ID, stored and checked before applying the effect (`INSERT ... ON CONFLICT (idempotency_key) DO NOTHING`, or a check
against an already-processed-IDs table/column) — rather than assuming the caller will only ever send a request once.
This is the same discipline `references/resilience-guide.md` names for a retried external call, applied here to the
receiving side of a retried internal event/command.

---

## Applying this guide across the workflow

- **`database-designer`, Step 2 (Schema design)**: after establishing aggregate boundaries per
  `references/ddd-guide.md`, apply this guide's section 3 high-contention signal to each aggregate — for any aggregate
  it flags, state the isolation level (if raised above the engine default) and concurrency-control strategy (optimistic
  `version` column, reusing the offline-first column if that track is also active, or pessimistic locking with its
  lock-ordering rule) in the schema notes. For any business rule already known to cross aggregates/services, note that
  it is out of scope for a single transaction and point to section 4.
- **Step 10, Business Rules**: for a rule whose `Post-conditions` touch more than one table within the same aggregate,
  state the transaction boundary explicitly (which statements commit together). For a rule whose effects legitimately
  cross aggregates or services, write it as an explicit saga per section 4 — ordered steps, each step's local
  transaction, and each step's compensating transaction — rather than describing it as a single atomic operation that
  isn't actually possible given the aggregate/service boundaries already confirmed.
- **`architecture-implementer`**: wrap the exact statements a Business Rule's transaction boundary names in one database
  transaction (the framework/ORM's transaction API — never manual, ad hoc multi-statement writes with no transaction
  wrapper); implement the named concurrency-control strategy (a conditional `UPDATE ... WHERE version = $2`
  for optimistic, `SELECT ... FOR UPDATE` in the framework's transaction API for pessimistic) exactly as specified,
  including the fixed lock-ordering rule for any multi-row pessimistic lock; wrap a transaction subject to serialization
  failure/deadlock in the bounded retry named above; and never open an HTTP/RPC call to another service from inside an
  open database transaction. For a documented saga, implement each step as its own committed local transaction plus its
  compensating transaction, and implement a named transactional outbox as an `outbox` table write in the same
  transaction as the state change, with a separate relay step/job — not as a direct broker publish call made right after
  the commit.

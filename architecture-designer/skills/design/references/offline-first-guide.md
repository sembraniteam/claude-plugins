# Offline-First Architecture Guide

Guidance for the optional offline-first track. This track is **not mandatory** — see "This track is not mandatory" below
for the deliberate decision test before activating it. In short: it applies when Stage 1–2 describes a mobile app,
field-service tool, PWA, or any application that must let users create or edit data during a meaningfully long offline
period, or when Stage 5 names a client-side embedded database or sync engine specifically for that purpose (never from
the database choice alone — see the decision test). Unlike the Web3 track, offline-sync patterns are stable,
well-established engineering knowledge — recommend concrete patterns and libraries here rather than deferring to
`<VERIFY>` placeholders.

## Core concept

"Offline-first" means the client (mobile app, desktop app, or PWA) treats its **local store as the primary read/write
target**, not the server. Every user action reads from and writes to local storage immediately — the UI never blocks on
network round-trips — and a background sync process reconciles local changes with the server (and other clients)
whenever connectivity is available. This inverts the usual "server is the source of truth, client is a cache" model:
locally, the client *is* the source of truth until sync confirms otherwise.

This is different from merely "handling network errors gracefully." A request-retry wrapper around an online-only app is
resilience, not offline-first. Offline-first requires: (1) a local persistent store the app can fully operate against,
(2) a queue of pending local mutations, (3) a sync protocol that reconciles local and remote state in both directions,
and (4) a conflict-resolution strategy for when the same record was changed in two places before sync ran.

## This track is not mandatory — decide deliberately, don't default into it

Most applications are correctly online-first. Reach for this track only when a genuine offline-write requirement exists,
not merely because the app is mobile, has a local cache, or occasionally loses connectivity — those are common to a
large share of ordinary apps that still don't need anything in this guide.

**Use this track when ALL of these hold:**

1. Users must be able to **create or edit** data with zero connectivity, not just view data fetched earlier.
2. The offline period is meaningfully long — minutes to hours or days — not a dropped packet or a brief network blip a
   retry would cover.
3. Reconciliation happens later and must handle the case where the same record was changed in two places before either
   side synced (the actual hard problem section 3 exists to solve).

**This track does NOT apply — a plain online-first app is correct instead — when:**

- The app only needs to **display previously-fetched data** while offline (a read-only cache) and simply blocks or
  queues writes until connectivity returns with no risk of two divergent versions. This is a caching concern, not
  offline-first.
- Brief connectivity drops are the only concern, and a retry-with-backoff strategy (Stage 5 item 10 — error handling and
  resilience) already covers it. A request-retry wrapper around an online-only app is resilience, not offline-first —
  see "Core concept" above.
- A local/embedded database was chosen for query performance or offline *reads* only, while every write still
  round-trips to the server before it's considered saved (e.g., SQLite used purely as a local cache in front of a
  service that still requires a live connection to write). Naming an embedded database in the stack is not, by itself,
  evidence of an offline-write requirement — confirm the actual write behavior before triggering this track from a Stage
  5 stack choice alone.

## When this track applies

Trigger during Stage 1–2 if the application: is a mobile app expected to work in poor/no connectivity (field service,
logistics, healthcare in remote areas, travel) where users must create or edit records during that time; is a PWA with
an explicit offline-write requirement; supports collaborative editing where clients may diverge before reconciling; or
the user directly asks for "offline mode," "offline sync," or "works without internet" in a way that implies offline
writes, not just offline viewing. **Apply the decision test above to this trigger too** before committing to the track —
a Stage 1–2 description that sounds like one of these (e.g. "mobile app" alone) can still turn out to be a
read-only-cache or brief-connectivity-blip case once the actual write behavior is confirmed. If it only becomes apparent
at Stage 5 (e.g., the user names WatermelonDB/PouchDB or a sync engine specifically for offline-write support), treat
that as the trigger instead — but apply the same decision test first, since naming a client-side embedded database alone
is not sufficient (see above).

## 1. Local storage layer

Pick the embedded store based on client platform and query needs:

| Platform                      | Recommendation                                                                                                                                                                                                                                                                                                                                                    |
|-------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| React Native                  | WatermelonDB (SQLite-backed, built for large datasets + sync) or RxDB                                                                                                                                                                                                                                                                                             |
| iOS native                    | Core Data or GRDB (SQLite wrapper) with a custom sync layer                                                                                                                                                                                                                                                                                                       |
| Android native                | Room (SQLite) with `WorkManager`-driven background sync                                                                                                                                                                                                                                                                                                           |
| Flutter                       | Drift (SQLite)                                                                                                                                                                                                                                                                                                                                                    |
| Web / PWA                     | IndexedDB directly, or Dexie.js / RxDB on top of it; Service Worker for background sync                                                                                                                                                                                                                                                                           |
| Cross-platform, sync included | PouchDB + CouchDB/Cloudant (built-in replication protocol), Firestore (built-in offline persistence + sync), or a comparable vendor mobile-sync platform — this sub-category churns quickly (MongoDB's own Realm/Atlas Device Sync, once a leading option here, was discontinued in 2025); verify a candidate is still actively supported before committing to it |
| Collaborative / rich-text     | Automerge or Yjs (CRDT document stores — see section 4)                                                                                                                                                                                                                                                                                                           |

A store with **built-in sync** (PouchDB/CouchDB, Firestore, or similar) removes most of the custom sync-engine work
below at the cost of coupling to that vendor's backend — weigh that coupling risk against the churn this sub-category
has shown. A plain embedded database (SQLite family, IndexedDB) requires building the outbox/sync-queue and conflict
resolution described next, but keeps the backend technology-agnostic.

## 2. Sync architecture: the outbox pattern

The standard implementation shape, regardless of storage choice:

1. **Local writes are immediate and optimistic.** The UI writes to the local store and renders the change instantly —
   never wait for the network.
2. **Every local write is also appended to an outbox** (a table/collection of pending mutations: entity, operation,
   payload, client-generated timestamp, and a locally unique mutation ID for idempotency).
3. **A background sync process** (triggered on connectivity-regained events, a periodic timer, or app foreground) drains
   the outbox: batches pending mutations, sends them to a sync endpoint, and marks each as synced/failed/conflicted
   based on the response.
4. **Pull path**: the same sync process asks the server for changes since the last successful sync cursor (a
   `last_synced_at` timestamp or a monotonic server-side sequence number — prefer the sequence number, since wall-clock
   cursors are vulnerable to clock skew and can miss records written in the same instant as the cursor), applies them
   locally, and advances the cursor only after they are durably applied.
5. **Idempotency is mandatory**: network retries will resend the same mutation. The server must dedupe by the
   client-generated mutation ID (or use `INSERT ... ON CONFLICT DO NOTHING`-style upserts) so a retried push never
   double-applies.

**Client-generated IDs**: records created offline need an ID before the server has ever seen them, so use
client-generated UUIDs (v4 or v7) as primary keys rather than server-assigned auto-increment IDs. This also removes the
need for an "ID remapping" step after first sync.

## 3. Conflict detection and resolution — handling divergent `updated_at`

This is the central hard problem: two clients (or a client and a concurrent server-side change) edit the same record
while offline, and sync later discovers both versions claim to be newer. The strategy must be chosen deliberately and
stated in the architecture document — do not leave it implicit.

### 3a. Last-Write-Wins (LWW) by `updated_at` — the default, with its failure mode named explicitly

The simplest strategy: each record carries an `updated_at` timestamp; whichever write has the greater timestamp wins,
and the loser is silently discarded (or kept as a shadow copy for audit). This is adequate for low-contention data
(personal settings, single-owner records) but has a well-known failure mode that must be surfaced to the user, not
hidden:

- **Client clock skew is the actual risk, not a theoretical one.** If `updated_at` is set by the client device's clock,
  a device with a fast/wrong clock can make a genuinely older edit look newer and silently overwrite a real, later
  change — with no error, no conflict flagged, just quiet data loss.
- **The fix**: never trust a client-supplied `updated_at` as the field used for LWW comparison. Let the client send its
  local edit timestamp for UI purposes only; the **server assigns the authoritative `updated_at`** at the moment it
  durably commits the write (`UPDATE ... SET updated_at = now()` server-side, or a DB trigger), and LWW comparisons
  during sync use that server-assigned value, never the client's. This turns "which of two client clocks do we trust"
  into "which write reached the server first," which is deterministic and doesn't depend on device clock accuracy.
- Even with a server-assigned timestamp, two offline clients can each believe their edit is "the latest they knew
  about" — LWW's job is only to pick a deterministic winner, not to guarantee the winner is the semantically correct
  merge. State this trade-off explicitly wherever LWW is chosen: it guarantees convergence (every client ends up with
  the same value), not correctness (the discarded edit may have been the one the user actually wanted kept).

### 3b. Version counters for real conflict *detection* (optimistic concurrency)

`updated_at` alone tells you which write is newer; it does not tell you whether the writes actually conflict (a true
conflict is when the client's write was based on a version the server no longer has — a stale read-modify-write). Add an
integer `version` column, incremented by the server on every successful write. The client must send back the `version`
it last read; the server accepts the write only if it still matches (compare-and-swap):

```sql
UPDATE orders
SET status     = $1,
    version    = version + 1,
    updated_at = now()
WHERE id = $2
  AND version = $3;
-- 0 rows affected => the client's base version is stale => real conflict, not just "an update happened"
```

This is the mechanism that should actually gate whether a write is auto-resolved via LWW or routed to conflict handling
(3c/3d/3e) — `updated_at` tells you who's newer, `version` tells you whether there's a conflict to resolve at all. Use
both together rather than `updated_at` alone: many "conflicts" caught by version-mismatch are not conflicts (the
client's stale read happened to match what the server already has), and LWW-only systems either resolve those silently
(fine) or, without a version check, cannot distinguish a real conflict from a harmless double-apply of a retried
request.

### 3c. Field-level merge instead of record-level overwrite

A naive LWW implementation replaces the *entire record* with whichever write is newer, which discards unrelated field
edits made by the other write (e.g., client A changed `address`, client B concurrently changed `phone` — record-level
LWW loses one of the two). Where the schema and update patterns allow it, resolve conflicts **per field**, not per
record: track (or infer, if each write's diff is known) which fields each write actually touched, and merge
non-overlapping field changes automatically; only fields both writes touched need LWW or manual resolution. This is
significantly more implementation effort and should be scoped to the entities where concurrent partial edits are
actually likely (user profiles, shared documents) rather than applied universally.

### 3d. CRDTs — when merge must be automatic and lossless

For genuinely collaborative data (shared text documents, shared lists/counters edited concurrently by multiple users
while offline), Conflict-free Replicated Data Types make convergent, automatic merging structurally guaranteed rather
than a policy choice — every replica is mathematically guaranteed to converge to the same state without a central
arbiter. Reach for a CRDT library (Yjs or Automerge for rich text/JSON documents; Redis CRDTs — Redis Enterprise/Redis
Cloud Active-Active only, not available in open-source Redis/Valkey/DragonflyDB — or Riak, maintained today via the
OpenRiak community fork, for counters/sets at the database layer) only when the data model genuinely needs concurrent
multi-writer merging — it is a larger architectural commitment (the CRDT becomes the document's storage format, not just
a sync detail) and is overkill for typical CRUD entities where LWW + version-conflict detection is sufficient.

**Not every CRDT is lossless, and "lossless" is not the same as "semantically correct."** An LWW-Register CRDT is still
a CRDT by the formal definition (it satisfies the convergence guarantee), but it resolves each concurrent write by
discarding the loser — the exact same silent-data-loss failure mode named in 3a, just relabeled. The libraries
recommended above avoid that failure mode because they use merge structures that keep both sides of a concurrent edit
(multi-value registers, OR-Sets for lists, RGA-style interleaving for text) rather than picking one write as the
winner — that is what "lossless" means here: no concurrent write is silently dropped. It does not mean the automatic
merge result is guaranteed to match either user's intent — two people concurrently editing the same sentence in a text
CRDT will both have their keystrokes preserved, but the interleaved result can still read as nonsense and may need human
review. State this distinction wherever a CRDT is chosen: it guarantees no data is discarded, not that the merge is
meaningful.

### 3e. Manual conflict resolution UI

For high-value or irreversible data (financial records, medical records, anything where silently picking a winner is
unacceptable), do not auto-resolve at all: when the version check in 3b detects a real conflict, surface both versions
to the user (or a reviewer) and let them choose or merge manually. This is the correct default whenever the cost of a
wrong automatic resolution exceeds the cost of asking.

### 3f. Deletes need tombstones, not hard deletes

A record hard-deleted locally or on the server cannot be "synced" to other clients — there's nothing left to compare
timestamps against. Use soft deletes: a `deleted_at` (or `is_deleted` + `updated_at`) column that participates in sync
like any other field update. Clients apply a tombstone by removing the record locally; a genuinely permanent purge
(removing the tombstone row itself) only happens after enough time has passed that all clients are assumed to have
synced it, or via an explicit retention/GC job — never as the direct result of the delete operation.

This is the same `deleted_at` column the database-designer agent adds for general soft-delete support (its Step 2) — an
offline-synced table does not get two separate delete-tracking columns. The general mechanics apply identically here:
the mandatory `WHERE deleted_at IS NULL` default scope, the partial-unique-index adjustment for any `UNIQUE` constraint,
and the compliance-driven purge policy. The only thing this track adds on top is that the tombstone must also flow
through the sync protocol itself (push/pull), not just filter local reads.

## 4. Schema additions this track requires

When this track is active, the database-designer agent adds these to every SQL table that participates in offline sync
(not to tables that are server-only, e.g., internal admin/audit tables never touched by an offline client):

| Column                        | Type                                 | Purpose                                                                    |
|-------------------------------|--------------------------------------|----------------------------------------------------------------------------|
| `id`                          | `UUID` (client-generatable)          | Allows offline record creation without a server round-trip                 |
| `updated_at`                  | `TIMESTAMP WITH TIME ZONE`           | **Server-assigned**, never trusted from the client — see 3a                |
| `version`                     | `BIGINT`, default 1                  | Server-incremented on every write; used for compare-and-swap — see 3b      |
| `deleted_at`                  | `TIMESTAMP WITH TIME ZONE`, nullable | Tombstone for sync-safe deletes — see 3f                                   |
| `origin_device_id` (optional) | `TEXT`, nullable                     | Attribution for debugging conflicting writes; not used in resolution logic |

Index `updated_at` (or a dedicated `sync_cursor`/sequence column, if used instead — see section 2 point 4) for the
pull-sync query's `WHERE updated_at > $cursor` scan.

## 5. Sync API shape

Document this as part of the architecture's API contracts (Stage 5 / LLD): a dedicated sync endpoint, not the same CRUD
endpoints used for direct (online) access, since sync operates in batches with cursor and conflict semantics that
ordinary REST CRUD does not need.

- `POST /sync/push` — body: batch of `{ mutationId, entity, operation, payload, clientVersion }`. Response: per-mutation
  result — `applied`, `conflict` (with the server's current version of the record), or `rejected` (validation failure).
- `GET /sync/pull?since={cursor}` — response: `{ changes: [...], cursor: <new cursor> }`, paginated if the change set is
  large. The client only advances its stored cursor after successfully applying and persisting the returned batch.

## 6. What to verify before deployment

State these explicitly in the architecture document rather than assuming they'll be caught later: a test plan that
simulates two clients editing the same record while both offline, then both reconnecting (verifies the conflict path,
not just the happy path); a test for a device with a deliberately wrong clock (verifies the server-assigned-timestamp
fix in 3a actually holds); and a test for a push retried after a dropped response (verifies idempotency via mutation ID,
per section 2 point 5).

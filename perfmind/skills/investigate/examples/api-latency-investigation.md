# Example: API Latency Investigation Output

**User provided:** p99 latency of 2,800ms on `POST /api/orders`, p50 is 120ms. No recent deploys. Pasted a slow-query log showing `SELECT * FROM order_items WHERE order_id = ?` running 200–400ms per call.

**After gathering evidence and running multi-domain analysis (Step 3):**

---

**App type & scope:** API/Backend — Node.js order service, PostgreSQL database, analysis focused on database and response time domains.

The primary bottleneck is an N+1 query pattern in the order detail endpoint. Each call to `POST /api/orders` triggers between 8 and 35 sequential `SELECT` queries against `order_items`, one per item in the order. The tail latency spread (p50=120ms vs p99=2,800ms) matches large-order variance, confirming that query count — not a fixed overhead — is driving the tail.

**Findings:**

1. **N+1 query on order items** `[Database]`
   - Evidence: slow-query log shows 8–35 identical `SELECT * FROM order_items WHERE order_id = ?` per request
   - Fix: replace with a single `SELECT * FROM order_items WHERE order_id IN (?)` batch query or ORM eager-load

2. **`SELECT *` on hot path** `[Database]`
   - Evidence: query fetches all 14 columns; response only uses 4 (`id`, `sku`, `quantity`, `price`)
   - Fix: project only required columns to reduce data transfer and serialization cost

3. **Missing index on `order_items.order_id`** `[Database]`
   - Evidence: `EXPLAIN ANALYZE` shows sequential scan on 2.1M-row table
   - Fix: `CREATE INDEX CONCURRENTLY idx_order_items_order_id ON order_items(order_id)`

Run `/perfmind:report` to get role-specific recommendations, or ask the `performance-analyst` agent for a deep dive into one domain.

---

**Notes on this example:**
- Step 4 output is brief and structured — no narrative prose before the four-part block
- Evidence cites concrete metrics (p50/p99 numbers, row counts, column counts)
- Domain tags are included per finding
- Closing prompt invites next step without being prescriptive

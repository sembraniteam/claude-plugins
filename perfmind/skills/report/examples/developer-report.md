# Example: Developer Report Output

**Findings in conversation** (from a prior `/perfmind:investigate` session on an API latency issue):

1. N+1 query on order items — 8-35 sequential `SELECT` queries per request against `order_items`
2. `SELECT *` on hot path — fetches 14 columns, only 4 used
3. Missing index on `order_items.order_id` — sequential scan on a 2.1M-row table

**Detected role:** Developer (user said "give me actionable fixes as a developer")

**Generated report:**

---

## Performance Report — Developer

### Critical (fix this sprint)
- **N+1 query on order items**: Each `POST /api/orders` call triggers 8-35 sequential `SELECT` queries against `order_items`, one per item in the order.
  Fix: Replace with a single `SELECT * FROM order_items WHERE order_id IN (?)` batch query or ORM eager-load.
  Evidence: Slow-query log shows repeated identical queries per request; p99 (2,800ms) vs p50 (120ms) spread matches order-size variance.
- **Missing index on `order_items.order_id`**: Sequential scan on a 2.1M-row table on every lookup.
  Fix: `CREATE INDEX CONCURRENTLY idx_order_items_order_id ON order_items(order_id)`.
  Evidence: `EXPLAIN ANALYZE` shows `Seq Scan` instead of `Index Scan`.

### High Priority
- **`SELECT *` on hot path**: Query fetches all 14 columns; response only uses 4 (`id`, `sku`, `quantity`, `price`).
  Fix: Project only required columns to reduce data transfer and serialization cost.
  Evidence: Response payload inspection shows unused fields.

### To Watch
- None identified yet — re-run `/perfmind:investigate` after the above fixes to check for new bottlenecks.

### Implementation Checklist
1. [ ] Add composite/single-column index on `order_items.order_id` — run `EXPLAIN ANALYZE` before and after to confirm the scan type changes
2. [ ] Replace N+1 query loop with a batched `IN (?)` query or ORM eager-load
3. [ ] Trim `SELECT *` to the 4 columns actually used in the response
4. [ ] Re-measure p99 latency on `POST /api/orders` after deploying; confirm it approaches p50

---

**Notes on this example:**
- Each finding maps directly to a conversation finding — no invented metrics or guesses
- Fixes are specific and actionable (exact SQL/index commands, not vague advice)
- Checklist items are ordered by dependency (index and batching first, since they address the largest latency contributors)
- No jargon-free rewriting needed here — Developer reports keep technical terms as-is, unlike Leadership reports

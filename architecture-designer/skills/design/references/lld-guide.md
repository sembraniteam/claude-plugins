# Low-Level Design Guide

Use this guide when executing Step 10 — Low-Level Design. It defines the format and content rules for each LLD artifact. Work through the artifacts in the order listed below.

---

## 1. API Contracts

Document every endpoint that appears in a sequence diagram. An endpoint not in the sequence diagram does not need an API contract yet.

### Format

For each endpoint, use this template:

```
### POST /auth/login

| Field        | Value                        |
|--------------|------------------------------|
| Method       | POST                         |
| Path         | /auth/login                  |
| Auth         | None                         |
| Rate limit   | 10 req/min per IP            |
| Description  | Authenticates a registered user and returns a JWT |

**Request**

| Field     | Type   | Required | Validation            |
|-----------|--------|----------|-----------------------|
| email     | string | yes      | valid email format    |
| password  | string | yes      | 8–128 characters      |

**Responses**

| Status | Body                                       | When                          |
|--------|---------------------------------------------|-------------------------------|
| 200    | `{ token: string, expiresAt: ISO8601 }`    | Credentials valid             |
| 400    | `{ error: "VALIDATION_ERROR", fields: [] }` | Missing or malformed fields   |
| 401    | `{ error: "INVALID_CREDENTIALS" }`         | Wrong email or password       |
| 429    | `{ error: "RATE_LIMITED", retryAfter: int }`| Too many attempts             |
| 500    | `{ error: "INTERNAL_ERROR" }`              | Unexpected server fault       |
```

### Rules

- Derive every endpoint from the sequence diagrams — do not invent new ones
- Auth field values: `None`, `Bearer JWT`, `API Key (header)`, `API Key (query)`, `Session cookie`
- Rate limit only if mentioned in NFRs or capacity planning — otherwise omit the row
- Always include at least 400, 401/403 (if auth required), and 500 responses
- Use JSON field paths for nested bodies (e.g., `address.city`)
- For file uploads: note `Content-Type: multipart/form-data` and max size

---

## 2. Business Rules

Document non-trivial logic blocks visible in the sequence diagrams — anything that has conditional branches, aggregation, or external side effects beyond a simple CRUD operation.

### Format

```
### Calculate Order Total

**Trigger:** `POST /orders` request received  
**Pre-conditions:**
- Cart is non-empty
- All cart items are still in stock

**Logic:**
1. Sum `(unit_price × quantity)` for each cart item → `subtotal`
2. If user has an active promo code, apply discount:
   - Percentage discount: `subtotal × (1 − discount_rate)`
   - Fixed discount: `MAX(subtotal − fixed_amount, 0)`
3. Calculate tax: `discounted_subtotal × tax_rate` (rate from user's region)
4. Shipping fee: free if `subtotal >= free_shipping_threshold`, else flat rate from config
5. `total = discounted_subtotal + tax + shipping`

**Post-conditions:**
- Order row created with status `PENDING`
- Inventory reserved (not decremented until payment confirmed)
- Cart cleared

**Edge cases:**
- Promo code expired → reject with `PROMO_EXPIRED`
- Item out of stock between cart add and checkout → reject with `ITEM_UNAVAILABLE`, list affected items
- Total rounds to zero after discount → reject with `ZERO_AMOUNT_ORDER`
```

### Rules

- Only write rules for non-trivial logic — simple CRUD (create user, get product) does not need a rule
- Identify the trigger from the sequence diagram (which message or event starts this logic)
- Edge cases must include the exact error code from the Error Catalog (write that section first if needed)

---

## 3. Data Transfer Objects (DTOs)

Write DTOs for complex bodies that appear in multiple endpoints or have nested structures. Simple flat objects (login request, ID-only response) do not need a separate DTO definition.

### Format

```
### OrderLineItem

Used in: `POST /orders` request body, `GET /orders/:id` response

| Field       | Type    | Required | Constraints               | Description              |
|-------------|---------|----------|---------------------------|--------------------------|
| productId   | UUID    | yes      | must exist in products    | Product being ordered    |
| quantity    | integer | yes      | 1–99                      | Units to purchase        |
| unitPrice   | decimal | yes      | > 0, 2 decimal places     | Price at time of order   |
| discount    | decimal | no       | 0.00–1.00, default: 0     | Line-level discount rate |
```

### Rules

- Reference DTOs by name in the API contracts: e.g., "Request body: `OrderLineItem[]`"
- Define arrays as `TypeName[]`
- Use concrete types: `string`, `integer`, `decimal`, `boolean`, `UUID`, `ISO8601`, `object`, `array`

---

## 4. Inter-Service Contracts (microservices / event-driven only)

Skip this section entirely if the architecture is a monolith or modular monolith.

Document every event or message that flows between services. Derive these from the sequence and business-process diagrams.

### Format

```
### order.created (event)

**Broker:** Kafka topic `orders.events` (partition key: `orderId`)  
**Producer:** Order Service  
**Consumers:** Inventory Service, Notification Service, Analytics Service

**Payload schema:**

| Field       | Type     | Description                          |
|-------------|----------|--------------------------------------|
| eventId     | UUID     | Unique event identifier              |
| eventType   | string   | Always `order.created`               |
| occurredAt  | ISO8601  | When the order was placed            |
| orderId     | UUID     | The new order's ID                   |
| customerId  | UUID     | Customer who placed the order        |
| lines       | array    | `OrderLineItem[]` (see DTOs)         |
| totalAmount | decimal  | Pre-calculated total                 |

**Consumer obligations:**
- Inventory Service: reserve stock within 30 s; emit `inventory.reserved` or `inventory.failed`
- Notification Service: send order confirmation email within 60 s; idempotent on retry
- Analytics Service: append to analytics pipeline; failures silently logged, not retried
```

### Rules

- Every event must have exactly one producer
- Consumers must describe their SLA and idempotency guarantee
- If using request/reply over messaging (not HTTP), document the reply topic and correlation ID
- For REST-over-HTTP inter-service calls, use the API contract format instead

---

## 5. Error Catalog

A single table of all application-level error codes. Derive entries from the API contracts above.

### Format

```markdown
## Error Catalog

| Code                  | HTTP Status | Message                                 | Description                                        | Recovery                           |
|-----------------------|-------------|-----------------------------------------|----------------------------------------------------|------------------------------------|
| `VALIDATION_ERROR`    | 400         | Invalid request fields                  | One or more fields failed validation; see `fields` | Fix the highlighted fields         |
| `INVALID_CREDENTIALS` | 401         | Email or password is incorrect          | Authentication failed                              | Re-enter credentials               |
| `TOKEN_EXPIRED`       | 401         | Session has expired                     | JWT past its `exp` claim                           | Re-authenticate                    |
| `FORBIDDEN`           | 403         | You do not have access to this resource | Authenticated but lacks permission                 | Contact admin or use correct role  |
| `NOT_FOUND`           | 404         | Resource not found                      | The requested entity does not exist                | Verify the ID                      |
| `CONFLICT`            | 409         | Resource already exists                 | Duplicate unique field                             | Use a different value              |
| `RATE_LIMITED`        | 429         | Too many requests                       | Rate limit exceeded; check `retryAfter`            | Wait and retry                     |
| `PROMO_EXPIRED`       | 422         | Promo code has expired                  | Business rule violation                            | Remove promo code or use another   |
| `ITEM_UNAVAILABLE`    | 422         | One or more items are out of stock      | Items went out of stock since cart was loaded      | Remove unavailable items           |
| `INTERNAL_ERROR`      | 500         | An unexpected error occurred            | Unhandled server fault                             | Retry; contact support if persists |
```

### Rules

- Every error code referenced in an API contract must appear in this catalog
- HTTP status must match the standard semantics (400 client error, 5xx server error)
- "Recovery" is written for the end user, not the developer
- System-level errors (`INTERNAL_ERROR`) are the only entries where the description can be vague — the actual error is logged server-side, not exposed to clients

---

## Section order in the architecture document

When writing section 10 (Low-Level Design) in the architecture document, use this order:

1. **API Contracts** — one sub-section per endpoint, grouped by resource (auth, users, orders, etc.)
2. **Business Rules** — one sub-section per rule, ordered from most fundamental to most derived
3. **Data Transfer Objects** — only complex/shared DTOs; simple flat bodies are documented inline in API contracts
4. **Inter-Service Contracts** — omit entirely for monoliths
5. **Error Catalog** — always last; a single table covering all codes referenced above

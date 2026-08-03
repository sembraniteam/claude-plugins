# Domain-Driven Design (DDD) Guide

Use this guide at the start of Stage 6a, before spawning `database-designer`, per `design/SKILL.md`. It defines the
lightweight bounded-context modeling step every project runs — scaled to the system's actual complexity, never skipped
entirely — and how its output (`domainModel`) constrains the schema `database-designer` produces.

## Why this matters

A schema designed by grouping "nouns that seem related" rather than by explicit domain boundaries tends to grow
unplanned cross-cutting foreign keys and unclear transaction scope — two tables that are actually independent concerns
end up sharing one transaction because nothing ever forced the question "should these commit together?" DDD's
bounded-context/aggregate vocabulary exists to force that question once, at design time, instead of discovering the
answer from a production race condition.

## When this applies

Every project runs this step — it is not an optional track like the Web3 or offline-first tracks. It scales down, not
away: a small system may honestly have one bounded context with one or two aggregates, and that is a complete, correct
answer, not a skipped step. State the scale-down explicitly ("single bounded context — this system has one cohesive
domain with no natural sub-domain split") rather than omitting the section.

## Step 1 — Identify bounded contexts

A bounded context is a boundary within which a specific domain model and its terminology apply consistently — the same
word can mean different things in different contexts (e.g. "Order" in a sales context vs. a fulfillment/shipping
context), and that's a signal for a context boundary, not a naming bug to fix.

Derive candidate contexts from Stage 1's business processes and Stage 2's functional requirements: group functional
requirements that share the same core nouns and the same team/workflow ownership into one context; a requirement that
uses the same noun differently, or is owned by a clearly separate workflow (e.g. "billing" vs. "inventory" vs.
"fulfillment"), suggests a separate context. For an architecture pattern that is already microservices or event-driven
(Stage 5 item 1), bounded contexts frequently — but not always — map one-to-one onto services; for a monolith or modular
monolith, they map onto internal module boundaries within the single deployable, not separate services.

## Step 2 — Identify aggregates within each context

Within each bounded context, identify aggregates: a cluster of entities and **value objects** (immutable objects defined
entirely by their attributes, with no identity of their own — e.g. a `Money` amount+currency pair, an
`Address`) treated as a single unit for data changes, with one entity as the **aggregate root** (the only member other
code is allowed to reference directly) and a set of **invariants** — business rules that must hold true at the end of
every transaction touching the aggregate (e.g. "an Order's line-item total must equal its stated total," "a StockItem's
quantity must never go negative").

**Sizing rule**: an aggregate should be the smallest cluster that still lets every invariant be enforced within one
transaction. A single aggregate containing the entire domain graph makes every write contend on the same lock; an
aggregate so small that enforcing one invariant requires touching three separate aggregates in one transaction pushes
consistency logic into application code where it's easy to get wrong. When genuinely unsure, prefer the smaller
aggregate and handle cross-aggregate consistency via a **domain event** (an immutable record of something that already
happened in the domain — e.g. `OrderPlaced` — published so other aggregates or bounded contexts can react to it
asynchronously) or a follow-up command rather than merging them — the same "smallest change that closes the requirement"
bias this plugin applies elsewhere.

## Step 3 — Record the ubiquitous language

For each bounded context, list the domain terms whose meaning is specific to that context (not general English) — short
glossary entries, one line each. This is what keeps the Stage 5 justifications, the diagrams, the schema, and the final
document using the same word for the same concept instead of drifting ("Order" vs. "Purchase" vs. "Cart" for the same
entity across different sections).

## Step 4 — Map relationships between contexts

Only applies when Step 1 identified 2 or more bounded contexts — skip entirely for a single-context system. For every
pair of contexts that actually integrate (one reads or reacts to the other's data or events), name the integration
pattern using the standard DDD vocabulary — the same list `references/diagrams-guide.md`'s Context Map Diagram section
uses: **Partnership**, **Shared Kernel**, **Customer/Supplier**, **Conformist**, **Anticorruption Layer**, **Open Host
Service**, **Published Language**, or **Separate Ways**. Get the upstream/downstream direction right for the five
asymmetric patterns (Customer/Supplier, Conformist, Anticorruption Layer, Open Host Service, Published Language) — it
determines which team's model the integration defers to, not just that an integration exists. Decide this now, as a
domain-modeling decision, rather than inventing it later when the Context Map diagram is generated — same discipline as
recording an architectural driver's rationale at the point it's decided, not reconstructed afterward.

## Step 5 — Confirm and persist

Present the bounded contexts, their aggregates (root, entities, invariants), the ubiquitous language, and (when 2+
contexts) the relationships between them, to the user for confirmation — same pattern as every other Stage 1–6 sub-step.
Once confirmed, write to `session.json`'s top-level `domainModel`:

```json
{
  "boundedContexts": [
    {
      "name": "Inventory",
      "description": "Tracks stock levels and warehouse locations",
      "aggregates": [
        {
          "name": "StockItem",
          "rootEntity": "StockItem",
          "entities": [
            "StockItem",
            "StockMovement"
          ],
          "invariants": [
            "quantity must never go negative",
            "every StockMovement must reference a valid StockItem"
          ]
        }
      ],
      "ubiquitousLanguage": {
        "SKU": "Stock keeping unit, the unique identifier for a distinct product/variant"
      }
    },
    {
      "name": "Orders",
      "description": "Handles cart, checkout, and order lifecycle"
    }
  ],
  "relationships": [
    {
      "from": "Orders",
      "to": "Inventory",
      "pattern": "Customer/Supplier",
      "description": "Orders is the customer — Inventory's stock-reservation API must prioritize Orders' checkout-latency needs"
    }
  ]
}
```

`relationships` is omitted entirely for a single-bounded-context system. See `references/session-schema.md` for exactly
when this is written relative to `stage6a`.

## How this feeds `database-designer`

Pass `domainModel` to `database-designer` alongside the existing Stage 6a inputs. It constrains Step 2 (Schema design)
of that agent's process:

- **One transactional-consistency boundary per aggregate** — tables belonging to one aggregate may share a transaction;
  a write that needs to touch two different aggregates' tables atomically is a signal the aggregate boundary was drawn
  wrong, not a normal multi-table transaction.
- **Cross-aggregate references are by ID, never by embedding** — a `StockItem` referencing a `Supplier` (a different
  aggregate) stores `supplier_id`, not a copy of supplier fields; this is standard normalization, but DDD gives the
  additional reason: the aggregate that isn't the source of truth for a field should never hold a mutable copy of it.
- **Cross-bounded-context references are eventually consistent for event-driven/microservices patterns** — when Stage 5
  named an event-driven or microservices architecture pattern, a reference from one bounded context's aggregate to
  another context's entity is not a same-transaction FK at all; it's an ID reference kept in sync via a domain event,
  and the schema notes should say so explicitly rather than modeling it as an ordinary FK.

## Relationship to the class diagram and context map

`references/diagrams-guide.md`'s Class Diagram section already triggers on "DDD aggregates, complex business rules" —
when a class diagram is generated for a bounded context with a non-trivial domain model, use the aggregates and
invariants from `domainModel` directly as its content, rather than re-deriving the domain model from scratch at the
diagram-generation step. These two diagrams cover different scopes: the Class Diagram shows the aggregates *within*
one bounded context; when `domainModel.boundedContexts` has 2 or more entries, also generate
`references/diagrams-guide.md`'s Context Map Diagram, which shows the integration pattern (the same eight-pattern
vocabulary from Step 4 above) *between* contexts — this diagram's content is exactly Step 4's confirmed `relationships`,
not something to be invented fresh at diagram-generation time.

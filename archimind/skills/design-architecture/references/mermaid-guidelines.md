# Mermaid Diagram Guidelines

## Diagram Type Selection

| Use case                     | Diagram type      |
|------------------------------|-------------------|
| System / service topology    | `flowchart TD`    |
| Database entity-relationship | `erDiagram`       |
| Request / event flow         | `sequenceDiagram` |

## General Rules

- Keep diagrams focused: **8–15 nodes maximum**. Split into multiple diagrams rather than squeezing everything in.
- Label all edges with action verbs: "calls", "publishes to", "reads from", "caches in", "subscribes to"
- Use subgraphs to group related nodes (e.g., `subgraph "Client Tier"`)
- Every node label should be a noun (service, component, or store name)

## Architecture Diagrams (`flowchart TD`)

- Show all services/components and their primary communication paths
- Include non-relational stores (cache, search index, message queue, object storage) alongside relational ones
- Avoid showing internal implementation detail — only inter-component connections
- For review workflows: mark **changed or new** components with `[NEW]` or `[UPDATED]` suffixes in their labels
- For review workflows: mark **problematic** current-state nodes with `⚠` in the label (Before diagram only)

## ERD (`erDiagram`)

- Include every table in the final schema
- Show all relationships with correct cardinality notation (`||--o{`, `}o--||`, etc.)
- Annotate primary keys with `PK` and foreign keys with `FK`
- Place the ERD in the `## ERD` section only — not inside `## Architecture Diagram` options

## Syntax Checklist

```mermaid
flowchart TD
  subgraph "External"
    Client([Client])
  end
  subgraph "API Layer"
    API[API Gateway]
  end
  subgraph "Data"
    DB[(PostgreSQL)]
    Cache[(Redis)]
  end
  Client -->|HTTP| API
  API -->|reads from| DB
  API -->|caches in| Cache
```

- Use `[Label]` for rectangular nodes (services)
- Use `([Label])` for rounded rectangle (clients, end users)
- Use `[(Label)]` for database cylinder shape
- Use `{Label}` for decision diamond (rarely needed in topology diagrams)
- Wrap subgraph labels in double quotes if they contain spaces

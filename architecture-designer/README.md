# architecture-designer

Guided architecture and infrastructure design workflow for Claude Code — from requirements gathering to code implementation, with interactive Mermaid diagrams, browser preview, and structured documentation.

## Skills

### `/architecture-designer:design`

Runs the full six-stage design process:

1. **Requirements gathering** — application goals, stakeholders, business processes, success criteria
2. **Requirements analysis** — functional vs non-functional requirements (performance, security, scalability, availability)
3. **Feasibility study and constraints** — budget, timeline, regulations, team competencies, legacy integrations
4. **Capacity planning** — users, TPS, data volume, peak load, growth projections
5. **Technology selection** — stack, architecture pattern, database, infrastructure; every choice justified against stages 1–4
6. **Diagram generation** — Mermaid diagrams rendered in the browser with zoom/pan/download

Produced artifacts:
- Browser preview at `http://localhost:<port>` with zoomable, downloadable PNG diagrams
- `docs/architecture-designer/architecture/{ddmmyyyy}-{topic}.md` — complete, reviewed, and approved architecture document

### `/architecture-designer:review`

Reviews and revises an existing architecture:
- Document-based review (reads `docs/architecture-designer/architecture/`)
- Codebase-based review (scans project structure, reconstructs actual architecture)
- Drift detection (compares document against codebase)
- Revision flow with new versioned document, preserving full history

## Sub-agents

| Agent                                            | Role                                                                                                          |
|--------------------------------------------------|---------------------------------------------------------------------------------------------------------------|
| `architecture-designer:architecture-reviewer`    | Validates diagrams for technical correctness, cross-diagram consistency, requirements traceability, and risks |
| `architecture-designer:database-designer`        | Designs schema, ERD, index plan, engine selection, and secure connection config for SQL and NoSQL             |
| `architecture-designer:document-reviewer`        | Audits saved documents for format compliance and content completeness                                         |
| `architecture-designer:architecture-implementer` | Implements project skeleton, data models, routes, and infrastructure files from an approved document          |

## Scripts

All scripts are Node.js ESM (`.mjs`) with no external dependencies. They run identically on Windows, macOS, and Linux.

```bash
# Find a free port in 3000–9000
node scripts/find-port.mjs

# Start the preview server (opens browser automatically)
node scripts/preview-server.mjs <port>
```

The preview server reads `docs/architecture-designer/diagrams.json` on every request. Reload the browser page to see diagram updates without restarting the server.

## Document format

Architecture documents are saved to:
```
docs/architecture-designer/architecture/{ddmmyyyy}-{topic}.md
```

Every document begins with a metadata table:

| Date        | Version | Status   | Reason | Previous Document |
|-------------|---------|----------|--------|-------------------|
| 05-Jul-2026 | 1.0     | Approved | -      | -                 |

Revisions create new files (never overwrite), with `Version` incremented, `Reason` filled, and `Previous Document` pointing to the revised file.

## Diagram types

| Diagram          | Mermaid type                       | When created                     |
|------------------|------------------------------------|----------------------------------|
| Use case         | `flowchart`                        | Multiple user roles              |
| Business process | `flowchart TD`                     | Complex multi-step workflows     |
| ERD              | `erDiagram`                        | SQL databases                    |
| Sequence         | `sequenceDiagram`                  | Auth flow + main transaction     |
| Class            | `classDiagram`                     | Rich domain model                |
| State            | `stateDiagram-v2`                  | Entities with status lifecycles  |
| C4 Context       | `C4Context`                        | External actors and integrations |
| C4 Container     | `C4Container`                      | Multiple deployable components   |
| Deployment       | `flowchart` or `architecture-beta` | Cloud/infrastructure layout      |

All diagrams support zoom in/out/reset (mouse wheel, pinch, buttons) and PNG download.

# Archimind

AI-powered architecture, database, and feature designer for Claude Code. Gathers requirements, commits to a direct recommendation, and visualizes everything with an interactive Mermaid JS diagram viewer running locally in your browser.

## Features

- **Design Architecture** — Gather requirements, produce a direct architecture recommendation with C4 context diagram, Infrastructure Layout, Request Flow, and Logical Architecture diagrams, tech stack table, SPOF analysis, observability strategy, and ADR.
- **Review Architecture** — Audit an existing system against a 12-category checklist, identify antipatterns by name, and recommend a targeted redesign with Before/After diagrams, migration path, and ADR.
- **Design Database** — Design new schemas or normalize existing SQL DDL. Includes ER diagrams, table specs, index strategy, normalization analysis, and security controls.
- **Design Feature** — Plan a new feature or module within an existing application. Recommends a direct implementation approach with Feature Integration and Feature Flow diagrams, testing strategy, conditional ERD, and ADR.
- **Visualize** — Run a local static site viewer with Mermaid JS rendering, sidebar section nav, and pan/zoom/PNG-download controls for every diagram.

## Requirements

- **Python 3** — Required for the local HTTP server (`python3 -m http.server`)
- **Claude Code** — This plugin targets the Claude Code CLI/IDE

## Installation

### Option A: Marketplace (once published)

```bash
cc plugin install archimind
```

### Option B: Local

```bash
cc --plugin-dir /path/to/archimind
```

### Option C: Project-level

Copy or symlink the plugin directory into your project's `.claude-plugin/` directory.

## Usage

### Design a new architecture

Say any of:
- "Design an architecture for my e-commerce platform"
- "Help me architect a real-time chat app"
- "What architecture should I use for a SaaS multi-tenant system?"

Claude asks clarifying questions, confirms a requirements summary, then commits to a direct architecture recommendation with diagrams, tech stack, and a full Architecture Decision Record. The design is saved to `docs/archimind/architecture/`.

### Review an existing architecture

Say any of:
- "Review my current architecture"
- "Audit my system design — here's the current setup: ..."
- "What's wrong with my architecture?"

Claude analyzes your existing system against a structured checklist, identifies antipatterns by canonical name, and recommends a targeted redesign with Before/After diagrams and a phased migration path.

### Design or normalize a database

Say any of:
- "Design a database for a blog platform"
- "Normalize this schema: `CREATE TABLE ...`"
- "What indexes should I add to my users table?"

Paste your SQL DDL directly in the chat for normalization. Output includes an ERD, table specifications, index recommendations, and database security controls.

### Design a new feature or module

Say any of:
- "Design a notification feature for my app"
- "How should I implement this feature?"
- "Plan the implementation of the checkout module"

Claude gathers requirements and existing application context, then commits to a direct implementation recommendation with integration and flow diagrams, testing strategy, and an ADR. The design is saved to `docs/archimind/features/`.

### Open the diagram viewer

Say any of:
- "Visualize the architecture"
- "Open the diagram viewer"
- "Start the server"

The viewer opens at `http://localhost:{available-port}`.

### Stop the viewer

Say: "Stop the server" or "Close the viewer"

Or run directly:
```bash
bash "$CLAUDE_PLUGIN_ROOT/scripts/stop-server.sh"
```

### Re-open a saved document

```bash
bash "$CLAUDE_PLUGIN_ROOT/scripts/open-doc.sh" docs/archimind/architecture/{filename}.md
```

## Output Files

All design documents are saved to `docs/archimind/` after the user confirms the recommendation:

```
docs/archimind/
├── architecture/
│   ├── {timestamp_ms}-{topic}.md           ← new architecture design
│   └── {timestamp_ms}-{topic}-review.md    ← existing system review
├── database/
│   └── {timestamp_ms}-{topic}.md           ← database schema design
└── features/
    └── {timestamp_ms}-{topic}.md           ← feature/module design
```

The timestamp prefix (Unix milliseconds) makes files sort chronologically. Each document includes the full design, Design Rationale, Architecture Decision Record (ADR), and Final Documentation — self-contained for future reference.

> **Note:** To exclude AI-generated designs from version control, add `docs/archimind/` to your project's `.gitignore`.

## Viewer

The static site viewer reads `content.md` served by a local Python HTTP server:

- **Sidebar** — Section nav: **Architecture Diagram** | **ERD** | **Revision** (items disabled when section is absent)
- **Architecture Diagram** — Full design content as a single scrollable view with all Mermaid diagrams
- **ERD** — Dedicated view for the entity-relationship diagram
- **Revision** — Before/After tabs for architecture review comparisons
- **↓ PNG** — Every Mermaid diagram has a download button (2× retina quality)
- **Pan/zoom** — Each diagram has −/+/⤢ (reset) buttons; scroll wheel zooms; drag to pan
- **↺ Reload** — Re-fetches `content.md` to reflect updates without restarting the server

## File Structure

```
archimind/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── design-architecture/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── adr-guide.md               ← ADR format and guidance
│   │       ├── architecture-patterns.md   ← canonical pattern library
│   │       ├── database-selection-guide.md
│   │       ├── engineering-principles.md
│   │       ├── mermaid-guidelines.md      ← diagram syntax + C4 context format
│   │       ├── observability-guide.md
│   │       ├── output-template.md
│   │       └── threat-model-guide.md      ← STRIDE methodology
│   ├── design-database/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── data-types-guide.md
│   │       ├── index-guide.md
│   │       ├── normalization-guide.md
│   │       └── security-guide.md
│   ├── design-feature/
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── output-template.md
│   ├── review-architecture/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── anti-patterns.md           ← canonical antipattern names
│   │       ├── output-template.md
│   │       └── review-checklist.md        ← 12-category review checklist
│   └── visualize/
│       └── SKILL.md
├── scripts/
│   ├── find-port.sh       ← finds an unused TCP port in range 3000–3099
│   ├── start-server.sh    ← deploys viewer + starts Python HTTP server
│   ├── stop-server.sh     ← stops server via /tmp/.archimind-$UID.pid
│   ├── open-doc.sh        ← re-visualizes a saved docs/archimind/ document
│   └── site/
│       └── index.html     ← Mermaid JS viewer (HTML + Vanilla JS)
└── README.md
```

## License

MIT

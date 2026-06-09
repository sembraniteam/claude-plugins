# Archimind

AI-powered software architecture and database designer for Claude Code. Designs new architectures, audits existing ones, designs and normalizes databases, and visualizes everything with an interactive Mermaid JS diagram viewer.

## Features

- **Design Architecture** — Present three options (Low / Medium / High risk) with Mermaid diagrams, tech stack recommendations, database suggestions, and risk analysis.
- **Review Architecture** — Audit an existing system, identify antipatterns, and propose three redesign options with migration paths.
- **Design Database** — Design new schemas or normalize existing SQL DDL. Includes ER diagrams, data type recommendations, index strategy, and normalization analysis.
- **Visualize** — Run a local static site viewer with Mermaid JS rendering, left sidebar section nav, and tab navigation between architecture options, ERD, and Before/After revision.

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

Claude will ask clarifying questions, then present three architecture options as a tabbar with diagrams and tech stack recommendations. The design is saved to `docs/archimind/`.

### Review an existing architecture

Say any of:
- "Review my current architecture"
- "Audit my system design — here's the current setup: ..."
- "What's wrong with my architecture?"

Claude analyzes your existing system and proposes three redesign options.

### Design or normalize a database

Say any of:
- "Design a database for a blog platform"
- "Normalize this schema: `CREATE TABLE ...`"
- "What indexes should I add to my users table?"

Paste your SQL DDL directly in the chat for normalization.

### Open the diagram viewer

Say any of:
- "Visualize the architecture"
- "Open the diagram viewer"
- "Start the server"

The viewer opens at `http://localhost:{available-port}`.

### Stop the viewer

Say: "Stop the server" or "Close the viewer"

Or run directly (replace `$CLAUDE_PLUGIN_ROOT` with your plugin installation path):
```bash
bash "$CLAUDE_PLUGIN_ROOT/scripts/stop-server.sh"
```

## Output Files

All design documents are saved to `docs/archimind/` in your project directory after the user selects an option:

```
docs/archimind/
├── architecture/
│   ├── {timestamp_ms}-{topic}.md           ← new architecture design
│   └── {timestamp_ms}-{topic}-review.md    ← existing system review
└── database/
    └── {timestamp_ms}-{topic}.md           ← database schema design
```

The timestamp prefix (Unix milliseconds) makes files sort by creation time.

## Viewer Usage

The static site viewer reads a single `content.md` file served by a local HTTP server:

- **Sidebar section nav** — Three items: **Architecture Diagram** | **ERD** | **Revision** (disabled when section is absent)
- **Architecture Diagram** — Option tabs (Option 1 / Option 2 / Option 3) with full content per option including Mermaid diagrams
- **ERD** — Dedicated view for the entity-relationship diagram
- **Revision** — Before / After tabs for architecture review comparisons
- **Download as PNG** — Every Mermaid diagram has a ↓ PNG download button (2× retina quality)
- **Mermaid rendering** — All `mermaid` code blocks rendered as interactive diagrams via CDN
- **Pan/zoom** — Each diagram has −/+/⤢ (reset) buttons; scroll wheel zooms centered on cursor; drag to pan
- **↺ Reload** — Manual reload button in the sidebar footer re-fetches `content.md` to reflect updates

## File Structure

```
archimind/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   ├── design-architecture/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── architecture-patterns.md
│   │       ├── database-selection-guide.md
│   │       ├── observability-guide.md
│   │       └── output-template.md
│   ├── review-architecture/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── review-checklist.md
│   │       └── anti-patterns.md
│   ├── design-database/
│   │   ├── SKILL.md
│   │   └── references/
│   │       ├── normalization-guide.md
│   │       ├── index-guide.md
│   │       └── data-types-guide.md
│   └── visualize/
│       └── SKILL.md
├── scripts/
│   ├── find-port.sh       ← finds unused TCP port
│   ├── start-server.sh    ← deploys viewer + starts server
│   ├── stop-server.sh     ← stops server via .archimind.pid
│   └── site/
│       └── index.html     ← Mermaid JS viewer (HTML + Vanilla JS)
└── README.md
```

## License

MIT

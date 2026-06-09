---
name: visualize
description: This skill should be used when the user asks to "visualize the architecture", "open the diagram viewer", "show me the diagrams", "open the viewer", "start the viewer", "reopen this document", "re-visualize", "open this design in the viewer", "update the diagram", "revise the diagram", "change the architecture diagram", "edit the Mermaid code", or "regenerate the diagram", or when the user wants to view, update, or regenerate architecture or database diagrams in the browser, including previously saved docs/archimind/ documents.
---

# Visualize Architecture

Open a static website viewer that renders architecture options, ERDs, and Before/After revisions with Mermaid JS. The viewer serves a single `content.md` file from a local HTTP server.

## How It Works

1. Write the design content as markdown to `/tmp/archimind-viewer/content.md`
2. Start the local server (finds a free port, serves `scripts/site/`):

```bash
URL=$(bash "$CLAUDE_PLUGIN_ROOT/scripts/start-server.sh")
open "$URL"
```

3. The browser loads `index.html`, which fetches `content.md` and renders it client-side with Mermaid JS.
4. To stop the server when done:

```bash
bash "$CLAUDE_PLUGIN_ROOT/scripts/stop-server.sh"
```

## When to Open the Viewer

Open the viewer **before asking the user to select** an option:

1. After drafting architecture options (design-architecture skill) — open so the user can compare all three options with rendered Mermaid diagrams
2. After completing a database design (design-database skill) — open so the user can inspect the ERD
3. After drafting architecture review options (review-architecture skill) — open so the user can compare options and the Before/After revision
4. When the user explicitly asks to view or reopen the diagrams

## Re-opening a Saved Document

Previously saved documents in `docs/archimind/` contain only the selected option (single-option view — no option tabs). To re-visualize one:

```bash
bash "$CLAUDE_PLUGIN_ROOT/scripts/open-doc.sh" docs/archimind/architecture/{filename}.md
# or
bash "$CLAUDE_PLUGIN_ROOT/scripts/open-doc.sh" docs/archimind/database/{filename}.md
```

`open-doc.sh` copies the file to `/tmp/archimind-viewer/content.md`, restarts the server, and opens the browser. The viewer renders the saved document with its ERD, Revision (Before/After), and the single selected architecture option.

To list available saved documents:

```bash
find docs/archimind -name "*.md" | sort
```

## Updating a Diagram

When the user asks to update, revise, or edit a Mermaid diagram:

### Step 1: Read the current content

Read `/tmp/archimind-viewer/content.md` and locate the `mermaid` code block to change.

### Step 2: Produce the revised Mermaid code

Based on the user's instruction. Read `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/mermaid-guidelines.md` for diagram type selection, node limits, edge labeling, and subgraph conventions.

### Step 3: Update content.md

Use the **Edit tool** to update the Mermaid block in `/tmp/archimind-viewer/content.md`, then instruct the user to click **↺ Reload** in the viewer sidebar to see the change.

If the server is not running, start it first:

```bash
URL=$(bash "$CLAUDE_PLUGIN_ROOT/scripts/start-server.sh")
open "$URL"
```

## Viewer UI Overview

The viewer provides:

- **Sidebar (left)**: Document title header + **Sections** navigation (Architecture Diagram, ERD, Revision). ERD and Revision nav items are disabled when those sections are absent from the document.
- **Content area**: Option tabs (Option 1 / Option 2 / Option 3) for the Architecture Diagram section, or Before/After tabs for the Revision section.
- **Architecture Diagram view**: Each option tab renders the full option content with Mermaid diagrams. Options are parsed from `### Option N:` subheadings within `## Architecture Diagram`.
- **ERD view**: Renders the `## ERD` section.
- **Revision view**: Before/After tabs parsed from `### Before` and `### After` within `## Revision`.
- **Download button**: Every rendered Mermaid diagram has a **↓ PNG** button (2× retina quality).
- **Pan/zoom controls**: Each diagram has **−** / **+** / **⤢** (reset) buttons in its toolbar. Scroll wheel also zooms centered on the cursor. Drag to pan.
- **↺ Reload button**: In the sidebar footer — manually re-fetches `content.md`. Use after writing changes.

## Document Structure Convention

The viewer parses these heading patterns from `content.md`:

- `## Architecture Diagram` + `### Option N:` subheadings → option tabs
- `## ERD` → ERD nav view
- `## Revision` + `### Before` / `### After` → Before/After tabs

**Critical**: Use `### Option N:` (level-3) within `## Architecture Diagram`, not `## Option N:` (level-2). The viewer splits on level-3 headings to render option tabs.

For database design documents (no option tabs), the Architecture Diagram view renders as a single scrollable view.

For the full document template, see `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/output-template.md`.

## Troubleshooting

**Server not starting**: Python 3 must be installed. All scripts ship with execute permissions — if they are missing, the plugin installation may be corrupted. Reinstall with `cc plugin install archimind` (or re-add via `--plugin-dir` for local installs). (`find-port.sh` is called internally by `start-server.sh`.)

**Browser shows old content**: Click **↺ Reload** in the sidebar. This re-fetches `content.md` without a full page reload.

**Diagrams not rendering**: Requires an internet connection to load Mermaid JS from CDN. Check browser console for Mermaid syntax errors. Verify code blocks use triple backticks with the `mermaid` tag.

**Port already in use**: `start-server.sh` stops any previous archimind server instance before starting. If a port conflict persists, run `bash "$CLAUDE_PLUGIN_ROOT/scripts/stop-server.sh"` then retry.

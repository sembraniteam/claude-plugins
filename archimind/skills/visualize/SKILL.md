---
name: visualize
description: This skill should be used when the user asks to "visualize the architecture", "open the diagram viewer", "show me the diagrams", "show me the architecture", "let me see the options", "open the viewer", "start the viewer", "reopen this document", "re-visualize", "open this design in the viewer", "update the diagram", "edit the Mermaid code", or "regenerate the diagram", or when the user wants to view, update, or regenerate architecture or database diagrams in the browser. Also trigger on "show me the ERD", "display the diagram", and "can I see the design".
---

# Visualize Architecture

Open a static website viewer that renders architecture options, ERDs, and Before/After revisions with Mermaid JS. The viewer serves a single `content.md` file from a local HTTP server.

## How It Works

1. Write the design content as markdown to `/tmp/archimind-viewer/content.md`
2. Start the local server (finds a free port, serves `scripts/site/`) and open the browser — **run as a single command**:

```bash
open "$(bash "$CLAUDE_PLUGIN_ROOT/scripts/start-server.sh")"
```

3. The browser loads `index.html`, which fetches `content.md` and renders it client-side with Mermaid JS via CDN — **an internet connection is required**.

**Cleanup** — stop the server when done:

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
# Run from the project root, or use an absolute path:
bash "$CLAUDE_PLUGIN_ROOT/scripts/open-doc.sh" "$(pwd)/docs/archimind/architecture/{filename}.md"
# or
bash "$CLAUDE_PLUGIN_ROOT/scripts/open-doc.sh" "$(pwd)/docs/archimind/database/{filename}.md"
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

If the server is not running, start it first using the same single command from "How It Works":
`open "$(bash "$CLAUDE_PLUGIN_ROOT/scripts/start-server.sh")"`

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

<!-- Keep in sync with the "Document Structure Convention" section in design-architecture/SKILL.md and review-architecture/SKILL.md -->

The viewer parses these heading patterns from `content.md`:

- `## Architecture Diagram` + `### Option N:` subheadings → option tabs
- `## ERD` → ERD nav view
- `## Revision` + `### Before` / `### After` → Before/After tabs

**Critical**: Use `### Option N:` (level-3) within `## Architecture Diagram`, not `## Option N:` (level-2). The viewer splits on level-3 headings to render option tabs.

For database design documents (no option tabs), the Architecture Diagram view renders as a single scrollable view.

For the full document template, see `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/output-template.md`.

## When content.md Does Not Exist

If the user asks to open the viewer but no design session is active, do not start the server — the viewer will show a blank page. Determine which case applies:

**Case A — No design session started yet**: Inform the user the viewer displays content from an active design session. Suggest:
- `/archimind:design-architecture` — design a new system architecture
- `/archimind:review-architecture` — review and redesign an existing architecture
- `/archimind:design-database` — design a database schema

**Case B — Re-opening a previously saved document**: Use `open-doc.sh` with the saved file path (see "Re-opening a Saved Document" above).

**Case C — content.md exists from a prior session**: Start the server normally; warn the user the content may be from a previous session.

To check whether content.md currently exists:

```bash
ls /tmp/archimind-viewer/content.md 2>/dev/null && echo "exists" || echo "missing"
```

## Comparing Two Saved Documents

To compare two previously saved documents:

1. Open the first document in the viewer (substitute the actual filename — e.g., `1718123456789-payment-platform.md`):

```bash
bash "$CLAUDE_PLUGIN_ROOT/scripts/open-doc.sh" "$(pwd)/docs/archimind/architecture/1718123456789-payment-platform.md"
```

2. To switch the viewer to the second document, copy it to content.md and click **↺ Reload** in the sidebar:

```bash
cp "$(pwd)/docs/archimind/architecture/1718234567890-payment-platform-v2.md" /tmp/archimind-viewer/content.md
```

To list all available saved documents:

```bash
find docs/archimind -name "*.md" | sort
```

For a text-level diff between two saved documents:

```bash
diff docs/archimind/architecture/{file1}.md docs/archimind/architecture/{file2}.md
```

## Troubleshooting

**Server not starting**: Python 3 must be installed. All scripts ship with execute permissions (755) — if missing, the plugin installation may be corrupted. Reinstall with `cc plugin install archimind` (or re-add via `--plugin-dir` for local installs). `find-port.sh` is called internally by `start-server.sh` and does not need to be invoked directly.

**Browser shows old content**: Click **↺ Reload** in the sidebar. This re-fetches `content.md` without a full page reload. Do not hard-refresh the browser page — the viewer state resets.

**Diagrams not rendering (online)**: Verify code blocks use triple backticks with the `mermaid` tag. Open the browser console (F12 → Console) and look for Mermaid `SyntaxError` messages. Correct the diagram code using the Edit tool, then click **↺ Reload**.

**Diagrams not rendering (offline / CDN failure)**: The viewer loads Mermaid JS from `cdn.jsdelivr.net`. If diagrams are blank and the browser console shows `Failed to fetch` for the CDN:
1. Confirm the machine has internet access and can reach `cdn.jsdelivr.net`.
2. In air-gapped environments the viewer cannot render diagrams. As a fallback, output architecture descriptions in structured text within the chat, or paste Mermaid code into an online renderer (mermaid.live) when connectivity is available.

**Port already in use**: `start-server.sh` stops any previous archimind server instance before starting. If a port conflict persists, run `bash "$CLAUDE_PLUGIN_ROOT/scripts/stop-server.sh"` manually, then retry.

**Browser opens before server is ready (connection refused)**: If the browser shows "Connection Refused" or a blank tab immediately after the start command, the Python HTTP server may still be initializing. Click **↺ Reload** in the sidebar after 1–2 seconds. If the problem persists, run `bash "$CLAUDE_PLUGIN_ROOT/scripts/stop-server.sh"` and rerun the start command.

**Option tabs not appearing**: If the viewer renders content as a single scrollable page instead of option tabs (Option 1 / Option 2 / Option 3), the architecture options are using the wrong heading level. The viewer splits on `### Option N:` (level-3) within `## Architecture Diagram` only — `## Option N:` (level-2) is not recognized. Correct the heading levels in `content.md` using the Edit tool, then click **↺ Reload**.

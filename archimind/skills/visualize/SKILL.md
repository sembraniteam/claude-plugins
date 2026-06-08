---
name: visualize
description: This skill should be used when the user asks to "visualize the architecture", "open the diagram viewer", "show me the diagrams", "start the server", "stop the server", "close the viewer", "launch the architecture viewer", "render the Mermaid diagram", "open the static site", "update the diagram", "revise the diagram", "change the architecture diagram", "edit the Mermaid code", "regenerate the diagram", or wants to view, launch, stop, or update architecture and database diagrams.
---

# Visualize Architecture

Manage the Mermaid JS diagram viewer. Three responsibilities:
1. **Start** the local static site server to render architecture/database design documents
2. **Stop** the server when done
3. **Update** Mermaid diagrams inline within saved design documents

## Scripts

All scripts are at `$CLAUDE_PLUGIN_ROOT/scripts/`:

| Script            | Purpose                                                                                            |
|-------------------|----------------------------------------------------------------------------------------------------|
| `find-port.sh`    | Returns the first available TCP port ≥ 3000 (called internally by `start-server.sh`, not directly) |
| `start-server.sh` | Deploys viewer, generates manifest, starts server                                                  |
| `stop-server.sh`  | Stops the running server via saved PID                                                             |

## Starting the Viewer

When the user asks to open, launch, or start the viewer:

### Step 1: Verify docs exist

Check that `docs/archimind/` or its subdirectories contain at least one `.md` file:

```bash
find docs/archimind -name "*.md" 2>/dev/null | head -5
```

If no docs found, report: "No architecture or database designs found. Generate a design first using `/archimind:design-architecture` or `/archimind:design-database`."

### Step 2: Start the server

```bash
bash "$CLAUDE_PLUGIN_ROOT/scripts/start-server.sh"
```

The script will:
1. Find a free port using `find-port.sh`
2. Copy `index.html` to `docs/archimind/`
3. Generate `docs/archimind/manifest.json` scanning both `architecture/` and `database/` subdirectories and flat files
4. Start `python3 -m http.server` from `docs/archimind/`
5. Print the URL and save the PID

### Step 3: Report to user

After the server starts, report:
- The URL (e.g., `http://localhost:3421`)
- What the viewer shows: sidebar with document list, 3-item section navigation
- How to stop it: "Say 'stop the server' or 'close the viewer' to shut it down"

## Stopping the Viewer

When the user says "stop the server", "close the viewer", "stop archimind server" — or when an architecture decision has been finalized — run:

```bash
bash "$CLAUDE_PLUGIN_ROOT/scripts/stop-server.sh"
```

Report: "Server stopped." If the PID file doesn't exist, report: "No running server found."

**Auto-stop trigger**: After the user selects one architecture option (and the document is updated with `✅ SELECTED`), proactively offer to stop the viewer.

## Updating a Diagram

When the user asks to update, revise, or regenerate a Mermaid diagram in an existing design document:

### Step 1: Identify the document

List available documents:
```bash
find docs/archimind -name "*.md" | sort
```

### Step 2: Read the document

Read the target file and locate the Mermaid code block(s).

### Step 3: Generate the revised diagram

Based on the user's instruction, produce the updated Mermaid code:

- `flowchart TD` for service topology
- `erDiagram` for database diagrams
- `sequenceDiagram` for flows
- Keep diagrams focused: 8–15 nodes
- Label all edges with action verbs
- Use subgraphs to group related nodes

### Step 4: Apply the update

Replace the old Mermaid block in the file with the new one. Preserve all surrounding Markdown content.

### Step 5: Confirm

Inform the user: "Diagram updated in `{filepath}`. Refresh the browser to see the changes (auto-refresh every 10 seconds)."

## Viewer UI Overview

The viewer provides:

- **Sidebar (left)**: Two sections — a file list (all `.md` files in `docs/archimind/`, with category badges and timestamps) and a **Sections** navigation panel that appears when a document is loaded.
- **Sections nav (sidebar bottom)**: 3 items — **Architecture Diagram** | **ERD** | **Revision**. ERD and Revision items are disabled (grayed out) when those sections don't exist in the document.
- **Sub-tab bar (top of content area)**: Option tabs (Option 1 / Option 2 / Option 3 / Recommendation) for the Architecture Diagram view, or Before/After tabs for the Revision view.
- **Architecture Diagram view**: Each option tab renders the full option content including Mermaid diagrams. Tabs are parsed from `### Option N:` subheadings within `## Architecture Diagram`.
- **ERD view**: Renders the `## ERD` section with Mermaid `erDiagram`.
- **Revision view**: Shows **Before** / **After** tabs parsed from `### Before` and `### After` within `## Revision`.
- **Download as Image**: Every rendered Mermaid diagram has "↓ SVG" and "↓ PNG" download buttons.
- **Auto-refresh**: Page polls for changes every 10 seconds. The currently viewed tab and section are preserved across refreshes.

For database design documents (no Architecture Diagram options), the Architecture Diagram nav shows the content as a single view without option tabs.

## Manifest Format

`docs/archimind/manifest.json` is auto-generated by `start-server.sh`. Format:

```json
{
  "files": [
    {
      "path": "architecture/1735689600000-payment-platform-design.md",
      "name": "1735689600000-payment-platform-design.md",
      "title": "payment platform design",
      "category": "architecture"
    },
    {
      "path": "database/1735689600000-order-management-design.md",
      "name": "1735689600000-order-management-design.md",
      "title": "order management design",
      "category": "database"
    }
  ],
  "generated": "2025-06-08T10:00:00Z"
}
```

## Troubleshooting

**"Address already in use"**: Run stop-server.sh first, then start again.

**"python3 not found"**: Inform user: "Python 3 is required to run the viewer. Install it or use your system package manager."

**Diagrams not rendering**: Verify the Mermaid code block uses triple backticks with `mermaid` tag. Check browser console for Mermaid syntax errors.

**Browser doesn't open automatically**: Provide the URL manually: "Open `http://localhost:{port}` in your browser."

**Sidebar shows no files**: The `manifest.json` may be stale. Stop the server and restart — `start-server.sh` regenerates `manifest.json` on each start.

**ERD or Revision nav is disabled**: The loaded document doesn't contain a `## ERD` or `## Revision` section. Add one using the appropriate skill or manually.

---
name: architecture-designer:review
description: Use this skill when the user wants to review or revise an existing architecture, says "review my architecture", "audit my architecture", "check my architecture", "my architecture needs review", "update my architecture document", "revise the architecture", "architecture drift", "compare design vs implementation", "architecture is outdated", "architecture inconsistency", "check if my code matches my design", or wants to compare their architecture document against their current codebase. Also trigger when the user mentions their architecture document needs updating after new features were added or requirements changed.
---

# Architecture Designer — Review and Revision Workflow

This skill reviews an existing architecture (from a document, the codebase, or both), presents findings, and guides the user through a structured revision process that creates a new versioned document.

**Scripts directory:** `../../scripts/` relative to this SKILL.md.

---

## Step 1 — Determine review source

Ask the user:

> "What would you like me to review? I can:
> **(a)** Review your existing architecture document in `docs/architecture-designer/architecture/`
> **(b)** Scan your current codebase and reconstruct the actual architecture
> **(c)** Do both — compare the document against the codebase to find drift
>
> Which would you prefer?"

---

## Step 2a — Document-based review

If the user chose (a) or (c):

1. List all files in `docs/architecture-designer/architecture/` sorted by filename (newest date first). Present the list to the user and ask which document to review, or confirm using the latest.
2. Read the selected document.
3. Ask: **"What is your current goal for this review? Has anything changed since this document was written? (New requirements, new constraints, team changes, performance issues, etc.)"**
4. Spawn the `architecture-designer:architecture-reviewer` agent. Pass it:
   - The full contents of the architecture document
   - The user's current context/goals
   - Any new requirements or constraints the user described
   Let the agent assess: quality, consistency, completeness, and fit with current needs.
5. Present the reviewer's findings to the user.

---

## Step 2b — Codebase-based review

If the user chose (b) or (c):

Scan the codebase to reconstruct the actual architecture:

1. **Project structure**: list top-level directories and key files (`package.json`, `go.mod`, `pom.xml`, `requirements.txt`, `Cargo.toml`, `docker-compose.yml`, `Dockerfile`, etc.)
2. **Services / modules**: identify separate services, modules, or components (in a monorepo, list packages; for a monolith, identify major layers or domains)
3. **Dependencies**: read dependency manifests to identify frameworks, databases, message queues, HTTP clients, and key libraries
4. **Entry points**: find route/controller files, worker entry points, or serverless function definitions
5. **Database connections**: find ORM configurations, migration files, or schema definitions to identify the actual database technology and schema
6. **Infrastructure**: check for `Dockerfile`, `docker-compose.yml`, Kubernetes manifests, Terraform files, CI/CD pipelines

Compose a **Reconstructed Architecture Summary**:
- Architecture pattern (detected from structure)
- Technology stack (frameworks, databases, caches, queues)
- Key components and their relationships
- Deployment configuration

If the user also has a document (option c): compare the reconstructed architecture against the document and produce a **Drift Report**:
- Components in the document but absent from the code
- Components in the code but absent from the document
- Naming inconsistencies
- Technology substitutions (e.g., document says Redis, code uses Memcached)
- Structural differences (e.g., document shows microservices, code is a monolith)

---

## Step 3 — Present findings and ask for revision

Present the review findings (architecture review report, drift report, or both) to the user. Then ask:

> **"Based on these findings, would you like to revise the architecture? I can update the affected diagrams, create a new versioned document, and optionally regenerate the implementation skeleton."**

If the user does not want to revise: acknowledge the review is complete. They can run this skill again at any time.

---

## Step 4 — Revision process

If the user agrees to revise:

### 4a. Gather revision scope

Ask:
- Which findings should be addressed in this revision?
- Are there new requirements that should be incorporated?
- Is this a minor revision (1.1) or a major redesign (2.0)?

### 4b. Update diagrams

Based on the revision scope:
- For architecture changes: update the affected Mermaid diagrams (C4, sequence, deployment)
- For database changes: re-spawn the `architecture-designer:database-designer` agent with the updated requirements
- For new features: add new diagram elements as needed
- For removed components: remove or strike-through the relevant elements

### 4c. Architecture re-review

Spawn the `architecture-designer:architecture-reviewer` agent with:
- The updated requirements (original + changes)
- All updated diagrams

Fix any critical findings before proceeding.

### 4d. Browser preview

1. Update `docs/architecture-designer/diagrams.json` with the revised diagrams (same JSON format as the design workflow, including `details`, `rationale`, and — for ERD diagrams — `companionTable` rows; update all three to reflect what changed in the revision).
2. If a preview server from a previous run is already running (the user will know the URL): tell them to refresh their browser.
3. If no server is running: run `node <scripts_dir>/find-port.mjs`, then `node <scripts_dir>/preview-server.mjs <port>` in the background.
4. Ask: **"Does this revised architecture look correct to you?"**

If further revisions are needed, repeat from step 4b.

### 4e. Save the revised document

Once the user confirms the revision, save to:
```
docs/architecture-designer/architecture/{yyyymmdd}-{topic}.md
```

**Important**: never overwrite the previous document. Always create a new file. The history must remain intact.

The metadata table:
```markdown
| Date       | Version   | Status | Reason            | Previous Document   |
|------------|-----------|--------|-------------------|---------------------|
| {dd-mmm-y} | {version} | Draft  | {revision reason} | {previous filename} |
```

- `Version`: increment from the previous document. Use `1.1`, `1.2`, ... for minor changes; `2.0` for major redesigns. Ask the user if unsure.
- `Reason`: fill with the reason for this revision (e.g., "Added real-time notifications feature", "Migrated from monolith to microservices", "Performance improvements for 10× user growth")
- `Previous Document`: the filename of the document being revised (e.g., `20260705-inventory-app.md`)
- `Status`: always starts as `Draft`

Generate timestamps using JavaScript `Date`, not shell commands.

The document body follows the same structure as the design workflow (all sections, all diagrams). This is a standalone document, not a diff — someone reading it without the previous version should have complete context.

### 4f. Document review

Spawn the `architecture-designer:document-reviewer` agent. Pass it:
- Path to the new document
- Requirements summary
- Expected filename

Fix any failures, re-review until it passes. Then update `Status` to `Approved`.

### 4g. Implementation offer

After approval:

> **"The revised architecture document is approved. Would you like me to regenerate the project skeleton based on the updated architecture?"**

If yes: spawn `architecture-designer:architecture-implementer` with the new document path.

---

## Path resolution

`<scripts_dir>` = the `scripts/` directory of the architecture-designer plugin, two levels above this file (`../../scripts/`). Resolve it from the absolute path of this SKILL.md at runtime.

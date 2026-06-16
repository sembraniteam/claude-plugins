---
name: design-feature
description: This skill should be used when the user asks to "design a feature", "design a module", "plan a new feature", "how should I implement this feature", "design the implementation for", "architect a new module", "help me design a feature", "plan the implementation of", "what's the best way to implement this feature", "design a plugin", "design a new component for my app", or describes a specific feature or module they want to add to an existing application.
---

# Design Feature

Act as a **Senior Software Engineer** with 5+ years of production experience. Read and apply `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/engineering-principles.md` throughout this workflow.

Core behaviors:
- Understand the existing application context before proposing anything — a feature's design is constrained by what's already there
- Recommend the simplest implementation that satisfies all requirements; introduce abstractions only when a specific requirement demands it
- Identify coupling risks, testability concerns, and extension points in every option
- Explain the technical rationale and trade-offs behind every design decision

Follow the **Spec → Plan → Review → Ship** workflow strictly — gather requirements and application context first, generate all three options and write them to content.md, present a compact summary for user confirmation, then open the visual viewer for final selection. **Never output the full design options in the chat response** — the viewer is the display surface. Keep chat responses brief status updates.

## Workflow

At the very start, call **TaskCreate** to create one task per step:
1. Spec — Identify and gather missing requirements
2. Spec — Confirm requirements summary
3. Plan — Generate 3 feature design options → write content.md
4. Review — Present plan summary, confirm or iterate
5. Ship — Open viewer and await option selection
6. Ship — Write final documentation
7. Ship — Save permanent docs and stop server

Mark each task `in_progress` when starting it and `completed` when done.

---

### Stage 1: Spec — Gather Requirements

Analyze the user's initial message and any provided context (code snippets, files, prior conversation) to extract known information. Map what is found to the **8 required data points** in the catalog below — classify each as:
- **Known** — explicitly stated (e.g., "I'm adding this to my NestJS monorepo")
- **Inferable** — derivable with high confidence (e.g., "NestJS" → Node.js / TypeScript; "adding a checkout step" → new API endpoints + schema changes likely; "2-person startup" → small team + speed priority)
- **Unknown** — cannot be determined without asking

Ask only about **Unknown** data points using **AskUserQuestion** — map A/B/C/D options from the catalog to the tool's `options` array (up to 4 per question). Group up to 4 unknown data points per call. If all points are Known or Inferable, skip to **Confirm Requirements Summary** immediately. Never ask about information already provided.

**Required Data Points**

Use the corresponding options when a data point is Unknown:

**1. Application type**
- A) Web application (frontend + backend API)
- B) Backend service / API only
- C) Mobile application (iOS / Android / cross-platform)
- D) CLI tool or desktop application
- Other: Describe briefly

**2. Existing architecture style**
- A) Monolith (single deployable, shared codebase)
- B) Modular monolith (clear domain boundaries, single deploy)
- C) Microservices (independent services, separate deploys)
- D) Not sure / greenfield module within a larger system
- Other: Describe briefly

**3. Feature description** — what problem it solves and who uses it
*(If not stated in the initial message, ask as a free-text question using the "Other" option or a brief prompt. This is the most critical data point — never skip it.)*

**4. Schema changes required**
- A) Yes — needs new tables or significant schema additions
- B) Possibly — may need minor schema changes (new columns, indexes)
- C) No — reads from or writes to existing tables only
- D) Not sure yet

**5. Programming language / framework**
- A) Java / Kotlin (Spring Boot, Quarkus, Micronaut)
- B) Go (Gin, Echo, Fiber, standard library)
- C) Node.js / TypeScript (NestJS, Express, Fastify)
- D) Python (FastAPI, Django, Flask) or C# (.NET)
- Other: Specify

**6. Integration points with existing code**
- A) Calls into existing services / use-cases only (no new API endpoints)
- B) Adds new API endpoints and integrates with existing domain services
- C) Integrates across multiple existing modules or services
- D) Mostly standalone — minimal coupling to existing code

**7. Team size and context**
- A) Solo / tiny team (1–3), needs to ship fast
- B) Small team (4–10), balanced quality and speed
- C) Medium team (10–30), can afford proper abstractions
- D) Large team — multiple people working on different parts of this feature simultaneously

**8. Primary quality concern**
- A) Speed to ship — keep it simple, iterate later
- B) Testability — must be fully unit/integration testable
- C) Extensibility — other teams will build on top of this
- D) Performance — this feature is on a hot path

**Confirm Requirements Summary**

After collecting all answers, display a structured summary **before** generating any options. Present in this exact format, then wait for confirmation:

---

**Requirements Summary**

| Category              | Your Answer                            | Inferred from      |
|-----------------------|----------------------------------------|--------------------|
| Application type      | {value from Q1}                        | —                  |
| Architecture style    | {value from Q2}                        | —                  |
| Feature description   | {summary from Q3}                      | —                  |
| Schema changes        | {value from Q4}                        | —                  |
| Language / framework  | {value from Q5}                        | —                  |
| Integration points    | {value from Q6}                        | —                  |
| Team context          | {value from Q7}                        | —                  |
| Quality priority      | {value from Q8}                        | —                  |
| ERD needed            | {Yes / No / Optional}                  | Q4 (inferred)      |
| Coupling risk         | {Low / Medium / High}                  | Q6 + Q2 (inferred) |
| Abstraction level     | {Minimal / Moderate / High}            | Q7 + Q8 (inferred) |

**Key inferences:**
- {1–3 bullets summarizing constraints inferred from the combination of answers — e.g., "Solo team + speed priority → Option 1 (Inline) is the safest default"}

> Does this accurately capture your requirements? Reply with any corrections, or say **"Yes, proceed"** to generate the feature design options.

---

Wait for the user to confirm or correct. Only proceed to Stage 2 when the user explicitly approves.

---

### Stage 2: Plan — Generate Feature Design Options

After confirmation, compose the full design document — all 3 options, optional ERD, and Recommendation — **directly into `/tmp/archimind-viewer/content.md`** using the Write tool. Print a short status line like "Planning 3 options…" while writing. **Do not open the viewer yet — that happens in Stage 4: Ship.**

Design **exactly 3 options**: Inline, Modular, and Decoupled.

**Anti-over-engineering check before generating options**: Map each stated requirement to the simplest option that satisfies it. If Inline satisfies all requirements, say so explicitly in the Recommendation. Complexity must be justified by a specific, named requirement — not by preference for clean patterns.

#### Option 1: Inline
- Add the feature directly within the existing code structure with minimal new abstractions.
- Typical approach: New functions/methods within existing files or a single new file, no new layers, direct calls.
- Best for: Solo/small teams, tight deadlines, low integration complexity, features unlikely to change significantly.

#### Option 2: Modular
- Encapsulate the feature as a distinct module with clear public boundaries (interface/contract) and proper internal layering.
- Typical approach: Dedicated feature module/package with controller → service → repository layers, clean integration contracts.
- Best for: Teams that need testability and maintainability, features that other parts of the codebase will depend on.

#### Option 3: Decoupled
- Design the feature for maximum decoupling and extensibility — event-driven integration, plugin pattern, or abstraction interfaces.
- Typical approach: Domain events, abstract interfaces, dependency inversion, optional background processing.
- Best for: Features that will be extended by multiple teams, features on critical paths needing independent testing, or features that may need to be extracted into a separate service later.

#### Required Sections Per Option

Structure each option under `## Architecture Diagram` using `### Option N:` subheadings. Use `####` for subsections. The full scaffold is in `$CLAUDE_PLUGIN_ROOT/skills/design-feature/references/output-template.md` — **read it for structure only; never write to it**.

Required `####` subsections for each option — **every option must include two Mermaid diagrams** (no `architecture-beta`). Read `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/mermaid-guidelines.md` for diagram syntax:

- **Feature Integration** (`flowchart TD`) — how the new feature/module connects to existing components in the application. Show existing components as-is; mark the new feature's components with `[NEW]`. Follow with a 1–2 sentence description.
- **Feature Flow** (`sequenceDiagram`) — the primary end-to-end workflow of the feature (main user action through all layers to persistence). Label each arrow with the method name or event name. Follow with a 1–2 sentence description.
- **Module Structure** (`flowchart TD`) — *Optional, include only if the option introduces internal layering complex enough to warrant it.* Internal breakdown of the feature module: layers, sub-components, and their relationships. Follow with a 1–2 sentence description.
- **Key Components** — bulleted list of new files/classes/modules introduced, with one-line descriptions
- **Technology Stack** — table: Layer / Approach / Reason (only new choices; existing stack is assumed)
- **Data Layer Design** — which existing tables/entities are read from or written to; what schema changes (if any) are required
- **Testing Strategy** — unit test surface, integration test boundaries, mocking strategy for the new feature
- **Extension Points** — how other modules can hook into or extend this feature (empty for Option 1, more detailed in Options 2 and 3)
- **Risks & Mitigations** — table: Risk / Likelihood / Impact / Mitigation
- **When to Choose This Option** — 2–3 bullets

#### ERD Section (Conditional)

Include `## ERD` **only if** the requirements summary indicates schema changes are needed (Q4 answered A or B). Add a Mermaid `erDiagram` covering the new tables and relationships with existing entities. Include column specifications for new tables (PK, columns, types, key indexes). If no schema changes are needed, omit the `## ERD` section entirely.

#### Recommendation Section

Add `## Recommendation` with a **Narrative** — 4–6 sentences stating which option is recommended and why, referencing actual requirements (team size, quality priority, integration complexity, timeline). Acknowledge the main trade-off between the options.

Save the complete document with the Write tool. **Do not call start-server.sh at this stage.**

---

### Stage 3: Review — Confirm Before Shipping

After writing content.md, present a compact **Plan Summary** in chat:

---

**Plan Summary**

| Option | Tier      | Approach Name | Key Pattern                                   |
|--------|-----------|---------------|-----------------------------------------------|
| 1      | Inline    | {Name}        | {e.g., Direct functions in existing service}  |
| 2      | Modular   | {Name}        | {e.g., Feature module with service layer}     |
| 3      | Decoupled | {Name}        | {e.g., Domain events + abstract interfaces}   |

**Recommended:** Option N — {1–2 sentence rationale citing the key requirements that drove this recommendation.}

---

Use **AskUserQuestion** to ask the user what to do next:

```
question: "Three feature design options are ready. What would you like to do?"
header: "Next Step"
options:
  - label: "Ship — open the visual viewer"
    description: "Open the interactive viewer to compare all three options side by side and make your final choice"
  - label: "Iterate — adjust before viewing"
    description: "Request changes to the options, tech approach, or recommendation before opening the viewer"
```

If the user chooses **Iterate**: apply the requested changes to `/tmp/archimind-viewer/content.md`, update the Plan Summary table, and re-present Stage 3. Repeat until the user chooses **Ship**.

---

### Stage 4: Ship — Visual Selection and Final Documentation

Open the viewer:

```bash
open "$(bash "$CLAUDE_PLUGIN_ROOT/scripts/start-server.sh")"
```

Post a brief chat message: "Viewer is open at http://localhost:PORT — use **Architecture Diagram** to compare options side by side. Select an option when ready."

**Option Selection**

Use **AskUserQuestion** to ask the user to choose:

```
question: "Which feature design would you like to proceed with?"
header: "Select Option"
options:
  - label: "Option 1 — Inline"
    description: <one-line summary of Option 1 approach>
  - label: "Option 2 — Modular"
    description: <one-line summary of Option 2 approach>
  - label: "Option 3 — Decoupled"
    description: <one-line summary of Option 3 approach>
```

Allow iterations if the user wants adjustments. Re-present AskUserQuestion after each change. Do not proceed until the user makes an explicit choice.

**Mark Selected Option and Write Final Documentation**

Once the user has chosen, complete all the following in sequence:

1. Read the saved document
2. Insert decision header after the document title:
   ```markdown
   **Selected:** Option N — {Tier}: {Approach Name}
   **Decision date:** {ISO date}
   ```
3. Append a `## Decision Notes` section capturing user-requested adjustments and next steps

**Append Final Documentation** — each section must be substantive, no placeholders:

```markdown
## Final Documentation

### Overview
### Feature Design Decision
### Implementation Guide
### Data Design
### Testing Plan
### Integration Notes
### Trade-offs & Next Steps
```

For field-level guidance on each section, read `$CLAUDE_PLUGIN_ROOT/skills/design-feature/references/output-template.md`.

**Save Permanent Documentation and Stop Server**

1. Update `/tmp/archimind-viewer/content.md` with the Write tool. Inform the user: "The viewer is updated — click **↺ Reload** in the sidebar to see the final state."
2. Compute timestamp: `node -e 'process.stdout.write(String(Date.now()))'` (macOS) or `date +%s%3N` (Linux). Derive topic slug from the feature name (e.g., `user-notifications`, `payment-retry`).
3. Save permanent documentation:

```bash
mkdir -p docs/archimind/features
```

Write `docs/archimind/features/{timestamp_ms}-{topic}.md` using the **Write tool**. **This file must contain only the selected option** — not all three. Include: selected `### Option N:` section, ERD (if applicable), Recommendation, Decision Notes, and Final Documentation. Omit the other two options entirely. To re-visualize later: `bash "$CLAUDE_PLUGIN_ROOT/scripts/open-doc.sh" docs/archimind/features/{timestamp_ms}-{topic}.md`.

4. Stop the viewer server:

```bash
bash "$CLAUDE_PLUGIN_ROOT/scripts/stop-server.sh"
```

---

## Document Structure Convention

The viewer parses these heading patterns from `content.md`:

- `## Architecture Diagram` + `### Option N:` subheadings → option tabs
- `## ERD` → ERD nav view (omit entirely if no schema changes)

**Critical**: Use `### Option N:` (level-3) within `## Architecture Diagram`, not `## Option N:` (level-2). The viewer splits on level-3 headings to create option tabs.

## Mermaid Diagram Guidelines

Feature design uses **only two diagram types** — no `architecture-beta`:

- `flowchart TD` — Feature Integration and Module Structure diagrams
- `sequenceDiagram` — Feature Flow diagram

Read `$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/mermaid-guidelines.md` for full syntax reference. Mark new components in `flowchart TD` with `[NEW]` in the node label.

## Token Optimization

- Respond concisely; avoid repeating information already established
- If context becomes large, provide a brief summary before continuing
- Do not generate final documentation until the user has explicitly selected a design option

## Additional Resources

- **`$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/engineering-principles.md`** — 10 guiding principles. Read at the start of every session.
- **`$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/mermaid-guidelines.md`** — Diagram syntax, node limits, edge labeling conventions.
- **`$CLAUDE_PLUGIN_ROOT/skills/design-architecture/references/database-selection-guide.md`** — Read when the feature requires a new database or data store.
- **`$CLAUDE_PLUGIN_ROOT/skills/design-feature/references/output-template.md`** — Full document scaffold. **Read-only — never write to it.** Read during Stage 2 and Stage 4.

# Architecture Decision Record (ADR) Guide

Use this guide at Step 11 (`design/SKILL.md`) immediately after the architecture document is saved, and again at step 4f
(`review/SKILL.md`) when a revision changes a decision. It produces one small, standalone file per significant
decision — separate from the main document — so a later "why did we choose this, and when did that change?" question has
a direct file to open instead of diffing full document versions against each other.

## Why a separate file per decision

The main document (`references/document-template.md` section 6) already states each Stage 5 decision with its
justification — but that section is overwritten wholesale on every revision (a new document version, per
`design/SKILL.md` Step 11 and `review/SKILL.md` step 4f). There is no way to answer "what did we decide about the
database engine in March, and why did we change it in June?" from the document history alone without opening every
version. An ADR file is never edited or overwritten in place — like architecture documents and remediation plans, a
changed decision produces a *new* ADR that supersedes the old one, so the sequence of files itself is the decision
history.

## Which decisions get an ADR

Not every Stage 5 field needs one — a criterion for restraint, mirroring the rest of this plugin's "don't pad"
discipline for `riskRegister`/`tradeoffAnalysis`:

1. **Always**, regardless of driver citation — these are structural and expensive to reverse once implementation starts:
   architecture pattern, backend language/framework, frontend framework (if applicable), database engine (s),
   infrastructure provider, authentication approach.
2. **Any other Stage 5 item that cites an `architecturalDrivers` ID** in its justification (per
   `references/quality-driven-design-guide.md`'s Stage 5 citation rule) — a driver-cited decision is, by definition, one
   the architect considered significant enough to trace back to a requirement.
3. **Every `stage5.tradeoffAnalysis` entry** (`TO-n`) — a recorded trade-off is, by construction, a decision with real
   tension behind it, so it already has everything an ADR needs (drivers in tension, decision, rationale).

A Stage 5 item with no driver citation and not in category 1 ("no specific driver; standard choice for this scale," per
`quality-driven-design-guide.md`) does not get its own ADR — an undriven best-practice pick has no real decision history
worth recording standalone. This keeps the ADR set proportional to how many decisions actually mattered, the same way a
simple system's `riskRegister` legitimately has only two or three entries.

## Numbering and file naming

ADRs number sequentially for the life of the project, tracked by `session.json`'s top-level `adrs` array (see
`references/session-schema.md`) — never restart numbering per document revision. Save each to:

```
docs/architecture-designer/adr/{NNNN}-{slug}.md
```

- `{NNNN}`: 4-digit zero-padded sequence number (`0001`, `0002`, ...) — the next unused number after the highest
  `id` already in `session.json`'s `adrs` array (`ADR-0001` → sequence `1`), or `0001` if the array is absent/empty.
- `{slug}`: kebab-case short title of the decision (e.g. `database-engine-selection`,
  `event-driven-architecture-pattern`).

Create the `docs/architecture-designer/adr/` directory if it doesn't exist.

## Template

```markdown
# ADR-{NNNN}: {Decision Title}

| Field | Value |
|-------|-------|
| Status | Accepted |
| Date | {dd-mmm-yyyy} |
| Driver(s) | {AD-n, AD-m — or "no specific driver; standard choice for this scale"} |
| Related Trade-off | {TO-n — omit this row entirely if not sourced from `tradeoffAnalysis`} |
| Supersedes | {ADR-000X — omit this row entirely for a first-time decision} |
| Architecture Document | {path to the document version this decision belongs to} |

## Context

What situation/requirement made this decision necessary — cite the specific stages/requirements it responds to (Stage
1–4 facts, or the driver(s) named above), the same "cite a specific reason" discipline `design/SKILL.md` Stage 5 already
requires for the decision itself.

## Decision

The decision actually made, stated as one clear sentence, plus enough specificity to be unambiguous (a named product and
version, not a category — same "Fastify 5, not Node.js" specificity Stage 5 requires).

## Consequences

What becomes easier and what becomes harder as a result — both directions, not just the upside. For a decision sourced
from `stage5.tradeoffAnalysis`, this is that entry's trade-off point and sensitivity point restated in ADR form.

## Alternatives Considered

The other option(s) discussed and why they were not chosen. Never invent an alternative that was not actually discussed
during Stage 5 — omit this section (state "not discussed as alternatives were not raised") rather than fabricate a
plausible-sounding rejected option.
```

**Status values**: `Accepted` — write every ADR directly as `Accepted`, never `Proposed`, since by the time Step 11 runs
the decision has already been through Stage 5's confirmation round-trip with the user; there is no separate proposal
phase in this workflow the way a multi-stakeholder team ADR process might have one. The only other value is
`Superseded by ADR-{NNNN}`, applied to an *old* ADR file the moment a new one replaces its decision (see below) — never
edit an ADR's Context/Decision/Consequences after it is written; a changed decision always produces a new file.

## Generating ADRs (Step 11, first time)

For each decision selected per "Which decisions get an ADR" above: fill the template, save the file, then append
`{ "id": "ADR-{NNNN}", "path": "<absolute path>", "title": "<decision title>", "status": "Accepted", "relatedDecision": "<stage5 field name, e.g. \"database\", or a TO-n id>", "supersedes": null, "createdAt": "<current ISO timestamp>" }`
to `session.json`'s top-level `adrs` array (create it if absent). Do this for every selected decision before moving on —
same "read-fresh-modify-append-write-whole" discipline as `diagrams.json`.

## Revising ADRs (`review/SKILL.md` step 4f)

When a revision changes a decision that already has an ADR (a Stage 5 field changes, or an existing `tradeoffAnalysis`
entry is superseded by a new one): write a **new** ADR file with the next sequence number, its `Supersedes` row pointing
at the old ADR's ID, and its own fresh Context/Decision/Consequences reflecting the revised choice. Then make one
terminal write to the *old* ADR file — change its Status row to `Superseded by ADR-{new NNNN}` — mirroring exactly how
`references/session-schema.md` section "Superseding a remediation plan" handles a superseded remediation plan. Append
the new entry to `session.json`'s `adrs` array with its own `supersedes` field set to the old ADR's `id`; never edit the
old array entry.

A revision that changes a decision with **no** prior ADR (an undriven, standard-choice item from Stage 5 that never
qualified per "Which decisions get an ADR") only gets a new ADR if the revised decision now qualifies under that same
criteria (e.g. it now cites a driver, or a new trade-off was recorded for it) — evaluate it fresh against the criteria
each time, do not retroactively create one for a decision that still doesn't qualify.

A revision that leaves a decision unchanged never touches that decision's existing ADR.

## Cross-linking with the main document

The architecture document's **Architecture Decision Records** section (`references/document-template.md`) lists a
pointer table only — ID, title, status, and a reference to the file path — never a duplicate of the ADR's own
Context/Decision/Consequences prose. This keeps the main document scannable while the full rationale and alternatives
live in the one place a reader who wants that depth would look.

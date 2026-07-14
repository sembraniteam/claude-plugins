# session.json Schema Reference

The full contract for `docs/architecture-designer/session.json` — the canonical schema, the array-of-objects shape used by `documents`, `remediationPlans`, and `implementationPlans`, and the rules every reader and writer across the plugin must follow. `design/SKILL.md` owns this file's top-level structure; `review/SKILL.md`, `implement/SKILL.md`, and `implementation-planner.md` read and append to it per the single-writer-per-key rule below.

## Canonical schema

The top-level keys are fixed; the field names inside each stage object are the user's confirmed answers and may vary:

```json
{
  "schemaVersion": 2,
  "project": "inventory-app",
  "updatedAt": "2026-07-13T10:42:00Z",
  "stage1": { "applicationGoal": "...", "stakeholders": "...", "businessProcesses": "...", "painPoints": "...", "successCriteria": "..." },
  "stage2": { "functionalRequirements": ["..."], "nonFunctionalRequirements": { "performance": "...", "security": "...", "compliance": "...", "scalability": "...", "availability": "..." } },
  "stage3": { "budget": "...", "timeline": "...", "regulations": "...", "teamCompetencies": "...", "legacySystems": "...", "cloudPreference": "..." },
  "stage4": { "registeredUsers": "...", "concurrentUsers": "...", "tps": "...", "dataVolume": "...", "readWriteRatio": "...", "peakPatterns": "...", "geography": "..." },
  "stage5": { "architecturePattern": "...", "backend": "...", "frontend": "...", "database": "...", "infrastructure": "...", "supportingServices": "...", "authentication": "...", "observability": "...", "disasterRecovery": "..." },
  "stage6b": { "tool": "...", "stateBackend": "...", "modules": "...", "envStrategy": "...", "driftDetection": "..." },
  "stage6c": { "platform": "...", "stages": "...", "branchingStrategy": "...", "envPromotion": "...", "secretInjection": "...", "artifactManagement": "..." },
  "documents": [
    { "path": "/absolute/path/to/docs/architecture-designer/architecture/YYYYMMDD-topic.md", "createdAt": "2026-07-13T09:10:00Z" }
  ],
  "remediationPlans": [
    { "path": "/absolute/path/to/docs/architecture-designer/plan/YYYYMMDD-topic-remediation.md", "document": "/absolute/path/to/docs/architecture-designer/architecture/YYYYMMDD-topic.md", "createdAt": "2026-07-13T10:05:00Z" }
  ],
  "implementationPlans": [
    { "path": "/absolute/path/to/docs/architecture-designer/plan/YYYYMMDD-topic.md", "document": "/absolute/path/to/docs/architecture-designer/architecture/YYYYMMDD-topic.md", "remediationPlan": null, "supersedes": null, "createdAt": "2026-07-13T10:40:00Z" }
  ]
}
```

Sub-agents receive the full contents of this file as input and must read it tolerantly — inner field names are illustrative, not contractual. The only guaranteed top-level keys are `stage1`–`stage5` and (after Step 11) `documents`. `stage6b` and `stage6c` are written after Stage 6b/6c confirmation and must be included when passing session context to sub-agents. `remediationPlans` may also appear after `/architecture-designer:review` has run — written by that skill, and must be passed to implementation-planner when present. `implementationPlans` may also appear after `architecture-designer:implementation-planner` has run — written by that agent itself after saving its plan file, not by the `design` skill. `architecture-implementer` never writes to `session.json`; it only reads the plan path passed to it.

`schemaVersion` and `project` are guaranteed present in files written under this schema (v2). They may be absent in files written before this schema existed (v1) — see "Legacy (schema v1) tolerant read" below; a reader must not assume their presence without checking `schemaVersion` first.

## Arrays are objects, not strings

**`documents`, `remediationPlans`, and `implementationPlans` are arrays of objects, not arrays of strings.** Each save appends a new entry rather than overwriting — documents and plans are never overwritten on disk (each revision is a new file), so the array preserves that history. Each entry carries the fact that is true forever once written (its own path, the document it belongs to, the remediation plan it consumed, what it supersedes, and when it was created) — never a mutable field like a plan's `Status`, which changes over the item's life and is owned by whichever agent writes to the artifact file itself (see the `implement` skill and `implementation-planner` agent for how `Status` and `[x]`/`[ ]`/`FAIL` checkboxes are read and written). Treat the last entry as current unless a step says otherwise.

## Legacy (schema v1) tolerant read

Files written before this schema may still have plain strings inside these arrays instead of objects, and may lack `schemaVersion`/`project`/`updatedAt` entirely. Any reader must accept both shapes: a string entry `"...path..."` is equivalent to `{ "path": "...path...", "document": null, "remediationPlan": null, "supersedes": null, "createdAt": null }`. Never fail or ask the user to migrate — normalize silently. Do not rewrite old entries in place; the next append naturally writes the new shape going forward.

## Resolving links between arrays

Resolve `remediationPlans` against `implementationPlans` using the explicit link fields, not array position. To find the remediation plan an implementation plan consumed, read that implementation plan's own `remediationPlan` field. To find implementation plans that consumed a given remediation plan, filter `implementationPlans` for entries whose `remediationPlan` equals that remediation plan's `path`. A step checking whether a remediation plan's findings still have outstanding work must resolve the implementation plan this way (not "the last entry of `implementationPlans`") and then check: if that implementation plan's on-disk `Status` is `Complete` with no `[ ] FAIL` items under "Modifications to existing files", treat the remediation plan as fully resolved rather than re-surfacing it.

The same link fields resolve the resume-plan flow: an implementation plan whose `supersedes` field is non-null points at the plan it replaced, and any plan matching a given architecture document is found by filtering `implementationPlans` for entries whose `document` field equals that document's path.

## Single writer per key

`stage1`–`stage6c` are written only by `design/SKILL.md`. `documents` is appended to by `design/SKILL.md` (Step 11) and by `review/SKILL.md` (step 4f). `remediationPlans` is appended to only by `review/SKILL.md` (step 4e). `implementationPlans` is appended to only by `implementation-planner`. `architecture-implementer` never writes to `session.json`. No key is ever written by more than the writers listed here.

## No CAS — always read-fresh-modify-write-whole

`session.json` has no locking or compare-and-swap mechanism. Every writer must read the current file fresh immediately before writing, merge its change into the full object, and write the whole file back — never write a partial object or assume an in-memory copy from earlier in the conversation is still current. This is safe because these skills and agents run sequentially within one conversation; do not parallelize two writers against the same `session.json` (e.g. do not spawn `implementation-planner` for two documents concurrently).

## Merge-strategy question

When an existing project is found in the working directory and there is an architecture document to implement from, ask:

> "I found an existing project structure. How would you like to proceed?
> **(a) Merge** — add missing files from the architecture without overwriting existing code
> **(b) Fresh start** — generate the complete skeleton; any file that already exists will be flagged before being overwritten — you decide per collision
> **(c) Let me describe what to keep** — I'll describe my existing layout and we'll work around it"

Wait for the answer before proceeding. `design/SKILL.md` (Step 13), `review/SKILL.md` (step 4h), and `implement/SKILL.md` (Step 2) all ask this identical question before spawning `implementation-planner` — `implement/SKILL.md` is the canonical source of this text.

## Checking whether a remediation plan is fully resolved

A remediation plan (a `remediationPlans` entry) is fully resolved once every code change it lists has been applied. To check: find the entry (or entries) in `implementationPlans` whose `remediationPlan` field equals the remediation plan's `path`, taking the one with the latest `createdAt` if more than one. It is resolved if that implementation plan's `path` exists on disk, its on-disk `Status` is `Complete`, and its "Modifications to existing files" section contains no `[ ] FAIL` items.

Two consumers apply this check for different purposes:
- `review/SKILL.md`'s pre-Step-1 load ("Check for an existing remediation plan"): if resolved, skip straight to the "fully complete" message without re-parsing the remediation plan's own checkboxes.
- `design/SKILL.md` (Step 13) and `implement/SKILL.md` (Step 3), before spawning `implementation-planner`: if resolved, do not pass the remediation plan path — there is nothing left to plan or implement.

## Resumable-plan detection procedure

Three call sites spawn `architecture-designer:implementation-planner` — `design/SKILL.md` (Step 13), `review/SKILL.md` (step 4h), and `implement/SKILL.md` (Step 3). Immediately before spawning, all three run this same procedure against the confirmed architecture document's path (called `{document}` below) to decide whether to offer resuming a previous plan:

Scan `implementationPlans` for entries whose `document` field equals `{document}`. Keep only entries whose `path` still exists on disk and whose plan is actionable — read the plan's metadata table `Status` line: actionable means `Status` is `In progress`, OR `Status` is `Complete` but the plan's checklist contains at least one `[ ] FAIL` item anywhere (not just under "Modifications to existing files"). Do not filter on `Status == In progress` alone — `architecture-implementer` always sets `Status` to `Complete` at the end of a run even when files failed (see its Verification and output step), so `Complete`-with-`FAIL` plans are the common resumable case, not an edge case.

This is a lookup against `session.json` only — no need to open every candidate plan file to check its `document`/`Status`, since schema v2 already carries `document` and `createdAt` on each entry. Only the single winning candidate needs to be opened.

If more than one entry matches, take the one with the latest `createdAt`. If a match remains, read only that one plan file and count its checklist items: `[x]`/`[~]` done, remaining `[ ]`, and `[ ] FAIL` failed. Then offer:

> "There's a previous plan for this document that isn't finished ({N} of {M} files done, {X} failed). Continue from that plan, or start a new plan from scratch?"

If the user chooses to continue, pass the plan's `path` to `implementation-planner` as **Previous plan path**. If they choose fresh, or no matching plan is found, proceed without it.

### Orphaned plans from a prior document revision

The procedure above only matches `implementationPlans` entries whose `document` field equals the *current* document's path. If the architecture document was revised (a new `documents` entry was appended for the same topic, per `review/SKILL.md` step 4f), an actionable plan still pointing at the prior revision's path will never match again — it would otherwise sit `In progress` (or `Complete` with `[ ] FAIL`) forever with no resume offer and no way to close it out.

To catch this, after running the procedure above, also scan `implementationPlans` for actionable entries (same actionability test as above) whose `document` field's `{topic}` slug matches the current document's `{topic}` slug but whose path differs from the current document's path — i.e. plans tied to an earlier revision of the same architecture. If any are found, surface them separately from the resumable-plan offer:

> "Found {N} unfinished plan(s) for an earlier revision of this document (`{old document path}`). They won't be auto-resumed since the document has changed since then. Mark {them/it} as superseded by this revision, or leave as-is to review manually later?"

If the user confirms marking them superseded: for each one, make the same terminal write `implementation-planner` makes when resuming (see "Resolving links between arrays" above) — change the old plan file's `Status` row to `Superseded by document revision {new document path}` — but make this write directly (a plain file edit by the calling skill), since no new plan is being created and `implementation-planner` is not being spawned for this. Do not touch any other part of the old plan file.

# session.json Schema Reference

The full contract for `docs/architecture-designer/session.json` — the canonical schema, the array-of-objects shape used by `documents`, `remediationPlans`, and `implementationPlans`, and the rules every reader and writer across the plugin must follow. `design/SKILL.md` owns this file's top-level structure; `review/SKILL.md`, `implement/SKILL.md`, and `implementation-planner.md` read and append to it per the single-writer-per-key rule below.

## Canonical schema

The top-level keys are fixed; the field names inside each stage object are the user's confirmed answers and may vary:

```json
{
  "schemaVersion": 2,
  "project": "inventory-app",
  "description": "A warehouse inventory management application that lets staff track stock levels, receive shipments, and pick orders across multiple warehouse locations, replacing an error-prone spreadsheet-based process.",
  "updatedAt": "2026-07-13T10:42:00Z",
  "stage1": { "applicationGoal": "...", "stakeholders": "...", "businessProcesses": "...", "painPoints": "...", "successCriteria": "..." },
  "stage2": { "functionalRequirements": ["..."], "nonFunctionalRequirements": { "performance": "...", "security": "...", "compliance": "...", "scalability": "...", "availability": "..." } },
  "stage3": { "budget": "...", "timeline": "...", "regulations": "...", "teamCompetencies": "...", "legacySystems": "...", "cloudPreference": "..." },
  "stage4": { "registeredUsers": "...", "concurrentUsers": "...", "tps": "...", "dataVolume": "...", "readWriteRatio": "...", "peakPatterns": "...", "geography": "..." },
  "stage5": { "architecturePattern": "...", "backend": "...", "frontend": "...", "database": "...", "infrastructure": "...", "supportingServices": "...", "authentication": "...", "observability": "...", "disasterRecovery": "..." },
  "agentTools": [
    { "name": "gopls", "type": "mcp", "purpose": "Diagnostics and symbol search on generated Go files" }
  ],
  "web3": { "trustModel": "...", "immutability": "...", "onChainOffChainBoundary": "...", "externalDataOracles": "...", "finality": "...", "keyManagement": "...", "auditTier": "..." },
  "stage6b": { "tool": "...", "stateBackend": "...", "modules": "...", "envStrategy": "...", "driftDetection": "..." },
  "stage6c": { "platform": "...", "stages": "...", "branchingStrategy": "...", "envPromotion": "...", "secretInjection": "...", "artifactManagement": "..." },
  "documents": [
    { "path": "/absolute/path/to/docs/architecture-designer/architecture/YYYYMMDD-topic.md", "createdAt": "2026-07-13T09:10:00Z" }
  ],
  "remediationPlans": [
    { "path": "/absolute/path/to/docs/architecture-designer/plan/YYYYMMDD-topic-remediation.md", "document": "/absolute/path/to/docs/architecture-designer/architecture/YYYYMMDD-topic.md", "supersedes": null, "createdAt": "2026-07-13T10:05:00Z" }
  ],
  "implementationPlans": [
    { "path": "/absolute/path/to/docs/architecture-designer/plan/YYYYMMDD-topic.md", "document": "/absolute/path/to/docs/architecture-designer/architecture/YYYYMMDD-topic.md", "remediationPlan": null, "supersedes": null, "createdAt": "2026-07-13T10:40:00Z" }
  ]
}
```

Sub-agents receive the full contents of this file as input and must read it tolerantly — inner field names are illustrative, not contractual. The only guaranteed top-level keys are `schemaVersion`, `project`, `description`, `stage1`–`stage5`, and (after Step 11) `documents`. `agentTools` is written after Stage 5 confirmation but is never guaranteed — it may be absent or empty when no matching tools were found; pass it to sub-agents when present but never block on its absence. `stage6b` and `stage6c` are written after Stage 6b/6c confirmation and must be included when passing session context to sub-agents. `remediationPlans` may also appear after `/architecture-designer:review` has run — written by that skill, and must be passed to implementation-planner when present. `implementationPlans` may also appear after `architecture-designer:implementation-planner` has run — written by that agent itself after saving its plan file, not by the `design` skill. `architecture-implementer` never writes to `session.json`; it only reads the plan path passed to it.

`schemaVersion`, `project`, and `description` are guaranteed present in files written under this schema (v2) — none of the three is optional, and a session.json missing any of them is malformed under v2 and must be treated the same as a v1 file for read purposes (see tolerant-read rule below) until repaired. They may be absent in files written before this schema existed (v1) — see "Legacy (schema v1) tolerant read" below; a reader must not assume their presence without checking `schemaVersion` first.

**`description`** is a detailed, multi-sentence description of what the application is and does — its purpose, primary users, and the core problem it solves. It is not a one-line paraphrase or a restatement of the `project` slug; it must give a reader unfamiliar with the project enough context to understand what is being built without reading `stage1` in full. It has two valid sources: the user's own written text (used verbatim, never paraphrased), or a version drafted by `design/SKILL.md` from the Stage 1 answers (application goal, stakeholders, business processes, pain points) and shown to the user for approval/edits before being written. Either way it is required: `design/SKILL.md` must write it at the same time as `schemaVersion` and `project` (Stage 1 confirmation) and must not proceed past Stage 1 without it populated.

**`agentTools`** is optional and, unlike `documents`/`remediationPlans`/`implementationPlans`, is not an append-only history — it is overwritten wholesale each time Stage 5 is confirmed (initial or revised), reflecting only the currently-recommended tools for the currently-confirmed stack. Each entry is `{ "name": "<exact MCP/skill identifier>", "type": "mcp" | "skill" | "plugin", "purpose": "<one line>" }`, drafted per `references/agent-tools.md` from MCP servers and Skills actually available in the environment at Stage 5 — never a fabricated or aspirational tool name. A missing key or an empty array both mean "no matching tools were available for this stack" and are the normal case; no reader should treat either as an error or block on it.

**`web3`** is optional and only written when the Web3 / decentralized track is active per `references/web3-guide.md` — most sessions never write this key. Like `agentTools`, it is overwritten wholesale each time Stage 5 is confirmed (initial or revised), not appended to. Its inner fields are the user's confirmed answers to the guide's seven invariant dimensions; any value not yet confirmed by the user must be a `<VERIFY against {target network}'s official docs: ...>` placeholder, never a value stated from memory. Absence of this key means the application is not decentralized — no reader should treat that as an error.

## Arrays are objects, not strings

**`documents`, `remediationPlans`, and `implementationPlans` are arrays of objects, not arrays of strings.** Each save appends a new entry rather than overwriting — documents and plans are never overwritten on disk (each revision is a new file), so the array preserves that history. Each entry carries the fact that is true forever once written (its own path, the document it belongs to, the remediation plan it consumed, what it supersedes, and when it was created) — never a mutable field like a plan's `Status`, which changes over the item's life and is owned by whichever agent writes to the artifact file itself (see the `implement` skill and `implementation-planner` agent for how `Status` and `[x]`/`[ ]`/`FAIL` checkboxes are read and written). Treat the last entry as current unless a step says otherwise.

## Legacy (schema v1) tolerant read

Files written before this schema may still have plain strings inside these arrays instead of objects, and may lack `schemaVersion`/`project`/`description`/`updatedAt` entirely. Any reader must accept both shapes: a string entry `"...path..."` is equivalent to `{ "path": "...path...", "document": null, "remediationPlan": null, "supersedes": null, "createdAt": null }`. Never fail or ask the user to migrate — normalize silently. Do not rewrite old entries in place; the next append naturally writes the new shape going forward. If a legacy file is being written to and lacks `description`, backfill it at the same time `schemaVersion: 2` and `project` are backfilled (see `design/SKILL.md` Step 11) — synthesize it from whatever `stage1` content is present rather than leaving it absent going forward. Unlike the Stage 1 flow above, this backfill is written silently without re-confirming it with the user: it only summarizes `stage1` data the user already confirmed when it was first written, so there is nothing new to approve.

## Resolving links between arrays

Resolve `remediationPlans` against `implementationPlans` using the explicit link fields, not array position. To find the remediation plan an implementation plan consumed, read that implementation plan's own `remediationPlan` field. To find implementation plans that consumed a given remediation plan, filter `implementationPlans` for entries whose `remediationPlan` equals that remediation plan's `path`. A step checking whether a remediation plan's findings still have outstanding work must resolve the implementation plan this way (not "the last entry of `implementationPlans`") and then check: if that implementation plan's on-disk `Status` is `Complete` with no `[ ] FAIL` items under "Modifications to existing files", treat the remediation plan as fully resolved rather than re-surfacing it.

The same link fields resolve the resume-plan flow: an implementation plan whose `supersedes` field is non-null points at the plan it replaced, and any plan matching a given architecture document is found by filtering `implementationPlans` for entries whose `document` field equals that document's path.

## Single writer per key

"Single writer" means single *mutator*: each key has exactly one writer that may set or overwrite its value, except `documents`, which is append-only and has two legitimate appenders (see the exception below) — append-only removes the lost-update risk that the single-writer rule exists to prevent, so the same guarantee holds without restricting the key to one caller.

`schemaVersion`, `project`, and `description` are written only by `design/SKILL.md`, at Stage 1 confirmation (and backfilled by the same skill on legacy files per Step 11). `stage1`–`stage6c` are written only by `design/SKILL.md`. `agentTools` is written only by `design/SKILL.md`, at Stage 5 confirmation (overwritten in full on any Stage 5 revision, per `references/agent-tools.md`) — no other skill or agent writes to this key. `web3` is written only by `design/SKILL.md`, at Stage 5 confirmation, and only when the Web3 track is active (overwritten in full on any Stage 5 revision, per `references/web3-guide.md`) — no other skill or agent writes to this key.

**Exception — `documents` has two legitimate appenders:** `design/SKILL.md` (Step 11) and `review/SKILL.md` (step 4f) both append to it, and both are valid — each produces an architecture document (an initial design and a revision, respectively), so each is entitled to record the artifact it just wrote. Neither ever mutates or removes another writer's entry; each only appends its own new one. That append-only discipline is what makes two appenders safe here — there is no lost-update to guard against, since no writer's change can clobber another's. `remediationPlans` and `implementationPlans` are also append-only but, unlike `documents`, each currently has only one appender in practice (see below) — nothing here forbids a second legitimate appender being added for those keys too, as long as it only appends.

`remediationPlans` is appended to only by `review/SKILL.md` (step 4e). `implementationPlans` is appended to only by `implementation-planner`. `architecture-implementer` never writes to `session.json`. No key is ever written by more writers than listed here — for `documents`, that means no writer beyond the two named above; for every other key, exactly the one named.

## No CAS — always read-fresh-modify-write-whole

`session.json` has no locking or compare-and-swap mechanism. Every writer must read the current file fresh immediately before writing, merge its change into the full object, and write the whole file back — never write a partial object or assume an in-memory copy from earlier in the conversation is still current. This is safe because these skills and agents run sequentially within one conversation; do not parallelize two writers against the same `session.json` (e.g. do not spawn `implementation-planner` for two documents concurrently).

## Session completeness gate

`design/SKILL.md` (Stage 6), `review/SKILL.md` (before Step 1), and `implement/SKILL.md` (before Step 1) each run `python3 <scripts_dir>/validate-session.py` and show its output before proceeding, whenever `docs/architecture-designer/session.json` exists. The script checks the required top-level fields (`schemaVersion`, `project`, `description`) and confirmation stages 1–5, printing `SESSION CHECK PASSED` or `SESSION CHECK FAILED` with the specific missing fields/stages listed.

**This is a hard gate in all three skills**: if the check fails, do not proceed past the gate. Tell the user which fields and/or stages are missing and ask them to complete them — resuming stages 1–5 in `design`, or supplying the missing information directly so `session.json` can be updated — before continuing. Only proceed once the script reports `SESSION CHECK PASSED`.

Each skill's own trigger condition and rationale differ:
- **`design/SKILL.md`**: the gate always applies at Stage 6, since `design` is the skill that builds `session.json` through stages 1–5 in the first place — there is no "file doesn't exist" branch here. A missing top-level field on an otherwise-complete resumed session is the legacy-backfill case (Step 11), not a missing stage.
- **`review/SKILL.md` and `implement/SKILL.md`**: the gate applies only when `session.json` exists; if it does not exist at all, skip the gate entirely and proceed without session context, since both skills can still work from the architecture document (and, for `review`, the codebase) alone. A session that exists but is incomplete is treated more strictly than no session at all — an incomplete file signals the project started structured requirements tracking and abandoned it partway through, which is a stronger signal to pause and reconcile than never having used it. In `implement` specifically, neither skill step reads stage 1–5 data directly (Step 1 only reads the `documents` array for the document path); the gate exists to catch drift between the confirmed document and the requirements it was supposedly built from, not because implement's own logic consumes the stage fields.

## Proposed Additions rejection handling

`architecture-fixer` and `database-fixer` may return a fix log containing a **"Proposed Additions"** section — changes the fixer recommends beyond what the review report strictly required. Present each item to the user for confirmation before continuing: add confirmed items directly to `diagrams.json`; discard rejected ones.

**A rejected proposed addition does not resolve the finding that generated it.** Note which finding each rejected addition was tied to — the fixer cannot close that finding without the addition. Ask the user directly: accept the residual risk and note it in the document, or describe an alternative fix for the fixer to apply next cycle. Only re-spawn the reviewer once the user has chosen one of these for every rejected addition.

This section applies whenever a fixer's log is checked for "Proposed Additions" — regardless of whether one is found. Re-spawning the reviewer to verify the fixer's changes is a separate, unconditional step at every call site (`design/SKILL.md` Step 7 and Stage 6a, `review/SKILL.md` step 4b and step 4c) — it happens whether or not a Proposed Additions section was present, not only when one was.

## Merge-strategy question

When an existing project is found in the working directory and there is an architecture document to implement from, ask:

> "I found an existing project structure. How would you like to proceed?
> **(a) Merge** — add missing files from the architecture without overwriting existing code
> **(b) Fresh start** — generate the complete skeleton; any file that already exists will be flagged before being overwritten — you decide per collision
> **(c) Let me describe what to keep** — I'll describe my existing layout and we'll work around it"

Wait for the answer before proceeding. `design/SKILL.md` (Step 13), `review/SKILL.md` (step 4h), and `implement/SKILL.md` (Step 2) all ask this identical question before spawning `implementation-planner` — `implement/SKILL.md` is the authoritative owner of this question's exact wording (even though the copy quoted above lives here); if the wording ever needs to change, edit it here and treat `implement/SKILL.md`'s intent as the tiebreaker.

## Existing-project scan categories

Before asking the "Merge-strategy question" above, `design/SKILL.md` (Step 13), `review/SKILL.md` (step 4h), and `implement/SKILL.md` (Step 2) each scan the working directory for signs of an existing project. All three use the same four categories, so that scanning the same directory from any of the three skills reaches the same "empty vs. not empty" conclusion:

- Dependency manifests: `package.json`, `go.mod`, `Cargo.toml`, `requirements.txt`, `pyproject.toml`, `pom.xml`
- Source directories: `src/`, `app/`, `lib/`, `cmd/`, `internal/`
- Configuration: `Dockerfile`, `docker-compose.yml`, `.env`, `.env.example`
- Test directories: `tests/`, `test/`, `spec/`, `__tests__/`

A project is "empty" only if none of the four categories finds anything. If any single category finds something, treat it as "files already exist" and ask the Merge-strategy question above.

## Implementation task-group table

`implementation-planner` (Step 4, "Create implementation tasks") and `architecture-implementer` (Step 1, "Locate the pre-created tasks") both need the identical file-group-to-task-title mapping — the planner creates one `TaskCreate` per row below, and the implementer looks them up by the same titles via `TaskList`. Both agents use this exact table; neither restates it independently:

| Task title                 | What it covers                                                                          |
|----------------------------|-----------------------------------------------------------------------------------------|
| Implement data models      | Model files, migration files, schema/ORM definitions                                    |
| Implement API routes       | Route handlers, controllers, middleware                                                 |
| Write configuration files  | package.json, .env.example, tsconfig, docker-compose, Dockerfile                        |
| Write infrastructure files | Terraform, CDK, Kubernetes manifests, CI/CD pipeline configs                            |
| Write setup scripts        | npm scripts, cross-platform setup and run commands                                      |
| Apply remediation changes  | Modifications to existing files per the remediation plan (only when a plan is provided) |

`implementation-planner` omits any row with no files in the confirmed tree for the current project; `architecture-implementer` only looks up rows that were actually created.

## Checking whether a remediation plan is fully resolved

A remediation plan (a `remediationPlans` entry) is fully resolved once every code change it lists has been applied. To check: find the entry (or entries) in `implementationPlans` whose `remediationPlan` field equals the remediation plan's `path`, taking the one with the latest `createdAt` if more than one. It is resolved if that implementation plan's `path` exists on disk, its on-disk `Status` is `Complete`, and its "Modifications to existing files" section contains no `[ ] FAIL` items.

Two consumers apply this check for different purposes:
- `review/SKILL.md`'s pre-Step-1 load ("Check for an existing remediation plan"): if resolved, skip straight to the "fully complete" message without re-parsing the remediation plan's own checkboxes.
- `design/SKILL.md` (Step 13) and `implement/SKILL.md` (Step 3), before spawning `implementation-planner`: if resolved, do not pass the remediation plan path — there is nothing left to plan or implement.

## Finding the applicable remediation plan

Before spawning `implementation-planner`, `design/SKILL.md` (Step 13) and `implement/SKILL.md` (Step 3) both need to know whether an unresolved remediation plan applies to the document being implemented. Both use the same lookup: in `session.json`'s `remediationPlans` array, find the entry whose `document` field equals the confirmed architecture document's path. If found and its `path` still exists on disk, it is the remediation plan to pass along — unless section "Checking whether a remediation plan is fully resolved" above rules it out (a fully resolved plan is never passed).

A remediation plan's mere presence does not by itself prove an existing codebase. When translating the existing-project scan into the strategy label passed to `implementation-planner`, trust the scan (section "Existing-project scan categories" above), not whether a remediation plan happens to exist — a remediation plan can exist for a project that was never actually built.

## Superseding a remediation plan

`remediationPlans` entries carry a `supersedes` field (mirroring `implementationPlans`), used when `review/SKILL.md`'s pre-Step-1 check offers to carry a previous plan's deferred `[ ]` items forward (see "Check for an existing remediation plan" in that skill) and the user accepts. The old plan file is never edited in place to add or resolve findings — remediation plans follow the same "new file each revision" convention as architecture documents (`review/SKILL.md` step 4e always writes a fresh, collision-suffixed file, never overwriting). Instead, once the new plan is saved in step 4e:

- Set the new entry's `supersedes` field to the old plan's `path`.
- Make one terminal write to the *old* plan file — change its `Status` row to `Superseded by {new plan path}` — the same pattern `implementation-planner` uses for `implementationPlans` (see "Resolving links between arrays" above).

This is what closes out an old plan whose deferred items were folded into a new one. A plan whose deferred items the user declined to carry forward is left untouched and is simply re-offered on the next review session's pre-Step-1 check.

## Reviewer–fixer cycle procedure

Six call sites across `design/SKILL.md` and `review/SKILL.md` spawn a reviewer agent (`architecture-reviewer`, `database-reviewer`, or `document-reviewer`), and on a failing verdict, spawn the matching fixer (`architecture-fixer`, `database-fixer`, or `document-fixer`) before re-verifying. All six follow this same procedure — only the agent names, the artifact being fixed, and the verdict vocabulary vary:

1. Spawn the fixer with the review report, the artifact being corrected (`diagrams.json` path, or the document path for `document-fixer`), and the requirements summary.
2. After the fixer applies its correction, apply section "Proposed Additions rejection handling" above if the fixer's log contains that section.
3. Re-spawn the reviewer to verify. Read the verdict line itself — do not re-derive pass/fail from the findings list.
4. Repeat from step 1 until the exit condition below is met, **up to a maximum of 3 reviewer–fixer cycles**. If it is not met after 3 cycles, stop, present the remaining findings verbatim, and ask the user for guidance rather than cycling further.

**Exit condition — read the reviewer's literal verdict string; the two verdict vocabularies are not interchangeable:**

- **Binary reviewers** (`database-reviewer`, `document-reviewer`): stop once the verdict reads `DATABASE REVIEW PASSED` / `DOCUMENT REVIEW PASSED`. Any `FAILED` verdict means cycle again.
- **Three-tier reviewer** (`architecture-reviewer`): stop once the verdict reads `REVIEW PASSED`. `REVIEW CONDITIONALLY PASSED` is emitted *specifically because* Major findings remain — by the reviewer's own verdict definitions, it can never mean "all Major items resolved." Treat `REVIEW CONDITIONALLY PASSED` as a stop condition only once every remaining Major finding has been through step 2 above (the user explicitly accepted the residual risk or provided an alternative fix for each) — otherwise keep cycling. `REVIEW FAILED` (Critical present) always means cycle again.

Do not open the browser preview, or proceed past the calling step, until this exit condition is met.

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

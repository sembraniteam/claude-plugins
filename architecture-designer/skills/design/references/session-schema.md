# session.json Schema Reference

The full contract for `docs/architecture-designer/session.json` — the canonical schema, the array-of-objects shape used
by `documents`, `remediationPlans`, and `implementationPlans`, and the rules every reader and writer across the plugin
must follow. `design/SKILL.md` owns this file's top-level structure; `review/SKILL.md`, `implement/SKILL.md`, and
`implementation-planner.md` read and append to it per the single-writer-per-key rule below.

## Canonical schema

The top-level keys are fixed; the field names inside each stage object are the user's confirmed answers and may vary:

```json
{
  "schemaVersion": 2,
  "project": "inventory-app",
  "description": "A warehouse inventory management application that lets staff track stock levels, receive shipments, and pick orders across multiple warehouse locations, replacing an error-prone spreadsheet-based process.",
  "updatedAt": "2026-07-13T10:42:00Z",
  "stage1": {
    "applicationGoal": "...",
    "stakeholders": "...",
    "businessProcesses": "...",
    "painPoints": "...",
    "successCriteria": "..."
  },
  "stage2": {
    "functionalRequirements": [
      "..."
    ],
    "nonFunctionalRequirements": {
      "performance": "...",
      "security": "...",
      "compliance": "...",
      "scalability": "...",
      "availability": "...",
      "errorHandling": "..."
    },
    "qualityAttributeScenarios": [
      {
        "id": "QAS-1",
        "qualityAttribute": "Performance",
        "source": "...",
        "stimulus": "...",
        "environment": "...",
        "artifact": "...",
        "response": "...",
        "responseMeasure": "..."
      }
    ],
    "domainEdgeCases": [
      {
        "category": "Inventory & Order Fulfillment",
        "question": "Can a partially-shipped order be cancelled for only its unshipped items?",
        "answer": "No — cancellation is all-or-nothing for v1; partial cancellation is explicitly out of scope."
      }
    ]
  },
  "stage3": {
    "budget": "...",
    "timeline": "...",
    "regulations": "...",
    "teamCompetencies": "...",
    "legacySystems": "...",
    "cloudPreference": "..."
  },
  "stage4": {
    "registeredUsers": "...",
    "concurrentUsers": "...",
    "tps": "...",
    "dataVolume": "...",
    "readWriteRatio": "...",
    "peakPatterns": "...",
    "geography": "..."
  },
  "architecturalDrivers": [
    {
      "id": "AD-1",
      "description": "...",
      "source": "QAS-1",
      "rationale": "..."
    }
  ],
  "stage5": {
    "architecturePattern": "...",
    "backend": "...",
    "frontend": "...",
    "database": "...",
    "infrastructure": "...",
    "supportingServices": "...",
    "authentication": "...",
    "observability": "...",
    "disasterRecovery": "...",
    "errorHandlingResilience": "...",
    "rateLimiting": "...",
    "tradeoffAnalysis": [
      {
        "id": "TO-1",
        "driversInTension": ["AD-1", "AD-2"],
        "tradeoffPoint": "...",
        "sensitivityPoint": "...",
        "decision": "...",
        "rationale": "...",
        "relatedRisks": ["RISK-1"]
      }
    ],
    "costEstimate": {
      "breakdown": [
        {
          "component": "Database",
          "serviceTier": "AWS RDS PostgreSQL db.t3.medium, Multi-AZ",
          "monthlyCost": "...",
          "sizingBasis": "...",
          "source": "WebSearch verified 29-Jul-2026"
        }
      ],
      "monthlyTotal": "...",
      "annualTotal": "...",
      "scaleSensitivity": "...",
      "budgetReconciliation": "..."
    }
  },
  "riskRegister": [
    {
      "id": "RISK-1",
      "category": "Technical",
      "description": "...",
      "likelihood": "Medium",
      "impact": "Medium",
      "mitigation": "...",
      "relatedDriver": "AD-1",
      "status": "Open"
    }
  ],
  "domainModel": {
    "boundedContexts": [
      {
        "name": "...",
        "description": "...",
        "aggregates": [
          {
            "name": "...",
            "rootEntity": "...",
            "entities": ["..."],
            "invariants": ["..."]
          }
        ],
        "ubiquitousLanguage": {
          "term": "definition"
        }
      }
    ],
    "relationships": [
      {
        "from": "...",
        "to": "...",
        "pattern": "Customer/Supplier",
        "description": "..."
      }
    ]
  },
  "agentTools": [
    {
      "name": "gopls",
      "type": "mcp",
      "purpose": "Diagnostics and symbol search on generated Go files"
    }
  ],
  "web3": {
    "trustModel": "...",
    "immutability": "...",
    "onChainOffChainBoundary": "...",
    "externalDataOracles": "...",
    "finality": "...",
    "keyManagement": "...",
    "auditTier": "...",
    "crossChainBridgeRisk": "..."
  },
  "offlineFirst": {
    "localStorage": "...",
    "syncArchitecture": "...",
    "conflictResolution": "...",
    "deleteHandling": "..."
  },
  "stage6b": {
    "tool": "...",
    "stateBackend": "...",
    "modules": "...",
    "envStrategy": "...",
    "driftDetection": "..."
  },
  "stage6c": {
    "platform": "...",
    "stages": "...",
    "branchingStrategy": "...",
    "envPromotion": "...",
    "secretInjection": "...",
    "artifactManagement": "..."
  },
  "pending": {
    "stage": "stage2",
    "answers": {
      "functionalRequirements": [
        "..."
      ]
    },
    "updatedAt": "2026-07-13T09:40:00Z"
  },
  "progress": {
    "owner": "design",
    "lastCompletedStep": "step7",
    "reviewCycles": {
      "database": {
        "verdict": "DATABASE REVIEW PASSED",
        "cycleCount": 1,
        "approvedOutput": "... full schema/ERD/index plan/engine/connection-config text ...",
        "updatedAt": "2026-07-13T09:55:00Z"
      },
      "architecture": {
        "verdict": "REVIEW PASSED",
        "cycleCount": 2,
        "diagramsHash": "sha256:...",
        "updatedAt": "2026-07-13T10:20:00Z"
      },
      "document": {
        "verdict": "DOCUMENT REVIEW PASSED",
        "cycleCount": 1,
        "documentHash": "sha256:...",
        "updatedAt": "2026-07-13T10:50:00Z"
      }
    },
    "updatedAt": "2026-07-13T10:20:00Z"
  },
  "lld": {
    "apiContracts": "...",
    "businessRules": "...",
    "dtos": "...",
    "interServiceContracts": "...",
    "errorCatalog": "...",
    "confirmedGroups": [
      "apiContracts",
      "businessRules"
    ],
    "updatedAt": "2026-07-13T10:35:00Z"
  },
  "testStrategy": {
    "testPyramid": "...",
    "loadTesting": "...",
    "resilienceTesting": "...",
    "securityTesting": "...",
    "uat": "..."
  },
  "adrs": [
    {
      "id": "ADR-0001",
      "path": "/absolute/path/to/docs/architecture-designer/adr/0001-database-engine-selection.md",
      "title": "Database engine selection",
      "status": "Accepted",
      "relatedDecision": "database",
      "supersedes": null,
      "createdAt": "2026-07-13T10:38:00Z"
    }
  ],
  "documents": [
    {
      "path": "/absolute/path/to/docs/architecture-designer/architecture/YYYYMMDD-topic.md",
      "createdAt": "2026-07-13T09:10:00Z"
    }
  ],
  "remediationPlans": [
    {
      "path": "/absolute/path/to/docs/architecture-designer/plan/YYYYMMDD-topic-remediation.md",
      "document": "/absolute/path/to/docs/architecture-designer/architecture/YYYYMMDD-topic.md",
      "supersedes": null,
      "createdAt": "2026-07-13T10:05:00Z"
    }
  ],
  "implementationPlans": [
    {
      "path": "/absolute/path/to/docs/architecture-designer/plan/YYYYMMDD-topic.md",
      "document": "/absolute/path/to/docs/architecture-designer/architecture/YYYYMMDD-topic.md",
      "remediationPlan": null,
      "supersedes": null,
      "createdAt": "2026-07-13T10:40:00Z"
    }
  ],
  "reviewHistory": [
    {
      "date": "2026-07-20T14:15:00Z",
      "source": "codebase",
      "outcome": "declined",
      "summary": "Payment service uses Memcached instead of the documented Redis; user declined to revise.",
      "path": "/absolute/path/to/docs/architecture-designer/review/20260720-topic-review.md"
    }
  ]
}
```

Sub-agents receive the full contents of this file as input and must read it tolerantly — inner field names are
illustrative, not contractual. The only guaranteed top-level keys are `schemaVersion`, `project`, `description`,
`stage1`–`stage5`, and (after Step 11) `documents`. `agentTools` is written after Stage 5 confirmation but is never
guaranteed — it may be absent or empty when no matching tools were found; pass it to sub-agents when present but never
block on its absence. `stage6b` and `stage6c` are written after Stage 6b/6c confirmation and must be included when
passing session context to sub-agents. `remediationPlans` may also appear after `/architecture-designer:review` has
run — written by that skill, and must be passed to implementation-planner when present. `reviewHistory` may also appear
after `/architecture-designer:review` has run — append-only, written solely by that skill (unlike
`documents`/`adrs`, no other skill ever appends to it), one entry per Step 3 reached regardless of whether the user
chose to revise; read it (if present) only to surface prior findings for continuity per its own "Check for prior review
history" step, never as a gate. `implementationPlans` may also appear after
`architecture-designer:implementation-planner` has run — written by that agent itself after saving its plan file, not by
the `design` skill. Each entry may also carry an optional `split` object when the plan was too large for one file — see
"Resolving a split plan's parts" below. `architecture-implementer` never writes to `session.json`; it only reads the
plan path passed to it. `progress`, `lld`, `testStrategy`, `adrs`, and `pending` are never guaranteed either — see their
own paragraphs below and "Resuming Steps 6a–13 via `progress`" for how a reader distinguishes their absence (nothing
reached Stage 6a yet) from a resumed legacy session that predates this schema addition (same "absent means
not-yet-applicable" treatment either way — no reader should error on their absence).

**`testStrategy`** is optional and holds the confirmed Test Strategy content from Step 10b, written once Step 10b's plan
is confirmed. Two writers: `design/SKILL.md` Step 10b (first write, for a project's initial plan) and `review/SKILL.md`
's
"Update Test Strategy" step (4d.6, an authorized second writer, same class of exception as `lld` above) — it overwrites
the key in full whenever 4a flags an NFR, capacity, resilience/rate-limiting, or core-feature change; a revision outside
that scope leaves the prior pass's plan as confirmed. Step 11/4f reads this key to build document section 17. Absence
means Step 10b hasn't confirmed a plan yet, or the session predates this key.

**`adrs`** is optional and holds the append-only history of generated Architecture Decision Records, per
`references/adr-guide.md`. Two appenders: `design/SKILL.md` Step 11 (first write, for a project's initial decisions) and
`review/SKILL.md` step 4f (an authorized second appender, mirroring the `documents` append-only exception below) — each
appends new entries for newly-qualifying or superseding decisions; neither ever mutates or removes another entry (a
superseded ADR's own file gets a terminal `Status` edit per `references/adr-guide.md`'s "Revising ADRs," but its
`session.json` entry is never rewritten — the newer entry's `supersedes` field is what records the relationship). Step
11/4f reads this key to build document section 18's pointer table. Absence means no ADR has been generated yet, or the
session predates this key.

**`pending`** is optional and holds whatever answers have been gathered so far for the stage or step currently in
progress, before that stage's own confirmed key is written. It is overwritten wholesale (not merged) each time a new
answer is captured within the same stage, and deleted entirely — not left stale — the moment that stage's real key is
written at confirmation. See "Mid-stage pending answers" below for the full rule; both `design/SKILL.md` and
`review/SKILL.md` step 4a are authorized writers, mirroring the `web3`/`stage6b`/`stage6c` two-writer pattern for the
same sequential-execution reason. Absence means either nothing is mid-stage right now, or the session predates this
key — both are the normal case.

**`progress`** is optional and tracks how far Stage 6a–Step 13 has gotten in the current design/revision pipeline, so a
resumed session doesn't have to re-derive this from document/diagram side effects alone or blindly re-run expensive
reviewer cycles. It has two authorized writers (`design/SKILL.md` and `review/SKILL.md`), updated incrementally
throughout Stage 6a onward rather than written once — see "Recording `progress.lastCompletedStep`" and "Resuming Steps
6a–13 via `progress`" below for the full contract, and "Reviewer–fixer cycle procedure" for how `reviewCycles` entries
get written. `owner` (`"design"` or `"review"`) records which skill's pipeline pass this `progress` snapshot belongs
to — write it (overwrite in full) the first time either skill touches `progress` in a new pass (Stage 6a for `design`,
step 4b for `review`), so a skill resuming a session can tell whether an in-flight `progress` belongs to its own
interrupted run or to the other skill's, rather than assuming ownership. Absence means no design/revision pipeline has
reached Stage 6a yet in this session's current cycle, or the session predates this key.

**`lld`** is optional and holds the confirmed Low-Level Design content from Step 10, written incrementally as each of
the five artifact groups is confirmed rather than batched at the end. Two writers: `design/SKILL.md` Step 10 (first
write, for a project's initial LLD) and `review/SKILL.md`'s "Update Low-Level Design" step, 4d.5 (an authorized second
writer, same class of exception as `stage6b`/`stage6c`/`web3`/`offlineFirst` below — safe because
`design` and `review` never run concurrently within one conversation) — it updates only the LLD groups a revision's
scope (4a) actually flagged, leaving groups it didn't touch as confirmed by the prior pass. Step 11/4f reads this key to
build document section 10 instead of relying on conversation memory. Absence means Step 10 hasn't confirmed any group
yet, or the session predates this key.

`schemaVersion`, `project`, and `description` are guaranteed present in files written under this schema (v2) — none of
the three is optional, and a session.json missing any of them is malformed under v2 and must be treated the same as a v1
file for read purposes (see tolerant-read rule below) until repaired. They may be absent in files written before this
schema existed (v1) — see "Legacy (schema v1) tolerant read" below; a reader must not assume their presence without
checking `schemaVersion` first.

**`description`** is a detailed, multi-sentence description of what the application is and does — its purpose, primary
users, and the core problem it solves. It is not a one-line paraphrase or a restatement of the `project` slug; it must
give a reader unfamiliar with the project enough context to understand what is being built without reading `stage1` in
full. It has two valid sources: the user's own written text (used verbatim, never paraphrased), or a version drafted by
`design/SKILL.md` from the Stage 1 answers (application goal, stakeholders, business processes, pain points) and shown
to the user for approval/edits before being written. Either way it is required: `design/SKILL.md` must write it at the
same time as `schemaVersion` and `project` (Stage 1 confirmation) and must not proceed past Stage 1 without it
populated.

**`agentTools`** is optional and, unlike `documents`/`remediationPlans`/`implementationPlans`, is not an append-only
history — it is overwritten wholesale each time Stage 5 is confirmed (initial or revised), reflecting only the
currently-recommended tools for the currently-confirmed stack. Each entry is
`{ "name": "<exact MCP/skill identifier>", "type": "mcp" | "skill", "purpose": "<one line>" }`, drafted per
`references/agent-tools.md` from MCP servers and Skills actually available in the environment at Stage 5 — never a
fabricated or aspirational tool name. A missing key or an empty array both mean "no matching tools were available for
this stack" and are the normal case; no reader should treat either as an error or block on it.

**`web3`** is optional and only written when the Web3 / decentralized track is active per `references/web3-guide.md` —
most sessions never write this key. Like `agentTools`, it is overwritten wholesale each time Stage 5 is confirmed
(initial or revised), not appended to — and, unlike `agentTools`, it has a second authorized writer (`review/SKILL.md`
step 4b, on a decentralization-status-changing revision; see "Single writer per key" below for the exact carve-out). Its
inner fields are the user's confirmed answers to the guide's eight invariant dimensions; any value not yet confirmed by
the user must be a `<VERIFY against {target network}'s official docs: ...>` placeholder, never a value stated from
memory. Absence of this key means the application is not decentralized — no reader should treat that as an error.

**`offlineFirst`** is optional and only written when the offline-first track is active per
`references/offline-first-guide.md` — most sessions never write this key. Same write pattern as `web3`: overwritten
wholesale each time Stage 5 is confirmed (initial or revised), with `review/SKILL.md` step 4b as the same-shaped second
authorized writer on an offline-requirement-changing revision. Its inner fields (`localStorage`, `syncArchitecture`,
`conflictResolution`, `deleteHandling`) are the user's confirmed answers to that guide's questions — unlike `web3`'s
dimensions, these are grounded in stable, well-established sync patterns rather than facts about an external network, so
no `<VERIFY>` placeholder discipline applies here. Absence of this key means the application has no offline
requirement — no reader should treat that as an error. Presence of this key is also what `database-designer` uses to
trigger adding the offline-sync schema columns (`references/offline-first-guide.md` section 4) — see that agent's Step

2.

## Arrays are objects, not strings

**`documents`, `remediationPlans`, and `implementationPlans` are arrays of objects, not arrays of strings.** Each save
appends a new entry rather than overwriting — documents and plans are never overwritten on disk (each revision is a new
file), so the array preserves that history. Each entry carries the fact that is true forever once written (its own path,
the document it belongs to, the remediation plan it consumed, what it supersedes, and when it was created) — never a
mutable field like a plan's `Status`, which changes over the item's life and is owned by whichever agent writes to the
artifact file itself (see the `implement` skill and `implementation-planner` agent for how `Status` and `[x]`/`[ ]`/
`FAIL` checkboxes are read and written). Treat the last entry as current unless a step says otherwise.

## Legacy (schema v1) tolerant read

Files written before this schema may still have plain strings inside these arrays instead of objects, and may lack
`schemaVersion`/`project`/`description`/`updatedAt` entirely. Any reader must accept both shapes: a string entry
`"...path..."` is equivalent to `{ "path": "...path..." }`, with every other field (e.g. `document`/`remediationPlan`/
`supersedes`/`createdAt` on `implementationPlans`, `document`/`supersedes`/`createdAt` on `remediationPlans`,
`createdAt` on `documents`) simply absent rather than backfilled with an explicit `null` — treat "absent" and
"explicit null" as equivalent when reading. Never fail or ask the user to migrate — normalize silently. Do not rewrite
old entries in place; the next append naturally writes the new shape going forward. If a legacy file is being written to
and lacks `description`, backfill it at the same time
`schemaVersion: 2` and `project` are backfilled (see `design/SKILL.md`'s "Legacy-session backfill check," run at session
resume and again at the Stage 6 gate — Step 11's own backfill note is the same check, just triggered by a document save
instead) — synthesize it from whatever `stage1` content is present rather than leaving it absent going forward. Unlike
the Stage 1 flow above, this backfill is written silently without re-confirming it with the user: it only summarizes
`stage1` data the user already confirmed when it was first written, so there is nothing new to approve.

## Legacy-session backfill check

`design/SKILL.md` runs this check at three points: immediately when resuming an existing session, again immediately
before the Stage 6 "Session completeness gate" below (in case the session was resumed partway and only reached full
stage1–5 confirmation between those two points in the conversation), and a third time at Step 11 as part of saving the
architecture document — see "Legacy (schema v1) tolerant read" above, whose own backfill note is this same check, just
triggered by a document save instead of a session resume.

**Trigger**: `schemaVersion`, `project`, or `description` is missing **and `stage1` is present** — a v1 file with real
Stage 1 content that never got the newer top-level fields. This is distinct from the `pending`-only case in "Mid-stage
pending answers" below (a session holding only `pending` with no `stage1` yet means Stage 1 simply hasn't been
confirmed, not a legacy file to repair).

**Procedure**: when triggered, backfill immediately — do not wait for Step 11 — synthesizing `description` from whatever
`stage1` content is present, per the backfill rule in "Legacy (schema v1) tolerant read" above, and writing it silently
(no user confirmation needed, since it only summarizes `stage1` data the user already confirmed). This applies
regardless of how many of stage1–5 are confirmed at the point the check runs — even a session resumed after only
stage1–2 was ever confirmed needs this now, since stages 3–6 never re-touch these top-level fields. Skipping this check
leaves the Stage 6 completeness gate permanently unpassable for that session, since Stage 1 never runs again to supply
the missing fields.

## Resolving links between arrays

Resolve `remediationPlans` against `implementationPlans` using the explicit link fields, not array position. To find the
remediation plan an implementation plan consumed, read that implementation plan's own `remediationPlan` field. To find
implementation plans that consumed a given remediation plan, filter `implementationPlans` for entries whose
`remediationPlan` equals that remediation plan's `path`. A step checking whether a remediation plan's findings still
have outstanding work must resolve the implementation plan this way (not "the last entry of `implementationPlans`") and
then check: if that implementation plan's on-disk `Status` is `Complete` with no `[ ] FAIL` items under "Modifications
to existing files", treat the remediation plan as fully resolved rather than re-surfacing it.

The same link fields resolve the resume-plan flow: an implementation plan whose `supersedes` field is non-null points at
the plan it replaced, and any plan matching a given architecture document is found by filtering `implementationPlans`for
entries whose `document` field equals that document's path.

## Resolving a split plan's parts

`implementationPlans` entries may carry an optional `split` object —
`{ "part": <1-based index>, "total": <part count>, "previousPlan": "<path or null>", "nextPlan": "<path or null>" }` —
written by `implementation-planner` when a plan's checklist was too large for one file (see that agent's "Splitting
large plans" step). Its absence means the plan was not split; no reader should treat a missing `split` key as an error,
the same convention as `agentTools`. To walk a split plan's parts in order, follow `split.nextPlan` starting from the
entry whose `split.part` is `1` (or resolve by filename: `{yyyymmdd}-{topic}-part{n}-of-{N}.md`) rather than assuming
array order — `implementationPlans` is a flat, append-only history that may contain unrelated plans for other documents
interleaved between a split plan's own entries.

## Implementation-planner → architecture-implementer spawn sequence

`design/SKILL.md` (Step 13), `review/SKILL.md` (step 4h), and `implement/SKILL.md` (Steps 3–4) all spawn
`implementation-planner` and then `architecture-implementer` in this same two-step sequence, differing only in how each
call site sources its own six input values (document path, existing project summary/strategy label, technology stack,
agent tools, remediation plan path, previous plan path) — see each call site for that detail, not restated here:

1. Spawn `architecture-designer:implementation-planner` with the six inputs.
2. Wait for it to report the plan was saved and confirmed; do not proceed if it did not. `implementation-planner` never
   produces a distinct failure report — per its own Step 1, it simply does not reach the "Implementation Plan Ready"
   report while ambiguities remain unresolved. If its turn ends without that report, keep resolving the open question
   with the user and re-spawn it once ready.
3. Spawn `architecture-designer:architecture-implementer` with the first plan file's path (Part 1, if
   implementation-planner split the plan — see its "Output" section), plus the same document path, existing project
   summary, technology stack, agent tools, and remediation plan path.
4. If the plan was split into multiple parts, follow "Split-plan implementation loop" below to spawn
   `architecture-implementer` again for each subsequent part in order, until its stop condition is met.
5. **Once implementation is complete** — immediately after step 3 if the plan was not split, or once "Split-plan
   implementation loop" reaches its stop condition if it was — run "Implementation reviewer–fixer cycle" below before
   the calling skill's post-implementation wrap-up step. This step applies unconditionally, split or not; it is not part
   of the split-only loop below.

## Split-plan implementation loop

Three call sites reach this loop after "Implementation-planner → architecture-implementer spawn sequence" above has
already spawned `architecture-implementer` on Part 1 (its step 3) — `design/SKILL.md` (Step 13), `review/SKILL.md` (step
4h), and `implement/SKILL.md` (Step 4). This loop picks up from there; it does not re-spawn Part 1:

1. Once the current part's `Status` reads `Complete`, read its `Next plan` metadata-table row —
   `architecture-implementer` states this verbatim in its summary (see its "Reporting a split plan's next part" step),
   so there is no need to re-open the plan file to find it.
2. If `Next plan` names another file (not `None — final part`), spawn `architecture-designer:architecture-implementer`
   again with that file's path (same document path, existing project summary, technology stack, agent tools, and
   remediation plan path used for every prior part) and repeat from step 1.
3. Stop once a part's `Next plan` row reads `None — final part` — this is this loop's stop condition, referenced by step
   5 of "Implementation-planner → architecture-implementer spawn sequence" above.

Report each part's completion to the user as it finishes, rather than staying silent through all parts. A calling skill
with its own post-implementation wrap-up step (e.g. `implement/SKILL.md`'s Step 5) proceeds to it only once the parent
sequence's step 5 review cycle reaches its exit condition — not after any individual part, and not merely once every
part reports `Complete`. A part reporting `Complete` means `architecture-implementer` believes its own work is done; it
does not yet mean an independent check has confirmed that.

## Implementation reviewer–fixer cycle

Spawn `architecture-designer:implementation-reviewer` with: the full ordered list of plan file path (s) (every part, if
split; the single path otherwise), the architecture document path, the technology stack, and the `agentTools` array if
present. This follows the same "Reviewer–fixer cycle procedure" below, with `implementation` as the `<type>` — read that
section for the full step 0–4 mechanics (unconditional recording, the fixer spawn, re-verification, the 3-cycle cap)
rather than a restated copy here. Two implementation-specific details that section doesn't cover:

- **Status re-arm**: if `implementation-fixer` is spawned (a FAILED verdict), it flips the last plan part's `Status`
  row from `Complete` back to `In progress` for the duration of its fix pass, then back to `Complete` once its fixes are
  confirmed — see `agents/implementation-fixer.md`'s "Re-arm the deploy-command hook for the duration of this run" for
  why. This is the one case in this cycle where `Status` moves after `architecture-implementer` already set it; no
  calling-skill action is needed for this — the fixer does it directly, as part of its own write pass.
- **Exit condition applies before wrap-up, not before a preview or an approval gate**: unlike the other three cycle
  types (which block a browser preview or a document's `Approved` status), this cycle's exit condition
  (`IMPLEMENTATION REVIEW PASSED`, or the 3-cycle cap reached) gates the calling skill's post-implementation wrap-up
  step (`design/SKILL.md` Step 13, `review/SKILL.md` step 4h, `implement/SKILL.md` Step 5) — do not tell the user
  implementation is finished, or hand back the "Next steps" list, until this exit condition is met. If the 3-cycle cap
  is reached without a PASSED verdict, present the remaining findings verbatim and let the user decide whether to
  proceed to wrap-up anyway or investigate further — same as the general procedure's own cap handling.

## Single writer per key

"Single writer" means single *mutator*: each key has exactly one writer that may set or overwrite its value, except
`documents`/`adrs` (append-only, two legitimate appenders each — see the exception below) and `web3`/`offlineFirst`/
`stage6b`/`stage6c`/`progress`/`pending`/`architecturalDrivers`/`riskRegister`/`domainModel`/
`stage2.qualityAttributeScenarios`/`stage5.tradeoffAnalysis`/`stage5.costEstimate`/`lld`/`testStrategy`/
`stage2.domainEdgeCases` (each with two legitimate whole-value overwriters, or in `lld`'s/`testStrategy`'s/
`stage2.domainEdgeCases`'s case two legitimate incremental-writers — see below). These exceptions exist for different
reasons: `documents`'s and `adrs`'s two appenders are safe because append-only removes the lost-update risk the
single-writer rule exists to prevent; the rest's two overwriters are safe for the sequential-execution reason given
below, not an append-only one.

`schemaVersion`, `project`, and `description` are written only by `design/SKILL.md`, at Stage 1 confirmation (and
backfilled by the same skill on legacy files per Step 11). `stage1`, `stage3`, and `stage4` are written only by
`design/SKILL.md`. `stage2` is written only by `design/SKILL.md`, **except its nested `qualityAttributeScenarios`
field**, which has one authorized second writer: `review/SKILL.md` step 4b overwrites it in full when step 4a flags an
NFR change, per `references/quality-driven-design-guide.md`. `stage2.domainEdgeCases` also has one authorized second
writer — `review/SKILL.md` step 4b — but unlike `qualityAttributeScenarios` it is written incrementally (new entries
appended for a newly-matched category), the same class of exception as `lld`/`testStrategy` below rather than the
whole-value-overwrite pattern: an existing category's answer is still valid after an unrelated revision and is never
re-asked or removed just because a different category was newly matched, per `references/domain-edge-cases-guide.md` —
every other `stage2` field is written only by `design/SKILL.md`. `stage5` follows the identical whole-value-overwrite
pattern for its nested
`tradeoffAnalysis` field: written by `design/SKILL.md` at Stage 5 confirmation, with `review/SKILL.md` step 4b as the
same authorized second writer when a revision changes a technology decision or introduces a new requirement tension.
`stage5.costEstimate` follows the same two-writer pattern: written by `design/SKILL.md` at Stage 5 confirmation, with
`review/SKILL.md` step 4b as the same authorized second writer when a revision changes a capacity number or a
cost-affecting technology decision, per `references/cost-estimation-guide.md` — every other `stage5` field is written
only by `design/SKILL.md`. `architecturalDrivers` and `riskRegister` are written by `design/SKILL.md` at Stage 5
confirmation (overwritten in full on any Stage 2 or Stage 5 revision per Step 9, per
`references/quality-driven-design-guide.md`), with the same authorized second writer: `review/SKILL.md` step 4b
overwrites either in full when step 4a flags an NFR change or a technology-decision/requirement-tension change,
mirroring exactly how it handles `web3` below. `domainModel` is written by `design/SKILL.md` at Stage 6a (overwritten in
full when Stage 6a's domain modeling is re-run per Step 9, per `references/ddd-guide.md`), with the same authorized
second writer: `review/SKILL.md` step 4b overwrites it in full when step 4a flags a bounded-context or
aggregate-boundary change. `agentTools` is written only by `design/SKILL.md`, at Stage 5 confirmation (overwritten in
full on any Stage 5 revision, per `references/agent-tools.md`) — no other skill or agent writes to this key. `lld` is
written by `design/SKILL.md` at Step 10, incrementally per confirmed artifact group, with one authorized second writer:
`review/SKILL.md`'s "Update Low-Level Design" step (4d.5) updates the same key, incrementally per group, whenever 4a
flags a change touching an API contract, business rule, DTO, inter-service contract, or error condition — groups outside
that revision's scope are left as `design`/a prior revision confirmed them. `testStrategy` follows a similar pattern —
written by `design/SKILL.md` at Step 10b (overwritten in full, not per-group like `lld`, since its five parts are
confirmed together in one round-trip per `references/test-strategy-guide.md`), with `review/SKILL.md`'s "Update Test
Strategy" step (4d.6) as the authorized second writer whenever 4a flags an NFR, capacity, resilience/rate-limiting, or
core-feature change. `web3` is written by
`design/SKILL.md` at Stage 5 confirmation, and only when the Web3 track is active (overwritten in full on any Stage 5
revision, per `references/web3-guide.md`) — with one authorized second writer: `review/SKILL.md` step 4b also overwrites
it in full when a revision changes the project's decentralization status (creating the key if newly decentralized,
updating it if the target network or a dimension's answer changed, or deleting it entirely if the decentralized
component was removed). `offlineFirst` follows the identical pattern — written by `design/SKILL.md` at Stage 5
confirmation, only when the offline-first track is active (per
`references/offline-first-guide.md`), with `review/SKILL.md` step 4b as the same authorized second writer when a
revision changes the project's offline requirement. `stage6b` and `stage6c` are written by `design/SKILL.md` at their
respective confirmation steps — with the same one authorized second writer: `review/SKILL.md` step 4b also overwrites
either in full when a revision changes the infrastructure provider, IaC tool, or CI/CD platform (per
`references/iac-guide.md`/`references/cicd-guide.md`), mirroring exactly how it handles `web3`. `progress` is written by
both `design/SKILL.md` (from Stage 6a onward) and `review/SKILL.md` (from step 4b onward) — see "Recording
`progress.lastCompletedStep`" and "Reviewer–fixer cycle procedure" for exactly what each write updates; unlike the other
two-writer keys, its writes are incremental field-level updates within the same read-fresh-modify-write-whole cycle
rather than one wholesale overwrite per skill run, since either skill may touch it many times across a single pipeline
pass. `pending` is written by both `design/SKILL.md` (Stages 1–6c) and `review/SKILL.md` (step 4a) — always overwritten
wholesale with the stage currently in progress, and deleted (not left stale) once that stage's real key is confirmed.
All fifteen two-writer keys/fields (`web3`, `offlineFirst`, `stage6b`, `stage6c`, `progress`, `pending`,
`architecturalDrivers`, `riskRegister`, `domainModel`, `stage2.qualityAttributeScenarios`, `stage5.tradeoffAnalysis`,
`stage5.costEstimate`, `lld`, `testStrategy`, `stage2.domainEdgeCases`) are safe for the same reason stated in "No CAS —
always read-fresh-modify-write-whole" below: these skills never run concurrently within one conversation, so whichever
write happens later is always the intentionally-authoritative one, not a lost update — unlike `documents`'s/`adrs`'s two
appenders, most of these keys' writers overwrite the whole value (or, for `progress`/`lld`/`testStrategy`, individual
fields/groups within it) rather than append; `stage2.domainEdgeCases` is the one exception that appends new entries (per
`references/domain-edge-cases-guide.md`) rather than overwriting the array, but is still safe for the identical
sequential-execution reason, not an append-only one (unlike `documents`/`adrs`, a second `stage2.domainEdgeCases`
writer appending concurrently within the same conversation is not a scenario this plugin's skills ever create). No other
skill or agent writes to any of these keys.

**Exception — `documents` and `adrs` each have two legitimate appenders:** `design/SKILL.md` (Step 11) and
`review/SKILL.md` (step 4f) both append to `documents`, and both are valid — each produces an architecture document (an
initial design and a revision, respectively), so each is entitled to record the artifact it just wrote. The same two
call sites append to `adrs` for the same reason — each produces newly-qualifying or superseding ADRs at the point it
saves a document, per `references/adr-guide.md`. Neither ever mutates or removes another writer's entry; each only
appends its own new one (for `adrs`, a superseded decision's *new* entry records the relationship via its own
`supersedes` field — the old entry itself is never rewritten). That append-only discipline is what makes two appenders
safe here — there is no lost-update to guard against, since no writer's change can clobber another's. `remediationPlans`
and
`implementationPlans` are also append-only but, unlike `documents`/`adrs`, each currently has only one appender in
practice (see below) — nothing here forbids a second legitimate appender being added for those keys too, as long as it
only appends.

`remediationPlans` is appended to only by `review/SKILL.md` (step 4e). `implementationPlans` is appended to only by
`implementation-planner`. `reviewHistory` is appended to only by `review/SKILL.md` (Step 3) — unlike `documents`/`adrs`,
it has exactly one appender, not two; nothing else in this plugin ever writes to it. `architecture-implementer` never
writes to `session.json`. No key is ever written by more writers than listed here — for `documents`, `adrs`, `web3`,
`offlineFirst`, `stage6b`, `stage6c`, `progress`, `pending`,
`architecturalDrivers`, `riskRegister`, `domainModel`, `stage2.qualityAttributeScenarios`, `stage2.domainEdgeCases`,
`stage5.tradeoffAnalysis`, `stage5.costEstimate`, `lld`, and `testStrategy`, that means no writer beyond the two named
above for each; for every other key, exactly the one named.

## Recording `progress.lastCompletedStep`

Both `design/SKILL.md` and `review/SKILL.md` mark their pipeline position using one shared vocabulary, so a resumed
session reads the same signal regardless of which skill last advanced it. After completing the work each row describes,
write that row's label to `session.json`'s `progress.lastCompletedStep` (read-fresh-modify-write-whole, same as any
other field in this key):

| Label     | `design/SKILL.md`                          | `review/SKILL.md`                                                                                                                       |
|-----------|--------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| `step6a`  | Stage 6a — database design reviewed/passed | step 4b's database-design portion, when it runs                                                                                         |
| `step6d`  | Stage 6e — `diagrams.json` fully written   | step 4b — revised diagrams fully written                                                                                                |
| `step7`   | Step 7 — architecture review passed        | step 4c — architecture re-review passed                                                                                                 |
| `step8`   | Step 8 — browser preview opened            | step 4d — preview opened/refreshed                                                                                                      |
| `step9`   | Step 9 — user confirmed the design         | step 4d — user confirmed the revision                                                                                                   |
| `step10`  | Step 10 — all five LLD groups confirmed    | "Update Low-Level Design" step (4d.5) — run only when 4a flagged an LLD-affecting change; skip straight to `step10b`/`step11` otherwise |
| `step10b` | Step 10b — Test Strategy confirmed         | "Update Test Strategy" step (4d.6) — run only when 4a flagged a test-affecting change; skip straight to `step11` otherwise              |
| `step11`  | Step 11 — document saved (incl. ADRs)      | step 4f — revised document saved (incl. ADRs)                                                                                           |
| `step12`  | Step 12 — document reviewed/approved       | step 4g — document reviewed/approved                                                                                                    |
| `step13`  | Step 13 — implementation offered           | step 4h — implementation offered                                                                                                        |

Each label supersedes the previous one (this is forward progress through one pipeline pass, not a set) — writing `step9`
after `step7` is normal; writing `step7` after `step9` only happens if the user requested a revision that regresses the
pipeline (e.g. Step 9's "if the user requests revisions" branch), in which case write the earlier label again to reflect
that the later steps must be re-done. See "Resuming Steps 6a–13 via `progress`" below for how this label is consumed on
resume.

## Mid-stage pending answers

Within any stage/step that gathers multiple answers before its own confirmation (`design/SKILL.md` Stages 1–6c,
`review/SKILL.md` step 4a), upsert `session.json`'s `pending` key after each individual answer the user gives, rather
than waiting for the whole stage to be confirmed:
`{ "stage": "<current stage/step id>", "answers": { ...whatever has been captured so far... }, "updatedAt": "..." }`.
Overwrite it wholesale on each update (it is scratch space for one in-progress stage, not a history). The moment the
stage is confirmed and its real key (e.g. `stage2`) is written, delete `pending` entirely in that same write — never
leave it pointing at a stage that has already been confirmed. On session resume, a present `pending` key means the
previous session died mid-stage: re-ask only the remaining questions for `pending.stage`, showing the user what was
already captured in `pending.answers` rather than re-asking from scratch.

**Special case — `pending.stage == "stage1"`**: Stage 1 is the one stage where checkpointing `pending` can happen
*before* `session.json` itself otherwise exists (`schemaVersion`/`project`/`description`/`stage1` are normally all
written together at Stage 1 confirmation — see `design/SKILL.md`'s "`description` is required"). A `pending`-only file
(holding nothing but `pending`, no `schemaVersion`/`project`/`description`/`stage1`) is valid and expected in this one
case — create `docs/architecture-designer/session.json` with just `{ "pending": {...} }` the first time Stage 1
checkpoints an answer, rather than waiting for full Stage 1 confirmation to create the file. The "Legacy-session
backfill check" (`design/SKILL.md`) must not fire against a `pending`-only file: that check exists to repair a v1 file
whose `stage1` content already exists but whose top-level fields don't — a file with no `stage1` key at all has nothing
to synthesize `description` from and is simply "Stage 1 not yet confirmed," not a legacy file to repair.

## Resuming Steps 6a–13 via `progress`

Once `session.json`'s stage1–stage5 are confirmed and the "Session completeness gate" above passes (this precondition
intentionally does **not** require stage6b/6c — `progress.lastCompletedStep` can already read `"step6a"` before either
of those is ever confirmed, since Stage 6a runs first), a resumed session must also check whether Stage 6a–Step 13 was
already in progress, rather than restarting the whole pipeline from Stage 6a:

1. If `pending` is present, resume that stage/step's remaining questions first (see "Mid-stage pending answers" above) —
   this can only apply to Stages 1–6c, since `pending` is not written past that point.
2. Read `progress`. If absent, start from Stage 6a — nothing past stage1–6c has run yet in this cycle. If present, check
   `progress.owner`: if it names the *other* skill (e.g. `design` resuming finds `owner: "review"`) and
   `progress.lastCompletedStep` is before `step11` (that other skill's pass never reached a document save — see
   "Recording `progress.lastCompletedStep`"'s label table for what `step11` means in each skill), this `progress`belongs
   to an interrupted run of the other skill, not this one: do not resume it as your own pipeline state. Tell the user an
   interrupted `{other skill}` session was found and that running `/architecture-designer:{other skill}` is how to
   resume it, then proceed with the stage6b/6c-presence-based resume already in place for Stages 6a–6c, ignoring
   `progress`/`lastCompletedStep`/`reviewCycles` entirely for this pass. Otherwise (owner matches, or`lastCompletedStep`
   is `step11` or later meaning the other skill's pass already completed and left a clean handoff), continue below.
3. For each `progress.reviewCycles.<type>` entry recorded at or before the resumed position: for `architecture`/
   `document`, recompute the relevant artifact's hash
   (`python3 <scripts_dir>/hash-file.py docs/architecture-designer/diagrams.json` for `architecture`, or against the
   document path for `document`) and compare it to the entry's stored `diagramsHash`/`documentHash`. A mismatch means
   the artifact changed after that verdict was recorded (a later fixer pass, a manual edit, or a regenerated diagram
   set) — treat that verdict as invalid and re-run that reviewer–fixer cycle (see "Reviewer–fixer cycle procedure")
   rather than trusting the stale `PASSED`. A match means the verdict still holds — skip re-running that reviewer and
   proceed past it. For `database`, there is no hash to check — `approvedOutput` holds the actual approved content
   directly (see "Persisting the database design output" below), so a present `database` entry with a `PASSED` verdict
   is always still valid; use `approvedOutput` directly wherever the database-designer/fixer's output would otherwise be
   needed (Stage 6d's ERD diagram, Step 11 section 7) instead of re-deriving it from conversation memory that may no
   longer exist.
4. If `docs/architecture-designer/last-review.md` exists and represents an unresolved cycle per that section's "Resuming
   an interrupted cycle", resume the fixer loop directly rather than re-spawning the reviewer.
5. Resume from the step immediately after `lastCompletedStep` (per the label table above), skipping any step whose work
   is confirmed still valid by steps 3–4. Brief the user on where the session picked back up (e.g., "The architecture
   review had already passed and the diagrams haven't changed since — skipping straight to the browser preview").
   **Stage 6b/6c fall outside this label table entirely** — they use the presence-based resume from step 2 above
   (`stage6b`/`stage6c` key present in `session.json` = already confirmed this pass), never a
   `progress.lastCompletedStep`
   value, since neither stage writes to `progress`. Do not look for a `step6b`/`step6c` label here; check key presence
   instead, per the "Session completeness gate" precondition note at the top of this section.

## No CAS — always read-fresh-modify-write-whole

`session.json` has no locking or compare-and-swap mechanism. Every writer must read the current file fresh immediately
before writing, merge its change into the full object, and write the whole file back — never write a partial object or
assume an in-memory copy from earlier in the conversation is still current. This is safe because these skills and agents
run sequentially within one conversation; do not parallelize two writers against the same `session.json` (e.g. do not
spawn `implementation-planner` for two documents concurrently).

**This is a usage invariant, not a mechanically enforced one**: nothing in this plugin detects or prevents two separate
Claude Code sessions running `/architecture-designer:design`/`review`/`implement` concurrently against the same
`docs/architecture-designer/` directory (e.g. two terminal tabs, or two team members, both invoking a skill against a
shared working copy). That scenario reintroduces the lost-update risk read-fresh-modify-write-whole is designed to avoid
within a single conversation. Avoid it operationally — do not run more than one architecture-designer skill against the
same project directory at a time.

## Session completeness gate

`design/SKILL.md` (Stage 6), `review/SKILL.md` (before Step 1), and `implement/SKILL.md` (before Step 1) each run
`python3 <scripts_dir>/validate-session.py` and show its output before proceeding, whenever
`docs/architecture-designer/session.json` exists. The script runs three checks, in order, printing`SESSION CHECK PASSED`
or `SESSION CHECK FAILED` at the end:

1. **Completeness** — the required top-level fields (`schemaVersion`, `project`, `description`) and confirmation stages
   1–5 are present and non-empty. "Non-empty" is checked recursively, not just by presence/length — a stage object whose
   only field is an empty string (e.g. `{"backend": ""}`) fails this check rather than passing as a non-empty dict.
2. **Structural schema** — every other key present (`updatedAt`, `agentTools`, `pending`, `progress`, `lld`,
   `testStrategy`, `documents`, `adrs`,
   `remediationPlans`, `implementationPlans`, `architecturalDrivers`, `riskRegister`, `domainModel`) is checked against
   `<scripts_dir>/session-schema.json`, a JSON Schema covering the fixed-shape parts of this file
   (array-of-objects-or-legacy-string entries, the `split` object, enums like `agentTools[].type`,
   `riskRegister[].category`/`.likelihood`/`.impact`/`.status`, `domainModel.relationships[].pattern`, and
   `adrs[].status` — and the required fields on `architecturalDrivers`/`riskRegister`/`domainModel`/`adrs` entries, e.g.
   every `architecturalDrivers` entry must carry `id` and `description`, and every `adrs` entry must carry `id`, `path`,
   `title`, and `status`). `stage1`–`stage5` (including `stage2.qualityAttributeScenarios`, `stage2.domainEdgeCases`,
   `stage5.tradeoffAnalysis`, and `stage5.costEstimate`), `web3`, `offlineFirst`, `stage6b`, `stage6c`, `testStrategy`
   stay untyped in that schema, since their inner field names are the user's own confirmed answers or agent-drafted
   prose and legitimately vary by project.
3. **Referential integrity** (advisory, printed but never fails the gate) — two independent checks:
   (a) link fields between `documents`/`remediationPlans`/`implementationPlans` (`document`, `remediationPlan`,
   `supersedes`, `split.previousPlan`/`split.nextPlan`) are checked for whether they resolve to a path present elsewhere
   in the file; (b) cross-references between the ADD/ATAM/DDD keys — `stage5.tradeoffAnalysis[].
   driversInTension`/`.relatedRisks`, `riskRegister[].relatedDriver`, `architecturalDrivers[].source` (when it starts
   with `QAS-`), and `domainModel.relationships[].from`/`.to` — are checked for whether the id/name they cite actually
   exists in `architecturalDrivers[]`/`riskRegister[]`/`stage2.qualityAttributeScenarios[]`/
   `domainModel.boundedContexts[]`; duplicate `id` values within any one of `architecturalDrivers`, `riskRegister`,
   `stage5.tradeoffAnalysis`, or `stage2.qualityAttributeScenarios` are also flagged. A mismatch is surfaced as a
   warning, not a failure, since some links are legitimately still pending at the moment the gate runs (e.g. a fresh
   `remediationPlans` entry's `document` field is written before the document itself, per `review/SKILL.md` step
   4e/4f) — this layer exists to surface possible drift for a human to look at, not to block on a timing artifact.

Only layers 1 and 2 affect the exit code and the `SESSION CHECK PASSED`/`FAILED` verdict.

**This is a hard gate in all three skills**: if the check fails, do not proceed past the gate. For a layer-1 failure,
tell the user which fields and/or stages are missing and ask them to complete them — resuming stages 1–5 in `design`, or
supplying the missing information directly so `session.json` can be updated. For a layer-2 failure, the file itself is
malformed (not merely incomplete) — read the specific violation the script printed and fix `session.json` directly (or
investigate which agent/skill wrote the bad shape, since this indicates a real bug rather than an in-progress session)
before continuing. Only proceed once the script reports `SESSION CHECK PASSED`.

Each skill's own trigger condition and rationale differ:

- **`design/SKILL.md`**: the gate always applies at Stage 6, since `design` is the skill that builds `session.json`
  through stages 1–5 in the first place — there is no "file doesn't exist" branch here. A missing top-level field on an
  otherwise-complete resumed session is the legacy-backfill case (Step 11), not a missing stage.
- **`review/SKILL.md` and `implement/SKILL.md`**: the gate applies only when `session.json` exists; if it does not exist
  at all, skip the gate entirely and proceed without session context, since both skills can still work from the
  architecture document (and, for `review`, the codebase) alone. A session that exists but is incomplete is treated more
  strictly than no session at all — an incomplete file signals the project started structured requirements tracking and
  abandoned it partway through, which is a stronger signal to pause and reconcile than never having used it. In
  `implement` specifically, neither skill step reads stage 1–5 data directly (Step 1 only reads the `documents` array
  for the document path); the gate exists to catch drift between the confirmed document and the requirements it was
  supposedly built from, not because implement's own logic consumes the stage fields.

## Proposed Additions rejection handling

`architecture-fixer` and `database-fixer` may return a fix log containing a **"Proposed Additions"** section — changes
the fixer recommends beyond what the review report strictly required. Present each item to the user for confirmation
before continuing: add confirmed items directly to `diagrams.json`; discard rejected ones.

**A rejected proposed addition does not resolve the finding that generated it.** Note which finding each rejected
addition was tied to — the fixer cannot close that finding without the addition. Ask the user directly: accept the
residual risk and note it in the document, or describe an alternative fix for the fixer to apply next cycle. Only
re-spawn the reviewer once the user has chosen one of these for every rejected addition.

This section applies whenever a fixer's log is checked for "Proposed Additions" — regardless of whether one is found.
Re-spawning the reviewer to verify the fixer's changes is a separate, unconditional step at every call site
(`design/SKILL.md` Step 7 and Stage 6a, `review/SKILL.md` step 4b and step 4c) — it happens whether or not a Proposed
Additions section was present, not only when one was.

## Merge-strategy question

When an existing project is found in the working directory and there is an architecture document to implement from, ask:

> "I found an existing project structure. How would you like to proceed?
> **(a) Merge** — add missing files from the architecture without overwriting existing code
> **(b) Fresh start** — generate the complete skeleton; any file that already exists will be flagged before being
> overwritten — you decide per collision
> **(c) Let me describe what to keep** — I'll describe my existing layout and we'll work around it"

Wait for the answer before proceeding. `design/SKILL.md` (Step 13), `review/SKILL.md` (step 4h), and
`implement/SKILL.md`
(Step 2) all ask this identical question before spawning `implementation-planner`, each by reading it from this section
rather than quoting their own copy — this section is the single source of truth for the question's exact wording; edit
it here only.

## Existing-project scan categories

Before asking the "Merge-strategy question" above, `design/SKILL.md` (Step 13), `review/SKILL.md` (step 4h), and
`implement/SKILL.md` (Step 2) each scan the working directory for signs of an existing project. All three use the same
four categories, so that scanning the same directory from any of the three skills reaches the same "empty vs. not empty"
conclusion:

- Dependency manifests: `package.json`, `go.mod`, `Cargo.toml`, `requirements.txt`, `pyproject.toml`, `pom.xml`
- Source directories: `src/`, `app/`, `lib/`, `cmd/`, `internal/`
- Configuration: `Dockerfile`, `docker-compose.yml`, `.env`, `.env.example`
- Test directories: `tests/`, `test/`, `spec/`, `__tests__/`

A project is "empty" only if none of the four categories finds anything. If any single category finds something, treat
it as "files already exist" and ask the Merge-strategy question above.

## Implementation task-group table

`implementation-planner` (Step 4, "Create implementation tasks") and `architecture-implementer` (Step 1, "Locate the
pre-created tasks") both need the identical file-group-to-task-title mapping — the planner creates one `TaskCreate` per
row below, and the implementer looks them up by the same titles via `TaskList`. Both agents use this exact table;
neither restates it independently:

| Task title                 | What it covers                                                                                                                                                                                      |
|----------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Run project scaffolding    | The official generator command from the plan's Scaffolding section, if present                                                                                                                      |
| Implement data models      | Model files, migration files, schema/ORM definitions                                                                                                                                                |
| Implement API routes       | Route handlers, controllers, middleware                                                                                                                                                             |
| Write configuration files  | package.json, .env.example, tsconfig, docker-compose, Dockerfile                                                                                                                                    |
| Write infrastructure files | Terraform, CDK, Kubernetes manifests, CI/CD pipeline configs                                                                                                                                        |
| Write setup scripts        | npm scripts, cross-platform setup and run commands                                                                                                                                                  |
| Write test files           | Unit test per data model, integration test per API route group, unit test per non-trivial business rule, mock test per external integration, plus any test helpers/utilities and fixtures/factories |
| Apply remediation changes  | Modifications to existing files per the remediation plan (only when a plan is provided)                                                                                                             |

`implementation-planner` omits any row with no files in the confirmed tree for the current project;
`architecture-implementer` only looks up rows that were actually created.

## Checking whether a remediation plan is fully resolved

A remediation plan (a `remediationPlans` entry) is fully resolved once every code change it lists has been applied. To
check: find the entry (or entries) in `implementationPlans` whose `remediationPlan` field equals the remediation plan's
`path`.

**If any matching entry carries a `split` object** (see "Resolving a split plan's parts" below): a remediation finding
can land in any part's "Modifications to existing files" section, not necessarily the part with the latest `createdAt` —
checking only one representative entry can miss a `[ ] FAIL` sitting in an earlier part. Resolve against **all** sibling
parts (same `split.total`, linked via `previousPlan`/`nextPlan`) collectively: resolved only if every part's `path`
exists on disk, every part's on-disk `Status` is `Complete`, and no part's "Modifications to existing files" section
contains a `[ ] FAIL` item.

**Otherwise** (no `split` object — the normal single-file case), take the one entry with the latest `createdAt` if more
than one matches. It is resolved if that implementation plan's `path` exists on disk, its on-disk `Status` is`Complete`,
and its "Modifications to existing files" section contains no `[ ] FAIL` items.

Two consumers apply this check for different purposes:

- `review/SKILL.md`'s pre-Step-1 load ("Check for an existing remediation plan"): if resolved, skip straight to the
  "fully complete" message without re-parsing the remediation plan's own checkboxes.
- `design/SKILL.md` (Step 13) and `implement/SKILL.md` (Step 3), before spawning `implementation-planner`: if resolved,
  do not pass the remediation plan path — there is nothing left to plan or implement.

## Pre-review remediation-plan carry-forward check

`review/SKILL.md` runs this check before Step 1, whenever `session.json` contains a `"remediationPlans"` array.

Scan **every** entry (not just the last one — entries are objects, or legacy bare-string paths in older files; see
"Legacy (schema v1) tolerant read" above), skipping any whose `path` no longer exists on disk and any whose on-disk
`Status` already reads `Superseded by ...` (already closed out per "Superseding a remediation plan" below, so not
re-offered). Checking only the latest entry would miss an older plan whose deferred items the user previously declined
to carry forward — that plan is left un-superseded on purpose and must keep surfacing on every future scan, the same
reasoning "Orphaned plans from a prior document revision" below applies to scanning all matching entries rather than
assuming the latest is the only one relevant.

For each remaining entry:

- **Cross-check against the implementation plan first**: apply "Checking whether a remediation plan is fully resolved"
  above. If resolved, treat this entry as fully complete without re-parsing its own checkboxes. Otherwise, inspect the
  remediation plan file directly.
- **If an entry has `[ ]` (deferred) items**: surface it before Step 1 (one prompt per entry with deferred items, if
  more than one). **At most one entry can be carried forward and superseded per review session** — each new
  `remediationPlans` entry has a single `supersedes` path, so only the one plan named there gets closed out when step 4e
  saves; a second "yes" in the same session would have no `supersedes` slot to record it in, and that plan would
  incorrectly keep surfacing as un-superseded forever. So: prompt about the most recent entry with deferred items first:
  > "I found a previous remediation plan at `{path}` with **{N} deferred item (s)** not yet addressed. Here they are:
  > {list of [ ] items}
  > Would you like to include these in this review session?"
  If yes: carry the deferred items forward into step 4a (revision scope) so they can be addressed or remain deferred,
  and remember this plan's path as the one step 4e's new plan will supersede. If no: proceed without carrying this
  plan's items forward — do not mark it `Superseded`; its deferred items remain outstanding and this same scan surfaces
  it again on the next review session. If any other, older entries also have deferred items: note them to the user for
  awareness (path and count only) but do not offer to carry them forward in this same session — each can only be picked
  up as the single carried-forward plan in a future review session, one at a time.
- **If zero entries remain after filtering** (nothing matched, or every match was already superseded/missing from disk):
  proceed to Step 1 without comment.
- **If every remaining entry is either fully resolved or has every item `[x] *(code aligned)*`** (nothing deferred
  anywhere): note it briefly to the user — "Previous remediation plan (s) are fully complete — all findings have been
  code-aligned. Starting fresh review." — then continue to Step 1.

## Finding the applicable remediation plan

Before spawning `implementation-planner`, `design/SKILL.md` (Step 13) and `implement/SKILL.md` (Step 3) both need to
know whether an unresolved remediation plan applies to the document being implemented. Both use the same lookup: in
`session.json`'s `remediationPlans` array, find the entry whose `document` field equals the confirmed architecture
document's path. If found and its `path` still exists on disk, it is the remediation plan to pass along — unless section
"Checking whether a remediation plan is fully resolved" above rules it out (a fully resolved plan is never passed).

A remediation plan's mere presence does not by itself prove an existing codebase. When translating the existing-project
scan into the strategy label passed to `implementation-planner`, trust the scan (section "Existing-project scan
categories" above), not whether a remediation plan happens to exist — a remediation plan can exist for a project that
was never actually built.

## Superseding a remediation plan

`remediationPlans` entries carry a `supersedes` field (mirroring `implementationPlans`), used when `review/SKILL.md`'s
pre-Step-1 check offers to carry a previous plan's deferred `[ ]` items forward (see "Check for an existing remediation
plan" in that skill) and the user accepts. The old plan file is never edited in place to add or resolve findings —
remediation plans follow the same "new file each revision" convention as architecture documents (`review/SKILL.md` step
4e always writes a fresh, collision-suffixed file, never overwriting). Instead, once the new plan is saved in step 4e:

- Set the new entry's `supersedes` field to the old plan's `path`.
- Make one terminal write to the *old* plan file — change its `Status` row to `Superseded by {new plan path}` — the same
  pattern `implementation-planner` uses for `implementationPlans` (see "Resolving links between arrays" above).

This is what closes out an old plan whose deferred items were folded into a new one. A plan whose deferred items the
user declined to carry forward is left untouched and is simply re-offered on the next review session's pre-Step-1 check.

## Requirements-summary scope for sub-agent spawns

Ten call sites assemble a "requirements summary" to pass into a spawned sub-agent: `design/SKILL.md` Stage 6a
(`database-designer` + `database-reviewer`), Step 7 (`architecture-reviewer`), and Step 12 (`document-reviewer`);
`review/SKILL.md` Step 2a (`architecture-reviewer`), step 4b (`database-designer` + `database-reviewer`), step 4c
(`architecture-reviewer`), and step 4g (`document-reviewer`); and `architecture-fixer`/`database-fixer`/`document-fixer`
's own "What you receive" input — the last three are spawned via the shared "Reviewer–fixer cycle procedure" below
rather than a uniquely-numbered step, reusing the requirements summary already assembled for their paired reviewer's
spawn immediately above, but still subject to the same scope rule via their own agent file's documented inputs. All ten
use the same scope rule: read every relevant top-level `session.json` key, not stage1–5 alone — stage1–5 (including
`stage2.domainEdgeCases`, `stage5.tradeoffAnalysis`, and `stage5.costEstimate`) and the top-level `description` always,
plus `agentTools`, `stage6b`, `stage6c`, `web3`, `offlineFirst`, `architecturalDrivers`, `riskRegister`, `domainModel`,
`testStrategy`, and `adrs` whenever present.

This matters most for `web3` and `offlineFirst`: a receiving agent's Web3-specific or offline-sync-specific dimension or
check can only fire if that key was actually included in what it received. Omitting it because "the caller only read
stages 1–5" produces a false "not applicable" from the receiving agent, not an honest evaluation — the agent has no way
to distinguish "this project isn't decentralized/offline-first" from "the caller didn't pass me the key that would tell
me so." The same reasoning applies to `stage6b`/`stage6c` for IaC/CI-CD-aware checks, `agentTools` for any check that
reasons about available tooling, `domainModel` for aggregate-boundary-aware schema checks, `architecturalDrivers`/
`riskRegister` for driver-traceability and risk-cross-check findings, and `testStrategy`/`adrs` for `document-reviewer`/
`document-fixer`'s C17–C19 checks (Step 12/step 4g) — the same false-"not applicable" risk applies if either is omitted
from what those two agents receive. `architecturalDrivers`, `riskRegister`, `domainModel`, `testStrategy`, and `adrs`
are "whenever present" rather than "always" because a resumed session that confirmed Stage 5, Stage 6a, or Step 10b
before these keys existed in this plugin's schema will legitimately lack them — the same reason `stage6b`/`stage6c`
are "whenever present" rather than "always."

Each call site's own text still states any call-specific detail beyond this shared rule — e.g. "so the reviewer's Web3
dimension can actually fire on this first pass," or the fallback to the previous document's Requirements Summary section
when `session.json` is absent — this section exists so the scope rule itself (the fixed key list, and why it's not just
stage1–5) is defined once rather than restated at all eight sites that apply it.

## Reviewer–fixer cycle procedure

Six call sites across `design/SKILL.md` and `review/SKILL.md` spawn a reviewer agent (`architecture-reviewer`,
`database-reviewer`, or `document-reviewer`), plus one additional call site — the "Implementation reviewer–fixer cycle"
section below, itself reached from step 5 of "Implementation-planner → architecture-implementer spawn sequence" (which
runs regardless of whether the plan was split — "Split-plan implementation loop" only covers the split case, spawning
`architecture-implementer` per part, before control returns to that step 5) and so exercised from all three of
`design/SKILL.md` Step 13, `review/SKILL.md` step 4h, and `implement/SKILL.md` Step 4 — spawns `implementation-reviewer`
once per completed implementation run. **Recording step 0 below is unconditional — run it every time any call site
receives a report back from a reviewer, regardless of verdict.** Only steps 1–4 (the fixer cycle itself) are conditional
on a failing verdict. A call site's own text (e.g. "If it returns `DATABASE REVIEW FAILED`, follow this section")
describes when steps 1–4 apply, never step 0 — do not read a call site's failure-gated phrasing as gating step 0 as
well; a clean first-try pass still runs step 0 once, then stops.

0. **(Unconditional — every time a reviewer returns a report, passing or not)** Overwrite
   `docs/architecture-designer/last-review.md` with: which reviewer produced it (`database-reviewer` /
   `architecture-reviewer` / `document-reviewer`), the cycle number this is (1 on first spawn, incrementing each time
   step 3 below re-spawns), the literal verdict string, and the full findings list verbatim. This file always holds only
   the *currently unresolved* cycle's report — overwrite it, never append — so a session that dies mid-cycle can resume
   the fixer loop from disk instead of re-spawning the reviewer from scratch. Once the exit condition below is actually
   met (verdict passed), the file becomes stale/ignorable — no need to delete it, the next cycle's first spawn
   overwrites it.

   Also write this same information into `session.json`'s `progress.reviewCycles.<type>` (`database`/`architecture`/
   `document`/`implementation`) — `verdict`, `cycleCount`, and `updatedAt`, always. For `architecture` and `document`
   specifically, also record a hash of the artifact this cycle just reviewed (`diagramsHash` = sha256 of
   `docs/architecture-designer/diagrams.json` for `architecture`, computed via
   `python3 <scripts_dir>/hash-file.py docs/architecture-designer/diagrams.json`; `documentHash` = same script against
   the document path, for `document`) — used on resume to detect whether that artifact changed since this verdict (see
   "Resuming Steps 6a–13 via `progress`" below). **`database` never records a hash** — see "Persisting the database
   design output" below for why its entry looks different. **`implementation` never records a hash either** — the
   artifact under review is the codebase on disk, not one file; instead its entry records `reviewedPlans` (the ordered
   list of plan path (s) this cycle checked), which is enough to identify what was reviewed without needing a stored
   value to detect drift against, since a resumed session re-running this cycle simply re-reviews the current plan state
   directly.

   Do this on every iteration, passing or not, so a mid-cycle death shows the true last-known cycle count rather than a
   stale earlier one. Before the *first* spawn of a brand-new cycle for a given type (as opposed to a re-spawn within an
   already-running cycle), clear any stale prior entry at `progress.reviewCycles.<type>` first — it belongs to a
   superseded pipeline run, and leaving it in place risks a resumed session trusting an old verdict against a new
   artifact.
1. Spawn the fixer with the review report, the artifact being corrected (`diagrams.json` path, or the document path for
   `document-fixer`), and the requirements summary. **For `implementation`, the input list is different** — see
   "Implementation reviewer–fixer cycle" above: `implementation-fixer` takes the review report, the plan path (s), the
   architecture document path, technology stack, and `agentTools`, not a requirements summary or a single "artifact"
   path (the artifact is the whole generated codebase, not one file).
2. After the fixer applies its correction, apply section "Proposed Additions rejection handling" above if the fixer's
   log contains that section.
3. Re-spawn the reviewer to verify. Read the verdict line itself — do not re-derive pass/fail from the findings list.
   Repeat step 0 above for this new report (increment the cycle number).
4. Repeat from step 1 until the exit condition below is met, **up to a maximum of 3 reviewer–fixer cycles**. If it is
   not met after 3 cycles, stop, present the remaining findings verbatim, and ask the user for guidance rather than
   cycling further.

**Exit condition — read the reviewer's literal verdict string; the two verdict vocabularies are not interchangeable:**

- **Binary reviewers** (`database-reviewer`, `document-reviewer`, `implementation-reviewer`): stop once the verdict
  reads `DATABASE REVIEW PASSED` / `DOCUMENT REVIEW PASSED` / `IMPLEMENTATION REVIEW PASSED`. Any `FAILED` verdict means
  cycle again.
- **Three-tier reviewer** (`architecture-reviewer`): stop once the verdict reads `REVIEW PASSED`.
  `REVIEW CONDITIONALLY PASSED` is emitted *specifically because* Major findings remain — by the reviewer's own verdict
  definitions, it can never mean "all Major items resolved." Treat `REVIEW CONDITIONALLY PASSED` as a stop condition
  only once every remaining Major finding has been through step 2 above (the user explicitly accepted the residual risk
  or provided an alternative fix for each) — otherwise keep cycling. `REVIEW FAILED` (Critical present) always means
  cycle again.

Do not open the browser preview, or proceed past the calling step, until this exit condition is met.

**Persisting the database design output**: unlike `architecture`/`document`, the `database` type is not reviewing a file
that already exists on disk at the time it runs — Stage 6a happens before `diagrams.json` even has its skeleton (written
in Stage 6d) and before any document exists. Hashing an external file would either fail (file absent) or, once
`diagrams.json` does exist later, drift out of sync every time an unrelated diagram is added or edited (falsely
invalidating a database verdict that never changed). So instead of a hash, step 0 for `database` writes the actual
approved content directly into `progress.reviewCycles.database.approvedOutput` — the full corrected schema, ERD, index
plan, engine recommendation, transaction and concurrency strategy, and connection config text (the fixer's corrected
version if any cycle ran, otherwise the database-designer's original output; same "final approved version" rule the
calling step already states). This makes the design's own content, not a derived hash, the thing that's durable — a
crash between Stage 6a passing and Stage 6d's ERD-diagram write does not lose the database design, and there is nothing
external to go stale against. Stage 6d reads
`progress.reviewCycles.database.approvedOutput` from `session.json` to build the ERD diagram, rather than relying on
conversation memory only. **Step 11 does not read `approvedOutput` for the ERD itself** — per `design/SKILL.md` Step
11's own instruction, the `erDiagram` block in document section 8 is copied verbatim from Stage 6d's already-written
`diagrams.json` entry, so the diagram is derived from `approvedOutput` exactly once, not independently at both points
(see `design/SKILL.md` Step 11 and `review/SKILL.md` 4f). Step 11 still reads `approvedOutput` directly for section 8's
surrounding prose — the schema, index table, connection config, and migration strategy, which have no `diagrams.json`
equivalent to copy from.

**Resuming an interrupted cycle**: if `docs/architecture-designer/last-review.md` exists and its recorded
`{reviewer, cycleCount}` has no matching *passed* entry in `session.json`'s `progress.reviewCycles.<type>` (i.e. the
last thing on disk is an unresolved cycle, not a verdict that already passed), treat the cycle as still open on resume:
re-spawn the matching fixer directly with the saved report from step 1 above rather than re-spawning the reviewer from
scratch to regenerate a report you already have.

## Resumable-plan detection procedure

Three call sites spawn `architecture-designer:implementation-planner` — `design/SKILL.md` (Step 13), `review/SKILL.md`
(step 4h), and `implement/SKILL.md` (Step 3). Immediately before spawning, all three run this same procedure against the
confirmed architecture document's path (called `{document}` below) to decide whether to offer resuming a previous plan:

**Required first check — a stuck fixer, not a stuck plan**: before scanning `implementationPlans` below, check whether
`docs/architecture-designer/last-review.md` shows an unresolved `implementation`-type cycle (its recorded `{reviewer,
cycleCount}` has no matching *passed* entry in `progress.reviewCycles.implementation` — same test "Reviewer–fixer cycle
procedure"'s own "Resuming an interrupted cycle" uses) **and** the plan file it names reads `Status: In progress`. If
both hold, this is not a plan that needs (re-)planning — it's an `implementation-fixer` run that died mid-fix before
flipping `Status` back to `Complete` (see `agents/implementation-fixer.md`'s "Resuming, checkpointing, and the Status
re-arm"). Re-spawn `implementation-fixer` directly against that same report to resume it (it detects the resume itself
from the plan's `Status` and `last-review.md`'s per-item checkpoints) — **do not** proceed to this procedure's own scan
below or offer a **Previous plan path** to `implementation-planner`; that would misroute a stuck fix into a fresh
re-plan. Skip this check entirely if `last-review.md` doesn't exist, names a different type, or its cycle already
passed — proceed to the scan below as normal.

Scan `implementationPlans` for entries whose `document` field equals `{document}`. Keep only entries whose `path` still
exists on disk and whose plan is actionable — read the plan's metadata table `Status` line: actionable means `Status` is
`In progress`, OR `Status` is `Complete` but the plan's checklist contains at least one `[ ] FAIL` item anywhere (not
just under "Modifications to existing files"). Do not filter on `Status == In progress` alone —
`architecture-implementer` always sets `Status` to `Complete` at the end of a run even when files failed (see its
Verification and output step), so `Complete`-with-`FAIL` plans are the common resumable case, not an edge case.

This is a lookup against `session.json` only — no need to open every candidate plan file to check its `document`/
`Status`, since schema v2 already carries `document` and `createdAt` on each entry. Only the single winning candidate
needs to be opened.

If more than one entry matches, check whether any carry a `split` object (see "Resolving a split plan's parts" below):if
so, select the one with the **lowest** `split.part` among the actionable entries, not the latest `createdAt`. All parts
of a split plan are saved in the same batch with `createdAt` increasing by part number (per implementation-planner's
"Save all {N} files in this step"), so the part saved *last* is the *last* one that needs implementing — the opposite of
what a latest-`createdAt` tie-break would select. Parts must be resumed in sequence, so the lowest-numbered
still-actionable part is always the correct resume point. If no matching entry carries a `split`object (the normal
single-file case, or the resume/supersede chain where only the newest revision should ever be actionable), fall back to
the latest `createdAt`.

If a match remains, read only that one plan file and count its checklist items: `[x]`/`[~]` done, remaining `[ ]`, and
`[ ] FAIL` failed. Then offer:

> "There's a previous plan for this document that isn't finished ({N} of {M} files done, {X}
> failed)[, part {split.part} of {split.total}, if the plan was split]. Continue from that plan, or start a new plan
> from
> scratch?"

If the user chooses to continue, pass the plan's `path` to `implementation-planner` as **Previous plan path**. If they
choose fresh, or no matching plan is found, proceed without it.

### Orphaned plans from a prior document revision

The procedure above only matches `implementationPlans` entries whose `document` field equals the *current* document's
path. If the architecture document was revised (a new `documents` entry was appended for the same topic, per
`review/SKILL.md` step 4f), an actionable plan still pointing at the prior revision's path will never match again — it
would otherwise sit `In progress` (or `Complete` with `[ ] FAIL`) forever with no resume offer and no way to close it
out.

To catch this, after running the procedure above, also scan `implementationPlans` for actionable entries (same
actionability test as above) whose `document` field's `{topic}` slug matches the current document's `{topic}` slug but
whose path differs from the current document's path — i.e. plans tied to an earlier revision of the same architecture.
If any are found, surface them separately from the resumable-plan offer:

> "Found {N} unfinished plan (s) for an earlier revision of this document (`{old document path}`). They won't be
> auto-resumed since the document has changed since then. Mark {them/it} as superseded by this revision, or leave as-is
> to
> review manually later?"

If the user confirms marking them superseded: for each one, make the same terminal write `implementation-planner` makes
when resuming (see "Resolving links between arrays" above) — change the old plan file's `Status` row to
`Superseded by document revision {new document path}` — but make this write directly (a plain file edit by the calling
skill), since no new plan is being created and `implementation-planner` is not being spawned for this. Do not touch any
other part of the old plan file.

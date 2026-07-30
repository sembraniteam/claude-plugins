# Agent Tools Selection Guide

Guidance for the optional `agentTools` addendum to Stage 5 — identifying which MCP servers, Skills, or Plugins already
available in the current Claude Code environment would help an agent implement, provision, or verify the chosen
technology stack, and recording them in `session.json` so every downstream sub-agent that receives it — not just
`implementation-planner` and `architecture-implementer` — knows what's available for the rest of this project's
lifetime, from design-time review through implementation. See "How downstream consumers use it" below for the current
full list.

## Core rule: availability, not aspiration

Only ever record a tool that is actually connected or installed in the current session — visible in the assistant's own
MCP tool listing or installed-skills listing at the time Stage 5 runs. Never write down a plausible-sounding MCP or
plugin name from general knowledge; an agent spawned later has no way to use a tool that isn't there, and a fabricated
entry silently breaks the implementation flow. If nothing in the current environment matches the chosen stack, that is a
normal, expected outcome — leave `agentTools` an empty array (or omit the key) and say so; do not force a
recommendation.

## When to run this check

Run it once, at the end of Stage 5, immediately after the eleven technology recommendations are confirmed and before
moving to Stage 6. The stack is fixed at that point, so tool matching has something concrete to match against; running
it earlier (before backend/database/infra are chosen) or deferring it to Step 13 (implementation offer, potentially days
later in a resumed session) both risk matching against a stale or incomplete stack.

## Procedure

1. List the MCP servers connected in the current session and the plugin Skills currently installed (both are visible in
   this environment's own tool/skill metadata — do not guess).
2. Cross-reference each confirmed Stage 5 choice (language/framework, database, cloud provider, auth approach,
   observability, and any domain named in Stage 1–2 such as payments or blockchain) against the category table below.
3. For every match found among tools actually available, draft one `agentTools` entry:
   `{ "name": "<exact tool or skill identifier>", "type": "mcp" | "skill", "purpose": "<one line: what it helps with for this project>" }`.
   A Claude Code plugin's user-facing capability is invoked as a Skill (or, if it bundles one, an MCP server) — record
   it with the type matching how it's actually invoked, not a separate `"plugin"` type.
4. Present the drafted list to the user alongside the rest of the Stage 5 summary: "These agent tools are available in
   this environment and match your stack — include them so implementation can use them later?" Let the user drop any
   entry.
5. Write the confirmed array to `session.json` under `"agentTools"` at the same time as the rest of Stage 5 (see
   `references/session-schema.md`).

## Category → tool mapping

This table names the kinds of MCP/Skill integrations that commonly exist in a Claude Code environment for a given
technology domain — treat it as a lookup of *what to search for*, not a guarantee any of it is installed. Confirm actual
availability per the core rule above before recording anything.

| Stack element (Stage 5)                                        | Look for an MCP/Skill named for…                                                                                                                   | Typical `purpose` when matched                                                                                                                         |
|----------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------|
| Go backend                                                     | a Go language-server MCP (e.g. `gopls`)                                                                                                            | Diagnostics, symbol search/rename, and vulnerability scanning on generated Go files                                                                    |
| Rust backend                                                   | a Rust language-server MCP (e.g. `rust-analyzer`)                                                                                                  | Diagnostics, symbol search/rename, and compile-error checking on generated Rust files                                                                  |
| Dart / Flutter frontend or mobile                              | a Dart/Flutter MCP (e.g. `dart-mcp-server`)                                                                                                        | Package/dependency exploration, hot reload/restart, and widget/runtime error inspection                                                                |
| Firebase (auth, Firestore, hosting, Cloud Functions)           | a Firebase MCP                                                                                                                                     | Provisioning the Firebase project/app, security rules, and SDK config during implementation                                                            |
| Stellar (blockchain / on-chain payments)                       | a Stellar-ecosystem plugin (skills for smart contracts, dApps, chain data, payments)                                                               | Contract, dApp, or agentic-payment implementation guidance specific to Stellar                                                                         |
| Any other target network on a Web3 stack (see `web3-guide.md`) | an MCP/plugin named for that specific network (e.g. an Ethereum or Solana toolkit) — same "search for it, never assume it" rule as the Stellar row | Whatever that network-specific tool's own capabilities cover                                                                                           |
| Auth, PII handling, compliance-sensitive systems               | a security-audit plugin (dependency/code vulnerability scanning skills)                                                                            | Post-implementation scan of generated auth/credential-handling code before it ships                                                                    |
| High-TPS or latency-sensitive systems (Stage 4)                | a performance-analysis plugin                                                                                                                      | Profiling guidance once the generated skeleton is running                                                                                              |
| Release/versioning process named in Stage 3                    | a changelog/release-notes plugin                                                                                                                   | Generating an initial `CHANGELOG.md` "Unreleased" entry for the implemented skeleton                                                                   |
| Git branching/commit conventions                               | a git-workflow helper plugin                                                                                                                       | Determining the branch name and first-commit message to suggest in the implementation summary (never auto-created — see `architecture-implementer.md`) |
| Any other named external service (Stage 5)                     | a matching vendor MCP, if one is connected                                                                                                         | Whatever that MCP's own tools cover for provisioning or querying that service                                                                          |

If a stack element has no match in the current environment (the common case for most SQL/NoSQL databases, most cloud IaC
providers, and most frontend frameworks — few of these have a dedicated MCP in a typical setup), simply do not produce
an entry for it. A short or empty `agentTools` list is normal.

**Most of this table's `purpose` column is implementation-phase** (diagnostics on generated files, provisioning during
implementation, a post-implementation scan). A few entries are also live-lookup tools usable during design-time review
or fixing, not just implementation — most notably the Web3-network row: a network-specific MCP/plugin can verify whether
a claimed contract address or chain identifier is real at review time, not only once code exists. Don't assume every
entry is implementation-only just because most of this table's phrasing is — check whether an entry's actual capability
(not just its listed `purpose` string) applies to the design-time task at hand.

## How downstream consumers use it

Every sub-agent spawned from `design/SKILL.md` or `review/SKILL.md` receives `agentTools` whenever it's non-empty, per
`references/session-schema.md`'s "Requirements-summary scope for sub-agent spawns". What each does with it differs:

**Must invoke a matching entry, not just receive it:**

- `architecture-implementer` — where a listed tool's domain matches a file, step, or process it is about to perform
  (e.g. a Go diagnostics MCP while writing `.go` files, a Firebase MCP while wiring up Firebase config, a changelog
  plugin when a release process was named), **must invoke it** for that step rather than merely preferring it over a
  generic `Read`/`Bash` approach — verifying correctness, provisioning a resource, or generating the artifact it exists
  for, rather than only stubbing a placeholder. See its "Using agent tools" and "Agent-tools usage log" sections.
- `database-designer` — when a matched tool's domain fits the recommended engine/platform, must use it to verify the
  engine's actual capabilities before finalizing the recommendation (its "Using agent tools" step).
- `database-fixer` and `architecture-fixer` — when a matched tool's domain fits the specific finding being corrected,
  must use it to verify the corrected value before writing the fix, rather than trusting memory (each agent's own
  "Using agent tools" section).
- `database-reviewer` — its whole purpose is independent verification, so an available matching tool must be used to
  check at least one claim in the design being reviewed, not just noted (its dimension 9).
- `architecture-reviewer` — not a blanket obligation like the others, since most of this guide's `purpose` column is
  implementation-phase and this agent runs pre-implementation; but a matched Web3-network entry is a live-lookup
  exception and must be used to verify a suspicious network fact (its dimension 7's fabrication check).

**Receives it for context/completeness, no invocation obligation:**

- `implementation-planner` surfaces it in the plan's metadata so a human skimming the plan knows what's available — it
  does not change the folder structure or checklist itself.
- `document-reviewer` and `document-fixer` receive it per the scope rule above, but since architecture-level review and
  fixing already runs upstream of document review, and this guide's `purpose` column is implementation-phase, neither
  currently has a matching design-time action to perform with it.

## Evidentiary reporting convention (USED / NOT APPLICABLE / UNAVAILABLE)

Every agent listed above under "must invoke a matching entry" (`architecture-implementer`, `database-designer`,
`database-fixer`, `architecture-fixer`, `database-reviewer`, and `architecture-reviewer` for its Web3-network
exception) reports the outcome of that obligation using this same three-value convention in its own output — each
agent's "Using agent tools" section (or, for `architecture-implementer`, its "Agent-tools usage log" section) points
back here rather than redefining it:

- **USED** — a matching `agentTools` entry existed and was actually invoked; quote the actual tool output (or a
  representative excerpt of it) as evidence, not just a restated claim that it was called.
- **NOT APPLICABLE** — `agentTools` was non-empty, but no entry's domain matched the specific fact, engine, finding,
  or step at hand; state briefly why nothing matched.
- **UNAVAILABLE** — a plausible domain match exists in principle, but `agentTools` was empty, absent, or contained no
  entry of that domain; state that no matching tool was available to invoke.

Do not report an outcome at all for a step where none of the three applies (e.g. a fix with no `agentTools` entry
whose domain is relevant, and no reasonable expectation one should exist) — omit the line entirely rather than
padding the output with an empty note.

This field is entirely optional end to end: an empty or absent `agentTools` never blocks Stage 6, document approval, or
implementation — it is a convenience, not a gate. Once a non-empty entry matches something a "must invoke" consumer
above is actually doing, though, using it for that match is mandatory, not optional — see each linked section for the
exact requirement.

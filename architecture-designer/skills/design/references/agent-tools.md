# Agent Tools Selection Guide

Guidance for the optional `agentTools` addendum to Stage 5 — identifying which MCP servers, Skills, or Plugins already available in the current Claude Code environment would help an agent implement, provision, or verify the chosen technology stack, and recording them in `session.json` so `implementation-planner` and `architecture-implementer` know to use them later in the same project's lifetime.

## Core rule: availability, not aspiration

Only ever record a tool that is actually connected or installed in the current session — visible in the assistant's own MCP tool listing or installed-skills listing at the time Stage 5 runs. Never write down a plausible-sounding MCP or plugin name from general knowledge; an agent spawned later has no way to use a tool that isn't there, and a fabricated entry silently breaks the implementation flow. If nothing in the current environment matches the chosen stack, that is a normal, expected outcome — leave `agentTools` an empty array (or omit the key) and say so; do not force a recommendation.

## When to run this check

Run it once, at the end of Stage 5, immediately after the nine technology recommendations are confirmed and before moving to Stage 6. The stack is fixed at that point, so tool matching has something concrete to match against; running it earlier (before backend/database/infra are chosen) or deferring it to Step 13 (implementation offer, potentially days later in a resumed session) both risk matching against a stale or incomplete stack.

## Procedure

1. List the MCP servers connected in the current session and the plugin Skills currently installed (both are visible in this environment's own tool/skill metadata — do not guess).
2. Cross-reference each confirmed Stage 5 choice (language/framework, database, cloud provider, auth approach, observability, and any domain named in Stage 1–2 such as payments or blockchain) against the category table below.
3. For every match found among tools actually available, draft one `agentTools` entry: `{ "name": "<exact tool or skill identifier>", "type": "mcp" | "skill" | "plugin", "purpose": "<one line: what it helps with for this project>" }`.
4. Present the drafted list to the user alongside the rest of the Stage 5 summary: "These agent tools are available in this environment and match your stack — include them so implementation can use them later?" Let the user drop any entry.
5. Write the confirmed array to `session.json` under `"agentTools"` at the same time as the rest of Stage 5 (see `references/session-schema.md`).

## Category → tool mapping

This table names the kinds of MCP/Skill integrations that commonly exist in a Claude Code environment for a given technology domain — treat it as a lookup of *what to search for*, not a guarantee any of it is installed. Confirm actual availability per the core rule above before recording anything.

| Stack element (Stage 5)                                        | Look for an MCP/Skill named for…                                                                                                                   | Typical `purpose` when matched                                                              |
|----------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------|
| Go backend                                                     | a Go language-server MCP (e.g. `gopls`)                                                                                                            | Diagnostics, symbol search/rename, and vulnerability scanning on generated Go files         |
| Dart / Flutter frontend or mobile                              | a Dart/Flutter MCP (e.g. `dart-mcp-server`)                                                                                                        | Package/dependency exploration, hot reload/restart, and widget/runtime error inspection     |
| Firebase (auth, Firestore, hosting, Cloud Functions)           | a Firebase MCP                                                                                                                                     | Provisioning the Firebase project/app, security rules, and SDK config during implementation |
| Stellar (blockchain / on-chain payments)                       | a Stellar-ecosystem plugin (skills for smart contracts, dApps, chain data, payments)                                                               | Contract, dApp, or agentic-payment implementation guidance specific to Stellar              |
| Any other target network on a Web3 stack (see `web3-guide.md`) | an MCP/plugin named for that specific network (e.g. an Ethereum or Solana toolkit) — same "search for it, never assume it" rule as the Stellar row | Whatever that network-specific tool's own capabilities cover                                |
| Auth, PII handling, compliance-sensitive systems               | a security-audit plugin (dependency/code vulnerability scanning skills)                                                                            | Post-implementation scan of generated auth/credential-handling code before it ships         |
| High-TPS or latency-sensitive systems (Stage 4)                | a performance-analysis plugin                                                                                                                      | Profiling guidance once the generated skeleton is running                                   |
| Release/versioning process named in Stage 3                    | a changelog/release-notes plugin                                                                                                                   | Generating changelog or store release notes for the implemented project                     |
| Git branching/commit conventions                               | a git-workflow helper plugin                                                                                                                       | Consistent branch and commit naming for the generated skeleton                              |
| Any other named external service (Stage 5)                     | a matching vendor MCP, if one is connected                                                                                                         | Whatever that MCP's own tools cover for provisioning or querying that service               |

If a stack element has no match in the current environment (the common case for most SQL/NoSQL databases, most cloud IaC providers, and most frontend frameworks — few of these have a dedicated MCP in a typical setup), simply do not produce an entry for it. A short or empty `agentTools` list is normal.

## How downstream consumers use it

- `implementation-planner` receives `agentTools` as an optional input and surfaces it in the plan so a human skimming the plan file knows what's available — it does not change the folder structure or checklist itself.
- `architecture-implementer` receives the same list and, where a listed tool's domain matches a file it is about to write or verify (e.g. a Go diagnostics MCP while writing `.go` files, a Firebase MCP while wiring up Firebase config), prefers it over a generic `Read`/`Bash` approach for that step — using it to verify correctness (diagnostics, vulnerability checks) or to actually provision a resource (project/app creation) rather than only stubbing a placeholder.

This field is entirely optional end to end: an empty or absent `agentTools` never blocks Stage 6, document approval, or implementation — it is a convenience, not a gate.

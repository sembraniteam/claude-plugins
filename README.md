# sembraniteam-claude-plugins

A collection of [Claude Code](https://claude.ai/code) plugins for automating git workflows, release documentation, debugging, software architecture design, performance investigation, and security auditing.

## Plugins

### [architecture-designer](./architecture-designer)

Guided architecture and infrastructure design workflow — from requirements gathering to code implementation — with interactive Mermaid diagrams, browser preview, and structured documentation.

| Component                          | Description                                                                                                                                                                                                                                                                                                                                                                             |
|------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `/architecture-designer:design`    | Six-stage interactive session — requirements → analysis → feasibility → capacity → technology → architecture (DB · IaC · CI/CD · diagrams) — followed by review, preview, and LLD steps; generates Mermaid diagrams, browser preview, IaC module plan, CI/CD pipeline design, API contracts, business rules, error catalog, versioned architecture document, and optional code scaffold |
| `/architecture-designer:review`    | Review existing architecture from document, codebase, or both; detect design-vs-implementation drift, apply revisions, and save a new versioned document                                                                                                                                                                                                                                |
| `/architecture-designer:implement` | Turn an approved architecture document into a working project skeleton; detects existing project structure, proposes folder layout for confirmation, then generates models, routes, config, and infrastructure files                                                                                                                                                                    |
| `architecture-reviewer` agent      | Evaluates technical correctness across diagrams, alignment with requirements, and risks (SPOF, bottlenecks, security gaps, observability, DR); returns Critical / Major / Minor findings with a REVIEW PASSED / CONDITIONALLY PASSED / FAILED verdict                                                                                                                                   |
| `architecture-fixer` agent         | Applies targeted fixes to Mermaid diagrams based on architecture-reviewer findings; updates `diagrams.json` in place and returns a fix log                                                                                                                                                                                                                                              |
| `database-designer` agent          | Designs the full data layer: engine selection, normalized schema, ERD, index plan, and secure connection configuration; output is incorporated directly into the architecture document                                                                                                                                                                                                  |
| `database-reviewer` agent          | Audits database-designer output across five dimensions: engine fit, schema/3NF, ERD accuracy, index completeness, and security config; returns DATABASE REVIEW PASSED / FAILED                                                                                                                                                                                                          |
| `database-fixer` agent             | Applies targeted corrections to schema, ERD, index plan, and connection config; writes the corrected ERD and `indexPlan` directly into `diagrams.json` (same pattern as `architecture-fixer`), and returns the corrected schema, ERD, index plan, and connection config for document embedding                                                                                          |
| `document-reviewer` agent          | Audits format compliance (metadata table, `dd-mmm-yyyy` date, filename pattern, Mermaid fenced blocks) and content completeness; returns DOCUMENT REVIEW PASSED / FAILED                                                                                                                                                                                                                |
| `document-fixer` agent             | Fixes specific F1–F7 format and C1–C8 content failures in the architecture document based on document-reviewer findings; overwrites the draft in place                                                                                                                                                                                                                                  |
| `architecture-implementer` agent   | Reads the approved architecture document, proposes a folder structure for confirmation, then scaffolds project code (models from ERD, handlers from sequence diagrams) and infrastructure files                                                                                                                                                                                         |

**Prerequisites:** Node.js; run `npm install` in `architecture-designer/scripts/` once to enable full Mermaid diagram syntax validation

---

### [changelog-manager](./changelog-manager)

Generates and maintains `CHANGELOG.md` and platform-specific release notes from git commit history.

| Component                                   | Description                                                                  |
|---------------------------------------------|------------------------------------------------------------------------------|
| `/changelog-manager:generate-changelog`     | Generate or update `CHANGELOG.md` with automatic semver bumping              |
| `/changelog-manager:generate-release-notes` | Create bilingual release notes for App Store, Play Store, or Web             |
| `/changelog-manager:changelog-config`       | Configure languages and platforms for your project                           |
| `changelog-reviewer` agent                  | Review changelog quality, semver accuracy, and release notes limits          |
| `release-notes-validator` agent             | Auto-trim release note items and append a closing phrase when limits are hit |

**Prerequisites:** Git, `jq`, Python 3

---

### [debugging-workflow](./debugging-workflow)

Parallel hypothesis debugging — generates multiple root-cause hypotheses, investigates them concurrently in isolated git worktrees, arbitrates when fixes conflict, and applies the winning diff to the original branch. Development-phase tool only; never touches production.

| Component                            | Description                                                                                                                                                   |
|--------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `/debugging-workflow:parallel-debug` | Orchestrate a full parallel debug session: preflight check, session setup, worktree isolation, agent spawning, arbitration, fix application, and cleanup      |
| Preflight check                      | Runs the project's install step + full test suite once before creating any worktree — stops before burning worktrees on a broken or too-slow test environment |
| `degraded_mode` setting              | Single shared worktree investigated sequentially instead of one worktree per hypothesis — for low-RAM/low-disk machines                                       |
| `hypothesis-investigator` agent      | Works in an isolated git worktree, writes a failing test, applies a targeted fix, and emits a structured YAML report                                          |
| `hypothesis-arbitrator` agent        | Invoked only when multiple investigators pass — re-verifies evidence and returns `ONE_WINNER`, `MERGE_FIXES`, or `ESCALATE_TO_USER`                           |

**Prerequisites:** Git

---

### [perfmind](./perfmind)

Performance investigation assistant for web, mobile, desktop, and API applications. Guides structured investigations from raw evidence (profiler output, GC logs, screenshots, metrics) to prioritized, role-tailored recommendations.

| Component                          | Description                                                                                                                                           |
|------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| `/perfmind:investigate [app-type]` | Start a structured investigation — accepts flame graphs, GC logs, metrics, traces                                                                     |
| `/perfmind:report [role]`          | Generate a role-tailored report (developer / DevOps / perf-engineer / leadership)                                                                     |
| `profiler-analysis` skill          | Auto-activates on flame graphs, GC logs, allocation traces, heap dumps, `.cpuprofile`, `pprof -top`, or `EXPLAIN ANALYZE` JSON                        |
| `scripts/parse-profiler.py`        | Deterministic top-N parser for `.cpuprofile`, `go tool pprof -top`, and PostgreSQL `EXPLAIN ANALYZE` JSON — the script computes, the skills interpret |
| `bottleneck-patterns` skill        | Auto-activates on slow response times, high CPU, memory leaks, jank, or ANR reports                                                                   |
| `impact-matrix` skill              | Auto-activates when asked to prioritize or rank performance findings                                                                                  |
| `performance-analyst` agent        | Hypothesis-driven deep-dive into a single performance domain                                                                                          |
| `report-generator` agent           | Generates polished, role-tailored reports from investigation findings                                                                                 |

**Supported platforms:** Web (Core Web Vitals), Android, iOS, Flutter, desktop, API/backend

---

### [git-helper](./git-helper)

Generates conventional commit messages and branch names from git context and user descriptions.

| Component                                 | Description                                                         |
|-------------------------------------------|---------------------------------------------------------------------|
| `/git-helper:generate-commit [file1 ...]` | Generate a conventional commit message from staged/unstaged changes |
| `/git-helper:generate-branch [#ticket]`   | Generate a branch name following team naming conventions            |

**Prerequisites:** Git

---

### [security-auditor](./security-auditor)

Structured security audit for development and production codebases. Maps every finding to a CWE ID and verifies dependency vulnerabilities against live CVE databases (NVD/OSV.dev/CISA KEV) via a bundled MCP server. CVE numbers only appear if returned by a tool call — never from model memory. Production mode enriches every CVE with EPSS exploitation probability and CISA KEV status.

| Component                            | Description                                                                                                                                           |
|--------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| `/audit [dev\|prod]`                 | Full codebase scan: structural SAST + dependency CVE verification + EPSS/KEV enrichment in prod mode                                                  |
| `/audit-diff [base-ref] [dev\|prod]` | Audit only files changed vs a base branch (or uncommitted/staged changes) — scoped analysis for PR review and codebases too large for a full `/audit` |
| `/audit-file <path>`                 | Deep single-file audit with data flow tracing, line-level evidence, and CWE mapping                                                                   |
| `/audit-deps`                        | Dependency-only scan — queries all manifest files and outputs a CVE table with severity and fix versions                                              |
| `/audit-report [--sarif]`            | Regenerates a complete `SECURITY-AUDIT.md` from current session findings; `--sarif` also emits `SECURITY-AUDIT.sarif.json` for GitHub code scanning   |
| `/audit-fix [SA-NNN]`                | Delegate one or more findings to `security-fixer`, then verify with `fix-reviewer`; one retry on failure                                              |
| `/audit-verify`                      | Re-run `fix-reviewer` against an existing fix manifest without applying new changes                                                                   |
| `security-auditor` agent             | Read-only subagent (`Read`, `Grep`, `Glob` only) for structural SAST analysis and CWE-mapped findings                                                 |
| `security-fixer` agent               | Applies minimal fixes per CWE root cause; outputs a fix manifest; never runs shell commands                                                           |
| `fix-reviewer` agent                 | Read-only post-fix verifier; assigns `fixed` / `partially-fixed` / `not-fixed` / `introduced-new-issue`                                               |
| `secure-code-review` skill           | OWASP Top 10 (2025) checklist, 38+ CWE mappings, severity scale, remediation protocol, and report template                                            |
| Baseline/suppression file            | `.security-audit-baseline.json` — accepted-risk findings stop reappearing in every report                                                             |
| PostToolUse hook                     | Warns when edited files contain high-risk patterns (SQL injection, eval, hardcoded secrets)                                                           |

**Prerequisites:** Python 3

**Optional:** `NVD_API_KEY` (raises NVD rate limit 5→50 req/30s), `GITHUB_TOKEN` (enables GitHub Advisory Database)

---

## Installation

Install all plugins at once using the marketplace:

```bash
cc plugin install https://github.com/sembraniteam/claude-plugins
```

Or install a single plugin by pointing to its directory:

```bash
cc plugin install https://github.com/sembraniteam/claude-plugins/architecture-designer
cc plugin install https://github.com/sembraniteam/claude-plugins/changelog-manager
cc plugin install https://github.com/sembraniteam/claude-plugins/debugging-workflow
cc plugin install https://github.com/sembraniteam/claude-plugins/git-helper
cc plugin install https://github.com/sembraniteam/claude-plugins/perfmind
cc plugin install https://github.com/sembraniteam/claude-plugins/security-auditor
```

---

## Quick Start

### Architecture design workflow

```
/architecture-designer:design
```

Claude walks you through six stages — requirements gathering, requirements analysis, feasibility and constraints, capacity planning, technology selection, and architecture and infrastructure design — followed by review, preview, and a low-level design step. Stage 6 covers four sub-phases in sequence — database schema (via `database-designer` agent), IaC tool selection and module structure, CI/CD pipeline design (platform, stages, branching strategy, environment promotion), and Mermaid diagram generation. At each stage it summarizes what it heard and asks for confirmation before continuing. After all diagrams are reviewed, a Low-Level Design step produces API contracts (per sequence-diagram endpoint), business rules with pseudocode, DTOs, inter-service contracts (microservices only), and an error catalog — all confirmed section by section before saving. The browser preview opens at `http://localhost:{port}` with zoom, pan, and per-diagram 2× resolution PNG export. Each diagram includes collapsible Details and Design Rationale blocks; ERD diagrams include an inline index plan table. Once you approve the design, the full document (HLD + IaC plan + CI/CD pipeline + LLD) is saved to `docs/architecture-designer/architecture/{yyyymmdd}-{topic}.md` and verified by a `document-reviewer` agent. You can then choose to scaffold the project with `architecture-implementer`.

```
/architecture-designer:review
```

Review an existing architecture from a saved document, the current codebase, or both. Detects drift between documented and implemented architecture, presents findings, and — if you approve revisions — goes through the same preview and document-save flow, saving a new versioned document.

```
/architecture-designer:implement
```

Turn an approved architecture document into a working project skeleton. Detects any existing project structure and asks whether to merge or start fresh, proposes the full folder layout for your confirmation, then generates data models (from the ERD), API route stubs (from sequence diagrams), configuration files, Docker setup, and infrastructure files.

### Commit workflow

```
/git-helper:generate-commit
```

Asks pre-flight questions (stage files, create branch, auto-commit), analyzes your changes, and generates a conventional commit message. Executes confirmed actions automatically.

### Changelog + release notes workflow

```
/changelog-manager:generate-changelog
```

Reads your git history since the last tag, writes a new version block to `CHANGELOG.md`, then offers to generate release notes for App Store, Play Store, or Web in your configured languages.

### First-time setup for changelog-manager

```
/changelog-manager:changelog-config
```

Creates `.claude/changelog-manager.local.md` with your preferred languages and platforms.

### Parallel debugging workflow

```
/debugging-workflow:parallel-debug <error message or stack trace>
```

Runs a preflight check (install + full test suite once, capped at a few minutes) before touching anything — if the environment is broken or too slow to multiply across worktrees, it stops and recommends manual debugging instead. Otherwise it creates a session directory, confirms the working tree is clean, generates 2–4 root-cause hypotheses, spins up isolated git worktrees for each, and spawns `hypothesis-investigator` agents in parallel. When multiple investigators produce passing fixes, `hypothesis-arbitrator` re-verifies evidence and decides whether to merge, pick one winner, or escalate to you. The winning diff is applied to your original branch and re-verified before the session worktrees are cleaned up.

To tune the number of hypotheses, time budget, agent parallelism, or the preflight timeout, create `.claude/debugging-workflow.local.md` — a template is at `debugging-workflow/skills/parallel-debug/examples/debugging-workflow.local.md`. Set `degraded_mode: true` there on low-RAM/low-disk machines to use a single shared worktree investigated sequentially instead of one worktree per hypothesis.

### Performance investigation workflow

```
/perfmind:investigate
```

Paste in profiler output, GC logs, screenshots, or metrics. Claude gathers evidence across multiple performance domains (response time, CPU, memory, GC, database, networking, battery) and produces a prioritized findings list. For Chrome/Node `.cpuprofile` files, `go tool pprof -top` output, or PostgreSQL `EXPLAIN (ANALYZE, FORMAT JSON)`, the `profiler-analysis` skill runs `scripts/parse-profiler.py` first — a deterministic script computes the ranked top-N hotspots, Claude interprets the result, instead of eyeballing raw output.

```
/perfmind:report developer
```

Generates a role-tailored report from the current investigation. Available roles: `developer`, `perf-engineer`, `devops`, `leadership`.

### Security audit workflow

```
/audit
```

Claude asks whether you're auditing a development or production codebase, maps your project (languages, frameworks, entry points, dependency manifests), spawns a read-only `security-auditor` agent for structural SAST analysis, then queries OSV.dev and NVD for every dependency version found. In production mode, each CVE is enriched with its EPSS exploitation probability (FIRST.org) and CISA KEV status — KEV-listed CVEs are automatically escalated to Critical. Output is a full report using the OWASP Top 10 (2025) checklist. Findings matching `.security-audit-baseline.json` (accepted risk) are excluded from the active list but still shown as suppressed.

```
/audit-diff main
```

Audit only the files changed vs `main` (or vs the repo's default branch, plus any uncommitted/staged changes, if no ref is given) — the recommended way to review a PR or to stay within context on a codebase too large for a full `/audit`.

```
/audit-file src/api/users.py
```

Deep single-file audit with data flow tracing from input sources to dangerous sinks (SQL, shell, file paths, eval, deserialization). Every finding is mapped to a CWE ID with line-level evidence and a concrete remediation.

```
/audit-deps
```

Dependency-only scan — no code analysis. Queries all manifest files (npm, PyPI, Go, Maven, Rust, Ruby, PHP, NuGet) and outputs a CVE table with CVSS scores and fix versions.

```
/audit-report --sarif
```

Regenerates and saves `SECURITY-AUDIT.md` from the current session's findings; `--sarif` also writes `SECURITY-AUDIT.sarif.json` for GitHub code scanning or any tool that ingests SARIF 2.1.0.

---

## Repository Structure

```
.
├── .claude-plugin/
│   └── marketplace.json          # Plugin registry
├── architecture-designer/
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── agents/
│   │   ├── architecture-reviewer.md    # Technical correctness + requirements alignment; REVIEW PASSED / FAILED
│   │   ├── architecture-fixer.md       # Fixes Mermaid diagrams from reviewer findings; updates diagrams.json
│   │   ├── database-designer.md        # ERD, index plan, engine selection, and secure connection config
│   │   ├── database-reviewer.md        # Audits database design across 5 dimensions; DATABASE REVIEW PASSED / FAILED
│   │   ├── database-fixer.md           # Fixes schema, ERD, index plan; writes ERD + companionTable to diagrams.json in place
│   │   ├── document-reviewer.md        # Format + content auditor; DOCUMENT REVIEW PASSED / FAILED
│   │   ├── document-fixer.md           # Fixes F1–F7 format and C1–C6 content failures in place
│   │   └── architecture-implementer.md # Scaffold generator from architecture document
│   ├── skills/
│   │   ├── design/
│   │   │   ├── SKILL.md                # Six-stage design + review/preview/LLD steps: requirements → technology → IaC → CI/CD → LLD → document
│   │   │   └── references/
│   │   │       ├── diagrams-guide.md   # Mermaid templates, anti-overlap rules (ELK, align), CI/CD pipeline template
│   │   │       ├── iac-guide.md        # IaC tool selection, state backend, module structure, environment strategy
│   │   │       ├── cicd-guide.md       # CI/CD platform selection, pipeline stages, branching, promotion, secrets
│   │   │       ├── lld-guide.md        # LLD artifact formats: API contracts, business rules, DTOs, error catalog
│   │   │       └── tech-stacks.md      # Technology options by pattern, scale, cloud, and language
│   │   ├── review/
│   │   │   └── SKILL.md                # Review document / codebase drift → revise → new document
│   │   └── implement/
│   │       └── SKILL.md                # Standalone implementation: find doc → assess project → save plan → scaffold
│   └── scripts/
│       ├── find-port.mjs               # Finds available port 3000–9000 via net.createServer()
│       ├── preview-server.mjs          # Serves preview HTML; auto-opens browser; 2× resolution PNG export
│       ├── validate-diagrams.mjs       # Validates diagrams.json syntax (mermaid + @mermaid-js/parser); exits 0/1
│       ├── validate-session.mjs        # Pre-flight check that session.json stages 1–5 are complete
│       ├── package.json                # mermaid, jsdom, @mermaid-js/parser — run `npm install` once
│       └── .gitignore                  # Excludes node_modules/
├── changelog-manager/
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── agents/
│   │   ├── changelog-reviewer.md
│   │   └── release-notes-validator.md
│   ├── scripts/
│   │   ├── analyze-commits.sh
│   │   └── generate-release-notes.py
│   └── skills/
│       ├── changelog-config/
│       ├── generate-changelog/
│       └── generate-release-notes/
├── debugging-workflow/
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── agents/
│   │   ├── hypothesis-arbitrator.md
│   │   └── hypothesis-investigator.md
│   └── skills/
│       └── parallel-debug/
│           ├── SKILL.md
│           ├── examples/
│           └── references/
├── git-helper/
│   ├── .claude-plugin/
│   │   └── plugin.json
│   └── skills/
│       ├── generate-branch/
│       └── generate-commit/
├── perfmind/
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── agents/
│   │   ├── performance-analyst.md
│   │   └── report-generator.md
│   ├── scripts/
│   │   └── parse-profiler.py     # Deterministic top-N parser: cpuprofile, pprof -top, EXPLAIN ANALYZE JSON
│   └── skills/
│       ├── bottleneck-patterns/
│       │   ├── SKILL.md
│       │   └── references/
│       ├── impact-matrix/
│       │   └── SKILL.md
│       ├── investigate/
│       │   ├── SKILL.md
│       │   └── examples/
│       ├── profiler-analysis/
│       │   └── SKILL.md
│       └── report/
│           ├── SKILL.md
│           └── references/
└── security-auditor/
    ├── .claude-plugin/
    │   └── plugin.json
    ├── .mcp.json
    ├── agents/
    │   ├── security-auditor.md       # Read-only SAST agent (Read + Grep + Glob only)
    │   ├── security-fixer.md         # Applies minimal CWE-root-cause fixes; outputs fix manifest
    │   └── fix-reviewer.md           # Verifies fixes closed the root cause; never writes files
    ├── commands/
    │   ├── audit.md                  # Full codebase audit orchestrator
    │   ├── audit-diff.md             # Audit only files changed vs a base branch
    │   ├── audit-file.md             # Single-file deep audit
    │   ├── audit-deps.md             # Dependency CVE scan
    │   ├── audit-fix.md              # Remediation pipeline: fixer → reviewer, one retry on failure
    │   ├── audit-verify.md           # Re-run fix-reviewer against an existing fix manifest
    │   └── audit-report.md           # Save findings as SECURITY-AUDIT.md (+ optional SARIF)
    ├── hooks/
    │   └── hooks.json                # PostToolUse hook — warns on high-risk patterns
    ├── scripts/
    │   ├── security-lint.py          # Hook script — CWE-89/78/798/502/94 pattern detection
    │   └── vuln_server.py            # MCP server: NVD + OSV.dev + MITRE CWE + GitHub Advisory + EPSS + CISA KEV
    ├── skills/
    │   └── secure-code-review/
    │       ├── SKILL.md              # OWASP Top 10 (2025), 38+ CWE mappings, report template
    │       └── references/
    │           ├── baseline-suppression.md  # .security-audit-baseline.json format & matching
    │           ├── sarif-output.md          # SARIF 2.1.0 structure for /audit-report --sarif
    │           └── remediation-protocol.md  # Fix manifest, verdicts, per-CWE fix examples
    └── test-fixtures/                # Intentionally vulnerable demo files
        ├── vulnerable_app.py
        ├── insecure_api.js
        └── package.json
```

---

## License

MIT — see individual plugin directories for full license text.

# sembraniteam-claude-plugins

A collection of [Claude Code](https://claude.ai/code) plugins for automating git workflows, release documentation, debugging, and software architecture design.

## Plugins

### [archimind](./archimind)

Design and review system architectures, database schemas, and feature modules with three-option comparison and visual Mermaid diagrams in a local browser viewer.

| Component                        | Description                                                                                                                     |
|----------------------------------|---------------------------------------------------------------------------------------------------------------------------------|
| `/archimind:design-architecture` | Design a new architecture — presents three options (Lean/Standard/Advanced) with diagrams and tech stack recommendations        |
| `/archimind:review-architecture` | Audit an existing system, identify antipatterns, and propose three redesign options with migration paths                        |
| `/archimind:design-database`     | Design new schemas or normalize existing SQL DDL with ER diagrams and index strategy                                            |
| `/archimind:design-feature`      | Design a new feature or module — presents three options (Inline/Modular/Decoupled) with integration diagrams and test strategy  |
| `/archimind:visualize`           | Launch a local Mermaid JS viewer with tab navigation, pan/zoom, and PNG export                                                  |

**Prerequisites:** Python 3

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

Parallel hypothesis debugging — generates multiple root-cause hypotheses, investigates them concurrently in isolated git worktrees, arbitrates when fixes conflict, and applies the winning diff to the original branch.

| Component                            | Description                                                                                                                             |
|--------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------|
| `/debugging-workflow:parallel-debug` | Orchestrate a full parallel debug session: session setup, worktree isolation, agent spawning, arbitration, fix application, and cleanup |
| `hypothesis-investigator` agent      | Works in an isolated git worktree, writes a failing test, applies a targeted fix, and emits a structured YAML report                    |
| `hypothesis-arbitrator` agent        | Invoked only when multiple investigators pass — re-verifies evidence and returns `ONE_WINNER`, `MERGE_FIXES`, or `ESCALATE_TO_USER`     |

**Prerequisites:** Git

---

### [perfmind](./perfmind)

Performance investigation assistant for web, mobile, desktop, and API applications. Guides structured investigations from raw evidence (profiler output, GC logs, screenshots, metrics) to prioritized, role-tailored recommendations.

| Component                          | Description                                                                         |
|------------------------------------|-------------------------------------------------------------------------------------|
| `/perfmind:investigate [app-type]` | Start a structured investigation — accepts flame graphs, GC logs, metrics, traces   |
| `/perfmind:report [role]`          | Generate a role-tailored report (developer / DevOps / perf-engineer / leadership)   |
| `profiler-analysis` skill          | Auto-activates when flame graphs, allocation traces, or heap dumps are shared       |
| `bottleneck-patterns` skill        | Auto-activates on slow response times, high CPU, memory leaks, jank, or ANR reports |
| `impact-matrix` skill              | Auto-activates when asked to prioritize or rank performance findings                |
| `performance-analyst` agent        | Hypothesis-driven deep-dive into a single performance domain                        |
| `report-generator` agent           | Generates polished, role-tailored reports from investigation findings               |

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

## Installation

Install all plugins at once using the marketplace:

```bash
cc plugin install https://github.com/sembraniteam/claude-plugins
```

Or install a single plugin by pointing to its directory:

```bash
cc plugin install https://github.com/sembraniteam/claude-plugins/archimind
cc plugin install https://github.com/sembraniteam/claude-plugins/changelog-manager
cc plugin install https://github.com/sembraniteam/claude-plugins/debugging-workflow
cc plugin install https://github.com/sembraniteam/claude-plugins/git-helper
cc plugin install https://github.com/sembraniteam/claude-plugins/perfmind
```

---

## Quick Start

### Architecture design workflow

```
/archimind:design-architecture
```

Claude gathers requirements dynamically (skipping questions already answered in context), then presents three architecture options (Lean/Standard/Advanced) with Mermaid diagrams, tech stack recommendations, and trade-off analysis. The selected option is saved to `docs/archimind/architecture/`.

```
/archimind:visualize
```

Launches a local interactive viewer at `http://localhost:{port}` to explore diagrams with pan/zoom, tab navigation between options, and PNG export.

### Feature design workflow

```
/archimind:design-feature
```

Claude analyzes the existing application context and feature requirements, then presents three implementation options (Inline/Modular/Decoupled) with integration diagrams and testing strategies. The selected option is saved to `docs/archimind/features/`.

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

Creates a session directory, confirms the working tree is clean, generates 2–4 root-cause hypotheses, spins up isolated git worktrees for each, and spawns `hypothesis-investigator` agents in parallel. When multiple investigators produce passing fixes, `hypothesis-arbitrator` re-verifies evidence and decides whether to merge, pick one winner, or escalate to you. The winning diff is applied to your original branch and re-verified before the session worktrees are cleaned up.

To tune the number of hypotheses, time budget, or agent parallelism, create `.claude/debugging-workflow.local.md` — a template is at `debugging-workflow/skills/parallel-debug/examples/debugging-workflow.local.md`.

### Performance investigation workflow

```
/perfmind:investigate
```

Paste in profiler output, GC logs, screenshots, or metrics. Claude gathers evidence across multiple performance domains (response time, CPU, memory, GC, database, networking, battery) and produces a prioritized findings list.

```
/perfmind:report developer
```

Generates a role-tailored report from the current investigation. Available roles: `developer`, `perf-engineer`, `devops`, `leadership`.

---

## Repository Structure

```
.
├── .claude-plugin/
│   └── marketplace.json          # Plugin registry
├── archimind/
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── scripts/
│   │   ├── find-port.sh
│   │   ├── start-server.sh
│   │   ├── stop-server.sh
│   │   └── site/
│   │       └── index.html        # Mermaid JS viewer
│   └── skills/
│       ├── design-architecture/
│       ├── design-database/
│       ├── design-feature/
│       ├── review-architecture/
│       └── visualize/
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
└── perfmind/
    ├── .claude-plugin/
    │   └── plugin.json
    ├── agents/
    │   ├── performance-analyst.md
    │   └── report-generator.md
    └── skills/
        ├── bottleneck-patterns/
        │   ├── SKILL.md
        │   └── references/
        ├── impact-matrix/
        │   └── SKILL.md
        ├── investigate/
        │   ├── SKILL.md
        │   └── examples/
        ├── profiler-analysis/
        │   └── SKILL.md
        └── report/
            ├── SKILL.md
            └── references/
```

---

## License

MIT — see individual plugin directories for full license text.

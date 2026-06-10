# sembraniteam-claude-plugins

A collection of [Claude Code](https://claude.ai/code) plugins for automating git workflows, release documentation, debugging, and software architecture design.

## Plugins

### [archimind](./archimind)

AI-powered software architecture and database designer with interactive Mermaid JS visualization.

| Component                              | Description                                                                    |
|----------------------------------------|--------------------------------------------------------------------------------|
| `/archimind:design-architecture`       | Design a new architecture — presents three options (Lean/Standard/Advanced) with diagrams and tech stack recommendations |
| `/archimind:review-architecture`       | Audit an existing system, identify antipatterns, and propose three redesign options with migration paths |
| `/archimind:design-database`           | Design new schemas or normalize existing SQL DDL with ER diagrams and index strategy |
| `/archimind:visualize`                 | Launch a local Mermaid JS viewer with tab navigation, pan/zoom, and PNG export |

**Prerequisites:** Python 3

---

### [changelog-manager](./changelog-manager)

Generates and maintains `CHANGELOG.md` and platform-specific release notes from git commit history.

| Component                                   | Description                                                         |
|---------------------------------------------|---------------------------------------------------------------------|
| `/changelog-manager:generate-changelog`     | Generate or update `CHANGELOG.md` with automatic semver bumping     |
| `/changelog-manager:generate-release-notes` | Create bilingual release notes for App Store, Play Store, or Web    |
| `/changelog-manager:changelog-config`       | Configure languages and platforms for your project                  |
| `changelog-reviewer` agent                  | Review changelog quality, semver accuracy, and release notes limits |

**Prerequisites:** Git, `jq`, Python 3

---

### [debugging-workflow](./debugging-workflow)

Systematic debugging plugin with a structured 8-step process: pre-flight checklist, context gathering, git diff analysis, test discovery, root cause analysis, targeted fix, multi-language verification, and test execution.

| Component                           | Description                                                |
|-------------------------------------|------------------------------------------------------------|
| `/debugging-workflow:debug [error]` | Run the full debugging workflow from error to verified fix |
| `analyze-code` skill                | Auto-detect language and run appropriate analysis tools    |
| `code-analyzer` agent               | Autonomous full-project static analysis reporter           |

**Supported languages:** Dart/Flutter, Rust, TypeScript, JavaScript, Python, Go, Java, Kotlin, Swift, Ruby, C/C++

**Prerequisites:** Git, plus the analyze tool for your language (`dart`, `cargo`, `npx`, `ruff`, `go`, etc.)

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
cc plugin install https://github.com/sembraniteam/claude-plugins/git-helper
cc plugin install https://github.com/sembraniteam/claude-plugins/debugging-workflow
```

---

## Quick Start

### Architecture design workflow

```
/archimind:design-architecture
```

Claude asks 8 requirements questions, then presents three architecture options (Lean/Standard/Advanced) with Mermaid diagrams, tech stack recommendations, and trade-off analysis. The selected option is saved to `docs/archimind/architecture/`.

```
/archimind:visualize
```

Launches a local interactive viewer at `http://localhost:{port}` to explore diagrams with pan/zoom, tab navigation between options, and PNG export.

### Commit workflow

```
/git-helper:generate-commit
```

Analyzes your staged changes and outputs a ready-to-run `git commit` command. After generating the message, it offers to generate a branch name if you need one.

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

### Debugging workflow

```
/debugging-workflow:debug <error message or stack trace>
```

Runs a structured 8-step debugging session: parses the error, reads relevant files, checks `git diff`, finds related tests, concludes the root cause, applies a fix, verifies with the appropriate language tool, and runs tests.

### First-time setup for debugging-workflow

```
/debugging-workflow:debug
```

On first run, if no `.claude/debugging-workflow.local.md` exists, Claude will offer to create one and walk you through setting `lint_config_path`, `skip_verification`, and an optional `analyze_command`.

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
│       ├── review-architecture/
│       └── visualize/
├── changelog-manager/
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── agents/
│   │   └── changelog-reviewer.md
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
│   │   └── code-analyzer.md
│   └── skills/
│       ├── analyze-code/
│       │   ├── SKILL.md
│       │   └── examples/
│       └── debug/
│           ├── SKILL.md
│           └── references/
└── git-helper/
    ├── .claude-plugin/
    │   └── plugin.json
    ├── scripts/
    │   └── collect-context.sh
    └── skills/
        ├── generate-branch/
        └── generate-commit/
```

---

## License

MIT — see individual plugin directories for full license text.

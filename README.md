# sembraniteam-claude-plugins

A collection of [Claude Code](https://claude.ai/code) plugins for automating git workflows and release documentation.

## Plugins

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

### [git-helper](./git-helper)

Generates conventional commit messages and branch names from git context and user descriptions.

| Component                                 | Description                                                         |
|-------------------------------------------|---------------------------------------------------------------------|
| `/git-helper:generate-commit [file1 ...]` | Generate a conventional commit message from staged/unstaged changes |
| `/git-helper:generate-branch [#ticket]`   | Generate a branch name following team naming conventions            |

**Prerequisites:** Git

---

## Installation

Install both plugins at once using the marketplace:

```bash
cc plugin install https://github.com/sembraniteam/claude-plugins
```

Or install a single plugin by pointing to its directory:

```bash
cc plugin install https://github.com/sembraniteam/claude-plugins/changelog-manager
cc plugin install https://github.com/sembraniteam/claude-plugins/git-helper
```

---

## Quick Start

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

---

## Repository Structure

```
.
├── .claude-plugin/
│   └── marketplace.json          # Plugin registry
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

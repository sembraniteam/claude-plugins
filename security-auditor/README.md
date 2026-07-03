# security-auditor

A Claude Code plugin for structured, professional security audits — usable in both development and production contexts. It maps every finding to a CWE ID and verifies dependency vulnerabilities against real CVE databases (NVD/OSV.dev) via a bundled MCP server.

---

## Features

- **`/audit`** — Full codebase scan: code analysis + dependency CVE verification
- **`/audit-file <path>`** — Deep single-file audit with line-level evidence and CWE mapping
- **`/audit-deps`** — Dependency-only scan against OSV.dev + NVD, outputs a CVE table
- **`/audit-report`** — Regenerates a complete `SECURITY-AUDIT.md` from session findings
- **Bundled MCP server** (`scripts/vuln_server.py`) — Queries NVD, OSV.dev, MITRE CWE API, and GitHub Advisory Database
- **OWASP Top 10 (2021)** checklist + 35+ CWE mappings
- **PostToolUse hook** — Warns when edited files contain high-risk patterns (opt-out available)
- **Anti-hallucination guarantee** — CVE numbers only appear if returned by an MCP tool call; never from model memory

---

## Installation

### Option 1: Install from this repo (marketplace)

```bash
# Add this repo as a marketplace source
/plugin marketplace add sembraniteam/claude-plugins

# Install the plugin
/plugin install security-auditor@sembraniteam-claude-plugins
```

### Option 2: Local install (development)

```bash
# Clone the repo
git clone https://github.com/sembraniteam/claude-plugins.git

# Add the local repo as a marketplace
/plugin marketplace add /path/to/claude-plugins

# Install
/plugin install security-auditor@sembraniteam-claude-plugins
```

---

## Environment Variables

| Variable       | Required | Description                                                                                                         |
|----------------|----------|---------------------------------------------------------------------------------------------------------------------|
| `NVD_API_KEY`  | Optional | NVD API key — raises rate limit from 5 to 50 req/30s. Get one at https://nvd.nist.gov/developers/request-an-api-key |
| `GITHUB_TOKEN` | Optional | GitHub personal access token — enables GitHub Advisory Database queries                                             |

Set them in your shell profile or Claude Code's environment settings:

```bash
export NVD_API_KEY="your-key-here"
export GITHUB_TOKEN="ghp_your_token_here"
```

---

## Commands

### `/audit [dev|prod]`

Full security audit of the current project.

```
/audit
# → asks: development or production mode?

/audit prod
# → skips the question, runs in production mode
```

**What it does:**
1. Maps your project (languages, frameworks, entry points, dependency manifests)
2. Spawns `security-auditor` agent for read-only structural code analysis
3. Queries OSV.dev + NVD for every dependency version found
4. Outputs a full report using the `secure-code-review` skill template

---

### `/audit-file <path>`

Deep single-file audit with data flow tracing and line-level evidence.

```
/audit-file src/api/users.py
/audit-file controllers/AuthController.js
```

---

### `/audit-deps`

Scan only dependency manifests. Fast — no code analysis.

```
/audit-deps
```

**Output:**

| Package | Installed | CVE            | CVSS | Severity | Fixed In |
|---------|-----------|----------------|------|----------|----------|
| lodash  | 4.17.4    | CVE-2019-10744 | 9.8  | Critical | 4.17.21  |
| axios   | 0.21.0    | CVE-2021-3749  | 7.5  | High     | 0.21.2   |

---

### `/audit-report`

Regenerate and save the full report from this session.

```
/audit-report
# → saves SECURITY-AUDIT.md in current directory
```

---

## Example Report Output

```markdown
# Security Audit Report

**Project**: my-web-app
**Date**: 2026-07-03
**Mode**: production
**Stack**: Python / Flask, SQLite

## Executive Summary

Audited 23 files and 8 dependency manifests. Found 12 issues (2 critical, 4 high,
5 medium, 1 low). Most urgent: SQL injection in `api/users.py:42` allows unauthenticated
data extraction from the users table.

| Severity | Count |
|----------|-------|
| Critical | 2     |
| High     | 4     |
| Medium   | 5     |
| Low      | 1     |

## Findings Summary

| ID     | Title                        | Severity       | CWE     | CVE | Location          |
|--------|------------------------------|----------------|---------|-----|-------------------|
| VULN-1 | SQL Injection in user lookup | Critical (est) | CWE-89  | —   | `api/users.py:42` |
| VULN-2 | Hardcoded API key            | High (est)     | CWE-798 | —   | `config.py:7`     |
| VULN-3 | OS Command Injection in ping | Critical (est) | CWE-78  | —   | `api/admin.py:88` |

## Dependency Vulnerabilities

| Package | Installed | CVE            | CVSS | Severity | Fixed In |
|---------|-----------|----------------|------|----------|----------|
| lodash  | 4.17.4    | CVE-2019-10744 | 9.8  | Critical | 4.17.21  |
```

---

## Architecture

```
security-auditor/
├── commands/          # Slash command prompt templates (/audit, /audit-file, etc.)
├── agents/
│   └── security-auditor.md   # Read-only code analysis subagent (Read+Grep+Glob only)
├── skills/
│   └── secure-code-review/
│       └── SKILL.md          # OWASP checklist, CWE mapping, report template
├── scripts/
│   ├── vuln_server.py         # MCP server: NVD + OSV.dev + MITRE CWE + GitHub Advisory
│   └── security-lint.py       # PostToolUse hook script
├── hooks/
│   └── hooks.json             # PostToolUse hook definition
└── .mcp.json                  # MCP server registration
```

**Data flow:**
1. User runs `/audit` → command orchestrates the workflow
2. Command spawns `security-auditor` agent (read-only: `Read`, `Grep`, `Glob` only)
3. Agent returns structured findings with CWE IDs
4. Command calls MCP tools (`query_osv`, `get_cve`) for dependency CVEs
5. `secure-code-review` skill formats the final report

---

## Disabling the PostToolUse Hook

The hook warns about high-risk patterns (SQL injection, eval, hardcoded secrets) whenever you edit a source file. To disable it:

**Option 1 — Per project**: add to your project's `.claude/settings.json`:
```json
{
  "disabledHooks": ["security-auditor:PostToolUse"]
}
```

**Option 2 — Global disable**: remove the `PostToolUse` entry from the plugin's `hooks/hooks.json` after installation.

---

## Limitations & Disclaimer

- This tool performs **static analysis only** — it cannot detect vulnerabilities that only manifest at runtime (timing attacks, race conditions, business logic flaws).
- It **may produce false positives** (flagging safe patterns that look risky) and **false negatives** (missing vulnerabilities outside its detection patterns).
- CVE data is queried live from OSV.dev and NVD — results depend on database coverage and your internet connection.
- **This tool is not a substitute for professional penetration testing** or a comprehensive security review by a human expert.
- All findings should be verified by a qualified developer or security engineer before remediation.

**License**: MIT

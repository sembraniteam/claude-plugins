# security-auditor

A Claude Code plugin for structured, professional security audits — usable in both development and production contexts. It maps every finding to a CWE ID and verifies dependency vulnerabilities against real CVE databases (NVD/OSV.dev) via a bundled MCP server.

---

## Features

- **`/audit`** — Full codebase scan: code analysis + dependency CVE verification
- **`/audit-file <path>`** — Deep single-file audit with line-level evidence and CWE mapping
- **`/audit-deps`** — Dependency-only scan against OSV.dev + NVD, outputs a CVE table
- **`/audit-report`** — Regenerates a complete `SECURITY-AUDIT.md` from session findings
- **`/audit-fix [SA-NNN|all]`** — Verified remediation: plan → confirm → fix → auto-verify
- **`/audit-verify`** — Run independent fix verification on manual or existing changes
- **Bundled MCP server** (`scripts/vuln_server.py`) — Queries NVD, OSV.dev, MITRE CWE API, and GitHub Advisory Database
- **OWASP Top 10 (2025)** checklist + 38+ CWE mappings
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

### `/audit-fix [finding-id|all]`

Apply verified, minimal fixes to findings from the most recent audit report.

```
/audit-fix
# → shows all findings, confirms scope, then fixes

/audit-fix all
# → fixes all findings (still shows plan per finding before writing)

/audit-fix SA-001
# → fixes only SA-001

/audit-fix SA-001,SA-003
# → fixes SA-001 and SA-003 only

/audit-fix critical
# → fixes all Critical-severity findings
```

**What it does:**
1. Validates that an audit report exists in the session (or as `SECURITY-AUDIT.md`)
2. Shows the list of findings in scope + any that may need human review
3. Delegates to `security-fixer`: shows a fix plan per finding, waits for confirmation, applies minimal changes
4. Automatically delegates the fix manifest to `fix-reviewer` for independent verification
5. If reviewer flags a finding as `not-fixed` or `introduced-new-issue`, sends it back to the fixer for one retry
6. After one failed retry, marks the finding `needs-human` — the loop never runs more than twice per finding
7. Closes with a summary of what was fixed, what needs human attention, and next steps

> **Fixes are never applied automatically.** The fixer always shows a plan before writing any file. Pass `"fix all without asking per item"` as confirmation to skip per-finding plan approvals.

---

### `/audit-verify`

Run the independent `fix-reviewer` agent on existing changes — useful when you fixed vulnerabilities manually or want a second opinion before committing.

```
/audit-verify
# → verifies fixes against the last audit report
```

Works with any fix — not just ones applied by `/audit-fix`. If no fix manifest is available, describes which files/findings to verify.

---

## Auditor → Fixer → Reviewer Workflow

```mermaid
flowchart TD
    A([User runs /audit]) --> B["security-auditor agent<br/>Read · Grep · Glob only"]
    B -->|Returns findings with stable SA-NNN IDs| C[(Audit report in session)]
    C -->|User explicitly runs /audit-fix| D[/audit-fix command]
    D --> E["security-fixer agent<br/>Read · Grep · Glob · Write · Edit · no Bash<br/>① Shows fix plan per finding<br/>② Waits for user confirmation<br/>③ Applies minimal change per CWE root cause<br/>④ Outputs fix manifest"]
    E -->|auto-continues| F["fix-reviewer agent<br/>Read · Grep · Glob only<br/>• Reads report + fix manifest + current files<br/>• Verdicts each SA-NNN: fixed / partially-fixed /<br/>  not-fixed / introduced-new-issue"]
    F -->|fixed / partially-fixed| G([Final summary to user])
    F -->|not-fixed / introduced-new-issue| H{Retry available?}
    H -->|Yes| E
    H -->|"No → needs-human"| G
```

---

## Tool Permissions per Agent

| Agent              | Read | Grep | Glob | Write | Edit | Bash |
|--------------------|------|------|------|-------|------|------|
| `security-auditor` | ✅    | ✅    | ✅    | ❌     | ❌    | ❌    |
| `security-fixer`   | ✅    | ✅    | ✅    | ✅     | ✅    | ❌    |
| `fix-reviewer`     | ✅    | ✅    | ✅    | ❌     | ❌    | ❌    |

The fixer never runs shell commands, installs packages, or executes tests — those remain the developer's responsibility.

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
| SA-001 | SQL Injection in user lookup | Critical (est) | CWE-89  | —   | `api/users.py:42` |
| SA-002 | Hardcoded API key            | High (est)     | CWE-798 | —   | `config.py:7`     |
| SA-003 | OS Command Injection in ping | Critical (est) | CWE-78  | —   | `api/admin.py:88` |

## Dependency Vulnerabilities

| Package | Installed | CVE            | CVSS | Severity | Fixed In |
|---------|-----------|----------------|------|----------|----------|
| lodash  | 4.17.4    | CVE-2019-10744 | 9.8  | Critical | 4.17.21  |
```

---

## Architecture

```
security-auditor/
├── commands/
│   ├── audit.md               # /audit — full codebase scan
│   ├── audit-file.md          # /audit-file — single file deep dive
│   ├── audit-deps.md          # /audit-deps — dependency CVE scan only
│   ├── audit-report.md        # /audit-report — save SECURITY-AUDIT.md
│   ├── audit-fix.md           # /audit-fix — remediation with verification
│   └── audit-verify.md        # /audit-verify — standalone fix verification
├── agents/
│   ├── security-auditor.md    # Read-only SAST agent (Read+Grep+Glob only)
│   ├── security-fixer.md      # Remediation agent (Read+Grep+Glob+Write+Edit, no Bash)
│   └── fix-reviewer.md        # Verification agent (Read+Grep+Glob only)
├── skills/
│   └── secure-code-review/
│       └── SKILL.md           # OWASP checklist, CWE mapping, report template,
│                              # remediation & verification protocol
├── scripts/
│   ├── vuln_server.py         # MCP server: NVD + OSV.dev + MITRE CWE + GitHub Advisory
│   └── security-lint.py       # PostToolUse hook script
├── hooks/
│   └── hooks.json             # PostToolUse hook definition
├── test-fixtures/             # Intentionally vulnerable demo files, for
│                              # trying the plugin against known-bad code
└── .mcp.json                  # MCP server registration
```

**Audit data flow:**
1. User runs `/audit` → command orchestrates the workflow
2. Command spawns `security-auditor` agent (read-only: `Read`, `Grep`, `Glob` only)
3. Agent returns structured findings with stable `SA-NNN` IDs and CWE mappings
4. Command calls MCP tools (`query_osv`, `get_cve`) for dependency CVEs
5. `secure-code-review` skill formats the final report

**Remediation data flow (user-triggered only):**
1. User runs `/audit-fix` → command validates audit report exists
2. Command spawns `security-fixer` → plan → confirm → apply → fix manifest
3. Command spawns `fix-reviewer` → reads manifest + current files → verdict per SA-NNN
4. If `not-fixed`: one retry loop; after that, `needs-human` and stop

---

## Disabling the PostToolUse Hook

The hook warns about high-risk patterns (SQL injection, eval, hardcoded secrets) whenever you edit a source file. To disable it:

**Option 1 — Per environment**: set the environment variable `SECURITY_AUDITOR_DISABLE_LINT=1` (e.g. in your shell profile) before starting Claude Code. The hook script checks this and exits immediately without scanning.

**Option 2 — Global disable**: remove the `PostToolUse` entry from the plugin's `hooks/hooks.json` after installation.

There is no Claude Code settings key for disabling a single plugin's hook by name — the two options above are the only mechanisms.

---

## Limitations & Disclaimer

- This tool performs **static analysis only** — it cannot detect vulnerabilities that only manifest at runtime (timing attacks, race conditions, business logic flaws).
- It **may produce false positives** (flagging safe patterns that look risky) and **false negatives** (missing vulnerabilities outside its detection patterns).
- CVE data is queried live from OSV.dev and NVD — results depend on database coverage and your internet connection.
- **This tool is not a substitute for professional penetration testing** or a comprehensive security review by a human expert.
- All findings should be verified by a qualified developer or security engineer before remediation.

### Automated Fix Disclaimer

> **Automated fixes from `/audit-fix` must be reviewed and tested by a human before being merged to production.**
>
> The `security-fixer` agent applies minimal, targeted code changes based on static analysis. It does not run your test suite, does not verify runtime behavior, and cannot account for integration effects or business logic that is not visible from the code alone. The `fix-reviewer` agent independently verifies each fix from code reading — but static verification is not a substitute for running your tests.
>
> **Recommended process before committing any auto-generated fix:**
> 1. Review the diff manually (the fix plan and fix manifest describe every change made)
> 2. Run your full test suite
> 3. Test the affected endpoint or code path manually with attack inputs
> 4. Commit each finding's fix separately for clean, reversible history
> 5. Run `/audit` again after committing to confirm the report is clean

**License**: MIT

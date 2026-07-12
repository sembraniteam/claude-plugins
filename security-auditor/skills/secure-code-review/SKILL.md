---
name: secure-code-review
description: Apply this skill whenever the user runs /audit, /audit-file, /audit-deps, /audit-report, asks to "review code for security", "check for vulnerabilities", "is this code safe", "audit my dependencies", "scan for CVEs", "find security issues", "OWASP audit", or describes security concerns about their codebase. Also apply whenever the security-auditor agent returns findings that need formatting into a report.
---

# Secure Code Review Methodology

This skill provides the checklist, CWE mapping, and report template used by all `security-auditor` commands.

## OWASP Top 10 (2025) Checklist + Extended Categories

Work through each category. Mark each as: ✓ checked, ⚠ findings, or N/A (not applicable to this codebase).

### OWASP Top 10

| #   | Category                              | Key checks                                                                                                                                                                                       |
|-----|---------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| A01 | Broken Access Control                 | Missing authz checks, IDOR, path traversal, CORS misconfiguration, privilege escalation, SSRF (outbound HTTP with user-controlled URL, missing allowlist, cloud metadata endpoint exposure)      |
| A02 | Security Misconfiguration             | Default credentials, unnecessary features enabled, verbose errors, missing security headers, overly-permissive cloud storage policies                                                            |
| A03 | Software Supply Chain Failures        | Dependencies with known CVEs (verified via MCP, never from memory), untrusted/typosquatted packages, unsigned or unverified build artifacts/container images, missing dependency pinning or SBOM |
| A04 | Cryptographic Failures                | Sensitive data in plaintext, weak algorithms, static keys/IVs, missing TLS                                                                                                                       |
| A05 | Injection                             | SQL, NoSQL, OS command, LDAP, XPath, template, expression language                                                                                                                               |
| A06 | Insecure Design                       | Missing rate limiting, insecure direct object references in design, trust boundary violations                                                                                                    |
| A07 | Authentication Failures               | Weak passwords, missing MFA support, insecure session management, credential stuffing exposure                                                                                                   |
| A08 | Software or Data Integrity Failures   | Unsigned updates/plugins, insecure deserialization, missing checksums/digital signatures, absent tamper-detection on critical data                                                               |
| A09 | Security Logging & Alerting Failures  | No audit trail for sensitive ops, PII logged, log injection, missing alerting on suspicious activity                                                                                             |
| A10 | Mishandling of Exceptional Conditions | Verbose error messages leaking internals, fail-open logic on exception/error paths, unhandled timeouts, generic catch-alls masking security failures                                             |

`A03:2025` (Software Supply Chain Failures) supersedes and broadens `A06:2021` (Vulnerable & Outdated Components) to also cover CI/CD pipeline integrity and build/distribution infrastructure. `A10:2025` (Mishandling of Exceptional Conditions) is new for 2025 — it did not exist as a Top 10 category in 2021. SSRF is no longer its own category; it is checked under A01.

### Extended Categories

| Category                 | Key checks                                                                             |
|--------------------------|----------------------------------------------------------------------------------------|
| Hardcoded Secrets        | API keys, passwords, tokens, private keys in source code or committed config           |
| Path Traversal           | `../` sequences, absolute path injection via user input                                |
| Insecure Deserialization | `pickle`, `yaml.load`, Java `ObjectInputStream`, PHP `unserialize` with untrusted data |
| XXE                      | XML parsers with external entity processing enabled                                    |
| Race Condition / TOCTOU  | File existence check followed by use, non-atomic read-modify-write operations          |
| Mass Assignment          | ORM models accepting all fields from request body without allowlist                    |
| Open Redirect            | `redirect(user_input)` without destination validation                                  |
| Clickjacking             | Missing `X-Frame-Options` or CSP `frame-ancestors` on pages with sensitive actions     |

---

## CWE Mapping Table

Map each vulnerability pattern to its CWE. These are used when writing findings.

| Vulnerability Pattern                | CWE ID   | CWE Name                                                                       |
|--------------------------------------|----------|--------------------------------------------------------------------------------|
| SQL Injection                        | CWE-89   | Improper Neutralization of Special Elements used in an SQL Command             |
| Stored XSS                           | CWE-79   | Improper Neutralization of Input During Web Page Generation                    |
| Reflected XSS                        | CWE-79   | Improper Neutralization of Input During Web Page Generation                    |
| OS Command Injection                 | CWE-78   | Improper Neutralization of Special Elements used in an OS Command              |
| Path Traversal                       | CWE-22   | Improper Limitation of a Pathname to a Restricted Directory                    |
| Code Injection / eval()              | CWE-94   | Improper Control of Generation of Code                                         |
| PHP Remote File Inclusion            | CWE-98   | Improper Control of Filename for Include/Require Statement                     |
| Hardcoded Credentials                | CWE-798  | Use of Hard-coded Credentials                                                  |
| Hardcoded Cryptographic Key          | CWE-321  | Use of Hard-coded Cryptographic Key                                            |
| Insecure Deserialization             | CWE-502  | Deserialization of Untrusted Data                                              |
| SSRF                                 | CWE-918  | Server-Side Request Forgery                                                    |
| Vulnerable/Outdated Dependency       | CWE-1395 | Dependency on Vulnerable Third-Party Component                                 |
| Not Failing Securely (fail-open)     | CWE-636  | Not Failing Securely ('Failing Open')                                          |
| Missing Authorization                | CWE-862  | Missing Authorization                                                          |
| Incorrect Authorization              | CWE-863  | Incorrect Authorization                                                        |
| IDOR                                 | CWE-639  | Authorization Bypass Through User-Controlled Key                               |
| Missing Authentication               | CWE-306  | Missing Authentication for Critical Function                                   |
| Weak Password Requirements           | CWE-521  | Weak Password Requirements                                                     |
| Broken Authentication (session)      | CWE-287  | Improper Authentication                                                        |
| Weak Cryptographic Algorithm         | CWE-327  | Use of a Broken or Risky Cryptographic Algorithm                               |
| Weak Hash (MD5/SHA1 for passwords)   | CWE-328  | Use of Weak Hash                                                               |
| Insufficient Randomness              | CWE-330  | Use of Insufficiently Random Values                                            |
| CSRF                                 | CWE-352  | Cross-Site Request Forgery                                                     |
| XXE                                  | CWE-611  | Improper Restriction of XML External Entity Reference                          |
| Open Redirect                        | CWE-601  | URL Redirection to Untrusted Site                                              |
| Unrestricted File Upload             | CWE-434  | Unrestricted Upload of File with Dangerous Type                                |
| Mass Assignment                      | CWE-915  | Improperly Controlled Modification of Dynamically-Determined Object Attributes |
| Race Condition / TOCTOU              | CWE-367  | Time-of-check Time-of-use (TOCTOU) Race Condition                              |
| Information Exposure via Error       | CWE-209  | Generation of Error Message Containing Sensitive Information                   |
| Missing Encryption of Sensitive Data | CWE-311  | Missing Encryption of Sensitive Data                                           |
| Cleartext Storage                    | CWE-312  | Cleartext Storage of Sensitive Information                                     |
| Log Injection                        | CWE-117  | Improper Output Neutralization for Logs                                        |
| Uncontrolled Resource Consumption    | CWE-400  | Uncontrolled Resource Consumption                                              |
| Clickjacking                         | CWE-1021 | Improper Restriction of Rendered UI Layers or Frames                           |
| Sensitive Data Exposure              | CWE-200  | Exposure of Sensitive Information to an Unauthorized Actor                     |
| Missing Input Validation             | CWE-20   | Improper Input Validation                                                      |
| Integer Overflow                     | CWE-190  | Integer Overflow or Wraparound                                                 |
| NULL Pointer Dereference             | CWE-476  | NULL Pointer Dereference                                                       |

---

## Severity Scale

Use CVSS v3.1 conceptual scoring:

| Severity     | CVSS Range | Meaning in practice                                                                          |
|--------------|------------|----------------------------------------------------------------------------------------------|
| **Critical** | ≥ 9.0      | Unauthenticated remote code execution, full data breach, auth bypass — fix immediately       |
| **High**     | 7.0 – 8.9  | Significant data exposure, privilege escalation, SSRF to internal services — fix this sprint |
| **Medium**   | 4.0 – 6.9  | Limited data disclosure, requires authentication or user interaction — fix next sprint       |
| **Low**      | < 4.0      | Defense-in-depth issue, requires chained exploits or unusual conditions                      |

When a CVSS score is not officially available (code-level finding, not a CVE), estimate severity and mark it `(est)`.

---

## Report Template

Use this exact structure for all reports:

```markdown
# Security Audit Report

**Project**: <name>
**Date**: <YYYY-MM-DD>
**Auditor**: security-auditor plugin v<version — read from `.claude-plugin/plugin.json`, never hardcode>
**Mode**: development | production
**Stack**: <languages and frameworks>

> **Disclaimer**: This report is a defensive audit aid generated by static analysis. It may contain false positives and cannot detect all vulnerability classes (race conditions at runtime, logic flaws requiring full app context, etc.). Human review and professional penetration testing are recommended before production deployment.

---

## Executive Summary

<2–4 sentences: what was audited, what was found at the top level, the most critical concern.>

| Severity  | Count |
|-----------|-------|
| Critical  | N     |
| High      | N     |
| Medium    | N     |
| Low       | N     |
| **Total** | N     |

**Top concern**: <one sentence on the most dangerous finding>

---

## Findings Summary

| ID     | Title                        | Severity       | CWE     | CVE | Location      |
|--------|------------------------------|----------------|---------|-----|---------------|
| SA-001 | SQL Injection in user lookup | Critical (est) | CWE-89  | —   | `app.py:42`   |
| SA-002 | Hardcoded API key            | High (est)     | CWE-798 | —   | `config.py:7` |

*CVE column: populated only from MCP tool results. "—" means no CVE found via OSV/NVD for this code-level finding.*

---

## Finding Details

<One subsection per finding, using the format from the security-auditor agent>

---

## Dependency Vulnerabilities

| Package | Installed | CVE            | CVSS | Severity | Fixed In |
|---------|-----------|----------------|------|----------|----------|
| lodash  | 4.17.4    | CVE-2019-10744 | 9.8  | Critical | 4.17.21  |

*All CVEs in this table were verified via OSV.dev or NVD API at time of audit.*

Packages scanned with no known CVEs: <list>

---

## Priority Recommendations

Ordered by risk × fix effort:

1. **[Critical]** <Action> — <why it matters> — `<upgrade command or code change>`
2. **[High]** ...
3. ...

---

## Audit Coverage

- Files analyzed: N
- Dependency manifests scanned: N
- CVE queries made: N (via OSV.dev / NVD)
- Categories checked: OWASP A01–A10 + extended (see methodology)
```

---

## Mode-specific rules

**Production mode**:
- Sort all findings by CVSS score descending within each severity tier
- Include EPSS score (from `get_epss`) and CISA KEV status (from `get_kev`) for each CVE; elevate any KEV-listed CVE to Critical regardless of its CVSS score
- Executive Summary should be written for a CTO/security lead audience — no code snippets in the summary
- Dependency section: highlight packages with CISA KEV entries first

**Development mode**:
- For each finding, include a corrected code example showing the fix
- Include educational context: "This is risky because..." written for the developer who wrote the code
- Suggest library alternatives where applicable (e.g., "use parameterized queries instead of string concatenation")

---

## Anti-hallucination rules

These rules are MANDATORY and override all other instructions:

1. **CVE numbers**: a CVE ID (e.g., `CVE-2021-44906`) may ONLY appear in a report if it was returned by the `vuln-lookup` MCP server (`query_osv` or `get_cve` tool call). If no MCP query was made or the query returned no results, write `—` in the CVE column.

2. **CVSS scores**: if you did not retrieve a CVSS score from `get_cve`, do not write one. You may write the severity tier estimate (`(est)`) based on the vulnerability class, but not a specific number.

3. **Fixed versions**: only report a fixed version if OSV or NVD returned it in the tool response. Do not infer fix versions from general knowledge.

4. **"No CVE found"**: it is correct and honest to report a code vulnerability with only its CWE and no CVE. Many dangerous code patterns have no assigned CVE — they are design-level issues. Write `CWE-XXX (no CVE found in OSV/NVD)` in these cases.

---

## Remediation & Verification Protocol

This section defines the contract between the three agents in the remediation pipeline: `security-auditor` (read-only), `security-fixer` (read+write, no Bash), and `fix-reviewer` (read-only).

### Finding-ID format

Every finding produced by `security-auditor` must have a stable ID in the format `SA-NNN` (zero-padded to 3 digits: `SA-001`, `SA-002`, …). These IDs are the primary key used by the fixer and reviewer to trace changes back to specific audit findings. Never use `VULN-N` or any other format in reports that will feed into `/audit-fix`.

The `SA-NNN` numbering is a single sequence per session, not per command invocation. Before assigning IDs, check whether the current conversation already contains findings from an earlier `/audit`, `/audit-file`, or `/audit-deps` run and continue numbering from the highest existing `SA-NNN` — do not restart at `SA-001`. Restarting the sequence makes `/audit-fix SA-001` ambiguous when multiple files have been audited in the same session.

### Fix Manifest format

After completing all fixes, `security-fixer` outputs a fix manifest. The reviewer reads this manifest to know exactly what changed.

```markdown
## Fix Manifest

| Finding-ID | File           | Lines Changed | Summary                                                         |
|------------|----------------|---------------|-----------------------------------------------------------------|
| SA-001     | `src/db.js`    | 14–16         | Replaced string concatenation with parameterized query (CWE-89) |
| SA-002     | `package.json` | 5             | Bumped lodash 4.17.4 → 4.17.21 (CVE-2019-10744)                 |
| SA-003     | —              | —             | NEEDS HUMAN: auth flow redesign required (CWE-287)              |
```

Every finding in scope must appear — either with a file entry or a `NEEDS HUMAN` note.

### Reviewer verdict values

`fix-reviewer` assigns exactly one of these verdicts per finding-ID:

| Verdict                | Meaning                                                                     |
|------------------------|-----------------------------------------------------------------------------|
| `fixed`                | Root cause eliminated at the CWE level; no bypass identified; no new issues |
| `partially-fixed`      | Reported line was fixed but other paths remain open, or a bypass exists     |
| `not-fixed`            | Change did not close the vulnerability; CWE root cause still present        |
| `introduced-new-issue` | Fix created a new security or functional problem                            |

### One-retry rule

When `/audit-fix` receives a `not-fixed` or `introduced-new-issue` verdict from the reviewer, it sends the finding back to the fixer **exactly once** with the reviewer's evidence as additional context. If the finding still fails after that retry, it is marked `needs-human` and the loop stops. The fixer and reviewer must never loop more than twice per finding.

### Minimal fix principle per CWE

The fixer changes only what is necessary to close the root cause. The following examples define what "correct" and "wrong" look like for the most common CWEs.

---

#### CWE-89 — SQL Injection

Root cause: user-controlled data reaches a SQL query via string concatenation or interpolation.

**✗ Wrong** — escaping the input still leaves the string-building path in place:
```python
# Still wrong: escaping can be bypassed with multi-byte encodings, and the pattern is fragile
query = "SELECT * FROM users WHERE id = '" + conn.escape(user_id) + "'"
```

**✓ Correct** — parameterized query; the database driver never treats user data as SQL:
```python
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

Review check: Grep the entire file for string concatenation into any `execute`/`query` call. A single missed call-site reopens the vulnerability.

---

#### CWE-79 — Cross-Site Scripting (XSS)

Root cause: user-controlled data is inserted into an HTML response without context-appropriate encoding.

**✗ Wrong** — sanitizing at input time; encoding is lost if the value is stored and later used in a different output context:
```javascript
// Wrong: strips tags on input, but stored value may still be dangerous in JS context
const safe = req.body.name.replace(/<[^>]*>/g, '');
db.save({ name: safe });
```

**✓ Correct** — encode at the output layer, in the correct context (HTML body, attribute, JS string, URL):
```javascript
// Correct: encode when rendering, not when receiving
res.send(`<p>${escapeHtml(user.name)}</p>`);
// For JS context: use JSON.stringify or a JS-specific escaper
```

Review check: confirm encoding is applied at every rendering point in the template/response, not just the one that was flagged.

---

#### CWE-78 — OS Command Injection

Root cause: user-controlled data is passed to a shell command interpreter as part of a command string.

**✗ Wrong** — shell=True with string formatting; any shell metacharacter in `filename` breaks the boundary:
```python
# Wrong: shell=True interprets the string as a shell command
subprocess.run(f"convert {filename} output.png", shell=True)
```

**✓ Correct** — pass arguments as a list (no shell expansion) and validate against a strict allowlist:
```python
# Correct: list form bypasses the shell entirely
import re
if not re.fullmatch(r'[a-zA-Z0-9_\-]+\.(jpg|png|gif)', filename):
    raise ValueError("Invalid filename")
subprocess.run(["convert", filename, "output.png"], shell=False)
```

Review check: search for all `subprocess`, `exec`, `system`, `popen` calls in the file. Any that use `shell=True` with user-controlled data are vulnerable regardless of where input validation happens.

---

#### CWE-22 — Path Traversal

Root cause: user-controlled input is joined into a file path without verifying the result stays inside the intended base directory.

**✗ Wrong** — stripping `..` is insufficient; URL encoding (`%2e%2e`), null bytes, or platform-specific separators can bypass it:
```python
# Wrong: simple strip is bypassable
safe_name = user_input.replace("../", "")
path = os.path.join(BASE_DIR, safe_name)
open(path)
```

**✓ Correct** — resolve the canonical absolute path first, then assert it starts with the allowed base:
```python
# Correct: realpath resolves all symlinks and .. segments before the check
resolved = os.path.realpath(os.path.join(BASE_DIR, user_input))
if not resolved.startswith(os.path.realpath(BASE_DIR) + os.sep):
    raise PermissionError("Access denied")
open(resolved)
```

Review check: confirm `realpath`/`resolve` is called on the joined path (not the input alone) and that the prefix check uses the resolved base dir.

---

#### CWE-798 — Hardcoded Credentials

Root cause: a secret value (password, API key, token, private key) is written as a literal string in source code.

**✗ Wrong** — moving the string to a variable does not help if it's still a literal in the same file:
```python
# Still wrong: literal string, just with a different variable name
DATABASE_PASSWORD = "hunter2"
```

**✓ Correct** — read from the environment or a secrets manager at runtime; never store the value in source:
```python
# Correct: value comes from the environment, not source
import os
DATABASE_PASSWORD = os.environ["DATABASE_PASSWORD"]
```

Review check: after the fix, Grep the entire file (and git history if accessible) for the old credential value. It must not appear anywhere. Also verify there is no fallback default (`.get("DATABASE_PASSWORD", "hunter2")` reintroduces the hardcoded secret).

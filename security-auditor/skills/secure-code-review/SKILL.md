---
name: secure-code-review
description: Apply this skill whenever the user runs /audit, /audit-diff, /audit-file, /audit-deps, /audit-report, /audit-fix, /audit-verify, asks to "review code for security", "check for vulnerabilities", "is this code safe", "audit my dependencies", "scan for CVEs", "find security issues", "OWASP audit", or describes security concerns about their codebase. Also apply whenever the security-auditor agent returns findings that need formatting into a report.
---

# Secure Code Review Methodology

This skill provides the checklist, CWE mapping, and report template used by all `security-auditor` commands.

## Additional Resources

- **`references/baseline-suppression.md`** — `.security-audit-baseline.json` format, matching rules, and how to fold suppressions into a report. Read this whenever a project has a baseline file, or when the user asks to suppress/accept a finding.
- **`references/sarif-output.md`** — SARIF 2.1.0 structure, field rules, and severity mapping for `/audit-report --sarif`. Read this only when generating SARIF output.
- **`references/remediation-protocol.md`** — Fix manifest schema, reviewer verdict values, the one-retry rule, and per-CWE minimal-fix examples used by `security-fixer` and `fix-reviewer`. Read this when fixing or verifying findings (`/audit-fix`, `/audit-verify`), not during a plain audit.

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

## Baseline Suppressions

<Only include this section if `.security-audit-baseline.json` exists — see `references/baseline-suppression.md`. Omit entirely if there is no baseline file or nothing matched it.>

N findings matched the baseline file and are not listed above as active findings:

| CWE     | File        | Title             | Approved By      | Date       | Status |
|---------|-------------|-------------------|------------------|------------|--------|
| CWE-798 | `config.py` | Hardcoded API key | jane@company.com | 2026-05-01 | active |

---

## Audit Coverage

- Files analyzed: N
- Dependency manifests scanned: N
- CVE queries made: N (via OSV.dev / NVD)
- Categories checked: OWASP A01–A10 + extended (see methodology)
- Findings suppressed by baseline: N (0 if no baseline file present)
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

This section defines the contract between the three agents in the remediation pipeline: `security-auditor` (read-only), `security-fixer` (read+write, no Bash), and `fix-reviewer` (read-only). The full protocol — fix manifest format, reviewer verdict values, the one-retry rule, and per-CWE minimal-fix examples — lives in `references/remediation-protocol.md`. Read it when fixing or verifying findings (`/audit-fix`, `/audit-verify`), not during a plain audit.

### Finding-ID format

Every finding produced by `security-auditor` must have a stable ID in the format `SA-NNN` (zero-padded to 3 digits: `SA-001`, `SA-002`, …). These IDs are the primary key used by the fixer and reviewer to trace changes back to specific audit findings. Never use `VULN-N` or any other format in reports that will feed into `/audit-fix`.

The `SA-NNN` numbering is a single sequence per session, not per command invocation. Before assigning IDs, check whether the current conversation already contains findings from an earlier `/audit`, `/audit-file`, or `/audit-deps` run and continue numbering from the highest existing `SA-NNN` — do not restart at `SA-001`. Restarting the sequence makes `/audit-fix SA-001` ambiguous when multiple files have been audited in the same session.

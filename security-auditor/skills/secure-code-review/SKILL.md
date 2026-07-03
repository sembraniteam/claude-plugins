---
name: secure-code-review
description: Apply this skill whenever the user runs /audit, /audit-file, /audit-deps, /audit-report, asks to "review code for security", "check for vulnerabilities", "is this code safe", "audit my dependencies", "scan for CVEs", "find security issues", "OWASP audit", or describes security concerns about their codebase. Also apply whenever the security-auditor agent returns findings that need formatting into a report.
---

# Secure Code Review Methodology

This skill provides the checklist, CWE mapping, and report template used by all `security-auditor` commands.

## OWASP Top 10 (2021) Checklist + Extended Categories

Work through each category. Mark each as: ✓ checked, ⚠ findings, or N/A (not applicable to this codebase).

### OWASP Top 10

| #   | Category                                 | Key checks                                                                                     |
|-----|------------------------------------------|------------------------------------------------------------------------------------------------|
| A01 | Broken Access Control                    | Missing authz checks, IDOR, path traversal, CORS misconfiguration, privilege escalation        |
| A02 | Cryptographic Failures                   | Sensitive data in plaintext, weak algorithms, static keys/IVs, missing TLS                     |
| A03 | Injection                                | SQL, NoSQL, OS command, LDAP, XPath, template, expression language                             |
| A04 | Insecure Design                          | Missing rate limiting, insecure direct object references in design, trust boundary violations  |
| A05 | Security Misconfiguration                | Default credentials, unnecessary features enabled, verbose errors, missing security headers    |
| A06 | Vulnerable & Outdated Components         | Dependencies with known CVEs (verified via MCP, never from memory)                             |
| A07 | Identification & Authentication Failures | Weak passwords, missing MFA support, insecure session management, credential stuffing exposure |
| A08 | Software & Data Integrity Failures       | Unsigned updates/plugins, insecure deserialization, CI/CD pipeline compromise                  |
| A09 | Logging & Monitoring Failures            | No audit trail for sensitive ops, PII logged, log injection                                    |
| A10 | SSRF                                     | Outbound HTTP with user-controlled URL, missing allowlist, cloud metadata endpoint exposure    |

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
**Auditor**: security-auditor plugin v0.1.0
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
| VULN-1 | SQL Injection in user lookup | Critical (est) | CWE-89  | —   | `app.py:42`   |
| VULN-2 | Hardcoded API key            | High (est)     | CWE-798 | —   | `config.py:7` |

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
- Include EPSS score and CISA KEV status if returned by the MCP `get_cve` tool
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

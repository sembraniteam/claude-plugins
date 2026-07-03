---
description: Run a deep security audit on a single file, mapping every finding to its CWE ID and providing line-level evidence.
---

You are running a focused, line-level security audit on a single file using the `security-auditor` plugin.

The target file is: `$ARGUMENTS`

If no file path was provided, ask: "Which file should I audit? Please provide the path."

## Step 1 — Read and understand the file

Read the file at the provided path. Identify:
- File type (language, framework role: controller, model, service, config, etc.)
- What kind of input does this file receive? (HTTP params, database results, file system, IPC, etc.)
- What outputs or effects does it produce? (HTTP response, DB writes, file writes, shell execution, etc.)

## Step 2 — Trace data flows

For each external input source, trace the data path through the file to all potential sinks:
- **Dangerous sinks**: SQL query construction, shell execution, file path assembly, template rendering, eval/exec, deserialization, HTTP response body, redirect target
- **Intermediate transformations**: note which ones sanitize/validate and which do not

## Step 3 — Check each vulnerability category

Work through the OWASP Top 10 + extended checklist from the `secure-code-review` skill, applied specifically to this file:

1. Injection (SQL, NoSQL, OS, LDAP, template) — trace every DB call and exec
2. Broken access control — does the file enforce authorization before sensitive operations?
3. Cryptographic failures — hash algorithms, encryption schemes, IV/salt handling
4. Security misconfiguration — debug flags, verbose error messages, permissive CORS
5. Vulnerable components — any `import`/`require`/`use` of third-party libraries? Flag for CVE check
6. Authentication failures — session handling, token validation, password checks
7. Injection via deserialization — `pickle`, `yaml.load`, `JSON.parse` with `__proto__`
8. SSRF — any outbound HTTP calls with user-controlled URLs
9. Hardcoded secrets — API keys, passwords, tokens inline in source
10. Path traversal — file path construction with user input

## Step 4 — Format findings

For EACH finding, output:

```
### [SA-NNN] <Title>

- **CWE**: CWE-XXX — <CWE Name>
- **Severity**: Critical / High / Medium / Low (estimated, see CVSS note in skill)
- **Line**: <file_path>:<line_number>
- **Status**: confirmed | needs-review

**Evidence**:
```<language>
<code snippet — the exact vulnerable line(s), 3–5 lines of context>
```

**Why this is dangerous**: <explanation of the attack vector and impact>

**Remediation**: <concrete fix, with code example>
```

If you found a third-party library used in this file that you suspect has a CVE, note: "Flag for CVE check: `<library>@<version>` — run `/audit-deps` for full scan."

## Step 5 — Summary

End with a one-paragraph summary: how many confirmed findings, how many needs-review, the highest severity, and the top recommendation.

> To automatically fix findings from this report, run `/audit-fix` (or `/audit-fix SA-001` for a specific finding).

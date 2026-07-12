---
description: Run a comprehensive security audit of the current codebase, covering OWASP Top 10, CWE mapping, and dependency CVE verification via NVD/OSV.
---

You are running a full security audit using the `security-auditor` plugin. Follow these steps in order.

## Step 1 — Determine audit mode

Check if `$ARGUMENTS` contains a mode hint:
- `dev` or `development` → development mode
- `prod` or `production` → production mode

If no mode is specified, ask the user:

> "Is this project currently in **development** or **production**?
>
> - **development**: verbose output, concrete fix suggestions per finding
> - **production**: prioritized by exploitability (CVSS + KEV/EPSS where available), executive-ready"

Store the mode and continue once confirmed.

## Step 2 — Map project structure

Use Read, Glob, and Grep to build a project map:

1. **Language & framework detection**: scan for `package.json`, `requirements.txt`, `go.mod`, `pom.xml`, `Cargo.toml`, `composer.json`, `Gemfile`, `build.gradle`, `*.csproj` — identify the primary stack.
2. **Entry points**: locate routes/controllers, input handlers (form submissions, API request bodies, URL params, file uploads), database query files, auth/session files, config files.
3. **Dependency manifests**: collect ALL manifest files found — you will query CVEs for each in Step 4.
4. **Secrets surface**: scan for `.env` files, config files with credentials patterns, any hardcoded strings resembling keys/passwords.

Summarize the map to the user before proceeding: "Scanning a [framework] project — found [N] entry points, [N] dependency manifests. Starting code analysis."

## Step 3 — Code analysis via subagent

Check this session for findings from an earlier `/audit`, `/audit-file`, or `/audit-deps` run. The `security-auditor` agent has a fresh context and cannot see them itself, so determine the next unused `SA-NNN` (or `SA-001` if none exist yet) before spawning it.

Spawn the `security-auditor` agent to perform a read-only structural analysis of the codebase. Pass it:
- The project root path
- The project map from Step 2 (entry points, auth files, DB query files)
- The audit mode (dev/prod)
- The starting `SA-NNN` number determined above

Wait for the agent to return its findings before proceeding.

## Step 4 — Dependency CVE verification via MCP

For each dependency manifest found in Step 2, query the `vuln-lookup` MCP server.

After collecting CVE IDs from OSV/NVD, enrich each one with exploitability signals:
- Call `get_epss(cve_id)` — returns the probability of exploitation in the next 30 days (FIRST.org EPSS). Scores above ~0.10 (10%) indicate elevated real-world risk.
- Call `get_kev(cve_id)` — checks the CISA Known Exploited Vulnerabilities catalog. Any CVE in KEV has **confirmed active exploitation** and must be treated as Critical regardless of its CVSS score.

Run these calls in parallel with each other (they hit independent APIs). Record the results for use in Step 5.

**npm (`package.json` / `package-lock.json`)**:
- Parse each dependency and its pinned version
- For each: call `query_osv(ecosystem="npm", package=name, version=version)`
- If OSV returns CVEs, also call `get_cve(cve_id)` on each CVE ID for full CVSS details

**Python (`requirements.txt` / `Pipfile.lock` / `pyproject.toml`)**:
- Use ecosystem `"PyPI"` with `query_osv`

**Go (`go.sum` / `go.mod`)**:
- Use ecosystem `"Go"`

**Maven (`pom.xml`)**:
- Use ecosystem `"Maven"`, package format: `groupId:artifactId`

**Rust (`Cargo.lock`)**:
- Use ecosystem `"crates.io"`

**PHP (`composer.lock`)**:
- Use ecosystem `"Packagist"`

**Ruby (`Gemfile.lock`)**:
- Use ecosystem `"RubyGems"`

**C#/.NET (`packages.config` / `*.nuspec` / `*.csproj` with `<PackageReference>` entries)**:
- Use ecosystem `"NuGet"`, package name is the `id` attribute (packages.config) or `Include` attribute (PackageReference)

> RULE: Never report a CVE number that was not returned by a tool call. If no CVE is found for a package, write "no known CVE in OSV" in the report.

## Step 5 — Generate security report

Apply the `secure-code-review` skill to compile and format the final report.

In **production mode**: sort all findings by CVSS score descending; group Critical/High at the top. Include EPSS score and CISA KEV status from the `get_epss` and `get_kev` tool results. Elevate any KEV-listed CVE to Critical priority regardless of CVSS.

In **development mode**: for each finding, include a concrete code fix example. Verbose is good here.

Output the full report in the chat. If the user runs `/audit-report` afterwards, they can regenerate it as a standalone `SECURITY-AUDIT.md` file.

> To automatically fix findings from this report, run `/audit-fix` (or `/audit-fix SA-001` for a specific finding).

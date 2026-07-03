---
description: Scan all dependency manifests in the current project against OSV.dev and NVD, and output a CVE table with severity and fix versions.
---

You are scanning project dependencies for known CVEs using the `security-auditor` plugin's `vuln-lookup` MCP server.

## Step 1 — Discover all manifest files

Search the project for dependency manifests:
- `package.json`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml` (npm/Node)
- `requirements.txt`, `Pipfile`, `Pipfile.lock`, `pyproject.toml`, `poetry.lock` (Python)
- `go.mod`, `go.sum` (Go)
- `pom.xml`, `build.gradle`, `build.gradle.kts` (Java/Kotlin)
- `Cargo.toml`, `Cargo.lock` (Rust)
- `composer.json`, `composer.lock` (PHP)
- `Gemfile`, `Gemfile.lock` (Ruby)
- `*.csproj`, `packages.config`, `*.nuspec` (C#/.NET)

List the manifests found before proceeding.

## Step 2 — Extract pinned versions

For each manifest:
- Parse the exact version currently installed (from the lockfile if available — lockfiles have the real pinned version, unlike `package.json` ranges)
- Build a list of `(ecosystem, package_name, version)` tuples

## Step 3 — Query OSV.dev for each package

For each `(ecosystem, package, version)`:
1. Call `query_osv(ecosystem=..., package=..., version=...)` via the `vuln-lookup` MCP server
2. If OSV returns vulnerabilities with CVE aliases, call `get_cve(cve_id)` on each to get CVSS score and severity from NVD

> RULE: Never write a CVE number that was not returned by one of these MCP tool calls. If OSV returns no results, the row in the output table shows "None found".

## Step 4 — Output the results table

For each package that has at least one CVE, output a row:

```
| Package | Installed | CVE | CVSS | Severity | Fixed In |
|---------|-----------|-----|------|----------|----------|
| lodash  | 4.17.4    | CVE-2019-10744 | 9.8 | Critical | 4.17.21 |
```

After the table with vulnerable packages, add a short section:

**Clean packages** (no CVEs found): list them in a compact format, e.g., `express@5.0.1 ✓, helmet@7.1.0 ✓`.

## Step 5 — Priority recommendation

List the top 3 most urgent updates based on CVSS score, with the exact upgrade command:

```
1. lodash 4.17.4 → 4.17.21  (CVE-2019-10744, CVSS 9.8)
   npm install lodash@4.17.21

2. ...
```

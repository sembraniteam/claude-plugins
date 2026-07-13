# SARIF Output

[SARIF](https://sarifweb.azurewebsites.net/) (Static Analysis Results Interchange Format) 2.1.0 is the format
GitHub code scanning, Azure DevOps, and most CI security dashboards ingest. Emitting it lets findings from
this plugin show up as annotations on the diff in a PR, alongside Semgrep/CodeQL results, instead of living
only in a markdown file nobody opens.

SARIF output is optional and generated only when explicitly requested (`/audit-report --sarif`) — it is a
secondary, machine-readable view of the same findings already in the markdown report, not a replacement for
the human-readable report.

## When to generate it

`/audit-report --sarif` generates both `SECURITY-AUDIT.md` and `SECURITY-AUDIT.sarif.json` from the same set
of session findings. Do not generate SARIF from `/audit` or `/audit-diff` directly — always route through
`/audit-report` so there is exactly one place that turns in-session findings into on-disk artifacts.

## Structure

Build the file directly as JSON — do not attempt to parse the markdown report back into structured data, the
findings are already structured in the conversation. One `run`, one `driver` (this plugin), one `result` per
active (non-suppressed) finding.

```json
{
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "security-auditor",
          "version": "0.8.0",
          "informationUri": "https://github.com/sembraniteam/claude-plugins",
          "rules": [
            {
              "id": "CWE-89",
              "name": "SQLInjection",
              "shortDescription": { "text": "Improper Neutralization of Special Elements used in an SQL Command" },
              "helpUri": "https://cwe.mitre.org/data/definitions/89.html",
              "properties": { "tags": ["security", "cwe-89"] }
            }
          ]
        }
      },
      "results": [
        {
          "ruleId": "CWE-89",
          "ruleIndex": 0,
          "level": "error",
          "message": { "text": "SA-001: SQL Injection in user lookup — user-controlled `id` reaches a query via string concatenation." },
          "locations": [
            {
              "physicalLocation": {
                "artifactLocation": { "uri": "api/users.py" },
                "region": { "startLine": 42 }
              }
            }
          ],
          "properties": { "security-severity": "9.8", "finding-id": "SA-001" }
        }
      ]
    }
  ]
}
```

## Field-by-field rules

- **`driver.version`**: read from `.claude-plugin/plugin.json`, same rule as the markdown report header — never hardcode.
- **`rules`**: one entry per distinct CWE ID that appears in the findings for this run, deduplicated. `id` is always the CWE ID (e.g. `CWE-89`), matching the CWE Mapping Table in `SKILL.md`. `helpUri` is always `https://cwe.mitre.org/data/definitions/<N>.html` where `<N>` is the numeric part of the CWE ID.
- **`results`**: one entry per **active** finding (findings suppressed by the baseline file are excluded from `results` entirely — SARIF has no concept of "known, accepted" the way the markdown report's Baseline Suppressions table does, so including them would just reintroduce the noise the baseline file exists to remove).
- **`message.text`**: prefix with the finding's `SA-NNN` ID so it stays traceable back to the markdown report and the fixer/reviewer pipeline.
- **`locations`**: `artifactLocation.uri` must be relative to the repository root (not absolute filesystem paths) — GitHub code scanning requires this to render inline annotations. `region.startLine` is required; add `region.endLine` if the finding spans multiple lines.
- **`properties.security-severity`**: the CVSS score as a string if one was retrieved via `get_cve`; omit this property entirely for code-level findings with no CVE (do not invent a score — same anti-hallucination rule as the markdown report).
- **`properties.finding-id`**: always include the `SA-NNN` ID here so CI tooling or a human can cross-reference back to `SECURITY-AUDIT.md`.

## Severity mapping

SARIF's `level` is one of `error`, `warning`, `note`, `none`. Map from this plugin's severity tiers:

| Plugin severity | SARIF `level` |
|-----------------|---------------|
| Critical        | `error`       |
| High            | `error`       |
| Medium          | `warning`     |
| Low             | `note`        |

## Anti-hallucination rule (applies here too)

The same rule from the main anti-hallucination section applies to SARIF generation: a `security-severity`
value or a CVE reference in `message.text` may only appear if it came from an MCP tool call in this session.
Do not backfill a CVSS-shaped number just to populate `security-severity` — omit the property instead.

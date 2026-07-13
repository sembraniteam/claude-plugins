# Baseline / Suppression File

Without a baseline, every finding a team has already reviewed and accepted (a known false positive, a
compensating control that isn't visible in the code, a risk formally accepted with a deadline) reappears on
every subsequent `/audit` or `/audit-diff` run. Teams stop reading reports that repeat the same noise every
week. The baseline file exists to make "already reviewed" a durable, auditable decision instead of something
a human has to re-derive from memory on every run.

## File location and format

Path: `.security-audit-baseline.json` in the project root. JSON, not YAML — deterministic to parse with no
indentation ambiguity.

```json
{
  "version": 1,
  "suppressions": [
    {
      "cwe": "CWE-798",
      "file": "config/legacy_loader.py",
      "title": "Hardcoded Credentials",
      "reason": "Legacy system scheduled for decommission Q3 2026; credential rotated and scoped to a read-only replica",
      "approved_by": "jane@company.com",
      "date": "2026-05-01",
      "expires": "2026-10-01"
    }
  ]
}
```

| Field         | Required | Meaning                                                                                                                                                                                     |
|---------------|----------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `cwe`         | yes      | The CWE ID of the suppressed finding (e.g. `CWE-798`)                                                                                                                                       |
| `file`        | yes      | Path to the file, relative to project root                                                                                                                                                  |
| `title`       | yes      | Short finding title, used as a secondary match key when line numbers drift                                                                                                                  |
| `reason`      | yes      | Why this is accepted risk, not a fix — required so suppressions are auditable, not silent                                                                                                   |
| `approved_by` | yes      | Who accepted the risk — a suppression with no owner is not a decision, it's a thing nobody reviewed                                                                                         |
| `date`        | yes      | When it was added, `YYYY-MM-DD`                                                                                                                                                             |
| `expires`     | no       | Optional `YYYY-MM-DD`. If present and in the past, treat the suppression as **stale**: still list it as suppressed but flag it for re-review in the report rather than silently dropping it |

If the file does not exist, treat the project as having zero suppressions — do not create it automatically,
and do not fail the audit. Read it once per audit run.

## Matching rule

Match a live finding against a baseline entry by `(file, cwe, title)` — **not** by line number. Code shifts
constantly; matching on line number would make every baseline entry expire the moment an unrelated line is
added above it, which defeats the purpose. This means a suppression stays valid as the surrounding file
changes, as long as the same vulnerability class in the same file with the same title is still present.

Do not fuzzy-match `title` — require an exact string match against the `title` field. A loose match risks
silently suppressing a different, unrelated finding that happens to share a CWE and file.

## Applying suppressions in a report

After `security-auditor` returns findings and before the report is generated:

1. Read `.security-audit-baseline.json` (skip this step entirely if the file doesn't exist).
2. For each finding, check for a matching suppression entry. If matched and not expired, remove it from the
   `Findings Summary` / `Finding Details` sections that would otherwise report it as active.
3. Add a **Baseline Suppressions** section to the report (below Audit Coverage) listing what was suppressed
   and why, so suppression stays visible even though the finding isn't re-flagged:

```markdown
## Baseline Suppressions

N findings matched `.security-audit-baseline.json` and are not listed above as active findings:

| CWE     | File                      | Title                 | Approved By      | Date       | Status                      |
|---------|---------------------------|-----------------------|------------------|------------|-----------------------------|
| CWE-798 | `config/legacy_loader.py` | Hardcoded Credentials | jane@company.com | 2026-05-01 | active (expires 2026-10-01) |
```

4. If a suppression's `expires` date has passed, mark its `Status` column `EXPIRED — recommend re-review` and
   still show it in this table — never silently re-suppress an expired entry without flagging it. Whether an
   expired entry should re-appear as an active finding or stay suppressed pending re-approval is a judgment
   call: default to re-flagging it as active (safer) and note in the finding that it was previously accepted
   under an expired suppression.
5. Update the `Audit Coverage` section's finding count to reflect only active (non-suppressed) findings, and
   add a line: `Findings suppressed by baseline: N`.

## Adding entries to the baseline

There is no dedicated command for this — it is a deliberate, low-frequency, human-reviewed action, not
something that should happen as a side effect of running an audit. After presenting a report, if the user
says something like "accept SA-003 as risk" or "suppress SA-003, reason: rotated key, expires in 90 days":

1. Confirm the CWE, file, and title from the finding with `SA-003`'s ID in the current report.
2. Ask for (or infer from the conversation) `reason`, `approved_by` (default to the current git user via
   `git config user.email` if not stated), and optionally `expires`.
3. Read the existing baseline file (or start a fresh `{"version": 1, "suppressions": []}` object if it
   doesn't exist yet), append the new entry, and write the file back with `Write`/`Edit`.
4. Confirm what was added and note that future audits will no longer list this finding as active.

Never add a suppression without an explicit, in-conversation user request — suppressing a finding is a risk
acceptance decision, not something to infer from silence.

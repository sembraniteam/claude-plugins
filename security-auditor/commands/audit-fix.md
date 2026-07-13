---
description: Apply verified fixes to security findings from an existing audit report. Shows a fix plan per finding, waits for confirmation, applies minimal changes, then automatically runs independent verification. Use /audit-fix all to fix everything, or /audit-fix SA-001 to target a specific finding.
---

You are running `/audit-fix` to remediate security findings with verified, minimal code changes.

**Important**: fixes are never applied automatically. This command always shows a plan before writing any file, and runs independent verification after.

## Step 0 — Validate audit report exists

Before anything else, check whether an audit report is available:
- Does this session contain `/audit`, `/audit-diff`, or `/audit-file` output with a findings list?
- Does a `SECURITY-AUDIT.md` file exist in the current directory?

If neither is found, stop and say:

> "No audit report found. Please run `/audit` (or `/audit-diff` for a PR-scoped scan) first to generate a security findings list, then run `/audit-fix` again."

## Step 1 — Parse scope from `$ARGUMENTS`

Determine what to fix:
- Empty or `all` → all findings from the audit report
- A single finding-ID (e.g., `SA-001`) → only that finding
- A comma-separated list (e.g., `SA-001,SA-003`) → only those findings
- A severity tier (e.g., `critical`, `high`) → all findings of that severity

## Step 2 — Display scope and confirm with user

List the findings in scope, grouped by category:

```
**In scope for /audit-fix:**

Fixable findings (security-fixer will handle these):
  SA-001 [Critical] SQL Injection in user lookup — src/db.js:14
  SA-002 [High] Hardcoded API key — config.js:7

Potentially needs-human (fixer will confirm before skipping):
  SA-003 [High] Auth session flow — may require architectural decision
```

Ask: "Should I proceed? The fixer will show a plan for each finding before writing anything. Reply 'yes' to confirm, or 'yes, fix all without asking per item' to skip per-finding plan confirmations."

Wait for the user's reply before proceeding.

## Step 3 — Delegate to security-fixer

Spawn the `security-fixer` agent with:
- The audit report content (from this session or `SECURITY-AUDIT.md`)
- The finding-IDs in scope
- The user's batch approval preference (per-item confirmation or batch mode)

The fixer will work through findings one by one: show plan → wait for approval (unless batch) → apply change → move to next. Wait for the fixer to return its complete fix manifest before proceeding.

## Step 4 — Auto-verify with fix-reviewer

Immediately after receiving the fix manifest, spawn the `fix-reviewer` agent — the user does not need to trigger this separately.

Say to the user: "Fixes applied. Running independent verification now..."

Pass the fix-reviewer:
- The original audit report
- The fix manifest from Step 3
- Instruction to read the current state of all changed files

Wait for the reviewer to return all verdicts before proceeding.

## Step 5 — Handle failed verdicts

For each finding where the reviewer returned `not-fixed` or `introduced-new-issue`:

1. Tell the user: "SA-NNN verdict: `not-fixed` — sending back to fixer for one retry. (Reviewer note: <reviewer's explanation>)"
2. Spawn `security-fixer` again for that specific finding only, passing the reviewer's verdict and evidence as additional context so the fixer knows what went wrong.
3. After the retry, spawn `fix-reviewer` again for that specific finding only.
4. If the retry verdict is still `not-fixed` or `introduced-new-issue`: **stop the loop for this finding**. Mark it `needs-human`. Do NOT retry again.

**Maximum retries per finding: 1.** After one failed retry, escalate to the user.

## Step 6 — Final summary

Output the closing summary:

```markdown
## /audit-fix Summary

### Fixed & Verified ✅
- SA-001 — SQL Injection in user lookup → `src/db.js:14–16` patched (CWE-89)
- SA-002 — Hardcoded API key → `config.js:7` replaced with env var (CWE-798)

### Needs Human Review ⚠️
- SA-003 — Auth session flow: fixer correctly deferred (requires architectural decision)
- SA-004 — XSS in template renderer: auto-fix failed after 1 retry (reviewer found bypass via double-encoding); manual fix recommended

### Next Steps for You
1. Run `npm install` — dependency version was updated in `package.json`
2. Run your test suite, especially paths that touch fixed findings
3. Test SA-001 manually: try `?id=' OR 1=1 --` on the user lookup endpoint
4. Commit each finding's fix in a separate commit for clean rollback ability
5. Run `/audit` again after committing to confirm the full report is clean
```

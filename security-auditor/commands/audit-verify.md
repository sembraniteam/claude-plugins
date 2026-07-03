---
description: Run the fix-reviewer agent independently against existing fixes — useful when you fixed vulnerabilities manually, made additional edits after /audit-fix, or want a second-opinion verification before committing. Works with any fix, not just ones from /audit-fix.
---

You are running `/audit-verify` to independently verify security fixes without running the fixer again.

## Step 1 — Gather inputs

### Audit report

Check for an audit report in this order:
1. `/audit` or `/audit-file` output in this session
2. A `SECURITY-AUDIT.md` file in the current directory

If no audit report is found, say:
> "No audit report found. Please point me to the original audit report file, or run `/audit` first to generate one."

### Fix manifest

Check for a fix manifest from a previous `/audit-fix` run in this session.

If there is no manifest, ask:
> "No fix manifest found from a previous `/audit-fix` run. Please describe which findings you've fixed and which files were changed (e.g., 'I manually fixed SA-001 in src/db.js and SA-002 in package.json'), and I'll verify those."

Accept the user's description and construct an informal manifest from it:

```markdown
## Fix Manifest (user-provided)

| Finding-ID | File           | Lines Changed  | Summary                          |
|------------|----------------|----------------|----------------------------------|
| SA-001     | `src/db.js`    | user-specified | Manual fix — parameterized query |
| SA-002     | `package.json` | user-specified | Manual version bump              |
```

## Step 2 — Run fix-reviewer

Spawn the `fix-reviewer` agent with:
- The audit report (from session or `SECURITY-AUDIT.md`)
- The fix manifest (from session, file, or constructed from user's description)
- Instruction to read the current state of all relevant files

Say: "Running independent verification of your fixes..."

## Step 3 — Present results

Present the reviewer's full output to the user — all verdict blocks, the summary table, and the next-steps section. Do not filter or summarize.

After the reviewer's output, add:

> "To target any remaining `partially-fixed` or `not-fixed` findings, run `/audit-fix SA-NNN` for each one. If you fix them manually, run `/audit-verify` again."

# Remediation & Verification Protocol

This defines the contract between `security-fixer` (read+write, no Bash) and `fix-reviewer` (read-only) — the
two agents `/audit-fix` and `/audit-verify` delegate to. Read this when fixing or verifying findings, not
during a plain `/audit`/`/audit-file`/`/audit-deps` run. `security-fixer.md` and `fix-reviewer.md` carry their
own operative copies of this contract (agents run with fresh context and can't rely on skill triggering); this
file is the canonical reference — if either agent's inline copy diverges from this file, this file wins.

## Fix Manifest format

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

## Reviewer verdict values

`fix-reviewer` assigns exactly one of these verdicts per finding-ID:

| Verdict                | Meaning                                                                     |
|------------------------|-----------------------------------------------------------------------------|
| `fixed`                | Root cause eliminated at the CWE level; no bypass identified; no new issues |
| `partially-fixed`      | Reported line was fixed but other paths remain open, or a bypass exists     |
| `not-fixed`            | Change did not close the vulnerability; CWE root cause still present        |
| `introduced-new-issue` | Fix created a new security or functional problem                            |

## One-retry rule

When `/audit-fix` receives a `not-fixed` or `introduced-new-issue` verdict from the reviewer, it sends the finding back to the fixer **exactly once** with the reviewer's evidence as additional context. If the finding still fails after that retry, it is marked `needs-human` and the loop stops. The fixer and reviewer must never loop more than twice per finding.

## Minimal fix principle per CWE

The fixer changes only what is necessary to close the root cause. The following examples define what "correct" and "wrong" look like for the most common CWEs.

---

### CWE-89 — SQL Injection

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

### CWE-79 — Cross-Site Scripting (XSS)

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

### CWE-78 — OS Command Injection

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

### CWE-22 — Path Traversal

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

### CWE-798 — Hardcoded Credentials

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

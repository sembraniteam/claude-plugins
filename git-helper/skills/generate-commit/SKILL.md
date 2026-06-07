---
name: generate-commit
description: This skill should be used when the user invokes /git-helper:generate-commit, or asks to "generate a commit message", "write a commit for me", "what should my commit message be", "help me commit my changes", "suggest a commit message", "prepare a commit", "what commit type should I use", or "stage and commit my changes". Produces a conventional commit with type, scope, subject, optional body, and breaking change footer.
argument-hint: "[file1 file2 ...]"
allowed-tools: ["Bash", "AskUserQuestion", "Skill"]
license: MIT
---

# Generate Commit Message

Generate a conventional commit message by analyzing the current git context. Gather user intent first, then analyze and generate, execute confirmed actions, and display a final summary.

## Pre-flight Questions

Before running any git commands, collect user intent using `AskUserQuestion` in up to two rounds.

**Round 1 — call `AskUserQuestion` with both questions in a single call.**

The "Stage files" options depend on whether file paths were provided by the user.

*If files were provided:*

```json
{
  "questions": [
    {
      "question": "Do you want to create a new branch for this commit?",
      "header": "New branch",
      "multiSelect": false,
      "options": [
        { "label": "Yes", "description": "Generate a branch name and optionally check it out" },
        { "label": "No",  "description": "Stay on the current branch" }
      ]
    },
    {
      "question": "Which files should be staged before committing?",
      "header": "Stage files",
      "multiSelect": false,
      "options": [
        { "label": "Yes — all",            "description": "git add --all" },
        { "label": "Yes — provided files", "description": "git add <the provided files>" },
        { "label": "No",                   "description": "Skip staging" }
      ]
    }
  ]
}
```

*If no files were provided (users can select "Other" to specify custom paths):*

```json
{
  "questions": [
    {
      "question": "Do you want to create a new branch for this commit?",
      "header": "New branch",
      "multiSelect": false,
      "options": [
        { "label": "Yes", "description": "Generate a branch name and optionally check it out" },
        { "label": "No",  "description": "Stay on the current branch" }
      ]
    },
    {
      "question": "Which files should be staged before committing?",
      "header": "Stage files",
      "multiSelect": false,
      "options": [
        { "label": "Yes — all", "description": "git add --all" },
        { "label": "No",        "description": "Skip staging" }
      ]
    }
  ]
}
```

Evaluate which follow-up questions are needed:
- If **New branch = Yes** → include the Checkout question
- If **Stage files ≠ No** → include the Auto-commit question

**Round 2 — if either condition is met, call `AskUserQuestion` with the applicable questions together.** Skip Round 2 entirely if neither applies.

```json
{
  "questions": [
    {
      "question": "After generating the branch name, run `git checkout -b <branch>` automatically?",
      "header": "Checkout",
      "multiSelect": false,
      "options": [
        { "label": "Yes", "description": "Switch to the new branch immediately" },
        { "label": "No",  "description": "Just show the branch name to copy" }
      ]
    },
    {
      "question": "After generating the commit message, run `git commit -m \"...\"` automatically?",
      "header": "Auto-commit",
      "multiSelect": false,
      "options": [
        { "label": "Yes", "description": "Commit will be created automatically" },
        { "label": "No",  "description": "Just display the command to run manually" }
      ]
    }
  ]
}
```

After all answers, display a confirmation to the user:

> **Your selections:**
> - New branch: Yes / No
> - Stage files: Yes (`git add <files>`) / No
> - Checkout branch: Yes / No / N/A
> - Execute commit: Yes / No / N/A

## Analysis & Generation

**Collect git context** — run the context script with any user-supplied file paths:

```bash
bash "$CLAUDE_PLUGIN_ROOT/scripts/collect-context.sh"
# with files:
bash "$CLAUDE_PLUGIN_ROOT/scripts/collect-context.sh" "src/auth/login.ts" "src/auth/logout.ts"
```

If both diffs are empty and status shows no changes, inform the user and stop.

**Determine commit fields** from the diff (staged = primary signal, unstaged = secondary):

| Field        | How to determine                                                                                                                                                 |
|--------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Type**     | Select one type from the table below. `feat`/`fix` take priority over `refactor` when in doubt.                                                                  |
| **Scope**    | Infer from changed file paths (e.g., `auth` from `src/auth/`). Omit if cross-cutting or uninferable. Lowercase, no spaces.                                       |
| **Breaking** | Yes if: public API/signature removed or incompatibly changed; env var/config key renamed/removed; DB schema requires migration; diff contains `BREAKING CHANGE`. |
| **Subject**  | `<type>[(<scope>)][!]: <description>` — imperative mood, lowercase first letter, no period, max 72 chars.                                                        |
| **Body**     | Include when change is non-obvious or breaking. Blank line after subject, wrap at 72 chars.                                                                      |
| **Footer**   | If breaking: `BREAKING CHANGE: <what broke and how to migrate>`. Add `Co-Authored-By` only if the user explicitly requests it.                                   |

**Commit type table:**

| Type       | When to use                           |
|------------|---------------------------------------|
| `feat`     | New user-facing feature               |
| `fix`      | User-facing bug fix                   |
| `docs`     | Documentation only                    |
| `refactor` | Code restructured, no behavior change |
| `test`     | Tests only, no production code        |
| `chore`    | Non-production maintenance            |
| `ci`       | CI/CD config changes                  |
| `perf`     | Performance improvement               |
| `revert`   | Reverting a previous commit           |
| `bump`     | Dependency version update             |

**Edge cases:**
- Empty staged diff: base type on unstaged diff, note user should stage first; still generate the message.
- Whitespace/formatting only: use `refactor`.
- Merge commit: `chore: merge <branch>` unless it introduces a feature/fix.
- Revert: `revert: revert "<original subject>"` with commit hash in body.

## Output & Execution

Display the final commit message in a code block, then show the ready-to-run command:

- **Subject only** — use the inline form: `git commit -m "feat(auth): add OAuth2 login support"`
- **With body or BREAKING CHANGE footer** — use the heredoc form:

```bash
git commit -m "$(cat <<'EOF'
feat(auth): add OAuth2 login support

Allow users to authenticate via Google and GitHub OAuth2 providers.
Token storage uses existing session infrastructure.

BREAKING CHANGE: removed /api/v1/auth/basic endpoint. Use /api/v2/auth instead.
EOF
)"
```

Execute confirmed actions in order, showing output for each:

1. **Stage files** — `git add <files>` or `git add --all`
2. **Generate branch name** — invoke `git-helper:generate-branch` via Skill tool, passing the commit subject as work description. Do not ask for a description again.
3. **Checkout branch** — `git checkout -b <generated-branch-name>`
4. **Execute commit** — run the commit command using subject + body + BREAKING CHANGE footer. Add `Co-Authored-By` trailer only if the user explicitly requested it.

If no actions were confirmed, inform the user the message is ready to use manually.

## Summary

After completing all actions, display a summary block:

| Field               | Value                                                            | Reason                                              |
|---------------------|------------------------------------------------------------------|-----------------------------------------------------|
| **Type**            | `feat`                                                           | Why this type was selected                          |
| **Scope**           | `auth` *(omit row if no scope)*                                  | Where the changes were inferred from                |
| **Commit message**  | `feat(auth): add OAuth2 login support`                           | N/A                                                 |
| **Breaking change** | Yes / No                                                         | What triggered the flag, or N/A if not breaking     |
| **Branch**          | `feature/add-oauth2-login` *(omit row if no branch was created)* | N/A                                                 |

## Additional Resources

- **`references/commit-types.md`** — Detailed type selection guide with examples for ambiguous cases

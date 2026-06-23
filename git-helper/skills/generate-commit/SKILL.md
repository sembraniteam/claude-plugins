---
name: generate-commit
description: This skill should be used when the user invokes /git-helper:generate-commit, or asks to "generate a commit message", "write a commit for me", "what should my commit message be", "help me commit my changes", "suggest a commit message", "prepare a commit", "what commit type should I use", "stage and commit my changes", "commit all my changes", or describes a change they just made and needs a commit message for it. Produces a conventional commit with type, scope, subject, optional body, and breaking change footer.
argument-hint: "[file1 file2 ...]"
allowed-tools: ["Bash", "AskUserQuestion", "Skill"]
---

# Generate Commit Message

Generate a conventional commit message by analyzing the current git context. Gather user intent first, then analyze and generate, execute confirmed actions, and display a final summary.

## Pre-flight Questions

Before running any git commands, collect user intent using `AskUserQuestion` in up to two rounds.

**Round 1** — ask both questions in a single call:
- **New branch**: "Do you want to create a new branch for this commit?" (Yes / No)
- **Stage files**: "Which files should be staged before committing?"
  - If files were provided as arguments: Yes — all / Yes — provided files / No
  - If no files were provided: Yes — all / No (user can select "Other" to specify custom paths)

**Round 2** — call only if needed, with only the applicable questions:
- **Checkout** (if New branch = Yes): "Should this skill run `git checkout -b <branch>` automatically?" (Yes / No)
- **Auto-commit** (if Stage files ≠ No): "Should this skill run `git commit` automatically after generating the message?" (Yes / No)

Skip Round 2 entirely if neither condition is met.

After all answers, display a confirmation to the user (substitute actual selections from user answers):

> **Your selections:**
> - New branch: Yes / No
> - Stage files: Yes (`git add <files>`) / No
> - Checkout branch: Yes / No / N/A
> - Execute commit: Yes / No / N/A

Proceed immediately to Analysis & Generation after showing the confirmation — do not wait for further input.

## Analysis & Generation

**Collect git context** — run these commands (append `-- <files>` to scope diffs to user-supplied paths):

```bash
git --no-pager log --oneline -10
git --no-pager status --short
git --no-pager diff
git --no-pager diff --cached
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

**Commit type table** — for ambiguous cases, see **`references/commit-types.md`**:

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

**IMPORTANT — execution vs display:** A "Yes" answer means RUN the git command and show its output. Do not display the command and wait for the user to run it themselves. Only display-without-running when the user answered "No" or N/A for that action.

Run each step below if and only if its condition is met. Skip steps whose condition is not met:

1. **Stage files** (condition: Stage files ≠ No) — run `git add <files>` or `git add --all`
2. **Generate branch name** (condition: New branch = Yes) — invoke the `git-helper:generate-branch` skill via the Skill tool, passing the commit subject as work description. After the skill completes, **capture the branch name from its output**: look for it in the fenced code block (e.g., `` `feature/add-login` ``) or the Summary table's Branch field. Store this value for step 3.
3. **Checkout branch** (condition: New branch = Yes AND Checkout = Yes) — run `git checkout -b <branch-name-captured-in-step-2>`
4. **Execute commit** (condition: Auto-commit = Yes) — run the commit command using subject + body + BREAKING CHANGE footer. Add `Co-Authored-By` trailer only if the user explicitly requested it.

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

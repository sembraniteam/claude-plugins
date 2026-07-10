---
name: generate-commit
description: This skill should be used when the user invokes /git-helper:generate-commit, or asks to "generate a commit message", "write a commit for me", "what should my commit message be", "help me commit my changes", "suggest a commit message", "prepare a commit", "what commit type should I use", "stage and commit my changes", "commit all my changes", "I'm done working on this", "commit everything I did", "write a commit for my changes", or describes a change they just made and needs a commit message for it. Produces a conventional commit with type, scope, subject, optional body, and breaking change footer.
argument-hint: "[file1 file2 ...]"
allowed-tools: ["Bash", "AskUserQuestion", "Skill"]
---

# Generate Commit Message

Generate a conventional commit message by analyzing the current git context. Gather user intent first, then analyze and generate, and execute confirmed actions.

## Pre-flight Questions

Before running any git commands, collect user intent using `AskUserQuestion` in up to two rounds.

**Round 1** — ask both questions in a single call:
- **New branch**: "Do you want to create a new branch for this commit?" (Yes / No)
- **Stage files**: "Which files should be staged before committing?"
  - If files were provided as arguments: Yes — all / Yes — provided files / No
  - If no files were provided: Yes — all / No (user can select "Other" to specify custom paths)

**Round 2** — ask only the questions whose condition is met; skip entirely if neither applies:

| Question                                                                         | Condition                 | Options  |
|----------------------------------------------------------------------------------|---------------------------|----------|
| "Should this skill run `git checkout -b <branch>` automatically?"                | New branch = Yes          | Yes / No |
| "Should this skill run `git commit` automatically after generating the message?" | No condition — always ask | Yes / No |

After all answers, display a confirmation to the user (substitute actual selections from user answers):

> **Your selections:**
> - New branch: Yes / No
> - Stage files: Yes (`git add <files>`) / No
> - Checkout branch: Yes / No / N/A
> - Execute commit: Yes / No

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

Always display the final commit message in a fenced code block so the user can verify it.

Then, based on what the user chose in Round 2:
- **Execute commit = No** — also display the ready-to-run command so the user can copy and run it manually. Stop here.
- **Execute commit = Yes** — do not print the command. Proceed directly to the execution steps below and run it via Bash. Show the command output, not the command text.

Command formats for reference (used internally or shown when Execute = No):
- **Subject only**: `git commit -m "feat(auth): add OAuth2 login support"`
- **With body or BREAKING CHANGE footer** — heredoc form:

```bash
git commit -m "$(cat <<'EOF'
feat(auth): add OAuth2 login support

Allow users to authenticate via Google and GitHub OAuth2 providers.
Token storage uses existing session infrastructure.

BREAKING CHANGE: removed /api/v1/auth/basic endpoint. Use /api/v2/auth instead.
EOF
)"
```

Run each step below if and only if its condition is met. Skip steps whose condition is not met:

1. **Stage files** (condition: Stage files ≠ No) — run `git add <files>` or `git add --all`
2. **Generate branch name** (condition: New branch = Yes) — invoke the `git-helper:generate-branch` skill via the Skill tool, passing the commit subject as work description. After the skill completes, **capture the branch name from its output**: look for it in the fenced code block (e.g., `` `feature/add-login` ``) or the branch name output. Store this value for step 3.
3. **Checkout branch** (condition: New branch = Yes AND Checkout = Yes) — run `git checkout -b <branch-name-captured-in-step-2>`
4. **Execute commit** (condition: Auto-commit = Yes) — run the commit command using subject + body + BREAKING CHANGE footer. Add `Co-Authored-By` trailer only if the user explicitly requested it.

If no actions were confirmed, inform the user the message is ready to use manually.

## Additional Resources

- **`references/commit-types.md`** — Detailed type selection guide with examples for ambiguous cases

### Example Outputs

Working commit message examples in `examples/`:
- **`feat-with-scope.md`** — Standard feature commit with scope
- **`fix-breaking-change.md`** — Breaking change with `!` and `BREAKING CHANGE` footer
- **`revert.md`** — Revert commit with hash in body
- **`chore-multi-scope.md`** — Chore commit touching multiple areas (cross-cutting scope omitted)

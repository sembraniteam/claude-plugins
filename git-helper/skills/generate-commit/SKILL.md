---
name: generate-commit
description: This skill should be used when the user invokes /git-helper:generate-commit, or asks to "generate a commit message", "write a commit for me", "what should my commit message be", "help me commit my changes", "suggest a commit message", "prepare a commit", "what commit type should I use", or "stage and commit my changes". Produces a conventional commit with type, scope, subject, optional body, and breaking change footer.
argument-hint: "[file1 file2 ...]"
allowed-tools: ["Bash"]
license: MIT
---

# Generate Commit Message

Generate a conventional commit message by analyzing the current git context. Gather user intent first, then analyze and generate, execute confirmed actions, and display a final summary.

## Pre-flight Questions

Before running any git commands, collect user intent in two rounds.

**Round 1 — ask both questions together:**

1. **New branch** — Do you want to create a new branch for this commit?
2. **Stage files** — Offer options based on whether the user provided files:
   - **If files were provided**, present three choices:
     1. Yes — all (`git add --all`)
     2. Yes — `<the provided files>` (`git add <files>`)
     3. No
   - **If no file path was provided**, present three choices:
     1. Yes — all (`git add --all`)
     2. Yes — specific files (user fills in which files)
     3. No

Wait for answers, then determine follow-up questions:
- If **Q1 = Yes** → ask Q3: **Checkout branch** — Do you want to run `git checkout -b <branch-name>` after the branch name is generated?
- If **Q2 = Yes** → ask Q4: **Execute commit** — Do you want to run `git commit -m "<message>"` automatically?

**Round 2 — ask applicable follow-up questions together** (Q3, Q4, or both). Skip if neither applies.

After all answers, confirm selections:

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

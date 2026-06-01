---
name: generate-commit
description: This skill should be used when the user invokes /git-helper:generate-commit, or asks to "generate a commit message", "write a commit for me", "what should my commit message be", "help me commit my changes", or "suggest a commit message". Analyzes staged changes, unstaged diffs, git status, and recent log history using conventional commit format to produce a properly formatted subject, body, and optional footer.
argument-hint: "[file1 file2 ...]"
allowed-tools: ["Bash"]
version: 0.2.0
---

# Generate Commit Message

Generate a conventional commit message by analyzing the current git context. Display the result for the user to copy and run manually — never execute the commit automatically.

## Step 1: Read Settings

Check if `.claude/git-helper.local.md` exists. If it does, parse the YAML frontmatter to get `default_scope`:

```bash
SETTINGS=".claude/git-helper.local.md"
if [ -f "$SETTINGS" ]; then
  FRONTMATTER=$(sed -n '/^---$/,/^---$/{ /^---$/d; p; }' "$SETTINGS")
  DEFAULT_SCOPE=$(echo "$FRONTMATTER" | grep '^default_scope:' | sed 's/default_scope: *//' | sed 's/^"\(.*\)"$/\1/')
fi
```

Use `default_scope` as a fallback when scope cannot be inferred from the diff (Step 5).

## Step 2: Collect Git Context

Run the context script, passing any user-supplied file paths as arguments:

```bash
# No file filter — analyze all changes
bash "$CLAUDE_PLUGIN_ROOT/scripts/collect-context.sh"

# One file
bash "$CLAUDE_PLUGIN_ROOT/scripts/collect-context.sh" "src/auth/login.ts"

# Multiple files
bash "$CLAUDE_PLUGIN_ROOT/scripts/collect-context.sh" "src/auth/login.ts" "src/auth/logout.ts"
```

`$CLAUDE_PLUGIN_ROOT` is set by the plugin runtime to the plugin's root directory.

**The `[file1 file2 ...]` arguments** are file paths that limit the diff output to those specific files. When provided, the script runs `git diff -- <files>` and `git diff --cached -- <files>` instead of showing all changes. Omit them to analyze all staged/unstaged changes.

The script outputs labeled sections (headers use `===` delimiters):
- `=== GIT LOG (last 10 commits) ===` — tone and style reference
- `=== GIT STATUS ===` — current working tree state
- `=== GIT DIFF (unstaged) ===` — unstaged changes (filtered to files if provided)
- `=== GIT DIFF STAGED ===` — staged changes (filtered to files if provided)
- `=== FILE FILTER ===` — the file paths used as filter (only when files were passed)

If both diffs are empty and status shows no changes, inform the user there is nothing to commit and stop.

## Step 3: Determine Commit Type

Analyze the staged diff first (primary signal), then unstaged diff and status as supporting context. Select exactly one type from the table below:

| Type       | When to use                                                  |
|------------|--------------------------------------------------------------|
| `feat`     | New feature visible to the user (not a build-script feature) |
| `fix`      | Bug fix visible to the user (not a build-script fix)         |
| `docs`     | Documentation changes only (e.g., README.md)                 |
| `refactor` | Production code restructured without behavior change         |
| `test`     | Tests added or refactored; no production code changed        |
| `chore`    | Non-production tasks (grunt tasks, tooling, etc.)            |
| `ci`       | CI configuration files or scripts changed                    |
| `perf`     | Performance improvement                                      |
| `revert`   | Reverting a previous commit                                  |
| `bump`     | Dependency version update                                    |

**Tie-breaking rules:**
- If staged diff is empty but unstaged diff is not, base the type on the unstaged diff and note that the user should stage changes first
- If changes span multiple types, pick the dominant type (the one with the most lines changed or highest user impact)
- `feat` and `fix` take priority over `refactor` when in doubt

## Step 4: Detect Breaking Changes

Mark as a breaking change if any of the following are true:
- A public API, function signature, or interface is removed or incompatibly changed
- An environment variable or config key is renamed or removed
- Database schema changes that require migration
- The diff contains a comment or message with `BREAKING CHANGE`

## Step 5: Determine Scope

Infer scope from the changed file paths (e.g., `auth` from `src/auth/login.ts`, `api` from `routes/api/`, `ui` from `components/`). If scope cannot be inferred and `default_scope` is set in `.claude/git-helper.local.md`, use that as the fallback. Omit scope entirely if changes are too broad or cross-cutting.

Scope must be lowercase, no spaces, no special characters.

## Step 6: Write the Subject Line

Format: `<type>[(<scope>)][!]: <description>`

**Rules for the description:**
- Imperative mood: "add login" not "adds login" or "added login"
- Lowercase first letter
- No period at the end
- Max 72 characters total (type + scope + description)
- Must complete the sentence: "If applied, this commit will _____"

**Examples:**
```
feat(auth): add OAuth2 login support
fix(api): handle null response from payment gateway
refactor: extract validation logic into separate module
feat!: remove deprecated v1 endpoints
```

## Step 7: Add Body (if needed)

Include a commit body when:
- The change is non-obvious and requires context
- A breaking change needs explanation

Separate body from subject with a blank line. Wrap at 72 characters.

## Step 8: Add Breaking Change Footer (if applicable)

If a breaking change was detected, append:

```
BREAKING CHANGE: <description of what broke and how to migrate>
```

## Step 9: Display the Final Message

Present the complete commit message in a code block:

```
feat(auth): add OAuth2 login support

Allow users to authenticate via Google and GitHub OAuth2 providers.
Token storage uses existing session infrastructure.

BREAKING CHANGE: removed /api/v1/auth/basic endpoint. Use /api/v2/auth instead.
```

Then show the ready-to-run git command:

```bash
git commit -m "feat(auth): add OAuth2 login support"
```

For multi-line messages (body or BREAKING CHANGE footer), show the heredoc form:

```bash
git commit -m "$(cat <<'EOF'
feat(auth): add OAuth2 login support

Allow users to authenticate via Google and GitHub OAuth2 providers.
Token storage uses existing session infrastructure.

BREAKING CHANGE: removed /api/v1/auth/basic endpoint. Use /api/v2/auth instead.
EOF
)"
```

## Edge Cases

- **Nothing staged**: Inform the user that changes need to be staged first (`git add`). Still generate the message based on unstaged diff so the user can review it before staging.
- **Only whitespace/formatting changes**: Use `refactor` (formatting changes with no logic change).
- **Merge commit**: Use `chore: merge <branch>` unless the merge introduces a feature or fix.
- **Revert**: Use `revert: revert "<original subject>"` and reference the reverted commit hash in the body.

## Step 10: Offer to Generate a Branch

After displaying the commit message, ask:

> Do you want to generate a new branch name for this commit?
> - **Yes** — generate a branch name based on this commit
> - **No** — done

If the user says **Yes**, invoke the `git-helper:generate-branch` plugin. Pass the commit subject line as the work description context so the branch name stays consistent with the commit intent. Do not ask for a work description again — use what is already known.

## Additional Resources

- **`references/commit-types.md`** — Detailed type selection guide with examples for ambiguous cases

---
description: Run a security audit scoped to only the files changed vs a base branch (plus uncommitted/staged changes) — the recommended default for PR review and for codebases too large for a full /audit to fit in context.
---

You are running a diff-scoped security audit using the `security-auditor` plugin. This is the recommended way to audit a pull request, and the recommended fallback whenever a full `/audit` would need to read more source than fits in context — scoping to the diff solves both problems at once.

## Step 1 — Parse arguments

`$ARGUMENTS` may contain, in any order:
- A mode hint: `dev`/`development` or `prod`/`production`
- A git ref (branch, tag, or commit) to diff against

Any remaining token that isn't a recognized mode keyword is treated as the base ref. If no mode is given, ask the same question `/audit` asks:

> "Is this project currently in **development** or **production**?"

## Step 2 — Resolve the base ref and list changed files

If a base ref was given, use it directly. Otherwise detect the repo's default branch:

```bash
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@'
# falls back to checking for a local `main` then `master` branch if the above is empty
```

Then collect the changed file set as the union of:

```bash
git diff --name-only --diff-filter=ACMR <base>...HEAD   # committed changes vs merge-base
git diff --name-only --diff-filter=ACMR HEAD             # unstaged working-tree changes
git diff --name-only --diff-filter=ACMR --staged         # staged changes
```

`--diff-filter=ACMR` keeps added/copied/modified/renamed files and drops deleted files (nothing to audit in a file that no longer exists). Deduplicate the combined list.

If this is not a git repository, has no commits, or the combined list is empty, say so plainly and stop:

> "No git changes found against `<base>`. Run `/audit` for a full codebase scan instead."

## Step 3 — Filter the changed set

Drop paths matching common generated/vendored directories before analysis: `node_modules/`, `dist/`, `build/`, `vendor/`, `.venv/`, `target/`, `*.min.js`, lockfiles that aren't being read for dependency scanning in Step 5, and any path Glob confirms doesn't exist (renamed/moved after the diff was taken).

Summarize to the user: "Diff vs `<base>`: N files changed. Starting code analysis."

## Step 4 — Chunking for large diffs

If the filtered changed-file count is roughly 40 or more, warn the user this is a large diff and that it will be analyzed in batches to avoid truncating the review:

> "This diff touches N files — analyzing in M batches to keep each pass within context."

Split the file list into batches of ~15–20 files each, grouped by directory where possible (keeps related files — e.g. a route and its test — in the same batch). Spawn `security-auditor` once per batch, continuing the `SA-NNN` sequence across batches exactly as described in `/audit` Step 3 (check the session for the highest existing `SA-NNN` before each spawn, never restart the sequence). This is the same chunking strategy `/audit` itself falls back on for a full-repository scan too large for one pass — see `/audit` Step 3 for the non-diff case.

## Step 5 — Code analysis via subagent

Spawn the `security-auditor` agent (or one per batch, per Step 4) scoped to **only the changed files**, not a full project map. Pass it:
- The project root path (for resolving imports/context, not for a full scan)
- The list of changed files to analyze
- The audit mode (dev/prod)
- The starting `SA-NNN` number

## Step 6 — Dependency CVE verification (only if manifests changed)

Check whether any changed file is a dependency manifest or lockfile (`package.json`, `package-lock.json`, `requirements.txt`, `go.sum`, `Cargo.lock`, `composer.lock`, `Gemfile.lock`, `pom.xml`, `*.csproj`, etc.).

- If none changed, skip this step and note in the report: "No dependency manifest changes in this diff — dependency CVEs not re-scanned. Run `/audit-deps` for a full dependency scan."
- If one or more changed, diff the manifest against `<base>` to find added or version-bumped packages specifically, and run the same `query_osv` / `get_cve` / `get_epss` / `get_kev` flow as `/audit` Step 4 — but only for the packages that actually changed, not the whole dependency tree.

## Step 7 — Baseline filtering and report

Apply `.security-audit-baseline.json` filtering as described in the `secure-code-review` skill's `references/baseline-suppression.md` before finalizing findings.

Generate the report via the `secure-code-review` skill, with the header noting the scope explicitly: `**Scope**: diff vs \`<base>\` (N files)` in place of a full-project stack line, plus the usual severity table and findings.

> To save this as a standalone report, run `/audit-report` (add `--sarif` for GitHub code scanning output). To fix findings, run `/audit-fix`.

# Step 5 Verification Rationale

Why `SKILL.md` Step 5 verifies artifacts before applying them, referenced inline from that step.

## Why verify commit_sha and contents

An agent's report is not proof by itself. A `commit_sha` that does not resolve via
`git cat-file -e <commit_sha>^{commit}` is a hallucinated field, not a typo to route around — never cherry-pick it.
Likewise, a commit's actual contents (`git show --name-only <commit_sha>`) must line up exactly with what the report
claims: the same paths as `fix_diff`, the report's `test_file` present, and none of the `side_effects_flagged` paths.
`side_effects_flagged` files were deliberately left unstaged by the investigator (Phase 3 of
`../../../agents/hypothesis-investigator.md`) precisely because they fell outside the hypothesis's scope — finding
one of them in the commit means the investigator's own staging discipline failed, not that the commit is "consistent"
with the report. `test_scope_files` records what the test run exercised, which is a different question from what the
commit contains (a test can pass while exercising code the fix never touched); it plays no part in this check.
Any mismatch is a discrepancy between claim and artifact, not a detail to reconcile silently — escalate to the user
rather than route around it or correct it automatically.

## Why the single-winner spot-check exists

`hypothesis-arbitrator` re-verifies every evidence citation it receives against `base_sha` (see its Step 2) before a
hypothesis can be selected. But a hypothesis that reaches Step 5 via the single-passing-report path (Step 4) never
goes through the arbitrator at all — its evidence would otherwise reach the apply stage having never been
independently checked by anyone but the investigator itself. The spot-check
(`git show <base_sha>:<evidence[0].file>`, confirming `evidence[0].excerpt` appears at `evidence[0].line`) closes
exactly that gap. If the citation doesn't check out, the report is unverified: do not apply it, and escalate to the
user with what the citation actually showed.

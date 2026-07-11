# Step 5 Verification Rationale

Why `SKILL.md` Step 5 verifies artifacts before applying them, referenced inline from that step.

## Why verify commit_sha and contents

An agent's report is not proof by itself. A `commit_sha` that does not resolve via
`git cat-file -e <commit_sha>^{commit}` is a hallucinated field, not a typo to route around — never cherry-pick it.
Likewise, a commit whose actual contents (`git show --name-only <commit_sha>`) touch files the report never
mentioned (missing from `test_file`, `test_scope_files`, or `side_effects_flagged`) is a discrepancy between claim
and artifact, not a detail to reconcile silently. Both cases must escalate to the user rather than be routed around
or corrected automatically.

## Why the single-winner spot-check exists

`hypothesis-arbitrator` re-verifies every evidence citation it receives against `base_sha` (see its Step 2) before a
hypothesis can be selected. But a hypothesis that reaches Step 5 via the single-passing-report path (Step 4) never
goes through the arbitrator at all — its evidence would otherwise reach the apply stage having never been
independently checked by anyone but the investigator itself. The spot-check
(`git show <base_sha>:<evidence[0].file>`, confirming `evidence[0].excerpt` appears at `evidence[0].line`) closes
exactly that gap. If the citation doesn't check out, the report is unverified: do not apply it, and escalate to the
user with what the citation actually showed.

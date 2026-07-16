# Step 5 Verification Rationale

Why `SKILL.md` Step 5 verifies artifacts before applying them, referenced inline from that step.

## Why verify fix_diff before applying it

An agent's report is not proof by itself. A `fix_diff` that fails `git apply --check` is not something to force
through with a fuzzier apply mode or hand-edit around — treat it exactly like a hallucinated field and escalate
rather than route around it. Likewise, the patch's actual contents (the `diff --git a/<path> b/<path>` headers
inside `fix_diff`) must include the report's `test_file` and none of the `side_effects_flagged` paths.
`side_effects_flagged` files were deliberately left out of the captured diff by the investigator (Phase 3 of
`../../../agents/hypothesis-investigator.md`) precisely because they fell outside the hypothesis's scope — finding
one of them in the patch means the investigator's own diff-scoping discipline failed, not that the patch is
"consistent" with the report.

Note the trust boundary this leaves: unlike the old commit-based design, where `git show --name-only <commit_sha>`
was an independently-produced artifact (a real git object the investigator couldn't retroactively edit), `fix_diff`
is now plain text living in the same self-authored YAML file as `status`, `confidence`, and every other field.
`git apply --check` is the main defense against a fabricated or inconsistent `fix_diff` — a patch that doesn't
correspond to real content at `base_sha` will almost always fail to apply cleanly — but a clean check only proves
"this patch is well-formed and matches the base tree," not "the investigator actually ran this exact diff and
produced the reported `test_result`."

`test_scope_files` records what the test run exercised, which is a different question
from what the patch contains (a test can pass while exercising code the fix never touched); it plays no part in this
check — coverage adequacy against `test_scope_files` is the arbitrator's Step 1 concern *when arbitration runs*.
On the single-passing-hypothesis path (no arbitration), nothing re-checks `test_scope_files` plausibility; the
single-winner spot-check below covers citation accuracy instead, which is a related but different guarantee. This
gap is narrower than it sounds, though: `SKILL.md` Step 4's gate already requires `initial_test_result: fail` AND
`test_result: pass` on the *same* test to reach Step 5 at all, and a test flipping red-to-green because of the fix
is itself empirical proof that the test is sensitive to the change — a stronger guarantee than a static
`test_scope_files` list could ever offer, since a listed file could still be present without the test actually
depending on it.

Any mismatch is a discrepancy between claim and artifact, not a detail to reconcile silently — escalate to the
user rather than route around it or correct it automatically.

## Why the single-winner spot-check exists

`hypothesis-arbitrator` re-verifies every evidence citation it receives against `base_sha` (see its Step 2) before a
hypothesis can be selected. But a hypothesis that reaches Step 5 via the single-passing-report path (Step 4) never
goes through the arbitrator at all — its evidence would otherwise reach the apply stage having never been
independently checked by anyone but the investigator itself. The spot-check
(`git show <base_sha>:<evidence[0].file>`, confirming `evidence[0].excerpt` appears at `evidence[0].line`) closes
exactly that gap. If the citation doesn't check out, the report is unverified: do not apply it, and escalate to the
user with what the citation actually showed.

# Evidence Report Format

Specification for the structured reports returned by each hypothesis-investigator agent and the final ranked report
assembled by the parallel-debug skill.

---

## Per-Agent Report

Each hypothesis-investigator agent produces exactly one report artifact: the `hN.report.yaml` file written in its own
Phase 4 (see `../../../agents/hypothesis-investigator.md`). There is no separate markdown report — a single artifact
means there is only ever one version of the truth for a hypothesis's outcome, since the orchestrator, the arbitrator,
and any human auditor all read the same file.

The investigator's final conversational message is a short receipt only (2–3 sentences: status, test result, one-line
root cause claim, report path) — a completion signal for the orchestrator and a skim-friendly note for a human watching
the live transcript. It is never a data source: nothing downstream re-derives report fields from it, and it is not
available at all for a crashed or timed-out agent, unlike the YAML file which the orchestrator can still act on.

The `status` and `confidence` fields in the YAML report follow these definitions:

### Status Definitions

**Hard rule:** `CONFIRMED` requires both `initial_test_result: fail` and `test_result: pass` on the *same* test. A test that never failed before the fix proves nothing about the fix — no matter how confidently the investigator narrates it, a report claiming `status: confirmed` without that pairing is invalid. This is not a guideline the investigator applies at its own discretion: the orchestrator recomputes this pairing directly from the raw fields at `SKILL.md` Step 4 rather than trusting the `status` field at face value, and treats a mismatch as a failed gate. This closes the most likely hallucination path in this plugin — a tautological test that trivially passes both before and after a fix, honestly reported as `pass` while proving nothing.

| Status           | Meaning                                                                                                                                          | Required field values                                    |
|------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------|
| `CONFIRMED ✓`    | The test reproduced the bug before the fix and passes after it; root cause is clearly the hypothesized mechanism                                 | `initial_test_result: fail` AND `test_result: pass`         |
| `UNCONFIRMED ✗`  | Evidence does not support the hypothesis; the predicted code pattern was not found, or the test showed a different failure                       | `test_result: fail` after the fix, or the hypothesis is explicitly refuted |
| `INCONCLUSIVE ?` | Mixed evidence — test reproduced the bug but the fix didn't fully resolve it, code pattern is present but may not be the cause, or the test passed both before and after the fix (a tautological pass that never actually exercised the bug) | Any pairing that doesn't satisfy CONFIRMED's or UNCONFIRMED's required values above — including `initial_test_result` not being `fail` |

### Confidence Definitions

Each level is an observable checklist against the report's own fields, not a subjective read of how convincing the narrative sounds:

| Level    | Criteria (all must hold)                                                                                                                                        |
|----------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `High`   | `status: confirmed` per the hard rule above, AND at least one `evidence` entry whose `excerpt` verbatim-matches the code at that `file`/`line` in `base_sha`        |
| `Medium` | `status: confirmed` or `inconclusive`, evidence points at the right area of code, but no entry is a verbatim match against `base_sha`, or the match exists but the causal link in `relevance` is indirect |
| `Low`    | Hypothesis is plausible but evidence is circumstantial — no verbatim code match against `base_sha`, or the claim rests on general reasoning about behavior rather than a specific cited line               |

A `high` confidence report whose citation does not actually verbatim-match `base_sha` is a defect in the report, not a matter of degree — see the arbitrator's Step 2 re-verification and the single-winner spot-check at `SKILL.md` Step 5, both of which exist specifically to catch this before a fix is applied.

---

## Final Ranked Report

The parallel-debug skill assembles this final format from the persisted `hN.report.yaml` files alone — not from the short
receipt message an investigator returned in the conversation, which is not available for a crashed or timed-out agent. Map
YAML fields to the template as follows:

- `status` → the Status badge: `confirmed`→`CONFIRMED ✓`, `inconclusive`→`INCONCLUSIVE ?`, `unconfirmed`→`UNCONFIRMED ✗`
- `confidence` → Confidence
- `test_result` / `test_command` → the Test line
- `test_file` / `test_name` → the `path/to/test.ext::test_name` reference
- `claim` → Root cause
- `fix_summary` → Fix
- `evidence` → Key evidence

For a hypothesis whose agent timed out or crashed (no `hN.report.yaml` was ever written), render its row using the synthetic
`test_result: not_run` record from Step 3 of `SKILL.md`, with `status: unconfirmed` and the remaining qualitative fields
as "N/A".

`initial_test_output_excerpt` and `final_test_output_excerpt` are not rendered in the table — they exist for audit, not
summary. Consult them directly in the `hN.report.yaml` file when a status or citation looks suspicious (e.g., an excerpt
that reads like a paraphrase rather than an actual test runner transcript is a signal the command may not have really
been run).

```markdown
# Parallel Debug Report

## Ranked Results

### 🥇 #1 — [Hypothesis Name] — CONFIRMED ✓, High Confidence
- **Test**: PASS — `path/to/test.ext::test_name`
- **Root cause**: [one sentence from agent report]
- **Fix**: [brief change description]
- **Key evidence**:
  - [evidence point 1]
  - [evidence point 2]

### 🥈 #2 — [Hypothesis Name] — INCONCLUSIVE ?, Medium Confidence
- **Test**: FAIL after [N] iterations
- **Evidence**:
  - [evidence point 1]
  - [evidence point 2]

### #3 — [Hypothesis Name] — UNCONFIRMED ✗
- **Test**: FAIL (bug not reproduced under this hypothesis)
- **Evidence**: [brief refutation]

[... remaining hypotheses in ranked order ...]

---

## Recommendation

[ONE of the following, based on results:]

**Single confirmed fix**: Apply the fix from hypothesis #1 (`path/to/file:line`). High confidence it resolves the bug.

**Multiple confirmed**: Multiple root causes detected. Apply fixes in this order:
1. [hypothesis #1 fix] — resolves [symptom aspect]
2. [hypothesis #2 fix] — resolves [symptom aspect]

**Inconclusive only**: No hypothesis was confirmed. The most promising lead is `[hypothesis name]` ([confidence reasoning]). Recommend a targeted sequential investigation focused on [specific area] — add instrumentation or narrow the hypothesis space before retrying in parallel.

**All unconfirmed**: No hypothesis reproduced the bug. The bug may require direct reproduction with additional logging. Recommended next steps: [1–2 specific suggestions].

---

## Summary Table

| Rank | Hypothesis     | Status           | Confidence |    Test     |
|-----:|----------------|------------------|:----------:|:-----------:|
|    1 | [name]         | CONFIRMED ✓      |    High    |    PASS     |
|    2 | [name]         | INCONCLUSIVE ?   |   Medium   |    FAIL     |
|    3 | [name]         | UNCONFIRMED ✗    |    Low     |    ERROR    |

**Agents spawned**: [N] — **Confirmed**: [N] — **Inconclusive**: [N] — **Unconfirmed**: [N]
```

---

## Ranking Algorithm

Apply this scoring to sort agent reports (higher score = higher rank):

```
score = (test_final_result * 100) + (confidence * 10) + evidence_count

test_final_result:
  PASS    → 3
  FAIL    → 1
  ERROR   → 0

confidence:
  High    → 3
  Medium  → 2
  Low     → 1

evidence_count:
  3 points  → 3
  2 points  → 2
  1 point   → 1
```

`test_final_result` is derived from the YAML `test_result` field written by each investigator: `pass` → `PASS`, `fail` → `FAIL`, `not_run` → `ERROR` (an agent that timed out or crashed produced no verifiable result, so it scores the same as a run that errored out).

In case of a tie: prefer the hypothesis with a code quote (specific file:line) over general observations.

This scoring only orders entries within the Final Ranked Report table; it is independent of the pass/fail gate in
`SKILL.md` Step 4, which additionally requires `status: confirmed` (not just `test_result: pass`) before a hypothesis
can be auto-applied or sent to arbitration. A high-scoring `inconclusive` report can rank above a lower-scoring
`confirmed` one in this table without becoming eligible for that gate.

---

## Iteration Budget to Minutes Mapping

`time_budget_minutes` is an approximate time budget per agent, not a total (agents run in parallel). Look up the iteration budget from this table — it is the single source of truth; do not recompute it from a formula:

| `time_budget_minutes` | Iteration budget passed to agents |
|-----------------------|-----------------------------------|
| 1–2                   | 1 iteration                       |
| 3–4                   | 2 iterations                      |
| 5–7                   | 3 iterations (default)            |
| 8–10                  | 4 iterations                      |
| 11–15                 | 5 iterations                      |

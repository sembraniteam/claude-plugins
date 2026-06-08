# Evidence Report Format

Specification for the structured reports returned by each hypothesis-investigator agent and the final ranked report
assembled by the parallel-debug skill.

---

## Per-Agent Evidence Report

Each hypothesis-investigator agent returns a report in this exact format. All fields are required; use "N/A" or "None"
for sections that do not apply.

```markdown
## Hypothesis Report: [hypothesis-slug]

**Status**: CONFIRMED ✓  |  INCONCLUSIVE ?  |  UNCONFIRMED ✗
**Confidence**: High  |  Medium  |  Low

### Test
- File: `path/to/test_file.ext`
- Test name: `test_function_name`
- Initial result: FAIL (bug reproduced)  |  PASS (bug not reproduced)  |  ERROR (could not run)
- Final result after fix: PASS  |  FAIL  |  TIMEOUT (budget exhausted)

### Root Cause
[One sentence — only if CONFIRMED or INCONCLUSIVE with evidence. If UNCONFIRMED: "Not applicable."]

### Fix Applied
- File: `path/to/source_file.ext:line_number`
- Change: [what was wrong → what it was changed to, in ≤20 words]
[If no fix: "None — hypothesis not confirmed."]

### Evidence
- [Specific code quote or test output, with file:line reference]
- [Second evidence point]
- [Third evidence point if available, otherwise omit]

### Confidence Reasoning
[1–2 sentences explaining the confidence level: what makes it certain or uncertain]
```

### Status Definitions

| Status           | Meaning                                                                                                                       |
|------------------|-------------------------------------------------------------------------------------------------------------------------------|
| `CONFIRMED ✓`    | Test reproduced the bug; fix made the test pass; root cause is clearly the hypothesized mechanism                             |
| `UNCONFIRMED ✗`  | Evidence does not support the hypothesis; the predicted code pattern was not found or test showed a different failure         |
| `INCONCLUSIVE ?` | Mixed evidence: test reproduced the bug but fix did not fully resolve it, or code pattern is present but may not be the cause |

### Confidence Definitions

| Level    | Criteria                                                                                            |
|----------|-----------------------------------------------------------------------------------------------------|
| `High`   | Test was green after fix; root cause directly matches hypothesis; no alternative explanations       |
| `Medium` | Test improved or partially passed; hypothesis explains most but not all observations                |
| `Low`    | Hypothesis is plausible but evidence is circumstantial; test could not definitively confirm or deny |

---

## Final Ranked Report

The parallel-debug skill assembles all agent reports into this final format.

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

**Inconclusive only**: No hypothesis was confirmed. The most promising lead is `[hypothesis name]` ([confidence reasoning]). Recommend a sequential deep-dive using the `debug` skill focused on [specific area].

**All unconfirmed**: No hypothesis reproduced the bug. The bug may require direct reproduction with additional logging. Recommended next steps: [1–2 specific suggestions].

---

## Summary Table

| Rank | Hypothesis     | Status           | Confidence | Test        |
|-----:|----------------|------------------|:----------:|:-----------:|
|    1 | [name]         | CONFIRMED ✓      | High       | PASS        |
|    2 | [name]         | INCONCLUSIVE ?   | Medium     | FAIL        |
|    3 | [name]         | UNCONFIRMED ✗    | Low        | ERROR       |

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

In case of a tie: prefer the hypothesis with a code quote (specific file:line) over general observations.

---

## Iteration Budget to Minutes Mapping

Settings value → approximate agent runtime:

| `time_budget_minutes` | Iteration budget passed to agents |
|-----------------------|-----------------------------------|
| 1–2                   | 1 iteration                       |
| 3–4                   | 2 iterations                      |
| 5–7                   | 3 iterations (default)            |
| 8–10                  | 4 iterations                      |
| 11–15                 | 5 iterations                      |

Formula: `max(1, time_budget_minutes // 2)`

# Remediation Plan Format

The format `review/SKILL.md` step 4e saves to `docs/architecture-designer/plan/{yyyymmdd}-{topic}-remediation.md`.

```markdown
# Remediation Plan: {topic}

| Architecture document | `{document path}`                                    |
|-----------------------|------------------------------------------------------|
| Review source          | {drift report, architecture review, or both}         |
| Date                   | {dd-mmm-yyyy}                                        |
| Status                 | In progress                                          |

## Findings

- [x] `src/auth/middleware.ts` — JWT used but document §5 specifies OAuth2 *(addressed in revision — code pending)*
- [ ] `src/payments/service.ts` — Payment service present in code but absent from architecture document *(deferred)*
```

Rules:
- **One checkbox per finding** from the drift report or architecture review report.
- **Source path is mandatory** on every item — the same file-path-citation rule that governs the drift report applies here. A finding without a file path (or a document section reference for document-only claims) must not be written.
- `[x]` for findings the user confirmed as addressed in this revision (the scope agreed in step 4a); `[ ]` for findings deferred.
- **Suffix progression** — use a two-phase suffix for `[x]` items so the document stays readable across sessions:
  - Write `*(addressed in revision — code pending)*` at this step — the diagram fix is done, but the code change will happen during implementation.
  - The implementer updates it to `*(code aligned)*` once the code change is verified. Only the suffix text changes; the `[x]` checkbox stays.
  - `[ ]` items always carry `*(deferred)*`.

This file is a **living document**: in future review sessions, re-open it, tick off deferred items (`[ ]` → `[x]`, with suffix `*(addressed in revision — code pending)*`), and update `Status` to `Complete` when every `[x]` item reads `*(code aligned)*` and no `[ ]` items remain.

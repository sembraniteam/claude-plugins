# Remediation Plan Format

The format `review/SKILL.md` step 4e saves to `docs/architecture-designer/plan/{yyyymmdd}-{topic}-remediation.md`.

```markdown
# Remediation Plan: {topic}

| Architecture document | `{document path}`                            |
|-----------------------|----------------------------------------------|
| Review source         | {drift report, architecture review, or both} |
| Date                  | {dd-mmm-yyyy}                                |
| Status                | In progress                                  |

## Findings

- [x] `src/auth/middleware.ts` — JWT used but document section 5 specifies OAuth2 *(addressed in revision — code pending)*
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

This file's `Status` row and individual item suffixes update in place after this step: `architecture-implementer` flips `[x]` items from `*(addressed in revision — code pending)*` to `*(code aligned)*` as each code change is verified (see the `implement` skill). The plan is fully resolved once every `[x]` item reads `*(code aligned)*` and no `[ ]` items remain — checked via `session-schema.md` section "Checking whether a remediation plan is fully resolved", not by re-reading this file's checkboxes directly.

The checklist itself, however, is never reopened to add new findings or tick off a deferred `[ ]` item. If a future review session carries this plan's deferred items forward, they are re-documented as fresh findings in a **new** remediation plan file — `review/SKILL.md` step 4e always writes a new file, the same "never overwrite, new file each revision" convention used for architecture documents — and this file is marked `Superseded by {new plan path}` at that point. See `session-schema.md` section "Superseding a remediation plan" for the exact mechanism.

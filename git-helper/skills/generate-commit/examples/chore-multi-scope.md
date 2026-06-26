# Example: Chore Touching Multiple Areas (Cross-Cutting)

**Scenario:** Updated ESLint and Prettier config, `.editorconfig`, and `tsconfig.json` across
multiple packages. No single scope dominates — changes are repo-wide.

**Git command (subject only):**

```bash
git commit -m "chore: update linting and formatting configuration"
```

**Summary table:**

| Field               | Value                                                | Reason                                                 |
|---------------------|------------------------------------------------------|--------------------------------------------------------|
| **Type**            | `chore`                                              | Tooling config update, no production code changed      |
| **Scope**           | *(omitted)*                                          | Cross-cutting — affects ESLint, Prettier, TS, editor   |
| **Commit message**  | `chore: update linting and formatting configuration` | N/A                                                    |
| **Breaking change** | No                                                   | Config-only; all existing code still compiles and runs |

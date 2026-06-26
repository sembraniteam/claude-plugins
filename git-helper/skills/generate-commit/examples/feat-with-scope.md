# Example: Feature with Scope

**Scenario:** Added OAuth2 login via Google and GitHub. Changed files under `src/auth/`.

**Git command (subject only — no body needed):**

```bash
git commit -m "feat(auth): add OAuth2 login support"
```

**Summary table:**

| Field               | Value                                  | Reason                                |
|---------------------|----------------------------------------|---------------------------------------|
| **Type**            | `feat`                                 | New user-facing authentication method |
| **Scope**           | `auth`                                 | Inferred from `src/auth/` file paths  |
| **Commit message**  | `feat(auth): add OAuth2 login support` | N/A                                   |
| **Breaking change** | No                                     | Existing login flows unchanged        |

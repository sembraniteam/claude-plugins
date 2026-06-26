# Example: Breaking Fix (API Removal)

**Scenario:** Removed the deprecated `/api/v1/auth/basic` endpoint. Changed files under `src/api/`.

**Git command (heredoc required — has body and BREAKING CHANGE footer):**

```bash
git commit -m "$(cat <<'EOF'
fix(api)!: remove deprecated basic auth endpoint

The /api/v1/auth/basic endpoint has been removed after the 6-month
deprecation period. All clients must migrate to /api/v2/auth.

BREAKING CHANGE: /api/v1/auth/basic is no longer available.
Migrate to /api/v2/auth which accepts Bearer tokens.
EOF
)"
```

**Summary table:**

| Field               | Value                                              | Reason                                        |
|---------------------|----------------------------------------------------|-----------------------------------------------|
| **Type**            | `fix`                                              | Removes broken/deprecated behavior            |
| **Scope**           | `api`                                              | Inferred from `src/api/` file paths           |
| **Commit message**  | `fix(api)!: remove deprecated basic auth endpoint` | N/A                                           |
| **Breaking change** | Yes                                                | Public endpoint removed; clients must migrate |

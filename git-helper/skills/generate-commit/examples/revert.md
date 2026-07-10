# Example: Revert Commit

**Scenario:** Reverting commit `a3f9c12` ("feat(auth): add OAuth2 login support") because it caused
a regression in session handling.

**Git command (heredoc required — body with hash and reason):**

```bash
git commit -m "$(cat <<'EOF'
revert: revert "feat(auth): add OAuth2 login support"

This reverts commit a3f9c12.
Reason: caused regression in session token renewal for existing users.
EOF
)"
```

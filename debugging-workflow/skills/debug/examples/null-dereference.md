# Example: Null Dereference

**User report:**
```
TypeError: Cannot read properties of undefined (reading 'email')
    at sendWelcomeEmail (src/auth/registration.ts:47:32)
    at POST /api/register (src/routes/auth.ts:23:5)
```

**After silent investigation (git diff, source read, grep for `sendWelcomeEmail`):**

---

**Root cause:** `db.findUser()` returns `undefined` when the INSERT fails silently due to a unique constraint violation on duplicate email addresses; `sendWelcomeEmail` assumes the returned user is always defined.

**Evidence:**
- `src/auth/registration.ts:44` — `const user = await db.findUser({ email })` — no null guard before line 47
- `src/db/users.ts:31` — `insertUser` catches `UniqueConstraintError` and returns `undefined` instead of re-throwing
- `src/routes/auth.ts:21` — no check on the result of `registerUser` before calling `sendWelcomeEmail`

**Fix:**
```diff
- const user = await db.findUser({ email });
- await sendWelcomeEmail(user.email, user.name);
+ const user = await db.findUser({ email });
+ if (!user) {
+   return res.status(409).json({ error: 'Email already registered' });
+ }
+ await sendWelcomeEmail(user.email, user.name);
```

---

**Notes on this example:**
- Investigation was silent — no intermediate narration before the final structured block
- Three evidence points used (third included because the call chain needed full context)
- Fix is minimal: only the broken assumption is addressed, no surrounding refactor

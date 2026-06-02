# Common Debugging Patterns

Root cause patterns by error category. Match the observed error to a pattern to narrow the diagnosis faster.

---

## Null / Undefined Reference

**Symptoms**: `NullPointerException`, `null is not an object`, `AttributeError: 'NoneType'`, `unwrap() on None`, `nil pointer dereference`

**Common causes:**
- Function returns null/None/nil when non-null is assumed
- Object not initialized before use (constructor order bug)
- Optional value used without check (forgot `?.` or null guard)
- Race condition: object accessed after it was destroyed/deallocated
- Config or environment variable not set (returns null)

**Investigation steps:**
1. Find where the null-returning path is: trace the variable back to its source
2. Check if the function can legitimately return null and whether callers handle it
3. Check initialization order in constructors / DI containers
4. Look for any `if (x != null)` guards that were removed

---

## Type Mismatch

**Symptoms**: `TypeError`, `ClassCastException`, `Type X is not assignable to Y`, `mismatched types`

**Common causes:**
- API returned a different type than expected (JSON schema changed)
- Serialization/deserialization issue (wrong type mapping)
- Implicit conversion removed by a type-system upgrade
- Generics: wrong type parameter passed
- Database column type mismatch (String vs int)

**Investigation steps:**
1. Print/log the actual type at runtime if possible
2. Compare against the expected type declaration
3. Check if the API or data source changed recently (`git diff`)
4. Look for recent model/schema changes

---

## Missing Import / Undefined Symbol

**Symptoms**: `cannot find symbol`, `Unresolved reference`, `ImportError`, `undefined: X`, `Module not found`

**Common causes:**
- Package not installed or wrong version
- Import path renamed/moved in a refactor
- Circular import
- Build cache out of date
- Case sensitivity mismatch (macOS vs Linux)

**Investigation steps:**
1. Run the package manager: `pub get`, `cargo build`, `npm install`, `pip install`, `go mod tidy`
2. Check if the symbol was renamed in recent commits (`git log -- <file>`)
3. Search for where the symbol is actually defined (`grep -r "class X\|def X\|fn X"`)
4. Clear build cache if type still not found after above steps

---

## Async / Concurrency Bug

**Symptoms**: Intermittent failures, data appears stale, race condition, deadlock, UI not updating

**Common causes:**
- `await` missing, causing promise/future to resolve later than expected
- State mutated from multiple threads without synchronization
- UI state read before async init completes
- Observer/listener removed while still needed
- Callback captured stale closure variable

**Investigation steps:**
1. Add logging/print at each async boundary to verify execution order
2. Check if the bug is deterministic or intermittent (intermittent → race condition)
3. Look for `setState` called after widget dispose (Flutter), or `this` used in stale closure (JS)
4. In Dart: check for missing `await` or missing `async` on function that calls `await`
5. In Rust: use `RUST_LOG=debug` and check for deadlocks with `cargo test -- --nocapture`

---

## Logic / Calculation Error

**Symptoms**: Wrong output value, off-by-one, incorrect calculation, unexpected loop behavior

**Common causes:**
- Off-by-one in index or range (< vs <=, 0-indexed vs 1-indexed)
- Integer overflow or precision loss
- Wrong operator precedence
- Incorrect conditional branch (wrong boolean logic)
- Early return missing in a branch

**Investigation steps:**
1. Add temporary `print` statements to trace intermediate values
2. Write a minimal reproduction case with known inputs and expected output
3. Check index boundaries carefully (does array start at 0 or 1?)
4. Verify operator precedence with parentheses
5. Use a debugger (breakpoint) if available

---

## Configuration / Environment Error

**Symptoms**: Works locally but not in CI/prod, missing API key, wrong URL, feature flag off

**Common causes:**
- `.env` file not committed or not loaded
- Environment variable name typo
- Different config file loaded per environment
- Feature flag disabled in target environment
- Certificate or TLS issue in production

**Investigation steps:**
1. Print all relevant env vars at startup to verify values
2. Compare `.env.example` with actual `.env`
3. Check CI/CD environment variable settings
4. Confirm config loading order (which file wins?)

---

## Dependency / Version Conflict

**Symptoms**: Build fails after `pub get`/`npm install`/`cargo update`, method not found that used to exist

**Common causes:**
- Dependency upgraded with breaking API change
- Two packages require incompatible versions of a shared dependency
- Lock file (pubspec.lock, Cargo.lock, package-lock.json) out of sync

**Investigation steps:**
1. Check `git diff pubspec.lock` or equivalent for changed versions
2. Read the changelog of the upgraded package for breaking changes
3. Pin the dependency to the last working version temporarily
4. Run `dart pub deps`, `cargo tree`, `npm ls` to see the full dependency tree

---

## File / Path Not Found

**Symptoms**: `FileNotFoundException`, `ENOENT`, `No such file or directory`

**Common causes:**
- Hardcoded path that differs between environments
- Asset not added to `pubspec.yaml` (Flutter)
- Working directory assumed wrong
- Case mismatch in file name on case-sensitive OS

**Investigation steps:**
1. Print the resolved absolute path just before the file operation
2. Verify file exists: `ls -la <path>`
3. Check if path is relative to working directory vs. script directory
4. In Flutter: confirm asset is declared in `pubspec.yaml` under `flutter.assets`

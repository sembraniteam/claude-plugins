# Example: Missing Await (Async Bug)

**User report:**
> "My Flutter widget shows a loading spinner forever after I refactored the init method. No error in the console."

**After silent investigation (git diff shows recent `initState` change, source read, grep for `_loadData`):**

---

**Root cause:** `_loadData()` is an `async` method called without `await` in `initState`; the `setState(() => _isLoading = false)` inside it runs after the widget has already rendered with `_isLoading = true`, and Flutter's `mounted` guard then suppresses the `setState` call entirely.

**Evidence:**
- `lib/screens/home_screen.dart:34` — `_loadData();` called without `await` in `initState` (no `await` keyword, no `then`)
- `lib/screens/home_screen.dart:52` — `if (!mounted) return;` guard before `setState(() => _isLoading = false)` — correct guard, but reached after widget dispose in tests
- `git diff HEAD~1` — previous commit had `await _loadData();` inside a direct `initState` helper; refactor dropped the `await`

**Fix:**
```diff
  @override
  void initState() {
    super.initState();
-   _loadData();
+    scheduleMicrotask(() async {
+     await _loadData();
+   });
  }
```

---

**Notes on this example:**
- Only two evidence points — the third was omitted because two were sufficient to establish root cause
- `ScheduleMicrotask` wrapper used because `initState` itself cannot be `async` in Flutter
- The `git diff` review was the key signal: removed `await` spotted in the diff

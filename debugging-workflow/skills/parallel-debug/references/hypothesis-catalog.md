# Hypothesis Catalog

Organized by symptom. For each bug report, match the observed symptom to a category, then select the most plausible hypotheses to investigate — `hypothesis_count` of them (2–4, default 3; see `.claude/debugging-workflow.local.md`). Prefer hypotheses that align with recently changed code (`git diff`) and the detected language.

---

## Symptom: Crash / Null Dereference

**Error patterns**: `NullPointerException`, `null is not an object`, `AttributeError: 'NoneType'`, `unwrap() on None`, `nil pointer dereference`, `EXC_BAD_ACCESS`, `Segmentation fault`

| Hypothesis                     | Mechanism                                                                                               | Most common in                      |
|--------------------------------|---------------------------------------------------------------------------------------------------------|-------------------------------------|
| `missing-null-guard`           | Non-null value assumed at call site, but function can legitimately return null/None/nil                 | All languages                       |
| `deferred-init-accessed-early` | `late`/`lazy` field accessed before the initializing async call completes                               | Dart, Kotlin                        |
| `pass-by-value-copy`           | Object copied at assignment; mutation applied to the copy, not the original, leaving original nil/empty | Go (struct receivers), Rust, Python |
| `destroyed-object-callback`    | Object accessed inside a callback that fires after the object has been deallocated/disposed             | Flutter, C++, Objective-C           |
| `concurrent-null-write`        | Race condition: one thread sets field to null between another thread's null-check and field access      | Java, Go, Kotlin                    |

**Key indicators**: recent removal of null-check guards, optional chaining (`?.`) removed, `!` added, `@NonNull` annotation removed, new async code path

---

## Symptom: Wrong / Unexpected Value

**Error patterns**: assertion failures, wrong output in logs, `expected X but got Y`, test fails on value comparison, calculation is off

| Hypothesis                  | Mechanism                                                                     | Most common in             |
|-----------------------------|-------------------------------------------------------------------------------|----------------------------|
| `stale-state`               | Cached or memoized value not invalidated when upstream data changed           | All languages              |
| `pass-by-value-mutation`    | Caller mutates a copy, expecting the original to change                       | Go, Rust, Python, Java     |
| `integer-overflow`          | Value exceeds type bounds; wraps or truncates silently                        | Rust (`u8`), C, Java, Dart |
| `floating-point-precision`  | Floating-point arithmetic accumulates error; equality comparison fails        | All languages              |
| `off-by-one-boundary`       | `<` vs `<=`; 0-indexed vs 1-indexed; exclusive vs inclusive range             | All languages              |
| `wrong-operator-precedence` | Expression evaluated in wrong order due to missing parentheses                | All languages              |
| `type-coercion-loss`        | Implicit cast between int/float, string/number, or bool/int drops information | JS, Python, PHP            |

**Key indicators**: recent changes to a computed value or cache, test expectations changed, recently added math or index operations

---

## Symptom: Stale / Outdated Data

**Error patterns**: UI shows old data after update, API returns cached response, feature flag not taking effect, config change not reflected

| Hypothesis               | Mechanism                                                                         | Most common in              |
|--------------------------|-----------------------------------------------------------------------------------|-----------------------------|
| `cache-no-invalidation`  | In-memory or HTTP cache not cleared after a mutation                              | All languages               |
| `stale-closure-capture`  | Closure captures variable by value at creation time, not at call time             | JS/TS, Dart, Python         |
| `static-field-singleton` | Class-level/static field persists data across test runs or instances              | Java, Kotlin, Dart          |
| `build-cache-stale`      | Generated code or compiled artifacts not regenerated after source change          | All languages (build tools) |
| `provider-not-notifying` | State change object does not call `notifyListeners()` / `setState()` / emit event | Flutter, React, Android     |

**Key indicators**: works after restart/clean build, issue appeared after adding caching, state management recently changed

---

## Symptom: Async / Timing Issue

**Error patterns**: intermittent failures, "works sometimes", data appears before it's loaded, UI updates out of order, test passes alone but fails in suite

| Hypothesis                    | Mechanism                                                                          | Most common in                |
|-------------------------------|------------------------------------------------------------------------------------|-------------------------------|
| `missing-await`               | `async` function called without `await`; caller reads result before it resolves    | Dart, JS/TS, Python           |
| `race-condition-shared-state` | Two concurrent operations read-modify-write the same field without synchronization | Go, Rust, Java, Dart isolates |
| `timer-test-interference`     | Timer or `Future.delayed` in production code fires unpredictably during tests      | Dart, JS/TS                   |
| `disposed-after-async`        | Widget/object used in an async callback after it was disposed/unmounted            | Flutter, React                |
| `event-listener-ordering`     | Event fired before listener registered; initialization order wrong                 | JS, Dart streams              |

**Key indicators**: error is intermittent, error appears only under load or in parallel test runs, recently added async code

---

## Symptom: Build / Compile Error

**Error patterns**: `cannot find symbol`, `Unresolved reference`, `ImportError`, `undefined: X`, `Module not found`, `Type X is not assignable to Y`

| Hypothesis                    | Mechanism                                                                                          | Most common in              |
|-------------------------------|----------------------------------------------------------------------------------------------------|-----------------------------|
| `dependency-version-conflict` | Upgraded package has breaking API change; or two packages require incompatible transitive versions | All languages               |
| `lock-file-out-of-sync`       | `pubspec.lock`/`Cargo.lock`/`package-lock.json` differs from declared constraints                  | All languages               |
| `renamed-symbol`              | Import path or class/function name changed in a refactor; old name still referenced                | All languages               |
| `circular-import`             | Module A imports B which imports A, causing partial initialization                                 | Python, JS/TS, Dart         |
| `build-cache-corrupted`       | Incremental build cached a stale intermediate; clean build fixes it                                | All languages (build tools) |

**Key indicators**: error appeared after `pub get`/`npm install`/`cargo update`, recently renamed file or class

---

## Symptom: UI / Render Issue

**Error patterns**: layout overflow, widget rebuilds too often, incorrect visual state, animation jank, UI not updating after state change

| Hypothesis                 | Mechanism                                                                              | Most common in   |
|----------------------------|----------------------------------------------------------------------------------------|------------------|
| `layout-overflow`          | Unbounded flex child; content wider/taller than constrained parent                     | Flutter, CSS     |
| `missing-key-stateful`     | Stateful widget missing a `Key`; Flutter destroys and recreates instead of updating    | Flutter          |
| `rebuild-on-every-frame`   | Non-const widget or new object literal in `build()` forces full subtree rebuild        | Flutter          |
| `provider-over-listen`     | `context.watch()` where `context.read()` was intended, triggering unnecessary rebuilds | Flutter Provider |
| `css-specificity-conflict` | Two CSS rules apply to the same element; wrong one wins                                | CSS, React, web  |
| `z-index-stacking`         | Element rendered behind another due to stacking context                                | CSS, web         |

**Key indicators**: visual issue appeared after moving widget up the tree, after wrapping with a new parent, after dependency upgrade

---

## Symptom: Performance / Memory

**Error patterns**: memory leak, `OutOfMemoryError`, slow response, high CPU, increasing heap, OOM crash under load

| Hypothesis                | Mechanism                                                                              | Most common in          |
|---------------------------|----------------------------------------------------------------------------------------|-------------------------|
| `listener-not-removed`    | Event listener, stream subscription, or observer added but never removed on dispose    | Flutter, JS/TS, Android |
| `resource-leak`           | File handle, DB connection, or socket opened but never closed                          | All languages           |
| `infinite-rebuild-loop`   | State change triggers a rebuild that triggers the same state change                    | Flutter, React          |
| `quadratic-algorithm`     | Nested loop over growing input; acceptable at small scale, blows up at production size | All languages           |
| `large-object-in-closure` | Closure captures a large object, preventing GC                                         | JS/TS, Dart, Python     |

**Key indicators**: memory grows over time without plateau, issue appeared after adding event listeners or subscriptions, performance degrades linearly or worse with input size

---

## Symptom: Test Failure (Test Written Before Source Change)

**Error patterns**: previously passing test now fails, test regression after a refactor

| Hypothesis                 | Mechanism                                                                                 | Most common in        |
|----------------------------|-------------------------------------------------------------------------------------------|-----------------------|
| `mock-contract-drift`      | Mock does not reflect updated API of the real implementation                              | All languages         |
| `test-ordering-dependency` | Test passes in isolation but fails when run after another test that pollutes shared state | All languages         |
| `snapshot-outdated`        | Snapshot test has stale expected output after intentional UI change                       | JS/TS (Jest), Flutter |
| `env-var-not-set-in-ci`    | Test depends on env variable set locally but not in CI                                    | All languages         |
| `flaky-timing`             | Test has hardcoded delay or timeout that works locally but fails on slow CI runners       | All languages         |

---

## Hypothesis Selection Guide

When generating hypotheses for a specific bug report, apply this order of preference:

1. **Match exact error string** — look up the error message in the symptom tables above
2. **Check `git diff`** — hypotheses involving recently changed code rank higher
3. **Language affinity** — prefer hypotheses common in the detected language
4. **Intermittency** — if the bug is intermittent, bias toward async/concurrency hypotheses
5. **"Works on my machine"** — if the bug is environment-specific, bias toward config/env/dependency hypotheses
6. **Diversity** — ensure the selected hypotheses cover distinct failure mechanisms (don't pick multiple variations of "null pointer")

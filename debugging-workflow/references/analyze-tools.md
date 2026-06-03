# Analyze Tools Reference

Language detection → tool mapping with flags, common errors, and fix patterns.

---

## Dart / Flutter

**Detection**: `pubspec.yaml` in root, or `.dart` files

### Tools

```bash
# Pure Dart project
dart analyze

# Flutter project
flutter analyze

# Format check (non-destructive)
dart format --output=none --set-exit-if-changed .

# Fix auto-fixable issues
dart fix --apply
```

### Common Errors

| Error                                           | Cause                          | Fix                                             |
|-------------------------------------------------|--------------------------------|-------------------------------------------------|
| `The method 'X' isn't defined`                  | Typo or missing import         | Add import or check spelling                    |
| `A value of type 'X?' can't be assigned to 'X'` | Null safety violation          | Add null check `??`, `!`, or `if (x != null)`   |
| `The getter 'X' isn't defined`                  | Missing property or wrong type | Check class definition, add `.?` if nullable    |
| `'await' can only be used in 'async'`           | Missing async keyword          | Add `async` to function signature               |
| `Avoid using `BuildContext` across async gaps`  | Mounted check missing          | Add `if (!context.mounted) return;` after await |

### Best Practices
- Use `final` and `const` wherever possible
- Prefer `?` nullable types over non-nullable with `!` operator
- Always check `context.mounted` after async gaps in Flutter widgets
- Use `late` only when initialization is guaranteed

---

## Rust

**Detection**: `Cargo.toml` in root, or `.rs` files

### Tools

```bash
# Check for compile errors (fast)
cargo check

# Lint with suggestions
cargo clippy

# Clippy with all warnings as errors
cargo clippy -- -D warnings

# Format check
rustfmt --check src/main.rs

# Format fix
cargo fmt

# Run with backtrace on panic
RUST_BACKTRACE=1 cargo run
```

### Common Errors

| Error                                                                 | Cause                                | Fix                                                      |
|-----------------------------------------------------------------------|--------------------------------------|----------------------------------------------------------|
| `cannot borrow X as mutable because it is also borrowed as immutable` | Borrow conflict                      | Restructure borrows; use clone or refcell                |
| `use of moved value`                                                  | Value moved into closure or function | Clone before move, or pass reference                     |
| `mismatched types`                                                    | Wrong type passed                    | Check function signature; use `.into()` or explicit cast |
| `the trait X is not implemented for Y`                                | Missing trait impl or wrong type     | Implement trait or use correct type                      |
| `unwrap() called on None`                                             | `.unwrap()` on Option/Result         | Replace with `?`, `.unwrap_or()`, or `match`             |

### Best Practices
- Use `?` for error propagation instead of `.unwrap()` in library code
- Prefer `match` or `if let` over `.unwrap()` for handling Options/Results
- Use `#[derive(Debug)]` on custom types for better error messages
- Avoid `clone()` in hot paths; use references

---

## TypeScript / JavaScript

**Detection**: `package.json`, `tsconfig.json`, `.ts`/`.tsx`/`.js`/`.jsx` files

### Tools

```bash
# TypeScript type checking (no emit)
npx tsc --noEmit

# ESLint on specific file
npx eslint src/myfile.ts

# ESLint on whole project
npx eslint .

# ESLint auto-fix
npx eslint --fix src/myfile.ts

# Prettier check
npx prettier --check src/myfile.ts
```

### Common Errors

| Error                                      | Cause                                 | Fix                                      |
|--------------------------------------------|---------------------------------------|------------------------------------------|
| `Object is possibly 'null' or 'undefined'` | Missing null check                    | Add `?.` optional chaining or null guard |
| `Property X does not exist on type Y`      | Wrong type or missing interface field | Update interface or use correct type     |
| `Cannot find module X`                     | Missing import or typo                | Check import path, run `npm install`     |
| `Type X is not assignable to type Y`       | Type mismatch                         | Cast, narrow, or update type definition  |
| `'X' is defined but never used`            | Dead code                             | Remove or prefix with `_`                |

### Best Practices
- Enable strict mode in `tsconfig.json`: `"strict": true`
- Avoid `any` type; use `unknown` with type guards
- Use `const` over `let`; never `var`
- Prefer async/await over raw Promise chains

---

## Python

**Detection**: `requirements.txt`, `pyproject.toml`, `setup.py`, `.py` files

### Tools

```bash
# Ruff (fast linter + formatter, modern)
ruff check .
ruff check --fix .
ruff format --check .

# Pylint
python -m pylint mymodule/

# MyPy (type checking)
python -m mypy mymodule/

# Flake8
flake8 mymodule/
```

### Common Errors

| Error                                 | Cause                         | Fix                                |
|---------------------------------------|-------------------------------|------------------------------------|
| `AttributeError: 'NoneType'`          | Variable is None unexpectedly | Add None check before access       |
| `ImportError: No module named X`      | Missing package or path issue | `pip install X` or fix sys.path    |
| `IndentationError`                    | Mixed tabs/spaces             | Use consistent spaces (4 spaces)   |
| `TypeError: unsupported operand type` | Wrong type in operation       | Cast or convert before operation   |
| `KeyError: 'X'`                       | Dict key missing              | Use `.get('X')` or check with `in` |

### Best Practices
- Use type hints: `def foo(x: int) -> str:`
- Use `pathlib.Path` over `os.path`
- Use `with` for file operations
- Prefer f-strings over `.format()` or `%`

---

## Go

**Detection**: `go.mod`, `.go` files

### Tools

```bash
# Vet (official static analysis)
go vet ./...

# Build check
go build ./...

# Format check
gofmt -l .

# Format fix
gofmt -w .

# Run tests
go test ./...

# golangci-lint (comprehensive)
golangci-lint run
```

### Common Errors

| Error                             | Cause                  | Fix                                       |
|-----------------------------------|------------------------|-------------------------------------------|
| `undefined: X`                    | Missing import or typo | Add import or fix symbol name             |
| `cannot use X (type Y) as type Z` | Type mismatch          | Convert explicitly                        |
| `declared but not used`           | Unused variable        | Remove or use `_` blank identifier        |
| `nil pointer dereference`         | Nil check missing      | Add `if x == nil` guard                   |
| `goroutine leak`                  | Goroutine not closed   | Use context cancellation or done channels |

### Best Practices
- Check all errors: `if err != nil { return err }`
- Use `context.Context` for cancellation
- Prefer table-driven tests
- Use `defer` for cleanup (file close, mutex unlock)

---

## Java / Kotlin

**Detection**: `pom.xml`, `build.gradle`, `build.gradle.kts`, `.java`, `.kt` files

### Tools

```bash
# Maven compile
mvn compile -q

# Gradle build
./gradlew build

# Gradle check (includes tests + lint)
./gradlew check

# Android lint
./gradlew lint

# ktlint (Kotlin)
ktlint src/**/*.kt

# ktlint fix
ktlint --format src/**/*.kt
```

### Common Errors

| Error                           | Cause                        | Fix                               |
|---------------------------------|------------------------------|-----------------------------------|
| `NullPointerException`          | Null reference accessed      | Add null check or use Kotlin `?.` |
| `ClassCastException`            | Wrong type cast              | Use `instanceof`/`is` check first |
| `cannot find symbol`            | Missing import or typo       | Add import statement              |
| `Smart cast to X is impossible` | Mutability conflict (Kotlin) | Use `val` or local copy           |
| `Unresolved reference` (Kotlin) | Missing dependency or import | Add import or Gradle dependency   |

---

## Swift

**Detection**: `.swift`, `Package.swift`, `.xcodeproj`

### Tools

```bash
# SwiftLint
swiftlint lint

# SwiftLint with fix
swiftlint --fix

# Swift Package build
swift build

# Swift Package tests
swift test
```

---

## Ruby

**Detection**: `Gemfile`, `.rb` files

### Tools

```bash
# RuboCop
rubocop

# RuboCop auto-fix
rubocop -A

# RSpec tests
bundle exec rspec
```

---

## C / C++

**Detection**: `CMakeLists.txt`, `Makefile`, `.c`, `.cpp`, `.h` files

### Tools

```bash
# CMake build
cmake --build build/

# Clang-Tidy
clang-tidy src/main.cpp -- -std=c++17

# Cppcheck
cppcheck --enable=all src/

# Address Sanitizer (compile flag)
# Add -fsanitize=address to compiler flags
```

---

## Multi-Language Projects

For projects mixing multiple languages (e.g., Flutter with Rust via FFI, or Node.js backend with Python scripts):

1. Detect primary language from the file where the error occurred
2. Run the primary language's tools first
3. If the bug touches the boundary (FFI, IPC, API), run tools for both languages
4. Check shared configuration files (env vars, JSON configs) separately

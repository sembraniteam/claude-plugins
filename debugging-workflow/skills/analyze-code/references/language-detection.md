# Language Detection

Detect the primary language by checking for marker files in priority order (first match wins):

| Priority | Marker file(s)                                       | Language        |
|----------|------------------------------------------------------|-----------------|
| 1        | `pubspec.yaml`                                       | Dart / Flutter  |
| 2        | `Cargo.toml`                                         | Rust            |
| 3        | `tsconfig.json` or any `.ts` / `.tsx` file           | TypeScript      |
| 4        | `package.json` (no tsconfig present)                 | JavaScript      |
| 5        | `go.mod`                                             | Go              |
| 6        | `requirements.txt`, `pyproject.toml`, or `setup.py`  | Python          |
| 7        | `pom.xml`                                            | Java / Maven    |
| 8        | `build.gradle` or `build.gradle.kts`                 | Kotlin / Gradle |
| 9        | `Package.swift` or `.xcodeproj`                      | Swift           |
| 10       | `Gemfile`                                            | Ruby            |
| 11       | `CMakeLists.txt` or `Makefile`                       | C / C++         |

**Rules:**
- Use the **first match** in priority order — do not combine multiple detections.
- For Dart: if `pubspec.yaml` contains `flutter:` as a top-level key, treat as Flutter; otherwise pure Dart.
- If no marker file is found, ask the user which language the project uses.

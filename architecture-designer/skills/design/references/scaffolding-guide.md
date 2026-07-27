# Project Scaffolding Guide

Guidance for `implementation-planner` (Step 3) and `architecture-implementer` (Step 2's "Scaffolding step"): when
bootstrapping a brand-new project, prefer invoking the confirmed stack's **official project generator CLI** over
hand-authoring the initial boilerplate (`package.json`, `tsconfig.json`, `go.mod`, `Cargo.toml`, framework config, base
folder skeleton) file by file.

## Why generate instead of hand-author

An official generator (`cargo new`, `flutter create`, `go mod init`, `npx create-next-app@latest`, and the others below)
encodes whatever that ecosystem's current best-practice layout and compatible dependency versions are *at the moment it
runs* — a real command execution, not a recollection. A model hand-writing `package.json`/`tsconfig.json`/framework
config from memory routinely gets subtly wrong: a dependency-version pairing that doesn't actually resolve, a config key
a recent major version renamed or removed, a default that changed. This is the same "verify, don't fabricate" discipline
`design/SKILL.md`'s version-grounding rule already applies to Stage 5 — running the generator *is* the verification step
for everything it touches.

## When this applies

**Only for a brand-new project** — the confirmed strategy is `Fresh start (empty project)`. For `Merge`,
`Fresh start (existing project)`, or `User-described layout`, never propose a scaffold step, regardless of whether a
generator exists for the confirmed stack: the target directory already has its own project files, and running a
generator into it will conflict with or overwrite them — exactly what those strategies exist to prevent. Proceed
straight to the per-file hand-authored checklist for those strategies, unchanged from before this guide existed.

## Non-interactive invocation is mandatory

Every command below must run without its interactive prompt wizard — an agent cannot answer a stdin prompt, and a
generator left waiting on one will hang the run until timeout. Pass whatever flag set skips the wizard; where a tool has
no such flag for a given choice, redirect empty input (`< /dev/null`) or set the tool's documented CI/non-interactive
environment variable (many JS scaffolders honor `CI=1`) rather than leaving it interactive.

**CLI flags drift across tool versions.** The commands below are the canonical *base* invocation for each generator;
before running one, prefer confirming its current flag set with that tool's own `--help` (e.g.
`npx create-next-app@latest --help`) over trusting a long remembered flag list verbatim — the same discipline as Stage
5's version-grounding rule, applied to CLI surface instead of package versions.

## Generator table

| Stack                                                        | Generator command                                                                                                                                                                                                                             | Produces                                                                      | Still hand-authored on top                                                                                                                        |
|--------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| Next.js (React/TS)                                           | `npx --yes create-next-app@latest <name> --typescript --eslint --tailwind --app --use-npm`                                                                                                                                                    | App Router structure, `package.json`, `tsconfig.json`, ESLint/Tailwind config | ERD-derived models, API routes beyond the default, `docker-compose.yml`, `.env.example`, IaC                                                      |
| React SPA (Vite)                                             | `npm create vite@latest <name> -- --template react-ts`                                                                                                                                                                                        | `package.json`, `vite.config.ts`, `tsconfig.json`, base `src/`                | Routing, models, API client, `.env.example`                                                                                                       |
| Vue                                                          | `npm create vue@latest <name>` (set `CI=1` to accept defaults non-interactively, or check `-- --help` for explicit flags)                                                                                                                     | `package.json`, base `src/`, chosen-feature config                            | Routing/store wiring, API client                                                                                                                  |
| SvelteKit                                                    | `npx sv create <name>`                                                                                                                                                                                                                        | `package.json`, `svelte.config.js`, base `src/`                               | Routes, models, API client                                                                                                                        |
| Nuxt                                                         | `npx nuxi@latest init <name>`                                                                                                                                                                                                                 | `package.json`, `nuxt.config.ts`, base `app/`                                 | Pages, models, API client                                                                                                                         |
| Angular                                                      | `npx @angular/cli@latest new <name> --routing --skip-git`                                                                                                                                                                                     | Full app skeleton, `angular.json`, `tsconfig.json`                            | Components/services per feature, API client                                                                                                       |
| Astro                                                        | `npm create astro@latest <name>` (check `-- --help` for a non-interactive template flag)                                                                                                                                                      | `package.json`, `astro.config.mjs`, base `src/`                               | Pages, content collections                                                                                                                        |
| NestJS                                                       | `npx @nestjs/cli@latest new <name> --package-manager npm --skip-git`                                                                                                                                                                          | Full modular structure, `package.json`, `tsconfig.json`, test scaffolding     | ERD-derived entities/DTOs/modules beyond the default `AppModule`                                                                                  |
| Node/Fastify                                                 | `npm init fastify@latest <name>`                                                                                                                                                                                                              | `package.json`, base plugin structure                                         | Everything else — routes, models, `.env.example`                                                                                                  |
| Node/Express                                                 | *(no actively-maintained official generator)* — `npm init -y` then hand-add dependencies                                                                                                                                                      | `package.json` skeleton only                                                  | Everything — Express has no framework-official scaffolder to prefer here                                                                          |
| Python/Django                                                | `django-admin startproject <name> .` then `python manage.py startapp <app>` once per domain module/app named in the architecture                                                                                                              | `manage.py`, settings package, one empty app skeleton per `startapp` call     | Models still need writing from the ERD — `startapp` only creates an empty `models.py`                                                             |
| Python/FastAPI                                               | *(no single official generator)* — `python -m venv .venv && pip install fastapi uvicorn` is the closest ecosystem-standard bootstrap                                                                                                          | Virtualenv only                                                               | Everything — `pyproject.toml`, routers, models all hand-authored                                                                                  |
| Go (any framework)                                           | `go mod init <module-path>`                                                                                                                                                                                                                   | `go.mod`                                                                      | Everything else — Go has no full-project generator; `go mod init` is still the canonical first command, always run before hand-authoring the rest |
| Rust (any framework)                                         | `cargo new <name>` (or `cargo new --lib <name>` for a library crate; `cargo init` instead of `cargo new` when the target directory already exists and should become the project root)                                                         | `Cargo.toml`, `src/main.rs` or `src/lib.rs`, `.gitignore`                     | Everything else — Rust web frameworks (Axum, Actix) have no official scaffolder beyond `cargo new` + `cargo add <deps>`                           |
| Java/Spring Boot                                             | `curl https://start.spring.io/starter.zip -d dependencies=<comma-separated Spring Initializr artifact ids matching the confirmed stack> -d type=maven-project -d javaVersion=<confirmed version> -o <name>.zip && unzip <name>.zip -d <name>` | `pom.xml`/`build.gradle`, `Application.java`, base package structure          | Entities, repositories, controllers per ERD/sequence diagrams                                                                                     |
| .NET                                                         | `dotnet new webapi -n <name>` (or `dotnet new sln` first, for a multi-project solution)                                                                                                                                                       | `.csproj`, `Program.cs`, a base controller                                    | Models, `DbContext`, additional controllers                                                                                                       |
| Flutter                                                      | `flutter create <name> --org <reverse-domain> --platforms=<confirmed target platforms>`                                                                                                                                                       | Full app skeleton, `pubspec.yaml`, platform folders                           | Screens, models, state-management wiring                                                                                                          |
| React Native (Expo)                                          | `npx create-expo-app@latest <name>`                                                                                                                                                                                                           | App skeleton, `package.json`                                                  | Screens, models, API client                                                                                                                       |
| React Native (bare, only when Expo was explicitly ruled out) | `npx @react-native-community/cli@latest init <name>`                                                                                                                                                                                          | App skeleton, native platform folders                                         | Screens, models, API client                                                                                                                       |
| Ruby on Rails                                                | `rails new <name> --database=postgresql` (adjust `--database` to the confirmed engine)                                                                                                                                                        | Full MVC skeleton, `Gemfile`, `config/`                                       | Models/migrations per ERD, controllers per routes                                                                                                 |
| PHP/Laravel                                                  | `laravel new <name>` (requires the Laravel installer) or `composer create-project laravel/laravel <name>`                                                                                                                                     | Full skeleton, `composer.json`, `.env.example`                                | Models/migrations per ERD, controllers per routes                                                                                                 |
| Prisma ORM (inside an already-scaffolded Node project)       | `npx prisma init --datasource-provider <confirmed engine>`                                                                                                                                                                                    | `prisma/schema.prisma` stub, a `DATABASE_URL` entry                           | The actual schema models — hand-authored from the ERD, inside the generated `schema.prisma`                                                       |
| Monorepo (Turborepo)                                         | `npx create-turbo@latest <name>`                                                                                                                                                                                                              | Workspace root, example apps/packages                                         | Replace example apps/packages with the actual services per the confirmed architecture pattern                                                     |
| Monorepo (Nx)                                                | `npx create-nx-workspace@latest <name>`                                                                                                                                                                                                       | Workspace root, base config                                                   | Same as above                                                                                                                                     |

This table is not exhaustive — for a confirmed stack not listed, check whether that ecosystem has an equivalently
canonical bootstrap command before falling back to hand-authoring; the pattern generalizes (`<tool> new`, `<tool> init`,
`<tool> create-<thing>` are the common shapes).

## Working-directory handling

Most generators create a new subdirectory named after `<name>`. Two cases:

- **The project root is meant to be a new subdirectory** of the current working directory — run the command as-is; the
  plan's tree root corresponds to that subdirectory.
- **The current working directory itself is meant to be the project root** (the common case for this plugin, since
  `implement` scaffolds into wherever the user invoked it) — prefer the tool's own current-directory convention over
  creating a subdirectory and moving files up manually: pass `.` as `<name>` where the tool supports scaffolding into
  the current (empty) directory, or use a dedicated `init` variant instead of `new` (`cargo init` vs `cargo new`,
  `flutter create .`). Moving generated files up a level by hand is more error-prone and can lose `.gitignore`/git-init
  handling the generator would otherwise have applied correctly to the intended root — avoid it when the tool's own
  current-directory mode is available.

## Confirm the target location and check for a same-name project before scaffolding

`implement/SKILL.md` Step 2's existing-project scan only inspects the current working directory itself. It never looks
at a path the generator is about to *create* — and most generator commands take a `<name>` argument that becomes a
brand-new subdirectory (`npx create-next-app@latest my-app` creates `./my-app/`, `flutter create my-app` creates
`./my-app/`, `cargo new my-app` creates `./my-app/`). A collision at that path is invisible to Step 2's scan and would
otherwise only surface when the generator itself refuses to run — after the plan is already confirmed.

Two things must happen before a scaffold command is finalized, whether at planning time (`implementation-planner` Step

3) or immediately before execution (`architecture-implementer`'s Scaffolding step):

1. **Ask the user for the target location** if the command takes a `<name>`/subdirectory argument — don't silently
   invent a project name. Confirm whether the current working directory itself is the intended root (use the `.`/`init`
   convention above) or a new named subdirectory (and if so, what name).
2. **Check whether that resolved path already exists** — `test -d <resolved-path> && echo EXISTS || echo MISSING` (or
   `ls <resolved-path>` for a non-directory target). This applies even when Step 2's scan found the working directory
   itself empty, since a same-named subdirectory is a different path the scan never covered.

If the path already exists: do not run the generator into it. Surface the collision to the user the same way Step 2
surfaces an existing-project collision, and ask how to proceed — pick a different name/location, or treat the existing
directory as the real merge target (re-run the existing-project scan against that path instead of assuming it's safe to
overwrite). Never let a generator run silently overwrite or merge into a directory nobody confirmed was empty.

## Verifying success before proceeding

After running a generator command: check its exit code, then confirm the "Produces" column's key file (s) actually exist
(`test -f package.json && echo EXISTS || echo MISSING`, `test -f go.mod`, `test -f Cargo.toml`, etc.) — the same binary
EXISTS/MISSING discipline `architecture-implementer` already applies to every hand-written file. Only once confirmed
does the rest of the plan's checklist begin. If the command fails or the expected files don't appear, this is a blocker,
not a file to mark `[ ] FAIL` and move past — nothing else in the plan can safely proceed against a scaffold that didn't
actually complete; stop and report it the same way any other mid-run blocker is reported.

## When no generator exists — hand-authoring is the correct outcome, not a fallback failure

Some confirmed stacks (a hand-picked Express/Fastify-plus-custom-libraries combination, a bespoke FastAPI layout, any Go
project beyond `go mod init`) have no official all-in-one generator. Run whatever minimal bootstrap command does exist
(`go mod init`, `npm init -y`) — that's still preferred over hand-authoring even the minimal file — but everything
beyond that minimal step is correctly hand-authored via the existing per-file checklist. This is the "generate first"
priority correctly evaluated for a stack with nothing fuller to prefer, not a failure to follow it.

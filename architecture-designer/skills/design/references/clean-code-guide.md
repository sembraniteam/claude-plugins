# Clean Code and Testable Code Guide

Use this guide at Step 10 (Business Rules — how rule logic is phrased) and by `architecture-implementer` when writing
and testing actual service/class code, per `design/SKILL.md`. Where `references/design-principles-guide.md` and
`references/design-patterns-guide.md` decide how classes are shaped and how they collaborate, this guide decides how the
code *inside* a single function, method, or test is written — the level closest to what actually ships, and the level
where an otherwise-correct design most often decays into something no one wants to touch.

**Attribution**: the Clean Code principles below, including the FIRST properties for unit tests, are from *Clean Code: A
Handbook of Agile Software Craftsmanship* (Robert C. Martin, 2008, chapter 9). The test-double taxonomy is from Gerard
Meszaros's *xUnit Test Patterns* (2007), popularized by Martin Fowler.

## Why this matters

A class diagram can be perfectly shaped — correct responsibilities, correct dependencies, the right pattern named — and
the resulting code can still be unreadable and untested a month later if the functions inside it are long, the names are
vague, the errors are swallowed, and nothing is written with a seam a test can substitute. Clean Code is the practice of
keeping the *inside* of a well-shaped class as easy to read and change as the diagram promised; testability is not a
separate concern bolted on afterward but a direct consequence of the same discipline (small, single-purpose functions
with explicit dependencies are, almost automatically, easy to test in isolation — see "Testability is a design
consequence, not an afterthought" below).

---

## Part 1 — Clean Code Principles

### Naming

- Use intention-revealing names — a name should answer why it exists, what it does, and how it's used without needing a
  comment. `daysSinceLastLogin` over `d`; `cancelOrder(reason)` over `process(o, r)`.
    - **Avoid disinformation** — a name that implies something the code doesn't do (a variable named `accountList` that
      is actually a `Set`) is worse than a merely bland name.
- Use pronounceable, searchable names — a single-letter or abbreviated name is fine only for a tiny scope (a loop index
  in a three-line loop), never for anything with wider reach.
- Class names are nouns (`OrderService`, `PaymentGateway`); method names are verbs (`calculateTotal`,
  `sendConfirmation`)
  — this is the same convention `references/diagrams-guide.md`'s Class Diagram template already uses, so a class diagram
  built to that convention is already naming things the Clean Code way by construction.
- One word per concept — don't mix `fetch`, `retrieve`, and `get` for the same kind of operation across the codebase;
  pick one verb and use it consistently. This is a narrower, code-level instance of the same consistency
  `references/design-principles-guide.md`'s DRY section applies to duplicated logic — here it's duplicated *vocabulary*
  for one concept.

### Functions

- **Small, and do one thing.** A function longer than fits on one screen, or whose body mixes several levels of
  abstraction (parsing a request *and* calculating tax *and* formatting a log line), should be split — each extracted
  piece becomes independently readable, testable, and reusable. This is Single Responsibility
  (`references/design-principles-guide.md`) applied at the function level rather than the class level.
- **One level of abstraction per function.** A function that reads `validateInput (); const total = subtotal * (1 - d)
    + shipping; auditLog.write (...)` mixes a high-level call, a low-level arithmetic expression, and an I/O call in one
  body — extract the arithmetic into a named function (`calculateTotal (...)`) so every line in the caller reads at the
      same altitude.
- **Few arguments.** Zero, one, or two parameters is easy to read and easy to test; three or more, especially several of
  the same primitive type in a row (`createUser(string, string, string, boolean)`), is error-prone at every call site
  and a signal to introduce a small parameter object (also a Builder candidate per
  `references/design-patterns-guide.md` when construction is multi-step) instead.
- **No side effects a name doesn't advertise.** A method named `checkPassword(password)` that, as a side effect, also
  resets the user's session should not exist under that name — a caller reading the call site has no way to know the
  session gets touched. Command-Query Separation formalizes this: a method should either be a command that changes state
  and returns nothing meaningful, or a query that returns data and changes nothing — never both. This is the same
  discipline `references/design-principles-guide.md`'s Tell-Don't-Ask section applies from the opposite direction
  (commands act on an object's own state instead of exposing it) — CQS is what keeps a command from also secretly being
  a query, or vice versa.
- **Prefer exceptions to error codes, and avoid deep nesting.** A function riddled with `if (error) { return -1 }`
  checks forces every caller to remember to check the return value, and the happy path gets buried in error-handling
  noise. Raise/throw on failure (mapped to the LLD's Error Catalog — see "Error handling" below) and keep the happy path
  visually flat.

### Comments

- **Prefer code that doesn't need a comment to explain what it does** — a well-named function and well-named variables
  make most explanatory comments redundant, and a redundant comment is a second thing that can silently go stale when
  the code beneath it changes.
- **A good comment explains why, not what** — a non-obvious constraint, a workaround for a specific external bug, or a
  business reason a reader couldn't infer from the code itself is worth writing down; restating what the next line
  already says in English is not.
- Never leave commented-out code, or a comment recording who changed what and when — that's what version control is for.

### Formatting

- Keep formatting consistent within a codebase — rely on the language/framework's standard formatter and linter
  (`prettier`, `black`, `gofmt`, `rustfmt`) rather than hand-tuned spacing; this is a solved, automatable problem, not a
  design decision worth debating per file.
- Keep related code close together — a function and the small helpers it calls should live near each other, not
  scattered across the file in an order that doesn't match how they're read.

### Error handling

- **Handle errors as their own logical concern, not folded into the middle of business logic** — extract the try/catch
  or error-check body into its own function so the caller's happy path and the error path are each independently
  readable, rather than interleaved line-by-line.
- **Map every error to the LLD Error Catalog** (`references/lld-guide.md`) — a route/handler's failure path returns the
  matching error code from that catalog rather than an ad hoc message invented at the call site; this is what makes the
  Error Catalog authoritative rather than aspirational.
- **Never return or pass `null` where a caller must remember to check it.** Prefer an explicit "not found" signal the
  type system can enforce (an `Optional`/`Maybe` type, a language-idiomatic empty-collection return, or a typed
  exception) over a bare `null` a caller can forget to guard against — a `NullPointerException`/`undefined is not a
  function` three call frames away from the actual missing value is one of the most common, and most preventable, bug
  classes in exactly this style of layered CRUD system.

### Boundaries (third-party and external code)

- **Wrap third-party libraries and external APIs behind an interface owned by this codebase**, rather than letting
  vendor-specific types and calling conventions leak into business logic throughout the code — this is the Adapter
  pattern (`references/design-patterns-guide.md`) applied specifically at every external-dependency boundary, and it is
  also what makes the dependency substitutable with a test double (see Part 2). A service that calls
  `stripe.charges.create(...)` directly, scattered across a dozen call sites, has a dozen places to change if the
  payment provider is ever swapped or mocked; a service that calls its own `PaymentGateway.charge(...)` interface has
  one.

### Objects and data structures

- Keep the distinction clear between an object (hides its data behind behavior — see Tell, Don't Ask in
  `references/design-principles-guide.md`) and a plain data structure (exposes its data, has no meaningful behavior — a
  DTO per `references/lld-guide.md`). A hybrid that both exposes every field via a getter/setter *and* carries business
  methods gets the worst of both: callers reach into its state anyway (defeating encapsulation) while the class also
  pretends to be responsible for enforcing invariants it never actually gets to check.

---

## Part 2 — Testable Code Best Practices

### Testability is a design consequence, not an afterthought

Code that is hard to unit test is almost always also badly designed by the principles above — a function with hidden
global-state dependencies, a class that instantiates its own collaborators instead of receiving them (violating
Dependency Inversion / the Hollywood Principle, per `references/design-principles-guide.md`), or a method that mixes
business logic with I/O in one body, are all *both* Clean Code violations *and* the specific reasons a test ends up
needing a real database, a real clock, or a real network call to exercise a few lines of arithmetic. Fixing the design
issue and making the code testable are usually the same fix, applied once.

### Functional core, imperative shell

Separate pure business logic (no I/O, no mutation of anything outside its own arguments, same input always produces the
same output) from the imperative shell that performs I/O (database calls, HTTP requests, file access, the system clock).
A pricing calculation, a validation rule, or a state-transition check should be a pure function the LLD's Business Rules
already describe as a sequence of steps (`references/lld-guide.md`) — testing it needs no mocks, no database, and no
setup beyond the input values themselves. The imperative shell around it (loading the entity, calling the pure function,
persisting the result) is what actually needs test doubles, and there should be as little logic in that shell as
possible for the same reason functions should be small: the more decision-making logic is inside the pure core, the more
of it is testable without any infrastructure at all.

### Dependency injection for testability

A class that receives its collaborators through its constructor (per Dependency Inversion/the Hollywood Principle,
`references/design-principles-guide.md`) can have any of those collaborators replaced with a test double in a unit test,
with zero changes to the class itself. A class that constructs its own collaborators internally (`new
StripeGateway()` inside a method) cannot be tested without either hitting the real dependency or resorting to fragile
techniques (module-level monkey-patching, reflection hacks) that Clean Code and DIP both exist to make unnecessary.

### Test double taxonomy

Use the specific term for the specific role — a generic "mock everything" habit obscures what a test actually verifies:

| Type      | Behavior                                                                                                         | Use when                                                                                                                                                                           |
|-----------|------------------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Dummy** | Passed to satisfy a parameter list; never actually invoked                                                       | A required constructor argument the test doesn't exercise                                                                                                                          |
| **Stub**  | Returns a fixed, pre-programmed answer regardless of how it's called                                             | The test needs a collaborator to return a specific value so a particular code path is exercised                                                                                    |
| **Fake**  | A working, simplified implementation (an in-memory repository instead of a real database)                        | The test needs realistic behavior (state actually persists across calls within the test) without real infrastructure                                                               |
| **Spy**   | A real or wrapped implementation that records how it was called, for later inspection                            | The test needs to assert that a specific call happened, with specific arguments, after the fact                                                                                    |
| **Mock**  | Pre-programmed with expectations about the calls it *should* receive; fails the test itself if they don't happen | The test's actual point is verifying an interaction occurred (e.g. "the email service was called exactly once with this order's confirmation") rather than checking a return value |

Prefer a Stub or Fake over a Mock whenever the test is really checking a *return value or resulting state*, not an
*interaction* — over-using Mocks couples tests to a class's internal implementation details (which collaborator it calls
and how) rather than its observable behavior, making the test break on a harmless internal refactor even when the
behavior didn't change.

### FIRST principles for unit tests

- **Fast** — a unit test suite that takes minutes to run gets skipped; keep unit tests to milliseconds each by testing
  the pure functional core (above) rather than routing every test through real I/O.
- **Independent** — no test should depend on another test having run first, or on shared mutable state between tests;
  each test sets up its own fixtures.
- **Repeatable** — the same test run twice, in any environment, produces the same result; no reliance on the real system
  clock, real network availability, or a fixed database state left over from a previous run. Inject a clock/time source
  as a collaborator (same DI discipline as any other dependency) rather than calling `Date.now()`/`time.Now()` directly
  inside logic under test.
- **Self-validating** — a test either passes or fails with no manual inspection of output needed; no "check the log for
  the expected line."
- **Timely** — write the test close to when the code is written (per `architecture-implementer`'s existing "Test files"
  step, generated alongside every model and route group, not deferred to the end).

### Arrange-Act-Assert (AAA)

Structure every unit test in three clearly separated parts — set up the inputs and collaborators (Arrange), invoke the
one behavior under test (Act), then check the outcome (Assert). A test that interleaves setup, invocation, and
assertions throughout its body is harder to read than one with a visible three-part shape, and the shape itself makes it
obvious when a test is checking more than one behavior at once (a smell to split into separate tests, the same "one
thing per unit" discipline Clean Code applies to functions).

### One assertion concept per test

Test one logical behavior per test case, even if that takes more than one literal `assert` call to check (e.g. asserting
several fields of one resulting object is still one concept). A test that exercises and asserts on several unrelated
behaviors in one body makes a failure ambiguous — which of the several things being checked actually broke — and couples
unrelated behaviors to the same test's fate.

---

## Applying this guide across the workflow

- **Step 10, Business Rules**: write each rule's `Logic` section as the pure functional core described above — named,
  ordered steps with no I/O or persistence concern folded in (persistence belongs in the rule's `Post-conditions`,
  already a separate section per `references/lld-guide.md`). A rule whose steps read at inconsistent levels of
  abstraction, or that names more than a handful of steps, is a candidate to extract a named sub-rule, mirroring the
  Small-Functions guidance above.
- **`architecture-implementer`**: apply Part 1's naming, function-size, error-handling (mapped to the document's Error
  Catalog), and boundary-wrapping (third-party calls behind an owned interface) rules while generating service and
  route-handler code — this is in addition to, not instead of, the agent's existing structural rules from
  `references/design-principles-guide.md`. For the "Test files" step specifically, apply Part 2 directly: prefer a Fake
  or Stub over hitting a real database or external API, use AAA structure, inject any time/randomness source rather than
  calling it directly inside code under test, and pick the specific test-double type the assertion actually needs
  (state/return-value check → Stub/Fake; interaction check → Spy/Mock) rather than defaulting to a mock for everything.

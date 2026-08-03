# Critical Thinking and Decision-Making

A reasoning discipline applied at two points in this skill — Stage 5 (technology and architecture choices) and Step 10
group (2) (business rules) — to catch two specific failure modes this plugin's own reference material makes easy to fall
into: pattern-matching a plausible-sounding answer from `tech-stacks.md` or `design-patterns-guide.md` without it
actually fitting this project's stated problem, and transcribing a diagram into a business rule without asking why the
rule exists or what happens when it's violated.

## The core loop

Apply before finalizing any non-trivial decision:

1. **State the actual problem, not the pattern.** Before naming a technology or writing a rule, state in one sentence
   the specific requirement, constraint, or business reason driving the need for a decision here. If the sentence could
   describe any project ("need a database"), it isn't specific enough yet.
2. **Name the real constraints**, sourced from stages 1–4 (or, for a Step 10 rule, from the confirmed diagrams and
   NFRs) — never invented or assumed. A constraint with no stated source is a guess, not a constraint.
3. **Generate at least two genuinely different options** before picking one — not two flavors of the same idea. Only one
   option considered is a sign of pattern-matching to the first familiar answer rather than reasoning about the problem.
4. **Stress-test the leading option** — actively construct the strongest argument against it before writing it down.
   Ask: "What would have to be true for this to be the wrong choice?" and check whether that condition holds here.
5. **Decide and record the rejected alternative (s) with why** — not just what was chosen, but what was seriously
   considered and why it lost. A decision with no stated rejected alternative usually means only one option was ever
   generated (step 3).
6. **Name the revisit trigger** — the specific future condition (a changed NFR, a capacity number crossing a threshold,
   a new constraint) that would make this decision worth reconsidering. `references/revision-triggers.md`
   formalizes this for Stage 5; a Step 10 rule's revisit trigger is usually "the invariant it protects changes."

## Anti-patterns to catch

- **Familiarity bias** — choosing a technology because it's the most popular or the one most examples use, not because
  it satisfies a specific driver from `architecturalDrivers`. A recommendation justified only by "it's popular" or
  "it's what most projects use" hasn't passed step 4 yet.
- **Overengineering** — proposing a pattern, service split, or resilience mechanism the requirements don't call for (a
  circuit breaker for a system with no external dependency; microservices for a five-screen internal tool). Cross-check
  against `references/design-principles-guide.md`'s YAGNI section.
- **Underengineering** — silently dropping a stated NFR because the simplest option doesn't satisfy it, rather than
  naming the gap and either solving it or flagging it explicitly. A dropped requirement is a decision — make it with the
  same rejected-alternative reasoning as any other, not by omission.
- **Cargo-culting a business rule from the diagram** — writing a rule that restates what the sequence diagram shows
  without asking why the business needs it. A rule with no traceable business reason is a candidate for the DRY/YAGNI
  check in `references/design-principles-guide.md` — it may not need to exist at all.

## Applying this to Stage 5 (technology and architecture choices)

For each of the eleven items, before writing the final recommendation: run the six-step loop above. The existing
"every recommendation must cite a specific reason from stages 1–4" rule already enforces step 2 and part of step 5 —
this loop additionally requires step 3 (a genuine second option, not just the chosen one) and step 4 (the stress-test)
for any item where `architecturalDrivers` marks real tension, per `references/quality-driven-design-guide.md`'s
Trade-off and Risk Analysis pass. Not every item needs the loop written out at length — a small system's straightforward
choices can state it briefly ("Postgres vs. MySQL considered; Postgres chosen for JSONB support needed by AD-3; no
meaningful risk identified") — but skipping straight to a conclusion with no visible alternative is exactly what this
loop exists to catch.

## Applying this to Step 10 group (2) — business rules

For each business rule, before finalizing its `Logic`: name the invariant it protects and the business reason it exists
(tie back to a Stage 1 goal or Stage 2 requirement — a rule with no traceable reason is a YAGNI candidate, not a rule to
keep); state what happens on violation (reject the operation, compensate, queue for manual review — this feeds the error
catalog, group (5)); and name at least one edge case the rule must hold under (concurrent modification, a boundary
value, partial failure). This applies even to single-write rules with a business invariant to protect, not only the
multi-write rules the transaction-boundary check already probes.

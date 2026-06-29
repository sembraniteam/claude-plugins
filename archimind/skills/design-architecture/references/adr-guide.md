# Architecture Decision Record (ADR) Guide

An ADR is a short document that captures **one** architectural decision: the context that forced it, what was chosen, what was rejected, and what the consequences are. Unlike decision notes, an ADR is self-contained — a future engineer can read it cold and understand the rationale without access to the original conversation.

---

## ADR Template

Use this exact structure when writing the `## Architecture Decision Record` section of any archimind output document.

```markdown
## Architecture Decision Record

**ADR ID:** {timestamp_ms}-{topic}
**Date:** {ISO date}
**Status:** Accepted

### Context

{2–4 sentences: what problem is being solved, who the stakeholders are, and what constraints or forces shaped the decision space. Include the key requirements that mattered most — team size, scale, timeline, compliance — because these will change over time and future readers need to know what was true at the time of the decision.}

### Decision

**Chosen:** Option N — {Tier}: {Architecture Name}

{2–3 sentences on what was decided. Be specific about the pattern selected (e.g., "Modular Monolith with a BFF pattern serving the mobile client") rather than just the tier label.}

### Consequences

**Positive:**
- {What becomes easier or better as a result of this decision}
- {Scalability or maintainability gain}
- {Risk reduced}

**Negative / Trade-offs accepted:**
- {What becomes harder or more constrained}
- {Operational burden introduced}
- {Ceiling or reversibility cost}

**Neutral / Watch list:**
- {Things to revisit when conditions change — e.g., "reconsider caching strategy when DAU exceeds 50k"}

### Rejected Alternatives

| Option                    | Reason Rejected                                                                                                                                                             |
|---------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Option N — {Tier}: {Name} | {Specific reason — not "too complex" but "requires Kafka operational expertise the team does not have, and the async workload volume does not justify it at current scale"} |
| Option N — {Tier}: {Name} | {Specific reason}                                                                                                                                                           |

### Review Trigger

{One sentence: the signal that should prompt revisiting this ADR — e.g., "Revisit if sustained p95 latency exceeds 500ms, or if team grows beyond 15 engineers."}
```

---

## Why structured ADRs matter

Informal decision notes answer "what did we choose" but not "why did we reject the others." Six months after a decision, teams often re-debate options that were already considered — because the reasoning was never written down. A structured ADR short-circuits this by documenting the decision space, not just the outcome.

The **Rejected Alternatives** section is the highest-value part. The most common failure mode is vague rejections ("too complex", "we're not ready"). The rejection reason must name the specific constraint that made it unsuitable at the time — this lets a future reader judge whether that constraint still applies.

The **Review Trigger** converts a static record into a living one: it tells the team when the decision expires.

---

## ADR storage

ADRs written by archimind are embedded in the final architecture document (`docs/archimind/architecture/{timestamp_ms}-{topic}.md`). For long-lived projects, consider extracting ADRs into a dedicated `docs/adr/` directory and cross-linking them from the architecture document.

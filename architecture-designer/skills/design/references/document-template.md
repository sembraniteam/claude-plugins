# Architecture Document Body Template

The section order and content for the architecture document saved by `design/SKILL.md` Step 11, and revised by `review/SKILL.md` step 4f, which follows the same structure.

1. **Project Overview** — name, purpose, date, version
2. **Requirements Summary** — functional and non-functional requirements from stages 1–2
3. **Constraints and Feasibility** — from stage 3
4. **Capacity Planning** — from stage 4 with numeric estimates
5. **Technology Decisions** — stack, architecture pattern, database, infrastructure, observability strategy, and DR approach, with justifications from stages 1–4
6. **Architecture Diagrams** — every created diagram with: a heading, a paragraph description, then the mermaid code block. For the ERD, include the index list table immediately after the mermaid block.
7. **Database Design** — the full output from the database-designer agent (schema, ERD explanation, index plan, connection config), or database-fixer's corrected version if a fixer cycle ran — never the pre-fix original once a fix has been applied
8. **Infrastructure as Code** — IaC tool and justification, state backend config, module breakdown table (module name, what it provisions, environment-specific sizing), environment strategy, drift detection approach. Follow `iac-guide.md` § 6 for the exact format.
9. **CI/CD Pipeline** — platform and justification, pipeline stages table (stage, trigger, tool, gate), branching strategy, environment promotion rules, secret injection approach, artifact management. Follow `cicd-guide.md` § 7 for the exact format.
10. **Low-Level Design** — API contracts, business rules, DTOs (complex/shared only), inter-service contracts (microservices/event-driven only), and error catalog. Follow the section order and formatting from `lld-guide.md`.

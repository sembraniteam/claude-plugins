# Discovery Question Banks (Stages 1-4)

The full interview questions for Stages 1-4 of `design/SKILL.md`. Ask them conversationally rather than as a rigid checklist, but cover every question in the relevant stage before summarizing and moving on.

## Stage 1 — Requirements Gathering

Goal: understand what the application must do and why it exists.

1. **Application goal**: What is the primary purpose of this application? What problem does it solve?
2. **Stakeholders**: Who are the main users? Are there multiple user roles (admin, end-user, partner, etc.)?
3. **Business processes**: What are the key workflows users will perform? Walk me through the most important one step by step.
4. **Pain points**: What problems or limitations exist in the current process (if any) that this application should fix?
5. **Success criteria**: How will you know the application has succeeded? What metrics or outcomes matter?

Summarize answers, confirm, then proceed.

## Stage 2 — Requirements Analysis

Goal: separate functional from non-functional requirements.

**Functional requirements** (features):
- What are the core features the application must have at launch?
- Are there secondary features that are nice-to-have but not essential for v1?
- Are there any explicit non-goals (things the application will NOT do)?

**Non-functional requirements** (qualities):
- **Performance**: Are there response time targets? (e.g., "search results in under 500ms")
- **Security**: What data is sensitive? Are there compliance requirements (GDPR, HIPAA, PCI-DSS, SOC 2)?
- **Scalability**: Must the system scale horizontally? Is auto-scaling important?
- **Availability**: What is the acceptable downtime? (e.g., 99.9% SLA = ~8.7 hours/year)
- **Number of users**: How many concurrent users are expected at launch? At peak?

Summarize as two lists (functional and non-functional), confirm, then proceed.

## Stage 3 — Feasibility Study and Constraints

Goal: identify real-world constraints that will shape technical decisions.

- **Budget**: Is there a rough infrastructure budget per month? (Helps choose cloud tier, managed vs self-hosted)
- **Timeline**: What is the target launch date? How long is the development runway?
- **Regulations**: Any specific regulations to comply with? (data residency, encryption at rest requirements, audit logging)
- **Team competencies**: What languages, frameworks, and platforms does your team know well?
- **Legacy systems**: Are there existing systems this application must integrate with? (databases, APIs, authentication providers, message brokers)
- **Preferred cloud / infrastructure**: Any preference between AWS, GCP, Azure, on-premise, or bare metal?

Summarize constraints, confirm, then proceed.

## Stage 4 — Capacity Planning

Goal: produce concrete numbers that will drive infrastructure sizing and technology choices.

- **Users**: How many registered users are expected at launch? In 12 months? In 3 years?
- **Concurrent users**: At peak, how many users will be active simultaneously?
- **Transactions per second (TPS)**: Estimate the busiest operation (e.g., API requests, orders, messages). How many per second at peak?
- **Data volume**: How much data will be stored at launch? How fast does it grow per month?
- **Read/write ratio**: Is the workload read-heavy, write-heavy, or balanced?
- **Peak load patterns**: Are there predictable spikes? (e.g., end-of-month billing, flash sales, daily at 9 AM)
- **Geographic distribution**: Are users concentrated in one region or globally distributed?

Summarize with explicit numbers (estimates are fine — label them as estimates), confirm, then proceed.

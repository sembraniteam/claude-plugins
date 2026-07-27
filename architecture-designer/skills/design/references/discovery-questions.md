# Discovery Question Banks (Stages 1-4)

The full interview questions for Stages 1-4 of `design/SKILL.md`. Ask them conversationally rather than as a rigid
checklist, but cover every question in the relevant stage before summarizing and moving on.

## Stage 1 — Requirements Gathering

Goal: understand what the application must do and why it exists.

1. **Application goal**: What is the primary purpose of this application? What problem does it solve?
2. **Stakeholders**: Who are the main users? Are there multiple user roles (admin, end-user, partner, etc.)?
3. **Business processes**: What are the key workflows users will perform? Walk me through the most important one step by
   step.
4. **Pain points**: What problems or limitations exist in the current process (if any) that this application should fix?
5. **Success criteria**: How will you know the application has succeeded? What metrics or outcomes matter?
6. **App description**: Would you like to write a detailed description of the app yourself (a few sentences on what it
   is, who it's for, and the problem it solves), or should one be drafted from your answers above for you to approve?

Summarize answers, confirm, then proceed. If the user chose to have the description drafted, include the drafted
`description` text in this summary explicitly (not folded into the application-goal answer) so they can approve or edit
it alongside everything else.

## Stage 2 — Requirements Analysis

Goal: separate functional from non-functional requirements.

**Functional requirements** (features):

- What are the core features the application must have at launch?
- Are there secondary features that are nice-to-have but not essential for v1?
- Are there any explicit non-goals (things the application will NOT do)?

**Non-functional requirements** (qualities):

- **Performance**: Are there response time targets? (e.g., "search results in under 500ms")
- **Security**: What data is sensitive? Are there compliance requirements (GDPR, HIPAA, PCI-DSS, SOC 2)? Does the
  application need to preserve deleted records (audit trail, recovery, or "undo") rather than permanently removing them
  on delete? If a soft-deleted record's unique field (email, username) can be reused by a new registration, is immediate
  reuse acceptable, or is a cooldown period required first (e.g. to mitigate account-takeover/fraud via re-registering
  with a just-deleted identity)?
- **Scalability**: Must the system scale horizontally? Is auto-scaling important?
- **Availability**: What is the acceptable downtime? (e.g., 99.9% SLA = ~8.7 hours/year)
- **Error handling & resilience**: What should happen when a critical external dependency fails (payment gateway,
  third-party API, another internal service)? Is a degraded-but-available response acceptable for any feature, or must
  it fail outright? Are there operations that must never silently fail (e.g., payment capture) versus ones that can
  retry quietly in the background?
- **Rate limiting & abuse prevention**: Is any part of the API public-facing or reachable by untrusted/semi-trusted
  clients? Are there distinct user tiers (anonymous, authenticated, paid) that should get different limits? Are there
  endpoints that are especially sensitive to abuse (login, password reset, anything that triggers a metered external
  call)?
- **Offline support**: Must the application let users *create or edit* data during a meaningfully long offline period
  (not just view previously-loaded data, and not just tolerate a brief connectivity blip)? This distinction matters —
  most apps don't need more than a retry policy for the latter. If genuine offline writes are required: which data must
  be editable offline, and is it plausible for the same record to be edited on two devices before either syncs — if so,
  how should that conflict be resolved (see Stage 5's offline-first track, which only activates when this genuine
  offline-write need is confirmed)?
- **Concurrency shape**: Is this a genuinely multi-user, concurrent-access system, or mostly single-user/async at any
  given moment (e.g. a personal tool, a batch pipeline)? This is a qualitative NFR flag only — Stage 4 captures the
  actual concurrent-user numbers for capacity planning; do not ask for a figure here.

Summarize as two lists (functional and non-functional), confirm, then proceed.

## Stage 3 — Feasibility Study and Constraints

Goal: identify real-world constraints that will shape technical decisions.

- **Budget**: Is there a rough infrastructure budget per month? (Helps choose cloud tier, managed vs self-hosted)
- **Timeline**: What is the target launch date? How long is the development runway?
- **Regulations**: Any specific regulations to comply with? (data residency, encryption at rest requirements, audit
  logging)
- **Team competencies**: What languages, frameworks, and platforms does your team know well?
- **Legacy systems**: Are there existing systems this application must integrate with? (databases, APIs, authentication
  providers, message brokers)
- **Preferred cloud / infrastructure**: Any preference between AWS, GCP, Azure, on-premise, or bare metal?

Summarize constraints, confirm, then proceed.

## Stage 4 — Capacity Planning

Goal: produce concrete numbers that will drive infrastructure sizing and technology choices.

- **Users**: How many registered users are expected at launch? In 12 months? In 3 years?
- **Concurrent users**: At peak, how many users will be active simultaneously?
- **Transactions per second (TPS)**: Estimate the busiest operation (e.g., API requests, orders, messages). How many per
  second at peak?
- **Data volume**: How much data will be stored at launch? How fast does it grow per month?
- **Read/write ratio**: Is the workload read-heavy, write-heavy, or balanced?
- **Peak load patterns**: Are there predictable spikes? (e.g., end-of-month billing, flash sales, daily at 9 AM)
- **Geographic distribution**: Are users concentrated in one region or globally distributed? If globally distributed,
  are there recurring features (digests, reminders, scheduled reports) that must fire at a specific *local* time per
  user or region, rather than a fixed UTC instant — this determines whether timezone-aware scheduling is needed (see
  `references/timezone-guide.md`)?

Summarize with explicit numbers (estimates are fine — label them as estimates), confirm, then proceed.

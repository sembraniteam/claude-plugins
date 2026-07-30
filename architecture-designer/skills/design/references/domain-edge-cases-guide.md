# Domain Edge-Case Elicitation Guide

Use this guide at the end of Stage 2, after the functional/non-functional requirements from
`references/discovery-questions.md` are gathered but before Stage 2 is confirmed. It mitigates a specific, structural
limitation of this whole design process: a diagram or document can be syntactically correct, internally consistent, and
still miss a domain nuance the user simply never thought to mention. Every downstream check in this plugin (
`architecture-reviewer`, `document-reviewer`, `validate-diagrams.mjs`) can only verify what was *stated* — none of them
can detect the absence of a requirement nobody raised. The only point in the pipeline that can actually close that gap
is asking about it before Stage 2 confirmation, while the domain is still open for discussion.

## Why this matters

"Users can place orders" and "users can place orders, and a partially-shipped order can still be cancelled for its
unshipped items" describe two different systems, but only a domain expert (or someone who has been burned by the gap
before) reliably thinks to state the second version unprompted. Left unasked, the gap doesn't surface as a design flaw
during review — every diagram and document check downstream will pass cleanly, because there is nothing inconsistent
about a design that simply never considered partial cancellation. It surfaces later, as a costly discovery during
implementation or after launch. This guide is the plugin's one deliberate point of proactively working against that
failure mode, rather than only validating structural correctness of whatever was already said.

## Procedure

1. **Match, don't force**: read the confirmed functional requirements (not yet the final confirmation — this runs
   before that) and check them against the **Signal** column in the table below. A category applies only when its
   signal is actually present — do not ask payment questions for a system with no payment feature, the same
   don't-force-it discipline `references/resilience-guide.md`/`references/rate-limiting-guide.md` apply to their own
   scope conditions.
2. **Ask only the matched categories' questions**, folded conversationally into the same Stage 2 discussion rather than
   as a separate rigid checklist — mirroring how Stage 1's questions are already combined into a conversational flow per
   `design/SKILL.md`.
3. **A "no" or "out of scope" answer is a valid, complete answer** — the goal is surfacing the question, not forcing
   every edge case into scope. Record the answer either way (including "not supported — explicitly out of scope for
   v1") so the decision is visible in the document rather than silently absent.
4. **Fold the confirmed answers into the same Stage 2 summary and confirmation** — this is not a separate round-trip;
   presenting the matched questions and their answers together with the functional/non-functional requirements list, in
   the same "does this summary look correct" confirmation Stage 2 already ends with.
5. Write the confirmed list to `session.json`'s `stage2.domainEdgeCases` (array) at the same time as `stage2` — see
   `references/session-schema.md`.

## Domain categories

This table is not exhaustive — for a domain not listed, apply the same underlying method (what does an expert in this
domain get asked about that a non-expert wouldn't think to state?) rather than skipping the step entirely for an
unlisted domain.

### Authentication & Account Management

**Signal**: login, registration, user accounts, or roles/permissions mentioned in the functional requirements.

- What happens after N failed login attempts — lockout, delay, CAPTCHA, or nothing?
- Can a user have multiple active sessions/devices simultaneously? If a password is reset, do other sessions get
  invalidated?
- Is there an account-recovery path if the user loses access to their registered email/phone? What identity check
  gates it?
- What happens to a user's data when their account is deleted — hard delete, soft delete with a retention window, or
  anonymization? (Ties into the `database-designer` agent's soft-delete pattern at Stage 6a, if applicable.)
- Can a single person hold multiple roles at once, or is role assignment exclusive?

### Payments & Billing

**Signal**: payments, checkout, subscriptions, invoicing, or a payment gateway mentioned.

- Are partial refunds supported, or only full-order refunds?
- How is currency rounding handled (e.g., splitting a total across line items, tax calculation) — which party absorbs
  the rounding difference?
- What happens on a chargeback or disputed payment — is the associated order/service automatically suspended?
- For subscriptions: what happens on a failed renewal charge — retry schedule, grace period, immediate suspension?
- Is proration required for a mid-cycle plan upgrade/downgrade?

### Inventory & Order Fulfillment

**Signal**: inventory, stock, orders, warehouses, or fulfillment mentioned.

- Can stock go negative (backorder allowed), or is a sale blocked at zero stock?
- When two customers race to buy the last unit, how is the conflict resolved (first-committed-wins, reservation
  hold with expiry, overselling accepted and resolved manually)?
- Can a partially-shipped order be cancelled for only its unshipped items, or is cancellation all-or-nothing?
- Are returns tied to original stock location, or restocked centrally?

### Scheduling & Booking

**Signal**: appointments, bookings, reservations, or calendar/availability mentioned.

- Can two bookings overlap for the same resource, or is double-booking prevented — and if prevented, what's the
  conflict-resolution rule (first-committed-wins, waitlist)?
- What is the cancellation/rescheduling policy — how close to the scheduled time can a change be made, and is there a
  penalty?
- Do bookings need to account for time zones across participants (see `references/timezone-guide.md` for the
  storage/display split)?
- What happens to a recurring booking series when one instance is cancelled or rescheduled — does it affect the whole
  series or just that occurrence?

### Messaging & Notifications

**Signal**: notifications, alerts, email/SMS/push, or messaging between users mentioned.

- Can a user opt out of a given notification category, and does an opt-out ever get overridden (e.g., a security alert
  that must always send)?
- What happens if a notification fails to deliver (bounced email, undeliverable push token) — retried, logged, or
  silently dropped?
- For user-to-user messaging: can a message be edited or deleted after sending, and does the recipient see that it was
  edited/deleted?
- Is there a rate limit on outbound notifications per user, to avoid one event triggering a flood?

### Multi-tenancy & Permissions

**Signal**: organizations, teams, workspaces, or per-customer data isolation mentioned.

- Is tenant data isolated at the database-row level (shared schema with a tenant ID column) or fully separated
  (per-tenant schema/database)? This is a Stage 5/6a decision, but the *requirement* for isolation strength belongs
  here.
- Can a single user belong to multiple tenants/organizations? If so, how do they switch context, and can permissions
  differ per tenant?
- What happens to a tenant's data when the tenant's subscription/account is cancelled — immediate deletion, retention
  window, export offered?

### File Upload & Media

**Signal**: file upload, images, documents, or attachments mentioned.

- What file types and size limits are enforced, and what happens to a rejected upload (silent failure, explicit error
  with reason)?
- Are uploaded files scanned for malware/content-policy violations before being made accessible to other users?
- If a file is deleted, is it immediately purged from storage/CDN, or retained for a period (recovery, audit)?

### Search & Filtering

**Signal**: search, browse, or filter/sort functionality mentioned.

- Does search need to handle typos/fuzzy matching, or is exact/prefix matching sufficient?
- Are search results scoped by permission (a user should never see a result they don't have access to, even if the
  underlying index does)?
- What's the behavior when a search index falls behind the source data (eventual consistency) — is a brief staleness
  window acceptable, or does the feature need synchronous consistency?

## Format

Record each answered question as one entry:

```json
{
  "category": "Inventory & Order Fulfillment",
  "question": "Can a partially-shipped order be cancelled for only its unshipped items?",
  "answer": "No — cancellation is all-or-nothing for v1; partial cancellation is explicitly out of scope."
}
```

## Where this fits

Write the confirmed list to `session.json`'s `stage2.domainEdgeCases` at the same time as `stage2` (see
`references/session-schema.md`). It is folded into the architecture document's Requirements Summary section (section 3,
`references/document-template.md`) as a sub-list, not a separate numbered section — this is elaboration on existing
requirements, not a new deliverable category.

## Skip condition

None outright — every project has at least one matched category, since every system does *something* (even a system
with none of the eight categories above still benefits from applying the same underlying method to whatever domain it
actually is). A system matching zero categories from the table is the signal to apply the general method by hand
rather than skip the step — state explicitly which categories were considered and found not to apply, rather than
silently omitting the pass.

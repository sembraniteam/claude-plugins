# Timezone Handling Guide

Use this guide when finalizing datetime columns in Stage 6a (per `database-designer.md`'s Step 2) and whenever the
system has scheduled/recurring features (digests, reminders, cron jobs) that must respect a user's local time. It covers
what `TIMESTAMP WITH TIME ZONE` alone does not: where the UTC-vs-local conversion happens, and why a recurring job
defined in local time needs different handling than one defined as a fixed interval.

## Why this matters

- **Storage/display confusion** — `TIMESTAMP WITH TIME ZONE` (PostgreSQL's `timestamptz`) stores an absolute instant,
  not a timezone; the type name is misleading. It does not remember "the user's timezone" — it only guarantees the value
  is unambiguous regardless of the session's timezone setting. Deciding *where* the conversion to a human-local display
  happens is a separate, unstated design decision this type alone doesn't make.
- **DST silently breaks naive scheduling** — a recurring job stored as "run at a fixed UTC offset from midnight" drifts
  by an hour twice a year for any user in a DST-observing region, because the offset between their local time and UTC
  itself changes. This is one of the most common timezone bugs in production systems and is invisible in testing unless
  a DST transition is deliberately exercised.
- **Silent data corruption vs. loud failure** — a naive offset-math bug doesn't crash; it just produces a timestamp
  that's off by one hour twice a year, which is far more expensive to detect and fix after the fact than to design
  correctly up front.

## Core rule: UTC at rest, local at the edges

Store every absolute-moment timestamp in UTC in the database (`TIMESTAMP WITH TIME ZONE` / `timestamptz`, per
`database-designer.md`'s Step 2 data-type rule — the column type enforces unambiguous storage, this rule adds the policy
of *what* to store in it: UTC, always, never a pre-converted local value). Convert to a human-readable local time only
at the presentation layer:

- **Backend**: all comparisons, storage, and business logic (`WHERE created_at > ...`, "expires in 24 hours", sorting)
  operate on UTC instants — never on a locally-converted value. Comparing two timestamps that were each converted to
  "local time" before comparison is a common source of off-by-one-hour bugs; convert only for display, never before a
  comparison or calculation.
- **Frontend**: convert to the viewer's local timezone at render time, using the browser's own timezone (`Intl.
  DateTimeFormat().resolvedOptions().timeZone` in JS) or a user-configured display-timezone preference if the product
  needs one (e.g. a user viewing data collected in a different region than where they currently are).
- **API responses**: return ISO 8601 with an explicit UTC offset or `Z` suffix (`2026-07-24T14:30:00Z`) — never a bare,
  ambiguous local-looking string with no offset.

## Recurring/scheduled features: local-time jobs need timezone-aware scheduling

Distinguish two kinds of "future" a scheduled feature can mean, since they need different handling:

- **Fixed-interval or fixed-instant**: "run 24 hours from now," "expire at this exact UTC instant" — store and schedule
  this as a plain UTC instant. DST is irrelevant; the interval is unaffected by any calendar's local rules.
- **Recurring wall-clock local time**: "send the daily digest at 9 AM for each user's local time," "run the weekly
  report every Monday at 6 AM in the business's configured timezone" — this must be scheduled using an IANA timezone
  identifier (e.g. `America/New_York`, `Asia/Jakarta`), not a fixed UTC offset computed once. A scheduler that
  understands "9 AM `America/New_York`" adjusts automatically across DST transitions; a scheduler storing "9 AM UTC-5"
  silently fires at 8 AM or 10 AM local time for roughly half the year in any DST-observing region.

State explicitly, for every recurring feature, which of these two categories it is — this determines whether DST
handling is even a concern for that feature.

## What not to hand-roll

Do not hand-write UTC-offset arithmetic (`date.setHours(date.getHours() + offsetHours)`) to convert or schedule across
timezones — DST transitions, and regions that have changed their offset rules over time, make naive offset math wrong in
ways that only surface on specific calendar dates. Use a maintained timezone-database-aware library or the platform's
own timezone-aware scheduling primitive instead.

## Library / primitive per stack

| Stack                    | Datetime/timezone library                                                                                                                                                                                                                                                                                                                     | Timezone-aware scheduling                                                                                                                                                                              |
|--------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Node.js                  | Native `Temporal` (Stage 4 as of 2026, but ships unflagged only from Node.js 26 — this guide's own `tech-stacks.md` default of Node.js 24 needs the `--harmony-temporal` flag or a fallback; verify it's shipped, unflagged, in the target runtime version) or `date-fns-tz` / `Luxon` when the target runtime is below the unflagged version | `node-cron`/`node-schedule` with an explicit IANA `timezone` option, or a managed scheduler (e.g. cloud provider's cron with timezone support) — never a bare UTC cron expression for a local-time job |
| Python                   | Standard library `zoneinfo` (3.9+) or `pendulum`                                                                                                                                                                                                                                                                                              | Celery beat / APScheduler with an explicit `timezone` argument                                                                                                                                         |
| Go                       | Standard library `time.LoadLocation("America/New_York")`                                                                                                                                                                                                                                                                                      | A cron library that accepts a `*time.Location` (e.g. `robfig/cron` with `.WithLocation(...)`)                                                                                                          |
| Java / Spring            | `java.time.ZonedDateTime` / `java.time.ZoneId`                                                                                                                                                                                                                                                                                                | Spring's `@Scheduled(cron = "...", zone = "...")`                                                                                                                                                      |
| .NET                     | `DateTimeOffset` + `TimeZoneInfo`                                                                                                                                                                                                                                                                                                             | Quartz.NET with an explicit `TimeZoneInfo`, or `NCrontab.Advanced` with timezone support                                                                                                               |
| PostgreSQL (query-level) | `AT TIME ZONE 'IANA/Zone'` for display-time conversion in SQL                                                                                                                                                                                                                                                                                 | n/a — scheduling belongs in the application layer, not the database                                                                                                                                    |

Prefer whichever option is already the standard choice for the confirmed backend language/framework (Stage 5) over
introducing a second dependency purely for timezone handling.

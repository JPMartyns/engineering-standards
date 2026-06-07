# Incident Report Template — Post-Mortem

<!--
PURPOSE:
  A copy-and-fill template for documenting production incidents after
  resolution. The incident report (post-mortem) captures what happened,
  why it happened, how it was resolved, and what actions will prevent
  recurrence. This is a blameless document — it focuses on SYSTEMS
  and PROCESSES, not on individuals.

WHEN TO USE:
  - MUST use for every Critical and High severity incident
  - SHOULD use for Medium severity incidents
  - MAY use for Low severity incidents that reveal systemic issues
  - MUST complete within 1 week of incident resolution
  → See [07-security-standards.md, §16] for severity classification and response phases

WHEN TO CREATE:
  After Phase 5 (Post-Mortem) of the incident response process:
  Phase 1: Detection & Triage (Minutes 0–30)
  Phase 2: Containment (Minutes 15–60)
  Phase 3: Investigation & Eradication (Hours 1–48)
  Phase 4: Recovery (Hours 24–72)
  Phase 5: Post-Mortem (Within 1 Week) ← this template

WHERE TO SAVE:
  docs/incidents/YYYY-MM-DD-title-in-kebab-case.md
  Example: docs/incidents/2026-03-15-auth-endpoint-500-errors.md

BLAMELESS CULTURE:
  - Focus on systems and processes, not on individuals
  - Everyone involved had good intentions and did their best with the
    information available at the time
  - The goal is to learn and improve, not to assign fault
  - Use language like "the deployment process" not "developer X deployed"
  → See [11-project-management.md, §7.4] for the post-incident review checklist

SEVERITY CLASSIFICATION:
  | Severity | Description                                       | Response Time   |
  |----------|---------------------------------------------------|-----------------|
  | Critical | Active exploitation, data breach, service down    | Within 1 hour   |
  | High     | Confirmed vulnerability exploited, data exposure  | Within 4 hours  |
  | Medium   | Vulnerability confirmed, not yet exploited        | Within 24 hours |
  | Low      | Potential vulnerability, no evidence of exploit   | Within 1 week   |
  → See [07-security-standards.md, §16] for the full severity table

RGPD BREACH NOTIFICATION:
  If the incident involves personal data:
  - Supervisory authority (CNPD in Portugal): notify within 72 hours
  - Affected individuals: notify without undue delay if high risk
  → See [07-security-standards.md, §14 — Breach Notification]

REFERENCES:
  → See [07-security-standards.md, §16] — Incident response phases, severity, post-mortem structure
  → See [08-observability.md, §10.3] — Incident investigation checklist
  → See [11-project-management.md, §7.4] — Post-incident review checklist
  → See [04-database-standards.md, §12] — Recovery procedures for data incidents

AI AGENT INSTRUCTIONS:
  When using this template to create an incident report:
  1. Copy this file to docs/incidents/YYYY-MM-DD-title.md
  2. Replace all placeholder text (marked with < > angle brackets) with actual content
  3. Remove all HTML comments (<!-- -->) from the final document
  4. Fill in the timeline using UTC timestamps for consistency
  5. Focus root cause analysis on systems and processes — never blame individuals
  6. Every action item MUST have an owner, priority, and deadline
  7. Create tracked issues for each action item after completing the report
  8. Write in English — all technical documentation uses English
  9. If personal data was involved, check RGPD breach notification requirements
-->

---

# Incident Report: <Title — Brief Description of the Incident>

<!-- TITLE GUIDANCE:
  Good: "Auth endpoint returning 500 errors due to database connection exhaustion"
  Good: "API key exposed in public repository"
  Bad:  "Production issue" (too vague)
  Bad:  "John broke the auth system" (blameful — focus on systems, not people)
-->

## Metadata

| Field            | Value                                            |
|------------------|--------------------------------------------------|
| **Date**         | <YYYY-MM-DD>                                     |
| **Severity**     | <Critical / High / Medium / Low>                 |
| **Duration**     | <Detection to resolution — e.g., "2 hours 15 minutes"> |
| **Detection**    | <How was the incident detected? Alert, user report, monitoring, manual discovery> |
| **Incident Owner** | <Name of the person who coordinated the response> |
| **Author**       | <Name of the person writing this report>         |
| **Status**       | <Investigating / Contained / Resolved / Post-mortem complete> |

<!-- RGPD BREACH — uncomment this section if personal data was involved:

| **Personal Data Involved** | Yes / No                                |
| **Data Categories Affected** | <e.g., emails, names, payment data>   |
| **Users Affected**          | <Number or estimate>                   |
| **CNPD Notified**           | Yes / No / Not required — Date: YYYY-MM-DD |
| **Users Notified**          | Yes / No / Not required — Date: YYYY-MM-DD |
→ See [07-security-standards.md, §14 — Breach Notification] for notification requirements
-->

## Summary

<!-- Write a concise paragraph (3–5 sentences) describing:
     - What happened (the observable effect)
     - What was the root cause (one sentence)
     - What was the impact (who/what was affected)
     - How it was resolved (one sentence)

     This summary should give a reader a complete picture of the incident
     without needing to read the rest of the document. -->

<One paragraph describing what happened, the root cause, impact, and resolution.>

## Impact

<!-- Quantify the impact as specifically as possible. -->

- **Systems affected:** <Which services, endpoints, or infrastructure components were impacted>
- **Users affected:** <Number of users impacted, or "all users" / "subset of users in region X">
- **Duration of user impact:** <How long users experienced degraded or unavailable service>
- **Data impact:** <Was data lost, corrupted, or exposed? If yes, describe scope>
- **Business impact:** <Revenue loss, SLA breach, reputation impact — if measurable>

## Timeline

<!-- Create a detailed, chronological timeline from detection to resolution.
     Use UTC timestamps for consistency. Include all key events:
     - When the incident was first detected
     - When triage began
     - Key investigation findings
     - Containment actions taken
     - When the fix was deployed
     - When normal operations were restored
     - When post-incident monitoring confirmed stability

     The incident log created during Phase 1 (→ See [07-security-standards.md, §16])
     is the primary source for this timeline. -->

| Time (UTC)       | Event                                            |
|------------------|--------------------------------------------------|
| <HH:MM>          | <First detection — alert, user report, or monitoring trigger> |
| <HH:MM>          | <Incident owner assigned, investigation begins>  |
| <HH:MM>          | <Key finding or diagnosis step>                  |
| <HH:MM>          | <Containment action taken>                       |
| <HH:MM>          | <Fix deployed or mitigation applied>             |
| <HH:MM>          | <Service restored, normal operations confirmed>  |
| <HH:MM>          | <Post-incident monitoring period started>        |

## Root Cause

<!-- Describe the technical root cause of the incident.
     Focus on SYSTEMS and PROCESSES, not people.

     BAD:  "Developer X forgot to add an index"
     GOOD: "The query on the orders table lacked an index on the created_at
            column, causing full table scans under load. The migration review
            process did not include a performance review step for new queries."

     Use the "5 Whys" technique if helpful:
     1. Why did the service go down? → Database connections exhausted
     2. Why were connections exhausted? → Connection pool was too small for the query pattern
     3. Why was the pool too small? → The pool size was set for the old query pattern
     4. Why wasn't it updated? → No monitoring on connection pool usage
     5. Why wasn't there monitoring? → Pool metrics were not included in the observability setup

     → Root cause: Missing connection pool monitoring and no review process for
       query pattern changes that affect pool usage. -->

<Describe the technical root cause. Focus on systems and processes, not individuals.>

## Contributing Factors

<!-- What conditions allowed this incident to happen or made its impact worse?
     These are not the root cause, but they contributed to the severity or
     delayed detection/resolution.

     Examples:
     - Missing alerts for database connection pool saturation
     - No staging environment to catch the issue before production
     - Runbook for this scenario was outdated
     - On-call engineer was unfamiliar with this subsystem -->

- <Contributing factor 1>
- <Contributing factor 2>
- <Contributing factor 3>

## Resolution

<!-- Describe what was done to fix the immediate issue.
     Include the specific actions taken and their effect.

     Example:
     "Increased the database connection pool from 10 to 25 connections
     and deployed the fix at 15:42 UTC. Error rate dropped to zero within
     2 minutes. Added a temporary rate limit on the /api/reports endpoint
     to prevent recurrence while the underlying query is optimized." -->

<Describe what was done to resolve the incident.>

## Action Items

<!-- Every action item MUST have an owner, priority, and deadline.
     Create tracked issues (GitHub Issues) for each action item after
     completing this report.

     Priority levels:
     - Critical: Must be completed before the next deploy
     - High: Must be completed within 1 week
     - Medium: Must be completed within 2 weeks
     - Low: Must be completed within 1 month

     → See [11-project-management.md, §7.4] for the prevention timeline -->

| Action                                  | Owner    | Priority | Deadline   | Issue |
|-----------------------------------------|----------|----------|------------|-------|
| <Immediate fix or hardening action>     | <Name>   | Critical | <Date>     | #     |
| <Monitoring or alerting improvement>    | <Name>   | High     | <Date>     | #     |
| <Process or documentation update>       | <Name>   | Medium   | <Date>     | #     |
| <Test to prevent regression>            | <Name>   | High     | <Date>     | #     |
| <Engineering standards update if gap found> | <Name> | Medium | <Date>     | #     |

## Lessons Learned

<!-- Reflect on the incident with the goal of learning and improving.
     Structure as: what went well, what could improve, and what was lucky.

     Be specific and actionable — "communication was bad" is not useful.
     "The incident was communicated via Slack but the on-call engineer
     had notifications muted — we need a backup notification channel"
     is actionable. -->

### What Went Well

<!-- What aspects of detection, response, or recovery worked as intended? -->

- <What worked well 1>
- <What worked well 2>

### What Could Improve

<!-- What aspects of detection, response, or recovery need improvement? -->

- <What could improve 1>
- <What could improve 2>

### Detection Gap

<!-- Why was this not caught earlier? Could we have detected this in
     development, CI, staging, or through monitoring before users were affected?
     → See [11-project-management.md, §7.4] for the detection gap analysis -->

<Explain why existing quality gates, tests, or monitoring did not catch this issue.>

---

## Post-Incident Review Checklist

<!-- This checklist tracks the post-incident process completion.
     → See [11-project-management.md, §7.4] for the full checklist -->

### Immediate (within 24 hours of resolution)

- [ ] Incident timeline documented (detection → diagnosis → mitigation → resolution)
- [ ] Root cause identified (or marked as "under investigation")
- [ ] Impact assessed (users affected, duration, data impact)
- [ ] Temporary mitigations documented

### Review (within 1 week of resolution)

- [ ] Incident report completed using this template
- [ ] Blameless post-mortem conducted (focus on systems, not individuals)
- [ ] Action items created as tracked issues with owners and deadlines
- [ ] Detection gap identified: why was this not caught earlier?

### Prevention (within 2 weeks of resolution)

- [ ] Action items in progress or completed
- [ ] Monitoring and alerting improved to detect similar incidents earlier
- [ ] Tests added to prevent regression
- [ ] Engineering standards updated if the incident exposed a gap (→ See [00-INDEX.md, §Contributing & Evolution])

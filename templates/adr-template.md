# ADR Template — Architecture Decision Record

<!--
PURPOSE:
  A copy-and-fill template for documenting architecture decisions.
  An ADR captures a single significant decision, its context,
  the alternatives considered, and the consequences accepted.
  ADRs are the institutional memory of a project — they answer
  "Why was it done this way?"

WHEN TO USE:
  - Introducing a major new dependency (database, auth, framework, UI kit)
  - Choosing or changing project architecture or layering rules
  - Deviating from a MUST or SHOULD rule in any engineering standards document
  - Making a security trade-off or accepting a known risk
  - Choosing infrastructure or deployment strategy
  - Adding significant complexity (queues, caching, background workers)
  - Making any decision that is hard to reverse
  → See [01-core-principles.md, §9.2] for the full list of triggers

WHERE TO SAVE:
  docs/adr/NNN-title-in-kebab-case.md
  Example: docs/adr/001-use-supabase-for-database-and-auth.md

NAMING RULES:
  - Sequential numbering with zero-padding: 001, 002, 003...
  - kebab-case for the title portion
  - Never reuse numbers — if a decision is reversed, mark the
    original as Superseded and create a new ADR with the next number

INDEX FILE:
  Maintain docs/adr/README.md listing all ADRs with status and date
  → See [01-core-principles.md, §9.5] for the index format

QUALITY RULES:
  - MUST be concise: 1–2 pages maximum. If longer, break into smaller decisions
  - MUST include at least 2 alternatives (if only one option exists, it is a
    constraint, not a decision — document it differently)
  - MUST be honest about trade-offs — an ADR with only positives is incomplete
  - MUST be specific — "we chose X because it is better" is not useful; explain
    better at what, for whom, and compared to what
  - SHOULD be written close in time to the decision — do not rely on memory
  - SHOULD be reviewed by at least one other team member
  → See [01-core-principles.md, §9.4] for the full quality rules

REFERENCES:
  → See [01-core-principles.md, §9] — Complete ADR guide (structure, triggers, quality, organization)
  → See [02-technology-radar.md, §1.4] — Technology evaluation framework and ADR requirements by impact
  → See [00-INDEX.md] — Cross-reference map for all engineering standards

AI AGENT INSTRUCTIONS:
  When using this template to create a new ADR:
  1. Copy this file to docs/adr/NNN-title.md with the next sequential number
  2. Replace all placeholder text (marked with < > angle brackets) with actual content
  3. Remove all HTML comments (<!-- -->) from the final document
  4. Ensure the ADR is self-contained — a reader should understand the decision
     without needing to read other documents (but cross-references are welcome)
  5. Use RFC keywords (MUST/SHOULD/MAY) only when defining rules that the team
     must follow as a consequence of the decision
  6. Update docs/adr/README.md with the new ADR entry
  7. Write in English — all technical documentation uses English
-->

---

# ADR <NNN>: <Title — Short, Descriptive Title That Identifies the Decision>

<!-- TITLE GUIDANCE:
  Good: "Use Supabase for database and authentication"
  Good: "Adopt feature-based module structure"
  Bad:  "Database decision" (too vague)
  Bad:  "We should probably use Supabase maybe" (not decisive)
-->

## Status

<!-- Choose exactly ONE status. Delete the others. -->

**Proposed** | **Accepted** | **Superseded** by [ADR <NNN>](./NNN-title.md) | **Deprecated**

<!-- STATUS LIFECYCLE:
  Proposed  → Under discussion, not yet agreed upon
  Accepted  → Agreed and in effect — the team follows this decision
  Superseded → Replaced by a newer decision (MUST link to the new ADR)
  Deprecated → No longer relevant (the feature/context was removed)

  RULES:
  - MUST never delete an ADR — mark it as Superseded or Deprecated instead
  - MUST include a reference to the superseding ADR when marking as Superseded
-->

## Date

<YYYY-MM-DD>

<!-- The date when this ADR was created or last changed status -->

## Context

<!-- CONTEXT GUIDANCE:
  Describe the situation that led to this decision. Include:
  - What problem are we solving?
  - What constraints exist? (technical, business, team, timeline)
  - What forces are at play? (requirements, risks, dependencies)
  - What is the current state? (existing system, pain points)

  Write as if explaining to a developer who joins in 6 months.
  Be factual — this is not the place for opinions or advocacy.
  Keep it to 1–3 paragraphs.
-->

<Describe the problem, constraints, and forces that led to this decision.>

## Decision

<!-- DECISION GUIDANCE:
  State the decision clearly and unambiguously. Use active voice:
  "We will use X" not "X was considered".

  Be specific:
  BAD:  "We will use Supabase because it is the best option."
  GOOD: "We will use Supabase as our database and authentication provider.
         It provides PostgreSQL with built-in Row Level Security, real-time
         subscriptions, and a managed auth system — which covers our current
         requirements without maintaining separate infrastructure for each
         concern. The trade-off is vendor lock-in to Supabase's API surface
         and pricing model."

  If the decision introduces rules the team must follow, state them here
  using RFC keywords (MUST/SHOULD/MAY).
-->

<State what was decided — clearly and unambiguously.>

## Alternatives Considered

<!-- ALTERNATIVES GUIDANCE:
  MUST include at least 2 alternatives. For each:
  - Brief description of the alternative
  - Pros (what it does well)
  - Cons (what it does poorly or the risks)
  - Why it was rejected (the decisive factor)

  If "do nothing" or "keep current approach" is a realistic option,
  include it as an alternative. This makes the case for change explicit.
-->

### Alternative 1: <Name>

- **Description:** <What this alternative entails>
- **Pros:** <What it does well>
- **Cons:** <What it does poorly, risks, limitations>
- **Why rejected:** <The decisive factor — what made this unacceptable or inferior>

### Alternative 2: <Name>

- **Description:** <What this alternative entails>
- **Pros:** <What it does well>
- **Cons:** <What it does poorly, risks, limitations>
- **Why rejected:** <The decisive factor — what made this unacceptable or inferior>

<!-- Add more alternatives if relevant. Each alternative strengthens
     the decision by showing what was considered and why it was not chosen. -->

## Consequences

<!-- CONSEQUENCES GUIDANCE:
  Every decision has trade-offs. An ADR that lists only positives is
  incomplete and not trustworthy. Be honest about what we gain,
  what we lose, and what we need to do as a result.
-->

### Positive

<!-- What benefits does this decision bring? -->

- <Expected benefit 1>
- <Expected benefit 2>

### Negative

<!-- What trade-offs, risks, or downsides are we accepting? -->

- <Accepted trade-off or risk 1>
- <Accepted trade-off or risk 2>

### Action Items

<!-- Concrete steps needed to implement this decision. Optional but recommended.
     If the decision requires code changes, migration steps, or configuration,
     list them here with owners if known. -->

- [ ] <Action item 1>
- [ ] <Action item 2>

---

<!-- OPTIONAL SECTIONS — include only if they add value:

## Review Trigger

Define when this decision should be revisited:
- "Revisit if the framework drops below 1 release per quarter"
- "Revisit when the team grows beyond 5 developers"
- "Revisit if monthly costs exceed €X"

## Related ADRs

- [ADR 001 — Title](./001-title.md) — relationship description
- [ADR 003 — Title](./003-title.md) — relationship description

## References

- Link to relevant documentation, RFCs, or external resources
- Link to the engineering standards section that informed this decision
-->

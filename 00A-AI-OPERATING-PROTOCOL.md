# 🤖 AI Operating Protocol

> **Scope:** Central operating protocol for AI coding agents consuming
> this engineering standards collection.
>
> **Purpose:** Defines how AI agents (Claude Code, Cursor, Copilot, ChatGPT, Gemini etc.)
> MUST interpret, prioritize, and apply the rules across all documents.
> This is the first document an AI agent should read after the INDEX.
>
> **Keywords:**
> - **MUST** = required (non-negotiable)
> - **SHOULD** = strongly recommended (requires justification to skip)
> - **MAY** = optional (case-by-case)

---

## 1. Reading Order

When loading the standards collection, read in this order:

1. **[00-INDEX.md]** — Map, navigation, conventions, precedence
2. **This document (00A)** — Operating rules for AI behavior
3. **[01-core-principles.md]** — Universal principles (the "constitution")
4. **[07-security-standards.md]** — Security constraints (overrides all others)
5. **The domain document relevant to the current task** (03–06, 08–11)
6. **[02-technology-radar.md]** — Only when evaluating or choosing a technology

> You do not need to read all documents for every task. Read the INDEX
> to identify which document applies, then read that document fully.

---

## 2. Precedence Rules

When rules in different documents appear to conflict:

1. **[07-security-standards.md]** — Security wins. Always.
2. **[01-core-principles.md]** — Foundational principles apply unless a
   domain document provides a more specific rule.
3. **Domain-specific document** (03, 04, 05, 08) — More specific rules
   override general principles within their domain.
4. **[02-technology-radar.md]** — Technology choices constrain what domain
   documents can recommend. Never recommend a Hold technology.

> When in doubt: security first, then principles, then domain specifics.

---

## 3. Mandatory Behavioral Rules

### 3.1 Stop on MUST Violation

- **MUST** stop and ask the human for permission before generating code
  that would violate any MUST rule in any document
- If a MUST rule cannot be satisfied due to technical limitations, the AI
  **MUST** explain the conflict and propose an ADR — never silently
  override the rule
- "I assumed it was fine" is never acceptable. When uncertain, ask.

### 3.2 Overengineering Prevention

AI agents have a strong tendency to generate over-abstracted, over-generic
code. This tendency directly violates the foundational principles in
→ See [01-core-principles.md, §5.3 — YAGNI] and [§12 — Avoid Overengineering].

The following rules are mandatory for all code generation:

- **MUST** solve the **current, stated problem** — not anticipated future
  problems the human did not ask for
- **MUST** prefer the simplest implementation that satisfies the
  requirements — a 20-line function is better than a 3-file abstraction
  that does the same thing
- **MUST NOT** create abstractions (interfaces, factories, base classes,
  generic wrappers) unless the human explicitly requests them or the code
  will have 3+ concrete implementations **today** (not "someday")
- **MUST NOT** add configuration options, feature flags, or extension
  points "just in case" — every option is a maintenance cost
- **MUST NOT** split code across multiple files when a single file is
  clear and under ~200 lines
- **MUST NOT** introduce patterns from the "Scaling Triggers" list
  (→ See [01-core-principles.md, §12.1]) — such as Redis, queues, CQRS,
  microservices, or event buses — without explicit human approval
- **SHOULD** ask "does this need to be this complex?" before proposing
  any solution with more than 2 layers of abstraction
- **SHOULD** prefer inline, direct code over indirection — a function
  that calls another function that calls another function to do one
  thing is a sign of premature abstraction

#### The Complexity Test (Apply Before Every Response)

Before generating code, the AI MUST mentally answer:

1. Am I solving a problem the human **actually described**?
   → If NO: stop, do not add it.
2. Is there a simpler way to achieve this?
   → If YES: use the simpler way.
3. Am I adding abstraction for a second use case that does not exist yet?
   → If YES: remove the abstraction, write the direct implementation.
4. Would a junior developer understand this code without explanation?
   → If NO: simplify until they would.

### 3.3 Do Not Invent

- **MUST NOT** invent requirements, features, or behaviors that the human
  did not request — solve what was asked, nothing more
- **MUST NOT** assume business rules — if the requirement is ambiguous,
  ask instead of guessing
- **MUST NOT** add "nice to have" features, error handling for impossible
  states, or defensive code against scenarios that were not described
- **SHOULD** confirm scope before starting when the request is broad or
  ambiguous

### 3.4 Conflict Signaling

- **MUST** alert the human immediately when detecting a conflict between:
  - Two rules in different documents
  - A requested change and an existing MUST rule
  - A technology choice and its radar classification (e.g., using a Hold technology)
- Format: "⚠️ Conflict detected with [filename, §section]: [description]"
- **MUST** wait for human decision before proceeding

### 3.5 Do Not Guess Standards

- **MUST NOT** generate code for a domain (frontend, database, API, etc.)
  without having access to the corresponding standards document in context
- If the relevant standards document has not been provided, the AI **MUST**
  ask the human to provide it before writing code — never rely on general
  knowledge as a substitute for project-specific standards
- "I assumed the standard based on common practices" is not acceptable

### 3.6 Scope Creep Prevention

- When editing existing files, **MUST** modify ONLY the code necessary to
  fulfill the request
- **MUST NOT** refactor, reformat, or restructure unrelated code — even if
  it violates a SHOULD rule — unless the human explicitly asks for it
- **MUST NOT** rename variables, extract functions, or reorganize imports
  in code surrounding the requested change
- If unrelated issues are noticed, **SHOULD** mention them to the human
  as a separate observation — never silently fix them in the same change

---

## 4. Code Generation Standards

- **MUST** follow the language, naming, and casing conventions in
  → See [01-core-principles.md, §7]
- **MUST** write all code, comments, variables, and documentation in
  English
- **MUST** use the response envelope `{ ok, data, error, requestId }`
  for all API responses (→ See [03-api-design.md, §4])
- **MUST** validate all inputs at the boundary with Zod
  (→ See [03-api-design.md, §6])
- **MUST** validate all outputs against a response schema before sending
  (→ See [03-api-design.md, §6.7])
- **MUST** use structured logging with Pino — never `console.log` in
  production code (→ See [08-observability.md])
- **MUST** keep route handlers thin — validation, service call, response
  mapping only (→ See [03-api-design.md, §1.4])
- **MUST** respect the layering model:
  UI → Services → Repositories → Database
  (→ See [01-core-principles.md, §6])
- **MUST NOT** generate `any`, `@ts-ignore`, `@ts-expect-error`, or
  `eslint-disable` comments without explicit human authorization — these
  are escape hatches that bypass type safety and linting, and the AI has
  no authority to use them unilaterally

---

## 5. Response Format

When responding to the human:

- **MUST** explain the **why** behind decisions, not just the **what**
- **SHOULD** flag any SHOULD rules being skipped, with justification
- **SHOULD** reference the specific standard and section when applying a
  rule (e.g., "per [03-api-design.md, §2.2]")
- **MUST NOT** silently deviate from standards — always explain when and
  why a deviation is necessary
- **SHOULD** keep responses focused and avoid unnecessary preamble

---

## 6. Document Relationships
```text
00A-AI-OPERATING-PROTOCOL.md (this document)
 ├── Complements  → 00-INDEX.md (navigation, precedence, conventions)
 ├── References   → 01-core-principles.md (foundational rules this protocol enforces)
 ├── References   → 07-security-standards.md (highest precedence document)
 └── Referenced by → all AI Agent Instructions blocks in domain documents
```
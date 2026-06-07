# 🏗️ Core Principles & Engineering Philosophy

> **Scope:** Universal engineering principles applicable to any modern software project, regardless of technology stack.
>
> **Purpose:** The foundational "constitution" of these engineering standards. Every other document in this collection derives its rules from the principles defined here. If a developer reads only one document, it should be this one.
>
> **Keywords:**
> - **MUST** = required (PR should be blocked if violated)
> - **SHOULD** = strongly recommended (requires justification to skip)
> - **MAY** = optional (case-by-case)

---

## 0. How to Use This Document

- This document defines **universal principles** — they apply to every project, every language, every framework.
- Technology-specific guidance lives in dedicated documents (see [00-INDEX.md](./00-INDEX.md) for the full map).
- Treat these principles as the **default baseline**. Deviating from a MUST or SHOULD requires an **Architecture Decision Record (ADR)** — see [Section 9](#9-architecture-decision-records-adr).
- When in doubt about a decision not covered by a specific document, return to this one — the answer is usually here.
- Cross-references to other documents use the format `→ See [XX-document-name.md]`.

### Document Relationships

```text
01-core-principles.md (this document)
 ├── Informs ALL other documents
 ├── Referenced by → 03-api-design.md (error handling philosophy, layering)
 ├── Referenced by → 04-database-standards.md (naming, fail-fast)
 ├── Referenced by → 05-frontend-standards.md (separation of concerns, clean code)
 ├── Referenced by → 06-testing-strategy.md (definition of done, quality mindset)
 ├── Referenced by → 07-security-standards.md (defense in depth, fail secure)
 ├── References → 11-project-management.md (refactoring planning, migration strategies)
 └── Referenced by → all other standards documents
```

### Boundary Definitions

| Question | This Document (01) | Other Document |
|----------|--------------------|----------------|
| **Which** technology to use? | — | → See [02-technology-radar.md] |
| **Why** certain principles matter (philosophy, SOLID, DRY, KISS)? | ✅ Sections 1–5 | — |
| **How** to name things universally (casing, files, functions)? | ✅ Section 7 | Domain docs add domain-specific naming |
| **How** to design an API endpoint? | — | → See [03-api-design.md] |
| **How** to structure database schemas? | — | → See [04-database-standards.md] |
| **How** to build frontend components? | — | → See [05-frontend-standards.md] |
| **What** to test and what coverage targets? | — | → See [06-testing-strategy.md] |
| **How** to secure the application? | — | → See [07-security-standards.md] (takes precedence on security) |
| **How** to plan and manage large refactoring efforts? | Techniques (§13) | → See [11-project-management.md] (planning, stakeholder, migration strategies) |
| **When** to write an ADR? | ✅ Section 9 (triggers, structure, quality) | → templates/adr-template.md (copy-paste template) |

### Technology Versions

This document is stack-agnostic in its principles. Code examples use the
following technologies for illustration — the principles apply regardless
of the specific tool:

| Technology | Version | Used In |
|---|---|---|
| TypeScript | 5.x+ | All code examples |
| Zod | 4.x | Validation examples (§2.3, §3.4) |
| Node.js | 24 LTS | Runtime context for examples |

> For the full technology stack and choices, see
> → See [02-technology-radar.md].

### AI Agent Instructions

This document is designed to be consumed by AI coding agents (e.g., Claude
Code). When interpreting this document:

- **MUST**, **SHOULD**, and **MAY** are RFC 2119 keywords — treat MUST as non-negotiable constraints, SHOULD as strong defaults that require explicit justification to override, and MAY as contextual options.
- Cross-references (→ See [XX-document.md]) point to authoritative definitions — always defer to the referenced document for the full rule.
- When this document conflicts with [07-security-standards.md], the security document takes precedence.
- BAD/GOOD code examples are pattern-matching references — apply the principle behind the example, not just the literal code.
- Anti-pattern tables describe common mistakes — use them as negative examples when reviewing or generating code.
- This is the foundational document. When no domain-specific document covers a situation, the rules here apply by default.
- If generating code requires violating a MUST rule, the AI **MUST stop** and ask the human for permission before proceeding — never silently override a standard.
- **MUST NOT** over-engineer — always prefer the simplest solution that meets the stated requirements. Do not add abstractions, patterns, or infrastructure beyond what was explicitly requested (→ See [01-core-principles.md, §12]).

### Glossary of Terms

These terms are used consistently across all documents in this collection.
When a document says "Service," it means exactly what is defined here — not
a generic interpretation.

| Term | Definition | Lives In |
|------|------------|----------|
| **Route Handler / Controller** | The HTTP entry point — receives a request, validates input (Zod), calls a service, maps the result to an HTTP response. Contains zero business logic. | `app/api/` (Next.js) or Express route files |
| **Service** | A function that contains **business logic** and orchestrates operations. Framework-agnostic — no HTTP objects, no React, no database queries. Calls repositories for data access. | `src/services/` or `src/features/*/services/` |
| **Repository** | A function or class that handles **data access** — database queries, external API calls, storage operations. Returns domain objects, not framework-specific types. Maps between `snake_case` (DB) and `camelCase` (app). | `src/repositories/` or `src/features/*/repositories/` |
| **Schema** | A Zod schema that defines the **shape and validation rules** for data. Used at boundaries (input validation, output validation, env vars). Types are inferred from schemas via `z.infer<>`. | `src/schemas/` or `src/features/*/schemas/` |
| **Helper / Utility** | A **pure function** that performs a small, reusable operation — formatting, parsing, calculation. Has no side effects, no dependencies on services or repositories. | `src/lib/` or `src/utils/` |
| **Feature Module** | A self-contained folder grouping all code for a domain concept — components, services, repositories, schemas, hooks. Exposes a public API via `index.ts`. | `src/features/<name>/` |
| **DTO (Data Transfer Object)** | The validated, typed data structure passed between layers. In this stack, Zod schemas serve as DTOs — input schemas for requests, response schemas for outputs. | Defined in schema files, used at layer boundaries |
| **ADR (Architecture Decision Record)** | A short document capturing a significant technical decision, alternatives considered, and trade-offs accepted. Required for deviations from MUST/SHOULD rules. | `docs/adr/` |
| **Domain** | A business concept area (e.g., "users," "invoices," "vehicles"). Feature modules are organized around domains. | Conceptual — reflected in folder and module names |
| **Boundary** | The point where data crosses from one trust zone to another — client → API, API → database, app → external service. Validation MUST happen at every boundary. | Conceptual — enforced at route handlers, repositories |
| **Agent Harness** | The deterministic shell around an LLM agent — loop control, tool-call validation, authorization, budgets, memory/state, and audit. Capability lives in the model; control lives in the harness. | `12-ai-engineering.md §6.1` |
| **Lethal Trifecta** | The combination that makes an AI agent dangerous: untrusted input + access to private data + an exfiltration path. Any one alone is safe; all three together enable prompt-injection exfiltration. | `12-ai-engineering.md §6.7` |
| **Action-Safety** | The gate every agent-initiated side-effecting action MUST pass: validate → authorize → human-confirm where irreversible → idempotent execute → audit. The model requests; deterministic code decides and acts. | `12-ai-engineering.md §6.8` |
| **AI Complexity Ladder** | The escalation order for AI features — prompt → RAG → workflow → agent — climbed only on measured need, never by default. The AI-specific form of simplicity-first. | `12-ai-engineering.md §1.6` |
| **Inference Location** | Where a model runs — managed API by default; self-hosted only on a measured driver (RGPD, cost-at-scale, offline latency, control). An axis orthogonal to the complexity ladder. | `12-ai-engineering.md §7.1` |
| **Agent Harness** | The non-model scaffolding that turns an LLM into a reliable agent — the execution loop, tool calling, context management, memory/state, control flow (retries, timeouts, step/budget limits), guardrails, and observability/evals. The model is the engine; the harness is everything around it that makes it production-grade. ("Harness engineering" = the discipline of designing this layer.) | Conceptual — defined in `12-ai-engineering.md`; built with agent frameworks (`02-technology-radar.md §3.26`) |

---

## 1. Philosophy & Mindset

Before any technical rule, there is a mindset. These are the beliefs that shape every decision in these standards.

### 1.1 Software Is Built for People

Code is read far more often than it is written. The primary audience of code is other developers — including your future self six months from now. Every naming choice, every abstraction, every comment is an act of communication. Optimize for the reader, not the writer.

### 1.2 Simplicity Is a Feature

The best code is the code that does not exist. The second best is code so simple that its correctness is obvious. Complexity is not a sign of sophistication — it is a cost that must be justified. Start with the simplest solution that works, and add complexity only when there is a measured, demonstrated need.

### 1.3 Correctness Over Speed

Shipping fast matters, but shipping broken matters more — in the wrong direction. A bug in production costs orders of magnitude more than preventing it during development. Invest in validation, type safety, and testing upfront. Slow is smooth, smooth is fast.

### 1.4 Ownership & Craftsmanship

Every line of code has an author. Take pride in your work. Leave the codebase better than you found it (the Boy Scout Rule). Do not tolerate "temporary" hacks that never get cleaned up — if it ships, it is production code, and it deserves production quality.

### 1.5 Pragmatism Over Dogma

Principles are guides, not gods. Rules exist to serve the project, not the other way around. When a principle conflicts with delivering real value, document the trade-off (ADR) and make a conscious decision. Blind adherence to patterns is as dangerous as ignoring them entirely.

### 1.6 Feedback Loops Matter

The faster you learn that something is wrong, the cheaper it is to fix. This applies at every level: type errors caught by the compiler, validation errors caught at the API boundary, bugs caught by tests, design flaws caught by code review, and user problems caught by monitoring. Build tight feedback loops everywhere.

---

## 2. Core Principles (The Non-Negotiables)

These are the foundational engineering principles that govern every technical decision across all projects. They are stack-agnostic, domain-agnostic, and non-negotiable — deviating from any MUST requires an ADR with explicit justification.

### 2.1 Type Safety First

- **MUST** use the strictest type-checking mode available in the language/toolchain (e.g., `strict: true` in TypeScript, type hints + mypy in Python)
- **MUST** treat type-safety violations as bugs, not warnings
- **MUST NOT** use escape hatches (`any`, `type: ignore`, unsafe casts) without:
  - A comment explaining **why** it is necessary
  - A plan to remove it (if temporary)
- **SHOULD** prefer runtime validation (schema-based parsing) when handling data from untrusted boundaries (user input, external APIs, environment variables, database results from dynamic queries)
- **SHOULD** prefer `unknown` over `any` — force explicit validation before use

> **Why:** Types are the cheapest form of documentation and the fastest feedback loop. A type error caught at compile time costs seconds; the same error in production costs hours, reputation, and money.

### 2.2 Explicit Over Implicit

- **MUST** make behavior visible and predictable — no hidden side effects, no magic values, no implicit type coercions
- **MUST** declare function signatures that communicate intent: parameter names, return types, and thrown errors should tell the full story
- **SHOULD** prefer named constants over magic numbers and magic strings:

  ```
  // BAD — implicit, meaningless
  if (retries > 3) { ... }
  if (status === "a") { ... }

  // GOOD — explicit, self-documenting
  const MAX_RETRIES = 3;
  if (retries > MAX_RETRIES) { ... }

  if (status === OrderStatus.ACTIVE) { ... }
  ```

- **SHOULD** prefer explicit configuration over convention-based defaults — when convention is used, it **MUST** be documented

> **Why:** Implicit behavior creates knowledge silos. If understanding the code requires "you just have to know," the system is fragile and hostile to new contributors.

### 2.3 Fail Fast, Fail Loud

- **MUST** detect and report errors as close to their origin as possible — never allow invalid data to propagate silently through the system
- **MUST** validate inputs at the system boundary (API entry point, form submission, external data ingestion) before any processing occurs
- **MUST** use meaningful error messages that identify **what** failed, **where** it failed, and **why** it failed (for developers — never expose internals to end users)
- **MUST NOT** silently swallow errors:

  ```
  // BAD — silent failure, debugging nightmare
  try {
    await processPayment(order);
  } catch (e) {
    // do nothing
  }

  // BAD — logs but continues as if nothing happened
  try {
    await processPayment(order);
  } catch (e) {
    console.log(e);
  }

  // GOOD — explicit handling with appropriate action
  try {
    await processPayment(order);
  } catch (error) {
    logger.error("Payment processing failed", { orderId: order.id, error });
    throw new PaymentError("Payment could not be processed", { cause: error });
  }
  ```

- **SHOULD** prefer `parse` (throw on failure) over `tryParse`/`safeParse` for internal invariants where failure means a programming error
- **SHOULD** use `safeParse` (return result) for external input where failure is expected and recoverable

> **Why:** Silent failures are the most expensive kind. They hide problems until they compound into critical incidents. Loud failures surface issues early, when they are cheapest to fix. → See [07-security-standards.md, Section 1 — Fail Secure] for the security perspective on this principle.

### 2.4 Security by Default

- **MUST** treat security as a foundational constraint, not a feature to be added later
- **MUST** validate ALL input from untrusted sources — client data, external APIs, webhooks, environment variables, file uploads
- **MUST** apply the principle of least privilege at every level — users, services, database roles, API keys
- **MUST** never expose system internals in error responses, logs, or client-facing output (stack traces, SQL errors, internal paths, secret values)
- **MUST** store secrets in environment variables or dedicated secret managers — never in code, config files, or version control
- **SHOULD** implement defense in depth — multiple independent security layers so that no single failure compromises the system

> **Why:** Security breaches are existential risks. A data leak or unauthorized access can end a business, destroy trust, and incur legal liability. Security is not optional, it is the foundation. → See [07-security-standards.md] for the complete security framework.

### 2.5 Separation of Concerns

- **MUST** keep distinct responsibilities in distinct modules — presentation logic, business logic, and data access **MUST NOT** be mixed in the same unit of code
- **MUST** ensure that each function, class, or module has a clear, single responsibility
- **MUST** define clear boundaries between layers, with explicit interfaces (not implicit shared state)
- **SHOULD** design modules so they can be understood, tested, and modified independently

> **Why:** Mixed concerns create code that is hard to test, hard to change, and hard to reason about. When everything depends on everything, a small change can break the entire system. → See [Section 6](#6-separation-of-concerns-layering--modular-design) for the full layering and modular design guide.

### 2.6 Readable Code Over Clever Code

- **MUST** prioritize clarity and readability in all code — the goal is code that any competent developer can understand without needing the original author's explanation
- **MUST** prefer straightforward solutions over "elegant" one-liners that sacrifice readability:

  ```
  // BAD — clever, but requires mental gymnastics to parse
  const r = d.reduce((a, c) => (c.s === "a" ? [...a, c.id] : a), []);

  // GOOD — boring, but immediately understandable
  const activeIds = [];
  for (const document of documents) {
    if (document.status === "active") {
      activeIds.push(document.id);
    }
  }

  // ALSO GOOD — clear functional style with descriptive names
  const activeIds = documents
    .filter((doc) => doc.status === "active")
    .map((doc) => doc.id);
  ```

- **SHOULD** write code that reads like well-structured prose — good naming eliminates most need for comments
- **SHOULD** keep functions short and focused — if a function requires scrolling to read, it likely does too much

> **Why:** Code is read 10x more often than it is written. Clever code impresses the author for a moment; readable code serves the team for years. Debugging clever code is twice as hard as writing it — so if you write it as cleverly as possible, you are by definition not smart enough to debug it.

### 2.7 Small, Composable Units

- **MUST** design functions, modules, and components as small, focused units that do one thing well
- **SHOULD** prefer composition over inheritance — build complex behavior by combining simple, independent pieces
- **SHOULD** keep functions under ~20–30 lines as a guideline (not a hard rule) — if a function grows beyond this, consider whether it has multiple responsibilities that should be split
- **SHOULD** design units with clear inputs and outputs (pure functions where possible) — minimize reliance on shared mutable state

> **Why:** Small units are easier to name, easier to test, easier to reuse, and easier to replace. Composition scales; monoliths collapse under their own weight.

### 2.8 Measure Before Optimizing

- **MUST NOT** optimize based on assumptions or intuition — premature optimization is the root of much unnecessary complexity
- **MUST** identify and measure the actual bottleneck before investing effort in optimization
- **SHOULD** define performance budgets for user-facing applications (e.g., LCP, TTFB targets) and measure against them
- **SHOULD** use profiling tools and real data to guide optimization decisions

> **Why:** Developers are notoriously bad at guessing where performance bottlenecks are. Optimizing the wrong thing wastes time, adds complexity, and delivers no value. Measure first, optimize second, verify third. → See [Section 12](#12-non-goals--avoid-overengineering) for related guidance on avoiding unnecessary complexity.

---

## 3. Clean Code in Practice

Clean code is not an aesthetic preference — it is an engineering discipline. Clean code reduces bugs, accelerates onboarding, simplifies maintenance, and makes the system safer. This section provides practical, actionable rules for the daily craft of writing code.

### 3.1 Function Design

Functions are the fundamental building blocks of any codebase. Their quality determines the quality of the entire system.

#### Rules

- **MUST** keep functions focused on a single task — if the function name requires "and" to describe what it does, it does too much
- **MUST** keep function signatures honest — the name, parameters, and return type should fully communicate the function's behavior without needing to read the implementation
- **SHOULD** keep functions short (guideline: ~5–20 lines of logic). This is not a hard rule — clarity matters more than line count. A 30-line function that reads well is better than three 10-line functions that obscure the flow
- **SHOULD** limit function parameters to 3 or fewer. When more are needed, group related parameters into a well-named object:

  ```
  // BAD — too many parameters, unclear at the call site
  function createUser(name, email, role, isActive, teamId, sendWelcome) { ... }

  // GOOD — grouped, self-documenting
  function createUser(params: CreateUserParams) { ... }
  ```

- **SHOULD** prefer pure functions where possible — same inputs always produce the same outputs, no side effects. Pure functions are trivial to test and safe to refactor
- **MUST NOT** mix side effects with computations in the same function when avoidable:

  ```
  // BAD — computation + side effect mixed
  function calculateTotalAndSendEmail(order) {
    const total = order.items.reduce((sum, item) => sum + item.price, 0);
    emailService.send(order.customer, `Your total is ${total}`);
    return total;
  }

  // GOOD — separated concerns
  function calculateTotal(items) {
    return items.reduce((sum, item) => sum + item.price, 0);
  }

  function notifyCustomer(customer, total) {
    emailService.send(customer, `Your total is ${total}`);
  }
  ```

### 3.2 Guard Clauses & Early Returns

Deeply nested code is hard to follow and error-prone. Guard clauses flatten the logic and make the "happy path" immediately visible.

#### Rules

- **SHOULD** use guard clauses (early returns) to handle edge cases and error conditions at the top of a function, keeping the main logic at the base indentation level:

  ```
  // BAD — deep nesting, hard to follow
  function processOrder(order) {
    if (order) {
      if (order.items.length > 0) {
        if (order.status === "pending") {
          // ... actual logic buried 3 levels deep
        } else {
          throw new InvalidStatusError("Order is not pending");
        }
      } else {
        throw new ValidationError("Order has no items");
      }
    } else {
      throw new NotFoundError("Order");
    }
  }

  // GOOD — guard clauses, flat and clear
  function processOrder(order) {
    if (!order) throw new NotFoundError("Order");
    if (order.items.length === 0) throw new ValidationError("Order has no items");
    if (order.status !== "pending") throw new InvalidStatusError("Order is not pending");

    // Happy path — clear and unindented
    // ... actual logic here
  }
  ```

- **SHOULD** limit nesting to a maximum of 2–3 levels — if you need more, extract inner logic into a well-named function
- **MUST NOT** use `else` after a guard clause that returns or throws — it is redundant and adds noise

### 3.3 Conditionals & Boolean Logic

Complex conditionals are one of the most common sources of bugs and confusion.

#### Rules

- **MUST** extract complex boolean expressions into well-named variables or functions:

  ```
  // BAD — what does this condition mean?
  if (user.role === "admin" || (user.role === "editor" && user.teamId === resource.teamId && !resource.isLocked)) {
    // ...
  }

  // GOOD — intention is immediately clear
  const isAdmin = user.role === "admin";
  const isTeamEditorWithAccess = user.role === "editor"
    && user.teamId === resource.teamId
    && !resource.isLocked;

  if (isAdmin || isTeamEditorWithAccess) {
    // ...
  }

  // BETTER — encapsulated in a reusable function
  if (canEditResource(user, resource)) {
    // ...
  }
  ```

- **SHOULD** prefer positive conditions over negated ones — the human brain processes positive logic more easily:

  ```
  // LESS CLEAR
  if (!isNotActive) { ... }

  // CLEAR
  if (isActive) { ... }
  ```

- **SHOULD** avoid boolean parameters (flag arguments) that change function behavior — they hide branching logic at the call site:

  ```
  // BAD — what does "true" mean at the call site?
  createUser(data, true);

  // GOOD — explicit
  createUser(data, { sendWelcomeEmail: true });

  // ALSO GOOD — separate functions for different behaviors
  createUser(data);
  createUserAndNotify(data);
  ```

### 3.4 Error Handling Discipline

Error handling is not an afterthought — it is a core part of the design. Poorly handled errors are the root cause of most production incidents.

#### Rules

- **MUST** handle errors explicitly — every operation that can fail must have a deliberate error handling strategy
- **MUST** use custom error classes with stable error codes for programmatic handling — never rely on parsing error message strings:

  ```
  // BAD — fragile, breaks if message changes
  if (error.message.includes("not found")) { ... }

  // GOOD — stable, programmatic
  if (error instanceof NotFoundError) { ... }
  if (error.code === "NOT_FOUND") { ... }
  ```

- **MUST** propagate errors with context — when catching and rethrowing, add information about the current operation:

  ```
  // BAD — original context lost
  try {
    await repository.findUser(userId);
  } catch (error) {
    throw new Error("Something went wrong");
  }

  // GOOD — context preserved, cause chained
  try {
    await repository.findUser(userId);
  } catch (error) {
    throw new AppError(
      "USER_FETCH_FAILED",
      `Failed to fetch user ${userId}`,
      500,
      { cause: error }
    );
  }
  ```

- **MUST** distinguish between recoverable errors (expected — e.g., "user not found") and unrecoverable errors (unexpected — e.g., database connection lost). Handle them differently
- **MUST NOT** use exceptions for control flow — exceptions are for exceptional situations, not for expected business outcomes
- **SHOULD** centralize error-to-response mapping at the application boundary (API handler, global error handler) — not scattered across every function

> → See [03-api-design.md] for API-specific error handling patterns and response envelopes.
> → See [07-security-standards.md, Section 1 — Fail Secure] for security-oriented error handling.

### 3.5 Comments Philosophy

Comments are a tool for communicating what the code cannot express on its own. They are not a substitute for clear code.

#### Rules

- **MUST** write comments that explain **why**, not **what** — if a comment restates what the code does, the code should be made clearer instead:

  ```
  // BAD — restates the obvious
  // Increment counter by 1
  counter += 1;

  // BAD — explains "what" instead of "why"
  // Loop through users and filter active ones
  const activeUsers = users.filter((u) => u.isActive);

  // GOOD — explains "why" (the non-obvious decision)
  // We filter at the application level instead of the query level because
  // RLS policies already handle access control, and adding a WHERE clause
  // here would conflict with the index on (tenant_id, created_at).
  const activeUsers = users.filter((u) => u.isActive);
  ```

- **MUST** keep comments up to date — a stale comment is worse than no comment, because it actively misleads
- **SHOULD** use comments for:
  - **Intent** — why this approach was chosen over alternatives
  - **Warnings** — "do not change this without also updating X"
  - **Context** — business rules, regulatory requirements, or external constraints that the code alone cannot convey
  - **TODOs** — with a reference (ticket/issue number) and owner, never open-ended
- **MUST NOT** use comments to:
  - Disable code indefinitely — delete dead code, version control remembers it
  - Compensate for poor naming — rename instead
  - Create section dividers in long files — split the file instead

> → See [Section 8](#8-documentation-standards) for documentation standards beyond inline comments (TSDoc, README, etc.).

### 3.6 Code Organization Within Files

How code is organized within a single file affects readability and navigation.

#### Rules

- **SHOULD** follow a consistent top-to-bottom structure within files. A recommended order:
  1. Imports (grouped: external libraries → internal modules → types/schemas)
  2. Constants and configuration
  3. Type definitions (if co-located)
  4. Helper / utility functions (private to this file)
  5. Main exported function(s) / component(s)

- **SHOULD** keep related code close together — a function and its helpers should be near each other, not separated by hundreds of lines
- **MUST** keep files focused — if a file grows beyond ~200–300 lines, evaluate whether it contains multiple responsibilities that should be split
- **MUST NOT** create "god files" — files like `utils.ts`, `helpers.ts`, or `common.ts` that become dumping grounds for unrelated code. Every file should have a cohesive purpose reflected in its name
- **SHOULD** prefer many small, well-named files over few large files — file names serve as a table of contents for the codebase

### 3.7 Avoiding Anti-Patterns

Certain patterns consistently lead to maintenance nightmares. Recognizing and avoiding them is a core skill.

#### Rules

- **MUST NOT** use global mutable state — it creates hidden dependencies, race conditions, and makes testing nearly impossible
- **MUST NOT** hardcode values that may change (URLs, limits, feature flags, credentials) — externalize them to configuration or environment variables
- **MUST NOT** ignore compiler/linter warnings — treat warnings as errors in CI. A warning is the system telling you something is wrong; ignoring it normalizes carelessness
- **SHOULD** avoid stringly-typed patterns — prefer enums, union types, or constants over raw strings for values with a fixed set of options:

  ```
  // BAD — stringly-typed, no autocomplete, easy to typo
  if (order.status === "pendng") { ... }

  // GOOD — type-safe, compiler catches typos
  if (order.status === OrderStatus.PENDING) { ... }
  ```

- **SHOULD** avoid deep inheritance hierarchies — prefer composition. If a class hierarchy exceeds 2–3 levels, the design likely needs rethinking
- **SHOULD** avoid premature generalization — do not build abstractions for problems you do not yet have (→ See [Section 5 — YAGNI](#5-dry-kiss-yagni--with-nuance))
- **SHOULD** address anti-patterns through disciplined refactoring rather than tolerating them — → See [Section 13](#13-refactoring-guidelines) for when and how to refactor

### 3.8 Date & Time Discipline

Incorrect date/time handling is a frequent source of subtle, hard-to-debug
bugs — especially across timezones, locales, and daylight saving transitions.
These rules apply universally, regardless of the library or API used.

#### Rules

- **MUST** store and process all timestamps on the server and database in
  **UTC** — never in a local timezone
- **MUST** convert to the user's locale/timezone only at the **UI boundary**
  (the last step before displaying to the user)
- **MUST** use ISO-8601 format (`2026-03-28T14:30:00Z`) for all date/time
  serialization (API payloads, logs, database storage) — never ambiguous
  formats like `03/28/2026` or `28-03-2026`
- **MUST** use `timestamptz` (timestamp with time zone) in PostgreSQL, never
  `timestamp` (without timezone)
  (→ See [04-database-standards.md] for column type guidance)
- **SHOULD** use a dedicated date library (→ See [02-technology-radar.md,
  §3.19 — Date & Time]) rather than manual string formatting or raw
  Date arithmetic
- **SHOULD** prefer the Temporal API (native) when browser/runtime support
  allows; fall back to date-fns for broader compatibility
- **MUST NOT** use manual string parsing or regex to extract date components
  — use a proper parser (library or Temporal)
- **MUST NOT** assume all days have 24 hours, all hours have 60 minutes, or
  all months have the same number of days — DST transitions and leap
  seconds break these assumptions

> **Why:** A date stored as "March 28, 2026 at 14:30" is meaningless
> without timezone context — it could represent any of 24+ different
> instants. UTC + UI-boundary conversion eliminates an entire class of
> bugs. ISO-8601 eliminates format ambiguity across locales.

---

## 4. SOLID Principles (Practical Guide)

SOLID is not an academic exercise — it is a set of practical design guidelines that prevent code from becoming rigid, fragile, and expensive to change. These principles apply to functions, modules, and components — not just classes in object-oriented programming.

> **Important:** SOLID principles are guidelines for **managing complexity**, not rules to follow blindly. Applying them to trivially simple code adds unnecessary abstraction. Use judgment: the more a piece of code is likely to change, grow, or be reused, the more SOLID matters.

---

### 4.1 Single Responsibility Principle (SRP)

> _"A module should have one, and only one, reason to change."_

A function, class, or module should do one thing, and the decision to change it should come from one source of requirements — not multiple.

#### What SRP Means in Practice

- **MUST** ensure each module (file, function, class, component) has a single, clearly identifiable responsibility
- **MUST** be able to describe what a module does in one sentence without using "and":

  ```
  // BAD — "this function validates the order AND calculates the total AND sends the confirmation email"
  function processOrder(order) {
    // validation logic (30 lines)
    // price calculation logic (20 lines)
    // email sending logic (15 lines)
  }

  // GOOD — each function has one job
  function validateOrder(order) { ... }
  function calculateOrderTotal(items) { ... }
  function sendOrderConfirmation(order, total) { ... }

  // Orchestration happens at a higher level
  function processOrder(order) {
    validateOrder(order);
    const total = calculateOrderTotal(order.items);
    sendOrderConfirmation(order, total);
  }
  ```

- **SHOULD** use the "reason to change" test: if business rules, UI requirements, and data format changes would all require modifying the same module, it has too many responsibilities

#### Common SRP Violations

| Violation | Symptom | Fix |
|-----------|---------|-----|
| API handler contains business logic | Changing a business rule requires editing a route handler | Extract to a service function |
| Component fetches data AND renders UI | Changing the data source requires editing the UI component | Separate data fetching from presentation |
| Utility function that does formatting + validation + logging | Any small change risks breaking the other behaviors | Split into focused, single-purpose functions |
| Service function that queries the database directly | Changing the database requires editing business logic | Extract data access to a repository |

#### When NOT to Over-Apply SRP

- **MUST NOT** split code so aggressively that understanding a single operation requires jumping across 10 files — coherence matters. SRP means "one responsibility," not "one line"
- **SHOULD** keep related logic together when it genuinely belongs to the same concern — splitting a 10-line function into three 4-line functions across three files is usually worse, not better
- A good test: **"If I change one of these pieces, do I always have to change the other?"** If yes, they are the same responsibility and should stay together

---

### 4.2 Open/Closed Principle (OCP)

> _"Software entities should be open for extension, but closed for modification."_

You should be able to add new behavior to a system without rewriting existing, tested code.

#### What OCP Means in Practice

- **SHOULD** design systems so that new features can be added by writing **new code**, not by modifying existing, stable code
- **SHOULD** use extension points (strategy pattern, plugin architecture, configuration-driven behavior) where change is expected:

  ```
  // BAD — adding a new payment method requires modifying this function
  function processPayment(method, amount) {
    if (method === "credit_card") {
      // credit card logic
    } else if (method === "paypal") {
      // paypal logic
    } else if (method === "bank_transfer") {
      // bank transfer logic — yet another modification
    }
    // Every new method = change this function = risk breaking existing methods
  }

  // GOOD — adding a new payment method means registering a new processor
  const paymentProcessors = {
    credit_card: processCreditCard,
    paypal: processPaypal,
    bank_transfer: processBankTransfer,  // ← new code, no existing code changed
  };

  function processPayment(method, amount) {
    const processor = paymentProcessors[method];
    if (!processor) throw new ValidationError(`Unsupported payment method: ${method}`);
    return processor(amount);
  }
  ```

- **SHOULD** identify the **axes of change** — the things most likely to vary — and design abstractions around them

#### When NOT to Over-Apply OCP

- **MUST NOT** build extension points "just in case" — this creates unused abstractions that add complexity for no benefit (→ See [Section 5 — YAGNI](#5-dry-kiss-yagni--with-nuance))
- Simple `if/else` is perfectly fine when the options are known, stable, and few (2–3 cases). OCP matters when the list is expected to grow or when the branching logic is complex
- A good test: **"Has this branching logic already grown twice, or is there a strong reason to expect it will?"** If not, keep it simple

---

### 4.3 Liskov Substitution Principle (LSP)

> _"Subtypes must be substitutable for their base types without altering the correctness of the program."_

Any implementation of an interface or contract must honor the expectations set by that contract — no surprises.

#### What LSP Means in Practice

- **MUST** ensure that any implementation of an interface or abstract contract fulfills the full behavioral expectations of that contract — not just the type signature, but the semantics
- **MUST NOT** create implementations that silently ignore parts of the contract, throw unexpected errors for standard operations, or change the meaning of inherited behavior:

  ```
  // Contract: a Repository provides CRUD operations for an entity
  interface UserRepository {
    findById(id: string): Promise<User | null>;
    save(user: User): Promise<User>;
    delete(id: string): Promise<void>;
  }

  // BAD — violates LSP: "delete" does nothing, breaking the contract silently
  class ReadOnlyUserRepository implements UserRepository {
    async findById(id) { /* works */ }
    async save(user) { throw new Error("Not supported"); }
    async delete(id) { /* silently does nothing — caller thinks it succeeded */ }
  }

  // GOOD — if read-only behavior is needed, define a separate, honest contract
  interface ReadableUserRepository {
    findById(id: string): Promise<User | null>;
  }

  interface WritableUserRepository extends ReadableUserRepository {
    save(user: User): Promise<User>;
    delete(id: string): Promise<void>;
  }
  ```

- **SHOULD** think of LSP as the **"principle of no surprises"** — a consumer of an interface should never need to know which implementation it is using

#### LSP Beyond Classes

LSP applies to any substitutable component, not just class inheritance:

- **Functions that accept callbacks** — the callback must honor the expected signature and behavior
- **Configuration-driven strategies** — each strategy (e.g., payment processors, notification channels) must fulfill the same contract
- **Replaceable modules** — swapping a database adapter, email provider, or storage backend must not change the behavior expected by the consuming code

---

### 4.4 Interface Segregation Principle (ISP)

> _"No client should be forced to depend on interfaces it does not use."_

Keep interfaces small and focused. Do not force consumers to deal with capabilities they do not need.

#### What ISP Means in Practice

- **SHOULD** prefer small, focused interfaces over large, monolithic ones:

  ```
  // BAD — every consumer depends on the entire interface, even if they only need one method
  interface UserService {
    createUser(data): Promise<User>;
    updateUser(id, data): Promise<User>;
    deleteUser(id): Promise<void>;
    getUserById(id): Promise<User>;
    listUsers(filters): Promise<User[]>;
    exportUsersToCSV(): Promise<Buffer>;
    sendWelcomeEmail(user): Promise<void>;
    resetPassword(email): Promise<void>;
    verifyEmail(token): Promise<void>;
  }

  // GOOD — segregated by concern, consumers depend only on what they need
  interface UserReader {
    getUserById(id): Promise<User>;
    listUsers(filters): Promise<User[]>;
  }

  interface UserWriter {
    createUser(data): Promise<User>;
    updateUser(id, data): Promise<User>;
    deleteUser(id): Promise<void>;
  }

  interface UserNotifier {
    sendWelcomeEmail(user): Promise<void>;
    resetPassword(email): Promise<void>;
    verifyEmail(token): Promise<void>;
  }

  interface UserExporter {
    exportUsersToCSV(): Promise<Buffer>;
  }
  ```

- **SHOULD** design function signatures to accept only the data they need — not entire objects when a subset suffices:

  ```
  // BAD — function depends on the entire User object but only uses the email
  function sendNotification(user: User) {
    mailer.send(user.email, "Hello!");
  }

  // GOOD — depends only on what it needs
  function sendNotification(email: string) {
    mailer.send(email, "Hello!");
  }
  ```

- **SHOULD** apply ISP to configuration and props — do not pass entire config objects when a component only needs two fields

#### When NOT to Over-Apply ISP

- Do not create an interface for every single method — group methods that **logically belong together** and are **always used together**. ISP is about preventing forced dependencies, not about achieving maximum granularity

---

### 4.5 Dependency Inversion Principle (DIP)

> _"High-level modules should not depend on low-level modules. Both should depend on abstractions."_

Business logic should not be coupled to specific implementations of infrastructure (database, email, storage, APIs). Depend on contracts, not concrete tools.

#### What DIP Means in Practice

- **SHOULD** define contracts (interfaces/types) for external dependencies and have the business logic depend on the contract, not the implementation:

  ```
  // BAD — service directly depends on Supabase (a specific tool)
  // Changing the database requires rewriting the business logic
  async function createUser(data) {
    const validated = userSchema.parse(data);
    const { data: user } = await supabase
      .from("users")
      .insert(validated)
      .select()
      .single();
    return user;
  }

  // GOOD — service depends on a repository contract
  // The repository implementation can be swapped without touching business logic

  // Contract (abstraction)
  interface UserRepository {
    create(data: CreateUserInput): Promise<User>;
  }

  // Service (high-level — depends on abstraction)
  function createUserService(repo: UserRepository) {
    return async (data) => {
      const validated = userSchema.parse(data);
      return repo.create(validated);
    };
  }

  // Implementation (low-level — fulfills the contract)
  class SupabaseUserRepository implements UserRepository {
    async create(data) {
      const { data: user } = await supabase
        .from("users").insert(data).select().single();
      return user;
    }
  }
  ```

- **SHOULD** apply DIP at the architectural boundary between business logic and side effects:
  - Database access
  - External API calls
  - Email / notification sending
  - File storage
  - Logging (when testability matters)

- **SHOULD** use dependency injection (passing dependencies as parameters or constructor arguments) as the mechanism — not service locators or global singletons

#### When NOT to Over-Apply DIP

- **MUST NOT** abstract everything — DIP adds indirection, which has a readability cost. Apply it where substitutability or testability provides real value:
  - **Worth it:** database repositories, external API clients, payment processors, email services
  - **Usually not worth it:** utility functions, formatters, internal helpers that will never be swapped
- A good test: **"Will I ever need to swap this implementation, or do I need to mock it in tests?"** If the answer to both is no, a direct dependency is simpler and clearer

---

### 4.6 Applying SOLID — Rules of Thumb

- **MUST NOT** apply SOLID dogmatically to trivial code — a 10-line script does not need five interfaces and three layers of abstraction
- **SHOULD** apply SOLID principles proportionally to the complexity and expected lifespan of the code:

  | Code Context | SOLID Rigor |
  |---|---|
  | Throwaway scripts, prototypes | Low — focus on getting it working |
  | Internal tools, admin panels | Medium — focus on SRP and readability |
  | Core business logic, shared libraries | High — full SOLID where applicable |
  | Public APIs, long-lived systems | High — especially OCP, DIP, and LSP |

- **SHOULD** use SOLID as a **diagnostic tool**: when code becomes hard to test, hard to change, or hard to understand, check which SOLID principle is being violated — the answer usually points to the fix
- **MUST** document in an ADR when a significant architectural decision intentionally deviates from SOLID principles (e.g., "We chose to couple the service directly to Supabase because we have no plan to change databases and the indirection adds complexity without benefit")

---

## 5. DRY, KISS, YAGNI — With Nuance

These three principles are among the most widely known — and the most widely misapplied. Each is powerful when used with judgment, and destructive when applied dogmatically. This section defines each principle, shows when it helps, and — critically — shows when over-applying it causes more harm than the problem it was meant to solve.

---

### 5.1 DRY — Don't Repeat Yourself

> _"Every piece of knowledge must have a single, unambiguous, authoritative representation within a system."_

DRY is about eliminating **knowledge duplication** — not about eliminating **code that looks similar**.

#### What DRY Actually Means

DRY targets **knowledge** — business rules, data definitions, decisions. If a business rule is defined in two places, changing it requires finding and updating both, and missing one creates an inconsistency bug.

DRY does **NOT** mean "never write similar-looking code." Two pieces of code can look identical today but represent different concerns that will evolve independently.

#### Rules

- **MUST** have a single source of truth for:
  - Business rules and domain logic
  - Data schemas and validation rules (define once, derive types from them)
  - Configuration values and constants
  - API contracts (shared between client and server when possible)

- **SHOULD** extract shared logic only when the duplication represents the **same knowledge** — i.e., if one instance changes, all others must change in the same way

- **MUST NOT** merge code solely because it looks similar — first ask: **"Do these change for the same reason?"**

  ```
  // SCENARIO: Two functions that look almost identical

  function formatUserDisplayName(user) {
    return `${user.firstName} ${user.lastName}`;
  }

  function formatInvoiceRecipient(recipient) {
    return `${recipient.firstName} ${recipient.lastName}`;
  }

  // TEMPTATION: "These are the same! Let me DRY them up!"
  function formatFullName(entity) {
    return `${entity.firstName} ${entity.lastName}`;
  }

  // PROBLEM: Six months later, invoices need to include company name:
  // "John Doe — Acme Corp"
  // But user display names stay as "John Doe"
  // Now the "DRY" abstraction must handle both cases with conditionals,
  // and it becomes more complex than the original duplication.
  ```

#### The Rule of Three

- **SHOULD** tolerate duplication until a pattern appears at least **2–3 times** before extracting a shared abstraction
- The first time: just write it
- The second time: notice the similarity, but tolerate the duplication
- The third time: now you have enough data to know what the **right** abstraction is — extract it

> **Why the Rule of Three?** Premature abstraction is more expensive than duplication. With only two examples, you do not have enough information to know what varies and what stays the same. The wrong abstraction creates a dependency that is harder to undo than the duplication it replaced.

#### Signs You Over-Applied DRY

- A shared function has accumulated parameters or flags to handle "slightly different" cases
- Changing a shared module for one use case breaks another
- Developers are afraid to modify a shared abstraction because they do not know what depends on it
- The abstraction is more complex than the original duplicated code would have been

#### DRY vs WET Spectrum

| Approach | Description | Use When |
|---|---|---|
| **DRY** | Single source of truth, shared abstraction | The duplicated code represents the same knowledge and changes for the same reason |
| **WET** (Write Everything Twice) | Tolerate controlled duplication | The code looks similar but represents different concerns, or you do not yet know the right abstraction |
| **AHA** (Avoid Hasty Abstractions) | Abstract only with sufficient evidence | You have seen the pattern enough times to confidently identify what varies and what is stable |

- **SHOULD** default to AHA — prefer duplication over the wrong abstraction

---

### 5.2 KISS — Keep It Simple, Stupid

> _"The simplest solution that meets the requirements is usually the best."_

Simplicity is not about writing less code — it is about reducing **unnecessary cognitive load**. Simple code is code where the reader does not need to hold a mental model of multiple layers, indirections, and abstractions to understand what happens.

#### Rules

- **MUST** choose the simplest approach that correctly solves the current problem — not a future, hypothetical problem
- **MUST** justify every layer of abstraction — if you cannot explain why an abstraction exists (beyond "it might be useful someday"), remove it
- **SHOULD** prefer flat, straightforward code over elegant but complex constructions:

  ```
  // OVER-ENGINEERED — generic event bus for a system with two events
  class EventBus {
    private handlers: Map<string, Function[]> = new Map();
    subscribe(event: string, handler: Function) { ... }
    publish(event: string, payload: unknown) { ... }
    unsubscribe(event: string, handler: Function) { ... }
  }

  const bus = new EventBus();
  bus.subscribe("user.created", sendWelcomeEmail);
  bus.subscribe("user.created", createDefaultSettings);

  // SIMPLE — direct function calls for two known operations
  async function onUserCreated(user) {
    await sendWelcomeEmail(user);
    await createDefaultSettings(user);
  }
  ```

- **SHOULD** resist the temptation to generalize before the need is proven — a specific solution today is better than a generic framework for a problem that may never arrive
- **SHOULD** count the number of concepts a reader needs to understand to follow a piece of code — the fewer, the better

#### The Complexity Test

Before adding complexity, ask these questions in order:

1. **Is this complexity required by the current requirements?** If no → do not add it.
2. **Is there a simpler way to achieve the same result?** If yes → use the simpler way.
3. **Can I add this complexity later, when the need is proven, without major refactoring?** If yes → defer it. If no → consider adding it now, but document the decision (ADR).

#### Signs You Violated KISS

- New team members need extensive onboarding to understand a simple feature
- A "utility" or "framework" inside the codebase is more complex than the features it supports
- Debugging a simple issue requires tracing through multiple layers of abstraction
- The architecture diagram for a CRUD feature looks like a distributed system

---

### 5.3 YAGNI — You Ain't Gonna Need It

> _"Do not build it until you need it."_

YAGNI is about resisting the urge to build for imagined future requirements. Every feature, abstraction, and capability that exists in code but is not used **today** is a liability: it costs time to build, time to maintain, time to understand, and time to work around when it does not quite fit the actual need that eventually arrives.

#### Rules

- **MUST NOT** build features, abstractions, or infrastructure for anticipated future requirements that are not validated:

  ```
  // YAGNI VIOLATION — building a plugin system for an app with 2 hard-coded integrations
  class PluginManager {
    private plugins: Map<string, Plugin> = new Map();
    register(name: string, plugin: Plugin) { ... }
    execute(name: string, context: PluginContext) { ... }
    unregister(name: string) { ... }
  }

  // WHAT WAS ACTUALLY NEEDED
  function syncWithStripe(order) { ... }
  function notifyViaSlack(message) { ... }
  ```

- **MUST NOT** add configuration options "just in case" — every config option is a decision point that someone will need to understand and maintain
- **MUST NOT** create database columns, API fields, or UI elements for features that are not yet approved or designed
- **SHOULD** keep clean seams (clear interfaces, separated concerns) so that complexity **can** be added later — but do not add the complexity itself

#### YAGNI Does NOT Mean

- **Does NOT mean "never plan ahead"** — you should design with clean boundaries and extensibility points. The distinction: building a **seam** (a clean interface that allows future extension) is cheap. Building the **full extension** for an unproven need is expensive.
- **Does NOT mean "ignore non-functional requirements"** — security, accessibility, observability, and error handling are always needed. They are current requirements, not future ones.
- **Does NOT mean "write throwaway code"** — the code you write should still be clean, tested, and maintainable. YAGNI controls **scope**, not **quality**.

#### The Seam vs Implementation Distinction

```
// SEAM (cheap, good) — a clean interface that allows future extension
interface NotificationSender {
  send(recipient: string, message: string): Promise<void>;
}

// Current implementation (simple, direct)
class EmailNotificationSender implements NotificationSender {
  async send(recipient, message) {
    await emailClient.send(recipient, message);
  }
}

// YAGNI VIOLATION (expensive, premature) — building SMS, push, webhook
// senders before anyone has asked for them
class SMSNotificationSender implements NotificationSender { ... }
class PushNotificationSender implements NotificationSender { ... }
class WebhookNotificationSender implements NotificationSender { ... }
class NotificationRouter {
  // Complex routing logic for channels nobody uses yet
}
```

The seam costs almost nothing and enables future extension. The full implementation costs hours/days and may never be needed — or may need a completely different design than what you imagined.

---

### 5.4 How These Principles Interact

DRY, KISS, and YAGNI sometimes pull in different directions. When they conflict, use this priority:

```
1. Correctness     — above all, the code must work correctly
2. Clarity (KISS)  — the code must be understandable
3. Scope (YAGNI)   — build only what is needed now
4. Deduplication (DRY) — eliminate knowledge duplication (not code similarity)
```

| Scenario | Tension | Resolution |
|---|---|---|
| Two similar functions for different domains | DRY says merge; KISS/YAGNI say they may diverge | Keep them separate until the third instance proves they are the same |
| Complex abstraction that eliminates duplication | DRY says abstract; KISS says it is harder to understand | Prefer the simpler duplicated version unless the duplication has already caused bugs |
| Generic framework for a one-use-case feature | YAGNI says do not build it; the developer says "we will need it later" | Build the simple version now; create a seam for extension; build the framework when the need is proven |
| Security validation that "slows things down" | Speed says skip it; correctness says it is required | Non-negotiable — security, error handling, and validation are current requirements, never YAGNI |

> **Key insight:** Duplication is cheaper than the wrong abstraction. You can always extract a shared module later (with the benefit of more data points). Undoing the wrong abstraction is far more expensive because other code has already coupled to it.

---

## 6. Separation of Concerns, Layering & Modular Design

Good architecture is not about choosing the right framework — it is about organizing code so that each part has a clear purpose, changes are localized, and the system can evolve without cascading rewrites. This section defines the three pillars of structural quality: separating concerns, enforcing layers, and designing modular boundaries.

---

### 6.1 Separation of Concerns

> _"Each part of the system should address a distinct aspect of the problem."_

Separation of concerns means that presentation logic, business rules, data access, and infrastructure concerns live in distinct, identifiable parts of the codebase — not tangled together in the same function or file.

#### Rules

- **MUST** separate these fundamental concerns into distinct modules:

  | Concern | Responsibility | Must NOT Contain |
  |---|---|---|
  | **Presentation / UI** | Rendering, user interaction, display formatting | Business rules, database queries, direct API calls to external services |
  | **Business logic / Services** | Domain rules, use-case orchestration, validation of business invariants | UI rendering, framework-specific code, direct database queries |
  | **Data access / Repositories** | Database queries, external API communication, data mapping | Business rules, UI rendering, request/response handling |
  | **Schemas / Contracts** | Data shape definitions, validation rules, type definitions | Implementation logic of any kind |
  | **Configuration** | Environment variables, feature flags, constants | Business logic, data access |

- **MUST** be able to answer for any function or file: **"Which concern does this belong to?"** If the answer is "multiple," the code needs to be restructured

- **MUST NOT** mix concerns within a single function:

  ```
  // BAD — UI concern + business logic + data access in one function
  function handleSubmit(formData) {
    // Presentation concern: reading form values
    const name = formData.get("name");
    const email = formData.get("email");

    // Business logic: discount calculation
    const discount = calculateLoyaltyDiscount(email);

    // Data access: direct database call
    const user = await db.query("INSERT INTO users ...");

    // Presentation concern: UI feedback
    showToast("User created!");
  }

  // GOOD — each concern in its own layer
  // UI layer: handles form interaction
  function handleSubmit(formData) {
    const input = parseFormData(formData);
    const result = await userService.createUser(input);
    showToast("User created!");
  }

  // Service layer: business logic
  function createUser(input) {
    const validated = createUserSchema.parse(input);
    validated.discount = calculateLoyaltyDiscount(validated.email);
    return userRepository.create(validated);
  }

  // Repository layer: data access
  function create(userData) {
    return db.query("INSERT INTO users ...", [userData]);
  }
  ```

#### Why It Matters

- **Testability:** business logic can be tested without a UI, a database, or a network
- **Changeability:** swapping a database, redesigning a UI, or changing an API contract affects only the relevant layer
- **Readability:** each file has a clear purpose — no mental context-switching within a single module
- **Security:** validation and authorization are easier to enforce when they live in well-defined places, not scattered across the codebase

---

### 6.2 Layering Rules

Layers define the **dependency direction** — which parts of the system are allowed to know about and call which other parts. Without enforced layers, the codebase devolves into a web of circular dependencies where everything depends on everything.

#### The Standard Layers

```text
┌─────────────────────────────────────────────┐
│             Presentation / UI               │  ← Knows about services
│   (components, pages, views, controllers)   │  ← MUST NOT know about repositories
├─────────────────────────────────────────────┤
│           Application Services              │  ← Knows about repositories and schemas
│      (use-cases, business orchestration)    │  ← MUST NOT know about UI or framework
├─────────────────────────────────────────────┤
│         Repositories / Data Access          │  ← Knows about database/external APIs
│      (queries, API clients, adapters)       │  ← MUST NOT know about services or UI
├─────────────────────────────────────────────┤
│        Schemas, Types & Contracts           │  ← Shared across layers
│    (validation, type definitions, DTOs)     │  ← MUST NOT contain implementation
├─────────────────────────────────────────────┤
│          Shared Utilities / Lib             │  ← Pure functions, helpers
│     (formatting, date handling, parsing)    │  ← MUST NOT depend on any layer above
└─────────────────────────────────────────────┘
```

#### Dependency Direction Rules

- **MUST** enforce a strict top-to-bottom dependency direction: UI → Services → Repositories
- **MUST NOT** allow upward dependencies:
  - Repositories **MUST NOT** import from services or UI
  - Services **MUST NOT** import from UI
- **MUST NOT** allow circular dependencies between any modules — if A depends on B, B must not depend on A (directly or transitively)
- **SHOULD** use schemas and types as the shared language between layers — they may be imported by any layer
- **SHOULD** keep shared utilities (lib) free of dependencies on any application layer — they are leaf nodes in the dependency graph

#### Enforcement

- **SHOULD** structure the project directory to reflect the layering:

  ```text
  src/
    components/     ← Presentation
    services/       ← Business logic
    repositories/   ← Data access
    schemas/        ← Shared contracts
    lib/            ← Shared utilities
  ```

- **SHOULD** use linting rules or architectural testing tools to enforce dependency direction automatically (e.g., ESLint import restrictions, dependency-cruiser)
- **MUST** treat layer violations as code review blockers — a repository that imports a component, or a component that queries the database directly, is an architectural defect

#### Layer Communication

- **MUST** communicate between layers using well-defined data structures (DTOs, validated schemas) — not framework-specific objects:

  ```
  // BAD — service receives a framework-specific request object
  function createUser(req: HttpRequest) {
    const body = req.body;  // coupled to HTTP framework
    // ...
  }

  // GOOD — service receives a validated, plain data structure
  function createUser(input: CreateUserInput) {
    // ... framework-agnostic business logic
  }
  ```

- **SHOULD** avoid passing more data between layers than necessary — each layer boundary is an opportunity to narrow the data to what the receiving layer actually needs

---

### 6.3 Modular Design

Modularization is about organizing code into **cohesive, loosely coupled units** with clear boundaries. Good modules can be understood, tested, modified, and replaced independently.

#### Core Concepts

| Concept | Definition | Goal |
|---|---|---|
| **Cohesion** | How strongly the elements within a module relate to each other | **High** — everything inside a module should contribute to a single, well-defined purpose |
| **Coupling** | How much one module depends on the internals of another | **Low** — modules should interact through narrow, stable interfaces, not by reaching into each other's internals |
| **Encapsulation** | Hiding internal details behind a public interface | Each module exposes **what** it does, not **how** it does it |
| **Composability** | The ability to combine small modules into larger behavior | Modules should be combinable like building blocks, not tangled like spaghetti |

#### Rules

- **MUST** design modules with high cohesion — group code that changes together, serves the same purpose, and operates on the same data
- **MUST** minimize coupling between modules — a change inside one module should not require changes in others
- **MUST** define clear public interfaces (exports) for each module — internal implementation details **MUST NOT** be accessed by other modules:

  ```text
  // Module: user-management

  PUBLIC (exported — the contract):
    createUser(input)
    getUserById(id)
    updateUser(id, changes)
    deleteUser(id)
    UserSchema, User type

  PRIVATE (internal — implementation details):
    hashPassword(password)
    generateVerificationToken()
    formatUserForResponse(dbRow)
    SQL queries, repository details
  ```

- **SHOULD** apply the **"module boundary test"**: imagine drawing a box around the module. The lines crossing the boundary (imports and exports) should be few, well-defined, and stable. If the boundary is porous (many internal details leak out), the module is not well encapsulated

- **SHOULD** prefer feature-based modules over type-based modules when the codebase grows:

  ```text
  // TYPE-BASED (groups by technical role — weak cohesion across features)
  src/
    components/
      UserList.tsx
      UserForm.tsx
      InvoiceList.tsx
      InvoiceForm.tsx
    services/
      userService.ts
      invoiceService.ts
    repositories/
      userRepository.ts
      invoiceRepository.ts

  // FEATURE-BASED (groups by domain — high cohesion within features)
  src/
    features/
      users/
        components/
        services/
        repositories/
        schemas/
        index.ts         ← public API of this feature module
      invoices/
        components/
        services/
        repositories/
        schemas/
        index.ts
    shared/              ← truly shared code (UI primitives, utilities)
  ```

- **SHOULD** use an `index` file (or equivalent) as the public interface of a feature module — other modules import from the index, never from internal files directly

#### When to Split a Module

- **SHOULD** split a module when it shows these symptoms:
  - The module has **multiple reasons to change** (SRP violation at the module level)
  - The module file or folder has grown beyond **~500 lines or ~10 files** and contains distinct sub-concerns
  - Different parts of the module are used by **different consumers** (some consumers need part A but not part B)
  - The module name requires "and" to describe its purpose

#### When to Keep Together

- **SHOULD** keep code in the same module when:
  - The pieces **always change together** — splitting would create shotgun surgery (changing one feature requires touching many modules)
  - The pieces are **tightly coupled by nature** — they share internal data structures and splitting would require exposing internals
  - The module is small and cohesive — splitting would create trivially small modules that add navigation overhead without benefit

#### Module Dependency Rules

- **MUST** maintain a clear, acyclic dependency graph between modules — if Module A depends on Module B, Module B must not depend on Module A
- **SHOULD** resolve circular dependencies by:
  1. Extracting the shared concern into a third module that both depend on
  2. Introducing an interface/contract that inverts the dependency direction
  3. Merging the modules if they are truly inseparable (they may actually be one concern)

- **SHOULD** visualize module dependencies periodically (especially as the project grows) to identify unhealthy coupling patterns — tools like dependency-cruiser can automate this

  ```text
  // HEALTHY — clear, acyclic dependencies
  users → shared
  invoices → shared
  invoices → users (one-directional)

  // UNHEALTHY — circular dependency
  users → invoices → users  ← PROBLEM
  
  // FIX — extract shared concept
  users → shared
  invoices → shared
  shared/customer-types  ← the shared concept both need
  ```

---

### 6.4 Architecture Patterns — Rules of Thumb

These are guidelines for choosing how much architectural structure a project needs. Over-architecting a simple project is as harmful as under-architecting a complex one.

#### Scale Architecture to Project Complexity

| Project Stage | Recommended Structure | Rationale |
|---|---|---|
| **Prototype / Script** | Flat files, minimal structure | Speed matters more than architecture |
| **Small project** (1 developer, <10 routes) | Layered folders (components, services, repositories, schemas) | Clear separation without overhead |
| **Medium project** (2–5 developers, 10–50 routes) | Layered + feature modules for complex domains | Feature modules prevent cross-team conflicts |
| **Large project** (5+ developers, 50+ routes) | Feature modules as primary organization, shared kernel | Module boundaries become team boundaries |

- **MUST** start with the simplest structure that provides clear separation of concerns
- **MUST** document the architectural decision in an ADR when migrating from one structure to another
- **MUST NOT** adopt complex patterns (microservices, CQRS, event sourcing) without a proven, measured need — → See [Section 12](#12-non-goals--avoid-overengineering) for scaling triggers

#### The Refactoring Safety Net

Good separation and modularity make refactoring safe. If the codebase follows these principles:

- Concerns are separated → you can change one layer without breaking others
- Layers have clear direction → you know the impact radius of any change
- Modules are cohesive → you can refactor within a module without affecting the rest of the system
- Dependencies are explicit → you can trace the impact of any change through the dependency graph

If refactoring feels dangerous, the architecture has structural debt that should be addressed.

---

## 7. Naming Conventions (Universal)

Naming is the most frequent design decision a developer makes. Every variable, function, file, and module is an act of communication. Good names make code self-documenting; bad names force readers to decode intent from context, comments, or — worst case — the implementation itself.

---

### 7.1 Naming Philosophy

- **MUST** choose names that reveal intent — a reader should understand what something **is** or what it **does** without reading the implementation:

  ```
  // BAD — reveals nothing about purpose
  const d = getData();
  const tmp = process(d);
  const flag = check(tmp);

  // GOOD — intent is immediately clear
  const activeUsers = fetchActiveUsers();
  const enrichedUsers = attachLoyaltyScores(activeUsers);
  const hasEligibleUsers = enrichedUsers.length > 0;
  ```

- **MUST** use names proportional to scope — the larger the scope, the more descriptive the name should be:

  | Scope | Acceptable Name Length | Example |
  |---|---|---|
  | Loop variable (1–3 lines) | Single letter or very short | `i`, `x`, `item` |
  | Local variable (within a function) | Short but descriptive | `total`, `retryCount`, `userEmail` |
  | Function / method | Descriptive verb + noun | `calculateDiscount`, `sendWelcomeEmail` |
  | Module-level / exported | Fully descriptive, unambiguous | `UserAuthenticationService`, `validateCreateOrderInput` |

- **MUST** be consistent — once a concept has a name, use the same name everywhere. Do not refer to the same thing as `user`, `client`, `account`, and `customer` across different parts of the system unless they represent genuinely different concepts
- **MUST NOT** use abbreviations unless they are universally understood in the domain (e.g., `id`, `url`, `api`, `db` are acceptable; `usr`, `mgr`, `proc`, `svc` are not)

### 7.2 Universal Casing Rules

Different contexts demand different casing conventions. The specific standard depends on the language and ecosystem, but the principle is universal: **be consistent within each context and follow the ecosystem's established convention**.

#### General Reference Table

| Context | Convention | Examples |
|---|---|---|
| Local variables, function parameters | `camelCase` | `userId`, `totalAmount`, `isActive` |
| Functions, methods | `camelCase` | `calculateTotal`, `getUserById` |
| Types, interfaces, classes, enums | `PascalCase` | `UserProfile`, `OrderStatus`, `PaymentResult` |
| Constants (true compile-time / environment constants) | `UPPER_SNAKE_CASE` | `MAX_RETRIES`, `DEFAULT_PAGE_SIZE`, `API_BASE_URL` |
| Database tables, columns | `snake_case` | `user_profiles`, `created_at`, `is_active` |
| File and folder names | `kebab-case` | `user-profile.ts`, `order-service.ts`, `api-client/` |
| Environment variables | `UPPER_SNAKE_CASE` | `DATABASE_URL`, `JWT_SECRET` |
| URL paths and API endpoints | `kebab-case` | `/api/user-profiles`, `/api/order-items` |

#### Rules

- **MUST** follow the casing convention established by the language and ecosystem — do not invent project-specific conventions that contradict community standards
- **MUST** be consistent within each context — never mix `camelCase` and `snake_case` in the same layer (e.g., all JavaScript variables in camelCase, all database columns in snake_case)
- **SHOULD** handle casing transformation at the boundary between layers — for example, map `snake_case` database column names to `camelCase` object properties at the repository level, so the rest of the application works with a single convention
- **MUST NOT** use `UPPER_SNAKE_CASE` for regular variables or runtime-computed values — reserve it for true constants whose value is known at compile time or configuration time

### 7.3 Naming Functions & Methods

Functions represent **actions**. Their names should communicate what they do and, when relevant, what they return.

#### Rules

- **MUST** name functions with a **verb** (or verb phrase) that describes the action:

  | Pattern | Use When | Examples |
  |---|---|---|
  | `verbNoun` | General actions | `createUser`, `sendEmail`, `calculateTotal` |
  | `getX` / `fetchX` | Retrieving data | `getUserById`, `fetchActiveOrders` |
  | `isX` / `hasX` / `canX` | Boolean-returning functions | `isExpired`, `hasPermission`, `canEdit` |
  | `toX` / `fromX` | Transformations / conversions | `toJSON`, `fromDTO`, `toCents` |
  | `validateX` / `parseX` | Validation / parsing | `validateEmail`, `parseConfig` |
  | `handleX` / `onX` | Event handlers | `handleSubmit`, `onUserCreated` |

- **MUST NOT** use vague verbs that convey no specific action:

  ```
  // BAD — what does "do", "process", "manage", "handle" mean specifically?
  function doUser() { ... }
  function processData() { ... }
  function manageOrders() { ... }
  function handleStuff() { ... }

  // GOOD — specific action
  function activateUser() { ... }
  function enrichOrderWithPricing() { ... }
  function cancelExpiredOrders() { ... }
  ```

- **SHOULD** make the function name reflect the level of abstraction — a high-level orchestration function should have a high-level name; a low-level utility should have a precise, technical name:

  ```
  // High-level (service layer) — business language
  function processMonthlyBilling() { ... }

  // Low-level (utility) — technical precision
  function roundToTwoDecimalPlaces(value) { ... }
  ```

- **SHOULD** avoid redundant context — if a function lives inside a `UserService` module, do not repeat "user" in every method name:

  ```
  // BAD — redundant context
  class UserService {
    getUserById() { ... }
    createUser() { ... }
    deleteUser() { ... }
  }

  // GOOD — the class context provides the noun
  class UserService {
    getById() { ... }
    create() { ... }
    delete() { ... }
  }
  ```

### 7.4 Naming Variables & Properties

Variables represent **things**. Their names should communicate what data they hold.

#### Rules

- **MUST** name booleans as questions that read naturally with `if`:

  ```
  // BAD — ambiguous, doesn't read like a question
  const active = true;
  const email = false;
  const loading = true;

  // GOOD — reads naturally: "if isActive", "if hasVerifiedEmail", "if isLoading"
  const isActive = true;
  const hasVerifiedEmail = false;
  const isLoading = true;
  ```

  Common boolean prefixes: `is`, `has`, `can`, `should`, `was`, `will`

- **MUST** name collections (arrays, lists, sets) as **plurals** to signal "more than one":

  ```
  // BAD — singular name for a collection
  const user = fetchAllUsers();
  const item = order.getItems();

  // GOOD — plural signals collection
  const users = fetchAllUsers();
  const items = order.getItems();
  ```

- **MUST NOT** use single-letter variable names outside of trivially short scopes (loop counters, lambda parameters in simple operations):

  ```
  // ACCEPTABLE — trivial scope, meaning is obvious
  for (let i = 0; i < items.length; i++) { ... }
  const doubled = numbers.map((n) => n * 2);

  // NOT ACCEPTABLE — meaningful logic, single letter hides intent
  const u = await getUser(id);
  const r = calculateResult(u.orders);
  if (r.s === "f") { ... }
  ```

- **SHOULD** avoid negative boolean names — they create double-negative confusion:

  ```
  // BAD — double negation is confusing
  if (!isNotReady) { ... }
  if (!isDisabled) { ... }

  // GOOD — positive, clear
  if (isReady) { ... }
  if (isEnabled) { ... }
  ```

### 7.5 Naming Types, Interfaces & Schemas

Types represent **shapes and contracts**. Their names should communicate what data structure or concept they describe.

#### Rules

- **MUST** use `PascalCase` for all type names, interface names, and schema names
- **SHOULD** use descriptive noun phrases that reflect the domain concept:

  ```
  // Types and interfaces
  type UserProfile = { ... }
  type CreateOrderInput = { ... }
  type PaginatedResponse<T> = { ... }
  interface PaymentProcessor { ... }
  ```

- **SHOULD** use consistent suffixes to distinguish related types:

  | Suffix | Purpose | Example |
  |---|---|---|
  | `Input` / `Params` | Data coming into a function or API | `CreateUserInput`, `SearchParams` |
  | `Output` / `Result` | Data returned from a function or API | `CreateUserResult`, `SearchOutput` |
  | `Config` / `Options` | Configuration objects | `DatabaseConfig`, `RetryOptions` |
  | `Schema` | Validation schema (e.g., Zod, Pydantic) | `CreateUserSchema`, `LoginSchema` |
  | `Error` | Custom error classes | `NotFoundError`, `ValidationError` |
  | `Repository` | Data access interfaces | `UserRepository`, `OrderRepository` |
  | `Service` | Business logic interfaces | `BillingService`, `NotificationService` |

- **MUST NOT** use prefixes like `I` for interfaces (e.g., `IUserService`) unless the language/ecosystem convention demands it — modern TypeScript and most languages do not require this

### 7.6 Naming Files & Directories

File and directory names serve as the **table of contents** for the codebase. A developer should be able to navigate the project by reading names alone.

#### Rules

- **MUST** use `kebab-case` for file and directory names (exception: framework conventions that require otherwise, e.g., component files in some ecosystems)
- **MUST** name files after their primary export or purpose — one concept per file:

  ```
  // BAD — vague, becomes a dumping ground
  utils.ts
  helpers.ts
  common.ts
  misc.ts
  types.ts  (for the entire project)

  // GOOD — specific, cohesive
  format-currency.ts
  calculate-discount.ts
  user-schema.ts
  order-repository.ts
  date-utils.ts  (acceptable if limited to date-related utilities)
  ```

- **SHOULD** use directory names that reflect the architectural role or domain concept:

  ```
  // Architectural roles
  services/
  repositories/
  schemas/
  lib/

  // Domain concepts (feature modules)
  features/users/
  features/invoices/
  features/authentication/
  ```

- **MUST NOT** create deeply nested directory structures that add navigation overhead without adding clarity — if a folder contains a single file, the folder likely is not needed
- **SHOULD** keep nesting to a maximum of 3–4 levels under `src/` — deeper nesting signals either over-organization or a module that should be restructured

### 7.7 Common Naming Pitfalls

| Pitfall | Problem | Fix |
|---|---|---|
| **Generic names** (`data`, `info`, `item`, `thing`, `result`, `temp`) | Convey no meaning — the reader must trace the code to understand | Use domain-specific names: `orderSummary`, `userCredentials`, `paymentResult` |
| **Acronyms and abbreviations** (`usrMgr`, `txnProc`, `acctSvc`) | Require domain knowledge to decode, hostile to new team members | Spell it out: `userManager`, `transactionProcessor`, `accountService` |
| **Inconsistent vocabulary** (using `user` / `client` / `account` / `customer` interchangeably) | Creates confusion about whether these are the same concept or different ones | Choose one term per concept and use it everywhere; document the glossary if the domain has multiple related terms |
| **Misleading names** (a function called `getUser` that also modifies the database) | The name lies about what the code does — the most dangerous form of bad naming | Rename to match actual behavior: `getOrCreateUser`, or split into `getUser` + `createUser` |
| **Encoding type in the name** (`userString`, `orderArray`, `isActiveBoolean`) | Redundant — the type system already communicates this; the name becomes stale if the type changes | Name by meaning, not by type: `userName`, `orders`, `isActive` |

> → See domain-specific documents for additional naming conventions: [04-database-standards.md] for table/column naming, [05-frontend-standards.md] for component naming, [03-api-design.md] for endpoint naming.

---

## 8. Documentation Standards

Documentation is a deliverable, not an afterthought. Code that works but cannot be understood, onboarded into, or maintained by others is a liability. This section defines what to document, where to document it, and to what standard.

---

### 8.1 Documentation Philosophy

- **MUST** treat documentation as part of the Definition of Done — a feature without documentation is not complete (→ See [Section 11](#11-definition-of-done-universal))
- **MUST** write all technical documentation in **English** — code, comments, commit messages, README, ADRs, and technical docs. This ensures maximum compatibility with tooling, AI assistants, search, and international collaboration
- **SHOULD** optimize documentation for the **most common reader**: a developer joining the project (or returning after a break) who needs to understand the system quickly
- **SHOULD** keep documentation **close to the code it describes** — documentation that lives far from the code it documents becomes stale faster
- **MUST NOT** document what the code already communicates clearly — well-named functions, types, and modules are the best documentation. Written documentation should fill the gaps that code cannot express: intent, constraints, trade-offs, and context

#### The Documentation Pyramid

```text
┌─────────────────────────┐
│   Architecture Docs     │  ← Why: decisions, trade-offs, system shape
│   (ADRs, diagrams)      │     Audience: new developers, future self
├─────────────────────────┤
│   API & Module Docs     │  ← What: contracts, interfaces, public APIs
│   (docstrings, OpenAPI) │     Audience: consumers of the module
├─────────────────────────┤
│   Code-Level Docs       │  ← How (when non-obvious): inline comments
│   (comments, TODOs)     │     Audience: developers reading the code
├─────────────────────────┤
│   Self-Documenting Code │  ← The foundation: naming, types, structure
│   (names, types, tests) │     Audience: everyone, always
└─────────────────────────┘

Priority: invest most effort at the base (self-documenting code)
and add upper layers only where the code alone is insufficient.
```

---

### 8.2 Code Documentation (Docstrings)

Docstrings (TSDoc, JSDoc, Python docstrings) document the **public interface** of functions, classes, and modules — the "contract" that consumers depend on.

#### Rules

- **MUST** add docstrings to:
  - All exported / public functions and methods
  - All exported types and interfaces that are not self-explanatory
  - All service-layer and repository-layer functions
  - Any function with non-obvious behavior, constraints, or side effects

- **SHOULD** add docstrings to:
  - Complex utility functions
  - Functions with more than 2 parameters
  - Functions that throw specific errors (document which errors and when)

- **MAY** skip docstrings for:
  - Trivially simple, self-explanatory private functions (e.g., `function add(a, b) { return a + b; }`)
  - Functions whose name, parameters, and return type tell the complete story

#### Docstring Content

- **MUST** include:
  - A brief description of **what** the function does (one sentence)
  - `@param` — description of each parameter and its expected values/constraints
  - `@returns` — description of the return value
  - `@throws` — which errors the function may throw and under what conditions

- **SHOULD** include:
  - `@example` — a usage example for functions with non-obvious usage patterns
  - Business context — **why** this function exists, if not obvious from the name

- **MUST NOT** include:
  - Redundant restatement of the type signature — the type system already communicates this
  - Implementation details — the docstring describes the **contract**, not the algorithm

#### Example

```
/**
 * Calculates the total price for an order, applying applicable discounts
 * and tax based on the customer's region.
 *
 * @param items - The line items in the order. Each must have a positive price and quantity.
 * @param region - The customer's region code, used to determine tax rate.
 * @param couponCode - Optional promotional coupon. Validated against active promotions.
 * @returns The final order total in the smallest currency unit (e.g., cents).
 * @throws {ValidationError} If any item has an invalid price or quantity.
 * @throws {NotFoundError} If the coupon code does not match an active promotion.
 *
 * @example
 * const total = calculateOrderTotal(
 *   [{ productId: "abc", price: 1000, quantity: 2 }],
 *   "PT",
 *   "SUMMER20"
 * );
 * // Returns: 1840 (2000 - 20% discount + 23% IVA)
 */
function calculateOrderTotal(items, region, couponCode?) { ... }
```

---

### 8.3 README Standards

Every project **MUST** have a `README.md` that serves as the entry point for anyone encountering the project. The README answers: **"What is this, how do I run it, and where do I find more information?"**

#### Minimum Required Sections

- **MUST** include the following sections in every project README:

  ```markdown
  # Project Name

  Brief description — what this project does and why it exists (1–3 sentences).

  ## Tech Stack

  List of core technologies and their roles in the project.

  ## Getting Started

  ### Prerequisites
  - Runtime version (e.g., Node.js >= 20, Python >= 3.12)
  - Package manager
  - Required external services (database, third-party APIs)

  ### Setup
  Step-by-step instructions to go from clone to running application:
  1. Clone the repository
  2. Copy environment file: `cp .env.example .env.local`
  3. Install dependencies
  4. Start development server

  ## Project Structure

  Brief explanation of the folder structure and key architectural conventions.
  Link to 01-core-principles.md and other relevant standards.

  ## Available Scripts

  List of available commands (dev, build, test, lint) with brief descriptions.

  ## Environment Variables

  Reference to .env.example with explanation of required variables,
  or a table listing each variable, its purpose, and whether it is required.
  ```

#### Recommended Additional Sections

- **SHOULD** include when applicable:

  | Section | Include When |
  |---|---|
  | **Architecture Overview** | The system has multiple services, layers, or complex data flows |
  | **Deployment** | Deployment process is not fully automated or has manual steps |
  | **Contributing** | The project accepts contributions (team or open source) |
  | **API Reference** | The project exposes an API (or link to API documentation) |
  | **Troubleshooting / FAQ** | Common setup issues exist |
  | **License** | Always for open source; recommended for all projects |

#### README Maintenance Rules

- **MUST** update the README when:
  - Setup steps change (new dependency, new env var, new prerequisite)
  - Project structure changes significantly
  - Core architectural decisions change
- **SHOULD** review the README as part of the onboarding process — if a new developer cannot set up the project by following the README alone, the README is incomplete
- **MUST NOT** let the README become a comprehensive wiki — keep it focused on getting started and orienting the reader. Detailed docs belong in the `docs/` directory

---

### 8.4 Architecture Documentation

Architecture documentation captures the **system-level decisions** that shape the project — the "why" behind the structure. This is the documentation that helps developers understand the big picture, not just individual functions.

#### Architecture Decision Records (ADR)

- ADRs are the primary tool for documenting architecture decisions — → See [Section 9](#9-architecture-decision-records-adr) for the complete ADR guide

#### System Documentation

- **SHOULD** maintain a high-level architecture overview in `docs/architecture.md` (or equivalent) for projects with non-trivial architecture:
  - System context — what the system does, who uses it, what it integrates with
  - High-level component diagram — the major parts and how they interact
  - Key data flows — how a request moves through the system
  - Technology choices — what is used and why (reference the ADRs)

- **SHOULD** use diagrams for architecture documentation — visual representations communicate structure more effectively than prose:
  - Prefer simple, text-based diagram formats that live in version control (Mermaid, PlantUML, ASCII diagrams)
  - **MUST NOT** rely solely on diagrams in external tools (Figma, Miro, Lucidchart) that are not version-controlled — these drift from reality. If external tools are used, maintain a version-controlled copy or reference link

- **SHOULD** keep architecture documentation at a level of abstraction that changes infrequently — component names, data flow direction, integration boundaries. Implementation details that change often should not be in architecture docs

#### Rules

- **MUST** document the system architecture before the project reaches production — even a simple one-page overview
- **MUST** update architecture documentation when the system structure changes (new service, new integration, changed data flow)
- **SHOULD** date architecture documents and indicate the last review — stale architecture docs are misleading

---

### 8.5 API Documentation

Any API (HTTP, library, module) that is consumed by others — whether external users, other teams, or other modules within the project — **MUST** be documented.

#### Rules

- **MUST** document every public API endpoint with:
  - HTTP method and path
  - Purpose (what the endpoint does)
  - Request parameters (path, query, body) with types and constraints
  - Response format (success and error) with examples
  - Authentication and authorization requirements
  - Rate limiting information (if applicable)

- **SHOULD** use a machine-readable API specification format:
  - **OpenAPI / Swagger** for HTTP APIs (preferred)
  - **GraphQL SDL** for GraphQL APIs
  - **Type definitions** for library/module APIs

- **SHOULD** keep API documentation in sync with the implementation:
  - Prefer documentation generated from code (schema-first or code-first with extraction) over manually maintained docs
  - If documentation is manual, include it in the Definition of Done for API changes

- **MUST NOT** expose internal API documentation publicly unless intended — internal endpoints should be documented separately from public ones

> → See [03-api-design.md] for detailed API design standards including error handling, pagination, and response envelopes.

---

### 8.6 Inline Documentation — TODOs and Technical Debt

TODOs and similar markers are a form of documentation for known incomplete work. Unmanaged, they become noise — managed properly, they are a useful tracking mechanism.

#### Rules

- **MUST** include a reference (issue number, ticket ID) with every TODO:

  ```
  // BAD — open-ended, no tracking, will be forgotten
  // TODO: fix this later
  // TODO: handle edge case
  // FIXME: sometimes breaks

  // GOOD — tracked, attributable, actionable
  // TODO(#234): Add retry logic for transient API failures
  // FIXME(#567): Race condition when two users update simultaneously
  ```

- **MUST NOT** use TODOs as a substitute for fixing known issues — a TODO without a corresponding issue/ticket is invisible to project management
- **SHOULD** periodically audit TODOs (e.g., during sprint planning) and either resolve them or create tickets
- **SHOULD** use consistent markers:

  | Marker | Meaning |
  |---|---|
  | `TODO` | Planned improvement or missing feature |
  | `FIXME` | Known bug or broken behavior that needs fixing |
  | `HACK` | Intentional workaround — document why and the conditions for removal |
  | `NOTE` | Important context for the reader (not an action item) |

---

### 8.7 What NOT to Document

Over-documentation is almost as harmful as under-documentation — it creates noise, becomes stale, and gives a false sense of understanding.

- **MUST NOT** document what the code already says clearly:

  ```
  // BAD — the code already says this
  /** Returns the user's full name. */
  function getUserFullName(user) {
    return `${user.firstName} ${user.lastName}`;
  }

  // GOOD — documents the non-obvious "why"
  /**
   * Returns the user's display name for UI rendering.
   * Falls back to email prefix if name fields are empty,
   * which happens for users imported from the legacy system.
   */
  function getUserDisplayName(user) {
    if (user.firstName && user.lastName) {
      return `${user.firstName} ${user.lastName}`;
    }
    return user.email.split("@")[0];
  }
  ```

- **MUST NOT** maintain documentation that duplicates information available in a single source of truth — e.g., do not manually list all environment variables in both the README and a separate doc when `.env.example` serves as the source
- **SHOULD** delete stale documentation rather than leaving it — inaccurate docs are worse than missing docs
- **SHOULD** prefer improving code clarity (better names, simpler structure) over adding explanatory comments

> **Rule of thumb:** if you feel the need to write a long comment explaining what a piece of code does, consider whether the code itself can be rewritten to not need the explanation.

---

## 9. Architecture Decision Records (ADR)

An Architecture Decision Record is a short document that captures a significant decision, the context behind it, the alternatives considered, and the consequences accepted. ADRs are the **institutional memory** of a project — they answer the question that every developer eventually asks: _"Why was it done this way?"_

---

### 9.1 Why ADRs Matter

Without ADRs:
- Developers change things that were designed intentionally, because they do not know the reasoning
- The same debates happen repeatedly, wasting time and creating inconsistency
- New team members make assumptions about past decisions instead of understanding the actual trade-offs
- Technical debt accumulates invisibly — no one remembers which shortcuts were intentional and which were accidental

With ADRs:
- Decisions have documented rationale — they can be evaluated, challenged, and revisited with context
- Onboarding is faster — new developers understand not just **what** was built but **why**
- Trade-offs are explicit — the team consciously accepts risks instead of discovering them later
- Reversals are informed — when revisiting a decision, the original alternatives and their rejected reasons are available

---

### 9.2 When to Create an ADR

- **MUST** create an ADR when:
  - Introducing a **major new dependency** (database, auth provider, UI framework, state management library, payment processor)
  - Choosing or changing the **project architecture** (monolith vs microservices, layering strategy, module structure)
  - Deviating significantly from a **MUST** or **SHOULD** rule in any standards document — the ADR serves as the justification
  - Making a **security trade-off** (accepting a risk, choosing a weaker control for pragmatic reasons)
  - Choosing an **infrastructure or deployment strategy** (hosting provider, CI/CD platform, containerization approach)
  - Adding **significant complexity** to the system (queues, caching layers, background workers, event-driven patterns)
  - Making a decision that is **hard to reverse** — the higher the reversal cost, the more important the ADR

- **SHOULD** create an ADR when:
  - Choosing between two reasonable approaches where the team might later wonder why one was picked over the other
  - Establishing a **convention or pattern** that the team is expected to follow (e.g., "we use X pattern for Y across the project")
  - Deciding **not** to do something that might seem obvious (e.g., "we decided not to use an ORM because...")
  - Replacing or deprecating a previous decision (the new ADR should reference the old one)

- **MAY** skip an ADR when:
  - The decision is trivially reversible (e.g., a utility function name, a CSS class structure)
  - The decision follows an already-documented standard with no deviation
  - The decision is temporary and will be revisited within a defined short timeframe (document as a TODO with a ticket instead)

#### Quick Decision Test

Ask yourself: **"If a new developer joins in six months and asks 'why did we do it this way?', will anyone remember the answer?"** If the answer is no, write an ADR.

---

### 9.3 ADR Structure

Every ADR **MUST** follow a consistent structure. The goal is to be concise but complete — an ADR should take 10–30 minutes to write and 5 minutes to read.

#### Required Fields

| Field | Purpose |
|---|---|
| **Title** | Short, descriptive title that identifies the decision |
| **Status** | Current lifecycle state of the decision |
| **Context** | The problem, constraints, and forces that led to this decision |
| **Decision** | What was decided — clearly and unambiguously stated |
| **Alternatives Considered** | At least 2 alternatives and why they were not chosen |
| **Consequences** | The expected positive outcomes, negative trade-offs, and risks accepted |

#### Status Lifecycle

```text
Proposed → Accepted → See [Superseded | Deprecated]
```

| Status | Meaning |
|---|---|
| **Proposed** | Under discussion, not yet agreed upon |
| **Accepted** | Agreed and in effect — the team follows this decision |
| **Superseded** | Replaced by a newer decision (link to the new ADR) |
| **Deprecated** | No longer relevant (the feature/context was removed) |

- **MUST** never delete an ADR — mark it as Superseded or Deprecated instead. The historical record is valuable even for decisions that are no longer active
- **MUST** include a reference to the superseding ADR when marking one as Superseded

#### ADR Template Reference

The full ADR template with field descriptions and examples is maintained in `templates/adr-template.md`. The minimum structure:

```markdown
# ADR NNN: <Title>

## Status
Proposed | Accepted | Superseded by [ADR NNN] | Deprecated

## Date
YYYY-MM-DD

## Context
What problem are we solving? What constraints and forces exist?

## Decision
What are we doing? State the decision clearly.

## Alternatives Considered

### Alternative 1: <Name>
- Description
- Pros
- Cons
- Why rejected

### Alternative 2: <Name>
- Description
- Pros
- Cons
- Why rejected

## Consequences

### Positive
- Expected benefits

### Negative
- Accepted trade-offs and risks

### Action Items
- Concrete steps to implement this decision (if any)
```

---

### 9.4 ADR Quality Rules

- **MUST** write ADRs in English, consistent with all technical documentation
- **MUST** be concise — an ADR is not a research paper. One to two pages is the target length. If it needs more, the decision may need to be broken into smaller decisions
- **MUST** include at least **two alternatives** in every ADR — if there is only one option, it is not a decision, it is a constraint (document it differently)
- **MUST** be honest about trade-offs — every decision has downsides. An ADR that lists only positives is incomplete and not trustworthy
- **MUST** be specific — "we chose X because it is better" is not useful. Explain **better at what**, **for whom**, and **compared to what**:

  ```markdown
  // BAD — vague, not actionable
  ## Decision
  We will use Supabase because it is the best option.

  // GOOD — specific, reasoned
  ## Decision
  We will use Supabase as our database and authentication provider.
  It provides PostgreSQL with built-in Row Level Security, real-time
  subscriptions, and a managed auth system — which covers our current
  requirements without maintaining separate infrastructure for each concern.
  The trade-off is vendor lock-in to Supabase's API surface and pricing model.
  ```

- **SHOULD** be written close in time to the decision — do not rely on memory. Write the ADR when the decision is made, not weeks later
- **SHOULD** be reviewed by at least one other team member — a decision made in isolation is more likely to have blind spots

---

### 9.5 ADR Organization

- **MUST** store ADRs in the project repository under `docs/adr/`
- **MUST** use sequential numbering with zero-padding: `001-title.md`, `002-title.md`, etc.
- **MUST** use `kebab-case` for the title portion of the filename
- **SHOULD** maintain an index file (`docs/adr/README.md`) listing all ADRs with their status for quick reference:

  ```markdown
  # Architecture Decision Records

  | # | Title | Status | Date |
  |---|---|---|---|
  | 001 | [Use Supabase for database and auth](./001-use-supabase.md) | Accepted | 2026-01-15 |
  | 002 | [Adopt feature-based module structure](./002-feature-modules.md) | Accepted | 2026-02-01 |
  | 003 | [Use JWT with short expiry for API auth](./003-jwt-auth.md) | Superseded by 007 | 2026-02-10 |
  ```

- **SHOULD** reference ADRs from the code when relevant — a comment linking to the ADR is more maintainable than repeating the rationale in the code:

  ```
  // Uses direct Supabase query instead of generic repository pattern.
  // See ADR-001: we decided against an abstraction layer because we have
  // no plan to change databases and the indirection adds complexity.
  ```

---

### 9.6 Common ADR Triggers (Quick Reference)

This is a non-exhaustive list of situations that **MUST** or **SHOULD** trigger an ADR, consolidated from all standards documents:

| Trigger | Source |
|---|---|
| New major dependency (auth, DB, framework, UI kit) | This document, Section 9.2 |
| Change in project structure or layering rules | This document, Section 9.2 |
| Deviation from a MUST/SHOULD rule in any standard | This document, Section 9.2 |
| Security trade-off or risk acceptance | [07-security-standards.md, Section 2] |
| Authorization model choice (RBAC vs ABAC) | [07-security-standards.md, Section 5] |
| Authentication strategy choice | [07-security-standards.md, Section 4] |
| Introduction of Redis, queues, or background workers | This document, Section 12 |
| Migration from one architecture pattern to another | This document, Section 9.2 |
| API versioning strategy | → See [03-api-design.md] |
| Database technology or migration strategy change | → See [04-database-standards.md] |
| Adoption of Kubernetes or complex infrastructure | [07-security-standards.md, Section 12] |
| Choice to intentionally deviate from SOLID principles | This document, Section 4.6 |

---

## 10. Dependency Management Philosophy

Every external dependency is a trade-off. It saves development time today, but it introduces maintenance cost, security risk, and coupling to someone else's decisions tomorrow. Dependencies are not free — they are technical debt with interest, payable in upgrade effort, vulnerability response, and breaking changes.

This section defines the mindset and decision framework for managing this trade-off responsibly.

---

### 10.1 The Dependency Cost Model

Before adding a dependency, understand what you are actually adding to the project:

| Cost Category | Description |
|---|---|
| **Maintenance burden** | Someone must keep it updated — every dependency is a subscription to future work |
| **Security surface** | Every dependency (and its transitive dependencies) is an attack vector — a single compromised package can compromise your entire application |
| **Bundle size** | Client-side dependencies directly impact user experience (load time, bandwidth) |
| **API coupling** | Your code becomes coupled to the dependency's API — if it changes, you change |
| **Transitive risk** | A dependency's dependencies are also your dependencies — you inherit their risks and bugs without choosing them |
| **Abandonment risk** | If the maintainer stops updating, you are stuck with a rotting foundation |
| **Learning cost** | Every dependency has its own API, patterns, quirks, and bugs that the team must learn |

> **Key insight:** The true cost of a dependency is not the 5 minutes it takes to install — it is the cumulative cost of maintaining, updating, auditing, debugging, and eventually replacing it over the lifetime of the project.

---

### 10.2 The Decision Framework

#### Before Installing Anything, Ask These Questions (In Order)

1. **Can the platform solve this natively?**
   The language, runtime, or framework may already provide the capability. Native solutions have zero dependency cost.

2. **Can an existing dependency in the project solve this?**
   A package already in the project has already been vetted and its cost is already being paid. Check if it covers the use case before adding another.

3. **Can I solve this with a small, focused utility function?**
   If the solution is 10–50 lines of straightforward code, writing it yourself may be cheaper than adopting and maintaining a dependency — especially for simple operations (date formatting, string manipulation, basic validation patterns).

4. **Is the dependency truly necessary?**
   Only at this point should you consider adding a new package. The dependency should provide substantial value that justifies its ongoing cost.

#### Rules

- **MUST** justify every new dependency — the justification should be documentable: "We added X because it provides Y, which would take Z effort to build and maintain ourselves"
- **MUST NOT** add a dependency for trivial functionality — a package that provides a single utility function (e.g., `is-odd`, `left-pad`, `is-array`) is almost never justified
- **SHOULD** prefer dependencies that are:
  - **Actively maintained** — recent commits, responsive issue handling, regular releases
  - **Widely adopted** — large user base increases the likelihood of bugs being found and fixed
  - **Well-tested** — the dependency should have its own comprehensive test suite
  - **Minimal in scope** — does one thing well, with few transitive dependencies
  - **Permissively licensed** — MIT or Apache-2.0 preferred; review other licenses with care
- **SHOULD** check before installing:

  | Criterion | How to Check |
  |---|---|
  | Last meaningful commit | Repository activity (not just bot updates) |
  | Open issue responsiveness | Are maintainers engaging with issues? |
  | Download trend | Stable or growing, not declining |
  | Bundle size impact | Bundlephobia or equivalent analysis tool |
  | Transitive dependency count | Fewer is better — each one adds risk |
  | Known vulnerabilities | Security advisory databases |
  | License | Compatible with project requirements |

---

### 10.3 Dependency Tiers

Not all dependencies carry the same risk. Classify them by their impact to determine the appropriate level of scrutiny:

| Tier | Description | Examples | Scrutiny Level |
|---|---|---|---|
| **Critical** | Core to the application's functionality, deeply integrated, extremely hard to replace | Framework, database client, auth provider, ORM | Maximum — ADR required, thorough evaluation, monitor closely |
| **Important** | Significant functionality, moderate replacement effort | Validation library, HTTP client, date library, testing framework | High — evaluate carefully, review alternatives |
| **Convenience** | Saves time but easily replaceable with a small utility | Formatting helpers, slug generators, ID generators | Medium — ensure the value justifies the cost |
| **Development-only** | Used only during development, not shipped to production | Linters, formatters, test utilities, type checkers | Lower — still evaluate, but the risk surface is smaller |

#### Rules

- **MUST** create an ADR for all **Critical** tier dependency decisions
- **SHOULD** create an ADR for **Important** tier dependencies when multiple viable alternatives exist
- **SHOULD** periodically review **Convenience** tier dependencies — they are the most likely to be replaceable with native code or an existing dependency
- **MUST** keep development-only dependencies strictly in devDependencies (or equivalent) — they must never reach the production bundle

---

### 10.4 Keeping Dependencies Healthy

Adding a dependency is not a one-time decision — it is an ongoing commitment.

#### Update Strategy

- **MUST** keep dependencies updated — outdated dependencies accumulate security vulnerabilities and compatibility issues
- **SHOULD** adopt a tiered update strategy:

  | Update Type | Approach | Rationale |
  |---|---|---|
  | **Security patches** | Apply as soon as possible (automated when feasible) | Security is non-negotiable |
  | **Patch versions** (x.x.PATCH) | Apply regularly, low risk | Bug fixes, minimal breaking change risk |
  | **Minor versions** (x.MINOR.x) | Review changelog, apply in batches | New features, low breaking change risk |
  | **Major versions** (MAJOR.x.x) | Evaluate carefully, plan migration, test thoroughly | Breaking changes expected |

- **SHOULD** use automated dependency update tools to stay on top of updates — manual tracking does not scale
- **MUST** run the full test suite after any dependency update before merging

#### Removal Discipline

- **SHOULD** periodically audit the dependency list for packages that are:
  - No longer used (dead dependencies — installed but not imported)
  - Replaceable by native platform features (the platform may have caught up since the dependency was added)
  - Replaceable by a dependency already in the project
  - Unmaintained or abandoned (no updates in 12+ months for active ecosystems)
- **SHOULD** treat dependency removal as a positive contribution — fewer dependencies means a smaller attack surface, faster installs, and less maintenance

#### Lock Files

- **MUST** commit lock files to version control — they ensure reproducible builds across all environments
- **MUST** use deterministic install commands in CI/CD — the install command must respect the lock file exactly, never modifying it
- **MUST** review lock file changes in pull requests — unexpected changes may indicate supply chain issues

> → See [07-security-standards.md, Section 11] for detailed supply chain security, vulnerability scanning, and attack prevention guidance.

---

### 10.5 The "Build vs Buy" Decision

When the decision is not trivial (the functionality is significant and a dependency exists), use this framework:

#### Favor Building When

- The functionality is core to your competitive advantage or business differentiator
- The scope is small and well-defined (< 200 lines of straightforward code)
- The available packages are poorly maintained, bloated, or do not quite fit your needs
- You need deep control over the behavior and cannot afford to depend on external release cycles
- The functionality touches sensitive areas (security, encryption, auth) where you need full understanding and auditability

#### Favor Buying (Using a Dependency) When

- The problem is well-solved by a mature, widely-used library (do not reinvent the wheel for cryptography, date handling, PDF generation, etc.)
- Building it yourself would take significant effort and ongoing maintenance
- The dependency is actively maintained by a reputable team or organization
- The dependency is a de facto standard in the ecosystem
- The problem domain is complex and error-prone (e.g., timezone handling, email parsing, image processing)

#### Rules

- **MUST NOT** build custom implementations for:
  - Cryptography and hashing — always use established, audited libraries
  - Authentication protocols (OAuth, JWT verification) — too error-prone to implement from scratch
  - Complex data formats (PDF, Excel, image processing) — use battle-tested libraries
- **SHOULD** build custom implementations for:
  - Simple utilities specific to your domain
  - Thin wrappers that adapt a dependency to your application's interface (→ See [Section 4.5 — DIP](#45-dependency-inversion-principle-dip))
  - Business logic that is unique to your application

> **Rule of thumb:** use dependencies for the **infrastructure** of your application (how it works), and write custom code for the **domain** of your application (what it does).

---

## 11. Definition of Done (Universal)

"Done" is not "it works on my machine." Done means the feature is complete, verified, documented, and ready for production — with confidence. A shared Definition of Done eliminates ambiguity, prevents shortcuts, and establishes a quality baseline that every feature must meet before it can be considered shippable.

---

### 11.1 Why a Definition of Done Matters

Without a shared DoD:
- "Done" means different things to different developers — one considers it done after the happy path works, another after tests pass, another after documentation is updated
- Quality becomes inconsistent — some features ship polished, others ship with known gaps
- Code review becomes subjective — reviewers do not have a clear standard to review against
- Technical debt accumulates silently — shortcuts taken under "it's done, just needs polish" never get polished

With a shared DoD:
- Every feature meets the same quality bar
- Code reviews have a concrete checklist to verify against
- The team can confidently say "this is ready for production"
- Gaps are visible and intentional, not accidental

---

### 11.2 Universal Definition of Done

A feature is **done** when ALL of the following are true. These criteria apply to every feature, in every project, regardless of technology stack.

#### Code Quality

- [ ] Code follows the principles in this document (clean code, SOLID, naming, separation of concerns)
- [ ] No compiler/linter errors or warnings — the CI pipeline passes cleanly
- [ ] No `any` types, unsafe casts, or suppressed warnings without documented justification
- [ ] Functions are small, focused, and well-named
- [ ] No dead code, commented-out code, or orphaned files introduced

#### Input Validation & Error Handling

- [ ] All inputs from untrusted sources are validated at the system boundary (API, form, external data)
- [ ] Error handling is explicit — no silent failures, no swallowed exceptions
- [ ] Errors return structured, predictable responses (no stack traces or internal details exposed to users)
- [ ] Custom error types are used where appropriate (not generic `Error` or `Exception`)
- [ ] Edge cases are identified and handled (empty states, null values, boundary conditions)

#### Business Logic Integrity

- [ ] Business logic resides in the service layer — not in UI components, not in data access code
- [ ] The feature correctly implements the specified requirements
- [ ] Layering rules are respected — no upward dependencies, no circular dependencies

#### Testing

- [ ] Critical paths have automated tests (at minimum, unit tests for business logic)
- [ ] Tests follow Arrange–Act–Assert pattern and are readable
- [ ] Tests cover both the happy path and key failure scenarios
- [ ] All tests pass in CI

#### Security

- [ ] No secrets or credentials hardcoded in the code
- [ ] Authentication and authorization are enforced for protected operations
- [ ] Input validation prevents injection and malformed data
- [ ] Sensitive data is not exposed in logs, error messages, or client responses
- [ ] No new security warnings introduced by dependency changes

#### Documentation

- [ ] Public functions and services have docstrings (what, params, returns, throws)
- [ ] README updated if setup steps, environment variables, or project structure changed
- [ ] ADR created if a significant architectural decision was made
- [ ] Non-obvious decisions have inline comments explaining **why**
- [ ] TODOs include a ticket/issue reference

#### Code Review

- [ ] Code has been reviewed (even in solo projects — a self-review on the PR diff catches surprising issues)
- [ ] PR description explains **what** changed and **why**
- [ ] Review feedback has been addressed or explicitly discussed

---

### 11.3 Domain-Specific Extensions

The universal DoD above is the **minimum baseline**. Each domain adds its own criteria on top:

| Domain | Additional Criteria | Reference |
|---|---|---|
| **Frontend / UI** | Responsive/mobile verified, accessibility checked, loading/error/empty states handled, touch targets adequate | → See [05-frontend-standards.md] |
| **API** | Request/response validation in place, error envelope consistent, pagination capped, rate limiting configured | → See [03-api-design.md] |
| **Database** | Migration created, RLS policies in place (if applicable), indexes reviewed, naming conventions followed | → See [04-database-standards.md] |
| **Security-sensitive features** | STRIDE assessment completed, threat mitigations documented, security headers verified | → See [07-security-standards.md] |
| **Infrastructure / Deployment** | Environment variables configured, deployment pipeline tested, rollback plan identified | → See [09-devops-cicd.md] |

- **MUST** apply the universal DoD to every feature
- **MUST** apply the relevant domain-specific extensions based on what the feature touches
- **SHOULD** include the applicable DoD checklist in PR templates so it is visible during code review

---

### 11.4 Using the DoD in Practice

#### In Pull Requests

- **SHOULD** embed the DoD as a checklist in the PR template (`.github/pull_request_template.md` or equivalent) — reviewers and authors check off items as they verify:

  ```markdown
  ## Definition of Done

  ### Universal
  - [ ] Code quality: clean, no warnings, well-named
  - [ ] Validation: inputs validated, errors handled
  - [ ] Logic: business rules in services, layering respected
  - [ ] Tests: critical paths covered, CI green
  - [ ] Security: no secrets, auth enforced, data protected
  - [ ] Docs: docstrings, README, ADR if needed

  ### Domain (check applicable)
  - [ ] Frontend: responsive, a11y, states handled
  - [ ] API: validation, error envelope, rate limits
  - [ ] Database: migration, RLS, indexes
  ```

#### In Code Review

- **SHOULD** use the DoD as the primary review framework — a reviewer's job is not to find stylistic preferences, but to verify that the DoD is met
- **MUST** block merge if any MUST-level DoD item is not satisfied
- **SHOULD** flag missing SHOULD-level items as review comments with a request for justification

#### Handling Incomplete Items

- **MUST NOT** merge features that violate MUST-level criteria — no exceptions, no "we'll fix it later"
- **SHOULD** document any intentionally skipped SHOULD-level criteria in the PR description with justification
- If a feature genuinely cannot meet a criterion (e.g., tests cannot cover a third-party integration), **MUST** document the gap and create a follow-up ticket

---

### 11.5 DoD Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| **"It works, ship it"** | Skipping validation, tests, documentation, and review because the happy path works | Apply the full DoD — "works" is the minimum, not the goal |
| **DoD as decoration** | The checklist exists in the PR template but nobody actually verifies the items | Make DoD verification an explicit step in the review process — reviewers must check, not just glance |
| **Negotiating down the DoD** | "We're in a hurry, let's skip tests this time" becomes the norm | The DoD is the quality floor, not a negotiable target. If time pressure is real, reduce scope — not quality |
| **One-size-fits-all** | Applying the same heavyweight DoD to a typo fix and a payment integration | Scale the effort, not the standard. A typo fix satisfies most items trivially — the DoD is still met, it just takes 30 seconds to verify instead of 30 minutes |
| **Stale DoD** | The DoD was written once and never updated as the project evolved | Review and update the DoD periodically — at minimum when new domain standards are added or when gaps are identified |

---

## 12. Non-Goals / Avoid Overengineering

The previous sections define what good engineering looks like. This section defines where to **stop**. Overengineering — building more than what is needed, more complex than what is justified, more abstract than what is understood — is one of the most common and most expensive mistakes in software development. It disguises itself as "good practice" while silently draining time, adding bugs, and making the system harder to understand.

> **The goal of engineering is not to build the most sophisticated system possible. It is to build the simplest system that solves the actual problem reliably, securely, and maintainably.**

---

### 12.1 Explicit Non-Goals

The following are **not goals** of any project unless a measured, documented need proves otherwise:

| Non-Goal | Why It Is a Non-Goal | When It Becomes a Goal |
|---|---|---|
| **Microservices architecture** | Adds enormous operational complexity (deployment, networking, observability, data consistency). A well-structured monolith serves most projects far better. | When independent teams need independent deployment cycles, or when specific components have fundamentally different scaling requirements — proven by data, not intuition |
| **Custom framework inside the app** | Frameworks within frameworks obscure behavior, create learning curves, and rarely justify their cost | Almost never — if you need a framework, use an established one |
| **Generic, reusable solutions for single-use problems** | Building for reuse when there is only one use case adds complexity without benefit (→ YAGNI) | When the pattern has been proven across 3+ concrete use cases |
| **Complex caching layers (Redis, Memcached)** | Caching adds invalidation complexity, consistency bugs, and operational overhead | When database query performance is a measured bottleneck that cannot be solved with indexing, query optimization, or read replicas |
| **Message queues and event-driven architecture** | Adds operational complexity, eventual consistency challenges, and debugging difficulty | When you have operations that exceed request timeouts, need retry semantics, or require decoupled processing at proven scale |
| **Background job systems** | Adds infrastructure, monitoring, and failure handling complexity | When specific tasks demonstrably cannot complete within a request/response cycle |
| **CQRS / Event Sourcing** | Dramatically increases system complexity and cognitive load | When read and write patterns have fundamentally different scaling needs — proven by measurement, not theory |
| **GraphQL** | Adds query complexity, security considerations (depth limiting, cost analysis), and tooling overhead | When multiple clients with significantly different data needs consume the same API, and REST causes substantial over/under-fetching — measured, not assumed |
| **Kubernetes** | Enormous operational complexity that is itself a security and reliability risk | When the project genuinely requires the orchestration capabilities (auto-scaling, multi-region, complex networking) that simpler platforms cannot provide |
| **Multi-region deployment** | Adds data replication, consistency, and latency complexity | When users in multiple geographic regions experience measurable latency issues |

- **MUST NOT** adopt any of the above without an ADR that documents the measured need, the alternatives considered, and the accepted operational cost
- **MUST** start simple and add complexity only when the simple approach has been proven insufficient

---

### 12.2 The Complexity Budget

Think of every project as having a **complexity budget** — a finite amount of complexity the team can effectively manage. Every architectural choice, every abstraction, every dependency, and every tool spends from this budget.

#### Rules

- **MUST** treat complexity as a cost, not a feature — every layer of abstraction, every configuration option, every generic solution consumes budget that could be spent on delivering value
- **SHOULD** allocate complexity budget to where it provides the most value:

  | Worth the Complexity | Rarely Worth the Complexity |
  |---|---|
  | Input validation and error handling | Generic plugin systems for 2 integrations |
  | Security controls (auth, RLS, encryption) | Event bus for 3 event types |
  | Clean separation of concerns | Microservices for a team of 2 |
  | Automated testing of critical paths | 100% test coverage on utility functions |
  | Structured logging and error monitoring | Custom observability infrastructure |
  | Type safety and schema validation | Abstract factory pattern for one implementation |

- **SHOULD** regularly ask: **"Is this complexity paying for itself?"** If a pattern, abstraction, or tool is consuming more time in maintenance and cognitive load than it saves, it should be simplified or removed

#### The Simplicity Audit

Periodically (e.g., every quarter or after a major release), review the codebase for unnecessary complexity:

- Are there abstractions that only have one implementation and no realistic prospect of a second?
- Are there configuration options that nobody has ever changed from the default?
- Are there "generic" solutions that serve exactly one use case?
- Are there dependencies that could be replaced with 20 lines of code?
- Are there architectural patterns that were added "for the future" but the future never arrived?

If the answer to any of these is yes, consider simplifying. Removing unnecessary complexity is as valuable as adding necessary functionality.

---

### 12.3 Scaling Triggers

The non-goals in Section 12.1 become legitimate goals when specific, measurable conditions are met. These are the triggers — the signals that the simple approach has reached its limits and additional complexity is justified.

#### Rules

- **MUST** measure before scaling — intuition about performance bottlenecks is wrong more often than it is right
- **MUST** document the trigger and the decision in an ADR before introducing the added complexity
- **SHOULD** try the simpler optimization first — indexing before caching, query optimization before read replicas, code splitting before microservices

#### Trigger Reference

| Trigger Signal | Simple Solution First | Complex Solution (If Simple Fails) |
|---|---|---|
| Slow database queries | Add indexes, optimize queries, select fewer columns | Read replicas, caching layer, materialized views |
| Request timeouts on long operations | Optimize the operation, increase timeout if safe | Background job queue, async processing |
| High server load under traffic spikes | Vertical scaling (bigger instance), CDN for static assets, caching headers | Horizontal scaling, load balancer, auto-scaling |
| Multiple teams stepping on each other in the same codebase | Feature modules with clear boundaries, code ownership rules | Service extraction (only for the contested boundary) |
| Client bundle too large | Code splitting, lazy loading, tree shaking, dependency audit | Micro-frontends (extreme cases only) |
| Need to process events from multiple sources | Direct API calls, webhook handlers | Message queue, event bus |
| Read and write loads have fundamentally different patterns | Optimize queries, add read replicas | CQRS (only when proven necessary) |

---

### 12.4 Signs of Overengineering

Learn to recognize overengineering in progress — catching it early saves enormous amounts of wasted effort.

| Sign | What It Looks Like | What to Do |
|---|---|---|
| **Speculative generality** | Building abstractions for requirements that do not exist yet — "we might need this later" | Remove the abstraction, build a seam instead (→ Section 5.3) |
| **Resume-driven development** | Choosing technologies because they look good on a CV, not because they solve the project's problems | Evaluate technology against project needs, not career goals — document in ADR |
| **Architecture astronautics** | Spending more time designing the architecture than building the features — the system diagram has 15 boxes but zero users | Ship the simplest version, iterate based on real feedback |
| **Premature abstraction** | Creating interfaces, factories, and patterns before the second use case exists | Follow the Rule of Three (→ Section 5.1) — abstract after the pattern is proven |
| **Configuration over convention** | Making everything configurable instead of picking sensible defaults | Choose defaults that work for 90% of cases; make only proven variation points configurable |
| **Gold plating** | Adding polish, features, or optimizations that nobody asked for and nobody will notice | Focus on the requirements — deliver what was asked, then ask what is next |
| **Complexity pride** | Feeling that a simple solution is "not engineering enough" — adding layers to feel productive | Simplicity is the ultimate sophistication. If it works, is tested, and is maintainable — it is enough |

---

### 12.5 The Right Mindset

- **Start simple.** Build the minimum that works correctly, securely, and maintainably.
- **Keep seams clean.** Design boundaries that allow future extension without requiring today's implementation.
- **Measure before acting.** Do not optimize, scale, or abstract without evidence that it is needed.
- **Add complexity reluctantly.** Every new layer, tool, or pattern must earn its place by solving a proven problem.
- **Remove complexity eagerly.** Deleting unnecessary code, abstractions, and dependencies is a positive contribution — celebrate it.
- **Document the decisions.** When complexity is added, the ADR ensures that future developers understand why — and can revisit the decision when conditions change.

> _"Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away."_
> — Antoine de Saint-Exupéry

---

## 13. Refactoring Guidelines

Refactoring is the disciplined act of improving the internal structure of existing code without changing its external behavior. It is how the principles in this document are applied retroactively — transforming code that works but is hard to understand, hard to change, or hard to extend into code that embodies clean code (§3), SOLID (§4), and proper separation of concerns (§6).

Refactoring is not rewriting. It is not a project. It is a daily practice — small, safe, continuous improvements that prevent technical debt from compounding.

> → See [11-project-management.md] for refactoring planning, stakeholder justification, migration strategies (Strangler Fig, Branch by Abstraction), and large-scale refactor management.

---

### 13.1 When to Refactor

Refactoring is not an end in itself — it serves a purpose. Refactor when the current state of the code is actively impeding progress, reliability, or comprehension.

#### Clear Signals That Refactoring Is Needed

| Signal | What It Looks Like | Relevant Principle |
|---|---|---|
| **Adding a feature requires modifying many unrelated files** | Shotgun surgery — a single change touches 5+ files across multiple layers | Separation of Concerns (§6), SRP (§4.1) |
| **Developers are afraid to change the code** | "Don't touch that, it might break something" — fear-driven development | Missing tests, high coupling (§6.3) |
| **The same bug keeps recurring in variations** | A fix in one place does not prevent the same class of bug elsewhere | Duplication of knowledge, DRY (§5.1) |
| **New team members cannot understand a module without help** | Onboarding requires oral tradition instead of reading the code | Readability (§2.6), Naming (§7), Comments (§3.5) |
| **Functions or files have grown beyond reasonable size** | 500+ line files, 50+ line functions, God classes | SRP (§4.1), Small Composable Units (§2.7) |
| **Duplicated logic has crossed the Rule of Three** | The same knowledge exists in 3+ places and has already diverged | DRY — Rule of Three (§5.1) |
| **Business logic is scattered across layers** | Validation in the UI, calculations in the repository, rules in the API handler | Layering (§6.2) |
| **Tests are hard to write or excessively complex** | Testing a function requires mocking 10 dependencies or setting up complex state | High coupling, SRP violation, DIP (§4.5) |
| **Magic numbers, magic strings, or stringly-typed patterns are widespread** | Behavior depends on raw strings or unexplained numeric values | Explicit Over Implicit (§2.2), Anti-Patterns (§3.7) |
| **The code has accumulated TODO/FIXME/HACK markers** | Technical debt is documented but never addressed | Documentation (§8.6) |

#### Rules

- **SHOULD** refactor when any of the signals above are actively slowing development, causing bugs, or increasing cognitive load
- **SHOULD** prefer refactoring as part of feature work — "I need to add feature X, and the code in this area is messy, so I will clean it up as part of the same PR"
- **MUST NOT** refactor without a clear purpose — "this code is ugly" is not sufficient justification. The question is always: **"What concrete problem will this refactoring solve?"**

---

### 13.2 When NOT to Refactor

Refactoring has a cost — time, risk, and cognitive effort. Sometimes the cost outweighs the benefit.

#### Do NOT Refactor When

| Condition | Why Not | What to Do Instead |
|---|---|---|
| **The code works and is not in your path** | Refactoring code you are not actively working on introduces risk without immediate benefit | Leave it alone; apply the Boy Scout Rule only to code you are already touching (§13.4) |
| **There are no tests covering the area** | Without tests, you have no safety net — you cannot verify that the refactoring preserved behavior | Write tests first, then refactor. If writing tests is not feasible, do not refactor |
| **The change is purely cosmetic** | Renaming variables for style preference, reorganizing imports, reformatting — with no measurable improvement in clarity or maintainability | Let the linter/formatter handle cosmetic concerns automatically |
| **A critical deadline is imminent** | Refactoring under time pressure increases the risk of introducing bugs and missing the deadline | Document the debt (TODO with ticket), ship, and plan the refactor for after the deadline |
| **You are refactoring to learn, not to improve** | Exploring a codebase by rewriting it is learning, not refactoring — it introduces risk to production code | Use a branch or a throwaway copy to explore; do not merge experimental refactors |
| **The code is scheduled for replacement** | If a module will be replaced or deprecated in the near term, improving its internals is wasted effort | Focus effort on the replacement instead |

#### Rules

- **MUST NOT** refactor production code without test coverage — tests are the safety net that makes refactoring safe. No tests = no refactoring
- **MUST NOT** refactor as a procrastination strategy — refactoring should serve the current work, not delay it
- **SHOULD NOT** pursue large-scale refactoring without planning — → See [11-project-management.md] for how to scope and manage large refactors

---

### 13.3 Fundamental Techniques

These are the core refactoring moves that address the most common structural problems. Each is small, safe, and reversible.

#### Extract Function

**Problem:** A function does too much — it has multiple responsibilities, or a section of logic is reused or hard to name within the larger function.

**Technique:** Pull the section into a new, well-named function.
```
// BEFORE — one function doing too much
function processOrder(order) {
  // Validate (15 lines)
  if (!order.items || order.items.length === 0) { ... }
  if (!order.customerId) { ... }
  // ... more validation

  // Calculate total (10 lines)
  let total = 0;
  for (const item of order.items) { ... }
  // ... tax, discounts

  // Persist (5 lines)
  await db.orders.insert({ ...order, total });
}

// AFTER — each responsibility in its own function
function processOrder(order) {
  validateOrder(order);
  const total = calculateOrderTotal(order.items);
  await orderRepository.create({ ...order, total });
}
```

**When NOT to:** Do not extract a function that is only 2–3 lines and is only used once — the indirection adds more cost than the clarity it provides.

#### Rename for Clarity

**Problem:** A variable, function, or file name is vague, misleading, or does not reflect its current purpose.

**Technique:** Rename it to reveal intent. Use the IDE's rename refactoring to update all references safely.
```
// BEFORE
const d = getResults();
function handle(x) { ... }

// AFTER
const searchResults = fetchActiveListings();
function applyDiscountToOrder(order) { ... }
```

**When NOT to:** Be cautious renaming public API surfaces (exported functions, API endpoints, database columns) — these may have external consumers. Renaming internals is always safe with IDE support.

#### Move to Correct Layer

**Problem:** Logic is in the wrong architectural layer — a UI component contains business rules, a repository contains validation, an API handler contains data transformation.

**Technique:** Move the logic to the appropriate layer as defined in §6.2 (Layering Rules).
```
// BEFORE — business rule in the API handler
app.post("/orders", async (req, res) => {
  const discount = req.body.isVIP ? 0.2 : 0;  // ← business logic in handler
  const total = calculateTotal(req.body.items, discount);
  await db.orders.insert({ ...req.body, total });
  res.json({ total });
});

// AFTER — business rule in the service layer
app.post("/orders", async (req, res) => {
  const input = createOrderSchema.parse(req.body);
  const result = await orderService.createOrder(input);
  res.json(result);
});

// Service — owns the business rule
function createOrder(input) {
  const discount = calculateCustomerDiscount(input.customerId);
  const total = calculateTotal(input.items, discount);
  return orderRepository.create({ ...input, total, discount });
}
```

**When NOT to:** If the "wrong layer" code is trivial (a single line of formatting in a component) and moving it adds complexity without benefit, leave it and add a comment explaining the trade-off.

#### Simplify Conditional Logic

**Problem:** Complex, deeply nested, or duplicated conditional logic that is hard to follow.

**Techniques:**
- Extract boolean expressions into named variables or functions (→ §3.3)
- Use guard clauses to flatten nested conditions (→ §3.2)
- Replace conditional chains with lookup tables or strategy patterns (→ §4.2)
```
// BEFORE — deeply nested, hard to follow
function getShippingCost(order) {
  if (order.country === "PT") {
    if (order.total > 50) {
      return 0;
    } else {
      if (order.isExpress) {
        return 8;
      } else {
        return 4;
      }
    }
  } else {
    if (order.country === "ES") {
      return order.isExpress ? 12 : 7;
    } else {
      return order.isExpress ? 20 : 15;
    }
  }
}

// AFTER — guard clauses + lookup
const SHIPPING_RATES = {
  PT: { standard: 4, express: 8, freeThreshold: 50 },
  ES: { standard: 7, express: 12, freeThreshold: null },
  DEFAULT: { standard: 15, express: 20, freeThreshold: null },
};

function getShippingCost(order) {
  const rates = SHIPPING_RATES[order.country] ?? SHIPPING_RATES.DEFAULT;

  const hasFreeShipping = rates.freeThreshold && order.total > rates.freeThreshold;
  if (hasFreeShipping) return 0;

  return order.isExpress ? rates.express : rates.standard;
}
```

**When NOT to:** If the conditional has 2–3 simple branches and is easy to read as-is, do not over-abstract it into a lookup table or strategy — that would violate KISS (§5.2).

#### Replace Magic Values with Named Constants

**Problem:** Raw numbers or strings scattered across the code with no explanation of what they represent.

**Technique:** Extract into well-named constants or enums (→ §2.2 Explicit Over Implicit).
```
// BEFORE
if (attempts > 3) { ... }
if (user.role === "adm") { ... }
setTimeout(fn, 86400000);

// AFTER
const MAX_LOGIN_ATTEMPTS = 3;
if (attempts > MAX_LOGIN_ATTEMPTS) { ... }

if (user.role === UserRole.ADMIN) { ... }

const ONE_DAY_MS = 24 * 60 * 60 * 1000;
setTimeout(fn, ONE_DAY_MS);
```

**When NOT to:** Values that are self-evident in context (e.g., `0`, `1`, empty string as initial values) do not need extraction.

#### Introduce Parameter Object

**Problem:** A function has accumulated many parameters, making it hard to call correctly and easy to mix up argument order.

**Technique:** Group related parameters into a well-named object (→ §3.1 Function Design).
```
// BEFORE — 6 parameters, easy to mix up
function createInvoice(customerId, items, dueDate, currency, taxRate, notes) { ... }

// AFTER — grouped into a self-documenting object
function createInvoice(params: CreateInvoiceParams) { ... }

// Call site reads clearly
createInvoice({
  customerId: "abc-123",
  items: lineItems,
  dueDate: nextMonth,
  currency: "EUR",
  taxRate: 0.23,
  notes: "Net 30",
});
```

**When NOT to:** Functions with 1–3 clear, distinct parameters usually do not benefit from a parameter object — the direct form is simpler.

#### Remove Dead Code

**Problem:** Code that is never executed — unused functions, unreachable branches, commented-out blocks, unused imports.

**Technique:** Delete it. Version control remembers everything.

- **MUST** remove dead code rather than commenting it out — commented-out code creates noise and confusion
- **SHOULD** use IDE and linter tools to identify unused exports, unreachable code, and unused variables
- **SHOULD** verify with search-across-project before deleting exports that might be used elsewhere

**When NOT to:** Code behind a feature flag that is intentionally disabled is not dead code — it is dormant. Ensure the flag and the code have a documented lifecycle.

---

### 13.4 The Boy Scout Rule

> _"Always leave the code better than you found it."_

Refactoring is most effective when it happens continuously, in small increments, as part of daily work — not as a separate "refactoring sprint" that never gets prioritized.

#### Rules

- **SHOULD** apply the Boy Scout Rule to every file you touch: if you open a file to fix a bug or add a feature, leave that file slightly cleaner than you found it
- **SHOULD** keep Boy Scout improvements small and safe — rename a variable, extract a function, remove dead code, fix a type annotation. Not a full rewrite
- **SHOULD** include Boy Scout improvements in the same commit or PR as the feature work — they are part of the change, not separate cleanup
- **MUST NOT** use the Boy Scout Rule as justification for large, unreviewed changes — if a Boy Scout improvement grows beyond a few minutes of work, it becomes a refactoring task that should be scoped and reviewed separately

#### Examples of Good Boy Scout Improvements

- Renaming a vague variable you encountered while debugging
- Adding a missing return type to a function you just called
- Extracting a magic number into a named constant in code you are modifying
- Removing an unused import or dead function in a file you are editing
- Adding a brief "why" comment to a non-obvious line you just spent time understanding
- Fixing a linter warning in the file you are already changing

#### Examples of Bad Boy Scout Scope Creep

- Rewriting an entire module because you noticed it was messy while fixing a one-line bug
- Changing the naming convention of 50 variables across 20 files because you touched one of those files
- Refactoring a function's internals when you only needed to change how it was called

---

### 13.5 Refactor vs Rewrite

The temptation to "throw it all away and start fresh" is strong when working with messy code. It is almost always the wrong decision.

#### Why Rewrites Are Dangerous

- **The existing code embeds knowledge** — bug fixes, edge case handling, and business rules that were discovered over months or years. A rewrite starts at zero and must rediscover all of them
- **The Second System Effect** — the rewrite tends to over-engineer, adding "all the things we wish we had" instead of solving the actual problems
- **Rewrites take longer than expected** — always. Meanwhile, the old system still needs maintenance, and the team is split between two codebases
- **Users do not care about internals** — a rewrite delivers zero user value until it fully replaces the old system. Incremental refactoring delivers improvements continuously

#### When to Refactor (Almost Always)

- The code is functional but poorly structured
- The problems are localizable — specific modules, specific patterns
- Tests exist (or can be written) to verify behavior preservation
- The team can improve the code incrementally while continuing to deliver features

#### When to Rewrite (Rare, Requires ADR)

- The technology stack is fundamentally obsolete (e.g., framework is EOL, language version is unsupported, security patches are unavailable)
- The architecture cannot support a critical, validated requirement that refactoring cannot address (not "might need someday" — validated and urgent)
- The cost of continued maintenance exceeds the cost of a rewrite — **measured**, not assumed
- The existing codebase has no tests, no documentation, and no one who understands it — and the system is small enough that a rewrite is genuinely faster

#### Rules

- **MUST** create an ADR before starting any rewrite — documenting the specific, measured reasons why refactoring is insufficient
- **MUST** define a clear scope for a rewrite — never rewrite "everything." Identify the specific module or boundary to replace
- **SHOULD** prefer the Strangler Fig pattern (→ See [11-project-management.md]) — incrementally replacing parts of the old system while both coexist, rather than a big-bang cutover
- **MUST NOT** rewrite based on aesthetic preferences — "I don't like how this was written" is a reason to refactor, not to rewrite

---

### 13.6 Prerequisites for Safe Refactoring

Refactoring without a safety net is not refactoring — it is gambling. These prerequisites ensure that refactoring improves the code without introducing regressions.

#### Test Coverage

- **MUST** have automated tests covering the behavior of the code being refactored — at minimum, tests that verify the inputs and outputs of the functions being changed
- **SHOULD** write characterization tests before refactoring untested code — tests that capture the current behavior (even if imperfect) so that changes can be verified:
```
  // Characterization test: captures current behavior as a baseline
  // This is not asserting correctness — it is asserting "same as before"
  test("calculateTotal matches current behavior", () => {
    const result = calculateTotal(sampleItems, "PT");
    expect(result).toBe(4920); // Current output — verify this doesn't change
  });
```

- If writing tests is not feasible (e.g., deeply coupled legacy code), **MUST NOT** proceed with the refactoring until the code can be made testable — this may require a minimal, focused refactoring just to enable testing (extract function, inject dependency)

#### Version Control Discipline

- **MUST** make small, frequent commits during refactoring — each commit should represent one logical refactoring step that leaves the code in a working state
- **MUST** keep refactoring commits separate from feature or bug fix commits — this makes it easy to revert a refactoring step without losing feature work
- **SHOULD** use a PR with a clear description of what was refactored and why — even for Boy Scout improvements, the PR diff should be reviewable

#### Measure Before and After

- **SHOULD** capture relevant metrics before starting a non-trivial refactoring:
  - Test pass rate and coverage in the affected area
  - Cyclomatic complexity or cognitive complexity of the affected functions
  - Build time or test execution time (if relevant)
  - Number of lint warnings in the affected files
- **SHOULD** verify that metrics improved (or at least did not regress) after the refactoring is complete
- **SHOULD** document the improvement in the PR description — this builds confidence in refactoring as a practice and provides evidence of value

> → See [06-testing-strategy.md] for guidance on test types and when to use each.
> → See [10-git-workflow.md] for commit and PR conventions during refactoring.
> → See [11-project-management.md] for planning and managing large-scale refactoring efforts.
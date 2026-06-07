# 🧪 Testing Strategy

> **Scope:** Cross-cutting testing strategy, governance, and shared configuration
> applicable to all projects covered by these engineering standards.
>
> **Purpose:** The testing "constitution" — defines the test pyramid, when to use
> each test type, how test types complement each other, coverage targets, CI quality
> gates, test data management, mocking philosophy, and shared tooling configuration.
> This is the document that answers "what should I test, when, and why?" — ensuring
> every project has a deliberate, consistent, and maintainable testing strategy.
>
> **Keywords:**
> - **MUST** = required (PR should be blocked if violated)
> - **SHOULD** = strongly recommended (requires justification to skip)
> - **MAY** = optional (case-by-case)

---

## 0. How to Use This Document

- This document defines the **testing strategy** — the test pyramid, when to use
  each test type, coverage governance, CI quality gates, test data management,
  mocking philosophy, and shared configuration for the test runner (Vitest) and
  E2E framework (Playwright).
- It does **not** define domain-specific testing patterns — how to test an API
  endpoint, how to test a database query, or how to test a React component. Those
  patterns live in the domain documents and are referenced throughout this document.
- It does **not** define which testing tools to use — that decision lives in
  → See [02-technology-radar.md, Section 4.11 — Testing]. This document assumes the
  tools have been chosen and focuses on **how to use them strategically**.
- This document is a **pillar**, not a domain document. In the document hierarchy
  (→ See [00-INDEX.md]), it sits alongside [01-core-principles.md],
  [02-technology-radar.md], and [07-security-standards.md] — cross-cutting
  documents that inform all domain standards. Domain documents (03, 04, 05) derive
  their testing sections from the strategy defined here.

### Quick Navigation

| I need to... | Go to |
|---|---|
| Understand **why** we test and what makes a good test | § 1 — Testing Philosophy |
| Decide **what type of test** to write for this code | § 2.7 — Decision Guide |
| Set up **Vitest** configuration for a project | § 3.1 — Vitest Configuration |
| Set up **Playwright** configuration for a project | § 5.1 — Playwright Configuration |
| Create **test data** without duplication | § 6 — Test Data Management |
| Decide **when to mock** and when to use the real thing | § 7.1 — The Golden Rule |
| Configure **CI quality gates** | § 8 — CI/CD Integration |
| Set **coverage targets** for my project | § 9.1 — Recommended Targets |
| Verify before **merging a PR** | § 14.1 — Pre-Merge Checklist |
| Verify before **releasing to production** | § 14.2 — Pre-Release Checklist |

### Why This Distinction Matters

The domain documents already contain substantial testing content:

- **[03-api-design.md, § 13]** — 650+ lines on API testing: Arrange-Act-Assert
  with Supertest, Express + Next.js Route Handler setup, testing checklists per
  endpoint, API test factories, and anti-patterns.
- **[04-database-standards.md, § 13]** — 600+ lines on database testing: Supabase
  local setup, RLS policy testing, constraint testing, migration testing, soft
  delete testing, database test factories, and anti-patterns.
- **[05-frontend-standards.md, § 15]** — 500+ lines on frontend testing: component
  tests with Vitest + Testing Library, hook testing with `renderHook`, Playwright
  E2E patterns, visual regression awareness, axe-core accessibility testing, and
  anti-patterns.
- **[07-security-standards.md, § 13]** — security testing: SAST, DAST, SCA
  scanning, dependency vulnerability management, and the security testing pipeline.

If this document duplicated those patterns, it would create a maintenance nightmare
— two sources of truth that inevitably diverge. Instead, the boundary is sharp:

```text
This document (06)                     Domain documents (03, 04, 05, 07)
─────────────────────                  ──────────────────────────────────
STRATEGY — what to test and when       PATTERNS — how to test in that domain
GOVERNANCE — coverage, CI gates        SPECIFICS — setup, utilities, examples
PRINCIPLES — what makes a good test    RECIPES — copy-paste-ready test code
CONFIGURATION — shared Vitest/PW       CUSTOMIZATION — domain-specific config
CROSS-CUTTING — factories, mocking     DOMAIN-SPECIFIC — entity factories, mocks
```

### Boundary Definitions

Understanding where this document ends and others begin is critical to avoiding
duplication and contradictions:

| Question | This Document (06) | Other Document |
|----------|--------------------|----------------|
| **Which** test runner to use? | — | → See [02-technology-radar.md] says "Vitest (Adopt)" |
| **How** to configure Vitest for all projects? | ✅ Section 3.3 | — |
| **Which** E2E framework to use? | — | → See [02-technology-radar.md] says "Playwright (Adopt)" |
| **How** to configure Playwright for all projects? | ✅ Section 5.3 | — |
| **When** to write a unit test vs integration vs E2E? | ✅ Section 2 | — |
| **How** to test an API endpoint with Supertest? | — | → See [03-api-design.md, § 13.3–13.4] |
| **How** to test RLS policies in Supabase? | — | → See [04-database-standards.md, § 13.4] |
| **How** to test a React component with Testing Library? | — | → See [05-frontend-standards.md, § 2] |
| **How** to test a custom hook with `renderHook`? | — | → See [05-frontend-standards.md, § 3] |
| **How** to write Playwright E2E tests for forms? | — | → See [05-frontend-standards.md, § 4] |
| **How** to run axe-core in component/E2E tests? | — | → See [05-frontend-standards.md, § 6] |
| **What** is the factory pattern and when to use it? | ✅ Section 6 | — |
| **How** to build an API request factory? | — | → See [03-api-design.md, § 13.6] |
| **How** to build a database record factory? | — | → See [04-database-standards.md, § 13.3] |
| **What** is the mocking strategy and philosophy? | ✅ Section 7 | — |
| **How** to mock API responses in frontend tests? | ✅ Section 7.3 (MSW setup) | → See [05-frontend-standards.md, § 15] (usage in component tests) |
| **What** coverage targets and CI gates to enforce? | ✅ Sections 8, 9 | — |
| **How** to configure GitHub Actions for the full pipeline? | ✅ Section 8.2 (baseline) | → See [09-devops-cicd.md] (complete CI/CD configuration) |
| **What** security tests to include? | ✅ Section 12 (strategy) | → See [07-security-standards.md, § 13] (SAST/DAST/SCA patterns) |
| **What** accessibility tests to include? | ✅ Section 10 (strategy) | → See [05-frontend-standards.md, § 9, § 6] (WCAG target, axe-core patterns) |
| **What** makes a good test? | ✅ Section 1 | — |
| **What** is the Definition of Done for tests? | — | → See [01-core-principles.md, § 11] (DoD includes "tests pass") |
| **How** to evaluate **non-deterministic** LLM / agent output (golden sets, LLM-as-judge, RAG & agent metrics)? | — | → See [12-ai-engineering.md, Ch. 5] — AI eval is the quality gate for AI features; it plugs into the CI gate (§ 8) |

### Where Domain-Specific Testing Patterns Live

When you need to **write a test** for a specific domain, go directly to the
domain document. This table maps every testing need to its authoritative source:

| I need to test... | Go to | Section |
|---|---|---|
| An API endpoint (happy path, validation, auth, errors) | [03-api-design.md] | § 13 — API Testing Patterns |
| Express route handler setup with Supertest | [03-api-design.md] | § 13.3 — Test Setup: Express |
| Next.js Route Handler testing setup | [03-api-design.md] | § 13.4 — Test Setup: Next.js |
| Testing checklist for each endpoint | [03-api-design.md] | § 13.5 — Testing Checklist per Endpoint |
| API test data factories and isolation | [03-api-design.md] | § 13.6 — Test Data & Isolation |
| RLS policies (user access, admin access, cross-tenant) | [04-database-standards.md] | § 13.4 — Testing RLS Policies |
| Database constraints (NOT NULL, UNIQUE, CHECK, FK) | [04-database-standards.md] | § 13.5 — Testing Constraints |
| Database migrations (apply, rollback, idempotency) | [04-database-standards.md] | § 13.6 — Testing Migrations |
| Soft delete behavior (filtering, cascading) | [04-database-standards.md] | § 13.7 — Testing Soft Delete |
| Database test factories and setup | [04-database-standards.md] | § 13.3 — Test Data Factories |
| React component rendering and interaction | [05-frontend-standards.md] | § 2 — Component Tests |
| Custom React hooks (`renderHook`) | [05-frontend-standards.md] | § 3 — Hook Testing |
| E2E flows with Playwright (forms, navigation) | [05-frontend-standards.md] | § 4 — E2E Patterns |
| Visual regression testing | [05-frontend-standards.md] | § 5 — Visual Regression |
| Accessibility testing with axe-core | [05-frontend-standards.md] | § 6 — Accessibility Testing |
| Security scanning (SAST, DAST, SCA) | [07-security-standards.md] | § 13 — Security Testing |
| Webhook integration testing | [03-api-design.md] | § 12.5 — Webhook Testing |

### Technology Versions

This document references the following tools and their current stable versions.
For the evaluation criteria, adoption rationale, and alternatives for each tool,
→ See [02-technology-radar.md, Section 4.11 — Testing].

| Tool | Version | Radar Status | Role in Strategy |
|---|---|---|---|
| **Vitest** | 4.x (4.1.1) | ✅ Adopt | Unit and integration test runner. Vite-native, ESM-first, Jest-compatible API. Shared configuration defined in § 3.3. |
| **Playwright** | 1.58.x | ✅ Adopt | E2E test framework. Cross-browser (Chromium, Firefox, WebKit), auto-waiting, trace viewer. Shared configuration defined in § 5.3. |
| **@testing-library/react** | 16.x | ✅ Adopt | Component testing utilities. User-centric queries (`getByRole`, `getByLabel`). Patterns in → See [05-frontend-standards.md, § 2]. |
| **Supertest** | 7.x | ✅ Adopt | HTTP assertion library for API integration tests. Patterns in → See [03-api-design.md, § 13.3]. |
| **@faker-js/faker** | 10.x (10.4.0) | ✅ Adopt | Realistic test data generation. Requires Node.js ≥ 20. Factory pattern defined in § 6. |
| **axe-core** | 4.11.x | ✅ Adopt | Automated accessibility testing (WCAG 2.x). Strategy in § 10, patterns in → See [05-frontend-standards.md, § 6]. |
| **MSW** | 2.x (2.12) | 🔬 Trial | API mocking at the network level for frontend tests. Setup and integration defined in § 7.3. |
| **Storybook** | 8.x | 🔬 Trial | Component isolation and visual testing. Awareness in → See [02-technology-radar.md]. |
| **k6** | — | 🔍 Assess | Load and performance testing. Awareness in § 11.4. |

> **Vitest 4.x migration note:** Vitest 4 introduces breaking changes from 3.x.
> The most significant for this strategy: `coverage.all` has been removed — Vitest 4
> only reports coverage for files that are actually imported during tests. You **MUST**
> define `coverage.include` explicitly to see all source files in the report. The V8
> coverage provider now uses AST-based analysis (replacing `v8-to-istanbul`),
> producing significantly more accurate reports. Browser Mode is now stable, enabling
> component tests to run in a real browser environment instead of JSDOM.
>
> **Playwright 1.58.x note:** Playwright 1.57+ runs on Chrome for Testing builds
> instead of Chromium. The 1.58.x line adds a Timeline view in the HTML report's
> Speedboard tab for analyzing test execution performance, improved search in UI Mode
> and Trace Viewer, and reorganized network details panels. The `page.accessibility()`
> API has been removed — use `@axe-core/playwright` instead.

### Document Relationships

```text
06-testing-strategy.md (this document)
 │
 │  DERIVES FROM (inherits principles)
 ├── → 01-core-principles.md
 │      Quality mindset (§ 1), Fail Fast (§ 2.3), Arrange-Act-Assert pattern,
 │      Definition of Done (§ 11), Boy Scout Rule for tests (§ 13.4)
 │
 ├── → 02-technology-radar.md
 │      Tool choices: Vitest (§ 4.11), Playwright (§ 4.11), Testing Library,
 │      Supertest, Faker.js, axe-core, MSW (Trial), k6 (Assess)
 │
 │  COMPLEMENTS (mutual reinforcement)
 ├── → 07-security-standards.md
 │      Security testing integrates with quality gates (§ 13),
 │      input validation testing, auth flow testing, dependency scanning
 │
 │  INFORMS (provides strategy for domain patterns)
 ├── → 03-api-design.md § 13
 │      API testing follows this pyramid and coverage targets;
 │      uses shared Vitest config and factory pattern from here
 │
 ├── → 04-database-standards.md § 13
 │      Database testing follows this isolation strategy and coverage targets;
 │      uses shared Vitest config and factory pattern from here
 │
 ├── → 05-frontend-standards.md § 15
 │      Frontend testing follows this pyramid and mocking strategy;
 │      uses shared Vitest/Playwright config from here
 │
 │  REFERENCED BY (other docs point here for governance)
 ├── → 09-devops-cicd.md
 │      CI pipeline implements the quality gates defined in § 8
 │
 └── → 01-core-principles.md § 13.6
       "Prerequisites for Safe Refactoring" references this document
       for test type guidance before refactoring
```

### Prerequisites

Before reading this document, you should be familiar with:

- → See [01-core-principles.md] — especially:
  - § 1.3 (Correctness Over Speed) — the philosophical foundation for why we test
  - § 1.6 (Feedback Loops Matter) — tests are the tightest feedback loop
  - § 2.3 (Fail Fast, Fail Loud) — the validation strategy that testing reinforces
  - § 3.1 (Function Design) — pure functions are the easiest code to test; this
    principle shapes the test pyramid
  - § 11 (Definition of Done) — "tests pass" is a DoD requirement, not a nice-to-have
  - § 13 (Refactoring Guidelines) — characterization tests, test coverage as a
    refactoring prerequisite
- → See [02-technology-radar.md, Section 4.11 — Testing] — the tooling choices and
  their rationale. Understanding **why** Vitest over Jest and **why** Playwright
  over Cypress helps contextualize the configuration decisions in this document.

### How This Document Is Organized

The document follows a natural progression from philosophy to practice:

| Section | Focus | Key question it answers |
|---|---|---|
| § 1 — Testing Philosophy | Why we test, what makes a good test | "Why should I bother writing tests?" |
| § 2 — Test Pyramid & Strategy | When to use each test type | "What type of test should I write for this code?" |
| § 3 — Unit Testing Standards | Fast, focused tests for isolated logic | "How do I set up and structure unit tests?" |
| § 4 — Integration Testing Standards | Tests that verify component interactions | "How do I test code that talks to a database or API?" |
| § 5 — E2E Testing Standards | Full user flow tests in a real browser | "How do I test that login-to-dashboard actually works?" |
| § 6 — Test Data Management | Factories, seeds, isolation | "How do I create test data without duplication?" |
| § 7 — Mocking & Test Doubles | When and how to mock | "When should I mock, and when should I use the real thing?" |
| § 8 — CI/CD Integration | Quality gates and pipeline config | "How do I enforce testing in the CI pipeline?" |
| § 9 — Coverage Strategy | Coverage as a metric, not a goal | "What coverage targets should I set?" |
| § 10 — Accessibility Testing | Automated + manual a11y testing | "How do I ensure my app is accessible?" |
| § 11 — Performance Testing | Lighthouse, bundle size, load testing | "When does performance testing become necessary?" |
| § 12 — Security Testing | Security-focused test strategy | "What security tests should I include?" |
| § 13 — Test Maintenance & Quality | Flaky tests, refactoring, cleanup | "How do I keep my test suite healthy over time?" |
| § 14 — Testing Checklist | Pre-merge and pre-release checklists | "What should I verify before shipping?" |

### AI Agent Instructions

This document is designed to be consumed by AI coding agents (e.g., Claude
Code). When interpreting this document:

- **MUST**, **SHOULD**, and **MAY** are RFC 2119 keywords — treat MUST as non-negotiable constraints, SHOULD as strong defaults that require explicit justification to override, and MAY as contextual options.
- Cross-references (→ See [XX-document.md]) point to authoritative definitions — always defer to the referenced document for the full rule.
- When this document conflicts with [07-security-standards.md], the security document takes precedence.
- BAD/GOOD code examples are pattern-matching references — apply the principle behind the example, not just the literal code.
- Anti-pattern tables describe common mistakes — use them as negative examples when reviewing or generating code.
- Every test generated MUST follow the test pyramid, naming conventions, and Arrange-Act-Assert pattern defined here.
- If generating code requires violating a MUST rule, the AI **MUST stop** and ask the human for permission before proceeding — never silently override a standard.
- **MUST NOT** over-engineer — always prefer the simplest solution that meets the stated requirements. Do not add abstractions, patterns, or infrastructure beyond what was explicitly requested (→ See [01-core-principles.md, §12]).
- **Version-critical rules for code generation:**
  - Vitest 4.x: DO NOT use Jest syntax or imports. `vi.mock()` MUST be at the top level of the test file, never inside `describe` blocks. DO NOT mock the database in integration tests — use a real test database with isolation (→ §4).

---

## 1. Testing Philosophy

Testing is not a phase that happens after development — it is an integral part
of development. A feature without tests is an unfinished feature, the same way
a function without error handling is an unfinished function. The mindset defined
in this section shapes every rule, every threshold, and every decision in the
rest of this document.

These principles are stack-agnostic and tier-agnostic — they apply equally to a
three-line unit test and a fifty-line E2E scenario.

> This section extends the philosophy defined in → See [01-core-principles.md,
> Section 1 — Philosophy & Mindset], applying it specifically to the testing
> domain.

---

### 1.1 Why We Test

Tests exist to serve three purposes — in this order of importance:

**1. Confidence to change**

The primary value of a test suite is not catching bugs in new code — it is
enabling safe changes to existing code. Without tests, every refactoring is a
gamble. With tests, a developer can rename a function, restructure a module, or
optimize an algorithm and know within seconds whether anything broke.

This is why tests are a prerequisite for refactoring
(→ See [01-core-principles.md, § 13.6 — Prerequisites for Safe Refactoring]).
Without tests, refactoring becomes "changing code and hoping for the best." With
tests, refactoring becomes a routine, low-risk activity that keeps the codebase
healthy.

```text
Without tests:                         With tests:
─────────────                          ──────────
"I need to change this function"       "I need to change this function"
 → "What else depends on it?"           → Change it
 → "I'm not sure..."                    → Run tests
 → "Let me test manually..."            → ✅ 47 tests pass, 0 fail
 → 45 minutes later, found 2 issues     → Done in 30 seconds
 → "Did I miss anything?"               → Confidence: high
 → Confidence: low
```

**2. Living documentation**

A well-written test suite is the most honest documentation a project has.
Comments lie — they are written once and never updated. READMEs go stale — they
describe the system as it was, not as it is. API documentation drifts — someone
changes the behavior but forgets to update the docs.

Tests cannot lie. A test that passes is a true statement about the system's
behavior right now. A test that says `'returns 404 when the user does not exist'`
is a specification that is verified on every CI run.

```ts
// This IS the documentation for calculateShipping:
describe('calculateShipping', () => {
  it('returns 0 for orders above the free shipping threshold', () => { ... });
  it('applies flat rate for domestic orders below threshold', () => { ... });
  it('applies weight-based rate for international orders', () => { ... });
  it('throws InvalidAddressError when the postal code is malformed', () => { ... });
  it('uses the warehouse closest to the destination', () => { ... });
});
// Reading these test names tells you more about the function
// than any comment or README ever could.
```

**3. Regression prevention**

Once a bug is found and fixed, a test ensures it never returns. The cost of
writing that test is paid once; the cost of re-discovering the bug is paid every
time it escapes.

- **MUST** write a failing test that reproduces a bug **before** fixing it —
  the test proves the bug exists, the fix makes the test pass, and the test
  prevents the bug from ever recurring
- **SHOULD** reference the bug ticket in the test name or comment so future
  developers understand why the test exists:

```ts
// Regression: fixes #234 — double-submit created duplicate orders
it('rejects the second submission when the idempotency key matches', async () => {
  // Arrange
  const idempotencyKey = 'order-abc-123';
  await orderService.create(validOrder, { idempotencyKey });

  // Act — attempt to create the same order again
  const duplicate = orderService.create(validOrder, { idempotencyKey });

  // Assert — second attempt is rejected, not silently duplicated
  await expect(duplicate).rejects.toThrow(ConflictError);
});
```

> **The absence of tests is not "saving time" — it is borrowing time from the
> future at a punishing interest rate.** Every untested feature is a silent bet
> that the code will never need to change, that no one will ever misunderstand
> it, and that the environment around it will remain frozen. That bet almost
> always loses.

---

### 1.2 What Makes a Good Test

A test that passes is not automatically a good test. A test that increases
coverage is not automatically a good test. Good tests share specific properties,
and understanding these properties helps distinguish tests that provide real
value from tests that provide only a false sense of security.

#### The Properties

| Property | Meaning | What happens when violated |
|---|---|---|
| **Deterministic** | Same code → same result, every time, on every machine | Flaky tests. The team learns to ignore failures. "It's just flaky" becomes the excuse for real bugs. Trust in the suite erodes. |
| **Independent** | No test depends on another test's execution, order, or state | Reordering tests produces different results. Running a subset fails unexpectedly. Debugging requires running the entire suite. |
| **Fast** | Unit tests in milliseconds; integration tests in low seconds | Developers stop running tests locally. Feedback loop breaks. Tests are only run in CI, where failures take 10+ minutes to surface. |
| **Focused** | Tests one behavior; fails for one reason | When it fails, you cannot tell which behavior broke. Multiple assertions test multiple things. Diagnosis takes investigation instead of a glance. |
| **Readable** | Intent is clear from the test name and structure alone | A failing test in CI requires reading the implementation to understand what went wrong. New developers cannot understand the test suite. |
| **Resilient** | Survives refactoring that preserves behavior | Internal changes (renaming a private function, changing a data structure, extracting a helper) break dozens of tests. The team avoids refactoring because "it will break all the tests." |

#### How to Evaluate

When reviewing a test (your own or someone else's), ask these questions:

1. **Can I understand what this test verifies by reading only the test name?**
   If not, the name needs improvement.
2. **If I delete the implementation and rewrite it differently (but with the
   same behavior), will this test still pass?** If not, the test is coupled to
   implementation details.
3. **Does this test add confidence that I would not already have from other
   tests or from the type system?** If not, the test may be redundant.
4. **If this test fails in CI at 3am, can I understand why from the test name
   and the failure message alone, without opening the source code?** If not,
   the assertions or the naming need work.

#### Examples

```ts
// BAD — not deterministic (depends on current time)
it('shows greeting message', () => {
  const result = getGreeting();
  expect(result).toBe('Good morning'); // Fails after noon
});

// GOOD — deterministic (controls the input)
it('returns "Good morning" for hours before 12', () => {
  const result = getGreeting(new Date('2026-01-15T08:00:00'));
  expect(result).toBe('Good morning');
});
```

```ts
// BAD — not focused (tests two unrelated behaviors)
it('creates user and sends welcome email', async () => {
  const user = await userService.create(validInput);
  expect(user.id).toBeDefined();           // Behavior 1: user creation
  expect(sendEmail).toHaveBeenCalled();     // Behavior 2: email sending
});

// GOOD — focused (one behavior per test)
it('creates a user with a generated UUID', async () => {
  const user = await userService.create(validInput);
  expect(user.id).toMatch(/^[0-9a-f-]{36}$/);
});

it('sends a welcome email after creating a user', async () => {
  await userService.create(validInput);
  expect(sendEmail).toHaveBeenCalledWith(
    validInput.email,
    expect.stringContaining('Welcome'),
  );
});
```

```ts
// BAD — not resilient (tests implementation details)
it('calls repository.findById with the correct ID', async () => {
  await userService.getById('abc-123');
  expect(mockRepository.findById).toHaveBeenCalledWith('abc-123');
  // This test breaks if the service starts using a different method name
  // or retrieves the user through a cache layer first.
});

// GOOD — resilient (tests the observable outcome)
it('returns the user when the ID exists', async () => {
  const user = await userService.getById('abc-123');
  expect(user).toMatchObject({ id: 'abc-123', name: 'Maria Silva' });
  // This test survives internal refactoring as long as the behavior is preserved.
});
```

- **MUST** ensure every test is deterministic — no dependency on time, random
  values, network, or execution order. Use `vi.useFakeTimers()` for time,
  `faker.seed()` for randomness, and test isolation for state.
- **MUST** ensure every test is independent — use `beforeEach` for setup,
  `afterEach` for cleanup, and factories for fresh data (→ See [Section 6]).
- **SHOULD** keep unit tests under 50ms and integration tests under 5 seconds.
  If a test is slower, investigate — it may be doing more work than necessary.
- **SHOULD** use one logical assertion per test. Multiple `expect()` calls are
  fine when they verify the same behavior (e.g., checking both status code and
  response body of an API response), but testing two unrelated behaviors in one
  test is an anti-pattern.

---

### 1.3 Testing Is Not Coverage

Coverage is a **metric**, not a **goal**. It measures how much code was executed
during tests — not how well that code was tested. This distinction is so
important that it deserves its own section in the philosophy, before any
discussion of targets or tools.

#### The Illusion of High Coverage

Consider this function and its "test":

```ts
// Implementation
function calculateDiscount(subtotal: number, couponCode: string): number {
  if (couponCode === 'SUMMER20') {
    return subtotal * 0.20;
  }
  if (couponCode === 'VIP50') {
    return subtotal * 0.50;
  }
  return 0;
}

// "Test" — achieves 100% line coverage
it('runs without crashing', () => {
  calculateDiscount(100, 'SUMMER20');
  calculateDiscount(100, 'VIP50');
  calculateDiscount(100, 'INVALID');
  // No assertions. Every line was executed. Coverage: 100%.
  // Confidence: 0%.
});
```

This test provides zero value — it will pass even if every `return` statement
is wrong. Coverage tools report 100% because every line was reached, but no
assertion verifies the output. The numbers look green; the code is unverified.

Now compare with meaningful tests at lower coverage:

```ts
it('applies 20% discount for SUMMER20 coupon', () => {
  expect(calculateDiscount(100, 'SUMMER20')).toBe(20);
});

it('applies 50% discount for VIP50 coupon', () => {
  expect(calculateDiscount(100, 'VIP50')).toBe(50);
});

it('returns 0 for unrecognized coupon codes', () => {
  expect(calculateDiscount(100, 'INVALID')).toBe(0);
});

it('calculates discount on the exact subtotal, not a rounded value', () => {
  expect(calculateDiscount(99.99, 'SUMMER20')).toBeCloseTo(19.998);
});
```

Same coverage, radically different confidence. The difference is **assertions
that verify behavior**.

#### The Right Relationship with Coverage

Use coverage to:

- **Find untested areas** — low coverage in a critical module is a signal to
  investigate. Not every uncovered line needs a test, but every uncovered line
  deserves the question: "should this be tested?"
- **Track trends** — declining coverage over time suggests new code is being
  added without tests. A coverage trend dashboard is more useful than a single
  number.
- **Enforce minimums** — a coverage threshold prevents coverage from regressing
  below a baseline. It catches "I forgot to add tests" but does not catch "I
  added bad tests."

Do not use coverage to:

- **Evaluate test quality** — a high number does not mean good tests.
- **Set promotion criteria** — "you cannot be promoted until coverage is X%"
  creates perverse incentives.
- **Compare developers** — coverage is a property of the codebase, not of
  individuals.
- **Block all deployments** — coverage gates that block urgent hotfixes are a
  governance failure, not a quality success.

- **MUST** use coverage as a diagnostic tool — to find gaps, not to prove
  quality
- **MUST NOT** write tests solely to increase a coverage number — every test
  must have a meaningful assertion that verifies behavior
- **SHOULD** review coverage reports in PRs to catch untested new code, not to
  enforce a percentage
- **SHOULD** track coverage trends over time rather than obsessing over a
  single snapshot

> → See [Section 9 — Coverage Strategy] for specific targets by layer, what
> to exclude, and how to configure coverage in Vitest 4.x.

---

### 1.4 The Cost Equation

Every testing decision involves a trade-off. Understanding the costs on both
sides — too little testing and too much testing — prevents both recklessness
and over-engineering.

#### The Cost of NOT Testing

| Cost | When it is paid | Magnitude |
|---|---|---|
| **Bugs in production** | After deployment, when users discover the problem | Hours to days to fix; reputation damage; potential data loss |
| **Fear of refactoring** | Every time a developer needs to change existing code | Code rots because no one dares touch it. Technical debt compounds exponentially. |
| **Manual regression testing** | Before every release | Person-hours spent clicking through the application. Slow, error-prone, incomplete. Scales linearly with application size. |
| **Knowledge silos** | When the original developer leaves or forgets | The behavior is undocumented. New developers guess, get it wrong, and introduce subtle bugs. |
| **Debugging time** | Every time something breaks in production | Without tests to narrow the problem, debugging is a haystack search. Minutes of prevention become hours of diagnosis. |
| **Loss of velocity** | Over time, gradually, then suddenly | Early in a project, shipping without tests feels fast. Six months later, every change takes three times longer because nothing is verified. |

#### The Cost of OVER-Testing

| Cost | When it is paid | Magnitude |
|---|---|---|
| **Slow CI pipelines** | Every PR, every push | Developers wait 20+ minutes for tests. Context switching increases. Feedback loop breaks. |
| **Brittle tests** | Every refactoring, even when behavior is preserved | Tests break on internal changes. "Fixing tests" becomes a chore. Developers avoid refactoring. |
| **Maintenance burden** | Ongoing, for the life of the test | Tests that verify trivial behavior still need updating when the code evolves. 1000 trivial tests cost more to maintain than 200 meaningful ones. |
| **Test fatigue** | When the team loses faith in the suite | When tests are noisy, slow, and frequently break for irrelevant reasons, developers stop trusting them. "The tests are probably just flaky" becomes the response to real failures. |
| **False sense of security** | When coverage is high but assertions are weak | The dashboard shows 90% coverage. The team feels confident. But the tests assert `toBeTruthy()` on everything and would pass even if the logic were completely wrong. |

#### The Sweet Spot

The goal is not maximum testing — it is **optimal testing**: the minimum
investment that provides sufficient confidence for the risk profile of the code.

```text
Confidence ▲
           │                    ╭──────────── diminishing returns
           │                 ╭──╯
           │              ╭──╯
           │           ╭──╯
           │        ╭──╯
           │     ╭──╯
           │  ╭──╯
           │──╯
           │
           └──────────────────────────────────────► Testing investment
              ▲                    ▲
              │                    │
         sweet spot          over-testing
         (here)              (not here)
```

The sweet spot is where:
- Every critical path has tests
- Business logic is verified at the unit tier
- Component interactions are verified at the integration tier
- Critical user journeys are verified at the E2E tier
- Trivial code is left untested (but genuinely trivial, not "simple-looking")
- The test suite runs fast enough to stay in the feedback loop

#### Rules

- **MUST** test every critical path — authentication, authorization, data
  mutation, payment flows, and any feature where failure has significant
  business consequences
- **MUST** test every bug fix with a regression test (→ See [Section 1.1])
- **SHOULD** test business logic, validation rules, data transformations, and
  state transitions
- **MAY** skip tests for trivial code — getters, pass-through functions,
  configuration constants, type-only files — but only when the code is
  genuinely trivial
- **MUST NOT** skip tests because "I'll add them later" — later never comes.
  If the code ships, it ships with tests. This is a Definition of Done
  requirement (→ See [01-core-principles.md, § 11 — Definition of Done])
- **MUST NOT** add tests solely to satisfy a coverage metric — every test
  must provide real confidence about a real behavior

> **Why:** Testing is an investment with diminishing returns. The first few tests
> provide enormous value. Each additional test provides less value than the
> previous one. At some point, the cost of writing, running, and maintaining
> a test exceeds the confidence it provides. The art of testing is knowing where
> that point is — and it is different for every module, every project, and every
> stage of maturity.

---

### 1.5 Test the Behavior, Not the Implementation

This principle is so fundamental — and so frequently violated — that it deserves
its own section. It appears in the anti-patterns of every domain testing section
([03-api-design.md § 13.7], [04-database-standards.md § 13.8],
[05-frontend-standards.md § 7]), but the underlying philosophy is defined here.

#### The Principle

A test should verify **what the code does** (its observable behavior), not
**how it does it** (its internal implementation). If you refactor the internals
of a function — change variable names, extract helpers, restructure data
flow — but the inputs and outputs remain the same, no test should break.

When tests are coupled to implementation:
- Refactoring breaks tests even when behavior is preserved
- The team avoids refactoring because "it will break all the tests"
- Tests become a maintenance burden instead of a safety net
- The codebase ossifies — the tests that were supposed to enable change now
  prevent it

When tests are coupled to behavior:
- Refactoring is safe — tests confirm behavior is preserved
- Tests survive internal changes
- Tests serve as specifications of what the system does
- The test suite enables change instead of preventing it

#### How to Identify the Violation

Ask this question: **"If I rewrote the implementation from scratch — different
variable names, different algorithms, different internal structure — but the
function accepts the same inputs and produces the same outputs, would this test
still pass?"**

If the answer is no, the test is testing implementation, not behavior.

#### Common Violations

**Violation 1: Asserting that internal methods were called**

```ts
// BAD — tests implementation (how the service works internally)
it('calls the repository with the correct parameters', async () => {
  await orderService.getOrdersForUser('user-123');

  expect(mockOrderRepository.findByUserId).toHaveBeenCalledWith('user-123');
  expect(mockOrderRepository.findByUserId).toHaveBeenCalledTimes(1);
  // If the service switches to a different repository method, a cache,
  // or a batching strategy, this test breaks — even though the behavior
  // (returning the user's orders) is preserved.
});

// GOOD — tests behavior (what the service returns)
it('returns all orders belonging to the user', async () => {
  // Arrange — seed test data (real DB or factory)
  const user = createFakeUser({ id: 'user-123' });
  const order1 = createFakeOrder({ userId: user.id });
  const order2 = createFakeOrder({ userId: user.id });
  const otherOrder = createFakeOrder({ userId: 'other-user' });

  // Act
  const orders = await orderService.getOrdersForUser(user.id);

  // Assert — verifies the result, not the internal call
  expect(orders).toHaveLength(2);
  expect(orders).toEqual(
    expect.arrayContaining([
      expect.objectContaining({ id: order1.id }),
      expect.objectContaining({ id: order2.id }),
    ]),
  );
});
```

**Violation 2: Testing internal state instead of observable output**

```ts
// BAD — tests internal state of a React component
it('sets isLoading to true when fetching', () => {
  const { result } = renderHook(() => useUsers());
  // Inspecting internal state — coupled to implementation
  expect(result.current.isLoading).toBe(true);
  // If the hook renames the flag to `isPending` or uses a
  // different loading mechanism, this test breaks.
});

// GOOD — tests what the user sees
it('shows a loading spinner while users are being fetched', async () => {
  render(<UserList />);
  expect(screen.getByRole('status')).toBeInTheDocument();
  // Tests the observable UI, not the internal hook state.
  // Survives any refactoring that preserves the loading indicator.
});
```

**Violation 3: Testing execution order**

```ts
// BAD — tests the order of internal operations
it('validates before saving', async () => {
  const validateSpy = vi.spyOn(validator, 'validate');
  const saveSpy = vi.spyOn(repository, 'save');

  await userService.create(validInput);

  const validateOrder = validateSpy.mock.invocationCallOrder[0];
  const saveOrder = saveSpy.mock.invocationCallOrder[0];
  expect(validateOrder).toBeLessThan(saveOrder);
  // If the service restructures to validate inline or uses a pipeline,
  // this test breaks even though the behavior (valid data is saved,
  // invalid data is rejected) is preserved.
});

// GOOD — tests that invalid data is rejected (the behavior)
it('rejects invalid input without persisting anything', async () => {
  const invalidInput = { email: 'not-an-email' };

  await expect(userService.create(invalidInput)).rejects.toThrow(
    ValidationError,
  );

  const users = await repository.findAll();
  expect(users).toHaveLength(0); // Nothing was persisted
});
```

#### Where the Line Gets Blurry

There are legitimate cases where testing internal interactions is acceptable:

- **Verifying a side effect occurred** — "a welcome email was sent" is a
  behavior, even though it requires asserting on a mock. The key is: are you
  testing that the side effect happened (behavior) or that a specific internal
  method was called with specific arguments (implementation)?
- **Verifying security boundaries** — "the auth middleware was invoked" may be
  worth testing directly because the consequence of it not being invoked is a
  security vulnerability, not just a behavioral difference.
- **Verifying performance-critical internal behavior** — "the cache is hit on
  the second call" may be worth testing if caching is a critical performance
  requirement, not an implementation detail.

The test: **would a user, API consumer, or product owner care about this
assertion?** If yes, it is behavior. If only a developer implementing the
internals would care, it is implementation.

#### Rules

- **MUST** write tests that verify observable behavior — inputs, outputs, side
  effects visible at the system boundary, and user-visible outcomes
- **MUST NOT** write tests that assert on internal method calls, private
  function invocations, or execution order — unless the internal behavior has
  direct security or performance implications
- **SHOULD** apply the "rewrite test" — mentally replace the implementation
  with a completely different one that has the same inputs and outputs. If the
  test would break, it is coupled to implementation.
- **SHOULD** prefer testing through the public interface (API endpoint,
  exported function, rendered component) over testing internal collaborators
  in isolation

> **Why:** Tests coupled to implementation are the number one cause of "the
> tests are slowing us down." They create a paradox: the tests that were written
> to enable safe change now prevent any change. The fix is not fewer tests — it
> is better-targeted tests that verify what matters and ignore how it happens.
> → See [01-core-principles.md, § 1.2 — Simplicity Is a Feature].

---

### 1.6 Tests Are Production Code

Tests deserve the same care, quality, and craftsmanship as the code they
verify. A test file that is messy, duplicated, and poorly named is just as
much a liability as a messy source file — perhaps more, because a bad test
actively misleads anyone reading it.

#### Why This Matters

When tests are treated as second-class code:
- Test files accumulate duplication — the same setup is copy-pasted across
  dozens of tests, so a single change to the data model requires updating 40
  files.
- Test names are vague — `'should work'`, `'test 1'`, `'handles edge case'` —
  providing no documentation value.
- Dead tests accumulate — `test.skip` and commented-out tests litter the suite,
  and no one knows whether they are intentionally disabled or accidentally
  forgotten.
- Review standards drop — "it's just a test" becomes the justification for
  accepting poorly structured test code in PRs.

When tests are treated as production code:
- Tests use factories and helpers to eliminate duplication (→ See [Section 6]).
- Test names are specifications that document the system's behavior
  (→ See [Section 3.6 — Test Naming Conventions]).
- Dead code is removed — the Boy Scout Rule applies to tests too
  (→ See [01-core-principles.md, § 13.4]).
- Tests are reviewed with the same rigor as implementation code.

#### Rules

- **MUST** apply the same naming conventions to test code as to production code
  — clear variable names, descriptive function names, no magic values
  (→ See [01-core-principles.md, § 3 — Naming Conventions])
- **MUST** apply the DRY principle to test setup — extract repeated setup into
  factories, helpers, or `beforeEach` blocks. But do not over-abstract: a test
  should be readable without navigating to five helper files.
- **MUST** review test code in PRs with the same attention as implementation
  code — a poorly written test is a technical debt item just like a poorly
  written function
- **SHOULD** apply the Boy Scout Rule to test files — if you are editing a test
  file, leave it slightly cleaner than you found it
  (→ See [01-core-principles.md, § 13.4 — The Boy Scout Rule])
- **SHOULD** refactor tests when they become hard to read, brittle, or
  duplicated — test refactoring is as valuable as code refactoring
  (→ See [Section 13 — Test Maintenance & Quality])
- **MUST NOT** tolerate commented-out tests or unexplained `test.skip` calls —
  either fix the test, document why it is skipped (with a ticket reference),
  or delete it. Git remembers everything.
- **MUST NOT** accept `'should work'`, `'test 1'`, or similarly vague test
  names in code review

#### The Balance: Readable vs DRY

Test code has a unique tension that production code does not: **readability
sometimes trumps DRY**. A test should be understandable in isolation — a
developer reading a failing test should not need to navigate through multiple
helper files to understand what the test does.

```ts
// TOO DRY — the test is unreadable without finding the helper
it('returns 201', async () => {
  const response = await makeRequest();  // What request? What data? What auth?
  assertSuccess(response);               // What is being asserted?
});

// TOO WET — everything is duplicated, maintenance nightmare
it('creates a user and returns 201', async () => {
  const input = {
    name: 'João Silva',
    email: 'joao@example.com',
    password: 'SecureP@ss123',
    role: 'user',
  };
  const response = await request(app)
    .post('/api/v1/users')
    .send(input)
    .set('Authorization', `Bearer ${generateToken({ role: 'admin' })}`);
  expect(response.status).toBe(201);
  expect(response.body.ok).toBe(true);
  expect(response.body.data.name).toBe('João Silva');
  expect(response.body.data.email).toBe('joao@example.com');
  expect(response.body.data.id).toBeDefined();
});

// JUST RIGHT — factories handle data, test is focused and readable
it('creates a user and returns 201 with the user data', async () => {
  // Arrange
  const input = createFakeUserInput({ role: 'user' });

  // Act
  const response = await request(app)
    .post('/api/v1/users')
    .send(input)
    .set('Authorization', `Bearer ${adminToken}`);

  // Assert
  expect(response.status).toBe(201);
  expect(response.body.ok).toBe(true);
  expect(response.body.data).toMatchObject({
    name: input.name,
    email: input.email,
  });
});
```

The "just right" version:
- Uses a factory for test data — no hardcoded strings, but the relevant
  override (`role: 'user'`) is visible in the test
- Uses a shared `adminToken` from `beforeAll` — common setup, not duplicated
- Keeps the HTTP call and assertions in the test — the reader sees the full
  flow without navigating elsewhere
- Uses `toMatchObject` instead of checking every field — focused on what this
  test cares about

- **SHOULD** extract **data creation** into factories and helpers
- **SHOULD** keep **test logic** (arrange, act, assert) in the test itself
- **SHOULD** extract **common setup** (database connections, auth tokens, server
  instances) into `beforeAll` / `beforeEach` blocks
- **MUST NOT** extract the assertions into helpers (unless the assertion is a
  custom matcher) — the assertion is the most important part of the test and
  should be visible at the call site

---

## 2. Test Pyramid & Strategy

The test pyramid is the central mental model for this entire document. It defines
how testing effort is distributed across different tiers — from fast, cheap,
focused tests at the base to slow, expensive, comprehensive tests at the top.
Every rule in later sections (coverage targets, CI gates, mocking strategy)
derives from the position of each test type in this pyramid.

This section defines the model, profiles each tier, and provides a decision
guide for choosing the right test type for any given piece of code.

> The test pyramid is a **model**, not a law. It provides a default allocation
> that works for most projects. Deviating from it is acceptable when justified
> — but the burden of proof is on the deviation, not on the model.

---

### 2.1 The Test Pyramid

```text
                     ╱╲
                    ╱  ╲
                   ╱    ╲                  Fewer tests
                  ╱ E2E  ╲                 Slowest, most expensive
                 ╱________╲                Highest confidence per test
                ╱          ╲               Test: complete user journeys
               ╱ Integration╲            Moderate speed and cost
              ╱______________╲           Test: component interactions
             ╱                ╲          Many tests
            ╱   Unit  Tests    ╲         Fastest, cheapest
           ╱____________________╲        Test: isolated logic
          ╱                      ╲
         ╱   Static Analysis      ╲      Not "tests" — but catches bugs
        ╱  (TypeScript + ESLint)   ╲     before any test runs
       ╱____________________________╲
```

The pyramid has a physics to it: tests at the bottom are fast and cheap, so you
can afford many of them. Tests at the top are slow and expensive, so you write
few of them. The total confidence comes from the **combination** of all layers —
no single layer provides enough confidence on its own.

#### Recommended Allocation

| Tier | Proportion | Typical count (small–medium project) | Run time per test |
|---|---|---|---|
| **Static Analysis** | Always-on (not counted) | N/A — runs on every file | Milliseconds (compile/lint) |
| **Unit** | 70–80% of test count | 100–500 tests | 1–50 ms |
| **Integration** | 15–25% of test count | 20–100 tests | 100 ms – 5 s |
| **E2E** | 5–10% of test count | 5–20 tests | 5–30 s |

These proportions are guidelines, not laws. The right ratio depends on the
application:

- An **API-only service** with complex business logic may have 85% unit tests,
  14% integration tests, and 1% E2E tests (smoke tests only — no UI to test).
- A **full-stack CRUD app** with simple logic may lean toward integration and
  component tests (60% unit, 30% integration, 10% E2E).
- A **design system / component library** may invest heavily in component tests
  and visual regression, with few E2E tests.

→ See [Section 2.8 — Adapting the Strategy by Project Type] for specific
guidance.

#### How the Layers Complement Each Other

Each layer catches different categories of bugs. Together, they form a
comprehensive safety net:

```text
What each layer catches:

Unit tests catch:
  ✓ Logic errors in pure functions
  ✓ Incorrect calculations, wrong return values
  ✓ Missing edge cases (null, empty, boundary values)
  ✓ Validation schema errors
  ✓ Type guard failures

  ✗ Cannot catch: integration mismatches, routing errors,
    middleware failures, UI rendering issues

Integration tests catch:
  ✓ Incorrect API responses (wrong status, wrong body)
  ✓ Database query errors (wrong data, missing joins)
  ✓ Middleware failures (auth rejection, validation bypass)
  ✓ RLS policy violations (unauthorized data access)
  ✓ Service-to-repository communication errors

  ✗ Cannot catch: UI rendering, browser-specific behavior,
    full user flow breakages across multiple pages

E2E tests catch:
  ✓ Broken user flows (login → dashboard → action)
  ✓ Navigation and routing errors
  ✓ Form submission failures end-to-end
  ✓ Client-server integration mismatches
  ✓ Visual regressions (with screenshot comparison)

  ✗ Cannot catch: every edge case (too slow and expensive
    to test every permutation)
```

- **MUST** maintain a balanced pyramid — more unit tests than integration tests,
  more integration tests than E2E tests
- **MUST NOT** rely on a single tier — a project with 500 unit tests and zero
  integration tests has blind spots, regardless of coverage percentage
- **SHOULD** use the pyramid as the default allocation and adjust based on
  project type (→ See [Section 2.8])
- **SHOULD** evaluate the combined coverage of all tiers, not each tier in
  isolation — the question is "is this behavior covered at any tier?" not
  "does each tier cover everything?"

---

### 2.2 Unit Tier Profile

Unit tests are the **foundation** of the pyramid — fast, cheap, focused, and
abundant. They test isolated units of logic (functions, classes, hooks, schemas)
without external dependencies.

#### Characteristics

| Property | Value |
|---|---|
| **Speed** | 1–50 ms per test |
| **Cost to write** | Low — straightforward input/output verification |
| **Cost to maintain** | Low — focused tests rarely break for unrelated reasons |
| **Confidence per test** | Moderate — verifies logic in isolation but not integration |
| **Failure diagnosis** | Immediate — points to the exact function and assertion |
| **External dependencies** | None — all external dependencies are mocked or injected |
| **Tool** | Vitest (→ See [Section 3.3] for configuration) |

#### What Unit Tests Verify

- **Pure functions** — given input X, the function returns Y. No side effects,
  no dependencies, no database, no network. This is the cheapest and most
  valuable type of test.

  ```ts
  // Pure function — perfect unit test candidate
  function calculateShippingCost(
    weight: number,
    zone: 'domestic' | 'eu' | 'international',
  ): number {
    if (weight <= 0) throw new ValidationError('Weight must be positive');
    const rates = { domestic: 2.50, eu: 7.50, international: 00 };
    return Math.round(weight * rates[zone] * 100) / 100;
  }
  ```

- **Validation schemas** — Zod schemas with custom refinements and transforms.
  Test that valid input passes, invalid input fails with correct error messages.

  ```ts
  // Schema validation — test the boundary between valid and invalid
  const createUserSchema = z.object({
    email: z.string().email(),
    name: z.string().min(2).max(100),
    role: z.enum(['user', 'admin']).default('user'),
  });
  ```

- **Service logic (pure parts)** — business rules, permission checks, state
  transitions, data transformations. Extract pure logic from services and test
  it directly.

- **Custom hooks** — React hooks that encapsulate reusable logic
  (`useDebounce`, `usePagination`, `useUrlState`). Test with `renderHook`
  from Testing Library.
  → See [05-frontend-standards.md, § 3] for hook testing patterns.

- **Utility functions** — formatters, validators, parsers, converters. Pure
  functions that transform data.

- **Type guards** — `isApiError()`, `isValidStatus()`. Verify that the guard
  correctly narrows the type.

- **Error classes** — custom error constructors, error mapping functions.

#### What Unit Tests Do NOT Verify

- **Framework internals** — do not test that React renders a `<div>` or that
  Express routes requests. The framework is already tested.
- **Trivial code** — a getter that returns a property, a one-line
  pass-through, or a constant definition.
- **External library behavior** — do not test that `dayjs` formats dates
  correctly. Test **your** code that uses `dayjs`.
- **Configuration objects** — static config consumed by a framework has no
  behavior to test (unless it contains computed logic).
- **TypeScript types** — the compiler validates types. Writing runtime tests
  for type-checked code is redundant (unless testing **runtime** validation
  like Zod schemas).
- **Database interactions** — that is integration testing.
- **HTTP request/response cycles** — that is integration testing.

#### When to Prefer Unit Tests Over Other Tiers

- The code is a **pure function** — no side effects, no external dependencies.
  This is the ideal unit test candidate.
- The code has **branching logic** — multiple code paths (if/else, switch,
  ternary) that each need verification. Unit tests can exhaustively cover
  every branch at minimal cost.
- The code handles **edge cases** — null inputs, empty arrays, boundary values,
  unicode characters, negative numbers. Unit tests are cheap enough to cover
  dozens of edge cases.
- The code is **shared across many consumers** — a utility function used by 20
  components should have thorough unit tests. A bug here propagates everywhere.

---

### 2.3 Integration Tier Profile

Integration tests verify that **components of the system work correctly
together** — a service calling a repository, an API route processing a request
through middleware, or a React component rendering data from a hook.

#### Characteristics

| Property | Value |
|---|---|
| **Speed** | 100 ms – 5 s per test |
| **Cost to write** | Medium — requires setup (test database, server instance, mock providers) |
| **Cost to maintain** | Medium — more moving parts mean more reasons to update |
| **Confidence per test** | High — verifies real interactions between components |
| **Failure diagnosis** | Good — narrows the problem to the integration boundary |
| **External dependencies** | Selective — uses real database and server, mocks external APIs |
| **Tool** | Vitest + Supertest (API), Vitest + test DB (services), Vitest + Testing Library (components) |

#### What Integration Tests Verify

- **API route handlers** — the full request/response cycle: routing, validation,
  authentication, service call, error handling, response format.
  → See [03-api-design.md, § 13] for detailed patterns.

  ```ts
  // Integration test: API route handler + validation + service + DB
  it('returns 201 with the created user when input is valid', async () => {
    const input = createFakeUserInput();

    const response = await request(app)
      .post('/api/v1/users')
      .send(input)
      .set('Authorization', `Bearer ${adminToken}`);

    expect(response.status).toBe(201);
    expect(response.body.ok).toBe(true);
    expect(response.body.data).toMatchObject({
      name: input.name,
      email: input.email,
    });
  });
  ```

- **Service + database interactions** — verifies that services correctly read
  from and write to the database, including query correctness, casing
  transformations, and relationship handling.
  → See [04-database-standards.md, § 13] for database testing patterns.

- **RLS policy enforcement** — verifies that Row-Level Security policies
  correctly restrict access per user role. This is a **critical security
  test** that must be run against a real database.
  → See [04-database-standards.md, § 13.4] for RLS testing patterns.

- **Middleware behavior** — verifies that authentication, authorization,
  rate limiting, and validation middleware work correctly in the request
  pipeline.

- **Component + hook composition** — verifies that a React component
  correctly renders data from a hook, handles loading and error states,
  and responds to user interaction.
  → See [05-frontend-standards.md, § 2–3] for component and hook
  testing patterns.

- **Database constraint enforcement** — verifies that NOT NULL, UNIQUE,
  CHECK, and foreign key constraints correctly reject invalid data.
  → See [04-database-standards.md, § 13.5] for constraint testing patterns.

#### What Integration Tests Do NOT Verify

- **Pure business logic in isolation** — if a function is pure (no side
  effects, no external dependencies), test it at the unit tier. Integration
  tests are for **interactions**, not calculations.
- **Third-party API behavior** — mock external services at the boundary.
  You are testing **your code's** integration with the contract, not
  the third party's implementation.
- **UI layout and styling** — integration tests verify behavior, not
  appearance. Use visual regression for layout concerns.
- **Every edge case** — integration tests are more expensive than unit
  tests. Cover the main paths and critical edge cases here; exhaustive
  edge case coverage belongs at the unit tier.

#### When to Prefer Integration Tests Over Other Tiers

- The code **crosses a boundary** — service → database, handler → service,
  component → hook → API. Whenever data flows between two layers, an
  integration test verifies the handoff.
- The code **depends on middleware or infrastructure** — authentication,
  validation, error handling middleware must be tested with real HTTP
  requests, not in isolation.
- The behavior **cannot be verified in isolation** — a service that
  constructs a SQL query and maps the result to a domain object needs a
  real database to verify correctness.
- The cost of failure is **moderate to high** — API endpoints, RLS policies,
  and data mutations deserve integration coverage because bugs at these
  boundaries have direct user impact.

---

### 2.4 E2E Tier Profile

End-to-end tests verify that the **entire application works from the user's
perspective** — browser, frontend, API, database, and all integrations
together. They are the most expensive tests to write and maintain, but
provide the highest confidence for critical user journeys.

#### Characteristics

| Property | Value |
|---|---|
| **Speed** | 5–30 s per test (sometimes longer for complex flows) |
| **Cost to write** | High — requires full environment, Page Objects, data seeding |
| **Cost to maintain** | High — any change in UI, routing, or flow can break E2E tests |
| **Confidence per test** | Very high — proves the entire stack works together |
| **Failure diagnosis** | Hard — failure could be anywhere in the full stack |
| **External dependencies** | Full stack — real browser, real server, real database |
| **Tool** | Playwright (→ See [Section 5.3] for configuration) |

#### What E2E Tests Verify

E2E tests cover **critical user flows** — the paths where failure has the
highest business impact:

- **Authentication flows** — login, logout, session refresh, token expiration.
  A broken auth flow means users cannot access the application.

  ```ts
  test('redirects to dashboard after successful login', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login('user@example.com', 'validPassword123');

    await expect(page).toHaveURL('/dashboard');
    await expect(
      page.getByRole('heading', { name: 'Dashboard' }),
    ).toBeVisible();
  });
  ```

- **Primary data submission** — creating, updating, or deleting important
  records through forms. A broken form means data loss or user frustration.

- **Navigation and routing** — main routes resolve correctly, protected
  routes redirect unauthenticated users, deep links work.

- **Checkout / payment flows** — if the application processes payments, the
  checkout flow is the highest-value test. A broken checkout is lost revenue.

- **Smoke tests** — "does the app load and can a user complete the primary
  flow?" The fastest way to verify a deployment works.

#### What E2E Tests Do NOT Verify

- **Every edge case** — E2E tests are too slow and expensive for exhaustive
  edge case coverage. Test edge cases at the unit or integration tier.
- **API validation rules** — testing that an endpoint rejects invalid input
  is much faster with Supertest than with a browser.
- **Visual styling** — E2E tests verify behavior, not appearance. Use visual
  regression testing (screenshot comparison) for styling verification
  (→ See [05-frontend-standards.md, § 5]).
- **Third-party widget behavior** — do not test that Stripe's payment form
  renders correctly. Test that **your** integration with Stripe processes a
  payment.
- **CRUD variations** — if creating a user with one set of data works,
  creating another user with slightly different data does not need a
  separate E2E test. Vary input at the integration or unit tier.

#### When to Prefer E2E Tests Over Other Tiers

- The flow **crosses the entire stack** — from browser interaction, through
  the API, to the database, and back. Only E2E tests verify this complete
  chain.
- The flow is **business-critical** — login, checkout, registration,
  primary data submission. The cost of this flow breaking in production is
  high enough to justify the expensive test.
- The flow is a **deployment smoke test** — after deploying, you need to
  verify the application works. A handful of E2E smoke tests provide this
  assurance faster than manual verification.
- The behavior involves **browser-specific concerns** — navigation,
  redirects, cookies, local storage, browser APIs.

---

### 2.5 Static Analysis: The Invisible Layer

Static analysis is not traditionally considered "testing," but it catches
an entire category of bugs before any test runs. In the context of these
standards — where TypeScript strict mode is mandatory
(→ See [01-core-principles.md, § 2.1 — Type Safety First]) — static
analysis forms the invisible foundation of the testing strategy.

#### What Static Analysis Catches

| Tool | What it catches | When it catches it |
|---|---|---|
| **TypeScript (strict mode)** | Type mismatches, null/undefined access, missing properties, incorrect function signatures, unreachable code | At compile time, in the IDE, before tests run |
| **ESLint** | Code style violations, common error patterns, unused variables, inconsistent imports | At lint time, in the IDE, in CI |
| **Zod (runtime validation)** | Invalid data from untrusted boundaries (API input, env vars, external API responses) | At runtime, at the system boundary — verified by unit and integration tests |

#### Why This Matters for the Test Pyramid

Static analysis eliminates a large class of bugs that would otherwise require
unit tests. Consider this example:

```ts
// Without TypeScript strict mode, this bug requires a test:
function getUsername(user) {
  return user.name.toUpperCase(); // Crashes if user is null
}

// With TypeScript strict mode, this bug is caught at compile time:
function getUsername(user: User): string {
  return user.name.toUpperCase(); // TS error if User allows null
}
// The compiler forces you to handle the null case before the code runs.
// No test needed — the type system is the test.
```

This is why the testing trophy model (→ See [Section 2.6]) places static
analysis as the explicit base layer: in a TypeScript project with strict
mode, a significant percentage of potential bugs are caught before any
test runs.

#### Rules

- **MUST** treat TypeScript and ESLint as the first quality gate — they run
  before tests in the CI pipeline (→ See [Section 8.1])
- **MUST NOT** write unit tests for behavior that TypeScript already
  enforces — if the compiler rejects the invalid input, a test for the
  same scenario is redundant
- **SHOULD** use static analysis as a signal for which tests to write — if
  TypeScript cannot enforce a business rule (e.g., "quantity must be
  positive"), that rule needs a test. If TypeScript can enforce it
  (e.g., "email must be a string"), it does not.
- **SHOULD** use Zod for runtime validation at untrusted boundaries and
  test the schemas that Zod enforces
  (→ See [01-core-principles.md, § 2.1 — Type Safety First])

---

### 2.6 The Testing Trophy (Awareness)

The "testing trophy" model (popularized by Kent C. Dodds) reframes the
traditional pyramid for modern full-stack applications:

```text
Traditional Pyramid:              Testing Trophy:

      ╱╲  E2E                         ╱╲  E2E (few)
     ╱  ╲                            ╱  ╲
    ╱    ╲                          ╱    ╲
   ╱______╲ Integration            ╱______╲ Integration (MOST)
  ╱        ╲                      ╱        ╲    ← primary investment
 ╱__________╲ Unit (MOST)        ╱__________╲ Unit (some)
╱            ╲                  ╱            ╲
                               ╱______________╲ Static (TypeScript, ESLint)

Focus: test isolated logic      Focus: test realistic interactions
Best for: complex logic,        Best for: CRUD apps, full-stack
  algorithms, libraries           TypeScript, component-heavy UIs
```

#### The Trophy Model Rationale

The trophy model argues that for full-stack TypeScript applications:

1. **Static analysis (TypeScript + ESLint)** already catches many bugs that
   unit tests would otherwise cover — type errors, null access, missing
   properties, unused variables.
2. **Integration tests provide more confidence per test** than unit tests
   because they exercise real interactions between components — the service
   talks to a real database, the component renders with real data, the API
   route processes a real request.
3. **Unit tests remain valuable** for complex business logic, but for simple
   CRUD services that just bridge the API to the database, unit tests add
   cost without proportional confidence.

#### Our Position

The **traditional pyramid** remains our **default model**. The trophy model
is a valid alternative for specific project types.

Why the pyramid is our default:
- It is safer for projects at any maturity level
- It forces developers to think about pure function design, which produces
  better code (→ See [01-core-principles.md, § 3.1 — Function Design])
- It produces the fastest test suite (unit tests run in milliseconds)
- It is easier to maintain (unit tests have fewer reasons to break)

When the trophy model is valid:
- TypeScript strict mode is enforced across the project
- The application is primarily CRUD with straightforward business logic
- Integration tests can run fast enough to stay in the feedback loop
  (< 10 seconds for a single test file)
- The team has experience with integration testing and can avoid common
  pitfalls (shared state, slow setup, flaky tests)

#### Rules

- **MUST** respect the core principle of both models: more fast/cheap tests
  than slow/expensive tests — regardless of which model is chosen
- **SHOULD** use the traditional pyramid as the default for all projects
- **MAY** adopt the trophy model for full-stack Next.js CRUD applications
  where integration tests provide more value than unit tests — document
  the decision in an ADR
  (→ See [01-core-principles.md, § 9 — Architecture Decision Records])
- **MUST NOT** use the trophy model as justification for skipping unit tests
  on complex business logic — pure functions with branching logic, complex
  calculations, and state machines still need unit tests regardless of the
  model chosen
- **MUST NOT** use the trophy model as justification for slow test suites —
  if integration tests take more than 10 seconds per file, the model is
  not working for the project

---

### 2.7 Decision Guide: What Type of Test Should I Write?

When in doubt about which test tier to use, follow this decision tree. Start
at the top and follow the path that matches your code:

```text
START: I need to write a test for this code.
│
├── Is it a pure function with no side effects?
│   │
│   ├── YES → Is the logic complex (branching, edge cases, calculations)?
│   │   │
│   │   ├── YES → ✅ UNIT TEST (Vitest)
│   │   │         Exhaustive coverage of all branches and edge cases.
│   │   │         Examples: calculateTotal(), validateCoupon(), formatCurrency()
│   │   │
│   │   └── NO → Is it used by many consumers (shared utility)?
│   │       │
│   │       ├── YES → ✅ UNIT TEST (Vitest)
│   │       │         A bug here propagates everywhere.
│   │       │         Examples: slugify(), deepMerge(), parseDate()
│   │       │
│   │       └── NO → The type system + integration tests probably cover it.
│   │                 MAY skip a dedicated unit test if tested at a higher tier.
│   │
│   └── NO → Does it interact with a database?
│       │
│       ├── YES → ✅ INTEGRATION TEST (Vitest + test DB)
│       │         Use a real test database, not mocks.
│       │         → See [04-database-standards.md, § 13] for patterns.
│       │         Examples: repository queries, RLS policies, constraints
│       │
│       └── NO → Does it handle HTTP requests/responses?
│           │
│           ├── YES → ✅ INTEGRATION TEST (Vitest + Supertest)
│           │         Test the full request/response cycle.
│           │         → See [03-api-design.md, § 13] for patterns.
│           │         Examples: API route handlers, middleware, validation
│           │
│           └── NO → Is it a UI component or hook?
│               │
│               ├── YES → Is it a Server Component that uses `await`?
│               │   │
│               │   ├── YES → ✅ E2E TEST (Playwright)
│               │   │         Vitest does not support async Server Components.
│               │   │         → See [05-frontend-standards.md, § 1]
│               │   │
│               │   └── NO → ✅ COMPONENT TEST (Vitest + Testing Library)
│               │             → See [05-frontend-standards.md, § 2–3]
│               │
│               └── Is it a critical user flow (login, checkout, registration)?
│                   │
│                   ├── YES → ✅ E2E TEST (Playwright)
│                   │         → See [Section 5] for E2E strategy.
│                   │
│                   └── NO → Reconsider: is this behavior already covered
│                             by a test at another tier?
│                             If not, write a unit or integration test.
```

#### Quick Reference Table

For rapid decision-making, this table maps common code patterns to test types:

| Code pattern | Test type | Tool | Example |
|---|---|---|---|
| Pure function (no side effects) | Unit | Vitest | `calculateTotal(items, taxRate)` |
| Zod schema with refinements | Unit | Vitest | `createUserSchema.parse(input)` |
| Custom React hook | Unit / Component | Vitest + `renderHook` | `useDebounce(value, delay)` |
| Type guard function | Unit | Vitest | `isApiError(error)` |
| Service calling a repository | Integration | Vitest + test DB | `orderService.getByUserId(id)` |
| API route handler | Integration | Vitest + Supertest | `POST /api/v1/users` |
| RLS policy enforcement | Integration | Vitest + Supabase local | User A cannot see User B's data |
| Database constraint | Integration | Vitest + test DB | UNIQUE constraint rejects duplicate |
| React component with interaction | Component | Vitest + Testing Library | `<OrderForm />` submit flow |
| Middleware chain | Integration | Vitest + Supertest | Auth → validation → handler |
| Login → dashboard flow | E2E | Playwright | Full browser flow |
| Checkout with payment | E2E | Playwright | Form → API → confirmation |
| Smoke test after deployment | E2E | Playwright | App loads, primary page renders |
| Async Server Component | E2E | Playwright | Page with `await` data fetching |

---

### 2.8 Adapting the Strategy by Project Type

The pyramid model is the default, but the **emphasis** within the pyramid
shifts depending on the type of project.

#### API-Only Service (Express / NestJS)

No browser, no UI — the API is the product.

```text
Emphasis:
  Unit:        ████████████████████  (80%) — business logic, validation, calculations
  Integration: ████████████         (18%) — API routes + DB, middleware, auth
  E2E:         █                    (2%)  — smoke tests only (health check, basic CRUD)
```

- **High investment in unit tests** — business logic is the core value. Every
  function, every validation rule, every calculation gets unit tests.
- **Moderate investment in integration tests** — API routes are tested with
  Supertest to verify the HTTP contract. Database interactions are tested
  with a real test database.
- **Minimal E2E** — no browser to test. A few smoke tests verify the API
  is reachable and responds correctly to a basic request.

#### Full-Stack Next.js Application

The typical project: React frontend + API routes + database.

```text
Emphasis:
  Unit:        ██████████████       (65%) — services, utilities, hooks, schemas
  Integration: ████████████         (25%) — API routes, components + hooks, RLS
  E2E:         █████                (10%) — critical user flows (login, forms, checkout)
```

- **Balanced investment** — business logic in services gets unit tests,
  API and database layers get integration tests, critical flows get E2E.
- **Component tests count as integration** — a component rendering with
  data from a hook is an integration test in behavior, even though it
  runs in Vitest.
- **E2E focuses on the flows that matter** — login, registration, primary
  CRUD operations, and deployment smoke tests.

#### Component Library / Design System

The product is a collection of reusable UI components.

```text
Emphasis:
  Unit:        ██████████           (45%) — utility functions, hook logic
  Integration: ██████████████       (45%) — component rendering, interaction, a11y
  E2E:         ████                 (10%) — visual regression, cross-browser checks
```

- **Heavy investment in component tests** — every component is tested with
  Testing Library for rendering, interaction, and accessibility.
- **Visual regression is important** — screenshot comparison catches styling
  regressions that functional tests miss
  (→ See [05-frontend-standards.md, § 5]).
- **Storybook integration** — if adopted (🔬 Trial in the radar), stories
  serve as both documentation and visual test targets.
- **E2E tests verify cross-browser behavior** — if the library supports
  multiple browsers, Playwright tests verify rendering consistency.

#### Python Backend / Data Service (FastAPI)

Server-side logic with Python, typically for AI/ML, data processing, or
automation.

```text
Emphasis:
  Unit:        ████████████████████  (80%) — data transformations, business logic
  Integration: ████████████          (18%) — API endpoints, database, external APIs
  E2E:         █                     (2%)  — health check, basic request/response
```

- **Unit tests are dominant** — Python services typically contain complex data
  transformations and business logic that benefit from exhaustive unit testing.
- **Integration tests verify the API contract** — use `httpx` with
  `TestClient` (FastAPI) or equivalent.
- **Minimal E2E** — similar to API-only services, unless the service has a
  UI (admin panel, dashboard).

> **Note:** Python-specific testing tools (pytest, httpx, factory_boy) are
> not covered in this document — they will be addressed when
> Python-specific standards are formalized.

#### Rules

- **MUST** adapt the pyramid proportions to the project type — do not force
  a one-size-fits-all ratio
- **SHOULD** document the chosen testing strategy in the project README or
  in an ADR if it deviates significantly from the defaults above
- **MUST NOT** use project type as an excuse for no E2E tests — even
  API-only services benefit from at least one smoke test
- **MUST NOT** use project type as an excuse for no unit tests — even
  component-heavy UIs contain utility functions and hooks that deserve
  unit tests

---

## 3. Unit Testing Standards

§ 2.2 defined **what** to unit test and **when** to prefer unit tests over
other tiers. This section defines the **how** — shared Vitest configuration,
file organization, test structure, naming conventions, and mocking guidance
at the unit level.

> For domain-specific unit testing patterns (API service tests, schema
> validation tests, hook tests), see the domain documents:
> → See [03-api-design.md, § 13], [04-database-standards.md, § 13],
> [05-frontend-standards.md, § 15].

---

### 3.1 Vitest Configuration (Shared Baseline)

All projects **MUST** use this baseline configuration, extending or overriding
only when the project has a justified need.

```ts
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import path from 'node:path';

export default defineConfig({
  test: {
    // --- Environment ---
    environment: 'node', // Use 'jsdom' only for component tests without Browser Mode

    // --- File patterns ---
    include: ['src/**/*.test.ts', 'src/**/*.test.tsx'],
    exclude: ['node_modules', 'dist', 'tests/e2e/**'],

    // --- Setup ---
    setupFiles: ['./vitest.setup.ts'],

    // --- Mock cleanup ---
    restoreMocks: true, // Automatically calls vi.restoreAllMocks() after each test

    // --- Coverage (Vitest 4.x) ---
    coverage: {
      provider: 'v8',
      // CRITICAL in Vitest 4.x: coverage.all was removed.
      // You MUST define include explicitly to see uncovered files in the report.
      include: ['src/**/*.ts', 'src/**/*.tsx'],
      exclude: [
        'src/**/*.test.ts',
        'src/**/*.test.tsx',
        'src/**/*.d.ts',
        'src/**/index.ts',       // Barrel files — no logic to test
        'src/**/types.ts',       // Type-only files — no runtime behavior
        'src/**/*.stories.tsx',  // Storybook stories
        'src/**/*.config.ts',   // Configuration files
      ],
      reporter: ['text', 'html', 'json-summary', 'lcov'],
      // Thresholds — adjust per project maturity
      // → See Section 9 for recommended targets by layer
    },

    // --- Performance ---
    pool: 'forks',         // Process isolation — prevents cross-contamination
    fileParallelism: true, // Run test files in parallel

    // --- Reporting ---
    reporters: ['default'],
    outputFile: {
      json: './coverage/test-results.json',
    },
  },

  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

```ts
// vitest.setup.ts
// Runs before all test files. Add global setup here.

// Example: Extend matchers for Testing Library (component tests)
// import '@testing-library/jest-dom/vitest';

// Example: MSW server setup (→ See Section 7.3)
// import { server } from './src/mocks/node';
// beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
// afterEach(() => server.resetHandlers());
// afterAll(() => server.close());
```

#### Configuration Rules

- **MUST** configure in `vitest.config.ts` — not inline in `vite.config.ts`
  unless the project is trivially small
- **MUST** set `coverage.include` explicitly — Vitest 4.x no longer includes
  uncovered files by default (breaking change from 3.x)
- **MUST** set `restoreMocks: true` — prevents mock leaks between tests
  without requiring manual `vi.restoreAllMocks()` in every file
- **MUST** use `v8` coverage provider — in Vitest 4.x, the V8 provider uses
  AST-based analysis and is as accurate as Istanbul while being faster
- **SHOULD** use `pool: 'forks'` for test isolation — prevents global state
  leaks between test files. Use `pool: 'threads'` only when tests are
  pure and speed is critical.
- **SHOULD** co-locate test files with source (→ See [Section 3.2])

#### npm Scripts (Standard)

Every project **MUST** have these scripts in `package.json`:

```json
{
  "scripts": {
    "test": "vitest",
    "test:run": "vitest run",
    "test:coverage": "vitest run --coverage",
    "test:ui": "vitest --ui"
  }
}
```

| Script | Purpose | When to use |
|---|---|---|
| `test` | Watch mode — reruns on file changes | During development |
| `test:run` | Single run — exit with code 0 or 1 | In CI, in pre-commit hooks |
| `test:coverage` | Single run + coverage report | In CI, before PRs |
| `test:ui` | Visual UI for browsing tests and results | Debugging, exploring test suite |

---

### 3.2 Test File Organization

- **MUST** co-locate unit and integration tests with their source files:

```text
src/
├── services/
│   ├── order-service.ts
│   ├── order-service.test.ts       ← Unit tests for pure logic
│   └── order-service.int.test.ts   ← Integration tests (with DB)
├── utils/
│   ├── format-currency.ts
│   └── format-currency.test.ts
├── schemas/
│   ├── user-schema.ts
│   └── user-schema.test.ts
└── components/
    ├── OrderForm.tsx
    └── OrderForm.test.tsx
```

- **MUST** keep E2E tests in a dedicated directory (separate from unit/integration):

```text
tests/
└── e2e/
    ├── auth-flow.spec.ts
    ├── checkout-flow.spec.ts
    └── pages/                      ← Page Object Models
        ├── login.page.ts
        └── checkout.page.ts
```

- **MUST** use the naming convention:
  - `<module>.test.ts` — unit tests (default)
  - `<module>.int.test.ts` — integration tests (when both exist for the same module)
  - `<flow>.spec.ts` — E2E tests (Playwright convention)

> **Why co-location?** When a test lives next to its source file, developers
> see it every time they open the module. It is obvious that the test exists,
> obvious that it needs updating when the source changes, and obvious when a
> module has no test. Centralized `__tests__/` directories create distance
> between code and tests, making it easy to forget about them.

---

### 3.3 Arrange-Act-Assert Pattern

Every test **MUST** follow the Arrange-Act-Assert (AAA) pattern — the
universal test structure across all tiers.

> → See [01-core-principles.md, § 11 — Definition of Done] — AAA is a DoD
> requirement.

```ts
it('applies 23% tax rate for PT locale', () => {
  // Arrange — set up test data and preconditions
  const items = [
    { name: 'Widget', price: 10.0, quantity: 2 },
    { name: 'Gadget', price: 25.0, quantity: 1 },
  ];
  const taxRate = 0.23;

  // Act — execute the behavior under test
  const total = calculateTotal(items, taxRate);

  // Assert — verify the result
  expect(total).toBe(55.35); // (20 + 25) * 1.23
});
```

#### Rules

- **MUST** separate the three phases visually — blank lines and comments
  (`// Arrange`, `// Act`, `// Assert`) in longer tests. For short tests
  (3–5 lines), the structure is implicit and comments are optional.
- **MUST** have exactly one logical Act per test — multiple actions means
  multiple behaviors, which means the test should be split
- **SHOULD** keep Arrange minimal — use factories (→ See [Section 6]) for
  complex test data instead of building it inline
- **SHOULD** prefer specific assertions over vague ones:

```ts
// BAD — vague assertions that hide failures
expect(result).toBeTruthy();          // Passes for any truthy value
expect(result).toBeDefined();         // Passes for literally anything except undefined
expect(users.length).toBeGreaterThan(0); // Passes for 1 or 1000

// GOOD — specific assertions that pinpoint failures
expect(result).toBe(55.35);
expect(result).toEqual({ id: 'abc', name: 'Maria' });
expect(users).toHaveLength(3);
expect(error.code).toBe('VALIDATION_ERROR');
```

---

### 3.4 Test Naming Conventions

Test names should read as specifications — a developer should understand what
the system does by reading the test names alone.

```ts
// BAD — vague, no behavior described
it('should work')
it('test calculateTotal')
it('handles edge case')

// GOOD — states scenario and expected outcome
it('returns 0 when the items array is empty')
it('applies 23% tax rate for PT locale')
it('throws ValidationError when price is negative')
it('rounds total to 2 decimal places')
```

- **MUST** describe the expected behavior, not the implementation
- **SHOULD** follow the pattern: `<expected result> when <condition>`
- **SHOULD** group related tests with `describe` blocks:

```ts
describe('calculateTotal', () => {
  describe('when items are valid', () => {
    it('sums prices multiplied by quantity', () => { ... });
    it('applies the tax rate to the subtotal', () => { ... });
    it('rounds to 2 decimal places', () => { ... });
  });

  describe('when input is invalid', () => {
    it('returns 0 when items array is empty', () => { ... });
    it('throws ValidationError when price is negative', () => { ... });
    it('throws ValidationError when quantity is zero', () => { ... });
  });
});
```

The `describe` nesting creates a readable spec when tests run:

```text
calculateTotal
  when items are valid
    ✓ sums prices multiplied by quantity
    ✓ applies the tax rate to the subtotal
    ✓ rounds to 2 decimal places
  when input is invalid
    ✓ returns 0 when items array is empty
    ✓ throws ValidationError when price is negative
    ✓ throws ValidationError when quantity is zero
```

---

### 3.5 Mocking at the Unit Level

Unit tests isolate the code under test from external dependencies. This
requires mocking — but **only at boundaries**
(→ See [Section 7] for the complete mocking philosophy).

#### What to Mock in Unit Tests

| Dependency type | Mock? | How |
|---|---|---|
| External APIs (Stripe, SendGrid, etc.) | ✅ Always | `vi.mock()` or MSW |
| Database / repository calls | ✅ In unit tests | `vi.mock()` or dependency injection |
| `Date.now()`, `Math.random()` | ✅ When result depends on them | `vi.useFakeTimers()`, `faker.seed()` |
| Environment variables | ✅ When behavior changes per env | `vi.stubEnv()` |
| Sibling services (your own code) | ⚠️ Rarely | Prefer dependency injection; mock only if unavoidable |
| The function's own logic | ❌ Never | If you mock the thing you're testing, you're testing the mock |

#### `vi.mock()` Essentials

```ts
// Mock an entire module — hoisted to the top of the file automatically
vi.mock('@/lib/email', () => ({
  sendEmail: vi.fn().mockResolvedValue({ success: true }),
}));

// Override per-test when needed
it('handles email send failure', async () => {
  const { sendEmail } = await import('@/lib/email');
  vi.mocked(sendEmail).mockRejectedValueOnce(new Error('SMTP timeout'));

  await expect(notifyUser(user)).rejects.toThrow('Failed to notify user');
});
```

- **MUST** keep `vi.mock()` calls at the top level of the file — Vitest
  hoists them automatically; placing them inside `describe` or `it` causes
  confusing behavior
- **MUST NOT** mock more than necessary — mock the boundary, not the internals.
  If you find yourself mocking 5+ modules to test one function, the function
  has too many dependencies and should be refactored.
- **SHOULD** prefer dependency injection over `vi.mock()` when possible —
  pass the dependency as a parameter instead of importing and mocking:

```ts
// HARD TO TEST — imports the dependency directly
import { sendEmail } from '@/lib/email';

async function notifyUser(user: User): Promise<void> {
  await sendEmail(user.email, 'Welcome!');
}

// EASY TO TEST — dependency is injected
async function notifyUser(
  user: User,
  emailSender: (to: string, body: string) => Promise<void> = sendEmail,
): Promise<void> {
  await emailSender(user.email, 'Welcome!');
}

// Test — no vi.mock() needed
it('sends a welcome email to the user', async () => {
  const mockSender = vi.fn().mockResolvedValue(undefined);
  await notifyUser(user, mockSender);
  expect(mockSender).toHaveBeenCalledWith(user.email, 'Welcome!');
});
```

---

### 3.6 Anti-Patterns

| Anti-Pattern | Why it is bad | What to do instead |
|---|---|---|
| **Testing implementation details** | Breaks on refactoring when behavior is preserved (→ See [§ 1.5]) | Test inputs and outputs, not internal calls |
| **Multiple Acts in one test** | Cannot tell which action caused the failure | One test = one behavior |
| **Shared mutable state between tests** | Order-dependent, flaky | Reset state in `beforeEach`; fresh factories per test |
| **`toBeTruthy()` on objects** | Hides actual value; passes for unexpected truthy values | Use `toEqual()`, `toMatchObject()`, or property assertions |
| **Copy-pasting test data** | Duplication; changes require updating every copy | Use factories (→ Section 6) |
| **Testing framework behavior** | Wastes time testing code you do not own | Trust the framework; test your logic |
| **Snapshot abuse** | Large snapshots are never reviewed; pass for wrong reasons | Use targeted assertions; reserve snapshots for intentional locks |
| **`test.skip` without a reason** | Skipped tests rot silently | Add a TODO with ticket reference, or delete |
| **Mocking your own code extensively** | Tests pass but real interactions are broken; signal of tight coupling | Refactor for dependency injection; test through public interface |

---

### 3.7 VS Code Integration

The right editor setup makes the difference between "testing is a chore" and
"testing is part of the flow." These extensions integrate Vitest and Playwright
directly into VS Code — run tests with a click, debug with breakpoints, see
coverage inline, and generate E2E tests by recording browser interactions.

#### Recommended Extensions

| Extension | ID | Purpose |
|---|---|---|
| **Vitest** (official) | `vitest.explorer` | Run/debug unit and integration tests from the editor. Continuous run (watch mode per file), inline coverage, breakpoint debugging. Uses VS Code's native Testing API. |
| **Playwright Test for VS Code** (official) | `ms-playwright.playwright` | Run/debug E2E tests from the editor. Pick Locator (click element → get locator code), Record New Test (browser recording → generated code), Trace Viewer integration, multi-browser selection. |
| **Error Lens** | `usernamehw.errorlens` | Shows errors and warnings inline next to the code. When a test fails, the error appears at the exact line — no need to open the Problems panel. |
| **Coverage Gutters** | `ryanluker.vscode-coverage-gutters` | Displays coverage inline in the gutter (green = covered, red = uncovered). Reads `lcov.info` from Vitest's coverage output. |

> **Warning:** There is a deprecated Vitest extension (`ZixuanChen.vitest-explorer`)
> that still appears in search results. Do **not** install it — use only the
> official `vitest.explorer` from the Vitest team.

#### Setup Tips

- **Vitest extension** — works automatically when `vitest.config.ts` is
  detected in the workspace. Enable "Continuous Run" (the eye icon in the
  Testing sidebar) to re-run tests on file save — this is faster than the
  terminal `vitest --watch` because it runs only the affected tests.

- **Playwright extension** — after installing, run the command
  `Test: Install Playwright` from the Command Palette if you have not already
  set up Playwright. The **Pick Locator** feature is particularly valuable:
  it opens a browser where you click on elements and the extension generates
  the accessible locator (`getByRole`, `getByLabel`, etc.) — aligned with the
  locator priority defined in § 5.2.

- **Coverage Gutters** — after running `npm run test:coverage`, press
  `Ctrl+Shift+P` → "Coverage Gutters: Display Coverage" to see inline
  coverage. Requires the Vitest coverage reporter to include `'lcov'`:

```ts
// Add 'lcov' to the reporter array in vitest.config.ts
coverage: {
  reporter: ['text', 'html', 'json-summary', 'lcov'],
},
```

#### Rules

- **SHOULD** install the Vitest and Playwright VS Code extensions in every
  development environment — they significantly reduce the friction of running
  and debugging tests
- **SHOULD** use Playwright's Pick Locator to generate accessible selectors
  instead of manually writing CSS selectors
- **MAY** use Playwright's Record New Test to bootstrap E2E tests quickly,
  then refine the generated code manually (codegen produces working but
  non-optimal tests)

---

## 4. Integration Testing Standards

§ 2.3 defined the integration tier profile — what integration tests verify,
their cost characteristics, and when to prefer them. This section defines the
**how** — test database setup, isolation strategies, environment configuration,
and the cross-references to domain-specific patterns.

> **Critical boundary reminder:** This section covers the **strategy** of
> integration testing. The **recipes** live in the domain documents:
> - API route testing → See [03-api-design.md, § 13.3–13.4]
> - Database testing → See [04-database-standards.md, § 13.2–13.7]
> - Component+hook testing → See [05-frontend-standards.md, § 2–3]

---

### 4.1 Test Database Setup

Integration tests that touch the database **MUST** use a real test database —
never mocks, and never the development or production database.

#### Supabase Local (Default)

The Supabase CLI runs a full local stack via Docker. This is the default
approach for all projects using Supabase.

```bash
# Start the local Supabase stack (first run downloads Docker images)
npx supabase start

# Output includes local credentials:
# API URL:    http://localhost:54321
# DB URL:     postgresql://postgres:postgres@localhost:54322/postgres
# Studio URL: http://localhost:54323
# Anon key:   eyJ...
# Service key: eyJ...

# Reset database: reapplies all migrations + seed data
npx supabase db reset
```

| Service | Default Port | Purpose |
|---|---|---|
| Supabase API (PostgREST) | 54321 | API access to the database |
| PostgreSQL | 54322 | Direct database connection |
| Studio | 54323 | Visual database management |
| Mailpit (email capture) | 54324 | Captures emails from Auth (never sends real emails) |

> For detailed Supabase local setup, Docker requirements, and `config.toml`
> customization: → See [04-database-standards.md, § 13.2 — Test Database Setup].

#### Rules

- **MUST** use a dedicated test database — never run tests against development
  or production data
- **MUST** run `npx supabase db reset` before integration test suites to
  ensure a known baseline (migrations applied + seed data loaded)
- **MUST** include `supabase start` as a prerequisite in the project README
  and CI setup
- **SHOULD** use the local Supabase stack for integration tests — it provides
  the same PostgreSQL, Auth, RLS, and PostgREST behavior as production
- **SHOULD** configure test scripts to check that Supabase is running before
  executing tests — fail fast with a clear message instead of cryptic
  connection errors

---

### 4.2 Test Isolation Strategies

Each test should produce the same result regardless of which tests ran before
it. With a real database, this requires an explicit isolation strategy.

| Strategy | How it works | Speed | Best for |
|---|---|---|---|
| **Transaction rollback** | Wrap each test in a transaction; rollback in `afterEach` | ⚡ Fast | Most integration tests — read/write operations on existing data |
| **Truncate + reseed** | Clear all tables; insert baseline data in `beforeAll` or `beforeEach` | 🏃 Moderate | Test suites that depend on specific data states or test deletions |
| **Database reset** | Run `npx supabase db reset` before the suite | 🐢 Slow | Migration testing, destructive schema changes |

> **Supabase-specific note:** Application-level tests using the Supabase client
> (PostgREST) **cannot** use database transactions for isolation, because each
> API request is a separate connection with its own transaction. For
> Supabase client tests, use truncate + reseed.
>
> Direct PostgreSQL connection tests (via `pg` or Prisma) **can** use
> transaction rollback for isolation.

#### Rules

- **MUST** ensure test isolation — each test starts with a known state
- **SHOULD** prefer transaction rollback for speed when the database driver
  supports it (direct PostgreSQL connections)
- **SHOULD** use truncate + reseed for Supabase client integration tests
- **MAY** use database reset (`supabase db reset`) for migration testing,
  but not for every test suite — it is too slow
- **MUST NOT** rely on test execution order — tests must pass when run
  individually, in any order, or in parallel

---

### 4.3 Test Environment Configuration

```bash
# .env.test — loaded when NODE_ENV=test
# Local Supabase stack credentials (from `supabase start` output)
DATABASE_URL=postgresql://postgres:postgres@localhost:54322/postgres
SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=<your-local-anon-key>
SUPABASE_SERVICE_ROLE_KEY=<your-local-service-role-key>

# Disable external services — tests must not call real providers
SMTP_ENABLED=false
STRIPE_ENABLED=false
ANALYTICS_ENABLED=false

# Test-specific settings
LOG_LEVEL=silent
NODE_ENV=test
```

#### Rules

- **MUST** use a separate `.env.test` file — never share environment variables
  with development or production
- **MUST** disable all external service integrations (email, payment,
  analytics, SMS) — tests must be hermetic
- **MUST NOT** use real API keys, tokens, or secrets in `.env.test` — use
  local-only credentials from `supabase start`
- **MUST NOT** commit `.env.test` with real secrets to version control — add
  it to `.gitignore` and provide a `.env.test.example` template
- **SHOULD** set `LOG_LEVEL=silent` to keep test output clean — enable verbose
  logging only when debugging a specific test

---

### 4.4 Integration Testing Patterns by Domain

This section serves as a routing table — it points you to the right domain
document for each integration testing scenario.

#### API Route Testing (Vitest + Supertest)

Tests the full HTTP request/response cycle: routing → validation →
authentication → service logic → database → response formatting.

- Setup: `request(app).post('/api/v1/users').send(input).expect(201)`
- Verify both status code AND response body structure (envelope)
- Test happy path, validation errors, auth failures, and conflicts

→ **Complete patterns, setup code, and checklist:**
[03-api-design.md, § 13 — API Testing Patterns]

#### Database Testing (Vitest + Supabase Local)

Tests RLS policies, constraints, migrations, repository queries, and
soft delete behavior against a real PostgreSQL instance.

- Use dedicated test database via `supabase start`
- Test both authorized and unauthorized access for RLS
- Verify constraint violations produce expected errors

→ **Complete patterns, RLS testing, constraint testing:**
[04-database-standards.md, § 13 — Database Testing Patterns]

#### Component + Hook Testing (Vitest + Testing Library)

Tests that React components render correctly with data from hooks,
handle loading/error states, and respond to user interaction.

- Render components with Testing Library
- Use `renderHook` for custom hook testing
- Query by accessible roles (`getByRole`, `getByLabel`)

→ **Complete patterns, hook testing, query priority:**
[05-frontend-standards.md, § 2–3]

---

### 4.5 Anti-Patterns

| Anti-Pattern | Why it is bad | What to do instead |
|---|---|---|
| **Sharing database state between tests** | Order-dependent; one test's setup pollutes another | Isolate with transactions or truncate + reseed |
| **Using production database for tests** | Data corruption risk; inconsistent results | Use local Supabase (`supabase start`) |
| **Mocking the database in integration tests** | Defeats the purpose — you are testing the integration | Use a real test database |
| **Not cleaning up after tests** | Accumulated data causes flaky tests | Use `afterEach` / `afterAll` cleanup hooks |
| **Testing implementation via SQL assertions** | Fragile — breaks when query optimization changes | Test through the public interface (API response, service return) |
| **Hardcoding test data inline** | Duplication, inconsistency, hard to maintain | Use factories (→ Section 6) |
| **Testing against remote Supabase in CI** | Slow, flaky, costs money, shared state between CI runs | Use `supabase start` in CI with `supabase db reset` |

---

## 5. E2E Testing Standards

§ 2.4 defined the E2E tier profile — what E2E tests verify, their cost, and
when to prefer them. This section defines the **how** — shared Playwright
configuration, Page Object Model structure, test data management, flaky test
handling, and cross-browser strategy.

> For frontend-specific E2E patterns (form testing, navigation testing,
> component interaction patterns): → See [05-frontend-standards.md, § 4].

---

### 5.1 Playwright Configuration (Shared Baseline)

All projects **MUST** use this baseline configuration, extending or overriding
only when justified:

```ts
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  // --- Test directory ---
  testDir: './tests/e2e',
  testMatch: '**/*.spec.ts',

  // --- Execution ---
  fullyParallel: true,
  forbidOnly: !!process.env.CI,      // Fail CI if .only is left in code
  retries: process.env.CI ? 2 : 0,   // Retry flaky tests in CI only
  workers: process.env.CI ? 1 : undefined, // Sequential in CI for stability

  // --- Timeouts ---
  timeout: 30_000,                    // Per-test timeout (30s)
  expect: {
    timeout: 5_000,                   // Per-assertion timeout (5s)
  },

  // --- Reporting ---
  reporter: process.env.CI
    ? [['html', { open: 'never' }], ['json', { outputFile: 'test-results.json' }]]
    : [['html', { open: 'on-failure' }]],

  // --- Global settings ---
  use: {
    baseURL: process.env.BASE_URL || 'http://localhost:3000',
    trace: 'on-first-retry',          // Capture trace on failure for debugging
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },

  // --- Browser projects ---
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    // Add when cross-browser support is required:
    // { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    // { name: 'webkit', use: { ...devices['Desktop Safari'] } },
    // { name: 'mobile-chrome', use: { ...devices['Pixel 7'] } },
  ],

  // --- Dev server (auto-start for local runs) ---
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    // Playwright 1.57+ supports `wait` — a regex matched against stdout/stderr
    // to detect when the server is ready, instead of polling the URL:
    // wait: /ready on http:\/\/localhost:3000/,
  },
});
```

> **Playwright 1.57+ note:** Playwright now runs on **Chrome for Testing**
> builds instead of Chromium. For most projects this is transparent, but it
> means the browser in headed mode shows the Chrome icon and title. On Arm64
> Linux, Playwright continues to use Chromium.

#### Configuration Rules

- **MUST** keep E2E tests in a dedicated `tests/e2e/` directory
- **MUST** set `forbidOnly: !!process.env.CI` — a forgotten `.only` silently
  skips all other tests
- **MUST** enable `trace: 'on-first-retry'` — traces are invaluable for
  debugging CI failures. Use Playwright's Trace Viewer to inspect DOM
  snapshots, network requests, and console logs for failed tests.
- **SHOULD** start with Chromium only — add Firefox and WebKit when there is
  evidence of cross-browser issues (analytics, bug reports)
- **SHOULD** use `retries: 2` in CI as a safety net for transient failures,
  not as a fix for flaky tests
- **SHOULD** use `workers: 1` in CI for predictability — parallel E2E tests
  can conflict on shared resources (database state, ports)

#### npm Scripts (Standard)

```json
{
  "scripts": {
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "test:e2e:debug": "playwright test --debug",
    "test:e2e:codegen": "playwright codegen http://localhost:3000"
  }
}
```

| Script | Purpose | When to use |
|---|---|---|
| `test:e2e` | Run all E2E tests headless | CI, pre-release verification |
| `test:e2e:ui` | Interactive UI Mode — browse, run, debug tests visually | Development, debugging |
| `test:e2e:debug` | Step-through debugging with Playwright Inspector | Investigating a specific failure |
| `test:e2e:codegen` | Record browser interactions to generate test code | Bootstrapping new tests quickly |

---

### 5.2 Page Object Model Pattern

The Page Object Model (POM) encapsulates page-specific selectors and
actions into reusable classes. The test file describes **what** happens;
the Page Object describes **how** it happens on that page.

```ts
// tests/e2e/pages/login.page.ts
import { type Page, type Locator } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.getByLabel('Email');
    this.passwordInput = page.getByLabel('Password');
    this.submitButton = page.getByRole('button', { name: 'Sign in' });
    this.errorMessage = page.getByRole('alert');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
}
```

```ts
// tests/e2e/auth-flow.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from './pages/login.page';

test.describe('Authentication Flow', () => {
  test('redirects to dashboard after successful login', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();

    await loginPage.login('user@example.com', 'validPassword123');

    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible();
  });

  test('shows error for invalid credentials', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await loginPage.goto();

    await loginPage.login('user@example.com', 'wrongPassword');

    await expect(loginPage.errorMessage).toBeVisible();
    await expect(loginPage.errorMessage).toContainText('Invalid credentials');
  });
});
```

#### Advanced: POM with Playwright Fixtures

For larger test suites, Playwright fixtures eliminate repetitive Page Object
instantiation:

```ts
// tests/e2e/fixtures.ts
import { test as base } from '@playwright/test';
import { LoginPage } from './pages/login.page';
import { DashboardPage } from './pages/dashboard.page';

type TestFixtures = {
  loginPage: LoginPage;
  dashboardPage: DashboardPage;
};

export const test = base.extend<TestFixtures>({
  loginPage: async ({ page }, use) => {
    await use(new LoginPage(page));
  },
  dashboardPage: async ({ page }, use) => {
    await use(new DashboardPage(page));
  },
});

export { expect } from '@playwright/test';
```

```ts
// tests/e2e/auth-flow.spec.ts — cleaner with fixtures
import { test, expect } from './fixtures';

test('redirects to dashboard after successful login', async ({ loginPage, dashboardPage }) => {
  await loginPage.goto();
  await loginPage.login('user@example.com', 'validPassword123');
  await expect(dashboardPage.heading).toBeVisible();
});
```

#### POM Rules

- **SHOULD** use the Page Object Model for all E2E test suites
- **MUST** use accessible locators in Page Objects: `getByRole` → `getByLabel`
  → `getByText` → `getByTestId` (last resort)
  (→ See [02-technology-radar.md — Testing Library] for query priority)
- **MUST NOT** use CSS selectors (`.class-name`, `#id`) or XPath in Page
  Objects — they break on styling changes and provide no accessibility value
- **SHOULD** encapsulate multi-step actions (login, checkout, form submission)
  as methods on the Page Object
- **SHOULD** keep assertions in the test file, not in the Page Object — the
  POM handles interaction, the test handles verification
- **MAY** use Playwright fixtures for large suites with many Page Objects —
  they reduce boilerplate and improve readability

---

### 5.3 Test Data Management for E2E

E2E tests need data in the database to exercise the full stack. Unlike
integration tests (which can use transaction rollback), E2E tests operate
through the browser and cannot directly manage database transactions.

#### Strategies

| Strategy | How | When to use |
|---|---|---|
| **API seeding** | Use the application's API (or Supabase client) to create test data in `test.beforeEach` | Default — fastest, most realistic |
| **SQL seeding** | Run seed scripts directly against the test database before the suite | Complex data dependencies; migration testing |
| **UI seeding** | Create data through the UI (fill forms, submit) | Avoid — slow, fragile, use only when testing the creation flow itself |

```ts
// API seeding example — create test data before E2E tests
import { test } from '@playwright/test';
import { createClient } from '@supabase/supabase-js';

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!, // Service role for setup only
);

test.beforeEach(async () => {
  // Clean slate
  await supabase.from('orders').delete().neq('id', '');
  // Seed test data
  await supabase.from('users').upsert({
    id: 'test-user-uuid',
    email: 'e2e-user@example.com',
    name: 'E2E Test User',
  });
});
```

- **MUST** set up test data explicitly — never depend on data from other tests
- **MUST NOT** use real user data (PII) in E2E tests
- **SHOULD** prefer API seeding over UI seeding — it is faster and more stable
- **SHOULD** clean up test data in `afterEach` or `beforeEach` to prevent
  accumulation

---

### 5.4 Handling Flaky Tests

A flaky test sometimes passes and sometimes fails with the same code. Flaky
E2E tests are the most common and the most dangerous — they erode trust in
the entire suite.

#### Common Sources and Mitigations

| Source | Symptom | Mitigation |
|---|---|---|
| **Timing / race conditions** | Element not found, click intercepted | Use Playwright's auto-waiting; use `expect().toBeVisible()` before interacting |
| **Shared database state** | Test passes alone, fails in suite | Isolate data per test; clean up in `beforeEach` |
| **Animations / transitions** | Click hits wrong element; assertion too early | Disable CSS animations in test env or use `page.waitForLoadState('networkidle')` sparingly |
| **Network latency** | API calls timeout intermittently | Use `retries: 2` in CI as safety net; investigate root cause |
| **Date/time sensitivity** | Test fails at midnight or month boundary | Mock time at the application level or use fixed test dates |

#### The Quarantine Protocol

When a flaky test is identified:

1. **Tag it immediately** — add `test.fixme()` or move to a `*.flaky.spec.ts` file
2. **File a ticket** — with the failure pattern, frequency, and suspected cause
3. **Fix within the sprint** — quarantine is temporary, not permanent
4. **Restore and monitor** — move back to the main suite; watch for recurrence

- **MUST** fix flaky tests immediately — do not let them accumulate
- **MUST NOT** increase `retries` as a permanent fix — retries mask the root cause
- **MUST NOT** delete a test because it is flaky — flakiness is a test bug,
  not a reason to remove coverage
- **SHOULD** use Playwright's Trace Viewer to diagnose flaky failures — traces
  show the exact DOM state, network requests, and console output at the moment
  of failure

---

### 5.5 Cross-Browser Testing Strategy

Not every project needs cross-browser E2E tests. The decision depends on the
user base and the cost-benefit analysis.

| Tier | Browsers | When to use | Run frequency |
|---|---|---|---|
| **Default** | Chromium only | All projects | Every PR |
| **Extended** | Chromium + Firefox | User analytics show Firefox usage > 5% | Nightly or weekly |
| **Full** | Chromium + Firefox + WebKit | Public-facing apps, diverse user base, compliance | Nightly |
| **Mobile** | + Pixel 7, iPhone 14 viewports | Mobile-first apps, mobile traffic > 30% | Nightly or weekly |

- **SHOULD** start with Chromium only and expand based on evidence
- **SHOULD** run multi-browser tests on a schedule (nightly) rather than on
  every PR — they are slow and rarely catch PR-specific issues
- **MAY** run a reduced suite (smoke tests only) across all browsers, and
  the full suite on Chromium only

---

### 5.6 Anti-Patterns

| Anti-Pattern | Why it is bad | What to do instead |
|---|---|---|
| **Using `page.waitForTimeout()`** | Arbitrary waits are slow and still flaky | Use Playwright's auto-waiting or `expect().toBeVisible()` |
| **Testing every CRUD operation** | Extremely slow, high maintenance | Test CRUD at integration tier; E2E for critical flows only |
| **CSS/XPath selectors** | Break on styling changes; no a11y value | Use `getByRole`, `getByLabel`, `data-testid` (last resort) |
| **No trace/screenshot on failure** | Debugging CI failures is guesswork | Enable `trace: 'on-first-retry'` and `screenshot: 'only-on-failure'` |
| **Tests depending on execution order** | Fragile, impossible to run in isolation | Each test seeds its own data |
| **Hardcoding URLs** | Tests break when routes change | Use `baseURL` config and relative paths |
| **Testing third-party UIs** | Testing code you do not own | Mock or skip; test your integration only |
| **No POM pattern** | Selectors scattered across test files | Encapsulate in Page Object classes |

---

## 6. Test Data Management

Test data is the invisible backbone of every test suite. Poor test data
management — hardcoded strings, duplicated objects, shared mutable state —
leads to brittle tests that break for the wrong reasons and pass for the
wrong reasons.

This section defines the factory pattern, seed data strategy, isolation
rules, and sensitive data handling. Domain-specific factories (API request
factories, database record factories) live in the domain documents; this
section defines the **pattern** they all follow.

> For domain-specific factory examples:
> → See [03-api-design.md, § 13.6 — Test Data & Isolation]
> → See [04-database-standards.md, § 13.3 — Test Data Factories]

---

### 6.1 The Factory Pattern

A factory is a function that generates a valid test entity with sensible
defaults. Each test overrides only the fields relevant to its assertion —
everything else gets a realistic default from Faker.

> `@faker-js/faker` is ✅ Adopt in the Technology Radar
> (→ See [02-technology-radar.md, § 4.11]).
> Current stable version: **10.x** (requires Node.js ≥ 20).

#### Basic Factory

```ts
// tests/factories/user.factory.ts
import { faker } from '@faker-js/faker';

interface CreateUserInput {
  name?: string;
  email?: string;
  role?: 'user' | 'admin';
  isActive?: boolean;
}

interface User {
  id: string;
  name: string;
  email: string;
  role: 'user' | 'admin';
  isActive: boolean;
  createdAt: Date;
}

/**
 * Creates a valid User with realistic defaults.
 * Override only the fields relevant to your test.
 */
export function createFakeUser(overrides: CreateUserInput = {}): User {
  return {
    id: faker.string.uuid(),
    name: overrides.name ?? faker.person.fullName(),
    email: overrides.email ?? faker.internet.email(),
    role: overrides.role ?? 'user',
    isActive: overrides.isActive ?? true,
    createdAt: new Date(),
  };
}
```

#### Usage in Tests

```ts
// Test only cares about the role — everything else is a realistic default
it('returns 403 when a regular user accesses admin endpoint', async () => {
  const user = createFakeUser({ role: 'user' });
  // ... test with this user
});

// Test only cares about the active flag
it('excludes inactive users from the listing', async () => {
  const active = createFakeUser({ isActive: true });
  const inactive = createFakeUser({ isActive: false });
  // ... seed both, assert only active is returned
});

// Test needs multiple users — each call generates unique data
it('returns all users matching the search query', async () => {
  const users = Array.from({ length: 5 }, () => createFakeUser());
  // ... seed all, search, assert count
});
```

#### Generating Multiple Entities

For bulk creation, use `faker.helpers.multiple` or simple array generation:

```ts
// Using faker.helpers.multiple
const users = faker.helpers.multiple(
  () => createFakeUser({ role: 'user' }),
  { count: 10 },
);

// Using Array.from (when you need the index)
const orders = Array.from({ length: 5 }, (_, i) =>
  createFakeOrder({ sequenceNumber: i + 1 }),
);
```

#### Composing Factories (Related Entities)

When entities have relationships, compose factories to maintain referential
integrity:

```ts
// tests/factories/order.factory.ts
import { faker } from '@faker-js/faker';
import { createFakeUser } from './user.factory';

interface CreateOrderInput {
  userId?: string;
  status?: 'pending' | 'confirmed' | 'shipped';
  totalCents?: number;
}

export function createFakeOrder(overrides: CreateOrderInput = {}) {
  return {
    id: faker.string.uuid(),
    userId: overrides.userId ?? createFakeUser().id,
    status: overrides.status ?? 'pending',
    totalCents: overrides.totalCents ?? faker.number.int({ min: 500, max: 50000 }),
    createdAt: new Date(),
  };
}

// Usage — test needs a user with their orders
it('returns orders belonging to the user', async () => {
  const user = createFakeUser();
  const order1 = createFakeOrder({ userId: user.id });
  const order2 = createFakeOrder({ userId: user.id });
  // ... seed user and orders, query, assert
});
```

#### Factory Rules

- **MUST** create factory functions for every domain entity used in tests
- **MUST** generate valid data by default — a factory call with no arguments
  should produce a valid, insertable entity
- **MUST** use `@faker-js/faker` for realistic data — not hardcoded strings
  like `"John Doe"` or `"test@test.com"`
- **MUST** install Faker as a dev dependency only — it must never reach
  production bundles
- **SHOULD** accept partial overrides via a single options object so tests
  specify only what they care about
- **SHOULD** store factories in `tests/factories/` or co-locate with the
  entity module
- **SHOULD** use `faker.seed()` when tests require deterministic,
  reproducible output (snapshot tests, specific value assertions)
- **MAY** use locale-specific Faker for region-appropriate data:

```ts
import { fakerPT_PT as faker } from '@faker-js/faker';
// Generates Portuguese names, addresses, phone numbers
const name = faker.person.fullName(); // e.g. "Maria Fernanda Oliveira"
```

---

### 6.2 Seed Data Strategy

Seed data provides a baseline state for development and testing environments.
There are different seed types for different purposes:

| Seed Type | Purpose | Characteristics | When to run |
|---|---|---|---|
| **Development seeds** | Provide a rich, realistic dataset for local dev | Many records, varied data, covers many UI states | On `supabase db reset` or `npm run db:seed` |
| **Test seeds** | Provide minimal, predictable data for integration tests | Few records, deterministic, only what tests need | In `beforeAll` / `beforeEach` of test suites |
| **E2E seeds** | Provide the exact state for E2E scenarios | Specific users with known credentials, specific records for specific flows | Before E2E suite (via API or script) |

#### Development Seeds

```sql
-- supabase/seed.sql — loaded by `supabase db reset`
-- Idempotent: uses INSERT ... ON CONFLICT DO NOTHING

INSERT INTO users (id, name, email, role)
VALUES
  ('dev-admin-uuid', 'Admin Dev', 'admin@dev.local', 'admin'),
  ('dev-user-uuid', 'User Dev', 'user@dev.local', 'user')
ON CONFLICT (id) DO NOTHING;
```

#### Test Seeds (via Factories)

```ts
// tests/helpers/seed.ts
import { createFakeUser } from '../factories/user.factory';
import { supabaseAdmin } from './supabase-test-client';

export async function seedTestUsers(count = 3) {
  const users = Array.from({ length: count }, () => createFakeUser());
  const { error } = await supabaseAdmin.from('users').insert(users);
  if (error) throw new Error(`Seed failed: ${error.message}`);
  return users;
}

export async function cleanupTestData() {
  // Delete in reverse dependency order
  await supabaseAdmin.from('orders').delete().neq('id', '');
  await supabaseAdmin.from('users').delete().neq('id', '');
}
```

#### Rules

- **MUST** keep seeds idempotent — running them twice produces the same state
- **MUST** separate development seeds from test seeds — dev seeds are rich;
  test seeds are minimal
- **SHOULD** create E2E test data via the API rather than direct DB inserts —
  this exercises the full stack and catches integration bugs
- **MUST NOT** include real user data (PII) in any seed file

---

### 6.3 Test Isolation

Every test must be independent — same result regardless of execution order
or which other tests ran before it.

- **MUST** reset relevant state before or after each test
- **MUST NOT** share mutable state between test files
- **SHOULD** use `beforeEach` for setup and `afterEach` for cleanup within
  a file
- **SHOULD** prefer creating new data (via factories) over modifying shared
  data — fresh data per test eliminates coupling

```ts
describe('OrderService', () => {
  let testUser: User;

  // Fresh user per test — no coupling between tests
  beforeEach(async () => {
    testUser = createFakeUser();
    await insertUser(testUser);
  });

  afterEach(async () => {
    await cleanupTestData();
  });

  it('creates an order for the user', async () => {
    const order = await orderService.create({
      userId: testUser.id,
      items: [createFakeOrderItem()],
    });
    expect(order.userId).toBe(testUser.id);
  });

  it('rejects orders for inactive users', async () => {
    await deactivateUser(testUser.id);
    await expect(
      orderService.create({ userId: testUser.id, items: [] }),
    ).rejects.toThrow('User is inactive');
  });
});
```

---

### 6.4 Sensitive Data in Tests

- **MUST NOT** use real personal data (names, emails, phone numbers, NIF,
  addresses) in tests — use Faker.js
- **MUST NOT** commit real API keys, tokens, or secrets in test files or
  `.env.test`
- **MUST** use placeholder or local-only credentials (Supabase local keys
  from `supabase start`)
- **SHOULD** use `faker.helpers.fake()` or locale-specific Faker for
  region-appropriate data (Portuguese names, PT phone numbers)

> → See [07-security-standards.md] for RGPD compliance requirements.
> → See [07-security-standards.md, § 13] for security-specific test data.

---

### 6.5 Anti-Patterns

| Anti-Pattern | Why it is bad | What to do instead |
|---|---|---|
| **Hardcoded `"test@test.com"` everywhere** | Not realistic; no uniqueness; hides email-format edge cases | Use `faker.internet.email()` |
| **Sharing one entity across tests** | Mutation in one test affects another | Fresh factory data per test |
| **Giant seed files** | Slow to load; most tests need a fraction of the data | Minimal seeds + factories for test-specific data |
| **Real PII in test data** | RGPD legal risk; ethical concern; leaks into CI logs | Use Faker.js exclusively |
| **No cleanup after tests** | Accumulated data causes flakiness and slowness | Transaction rollback or truncate + reseed |
| **Copy-pasting test objects** | One schema change requires updating dozens of files | Central factory with defaults |

---

## 7. Mocking & Test Doubles

Mocking is powerful and dangerous. Used correctly, it isolates the code under
test from external dependencies. Used incorrectly, it creates tests that pass
even when the system is broken — because the tests are verifying the mocks, not
the real code.

§ 3.5 covered mocking at the unit level (what to mock, `vi.mock()` basics).
This section defines the **complete mocking philosophy** — when to mock, when
NOT to mock, the test doubles taxonomy, MSW for network-level mocking, and
`vi.hoisted()` patterns for Vitest 4.

---

### 7.1 The Golden Rule: Mock at Boundaries, Not Internals

```text
YOUR CODE                         EXTERNAL WORLD
┌──────────────────────┐         ┌────────────────────┐
│                      │         │                    │
│  Service Logic       │         │  Database          │  ← mock in unit tests,
│  Business Rules      │  ────►  │  External APIs     │    real in integration
│  Utilities           │         │  File System       │
│  Components          │         │  Time / Randomness │  ← mock always
│  Hooks               │         │  Email / SMS       │  ← mock always
│                      │         │  Payment providers │  ← mock always
│  (DO NOT MOCK)       │         │  (MOCK THESE)      │
└──────────────────────┘         └────────────────────┘
```

The boundary is the point where **your code** meets **the outside world**.
Mock at that point — not deeper inside your own code.

- **MUST** mock external services (Stripe, SendGrid, etc.) — tests must not
  depend on external availability, cost money, or send real emails
- **MUST** mock time and randomness when test results depend on them
- **SHOULD** mock at the **boundary** (the function that calls the external
  system), not deep inside your code
- **MUST NOT** mock your own code to test your own code — if you need to mock
  `ServiceA` to test `ServiceB`, the coupling is too tight. Refactor.
- **MUST NOT** mock the database in integration tests — the purpose is to
  verify the real interaction (→ See [Section 4])

---

### 7.2 Test Doubles Taxonomy

Different test situations require different types of fakes. Using the right
one makes tests clearer and more maintainable:

| Double | What it does | When to use | Example |
|---|---|---|---|
| **Stub** | Returns a fixed value; does not track calls | External service that returns data | API that returns a price list |
| **Mock** | Records calls; allows assertions on invocations | Verify a side effect occurred | Email was sent, event was emitted |
| **Spy** | Wraps the real function; calls original but records | Observe without changing behavior | Verify `console.error` was called |
| **Fake** | A simplified but working implementation | When a real implementation is too slow or complex | In-memory database, fake email transport |

```ts
// STUB — returns fixed data, no tracking
vi.spyOn(priceService, 'getRate').mockResolvedValue(1.23);

// MOCK — verify it was called with correct arguments
const sendEmail = vi.fn();
await notifyUser(user, sendEmail);
expect(sendEmail).toHaveBeenCalledWith(
  user.email,
  expect.stringContaining('Welcome'),
);

// SPY — observe without changing behavior
const consoleSpy = vi.spyOn(console, 'error');
await processOrder(invalidOrder);
expect(consoleSpy).toHaveBeenCalled();
consoleSpy.mockRestore(); // Restore original

// FAKE — simplified real implementation
class FakeEmailTransport implements EmailTransport {
  readonly sentEmails: Array<{ to: string; body: string }> = [];
  async send(to: string, body: string) {
    this.sentEmails.push({ to, body });
  }
}
```

#### Choosing the Right Double

```text
Do I need to verify the function was called?
├── NO → Do I need controlled return values?
│   ├── YES → STUB (mockReturnValue / mockResolvedValue)
│   └── NO → You probably don't need a double at all
│
└── YES → Do I need the original behavior to run?
    ├── YES → SPY (vi.spyOn without mockImplementation)
    └── NO → MOCK (vi.fn() or vi.spyOn with mockImplementation)
```

---

### 7.3 MSW for Network-Level Mocking

MSW (Mock Service Worker) intercepts HTTP requests at the network level —
your application code does not know it is being mocked. This is the preferred
approach for mocking API responses in frontend tests because it tests the
real `fetch` / `axios` / `ky` calls, including headers, serialization, and
error handling.

> MSW is 🔬 Trial in the Technology Radar
> (→ See [02-technology-radar.md, § 4.11]).
> Current version: **2.x** (2.12.x). Uses Fetch API primitives.

#### Setup

```ts
// src/mocks/handlers.ts — shared mock definitions
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/v1/users/:id', ({ params }) => {
    return HttpResponse.json({
      ok: true,
      data: {
        id: params.id,
        name: 'Maria Silva',
        email: 'maria@example.com',
        role: 'user',
      },
    });
  }),

  http.post('/api/v1/users', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json(
      { ok: true, data: { id: 'new-uuid', ...body } },
      { status: 201 },
    );
  }),
];
```

```ts
// src/mocks/node.ts — Vitest integration (Node.js process)
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);
```

```ts
// vitest.setup.ts — enable MSW before all tests
import { beforeAll, afterEach, afterAll } from 'vitest';
import { server } from './src/mocks/node';

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

#### Per-Test Overrides

Override a handler for a single test without affecting others:

```ts
import { server } from '@/mocks/node';
import { http, HttpResponse } from 'msw';

it('shows error message when API returns 500', async () => {
  // Override the default handler for this test only
  server.use(
    http.get('/api/v1/users/:id', () => {
      return HttpResponse.json(
        { ok: false, error: { code: 'INTERNAL_ERROR', message: 'Server error' } },
        { status: 500 },
      );
    }),
  );

  // server.resetHandlers() in afterEach restores the default
  render(<UserProfile userId="abc-123" />);
  await expect(screen.findByRole('alert')).resolves.toBeInTheDocument();
});
```

#### MSW Rules

- **SHOULD** use MSW for frontend tests that fetch data — more realistic than
  mocking `fetch` directly
- **MUST** set `onUnhandledRequest: 'error'` — catches accidental unmocked
  requests that would silently hit a real server or hang indefinitely
- **MUST** call `server.resetHandlers()` in `afterEach` — prevents per-test
  overrides from leaking
- **SHOULD** keep shared handlers in `src/mocks/handlers.ts` and use
  `server.use()` for per-test overrides
- **SHOULD** use the same response envelope format as the real API
  (→ See [03-api-design.md, § 4]) — MSW mocks should be realistic

---

### 7.4 `vi.mock()` and `vi.hoisted()` in Vitest 4

`vi.mock()` replaces an entire module's exports. It is **hoisted** to the top
of the file automatically — regardless of where you write it, it executes
before all imports.

#### The Hoisting Problem

Because `vi.mock()` is hoisted, you cannot reference variables defined in the
same file scope:

```ts
// ❌ BROKEN — myValue is not yet defined when vi.mock runs
const myValue = 'hello';
vi.mock('./module', () => ({
  getValue: () => myValue, // ReferenceError: myValue is not defined
}));
```

#### The Solution: `vi.hoisted()`

`vi.hoisted()` lifts variable declarations alongside the mock:

```ts
// ✅ CORRECT — vi.hoisted runs at the same time as vi.mock
const mocks = vi.hoisted(() => ({
  sendEmail: vi.fn(),
  generateId: vi.fn(() => 'fixed-uuid'),
}));

vi.mock('@/lib/email', () => ({
  sendEmail: mocks.sendEmail,
}));

vi.mock('@/lib/id', () => ({
  generateId: mocks.generateId,
}));

it('sends welcome email with the generated ID', async () => {
  mocks.sendEmail.mockResolvedValue({ success: true });

  await createUser(validInput);

  expect(mocks.sendEmail).toHaveBeenCalledWith(
    validInput.email,
    expect.stringContaining('fixed-uuid'),
  );
});
```

#### Type-Safe Dynamic Import Syntax

Vitest 4 supports `vi.mock(import('./module'))` for type-checked factories:

```ts
vi.mock(import('@/lib/email'), () => ({
  sendEmail: vi.fn().mockResolvedValue({ success: true }),
}));
// TypeScript validates that the factory returns the correct shape
```

#### Rules

- **MUST** keep `vi.mock()` at the top level of the file — never inside
  `describe`, `it`, or `beforeEach`
- **MUST** use `vi.hoisted()` when the mock factory references variables —
  do not rely on the implicit hoisting of `const`
- **SHOULD** prefer `vi.mock(import('./module'))` for type safety
- **SHOULD** prefer dependency injection over `vi.mock()` when possible
  (→ See [§ 3.5] for the DI pattern)
- **MUST NOT** over-mock — if you are mocking 5+ modules to test one function,
  the function has too many dependencies. Refactor first.

---

### 7.5 When NOT to Mock

Knowing when **not** to mock is as important as knowing when to mock:

| Scenario | Why you should NOT mock | What to do instead |
|---|---|---|
| **Database in integration tests** | You are testing the integration; mocking defeats the purpose | Use a real test database (→ Section 4.1) |
| **Your own services** | Tests pass but real interactions are broken | Refactor for loose coupling; test through the public interface |
| **The function you are testing** | You are testing the mock, not your code | Test the real function with controlled inputs |
| **Standard library functions** | They are already tested; mocking adds fragility | Use real `Array`, `Date`, `JSON` — only mock `Date.now()` for time control |
| **Simple adapters** | The adapter is trivial; mocking adds more code than testing the real thing | Test the adapter with real inputs |

---

### 7.6 Anti-Patterns

| Anti-Pattern | Why it is bad | What to do instead |
|---|---|---|
| **Mocking everything** | Tests pass with broken integrations | Mock only external boundaries |
| **Mocking the DB in integration tests** | Defeats the purpose | Use real test database |
| **Testing that mock was called, not the outcome** | Testing the test, not the code | Assert on observable output |
| **Not restoring mocks** | Leaks between tests; mysterious failures | Set `restoreMocks: true` in Vitest config |
| **Mocking `fetch` directly** | Misses headers, serialization, error handling | Use MSW at the network level |
| **Complex mock chains** | Hard to read, maintain, often wrong | Simplify code under test or use a fake |
| **Mock assertions without behavior assertions** | Proves the code ran, not that it worked | Always assert on the result, not just the call |

---

## 8. CI/CD Integration

A test suite is only as valuable as its enforcement. Tests that developers can
skip, ignore, or bypass provide zero value. CI quality gates make testing
non-negotiable — every PR must pass every gate before merging.

This section defines the quality gate pipeline, a baseline GitHub Actions
configuration, and the rules for merge blocking. The complete CI/CD pipeline
(Docker, deployments, environments) will live in → See [09-devops-cicd.md] — this
section covers only the testing-related gates.

---

### 8.1 Quality Gate Pipeline

Tests run as part of a sequential quality gate pipeline. Each stage is cheaper
than the next — failing early saves CI time and gives faster feedback.

```text
┌─────────┐   ┌────────────┐   ┌───────────┐   ┌──────────┐   ┌─────────┐
│  Lint   │──►│ Typecheck  │──►│   Test    │──►│ Coverage │──►│  Build  │
│ ESLint  │   │tsc --noEmit│   │  Vitest   │   │  Report  │   │  next   │
│         │   │            │   │  run      │   │          │   │  build  │
└─────────┘   └────────────┘   └───────────┘   └──────────┘   └─────────┘
  ~10s           ~15s             ~30-120s        ~5s            ~60-120s
  Fail fast     Fail fast        Fail if any    Warn if       Fail if
  on style     on type errors   test fails     below target  build breaks
```

- **MUST** run gates in this order: lint → typecheck → test → build
- **MUST** block merge if any gate fails — no exceptions without an ADR
- **SHOULD** run E2E tests as a separate job (after quality gates) — they are
  slower and may need a running application
- **SHOULD** treat coverage as a warning, not a hard gate, unless the project
  is mature (→ See [Section 9])

---

### 8.2 GitHub Actions Configuration (Baseline)

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true    # New push to same PR cancels previous run

jobs:
  quality-gates:
    name: Quality Gates
    runs-on: ubuntu-latest
    timeout-minutes: 15

    steps:
      - uses: actions/checkout@v6

      - uses: actions/setup-node@v6
        with:
          node-version: 22
          cache: 'npm'

      - run: npm ci

      # Gate 1: Lint
      - name: Lint
        run: npm run lint

      # Gate 2: Type check
      - name: Type Check
        run: npx tsc --noEmit

      # Gate 3: Unit & Integration Tests + Coverage
      - name: Test
        run: npm run test:coverage

      # Gate 4: Build
      - name: Build
        run: npm run build

      # Upload coverage report as artifact
      - name: Upload Coverage
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: coverage/
          retention-days: 14

  e2e:
    name: E2E Tests
    needs: quality-gates          # Only run if quality gates pass
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - uses: actions/checkout@v6

      - uses: actions/setup-node@v6
        with:
          node-version: 22
          cache: 'npm'

      - run: npm ci

      # --- Supabase local stack (required if E2E tests hit the API/DB) ---
      # Uncomment and adapt when your E2E tests need a running backend:
      #
      # - name: Start Supabase
      #   run: npx supabase start
      #
      # - name: Reset Database (apply migrations + seed)
      #   run: npx supabase db reset
      #
      # → See [04-database-standards.md, § 13.2] for Supabase CI setup details.
      # → See [09-devops-cicd.md] for the complete pipeline with Docker + Supabase.

      # Install only the browser(s) needed — not all of them
      - name: Install Playwright Browsers
        run: npx playwright install --with-deps chromium

      - name: Run E2E Tests
        run: npm run test:e2e

      # Upload report and traces on failure — essential for debugging
      - name: Upload Playwright Report
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-report
          path: playwright-report/
          retention-days: 14

      - name: Upload Traces
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: playwright-traces
          path: test-results/
          retention-days: 14
```

#### Why This Configuration

| Decision | Rationale |
|---|---|
| `actions/checkout@v6`, `actions/setup-node@v6` | Latest stable versions (March 2026). v6 runs on Node.js 24 internally. |
| `node-version: 22` | Current LTS. Faker.js 10.x requires ≥ 20. |
| `cache: 'npm'` | Caches `node_modules` based on `package-lock.json`. Saves 20-60s per run. |
| `concurrency` + `cancel-in-progress` | New pushes to the same PR cancel the old run. Prevents wasting CI minutes on stale commits. |
| `timeout-minutes` per job | Prevents runaway tests from burning CI budget indefinitely. 15 min for unit/integration, 30 min for E2E. |
| E2E in separate job with `needs` | E2E only runs if quality gates pass. Saves ~5-10 min when unit tests fail. |
| `npx playwright install --with-deps chromium` | Installs only Chromium, not all browsers. Saves ~2 min and ~500MB. |
| `upload-artifact` on failure | Playwright traces and reports are essential for debugging CI-only failures. |
| `retention-days: 14` | Artifacts are kept for 2 weeks — enough to investigate without accumulating storage. |

---

### 8.3 Pipeline Rules

- **MUST** set `timeout-minutes` on every CI job — runaway tests should not
  burn minutes indefinitely
- **MUST** upload Playwright traces and reports as artifacts on failure —
  debugging CI failures without traces is guesswork
- **MUST** install only the browsers needed — `chromium` only unless
  cross-browser is enabled (→ See [Section 5.5])
- **SHOULD** use `concurrency` with `cancel-in-progress: true` — stale runs
  waste CI resources
- **SHOULD** run E2E in a separate job that depends on quality gates passing
- **SHOULD** cache `node_modules` and Playwright browsers to reduce CI time
- **MAY** run E2E on a nightly schedule instead of every PR if the suite is
  too slow for the PR feedback loop (> 10 min)

---

### 8.4 Merge Blocking Rules

- **MUST** require all quality gate checks to pass before merging
- **MUST** require at least one approving review on the PR
- **SHOULD** configure GitHub branch protection rules:
  - Required status checks: `quality-gates`, `e2e`
  - Require branches to be up to date before merging
  - Do not allow bypassing the above settings (even for admins)
- **MUST NOT** allow "merge anyway" when tests fail — if an urgent hotfix
  must bypass, create an ADR documenting the risk
  (→ See [01-core-principles.md, § 9 — ADR])

---

### 8.5 Anti-Patterns

| Anti-Pattern | Why it is bad | What to do instead |
|---|---|---|
| **Allowing merge with failing tests** | Broken code enters main; trust erodes | Enforce branch protection; no exceptions |
| **No timeout on CI jobs** | Hung test burns minutes until global limit | Set `timeout-minutes` per job |
| **Not uploading failure artifacts** | CI failures impossible to debug | Upload traces, screenshots, coverage |
| **All browsers on every PR** | Slow feedback; rarely catches PR-specific bugs | Chromium on PRs, full matrix nightly |
| **Ignoring flaky CI tests** | "It's just flaky" becomes excuse for real failures | Fix or quarantine immediately (→ § 5.4) |
| **No `concurrency` / `cancel-in-progress`** | Stale CI runs waste resources and confuse results | Cancel previous run on new push |

---

## 9. Coverage Strategy

§ 1.3 established the philosophy: coverage is a metric, not a goal. This
section turns that philosophy into actionable targets, configuration, and
guidance on reading coverage reports.

---

### 9.1 Recommended Targets by Layer

These targets are **minimums** — floors to prevent regression, not ceilings to
chase. Focus on testing meaningful behavior; use coverage to find gaps.

| Layer | Target | Rationale |
|---|---|---|
| **Services / business logic** | ≥ 80% | Core logic where bugs have the highest business impact. Complex branching deserves thorough coverage. |
| **Utilities / helpers** | ≥ 90% | Pure functions with clear inputs/outputs — cheap to test and widely consumed. A bug here propagates everywhere. |
| **Validation schemas (Zod)** | ≥ 90% | Schemas guard the system boundary. Every refinement and transform should be verified. |
| **API route handlers** | ≥ 70% | Integration-tested via Supertest. Harder to hit every branch at the unit level, but the HTTP contract must be covered. |
| **React components** | ≥ 60% | Interactive components with logic and event handlers. Skip trivial render-only wrappers. |
| **Custom hooks** | ≥ 80% | Hooks encapsulate reusable logic consumed by many components. |
| **Repository / data access** | ≥ 70% | Tested via integration tests with real DB. Coverage reflects queries exercised. |
| **E2E coverage** | Not measured as % | E2E tests cover critical flows, not code lines. Track flow coverage qualitatively. |

#### Adapting Targets to Project Maturity

| Project stage | Approach |
|---|---|
| **New project (0–3 months)** | Set thresholds low (50–60%) to avoid blocking velocity. Focus on testing critical paths. Increase thresholds as the codebase stabilizes. |
| **Growing project (3–12 months)** | Raise to the recommended targets above. Coverage should trend upward as tests are added with each feature. |
| **Mature project (12+ months)** | Recommended targets are the minimum. Consider per-module thresholds for critical domains (e.g., payment service at 90%). |

---

### 9.2 What NOT to Chase Coverage On

Exclude these from coverage reports — they inflate the denominator without
adding testable behavior:

- **Generated code** — ORM models, GraphQL codegen, Swagger types, Supabase
  type definitions (`database.types.ts`)
- **Configuration files** — `next.config.ts`, `tailwind.config.ts`,
  `vitest.config.ts`, `playwright.config.ts`
- **Type-only files** — `types.ts`, `*.d.ts` — no runtime behavior
- **Barrel files** — `index.ts` that only re-export from other modules
- **Storybook stories** — `*.stories.tsx` — documentation, not logic
- **Migration files** — SQL migrations are tested via `supabase db reset`,
  not via code coverage
- **Seed files** — `seed.sql`, seed scripts — tested by running them, not
  by coverage

---

### 9.3 Coverage Configuration (Vitest 4.x)

The shared Vitest configuration in § 3.1 already defines `coverage.provider`,
`coverage.include`, `coverage.exclude`, and `coverage.reporter`. This section
adds only the pieces that § 3.1 leaves for you to configure per project:
**thresholds** and **project-specific exclusions**.

```ts
// In vitest.config.ts → test.coverage (additions to the § 3.1 baseline)
coverage: {
  // ...base config from § 3.1 (provider, include, exclude, reporter)

  // Add project-specific exclusions on top of the baseline
  exclude: [
    // ...all excludes from § 3.1, plus:
    'src/**/database.types.ts',  // Supabase generated types — no logic to test
    'src/**/generated/**',       // Any codegen output
  ],

  // Thresholds — adjust per project maturity (→ See § 9.1)
  thresholds: {
    statements: 70,
    branches: 70,
    functions: 70,
    lines: 70,
  },
},
```

> **Vitest 4.x V8 accuracy:** The V8 coverage provider now uses AST-based
> analysis instead of the previous `v8-to-istanbul` remapping. Coverage
> reports are significantly more accurate — fewer false positives, more
> precise branch detection. If upgrading from Vitest 3.x, expect coverage
> numbers to change (usually decrease slightly) due to the improved accuracy.

---

### 9.4 How to Read Coverage Reports

```bash
# Generate and open the HTML report
npm run test:coverage
open coverage/index.html
```

When reviewing a coverage report, focus on — in this priority order:

1. **Uncovered branches (red highlights)** — code paths no test exercises.
   Ask: "What input triggers this branch? Is this branch reachable? Should
   I test it?"

2. **Uncovered functions** — entire functions at 0%. Ask: "Is this function
   used? If it is used, it needs a test. If it is dead code, delete it."

3. **Critical modules with low coverage** — services, validators, and
   utilities below their target. These are the highest-priority gaps.

4. **New code without coverage** — in a PR review, check that new functions
   and branches are covered. The coverage diff matters more than the
   absolute number.

What coverage reports **cannot** tell you:

- Whether assertions are meaningful (→ See [§ 1.3])
- Whether the test is resilient to refactoring (→ See [§ 1.5])
- Whether edge cases are covered (a branch can be "covered" by one test
  that only checks the happy path)

---

### 9.5 Coverage in Pull Request Reviews

- **SHOULD** review the coverage report diff in every PR — check that new
  code is tested, not just that the overall number is stable
- **SHOULD** question new functions or branches with 0% coverage in the PR
  — "why is this untested?" is a legitimate review comment
- **SHOULD** track coverage trends over time (weekly/monthly) rather than
  obsessing over a single PR's number
- **MUST NOT** reject a PR solely because coverage decreased by 1% — context
  matters. A PR that removes tested code and adds new tested code may show
  a net decrease.

---

### 9.6 Anti-Patterns

| Anti-Pattern | Why it is bad | What to do instead |
|---|---|---|
| **Writing tests solely to increase coverage** | Produces meaningless tests with weak assertions | Write tests for behavior; use coverage to find gaps |
| **Excluding files to inflate the percentage** | Hides untested code behind config | Exclude only genuinely non-testable code |
| **100% coverage as a requirement** | Diminishing returns; forces testing trivial code | Set realistic thresholds per layer |
| **Never looking at coverage** | Blind spots accumulate silently | Review reports in PRs; track trends |
| **Coverage gates that block hotfixes** | Governance failure — urgency blocked by a number | Use coverage as a warning in CI; hard-gate only for mature projects |
| **Comparing coverage between developers** | Coverage is a codebase property, not individual performance | Track team trends, not individual contributions |

---

## 10. Accessibility Testing

Accessibility is a requirement, not a feature
(→ See [05-frontend-standards.md, § 1.4]). Automated accessibility testing
catches common violations early — before they reach users who depend on
assistive technologies. This section defines the **strategy**; the patterns
(axe-core integration, query priority, manual checklist) live in the frontend
document.

> → See [05-frontend-standards.md, § 9] for WCAG 2.2 AA compliance target.
> → See [05-frontend-standards.md, § 6] for axe-core integration patterns.
> → See [02-technology-radar.md, § 4.11] for axe-core evaluation.

---

### 10.1 Automated Testing with axe-core

`axe-core` (4.11.x) detects accessibility violations programmatically:
missing alt text, insufficient color contrast, improper ARIA usage, missing
form labels, incorrect heading hierarchy, and more. It targets **WCAG 2.x
Level A and AA** rules by default.

> **Playwright note:** The `page.accessibility()` API was removed in
> Playwright 1.57. Use `@axe-core/playwright` instead.

#### Where to Run axe-core

| Context | Tool | What it catches | When to run |
|---|---|---|---|
| **Component tests** | `jest-axe` + Vitest | Violations in isolated components (missing labels, ARIA errors) | Every test run (fast) |
| **E2E tests** | `@axe-core/playwright` | Violations on full pages with real data and styling | Every E2E run or nightly |
| **CI (Lighthouse)** | Lighthouse CI | Accessibility score regression across builds | Every PR or nightly |

- **MUST** run axe-core checks on all new interactive components (forms,
  modals, navigation menus, dropdowns, dialogs)
- **SHOULD** include `@axe-core/playwright` checks in E2E tests for critical
  pages (login, dashboard, checkout, public-facing pages)
- **SHOULD** set a Lighthouse accessibility threshold (≥ 90) in CI and warn
  on regression
- **MAY** run full-page axe-core scans nightly — they are slower and may flag
  third-party widget issues outside your control

---

### 10.2 Manual Testing Checklist

Automated testing catches approximately 30–50% of accessibility issues. The
rest requires human verification:

| Check | How to test | What to look for |
|---|---|---|
| **Keyboard navigation** | Unplug your mouse; use Tab, Enter, Escape, Arrow keys | Can you complete every flow? Is the tab order logical? Can you escape modals? |
| **Screen reader** | Use VoiceOver (macOS), NVDA (Windows), or Orca (Linux) | Is content read in a logical order? Are interactive elements announced correctly? Are form errors conveyed? |
| **Zoom** | Zoom browser to 200% | Does the layout remain usable? Is text readable? Are interactive elements reachable? |
| **Color contrast** | Use browser DevTools or axe-core | Can all text be read against its background? Are focus indicators visible? |
| **Focus visibility** | Tab through the page | Is it always clear which element has keyboard focus? |

- **SHOULD** perform manual keyboard testing on every new feature before merge
- **SHOULD** test with a screen reader at least once per sprint on new features
- **MAY** include manual accessibility checks in the Definition of Done for
  user-facing features

---

### 10.3 Anti-Patterns

| Anti-Pattern | Why it is bad | What to do instead |
|---|---|---|
| **Skipping a11y tests — "it works for me"** | You are not every user | Run axe-core; test with keyboard; test with screen reader |
| **Disabling axe-core rules to pass** | Hides real violations from real users | Fix the violation or document a justified exception with an ADR |
| **Only automated testing** | Misses ~50% of issues | Complement with manual testing |
| **Adding ARIA without understanding** | Incorrect ARIA is worse than no ARIA | Follow WCAG 2.2 AA; → See [05-frontend-standards.md, § 9] |
| **Accessibility as a last-sprint task** | Retrofitting is expensive and incomplete | Build accessibility in from the start |

---

## 11. Performance Testing (Awareness)

Performance testing ensures the application meets speed and responsiveness
expectations. This section establishes awareness and minimum practices —
full performance engineering is an advanced topic that scales with
application maturity and traffic.

> k6 is 🔍 Assess in the Technology Radar
> (→ See [02-technology-radar.md, § 4.11]).
> → See [05-frontend-standards.md, § 10] for frontend performance guidelines.

---

### 11.1 Lighthouse in CI

Lighthouse provides automated audits for performance, accessibility, best
practices, and SEO. Running it in CI catches regressions before they reach
production.

- **SHOULD** run Lighthouse CI on critical pages (homepage, login, dashboard)
  as part of the CI pipeline or on a nightly schedule
- **SHOULD** set minimum thresholds and warn (or fail) on regression:

| Category | Minimum threshold |
|---|---|
| Performance | ≥ 80 |
| Accessibility | ≥ 90 |
| Best Practices | ≥ 90 |
| SEO | ≥ 80 |

- **MAY** track Lighthouse scores over time to detect gradual degradation

---

### 11.2 Bundle Size Monitoring

Large JavaScript bundles slow page loads. Monitoring prevents accidental bloat.

- **SHOULD** track bundle size in CI using `next-bundle-analyzer` or `size-limit`
- **SHOULD** set a bundle size budget and warn when it is exceeded
- **SHOULD** review dependency size before adding new packages
  (→ See [01-core-principles.md, § 10 — Dependency Management])

---

### 11.3 Core Web Vitals

- **SHOULD** monitor Core Web Vitals (LCP, INP, CLS) in production via RUM
  (Real User Monitoring)
- **SHOULD** use Lighthouse as a synthetic check in CI to catch regressions
- **MAY** set performance budgets for Core Web Vitals in CI

---

### 11.4 Load Testing (Awareness)

Load testing verifies that the application handles expected traffic. It
becomes necessary when:

- The application serves real users with traffic expectations
- Performance SLAs are defined (e.g., p95 response time < 200ms)
- The architecture changes significantly (new database, caching layer, hosting)

- **MAY** use k6 (🔍 Assess) for developer-friendly load testing when needed
- **MUST** create an ADR if introducing load testing as a regular practice —
  it adds infrastructure and maintenance cost
  (→ See [01-core-principles.md, § 9 — ADR])

---

## 12. Security Testing

Security testing verifies that the application is resilient against common
attack vectors. This section defines the strategy and cross-references — the
detailed SAST/DAST/SCA patterns live in the security standards document.

> → See [07-security-standards.md, § 13] for the comprehensive security
> testing pipeline (SAST, DAST, SCA, remediation SLAs).

---

### 12.1 Input Validation Testing

Every user-facing input is a potential attack surface:

- **MUST** test that validation rejects malformed, oversized, and malicious
  input (SQL injection patterns, XSS payloads, path traversal attempts)
- **MUST** test that error messages do not leak internal details (stack traces,
  SQL queries, file paths, dependency versions)
- **SHOULD** include security test cases alongside functional tests — not in a
  separate, forgettable suite

> → See [03-api-design.md, § 13] for API input validation testing.
> → See [07-security-standards.md, § 3] for validation rules and payloads.

---

### 12.2 Authentication & Authorization Testing

- **MUST** test that protected endpoints return 401 for unauthenticated requests
- **MUST** test that authorization rules return 403 (or 404 for ownership-based
  resources) for unauthorized access
- **MUST** test session lifecycle: login, logout, token refresh, expiration
- **SHOULD** test that privilege escalation is not possible (regular user
  cannot access admin endpoints, modify other users' data, or bypass RLS)

> → See [07-security-standards.md, § 6] for authentication standards.
> → See [04-database-standards.md, § 13.4] for RLS testing patterns.

---

### 12.3 Dependency Vulnerability Scanning

- **MUST** run `npm audit` in CI — fail on critical and high severity
  vulnerabilities
- **SHOULD** integrate automated dependency scanning (GitHub Dependabot,
  Snyk, or Socket)
- **SHOULD** remediate critical vulnerabilities within 72 hours and high
  within 2 weeks

> → See [07-security-standards.md, § 13] for the complete security testing
> pipeline and remediation SLAs.

---

### 12.4 Anti-Patterns

| Anti-Pattern | Why it is bad | What to do instead |
|---|---|---|
| **No security tests at all** | Common vulnerabilities go undetected | Add security test cases to existing suites |
| **Security testing only at the end** | Too late; fixing is expensive | Integrate into CI from day one |
| **Testing only happy paths for auth** | Missing the attack surface | Test 401, 403, expiry, escalation, header manipulation |
| **Ignoring `npm audit` warnings** | Known vulnerabilities in dependency tree | Address critical/high; document accepted risks |

---

## 13. Test Maintenance & Quality

A test suite is a living system that requires ongoing maintenance. Unmaintained
tests slow development, produce false signals, and erode trust. This section
covers when to refactor tests, how to handle flaky tests systematically, and
when it is appropriate to delete a test.

---

### 13.1 When to Refactor Tests

Tests accumulate technical debt just like production code:

- **SHOULD** refactor when tests are hard to read — if a developer cannot
  understand a test's intent within 30 seconds, it needs rewriting
- **SHOULD** refactor when tests are brittle — if they break on every
  refactoring even when behavior is preserved, they are testing implementation
  (→ See [§ 1.5])
- **SHOULD** refactor when tests are slow — if a test file takes > 10s,
  investigate: unnecessary setup, redundant assertions, missing mocks
- **SHOULD** apply the Boy Scout Rule to tests — leave test files slightly
  cleaner than you found them
  (→ See [01-core-principles.md, § 13.4])

---

### 13.2 Dealing with Flaky Tests

Flaky tests are a systemic problem with a strict protocol:

1. **Identify** — track which tests are flaky via CI dashboards, Playwright
   retry tracking, or `--reporter=json` analysis
2. **Quarantine** — tag with `test.fixme()` or move to `*.flaky.spec.ts` so
   the main suite stays green and trustworthy
3. **Fix** — investigate root cause (timing, shared state, external dependency)
   and resolve it
4. **Restore** — move the fixed test back; monitor for recurrence
5. **Prevent** — review what caused the flakiness and add a safeguard (better
   isolation, auto-waiting, deterministic data)

- **MUST** fix quarantined tests within the current sprint — quarantine is
  temporary, not permanent
- **MUST NOT** increase retry count as a permanent fix
- **MUST NOT** delete a test because it is flaky — flakiness is a bug in the
  test, not a reason to remove coverage

---

### 13.3 When to Delete Tests

Tests are not sacred — sometimes deleting is the right decision:

- **MAY** delete when the feature it tests has been removed
- **MAY** delete when a higher-tier test now covers the same behavior with
  better confidence
- **MAY** delete when the test only verifies framework behavior, not
  application logic
- **MUST NOT** delete because it is "inconvenient" or "probably unnecessary"
  without understanding what it covers
- **MUST** verify that deleting a test does not leave critical behavior
  untested — check coverage before and after

---

### 13.4 Test Documentation

Good tests are self-documenting, but some need extra context:

- **SHOULD** add a comment when a test reproduces a specific bug:
  `// Regression: fixes #234 — double-submit created duplicate orders`
- **SHOULD** add a comment when setup is unusual or non-obvious
- **SHOULD** add a comment when an edge case might look like a mistake to
  a future developer

---

### 13.5 Anti-Patterns

| Anti-Pattern | Why it is bad | What to do instead |
|---|---|---|
| **Never reviewing test quality** | Bad tests accumulate | Include test review in code review |
| **Flaky tests ignored for weeks** | Trust collapses | Quarantine immediately; fix within sprint |
| **Tests with no assertions** | Always pass; test nothing | Every test needs at least one meaningful assertion |
| **Commented-out tests** | Dead code that misleads | Delete; Git remembers |
| **Duplicated tests** | Maintenance burden, no extra confidence | Identify and remove redundancy |

---

## 14. Testing Checklist

### 14.1 Pre-Merge Checklist

Before submitting a PR, verify:

- [ ] All tests pass — `npm run test:run` exits with 0
- [ ] New behavior has tests — every feature, bug fix, or behavior change
      includes corresponding tests
- [ ] No `test.skip` or `test.only` left in code
- [ ] No `console.log` left in test files
- [ ] Test names describe behavior — not implementation
- [ ] Factories used for test data — no hardcoded `"John Doe"` or
      `"test@test.com"`
- [ ] Mocks are restored — `restoreMocks: true` in config or manual cleanup
- [ ] No shared mutable state — each test is independent
- [ ] Accessibility checked — axe-core on new components and pages
- [ ] Coverage not regressed — no significant drop in critical modules

### 14.2 Pre-Release Checklist

Before releasing to production:

- [ ] All CI quality gates pass — lint, typecheck, test, build
- [ ] E2E tests pass — all critical user flows verified
- [ ] Cross-browser E2E pass (if applicable)
- [ ] Security scan clean — `npm audit` shows no critical/high vulnerabilities
- [ ] Performance budget met — Lighthouse scores above thresholds
- [ ] Manual accessibility check on new features — keyboard and screen reader
- [ ] No quarantined flaky tests — all fixed or explicitly documented

### 14.3 Quick Reference: Common Testing Mistakes

| # | Mistake | Fix |
|---|---|---|
| 1 | No tests for error paths | Test both happy and unhappy paths |
| 2 | Testing implementation details | Test inputs/outputs, not internal calls (→ § 1.5) |
| 3 | Shared state between tests | Reset in `beforeEach`; use factories (→ § 6) |
| 4 | Hardcoded test data | Use factories with Faker.js (→ § 6.1) |
| 5 | `toBeTruthy()` on objects | Use `toEqual`, `toMatchObject`, specific assertions |
| 6 | Mocking DB in integration tests | Use real test database (→ § 4.1) |
| 7 | No assertions in a test | Every test needs at least one meaningful assertion |
| 8 | E2E for every edge case | Edge cases at unit/integration; E2E for critical flows (→ § 2.4) |
| 9 | Ignoring flaky tests | Fix immediately; quarantine if needed (→ § 13.2) |
| 10 | `page.waitForTimeout()` in E2E | Use Playwright auto-waiting or explicit assertions |
| 11 | No trace on CI failure | Enable `trace: 'on-first-retry'` (→ § 5.1) |
| 12 | Coverage as a goal | Focus on behavior; use coverage to find gaps (→ § 1.3) |
| 13 | Skipping accessibility tests | Run axe-core on all new components (→ § 10) |
| 14 | No cleanup after tests | Transaction rollback or truncate + reseed (→ § 4.2) |
| 15 | Mocking your own code extensively | Refactor for DI; test through public interface (→ § 7.1) |

---

## Document History

| Date | Change | Motivation |
|---|---|---|
| 2026-03 | Initial version | Complete testing strategy — philosophy, pyramid, unit/integration/E2E standards, test data, mocking, CI/CD, coverage, accessibility, performance, security, maintenance, and checklists |

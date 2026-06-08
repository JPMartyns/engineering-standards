# 🧭 Technology Radar

> **Scope:** Technology evaluation framework and curated radar for all projects covered by these engineering standards.
>
> **Purpose:** The decision guide that answers "what tool/framework/language to use for what?" and "how to evaluate a new technology before adopting it?" — ensuring technology choices are deliberate, justified, and aligned with project needs.
>
> **Keywords:**
> - **MUST** = required (deviation requires an ADR with explicit justification)
> - **SHOULD** = strongly recommended (requires justification to skip)
> - **MAY** = optional (case-by-case)

---

## 0. How to Use This Document

- This document defines **what technologies to use and how to evaluate new ones**. It does not define how to use them — that belongs in the domain-specific documents.
- The boundary is clear: **this document says "use PostgreSQL for relational data" — [04-database-standards.md] says "and here is how: naming, migrations, RLS, indexing."**
- Every technology listed here has been evaluated against the framework in [Section 1](#1-technology-evaluation-framework) and classified into a radar category defined in [Section 2](#2-radar-categories).
- Before adopting any technology not listed in this radar, evaluate it using the framework in Section 1 and propose its inclusion via an ADR.
- This is the **most perishable document** in the collection — technology evolves fast. See [Section 7](#7-radar-governance) for the review and update process.

### Document Relationships

```text
02-technology-radar.md (this document)
 ├── Derives from    → 01-core-principles.md (dependency philosophy, YAGNI, pragmatism)
 ├── Complements     → 07-security-standards.md (security tooling choices align with security standards)
 ├── Referenced by   → 03-api-design.md (API framework and tooling choices)
 ├── Referenced by   → 04-database-standards.md (database engine and ORM choices)
 ├── Referenced by   → 05-frontend-standards.md (frontend framework, styling, state management choices)
 ├── Referenced by   → 06-testing-strategy.md (test runner, E2E framework choices)
 ├── Referenced by   → 08-observability.md (monitoring and logging tool choices)
 └── Referenced by   → 09-devops-cicd.md (CI/CD, containerization, hosting choices)
```

### Boundary Definitions

| Question | This Document (02) | Other Document |
|----------|--------------------|----------------|
| **Which** technology to use for a given purpose? | ✅ Sections 3–4 (radar tables + profiles) | — |
| **How** to evaluate a new technology? | ✅ Section 1 (evaluation framework) | — |
| **How** to use the chosen technology? | — | Domain-specific documents (03–09) |
| **How** to manage dependencies day-to-day? | — | → See [01-core-principles.md, §10] (dependency philosophy) |
| **When** does a technology choice require an ADR? | ✅ Section 1.3 (ADR by impact) | → See [01-core-principles.md, §9] (ADR structure) |
| **What** security tools to use? | ✅ Sections 3.12, 3.15 (tool choices) | → See [07-security-standards.md] (how to use them) |

### Technology Versions

This document was last comprehensively reviewed against these ecosystem
states. Individual entries may have been updated more recently — check the
changelog in [Section 7](#7-radar-governance).

| Ecosystem | Baseline State | Date |
|-----------|----------------|------|
| Node.js | v24 LTS (Active), v22 LTS (Maintenance) | March 2026 |
| Next.js | 16.x (Turbopack default, standalone Docker) | March 2026 |
| React | 19.x (React Compiler stable) | March 2026 |
| TypeScript | 5.x (6.0 Beta with Temporal support) | March 2026 |
| Tailwind CSS | v4 (CSS-native config, Oxide engine) | March 2026 |
| PostgreSQL | 15+ (via Supabase or direct) | March 2026 |
| Prisma | v7 (100% TypeScript, driver adapters) | March 2026 |
| ESLint | v10 (flat config only) | March 2026 |
| Temporal API | TC39 Stage 4, ES2026 (Chrome+Firefox+Edge) | March 2026 |
| LLM Providers | Claude Opus 4.8 / GPT-5.5 / Gemini 3.x Flash | June 2026 |
| AI SDK (TypeScript) | Vercel AI SDK 6 | June 2026 |
| Agent / RAG stack | LangGraph, pgvector, Docling, MCP (Linux Foundation) | June 2026 |

### AI Agent Instructions

This document is designed to be consumed by AI coding agents (e.g., Claude
Code). When interpreting this document:

- **MUST**, **SHOULD**, and **MAY** are RFC 2119 keywords — treat MUST as non-negotiable constraints, SHOULD as strong defaults that require explicit justification to override, and MAY as contextual options.
- Cross-references (→ See [XX-document.md]) point to authoritative definitions — always defer to the referenced document for the full rule.
- When this document conflicts with [07-security-standards.md], the security document takes precedence.
- BAD/GOOD code examples are pattern-matching references — apply the principle behind the example, not just the literal code.
- Anti-pattern tables describe common mistakes — use them as negative examples when reviewing or generating code.
- Before recommending or using any technology, check its radar category. Adopt = use by default. Hold = do not use in new projects.
- If generating code requires violating a MUST rule, the AI **MUST stop** and ask the human for permission before proceeding — never silently override a standard.
- **MUST NOT** over-engineer — always prefer the simplest solution that meets the stated requirements. Do not add abstractions, patterns, or infrastructure beyond what was explicitly requested (→ See [01-core-principles.md, §12]).

---

## 1. Technology Evaluation Framework

Every technology choice — language, framework, platform, service, or tool — carries long-term consequences.
This framework provides a structured, repeatable process for evaluating technologies before adoption.

> For dependency-level evaluation (npm packages, Python libraries), the detailed cost model and decision
> framework in → See [01-core-principles.md, Section 10 — Dependency Management Philosophy] applies.
> This section covers **broader technology decisions**: languages, frameworks, platforms, infrastructure
> services, and major tooling choices.

---

### 1.1 Evaluation Principles

Before applying any criteria, internalize these principles:

- **No technology is inherently good or bad** — only appropriate or inappropriate for a given context.
  A tool that is perfect for a startup MVP may be a liability for an enterprise system, and vice versa.
- **The best technology is the one your team can operate** — a theoretically superior tool that no one
  on the team understands is worse than a "good enough" tool the team knows well.
- **Switching costs are real** — adopting a technology is easy; migrating away from it is expensive.
  Evaluate the exit cost, not just the entry cost.
- **Hype is not a signal** — popularity on social media, conference talks, or "State of X" surveys is
  marketing, not evidence. Evaluate based on production track record and technical merit.

---

### 1.2 Evaluation Criteria

Every technology under consideration **MUST** be evaluated against these criteria before adoption.
Not every criterion carries equal weight — the context determines priority — but none should be skipped entirely.

| #  | Criterion              | Key Questions                                                                                      | How to Assess                                        |
|----|------------------------|----------------------------------------------------------------------------------------------------|------------------------------------------------------|
| 1  | **Problem Fit**        | Does it solve a real, current problem? Or are we adopting it looking for a problem to solve?       | Map to a concrete requirement or pain point          |
| 2  | **Maturity & Stability** | Is it production-proven? How often do breaking changes occur? Is the API surface stable?         | Release history, semver adherence, changelog review  |
| 3  | **Community & Ecosystem** | Is there an active community? Quality documentation? Third-party integrations?                  | GitHub activity, Stack Overflow presence, plugin ecosystem |
| 4  | **Team Competence**    | Can the current team operate it? What is the learning curve? Is hiring realistic?                  | Team assessment, documentation quality, tutorial availability |
| 5  | **Security Posture**   | Does it have a security policy? CVE history? Active vulnerability response?                        | SECURITY.md, CVE databases, response time to past issues |
| 6  | **Maintenance & Governance** | Who maintains it? Single maintainer vs organization? Funding model?                          | Governance model, bus factor, sponsorship/backing    |
| 7  | **Performance Profile** | Does it meet the performance requirements? Where are the known bottlenecks?                       | Benchmarks (with skepticism), profiling, load testing |
| 8  | **Integration Cost**   | How well does it fit with the existing stack? What adapters or glue code are needed?               | Proof of concept, compatibility matrix               |
| 9  | **Operational Cost**   | What does it cost to run, monitor, and maintain in production? (infra, licensing, team time)       | TCO analysis, pricing model review                   |
| 10 | **Exit Cost**          | How hard is it to migrate away? Does it create vendor lock-in? Are there open standards?           | Data portability, API standardization, alternatives  |
| 11 | **License**            | Is the license compatible with project requirements? Any viral/copyleft concerns?                  | SPDX identifier, license text review                 |

#### Weighting Guidance

- For **early-stage projects / MVPs**: prioritize Problem Fit, Team Competence, and Integration Cost
  — speed of delivery matters most
- For **production systems with real users**: prioritize Security Posture, Maturity, Maintenance,
  and Operational Cost — reliability matters most
- For **long-lived enterprise systems**: prioritize Exit Cost, Governance, and License
  — sustainability matters most

---

### 1.3 Evaluation Process

Technology evaluation is not a solo activity. Even in small teams, the process benefits from structure.

#### Step-by-Step

1. **Identify the need** — What specific problem are you solving? Document it clearly.
   If you cannot articulate the problem without mentioning the technology, you may be solution-shopping.

2. **Survey the landscape** — Identify 2–3 realistic candidates (including "do nothing" or "use what we have").
   A single-option evaluation is not an evaluation — it is a confirmation bias exercise.

3. **Score against criteria** — Use the evaluation criteria table above. Document scores and reasoning.
   Be honest about weaknesses, not just strengths.

4. **Build a proof of concept** — For significant decisions (Critical or Important tier),
   build a small, time-boxed PoC that tests the riskiest assumptions — not a demo of the happy path.

5. **Make the decision** — Document it in an ADR (→ See [01-core-principles.md, Section 9]).
   Include: what was chosen, what was rejected, and why.

6. **Define the review trigger** — Set a condition under which the decision should be revisited
   (e.g., "revisit if the framework drops below 1 release per quarter" or "revisit when the team
   grows beyond 5 developers").

#### ADR Requirements by Impact

| Decision Impact | Examples                                                          | ADR Required? |
|-----------------|-------------------------------------------------------------------|---------------|
| **Critical**    | Primary language, core framework, database engine, cloud provider | **MUST**      |
| **Important**   | ORM, test framework, CI/CD platform, auth provider                | **SHOULD**    |
| **Moderate**    | Utility library, monitoring tool, formatting tool                 | **MAY**       |
| **Low**         | Dev-only convenience tool, editor plugin                          | No            |

> → See [01-core-principles.md, Section 10.3 — Dependency Tiers] for the full tier classification
> that informs these impact levels.

---

## 2. Radar Categories

Every technology in this radar is classified into one of four categories.
These categories reflect **confidence level and recommended usage**, not quality judgments.

A technology in Hold is not necessarily bad — it may be excellent in other contexts but inappropriate
for the current stack, team size, or project phase.

---

### 2.1 Category Definitions

#### ✅ Adopt

**Use by default in new projects.**

- The technology has been evaluated, tested in production, and proven reliable.
- The team has sufficient competence to operate it without significant ramp-up.
- It is the **recommended default** for its category — deviating from it requires justification.
- Choosing an alternative over an Adopt technology **SHOULD** be documented in an ADR.

> Think of Adopt as "the house standard." You pick it unless you have a good reason not to.

#### 🔬 Trial

**Use in real projects with the explicit intent to evaluate.**

- The technology shows strong potential and has passed initial assessment.
- It is approved for use in non-critical paths or new projects where the risk is acceptable.
- The team **MUST** document lessons learned after each Trial usage.
- A Trial technology **SHOULD** be promoted to Adopt or moved to Hold within 2–3 project cycles.
- Trial is not a permanent state — it is a time-boxed experiment.

> Think of Trial as "we believe this is good, and we are proving it."

#### 🔍 Assess

**Investigate and learn, but do not use in real projects yet.**

- The technology is interesting and potentially valuable, but has not been evaluated enough.
- Approved for: personal learning, hackathons, spike investigations, proof of concepts.
- **MUST NOT** be used in production code or client-facing projects.
- The goal of Assess is to gather enough information to move the technology to Trial or Hold.

> Think of Assess as "on the reading list — worth understanding, not yet worth betting on."

#### ⛔ Hold

**Do not adopt in new projects.**

- The technology is either: outdated, superseded by a better alternative, misaligned with the
  current stack, too complex for the team's current maturity, or presents unacceptable risks.
- **Existing usage in legacy projects is acceptable** — Hold does not mean "rip it out immediately."
- New projects **MUST NOT** adopt Hold technologies without an ADR explaining exceptional circumstances.
- When a Hold technology exists in a project, **SHOULD** plan migration to the Adopt alternative
  when practical (during major refactors, not as a standalone effort).

> Think of Hold as "we know about it, we have chosen not to use it — here is why."

---

### 2.2 Lifecycle & Movement Rules

Technologies move between categories based on evidence, not opinion.

```text
  ┌──────────┐     Evaluation      ┌──────────┐     PoC / Spike      ┌──────────┐
  │          │    positive &       │          │    successful &      │          │
  │  Assess  │───────────────────► │  Trial   │────────────────────► │  Adopt   │
  │          │    team interest    │          │    production-proven │          │
  └────┬─────┘                     └────┬─────┘                      └─────┬────┘
       │                                │                                  │
       │ Not a fit /                    │ Problems found /                 │ Superseded /
       │ better alternative             │ better alternative emerged       │ no longer maintained
       │                                │                                  │
       ▼                                ▼                                  ▼
  ┌──────────┐                     ┌──────────┐                      ┌──────────┐
  │  Hold /  │                     │   Hold   │                      │   Hold   │
  │  Drop    │                     │          │                      │          │
  └──────────┘                     └──────────┘                      └──────────┘
```

#### Movement Rules

- **Assess → Trial**: Requires a documented evaluation (Section 1 criteria) and team agreement.
- **Trial → Adopt**: Requires successful usage in at least one real project, documented lessons
  learned, and no blocking issues discovered.
- **Trial → Hold**: If the trial reveals significant issues, document them and move to Hold.
- **Adopt → Hold**: When a technology is superseded, no longer maintained, or the ecosystem shifts.
  **MUST** be documented in an ADR with a migration recommendation.
- **Any → Drop** (removed from radar): Only for technologies that are no longer relevant enough
  to track (e.g., a tool that has been discontinued).
- **Hold → Trial**: Rare, but possible if circumstances change significantly (new major version,
  team composition change, different project context). Requires a fresh evaluation.

#### Rules

- **MUST NOT** skip categories — a technology cannot go from Assess directly to Adopt.
  The Trial phase exists to catch issues that assessment alone cannot reveal.
- **MUST** document every category change in the radar's changelog (Section 7).
- **SHOULD** review the full radar quarterly — see [Section 7](#7-radar-governance).

---

## 3. The Radar

This section provides the at-a-glance view of all evaluated technologies, organized by domain.
For detailed profiles explaining the reasoning behind each classification, see [Section 4](#4-technology-profiles).

> **Reading guide:** Scan the table for your domain of interest. The category column tells you the
> recommendation. If you need the "why," follow the link to the corresponding profile in Section 4.

### Last Updated: 2026-03

---

### 3.1 Languages

| Technology       | Category    | Primary Use Case                              | Notes                                    |
|------------------|-------------|-----------------------------------------------|------------------------------------------|
| TypeScript       | ✅ Adopt    | All application code (frontend + backend)     | Strict mode required                     |
| JavaScript       | ⛔ Hold     | Legacy code only                              | Use TypeScript for all new code          |
| Python           | ✅ Adopt    | Automation, scripting, AI/ML, data processing | Not for web backends by default          |
| SQL              | ✅ Adopt    | Database queries, migrations                  | PostgreSQL dialect preferred             |
| HTML / CSS       | ✅ Adopt    | Markup and base styling                       | Foundational — always relevant           |

---

### 3.2 Frontend Frameworks

| Technology       | Category    | Primary Use Case                              | Notes                                    |
|------------------|-------------|-----------------------------------------------|------------------------------------------|
| React            | ✅ Adopt    | UI component library (via Next.js or Vite)    | Server Components by default in Next.js  |
| Next.js          | ✅ Adopt    | Full-stack React framework                    | App Router, default for web apps         |
| Vite + React     | ✅ Adopt    | Lightweight SPAs, internal tools, prototypes  | Not for SEO-dependent sites              |
| Astro            | 🔬 Trial    | Content-heavy sites, blogs, marketing pages   | Excellent static performance, great SEO  |
| Svelte/SvelteKit | 🔍 Assess   | Alternative reactive framework                | Interesting DX, smaller ecosystem        |
| Vue.js           | ⛔ Hold     | —                                             | Not aligned with current stack           |
| Angular          | ⛔ Hold     | —                                             | Too heavyweight for current team/projects|

---

### 3.3 Styling

| Technology        | Category    | Primary Use Case                             | Notes                                    |
|-------------------|-------------|----------------------------------------------|------------------------------------------|
| Tailwind CSS      | ✅ Adopt    | All styling (utility-first)                  | v4: CSS-native config via @theme, Oxide engine |
| CSS Modules       | 🔬 Trial    | Complex scoped styles                        | When utilities are insufficient          |
| Sass / SCSS       | ⛔ Hold     | —                                            | Tailwind covers the use cases            |
| styled-components | ⛔ Hold     | —                                            | Runtime CSS-in-JS, performance concerns  |
| Emotion           | ⛔ Hold     | —                                            | Same concerns as styled-components       |

---

### 3.4 UI Component Libraries

| Technology        | Category    | Primary Use Case                             | Notes                                    |
|-------------------|-------------|----------------------------------------------|------------------------------------------|
| shadcn/ui         | ✅ Adopt    | Pre-built accessible components              | Copy-paste model, full ownership of code |
| Radix UI          | ✅ Adopt    | Headless accessible primitives               | Foundation of shadcn/ui                  |
| Headless UI       | 🔬 Trial    | Lightweight headless components              | Tailwind Labs project, good alternative  |
| Material UI (MUI) | ⛔ Hold     | —                                            | Heavy, opinionated styling, hard to customize |
| Chakra UI         | ⛔ Hold     | —                                            | Runtime CSS-in-JS, moving to Ark UI      |

---

### 3.5 Validation & Schema

| Technology        | Category    | Primary Use Case                             | Notes                                    |
|-------------------|-------------|----------------------------------------------|------------------------------------------|
| Zod               | ✅ Adopt    | Runtime validation, schema definition, type inference | Single source of truth for types + validation |
| Yup               | ⛔ Hold     | Form validation                              | Zod covers all use cases with better TS inference |
| Joi               | ⛔ Hold     | Server-side validation                       | Node.js only, no TS inference, heavier   |
| class-validator   | 🔍 Assess   | Decorator-based validation (NestJS)          | Relevant only if NestJS is adopted       |

---

### 3.6 State Management

| Technology        | Category    | Primary Use Case                             | Notes                                    |
|-------------------|-------------|----------------------------------------------|------------------------------------------|
| React Server Components | ✅ Adopt | Server-side data fetching, reduce client state | Default in Next.js App Router       |
| React hooks (useState/useReducer) | ✅ Adopt | Local component state               | Prefer over external libraries for simple state |
| React Context     | ✅ Adopt    | Shared state across component tree           | For low-frequency updates (theme, auth, locale) |
| TanStack Query    | ✅ Adopt    | Server state (async data fetching, caching)  | Replaces manual fetch + useEffect patterns |
| Zustand           | 🔬 Trial    | Lightweight global client state              | When Context is insufficient, simpler than Redux |
| Redux Toolkit     | ⛔ Hold     | Complex global state                         | Overkill for current project scale       |
| Jotai / Recoil    | 🔍 Assess   | Atomic state management                      | Interesting pattern, not yet needed      |

---

### 3.7 Backend Frameworks

| Technology        | Category    | Primary Use Case                             | Notes                                    |
|-------------------|-------------|----------------------------------------------|------------------------------------------|
| Next.js API Routes| ✅ Adopt    | API endpoints co-located with frontend       | Route Handlers (App Router), default for full-stack |
| Express.js        | ✅ Adopt    | Standalone Node.js REST APIs                 | Mature, minimal, huge ecosystem          |
| NestJS            | 🔬 Trial    | Structured enterprise-style Node.js APIs     | TypeScript-native, SOLID-friendly, steeper learning curve |
| FastAPI           | 🔬 Trial    | Python APIs, AI/ML service endpoints         | Excellent performance, auto-docs, async  |
| Hono              | 🔍 Assess   | Lightweight edge-first API framework         | Ultra-fast, runs on Cloudflare Workers   |
| Koa               | ⛔ Hold     | —                                            | Express covers the use case, larger ecosystem |
| Django            | ⛔ Hold     | —                                            | Not aligned with current stack (Python web) |

---

### 3.8 Database & Data

| Technology        | Category    | Primary Use Case                             | Notes                                    |
|-------------------|-------------|----------------------------------------------|------------------------------------------|
| PostgreSQL        | ✅ Adopt    | Primary relational database                  | Via Supabase or direct                   |
| Supabase          | ✅ Adopt    | Managed PostgreSQL + Auth + Realtime + Storage | Default BaaS for new projects          |
| Prisma            | ✅ Adopt    | Type-safe ORM for Node.js/TS                 | v7: Rust-free, 100% TS, major performance gains |
| Drizzle ORM       | 🔬 Trial    | Lightweight type-safe SQL builder            | v1 beta, SQL-first, growing adoption rapidly |
| Redis             | 🔍 Assess   | Caching, session store, rate limiting        | Add only when measured need exists       |
| MongoDB           | ⛔ Hold     | —                                            | PostgreSQL (+ JSONB) covers most use cases |
| MySQL             | ⛔ Hold     | —                                            | PostgreSQL preferred for all new projects |
| SQLite            | 🔍 Assess   | Embedded database, local-first apps          | Interesting with Turso/libSQL for edge   |

---

### 3.9 Authentication & Authorization

| Technology        | Category    | Primary Use Case                             | Notes                                    |
|-------------------|-------------|----------------------------------------------|------------------------------------------|
| Supabase Auth     | ✅ Adopt    | Authentication for Supabase-backed projects  | Built-in RLS integration, social login, MFA |
| NextAuth.js (Auth.js) | 🔬 Trial | Authentication for non-Supabase projects  | Framework-agnostic (v5), many providers  |
| Passport.js       | ⛔ Hold     | Express.js auth middleware                   | Callback-heavy, Auth.js is the modern path |
| Clerk             | 🔍 Assess   | Managed auth with pre-built UI components    | Excellent DX, evaluate pricing at scale  |
| Lucia Auth        | ⛔ Hold     | Lightweight session auth library             | Deprecated by author (early 2025)        |
| Keycloak          | 🔍 Assess   | Self-hosted enterprise identity provider     | Powerful but heavy for small projects    |

---

### 3.10 API Tooling & Documentation

| Technology        | Category    | Primary Use Case                             | Notes                                    |
|-------------------|-------------|----------------------------------------------|------------------------------------------|
| OpenAPI / Swagger | ✅ Adopt    | API specification and documentation          | Standard for REST API contracts          |
| Postman           | ✅ Adopt    | API testing, exploration, collaboration      | Team collections, environment management |
| Insomnia          | 🔬 Trial    | Lightweight API client                       | Simpler alternative to Postman           |
| Bruno             | 🔍 Assess   | Git-friendly API client (files, not cloud)   | Offline-first, version-controllable      |
| tRPC              | 🔍 Assess   | End-to-end type-safe APIs (TS only)          | Eliminates API contracts, tight coupling |
| GraphQL           | ⛔ Hold     | —                                            | REST covers current needs, added complexity |

---

### 3.11 Testing

| Technology        | Category    | Primary Use Case                             | Notes                                    |
|-------------------|-------------|----------------------------------------------|------------------------------------------|
| Vitest            | ✅ Adopt    | Unit and integration testing                 | Vite-native, Jest-compatible API, fast   |
| Playwright        | ✅ Adopt    | End-to-end testing, cross-browser            | Best-in-class E2E, auto-wait, codegen   |
| Testing Library   | ✅ Adopt    | Component testing (React)                    | User-centric queries, pairs with Vitest  |
| Supertest         | ✅ Adopt    | HTTP assertion for API integration tests     | Pairs with Express/NestJS                |
| Jest              | ⛔ Hold     | Unit testing                                 | Vitest supersedes — faster, ESM-native   |
| Cypress           | ⛔ Hold     | E2E testing                                  | Playwright preferred — faster, multi-browser |
| Storybook         | 🔬 Trial    | Component documentation and visual testing   | Valuable for design systems, adds build overhead |
| k6                | 🔍 Assess   | Load and performance testing                 | Script-based, developer-friendly         |
| Faker.js          | ✅ Adopt    | Realistic test data generation               | Essential for seed scripts and test factories |

---

### 3.12 Code Quality & Formatting

| Technology        | Category    | Primary Use Case                             | Notes                                    |
|-------------------|-------------|----------------------------------------------|------------------------------------------|
| ESLint            | ✅ Adopt    | Linting (TS + React + Next.js)               | v10: flat config only (eslint.config.js) |
| Prettier          | ✅ Adopt    | Code formatting                              | Pair with ESLint, no debates on style    |
| Husky             | ✅ Adopt    | Git hooks (pre-commit, commit-msg)           | Enforces quality gates locally           |
| lint-staged       | ✅ Adopt    | Run linters only on staged files             | Performance optimization for Husky       |
| commitlint        | ✅ Adopt    | Enforce Conventional Commits                 | Pairs with Husky commit-msg hook         |
| Biome             | 🔬 Trial    | All-in-one linter + formatter (Rust-based)   | v2.3: React/Next.js domains, 462 rules, type-aware |
| SonarQube         | 🔬 Trial    | Static analysis, code quality dashboard      | Deeper analysis than ESLint alone        |
| EditorConfig      | ✅ Adopt    | Cross-editor formatting consistency          | .editorconfig in project root            |

---

### 3.13 DevOps & Containerization

| Technology        | Category    | Primary Use Case                             | Notes                                    |
|-------------------|-------------|----------------------------------------------|------------------------------------------|
| Docker            | ✅ Adopt    | Containerization, reproducible environments  | Required for production deployments      |
| Docker Compose    | ✅ Adopt    | Local multi-container development            | Dev databases, queues, services          |
| GitHub Actions    | ✅ Adopt    | CI/CD pipelines                              | Integrated with GitHub, generous free tier |
| Terraform         | 🔍 Assess   | Infrastructure as Code (IaC)                 | Powerful but complex for small projects  |
| Kubernetes (K8s)  | ⛔ Hold     | Container orchestration                      | Massive overkill for current project scale |
| Jenkins           | ⛔ Hold     | CI/CD server                                 | GitHub Actions preferred, less maintenance |
| Pulumi            | 🔍 Assess   | IaC with real programming languages          | Alternative to Terraform using TS/Python |
| Nginx             | 🔬 Trial    | Reverse proxy, static file serving, load balancing | Essential for self-hosted deployments |

---

### 3.14 Hosting & Deployment

| Technology        | Category    | Primary Use Case                             | Notes                                    |
|-------------------|-------------|----------------------------------------------|------------------------------------------|
| Vercel            | ✅ Adopt    | Next.js hosting, frontend deployments        | Zero-config, preview deployments, edge   |
| Supabase Cloud    | ✅ Adopt    | Managed PostgreSQL + backend services        | Pairs with Supabase Auth, Realtime, Storage |
| Cloudflare Pages  | 🔬 Trial    | Static sites, edge-deployed apps             | Generous free tier, Astro-friendly       |
| Railway           | 🔬 Trial    | Simple backend/container hosting             | Docker deploy, managed DBs, good DX     |
| Render            | 🔬 Trial    | Backend/container hosting, managed DBs       | Similar to Railway, free tier available  |
| Fly.io            | 🔍 Assess   | Edge-deployed containers                     | Global distribution, interesting model   |
| AWS (general)     | 🔍 Assess   | Full cloud infrastructure                    | Powerful but complex, evaluate per-service |
| DigitalOcean      | 🔍 Assess   | VPS and managed services                     | Simpler than AWS, good for learning      |
| Heroku            | ⛔ Hold     | PaaS hosting                                 | Pricing no longer competitive, better alternatives |
| Netlify           | ⛔ Hold     | —                                            | Vercel preferred for React/Next.js ecosystem |

---

### 3.15 Observability & Monitoring

| Technology        | Category    | Primary Use Case                             | Notes                                    |
|-------------------|-------------|----------------------------------------------|------------------------------------------|
| Sentry            | ✅ Adopt    | Error tracking, performance monitoring       | Excellent Next.js/Node.js integration    |
| UptimeRobot       | ✅ Adopt    | Uptime monitoring, status pages              | Free tier covers most needs              |
| LogRocket         | 🔬 Trial    | Session replay, frontend observability       | Valuable for debugging UX issues         |
| Grafana           | 🔍 Assess   | Metrics visualization, dashboards            | Powerful but requires infrastructure     |
| Prometheus        | 🔍 Assess   | Metrics collection                           | Pairs with Grafana, complex setup        |
| New Relic         | 🔍 Assess   | Full-stack APM                               | Comprehensive but expensive at scale     |
| Axiom             | 🔬 Trial    | Log management and analytics                 | Generous free tier, modern alternative to ELK |
| Pino              | ✅ Adopt    | Structured JSON logging (Node.js)            | Fastest Node.js logger, production-grade |
| Winston           | ⛔ Hold     | Node.js logging                              | Pino preferred — faster, structured      |

---

### 3.16 Security Tooling

| Technology        | Category    | Primary Use Case                             | Notes                                    |
|-------------------|-------------|----------------------------------------------|------------------------------------------|
| npm audit         | ✅ Adopt   | Node.js dependency vulnerability scanning    | Built-in, zero setup, run in CI          |
| gitleaks          | ✅ Adopt   | Secret detection in Git history              | Pre-commit hook, prevents credential leaks |
| Snyk              | 🔬 Trial   | Multi-language vulnerability scanning        | Deeper analysis than npm audit           |
| Trivy             | 🔬 Trial   | Container + dependency + IaC scanning        | Aqua Security, comprehensive             |
| OWASP ZAP         | 🔬 Trial   | Dynamic application security testing (DAST)  | Automated security scanning in CI        |
| SonarQube         | 🔬 Trial   | SAST + code quality (security rules)         | Also listed in Code Quality              |
| Socket.dev        | 🔍 Assess  | Supply chain analysis for npm                | Detects malicious packages               |
| HashiCorp Vault   | 🔍 Assess  | Secrets management and rotation              | Enterprise-grade, complex for small teams |
| Dependabot        | ✅ Adopt   | Automated dependency update PRs              | GitHub-native, zero setup                |
| Renovate          | 🔬 Trial   | Automated dependency updates (advanced)      | More configurable than Dependabot        |

---

### 3.17 Messaging, Queues & Real-time

| Technology        | Category    | Primary Use Case                             | Notes                                    |
|-------------------|-------------|----------------------------------------------|------------------------------------------|
| Supabase Realtime | ✅ Adopt   | Real-time subscriptions (DB changes, presence)| Built-in with Supabase, zero extra infra |
| WebSocket (native)| 🔬 Trial   | Custom real-time communication               | Use only when Supabase Realtime is insufficient |
| Pusher            | 🔍 Assess  | Managed real-time messaging                  | Simple API, evaluate pricing at scale    |
| Upstash           | 🔍 Assess  | Serverless Redis + Kafka + QStash            | Pay-per-use, edge-compatible             |
| RabbitMQ          | 🔍 Assess  | Message broker, task queues                  | Add only when async processing is needed |
| BullMQ            | 🔍 Assess  | Node.js job queue (Redis-backed)             | Background jobs, scheduled tasks         |
| Apache Kafka      | ⛔ Hold    | Event streaming                              | Enterprise-scale, massive overkill currently |

---

### 3.18 Payments

| Technology        | Category    | Primary Use Case                             | Notes                                    |
|-------------------|-------------|----------------------------------------------|------------------------------------------|
| Stripe            | ✅ Adopt    | Payment processing, subscriptions, invoicing | Supports MB WAY in PT, best-in-class DX |
| Easypay           | 🔍 Assess   | Portuguese payment methods (MB WAY, Multibanco, MB references) | Local provider, relevant for PT market |
| ifthenpay         | 🔍 Assess   | Portuguese payment methods (MB WAY, Multibanco) | Alternative to Easypay, simpler API    |
| LemonSqueezy      | 🔍 Assess   | Merchant of Record (handles VAT/tax)         | Simpler than Stripe for digital products |
| PayPal            | ⛔ Hold     | —                                            | Stripe preferred for developer experience |

---

### 3.19 Date & Time

| Technology        | Category    | Primary Use Case                             | Notes                                    |
|-------------------|-------------|----------------------------------------------|------------------------------------------|
| Temporal API      | 🔬 Trial    | Native date/time handling (ES2026)           | Stage 4, Chrome+Firefox+Edge shipped. Safari pending. Zero bundle cost. |
| date-fns          | ✅ Adopt    | Date manipulation and formatting             | v4, tree-shakeable, excellent TS support. Fallback until Temporal is universal. |
| date-fns-tz       | ✅ Adopt    | Timezone conversions (with date-fns)         | Required companion for timezone work with date-fns |
| Day.js            | 🔍 Assess   | Lightweight date manipulation                | ~2KB, Moment-compatible API, plugin-based |
| Luxon             | 🔍 Assess   | Timezone-rich date handling                  | Best pre-Temporal TZ support, larger bundle (~23KB) |
| Moment.js         | ⛔ Hold     | —                                            | Legacy, maintenance mode. Never for new projects. |

---

### 3.20 Build Tooling

| Technology        | Category    | Primary Use Case                             | Notes                                    |
|-------------------|-------------|----------------------------------------------|------------------------------------------|
| Vite              | ✅ Adopt    | Dev server and build tool                    | Fast HMR, used by Astro/SvelteKit too   |
| Turbopack         | ✅ Adopt    | Next.js default bundler (dev + production)   | Stable since Next.js 16, 2-5x faster builds |
| Turborepo         | 🔍 Assess   | Monorepo build orchestration                 | Relevant when managing multiple packages |
| Webpack           | ⛔ Hold     | Legacy bundler                               | Turbopack is now default in Next.js 16   |
| esbuild           | 🔬 Trial    | Ultra-fast JS/TS bundler                     | Used internally by Vite, useful standalone for libraries |

---

### 3.21 Email Services

| Technology        | Category    | Primary Use Case                             | Notes                                    |
|-------------------|-------------|----------------------------------------------|------------------------------------------|
| Resend            | 🔬 Trial   | Transactional email (API-first)              | Excellent DX, pairs with react-email     |
| react-email       | 🔬 Trial   | Email templates with React components        | Build emails like UI components          |
| Nodemailer        | ✅ Adopt   | SMTP email sending (Node.js)                 | Low-level, works with any SMTP provider  |
| SendGrid          | 🔍 Assess  | Transactional + marketing email              | Established but heavier than Resend      |
| Mailgun           | 🔍 Assess  | Transactional email                          | Developer-focused, reliable delivery     |

---

### 3.22 SEO & Web Analytics

| Technology              | Category    | Primary Use Case                             | Notes                                    |
|-------------------------|-------------|----------------------------------------------|------------------------------------------|
| Google Search Console   | ✅ Adopt   | Search indexation monitoring, crawl errors   | Free, essential for any public site      |
| Google Lighthouse       | ✅ Adopt   | Performance, SEO, a11y audits                | Built into Chrome DevTools, CI-compatible|
| Google Analytics (GA4)  | 🔬 Trial   | Traffic analytics, user behavior             | RGPD compliance requires consent banner  |
| Vercel Analytics        | 🔬 Trial   | Web Vitals, performance in production        | Native Vercel integration, privacy-friendly |
| Plausible               | 🔍 Assess  | Privacy-first analytics (no cookies)         | RGPD-compliant by default, EU-hosted     |
| Semrush / Ahrefs        | 🔍 Assess  | SEO research, keyword analysis, backlinks    | Paid tools, relevant for client projects |

### 3.23 Internationalization (i18n)

| Technology        | Category    | Primary Use Case                             | Notes                                    |
|-------------------|-------------|----------------------------------------------|------------------------------------------|
| next-intl         | ✅ Adopt   | i18n for Next.js (App Router)                | Type-safe, Server Components compatible  |
| react-i18next     | 🔬 Trial   | i18n for React (Vite SPAs, non-Next.js)      | Most popular React i18n, large ecosystem |
| i18next           | 🔬 Trial   | Framework-agnostic i18n core                 | Foundation of react-i18next              |
| FormatJS (react-intl) | 🔍 Assess | ICU message format, advanced pluralization | More complex API, powerful for complex locales |

---

### 3.24 LLM Providers & Gateways

| Technology        | Category    | Primary Use Case                             | Notes                                    |
|-------------------|-------------|----------------------------------------------|------------------------------------------|
| Anthropic API (Claude) | ✅ Adopt | LLM for reasoning, coding, agents, document analysis | Opus 4.8 (1M context window), strong tool-use. Default for reasoning-heavy and agentic work. Use prompt caching to cut cost on stable system prompts. |
| OpenAI API        | ✅ Adopt   | LLM, embeddings, realtime/voice, broad tooling | GPT-5.5; widest ecosystem. Source for embeddings and the Realtime API (voice). Evaluate cost per use case. |
| Google Gemini API | ✅ Adopt   | High-volume, long-context, multimodal, cost-sensitive | Gemini 3.x/2.5 Flash & Flash-Lite: lowest cost/highest speed of the three providers, 1M context. Default for cost-sensitive and high-volume work. MUST use the paid tier (free tier trains on data + is EU-restricted). |
| AI Gateway (Vercel AI Gateway / OpenRouter) | 🔬 Trial | Provider routing, fallback, cost control, caching | Single endpoint to swap providers; centralizes keys, caching, and per-app budgets. Reduces lock-in to one provider. |

---

### 3.25 Local & Self-Hosted Inference

| Technology        | Category    | Primary Use Case                             | Notes                                    |
|-------------------|-------------|----------------------------------------------|------------------------------------------|
| Ollama            | 🔬 Trial   | Local model serving for dev/prototyping       | Easiest local runtime; binds to localhost by default. Use for RGPD-sensitive dev and offline iteration. Open-weight families: Qwen3, Gemma, Phi-4. |
| vLLM              | 🔍 Assess  | Production-grade self-hosted serving           | OpenAI-compatible API; high-throughput, continuous batching. Needs a GPU host behind a reverse proxy with auth. → See [07-security-standards.md] |
| llama.cpp         | 🔍 Assess  | CPU / GGUF / Apple Silicon inference           | Lower-level; quantized models, fine control. Foundation of much of the local ecosystem. |
| LM Studio         | 🔍 Assess  | Desktop GUI for local model testing            | Non-technical / quick evaluation. Not a production serving path. |

---

### 3.26 AI SDKs & Agent Frameworks

| Technology        | Category    | Primary Use Case                             | Notes                                    |
|-------------------|-------------|----------------------------------------------|------------------------------------------|
| Vercel AI SDK     | 🔬 Trial   | AI features & agents in TS/Next.js (front + API) | De facto TS standard (v6): useChat, streamText, tool-calling with Zod, agent loops. Default for the TS side of the stack. |
| LangGraph         | 🔬 Trial   | Stateful, production agents (Python/JS)        | Graph state machine, human-in-the-loop, durable execution. Fits FastAPI agent backends. |
| LlamaIndex        | 🔬 Trial   | RAG / document indexing & document agents      | Strong indexing + retrieval primitives. Relevant to the document-assistant use case. |
| Mastra            | 🔍 Assess  | TS-first batteries-included agent framework    | Growing fast; native MCP support. Assess vs Vercel AI SDK for the TS agent path. |
| Pydantic AI       | 🔍 Assess  | Type-safe Python-first agents                  | Structured outputs + validation + DI. Clean fit for Python services. |
| LangChain         | 🔍 Assess  | LLM app framework (broad components)           | Useful components, fast-moving API. Prefer LangGraph for the production agent layer. |
| CrewAI            | 🔍 Assess  | Role-based multi-agent prototyping             | Lowest learning curve for multi-agent demos. Watch for complexity hiding at production scale. |
| Claude Agent SDK / OpenAI Agents SDK | 🔍 Assess | Vendor-native agent frameworks | Claude-native and OpenAI-first respectively. Assess when locked to one provider. |

---

### 3.27 Document Ingestion & Parsing

| Technology        | Category    | Primary Use Case                             | Notes                                    |
|-------------------|-------------|----------------------------------------------|------------------------------------------|
| Docling           | 🔬 Trial   | Layout-aware PDF/doc parsing for RAG (self-hosted) | Open-source (IBM); strong table-structure recognition. Self-hostable → RGPD-friendly. Default ingestion choice for invoices, fiscal docs, contracts. |
| PyMuPDF4LLM       | 🔬 Trial   | Fast, simple text extraction → Markdown        | Lightweight, fastest option. Use when documents are text-clean and layout is simple (no complex tables). |
| LlamaParse        | 🔍 Assess  | Vision-based parsing of complex layouts (API)  | Excellent on complex tables/figures, but cloud-only — no on-prem path. Excludes it from data-sensitive (RGPD) pipelines. |
| Unstructured      | 🔍 Assess  | Multi-format ingestion (PDF, email, HTML, Office) | Broad format coverage + OCR. Table extraction inconsistent on complex/merged cells; expect post-processing. |

---

### 3.28 RAG Storage & Retrieval

| Technology        | Category    | Primary Use Case                             | Notes                                    |
|-------------------|-------------|----------------------------------------------|------------------------------------------|
| pgvector (Supabase) | ✅ Adopt  | Vector storage co-located with relational data | Default for RAG. Embeddings live beside app data; supports hybrid (vector + FTS) and metadata filters. Add a dedicated vector DB only when a measured need exists. → See [04-database-standards.md] (HNSW indexing, RLS) |
| Qdrant            | 🔬 Trial   | Dedicated vector DB (filtered + hybrid at scale) | Open-source, rich payload filtering, production-grade. Trial when pgvector's filtering/scale is insufficient. |
| Pinecone          | 🔍 Assess  | Managed vector DB at large scale               | Zero-ops, scales well. Evaluate pricing vs self-hosted. |
| Chroma            | 🔍 Assess  | Prototyping / local experiments                | Fast to start; not a production target. Migrate to pgvector/Qdrant for real workloads. |
| Neo4j (Graph RAG) | 🔍 Assess  | Knowledge-graph retrieval (Graph RAG)          | For relationship-heavy retrieval. Add only when flat vector retrieval proves insufficient. |
| Embedding models  | 🔬 Trial   | Converting text/docs to vectors                | OpenAI text-embedding-3, Cohere, nomic-embed (open), Qwen3-Embedding. For PT, prefer strong multilingual models. Train/serve consistency matters. |
| Rerankers         | 🔬 Trial   | Re-scoring top-K retrieval for precision       | Near-standard production step. BGE-reranker-v2-m3 (open, multilingual — good for PT, no recurring cost); Cohere Rerank 3.5 (API). |
| Web retrieval APIs| 🔍 Assess  | Web-enhanced RAG (W-RAG), live grounding       | Tavily, Exa, Firecrawl. For answers needing fresh/public web data alongside the corpus. |

---

### 3.29 LLM Observability & Evaluation

| Technology        | Category    | Primary Use Case                             | Notes                                    |
|-------------------|-------------|----------------------------------------------|------------------------------------------|
| Langfuse          | 🔬 Trial   | Tracing, cost, prompt mgmt for LLM/agent apps  | Open-source leader; self-hostable, framework-agnostic (Python + TS SDKs). Acquired by ClickHouse (Jan 2026) — governance roadmap to watch. → See [08-observability.md] |
| Ragas             | 🔬 Trial   | RAG evaluation (faithfulness, relevance, recall) | The evaluation loop that turns RAG from "vibes" to evidence. Pairs with a golden test set. Core to the document-assistant use case. |
| DeepEval          | 🔍 Assess  | General LLM evaluation / regression testing    | Model-agnostic test interfaces beyond RAG (reasoning, factual accuracy). Assess alongside Ragas. |
| Helicone          | 🔍 Assess  | Drop-in proxy for multi-provider cost/latency  | Simplest install; fast cost visibility across providers. Lighter than full observability platforms. |
| LangSmith         | 🔍 Assess  | Deep tracing for LangChain/LangGraph stacks    | Deepest LangChain/LangGraph integration, proprietary. Assess only if the stack goes LangChain-heavy. |

---

### 3.30 Agent Protocols & Interoperability

| Technology        | Category    | Primary Use Case                             | Notes                                    |
|-------------------|-------------|----------------------------------------------|------------------------------------------|
| MCP (Model Context Protocol) | 🔬 Trial | Standard for connecting agents to tools/data | De facto standard, vendor-neutral (Linux Foundation / Agentic AI Foundation). The integration layer for the personal-assistant and booking use cases. Strong Adopt candidate. → See [07-security-standards.md] (server auth, OAuth) |
| A2A (Agent-to-Agent) | 🔍 Assess | Cross-agent communication                   | Google-originated protocol for agents talking to agents. Relevant only for multi-agent systems — not yet needed. |
| AGENTS.md         | 🔍 Assess  | Repo-level instructions for coding agents      | Convention for telling agents about a codebase. Ties to the Claude Code workflow; track as it stabilizes. |

> **Consuming MCP — direct tool-calls vs code execution.** By default an MCP client loads every
> tool definition into context and routes intermediate results through the model — token-heavy at
> scale (static tool loading degrades past a few dozen tools). Anthropic's *code-execution-with-MCP*
> pattern instead exposes servers as code APIs the model calls from a sandbox, discovering tools on
> demand (progressive disclosure) and keeping intermediate data out of context — one Anthropic
> workflow dropped ~150K → ~2K tokens (~98.7%). A **cost/latency** optimization, not a capability
> one; it requires a code-execution sandbox (→ §3.32; [12-ai-engineering.md, §6.2/§6.8]).

---

### 3.31 AI Channels & Modalities

| Technology        | Category    | Primary Use Case                             | Notes                                    |
|-------------------|-------------|----------------------------------------------|------------------------------------------|
| WhatsApp Business Cloud API | 🔍 Assess | Conversational channel (support, booking) | Official channel for client/commercial bots. Requires a BSP + Meta business verification + template approval. Per-message pricing: customer-initiated/service messages (within 24h window) are free; cost is in business-initiated utility templates. Since Jan 2026 Meta allows only task-specific agents, not general-purpose bots. |
| Web chat widget (via Vercel AI SDK) | 🔍 Assess | Embedded site assistant (business FAQ / Q&A) | Cheapest channel; built on useChat/streamText. Pair with a low-cost model behind an AI Gateway with caching + per-site rate limiting. Enforce strict grounding + refusal on out-of-scope queries. → See [03-api-design.md], §3.24, §3.26 |
| Unofficial WhatsApp libraries (Baileys) | 🚫 Hold | WhatsApp automation without the official API | Reverse-engineered multi-device protocol, WebSocket-based — lightweight, no Puppeteer (preferred over whatsapp-web.js / Venom, which spawn a headless Chromium and are RAM-heavy). Violates WhatsApp ToS; ban risk falls on the sending number. Acceptable ONLY for personal/internal projects where you own the risk (with consent, throttling, opt-out). NEVER for client deliverables — use the official Cloud API via a BSP. |
| Cal.com           | 🔍 Assess  | Scheduling/booking backend exposed as an agent tool | Open-core: code is AGPLv3 (self-hostable, but real infra + ops cost, and team/enterprise `ee/` features need a paid license); AGPLv3 copyleft has implications for closed commercial SaaS — review before reselling. Cloud Free tier = 1 individual user only. Platform API (white-label/embed) is paid per booking (~$0.50–$0.99/extra booking). Handles double-booking, timezones, buffers, reminders, calendar sync. Expose to the agent as a tool/MCP server. |
| Self-built scheduling / Easy!Appointments | 🔍 Assess | Simpler booking for single-business use cases | For one business with fixed services/staff, a custom slot manager on the existing stack (Next + PostgreSQL + Prisma) avoids licensing entirely and gives full control. Easy!Appointments (GPL) is a lighter ready-made alternative. Match the tool to scope — Cal.com is the heavy/complete end. |
| Speech-to-Text — Deepgram / ElevenLabs Scribe | 🔍 Assess | Voice input / transcription | Low-latency streaming STT with strong multilingual (incl. PT) support. Foundation of any voice channel. |
| Text-to-Speech — Cartesia / ElevenLabs | 🔍 Assess | Voice output | Cartesia leads on raw latency; ElevenLabs on voice quality/range. Choose by latency-vs-naturalness need. |
| Speech-to-Speech — OpenAI Realtime API | 🔍 Assess | Real-time voice agents (single integration) | Simplest realtime path but highest cost/hour. A self-built STT→LLM→TTS pipeline is cheaper and more controllable. Voice is a phase-2 modality — start with text. |

---

### 3.32 Agent Code-Execution Sandboxing

Running code an agent generated is running **untrusted** code (→ See [12-ai-engineering.md, §6.7]:
if the prompt is untrusted, the code is untrusted). Shared-kernel containers (Docker / runc)
isolate *trusted* app workloads (→ [09-devops-cicd.md]; [07-security-standards.md, §12]) but are
**not** a security boundary against untrusted code — one kernel exploit escapes to the host. Code
an agent wrote needs kernel-level isolation:

| Technology | Category | Primary Use Case | Notes |
|------------|----------|------------------|-------|
| gVisor | 🔍 Assess | User-space-kernel isolation for semi-/untrusted code | Intercepts syscalls in a user-space kernel — stronger than shared-kernel containers, lighter than a full VM. Powers Modal sandboxes. Middle rung of the isolation ladder. |
| Firecracker / Kata Containers (microVM) | 🔍 Assess | Hardware-level isolation for untrusted code (gold standard) | Dedicated guest kernel per sandbox via a lightweight VM — the boundary to use when an agent executes code derived from untrusted input. Firecracker powers AWS Lambda/Fargate and E2B; self-hosting either is real infra + ops cost. |
| Managed sandbox services — E2B, Modal, Daytona, Vercel / Cloudflare Sandbox | 🔍 Assess | Sandbox-as-a-service: ephemeral isolated execution for agent code | Per-session sandboxes provisioned via SDK. E2B = Firecracker microVM, purpose-built for untrusted agent code; Modal = gVisor + GPU; Daytona = container-based, fastest cold start (weaker isolation). Default path unless data residency forces self-host (→ [12-ai-engineering.md, §7.4]). |

> **Scope.** This entry is about isolating *agent-generated / untrusted* code, not app
> containerization — Docker stays ✅ Adopt for trusted app workloads (§4 profile; [09-devops-cicd.md]).
> The *when / why* an agent needs a sandbox lives in [12-ai-engineering.md, §6.8]; this radar owns
> the *what*. → See [07-security-standards.md, §12] (container hardening vs untrusted-code sandbox).

---

## 4. Technology Profiles

This section provides detailed profiles for every technology listed in the radar.
Each profile explains the reasoning behind its classification and provides guidance for decision-making.

> **This is a reference section** — not meant to be read top-to-bottom.
> Use the radar tables in [Section 3](#3-the-radar) to find the technology, then jump to its profile here.

### Profile Structure

Each profile follows a consistent format scaled to its radar category:

- **Adopt**: Full profile — what, why, when, when NOT, configuration baseline, key references
- **Trial**: Medium profile — what, why it is being trialed, what to observe, success criteria
- **Assess**: Short profile — what, why it is on the radar, when to reassess
- **Hold**: Minimal profile — why not, what to use instead

---

### 4.1 Languages

---

#### TypeScript — ✅ Adopt

**What it is:**
A statically-typed superset of JavaScript that compiles to plain JavaScript.
Adds a type system on top of JS, enabling compile-time error detection, better tooling (autocomplete,
refactoring), and self-documenting code through type annotations.

**Why Adopt:**
TypeScript is the foundation of the entire stack. It provides the type safety that
[01-core-principles.md, Section 2] defines as a non-negotiable principle. The cost of adopting
TypeScript (learning curve, compilation step) is paid once; the cost of NOT adopting it (runtime
type errors, lack of refactoring confidence, implicit contracts) is paid continuously.

**When to use:**
- All application code — frontend (React, Next.js), backend (Express, NestJS, API routes), and shared
  libraries
- Configuration files where supported (e.g., `next.config.ts`, `tailwind.config.ts`, `vitest.config.ts`)
- Scripts and utilities (prefer `.ts` over `.js` even for one-off scripts, using `tsx` for execution)

**When NOT to use:**
- Shell scripts and system automation — use Bash or Python instead
- Quick prototyping where types are genuinely counterproductive (rare — usually types help even in prototypes)
- Configuration files that do not support TypeScript natively (e.g., `.eslintrc.json`, `package.json`)

**Configuration baseline:**
- **MUST** enable `strict: true` in `tsconfig.json` — this is non-negotiable
- **MUST** enable `noUncheckedIndexedAccess: true` — prevents unsafe array/object access
- **SHOULD** enable `exactOptionalProperties: true` — distinguishes `undefined` from missing properties
- **MUST NOT** use `any` without documented justification — prefer `unknown` and type narrowing
- **SHOULD** use `tsx` (or `ts-node` with ESM) for running scripts directly without manual compilation

**Key references:**
- → See [01-core-principles.md, Section 2] — Type Safety First principle
- → See [01-core-principles.md, Section 7] — Naming conventions
- → See [05-frontend-standards.md] — TypeScript usage in React/Next.js context
- → See [03-api-design.md] — TypeScript usage in API contracts

---

#### JavaScript — ⛔ Hold

**Why Hold:** TypeScript provides all of JavaScript's capabilities plus type safety, better tooling,
and self-documenting code. Writing new code in plain JavaScript means opting out of the primary
quality control mechanism in the stack.

**What to use instead:** TypeScript with `strict: true` for all new code.

**Legacy note:** Existing JavaScript code does not need to be migrated immediately. When modifying
a `.js` file significantly, **SHOULD** convert it to `.ts` as part of the change.

---

#### Python — ✅ Adopt

**What it is:**
A high-level, interpreted programming language known for readability, extensive standard library,
and dominant position in AI/ML, data science, and automation.

**Why Adopt:**
Python is the de facto language for AI/ML, data processing, and automation scripting. Its ecosystem
(NumPy, Pandas, scikit-learn, FastAPI, LangChain) is unmatched in these domains. It complements
TypeScript — where TS handles web application code, Python handles data and automation workflows.

**When to use:**
- AI/ML projects, model training, inference pipelines
- Data processing, ETL scripts, data analysis
- Automation and scripting (file processing, API integrations, scheduled tasks)
- Backend APIs when the project is Python-centric (FastAPI)

**When NOT to use:**
- Web application frontends — use TypeScript + React
- Web backends when the rest of the stack is TypeScript — keep the stack consistent unless Python
  offers a specific advantage (e.g., AI/ML integration)
- Performance-critical real-time systems — Python's GIL and interpreted nature are limiting

**Configuration baseline:**
- **SHOULD** use Python 3.11+ (performance improvements, better error messages)
- **SHOULD** use type hints consistently (`from typing import ...` or built-in generics in 3.10+)
- **SHOULD** use a virtual environment manager (`venv`, `poetry`, or `uv`)
- **SHOULD** use a linter and formatter (`ruff` is the modern all-in-one choice)
- **SHOULD** pin dependencies with lock files (`poetry.lock`, `uv.lock`, or `pip-compile` output)

**Key references:**
- → See [01-core-principles.md, Section 10] — Dependency management applies equally to Python packages
- → See [07-security-standards.md, Section 11] — pip audit for vulnerability scanning

---

#### SQL — ✅ Adopt

**Why Adopt:** SQL is the language of relational databases. There is no alternative for defining
schemas, writing migrations, complex queries, and database functions. ORMs abstract it but do not
replace the need to understand it.

**Dialect:** PostgreSQL SQL → See [04-database-standards.md] for conventions.

**Guidance:** Every developer **SHOULD** be comfortable writing raw SQL for queries, migrations,
and debugging — even when using an ORM. The ORM is a convenience layer, not a replacement for
SQL literacy.

---

#### HTML / CSS — ✅ Adopt

**Why Adopt:** Foundational web technologies. Regardless of frameworks and abstractions (JSX,
Tailwind, CSS-in-JS), the output is always HTML and CSS. Understanding the fundamentals is
non-negotiable for frontend quality, accessibility, and debugging.

**Guidance:** Proficiency in semantic HTML and CSS layout (Flexbox, Grid) is a prerequisite.
Tailwind CSS (→ Adopt) is the styling tool, but it generates CSS — understanding what it generates
is essential for debugging and for cases where Tailwind alone is insufficient.

---

### 4.2 Frontend Frameworks

---

#### React — ✅ Adopt

**What it is:**
A JavaScript library for building user interfaces through composable, declarative components.
Maintained by Meta with the largest frontend ecosystem in terms of packages, tooling, and community.

**Why Adopt:**
React is the UI layer of the stack, used via Next.js for full applications and via Vite for
lightweight SPAs. Its component model aligns with the separation of concerns principle
(→ See [01-core-principles.md, Section 6]), and its ecosystem provides solutions for virtually every
UI challenge. The hiring market and community support are unmatched.

**When to use:**
- All interactive user interfaces — via Next.js (default) or Vite + React (SPAs)
- Shared component libraries
- Email templates (via react-email)

**When NOT to use:**
- Content-heavy static sites with minimal interactivity — consider Astro (which can still use
  React components for interactive islands)
- Non-web contexts (CLI tools, scripts, data pipelines) — wrong tool entirely

**Key patterns:**
- **MUST** prefer Server Components by default in Next.js — add `'use client'` only when the
  component needs browser APIs, event handlers, or React hooks that require client state
- **MUST** keep components focused — a component does one thing well
  (→ See [01-core-principles.md, Section 4 — SRP])
- **SHOULD** extract business logic into hooks or service functions — components should orchestrate
  UI, not contain business rules
- **MUST NOT** use `useEffect` for data fetching in new code — use Server Components or TanStack Query

**Key references:**
- → See [05-frontend-standards.md] — Detailed React patterns, component structure, accessibility
- → See [01-core-principles.md, Section 6] — Separation of concerns and layering

---

#### Next.js — ✅ Adopt

**What it is:**
A full-stack React framework by Vercel that provides server-side rendering (SSR), static site
generation (SSG), API routes, file-based routing, middleware, and optimized production builds.
Next.js 16 (current, Oct 2025) uses Turbopack as the default bundler, includes React 19.2 with
View Transitions and Activity, and introduces Cache Components with the `"use cache"` directive.

**Why Adopt:**
Next.js is the default framework for web applications. It eliminates the need to assemble
a custom stack (routing, SSR, API layer, build config) and provides production-grade defaults.
The App Router enables React Server Components, nested layouts, and streaming. Version 16
stabilized Turbopack for production, introduced explicit opt-in caching (replacing the implicit
caching of earlier versions), and the React Compiler is now stable for automatic memoization.

**When to use:**
- Full-stack web applications (the default choice)
- SEO-critical sites that need server rendering
- Applications that combine frontend UI with backend API routes
- Projects deployed to Vercel (optimized integration) or any Node.js hosting

**When NOT to use:**
- Pure SPAs with no SEO requirements and no server-side logic — use Vite + React (simpler, lighter)
- Content-heavy static sites with minimal interactivity — consider Astro
- Projects where the backend is a separate service (Python, NestJS) and the frontend is purely
  client-side — Vite + React may be simpler

**Configuration baseline (v16+):**
- **MUST** use App Router (not Pages Router) for all new projects
- **MUST** prefer Server Components by default
- **MUST** use async request APIs (`params`, `searchParams` are now Promises) — synchronous
  access was removed in v16
- **SHOULD** use Route Handlers (`app/api/`) for API endpoints
- **SHOULD** use `next.config.ts` (TypeScript config)
- **SHOULD** enable `reactCompiler: true` for automatic memoization (stable in v16)
- **MAY** use `"use cache"` directive for explicit caching of pages, components, and functions
- Turbopack is the default bundler — no `--turbopack` flag needed (use `--webpack` to opt out)

**Key references:**
- → See [03-api-design.md] — API route conventions within Next.js
- → See [05-frontend-standards.md] — Next.js-specific frontend patterns
- → See [09-devops-cicd.md] — Deployment and environment configuration

---

#### Vite + React — ✅ Adopt

**What it is:**
A development pattern combining Vite (fast build tool and dev server) with React and TypeScript
to create lightweight Single Page Applications without the overhead of a full-stack framework.

**Why Adopt:**
Not every project needs SSR, API routes, or server-side logic. For internal tools, admin
dashboards, prototypes, and client-side applications, Vite + React provides a faster setup,
simpler mental model, and lighter output than Next.js.

**When to use:**
- Internal tools and admin dashboards (no SEO needed)
- Interactive prototypes and proof of concepts
- Client-side applications that consume an external API
- Projects where the backend is a separate service

**When NOT to use:**
- Any project that needs SEO — SPAs have poor default indexability
- Projects that need API routes, authentication, or server-side logic — use Next.js
- Content sites, blogs, marketing pages — use Astro

**Configuration baseline:**
- **MUST** scaffold with TypeScript: `npm create vite@latest my-app -- --template react-ts`
- **MUST** add ESLint, Prettier, and Tailwind CSS to match the standard tooling
- **SHOULD** use the same project structure conventions as Next.js where applicable
  (features/, services/, schemas/, lib/)

---

#### Astro — 🔬 Trial

**What it is:**
A web framework optimized for content-heavy sites. Generates static HTML by default and loads
JavaScript only where explicitly needed (islands architecture). Supports React, Vue, and Svelte
components within the same project.

**Why Trial:**
For freelance projects (business websites, landing pages, marketing sites), Astro offers superior
performance, perfect SEO, and simpler hosting (static deploy) compared to Next.js. Its ability to
use React components for interactive sections means existing component skills transfer directly.

**What to observe during trial:**
- Developer experience compared to Next.js for content sites
- Build times and deployment simplicity (static hosting vs Node.js server)
- Component reuse — can React components be shared between Astro and Next.js projects?
- Content management patterns (Markdown, MDX, CMS integration)

**Success criteria for promotion to Adopt:**
- Successfully shipped at least one client-facing content site
- Deployment and maintenance overhead is measurably lower than Next.js for the same type of project
- No significant pain points with routing, styling, or interactive components

---

#### Svelte / SvelteKit — 🔍 Assess

**What it is:** A reactive UI framework that compiles components to vanilla JavaScript at build
time, eliminating the need for a virtual DOM. SvelteKit is its full-stack framework (like Next.js
for React).

**Why on the radar:** Excellent developer experience, smaller bundle sizes, and growing ecosystem.
Worth monitoring as a potential alternative to React for specific project types.

**When to reassess:** When the team has bandwidth for experimentation beyond the core stack, or
if a project requirement specifically favors Svelte's strengths (e.g., animation-heavy interfaces).

---

#### Vue.js — ⛔ Hold

**Why Hold:** React is the established UI library in the current stack. Vue is excellent but
adopting it would split frontend expertise across two ecosystems without clear benefit.

**What to use instead:** React (via Next.js or Vite).

---

#### Angular — ⛔ Hold

**Why Hold:** Angular's opinionated, enterprise-oriented architecture (dependency injection,
decorators, modules, RxJS) adds significant complexity that is not justified for the current
project scale and team size.

**What to use instead:** Next.js for full-stack apps, NestJS (🔬 Trial) if the desire is for
a structured, opinionated backend framework — NestJS is heavily inspired by Angular's architecture.

---

### 4.3 Styling

---

#### Tailwind CSS — ✅ Adopt

**What it is:**
A utility-first CSS framework that provides low-level utility classes (e.g., `flex`, `p-4`,
`text-sm`, `bg-blue-500`) as building blocks for UI design. Instead of writing custom CSS,
you compose styles directly in the markup using predefined classes. Tailwind v4 (current)
is a ground-up rewrite with a Rust-based Oxide engine and CSS-native configuration.

**Why Adopt:**
Tailwind eliminates the two biggest pain points of CSS at scale: naming things and managing
specificity. With utility classes, there is no need to invent class names (`.card-wrapper-inner`),
no specificity wars, and no dead CSS accumulation. Version 4 moves design tokens directly into
CSS via `@theme` directives, making tokens inspectable in DevTools and enabling runtime theme
switching without rebuilds. The Oxide engine delivers 5-10x faster builds.

**When to use:**
- All styling in React/Next.js and Astro projects — it is the default styling approach
- Responsive design — Tailwind's mobile-first breakpoints (`sm:`, `md:`, `lg:`) enforce the
  correct approach by design
- Design systems — use `@theme` directives in CSS to define colors, spacing, typography as tokens
- Container queries — built-in support in v4 via `@container` and `@md:`, `@lg:` utilities

**When NOT to use:**
- Highly dynamic styles that depend on runtime values (e.g., a color picker that sets any hex
  value) — use inline `style` for truly dynamic values
- Complex CSS animations that would result in unreadable class strings — extract to a CSS Module
  or `@keyframes` in a global stylesheet
- Third-party component libraries that ship their own styling system — do not fight the library

**Configuration baseline (v4):**
- **MUST** use CSS-native configuration — `@import "tailwindcss"` and `@theme` directives in CSS
  replace the old `tailwind.config.js` / `tailwind.config.ts` file
- **MUST** follow mobile-first approach — base styles apply to mobile, responsive modifiers add
  complexity for larger screens
- **MUST** define design tokens in `@theme` blocks in your CSS file — these become CSS custom
  properties automatically
- **SHOULD** use `tailwind-merge` (via `cn()` utility) to handle conditional class merging without
  conflicts — this is the standard pattern in shadcn/ui
- **SHOULD** install the Tailwind CSS IntelliSense VS Code extension v4+ for autocomplete
- **SHOULD** use `npx @tailwindcss/upgrade` when migrating from v3 — handles ~90% of changes
  automatically (class renames, config migration)
- **MUST NOT** overuse `@apply` — it defeats the purpose of utility-first. Extract to components
  instead of creating CSS abstractions

**Migration note (v3 → v4):**
- `tailwind.config.js` / `tailwind.config.ts` → `@theme` directives in CSS
- `@tailwind base/components/utilities` → `@import "tailwindcss"`
- Gradient classes renamed: `bg-gradient-to-r` → `bg-linear-to-r`
- Flexbox shorthand renamed: `flex-shrink-0` → `shrink-0`, `flex-grow` → `grow`
- PostCSS plugin changed: `tailwindcss` → `@tailwindcss/postcss`
- Vite plugin available: `@tailwindcss/vite` (no PostCSS needed)

**Key references:**
- → See [05-frontend-standards.md] — Detailed styling patterns and responsive design conventions
- → See [01-core-principles.md, Section 1.2] — Simplicity Is a Feature (Tailwind reduces CSS complexity)

---

#### CSS Modules — 🔬 Trial

**What it is:** A CSS file convention where class names are locally scoped to the component that
imports them, preventing global namespace collisions. Each `.module.css` file generates unique
class names at build time.

**Why Trial:** For the rare cases where Tailwind utilities are insufficient — complex animations,
deeply nested selectors, or styles that are genuinely more readable as traditional CSS. CSS Modules
provide scoping without the runtime cost of CSS-in-JS.

**What to observe during trial:**
- How often does the need actually arise? If it is rare, the feature is a good escape hatch. If
  it becomes frequent, the styling approach may need revisiting.
- Are the resulting styles easy to maintain alongside Tailwind? Watch for inconsistency.

**Success criteria:** Useful as an occasional escape hatch without creating a parallel styling system.

---

#### Sass / SCSS — ⛔ Hold

**Why Hold:** Tailwind CSS covers the vast majority of styling needs. Sass features (variables,
nesting, mixins) are either handled by Tailwind's config (variables → tokens, mixins → components)
or by modern CSS (native nesting, custom properties). Adding Sass introduces a preprocessor
dependency without proportional value.

**What to use instead:** Tailwind CSS for utilities, CSS Modules for scoped complex styles.

---

#### styled-components — ⛔ Hold

**Why Hold:** Runtime CSS-in-JS libraries inject styles via JavaScript at runtime, which adds
bundle size, creates a performance cost on every render, and conflicts with React Server Components
(which cannot run client-side JavaScript). The React ecosystem is moving away from runtime CSS-in-JS.

**What to use instead:** Tailwind CSS (zero-runtime) or CSS Modules (build-time scoping).

---

#### Emotion — ⛔ Hold

**Why Hold:** Same concerns as styled-components — runtime CSS-in-JS with performance overhead and
Server Component incompatibility. Emotion and styled-components solve the same problem in the same
way, and both are being superseded by zero-runtime approaches.

**What to use instead:** Tailwind CSS or CSS Modules.

---

### 4.4 UI Component Libraries

---

#### shadcn/ui — ✅ Adopt

**What it is:**
A collection of accessible, well-designed UI components built on top of Radix UI primitives and
styled with Tailwind CSS. Unlike traditional component libraries (MUI, Chakra), shadcn/ui uses a
copy-paste model — you add components directly into your project source code, giving you full
ownership and customization control.

**Why Adopt:**
shadcn/ui solves the biggest problem with component libraries: the moment you need to customize
beyond what the library allows, you fight the library. With shadcn/ui, the code is yours from day
one. It is accessible (built on Radix), beautiful by default, and fully customizable because it
lives in your codebase. The `cn()` utility (tailwind-merge + clsx) becomes a standard pattern
across the project.

**When to use:**
- Any React/Next.js project that needs UI components (forms, dialogs, tables, navigation, etc.)
- Projects where design consistency matters but full design-system-from-scratch is not justified
- As the starting point for a custom component library — start with shadcn, customize to match
  the brand

**When NOT to use:**
- Non-React projects (Astro content pages that do not use React islands, for example)
- When a completely unique visual identity is required from scratch — shadcn gives you a head start,
  but heavily customizing every component may not save time over building from primitives directly

**Configuration baseline:**
- **MUST** initialize with `npx shadcn@latest init` and select the project's design tokens
- **MUST** keep components in `src/components/ui/` — this is the convention and aligns with the
  standard project structure
- **SHOULD** customize the theme in `tailwind.config.ts` and `globals.css` CSS variables to match
  the project's brand before adding components
- **SHOULD** only add the components you actually need — do not install the entire library

**Key references:**
- → See [05-frontend-standards.md] — Component structure and accessibility standards
- Pairs with: Radix UI (primitives), Tailwind CSS (styling), react-hook-form + Zod (forms)

---

#### Radix UI — ✅ Adopt

**What it is:**
A library of unstyled, accessible UI primitives (Dialog, Dropdown, Tooltip, Accordion, etc.) that
handle complex interaction patterns (focus management, keyboard navigation, ARIA attributes) while
leaving visual design entirely to you.

**Why Adopt:**
Accessibility is hard to implement correctly. Radix solves the hardest parts — keyboard navigation,
screen reader support, focus trapping — so you do not have to. It is the foundation that shadcn/ui
is built upon. Even when not using shadcn, Radix primitives are the recommended starting point for
custom interactive components.

**When to use:**
- Building custom interactive components that need accessibility (dialogs, dropdowns, tooltips,
  popovers, tabs, accordions)
- When shadcn/ui components need deeper customization — drop down to the Radix primitive

**When NOT to use:**
- Simple elements that do not need complex interaction patterns — a styled `<button>` does not need
  a Radix primitive
- When shadcn/ui already provides the component you need — use shadcn, which wraps Radix with
  sensible defaults

---

#### Headless UI — 🔬 Trial

**What it is:** A set of unstyled, accessible UI components from Tailwind Labs (the team behind
Tailwind CSS). Similar in concept to Radix UI but with a smaller component set.

**Why Trial:** Created by the Tailwind team, it has excellent Tailwind integration by design. Smaller
API surface than Radix, which means less to learn. Worth evaluating for projects where shadcn/ui is
not used but Tailwind is.

**What to observe:** Component coverage compared to Radix — does it cover the primitives you need?
If gaps appear frequently, Radix remains the better foundation.

---

#### Material UI (MUI) — ⛔ Hold

**Why Hold:** MUI is heavily opinionated with Material Design aesthetics that are difficult to
customize away from. It ships significant JavaScript and CSS runtime overhead, and its styling
system (Emotion-based) conflicts with the Tailwind-first approach and React Server Components.

**What to use instead:** shadcn/ui + Radix UI for accessible components with full styling control.

---

#### Chakra UI — ⛔ Hold

**Why Hold:** Chakra uses runtime CSS-in-JS (Emotion) with the same performance concerns as
styled-components. The project is undergoing a major rewrite (Ark UI + Panda CSS) which introduces
uncertainty. The current version is not compatible with React Server Components.

**What to use instead:** shadcn/ui + Radix UI.

---

### 4.5 Validation & Schema

---

#### Zod — ✅ Adopt

**What it is:**
A TypeScript-first schema validation library that lets you define a schema once and derive both
the runtime validation and the TypeScript type from it. This "single source of truth" pattern
eliminates the drift between what you validate at runtime and what TypeScript believes at compile
time.

**Why Adopt:**
Zod closes the gap between compile-time types and runtime reality. TypeScript types disappear at
runtime — they cannot catch invalid API responses, malformed user input, or misconfigured environment
variables. Zod schemas validate at runtime AND infer TypeScript types, meaning one definition
serves both purposes. This aligns directly with the Fail Fast principle
(→ See [01-core-principles.md, Section 2]) — invalid data is caught at the boundary, not deep inside
business logic.

**When to use:**
- API request validation — validate incoming data at the boundary (Route Handlers, Express
  middleware, NestJS pipes)
- API response validation — validate data received from external APIs before trusting it
- Form validation — pairs with react-hook-form via `@hookform/resolvers/zod`
- Environment variable validation — parse `process.env` through a schema at startup
  (fail fast if config is wrong)
- Any trust boundary — wherever data crosses from untrusted to trusted context

**When NOT to use:**
- Internal function parameters where TypeScript types are sufficient — adding Zod to every internal
  function is overengineering. Validate at boundaries, trust internally.
- Performance-critical hot paths where validation overhead matters — rare, but profile first
- Python projects — use Pydantic instead (Python's equivalent with similar philosophy)

**Configuration baseline:**
- **MUST** define schemas in a dedicated `schemas/` directory, organized by domain
- **MUST** use `z.infer<typeof schema>` to derive types — never manually duplicate the type
- **SHOULD** use `.transform()` for data normalization (trimming strings, converting formats)
- **SHOULD** use `.refine()` and `.superRefine()` for complex business validations
- **MUST NOT** use Zod inside React components directly — schemas belong in the schema layer,
  not the UI layer

**Key references:**
- → See [01-core-principles.md, Section 2] — Fail Fast, Type Safety First
- → See [03-api-design.md] — API validation patterns with Zod
- → See [07-security-standards.md, Section 3] — Input validation at trust boundaries

---

#### Yup — ⛔ Hold

**Why Hold:** Zod provides the same validation capabilities with superior TypeScript inference.
Yup's type inference requires manual type definitions, which creates drift risk.

**What to use instead:** Zod for all validation needs.

---

#### Joi — ⛔ Hold

**Why Hold:** Joi is Node.js-only (does not run in the browser), has no TypeScript type inference,
and is heavier than Zod. It was the standard before Zod existed but has been superseded.

**What to use instead:** Zod for Node.js and browser environments.

---

#### class-validator — 🔍 Assess

**What it is:** A decorator-based validation library commonly used with NestJS. Uses TypeScript
decorators on class properties to define validation rules.

**Why on the radar:** If NestJS (🔬 Trial) is adopted, class-validator is its natural validation
companion. The decorator approach aligns with NestJS's architecture.

**When to reassess:** When the decision on NestJS moves from Trial to Adopt or Hold, revisit
class-validator accordingly.

---

### 4.6 State Management

---

#### React Server Components — ✅ Adopt

**What it is:**
A React architecture pattern (stable in Next.js App Router) where components execute on the server
by default. Server Components can fetch data directly, access the database, read the filesystem,
and send only the rendered HTML to the client — with zero JavaScript shipped for those components.

**Why Adopt:**
Server Components fundamentally change state management strategy. Data that previously required
client-side fetching (useEffect + useState + loading states) can now be fetched directly in the
component on the server. This eliminates entire categories of client state and the bugs that come
with them (race conditions, stale data, waterfall requests).

**When to use:**
- **Default for all components in Next.js App Router** — every component is a Server Component
  unless marked with `'use client'`
- Data fetching — fetch directly in the component, no need for client-side state management
- Layouts and pages that display data but do not need interactivity

**When NOT to use (switch to Client Component):**
- Components that use browser APIs (window, document, localStorage)
- Components that need event handlers (onClick, onChange, onSubmit)
- Components that use React hooks requiring client state (useState, useReducer, useEffect)
- Components that use context providers

**Key rule:** Start as Server Component. Add `'use client'` only when you hit a specific
client-side requirement. Never add it preemptively.

---

#### React Hooks (useState / useReducer) — ✅ Adopt

**Why Adopt:** Built-in React primitives for local component state. No dependency, no overhead,
no abstraction leakage. Prefer these for all state that is local to a single component or a
small component subtree.

**Guidance:**
- `useState` for simple state (toggles, form fields, counters)
- `useReducer` for complex state with multiple related updates (form with many fields, state machines)
- **MUST NOT** lift state up to global stores just because multiple components need it — consider
  whether composition, props, or Context solves the problem first

---

#### React Context — ✅ Adopt

**Why Adopt:** Built-in React mechanism for sharing state across a component tree without prop
drilling. Zero dependencies, works with Server Components (as long as the provider is a Client
Component boundary).

**When to use:**
- Low-frequency updates that affect many components: theme, locale, authentication status,
  feature flags
- Data that changes rarely but is read widely

**When NOT to use:**
- High-frequency updates (e.g., real-time position, rapidly changing form state) — Context triggers
  re-renders on all consumers, causing performance issues
- Server state (data from APIs) — use TanStack Query instead
- Complex state logic with many actions — consider Zustand

**Key rule:** Context is for **distribution**, not for **state management**. If you find yourself
building a mini-Redux inside Context (reducer + dispatch + complex selectors), step back and
evaluate Zustand.

---

#### TanStack Query (React Query) — ✅ Adopt

**What it is:**
A library for managing server state (asynchronous data from APIs) in React applications. Handles
fetching, caching, synchronization, pagination, optimistic updates, and background re-fetching
with a declarative hook-based API.

**Why Adopt:**
Server state and client state are fundamentally different problems. Client state is synchronous
and controlled by the user. Server state is asynchronous, shared, and can become stale at any
moment. TanStack Query treats server state as a cache problem, providing automatic background
re-fetching, stale-while-revalidate patterns, request deduplication, and retry logic — all things
you would otherwise build manually (and incorrectly).

**When to use:**
- Any client-side data fetching in Client Components (Vite + React SPAs, or Client Components
  within Next.js that need real-time data)
- Data that needs caching, polling, or optimistic updates
- Complex data dependencies (queries that depend on other queries)
- Infinite scroll and pagination

**When NOT to use:**
- Server Components in Next.js — fetch directly on the server, no need for TanStack Query
- Static data that does not change (hardcoded config, constants)
- Simple one-off fetches in small prototypes where the full library is overkill

**Configuration baseline:**
- **MUST** configure a `QueryClientProvider` at the application root
- **SHOULD** set sensible defaults: `staleTime` (how long data is considered fresh),
  `gcTime` (how long unused data stays in cache)
- **SHOULD** use query keys that reflect the data identity — e.g., `['todos', userId]`
- **MUST NOT** use TanStack Query as a global state manager — it manages server state.
  For client state, use hooks, Context, or Zustand.

**Key references:**
- → See [05-frontend-standards.md] — Data fetching patterns
- → See [03-api-design.md] — API response format that TanStack Query consumes

---

#### Zustand — 🔬 Trial

**What it is:** A minimal, un-opinionated global state management library for React. Provides a
simple API (create a store, use a hook) without the boilerplate of Redux (no actions, no reducers,
no dispatch, no providers).

**Why Trial:** With Server Components + TanStack Query + Context, most projects do not need a
global state library. Zustand is the escape hatch for when you genuinely do — complex client-side
state shared across distant components (e.g., a multi-step wizard, a drawing canvas, a complex
filter system).

**What to observe during trial:**
- Does the use case truly require global state, or could composition + Context solve it?
- Is the API surface small enough that it does not fragment state management patterns in the project?

**Success criteria:** Clear, recurring use cases where built-in React primitives are insufficient.

---

#### Redux Toolkit — ⛔ Hold

**Why Hold:** Redux introduced essential patterns (single source of truth, immutable updates,
predictable state), but the boilerplate and complexity cost is not justified for current project
scale. Server Components + TanStack Query + Context + Zustand cover the state management spectrum
with significantly less overhead.

**What to use instead:** TanStack Query for server state, React hooks + Context for client state,
Zustand if global state is genuinely needed.

---

#### Jotai / Recoil — 🔍 Assess

**What it is:** Atomic state management libraries where state is defined as independent atoms
that components can subscribe to individually. Different mental model from both Redux (centralized
store) and Zustand (multiple stores).

**Why on the radar:** The atomic model is interesting for applications with highly granular,
independent pieces of state. Jotai is actively maintained and growing. Recoil (Meta) has uncertain
maintenance.

**When to reassess:** When a project has a clear use case for fine-grained state subscriptions
that Zustand does not handle well.

---

### 4.7 Backend Frameworks

---

#### Next.js API Routes (Route Handlers) — ✅ Adopt

**What it is:**
Server-side API endpoints defined within a Next.js application using the App Router convention.
Each file in `app/api/` exports HTTP method handlers (`GET`, `POST`, `PUT`, `DELETE`) that run
exclusively on the server. They share the same deployment, authentication context, and TypeScript
configuration as the frontend.

**Why Adopt:**
For full-stack Next.js applications, Route Handlers eliminate the need for a separate backend
service. The API lives alongside the frontend, shares types and schemas (Zod), and deploys as a
single unit. This reduces operational complexity (one deployment, one repository, one CI pipeline)
and aligns with the principle of starting simple
(→ See [01-core-principles.md, Section 12 — Non-Goals]).

**When to use:**
- Full-stack Next.js applications where the API serves primarily the co-located frontend
- CRUD operations, form submissions, authentication flows
- Lightweight backend logic that does not justify a separate service
- Webhook endpoints (Stripe, Supabase, third-party integrations)

**When NOT to use:**
- APIs consumed by multiple clients (mobile app, third-party integrations, microservices) — a
  standalone API service is more appropriate
- CPU-intensive or long-running operations — serverless functions have execution time limits
- Projects where the backend team and frontend team operate independently — separate services
  enable independent deployment and scaling
- When the business logic complexity outgrows what Route Handlers can organize cleanly — consider
  Express or NestJS

**Key patterns:**
- **MUST** validate all incoming data with Zod at the route handler level (trust boundary)
- **MUST** keep route handlers thin — they receive the request, validate input, call a service
  function, and return the response. Business logic belongs in `services/`
- **MUST NOT** import route handlers from client components — they are server-only code
- **SHOULD** use the standard response envelope defined in → See [03-api-design.md]

**Key references:**
- → See [03-api-design.md] — API design conventions, error handling, response envelopes
- → See [07-security-standards.md, Section 3] — Input validation at trust boundaries

---

#### Express.js — ✅ Adopt

**What it is:**
A minimal, un-opinionated web framework for Node.js that provides HTTP request handling, routing,
and middleware composition. The most widely used Node.js framework with the largest ecosystem of
middleware and plugins.

**Why Adopt:**
Express is the baseline for standalone Node.js APIs. When a project needs a backend separate from
the frontend (multi-client API, background processing service, microservice), Express provides the
simplest starting point with maximum flexibility. Its middleware pattern is straightforward to
understand and compose, and virtually every Node.js library provides Express-compatible middleware.

**When to use:**
- Standalone REST APIs that serve multiple clients (web, mobile, third-party)
- Backend services that do not need a frontend (worker services, API gateways)
- Projects where the team needs full control over the stack without framework opinions
- Quick API prototypes that may evolve into larger services

**When NOT to use:**
- Full-stack web applications with a React frontend — use Next.js (simpler, single deployment)
- Large-scale APIs where architectural structure is needed from day one — consider NestJS
- Projects where Express's un-opinionated nature leads to inconsistent patterns across the team

**Configuration baseline:**
- **MUST** use TypeScript (never plain JavaScript Express in new projects)
- **MUST** structure the application in layers: routes → controllers → services → repositories
  (→ See [01-core-principles.md, Section 6])
- **MUST** add error handling middleware that catches all errors and returns structured responses
- **MUST** add security middleware: `helmet` (security headers), `cors`, rate limiting
  (→ See [07-security-standards.md, Section 6])
- **SHOULD** use `express-async-errors` or a wrapper to handle async errors without try-catch in
  every route
- **SHOULD** use Zod for request validation via custom middleware

**Key references:**
- → See [03-api-design.md] — API design conventions (apply regardless of framework)
- → See [07-security-standards.md, Section 9] — Security headers configuration
- → See [07-security-standards.md, Section 6] — Rate limiting and abuse prevention

---

#### NestJS — 🔬 Trial

**What it is:**
A progressive, TypeScript-native Node.js framework that provides an opinionated architecture
inspired by Angular — modules, controllers, services, dependency injection, decorators, and
guards. Built on top of Express (default) or Fastify.

**Why Trial:**
NestJS solves Express's biggest weakness: lack of structure. As projects grow, Express applications
tend to become disorganized because the framework provides no architectural guidance. NestJS
enforces separation of concerns, dependency injection, and modular organization from day one. Its
patterns align with SOLID principles (→ See [01-core-principles.md, Section 4]), particularly
Dependency Inversion and Single Responsibility.

**What to observe during trial:**
- Learning curve impact — decorators, modules, and dependency injection are new concepts if coming
  from Express. Is the team productive within a reasonable timeframe?
- Boilerplate overhead — NestJS requires more files and ceremony than Express for simple endpoints.
  Is the structure valuable or just overhead for the project's scale?
- Testing patterns — NestJS's DI makes unit testing services straightforward. Validate this in
  practice.
- Performance — NestJS adds a framework layer over Express/Fastify. Measure if the overhead is
  negligible for the project's needs.

**Success criteria for promotion to Adopt:**
- Successfully shipped at least one API with NestJS that the team can maintain and extend
- The architectural structure provided measurable benefits (easier onboarding, clearer code
  organization, better testability) compared to a similarly complex Express project
- The learning curve investment is justified by productivity gains

---

#### FastAPI — 🔬 Trial

**What it is:**
A modern, high-performance Python web framework for building APIs. Built on Starlette (async HTTP)
and Pydantic (data validation — Python's equivalent of Zod). Generates OpenAPI documentation
automatically from type hints.

**Why Trial:**
FastAPI is the natural choice for Python-centric backend services, particularly AI/ML endpoints.
When a project already uses Python for data processing or model inference, exposing those
capabilities via FastAPI avoids the overhead of a Node.js intermediary. Its validation model
(Pydantic) mirrors the Zod philosophy of schema-first development.

**What to observe during trial:**
- Integration with the TypeScript frontend — does the generated OpenAPI spec enable smooth
  client generation?
- Deployment model — FastAPI requires a Python runtime (uvicorn), separate from Node.js hosting.
  Is the operational overhead acceptable?
- When does it make sense to use FastAPI vs adding a Python script called from a Node.js service?

**Success criteria for promotion to Adopt:**
- A clear category of projects where FastAPI is the right choice over Node.js alternatives
- The team is comfortable operating a Python backend in production (deployment, monitoring, debugging)

---

#### Hono — 🔍 Assess

**What it is:** An ultra-lightweight, edge-first web framework that runs on Cloudflare Workers,
Deno, Bun, and Node.js. Minimal API surface with excellent performance.

**Why on the radar:** As edge computing matures, lightweight frameworks that run close to the user
become more relevant. Hono's multi-runtime support and tiny footprint make it interesting for
edge API endpoints and Cloudflare Workers projects.

**When to reassess:** When a project specifically targets edge deployment (Cloudflare Workers) or
when multi-runtime support becomes a requirement.

---

#### Koa — ⛔ Hold

**Why Hold:** Created by the original Express team, Koa introduced async/await middleware before
Express adopted it. However, Express has caught up (v5+), and Koa's ecosystem is significantly
smaller. There is no compelling advantage over Express for new projects.

**What to use instead:** Express.js for minimal APIs, NestJS for structured APIs.

---

#### Django — ⛔ Hold

**Why Hold:** Django is an excellent full-stack Python framework, but its monolithic approach
(ORM, admin, templates, auth — all bundled) does not align with the current architecture.
When Python is needed for backends, FastAPI provides a modern, lightweight, async-first approach
that integrates better with a TypeScript frontend.

**What to use instead:** FastAPI for Python APIs.

---

### 4.8 Database & Data

---

#### PostgreSQL — ✅ Adopt

**What it is:**
An advanced open-source relational database known for reliability, data integrity, extensibility,
and standards compliance. Supports JSON/JSONB, full-text search, geographic data (PostGIS), and
Row-Level Security (RLS) natively.

**Why Adopt:**
PostgreSQL is the primary database engine for all projects. It is chosen for its combination of
relational integrity, advanced features (JSONB eliminates most NoSQL use cases), RLS (security
at the data layer), and maturity (35+ years of active development). The decision to standardize
on a single database engine reduces cognitive overhead, simplifies operations, and allows the
team to build deep expertise rather than shallow familiarity across multiple engines.

**When to use:**
- All persistent data storage needs — it is the default
- Structured data with relationships — its core strength
- Semi-structured data (JSON documents) — JSONB with GIN indexes
- Full-text search — `tsvector` and `tsquery` before reaching for Elasticsearch
- Geospatial data — PostGIS extension

**When NOT to use:**
- Ephemeral caching (session data, rate limit counters) — consider Redis (🔍 Assess) when
  the performance profile demands it
- Embedded/local-first databases for offline applications — consider SQLite (🔍 Assess)
- Time-series data at extreme scale — specialized databases (TimescaleDB, which is a PostgreSQL
  extension, may help)

**Configuration baseline:**
- **MUST** use parameterized queries — never concatenate user input into SQL
  (→ See [07-security-standards.md, Section 10 — A03: Injection])
- **MUST** enable and configure RLS for multi-tenant applications
  (→ See [07-security-standards.md, Section 5])
- **SHOULD** use UUIDs as primary keys for public-facing IDs
- **SHOULD** use `timestamptz` (timestamp with time zone) for all temporal data
- **MUST** define indexes based on query patterns, not guesswork — measure first

**Key references:**
- → See [04-database-standards.md] — Full database conventions (naming, migrations, RLS, indexing)
- → See [07-security-standards.md, Section 8] — Encryption at rest

---

#### Supabase — ✅ Adopt

**What it is:**
An open-source Backend-as-a-Service (BaaS) built on top of PostgreSQL. Provides managed database,
authentication, real-time subscriptions, edge functions, file storage, and auto-generated REST/
GraphQL APIs — all backed by a real PostgreSQL database that you fully own and can query directly.

**Why Adopt:**
Supabase provides the infrastructure layer that would otherwise require significant DevOps effort:
managed PostgreSQL with backups, authentication with social providers and MFA, real-time
subscriptions via websockets, and file storage with access policies. Critically, unlike Firebase,
the underlying database is standard PostgreSQL — there is no vendor lock-in on data. You can always
migrate away by taking your PostgreSQL database with you.

**When to use:**
- New full-stack projects that need auth + database + storage (the default starting point)
- Projects where rapid development speed is prioritized (startup MVPs, freelance projects)
- Applications that need real-time features (live updates, presence, collaborative features)

**When NOT to use:**
- Projects that require databases other than PostgreSQL
- Microservice architectures where each service owns its database — Supabase is designed for
  application-level access
- When full infrastructure control is required (custom networking, VPC peering, specific compliance
  needs) — use self-hosted PostgreSQL

**Configuration baseline:**
- **MUST** configure RLS on every table — Supabase exposes the database to client-side queries,
  RLS is the security boundary (→ See [07-security-standards.md, Section 5])
- **MUST** use the service role key only on the server — never expose it to the client
- **SHOULD** use Supabase Auth for authentication unless there is a specific reason to use an
  alternative (→ Section 4.9 — Supabase Auth)
- **SHOULD** define database schemas and migrations in version-controlled SQL files, not only
  through the dashboard UI

**Key references:**
- → See [04-database-standards.md] — Database standards apply to Supabase's PostgreSQL
- → See [07-security-standards.md, Section 4 — 5] — Auth and authorization with Supabase

---

#### Prisma — ✅ Adopt

**What it is:**
A TypeScript-first ORM that provides a declarative schema language (`schema.prisma`), auto-generated
type-safe query client, and migration system. Prisma v7 (current) removed the Rust engine entirely,
rebuilding the client in 100% TypeScript — resulting in 90% smaller packages, 3-4x faster
performance, and native serverless/edge compatibility.

**Why Adopt:**
Prisma v7 addressed the major concerns that kept it in Trial: the Rust engine is gone (eliminating
binary compatibility issues), performance improved significantly, and the new Prisma Studio via CLI
provides a better database inspection experience. The type-safe query client remains the best DX
among Node.js ORMs — full autocomplete, compile-time error detection, and relation handling.
Configuration now uses `prisma.config.ts` for a TypeScript-native setup experience.

**When to use:**
- Full-stack Next.js applications with complex data models and relations
- Projects that benefit from auto-generated, type-safe database clients
- Teams that prefer a schema-first approach with managed migrations
- Applications connecting to Supabase PostgreSQL or self-managed PostgreSQL

**When NOT to use:**
- Simple CRUD where Supabase's client library is sufficient — Prisma adds overhead that is not
  justified for basic operations
- Projects requiring raw SQL control for most queries — consider Drizzle (🔬 Trial) instead
- Performance-critical hot paths where ORM overhead matters — profile first, drop to raw SQL
  via `prisma.$queryRaw` when needed

**Configuration baseline (v7):**
- **MUST** configure via `prisma.config.ts` (TypeScript config file) for datasource and migrations
- **MUST** use the `prisma-client` generator (not the legacy `prisma-client-js`)
- **SHOULD** use `npx prisma studio` for database inspection (rebuilt in v7)
- **SHOULD** enable query logging in development to review generated SQL
- **SHOULD** use `compilerBuild: "fast"` or `"small"` based on deployment needs (v7.3+)
- **MUST** keep schema and migrations in version control

**Key references:**
- → See [04-database-standards.md] — Database conventions that Prisma migrations must follow
- → See [01-core-principles.md, Section 6] — Layering rules (Prisma lives in the repository layer)

---

#### Drizzle ORM — 🔬 Trial

**What it is:**
A lightweight, type-safe SQL-first ORM for TypeScript (~7.4kb minified+gzipped). Unlike Prisma
(which abstracts SQL behind its own query language), Drizzle's API maps closely to SQL syntax —
if you know SQL, you know Drizzle. Zero dependencies, no binary, serverless-ready by design.
Currently in v1 beta with MSSQL support, relational queries v2, and a redesigned migration engine.

**Why Trial:**
Drizzle has rapidly grown from a niche alternative to one of the most adopted ORMs in the
TypeScript ecosystem. Major starters (T3 Stack, Epic Web) have switched from Prisma to Drizzle
as their default. Its SQL-first philosophy aligns with the principle that SQL literacy is
non-negotiable (→ Section 4.1 — SQL). The built-in Zod/Valibot integration (now part of the
`drizzle-orm` package) makes schema validation seamless.

**What to observe during trial:**
- Migration stability — the v1 beta redesigned the migration engine with commutativity checks.
  Validate that migrations are reliable across environments.
- DX comparison with Prisma — is the SQL-first approach more productive for the project's
  query complexity, or does Prisma's abstraction save time?
- Drizzle Studio — evaluate the built-in database GUI for development workflows
- Ecosystem maturity — v1 is still in beta. Monitor for breaking changes and stability.

**Success criteria for promotion to Adopt:**
- Drizzle v1.0 reaches stable release
- Successfully shipped at least one project with reliable migrations and queries
- Clear use cases where Drizzle is preferred over Prisma (serverless, SQL-heavy, performance)

---

#### Redis — 🔍 Assess

**What it is:** An in-memory key-value data store used for caching, session management, rate
limiting, pub/sub messaging, and job queues. Extremely fast due to in-memory operation.

**Why on the radar:** As applications grow, PostgreSQL alone may not meet performance requirements
for caching, session storage, or rate limiting. Redis is the standard solution for these patterns.
However, adding Redis introduces operational complexity (another service to manage, monitor, and
back up).

**When to reassess:** When a specific performance measurement shows that PostgreSQL-based caching
is insufficient, or when implementing rate limiting that requires sub-millisecond response times.
Follow the principle: → See [01-core-principles.md, Section 2 — Measure Before Optimizing].

---

#### MongoDB — ⛔ Hold

**Why Hold:** PostgreSQL with JSONB covers the vast majority of document storage use cases while
maintaining relational integrity, ACID transactions, and the ability to add structure incrementally.
MongoDB's schemaless nature, which is often presented as an advantage, frequently becomes a
maintenance liability as data evolves without enforced structure.

**What to use instead:** PostgreSQL with JSONB columns for flexible document storage.

---

#### MySQL — ⛔ Hold

**Why Hold:** PostgreSQL is the standardized relational database. MySQL is reliable but offers
fewer advanced features (no native JSONB with indexing, limited RLS, weaker extension ecosystem).
Standardizing on one relational database allows the team to build deep expertise.

**What to use instead:** PostgreSQL.

---

#### SQLite — 🔍 Assess

**What it is:** An embedded relational database that stores data in a single file. Zero
configuration, zero server, runs in the application process.

**Why on the radar:** The local-first and edge computing movements are reviving SQLite. Projects
like Turso (libSQL) and LiteFS enable SQLite replication across edge nodes. Interesting for
offline-capable applications, embedded systems, and edge deployments.

**When to reassess:** When a project requires offline-first capability or edge-deployed data persistence.

---

### 4.9 Authentication & Authorization

---

#### Supabase Auth — ✅ Adopt

**What it is:**
The authentication module built into Supabase. Provides email/password authentication, social
login (Google, GitHub, etc.), magic links, phone/OTP authentication, and multi-factor authentication
(MFA). Integrates directly with PostgreSQL RLS for row-level authorization.

**Why Adopt:**
For Supabase-backed projects, Supabase Auth is the natural choice because it is deeply integrated
with the database layer. User sessions are automatically available in RLS policies, meaning
authorization rules are enforced at the database level — the most secure boundary possible
(→ See [07-security-standards.md, Section 5]). This eliminates an entire class of authorization
bypass vulnerabilities.

**When to use:**
- All projects that use Supabase as the backend
- Applications that need RLS-based authorization (multi-tenant, user-owned data)
- Projects that need social login, MFA, or magic links with minimal custom code

**When NOT to use:**
- Projects not using Supabase — the auth module is tightly coupled to Supabase's infrastructure
- Applications that need highly custom authentication flows not supported by Supabase
  (e.g., enterprise SAML/OIDC federation at scale)
- Microservice architectures where a centralized identity provider is needed

**Configuration baseline:**
- **MUST** enable email confirmation for production applications
- **MUST** configure RLS policies that reference `auth.uid()` for user-scoped data
- **SHOULD** enable MFA for applications handling sensitive data
  (→ See [07-security-standards.md, Section 4])
- **SHOULD** configure rate limiting on auth endpoints to prevent brute force attacks
- **MUST NOT** expose the `service_role` key to the client — it bypasses all RLS policies

**Key references:**
- → See [07-security-standards.md, Section 4] — Authentication standards
- → See [07-security-standards.md, Section 5] — Authorization and RLS
- → See [04-database-standards.md] — RLS policy conventions

---

#### NextAuth.js (Auth.js) — 🔬 Trial

**What it is:**
An authentication library for Next.js (and other frameworks, as Auth.js v5) that supports OAuth
providers, credentials-based login, JWT and database sessions, and role-based access. Provider
ecosystem covers Google, GitHub, Discord, and dozens more.

**Why Trial:**
For projects that do not use Supabase — or where the frontend is deployed separately from the
database — Auth.js fills the authentication gap. Version 5 is framework-agnostic, supporting
Next.js, SvelteKit, and Express. It handles the OAuth complexity (token exchange, session
management, CSRF protection) that is error-prone to implement manually.

**What to observe during trial:**
- Session management model — JWT vs database sessions: which fits the project's security and
  performance requirements?
- Provider configuration complexity — is it straightforward for the providers you need?
- Integration with authorization patterns — how well does it work with your API authorization logic?
- Version stability — Auth.js v5 had breaking changes during beta. Verify stability.

**Success criteria for promotion to Adopt:**
- Reliable authentication in at least one non-Supabase project
- Session management is secure and performant
- No significant pain points with provider configuration or version upgrades

---

#### Passport.js — ⛔ Hold

**Why Hold:** Passport.js relies on a callback-based architecture that predates modern async/await
patterns. Its "strategy" system, while flexible, results in fragmented documentation and inconsistent
implementations across providers. Auth.js provides a more modern, cohesive approach.

**What to use instead:** Auth.js (NextAuth v5) for multi-provider authentication.

---

#### Clerk — 🔍 Assess

**What it is:** A managed authentication platform that provides pre-built UI components (sign-in,
sign-up, user profile), embeddable widgets, and a complete user management dashboard. Handles
authentication, session management, and user metadata.

**Why on the radar:** Clerk offers the fastest path from zero to working authentication — drop in a
component, and authentication works. The DX is excellent, and the pre-built components are polished.
The trade-off is pricing at scale and vendor lock-in (your users live in Clerk's infrastructure).

**When to reassess:** When a project needs authentication without a database backend (Supabase),
or when evaluating the build-vs-buy trade-off for auth specifically.

---

#### Lucia Auth — ⛔ Hold

**Why Hold:** The author officially deprecated Lucia in early 2025, recommending that developers
implement session management directly instead. Adopting a deprecated library creates immediate
technical debt.

**What to use instead:** Supabase Auth for Supabase projects, Auth.js for others.

**Lesson learned:** This is a real-world example of why the Maintenance & Governance criterion
(Section 1.2, #6) matters — a single-maintainer project carries inherent bus-factor risk.

---

#### Keycloak — 🔍 Assess

**What it is:** An open-source identity and access management (IAM) platform. Provides SSO,
identity federation (SAML, OIDC), user management, and fine-grained authorization. Self-hosted,
Java-based.

**Why on the radar:** Keycloak is the standard for self-hosted enterprise identity management. If a
project requires SAML federation, enterprise SSO, or compliance with specific identity standards,
Keycloak is the proven solution.

**When to reassess:** When a project requires enterprise identity features (SAML, OIDC federation,
centralized identity management) that Supabase Auth and Auth.js cannot provide.

---

### 4.10 API Tooling & Documentation

---

#### OpenAPI / Swagger — ✅ Adopt

**What it is:**
The OpenAPI Specification (formerly Swagger) is a standard format for describing REST APIs. It
defines endpoints, request/response schemas, authentication methods, and error responses in a
machine-readable YAML or JSON document. Tools built on this spec generate interactive documentation
(Swagger UI), client SDKs, and server stubs.

**Why Adopt:**
An API without documentation is an API no one can use correctly — including your future self.
OpenAPI provides a single source of truth for the API contract that is both human-readable and
machine-readable. It enables auto-generated interactive docs (try endpoints directly from the
browser), client code generation for consumers, and contract-first development where the spec
is written before the implementation.

**When to use:**
- All public or shared REST APIs — any API consumed by a frontend team, mobile app, or third party
- Internal APIs that are expected to grow or be maintained by multiple developers
- Contract-first development — define the spec, then implement

**When NOT to use:**
- Purely internal APIs within a full-stack Next.js app where frontend and backend share types via
  TypeScript — the shared types and Zod schemas serve as the contract
- Rapid prototyping where the API is expected to change significantly before stabilizing

**Configuration baseline:**
- **SHOULD** generate OpenAPI spec from code annotations or Zod schemas rather than maintaining
  it manually (reduces drift)
- **SHOULD** host interactive documentation (Swagger UI or Scalar) on a `/docs` endpoint in
  development and staging environments
- **MUST** protect or disable API documentation endpoints in production
  (→ See [07-security-standards.md, Section 10 — A05: Security Misconfiguration])
- **SHOULD** version the OpenAPI spec alongside the codebase

**Key references:**
- → See [03-api-design.md] — API design conventions that the OpenAPI spec documents
- → See [07-security-standards.md, Section 10] — Disable docs endpoints in production

---

#### Postman — ✅ Adopt

**What it is:**
An API development platform for building, testing, documenting, and sharing API requests. Provides
a GUI for constructing HTTP requests, organizing them into collections, managing environments
(dev, staging, production), and running automated test sequences.

**Why Adopt:**
Postman is the industry-standard tool for API exploration and manual testing. Collections serve as
executable API documentation — a new developer can import the collection and immediately understand
and test every endpoint. Environment management allows switching between dev/staging/production
without editing requests.

**When to use:**
- Exploring and manually testing APIs during development
- Sharing API collections with team members or clients
- Running pre-deployment smoke tests (collection runner)
- Documenting APIs for non-technical stakeholders

**When NOT to use:**
- Automated CI/CD testing — use Vitest + Supertest for programmatic API tests
- Performance testing — use k6 (🔍 Assess) or dedicated load testing tools

**Guidance:**
- **SHOULD** maintain a Postman collection per project, kept in sync with the API
- **SHOULD** use environment variables for URLs, tokens, and IDs — never hardcode them in requests
- **SHOULD** export collections and commit them to the repository for version control

---

#### Insomnia — 🔬 Trial

**What it is:** A REST and GraphQL API client focused on simplicity and speed. Lighter weight than
Postman with a cleaner interface for individual developers.

**Why Trial:** For solo development and small teams, Insomnia's streamlined interface may offer
better productivity than Postman's feature-rich (and sometimes heavy) platform. Worth comparing
side-by-side during daily API development.

**What to observe:** Does the simpler feature set cover your needs, or do you miss Postman's
collection runner, team workspaces, or automated testing?

---

#### Bruno — 🔍 Assess

**What it is:** An open-source API client that stores request collections as plain text files in
the project directory, version-controlled alongside the code. No cloud sync, no account required.

**Why on the radar:** Bruno's file-based approach aligns with the principle that project assets
should live in the repository. API collections become part of the codebase — reviewable in PRs,
versioned in Git, and available offline. This is a fundamentally different model from Postman's
cloud-first approach.

**When to reassess:** When evaluating alternatives to Postman's cloud dependency, or when a project
requires fully offline, version-controlled API collections.

---

#### tRPC — 🔍 Assess

**What it is:** A framework for building type-safe APIs where the client and server share TypeScript
types directly — no API specification, no code generation, no runtime schema validation at the
network boundary. The client calls server functions as if they were local.

**Why on the radar:** For projects where the same developer controls both frontend and backend
(TypeScript end-to-end), tRPC eliminates the API contract layer entirely. Type changes propagate
instantly from server to client. The developer experience is exceptional for this specific use case.

**Why not Trial:** tRPC creates tight coupling between client and server. If the API ever needs to
serve a mobile app, a third-party integration, or a non-TypeScript client, tRPC cannot accommodate
that without a rewrite. The flexibility trade-off is significant for the Exit Cost criterion
(Section 1.2, #10).

**When to reassess:** When a project is definitively TypeScript-only (single developer, no external
consumers) and the DX benefit justifies the coupling.

---

#### GraphQL — ⛔ Hold

**Why Hold:** GraphQL solves a real problem — over-fetching and under-fetching in complex data
graphs — but introduces significant complexity: custom query language, resolver architecture,
N+1 query management, caching challenges, and a larger attack surface (query complexity attacks).
For the current project scale and team size, well-designed REST APIs with resource-specific
endpoints and sparse fieldsets cover the same needs with far less complexity.

**What to use instead:** REST APIs with OpenAPI spec. If specific endpoints need flexible field
selection, implement a `fields` query parameter rather than adopting a full query language.

---

### 4.11 Testing

---

#### Vitest — ✅ Adopt

**What it is:**
A Vite-native testing framework with a Jest-compatible API. Provides unit and integration testing
with native ESM support, TypeScript support without configuration, and significant speed
improvements over Jest due to Vite's transformation pipeline and smart file watching.

**Why Adopt:**
Vitest is the modern replacement for Jest in the TypeScript ecosystem. It understands ESM natively
(no more `moduleNameMapper` hacks), integrates with Vite's configuration (shared aliases, plugins),
and runs tests faster due to smart re-runs and parallel execution. The API is Jest-compatible,
meaning migration from Jest is nearly mechanical — rename the config, change imports, and most
tests pass unchanged.

**When to use:**
- All unit tests — pure functions, service logic, utilities, schema validation
- Integration tests — service + repository interactions, API route handler testing
- Component tests — React component rendering and behavior (via Testing Library)

**When NOT to use:**
- End-to-end tests — use Playwright (different testing level, different tool)
- Load and performance testing — use k6 (🔍 Assess) or specialized tools

**Configuration baseline:**
- **MUST** configure in `vitest.config.ts` (or extend `vite.config.ts`)
- **MUST** follow the Arrange–Act–Assert pattern in all tests
  (→ See [01-core-principles.md, Section 11 — Definition of Done])
- **SHOULD** co-locate test files with source files: `service.ts` + `service.test.ts`
- **SHOULD** configure coverage thresholds appropriate to the project's maturity
- **SHOULD** use `vi.mock()` sparingly — prefer dependency injection over module mocking when
  possible

**Key references:**
- → See [06-testing-strategy.md] — Full testing strategy, test pyramid, and quality gates
- → See [01-core-principles.md, Section 11] — Definition of Done includes testing requirements

---

#### Playwright — ✅ Adopt

**What it is:**
A cross-browser end-to-end testing framework by Microsoft. Automates Chromium, Firefox, and WebKit
with a single API. Provides auto-waiting (no manual sleep/waitFor), codegen (record interactions
to generate test code), trace viewer (debug failures visually), and parallel test execution.

**Why Adopt:**
E2E tests verify that the entire application works from the user's perspective — the most valuable
(and most expensive) layer of the test pyramid. Playwright is the best-in-class tool for this: it
supports all major browsers, handles modern web patterns (SPAs, SSR, iframes, shadow DOM), and its
auto-waiting mechanism eliminates the flakiness that plagued earlier E2E tools.

**When to use:**
- Critical user flows — login, checkout, data submission, navigation paths that must not break
- Smoke tests for deployment verification — "does the app load and can a user complete the
  primary flow?"
- Cross-browser testing when browser compatibility is a requirement
- Visual regression testing (screenshot comparison)

**When NOT to use:**
- Unit testing business logic — use Vitest (testing individual functions does not need a browser)
- API-only testing — use Vitest + Supertest (faster, no browser overhead)
- Testing every edge case — E2E tests are slow and expensive. Reserve them for critical paths,
  use unit and integration tests for exhaustive coverage

**Configuration baseline:**
- **MUST** keep E2E tests in a dedicated `tests/e2e/` directory
- **SHOULD** use Page Object Model pattern for maintainable selectors and actions
- **SHOULD** use `data-testid` attributes for stable element selection — never rely on CSS classes
  or text content that may change
- **SHOULD** run E2E tests in CI against a staging or preview environment, not in unit test CI
- **SHOULD** use Playwright's codegen (`npx playwright codegen`) to bootstrap tests quickly, then
  refine manually

**Key references:**
- → See [06-testing-strategy.md] — Where E2E fits in the test pyramid, how many to write
- → See [09-devops-cicd.md] — CI pipeline configuration for E2E tests

---

#### Testing Library (@testing-library/react) — ✅ Adopt

**What it is:**
A family of testing utilities that encourage testing components the way users interact with them.
Instead of testing implementation details (internal state, component instances, class names), Testing
Library provides queries based on accessibility roles, labels, text content, and user-visible elements.

**Why Adopt:**
Testing Library enforces a testing philosophy aligned with the principle that software is built for
people (→ See [01-core-principles.md, Section 1.1]). Tests that query by role and label are resilient
to refactoring (changing the component internals does not break the test) and simultaneously
validate accessibility (if the test cannot find the element by role, the screen reader cannot either).

**When to use:**
- All React component tests — rendering, interaction, accessibility validation
- Form testing — fill inputs by label, submit by button role
- Integration tests that verify component composition and data flow

**When NOT to use:**
- Non-React testing (API routes, services, utilities) — use Vitest directly
- E2E tests — use Playwright (Testing Library tests components in isolation, not full pages)

**Guidance:**
- **MUST** prefer queries in this priority order: `getByRole` → `getByLabelText` → `getByText` →
  `getByTestId`. `getByTestId` is the last resort, not the default.
- **MUST NOT** use `container.querySelector` or other DOM traversal — it tests implementation details
- **SHOULD** use `userEvent` (from `@testing-library/user-event`) over `fireEvent` — it simulates
  real user interactions more accurately

---

#### Supertest — ✅ Adopt

**What it is:**
An HTTP assertion library for testing Node.js HTTP servers. Provides a fluent API for making
requests to an Express/NestJS/Hono app and asserting on status codes, headers, and response bodies
— without starting a real server or network listener.

**Why Adopt:**
Supertest fills the gap between unit tests (test a function) and E2E tests (test the full app in
a browser). It enables integration testing of API routes with real HTTP semantics (middleware,
error handling, content negotiation) but without the overhead of a running server or browser.

**When to use:**
- API route integration tests — verify that the full request/response cycle works correctly
- Testing middleware behavior (auth, validation, rate limiting)
- Testing error handling and edge cases at the HTTP level

**When NOT to use:**
- Testing business logic in isolation — use Vitest to test service functions directly
- Frontend testing — use Testing Library for component tests

---

#### Jest — ⛔ Hold

**Why Hold:** Vitest provides the same API with better ESM support, faster execution, and native
TypeScript handling. Jest's CJS-first architecture requires increasingly complex configuration to
work with modern TypeScript/ESM projects.

**What to use instead:** Vitest. Migration is near-mechanical — the API is intentionally compatible.

---

#### Cypress — ⛔ Hold

**Why Hold:** Playwright offers faster execution, native multi-browser support (Chromium, Firefox,
WebKit in one test run), better auto-waiting, and a more powerful debugging experience (trace viewer).
Cypress is limited to Chromium-based browsers for most features and has a slower test execution model.

**What to use instead:** Playwright for all E2E testing.

---

#### Storybook — 🔬 Trial

**What it is:** A development environment for building, documenting, and testing UI components in
isolation. Each component gets a "story" that renders it in different states (default, loading,
error, disabled, etc.) outside the application context.

**Why Trial:** Storybook is valuable for component libraries and design systems where visual
consistency matters. It enables visual testing (screenshot comparison), interactive documentation,
and component development without needing to navigate to the specific page that uses the component.
The trade-off is build overhead and maintenance of story files.

**What to observe during trial:**
- Is the overhead of maintaining `.stories.tsx` files justified by the benefits?
- Does it improve component quality and consistency compared to developing components in-place?
- Is it useful for collaboration with designers or non-technical stakeholders?

**Success criteria:** Storybook demonstrably improves component quality or design communication
for the project. If stories become stale and unmaintained, move to Hold.

---

#### k6 — 🔍 Assess

**What it is:** A developer-centric load testing tool where test scripts are written in JavaScript.
Simulates concurrent users hitting API endpoints to measure response times, throughput, and
failure rates under load.

**Why on the radar:** Performance testing is often neglected until production issues emerge. k6
provides an accessible entry point for developers already comfortable with JavaScript — write a
test script, run it, get results. No complex infrastructure required.

**When to reassess:** When an application handles real user traffic and performance SLAs need to
be validated, or before a major launch where traffic patterns are uncertain.

---

#### Faker.js (@faker-js/faker) — ✅ Adopt

**What it is:**
A library for generating realistic fake data: names, emails, addresses, phone numbers, dates,
UUIDs, product descriptions, and hundreds of other data types. Supports localization (including
Portuguese) for region-appropriate fake data.

**Why Adopt:**
Realistic test data is essential for meaningful tests, seed scripts, and development environments.
Hardcoding test data (`"John Doe"`, `"test@test.com"`) creates fragile tests that may pass for
the wrong reasons. Faker generates diverse, realistic data that exposes edge cases (long names,
special characters, unicode) that handcrafted test data misses.

**When to use:**
- Test factories — generate realistic entities for unit and integration tests
- Database seed scripts — populate development and staging environments with meaningful data
- Storybook stories — render components with varied, realistic content
- Load testing data — generate large volumes of varied test input

**When NOT to use:**
- Production code — Faker is a dev dependency only, it must never reach production bundles
- Security testing — Faker data is random but not adversarial. For security testing, use
  purpose-built payloads (→ See [07-security-standards.md, Section 13])

**Guidance:**
- **MUST** install as a dev dependency only (`devDependencies`)
- **SHOULD** create factory functions that wrap Faker for domain entities
  (e.g., `createFakeUser()`, `createFakeOrder()`)
- **SHOULD** use `faker.seed()` for reproducible test data when tests need deterministic output

---

### 4.12 Code Quality & Formatting

---

#### ESLint — ✅ Adopt

**What it is:**
A pluggable static analysis tool for JavaScript and TypeScript that identifies and auto-fixes
code quality issues, potential bugs, and style violations. Supports hundreds of rules through
plugins for React, Next.js, accessibility, security, and import ordering. ESLint v10 (current
stable, Feb 2026) uses flat config exclusively.

**Why Adopt:**
ESLint is the first line of defense against code quality issues. It catches bugs before they
reach code review (unused variables, unreachable code, type coercion pitfalls), enforces
consistency (import ordering, naming patterns), and can enforce security rules (no `eval`,
no `dangerouslySetInnerHTML` without justification). Combined with CI enforcement, it creates
an automated quality gate that scales without human review overhead.

**When to use:**
- Every TypeScript and JavaScript project — no exceptions

**Configuration baseline (v10 — flat config):**
- **MUST** use flat config format (`eslint.config.js` or `eslint.config.ts`) — the legacy
  `.eslintrc.*` format has been completely removed in ESLint v10
- **MUST** use `defineConfig()` from `eslint/config` for cleaner configuration and automatic
  flattening of nested configs
- **MUST** extend recommended configs using `extends` in `defineConfig()`: `@eslint/js`,
  `typescript-eslint`, `eslint-plugin-react`, `eslint-plugin-next`
- **SHOULD** add security-focused plugins: `eslint-plugin-security`
- **SHOULD** add accessibility plugin: `eslint-plugin-jsx-a11y`
- **MUST** run ESLint in CI — fail the build on errors
- **MUST NOT** accumulate `eslint-disable` comments — each one should be justified with a comment
  explaining why

**Migration note (eslintrc → flat config):**
- `.eslintrc.json` / `.eslintrc.js` → `eslint.config.js` (or `.ts`, `.mjs`, `.mts`)
- `extends: [...]` → `extends: [...]` inside `defineConfig()` (similar concept, different syntax)
- `.eslintignore` → `globalIgnores()` helper or `ignores` property in config objects
- Run `npx @eslint/migrate-config .eslintrc.json` for automated migration assistance

**Key references:**
- → See [07-security-standards.md, Section 13] — ESLint security plugins as part of SAST
- → See [09-devops-cicd.md] — CI pipeline configuration

---

#### Prettier — ✅ Adopt

**What it is:**
An opinionated code formatter that enforces a consistent style by parsing code and reprinting it
according to its own rules. Unlike ESLint (which flags issues), Prettier automatically rewrites
the code — eliminating all formatting debates.

**Why Adopt:**
Formatting discussions are a waste of engineering time. Prettier resolves them permanently — the
formatter decides, the team accepts, and code reviews focus on logic instead of semicolons and
indentation. Combined with format-on-save in the editor and pre-commit hooks, formatting becomes
invisible.

**When to use:**
- Every TypeScript, JavaScript, JSON, CSS, Markdown, and HTML file

**Configuration baseline:**
- **MUST** configure `.prettierrc` at the project root with consistent settings across all projects
- **MUST** integrate with ESLint via `eslint-config-prettier` (disables ESLint formatting rules
  that conflict with Prettier)
- **SHOULD** enable format-on-save in the editor (VS Code: `editor.formatOnSave: true`)
- **SHOULD** add to pre-commit hook via Husky + lint-staged

---

#### Husky — ✅ Adopt

**What it is:**
A tool that manages Git hooks (pre-commit, commit-msg, pre-push) by installing hook scripts that
run automatically during Git operations. Ensures quality gates execute locally before code is pushed.

**Why Adopt:**
CI catches issues, but after the developer has already pushed and waited for the pipeline. Git
hooks catch issues instantly — before the commit is even created. This tightens the feedback loop
(→ See [01-core-principles.md, Section 1.6 — Feedback Loops Matter]) and prevents broken commits from
entering the repository.

**When to use:**
- Every project — it is part of the standard tooling baseline

**Configuration baseline:**
- **MUST** configure a `pre-commit` hook that runs lint-staged
- **SHOULD** configure a `commit-msg` hook that runs commitlint
- **SHOULD** document setup in the README (contributors need to run `npx husky install` after cloning)

---

#### lint-staged — ✅ Adopt

**Why Adopt:** Without lint-staged, pre-commit hooks would lint and format the entire codebase on
every commit — unacceptably slow for large projects. lint-staged runs tools only on staged files,
keeping the feedback loop fast regardless of project size.

**Guidance:** Configure in `package.json` or `.lintstagedrc` to run ESLint + Prettier on staged
`.ts`, `.tsx`, `.js`, `.jsx`, `.css`, and `.json` files.

---

#### commitlint — ✅ Adopt

**Why Adopt:** Enforces Conventional Commits format (`feat:`, `fix:`, `chore:`, etc.) automatically.
This enables automated changelog generation, semantic versioning, and meaningful Git history.
Without enforcement, commit message conventions decay within weeks.

**Guidance:**
- **MUST** use `@commitlint/config-conventional` as the base configuration
- **MUST** run via Husky `commit-msg` hook

---

#### Biome — 🔬 Trial

**What it is:**
A Rust-based toolchain that combines linting (462 rules), formatting, and import sorting in a
single binary. Biome v2 (current, since mid-2025) introduced linter domains for React and Next.js,
type-aware linting, and plugin support via GritQL. 10-100x faster than ESLint + Prettier.

**Why Trial:**
Biome v2 closed the critical gaps that previously kept it in Assess. It now has dedicated React
and Next.js linter domains with recommended rule sets, type-aware linting capabilities (~85%
coverage of typescript-eslint rules), and a growing plugin system. The single `biome check --write`
command replacing both `eslint --fix` and `prettier --write` is a genuine DX improvement. For new
projects, especially Vite + React SPAs, Biome is a viable replacement for the ESLint + Prettier
combination.

**What to observe during trial:**
- Rule coverage vs ESLint — does Biome catch the same issues in practice? Run both tools on the
  same codebase and compare findings.
- Ecosystem compatibility — do shadcn/ui, Next.js, and other tools in the stack work seamlessly
  with Biome's formatting output?
- Team adoption — is the team comfortable with Biome's rule naming and configuration format
  compared to ESLint's familiar ecosystem?
- CI integration — verify `biome ci` works reliably in GitHub Actions pipelines

**Success criteria for promotion to Adopt:**
- Successfully replaces ESLint + Prettier in at least one project without missing critical issues
- No significant gaps in React/Next.js/accessibility rule coverage for the project's needs
- Team prefers the DX over the ESLint + Prettier combination

---

#### SonarQube — 🔬 Trial

**What it is:** A static analysis platform that provides deep code quality inspection — code smells,
security vulnerabilities, duplicated code, cognitive complexity analysis — with a web dashboard for
tracking quality trends over time.

**Why Trial:** ESLint catches surface-level issues. SonarQube goes deeper — detecting complex
security vulnerabilities, measuring cognitive complexity, tracking quality trends across releases,
and enforcing quality gates. It is a SAST tool (→ See [07-security-standards.md, Section 13]) that
complements ESLint rather than replacing it.

**What to observe during trial:**
- Signal-to-noise ratio — does it surface actionable findings, or mostly false positives?
- Integration overhead — is the dashboard and CI integration worth maintaining?
- Overlap with ESLint — how much of SonarQube's value is already covered by ESLint plugins?

**Success criteria:** SonarQube consistently surfaces issues that ESLint misses, and the dashboard
provides value for tracking quality trends.

---

#### EditorConfig — ✅ Adopt

**Why Adopt:** A simple `.editorconfig` file at the project root ensures that every editor and IDE
applies the same basic formatting rules (indentation, line endings, trailing whitespace, final
newline) regardless of the developer's personal settings. It is a 5-line file that prevents an
entire class of diff noise.

**Guidance:** Add to every project root. Supported natively by most editors and IDEs.

---

### 4.13 DevOps & Containerization

---

#### Docker — ✅ Adopt

**What it is:**
A platform for building, shipping, and running applications inside containers — lightweight,
isolated environments that package the application code, runtime, libraries, and configuration
into a single portable unit. A container runs identically on a developer's laptop, in CI, and
in production.

**Why Adopt:**
Docker solves the "works on my machine" problem permanently. By defining the environment in a
`Dockerfile`, every team member, CI pipeline, and production server runs the exact same setup.
This eliminates environment drift (different Node.js versions, missing system dependencies,
OS-specific behavior) and makes deployments reproducible and predictable.

**When to use:**
- Production deployments — containerize every application that runs on a server
- Development environments — run databases, caches, and services locally without installing them
  on the host machine
- CI/CD pipelines — run tests and builds in containers for reproducibility
- Multi-service development — run the full stack locally (app + database + queue) with Docker Compose

**When NOT to use:**
- Static sites deployed to CDNs (Vercel, Cloudflare Pages) — no container needed
- Serverless functions — the platform manages the runtime
- Development of the application code itself — develop natively, containerize for deployment.
  Running your editor and dev server inside a container adds friction without proportional benefit.

**Configuration baseline:**
- **MUST** use multi-stage builds to minimize production image size — build stage (install deps,
  compile) → production stage (copy only artifacts, no dev deps)
- **MUST** use a non-root user in production containers
  (→ See [07-security-standards.md, Section 12])
- **MUST** use specific image tags (`node:20-alpine`), never `latest` — reproducibility requires
  pinned versions
- **MUST** add a `.dockerignore` file — exclude `node_modules`, `.git`, `.env`, test files
- **SHOULD** use Alpine-based images for smaller footprint and reduced attack surface
- **SHOULD** scan images for vulnerabilities with Trivy (🔬 Trial) before deploying

**Key references:**
- → See [07-security-standards.md, Section 12] — Container and infrastructure security
- → See [09-devops-cicd.md] — Docker in CI/CD pipelines, build optimization

---

#### Docker Compose — ✅ Adopt

**What it is:**
A tool for defining and running multi-container applications using a declarative YAML file
(`docker-compose.yml`). Defines services, networks, and volumes in a single file, then starts
the entire stack with one command.

**Why Adopt:**
Local development often requires more than the application itself — a PostgreSQL database, Redis
for caching, a mail server for testing. Docker Compose lets you define this entire environment
declaratively and spin it up with `docker compose up`. New team members get a working environment
in minutes, not hours.

**When to use:**
- Local development environments — database, cache, queue, mock services
- Integration testing — spin up dependencies, run tests, tear down
- Demo environments — reproducible full-stack setup for demonstrations

**When NOT to use:**
- Production orchestration — Docker Compose is a development tool. For production, use a platform
  (Vercel, Railway, Fly.io) or orchestrator (Kubernetes, if at that scale).

**Guidance:**
- **SHOULD** include a `docker-compose.yml` in every project that has external dependencies
- **SHOULD** configure volume mounts for database persistence across restarts
- **SHOULD** use `.env` files for Compose variables (ports, credentials) — never hardcode

---

#### GitHub Actions — ✅ Adopt

**What it is:**
A CI/CD platform integrated directly into GitHub repositories. Defines automated workflows
(build, test, lint, deploy) as YAML files in `.github/workflows/`. Triggered by events (push,
pull request, schedule, manual dispatch).

**Why Adopt:**
GitHub Actions is the natural CI/CD choice for projects hosted on GitHub — zero additional
infrastructure, integrated with PRs (status checks, annotations), and a generous free tier for
public and private repositories. The marketplace provides pre-built actions for common tasks
(deploy to Vercel, run Playwright, scan with Trivy), reducing pipeline setup time.

**When to use:**
- All projects hosted on GitHub — CI/CD should be automated from day one
- Automated quality gates: lint, typecheck, test, security scan on every PR
- Automated deployments to Vercel, Railway, Cloudflare, or custom infrastructure
- Scheduled tasks: dependency scanning, DAST scans, stale issue cleanup

**When NOT to use:**
- Projects not hosted on GitHub — use the platform's native CI (GitLab CI, Bitbucket Pipelines)
- Extremely complex build pipelines that exceed GitHub Actions' capabilities — rare for current
  project scale

**Configuration baseline:**
- **MUST** run on every pull request: lint, typecheck, unit tests, security audit
- **SHOULD** run E2E tests on staging deployments (not on every PR — too slow)
- **SHOULD** use job matrices for multi-version testing when applicable
- **MUST** pin action versions to specific SHAs or tags, not `@latest`
  (→ See [07-security-standards.md, Section 11] — supply chain security applies to CI too)
- **SHOULD** cache `node_modules` and other heavy dependencies between runs for faster pipelines

**Key references:**
- → See [09-devops-cicd.md] — Full CI/CD pipeline design and configuration
- → See [07-security-standards.md, Section 13] — Security testing in CI

---

#### Terraform — 🔍 Assess

**What it is:** An Infrastructure as Code (IaC) tool that defines cloud resources in declarative
configuration files. Supports all major cloud providers.

**Why on the radar:** As projects move beyond PaaS to custom cloud infrastructure, managing
resources manually becomes error-prone. Terraform codifies infrastructure, making it reproducible
and reviewable.

**When to reassess:** When a project requires custom cloud infrastructure beyond what PaaS
platforms provide.

---

#### Pulumi — 🔍 Assess

**What it is:** An IaC tool using real programming languages (TypeScript, Python, Go) instead of
a custom DSL (HCL).

**Why on the radar:** For a TypeScript-focused team, writing infrastructure in TypeScript has a
lower barrier to entry than learning HCL.

**When to reassess:** Alongside Terraform — when custom IaC is needed.

---

#### Kubernetes (K8s) — ⛔ Hold

**Why Hold:** Kubernetes introduces massive operational complexity that is justified only when
managing dozens of services across multiple nodes. For the current project scale, a PaaS platform
provides the deployment and scaling capabilities needed without the operational burden.

**What to use instead:** Vercel for Next.js, Railway or Render for containerized backends.

---

#### Jenkins — ⛔ Hold

**Why Hold:** Jenkins is a self-hosted CI/CD server that requires installation, maintenance,
plugin management, and security patching. GitHub Actions provides equivalent functionality with
zero infrastructure management.

**What to use instead:** GitHub Actions.

---

#### Nginx — 🔬 Trial

**What it is:** A high-performance HTTP server, reverse proxy, and load balancer.

**Why Trial:** For self-hosted deployments (VPS), Nginx is essential as the entry point that routes
traffic to application containers, handles SSL certificates, and serves static assets. Not needed
when deploying to PaaS platforms which handle this layer automatically.

**What to observe:** Does the project actually need self-hosted deployment? Configuration complexity
and team comfort level.

**Success criteria:** A clear, recurring need for self-hosted deployments requiring a reverse proxy.

---

### 4.14 Hosting & Deployment

---

#### Vercel — ✅ Adopt

**What it is:**
A cloud platform optimized for frontend frameworks (especially Next.js). Provides zero-configuration
deployments, automatic preview URLs for pull requests, edge functions, serverless API routes, image
optimization, and analytics.

**Why Adopt:**
For Next.js applications, Vercel is the path of least resistance to production. Push to GitHub,
the app is deployed. The platform handles SSL, CDN, serverless scaling, and image optimization
without configuration.

**When to use:**
- All Next.js applications (the default deployment target)
- Static sites and SPAs (Vite + React)
- Projects where preview deployments per PR are valuable

**When NOT to use:**
- Backend-only services — use Railway, Render, or Fly.io
- Projects that exceed Vercel's tier limits (execution time, bandwidth)
- Applications that need persistent server processes (WebSocket servers, long-running tasks)

**Configuration baseline:**
- **MUST** connect the GitHub repository for automatic deployments
- **MUST** configure environment variables in the Vercel dashboard
- **SHOULD** configure preview deployments for PRs
- **SHOULD** set appropriate environment variable scopes (Production, Preview, Development)

---

#### Supabase Cloud — ✅ Adopt

**Why Adopt:** The managed hosting for Supabase projects. Provides PostgreSQL with automatic
backups, connection pooling, Auth, Realtime, Storage, and Edge Functions. See Section 4.8
(Supabase) for the full profile.

---

#### Cloudflare Pages — 🔬 Trial

**What it is:** A static site and JAMstack hosting platform deployed to Cloudflare's global edge
network.

**Why Trial:** For Astro sites and static deployments, Cloudflare Pages offers the fastest global
delivery, the most generous free tier (unlimited bandwidth), and Cloudflare's security features.

**What to observe:** Deployment experience, build configuration, and edge function capabilities
compared to Vercel.

---

#### Railway — 🔬 Trial

**What it is:** A PaaS for deploying applications and databases. Supports Docker containers,
Node.js, Python, and provides managed PostgreSQL and Redis.

**Why Trial:** For standalone backends that do not fit in Vercel's serverless model. Simple
container hosting with managed databases.

**What to observe:** Pricing at scale, cold start behavior, database performance.

---

#### Render — 🔬 Trial

**What it is:** A cloud platform offering web services, static sites, background workers, cron
jobs, managed PostgreSQL, and Redis.

**Why Trial:** Similar to Railway with a slightly different pricing model. Worth evaluating
alongside Railway.

**What to observe:** Cold start times on free tier, deployment speed, auto-scaling behavior.

---

#### Fly.io — 🔍 Assess

**What it is:** A platform for deploying applications as micro-VMs on a global edge network.

**Why on the radar:** Edge deployment model is interesting for latency-sensitive applications.

**When to reassess:** When a project has a global user base where single-region latency is
measurable and impactful.

---

#### AWS (general) — 🔍 Assess

**What it is:** Amazon Web Services — the largest cloud infrastructure provider.

**Why on the radar:** Industry standard for cloud infrastructure. Learning AWS is a career
investment. Evaluate individual services as needed (S3, SES, CloudFront).

**When to reassess:** When a specific AWS service solves a problem no PaaS platform addresses.

---

#### DigitalOcean — 🔍 Assess

**What it is:** A developer-friendly cloud provider with simpler infrastructure than AWS.

**Why on the radar:** Best learning platform for cloud infrastructure. Droplets (VPS) are ideal
for understanding what PaaS abstracts away.

**When to reassess:** When a project needs a VPS or simple cloud infrastructure.

---

#### Heroku — ⛔ Hold

**Why Hold:** Pricing became non-competitive after removing the free tier in 2022. Railway, Render,
and Fly.io offer better value.

**What to use instead:** Railway or Render.

---

#### Netlify — ⛔ Hold

**Why Hold:** Vercel provides superior Next.js integration. Cloudflare Pages offers better edge
performance for static sites.

**What to use instead:** Vercel for Next.js, Cloudflare Pages for static sites.

---

### 4.15 Observability & Monitoring

---

#### Sentry — ✅ Adopt

**What it is:**
An error tracking and performance monitoring platform. Captures runtime errors, unhandled exceptions,
and performance metrics from both frontend and backend applications.

**Why Adopt:**
Without error tracking, production bugs are invisible until a user reports them. Sentry makes
errors visible immediately with stack traces, breadcrumbs, and release tracking. Its Next.js
integration captures both server-side and client-side errors with a single setup.

**When to use:**
- Every production application — error tracking is not optional
- Performance-sensitive applications — track web vitals and API response times
- Release tracking — correlate errors with specific deployments

**When NOT to use:**
- Development environments — noisy and unnecessary
- Logging — Sentry captures errors, not application logs. Use Pino for logging.

**Configuration baseline:**
- **MUST** install the framework-specific SDK (`@sentry/nextjs`, `@sentry/node`)
- **MUST** configure source maps upload for readable stack traces
- **MUST** set appropriate sample rates — 100% for errors, 10–20% for performance transactions
- **MUST NOT** send PII to Sentry — configure data scrubbing rules
  (→ See [07-security-standards.md, Section 14])
- **SHOULD** configure release and environment tags

**Key references:**
- → See [08-observability.md] — Full observability strategy
- → See [07-security-standards.md, Section 14] — Data protection with third-party services

---

#### UptimeRobot — ✅ Adopt

**What it is:**
A simple uptime monitoring service that pings endpoints and alerts when they go down.

**Why Adopt:**
Uptime monitoring is the most basic observability need. UptimeRobot provides this with zero
complexity. The free tier covers up to 50 monitors with 5-minute intervals.

**When to use:**
- Every production application — monitor main URL and key API endpoints
- Public status pages
- SSL certificate expiry monitoring

---

#### Pino — ✅ Adopt

**What it is:**
A high-performance, structured JSON logging library for Node.js.

**Why Adopt:**
Structured logging is the foundation of production observability. Pino produces JSON logs with
consistent fields that log aggregation tools can index and query. It is 5x faster than Winston.

**When to use:**
- All Node.js backend applications

**Configuration baseline:**
- **MUST** configure log levels appropriately (error, warn, info, debug)
- **MUST** include request context in logs (request ID, user ID, endpoint)
- **MUST NOT** log sensitive data (→ See [07-security-standards.md, Section 15])
- **SHOULD** use `pino-pretty` for development only
- **SHOULD** configure a transport to a log aggregation system in production

**Key references:**
- → See [08-observability.md] — Logging standards
- → See [07-security-standards.md, Section 15] — Security logging

---

#### LogRocket — 🔬 Trial

**What it is:** A session replay and frontend observability platform.

**Why Trial:** Session replay is invaluable for debugging frontend issues that are difficult to
reproduce. Worth evaluating for projects where UX quality is critical.

**What to observe:** Privacy implications (RGPD consent required), performance impact, and
signal-to-noise ratio.

---

#### Axiom — 🔬 Trial

**What it is:** A modern log management and analytics platform.

**Why Trial:** Centralized log management without the operational burden of self-hosting ELK.
Generous free tier (500GB ingest/month).

**What to observe:** Query capabilities, Pino integration, alerting usefulness, cost projection.

---

#### Grafana — 🔍 Assess

**What it is:** An open-source observability platform for visualizing metrics through dashboards.

**Why on the radar:** Industry standard for infrastructure dashboards. Relevant when projects need
custom metrics visualization beyond Sentry and UptimeRobot.

**When to reassess:** When custom metrics dashboards are needed.

---

#### Prometheus — 🔍 Assess

**What it is:** An open-source metrics collection and alerting system.

**Why on the radar:** Pairs with Grafana for a complete self-hosted monitoring stack.

**When to reassess:** Alongside Grafana.

---

#### New Relic — 🔍 Assess

**What it is:** A full-stack APM platform.

**Why on the radar:** Most comprehensive observability in a single platform. Trade-off is cost.

**When to reassess:** When observability needs exceed Sentry + Axiom + UptimeRobot.

---

#### Winston — ⛔ Hold

**Why Hold:** Pino provides the same capabilities with 5x better performance.

**What to use instead:** Pino.

---

### 4.16 Security Tooling

---

#### npm audit — ✅ Adopt

**Why Adopt:** Built into npm, zero setup. Scans for known vulnerabilities. Minimum viable
dependency security check.

**Guidance:**
- **MUST** run in CI — consider failing on high/critical findings
- **SHOULD** combine with Dependabot for automated fix PRs

---

#### gitleaks — ✅ Adopt

**What it is:**
A tool that scans Git repositories for hardcoded secrets.

**Why Adopt:**
A single committed secret can compromise an entire system. gitleaks prevents this by scanning
for secret patterns before they enter the repository.

**Configuration baseline:**
- **MUST** install as a pre-commit hook via Husky
- **SHOULD** run in CI as additional safety net
- **SHOULD** scan existing repository history when first adopting

**Key references:**
- → See [07-security-standards.md, Section 7] — Secrets management
- → See [07-security-standards.md, Section 13] — Pre-commit security scanning

---

#### Dependabot — ✅ Adopt

**Why Adopt:** GitHub-native automated dependency updates. Zero configuration beyond a YAML file.

**Guidance:**
- **MUST** enable for all GitHub repositories
- **SHOULD** configure update schedule (weekly for patch/minor, immediate for security)
- **SHOULD** group minor/patch updates to reduce PR noise

---

#### Snyk — 🔬 Trial

**What it is:** A developer security platform scanning code, dependencies, containers, and IaC.

**Why Trial:** Deeper analysis than npm audit with fix suggestions and multi-ecosystem support.

**What to observe:** Signal quality, fix suggestion quality, IDE integration value.

---

#### Trivy — 🔬 Trial

**What it is:** An open-source scanner covering containers, dependencies, IaC, and secrets.

**Why Trial:** Most comprehensive single scanning tool — covers multiple security dimensions.

**What to observe:** GitHub Actions integration, scan speed, false positive rate.

**Key references:**
- → See [07-security-standards.md, Section 12] — Container security
- → See [07-security-standards.md, Section 13] — Combined security pipeline

---

#### OWASP ZAP — 🔬 Trial

**What it is:** An open-source DAST tool that tests running applications for vulnerabilities.

**Why Trial:** Complements SAST by finding runtime vulnerabilities (misconfigured headers, exposed
endpoints, CORS issues).

**What to observe:** CI integration ease, false positive rate, passive vs active scan balance.

**Key references:**
- → See [07-security-standards.md, Section 13] — DAST integration

---

#### Renovate — 🔬 Trial

**What it is:** Automated dependency updates with advanced configuration (grouping, automerge,
monorepo support).

**Why Trial:** More configurable than Dependabot. Worth evaluating if Dependabot feels limiting.

**What to observe:** Configuration complexity vs Dependabot.

---

#### Socket.dev — 🔍 Assess

**What it is:** Supply chain security platform analyzing npm packages for malicious behavior.

**Why on the radar:** Detects zero-day supply chain attacks by analyzing package behavior, not
just known CVEs.

**When to reassess:** When supply chain security becomes a priority.

---

#### HashiCorp Vault — 🔍 Assess

**What it is:** Enterprise secrets management platform.

**Why on the radar:** Relevant when managing many secrets across multiple services with rotation
and audit requirements.

**When to reassess:** When secret management complexity exceeds environment variables.

---

### 4.17 Messaging, Queues & Real-time

---

#### Supabase Realtime — ✅ Adopt

**What it is:**
The real-time engine built into Supabase. Provides database change subscriptions, broadcast
messaging, and presence tracking.

**Why Adopt:**
For Supabase-backed projects, Realtime is included at zero additional cost. It leverages
PostgreSQL's replication log to stream database changes to connected clients.

**When to use:**
- Live updates, collaborative features, presence indicators, real-time dashboards

**When NOT to use:**
- High-throughput event streaming (thousands of events/second)
- Projects not using Supabase
- Complex pub/sub patterns with routing and delivery guarantees

---

#### WebSocket (native) — 🔬 Trial

**What it is:** A protocol providing full-duplex, persistent connections between client and server.

**Why Trial:** When Supabase Realtime is insufficient. Understanding the underlying technology is
essential even when using abstractions.

**What to observe:** Connection management complexity (reconnection, heartbeats, scaling).

---

#### Pusher — 🔍 Assess

**What it is:** A managed real-time messaging service.

**Why on the radar:** For non-Supabase projects needing real-time without WebSocket infrastructure.

**When to reassess:** When a non-Supabase project needs real-time features.

---

#### Upstash — 🔍 Assess

**What it is:** Serverless Redis, Kafka, and message queue with pay-per-request pricing.

**Why on the radar:** Solves Redis and queues in serverless environments.

**When to reassess:** When needing caching or job queues in serverless environments.

---

#### RabbitMQ — 🔍 Assess

**What it is:** An open-source message broker implementing AMQP.

**Why on the radar:** Standard for reliable asynchronous task processing.

**When to reassess:** When a project needs async processing beyond simpler approaches.

---

#### BullMQ — 🔍 Assess

**What it is:** A Node.js job queue library backed by Redis.

**Why on the radar:** Simplest path to background job processing in Node.js.

**When to reassess:** When needing background jobs and Redis is available.

---

#### Apache Kafka — ⛔ Hold

**Why Hold:** Designed for high-throughput distributed event streaming at massive scale. Operational
complexity is orders of magnitude beyond current needs.

**What to use instead:** Supabase Realtime, BullMQ, or RabbitMQ.

---

### 4.18 Payments

---

#### Stripe — ✅ Adopt

**What it is:**
A payment processing platform providing one-time payments, subscriptions, invoicing, customer
management, and fraud prevention. Supports MB WAY and Multibanco (Portugal) natively.

**Why Adopt:**
Best developer experience of any payment platform — comprehensive documentation, well-designed API,
test mode, webhook events, PCI compliance handling, and SCA/3DS for European regulation.

**When to use:**
- All projects that accept payments
- Subscriptions (Stripe Billing), marketplace payments (Stripe Connect)
- Portuguese payment methods: MB WAY and Multibanco references

**When NOT to use:**
- Digital products where VAT compliance is not feasible — consider LemonSqueezy
- Markets where Stripe is not available

**Configuration baseline:**
- **MUST** use test mode during development
- **MUST** verify webhook signatures
- **MUST** handle payment events via webhooks, not polling
- **MUST NOT** store raw card numbers — use Stripe's tokenization
- **SHOULD** implement idempotency keys for payment creation

**Key references:**
- → See [07-security-standards.md, Section 8] — Encryption and sensitive data
- → See [03-api-design.md] — Webhook handling patterns

---

#### Easypay — 🔍 Assess

**What it is:** Portuguese payment provider supporting MB WAY, Multibanco, credit cards.

**Why on the radar:** For projects requiring Portuguese payment methods outside Stripe's scope.

**When to reassess:** When a client specifically requires a local payment provider.

---

#### ifthenpay — 🔍 Assess

**What it is:** Portuguese payment gateway for Multibanco, MB WAY, credit cards, Payshop.

**Why on the radar:** Alternative to Easypay for Portuguese-market projects.

**When to reassess:** Alongside Easypay.

---

#### LemonSqueezy — 🔍 Assess

**What it is:** A Merchant of Record platform handling VAT/tax collection for digital products.

**Why on the radar:** Eliminates VAT compliance burden for digital product sales across EU countries.

**When to reassess:** When launching digital products sold to customers across multiple EU countries.

---

#### PayPal — ⛔ Hold

**Why Hold:** Stripe provides superior DX, cleaner API, and broader payment method support.

**What to use instead:** Stripe.

---

### 4.19 Date & Time

---

#### Temporal API — 🔬 Trial

**What it is:**
The native JavaScript date/time API (ES2026, TC39 Stage 4). A global
namespace object providing immutable, timezone-aware types: Instant,
ZonedDateTime, PlainDate, PlainTime, Duration, and more.

**Why Trial:**
Temporal reached Stage 4 in March 2026 and is part of ES2026. Shipped
in Chrome 144, Firefox 139, and Edge 144. Safari support is in Technology
Preview. TypeScript 6.0 Beta includes type definitions. Zero bundle cost
when native — eliminates the need for date libraries entirely.

**What to observe during Trial:**
- Safari shipping timeline (currently Technology Preview only)
- Node.js v26 support timeline
- Integration with form libraries and date pickers
- Polyfill performance and size (~100KB) when Safari fallback is needed

**Success criteria for Adopt:**
- Safari ships native support (full cross-browser availability)
- Node.js ships native support
- TypeScript types are stable (non-beta)
- At least one real project uses Temporal without polyfill issues

**Key references:**
- [TC39 Proposal](https://github.com/tc39/proposal-temporal)
- [MDN Documentation](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Temporal)
- Polyfills: @js-temporal/polyfill, temporal-polyfill

---

#### date-fns — ✅ Adopt

**What it is:**
A modular, functional date utility library for JavaScript. Each function
is a standalone import, enabling effective tree-shaking. Works with
native Date objects.

**Why Adopt:**
date-fns provides the most comprehensive set of date utilities with
excellent TypeScript support. Its functional, modular architecture aligns
with the project's principles (composability, tree-shaking, explicit
imports). It is the recommended library until the Temporal API achieves
full cross-browser support.

**When to use:**
- All date manipulation, formatting, and comparison in production code
- Timezone conversions via date-fns-tz companion package
- Projects that must support Safari or older browsers without polyfills

**When NOT to use:**
- When the project targets only Chrome/Firefox/Edge and can use Temporal
  natively — prefer the platform over a dependency
- Simple formatting that the Intl API handles natively

**Configuration baseline:**
- Import only the functions you need (never import the full library)
- Pair with date-fns-tz for timezone operations
- Use ISO-8601 format strings for consistency

**Key references:**
- [Official documentation](https://date-fns.org/)
- [date-fns-tz](https://github.com/marnusw/date-fns-tz)

---

### 4.20 Build Tooling

---

#### Vite — ✅ Adopt

**What it is:**
A next-generation frontend build tool and development server. Provides instant server start via
native ESM, lightning-fast HMR, and optimized production builds via Rollup.

**Why Adopt:**
Vite transformed frontend development — instant server start and sub-second HMR regardless of
project size.

**When to use:**
- All new React SPA projects
- As the build tool under Vitest
- As the underlying engine for Astro and other Vite-based frameworks

**When NOT to use:**
- Next.js projects — Next.js uses its own build system

---

#### esbuild — 🔬 Trial

**What it is:** An extremely fast JavaScript/TypeScript bundler written in Go.

**Why Trial:** Valuable standalone for building libraries, CLI tools, and Node.js packages where
Vite's full feature set is unnecessary.

**What to observe:** Use cases beyond what Vite provides.

---

#### Turbopack — ✅ Adopt

**What it is:**
A Rust-based incremental bundler by Vercel, now the default bundler in Next.js 16 for both
development and production. Uses a unified graph for all environments (client, server, edge),
parallelized incremental computation, and filesystem caching for near-instant rebuilds.

**Why Adopt:**
Turbopack became stable and the default bundler in Next.js 16 (October 2025). It is no longer
opt-in — all `next dev` and `next build` commands use Turbopack by default. File system caching
became stable in v16.1. Real-world results show 2-5x faster production builds and up to 10x
faster Fast Refresh. Server Fast Refresh (fine-grained server-side hot reloading) shipped in v16.2.

**When to use:**
- All Next.js 16+ projects — it is the default, no configuration needed
- Development — instant HMR, lazy bundling, filesystem caching across restarts
- Production builds — faster than Webpack with improved tree-shaking

**When NOT to use:**
- Non-Next.js projects — Turbopack is currently Next.js-only (standalone version planned)
- Projects with custom Webpack plugins that have no Turbopack equivalent — use `--webpack` flag
- Vite + React SPAs — continue using Vite (Turbopack is for Next.js)

**Configuration baseline:**
- **No configuration needed** — Turbopack is the default in Next.js 16+
- **SHOULD** use filesystem caching (enabled by default in dev since v16.1)
- **MAY** opt into build caching with `experimental.turbopackFileSystemCacheForBuild`
- To opt out (if needed): `next dev --webpack` / `next build --webpack`
- Turbopack config is now top-level in `next.config.ts` (not under `experimental`)

---

#### Turborepo — 🔍 Assess

**What it is:** A build system for JavaScript/TypeScript monorepos.

**Why on the radar:** Relevant when managing multiple related packages.

**When to reassess:** When managing a shared component library across multiple apps.

---

#### Webpack — ⛔ Hold

**Why Hold:** Turbopack is now the default bundler in Next.js 16 for both development and
production. Vite provides a superior experience for standalone projects. Webpack's complex
configuration system is no longer justified. Next.js still supports Webpack via the `--webpack`
flag for projects with custom plugins that have no Turbopack equivalent, but this is a
transitional escape hatch, not a recommended path.

**What to use instead:** Turbopack (via Next.js 16+) for Next.js projects, Vite for standalone
projects.

---

### 4.21 Email Services

---

#### Nodemailer — ✅ Adopt

**What it is:**
The standard Node.js library for sending emails via SMTP.

**Why Adopt:**
Foundational email layer. Works with any SMTP server — no vendor lock-in.

**When to use:**
- Sending emails through SMTP when a higher-level service is not available
- Projects with an existing SMTP provider

**When NOT to use:**
- When Resend provides better DX for the use case
- High-volume marketing email

**Guidance:**
- **MUST** use environment variables for SMTP credentials
- **MUST** validate email addresses before sending
- **SHOULD** implement retry logic for transient failures
- **MUST NOT** send emails synchronously in request handlers

---

#### Resend — 🔬 Trial

**What it is:**
An API-first email service with native react-email integration.

**Why Trial:**
Modern approach — clean API, excellent documentation, React component model for templates.

**What to observe:** Delivery reliability, react-email workflow, pricing at scale, API reliability.

**Success criteria:** Reliable delivery, maintainable templates, sustainable pricing.

---

#### react-email — 🔬 Trial

**What it is:** Library for building email templates using React components.

**Why Trial:** Abstracts the pain of email HTML behind React components that produce battle-tested
email-compatible output.

**What to observe:** Rendering consistency across email clients (especially Outlook), integration
with Resend and Nodemailer.

---

#### SendGrid — 🔍 Assess

**What it is:** Established email platform for transactional and marketing email.

**Why on the radar:** Proven track record for high-volume email. Fallback if Resend's pricing or
reliability becomes an issue.

**When to reassess:** When email volumes exceed Resend's comfort zone, or when marketing email
capabilities are needed.

---

#### Mailgun — 🔍 Assess

**What it is:** Developer-focused email API with inbound email processing capability.

**Why on the radar:** Inbound email parsing is a unique capability for projects that need to
receive and process emails.

**When to reassess:** When a project needs to receive and parse incoming emails.

---

### 4.22 SEO & Web Analytics

---

#### Google Search Console — ✅ Adopt

**What it is:**
A free Google service monitoring how a website appears in Google Search results.

**Why Adopt:**
For any public-facing website, Google Search is the primary traffic source. Search Console is
the only tool showing exactly how Google sees the site.

**When to use:**
- Every public-facing website — no exceptions
- Client projects — set up from day one, include in handover
- Diagnosing indexation problems

**When NOT to use:**
- Internal tools behind authentication

**Configuration baseline:**
- **MUST** verify site ownership via DNS TXT record or HTML file
- **MUST** submit the sitemap after verification
- **SHOULD** configure email alerts for critical issues
- **SHOULD** review monthly — check crawl errors, dropped pages, Core Web Vitals

**Relationship with other standards:**
- `robots.txt` and `sitemap.xml` → See [05-frontend-standards.md]
- Core Web Vitals → complements Sentry and Vercel Analytics
- Security issues → See [07-security-standards.md]

---

#### Google Lighthouse — ✅ Adopt

**What it is:**
An auditing tool built into Chrome DevTools analyzing Performance, Accessibility, Best Practices,
SEO, and PWA.

**Why Adopt:**
Most comprehensive automated quality audit for web pages. Free, requires no setup.

**When to use:**
- During development, in CI pipelines, client presentations, before launch

**When NOT to use:**
- As sole performance metric — Lighthouse is lab data. Use Vercel Analytics or Search Console
  for field data.

**Configuration baseline:**
- **SHOULD** run on every critical page before deployment
- **SHOULD** integrate Lighthouse CI into the CI pipeline
- **SHOULD** set minimum score thresholds (Performance ≥ 80, Accessibility ≥ 90, SEO ≥ 90)
- **MUST** prioritize Accessibility score — it reflects real user impact

**Key references:**
- → See [05-frontend-standards.md] — Accessibility and performance standards
- → See [06-testing-strategy.md] — Lighthouse CI as quality gate

---

#### Google Analytics (GA4) — 🔬 Trial

**What it is:**
Google's web analytics platform using an event-based model.

**Why Trial:**
Industry standard for analytics with deep Google ecosystem integration. However, RGPD compliance
requires informed consent, cookie banner, and privacy policy disclosure.

**What to observe:** RGPD compliance burden, data accuracy with consent banners, configuration
complexity.

**Success criteria:** RGPD-compliant implementation where analytics data is actively used for
product decisions.

**RGPD note:** **MUST** implement a cookie consent mechanism before enabling GA4 on any production
site. → See [07-security-standards.md, Section 14]

---

#### Vercel Analytics — 🔬 Trial

**What it is:**
Built-in analytics from Vercel providing real-user Web Vitals and basic traffic analytics.

**Why Trial:**
Collects real-user performance data (field data). Does not use cookies — more RGPD-friendly
than GA4.

**What to observe:** Value of field data vs Lighthouse lab data, traffic analytics depth,
privacy model.

**Success criteria:** Actionable performance insights that complement Lighthouse.

---

#### Plausible — 🔍 Assess

**What it is:** Lightweight, privacy-first analytics. No cookies, EU-hosted.

**Why on the radar:** Does not require cookie consent under RGPD — removes legal complexity and
negative UX impact of consent popups.

**When to reassess:** When launching privacy-sensitive projects or when GA4's burden is unacceptable.

---

#### Semrush / Ahrefs — 🔍 Assess

**What it is:** Professional SEO research platforms.

**Why on the radar:** For freelance projects where SEO is a deliverable. Paid tools (€100+/month).

**When to reassess:** When actively offering SEO services to clients.

### 4.23 Internationalization (i18n)

---

#### next-intl — ✅ Adopt

**What it is:**
An internationalization library designed specifically for Next.js App Router. Provides type-safe
message keys, Server Component support, locale-based routing, number/date/time formatting, and
pluralization — all integrated with Next.js's file-based routing and middleware.

**Why Adopt:**
For Next.js applications that need multiple languages, next-intl is the most aligned choice. It
works natively with Server Components (messages are resolved on the server, no client-side bundle
for translations), supports type-safe keys (typos in translation keys are caught at build time),
and integrates with Next.js middleware for locale detection and routing.

**When to use:**
- Any Next.js application that needs multi-language support
- Projects starting with one language but planning to add more — next-intl's structure scales
  from 2 to 20+ locales without architectural changes

**When NOT to use:**
- Non-Next.js projects (Vite + React SPAs) — use react-i18next instead
- Projects that will never need more than one language — do not add i18n infrastructure preemptively

**Configuration baseline:**
- **MUST** organize translations in structured JSON files per locale (`messages/en.json`,
  `messages/pt.json`)
- **MUST** configure Next.js middleware for locale detection and routing
- **SHOULD** enable type-safe message keys via TypeScript integration
- **SHOULD** extract hardcoded strings early — retrofitting i18n is significantly more expensive
  than starting with it
- **SHOULD** use ICU message format for plurals and interpolation

**Scaling guidance:**
- **Small projects (2–3 locales):** JSON files in the repository, manual translation management
- **Medium projects (4–10 locales):** Consider a translation management platform (Crowdin, Lokalise)
  that syncs with the JSON files
- **Large projects (10+ locales):** Translation platform is required. Automate sync via CI.
  Consider lazy-loading locale files to reduce bundle impact.

**Key references:**
- → See [05-frontend-standards.md] — i18n implementation patterns, string extraction, RTL support
- → See [01-core-principles.md, Section 1.1] — Software Is Built for People (localization is UX)

---

#### react-i18next — 🔬 Trial

**What it is:**
The React binding for i18next, the most popular JavaScript internationalization framework.
Provides hooks (`useTranslation`), components (`<Trans>`), and plugins for language detection,
backend loading, and caching.

**Why Trial:**
For Vite + React SPAs and non-Next.js projects, react-i18next is the most established solution.
Its plugin ecosystem is vast (lazy loading, language detection, ICU format), and the community
is the largest in the React i18n space. Trial because next-intl is preferred for Next.js — 
react-i18next is the fallback for other React contexts.

**What to observe during trial:**
- Bundle size impact — i18next loads all translations by default. Configure lazy loading for
  production.
- DX compared to next-intl — is the API ergonomic for the project's needs?
- Type safety — i18next supports type-safe keys but requires more configuration than next-intl.

**Success criteria:** Reliable i18n in at least one non-Next.js React project.

---

#### i18next — 🔬 Trial

**What it is:** The framework-agnostic core of react-i18next. Runs in Node.js, browsers, and any
JavaScript environment. Provides translation resolution, interpolation, pluralization, and a
plugin system for loading translations from various sources.

**Why Trial:** Relevant for backend services (Express, NestJS) that need to generate localized
content (emails, PDFs, error messages). Also the foundation for react-i18next.

**What to observe:** Use cases in backend services where localized output is needed.

---

#### FormatJS (react-intl) — 🔍 Assess

**What it is:** A suite of libraries for internationalization using the ICU message format standard.
Provides advanced pluralization, gender-aware translations, and number/date formatting.

**Why on the radar:** FormatJS handles complex localization scenarios (languages with multiple
plural forms, gender agreement) more robustly than simpler i18n libraries. Relevant if the
project targets languages with complex grammatical rules.

**When to reassess:** When targeting languages with complex plural or gender rules (Arabic, Polish,
Russian) where simpler i18n approaches produce awkward translations.

---

### 4.24 LLM Providers & Gateways

---

#### Anthropic API (Claude) — ✅ Adopt

**What it is:**
Anthropic's API for the Claude model family (Opus, Sonnet, Haiku). Provides large-context LLMs for
reasoning, coding, agentic workflows, and document analysis, with native tool use, prompt caching,
vision input, and structured outputs.

**Why Adopt:**
Claude is the default model for reasoning-heavy and agentic work across the stack. Its strength in
tool use, instruction-following, and long-context document analysis directly serves the document-
assistant and agent use cases. The promotion from Trial to Adopt is justified by real project usage,
not by maturity alone (see §2.2 movement rules).

**When to use:**
- Reasoning-heavy tasks, coding assistants, and agent orchestration
- Document analysis and the generation step of RAG pipelines
- Structured extraction where accuracy matters more than per-token cost
- Workflows needing large context windows or prompt caching of stable context

**When NOT to use:**
- High-volume, low-complexity classification/routing — use a cheaper/smaller model or Gemini Flash
- RGPD-strict workloads where no data may leave the perimeter — use local inference (§3.25)
- Trivial tasks a small local model handles adequately (Complexity Test — avoid overkill)

**Configuration baseline:**
- **MUST** store API keys in environment variables / a secret manager — never in code or client bundles → See [07-security-standards.md]
- **MUST** set spending limits and budget alerts on the account
- **MUST** validate structured/tool outputs against a schema (Zod / Pydantic) before use
- **MUST** implement timeouts and retries with exponential backoff
- **MUST** assess RGPD before sending personal data (DPA, data-retention settings) → See [07-security-standards.md]
- **SHOULD** pin explicit model versions (dated strings), not floating aliases, and test before upgrading
- **SHOULD** use prompt caching for stable system prompts / repeated context to cut cost
- **SHOULD** route calls through an abstraction or AI Gateway to reduce provider lock-in (§3.24)

**Key references:**
- → See [07-security-standards.md] — API key management, prompt injection, RGPD/data processing
- → See [08-observability.md] — tracing LLM calls (Langfuse, §3.29)
- → See §3.26 — agent frameworks that orchestrate Claude
- → See §3.28 — Claude as the generation step over retrieved context

---

#### OpenAI API — ✅ Adopt

**What it is:**
OpenAI's API covering the GPT model family, text embeddings (text-embedding-3), and the Realtime API
for speech-to-speech voice agents. Has the broadest third-party ecosystem and SDK/tooling support of
the providers.

**Why Adopt:**
OpenAI is adopted primarily as the default source of embeddings for RAG and as the simplest path to
real-time voice, in addition to general-purpose LLM tasks. Its ecosystem breadth makes it the lowest-
friction integration when tooling availability matters. Promotion to Adopt reflects real usage.

**When to use:**
- Generating embeddings for RAG retrieval (§3.28)
- Real-time voice agents via the Realtime API (§3.31)
- General LLM tasks where ecosystem/SDK breadth reduces integration effort
- Multimodal inputs where the model fits the task

**When NOT to use:**
- RGPD-strict workloads where data may not leave the perimeter — use local inference (§3.25)
- Cost-sensitive, high-volume generation — compare against Gemini Flash for price/speed
- Designs that must avoid single-provider lock-in — front with an AI Gateway (§3.24)

**Configuration baseline:**
- **MUST** store API keys in environment variables / a secret manager — never client-side → See [07-security-standards.md]
- **MUST** set spending limits and budget alerts
- **MUST** validate structured/tool outputs against a schema (Zod / Pydantic)
- **MUST** implement timeouts and retries with exponential backoff
- **MUST** keep the embedding model identical at index time and query time — mismatched models silently break retrieval → See §3.28
- **SHOULD** pin explicit model versions and test before upgrading
- **SHOULD** route through an abstraction or AI Gateway to reduce lock-in (§3.24)

**Key references:**
- → See §3.28 — embeddings for RAG (model-consistency rule)
- → See §3.31 — Realtime API as the voice modality
- → See [07-security-standards.md] — key management, RGPD/data processing
- → See [08-observability.md] — cost and latency tracing

---

#### Google Gemini API — ✅ Adopt

**What it is:**
Google's API for the Gemini model family (Pro, Flash, Flash-Lite). Large context windows (1M tokens),
multimodal input, with Flash / Flash-Lite positioned as the highest-speed, lowest-cost options among
the major providers.

**Why Adopt:**
Gemini is the default for cost-sensitive and high-volume workloads — classification, routing, high-traffic
public chat — where Flash/Flash-Lite's price and speed beat Claude and GPT. Adoption is conditional on
using the paid tier, which both unlocks production reliability and resolves the data/RGPD constraint that
the free tier cannot meet.

**When to use:**
- Cost-sensitive, high-volume generation and classification/routing
- Long-context or multimodal tasks where the model fits
- Public-facing chat (e.g., site FAQ widget) where per-request cost must stay low

**When NOT to use:**
- Hardest reasoning / multi-file coding — prefer Claude (§4.24, Anthropic)
- Fully offline / on-prem requirements where no data may leave the perimeter — use local inference (§3.25)
- Designs that must avoid single-provider lock-in — front with an AI Gateway (§3.24)

**Configuration baseline:**
- **MUST** use the paid tier (or Vertex AI, EU region) for any client or personal data — the free tier may use inputs/outputs for model training and is restricted for EU commercial use → See [07-security-standards.md]
- **MUST** store API keys in environment variables / a secret manager — never client-side
- **MUST** set spending limits and budget alerts
- **MUST** validate structured/tool outputs against a schema (Zod / Pydantic)
- **MUST** implement timeouts and retries with exponential backoff (handle 429s gracefully)
- **SHOULD** default to Flash / Flash-Lite for cost-sensitive work; reserve Pro for harder reasoning
- **SHOULD** use batch mode (≈50% off) for async, non-real-time workloads
- **SHOULD** use context caching (paid tier) for stable, repeated context
- **SHOULD** pin explicit model versions and test before upgrading
- **SHOULD** route through an abstraction or AI Gateway to reduce lock-in (§3.24)

**Key references:**
- → See §3.24 — provider comparison and AI Gateway routing
- → See [07-security-standards.md] — free-tier data-training caveat, RGPD/data processing
- → See [08-observability.md] — cost and latency tracing

---

### 4.25 Local & Self-Hosted Inference

---

#### Ollama — 🔬 Trial

**What it is:**
A local model runtime that downloads and serves open-weight LLMs (Qwen3, Gemma, Phi-4, and others)
behind a simple local API. Designed for low-friction local inference — one command to pull and run a
model — and binds to localhost by default.

**Why Trial:**
Ollama is on trial as the default runtime for local, RGPD-sensitive development and offline iteration:
running models on the developer's own machine means no data leaves the perimeter and no per-token cost
during prototyping. It is a development/prototyping tool — the production serving path is vLLM (§3.25),
not Ollama — and it has personal-project usage but is not yet proven in a structured workflow.

**When to use:**
- Local development and iteration on RAG/agent logic without cloud cost or data exposure
- Prototyping with small open-weight models (≤ ~8B) on constrained hardware
- Personal / internal projects where data must stay on-device

**When NOT to use:**
- Production multi-user serving — use vLLM behind a reverse proxy with auth (§3.25)
- Tasks needing frontier-level reasoning that small local models cannot deliver — use a cloud provider (§4.24)
- Anything where the model size genuinely exceeds the local hardware (the trade-off learned the hard way:
  a 4B model on a weak laptop is both slow and quality-limited)

**What to observe:**
- Quality/latency of small models (e.g., Qwen3, Gemma, Phi-4) on real PT-language tasks vs cloud models
- Where the dev/prod boundary lands — what is prototyped locally vs what must run on a stronger hosted model
- Resource ceiling on available hardware (RAM/VRAM) and which model sizes are actually usable

**Configuration baseline:**
- **MUST NOT** expose the Ollama port beyond localhost without authentication / a reverse proxy → See [07-security-standards.md]
- **SHOULD** treat Ollama as a dev runtime and plan a separate production serving path (vLLM) early
- **SHOULD** pick multilingual open-weight models (Qwen3, Gemma) for PT-language work

**Success criteria (to promote to Adopt):**
- Used as the standard local-dev inference step in at least one real project, with a clear, documented
  hand-off to a production serving path

**Key references:**
- → See §3.25 — vLLM as the production serving counterpart
- → See [07-security-standards.md] — never expose a local inference port without auth
- → See §4.24 — cloud providers for tasks beyond local model capability

---

### 4.26 AI SDKs & Agent Frameworks

---

#### Vercel AI SDK — 🔬 Trial

**What it is:**
The de facto TypeScript toolkit (v6) for building AI features and agents — a unified provider interface,
streaming primitives (`streamText`, `useChat`), tool-calling with Zod schemas, and agent loops, designed
to work across both Next.js frontend and API routes.

**Why Trial:**
It is the default for the TS side of the stack: it unifies providers (reducing lock-in) and its agent and
streaming abstractions fit the site-widget and booking use cases directly. New to the radar, so it enters
as Trial despite its de facto status — Assess→Adopt is not allowed to skip (§2.2).

**What to observe:**
- Provider-swap ergonomics and how cleanly it fronts Anthropic/OpenAI/Gemini
- Streaming UX in Next.js and tool-calling reliability with Zod schemas
- Whether its agent loop suffices for complex flows, or a dedicated framework (LangGraph) is needed
- Version churn (v6 stable, v7 in canary)

**Success criteria (to promote to Adopt):**
- Used in a real TS project (e.g., site FAQ widget or booking front end) with streaming + tool-calling proven

**Key references:**
- → See §3.26, §3.31 — agent/channel use cases; → See §4.24 — providers it fronts
- → See [05-frontend-standards.md] — usage within the Next.js/React layer

---

#### LangGraph — 🔬 Trial

**What it is:**
A stateful agent-orchestration framework (Python + JS) modelling agents as a graph state machine, with
durable execution, checkpointing, and human-in-the-loop control.

**Why Trial:**
It is the default for production-grade, stateful agents on the Python/FastAPI side — agentic RAG and
multi-step flows (e.g., a booking agent that checks availability, proposes, confirms). Generally
production-proven, but unproven in this stack's real work.

**What to observe:**
- Fit with a FastAPI backend and integration with observability (Langfuse, §4.29)
- Complexity-vs-payoff: it should be reserved for flows where simple tool-calling is genuinely insufficient
- Debuggability of graph state in real failure cases

**Success criteria (to promote to Adopt):**
- Used in one real agentic project where plain tool-calling was not enough, with stable, debuggable behavior

**Key references:**
- → See §3.26 — agent framework selection; → See §4.29 — tracing agent runs
- Note: agent *patterns* (CRAG, Agentic RAG, Adaptive RAG) belong to the future AI engineering doc, not the radar

---

#### LlamaIndex — 🔬 Trial

**What it is:**
A Python (and TS) framework specialized in indexing, retrieval, and document agents — connectors,
chunking/indexing primitives, query engines, and RAG-oriented abstractions.

**Why Trial:**
On trial as a higher-level option for the retrieval/indexing layer of the document-assistant use case,
where its primitives can shortcut hand-built pipelines. Its scope overlaps with a hand-rolled
pgvector + Docling pipeline, so the trial is about whether the abstraction earns its weight.

**What to observe:**
- Whether its abstractions speed development without hiding the retrieval behavior we need to tune
- Interop with the chosen store (pgvector/Qdrant) and ingestion (Docling)
- Lock-in / escape-hatch cost if a custom pipeline is later preferred

**Success criteria (to promote to Adopt):**
- Used in one real RAG project where it measurably reduced effort vs a hand-built pipeline

**Key references:**
- → See §3.28 — storage/retrieval it builds on; → See §4.27 — ingestion (Docling)

---

### 4.27 Document Ingestion & Parsing

---

#### Docling — 🔬 Trial

**What it is:**
An open-source (IBM) document-parsing toolkit that converts PDFs, Office files, and images into
structured, AI-ready formats (Markdown / JSON) with layout awareness, table-structure recognition,
and OCR. Self-hostable, so documents never have to leave the perimeter.

**Why Trial:**
Docling is on trial as the default ingestion layer for RAG. Ingestion quality is the single biggest
lever on retrieval quality — broken tables and lost structure cannot be recovered downstream — and
Docling's self-hostable, table-aware parsing fits the document-assistant use case and RGPD constraints.
It is not yet proven across the document types found in real client work.

**What to observe:**
- Table-extraction fidelity on real PT documents (invoices, fiscal docs, contracts)
- OCR accuracy on scanned / low-quality inputs (vs falling back to a VLM-OCR model)
- Throughput and resource cost of self-hosting at expected document volumes
- Quality of output when fed into the chunking → embedding → retrieval pipeline

**Success criteria (to promote to Adopt):**
- Used in at least one real document-assistant project, integrated into the ingestion pipeline
- Table and OCR fidelity validated on the client's actual document types, with acceptable performance

**Key references:**
- → See §3.28 — retrieval pipeline that consumes the parsed output
- → See [07-security-standards.md] — self-hosted ingestion for RGPD-sensitive documents
- Note: chunking and ingestion *strategy* (the "how") belongs to the future AI engineering domain doc, not the radar

---

### 4.28 RAG Storage & Retrieval

---

#### pgvector (Supabase) — ✅ Adopt

**What it is:**
A PostgreSQL extension that adds a vector data type and approximate nearest-neighbor similarity search
(HNSW / IVFFlat indexes), available natively in Supabase. Stores embeddings alongside relational data
in the same database.

**Why Adopt:**
pgvector is the default RAG storage because it is an extension of the already-adopted stack (PostgreSQL
+ Supabase), not a new system. Keeping embeddings beside application data means transactional consistency,
metadata filtering and joins, RLS for multitenant isolation, and one datastore to operate instead of two.
A dedicated vector DB is added only when a measured need proves pgvector insufficient — the same
"add complexity only on evidence" rule applied to Redis.

**When to use:**
- RAG over modest-to-medium corpora (the common case for SMB / freelance projects)
- Any project already on PostgreSQL / Supabase
- Retrieval that needs metadata filtering, relational joins, or per-tenant isolation (RLS)

**When NOT to use:**
- Very large-scale or specialized filtered-vector workloads where a dedicated vector DB is measured to be needed — use Qdrant (§3.28)
- Massive pure-vector workloads with no relational component

**Configuration baseline:**
- **MUST** use an HNSW index for production similarity search — never rely on sequential scan → See [04-database-standards.md]
- **MUST** enable RLS on embedding tables for any multitenant data → See [04-database-standards.md], [07-security-standards.md]
- **MUST** keep the embedding model identical at index time and query time — mismatched models silently break retrieval → See §4.24 (OpenAI)
- **SHOULD** combine vector search with PostgreSQL full-text search for hybrid retrieval
- **SHOULD** use quantized vector types (e.g., `halfvec`) to cut storage on high-dimension embeddings
- **SHOULD** tune HNSW parameters (`m`, `ef_construction`) and query-time `ef_search` for the recall/latency trade-off
- **MAY** add a dedicated vector DB only when metrics show pgvector's filtering or scale is insufficient

**Key references:**
- → See [04-database-standards.md] — HNSW indexing, RLS, vector column design
- → See [07-security-standards.md] — multitenant isolation for embeddings
- → See §3.28 — embeddings and reranking that feed retrieval
- → See §4.24 — embedding-model consistency rule

---

### 4.29 LLM Observability & Evaluation

---

#### Langfuse — 🔬 Trial

**What it is:**
An open-source LLM observability and evaluation platform: tracing, cost tracking, prompt management,
and evals. Self-hostable, framework-agnostic, with Python and TS SDKs.

**Why Trial:**
The default observability layer for LLM/agent apps — self-hostable (RGPD-friendly) and framework-agnostic.
On trial rather than Adopt partly because of a governance unknown: it was acquired by ClickHouse (Jan 2026)
and the long-term roadmap is still to be confirmed.

**What to observe:**
- Self-host operational cost and trace coverage across the Python/TS SDKs and agent frameworks
- Whether cost/latency/quality visibility is actually actionable in iteration
- The ClickHouse-acquisition roadmap and any licensing/governance shifts

**Success criteria (to promote to Adopt):**
- Instrumented in one real LLM project, providing cost and quality visibility that changed decisions

**Key references:**
- → See [08-observability.md] — how to instrument and what to track (the "how")
- → See §3.29 — evaluation tools it pairs with

---

#### Ragas — 🔬 Trial

**What it is:**
A RAG evaluation framework that computes metrics — faithfulness, answer/context relevance, recall —
against a test set, turning retrieval-strategy choices into measured evidence rather than guesswork.

**Why Trial:**
The evaluation loop is what separates a professional RAG system from a shallow prototype. Ragas is the
default for measuring strategies, on trial until proven on a real golden set (notably absent from past
course-project work).

**What to observe:**
- Whether its metrics align with human judgment on PT-language content
- Effort to build and maintain a representative golden set
- Feasibility of running it as a gate in CI

**Success criteria (to promote to Adopt):**
- A golden set + Ragas used to choose between RAG strategies in a real project, integrated into the workflow

**Key references:**
- → See §3.29 — observability/eval tooling
- → See [06-testing-strategy.md] — evaluation as a testing discipline
- Note: evaluation *methodology* (benchmark design, metric selection) belongs to the future AI engineering doc

---

### 4.30 Agent Protocols & Interoperability

---

#### MCP (Model Context Protocol) — 🔬 Trial

**What it is:**
An open, vendor-neutral protocol (donated to the Linux Foundation / Agentic AI Foundation) that
standardizes how agents connect to tools and data sources through MCP servers.

**Why Trial:**
The integration layer for agent tool-use — e.g., exposing Cal.com or a calendar/email as an MCP server.
It is the de facto standard, so it enters as a strong Adopt candidate, but as a new radar entry it starts
at Trial pending first real use.

**What to observe:**
- Server auth/security (OAuth, scopes) — an agent with tool access is a security-critical surface
- Maturity of available servers vs the cost of building custom ones
- Whether MCP is worth it for simple cases, or direct tool-calling is leaner

**Success criteria (to promote to Adopt):**
- An MCP server (custom or existing) integrated into a real agent, with auth handled correctly

**Key references:**
- → See §3.30 — protocol selection; → See §3.31 — Cal.com exposed as an MCP server
- → See [07-security-standards.md] — server authentication and the risk surface of tool-enabled agents

---

## 5. Stack Baselines

A stack baseline is a **pre-approved combination of technologies** for a specific type of project.
It eliminates the decision overhead of choosing tools for every new project — the baseline is
the default, and deviations require justification.

Each baseline includes only technologies classified as ✅ Adopt or 🔬 Trial in this radar.
Technologies in 🔍 Assess or ⛔ Hold are never part of a baseline.

> **Rule:** Starting a new project? Pick the matching baseline and begin. Customize only when
> a specific requirement demands it — and document the deviation in an ADR.

---

### 5.1 Full-Stack Web Application (Next.js)

**When to use:** Applications with a user-facing frontend, server-side logic, authentication,
and database. This is the **default baseline** — use it unless a different type clearly fits better.

**Examples:** SaaS products, client portals, e-commerce platforms, internal business applications,
dashboard applications with user accounts.

```text
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                             │
│  Next.js (App Router) + React + TypeScript                  │
│  Tailwind CSS + shadcn/ui + Radix UI                        │
│  TanStack Query (client data) + React hooks (local state)   │
├─────────────────────────────────────────────────────────────┤
│                        BACKEND                              │
│  Next.js Route Handlers (API)                               │
│  Zod (validation at boundaries)                             │
├─────────────────────────────────────────────────────────────┤
│                     DATA & AUTH                             │
│  Supabase (PostgreSQL + Auth + Realtime + Storage)          │
│  Prisma (ORM — Trial, evaluate per project)                 │
├─────────────────────────────────────────────────────────────┤
│                      TESTING                                │
│  Vitest + Testing Library (unit + component)                │
│  Playwright (E2E critical paths)                            │
│  Faker.js (test data)                                       │
├─────────────────────────────────────────────────────────────┤
│                    CODE QUALITY                             │
│  ESLint + Prettier + EditorConfig                           │
│  Husky + lint-staged + commitlint                           │
│  gitleaks (pre-commit secret detection)                     │
├─────────────────────────────────────────────────────────────┤
│                   OBSERVABILITY                             │
│  Sentry (errors + performance)                              │
│  Pino (structured logging in API routes)                    │
│  UptimeRobot (uptime monitoring)                            │
│  Google Search Console + Lighthouse (SEO + audits)          │
├─────────────────────────────────────────────────────────────┤
│                    DEPLOYMENT                               │
│  Vercel (hosting) + Supabase Cloud (database)               │
│  GitHub Actions (CI/CD)                                     │
│  Dependabot (dependency updates)                            │
├─────────────────────────────────────────────────────────────┤
│                     PAYMENTS                                │
│  Stripe (if applicable)                                     │
├─────────────────────────────────────────────────────────────┤
│                      EMAIL                                  │
│  Resend + react-email (Trial) or Nodemailer (SMTP fallback) │
└─────────────────────────────────────────────────────────────┘
```

#### Key Decisions for This Baseline

- **Server Components by default** — add `'use client'` only when needed
  (→ See [05-frontend-standards.md])
- **Supabase handles auth + database + realtime** — no need for separate services until the
  project outgrows Supabase's capabilities
- **TanStack Query for client-side data fetching** — Server Components handle the majority of
  data needs; TanStack Query is for Client Components that need caching and real-time data
- **Prisma is optional (Trial)** — for simple CRUD, Supabase's client library is sufficient.
  Add Prisma when complex queries, relations, or migrations justify the overhead
- **Payments are conditional** — include Stripe only when the project accepts payments

#### When to Deviate

- If the API needs to serve multiple clients (mobile app, third-party) → consider separating
  the backend (see Baseline 5.2)
- If the project has no auth or database needs → consider Landing Page baseline (5.4)
- If the project is heavily content-driven with minimal interactivity → consider Landing Page
  baseline (5.4) with Astro

---

### 5.2 API-Only Backend (REST)

**When to use:** Standalone backend services that expose a REST API consumed by one or more
clients (frontend, mobile app, third-party integrations). The backend is developed, deployed,
and scaled independently from any frontend.

**Examples:** Multi-client APIs (web + mobile), microservices, webhook processors, backend
services for third-party integrations, data processing APIs.

```text
┌─────────────────────────────────────────────────────────────┐
│                      FRAMEWORK                              │
│  Express.js + TypeScript (default)                          │
│  — OR NestJS + TypeScript (Trial — for structured APIs)     │
│  — OR FastAPI + Python (Trial — for AI/ML endpoints)        │
├─────────────────────────────────────────────────────────────┤
│                     VALIDATION                              │
│  Zod (Express) or class-validator (NestJS) or Pydantic      │
│  (FastAPI)                                                  │
├─────────────────────────────────────────────────────────────┤
│                    DATA & AUTH                              │
│  PostgreSQL (via Supabase Cloud or self-managed)            │
│  Prisma (Trial) or direct SQL queries                       │
│  Auth.js or Supabase Auth (depending on architecture)       │
├─────────────────────────────────────────────────────────────┤
│                   DOCUMENTATION                             │
│  OpenAPI / Swagger (auto-generated or spec-first)           │
│  Postman collection (manual testing + team sharing)         │
├─────────────────────────────────────────────────────────────┤
│                      TESTING                                │
│  Vitest + Supertest (unit + API integration)                │
│  Faker.js (test data)                                       │
├─────────────────────────────────────────────────────────────┤
│                    CODE QUALITY                             │
│  ESLint + Prettier + EditorConfig                           │
│  Husky + lint-staged + commitlint                           │
│  gitleaks (pre-commit secret detection)                     │
├─────────────────────────────────────────────────────────────┤
│                   OBSERVABILITY                             │
│  Sentry (errors)                                            │
│  Pino (structured logging)                                  │
│  UptimeRobot (uptime monitoring)                            │
├─────────────────────────────────────────────────────────────┤
│                    DEPLOYMENT                               │
│  Docker + Docker Compose (containerization)                 │
│  Railway or Render (Trial — hosting)                        │
│  GitHub Actions (CI/CD)                                     │
│  Dependabot (dependency updates)                            │
└─────────────────────────────────────────────────────────────┘
```

#### Key Decisions for This Baseline

- **Framework choice depends on project complexity:**
  - Express.js → default for most APIs (simple, flexible, maximum ecosystem)
  - NestJS → when the API is complex enough that Express's lack of structure becomes a liability
  - FastAPI → when the backend is Python-centric (AI/ML endpoints, data processing)
- **Docker is required** — standalone APIs need containerization for reproducible deployments
- **OpenAPI spec is required** — a standalone API without documentation is unusable
- **No frontend tooling** — this baseline excludes React, Tailwind, and component libraries

#### When to Deviate

- If the API only serves a co-located Next.js frontend → use Full-Stack baseline (5.1)
- If the API is a simple webhook processor → strip to Express + Zod + Vitest + Docker
- If the service needs background job processing → add BullMQ (🔍 Assess) + Redis

---

### 5.3 Automation & Scripting (Python)

**When to use:** Scripts, automation workflows, data processing pipelines, AI/ML experiments,
and CLI tools. Not user-facing web applications.

**Examples:** Data extraction (ETL), web scraping, API integrations, report generation, file
processing, AI model training, scheduled tasks (cron jobs).

```text
┌─────────────────────────────────────────────────────────────┐
│                      LANGUAGE                               │
│  Python 3.11+ with type hints                               │
├─────────────────────────────────────────────────────────────┤
│                     VALIDATION                              │
│  Pydantic (data validation + settings management)           │
├─────────────────────────────────────────────────────────────┤
│                    ENVIRONMENT                              │
│  uv or poetry (dependency management + virtual environment) │
│  ruff (linter + formatter — replaces flake8 + black + isort)│
├─────────────────────────────────────────────────────────────┤
│                      TESTING                                │
│  pytest (unit + integration testing)                        │
│  Faker (test data generation)                               │
├─────────────────────────────────────────────────────────────┤
│                    CODE QUALITY                             │
│  ruff (linting + formatting in one tool)                    │
│  mypy or pyright (static type checking)                     │
│  pre-commit (Git hooks framework for Python projects)       │
├─────────────────────────────────────────────────────────────┤
│                   COMMON LIBRARIES                          │
│  requests or httpx (HTTP client)                            │
│  pandas (data manipulation — when needed)                   │
│  python-dotenv (environment variables)                      │
│  click or typer (CLI interfaces — when needed)              │
├─────────────────────────────────────────────────────────────┤
│                    AI/ML (when applicable)                  │
│  OpenAI / Anthropic SDK (LLM integration)                   │
│  LangChain (Assess — complex AI pipelines only)             │
│  Hugging Face (Assess — open-source models)                 │
├─────────────────────────────────────────────────────────────┤
│                    DEPLOYMENT                               │
│  Docker (containerization — for services and scheduled jobs)│
│  GitHub Actions (CI + scheduled execution)                  │
│  — OR direct execution (simple scripts, manual triggers)    │
└─────────────────────────────────────────────────────────────┘
```

#### Key Decisions for This Baseline

- **Python, not TypeScript** — for automation and scripting, Python's ecosystem is superior
- **ruff replaces the traditional Python toolchain** — single Rust-based tool for linting,
  formatting, and import sorting
- **uv or poetry for dependency management** — reproducible builds with lock files
- **Pydantic is the Python equivalent of Zod** — validates data at boundaries with type inference
- **Docker is conditional** — simple scripts do not need containerization; services and scheduled
  jobs do

#### When to Deviate

- If the script needs to expose an API → add FastAPI (Trial)
- If the automation is trivial (< 100 lines, no dependencies beyond stdlib) → skip the full
  baseline

---

### 5.4 Landing Page / Static Site

**When to use:** Content-focused websites with minimal or no interactivity, no authentication,
and no database. Primary goal: fast loading, excellent SEO, simple maintenance.

**Examples:** Company websites (concessionário, distribuidora), portfolio sites, marketing landing
pages, documentation sites, blogs.

```text
┌─────────────────────────────────────────────────────────────┐
│                      FRAMEWORK                              │
│  Astro (Trial — default for static sites)                   │
│  — OR Next.js (if interactive features justify it)          │
│  — OR Vite + React (if it is a SPA with no SEO needs)       │
├─────────────────────────────────────────────────────────────┤
│                      STYLING                                │
│  Tailwind CSS                                               │
│  shadcn/ui (if using React components in Astro islands)     │
├─────────────────────────────────────────────────────────────┤
│                    CODE QUALITY                             │
│  ESLint + Prettier + EditorConfig                           │
│  Husky + lint-staged + commitlint                           │
├─────────────────────────────────────────────────────────────┤
│                      SEO                                    │
│  Google Search Console (indexation monitoring)              │
│  Google Lighthouse (audits — target ≥ 90 all categories)    │
│  robots.txt + sitemap.xml (→ 05-frontend-standards.md)      │
│  Structured data / JSON-LD (schema.org markup)              │
├─────────────────────────────────────────────────────────────┤
│                    ANALYTICS                                │
│  Vercel Analytics (Trial — if deployed to Vercel)           │
│  — OR Plausible (Assess — privacy-first alternative)        │
│  — OR GA4 (Trial — if deeper analytics needed, with RGPD    │
│       consent banner)                                       │
├─────────────────────────────────────────────────────────────┤
│                   OBSERVABILITY                             │
│  UptimeRobot (uptime monitoring)                            │
│  Sentry (if the site has interactive components)            │
├─────────────────────────────────────────────────────────────┤
│                    DEPLOYMENT                               │
│  Vercel (default) or Cloudflare Pages (Trial)               │
│  GitHub Actions (CI/CD)                                     │
└─────────────────────────────────────────────────────────────┘
```

#### Key Decisions for This Baseline

- **Astro is the default for static sites (Trial)** — zero JavaScript by default, perfect
  Lighthouse scores, React components for interactive islands
- **No backend, no database, no auth** — if the project needs these, use Baseline 5.1
- **SEO is a first-class concern** — Search Console, Lighthouse audits, sitemap, and structured
  data are not optional
- **Lighthouse target ≥ 90 in all categories** — static sites have no excuse for poor scores
- **Analytics choice depends on privacy requirements** — Vercel Analytics or Plausible preferred
  over GA4 for RGPD simplicity

#### When to Deviate

- If the client needs a contact form → add Supabase for form submissions or use a form service
- If the client needs a CMS → add a headless CMS (evaluate using Section 1)
- If the site grows to need auth or user accounts → migrate to Baseline 5.1

---

### 5.5 Baseline Comparison Matrix

| Dimension              | Full-Stack (5.1)     | API-Only (5.2)       | Automation (5.3)     | Landing Page (5.4)   | AI/RAG (5.6) |
|------------------------|----------------------|----------------------|----------------------|----------------------|----------------------|
| **Primary Language**   | TypeScript           | TypeScript or Python | Python               | TypeScript           | TypeScript + Python |
| **Framework**          | Next.js              | Express / NestJS / FastAPI | None (scripts) | Astro / Next.js      | FastAPI + Next.js |
| **Database**           | Supabase (PostgreSQL)| PostgreSQL           | Optional             | None                 | Supabase (PostgreSQL + pgvector) |
| **Auth**               | Supabase Auth        | Auth.js / Supabase   | None                 | None                 | Supabase / Auth.js |
| **Testing**            | Vitest + Playwright  | Vitest + Supertest   | pytest               | Lighthouse audits    | Ragas + Vitest / pytest |
| **Deployment**         | Vercel               | Railway / Render     | Docker / GH Actions  | Vercel / CF Pages    | Docker + Vercel |
| **SEO Priority**       | Medium               | None                 | None                 | Critical             | Low |
| **Docker Required**    | No (Vercel handles)  | Yes                  | Conditional          | No (static deploy)   | Conditional (AI service) |
| **Typical Complexity** | High                 | Medium–High          | Low–Medium           | Low                  | High |

---

### 5.6 AI / RAG Application

**When to use:** Applications whose core value is an LLM reasoning over private/domain data — document
assistants, support/booking assistants, internal knowledge search. Not generic web apps that merely
call an LLM for a minor feature (use 5.1 and add the provider SDK).

**Examples:** Internal "chat with your documents" assistant, WhatsApp/site booking assistant, business
FAQ widget, document extraction pipeline.

```text
┌─────────────────────────────────────────────────────────────┐
│                      ARCHITECTURE                          │
│  AI service: Python 3.11+ + FastAPI (Trial)                 │
│  Frontend:   Next.js + Vercel AI SDK (Trial)                │
├─────────────────────────────────────────────────────────────┤
│                    LLM PROVIDER                            │
│  Claude (Adopt — reasoning/generation default)              │
│  Gemini Flash (Adopt — cost-sensitive/high-volume)          │
│  OpenAI (Adopt — embeddings, voice)                         │
│  AI Gateway (Trial — routing/fallback, reduces lock-in)     │
│  — OR Ollama (Trial, dev) → vLLM (Assess, prod) for RGPD    │
├─────────────────────────────────────────────────────────────┤
│                     INGESTION                              │
│  Docling (Trial — layout/table-aware parsing, self-hosted)  │
├─────────────────────────────────────────────────────────────┤
│                  STORAGE & RETRIEVAL                       │
│  pgvector / Supabase (Adopt — default vector store)         │
│  Multilingual embeddings + reranker (Trial)                 │
│  Hybrid search (vector + PostgreSQL FTS)                    │
│  — Qdrant (Assess) only on measured need                    │
├─────────────────────────────────────────────────────────────┤
│              AGENT LAYER (when needed)                     │
│  Vercel AI SDK tool-calling (TS) — simple flows             │
│  — OR LangGraph (Trial, Python) — stateful/multi-step       │
│  LlamaIndex (Trial — retrieval/indexing primitives)         │
│  MCP (Trial — tools/data integration, e.g., Cal.com)        │
├─────────────────────────────────────────────────────────────┤
│                    VALIDATION                              │
│  Pydantic (Python) / Zod (TS) on all structured outputs     │
├─────────────────────────────────────────────────────────────┤
│              EVALUATION & OBSERVABILITY                    │
│  Ragas (Trial — RAG eval) + golden set — NOT optional       │
│  Langfuse (Trial — tracing, cost, prompt mgmt)              │
├─────────────────────────────────────────────────────────────┤
│              CHANNEL (booking/support variant)            │
│  WhatsApp Business Cloud API via BSP (Assess)               │
│  Cal.com (Assess) or self-built scheduling                  │
├─────────────────────────────────────────────────────────────┤
│                    DEPLOYMENT                              │
│  Docker (AI service); Railway/Render/VPS (FastAPI)          │
│  Vercel (Next.js frontend)                                  │
└─────────────────────────────────────────────────────────────┘
```

#### Key Decisions for This Baseline

- **Split architecture** — Python/FastAPI for the AI/RAG service (ecosystem), Next.js for the frontend.
  Keep the AI service behind a clean API boundary (→ 03-api-design.md)
- **pgvector is the default vector store, not a dedicated DB** — embeddings live beside relational data;
  add Qdrant only when metrics prove pgvector insufficient (same evidence rule as Redis)
- **Ingestion quality is the biggest lever on RAG quality** — Docling first; garbage chunks cannot be
  recovered downstream
- **Evaluation is mandatory, not optional** — Ragas + a golden set is what separates a professional system
  from a shallow prototype; it is the freelance differentiator
- **Observability from day one** — Langfuse instruments cost/quality before problems compound
- **RGPD drives the provider choice** — cloud providers MUST run on paid tiers; for data that cannot leave
  the perimeter, use local (Ollama dev → vLLM prod) (→ 07-security-standards.md)
- **The agent layer is conditional** — start with tool-calling; add LangGraph only when flows are genuinely
  stateful/multi-step (Complexity Test)
- **The "how" lives elsewhere** — chunking, retrieval strategies, agent patterns, eval methodology belong
  to the future 12-ai-engineering.md, not the radar

#### When to Deviate

- **Site FAQ widget (simplest case)** → TS-only: Next.js + Vercel AI SDK + pgvector + strict grounding;
  skip FastAPI, the agent layer, and the channel block
- **Agentic/booking assistant** → add the agent layer (LangGraph or Vercel AI SDK), the channel block
  (WhatsApp + Cal.com), and MCP for tool integration
- **Fully on-prem / RGPD-strict** → replace cloud providers with self-hosted vLLM; keep ingestion and
  storage self-hosted (Docling + pgvector)
- **Trivial LLM feature inside an existing app** → do not use this baseline; use 5.1 and add the provider SDK

---

## 6. Decision Guides

These guides provide quick answers to common technology decisions. Each guide presents the
decision context, the recommended path, and the reasoning — enabling fast, justified choices
without re-reading the full radar.

> **How to use:** Find the decision you are facing, follow the recommended path. If your context
> differs from the assumptions stated, consult the full technology profiles in
> [Section 4](#4-technology-profiles) for nuance.

---

### 6.1 Choosing a Frontend Framework

```text
Do you need a user-facing web application?
│
├─ YES → Does it need SEO (public pages, Google indexing)?
│        │
│        ├─ YES → Does it have significant server-side logic (auth, DB, API)?
│        │        │
│        │        ├─ YES → Next.js (App Router) ✅
│        │        │        [Baseline 5.1 — Full-Stack Web Application]
│        │        │
│        │        └─ NO → Is it primarily content (blog, marketing, company site)?
│        │                 │
│        │                 ├─ YES → Astro 🔬
│        │                 │        [Baseline 5.4 — Landing Page / Static Site]
│        │                 │
│        │                 └─ NO → Next.js (with static export if no server needed)
│        │
│        └─ NO → Is it a lightweight tool, dashboard, or prototype?
│                 │
│                 ├─ YES → Vite + React ✅
│                 │
│                 └─ NO → Next.js (default — covers most cases)
│
└─ NO → You probably need a backend, not a frontend.
         [See Section 6.2 — Choosing a Backend Framework]
```

**Summary:**
- **Default:** Next.js — covers the widest range of use cases
- **Static/content sites:** Astro — faster, lighter, better for SEO-only sites
- **Internal SPAs:** Vite + React — simplest setup, no server overhead
- **Rule of thumb:** When in doubt, start with Next.js. It is easier to simplify later than to
  add SSR, API routes, and auth to a Vite SPA.

---

### 6.2 Choosing a Backend Framework

```text
Does the project need a backend separate from the frontend?
│
├─ NO → Use Next.js Route Handlers ✅
│        [Co-located API, single deployment, shared types]
│
└─ YES → What is the primary language?
          │
          ├─ TypeScript/JavaScript
          │   │
          │   ├─ Is the API complex (many modules, DI needed, large team)?
          │   │   │
          │   │   ├─ YES → NestJS 🔬
          │   │   │        [Structured, SOLID-friendly, steeper learning curve]
          │   │   │
          │   │   └─ NO → Express.js ✅
          │   │            [Minimal, flexible, largest ecosystem]
          │   │
          │   └─ Is it a lightweight edge API?
          │       │
          │       └─ YES → Hono 🔍 (if targeting Cloudflare Workers)
          │
          └─ Python
              │
              └─ FastAPI 🔬
                 [Async, auto-docs, Pydantic validation, ideal for AI/ML]
```

**Summary:**
- **Default (with frontend):** Next.js Route Handlers
- **Default (standalone TS):** Express.js
- **Structured TS APIs:** NestJS — when Express's lack of structure becomes a problem
- **Python APIs:** FastAPI — modern, async, excellent for AI/ML
- **Rule of thumb:** Start with Route Handlers. Extract to Express only when the backend
  genuinely needs independent deployment or serves multiple clients.

---

### 6.3 Choosing a Database Strategy

```text
Does the project need persistent data storage?
│
├─ NO → Skip the database entirely.
│
└─ YES → Do you need relational data (users, orders, products, relationships)?
          │
          ├─ YES → PostgreSQL ✅
          │        │
          │        ├─ Do you also need auth, realtime, and file storage?
          │        │   │
          │        │   ├─ YES → Supabase ✅
          │        │   │
          │        │   └─ NO → Self-managed PostgreSQL
          │        │
          │        ├─ Do you need an ORM?
          │        │   │
          │        │   ├─ Complex queries/relations → Prisma 🔬 (evaluate)
          │        │   ├─ SQL-first approach → Drizzle 🔍 (assess)
          │        │   └─ Simple CRUD → Supabase client library (no ORM needed)
          │        │
          │        └─ Do you need flexible/document-like data?
          │            │
          │            └─ Use PostgreSQL JSONB columns (not MongoDB)
          │
          └─ Do you need caching or ephemeral data?
              │
              └─ Redis 🔍 — only when measured need exists.
```

**Summary:**
- **Default:** Supabase (PostgreSQL + Auth + Realtime + Storage)
- **Document storage:** PostgreSQL JSONB (not MongoDB)
- **ORM:** Prisma for complex queries (Trial), Supabase client for simple CRUD
- **Caching:** Redis only when PostgreSQL performance is measured as insufficient
- **Rule of thumb:** PostgreSQL handles 95% of data needs.

---

### 6.4 Choosing an Authentication Strategy

```text
Does the project need user authentication?
│
├─ NO → Skip auth entirely.
│
└─ YES → Is the project using Supabase?
          │
          ├─ YES → Supabase Auth ✅
          │
          └─ NO → Is the project a Next.js app?
                   │
                   ├─ YES → Auth.js (NextAuth v5) 🔬
                   │
                   └─ NO → Is it an Express/NestJS API?
                            │
                            ├─ Simple needs → Auth.js or custom JWT with Zod
                            │
                            └─ Enterprise needs (SAML, SSO) → Keycloak 🔍
```

**Summary:**
- **Default (Supabase):** Supabase Auth — RLS integration is the most secure combination
- **Default (non-Supabase):** Auth.js
- **Enterprise:** Keycloak — only for SAML/SSO
- **Avoid:** Passport.js (Hold), Lucia Auth (deprecated)

---

### 6.5 Choosing a State Management Approach

```text
What kind of state are you managing?
│
├─ SERVER STATE (data from APIs, database)
│   │
│   ├─ In Server Components → Fetch directly (no library needed) ✅
│   │
│   └─ In Client Components → TanStack Query ✅
│
├─ LOCAL CLIENT STATE (form inputs, toggles, UI state)
│   │
│   ├─ Single component → useState / useReducer ✅
│   │
│   └─ Small component tree → Props or composition
│
├─ SHARED CLIENT STATE (theme, locale, auth status)
│   │
│   └─ Low-frequency updates → React Context ✅
│
└─ COMPLEX GLOBAL CLIENT STATE (multi-step wizard, canvas, filters)
    │
    └─ Context is insufficient → Zustand 🔬
```

**Summary:**
- **Server data in Server Components:** Fetch directly
- **Server data in Client Components:** TanStack Query
- **Local state:** React hooks
- **Shared state:** React Context
- **Complex global state:** Zustand (Trial)
- **Rule of thumb:** The best state management is the least state management.

---

### 6.6 Choosing a Testing Strategy

```text
What are you testing?
│
├─ PURE FUNCTIONS → Vitest ✅
│
├─ REACT COMPONENTS → Vitest + Testing Library ✅
│
├─ API ROUTES → Vitest + Supertest ✅
│
├─ CRITICAL USER FLOWS → Playwright ✅
│
├─ VISUAL CONSISTENCY → Storybook 🔬 + Playwright screenshots
│
└─ PERFORMANCE UNDER LOAD → k6 🔍
```

**Summary:**
- Follow the test pyramid — many unit tests, fewer integration tests, even fewer E2E tests.
- → See [06-testing-strategy.md] for the full strategy.

---

### 6.7 Choosing a Deployment Platform

```text
What are you deploying?
│
├─ Next.js application → Vercel ✅
│
├─ Static site (Astro, Vite SPA)
│   ├─ Vercel ✅ (default)
│   └─ Cloudflare Pages 🔬 (edge performance priority)
│
├─ Standalone backend (Express, NestJS, FastAPI)
│   ├─ Railway 🔬
│   └─ Render 🔬
│
├─ Database → Supabase Cloud ✅
│
└─ Scheduled jobs / background workers
    ├─ GitHub Actions (simple)
    └─ Railway / Render (persistent)
```

**Summary:**
- **Next.js → Vercel**, **Static → Vercel or CF Pages**, **Backends → Railway or Render**
- **Rule of thumb:** Use PaaS. Avoid managing servers until PaaS limitations are measured.

---

### 6.8 Choosing a Payment Integration

```text
Does the project accept payments?
│
├─ NO → Skip.
│
└─ YES → What type?
          │
          ├─ Standard (cards, MB WAY, subscriptions) → Stripe ✅
          │
          ├─ Portuguese market only (Multibanco, MB WAY)
          │   ├─ Stripe covers this ✅
          │   └─ Client requires local provider → Easypay 🔍 or ifthenpay 🔍
          │
          └─ Digital products across EU (VAT handling)
              ├─ Can handle VAT → Stripe ✅
              └─ Want VAT handled automatically → LemonSqueezy 🔍
```

**Summary:**
- **Default:** Stripe — covers cards, MB WAY, Multibanco, subscriptions
- **Rule of thumb:** Start with Stripe. Switch only for specific requirements it cannot meet.

---

### 6.9 Choosing an Email Strategy

```text
Does the project send emails?
│
├─ NO → Skip.
│
└─ YES → What kind?
          │
          ├─ Transactional (welcome, reset, confirmation)
          │   ├─ Modern stack → Resend + react-email 🔬
          │   └─ SMTP-based → Nodemailer ✅
          │
          └─ Marketing (campaigns, newsletters)
              └─ Not covered by current radar. Evaluate using Section 1.
```

**Summary:**
- **Transactional (modern):** Resend + react-email
- **Transactional (SMTP):** Nodemailer
- **Rule of thumb:** Resend for new projects, Nodemailer when SMTP is already available.

---

### 6.10 Choosing a Monitoring Strategy

```text
What do you need to monitor?
│
├─ ERRORS → Sentry ✅
│
├─ UPTIME → UptimeRobot ✅
│
├─ LOGS
│   ├─ Emit → Pino ✅
│   └─ Aggregate → Axiom 🔬
│
├─ SEO → Google Search Console ✅ + Lighthouse ✅
│
├─ USER BEHAVIOR
│   ├─ Privacy-first → Vercel Analytics 🔬 or Plausible 🔍
│   ├─ Full analytics → GA4 🔬 (with RGPD consent)
│   └─ Session replay → LogRocket 🔬
│
└─ INFRASTRUCTURE → Grafana + Prometheus 🔍
```

**Summary — minimum viable monitoring for any production app:**
1. **Sentry** — know when things break
2. **UptimeRobot** — know when things are down
3. **Pino** — have logs when you need to debug
4. **Search Console** — know how Google sees the site (public sites only)

### 6.11 Choosing an i18n Strategy
```text
Does the project need multiple languages?
│
├─ NO → Do not add i18n infrastructure. Hardcoded strings are fine.
│        Add i18n later if the need emerges — but keep strings in
│        components (not spread across utility files) to ease extraction.
│
└─ YES → What framework are you using?
          │
          ├─ Next.js → next-intl ✅
          │   [Server Component support, type-safe, locale routing]
          │
          ├─ Vite + React → react-i18next 🔬
          │   [Largest ecosystem, plugin support, lazy loading]
          │
          └─ Backend (Express/NestJS) → i18next 🔬
              [Framework-agnostic, for localized emails/PDFs/messages]
```

**Summary:**
- **Next.js:** next-intl — native App Router integration, type-safe
- **Vite + React:** react-i18next — established, flexible, large ecosystem
- **Backend:** i18next — framework-agnostic core
- **Rule of thumb:** If you know the project will need i18n, set it up from day one. Retrofitting
  translations into an existing codebase is 5–10x more expensive than starting with the structure.

---

### 6.12 Choosing an LLM Provider

```text
Can the data leave your perimeter (no strict on-prem/RGPD block)?
│
├─ NO → Self-hosted open-weight model
│        │
│        ├─ Development / single machine → Ollama 🔬 (Qwen3, Gemma, Phi-4)
│        │
│        └─ Production / multi-user → vLLM 🔍 (behind reverse proxy + auth)
│
└─ YES → What is the dominant constraint?
          │
          ├─ Hardest reasoning / multi-file coding / agents → Claude ✅
          │   [Default for reasoning and generation quality]
          │
          ├─ Cost-sensitive / high-volume / public traffic → Gemini Flash ✅
          │   [Lowest cost + highest speed — MUST use paid tier]
          │
          ├─ Embeddings or real-time voice → OpenAI ✅
          │   [text-embedding-3; Realtime API for voice]
          │
          └─ Need provider flexibility / fallback → front everything with
              an AI Gateway 🔬 [Swap providers without code changes]
```

**Summary:**
- **Default (quality):** Claude — reasoning, coding, agents, document generation
- **Default (cost/volume):** Gemini Flash — paid tier only (free tier trains on data + is EU-restricted)
- **Embeddings & voice:** OpenAI — and keep the embedding model identical at index and query time
- **RGPD-strict:** local (Ollama → vLLM); cloud providers MUST run on paid tiers → See [07-security-standards.md]
- **Rule of thumb:** Pick the cheapest model that passes your evals for the task — not the strongest by
  default. Front providers with an AI Gateway so the choice stays reversible.

---

### 6.13 Choosing a RAG Storage Strategy

```text
Do you need retrieval over private/domain data (RAG)?
│
├─ NO → No vector store needed. Stop here.
│
└─ YES → Are you already on PostgreSQL / Supabase?
          │
          ├─ YES → pgvector ✅
          │        [Default — embeddings beside relational data, metadata
          │         filtering, RLS, hybrid search with FTS]
          │        │
          │        └─ Hitting limits? Measure first:
          │            │
          │            ├─ Filtering/scale insufficient (proven by metrics)
          │            │   → add Qdrant 🔍 for the vector workload
          │            │
          │            └─ Relationship-heavy retrieval needed
          │                → assess Graph RAG (Neo4j) 🔍
          │
          └─ NO → Is the corpus large or the workload pure-vector at scale?
                   │
                   ├─ YES → Qdrant 🔍 (self-host) or Pinecone 🔍 (managed)
                   │
                   └─ NO → Still pgvector ✅ (add Supabase/PostgreSQL — it
                            earns its place as the relational store too)
```

**Summary:**
- **Default:** pgvector (Supabase) — one datastore, transactional consistency, RLS, hybrid search
- **Scale up only on evidence:** Qdrant when pgvector's filtering/scale is measured to be insufficient
- **Graph RAG (Neo4j):** only when flat vector retrieval is proven inadequate for relationship-heavy data
- **Prototyping:** Chroma is fine to start, but migrate to pgvector/Qdrant for anything real
- **Rule of thumb:** Start with pgvector. A dedicated vector DB is a second system to operate — add it
  only when metrics, not intuition, show pgvector falling short. → See [04-database-standards.md]

---

## 7. Radar Governance

This is the most perishable document in the engineering standards collection. Technologies
evolve, new tools emerge, projects reveal unexpected strengths or weaknesses in current choices,
and the team's competence grows. A radar that is not actively maintained becomes misleading —
worse than having no radar at all.

This section defines when, how, and by whom the radar is updated.

---

### 7.1 Review Cadence

| Review Type        | Frequency     | Scope                                           | Trigger                                    |
|--------------------|---------------|-------------------------------------------------|--------------------------------------------|
| **Quarterly Review** | Every 3 months | Full radar scan — review all categories for staleness, validate that classifications still hold | Calendar-based (schedule it) |
| **Post-Project Review** | After each project delivery | Technologies used in the project — was the classification accurate? Lessons learned? | Project completion |
| **Trigger-Based Review** | As needed | Specific technology — when an event forces reassessment | See trigger list below |

#### Quarterly Review Process

1. **Scan the radar** — for each technology, ask: "Is this classification still accurate?"
2. **Check for movements:**
   - Trial technologies: has enough evidence accumulated to promote to Adopt or demote to Hold?
   - Assess technologies: is it time to start a Trial, or has interest faded?
   - Hold technologies: has something changed that warrants reassessment?
   - Adopt technologies: is this still the best choice? Has a superior alternative emerged?
3. **Check for gaps** — are there technologies the team is using or evaluating that are not yet
   on the radar? Add them.
4. **Update the changelog** (Section 7.4) with all changes and reasoning.

#### Post-Project Review Questions

- Which radar technologies did we use? Were the classifications accurate?
- Did we discover strengths or weaknesses not captured in the technology profiles?
- Did we adopt any technology not on the radar? If so, add it and classify it.
- Did any Trial technology prove itself (→ promote to Adopt) or disappoint (→ demote to Hold)?
- Were the Stack Baselines (Section 5) appropriate, or did we need to deviate? Why?

---

### 7.2 Triggers for Immediate Review

Do not wait for the quarterly review when any of these events occur:

| Trigger                                   | Action                                                     |
|-------------------------------------------|------------------------------------------------------------|
| **Security vulnerability** in an Adopt/Trial technology | Assess severity. If critical and unpatched, consider immediate move to Hold. |
| **Project/library deprecated** by maintainer | Move to Hold immediately. Document and recommend alternatives. |
| **Major version release** with breaking changes | Review the technology profile. Update baselines and migration notes. |
| **Team composition change** | Review Team Competence criterion for Trial and Assess technologies. |
| **New project type** not covered by baselines | Create a new Stack Baseline or extend an existing one. |
| **Production incident** caused by a technology choice | Post-mortem. Update profile with lessons learned. Consider reclassification. |
| **Significant ecosystem shift** | Review affected categories (e.g., RSC changing state management landscape). |

---

### 7.3 How to Propose a Change

Every radar change follows a lightweight but documented process:

#### Adding a New Technology

1. Evaluate using the framework in [Section 1](#1-technology-evaluation-framework)
2. Classify into the appropriate category (almost always starts as 🔍 Assess)
3. Write the radar table entry (Section 3) and technology profile (Section 4)
4. If classified as Trial or higher, document the decision in an ADR
   (→ See [01-core-principles.md, Section 9])
5. Add to the changelog (Section 7.4)

#### Moving a Technology Between Categories

1. State the current category and proposed new category
2. Provide evidence for the change (project experience, ecosystem event, security issue)
3. Update the radar table, technology profile, and any affected Stack Baselines or Decision Guides
4. For Adopt → Hold moves, **MUST** include a migration recommendation
5. For any movement, **MUST** add to the changelog

#### Removing a Technology from the Radar

- Only for technologies no longer relevant enough to track
- Move to Hold first, then remove in the next quarterly review if still irrelevant
- **MUST** add to the changelog with removal reasoning

---

### 7.4 Changelog

Every radar change is recorded here in reverse chronological order.

| Date       | Technology         | Change               | Reasoning                                         |
|------------|--------------------|----------------------|---------------------------------------------------|
| 2026-06-03 | AI Engineering cluster | Added: §3.24–3.31 / §4.24–4.30 | New cluster (providers, local inference, SDKs/agents, ingestion, RAG storage, observability/eval, protocols, channels) reflecting acquired LLM/RAG/agent competencies. Supersedes the old single "AI & Automation" entry. |
| 2026-06-03 | Anthropic API (Claude) | Moved: Trial → Adopt | Real, daily usage (Claude / Claude Code); default reasoning and agent model. |
| 2026-06-03 | OpenAI API | Moved: Trial → Adopt | Default for embeddings and real-time voice; broadest ecosystem; real usage. |
| 2026-06-03 | Google Gemini API | Moved: Trial → Adopt | Cost-sensitive/high-volume default. Conditional on paid tier — free tier trains on data and is EU-restricted. |
| 2026-06-03 | pgvector (Supabase) | Moved: → Adopt | Extension of the already-adopted PostgreSQL/Supabase stack; default RAG storage. |
| 2026-06-03 | Baileys (unofficial WhatsApp) | Added: Hold | Violates WhatsApp ToS; ban risk on the sending number. Personal/internal only — never client deliverables. |
| 2026-06-03 | AI & Automation (old §3.21/§4.21) | Removed | Superseded by the AI Engineering cluster; items migrated. |
| 2026-03-25 | Turbopack          | Moved: Assess → Adopt | Stable and default bundler in Next.js 16 (Oct 2025) for both dev and production. No longer opt-in. |
| 2026-03-25 | Prisma             | Moved: Trial → Adopt | v7 removed Rust engine, 100% TypeScript, 3-4x faster, major DX improvements. Production-proven. |
| 2026-03-25 | Drizzle ORM        | Moved: Assess → Trial | v1 beta, massive adoption growth, T3 Stack default, built-in Zod integration. Ready for real project evaluation. |
| 2026-03-25 | Biome              | Moved: Assess → Trial | v2.3 with React/Next.js domains, 462 lint rules, type-aware linting, plugin support via GritQL. |
| 2026-03-25 | Tailwind CSS       | Updated: profile     | v4 rewrite: CSS-native config via @theme (replaces tailwind.config.js), Oxide engine (Rust), 5-10x faster. |
| 2026-03-25 | ESLint             | Updated: profile     | v10 released (Feb 2026): .eslintrc completely removed, flat config only, defineConfig() helper. |
| 2026-03-25 | Next.js            | Updated: profile     | v16.2.1 current: Turbopack default, React Compiler stable, "use cache" directive, async request APIs. |
| 2026-03-25 | Webpack            | Updated: profile     | Reinforced Hold — Turbopack is now default in Next.js 16, Webpack available only via --webpack flag. |

---

### 7.5 Radar Health Metrics

To ensure the radar remains useful and active, track these indicators:

| Metric                               | Healthy Range          | Warning Sign                            |
|--------------------------------------|------------------------|-----------------------------------------|
| **Last full review date**            | Within last 3 months   | > 6 months since last review            |
| **Trial technologies without update**| < 6 months in Trial    | > 12 months without promotion or demotion |
| **Assess technologies without update**| < 12 months in Assess | > 18 months without movement             |
| **Changelog entries per quarter**    | ≥ 1                    | 0 entries for 2+ quarters (radar is stale) |
| **Technologies used but not on radar**| 0                     | Any technology in active use not tracked |

#### Rules

- **MUST NOT** allow Trial technologies to remain in Trial indefinitely — promote to Adopt or
  demote to Hold within 2–3 project cycles (as defined in [Section 2.1](#21-category-definitions))
- **SHOULD NOT** allow Assess technologies to remain in Assess for more than 18 months — either
  start a Trial or acknowledge that interest has faded and remove or move to Hold
- **MUST** conduct at least one full radar review per year — if quarterly reviews are missed, an
  annual review is the absolute minimum
- **SHOULD** treat a stale radar as a problem to fix, not a document to ignore — an outdated radar
  actively misleads decisions

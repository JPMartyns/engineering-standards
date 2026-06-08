# 🖥️ Frontend Standards

> **Scope:** Practical guide for building, styling, and shipping frontend
> interfaces with React and Next.js across all projects covered by these
> engineering standards.
>
> **Purpose:** The reference that answers "how should this component be
> structured, how should this page be styled, and how should this state be
> managed?" — ensuring every frontend is consistent, accessible, performant,
> and maintainable, regardless of the project type.
>
> **Keywords:**
> - **MUST** = required (PR should be blocked if violated)
> - **SHOULD** = strongly recommended (requires justification to skip)
> - **MAY** = optional (case-by-case)

---

## 0. How to Use This Document

- This document defines **how to build frontend interfaces** — project
  structure, component patterns, styling, state management, data fetching,
  forms, error handling, accessibility, performance, SEO, and testing.
- It does **not** define which frameworks or libraries to use (that lives in
  → See [02-technology-radar.md]) or how to secure the application against attacks
  (that lives in → See [07-security-standards.md]). It references both heavily.
- Code examples use **TypeScript** with **React 19.2**, **Next.js 16 App
  Router** (default full-stack), and **Tailwind CSS v4** — reflecting the
  Adopt choices in → See [02-technology-radar.md, Sections 4.2–4.6].
- The layering model assumed throughout is:
  `Page / Layout → Component → Hook / Service → API`
  (→ See [01-core-principles.md, Section 6]).
- The API layer provides responses in **camelCase JSON** with a standard
  envelope `{ ok, data, error, requestId, meta }`
  (→ See [03-api-design.md, Section 4]). This document defines how the
  frontend consumes that contract — mapping errors to UI, implementing
  pagination, and handling loading states.
- When a rule here overlaps with security, the security document takes
  precedence — this document defers to → See [07-security-standards.md] on all
  security-related decisions. Client-side validation is UX, not security
  (→ See [07-security-standards.md, Section 3]).
- When a rule here overlaps with testing strategy, this document covers
  frontend-specific testing patterns (component tests, hook tests). The
  complete testing strategy (pyramid, coverage, CI gates) lives in
  → See [06-testing-strategy.md].

### Boundary Definitions

Understanding where this document ends and others begin prevents duplication
and contradictions:

| Question | This Document (05) | Other Document |
|---|---|---|
| **Which** styling framework to use? | — | → See [02-technology-radar.md] says "Tailwind CSS (Adopt)" |
| **How** to use Tailwind CSS with patterns and conventions? | ✅ Section 4 | — |
| **Which** state management library to use? | — | → See [02-technology-radar.md] defines the hierarchy |
| **How** to implement state management patterns? | ✅ Section 5 | — |
| **What** does the API response format look like? | — | → See [03-api-design.md, Section 4] defines the contract |
| **How** does the frontend consume API responses? | ✅ Sections 6, 8 | — |
| **What** security headers to configure? | — | → See [07-security-standards.md, Section 9] |
| **How** to implement cookie consent UI? | ✅ Section 12 (awareness) | → See [07-security-standards.md, Section 14] defines RGPD rules |
| **What** testing strategy and coverage targets? | — | → See [06-testing-strategy.md] |
| **How** to write component and hook tests? | ✅ Section 15 | — |
| **How** to handle database schema and queries? | — | → See [04-database-standards.md] |
| **How** to consume Supabase Realtime in the frontend? | ✅ Section 14 | → See [04-database-standards.md, Section 7] defines RLS policies |

### Technology Versions

This document is written for and tested with the following versions. When
upgrading, review the relevant sections for breaking changes:

| Technology | Version | Release Date |
|---|---|---|
| Next.js | 16.2 | March 2026 |
| React | 19.2 | October 2025 |
| Tailwind CSS | 4.x | January 2025 |
| Zod | 4.x | May 2025 |
| shadcn/ui CLI | v4 | March 2026 |
| TanStack Query | 5.x | — |
| react-hook-form | 7.x | — |
| next-themes | 0.4.x | — |
| next-intl | 4.x | — |
| Vitest | 3.x | — |
| Playwright | latest | — |

### Document Relationships

```text
05-frontend-standards.md (this document)
 ├── Derives from    → 01-core-principles.md (SRP, separation of concerns, naming, clean code)
 ├── Derives from    → 02-technology-radar.md (React, Next.js, Tailwind, shadcn/ui, state mgmt choices)
 ├── Complements     → 07-security-standards.md (CSP, CORS, input validation boundary, RGPD UI)
 ├── Complements     → 03-api-design.md (API consumption, error mapping, pagination patterns)
 ├── Complements     → 04-database-standards.md (Supabase Realtime, RLS + client, casing bridge)
 ├── Referenced by   → 06-testing-strategy.md (frontend testing patterns feed into test pyramid)
 ├── Referenced by   → 09-devops-cicd.md (build optimization, bundle analysis in CI)
 └── Referenced by   → 08-observability.md (client-side error tracking, performance monitoring)
```

### AI Agent Instructions

This document is designed to be consumed by AI coding agents (e.g., Claude
Code). When interpreting this document:

- **MUST**, **SHOULD**, and **MAY** are RFC 2119 keywords — treat MUST as non-negotiable constraints, SHOULD as strong defaults that require explicit justification to override, and MAY as contextual options.
- Cross-references (→ See [XX-document.md]) point to authoritative definitions — always defer to the referenced document for the full rule.
- When this document conflicts with [07-security-standards.md], the security document takes precedence.
- BAD/GOOD code examples are pattern-matching references — apply the principle behind the example, not just the literal code.
- Anti-pattern tables describe common mistakes — use them as negative examples when reviewing or generating code.
- Every React component generated or reviewed MUST follow the component patterns, accessibility rules, and performance guidelines defined here.
- **Version-critical rules for code generation:**
  - React 19: DO NOT use `forwardRef` (refs are regular props), DO NOT use `defaultProps` (use ES default parameters), DO NOT use `React.FC` (unnecessary), USE `<form action={...}>` for form submissions where applicable.
  - Tailwind CSS v4: DO NOT generate `tailwind.config.js` (v4 uses CSS-native `@theme`), DO NOT use `@apply` unless extracting a component class, DO NOT reference `tailwind.config.ts` — configuration lives in CSS via `@theme` blocks.
  - Next.js 16: PREFER Server Components by default, DO NOT add `'use client'` unless the component uses state, effects, or browser APIs. `params` and `searchParams` in page/layout components are async — always `await` them.
- If generating code requires violating a MUST rule, the AI **MUST stop** and ask the human for permission before proceeding — never silently override a standard.
- **MUST NOT** over-engineer — always prefer the simplest solution that meets the stated requirements. Do not add abstractions, patterns, or infrastructure beyond what was explicitly requested (→ See [01-core-principles.md, §12]).

---

## 1. Frontend Philosophy

The frontend is the part of the application that users actually see, touch, and
judge. A backend can be perfectly designed, an API flawlessly documented, a
database impeccably normalized — but if the interface is slow, confusing, or
inaccessible, none of that matters to the person using it. Every decision in
this document serves one goal: building interfaces that are fast, inclusive,
and maintainable.

These principles guide every decision in this document.

### 1.1 React and Next.js First

React is the UI layer; Next.js is the application framework. Together, they
are the default choice for any web application that needs interactivity,
server-side rendering, or both. This is not a technology preference — it is
a deliberate baseline that enables team consistency, shared component
libraries, and predictable project structure.

- **MUST** use Next.js App Router for all new web applications — the Pages
  Router is legacy and should not be used in new projects
- **MUST** use React Server Components by default — add `'use client'` only
  when the component requires browser APIs, event handlers, or client-side
  hooks (→ See [Section 3.1](#31-server-vs-client-components--decision-guide))
- **MAY** use Vite + React for lightweight SPAs, internal tools, or prototypes
  where SSR is not needed (→ See [02-technology-radar.md, Section 4.2])
- **MAY** use Astro for content-heavy static sites where Next.js would be
  overkill (→ See [02-technology-radar.md, Section 4.2])

> **Why:** A consistent framework baseline eliminates the "which tool?" question
> on every new project. Developers move between projects without relearning
> fundamentals. Shared components, patterns, and knowledge compound over time
> instead of fragmenting across different frameworks.

### 1.2 Component-Driven Development

The UI is built from small, focused, composable components — not monolithic
pages. Each component has a single responsibility, explicit inputs (props), and
predictable output. Components are the unit of reuse, testing, and design.

- **MUST** keep components focused — a component does one thing well
  (→ See [01-core-principles.md, Section 4.1 — SRP])
- **MUST** prefer composition over configuration — build complex UIs by
  combining simple components, not by adding flags and conditionals to a
  single component
- **SHOULD** design components from the consumer's perspective — what props
  does the parent need to pass? — not from the implementation outward
- **SHOULD** co-locate component files (component, styles, tests, types) in
  the same directory rather than grouping by file type

> **Why:** Small, composable components are easier to test, easier to review,
> easier to replace, and easier for new developers to understand. A 50-line
> component that does one thing is worth more than a 500-line component that
> does everything.

### 1.3 Mobile-First, Always

Every interface starts as a mobile layout. Responsive modifiers add complexity
for larger screens — never the other way around. This is not about "supporting
mobile" — it is about designing for the most constrained environment first and
progressively enhancing from there.

- **MUST** write base Tailwind styles for the smallest screen and use
  responsive modifiers (`sm:`, `md:`, `lg:`) to adapt for larger viewports
- **MUST** ensure all interactive elements have a comfortable touch target of
  **44×44px** (recommended). WCAG 2.2 AA requires a minimum of **24×24px**
  (→ See [Section 9.1](#91-target-wcag-22-level-aa))
- **MUST** include the viewport meta tag:
  `<meta name="viewport" content="width=device-width, initial-scale=1" />`
- **SHOULD** test on real devices, not only browser DevTools — emulation
  misses touch behavior, performance, and rendering differences
- **SHOULD** use Tailwind's standard breakpoints unless the project has a
  justified reason to deviate:
  `sm: 640px` | `md: 768px` | `lg: 1024px` | `xl: 1280px` | `2xl: 1536px`

> **Why:** More than half of global web traffic comes from mobile devices.
> Designing desktop-first and "making it responsive" leads to cramped mobile
> layouts, hidden features, and unreadable text. Designing mobile-first
> forces clarity: if the feature works on a 375px screen, it works everywhere.

### 1.4 Accessibility Is a Requirement, Not a Feature

Accessibility (a11y) is not a nice-to-have checkbox, a last-sprint polish
task, or something "we will add later." It is a fundamental quality attribute
that is built into every component from the start, just like type safety or
error handling.

- **MUST** target **WCAG 2.2 Level AA** compliance as the baseline for all
  projects (→ See [Section 9.1](#91-target-wcag-22-level-aa))
- **MUST** use semantic HTML elements before reaching for ARIA attributes —
  a `<button>` is always better than a `<div role="button" tabIndex={0}>`
- **MUST** ensure all interactive elements are keyboard-accessible
- **SHOULD** use shadcn/ui and Radix UI primitives as the component foundation
  — they are built with accessibility by default (keyboard navigation, focus
  management, ARIA attributes)
- **SHOULD** test accessibility during development, not as a separate phase
  (→ See [Section 9.8](#98-testing-accessibility))

> **Why:** Accessibility is a legal requirement in many jurisdictions (EAA in
> the EU, ADA in the US). Beyond compliance, accessible interfaces work better
> for everyone — keyboard users, screen reader users, users with temporary
> injuries, users in bright sunlight, and power users who prefer keyboard
> shortcuts. Retrofitting accessibility is expensive; building it in is almost
> free.

### 1.5 Progressive Enhancement

The application should deliver a functional experience with the minimum amount
of client-side JavaScript. Server Components render HTML on the server. Client
Components add interactivity where needed. JavaScript enhances the experience
— it should not be a prerequisite for basic functionality.

- **MUST** render meaningful content from the server — the initial HTML should
  contain real content, not an empty `<div id="root">` waiting for JavaScript
  to hydrate
- **MUST** handle loading, error, and empty states explicitly — every
  asynchronous operation has three possible outcomes, and the UI must account
  for all three (→ See [Section 8](#8-error-handling-in-ui))
- **SHOULD** ensure core content is accessible without JavaScript — forms
  should work with progressive enhancement where possible (Server Actions)
- **SHOULD** use the `<noscript>` tag to inform users when JavaScript is
  required for interactive features

> **Why:** Server-rendered content is faster (no JS download → parse → execute
> before first paint), more accessible (screen readers and crawlers see real
> content), better for SEO and AI discoverability (→ See [Section 12](#12-seo--ai-discoverability-geo)),
> and more resilient (the page works even if a JS bundle fails to load).

### 1.6 UI Is Not Business Logic

Components orchestrate the user interface — they display data, capture input,
and trigger actions. They do not calculate discounts, validate business rules,
or decide authorization policy. Business logic belongs in services and hooks;
the UI layer consumes their output.

- **MUST** keep components free of business rules — a component should not
  contain logic that would need to change if the business rules change but
  the UI stays the same
  (→ See [01-core-principles.md, Section 6 — Separation of Concerns])
- **MUST** extract data transformation, validation logic, and orchestration
  into dedicated hooks or service functions
- **MUST NOT** import repository or database modules directly in components
  — the layering boundary is `Component → Service → Repository`
- **SHOULD** keep the `'use client'` boundary as thin as possible — push
  logic down into hooks and services that can be tested independently

> **Why:** When business logic lives in components, it cannot be reused across
> different UIs (web, mobile, email), cannot be tested without rendering a
> component, and creates tight coupling between presentation and domain.
> Separating concerns makes both the UI and the logic independently
> changeable and testable.

---

## 2. Project Structure

A well-organized project structure is a map — a developer opening the codebase
for the first time should understand where things live and where to add new code
without reading a manual. The structure should reflect the architecture: routing
lives in `app/`, domain logic lives in feature modules, shared primitives live
in `components/ui/`, and the dependency direction is always top-to-bottom.

> The architectural foundation for this section — layering, dependency direction,
> and modular design — is defined in → See [01-core-principles.md, Section 6].
> This section applies those principles specifically to React/Next.js projects.

---

### 2.1 Next.js App Router Conventions

The App Router uses a file-system-based routing model where folders inside `app/`
map directly to URL segments. Special filenames have specific roles that Next.js
recognizes automatically.

#### Special Files

| File | Purpose | Rendering |
|---|---|---|
| `page.tsx` | The UI for a route segment — required to make a route publicly accessible | Server Component (default) |
| `layout.tsx` | Shared UI that wraps child routes — persists across navigations, does not rerender | Server Component (default) |
| `loading.tsx` | Instant loading UI shown while the page is streaming (wraps page in `<Suspense>`) | Server Component |
| `error.tsx` | Error boundary for the segment and its children — catches runtime errors | **Client Component** (required) |
| `not-found.tsx` | UI shown when `notFound()` is called within the segment | Server Component |
| `template.tsx` | Like layout, but creates a new instance on every navigation (remounts) — rare | Server Component |
| `default.tsx` | Fallback UI for parallel routes when no matching segment exists | Server Component |
| `route.ts` | API route handler (GET, POST, etc.) — cannot coexist with `page.tsx` in the same folder | Server-only |
| `proxy.ts` | Request interception at the network boundary (replaces `middleware.ts` in Next.js 16) | **Root-level only**, Node.js runtime |

- **MUST** use `page.tsx` to define routes — a folder without a `page.tsx` is
  not a route (it can still contain components and logic)
- **MUST** place `proxy.ts` at the project root (next to `app/`) — not inside
  `app/`. This file replaces the deprecated `middleware.ts` in Next.js 16
- **MUST** mark `error.tsx` files with `'use client'` — React error boundaries
  require client-side rendering
- **SHOULD** provide `loading.tsx` for every route that fetches data — instant
  loading states are critical for perceived performance
- **SHOULD** provide `not-found.tsx` at the root `app/` level and for key
  segments where a custom 404 experience matters

#### Route Groups

Route groups use parenthesized folder names `(group-name)` to organize routes
without affecting the URL structure. They are essential for:

- Applying different layouts to different sections (marketing vs dashboard)
- Grouping related routes logically (auth pages, settings pages)
- Isolating loading and error boundaries per section

```text
app/
  (marketing)/          ← URL: / , /about, /pricing (no "marketing" in URL)
    layout.tsx          ← Marketing layout (public header, footer)
    page.tsx            ← Homepage
    about/
      page.tsx
    pricing/
      page.tsx
  (dashboard)/          ← URL: /dashboard/*
    layout.tsx          ← Dashboard layout (sidebar, auth check)
    dashboard/          ← This folder creates the /dashboard segment
      page.tsx
      settings/
        page.tsx
  (auth)/               ← URL: /login, /register
    layout.tsx          ← Auth layout (centered card, no navigation)
    login/
      page.tsx
    register/
      page.tsx
```

- **SHOULD** use route groups to separate public pages from authenticated areas
- **SHOULD** use route groups when different sections need different layouts
- **MUST NOT** create route groups for organizational convenience alone if a
  simple folder structure is sufficient — groups add indirection

---

### 2.2 Feature-Based Module Organization

As the project grows beyond a handful of routes, code organization shifts from
type-based grouping (all components together, all services together) to
feature-based modules where each domain concept is self-contained.

> This follows the guidance in → See [01-core-principles.md, Section 6.3] —
> prefer feature-based modules over type-based modules for cohesion.

```text
# FEATURE-BASED (recommended for medium+ projects)
src/
  features/
    users/
      components/
        user-card.tsx
        user-form.tsx
      services/
        user-service.ts
      schemas/
        user-schema.ts
      hooks/
        use-user-query.ts
      index.ts              ← Public API of this feature module
    invoices/
      components/
      services/
      schemas/
      hooks/
      index.ts
  components/
    ui/                     ← shadcn/ui components (shared primitives)
    layout/                 ← Layout-level components (Header, Sidebar, Footer)
  lib/                      ← Shared utilities, pure functions
  hooks/                    ← Shared hooks (not feature-specific)
```

- **MUST** use feature-based organization when the project has more than 10
  routes or multiple developers working simultaneously
- **MUST** expose each feature module through an `index.ts` that acts as its
  public API — other modules import from the index, never from internal files
- **MUST NOT** create cross-dependencies between feature modules — if two
  features need shared code, extract it to `shared/` or `lib/`
- **SHOULD** keep feature modules aligned with domain concepts (users,
  invoices, vehicles), not with UI pages — a feature may serve multiple pages

---

### 2.3 Component File Organization (Co-location)

Components and their related files live together. A component file should not
require searching across three different directories to find its types, tests,
and styles.

```text
# GOOD — co-located
src/
  features/users/components/
    user-card/
      user-card.tsx           ← Component
      user-card.test.tsx      ← Tests
      user-card.module.css    ← Styles (if CSS Module needed)
      index.ts                ← Re-export: export { UserCard } from './user-card'
```

- **SHOULD** co-locate component tests, types, and styles in the same
  directory as the component
- **MUST** follow the naming conventions defined in
  → See [01-core-principles.md, Section 7]:
  - Folders and non-component files: `kebab-case`
  - Component files: `kebab-case` for the filename, `PascalCase` for the export
    (e.g., `user-card.tsx` exports `UserCard`)

---

### 2.4 Shared vs Feature-Scoped Code

Not everything belongs in a feature module. Some code is genuinely shared across
the entire application.

| Code | Location | Rationale |
|---|---|---|
| shadcn/ui components (`Button`, `Dialog`, `Input`) | `src/components/ui/` | UI primitives used everywhere |
| Layout components (`Header`, `Sidebar`, `Footer`) | `src/components/layout/` | Application shell, not feature-specific |
| `cn()` utility, date formatters, currency formatters | `src/lib/` | Pure utility functions |
| Zod schemas for API envelope (`ApiResponse`) | `src/schemas/` | Shared contracts (→ See [03-api-design.md]) |
| Custom errors (`AppError`, `NotFoundError`) | `src/errors/` | Error hierarchy used across layers |
| `ThemeProvider`, `QueryProvider` | `src/providers/` | Application-level providers |
| `useMediaQuery`, `useDebounce` | `src/hooks/` | Generic hooks, not tied to a domain |
| `useUserProfile`, `useInvoiceList` | `src/features/*/hooks/` | Feature-specific hooks |

- **MUST** place truly shared code in `src/lib/`, `src/hooks/`, or
  `src/components/ui/` — not inside a feature module
- **MUST NOT** place feature-specific code in shared directories
- **SHOULD** apply the "Rule of Three" before moving code to shared: if only
  one feature uses it, keep it local. If three or more use it, extract.

---

### 2.5 Barrel Files — When and When Not

A barrel file (`index.ts`) re-exports selected items from a directory, providing
a clean public API.

- **MUST** use a barrel file (`index.ts`) at the root of each feature module
  to define its public API
- **MUST NOT** create barrel files inside `app/` — Next.js special files are
  resolved by the framework
- **SHOULD NOT** create barrel files inside `components/ui/` — shadcn/ui
  components are imported directly, and a barrel would hurt tree-shaking
- **SHOULD NOT** create deep barrel file chains — this creates opaque
  dependency graphs and slows down build tools

---

### 2.6 Standard Directory Template

```text
project-root/
├── src/
│   ├── app/                      ← Next.js App Router (routing only)
│   │   ├── (marketing)/          ← Public pages route group
│   │   │   ├── layout.tsx
│   │   │   └── page.tsx
│   │   ├── (dashboard)/          ← Authenticated pages route group
│   │   │   ├── layout.tsx
│   │   │   └── dashboard/
│   │   │       ├── page.tsx
│   │   │       ├── loading.tsx
│   │   │       └── error.tsx
│   │   ├── (auth)/               ← Authentication pages route group
│   │   │   ├── layout.tsx
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   ├── api/                  ← API route handlers
│   │   ├── layout.tsx            ← Root layout (providers, fonts, metadata)
│   │   ├── error.tsx             ← Global error boundary
│   │   ├── not-found.tsx         ← Global 404 page
│   │   ├── sitemap.ts            ← Dynamic sitemap generation
│   │   └── robots.ts             ← Dynamic robots.txt generation
│   │
│   ├── components/
│   │   ├── ui/                   ← shadcn/ui components (managed by CLI)
│   │   └── layout/               ← Application shell (Header, Sidebar, Footer)
│   │
│   ├── features/                 ← Feature modules (domain-driven)
│   │   └── vehicles/
│   │       ├── components/
│   │       ├── hooks/
│   │       ├── services/
│   │       ├── schemas/
│   │       └── index.ts
│   │
│   ├── hooks/                    ← Shared custom hooks
│   ├── lib/                      ← Shared utilities, adapters, cn()
│   ├── schemas/                  ← Shared Zod schemas
│   ├── services/                 ← Shared services
│   ├── errors/                   ← Custom error classes
│   ├── types/                    ← Shared TypeScript types
│   ├── providers/                ← Application-level providers
│   └── config/                   ← App configuration, constants
│
├── tests/e2e/                    ← Playwright E2E tests
├── public/                       ← Static assets
├── proxy.ts                      ← Request interception (Next.js 16)
├── next.config.ts
├── .env.example
└── package.json
```

- **MUST** keep `app/` focused on routing — `page.tsx`, `layout.tsx`,
  `loading.tsx`, `error.tsx`, and route handlers only
- **MUST NOT** place reusable components or business logic inside `app/`
- **SHOULD** keep page files thin — they import and compose, rarely exceeding
  50 lines

---

## 3. Component Standards

Components are the building blocks of the frontend. Every piece of UI — from a
button to a full page layout — is a component with explicit inputs, predictable
output, and clear responsibility. This section defines how to design, structure,
and compose components.

> For the principles behind these standards (SRP, composition, naming):
> → See [01-core-principles.md, Sections 4, 5, 7].
> For the technology choices (React, shadcn/ui, Radix UI):
> → See [02-technology-radar.md, Sections 4.2, 4.4].

---

### 3.1 Server vs Client Components — Decision Guide

React Server Components (RSC) are the default in Next.js App Router. They
render on the server, ship zero JavaScript to the client, and can directly
access server-side resources. Use Client Components only when you need
browser APIs, event handlers, or React hooks that require client-side state.

```text
                    ┌─────────────────────┐
                    │ Does this component │
                    │ need any of these?  │
                    └──────────┬──────────┘
                               │
    ┌──────────────────────────┼──────────────────────────┐
    │                          │                          │
    ▼                          ▼                          ▼
useState/useEffect    onClick/onChange      Browser APIs
useReducer            onSubmit/onBlur       localStorage
useContext             form interactions     window/document
useRef (mutable)       hover/focus states    IntersectionObserver
                                             navigator
    │                          │                          │
    └──────────────────────────┼──────────────────────────┘
                               │
                    YES to any?│
                    ┌──────────┴──────────┐
                    │     'use client'    │
                    │  Client Component   │
                    └─────────────────────┘

                    NO to all?
                    ┌─────────────────────┐
                    │  Server Component   │
                    │     (default)       │
                    └─────────────────────┘
```

- **MUST** default to Server Components — only add `'use client'` when required
- **MUST** push the `'use client'` boundary as deep as possible — if a page
  has one interactive button, only the button component needs `'use client'`,
  not the entire page
- **MUST NOT** add `'use client'` to layout files unless absolutely necessary
  — layouts should be Server Components that persist across navigations
- **SHOULD** separate interactive parts into small Client Component leaves
  and keep the parent tree as Server Components

### 3.2 Component Anatomy

Every component follows a consistent structure:

```tsx
// 1. Imports
import { cn } from '@/lib/utils';
import type { Vehicle } from '@/features/vehicles/schemas/vehicle-schema';

// 2. Types (exported if needed externally)
interface VehicleCardProps {
  vehicle: Vehicle;
  className?: string;
}

// 3. Component (named export)
export function VehicleCard({ vehicle, className }: VehicleCardProps) {
  return (
    <article className={cn('rounded-lg border p-4', className)}>
      <h3 className="text-lg font-semibold">{vehicle.brand} {vehicle.model}</h3>
      <p className="text-muted-foreground">€{vehicle.price.toLocaleString()}</p>
    </article>
  );
}
```

- **MUST** use named exports for components (not default exports) — named
  exports enable consistent imports and better refactoring support
- **MUST** accept a `className` prop on reusable components and merge it
  with `cn()` — this allows consumers to customize styling
- **SHOULD** use `interface` for component props (not `type`) — interfaces
  are extensible and provide better error messages
- **MUST NOT** use `defaultProps` on function components — deprecated in
  React 19. Use JavaScript default parameters instead

### 3.3 Component Sizing — When to Split

A component is too large when it has multiple responsibilities or when reading
it requires scrolling to understand the full picture.

| Signal | Action |
|---|---|
| Component exceeds **150 lines** | Split into smaller components |
| More than **5 props** | Consider composition or compound pattern |
| Multiple `useState` calls for unrelated state | Extract into a custom hook |
| Rendering multiple distinct sections | Split each section into its own component |
| Conditional rendering with large branches | Extract branches into components |
| The component name needs "And" (e.g., `HeaderAndNavigation`) | Two components |

- **SHOULD** keep components under 150 lines — this is a guideline, not a
  hard limit, but consistently exceeding it signals poor separation
- **SHOULD** extract complex rendering logic into child components rather
  than adding `renderX()` methods inside a component

### 3.4 Composition Patterns

#### Children Pattern (Projection)

```tsx
function Card({ children, className }: { children: React.ReactNode; className?: string }) {
  return <div className={cn('rounded-lg border p-4', className)}>{children}</div>;
}

// Usage — consumer controls the content
<Card>
  <h3>Vehicle Details</h3>
  <p>Content here</p>
</Card>
```

#### Compound Components

```tsx
function Card({ children }: { children: React.ReactNode }) {
  return <div className="rounded-lg border">{children}</div>;
}

Card.Header = function CardHeader({ children }: { children: React.ReactNode }) {
  return <div className="border-b p-4">{children}</div>;
};

Card.Body = function CardBody({ children }: { children: React.ReactNode }) {
  return <div className="p-4">{children}</div>;
};

// Usage — structured but flexible
<Card>
  <Card.Header>Title</Card.Header>
  <Card.Body>Content</Card.Body>
</Card>
```

- **SHOULD** prefer the `children` pattern for simple content projection
- **MAY** use compound components when a component has distinct structural
  sections that should be explicitly composed by the consumer

### 3.5 Props Design

- **MUST** keep props minimal — pass only what the component needs to render,
  not entire objects when only 2 fields are used
- **MUST NOT** use boolean props that create ambiguous states — prefer union
  types or enums:

  ```tsx
  // BAD — boolean trap
  <Button primary outlined disabled />

  // GOOD — explicit variant
  <Button variant="primary" state="disabled" />
  ```

- **SHOULD** use `ComponentProps<'element'>` for components that extend native
  HTML elements — this automatically includes all native attributes

### 3.6 Naming Conventions

Naming follows → See [01-core-principles.md, Section 7], applied to React:

| Item | Convention | Example |
|---|---|---|
| Component file | `kebab-case.tsx` | `vehicle-card.tsx` |
| Component export | `PascalCase` | `VehicleCard` |
| Props interface | `PascalCase + Props` | `VehicleCardProps` |
| Hook | `camelCase` with `use` prefix | `useVehicleQuery` |
| Event handler prop | `on` + event | `onSubmit`, `onChange` |
| Event handler function | `handle` + event | `handleSubmit`, `handleChange` |
| Boolean prop | reads as question | `isLoading`, `hasError`, `canEdit` |
| Utility function | `camelCase` | `formatCurrency`, `mapApiError` |

### 3.7 AI Transparency & Disclosure (EU AI Act Art. 50)

When a UI exposes an AI system to users, the frontend is where transparency is actually delivered.
This section owns the *UI mechanics*; *whether* the obligation binds (deployer vs provider, which
features are in scope) is a legal / architecture decision → See [12-ai-engineering.md, §7.3].

**Rules:**

- A UI where a user **interacts with an AI** (chatbot, assistant, AI-driven support) **MUST**
  disclose this clearly at the start of the interaction — a user **MUST NOT** be left to believe
  they are talking to a human. (AI Act Art. 50(1))
- **AI-generated or AI-manipulated output** shown to users (text, image, audio, video) **MUST** be
  **labelled** as AI-generated where the obligation binds. (Art. 50(4))
- The disclosure and labels **MUST** be perceivable and accessible — visible by default, not hidden
  in a tooltip or buried in a policy page, and announced to assistive tech. → See §9 (a11y). Dark
  patterns that downplay AI use are non-compliant.
- Disclosure / label copy **SHOULD** be centralized (an i18n string + a reusable component) so it is
  consistent across surfaces and translatable. → See §13 (i18n).

**Why:**

Transparency under Art. 50 is both a legal duty and a trust contract, and it is delivered in the
frontend — a one-line intro in a chat panel, a persistent "AI assistant" label, a badge on
AI-generated content. The failure mode is an assistant that reads exactly like a human agent, or
AI-produced text / images shipped with no marker: non-compliant, and corrosive to trust the moment a
user discovers it.

**GOOD — disclosed assistant + labelled output:**

```tsx
function AssistantIntro() {
  // Disclosure up-front; copy from i18n (§13), accessible by default (§9)
  return <p role="note">{t("assistant.aiDisclosure")}</p>; // "You're chatting with an AI assistant."
}

function AiMessage({ text }: { text: string }) {
  return (
    <article aria-label={t("assistant.aiGeneratedLabel")}>
      <span className="badge">{t("assistant.aiGeneratedLabel")}</span> {/* "AI-generated" */}
      <Markdown>{text}</Markdown>
    </article>
  );
}
```

### 3.8 Anti-Patterns

| Anti-Pattern | Why It Is Wrong | Correct Alternative |
|---|---|---|
| `'use client'` on every component | Ships unnecessary JS, defeats SSR benefits | Default to Server Components (§3.1) |
| God components (500+ lines) | Impossible to test, understand, or reuse | Split by responsibility (§3.3) |
| Prop drilling through 4+ levels | Fragile, hard to maintain | Context, composition, or state management (§5) |
| `useEffect` for data fetching | Race conditions, no caching, no dedup | Server Components or TanStack Query (§6) |
| Business logic in components | Cannot reuse, cannot test without rendering | Extract to hooks or services (§1.6) |
| Default exports for components | Inconsistent imports, poor refactoring | Named exports always (§3.2) |
| `any` in props types | Loses type safety, hides bugs | Explicit `interface` with typed fields |
| `defaultProps` on function components | Deprecated in React 19 | Default values in destructuring |

---

## 4. Styling Standards

Styling is not decoration — it is communication. Every color choice, spacing
decision, and animation communicates hierarchy, state, and intent to the user.
The styling system must be consistent (design tokens), maintainable (utility-first),
and adaptive (responsive, dark mode, accessible contrast).

> Technology choices for styling are defined in → See [02-technology-radar.md, Section 4.3].
> This section defines **how** to use them with patterns, conventions, and rules.

---

### 4.1 Tailwind CSS Patterns & Conventions

Tailwind CSS v4 is a ground-up rewrite with a CSS-first configuration model.
The `tailwind.config.js` file is replaced by the `@theme` directive in CSS.
Design tokens are defined once in CSS and automatically generate both utility
classes and native CSS variables.

#### Setup (Tailwind v4)

```css
/* src/app/globals.css */
@import "tailwindcss";

/* Dark mode via class strategy */
@custom-variant dark (&:where(.dark, .dark *));

/* Design tokens — generates utility classes AND CSS variables */
@theme {
  --font-sans: "Inter", ui-sans-serif, system-ui, sans-serif;
  --font-display: "Cal Sans", "Inter", sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, monospace;

  --color-brand-500: oklch(0.60 0.16 250);
  --color-brand-600: oklch(0.50 0.14 250);

  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;

  --ease-out: cubic-bezier(0, 0, 0.2, 1);
  --ease-spring: cubic-bezier(0.175, 0.885, 0.32, 1.275);

  --duration-fast: 100ms;
  --duration-normal: 200ms;
  --duration-slow: 300ms;
}
```

> **Note:** In Tailwind v4, `@import "tailwindcss"` replaces the old `@tailwind base`,
> `@tailwind components`, `@tailwind utilities` directives. The `@theme` directive
> replaces `tailwind.config.js` for token definition.

#### Utility-First Rules

- **MUST** compose styles using Tailwind utility classes directly in JSX — this
  is the default and primary styling approach
- **MUST NOT** overuse `@apply` — it defeats the purpose of utility-first.
  If you find yourself writing `@apply` blocks with 5+ utilities, extract to a
  React component instead:

  ```tsx
  // BAD — recreating CSS abstractions with @apply
  // globals.css
  .btn-primary {
    @apply rounded-md bg-brand-500 px-4 py-2 text-white hover:bg-brand-600;
  }

  // GOOD — React component is the abstraction
  function PrimaryButton({ children, ...props }: ButtonProps) {
    return (
      <button className="rounded-md bg-brand-500 px-4 py-2 text-white hover:bg-brand-600" {...props}>
        {children}
      </button>
    );
  }
  ```

- **SHOULD** use `@apply` only for base element styling that cannot be
  componentized (e.g., styling `<body>`, `<html>`, or third-party elements)
- **MUST** install and use the **Tailwind CSS IntelliSense** VS Code extension
  — it provides autocomplete, linting, and class sorting

#### The `cn()` Utility

The `cn()` utility combines `clsx` (conditional classes) with `tailwind-merge`
(conflict resolution). It is the standard pattern in shadcn/ui and should be
used across all projects:

```ts
// src/lib/utils.ts
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

```tsx
// Usage — conditional classes without conflicts
<div className={cn(
  'rounded-lg border p-4',
  isActive && 'border-brand-500 bg-brand-500/10',
  className  // allows parent to override
)} />
```

- **MUST** use `cn()` for any conditional or dynamic class composition — never
  use string concatenation or template literals for Tailwind classes
- **MUST** accept a `className` prop on reusable components and merge it with
  `cn()` — this allows consumers to customize styling without forking the
  component

#### Class Ordering Convention

- **SHOULD** follow this order within a `className` string (Tailwind IntelliSense
  auto-sorts when configured):
  1. Layout (`flex`, `grid`, `block`, `relative`, `absolute`)
  2. Sizing (`w-`, `h-`, `min-`, `max-`)
  3. Spacing (`p-`, `m-`, `gap-`)
  4. Typography (`text-`, `font-`, `leading-`, `tracking-`)
  5. Colors (`bg-`, `text-`, `border-`)
  6. Borders & Shadows (`border-`, `rounded-`, `shadow-`)
  7. Effects (`opacity-`, `transition-`, `animate-`)
  8. Responsive modifiers (`sm:`, `md:`, `lg:`)
  9. State modifiers (`hover:`, `focus:`, `active:`, `dark:`)

- **SHOULD** enable the Prettier plugin for Tailwind CSS (`prettier-plugin-tailwindcss`)
  to enforce consistent class ordering automatically

---

### 4.2 Design Tokens & CSS Variables

Design tokens are the single source of truth for visual consistency. In
Tailwind v4, tokens defined with `@theme` serve double duty: they generate
utility classes **and** are available as CSS variables everywhere.

#### Token Categories

| Category | Namespace | Example | Generated Utility |
|---|---|---|---|
| Colors | `--color-*` | `--color-brand-500: oklch(...)` | `bg-brand-500`, `text-brand-500` |
| Spacing | `--spacing-*` | `--spacing-18: 4.5rem` | `p-18`, `m-18`, `gap-18` |
| Typography | `--font-*` | `--font-display: "Cal Sans"` | `font-display` |
| Font size | `--text-*` | `--text-hero: 3rem` | `text-hero` |
| Border radius | `--radius-*` | `--radius-lg: 0.5rem` | `rounded-lg` |
| Shadows | `--shadow-*` | `--shadow-card: 0 2px 8px ...` | `shadow-card` |
| Breakpoints | `--breakpoint-*` | `--breakpoint-3xl: 1920px` | `3xl:` variant |
| Easing | `--ease-*` | `--ease-spring: cubic-bezier(...)` | `ease-spring` |
| Duration | `--duration-*` | `--duration-fast: 100ms` | `duration-fast` |

#### Rules

- **MUST** define all design tokens in `@theme` inside `globals.css` — never
  hardcode colors, spacing, or font sizes directly in component classes:

  ```tsx
  // BAD — hardcoded color, not part of the design system
  <div className="bg-[#1a56db]">

  // GOOD — uses a design token
  <div className="bg-brand-500">
  ```

- **MUST** use the `@theme` directive for tokens that should generate utility
  classes. Use `:root` for CSS variables that should NOT generate utilities
  (e.g., theme-switching variables consumed by `@theme`)
- **SHOULD** use OKLCH color space for custom colors — it provides perceptually
  uniform lightness steps, producing more consistent color ramps than hex or HSL
- **SHOULD** keep the token set minimal — start with the tokens you actually use
  and add as needed. A 50-token system is easier to maintain than a 200-token one
- **SHOULD** reference tokens via CSS variables when needed in inline styles or
  arbitrary values: `style={{ color: 'var(--color-brand-500)' }}`

#### shadcn/ui Token Integration

shadcn/ui defines its own semantic token layer using CSS variables (e.g.,
`--background`, `--foreground`, `--primary`, `--muted`, `--destructive`).
These tokens live in `:root` and `.dark` selectors, and the shadcn/ui
components reference them:

```css
/* shadcn/ui token pattern (in globals.css, below @theme) */
:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --primary: oklch(0.205 0 0);
  --primary-foreground: oklch(0.985 0 0);
  --muted: oklch(0.965 0 0);
  --muted-foreground: oklch(0.556 0 0);
  --destructive: oklch(0.577 0.245 27.325);
  --border: oklch(0.922 0 0);
  --ring: oklch(0.708 0 0);
  --radius: 0.625rem;
  /* ... */
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --primary: oklch(0.985 0 0);
  --primary-foreground: oklch(0.205 0 0);
  --muted: oklch(0.269 0 0);
  --muted-foreground: oklch(0.708 0 0);
  --destructive: oklch(0.396 0.141 25.723);
  --border: oklch(0.269 0 0);
  --ring: oklch(0.439 0 0);
  /* ... */
}
```

- **MUST** keep the shadcn/ui semantic tokens as the component-level token
  layer — do not replace them with custom names in shadcn/ui components
- **SHOULD** customize the token values (colors) via `shadcn/create` presets
  or by editing the `:root` / `.dark` variables directly
- **MAY** add project-specific semantic tokens alongside shadcn/ui tokens
  when the design requires concepts shadcn/ui does not cover (e.g.,
  `--color-success`, `--color-warning`, `--color-info`)

---

### 4.3 Component Styling Patterns

#### Variants with `cva` (class-variance-authority)

`cva` is the standard pattern for components with multiple visual variants.
shadcn/ui uses it extensively:

```tsx
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const badgeVariants = cva(
  'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors',
  {
    variants: {
      variant: {
        default: 'border-transparent bg-primary text-primary-foreground',
        secondary: 'border-transparent bg-secondary text-secondary-foreground',
        destructive: 'border-transparent bg-destructive text-destructive-foreground',
        outline: 'text-foreground',
      },
    },
    defaultVariants: {
      variant: 'default',
    },
  }
);

interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}
```

- **SHOULD** use `cva` for any component with 2+ visual variants — it provides
  type-safe variant props and consistent class composition
- **SHOULD** always include a `defaultVariants` configuration so the component
  works without explicit variant props
- **MUST** merge the consumer's `className` with `cn()` after the variant classes
  — this ensures consumers can override specific styles

#### Conditional Styling

```tsx
// Simple boolean condition
<div className={cn('rounded-lg border', isSelected && 'border-brand-500 ring-2 ring-brand-500/20')} />

// Multiple conditions
<div className={cn(
  'rounded-lg border p-4 transition-colors',
  status === 'active' && 'border-green-500 bg-green-50',
  status === 'error' && 'border-red-500 bg-red-50',
  status === 'pending' && 'border-yellow-500 bg-yellow-50',
  disabled && 'pointer-events-none opacity-50',
)} />
```

- **MUST** use `cn()` for all conditional class logic — never ternaries in
  template literals that break Tailwind IntelliSense
- **MUST NOT** use JavaScript to conditionally set inline styles for values
  that have Tailwind equivalents — the dark mode variant `dark:` and
  responsive modifiers `sm:` are the correct tools

---

### 4.4 Breakpoints & Responsive Design

Tailwind's default breakpoints are the standard unless a project has a
justified reason to deviate. All responsive design follows mobile-first
(→ See [Section 1.3](#13-mobile-first-always)).

#### Standard Breakpoints

| Prefix | Min-Width | Typical Use |
|---|---|---|
| (none) | 0px | Mobile (base styles) |
| `sm:` | 640px | Large phones / small tablets |
| `md:` | 768px | Tablets |
| `lg:` | 1024px | Small desktops / landscape tablets |
| `xl:` | 1280px | Standard desktops |
| `2xl:` | 1536px | Large desktops |

```tsx
// Mobile-first: base styles → layer up
<div className="
  grid grid-cols-1 gap-4 p-4
  sm:grid-cols-2 sm:gap-6
  lg:grid-cols-3 lg:p-8
  xl:grid-cols-4
">
```

#### Container Queries (Tailwind v4)

Tailwind v4 includes first-class container query support. Use container queries
for components that need to adapt based on their **container's** size rather
than the viewport:

```tsx
// Parent marks itself as a container
<div className="@container">
  {/* Child responds to container size, not viewport */}
  <div className="flex flex-col @md:flex-row @lg:grid @lg:grid-cols-3">
    ...
  </div>
</div>
```

- **SHOULD** use container queries for reusable components that may be placed
  in different layout contexts (sidebars, modals, main content) — viewport
  breakpoints assume a fixed layout context
- **MAY** use container queries alongside viewport breakpoints — they are
  complementary, not mutually exclusive

#### Touch Targets

- **MUST** ensure all interactive elements have a minimum touch target of
  **44×44px** (recommended; WCAG 2.2 AA minimum is 24×24px):

  ```tsx
  // Tailwind: min-h-11 min-w-11 = 44px (assuming default 4px scale)
  <button className="min-h-11 min-w-11 px-4 py-2">Submit</button>
  ```

- **SHOULD** use `p-` (padding) rather than fixed `h-` / `w-` to achieve touch
  targets — this allows the element to grow with content

---

### 4.5 Dark/Light Theme

Dark mode is not optional — it is an expected feature of modern web
applications. The implementation uses `next-themes` for SSR-safe theme
switching and Tailwind's `dark:` variant for styling.

#### Architecture

```text
┌─────────────────────────────────────────────────────────┐
│ next-themes (ThemeProvider)                             │
│  - Manages theme state (light / dark / system)          │
│  - Persists user preference to localStorage             │
│  - Applies .dark class to <html> element                │
│  - Handles SSR without flash of wrong theme (FOWT)      │
├─────────────────────────────────────────────────────────┤
│ Tailwind CSS v4 (@custom-variant dark)                  │
│  - dark: variant activates when .dark class is present  │
│  - e.g., dark:bg-gray-900, dark:text-white              │
├─────────────────────────────────────────────────────────┤
│ CSS Variables (:root / .dark)                           │
│  - Semantic tokens change values per theme              │
│  - Components reference tokens, not hardcoded colors    │
│  - shadcn/ui uses this pattern by default               │
└─────────────────────────────────────────────────────────┘
```

#### Theme Priority Hierarchy

```text
1. User's explicit choice (stored in localStorage) → Highest priority
2. System preference (prefers-color-scheme)         → Fallback
3. Default theme (light)                            → Last resort
```

This is a three-way system: the user can choose light, dark, or "follow
system." `next-themes` handles all three scenarios out of the box.

#### Implementation Pattern

```tsx
// src/providers/theme-provider.tsx
'use client';

import { ThemeProvider as NextThemesProvider } from 'next-themes';

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  return (
    <NextThemesProvider
      attribute="class"
      defaultTheme="system"
      enableSystem
      disableTransitionOnChange
    >
      {children}
    </NextThemesProvider>
  );
}
```

```tsx
// src/app/layout.tsx (Root Layout)
import { ThemeProvider } from '@/providers/theme-provider';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}
```

```css
/* src/app/globals.css */
@import "tailwindcss";
@custom-variant dark (&:where(.dark, .dark *));

/* Theme tokens — values change per theme */
:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  /* ... shadcn/ui tokens ... */
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  /* ... shadcn/ui tokens ... */
}
```

```tsx
// Three-way theme toggle component
'use client';

import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';
import { Sun, Moon, Monitor } from 'lucide-react';

export function ThemeToggle() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  // Prevent hydration mismatch — render after mount
  useEffect(() => setMounted(true), []);
  if (!mounted) return null;

  return (
    <div role="radiogroup" aria-label="Theme selection">
      <button onClick={() => setTheme('light')} aria-pressed={theme === 'light'}>
        <Sun className="h-4 w-4" />
      </button>
      <button onClick={() => setTheme('dark')} aria-pressed={theme === 'dark'}>
        <Moon className="h-4 w-4" />
      </button>
      <button onClick={() => setTheme('system')} aria-pressed={theme === 'system'}>
        <Monitor className="h-4 w-4" />
      </button>
    </div>
  );
}
```

#### Rules

- **MUST** use `next-themes` for theme management — do not build a custom
  solution. It handles SSR, localStorage persistence, system preference
  detection, and FOWT prevention
- **MUST** add `suppressHydrationWarning` to the `<html>` tag — `next-themes`
  modifies the element before React hydration, which would otherwise trigger
  a warning
- **MUST** use `disableTransitionOnChange` in the `ThemeProvider` — without it,
  every element with CSS transitions animates simultaneously during theme
  switch, which looks jarring
- **MUST** use CSS variables for theme-dependent colors — components reference
  `bg-background`, `text-foreground`, `border-border`, not `bg-white dark:bg-gray-900`.
  The CSS variable approach ensures theme changes propagate automatically:

  ```tsx
  // BAD — hardcoded theme colors in every component
  <div className="bg-white text-black dark:bg-gray-900 dark:text-white">

  // GOOD — semantic tokens that adapt automatically
  <div className="bg-background text-foreground">
  ```

- **MUST** check `mounted` state before rendering theme-dependent UI in Client
  Components — during SSR, the theme is unknown. Rendering theme-specific
  content before mount causes hydration mismatches
- **SHOULD** provide a three-way toggle (light / dark / system) — respecting
  the user's system preference is important for UX
- **SHOULD** test both themes during development — not just the one you prefer.
  Use the toggle frequently while building

---

### 4.6 CSS Modules — Escape Hatch

CSS Modules are the approved fallback for cases where Tailwind utilities are
insufficient. They provide locally-scoped class names without runtime cost.

> → See [02-technology-radar.md, Section 4.3 — CSS Modules (Trial)]

#### When to Use CSS Modules

- Complex CSS animations with `@keyframes` that would result in unreadable
  utility class strings
- Third-party component overrides that require targeting specific CSS selectors
- Styles that genuinely map better to traditional CSS (complex pseudo-element
  chains, deeply nested selectors)

#### Rules

- **MUST** use the `.module.css` extension — this activates local scoping
- **MUST** co-locate the module file with its component (→ See [Section 2.3])
- **MUST NOT** create a parallel styling system — CSS Modules are an escape
  hatch, not an alternative to Tailwind. If more than 10% of components use
  CSS Modules, reassess the styling approach
- **SHOULD** reference design tokens via CSS variables inside modules:

  ```css
  /* user-card.module.css */
  .shimmer {
    background: linear-gradient(
      90deg,
      var(--color-muted) 0%,
      var(--color-muted-foreground) 50%,
      var(--color-muted) 100%
    );
    animation: shimmer 1.5s infinite;
  }

  @keyframes shimmer {
    0% { background-position: -200% 0; }
    100% { background-position: 200% 0; }
  }
  ```

---

### 4.7 Visual Design Principles

Code quality alone does not make a great product — design quality does.
These principles guide visual decisions beyond "does it work?" toward
"is it memorable?" They apply to every project, from freelance client
sites to personal learning projects.

> These guidelines incorporate principles from the frontend-design skill
> reference and adapt them into actionable rules for the standards stack.

#### Typography

Typography is the most impactful design decision. The right font pairing
elevates an interface from "functional" to "crafted."

- **SHOULD** choose fonts with intention — avoid defaulting to Inter, Roboto,
  or system fonts on every project. Explore options from Google Fonts or
  Fontsource that match the project's tone:
  - **Display fonts** for headings: Cal Sans, Bricolage Grotesque, Playfair
    Display, Space Grotesk, Instrument Serif
  - **Body fonts** for readability: Geist, DM Sans, Source Sans Pro, Nunito
  - **Monospace** for code: JetBrains Mono, Fira Code, Geist Mono
- **SHOULD** pair a distinctive display font with a refined body font — this
  creates visual hierarchy without relying solely on size and weight
- **MUST** load fonts using `next/font` for automatic optimization, self-hosting,
  and zero layout shift:

  ```tsx
  // src/app/layout.tsx
  import { Inter, Bricolage_Grotesque } from 'next/font/google';

  const sans = Inter({ subsets: ['latin'], variable: '--font-sans' });
  const display = Bricolage_Grotesque({ subsets: ['latin'], variable: '--font-display' });

  export default function RootLayout({ children }) {
    return (
      <html lang="en" className={`${sans.variable} ${display.variable}`}>
        <body className="font-sans">{children}</body>
      </html>
    );
  }
  ```

- **MUST** define font variables in `@theme` to make them available as utilities:

  ```css
  @theme {
    --font-sans: var(--font-sans); /* from next/font */
    --font-display: var(--font-display);
  }
  ```

#### Color & Theme

- **SHOULD** commit to a cohesive color palette with a dominant color and
  sharp accents — timid, evenly-distributed palettes look generic. One
  strong brand color with neutral companions creates more impact
- **SHOULD** use OKLCH for custom color definitions — it produces perceptually
  uniform lightness steps, making color ramps more consistent than hex or HSL
- **SHOULD** define both light and dark variants of the palette from the start
  — not as an afterthought
- **MUST NOT** use the same visual design across every project — vary themes,
  color palettes, and fonts to match each project's purpose and audience.
  A car dealership site should look different from a SaaS dashboard

#### Motion & Micro-Interactions

Motion should be purposeful — it communicates state changes, guides attention,
and adds polish. Gratuitous animation is worse than no animation.

- **SHOULD** focus on high-impact moments: page load reveals (staggered
  `animation-delay`), hover states, and state transitions. One well-orchestrated
  entrance animation creates more delight than scattered micro-interactions
- **SHOULD** use CSS transitions for simple state changes (hover, focus, color
  shifts) and Framer Motion (→ See [02-technology-radar.md]) for complex
  orchestrated animations:

  ```tsx
  // CSS transition — simple, zero JS
  <button className="transition-colors duration-normal hover:bg-brand-600">

  // Tailwind v4 — @starting-style for enter animations (no JS)
  <div className="starting:opacity-0 starting:translate-y-4 transition-all duration-slow">
  ```

- **SHOULD** respect the user's motion preference — always provide a reduced
  motion alternative:

  ```tsx
  <div className="animate-fade-in motion-reduce:animate-none">
  ```

- **MUST NOT** animate layout properties (`width`, `height`, `top`, `left`)
  directly — use `transform` and `opacity` for performant animations.
  Layout animations cause reflow and degrade performance

#### Spatial Composition

- **SHOULD** use asymmetry and generous negative space intentionally — not
  every layout needs to be a centered, symmetrical grid. Off-center content,
  overlapping elements, and unexpected spacing create visual interest
- **SHOULD** use CSS Grid for two-dimensional layouts and Flexbox for
  one-dimensional alignment — Grid is not "the new Flexbox"; they solve
  different problems
- **MAY** break the grid occasionally for emphasis — a full-bleed image or
  an element that extends beyond its container adds dynamism

#### Backgrounds & Visual Depth

- **SHOULD** create atmosphere and depth rather than defaulting to flat solid
  colors — consider gradient meshes, subtle noise textures, layered
  transparencies, and contextual shadows that match the project's aesthetic
- **SHOULD** use `backdrop-blur` and `bg-opacity` for glass-morphism effects
  sparingly — they add visual richness but have performance cost on mobile
- **MUST NOT** use heavy background effects that impact Core Web Vitals
  (→ See [Section 11](#11-performance)) — visual polish must not compromise
  performance

---

### 4.8 Anti-Patterns (Styling)

| Anti-Pattern | Why It Is Wrong | Correct Alternative |
|---|---|---|
| Inline styles for values Tailwind can handle | Bypasses the design system, not responsive/dark-mode-aware | Use Tailwind utilities or design tokens |
| `@apply` blocks with 5+ utilities | Recreates CSS abstractions, loses utility-first benefits | Extract to a React component |
| Hardcoded hex colors in className | Not part of the design token system, impossible to theme | Define tokens in `@theme`, use generated utilities |
| `!important` to override styles | Specificity escalation, unmaintainable cascade | Use `cn()` with `tailwind-merge` to resolve conflicts |
| Conditional styling with JS (`style={{ color: dark ? ... : ... }}`) | Bypasses Tailwind's dark mode system, not SSR-safe | Use `dark:` variant or CSS variables |
| Copy-pasting identical class strings across components | Violates DRY, creates inconsistency over time | Extract to a shared component or `cva` variant |
| Using the same fonts/colors/layout on every project | Produces generic "AI-generated" aesthetics | Commit to a unique visual direction per project (§4.7) |
| Ignoring dark mode during development | Broken dark theme shipped to production | Toggle themes frequently while building (§4.5) |
| Background images/effects that block rendering | Hurts LCP and CLS, bad mobile experience | Optimize assets, use `loading="lazy"`, test Core Web Vitals |
| Fighting shadcn/ui component styles instead of customizing tokens | Fragile overrides that break on updates | Customize the `:root` / `.dark` CSS variables |

---

## 5. State Management

State management is the art of putting data in the right place. The wrong
abstraction creates more problems than the state itself — over-engineered
global stores for local toggles, `useEffect` waterfalls for data that should
live on the server, and prop-drilling marathons for data that should be in
Context.

The guiding principle is simple: **the best state management is the least
state management.** Every piece of state should live in the most local,
most appropriate place — and move to a broader scope only when there is a
demonstrated need.

> The technology choices for state management are defined in
> → See [02-technology-radar.md, Section 4.6 and Decision Guide 6.5].
> This section defines **how** to apply those choices with practical patterns.

---

### 5.1 Decision Hierarchy

Before writing any state code, run through this hierarchy top-to-bottom.
Stop at the first level that solves the problem. Reaching for a more
complex solution without exhausting simpler ones is overengineering.

```text
┌─────────────────────────────────────────────────────────────┐
│  1. NO STATE — Can this be derived or computed?             │
│     Derived values, computed props, .filter(), .map()       │
│     If yes → no state needed, just compute it.              │
├─────────────────────────────────────────────────────────────┤
│  2. SERVER STATE — Does this data come from an API or DB?   │
│     ├─ Server Component → fetch directly (await)            │
│     └─ Client Component → TanStack Query                    │
├─────────────────────────────────────────────────────────────┤
│  3. URL STATE — Should this survive a page refresh?         │
│     Filters, sort, pagination, active tab, search query     │
│     → Use searchParams (URL as source of truth)             │
├─────────────────────────────────────────────────────────────┤
│  4. LOCAL STATE — Is this used by one component?            │
│     Toggles, form inputs, dropdown open/closed              │
│     → useState or useReducer                                │
├─────────────────────────────────────────────────────────────┤
│  5. SHARED STATE — Is this used across many components?     │
│     Theme, locale, auth status, feature flags               │
│     → React Context (low-frequency updates only)            │
├─────────────────────────────────────────────────────────────┤
│  6. COMPLEX GLOBAL STATE — Nothing above works?             │
│     Multi-step wizard, drawing canvas, complex filter panel │
│     → Zustand (Trial — requires justification)              │
└─────────────────────────────────────────────────────────────┘
```

- **MUST** follow this hierarchy in order — reaching for Zustand or Context
  before considering derived values, URL state, or local state is a code
  smell
- **MUST** justify in code review any state that skips a level — "why is
  this not in the URL?" or "why is this in Context instead of local state?"
  are valid review questions

---

### 5.2 Server State (Fetched Data)

Server state is data that originates from an external source (API, database,
third-party service). It is fundamentally different from client state — it is
asynchronous, shared across users, and can become stale at any moment.

#### In Server Components (Default)

The simplest and most performant approach. Data is fetched on the server,
rendered to HTML, and shipped to the client with zero JavaScript overhead:

```tsx
// Server Component — data fetched at render time
export default async function DashboardPage() {
  const stats = await statsService.getOverview();
  const recentOrders = await orderService.listRecent({ limit: 5 });

  return (
    <div>
      <StatsGrid stats={stats} />
      <RecentOrdersTable orders={recentOrders} />
    </div>
  );
}
```

- **MUST** fetch data in Server Components for initial page loads — this is
  the default approach in Next.js 16
- **MUST** validate data from external sources with Zod at the service layer
  (→ See [01-core-principles.md, Section 2 — Fail Fast])
- **SHOULD** use Next.js caching and revalidation patterns intentionally:

  ```tsx
  // Next.js 16: opt into caching with "use cache"
  // (requires cacheComponents: true in next.config.ts)
  async function getStats() {
    'use cache';
    return await statsService.getOverview();
  }
  ```

- **MUST NOT** use TanStack Query in Server Components — there is no
  client-side cache to manage on the server

#### In Client Components (TanStack Query)

When data must be fetched on the client — for real-time updates, pagination
triggered by user interaction, or data that changes after the initial render:

```tsx
'use client';

import { useQuery } from '@tanstack/react-query';

export function NotificationBell() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['notifications', 'unread'],
    queryFn: () => fetch('/api/notifications?status=unread').then(r => r.json()),
    staleTime: 30_000,       // Fresh for 30 seconds
    refetchInterval: 60_000, // Refetch every 60 seconds
  });

  if (isLoading) return <BellSkeleton />;
  if (error) return <BellError />;

  return <Bell count={data.data.length} />;
}
```

- **MUST** configure `QueryClientProvider` at the application root
  (in a Client Component provider file):

  ```tsx
  // src/providers/query-provider.tsx
  'use client';

  import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
  import { useState } from 'react';

  export function QueryProvider({ children }: { children: React.ReactNode }) {
    const [queryClient] = useState(() => new QueryClient({
      defaultOptions: {
        queries: {
          staleTime: 60_000,    // 1 minute default
          gcTime: 5 * 60_000,   // 5 minutes garbage collection
          retry: 1,             // Retry failed queries once
          refetchOnWindowFocus: false, // Disable for most apps
        },
      },
    }));

    return (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );
  }
  ```

- **MUST** use query keys that reflect the data identity — include all
  variables that affect the query result:

  ```tsx
  // BAD — same key returns different data depending on hidden state
  queryKey: ['users']

  // GOOD — key includes all parameters
  queryKey: ['users', { page, status, search }]
  ```

- **SHOULD** encapsulate TanStack Query usage in custom hooks within
  the feature module:

  ```tsx
  // src/features/users/hooks/use-users-query.ts
  import { useQuery } from '@tanstack/react-query';
  import { userService } from '../services/user-service';

  export function useUsersQuery(filters: UserFilters) {
    return useQuery({
      queryKey: ['users', filters],
      queryFn: () => userService.list(filters),
    });
  }
  ```

- **MUST NOT** use TanStack Query for client-only state (form values,
  UI toggles, theme) — it is a server state cache, not a global store
- **MUST NOT** use `useEffect` + `useState` for data fetching in new code
  — TanStack Query handles loading, error, caching, and refetching

> For complete data fetching patterns including loading states, error
> handling, and pagination: → See [Section 6 — Data Fetching].

---

### 5.3 Client State (Local UI)

Client state is data that exists only in the browser, controlled entirely
by the user or the UI logic. It does not come from an API and does not
need to be shared across the application.

#### `useState` — Simple State

For toggles, counters, single form fields, and component-level UI state:

```tsx
const [isOpen, setIsOpen] = useState(false);
const [selectedId, setSelectedId] = useState<string | null>(null);
const [count, setCount] = useState(0);
```

#### `useReducer` — Complex Local State

For state with multiple related fields that change together, or state
transitions that follow specific rules:

```tsx
type FilterState = {
  search: string;
  status: 'all' | 'active' | 'archived';
  dateRange: { from: Date | null; to: Date | null };
};

type FilterAction =
  | { type: 'SET_SEARCH'; payload: string }
  | { type: 'SET_STATUS'; payload: FilterState['status'] }
  | { type: 'SET_DATE_RANGE'; payload: FilterState['dateRange'] }
  | { type: 'RESET' };

function filterReducer(state: FilterState, action: FilterAction): FilterState {
  switch (action.type) {
    case 'SET_SEARCH':
      return { ...state, search: action.payload };
    case 'SET_STATUS':
      return { ...state, status: action.payload };
    case 'SET_DATE_RANGE':
      return { ...state, dateRange: action.payload };
    case 'RESET':
      return initialFilterState;
  }
}

const [filters, dispatch] = useReducer(filterReducer, initialFilterState);
```

#### Rules

- **MUST** keep client state as local as possible — if only one component
  uses the state, it stays in that component
- **SHOULD** prefer `useState` for simple values (booleans, strings, numbers)
  and `useReducer` for state with 3+ related fields or complex transitions
- **MUST NOT** lift state to a parent component "just in case" a sibling
  might need it later — lift only when a sibling actually needs it (YAGNI)
- **SHOULD** use `useEffectEvent` (React 19.2) to separate event-like logic
  from effects, preventing unnecessary effect re-runs:

  ```tsx
  import { useEffect, useEffectEvent } from 'react';

  function ChatRoom({ roomId, theme }: { roomId: string; theme: string }) {
    // Event logic that reads current props but should NOT trigger reconnection
    const onConnected = useEffectEvent(() => {
      showNotification('Connected!', theme);
    });

    // Effect depends only on roomId — theme changes do NOT cause reconnection
    useEffect(() => {
      const connection = createConnection(roomId);
      connection.on('connected', onConnected);
      connection.connect();
      return () => connection.disconnect();
    }, [roomId]); // ✅ theme is NOT in deps — correct!
  }
  ```

- **SHOULD** use `useEffectEvent` for callbacks inside effects that need
  current values (notifications, analytics, logging) but should not trigger
  effect re-execution. Do NOT use it just to silence lint warnings

---

### 5.4 URL State (searchParams)

The URL is the most underused state management tool. For any state that
should survive a page refresh, be shareable via link, or work with the
browser's back/forward buttons — the URL is the correct home.

#### What Belongs in the URL

| State | URL? | Why |
|---|---|---|
| Active filters (`status=active`) | ✅ | Shareable, bookmarkable, back button works |
| Sort order (`sortBy=price&sortOrder=asc`) | ✅ | Part of the "view" the user configured |
| Pagination (`page=3`) | ✅ | Direct link to page 3, back button returns to page 2 |
| Search query (`search=mercedes`) | ✅ | Shareable, bookmarkable |
| Active tab (`tab=settings`) | ✅ | Direct link to the settings tab |
| Modal open/closed | ❌ | Transient UI state, not part of the "view" |
| Form input values | ❌ | Too noisy in the URL, changes on every keystroke |
| Dropdown open/closed | ❌ | Micro-interaction state, not meaningful |

#### Implementation Pattern

```tsx
'use client';

import { useSearchParams, useRouter, usePathname } from 'next/navigation';

export function useUrlState<T extends string>(
  key: string,
  defaultValue: T,
): [T, (value: T) => void] {
  const searchParams = useSearchParams();
  const router = useRouter();
  const pathname = usePathname();

  const value = (searchParams.get(key) as T) ?? defaultValue;

  function setValue(newValue: T) {
    const params = new URLSearchParams(searchParams.toString());
    if (newValue === defaultValue) {
      params.delete(key); // Clean URL when value is default
    } else {
      params.set(key, newValue);
    }
    router.push(`${pathname}?${params.toString()}`);
  }

  return [value, setValue];
}

// Usage
function VehicleFilters() {
  const [status, setStatus] = useUrlState('status', 'all');
  const [sortBy, setSortBy] = useUrlState('sortBy', 'createdAt');

  return (
    <div>
      <Select value={status} onValueChange={setStatus}>
        <SelectItem value="all">All</SelectItem>
        <SelectItem value="available">Available</SelectItem>
        <SelectItem value="sold">Sold</SelectItem>
      </Select>
      {/* ... */}
    </div>
  );
}
```

#### Rules

- **SHOULD** use URL `searchParams` as the source of truth for filters,
  sort, pagination, search queries, and active tabs
- **MUST** sync URL state with TanStack Query — the query key should include
  the URL parameters so the cache updates when the URL changes:

  ```tsx
  const searchParams = useSearchParams();
  const filters = parseFilters(searchParams);

  const { data } = useQuery({
    queryKey: ['vehicles', filters],  // URL params in the key
    queryFn: () => vehicleService.list(filters),
  });
  ```

- **SHOULD** remove parameters from the URL when they equal the default
  value — keep URLs clean: `/vehicles` instead of
  `/vehicles?status=all&sortBy=createdAt&sortOrder=desc&page=1`
- **SHOULD** validate URL parameters with Zod before using them — URLs
  are user-editable input

---

### 5.5 Form State

Form state is a special category — it is local, transient, and has specific
UX requirements (validation, touched tracking, submit handling). It is
covered in detail in → See [Section 7 — Form Handling].

The key rule here is placement: **form state lives in react-hook-form, not
in component state or global stores.** Do not duplicate form state with
`useState` alongside `react-hook-form` — the form library is the single
source of truth for form values.

---

### 5.6 Global Client State (Zustand)

Zustand is the last resort in the hierarchy — for complex client-side state
that is shared across distant components and cannot be solved by
composition, Context, or URL state.

> Zustand is classified as **Trial** in → See [02-technology-radar.md, Section 4.6].
> Its usage requires justification.

#### When Zustand Is Justified

- Multi-step wizard with branching logic and state that must persist across
  steps and back-navigation
- Drawing canvas or rich interactive editor with complex undo/redo
- Complex filter panel with 10+ interdependent filters shared across
  multiple views
- Shopping cart state that must persist across routes but not in the URL

#### When Zustand Is NOT Justified

- Theme or locale switching → React Context
- Auth status → React Context or Server Components
- Server data caching → TanStack Query
- Simple toggle shared between 2 components → lift state to common parent
- Filter state with 2–3 options → URL searchParams

#### Pattern

```tsx
// src/stores/cart-store.ts
import { create } from 'zustand';

interface CartItem {
  productId: string;
  name: string;
  price: number;
  quantity: number;
}

interface CartStore {
  items: CartItem[];
  addItem: (item: Omit<CartItem, 'quantity'>) => void;
  removeItem: (productId: string) => void;
  updateQuantity: (productId: string, quantity: number) => void;
  clearCart: () => void;
  totalItems: () => number;
  totalPrice: () => number;
}

export const useCartStore = create<CartStore>((set, get) => ({
  items: [],

  addItem: (item) => set((state) => {
    const existing = state.items.find(i => i.productId === item.productId);
    if (existing) {
      return {
        items: state.items.map(i =>
          i.productId === item.productId
            ? { ...i, quantity: i.quantity + 1 }
            : i
        ),
      };
    }
    return { items: [...state.items, { ...item, quantity: 1 }] };
  }),

  removeItem: (productId) => set((state) => ({
    items: state.items.filter(i => i.productId !== productId),
  })),

  updateQuantity: (productId, quantity) => set((state) => ({
    items: state.items.map(i =>
      i.productId === productId ? { ...i, quantity } : i
    ),
  })),

  clearCart: () => set({ items: [] }),

  totalItems: () => get().items.reduce((sum, i) => sum + i.quantity, 0),

  totalPrice: () => get().items.reduce((sum, i) => sum + i.price * i.quantity, 0),
}));
```

#### Rules

- **MUST** create an ADR when introducing Zustand to a project — document
  why the hierarchy alternatives (§5.1) were insufficient
- **MUST** keep stores focused and small — one store per domain concept
  (cart store, wizard store), not one mega-store for everything
- **MUST NOT** put server state in Zustand — server data belongs in
  TanStack Query
- **SHOULD** use selectors to prevent unnecessary re-renders — components
  should subscribe only to the slice of state they need:

  ```tsx
  // BAD — rerenders on ANY store change
  const store = useCartStore();

  // GOOD — rerenders only when totalItems changes
  const totalItems = useCartStore((state) => state.totalItems());
  ```

- **SHOULD** co-locate Zustand stores in the feature module that owns them
  (`features/cart/stores/cart-store.ts`), not in a global `stores/` directory
  — unless the store is genuinely shared across multiple features

---

### 5.7 Anti-Patterns

| Anti-Pattern | Why It Is Wrong | Correct Alternative |
|---|---|---|
| Global store for everything (Redux mindset) | Unnecessary complexity, every component coupled to one store | Follow the hierarchy: local → URL → Context → Zustand |
| `useEffect` + `useState` for API data | Race conditions, no caching, no loading/error states, stale data | Server Components or TanStack Query (§5.2) |
| Duplicating server data in client state | Two sources of truth, data drift, manual sync bugs | Let TanStack Query be the cache |
| Context for high-frequency updates | Re-renders every consumer on every change (performance) | Zustand with selectors, or `useReducer` locally |
| Prop drilling through 4+ levels | Fragile, every intermediate component is coupled to data it does not use | Composition (children pattern), Context, or restructure the tree |
| Filters/sort/pagination in `useState` | Lost on refresh, not shareable, breaks back button | URL searchParams (§5.4) |
| Zustand without justification | Adds dependency and mental model overhead for no gain | useState, Context, or URL state first |
| Storing derived values in state | Extra state to maintain, stale when source changes | Compute on render: `const total = items.reduce(...)` |
| `useEffect` to sync state A with state B | Creates render loops, hard to debug, sign of wrong data model | Derive B from A, or restructure so only one state exists |
| Using `useEffectEvent` to silence lint | Hides dependency bugs instead of fixing the data flow | Fix the dependency array correctly; only use `useEffectEvent` for true event callbacks |

---

## 6. Data Fetching

Data fetching is where the frontend meets the backend contract. Every
pattern in this section assumes the API follows the conventions in
→ See [03-api-design.md] — specifically the standard response envelope
`{ ok, data, error, requestId, meta }`, the error structure, and the
pagination format.

The fundamental rule is: **fetch data as close to where it is needed as
possible, and as early in the rendering pipeline as possible.** Server
Components fetch on the server. Client Components use TanStack Query.
Nothing uses `useEffect` + `useState` for data fetching.

> For the state management context of data fetching decisions:
> → See [Section 5 — State Management, §5.1 Decision Hierarchy and §5.2 Server State].

---

### 6.1 Server Components Data Fetching (Default)

Server Components can `await` data directly during rendering. This is the
default approach for all initial page loads — it eliminates client-side
waterfalls, ships zero JavaScript for the data fetching logic, and produces
HTML with real content for SEO and AI discoverability
(→ See [Section 12](#12-seo--ai-discoverability-geo)).

```tsx
// app/(dashboard)/dashboard/vehicles/page.tsx — Server Component
import { vehicleService } from '@/features/vehicles/services/vehicle-service';
import { VehicleList } from '@/features/vehicles/components/vehicle-list';
import { VehicleFilters } from '@/features/vehicles/components/vehicle-filters';

interface PageProps {
  searchParams: Promise<{
    page?: string;
    status?: string;
    sortBy?: string;
  }>;
}

export default async function VehiclesPage({ searchParams }: PageProps) {
  const params = await searchParams;
  const filters = {
    page: Number(params.page) || 1,
    status: params.status,
    sortBy: params.sortBy || 'createdAt',
  };

  const result = await vehicleService.list(filters);

  return (
    <div>
      <h1>Vehicles</h1>
      <VehicleFilters current={filters} />        {/* Client Component */}
      <VehicleList vehicles={result.data} />       {/* Server Component */}
      <Pagination meta={result.meta} />            {/* Client Component */}
    </div>
  );
}
```

> **Note (Next.js 16):** In Next.js 16, `searchParams` is a Promise and must
> be awaited. This is a breaking change from Next.js 14 where it was a plain
> object.

#### Parallel Data Fetching

When a page needs multiple independent data sources, fetch them in parallel
to avoid sequential waterfalls:

```tsx
export default async function DashboardPage() {
  // BAD — sequential: total time = sum of all fetches
  const stats = await statsService.getOverview();
  const orders = await orderService.listRecent();
  const alerts = await alertService.getActive();

  // GOOD — parallel: total time = slowest fetch
  const [stats, orders, alerts] = await Promise.all([
    statsService.getOverview(),
    orderService.listRecent(),
    alertService.getActive(),
  ]);

  return (
    <div>
      <StatsGrid stats={stats} />
      <RecentOrders orders={orders} />
      <AlertBanner alerts={alerts} />
    </div>
  );
}
```

#### Streaming with Suspense

For pages where some data is fast and some is slow, use `<Suspense>` to
stream the fast content immediately while the slow content loads:

```tsx
import { Suspense } from 'react';

export default async function DashboardPage() {
  const stats = await statsService.getOverview(); // Fast — renders immediately

  return (
    <div>
      <StatsGrid stats={stats} />

      {/* Slow content streams in when ready */}
      <Suspense fallback={<RecentOrdersSkeleton />}>
        <RecentOrders />  {/* This async Server Component fetches its own data */}
      </Suspense>

      <Suspense fallback={<AnalyticsChartSkeleton />}>
        <AnalyticsChart />
      </Suspense>
    </div>
  );
}

// RecentOrders.tsx — async Server Component
async function RecentOrders() {
  const orders = await orderService.listRecent(); // Slow fetch
  return <OrderTable orders={orders} />;
}
```

#### Rules

- **MUST** fetch data in Server Components for initial page loads — this is
  the default and most performant approach
- **MUST** use `Promise.all()` for independent data fetches on the same page
  — sequential awaits create unnecessary waterfalls
- **SHOULD** use `<Suspense>` boundaries to stream slow content independently
  — this keeps the page responsive while heavy data loads
- **SHOULD** provide meaningful skeleton components as `<Suspense>` fallbacks
  — not spinner icons (→ See [Section 8.5](#85-fallback-uis))
- **MUST NOT** fetch data in `layout.tsx` for data that changes per page —
  layouts persist across navigations and do not refetch. Only fetch data in
  layouts that is truly shared (user profile, navigation items)

---

### 6.2 TanStack Query Patterns (Client-Side)

TanStack Query is used in Client Components for data that must be fetched
or refetched after the initial page render — user-triggered pagination,
real-time updates, mutations with optimistic UI, and interactive data
exploration.

> For TanStack Query setup and configuration:
> → See [Section 5.2 — Server State, Client Components].

#### Query Keys Strategy

Query keys are the identity of cached data. Well-designed keys enable
automatic cache invalidation, background refetching, and data sharing
between components.

```tsx
// Convention: [entity, ...identifiers, { ...filters }]
// Examples:
['vehicles']                                    // All vehicles (list)
['vehicles', vehicleId]                         // Single vehicle
['vehicles', { page: 1, status: 'available' }]  // Filtered list
['vehicles', vehicleId, 'images']                // Vehicle's images

// Create a query key factory for consistency
export const vehicleKeys = {
  all:     ['vehicles'] as const,
  lists:   () => [...vehicleKeys.all, 'list'] as const,
  list:    (filters: VehicleFilters) => [...vehicleKeys.lists(), filters] as const,
  details: () => [...vehicleKeys.all, 'detail'] as const,
  detail:  (id: string) => [...vehicleKeys.details(), id] as const,
};

// Usage
useQuery({ queryKey: vehicleKeys.list(filters), queryFn: ... });
useQuery({ queryKey: vehicleKeys.detail(vehicleId), queryFn: ... });

// Invalidation — invalidate all vehicle lists after a mutation
queryClient.invalidateQueries({ queryKey: vehicleKeys.lists() });
```

- **MUST** use a query key factory per entity — this prevents key
  inconsistencies across components and simplifies invalidation
- **MUST** include all variables that affect the result in the key — if
  the query depends on `page`, `status`, and `search`, all three must be
  in the key
- **SHOULD** co-locate query key factories with the feature module
  (`features/vehicles/hooks/vehicle-keys.ts`)

#### Mutations

Mutations modify server data (create, update, delete). TanStack Query's
`useMutation` pairs with cache invalidation to keep the UI in sync:

```tsx
import { useMutation, useQueryClient } from '@tanstack/react-query';

export function useDeleteVehicle() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (vehicleId: string) => vehicleService.delete(vehicleId),
    onSuccess: () => {
      // Invalidate all vehicle lists — they may have changed
      queryClient.invalidateQueries({ queryKey: vehicleKeys.lists() });
    },
    onError: (error) => {
      // Show toast notification with error message
      toast.error(mapApiError(error));
    },
  });
}
```

#### Loading, Error, and Empty States

Every query has three possible outcomes beyond success. All three **MUST**
be handled explicitly:

```tsx
export function VehicleList({ filters }: { filters: VehicleFilters }) {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: vehicleKeys.list(filters),
    queryFn: () => vehicleService.list(filters),
  });

  // 1. Loading state
  if (isLoading) return <VehicleListSkeleton />;

  // 2. Error state
  if (isError) return <ErrorCard error={error} onRetry={() => refetch()} />;

  // 3. Empty state
  if (data.data.length === 0) return <EmptyState message="No vehicles found." />;

  // 4. Success state
  return (
    <div>
      {data.data.map((vehicle) => (
        <VehicleCard key={vehicle.id} vehicle={vehicle} />
      ))}
      <Pagination meta={data.meta} />
    </div>
  );
}
```

- **MUST** handle loading, error, and empty states for every query —
  an unhandled loading state shows a blank screen; an unhandled error
  state shows a broken UI; an unhandled empty state confuses the user
- **SHOULD** provide skeleton components that match the layout of the
  loaded content — this reduces layout shift (CLS)
- **SHOULD** provide a retry action in error states — many errors are
  transient (network hiccups, server restarts)
- **SHOULD** distinguish between "no data because of filters" and "no
  data at all" in empty states — "No vehicles match your filters" with
  a "Clear filters" button is more helpful than "No vehicles found"

---

### 6.3 Next.js Caching & Revalidation

Next.js 16 replaces the implicit caching model of earlier versions with
explicit, opt-in caching via Cache Components and the `"use cache"` directive.

> **Important:** In Next.js 16, all data fetching is dynamic by default.
> Nothing is cached unless you explicitly opt in. This is a significant
> change from Next.js 14 where `fetch()` was cached by default.

#### Cache Components (`"use cache"`)

```tsx
// Enable in next.config.ts
const nextConfig = { cacheComponents: true };

// Mark a function or component for caching
async function getPopularVehicles() {
  'use cache';
  return await vehicleService.listPopular();
}

// Revalidation with tags
import { cacheTag } from 'next/cache';

async function getVehicle(id: string) {
  'use cache';
  cacheTag(`vehicle-${id}`);
  return await vehicleService.findById(id);
}

// Invalidation
import { revalidateTag } from 'next/cache';
revalidateTag('vehicle-abc123', 'max');  // Next.js 16: requires cacheLife profile
```

#### Rules

- **MUST** understand that data fetching in Next.js 16 is dynamic by default
  — there is no implicit caching to worry about or fight against
- **SHOULD** use `"use cache"` for data that changes infrequently and is
  read often — popular products, site-wide settings, navigation data
- **SHOULD** use `cacheTag()` to tag cached data for targeted invalidation
  after mutations
- **MUST** pass a `cacheLife` profile as the second argument to
  `revalidateTag()` in Next.js 16 — the single-argument form is deprecated:

  ```tsx
  // Next.js 16 — correct
  revalidateTag('vehicles', 'max');
  revalidateTag('news', 'hours');

  // Deprecated — single argument
  revalidateTag('vehicles');
  ```

- **MUST NOT** cache user-specific data without proper cache key isolation
  — cached data is shared across users unless scoped

---

### 6.4 SWR Patterns

Stale-While-Revalidate (SWR) is a pattern where the UI shows cached (stale)
data immediately while fetching fresh data in the background. TanStack Query
implements this natively via `staleTime` and `gcTime`:

```tsx
const { data } = useQuery({
  queryKey: ['dashboard-stats'],
  queryFn: () => statsService.getOverview(),
  staleTime: 5 * 60_000,     // Data is "fresh" for 5 minutes
  gcTime: 30 * 60_000,       // Keep in cache for 30 minutes
  refetchOnWindowFocus: true, // Refetch when user returns to tab
});
```

- **SHOULD** configure `staleTime` based on how frequently the data changes:
  - Real-time data (chat, notifications): `0` (always stale, always refetch)
  - Active data (dashboard stats, order counts): `30_000` to `60_000` (30s–1m)
  - Semi-static data (user profile, settings): `5 * 60_000` (5 min)
  - Static data (categories, config): `Infinity` (never stale, manual invalidation)
- **SHOULD** use `refetchOnWindowFocus: true` for data that might change
  while the user is on another tab (dashboard, notifications)

---

### 6.5 API Response Consumption

The frontend consumes API responses that follow the standard envelope defined
in → See [03-api-design.md, Section 4].

#### Mapping API Errors to UI

The API returns errors in a structured format with a `code` field. The
frontend maps these codes to user-friendly messages:

```tsx
// src/lib/api-errors.ts
const ERROR_MESSAGES: Record<string, string> = {
  VALIDATION_ERROR: 'Please check the form for errors.',
  NOT_FOUND: 'The requested item could not be found.',
  UNAUTHORIZED: 'Please log in to continue.',
  FORBIDDEN: 'You do not have permission to perform this action.',
  CONFLICT: 'This item has been modified by another user. Please refresh.',
  RATE_LIMITED: 'Too many requests. Please wait a moment and try again.',
  INTERNAL_ERROR: 'An unexpected error occurred. Please try again later.',
};

export function mapApiError(error: unknown): string {
  if (error instanceof ApiError) {
    return ERROR_MESSAGES[error.code] ?? ERROR_MESSAGES.INTERNAL_ERROR;
  }
  return ERROR_MESSAGES.INTERNAL_ERROR;
}
```

> For the complete error code catalogue: → See [03-api-design.md, Section 5].

#### Consuming Pagination Responses

```tsx
// The API returns: { ok, data: [...], meta: { page, pageSize, totalItems, totalPages } }
function usePaginatedVehicles(page: number, filters: VehicleFilters) {
  return useQuery({
    queryKey: vehicleKeys.list({ ...filters, page }),
    queryFn: () => vehicleService.list({ ...filters, page }),
    placeholderData: keepPreviousData, // Show previous page while loading next
  });
}

// In the component
const { data } = usePaginatedVehicles(currentPage, filters);
const vehicles = data?.data ?? [];
const meta = data?.meta;

return (
  <div>
    {vehicles.map(v => <VehicleCard key={v.id} vehicle={v} />)}
    {meta && (
      <Pagination
        currentPage={meta.page}
        totalPages={meta.totalPages}
        onPageChange={setPage}
      />
    )}
  </div>
);
```

- **MUST** use `keepPreviousData` (TanStack Query) for paginated data —
  this prevents the UI from flashing to a loading state between pages
- **SHOULD** always access `data.data` (not just `data`) to match the
  response envelope — the first `data` is TanStack Query's wrapper, the
  second is the API's `data` field

#### Consuming Cursor-Based Pagination (Infinite Scroll)

```tsx
import { useInfiniteQuery } from '@tanstack/react-query';

function useInfiniteVehicles(filters: VehicleFilters) {
  return useInfiniteQuery({
    queryKey: vehicleKeys.list({ ...filters, type: 'infinite' }),
    queryFn: ({ pageParam }) =>
      vehicleService.list({ ...filters, cursor: pageParam }),
    initialPageParam: undefined as string | undefined,
    getNextPageParam: (lastPage) =>
      lastPage.meta.hasMore ? lastPage.meta.nextCursor : undefined,
  });
}

// In the component
const { data, fetchNextPage, hasNextPage, isFetchingNextPage } =
  useInfiniteVehicles(filters);

const allVehicles = data?.pages.flatMap(page => page.data) ?? [];
```

---

### 6.6 Anti-Patterns

| Anti-Pattern | Why It Is Wrong | Correct Alternative |
|---|---|---|
| `useEffect` + `useState` for data fetching | Race conditions, no caching, no retry, no loading/error states | Server Components or TanStack Query |
| Sequential awaits for independent data | Waterfall — page loads as slow as the sum of all fetches | `Promise.all()` for parallel fetching (§6.1) |
| Fetching data in `layout.tsx` that changes per page | Layouts persist — data becomes stale on navigation | Fetch in `page.tsx`, or use `<Suspense>` within the layout |
| No loading states | Blank screen while data loads — user thinks the page is broken | `loading.tsx`, `<Suspense>` fallbacks, skeleton components |
| No error handling on queries | Unhandled promise rejection, broken UI with no feedback | `isError` + `<ErrorCard>` with retry action |
| Ignoring empty states | User sees an empty page with no guidance | Dedicated empty state with message and action |
| Caching user-specific data without key isolation | User A sees User B's data | Include user ID in cache key, or avoid caching |
| Fetching the same data in multiple sibling components | Duplicated requests, inconsistent data | Fetch in the parent and pass down, or use TanStack Query (automatic deduplication) |
| Not invalidating cache after mutations | UI shows stale data after create/update/delete | `invalidateQueries()` in `onSuccess` of mutations |
| Using `fetch()` in Client Components without TanStack Query | Loses caching, deduplication, retry, background refetch | Wrap in TanStack Query — even simple fetches benefit |

---

## 7. Form Handling

Forms are the primary mechanism through which users provide input to an
application — creating accounts, submitting orders, updating settings,
filtering data. A well-designed form is invisible: the user focuses on
their task, not on fighting the interface. A poorly designed form creates
friction, frustration, and abandoned workflows.

The standard stack for forms is **react-hook-form + Zod resolver**. This
combination provides minimal re-renders, type-safe validation, and a clean
separation between form state and UI rendering.

> **Critical reminder:** Client-side validation is **UX**, not security.
> Every validation rule in the form must also exist on the server.
> → See [07-security-standards.md, Section 3 — Input Validation].
> → See [03-api-design.md, Section 6 — Input Validation].

---

### 7.1 react-hook-form + Zod Pattern

The core pattern: define a Zod schema, derive the TypeScript type, and
connect it to `react-hook-form` via the Zod resolver. The schema is the
single source of truth for both validation rules and form types.

```tsx
// 1. Schema — lives in the feature's schemas/ directory
// src/features/vehicles/schemas/vehicle-schema.ts
import { z } from 'zod';

export const createVehicleSchema = z.object({
  brand: z
    .string()
    .min(1, 'Brand is required')
    .max(100, 'Brand must not exceed 100 characters')
    .trim(),
  model: z
    .string()
    .min(1, 'Model is required')
    .max(100, 'Model must not exceed 100 characters')
    .trim(),
  year: z
    .coerce.number()
    .int('Year must be a whole number')
    .min(1900, 'Year must be 1900 or later')
    .max(new Date().getFullYear() + 1, 'Year cannot be in the future'),
  price: z
    .coerce.number()
    .positive('Price must be a positive number')
    .max(10_000_000, 'Price exceeds maximum'),
  status: z.enum(['available', 'reserved', 'sold']).default('available'),
  description: z
    .string()
    .max(2000, 'Description must not exceed 2000 characters')
    .trim()
    .optional(),
});

export type CreateVehicleInput = z.infer<typeof createVehicleSchema>;
```

```tsx
// 2. Form component — lives in the feature's components/ directory
// src/features/vehicles/components/vehicle-form.tsx
'use client';

import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { createVehicleSchema, type CreateVehicleInput } from '../schemas/vehicle-schema';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

interface VehicleFormProps {
  onSubmit: (data: CreateVehicleInput) => Promise<void>;
  defaultValues?: Partial<CreateVehicleInput>;
  isSubmitting?: boolean;
}

export function VehicleForm({ onSubmit, defaultValues, isSubmitting }: VehicleFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<CreateVehicleInput>({
    resolver: zodResolver(createVehicleSchema),
    defaultValues: {
      brand: '',
      model: '',
      status: 'available',
      ...defaultValues,
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <div>
        <Label htmlFor="brand">Brand</Label>
        <Input id="brand" {...register('brand')} aria-invalid={!!errors.brand} />
        {errors.brand && (
          <p role="alert" className="text-sm text-destructive mt-1">
            {errors.brand.message}
          </p>
        )}
      </div>

      <div>
        <Label htmlFor="year">Year</Label>
        <Input id="year" type="number" {...register('year')} aria-invalid={!!errors.year} />
        {errors.year && (
          <p role="alert" className="text-sm text-destructive mt-1">
            {errors.year.message}
          </p>
        )}
      </div>

      {/* ... other fields ... */}

      <Button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Saving...' : 'Save Vehicle'}
      </Button>
    </form>
  );
}
```

#### Rules

- **MUST** use `react-hook-form` with `@hookform/resolvers/zod` for all
  forms — do not mix validation approaches (manual `useState` validation,
  inline regex, etc.)
- **MUST** define the Zod schema in the feature's `schemas/` directory and
  derive the TypeScript type with `z.infer<typeof schema>` — never duplicate
  the type manually
- **MUST** use the same schema (or a compatible one) on the server for API
  validation — the client and server schemas should share a common base
  (→ See [03-api-design.md, Section 6.2])
- **MUST** add `noValidate` to the `<form>` element — this disables native
  browser validation, which conflicts with custom validation UX
- **MUST** add `aria-invalid` to inputs with errors and render error messages
  with `role="alert"` — this makes validation errors accessible to screen
  readers
- **SHOULD** provide `defaultValues` for every field — react-hook-form works
  best with controlled defaults, and it prevents uncontrolled-to-controlled
  warnings
- **MUST NOT** import Zod schemas directly in the component file — import
  from the schemas directory to maintain the layering boundary (component →
  schema, not component contains schema)

---

### 7.2 Form Composition

Complex forms should be broken into reusable, focused sections — not built
as a single monolithic component. Each section handles a logical group of
fields.

#### Reusable Field Components

Wrap common field patterns into reusable components that integrate with
react-hook-form:

```tsx
// src/components/forms/form-field.tsx
'use client';

import { useFormContext } from 'react-hook-form';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

interface FormFieldProps {
  name: string;
  label: string;
  type?: string;
  placeholder?: string;
  description?: string;
}

export function FormField({ name, label, type = 'text', placeholder, description }: FormFieldProps) {
  const { register, formState: { errors } } = useFormContext();
  const error = errors[name];

  return (
    <div className="space-y-1">
      <Label htmlFor={name}>{label}</Label>
      {description && (
        <p className="text-sm text-muted-foreground">{description}</p>
      )}
      <Input
        id={name}
        type={type}
        placeholder={placeholder}
        {...register(name)}
        aria-invalid={!!error}
        aria-describedby={error ? `${name}-error` : undefined}
      />
      {error && (
        <p id={`${name}-error`} role="alert" className="text-sm text-destructive">
          {error.message as string}
        </p>
      )}
    </div>
  );
}
```

#### Form Sections

Break large forms into logical sections that can be composed:

```tsx
// src/features/vehicles/components/vehicle-details-section.tsx
export function VehicleDetailsSection() {
  return (
    <fieldset className="space-y-4">
      <legend className="text-lg font-semibold">Vehicle Details</legend>
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <FormField name="brand" label="Brand" />
        <FormField name="model" label="Model" />
        <FormField name="year" label="Year" type="number" />
        <FormField name="price" label="Price" type="number" />
      </div>
    </fieldset>
  );
}

// Parent form composes sections
export function VehicleForm({ onSubmit, defaultValues }: VehicleFormProps) {
  const methods = useForm<CreateVehicleInput>({
    resolver: zodResolver(createVehicleSchema),
    defaultValues,
  });

  return (
    <FormProvider {...methods}>
      <form onSubmit={methods.handleSubmit(onSubmit)} noValidate>
        <VehicleDetailsSection />
        <VehiclePricingSection />
        <VehicleMediaSection />
        <Button type="submit">Save</Button>
      </form>
    </FormProvider>
  );
}
```

- **SHOULD** use `FormProvider` and `useFormContext()` when the form has
  multiple sections — this avoids prop-drilling the `register` and `errors`
  objects through every section
- **SHOULD** use `<fieldset>` and `<legend>` to group related fields —
  this improves both accessibility and visual structure
- **SHOULD** create reusable field components (`FormField`, `FormSelect`,
  `FormTextarea`) that encapsulate the label + input + error pattern

---

### 7.3 Validation UX

Validation should guide the user, not punish them. The goal is to help
users provide valid input with minimum friction.

#### Validation Timing

| Strategy | When | Best For |
|---|---|---|
| On submit | Errors shown after form submission | Simple forms, few fields |
| On blur (touched) | Error shown when user leaves a field | Medium forms, real-time guidance |
| On change (after touch) | Error updates as user types (after first blur) | Fields with format requirements |

- **SHOULD** use the **on-blur after first submit** strategy as the default —
  react-hook-form's `mode: 'onTouched'` or `mode: 'onBlur'` provides this:

  ```tsx
  const { ... } = useForm({
    resolver: zodResolver(schema),
    mode: 'onTouched', // Validate on blur, revalidate on change
  });
  ```

- **SHOULD** show inline errors immediately below the field, not in a
  summary at the top — users should not scroll to understand what is wrong
- **SHOULD** use positive feedback for corrected errors — when the user
  fixes a field, the error disappears immediately (react-hook-form does
  this automatically with `mode: 'onTouched'`)
- **MUST** preserve user input on validation failure — never clear the
  form when validation fails
- **MUST** focus the first field with an error after form submission fails
  — this helps the user find and fix the error quickly:

  ```tsx
  const { ... } = useForm({
    resolver: zodResolver(schema),
    shouldFocusError: true, // Default: true — focuses first error field
  });
  ```

#### Server-Side Error Integration

When the API returns validation errors (field-level errors from
→ See [03-api-design.md, Section 5]), map them back to the form:

```tsx
async function handleSubmit(data: CreateVehicleInput) {
  try {
    await vehicleService.create(data);
    toast.success('Vehicle created successfully');
    router.push('/dashboard/vehicles');
  } catch (error) {
    if (error instanceof ApiError && error.code === 'VALIDATION_ERROR' && error.fieldErrors) {
      // Map server field errors back to the form
      for (const [field, messages] of Object.entries(error.fieldErrors)) {
        form.setError(field as keyof CreateVehicleInput, {
          type: 'server',
          message: messages[0], // Show first error message
        });
      }
    } else {
      toast.error(mapApiError(error));
    }
  }
}
```

- **MUST** map API `fieldErrors` back to the form using `setError()` —
  this shows server validation errors inline, next to the relevant field
- **MUST** show non-field errors (general API errors) as toast notifications
  — not inline in the form
- **SHOULD** distinguish between client validation errors and server
  validation errors visually — both appear inline, but the user should
  understand that server errors may require different action

---

### 7.4 Multi-Step Forms

Multi-step forms (wizards) break a long form into manageable steps. Each
step validates its own subset of fields before allowing progression.

```tsx
'use client';

import { useState } from 'react';
import { useForm, FormProvider } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

// Each step has its own schema
const step1Schema = z.object({ brand: z.string().min(1), model: z.string().min(1) });
const step2Schema = z.object({ price: z.coerce.number().positive(), year: z.coerce.number() });
const step3Schema = z.object({ description: z.string().optional() });

// Full schema for final submission
const fullSchema = step1Schema.merge(step2Schema).merge(step3Schema);
type FullFormData = z.infer<typeof fullSchema>;

const steps = [
  { schema: step1Schema, component: Step1Details },
  { schema: step2Schema, component: Step2Pricing },
  { schema: step3Schema, component: Step3Description },
];

export function VehicleWizard() {
  const [currentStep, setCurrentStep] = useState(0);

  const methods = useForm<FullFormData>({
    resolver: zodResolver(fullSchema),
    mode: 'onTouched',
  });

  async function handleNext() {
    const currentStepSchema = steps[currentStep].schema;
    const fields = Object.keys(currentStepSchema.shape) as (keyof FullFormData)[];

    // Validate only the current step's fields
    const isValid = await methods.trigger(fields);
    if (isValid) setCurrentStep((prev) => prev + 1);
  }

  function handleBack() {
    setCurrentStep((prev) => prev - 1);
  }

  async function handleFinalSubmit(data: FullFormData) {
    await vehicleService.create(data);
    router.push('/dashboard/vehicles');
  }

  const StepComponent = steps[currentStep].component;

  return (
    <FormProvider {...methods}>
      <form onSubmit={methods.handleSubmit(handleFinalSubmit)} noValidate>
        {/* Progress indicator */}
        <StepIndicator current={currentStep} total={steps.length} />

        {/* Current step */}
        <StepComponent />

        {/* Navigation */}
        <div className="flex justify-between mt-6">
          {currentStep > 0 && (
            <Button type="button" variant="outline" onClick={handleBack}>Back</Button>
          )}
          {currentStep < steps.length - 1 ? (
            <Button type="button" onClick={handleNext}>Next</Button>
          ) : (
            <Button type="submit">Submit</Button>
          )}
        </div>
      </form>
    </FormProvider>
  );
}
```

#### Rules

- **MUST** validate each step independently before allowing progression —
  use `methods.trigger(fields)` to validate only the current step's fields
- **MUST** preserve data from previous steps — the `useForm` instance holds
  all values across steps
- **SHOULD** show a progress indicator (step numbers, breadcrumbs, or
  progress bar) so the user knows where they are and how much remains
- **SHOULD** allow navigating back without losing data
- **SHOULD** submit all data at the final step, not incrementally per step —
  unless the backend requires incremental saves (e.g., draft functionality)
- **MAY** use the `<Activity>` component (React 19.2) to preserve step
  component state when navigating back, instead of unmounting and remounting

---

### 7.5 Server Actions Integration

Next.js Server Actions provide a way to handle form submissions without
API routes. They run on the server and can be called directly from Client
Components.

```tsx
// src/features/vehicles/actions/create-vehicle-action.ts
'use server';

import { createVehicleSchema } from '../schemas/vehicle-schema';
import { vehicleService } from '../services/vehicle-service';
import { revalidatePath } from 'next/cache';

export async function createVehicleAction(formData: FormData) {
  const raw = Object.fromEntries(formData);
  const parsed = createVehicleSchema.safeParse(raw);

  if (!parsed.success) {
    return {
      ok: false as const,
      fieldErrors: parsed.error.flatten().fieldErrors,
    };
  }

  try {
    await vehicleService.create(parsed.data);
    revalidatePath('/dashboard/vehicles');
    return { ok: true as const };
  } catch (error) {
    return {
      ok: false as const,
      error: 'Failed to create vehicle. Please try again.',
    };
  }
}
```

```tsx
// In the form component — using useActionState (React 19)
'use client';

import { useActionState } from 'react';
import { createVehicleAction } from '../actions/create-vehicle-action';

export function VehicleFormServerAction() {
  const [state, formAction, isPending] = useActionState(createVehicleAction, null);

  return (
    <form action={formAction}>
      <div>
        <Label htmlFor="brand">Brand</Label>
        <Input id="brand" name="brand" />
        {state?.fieldErrors?.brand && (
          <p role="alert" className="text-sm text-destructive">
            {state.fieldErrors.brand[0]}
          </p>
        )}
      </div>

      {state?.error && <p className="text-destructive">{state.error}</p>}

      <Button type="submit" disabled={isPending}>
        {isPending ? 'Saving...' : 'Save Vehicle'}
      </Button>
    </form>
  );
}
```

#### When to Use Server Actions vs API Routes

| Criteria | Server Actions | API Routes |
|---|---|---|
| Simple form submission (create, update) | ✅ Preferred | Works but more boilerplate |
| Complex validation with react-hook-form | Possible but verbose | ✅ Preferred — full RHF integration |
| Consumed by external clients (mobile, third-party) | ❌ Not suitable | ✅ Required — public API contract |
| Need RESTful endpoints | ❌ Not suitable | ✅ Required |
| Progressive enhancement (works without JS) | ✅ Built-in | Requires extra work |
| File uploads | ✅ FormData native | ✅ FormData or multipart |

- **SHOULD** use Server Actions for simple form submissions where
  progressive enhancement is valuable (contact forms, newsletter signups,
  simple CRUD)
- **SHOULD** use API routes + react-hook-form for complex forms that need
  rich client-side validation UX, multi-step flows, or that serve as API
  endpoints for other consumers
- **MUST** validate input with Zod in Server Actions — never trust FormData
  directly
- **MUST** return structured results from Server Actions (not throw errors)
  — the form needs the result to display field errors or success messages

---

### 7.6 Anti-Patterns

| Anti-Pattern | Why It Is Wrong | Correct Alternative |
|---|---|---|
| `useState` for each form field | Verbose, no validation, no error tracking, excessive re-renders | react-hook-form manages all form state |
| Client-only validation (no server validation) | Security vulnerability — client validation is bypassable | Always validate on the server too (→ 03 §6, 07 §15.3) |
| Clearing the form on validation failure | User loses all input and must start over | Preserve input, show errors inline |
| Generic error at the top of the form | User must scan every field to find the problem | Inline errors below each invalid field |
| Validating on every keystroke (no debounce) | Distracting, shows errors before user finishes typing | `mode: 'onTouched'` — validate on blur, revalidate on change |
| Duplicating Zod schema in the component | Breaks single source of truth, creates drift risk | Import schema from `schemas/` directory |
| Submitting without disabling the button | Double submissions, duplicate records | Disable button while `isSubmitting` is true |
| No loading state during submission | User clicks again thinking nothing happened | Show "Saving..." or spinner on the submit button |
| Mixing react-hook-form with manual `useState` for the same fields | Two sources of truth, conflicting updates | Let react-hook-form be the single source of truth (§5.5) |
| Not mapping server `fieldErrors` back to the form | Server validation errors shown as generic toast, user cannot find the field | Use `setError()` to map errors inline (§7.3) |

---

## 8. Error Handling in UI

Errors are inevitable — APIs fail, networks drop, data is missing, users
navigate to non-existent pages, and code has bugs. The frontend's job is
not to prevent all errors (that is impossible) but to **handle every error
gracefully** so the user always knows what happened and what they can do
about it.

A well-handled error is invisible friction. A poorly handled error — a blank
screen, a cryptic message, or a frozen interface — destroys trust.

> For the error handling philosophy and custom error class hierarchy:
> → See [01-core-principles.md, Section 3.4 — Error Handling Discipline].
> For the API error response format and error codes:
> → See [03-api-design.md, Section 5 — Error Handling].
> For security considerations in error messages:
> → See [07-security-standards.md, Section 1 — Fail Secure].

---

### 8.1 Error Boundaries (React)

React Error Boundaries catch JavaScript errors during rendering, in
lifecycle methods, and in constructors of the component tree below them.
They display a fallback UI instead of a crashed component tree.

In Next.js 16, error boundaries are primarily managed through the
file-based `error.tsx` convention. For component-level control, Next.js
16.2 introduces `unstable_catchError()`.

#### How Error Boundaries Work

```text
                    ┌─────────────┐
                    │ layout.tsx  │ ← NOT caught by error.tsx in same segment
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ error.tsx   │ ← Catches errors from children below
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
        ┌─────▼─────┐ ┌────▼───┐ ┌──────▼─────┐
        │loading.tsx│ │page.tsx│ │ nested     │
        └───────────┘ └────────┘ │ layout.tsx │
                                 └────────────┘
```

Key rules of error boundary hierarchy:
- `error.tsx` catches errors from `page.tsx`, `loading.tsx`, and nested
  layouts/pages **below** it
- `error.tsx` does **NOT** catch errors from `layout.tsx` or `template.tsx`
  in the **same** segment — use `error.tsx` in the parent segment for that
- `global-error.tsx` catches errors from the root `layout.tsx` — it replaces
  the entire page, including `<html>` and `<body>`

#### What Error Boundaries Do NOT Catch

- Errors in event handlers (onClick, onChange) — catch manually with
  try/catch
- Errors in async code (setTimeout, Promises) outside of rendering — catch
  manually
- Errors in Server Components during streaming — these surface as generic
  messages in production (sensitive details stripped)

---

### 8.2 Next.js error.tsx / not-found.tsx Conventions

#### `error.tsx` — Runtime Error Boundary

```tsx
// app/(dashboard)/dashboard/error.tsx
'use client'; // REQUIRED — error boundaries must be Client Components

import type { ErrorInfo } from 'next/error';

export default function DashboardError({ error, unstable_retry }: ErrorInfo) {
  return (
    <div className="flex flex-col items-center justify-center gap-4 p-8">
      <h2 className="text-xl font-semibold">Something went wrong</h2>
      <p className="text-muted-foreground">
        {error.message || 'An unexpected error occurred.'}
      </p>
      <button
        onClick={() => unstable_retry()}
        className="rounded-md bg-primary px-4 py-2 text-primary-foreground"
      >
        Try again
      </button>
    </div>
  );
}
```

> **Next.js 16.2:** The `unstable_retry()` function replaces the older
> `reset()` prop as the preferred recovery mechanism. While `reset()` only
> clears the error state and re-renders children, `unstable_retry()` calls
> `router.refresh()` and `reset()` within a `startTransition()` — providing
> built-in retry logic that re-fetches data and re-renders the segment.
> Use `unstable_retry()` for most error recovery scenarios.

#### `not-found.tsx` — Resource Not Found

```tsx
// app/(dashboard)/dashboard/vehicles/[id]/not-found.tsx
import Link from 'next/link';

export default function VehicleNotFound() {
  return (
    <div className="flex flex-col items-center justify-center gap-4 p-8">
      <h2 className="text-xl font-semibold">Vehicle not found</h2>
      <p className="text-muted-foreground">
        The vehicle you are looking for does not exist or has been removed.
      </p>
      <Link
        href="/dashboard/vehicles"
        className="rounded-md bg-primary px-4 py-2 text-primary-foreground"
      >
        Back to vehicles
      </Link>
    </div>
  );
}
```

Triggered programmatically with `notFound()` from `next/navigation`:

```tsx
// app/(dashboard)/dashboard/vehicles/[id]/page.tsx
import { notFound } from 'next/navigation';

export default async function VehiclePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const vehicle = await vehicleService.findById(id);

  if (!vehicle) {
    notFound(); // Renders the nearest not-found.tsx
  }

  return <VehicleDetail vehicle={vehicle} />;
}
```

#### `global-error.tsx` — Root Layout Errors

```tsx
// app/global-error.tsx
'use client';

import type { ErrorInfo } from 'next/error';

export default function GlobalError({ error, unstable_retry }: ErrorInfo) {
  return (
    <html lang="en">
      <body>
        <div className="flex min-h-screen items-center justify-center">
          <div className="text-center">
            <h1 className="text-2xl font-bold">Something went wrong</h1>
            <p className="mt-2 text-muted-foreground">{error.message}</p>
            <button onClick={() => unstable_retry()} className="mt-4 underline">
              Try again
            </button>
          </div>
        </div>
      </body>
    </html>
  );
}
```

#### Component-Level Error Boundaries (Next.js 16.2)

For error boundaries at the component level (not tied to route segments),
use `unstable_catchError()`:

```tsx
// src/components/error-boundary.tsx
'use client';

import { unstable_catchError, type ErrorInfo } from 'next/error';

function FallbackUI(
  props: { title: string },
  { error, unstable_retry }: ErrorInfo,
) {
  return (
    <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4">
      <h3 className="font-semibold text-destructive">{props.title}</h3>
      <p className="text-sm text-muted-foreground">{error.message}</p>
      <button onClick={() => unstable_retry()} className="mt-2 text-sm underline">
        Try again
      </button>
    </div>
  );
}

export default unstable_catchError(FallbackUI);
```

```tsx
// Usage — wrap any component that might fail
import ErrorBoundary from '@/components/error-boundary';

export default function DashboardPage() {
  return (
    <div>
      <StatsGrid />
      <ErrorBoundary title="Failed to load recent orders">
        <RecentOrders />
      </ErrorBoundary>
      <ErrorBoundary title="Failed to load analytics">
        <AnalyticsChart />
      </ErrorBoundary>
    </div>
  );
}
```

#### Rules

- **MUST** provide `error.tsx` at the root `app/` level — this is the
  catch-all for any unhandled error in the application
- **MUST** provide `global-error.tsx` at the root `app/` level — this
  catches errors in the root layout itself
- **MUST** mark all `error.tsx` and `global-error.tsx` files with
  `'use client'` — error boundaries require client-side rendering
- **SHOULD** provide `error.tsx` at each major route group level
  (`(dashboard)/error.tsx`, `(auth)/error.tsx`) for granular error isolation
- **SHOULD** use `notFound()` for "resource not found" scenarios instead of
  letting them bubble to `error.tsx` — `not-found.tsx` provides a more
  specific and helpful UX than a generic error message
- **SHOULD** use `unstable_catchError()` to wrap individual components that
  may fail independently — this prevents one broken widget from crashing
  the entire page
- **SHOULD** use `unstable_retry()` instead of the older `reset()` for
  error recovery — it re-fetches data in addition to resetting the boundary
- **MUST NOT** expose sensitive error details to users in production — Next.js
  automatically strips server error details in production, showing only
  generic messages. The `error.digest` field can be used to correlate with
  server-side logs

---

### 8.3 Toast Notifications

Toast notifications are the appropriate mechanism for communicating
transient, non-blocking feedback to the user — operation success, operation
failure, and informational messages. Use `sonner` (the toast library
included with shadcn/ui).

#### When to Use Toasts vs Inline Errors

| Scenario | Mechanism | Why |
|---|---|---|
| Form field validation error | Inline error (below the field) | User needs to see which field is wrong |
| Form submission success | Toast | Transient confirmation, does not block the UI |
| API error (non-field) | Toast | General error not tied to a specific field |
| Background operation completed | Toast | User may not be looking at the relevant UI |
| Network connectivity lost | Banner (persistent) | Not transient — user needs to know until resolved |
| Permission denied | Toast or redirect | Depends on context — toast for actions, redirect for pages |

```tsx
// Toast usage with sonner
import { toast } from 'sonner';

// Success
toast.success('Vehicle created successfully');

// Error (from API)
toast.error(mapApiError(error));

// With action
toast('Invoice saved as draft', {
  action: {
    label: 'View',
    onClick: () => router.push(`/invoices/${id}`),
  },
});

// Promise-based (loading → success → error)
toast.promise(vehicleService.create(data), {
  loading: 'Creating vehicle...',
  success: 'Vehicle created successfully',
  error: 'Failed to create vehicle',
});
```

#### Rules

- **MUST** use toasts for transient feedback (success, error, info) — never
  use `alert()` or custom modal dialogs for simple confirmations
- **MUST** configure the `<Toaster />` component in the root layout:

  ```tsx
  // app/layout.tsx
  import { Toaster } from '@/components/ui/sonner';

  export default function RootLayout({ children }) {
    return (
      <html lang="en">
        <body>
          {children}
          <Toaster richColors position="bottom-right" />
        </body>
      </html>
    );
  }
  ```

- **SHOULD** use `toast.promise()` for async operations — it handles
  loading, success, and error states in one call
- **MUST NOT** use toasts for form validation errors — those must be inline
  (→ See [Section 7.3](#73-validation-ux))
- **SHOULD** keep toast messages concise — one sentence, actionable when
  possible

---

### 8.4 Error Mapping — API to UI

The API returns structured errors following the format in
→ See [03-api-design.md, Section 5]. The frontend must map these errors to
appropriate UI feedback.

```tsx
// src/lib/api-errors.ts

/** Error class for structured API errors */
export class ApiError extends Error {
  constructor(
    public code: string,
    message: string,
    public statusCode: number,
    public fieldErrors?: Record<string, string[]>,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/** Parse API response and throw ApiError on failure */
export async function handleApiResponse<T>(response: Response): Promise<T> {
  const json = await response.json();

  if (!json.ok) {
    throw new ApiError(
      json.error.code,
      json.error.message,
      response.status,
      json.error.fieldErrors,
    );
  }

  return json.data;
}

/** Map API error codes to user-friendly messages */
const ERROR_MESSAGES: Record<string, string> = {
  VALIDATION_ERROR: 'Please check the form for errors.',
  NOT_FOUND: 'The requested item could not be found.',
  UNAUTHORIZED: 'Your session has expired. Please log in again.',
  FORBIDDEN: 'You do not have permission to perform this action.',
  CONFLICT: 'This item has been modified. Please refresh and try again.',
  RATE_LIMITED: 'Too many requests. Please wait a moment.',
  INTERNAL_ERROR: 'An unexpected error occurred. Please try again later.',
};

export function mapApiError(error: unknown): string {
  if (error instanceof ApiError) {
    return ERROR_MESSAGES[error.code] ?? ERROR_MESSAGES.INTERNAL_ERROR;
  }
  if (error instanceof Error) {
    return error.message;
  }
  return ERROR_MESSAGES.INTERNAL_ERROR;
}
```

#### Error Handling Flow

```text
API returns error
       │
       ▼
handleApiResponse() throws ApiError
       │
       ▼
Is it a VALIDATION_ERROR with fieldErrors?
├── YES → map fieldErrors to form with setError() (→ §7.3)
└── NO  → show toast with mapApiError()
```

#### Rules

- **MUST** use `handleApiResponse()` (or equivalent) to parse all API
  responses — never access `response.json()` directly without checking `ok`
- **MUST** map API error codes to user-friendly messages — never show raw
  error codes or server error messages to users
- **MUST** handle `UNAUTHORIZED` errors by redirecting to login — not just
  showing a toast
- **SHOULD** handle `CONFLICT` errors with a "refresh and retry" flow —
  the user should not lose their work
- **MUST NOT** expose server error details (stack traces, internal messages)
  to the user — Next.js strips these in production, but the frontend should
  also not try to display `error.digest` or raw server messages

---

### 8.5 Fallback UIs

Every asynchronous operation has three states beyond success that must be
designed explicitly: loading, error, and empty.

#### Loading States (Skeletons)

Skeleton components should mirror the layout of the loaded content to
minimize Cumulative Layout Shift (CLS):

```tsx
// BAD — generic spinner, no layout hint
function Loading() {
  return <Spinner />;
}

// GOOD — skeleton that matches the loaded layout
function VehicleCardSkeleton() {
  return (
    <div className="animate-pulse rounded-lg border p-4">
      <div className="h-40 rounded-md bg-muted" />          {/* Image placeholder */}
      <div className="mt-3 h-5 w-3/4 rounded bg-muted" />   {/* Title placeholder */}
      <div className="mt-2 h-4 w-1/2 rounded bg-muted" />   {/* Subtitle placeholder */}
      <div className="mt-4 h-8 w-24 rounded bg-muted" />    {/* Button placeholder */}
    </div>
  );
}

function VehicleListSkeleton() {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: 6 }).map((_, i) => (
        <VehicleCardSkeleton key={i} />
      ))}
    </div>
  );
}
```

#### Empty States

Empty states should explain **why** the view is empty and offer a **path
forward**:

```tsx
// BAD — no explanation, no action
function EmptyState() {
  return <p>No data.</p>;
}

// GOOD — context-aware with action
function VehicleEmptyState({ hasFilters }: { hasFilters: boolean }) {
  if (hasFilters) {
    return (
      <div className="py-12 text-center">
        <p className="text-lg text-muted-foreground">No vehicles match your filters.</p>
        <button onClick={clearFilters} className="mt-4 underline">
          Clear all filters
        </button>
      </div>
    );
  }

  return (
    <div className="py-12 text-center">
      <p className="text-lg text-muted-foreground">No vehicles yet.</p>
      <Link href="/dashboard/vehicles/new" className="mt-4 inline-block underline">
        Add your first vehicle
      </Link>
    </div>
  );
}
```

#### Rules

- **MUST** handle all three fallback states (loading, error, empty) for
  every data-driven component — leaving any unhandled creates a broken UX
- **MUST** use skeleton components that match the loaded layout — not generic
  spinners that cause layout shift
- **SHOULD** distinguish between "empty because of filters" and "empty
  because no data exists" — the actions are different (clear filters vs
  create first item)
- **SHOULD** provide actionable guidance in empty states — "No vehicles yet.
  Add your first vehicle" is more helpful than "No data"
- **SHOULD** use `animate-pulse` (Tailwind) for skeleton loading animations
  — it is subtle and non-distracting

---

### 8.6 Anti-Patterns

| Anti-Pattern | Why It Is Wrong | Correct Alternative |
|---|---|---|
| Blank screen on error (no error boundary) | User thinks the app is broken with no recovery path | Add `error.tsx` at every major route group level |
| Generic spinner for all loading states | Causes layout shift (CLS), gives no hint about what is loading | Skeleton components that match the loaded layout |
| `console.error` as the only error handling | Error is logged but user sees nothing — or worse, a broken UI | Catch errors, show appropriate UI feedback (toast, error state, boundary) |
| Showing raw error messages to users | Confusing, unprofessional, potential security leak (stack traces) | Map error codes to user-friendly messages (§8.4) |
| Using `alert()` for error notification | Blocks the main thread, terrible UX, no styling control | Use toast notifications (§8.3) |
| Toast for form validation errors | User cannot find which field is wrong | Inline errors below each invalid field (→ §7.3) |
| Missing empty states | User sees an empty page and wonders if the app is broken | Dedicated empty state with explanation and call to action |
| `error.tsx` without a retry button | User is stuck with no recovery path except refreshing the page | Always include `unstable_retry()` or navigation action |
| Not handling `UNAUTHORIZED` API errors | User sees "Permission denied" toast but stays on the page | Redirect to login page on 401 responses |
| Catching and swallowing errors silently | Bugs are hidden, debugging becomes impossible | Log errors to monitoring (Sentry), show user feedback |

---

## 9. Accessibility (a11y)

Accessibility is how you ensure that every person — regardless of ability,
device, or context — can use the application. It is not a checklist to run
before launch; it is a design and development discipline that is embedded in
every component, every interaction, and every decision from the start.

> This section operationalizes the principle defined in
> → See [Section 1.4 — Accessibility Is a Requirement, Not a Feature].
> For security-related UI considerations (cookie consent banners, privacy UIs):
> → See [07-security-standards.md, Section 14 — RGPD].

---

### 9.1 Target: WCAG 2.2 Level AA

The **Web Content Accessibility Guidelines (WCAG) 2.2** is the current W3C
standard (published October 2023, reaffirmed May 2025). It is the baseline
for all projects.

- **MUST** target **WCAG 2.2 Level AA** conformance — this is the standard
  referenced by the European Accessibility Act (EAA), ADA guidance, and
  most international regulations
- **SHOULD** treat Level AAA criteria as aspirational goals — implement them
  where practical, but they are not achievable for all content types
- **MUST** understand that WCAG 2.2 is backward compatible — conforming to
  2.2 automatically satisfies 2.1 and 2.0

#### Key New Criteria in WCAG 2.2 (Level AA)

These criteria were added in WCAG 2.2 and represent the most common gaps
in existing applications:

| Criterion | Requirement | Frontend Impact |
|---|---|---|
| **2.4.11 Focus Not Obscured** | Focused element must not be entirely hidden by sticky headers, banners, or overlays | Use `scroll-margin-top` on focusable elements; manage z-index of sticky elements |
| **2.5.7 Dragging Movements** | Any drag interaction must have a non-dragging alternative (click/tap) | Provide button alternatives for drag-to-reorder, drag-to-resize |
| **2.5.8 Target Size (Minimum)** | Interactive targets must be at least **24×24 CSS pixels** (or have sufficient spacing) | Ensure buttons, links, and controls meet minimum size |
| **3.2.6 Consistent Help** | Help mechanisms (contact, chat, FAQ) must appear in the same relative position across pages | Place help elements in consistent locations in layouts |
| **3.3.7 Redundant Entry** | Do not ask users to re-enter information already provided in the same session | Auto-populate fields from previous steps; use stored data |
| **3.3.8 Accessible Authentication** | Authentication must not require cognitive function tests (puzzles, memory) | Support paste in password fields; allow password managers; provide alternatives to CAPTCHAs |

> **Note on touch targets:** WCAG 2.2 AA requires a **minimum of 24×24 CSS
> pixels**. However, the Apple Human Interface Guidelines and our own §1.3
> recommend **44×44px** as the comfortable touch target — SHOULD aim for 44px,
> MUST meet 24px.

---

### 9.2 Semantic HTML First

Semantic HTML is the foundation of accessibility. Before reaching for ARIA
attributes, use the right HTML element — it comes with built-in keyboard
behavior, screen reader support, and browser features for free.

```tsx
// BAD — div pretending to be a button
<div className="btn" onClick={handleClick}>
  Submit
</div>

// GOOD — native button with all a11y for free
<button onClick={handleClick}>
  Submit
</button>
```

| Need | Use | Not |
|---|---|---|
| Clickable action | `<button>` | `<div onClick>` or `<a onClick>` |
| Navigation | `<a href="...">` | `<button onClick={() => router.push()}>` |
| Page title | `<h1>` – `<h6>` (hierarchical) | `<div className="title">` |
| List of items | `<ul>` / `<ol>` + `<li>` | `<div>` with visual bullets |
| Form input | `<input>` with `<label>` | `<div contentEditable>` |
| Navigation region | `<nav>` | `<div className="nav">` |
| Main content | `<main>` | `<div className="content">` |
| Complementary info | `<aside>` | `<div className="sidebar">` |
| Table data | `<table>` with `<th>` | `<div>` grid with CSS |

#### Rules

- **MUST** use semantic HTML elements before ARIA — the first rule of ARIA
  is "don't use ARIA" when a native element exists
- **MUST** maintain a logical heading hierarchy (`h1` → `h2` → `h3`) —
  never skip heading levels for visual sizing. Use CSS to style headings,
  not wrong heading levels
- **MUST** use `<button>` for actions and `<a>` for navigation — never
  use `<a>` without an `href` or a `<div>` with an `onClick` as a button
- **SHOULD** use landmark elements (`<main>`, `<nav>`, `<aside>`, `<footer>`,
  `<header>`) to structure pages — screen readers use these to navigate
  between sections

---

### 9.3 Keyboard Navigation

Every interactive element must be reachable and operable with only a
keyboard. Many users cannot use a mouse — including screen reader users,
users with motor disabilities, and power users who prefer keyboard.

#### Rules

- **MUST** ensure all interactive elements are reachable via `Tab` key —
  native `<button>`, `<a>`, `<input>`, `<select>` elements are automatically
  focusable. Custom interactive elements need `tabIndex={0}`
- **MUST** ensure all actions can be triggered with `Enter` or `Space` —
  native buttons handle this automatically. Custom elements need explicit
  `onKeyDown` handlers
- **MUST** provide visible focus indicators — never add `outline: none`
  without a replacement. Tailwind provides `focus-visible:ring-2
  focus-visible:ring-ring` as a standard pattern:

  ```tsx
  <button className="focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2">
    Submit
  </button>
  ```

- **MUST** ensure focused elements are not obscured by sticky headers or
  overlays (WCAG 2.2 §2.4.11). Use `scroll-margin-top` to account for
  sticky elements:

  ```css
  /* Account for sticky header height */
  :target, :focus {
    scroll-margin-top: 5rem; /* Height of sticky header + buffer */
  }
  ```

- **MUST** support `Escape` to close modals, drawers, dropdowns, and
  popovers — shadcn/ui and Radix UI handle this automatically
- **SHOULD** implement logical tab order that follows the visual reading
  order — avoid `tabIndex` values greater than 0 (they override natural
  order and create confusion)
- **MUST NOT** create keyboard traps — the user must always be able to
  navigate away from any element using standard keyboard controls

---

### 9.4 Focus Management

Focus management is critical for dynamic content — modals, drawers,
route changes, and programmatically revealed content must direct focus
appropriately.

#### Rules

- **MUST** trap focus inside modals and drawers — the user should not be
  able to tab to elements behind the modal. Radix UI's `Dialog` component
  handles this automatically
- **MUST** return focus to the trigger element when a modal or drawer
  closes — the user should be back where they started. Radix UI handles
  this automatically
- **SHOULD** move focus to new content when it appears programmatically —
  if a button reveals a form section, focus should move to the first field
  of that section
- **SHOULD** manage focus on route changes — after navigation, focus should
  move to the main content area or the page heading. Next.js handles basic
  focus management on route transitions, but custom single-page transitions
  may need explicit management
- **SHOULD** use `aria-live` regions for content that updates dynamically
  without user interaction (notifications, status updates, real-time data):

  ```tsx
  // Announces changes to screen readers without moving focus
  <div aria-live="polite" aria-atomic="true">
    {statusMessage}
  </div>
  ```

---

### 9.5 ARIA Patterns

ARIA (Accessible Rich Internet Applications) attributes supplement semantic
HTML when native elements are insufficient — custom widgets, complex
interactions, and dynamic state changes.

#### Common Patterns

```tsx
// aria-label — labels an element when visible text is insufficient
<button aria-label="Close dialog">
  <X className="h-4 w-4" />  {/* Icon-only button needs a label */}
</button>

// aria-describedby — provides additional description
<input
  id="email"
  aria-describedby="email-help email-error"
/>
<p id="email-help" className="text-sm text-muted-foreground">
  We will never share your email.
</p>
{error && <p id="email-error" role="alert">{error}</p>}

// aria-expanded — communicates open/closed state
<button aria-expanded={isOpen} aria-controls="menu-content">
  Menu
</button>
<div id="menu-content" hidden={!isOpen}>
  ...
</div>

// aria-current — indicates current item in navigation
<nav>
  {links.map(link => (
    <a
      key={link.href}
      href={link.href}
      aria-current={pathname === link.href ? 'page' : undefined}
    >
      {link.label}
    </a>
  ))}
</nav>

// role="alert" — announces important messages immediately
{error && <p role="alert">{error}</p>}
```

#### Rules

- **MUST** provide accessible names for all interactive elements — via
  visible `<label>`, `aria-label`, or `aria-labelledby`
- **MUST** use `role="alert"` for error messages and important notifications
  that need to be announced immediately by screen readers
- **MUST** communicate state changes with ARIA attributes — `aria-expanded`,
  `aria-selected`, `aria-checked`, `aria-pressed`, `aria-disabled`
- **SHOULD** use `aria-describedby` to link inputs with their help text and
  error messages — this ensures screen readers announce the context
- **MUST NOT** use ARIA to replicate what native HTML already provides —
  `<button>` already has `role="button"`, `<a>` already has `role="link"`.
  Adding them explicitly is redundant and can cause issues
- **MUST NOT** use `aria-hidden="true"` on focusable elements — this creates
  a confusing experience where a screen reader cannot see an element the
  user can tab to

---

### 9.6 Color Contrast

Sufficient color contrast ensures text and UI elements are readable for
users with low vision, color blindness, or in challenging environments
(bright sunlight, low-quality screens).

#### WCAG 2.2 AA Contrast Requirements

| Element | Minimum Ratio | Example |
|---|---|---|
| Normal text (<18px or <14px bold) | **4.5:1** | Body text, labels, descriptions |
| Large text (≥18px or ≥14px bold) | **3:1** | Headings, large buttons |
| UI components (borders, icons, focus indicators) | **3:1** | Input borders, icon buttons, checkboxes |
| Decorative elements | No requirement | Background patterns, dividers |

#### Dark Mode Considerations

- **MUST** verify contrast ratios in **both** light and dark themes — a
  color that passes in light mode may fail in dark mode and vice versa
- **SHOULD** avoid pure white (`#fff`) on pure black (`#000`) in dark mode
  — this creates excessive contrast that causes eye strain. Use slightly
  muted values (e.g., `--foreground: oklch(0.985 0 0)` on
  `--background: oklch(0.145 0 0)`)
- **SHOULD** test color contrast during development using browser DevTools
  (Chrome's built-in contrast checker) or the axe DevTools extension

#### Rules

- **MUST** meet the minimum contrast ratios listed above for all text and
  interactive UI elements
- **MUST** never convey information using color alone — always pair color
  with another indicator (icon, text, pattern):

  ```tsx
  // BAD — color alone indicates status
  <span className={status === 'error' ? 'text-red-500' : 'text-green-500'}>
    {status}
  </span>

  // GOOD — color + icon + text
  <span className="flex items-center gap-1.5">
    {status === 'error' ? <AlertCircle className="h-4 w-4 text-destructive" /> : <Check className="h-4 w-4 text-green-600" />}
    <span>{status === 'error' ? 'Failed' : 'Completed'}</span>
  </span>
  ```

- **SHOULD** use the shadcn/ui semantic color tokens (`--destructive`,
  `--muted`, `--primary`) which are designed with sufficient contrast in
  both light and dark themes

---

### 9.7 Accessible Components (shadcn/ui + Radix UI)

shadcn/ui components are built on Radix UI primitives, which provide
accessibility out of the box — keyboard navigation, focus management, ARIA
attributes, and screen reader support. Using these components is the primary
strategy for accessible UI.

#### What Radix UI Provides Automatically

- **Dialog/Sheet/AlertDialog:** Focus trapping, focus return, `Escape` to
  close, `aria-labelledby`/`aria-describedby`, scroll lock
- **DropdownMenu/Select/Combobox:** Arrow key navigation, type-ahead,
  `aria-expanded`, `aria-selected`
- **Tabs:** Arrow key switching, `aria-selected`, `role="tablist"`/`role="tab"`
- **Tooltip:** Delayed show, keyboard activation, `role="tooltip"`,
  dismissable with `Escape`
- **Accordion:** Arrow key navigation, `aria-expanded`, `aria-controls`
- **Checkbox/Radio/Switch:** `aria-checked`, keyboard toggle with `Space`

#### Rules

- **MUST** use shadcn/ui and Radix UI as the foundation for interactive
  components — do not build custom dialogs, dropdowns, tabs, or menus from
  scratch unless there is a specific, documented reason
- **MUST** provide labels for all shadcn/ui form components — `<Label>`
  associated with inputs via `htmlFor`, or `aria-label` for icon-only inputs
- **SHOULD** verify that customizations to shadcn/ui components do not break
  the underlying Radix accessibility — if you override the component
  structure, test keyboard navigation and screen reader behavior
- **MUST NOT** override or remove ARIA attributes set by Radix UI primitives
  — they exist for a reason

---

### 9.8 Testing Accessibility

Accessibility testing should happen continuously during development, not as
a separate phase before launch.

#### Automated Testing

| Tool | What It Catches | When to Use |
|---|---|---|
| **axe DevTools** (browser extension) | ~40% of WCAG issues (contrast, labels, ARIA, landmarks) | During development — run on every page |
| **Lighthouse a11y audit** | Similar to axe, integrated in Chrome DevTools | CI and periodic audits |
| **eslint-plugin-jsx-a11y** | Missing alt text, invalid ARIA, interactive role issues | On every save (lint) |
| **@axe-core/react** | Runtime a11y violations in React DevTools console | Development mode only |

#### Manual Testing

Automated tools catch ~40% of issues. The rest require manual testing:

- **MUST** test keyboard navigation on every new interactive component —
  can you reach and operate every element with only Tab, Enter, Space,
  Escape, and Arrow keys?
- **SHOULD** test with a screen reader periodically — VoiceOver (macOS),
  NVDA (Windows, free), or Narrator (Windows, built-in). Even 10 minutes
  of screen reader testing reveals issues automated tools miss
- **SHOULD** test with zoom at 200% — does the layout break? Can the user
  still access all content?
- **SHOULD** test with the `prefers-reduced-motion` media query active —
  do animations respect it?

#### Integration with CI

- **SHOULD** run Lighthouse accessibility audits in CI with a minimum score
  threshold (target ≥ 90)
- **SHOULD** include basic accessibility checks in Playwright E2E tests
  using `@axe-core/playwright`:

  ```tsx
  import AxeBuilder from '@axe-core/playwright';

  test('dashboard has no a11y violations', async ({ page }) => {
    await page.goto('/dashboard');
    const results = await new AxeBuilder({ page }).analyze();
    expect(results.violations).toEqual([]);
  });
  ```

- **MUST** treat critical accessibility violations (missing labels, keyboard
  traps, zero-contrast text) as CI blockers — they are as serious as broken
  functionality

---

### 9.9 Anti-Patterns

| Anti-Pattern | Why It Is Wrong | Correct Alternative |
|---|---|---|
| `outline: none` without replacement focus style | Keyboard users cannot see where they are | Use `focus-visible:ring-2` — visible but only on keyboard focus |
| `<div onClick>` instead of `<button>` | No keyboard support, no screen reader announcement, no focus | Use `<button>` for actions, `<a>` for navigation |
| Missing `alt` text on informative images | Screen readers announce "image" with no context | Add descriptive `alt`; use `alt=""` for decorative images |
| Using `tabIndex > 0` | Overrides natural tab order, creates unpredictable navigation | Use `tabIndex={0}` to add to natural order, or restructure DOM |
| Autoplaying video/audio without controls | Disorienting, impossible to stop for screen reader users | Never autoplay; always provide visible controls |
| CAPTCHA without alternative | Blocks users with cognitive or visual disabilities (WCAG 2.2 §3.3.8) | Support password managers, use passkeys, provide alternatives |
| Color-only status indicators | Invisible to colorblind users (~8% of males) | Combine color with icon, text, or pattern |
| Sticky header covering focused element | Keyboard user cannot see the focused element (WCAG 2.2 §2.4.11) | Use `scroll-margin-top` to account for sticky element height |
| Drag-only interactions with no alternative | Unusable for keyboard and switch users (WCAG 2.2 §2.5.7) | Provide button-based alternative (move up/down, click to set) |
| Building custom dialogs from `<div>` | No focus trap, no focus return, no Escape to close, no ARIA | Use shadcn/ui `Dialog` (Radix UI) — accessibility built in |
| Testing a11y only before launch | Accessibility bugs are expensive to fix retroactively | Test continuously: lint, axe DevTools, manual keyboard tests |

---

## 10. Routing & Navigation

Next.js App Router uses file-system-based routing where folders and files
inside `app/` define the route structure. This section covers practical
routing patterns, the new `proxy.ts` system, and navigation UX.

> For the project structure and file conventions:
> → See [Section 2 — Project Structure].
> For authentication and authorization at the route level:
> → See [07-security-standards.md, Section 5 — Authentication].

---

### 10.1 App Router Patterns

#### Layouts

Layouts wrap child routes and persist across navigations — they do not
remount or re-render when the user navigates between pages that share
the same layout.

```tsx
// app/(dashboard)/layout.tsx — shared dashboard shell
import { Sidebar } from '@/components/layout/sidebar';
import { Header } from '@/components/layout/header';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen">
      <Sidebar />
      <div className="flex-1">
        <Header />
        <main className="p-6">{children}</main>
      </div>
    </div>
  );
}
```

- **MUST** use layouts for persistent UI (navigation, sidebar, footer)
  that should not remount on route change
- **MUST** use the root `app/layout.tsx` for providers (`ThemeProvider`,
  `QueryProvider`), global fonts, and `<html>` / `<body>` tags
- **MUST NOT** fetch per-page data in layouts — layouts persist and do
  not refetch on navigation. Data that changes per page belongs in
  `page.tsx` (→ See [Section 6.1](#61-server-components-data-fetching))
- **MAY** use `template.tsx` instead of `layout.tsx` when you need a fresh
  instance on every navigation (remounts, re-runs effects) — this is rare

#### Route Groups

Route groups `(group-name)` organize routes without affecting the URL.
Covered in detail in → See [Section 2.1](#21-nextjs-app-router-conventions).

#### Dynamic Routes

```text
app/
  (dashboard)/dashboard/
    vehicles/
      page.tsx              ← /dashboard/vehicles (list)
      [id]/
        page.tsx            ← /dashboard/vehicles/:id (detail)
        edit/
          page.tsx          ← /dashboard/vehicles/:id/edit
      new/
        page.tsx            ← /dashboard/vehicles/new (create)
```

```tsx
// app/(dashboard)/dashboard/vehicles/[id]/page.tsx
interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function VehiclePage({ params }: PageProps) {
  const { id } = await params; // Next.js 16: params is a Promise
  const vehicle = await vehicleService.findById(id);

  if (!vehicle) notFound();

  return <VehicleDetail vehicle={vehicle} />;
}
```

- **MUST** validate dynamic route parameters — treat them as untrusted
  user input (users can type anything in the URL)
- **MUST** handle the not-found case explicitly — use `notFound()` when
  a resource does not exist (→ See [Section 8.2](#82-nextjs-errortsx--not-foundtsx-conventions))
- **SHOULD** keep nesting to a maximum of 3 levels — deeply nested routes
  create complex URL structures and confusing navigation

---

### 10.2 Loading & Error Conventions

Every route segment can have its own loading and error UI. These files
create automatic `<Suspense>` and error boundaries around the segment.

| File | Purpose | Renders When |
|---|---|---|
| `loading.tsx` | Instant loading fallback | While the page is streaming/loading |
| `error.tsx` | Error boundary fallback | When an error occurs in the segment |
| `not-found.tsx` | 404 fallback | When `notFound()` is called |

```text
app/(dashboard)/dashboard/vehicles/
  layout.tsx      ← Persists during navigation
  loading.tsx     ← Shows skeleton while page loads
  error.tsx       ← Catches errors from page and children
  not-found.tsx   ← Shows when vehicle not found
  page.tsx        ← The actual page
  [id]/
    loading.tsx   ← Loading for detail page
    error.tsx     ← Error boundary for detail page
    not-found.tsx ← "Vehicle not found" for specific IDs
    page.tsx
```

- **SHOULD** provide `loading.tsx` for every route that fetches data —
  use skeleton components that match the layout of the loaded content
  (→ See [Section 8.5](#85-fallback-uis))
- **SHOULD** provide `error.tsx` at each major route group level for
  granular error isolation
- **MUST** remember that `loading.tsx` wraps the page in `<Suspense>`
  automatically — you do not need to add `<Suspense>` manually for the
  page-level loading state

---

### 10.3 Proxy Patterns (proxy.ts)

In Next.js 16, `proxy.ts` replaces `middleware.ts` as the request
interception layer. It runs before routes are rendered and is designed
for lightweight routing logic — not heavy business logic.

> **Important architectural note:** `proxy.ts` is a "thin proxy" for
> redirects, rewrites, and header manipulation. It is NOT the right place
> for database queries, complex JWT validation, or heavy authorization
> logic. Verify authentication inside Server Functions and route handlers,
> not only in the proxy.

#### Basic Pattern

```tsx
// proxy.ts (project root or src/)
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Redirect old URLs
  if (pathname.startsWith('/old-dashboard')) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  // Check for auth cookie on protected routes
  const token = request.cookies.get('auth-token');
  if (pathname.startsWith('/dashboard') && !token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  // Add custom headers
  const response = NextResponse.next();
  response.headers.set('x-pathname', pathname);
  return response;
}

export const config = {
  matcher: [
    // Match all routes except static files and API routes
    '/((?!_next/static|_next/image|favicon.ico|api/).*)',
  ],
};
```

#### What Proxy Is For

| Use Case | Example |
|---|---|
| Authentication redirects | Redirect unauthenticated users to `/login` |
| Locale detection | Redirect based on `Accept-Language` header |
| URL rewrites | Map `/blog/:slug` to an external CMS |
| A/B testing | Route percentage of traffic to different pages |
| Bot detection | Block or redirect known bad bots |
| Custom headers | Add security headers or tracking headers |
| Legacy URL redirects | Map old URLs to new routes |

#### What Proxy Is NOT For

| Anti-Pattern | Why | Alternative |
|---|---|---|
| Database queries | Too slow, proxy runs on every request | Server Components, route handlers |
| Complex JWT validation | Heavy crypto operations slow down every request | Validate in Server Functions, use cookie existence check in proxy |
| Full session management | proxy.ts runs before rendering, not during | Use auth libraries (Supabase Auth, Auth.js) in Server Components |
| Business logic | Wrong layer — proxy is infrastructure, not domain | Services layer (→ See [01-core-principles.md, Section 6]) |
| Data fetching | proxy cannot pass data to components efficiently | Fetch in Server Components or route handlers |

#### Rules

- **MUST** place `proxy.ts` at the project root (or `src/`) — not inside
  `app/`. Only one proxy file is supported per project
- **MUST** use the `matcher` config to target specific routes — without a
  matcher, the proxy runs on every request including static assets
- **MUST** keep proxy logic lightweight — return `NextResponse.next()` as
  fast as possible for unmatched routes
- **MUST** verify authentication inside Server Functions too, not only in
  the proxy — a matcher change or route refactor can silently remove proxy
  coverage
- **MUST NOT** perform database queries or heavy computation in `proxy.ts`
  — it runs before every matched request and must be fast
- **SHOULD** use the proxy for "optimistic" auth checks (cookie existence)
  and validate fully in the route handler or Server Component

---

### 10.4 Dynamic Routes & Route Parameters

Dynamic segments use the `[param]` folder convention. Next.js 16 provides
several dynamic route patterns:

| Pattern | Example | Matches |
|---|---|---|
| `[id]` | `app/vehicles/[id]/page.tsx` | `/vehicles/abc123` |
| `[...slug]` | `app/docs/[...slug]/page.tsx` | `/docs/a`, `/docs/a/b`, `/docs/a/b/c` |
| `[[...slug]]` | `app/docs/[[...slug]]/page.tsx` | `/docs`, `/docs/a`, `/docs/a/b` (optional catch-all) |

- **MUST** validate all route parameters with Zod before using them —
  route params are user-editable URL input:

  ```tsx
  const paramsSchema = z.object({
    id: z.string().uuid('Invalid ID format'),
  });

  export default async function VehiclePage({ params }: PageProps) {
    const parsed = paramsSchema.safeParse(await params);
    if (!parsed.success) notFound();

    const vehicle = await vehicleService.findById(parsed.data.id);
    if (!vehicle) notFound();

    return <VehicleDetail vehicle={vehicle} />;
  }
  ```

- **SHOULD** prefer specific routes over catch-all when the structure is
  known — `[id]/edit/page.tsx` is clearer than a catch-all that interprets
  segments

---

### 10.5 Parallel & Intercepting Routes

#### Parallel Routes

Parallel routes render multiple pages in the same layout simultaneously
using named slots (`@slot`):

```text
app/(dashboard)/dashboard/
  layout.tsx          ← Renders @analytics and @activity in parallel
  @analytics/
    page.tsx          ← Analytics panel
    loading.tsx
  @activity/
    page.tsx          ← Activity feed
    loading.tsx
  page.tsx            ← Main dashboard content
```

```tsx
// layout.tsx — receives slots as props
export default function DashboardLayout({
  children,
  analytics,
  activity,
}: {
  children: React.ReactNode;
  analytics: React.ReactNode;
  activity: React.ReactNode;
}) {
  return (
    <div className="grid grid-cols-3 gap-4">
      <div className="col-span-2">{children}</div>
      <div className="space-y-4">
        {analytics}
        {activity}
      </div>
    </div>
  );
}
```

- **MAY** use parallel routes for dashboards with independent panels that
  load at different speeds — each slot has its own `loading.tsx` and
  `error.tsx`
- **MUST** provide `default.tsx` for slots that might not have a matching
  route — this prevents 404 errors when navigating

#### Intercepting Routes

Intercepting routes allow a route to be rendered within the current
layout context (typically as a modal) when navigated to via `<Link>`,
while showing the full page when accessed directly via URL.

```text
app/(dashboard)/dashboard/vehicles/
  page.tsx                        ← Vehicle list
  [id]/
    page.tsx                      ← Full vehicle detail page (direct URL access)
  (.)vehicles/[id]/
    page.tsx                      ← Intercepted: vehicle detail as modal overlay
```

The `(.)` convention intercepts routes at the same level. Other
conventions: `(..)` one level up, `(..)(..)` two levels up, `(...)` from
root.

- **MAY** use intercepting routes for the "modal with URL" pattern — the
  user sees a modal when clicking from a list, but can share the URL
  directly and it shows a full page
- **SHOULD** only use intercepting routes when the use case clearly
  benefits from dual rendering (modal + page) — the complexity is
  significant and must be justified

---

### 10.6 Modal vs Page — Decision Guide

One of the most common frontend decisions: "Should this be a modal or a
new page?" The wrong choice creates poor UX — a complex form crammed into
a modal, or a simple confirmation that needlessly navigates away.

#### Decision Diagram

```text
Does the user need to share a direct link to this content?
│
├─ YES → Does the content need its own full layout?
│        │
│        ├─ YES → NEW PAGE
│        │
│        └─ NO  → INTERCEPTING ROUTE (modal with URL)
│
└─ NO  → Is the interaction more than 3-4 fields or actions?
          │
          ├─ YES → Is the context of the current page important?
          │        │
          │        ├─ YES → DRAWER / SLIDE-OVER (keeps context visible)
          │        │
          │        └─ NO  → NEW PAGE
          │
          └─ NO  → MODAL (quick action, minimal input)
```

#### When to Use a Modal

- **Confirmations** — "Are you sure you want to delete this vehicle?"
- **Quick actions** — status change, simple approval, single-field edit
- **Previews** — quick look at a record without navigating away
- **Simple forms** — 1–3 fields (name, email, single selection)

#### When to Use a Drawer / Slide-Over

- **Detail panels** — showing record details while keeping the list visible
- **Moderate forms** — 4–6 fields, editing properties while seeing the item
- **Filters panel** — on mobile, showing filter options as a slide-over

#### When to Use a New Page

- **Complex forms** — more than 6 fields, multi-step flows, file uploads
- **Content that deserves its own URL** — shareable, bookmarkable
- **Full-screen experiences** — editors, builders, detailed views
- **Flows with multiple steps** — wizards, checkout, onboarding

#### When to Use an Intercepting Route (Modal with URL)

- **List → Detail preview** — click a vehicle in the list, see a modal
  preview with its own URL. Direct access shows the full page
- **Social media pattern** — click a photo in a grid, see it in a modal
  overlay. Direct link shows the full photo page

#### Rules

- **MUST** choose the pattern based on content complexity and URL needs —
  not on implementation convenience
- **MUST NOT** put forms with more than 6 fields in a modal — modals
  should be quick interactions, not cramped forms
- **MUST NOT** nest modals inside modals — this creates confusing navigation
  and broken focus management. If the user action from a modal requires
  another modal, the first should close or the flow belongs on a page
- **SHOULD** use shadcn/ui `Dialog` for modals and `Sheet` for drawers —
  both handle focus trapping, Escape to close, and accessibility
- **SHOULD** close the modal on successful action and show a toast
  notification — do not keep the modal open after success

---

### 10.7 Navigation UX

#### Active States

- **MUST** indicate the current page in navigation — the user should always
  know where they are:

  ```tsx
  'use client';

  import Link from 'next/link';
  import { usePathname } from 'next/navigation';
  import { cn } from '@/lib/utils';

  export function NavLink({ href, children }: { href: string; children: React.ReactNode }) {
    const pathname = usePathname();
    const isActive = pathname === href || pathname.startsWith(`${href}/`);

    return (
      <Link
        href={href}
        className={cn(
          'text-sm transition-colors',
          isActive
            ? 'font-medium text-foreground'
            : 'text-muted-foreground hover:text-foreground',
        )}
        aria-current={isActive ? 'page' : undefined}
      >
        {children}
      </Link>
    );
  }
  ```

- **MUST** use `aria-current="page"` on the active navigation link —
  screen readers use this to announce which page the user is on

#### Prefetching

Next.js 16 automatically prefetches linked routes when `<Link>` enters the
viewport. In 16, prefetching is incremental — only missing data is
prefetched, and shared layouts are deduplicated.

- **SHOULD** use `<Link>` from `next/link` for all internal navigation —
  it provides automatic prefetching, client-side transitions, and scroll
  position restoration
- **MUST NOT** use `<a>` tags for internal navigation — this causes full
  page reloads and loses client-side state
- **MAY** disable prefetching for links that are unlikely to be clicked
  with `prefetch={false}` — this reduces unnecessary network requests on
  pages with many links

#### Programmatic Navigation

```tsx
'use client';

import { useRouter } from 'next/navigation';

export function CreateVehicleForm() {
  const router = useRouter();

  async function handleSubmit(data: CreateVehicleInput) {
    const vehicle = await vehicleService.create(data);
    router.push(`/dashboard/vehicles/${vehicle.id}`);
  }
  // ...
}
```

- **MUST** use `useRouter()` from `next/navigation` (not `next/router`)
  for programmatic navigation in Client Components
- **SHOULD** use `router.push()` for forward navigation and `router.back()`
  for going back
- **SHOULD** use `router.refresh()` to revalidate the current route's data
  after a mutation (when not using TanStack Query)

---

### 10.8 Anti-Patterns

| Anti-Pattern | Why It Is Wrong | Correct Alternative |
|---|---|---|
| `<a>` for internal navigation | Full page reload, loses state, no prefetching | Use `<Link>` from `next/link` |
| Complex forms in modals | Cramped UX, no URL to share, hard to navigate | Use a new page for 6+ field forms (§10.6) |
| Nested modals (modal opens modal) | Confusing navigation, broken focus management | Close first modal, or use a page-based flow |
| No loading states on route transitions | User sees nothing during navigation, thinks app is frozen | Add `loading.tsx` to data-fetching routes (§10.2) |
| Heavy logic in `proxy.ts` | Slows every request, wrong architectural layer | Keep proxy thin; use Server Components for logic (§10.3) |
| Deeply nested routes (4+ levels) | Complex URLs, confusing navigation, hard to maintain | Flatten with route groups or restructure |
| No active state in navigation | User does not know where they are | Use `usePathname()` + `aria-current="page"` (§10.7) |
| Using `window.location` for navigation | Full reload, bypasses Next.js router, loses state | Use `router.push()` from `next/navigation` |
| Not validating route params | URL params are user input — injection risk | Validate with Zod, use `notFound()` for invalid (§10.4) |
| Auth only in proxy.ts | Matcher changes can silently remove coverage | Always verify auth in Server Functions too (§10.3) |

---

## 11. Performance

Performance is not a feature — it is a constraint that shapes every
decision. A page that takes 4 seconds to load loses half its visitors.
A button that takes 300ms to respond feels broken. An image that causes
content to shift destroys the user's reading flow.

The goal is measurable: meet the **Core Web Vitals** thresholds that Google
uses for search ranking and that users experience as "fast."

> For the performance impact of styling and animation decisions:
> → See [Section 4.7 — Visual Design Principles] and [Section 4.5 — Dark/Light Theme].
> For data fetching performance (parallel fetching, streaming):
> → See [Section 6 — Data Fetching].

---

### 11.1 Core Web Vitals Targets

Core Web Vitals are the three metrics Google uses to measure real-world
user experience. **INP replaced FID as a Core Web Vital in March 2024.**

| Metric | Full Name | Measures | Target | Poor |
|---|---|---|---|---|
| **LCP** | Largest Contentful Paint | Loading — when the largest element becomes visible | ≤ **2.5s** | > 4.0s |
| **INP** | Interaction to Next Paint | Responsiveness — how fast the page responds to any interaction | ≤ **200ms** | > 500ms |
| **CLS** | Cumulative Layout Shift | Visual stability — how much the layout shifts during loading | ≤ **0.1** | > 0.25 |

#### Rules

- **MUST** target "Good" scores for all three Core Web Vitals on production
  pages — LCP ≤ 2.5s, INP ≤ 200ms, CLS ≤ 0.1
- **SHOULD** target a **Lighthouse Performance score ≥ 90** on mobile — this
  is the standard for the Landing Page stack baseline
  (→ See [02-technology-radar.md, Section 5.4])
- **MUST** measure performance with **real user data** (Google Search Console,
  Vercel Analytics), not only synthetic tests (Lighthouse) — lab and field
  data can differ significantly
- **SHOULD** run Lighthouse audits in CI to catch regressions before they
  reach production

---

### 11.2 Image Optimization (next/image)

Images are typically the largest elements on a page and the primary driver
of LCP. `next/image` provides automatic optimization — format conversion
(WebP/AVIF), responsive sizing, lazy loading, and layout shift prevention.

```tsx
import Image from 'next/image';

// Static import — dimensions known at build time (best for CLS)
import heroImage from '@/public/images/hero.jpg';

export function HeroSection() {
  return (
    <Image
      src={heroImage}
      alt="Dealership showroom with luxury vehicles"
      priority           // Preloads the LCP image — no lazy loading
      placeholder="blur" // Shows blurred preview while loading
      sizes="100vw"      // Full-width image
      className="object-cover"
    />
  );
}

// Remote image — explicit dimensions required
export function VehicleCard({ vehicle }: { vehicle: Vehicle }) {
  return (
    <div className="relative aspect-video">
      <Image
        src={vehicle.imageUrl}
        alt={`${vehicle.brand} ${vehicle.model}`}
        fill                             // Fills the parent container
        sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
        className="rounded-lg object-cover"
        // No priority — lazy loaded by default (not LCP element)
      />
    </div>
  );
}
```

#### Rules

- **MUST** use `next/image` for all images — never use a raw `<img>` tag
  in Next.js projects
- **MUST** add `priority` to the **LCP image** on each page (typically the
  hero image or the first large visual) — this disables lazy loading and
  preloads the image
- **MUST** provide `alt` text for all informative images — empty `alt=""`
  for decorative images (→ See [Section 9.2](#92-semantic-html-first))
- **MUST** provide `width` and `height` (or use `fill` with a sized parent
  container) — this prevents CLS by reserving space before the image loads
- **MUST** provide a `sizes` attribute on responsive images — without it,
  the browser cannot select the correct source from the srcset, potentially
  downloading a larger image than needed
- **SHOULD** use static imports for local images — Next.js extracts
  dimensions automatically, eliminating CLS risk
- **SHOULD** configure `remotePatterns` in `next.config.ts` for external
  image domains instead of using the deprecated `domains` option
- **MUST NOT** add `priority` to every image — only the LCP element. Over-
  prioritizing defeats the purpose and slows everything down

---

### 11.3 Code Splitting & Lazy Loading

Next.js automatically code-splits at the route level (each page is its own
bundle). For further optimization, use `next/dynamic` to lazy-load heavy
components that are not needed immediately.

```tsx
import dynamic from 'next/dynamic';

// Lazy load a heavy component — not rendered during initial page load
const RichTextEditor = dynamic(() => import('@/components/rich-text-editor'), {
  loading: () => <EditorSkeleton />,
  ssr: false, // Skip SSR for browser-only components
});

// Lazy load a chart library — only loaded when the tab is active
const AnalyticsChart = dynamic(() => import('@/features/analytics/components/chart'), {
  loading: () => <ChartSkeleton />,
});
```

#### Rules

- **SHOULD** use `next/dynamic` for components that are below the fold,
  behind tabs, or in modals — they do not need to load with the initial
  page
- **SHOULD** use `ssr: false` for components that use browser-only APIs
  (canvas, WebGL, certain chart libraries) — this prevents SSR errors and
  reduces server rendering time
- **SHOULD** provide a `loading` component that matches the loaded
  component's layout — this prevents CLS
- **MUST NOT** lazy load components that are critical for the initial
  viewport (above the fold) — they should load with the page

---

### 11.4 Bundle Analysis & Performance Budgets

Understanding what is in your JavaScript bundle is the first step to
keeping it small.

#### Bundle Analysis

Next.js 16.1 includes an experimental Bundle Analyzer:

```bash
# Next.js 16.1+ built-in analyzer
npx next build --analyze

# Alternative: @next/bundle-analyzer
npm install @next/bundle-analyzer
```

- **SHOULD** run bundle analysis after adding new dependencies — check that
  the dependency does not disproportionately increase bundle size
- **SHOULD** use [bundlephobia.com](https://bundlephobia.com) to check
  package sizes **before** installing
  (→ See [01-core-principles.md, Section 10 — Dependency Management])

#### Performance Budgets

| Metric | Budget | Why |
|---|---|---|
| First Load JS (per route) | ≤ **150 KB** gzipped | Beyond this, parse + execute time impacts INP on mobile |
| Total page weight | ≤ **1 MB** (initial load) | Network cost on 3G connections |
| Number of requests | ≤ **50** (initial load) | Connection limits and waterfall cost |
| Third-party JS | ≤ **50 KB** gzipped | Analytics, chat, ads — each one costs INP |

- **SHOULD** define performance budgets per project and check them in CI
- **SHOULD** review the `First Load JS` column in the Next.js build output
  for every route — it shows how much JavaScript each page ships
- **MUST** investigate any route that ships more than 200 KB First Load JS
  — there is likely an unnecessary dependency or a missing code split

---

### 11.5 Memoization — Only When Measured

React 19.2 ships with the **React Compiler** (stable in Next.js 16), which
automatically memoizes components and hooks at build time. This
fundamentally changes the guidance around manual memoization.

#### With React Compiler Enabled

```tsx
// next.config.ts
const nextConfig = {
  reactCompiler: true, // Stable in Next.js 16
};
```

When enabled, the React Compiler analyzes components at build time and
automatically inserts `React.memo`, `useMemo`, and `useCallback` where
beneficial. This means:

- **SHOULD NOT** add `React.memo`, `useMemo`, or `useCallback` manually in
  new code when the React Compiler is enabled — the compiler does this
  better and more consistently
- **MAY** keep existing manual memoization — it does not conflict with the
  compiler, but the compiler may optimize it further or make it redundant
- **SHOULD** install `eslint-plugin-react-compiler` to catch patterns that
  prevent the compiler from optimizing (e.g., mutating objects in render)

#### Without React Compiler (or for specific optimization)

If the React Compiler is not enabled, or for targeted performance
optimization of specific hot paths:

- **MUST** measure before memoizing — use React DevTools Profiler or
  Chrome Performance panel to identify actual re-render bottlenecks
- **SHOULD** use `useMemo` for expensive computations that would re-run on
  every render with the same inputs
- **SHOULD** use `useCallback` for callback props passed to memoized child
  components — otherwise the child re-renders on every parent render
- **MUST NOT** wrap every value in `useMemo` and every function in
  `useCallback` "just in case" — premature memoization adds complexity,
  memory overhead, and can actually hurt performance by preventing garbage
  collection

> **Key insight:** The React Compiler makes manual memoization a
> last-resort optimization tool rather than a routine practice. Focus on
> component design (keeping components small, pushing `'use client'`
> boundaries down) rather than sprinkling `useMemo` everywhere.

---

### 11.6 Font Optimization (next/font)

Font loading is a common source of CLS (layout shift) and LCP delay.
`next/font` solves this by self-hosting fonts, generating optimal fallback
metrics, and eliminating external network requests to Google Fonts.

```tsx
// app/layout.tsx
import { Inter } from 'next/font/google';
import localFont from 'next/font/local';

// Google Font — auto-optimized and self-hosted
const sans = Inter({
  subsets: ['latin'],
  display: 'swap',     // Shows fallback font immediately, swaps when loaded
  variable: '--font-sans',
});

// Local font — for custom or licensed fonts
const display = localFont({
  src: './fonts/CalSans-SemiBold.woff2',
  display: 'swap',
  variable: '--font-display',
});

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${sans.variable} ${display.variable}`}>
      <body className="font-sans">{children}</body>
    </html>
  );
}
```

#### Rules

- **MUST** use `next/font` for all fonts — it self-hosts, generates optimal
  fallback metrics, and prevents FOUT/FOIT
- **MUST** use `display: 'swap'` — this shows text immediately with a
  fallback font, then swaps to the custom font when loaded. Never let text
  be invisible during font load
- **MUST** define font CSS variables (`--font-sans`, `--font-display`) and
  reference them in `@theme` (→ See [Section 4.2](#42-design-tokens--css-variables))
- **SHOULD** load only the subsets needed — `subsets: ['latin']` is smaller
  than loading all character sets
- **MUST NOT** load fonts via `<link>` tags in `<head>` — this creates
  external network requests to Google Fonts, adds latency, and loses the
  optimization benefits of `next/font`

---

### 11.7 Third-Party Scripts (next/script)

Third-party scripts (analytics, chat widgets, ad pixels) are a common
source of INP degradation — they compete with your application for main
thread time.

```tsx
import Script from 'next/script';

// Analytics — load after the page is interactive
<Script
  src="https://www.googletagmanager.com/gtag/js?id=GA_ID"
  strategy="afterInteractive"
/>

// Chat widget — load when idle (lowest priority)
<Script
  src="https://chat-widget.example.com/widget.js"
  strategy="lazyOnload"
/>

// Critical inline script — load before interactive (rare)
<Script id="theme-check" strategy="beforeInteractive">
  {`document.documentElement.classList.toggle('dark', 
    localStorage.getItem('theme') === 'dark')`}
</Script>
```

| Strategy | When It Loads | Use For |
|---|---|---|
| `beforeInteractive` | Before page is interactive | Critical: theme detection, polyfills |
| `afterInteractive` | After page is interactive (default) | Analytics, monitoring |
| `lazyOnload` | When browser is idle | Chat widgets, social media embeds, ad pixels |
| `worker` (experimental) | In a web worker | Heavy scripts that should not block main thread |

#### Rules

- **MUST** use `next/script` for all third-party scripts — never add
  `<script>` tags directly to `<head>` or `<body>`
- **MUST** use `strategy="lazyOnload"` for non-essential scripts (chat,
  social, ads) — these should never compete with your application for
  main thread time
- **SHOULD** audit third-party scripts quarterly — measure their INP
  impact and remove scripts that are no longer needed
- **SHOULD** limit total third-party JS to ≤ 50 KB gzipped — each script
  added increases the performance tax on every page load

---

### 11.8 Anti-Patterns

| Anti-Pattern | Why It Is Wrong | Correct Alternative |
|---|---|---|
| Raw `<img>` tags | No optimization, no responsive sizes, no lazy loading, CLS risk | Use `next/image` with proper `sizes` and dimensions (§11.2) |
| `priority` on every image | Over-prioritizes, slows down the actual LCP image | Only add `priority` to the LCP element on each page |
| Manual `React.memo` everywhere | Premature optimization, adds complexity, may hurt GC | Enable React Compiler; memoize only measured bottlenecks (§11.5) |
| Loading fonts via `<link>` to Google Fonts | External request, FOUT/FOIT, CLS, no fallback metrics | Use `next/font` for self-hosting and automatic optimization (§11.6) |
| Third-party scripts loaded synchronously | Blocks rendering, delays interactivity, kills INP | Use `next/script` with `lazyOnload` strategy (§11.7) |
| No `sizes` attribute on responsive images | Browser downloads the largest image variant regardless of viewport | Always provide `sizes` matching your responsive layout |
| Large client-side bundles (>200 KB per route) | Slow parse + execute on mobile, bad INP on first interaction | Code split with `next/dynamic`, move logic to Server Components |
| Animating layout properties (width, height, top) | Triggers reflow, jank, dropped frames | Animate `transform` and `opacity` only (§4.7) |
| No performance measurement | Cannot improve what you do not measure | Lighthouse in CI, Vercel Analytics in production, Web Vitals monitoring |
| Adding dependencies without checking bundle size | "Just one more package" compounds into massive bundles | Check bundlephobia.com before installing (→ 01 §10) |

---

## 12. SEO & AI Discoverability (GEO)

> **Applicability note:** Sections 12–13 apply primarily to **public-facing
> sites** (marketing, e-commerce, content, client projects with SEO needs).
> For internal dashboards, admin panels, or private applications, these
> sections **MAY** be skipped entirely.

Search engine optimization and AI discoverability are two sides of the same
coin: making content findable. Traditional SEO optimizes for ranking in
search engine results pages (SERPs). Generative Engine Optimization (GEO)
optimizes for being cited in AI-generated answers from ChatGPT, Gemini,
Perplexity, Claude, and Google AI Overviews.

The good news: the technical foundations overlap significantly. Server-rendered
content, semantic HTML, structured data, fast performance, and clear content
structure benefit both. GEO adds specific requirements around content
extractability, citation-friendliness, and AI crawler access.

> For SEO/analytics tooling choices:
> → See [02-technology-radar.md, Section 3.22 — SEO & Analytics].

---

### 12.1 SEO Fundamentals (Traditional)

#### `generateMetadata` in Next.js

Every page MUST have unique, descriptive metadata. Next.js provides two
approaches: static `metadata` export and dynamic `generateMetadata` function.

```tsx
// Static metadata — for pages with known content
// app/(marketing)/about/page.tsx
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'About Us | AutoElite',
  description: 'Learn about AutoElite, the trusted dealership in Lisbon since 2010.',
  alternates: {
    canonical: '/about',
  },
  openGraph: {
    title: 'About Us | AutoElite',
    description: 'Learn about AutoElite, the trusted dealership in Lisbon since 2010.',
    url: '/about',
    type: 'website',
    images: [{ url: '/images/og-about.jpg', width: 1200, height: 630 }],
  },
};
```

```tsx
// Dynamic metadata — for pages with data-driven content
// app/(marketing)/vehicles/[id]/page.tsx
import type { Metadata } from 'next';

export async function generateMetadata(
  { params }: { params: Promise<{ id: string }> },
): Promise<Metadata> {
  const { id } = await params;
  const vehicle = await vehicleService.findById(id);
  if (!vehicle) return { title: 'Vehicle Not Found' };

  const title = `${vehicle.brand} ${vehicle.model} ${vehicle.year} | AutoElite`;
  const description = `Buy a ${vehicle.brand} ${vehicle.model} (${vehicle.year}) for €${vehicle.price.toLocaleString()}. Available at AutoElite.`;

  return {
    title,
    description,
    alternates: { canonical: `/vehicles/${id}` },
    openGraph: {
      title,
      description,
      url: `/vehicles/${id}`,
      type: 'website',
      images: vehicle.images.length > 0
        ? [{ url: vehicle.images[0], width: 1200, height: 630 }]
        : [],
    },
  };
}
```

#### `sitemap.ts` and `robots.ts`

```tsx
// app/sitemap.ts — dynamic sitemap generation
import type { MetadataRoute } from 'next';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL!;

  // Static pages
  const staticPages: MetadataRoute.Sitemap = [
    { url: baseUrl, lastModified: new Date(), changeFrequency: 'monthly', priority: 1.0 },
    { url: `${baseUrl}/about`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.8 },
    { url: `${baseUrl}/contact`, lastModified: new Date(), changeFrequency: 'monthly', priority: 0.7 },
  ];

  // Dynamic pages — from database
  const vehicles = await vehicleService.listAll();
  const vehiclePages: MetadataRoute.Sitemap = vehicles.map((v) => ({
    url: `${baseUrl}/vehicles/${v.id}`,
    lastModified: v.updatedAt,
    changeFrequency: 'weekly' as const,
    priority: 0.6,
  }));

  return [...staticPages, ...vehiclePages];
}
```

```tsx
// app/robots.ts — dynamic robots.txt
import type { MetadataRoute } from 'next';

export default function robots(): MetadataRoute.Robots {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL!;

  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        disallow: ['/dashboard/', '/api/private/', '/admin/'],
      },
    ],
    sitemap: `${baseUrl}/sitemap.xml`,
  };
}
```

#### Open Graph & Twitter Card Metadata

- **MUST** include Open Graph metadata (`og:title`, `og:description`,
  `og:image`, `og:url`) on every public page — this controls how links
  appear when shared on social media, messaging apps, and AI tools
- **SHOULD** include Twitter Card metadata (`twitter:card`,
  `twitter:title`, `twitter:description`) — set `twitter:card` to
  `summary_large_image` for pages with hero images
- **MUST** use images at least **1200×630px** for Open Graph — this is the
  recommended size for high-quality previews across platforms

#### Canonical URLs

- **MUST** set canonical URLs on every page using
  `alternates.canonical` — this prevents duplicate content issues from
  query parameters, trailing slashes, or www vs non-www
- **MUST NOT** hardcode the domain in canonical URLs — use an environment
  variable (`NEXT_PUBLIC_SITE_URL`)

#### Semantic HTML for SEO

- **MUST** use one `<h1>` per page — it defines the page's primary topic
  for search engines
- **MUST** maintain a logical heading hierarchy (h1 → h2 → h3) — do not
  skip levels (→ See [Section 9.2](#92-semantic-html-first))
- **SHOULD** use descriptive link text — "View all vehicles" instead of
  "Click here"
- **SHOULD** provide meaningful `alt` text on images — especially on
  product/service pages where image search drives traffic

#### Rules

- **MUST** implement `generateMetadata` or static `metadata` on every
  public-facing page — pages without metadata are invisible to search
  engines
- **MUST** create `sitemap.ts` and `robots.ts` in the `app/` directory —
  dynamic generation ensures they stay in sync with the application
- **MUST NOT** hardcode domain names, company names, or URLs in metadata
  templates — use environment variables and configuration
- **SHOULD** validate metadata using Google's Rich Results Test and
  social media debuggers (Facebook Sharing Debugger, Twitter Card Validator)

---

### 12.2 Structured Data (JSON-LD)

Structured data (Schema.org markup in JSON-LD format) helps search engines
and AI systems understand the entities, relationships, and context of your
content. It is the bridge between human-readable content and machine-
readable meaning.

#### Implementation Pattern

```tsx
// src/components/seo/json-ld.tsx
interface JsonLdProps {
  data: Record<string, unknown>;
}

export function JsonLd({ data }: JsonLdProps) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{ __html: JSON.stringify(data) }}
    />
  );
}

// Usage in a page
export default async function VehiclePage({ params }: PageProps) {
  const vehicle = await vehicleService.findById((await params).id);

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: `${vehicle.brand} ${vehicle.model}`,
    description: vehicle.description,
    image: vehicle.images,
    offers: {
      '@type': 'Offer',
      price: vehicle.price,
      priceCurrency: 'EUR',
      availability: vehicle.status === 'available'
        ? 'https://schema.org/InStock'
        : 'https://schema.org/SoldOut',
    },
    brand: {
      '@type': 'Brand',
      name: vehicle.brand,
    },
  };

  return (
    <>
      <JsonLd data={jsonLd} />
      <VehicleDetail vehicle={vehicle} />
    </>
  );
}
```

#### Common Schema Types by Project

| Project Type | Recommended Schema Types |
|---|---|
| **Car dealership** | `Product`, `Offer`, `Organization`, `LocalBusiness`, `BreadcrumbList`, `FAQPage` |
| **Distribution company** | `Organization`, `Product`, `Service`, `ContactPoint`, `BreadcrumbList` |
| **SaaS application** | `SoftwareApplication`, `Organization`, `FAQPage`, `HowTo`, `Article` |
| **Blog / content site** | `Article`, `BlogPosting`, `Person` (author), `BreadcrumbList`, `FAQPage` |
| **Portfolio / agency** | `Organization`, `Person`, `Service`, `WebPage`, `BreadcrumbList` |

#### Organization Schema (every project)

```tsx
// app/layout.tsx — add to root layout
const organizationJsonLd = {
  '@context': 'https://schema.org',
  '@type': 'Organization',  // or 'LocalBusiness' for physical businesses
  '@id': `${process.env.NEXT_PUBLIC_SITE_URL}/#organization`,
  name: process.env.NEXT_PUBLIC_COMPANY_NAME,
  url: process.env.NEXT_PUBLIC_SITE_URL,
  logo: `${process.env.NEXT_PUBLIC_SITE_URL}/images/logo.png`,
  sameAs: [
    'https://www.facebook.com/company',
    'https://www.instagram.com/company',
    'https://www.linkedin.com/company/company',
  ],
  contactPoint: {
    '@type': 'ContactPoint',
    telephone: '+351-XXX-XXX-XXX',
    contactType: 'customer service',
    availableLanguage: ['Portuguese', 'English'],
  },
};
```

#### Rules

- **MUST** use JSON-LD format for structured data — it is the format
  recommended by Google and preferred by AI systems for extraction
- **MUST** include `Organization` or `LocalBusiness` schema on the root
  layout — this establishes the entity identity for the entire site
- **SHOULD** add `Product`, `Article`, `FAQPage`, or `Service` schema on
  relevant content pages — each schema type enhances a specific kind of
  search result
- **SHOULD** use `@id` and `sameAs` properties to connect entities across
  the site and to external platforms — AI systems use these to build a
  coherent entity graph
- **SHOULD** include `BreadcrumbList` schema on pages with navigation
  breadcrumbs — it helps search engines and AI understand site hierarchy
- **MUST** validate structured data using Google's Rich Results Test
  (https://search.google.com/test/rich-results) and Schema Markup Validator
  (https://validator.schema.org)
- **MUST NOT** add structured data that does not match the visible content
  on the page — this is considered spam by search engines

---

### 12.3 Generative Engine Optimization (GEO)

GEO is the practice of optimizing content so that AI platforms (ChatGPT,
Gemini, Perplexity, Claude, Google AI Overviews) cite, recommend, or
mention your brand when users ask questions.

> **Why this matters:** AI search traffic grew 527% year-over-year between
> 2024 and 2025. When someone asks an AI "What is the best car dealership
> in Lisbon?", the answer is synthesized from multiple web sources. If your
> content is not structured for AI extraction, you are invisible in this
> growing channel.

#### Technical Optimizations (What We Control as Developers)

##### `llms.txt` — AI Crawler Guide

`llms.txt` is an emerging standard file (similar to `robots.txt`) that
guides AI crawlers through your site's content structure:

```text
# llms.txt — placed in public/ or served via route handler
# Company: AutoElite
# Description: Premium used car dealership in Lisbon, Portugal.
# Updated: 2026-03-24

## Main Pages
- /: Homepage — overview of available vehicles and services
- /about: Company history, team, and certifications
- /vehicles: Full inventory with filters and search
- /services: Vehicle maintenance, financing, and trade-in
- /contact: Location, hours, and contact form

## Content
- /blog: Articles about car buying tips, maintenance guides, market trends

## API Documentation
- /api/docs: Public API documentation (if applicable)
```

```tsx
// Alternative: serve llms.txt dynamically via route handler
// app/llms.txt/route.ts
export async function GET() {
  const content = `# llms.txt
# Company: ${process.env.NEXT_PUBLIC_COMPANY_NAME}
# ...
`;
  return new Response(content, {
    headers: { 'Content-Type': 'text/plain' },
  });
}
```

##### AI Crawler Access

- **MUST** audit `robots.txt` to ensure AI crawlers are not blocked —
  check for rules that might inadvertently block `ChatGPT-User`,
  `Googlebot`, `PerplexityBot`, `ClaudeBot`, `Bytespider` (TikTok/Doubao)
- **MUST** ensure primary content is server-side rendered — AI crawlers
  typically do not execute JavaScript. Content hidden behind client-side
  rendering is invisible to AI systems
  (→ See [Section 1.5 — Progressive Enhancement])
- **SHOULD** check CDN/WAF settings (Cloudflare, Vercel) — some services
  block AI bots by default. Verify that legitimate AI crawlers are allowed
- **SHOULD** not gate public content behind login walls, cookie consents
  that block rendering, or interstitial pages — AI crawlers cannot navigate
  these

##### Machine-Consumable Page Architecture

- **MUST** use semantic HTML with clear heading hierarchy — AI systems use
  headings to understand content structure and extract relevant sections
- **SHOULD** provide direct answers early in the content (TLDR-first) —
  AI systems prioritize the first 200 words when evaluating relevance
- **SHOULD** structure FAQ content using `<details>` / `<summary>` elements
  AND `FAQPage` JSON-LD schema — this makes questions and answers
  extractable by both search engines and AI
- **SHOULD** include `dateModified` in `Article` schema and visible
  timestamps on content pages — AI systems aggressively deprioritize stale
  content

##### Content SSR Requirement

```tsx
// BAD — content only renders after JS loads and API call completes
'use client';
export default function VehiclePage() {
  const { data } = useQuery({ queryKey: ['vehicle', id], queryFn: ... });
  if (!data) return <Loading />;
  return <VehicleDetail vehicle={data} />;
}

// GOOD — content in the initial HTML, visible to crawlers
export default async function VehiclePage({ params }: PageProps) {
  const vehicle = await vehicleService.findById((await params).id);
  return <VehicleDetail vehicle={vehicle} />;  // HTML includes real content
}
```

#### Rules

- **MUST** serve public content as server-rendered HTML — AI systems and
  search engines see the HTML, not the JavaScript output
- **SHOULD** create an `llms.txt` file for projects with public-facing
  content — it costs minutes to set up and helps AI crawlers navigate
  the site
- **SHOULD** update `llms.txt` whenever the site structure changes
  significantly
- **SHOULD** monitor AI crawler access in server logs — look for
  `ChatGPT-User`, `PerplexityBot`, `ClaudeBot` user agents to verify
  they can reach your content

---

### 12.4 GEO Content Awareness (For Client Guidance)

These practices are primarily content and marketing decisions, not code.
However, as developers, we should understand them to advise clients and
make architectural choices that support AI discoverability.

#### TLDR-First Content Structure

AI systems evaluate the opening content of a page first. The primary answer
to the page's topic should appear in the first 200 words — not after a
lengthy introduction.

#### Headers as Questions

AI systems pattern-match headers to user queries. A header "What Does
Vehicle Inspection Include?" is more likely to be cited for the query
"what does vehicle inspection include" than a header "Our Inspection
Process."

#### Original Data & Statistics

Content with specific, citable data (benchmarks, case studies, statistics)
is significantly more likely to be cited by AI systems than generic
statements. A statement "Our dealership has sold 1,200 vehicles since 2015"
is more citable than "We are an experienced dealership."

#### E-E-A-T Alignment

Google's Experience, Expertise, Authoritativeness, and Trust guidelines
influence both traditional SEO and AI citation. For developer teams,
this means:
- Author pages with `Person` schema linked to articles
- Real company information (`Organization`/`LocalBusiness` schema)
- Visible timestamps and update dates on content
- Clear source attribution when citing data

#### Earned Media & Third-Party Mentions

AI systems strongly favor earned media (mentions on authoritative third-party
sites) over self-published content. This is a marketing concern, but
developers can support it with:
- Clean, shareable URL structures
- Proper Open Graph metadata for link previews
- Embeddable content (well-structured blog posts, infographics)

---

### 12.5 Measuring AI Visibility

AI visibility measurement is an evolving field. Unlike traditional SEO
with established tools and metrics, AI citation tracking is still maturing.

#### Manual Testing

- **SHOULD** test target queries in ChatGPT, Gemini, Perplexity, and
  Claude periodically — ask questions a potential customer would ask and
  check if your brand is cited
- **SHOULD** document which queries cite your brand and which do not —
  this forms a baseline for improvement

#### Analytics

- **SHOULD** track AI referral traffic in analytics — GA4 shows traffic
  from `chatgpt.com`, `perplexity.ai`, `gemini.google.com` as referral
  sources
- **SHOULD** monitor server logs for AI crawler user agents to verify
  content is being accessed

#### Tools (Awareness)

The GEO tooling ecosystem is rapidly evolving. As of 2026, dedicated
tools include SE Ranking, Otterly AI, Peec AI, and Semrush Enterprise AIO
for tracking AI brand mentions across platforms. Evaluate these as needs
grow.

---

### 12.6 UTM Parameters — Tracking Guide

UTM (Urchin Tracking Module) parameters are query string tags that track
where traffic comes from, enabling attribution of users to specific
campaigns, channels, and content pieces. They are essential for measuring
the effectiveness of marketing efforts on freelance client projects.

#### The 5 Standard UTM Parameters

| Parameter | Required | Purpose | Example |
|---|---|---|---|
| `utm_source` | ✅ | **Where** the traffic comes from | `google`, `facebook`, `newsletter`, `partner-site` |
| `utm_medium` | ✅ | **How** the traffic arrives | `cpc`, `email`, `social`, `referral`, `qr-code` |
| `utm_campaign` | ✅ | **Which** campaign or promotion | `summer-sale-2026`, `vehicle-launch-bmw-x3` |
| `utm_term` | Optional | Paid search keyword | `used-cars-lisbon`, `bmw-financing` |
| `utm_content` | Optional | Differentiates variations (A/B) | `hero-cta`, `sidebar-banner`, `footer-link` |

#### Naming Convention

- **MUST** use **lowercase** for all UTM values — analytics tools are
  case-sensitive: `Facebook` and `facebook` are tracked as separate sources
- **MUST** use **hyphens** (`-`) as word separators — not underscores,
  spaces, or camelCase: `summer-sale-2026` not `summer_sale_2026`
- **MUST** be **consistent** across all campaigns — establish a naming
  taxonomy and document it. Inconsistency fragments the data

#### Standard Values by Channel

| Channel | `utm_source` | `utm_medium` | Example `utm_campaign` |
|---|---|---|---|
| Google Ads | `google` | `cpc` | `brand-awareness-q2-2026` |
| Facebook / Instagram Ads | `facebook` or `instagram` | `paid-social` | `vehicle-promo-march` |
| Email newsletter | `newsletter` | `email` | `weekly-digest-w12` |
| LinkedIn organic post | `linkedin` | `social` | `new-inventory-announcement` |
| QR code (print flyer) | `flyer-lisbon` | `qr-code` | `showroom-visit-march-2026` |
| Partner website | `partner-name` | `referral` | `dealer-network-promo` |
| SMS campaign | `sms` | `sms` | `service-reminder-march` |

#### When to Use UTMs

| Scenario | Use UTMs? | Why |
|---|---|---|
| Link in email campaign | ✅ | Track which email drove the visit |
| Link in social media post | ✅ | Distinguish organic social from paid |
| Link in paid advertising | ✅ | Required for campaign attribution |
| QR code on printed material | ✅ | Track offline-to-online conversion |
| Link in partner/referral sites | ✅ | Track which partners drive traffic |
| Internal navigation links | ❌ | Pollutes analytics, breaks session tracking |
| Links within the same site | ❌ | Internal links do not need source tracking |
| Organic search results | ❌ | Analytics tracks these automatically |

#### Implementation in Next.js

```tsx
// Preserve UTMs across navigation — store on first visit
// src/hooks/use-utm-tracking.ts
'use client';

import { useSearchParams } from 'next/navigation';
import { useEffect } from 'react';

const UTM_PARAMS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content'];

export function useUtmTracking() {
  const searchParams = useSearchParams();

  useEffect(() => {
    const utms: Record<string, string> = {};
    let hasUtm = false;

    for (const param of UTM_PARAMS) {
      const value = searchParams.get(param);
      if (value) {
        utms[param] = value;
        hasUtm = true;
      }
    }

    // Store on first touch — do not overwrite existing UTMs (first-touch attribution)
    if (hasUtm && !sessionStorage.getItem('utm_params')) {
      sessionStorage.setItem('utm_params', JSON.stringify(utms));
    }
  }, [searchParams]);
}

// Retrieve stored UTMs for form submissions or API calls
export function getStoredUtms(): Record<string, string> {
  try {
    const stored = sessionStorage.getItem('utm_params');
    return stored ? JSON.parse(stored) : {};
  } catch {
    return {};
  }
}
```

#### Rules

- **MUST** use UTM parameters on all external links that drive traffic to
  the site — emails, social media, ads, partner links, QR codes
- **MUST** follow the naming convention (lowercase, hyphens, consistent
  taxonomy) — inconsistency makes analytics data unreliable
- **MUST NOT** use UTM parameters on internal links — they reset the
  referral source and break session attribution in analytics
- **MUST NOT** use UTM parameters on links that appear in SEO-indexed
  pages — search engines may index the UTM variant as a separate URL,
  causing duplicate content. Use `canonical` URLs to mitigate if needed
- **SHOULD** store UTM parameters on first visit and attach them to form
  submissions or lead generation events — this enables attribution of
  conversions back to the original source
- **SHOULD** strip UTM parameters from the URL after capture (for cleaner
  UX) using `router.replace()` with the parameters removed — but only
  after storing them
- **SHOULD** document the UTM naming taxonomy for each project so that
  marketing and development teams use consistent values

---

### 12.7 Anti-Patterns

| Anti-Pattern | Why It Is Wrong | Correct Alternative |
|---|---|---|
| No metadata on public pages | Invisible to search engines and AI | `generateMetadata` on every public page (§12.1) |
| Hardcoded domain in metadata | Breaks in staging/preview environments | Use `NEXT_PUBLIC_SITE_URL` environment variable |
| Client-rendered public content | AI crawlers and search engines see empty HTML | Server-render with Server Components (§12.3) |
| Blocking AI crawlers in robots.txt | Invisible to ChatGPT, Perplexity, Gemini | Audit robots.txt for AI bot user agents |
| Structured data that does not match content | Google considers this spam; can result in penalties | Only add schema that reflects visible page content |
| No `llms.txt` on public-facing sites | AI crawlers have no guide to site structure | Create `llms.txt` with priority pages (§12.3) |
| UTMs on internal links | Resets session source, pollutes analytics data | Only use UTMs on external inbound links (§12.6) |
| Inconsistent UTM naming | `Facebook` vs `facebook` fragments analytics | Lowercase, hyphens, documented taxonomy (§12.6) |
| Missing Open Graph images | Links shared on social media look broken | Provide 1200×630px OG image per page (§12.1) |
| Stale `dateModified` in schema | AI systems deprioritize content they think is outdated | Update `dateModified` when content is substantively refreshed |

---

## 13. Internationalization (i18n)

Internationalization is the process of making an application adaptable to
multiple languages and regions without engineering changes for each locale.
The standard library for Next.js i18n is **next-intl** — it provides
locale-based routing, type-safe translations, ICU message formatting, and
native Server Component support.

> For the technology choice rationale:
> → See [02-technology-radar.md, Section 3.23 — i18n].
> For the impact of i18n on SEO:
> → See [Section 12.1 — SEO Fundamentals] for `hreflang` and locale alternates.

---

### 13.1 next-intl Patterns (Next.js Default)

#### Project Structure for i18n

```text
project-root/
├── messages/                    ← Translation files (one per locale)
│   ├── en.json
│   ├── pt.json
│   └── es.json
├── src/
│   ├── i18n/
│   │   ├── routing.ts           ← Locale configuration (central)
│   │   ├── request.ts           ← Request-scoped config for Server Components
│   │   └── navigation.ts        ← Localized navigation APIs
│   ├── app/
│   │   └── [locale]/            ← Dynamic segment — all pages nested here
│   │       ├── layout.tsx
│   │       ├── page.tsx
│   │       └── (dashboard)/
│   │           └── ...
├── proxy.ts                     ← Locale detection and routing
└── next.config.ts               ← next-intl plugin integration
```

#### Setup

```tsx
// src/i18n/routing.ts — central routing configuration
import { defineRouting } from 'next-intl/routing';

export const routing = defineRouting({
  locales: ['en', 'pt'],
  defaultLocale: 'pt',          // Portuguese as default for PT-based projects
  localePrefix: 'as-needed',    // /about (default locale), /en/about (other locales)
});
```

```tsx
// src/i18n/request.ts — request-scoped config for Server Components
import { getRequestConfig } from 'next-intl/server';
import { hasLocale } from 'next-intl';
import { routing } from './routing';

export default getRequestConfig(async ({ requestLocale }) => {
  const requested = await requestLocale;
  const locale = hasLocale(routing.locales, requested)
    ? requested
    : routing.defaultLocale;

  return {
    locale,
    messages: (await import(`../../messages/${locale}.json`)).default,
  };
});
```

```tsx
// src/i18n/navigation.ts — localized navigation APIs
import { createNavigation } from 'next-intl/navigation';
import { routing } from './routing';

export const { Link, redirect, usePathname, useRouter, getPathname } =
  createNavigation(routing);
```

```tsx
// proxy.ts — locale negotiation (Next.js 16: proxy replaces middleware)
import createMiddleware from 'next-intl/middleware';
import { routing } from './src/i18n/routing';

export default createMiddleware(routing);

export const config = {
  matcher: '/((?!api|trpc|_next|_vercel|.*\\..*).*)',
};
```

```ts
// next.config.ts — plugin integration
import { NextConfig } from 'next';
import createNextIntlPlugin from 'next-intl/plugin';

const nextConfig: NextConfig = {};
const withNextIntl = createNextIntlPlugin();
export default withNextIntl(nextConfig);
```

```tsx
// src/app/[locale]/layout.tsx — root layout with locale
import { NextIntlClientProvider, hasLocale } from 'next-intl';
import { notFound } from 'next/navigation';
import { routing } from '@/i18n/routing';

export function generateStaticParams() {
  return routing.locales.map((locale) => ({ locale }));
}

export default async function RootLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ locale: string }>;
}) {
  const { locale } = await params;
  if (!hasLocale(routing.locales, locale)) notFound();

  return (
    <html lang={locale} suppressHydrationWarning>
      <body>
        <NextIntlClientProvider>
          {children}
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
```

#### Rules

- **MUST** use `next-intl` as the i18n library for Next.js App Router
  projects — it provides the most complete integration (routing, Server
  Components, type safety)
- **MUST** define routing configuration in `src/i18n/routing.ts` as the
  single source of truth — the proxy and navigation APIs both reference it
- **MUST** wrap the app with `<NextIntlClientProvider>` in the root layout
  — this enables translations in Client Components
- **MUST** nest all pages under `app/[locale]/` — this dynamic segment
  provides the locale to every page and layout
- **SHOULD** use `localePrefix: 'as-needed'` — the default locale has no
  prefix (`/about`) while other locales do (`/en/about`). This keeps URLs
  clean for the primary audience
- **SHOULD** export `generateStaticParams` in the layout to enable static
  rendering for all locale variants

---

### 13.2 String Extraction & Organization

#### Message File Structure

```json
// messages/pt.json
{
  "Common": {
    "loading": "A carregar...",
    "error": "Ocorreu um erro",
    "save": "Guardar",
    "cancel": "Cancelar",
    "delete": "Eliminar",
    "confirm": "Confirmar",
    "back": "Voltar",
    "next": "Seguinte"
  },
  "Navigation": {
    "home": "Início",
    "vehicles": "Veículos",
    "about": "Sobre Nós",
    "contact": "Contacto"
  },
  "VehicleList": {
    "title": "Veículos Disponíveis",
    "empty": "Nenhum veículo encontrado.",
    "clearFilters": "Limpar filtros",
    "resultCount": "{count, plural, =0 {Nenhum resultado} one {1 veículo} other {# veículos}}"
  },
  "VehicleDetail": {
    "price": "Preço: {price, number, ::currency/EUR}",
    "year": "Ano: {year}",
    "status": {
      "available": "Disponível",
      "reserved": "Reservado",
      "sold": "Vendido"
    },
    "contact": "Contactar sobre este veículo"
  }
}
```

#### Usage in Components

```tsx
// Server Component — use getTranslations (async)
import { getTranslations } from 'next-intl/server';

export default async function VehiclesPage() {
  const t = await getTranslations('VehicleList');

  return (
    <div>
      <h1>{t('title')}</h1>
      <p>{t('resultCount', { count: vehicles.length })}</p>
    </div>
  );
}

// Client Component — use useTranslations (hook)
'use client';
import { useTranslations } from 'next-intl';

export function VehicleStatusBadge({ status }: { status: string }) {
  const t = useTranslations('VehicleDetail.status');
  return <span>{t(status)}</span>;
}
```

#### Rules

- **MUST** organize messages by feature/component namespace — `VehicleList`,
  `VehicleDetail`, `Navigation`, not a flat list of keys
- **MUST** use the namespace as the first argument to `getTranslations` /
  `useTranslations` — this keeps component code clean and avoids key
  collisions
- **MUST** use ICU message syntax for plurals, numbers, dates, and
  selections — never implement pluralization logic manually:

  ```json
  // BAD — manual plural logic will break in other languages
  "items": "{count} items"

  // GOOD — ICU plural handles every language's rules
  "items": "{count, plural, =0 {No items} one {1 item} other {# items}}"
  ```

- **SHOULD** keep `Common` namespace for shared UI labels (buttons, actions,
  generic messages) and feature-specific namespaces for domain content
- **MUST NOT** hardcode user-visible strings in components — every string
  displayed to the user must go through the translation system, even if the
  app currently only supports one language. Adding the second language
  becomes trivial instead of a massive refactor

---

### 13.3 Locale Routing (URL-Based)

next-intl provides localized navigation APIs that automatically handle
locale prefixes, redirects, and link generation.

```tsx
// Use the localized Link (from i18n/navigation.ts, NOT from next/link)
import { Link } from '@/i18n/navigation';

// Automatically prefixed: /en/about or /about (default locale)
<Link href="/about">About</Link>

// Localized pathnames (if configured)
<Link href="/vehicles">Vehicles</Link>  // → /en/vehicles or /veiculos
```

#### Locale Prefix Strategies

| Strategy | Default Locale URL | Other Locale URL | When to Use |
|---|---|---|---|
| `always` | `/pt/about` | `/en/about` | All locales equal, no "main" language |
| `as-needed` | `/about` | `/en/about` | One primary locale, others secondary |
| `never` | `/about` | `/about` (cookie-based) | Single domain, locale in settings |

- **SHOULD** use `as-needed` for most projects — it keeps URLs clean for
  the primary audience while supporting additional locales
- **SHOULD** use the localized `Link`, `redirect`, `useRouter`, and
  `usePathname` from `@/i18n/navigation` — never use the Next.js originals
  directly in i18n projects

---

### 13.4 Date, Number & Currency Formatting

next-intl provides locale-aware formatting via the ICU message syntax and
the `useFormatter` hook:

```tsx
// In messages (ICU syntax)
"price": "Price: {amount, number, ::currency/EUR}"
"publishedAt": "Published on {date, date, long}"

// In code (useFormatter hook for dynamic formatting)
'use client';
import { useFormatter } from 'next-intl';

export function PriceTag({ price }: { price: number }) {
  const format = useFormatter();
  return (
    <span>
      {format.number(price, { style: 'currency', currency: 'EUR' })}
    </span>
  );
}

export function DateDisplay({ date }: { date: Date }) {
  const format = useFormatter();
  return <time dateTime={date.toISOString()}>{format.dateTime(date, 'long')}</time>;
}
```

- **MUST** format dates, numbers, and currencies through next-intl or the
  Intl API — never use manual string formatting that breaks in other locales
- **MUST** store dates in UTC on the server and convert to the user's
  timezone/locale only at the UI layer
  (→ See [01-core-principles.md, §3.8 — Date & Time Discipline])

---

### 13.5 RTL Support (Awareness)

Right-to-left (RTL) languages (Arabic, Hebrew, Persian) require the entire
layout to be mirrored. While RTL support may not be needed for all projects,
awareness of the requirements ensures the architecture does not block it.

- **SHOULD** use CSS logical properties (`margin-inline-start` instead of
  `margin-left`) — Tailwind v4 supports these natively via logical property
  utilities, and shadcn/ui has first-class RTL support as of January 2026
- **SHOULD** set the `dir` attribute on the `<html>` element based on the
  locale — next-intl can provide this information
- **MAY** defer full RTL support until a project requires it — but ensure
  the translation system and component architecture do not prevent adding
  it later

---

### 13.6 i18n + SEO (hreflang, Locale Alternates)

Search engines need to understand the relationship between locale variants
of the same page. This is done via `hreflang` alternate links and localized
sitemaps.

```tsx
// app/[locale]/vehicles/[id]/page.tsx — locale alternates in metadata
import type { Metadata } from 'next';

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { locale, id } = await params;
  const vehicle = await vehicleService.findById(id);
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL!;

  return {
    title: `${vehicle.brand} ${vehicle.model}`,
    alternates: {
      canonical: `${baseUrl}/${locale}/vehicles/${id}`,
      languages: {
        'pt': `${baseUrl}/vehicles/${id}`,        // Default locale (no prefix)
        'en': `${baseUrl}/en/vehicles/${id}`,
        'x-default': `${baseUrl}/vehicles/${id}`,  // Fallback
      },
    },
  };
}
```

```tsx
// app/sitemap.ts — localized sitemap
import type { MetadataRoute } from 'next';
import { routing } from '@/i18n/routing';

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = process.env.NEXT_PUBLIC_SITE_URL!;

  const vehicles = await vehicleService.listAll();

  return vehicles.flatMap((v) =>
    routing.locales.map((locale) => ({
      url: locale === routing.defaultLocale
        ? `${baseUrl}/vehicles/${v.id}`
        : `${baseUrl}/${locale}/vehicles/${v.id}`,
      lastModified: v.updatedAt,
      changeFrequency: 'weekly' as const,
      priority: 0.6,
    }))
  );
}
```

- **MUST** include `hreflang` alternate links for all public pages when
  the site supports multiple locales — use `alternates.languages` in
  `generateMetadata`
- **MUST** include `x-default` hreflang pointing to the default locale —
  this tells search engines which version to show for unsupported locales
- **SHOULD** generate a localized sitemap that includes all locale variants
  of each page

---

### 13.7 Anti-Patterns

| Anti-Pattern | Why It Is Wrong | Correct Alternative |
|---|---|---|
| Hardcoded strings in components | Impossible to translate without code changes | Use `useTranslations` / `getTranslations` for all user-visible text |
| Manual pluralization (`count === 1 ? 'item' : 'items'`) | Breaks in languages with complex plural rules (Arabic, Polish, etc.) | ICU plural syntax: `{count, plural, one {1 item} other {# items}}` |
| Using `next/link` directly in i18n projects | Links miss the locale prefix, leading to 404s | Use `Link` from `@/i18n/navigation` |
| Flat message files with hundreds of keys | Hard to maintain, namespace collisions, no feature ownership | Organize by feature namespace (`VehicleList.title`) |
| Formatting dates with `.toLocaleDateString()` manually | Inconsistent formatting, does not respect next-intl config | Use `useFormatter` or ICU date syntax |
| Missing `hreflang` on multilingual sites | Search engines cannot associate locale variants, duplicate content issues | `alternates.languages` in `generateMetadata` (§13.6) |
| Translating only after the app is "done" | Massive refactor to extract strings, broken layouts in other languages | Internationalize from day one — even single-language apps benefit (§13.2) |
| Storing locale in `useState` | Lost on refresh, no URL routing, not SSR-compatible | Use URL-based routing with `[locale]` segment |

---

## 14. Real-time & Optimistic Updates

Real-time features make applications feel alive — data updates appear
instantly across all connected clients without page refreshes. Optimistic
updates make interactions feel instant — the UI reflects changes immediately
while the server confirms in the background.

Both patterns are common in the projects this stack targets: a car
dealership showing live inventory status, a distribution app with real-time
order tracking, or a dashboard with live notifications.

> For the database-level configuration of real-time:
> → See [04-database-standards.md, Section 7 — RLS] (Realtime respects RLS policies).
> For the state management patterns that support real-time:
> → See [Section 5 — State Management].

---

### 14.1 Supabase Realtime Subscriptions

Supabase Realtime uses PostgreSQL's logical replication to broadcast
database changes (INSERT, UPDATE, DELETE) to connected clients via
WebSockets. It respects Row Level Security policies, so users only receive
updates for data they are authorized to see.

#### Setup Pattern: Server-Rendered Initial Data + Client Subscription

The recommended pattern combines Server Components for the initial data
load with a Client Component that subscribes to real-time updates:

```tsx
// app/(dashboard)/dashboard/vehicles/page.tsx — Server Component
import { vehicleService } from '@/features/vehicles/services/vehicle-service';
import { VehicleListRealtime } from '@/features/vehicles/components/vehicle-list-realtime';

export default async function VehiclesPage() {
  // Initial data fetched on the server — fast, SEO-friendly
  const initialVehicles = await vehicleService.listAvailable();

  // Pass to Client Component that subscribes to updates
  return <VehicleListRealtime initialVehicles={initialVehicles} />;
}
```

```tsx
// src/features/vehicles/components/vehicle-list-realtime.tsx — Client Component
'use client';

import { useEffect, useState } from 'react';
import { createClient } from '@/lib/supabase/client';
import type { Vehicle } from '../schemas/vehicle-schema';

interface Props {
  initialVehicles: Vehicle[];
}

export function VehicleListRealtime({ initialVehicles }: Props) {
  const [vehicles, setVehicles] = useState<Vehicle[]>(initialVehicles);
  const supabase = createClient();

  useEffect(() => {
    const channel = supabase
      .channel('vehicles-changes')
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'vehicles' },
        (payload) => {
          setVehicles((current) => {
            switch (payload.eventType) {
              case 'INSERT':
                return [...current, payload.new as Vehicle];
              case 'UPDATE':
                return current.map((v) =>
                  v.id === payload.new.id ? (payload.new as Vehicle) : v,
                );
              case 'DELETE':
                return current.filter((v) => v.id !== payload.old.id);
              default:
                return current;
            }
          });
        },
      )
      .subscribe();

    return () => {
      supabase.removeChannel(channel);
    };
  }, [supabase]);

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {vehicles.map((vehicle) => (
        <VehicleCard key={vehicle.id} vehicle={vehicle} />
      ))}
    </div>
  );
}
```

#### Filtered Subscriptions

Subscribe only to changes that matter — filtering reduces bandwidth and
processing:

```tsx
// Only listen for vehicles with status 'available'
.on(
  'postgres_changes',
  {
    event: '*',
    schema: 'public',
    table: 'vehicles',
    filter: 'status=eq.available',
  },
  handleChange,
)

// Only listen for a specific vehicle
.on(
  'postgres_changes',
  {
    event: 'UPDATE',
    schema: 'public',
    table: 'vehicles',
    filter: `id=eq.${vehicleId}`,
  },
  handleChange,
)
```

#### Custom Hook for Realtime

Encapsulate the subscription pattern in a reusable hook:

```tsx
// src/features/vehicles/hooks/use-realtime-vehicles.ts
'use client';

import { useEffect, useState } from 'react';
import { createClient } from '@/lib/supabase/client';
import type { Vehicle } from '../schemas/vehicle-schema';

export function useRealtimeVehicles(initialData: Vehicle[]) {
  const [vehicles, setVehicles] = useState<Vehicle[]>(initialData);
  const supabase = createClient();

  useEffect(() => {
    const channel = supabase
      .channel('vehicles-realtime')
      .on(
        'postgres_changes',
        { event: '*', schema: 'public', table: 'vehicles' },
        (payload) => {
          setVehicles((current) => {
            switch (payload.eventType) {
              case 'INSERT':
                return [...current, payload.new as Vehicle];
              case 'UPDATE':
                return current.map((v) =>
                  v.id === payload.new.id ? (payload.new as Vehicle) : v,
                );
              case 'DELETE':
                return current.filter((v) => v.id !== payload.old.id);
              default:
                return current;
            }
          });
        },
      )
      .subscribe();

    return () => { supabase.removeChannel(channel); };
  }, [supabase]);

  return vehicles;
}
```

#### Rules

- **MUST** enable Realtime on the table in Supabase before subscribing:
  `ALTER PUBLICATION supabase_realtime ADD TABLE vehicles;`
- **MUST** clean up subscriptions in the `useEffect` cleanup function —
  `supabase.removeChannel(channel)` prevents memory leaks and zombie
  connections
- **MUST** use Realtime only in Client Components — Server Components
  cannot maintain WebSocket connections
- **MUST** ensure RLS policies are in place on tables with Realtime —
  without RLS, all users receive all changes regardless of authorization
  (→ See [04-database-standards.md, Section 7])
- **SHOULD** use filtered subscriptions when possible — `filter: 'status=eq.available'`
  reduces the data pushed to each client
- **SHOULD** combine server-rendered initial data with client-side
  subscriptions — this gives fast initial load (SSR) plus live updates
- **SHOULD** encapsulate subscription logic in custom hooks within the
  feature module
- **SHOULD** handle subscription status (`SUBSCRIBED`, `CHANNEL_ERROR`,
  `TIMED_OUT`) to provide feedback when the connection drops:

  ```tsx
  .subscribe((status) => {
    if (status === 'CHANNEL_ERROR') {
      toast.error('Real-time connection lost. Retrying...');
    }
  });
  ```

---

### 14.2 Optimistic UI with TanStack Query

Optimistic updates show the expected result of a mutation immediately in
the UI, then reconcile with the server response. This makes actions feel
instant — the user sees their change without waiting for a network round
trip.

#### Pattern: Optimistic Mutation

```tsx
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { vehicleKeys } from '../hooks/vehicle-keys';
import { toast } from 'sonner';

export function useUpdateVehicleStatus() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, status }: { id: string; status: string }) =>
      vehicleService.updateStatus(id, status),

    // 1. Optimistic update — change the cache immediately
    onMutate: async ({ id, status }) => {
      // Cancel any in-flight queries that would overwrite our optimistic update
      await queryClient.cancelQueries({ queryKey: vehicleKeys.lists() });

      // Save the current data for rollback
      const previousVehicles = queryClient.getQueryData(vehicleKeys.lists());

      // Optimistically update the cache
      queryClient.setQueryData(vehicleKeys.lists(), (old: Vehicle[] | undefined) =>
        old?.map((v) => (v.id === id ? { ...v, status } : v)),
      );

      // Return the previous data for rollback
      return { previousVehicles };
    },

    // 2. Error — rollback to previous data
    onError: (_error, _variables, context) => {
      if (context?.previousVehicles) {
        queryClient.setQueryData(vehicleKeys.lists(), context.previousVehicles);
      }
      toast.error('Failed to update vehicle status. Changes have been reverted.');
    },

    // 3. Success or error — refetch to ensure consistency
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: vehicleKeys.lists() });
    },
  });
}
```

#### When to Use Optimistic Updates

| Scenario | Optimistic? | Why |
|---|---|---|
| Toggle status (available → reserved) | ✅ | Fast, single-field change, easily reversible |
| Delete an item from a list | ✅ | User expects it to disappear immediately |
| Like / favorite / bookmark | ✅ | Classic optimistic pattern, low-risk |
| Create a new record | ⚠️ Maybe | The server generates the ID — use placeholder, replace on confirm |
| Complex form submission | ❌ | Too many fields to optimistically predict the result |
| Payment processing | ❌ | Financial operations must confirm before showing success |
| Multi-step workflows | ❌ | Each step may depend on server-side validation |

#### Rules

- **MUST** always save previous data for rollback in `onMutate` — if the
  server rejects the mutation, the UI must revert cleanly
- **MUST** always invalidate queries in `onSettled` (not just `onSuccess`)
  — this ensures the cache is reconciled with the server regardless of
  whether the mutation succeeded or failed
- **MUST** cancel in-flight queries before applying optimistic updates —
  `queryClient.cancelQueries()` prevents a stale refetch from overwriting
  the optimistic data
- **MUST** inform the user on rollback — show a toast: "Failed to update.
  Changes have been reverted." The user needs to know their action did not
  persist
- **MUST NOT** use optimistic updates for financial transactions, auth
  changes, or operations where showing a false success has serious
  consequences
- **SHOULD** use optimistic updates for toggle-like operations (status
  changes, favorites, read/unread) and list removals (delete)

---

### 14.3 Conflict Resolution Patterns

When multiple users modify the same data simultaneously, conflicts can
occur. The patterns below apply to both real-time subscriptions and
optimistic updates.

#### Last Write Wins (Default)

The simplest strategy — the most recent write overwrites previous ones.
This is Supabase's default behavior and is acceptable for most applications.

- **Use when:** Conflicts are rare, data is not critical (e.g., status
  toggles, preference changes), or there is no collaboration feature
- **Risk:** A user's change can be silently overwritten by another user

#### Optimistic Locking (Version Check)

Use a version number or `updated_at` timestamp to detect conflicts:

```tsx
async function updateVehicle(id: string, data: Partial<Vehicle>, expectedVersion: number) {
  const result = await supabase
    .from('vehicles')
    .update({ ...data, version: expectedVersion + 1 })
    .eq('id', id)
    .eq('version', expectedVersion)  // Only succeeds if version matches
    .select()
    .single();

  if (!result.data) {
    throw new ConflictError(
      'CONFLICT',
      'This vehicle has been modified by another user. Please refresh and try again.',
    );
  }

  return result.data;
}
```

- **Use when:** Data integrity matters (pricing, inventory counts, order
  status) or multiple users may edit the same record
- **UI handling:** Show a toast with "Refresh and try again" — do not
  silently overwrite (→ See [Section 8.4 — Error Mapping])

#### Merge on Conflict

For collaborative editing (rare in the current project scope), merge
changes field-by-field. This requires operational transforms or CRDTs and
is significantly more complex.

- **MAY** consider this pattern only for collaborative features like
  shared document editing — it is overkill for standard CRUD applications

#### Rules

- **SHOULD** use "last write wins" as the default for most applications —
  it is simple and sufficient when conflicts are rare
- **SHOULD** use optimistic locking for records where conflicting edits
  would cause business problems (pricing, stock counts)
- **MUST** handle the `CONFLICT` error from the API gracefully — show a
  message and a way to refresh, never silently fail
  (→ See [03-api-design.md, Section 3 — 409 Conflict])

---

### 14.4 Anti-Patterns

| Anti-Pattern | Why It Is Wrong | Correct Alternative |
|---|---|---|
| Not cleaning up subscriptions | Memory leaks, zombie WebSocket connections, duplicate events | Always `removeChannel()` in `useEffect` cleanup |
| Subscribing without RLS policies | All users receive all changes — data leak | Enable RLS on every table with Realtime (→ 04 §7) |
| Using Realtime for everything | Unnecessary connections, higher Supabase costs, complex state | Use Realtime only for data that genuinely needs live updates |
| Optimistic update without rollback | UI shows false state permanently if the server rejects | Always save previous data and restore on error |
| Optimistic update for payments | User sees "Payment successful" before server confirms — dangerous | Wait for server confirmation for financial operations |
| Polling instead of Realtime | Wasteful, laggy, scales poorly | Use Supabase Realtime subscriptions |
| Not invalidating after optimistic update | Cache drifts from server state over time | Always `invalidateQueries()` in `onSettled` |
| Broad subscriptions on large tables | Receives every change on the table — bandwidth and performance cost | Use `filter` to narrow the subscription |
| Not handling connection errors | Realtime silently disconnects, UI shows stale data | Handle `CHANNEL_ERROR` status, show feedback to user |
| Ignoring conflicts in multi-user scenarios | Silent data loss when two users edit the same record | Use optimistic locking for critical data (§14.3) |

---

## 15. Frontend Testing Patterns

Frontend testing ensures the UI works as expected from the user's
perspective — components render correctly, interactions behave predictably,
and critical flows complete without errors. This section covers
frontend-specific patterns; the complete testing strategy (pyramid,
coverage, CI gates) lives in → See [06-testing-strategy.md].

> For testing technology choices:
> → See [02-technology-radar.md, Section 4.12 — Testing].
> For API testing patterns:
> → See [03-api-design.md, Section 13 — API Testing Patterns].

---

### 15.1 What to Test in Frontend

Not everything needs a test. Focus testing effort where it provides the
most value:

| What to Test | Priority | Tool |
|---|---|---|
| **Critical user flows** (login, checkout, form submission) | 🔴 High | Playwright (E2E) |
| **Async Server Components** (pages that fetch data) | 🔴 High | Playwright (E2E) — Vitest does not support async SC |
| **Interactive components** (forms, modals, dropdowns) | 🟡 Medium | Vitest + Testing Library |
| **Custom hooks** (useUrlState, useRealtimeVehicles) | 🟡 Medium | Vitest + renderHook |
| **Utility functions** (formatCurrency, mapApiError) | 🟡 Medium | Vitest |
| **Synchronous Server Components** (static rendering) | 🟢 Low | Vitest + Testing Library |
| **Styling** (correct classes applied) | ⚪ Low | Visual regression (optional) |
| **Third-party libraries** (shadcn/ui, Radix) | ⚪ None | Already tested by the library |

> **Important (Next.js 16 limitation):** Vitest currently does not support
> async Server Components. For pages and components that use `await` (data
> fetching in Server Components), use Playwright E2E tests instead.

---

### 15.2 Component Tests (Vitest + Testing Library)

Component tests render a component in isolation and verify it behaves
correctly from the user's perspective — not from the implementation's
perspective.

#### Query Priority

React Testing Library queries reflect how users find elements. Use them
in this priority order:

```text
1. getByRole        → Best — matches how assistive technology sees the page
2. getByLabelText   → For form fields associated with labels
3. getByPlaceholderText → When no label exists (less accessible)
4. getByText        → For non-interactive elements with visible text
5. getByTestId      → Last resort — invisible to users
```

- **MUST** prefer `getByRole` as the primary query — it tests
  accessibility and functionality simultaneously
- **MUST NOT** use `container.querySelector` or DOM traversal — it tests
  implementation details that break on refactoring

#### Example: Testing an Interactive Component

```tsx
// src/features/vehicles/components/__tests__/vehicle-form.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { VehicleForm } from '../vehicle-form';

describe('VehicleForm', () => {
  const mockSubmit = vi.fn();

  it('renders all required fields', () => {
    render(<VehicleForm onSubmit={mockSubmit} />);

    expect(screen.getByLabelText('Brand')).toBeInTheDocument();
    expect(screen.getByLabelText('Model')).toBeInTheDocument();
    expect(screen.getByLabelText('Year')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
  });

  it('shows validation errors for empty required fields', async () => {
    const user = userEvent.setup();
    render(<VehicleForm onSubmit={mockSubmit} />);

    await user.click(screen.getByRole('button', { name: /save/i }));

    expect(screen.getByRole('alert')).toBeInTheDocument();
    expect(mockSubmit).not.toHaveBeenCalled();
  });

  it('submits valid data', async () => {
    const user = userEvent.setup();
    render(<VehicleForm onSubmit={mockSubmit} />);

    await user.type(screen.getByLabelText('Brand'), 'Mercedes');
    await user.type(screen.getByLabelText('Model'), 'Classe A');
    await user.type(screen.getByLabelText('Year'), '2023');
    await user.type(screen.getByLabelText('Price'), '25000');
    await user.click(screen.getByRole('button', { name: /save/i }));

    expect(mockSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        brand: 'Mercedes',
        model: 'Classe A',
        year: 2023,
        price: 25000,
      }),
    );
  });

  it('disables submit button while submitting', () => {
    render(<VehicleForm onSubmit={mockSubmit} isSubmitting />);

    expect(screen.getByRole('button', { name: /saving/i })).toBeDisabled();
  });
});
```

#### Rules

- **MUST** use `userEvent` (from `@testing-library/user-event`) over
  `fireEvent` — `userEvent` simulates real user interactions more accurately
  (types character by character, triggers focus/blur events)
- **MUST** follow the Arrange–Act–Assert pattern consistently
- **MUST** test from the user's perspective — "when the user clicks Submit,
  the form data is sent" not "when handleSubmit is called, setState is
  invoked with..."
- **SHOULD** co-locate tests with components in `__tests__/` folders or
  alongside the component file (`vehicle-form.test.tsx`)
- **SHOULD** test validation errors, loading states, disabled states, and
  empty states — not just the happy path
- **MUST NOT** test implementation details — do not assert on internal state,
  hook return values, or CSS classes. If a refactoring changes the internals
  but the user experience stays the same, tests should still pass

---

### 15.3 Hook Testing

Custom hooks that contain non-trivial logic should be tested in isolation
using `renderHook`:

```tsx
// src/hooks/__tests__/use-debounce.test.ts
import { renderHook, act } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { useDebounce } from '../use-debounce';

describe('useDebounce', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('returns the initial value immediately', () => {
    const { result } = renderHook(() => useDebounce('hello', 500));
    expect(result.current).toBe('hello');
  });

  it('debounces value changes', () => {
    const { result, rerender } = renderHook(
      ({ value }) => useDebounce(value, 500),
      { initialProps: { value: 'hello' } },
    );

    rerender({ value: 'world' });
    expect(result.current).toBe('hello'); // Not yet updated

    act(() => { vi.advanceTimersByTime(500); });
    expect(result.current).toBe('world'); // Now updated
  });
});
```

- **SHOULD** test custom hooks that contain logic (debouncing, throttling,
  state machines, complex computations)
- **SHOULD NOT** test hooks that are thin wrappers around library hooks
  (a hook that just calls `useQuery` with specific keys does not need its
  own test — test the component that uses it instead)

---

### 15.4 E2E Patterns (Playwright)

E2E tests validate complete user flows in a real browser. They are the
primary testing strategy for async Server Components and critical user
journeys.

> The full E2E testing strategy will be defined in → See [06-testing-strategy.md].
> This section covers frontend-specific patterns.

```tsx
// tests/e2e/vehicles.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Vehicle management', () => {
  test('user can create a new vehicle', async ({ page }) => {
    // Navigate to the create page
    await page.goto('/dashboard/vehicles/new');

    // Fill the form
    await page.getByLabel('Brand').fill('Mercedes');
    await page.getByLabel('Model').fill('Classe A');
    await page.getByLabel('Year').fill('2023');
    await page.getByLabel('Price').fill('25000');

    // Submit
    await page.getByRole('button', { name: /save/i }).click();

    // Verify redirect and success
    await expect(page).toHaveURL(/\/dashboard\/vehicles\//);
    await expect(page.getByText('Vehicle created successfully')).toBeVisible();
  });

  test('vehicle list shows available vehicles', async ({ page }) => {
    await page.goto('/dashboard/vehicles');

    // Verify the page loaded with content
    await expect(page.getByRole('heading', { name: /vehicles/i })).toBeVisible();
    await expect(page.getByTestId('vehicle-card').first()).toBeVisible();
  });

  test('filters update the vehicle list', async ({ page }) => {
    await page.goto('/dashboard/vehicles');

    // Apply filter
    await page.getByRole('combobox', { name: /status/i }).click();
    await page.getByRole('option', { name: /available/i }).click();

    // Verify URL updated
    await expect(page).toHaveURL(/status=available/);

    // Verify results filtered (implementation-specific assertion)
    await expect(page.getByTestId('vehicle-card')).toHaveCount(await page.getByTestId('vehicle-card').count());
  });
});
```

#### Rules

- **MUST** use Playwright for E2E testing — it provides multi-browser
  support, auto-waiting, and trace viewer for debugging
- **MUST** use Playwright's locators (`getByRole`, `getByLabel`, `getByText`)
  — same user-centric approach as Testing Library
- **SHOULD** test the 3–5 most critical user flows: authentication, primary
  CRUD flow, payment (if applicable), and key navigation paths
- **SHOULD** place E2E tests in `tests/e2e/` with the naming convention
  `<flow>.spec.ts`
- **SHOULD** use Playwright for testing async Server Components that
  Vitest cannot handle

---

### 15.5 Visual Regression (Awareness)

Visual regression testing captures screenshots of components and pages,
comparing them against baseline images to detect unintended visual changes.

- **MAY** use Playwright's screenshot comparison for critical UI pages:

  ```tsx
  test('dashboard matches visual baseline', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveScreenshot('dashboard.png', {
      maxDiffPixelRatio: 0.01,
    });
  });
  ```

- **MAY** use Storybook (Trial — → See [02-technology-radar.md]) for
  component-level visual testing — each component gets stories that render
  it in different states, and Chromatic or Playwright screenshots detect
  visual changes
- **SHOULD** consider visual regression only after the design system is
  stable — visual tests are brittle during active design iteration

---

### 15.6 Accessibility Testing (axe-core Integration)

Automated accessibility testing catches ~40% of WCAG issues. Integrate
it into both component tests and E2E tests.

#### In Component Tests

```tsx
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

it('VehicleCard has no accessibility violations', async () => {
  const { container } = render(<VehicleCard vehicle={mockVehicle} />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

#### In E2E Tests

```tsx
import AxeBuilder from '@axe-core/playwright';

test('vehicles page has no a11y violations', async ({ page }) => {
  await page.goto('/dashboard/vehicles');
  const results = await new AxeBuilder({ page }).analyze();
  expect(results.violations).toEqual([]);
});
```

- **SHOULD** include axe-core accessibility checks in component tests for
  all reusable UI components
- **SHOULD** include accessibility audits in E2E tests for all public-facing
  pages
- **MUST** treat critical violations (missing labels, keyboard traps) as
  test failures — they are as serious as broken functionality
  (→ See [Section 9.8](#98-testing-accessibility))

---

### 15.7 Anti-Patterns

| Anti-Pattern | Why It Is Wrong | Correct Alternative |
|---|---|---|
| Testing implementation details (state, hooks, classes) | Tests break on refactoring even when behavior is unchanged | Test from the user's perspective: render, interact, assert |
| `container.querySelector('.my-class')` | Couples test to CSS implementation, fragile | Use `getByRole`, `getByLabelText`, `getByText` |
| `fireEvent` instead of `userEvent` | Does not simulate real user behavior (no focus, no keyboard events) | Use `userEvent.setup()` + `user.click()`, `user.type()` |
| Testing only the happy path | Bugs live in error handling, edge cases, and empty states | Test validation errors, loading, empty, disabled states |
| `getByTestId` as the first choice | Tests something invisible to users, hides a11y issues | Use `getByRole` first — `getByTestId` is last resort |
| Snapshot testing for components | Brittle — any change breaks the test, review fatigue, low signal | Assert specific elements and behaviors |
| Trying to unit test async Server Components | Vitest does not support them — tests will fail | Use Playwright E2E tests for async SC |
| No cleanup between tests | State leaks, flaky tests, order-dependent results | `afterEach(() => cleanup())` in setup file |
| Mocking everything | Tests pass but do not reflect real behavior | Mock at boundaries (API calls), not internal modules |
| No a11y testing | Accessibility bugs ship to production undetected | Add axe-core checks to component and E2E tests |

---
---

## 16. Frontend Design Checklist

These checklists distill the rules from this document into quick,
actionable verification steps. Use them during design, code review,
and before release.

---

### 16.1 Pre-Implementation Checklist

Before writing any code for a new page or feature, verify:

#### Component Design

- [ ] Server vs Client Components identified — `'use client'` only where
      needed (→ See [Section 3.1](#31-server-vs-client-components--decision-guide))
- [ ] Component responsibilities are clear — each component does one thing
      (→ See [Section 3.3](#33-component-sizing--when-to-split))
- [ ] Props interfaces designed with minimal, typed inputs — no boolean
      traps, no passing entire objects when 2 fields suffice
      (→ See [Section 3.5](#35-props-design))
- [ ] State management approach decided using the hierarchy
      (→ See [Section 5.1](#51-decision-hierarchy))
- [ ] Data fetching strategy identified — Server Component fetch vs
      TanStack Query (→ See [Section 6](#6-data-fetching))

#### UX & Accessibility

- [ ] Mobile layout designed first — responsive modifiers layer up
      (→ See [Section 1.3](#13-mobile-first-always))
- [ ] Modal vs Page decision made based on content complexity
      (→ See [Section 10.6](#106-modal-vs-page--decision-guide))
- [ ] Loading, error, and empty states designed — all three accounted for
      (→ See [Section 8.5](#85-fallback-uis))
- [ ] Keyboard navigation path planned for interactive elements
      (→ See [Section 9.3](#93-keyboard-navigation))
- [ ] Touch targets ≥ 44×44px for all interactive elements
      (→ See [Section 4.4](#44-breakpoints--responsive-design))

#### Data & API

- [ ] API endpoints identified (or Server Actions planned)
      (→ See [Section 7.5](#75-server-actions-integration))
- [ ] Zod schemas defined for form validation — shared with API if applicable
      (→ See [Section 7.1](#71-react-hook-form--zod-pattern))
- [ ] Error mapping planned — API error codes → UI feedback
      (→ See [Section 8.4](#84-error-mapping--api-to-ui))

---

### 16.2 Pre-Release Checklist

Before deploying a feature or page to production, verify:

#### Functionality

- [ ] All user flows tested — create, read, update, delete (as applicable)
- [ ] Form validation works on both client and server
      (→ See [Section 7.3](#73-validation-ux))
- [ ] Error states handled — API errors show toasts, validation errors
      show inline, 404 shows not-found page
      (→ See [Section 8](#8-error-handling-in-ui))
- [ ] Loading states present — skeletons for data-fetching pages, disabled
      buttons during submission
- [ ] Empty states provide guidance — message + action, not blank page
      (→ See [Section 8.5](#85-fallback-uis))

#### Performance

- [ ] LCP image has `priority` prop (→ See [Section 11.2](#112-image-optimization-nextimage))
- [ ] All images use `next/image` with proper `sizes` attribute
- [ ] Fonts loaded via `next/font` with `display: 'swap'`
      (→ See [Section 11.6](#116-font-optimization-nextfont))
- [ ] Third-party scripts use `next/script` with appropriate strategy
      (→ See [Section 11.7](#117-third-party-scripts-nextscript))
- [ ] Lighthouse Performance score ≥ 90 on mobile
      (→ See [Section 11.1](#111-core-web-vitals-targets))
- [ ] No route ships > 200 KB First Load JS
      (→ See [Section 11.4](#114-bundle-analysis--performance-budgets))

#### Accessibility

- [ ] WCAG 2.2 AA compliance verified — axe DevTools shows no violations
      (→ See [Section 9.1](#91-target-wcag-22-level-aa))
- [ ] Keyboard navigation works — all interactive elements reachable and
      operable via Tab, Enter, Space, Escape
      (→ See [Section 9.3](#93-keyboard-navigation))
- [ ] Focus indicators visible — no `outline: none` without replacement
- [ ] Color contrast meets minimum ratios (4.5:1 text, 3:1 UI)
      (→ See [Section 9.6](#96-color-contrast))
- [ ] Semantic HTML used — headings hierarchical, buttons for actions,
      links for navigation (→ See [Section 9.2](#92-semantic-html-first))

#### Styling & Theme

- [ ] Dark mode verified — both themes tested, no broken contrast or
      missing styles (→ See [Section 4.5](#45-darklight-theme))
- [ ] Design tokens used — no hardcoded colors, spacing, or font sizes
      (→ See [Section 4.2](#42-design-tokens--css-variables))
- [ ] Responsive design verified at all breakpoints — sm, md, lg, xl
      (→ See [Section 4.4](#44-breakpoints--responsive-design))

#### SEO & Metadata (Public Pages)

- [ ] `generateMetadata` or static `metadata` on every public page
      (→ See [Section 12.1](#121-seo-fundamentals-traditional))
- [ ] Open Graph image provided (1200×630px minimum)
- [ ] Canonical URL set via `alternates.canonical`
- [ ] Structured data (JSON-LD) added for relevant content types
      (→ See [Section 12.2](#122-structured-data-json-ld))
- [ ] `sitemap.ts` and `robots.ts` present and generating correctly
- [ ] Content is server-rendered — not hidden behind client-side JS
      (→ See [Section 12.3](#123-generative-engine-optimization-geo))

#### Security

- [ ] Client-side validation is UX only — server validates all input
      (→ See [07-security-standards.md, Section 3])
- [ ] No secrets exposed in client-side code — API keys, tokens only in
      Server Components or environment variables without `NEXT_PUBLIC_`
- [ ] Auth checked in Server Functions — not only in proxy.ts
      (→ See [Section 10.3](#103-proxy-patterns-proxyts))

---

### 16.3 Quick Reference: 15 Common Frontend Mistakes

| # | Mistake | Why It Matters | Fix |
|---|---|---|---|
| 1 | `'use client'` on every component | Ships unnecessary JS, defeats SSR | Default to Server Components (§3.1) |
| 2 | `useEffect` for data fetching | Race conditions, no caching | Server Components or TanStack Query (§6) |
| 3 | No loading or error states | Broken UX, blank screens | `loading.tsx`, `error.tsx`, skeletons (§8) |
| 4 | Hardcoded colors instead of tokens | Impossible to theme, inconsistent | Design tokens in `@theme` (§4.2) |
| 5 | No metadata on public pages | Invisible to search engines and AI | `generateMetadata` on every public page (§12.1) |
| 6 | Raw `<img>` instead of `next/image` | No optimization, CLS, slow LCP | Always use `next/image` (§11.2) |
| 7 | Complex form in a modal | Cramped UX, no URL to share | Use a page for 6+ field forms (§10.6) |
| 8 | `outline: none` without replacement | Keyboard users cannot see focus | `focus-visible:ring-2` (§9.3) |
| 9 | Fonts via `<link>` to Google Fonts | External request, FOUT, CLS | Use `next/font` (§11.6) |
| 10 | Filters in `useState` instead of URL | Lost on refresh, not shareable | URL `searchParams` (§5.4) |
| 11 | Auth only in proxy.ts | Silently bypassed on matcher changes | Verify auth in Server Functions too (§10.3) |
| 12 | `defaultProps` on function components | Deprecated in React 19 | Default values in destructuring (§3.2) |
| 13 | Internal links with `<a>` tags | Full page reload, no prefetch | Use `<Link>` from next/link (§10.7) |
| 14 | No `alt` text on images | Screen readers announce nothing | Descriptive `alt` for informative images (§9.2) |
| 15 | UTM parameters on internal links | Breaks session tracking in analytics | UTMs only on external inbound links (§12.6) |

---


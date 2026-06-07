# 🚀 DevOps & CI/CD Standards

> **Scope:** Cross-cutting operational standards for containerization, CI/CD
> pipelines, environment management, deployment strategies, and build
> optimization applicable to all projects covered by these engineering
> standards.
>
> **Purpose:** The operational "playbook" — defines how code moves from a
> developer's machine to production safely, reproducibly, and efficiently.
> This document answers the question: "I have code ready for production —
> how do I package it, test it automatically, deploy it, and keep it
> running securely?" It bridges the gap between domain-specific standards
> (API, database, frontend) and the infrastructure that delivers them to
> users.
>
> **Keywords:**
> - **MUST** = required (PR should be blocked if violated)
> - **SHOULD** = strongly recommended (requires justification to skip)
> - **MAY** = optional (case-by-case)

---

## 0. How to Use This Document

This document defines **operational standards** — how to containerize
applications, configure CI/CD pipelines, manage environments, deploy to
production, and optimize builds. It is the "how to ship" layer that sits
below domain-specific standards and above project management.

It does **not** define:

- **Which tools to use** — technology choices live in
  → See [02-technology-radar.md, §4.13–4.14]. This document assumes the tools
  have been chosen and focuses on **how to use them operationally**.
- **Quality gate pipelines** — the lint → typecheck → test → build pipeline
  lives in → See [06-testing-strategy.md, §8]. This document **extends** that
  baseline with deploy stages, Docker builds, and environment management.
- **Container security rules** — the full container security posture lives
  in → See [07-security-standards.md, §12]. This document **references** those
  rules and adds CI/CD-specific operational patterns.
- **Secrets management rules** — secrets storage, rotation, and leak
  detection live in → See [07-security-standards.md, §7]. This document covers
  only how secrets flow through CI/CD pipelines.
- **Migration strategy** — migration discipline and tooling live in
  → See [04-database-standards.md, §6]. This document covers only how
  migrations execute in CI/CD.
- **Observability integration** — Sentry configuration, source maps, and
  release tracking live in → See [08-observability.md, §3]. This document
  covers only the CI/CD steps that integrate with observability tooling.

### Quick Navigation

| I need to... | Go to |
|---|---|
| Understand the **philosophy** behind these DevOps standards | § 1 — DevOps Philosophy |
| Configure **environment variables** with validation | § 2 — Environment Management |
| Write a **Dockerfile** for a Next.js application | § 3.2 — Next.js Standalone Docker Pattern |
| Set up **Docker Compose** for local development | § 3.4 — Docker Compose for Local Development |
| Extend the CI pipeline with **deploy stages** | § 4 — CI/CD Pipeline Design |
| Deploy to **Vercel** (Next.js default path) | § 5.1 — Vercel Deployment |
| Deploy to **Railway/Render** (container hosting) | § 5.2 — Container Deployment |
| Optimize **build speed** in CI | § 6 — Build Optimization |
| Decide between **PaaS and IaC** | § 7 — Infrastructure Patterns |
| Know what to set up for a **new project** | § 8 — DevOps by Project Stage |
| Run through a **pre-deployment checklist** | § 9 — DevOps Checklist |

### Document Relationships
```text
09-devops-cicd.md (this document)
 ├── Derives from    → 01-core-principles.md (dependency management §10, fail-fast)
 ├── Derives from    → 02-technology-radar.md (Docker, GitHub Actions, Vercel, hosting choices)
 ├── Extends         → 06-testing-strategy.md, §8 (adds deploy stages to quality gate pipeline)
 ├── Complements     → 07-security-standards.md (container security §12, secrets §7, supply chain §11)
 ├── Complements     → 08-observability.md (Sentry releases, health checks, deploy markers)
 ├── References      → 04-database-standards.md, §6 (migration execution in CI/CD)
 ├── Referenced by   → 10-git-workflow.md (deploy triggers, branch protection)
 └── Referenced by   → 11-project-management.md (devops checklists §9)
```

### Boundary Definitions

| Question | This Document (09) | Other Document |
|---|---|---|
| **How** to write Dockerfiles and Compose files? | ✅ Section 3 | — |
| **How** to configure CI/CD pipeline stages? | ✅ Section 4 | → See [06-testing-strategy.md, §8] (quality gate stages) |
| **How** to deploy to Vercel, Railway, Render? | ✅ Section 5 | — |
| **How** to manage environment variables? | ✅ Section 2 (authoritative for patterns) | → See [07-security-standards.md, §7] (security constraints) |
| **How** to secure containers? | — | → See [07-security-standards.md, §12] (authoritative) |
| **How** to manage secrets storage and rotation? | — | → See [07-security-standards.md, §7] (authoritative) |
| **How** to run database migrations in CI? | ✅ Section 4 (CI execution) | → See [04-database-standards.md, §6] (migration strategy) |
| **How** to configure Sentry releases and source maps? | — | → See [08-observability.md, §3] (authoritative) |
| **How** to optimize build speed? | ✅ Section 6 | — |
| **Which** tools and platforms to use? | — | → See [02-technology-radar.md, §3.13–3.14] |
| **How** to containerize / deploy a self-hosted AI inference runtime or agent service? | ✅ Sections 3 + 5 (same Docker + deploy patterns) | → See [12-ai-engineering.md, §7.4] (when to self-host) & §8 (anchor-case runtimes); [02-technology-radar.md, §3.25] (which runtime); [10-git-workflow.md, §8.8] (model weights); [07-security-standards.md, §12] + [02-technology-radar.md, §3.32] (untrusted-code sandbox) |

### Technology Versions

This document is written against the following versions (March 2026):

| Technology | Version | Notes |
|---|---|---|
| Docker Engine | 29.x | Latest stable |
| Docker Compose | v5.1.x | Go SDK, `docker compose` (space) syntax |
| GitHub Actions | Current | `actions/checkout@v6`, `actions/setup-node@v6` |
| Node.js | 24 LTS | Active LTS; 22 LTS (Maintenance); 20 LTS EOL April 2026 |
| Next.js | 16.x | Standalone output, Turbopack default |
| Vercel | Current | Rolling Releases, Fluid compute |
| t3-env | 0.13.x | Standard Schema support (Zod, Valibot, ArkType) |

### AI Agent Instructions

This document is designed to be consumed by AI coding agents (e.g., Claude
Code). When interpreting this document:

- **MUST**, **SHOULD**, and **MAY** are RFC 2119 keywords — treat MUST as non-negotiable constraints, SHOULD as strong defaults that require explicit justification to override, and MAY as contextual options.
- Cross-references (→ See [XX-document.md]) point to authoritative definitions — always defer to the referenced document for the full rule.
- When this document conflicts with [07-security-standards.md], the security document takes precedence.
- BAD/GOOD code examples are pattern-matching references — apply the principle behind the example, not just the literal code.
- Anti-pattern tables describe common mistakes — use them as negative examples when reviewing or generating code.
- Every Dockerfile, CI pipeline, and deployment configuration MUST follow the patterns and security rules defined here.
- If generating code requires violating a MUST rule, the AI **MUST stop** and ask the human for permission before proceeding — never silently override a standard.
- **MUST NOT** over-engineer — always prefer the simplest solution that meets the stated requirements. Do not add abstractions, patterns, or infrastructure beyond what was explicitly requested (→ See [01-core-principles.md, §12]).

---

## 1. DevOps Philosophy

Before any Dockerfile or pipeline configuration, the team must share a
common understanding of **why** these operational patterns exist. DevOps is
not a role — it is a mindset that bridges development and operations,
ensuring that code flows from idea to production safely and predictably.

### 1.1 Core Principles

**Reproducibility — same build, same result, every time.**

A deployment that works on Tuesday but fails on Wednesday with the same
code is a process failure, not a code failure. Every build artifact —
Docker image, CI pipeline, environment configuration — must produce
identical results regardless of when, where, or by whom it is executed.
This is achieved through deterministic dependency installation (`npm ci`),
pinned versions (Docker images, GitHub Actions), and validated environment
variables.

→ See [01-core-principles.md, §10] for dependency management rules.
→ See [07-security-standards.md, §11] for lock file and supply chain rules.

**Infrastructure as configuration, not code.**

Environments should differ only in their configuration (environment
variables, secrets, resource limits), never in their code or
dependencies. The same Docker image that runs in development should run
in staging and production — only the configuration changes. This
eliminates "works on my machine" and "works in staging but not
production" failures.

**Automation over manual processes.**

Every repeatable task — testing, building, deploying, scanning — should
be automated. Manual processes are error-prone, inconsistent, and do not
scale. If a developer must remember to run a command before deploying,
that command should be in the pipeline.

- **MUST** automate quality gates (lint, typecheck, test, build) — no
  exceptions
  (→ See [06-testing-strategy.md, §8])
- **MUST** automate security scanning (dependency audit, container scan)
  (→ See [07-security-standards.md, §13])
- **SHOULD** automate deployments triggered by merges to protected branches
- **SHOULD** automate environment variable validation at build time

**Ship small, ship often.**

Small deployments are safe deployments. A deploy that changes 5 files is
easier to debug than one that changes 500. Frequent deploys reduce the
blast radius of bugs, make rollbacks simpler, and keep the feedback loop
tight. This principle directly supports the "fail fast" mindset from
→ See [01-core-principles.md, §1].

**Pragmatism: PaaS first, custom infrastructure when justified.**

For the current project scale (solo developer, small freelance teams),
managed platforms (Vercel, Supabase Cloud, Railway) provide the right
balance of capability, simplicity, and cost. Custom infrastructure
(Terraform, Kubernetes) introduces operational complexity that must be
justified by a clear, measured need — not by aspiration.

→ See [01-core-principles.md, §1.3] — "Start simple, add complexity only
when measured need exists."

- **MUST** start with the simplest deployment path that meets requirements
- **MUST** document the decision to move beyond PaaS in an ADR
  (→ See [01-core-principles.md, §9])
- **MUST NOT** adopt Kubernetes, Terraform, or custom IaC without a
  documented justification that simpler alternatives have been evaluated
  and found insufficient

### 1.2 The Deployment Pipeline Mental Model

Every change flows through a pipeline with progressive confidence gates.
Each stage is cheaper to fail than the next — catching a lint error costs
seconds, catching a production bug costs hours.

```text
Developer pushes code
        │
        ▼
┌─────────────────┐
│  Quality Gates  │  lint → typecheck → test → build
│  (→ 06 §8)      │  ~2-5 min — catch code problems
└────────┬────────┘
         │ pass
         ▼
┌─────────────────┐
│ Security Scan   │  npm audit, container scan, SAST
│ (→ 07 §13)      │  ~1-3 min — catch vulnerabilities
└────────┬────────┘
         │ pass
         ▼
┌─────────────────┐
│  Build & Push   │  Docker build, image push, source maps
│  (→ this doc)   │  ~2-5 min — create deployment artifact
└────────┬────────┘
         │ pass
         ▼
┌─────────────────┐
│  Deploy         │  Vercel, Railway, or container platform
│  (→ this doc)   │  ~1-3 min — ship to environment
└────────┬────────┘
         │ pass
         ▼
┌─────────────────┐
│  Verify         │  Health checks, smoke tests, Sentry
│  (→ 08 §5.1)    │  ~1 min — confirm deployment works
└─────────────────┘
```

- **MUST** enforce every gate — a deployment that skips quality gates or
  security scanning is a deployment that introduces uncontrolled risk
- **SHOULD** target total pipeline time under 15 minutes for the full
  cycle (quality gates through deploy verification)
- **MAY** run security scans in parallel with quality gates to reduce
  total pipeline time, provided both must pass before deployment

---

## 2. Environment Management

> **Ownership note:** This section is the **authoritative source** for
> environment variable management — validation patterns, `.env` file
> conventions, `NEXT_PUBLIC_*` rules, and Vercel scoping. For the
> **security constraints** around env vars (secrets storage, separation,
> leak prevention), → See [07-security-standards.md, §7]. For the
> **universal principle** of fail-fast at startup,
> → See [01-core-principles.md, §2.3].

Environments are the bridge between code and users. A well-managed
environment strategy ensures that developers work with realistic data,
QA catches bugs before production, and production remains stable and
predictable.

### 2.1 Environment Strategy

Every project operates across at least two environments, scaling to
three or four as the project matures:

| Environment | Purpose | Who uses it | Trigger |
|---|---|---|---|
| **Development** | Local development, rapid iteration | Developers | `npm run dev`, `docker compose up` |
| **Preview** | Per-PR deployments, stakeholder review | Developers, PMs, clients | Automatic on PR (Vercel preview) |
| **Production** | Live application serving real users | End users | Merge to `main` branch |

For projects that require a persistent shared testing environment:

| Environment | Purpose | Who uses it | Trigger |
|---|---|---|---|
| **Staging** | Pre-production validation with production-like data | QA, developers | Merge to `develop` branch or manual |

- **MUST** have at minimum Development and Production environments for
  every project
- **SHOULD** use preview deployments (Vercel) for PR-based review —
  this effectively replaces a dedicated staging environment for most
  projects
- **MAY** add a dedicated Staging environment when the project has a QA
  process, multiple stakeholders, or regulatory requirements
- **MUST** use different credentials and secrets across environments —
  development and production **MUST NOT** share database credentials,
  API keys, or signing keys
  (→ See [07-security-standards.md, §7])

### 2.2 Environment Variables — Validation and Typing

Environment variables are the primary mechanism for configuring
applications across environments. Unvalidated environment variables are
a persistent source of deployment failures — a missing `DATABASE_URL`
or a malformed `NEXT_PUBLIC_SUPABASE_URL` can crash an application at
runtime with a cryptic error.

**The solution: validate environment variables at build time using
`@t3-oss/env-nextjs` and Zod.**

```ts
// src/env.ts
import { createEnv } from '@t3-oss/env-nextjs';
import { z } from 'zod';

export const env = createEnv({
  /*
   * Server-side environment variables — never exposed to the client.
   * Accessing these on the client will throw a descriptive error.
   */
  server: {
    DATABASE_URL: z.string().url(),
    DIRECT_URL: z.string().url(),
    SUPABASE_SERVICE_ROLE_KEY: z.string().min(1),
    SENTRY_AUTH_TOKEN: z.string().min(1),
    NODE_ENV: z.enum(['development', 'test', 'production']).default('development'),
  },

  /*
   * Client-side environment variables — available in the browser.
   * MUST be prefixed with NEXT_PUBLIC_.
   */
  client: {
    NEXT_PUBLIC_SUPABASE_URL: z.string().url(),
    NEXT_PUBLIC_SUPABASE_ANON_KEY: z.string().min(1),
    NEXT_PUBLIC_SENTRY_DSN: z.string().url(),
    NEXT_PUBLIC_APP_URL: z.string().url(),
  },

  /*
   * Runtime env mapping for Next.js >= 13.4.4.
   * Only client-side variables need explicit mapping.
   */
  experimental__runtimeEnv: {
    NEXT_PUBLIC_SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL,
    NEXT_PUBLIC_SUPABASE_ANON_KEY: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
    NEXT_PUBLIC_SENTRY_DSN: process.env.NEXT_PUBLIC_SENTRY_DSN,
    NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL,
  },
});
```

**Build-time validation** — import `src/env.ts` in `next.config.ts` to
ensure the build fails immediately if any variable is missing or invalid:

```ts
// next.config.ts
import './src/env'; // Validates env vars at build time

import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  output: 'standalone',
  // For standalone output, transpile the t3-env packages
  transpilePackages: ['@t3-oss/env-nextjs', '@t3-oss/env-core'],
};

export default nextConfig;
```

**Usage** — import `env` anywhere in the application for type-safe,
validated access:

```ts
// In any server-side file
import { env } from '@/env';

const supabase = createClient(env.NEXT_PUBLIC_SUPABASE_URL, env.SUPABASE_SERVICE_ROLE_KEY);
```

**Rules:**

- **MUST** validate all environment variables at build time using
  `@t3-oss/env-nextjs` (or `@t3-oss/env-core` for non-Next.js projects)
  with Zod schemas
- **MUST** separate server-side and client-side variables in the schema —
  server variables accessed on the client will throw a descriptive error
  at runtime
- **MUST** import the env validation file in `next.config.ts` to trigger
  build-time validation
- **MUST NOT** access `process.env` directly anywhere in the application
  — always use the validated `env` object
- **SHOULD** use Zod refinements for complex validation (URL format,
  minimum length, enum values)
- **MAY** use `skipValidation: !!process.env.SKIP_ENV_VALIDATION` for
  faster local development when iterating on non-env-related code

### 2.3 .env File Conventions

```text
project/
├── .env.example        ← Committed — all keys with placeholders, never real values
├── .env                ← Git-ignored — local development values
├── .env.local          ← Git-ignored — local overrides (highest priority)
├── .env.test           ← Git-ignored — test environment values (used by Vitest)
└── .env.production     ← Git-ignored — NEVER committed, NEVER used in CI
```

- **MUST** commit `.env.example` with all required keys, short
  descriptions, and placeholder values — this is the single source of
  truth for which variables the project needs
  (→ See [07-security-standards.md, §7])
- **MUST** add `.env`, `.env.local`, `.env.production`, and `.env.test`
  to `.gitignore` **before the first commit**
- **MUST NOT** commit `.env.production` or any file containing real
  secrets — production values live in the deployment platform (Vercel
  dashboard, Railway variables, GitHub Actions secrets)
- **SHOULD** keep `.env.example` updated whenever a new variable is added
- **SHOULD** document the purpose of each variable in `.env.example` with
  inline comments

```env
# .env.example
# ==============================================================================
# Copy this file to .env and fill in real values.
# NEVER commit .env files with real values to version control.
# ==============================================================================

# --- Database (Supabase) ---
DATABASE_URL=postgresql://postgres:password@localhost:54322/postgres
DIRECT_URL=postgresql://postgres:password@localhost:54322/postgres

# --- Supabase ---
NEXT_PUBLIC_SUPABASE_URL=http://localhost:54321
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# --- Application ---
NEXT_PUBLIC_APP_URL=http://localhost:3000

# --- Sentry (→ See 08-observability.md §3) ---
NEXT_PUBLIC_SENTRY_DSN=https://your-dsn@sentry.io/project-id
SENTRY_AUTH_TOKEN=your-sentry-auth-token
```

### 2.4 NEXT_PUBLIC_* Rules

Next.js uses the `NEXT_PUBLIC_` prefix to determine which environment
variables are inlined into the client bundle at build time. This is a
**security boundary** — any variable with this prefix is visible to
every user in the browser's developer tools.

- **MUST** prefix client-safe variables with `NEXT_PUBLIC_`
- **MUST NOT** prefix server-only secrets with `NEXT_PUBLIC_` — this
  exposes them to every user
- **MUST** audit the client bundle periodically to verify no server
  secrets leaked into the build:

  ```bash
  # After building, search the output for known secret patterns
  grep -r "SUPABASE_SERVICE_ROLE" .next/ || echo "✅ No server secrets in client bundle"
  grep -r "SENTRY_AUTH_TOKEN" .next/ || echo "✅ No server secrets in client bundle"
  ```

- **MUST** understand that `NEXT_PUBLIC_` variables are **frozen at build
  time** — changing them requires a rebuild and redeploy. Runtime-only
  variables (without the prefix) can be changed by restarting the server.

| Variable Type | Prefix | Available in | Changed by |
|---|---|---|---|
| Client-safe | `NEXT_PUBLIC_*` | Browser + Server | Rebuild required |
| Server-only | No prefix | Server only | Server restart |

### 2.5 Vercel Environment Variable Scopes

Vercel provides three environment scopes that map directly to deployment
contexts:

| Scope | Applied to | Use case |
|---|---|---|
| **Production** | Deployments from the production branch (`main`) | Real API keys, production database URL |
| **Preview** | Deployments from non-production branches (PRs) | Test API keys, staging database URL |
| **Development** | Local development via `vercel env pull` | Local API keys, local database URL |

- **MUST** configure production secrets with the **Production** scope
  only — never "All Environments"
- **SHOULD** configure different values per scope for database URLs, API
  keys, and third-party service credentials — preview deployments should
  not hit the production database
- **SHOULD** use `vercel env pull` to sync Development-scoped variables
  to a local `.env.local` file — this keeps the team's local environments
  consistent
- **MUST NOT** use the same API keys for Preview and Production — a bug
  in a PR preview should not corrupt production data

```bash
# Sync development environment variables to local .env.local
vercel env pull .env.local

# Add a new environment variable via CLI
vercel env add STRIPE_SECRET_KEY production preview

# List all configured variables
vercel env ls
```

### 2.6 Environment Parity

Environment parity means minimizing the differences between development
and production so that code behaves identically in both. Perfect parity
is impossible (and unnecessary), but avoidable drift causes real bugs.

**What MUST be identical:**

- Node.js major version (use `.nvmrc` or `.node-version` to pin)
- npm/package manager version
- Database engine and major version (PostgreSQL via Supabase local)
- Application code and dependencies (`npm ci` ensures this)

**What MAY differ:**

- Database data (development uses seeds, production uses real data)
- External service endpoints (test vs production Stripe, SendGrid)
- Resource limits (local has no rate limits, production does)
- SSL/TLS configuration (local uses HTTP, production uses HTTPS)

**Rules:**

- **MUST** pin the Node.js version in a `.nvmrc` or `.node-version` file
  at the project root — the CI pipeline and all developers must use the
  same major version
- **MUST** use `npm ci` (not `npm install`) in CI and Docker builds for
  deterministic dependency resolution
  (→ See [01-core-principles.md, §10])
- **SHOULD** use Supabase local development (`supabase start`) to match
  the production database engine
  (→ See [04-database-standards.md, §13.2])
- **SHOULD** use Docker Compose to run supporting services (PostgreSQL,
  Redis) locally, matching production versions

### 2.7 Anti-Patterns

| Anti-Pattern | Why It Is Wrong | What to Do Instead |
|---|---|---|
| **Accessing `process.env` directly** | No type safety, no build-time validation — missing vars cause runtime crashes | Use `@t3-oss/env-nextjs` with Zod for validated, typed access |
| **Committing `.env` with real secrets** | Secrets in Git history forever — even after deletion | Use `.env.example` (committed) + `.env` (git-ignored) |
| **Same secrets across all environments** | A preview deploy bug can corrupt production data | Different credentials per environment scope |
| **`NEXT_PUBLIC_` on server secrets** | Exposes secrets to every browser user | Only prefix truly client-safe values |
| **Hardcoding environment-specific values** | Breaks when deploying to a different environment | Use environment variables for all environment-specific config |
| **No `.env.example` in the repo** | New developers guess which variables are needed | Maintain `.env.example` as the source of truth |
| **`npm install` in CI** | Can modify the lock file, introducing untested versions | Always use `npm ci` for deterministic builds |

---

## 3. Docker

Docker provides the reproducibility layer for deployments — a container
built today runs identically in six months, on any machine, in any
environment. This section defines how to write Dockerfiles, optimize
images, and use Docker Compose for local development.

For security-specific container rules (non-root users, image scanning,
secrets in Docker), see → See [07-security-standards.md, §12].
For the technology evaluation (why Docker, when to use it, when not),
see → See [02-technology-radar.md, §4.13].

### 3.1 Dockerfile Best Practices

Every production Dockerfile **MUST** use multi-stage builds. A
multi-stage build separates the build environment (which needs
compilers, dev dependencies, and build tools) from the production
environment (which needs only the compiled output and runtime
dependencies). This dramatically reduces image size, attack surface,
and startup time.

**Principles:**

- **MUST** use multi-stage builds — separate `deps`, `build`, and
  `runner` stages
- **MUST** use a specific image tag, never `latest` — reproducibility
  requires pinned versions
  (→ See [07-security-standards.md, §12])
- **MUST** use a non-root user in the final (runner) stage
- **SHOULD** use Alpine-based images for smaller footprint (`node:24-alpine`)
- **SHOULD** order layers from least-frequently-changed to
  most-frequently-changed to maximize cache hits
- **MUST** add a `.dockerignore` file to exclude unnecessary files from
  the build context (→ See §3.3)

**Layer ordering for optimal caching:**

```text
1. Base image selection           ← Changes rarely (Node.js upgrades)
2. System dependencies            ← Changes rarely
3. Package manifest (package.json)← Changes when deps change
4. npm ci                         ← Rebuilds only when manifest changes
5. Application source code        ← Changes on every commit
6. Build command                  ← Runs on every commit
```

### 3.2 Next.js Standalone Docker Pattern

Next.js's `standalone` output mode produces a minimal, self-contained
build that includes only the files needed to run the application. This
reduces Docker image size from 2GB+ to ~200MB — a 90%+ reduction.

This is the **reference architecture** for containerizing Next.js
applications:

```dockerfile
# ============================================================================
# Next.js Standalone Docker Build
# Reference: https://nextjs.org/docs/app/getting-started/deploying
# ============================================================================

# --- Stage 1: Dependencies ---
FROM node:24-alpine AS deps

# Install libc6-compat for Alpine compatibility with some npm packages
RUN apk add --no-cache libc6-compat

WORKDIR /app

# Copy package manifest and lock file first — this layer is cached
# until dependencies change
COPY package.json package-lock.json ./

# Deterministic install from lock file
RUN npm ci

# --- Stage 2: Build ---
FROM node:24-alpine AS build

WORKDIR /app

# Copy dependencies from the deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy source code
COPY . .

# Disable Next.js telemetry during build
ENV NEXT_TELEMETRY_DISABLED=1

# Build the application
# Environment variables needed at build time (NEXT_PUBLIC_*) must be
# available here — pass them as build args or use .env.production
RUN npm run build

# --- Stage 3: Runner (Production) ---
FROM node:24-alpine AS runner

WORKDIR /app

# Production environment
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Create non-root user and group
# → See [07-security-standards.md, §12] — never run as root
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Copy public assets
COPY --from=build /app/public ./public

# Create .next directory with correct ownership
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Copy standalone output — includes only necessary node_modules
COPY --from=build --chown=nextjs:nodejs /app/.next/standalone ./

# Copy static assets
COPY --from=build --chown=nextjs:nodejs /app/.next/static ./.next/static

# Switch to non-root user
USER nextjs

# Expose port (configurable via PORT env var)
EXPOSE 3000

# Set hostname to listen on all interfaces
ENV HOSTNAME="0.0.0.0"
ENV PORT=3000

# Start the standalone server
CMD ["node", "server.js"]
```

**Prerequisites** — enable standalone output in `next.config.ts`:

```ts
// next.config.ts
const nextConfig: NextConfig = {
  output: 'standalone',
  // If using @t3-oss/env-nextjs with standalone:
  transpilePackages: ['@t3-oss/env-nextjs', '@t3-oss/env-core'],
};
```

**Build-time environment variables:**

`NEXT_PUBLIC_*` variables are inlined at build time. For Docker builds,
pass them as build arguments:

```bash
docker build \
  --build-arg NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co \
  --build-arg NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ... \
  --build-arg NEXT_PUBLIC_APP_URL=https://myapp.com \
  -t myapp:latest .
```

And declare them in the Dockerfile's build stage:

```dockerfile
# In the build stage, before `RUN npm run build`:
ARG NEXT_PUBLIC_SUPABASE_URL
ARG NEXT_PUBLIC_SUPABASE_ANON_KEY
ARG NEXT_PUBLIC_APP_URL
```

> **Important:** Only `NEXT_PUBLIC_*` variables need to be available at
> build time. Server-only variables (without the prefix) are read at
> runtime and should be injected via `docker run -e` or the deployment
> platform's environment configuration. **MUST NOT** pass server-only
> secrets as build args — they are visible in `docker history`.
> (→ See [07-security-standards.md, §12])

### 3.3 .dockerignore Configuration

A `.dockerignore` file prevents unnecessary and sensitive files from
entering the Docker build context. Without it, the entire project
directory — including `node_modules`, `.git`, and `.env` files — is
sent to the Docker daemon.

```dockerignore
# .dockerignore
# ==============================================================================
# Exclude files that should not be in the Docker build context.
# This reduces build time, image size, and prevents secret leakage.
# ==============================================================================

# Version control
.git
.gitignore

# Dependencies (rebuilt inside the container)
node_modules

# Environment files (secrets — inject at runtime, not build time)
.env
.env.*
!.env.example

# Build output (rebuilt inside the container)
.next
out
dist
build
coverage

# Tests (not needed in production image)
tests
__tests__
*.test.ts
*.test.tsx
*.spec.ts
*.spec.tsx
playwright-report
test-results

# Documentation
*.md
docs
LICENSE

# IDE and editor
.vscode
.idea
*.swp
*.swo

# Docker files (prevent recursive context)
Dockerfile
docker-compose*.yml

# Misc
.turbo
.vercel
.husky
```

- **MUST** maintain a `.dockerignore` in every project that uses Docker
- **MUST** exclude `.env` files — secrets must not enter the image
- **MUST** exclude `node_modules` — dependencies are installed fresh
  inside the container with `npm ci`
- **SHOULD** exclude tests, documentation, and IDE files — they add
  no value to the production image

### 3.4 Docker Compose for Local Development

Docker Compose defines a multi-service development environment in a
single file. Use it to run databases, caches, and supporting services
locally without installing them on the host machine.

> **Version note (March 2026):** Docker Compose v5 is the current major
> version. The `version` top-level key in `compose.yaml` is optional and
> ignored — remove it if present. Use the `docker compose` command
> (space, not hyphen).

```yaml
# compose.yaml
# ==============================================================================
# Local development environment
# Start: docker compose up -d
# Stop:  docker compose down
# Reset: docker compose down -v (removes volumes — destroys data)
# ==============================================================================

services:
  # --- PostgreSQL Database ---
  db:
    image: postgres:17-alpine
    restart: unless-stopped
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: app_dev
    ports:
      - '5432:5432'
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ['CMD-SHELL', 'pg_isready -U postgres']
      interval: 10s
      timeout: 5s
      retries: 5

  # --- Redis (when needed for caching/sessions) ---
  # Uncomment when the project requires Redis
  # redis:
  #   image: redis:7-alpine
  #   restart: unless-stopped
  #   ports:
  #     - '6379:6379'
  #   volumes:
  #     - redis_data:/data
  #   healthcheck:
  #     test: ['CMD', 'redis-cli', 'ping']
  #     interval: 10s
  #     timeout: 5s
  #     retries: 5

volumes:
  postgres_data:
  # redis_data:
```

> **Note:** For Supabase-based projects, use `supabase start` instead
> of a standalone PostgreSQL container. Supabase CLI provides a full
> local stack (PostgreSQL, Auth, Storage, Realtime) that matches the
> production environment more closely.
> → See [04-database-standards.md, §13.2]

**Rules:**

- **SHOULD** include a `compose.yaml` in every project that has external
  service dependencies (database, cache, queue)
- **MUST** pin service image versions (e.g., `postgres:17-alpine`, not
  `postgres:latest`)
- **MUST** configure volume mounts for data persistence across container
  restarts
- **SHOULD** define healthchecks for all services — dependent services
  can wait for readiness
- **MUST** use `env_file` or environment variables — never hardcode
  secrets in `compose.yaml`
  (→ See [07-security-standards.md, §12])
- **MUST NOT** use Docker Compose for production orchestration — use a
  PaaS platform (Vercel, Railway) or a dedicated orchestrator
  (→ See [02-technology-radar.md, §4.13])

### 3.5 Image Optimization

A smaller image means faster pulls, faster deploys, less storage, and
a smaller attack surface.

| Technique | Impact | Details |
|---|---|---|
| Multi-stage builds | 50-90% size reduction | Separate build and runtime stages |
| Standalone output (Next.js) | 90%+ size reduction | Only necessary files in final image |
| Alpine base images | ~50MB vs ~350MB | `node:24-alpine` instead of `node:24` |
| `.dockerignore` | Faster build context | Exclude node_modules, .git, tests |
| Layer ordering | Faster rebuilds | Put rarely-changed layers first |
| `npm ci --omit=dev` | Smaller node_modules | No dev dependencies in production (standalone handles this automatically) |

- **MUST** target production images under 300MB for Node.js applications
  (Next.js standalone typically achieves ~150-200MB)
- **SHOULD** regularly check image size with `docker images` and
  investigate significant increases
- **MAY** use distroless images (`gcr.io/distroless/nodejs24`) for
  hardened production images — these have no shell or package manager,
  reducing attack surface further
  (→ See [07-security-standards.md, §12])

### 3.6 Anti-Patterns

| Anti-Pattern | Why It Is Wrong | What to Do Instead |
|---|---|---|
| **Single-stage Dockerfile** | Includes build tools and dev deps in production — bloated, insecure | Use multi-stage builds (deps → build → runner) |
| **`FROM node:latest`** | Non-reproducible — version changes without notice | Pin to specific version: `node:24-alpine` |
| **Running as root** | Container compromise = host compromise | `adduser --system` + `USER nextjs` |
| **No `.dockerignore`** | Sends entire project to Docker daemon — slow, leaks secrets | Maintain `.dockerignore` with sensible exclusions |
| **`npm install` in Dockerfile** | May modify lock file, non-deterministic | Always use `npm ci` |
| **Copying `node_modules` from host** | Platform mismatch (macOS → Linux), non-reproducible | Install inside container with `npm ci` |
| **Secrets as build args** | Visible in `docker history` — permanent exposure | Inject server secrets at runtime via `-e` |
| **`docker-compose` (hyphen)** | Legacy v1 syntax, deprecated | Use `docker compose` (space) — v5 syntax |
| **Docker Compose in production** | Not designed for production orchestration | Use PaaS or dedicated orchestrator |

---

## 4. CI/CD Pipeline Design

The CI/CD pipeline is the automated path from code push to production
deployment. This section extends the quality gate pipeline defined in
→ See [06-testing-strategy.md, §8] with security scanning, Docker builds,
Sentry integration, database migrations, and deployment stages.

The quality gates baseline (lint → typecheck → test → build) is **not
repeated here** — it is defined and maintained in the testing strategy
document. This section adds the stages that come **after** quality gates
pass.

### 4.1 Pipeline Philosophy

**Fail fast, gate progressively.** Each stage validates a different
dimension of readiness. Cheaper checks run first so that failures
surface in seconds, not minutes.

**The full pipeline:**

```text
┌───────────────────────────────────────────────────────────────────┐
│  PR Pipeline (runs on every pull request)                         │
│                                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │  Lint    │─►│Typecheck │─►│  Test    │─►│  Build   │           │
│  │  ~10s    │  │  ~15s    │  │  ~30-120s│  │  ~60-120s│           │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
│       └────────────── Quality Gates (→ 06 §8) ──────────────┘     │
│                                                                   │
│  ┌──────────┐  ┌──────────┐                                       │
│  │ Security │  │   E2E    │  (parallel or sequential)             │
│  │  Scan    │  │  Tests   │                                       │
│  │  ~1-3min │  │  ~5-15min│                                       │
│  └──────────┘  └──────────┘                                       │
└───────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────┐
│  Deploy Pipeline (runs on merge to main)                          │
│                                                                   │
│  Quality Gates ─► Security Scan ─► Build Artifact ─► Deploy       │
│                                    (Docker/Vercel)   ─► Verify    │
│                                                                   │
│  Additional steps:                                                │
│  • Sentry source map upload (→ 08 §3.4)                           │
│  • Database migration (→ 04 §6)                                   │
│  • Deploy markers (→ 08 §3.5)                                     │
│  • Health check verification (→ 08 §5.1)                          │
└───────────────────────────────────────────────────────────────────┘
```

### 4.2 GitHub Actions — Extended Pipeline

This configuration extends the baseline from → See [06-testing-strategy.md,
§8.2] with security scanning and deployment stages. The quality gates
and E2E jobs are identical to the baseline — they are not duplicated
here.

```yaml
# .github/workflows/deploy.yml
# ==============================================================================
# Deployment Pipeline
# Extends the quality gate baseline (→ 06 §8.2) with security scanning,
# Sentry integration, and deploy stages.
# Triggered on merge to main (production) or develop (staging).
# ==============================================================================
name: Deploy

on:
  push:
    branches: [main]

concurrency:
  group: deploy-${{ github.ref }}
  cancel-in-progress: false    # Do NOT cancel deploy — let it finish

jobs:
  # ── Quality Gates (same as ci.yml) ──────────────────────────────
  quality-gates:
    name: Quality Gates
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v6
      - uses: actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020 # v6
        with:
          node-version-file: '.nvmrc'
          cache: 'npm'
      - run: npm ci
      - name: Lint
        run: npm run lint
      - name: Type Check
        run: npx tsc --noEmit
      - name: Test
        run: npm run test:coverage
      - name: Build
        run: npm run build

  # ── Security Scan ──────────────────────────────────────────────
  security-scan:
    name: Security Scan
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v6
      - uses: actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020 # v6
        with:
          node-version-file: '.nvmrc'
          cache: 'npm'
      - run: npm ci

      # Dependency vulnerability audit
      - name: npm audit
        run: npm audit --audit-level=high
        continue-on-error: false

      # Additional scanning tools can be added here:
      # - Snyk, Grype, OSV-Scanner
      # → See [07-security-standards.md, §11] for tool options

  # ── Deploy to Vercel ───────────────────────────────────────────
  deploy:
    name: Deploy to Production
    needs: [quality-gates, security-scan]
    runs-on: ubuntu-latest
    timeout-minutes: 15
    environment:
      name: production
      url: ${{ steps.deploy.outputs.url }}

    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v6

      # For Vercel-hosted Next.js apps, Vercel handles the deploy
      # automatically when connected to the GitHub repo. This job
      # serves as a gate — deploy only proceeds if quality gates
      # and security scan pass.
      #
      # If using Vercel CLI for programmatic deploys:
      # - name: Deploy to Vercel
      #   id: deploy
      #   run: |
      #     npx vercel deploy --prod --token=${{ secrets.VERCEL_TOKEN }}
      #   env:
      #     VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
      #     VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}

      # Upload source maps to Sentry (→ 08 §3.4)
      # This step runs after deploy to associate source maps with
      # the deployed release.
      - uses: actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020 # v6
        with:
          node-version-file: '.nvmrc'
          cache: 'npm'
      - run: npm ci

      - name: Create Sentry Release
        run: |
          npx @sentry/cli releases new "${{ github.sha }}"
          npx @sentry/cli releases set-commits "${{ github.sha }}" --auto
          npx @sentry/cli releases finalize "${{ github.sha }}"
          npx @sentry/cli releases deploys "${{ github.sha }}" new -e production
        env:
          SENTRY_AUTH_TOKEN: ${{ secrets.SENTRY_AUTH_TOKEN }}
          SENTRY_ORG: ${{ secrets.SENTRY_ORG }}
          SENTRY_PROJECT: ${{ secrets.SENTRY_PROJECT }}

      # Post-deploy verification
      - name: Verify Deployment
        run: |
          sleep 30  # Wait for deployment to propagate
          STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${{ vars.PRODUCTION_URL }}/api/health")
          if [ "$STATUS" != "200" ]; then
            echo "❌ Health check failed with status $STATUS"
            exit 1
          fi
          echo "✅ Health check passed"
```

> **Note on Vercel automatic deploys:** When a Vercel project is connected
> to a GitHub repo, Vercel triggers its own build and deploy on every push.
> The GitHub Actions pipeline above serves as a **gate** — the Vercel
> deploy only uses the code that passed all gates. For maximum control,
> disable Vercel's automatic deploys and use the Vercel CLI from the
> pipeline instead.

### 4.3 Sentry Source Map Upload

Source maps connect minified production code back to original source
files, making error stack traces readable. They **MUST** be uploaded
to Sentry during the CI/CD pipeline.

→ See [08-observability.md, §3.4] for full source map configuration.
→ See [08-observability.md, §3.5] for release tracking.

- **MUST** upload source maps to Sentry in the deploy pipeline
- **MUST** set `SENTRY_AUTH_TOKEN` as a GitHub Actions secret — never
  in `.env` files
- **MUST** delete client-side source maps from the production build
  after upload — they contain original source code
- **SHOULD** tag Sentry releases with the Git commit SHA for traceability
- **SHOULD** create deploy markers in Sentry to track when releases
  were deployed to each environment

### 4.4 Database Migration in CI

Database migrations execute as part of the deployment pipeline. The
migration strategy and tooling are defined in
→ See [04-database-standards.md, §6].

**For Prisma projects:**

```yaml
# In the deploy job, before the deploy step:
- name: Run Migrations
  run: npx prisma migrate deploy
  env:
    DIRECT_URL: ${{ secrets.DIRECT_URL }}
```

**For Supabase CLI projects:**

```yaml
# In the deploy job, before the deploy step:
- name: Push Migrations
  run: npx supabase db push --linked
  env:
    SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
    SUPABASE_DB_PASSWORD: ${{ secrets.SUPABASE_DB_PASSWORD }}
```

- **MUST** run migrations **before** deploying new application code —
  the new code may depend on schema changes
- **MUST** use `prisma migrate deploy` (not `prisma migrate dev`) in
  CI/production — `dev` is interactive and creates new migrations
- **MUST** use the **direct** database connection URL for migrations
  (not the pooled connection) — Prisma CLI needs a direct connection
  (→ See [04-database-standards.md, §6.2])
- **MUST NOT** run migrations as part of the application startup — they
  should be a separate, auditable pipeline step

### 4.5 Caching Strategies

CI caching reduces pipeline time by persisting dependencies and build
artifacts between runs.

| Cache Target | Key | Savings | How |
|---|---|---|---|
| npm dependencies | `package-lock.json` hash | 20-60s | `actions/setup-node` with `cache: 'npm'` |
| Next.js build cache | `.next/cache` | 30-60s | `actions/cache` with `.next/cache` path |
| Playwright browsers | Playwright version | 60-120s | `actions/cache` with browser install path |
| Docker layers | Dockerfile + context hash | 60-180s | BuildKit cache mounts or registry cache |

```yaml
# Next.js build cache (add to quality-gates job)
- name: Cache Next.js Build
  uses: actions/cache@5a3ec84eff668545956fd18022155c47e93e2684 # v4
  with:
    path: .next/cache
    key: nextjs-${{ runner.os }}-${{ hashFiles('package-lock.json') }}-${{ hashFiles('**/*.ts', '**/*.tsx') }}
    restore-keys: |
      nextjs-${{ runner.os }}-${{ hashFiles('package-lock.json') }}-
      nextjs-${{ runner.os }}-
```

- **MUST** cache npm dependencies via `actions/setup-node` with
  `cache: 'npm'` — this is free and saves 20-60s per run
- **SHOULD** cache the Next.js build cache (`.next/cache`) for faster
  incremental builds
- **SHOULD** cache Playwright browsers for E2E jobs — downloading
  browsers on every run wastes 1-2 minutes
- **MAY** use Docker BuildKit cache mounts for containerized builds

### 4.6 Pipeline Security

CI/CD pipelines are a high-value attack target. A compromised pipeline
can exfiltrate secrets, inject malicious code, or deploy backdoored
artifacts.

→ See [07-security-standards.md, §11] for full supply chain security
rules.

**Rules for this document:**

- **MUST** pin all third-party GitHub Actions to full commit SHAs —
  never use mutable tags (`@v4`, `@latest`). Tags can be silently
  repointed to malicious commits
  (→ See [07-security-standards.md, §11] for the Trivy incident)
- **MUST** use GitHub Actions secrets for all sensitive values — never
  hardcode in workflow files
- **MUST** set `timeout-minutes` on every job — runaway processes should
  not burn CI budget indefinitely
- **MUST** use environment protection rules for production secrets —
  restrict which branches and workflows can access them
- **SHOULD** use `concurrency` with `cancel-in-progress: true` for PR
  pipelines (but `false` for deploy pipelines — never cancel a deploy
  mid-flight)
- **SHOULD** minimize `permissions` in workflow files — follow least
  privilege

```yaml
# Minimal permissions example
permissions:
  contents: read       # Read repo content
  pull-requests: write # Post status checks (if needed)
  # Do NOT grant write to all scopes
```

### 4.7 GitHub Actions 2026 — Awareness

GitHub is actively evolving Actions security. The following features are
on the 2026 roadmap and should be adopted as they reach general
availability:

**Dependency Locking (coming 2026):** A new `dependencies:` section in
workflow YAML that locks all direct and transitive action dependencies
with commit SHAs — similar to `go.mod` + `go.sum`. This will make SHA
pinning automatic rather than manual.

**Egress Firewall (coming 2026):** A native Layer 7 firewall that runs
outside the runner VM, controlling outbound network access. Organizations
will be able to define allowed domains and block unauthorized data
exfiltration.

**Environment without Deployment (available now):** Workflows can use
environment secrets and variables without creating a deployment record
by setting `deployment: false`. Useful for build jobs that need secrets
but are not deployments.

**Timezone Support for Schedules (available now):** Cron schedules can
now specify IANA timezones instead of being locked to UTC.

- **SHOULD** adopt dependency locking when it reaches general availability
  — it replaces manual SHA pinning
- **MAY** evaluate egress firewall for enhanced supply chain security
  when available
- **MAY** use `deployment: false` for jobs that need environment secrets
  without creating deployment records

### 4.8 Anti-Patterns

| Anti-Pattern | Why It Is Wrong | What to Do Instead |
|---|---|---|
| **Skipping quality gates for "urgent" deploys** | Breaks trust in the pipeline; bugs reach production | Fix the pipeline, not the process — no exceptions without an ADR |
| **`cancel-in-progress: true` on deploy** | Cancelling a deploy mid-flight can leave infrastructure in an inconsistent state | Use `cancel-in-progress: false` for deploy workflows |
| **Pinning actions to tags (`@v4`)** | Tags are mutable — can be repointed to malicious commits | Pin to full commit SHAs |
| **Running migrations during app startup** | Non-auditable, can run multiple times concurrently, blocks startup | Run migrations as a separate pipeline step |
| **No timeout on CI jobs** | Runaway tests burn CI minutes indefinitely | Set `timeout-minutes` on every job |
| **Hardcoding secrets in workflow YAML** | Secrets visible in repo history — permanent exposure | Use GitHub Actions secrets |
| **`npm install` in CI** | Can modify lock file, non-deterministic | Use `npm ci` |
| **No caching** | Every run installs deps from scratch — slow and wasteful | Cache npm, Next.js build, Playwright browsers |

---

## 5. Deployment Strategies

This section defines how applications reach their hosting environment.
The deployment strategy depends on the application type: Next.js
applications default to Vercel; standalone backends (NestJS, FastAPI)
deploy as containers to Railway, Render, or Fly.io.

For the technology evaluation of hosting platforms, see
→ See [02-technology-radar.md, §4.14].

### 5.1 Vercel Deployment (Next.js Default Path)

Vercel is the default deployment target for all Next.js applications. It
provides zero-configuration deployments, automatic preview URLs per PR,
edge functions, image optimization, and a global CDN.

**How it works:**

1. Connect the GitHub repository to a Vercel project (one-time setup)
2. Push to any branch → Vercel builds and deploys automatically
3. Push to `main` → production deployment
4. Push to any other branch (or open a PR) → preview deployment with
   a unique URL

**Preview deployments** are one of Vercel's most valuable features — every
PR gets a live, shareable URL that stakeholders can review before merging.
This effectively replaces a dedicated staging environment for most
projects.

**Configuration:**

- **MUST** connect the GitHub repository for automatic deployments
- **MUST** configure environment variables in the Vercel dashboard with
  appropriate scopes (→ See §2.5)
- **MUST** set the production branch to `main`
- **SHOULD** enable preview deployments for all PRs — this is the default
  behavior
- **SHOULD** configure the build command and output directory if using a
  monorepo or non-standard project structure
- **MAY** use Vercel CLI for programmatic deploys from CI when more
  control is needed

**Vercel CLI commands:**

```bash
# Install globally
npm i -g vercel

# Link to an existing project
vercel link

# Deploy to preview
vercel deploy

# Deploy to production
vercel deploy --prod

# Pull environment variables for local development
vercel env pull .env.local
```

**Rolling Releases (awareness):**

Vercel supports Rolling Releases — a strategy that gradually shifts
traffic from the previous deployment to the new one, reducing the risk
of a bad deploy affecting all users simultaneously. This is an advanced
feature that **MAY** be evaluated for high-traffic applications.

### 5.2 Container Deployment (Railway, Render, Fly.io)

For applications that do not fit Vercel's serverless model — standalone
backends (NestJS, FastAPI), WebSocket servers, long-running workers —
use a container hosting platform.

| Platform   | Status  | Best for |
|----------|-----------|----------|
| Railway  | 🔬 Trial | Simple container hosting, managed databases |
| Render   | 🔬 Trial | Similar to Railway, web services + background workers |
| Fly.io   | 🔍 Assess| Edge-deployed containers, global latency needs |

→ See [02-technology-radar.md, §4.14] for full platform evaluations.

**General container deployment flow:**

```text
1. Build Docker image (locally or in CI)
2. Push image to container registry (Docker Hub, GHCR, platform registry)
3. Platform pulls image and runs it
4. Health check passes → traffic routes to new container
5. Old container drains and shuts down
```

**Railway-specific:**

Railway can deploy directly from a `Dockerfile` in the repo — no
separate image push required. It detects the Dockerfile automatically.

```bash
# Railway CLI deploy
railway up
```

- **MUST** include a health check endpoint in every containerized
  application — the platform uses it to determine readiness
  (→ See [08-observability.md, §5.1])
- **MUST** configure environment variables in the platform dashboard —
  never bake secrets into the Docker image
- **SHOULD** use the platform's managed database (Railway PostgreSQL,
  Render PostgreSQL) for simplicity, or connect to Supabase Cloud

### 5.3 Rollback Strategy

Every deployment must have a clear rollback path. When a deploy
introduces a bug, the fastest recovery is reverting to the previous
known-good state.

**Vercel rollback:**

Vercel maintains a history of all deployments. Rolling back is instant
— it repoints the production URL to a previous deployment without
rebuilding.

```bash
# Via Vercel dashboard: Deployments → select previous → Promote to Production
# Via CLI:
vercel rollback
```

**Container rollback:**

For container deployments, rollback means deploying the previous image
version.

```bash
# Tag-based rollback
docker pull myapp:previous-sha
railway up --image myapp:previous-sha
```

**Database rollback considerations:**

If the deployment included database migrations, rollback is more complex.
Not all migrations are reversible (dropping a column destroys data).
This is why migrations should be backward-compatible whenever possible.

→ See [04-database-standards.md, §6.5] for reversible vs. irreversible
migrations.

- **MUST** ensure every production deployment can be rolled back within
  5 minutes — either via platform UI or CLI
- **MUST** test rollback procedures periodically — a rollback plan that
  has never been tested is not a plan
- **SHOULD** design migrations to be backward-compatible so that the
  previous code version can still work with the new schema
- **MUST NOT** rely on "just fix it forward" as the only recovery
  strategy — sometimes the fix is not obvious and the outage continues

### 5.4 Deploy Verification

Every deployment must be verified before it is considered complete.
Deploy verification confirms that the new version is running correctly
and serving traffic.

**Health checks** — the minimum verification:

→ See [08-observability.md, §5.1] for health check endpoint design.

```bash
# Simple health check after deploy
curl -f https://myapp.com/api/health || echo "Deploy verification FAILED"
```

**Smoke tests** — targeted tests against production:

```bash
# Check that key pages respond
curl -f -s -o /dev/null https://myapp.com/ || exit 1
curl -f -s -o /dev/null https://myapp.com/api/health || exit 1
```

**Sentry deploy markers:**

→ See [08-observability.md, §3.5] for release tracking.

Deploy markers in Sentry allow you to correlate errors with specific
deployments — answering "did this error start with the latest deploy?"

- **MUST** verify deployment health (HTTP 200 on `/api/health`) after
  every production deploy
- **SHOULD** create Sentry deploy markers for every production deployment
- **SHOULD** monitor Sentry for new errors in the first 15 minutes after
  a deploy — elevated error rates indicate a bad deploy
- **MAY** run automated smoke tests against production after deploy

### 5.5 Anti-Patterns

| Anti-Pattern | Why It Is Wrong | What to Do Instead |
|---|---|---|
| **Deploy without verification** | Broken deploys go unnoticed until users complain | Health check + smoke tests after every deploy |
| **No rollback plan** | When things break, recovery is ad-hoc and slow | Document and test rollback procedures |
| **Deploying on Friday afternoon** | If something breaks, the team is unavailable to fix it | Deploy early in the week; avoid pre-weekend deploys |
| **Manual deploys via SSH** | Non-reproducible, error-prone, no audit trail | Automate deploys through CI/CD |
| **Deploying database migrations and code simultaneously** | If either fails, rollback is complex | Run migrations first, then deploy code |
| **No Sentry deploy markers** | Cannot correlate errors with deploys | Tag releases with Git SHA in Sentry |

---

## 6. Build Optimization

Build speed directly impacts developer productivity and CI costs. A
pipeline that takes 20 minutes per PR discourages frequent pushes and
slows the feedback loop. The target is a complete PR pipeline (quality
gates + security scan) under 10 minutes, and a full deploy pipeline
under 15 minutes.

### 6.1 Next.js Build Optimization

**Turbopack (default in Next.js 16):**

Turbopack is the default bundler in Next.js 16, replacing Webpack for
both development and production builds. It provides significantly faster
build times through incremental computation and Rust-based processing.

→ See [02-technology-radar.md, §4.1] for the Turbopack evaluation.

- **MUST** use Turbopack (the default) — do not downgrade to Webpack
  unless a documented incompatibility exists
- **SHOULD** cache the `.next/cache` directory in CI to enable
  incremental builds (→ See §4.5)

**Standalone output:**

The `output: 'standalone'` setting in `next.config.ts` produces a
self-contained build that includes only necessary files and a minimal
`server.js`. This is required for Docker deployments and recommended
for all non-Vercel deployments.

→ See §3.2 for the complete Docker pattern using standalone output.

- **MUST** enable `output: 'standalone'` for Docker-based deployments
- **SHOULD** enable `output: 'standalone'` even for Vercel deployments
  if the project may need to migrate to container hosting in the future

### 6.2 Docker Build Optimization

**BuildKit cache mounts:**

Docker BuildKit (the default builder) supports cache mounts that persist
data between builds without including it in the final image layer. This
is particularly useful for npm caches.

```dockerfile
# Instead of plain npm ci, use a cache mount:
RUN --mount=type=cache,target=/root/.npm npm ci
```

**Multi-stage layer caching:**

The multi-stage Dockerfile in §3.2 is already optimized for caching.
The key insight is that the `deps` stage (which runs `npm ci`) only
rebuilds when `package.json` or `package-lock.json` changes. On a
typical PR that only changes application code, the deps stage is cached
and the build starts from the `COPY . .` step.

**Registry-based caching for CI:**

When building Docker images in CI, the build cache is lost between runs
(each CI run starts with a clean environment). Registry-based caching
solves this by pushing and pulling cache layers from a container registry.

```bash
# Build with registry cache (GitHub Container Registry example)
docker build \
  --cache-from type=registry,ref=ghcr.io/user/myapp:cache \
  --cache-to type=registry,ref=ghcr.io/user/myapp:cache,mode=max \
  -t myapp:${{ github.sha }} .
```

- **SHOULD** use BuildKit cache mounts for npm installs in Docker builds
- **MAY** use registry-based caching for CI Docker builds when build
  time exceeds 5 minutes

### 6.3 CI Pipeline Speed Optimization

| Technique | Impact | Effort |
|-----------|--------|--------|
| Cache npm dependencies | -20-60s | Low (built into `setup-node`) |
| Cache Next.js build | -30-60s | Low (single `actions/cache` step) |
| Cache Playwright browsers | -60-120s | Low (single `actions/cache` step) |
| Run security scan in parallel | -1-3min from critical path | Low (separate job, no `needs`) |
| Use `concurrency` + `cancel-in-progress` | Avoid wasted runs | Low (2 lines of YAML) |
| Install only Chromium for E2E | -120s vs all browsers | Low (already in baseline) |
| Use `.nvmrc` with `node-version-file` | Avoid version mismatch | Low |

- **MUST** set `concurrency` with `cancel-in-progress: true` on PR
  pipelines — stale runs waste CI minutes
- **MUST** set `timeout-minutes` on every job — prevent runaway builds
- **SHOULD** run independent jobs in parallel (security scan does not
  need to wait for quality gates)
- **SHOULD** install only the browsers needed for E2E (Chromium only
  unless cross-browser is required)
  (→ See [06-testing-strategy.md, §8.3])

### 6.4 Bundle Analysis in CI

Bundle size monitoring catches unexpected size increases before they
reach production. A sudden 500KB jump in the client bundle usually means
an accidental full-library import or a server-only dependency leaking
into the client.

→ See [05-frontend-standards.md, §10] for frontend performance budgets
and bundle analysis tools.

- **SHOULD** run `next-bundle-analyzer` or `size-limit` as part of the
  CI pipeline to track bundle size trends
- **SHOULD** configure size-limit to fail CI when the bundle exceeds a
  defined threshold (e.g., 250KB gzipped for the initial load)
- **MAY** post bundle size changes as PR comments for visibility

### 6.5 Anti-Patterns

| Anti-Pattern | Why It Is Wrong | What to Do Instead |
|--------------|-----------------|--------------------|
| **No build caching** | Every build starts from scratch — slow and wasteful | Cache npm, Next.js build, Docker layers |
| **Installing all Playwright browsers** | Downloads ~1.5GB of browsers — 2+ minutes wasted | Install only Chromium: `--with-deps chromium` |
| **Sequential independent jobs** | Security scan waits for quality gates — adds 1-3 min | Run independent jobs in parallel |
| **No timeout on CI jobs** | Hung build consumes CI minutes forever | Set `timeout-minutes` per job |
| **Webpack in Next.js 16** | Slower builds, missing Turbopack optimizations | Use Turbopack (the default) |
| **No bundle size monitoring** | Accidental 1MB import goes unnoticed | Run size-limit or bundle-analyzer in CI |

---

## 7. Infrastructure Patterns (Awareness)

This section provides a decision framework for when to move beyond PaaS
platforms. For the current project scale, PaaS is the correct choice.
This section exists so that the decision to adopt custom infrastructure
is deliberate, documented, and justified — not accidental.

### 7.1 PaaS vs IaC Decision Framework

| Dimension | PaaS (Vercel, Railway, Render) | IaC (Terraform, Pulumi) |
|-----------|--------------------------------|-------------------------|
| **Setup time** | Minutes | Days to weeks |
| **Operational burden** | Near zero — platform manages infra | Significant — you manage everything |
| **Cost at small scale** | Free tiers available | Cloud resources cost from day one |
| **Flexibility** | Limited to platform capabilities | Unlimited — any cloud service |
| **Scaling** | Automatic (within tier limits) | Manual configuration required |
| **Learning curve** | Low | High (HCL for Terraform, or TS for Pulumi) |
| **Debugging** | Limited observability into infra | Full access to infrastructure |

**When PaaS is the right choice:**

- Solo developer or small team (1-3 people)
- Standard web application (Next.js, API server, database)
- Budget is limited and predictable
- Operational expertise is limited
- Time to market is more important than infra customization

**When to consider IaC:**

- Multiple services that need to communicate internally (VPC, subnets)
- Compliance requirements that mandate specific infrastructure config
- Cost optimization requires fine-grained resource control
- The team has dedicated DevOps/SRE capacity
- PaaS limits (execution time, bandwidth, regions) are consistently hit

- **MUST** start with PaaS for every new project
- **MUST** document the decision to adopt IaC in an ADR
  (→ See [01-core-principles.md, §9])
- **MUST NOT** adopt IaC to "learn it" in a production project — use a
  personal learning project instead

### 7.2 Terraform and Pulumi (Assess)

Both Terraform and Pulumi are in 🔍 Assess status on the Technology
Radar (→ See [02-technology-radar.md, §4.13]).

**Terraform:** Declarative IaC using HCL (HashiCorp Configuration
Language). Industry standard with the largest community and provider
ecosystem.

**Pulumi:** IaC using real programming languages (TypeScript, Python,
Go). Lower barrier for a TypeScript-focused team.

**When to reassess:** When a project requires custom cloud infrastructure
that PaaS platforms cannot provide — typically when managing VPCs,
custom networking, or multi-service architectures with specific
compliance requirements.

### 7.3 Kubernetes (Hold)

Kubernetes is ⛔ Hold on the Technology Radar
(→ See [02-technology-radar.md, §4.13]).

**Why Hold:** Kubernetes introduces massive operational complexity —
cluster management, networking, RBAC, monitoring, upgrades — that is
justified only when managing dozens of services across multiple nodes.
For the current project scale, a PaaS platform provides equivalent
deployment and scaling capabilities without the operational burden.

**What to use instead:** Vercel for Next.js, Railway or Render for
containerized backends.

→ See [07-security-standards.md, §12] for Kubernetes security rules
(to be applied if and when Kubernetes is adopted).

- **MUST NOT** adopt Kubernetes without a documented ADR that demonstrates
  simpler alternatives have been evaluated and found insufficient
- **MUST NOT** adopt Kubernetes because "we might need it later" — adopt
  it when you **do** need it

### 7.4 Self-Hosted vs Managed Services

| Approach | Pros | Cons | When to Use |
|----------|------|------|-------------|
| **Managed** (Vercel, Supabase Cloud, Railway) | Zero ops, automatic updates, built-in monitoring | Less control, potential vendor lock-in, cost at scale | Default for all projects |
| **Self-hosted** (VPS + Docker + Nginx) | Full control, predictable cost, no vendor lock-in | Operational burden: updates, security patches, monitoring, backups | When managed platforms are insufficient or too expensive |

- **MUST** default to managed services for all new projects
- **MUST** document the decision to self-host in an ADR
- **SHOULD** have a concrete, measurable reason to self-host (cost
  analysis, compliance requirement, feature gap) before doing so

### 7.5 Anti-Patterns

| Anti-Pattern | Why It Is Wrong | What to Do Instead |
|--------------|-----------------|--------------------|
| **Kubernetes for a 3-service app** | Massive operational overhead for minimal benefit | Use PaaS (Vercel, Railway) |
| **IaC for a personal project** | Learning overhead delays shipping | Use PaaS; learn IaC in a dedicated learning project |
| **Self-hosting "to save money"** | The hidden cost of operations (updates, security, monitoring) often exceeds PaaS pricing | Calculate total cost including time spent on ops |
| **No ADR before infra change** | Critical infrastructure decisions made without documentation | ADR for every move beyond PaaS |

---

## 8. DevOps by Project Stage

Not every project needs the same DevOps sophistication. A personal
learning project should not have Terraform, and a production SaaS
should not deploy manually. This section provides a progressive guide
for scaling DevOps practices as projects grow.

### 8.1 Personal Project / Learning

**Goal:** Ship fast, learn, iterate.

| Layer | Approach |
|-------|----------|
| Hosting | Vercel free tier (Hobby) |
| Database | Supabase free tier |
| CI/CD | GitHub Actions (free for public repos) — quality gates only |
| Docker | Not needed — Vercel handles builds |
| Environments | Development + Production only |
| Monitoring | Sentry free tier (→ 08) |

**Minimum checklist:**

- `.env.example` committed with all required variables
- Environment variables validated with `@t3-oss/env-nextjs`
- GitHub repo connected to Vercel for automatic deploys
- Sentry configured for error tracking
- `.nvmrc` with the Node.js version

### 8.2 Freelance Client MVP

**Goal:** Professional delivery, client confidence, fast iteration.

| Layer | Approach |
|-------|----------|
| Hosting | Vercel Pro ($20/month/seat) or Hobby (if within limits) |
| Database | Supabase Pro ($25/month) for backups and higher limits |
| CI/CD | GitHub Actions — quality gates + security scan |
| Docker | Docker Compose for local dev (database, services) |
| Environments | Development + Preview (per PR) + Production |
| Monitoring | Sentry + UptimeRobot (→ 08) |

**Additional over Personal:**

- CI pipeline with quality gates (→ 06 §8) running on every PR
- `npm audit` in CI for dependency vulnerability scanning
- Vercel preview deployments for client review
- Health check endpoint (`/api/health`)
- UptimeRobot monitoring on production URL

### 8.3 Growing Product

**Goal:** Reliability, team collaboration, observability.

| Layer | Approach |
|-------|----------|
| Hosting | Vercel Pro + Railway/Render for backend services |
| Database | Supabase Pro with point-in-time recovery |
| CI/CD | Full pipeline — quality gates + security + E2E + deploy |
| Docker | Dockerized backend services, Docker Compose for local dev |
| Environments | Development + Preview + Staging + Production |
| Monitoring | Sentry + UptimeRobot + structured logging (→ 08) |

**Additional over Freelance MVP:**

- Docker-based backend deployment (Railway or Render)
- E2E tests in CI (Playwright)
- Sentry source map upload and release tracking
- Database migrations in CI pipeline
- Bundle size monitoring in CI
- Staging environment for QA

### 8.4 Production at Scale

**Goal:** Operational excellence, compliance, disaster recovery.

| Layer | Approach |
|-------|----------|
| Hosting | Vercel Enterprise or custom infrastructure |
| Database | Supabase Enterprise or managed PostgreSQL (RDS, Cloud SQL) |
| CI/CD | Full pipeline + container scanning + IaC validation |
| Docker | Full containerization with registry-based caching |
| Environments | Development + Preview + Staging + Production + Disaster Recovery |
| Monitoring | Full observability stack (→ 08) + custom dashboards |
| IaC | Terraform or Pulumi — evaluate based on need |

**Additional over Growing Product:**

- Container image vulnerability scanning (Grype, Trivy)
- Infrastructure as Code (if PaaS limits are reached)
- Secret rotation automation
- Multi-region deployment (if user base is global)
- Disaster recovery runbooks

### 8.5 Decision Guide — When to Add Each Layer

```text
Project start
    │
    ├── Always: .env.example, env validation, .nvmrc, Sentry
    │
    ├── First client / first user: CI quality gates, UptimeRobot,
    │   health check endpoint, preview deployments
    │
    ├── First team member: Docker Compose for local dev,
    │   branch protection, required PR reviews
    │
    ├── Backend service needed: Docker, Railway/Render,
    │   container health checks
    │
    ├── Growing user base: E2E in CI, Sentry source maps,
    │   staging environment, bundle monitoring
    │
    ├── Compliance / scale: Container scanning, IaC evaluation,
    │   secret rotation, multi-environment
    │
    └── Never (at current scale): Kubernetes, Jenkins,
        self-hosted CI, custom orchestration
```

- **MUST** implement each layer only when the project stage justifies it
  — premature complexity slows development
- **MUST NOT** skip foundational layers (env validation, CI quality gates)
  because the project is "small" — these catch bugs regardless of scale
- **SHOULD** move to the next stage when the current setup becomes a
  bottleneck, not in anticipation of future needs

---

## 9. DevOps Checklist

### 9.1 New Project Setup Checklist

```text
□ .nvmrc (or .node-version) — pin Node.js version
□ .env.example — all required variables with placeholders
□ .gitignore — includes .env, .env.*, node_modules, .next, dist
□ src/env.ts — @t3-oss/env-nextjs with Zod validation
□ next.config.ts — imports env.ts for build-time validation
□ compose.yaml — Docker Compose for local services (if needed)
□ .dockerignore — excludes sensitive and unnecessary files (if Docker)
□ Dockerfile — multi-stage build (if container deployment)
□ .github/workflows/ci.yml — quality gates pipeline (→ 06 §8)
□ GitHub repo connected to Vercel (if Next.js)
□ Environment variables configured in Vercel/platform dashboard
□ Sentry project created and SDK configured (→ 08 §3)
□ /api/health endpoint implemented (→ 08 §5.1)
□ UptimeRobot monitor on production URL (→ 08 §5.2)
□ README.md — setup instructions, env var documentation
```

### 9.2 Pre-Deployment Checklist

```text
□ All CI quality gates pass (lint, typecheck, test, build)
□ Security scan passes (npm audit, no high/critical vulnerabilities)
□ E2E tests pass (if configured)
□ Environment variables verified for target environment
□ Database migrations reviewed and tested locally
□ No NEXT_PUBLIC_ prefix on server-only secrets
□ Bundle size within acceptable limits
□ PR reviewed and approved
□ Deployment branch is up to date with main
□ Rollback plan confirmed (previous deploy available)
```

### 9.3 Post-Deployment Verification Checklist

```text
□ Health check endpoint returns 200 (/api/health)
□ Key pages load correctly (homepage, login, dashboard)
□ Sentry deploy marker created
□ No new errors in Sentry (monitor for 15 minutes)
□ UptimeRobot confirms uptime
□ Database migrations applied successfully (if any)
□ Source maps working in Sentry (trigger test error, verify stack trace)
□ Environment-specific features working (payments in test mode for preview)
```

### 9.4 Environment Security Audit Checklist

```text
□ No secrets committed to Git history (run gitleaks or trufflehog)
□ .env files are in .gitignore
□ NEXT_PUBLIC_ variables audited — no server secrets exposed
□ Production secrets differ from development/preview
□ GitHub Actions secrets configured (not hardcoded in YAML)
□ Environment protection rules on production environment
□ Secret rotation dates documented
□ Container images scanned for vulnerabilities (if Docker)
□ CI actions pinned to full commit SHAs (not tags)
□ npm audit has no high/critical findings
```

→ See [07-security-standards.md, §7] for full secrets management rules.
→ See [07-security-standards.md, §11] for full supply chain security rules.
→ See [07-security-standards.md, §12] for full container security rules.

---

## 10. Monorepo CI Pitfalls

Monorepos introduce CI challenges that do not exist in single-package
repositories. The issues below are non-obvious, platform-dependent,
and have caused multi-day debugging sessions in real projects.

### 10.1 Prisma — Shared Generated Client in Hoisted node_modules

When multiple workspaces in a monorepo depend on `@prisma/client`,
npm hoists the package to the root `node_modules/`. All workspaces
share the same `node_modules/.prisma/client/` directory, which means
**the last `prisma generate` to run overwrites all previous ones**.

- **MUST** generate Prisma clients in dependency order — the workspace
  with the **largest schema** (superset of models) MUST generate last.
  This ensures all model types are available to all consumers.

  ```yaml
  # GOOD — superset (web, 12 models) generates last
  - name: Generate Prisma Clients
    run: |
      cd apps/whatsapp-service && npx prisma generate  # 1 model
      cd ../../apps/web && npx prisma generate          # 12 models (superset)
  ```

  ```yaml
  # BAD — subset generates last, overwrites superset types
  - name: Generate Prisma Clients
    run: |
      npx prisma generate --schema apps/web/prisma/schema.prisma
      npx prisma generate --schema apps/whatsapp-service/prisma/schema.prisma
  ```

- **MUST** run `prisma generate` from inside the workspace directory
  (not from the monorepo root with `--schema`). The working directory
  affects where Prisma locates `prisma.config.ts` and resolves the
  output path.

- **SHOULD** add a CI comment explaining why the generation order
  matters — without it, a future contributor will reorder alphabetically
  and break the pipeline silently.

- **SHOULD** consider using Prisma's `output` option in the schema
  generator to write each workspace's client to a unique path, avoiding
  the overwrite problem entirely. This is the architecturally correct
  long-term solution but requires import path changes across the
  codebase.

### 10.2 Turborepo — Environment Variable Filtering

Turborepo does not automatically pass all environment variables from
the parent process to task subprocesses. Variables that are not declared
in `turbo.json` may be silently filtered.

- **MUST** declare CI-only environment variables (e.g.,
  `SKIP_ENV_VALIDATION`, `CI`, `SENTRY_AUTH_TOKEN`) in
  `globalPassThroughEnv` in `turbo.json`:

  ```json
  {
    "globalPassThroughEnv": ["SKIP_ENV_VALIDATION", "CI"]
  }
  ```

- **MUST** use `globalPassThroughEnv` (not `globalEnv`) for CI flags
  that should not affect the Turbo cache hash. `globalEnv` includes
  the variable in cache key computation — changing the value
  invalidates all cached tasks.

- **SHOULD** test CI environment variable propagation explicitly when
  adding a new env var to the pipeline. A variable that works in
  `npm run build` may not work in `turbo run build`.

### 10.3 ESLint projectService — Cross-Platform Divergence

The `typescript-eslint` `projectService` option uses TypeScript's
language service API, which can resolve types differently on Linux
vs Windows for monorepo setups with hoisted dependencies. This
manifests as `no-unsafe-*` false positives in CI that do not appear
locally.

- **SHOULD** treat `tsc --noEmit` as the authoritative type-safety
  gate, not ESLint typed-linting rules. The TypeScript compiler
  produces identical results across platforms; the ESLint
  `projectService` does not always do so.

- **SHOULD** validate ESLint typed-linting rules on the CI platform
  early in the project, before accumulating thousands of lines of
  code. Cross-platform divergence is easier to fix in a small
  codebase.

- **MAY** use ESLint overrides to suppress typed-linting false
  positives when they are confirmed to be platform-specific. Document
  the suppression with an ADR reference and ensure `tsc --noEmit`
  remains active as the safety net.

### 10.4 Next.js Build — Environment Validation at Compile Time

Next.js executes `next.config.ts`, `instrumentation.ts`, and Sentry
config files during `next build`. If any of these files (directly or
transitively) call an environment validation function, the build will
fail in CI where production secrets are not available.

- **MUST** guard all environment validation functions with a
  `SKIP_ENV_VALIDATION` check **inside the function itself**, not
  only at the call site:

  ```typescript
  // GOOD — guard inside the function covers all call sites
  export function validateEnv(): Env {
    if (process.env.SKIP_ENV_VALIDATION === "true") {
      return process.env as unknown as Env;
    }
    const parsed = envSchema.safeParse(process.env);
    // ...
  }
  ```

  ```typescript
  // INSUFFICIENT — only covers this one call site
  // next.config.ts
  if (!process.env.SKIP_ENV_VALIDATION) {
    validateEnv();
  }
  ```

- **MUST** ensure the skip flag reaches the build process — see § 10.2
  (Turborepo environment variable filtering).

### 10.5 npm ci — Workspace postinstall Scripts

`npm ci` does not reliably run `postinstall` scripts for individual
workspaces in all npm versions and monorepo configurations. Code
generation steps (Prisma, Next.js typegen) that depend on
`postinstall` may silently not run.

- **MUST** add explicit CI steps for any code generation that is
  normally triggered by `postinstall`:

  ```yaml
  # Do not rely on postinstall — run explicitly
  - name: Generate Prisma Clients
    run: cd apps/web && npx prisma generate

  - name: Generate Next.js types
    working-directory: apps/web
    run: npx next typegen
  ```

- **SHOULD** keep `postinstall` in `package.json` for local
  development convenience, but never depend on it for CI correctness.
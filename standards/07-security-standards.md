# 🔒 Security Standards (Security by Design)

> **Scope:** Universal security standards applicable to any modern web application, regardless of technology stack.
>
> **Purpose:** A comprehensive, reusable security baseline ensuring every project is secure by design — from development through production and incident response.
>
> **Keywords:**
> - **MUST** = required (deployment should be blocked if violated)
> - **SHOULD** = strongly recommended (requires justification to skip)
> - **MAY** = optional (case-by-case)

---

## 0. How to Use This Document

- This document defines **security standards** — principles, controls, and
  checklists that apply across every layer of every application.
- It does **not** define which security tools to use (that lives in
  → See [02-technology-radar.md]) or how to implement specific features like
  API design or database access — those belong in their domain documents.
  This document defines the **security constraints** those implementations
  must satisfy.
- Security rules in this document **take precedence** over all other
  domain documents when rules overlap. If [03-api-design.md] says SHOULD
  and this document says MUST for the same concern, MUST wins.
- Code examples use **TypeScript** (Node.js) and **Python** where
  applicable, reflecting the Adopt choices in
  → See [02-technology-radar.md].

### Document Relationships

```text
07-security-standards.md (this document)
 ├── Derives from    → 01-core-principles.md (fail-fast, security by default, least privilege)
 ├── Constrains      → 03-api-design.md (input validation, rate limiting, auth, CORS, error responses)
 ├── Constrains      → 04-database-standards.md (RLS, encryption at rest, SQL injection, connection security)
 ├── Constrains      → 05-frontend-standards.md (XSS, CSP, security headers, client-side validation scope)
 ├── Constrains      → 08-observability.md (PII in logs, audit trail, security event logging)
 ├── Constrains      → 09-devops-cicd.md (container security, secrets in CI, dependency scanning)
 ├── Referenced by   → 06-testing-strategy.md (security testing patterns)
 ├── Referenced by   → 10-git-workflow.md (secret detection, pre-commit hooks)
 ├── Referenced by   → 11-project-management.md (security checklists, incident process)
 └── Provides        → templates/incident-report.md, templates/data-inventory.md
```

### Boundary Definitions

| Question | This Document (07) | Other Document |
|---|---|---|
| **Which** security tools to use? | — | → See [02-technology-radar.md] |
| **How** to validate input (security rules)? | ✅ Section 3 (authoritative for security) | → See [03-api-design.md, §6] (Zod patterns) |
| **How** to implement authentication? | ✅ Section 4 (security constraints) | → See [03-api-design.md, §9] (API patterns) |
| **How** to implement RLS? | — | → See [04-database-standards.md, §7] (authoritative) |
| **How** to encrypt data? | ✅ Section 8 | — |
| **How** to configure security headers? | ✅ Section 9 | — |
| **How** to handle RGPD compliance? | ✅ Section 14 (authoritative) | → templates/data-inventory.md |
| **How** to respond to incidents? | ✅ Section 16 | → templates/incident-report.md |
| **How** to manage secrets in CI/CD? | — | → See [09-devops-cicd.md, §2] (env management) |
| **How** to manage environment variables? | ✅ §3 (security constraints only) | → See [09-devops-cicd.md, §2] (authoritative for patterns) |

### Technology Versions

| Technology | Version | Role |
|---|---|---|
| OWASP Top 10 | 2025 Edition | Threat reference |
| Zod | 4.x | Input validation (TypeScript) |
| Pydantic | 2.x | Input validation (Python) |
| Argon2id | — | Password hashing (preferred) |
| bcrypt | cost ≥ 12 | Password hashing (minimum) |
| gitleaks | 8.x | Secret detection (pre-commit) |
| Trivy | 0.69.3+ | Container + dependency scanning (pin to verified SHA) |
| Snyk | Latest | Multi-language dependency scanning |
| DOMPurify | Latest | HTML sanitization |

### AI Agent Instructions

This document is designed to be consumed by AI coding agents (e.g., Claude
Code). When interpreting this document:

- **MUST**, **SHOULD**, and **MAY** are RFC 2119 keywords — treat MUST as
  non-negotiable constraints, SHOULD as strong defaults that require
  explicit justification to override, and MAY as contextual options.
- Security rules are non-negotiable. This document takes precedence over
  all other domain documents when rules overlap.
- Cross-references (→ See [XX-document.md]) point to authoritative
  definitions — always defer to the referenced document for the full rule.
- BAD/GOOD code examples are pattern-matching references — apply the
  principle behind the example, not just the literal code.
- The Pre-Deployment Security Checklist (§17) is a mandatory gate — never
  skip checklist items without documented justification.
- Anti-pattern tables describe common mistakes — use them as negative examples when reviewing or generating code.
- If generating code requires violating a MUST rule, the AI **MUST stop** and ask the human for permission before proceeding — never silently override a standard.
- **MUST NOT** over-engineer — always prefer the simplest solution that meets the stated requirements. Do not add abstractions, patterns, or infrastructure beyond what was explicitly requested (→ See [01-core-principles.md, §12]).

---

## 1. Security Principles

Every security decision in this document derives from four foundational principles.
Deviating from any of them **MUST** be documented in an ADR with explicit risk acceptance.

### Zero Trust

- **MUST** authenticate and authorize every request, even between internal services
- **MUST** never trust data from any source (client, external API, internal service) without validation
- **MUST** never rely solely on network boundaries (VPC, firewall) as a security control

### Least Privilege

- **MUST** grant the minimum permissions necessary for any user, service, or component to perform its function
- **MUST** scope database credentials, API keys, and service accounts to their specific purpose (no shared "admin" keys across services)
- **SHOULD** review and revoke unused permissions periodically

### Defense in Depth

- **MUST** implement multiple independent security layers — never depend on a single control
- Security layers (from outer to inner):
  1. Network/Transport (TLS, firewalls, CDN protection)
  2. Application (authentication, rate limiting, input validation)
  3. Business Logic (authorization checks in services)
  4. Data (RLS, encryption at rest, parameterized queries)
- If any single layer fails, the remaining layers **MUST** still prevent unauthorized access or data exposure

### Fail Secure

- **MUST** default to denying access when a security control fails (auth service down → reject, not allow)
- **MUST NOT** expose system internals in error responses (stack traces, DB errors, internal paths)
- **MUST** log security failures for investigation while returning generic error messages to the client

---

## 2. Threat Modeling (Lightweight — STRIDE)

Every feature that handles user data, authentication, payments, or external integrations **MUST** go through a lightweight threat assessment before implementation.

### Process (Per Feature / Epic)

1. **Identify assets**: What data or capability does this feature expose? (e.g., user PII, payment info, admin actions)
2. **Map trust boundaries**: Where does data cross from untrusted to trusted zones? (e.g., client → API, API → database, service → external API)
3. **Apply STRIDE**: For each trust boundary, ask the six threat questions:

   | Threat                     | Question to Ask                                          |
   |----------------------------|----------------------------------------------------------|
   | **Spoofing**               | Can someone impersonate a legitimate user or service?    |
   | **Tampering**              | Can someone modify data in transit or at rest?           |
   | **Repudiation**            | Can someone perform an action and deny it later?         |
   | **Info Disclosure**        | Can sensitive data leak through responses, logs, or errors? |
   | **Denial of Service**      | Can someone degrade or disable the service?              |
   | **Elevation of Privilege** | Can a user gain access beyond their authorized role?     |

4. **Document mitigations**: For each identified threat, note the control that addresses it (e.g., "Spoofing → JWT validation + session binding")
5. **Accept or escalate residual risk**: If a threat cannot be fully mitigated, document the accepted risk in an ADR

### Rules

- **MUST** perform STRIDE analysis for: authentication flows, payment processing, file uploads, admin/backoffice features, and any endpoint exposing PII
- **SHOULD** perform STRIDE analysis for all new features that involve data mutation or cross trust boundaries
- **SHOULD** extend STRIDE with the AI-specific threat surface when a feature uses an LLM or agent — prompt injection and the *lethal trifecta* (untrusted input + access to private data + an exfiltration path) fall outside the six classic categories. → See [12-ai-engineering.md, §6.7]
- **SHOULD** document threat assessments inline in the feature's issue/ticket or in `docs/security/`
- **MAY** use a simplified one-line-per-threat format for low-risk features:

  ```md
  ## Threat Assessment: [Feature Name]
  - Spoofing: Mitigated by [control]
  - Tampering: Mitigated by [control]
  - Repudiation: Mitigated by [control]
  - Info Disclosure: Mitigated by [control]
  - DoS: Mitigated by [control]
  - Elevation: Mitigated by [control]
  ```

### When to Revisit

- **MUST** revisit threat model when the feature scope changes significantly
- **SHOULD** revisit when new integrations or data sources are added

---

## 3. Input Validation & Sanitization

> **Ownership note:** This section defines input validation from the
> **security** perspective — what MUST be validated, sanitized, and
> escaped, and what attack vectors validation prevents. For the **API
> implementation patterns** (Zod schemas, middleware, response
> validation), see → See [03-api-design.md, §6]. This section takes
> precedence when security rules and API convenience rules conflict.

### Core Rule

- **MUST** validate ALL input on the server — client-side validation is UX only, never a security control
- **MUST** treat every external input as untrusted: request body, query params, path params, headers, cookies, file uploads, webhook payloads

### Validation Rules

- **MUST** validate input at the application boundary (API route / controller) before any processing
- **MUST** use a schema-based validation library appropriate to the stack:

  | Stack            | Recommended Libraries                      |
  |------------------|--------------------------------------------|
  | TypeScript/Node  | Zod (preferred), io-ts                     |
  | Python           | Pydantic (preferred), marshmallow, cerberus |
  | General          | JSON Schema (OpenAPI-driven validation)    |

- **MUST** enforce:
  - Type correctness (string, number, boolean, date — never trust raw types)
  - Allowed value ranges (min/max length, min/max number, enums for fixed sets)
  - Required vs optional fields explicitly declared
  - Maximum payload size limits at the server/framework level
- **MUST** fail fast — reject invalid input immediately, before reaching business logic or database
- **MUST** return structured, predictable error responses that describe which fields failed and why (without exposing internals)
- **MUST NOT** rely on database constraints as the primary validation layer — they are the last safety net, not the first

#### Server Actions (Next.js)

Next.js Server Actions are compiled into HTTP POST endpoints. They MUST
be treated with the same security rigor as API Route Handlers:

- **MUST** validate all inputs with Zod inside the Server Action
- **MUST** verify authentication and authorization before any processing
- **MUST NOT** rely on TypeScript types alone for security — types are
  stripped at runtime and provide zero protection against malicious input
- **MUST NOT** assume Server Actions are "safe" because they run on the
  server — they are publicly callable via HTTP

> → See [03-api-design.md, §1.5] for implementation patterns.

### Sanitization Rules

- **MUST** sanitize user-generated content before rendering in HTML contexts (use DOMPurify or equivalent — never trust raw HTML from users)
- **MUST** use parameterized queries / prepared statements for all database operations — never concatenate or interpolate user input into SQL
- **MUST** escape output appropriate to the context:

  | Output Context | Escaping Strategy                                         |
  |----------------|-----------------------------------------------------------|
  | HTML body      | HTML entity encoding (or framework auto-escaping)         |
  | HTML attribute | Attribute encoding                                        |
  | JavaScript     | JS string escaping (avoid inline scripts)                 |
  | URL parameter  | URL encoding (encodeURIComponent)                         |
  | SQL            | Parameterized queries (never manual escaping)             |
  | Shell commands | Avoid entirely; if unavoidable, use safe APIs with argument arrays |

- **MUST NOT** use blocklist-based sanitization (e.g., "remove `<script>` tags") — attackers always find bypasses. Use allowlist-based approaches
- **MUST NOT** attempt to manually sanitize SQL — always use parameterized queries

### File Upload Validation

- **MUST** validate file type by inspecting magic bytes (file signature), not just the file extension or MIME type from the client
- **MUST** enforce maximum file size at both the server framework level and application level
- **MUST** rename uploaded files (use UUIDs) — never use the original client-provided filename in storage paths
- **MUST** store uploaded files outside the web root (or in object storage like S3/R2) — never in a publicly served directory
- **SHOULD** scan uploaded files for malware in high-risk applications (e.g., ClamAV)
- **MUST NOT** execute or interpret uploaded files server-side

### Environment Variable Validation

- **MUST** validate all environment variables at application startup and fail fast if any required value is missing or malformed
- **MUST** centralize env validation in a single module (e.g., `src/config/env.ts`, `config/settings.py`)
- **MUST** separate public (client-safe) from private (server-only) variables with clear naming conventions (e.g., `NEXT_PUBLIC_*` in Next.js)

> For the full environment management guide (validation patterns, `.env`
> conventions, Vercel scoping), see → See [09-devops-cicd.md, §2]. This
> section defines only the security constraints.

### Defense in Depth — Validation Layers

```text
Layer 1: Client-side       → UX feedback (not security)
Layer 2: API boundary      → Schema validation (Zod, Pydantic) — PRIMARY
Layer 3: Service layer     → Business rule validation (domain invariants)
Layer 4: Database           → Constraints, CHECK, NOT NULL, UNIQUE — LAST SAFETY NET
```

All four layers **SHOULD** be present. Layer 2 is the **minimum mandatory** control.

---

## 4. Authentication Standards

### Strategy Selection

Choose the authentication model based on project requirements. Document the choice in an ADR.

| Model                   | Best For                                     | Key Concern                        |
|-------------------------|----------------------------------------------|------------------------------------|
| Session-based (cookies) | SSR web apps, browser-only clients           | Requires server-side session store |
| Token-based (JWT)       | APIs consumed by mobile, SPAs, third-parties | Hard to revoke before expiry       |
| Managed Auth provider   | Most projects (recommended default)          | External dependency                |

- **SHOULD** prefer a managed auth provider (Supabase Auth, Auth.js, Clerk, Firebase Auth) as the default — authentication is high-risk to build from scratch
- **MUST** document auth strategy choice in an ADR

### Credential Handling

- **MUST** hash passwords with a modern, slow algorithm:
  - Recommended: **Argon2id** (preferred) or **bcrypt** (minimum cost factor 12)
  - Acceptable: **scrypt**
  - **MUST NOT** use: MD5, SHA-1, SHA-256 (alone), or any fast hash for passwords
- **MUST NOT** store plaintext passwords under any circumstance
- **MUST NOT** log passwords, tokens, or session identifiers — not even partially
- **MUST** enforce minimum password complexity:
  - Minimum 10 characters (NIST SP 800-63B recommendation)
  - **SHOULD** check against known breached passwords (e.g., HaveIBeenPwned API)
  - **SHOULD NOT** enforce arbitrary complexity rules (uppercase + symbol + number) — length matters more than complexity per NIST guidelines

### Session Security

- **MUST** set cookie flags for session cookies:
  - `HttpOnly` — prevents JavaScript access (XSS protection)
  - `Secure` — transmitted only over HTTPS
  - `SameSite=Lax` (minimum) or `Strict` — CSRF protection
  - `Path=/` — scoped appropriately
- **MUST** define session expiration:
  - Idle timeout: **SHOULD** expire after 15–30 minutes of inactivity for sensitive applications
  - Absolute timeout: **MUST** enforce a maximum session lifetime (e.g., 24h for standard apps, 1h for admin/financial)
- **MUST** regenerate session ID after successful login (prevents session fixation attacks)
- **MUST** invalidate all sessions on password change
- **SHOULD** implement refresh token rotation for token-based flows (each refresh token is single-use)

### JWT-Specific Rules (When Using Tokens)

- **MUST** use asymmetric signing (RS256, ES256) for multi-service architectures
- **MAY** use symmetric signing (HS256) for single-service applications only
- **MUST** set short expiration on access tokens (recommended: 15 minutes or less)
- **MUST** validate ALL claims on every request: `exp` (expiration), `iss` (issuer), `aud` (audience)
- **MUST NOT** store sensitive data in the JWT payload — it is base64-encoded, not encrypted (anyone can read it)
- **MUST NOT** store JWTs in localStorage (vulnerable to XSS) — prefer HttpOnly cookies or in-memory storage with refresh flow
- **MUST** implement a revocation strategy for critical scenarios:
  - Token blacklist (Redis-backed) or short expiry + refresh rotation
  - **MUST** be able to revoke access when a user is banned, password is changed, or a breach is detected

### Multi-Factor Authentication (MFA)

- **SHOULD** offer MFA for applications handling sensitive data, financial transactions, or admin access
- **SHOULD** support TOTP (e.g., Google Authenticator, Authy) as the baseline MFA method
- **MAY** support WebAuthn/Passkeys for stronger phishing-resistant authentication
- **MUST NOT** use SMS-based 2FA as the sole MFA option (vulnerable to SIM swapping) — acceptable only as a fallback

### OAuth / Social Login (When Applicable)

- **MUST** validate the `state` parameter to prevent CSRF in OAuth flows
- **MUST** verify tokens with the identity provider (never trust client-provided tokens)
- **MUST** validate redirect URIs against a strict allowlist — never accept arbitrary redirect URLs
- **SHOULD** request minimal scopes (least privilege)

### Account Security Controls

- **MUST** implement account lockout or progressive delays after repeated failed login attempts (e.g., exponential backoff or temporary lock after 5 failures)
- **MUST** implement secure password reset flow:
  - Time-limited tokens (max 1 hour)
  - Single-use (invalidate after use)
  - Sent only to the verified email address
  - **MUST NOT** reveal whether an email exists in the system ("If this email exists, you will receive a reset link")
- **SHOULD** notify users of security events: new device/location login, password change, MFA changes

---

## 5. Authorization (RBAC / ABAC)

Authorization answers: "What is this authenticated user allowed to do?"

### Core Rules

- **MUST** enforce authorization on the SERVER for every protected action — frontend visibility controls (hiding buttons, routes) are UX only, never security
- **MUST** check authorization AFTER authentication — never authorize an unauthenticated request
- **MUST** default to DENY — if no explicit rule grants access, access is denied
- **MUST NOT** rely on security through obscurity (hidden URLs, unlinked pages, undocumented endpoints)

### Model Selection

| Model            | When to Use                                  | Complexity |
|------------------|----------------------------------------------|------------|
| RBAC (default)   | Most applications — roles map to permissions | Low        |
| RBAC + Ownership | When users own resources and access is scoped | Medium    |
| ABAC             | Complex policies (multi-attribute decisions) | High       |

- **SHOULD** start with RBAC as the default model
- **MUST** document the authorization model in an ADR
- **MUST** require an ADR to migrate from RBAC to ABAC

### RBAC Implementation Rules

- **MUST** define roles and their permissions centrally in a single source of truth (e.g., `src/config/permissions.ts`, database table, or policy file)
- **MUST NOT** hardcode role checks scattered across the codebase:

  ```ts
  // BAD — role check scattered in handler, fragile
  if (user.role === "admin") { /* allow */ }

  // GOOD — centralized permission check
  if (hasPermission(user, "vehicles:delete")) { /* allow */ }
  ```

- **SHOULD** define permissions as granular actions on resources:
  - Format: `resource:action` (e.g., `vehicles:create`, `users:read`, `invoices:export`)
  - Map roles to sets of permissions:

  ```ts
  const ROLE_PERMISSIONS = {
    admin:   ["vehicles:*", "users:*", "partners:*", "invoices:*"],
    partner: ["vehicles:create", "vehicles:read", "vehicles:update",
              "leads:read", "invoices:read"],
    viewer:  ["vehicles:read", "leads:read"],
  } as const;
  ```

- **SHOULD** implement permission checks in a reusable middleware or guard (not duplicated per route)

### Resource-Level Authorization (Ownership / IDOR Prevention)

- **MUST** verify that the authenticated user has access to the SPECIFIC resource being requested — not just the resource type
- **MUST** check ownership or scope on every read, update, and delete operation:

  ```ts
  // BAD — checks role but not ownership (IDOR vulnerability)
  async function getInvoice(invoiceId: string, user: AuthUser) {
    return await db.invoices.findById(invoiceId);
  }

  // GOOD — checks role AND ownership
  async function getInvoice(invoiceId: string, user: AuthUser) {
    const invoice = await db.invoices.findById(invoiceId);
    if (!invoice) throw new NotFoundError("Invoice");
    if (invoice.userId !== user.id && !hasPermission(user, "invoices:read_all")) {
      throw new ForbiddenError("Access denied to this resource");
    }
    return invoice;
  }
  ```

- **SHOULD** enforce resource scoping at the query level when possible (more secure — data never leaves the DB):

  ```ts
  // BEST — the unauthorized data is never even fetched
  const invoice = await db.invoices.findOne({
    where: { id: invoiceId, userId: user.id }
  });
  ```

- **MUST** apply equivalent checks in Supabase via RLS policies — RLS is the database-level enforcement of ownership rules

### Multi-Tenant Authorization

- **MUST** enforce tenant isolation — a user in Tenant A must NEVER access data from Tenant B
- **MUST** include tenant scoping in every query (either via RLS or application-level filters)
- **SHOULD** treat tenant boundary violations as critical security incidents

### Authorization in the Service Layer

- **MUST** centralize authorization logic in the service layer — not in UI components, not in repository/data layer
- **SHOULD** implement authorization as a composable function or middleware:

  ```text
  Request → Authentication → Authorization Check → Service Logic → Response
                                    ↓
                              Deny (403) if unauthorized
  ```

- **MUST** log authorization failures with context (userId, resource, action, reason) for audit purposes

### Audit Trail for Sensitive Actions

- **MUST** log all state-changing operations on protected resources: Who (userId), What (action), Which (resourceId), When (timestamp), Result (success/failure)
- **SHOULD** store audit logs in a separate, append-only store (not the same table as the resource)
- **MUST NOT** allow users to modify or delete their own audit log entries

> **AI agents as actors.** When the actor is an AI agent, authorization is necessary but not
> sufficient: agent-initiated side-effecting actions also pass the action-safety gate (validate →
> authorize → human-confirm where irreversible → idempotent execute → audit `agent.action.*`, §15).
> → See [12-ai-engineering.md, §6.8].

---

## 6. API Security (Rate Limiting, Throttling, Abuse Prevention)

### Rate Limiting

- **MUST** implement rate limiting on ALL public-facing APIs
- **MUST** apply stricter limits on sensitive endpoints:

  | Endpoint Category                     | Recommended Limit           | Rationale                     |
  |---------------------------------------|-----------------------------|-------------------------------|
  | Authentication (login, register, reset) | 5–10 req/min per IP       | Brute force prevention        |
  | Password reset / OTP                  | 3–5 req/min per IP          | Token guessing prevention     |
  | Contact forms / lead gen              | 3–5 req/min per IP          | Spam prevention               |
  | Standard read endpoints               | 60–120 req/min per user     | Normal usage headroom         |
  | File upload                           | 5–10 req/min per user       | Resource exhaustion prevention|
  | Admin / backoffice                    | 30–60 req/min per user      | Lower traffic, higher risk    |
  | Webhooks (inbound)                    | Based on provider SLA       | Varies by integration         |

- **MUST** return `429 Too Many Requests` with a `Retry-After` header when limit is exceeded
- **SHOULD** implement rate limiting at multiple levels (defense in depth):

  ```text
  Layer 1: CDN / Reverse Proxy (Cloudflare, Nginx)  → IP-based, coarse
  Layer 2: API Gateway / Middleware                   → User/key-based, granular
  Layer 3: Application (per-endpoint)                 → Business-rule-based
  ```

- **SHOULD** use sliding window or token bucket algorithms — fixed window allows burst attacks at window boundaries
- **MUST** identify callers appropriately:
  - Unauthenticated: rate limit by IP (with awareness of shared IPs / NAT)
  - Authenticated: rate limit by user ID or API key (more accurate)

#### Recommended Tools

| Context                      | Tools                                                      |
|------------------------------|------------------------------------------------------------|
| CDN / Edge                   | Cloudflare Rate Limiting, AWS WAF                          |
| Node.js middleware           | express-rate-limit, @nestjs/throttler, rate-limiter-flexible |
| Python middleware            | slowapi (FastAPI), django-ratelimit                        |
| Distributed (multi-instance) | Redis-backed limiters (rate-limiter-flexible + Redis, Upstash Redis) |
| Reverse proxy                | Nginx limit_req, HAProxy                                   |

### Request Size & Payload Protection

- **MUST** enforce maximum request body size at the server/framework level:
  - JSON APIs: **SHOULD** default to 1 MB max (adjust per endpoint if needed)
  - File uploads: **MUST** set explicit per-endpoint limits matching business requirements
- **MUST** enforce maximum URL length and query string size
- **MUST** reject requests with unexpected Content-Types
- **SHOULD** set maximum JSON nesting depth to prevent deserialization attacks (e.g., deeply nested objects causing stack overflow)
- **MUST** validate and limit array sizes in request payloads (e.g., `ids: z.array(z.string()).max(100)`)

### API Endpoint Hardening

- **MUST** disable or restrict HTTP methods not in use (e.g., if an endpoint only supports GET, reject POST/PUT/DELETE)
- **MUST** return `404` (not `403`) for resources that the user should not know exist — `403` confirms the resource exists, `404` reveals nothing
- **MUST NOT** expose internal identifiers in predictable patterns when avoidable:
  - **SHOULD** prefer UUIDs or NanoIDs over sequential integer IDs for public-facing resource identifiers (prevents enumeration)
  - Sequential IDs **MAY** be used internally (database PKs) but **SHOULD NOT** be the public-facing identifier
- **MUST** remove or disable default framework error pages and debug endpoints in production (e.g., Next.js dev overlays, Django debug toolbar, FastAPI /docs in production)
- **MUST NOT** expose server technology details:
  - Remove `X-Powered-By` header
  - Remove `Server` header or set to a generic value
  - Suppress framework-specific error formats in production

### API Versioning Security

- **SHOULD** implement API versioning from the start for public APIs (e.g., `/api/v1/...`)
- **MUST** deprecate and eventually disable old API versions — unmaintained old versions become security liabilities
- **MUST** apply the same security controls (auth, rate limiting, validation) to ALL API versions equally

### Bot & Scraping Prevention (When Applicable)

- **SHOULD** implement progressive challenges for suspicious traffic:
  1. Rate limiting (first defense)
  2. CAPTCHA on sensitive forms (registration, contact, password reset)
  3. Request fingerprinting for pattern detection
- **SHOULD** monitor for abnormal access patterns:
  - Sequential resource ID access (enumeration)
  - Unusual User-Agent strings or missing headers
  - High-frequency requests just below rate limits
- **MAY** use managed bot protection services for high-value applications (Cloudflare Bot Management, AWS WAF Bot Control)

### CORS (Cross-Origin Resource Sharing)

- **MUST** configure CORS with explicit allowed origins in production — never use `*` (wildcard) for authenticated endpoints
- **MUST** restrict allowed methods and headers to what the API actually requires
- **SHOULD** keep CORS configuration centralized (not per-route)
- **MUST** validate the `Origin` header server-side — do not rely solely on CORS headers (they only protect browsers, not direct HTTP clients)

### Webhook Security (Inbound)

- **MUST** verify webhook signatures from external providers (e.g., Stripe signature verification, GitHub webhook secrets)
- **MUST NOT** trust webhook payloads without signature validation — anyone can send a POST to your webhook URL
- **SHOULD** implement idempotency for webhook handlers (providers may send duplicate events)
- **SHOULD** process webhooks asynchronously (return 200 immediately, process in background) to avoid timeouts
- **MUST** validate that the webhook payload structure matches the expected schema (Zod / Pydantic)

---

## 7. Secrets Management & Rotation

### What Qualifies as a Secret

Any value that grants access to a system, service, or data:
- Database credentials and connection strings
- API keys (Stripe, SendGrid, Supabase service_role, etc.)
- JWT signing keys and encryption keys
- OAuth client secrets
- Webhook signing secrets
- SSH keys and deploy tokens
- TLS/SSL private keys

### Fundamental Rules

- **MUST** never commit secrets to version control — not in code, not in config files, not in comments, not in documentation
- **MUST** add all secret-containing files to `.gitignore` BEFORE the first commit of the repository
- **MUST** include a `.env.example` file with all required keys, short descriptions, and placeholder values (never real values):

  ```env
  # .env.example
  # Database
  DATABASE_URL=postgresql://user:password@localhost:5432/dbname

  # Authentication
  JWT_SECRET=generate-a-strong-random-string-min-64-chars

  # External Services
  STRIPE_SECRET_KEY=sk_test_...
  STRIPE_WEBHOOK_SECRET=whsec_...

  # Supabase
  NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
  NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
  SUPABASE_SERVICE_ROLE_KEY=your-service-role-key  # NEVER expose to client
  ```

- **MUST** separate public (client-safe) and private (server-only) variables with clear naming conventions:
  - Next.js: `NEXT_PUBLIC_*` for client-safe, all others are server-only
  - Nuxt: `NUXT_PUBLIC_*` for client-safe
  - General: document the convention in the project README
- **MUST** never expose server-only secrets to the client bundle — verify with a build audit (search the built output for secret values)

### Secret Generation Standards

- **MUST** generate secrets using cryptographically secure methods:

  ```bash
  # Good — cryptographically random
  openssl rand -base64 64
  node -e "console.log(require('crypto').randomBytes(64).toString('base64'))"
  python3 -c "import secrets; print(secrets.token_urlsafe(64))"

  # BAD — predictable, insufficient entropy
  JWT_SECRET=my-secret-key
  JWT_SECRET=123456
  JWT_SECRET=company-name-2024
  ```

- **MUST** use minimum key lengths:
  - JWT signing keys: minimum 256 bits (64 hex chars / 43 base64 chars)
  - Encryption keys: match the algorithm requirement (e.g., 256 bits for AES-256)
  - API tokens: minimum 128 bits of entropy
- **MUST NOT** reuse the same secret across different environments (dev, staging, production must have different values)
- **MUST NOT** reuse the same secret across different purposes (JWT signing key ≠ encryption key ≠ API token)

### Storage by Maturity Level

| Level            | Approach                                                                        | When to Use                     |
|------------------|---------------------------------------------------------------------------------|---------------------------------|
| **Basic**        | `.env` local + provider dashboard                                               | Solo/freelance, small projects  |
| **Intermediate** | Centralized secret manager (Infisical, Doppler, Vercel Env Vars with scoping)   | Client projects, team projects  |
| **Advanced**     | Dedicated vault (HashiCorp Vault, AWS Secrets Manager, GCP Secret Manager)      | Enterprise, fintech, health data |

- **MUST** use at minimum Level 1 (Basic) for every project
- **SHOULD** use Level 2 (Intermediate) for any project handling real user data or payment information
- **MUST** use Level 3 (Advanced) for applications subject to regulatory compliance (PCI-DSS, HIPAA, SOC2)

#### Recommended Tools by Context

| Context                    | Tools                                                       |
|----------------------------|-------------------------------------------------------------|
| Platform-native            | Vercel Env Vars, Railway Variables, Render Env Groups       |
| Centralized management     | Infisical (open-source), Doppler, 1Password Secrets Automation |
| Cloud vault                | AWS Secrets Manager, GCP Secret Manager, Azure Key Vault    |
| Self-hosted vault          | HashiCorp Vault                                             |
| CI/CD secrets              | GitHub Actions Secrets, GitLab CI Variables                 |

### Secret Rotation

- **MUST** have a documented procedure for rotating each secret in the project — even if rotation is manual
- **MUST** rotate secrets immediately when:
  - A team member with access leaves the project
  - A secret is suspected or confirmed to be exposed
  - A breach of any related system is detected
- **SHOULD** rotate high-risk secrets periodically:

  | Secret Type              | Recommended Rotation   |
  |--------------------------|------------------------|
  | Database passwords       | Every 90 days          |
  | JWT signing keys         | Every 90–180 days      |
  | API keys (third-party)   | Every 90–180 days      |
  | Encryption keys          | Annually (with re-encryption plan) |
  | Service account tokens   | Every 90 days          |

- **SHOULD** implement zero-downtime rotation for critical secrets:
  - Support two active keys simultaneously during rotation window (old key valid for a grace period while new key is deployed)
  - Example: JWT verification accepts both old and new signing keys during rotation

### Leak Detection & Response

- **MUST** enable secret scanning on repositories:
  - GitHub: enable "Secret scanning" and "Push protection" in repo settings
  - **SHOULD** use pre-commit hooks to catch secrets before they reach the repo: `gitleaks`, `trufflehog`, `detect-secrets`
- **MUST** have a documented response procedure for exposed secrets:
  1. **Revoke** the exposed secret immediately (not "later today" — NOW)
  2. **Rotate** — generate and deploy a new secret
  3. **Audit** — check access logs for unauthorized usage during exposure window
  4. **Post-mortem** — document how the leak happened and add preventive controls
- **MUST NOT** assume a secret is safe because the repository is private — private repos can be cloned, forked, or compromised

### CI/CD Pipeline Secrets

- **MUST** inject secrets via the CI/CD platform's secret management (GitHub Actions Secrets, GitLab CI Variables) — never in pipeline files
- **MUST NOT** echo or print secrets in CI logs — mask them in pipeline configuration
- **SHOULD** use short-lived, scoped tokens for CI/CD operations (e.g., GitHub's `GITHUB_TOKEN` with minimal permissions)
- **MUST** restrict which branches and workflows can access production secrets (environment protection rules)

---

## 8. Encryption (At Rest + In Transit)

### In Transit — Transport Security

- **MUST** enforce HTTPS (TLS 1.2 minimum, TLS 1.3 preferred) for ALL communications — no exceptions, including:
  - Client to server
  - Server to database
  - Server to external APIs
  - Service to service (internal)
- **MUST** redirect HTTP to HTTPS at the infrastructure level (CDN, reverse proxy, or application middleware)
- **MUST** enable HSTS (HTTP Strict Transport Security) header in production:

  ```
  Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
  ```

- **MUST NOT** disable TLS certificate verification in production code — this is acceptable only in local development with self-signed certificates
- **SHOULD** pin TLS versions and disable deprecated protocols (SSLv3, TLS 1.0, TLS 1.1) at the infrastructure level
- **SHOULD** use TLS for database connections:
  - PostgreSQL: `?sslmode=require` (minimum) or `verify-full` (preferred)
  - Supabase: TLS is enforced by default on hosted instances
- **SHOULD** verify TLS configuration periodically (e.g., SSL Labs test — target grade A or A+)

### At Rest — Data Storage Encryption

#### Infrastructure-Level (Disk / Volume Encryption)

- **MUST** enable disk encryption on all production servers and databases:
  - Most cloud providers enable this by default (Supabase, Vercel, AWS RDS, GCP Cloud SQL) — **verify, don't assume**
  - Self-hosted: enable LUKS (Linux) or equivalent
- **MUST** encrypt all backups — a backup is a full copy of your data; an unencrypted backup is a breach waiting to happen
- **MUST** encrypt object storage buckets (S3, Cloudflare R2, GCS):
  - Enable server-side encryption (SSE) — most providers support this natively
  - **SHOULD** use provider-managed keys (SSE-S3, SSE-GCS) as the minimum
  - **MAY** use customer-managed keys (SSE-KMS) for higher control

#### Application-Level (Field-Level Encryption)

- **SHOULD** encrypt highly sensitive fields at the application layer before storing in the database:
  - Examples: government IDs (NIF, SSN), payment card data, health records, API keys stored for users
  - **This provides protection even if the database is fully compromised**
- **MUST** use AES-256-GCM (authenticated encryption) for field-level encryption:
  - GCM provides both confidentiality AND integrity (detects tampering)
  - **MUST NOT** use AES-ECB (insecure — identical plaintext blocks produce identical ciphertext)
  - **MUST NOT** use AES-CBC without authentication (vulnerable to padding oracle attacks)
- **MUST** store encryption keys separately from encrypted data — never in the same database:
  - Minimum: environment variable (different from DB credentials)
  - Recommended: dedicated key management service (KMS)
- **SHOULD** implement envelope encryption for scalability:

  ```text
  Data Encryption Key (DEK) → encrypts the data (unique per record or batch)
  Key Encryption Key (KEK) → encrypts the DEK (stored in KMS / vault)

  Benefits:
  - Rotating the KEK doesn't require re-encrypting all data
  - Each record can have its own DEK (limits blast radius)
  ```

- **MUST** plan for key rotation from the start:
  - Store a `key_version` or `encryption_key_id` alongside encrypted fields
  - On read: decrypt with the key version indicated
  - On write: always encrypt with the latest key version
  - Background migration: re-encrypt old records gradually

#### When to Use Field-Level Encryption

| Data Type                         | Field-Level Encryption   | Rationale                              |
|-----------------------------------|--------------------------|----------------------------------------|
| Government IDs (NIF, SSN, etc.)   | **MUST**                 | Regulatory + high-value target         |
| Payment card numbers              | **MUST** (or tokenize)   | PCI-DSS requirement                    |
| Health / medical records          | **MUST**                 | RGPD special category + HIPAA          |
| API keys / tokens stored for users| **MUST**                 | Credential compromise risk             |
| Email addresses                   | **MAY**                  | Depends on risk profile                |
| Phone numbers                     | **SHOULD**               | PII under RGPD                         |
| Addresses                         | **MAY**                  | Lower risk, but still PII              |
| Passwords                         | **NEVER encrypt — HASH** | Passwords must be hashed (Argon2id), never encrypted |

### Searching Encrypted Data

When field-level encryption is applied and searching is needed:

- **SHOULD** use blind indexes for equality searches:
  - Store a keyed HMAC hash of the plaintext alongside the encrypted value
  - Search against the hash, decrypt only matching records
  - Example: `nif_encrypted` (AES-256-GCM) + `nif_blind_index` (HMAC-SHA256)
- **MUST NOT** use deterministic encryption for searchability (same input → same output reveals patterns)
- **SHOULD** accept that range queries and partial matches are not possible on encrypted fields — design the data model accordingly

### Encryption Anti-Patterns

- **MUST NOT** invent custom encryption algorithms or protocols — use established, audited libraries
- **MUST NOT** use encoding (Base64, hex) as encryption — encoding is trivially reversible, it provides zero security
- **MUST NOT** store encryption keys in the same database as encrypted data
- **MUST NOT** hardcode encryption keys in source code
- **MUST NOT** use deprecated algorithms: DES, 3DES, RC4, MD5 for any cryptographic purpose, Blowfish (use AES instead)
- **MUST NOT** disable TLS verification in production

### Recommended Libraries

| Stack          | Library                                          |
|----------------|--------------------------------------------------|
| Node.js        | Built-in `crypto` module (AES-256-GCM)           |
| Python         | `cryptography` library (Fernet or AES-GCM)       |
| Key Management | AWS KMS, GCP Cloud KMS, HashiCorp Vault Transit  |

---

## 9. Security Headers & Transport Security

Security headers are server-sent instructions that tell browsers how to behave when rendering your application. They mitigate entire categories of attacks (XSS, clickjacking, MIME sniffing, data leakage) with minimal implementation effort.

### Mandatory Headers

The following headers **MUST** be present on all production responses:

#### Content-Security-Policy (CSP)

- **MUST** define a Content-Security-Policy that restricts resource loading to trusted origins
- **MUST** start with a restrictive base policy and loosen only as needed:

  ```
  Content-Security-Policy:
    default-src 'self';
    script-src 'self';
    style-src 'self' 'unsafe-inline';
    img-src 'self' data: https:;
    font-src 'self';
    connect-src 'self' https://api.your-domain.com;
    frame-ancestors 'none';
    base-uri 'self';
    form-action 'self';
    object-src 'none';
    upgrade-insecure-requests;
  ```

- **MUST NOT** use `unsafe-eval` in `script-src` — this re-enables the most dangerous XSS vector
- **SHOULD** avoid `unsafe-inline` in `script-src` — use nonces or hashes instead:
  - Generate a unique nonce per request: `script-src 'nonce-<random>'`
  - Reference it in script tags: `<script nonce="<random>">`
- **MAY** use `unsafe-inline` in `style-src` when CSS-in-JS or inline styles are required (common with Tailwind / frameworks) — this is a pragmatic trade-off with lower risk than inline scripts
- **SHOULD** deploy CSP in report-only mode first to identify violations without breaking functionality:

  ```
  Content-Security-Policy-Report-Only: <policy>; report-uri /api/csp-reports;
  ```

- **SHOULD** monitor CSP violation reports to detect XSS attempts and policy misconfigurations

#### Strict-Transport-Security (HSTS)

- **MUST** enable HSTS on all production domains:

  ```
  Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
  ```

- `max-age=63072000` = 2 years (minimum recommended for preload eligibility)
- `includeSubDomains` = applies to all subdomains
- `preload` = eligible for browser preload lists (submit at hstspreload.org)
- **MUST NOT** enable HSTS until HTTPS is fully operational across all subdomains — a misconfigured HSTS can lock users out

#### X-Content-Type-Options

- **MUST** set:

  ```
  X-Content-Type-Options: nosniff
  ```

- Prevents MIME type sniffing — the browser will strictly follow the declared Content-Type

#### X-Frame-Options / frame-ancestors

- **MUST** prevent clickjacking with at least one of:

  ```
  X-Frame-Options: DENY
  ```

  or via CSP (preferred — more flexible):

  ```
  Content-Security-Policy: frame-ancestors 'none';
  ```

- **MAY** use `frame-ancestors 'self'` if embedding in same-origin iframes is required
- **MAY** allow specific trusted domains: `frame-ancestors 'self' https://trusted-partner.com`

#### Referrer-Policy

- **MUST** set a restrictive Referrer-Policy:

  ```
  Referrer-Policy: strict-origin-when-cross-origin
  ```

  This sends only the origin (not full URL) on cross-origin requests, and the full referrer on same-origin requests.

- **MAY** use `no-referrer` for maximum privacy (but may break some analytics)

#### Permissions-Policy

- **SHOULD** disable browser features not used by the application:

  ```
  Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=(), usb=(), magnetometer=(), gyroscope=()
  ```

- Only enable features that the application explicitly requires
- **MUST** review this policy when adding new features (e.g., enabling camera for QR scanning)

### Headers to Remove

- **MUST** remove or suppress headers that reveal server technology:

  | Header              | Action                                   |
  |---------------------|------------------------------------------|
  | `X-Powered-By`      | Remove (Express, Next.js, etc. add this) |
  | `Server`             | Remove or set to a generic value         |
  | `X-AspNet-Version`   | Remove                                   |
  | `X-Debug-*`          | Remove in production                     |

  ```ts
  // Next.js — next.config.js
  const nextConfig = {
    poweredByHeader: false, // removes X-Powered-By
  };

  // Express
  app.disable('x-powered-by');

  // NestJS (uses Express under the hood by default)
  app.getHttpAdapter().getInstance().disable('x-powered-by');

  // Nginx
  server_tokens off;

  // FastAPI / Uvicorn — does not add these by default,
  // but verify with a response header audit
  ```

### API-Specific Headers

- **MUST** set appropriate `Content-Type` on all API responses:

  ```
  Content-Type: application/json; charset=utf-8
  ```

- **MUST** set `X-Content-Type-Options: nosniff` on API responses as well
- **MUST** prevent search engine indexing of API routes:

  ```
  X-Robots-Tag: noindex, nofollow
  ```

- **SHOULD** include cache control headers for sensitive responses:

  ```
  Cache-Control: no-store, no-cache, must-revalidate, private
  Pragma: no-cache
  ```

### Implementation Strategy

- **SHOULD** configure security headers at the infrastructure level (CDN, reverse proxy) for global coverage, with application-level headers as a fallback

  | Level               | How                                                          |
  |---------------------|--------------------------------------------------------------|
  | CDN / Edge          | Cloudflare Transform Rules, Vercel headers config, AWS CloudFront |
  | Reverse Proxy       | Nginx `add_header`, Caddy header directives                  |
  | Application         | Framework middleware (Next.js headers in `next.config.js`, Express middleware, FastAPI middleware) |
  | Meta tags (limited) | `<meta>` for CSP and referrer — only as fallback, headers are preferred |

- **SHOULD** centralize all security headers in one configuration file per project for easy auditing

  ```js
  // Example: next.config.js (Vercel / Next.js)
  const securityHeaders = [
    { key: 'X-Content-Type-Options', value: 'nosniff' },
    { key: 'X-Frame-Options', value: 'DENY' },
    { key: 'Referrer-Policy', value: 'strict-origin-when-cross-origin' },
    { key: 'Permissions-Policy', value: 'camera=(), microphone=(), geolocation=()' },
    { key: 'Strict-Transport-Security', value: 'max-age=63072000; includeSubDomains; preload' },
    // CSP should be configured carefully per project
  ];

  module.exports = {
    poweredByHeader: false,
    async headers() {
      return [{ source: '/(.*)', headers: securityHeaders }];
    },
  };
  ```

### Verification & Testing

- **MUST** verify security headers before production launch using:
  - [securityheaders.com](https://securityheaders.com) — target grade A or A+
  - [Mozilla Observatory](https://observatory.mozilla.org) — target grade A or A+
  - Browser DevTools → Network tab → Response Headers
- **SHOULD** automate header verification in CI/CD (e.g., curl the staging URL and assert expected headers are present)
- **SHOULD** re-verify after any infrastructure or deployment configuration change

---


## 10. OWASP Top 10 — Practical Prevention (2025 Edition)

This section maps to the **OWASP Top 10 (2025)** and provides actionable
prevention rules for each risk category. Where a risk is covered in depth
by a dedicated section in this document, a cross-reference is provided
to avoid duplication.

> **Note:** The 2025 edition introduces two new categories (A03: Software
> Supply Chain Failures and A10: Mishandling of Exceptional Conditions),
> consolidates SSRF into A01: Broken Access Control, and reorders several
> categories based on updated incidence data.

---

### A01:2025 — Broken Access Control

**Risk:** Users can act outside their intended permissions — accessing
other users' data, escalating roles, or bypassing restrictions.
Remains the #1 risk. Now includes Server-Side Request Forgery (SSRF),
previously a standalone category in 2021.

**Covered in depth:** [Section 5 — Authorization (RBAC / ABAC)]

**Additional rules:**

- **MUST** deny access by default — every endpoint and resource is protected unless explicitly made public
- **MUST** prevent IDOR (Insecure Direct Object Reference):
  - Always verify resource ownership, not just authentication
  - Prefer query-level scoping over post-fetch checks
- **MUST** enforce server-side access control — never rely on client-side hiding (hidden routes, disabled buttons, conditional rendering)
- **MUST** block access to sensitive file paths and metadata:
  - Reject requests to `/.env`, `/.git`, `/wp-admin`, `/server-status`, `/package.json`, and similar paths
  - Return `404` (not `403`) for these — do not confirm their existence
- **MUST** disable directory listing on all web servers
- **SHOULD** implement rate limiting on access control failures — many rapid 403s from the same source may indicate an enumeration attack
- **MUST** invalidate sessions and tokens when a user's permissions change (role downgrade, deactivation, ban)

#### SSRF Prevention (Consolidated from A10:2021)

- **MUST** validate and sanitize all user-provided URLs before the server fetches them:
  - **MUST** enforce an allowlist of permitted domains when possible (e.g., only allow image URLs from specific CDNs)
  - **MUST** block requests to private/internal IP ranges:
    - `127.0.0.0/8` (localhost)
    - `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` (private networks)
    - `169.254.169.254` (cloud metadata endpoint — critical)
    - `fd00::/8` (IPv6 private)
  - **MUST** block non-HTTP(S) protocols (`file://`, `ftp://`, `gopher://`, `dict://`)
- **MUST** resolve DNS and validate the target IP BEFORE making the request — an attacker can use a domain that resolves to an internal IP
- **SHOULD** use a dedicated outbound HTTP client with SSRF protections:
  - Node.js: `ssrf-req-filter`, or validate with `url` + `dns` modules
  - Python: `requests` with custom transport adapter for IP validation
- **MUST** disable or restrict access to cloud metadata endpoints:
  - AWS: enforce IMDSv2 (requires token, prevents simple SSRF)
  - GCP: use metadata server restrictions
  - Azure: use managed identity with minimal permissions
- **MUST NOT** return raw responses from server-side fetches to the client — validate and transform the response before forwarding

---

### A02:2025 — Security Misconfiguration

**Risk:** Insecure default settings, incomplete configurations, open
cloud storage, unnecessary features enabled, verbose error messages.
Moved from #5 (2021) to #2 (2025) — reflects how increasing system
complexity makes misconfiguration more prevalent and dangerous.

**Covered partially:** [Section 9 — Security Headers]

**Rules:**

- **MUST** disable or remove all default credentials, accounts, and sample data before production deployment
- **MUST** disable debug mode, development tools, and detailed error messages in production:
  - Next.js: ensure `NODE_ENV=production`
  - Django: `DEBUG=False`
  - FastAPI: disable `/docs` and `/redoc` in production or protect with auth
  - Express: do not use `errorhandler` middleware in production
- **MUST** review cloud service configurations:
  - Storage buckets: no public access unless explicitly required
  - Database: no public network access — use private networking
  - Serverless functions: minimum IAM permissions
- **MUST** remove unused dependencies, features, endpoints, and documentation from production builds
- **SHOULD** implement configuration audits as part of the deployment pipeline (automated checks for known misconfigurations)
- **SHOULD** keep all server software, frameworks, and runtimes updated to the latest stable versions

---

### A03:2025 — Software Supply Chain Failures (New in 2025)

**Risk:** Breakdowns or compromises in the process of building,
distributing, or updating software. This expands beyond "Vulnerable
and Outdated Components" (A06:2021) to cover the entire supply chain:
malicious packages, compromised maintainers, tampered build processes,
and dependency confusion attacks.

**Covered in depth:** [Section 11 — Dependency & Supply Chain Security]

**Why this is now #3:**
Supply chain attacks have escalated dramatically. The Trivy supply chain
compromise (March 2026) demonstrated how a trusted security tool can be
weaponized to steal CI/CD secrets across thousands of organizations
(→ See [Section 11] for the case study and mitigation guidance).

**Key reminders:**

- Verify package integrity and pin versions via lock files
- Use `npm ci` / `--frozen-lockfile` in CI (never `npm install`)
- Pin GitHub Actions to full commit SHAs, not mutable version tags
- Run SCA scanning in CI on every PR
- Monitor for suspicious package behavior (Socket.dev)
- Maintain an incident response plan for dependency compromises

---

### A04:2025 — Cryptographic Failures

**Risk:** Sensitive data is exposed due to weak or missing encryption,
poor key management, or use of deprecated algorithms.

**Covered in depth:** [Section 8 — Encryption (At Rest + In Transit)]

**Additional rules:**

- **MUST** classify data by sensitivity level at the start of each project:

  | Classification | Examples                               | Required Protection                           |
  |----------------|----------------------------------------|-----------------------------------------------|
  | **Critical**   | Passwords, payment cards, health data  | Hash (passwords) or AES-256-GCM + KMS         |
  | **High**       | Government IDs, API keys, tokens       | AES-256-GCM + separate key storage            |
  | **Medium**     | Email, phone, address                  | TLS in transit + disk encryption at rest      |
  | **Low**        | Public product info, published content | TLS in transit                                |

- **MUST** never transmit sensitive data in URL query parameters — URLs are logged in browser history, server logs, proxy logs, and Referer headers
- **MUST** disable caching for responses containing sensitive data:
  ```
  Cache-Control: no-store, no-cache, must-revalidate, private
  ```
- **MUST NOT** use weak or deprecated algorithms:
  - Forbidden: MD5, SHA-1 (for security), DES, 3DES, RC4, Blowfish
  - Acceptable hashing: SHA-256, SHA-384, SHA-512 (for integrity, not passwords)
  - Acceptable encryption: AES-256-GCM, ChaCha20-Poly1305
  - Password hashing: Argon2id, bcrypt, scrypt only

---

### A05:2025 — Injection

**Risk:** Untrusted data is sent to an interpreter as part of a command
or query, tricking it into executing unintended operations.

**Covers:** SQL Injection, NoSQL Injection, OS Command Injection,
LDAP Injection, Template Injection, Header Injection.

**Covered partially:** [Section 3 — Input Validation & Sanitization]

#### SQL Injection

- **MUST** use parameterized queries / prepared statements for ALL database operations — no exceptions:

  ```ts
  // BAD — SQL Injection vulnerability
  const query = `SELECT * FROM users WHERE email = '${email}'`;

  // GOOD — Parameterized query (Node.js / pg)
  const result = await pool.query(
    'SELECT * FROM users WHERE email = $1',
    [email]
  );

  // GOOD — Supabase client (parameterized by default)
  const { data } = await supabase
    .from('users')
    .select('*')
    .eq('email', email);
  ```

  ```python
  # BAD — SQL Injection vulnerability
  cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")

  # GOOD — Parameterized query (Python / psycopg2)
  cursor.execute("SELECT * FROM users WHERE email = %s", (email,))

  # GOOD — SQLAlchemy ORM (parameterized by default)
  user = session.query(User).filter_by(email=email).first()
  ```

- **MUST NOT** concatenate or interpolate user input into SQL strings — even for column names, table names, or ORDER BY clauses:

  ```ts
  // BAD — column name injection
  const query = `SELECT * FROM users ORDER BY ${sortColumn}`;

  // GOOD — allowlist of valid column names
  const ALLOWED_SORT_COLUMNS = ['name', 'created_at', 'email'] as const;
  if (!ALLOWED_SORT_COLUMNS.includes(sortColumn)) {
    throw new ValidationError('Invalid sort column');
  }
  const query = `SELECT * FROM users ORDER BY ${sortColumn}`;
  ```

#### NoSQL Injection

- **MUST** validate and sanitize input before using in NoSQL queries
- **MUST NOT** pass raw user input as query operators:

  ```ts
  // BAD — NoSQL Injection (MongoDB)
  db.users.find({ email: req.body.email, password: req.body.password });

  // GOOD — Validate types with Zod first
  const schema = z.object({
    email: z.string().email(),
    password: z.string().min(10)
  });
  const { email, password } = schema.parse(req.body);
  ```

#### OS Command Injection

- **MUST** avoid executing shell commands with user input entirely
- **MUST NOT** use `child_process.exec()` (Node.js) or `os.system()` (Python) with user-provided data:

  ```ts
  // BAD — Command Injection
  exec(`convert ${filename} output.png`);

  // GOOD — Use argument arrays (no shell interpolation)
  execFile('convert', [filename, 'output.png']);
  ```

  ```python
  # BAD — Command Injection
  os.system(f"convert {filename} output.png")

  # GOOD — Use subprocess with argument list, shell=False
  subprocess.run(['convert', filename, 'output.png'], shell=False)
  ```

- **SHOULD** use purpose-built libraries instead of shell commands (e.g., sharp for image processing in Node.js, Pillow in Python)

#### Template Injection (SSTI)

- **MUST NOT** pass user input directly into server-side template engines as template code (e.g., Jinja2, EJS, Handlebars)
- **MUST** treat user input as DATA within templates, never as template syntax

#### Header Injection / Response Splitting

- **MUST** validate and sanitize any user input used in HTTP response headers
- **MUST NOT** include raw user input in `Set-Cookie`, `Location`, or custom headers without sanitization — newline characters (`\r\n`) can inject additional headers or split the response

---

### A06:2025 — Insecure Design

**Risk:** The application has fundamental design flaws that cannot be
fixed by better implementation — security was not considered in the
design phase.

**Covered in depth:** [Section 2 — Threat Modeling (STRIDE)]

**Additional rules:**

- **MUST** consider security requirements during feature design, not as an afterthought
- **MUST** apply the principle of least privilege in every design decision
- **SHOULD** use secure design patterns:
  - Server-side validation as the authority (never trust the client)
  - Immutable operations where possible (append-only audit logs)
  - Idempotent operations for safety under retry conditions
- **SHOULD** design with abuse cases in mind, not just happy paths:
  - "What if a user submits this form 10,000 times?"
  - "What if they modify the price in the request body?"
  - "What if they access another user's resource ID?"
- **MUST** limit resource consumption by design:
  - Cap pagination sizes
  - Timeout long-running operations
  - Limit batch operation sizes
  - Enforce upload size and count limits

---

### A07:2025 — Authentication Failures

**Risk:** Weaknesses in authentication mechanisms allow attackers
to compromise passwords, keys, or session tokens, or exploit flaws
to assume other users' identities.

**Covered in depth:** [Section 4 — Authentication Standards]

**Key reminders:**

- Credential stuffing protection (rate limiting + account lockout)
- Secure session management (HttpOnly, Secure, SameSite cookies)
- MFA for sensitive operations
- Secure password reset flow (time-limited, single-use tokens)

---

### A08:2025 — Software and Data Integrity Failures

**Risk:** Code and infrastructure do not protect against integrity
violations — untrusted sources for updates, insecure CI/CD pipelines,
and deserialization of untrusted data.

#### Supply Chain Integrity

- **MUST** use lock files (`package-lock.json`, `pnpm-lock.yaml`, `poetry.lock`) and commit them to version control — ensures reproducible builds with exact dependency versions
- **MUST** verify package integrity during installation (npm verifies checksums automatically via lock file)
- **SHOULD** pin exact versions for critical dependencies in production applications
- **MUST NOT** run arbitrary `postinstall` scripts from untrusted packages without review

#### CI/CD Pipeline Integrity

- **MUST** protect the CI/CD pipeline as a critical security boundary:
  - Restrict who can modify pipeline configuration
  - Use signed commits for pipeline changes
  - Audit pipeline execution logs
- **MUST** pin all third-party GitHub Actions to full commit SHAs — mutable
  version tags can be silently repointed to malicious commits
  (demonstrated in the Trivy supply chain attack, March 2026)
- **MUST** ensure build artifacts are produced in a controlled, reproducible environment
- **SHOULD** sign release artifacts (Docker images, binaries) when distributing to external consumers

#### Deserialization Safety

- **MUST** validate ALL serialized data from untrusted sources before deserialization (JSON, XML, YAML, binary formats)
- **MUST** use schema validation (Zod, Pydantic, JSON Schema) on any data received from external systems, webhooks, queues, or file uploads
- **MUST NOT** use insecure deserialization functions:

  ```python
  # BAD — arbitrary code execution via pickle
  import pickle
  data = pickle.loads(untrusted_input)  # NEVER with untrusted data

  # GOOD — safe JSON deserialization + validation
  import json
  from pydantic import BaseModel
  raw = json.loads(untrusted_input)
  validated = MyModel.model_validate(raw)
  ```

  ```ts
  // GOOD — safe JSON parsing + validation
  const raw = JSON.parse(untrustedInput);
  const validated = mySchema.parse(raw);  // Zod validation
  ```

- **MUST NOT** use `eval()`, `new Function()`, or `vm.runInNewContext()` to process untrusted data in Node.js

---

### A09:2025 — Security Logging and Alerting Failures

**Risk:** Without adequate logging, monitoring, and **alerting**,
breaches go undetected, attacks continue unimpeded, and forensic
analysis after an incident is impossible. The 2025 edition adds
emphasis on alerting as a critical detection and response capability.

**Covered in depth:** [08-observability.md], [Section 15 — Security Logging & Audit Trail]

**Additional rules specific to security:**

- **MUST** log security-relevant events:

  | Event                                | Log Level | Required Fields                          |
  |--------------------------------------|-----------|------------------------------------------|
  | Login success                        | info      | userId, IP, userAgent, timestamp         |
  | Login failure                        | warn      | attemptedEmail, IP, userAgent, reason    |
  | Authorization failure                | warn      | userId, resource, action, reason         |
  | Rate limit triggered                 | warn      | IP, endpoint, limit exceeded             |
  | Password change / reset              | info      | userId, timestamp                        |
  | MFA enable / disable                 | info      | userId, timestamp                        |
  | Admin action                         | info      | userId, action, targetResource           |
  | Input validation failure (suspicious)| warn      | IP, endpoint, payload summary            |
  | Account lockout                      | warn      | userId/email, IP, failureCount           |
  | Token revocation                     | info      | userId, reason                           |

- **MUST NOT** log sensitive data in security logs:
  - No passwords (even failed attempts)
  - No full tokens or session IDs (log last 4 chars only: `...a1b2`)
  - No credit card numbers
  - PII only when necessary and compliant with privacy regulations
- **MUST** make security logs tamper-resistant:
  - **SHOULD** store security logs in a separate, append-only destination (different from application logs)
  - **MUST NOT** allow application code to modify or delete security logs
  - **SHOULD** forward security logs to an external service (Sentry, Datadog, Grafana Loki, CloudWatch)
- **MUST** configure alerts for suspicious patterns — logging without alerting is just generating data nobody reads:
  - Multiple failed login attempts from the same IP
  - Unusual geographic access patterns
  - Sudden spike in 403/429 responses
  - Access to known attack paths (`/.env`, `/wp-admin`, etc.)
- **MUST** retain security logs for a minimum period:
  - **SHOULD** retain for at least 90 days (longer for compliance requirements)
  - **MUST** comply with data retention regulations (RGPD — do not retain personal data beyond the justified period)

---

### A10:2025 — Mishandling of Exceptional Conditions (New in 2025)

**Risk:** Applications that fail to prevent, detect, and respond
to unusual and unpredictable situations — leading to crashes,
unexpected behavior, information disclosure, or denial of service.
This category elevates error handling from a code quality concern
to a security risk.

**Rules:**

- **MUST** handle all expected error conditions explicitly — never rely
  on generic catch-all handlers as the primary strategy
- **MUST NOT** expose internal details through error messages in production:
  - No stack traces
  - No database error messages or query details
  - No internal file paths or server configuration
  - No dependency version information
- **MUST** implement graceful degradation — when a component fails,
  the application should continue operating in a reduced capacity
  rather than crashing entirely
- **MUST** validate all assumptions about external data — API responses,
  database results, file system operations, and network calls can all
  fail in unexpected ways:

  ```ts
  // BAD — assumes API always returns expected shape
  const user = await fetchUser(id);
  const email = user.data.email; // crashes if user.data is null

  // GOOD — handles exceptional conditions
  const user = await fetchUser(id);
  if (!user?.data?.email) {
    throw new NotFoundError('User');
  }
  const email = user.data.email;
  ```

- **MUST** set timeouts on all external calls (HTTP requests, database
  queries, third-party API calls) — a missing timeout can hang the
  entire application
- **MUST** implement circuit breakers or fallback strategies for
  critical external dependencies — if a payment provider is down,
  the entire application should not become unresponsive
- **SHOULD** use structured error types (custom error classes) to
  distinguish between recoverable and non-recoverable failures
  (→ See [03-api-design.md, Error Handling])
- **SHOULD** test error paths as rigorously as success paths — error
  handling code that is never tested is error handling code that
  does not work when needed
- **MUST** ensure error boundaries (React) or global error handlers
  catch unhandled exceptions and display safe fallback UIs —
  never a blank screen or raw error dump

---
## 11. Dependency & Supply Chain Security

### Core Principle

Every external dependency is an extension of your attack surface. A compromised dependency runs with the same privileges as your application code.

> **⚠️ Real-World Case Study — Trivy Supply Chain Attack (March 2026):**
> On March 19, 2026, Trivy — one of the most widely used open-source
> vulnerability scanners — was compromised. Attackers force-pushed 76 of
> 77 version tags in the `trivy-action` GitHub Action to malicious commits
> that stole CI/CD secrets, cloud credentials, and SSH keys. The malicious
> binary (v0.69.4) was also distributed via GitHub Releases and Docker Hub.
> The attack exploited mutable Git tags and incomplete credential rotation
> from a prior breach. This incident demonstrates that **security tools
> themselves are high-value targets** and reinforces the critical importance
> of SHA pinning, tool diversification, and rapid incident response.

### CI/CD Supply Chain Rules

- **MUST** pin all third-party GitHub Actions to **full commit SHAs** — never
  use mutable version tags (`@v1`, `@v0.12.0`). Tags can be silently repointed
  to malicious commits:

  ```yaml
  # BAD — mutable tag, can be hijacked
  - uses: zaproxy/action-baseline@v0.12.0

  # GOOD — immutable SHA, points to a specific verified commit
  - uses: zaproxy/action-baseline@7cea08522cd8612907c4caefd5cbc61c793e9117
  ```

- **MUST** verify the SHA corresponds to the expected release before pinning
  (check the repository's releases page and cross-reference the commit)
- **SHOULD** use tools like `pin-github-action` or Renovate's `pinGitHubActionDigests`
  to automate SHA pinning and updates
- **SHOULD** diversify security scanning tools — do not rely exclusively on a
  single scanner for all security dimensions. Use complementary tools to reduce
  single-vendor risk

### Dependency Selection Rules

- **MUST** evaluate every new dependency before installation:

  | Criteria                | What to Check                                     |
  |-------------------------|---------------------------------------------------|
  | Maintenance status      | Last commit date, release frequency, open issues  |
  | Popularity & trust      | Download count, GitHub stars, known maintainers   |
  | Security track record   | CVE history, security policy (`SECURITY.md`)      |
  | Scope of access         | What permissions / APIs does it access?           |
  | Transitive dependencies | How many sub-dependencies does it pull in?        |
  | Bundle size             | Impact on client bundle (bundlephobia.com)        |
  | License compatibility   | MIT, Apache-2.0 preferred; review others          |

- **MUST** justify the addition of every new dependency — prefer native platform APIs or existing dependencies first
- **SHOULD** prefer packages with:
  - Minimal transitive dependencies
  - TypeScript types included (not separate `@types/` package maintained by a different party)
  - A responsible disclosure / security policy
- **SHOULD** prefer well-known, widely-audited packages over obscure alternatives

### Lock Files & Reproducible Builds

- **MUST** commit lock files to version control:
  - npm: `package-lock.json`
  - pnpm: `pnpm-lock.yaml`
  - yarn: `yarn.lock`
  - Python: `poetry.lock` / `pip-compile` output / `uv.lock`
- **MUST** use deterministic install commands in CI/CD:
  - npm: `npm ci` (not `npm install` — `ci` respects the lock file exactly)
  - pnpm: `pnpm install --frozen-lockfile`
  - yarn: `yarn install --frozen-lockfile`
  - Python: `pip install -r requirements.txt` (with pinned versions)
- **MUST NOT** use `npm install` in CI — it can modify the lock file and introduce untested dependency versions
- **SHOULD** verify lock file integrity — if the lock file changes unexpectedly in a PR, review the diff carefully

### Vulnerability Scanning

- **MUST** scan dependencies for known vulnerabilities as part of CI:

  | Tool                  | Ecosystem                       | Integration                     |
  |-----------------------|---------------------------------|---------------------------------|
  | `npm audit`           | Node.js                         | Built-in, run in CI pipeline    |
  | `pip audit`           | Python                          | Run in CI pipeline              |
  | Snyk                  | Multi-language                  | CLI + CI + IDE plugins          |
  | Trivy                 | Multi (deps + containers + IaC) | CI pipeline, Docker scanning    |
  | GitHub Dependabot     | Multi-language                  | Automated PRs + alerts          |
  | Renovate              | Multi-language                  | Automated PRs + merge policies  |
  | Socket.dev            | npm / PyPI                      | Supply chain anomaly detection  |
  | OSV-Scanner (Google)  | Multi-language                  | Open-source, CI-friendly        |

- **MUST** fail CI builds on **critical** and **high** severity vulnerabilities
- **SHOULD** fail CI builds on **medium** severity — with documented exceptions for false positives or unused code paths
- **MUST** have a response process for new CVEs:

  | Severity   | Response Time         | Action                                |
  |------------|-----------------------|---------------------------------------|
  | Critical   | Within 24 hours       | Patch, update, or remove immediately  |
  | High       | Within 48 hours       | Patch or document risk acceptance     |
  | Medium     | Within 1 week         | Evaluate and plan update              |
  | Low        | Next maintenance cycle| Track and update when convenient      |

### Supply Chain Attack Prevention

#### Typosquatting Protection

- **MUST** double-check package names before installation — verify on the official registry page (npmjs.com, pypi.org)
- **SHOULD** use scoped packages (`@scope/package`) for internal packages to reduce typosquatting risk
- **SHOULD** use `socket.dev` or equivalent tools that detect suspicious new packages

#### Dependency Confusion Prevention

- **MUST** configure private registries correctly when using private packages:
  - npm: use `.npmrc` with `@scope:registry=https://your-private-registry`
  - Python: configure `--index-url` and `--extra-index-url` properly
- **SHOULD** publish placeholder packages on public registries for internal package names (to prevent attackers from claiming them)

#### Post-install Script Protection

- **SHOULD** audit `postinstall` scripts of new dependencies before adding:
  ```bash
  # Check what scripts a package runs
  npm show <package-name> scripts
  ```
- **SHOULD** use tools that flag packages with install scripts:
  - Socket.dev detects and warns about install scripts
  - `npm config set ignore-scripts true` for initial auditing (re-enable for actual build)

#### Maintainer Compromise Protection

- **SHOULD** prefer packages with multiple maintainers (single-maintainer packages are higher risk)
- **SHOULD** monitor for unexpected ownership transfers (Socket.dev and Snyk alert on these)
- **SHOULD** pin exact versions for critical security-related dependencies (e.g., auth libraries, encryption packages) — review every update manually before merging

### Automated Dependency Updates

- **SHOULD** enable automated dependency update tooling:

  | Tool         | Strengths                                          |
  |--------------|----------------------------------------------------|
  | Dependabot   | GitHub-native, simple setup, security-focused PRs  |
  | Renovate     | Highly configurable, grouping, auto-merge policies |

- **SHOULD** configure update policies:
  - Security patches: auto-merge after CI passes (minor/patch versions)
  - Minor updates: auto-create PR, require manual review
  - Major updates: require manual review and testing
- **MUST** ensure CI runs the full test suite on dependency update PRs
- **SHOULD** group related dependency updates to reduce PR noise (e.g., all `@types/*` packages in one PR)

### Pre-commit Dependency Checks

- **SHOULD** add a pre-commit or pre-push hook that runs `npm audit --audit-level=high` (or equivalent) to catch vulnerabilities before they reach the repository
- **SHOULD** integrate dependency scanning into the IDE (Snyk IDE plugins, Socket.dev extension) for real-time feedback during development

---

## 12. Container & Infrastructure Security

> **Scope — trusted app containers, not an untrusted-code sandbox.** This section hardens
> containers that run *your own trusted application code*. It is **not** a security boundary for
> running **untrusted, agent-generated code**: Docker / runc share the host kernel, so a kernel
> exploit escapes the container. Sandboxing code an AI agent wrote needs stronger isolation
> (user-space kernel or microVM). → See [02-technology-radar.md, §3.32] (the *what*);
> [12-ai-engineering.md, §6.8] (when an agent needs it).

### Container Image Security

#### Base Image Selection

- **MUST** use minimal base images to reduce attack surface:

  | Image Type                     | Use Case                 | Size     | Security Profile                          |
  |--------------------------------|--------------------------|----------|-------------------------------------------|
  | `node:24-alpine`               | Node.js production       | ~50MB    | Good — minimal OS                         |
  | `python:3.13-slim`             | Python production        | ~120MB   | Good — no extras                          |
  | `gcr.io/distroless/nodejs24`   | Node.js hardened         | ~40MB    | Excellent — no shell, no package manager  |
  | `gcr.io/distroless/python3`    | Python hardened          | ~50MB    | Excellent — no shell                      |
  | `node:24` (full)               | Development / build stage ONLY | ~350MB+ | Poor — full OS, many tools          |

- **MUST NOT** use `latest` tag for base images — always pin to a specific version:

  ```dockerfile
  # BAD — unpredictable, can change anytime
  FROM node:latest

  # GOOD — pinned, reproducible
  FROM node:24-alpine3.21
  ```

- **SHOULD** use distroless images for production when possible — they contain no shell, no package manager, and no unnecessary binaries, which drastically limits what an attacker can do if they compromise the application
- **SHOULD** update base images regularly to pick up OS-level security patches

#### Multi-Stage Builds

- **MUST** use multi-stage builds to separate build environment from runtime environment:

  ```dockerfile
  # Stage 1: Build (heavy image with dev tools)
  FROM node:24-alpine AS builder
  WORKDIR /app
  COPY package.json package-lock.json ./
  RUN npm ci
  COPY . .
  RUN npm run build

  # Stage 2: Production (minimal image, only runtime)
  FROM node:24-alpine AS runner
  WORKDIR /app

  # Create non-root user
  RUN addgroup --system --gid 1001 appgroup && \
      adduser --system --uid 1001 appuser

  # Copy only production artifacts
  COPY --from=builder /app/dist ./dist
  COPY --from=builder /app/node_modules ./node_modules
  COPY --from=builder /app/package.json ./

  # Drop privileges
  USER appuser

  EXPOSE 3000
  CMD ["node", "dist/server.js"]
  ```

- **MUST** ensure build-time secrets, dev dependencies, source code, and build tools do NOT exist in the final production stage
- **SHOULD** copy only the specific files/folders needed — never `COPY --from=builder /app /app` (copies everything)

#### Non-Root Execution

- **MUST** run containers as a non-root user in production:

  ```dockerfile
  RUN addgroup --system --gid 1001 appgroup && \
      adduser --system --uid 1001 appuser
  USER appuser
  ```

- **MUST NOT** use `--privileged` flag when running containers — this disables all security isolation
- **SHOULD** set filesystem to read-only where possible:

  ```yaml
  # docker-compose.yml
  services:
    app:
      read_only: true
      tmpfs:
        - /tmp
  ```

#### Secrets in Docker

- **MUST NOT** pass secrets via build arguments (`ARG`) — they are visible in `docker history`:

  ```dockerfile
  # BAD — secret visible in image history
  ARG DATABASE_URL
  ENV DATABASE_URL=$DATABASE_URL

  # BAD — secret baked into the image
  COPY .env /app/.env
  ```

- **MUST** inject secrets at runtime via:
  - Environment variables (docker run -e, docker-compose env_file)
  - Docker Secrets (Swarm) or Kubernetes Secrets
  - Vault sidecar / init container pattern
  - Cloud provider secret injection (ECS task secrets, GKE workload identity)
- **MUST NOT** include `.env` files in Docker images — add `.env` to `.dockerignore`

#### .dockerignore

- **MUST** maintain a `.dockerignore` file to prevent sensitive and unnecessary files from entering the build context:

  ```
  # .dockerignore
  .env
  .env.*
  .git
  .gitignore
  node_modules
  dist
  coverage
  tests
  docs
  *.md
  .vscode
  .idea
  docker-compose*.yml
  Dockerfile
  ```

### Container Vulnerability Scanning

- **MUST** scan container images for vulnerabilities before deployment:

  | Tool              | Integration                                |
  |-------------------|--------------------------------------------|
  | Trivy             | CLI + CI/CD (GitHub Actions, GitLab CI) — **pin to verified SHA** |
  | Grype (Anchore)   | CLI + CI/CD — recommended as a Trivy alternative |
  | Snyk Container    | CLI + CI + Docker Desktop integration      |
  | Docker Scout      | Docker Desktop + Docker Hub integration    |
  | AWS ECR Scanning  | Native in AWS ECR                          |
  | GCP Artifact Analysis | Native in GCP Artifact Registry        |

  > **⚠️ Trivy usage note (March 2026):** Following the Trivy supply chain
  > compromise, verify you are using a safe version (≥ v0.70.0 or last known
  > safe v0.69.3). Pin the Trivy GitHub Action to a full commit SHA, and
  > pin Docker images by digest. Consider using Grype as a complementary or
  > alternative scanner to reduce single-vendor risk.
  > → See [Section 11] for full incident details.

  ```bash
  # Example: scan with Trivy in CI
  trivy image --severity HIGH,CRITICAL --exit-code 1 myapp:latest
  ```

- **MUST** fail CI/CD pipeline if critical vulnerabilities are found in the container image
- **SHOULD** scan images on a regular schedule (not just at build time) — new CVEs are discovered after images are built
- **SHOULD** use a private container registry with access controls (not public Docker Hub for production images)

### Docker Compose Security (Development & Staging)

- **MUST NOT** expose database ports to the host network in production:

  ```yaml
  # BAD — database accessible from outside
  services:
    db:
      ports:
        - "5432:5432"

  # GOOD — only accessible within the Docker network
  services:
    db:
      expose:
        - "5432"
  ```

- **SHOULD** define internal networks to isolate service communication:

  ```yaml
  services:
    app:
      networks:
        - frontend
        - backend
    db:
      networks:
        - backend

  networks:
    frontend:
    backend:
      internal: true
  ```

- **MUST** use `env_file` or runtime secrets — never hardcode secrets in `docker-compose.yml`

### Infrastructure as Code (IaC) Security

When using Terraform, Pulumi, CloudFormation, or similar tools:

- **MUST** scan IaC templates for security misconfigurations before applying:

  | Tool              | Supported IaC                              |
  |-------------------|--------------------------------------------|
  | Trivy             | Terraform, CloudFormation, Kubernetes YAML |
  | Checkov           | Terraform, CloudFormation, Kubernetes, ARM |
  | KICS (Checkmarx)  | Terraform, CloudFormation, Kubernetes, Ansible, Docker, OpenAPI |
  | Snyk IaC          | Multi-format                               |

- **MUST** store IaC configuration in version control with the same review process as application code
- **MUST NOT** store secrets in IaC files — use vault references or encrypted secret backends
- **MUST** apply least privilege to IaC execution roles — the Terraform service account should not have admin access to the entire cloud account
- **SHOULD** enable state file encryption and access controls (e.g., Terraform state in S3 with encryption + DynamoDB locking)

### Kubernetes Security (When Applicable)

When the project scales to require Kubernetes orchestration:

- **MUST** document the decision to adopt Kubernetes in an ADR — do not adopt Kubernetes unless the operational complexity is justified
- **MUST** enforce Pod Security Standards:
  - Run pods as non-root (`runAsNonRoot: true`)
  - Drop all capabilities (`drop: ["ALL"]`)
  - Read-only root filesystem (`readOnlyRootFilesystem: true`)
  - Disallow privilege escalation (`allowPrivilegeEscalation: false`)

  ```yaml
  apiVersion: v1
  kind: Pod
  spec:
    securityContext:
      runAsNonRoot: true
      runAsUser: 1001
      fsGroup: 1001
    containers:
      - name: app
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop: ["ALL"]
  ```

- **MUST** use Kubernetes Secrets (or external vault) for sensitive data — never in ConfigMaps or pod specs
- **MUST** define NetworkPolicies to restrict pod-to-pod communication (default Kubernetes allows all pods to communicate freely)
- **SHOULD** use namespaces to isolate environments and teams
- **SHOULD** scan Kubernetes manifests with the same IaC scanning tools (Trivy, Checkov, Kubesec)
- **SHOULD** implement resource limits (CPU, memory) on all containers to prevent resource exhaustion attacks

### Scaling Guidance

| Project Stage            | Recommended Approach                                                          |
|--------------------------|-------------------------------------------------------------------------------|
| Solo / Freelance         | Docker Compose for local dev, managed hosting (Vercel, Railway, Render) for production |
| Small team / Growing     | Docker + CI/CD with container registry, managed services (ECS, Cloud Run, Fly.io) |
| Large scale / Multi-team | Kubernetes (managed: EKS, GKE, AKS) with full security policies              |

- **MUST NOT** adopt Kubernetes for projects that can be served by simpler platforms — operational complexity is itself a security risk (more to misconfigure, more to monitor, more to patch)

---

## 13. Security Testing (SAST / DAST / SCA)

Security testing **MUST** be automated and integrated into the development workflow. Manual security review is valuable but insufficient as the sole control — humans miss patterns that tools catch, and tools catch issues at a speed and consistency humans cannot match.

### Overview

| Type | What It Tests         | When It Runs             | What It Finds                     |
|------|-----------------------|--------------------------|-----------------------------------|
| SAST | Source code (static)  | Every commit / PR in CI  | Code-level vulnerabilities        |
| SCA  | Dependencies          | Every install + CI + scheduled | Known CVEs in third-party code |
| DAST | Running application   | Against staging / preview | Exploitable runtime vulnerabilities |

All three types are complementary. No single type provides complete coverage.

---

### SAST — Static Application Security Testing

#### Rules

- **MUST** integrate SAST scanning into the CI/CD pipeline — run on every pull request before merge
- **SHOULD** integrate SAST into developer IDEs for real-time feedback during coding (shift-left approach)
- **MUST** fail the CI pipeline on high and critical severity findings
- **SHOULD** triage medium severity findings within one sprint
- **MUST** track and document false positives — mark as suppressed with justification, not silently ignored

#### Recommended Tools

| Tool                         | Languages / Frameworks              | Integration            | Cost                   |
|------------------------------|-------------------------------------|------------------------|------------------------|
| SonarQube / SonarCloud       | Multi-language (JS/TS, Python, etc.)| CI + IDE (SonarLint)   | Free (Community) / Paid|
| Semgrep                      | Multi-language, custom rules        | CI + CLI + IDE         | Free (OSS) / Paid      |
| CodeQL (GitHub)              | Multi-language                      | GitHub Actions native  | Free for public repos  |
| ESLint Security plugins      | JavaScript / TypeScript             | CI + IDE               | Free                   |
| Bandit                       | Python                              | CI + CLI               | Free                   |
| Snyk Code                    | Multi-language                      | CI + IDE + CLI         | Free tier / Paid       |

#### Minimum SAST Configuration

- **MUST** enable at minimum one SAST tool covering the project's primary language(s)
- **SHOULD** configure rules relevant to the OWASP Top 10:
  - SQL injection patterns
  - XSS patterns (dangerouslySetInnerHTML, unescaped output)
  - Hardcoded secrets and credentials
  - Insecure cryptographic usage
  - Command injection patterns
  - Path traversal patterns
  - Insecure deserialization
- **SHOULD** add project-specific custom rules when patterns of risk are identified (e.g., Semgrep custom rules)

#### ESLint Security Plugins (JavaScript / TypeScript)

- **SHOULD** add security-focused ESLint plugins as a lightweight SAST layer:

  ```bash
  npm install --save-dev eslint-plugin-security eslint-plugin-no-unsanitized
  ```

  ```js
  // eslint.config.js (flat config — required for ESLint v10+)
  import pluginSecurity from 'eslint-plugin-security';
  import noUnsanitized from 'eslint-plugin-no-unsanitized';

  export default [
    pluginSecurity.configs.recommended,
    {
      plugins: {
        'no-unsanitized': noUnsanitized,
      },
      rules: {
        'security/detect-object-injection': 'warn',
        'security/detect-non-literal-regexp': 'warn',
        'security/detect-unsafe-regex': 'error',
        'security/detect-buffer-noassert': 'error',
        'security/detect-eval-with-expression': 'error',
        'security/detect-no-csrf-before-method-override': 'error',
        'security/detect-possible-timing-attacks': 'warn',
        'no-unsanitized/method': 'error',
        'no-unsanitized/property': 'error',
      },
    },
  ];
  ```

- These catch common patterns but are NOT a substitute for a dedicated SAST scanner — they complement each other

#### Bandit (Python)

- **SHOULD** integrate Bandit for Python projects:

  ```bash
  pip install bandit

  # Run against the project
  bandit -r src/ -f json -o bandit-report.json

  # In CI — fail on high severity
  bandit -r src/ -ll
  ```

- **SHOULD** configure `.bandit` or `pyproject.toml` to suppress known false positives with documented justifications

---

### SCA — Software Composition Analysis

**Covered in depth:** [Section 11 — Dependency & Supply Chain Security]

#### Key Integration Rules

- **MUST** run SCA in CI on every PR that modifies dependency files (`package.json`, `package-lock.json`, `requirements.txt`, `poetry.lock`)
- **MUST** run SCA on a scheduled basis (weekly minimum) to catch newly disclosed CVEs in existing dependencies
- **SHOULD** enable automated PR creation for vulnerable dependencies (Dependabot, Renovate)

#### Recommended Tools

| Tool              | Ecosystem          | Key Strength                     |
|-------------------|--------------------|----------------------------------|
| `npm audit`       | Node.js            | Built-in, zero setup             |
| `pip audit`       | Python             | Built-in (pip >= 22.3)           |
| Snyk              | Multi-language     | Deep analysis + fix suggestions  |
| Trivy             | Multi (deps + containers) | Unified scanning            |
| Socket.dev        | npm / PyPI         | Behavioral analysis (supply chain)|
| Dependabot        | Multi-language     | GitHub-native automated PRs      |
| OSV-Scanner       | Multi-language     | Google's open-source CVE scanner |

---

### DAST — Dynamic Application Security Testing

#### Rules

- **SHOULD** run DAST against staging or preview environments on a regular cadence (minimum: before each production release)
- **MUST NOT** run aggressive DAST scans against production without explicit coordination — DAST sends real attack payloads that can corrupt data, trigger lockouts, or cause service disruption
- **SHOULD** start with passive scanning (observe traffic, check headers, analyze responses) before running active scanning (send attack payloads)
- **MUST** review DAST findings manually before acting — DAST tools have a higher false positive rate than SAST

#### Recommended Tools

| Tool              | Type                 | Integration            | Cost                    |
|-------------------|----------------------|------------------------|-------------------------|
| ZAP (by Checkmarx) | Full DAST scanner    | CLI + CI + Docker      | Free                    |
| Nuclei            | Template-based scanner| CLI + CI              | Free                    |
| Burp Suite        | Full DAST + manual   | Manual + CI (Pro)      | Free (Community) / Paid |
| Nikto             | Web server scanner   | CLI + CI               | Free                    |
| StackHawk         | Developer-focused DAST| CI-native             | Free tier / Paid        |

#### ZAP Integration (Recommended Default)

- **SHOULD** use ZAP (by Checkmarx, formerly OWASP ZAP) as the default
  DAST tool — free, open-source, and actively maintained:

  ```bash
  # Quick baseline scan via Docker (passive scan)
  docker run --rm -t zaproxy/zap-stable zap-baseline.py \
    -t https://staging.your-app.com

  # Full active scan (more thorough, more time)
  docker run --rm -t zaproxy/zap-stable zap-full-scan.py \
    -t https://staging.your-app.com
  ```

  ```yaml
  # GitHub Actions example — MUST pin to SHA, not tag
  - name: ZAP Baseline Scan
    uses: zaproxy/action-baseline@7cea08522cd8612907c4caefd5cbc61c793e9117  # v0.14.0
    with:
      target: 'https://staging.your-app.com'
      fail_action: true
  ```

- **SHOULD** run the baseline (passive) scan in CI on every deployment to staging
- **MAY** run the full (active) scan weekly or before major releases

#### DAST Scope

- **SHOULD** configure DAST to test:
  - Authentication and session handling
  - Input validation (XSS, injection)
  - Security headers presence and configuration
  - Error handling (information disclosure)
  - Access control (authenticated vs unauthenticated access)
  - HTTPS and TLS configuration
- **SHOULD** provide DAST tools with authentication credentials to test both unauthenticated and authenticated surfaces

---

### Combined Security Testing Pipeline

- **SHOULD** implement a layered security testing pipeline:

  ```text
  Developer Workstation:
    └─ IDE plugins (SonarLint, Snyk, ESLint security)
       → Real-time feedback during coding

  Pre-commit:
    └─ gitleaks (secret detection)
    └─ ESLint security rules
       → Block secrets and obvious patterns before commit

  Pull Request (CI):
    └─ SAST (SonarQube / Semgrep / CodeQL)
    └─ SCA (npm audit / Snyk / Trivy)
    └─ Dependency license check
       → Block merge on high/critical findings

  Staging Deployment:
    └─ DAST baseline scan (ZAP passive)
    └─ Security header verification
       → Alert or block promotion to production

  Scheduled (Weekly):
    └─ SCA re-scan (new CVEs on existing dependencies)
    └─ DAST full scan (active)
    └─ Container image re-scan
       → Create tickets for new findings

  Pre-Release:
    └─ Full DAST active scan
    └─ Manual penetration testing (for high-value releases)
       → Sign-off before production deployment
  ```

- **MUST** maintain a centralized view of all security findings (use the SAST/DAST tool's dashboard or aggregate into GitHub Issues / project board)
- **MUST** track mean time to remediation (MTTR) for security findings — this is the key metric for security testing effectiveness

### Maturity Levels

| Level            | What to Implement                                                                     | When                                       |
|------------------|---------------------------------------------------------------------------------------|--------------------------------------------|
| **Basic**        | ESLint security plugins + `npm audit` / `pip audit` + gitleaks in pre-commit          | Every project from day one                 |
| **Intermediate** | Add SAST (SonarQube or Semgrep) + Dependabot/Renovate + DAST baseline in CI           | Projects with real users / client data     |
| **Advanced**     | Full pipeline (SAST + SCA + DAST active + container scanning + IaC scanning) + scheduled re-scans | Production applications with sensitive data |
| **Enterprise**   | All above + manual penetration testing + bug bounty program + compliance reporting     | Regulated industries, financial, health    |

- **MUST** implement at minimum the Basic level for every project
- **SHOULD** implement the Intermediate level for any project handling real user data

---

## 14. Data Protection & Privacy (RGPD / GDPR)

### Applicability

This section applies to any project that processes personal data of individuals in the European Union / European Economic Area, regardless of where the application is hosted. Under RGPD, "personal data" includes any information that can identify a natural person directly or indirectly: name, email, IP address, phone number, location data, cookie identifiers, government IDs, and more.

- **MUST** treat RGPD compliance as a technical requirement, not just a legal formality
- **MUST** apply Privacy by Design and Privacy by Default — data protection must be built into the system architecture, not bolted on afterward

### Data Classification & Inventory

- **MUST** maintain a data inventory for each project that documents:
  - What personal data is collected
  - Why it is collected (legal basis)
  - Where it is stored (database, logs, backups, third-party services)
  - Who has access to it
  - How long it is retained
  - How it is protected

- **MUST** classify personal data by sensitivity:

  | Category             | Examples                                          | Required Controls                                             |
  |----------------------|---------------------------------------------------|---------------------------------------------------------------|
  | **Special category** | Health data, biometrics, political opinions, sexual orientation, ethnicity | Explicit consent + encryption + strict access control |
  | **High sensitivity** | Government IDs (NIF, CC), financial data, passwords | Encryption at rest + field-level encryption + audit log       |
  | **Standard PII**     | Name, email, phone, address, date of birth        | Encryption in transit + access control + retention limits     |
  | **Pseudonymized**    | User IDs, hashed identifiers                      | Standard security controls                                    |
  | **Anonymous**        | Aggregated statistics, non-identifiable data       | Not subject to RGPD                                           |

- **SHOULD** document the data inventory in `docs/data-inventory.md` or equivalent, and keep it updated when features change

### Legal Basis for Processing

- **MUST** have a valid legal basis for every type of personal data processing:

  | Legal Basis             | When to Use                                      | Example                           |
  |-------------------------|--------------------------------------------------|-----------------------------------|
  | **Consent**             | Optional data, marketing, analytics, cookies     | Newsletter signup, cookie consent |
  | **Contract**            | Data necessary to fulfill a contract/service     | Name and email to create account  |
  | **Legal obligation**    | Required by law                                  | Tax invoices, fraud prevention    |
  | **Legitimate interest** | Business need, balanced against user rights      | Basic analytics, security logs    |

- **MUST** never use "consent" as the legal basis when the user has no real choice — use "legitimate interest" or "contract" instead, as forced consent is not valid consent under RGPD
- **MUST** make consent:
  - Freely given (no pre-checked boxes)
  - Specific (separate consent for different purposes)
  - Informed (clear explanation of what they consent to)
  - Revocable (as easy to withdraw as to give)

### Consent Management (Technical Implementation)

- **MUST** implement a cookie consent mechanism for non-essential cookies and tracking scripts:
  - **MUST NOT** load analytics, marketing, or tracking scripts before the user gives explicit consent
  - **MUST** respect the user's choice — if they decline, no non-essential cookies are set
  - **SHOULD** use a consent management tool or build a compliant banner:
    - Accept / Reject with equal prominence (no dark patterns)
    - Granular options (analytics, marketing, functional)
    - Persistent record of consent (what was consented, when, version)

- **MUST** store consent records:

  ```ts
  interface ConsentRecord {
    userId: string;
    consentVersion: string;
    purposes: {
      essential: true;
      analytics: boolean;
      marketing: boolean;
    };
    givenAt: string;
    method: string;
    ipAddress?: string;
  }
  ```

- **MUST** be able to demonstrate that consent was given (accountability principle)

### Data Subject Rights (Technical Implementation)

The RGPD grants individuals specific rights over their data. The application **MUST** be technically capable of fulfilling each of these rights:

#### Right of Access (Article 15)

- **MUST** provide a mechanism for users to request a copy of all their personal data
- **SHOULD** implement an automated data export feature (e.g., "Download my data" in account settings)
- **MUST** respond within 30 days of the request
- **SHOULD** export in a structured, machine-readable format (JSON or CSV)

#### Right to Rectification (Article 16)

- **MUST** allow users to correct inaccurate personal data
- **SHOULD** provide self-service editing for common fields (name, email, phone, address)

#### Right to Erasure — "Right to be Forgotten" (Article 17)

- **MUST** implement account deletion that removes or anonymizes all personal data:
  - Delete personal data from the primary database
  - Delete or anonymize personal data from backups (within a reasonable timeframe)
  - Delete personal data from logs (or ensure log retention policies handle this automatically)
  - Notify third-party processors to delete the data
  - Remove data from search engine caches if applicable
- **MUST** design the data model to support deletion from the start:

  ```text
  Strategy 1: Hard delete
  - Physically remove the user's records
  - Simple but may break referential integrity

  Strategy 2: Soft delete + anonymization (RECOMMENDED)
  - Set deleted_at timestamp
  - Replace PII with anonymized values:
    - name → "Deleted User"
    - email → "deleted-{uuid}@anonymized.local"
    - phone → NULL
    - address → NULL
  - Retain non-personal data for business analytics
  - After retention period, hard delete if needed
  ```

- **MUST** handle cascading deletion — when a user is deleted, their data in related tables must also be deleted or anonymized
- **SHOULD** implement a grace period before permanent deletion (e.g., 30 days) — clearly communicate this to the user

#### Right to Data Portability (Article 20)

- **MUST** provide personal data in a structured, commonly used, machine-readable format (JSON, CSV) upon request
- **SHOULD** combine this with the Right of Access export feature

#### Right to Object (Article 21)

- **MUST** allow users to object to processing based on legitimate interest or direct marketing
- **MUST** stop processing for direct marketing immediately upon objection (no exceptions)

### Data Minimization in Practice

- **MUST** collect only the data strictly necessary for each feature:

  ```ts
  // BAD — collecting unnecessary data
  const leadSchema = z.object({
    name: z.string(),
    email: z.string().email(),
    phone: z.string(),
    dateOfBirth: z.string(),
    maritalStatus: z.string(),
    income: z.number(),
  });

  // GOOD — minimum necessary data
  const leadSchema = z.object({
    name: z.string().min(1).max(200),
    email: z.string().email(),
    phone: z.string().optional(),
    message: z.string().max(2000),
  });
  ```

- **MUST** review data collection requirements for each feature — "nice to have" data is not a valid reason to collect it
- **SHOULD** anonymize or aggregate data when the specific purpose no longer requires identification

### Data Retention

- **MUST** define retention periods for each type of personal data and document them:

  | Data Type                | Suggested Retention            | Rationale                       |
  |--------------------------|--------------------------------|---------------------------------|
  | Account data             | Until account deletion + grace period | Service contract duration  |
  | Contact form submissions | 12 months                      | Business follow-up period       |
  | Access / security logs   | 90 days – 1 year               | Security monitoring             |
  | Payment records          | 7–10 years                     | Tax / legal obligations (Portugal) |
  | Analytics data           | 26 months (if anonymized after)| Business analysis               |
  | Marketing consent        | Until withdrawal + 3 years     | Proof of consent                |
  | Deleted account data     | 30 days (grace) then hard delete | Recovery window              |

- **MUST** implement automated cleanup:
  - **SHOULD** create scheduled jobs that delete or anonymize expired personal data
  - **MUST NOT** retain personal data indefinitely "just in case"
- **MUST** document retention periods in the privacy policy

### Third-Party Data Processors

- **MUST** maintain a list of all third-party services that process personal data on behalf of the project:

  | Service          | Data Shared                 | Location       | DPA Required   |
  |------------------|-----------------------------|----------------|----------------|
  | Supabase         | Full database content       | EU (Frankfurt) | Yes            |
  | Vercel           | Request logs, analytics     | Global (US/EU) | Yes            |
  | Stripe           | Payment + customer data     | US + EU        | Yes (built-in) |
  | SendGrid         | Email addresses + content   | US             | Yes            |
  | Sentry           | Error data (may include PII)| US             | Yes            |
  | Google Analytics  | User behavior, IP, device  | US             | Yes + consent  |
  | Cloudflare       | Request data, IPs           | Global         | Yes            |

- **MUST** ensure a Data Processing Agreement (DPA) is in place with every third-party processor
- **SHOULD** prefer EU-based hosting and processing when possible to simplify data transfer compliance
- **MUST** document international data transfers and the legal mechanism used (Standard Contractual Clauses, adequacy decision, etc.)
- **MUST** inform users in the privacy policy about which third parties process their data

### Privacy by Design — Technical Checklist

For every new feature that handles personal data:

- [ ] Data minimization: only the necessary fields are collected
- [ ] Legal basis identified and documented
- [ ] Consent mechanism in place (if consent is the legal basis)
- [ ] Data export is possible for this data (Right of Access)
- [ ] Data deletion or anonymization is possible (Right to Erasure)
- [ ] Retention period defined
- [ ] Encryption appropriate to the data classification is applied
- [ ] Access controls limit who can view this data
- [ ] Third-party processors are documented and have DPAs
- [ ] Privacy policy is updated to reflect the new data collection
- [ ] Audit logging covers access to this data

### Breach Notification

- **MUST** have a documented incident response procedure for personal data breaches
- **MUST** be technically capable of:
  - Detecting a breach (monitoring, alerts — see Section 15)
  - Determining what data was affected (audit logs)
  - Containing the breach (revoking access, rotating credentials)
- **MUST** know the notification requirements:
  - **Supervisory authority (CNPD in Portugal):** within 72 hours of becoming aware of the breach
  - **Affected individuals:** without undue delay if the breach poses a high risk to their rights
- **SHOULD** prepare a breach notification template in advance with the required information:
  - Nature of the breach
  - Categories and approximate number of affected individuals
  - Likely consequences
  - Measures taken to address the breach

---

## 15. Security Logging & Audit Trail

### Logging Categories

This project distinguishes three categories of logging, each with different purposes, retention, and access controls:

| Category         | Purpose                                    | Retention      | Access            |
|------------------|--------------------------------------------|----------------|-------------------|
| Application Logs | Debugging, performance, operations         | 7–30 days      | Development team  |
| Security Logs    | Attack detection, incident investigation   | 90 days – 1 year | Security / Ops  |
| Audit Trail      | Accountability, compliance, dispute resolution | 1–7 years   | Restricted (read-only) |

All three categories **MUST** be implemented in any project handling real user data.

---

### Security Logging

#### What to Log

- **MUST** log the following security-relevant events:

  **Authentication events:**
  - Login success (userId, IP, userAgent, timestamp, method)
  - Login failure (attemptedIdentifier, IP, userAgent, reason, timestamp)
  - Logout (userId, timestamp)
  - Password change (userId, timestamp)
  - Password reset request (email, IP, timestamp)
  - MFA enable / disable / challenge failure (userId, timestamp)
  - Session creation and invalidation

  **Authorization events:**
  - Authorization failure (userId, resource, action, reason, timestamp)
  - Role or permission changes (targetUserId, changedBy, oldRole, newRole)
  - Access to admin or backoffice features (userId, action)

  **Abuse detection events:**
  - Rate limit triggered (IP, endpoint, limitExceeded, timestamp)
  - Account lockout (userId/email, IP, failureCount, timestamp)
  - Suspicious input patterns (IP, endpoint, patternType)
  - Access to known attack paths (IP, path — /.env, /.git, /wp-admin)
  - Unusual geographic or device access (userId, location, device)

  **System security events:**
  - Application startup and shutdown
  - Configuration changes
  - TLS certificate expiration warnings
  - Dependency vulnerability alerts

  **Agent events (when AI agents take actions → See [12-ai-engineering.md, §6.8] and §6.3):**
  - Agent action executed — one event per side-effecting tool call (principal, action, resourceId, result)
  - Agent action denied / not confirmed — blocked by the action-safety gate (principal, action, reason)
  - Agent budget / step ceiling exceeded (taskId, steps, reason)

#### What MUST NOT Be Logged

- **MUST NOT** log:
  - Passwords (even failed attempts — log "invalid password" not the value)
  - Full tokens or session identifiers (log last 4-6 characters: `...a1b2c3`)
  - Credit card numbers (log last 4 digits only: `****1234`)
  - Full government IDs
  - Encryption keys or secrets
  - Request bodies containing sensitive data (log metadata only)
- **SHOULD** implement a log sanitization layer that automatically redacts known sensitive field names:

  ```ts
  const SENSITIVE_FIELDS = [
    'password', 'token', 'secret', 'authorization',
    'cookie', 'creditCard', 'cardNumber', 'cvv',
    'ssn', 'nif', 'apiKey', 'privateKey',
  ];

  function sanitizeForLogging(data: Record<string, unknown>): Record<string, unknown> {
    const sanitized = { ...data };
    for (const key of Object.keys(sanitized)) {
      if (SENSITIVE_FIELDS.some(field => key.toLowerCase().includes(field))) {
        sanitized[key] = '[REDACTED]';
      }
    }
    return sanitized;
  }
  ```

#### Log Structure

- **MUST** use structured logging (JSON format) — never unstructured text strings:

  ```ts
  // BAD — unstructured, unparseable, no context
  console.log("Login failed for user " + email);

  // GOOD — structured, searchable, machine-parseable
  logger.warn({
    event: 'auth.login.failure',
    email: maskEmail(email),
    ip: request.ip,
    userAgent: request.headers['user-agent'],
    reason: 'invalid_password',
    requestId: request.id,
    timestamp: new Date().toISOString(),
  });
  ```

- **MUST** include in every security log entry:
  - `event` — structured event name using dot notation (e.g., `auth.login.success`, `authz.denied`, `ratelimit.exceeded`)
  - `timestamp` — ISO-8601 UTC
  - `requestId` — correlation ID for tracing
  - `ip` — client IP address
  - `userId` — when authenticated (omit for anonymous actions)
- **SHOULD** use a consistent event naming taxonomy:

  ```text
  auth.login.success
  auth.login.failure
  auth.logout
  auth.password.change
  auth.password.reset_request
  auth.mfa.enable
  auth.mfa.disable
  auth.session.create
  auth.session.invalidate
  authz.denied
  authz.role.change
  ratelimit.exceeded
  security.suspicious_input
  security.attack_path_access
  security.account.lockout
  audit.resource.create
  audit.resource.update
  audit.resource.delete
  agent.action.<name>
  agent.action.denied
  agent.budget.exceeded
  ```

#### Log Storage & Protection

- **MUST** store security logs separately from application logs when possible (different log stream, different access controls)
- **MUST NOT** allow application code to modify or delete security logs
- **SHOULD** forward security logs to an external service for tamper resistance and centralized analysis:

  | Tool                  | Type                 | Key Strength                   |
  |-----------------------|----------------------|--------------------------------|
  | Sentry                | Error tracking       | Rich error context, alerting   |
  | Grafana Loki          | Log aggregation      | Pairs with Grafana dashboards  |
  | Datadog               | Full observability   | Logs + metrics + APM           |
  | AWS CloudWatch        | Cloud-native logging | Native AWS integration         |
  | Betterstack (Logtail) | Log management       | Developer-friendly, affordable |
  | Axiom                 | Log aggregation      | Generous free tier, fast       |

- **SHOULD** encrypt security logs at rest and in transit
- **MUST** restrict access to security logs — only authorized personnel should be able to read them

#### Alerting

- **SHOULD** configure real-time alerts for critical security events:

  | Pattern                                 | Alert Priority | Action                               |
  |-----------------------------------------|----------------|--------------------------------------|
  | 5+ failed logins from same IP in 5 min  | High           | Investigate, potential brute force   |
  | Admin action from new IP/device         | High           | Verify with admin                    |
  | Rate limit exceeded 10+ times in 1 min  | Medium         | Review, potential attack             |
  | Access to /.env, /.git, /wp-admin       | Medium         | Log and monitor                      |
  | Authorization failure spike             | High           | Investigate, potential privilege escalation |
  | Successful login after multiple failures| Medium         | Verify legitimacy                    |
  | New admin role granted                  | High           | Verify authorization                 |
  | Bulk data export or access              | High           | Verify authorization                 |

- **SHOULD** use the alerting capabilities of the chosen log platform (Sentry alerts, Grafana alert rules, Datadog monitors)
- **MUST** define escalation paths — who gets notified and how (email, Slack, SMS) based on alert priority

---

### Audit Trail

The audit trail is a **tamper-resistant, append-only record** of all significant business actions performed in the system. It exists for accountability, compliance, and dispute resolution.

#### What to Audit

- **MUST** create an audit record for every state-changing operation on protected or sensitive resources:

  | Action Category        | Examples                                              |
  |------------------------|-------------------------------------------------------|
  | Data creation          | New user registered, vehicle listed, lead created     |
  | Data modification      | Price changed, status updated, profile edited         |
  | Data deletion          | Account deleted, record removed                       |
  | Permission changes     | Role assigned, access granted/revoked                 |
  | Financial operations   | Payment processed, refund issued, invoice generated   |
  | Configuration changes  | Settings modified, feature flags toggled              |
  | Data exports           | Report generated, bulk data exported                  |

#### Audit Record Structure

- **MUST** include the following fields in every audit record:

  ```ts
  interface AuditRecord {
    id: string;
    timestamp: string;
    actor: {
      userId: string;
      role: string;
      ip: string;
      userAgent?: string;
    };
    action: string;
    resource: {
      type: string;
      id: string;
    };
    changes?: {
      before: Record<string, unknown>;
      after: Record<string, unknown>;
    };
    result: 'success' | 'failure';
    metadata?: Record<string, unknown>;
  }
  ```

- **MUST** capture the `before` and `after` values for update operations:

  ```ts
  // Example audit record
  {
    id: "audit_a1b2c3d4",
    timestamp: "2026-03-15T14:32:07.000Z",
    actor: {
      userId: "user_789",
      role: "partner",
      ip: "198.51.100.42",
    },
    action: "vehicle.price.update",
    resource: {
      type: "vehicle",
      id: "vehicle_456",
    },
    changes: {
      before: { price: 15000 },
      after: { price: 12000 },
    },
    result: "success",
  }
  ```

#### Audit Trail Storage

- **MUST** store audit records in an append-only manner:
  - **MUST NOT** allow UPDATE or DELETE operations on the audit table — not even by administrators
  - In PostgreSQL, enforce with a trigger:

    ```sql
    -- Create audit table
    CREATE TABLE audit_logs (
      id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
      actor_id TEXT NOT NULL,
      actor_role TEXT NOT NULL,
      actor_ip INET,
      action TEXT NOT NULL,
      resource_type TEXT NOT NULL,
      resource_id TEXT NOT NULL,
      changes JSONB,
      result TEXT NOT NULL CHECK (result IN ('success', 'failure')),
      metadata JSONB
    );

    -- Prevent modifications
    CREATE OR REPLACE FUNCTION prevent_audit_modification()
    RETURNS TRIGGER AS $$
    BEGIN
      RAISE EXCEPTION 'Audit logs cannot be modified or deleted';
    END;
    $$ LANGUAGE plpgsql;

    CREATE TRIGGER audit_immutability
      BEFORE UPDATE OR DELETE ON audit_logs
      FOR EACH ROW
      EXECUTE FUNCTION prevent_audit_modification();

    -- Index for common queries
    CREATE INDEX idx_audit_actor ON audit_logs (actor_id, timestamp DESC);
    CREATE INDEX idx_audit_resource ON audit_logs (resource_type, resource_id, timestamp DESC);
    CREATE INDEX idx_audit_action ON audit_logs (action, timestamp DESC);
    ```

- **SHOULD** store audit logs in a separate database or schema from application data when possible
- **SHOULD** replicate or forward audit logs to an external service for additional tamper resistance

#### Audit Trail in Supabase

- **SHOULD** implement audit logging at the application service layer (insert audit records when performing actions)
- **MAY** supplement with database-level triggers for critical tables as a defense-in-depth measure
- **MUST** use a dedicated service_role connection for audit writes — the audit table should not be accessible via the client-facing anon key or user JWTs
- **MUST** ensure RLS on the audit table blocks all client access:

  ```sql
  ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
  -- No policies = no access via anon/authenticated roles
  -- Only service_role (bypasses RLS) can read/write
  ```

#### Retention & Compliance

- **MUST** define audit trail retention periods based on business and legal requirements:

  | Context                    | Minimum Retention              |
  |----------------------------|--------------------------------|
  | General business actions   | 1 year                         |
  | Financial transactions     | 7–10 years (Portuguese tax law)|
  | User consent records       | Duration of consent + 3 years  |
  | Security incidents         | 3–5 years                      |
  | Health / special category  | As required by regulation      |

- **MUST NOT** delete audit records before the retention period expires
- **SHOULD** implement automated archival for old audit records (move to cold storage, not delete)

#### Querying the Audit Trail

- **SHOULD** provide an admin interface for querying audit logs:
  - Filter by: actor, action, resource, date range, result
  - **MUST** restrict audit log viewing to authorized roles only
  - **MUST** audit access to the audit trail itself (who viewed the audit logs and when)
- **SHOULD** support correlation — link audit records to the corresponding requestId in application/security logs for full request tracing

---

## 16. Incident Response (Lightweight)

### Purpose

A documented incident response procedure ensures that when a security incident occurs, the team acts quickly, methodically, and without destroying evidence — rather than improvising under pressure.

- **MUST** have a documented incident response procedure before the application goes to production — even for solo/freelance projects
- The procedure scales with project size: a solo developer needs a simple checklist; a team needs roles and communication channels

### Severity Classification

- **MUST** classify incidents by severity to prioritize response:

  | Severity     | Description                                                     | Response Time    | Examples                                                                  |
  |--------------|-----------------------------------------------------------------|------------------|---------------------------------------------------------------------------|
  | **Critical** | Active exploitation, data breach confirmed, service fully compromised | Immediate (within 1 hour) | Database credentials exposed and used, ransomware, confirmed data exfiltration |
  | **High**     | Confirmed vulnerability being actively exploited, significant data exposure risk | Within 4 hours | Secret exposed in public repo, auth bypass discovered, critical CVE in production |
  | **Medium**   | Vulnerability confirmed but not yet exploited, limited exposure | Within 24 hours  | Non-critical secret exposed in private repo, medium CVE, suspicious patterns |
  | **Low**      | Potential vulnerability, no evidence of exploitation            | Within 1 week    | Low-severity CVE, minor misconfiguration, informational finding           |

### Incident Response Phases

#### Phase 1: Detection & Triage (Minutes 0–30)

- **MUST** confirm the incident is real (not a false positive)
- **MUST** classify severity using the table above
- **MUST** assign an incident owner — one person responsible for coordinating the response
- **MUST** begin a written incident log immediately:

  ```md
  ## Incident Log: [Brief Description]
  **Severity:** Critical / High / Medium / Low
  **Detected:** 2026-03-15T14:30:00Z
  **Owner:** [Name]
  **Status:** Investigating / Contained / Resolved / Post-mortem complete

  ### Timeline
  - 14:30 — Alert received: Sentry reported unusual error spike on /api/auth
  - 14:35 — Confirmed: auth endpoint returning 500 with partial stack traces
  - 14:40 — Containment: disabled endpoint via feature flag
  - ...
  ```

- **SHOULD** use a dedicated channel for incident communication

#### Phase 2: Containment (Minutes 15–60)

**The goal is to STOP the damage. Speed matters more than perfection.**

- **MUST** take immediate containment actions based on incident type:

  | Incident Type                    | Immediate Containment Actions                                     |
  |----------------------------------|-------------------------------------------------------------------|
  | Secret / API key exposed         | 1. Revoke immediately. 2. Generate and deploy new secret. 3. Check access logs |
  | Unauthorized access detected     | 1. Disable compromised account. 2. Invalidate all sessions. 3. Reset credentials |
  | Vulnerability actively exploited | 1. Deploy hotfix or disable feature. 2. Block attacking IPs. 3. Enable stricter rate limiting |
  | Data breach confirmed            | 1. Isolate affected system. 2. Revoke compromised credentials. 3. Preserve logs. 4. Start RGPD 72h countdown |
  | Dependency compromise            | 1. Pin to last safe version. 2. Audit for compromise indicators. 3. Rebuild and redeploy |
  | Malicious insider                | 1. Revoke all access immediately. 2. Preserve audit logs. 3. Change all accessible secrets |

- **MUST** prioritize containment over root cause analysis
- **MUST NOT** destroy evidence during containment:
  - Do NOT delete logs
  - Do NOT restart servers without capturing current state
  - Do NOT redeploy without preserving the compromised version
  - Do NOT modify database records to "fix" the issue

#### Phase 3: Investigation & Eradication (Hours 1–48)

- **MUST** determine the scope of the incident:
  - What systems were affected?
  - What data was accessed, modified, or exfiltrated?
  - How did the attacker gain access (attack vector)?
  - How long was the system compromised (dwell time)?
  - Are there indicators of compromise (IoC) in other systems?
- **MUST** use available evidence:
  - Security logs (Section 15)
  - Audit trail records
  - Application logs
  - Infrastructure access logs
  - Version control history (git log)
  - Network logs (if available)
- **MUST** eradicate the root cause:
  - Patch the vulnerability
  - Remove unauthorized access
  - Rotate all potentially compromised credentials
  - Update affected dependencies
  - Fix the misconfiguration
- **MUST** verify eradication:
  - Confirm the vulnerability is no longer exploitable
  - Run security scans (SAST, DAST) on the fix
  - Review related code/configuration for similar issues

#### Phase 4: Recovery (Hours 24–72)

- **MUST** restore normal operations methodically:
  - Redeploy from a known clean state
  - Re-enable disabled features incrementally
  - Monitor closely for recurrence (increased alerting for 48–72 hours)
- **MUST** rotate credentials broadly if scope is uncertain:
  - All database passwords
  - All API keys that may have been exposed
  - All JWT signing keys (accept both old and new during transition)
  - All service account tokens
- **SHOULD** communicate recovery status to affected parties

#### Phase 5: Post-Mortem (Within 1 Week)

- **MUST** conduct a blameless post-mortem for every High and Critical severity incident
- **SHOULD** conduct a post-mortem for Medium severity incidents
- **MUST** document the post-mortem using a structured format:

  ```md
  ## Post-Mortem: [Incident Title]
  **Date:** [Date of incident]
  **Severity:** [Level]
  **Duration:** [Detection to resolution]
  **Author:** [Post-mortem author]

  ### Summary
  One paragraph describing what happened.

  ### Impact
  - What was affected (systems, data, users)
  - Number of users affected (if applicable)
  - Duration of impact
  - Data exposure details (if applicable)

  ### Timeline
  Detailed timeline from the incident log.

  ### Root Cause
  Technical root cause — focus on SYSTEMS and PROCESSES, not people.

  ### Contributing Factors
  What conditions allowed this to happen?

  ### Resolution
  What was done to fix the immediate issue.

  ### Action Items
  | Action                              | Owner   | Priority | Deadline   |
  |-------------------------------------|---------|----------|------------|
  | Add gitleaks pre-commit hook        | [Name]  | High     | [Date]     |
  | Enable GitHub secret scanning       | [Name]  | High     | [Date]     |
  | Add rate limiting to auth endpoints | [Name]  | Medium   | [Date]     |

  ### Lessons Learned
  What did we learn? What would we do differently?
  ```

- **MUST** track action items to completion

### RGPD Breach Notification Integration

- **MUST** evaluate whether the incident constitutes a personal data breach under RGPD
- **MUST** start the 72-hour notification clock from the moment the breach is confirmed:

  | Action                            | Deadline                           | Responsible         |
  |-----------------------------------|------------------------------------|---------------------|
  | Notify CNPD (Portuguese DPA)      | Within 72 hours                    | Project owner / DPO |
  | Notify affected individuals       | Without undue delay (if high risk) | Project owner / DPO |
  | Document the breach internally    | Immediately                        | Incident owner      |

- **SHOULD** have a pre-drafted notification template ready:

  ```md
  ## Data Breach Notification — [Organization Name]

  **Date of breach:** [Date]
  **Date of detection:** [Date]
  **Nature of breach:** [unauthorized access / data exposure / ...]

  **Personal data affected:**
  - Categories: [names, emails, phone numbers, ...]
  - Approximate number of affected individuals: [number]

  **Likely consequences:**
  [Description of potential impact on affected individuals]

  **Measures taken:**
  - [Containment actions]
  - [Eradication actions]
  - [Notification to affected individuals — if applicable]

  **Contact:**
  [Name, email, phone for the DPO or responsible person]
  ```

### Emergency Contacts & Resources

- **MUST** maintain an up-to-date list of emergency contacts:

  ```md
  ## Emergency Contacts

  ### Internal
  - Project Owner: [Name] — [Phone] — [Email]
  - Technical Lead: [Name] — [Phone] — [Email]

  ### Service Providers
  - Hosting (Vercel/Railway): [Support URL / contact]
  - Database (Supabase): [Support URL / contact]
  - Domain/DNS (Cloudflare): [Support URL / contact]
  - Payment processor (Stripe): [Support URL / contact]

  ### Regulatory
  - CNPD (Portuguese DPA): [https://www.cnpd.pt]

  ### Security Resources
  - CERT.PT (Portuguese CERT): [https://www.cncs.gov.pt]
  ```

- **MUST** ensure this document is accessible even if primary systems are compromised (keep a copy outside the production infrastructure)

### Incident Response Drills (Optional but Recommended)

- **MAY** conduct periodic incident response drills for team projects
- **SHOULD** review and update the incident response procedure at least annually or after every real incident

---

## 17. Pre-Deployment Security Checklist

Use these checklists before deploying to production. Each level includes all checks from the previous level.

---

### Level 1: Every Deploy (Continuous)

These checks **MUST** pass on every deployment — most should be automated in CI/CD.

#### Automated Gates (CI/CD)

- [ ] **Lint passes** — no ESLint / Pylint errors (including security plugins)
- [ ] **Type check passes** — `tsc --noEmit` or equivalent with strict mode
- [ ] **Tests pass** — unit + integration test suites green
- [ ] **SAST scan clean** — no new high/critical findings (SonarQube, Semgrep, CodeQL, Bandit)
- [ ] **Dependency audit clean** — `npm audit` / `pip audit` reports no high/critical vulnerabilities
- [ ] **Secret scanning clean** — gitleaks or equivalent confirms no secrets in the codebase
- [ ] **Container scan clean** (if applicable) — Trivy reports no critical vulnerabilities
- [ ] **Build succeeds** — production build completes without errors

#### Manual Verification (Quick)

- [ ] **No secrets in code** — quick review of PR diff
- [ ] **Environment variables correct** — production env vars set and match `.env.example`
- [ ] **Error responses safe** — no stack traces, internal paths, or database errors exposed
- [ ] **Debug mode off** — `NODE_ENV=production`, `DEBUG=False`, dev tools disabled

---

### Level 2: New Feature / Major Release

Everything from Level 1, plus:

#### Input & Data Validation

- [ ] **All new inputs validated** — every new form field, API parameter validated with Zod / Pydantic at the server boundary
- [ ] **File uploads secured** (if applicable) — magic byte validation, size limits, renamed files, stored outside web root
- [ ] **Output encoding correct** — user-generated content properly escaped
- [ ] **Pagination capped** — new list endpoints have maximum page size enforced
- [ ] **Array inputs limited** — batch operations have explicit max array sizes

#### Authentication & Authorization

- [ ] **Authentication enforced** — every new protected endpoint requires valid authentication
- [ ] **Authorization enforced** — every new protected endpoint checks permissions AND resource ownership
- [ ] **IDOR tested** — new endpoints tested by attempting to access resources belonging to a different user
- [ ] **Role boundaries tested** — verify that each role can ONLY perform defined actions
- [ ] **Session handling correct** — new auth flows regenerate session IDs, respect expiration

#### API Security

- [ ] **Rate limiting configured** — new endpoints have appropriate rate limits
- [ ] **HTTP methods restricted** — endpoints only accept supported methods
- [ ] **Request size limits set** — body size limits configured for new endpoints
- [ ] **Sensitive data not in URLs** — no tokens, passwords, or PII in query parameters
- [ ] **API responses minimal** — endpoints return only necessary fields
- [ ] **Webhook signatures verified** (if applicable)

#### Data Protection

- [ ] **RGPD compliance checked** — new data collection has legal basis, consent mechanism, retention period
- [ ] **Data minimization applied** — only strictly necessary fields collected
- [ ] **Deletion path exists** — new personal data can be deleted or anonymized
- [ ] **Data export includes new fields** — Right of Access export covers new personal data
- [ ] **Third-party processors documented** — new external services added to processor list with DPA

#### Threat Assessment

- [ ] **STRIDE analysis completed** — for features involving auth, payments, PII, file uploads, or admin actions
- [ ] **Abuse cases considered** — "what if someone does this 10,000 times?"

#### Observability

- [ ] **Security events logged** — new auth, authorization, and sensitive actions produce structured log entries
- [ ] **Audit trail entries created** — new state-changing operations produce audit records with before/after values
- [ ] **Sensitive data redacted in logs** — new log statements do not contain passwords, tokens, or PII
- [ ] **Error monitoring configured** — new error paths report to Sentry or equivalent

---

### Level 3: Initial Launch (Go-Live)

Everything from Levels 1 and 2, plus:

#### Transport & Infrastructure Security

- [ ] **HTTPS enforced** — all traffic redirected to HTTPS, no mixed content
- [ ] **HSTS enabled** — `Strict-Transport-Security` header present
- [ ] **TLS configuration verified** — SSL Labs test grade A or A+
- [ ] **Database connections encrypted** — TLS/SSL enabled for all database connections
- [ ] **Backup encryption verified** — database and file backups encrypted at rest

#### Security Headers

- [ ] **Security headers audit passed** — securityheaders.com grade A or A+:
- [ ] Content-Security-Policy configured and tested
- [ ] X-Content-Type-Options: nosniff
- [ ] X-Frame-Options: DENY (or CSP frame-ancestors)
- [ ] Referrer-Policy: strict-origin-when-cross-origin
- [ ] Permissions-Policy configured
- [ ] Strict-Transport-Security present
- [ ] **Technology headers removed** — X-Powered-By, Server version not exposed
- [ ] **API routes not indexable** — X-Robots-Tag: noindex on API responses
- [ ] **Cache headers correct** — sensitive responses use `Cache-Control: no-store`

#### Database Security

- [ ] **RLS enabled on every table** (Supabase) — → See [04-database-standards.md, §7] for policy patterns and per-table checklist
- [ ] **RLS policies tested** — users cannot access data outside their scope
- [ ] **service_role key server-only** — never exposed to client
- [ ] **Database credentials unique** — production different from dev/staging
- [ ] **Database not publicly accessible** — restricted to application servers only
- [ ] **Migrations reviewed** — all migration files reviewed for security
- [ ] **Indexes in place** — performance-critical queries indexed

#### Secrets Management

- [ ] **All secrets in environment variables** — none hardcoded
- [ ] **Secrets differ per environment** — dev, staging, production use different values
- [ ] **Secret rotation procedure documented**
- [ ] **GitHub secret scanning enabled** — push protection active
- [ ] **Pre-commit hooks installed** — gitleaks or equivalent
- [ ] **.gitignore verified** — `.env` and sensitive files excluded
- [ ] **.dockerignore verified** (if applicable)

#### Dependency & Supply Chain

- [ ] **All dependencies audited** — `npm audit` / `pip audit` clean
- [ ] **Lock files committed**
- [ ] **CI uses deterministic installs** — `npm ci` / `--frozen-lockfile`
- [ ] **Dependabot or Renovate enabled**
- [ ] **No unnecessary dependencies** — unused packages removed

#### Security Testing

- [ ] **SAST scan completed** — no unaddressed high/critical findings
- [ ] **DAST baseline scan completed** — ZAP or equivalent against staging
- [ ] **Container scan completed** (if applicable)
- [ ] **Manual security review completed** — focused review of auth, access control, input handling

#### RGPD & Privacy

- [ ] **Privacy policy published** — accessible from the application
- [ ] **Cookie consent implemented** — non-essential cookies blocked until consent
- [ ] **Data inventory documented**
- [ ] **Data subject rights functional** — users can access, export, correct, delete their data
- [ ] **Third-party DPAs in place**
- [ ] **Data retention automation** — scheduled cleanup configured
- [ ] **Breach notification procedure ready**

#### Monitoring & Incident Readiness

- [ ] **Error monitoring active** — Sentry or equivalent configured
- [ ] **Uptime monitoring active** — UptimeRobot, Betterstack, or equivalent
- [ ] **Security alerting configured** — alerts for failed logins, rate limit spikes
- [ ] **Audit trail functional** — immutable audit records being produced
- [ ] **Incident response plan documented** — procedure, contacts, templates ready
- [ ] **Backup and recovery tested** — database backup restored at least once

#### Application Hardening

- [ ] **Default credentials removed**
- [ ] **Debug endpoints disabled**
- [ ] **Admin panel protected** — requires authentication, not publicly discoverable
- [ ] **Error pages customized** — no framework default error pages in production
- [ ] **File system permissions correct**
- [ ] **Directory listing disabled**

#### Documentation

- [ ] **README up to date**
- [ ] **ADRs documented**
- [ ] **Runbook available** — deploy, rollback, restart, scale procedures
- [ ] **Emergency contacts current**

---

### Checklist Usage Rules

- **MUST** complete Level 1 for every production deployment — automate as much as possible in CI/CD
- **MUST** complete Level 2 for every new feature or significant change
- **MUST** complete Level 3 before the first production deployment of any new application
- **SHOULD** store the completed checklist with the release (PR comment, release note, or deploy record)
- **MUST** not skip checklist items without documented justification — "we're in a hurry" is never a valid reason
- **SHOULD** review and update this checklist quarterly or after every security incident

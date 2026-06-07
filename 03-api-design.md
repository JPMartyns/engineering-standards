# 🔌 API Design Standards

> **Scope:** Practical guide for designing, implementing, and maintaining REST APIs
> across all projects covered by these engineering standards.
>
> **Purpose:** The reference that answers "how should this endpoint look, behave,
> and respond?" — ensuring every API is consistent, predictable, and
> well-documented, regardless of the underlying framework.
>
> **Keywords:**
> - **MUST** = required (PR should be blocked if violated)
> - **SHOULD** = strongly recommended (requires justification to skip)
> - **MAY** = optional (case-by-case)

---

## 0. How to Use This Document

- This document defines **how to design and implement APIs** — URL structure,
  request/response format, error handling, pagination, and documentation patterns.
- It does **not** define how to secure APIs (that lives in
  → See [07-security-standards.md]) or which frameworks to use (that lives in
  → See [02-technology-radar.md]). It references both heavily.
- Code examples use **TypeScript** with **Next.js Route Handlers** (default
  full-stack) and **Express.js** (standalone APIs), reflecting the Adopt
  choices in → See [02-technology-radar.md, Section 4.7].
- The layering model assumed throughout is:
  `Route Handler / Controller → Service → Repository`
  (→ See [01-core-principles.md, Section 6]).
- When a rule here overlaps with security, the security document takes
  precedence — this document defers to → See [07-security-standards.md] on
  all security-related decisions.

### Document Relationships

```text
03-api-design.md (this document)
 ├── Derives from    → 01-core-principles.md (error handling, layering, fail-fast, naming)
 ├── Derives from    → 02-technology-radar.md (framework choices, API tooling)
 ├── Complements     → 07-security-standards.md (validation rules, rate limiting, auth, CORS)
 ├── Referenced by   → 04-database-standards.md (response format ↔ query patterns)
 ├── Referenced by   → 05-frontend-standards.md (API consumption, error handling in UI)
 ├── Referenced by   → 06-testing-strategy.md (API testing patterns)
 └── Referenced by   → 08-observability.md (request IDs, logging, monitoring)
```

### Boundary Definitions

| Question | This Document (03) | Other Document |
|----------|--------------------|----------------|
| **Which** API framework to use? | — | → See [02-technology-radar.md, §3.7] |
| **How** to structure URLs, methods, status codes? | ✅ Sections 2–3 | — |
| **How** to format requests and responses? | ✅ Section 4 | — |
| **How** to handle errors in the API? | ✅ Section 5 | → See [01-core-principles.md, §3.4] (error philosophy) |
| **How** to validate input with Zod? | ✅ Section 6 | → See [07-security-standards.md, §3] (security constraints) |
| **How** to validate output? | ✅ Section 6.7 (Output Validation) | — |
| **How** to secure API endpoints (auth, rate limiting, CORS)? | ✅ Section 9–10 (patterns) | → See [07-security-standards.md] (takes precedence on security rules) |
| **How** to test API endpoints? | ✅ Section 13 (API-specific patterns) | → See [06-testing-strategy.md] (strategy, pyramid, CI gates) |
| **How** to handle file uploads? | ✅ Section 6.8 | → See [07-security-standards.md, §3] (security constraints) |

### Technology Versions

| Technology | Version | Role |
|---|---|---|
| Next.js | 16.x | Route Handlers (App Router) |
| Express.js | 4.x / 5.x | Standalone API framework |
| Zod | 4.x | Schema validation |
| Auth.js | v5 | Multi-provider authentication |
| Supabase Auth | Latest | Default authentication provider |
| TypeScript | 5.x+ | All code examples |

### AI Agent Instructions

This document is designed to be consumed by AI coding agents (e.g., Claude
Code). When interpreting this document:

- **MUST**, **SHOULD**, and **MAY** are RFC 2119 keywords — treat MUST as non-negotiable constraints, SHOULD as strong defaults that require explicit justification to override, and MAY as contextual options.
- Cross-references (→ See [XX-document.md]) point to authoritative definitions — always defer to the referenced document for the full rule.
- When this document conflicts with [07-security-standards.md], the security document takes precedence.
- BAD/GOOD code examples are pattern-matching references — apply the principle behind the example, not just the literal code.
- Anti-pattern tables describe common mistakes — use them as negative examples when reviewing or generating code.
- Every API endpoint generated or reviewed MUST follow the response envelope, error format, and URL conventions defined here.
- If generating code requires violating a MUST rule, the AI **MUST stop** and ask the human for permission before proceeding — never silently override a standard.
- **MUST NOT** over-engineer — always prefer the simplest solution that meets the stated requirements. Do not add abstractions, patterns, or infrastructure beyond what was explicitly requested (→ See [01-core-principles.md, §12]).
- **Version-critical rules for code generation:**
  - Next.js 16 App Router: `params` and `searchParams` in Page, Layout, and Route Handler components are **Promises** and MUST be awaited. Synchronous access will cause runtime errors.
  - Zod 4: Use top-level format functions (`z.email()`, `z.uuid()`) instead of `z.string().email()`. Use unified `error` param instead of `errorMap`.

---

## 1. API Design Philosophy

An API is not an afterthought bolted onto a working backend — it is the **public
contract** of your application. Every consumer (frontend, mobile app, third-party
integration, your future self) depends on this contract being consistent,
predictable, and well-documented. A poorly designed API creates friction that
compounds across every client that consumes it.

These principles guide every decision in this document.

### 1.1 APIs Are Contracts, Not Implementation Details

An API endpoint is a **promise** to its consumers: "send me this, and I will
respond with that." Once published, changing that promise has a cost — every
consumer that depends on it must adapt.

- **MUST** design APIs from the **consumer's perspective** first — what does the
  caller need? — not from the database schema outward
- **MUST** treat published API responses as a contract — removing fields, changing
  types, or altering behavior are **breaking changes** (→ See [Section 8](#8-versioning-strategy))
- **SHOULD** design the API before writing the implementation — even a quick
  sketch of endpoints, request shapes, and response shapes prevents rework

> **Why:** When the API is shaped by the database schema, internal changes (column
> renames, table splits, normalization) ripple outward to every consumer. When
> the API is shaped by consumer needs, the internal implementation can change
> freely behind a stable contract.

### 1.2 Resource-Oriented Design

REST APIs model **resources** (nouns), not **actions** (verbs). A resource is any
concept that consumers interact with — users, orders, invoices, appointments.
HTTP methods express the action; the URL identifies the resource.

- **MUST** model endpoints around resources, not operations:

  ```
  # BAD — action-oriented (RPC-style)
  POST /api/getUserById
  POST /api/createNewOrder
  POST /api/deleteInvoice

  # GOOD — resource-oriented (REST)
  GET    /api/users/:id
  POST   /api/orders
  DELETE /api/invoices/:id
  ```

- **SHOULD** keep resources aligned with **domain concepts**, not database tables
  — if the business says "appointment," the API says `/appointments`, even if the
  database table is called `bookings`

> **Why:** Resource-oriented design leverages HTTP semantics (methods, status
> codes, caching headers) that clients, proxies, and tools already understand.
> Action-oriented APIs reinvent these semantics poorly and inconsistently.

### 1.3 Consistency Over Cleverness

A predictable API is more valuable than a clever one. If a developer learns how
one endpoint behaves — naming, error format, pagination — they should be able to
predict how every other endpoint behaves.

- **MUST** use the same response envelope across all endpoints
  (→ See [Section 4](#4-request--response-format))
- **MUST** use the same error structure across all endpoints
  (→ See [Section 5](#5-error-handling))
- **MUST** use consistent naming patterns across all URLs
  (→ See [Section 2](#2-url--resource-design))
- **SHOULD** prefer boring, well-understood patterns over novel approaches — REST
  conventions exist because they reduce the learning curve for every new consumer

> **Why:** Inconsistency forces consumers to read documentation for every single
> endpoint instead of learning the pattern once. It also introduces bugs when
> consumers assume consistency that does not exist.

### 1.4 Thin Handlers, Rich Services

API route handlers (controllers) are **translators** between HTTP and business
logic. They receive a request, validate input, call a service, and format the
response. They do not contain business rules.

- **MUST** keep route handlers focused on HTTP concerns:
  1. Parse and validate the incoming request (Zod)
  2. Call the appropriate service function
  3. Map the service result to an HTTP response (status code + envelope)
  4. Handle errors via centralized error mapping

- **MUST NOT** place business logic, database queries, or authorization
  decisions directly in route handlers

- **SHOULD** keep route handler functions short enough that their entire flow
  is visible without scrolling

  ```ts
  // GOOD — thin handler, clear flow
  export async function POST(request: NextRequest) {
    const body = await request.json();
    const parsed = createOrderSchema.parse(body);

    const order = await orderService.create(parsed);

    return NextResponse.json(
      { ok: true, data: order, requestId: getRequestId() },
      { status: 201 }
    );
  }
  ```

> **Why:** Thin handlers are testable, replaceable, and framework-independent.
> If you migrate from Next.js Route Handlers to Express (or vice versa), only
> the handler layer changes — business logic stays untouched.
> → See [01-core-principles.md, Section 6 — Separation of Concerns & Layering].

### 1.5 Server Actions Are API Endpoints

Next.js Server Actions (`'use server'`) look like regular functions but
are compiled into HTTP POST endpoints. Every security rule that applies
to API Route Handlers also applies to Server Actions.

- **MUST** validate all inputs with Zod inside the Server Action — the
  function signature alone does not provide runtime validation
- **MUST** verify authentication and authorization inside the Server
  Action — RLS alone is not sufficient if the action performs logic
  before the database call
- **MUST** return structured error responses — not raw thrown errors
- **MUST NOT** treat Server Actions as "safe" because they are
  server-side — they are publicly callable endpoints
```ts
// BAD — no validation, no auth, trusts the input
'use server';
export async function updateProfile(data: { name: string }) {
  await db.user.update({ where: { id: data.id }, data });
}

// GOOD — validated, authenticated, structured response
'use server';
import { updateProfileSchema } from '@/schemas/user-schema';
import { getAuthenticatedUser } from '@/lib/auth';

export async function updateProfile(formData: FormData) {
  const user = await getAuthenticatedUser();
  if (!user) return { ok: false, error: { code: 'UNAUTHORIZED' } };

  const parsed = updateProfileSchema.safeParse(Object.fromEntries(formData));
  if (!parsed.success) return { ok: false, error: { code: 'VALIDATION_ERROR', details: parsed.error.flatten() } };

  await userService.updateProfile(user.id, parsed.data);
  return { ok: true };
}
```

> **Why:** AI agents frequently treat Server Actions as local function
> calls and omit validation, auth, and error handling. They are not local
> — they are HTTP endpoints with the same attack surface as Route Handlers.
> → See [07-security-standards.md, §3] for the full input validation rules.

### 1.6 Fail Fast, Respond Clearly

When something goes wrong, the API must tell the consumer **what** failed,
**why** it failed, and **what they can do about it** — immediately, not after
silently corrupting data.

- **MUST** validate all input at the API boundary before any processing
  (→ See [Section 6](#6-input-validation))
- **MUST** return structured, machine-readable error responses — never raw
  exception messages or stack traces
  (→ See [Section 5](#5-error-handling))
- **MUST** use appropriate HTTP status codes — a `200 OK` with an error in
  the body is an anti-pattern
- **MUST NOT** return `500 Internal Server Error` for client mistakes — if the
  consumer sent bad data, that is a `4xx`, not a `5xx`

> **Why:** APIs that return vague errors ("Something went wrong") or wrong
> status codes (200 for errors) force consumers into guesswork and defensive
> coding. Clear errors reduce support requests and debugging time.
> → See [01-core-principles.md, Section 2.3 — Fail Fast, Fail Loud].
> → See [07-security-standards.md, Section 1 — Fail Secure].

### 1.7 Design for Evolution

APIs change. New fields are added, behaviors are refined, consumers grow.
A well-designed API can evolve without breaking existing consumers.

- **SHOULD** design responses with extension in mind — adding new fields to a
  response is a non-breaking change; removing or renaming fields is breaking
- **SHOULD** accept unknown fields gracefully in requests (ignore, do not
  reject) unless strict validation is a security requirement
- **MUST** plan for versioning from the start, even if v1 is the only version
  for months (→ See [Section 8](#8-versioning-strategy))
- **SHOULD** document what constitutes a breaking vs non-breaking change for
  the team

> **Why:** APIs that cannot evolve without breaking consumers accumulate
> technical debt and force "big bang" migrations. Designing for evolution
> is cheaper upfront than retrofitting later.

---

## 2. URL & Resource Design

URLs are the most visible part of an API. A well-designed URL is self-documenting
— a developer reading it for the first time should understand what resource it
refers to without checking the documentation.

### 2.1 Base URL Structure

- **MUST** prefix all API routes with `/api/` to separate them from page routes
  and static assets:

  ```
  /api/users
  /api/orders/:id
  /api/invoices/:id/line-items
  ```

- **SHOULD** include a version segment when the API is consumed by external
  clients or multiple independent consumers
  (→ See [Section 8](#8-versioning-strategy)):

  ```
  /api/v1/users
  /api/v1/orders/:id
  ```

- **MAY** omit the version segment for internal APIs within a full-stack Next.js
  application where frontend and backend deploy together — the shared TypeScript
  types and Zod schemas serve as the contract

### 2.2 Resource Naming Rules

- **MUST** use **plural nouns** for collection resources:

  ```
  # BAD — singular, inconsistent
  GET /api/user
  GET /api/order/:id

  # GOOD — plural, predictable
  GET /api/users
  GET /api/orders/:id
  ```

- **MUST** use **kebab-case** for multi-word resource names:

  ```
  # BAD — camelCase, snake_case, or concatenated
  GET /api/lineItems
  GET /api/line_items
  GET /api/lineitems

  # GOOD — kebab-case
  GET /api/line-items
  GET /api/service-appointments
  ```

- **MUST** use **nouns**, not **verbs** — the HTTP method is the verb:

  ```
  # BAD — verb in URL
  POST /api/users/create
  GET  /api/orders/getAll
  POST /api/invoices/delete/:id

  # GOOD — resource noun + HTTP method
  POST   /api/users
  GET    /api/orders
  DELETE /api/invoices/:id
  ```

- **MUST** use **lowercase** only — URLs are case-sensitive in most servers,
  and mixed case creates ambiguity

- **SHOULD** use domain language that consumers understand, not internal
  database table names or abbreviations:

  ```
  # BAD — internal naming leaked
  GET /api/tbl-usr
  GET /api/svc-appt

  # GOOD — domain language
  GET /api/users
  GET /api/service-appointments
  ```

> **Note:** These naming rules apply to **API endpoints** — URLs consumed by
> code, not by end users or search engines. API URLs are part of the codebase
> and follow the English-only rule (→ See [01-core-principles.md, Section 8.1]).
> User-facing page URLs (SEO, navigation) follow different rules and may use
> the target market's language — → See [05-frontend-standards.md] for
> page URL conventions.

### 2.3 Resource Hierarchy & Nesting

Nesting expresses a **parent-child ownership** relationship: a line item
belongs to an invoice, a comment belongs to a post.

- **MUST** limit nesting to a maximum of **2 levels** — deeper nesting creates
  brittle, hard-to-read URLs:

  ```
  # GOOD — 1 level of nesting (item belongs to order)
  GET /api/orders/:orderId/items
  GET /api/orders/:orderId/items/:itemId

  # BAD — 3+ levels (unreadable, fragile)
  GET /api/users/:userId/orders/:orderId/items/:itemId/reviews
  ```

- **SHOULD** flatten deep hierarchies by promoting sub-resources to top-level
  when they have independent identity:

  ```
  # Instead of deeply nested:
  GET /api/users/:userId/orders/:orderId/items/:itemId

  # Flatten — items have their own identity:
  GET /api/order-items/:itemId

  # Or use query parameters to filter:
  GET /api/order-items?orderId=abc123
  ```

- **SHOULD** nest only when the child resource **cannot exist** without the
  parent — if the child has independent identity or is queried across parents,
  promote it to top-level

#### Decision Guide: Nest or Flatten?

```text
Does the child resource make sense without the parent?
 ├── YES → Top-level resource (e.g., /api/products)
 └── NO  → Does the consumer ever need to query across parents?
           ├── YES → Top-level with filter (e.g., /api/comments?postId=x)
           └── NO  → Nested (e.g., /api/orders/:id/items)
```

### 2.4 Resource Identifiers

- **SHOULD** use **UUIDs or NanoIDs** as public-facing resource identifiers —
  sequential integers expose resource count and are trivially enumerable:

  ```
  # ACCEPTABLE (internal tools, admin panels)
  GET /api/users/42

  # PREFERRED (public APIs, client-facing)
  GET /api/users/f47ac10b-58cc-4372-a567-0e02b2c3d479
  GET /api/users/V1StGXR8_Z5jdHi6B-myT
  ```

- **MAY** use sequential integers for internal-only resources or admin
  endpoints where enumeration risk is acceptable
- **MUST NOT** expose database-internal composite keys or technical
  identifiers in URLs (e.g., `/api/users/tenant_1_user_42`)

> → See [07-security-standards.md, Section 6 — API Endpoint Hardening]
> for the security rationale behind non-sequential identifiers.

### 2.5 Query Parameters

Query parameters are for **optional modifiers** that do not identify the
resource — filtering, sorting, pagination, field selection.

- **MUST** use **camelCase** for query parameter names (consistent with JSON
  response fields):

  ```
  # BAD — mixed conventions
  GET /api/orders?page_size=20&sort-by=created_at

  # GOOD — camelCase throughout
  GET /api/orders?pageSize=20&sortBy=createdAt
  ```

- **MUST** validate all query parameters with Zod — unvalidated query params
  are an injection vector
  (→ See [Section 6](#6-input-validation),
  → See [07-security-standards.md, Section 3])

- **SHOULD** use consistent parameter names across all endpoints:

  | Purpose       | Parameter Name                 | Example                            |
  |---------------|--------------------------------|------------------------------------|
  | Pagination    | `page`, `pageSize` or `cursor` | `?page=2&pageSize=20`              |
  | Sorting       | `sortBy`, `sortOrder`          | `?sortBy=createdAt&sortOrder=desc` |
  | Filtering     | Field name directly            | `?status=active&role=admin`        |
  | Searching     | `search` or `q`                | `?search=john`                     |
  | Field selection | `fields`                     | `?fields=id,name,email`            |

- **MUST NOT** use query parameters for actions or state mutations:

  ```
  # BAD — mutation via query parameter
  GET /api/orders/:id?action=cancel

  # GOOD — use the appropriate HTTP method
  POST /api/orders/:id/cancel
  ```

  > **Note:** The `cancel` example is one of the rare cases where an
  > **action sub-resource** is acceptable — when the operation does not map
  > cleanly to a standard CRUD method on the resource itself.
  > Other examples: `POST /api/orders/:id/refund`,
  > `POST /api/users/:id/deactivate`.

### 2.6 URL Anti-Patterns

| Anti-Pattern | Example | Why It Is Wrong | Correct Alternative |
|--------------|---------|-----------------|---------------------|
| Verbs in URL | `POST /api/createUser` | HTTP method is the verb | `POST /api/users` |
| Singular nouns | `GET /api/user/:id` | Inconsistent with collection | `GET /api/users/:id` |
| File extensions | `GET /api/users.json` | Content negotiation via headers | `GET /api/users` with `Accept: application/json` |
| Trailing slashes | `GET /api/users/` | Ambiguous, causes redirect issues | `GET /api/users` |
| Mixed case | `GET /api/userOrders` | Case-sensitive, easy to mistype | `GET /api/user-orders` |
| Deep nesting | `GET /api/a/:id/b/:id/c/:id/d` | Unreadable, fragile | Flatten or use query params |
| IDs in body for GET | `GET /api/users` with `{"id": "x"}` | GET has no body semantics | `GET /api/users/:id` |
| Encoded slashes | `GET /api/users%2F42` | Breaks routing, confuses proxies | Use path segments properly |

---

## 3. HTTP Methods & Status Codes

HTTP methods and status codes are not arbitrary choices — they carry semantic
meaning that clients, browsers, proxies, caches, and monitoring tools rely on.
Using them correctly makes the API predictable and enables the HTTP ecosystem
to work in your favor.

### 3.1 HTTP Methods

Each HTTP method has a defined semantic. Using the wrong method does not just
violate convention — it breaks caching, confuses monitoring, and can introduce
security vulnerabilities.

| Method | Purpose | Request Body | Idempotent | Safe | Cacheable |
|--------|---------|-------------|------------|------|-----------|
| `GET` | Retrieve a resource or collection | No | Yes | Yes | Yes |
| `POST` | Create a new resource or trigger an action | Yes | **No** | No | No |
| `PUT` | Replace a resource entirely | Yes | Yes | No | No |
| `PATCH` | Partially update a resource | Yes | Yes* | No | No |
| `DELETE` | Remove a resource | Optional | Yes | No | No |

> \* `PATCH` is idempotent when applied as a **merge** (set field X to value Y).
> It is NOT idempotent when applied as a **delta** (increment field X by 1).
> **SHOULD** prefer merge semantics for simplicity.

#### Rules

- **MUST** use `GET` for read operations — never use `POST` to retrieve data
  (exception: complex search with large filter payloads that exceed URL length
  limits — in that case, `POST /api/resources/search` is acceptable)

- **MUST** use `POST` for creating new resources where the server assigns the
  identifier

- **SHOULD** use `PUT` only for **full replacement** — the client sends the
  complete resource representation. If the client sends a partial object,
  use `PATCH` instead:

  ```ts
  // PUT — full replacement (client sends ALL fields)
  PUT /api/users/:id
  {
    "name": "João Silva",
    "email": "joao@example.com",
    "role": "admin",
    "phone": "+351912345678"
  }

  // PATCH — partial update (client sends ONLY changed fields)
  PATCH /api/users/:id
  {
    "phone": "+351987654321"
  }
  ```

- **SHOULD** prefer `PATCH` over `PUT` for most update operations — in
  practice, full replacement is rare and error-prone (client must know all
  fields)

- **MUST** make `DELETE` operations idempotent — deleting an already-deleted
  resource returns `204` (or `404`), never an error:

  ```ts
  // First call — resource exists, deleted successfully
  DELETE /api/orders/abc-123  →  204 No Content

  // Second call — resource already gone, still succeeds
  DELETE /api/orders/abc-123  →  204 No Content (or 404)
  ```

  > **Note:** Both `204` and `404` on repeated DELETE are valid conventions.
  > `204` emphasizes idempotency (the end state is the same). `404` emphasizes
  > accuracy (the resource no longer exists). Pick one and be **consistent**
  > across the API. This document recommends `204` as the default.

- **MUST NOT** use `GET` for operations that change state — GET requests can
  be retried by browsers, prefetched by crawlers, and cached by proxies

### 3.2 Idempotency

Idempotency means performing the same operation multiple times produces the
same result as performing it once. This is critical for reliability — network
failures, retries, and duplicate requests are inevitable in distributed systems.

- **MUST** ensure `GET`, `PUT`, `DELETE` are idempotent by design
- **SHOULD** implement idempotency for `POST` operations that create resources
  or trigger side effects (payments, emails, notifications) using an
  **idempotency key**:

  ```ts
  // Client sends a unique key with the request
  POST /api/payments
  Headers:
    Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000

  // Server checks if this key was already processed
  // If yes → return the original response (no duplicate charge)
  // If no  → process and store the key with the response
  ```

- **SHOULD** store idempotency keys with a TTL (e.g., 24–72 hours) — they
  do not need to persist forever
- **SHOULD** return the **original response** (same status code, same body)
  when a duplicate idempotency key is received

> **Why:** Without idempotency, a network timeout on a payment request leaves
> the client unsure: "did the payment go through?" If they retry, they risk
> double-charging. Idempotency keys eliminate this ambiguity.

### 3.3 Status Codes

Status codes communicate the **outcome** of an operation. They are grouped by
class, and each has a specific meaning.

#### Success Codes (2xx)

| Code | Name | When to Use |
|------|------|-------------|
| `200` | OK | Successful `GET`, `PATCH`, `PUT`, or `POST` that returns data |
| `201` | Created | Successful `POST` that creates a new resource — **SHOULD** include `Location` header with the new resource URL |
| `204` | No Content | Successful `DELETE` or an update that returns no body |

- **MUST** use `201` (not `200`) when a `POST` creates a new resource
- **SHOULD** return the created resource in the response body of a `201`
- **MUST** use `204` only when the response intentionally has no body — if
  using the standard response envelope, prefer `200` with an empty `data`

#### Client Error Codes (4xx)

| Code | Name | When to Use |
|------|------|-------------|
| `400` | Bad Request | Malformed request: invalid JSON, missing required fields, type mismatches |
| `401` | Unauthorized | Missing or invalid authentication — the client is not identified |
| `403` | Forbidden | Authenticated but not authorized — the client is identified but lacks permission |
| `404` | Not Found | Resource does not exist — **also** use when the client should not know the resource exists (→ See [07-security-standards.md, Section 6]) |
| `409` | Conflict | State conflict: duplicate unique value, concurrent modification, invalid state transition |
| `422` | Unprocessable Entity | Structurally valid request but semantically invalid (business rule violation) |
| `429` | Too Many Requests | Rate limit exceeded — **MUST** include `Retry-After` header |

##### When to Use 400 vs 422

This is one of the most debated distinctions in API design. This standard
draws a clear line:

```text
Can the request be parsed and its structure understood?
 ├── NO  → 400 Bad Request
 │         (malformed JSON, wrong Content-Type, missing required field,
 │          type mismatch — Zod structural validation failures)
 └── YES → Is the data valid according to business rules?
           ├── NO  → 422 Unprocessable Entity
           │         (email already taken, insufficient balance,
           │          appointment in the past, order in wrong state)
           └── YES → Process the request
```

- **SHOULD** use `400` for **structural** validation failures (Zod `.parse()`
  rejects the shape)
- **SHOULD** use `422` for **semantic/business** validation failures (shape
  is correct but business rules reject it)
- **MAY** use `400` for both if the team prefers simplicity — document the
  decision in an ADR

##### When to Use 401 vs 403

```text
Does the server know who the caller is?
 ├── NO  → 401 Unauthorized (misleading name — it means "unauthenticated")
 │         Action: client should authenticate (login, refresh token)
 └── YES → Does the caller have permission for this action?
           ├── NO  → 403 Forbidden
           │         Action: client should NOT retry (they lack permission)
           └── YES → Process the request
```

##### When to Use 404 as a Security Control

- **SHOULD** return `404` (not `403`) for resources the caller should not know
  exist — `403` confirms existence, `404` reveals nothing:

  ```ts
  // User A tries to access User B's private order
  // BAD — confirms the order exists
  GET /api/orders/xyz-789  →  403 Forbidden

  // GOOD — reveals nothing about the order's existence
  GET /api/orders/xyz-789  →  404 Not Found
  ```

> → See [07-security-standards.md, Section 6 — API Endpoint Hardening]

#### Server Error Codes (5xx)

| Code | Name | When to Use |
|------|------|-------------|
| `500` | Internal Server Error | Unexpected, unhandled error — something the developer did not anticipate |
| `502` | Bad Gateway | Upstream service (database, external API) returned an invalid response |
| `503` | Service Unavailable | Service is temporarily down (maintenance, overload) — **SHOULD** include `Retry-After` header |
| `504` | Gateway Timeout | Upstream service did not respond in time |

- **MUST** log the full error details server-side for every `5xx` response
  (→ See [08-observability.md])
- **MUST NOT** expose internal error details (stack traces, SQL errors, file
  paths) in `5xx` responses to the client
  (→ See [07-security-standards.md, Section 1 — Fail Secure])
- **MUST** return a generic, safe error message to the client for all `5xx`
  errors:

  ```json
  {
    "ok": false,
    "error": {
      "code": "INTERNAL_ERROR",
      "message": "An unexpected error occurred. Please try again later."
    },
    "requestId": "req_abc123"
  }
  ```

### 3.4 Method + Status Code Quick Reference

A fast-lookup table mapping each operation to its expected outcomes:

| Operation | Method | Success | Common Errors |
|-----------|--------|---------|---------------|
| List resources | `GET` | `200` | `401`, `403`, `429` |
| Get single resource | `GET` | `200` | `401`, `403`, `404`, `429` |
| Create resource | `POST` | `201` | `400`, `401`, `403`, `409`, `422`, `429` |
| Full update | `PUT` | `200` | `400`, `401`, `403`, `404`, `409`, `422` |
| Partial update | `PATCH` | `200` | `400`, `401`, `403`, `404`, `409`, `422` |
| Delete resource | `DELETE` | `204` | `401`, `403`, `404` |
| Action / trigger | `POST` | `200` or `202` | `400`, `401`, `403`, `409`, `422`, `429` |

---

## 4. Request & Response Format

A consistent request and response format is the backbone of a predictable API.
When every endpoint speaks the same "language" — same envelope, same field
names, same date format — consumers can build generic HTTP clients, error
handlers, and data parsers that work across the entire API without
endpoint-specific logic.

### 4.1 Content Type

- **MUST** use `application/json` as the default content type for both
  requests and responses
- **MUST** set the `Content-Type: application/json` header on all JSON
  responses
- **MUST** reject requests with unexpected `Content-Type` headers on
  endpoints that expect JSON — return `415 Unsupported Media Type`
- **MAY** support additional content types (e.g., `multipart/form-data`
  for file uploads) on specific endpoints — document them explicitly

### 4.2 JSON Conventions

These rules ensure that JSON payloads are consistent and interoperable
across the entire API surface.

- **MUST** use **camelCase** for all JSON field names — this aligns with
  JavaScript/TypeScript conventions and avoids transformation at the
  frontend boundary:

  ```json
  {
    "firstName": "João",
    "lastName": "Silva",
    "createdAt": "2025-03-15T10:30:00.000Z",
    "isActive": true
  }
  ```

- **MUST** use **ISO 8601** format for all dates and timestamps, always
  in **UTC** (with the `Z` suffix):

  ```
  // BAD — ambiguous, locale-dependent, no timezone
  "date": "15/03/2025"
  "date": "March 15, 2025"
  "date": "2025-03-15 10:30:00"

  // GOOD — ISO 8601, UTC, unambiguous
  "createdAt": "2025-03-15T10:30:00.000Z"
  "updatedAt": "2025-03-15T14:22:33.456Z"
  ```

  > **Why:** ISO 8601 in UTC eliminates timezone ambiguity. The frontend
  > is responsible for converting to the user's local timezone for display.
  > Storing and transmitting in UTC is a universal best practice that
  > prevents an entire class of timezone-related bugs.

- **MUST** represent `null` explicitly when a field has no value — do not
  omit the field, as omission is ambiguous (missing vs intentionally empty):

  ```json
  {
    "phone": null,
    "address": null
  }
  ```

  > **Note:** This rule applies to **responses**. In **requests** (e.g.,
  > PATCH), omitting a field means "do not change this field," which is
  > the correct semantic for partial updates.

- **MUST** use **numbers** for numeric values — never strings:

  ```json
  // BAD — string that must be parsed
  { "price": "29.99", "quantity": "3" }

  // GOOD — native JSON numbers
  { "price": 29.99, "quantity": 3 }
  ```

  > **Exception:** Use strings for values that exceed JavaScript's safe
  > integer range (`Number.MAX_SAFE_INTEGER`, ~9 quadrillion) or that
  > require exact decimal precision (monetary values in some systems).
  > In that case, document the convention explicitly.

- **MUST** use **boolean** for true/false values — never strings or integers:

  ```json
  // BAD — stringly-typed
  { "isActive": "true", "isVerified": 1 }

  // GOOD — native JSON booleans
  { "isActive": true, "isVerified": false }
  ```

- **SHOULD** use **arrays** (even if empty) for collections — never `null`
  for an empty collection:

  ```json
  // BAD — consumer must check null vs array
  { "tags": null }

  // GOOD — empty array, consumer can always .map()
  { "tags": [] }
  ```

### 4.3 Standard Response Envelope

Every API response — success or error — **MUST** follow the same envelope
structure. This allows consumers to build a single response handler that
works for all endpoints.

#### Success Response

```ts
// TypeScript type definition
type ApiSuccessResponse<T> = {
  ok: true;
  data: T;
  meta?: PaginationMeta;
  requestId: string;
};
```

```json
// Example: GET /api/users/f47ac10b
{
  "ok": true,
  "data": {
    "id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
    "name": "João Silva",
    "email": "joao@example.com",
    "role": "admin",
    "createdAt": "2025-01-10T08:00:00.000Z"
  },
  "requestId": "req_abc123def456"
}
```

```json
// Example: GET /api/users (collection with pagination)
{
  "ok": true,
  "data": [
    { "id": "f47ac10b", "name": "João Silva", "email": "joao@example.com" },
    { "id": "a1b2c3d4", "name": "Maria Santos", "email": "maria@example.com" }
  ],
  "meta": {
    "page": 1,
    "pageSize": 20,
    "totalItems": 142,
    "totalPages": 8
  },
  "requestId": "req_xyz789ghi012"
}
```

#### Error Response

```ts
// TypeScript type definition
type ApiErrorResponse = {
  ok: false;
  error: {
    code: string;
    message: string;
    details?: unknown;
    fieldErrors?: Record<string, string[]>;
  };
  requestId: string;
};
```

```json
// Example: 400 Bad Request (validation failure)
{
  "ok": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "fieldErrors": {
      "email": ["Invalid email format"],
      "name": ["Name is required", "Name must be at least 2 characters"]
    }
  },
  "requestId": "req_err456def789"
}
```

```json
// Example: 404 Not Found
{
  "ok": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "User not found"
  },
  "requestId": "req_err789ghi012"
}
```

```json
// Example: 409 Conflict
{
  "ok": false,
  "error": {
    "code": "CONFLICT",
    "message": "A user with this email already exists"
  },
  "requestId": "req_err012jkl345"
}
```

#### Envelope Rules

- **MUST** include the `ok` field (boolean discriminator) in every response
  — it allows consumers to check success/failure without inspecting status
  codes:

  ```ts
  // Consumer-side pattern
  const response = await fetch('/api/users');
  const result = await response.json();

  if (result.ok) {
    // TypeScript narrows to ApiSuccessResponse
    renderUsers(result.data);
  } else {
    // TypeScript narrows to ApiErrorResponse
    showError(result.error.message);
  }
  ```

- **MUST** include `requestId` in every response (success and error) for
  traceability — this is the correlation ID that links a client request to
  server logs (→ See [Section 4.4](#44-request-id--traceability))
- **MUST** include the `data` field in success responses — even for empty
  results, use `"data": null` (single resource not found in a search) or
  `"data": []` (empty collection)
- **MUST** include the `error` object in error responses with at least
  `code` (stable, machine-readable) and `message` (human-readable)
- **SHOULD** include `fieldErrors` in validation error responses (`400`,
  `422`) to enable per-field error display in forms
- **MAY** include `meta` in collection responses for pagination information
  (→ See [Section 7](#7-pagination-filtering--sorting))
- **MUST NOT** include `data` and `error` in the same response — a response
  is either a success or an error, never both

#### Why Not Use HTTP Status Codes Alone?

HTTP status codes are essential (→ See [Section 3.3](#33-status-codes)), but
they are not sufficient:

- Status codes are **coarse** — `400` does not tell the consumer which field
  failed validation
- Status codes are **limited** — there is no standard code for "email already
  taken" vs "username already taken" (both are `409`)
- Status codes are **not always accessible** — some HTTP clients or proxies
  make it awkward to read the status code separately from the body
- The `ok` boolean **duplicates** the status code class intentionally — it
  provides an in-body discriminator that works even when the transport layer
  obscures the status code

### 4.4 Request ID & Traceability

Every request that enters the API **MUST** be assigned a unique identifier
that follows it through all layers — from the route handler to the service,
to the database query, to the log entry, and back to the client in the
response.

- **MUST** generate a unique `requestId` for every incoming request (UUID
  v4 or a prefixed NanoID like `req_V1StGXR8_Z5jdHi6B`):

  ```ts
  // Middleware / utility
  import { nanoid } from 'nanoid';

  export function generateRequestId(): string {
    return `req_${nanoid(21)}`;
  }
  ```

- **MUST** include the `requestId` in every response (success and error)
- **MUST** include the `requestId` in every log entry produced during
  request processing — this allows correlating a client error report
  ("I got requestId req_abc123") with the full server-side trace
- **SHOULD** accept an incoming `X-Request-ID` header from the client
  and use it as the `requestId` if present (useful for distributed
  tracing) — if the header is missing, generate a new one
- **SHOULD** propagate the `requestId` to downstream service calls
  (external APIs, background jobs) for end-to-end tracing
- **MUST NOT** use `requestId` for authentication, authorization, or
  any security-sensitive purpose — it is purely a diagnostic tool

  ```ts
  // Example: Request ID middleware for Express
  import { nanoid } from 'nanoid';
  import { Request, Response, NextFunction } from 'express';

  export function requestIdMiddleware(
    req: Request,
    _res: Response,
    next: NextFunction
  ): void {
    const requestId =
      (req.headers['x-request-id'] as string) || `req_${nanoid(21)}`;

    req.requestId = requestId;
    next();
  }
  ```

  ```ts
  // Example: Request ID in Next.js Route Handler
  import { nanoid } from 'nanoid';
  import { NextRequest, NextResponse } from 'next/server';

  export async function GET(request: NextRequest) {
    const requestId =
      request.headers.get('x-request-id') || `req_${nanoid(21)}`;

    // ... service call with requestId for logging

    return NextResponse.json(
      { ok: true, data: result, requestId },
      { status: 200 }
    );
  }
  ```

> **Why:** When a user reports "something went wrong," the `requestId` is
> the key that unlocks the entire server-side story — what happened, in
> what order, and where it failed. Without it, debugging production issues
> becomes guesswork.
> → See [08-observability.md] for logging and monitoring standards that
> build on the requestId pattern.

---

### 4.5 Streaming Responses (SSE)

Most endpoints return a single response in the standard envelope (§4.3). When output is produced
incrementally and waiting for the whole thing hurts UX — token-by-token AI output, long exports,
progress on a long task — the endpoint **MAY** stream instead. Streaming is an *exception* to the
single-envelope rule, with its own contract. *What* to stream in an AI pipeline → See
[12-ai-engineering.md, §2.3]; UI consumption → See [05-frontend-standards.md].

**Rules:**

- Stream only on a real incremental-output need; a request that completes in one step **MUST** use
  the standard envelope (§4.3), not a stream.
- Use **Server-Sent Events** (`Content-Type: text/event-stream`) for unidirectional server→client
  streams. **MUST NOT** reach for WebSockets for response streaming — they are bidirectional and add
  connection complexity a one-way token stream does not need.
- Each event **MUST** carry a typed shape so the client can dispatch — a `type` discriminator
  (`token` / `error` / `done`) plus its payload — mirroring the discriminated-union discipline of
  the envelope.
- **Error semantics depend on whether bytes have been sent:**
  - Error **before the first byte** → behave normally: proper HTTP status + standard error envelope
    (§5). The stream never starts.
  - Error **after streaming has started** → the status is already `200`; you **MUST NOT** try to
    change it. Emit an in-stream **error event** (`type: "error"`, same `code` / `message` as the
    envelope error, §5.3), then close the stream.
- The stream **MUST** end with an explicit **terminal event** (`type: "done"`) so the client can
  tell clean completion from a dropped connection. Final metadata (token usage, trace id) rides on
  that terminal event.
- The server **MUST** detect client disconnect and cancel upstream work (abort the model call, close
  cursors) — an abandoned stream that keeps generating burns cost and leaks resources.
- Streams **MUST** be bounded: a max-output / token cap, a hard timeout, and a per-user
  concurrent-stream limit — an unbounded stream is a DoS vector. → See §10; [07-security-standards.md, §6].
- Clients **SHOULD** be able to fall back to a non-streaming variant when a proxy / CDN buffers or
  breaks SSE.

**Why:**

Streaming exists for one reason: perceived latency — a 15-second answer feels broken behind a
spinner but fast when tokens appear immediately. But it breaks two assumptions baked into the rest
of this document: the single response envelope, and "the status code describes the outcome". The
moment the first byte ships, the status is locked at `200`, so a failure halfway can only be
reported *inside* the stream — an endpoint that omits an error event leaves the client unable to
tell "finished" from "died mid-sentence", which the terminal event resolves. The boundedness rules
are not polish: a model loop with no token cap, no timeout, and no concurrency limit is a cheap,
direct denial-of-service.

**GOOD — typed SSE with terminal + in-stream error events (Next.js Route Handler):**

```ts
export async function POST(req: Request) {
  // Pre-stream failures use the normal envelope + status (§5) — the stream has not started.
  const input = ChatInput.parse(await req.json());            // throws → mapped to 422 envelope
  await authorize(/* ... */);                                 // throws → 401/403 envelope

  const stream = new ReadableStream({
    async start(controller) {
      const send = (e: { type: "token" | "error" | "done"; [k: string]: unknown }) =>
        controller.enqueue(`data: ${JSON.stringify(e)}\n\n`);
      try {
        for await (const token of model.stream(input, { signal: req.signal })) { // honor disconnect
          send({ type: "token", text: token });
        }
        send({ type: "done", usage: model.usage, traceId });   // terminal event + final metadata
      } catch (err) {
        // Status is already 200 — report the failure as an in-stream event, not an HTTP status.
        send({ type: "error", code: toErrorCode(err), message: safeMessage(err) }); // → §5.3
      } finally {
        controller.close();
      }
    },
  });

  return new Response(stream, {
    headers: { "Content-Type": "text/event-stream", "Cache-Control": "no-cache" },
  });
}
```

> `model.stream`, `toErrorCode`, `safeMessage`, `traceId` are pattern placeholders. Transport and
> event shape are this document's; *what* to stream → See [12-ai-engineering.md, §2.3]; UI rendering
> → See [05-frontend-standards.md]; time-to-first-token / token-cost metrics → See
> [08-observability.md]. Prefer an SDK's streaming helpers (→ [02-technology-radar.md, §3.26]) over a
> hand-rolled parser.

---

## 5. Error Handling

Error handling in APIs is not an afterthought — it is a **design decision**
that directly impacts the consumer experience. A well-designed error system
tells the consumer exactly what went wrong, why, and what they can do about
it — consistently, across every endpoint.

This section defines the implementation patterns. For the underlying
philosophy, → See [01-core-principles.md, Section 3.4 — Error Handling
Discipline]. For the security perspective,
→ See [07-security-standards.md, Section 1 — Fail Secure].

### 5.1 Error Response Structure

Every error response **MUST** follow the envelope defined in
[Section 4.3](#43-standard-response-envelope):

```json
{
  "ok": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description",
    "details": {},
    "fieldErrors": {}
  },
  "requestId": "req_abc123"
}
```

| Field | Required | Purpose |
|-------|----------|---------|
| `code` | **MUST** | Stable, machine-readable identifier. Consumers use this for programmatic handling (`if (error.code === 'NOT_FOUND')`). **MUST** never change once published. |
| `message` | **MUST** | Human-readable description safe to display to end users. **MUST NOT** contain stack traces, SQL errors, file paths, or internal details. |
| `details` | **MAY** | Additional context for debugging (e.g., which constraint was violated). **MUST** be reviewed for information leakage before including. |
| `fieldErrors` | **SHOULD** for `400`/`422` | Per-field validation errors as `Record<string, string[]>`. Enables forms to display errors next to the relevant input. |

### 5.2 AppError Class Hierarchy

A custom error class hierarchy provides type-safe, consistent error handling
across the entire application. Every expected error thrown in the service
layer should be an instance of `AppError` or one of its subclasses.

```ts
// src/errors/app-error.ts

export class AppError extends Error {
  constructor(
    public readonly code: string,
    message: string,
    public readonly statusCode: number = 500,
    public readonly details?: unknown
  ) {
    super(message);
    this.name = 'AppError';

    // Maintains proper prototype chain in TypeScript
    Object.setPrototypeOf(this, new.target.prototype);
  }
}
```

#### Standard Subclasses

Each subclass maps to a specific HTTP status code and error category.
This is the **recommended baseline** — extend it as the project grows.

```ts
// src/errors/index.ts

export class ValidationError extends AppError {
  constructor(
    message: string,
    public readonly fieldErrors?: Record<string, string[]>
  ) {
    super('VALIDATION_ERROR', message, 400, fieldErrors);
    this.name = 'ValidationError';
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string, identifier?: string) {
    const message = identifier
      ? `${resource} with ID ${identifier} not found`
      : `${resource} not found`;
    super('NOT_FOUND', message, 404);
    this.name = 'NotFoundError';
  }
}

export class UnauthorizedError extends AppError {
  constructor(message: string = 'Authentication required') {
    super('UNAUTHORIZED', message, 401);
    this.name = 'UnauthorizedError';
  }
}

export class ForbiddenError extends AppError {
  constructor(message: string = 'Insufficient permissions') {
    super('FORBIDDEN', message, 403);
    this.name = 'ForbiddenError';
  }
}

export class ConflictError extends AppError {
  constructor(message: string) {
    super('CONFLICT', message, 409);
    this.name = 'ConflictError';
  }
}

export class BusinessRuleError extends AppError {
  constructor(code: string, message: string) {
    super(code, message, 422);
    this.name = 'BusinessRuleError';
  }
}

export class RateLimitError extends AppError {
  constructor(retryAfterSeconds?: number) {
    super(
      'RATE_LIMITED',
      'Too many requests. Please try again later.',
      429,
      retryAfterSeconds ? { retryAfter: retryAfterSeconds } : undefined
    );
    this.name = 'RateLimitError';
  }
}
```

#### Rules

- **MUST** use `AppError` subclasses for all expected errors in the service
  layer — never throw generic `new Error()` for known failure modes
- **MUST** include a stable `code` property on every error — consumers
  depend on codes for programmatic handling, not on message strings
  (→ See [01-core-principles.md, Section 3.4])
- **MUST** keep the `message` safe for end-user display — no internal
  details, no database error strings
- **SHOULD** use `BusinessRuleError` for domain-specific failures that
  do not fit the standard HTTP error categories:

  ```ts
  // Domain-specific business rules
  throw new BusinessRuleError(
    'INSUFFICIENT_BALANCE',
    'Account balance is insufficient for this transaction'
  );

  throw new BusinessRuleError(
    'APPOINTMENT_IN_PAST',
    'Cannot schedule an appointment in the past'
  );

  throw new BusinessRuleError(
    'ORDER_NOT_CANCELLABLE',
    'Orders in "shipped" status cannot be cancelled'
  );
  ```

- **SHOULD** add new subclasses only when a genuinely different error
  **category** emerges — avoid creating a subclass per error code. The
  `BusinessRuleError` with different `code` values handles most
  domain-specific cases

### 5.3 Error Codes Catalogue

Error codes are the **stable contract** between the API and its consumers.
Unlike messages (which may be translated or rephrased), codes are permanent
and machine-readable.

#### Naming Convention

- **MUST** use `UPPER_SNAKE_CASE` for all error codes
- **MUST** use a descriptive, self-explanatory name — the code alone should
  communicate the problem category
- **SHOULD** use a consistent prefix pattern for domain-specific codes:

  ```
  // Standard codes (no prefix needed)
  VALIDATION_ERROR
  NOT_FOUND
  UNAUTHORIZED
  FORBIDDEN
  CONFLICT
  RATE_LIMITED
  INTERNAL_ERROR

  // Domain-specific codes (descriptive, self-explanatory)
  INSUFFICIENT_BALANCE
  APPOINTMENT_IN_PAST
  ORDER_NOT_CANCELLABLE
  EMAIL_ALREADY_REGISTERED
  VEHICLE_NOT_AVAILABLE
  PAYMENT_DECLINED
  INVOICE_ALREADY_PAID
  ```

#### Standard Error Codes Reference

These are the baseline codes that every project **SHOULD** implement from
the start:

| Code | Status | Thrown By | Meaning |
|------|--------|-----------|---------|
| `VALIDATION_ERROR` | `400` | `ValidationError` | Request failed structural validation (Zod) |
| `UNAUTHORIZED` | `401` | `UnauthorizedError` | Missing or invalid authentication |
| `FORBIDDEN` | `403` | `ForbiddenError` | Authenticated but insufficient permissions |
| `NOT_FOUND` | `404` | `NotFoundError` | Resource does not exist (or caller cannot know it exists) |
| `CONFLICT` | `409` | `ConflictError` | Duplicate value, concurrent modification, state conflict |
| `RATE_LIMITED` | `429` | `RateLimitError` | Too many requests |
| `INTERNAL_ERROR` | `500` | (catch-all) | Unexpected server error — generic safe message |

- **MUST** document all error codes used in the API — consumers need a
  reference to handle each case
- **MUST NOT** change or remove a published error code — it is part of
  the API contract (→ See [Section 8](#8-versioning-strategy))
- **MAY** add new error codes at any time — this is a non-breaking change

### 5.4 Centralized Error-to-Response Mapping

Error mapping **MUST** happen in a single place — not scattered across every
route handler. This ensures consistent error responses and prevents
accidentally leaking internal details.

#### Pattern: Express.js Error Middleware

```ts
// src/middleware/error-handler.ts
import { Request, Response, NextFunction } from 'express';
import { ZodError } from 'zod';
import { AppError, ValidationError } from '../errors';
import { logger } from '../lib/logger';

export function errorHandler(
  error: Error,
  req: Request,
  res: Response,
  _next: NextFunction
): void {
  const requestId = req.requestId;

  // 1. Zod validation errors → structured 400
  if (error instanceof ZodError) {
    const fieldErrors: Record<string, string[]> = {};
    for (const issue of error.issues) {
      const field = issue.path.join('.');
      if (!fieldErrors[field]) fieldErrors[field] = [];
      fieldErrors[field].push(issue.message);
    }

    res.status(400).json({
      ok: false,
      error: {
        code: 'VALIDATION_ERROR',
        message: 'Request validation failed',
        fieldErrors,
      },
      requestId,
    });
    return;
  }

  // 2. Known application errors → mapped response
  if (error instanceof AppError) {
    logger.warn('Application error', {
      code: error.code,
      message: error.message,
      statusCode: error.statusCode,
      requestId,
    });

    res.status(error.statusCode).json({
      ok: false,
      error: {
        code: error.code,
        message: error.message,
        ...(error instanceof ValidationError && error.fieldErrors
          ? { fieldErrors: error.fieldErrors }
          : {}),
        ...(error.details && process.env.NODE_ENV !== 'production'
          ? { details: error.details }
          : {}),
      },
      requestId,
    });
    return;
  }

  // 3. Unexpected errors → generic 500 (never expose internals)
  logger.error('Unhandled error', {
    error: error.message,
    stack: error.stack,
    requestId,
  });

  res.status(500).json({
    ok: false,
    error: {
      code: 'INTERNAL_ERROR',
      message: 'An unexpected error occurred. Please try again later.',
    },
    requestId,
  });
}
```

#### Pattern: Next.js Route Handler

Next.js Route Handlers do not have global error middleware like Express.
The recommended pattern is a **wrapper function** that provides consistent
error handling for every handler:

```ts
// src/lib/api-handler.ts
import { NextRequest, NextResponse } from 'next/server';
import { ZodError } from 'zod';
import { AppError, ValidationError } from '../errors';
import { generateRequestId } from '../lib/request-id';
import { logger } from '../lib/logger';

type RouteHandler = (
  request: NextRequest,
  context: { params: Record<string, string>; requestId: string }
) => Promise<NextResponse>;

export function apiHandler(handler: RouteHandler): (
  request: NextRequest,
  context: { params: Promise<Record<string, string>> }
) => Promise<NextResponse> {
  return async (request, context) => {
    const requestId =
      request.headers.get('x-request-id') || generateRequestId();

    // Next.js 16+: params are async and must be awaited
    const params = await context.params;

    try {
      return await handler(request, { params, requestId });
    } catch (error) {
      // Zod validation errors
      if (error instanceof ZodError) {
        const fieldErrors: Record<string, string[]> = {};
        for (const issue of error.issues) {
          const field = issue.path.join('.');
          if (!fieldErrors[field]) fieldErrors[field] = [];
          fieldErrors[field].push(issue.message);
        }

        return NextResponse.json(
          {
            ok: false,
            error: {
              code: 'VALIDATION_ERROR',
              message: 'Request validation failed',
              fieldErrors,
            },
            requestId,
          },
          { status: 400 }
        );
      }

      // Known application errors
      if (error instanceof AppError) {
        logger.warn('Application error', {
          code: error.code,
          requestId,
        });

        return NextResponse.json(
          {
            ok: false,
            error: {
              code: error.code,
              message: error.message,
              ...(error instanceof ValidationError && error.fieldErrors
                ? { fieldErrors: error.fieldErrors }
                : {}),
            },
            requestId,
          },
          { status: error.statusCode }
        );
      }

      // Unexpected errors
      logger.error('Unhandled error', {
        error: error instanceof Error ? error.message : String(error),
        stack: error instanceof Error ? error.stack : undefined,
        requestId,
      });

      return NextResponse.json(
        {
          ok: false,
          error: {
            code: 'INTERNAL_ERROR',
            message: 'An unexpected error occurred. Please try again later.',
          },
          requestId,
        },
        { status: 500 }
      );
    }
  };
}
```

Usage in a Route Handler:

```ts
// app/api/users/route.ts
import { apiHandler } from '@/lib/api-handler';
import { createUserSchema } from '@/schemas/user';
import { userService } from '@/services/user-service';

export const POST = apiHandler(async (request, { requestId }) => {
  const body = await request.json();
  const parsed = createUserSchema.parse(body);

  const user = await userService.create(parsed);

  return NextResponse.json(
    { ok: true, data: user, requestId },
    { status: 201 }
  );
});
```

#### Rules

- **MUST** centralize error-to-response mapping — route handlers should not
  contain their own try/catch blocks for error formatting
- **MUST** handle three categories in order:
  1. **Validation errors** (ZodError) → structured `400` with `fieldErrors`
  2. **Application errors** (AppError subclasses) → mapped status code + code
  3. **Unexpected errors** (everything else) → generic `500`
- **MUST NOT** expose `error.stack`, `error.details`, or any internal
  information in production error responses
- **SHOULD** log full error details server-side for every error (including
  `requestId` for correlation)
- **SHOULD** use `logger.warn` for expected application errors (4xx) and
  `logger.error` for unexpected errors (5xx) — this enables meaningful
  alerting (→ See [08-observability.md])

### 5.5 Error Handling Anti-Patterns

| Anti-Pattern | Why It Is Wrong | Correct Alternative |
|---|---|---|
| `200 OK` with error in body | Breaks HTTP semantics, confuses clients, caches, proxies | Use appropriate `4xx` / `5xx` status code |
| Raw exception message as response | Leaks internals (SQL errors, file paths, stack traces) | Map to safe `AppError` with generic message |
| Different error formats per endpoint | Consumers cannot build a generic error handler | Use the standard envelope everywhere |
| `catch (e) { /* ignore */ }` | Silent failure — data corruption, debugging nightmare | Handle explicitly or let it propagate to centralized handler |
| Parsing `error.message` for control flow | Fragile — breaks when message changes | Use `error.code` or `instanceof` checks |
| Business logic in error handler | Error handler becomes a god function | Keep error handler pure — map errors to responses only |
| Wrapping every service call in try/catch | Verbose, inconsistent, easy to forget | Let errors propagate to centralized handler |

---

## 6. Input Validation

> **Ownership note:** This section defines input validation from the **API
> design** perspective — schema patterns, Zod usage, and validation
> middleware. For the **security constraints** behind these rules
> (sanitization, file upload validation, defense in depth), the
> authoritative source is → See [07-security-standards.md, §3]. For the
> **universal principle** of fail-fast validation, see
> → See [01-core-principles.md, §2.3].

Every byte of data that enters the API from the outside world is **untrusted**
until validated. Input validation is simultaneously a design concern (ensuring
data integrity and clear error messages) and a security concern (preventing
injection, overflow, and abuse).

This section defines **how** to implement validation in the API layer. For
the security rules that validation must enforce (what to validate, sanitization
rules, context-specific escaping),
→ See [07-security-standards.md, Section 3 — Input Validation & Sanitization].

### 6.1 Core Principle: Validate at the Boundary

The API route handler is the **trust boundary** — the door between the
untrusted outside world and the trusted internals of the application. All
validation happens here, before data reaches the service layer.

```text
Untrusted World                   Trusted Application
─────────────────────────────────────────────────────
                    │
  Client Request ──►│ Route Handler ──► Service ──► Repository
                    │   ▲
                    │   │
                    │   Zod .parse()
                    │   (validation happens HERE)
                    │
```

- **MUST** validate all request data at the route handler level using Zod
  schemas — body, query parameters, path parameters, and relevant headers
- **MUST** use `.parse()` (throws on failure) at the API boundary — the
  centralized error handler (→ See [Section 5.4](#54-centralized-error-to-response-mapping))
  catches the `ZodError` and returns a structured `400`
- **MUST NOT** pass unvalidated data to the service layer — the service
  should be able to trust that its inputs are already valid
- **MUST NOT** rely on client-side validation as a security control —
  client validation is UX only
  (→ See [07-security-standards.md, Section 3])
- **MUST NOT** rely on database constraints as the primary validation —
  they are the last safety net, not the first

> **Why:** Validating at the boundary means the service layer never needs
> to worry about malformed data. This simplifies service code, prevents
> invalid data from propagating, and ensures every rejection produces a
> consistent, structured error response.
> → See [01-core-principles.md, Section 2.3 — Fail Fast, Fail Loud].

### 6.2 Schema Design with Zod

Zod is the **single source of truth** for request validation and TypeScript
type inference (→ See [02-technology-radar.md, Section 4.5 — Zod]).
A well-designed schema is reusable, composable, and self-documenting.

#### Base Schema Pattern

Define a **base schema** per resource, then derive request-specific schemas
from it. This avoids duplication and ensures consistency.

```ts
// src/schemas/user.ts
import { z } from 'zod';

// --- Base field definitions (reusable atoms) ---

// Zod 4: string format validators are promoted to top-level functions
// (z.email(), z.uuidv4(), z.e164(), etc.) — method equivalents on
// z.string() are deprecated but still available during transition.
const email = z
  .email('Invalid email format')
  .max(255, 'Email must not exceed 255 characters')
  .overwrite((val) => val.toLowerCase().trim());

const name = z
  .string()
  .min(2, 'Name must be at least 2 characters')
  .max(100, 'Name must not exceed 100 characters')
  .trim();

// Zod 4: unified error param replaces errorMap
const role = z.enum(['admin', 'manager', 'user'], {
  error: 'Role must be admin, manager, or user',
});

const phone = z
  .string()
  .regex(/^\+?[1-9]\d{1,14}$/, 'Invalid phone number format (E.164)')
  .optional();

// --- Request schemas (composed from base fields) ---

export const createUserSchema = z.object({
  name,
  email,
  role: role.default('user'),
  phone,
});

export const updateUserSchema = z.object({
  name: name.optional(),
  email: email.optional(),
  role: role.optional(),
  phone,
});

// --- Type inference (single source of truth) ---

export type CreateUserInput = z.infer<typeof createUserSchema>;
// → { name: string; email: string; role: "admin" | "manager" | "user"; phone?: string }

export type UpdateUserInput = z.infer<typeof updateUserSchema>;
// → { name?: string; email?: string; role?: "admin" | "manager" | "user"; phone?: string }
```

#### Rules

- **MUST** define one schema file per resource (e.g., `schemas/user.ts`,
  `schemas/order.ts`) — co-locate related schemas
- **MUST** use Zod's type inference (`z.infer<typeof schema>`) as the
  TypeScript type — never define types manually alongside schemas, as they
  will drift apart
- **MUST** include meaningful error messages in schema definitions — Zod 4
  uses a unified `error` parameter (replacing the old `errorMap` / `message`
  split from v3)
- **SHOULD** use `.overwrite()` for normalization transforms that do not
  change the type (e.g., `.trim()`, `.toLowerCase()`) — unlike `.transform()`,
  `.overwrite()` preserves the original schema class, enabling further
  chaining of type-specific methods
- **SHOULD** use Zod 4's top-level format functions (`z.email()`,
  `z.uuidv4()`, `z.e164()`, `z.url()`) instead of the deprecated string
  method equivalents (`z.string().email()`) — the top-level functions are
  more tree-shakable and concise
- **SHOULD** define base fields as reusable constants and compose schemas
  from them — this ensures that the `email` field has the same rules
  whether used in `createUserSchema` or `updateUserSchema`
- **SHOULD** use `.default()` for fields with sensible defaults rather
  than making them optional

### 6.3 Validating Different Input Sources

API input comes from multiple sources, and each must be validated
independently with its own schema.

#### Request Body

```ts
// POST / PUT / PATCH — body validation
export const POST = apiHandler(async (request, { requestId }) => {
  const body = await request.json();
  const parsed = createUserSchema.parse(body);
  // parsed is fully typed and validated
  const user = await userService.create(parsed);
  // ...
});
```

#### Query Parameters

```ts
// GET with filtering and pagination
const listUsersQuerySchema = z.object({
  page: z.coerce.number().int().min(1).default(1),
  pageSize: z.coerce.number().int().min(1).max(100).default(20),
  sortBy: z.enum(['createdAt', 'name', 'email']).default('createdAt'),
  sortOrder: z.enum(['asc', 'desc']).default('desc'),
  role: z.enum(['admin', 'manager', 'user']).optional(),
  search: z.string().max(200).optional(),
});

export const GET = apiHandler(async (request, { requestId }) => {
  const { searchParams } = new URL(request.url);
  const query = listUsersQuerySchema.parse(
    Object.fromEntries(searchParams)
  );
  // query.page is a number (coerced from string)
  // query.pageSize is capped at 100 (abuse prevention)
  const result = await userService.list(query);
  // ...
});
```

> **Note:** Query parameters arrive as strings. Use `z.coerce.number()` and
> `z.coerce.boolean()` to safely convert them — never use `parseInt()` or
> manual parsing.

#### Path Parameters

```ts
// Path parameter validation
const userIdParamSchema = z.object({
  id: z.uuidv4('Invalid user ID format'),
});

export const GET = apiHandler(async (request, { params, requestId }) => {
  const { id } = userIdParamSchema.parse(params);
  const user = await userService.findById(id);
  // ...
});
```

#### Headers (When Relevant)

```ts
// Webhook signature validation (→ See Section 12)
const webhookHeadersSchema = z.object({
  'stripe-signature': z.string().min(1, 'Missing Stripe signature'),
});
```

#### Rules

- **MUST** validate body, query params, and path params independently —
  each has its own schema
- **MUST** use `z.coerce` for query parameters and path parameters that
  should be numbers or booleans — they arrive as strings from the URL
- **MUST** cap `pageSize` and similar parameters with `.max()` to prevent
  abuse (→ See [Section 7](#7-pagination-filtering--sorting),
  → See [07-security-standards.md, Section 6])
- **MUST** limit string lengths with `.max()` to prevent payload abuse
- **SHOULD** validate path parameter format (UUID, NanoID) — reject
  malformed IDs before they reach the database
- **SHOULD** use `z.enum()` for parameters with a fixed set of valid
  values (roles, statuses, sort fields) — this prevents injection and
  provides clear error messages

### 6.4 Validation Middleware Pattern (Express)

For Express applications, validation can be extracted into reusable
middleware that validates a specific input source against a schema.

```ts
// src/middleware/validate.ts
import { Request, Response, NextFunction } from 'express';
import { ZodSchema } from 'zod';

type InputSource = 'body' | 'query' | 'params';

export function validate(schema: ZodSchema, source: InputSource = 'body') {
  return (req: Request, _res: Response, next: NextFunction) => {
    const parsed = schema.parse(req[source]);

    // Replace raw input with validated & transformed data
    req[source] = parsed;
    next();
  };
  // ZodError propagates to the centralized error handler
}
```

Usage in routes:

```ts
// src/routes/user-routes.ts
import { Router } from 'express';
import { validate } from '../middleware/validate';
import { createUserSchema, listUsersQuerySchema } from '../schemas/user';
import { userController } from '../controllers/user-controller';

const router = Router();

router.post(
  '/users',
  validate(createUserSchema, 'body'),
  userController.create
);

router.get(
  '/users',
  validate(listUsersQuerySchema, 'query'),
  userController.list
);

export { router as userRoutes };
```

> **Why middleware?** It separates validation from business logic, keeps
> controllers/handlers thin, and makes the validation rules visible in the
> route definition — a developer reading the route file immediately sees
> which schema applies.

### 6.5 Shared Schemas: Request → Response → OpenAPI

One of Zod's greatest strengths is that a single schema definition can serve
three purposes simultaneously:

```text
                    ┌──────────────┐
                    │  Zod Schema  │  ← Single source of truth
                    └──────┬───────┘
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
    Request Validation  TypeScript   OpenAPI Spec
    (.parse() at        Type         (generated from
     boundary)          (z.infer)    schema → docs)
```

- **MUST** use `z.infer<typeof schema>` for TypeScript types — never
  define parallel type declarations manually
- **SHOULD** generate OpenAPI specification from Zod schemas rather than
  maintaining the spec manually — this eliminates drift between validation
  and documentation (→ See [Section 11](#11-api-documentation),
  → See [02-technology-radar.md, Section 4.10 — OpenAPI])
- **SHOULD** share base field definitions between request and response
  schemas — but keep them separate when they differ (e.g., `password`
  exists in the request schema but **MUST NOT** exist in the response
  schema):

  ```ts
  // Request — includes password
  export const createUserSchema = z.object({
    name,
    email,
    password: z.string().min(8).max(128),
  });

  // Response — excludes password, includes server-generated fields
  // Zod 4: use top-level format functions (z.uuidv4, z.iso.datetime)
  export const userResponseSchema = z.object({
    id: z.uuidv4(),
    name,
    email,
    role,
    createdAt: z.iso.datetime(),
    updatedAt: z.iso.datetime(),
  });

  // NEVER return the request schema as the response — it may contain
  // sensitive fields (password, tokens, internal flags)
  ```

- **MUST NOT** use the same schema object for both request validation and
  response serialization without review — request schemas may accept
  sensitive fields that must never appear in responses

### 6.6 Validation Anti-Patterns

| Anti-Pattern | Why It Is Wrong | Correct Alternative |
|---|---|---|
| Manual `if/else` validation | Verbose, inconsistent, error-prone, no type inference | Zod schema with `.parse()` |
| `safeParse` at the boundary | Requires manual error formatting in every handler | `.parse()` + centralized `ZodError` handler |
| Validation inside services | Service receives unvalidated data, coupling increases | Validate at the route handler (boundary) |
| Duplicate type + schema | Type and schema drift apart silently | `z.infer<typeof schema>` only |
| Missing `.max()` on strings | Allows unbounded input — DoS and storage abuse | Always set reasonable max length |
| Missing `.max()` on arrays | Batch endpoints accept unlimited items — memory/CPU abuse | Always cap arrays (e.g., `.max(100)`) |
| Trusting `parseInt(query.page)` | `parseInt("10abc")` returns `10` — partial parse | `z.coerce.number()` rejects invalid input |

### 6.7 Output Validation

Validating input is half the contract. Validating output ensures the API
never accidentally leaks internal fields, database columns, or sensitive
data that the consumer should not receive.

- **MUST** validate API response data against a Zod schema before sending
  to the client — this is a security control, not optional polish
- **MUST** define separate schemas for input and output when they differ
  (e.g., `createUserInput` vs `userResponse`) — the response schema
  controls exactly which fields leave the system boundary
- **MUST NOT** return raw database rows or ORM objects directly — always
  map through a response schema that acts as an allowlist of fields
```ts
  // BAD — raw database object sent to client (may leak internal fields)
  const user = await userRepository.findById(id);
  return NextResponse.json({ ok: true, data: user });

  // GOOD — validated through response schema (allowlist)
  const user = await userRepository.findById(id);
  const response = userResponseSchema.parse(user);
  return NextResponse.json({ ok: true, data: response });
```

- **SHOULD** colocate input and output schemas in the same schema file
  for each domain concept

> **Why:** Output validation prevents accidental data leaks when database
> schemas change (new columns are added, internal fields are renamed).
> Without it, a single migration can expose sensitive data to every API
> consumer.
> → See [07-security-standards.md, §3 — Defense in Depth] for the
> security perspective.

### 6.8 File Upload Endpoints

File uploads cross multiple concerns: the API receives the file, validates
it, stores it, and returns a reference. Security constraints for uploads
are defined in → See [07-security-standards.md, §3 — File Upload Validation].
This section covers the **API design patterns** for implementing uploads.

#### Strategy Selection
```text
Upload size < 5 MB and infrequent?
 ├── YES → Direct upload to API route (simple, synchronous)
 └── NO  → How important is performance and scalability?
           ├── Standard → Direct upload to API + forward to storage
           └── Critical → Pre-signed URL (client uploads directly to storage)
```

#### Pattern 1: Direct Upload via API Route (Simple)

Best for small files (avatars, documents) in full-stack Next.js
applications. The API route receives the file and forwards it to storage.
```ts
// app/api/uploads/route.ts — Next.js Route Handler
import { NextRequest, NextResponse } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabase/server';
import { randomUUID } from 'crypto';

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5 MB
const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/webp'] as const;

export async function POST(request: NextRequest) {
  const formData = await request.formData();
  const file = formData.get('file') as File | null;

  if (!file) {
    return NextResponse.json(
      { ok: false, error: { code: 'MISSING_FILE', message: 'No file provided' } },
      { status: 400 },
    );
  }

  // Validate size
  if (file.size > MAX_FILE_SIZE) {
    return NextResponse.json(
      { ok: false, error: { code: 'FILE_TOO_LARGE', message: 'File exceeds 5 MB limit' } },
      { status: 400 },
    );
  }

  // Validate type (MIME from header — also validate magic bytes for security)
  if (!ALLOWED_TYPES.includes(file.type as typeof ALLOWED_TYPES[number])) {
    return NextResponse.json(
      { ok: false, error: { code: 'INVALID_FILE_TYPE', message: 'Only JPEG, PNG, and WebP allowed' } },
      { status: 400 },
    );
  }

  // Rename with UUID — never use client-provided filename
  // → See [07-security-standards.md, §3 — File Upload Validation]
  const extension = file.name.split('.').pop() ?? 'bin';
  const storagePath = `uploads/${randomUUID()}.${extension}`;

  const supabase = await createSupabaseServerClient();
  const { error } = await supabase.storage
    .from('documents')
    .upload(storagePath, file, { contentType: file.type, upsert: false });

  if (error) {
    return NextResponse.json(
      { ok: false, error: { code: 'UPLOAD_FAILED', message: 'File upload failed' } },
      { status: 500 },
    );
  }

  const { data: { publicUrl } } = supabase.storage
    .from('documents')
    .getPublicUrl(storagePath);

  return NextResponse.json(
    { ok: true, data: { url: publicUrl, path: storagePath } },
    { status: 201 },
  );
}
```

#### Pattern 2: Pre-Signed URL (Scalable)

Best for large files or high-traffic upload scenarios. The client uploads
directly to storage (Supabase Storage, S3, R2), bypassing the API server.
The API only generates and returns the upload URL.
```ts
// app/api/uploads/presign/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { createSupabaseServerClient } from '@/lib/supabase/server';
import { z } from 'zod';
import { randomUUID } from 'crypto';

const presignRequestSchema = z.object({
  filename: z.string().min(1),
  contentType: z.string().min(1),
});

export async function POST(request: NextRequest) {
  const body = await request.json();
  const parsed = presignRequestSchema.parse(body);

  const extension = parsed.filename.split('.').pop() ?? 'bin';
  const storagePath = `uploads/${randomUUID()}.${extension}`;

  const supabase = await createSupabaseServerClient();
  const { data, error } = await supabase.storage
    .from('documents')
    .createSignedUploadUrl(storagePath);

  if (error || !data) {
    return NextResponse.json(
      { ok: false, error: { code: 'PRESIGN_FAILED', message: 'Could not generate upload URL' } },
      { status: 500 },
    );
  }

  return NextResponse.json({
    ok: true,
    data: { signedUrl: data.signedUrl, path: storagePath, token: data.token },
  });
}
```

#### Rules

- **MUST** validate file type, size, and rename files on the server —
  never trust client-provided filenames or MIME types
  (→ See [07-security-standards.md, §3 — File Upload Validation])
- **MUST** use `multipart/form-data` content type for direct uploads —
  document this explicitly in the endpoint specification
- **MUST** return the stored file path or public URL in the response —
  the client needs a reference to associate the upload with a record
- **SHOULD** use pre-signed URLs for files larger than 5 MB or for
  high-traffic upload scenarios — this offloads bandwidth from the API
  server to the storage provider
- **SHOULD** set per-bucket storage policies in Supabase (or S3) to
  enforce file size and type limits at the storage level as a second
  validation layer
- **SHOULD** implement upload progress tracking on the client side for
  files larger than 1 MB
  (→ See [05-frontend-standards.md] for the frontend upload component)
- **MUST NOT** store uploaded files in the project's `public/` directory
  or any web-accessible path — always use object storage

#### Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| Using client filename as storage path | Path traversal, overwrites, encoding issues | Rename with UUID + original extension |
| Trusting `Content-Type` header alone | Attackers can spoof MIME types | Validate magic bytes on the server |
| Uploading through API for large files | Blocks the API server, hits body size limits | Use pre-signed URLs for files > 5 MB |
| No file size limit | DoS via huge uploads, storage costs | Enforce limits at framework + application level |

---

## 7. Pagination, Filtering & Sorting

Any endpoint that returns a collection of resources **MUST** support pagination.
An unbounded `SELECT *` that returns 50,000 rows because no one added a `LIMIT`
is a performance incident waiting to happen — for the database, the server, the
network, and the client.

This section defines the standard patterns. For the security perspective on
capping request sizes, → See [07-security-standards.md, Section 6 —
Request Size & Payload Protection].

### 7.1 Pagination Strategies

There are two main pagination strategies. Each has trade-offs, and the choice
depends on the use case.

#### Offset-Based Pagination

The client requests a specific **page number** and **page size**. The server
calculates the offset (`skip = (page - 1) * pageSize`) and returns the
corresponding slice.

```
GET /api/users?page=2&pageSize=20
```

```json
{
  "ok": true,
  "data": [ ... ],
  "meta": {
    "page": 2,
    "pageSize": 20,
    "totalItems": 142,
    "totalPages": 8
  },
  "requestId": "req_abc123"
}
```

**Pros:** Simple to implement, supports "jump to page 5," easy to display
page numbers in the UI.

**Cons:** Inconsistent results when data is inserted or deleted between
page requests (items shift, duplicates or gaps appear). Performance
degrades on large offsets (`OFFSET 100000` still scans 100,000 rows).

#### Cursor-Based Pagination

The client sends an opaque **cursor** (typically an encoded reference to
the last item seen). The server returns the next batch starting after
that cursor.

```
GET /api/users?cursor=eyJpZCI6ImFiYzEyMyJ9&pageSize=20
```

```json
{
  "ok": true,
  "data": [ ... ],
  "meta": {
    "pageSize": 20,
    "nextCursor": "eyJpZCI6ImRlZjQ1NiJ9",
    "hasMore": true
  },
  "requestId": "req_def456"
}
```

**Pros:** Consistent results regardless of concurrent inserts/deletes.
Constant performance regardless of position in the dataset (uses
`WHERE id > cursor` instead of `OFFSET`).

**Cons:** Cannot "jump to page 5" — only forward/backward traversal.
Slightly more complex to implement.

#### Decision Guide: Offset vs Cursor

```text
Does the UI need numbered pages or "jump to page X"?
 ├── YES → Is the dataset small and rarely mutated (< 10,000 items)?
 │          ├── YES → Offset-based (simplest, good enough)
 │          └── NO  → Consider cursor with estimated total count
 └── NO  → Does the dataset change frequently or grow large?
            ├── YES → Cursor-based (consistent, performant)
            └── NO  → Offset-based (simpler to implement)
```

- **SHOULD** use **offset-based** as the default for admin panels,
  backoffice tools, and small datasets — it is simpler and supports
  the UI patterns users expect (page numbers, "showing 21–40 of 142")
- **SHOULD** use **cursor-based** for feeds, timelines, real-time lists,
  large datasets (> 10,000 items), and public APIs where consistency
  matters
- **MAY** support both strategies on the same endpoint if consumers have
  different needs — detect by the presence of `cursor` vs `page`

### 7.2 Pagination Rules

- **MUST** paginate every collection endpoint — no endpoint should return
  an unbounded list
- **MUST** enforce a **maximum page size** to prevent abuse — a consumer
  requesting `pageSize=999999` should not crash the server:

  ```ts
  const paginationSchema = z.object({
    page: z.coerce.number().int().min(1).default(1),
    pageSize: z.coerce.number().int().min(1).max(100).default(20),
  });
  ```

- **MUST** set a **sensible default** page size (e.g., 20) when the
  consumer does not specify one
- **MUST** include pagination metadata in the response `meta` object
  (→ See [Section 4.3](#43-standard-response-envelope))
- **MUST** return an empty array (`"data": []`) — not `null` or an
  error — when a page has no results
- **SHOULD** include `totalItems` and `totalPages` for offset-based
  pagination — consumers need this to render page navigation
- **SHOULD** include `hasMore` and `nextCursor` for cursor-based
  pagination — consumers need this to know whether to fetch more
- **MUST NOT** return negative page numbers or page sizes — validate
  with `z.coerce.number().int().min(1)`

#### Standard Pagination Parameters

| Strategy | Parameters | Response Meta Fields |
|----------|-----------|---------------------|
| Offset | `page`, `pageSize` | `page`, `pageSize`, `totalItems`, `totalPages` |
| Cursor | `cursor`, `pageSize` | `pageSize`, `nextCursor`, `hasMore` |

### 7.3 Filtering

Filtering allows consumers to narrow results by specific field values.

- **MUST** use **query parameters** named after the field being filtered:

  ```
  GET /api/vehicles?status=available&brand=mercedes
  GET /api/orders?status=pending&customerId=abc123
  GET /api/appointments?date=2025-04-15
  ```

- **MUST** validate all filter parameters with Zod — including allowed
  values for enum fields:

  ```ts
  const listVehiclesQuerySchema = z.object({
    // Pagination
    page: z.coerce.number().int().min(1).default(1),
    pageSize: z.coerce.number().int().min(1).max(100).default(20),
    // Filters
    status: z.enum(['available', 'sold', 'reserved']).optional(),
    brand: z.string().max(100).optional(),
    minPrice: z.coerce.number().min(0).optional(),
    maxPrice: z.coerce.number().min(0).optional(),
    // Sort
    sortBy: z.enum(['createdAt', 'price', 'year']).default('createdAt'),
    sortOrder: z.enum(['asc', 'desc']).default('desc'),
  });
  ```

- **MUST** ignore unknown query parameters silently (do not error) —
  this allows forward compatibility when new filters are added
- **SHOULD** use the field name directly as the parameter name — avoid
  inventing a custom filter syntax (e.g., `?filter[status]=active`)
  unless the API requires advanced query capabilities
- **SHOULD** support multiple values for the same filter where it makes
  sense, using comma-separated values:

  ```
  GET /api/vehicles?status=available,reserved
  ```

  ```ts
  // Schema for multi-value filter
  status: z
    .string()
    .transform((val) => val.split(','))
    .pipe(z.array(z.enum(['available', 'sold', 'reserved'])))
    .optional(),
  ```

- **MAY** support range filters for numeric and date fields using
  `min`/`max` prefixes:

  ```
  GET /api/vehicles?minPrice=10000&maxPrice=30000
  GET /api/vehicles?minYear=2020&maxYear=2025
  ```

### 7.4 Sorting

- **MUST** use `sortBy` and `sortOrder` as the standard parameter names
  (consistent with the convention defined in
  [Section 2.5](#25-query-parameters)):

  ```
  GET /api/vehicles?sortBy=price&sortOrder=asc
  GET /api/users?sortBy=createdAt&sortOrder=desc
  ```

- **MUST** restrict `sortBy` to a **whitelist of allowed fields** using
  `z.enum()` — never allow arbitrary column names in sort parameters
  (SQL injection risk):

  ```ts
  // BAD — allows any column name (injection risk)
  sortBy: z.string().optional()

  // GOOD — whitelist of allowed sort fields
  sortBy: z.enum(['createdAt', 'price', 'name', 'year']).default('createdAt')
  ```

- **MUST** define a **default sort order** for every collection endpoint
  — unsorted results are unpredictable and confuse consumers. The
  recommended default is `createdAt` descending (newest first)
- **SHOULD** ensure that the sort field is backed by a database index
  for acceptable performance (→ See [04-database-standards.md])
- **MAY** support multi-field sorting for advanced use cases using
  comma-separated values:

  ```
  GET /api/vehicles?sortBy=brand,price&sortOrder=asc,desc
  ```

  > **Note:** Multi-field sorting adds complexity. Only implement it
  > when there is a demonstrated consumer need — start with single-field
  > sorting (→ See [01-core-principles.md, Section 5.3 — YAGNI]).

### 7.5 Full-Text Search

- **SHOULD** use `search` or `q` as the standard parameter name for
  full-text search:

  ```
  GET /api/vehicles?search=mercedes+classe+a
  GET /api/users?q=joao
  ```

- **MUST** limit search query length with `.max()` to prevent abuse:

  ```ts
  search: z.string().max(200).optional()
  ```

- **MUST** sanitize search queries to prevent injection — when using
  database full-text search or `LIKE` queries, use parameterized queries
  and escape special characters
  (→ See [07-security-standards.md, Section 3])
- **SHOULD** search across multiple relevant fields (name, email,
  description) — not just one. Document which fields are included in
  the search

### 7.6 Combined Example

A complete collection endpoint combining pagination, filtering, sorting,
and search:

```
GET /api/vehicles?page=1&pageSize=20&status=available&minPrice=15000&sortBy=price&sortOrder=asc&search=mercedes
```

```ts
// Schema
const listVehiclesQuerySchema = z.object({
  // Pagination
  page: z.coerce.number().int().min(1).default(1),
  pageSize: z.coerce.number().int().min(1).max(100).default(20),
  // Filters
  status: z.enum(['available', 'sold', 'reserved']).optional(),
  brand: z.string().max(100).optional(),
  minPrice: z.coerce.number().min(0).optional(),
  maxPrice: z.coerce.number().min(0).optional(),
  minYear: z.coerce.number().int().min(1900).optional(),
  maxYear: z.coerce.number().int().max(2100).optional(),
  // Search
  search: z.string().max(200).optional(),
  // Sorting
  sortBy: z.enum(['createdAt', 'price', 'year', 'brand']).default('createdAt'),
  sortOrder: z.enum(['asc', 'desc']).default('desc'),
});
```

```json
// Response
{
  "ok": true,
  "data": [
    {
      "id": "v_abc123",
      "brand": "Mercedes",
      "model": "Classe A",
      "year": 2022,
      "price": 18500,
      "status": "available"
    }
  ],
  "meta": {
    "page": 1,
    "pageSize": 20,
    "totalItems": 7,
    "totalPages": 1
  },
  "requestId": "req_xyz789"
}
```

### 7.7 Pagination Anti-Patterns

| Anti-Pattern | Why It Is Wrong | Correct Alternative |
|---|---|---|
| No pagination on collection endpoints | Returns entire dataset — crashes with scale | Always paginate, always cap `pageSize` |
| No maximum on `pageSize` | Consumer can request `pageSize=1000000` | `.max(100)` (or project-appropriate cap) |
| No default `pageSize` | Missing parameter returns all items | `.default(20)` in the Zod schema |
| `totalItems` on cursor-based pagination | Requires a `COUNT(*)` query — expensive on large tables | Use `hasMore` boolean instead |
| Arbitrary column names in `sortBy` | SQL injection vector | Whitelist with `z.enum()` |
| Returning `null` for empty pages | Consumer must handle `null` vs `[]` | Always return `"data": []` |
| Offset pagination on real-time data | Items shift between page requests | Use cursor-based for volatile data |

---

## 8. Versioning Strategy

APIs evolve. New fields are added, behaviors change, business requirements
shift. Versioning is the mechanism that allows an API to evolve without
breaking existing consumers. Done well, it is invisible most of the time.
Done poorly — or not at all — it forces "big bang" migrations that break
every client simultaneously.

### 8.1 Breaking vs Non-Breaking Changes

Before versioning, the team must agree on what constitutes a **breaking
change**. This is the foundation — without this shared definition,
versioning decisions become arbitrary.

#### Non-Breaking Changes (Safe to Deploy Without New Version)

- Adding a **new field** to a response object
- Adding a **new optional parameter** to a request
- Adding a **new endpoint**
- Adding a **new error code**
- Adding a **new enum value** to a response field
- Changing an **error message** (consumers should use `error.code`, not
  `error.message`)
- Improving performance or fixing bugs that do not alter the contract

#### Breaking Changes (Require a New Version or Migration Plan)

- **Removing** a field from a response
- **Renaming** a field in a request or response
- **Changing the type** of a field (e.g., `string` → `number`,
  `object` → `array`)
- **Changing the meaning** of a field (e.g., `price` was in cents, now
  in euros)
- **Removing** an endpoint
- **Changing URL structure** of an existing endpoint
- **Adding a required field** to a request (existing clients do not
  send it)
- **Removing an enum value** from a request field (existing clients may
  still send it)
- **Changing the default behavior** of an existing parameter
- **Changing authentication or authorization** requirements for an
  existing endpoint
- **Changing status codes** for existing operations (e.g., `200` → `201`)
- **Changing the error code** for an existing failure case

#### Rules

- **MUST** document these definitions in the project README or API
  documentation so the entire team shares the same understanding
- **MUST** treat any change in the "breaking" list as requiring either
  a **new API version** or a **deprecation plan with migration period**
- **SHOULD** prefer non-breaking changes whenever possible — most
  features can be delivered as additive changes to the existing version

> **Why:** The distinction matters because non-breaking changes can ship
> immediately to all consumers. Breaking changes require coordination,
> migration guides, and a deprecation timeline. Knowing the boundary
> prevents accidental breakage.

### 8.2 Versioning Approach: URL Path

This standard uses **URL path versioning** as the default strategy.

```
/api/v1/users
/api/v1/orders/:id
/api/v2/users        ← new version, different contract
```

#### Why URL Path (and Not Headers or Query Parameters)

| Approach | Example | Pros | Cons |
|----------|---------|------|------|
| **URL path** (chosen) | `/api/v1/users` | Visible, explicit, easy to route, easy to test in browser/Postman | URL changes per version |
| Header | `Accept: application/vnd.myapi.v1+json` | Clean URLs | Hidden, hard to test, easy to forget |
| Query parameter | `/api/users?version=1` | Simple | Breaks caching, easy to omit, parameter pollution |

- **MUST** use URL path versioning (`/api/v1/`, `/api/v2/`) for APIs
  consumed by external clients, multiple independent consumers, or
  mobile apps where client updates are not immediate
- **MAY** omit versioning for internal APIs within a full-stack Next.js
  application where frontend and backend deploy together — the shared
  TypeScript types and Zod schemas serve as the contract, and breaking
  changes deploy atomically
- **MUST** use the format `/api/v{N}/` where `N` is a positive integer
  — no minor versions, no dates, no prefixes:

  ```
  # GOOD — clear, simple
  /api/v1/users
  /api/v2/users

  # BAD — over-complicated, ambiguous
  /api/v1.2/users
  /api/2025-03/users
  /api/version1/users
  ```

> **Why URL path?** It is the most **explicit** approach — the version
> is visible in every request, in every log, in every Postman collection.
> There is no ambiguity about which version a client is using. This
> aligns with the principle of Explicit Over Implicit
> (→ See [01-core-principles.md, Section 2.2]).

### 8.3 When to Create a New Version

Creating a new API version is a **significant decision** — it doubles
the maintenance surface and splits the consumer base. It should be the
last resort, not the first reaction to a change.

```text
Need to make a change to the API?
 │
 ├── Is it a non-breaking change?
 │    └── YES → Deploy to current version. No new version needed.
 │
 ├── Is it a breaking change?
 │    └── Can you make it non-breaking with an additive approach?
 │         ├── YES → Add new field/endpoint alongside the old one.
 │         │         Deprecate the old one. No new version needed.
 │         └── NO  → Is this a single endpoint or a systemic change?
 │                    ├── Single endpoint → Deprecate + replace with
 │                    │   new endpoint in current version (e.g.,
 │                    │   /api/v1/users/search replaces old filter)
 │                    └── Systemic → New version (v2) required.
 │                        Document migration guide.
 ```

- **MUST** exhaust non-breaking alternatives before creating a new
  version
- **MUST** create an ADR when a new API version is introduced, documenting
  the reason, scope, and migration plan
  (→ See [01-core-principles.md, Section 9 — ADRs])
- **SHOULD** limit the scope of a new version — version only the
  endpoints that actually changed, not the entire API surface. Unchanged
  endpoints can remain at the current version

### 8.4 Deprecation Lifecycle

When a version or endpoint must be retired, follow a structured
deprecation process. Never remove an endpoint without warning.

#### Stages

```text
Active ──► Deprecated ──► Sunset ──► Removed

  │            │              │           │
  │            │              │           └─ Endpoint returns 410 Gone
  │            │              │              or is removed entirely
  │            │              │
  │            │              └─ Final date announced. Endpoint may
  │            │                 return warning headers. Active
  │            │                 outreach to remaining consumers.
  │            │
  │            └─ Endpoint still works but response includes
  │               deprecation headers. Migration guide available.
  │               New consumers should not integrate with it.
  │
  └─ Current, fully supported endpoint.
```

#### Rules

- **MUST** communicate deprecation through response headers before
  removing any endpoint or version:

  ```
  Deprecation: true
  Sunset: Sat, 01 Nov 2025 00:00:00 GMT
  Link: <https://docs.example.com/migration/v2>; rel="deprecation"
  ```

- **MUST** provide a **migration guide** when deprecating an endpoint —
  describe what replaces it, how the request/response differs, and
  provide code examples
- **MUST** maintain a deprecated endpoint for a minimum period appropriate
  to the consumer base:

  | Consumer Type | Minimum Deprecation Period |
  |---------------|--------------------------|
  | Internal frontend (same deploy) | 1 sprint / 2 weeks |
  | Internal mobile or separate teams | 1–3 months |
  | External / third-party consumers | 6–12 months |

- **SHOULD** log usage of deprecated endpoints to track how many
  consumers still depend on them — this informs the sunset timeline
- **SHOULD** return `410 Gone` (not `404`) after an endpoint is removed
  — `410` tells the consumer the resource existed but has been
  permanently removed, and they should stop trying:

  ```json
  {
    "ok": false,
    "error": {
      "code": "ENDPOINT_REMOVED",
      "message": "This endpoint has been removed. Please migrate to /api/v2/users."
    },
    "requestId": "req_abc123"
  }
  ```

### 8.5 API Versioning Security

Versioning has security implications — old versions that are no longer
maintained become vulnerability windows.

- **MUST** apply the same security controls (authentication, authorization,
  rate limiting, input validation) to **all** API versions equally —
  a deprecated endpoint must remain secure until it is removed
- **MUST** remove old versions eventually — unmaintained API versions
  accumulate unpatched vulnerabilities
- **MUST NOT** relax security requirements on old versions to ease
  maintenance burden — if you cannot maintain security, remove the version

> → See [07-security-standards.md, Section 6 — API Versioning Security]
> for additional security requirements.

---

## 9. Authentication & Authorization Patterns

Authentication (who are you?) and authorization (what can you do?) are the
**gatekeepers** of every API. This section defines how to implement them
in the API layer — the middleware chain, the patterns, and the practical
integration with the tools in the stack.

For the security rules, threat models, and detailed requirements:
- → See [07-security-standards.md, Section 4 — Authentication Standards]
- → See [07-security-standards.md, Section 5 — Authorization (RBAC / ABAC)]

For the tooling choices (Supabase Auth, Auth.js):
- → See [02-technology-radar.md, Section 4.9 — Auth & Identity]

### 9.1 The Middleware Chain

Every protected API request passes through a **sequential chain** of
checks before reaching the route handler. Each step has a single
responsibility, and failure at any step short-circuits the chain with
the appropriate error response.

```text
Request
  │
  ▼
┌───────────────────┐
│  1. Rate Limiting │ → 429 Too Many Requests
└────────┬──────────┘
         ▼
┌───────────────────┐
│  2. Authentication│ → 401 Unauthorized
│  (who are you?)   │
└────────┬──────────┘
         ▼
┌───────────────────┐
│  3. Authorization │ → 403 Forbidden (or 404 for hidden resources)
│ (can you do this?)│
└────────┬──────────┘
         ▼
┌───────────────────┐
│  4. Validation    │ → 400 Bad Request / 422 Unprocessable Entity
│  (is the data ok?)│
└────────┬──────────┘
         ▼
┌───────────────────┐
│  5. Route Handler │ → Business logic via service layer
└───────────────────┘
```

#### Why This Order Matters

- **Rate limiting first** — reject abusive traffic before spending any
  resources on authentication or database queries
- **Authentication before authorization** — you cannot check permissions
  for an unknown user
- **Authorization before validation** — do not waste time validating a
  request body from a user who does not have permission to perform the
  action
- **Validation last** — by this point, we know the caller is legitimate
  and permitted. Now validate their data.

#### Rules

- **MUST** follow this middleware order consistently across all protected
  endpoints
- **MUST** short-circuit on failure — if authentication fails, never
  proceed to authorization or validation
- **SHOULD** implement each step as an independent, composable middleware
  function (Express) or utility (Next.js)

### 9.2 Authentication Patterns

Authentication verifies the caller's identity. The standard approach in
modern APIs is **token-based authentication** using Bearer tokens in the
`Authorization` header.

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

#### Pattern: Supabase Auth (Default for Full-Stack Next.js)

Supabase Auth provides JWT-based authentication out of the box. For
Next.js applications, the recommended approach uses `@supabase/ssr`
to create a server client that handles cookies and token refresh
automatically. For standalone API endpoints that receive a Bearer
token, you can validate the token by calling `getUser()`.

```ts
// src/lib/supabase/server.ts — recommended for Next.js SSR
import { createServerClient } from '@supabase/ssr';
import { cookies } from 'next/headers';

export async function createSupabaseServerClient() {
  const cookieStore = await cookies();

  return createServerClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_ANON_KEY!,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value, options }) =>
            cookieStore.set(name, value, options)
          );
        },
      },
    }
  );
}
```

```ts
// src/lib/auth.ts — authenticate request using Supabase
import { createSupabaseServerClient } from './supabase/server';
import { UnauthorizedError } from '../errors';

export async function authenticateRequest(): Promise<AuthenticatedUser> {
  const supabase = await createSupabaseServerClient();

  const { data: { user }, error } = await supabase.auth.getUser();

  if (error || !user) {
    throw new UnauthorizedError('Invalid or expired token');
  }

  return {
    id: user.id,
    email: user.email!,
    role: user.app_metadata?.role ?? 'user',
  };
}
```

> **Important:** Always use `getUser()` — not `getSession()` — for
> server-side authentication. `getUser()` validates the JWT with
> Supabase's auth server on every call, while `getSession()` only
> reads the local session without revalidation.
> → See [07-security-standards.md, Section 4 — Token Validation].
>
> **Note:** Supabase is migrating to new API key formats
> (`sb_publishable_...` / `sb_secret_...`). New projects may use these
> instead of the legacy `SUPABASE_ANON_KEY` / `SUPABASE_SERVICE_ROLE_KEY`.
> The patterns above work with both formats.

#### Pattern: Auth.js v5 (NextAuth) for Multi-Provider

When the project requires multiple OAuth providers (Google, GitHub,
email/password) without Supabase, Auth.js v5 provides a unified
authentication layer. In v5, configuration lives in a single `auth.ts`
file at the project root, and the universal `auth()` function replaces
the old `getServerSession(authOptions)` pattern from v4.

```ts
// auth.ts — project root configuration
import NextAuth from 'next-auth';
import GitHub from 'next-auth/providers/github';
import Google from 'next-auth/providers/google';

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [GitHub, Google],
  callbacks: {
    session({ session, token }) {
      if (token.sub) session.user.id = token.sub;
      if (token.role) session.user.role = token.role as string;
      return session;
    },
    jwt({ token, user }) {
      if (user?.role) token.role = user.role;
      return token;
    },
  },
});
```

```ts
// app/api/auth/[...nextauth]/route.ts — API route handler
import { handlers } from '@/auth';
export const { GET, POST } = handlers;
```

```ts
// src/lib/auth.ts — authentication helper
import { auth } from '@/auth';
import { UnauthorizedError } from '../errors';

export async function authenticateRequest(): Promise<AuthenticatedUser> {
  // Auth.js v5: single auth() call replaces getServerSession(authOptions)
  const session = await auth();

  if (!session?.user) {
    throw new UnauthorizedError('Authentication required');
  }

  return {
    id: session.user.id,
    email: session.user.email!,
    role: session.user.role ?? 'user',
  };
}
```

> **Note (Next.js 16):** In Next.js 16, `middleware.ts` has been renamed
> to `proxy.ts`. Auth.js v5 integrates with the new proxy pattern:
> ```ts
> // proxy.ts
> export { auth as proxy } from '@/auth';
> ```

#### Pattern: Express Middleware

```ts
// src/middleware/authenticate.ts
import { Request, Response, NextFunction } from 'express';
import { UnauthorizedError } from '../errors';
import { verifyToken } from '../lib/jwt';

export async function authenticate(
  req: Request,
  _res: Response,
  next: NextFunction
): Promise<void> {
  const authHeader = req.headers.authorization;

  if (!authHeader?.startsWith('Bearer ')) {
    throw new UnauthorizedError('Missing or invalid authorization header');
  }

  const token = authHeader.slice(7);
  const user = await verifyToken(token);

  if (!user) {
    throw new UnauthorizedError('Invalid or expired token');
  }

  // Attach authenticated user to request for downstream use
  req.user = user;
  next();
}
```

#### Rules

- **MUST** use the `Authorization: Bearer <token>` header for API
  authentication — not query parameters, not cookies (for API endpoints)
- **MUST** validate tokens on every request — never trust a token
  without verification
  (→ See [07-security-standards.md, Section 4])
- **MUST** return `401 Unauthorized` with a clear error when
  authentication fails — never proceed with an anonymous user on
  a protected endpoint
- **MUST NOT** include tokens, secrets, or credentials in URL query
  parameters — URLs are logged in browser history, server access logs,
  and proxy logs
  (→ See [07-security-standards.md, Section 7])
- **SHOULD** define a consistent `AuthenticatedUser` type used across
  the entire application:

  ```ts
  // src/types/auth.ts
  type AuthenticatedUser = {
    id: string;
    email: string;
    role: UserRole;
  };

  type UserRole = 'admin' | 'manager' | 'user';
  ```

### 9.3 Authorization Patterns

Authorization determines whether an authenticated user has **permission**
to perform a specific action on a specific resource. It lives in the
**service layer** — not in the route handler, not in the database query.

> → See [07-security-standards.md, Section 5] for the full RBAC/ABAC
> model, audit trail requirements, and permission design rules.

#### Pattern: Role-Based Checks (RBAC)

The simplest authorization model: the user's role determines what they
can do.

```ts
// src/middleware/authorize.ts (Express)
import { Request, Response, NextFunction } from 'express';
import { ForbiddenError } from '../errors';
import { UserRole } from '../types/auth';

export function authorize(...allowedRoles: UserRole[]) {
  return (req: Request, _res: Response, next: NextFunction) => {
    const user = req.user;

    if (!user || !allowedRoles.includes(user.role)) {
      throw new ForbiddenError(
        'You do not have permission to perform this action'
      );
    }

    next();
  };
}

// Usage in routes
router.get('/users', authenticate, authorize('admin', 'manager'), userController.list);
router.delete('/users/:id', authenticate, authorize('admin'), userController.delete);
```

```ts
// Next.js Route Handler equivalent
export const DELETE = apiHandler(async (request, { params, requestId }) => {
  const user = await authenticateRequest();

  if (user.role !== 'admin') {
    throw new ForbiddenError(
      'You do not have permission to delete users'
    );
  }

  const { id } = userIdParamSchema.parse(params);
  await userService.delete(id);

  return NextResponse.json(
    { ok: true, data: null, requestId },
    { status: 200 }
  );
});
```

#### Pattern: Resource Ownership Checks

Role alone is often not enough. A `user` role can update **their own**
profile but not another user's. This requires checking **ownership** of
the specific resource.

```ts
// src/services/user-service.ts
import { ForbiddenError, NotFoundError } from '../errors';
import { AuthenticatedUser } from '../types/auth';

async function updateUser(
  userId: string,
  data: UpdateUserInput,
  currentUser: AuthenticatedUser
): Promise<User> {
  const user = await userRepository.findById(userId);

  if (!user) {
    throw new NotFoundError('User', userId);
  }

  // Admins can update anyone; regular users can only update themselves
  if (currentUser.role !== 'admin' && currentUser.id !== user.id) {
    // Return 404, not 403, to avoid confirming the resource exists
    // → See [Section 3.3 — 404 as a Security Control]
    throw new NotFoundError('User', userId);
  }

  return userRepository.update(userId, data);
}
```

#### Rules

- **MUST** check authorization in the service layer, not in route
  handlers — this ensures authorization is enforced regardless of
  which route handler calls the service
  (→ See [07-security-standards.md, Section 5 — Service Layer])
- **MUST** check both **role** AND **resource ownership** where
  applicable — role alone is not sufficient for multi-tenant or
  user-scoped resources
- **MUST** return `404 Not Found` (not `403 Forbidden`) when a user
  attempts to access a resource they should not know exists
  (→ See [Section 3.3](#33-status-codes))
- **MUST** log authorization failures with context (userId, resource,
  action) for audit purposes
  (→ See [07-security-standards.md, Section 5 — Audit Trail])
- **MUST NOT** rely on client-side role checks — the UI may hide
  buttons from non-admins, but the API must independently enforce
  permissions
- **SHOULD** keep authorization logic composable and testable —
  small, focused functions that can be unit tested with different
  role/ownership combinations

### 9.4 Public vs Protected Endpoints

Not every endpoint requires authentication. Define clearly which
endpoints are public and protect everything else by default.

- **MUST** protect all endpoints **by default** — public access is
  the exception, not the rule
- **MUST** document which endpoints are public and why
- **SHOULD** organize routes to make protection visible:

  ```ts
  // Express — explicit separation
  // Public routes (no authentication)
  router.get('/health', healthController.check);
  router.post('/auth/login', authController.login);
  router.post('/auth/register', authController.register);
  router.post('/webhooks/stripe', webhookController.stripe);

  // Protected routes (authentication required)
  router.use(authenticate); // Everything below requires auth
  router.get('/users', authorize('admin', 'manager'), userController.list);
  router.get('/users/me', userController.getProfile);
  router.patch('/users/me', userController.updateProfile);
  router.post('/orders', userController.createOrder);
  ```

- **SHOULD** keep the list of public endpoints minimal — the smaller
  the unauthenticated surface, the smaller the attack surface
  (→ See [07-security-standards.md, Section 1 — Zero Trust])

---

## 10. Rate Limiting & Abuse Prevention

Rate limiting protects the API from abuse — whether intentional (brute
force attacks, scraping, DDoS) or accidental (a client bug that fires
thousands of requests in a loop). Without rate limiting, a single
misbehaving consumer can degrade the service for everyone.

This section defines **implementation patterns** for the API layer. For
the security rules, recommended limits per endpoint type, tools, and
layered defense strategy:
→ See [07-security-standards.md, Section 6 — API Security (Rate
Limiting, Throttling, Abuse Prevention)].

### 10.1 Implementation Strategy

Rate limiting should be applied at **multiple layers** (defense in depth),
but this section focuses on the **application layer** — the middleware
that runs inside the API code.

```text
Layer 1: CDN / Reverse Proxy     → IP-based, coarse (Cloudflare, Nginx)
Layer 2: Application Middleware   → User/key-based, granular (this section)
Layer 3: Per-Endpoint Rules       → Business-rule-based (sensitive endpoints)
```

- **MUST** implement application-level rate limiting as middleware that
  runs **before** authentication (→ See [Section 9.1](#91-the-middleware-chain))
- **SHOULD** additionally configure CDN/proxy-level rate limiting as the
  first line of defense — application-level limiting alone is not enough
  for volumetric attacks
- **SHOULD** use a Redis-backed limiter for multi-instance deployments
  where in-memory counters are not shared across server instances

### 10.2 Pattern: Express Rate Limiting

```ts
// src/middleware/rate-limit.ts
import rateLimit from 'express-rate-limit';
import RedisStore from 'rate-limit-redis';
import { redis } from '../lib/redis';

// General API rate limit
export const generalLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 100,            // 100 requests per minute per IP
  standardHeaders: true, // Return RateLimit-* headers
  legacyHeaders: false,
  message: {
    ok: false,
    error: {
      code: 'RATE_LIMITED',
      message: 'Too many requests. Please try again later.',
    },
  },
  // Use Redis store for multi-instance deployments
  store: new RedisStore({
    sendCommand: (...args: string[]) => redis.call(...args),
  }),
});

// Strict limit for authentication endpoints
export const authLimiter = rateLimit({
  windowMs: 60 * 1000,
  max: 5, // 5 attempts per minute per IP
  standardHeaders: true,
  legacyHeaders: false,
  message: {
    ok: false,
    error: {
      code: 'RATE_LIMITED',
      message: 'Too many authentication attempts. Please try again later.',
    },
  },
  store: new RedisStore({
    sendCommand: (...args: string[]) => redis.call(...args),
  }),
});

// Usage in routes
app.use('/api/', generalLimiter);
app.use('/api/auth/', authLimiter); // Overrides general for auth routes
```

### 10.3 Pattern: Next.js Rate Limiting

Next.js Route Handlers do not have Express-style middleware. The
recommended approach is a **utility function** using Upstash Redis
(serverless-compatible) or an in-memory store for single-instance
deployments.

```ts
// src/lib/rate-limit.ts
import { Ratelimit } from '@upstash/ratelimit';
import { Redis } from '@upstash/redis';
import { RateLimitError } from '../errors';

const redis = new Redis({
  url: process.env.UPSTASH_REDIS_URL!,
  token: process.env.UPSTASH_REDIS_TOKEN!,
});

// Sliding window: 100 requests per 60 seconds
const generalLimiter = new Ratelimit({
  redis,
  limiter: Ratelimit.slidingWindow(100, '60 s'),
  analytics: true,
  prefix: 'ratelimit:general',
});

// Strict: 5 requests per 60 seconds
const authLimiter = new Ratelimit({
  redis,
  limiter: Ratelimit.slidingWindow(5, '60 s'),
  analytics: true,
  prefix: 'ratelimit:auth',
});

export async function checkRateLimit(
  identifier: string,
  type: 'general' | 'auth' = 'general'
): Promise<void> {
  const limiter = type === 'auth' ? authLimiter : generalLimiter;
  const { success, limit, remaining, reset } = await limiter.limit(identifier);

  if (!success) {
    const retryAfter = Math.ceil((reset - Date.now()) / 1000);
    throw new RateLimitError(retryAfter);
  }
}
```

Usage in a Route Handler:

```ts
// app/api/auth/login/route.ts
export const POST = apiHandler(async (request, { requestId }) => {
  // Rate limit by IP (before authentication)
  const ip = request.headers.get('x-forwarded-for') ?? 'unknown';
  await checkRateLimit(ip, 'auth');

  const body = await request.json();
  const parsed = loginSchema.parse(body);

  const result = await authService.login(parsed);

  return NextResponse.json(
    { ok: true, data: result, requestId },
    { status: 200 }
  );
});
```

### 10.4 Response Headers

When a request is rate-limited, the response must include headers that
tell the consumer **when** they can retry and **how much** quota remains.

- **MUST** return `429 Too Many Requests` when the rate limit is exceeded
- **MUST** include the `Retry-After` header (seconds until the limit
  resets):

  ```
  HTTP/1.1 429 Too Many Requests
  Retry-After: 30
  RateLimit-Limit: 100
  RateLimit-Remaining: 0
  RateLimit-Reset: 1711036800
  ```

- **SHOULD** include the standard `RateLimit-*` headers on all responses
  (not just 429) so consumers can monitor their usage proactively:

  | Header | Purpose |
  |--------|---------|
  | `RateLimit-Limit` | Maximum requests allowed in the window |
  | `RateLimit-Remaining` | Requests remaining in the current window |
  | `RateLimit-Reset` | Unix timestamp when the window resets |
  | `Retry-After` | Seconds until the consumer can retry (on 429 only) |

- **MUST** return the error in the standard response envelope
  (→ See [Section 4.3](#43-standard-response-envelope)):

  ```json
  {
    "ok": false,
    "error": {
      "code": "RATE_LIMITED",
      "message": "Too many requests. Please try again later."
    },
    "requestId": "req_abc123"
  }
  ```

### 10.5 Identifying Callers

The effectiveness of rate limiting depends on correctly identifying
the caller. Different strategies apply depending on whether the caller
is authenticated.

| Context | Identifier | Notes |
|---------|-----------|-------|
| Unauthenticated | Client IP (`X-Forwarded-For`) | Awareness: shared IPs (NAT, corporate networks) may affect legitimate users |
| Authenticated | User ID or API key | More accurate — limits apply per user, not per IP |
| Mixed endpoint | IP before auth, User ID after auth | Two-phase: coarse IP limit first, then granular user limit |

- **MUST** use IP-based limiting for unauthenticated endpoints (login,
  register, public APIs)
- **SHOULD** switch to user-based limiting for authenticated endpoints
  — this is more accurate and does not penalize users behind shared IPs
- **SHOULD** be aware that `X-Forwarded-For` can be spoofed — if using
  IP-based limiting, ensure the header is set by a trusted proxy
  (Cloudflare, load balancer), not directly by the client
  (→ See [07-security-standards.md, Section 6])

### 10.6 Rate Limiting Anti-Patterns

| Anti-Pattern | Why It Is Wrong | Correct Alternative |
|---|---|---|
| No rate limiting at all | Any consumer can exhaust resources | Always implement, even basic limits |
| Same limit for all endpoints | Auth endpoints need stricter limits than read endpoints | Per-endpoint or per-category limits |
| In-memory only in multi-instance | Each instance has its own counter — limit is multiplied | Use Redis-backed store |
| Rate limiting after authentication | Brute force attacks bypass the limit | Rate limit before authentication |
| Blocking legitimate users behind NAT | Shared IP gets rate-limited for one user's abuse | Combine IP + user-based limiting |
| No `Retry-After` header | Consumer does not know when to retry — hammers the API | Always include `Retry-After` on 429 |
| Generic 500 instead of 429 | Consumer cannot distinguish rate limit from server error | Return 429 with standard envelope |

---

## 11. API Documentation

An API without documentation is an API no one can use correctly —
including your future self. But documentation that is out of sync with
the implementation is worse than no documentation at all: it actively
misleads consumers into writing broken integrations.

The goal is **documentation that stays accurate by design** — generated
from the same source code and schemas that power the API, not maintained
as a separate artifact that drifts with every commit.

For the documentation philosophy and general rules:
→ See [01-core-principles.md, Section 8 — Documentation Standards].
For the tooling choices (OpenAPI, Postman):
→ See [02-technology-radar.md, Section 4.10 — API Tooling & Documentation].

### 11.1 Code-First vs Spec-First

There are two approaches to API documentation. Both produce an OpenAPI
specification — they differ in which comes first.

| Approach | Workflow | Best For |
|----------|----------|----------|
| **Spec-first** | Write OpenAPI YAML/JSON → Generate server stubs + client SDKs → Implement | Public APIs with external consumers, contract-driven teams |
| **Code-first** | Write code with Zod schemas → Generate OpenAPI spec from code → Serve docs | Internal APIs, full-stack apps, small teams iterating fast |

- **SHOULD** use **code-first** as the default approach — it aligns with
  the existing Zod-based validation workflow where schemas are already
  the single source of truth
  (→ See [Section 6.5](#65-shared-schemas-request--response--openapi))
- **MAY** use **spec-first** for public APIs consumed by external
  partners where the contract must be agreed before implementation begins
- **MUST NOT** maintain the OpenAPI spec manually alongside code-first
  schemas — this guarantees drift. Pick one source of truth.

> **Why code-first?** The team already writes Zod schemas for validation
> and TypeScript types. Generating the OpenAPI spec from those same
> schemas means zero extra documentation effort — the docs are a
> by-product of the code that already exists.

### 11.2 Generating OpenAPI from Zod

The Zod-to-OpenAPI pipeline turns existing validation schemas into a
full API specification with minimal additional annotation.

> **Zod 4 note:** Use `@asteasolutions/zod-to-openapi` **v8+** for Zod 4
> support (v7.x only supports Zod 3). Zod 4 also supports `.meta()`
> natively for attaching OpenAPI metadata to schemas, which
> `zod-to-openapi` v8 reads automatically alongside `.openapi()`.

```ts
// src/docs/openapi.ts
import {
  OpenAPIRegistry,
  OpenApiGeneratorV3,
  extendZodWithOpenApi,
} from '@asteasolutions/zod-to-openapi';
import { z } from 'zod';
import { createUserSchema, userResponseSchema } from '../schemas/user';

// Required once — extends Zod schemas with .openapi() method
extendZodWithOpenApi(z);

const registry = new OpenAPIRegistry();

// Register schemas
registry.register('CreateUserInput', createUserSchema);
registry.register('UserResponse', userResponseSchema);

// Register endpoints
registry.registerPath({
  method: 'post',
  path: '/api/v1/users',
  summary: 'Create a new user',
  tags: ['Users'],
  request: {
    body: {
      content: {
        'application/json': {
          schema: createUserSchema,
        },
      },
    },
  },
  responses: {
    201: {
      description: 'User created successfully',
      content: {
        'application/json': {
          schema: z.object({
            ok: z.literal(true),
            data: userResponseSchema,
            requestId: z.string(),
          }),
        },
      },
    },
    400: {
      description: 'Validation error',
      // ... error envelope schema
    },
  },
});

// Generate the spec
const generator = new OpenApiGeneratorV3(registry.definitions);

export const openApiSpec = generator.generateDocument({
  openapi: '3.1.0',
  info: {
    title: 'My API',
    version: '1.0.0',
    description: 'API documentation generated from Zod schemas',
  },
  servers: [
    { url: 'http://localhost:3000', description: 'Development' },
  ],
});
```

#### Serving the Documentation

```ts
// Express — serve Swagger UI
import swaggerUi from 'swagger-ui-express';
import { openApiSpec } from './docs/openapi';

// Development and staging only
if (process.env.NODE_ENV !== 'production') {
  app.use('/docs', swaggerUi.serve, swaggerUi.setup(openApiSpec));
  app.get('/docs/openapi.json', (_req, res) => {
    res.json(openApiSpec);
  });
}
```

```ts
// Next.js — serve via API route (dev/staging only)
// app/api/docs/openapi/route.ts
import { NextResponse } from 'next/server';
import { openApiSpec } from '@/docs/openapi';

export async function GET() {
  if (process.env.NODE_ENV === 'production') {
    return NextResponse.json(
      { ok: false, error: { code: 'NOT_FOUND', message: 'Not found' } },
      { status: 404 }
    );
  }

  return NextResponse.json(openApiSpec);
}
```

### 11.3 What to Document

Every endpoint in the API **MUST** be documented with sufficient
information for a consumer to integrate without reading the source code.

#### Per-Endpoint Documentation

- **MUST** document:
  - HTTP method and path
  - Summary (one line describing what the endpoint does)
  - Request parameters: path params, query params, request body — with
    types, constraints, and whether they are required or optional
  - Response format: success response with example, error responses
    with codes and examples
  - Authentication requirements (public, authenticated, specific roles)
  - Rate limiting tier (if different from the general limit)

- **SHOULD** document:
  - A longer description with context or usage notes when the summary
    is not sufficient
  - Request and response examples with realistic data
  - Related endpoints (e.g., "see also: GET /api/users/:id")

- **SHOULD** group endpoints by resource using **tags** (Users, Orders,
  Vehicles, Auth) — this organizes the documentation logically for
  consumers

#### API-Level Documentation

- **SHOULD** include in the OpenAPI spec's `info` section:
  - API title and version
  - Brief description of the API's purpose
  - Contact information for the team responsible
  - Link to the authentication guide

- **SHOULD** document the standard response envelope
  (→ See [Section 4.3](#43-standard-response-envelope)) in a shared
  section so consumers understand the format before reading individual
  endpoints

- **SHOULD** document the error codes catalogue
  (→ See [Section 5.3](#53-error-codes-catalogue)) so consumers can
  build comprehensive error handling

### 11.4 Keeping Documentation in Sync

Documentation that drifts from the implementation is actively harmful.
These rules minimize drift.

- **MUST** generate the OpenAPI spec from Zod schemas — never maintain
  it as a separate manual document
- **SHOULD** include documentation generation in the CI pipeline — if
  a schema changes and the spec is not regenerated, the build should
  warn or fail
- **SHOULD** include "API documentation updated" as a checklist item in
  the Definition of Done for any endpoint change
  (→ See [01-core-principles.md, Section 11 — Definition of Done])
- **SHOULD** version the generated OpenAPI spec file in the repository
  alongside the code — this allows reviewing documentation changes in
  pull requests
- **MUST NOT** edit the generated OpenAPI spec manually — edits will be
  overwritten on the next generation. If additional documentation is
  needed, add it to the schema annotations or registry configuration.

### 11.5 Documentation Security

API documentation is a **map of the attack surface**. In the wrong
hands, it tells an attacker exactly which endpoints exist, what
parameters they accept, and how authentication works.

- **MUST** disable or protect documentation endpoints in production
  (→ See [07-security-standards.md, Section 10 — A05: Security
  Misconfiguration]):

  ```ts
  // Only serve docs in non-production environments
  if (process.env.NODE_ENV !== 'production') {
    app.use('/docs', swaggerUi.serve, swaggerUi.setup(openApiSpec));
  }
  ```

- **MUST** separate internal and external API documentation — internal
  endpoints (admin, backoffice) should not appear in documentation
  accessible to external consumers
- **SHOULD** use a `@internal` tag or a separate OpenAPI registry for
  internal-only endpoints
- **MAY** serve documentation in production behind authentication for
  internal teams — but never publicly accessible

### 11.6 Documentation Anti-Patterns

| Anti-Pattern | Why It Is Wrong | Correct Alternative |
|---|---|---|
| Manual OpenAPI YAML alongside Zod schemas | Two sources of truth — guaranteed drift | Generate spec from Zod schemas |
| Documentation only in README | Not machine-readable, not interactive, not versioned with endpoints | OpenAPI spec + interactive UI (Swagger UI / Scalar) |
| No examples in documentation | Consumer must guess the request/response format | Include realistic examples for every endpoint |
| Documentation in production without protection | Exposes attack surface to anyone | Disable in production or protect with authentication |
| Documenting only the happy path | Consumer has no guidance for error handling | Document all error responses with codes and examples |
| Copy-pasting endpoint docs | Stale copies when the original changes | Generate from a single source (Zod schemas) |

---

## 12. Webhook Design

Webhooks are **event-driven API calls** — instead of a consumer polling
for changes ("is there a new payment?"), the provider pushes a
notification when an event occurs ("a payment was just completed"). They
are the backbone of integrations with services like Stripe, Supabase,
GitHub, and any third-party that needs to notify your application of
state changes.

This section covers both **inbound webhooks** (your API receives events
from external providers) and **outbound webhooks** (your API sends events
to external consumers).

For the security rules on webhook signature verification:
→ See [07-security-standards.md, Section 6 — Webhook Security (Inbound)].

### 12.1 Inbound Webhooks: Receiving Events

Inbound webhooks are endpoints in your API that external providers call
when something happens — a Stripe payment succeeds, a Supabase row is
inserted, a GitHub PR is merged.

#### The Golden Rule: Acknowledge First, Process Later

Webhook providers have **timeout limits** (typically 5–30 seconds). If
your endpoint does not respond in time, the provider considers the
delivery failed and retries — potentially causing duplicate processing.

```text
External Provider                    Your API
────────────────                    ─────────
      │                                │
      │  POST /api/webhooks/stripe     │
      │ ──────────────────────────►    │
      │                                │ 1. Verify signature
      │                                │ 2. Validate payload schema
      │                                │ 3. Store event (or enqueue)
      │        200 OK                  │ 4. Return 200 immediately
      │ ◄──────────────────────────    │
      │                                │ 5. Process asynchronously
      │                                │    (service layer, background job)
```

- **MUST** return `200` (or `2xx`) as quickly as possible — within
  seconds, not minutes
- **MUST** verify the webhook signature before any processing
  (→ See [07-security-standards.md, Section 6])
- **MUST** validate the payload structure with Zod before processing
- **SHOULD** separate acknowledgment from processing — store the raw
  event and process it asynchronously when the processing involves
  database writes, external API calls, or any operation that may be
  slow or fail
- **MAY** process synchronously for simple, fast operations (e.g.,
  updating a single field) — but always be aware of the provider's
  timeout limit

#### Pattern: Stripe Webhook Handler (Next.js)

```ts
// app/api/webhooks/stripe/route.ts
import { NextRequest, NextResponse } from 'next/server';
import Stripe from 'stripe';
import { generateRequestId } from '@/lib/request-id';
import { logger } from '@/lib/logger';

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);
const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET!;

export async function POST(request: NextRequest) {
  const requestId = generateRequestId();
  const body = await request.text(); // Raw body needed for signature
  const signature = request.headers.get('stripe-signature');

  if (!signature) {
    logger.warn('Webhook missing signature', { requestId });
    return NextResponse.json(
      { ok: false, error: { code: 'UNAUTHORIZED', message: 'Missing signature' }, requestId },
      { status: 401 }
    );
  }

  // 1. Verify signature (MUST — before any processing)
  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(body, signature, webhookSecret);
  } catch (error) {
    logger.warn('Webhook signature verification failed', {
      requestId,
      error: error instanceof Error ? error.message : String(error),
    });
    return NextResponse.json(
      { ok: false, error: { code: 'UNAUTHORIZED', message: 'Invalid signature' }, requestId },
      { status: 401 }
    );
  }

  // 2. Log the event for traceability
  logger.info('Webhook received', {
    requestId,
    eventId: event.id,
    eventType: event.type,
  });

  // 3. Route to the appropriate handler
  try {
    switch (event.type) {
      case 'payment_intent.succeeded':
        await handlePaymentSuccess(event.data.object, requestId);
        break;
      case 'payment_intent.payment_failed':
        await handlePaymentFailure(event.data.object, requestId);
        break;
      case 'customer.subscription.updated':
        await handleSubscriptionUpdate(event.data.object, requestId);
        break;
      default:
        logger.info('Unhandled webhook event type', {
          requestId,
          eventType: event.type,
        });
    }
  } catch (error) {
    // Log the processing error but still return 200
    // to prevent the provider from retrying
    logger.error('Webhook processing failed', {
      requestId,
      eventId: event.id,
      eventType: event.type,
      error: error instanceof Error ? error.message : String(error),
    });
    // Depending on strategy: return 200 (prevent retry) or 500 (trigger retry)
    // See §12.3 for retry handling guidance
  }

  // 4. Acknowledge receipt
  return NextResponse.json(
    { ok: true, data: { received: true }, requestId },
    { status: 200 }
  );
}
```

> **Note:** Webhook route handlers are an exception to the `apiHandler`
> wrapper pattern (→ See [Section 5.4](#54-centralized-error-to-response-mapping)).
> Webhooks need raw body access for signature verification, and their
> error handling logic differs (return 200 even on processing failures
> in some cases). It is acceptable to handle errors explicitly in webhook
> handlers.

#### Pattern: Supabase Database Webhook (Next.js)

Supabase can send webhooks when database events occur (INSERT, UPDATE,
DELETE). These use a simpler verification model based on a shared secret.

```ts
// app/api/webhooks/supabase/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { generateRequestId } from '@/lib/request-id';
import { logger } from '@/lib/logger';

const WEBHOOK_SECRET = process.env.SUPABASE_WEBHOOK_SECRET!;

// Supabase webhook payload schema
const supabaseWebhookSchema = z.object({
  type: z.enum(['INSERT', 'UPDATE', 'DELETE']),
  table: z.string(),
  schema: z.string(),
  record: z.record(z.unknown()).nullable(),
  old_record: z.record(z.unknown()).nullable(),
});

export async function POST(request: NextRequest) {
  const requestId = generateRequestId();

  // 1. Verify shared secret
  const authHeader = request.headers.get('authorization');
  if (authHeader !== `Bearer ${WEBHOOK_SECRET}`) {
    logger.warn('Supabase webhook unauthorized', { requestId });
    return NextResponse.json(
      { ok: false, error: { code: 'UNAUTHORIZED', message: 'Invalid secret' }, requestId },
      { status: 401 }
    );
  }

  // 2. Validate payload
  const body = await request.json();
  const parsed = supabaseWebhookSchema.safeParse(body);

  if (!parsed.success) {
    logger.warn('Supabase webhook invalid payload', { requestId });
    return NextResponse.json(
      { ok: false, error: { code: 'VALIDATION_ERROR', message: 'Invalid payload' }, requestId },
      { status: 400 }
    );
  }

  const { type, table, record, old_record } = parsed.data;

  // 3. Route by table and event type
  logger.info('Supabase webhook received', { requestId, type, table });

  try {
    if (table === 'orders' && type === 'UPDATE') {
      await handleOrderUpdate(record, old_record, requestId);
    }
    // ... other handlers
  } catch (error) {
    logger.error('Supabase webhook processing failed', {
      requestId, type, table,
      error: error instanceof Error ? error.message : String(error),
    });
  }

  return NextResponse.json(
    { ok: true, data: { received: true }, requestId },
    { status: 200 }
  );
}
```

### 12.2 Idempotency: Handling Duplicate Deliveries

Webhook providers retry failed deliveries. This means your handler
**will** receive the same event multiple times. If the handler is not
idempotent, duplicates cause real damage — double charges, duplicate
emails, incorrect state.

- **MUST** implement idempotency for all webhook handlers that produce
  side effects (database writes, payments, notifications)
- **SHOULD** use the provider's event ID as the idempotency key — every
  provider includes a unique event identifier:

  | Provider | Event ID Field |
  |----------|---------------|
  | Stripe | `event.id` (e.g., `evt_1MqLZaGswQrCE8...`) |
  | GitHub | `X-GitHub-Delivery` header |
  | Supabase | Not built-in — derive from record ID + event type |

- **SHOULD** store processed event IDs in a persistent store (database
  table or Redis) and check before processing:

  ```ts
  // src/services/webhook-service.ts
  async function processWebhookEvent(
    eventId: string,
    handler: () => Promise<void>
  ): Promise<{ processed: boolean }> {
    // Check if already processed
    const existing = await webhookEventRepository.findById(eventId);
    if (existing) {
      logger.info('Duplicate webhook event, skipping', { eventId });
      return { processed: false };
    }

    // Process the event
    await handler();

    // Mark as processed
    await webhookEventRepository.create({
      id: eventId,
      processedAt: new Date(),
    });

    return { processed: true };
  }
  ```

- **SHOULD** set a TTL on stored event IDs (e.g., 72 hours) — providers
  typically retry within a window, not indefinitely
- **MUST** return `200` for duplicate events — the provider considers
  non-200 as a delivery failure and will retry again

### 12.3 Retry Handling: When Processing Fails

When webhook processing fails, the decision of whether to return `200`
or `500` determines whether the provider retries.

```text
Processing failed — what do we return?
 │
 ├── Is the failure TRANSIENT? (database timeout, external API down)
 │    └── Return 500 → Provider retries automatically
 │         MUST ensure handler is idempotent (§12.2)
 │
 └── Is the failure PERMANENT? (invalid data, business rule violation)
      └── Return 200 → Prevent useless retries
           MUST log the failure for investigation
```

- **SHOULD** return `500` for transient failures to leverage the
  provider's built-in retry mechanism — but only if the handler is
  idempotent
- **SHOULD** return `200` for permanent failures (bad data, unhandled
  event types) to prevent infinite retry loops
- **MUST** log all processing failures with sufficient context for
  debugging — the event ID, event type, and error details
- **SHOULD** implement a dead letter queue or alerting for events that
  fail processing repeatedly — these need manual investigation
  (→ See [08-observability.md])

### 12.4 Outbound Webhooks: Sending Events

When your API needs to notify external consumers of events (e.g., an
order status change triggers a notification to a partner's system), you
are implementing outbound webhooks.

#### Design Rules

- **MUST** sign outbound webhook payloads with HMAC-SHA256 so consumers
  can verify authenticity:

  ```ts
  // src/lib/webhook-signer.ts
  import { createHmac } from 'crypto';

  export function signWebhookPayload(
    payload: string,
    secret: string
  ): string {
    return createHmac('sha256', secret)
      .update(payload)
      .digest('hex');
  }

  // Include signature in headers
  const signature = signWebhookPayload(
    JSON.stringify(payload),
    consumer.webhookSecret
  );

  await fetch(consumer.webhookUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Webhook-Signature': signature,
      'X-Webhook-Timestamp': Date.now().toString(),
    },
    body: JSON.stringify(payload),
  });
  ```

- **MUST** use the standard response envelope for webhook payloads to
  maintain consistency:

  ```json
  {
    "event": "order.status_changed",
    "timestamp": "2025-03-15T10:30:00.000Z",
    "data": {
      "orderId": "ord_abc123",
      "previousStatus": "pending",
      "newStatus": "confirmed"
    },
    "webhookId": "whk_xyz789"
  }
  ```

- **MUST** implement retry with exponential backoff for failed deliveries
  (consumer endpoint returns non-2xx or times out):

  ```text
  Attempt 1: immediate
  Attempt 2: after 1 minute
  Attempt 3: after 5 minutes
  Attempt 4: after 30 minutes
  Attempt 5: after 2 hours
  (give up after 5 attempts — alert operations team)
  ```

- **MUST** include a unique `webhookId` in every delivery so consumers
  can implement idempotency on their end
- **SHOULD** set a reasonable timeout for delivery attempts (5–10
  seconds) — do not wait indefinitely for a consumer endpoint to respond
- **SHOULD** allow consumers to register and manage their webhook URLs
  through the API (CRUD for webhook subscriptions)
- **SHOULD** include a timestamp in the webhook headers to allow
  consumers to reject stale deliveries (replay attack prevention)

### 12.5 Webhook Testing

Testing webhook integrations requires simulating provider calls and
verifying the full flow.

- **SHOULD** use the provider's CLI tools for local development:

  | Provider | Local Testing Tool |
  |----------|-------------------|
  | Stripe | `stripe listen --forward-to localhost:3000/api/webhooks/stripe` |
  | GitHub | Redeliver from the webhook settings page |
  | Supabase | Manual trigger via database INSERT/UPDATE |

- **SHOULD** write integration tests that simulate webhook deliveries
  with valid and invalid signatures:

  ```ts
  // __tests__/webhooks/stripe.test.ts
  import { describe, it, expect } from 'vitest';
  import { createMockStripeEvent } from '../helpers/stripe';

  describe('POST /api/webhooks/stripe', () => {
    it('rejects requests without a signature', async () => {
      const response = await fetch('/api/webhooks/stripe', {
        method: 'POST',
        body: JSON.stringify({ type: 'payment_intent.succeeded' }),
      });

      expect(response.status).toBe(401);
      const body = await response.json();
      expect(body.ok).toBe(false);
      expect(body.error.code).toBe('UNAUTHORIZED');
    });

    it('processes valid payment_intent.succeeded events', async () => {
      const { body, signature } = createMockStripeEvent(
        'payment_intent.succeeded',
        { amount: 5000, currency: 'eur' }
      );

      const response = await fetch('/api/webhooks/stripe', {
        method: 'POST',
        headers: { 'stripe-signature': signature },
        body,
      });

      expect(response.status).toBe(200);
      const result = await response.json();
      expect(result.ok).toBe(true);
      // Verify side effects (order updated, email sent, etc.)
    });

    it('handles duplicate events idempotently', async () => {
      const { body, signature } = createMockStripeEvent(
        'payment_intent.succeeded',
        { amount: 5000, currency: 'eur' }
      );

      // First delivery
      await fetch('/api/webhooks/stripe', {
        method: 'POST',
        headers: { 'stripe-signature': signature },
        body,
      });

      // Duplicate delivery — should not process again
      const response = await fetch('/api/webhooks/stripe', {
        method: 'POST',
        headers: { 'stripe-signature': signature },
        body,
      });

      expect(response.status).toBe(200);
      // Verify no duplicate side effects
    });
  });
  ```

- **MUST** test the idempotency mechanism — send the same event twice
  and verify that side effects only occur once
- **SHOULD** test with malformed payloads and invalid signatures to
  verify rejection behavior

---

## 13. API Testing Patterns

An API without tests is an API that breaks silently. Testing at the API
layer verifies that the **entire vertical slice** works — routing,
validation, authentication, service logic, error handling, and response
format — without the complexity of a full browser-based E2E test.

This section defines **what** to test and **how** to test at the API
layer. For the complete testing strategy (test pyramid, coverage targets,
CI integration, when to use each test type):
→ See [06-testing-strategy.md].

For the tooling choices (Vitest, Supertest):
→ See [02-technology-radar.md, Section 4.11 — Testing].

### 13.1 What to Test at the API Layer

API tests sit in the **integration test** tier of the test pyramid —
they exercise the route handler, middleware, validation, and service
layer together, typically with a real or test database.

```text
┌────────────────────────┐
│      E2E Tests         │  ← Browser/client simulation (Playwright)
│   (few, slow, costly)  │     → See [06-testing-strategy.md]
├────────────────────────┤
│   API Integration Tests│  ← THIS SECTION
│   (moderate, focused)  │     HTTP request → full stack → HTTP response
├────────────────────────┤
│     Unit Tests         │  ← Pure functions, services, utilities
│   (many, fast, cheap)  │     → See [06-testing-strategy.md]
└────────────────────────┘
```

#### What API Tests Verify

| Category | What to Test | Example |
|----------|-------------|---------|
| **Happy path** | Correct response for valid requests | `POST /api/users` with valid data → `201` + user in body |
| **Validation** | Rejection of invalid input | Missing required field → `400` + `fieldErrors` |
| **Authentication** | Protected endpoints require auth | No token → `401`; expired token → `401` |
| **Authorization** | Role and ownership enforcement | Regular user accessing admin endpoint → `403` (or `404`) |
| **Error handling** | Correct error codes and envelope | Duplicate email → `409` + `CONFLICT` code |
| **Pagination** | Correct meta, defaults, caps | `?pageSize=200` → capped to max, meta reflects actual values |
| **Edge cases** | Empty results, not found, concurrency | `GET /api/users/nonexistent` → `404` + standard envelope |
| **Response format** | Envelope consistency | Every response has `ok`, `requestId`, correct structure |

#### What NOT to Test at the API Layer

- **UI rendering** — that is E2E / component testing
- **External service internals** — mock them at the boundary
- **Database schema correctness** — that is migration testing
- **Business logic in isolation** — that is unit testing (test services
  directly, without HTTP)

### 13.2 Test Structure & Conventions

- **MUST** follow the **Arrange → Act → Assert** pattern in every test:

  ```ts
  it('creates a user and returns 201', async () => {
    // Arrange — prepare test data
    const input = {
      name: 'João Silva',
      email: 'joao@example.com',
      role: 'user',
    };

    // Act — make the HTTP request
    const response = await request(app)
      .post('/api/v1/users')
      .send(input)
      .set('Authorization', `Bearer ${adminToken}`);

    // Assert — verify the response
    expect(response.status).toBe(201);
    expect(response.body.ok).toBe(true);
    expect(response.body.data).toMatchObject({
      name: 'João Silva',
      email: 'joao@example.com',
      role: 'user',
    });
    expect(response.body.data.id).toBeDefined();
    expect(response.body.requestId).toBeDefined();
  });
  ```

- **MUST** test both the **status code** and the **response body** — a
  correct status code with a wrong body (or vice versa) is still a bug
- **MUST** verify the **envelope structure** (`ok`, `requestId`,
  `error.code`) — not just the data payload
- **SHOULD** use descriptive test names that state the expected behavior:

  ```ts
  // BAD — vague, does not describe the expectation
  it('should work')
  it('test POST users')

  // GOOD — states the scenario and expected outcome
  it('returns 201 with the created user when input is valid')
  it('returns 400 with fieldErrors when email is missing')
  it('returns 401 when no authorization header is provided')
  it('returns 404 when a regular user tries to access another user')
  ```

- **SHOULD** group tests by endpoint using `describe` blocks:

  ```ts
  describe('POST /api/v1/users', () => {
    describe('when input is valid', () => {
      it('returns 201 with the created user', async () => { ... });
      it('hashes the password before storing', async () => { ... });
      it('assigns the default role when none is specified', async () => { ... });
    });

    describe('when input is invalid', () => {
      it('returns 400 when email is missing', async () => { ... });
      it('returns 400 when email format is invalid', async () => { ... });
      it('returns 400 with multiple fieldErrors for multiple invalid fields', async () => { ... });
    });

    describe('when there is a conflict', () => {
      it('returns 409 when email is already registered', async () => { ... });
    });

    describe('when unauthenticated', () => {
      it('returns 401 when no token is provided', async () => { ... });
      it('returns 401 when token is expired', async () => { ... });
    });

    describe('when unauthorized', () => {
      it('returns 403 when a regular user tries to create an admin', async () => { ... });
    });
  });
  ```

### 13.3 Test Setup: Express with Supertest

Supertest allows sending HTTP requests to an Express app **without
starting a real server** — tests run fast and without port conflicts.

```ts
// src/app.ts — export the app without calling .listen()
import express from 'express';
import { userRoutes } from './routes/user-routes';
import { errorHandler } from './middleware/error-handler';
import { requestIdMiddleware } from './middleware/request-id';

const app = express();
app.use(express.json());
app.use(requestIdMiddleware);
app.use('/api/v1', userRoutes);
app.use(errorHandler);

export { app };
```

```ts
// __tests__/setup.ts
import { beforeAll, afterAll, beforeEach } from 'vitest';
import { app } from '../src/app';
import { db } from '../src/lib/database';
import { createTestUser, generateTestToken } from './helpers/auth';

// Test database setup
beforeAll(async () => {
  await db.migrate.latest();
});

beforeEach(async () => {
  await db.seed.run(); // Reset to known state
});

afterAll(async () => {
  await db.destroy();
});

// Reusable auth helpers
export async function getAdminToken(): Promise<string> {
  const admin = await createTestUser({ role: 'admin' });
  return generateTestToken(admin);
}

export async function getUserToken(): Promise<string> {
  const user = await createTestUser({ role: 'user' });
  return generateTestToken(user);
}
```

```ts
// __tests__/api/users.test.ts
import { describe, it, expect, beforeEach } from 'vitest';
import request from 'supertest';
import { app } from '../../src/app';
import { getAdminToken, getUserToken } from '../setup';

describe('POST /api/v1/users', () => {
  let adminToken: string;
  let userToken: string;

  beforeEach(async () => {
    adminToken = await getAdminToken();
    userToken = await getUserToken();
  });

  it('returns 201 with the created user when input is valid', async () => {
    const response = await request(app)
      .post('/api/v1/users')
      .send({
        name: 'Maria Santos',
        email: 'maria@example.com',
      })
      .set('Authorization', `Bearer ${adminToken}`);

    expect(response.status).toBe(201);
    expect(response.body).toMatchObject({
      ok: true,
      data: {
        name: 'Maria Santos',
        email: 'maria@example.com',
        role: 'user', // default role
      },
    });
    expect(response.body.data.id).toBeDefined();
    expect(response.body.requestId).toBeDefined();
  });

  it('returns 400 with fieldErrors when email is missing', async () => {
    const response = await request(app)
      .post('/api/v1/users')
      .send({ name: 'Maria Santos' })
      .set('Authorization', `Bearer ${adminToken}`);

    expect(response.status).toBe(400);
    expect(response.body).toMatchObject({
      ok: false,
      error: {
        code: 'VALIDATION_ERROR',
        message: 'Request validation failed',
      },
    });
    expect(response.body.error.fieldErrors).toHaveProperty('email');
    expect(response.body.requestId).toBeDefined();
  });

  it('returns 409 when email is already registered', async () => {
    // Arrange — create a user first
    await request(app)
      .post('/api/v1/users')
      .send({ name: 'João', email: 'duplicate@example.com' })
      .set('Authorization', `Bearer ${adminToken}`);

    // Act — try to create another with the same email
    const response = await request(app)
      .post('/api/v1/users')
      .send({ name: 'Maria', email: 'duplicate@example.com' })
      .set('Authorization', `Bearer ${adminToken}`);

    // Assert
    expect(response.status).toBe(409);
    expect(response.body.error.code).toBe('CONFLICT');
  });

  it('returns 401 when no token is provided', async () => {
    const response = await request(app)
      .post('/api/v1/users')
      .send({ name: 'Maria', email: 'maria@example.com' });

    expect(response.status).toBe(401);
    expect(response.body.error.code).toBe('UNAUTHORIZED');
  });

  it('returns 403 when a regular user tries to create users', async () => {
    const response = await request(app)
      .post('/api/v1/users')
      .send({ name: 'Maria', email: 'maria@example.com' })
      .set('Authorization', `Bearer ${userToken}`);

    expect(response.status).toBe(403);
    expect(response.body.error.code).toBe('FORBIDDEN');
  });
});
```

### 13.4 Test Setup: Next.js Route Handlers

Next.js Route Handlers do not plug into Supertest directly. The
recommended approach is to test the handler function with a mocked
`NextRequest`.

```ts
// __tests__/helpers/next-request.ts
import { NextRequest } from 'next/server';

export function createMockNextRequest(
  url: string,
  options: {
    method?: string;
    body?: unknown;
    headers?: Record<string, string>;
  } = {}
): NextRequest {
  const { method = 'GET', body, headers = {} } = options;

  const request = new NextRequest(new URL(url, 'http://localhost:3000'), {
    method,
    headers: new Headers(headers),
    ...(body ? { body: JSON.stringify(body) } : {}),
  });

  return request;
}
```

```ts
// __tests__/api/users.test.ts
import { describe, it, expect, beforeEach } from 'vitest';
import { POST } from '../../app/api/v1/users/route';
import { createMockNextRequest } from '../helpers/next-request';
import { generateTestToken, seedTestUser } from '../helpers/auth';

describe('POST /api/v1/users', () => {
  let adminToken: string;

  beforeEach(async () => {
    await seedTestDatabase();
    adminToken = await generateTestToken({ role: 'admin' });
  });

  it('returns 201 with the created user when input is valid', async () => {
    const request = createMockNextRequest('/api/v1/users', {
      method: 'POST',
      body: { name: 'Maria Santos', email: 'maria@example.com' },
      headers: { Authorization: `Bearer ${adminToken}` },
    });

    const response = await POST(request, { params: Promise.resolve({}) });
    const body = await response.json();

    expect(response.status).toBe(201);
    expect(body.ok).toBe(true);
    expect(body.data.name).toBe('Maria Santos');
    expect(body.requestId).toBeDefined();
  });

  it('returns 400 with fieldErrors when email is invalid', async () => {
    const request = createMockNextRequest('/api/v1/users', {
      method: 'POST',
      body: { name: 'Maria', email: 'not-an-email' },
      headers: { Authorization: `Bearer ${adminToken}` },
    });

    const response = await POST(request, { params: Promise.resolve({}) });
    const body = await response.json();

    expect(response.status).toBe(400);
    expect(body.ok).toBe(false);
    expect(body.error.code).toBe('VALIDATION_ERROR');
    expect(body.error.fieldErrors).toHaveProperty('email');
  });
});
```

### 13.5 Testing Checklist per Endpoint

Every new or modified endpoint **SHOULD** have tests covering these
categories. Use this as a review checklist.

| Category | Tests to Write | Priority |
|----------|---------------|----------|
| **Happy path** | Valid input → correct status code + response body | **MUST** |
| **Validation** | Missing fields, wrong types, out-of-range values → `400` + `fieldErrors` | **MUST** |
| **Authentication** | No token, invalid token, expired token → `401` | **MUST** |
| **Authorization** | Wrong role, wrong ownership → `403` or `404` | **MUST** |
| **Not found** | Non-existent resource → `404` | **MUST** |
| **Conflict** | Duplicate unique values, invalid state transitions → `409` | **SHOULD** |
| **Pagination** | Default values, max cap enforcement, empty results | **SHOULD** |
| **Envelope** | Every response has `ok`, `requestId`, correct structure | **SHOULD** |
| **Edge cases** | Empty strings, boundary values, special characters | **SHOULD** |
| **Idempotency** | Duplicate POST with idempotency key → same response | **MAY** |

- **MUST** test at minimum: happy path, validation, authentication,
  authorization, and not found — these cover the critical failure modes
- **SHOULD** test conflict and pagination for endpoints that support them
- **SHOULD** verify the response envelope structure in at least one test
  per endpoint — this catches regressions in the centralized error handler
- **MAY** test idempotency for endpoints that implement idempotency keys
  (→ See [Section 3.2](#32-idempotency))

### 13.6 Test Data & Isolation

- **MUST** isolate tests from each other — each test must start from a
  known state and not depend on the execution order or side effects of
  other tests:

  ```ts
  // Reset database to known state before each test
  beforeEach(async () => {
    await db.seed.run();
  });

  // OR use transactions that roll back after each test
  beforeEach(async () => {
    await db.raw('BEGIN');
  });

  afterEach(async () => {
    await db.raw('ROLLBACK');
  });
  ```

- **MUST** use **factory functions** or **seed data** for test fixtures
  — never hardcode IDs or rely on production data:

  ```ts
  // __tests__/helpers/factories.ts
  import { nanoid } from 'nanoid';

  export function buildUser(overrides: Partial<CreateUserInput> = {}) {
    return {
      name: `Test User ${nanoid(6)}`,
      email: `test-${nanoid(6)}@example.com`,
      role: 'user' as const,
      ...overrides,
    };
  }

  // Usage in tests
  const input = buildUser({ role: 'admin' });
  ```

- **MUST** mock external services (Stripe, email providers, external
  APIs) at the boundary — API tests should not make real HTTP calls to
  third parties:

  ```ts
  // Mock Stripe at the module level
  vi.mock('../src/lib/stripe', () => ({
    stripe: {
      paymentIntents: {
        create: vi.fn().mockResolvedValue({
          id: 'pi_mock_123',
          status: 'succeeded',
          amount: 5000,
        }),
      },
    },
  }));
  ```

- **SHOULD** use a **test database** that mirrors the production schema
  but contains only test data — never run tests against production or
  shared staging databases
- **SHOULD** clean up created resources after tests to prevent test
  pollution — prefer transaction rollback over manual cleanup

### 13.7 API Testing Anti-Patterns

| Anti-Pattern | Why It Is Wrong | Correct Alternative |
|---|---|---|
| Testing only the happy path | Bugs live in error paths, edge cases, and auth boundaries | Cover validation, auth, and error cases (§13.5 checklist) |
| Hardcoded test data and IDs | Fragile — breaks when seed data changes | Factory functions with random values |
| Tests that depend on execution order | Flaky — fails when run in isolation or parallel | Independent setup per test (`beforeEach`) |
| Testing implementation details | Breaks when code is refactored without behavior change | Test the HTTP contract (request → response) |
| No auth testing | Security vulnerabilities go undetected | Test every protected endpoint with and without valid auth |
| Real external API calls in tests | Slow, flaky, costs money (Stripe), fails offline | Mock external services at the boundary |
| Asserting only status code | Correct status with wrong body passes silently | Assert status code AND response body structure |
| Snapshot testing for API responses | Brittle — any new field or timestamp breaks the test | Assert specific fields with `toMatchObject` |

---

## 14. API Design Checklist

These checklists distill the rules from this document into quick,
actionable verification steps. Use them during design, code review,
and before release.

### 14.1 Pre-Implementation Checklist

Before writing any code for a new endpoint or API feature, verify
that the design decisions are sound.

#### Resource & URL Design

- [ ] Resources are modeled as **nouns**, not verbs
        (→ See [Section 2.2](#22-resource-naming-rules))
- [ ] URLs use **plural nouns** in **kebab-case**, all lowercase
- [ ] Nesting is limited to **2 levels maximum**
        (→ See [Section 2.3](#23-resource-hierarchy--nesting))
- [ ] Public-facing identifiers use **UUIDs or NanoIDs**, not
      sequential integers
        (→ See [Section 2.4](#24-resource-identifiers))
- [ ] Query parameters use **camelCase** and have consistent names
      across endpoints
        (→ See [Section 2.5](#25-query-parameters))

#### HTTP Semantics

- [ ] Correct **HTTP method** selected for the operation
        (→ See [Section 3.1](#31-http-methods))
- [ ] Expected **status codes** mapped for success and all failure
      modes (→ See [Section 3.4](#34-method--status-code-quick-reference))
- [ ] `POST` operations with side effects have an **idempotency
      strategy** defined
        (→ See [Section 3.2](#32-idempotency))

#### Request & Response

- [ ] **Response envelope** follows the standard format (`ok`, `data`,
      `error`, `requestId`)
        (→ See [Section 4.3](#43-standard-response-envelope))
- [ ] JSON fields use **camelCase**, dates use **ISO 8601 UTC**
        (→ See [Section 4.2](#42-json-conventions))
- [ ] **Request schema** (Zod) defined with appropriate types,
      constraints, and custom error messages
        (→ See [Section 6.2](#62-schema-design-with-zod))
- [ ] **Response schema** reviewed — no sensitive fields leaked
      (passwords, tokens, internal IDs)
        (→ See [Section 6.5](#65-shared-schemas-request--response--openapi))

#### Error Handling

- [ ] All expected failure modes mapped to **AppError subclasses**
      with stable error codes
        (→ See [Section 5.2](#52-apperror-class-hierarchy))
- [ ] **Validation errors** return `fieldErrors` for form integration
        (→ See [Section 5.1](#51-error-response-structure))
- [ ] 404 used instead of 403 for resources the caller should not
      know exist
        (→ See [Section 3.3](#33-status-codes))

#### Pagination & Filtering

- [ ] Collection endpoints have **pagination** with a capped
      `pageSize` (→ See [Section 7.2](#72-pagination-rules))
- [ ] Offset vs cursor strategy chosen based on the use case
        (→ See [Section 7.1](#71-pagination-strategies))
- [ ] `sortBy` restricted to a **whitelist** of allowed fields
        (→ See [Section 7.4](#74-sorting))
- [ ] **Default sort order** defined (`createdAt` desc recommended)

#### Security

- [ ] Endpoint **authentication** requirement defined (public vs
      protected) (→ See [Section 9.4](#94-public-vs-protected-endpoints))
- [ ] **Authorization** rules defined — role checks AND ownership
      checks where applicable
        (→ See [Section 9.3](#93-authorization-patterns))
- [ ] **Rate limiting** tier assigned (general, auth, or custom)
        (→ See [Section 10](#10-rate-limiting--abuse-prevention))
- [ ] Security review completed for sensitive operations
        (→ See [07-security-standards.md, Section 2 — Threat Modeling])

### 14.2 Pre-Release Checklist

Before merging or deploying an API change, verify that the
implementation meets the standards.

#### Implementation Quality

- [ ] Route handler is **thin** — validation, service call, response
      mapping only. No business logic.
        (→ See [Section 1.4](#14-thin-handlers-rich-services))
- [ ] Input validated with **Zod `.parse()`** at the boundary — body,
      query params, and path params
        (→ See [Section 6.3](#63-validating-different-input-sources))
- [ ] Error handling uses the **centralized error mapper** — no
      per-handler try/catch for error formatting
        (→ See [Section 5.4](#54-centralized-error-to-response-mapping))
- [ ] **`requestId`** included in every response and every log entry
        (→ See [Section 4.4](#44-request-id--traceability))
- [ ] String inputs have **`.max()` limits** to prevent payload abuse
- [ ] Array inputs have **`.max()` limits** to prevent batch abuse
- [ ] No **stack traces**, SQL errors, or internal paths exposed in
      error responses
        (→ See [07-security-standards.md, Section 1 — Fail Secure])

#### Testing

- [ ] **Happy path** tested — valid input returns correct status and
      response (→ See [Section 13.5](#135-testing-checklist-per-endpoint))
- [ ] **Validation** tested — invalid input returns `400` with
      `fieldErrors`
- [ ] **Authentication** tested — missing/invalid token returns `401`
- [ ] **Authorization** tested — wrong role/ownership returns `403`
      or `404`
- [ ] **Not found** tested — non-existent resource returns `404`
- [ ] **Envelope structure** verified — `ok`, `requestId`, `error.code`
      present in responses
- [ ] External services **mocked** — no real HTTP calls to Stripe,
      email providers, etc.
        (→ See [Section 13.6](#136-test-data--isolation))

#### Documentation

- [ ] Zod schemas registered in the **OpenAPI registry** for the new
      or modified endpoint
        (→ See [Section 11.2](#112-generating-openapi-from-zod))
- [ ] All request parameters, response fields, and error codes
      **documented** (→ See [Section 11.3](#113-what-to-document))
- [ ] Documentation endpoint **disabled in production**
        (→ See [Section 11.5](#115-documentation-security))

#### Versioning

- [ ] Change classified as **breaking or non-breaking**
        (→ See [Section 8.1](#81-breaking-vs-non-breaking-changes))
- [ ] If breaking: **new version or deprecation plan** in place
        (→ See [Section 8.3](#83-when-to-create-a-new-version))
- [ ] Published **error codes not changed or removed**
        (→ See [Section 5.3](#53-error-codes-catalogue))

#### Webhook Endpoints (If Applicable)

- [ ] **Signature verification** implemented before any processing
        (→ See [Section 12.1](#121-inbound-webhooks-receiving-events))
- [ ] **Idempotency** mechanism in place for duplicate deliveries
        (→ See [Section 12.2](#122-idempotency-handling-duplicate-deliveries))
- [ ] Handler returns `200` quickly — heavy processing is async
- [ ] Tested with **valid signatures, invalid signatures, and
      duplicate events**
        (→ See [Section 12.5](#125-webhook-testing))

### 14.3 Quick Reference: Common Mistakes

A fast-scan list of the most frequent API design mistakes caught
during code review, with direct links to the relevant standard.

| # | Mistake | Standard Reference |
|---|---------|-------------------|
| 1 | Verbs in URL (`POST /createUser`) | [§2.2 — Resource Naming](#22-resource-naming-rules) |
| 2 | `200 OK` with error in body | [§3.3 — Status Codes](#33-status-codes) |
| 3 | No response envelope (raw data or raw error) | [§4.3 — Response Envelope](#43-standard-response-envelope) |
| 4 | Missing `requestId` in response | [§4.4 — Request ID](#44-request-id--traceability) |
| 5 | Stack trace or SQL error in response | [§5.4 — Centralized Mapping](#54-centralized-error-to-response-mapping) |
| 6 | Manual `if/else` instead of Zod validation | [§6.1 — Validate at Boundary](#61-core-principle-validate-at-the-boundary) |
| 7 | Same schema for request and response | [§6.5 — Shared Schemas](#65-shared-schemas-request--response--openapi) |
| 8 | No `pageSize` cap on collection endpoints | [§7.2 — Pagination Rules](#72-pagination-rules) |
| 9 | Arbitrary column name in `sortBy` | [§7.4 — Sorting](#74-sorting) |
| 10 | Business logic in route handler | [§1.4 — Thin Handlers](#14-thin-handlers-rich-services) |
| 11 | Auth check in UI but not in API | [§9.3 — Authorization](#93-authorization-patterns) |
| 12 | No rate limiting on public endpoints | [§10 — Rate Limiting](#10-rate-limiting--abuse-prevention) |
| 13 | Webhook processed without signature check | [§12.1 — Inbound Webhooks](#121-inbound-webhooks-receiving-events) |
| 14 | Tests only cover happy path | [§13.5 — Testing Checklist](#135-testing-checklist-per-endpoint) |
| 15 | OpenAPI spec maintained manually alongside Zod | [§11.4 — Keeping Docs in Sync](#114-keeping-documentation-in-sync) |

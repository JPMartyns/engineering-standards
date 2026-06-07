# 📡 Observability Standards

> **Scope:** Practical guide for implementing logging, error tracking, monitoring,
> metrics, and alerting across all projects covered by these engineering standards.
>
> **Purpose:** The reference that answers "when something goes wrong in production,
> how do I know? And when something is slow or degrading, how do I detect it before
> users notice?" — ensuring every application is observable, debuggable, and
> monitored from day one.
>
> **Keywords:**
> - **MUST** = required (PR should be blocked if violated)
> - **SHOULD** = strongly recommended (requires justification to skip)
> - **MAY** = optional (case-by-case)

---

## 0. How to Use This Document

- This document defines **how to observe, monitor, and debug applications** —
  structured logging, error tracking, uptime monitoring, metrics, alerting,
  and audit trails.
- It does **not** define which observability tools to use (that lives in
  → See [02-technology-radar.md, § 3.15]) or the security rules around logging
  (that lives in → See [07-security-standards.md]). It references both heavily.
- Code examples use **TypeScript** with **Pino** (logging), **Sentry SDK**
  (error tracking), and **Next.js / Express.js** (frameworks), reflecting
  the Adopt choices in → See [02-technology-radar.md].
- The layering model assumed throughout is:
  `Route Handler / Controller → Service → Repository`
  (→ See [01-core-principles.md, § 6]).

> When observability requirements (detailed logging, error context) conflict
> with privacy or secret redaction rules, **security wins** —
> → See [07-security-standards.md] takes precedence. Never log sensitive data
> for the sake of debuggability.  

### Technology Versions

This document was written against the following versions. If you are using
significantly different versions, verify the API and configuration options
against official documentation before applying.

| Tool              | Version   | Role                         | Radar Status |
|-------------------|-----------|------------------------------|--------------|
| Pino              | 10.x      | Structured JSON logging      | ✅ Adopt     |
| pino-pretty       | 13.x      | Development log formatting   | ✅ Adopt     |
| pino-http         | 10.x      | HTTP request/response logging| ✅ Adopt     |
| @sentry/nextjs    | 10.x      | Error tracking + performance | ✅ Adopt     |
| @sentry/node      | 10.x      | Node.js error tracking       | ✅ Adopt     |
| UptimeRobot       | SaaS      | Uptime monitoring            | ✅ Adopt     |
| Axiom             | SaaS      | Log management + analytics   | 🔬 Trial     |
| Grafana           | —         | Metrics visualization        | 🔍 Assess    |
| Prometheus        | —         | Metrics collection           | 🔍 Assess    |

### Document Relationships

```text
08-observability.md (this document)
 ├── Derives from    → 01-core-principles.md (fail fast/loud, feedback loops)
 ├── Derives from    → 02-technology-radar.md (tool choices, evaluation)
 ├── Complements     → 07-security-standards.md (audit logging, PII rules, RGPD)
 ├── Complements     → 03-api-design.md (requestId, error envelope, 5xx logging)
 ├── Referenced by   → 05-frontend-standards.md (client-side error handling)
 ├── Referenced by   → 06-testing-strategy.md (performance testing, Web Vitals)
 └── Referenced by   → 09-devops-cicd.md (alerting integration, deploy markers)
```

### Boundary Definitions

Understanding where this document ends and others begin prevents duplication
and keeps each document focused.

| Topic                                    | This document (08)              | Other document                          |
|------------------------------------------|---------------------------------|-----------------------------------------|
| Pino is the Adopt logger                 | How to configure and use it     | → 02 defines why it is Adopt            |
| Log every 5xx with context               | Log schema and what to capture  | → 03 §5 defines the error envelope      |
| Never log PII or secrets                 | Redaction config and rules      | → 07 §A09 defines data protection rules |
| Monitor Supabase RLS failures            | Alert on auth/RLS errors        | → 04 §8 defines RLS policies            |
| Track client-side errors with Sentry     | Sentry integration patterns     | → 05 §8 defines error handling in UI    |
| Alert when error rate exceeds threshold  | Alerting strategy               | → 09 defines CI/CD pipeline integration |
| Use requestId for request tracing        | Propagation through the stack   | → 03 §4.4 defines requestId generation  |
| Audit state-changing operations          | Implementation patterns         | → 07 §A09, §5.3 defines what to audit   |
| Core Web Vitals in production            | Monitoring and alerting         | → 05 §10, → 06 §11 define measurement   |

### AI Agent Instructions

This document is designed to be consumed by AI coding agents (e.g., Claude
Code). When interpreting this document:

- **MUST**, **SHOULD**, and **MAY** are RFC 2119 keywords — treat MUST as non-negotiable constraints, SHOULD as strong defaults that require explicit justification to override, and MAY as contextual options.
- Cross-references (→ See [XX-document.md]) point to authoritative definitions — always defer to the referenced document for the full rule.
- When this document conflicts with [07-security-standards.md], the security document takes precedence.
- BAD/GOOD code examples are pattern-matching references — apply the principle behind the example, not just the literal code.
- Anti-pattern tables describe common mistakes — use them as negative examples when reviewing or generating code.
- Every logging statement, error report, and monitoring setup MUST follow the structured logging format and PII rules defined here.
- If generating code requires violating a MUST rule, the AI **MUST stop** and ask the human for permission before proceeding — never silently override a standard.
- **MUST NOT** over-engineer — always prefer the simplest solution that meets the stated requirements. Do not add abstractions, patterns, or infrastructure beyond what was explicitly requested (→ See [01-core-principles.md, §12]).
- When generating `catch` blocks, **MUST** use the structured logger (Pino) with `requestId` context — **NEVER** use `console.log`, `console.error`, or `console.warn` in application code.

---

## 1. Observability Philosophy

Observability is not a feature you bolt on after launch — it is a
**design requirement** that determines whether you can understand, debug,
and improve your application in production. A system without observability
is a system you are flying blind.

### 1.1 Why Observability Matters

Every application will eventually encounter unexpected behavior — a slow
query, a failed payment, a spike in error rates, a memory leak. The question
is not *if* these things will happen, but *how quickly you will know* and
*how much context you will have* to fix them.

Without observability:
- Bugs are reported by users, not by your systems
- "It works on my machine" is the default debugging posture
- Performance degrades silently until users leave
- Security incidents go undetected for days or weeks
- Post-mortems produce no actionable data

With observability:
- Errors surface immediately with full context
- Performance trends are visible before they become incidents
- Security anomalies trigger alerts, not lawsuits
- Every production issue has a trail that leads to the root cause

> **Principle:** Observability is the production feedback loop
> (→ See [01-core-principles.md, § 1.6 — Feedback Loops Matter]).
> Logging is the mechanism by which "fail loud" becomes actionable
> (→ See [01-core-principles.md, § 2.3 — Fail Fast, Fail Loud]).

### 1.2 The Three Pillars

Modern observability rests on three complementary data types. Each answers
different questions.

```text
┌─────────────────────────────────────────────────────────────────┐
│                     OBSERVABILITY                               │
│                                                                 │
│  ┌───────────┐     ┌───────────┐     ┌───────────┐              │
│  │   LOGS    │     │  METRICS  │     │  TRACES   │              │
│  │           │     │           │     │           │              │
│  │ What      │     │ How much  │     │ Where     │              │
│  │ happened? │     │ / how     │     │ did time  │              │
│  │           │     │ fast?     │     │ go?       │              │
│  └───────────┘     └───────────┘     └───────────┘              │
│                                                                 │
│  Events with       Numeric values     Request flow              │
│  context            over time          across layers            │
│  (structured JSON)  (counters,         (requestId               │
│                      gauges,           propagation)             │
│                      histograms)                                │
└─────────────────────────────────────────────────────────────────┘
```

**Logs** record discrete events with context — what happened, when, and to
whom. They are the foundation and the first pillar every project needs.

**Metrics** measure aggregate behavior over time — how many requests per
second, what is the p95 response time, how many active database connections.
They answer capacity and trend questions that individual logs cannot.

**Traces** follow a single request as it flows through multiple layers or
services. They answer "where did this request spend its time?" and are
essential for diagnosing latency in distributed systems.

For projects in this stack, the practical priority is:
1. **Logs first** — every project, from day one (Pino)
2. **Error tracking second** — every production project (Sentry)
3. **Metrics when needed** — when aggregate trends matter (Axiom, Grafana)
4. **Traces when services multiply** — when a single request crosses
   service boundaries (Sentry, OpenTelemetry)

### 1.3 Observability vs Monitoring

These terms are often used interchangeably, but they describe different
capabilities.

**Monitoring** is reactive — it answers known questions. "Is the server
up?" "Is the error rate above 5%?" You define the questions in advance
through alerts and dashboards.

**Observability** is proactive — it lets you ask *new* questions without
deploying new code. "Why did user X get a 500 error at 14:32?" "Which
endpoint got slower after the last deploy?" You can answer these questions
because the system produces rich, structured, queryable data.

- **MUST** treat monitoring (alerts + dashboards) as the **minimum**
- **SHOULD** design for observability (structured logs + correlation IDs +
  rich context) so that new questions can be answered without redeploying

### 1.4 The Cost of Flying Blind vs Over-Instrumenting

Observability has a cost — storage, network bandwidth, processing time,
and cognitive overhead. The goal is not to log everything, but to log
**the right things at the right level of detail**.

- **Under-instrumenting** means debugging production issues with guesswork,
  long resolution times, and frustrated users
- **Over-instrumenting** means excessive storage costs, slow log queries,
  alert fatigue, and developers who ignore monitoring because it is all noise

The pragmatic approach:
- **Start with the minimum viable observability** (→ See [Section 9])
- **Add instrumentation when a real need emerges** — not "just in case"
- **Review and prune** — if a log line or alert has never been useful,
  remove it

> This aligns with → See [01-core-principles.md, § 1.3 — Pragmatism Over Dogma]:
> start simple, add complexity only when measured need exists.

---

## 2. Structured Logging

Structured logging is the foundation of production observability. Instead of
free-form text strings (`console.log("user created")`), structured logs
produce machine-parseable JSON with consistent fields that log aggregation
tools can index, filter, and query.

### 2.1 Why Structured Logs

```text
// UNSTRUCTURED — human-readable but unsearchable
"User joao@example.com created successfully at 2025-03-15T10:30:00Z"

// STRUCTURED — machine-parseable, indexable, queryable
{
  "level": "info",
  "time": "2025-03-15T10:30:00.000Z",
  "requestId": "req_V1StGXR8_Z5jdHi6B",
  "msg": "User created",
  "userId": "f47ac10b",
  "email": "[Redacted]",
  "duration": 42
}
```

Unstructured logs become unusable the moment you have more than one server,
more than one developer, or more than a few hundred requests per minute.
You cannot `grep` your way through production — you need to query, filter,
aggregate, and correlate.

- **MUST** use structured JSON logging in all environments except local
  development
- **MUST** use Pino as the logging library for all Node.js applications
  (→ See [02-technology-radar.md, § 3.15 — Pino: Adopt])
- **MUST NOT** use `console.log`, `console.error`, or `console.warn` in
  production code — these produce unstructured output, lack consistent
  fields, and cannot be configured
- **MAY** use `pino-pretty` for human-readable output in local development
  only — it **MUST NOT** be used in production as it adds overhead and
  defeats the purpose of structured logging

### 2.2 Log Schema

Every log entry **MUST** include a consistent set of fields. This enables
log aggregation tools to index logs predictably and allows queries like
"show me all errors for requestId X" or "show me all logs from service Y
in the last hour."

#### Mandatory Fields

| Field       | Type     | Source      | Description                                          |
|-------------|----------|-------------|------------------------------------------------------|
| `level`     | string   | Pino        | Log severity: `error`, `warn`, `info`, `debug`       |
| `time`      | string   | Pino        | ISO 8601 timestamp in UTC                            |
| `msg`       | string   | Developer   | Human-readable description of the event              |
| `requestId` | string   | Middleware  | Correlation ID from → See [03-api-design.md, § 4.4]      |

#### Contextual Fields (added per-request or per-operation)

| Field       | Type     | When to Include                                       |
|-------------|----------|-------------------------------------------------------|
| `userId`    | string   | When the request is authenticated (after auth check)  |
| `method`    | string   | HTTP method (`GET`, `POST`, etc.)                     |
| `route`     | string   | API route pattern (e.g., `/api/users/:id`)            |
| `statusCode`| number   | HTTP response status code                             |
| `duration`  | number   | Request processing time in milliseconds               |
| `error`     | object   | Error details (for `error` and `warn` levels)         |
| `service`   | string   | Service or module name (useful in multi-service setups)|

#### Optional Fields (added when relevant)

| Field         | Type     | When to Include                                    |
|---------------|----------|----------------------------------------------------|
| `action`      | string   | Business action being performed (`createUser`)     |
| `resource`    | string   | Resource type being acted on (`user`, `order`)     |
| `resourceId`  | string   | Specific resource identifier                       |
| `ip`          | string   | Client IP (only when security-relevant)            |
| `userAgent`   | string   | Client user agent (only when debugging-relevant)   |
| `query`       | string   | Database query identifier (never the raw SQL)      |
| `cacheHit`    | boolean  | Whether a cache was hit                            |

### 2.3 Log Levels

Each level has a specific semantic meaning. Using the wrong level creates
noise (logging normal events as `warn`) or hides problems (logging failures
as `info`).

| Level   | Numeric | When to Use                                           | Example                                               |
|---------|---------|-------------------------------------------------------|-------------------------------------------------------|
| `error` | 50      | Something **failed** and needs human attention. The operation could not be completed. | Database connection lost, payment processing failed, unhandled exception |
| `warn`  | 40      | Something **unexpected** happened but the application **recovered** or can continue. | Retry succeeded after failure, deprecated API usage detected, rate limit approaching |
| `info`  | 30      | **Business events** worth tracking — normal operations that have business value. | User created, order completed, payment processed, job finished |
| `debug` | 20      | **Technical detail** useful only during development or active debugging. Never enable in production by default. | Query parameters, intermediate state, cache key computed |

**Rules:**

- **MUST** use `error` only for conditions that require investigation or
  action — if the application handled the situation gracefully, use `warn`
- **MUST** use `info` for business-significant events — not for routine
  technical operations (e.g., "database connected" is `info` at startup,
  but not on every query)
- **MUST** use `debug` for development-time detail — `debug` level
  **SHOULD** be disabled in production by default
- **MUST NOT** use `error` for expected failures like validation errors or
  "not found" responses — these are normal application behavior, not errors
  (use `warn` for suspicious patterns, `info` for routine 4xx responses)
- **SHOULD** configure log levels via environment variables so they can be
  changed without redeployment:

  ```ts
  // Production: info and above
  // Staging: debug and above (for troubleshooting)
  // Development: debug and above (with pino-pretty)
  const LOG_LEVEL = process.env.LOG_LEVEL || 'info';
  ```

### 2.4 Pino Configuration

This is the baseline Pino configuration that every project **SHOULD** start
from. It includes structured output, ISO timestamps, sensitive data
redaction, and environment-aware formatting.

```ts
// src/lib/logger.ts
import pino from 'pino';

const isProduction = process.env.NODE_ENV === 'production';
const isDevelopment = process.env.NODE_ENV === 'development';

export const logger = pino({
  // Log level from environment, default to 'info' in production
  level: process.env.LOG_LEVEL || (isProduction ? 'info' : 'debug'),

  // ISO 8601 timestamps instead of Unix epoch milliseconds
  timestamp: pino.stdTimeFunctions.isoTime,

  // Redact sensitive fields — MUST include at minimum these paths
  // → See [07-security-standards.md, § A09] for data protection rules
  redact: {
    paths: [
      'password',
      'token',
      'accessToken',
      'refreshToken',
      'authorization',
      'cookie',
      'creditCard',
      'ssn',
      '*.password',
      '*.token',
      '*.accessToken',
      '*.refreshToken',
      'req.headers.authorization',
      'req.headers.cookie',
    ],
    censor: '[Redacted]',
  },

  // Standard serializers for consistent error and request formatting
  serializers: {
    err: pino.stdSerializers.err,
    req: pino.stdSerializers.req,
    res: pino.stdSerializers.res,
  },

  // Use pino-pretty only in development — never in production
  ...(isDevelopment && {
    transport: {
      target: 'pino-pretty',
      options: {
        colorize: true,
        translateTime: 'SYS:HH:MM:ss.l',
        ignore: 'pid,hostname',
      },
    },
  }),
});
```

**Rules:**

- **MUST** configure `redact` with at minimum the paths listed above —
  add project-specific sensitive fields as needed
- **MUST** use `pino.stdTimeFunctions.isoTime` for human-readable,
  timezone-unambiguous timestamps
- **MUST NOT** use `pino-pretty` transport in production — it adds
  significant overhead and produces non-JSON output
- **SHOULD** use `pino.stdSerializers` for `err`, `req`, and `res` to
  ensure consistent formatting
- **SHOULD** set the default log level to `info` in production and `debug`
  in development
- **MAY** add a `name` property to identify the service in multi-service
  environments:

  ```ts
  const logger = pino({
    name: 'car-dealership-api',
    // ... rest of config
  });
  ```

### 2.5 Request-Scoped Logging

Every log entry produced during a request **MUST** include the `requestId`
for correlation. Pino's child logger pattern makes this efficient — create
a child logger with the `requestId` bound, and every subsequent log call
automatically includes it.

```ts
// src/middleware/request-logger.ts (Express.js)
import { Request, Response, NextFunction } from 'express';
import { nanoid } from 'nanoid';
import { logger } from '../lib/logger';

export function requestLogger(
  req: Request,
  _res: Response,
  next: NextFunction
): void {
  const requestId =
    (req.headers['x-request-id'] as string) || `req_${nanoid(21)}`;

  // Create a child logger with request context bound
  req.log = logger.child({
    requestId,
    method: req.method,
    route: req.originalUrl,
  });

  // Attach requestId to the request for downstream use
  req.requestId = requestId;

  req.log.info('Request received');
  next();
}
```

```ts
// src/lib/api-handler.ts (Next.js Route Handlers)
import { NextRequest, NextResponse } from 'next/server';
import { nanoid } from 'nanoid';
import { logger } from '../lib/logger';

type RouteContext = {
  params: Record<string, string>;
  requestId: string;
  log: pino.Logger;
};

export function apiHandler(
  handler: (req: NextRequest, ctx: RouteContext) => Promise<NextResponse>
) {
  return async (
    request: NextRequest,
    context: { params: Promise<Record<string, string>> }
  ) => {
    const requestId =
      request.headers.get('x-request-id') || `req_${nanoid(21)}`;
    const params = await context.params;

    // Child logger with request context
    const log = logger.child({
      requestId,
      method: request.method,
      route: request.nextUrl.pathname,
    });

    log.info('Request received');

    try {
      return await handler(request, { params, requestId, log });
    } catch (error) {
      // Error handling — see § 3 for Sentry integration
      // → See [03-api-design.md, § 5.4] for centralized error mapping
      log.error({ err: error }, 'Unhandled error');
      throw error;
    }
  };
}
```

**Rules:**

- **MUST** create a child logger per request with `requestId` bound —
  never pass `requestId` manually to every log call
- **MUST** propagate the child logger (or `requestId`) to service and
  repository layers so that all log entries for a request are correlated
- **SHOULD** accept an incoming `X-Request-ID` header and use it if present
  (→ See [03-api-design.md, § 4.4])
- **SHOULD** bind `method` and `route` to the child logger for filtering
- **SHOULD** add `userId` to the child logger after authentication succeeds:

  ```ts
  // After auth middleware verifies the user
  req.log = req.log.child({ userId: session.user.id });
  ```

### 2.6 Context Enrichment by Layer

Different application layers produce different types of log events. Each
layer **SHOULD** log events relevant to its responsibility without
duplicating what other layers log.

```text
┌──────────────────────────────────────────────────────────┐
│ Route Handler / Controller                               │
│  → Request received (info)                               │
│  → Request completed with status (info)                  │
│  → Validation failure (warn, if suspicious pattern)      │
│  → Unhandled error caught (error)                        │
├──────────────────────────────────────────────────────────┤
│ Service Layer                                            │
│  → Business operation started (debug)                    │
│  → Business event completed (info): "User created"       │
│  → Business rule violation (warn): "Insufficient balance"│
│  → External service call failed (error)                  │
├──────────────────────────────────────────────────────────┤
│ Repository / Data Access                                 │
│  → Slow query detected (warn): duration > threshold      │
│  → Connection pool exhausted (error)                     │
│  → Cache hit/miss (debug)                                │
│  → Migration applied (info, at startup)                  │
└──────────────────────────────────────────────────────────┘
```

- **MUST** log at the handler level: request received, request completed
  (with status code and duration), and unhandled errors
- **SHOULD** log at the service level: business events (`info`) and
  business rule violations (`warn`)
- **SHOULD** log at the repository level: slow queries (`warn`) and
  connection problems (`error`)
- **MUST NOT** log the same event at multiple layers — if the handler logs
  the error, the service should not also log it. The exception is when
  each layer adds *different* context.

### 2.7 What to Log

Not everything is worth logging. Log entries should either help you
**debug a problem**, **track a business event**, or **detect a trend**.

#### Business Events (level: `info`)

These are the events that answer "what is the application doing?"

- User registered, user logged in, user deleted
- Order created, order completed, order cancelled
- Payment processed, payment failed, refund issued
- Scheduled job started, scheduled job completed
- Email sent, notification delivered

#### Technical Events (level: `info` at startup, `debug` during runtime)

These are the events that answer "is the system healthy?"

- Application started (with version, environment, config summary)
- Application shutting down (graceful shutdown initiated)
- Database connection established
- Cache connection established
- External service connection verified

#### Performance Events (level: `warn`)

These are the events that answer "is something getting slow?"

- Request exceeded duration threshold (e.g., > 2000ms)
- Database query exceeded duration threshold (e.g., > 500ms)
- Memory usage exceeded threshold (e.g., > 80% heap)
- Connection pool utilization high (e.g., > 80% active connections)

#### AI / Agent Events (level: `info`; `warn` on budget/limit)

When the system uses an LLM or agent, log the operational signal — never the raw content:

- LLM call completed (model, tokens in / out, cost, latency, requestId) — token cost is a first-class metric, not an afterthought
- Agent step / tool call (agent task id, step number, tool name, result status) — span-level, so a trajectory can be reconstructed
- Agent budget / step ceiling exceeded (`agent.budget.exceeded`) — surfaced for alerting
- Agent side-effecting actions go to the **audit log**, not the application log (`agent.action.*` → §7.3)

> *What* to trace in an AI pipeline is defined by → See [12-ai-engineering.md, §5.7, §6.3, §6.8].
> The `agent.*` event taxonomy is owned by → See [07-security-standards.md, §15]. This document
> owns the *how* — structured fields, span correlation, metrics. Never log raw prompts/completions
> with PII (§2.8).

### 2.8 What NOT to Log

Logging the wrong data creates security vulnerabilities, compliance
violations, and noise.

#### Sensitive Data — MUST NOT Log

These rules are non-negotiable and align with
→ See [07-security-standards.md, § A09]:

- **MUST NOT** log passwords (even failed attempt values)
- **MUST NOT** log authentication tokens (JWT, API keys, session IDs) —
  log only the last 4 characters if identification is needed: `...a1b2`
- **MUST NOT** log credit card numbers, CVVs, or bank account numbers
- **MUST NOT** log personally identifiable information (PII) beyond what
  is strictly necessary for debugging — configure Pino's `redact` option
  as the safety net
- **MUST NOT** log full request/response bodies that may contain user data —
  log only the fields needed for debugging
- **MUST NOT** log database query parameters that contain user data — log
  the query identifier or pattern, not the values
- **MUST NOT** log raw LLM prompts or completions when they may contain
  personal data — prompts and model outputs are data flows like any other.
  Redact PII or log only metadata (model, token counts, latency, trace id).
  → See [07-security-standards.md, § 14]; [12-ai-engineering.md, §7.2]

> **RGPD Compliance:** Under RGPD (the EU regulation applicable in Portugal),
> personal data in logs is still personal data. If you log a user's email
> address, that log entry is subject to data retention rules, right to
> erasure requests, and breach notification requirements.
> → See [07-security-standards.md, § 14 — Data Protection & RGPD] for the
> full compliance framework.

#### Noise — SHOULD NOT Log

- Health check requests (from UptimeRobot or load balancers) — these
  generate massive volumes with no debugging value. Filter them in the
  HTTP logging middleware.
- Successful authentication token validation (routine, high-volume)
- Individual cache hits in tight loops
- Routine database query execution (log only slow queries)

#### Redaction Configuration

Pino's built-in `redact` option is the **safety net** — it ensures that
even if a developer accidentally passes sensitive data to a log call, it
will be censored in the output.

```ts
// Extended redaction for projects handling user data
const logger = pino({
  redact: {
    paths: [
      // Authentication
      'password',
      '*.password',
      'token',
      '*.token',
      'accessToken',
      '*.accessToken',
      'refreshToken',
      '*.refreshToken',

      // HTTP headers
      'req.headers.authorization',
      'req.headers.cookie',
      'req.headers["x-api-key"]',

      // PII
      'email',
      '*.email',
      'phone',
      '*.phone',
      'address',
      '*.address',
      'nif',
      '*.nif',
      'creditCard',
      '*.creditCard',

      // Database
      'connectionString',
      '*.connectionString',
      'databaseUrl',
      '*.databaseUrl',
    ],
    censor: '[Redacted]',
  },
});
```

- **MUST** configure redaction at logger initialization — not at individual
  log call sites
- **MUST** include authentication tokens, passwords, and PII fields in the
  redaction paths
- **SHOULD** review redaction paths when adding new features that handle
  sensitive data
- **SHOULD** use the `remove: true` option instead of `censor` for fields
  that should not appear at all (e.g., full request bodies):

  ```ts
  redact: {
    paths: ['req.body'],
    remove: true, // field is stripped entirely, not replaced
  }
  ```

### 2.9 Anti-Patterns

| Anti-Pattern | Why It Is Wrong | What to Do Instead |
|---|---|---|
| `console.log` in production | Unstructured, no levels, no context, no redaction | Use Pino with structured fields |
| Logging full request/response bodies | PII exposure, massive log volume, RGPD violation | Log only relevant fields (method, route, status, duration) |
| Using `error` level for 4xx responses | Creates noise and alert fatigue — 404 and 400 are normal | Use `info` for routine 4xx, `warn` for suspicious patterns |
| Passing `requestId` manually to every log call | Error-prone, verbose, inconsistent | Use Pino child loggers with `requestId` bound |
| Logging the same error at every layer | Duplicate entries, wastes storage, confuses analysis | Log at the layer that handles the error, not every layer it passes through |
| Logging secrets "temporarily for debugging" | Secrets in logs persist in log storage and backups | Use Pino redaction; never log secrets, not even temporarily |
| Enabling `debug` level in production permanently | Massive log volume, high storage cost, slow queries | Use `info` in production; enable `debug` temporarily via env var when investigating |
| Logging inside tight loops | Generates millions of entries, degrades application performance | Log aggregated results or use counters/metrics instead |

---

## 3. Error Tracking & Monitoring

Error tracking transforms invisible production failures into actionable
issues with full context. While structured logging captures the *what*,
error tracking captures the *why* — stack traces, breadcrumbs, user
context, and the exact sequence of events that led to the failure.

### 3.1 Sentry Integration

Sentry is the Adopt-tier error tracking platform
(→ See [02-technology-radar.md, § 3.15]). It captures runtime errors,
unhandled exceptions, and performance data from both frontend and backend.

The Sentry Next.js SDK (v10.x) provides unified instrumentation across all
Next.js runtime environments — client, server, and edge — through a single
package (`@sentry/nextjs`). It uses OpenTelemetry under the hood for
server-side tracing.

#### Setup Architecture

```text
┌──────────────────────────────────────────────────┐
│ Next.js Application                              │
│                                                  │
│  instrumentation-client.ts  → Browser SDK init   │
│  sentry.server.config.ts   → Node.js SDK init    │
│  sentry.edge.config.ts     → Edge SDK init       │
│  instrumentation.ts        → Registers configs   │
│  next.config.ts            → withSentryConfig()  │
│  global-error.tsx          → React error boundary│
│                                                  │
│  All environments share the same DSN but may     │
│  have different sample rates and integrations.   │
└──────────────────────────────────────────────────┘
```

#### Configuration Baseline

```ts
// instrumentation-client.ts (Browser — Client Components)
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,

  // Environment tag — matches deployment target
  environment: process.env.NEXT_PUBLIC_APP_ENV || 'development',

  // Error sampling: capture 100% of errors
  // Performance sampling: capture 10-20% of transactions
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.1 : 1.0,

  // Session Replay — captures user interactions leading to errors
  replaysSessionSampleRate: 0.1,  // 10% of normal sessions
  replaysOnErrorSampleRate: 1.0,  // 100% of error sessions

  integrations: [
    Sentry.replayIntegration(),
  ],
});
```

```ts
// sentry.server.config.ts (Node.js — Server Components, API Routes)
import * as Sentry from '@sentry/nextjs';

Sentry.init({
  dsn: process.env.NEXT_PUBLIC_SENTRY_DSN,
  environment: process.env.NEXT_PUBLIC_APP_ENV || 'development',

  // Server-side sample rates
  tracesSampleRate: process.env.NODE_ENV === 'production' ? 0.2 : 1.0,
});
```

```ts
// instrumentation.ts (Next.js instrumentation hook)
import * as Sentry from '@sentry/nextjs';

export async function register() {
  if (process.env.NEXT_RUNTIME === 'nodejs') {
    await import('./sentry.server.config');
  }

  if (process.env.NEXT_RUNTIME === 'edge') {
    await import('./sentry.edge.config');
  }
}

// Capture server-side rendering errors automatically
export const onRequestError = Sentry.captureRequestError;
```

```ts
// next.config.ts — Source maps and build integration
import type { NextConfig } from 'next';
import { withSentryConfig } from '@sentry/nextjs';

const nextConfig: NextConfig = {
  // ... existing Next.js configuration
};

export default withSentryConfig(nextConfig, {
  org: process.env.SENTRY_ORG,
  project: process.env.SENTRY_PROJECT,

  // Auth token for source map uploads — MUST be in CI/CD env vars
  // MUST NOT be committed to version control
  authToken: process.env.SENTRY_AUTH_TOKEN,

  // Upload wider set of source maps for readable stack traces
  widenClientFileUpload: true,

  // Route Sentry events through the server to avoid ad blockers
  tunnelRoute: '/monitoring',

  // Delete client source maps after upload — security best practice
  deleteSourcemapsAfterUpload: true,

  // Only print upload logs in CI
  silent: !process.env.CI,
});
```

**Rules:**

- **MUST** install `@sentry/nextjs` (or `@sentry/node` for standalone
  Node.js) in every production application — error tracking is not optional
- **MUST** configure source map uploads via `authToken` in CI/CD — without
  source maps, stack traces are unreadable minified code
- **MUST** delete client-side source maps after upload
  (`deleteSourcemapsAfterUpload: true`) — source maps expose your original
  source code to anyone who finds them
- **MUST NOT** commit `SENTRY_AUTH_TOKEN` to version control
  (→ See [07-security-standards.md, § 7 — Secrets Management])
- **MUST NOT** send PII to Sentry — configure data scrubbing rules in
  Sentry project settings
  (→ See [07-security-standards.md, § 14])
- **SHOULD** use `tunnelRoute` to route Sentry events through your server,
  avoiding ad blocker interference
- **SHOULD** set `tracesSampleRate` to 10-20% in production to control
  costs while maintaining visibility
- **SHOULD** configure `environment` tags to separate production, staging,
  and development data
- **MAY** disable Sentry in development environments to reduce noise —
  only enable when actively debugging

### 3.2 Error Classification

Not all errors are equal. Classifying errors correctly determines how they
are logged, tracked, and alerted on.

```text
                      ┌─────────────┐
                      │   Error     │
                      └──────┬──────┘
                             │
               ┌─────────────┼─────────────┐
               │                           │
        ┌──────▼──────┐            ┌───────▼──────┐
        │  Expected   │            │  Unexpected  │
        │  (AppError) │            │  (unhandled) │
        └──────┬──────┘            └───────┬──────┘
               │                           │
    ┌──────────┼──────────┐                │
    │                     │                │
┌───▼────┐         ┌──────▼────┐   ┌───────▼────────┐
│ Client │         │ Business  │   │ System failure │
│ error  │         │ rule      │   │ (DB down, OOM, │
│ (4xx)  │         │ violation │   │  unhandled exc)│
│        │         │ (422)     │   │                │
│ Log:   │         │           │   │ Log: error     │
│ info/  │         │ Log: warn │   │ Sentry: YES    │
│ warn   │         │           │   │ Alert: YES     │
│ Sentry:│         │ Sentry:   │   │                │
│ NO     │         │ NO*       │   │                │
└────────┘         └───────────┘   └────────────────┘
```

- **Expected errors** are part of normal application behavior — validation
  failures, not-found responses, business rule violations. They use the
  `AppError` class hierarchy (→ See [03-api-design.md, § 5.2]).
- **Unexpected errors** are bugs, infrastructure failures, or conditions
  the developer did not anticipate. These **MUST** go to Sentry.

**Rules:**

- **MUST** send all unexpected/unhandled errors to Sentry — these are the
  errors that need investigation
- **MUST NOT** send expected errors (4xx responses) to Sentry by default —
  they create noise and inflate error counts
- **SHOULD** use Sentry's `beforeSend` callback to filter known expected
  errors if they are accidentally captured:

  ```ts
  Sentry.init({
    beforeSend(event) {
      // Do not send expected AppErrors to Sentry
      const errorCode = event.extra?.errorCode as string;
      if (['NOT_FOUND', 'VALIDATION_ERROR', 'FORBIDDEN'].includes(errorCode)) {
        return null; // Drop the event
      }
      return event;
    },
  });
  ```

- **MAY** send business rule violations to Sentry if they occur at an
  unexpectedly high rate — this is an alerting decision, not a logging
  decision (→ See [Section 8])

### 3.3 Error Context Enrichment

The difference between a useful Sentry issue and a useless one is context.
Every error sent to Sentry **SHOULD** include enough context to understand
what happened without accessing the server.

```ts
// Setting user context after authentication
Sentry.setUser({
  id: session.user.id,
  // MUST NOT include email or PII unless Sentry data scrubbing is configured
});

// Setting tags for filtering in the Sentry dashboard
Sentry.setTag('transaction_type', 'payment');
Sentry.setTag('api_version', 'v1');

// Adding breadcrumbs for the timeline of events leading to the error
Sentry.addBreadcrumb({
  category: 'payment',
  message: 'Payment initiated for order',
  data: { orderId: order.id, amount: order.total },
  level: 'info',
});
```

**Rules:**

- **MUST** set user context (`Sentry.setUser`) after authentication with
  at minimum the user ID — this enables "show me all errors affecting
  user X"
- **MUST NOT** include email, name, or other PII in Sentry user context
  unless data scrubbing is configured in Sentry project settings
- **SHOULD** use `Sentry.setTag` for high-cardinality filtering dimensions
  (e.g., plan type, feature flag, API version)
- **SHOULD** add breadcrumbs for key business operations that precede
  potential errors (payment flows, multi-step forms, data migrations)
- **SHOULD** include `requestId` in error context so Sentry issues can be
  correlated with server-side logs:

  ```ts
  Sentry.setContext('request', { requestId });
  ```

### 3.4 Source Maps

Without source maps, Sentry stack traces show minified code like
`a.js:1:4523` instead of `src/services/payment.ts:42:handlePayment`.
Source maps are **non-negotiable** for production error tracking.

- **MUST** upload source maps to Sentry during the CI/CD build process
  using `withSentryConfig` (Next.js) or `@sentry/cli` (standalone)
- **MUST** set `SENTRY_AUTH_TOKEN` as a CI/CD environment variable — never
  in `.env` files committed to the repository
- **MUST** delete client-side source maps from the production build after
  upload — source maps contain your original source code and **MUST NOT**
  be publicly accessible
- **SHOULD** verify source maps are working by triggering a test error
  after each deploy and checking that the stack trace shows original
  file names and line numbers

### 3.5 Release Tracking

Release tracking connects errors to specific deployments, enabling you to
answer "did this error start with the latest deploy?"

```ts
// Set via environment variable during build
Sentry.init({
  release: process.env.SENTRY_RELEASE || process.env.VERCEL_GIT_COMMIT_SHA,
  // ...
});
```

- **SHOULD** configure release tracking with a unique identifier per deploy
  (Git commit SHA or a version string)
- **SHOULD** create deploy markers in Sentry to visualize when releases
  were deployed to each environment
- **MAY** use Sentry's release health to monitor crash-free session rates
  after each deploy

### 3.6 Frontend Error Tracking

Client-side errors require special handling because they occur in the
user's browser, outside your direct control.

React Error Boundaries (→ See [05-frontend-standards.md, § 8.1]) catch
rendering errors and display fallback UI. When combined with Sentry, every
boundary-caught error is automatically reported with the component stack
trace.

```tsx
// app/global-error.tsx — Catches root layout errors
'use client';

import * as Sentry from '@sentry/nextjs';
import { useEffect } from 'react';

export default function GlobalError({
  error,
}: {
  error: Error & { digest?: string };
}) {
  useEffect(() => {
    Sentry.captureException(error);
  }, [error]);

  return (
    <html>
      <body>
        <h1>Something went wrong</h1>
      </body>
    </html>
  );
}
```

- **MUST** implement `global-error.tsx` to catch root layout errors and
  report them to Sentry
- **MUST** implement segment-level `error.tsx` files for key routes
  (dashboard, checkout, admin)
  (→ See [05-frontend-standards.md, § 8.2])
- **SHOULD** configure Session Replay (`replaysOnErrorSampleRate: 1.0`) to
  capture the user's interaction timeline leading to errors
- **SHOULD** track `onRouterTransitionStart` for client-side navigation
  performance monitoring

### 3.7 Sentry Logs (Awareness)

As of Sentry SDK v10.x, Sentry supports **structured logging** — the
ability to send application logs directly to Sentry alongside errors and
traces. This is a new capability that unifies logs, errors, and
performance data in a single platform.

**Current recommendation:** Continue using **Pino for application logging**
and **Sentry for error tracking**. Sentry Logs is an emerging feature
worth evaluating, but Pino remains the standard for high-volume,
structured application logging due to its performance characteristics
and transport flexibility.

- **MAY** evaluate Sentry Logs for projects where having logs and errors
  in the same dashboard provides significant debugging value
- **MUST** continue using Pino as the primary application logger regardless
  of Sentry Logs adoption — Pino's redaction, performance, and transport
  ecosystem are more mature for general-purpose logging

### 3.8 Anti-Patterns

| Anti-Pattern | Why It Is Wrong | What to Do Instead |
|---|---|---|
| Sending all errors (including 4xx) to Sentry | Inflates error counts, creates noise, hides real problems | Filter expected errors with `beforeSend`; only send unexpected errors |
| No source maps in production | Stack traces are unreadable minified code — useless for debugging | Upload source maps in CI/CD, delete after upload |
| Leaving source maps publicly accessible | Exposes original source code, intellectual property, and potential vulnerabilities | Set `deleteSourcemapsAfterUpload: true` |
| Setting `tracesSampleRate: 1.0` in production | Sends 100% of transactions — excessive cost and bandwidth | Use 0.1–0.2 (10-20%) in production |
| Not setting user context | "An error occurred" with no information about who was affected | Set `Sentry.setUser({ id })` after authentication |
| Logging sensitive data in breadcrumbs | PII in breadcrumbs is sent to Sentry — external service | Include only non-sensitive identifiers (IDs, not emails) |
| Using Sentry as the application logger | Sentry is for errors and performance, not for `info`/`debug` logs | Use Pino for logging, Sentry for error tracking |
| Not verifying source maps after deploy | Broken source maps mean unreadable errors for the entire release | Trigger a test error after each deploy; check Sentry |

---

## 4. Request Tracing

Request tracing follows a single request as it flows through the entire
application stack — from the route handler, through the service layer, to
the database query, and back to the client. The `requestId` is the key
that ties everything together.

### 4.1 requestId as the Correlation Key

The `requestId` is generated at the entry point of every request and
included in every log entry, every Sentry event, and the API response.
When a user reports a problem, the `requestId` is the key that unlocks the
complete server-side story.

> The `requestId` generation and response envelope are defined in
> → See [03-api-design.md, § 4.4]. This section focuses on **propagation**
> through the application stack for observability purposes.

```text
Client request
    │
    ▼
┌──────────────────────────────────────────────────────┐
│ Route Handler / Controller                           │
│  → requestId generated or accepted from X-Request-ID │
│  → child logger created with { requestId }           │
│  → Sentry context set with requestId                 │
├──────────────────────────────────────────────────────┤
│ Service Layer                                        │
│  → receives requestId (via child logger or parameter)│
│  → all log calls automatically include requestId     │
├──────────────────────────────────────────────────────┤
│ Repository / Data Access                             │
│  → receives requestId for slow query logging         │
│  → requestId appears in database query comments (opt)│
├──────────────────────────────────────────────────────┤
│ Response                                             │
│  → requestId returned in response envelope           │
│  → requestId included in Sentry breadcrumbs          │
└──────────────────────────────────────────────────────┘
```

### 4.2 Propagation Patterns

#### Pattern 1: Child Logger Propagation (Recommended)

Pass the child logger through the call chain. Every log call automatically
includes the `requestId` and any other bound context.

```ts
// Route handler creates the child logger
const log = logger.child({ requestId, userId: session?.user?.id });

// Service receives the logger
const user = await userService.create(data, log);

// Service uses it naturally
async function create(data: CreateUserInput, log: Logger) {
  log.info({ action: 'createUser' }, 'Creating user');

  const user = await userRepository.insert(data, log);

  log.info({ userId: user.id }, 'User created');
  return user;
}
```

#### Pattern 2: Context Parameter (Alternative)

For cases where passing a logger is impractical (e.g., utility functions,
third-party integrations), pass a context object.

```ts
type RequestContext = {
  requestId: string;
  userId?: string;
};

async function processPayment(
  data: PaymentInput,
  ctx: RequestContext
) {
  logger.info({ ...ctx, action: 'processPayment' }, 'Processing payment');
  // ...
}
```

**Rules:**

- **MUST** propagate `requestId` through all application layers — handler,
  service, and repository
- **SHOULD** prefer child logger propagation (Pattern 1) over manual
  context passing (Pattern 2) — it is less error-prone and more natural
- **SHOULD** include `requestId` in Sentry context for error correlation:

  ```ts
  Sentry.setContext('request', { requestId });
  ```

- **SHOULD** propagate `requestId` to downstream HTTP calls via the
  `X-Request-ID` header for end-to-end tracing across services

### 4.3 Distributed Tracing (Awareness)

When an application evolves from a single service to multiple services
(e.g., a separate API, a background job processor, a notification service),
request tracing becomes **distributed tracing** — following a request
across service boundaries.

Sentry v10.x uses OpenTelemetry under the hood for distributed tracing.
The `requestId` pattern established here transitions naturally into
OpenTelemetry trace contexts when services multiply.

- **MAY** use Sentry's built-in distributed tracing when the architecture
  grows beyond a single service — Sentry propagates trace context through
  HTTP headers automatically
- **MUST** document the decision to adopt distributed tracing in an ADR
  (→ See [01-core-principles.md, § 9]) — it adds complexity and cost

### 4.4 Anti-Patterns

| Anti-Pattern | Why It Is Wrong | What to Do Instead |
|---|---|---|
| Not including `requestId` in log entries | Cannot correlate logs from the same request — debugging becomes guesswork | Use child loggers with `requestId` bound |
| Generating a new `requestId` at each layer | Multiple IDs for the same request — correlation breaks | Generate once at the entry point, propagate everywhere |
| Using `requestId` for authentication/authorization | `requestId` is a diagnostic tool, not a security credential | Keep `requestId` strictly for tracing (→ See [03 § 4.4]) |
| Not returning `requestId` in the response | User cannot report the ID for debugging, support cannot trace issues | Include in every response envelope (→ See [03 § 4.3]) |

---

## 5. Uptime & Health Monitoring

Uptime monitoring is the most fundamental observability need — knowing
whether your application is accessible to users. It is the first alert
system you should set up, even before structured logging.

### 5.1 Health Check Endpoints

Health check endpoints are dedicated URLs that report the application's
operational status. They are consumed by monitoring services (UptimeRobot),
load balancers, and container orchestrators.

#### `/health` — Liveness Check

Reports whether the application process is running and can handle requests.
This endpoint **MUST** be fast and simple — it should not check external
dependencies.

```ts
// app/api/health/route.ts (Next.js)
import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json(
    {
      status: 'ok',
      timestamp: new Date().toISOString(),
      version: process.env.APP_VERSION || 'unknown',
      environment: process.env.NODE_ENV,
    },
    { status: 200 }
  );
}
```

#### `/readiness` — Readiness Check

Reports whether the application is ready to serve traffic — checks
that all critical dependencies (database, cache, external services) are
accessible.

```ts
// app/api/readiness/route.ts (Next.js)
import { NextResponse } from 'next/server';
import { db } from '@/lib/database';

export async function GET() {
  const checks: Record<string, 'ok' | 'fail'> = {};

  // Check database connectivity
  try {
    await db.$queryRaw`SELECT 1`;
    checks.database = 'ok';
  } catch {
    checks.database = 'fail';
  }

  const allHealthy = Object.values(checks).every((s) => s === 'ok');

  return NextResponse.json(
    {
      status: allHealthy ? 'ok' : 'degraded',
      timestamp: new Date().toISOString(),
      checks,
    },
    { status: allHealthy ? 200 : 503 }
  );
}
```

**Rules:**

- **MUST** implement a `/health` endpoint in every production application
- **SHOULD** implement a `/readiness` endpoint that checks critical
  dependencies (database, required external services)
- **MUST** return HTTP `200` when healthy and `503` when unhealthy
- **MUST** keep health endpoints fast (< 100ms) — they are called
  frequently by monitoring services
- **MUST NOT** require authentication on health check endpoints — they
  must be accessible to monitoring services
- **MUST NOT** expose sensitive information (connection strings, internal
  IPs, error details) in health check responses
- **SHOULD** include a version identifier in the health response to verify
  which version is deployed
- **SHOULD** exclude health check requests from application logging to
  reduce noise:

  ```ts
  // In request logging middleware, skip health checks
  if (req.url === '/api/health' || req.url === '/api/readiness') {
    return next();
  }
  ```

### 5.2 UptimeRobot Configuration

UptimeRobot is the Adopt-tier uptime monitoring service
(→ See [02-technology-radar.md, § 3.15]).

> **Important:** As of 2025, UptimeRobot's free plan (50 monitors,
> 5-minute intervals) is restricted to **personal, non-commercial use**.
> Commercial projects **MUST** use a paid plan (starting at ~$7/month for
> the Solo plan with 1-minute intervals). Verify current pricing at
> [uptimerobot.com/pricing](https://uptimerobot.com/pricing/).

#### Recommended Monitors per Project

| Monitor Type | Target                    | Interval   | Alert On             |
|-------------|---------------------------|------------|----------------------|
| HTTP(S)     | Production URL (homepage) | 1–5 min    | Down for > 1 check   |
| HTTP(S)     | `/api/health` endpoint    | 1–5 min    | Down for > 1 check   |
| Keyword     | Key page (check for expected content) | 5 min | Keyword missing |
| SSL         | Production domain         | Daily      | Expiry < 14 days     |
| Port        | Database (if externally accessible) | 5 min | Connection refused |

- **MUST** configure at minimum an HTTP monitor for the production URL and
  the `/api/health` endpoint
- **MUST** configure SSL certificate expiry monitoring — expired
  certificates break HTTPS and destroy user trust
- **SHOULD** configure a keyword monitor to verify that key pages render
  correctly (not just return 200)
- **SHOULD** configure alerts via at least two channels (email + Slack
  or push notification) to avoid single points of notification failure

### 5.3 Status Page

A public status page communicates your application's availability to users
and stakeholders without them having to contact support.

- **SHOULD** create a status page for production applications with external
  users (UptimeRobot includes basic status pages on all plans)
- **MAY** use a custom domain for the status page
  (e.g., `status.myapp.com`)
- **SHOULD** include the following components on the status page:
  - Main website / application
  - API endpoints
  - Authentication service
  - Payment processing (if applicable)

### 5.4 Anti-Patterns

| Anti-Pattern | Why It Is Wrong | What to Do Instead |
|---|---|---|
| No uptime monitoring at all | You learn about downtime from users, not from your systems | Set up UptimeRobot on day one of production |
| Health endpoint that checks nothing | Returns 200 even when the database is down — false sense of security | `/health` for liveness, `/readiness` for dependency checks |
| Health endpoint behind authentication | Monitoring service cannot reach it — monitoring fails silently | Keep health endpoints public, expose no sensitive data |
| Checking health endpoint every 30 seconds from free tier | UptimeRobot free tier minimum is 5 minutes; exceeding limits causes monitoring gaps | Use the paid plan if faster intervals are needed |
| No SSL monitoring | Certificate expires without warning, causing browser security errors | Monitor SSL expiry with UptimeRobot (or similar) |

---

## 6. Metrics & Dashboards (Awareness)

Metrics measure aggregate behavior over time — request rates, error rates,
response time percentiles, database connection utilization. While logs tell
you about individual events, metrics tell you about **trends and capacity**.

This section is intentionally labeled "Awareness" because most projects in
this stack do not need custom metrics infrastructure from day one. Sentry
provides performance metrics, UptimeRobot provides availability metrics,
and Axiom (🔬 Trial) provides log-derived analytics. Custom metrics
(Grafana + Prometheus) become relevant when these tools are insufficient.

### 6.1 What Metrics Matter

For a web application, these are the metrics that correlate most directly
with user experience and system health.

#### Application Metrics

| Metric                  | What It Tells You                          | Alert When            |
|-------------------------|--------------------------------------------|-----------------------|
| Request rate (req/sec)  | Current load on the application            | Sudden spike or drop  |
| Error rate (% of 5xx)   | Percentage of requests failing             | > 1% for > 5 minutes  |
| Response time (p50/p95) | How fast the application responds          | p95 > 2000ms          |
| Apdex score             | User satisfaction with response times      | Below 0.8             |

#### Database Metrics

| Metric                      | What It Tells You                      | Alert When               |
|-----------------------------|----------------------------------------|--------------------------|
| Active connections          | How many connections are in use        | > 80% of pool maximum    |
| Query duration (p95)        | How fast queries execute               | p95 > 500ms              |
| Connection wait time        | How long requests wait for a connection| > 100ms average          |
| Dead tuples (PostgreSQL)    | Tables needing VACUUM                  | Growing continuously     |

#### Infrastructure Metrics (Hosting-Dependent)

| Metric            | What It Tells You                    | Alert When          |
|-------------------|--------------------------------------|---------------------|
| CPU utilization   | Processing load                      | > 80% sustained     |
| Memory usage      | Memory pressure                      | > 85% of available  |
| Disk usage        | Storage capacity                     | > 80% of available  |
| Network I/O       | Bandwidth utilization                | Approaching limits  |

> **Note:** Infrastructure metrics depend on your hosting platform (Vercel,
> Railway, AWS, etc.). Many platforms provide built-in dashboards for these
> metrics. Check your hosting provider's documentation before building
> custom monitoring.

### 6.2 Core Web Vitals in Production

Core Web Vitals measure real user experience in the browser. They are
both a performance metric and an SEO signal.

| Metric | Full Name                   | Target    | What It Measures                    |
|--------|-----------------------------|-----------|-------------------------------------|
| LCP    | Largest Contentful Paint    | < 2.5s    | Loading performance                 |
| INP    | Interaction to Next Paint   | < 200ms   | Responsiveness                      |
| CLS    | Cumulative Layout Shift     | < 0.1     | Visual stability                    |

- **SHOULD** monitor Core Web Vitals in production via Real User Monitoring
  (RUM) — Sentry and Vercel Analytics both provide this
  (→ See [05-frontend-standards.md, § 10])
- **SHOULD** track Core Web Vitals trends over time to detect regressions
  after deploys
  (→ See [06-testing-strategy.md, § 11.3])
- **MAY** set performance budgets and alert when Web Vitals degrade

### 6.3 Axiom for Log-Derived Metrics

Axiom (🔬 Trial in → See [02-technology-radar.md, § 3.15]) provides log
management with built-in analytics. As of 2026, Axiom's **Metrics**
feature is generally available, offering an alternative to
Grafana + Prometheus for teams that want metrics alongside their logs
without managing additional infrastructure.

Axiom's free tier (Personal) includes 500 GB/month of data ingestion
with 30 days retention — sufficient for most early-to-mid stage projects.
The paid plan (Axiom Cloud) starts at $25/month.

- **MAY** use Axiom as the log aggregation backend for Pino in production
  — Axiom provides a Pino transport and a Vercel integration
- **MAY** use Axiom Metrics for custom application metrics when
  Sentry's performance data is insufficient
- **MUST** create an ADR if adopting Axiom beyond Trial — evaluate cost
  projection, query capabilities, and team needs
  (→ See [01-core-principles.md, § 9])

### 6.4 Grafana + Prometheus (Awareness)

Grafana (metrics visualization) and Prometheus (metrics collection) are
🔍 Assess in the Technology Radar. They are the industry standard for
custom metrics dashboards but require infrastructure to host and maintain.

- **MAY** evaluate Grafana + Prometheus when custom metrics dashboards
  are needed and Axiom/Sentry metrics are insufficient
- **MUST** create an ADR before adopting — self-hosted monitoring
  infrastructure adds operational burden
  (→ See [02-technology-radar.md, § 3.15])

### 6.5 When to Invest in Metrics Infrastructure

```text
Do you need to know aggregate trends (not just individual events)?
 ├── NO  → Logs (Pino) + Error tracking (Sentry) are sufficient
 └── YES → Are Sentry's built-in performance metrics enough?
           ├── YES → Use Sentry Performance — no additional infrastructure
           └── NO  → Do you need log-derived analytics?
                     ├── YES → Try Axiom (🔬 Trial) — log analytics + metrics
                     └── NO  → Evaluate Grafana + Prometheus (🔍 Assess)
                               Document decision in an ADR
```

### 6.6 Anti-Patterns

| Anti-Pattern | Why It Is Wrong | What to Do Instead |
|---|---|---|
| Setting up Grafana + Prometheus for an MVP | Unnecessary infrastructure overhead — premature optimization | Start with Sentry + UptimeRobot; add metrics when needed |
| Collecting metrics but never looking at them | Wasted resources, false sense of observability | Only collect metrics you will alert on or review regularly |
| No performance baseline | Cannot detect degradation if you do not know what "normal" looks like | Establish baseline metrics after initial production deployment |
| Custom metrics for everything | Excessive cardinality, high storage cost, slow queries | Focus on the metrics in § 6.1 — add others only when investigating a specific problem |

---

## 7. Audit Logging

Audit logs record *who* did *what* to *which resource*, *when*, and *what
was the result*. They serve compliance, security investigation, and
accountability purposes. An audit log is fundamentally different from an
application log — it is a business record, not a debugging tool.

> **Important:** The rules about *what* MUST be audited are defined in
> → See [07-security-standards.md, § A09 and § 5.3]. This section focuses on
> *how* to implement audit logging — schema, storage, and retention.

### 7.1 Audit Log vs Application Log

| Aspect           | Application Log                          | Audit Log                                    |
|------------------|------------------------------------------|----------------------------------------------|
| Purpose          | Debugging and monitoring                 | Compliance, accountability, forensics        |
| Content          | Technical events, errors, performance    | Business actions on protected resources      |
| Audience         | Developers, SRE                          | Security team, compliance, legal             |
| Mutability       | Can be rotated, compressed, deleted      | **Append-only**, never modified or deleted   |
| Retention        | Days to weeks (cost-driven)              | Months to years (regulation-driven)          |
| Storage          | Same as application data (often)         | Separate, with restricted write access       |

### 7.2 What to Audit

The following events **MUST** be recorded in the audit log
(→ See [07-security-standards.md, § A09] for the complete list):

- All authentication events (login success, login failure, logout)
- All authorization failures (403 responses)
- All state-changing operations on protected resources (create, update,
  delete of users, orders, payments, configurations)
- All administrative actions (role changes, permission grants, setting
  modifications)
- All access to sensitive data (viewing PII, exporting data)

### 7.3 Audit Log Schema

Every audit log entry **SHOULD** follow a consistent schema that answers
the five W questions.

```ts
type AuditLogEntry = {
  // WHEN — timestamp of the action
  timestamp: string;         // ISO 8601 UTC

  // WHO — the actor
  actorId: string;           // User ID or system identifier
  actorType: 'user' | 'system' | 'api_key' | 'agent';  // 'agent' = AI-agent action → See [07-security-standards.md, §15] (agent.* taxonomy); [12-ai-engineering.md, §6.8]
  actorIp?: string;          // Client IP (when applicable)

  // WHAT — the action performed
  action: string;            // Verb: 'create', 'update', 'delete', 'login', 'export'

  // WHICH — the target resource
  resourceType: string;      // 'user', 'order', 'payment', 'setting'
  resourceId: string;        // Specific resource identifier

  // RESULT — what happened
  result: 'success' | 'failure' | 'denied';
  reason?: string;           // Why it failed or was denied

  // CONTEXT — additional details
  requestId: string;         // Correlation with application logs
  changes?: {                // For updates: what changed
    field: string;
    from: unknown;
    to: unknown;
  }[];
};
```

```ts
// Example: User role change
const auditEntry: AuditLogEntry = {
  timestamp: new Date().toISOString(),
  actorId: 'admin_user_123',
  actorType: 'user',
  actorIp: '192.168.1.1',
  action: 'update',
  resourceType: 'user',
  resourceId: 'user_456',
  result: 'success',
  requestId: 'req_V1StGXR8_Z5jdHi6B',
  changes: [
    { field: 'role', from: 'viewer', to: 'admin' },
  ],
};
```

### 7.4 Storage Strategy

- **MUST** store audit logs in a separate table or dataset from application
  logs — audit data has different retention and access requirements
- **MUST** make audit logs append-only — application code **MUST NOT** be
  able to update or delete audit log entries
  (→ See [07-security-standards.md, § A09])
- **SHOULD** use a separate database table (e.g., `audit_logs`) with
  restricted write-only permissions — the application can INSERT but
  not UPDATE or DELETE:

  ```sql
  -- PostgreSQL: Audit log table
  CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT now(),
    actor_id TEXT NOT NULL,
    actor_type TEXT NOT NULL,
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT NOT NULL,
    result TEXT NOT NULL,
    reason TEXT,
    request_id TEXT,
    changes JSONB,
    ip_address INET,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
  );

  -- Index for common queries
  CREATE INDEX idx_audit_actor ON audit_logs (actor_id, timestamp DESC);
  CREATE INDEX idx_audit_resource ON audit_logs (resource_type, resource_id, timestamp DESC);
  CREATE INDEX idx_audit_action ON audit_logs (action, timestamp DESC);

  -- RLS: Only the application role can INSERT, nobody can UPDATE or DELETE
  ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
  ```

- **MAY** forward audit logs to an external service (Axiom, Sentry) for
  advanced querying and alerting, in addition to database storage

### 7.5 Retention

- **MUST** retain audit logs for at least 90 days (longer for compliance)
  (→ See [07-security-standards.md, § A09])
- **MUST** comply with RGPD data retention rules — audit logs containing
  personal data are subject to the same regulations as any other personal
  data store. However, there is a legitimate interest in retaining audit
  logs for security purposes, even when a user requests erasure.
  Document this balance in a data inventory
  (→ See `templates/data-inventory.md`).
- **SHOULD** define a retention policy per project and document it in
  the project's ADR or security documentation

### 7.6 Anti-Patterns

| Anti-Pattern | Why It Is Wrong | What to Do Instead |
|---|---|---|
| Audit logs mixed with application logs | Different retention, access, and compliance requirements | Separate storage (table, dataset, or service) |
| Application can delete audit entries | Defeats the purpose — actors can cover their tracks | Append-only with restricted permissions |
| Logging PII in audit entries without redaction | RGPD violation — audit logs are still data stores | Log only user IDs and resource IDs, not full PII |
| No audit logging at all | Compliance risk, no forensic capability, no accountability | Start with auth events and state-changing operations |
| Audit logging everything | Excessive storage, slow queries, no signal in the noise | Audit only the events listed in → See [07 § A09] |

---

## 8. Alerting Strategy

Alerting bridges the gap between monitoring data and human action. A good
alerting strategy ensures that the right people are notified about the
right problems at the right time — and that routine events do not trigger
notification fatigue.

### 8.1 Alert Fatigue

Alert fatigue is the single biggest threat to an effective alerting
strategy. When too many alerts fire — or when alerts fire for non-actionable
events — developers learn to ignore them. When a real incident occurs, the
alert is lost in the noise.

**The test for every alert:** "If this fires at 3 AM, does someone need to
wake up and act?" If the answer is no, it should not be a critical alert.

### 8.2 Alert Classification

| Severity      | Response Time         | Notification Channel       | Example                                       |
|---------------|-----------------------|----------------------------|-----------------------------------------------|
| **Critical**  | Immediate (< 15 min)  | Push notification + SMS + email | Application down, database unreachable, payment system failure |
| **Warning**   | Within business hours | Email + Slack              | Error rate elevated, disk space > 80%, SSL expiring in 7 days |
| **Informational** | Next review cycle | Dashboard only (no notification) | Deploy completed, daily error summary, usage trends |

### 8.3 What to Alert On

| Condition                                  | Severity    | Source                |
|--------------------------------------------|-------------|-----------------------|
| Application unreachable (health check fail)| Critical    | UptimeRobot           |
| Error rate > 5% for > 5 minutes            | Critical    | Sentry                |
| Unhandled exception in production          | Warning     | Sentry                |
| Database connection failures               | Critical    | Application logs      |
| Response time p95 > 3000ms for > 10 min    | Warning     | Sentry Performance    |
| SSL certificate expiring in < 14 days      | Warning     | UptimeRobot           |
| Disk space > 80%                           | Warning     | Hosting platform      |
| Multiple failed login attempts (same IP)   | Warning     | Application logs / Sentry |
| Unusual geographic access pattern          | Warning     | Sentry / Logs         |
| Spike in 403/429 responses                 | Warning     | Application logs      |

### 8.4 What NOT to Alert On

- **Expected errors** (404s, validation failures) — these are normal
  application behavior
- **Transient blips** (single failed health check that recovers
  immediately) — configure UptimeRobot to alert only after 2+ consecutive
  failures
- **Info-level events** (user created, order completed) — these belong on
  dashboards, not in notification channels
- **Scheduled maintenance** — use UptimeRobot maintenance windows to
  suppress alerts during planned downtime
- **Development/staging errors** — only alert on production environments

### 8.5 Notification Channels

- **MUST** configure at least two notification channels for critical alerts
  (e.g., email + push notification) — a single channel is a single point
  of failure
- **SHOULD** use channel escalation — if the primary channel is not
  acknowledged within X minutes, escalate to the secondary
- **SHOULD** configure Slack (or equivalent) for team visibility on
  warning-level alerts
- **MAY** integrate PagerDuty or Opsgenie for on-call rotation when
  projects have SLA requirements

### 8.6 On-Call (Awareness)

For projects that grow to serve real users with availability expectations,
an on-call rotation becomes necessary. This is an operational maturity
milestone, not a day-one requirement.

- **MAY** establish an on-call rotation when the project has defined SLAs
  or serves users in multiple time zones
- **MUST** document the on-call policy (rotation schedule, escalation
  rules, response time expectations) before implementing it
- **SHOULD** start with a simple rotation (primary + backup) and evolve
  based on incident frequency

### 8.7 Anti-Patterns

| Anti-Pattern | Why It Is Wrong | What to Do Instead |
|---|---|---|
| Alert on every error | Creates noise, developers ignore alerts | Alert on error *rate thresholds*, not individual errors |
| No alerts at all | You learn about outages from users | Set up UptimeRobot + Sentry alerts on day one |
| Same severity for everything | Cannot prioritize — everything is "urgent" | Classify alerts as critical, warning, or informational |
| Single notification channel | If that channel is down or muted, you miss the alert | Configure at least two channels for critical alerts |
| Alerting on staging/dev | Wastes attention, creates false urgency | Only alert on production environments |
| Not acknowledging / resolving alerts | Alert history becomes useless, no accountability | Track alert acknowledgment and resolution |

---

## 9. Observability by Project Stage

Not every project needs the same level of observability. A weekend side
project has different needs than a production application serving paying
customers. This section defines what to implement at each stage, following
the principle of → See [01-core-principles.md, § 1.3 — Pragmatism Over Dogma]:
start simple, add complexity only when measured need exists.

### 9.1 MVP / Early Stage

**Goal:** Know when things break. Debug production issues without SSH-ing
into the server.

| Component          | Tool                | Configuration                         |
|--------------------|---------------------|---------------------------------------|
| Structured logging | Pino                | Default config from § 2.4             |
| Error tracking     | Sentry              | Default config from § 3.1             |
| Uptime monitoring  | UptimeRobot         | HTTP monitor on production URL        |
| Request tracing    | requestId           | Child logger pattern from § 4         |

**Estimated setup time:** 1-2 hours.

**Checklist:**
- [ ] Pino configured with structured JSON output and redaction
- [ ] Sentry SDK installed with source map uploads in CI/CD
- [ ] UptimeRobot monitoring the production URL
- [ ] requestId generated and included in all responses and logs
- [ ] `global-error.tsx` implemented for React error boundary + Sentry

### 9.2 Growing Project

**Goal:** Proactive visibility. Detect trends before they become incidents.

Everything from MVP, plus:

| Component          | Tool                | Configuration                         |
|--------------------|---------------------|---------------------------------------|
| Log aggregation    | Axiom (🔬 Trial)    | Pino → Axiom transport                |
| Custom alerts      | Sentry              | Error rate alerts, performance alerts |
| Health endpoints   | Application         | `/health` + `/readiness`              |
| Audit logging      | PostgreSQL table    | Schema from § 7.3                     |
| SSL monitoring     | UptimeRobot         | Certificate expiry alerts             |

**Additional checklist:**
- [ ] Axiom (or equivalent) receiving logs from production
- [ ] Sentry alert rules configured for error rate thresholds
- [ ] `/health` and `/readiness` endpoints implemented
- [ ] Audit logging for auth events and state-changing operations
- [ ] SSL certificate expiry monitored
- [ ] Status page configured for external communication

### 9.3 Production at Scale

**Goal:** Full operational visibility. Quantitative understanding of system
behavior. Incident response capabilities.

Everything from Growing Project, plus:

| Component              | Tool                   | Configuration                    |
|------------------------|------------------------|----------------------------------|
| Custom metrics         | Axiom Metrics or Grafana + Prometheus | Application + database metrics |
| Distributed tracing    | Sentry + OpenTelemetry | Cross-service trace propagation  |
| On-call rotation       | PagerDuty / Opsgenie   | Escalation policies              |
| Performance budgets    | Sentry / Lighthouse CI | Core Web Vitals thresholds       |
| Session replay         | Sentry (LogRocket 🔬 Trial) | Error session recording     |

**Additional checklist:**
- [ ] Custom dashboards for application and database metrics
- [ ] Distributed tracing across service boundaries
- [ ] On-call rotation documented and operational
- [ ] Performance budgets enforced in CI/CD
- [ ] Incident response playbook documented (→ `templates/incident-report.md`)

### 9.4 Decision Guide

```text
Is the project in production with real users?
 ├── NO  → MVP setup (Pino + Sentry + UptimeRobot)
 └── YES → Are you debugging issues reactively (after users report)?
           ├── YES → Growing Project setup (+ Axiom, + alerts, + health endpoints)
           └── NO  → Do you have SLAs or serve high-traffic?
                     ├── YES → Production at Scale (+ metrics, + tracing, + on-call)
                     └── NO  → Growing Project is likely sufficient
```

---

## 10. Observability Checklist

### 10.1 Pre-Deployment Checklist

Before deploying a new project or major feature to production, verify:

- [ ] **Logging:** Pino configured with structured JSON output
- [ ] **Redaction:** Sensitive fields redacted (passwords, tokens, PII)
- [ ] **Log levels:** `info` in production, `debug` disabled by default
- [ ] **Error tracking:** Sentry SDK installed and configured
- [ ] **Source maps:** Uploaded to Sentry in CI/CD pipeline
- [ ] **Source maps deleted:** Client source maps removed after upload
- [ ] **Auth token:** `SENTRY_AUTH_TOKEN` in CI/CD env vars, not in code
- [ ] **Request tracing:** `requestId` in all responses and log entries
- [ ] **Health endpoint:** `/health` returning 200 with version info
- [ ] **Uptime monitoring:** UptimeRobot (or equivalent) configured
- [ ] **Error boundary:** `global-error.tsx` catching and reporting errors
- [ ] **Audit logging:** Auth events and state-changing operations logged
- [ ] **Alert channels:** At least two notification channels configured

### 10.2 Post-Deployment Verification

After deploying, verify the observability stack is working:

- [ ] **Trigger a test error** — verify it appears in Sentry with readable
      stack traces (original file names and line numbers)
- [ ] **Check logs** — verify structured JSON output with correct fields
      (requestId, level, timestamp, msg)
- [ ] **Check health endpoint** — verify `/health` returns the new version
- [ ] **Check uptime monitor** — verify UptimeRobot shows the site as "up"
- [ ] **Review Sentry release** — verify the new release appears with
      correct environment tags
- [ ] **Check audit log** — perform a state-changing action and verify the
      audit entry is recorded

### 10.3 Incident Investigation Checklist

When investigating a production incident:

1. **Identify the scope** — How many users are affected? Which endpoints?
   Since when? (Check Sentry error rate, UptimeRobot timeline)
2. **Find the requestId** — If a user reported the issue, ask for the
   `requestId` from the API response. If from an alert, find it in the
   Sentry issue.
3. **Trace the request** — Search logs for the `requestId` to see the
   full timeline of the request through all layers.
4. **Check related errors** — Search Sentry for the same error code,
   endpoint, or user to identify patterns.
5. **Check recent deploys** — Did a recent deployment correlate with the
   start of the issue? Check Sentry release health.
6. **Check infrastructure** — Are database metrics normal? Is memory/CPU
   elevated? Check hosting platform dashboards.
7. **Document the incident** — Record the timeline, root cause, impact,
   and corrective actions in an incident report
   (→ See `templates/incident-report.md`).

# 🗄️ Database Standards

> **Scope:** Practical guide for designing, implementing, and maintaining PostgreSQL
> databases across all projects covered by these engineering standards.
>
> **Purpose:** The reference that answers "how should this table look, how should
> this migration work, and how should this query be structured?" — ensuring every
> database is consistent, performant, and secure, regardless of the access layer
> (Supabase Client, Prisma, or raw SQL).
>
> **Keywords:**
> - **MUST** = required (PR should be blocked if violated)
> - **SHOULD** = strongly recommended (requires justification to skip)
> - **MAY** = optional (case-by-case)

---

## 0. How to Use This Document

- This document defines **how to design and operate PostgreSQL databases** — schema
  design, naming conventions, migrations, RLS, indexing, query patterns, and
  performance optimization.
- It does **not** define which database engine or ORM to use (that lives in
  → See [02-technology-radar.md]) or how to protect data against attacks and comply
  with RGPD (that lives in → See [07-security-standards.md]). It references both
  heavily.
- Code examples use **SQL** (PostgreSQL dialect) and **TypeScript** with
  **Supabase Client** (default full-stack) and **Prisma v7** (Adopt — complex
  data models), reflecting the Adopt choices in
  → See [02-technology-radar.md, Section 4.8].
- The layering model assumed throughout is:
  `Route Handler / Controller → Service → Repository → Database`
  (→ See [01-core-principles.md, Section 6]).
- The API layer sends and receives **camelCase JSON**
  (→ See [03-api-design.md, Section 4]). The database stores data in
  **snake_case**. The Repository layer is the bridge that maps between the two.
- When a rule here overlaps with security, the security document takes
  precedence — this document defers to → See [07-security-standards.md] on all
  security-related decisions.

### Document Relationships

```text
04-database-standards.md (this document)
 ├── Derives from    → 01-core-principles.md (naming, fail-fast, layering, SOLID)
 ├── Derives from    → 02-technology-radar.md (PostgreSQL, Supabase, Prisma choices)
 ├── Complements     → 07-security-standards.md (SQL injection, encryption, RLS as security control, RGPD)
 ├── Complements     → 03-api-design.md (response format ↔ query patterns, pagination at DB level)
 ├── Referenced by   → 05-frontend-standards.md (real-time subscriptions, optimistic updates)
 ├── Referenced by   → 06-testing-strategy.md (database testing, test isolation, seeding)
 ├── Referenced by   → 08-observability.md (query monitoring, slow query logging)
 ├── Referenced by   → 09-devops-cicd.md (migration execution in CI/CD, backup automation)
 └── Referenced by   → 12-ai-engineering.md (agent state/memory storage + RLS)
```

### Boundary Definitions

| Question | This Document (04) | Other Document |
|----------|--------------------|----------------|
| **Which** database engine or ORM to use? | — | → See [02-technology-radar.md, §3.8] |
| **How** to name tables, columns, indexes? | ✅ Section 2 | — |
| **How** to write and manage migrations? | ✅ Section 6 | → See [09-devops-cicd.md] (CI/CD execution) |
| **How** to implement RLS policies? | ✅ Section 7 (authoritative) | → See [07-security-standards.md, §17] (checklist verification) |
| **How** to protect against SQL injection? | — | → See [07-security-standards.md, §3] |
| **How** to handle RGPD data deletion? | ✅ Section 3.4 (soft delete) | → See [07-security-standards.md, §14] (RGPD rules) |
| **How** to test database code? | ✅ Section 13 (DB-specific patterns) | → See [06-testing-strategy.md] (strategy, pyramid, CI gates) |
| **How** to configure connections for Prisma/Supabase? | ✅ Section 11 | — |
| **How** to persist agent state & memory (scoped tables + RLS)? | ✅ Section 3.8 + Section 7 | → See [12-ai-engineering.md, §6.5] (memory model: working / long-term / episodic) |
| **How** to store RAG embeddings (pgvector, HNSW, RLS)? | ✅ Section 3.9 | → See [02-technology-radar.md, §3.28] (tool choice); [12-ai-engineering.md, §3.3] (ingestion) |

### Technology Versions

| Technology | Version | Role |
|---|---|---|
| PostgreSQL | 15+ | Database engine |
| Supabase | Latest (Cloud) | Managed PostgreSQL + Auth + Storage |
| Supabase CLI | Latest | Local development + migrations |
| Prisma | v7.x | Type-safe ORM (Adopt) |
| Drizzle ORM | v1.x (beta) | SQL-first type-safe builder (Trial) |
| TypeScript | 5.x+ | All code examples |

### AI Agent Instructions

This document is designed to be consumed by AI coding agents (e.g., Claude
Code). When interpreting this document:

- **MUST**, **SHOULD**, and **MAY** are RFC 2119 keywords — treat MUST as non-negotiable constraints, SHOULD as strong defaults that require explicit justification to override, and MAY as contextual options.
- Cross-references (→ See [XX-document.md]) point to authoritative definitions — always defer to the referenced document for the full rule.
- When this document conflicts with [07-security-standards.md], the security document takes precedence.
- BAD/GOOD code examples are pattern-matching references — apply the principle behind the example, not just the literal code.
- Anti-pattern tables describe common mistakes — use them as negative examples when reviewing or generating code.
- Every table, migration, and query generated MUST follow the naming conventions, RLS rules, and indexing guidelines defined here.
- If generating code requires violating a MUST rule, the AI **MUST stop** and ask the human for permission before proceeding — never silently override a standard.
- **MUST NOT** over-engineer — always prefer the simplest solution that meets the stated requirements. Do not add abstractions, patterns, or infrastructure beyond what was explicitly requested (→ See [01-core-principles.md, §12]).
- **Version-critical rules for code generation:**
  - Prisma v7: DO NOT generate `@default(autoincrement())` for IDs — use UUID (`gen_random_uuid()`). DO NOT create `PrismaClient` without the global singleton pattern (→ §11). DO NOT use `connection_limit` URL parameter — use `pg.Pool({ max })` instead. The `datasource` block was removed from `schema.prisma`.

---

## 1. Database Design Philosophy

The database is the foundation of any data-driven application. Frameworks change,
APIs are rewritten, frontends are redesigned — but the data model endures. A
well-designed database makes every layer above it simpler; a poorly designed one
creates friction that compounds with every feature.

These principles guide every decision in this document.

### 1.1 PostgreSQL Is the Default

All projects use PostgreSQL as the primary database engine. This is a deliberate
strategic decision, not a default by inertia.

- **MUST** use PostgreSQL for all persistent, relational data storage
  (→ See [02-technology-radar.md, Section 4.8 — PostgreSQL])
- **MUST** leverage PostgreSQL-native features (JSONB, full-text search, arrays,
  `timestamptz`, generated columns) before reaching for external tools
- **SHOULD** build deep PostgreSQL expertise rather than shallow familiarity with
  multiple database engines — mastering one engine's query planner, indexing
  strategies, and extension ecosystem produces better results than knowing the
  basics of five engines

> **Why:** Standardizing on a single database reduces cognitive overhead, simplifies
> operations (backup, monitoring, upgrades), and allows investment in deep expertise.
> PostgreSQL's feature set — JSONB for document storage, `tsvector` for full-text
> search, PostGIS for geospatial data — covers use cases that would otherwise
> require separate specialized databases.

### 1.2 Data Integrity Is Non-Negotiable

The database is the **last safety net** in the system. Application code has bugs,
APIs receive unexpected input, services crash mid-operation. The database must
protect data integrity even when everything above it fails.

- **MUST** enforce data integrity at the database level — constraints, foreign keys,
  `NOT NULL`, `CHECK`, and `UNIQUE` are not optional
- **MUST NOT** rely solely on application-level validation to prevent invalid data —
  application logic is a convenience for good error messages; the database is the
  enforcement layer
- **SHOULD** think of database constraints as a complement to application validation,
  not a replacement — both layers serve different purposes
  (→ See [07-security-standards.md, Section 3 — Defense in Depth])

> **Why:** Application-level validation can be bypassed — by bugs, by direct database
> access, by migrations, by admin scripts, by future developers who forget the rule.
> Database constraints are always enforced, regardless of the access path. They are
> the one guarantee that invalid data cannot exist.

### 1.3 Pragmatic Normalization

Normalization is the default — but it is a tool, not a religion. The goal is to
eliminate data anomalies (update, insert, delete) while keeping the schema
practical and queryable.

- **SHOULD** normalize to Third Normal Form (3NF) as the starting point for all
  schema design — this eliminates the most common data anomalies
- **SHOULD** denormalize intentionally when there is a **measured** performance need —
  not as a shortcut, not as a guess, and not because "joins are slow" (they are
  not, with proper indexing)
- **MUST** document any intentional denormalization in an ADR, including what
  consistency trade-offs were accepted and how data integrity is maintained
  (→ See [01-core-principles.md, Section 9 — ADR])
- **MAY** use JSONB columns for truly semi-structured data (user preferences,
  metadata, configuration) — but not as a way to avoid designing proper relational
  schemas

> **Why:** Under-normalization causes update anomalies — the same fact stored in
> multiple places gets out of sync. Over-normalization causes excessive joins that
> hurt readability and performance. The sweet spot is 3NF by default, with
> documented exceptions when the access pattern demands it.

### 1.4 Design for Queries, Not for Storage

A database schema exists to serve the application's access patterns. The most
elegant ER diagram is worthless if it requires seven joins for the most common
query.

- **SHOULD** identify the primary access patterns (reads, writes, filters, sorts)
  **before** designing the schema — what questions will the application ask most
  frequently?
- **SHOULD** optimize the schema for the most common queries — the 80% case should
  be simple and fast; the 20% edge case can tolerate more complexity
- **MUST** design indexes based on actual query patterns, not guesswork — measure
  first (→ See [Section 8 — Indexing Strategy])
- **MUST** design APIs from the consumer's perspective, not from the database schema
  outward (→ See [03-api-design.md, Section 1.1])

> **Why:** A schema optimized for theoretical purity but misaligned with real access
> patterns will require complex queries, excessive joins, and compensating indexes.
> Starting from access patterns and working backward to the schema produces better
> results.

### 1.5 The Database Outlives the Application

Applications are rewritten. Frontends are redesigned. APIs get new versions.
But the data — and the schema that shapes it — tends to survive across generations
of application code. Decisions made in the schema today will constrain (or
empower) developers years from now.

- **MUST** treat schema design as a long-term investment — take more time to get it
  right, because changing it later is expensive (migrations, data backfills,
  downstream impact)
- **SHOULD** prefer explicit, self-documenting column names and constraints over
  clever shortcuts — a future developer reading the schema should understand the
  data model without external documentation
- **MUST** version-control all schema changes via migrations — the database schema
  is code and deserves the same discipline
  (→ See [Section 6 — Migration Standards])

> **Why:** The cost of a schema change scales with the amount of data and the number
> of consumers. A column rename on an empty table is trivial; the same rename on a
> table with millions of rows and ten services consuming it is a multi-sprint
> project. Invest in good schema design upfront.

### 1.6 Security at the Data Layer

Security is not only an application concern — the database itself is a security
boundary. Row Level Security (RLS), least privilege access, and encryption at
rest are not optional extras.

- **MUST** enable RLS on every table in Supabase projects — without RLS, the
  `anon` key exposes data publicly
  (→ See [07-security-standards.md, Section 5])
- **MUST** follow the principle of least privilege — application connections should
  have only the permissions they need, never superuser access
- **MUST** use parameterized queries exclusively — never interpolate user input
  into SQL (→ See [07-security-standards.md, Section 10 — A03: Injection])
- **SHOULD** treat the database as a defense-in-depth layer — even if the
  application layer is compromised, the database should limit the blast radius

> **Why:** The database contains the actual data — it is the ultimate target of any
> attack. Application-layer security can be bypassed; database-layer security
> cannot (short of a full database compromise). RLS policies, connection
> restrictions, and encryption at rest form the last line of defense.

---

## 2. Naming Conventions

A well-named database is self-documenting. A developer reading the schema should
understand the data model, relationships, and business rules without external
documentation. These conventions apply to all PostgreSQL databases and extend
the universal naming rules in → See [01-core-principles.md, Section 7].

> **Core rule:** Everything in the database uses `snake_case` and **English only**.
> No camelCase, no PascalCase, no kebab-case. PostgreSQL folds unquoted
> identifiers to lowercase — using `snake_case` avoids the need for quoted
> identifiers and aligns with PostgreSQL community conventions.

### 2.1 Tables

- **MUST** use `snake_case`, **plural** nouns:

  ```sql
  -- GOOD
  users
  vehicles
  service_appointments
  invoice_line_items

  -- BAD — singular
  user
  vehicle
  service_appointment

  -- BAD — camelCase (requires quoting)
  "serviceAppointments"
  "invoiceLineItems"
  ```

- **MUST** use descriptive domain names — the table name should reflect the
  business concept, not an abbreviation:

  ```sql
  -- BAD — cryptic, hostile to new developers
  svc_appt
  inv_li
  usr_prefs

  -- GOOD — readable, self-documenting
  service_appointments
  invoice_line_items
  user_preferences
  ```

- **SHOULD** use a consistent vocabulary — if the business says "vehicle," every
  table, column, and reference uses "vehicle," not "car," "automobile," or "auto"
  interchangeably
  (→ See [01-core-principles.md, Section 7.1 — Naming Philosophy])

### 2.2 Columns

- **MUST** use `snake_case`:

  ```sql
  -- GOOD
  first_name
  email_address
  total_amount_cents
  created_at

  -- BAD
  firstName
  EmailAddress
  TotalAmountCents
  ```

- **MUST** prefix boolean columns with `is_` or `has_`:

  ```sql
  is_active
  is_verified
  has_accepted_terms
  has_valid_license
  ```

- **MUST** use `_at` suffix for timestamp columns:

  ```sql
  created_at
  updated_at
  deleted_at
  published_at
  last_login_at
  ```

- **MUST** use `_on` suffix for date-only columns (no time component):

  ```sql
  birth_on
  hired_on
  due_on
  ```

- **SHOULD** store monetary values as integers in the smallest currency unit
  (cents, not euros/dollars) and reflect this in the column name:

  ```sql
  -- GOOD — unambiguous, no floating-point precision issues
  price_cents        -- 1999 = €19.99
  total_amount_cents -- 4500 = €45.00
  discount_cents     -- 500  = €5.00

  -- BAD — ambiguous (is it euros or cents?), invites float errors
  price
  total_amount
  discount
  ```

- **MUST** use `_id` suffix for foreign key columns, prefixed with the
  **singular** form of the referenced table:

  ```sql
  -- Table: vehicles
  -- References: users (owner), dealerships
  user_id          -- references users.id
  dealership_id    -- references dealerships.id

  -- BAD — no suffix, ambiguous
  user             -- is this a name? an object? a foreign key?
  dealership       -- unclear
  ```

### 2.3 Primary Keys

- **MUST** name the primary key column `id` on every table:

  ```sql
  -- GOOD — consistent, predictable
  users.id
  vehicles.id
  invoices.id

  -- BAD — inconsistent, redundant
  users.user_id
  vehicles.vehicle_id
  invoices.invoice_id
  ```

> **Why `id` and not `<table>_id`?** Within the table itself, the context is
> already clear — `users.id` is unambiguous. The `<entity>_id` pattern is
> reserved for foreign key columns in **other** tables, where the context
> is needed: `vehicles.user_id` references `users.id`.

### 2.4 Indexes

- **MUST** use the pattern `idx_<table>_<column(s)>`:

  ```sql
  idx_users_email
  idx_vehicles_make_model        -- composite index
  idx_orders_user_id_created_at  -- composite index
  ```

- **MUST** use `uniq_<table>_<column(s)>` for unique indexes:

  ```sql
  uniq_users_email
  uniq_vehicles_vin
  uniq_order_items_order_id_product_id  -- composite unique
  ```

### 2.5 Constraints

- **MUST** name all constraints explicitly — never rely on auto-generated names.
  Auto-generated names like `users_email_key` or `vehicles_pkey` are inconsistent
  across databases and impossible to reference reliably in migrations:

  | Constraint Type | Pattern                            | Example                              |
  |-----------------|------------------------------------|--------------------------------------|
  | Primary key     | `pk_<table>`                       | `pk_users`                           |
  | Foreign key     | `fk_<table>_<column>`              | `fk_vehicles_user_id`                |
  | Unique          | `uniq_<table>_<column(s)>`         | `uniq_users_email`                   |
  | Check           | `chk_<table>_<description>`        | `chk_orders_total_positive`          |
  | Not null        | *(use column definition directly)* | `email TEXT NOT NULL`                |

  ```sql
  -- GOOD — explicit, predictable, referenceable in migrations
  ALTER TABLE vehicles
    ADD CONSTRAINT pk_vehicles PRIMARY KEY (id),
    ADD CONSTRAINT fk_vehicles_user_id FOREIGN KEY (user_id) REFERENCES users(id),
    ADD CONSTRAINT fk_vehicles_dealership_id FOREIGN KEY (dealership_id) REFERENCES dealerships(id),
    ADD CONSTRAINT uniq_vehicles_vin UNIQUE (vin),
    ADD CONSTRAINT chk_vehicles_year_reasonable CHECK (year BETWEEN 1886 AND EXTRACT(YEAR FROM NOW()) + 2);

  -- BAD — implicit names, impossible to reference later
  ALTER TABLE vehicles
    ADD PRIMARY KEY (id),
    ADD FOREIGN KEY (user_id) REFERENCES users(id),
    ADD UNIQUE (vin);
  ```

### 2.6 Enums (PostgreSQL Custom Types)

- **MUST** use `snake_case` for the type name, singular:

  ```sql
  -- GOOD
  CREATE TYPE order_status AS ENUM ('pending', 'confirmed', 'shipped', 'delivered', 'cancelled');
  CREATE TYPE vehicle_fuel_type AS ENUM ('gasoline', 'diesel', 'electric', 'hybrid', 'plug_in_hybrid');

  -- BAD — PascalCase, plural
  CREATE TYPE OrderStatuses AS ENUM (...);
  ```

- **MUST** use `snake_case` for enum values (lowercase, underscores):

  ```sql
  -- GOOD
  'pending', 'in_progress', 'completed', 'on_hold'

  -- BAD — UPPER_CASE or mixed case
  'PENDING', 'IN_PROGRESS', 'InProgress'
  ```

### 2.7 Functions & Triggers

- **MUST** use `snake_case` for function names with a verb prefix that describes
  the action:

  ```sql
  -- Functions
  calculate_invoice_total(invoice_id UUID)
  update_updated_at_column()           -- trigger function for auto-updating timestamps
  validate_booking_overlap(start_at TIMESTAMPTZ, end_at TIMESTAMPTZ)
  get_user_active_vehicles(p_user_id UUID)

  -- BAD — vague, no verb
  invoice_stuff()
  do_booking()
  ```

- **MUST** prefix trigger names with `trg_<table>_<event>_<description>`:

  ```sql
  trg_users_before_update_set_updated_at
  trg_orders_after_insert_notify_new_order
  trg_audit_logs_before_update_prevent_modification
  ```

- **SHOULD** prefix function parameters with `p_` to distinguish from column
  names inside function bodies:

  ```sql
  CREATE FUNCTION get_user_vehicles(p_user_id UUID)
  RETURNS SETOF vehicles AS $$
    SELECT * FROM vehicles WHERE user_id = p_user_id;
  $$ LANGUAGE sql;
  ```

### 2.8 RLS Policies

- **MUST** name policies with the pattern `<operation>_<table>_<description>`:

  ```sql
  -- GOOD — operation is clear, scope is documented
  CREATE POLICY select_vehicles_own
    ON vehicles FOR SELECT
    USING (user_id = auth.uid());

  CREATE POLICY insert_vehicles_authenticated
    ON vehicles FOR INSERT
    WITH CHECK (user_id = auth.uid());

  CREATE POLICY update_vehicles_own
    ON vehicles FOR UPDATE
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

  CREATE POLICY delete_vehicles_own
    ON vehicles FOR DELETE
    USING (user_id = auth.uid());

  -- BAD — vague, no context
  CREATE POLICY "Enable read access" ON vehicles ...
  CREATE POLICY "policy1" ON vehicles ...
  ```

### 2.9 Database Schemas (Namespaces)

- **MUST** use `snake_case` for schema names:

  ```sql
  -- GOOD
  CREATE SCHEMA internal;       -- admin/internal functions
  CREATE SCHEMA reporting;      -- materialized views, reporting queries

  -- Default Supabase schemas (do not rename):
  -- public     → application tables
  -- auth       → Supabase Auth (managed)
  -- storage    → Supabase Storage (managed)
  -- extensions → PostgreSQL extensions
  ```

- **SHOULD** keep application tables in the `public` schema unless there is
  a specific reason to separate them (e.g., multi-tenant isolation, separating
  internal tooling from the application)

### 2.10 Quick Reference Table

| Object             | Convention                           | Example                                          |
|--------------------|--------------------------------------|--------------------------------------------------|
| Table              | `snake_case`, plural                 | `service_appointments`                           |
| Column             | `snake_case`                         | `total_amount_cents`                             |
| Primary key (col)  | `id`                                 | `users.id`                                       |
| Foreign key (col)  | `<entity_singular>_id`               | `vehicles.user_id`                               |
| Boolean column     | `is_` / `has_` prefix                | `is_active`, `has_verified_email`                |
| Timestamp column   | `_at` suffix                         | `created_at`, `published_at`                     |
| Date column        | `_on` suffix                         | `birth_on`, `due_on`                             |
| Money column       | `_cents` suffix (integer)            | `price_cents`, `discount_cents`                  |
| Index              | `idx_<table>_<columns>`              | `idx_vehicles_make_model`                        |
| Unique index       | `uniq_<table>_<columns>`             | `uniq_users_email`                               |
| PK constraint      | `pk_<table>`                         | `pk_users`                                       |
| FK constraint      | `fk_<table>_<column>`                | `fk_vehicles_user_id`                            |
| Check constraint   | `chk_<table>_<description>`          | `chk_orders_total_positive`                      |
| Enum type          | `snake_case`, singular               | `order_status`, `vehicle_fuel_type`              |
| Enum values        | `snake_case`                         | `'in_progress'`, `'plug_in_hybrid'`              |
| Function           | `snake_case`, verb prefix            | `calculate_invoice_total()`                      |
| Trigger            | `trg_<table>_<event>_<description>`  | `trg_users_before_update_set_updated_at`         |
| RLS policy         | `<operation>_<table>_<description>`  | `select_vehicles_own`                            |
| Schema             | `snake_case`                         | `reporting`, `internal`                          |

---

## 3. Schema Design

Schema design is the most consequential set of decisions in a database. A
well-designed schema makes queries simple, constraints enforceable, and
evolution manageable. A poorly designed schema creates workarounds that
compound over time.

This section defines the standard patterns for data types, primary keys,
standard columns, and table structure.

### 3.1 Data Type Selection

PostgreSQL offers a rich type system. Choosing the right type at design time
prevents an entire class of bugs and eliminates the need for application-level
type coercion.

#### Type Selection Guide

| Data | Correct Type | Avoid | Why |
|---|---|---|---|
| Identifiers (PKs, FKs) | `UUID` | `SERIAL`, `BIGSERIAL` | Non-sequential, safe to expose in APIs, no enumeration attacks |
| Short text (names, titles) | `VARCHAR(n)` | `TEXT` without constraint | Enforces max length at DB level |
| Long text (descriptions, notes) | `TEXT` | `VARCHAR(10000)` | TEXT has no performance difference; use CHECK for limits when needed |
| Monetary values | `INTEGER` (cents) | `NUMERIC`, `FLOAT`, `REAL` | Avoids floating-point errors; `_cents` suffix makes unit explicit (→ See [Section 2.2](#22-columns)) |
| Timestamps (events in time) | `TIMESTAMPTZ` | `TIMESTAMP` (without tz) | Always stores UTC; renders correctly in any timezone |
| Dates (no time component) | `DATE` | `TIMESTAMPTZ` | Semantically correct; avoids timezone confusion for pure dates |
| Booleans | `BOOLEAN` | `INTEGER` (0/1), `TEXT` ('yes'/'no') | Native type; enforced by PostgreSQL |
| Enumerations | `custom ENUM` or `TEXT` + CHECK | `INTEGER` codes | Readable in queries; self-documenting |
| Semi-structured data | `JSONB` | `JSON`, `TEXT` | Binary format, indexable with GIN, supports containment operators |
| IP addresses | `INET` | `TEXT` | Native validation, supports range queries and subnet matching |
| Email addresses | `CITEXT` (or `TEXT` + lower) | `VARCHAR` | Case-insensitive comparison without `LOWER()` in every query |

#### Rules

- **MUST** use `TIMESTAMPTZ` (timestamp with time zone) for all temporal data —
  never use `TIMESTAMP` without timezone. PostgreSQL stores `TIMESTAMPTZ` in UTC
  internally and converts to the session timezone on display. `TIMESTAMP` without
  timezone silently drops timezone information, creating bugs in any multi-timezone
  scenario
  (→ See [02-technology-radar.md, Section 4.8 — PostgreSQL Configuration Baseline])

- **MUST** use `UUID` for primary keys
  (→ See [Section 3.2](#32-primary-keys--identifiers))

- **MUST** use `INTEGER` for monetary values, stored in the smallest currency unit
  (→ See [Section 2.2](#22-columns) for naming convention)

- **SHOULD** use `JSONB` instead of `JSON` — `JSONB` stores data in a decomposed
  binary format that supports indexing, containment queries (`@>`), and does not
  preserve duplicate keys or whitespace. `JSON` stores raw text and must be
  re-parsed on every access

- **SHOULD** prefer `TEXT` over `VARCHAR(n)` for columns where the maximum length
  is not a meaningful business constraint — add a `CHECK` constraint when a
  reasonable maximum exists:

  ```sql
  -- GOOD — TEXT with explicit CHECK when limit matters
  description TEXT CONSTRAINT chk_vehicles_description_length
    CHECK (char_length(description) <= 5000),

  -- GOOD — VARCHAR when the limit is a known business rule
  vin VARCHAR(17) NOT NULL,  -- VIN is always exactly 17 characters

  -- AVOID — arbitrary VARCHAR limits that are not business rules
  description VARCHAR(255),  -- why 255? what happens at 256?
  ```

- **SHOULD** use the `CITEXT` extension for case-insensitive text fields
  (like email) when available — it eliminates the need for `LOWER()` in every
  query and unique constraint:

  ```sql
  -- With CITEXT (preferred)
  CREATE EXTENSION IF NOT EXISTS citext;
  email CITEXT NOT NULL,

  -- Without CITEXT (alternative)
  email TEXT NOT NULL,
  -- Requires LOWER() in queries and unique index:
  CREATE UNIQUE INDEX uniq_users_email ON users (LOWER(email));
  ```

### 3.2 Primary Keys & Identifiers

- **MUST** use `UUID` as the primary key type for all tables:

  ```sql
  CREATE TABLE vehicles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ...
  );
  ```

- **MUST** use `gen_random_uuid()` (PostgreSQL 13+ built-in) as the default
  value — this generates UUIDv4, which is random and non-sequential

- **MUST NOT** expose sequential IDs (`SERIAL`, `BIGSERIAL`) in public-facing APIs —
  sequential IDs leak information (total record count, creation order) and enable
  enumeration attacks (→ See [07-security-standards.md, Section 10])

> **Why UUID over SERIAL?**
>
> Sequential IDs (`1, 2, 3, ...`) have three problems in modern applications:
> 1. **Security** — an attacker can guess other valid IDs by incrementing
>    (`/api/users/1`, `/api/users/2`, ...). UUIDs are unguessable.
> 2. **Merging** — if two databases are merged (multi-tenant, migration),
>    sequential IDs collide. UUIDs do not.
> 3. **Client-side generation** — UUIDs can be generated client-side before
>    the database insert, enabling optimistic UI patterns. Sequential IDs
>    require a round-trip.
>
> **Performance note:** UUIDv4 is random, which means inserts are scattered
> across the B-tree index. For most applications (< millions of rows), this
> has negligible impact. If insert performance on very large tables becomes
> measurable, consider UUIDv7 (time-ordered UUIDs) — but measure first,
> do not pre-optimize (→ See [01-core-principles.md, Section 2 — Measure
> Before Optimizing]).

### 3.3 Standard Columns

Every table **MUST** include a set of standard columns that provide consistency
across the entire database.

#### Required Columns (Every Table)

```sql
CREATE TABLE example (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  -- ... domain-specific columns ...
  created_at  TIMESTAMPTZ NOT NULL    DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL    DEFAULT now()
);
```

- **MUST** include `created_at` with default `now()` — records when the row was
  inserted. Immutable after creation.
- **MUST** include `updated_at` with default `now()` — records the last
  modification. Must be updated automatically.

#### Auto-Updating `updated_at`

- **MUST** use a trigger to automatically update `updated_at` on every modification —
  never rely on the application to set this value, because direct SQL operations,
  migrations, and admin scripts would bypass it:

  ```sql
  -- Reusable trigger function (create once, use on every table)
  CREATE OR REPLACE FUNCTION update_updated_at_column()
  RETURNS TRIGGER AS $$
  BEGIN
    NEW.updated_at = now();
    RETURN NEW;
  END;
  $$ LANGUAGE plpgsql;

  -- Apply to each table
  CREATE TRIGGER trg_vehicles_before_update_set_updated_at
    BEFORE UPDATE ON vehicles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
  ```

### 3.4 Soft Delete

Soft delete marks a record as deleted (by setting `deleted_at`) instead of
physically removing it from the database. This provides a safety net for
accidental deletions and supports audit/compliance requirements.

- **SHOULD** use soft delete for important business entities — data that has
  financial, legal, or compliance significance:

  ```sql
  -- Add to tables that require soft delete
  deleted_at  TIMESTAMPTZ  DEFAULT NULL
  ```

- **SHOULD** filter out soft-deleted records by default in all application
  queries — a soft-deleted record should be invisible to normal operations:

  ```sql
  -- Application queries should always include this filter
  SELECT * FROM vehicles WHERE deleted_at IS NULL;

  -- Supabase Client
  const { data } = await supabase
    .from('vehicles')
    .select('*')
    .is('deleted_at', null);
  ```

- **SHOULD** create a partial index to optimize the common "active records"
  query:

  ```sql
  CREATE INDEX idx_vehicles_active ON vehicles (id)
    WHERE deleted_at IS NULL;
  ```

- **MAY** use a view to simplify access to active records:

  ```sql
  CREATE VIEW active_vehicles AS
    SELECT * FROM vehicles WHERE deleted_at IS NULL;
  ```

#### When to Use Soft Delete vs Hard Delete

| Use Soft Delete | Use Hard Delete |
|---|---|
| Users, accounts | Session data, temporary tokens |
| Orders, invoices, payments | Rate limit counters, cache entries |
| Vehicles, products (business entities) | Event queue items (after processing) |
| Any data with legal retention requirements | Data that MUST be deleted for RGPD compliance |
| Data referenced by other records (FK integrity) | Orphaned records with no dependencies |

- **MUST** hard delete when RGPD right-to-erasure requires it — soft delete alone
  does not satisfy the legal requirement to erase personal data. In this case,
  anonymize the record (replace PII with placeholder values) or hard delete it
  (→ See [07-security-standards.md, Section 14 — Right to Erasure])

> **Why not soft delete everything?** Soft-deleted records accumulate over time,
> increasing table size, backup size, and query complexity. They also complicate
> unique constraints — if a user soft-deletes their account and re-registers with
> the same email, the unique constraint on `email` conflicts. Use soft delete
> only where there is a clear business or compliance reason.

### 3.5 Audit Fields

For tables that require an audit trail beyond `created_at` / `updated_at`,
add fields that track who made the change.

- **SHOULD** add `created_by` and `updated_by` on tables where knowing
  the actor is important (e.g., tables modified by multiple users or
  admin actions):

  ```sql
  created_by  UUID  REFERENCES users(id),
  updated_by  UUID  REFERENCES users(id)
  ```

- For full audit trail requirements (before/after values, immutable log),
  → See [07-security-standards.md, Section 15 — Security Logging & Audit Trail].
  The 07 document defines the audit log table structure, trigger-based
  immutability, and retention policies. This document defers to it for
  audit trail implementation.

### 3.6 JSONB Usage Guidelines

PostgreSQL's `JSONB` type is powerful — but it should complement relational
design, not replace it. JSONB is appropriate for truly semi-structured data;
it is not a shortcut for avoiding proper schema design.

#### When JSONB Is Appropriate

| Good Use | Bad Use |
|---|---|
| User preferences (`{ theme: "dark", locale: "pt-PT" }`) | Core business attributes (user name, email, status) |
| Third-party API response caching | Data frequently used in WHERE, JOIN, or ORDER BY |
| Metadata or tags with variable shape | Data with known, stable structure (should be columns) |
| Configuration objects | Relationships between entities (should be FKs) |
| Event payloads, webhook bodies | Anything that needs referential integrity |

#### Rules

- **MUST NOT** use JSONB as the primary storage for data that has a known,
  stable structure — if you know the fields at design time, they should be
  columns with proper types and constraints

- **SHOULD** validate JSONB structure at the application level with Zod before
  inserting — the database cannot enforce JSON shape by default:

  ```ts
  // Validate JSONB shape before insert
  const userPreferencesSchema = z.object({
    theme: z.enum(['light', 'dark']).default('light'),
    locale: z.string().default('pt-PT'),
    notifications: z.object({
      email: z.boolean().default(true),
      push: z.boolean().default(false),
    }).default({}),
  });
  ```

- **SHOULD** index JSONB columns with GIN when you need to query them frequently:

  ```sql
  -- GIN index for containment queries (@>)
  CREATE INDEX idx_vehicles_metadata ON vehicles USING GIN (metadata);

  -- Query using containment
  SELECT * FROM vehicles WHERE metadata @> '{"fuel": "electric"}';
  ```

- **SHOULD** prefer extracting frequently queried JSONB fields into proper
  columns — if you find yourself writing `metadata->>'fuel'` in many queries,
  it should be a `fuel_type` column

### 3.7 Base Table Template

This template combines all standard patterns into a reusable starting point for
any new table. Copy it, rename it, and add domain-specific columns.

```sql
-- ============================================================
-- Table: vehicles
-- Description: Stores vehicle inventory for dealership listings
-- ============================================================

-- Create enum type (if needed)
CREATE TYPE vehicle_fuel_type AS ENUM (
  'gasoline', 'diesel', 'electric', 'hybrid', 'plug_in_hybrid'
);

-- Create table
CREATE TABLE vehicles (
  -- Primary key
  id                UUID        NOT NULL DEFAULT gen_random_uuid(),

  -- Foreign keys
  user_id           UUID        NOT NULL,
  dealership_id     UUID        NOT NULL,

  -- Domain-specific columns
  make              VARCHAR(50) NOT NULL,
  model             VARCHAR(50) NOT NULL,
  year              INTEGER     NOT NULL,
  vin               VARCHAR(17) NOT NULL,
  price_cents       INTEGER     NOT NULL,
  mileage_km        INTEGER     NOT NULL DEFAULT 0,
  fuel_type         vehicle_fuel_type NOT NULL DEFAULT 'gasoline',
  is_available      BOOLEAN     NOT NULL DEFAULT true,
  description       TEXT,
  metadata          JSONB       NOT NULL DEFAULT '{}',

  -- Audit fields
  created_by        UUID,
  updated_by        UUID,

  -- Standard timestamps
  created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at        TIMESTAMPTZ DEFAULT NULL,

  -- Named constraints (all in one place for clarity)
  CONSTRAINT pk_vehicles PRIMARY KEY (id),
  CONSTRAINT fk_vehicles_user_id
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
  CONSTRAINT fk_vehicles_dealership_id
    FOREIGN KEY (dealership_id) REFERENCES dealerships(id) ON DELETE RESTRICT,
  CONSTRAINT fk_vehicles_created_by
    FOREIGN KEY (created_by) REFERENCES users(id),
  CONSTRAINT fk_vehicles_updated_by
    FOREIGN KEY (updated_by) REFERENCES users(id),
  CONSTRAINT uniq_vehicles_vin UNIQUE (vin),
  CONSTRAINT chk_vehicles_year_reasonable
    CHECK (year BETWEEN 1886 AND EXTRACT(YEAR FROM now()) + 2),
  CONSTRAINT chk_vehicles_price_positive
    CHECK (price_cents > 0),
  CONSTRAINT chk_vehicles_mileage_non_negative
    CHECK (mileage_km >= 0)
);

-- Indexes
CREATE INDEX idx_vehicles_user_id ON vehicles (user_id);
CREATE INDEX idx_vehicles_dealership_id ON vehicles (dealership_id);
CREATE INDEX idx_vehicles_make_model ON vehicles (make, model);
CREATE INDEX idx_vehicles_active ON vehicles (id) WHERE deleted_at IS NULL;

-- Auto-update timestamp trigger
CREATE TRIGGER trg_vehicles_before_update_set_updated_at
  BEFORE UPDATE ON vehicles
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
```

> **Note:** This template uses named constraints declared at the bottom of the
> `CREATE TABLE` statement (not inline). This approach is preferred because it
> keeps all constraints visible in one place and makes them easy to reference
> in future migrations (`ALTER TABLE DROP CONSTRAINT fk_vehicles_user_id`).

#### Transactions

- **MUST** wrap multi-table mutations in a database transaction — if
  an operation modifies two or more tables and the changes are
  interdependent, partial completion MUST NOT be possible
- **MUST** use Prisma's `$transaction()` or Supabase RPC functions for
  transactional operations — never rely on sequential independent queries
```ts
// BAD — two independent operations, second can fail leaving orphan data
await orderRepository.create(orderData);
await inventoryRepository.decrement(orderData.items);

// GOOD — atomic, both succeed or both roll back
await prisma.$transaction(async (tx) => {
  await tx.order.create({ data: orderData });
  await tx.inventory.updateMany({ /* decrement */ });
});
```

> **Why:** Without transactions, a failure between two related writes
> leaves the database in an inconsistent state. The AI MUST default to
> transactional writes whenever multiple tables are involved.

---

### 3.8 Agent State & Memory Storage

When an AI agent persists state, its memory is ordinary relational data and **MUST** follow the
same rules as any other table — the only addition is mandatory *scoping*. The memory *model*
(working / long-term / episodic) is defined by → See [12-ai-engineering.md, §6.5]; this section
owns the *storage shape*.

**Rules:**

- Every memory row **MUST** carry explicit scope keys — at minimum a `principal_id` (the user/tenant
  the memory belongs to), plus `agent_id` and `run_id` where the layer requires it. Memory without a
  scope key is a cross-user leak waiting to happen.
- Memory tables **MUST** be protected by RLS scoped to the principal, exactly like any user-owned
  resource — recall is never allowed to cross principals. → See Section 7 (RLS, authoritative);
  [07-security-standards.md, §5].
- Variable-shaped memory content (facts, summaries, tool results) **SHOULD** use a typed `JSONB`
  column rather than a wide sparse schema. → See §3.6 (JSONB guidelines).
- Episodic / long-term memory recalled by similarity is a RAG retrieval concern, not a bespoke
  mechanism — store and index it like any embedded corpus. → See [12-ai-engineering.md, §3.3]
  (ingestion & vector storage); [02-technology-radar.md, §3.28] (pgvector / HNSW).
- Memory rows **MUST** carry the standard `created_at` / `updated_at` columns so retention and
  right-to-erasure apply. → See §3.5 (audit fields); [07-security-standards.md, §14] (RGPD).

**Why:**

Treating agent memory as a special store is the mistake — it is just scoped, authorized, retained
data. The failure mode is forgetting the scope key: a single missing `principal_id` (or an RLS gap)
turns "remember my preferences" into "remember everyone's preferences" — both a privacy breach and a
persistent-injection vector (recalled memory is untrusted input → [12-ai-engineering.md, §6.5, §6.7]).
Reusing the existing RLS, JSONB, and audit-field machinery keeps memory boundedly safe without
inventing anything new.

---

### 3.9 Vector Storage for RAG (pgvector + HNSW)

Embeddings are stored as a native pgvector column in the same database as related app data. This
section owns the *storage + index mechanics*; the **tool** choice (pgvector vs a dedicated vector
DB) is the radar's (→ [02-technology-radar.md, §3.28]) and RAG chunking/ingestion is
→ [12-ai-engineering.md, §3.3]'s.

**Rules:**

- Embeddings **MUST** be stored co-located with related relational data (one query can filter by
  metadata, enforce RLS, and join) — reach for a dedicated vector DB only on *measured* need
  (≳10M vectors or sub-5ms tail latency). → See [02-technology-radar.md, §3.28].
- Column type by dimension: use `vector(N)` for N ≤ 2000; use `halfvec(N)` for N > 2000 (e.g.
  3072-dim models). `vector` caps HNSW at 2000 dims; `halfvec` reaches 4000 and halves storage at
  negligible recall cost.
- The index **MUST** default to **HNSW** (robust to updates, no pre-population needed). Reserve
  IVFFlat for large, static datasets where build memory dominates. → See Section 8.
- The HNSW operator class **MUST** match the query distance operator — `*_cosine_ops` ↔ `<=>`,
  `*_l2_ops` ↔ `<->`, `*_ip_ops` ↔ `<#>`. A mismatch silently returns wrong neighbours. Cosine is
  the default for normalized text embeddings.
- HNSW build params start at `m=16`, `ef_construction=64`; tune only when recall is *measured*
  insufficient. Recall/latency is traded per-query via `hnsw.ef_search` set with `SET LOCAL` inside
  a transaction — **never** a session-global change (pooled connections leak it).
- Vector tables **MUST** enforce RLS scoped to the owning principal/tenant, like any other table —
  a similarity search with no scope filter is a cross-tenant leak. → See Section 7;
  [07-security-standards.md, §5]. For a dominant tenant, a partial HNSW index keeps the graph small.
- The embedding model and preprocessing **MUST** be identical at index time and query time, or
  similarity is measured in mismatched spaces. → See [12-ai-engineering.md, §3.3].
- Write-heavy corpora accumulate HNSW tombstones on re-ingestion — schedule periodic
  `REINDEX INDEX CONCURRENTLY`. → See §8.7.

**Why:**

An embedding is just another column; the win of pgvector is co-location — filter, authorize (RLS),
and join in one query, with no second datastore to secure or sync. The classic failures are
mechanical: indexing a >2000-dim model on `vector` (rejected — use `halfvec`); an operator-class /
query-operator mismatch (silent wrong results); and a missing scope filter so one tenant's query
returns another's chunks. The scale ceiling is real, which is exactly why the radar reserves a
dedicated vector store for measured need rather than as a default.

**GOOD — halfvec column, matched HNSW operator class, RLS, scoped + transaction-local query:**

```sql
CREATE TABLE document_chunks (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id  UUID NOT NULL REFERENCES tenants(id),      -- scope key for RLS
  content    TEXT NOT NULL,
  embedding  halfvec(3072) NOT NULL,                    -- vector(N) when N <= 2000
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX ON document_chunks USING hnsw (embedding halfvec_cosine_ops);  -- cosine <-> <=>

ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;                      -- Section 7
```

```sql
BEGIN;
SET LOCAL hnsw.ef_search = 80;                          -- transaction-local, never session-global
SELECT id, content
FROM document_chunks
WHERE tenant_id = $1                                    -- scope filter (defense in depth with RLS)
ORDER BY embedding <=> $2::halfvec(3072)                -- cosine, matches halfvec_cosine_ops
LIMIT 5;
COMMIT;
```

---

## 4. Relationships & Referential Integrity

Relational databases exist to model relationships between entities. Foreign keys
are the mechanism that enforces these relationships at the data layer — they
guarantee that a `vehicle.user_id` always points to a real user, and they define
what happens when that user is deleted.

Getting foreign keys and cascade rules right is critical: a missing foreign key
allows orphaned records; a careless `ON DELETE CASCADE` can wipe an entire
dependency chain from a single delete.

### 4.1 Foreign Key Rules

- **MUST** define foreign keys for every relationship — never rely on the
  application to enforce referential integrity. The database is the enforcement
  layer; the application is a convenience:

  ```sql
  -- GOOD — relationship enforced at DB level
  CREATE TABLE vehicles (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID NOT NULL,
    dealership_id UUID NOT NULL,

    CONSTRAINT fk_vehicles_user_id
      FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
    CONSTRAINT fk_vehicles_dealership_id
      FOREIGN KEY (dealership_id) REFERENCES dealerships(id) ON DELETE RESTRICT
  );

  -- BAD — "foreign key" exists only as a naming convention, no enforcement
  CREATE TABLE vehicles (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID NOT NULL,  -- no FK constraint → orphans are possible
    dealership_id UUID NOT NULL   -- no FK constraint → orphans are possible
  );
  ```

- **MUST** index all foreign key columns — PostgreSQL does **not** create
  indexes on FK columns automatically (unlike some other databases). Without
  an index, every `DELETE` or `UPDATE` on the parent table triggers a
  sequential scan on the child table to check for references:

  ```sql
  CREATE INDEX idx_vehicles_user_id ON vehicles (user_id);
  CREATE INDEX idx_vehicles_dealership_id ON vehicles (dealership_id);
  ```

- **MUST** use the naming convention from [Section 2.2](#22-columns) — FK
  columns as `<entity_singular>_id`, FK constraints as `fk_<table>_<column>`

### 4.2 Cascade Rules — The Default Is Safety

The `ON DELETE` and `ON UPDATE` clauses define what happens to child records
when the parent is modified or deleted. The wrong choice can cause silent
data loss.

#### ON DELETE Options

| Action | What Happens | When to Use |
|---|---|---|
| `RESTRICT` (default) | Blocks the delete if child records exist | **Default for most relationships** — forces the application to handle dependencies explicitly |
| `CASCADE` | Deletes all child records automatically | Only for true composition (child cannot exist without parent) |
| `SET NULL` | Sets the FK column to `NULL` | When the relationship is optional and the child should survive |
| `SET DEFAULT` | Sets the FK to its default value | Rarely used; requires a meaningful default |
| `NO ACTION` | Same as RESTRICT but checked at end of transaction | Multi-table operations where order matters |

#### Rules

- **MUST** default to `ON DELETE RESTRICT` — this is the safest option. It
  prevents accidental deletion of a parent that still has dependents, forcing
  the application to explicitly handle the situation:

  ```sql
  -- DEFAULT — safe, explicit
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT
  ```

- **SHOULD** use `ON DELETE CASCADE` **only** for true composition
  relationships — where the child is meaningless without the parent and
  should be deleted along with it:

  ```sql
  -- GOOD — invoice line items cannot exist without the invoice
  FOREIGN KEY (invoice_id) REFERENCES invoices(id) ON DELETE CASCADE

  -- GOOD — order items are part of the order
  FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
  ```

- **SHOULD** use `ON DELETE SET NULL` when the relationship is optional
  and the child record should survive the parent's deletion:

  ```sql
  -- The vehicle record should survive if the assigned salesperson is deleted
  salesperson_id UUID REFERENCES users(id) ON DELETE SET NULL
  ```

- **MUST NOT** use `ON DELETE CASCADE` on relationships where the child has
  independent business value — deleting a user should **not** cascade-delete
  their invoices, orders, or payment records:

  ```sql
  -- DANGEROUS — deleting a user wipes all their financial records
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE  -- ⚠️ NO

  -- SAFE — blocks deletion; application must handle user removal properly
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT  -- ✅ YES
  ```

- **MUST** use `ON UPDATE CASCADE` for natural keys that might change (rare
  with UUIDs) — with UUID primary keys, `ON UPDATE` is almost never relevant
  because UUIDs do not change

#### Decision Guide: Choosing ON DELETE Behavior

```text
Can the child exist without the parent?
 ├── NO (true composition — line item without invoice)
 │    └── ON DELETE CASCADE
 └── YES
      ├── Should the FK become NULL when the parent is removed?
      │    ├── YES (optional relationship — salesperson removed)
      │    │    └── ON DELETE SET NULL
      │    └── NO (FK is NOT NULL)
      │         └── ON DELETE RESTRICT (force explicit handling)
      └── Does the child have independent business value?
           └── YES (orders, invoices, payments)
                └── ON DELETE RESTRICT (always)
```

### 4.3 Relationship Patterns

#### One-to-Many (1:N) — The Most Common

One parent has many children. The FK lives on the child table.

```sql
-- One user has many vehicles
-- FK is on the "many" side (vehicles)
CREATE TABLE vehicles (
  id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
  ...
);
```

#### One-to-One (1:1) — Use Sparingly

One parent has exactly one child. Implemented as a 1:N with a `UNIQUE`
constraint on the FK.

```sql
-- One user has one profile (extended user data)
CREATE TABLE user_profiles (
  id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
  bio     TEXT,
  avatar_url TEXT,
  ...
);
```

- **SHOULD** consider whether a 1:1 relationship should just be additional
  columns on the parent table — a separate table is justified only when:
  - The child data is large and rarely queried (avoid loading it by default)
  - The child data has different access control rules (separate RLS policies)
  - The child data is optional and sparse (many NULLs on the parent would waste space)

#### Many-to-Many (N:M) — Junction Table

Two entities related through an intermediary. Requires a junction (join) table.

```sql
-- A vehicle can have many features; a feature can be on many vehicles
CREATE TABLE vehicle_features (
  vehicle_id  UUID NOT NULL REFERENCES vehicles(id) ON DELETE CASCADE,
  feature_id  UUID NOT NULL REFERENCES features(id) ON DELETE CASCADE,

  -- Junction table primary key: composite of both FKs
  CONSTRAINT pk_vehicle_features PRIMARY KEY (vehicle_id, feature_id),

  -- Standard timestamps
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Indexes for querying from either side
CREATE INDEX idx_vehicle_features_feature_id ON vehicle_features (feature_id);
-- vehicle_id is already indexed by the PK (it is the first column)
```

- **MUST** use a composite primary key on junction tables — `(entity_a_id, entity_b_id)` —
  this enforces uniqueness of the relationship and eliminates the need for
  a separate `id` column

- **SHOULD** add a UUID `id` column to the junction table only if the
  junction itself is an API resource (e.g., an "enrollment" that has its
  own attributes, status, and lifecycle):

  ```sql
  -- Junction with its own identity (it is a domain entity, not just a link)
  CREATE TABLE enrollments (
    id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE RESTRICT,
    course_id  UUID NOT NULL REFERENCES courses(id) ON DELETE RESTRICT,
    status     enrollment_status NOT NULL DEFAULT 'active',
    enrolled_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    CONSTRAINT uniq_enrollments_student_course UNIQUE (student_id, course_id)
  );
  ```

- **SHOULD** use `ON DELETE CASCADE` on both FKs of a pure junction table —
  if the parent entity is deleted, the relationship link should be removed.
  For junction tables that are domain entities (like `enrollments`), use
  `RESTRICT` to force explicit handling

### 4.4 Orphan Prevention

Orphaned records — child rows that reference a non-existent parent — are a
data integrity nightmare. They cause broken queries, misleading reports,
and silent failures.

- **MUST** use foreign keys to prevent orphans — this is the primary purpose
  of FKs (→ See [Section 4.1](#41-foreign-key-rules))

- **MUST NOT** defer FK enforcement in application code with plans to
  "clean up later" — orphans created by bugs or race conditions may never
  be cleaned up

- **SHOULD** audit for orphan records periodically, especially in databases
  that predate the adoption of these standards:

  ```sql
  -- Find orphaned vehicles (user_id points to non-existent user)
  SELECT v.id, v.user_id
  FROM vehicles v
  LEFT JOIN users u ON v.user_id = u.id
  WHERE u.id IS NULL;
  ```

- **SHOULD** handle the "soft delete + FK" dilemma carefully — if a parent
  is soft-deleted (`deleted_at IS NOT NULL`), child records still reference
  a valid row, but the business logic treats it as deleted. Solutions:
  - Filter by `deleted_at IS NULL` in application queries (simplest)
  - Add `deleted_at IS NULL` checks in RLS policies
  - Cascade the soft delete to children (set their `deleted_at` too)

### 4.5 Relationship Anti-Patterns

| Anti-Pattern | Problem | Correct Approach |
|---|---|---|
| **No foreign keys** ("we enforce it in the app") | Application bugs create orphans; direct SQL access bypasses the app | Always define FK constraints |
| **CASCADE on everything** | One delete can wipe an entire dependency chain silently | Default to RESTRICT; CASCADE only for true composition |
| **Polymorphic FK** (`entity_type + entity_id`) | No FK constraint possible; the DB cannot validate the reference | Use junction tables or separate FK columns per type |
| **Self-referencing without depth limit** | Infinite recursion in queries; unbounded tree traversal | Set a max depth in the application; consider `ltree` for deep hierarchies |
| **Missing index on FK column** | Every parent delete/update triggers a sequential scan on the child table | Always create an index on FK columns |
| **Nullable FK on a required relationship** | Allows "partial" data — a vehicle without an owner when ownership is mandatory | Use `NOT NULL` when the relationship is required |

---

## 5. Data Integrity & Constraints

Constraints are the database's immune system. They enforce business rules at
the lowest level — rules that cannot be bypassed by bugs, admin scripts, direct
SQL access, or future developers who did not read the documentation.

Every constraint is a guarantee: "this invariant holds, no matter what." Without
constraints, the only thing standing between your data and corruption is the
hope that every access path validates correctly. Hope is not an engineering
strategy.

This section complements the Defense in Depth model defined in
→ See [07-security-standards.md, Section 3]:

```text
Layer 1: Client-side       → UX feedback (not security)
Layer 2: API boundary      → Schema validation (Zod) — PRIMARY
Layer 3: Service layer     → Business rule validation
Layer 4: Database          → Constraints — LAST SAFETY NET ← this section
```

### 5.1 NOT NULL — The First Line of Defense

`NOT NULL` is the simplest and most impactful constraint. A nullable column
that should never be null is a bug waiting to happen — it forces every query
and every consumer to handle a case that should not exist.

- **MUST** default to `NOT NULL` on every column unless there is a specific
  business reason for the value to be absent. The question is not "should
  this be NOT NULL?" — the question is "is there a valid scenario where
  this value is unknown?":

  ```sql
  -- GOOD — defaults to NOT NULL, nullable only when justified
  CREATE TABLE vehicles (
    id            UUID        NOT NULL DEFAULT gen_random_uuid(),
    make          VARCHAR(50) NOT NULL,
    model         VARCHAR(50) NOT NULL,
    year          INTEGER     NOT NULL,
    vin           VARCHAR(17) NOT NULL,
    price_cents   INTEGER     NOT NULL,
    is_available  BOOLEAN     NOT NULL DEFAULT true,
    description   TEXT,               -- nullable: description is optional
    deleted_at    TIMESTAMPTZ,        -- nullable: NULL means "not deleted"
    ...
  );
  ```

- **MUST** justify nullable columns — if a column allows NULL, the developer
  should be able to explain what NULL means in the business context:

  | Column | Nullable? | Why |
  |---|---|---|
  | `email` | NOT NULL | Every user must have an email |
  | `phone` | NULL | Phone is optional at registration |
  | `deleted_at` | NULL | NULL means "active" (not deleted) |
  | `salesperson_id` | NULL | Vehicle may not yet have an assigned salesperson |
  | `price_cents` | NOT NULL | A vehicle listing without a price is invalid |

### 5.2 UNIQUE Constraints

- **MUST** enforce uniqueness at the database level for naturally unique fields —
  application-level checks are subject to race conditions (two requests
  checking simultaneously, both finding no conflict, both inserting):

  ```sql
  -- GOOD — database guarantees uniqueness, even under concurrency
  CONSTRAINT uniq_users_email UNIQUE (email)

  -- BAD — application-level check (race condition)
  -- 1. Request A: SELECT email → not found
  -- 2. Request B: SELECT email → not found
  -- 3. Request A: INSERT → success
  -- 4. Request B: INSERT → success (duplicate!)
  ```

- **SHOULD** use unique indexes instead of unique constraints when you need
  partial uniqueness or expression-based uniqueness:

  ```sql
  -- Unique email, but only for active (non-deleted) users
  -- This allows a soft-deleted user to re-register with the same email
  CREATE UNIQUE INDEX uniq_users_email_active
    ON users (email)
    WHERE deleted_at IS NULL;

  -- Case-insensitive unique email (without CITEXT)
  CREATE UNIQUE INDEX uniq_users_email_lower
    ON users (LOWER(email));
  ```

- **SHOULD** use composite unique constraints for combinations that must be
  unique together:

  ```sql
  -- A user can only have one role per organization
  CONSTRAINT uniq_user_org_roles_user_org
    UNIQUE (user_id, organization_id)

  -- A product can only appear once per order
  CONSTRAINT uniq_order_items_order_product
    UNIQUE (order_id, product_id)
  ```

### 5.3 CHECK Constraints

CHECK constraints enforce domain-level business rules that go beyond type
and nullability — ranges, formats, relationships between columns.

- **MUST** use CHECK constraints for rules that are always true, regardless
  of the application:

  ```sql
  -- Prices must be positive
  CONSTRAINT chk_vehicles_price_positive
    CHECK (price_cents > 0)

  -- Year must be reasonable (first car was 1886)
  CONSTRAINT chk_vehicles_year_reasonable
    CHECK (year BETWEEN 1886 AND EXTRACT(YEAR FROM now()) + 2)

  -- Mileage cannot be negative
  CONSTRAINT chk_vehicles_mileage_non_negative
    CHECK (mileage_km >= 0)

  -- Discount percentage must be between 0 and 100
  CONSTRAINT chk_promotions_discount_range
    CHECK (discount_percent BETWEEN 0 AND 100)

  -- End date must be after start date
  CONSTRAINT chk_promotions_date_order
    CHECK (end_at > start_at)
  ```

- **SHOULD** name CHECK constraints descriptively using the pattern from
  [Section 2.5](#25-constraints) — `chk_<table>_<description>`. A developer
  reading the constraint name should understand what it enforces without
  looking at the expression

- **SHOULD** keep CHECK constraints simple — they should validate data
  invariants, not implement business logic. Complex multi-table rules
  belong in the service layer or in database functions:

  ```sql
  -- GOOD — simple invariant, always true
  CHECK (price_cents > 0)

  -- AVOID — complex business rule that may need to change
  CHECK (
    CASE WHEN status = 'shipped' THEN tracking_number IS NOT NULL
         WHEN status = 'cancelled' THEN cancelled_at IS NOT NULL
    END
  )
  -- This belongs in application validation, not a CHECK constraint,
  -- because the state machine rules are business logic that evolves
  ```

### 5.4 Enums vs CHECK vs Lookup Tables

There are three ways to restrict a column to a set of allowed values.
Each has trade-offs:

| Approach | Add New Value | Remove Value | Referential Integrity | Best For |
|---|---|---|---|---|
| **PostgreSQL ENUM** | Requires `ALTER TYPE` (migration) | Difficult (requires recreating the type) | No | Small, stable sets (status, fuel type) |
| **CHECK constraint** | Requires `ALTER TABLE` (migration) | Requires `ALTER TABLE` | No | Small sets where enum type overhead is not wanted |
| **Lookup table + FK** | Insert a row (no migration) | Delete a row | Yes (FK enforced) | Large or frequently changing sets (countries, categories) |

#### Rules

- **SHOULD** use PostgreSQL `ENUM` types for small, stable value sets
  (3–10 values that rarely change):

  ```sql
  CREATE TYPE order_status AS ENUM (
    'pending', 'confirmed', 'processing', 'shipped', 'delivered', 'cancelled'
  );

  -- Usage
  status order_status NOT NULL DEFAULT 'pending'
  ```

- **SHOULD** use CHECK constraints when you want to avoid creating a
  custom type for a very small set (2–3 values):

  ```sql
  -- Simple enough for a CHECK
  priority TEXT NOT NULL DEFAULT 'medium'
    CONSTRAINT chk_tasks_priority CHECK (priority IN ('low', 'medium', 'high'))
  ```

- **SHOULD** use a lookup table when the set of values is large, changes
  frequently, or needs additional attributes (description, display order,
  active/inactive status):

  ```sql
  -- Lookup table for vehicle categories
  CREATE TABLE vehicle_categories (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(50) NOT NULL,
    slug        VARCHAR(50) NOT NULL,
    description TEXT,
    is_active   BOOLEAN NOT NULL DEFAULT true,
    sort_order  INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT uniq_vehicle_categories_slug UNIQUE (slug)
  );

  -- Reference via FK
  CREATE TABLE vehicles (
    ...
    category_id UUID NOT NULL REFERENCES vehicle_categories(id) ON DELETE RESTRICT,
    ...
  );
  ```

- **SHOULD** know the ENUM migration caveat — adding a value to an ENUM is
  straightforward, but removing or renaming a value is not:

  ```sql
  -- Adding a value — simple, safe
  ALTER TYPE order_status ADD VALUE 'refunded' AFTER 'cancelled';

  -- Removing a value — complex, requires:
  -- 1. Update all rows using the old value
  -- 2. Create a new type without the old value
  -- 3. Alter the column to use the new type
  -- 4. Drop the old type
  -- → This is why ENUM works best for STABLE sets
  ```

### 5.5 DEFAULT Values

Sensible defaults reduce the number of fields the application needs to
provide on insert, preventing accidental NULLs and simplifying queries.

- **MUST** set defaults for columns where a sensible default exists:

  ```sql
  -- Standard defaults
  id          UUID        NOT NULL DEFAULT gen_random_uuid(),
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  is_active   BOOLEAN     NOT NULL DEFAULT true,
  role        TEXT        NOT NULL DEFAULT 'user',
  metadata    JSONB       NOT NULL DEFAULT '{}',
  sort_order  INTEGER     NOT NULL DEFAULT 0,
  ```

- **MUST NOT** set defaults that hide missing data — if the application
  should explicitly provide a value, do not add a default:

  ```sql
  -- BAD — hides the fact that the application forgot to set the price
  price_cents INTEGER NOT NULL DEFAULT 0

  -- GOOD — forces the application to provide a price
  price_cents INTEGER NOT NULL  -- INSERT will fail if price is missing
  ```

### 5.6 Constraint Validation vs Application Validation

Constraints and application validation serve different purposes and operate
at different levels. Both are necessary; neither replaces the other.

| Concern | Database Constraint | Application Validation (Zod) |
|---|---|---|
| **Purpose** | Guarantee data integrity as the last safety net | Provide fast feedback and user-friendly error messages |
| **Bypassed by** | Nothing (short of superuser DDL) | Bugs, direct SQL, migrations, admin scripts |
| **Error messages** | Technical (`violates check constraint "chk_..."`) | User-friendly (`"Price must be greater than zero"`) |
| **Scope** | Single-table, single-row rules | Cross-entity, cross-service business rules |
| **Performance** | Negligible (checked at write time) | Runs before the query reaches the DB |
| **Change process** | Requires migration | Code change + deploy |

- **MUST** validate at the API boundary with Zod **and** enforce at the
  database level with constraints — the application provides the error
  messages; the database provides the guarantee
  (→ See [03-api-design.md, Section 6 — Input Validation])

- **SHOULD** handle constraint violation errors gracefully in the application —
  when a constraint fires, it means the application validation missed
  something. Log this as a warning (it may indicate a validation gap) and
  return a generic error to the client:

  ```ts
  // In the error handler — catch constraint violations
  if (error.code === '23505') {
    // Unique constraint violation
    // Log: this means Zod validation missed a duplicate check
    logger.warn('Unique constraint violation caught at DB level', {
      constraint: error.constraint,
      detail: error.detail,
    });
    throw new ConflictError('A record with this value already exists');
  }

  if (error.code === '23503') {
    // Foreign key constraint violation
    throw new BadRequestError('Referenced record does not exist');
  }

  if (error.code === '23514') {
    // Check constraint violation
    logger.warn('Check constraint violation caught at DB level', {
      constraint: error.constraint,
    });
    throw new BadRequestError('Invalid data');
  }
  ```

### 5.7 Constraint Anti-Patterns

| Anti-Pattern | Problem | Correct Approach |
|---|---|---|
| **All columns nullable** ("we'll validate in the app") | App bugs or direct SQL can insert incomplete data | Default to NOT NULL; nullable only with business justification |
| **No CHECK constraints** ("the app handles it") | Direct SQL, migrations, and admin scripts bypass the app | Add CHECK for invariants that must always hold |
| **Unique only in the app** (check-then-insert) | Race conditions create duplicates under concurrent requests | Use UNIQUE constraint or unique index |
| **Over-constraining** (complex business logic in CHECK) | Business rules change; migrations become frequent and risky | Keep DB constraints simple; put evolving rules in the service layer |
| **Default value that hides errors** (`DEFAULT 0` on price) | Missing price silently becomes 0 instead of failing | Only default values that are semantically correct |
| **Using triggers for simple validation** | Triggers are opaque and hard to debug | Prefer CHECK constraints for simple rules; triggers for cross-row or cross-table logic |

---

## 6. Migration Standards

Migrations are version-controlled, sequential scripts that evolve the database
schema over time. They are the **only** sanctioned way to change the production
database — not the dashboard, not a manual SQL session, not "just this once."

A migration is a commitment: once applied in production, it becomes part of
the project's permanent history. Getting migration discipline right prevents
data loss, environment drift, and deployment failures.

### 6.1 Fundamental Rules

- **MUST** track all schema changes via versioned migrations — the database
  schema is code and deserves the same discipline as application code
  (→ See [Section 1.5 — The Database Outlives the Application])

- **MUST NOT** alter the production database directly — not via the Supabase
  dashboard, not via `psql`, not via any tool outside the migration pipeline.
  Every change must flow through a migration file that is reviewed, tested,
  and version-controlled:

  ```text
  ✅ Migration file → Code review → CI → Deploy → Applied to production
  ❌ Dashboard → Click → Production changed (no history, no review, no rollback)
  ```

- **MUST** store migration files in version control alongside the application
  code — migrations are part of the deployment artifact

- **MUST NOT** edit or modify a migration that has already been applied to
  any shared environment (staging, production) — once applied, a migration
  is immutable history. If a migration was wrong, create a new migration
  to fix it

- **MUST** ensure that every developer on the team can recreate the entire
  database from scratch by running all migrations in sequence — migrations
  are the source of truth for the schema, not a database dump

### 6.2 Migration Tooling

The migration tool depends on the project stack
(→ See [02-technology-radar.md, Section 6.3 — Choosing a Database Strategy]):

| Stack | Migration Tool | Migration Location |
|---|---|---|
| Supabase projects | Supabase CLI (`supabase migration new`) | `supabase/migrations/` |
| Prisma projects | Prisma Migrate (`prisma migrate dev`) | `prisma/migrations/` |
| Raw SQL projects | Numbered SQL files (manual or `dbmate`) | `db/migrations/` |

#### Supabase CLI (Default)

```bash
# Create a new migration
supabase migration new add_vehicles_table

# Creates: supabase/migrations/20260315143200_add_vehicles_table.sql
# Write your SQL in this file, then:

# Apply locally
supabase db reset  # recreates local DB from all migrations

# Push to remote (linked project)
supabase db push
```

#### Prisma Migrate (Adopt — v7)

```bash
# Create and apply a migration
npx prisma migrate dev --name add_vehicles_table

# Creates: prisma/migrations/20260315143200_add_vehicles_table/migration.sql
# Prisma generates the SQL from schema.prisma changes

# Apply to production
npx prisma migrate deploy
```

- **MUST** configure `prisma.config.ts` with the **direct** connection URL for
  migrations — Prisma CLI needs a direct connection, not the pooled one:

  ```ts
  // prisma.config.ts
  import 'dotenv/config';
  import { defineConfig, env } from 'prisma/config';

  export default defineConfig({
    schema: 'prisma/schema.prisma',
    migrations: { path: 'prisma/migrations' },
    datasource: {
      url: env('DIRECT_URL'),  // direct connection for migrations
    },
  });
  ```

- **SHOULD** review the SQL that Prisma generates — Prisma auto-generates
  migrations from schema changes, but the generated SQL may not be optimal.
  Always read the `migration.sql` file before committing

### 6.3 Migration File Naming

- **MUST** use a timestamp prefix for ordering — this prevents conflicts when
  multiple developers create migrations concurrently:

  ```
  # Supabase format (auto-generated)
  20260315143200_add_vehicles_table.sql
  20260316091500_add_vehicle_features_junction.sql
  20260317102000_create_rls_policies_vehicles.sql

  # Pattern
  <YYYYMMDDHHMMSS>_<descriptive_snake_case_name>.sql
  ```

- **MUST** use descriptive names that communicate the change — a developer
  reading the migration list should understand what happened without
  opening the files:

  ```
  # GOOD — clear, specific
  20260315143200_add_vehicles_table.sql
  20260316091500_add_price_cents_column_to_vehicles.sql
  20260317102000_create_idx_vehicles_make_model.sql
  20260318140000_rename_vehicle_type_to_fuel_type.sql
  20260319080000_drop_legacy_cars_table.sql

  # BAD — vague, uninformative
  20260315143200_update.sql
  20260316091500_fix.sql
  20260317102000_changes.sql
  20260318140000_v2.sql
  ```

- **MUST** use verb-first naming that describes the action:

  | Action | Prefix | Example |
  |---|---|---|
  | Create table | `add_` or `create_` | `add_vehicles_table` |
  | Add column | `add_` | `add_price_cents_column_to_vehicles` |
  | Remove column | `drop_` or `remove_` | `drop_legacy_status_from_orders` |
  | Rename | `rename_` | `rename_vehicle_type_to_fuel_type` |
  | Create index | `create_` | `create_idx_vehicles_make_model` |
  | Add constraint | `add_` | `add_chk_vehicles_price_positive` |
  | Create RLS policy | `create_` | `create_rls_policies_vehicles` |
  | Seed data | `seed_` | `seed_vehicle_categories` |
  | Data backfill | `backfill_` | `backfill_vehicles_fuel_type_default` |

### 6.4 Migration Structure

Every migration file should follow a consistent structure:

```sql
-- Migration: 20260315143200_add_vehicles_table.sql
-- Description: Creates the vehicles table for dealership inventory
-- Author: your-name
-- Depends on: users, dealerships tables

-- ============================================================
-- UP: Apply changes
-- ============================================================

-- Create enum type
CREATE TYPE vehicle_fuel_type AS ENUM (
  'gasoline', 'diesel', 'electric', 'hybrid', 'plug_in_hybrid'
);

-- Create table
CREATE TABLE vehicles (
  id              UUID        NOT NULL DEFAULT gen_random_uuid(),
  user_id         UUID        NOT NULL,
  dealership_id   UUID        NOT NULL,
  make            VARCHAR(50) NOT NULL,
  model           VARCHAR(50) NOT NULL,
  year            INTEGER     NOT NULL,
  vin             VARCHAR(17) NOT NULL,
  price_cents     INTEGER     NOT NULL,
  mileage_km      INTEGER     NOT NULL DEFAULT 0,
  fuel_type       vehicle_fuel_type NOT NULL DEFAULT 'gasoline',
  is_available    BOOLEAN     NOT NULL DEFAULT true,
  description     TEXT,
  metadata        JSONB       NOT NULL DEFAULT '{}',
  created_by      UUID,
  updated_by      UUID,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at      TIMESTAMPTZ,

  CONSTRAINT pk_vehicles PRIMARY KEY (id),
  CONSTRAINT fk_vehicles_user_id
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE RESTRICT,
  CONSTRAINT fk_vehicles_dealership_id
    FOREIGN KEY (dealership_id) REFERENCES dealerships(id) ON DELETE RESTRICT,
  CONSTRAINT fk_vehicles_created_by
    FOREIGN KEY (created_by) REFERENCES users(id),
  CONSTRAINT fk_vehicles_updated_by
    FOREIGN KEY (updated_by) REFERENCES users(id),
  CONSTRAINT uniq_vehicles_vin UNIQUE (vin),
  CONSTRAINT chk_vehicles_year_reasonable
    CHECK (year BETWEEN 1886 AND EXTRACT(YEAR FROM now()) + 2),
  CONSTRAINT chk_vehicles_price_positive
    CHECK (price_cents > 0),
  CONSTRAINT chk_vehicles_mileage_non_negative
    CHECK (mileage_km >= 0)
);

-- Indexes
CREATE INDEX idx_vehicles_user_id ON vehicles (user_id);
CREATE INDEX idx_vehicles_dealership_id ON vehicles (dealership_id);
CREATE INDEX idx_vehicles_make_model ON vehicles (make, model);
CREATE INDEX idx_vehicles_active ON vehicles (id) WHERE deleted_at IS NULL;

-- Trigger: auto-update updated_at
CREATE TRIGGER trg_vehicles_before_update_set_updated_at
  BEFORE UPDATE ON vehicles
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- RLS
ALTER TABLE vehicles ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- DOWN: Revert changes (for tools that support rollback)
-- ============================================================

-- DROP TRIGGER trg_vehicles_before_update_set_updated_at ON vehicles;
-- DROP TABLE vehicles;
-- DROP TYPE vehicle_fuel_type;
```

### 6.5 Reversible vs Irreversible Migrations

Not all migrations can be safely reversed. Understanding this distinction is
critical for deployment safety.

#### Reversible (Safe) Operations

These operations can be undone without data loss:

| Operation | Rollback |
|---|---|
| Create table | Drop table |
| Add column (nullable) | Drop column |
| Create index | Drop index |
| Add constraint | Drop constraint |
| Create RLS policy | Drop policy |
| Create enum type | Drop type (if unused) |

#### Irreversible (Destructive) Operations

These operations destroy data or cannot be cleanly reversed:

| Operation | Why Irreversible | Safety Measure |
|---|---|---|
| Drop table | Data is permanently lost | Backup before applying; consider renaming to `_deprecated` first |
| Drop column | Column data is permanently lost | Backup the column data; multi-step migration |
| Change column type (narrowing) | Data may be truncated or lost | Backfill into new column; swap; drop old |
| Remove enum value | Rows using that value become invalid | Update rows first; then alter type |
| Truncate table | All rows deleted | Backup; never in production without explicit approval |

#### Rules for Destructive Migrations

- **MUST** confirm that a recent backup exists before applying any destructive
  migration to production
  (→ See [Section 12 — Backup & Recovery])

- **MUST** use a multi-step approach for dangerous column operations — never
  drop and recreate in a single migration:

  ```text
  Step 1 (Migration A): Add new column, backfill data
  Step 2 (Deploy):      Update application to use new column
  Step 3 (Migration B): Drop old column (after confirming new column works)
  ```

  ```sql
  -- Migration A: Add new column and backfill
  ALTER TABLE vehicles ADD COLUMN fuel_type vehicle_fuel_type;
  UPDATE vehicles SET fuel_type =
    CASE vehicle_type
      WHEN 'gas' THEN 'gasoline'
      WHEN 'ev' THEN 'electric'
      ELSE 'gasoline'
    END;
  ALTER TABLE vehicles ALTER COLUMN fuel_type SET NOT NULL;
  ALTER TABLE vehicles ALTER COLUMN fuel_type SET DEFAULT 'gasoline';

  -- Migration B (after deploy + validation): Drop old column
  ALTER TABLE vehicles DROP COLUMN vehicle_type;
  ```

- **SHOULD** use table renaming instead of dropping when deprecating tables:

  ```sql
  -- Step 1: Rename instead of drop (data preserved)
  ALTER TABLE legacy_cars RENAME TO _deprecated_legacy_cars;

  -- Step 2 (after 30 days with no issues): Drop
  DROP TABLE _deprecated_legacy_cars;
  ```

- **MUST** add a comment in the migration file for any destructive operation
  explaining what data is affected and confirming backup was considered:

  ```sql
  -- ⚠️ DESTRUCTIVE: Dropping column vehicle_type
  -- Data has been migrated to fuel_type in migration 20260318140000
  -- Backup confirmed: 2026-03-19 daily backup includes this column
  ALTER TABLE vehicles DROP COLUMN vehicle_type;
  ```

### 6.6 Large Table Migrations

Operations on large tables (millions of rows) require special care to avoid
locking the table and blocking reads/writes during the migration.

- **MUST** be aware of locking implications — these operations acquire an
  `ACCESS EXCLUSIVE` lock (blocks all access) on the table:

  | Operation | Lock Level | Risk |
  |---|---|---|
  | `ALTER TABLE ADD COLUMN` (with default, PG 11+) | `ACCESS EXCLUSIVE` (brief) | Low — PG 11+ handles this efficiently |
  | `ALTER TABLE ADD COLUMN ... NOT NULL DEFAULT` (PG < 11) | `ACCESS EXCLUSIVE` (rewrites table) | High — rewrites entire table |
  | `ALTER TABLE DROP COLUMN` | `ACCESS EXCLUSIVE` (brief) | Low — marks column as invisible |
  | `ALTER TABLE ALTER COLUMN TYPE` | `ACCESS EXCLUSIVE` (rewrites if type change) | High — may rewrite table |
  | `CREATE INDEX` | `SHARE` lock (blocks writes) | Medium — can be long on large tables |
  | `CREATE INDEX CONCURRENTLY` | No lock (allows writes) | Low — slower but non-blocking |

- **MUST** use `CREATE INDEX CONCURRENTLY` for indexes on large tables
  in production — the standard `CREATE INDEX` blocks writes for the
  duration of the build:

  ```sql
  -- GOOD — non-blocking (production-safe)
  CREATE INDEX CONCURRENTLY idx_vehicles_make_model
    ON vehicles (make, model);

  -- BAD — blocks all writes until the index is built
  CREATE INDEX idx_vehicles_make_model
    ON vehicles (make, model);
  ```

  > **Note:** `CREATE INDEX CONCURRENTLY` cannot run inside a transaction.
  > In Supabase migrations, this means the migration file must contain
  > only this statement (Supabase wraps each migration in a transaction
  > by default).

- **SHOULD** batch data backfills on large tables to avoid long-running
  transactions:

  ```sql
  -- BAD — single UPDATE on millions of rows (locks, WAL bloat)
  UPDATE vehicles SET fuel_type = 'gasoline' WHERE fuel_type IS NULL;

  -- GOOD — batched updates
  DO $$
  DECLARE
    batch_size INT := 10000;
    affected INT;
  BEGIN
    LOOP
      UPDATE vehicles
        SET fuel_type = 'gasoline'
        WHERE id IN (
          SELECT id FROM vehicles
          WHERE fuel_type IS NULL
          LIMIT batch_size
          FOR UPDATE SKIP LOCKED
        );

      GET DIAGNOSTICS affected = ROW_COUNT;
      EXIT WHEN affected = 0;

      COMMIT;
    END LOOP;
  END $$;
  ```

### 6.7 Seed Data

Seed data is initial data required for the application to function — lookup
table values, default roles, admin accounts for development, test fixtures.

- **MUST** separate seed data from schema migrations — seeds are environment-
  specific; schema migrations are universal:

  ```
  supabase/
  ├── migrations/         ← Schema changes (applied everywhere)
  │   ├── 20260315_add_vehicles_table.sql
  │   └── 20260316_add_features_table.sql
  └── seed.sql            ← Seed data (development/staging only)
  ```

- **MUST** make seed scripts idempotent — running the seed twice should not
  fail or create duplicates:

  ```sql
  -- GOOD — idempotent (ON CONFLICT)
  INSERT INTO vehicle_categories (slug, name, sort_order)
  VALUES
    ('sedan', 'Sedan', 1),
    ('suv', 'SUV', 2),
    ('truck', 'Truck', 3),
    ('van', 'Van', 4),
    ('coupe', 'Coupé', 5)
  ON CONFLICT (slug) DO UPDATE SET
    name = EXCLUDED.name,
    sort_order = EXCLUDED.sort_order;

  -- BAD — fails on second run
  INSERT INTO vehicle_categories (slug, name, sort_order)
  VALUES ('sedan', 'Sedan', 1);  -- duplicate key error
  ```

- **MUST NOT** include production secrets or real user data in seed files —
  seeds are committed to version control

- **SHOULD** include enough seed data for meaningful local development — a
  developer should be able to run the application immediately after setup
  and see realistic data

### 6.8 Migration Checklist

Before applying any migration to staging or production:

- [ ] Migration has a descriptive, verb-first name
- [ ] SQL is reviewed (manually for Prisma-generated migrations)
- [ ] Migration runs successfully on a clean database (`supabase db reset`)
- [ ] Migration runs successfully on a database with existing data
- [ ] Destructive operations have confirmed backup availability
- [ ] Large table operations use `CONCURRENTLY` where applicable
- [ ] RLS policies are included for new tables
- [ ] Indexes are created for new FK columns and frequent query patterns
- [ ] Seed data updated if new lookup tables were created
- [ ] The `updated_at` trigger is applied to new tables

---

## 7. Row Level Security (RLS)

> **Ownership note:** This section is the **authoritative source** for RLS
> implementation — policy patterns, helper functions, performance, and
> per-table checklists. The security document
> (→ See [07-security-standards.md, §17]) references RLS in the pre-deployment
> checklist as a verification gate, but this section defines the rules.

Row Level Security is PostgreSQL's mechanism for controlling which rows a user
can see, insert, update, or delete — enforced at the database level. In Supabase
projects, RLS is not optional: it is the **primary security boundary** between
the client and the data.

Without RLS, any client with the `anon` key can read and write every row in
every table. With RLS, the database itself enforces authorization rules —
regardless of how the query was constructed, which client sent it, or whether
the application code has a bug.

This section defines how to implement RLS policies. For the security rationale,
threat model, and authorization architecture:
→ See [07-security-standards.md, Section 5 — Authorization].

### 7.1 Fundamental Rules

- **MUST** enable RLS on **every** table in Supabase projects — no exceptions:

  ```sql
  ALTER TABLE vehicles ENABLE ROW LEVEL SECURITY;
  ```

  > **Why every table?** When RLS is disabled, the table is accessible to anyone
  > with a valid Supabase key (including the `anon` key, which is public).
  > Enabling RLS with no policies means **no access** — the secure default.
  > Policies then grant specific access explicitly.

- **MUST** write explicit policies for each operation — never use "allow all"
  policies in production:

  ```sql
  -- ⚠️ DANGEROUS — allows anyone to read anything
  CREATE POLICY "Enable read access for all users" ON vehicles
    FOR SELECT USING (true);

  -- ✅ SAFE — allows users to read only their own vehicles
  CREATE POLICY select_vehicles_own ON vehicles
    FOR SELECT USING (user_id = auth.uid());
  ```

- **MUST** use the `service_role` key only on the server — it bypasses all RLS
  policies. Exposing it to the client is equivalent to disabling RLS entirely
  (→ See [07-security-standards.md, Section 7 — Secrets Management])

- **MUST** treat RLS as defense in depth, not a replacement for application-level
  authorization — both layers should enforce the same rules independently:

  ```text
  Application layer:  Service → checks user.id === resource.userId
  Database layer:     RLS     → USING (user_id = auth.uid())
  ─────────────────────────────────────────────────────────────
  Result: Even if the application check has a bug, the database
          still blocks unauthorized access.
  ```

### 7.2 How RLS Works in Supabase

Understanding the mechanics is essential for writing correct policies.

#### The Auth Context

Supabase injects the authenticated user's information into every database
connection via PostgreSQL settings. The key functions:

| Function | Returns | Use Case |
|---|---|---|
| `auth.uid()` | The authenticated user's UUID | Ownership checks (`user_id = auth.uid()`) |
| `auth.role()` | The connection role (`anon`, `authenticated`) | Public vs authenticated access |
| `auth.jwt()` | The full JWT payload as JSONB | Custom claims (roles, tenant ID) |

```sql
-- Example: extract a custom role from the JWT
(auth.jwt() ->> 'user_role')::text = 'admin'

-- Example: extract tenant_id from JWT metadata
(auth.jwt() -> 'app_metadata' ->> 'tenant_id')::uuid = tenant_id
```

#### USING vs WITH CHECK

RLS policies have two clauses that serve different purposes:

| Clause | Applies To | Purpose |
|---|---|---|
| `USING (expression)` | SELECT, UPDATE, DELETE | Filters which **existing** rows the user can see or act on |
| `WITH CHECK (expression)` | INSERT, UPDATE | Validates that **new or modified** rows satisfy the policy |

```sql
-- SELECT: user can only see their own vehicles
CREATE POLICY select_vehicles_own ON vehicles
  FOR SELECT
  USING (user_id = auth.uid());

-- INSERT: user can only create vehicles assigned to themselves
CREATE POLICY insert_vehicles_own ON vehicles
  FOR INSERT
  WITH CHECK (user_id = auth.uid());

-- UPDATE: user can only update their own vehicles,
-- and cannot reassign them to another user
CREATE POLICY update_vehicles_own ON vehicles
  FOR UPDATE
  USING (user_id = auth.uid())          -- can only see/target own rows
  WITH CHECK (user_id = auth.uid());    -- cannot change user_id to someone else

-- DELETE: user can only delete their own vehicles
CREATE POLICY delete_vehicles_own ON vehicles
  FOR DELETE
  USING (user_id = auth.uid());
```

> **Critical:** An `UPDATE` policy needs **both** `USING` and `WITH CHECK`.
> `USING` controls which rows the user can target for update. `WITH CHECK`
> controls what the row can look like after the update. Without `WITH CHECK`
> on an UPDATE policy, a user could update `user_id` to someone else's ID,
> effectively transferring ownership.

### 7.3 Common Policy Patterns

#### Pattern 1: Owner-Based Access

The most common pattern — users can only access their own data.

```sql
-- Users can CRUD their own vehicles
CREATE POLICY select_vehicles_own ON vehicles
  FOR SELECT USING (user_id = auth.uid());

CREATE POLICY insert_vehicles_own ON vehicles
  FOR INSERT WITH CHECK (user_id = auth.uid());

CREATE POLICY update_vehicles_own ON vehicles
  FOR UPDATE
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

CREATE POLICY delete_vehicles_own ON vehicles
  FOR DELETE USING (user_id = auth.uid());
```

#### Pattern 2: Role-Based Access

Different access levels based on user roles stored in JWT claims or a
roles table.

```sql
-- Admins can read all vehicles
CREATE POLICY select_vehicles_admin ON vehicles
  FOR SELECT
  USING (
    (auth.jwt() -> 'app_metadata' ->> 'role')::text = 'admin'
  );

-- Managers can read vehicles from their dealership
CREATE POLICY select_vehicles_manager ON vehicles
  FOR SELECT
  USING (
    (auth.jwt() -> 'app_metadata' ->> 'role')::text = 'manager'
    AND dealership_id = (auth.jwt() -> 'app_metadata' ->> 'dealership_id')::uuid
  );

-- Regular users can read only their own vehicles
CREATE POLICY select_vehicles_own ON vehicles
  FOR SELECT
  USING (user_id = auth.uid());
```

> **Note:** Multiple SELECT policies on the same table are combined with
> **OR** logic — a row is visible if **any** SELECT policy allows it.
> Multiple policies for different operations (SELECT vs INSERT vs UPDATE)
> are independent — each operation is evaluated against its own policies.

#### Pattern 3: Tenant Isolation

For multi-tenant applications where each organization's data is isolated.

```sql
-- Helper function: get current user's tenant
CREATE OR REPLACE FUNCTION get_current_tenant_id()
RETURNS UUID AS $$
  SELECT (auth.jwt() -> 'app_metadata' ->> 'tenant_id')::uuid;
$$ LANGUAGE sql SECURITY DEFINER STABLE;

-- All operations scoped to tenant
CREATE POLICY select_vehicles_tenant ON vehicles
  FOR SELECT USING (tenant_id = get_current_tenant_id());

CREATE POLICY insert_vehicles_tenant ON vehicles
  FOR INSERT WITH CHECK (tenant_id = get_current_tenant_id());

CREATE POLICY update_vehicles_tenant ON vehicles
  FOR UPDATE
  USING (tenant_id = get_current_tenant_id())
  WITH CHECK (tenant_id = get_current_tenant_id());

CREATE POLICY delete_vehicles_tenant ON vehicles
  FOR DELETE USING (tenant_id = get_current_tenant_id());
```

#### Pattern 4: Public Read, Authenticated Write

For resources that are publicly visible but only modifiable by their owners.

```sql
-- Anyone can read available vehicles (even anonymous users)
CREATE POLICY select_vehicles_public ON vehicles
  FOR SELECT USING (is_available = true AND deleted_at IS NULL);

-- Only authenticated owners can insert/update/delete
CREATE POLICY insert_vehicles_own ON vehicles
  FOR INSERT WITH CHECK (
    auth.role() = 'authenticated'
    AND user_id = auth.uid()
  );

CREATE POLICY update_vehicles_own ON vehicles
  FOR UPDATE
  USING (user_id = auth.uid())
  WITH CHECK (user_id = auth.uid());

CREATE POLICY delete_vehicles_own ON vehicles
  FOR DELETE USING (user_id = auth.uid());
```

#### Pattern 5: No Client Access (Server-Only Tables)

For tables that should only be accessed by the backend using the
`service_role` key (e.g., audit logs, internal configuration).

```sql
-- Enable RLS with NO policies → no access via anon/authenticated roles
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
-- No CREATE POLICY statements
-- Only service_role (which bypasses RLS) can access this table
```

### 7.4 RLS Helper Functions

Complex policy expressions become repetitive and error-prone. Extract them
into `SECURITY DEFINER` functions for reuse and clarity.

- **SHOULD** create helper functions for policy expressions that are used
  across multiple tables:

  ```sql
  -- Check if the current user is an admin
  CREATE OR REPLACE FUNCTION is_admin()
  RETURNS BOOLEAN AS $$
    SELECT (auth.jwt() -> 'app_metadata' ->> 'role')::text = 'admin';
  $$ LANGUAGE sql SECURITY DEFINER STABLE;

  -- Check if the current user belongs to a specific dealership
  CREATE OR REPLACE FUNCTION belongs_to_dealership(p_dealership_id UUID)
  RETURNS BOOLEAN AS $$
    SELECT (auth.jwt() -> 'app_metadata' ->> 'dealership_id')::uuid = p_dealership_id;
  $$ LANGUAGE sql SECURITY DEFINER STABLE;

  -- Usage in policies (much cleaner)
  CREATE POLICY select_vehicles_admin ON vehicles
    FOR SELECT USING (is_admin());

  CREATE POLICY select_vehicles_dealership ON vehicles
    FOR SELECT USING (belongs_to_dealership(dealership_id));
  ```

- **MUST** use `SECURITY DEFINER` for RLS helper functions — this ensures
  the function runs with the privileges of the function owner (typically
  the database owner), not the calling user. Without it, the function
  cannot access `auth.jwt()` correctly in all contexts

- **MUST** mark RLS helper functions as `STABLE` (or `IMMUTABLE` if
  applicable) — this tells PostgreSQL the function returns the same
  result for the same inputs within a single query, enabling the query
  planner to optimize policy evaluation

### 7.5 RLS and Soft Delete

When tables use soft delete (`deleted_at`), RLS policies should filter out
soft-deleted records so they are invisible to normal operations.

- **SHOULD** include `deleted_at IS NULL` in SELECT policies to hide
  soft-deleted records from client queries:

  ```sql
  CREATE POLICY select_vehicles_own ON vehicles
    FOR SELECT
    USING (user_id = auth.uid() AND deleted_at IS NULL);
  ```

- **SHOULD** prevent clients from hard-deleting records on soft-delete
  tables — if soft delete is the strategy, the DELETE policy should either
  block deletes entirely (force the application to use UPDATE to set
  `deleted_at`) or be very restrictive:

  ```sql
  -- Option A: Block all client deletes (prefer soft delete via UPDATE)
  -- Simply do not create a DELETE policy → DELETE is denied by default

  -- Option B: Allow soft delete via UPDATE only
  CREATE POLICY update_vehicles_soft_delete ON vehicles
    FOR UPDATE
    USING (user_id = auth.uid() AND deleted_at IS NULL)
    WITH CHECK (user_id = auth.uid());
  -- The application sets deleted_at via an UPDATE, not a DELETE
  ```

### 7.6 RLS Performance Considerations

RLS policies are evaluated for every row in every query. Inefficient
policies can significantly degrade performance.

- **MUST** ensure that columns referenced in RLS policies are indexed —
  `auth.uid()` comparisons against `user_id` need an index on `user_id`
  (→ See [Section 4.1 — Foreign Key Rules], which already mandates FK
  indexes)

- **SHOULD** keep policy expressions simple — avoid subqueries or joins in
  policies when possible. If a policy requires a join (e.g., checking
  membership in a separate table), consider denormalizing the relevant
  data or using a helper function:

  ```sql
  -- AVOID — subquery in every row evaluation
  CREATE POLICY select_vehicles_team ON vehicles
    FOR SELECT USING (
      dealership_id IN (
        SELECT dealership_id FROM team_members
        WHERE user_id = auth.uid()
      )
    );

  -- BETTER — helper function (can be cached by query planner)
  CREATE OR REPLACE FUNCTION get_user_dealership_ids()
  RETURNS UUID[] AS $$
    SELECT ARRAY(
      SELECT dealership_id FROM team_members
      WHERE user_id = auth.uid()
    );
  $$ LANGUAGE sql SECURITY DEFINER STABLE;

  CREATE POLICY select_vehicles_team ON vehicles
    FOR SELECT USING (
      dealership_id = ANY(get_user_dealership_ids())
    );
  ```

- **SHOULD** use `EXPLAIN ANALYZE` to verify that RLS policies do not cause
  sequential scans on large tables
  (→ See [Section 11 — Performance & Optimization])

### 7.7 RLS Checklist (Per Table)

Before considering a table's RLS complete:

- [ ] RLS is enabled (`ALTER TABLE ... ENABLE ROW LEVEL SECURITY`)
- [ ] Separate policies exist for SELECT, INSERT, UPDATE, DELETE
- [ ] SELECT policy filters by ownership, tenant, or role
- [ ] INSERT policy uses `WITH CHECK` to prevent impersonation
- [ ] UPDATE policy uses **both** `USING` and `WITH CHECK`
- [ ] DELETE policy is either restrictive or absent (soft delete tables)
- [ ] Soft-deleted records are filtered in SELECT policies
- [ ] All columns in policy expressions are indexed
- [ ] Policies are named following the convention from [Section 2.8](#28-rls-policies)
- [ ] Policies are included in the migration file that creates the table
- [ ] RLS behavior is tested (→ See [Section 13 — Database Testing Patterns])

---

## 8. Indexing Strategy

Indexes are the primary tool for query performance. A well-placed index turns a
sequential scan of millions of rows into an instant lookup. A missing index
causes queries to degrade silently as tables grow. An unnecessary index wastes
write performance, storage, and memory.

The principle is simple: **index based on actual query patterns, not guesswork.
Measure first, index second.**
(→ See [01-core-principles.md, Section 2 — Measure Before Optimizing])

### 8.1 When to Create Indexes

- **MUST** index all foreign key columns — PostgreSQL does not create
  these automatically
  (→ See [Section 4.1 — Foreign Key Rules])

- **MUST** index columns that appear in RLS policy expressions —
  unindexed policy columns cause sequential scans on every query
  (→ See [Section 7.6 — RLS Performance])

- **SHOULD** index columns frequently used in `WHERE` clauses:

  ```sql
  -- Frequent query: find vehicles by make and model
  SELECT * FROM vehicles WHERE make = 'Toyota' AND model = 'Corolla';

  -- Index to support it
  CREATE INDEX idx_vehicles_make_model ON vehicles (make, model);
  ```

- **SHOULD** index columns used in `ORDER BY` when combined with
  `WHERE` filtering — without an index, PostgreSQL must sort the
  entire filtered result set:

  ```sql
  -- Frequent query: recent vehicles for a user
  SELECT * FROM vehicles
    WHERE user_id = $1 AND deleted_at IS NULL
    ORDER BY created_at DESC
    LIMIT 20;

  -- Composite index that supports both filtering and sorting
  CREATE INDEX idx_vehicles_user_active_recent
    ON vehicles (user_id, created_at DESC)
    WHERE deleted_at IS NULL;
  ```

- **SHOULD** index columns used in `JOIN` conditions (beyond FK
  columns, which are already indexed)

- **MUST NOT** over-index — every index has a cost:

  | Benefit | Cost |
  |---|---|
  | Faster reads (`SELECT`) | Slower writes (`INSERT`, `UPDATE`, `DELETE`) |
  | Index scan instead of seq scan | Storage space (index data on disk) |
  | | Memory usage (indexes cached in shared_buffers) |
  | | Maintenance overhead (autovacuum, reindex) |

### 8.2 Index Types

PostgreSQL supports multiple index types. Choose based on the query pattern.

#### B-tree (Default)

The default index type. Supports equality (`=`) and range (`<`, `>`,
`BETWEEN`, `<=`, `>=`) queries. Also supports `ORDER BY`, `IS NULL`,
and `LIKE 'prefix%'` (left-anchored patterns).

```sql
-- Equality
CREATE INDEX idx_users_email ON users (email);

-- Range + sorting
CREATE INDEX idx_vehicles_price ON vehicles (price_cents);

-- Multi-column (see Section 8.3)
CREATE INDEX idx_vehicles_make_model ON vehicles (make, model);
```

- **MUST** use B-tree (the default) for most indexes — it is the
  correct choice for the vast majority of query patterns

#### GIN (Generalized Inverted Index)

Designed for values that contain multiple elements — JSONB documents,
arrays, and full-text search vectors.

```sql
-- JSONB containment queries (@>, ?, ?|, ?&)
CREATE INDEX idx_vehicles_metadata ON vehicles USING GIN (metadata);

-- Query: find vehicles with specific metadata
SELECT * FROM vehicles WHERE metadata @> '{"color": "red"}';

-- Full-text search
ALTER TABLE vehicles ADD COLUMN search_vector tsvector;

CREATE INDEX idx_vehicles_search ON vehicles USING GIN (search_vector);

-- Query: full-text search
SELECT * FROM vehicles
  WHERE search_vector @@ to_tsquery('portuguese', 'toyota & corolla');

-- Array containment
CREATE INDEX idx_vehicles_tags ON vehicles USING GIN (tags);

-- Query: find vehicles with a specific tag
SELECT * FROM vehicles WHERE tags @> ARRAY['electric'];
```

- **SHOULD** use GIN for JSONB columns that are queried with containment
  operators (`@>`, `?`, `?|`, `?&`)
- **SHOULD** use GIN for full-text search (`tsvector` + `tsquery`)
- **SHOULD** use GIN for array columns queried with `@>`, `<@`, `&&`

#### GiST (Generalized Search Tree)

Supports geometric, geographic, and range data types. Needed for PostGIS
and range queries.

```sql
-- Geographic queries (PostGIS)
CREATE INDEX idx_dealerships_location
  ON dealerships USING GIST (location);

-- Range queries (e.g., date ranges)
CREATE INDEX idx_promotions_period
  ON promotions USING GIST (tstzrange(start_at, end_at));
```

- **SHOULD** use GiST for geographic data (PostGIS `geometry`/`geography`)
- **MAY** use GiST for range overlap queries (`&&` operator on range types)

#### Quick Reference: Which Index Type?

| Query Pattern | Index Type | Example |
|---|---|---|
| `WHERE x = value` | B-tree | `idx_users_email` |
| `WHERE x BETWEEN a AND b` | B-tree | `idx_vehicles_price` |
| `ORDER BY x` | B-tree | `idx_vehicles_created_at` |
| `WHERE jsonb @> '{...}'` | GIN | `idx_vehicles_metadata` |
| `WHERE tsvector @@ tsquery` | GIN | `idx_vehicles_search` |
| `WHERE array @> ARRAY[...]` | GIN | `idx_vehicles_tags` |
| `WHERE ST_DWithin(geo, ...)` | GiST | `idx_dealerships_location` |
| `WHERE range && range` | GiST | `idx_promotions_period` |

### 8.3 Composite Indexes

A composite (multi-column) index covers queries that filter or sort on
multiple columns. Column order matters significantly.

- **MUST** place the most selective column (the one that filters out the
  most rows) first in a composite index — PostgreSQL reads composite
  indexes left to right:

  ```sql
  -- Query: find active vehicles for a specific user
  SELECT * FROM vehicles
    WHERE user_id = $1 AND is_available = true;

  -- user_id is more selective (filters to ~10 rows)
  -- is_available is less selective (true for ~80% of rows)

  -- GOOD — selective column first
  CREATE INDEX idx_vehicles_user_available
    ON vehicles (user_id, is_available);

  -- LESS EFFECTIVE — non-selective column first
  CREATE INDEX idx_vehicles_available_user
    ON vehicles (is_available, user_id);
  ```

- **MUST** understand the "leftmost prefix" rule — a composite index on
  `(a, b, c)` can satisfy queries on:
  - `WHERE a = ...` ✅
  - `WHERE a = ... AND b = ...` ✅
  - `WHERE a = ... AND b = ... AND c = ...` ✅
  - `WHERE b = ...` ❌ (cannot skip `a`)
  - `WHERE a = ... AND c = ...` ⚠️ (uses `a` only, scans for `c`)

  ```sql
  -- This single composite index supports multiple query patterns
  CREATE INDEX idx_vehicles_dealership_make_model
    ON vehicles (dealership_id, make, model);

  -- Supported:
  SELECT * FROM vehicles WHERE dealership_id = $1;
  SELECT * FROM vehicles WHERE dealership_id = $1 AND make = $2;
  SELECT * FROM vehicles WHERE dealership_id = $1 AND make = $2 AND model = $3;

  -- NOT supported efficiently:
  SELECT * FROM vehicles WHERE make = $1;  -- needs separate index
  ```

- **SHOULD** include the `ORDER BY` column at the end of a composite
  index when queries both filter and sort:

  ```sql
  -- Query: recent vehicles for a user, paginated
  SELECT * FROM vehicles
    WHERE user_id = $1
    ORDER BY created_at DESC
    LIMIT 20;

  -- Index: filter column + sort column
  CREATE INDEX idx_vehicles_user_recent
    ON vehicles (user_id, created_at DESC);
  ```

### 8.4 Partial Indexes

A partial index only includes rows that match a `WHERE` condition. This
makes the index smaller, faster, and cheaper to maintain.

- **SHOULD** use partial indexes for queries that consistently filter on a
  specific condition:

  ```sql
  -- Most queries only care about active (non-deleted) records
  CREATE INDEX idx_vehicles_active
    ON vehicles (id)
    WHERE deleted_at IS NULL;

  -- Only available vehicles appear in search results
  CREATE INDEX idx_vehicles_available_search
    ON vehicles (make, model, price_cents)
    WHERE is_available = true AND deleted_at IS NULL;

  -- Unique email, but only for active users (allows re-registration
  -- after soft delete)
  CREATE UNIQUE INDEX uniq_users_email_active
    ON users (email)
    WHERE deleted_at IS NULL;
  ```

- **SHOULD** use partial indexes to solve the soft-delete unique constraint
  problem — a standard `UNIQUE (email)` prevents a soft-deleted user from
  re-registering. A partial unique index on `WHERE deleted_at IS NULL`
  enforces uniqueness only among active records

### 8.5 Covering Indexes (Index-Only Scans)

A covering index includes all columns needed by a query, allowing
PostgreSQL to satisfy the query entirely from the index without
reading the table (heap). This is called an "index-only scan."

```sql
-- Query: list vehicle IDs and prices for a dealership
SELECT id, price_cents FROM vehicles
  WHERE dealership_id = $1 AND is_available = true;

-- Covering index: includes id and price_cents
CREATE INDEX idx_vehicles_dealership_listing
  ON vehicles (dealership_id, id, price_cents)
  WHERE is_available = true;
```

- **MAY** use `INCLUDE` (PostgreSQL 11+) to add non-key columns to an
  index for covering purposes without affecting the index sort order:

  ```sql
  -- Filter by dealership, but INCLUDE price for index-only scan
  CREATE INDEX idx_vehicles_dealership_with_price
    ON vehicles (dealership_id)
    INCLUDE (id, price_cents)
    WHERE is_available = true;
  ```

- **SHOULD** consider covering indexes only for critical, high-frequency
  queries — they increase index size and should not be used casually

### 8.6 Full-Text Search Indexes

PostgreSQL's built-in full-text search is the default before considering
external tools like Elasticsearch
(→ See [02-technology-radar.md, Section 4.8 — PostgreSQL]).

```sql
-- Step 1: Add a search vector column
ALTER TABLE vehicles
  ADD COLUMN search_vector tsvector
  GENERATED ALWAYS AS (
    setweight(to_tsvector('portuguese', coalesce(make, '')), 'A') ||
    setweight(to_tsvector('portuguese', coalesce(model, '')), 'A') ||
    setweight(to_tsvector('portuguese', coalesce(description, '')), 'B')
  ) STORED;

-- Step 2: Create GIN index
CREATE INDEX idx_vehicles_search ON vehicles USING GIN (search_vector);

-- Step 3: Query
SELECT id, make, model,
  ts_rank(search_vector, query) AS rank
FROM vehicles,
  to_tsquery('portuguese', 'toyota & corolla') AS query
WHERE search_vector @@ query
ORDER BY rank DESC
LIMIT 20;
```

- **SHOULD** use `GENERATED ALWAYS AS ... STORED` for search vectors
  when possible (PostgreSQL 12+) — this keeps the vector automatically
  in sync with the source columns without triggers

- **SHOULD** use `setweight()` to assign different weights to different
  fields — a match in the title (`'A'`) should rank higher than a match
  in the description (`'B'`)

- **SHOULD** use the appropriate text search configuration for the
  target language (`'portuguese'`, `'english'`, `'simple'`)

### 8.7 Index Monitoring

Creating indexes is not a one-time task. Query patterns change, tables
grow, and indexes may become unused or inefficient.

- **SHOULD** monitor for unused indexes periodically — unused indexes
  cost write performance and storage with zero benefit:

  ```sql
  -- Find indexes with zero scans since last stats reset
  SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
  FROM pg_stat_user_indexes
  WHERE idx_scan = 0
    AND indexrelid NOT IN (
      SELECT conindid FROM pg_constraint  -- exclude PK/UNIQUE constraints
      WHERE contype IN ('p', 'u')
    )
  ORDER BY pg_relation_size(indexrelid) DESC;
  ```

- **SHOULD** monitor for missing indexes — queries doing sequential scans
  on large tables:

  ```sql
  -- Tables with high sequential scan counts (potential missing indexes)
  SELECT
    schemaname,
    relname AS table_name,
    seq_scan,
    seq_tup_read,
    idx_scan,
    pg_size_pretty(pg_relation_size(relid)) AS table_size
  FROM pg_stat_user_tables
  WHERE seq_scan > 100
    AND pg_relation_size(relid) > 10 * 1024 * 1024  -- > 10 MB
  ORDER BY seq_tup_read DESC;
  ```

- **SHOULD** check index bloat and reindex when necessary — after many
  updates and deletes, indexes accumulate dead entries:

  ```sql
  -- Reindex a specific index
  REINDEX INDEX CONCURRENTLY idx_vehicles_make_model;

  -- Reindex all indexes on a table
  REINDEX TABLE CONCURRENTLY vehicles;
  ```

### 8.8 Indexing Anti-Patterns

| Anti-Pattern | Problem | Correct Approach |
|---|---|---|
| **Index every column** | Writes become slow; storage balloons; most indexes are never used | Index based on query patterns; monitor usage |
| **No indexes beyond PK** | Queries degrade as tables grow; sequential scans everywhere | Index FK columns, WHERE clauses, ORDER BY columns |
| **Ignoring composite indexes** | Separate single-column indexes are less efficient than one composite index for multi-column queries | Use composite indexes for common multi-column filters |
| **Wrong column order in composite** | Index is not used because the leftmost prefix does not match the query | Put the most selective (equality) column first |
| **Indexing low-cardinality columns alone** | A B-tree index on `is_active` (true/false) is nearly useless — it does not filter enough rows | Use partial indexes or include as part of a composite |
| **`CREATE INDEX` on large prod tables** | Blocks writes for the duration of the build | Use `CREATE INDEX CONCURRENTLY` (→ See [Section 6.6]) |
| **Never monitoring indexes** | Unused indexes accumulate; missing indexes go unnoticed | Review `pg_stat_user_indexes` periodically |

---

## 9. Query Patterns & Data Access

The data access layer is the bridge between the application's business logic and
the database. It is responsible for translating domain operations into efficient
queries and mapping database results back into application types.

This section defines the patterns for structuring data access code, preventing
common query problems, and handling the casing transformation between the
database (`snake_case`) and the application (`camelCase`).

The layering model assumed throughout:
`Route Handler → Service → Repository → Database`
(→ See [01-core-principles.md, Section 6])

### 9.1 The Repository Pattern

The Repository is the **only** layer that touches the database. Services call
repositories; repositories execute queries. This separation ensures that
business logic is decoupled from the specific database client
(→ See [01-core-principles.md, Section 4.5 — Dependency Inversion]).

```text
Service Layer                Repository Layer             Database
──────────────────           ──────────────────           ──────────
- Business logic             - Query construction         - PostgreSQL
- Validation (Zod)           - Casing transformation      - RLS enforcement
- Orchestration              - Error mapping              - Constraints
- Domain types (camelCase)   - snake_case ↔ camelCase     - snake_case
```

#### Repository Structure

- **MUST** isolate all database queries inside repository files — services
  must never construct or execute queries directly:

  ```ts
  // src/repositories/vehicle-repository.ts
  import { supabase } from '@/lib/supabase';
  import { toCamelCase, toSnakeCase } from '@/lib/case-utils';
  import type { Vehicle, CreateVehicleInput } from '@/types/vehicle';

  export const vehicleRepository = {
    async findById(id: string): Promise<Vehicle | null> {
      const { data, error } = await supabase
        .from('vehicles')
        .select('id, make, model, year, price_cents, is_available, created_at')
        .eq('id', id)
        .is('deleted_at', null)
        .single();

      if (error?.code === 'PGRST116') return null; // not found
      if (error) throw error;

      return toCamelCase(data);
    },

    async create(input: CreateVehicleInput): Promise<Vehicle> {
      const { data, error } = await supabase
        .from('vehicles')
        .insert(toSnakeCase(input))
        .select()
        .single();

      if (error) throw error;

      return toCamelCase(data);
    },

    async findByUser(
      userId: string,
      options: { page: number; pageSize: number }
    ): Promise<{ items: Vehicle[]; total: number }> {
      const from = (options.page - 1) * options.pageSize;
      const to = from + options.pageSize - 1;

      const { data, error, count } = await supabase
        .from('vehicles')
        .select('id, make, model, year, price_cents, is_available', { count: 'exact' })
        .eq('user_id', userId)
        .is('deleted_at', null)
        .order('created_at', { ascending: false })
        .range(from, to);

      if (error) throw error;

      return {
        items: (data ?? []).map(toCamelCase),
        total: count ?? 0,
      };
    },
  };
  ```

- **MUST** return domain types (camelCase) from repositories — the service
  layer should never see `snake_case` property names

- **MUST NOT** import Supabase Client, Prisma, or any database client
  outside the repository layer — if you see `supabase.from(...)` in a
  service file, it belongs in a repository

- **SHOULD** name repository files after the entity: `vehicle-repository.ts`,
  `user-repository.ts`, `invoice-repository.ts`
  (→ See [01-core-principles.md, Section 7.6 — Naming Files])

### 9.2 Casing Transformation (snake_case ↔ camelCase)

The database uses `snake_case` (PostgreSQL convention). The application uses
`camelCase` (TypeScript convention). The API sends and receives `camelCase`
(→ See [03-api-design.md, Section 4]). The repository layer is the
**single point** where this transformation happens.

- **MUST** transform database results from `snake_case` to `camelCase` in
  the repository, before returning to the service layer

- **MUST** transform application inputs from `camelCase` to `snake_case` in
  the repository, before sending to the database

- **SHOULD** implement generic transformation utilities:

  ```ts
  // src/lib/case-utils.ts

  /**
   * Converts a snake_case string to camelCase.
   * Example: 'created_at' → 'createdAt'
   */
  function snakeToCamel(str: string): string {
    return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
  }

  /**
   * Converts a camelCase string to snake_case.
   * Example: 'createdAt' → 'created_at'
   */
  function camelToSnake(str: string): string {
    return str.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`);
  }

  /**
   * Transforms all keys in an object from snake_case to camelCase.
   */
  export function toCamelCase<T>(obj: Record<string, unknown>): T {
    const result: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(obj)) {
      result[snakeToCamel(key)] = value;
    }
    return result as T;
  }

  /**
   * Transforms all keys in an object from camelCase to snake_case.
   */
  export function toSnakeCase(obj: Record<string, unknown>): Record<string, unknown> {
    const result: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(obj)) {
      result[camelToSnake(key)] = value;
    }
    return result;
  }
  ```

> **Note on Prisma v7:** Prisma handles casing automatically — the `schema.prisma`
> file maps `snake_case` database columns to `camelCase` model fields via the
> `@map` attribute. When using Prisma, manual casing transformation is not
> needed. The repository still handles query construction and error mapping.
>
> ```prisma
> // schema.prisma (v7 — no datasource block; that lives in prisma.config.ts)
> generator client {
>   provider = "prisma-client"
>   output   = "./generated/prisma/client"
> }
>
> model Vehicle {
>   id          String   @id @default(uuid())
>   userId      String   @map("user_id")
>   priceCents  Int      @map("price_cents")
>   createdAt   DateTime @map("created_at") @default(now())
>
>   @@map("vehicles")
> }
> ```
>
> ```ts
> // Import from generated path (v7)
> import { PrismaClient } from './generated/prisma/client';
> ```

### 9.3 Query Safety Rules

- **MUST** use parameterized queries — never interpolate user input into SQL.
  The Supabase Client and Prisma are parameterized by default. For raw SQL,
  always use positional parameters
  (→ See [07-security-standards.md, Section 10 — A03: Injection]):

  ```ts
  // Supabase Client — parameterized by default ✅
  const { data } = await supabase
    .from('vehicles')
    .select('*')
    .eq('make', userInput);

  // Prisma — parameterized by default ✅
  const vehicles = await prisma.vehicle.findMany({
    where: { make: userInput },
  });

  // Raw SQL (pg) — use $1, $2, ... parameters ✅
  const result = await pool.query(
    'SELECT * FROM vehicles WHERE make = $1 AND year >= $2',
    [make, minYear]
  );

  // RAW SQL — NEVER do this ❌
  const result = await pool.query(
    `SELECT * FROM vehicles WHERE make = '${make}'`
  );
  ```

- **MUST** select only needed columns — never use `SELECT *` or
  `.select('*')` in production code:

  ```ts
  // BAD — fetches all columns, including potentially large ones
  const { data } = await supabase.from('vehicles').select('*');

  // GOOD — fetches only what the consumer needs
  const { data } = await supabase
    .from('vehicles')
    .select('id, make, model, year, price_cents, is_available');
  ```

  > **Why?** `SELECT *` fetches columns you do not need (e.g., large `TEXT`
  > descriptions, `JSONB` metadata), wastes network bandwidth, prevents
  > index-only scans, and leaks internal fields that should not reach the
  > API response (e.g., `deleted_at`, internal IDs).

- **MUST** add reasonable `LIMIT` to all queries that return collections —
  unbounded result sets can exhaust memory and crash the application
  (→ See [03-api-design.md, Section 7.2 — Pagination Rules])

- **SHOULD** use `.single()` when expecting exactly one result (Supabase)
  or `findUnique` / `findFirst` (Prisma) — this makes the intent explicit
  and returns an error if multiple rows match

### 9.4 The N+1 Query Problem

The N+1 problem occurs when fetching a list of N items, then executing one
additional query per item to fetch related data. This results in N+1 total
queries instead of 1 or 2.

```ts
// ❌ N+1 PROBLEM — 1 query for vehicles + N queries for users
const vehicles = await vehicleRepository.findAll();
for (const vehicle of vehicles) {
  vehicle.user = await userRepository.findById(vehicle.userId);
  // This executes once per vehicle — 100 vehicles = 100 extra queries
}
```

#### Solutions

**Solution 1: Join in a Single Query (Preferred)**

```ts
// ✅ Supabase — fetch related data in one query
const { data } = await supabase
  .from('vehicles')
  .select(`
    id, make, model, price_cents,
    users ( id, name, email )
  `)
  .is('deleted_at', null);

// ✅ Prisma — include related data
const vehicles = await prisma.vehicle.findMany({
  where: { deletedAt: null },
  include: {
    user: { select: { id: true, name: true, email: true } },
  },
});
```

**Solution 2: Batch Fetch with IN Clause**

When a join is not practical (different data sources, complex transformations):

```ts
// ✅ Fetch all vehicles, then batch-fetch users in one query
const vehicles = await vehicleRepository.findAll();

const userIds = [...new Set(vehicles.map((v) => v.userId))];
const users = await userRepository.findByIds(userIds);
const userMap = new Map(users.map((u) => [u.id, u]));

const enriched = vehicles.map((v) => ({
  ...v,
  user: userMap.get(v.userId),
}));
```

```ts
// Repository method for batch fetch
async findByIds(ids: string[]): Promise<User[]> {
  const { data, error } = await supabase
    .from('users')
    .select('id, name, email')
    .in('id', ids);

  if (error) throw error;
  return (data ?? []).map(toCamelCase);
}
```

- **MUST** never fetch related data inside a loop — this is always an N+1
  problem, regardless of the database client
- **SHOULD** prefer joins (Solution 1) when the related data is in the same
  database — it is simpler and more efficient
- **SHOULD** use batch fetch (Solution 2) when joins are not possible or
  when data comes from different sources

### 9.5 Pagination at the Database Level

The API pagination patterns from → See [03-api-design.md, Section 7] must be
supported by efficient database queries.

#### Offset-Based Pagination

```ts
// Repository: offset-based pagination
async findPaginated(options: {
  page: number;
  pageSize: number;
  filters?: VehicleFilters;
}): Promise<{ items: Vehicle[]; total: number }> {
  const from = (options.page - 1) * options.pageSize;
  const to = from + options.pageSize - 1;

  let query = supabase
    .from('vehicles')
    .select('id, make, model, year, price_cents', { count: 'exact' })
    .is('deleted_at', null)
    .order('created_at', { ascending: false })
    .range(from, to);

  // Apply dynamic filters
  if (options.filters?.make) {
    query = query.eq('make', options.filters.make);
  }
  if (options.filters?.minPrice) {
    query = query.gte('price_cents', options.filters.minPrice);
  }

  const { data, error, count } = await query;
  if (error) throw error;

  return {
    items: (data ?? []).map(toCamelCase),
    total: count ?? 0,
  };
}
```

#### Cursor-Based Pagination

```ts
// Repository: cursor-based pagination
async findAfterCursor(options: {
  cursor?: string; // last item's created_at as ISO string
  pageSize: number;
}): Promise<{ items: Vehicle[]; hasMore: boolean }> {
  let query = supabase
    .from('vehicles')
    .select('id, make, model, year, price_cents, created_at')
    .is('deleted_at', null)
    .order('created_at', { ascending: false })
    .limit(options.pageSize + 1); // fetch one extra to detect "hasMore"

  if (options.cursor) {
    query = query.lt('created_at', options.cursor);
  }

  const { data, error } = await query;
  if (error) throw error;

  const items = (data ?? []).map(toCamelCase);
  const hasMore = items.length > options.pageSize;

  return {
    items: hasMore ? items.slice(0, -1) : items, // remove the extra
    hasMore,
  };
}
```

> **Performance note:** Offset-based pagination degrades on large offsets
> (`OFFSET 100000` still scans and discards 100,000 rows). For large datasets,
> cursor-based pagination provides consistent performance because it uses a
> `WHERE` clause on an indexed column instead of `OFFSET`.

### 9.6 Soft Delete in Queries

Soft-deleted records must be invisible in normal application queries.
This requires discipline — every query must remember to filter by
`deleted_at IS NULL`.

- **MUST** filter `deleted_at IS NULL` in every repository query that
  returns records to the application:

  ```ts
  // Every query includes this filter
  .is('deleted_at', null)
  ```

- **SHOULD** centralize the soft delete filter to avoid forgetting it.
  Options:

  ```ts
  // Option A: Base query builder that always adds the filter
  function baseQuery(table: string) {
    return supabase.from(table).select().is('deleted_at', null);
  }

  // Option B: RLS policy handles it (→ See Section 7.5)
  // If the RLS policy includes `deleted_at IS NULL`, the filter
  // is enforced automatically for all client-side queries.

  // Option C: Prisma middleware
  prisma.$use(async (params, next) => {
    if (params.action === 'findMany' || params.action === 'findFirst') {
      params.args.where = { ...params.args.where, deletedAt: null };
    }
    return next(params);
  });
  ```

- **SHOULD** provide a separate method for queries that need to include
  soft-deleted records (admin, recovery, audit):

  ```ts
  // Normal: only active records
  async findById(id: string): Promise<Vehicle | null> { ... }

  // Admin: includes soft-deleted (uses service_role or bypasses filter)
  async findByIdIncludeDeleted(id: string): Promise<Vehicle | null> { ... }
  ```

### 9.7 Query Anti-Patterns

| Anti-Pattern | Problem | Correct Approach |
|---|---|---|
| **Database queries in services** | Couples business logic to specific DB client; violates layering | Move all queries to repository layer |
| **`SELECT *` in production** | Wastes bandwidth, prevents index-only scans, leaks internal columns | Select only needed columns |
| **N+1 queries** (loop + query) | 100 items = 101 queries; database connection exhaustion | Use joins or batch fetch with `IN` |
| **Unbounded queries** (no LIMIT) | Large result sets exhaust memory; application crashes | Always paginate or add a LIMIT |
| **Forgetting soft delete filter** | Deleted records appear in results | Centralize filter; use RLS or base query builder |
| **Mixed casing in service layer** | `user.created_at` in one place, `user.createdAt` in another | Transform at repository boundary; services use camelCase only |
| **String concatenation in queries** | SQL injection vulnerability | Use parameterized queries exclusively |
| **Ignoring query errors** | Silent failures; stale or missing data returned | Always check and propagate errors |

---

## 10. Connection Management

Every database query requires a connection. Opening a connection is expensive
(TCP handshake, TLS negotiation, authentication), and PostgreSQL has a finite
number of connections it can handle simultaneously. Poor connection management
manifests as intermittent failures, "too many connections" errors, and degraded
performance under load.

Understanding how connections work — and how your deployment model affects them —
is essential for building reliable applications.

### 10.1 How PostgreSQL Connections Work

PostgreSQL uses a **process-per-connection** model: each client connection
spawns a dedicated server process. This is reliable but resource-intensive.

Connection limits depend on the **compute size** (not just the plan). The
default compute on the Free plan is Nano; on paid plans, Micro:

| Compute Size | Max Direct Connections | Supavisor Pool Clients |
|---|---|---|
| Nano (Free default) | 60 | 200 |
| Micro (Pro default) | 60 | 200 |
| Small | 120 | 400 |
| Medium | 120 | 400 |
| Large+ | 160+ | 600+ |

> These limits are shared across **all** clients — the Supabase Client,
> Prisma, direct `psql` sessions, migrations, the Supabase dashboard, and
> any other tool connecting to the database. A single misbehaving client
> that leaks connections can exhaust the limit for everyone.
> The Supavisor pool client limits are hard-coded per compute size and
> cannot be changed without upgrading.

### 10.2 Connection Pooling

A connection pooler sits between the application and PostgreSQL. It maintains
a pool of open connections and reuses them across requests, instead of opening
and closing a connection for each query.

```text
Without pooler:                    With pooler:
Request 1 → Connect → Query → Close    Request 1 ─┐
Request 2 → Connect → Query → Close                ├─ Pooler ── Pool of N connections ── PostgreSQL
Request 3 → Connect → Query → Close    Request 2 ─┤
(3 connections opened and closed)       Request 3 ─┘
                                        (N connections reused)
```

#### Supabase Connection Types

Supabase provides **three** connection strings, each for a different use case.
Find them in the Supabase Dashboard under the **Connect** button:

| Connection Type | Host/Port | IPv4 | Use Case |
|---|---|---|---|
| **Direct** | `db.xxxx.supabase.co:5432` | ❌ IPv6 only (unless IPv4 add-on enabled) | Migrations, admin, long-lived servers |
| **Transaction pooler** | `pooler.supabase.com:6543` | ✅ | **Default for applications** — serverless, ORMs, short-lived queries |
| **Session pooler** | `pooler.supabase.com:5432` | ✅ | Prepared statements, LISTEN/NOTIFY, session-dependent features |

- **MUST** use the **transaction pooler** (port 6543) for application queries —
  it handles the most concurrent clients and is IPv4 compatible:

  ```env
  # Application queries — transaction pooler (port 6543)
  DATABASE_URL="postgresql://postgres.xxxx:password@aws-0-region.pooler.supabase.com:6543/postgres?pgbouncer=true"

  # Migrations — direct connection (port 5432, requires IPv6 or IPv4 add-on)
  DIRECT_URL="postgresql://postgres.xxxx:password@aws-0-region.supabase.com:5432/postgres"

  # Alternative migrations — session pooler (port 5432 on pooler host, IPv4 compatible)
  # Use this if direct connection fails due to IPv6
  DIRECT_URL="postgresql://postgres.xxxx:password@aws-0-region.pooler.supabase.com:5432/postgres"
  ```

- **MUST** understand the pooling modes and their implications:

  | Mode | How It Works | Use Case |
  |---|---|---|
  | **Transaction** (default) | Connection is assigned for the duration of a single transaction, then returned to the pool | Standard application queries — the default and recommended mode |
  | **Session** | Connection is assigned for the entire client session (until disconnect) | Long-lived connections, LISTEN/NOTIFY, prepared statements |

  > **Important:** In **Transaction mode** (the default), features that depend
  > on session state do not work reliably: `SET` commands, prepared statements,
  > `LISTEN/NOTIFY`, and advisory locks. These require **Session mode** or a
  > direct connection.

### 10.3 Serverless and Connection Challenges

Serverless environments (Vercel Serverless Functions, Supabase Edge Functions,
AWS Lambda) create a unique connection challenge: each function invocation may
run in a separate container, and each container may open its own database
connection. Under load, hundreds of concurrent invocations can exhaust the
connection limit.

```text
Traditional server:          Serverless:
┌──────────────┐             ┌─ Lambda 1 ── connection 1 ─┐
│  Node.js     │             ├─ Lambda 2 ── connection 2 ─┤
│  server      ├── pool ──── │...                         ├── PostgreSQL
│  (1 process) │  (10 conn)  ├─ Lambda 49 ── connection 49┤
└──────────────┘             └─ Lambda 50 ── connection 50 ┘
= 10 connections             = 50+ connections (uncontrolled)
```

#### Rules for Serverless Deployments

- **MUST** use the connection pooler for all serverless deployments — never
  connect directly to PostgreSQL from serverless functions

- **SHOULD** prefer the Supabase Client library over direct PostgreSQL
  connections in serverless contexts — the Supabase Client communicates
  via HTTP (PostgREST), not direct TCP connections, which completely avoids
  the connection limit problem:

  ```ts
  // PREFERRED in serverless — HTTP-based, no connection management needed
  import { createClient } from '@supabase/supabase-js';
  const supabase = createClient(url, anonKey);

  const { data } = await supabase.from('vehicles').select('*');

  // REQUIRES CARE in serverless — TCP connection via driver adapter, needs pooler
  import { PrismaClient } from './generated/prisma/client';
  import { PrismaPg } from '@prisma/adapter-pg';
  import { Pool } from 'pg';
  const pool = new Pool({ connectionString: process.env.DATABASE_URL, max: 1 });
  const prisma = new PrismaClient({ adapter: new PrismaPg(pool) });
  ```

- **MUST** configure Prisma v7 to use the connection pooler in serverless:

  ```ts
  // prisma.config.ts — datasource for CLI (migrations use direct connection)
  import 'dotenv/config';
  import { defineConfig, env } from 'prisma/config';

  export default defineConfig({
    schema: 'prisma/schema.prisma',
    migrations: { path: 'prisma/migrations' },
    datasource: {
      url: env('DIRECT_URL'),  // direct connection for migrations only
    },
  });
  ```

  ```env
  # .env
  # Pooled connection — used by PrismaClient at runtime (IPv4 compatible)
  DATABASE_URL="postgresql://postgres.xxxx:password@aws-0-region.pooler.supabase.com:6543/postgres?pgbouncer=true"

  # Direct connection — used by Prisma CLI for migrations only (may require IPv6)
  DIRECT_URL="postgresql://postgres.xxxx:password@aws-0-region.supabase.com:5432/postgres"
  ```

  > **Note (Prisma v7):** The `datasource` block was removed from `schema.prisma`.
  > The `directUrl` property was also removed. All datasource configuration now
  > lives in `prisma.config.ts`. The runtime connection is configured via the
  > driver adapter when instantiating `PrismaClient`.

#### The Hot Reload Connection Leak (Next.js + Prisma)

In Next.js development, every file save triggers a hot reload that re-executes
module-level code. If the `PrismaClient` is instantiated at module scope
without protection, each reload creates a new client with its own connection
pool — rapidly exhausting the database connection limit.

Symptoms:
- Application works for a few minutes, then fails with connection errors
- Switching between pages or saving files triggers the failure
- Restarting the dev server temporarily fixes it (until connections accumulate again)

- **MUST** use the singleton pattern to prevent connection leaks during
  hot reload:

  ```ts
  // src/lib/prisma.ts — MANDATORY for Next.js + Prisma v7
  import { PrismaClient } from './generated/prisma/client';
  import { PrismaPg } from '@prisma/adapter-pg';
  import { Pool } from 'pg';

  const globalForPrisma = globalThis as unknown as {
    prisma: PrismaClient | undefined;
    pool: Pool | undefined;
  };

  // Reuse the pg Pool across hot reloads (prevents connection leaks)
  const pool =
    globalForPrisma.pool ??
    new Pool({
      connectionString: process.env.DATABASE_URL,
      max: 5,  // limit connections — critical for Supabase Free (60 total)
    });

  const adapter = new PrismaPg(pool);

  export const prisma =
    globalForPrisma.prisma ??
    new PrismaClient({ adapter });

  if (process.env.NODE_ENV !== 'production') {
    globalForPrisma.prisma = prisma;
    globalForPrisma.pool = pool;
  }
  ```

  > **Prisma v7 change:** `PrismaClient` no longer manages its own connection
  > pool. You supply a `pg.Pool` via the `@prisma/adapter-pg` driver adapter,
  > giving you direct control over pool size via `max`. The singleton must
  > preserve both the `Pool` and the `PrismaClient` in `globalThis`.

- **MUST** limit the `pg.Pool` size explicitly via the `max` option — the
  default `max` for the `pg` library is **10**, which on Supabase Free
  (60 connections shared across all clients) can be too aggressive.
  Start with `max: 5` for serverless or constrained environments:

  ```ts
  // Pool size control (Prisma v7 — via pg.Pool, NOT via URL params)
  const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    max: 5,                       // max connections in the pool
    idleTimeoutMillis: 30000,     // close idle connections after 30s
    connectionTimeoutMillis: 5000, // fail if connection takes > 5s
  });
  ```

  > **Migration from Prisma v6:** The `connection_limit` URL parameter no
  > longer applies. Pool configuration is now done via the `pg.Pool` constructor
  > options. The `pgbouncer=true` URL parameter is still required when connecting
  > through Supavisor in transaction mode.

> **This combination — singleton (Pool + PrismaClient) + pooled URL (port 6543) +
> `pgbouncer=true` + `pg.Pool({ max })` — is required for reliable Prisma v7 +
> Supabase operation.** Missing any one of these causes intermittent connection
> failures.

#### IPv6 and Direct Connection Limitations

Supabase direct connections (port 5432) require IPv6 by default. If the
development environment or hosting provider does not support IPv6, direct
connections will fail with `Network is unreachable` or similar errors.

- **MUST** use the pooled connection string (port 6543) when direct connections
  fail due to IPv6 limitations — the pooler is accessible via IPv4

- **MAY** enable the IPv4 add-on ($4/month per database) on paid Supabase plans
  for direct connection access via IPv4. The IPv4 add-on is **not available**
  on the Free plan

- **SHOULD** add `?pgbouncer=true` to the pooled URL when using Prisma —
  this tells Prisma to disable features incompatible with connection pooling
  (prepared statements in transaction mode)

- If migrations fail with the direct URL due to IPv6, **MAY** use one of
  these alternatives:
  - Use the **session pooler** (`pooler.supabase.com:5432`) which is IPv4
    compatible and supports the prepared statements Prisma CLI needs
  - Run migrations from an environment that supports IPv6
  - Use the Supabase CLI (`supabase db push`) which connects through
    Supabase's own infrastructure

### 10.4 Decision Guide: Supabase Client vs Prisma

| Aspect | Supabase Client | Prisma |
|---|---|---|
| **Protocol** | HTTP (PostgREST) | TCP (direct PostgreSQL connection) |
| **Connections** | Zero concern — PostgREST manages its own pool | Requires configuration (pool size, pooler, singleton) |
| **Type safety** | Types via `supabase gen types` — good but less deep | Types from schema — excellent, with relations and autocomplete |
| **Relations** | Embed syntax `.select('*, users(*)')` — functional but limited | `include` / `select` — intuitive for complex graphs |
| **Complex queries** | Limited to PostgREST capabilities | Supports aggregations, group by, raw SQL fallback |
| **Migrations** | SQL manual (Supabase CLI) — full control | Generated from `schema.prisma` — convenient, review the SQL |
| **RLS** | Works natively — RLS applied to every query | Works, but needs careful `service_role` configuration |
| **Serverless** | Ideal — HTTP is stateless, no pooling issues | Requires pooler + singleton + `pg.Pool({ max })` |
| **Real-time** | Native integration (subscriptions, presence) | No real-time support |
| **Learning curve** | Low — if you know the Supabase API | Medium — schema language, migrations, connection management |

**When to use Supabase Client (default):**
- Next.js full-stack projects with Supabase backend
- CRUD-dominant applications with simple to moderate queries
- Projects that need real-time features
- Serverless deployments where connection management is a concern
- Freelance/MVP projects where speed of development matters

**When to use Prisma:**
- Standalone APIs (Express, NestJS) that do not use Supabase Client
- Projects with complex relational queries (deep includes, aggregations)
- Projects that benefit from declarative migration workflow
- Teams that value Prisma's developer experience (autocomplete, type safety)

**When NOT to use Prisma with Supabase:**
- If the project's queries are simple CRUD — Prisma adds connection management
  complexity without proportional benefit
- In serverless environments without proper configuration (singleton + pooler +
  connection limit) — connection exhaustion is likely

> **Rule of thumb:** Start with Supabase Client. Add Prisma only when the
> query complexity justifies the operational overhead. Both are ✅ Adopt in
> → See [02-technology-radar.md] — the question is which fits the project's
> complexity, not which is "better."

### 10.5 Connection Configuration by Stack

| Stack | Query Connection | Migration Connection | Notes |
|---|---|---|---|
| **Supabase Client** (default) | HTTP via PostgREST (no TCP pool needed) | Supabase CLI (direct) | Simplest — no connection management |
| **Prisma v7 + Supabase** | Pooled URL (port 6543) via `pg.Pool` adapter | Direct URL in `prisma.config.ts` | Pool + adapter + singleton |
| **Raw pg + Supabase** | Pooled URL | Direct URL | Use `pg.Pool` with `max` limit |
| **Self-hosted PostgreSQL** | Application pool (`pg.Pool`) | Direct connection | Configure pool size based on instance |

#### Raw `pg` Pool Configuration

For applications using the `pg` library directly (Express.js standalone APIs):

```ts
// src/lib/db.ts
import { Pool } from 'pg';

export const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 10,                    // Maximum connections in the pool
  idleTimeoutMillis: 30000,   // Close idle connections after 30s
  connectionTimeoutMillis: 5000, // Fail if connection takes > 5s
  allowExitOnIdle: true,      // Allow process to exit when pool is idle
});

// Graceful shutdown
process.on('SIGTERM', async () => {
  await pool.end();
  process.exit(0);
});
```

- **MUST** set a reasonable `max` pool size — a good starting point is
  `max = (PostgreSQL max_connections) / (number of application instances)`.
  For Supabase Free (60 connections) with 2 instances: `max = 20` leaves
  headroom for migrations and admin

- **MUST** implement graceful shutdown — close the pool when the process
  exits to prevent connection leaks

- **MUST** set `connectionTimeoutMillis` — without it, a connection request
  waits indefinitely if the pool is exhausted, causing the request to hang

### 10.6 Connection Troubleshooting

| Symptom | Likely Cause | Solution |
|---|---|---|
| `too many connections for role` | Connection limit exhausted | Use pooler; reduce pool `max`; check for leaks |
| Intermittent `connection refused` | Serverless opening too many direct connections | Switch to pooled connection string |
| Queries hang indefinitely | Pool exhausted, no timeout configured | Set `connectionTimeoutMillis`; increase pool or reduce query time |
| `prepared statement already exists` | Transaction-mode pooler + prepared statements | Use `?pgbouncer=true` in URL; or use session mode |
| Slow first query after idle | Connection was closed; new TCP + TLS handshake | Accept (normal) or use keep-alive settings |
| Memory spikes on database server | Too many connections (each consumes ~10 MB) | Reduce pool `max`; use pooler |
| `Network is unreachable` (direct connection) | IPv6 required but not supported by environment | Use pooled connection (port 6543); or enable IPv4 add-on on paid plans |
| Connections exhaust in Next.js development | PrismaClient hot reload leak | Use the `globalThis` singleton pattern (→ See Section 10.3) |
| Connections exhaust despite singleton | Prisma v7 `pg.Pool` `max` too large for Supabase limits | Set `max: 5` (or lower) in `new Pool()` constructor |

### 10.7 Connection Security

- **MUST** use TLS/SSL for all database connections — never connect over
  unencrypted channels
  (→ See [07-security-standards.md, Section 8 — Encryption in Transit]):

  ```ts
  // pg library — enforce SSL
  const pool = new Pool({
    connectionString: process.env.DATABASE_URL,
    ssl: { rejectUnauthorized: true },  // verify server certificate
  });
  ```

  > **Note:** Supabase connections use SSL by default. The connection
  > string includes `sslmode=require`. Verify this is present.

- **MUST** store database connection strings in environment variables —
  never in code or config files committed to version control
  (→ See [07-security-standards.md, Section 7 — Secrets Management])

- **SHOULD** use different database roles for different access patterns
  (principle of least privilege):

  | Role | Access | Use Case |
  |---|---|---|
  | `anon` | RLS-restricted read/write | Supabase Client (public-facing) |
  | `authenticated` | RLS-restricted, user-scoped | Supabase Client (logged-in users) |
  | `service_role` | Bypasses RLS | Server-side admin operations |
  | Application role | Schema-specific grants | Direct `pg` connections with limited permissions |

---

## 11. Performance & Optimization

Database performance is not about premature optimization — it is about
knowing how to diagnose problems when they appear and having the tools
to fix them. Most database performance issues stem from a small set of
common causes: missing indexes, inefficient queries, and unbounded result
sets.

The principle remains: **measure first, optimize second.**
(→ See [01-core-principles.md, Section 2 — Measure Before Optimizing])

### 11.1 EXPLAIN ANALYZE — The Primary Diagnostic Tool

`EXPLAIN ANALYZE` is the most important performance tool in PostgreSQL. It
shows exactly how the query planner executes a query — which indexes it uses,
how many rows it scans, and where time is spent.

- **MUST** use `EXPLAIN ANALYZE` before adding or modifying indexes — never
  guess what the query planner is doing:

  ```sql
  EXPLAIN ANALYZE
  SELECT id, make, model, price_cents
  FROM vehicles
  WHERE user_id = 'a1b2c3d4-...'
    AND deleted_at IS NULL
  ORDER BY created_at DESC
  LIMIT 20;
  ```

  Example output:

  ```
  Limit  (cost=0.42..15.30 rows=20 width=72) (actual time=0.045..0.098 rows=20 loops=1)
    -> Index Scan Backward using idx_vehicles_user_active_recent on vehicles
         (cost=0.42..148.30 rows=200 width=72) (actual time=0.043..0.092 rows=20 loops=1)
         Index Cond: (user_id = 'a1b2c3d4-...'::uuid)
         Filter: (deleted_at IS NULL)
  Planning Time: 0.120 ms
  Execution Time: 0.125 ms
  ```

#### How to Read EXPLAIN ANALYZE Output

| Key Indicator | What It Means | Concern Level |
|---|---|---|
| `Seq Scan` | Sequential scan — reads every row in the table | ⚠️ On large tables (> 10K rows) |
| `Index Scan` | Uses an index to find rows | ✅ Efficient |
| `Index Only Scan` | Satisfies query entirely from the index | ✅ Most efficient |
| `Bitmap Heap Scan` | Combines index with table access | ✅ Normal for multi-condition queries |
| `Sort` (without index) | In-memory or disk sort | ⚠️ Check if an index could eliminate it |
| `actual time` | Real execution time in milliseconds | Compare with `cost` estimates |
| `rows` (estimated vs actual) | Planner's estimate vs reality | Large discrepancy → stale statistics |
| `loops` | How many times the node was executed | High loops in nested loops → possible N+1 |

- **MUST** look for `Seq Scan` on large tables — this usually means a
  missing index. A Seq Scan on a table with 100K rows reads all 100K rows
  even if only 10 match the filter

- **SHOULD** investigate when estimated rows differ significantly from
  actual rows — this means the planner's statistics are stale. Fix with:

  ```sql
  ANALYZE vehicles;  -- updates statistics for the vehicles table
  ```

### 11.2 Common Performance Problems

#### Problem 1: Missing Index

**Symptom:** Query is slow. `EXPLAIN ANALYZE` shows `Seq Scan`.

```sql
-- Slow: sequential scan on 500K rows
EXPLAIN ANALYZE
SELECT * FROM vehicles WHERE make = 'Toyota';
-- → Seq Scan on vehicles  (actual time=0.012..45.678 rows=150 ...)

-- Fix: add an index
CREATE INDEX idx_vehicles_make ON vehicles (make);

-- Fast: index scan
-- → Index Scan using idx_vehicles_make  (actual time=0.025..0.234 rows=150 ...)
```

#### Problem 2: N+1 Queries

**Symptom:** Page loads slowly. Database logs show dozens of similar queries
in sequence.

**Solution:** → See [Section 9.4 — The N+1 Query Problem]

#### Problem 3: Unbounded Queries

**Symptom:** Memory spikes, timeouts, or crashes when tables grow.

```ts
// ❌ Fetches entire table into memory
const { data } = await supabase.from('vehicles').select('*');

// ✅ Paginated, limited, with selected columns
const { data } = await supabase
  .from('vehicles')
  .select('id, make, model, price_cents')
  .is('deleted_at', null)
  .order('created_at', { ascending: false })
  .range(0, 19);
```

#### Problem 4: Expensive COUNT on Large Tables

**Symptom:** List endpoints are slow, especially with filters. The query
itself is fast, but `{ count: 'exact' }` adds significant time.

```sql
-- COUNT(*) must scan all matching rows (even with index)
SELECT COUNT(*) FROM vehicles WHERE is_available = true;
-- On 1M rows, this may take hundreds of milliseconds
```

**Solutions (in order of preference):**

1. **Use cursor-based pagination** — avoids COUNT entirely by using
   `hasMore` instead of `totalItems`
   (→ See [03-api-design.md, Section 7.1])

2. **Use estimated counts for large datasets** — PostgreSQL tracks
   approximate row counts in system statistics:

   ```sql
   -- Fast approximate count (from last ANALYZE)
   SELECT reltuples::bigint AS estimate
   FROM pg_class
   WHERE relname = 'vehicles';
   ```

3. **Cache the count** — if the exact count is needed, compute it
   periodically (background job) rather than on every request

#### Problem 5: Large Offset Pagination

**Symptom:** Pages 1–10 are fast, pages 100+ are increasingly slow.

```sql
-- Slow: OFFSET 100000 must scan and discard 100,000 rows
SELECT * FROM vehicles ORDER BY created_at DESC LIMIT 20 OFFSET 100000;
```

**Solution:** Switch to cursor-based pagination for large datasets
(→ See [Section 9.5]):

```sql
-- Fast: cursor-based (uses an indexed WHERE, no scanning)
SELECT * FROM vehicles
WHERE created_at < '2026-01-15T10:30:00Z'
ORDER BY created_at DESC
LIMIT 20;
```

#### Problem 6: Bloated Tables and Indexes

**Symptom:** Queries gradually slow down over time, even with proper
indexes. Table and index sizes grow disproportionately to row count.

**Cause:** Dead tuples from frequent UPDATEs and DELETEs accumulate.
PostgreSQL's MVCC model keeps old row versions until autovacuum cleans
them up.

**Solutions:**

```sql
-- Check dead tuple count
SELECT
  relname AS table_name,
  n_dead_tup,
  n_live_tup,
  round(n_dead_tup::numeric / greatest(n_live_tup, 1) * 100, 2) AS dead_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;

-- Manual vacuum (if autovacuum is lagging)
VACUUM ANALYZE vehicles;

-- Reclaim space aggressively (locks table briefly)
VACUUM FULL vehicles;  -- use with caution in production

-- Rebuild bloated indexes
REINDEX INDEX CONCURRENTLY idx_vehicles_make_model;
```

- **SHOULD** monitor autovacuum activity — if dead tuples accumulate
  faster than autovacuum cleans them, tune the autovacuum settings
  (→ See [08-observability.md] when available)

### 11.3 Query Optimization Checklist

When a query is slow, work through this checklist in order:

1. **Run `EXPLAIN ANALYZE`** — identify the bottleneck (Seq Scan? Sort?
   Nested Loop with high loops?)
2. **Check for missing indexes** — does the WHERE clause filter on an
   unindexed column?
3. **Check for `SELECT *`** — are you fetching columns you do not need?
4. **Check for missing LIMIT** — is the query returning more rows than
   necessary?
5. **Check for N+1** — is the slow "query" actually dozens of queries
   in a loop?
6. **Check statistics** — run `ANALYZE tablename` if estimated vs actual
   rows diverge significantly
7. **Check for bloat** — has the table accumulated dead tuples?
8. **Check for lock contention** — are concurrent queries blocking each
   other? (→ See [Section 6.6 — Large Table Migrations])
9. **Consider query restructuring** — can the query be rewritten to use
   existing indexes more effectively?
10. **Consider denormalization** — only as a last resort, after all other
    options are exhausted, with an ADR documenting the decision
    (→ See [Section 1.3 — Pragmatic Normalization])

### 11.4 Performance Anti-Patterns

| Anti-Pattern | Problem | Correct Approach |
|---|---|---|
| **Optimizing without measuring** | Adds complexity for no proven benefit | `EXPLAIN ANALYZE` first; optimize only what is measured as slow |
| **`SELECT *` everywhere** | Wastes bandwidth, prevents index-only scans, leaks internal fields | Select only needed columns |
| **No LIMIT on collection queries** | Memory exhaustion on large tables | Always paginate or add explicit LIMIT |
| **COUNT(*) on every list request** | Expensive on large tables; often unnecessary | Use cursor pagination with `hasMore`; or estimated counts |
| **OFFSET for deep pagination** | `OFFSET 100000` scans 100K rows | Cursor-based pagination for large datasets |
| **Premature denormalization** | Increases complexity and data inconsistency risk | Normalize first; denormalize only when measured need exists |
| **Caching before optimizing queries** | Hides the real problem; adds cache invalidation complexity | Fix the query first; cache only when the optimized query is still too slow |
| **Adding indexes for every column** | Slows writes, wastes storage, most are never used | Index based on actual query patterns; monitor usage |
| **Ignoring autovacuum** | Dead tuples accumulate, table bloat, degrading performance | Monitor dead tuple counts; tune autovacuum if needed |

---

## 12. Backup & Recovery

Backups are the last line of defense when everything else fails — accidental
deletions, corrupted migrations, application bugs that overwrite data, or
security incidents that compromise the database. A backup strategy is not
complete until it has been tested: **a backup that has never been restored
is not a backup — it is a hope.**

This section defines what to back up, how often, and — critically — how to
recover when something goes wrong.

### 12.1 Backup Strategy

#### Supabase (Managed)

Supabase provides automatic backups with different capabilities per plan:

| Plan | Price | Automatic Backups | PITR | Retention |
|---|---|---|---|---|
| **Free** | $0/month | ❌ None | ❌ Not available | — |
| **Pro** | $25/month | ✅ Daily | Add-on ($100/month) | 7 days |
| **Team** | $599/month | ✅ Daily | Add-on ($100/month) | 14 days |
| **Enterprise** | Custom | ✅ Daily | Add-on ($100/month, >28 days available) | Custom |

> **⚠️ Critical: The Free plan has NO automatic backups.** If you are running
> any production workload on the Free plan, an accidental deletion, a bad
> migration, or a corrupted query means **permanent data loss** with no
> recovery path. This is an existential risk for any real project.
>
> **Recommendation:** For any project with real users or real data, upgrade
> to the Pro plan ($25/month) at minimum. The cost of a single data loss
> incident far exceeds the subscription cost.

- **MUST** know which backup tier the project is on — the difference
  between no backups and daily backups, and between daily backups and PITR,
  determines how much data you can lose in a disaster

- **SHOULD** enable PITR (add-on on Pro plan or above) for any project with
  production data that matters — daily backups mean that a mistake at
  23:59 loses an entire day of data. PITR requires at least the Small
  compute add-on to function properly

- **MUST** understand the backup scope — Supabase backups include the
  full PostgreSQL database (all schemas, tables, RLS policies, functions,
  triggers). They do **not** include Supabase Storage files (those have
  separate backup considerations)

- **SHOULD** implement manual backup procedures for Free plan projects
  using `pg_dump` via the Supabase CLI or direct connection:

  ```bash
  # Manual backup for Free plan projects
  pg_dump --format=custom --compress=9 \
    --file="backup_$(date +%Y%m%d_%H%M%S).dump" \
    "$DATABASE_URL"
  ```

#### Self-Hosted PostgreSQL

For self-hosted or non-Supabase PostgreSQL:

- **MUST** configure automated backups using `pg_dump` (logical) or
  `pg_basebackup` (physical):

  ```bash
  # Logical backup (portable, smaller, slower to restore)
  pg_dump --format=custom --compress=9 \
    --file="/backups/mydb_$(date +%Y%m%d_%H%M%S).dump" \
    "$DATABASE_URL"

  # Restore from logical backup
  pg_restore --clean --if-exists --dbname="$DATABASE_URL" \
    "/backups/mydb_20260315_143200.dump"
  ```

- **MUST** configure WAL archiving for PITR capability on self-hosted
  instances — without WAL archiving, recovery is limited to the last
  full backup

- **MUST** encrypt all backups at rest
  (→ See [07-security-standards.md, Section 8 — Encryption at Rest])

- **MUST** store backups in a different location than the database —
  a backup on the same disk as the database is lost if the disk fails

### 12.2 Point-in-Time Recovery (PITR)

PITR allows restoring the database to any specific moment in time — not
just to the last backup snapshot. This is the most powerful recovery
tool available.

**How it works:** PostgreSQL continuously writes every change to the
Write-Ahead Log (WAL). PITR replays these WAL entries up to a specific
timestamp, effectively "rewinding" the database to that exact moment.

#### When PITR Saves You

| Scenario | Without PITR (Daily Backup) | With PITR |
|---|---|---|
| Accidental `DELETE FROM vehicles` at 14:30 | Restore daily backup from last night → lose today's data | Restore to 14:29 → lose only the seconds before the mistake |
| Bad migration drops a column at 10:00 | Restore daily backup → lose everything since last night | Restore to 09:59 → lose only the minute before the migration |
| Application bug corrupts data over 2 hours | Restore daily backup → lose everything since last night | Restore to before the bug started |

#### How to Use PITR in Supabase

```text
1. Go to Supabase Dashboard → Database → Backups → Point in Time
2. Select the target timestamp (just BEFORE the incident)
3. Supabase restores the database to the selected point in time
4. The project is inaccessible during restoration (plan for downtime)
5. Downtime depends on database size — the larger, the longer
6. Verify the restored data is correct after completion
```

- **MUST** note the exact timestamp of the incident as soon as it is
  detected — PITR precision depends on knowing when the problem occurred.
  Check application logs, audit trail, and `updated_at` timestamps to
  determine the exact moment

- **SHOULD** practice PITR recovery at least once in a non-production
  environment — knowing how to use it under pressure is different from
  reading about it

### 12.3 Recovery Procedures

When something goes wrong, having a documented procedure prevents panic
and reduces recovery time.

#### Procedure 1: Accidental Data Deletion

**Scenario:** Someone accidentally deleted records they should not have.

```text
Severity assessment:
├── Was it a soft delete? (deleted_at was set)
│    └── YES → Simple recovery: UPDATE ... SET deleted_at = NULL
│              Time to recover: minutes
├── Was it a hard delete on a few records?
│    └── Check audit trail (→ 07-security-standards.md, Section 15)
│        for the deleted data → manual re-insert or PITR
│        Time to recover: minutes to hours
└── Was it a bulk hard delete or TRUNCATE?
     └── PITR to just before the deletion (if available)
         OR restore from daily backup (if no PITR)
         Time to recover: 30 minutes to hours (depends on DB size)
```

Steps:
1. **Stop the bleeding** — identify and stop whatever is causing the deletion
   (disable the endpoint, revert the deploy, revoke access)
2. **Assess scope** — how many records? which tables? when did it start?
3. **Choose recovery method** — soft delete undo, PITR, or backup restore
4. **Verify** — confirm the recovered data is correct and complete
5. **Post-mortem** — document what happened and how to prevent recurrence
   (→ See [07-security-standards.md, Section 16 — Incident Response])

#### Procedure 2: Bad Migration

**Scenario:** A migration was applied that corrupted or lost data.

```text
Was the migration destructive (DROP TABLE, DROP COLUMN)?
├── YES → Was there a backup before the migration?
│    ├── YES → Restore backup or PITR to pre-migration
│    └── NO  → Data may be permanently lost → post-mortem required
└── NO (additive migration — ADD COLUMN, CREATE INDEX)
     └── Create a new migration to revert the change
         (→ See Section 6.5 — Reversible Migrations)
```

Steps:
1. **Do not apply more migrations** — stop the pipeline
2. **Assess** — is the migration reversible? Is data lost or just altered?
3. **Revert if possible** — create a down migration and apply it
4. **PITR if destructive** — restore to pre-migration timestamp
5. **Re-apply correctly** — fix the migration and re-run through the
   normal pipeline (code review → CI → deploy)

#### Procedure 3: Application Bug Corrupting Data

**Scenario:** A bug in the application wrote incorrect data over a period.

```text
1. Identify the time range of corruption
   (audit trail, logs, updated_at timestamps)
2. Identify affected tables and columns
3. Options:
   a. If audit trail has before/after values → restore from audit records
   b. If corruption is limited → PITR to before corruption, extract
      correct data, merge into current database
   c. If corruption is extensive → PITR full restore, re-apply
      legitimate changes since the corruption started
```

- **MUST** prioritize identifying the exact start time of the corruption —
  the accuracy of recovery depends on this

### 12.4 Backup Testing

- **MUST** test backup restoration at least once before the first
  production launch — a backup process that has never been tested may
  fail when it matters most
  (→ See [07-security-standards.md, Section 17 — Pre-Deployment Checklist])

- **SHOULD** test backup restoration periodically (quarterly) for
  production applications — backup formats can change, tools can break,
  and the process can drift

- **SHOULD** document the restoration procedure as a runbook — step-by-step
  instructions that any team member can follow under pressure:

  ```markdown
  ## Database Restoration Runbook

  ### Prerequisites
  - Access to Supabase dashboard (or database server)
  - Knowledge of the incident timestamp
  - Notification to the team that restoration is in progress

  ### For Supabase (PITR)
  1. Open Dashboard → Database → Backups → Point in Time
  2. Select timestamp: [BEFORE the incident]
  3. Click "Start restoration"
  4. Wait for completion (monitor progress in dashboard)
     ⚠️ Project is inaccessible during restoration
  5. Verify data integrity: run key queries to confirm critical data
  6. Notify team that service is restored

  ### For Supabase (Daily Backup)
  1. Open Dashboard → Database → Backups
  2. Select the most recent backup BEFORE the incident
  3. Download or restore directly
  4. Verify data integrity
  5. Notify team

  ### For Free Plan (Manual Backup)
  1. Locate the most recent pg_dump file
  2. Create a new Supabase project (or use local)
  3. pg_restore into the new project
  4. Verify data integrity
  5. Migrate application to the restored database

  ### Post-Recovery
  - [ ] Data integrity verified (spot-check critical tables)
  - [ ] Application tested against restored database
  - [ ] Team notified of recovery completion
  - [ ] Post-mortem scheduled
  - [ ] Incident documented
  ```

### 12.5 Defense Layers Against Data Loss

The backup strategy is part of a broader defense-in-depth approach to
protecting data. Each layer catches what the previous layer missed:

```text
Layer 1: Prevention
  ├── Soft deletes (→ Section 3.4) — "deleted" data is still in the DB
  ├── ON DELETE RESTRICT (→ Section 4.2) — blocks accidental cascade
  ├── Destructive migration safeguards (→ Section 6.5) — multi-step approach
  └── RLS policies (→ Section 7) — unauthorized access blocked at DB level

Layer 2: Detection
  ├── Audit trail (→ 07-security, Section 15) — who changed what, when
  ├── Application monitoring (→ 08-observability) — alerts on anomalies
  └── Constraint violations logged (→ Section 5.6) — catch unexpected writes

Layer 3: Recovery
  ├── Soft delete undo — UPDATE deleted_at = NULL (seconds)
  ├── PITR — restore to exact moment (minutes to hours)
  ├── Daily backup restore — last known good state (hours)
  └── Audit trail reconstruction — manual data re-entry (hours to days)
```

- **MUST** have at least Layers 1 and 3 operational for any production
  application — prevention and recovery are mandatory
- **SHOULD** have all three layers for applications with business-critical
  data

### 12.6 Backup Anti-Patterns

| Anti-Pattern | Problem | Correct Approach |
|---|---|---|
| **"We have backups" (never tested)** | Backup may be corrupted, incomplete, or unrestorable | Test restoration at least once before launch |
| **Backups on the same disk** | Disk failure destroys both database and backups | Store backups in a different location/region |
| **Production on Free plan (no backups)** | Accidental deletion = permanent, unrecoverable data loss | Upgrade to Pro ($25/month) or implement manual pg_dump |
| **No PITR for production** | Daily backup = up to 24 hours of data loss | Enable PITR add-on for production data |
| **No documented recovery procedure** | Team panics under pressure, makes mistakes | Write a runbook; practice restoration |
| **Relying only on soft delete** | TRUNCATE, DROP TABLE, and schema corruption bypass soft delete | Soft delete is Layer 1; backups (Layer 3) are still required |
| **Unencrypted backups** | Backup is a full copy of the database — a breach if exposed | Encrypt all backups at rest |
| **No backup retention policy** | Old backups accumulate, costing storage; or expire too soon | Define retention aligned with business/legal needs |

---

## 13. Database Testing Patterns

Database tests verify that the data layer works correctly — schemas enforce
their constraints, RLS policies block unauthorized access, migrations apply
cleanly, and repository queries return the expected results.

This section covers testing patterns specific to the database. For the
complete testing strategy (test pyramid, coverage targets, CI integration):
→ See [06-testing-strategy.md].
For API-level integration testing patterns:
→ See [03-api-design.md, Section 13].

### 13.1 What to Test at the Database Layer

| Category | What to Test | Why |
|---|---|---|
| **RLS policies** | Users can only access their own data; admins can access all | RLS is the security boundary — a misconfigured policy is a data breach |
| **Constraints** | NOT NULL, UNIQUE, CHECK, FK constraints reject invalid data | Constraints are the last safety net — verify they actually fire |
| **Migrations** | Each migration applies cleanly on an empty and populated database | A migration that works on empty tables but fails on real data breaks production |
| **Repository queries** | Queries return correct data with correct casing transformation | The repository is the bridge between DB and app — bugs here propagate everywhere |
| **Soft delete filtering** | Soft-deleted records are invisible in normal queries | Forgetting the filter leaks "deleted" data to the application |
| **Seed data** | Seeds are idempotent and produce a usable development state | Broken seeds block every developer on the team |

### 13.2 Test Database Setup

- **MUST** use a dedicated test database — never run tests against
  development, staging, or production databases:

  ```env
  # .env.test
  DATABASE_URL="postgresql://postgres:postgres@localhost:54322/postgres"
  # Uses Supabase local (supabase start) or a dedicated test instance
  ```

- **SHOULD** use Supabase local development (`supabase start`) for
  database testing — it provides a full local PostgreSQL instance with
  RLS, Auth, and all Supabase features:

  ```bash
  # Start local Supabase (includes PostgreSQL, Auth, Storage, etc.)
  supabase start

  # Reset database to clean state (re-runs all migrations + seed)
  supabase db reset

  # Local connection details (output by supabase start):
  # DB URL:    postgresql://postgres:postgres@localhost:54322/postgres
  # Studio:    http://localhost:54323
  # API URL:   http://localhost:54321
  ```

- **SHOULD** reset the database before each test suite (not each test)
  for performance, and use transaction rollback for per-test isolation:

  ```ts
  // tests/setup.ts
  import { createClient } from '@supabase/supabase-js';

  const supabase = createClient(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!  // service_role to bypass RLS in setup
  );

  // Clean specific tables before test suite
  export async function resetTestData() {
    // Delete in reverse dependency order to respect FK constraints
    await supabase.from('vehicle_features').delete().neq('vehicle_id', '');
    await supabase.from('vehicles').delete().neq('id', '');
    // Seed required reference data
    await seedTestData();
  }
  ```

### 13.3 Test Data Factories

- **MUST** use factory functions to generate test data — never hardcode
  IDs or values that depend on a specific database state
  (→ See [03-api-design.md, Section 13.6]):

  ```ts
  // tests/factories/vehicle-factory.ts
  import { faker } from '@faker-js/faker';

  export function buildVehicle(overrides: Partial<CreateVehicleInput> = {}) {
    return {
      make: faker.vehicle.manufacturer(),
      model: faker.vehicle.model(),
      year: faker.number.int({ min: 2015, max: 2026 }),
      vin: faker.vehicle.vin(),
      priceCents: faker.number.int({ min: 500000, max: 10000000 }),
      mileageKm: faker.number.int({ min: 0, max: 200000 }),
      fuelType: faker.helpers.arrayElement([
        'gasoline', 'diesel', 'electric', 'hybrid',
      ]),
      isAvailable: true,
      ...overrides,
    };
  }

  // Usage
  const vehicle = buildVehicle({ make: 'Toyota', priceCents: 2500000 });
  ```

- **SHOULD** create a helper to insert test data directly into the
  database (bypassing the application layer) for test setup:

  ```ts
  // tests/helpers/db-helpers.ts
  export async function insertTestUser(overrides = {}) {
    const userData = {
      id: faker.string.uuid(),
      email: faker.internet.email(),
      name: faker.person.fullName(),
      ...overrides,
    };

    const { data, error } = await supabaseAdmin
      .from('users')
      .insert(userData)
      .select()
      .single();

    if (error) throw error;
    return data;
  }

  export async function insertTestVehicle(userId: string, overrides = {}) {
    const vehicleData = {
      ...buildVehicle(),
      user_id: userId,  // snake_case: direct DB insert
      ...overrides,
    };

    const { data, error } = await supabaseAdmin
      .from('vehicles')
      .insert(vehicleData)
      .select()
      .single();

    if (error) throw error;
    return data;
  }
  ```

### 13.4 Testing RLS Policies

RLS testing is the most critical database test category. A misconfigured
policy can expose data to unauthorized users — this is a security
vulnerability, not just a bug.

- **MUST** test RLS policies with different user contexts — verify that
  each role sees only the data it should:

  ```ts
  // tests/rls/vehicles-rls.test.ts
  import { createClient } from '@supabase/supabase-js';

  // Create clients with different auth contexts
  const anonClient = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
  const adminClient = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

  // Helper: create authenticated client for a specific user
  async function createAuthenticatedClient(email: string, password: string) {
    const client = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
    await client.auth.signInWithPassword({ email, password });
    return client;
  }

  describe('vehicles RLS policies', () => {
    let userA: { id: string; client: SupabaseClient };
    let userB: { id: string; client: SupabaseClient };
    let vehicleA: { id: string };

    beforeAll(async () => {
      // Setup: create two users and a vehicle owned by userA
      // Use adminClient (service_role) to set up test data
      userA = await createTestUserWithClient('usera@test.com', 'password123');
      userB = await createTestUserWithClient('userb@test.com', 'password123');
      vehicleA = await insertTestVehicle(userA.id);
    });

    describe('SELECT policies', () => {
      it('allows user to read their own vehicles', async () => {
        const { data, error } = await userA.client
          .from('vehicles')
          .select('id')
          .eq('id', vehicleA.id);

        expect(error).toBeNull();
        expect(data).toHaveLength(1);
        expect(data![0].id).toBe(vehicleA.id);
      });

      it('blocks user from reading another user\'s vehicles', async () => {
        const { data, error } = await userB.client
          .from('vehicles')
          .select('id')
          .eq('id', vehicleA.id);

        expect(error).toBeNull();
        expect(data).toHaveLength(0);  // RLS filters it out silently
      });

      it('blocks anonymous access to vehicles', async () => {
        const { data, error } = await anonClient
          .from('vehicles')
          .select('id');

        expect(error).toBeNull();
        expect(data).toHaveLength(0);  // No anon policy → no access
      });
    });

    describe('INSERT policies', () => {
      it('allows user to create a vehicle assigned to themselves', async () => {
        const newVehicle = buildVehicle();
        const { error } = await userA.client
          .from('vehicles')
          .insert({ ...newVehicle, user_id: userA.id });

        expect(error).toBeNull();
      });

      it('blocks user from creating a vehicle assigned to another user', async () => {
        const newVehicle = buildVehicle();
        const { error } = await userA.client
          .from('vehicles')
          .insert({ ...newVehicle, user_id: userB.id });

        expect(error).not.toBeNull();  // WITH CHECK fails
      });
    });

    describe('UPDATE policies', () => {
      it('allows user to update their own vehicle', async () => {
        const { error } = await userA.client
          .from('vehicles')
          .update({ is_available: false })
          .eq('id', vehicleA.id);

        expect(error).toBeNull();
      });

      it('blocks user from transferring vehicle to another user', async () => {
        const { error } = await userA.client
          .from('vehicles')
          .update({ user_id: userB.id })
          .eq('id', vehicleA.id);

        expect(error).not.toBeNull();  // WITH CHECK prevents ownership transfer
      });
    });

    describe('DELETE policies', () => {
      it('blocks user from deleting another user\'s vehicle', async () => {
        const { error } = await userB.client
          .from('vehicles')
          .delete()
          .eq('id', vehicleA.id);

        // RLS silently filters — no rows match, so nothing is deleted
        // This is NOT an error; it simply deletes 0 rows
        expect(error).toBeNull();

        // Verify vehicle still exists
        const { data } = await userA.client
          .from('vehicles')
          .select('id')
          .eq('id', vehicleA.id);

        expect(data).toHaveLength(1);
      });
    });
  });
  ```

- **MUST** test the critical RLS scenarios per table:

  | Test | Expectation | Why |
  |---|---|---|
  | Owner reads own data | Returns data | Basic functionality |
  | User reads another's data | Returns empty (not error) | IDOR prevention |
  | Anonymous reads protected data | Returns empty | Public exposure prevention |
  | User inserts with own user_id | Succeeds | Basic functionality |
  | User inserts with another's user_id | Fails (WITH CHECK) | Impersonation prevention |
  | User updates own data | Succeeds | Basic functionality |
  | User transfers ownership via UPDATE | Fails (WITH CHECK) | Ownership theft prevention |
  | User deletes another's data | Deletes 0 rows | Data protection |

- **SHOULD** note that RLS violations on SELECT do not return errors —
  they silently return empty results. This means you must assert on
  `data.length`, not on `error`:

  ```ts
  // RLS blocks this SELECT — no error, just empty results
  const { data, error } = await userB.client
    .from('vehicles')
    .select('*')
    .eq('id', vehicleA.id);

  expect(error).toBeNull();       // no error!
  expect(data).toHaveLength(0);   // RLS silently filtered the row
  ```

### 13.5 Testing Constraints

- **SHOULD** test that constraints enforce business rules at the database
  level — these tests verify that even if application validation is
  bypassed, the database rejects invalid data:

  ```ts
  describe('vehicles constraints', () => {
    it('rejects negative price (CHECK constraint)', async () => {
      const vehicle = buildVehicle();
      const { error } = await adminClient
        .from('vehicles')
        .insert({ ...vehicle, user_id: testUser.id, price_cents: -100 });

      expect(error).not.toBeNull();
      expect(error!.code).toBe('23514');  // check_violation
    });

    it('rejects duplicate VIN (UNIQUE constraint)', async () => {
      const vin = 'WBA3A5G59DNP26082';

      // First insert succeeds
      await adminClient.from('vehicles').insert({
        ...buildVehicle(), user_id: testUser.id, vin,
      });

      // Second insert with same VIN fails
      const { error } = await adminClient.from('vehicles').insert({
        ...buildVehicle(), user_id: testUser.id, vin,
      });

      expect(error).not.toBeNull();
      expect(error!.code).toBe('23505');  // unique_violation
    });

    it('rejects vehicle without required user_id (FK constraint)', async () => {
      const { error } = await adminClient
        .from('vehicles')
        .insert({
          ...buildVehicle(),
          user_id: '00000000-0000-0000-0000-000000000000',  // non-existent
        });

      expect(error).not.toBeNull();
      expect(error!.code).toBe('23503');  // foreign_key_violation
    });
  });
  ```

### 13.6 Testing Migrations

- **MUST** verify that all migrations apply cleanly on an empty database —
  this is the "new developer" scenario:

  ```bash
  # Test: clean database from scratch
  supabase db reset
  # If this succeeds, all migrations are valid in sequence
  ```

- **SHOULD** verify that destructive migrations handle existing data
  correctly — test on a database with seed data:

  ```bash
  # Test: migrations on populated database
  supabase db reset          # apply all migrations + seed
  supabase migration new test_migration  # create a test migration
  supabase db reset          # verify everything still works
  ```

- **SHOULD** include migration tests in CI — `supabase db reset` should
  be part of the CI pipeline to catch broken migrations before they
  reach production
  (→ See [09-devops-cicd.md] when available)

### 13.7 Testing Soft Delete Behavior

- **SHOULD** verify that soft-deleted records are invisible in normal queries
  but recoverable when needed:

  ```ts
  describe('soft delete', () => {
    let vehicle: { id: string };

    beforeAll(async () => {
      vehicle = await insertTestVehicle(testUser.id);
    });

    it('hides soft-deleted vehicles from normal queries', async () => {
      // Soft delete it
      await adminClient
        .from('vehicles')
        .update({ deleted_at: new Date().toISOString() })
        .eq('id', vehicle.id);

      // Normal query should not find it
      const { data } = await userClient
        .from('vehicles')
        .select('id')
        .eq('id', vehicle.id);

      expect(data).toHaveLength(0);
    });

    it('allows recovery of soft-deleted vehicles', async () => {
      // Un-delete
      await adminClient
        .from('vehicles')
        .update({ deleted_at: null })
        .eq('id', vehicle.id);

      // Now visible again
      const { data } = await userClient
        .from('vehicles')
        .select('id')
        .eq('id', vehicle.id);

      expect(data).toHaveLength(1);
    });
  });
  ```

### 13.8 Database Testing Anti-Patterns

| Anti-Pattern | Problem | Correct Approach |
|---|---|---|
| **Testing against production database** | Risk of data corruption; flaky tests from real data changes | Dedicated test database (local Supabase) |
| **No RLS tests** | Policy misconfigurations go undetected until data breach | Test every table's RLS with multiple user contexts |
| **Hardcoded IDs in tests** | Tests break when seed data changes | Factory functions with generated data |
| **Tests depend on execution order** | Flaky when run in parallel or isolated | Each test creates its own data; use beforeAll/beforeEach |
| **Testing only with service_role** | Bypasses RLS entirely — tests pass but policies are untested | Test with authenticated user clients, not service_role |
| **No migration tests in CI** | Broken migrations discovered in production | `supabase db reset` in CI pipeline |
| **Testing repository logic through the API** | Slow, couples tests to HTTP layer | Test repositories directly for data access logic |
| **Asserting on `error` for RLS violations** | RLS SELECT violations return empty results, not errors | Assert on `data.length === 0`, not `error !== null` |

---

## 14. Database Design Checklist

These checklists distill the rules from this document into quick, actionable
verification steps. Use them during design, code review, and before release.

The format mirrors the checklists in
→ See [03-api-design.md, Section 14] and
→ See [07-security-standards.md, Section 17].

### 14.1 Pre-Implementation Checklist

Before writing any migration or query for a new table or feature, verify
that the design decisions are sound.

#### Schema Design

- [ ] Tables use `snake_case`, **plural** names
      (→ See [Section 2.1](#21-tables))
- [ ] Columns use `snake_case`; booleans prefixed with `is_` / `has_`;
      timestamps suffixed with `_at`; dates with `_on`
      (→ See [Section 2.2](#22-columns))
- [ ] Primary key is `UUID` with `DEFAULT gen_random_uuid()`
      (→ See [Section 3.2](#32-primary-keys--identifiers))
- [ ] All temporal columns use `TIMESTAMPTZ`, not `TIMESTAMP`
      (→ See [Section 3.1](#31-data-type-selection))
- [ ] Monetary values stored as `INTEGER` in cents with `_cents` suffix
      (→ See [Section 2.2](#22-columns))
- [ ] `created_at` and `updated_at` present with correct defaults
      (→ See [Section 3.3](#33-standard-columns))
- [ ] `updated_at` trigger (`update_updated_at_column`) applied
      (→ See [Section 3.3](#33-standard-columns))
- [ ] Soft delete (`deleted_at`) considered for business-critical entities
      (→ See [Section 3.4](#34-soft-delete))
- [ ] JSONB used only for truly semi-structured data, not to avoid
      proper schema design
      (→ See [Section 3.6](#36-jsonb-usage-guidelines))

#### Relationships & Integrity

- [ ] Foreign keys defined for **every** relationship
      (→ See [Section 4.1](#41-foreign-key-rules))
- [ ] All FK columns are indexed
      (→ See [Section 4.1](#41-foreign-key-rules))
- [ ] `ON DELETE` behavior explicitly chosen per FK — default `RESTRICT`
      (→ See [Section 4.2](#42-cascade-rules--the-default-is-safety))
- [ ] `CASCADE` used only for true composition relationships
      (→ See [Section 4.2](#42-cascade-rules--the-default-is-safety))
- [ ] Junction tables use composite PK `(entity_a_id, entity_b_id)`
      (→ See [Section 4.3](#43-relationship-patterns))

#### Constraints

- [ ] Columns default to `NOT NULL` — nullable only with justification
      (→ See [Section 5.1](#51-not-null--the-first-line-of-defense))
- [ ] `UNIQUE` constraints on naturally unique fields (email, VIN, slug)
      (→ See [Section 5.2](#52-unique-constraints))
- [ ] `CHECK` constraints for invariants (positive price, valid range)
      (→ See [Section 5.3](#53-check-constraints))
- [ ] All constraints explicitly named with standard prefixes
      (`pk_`, `fk_`, `uniq_`, `chk_`)
      (→ See [Section 2.5](#25-constraints))
- [ ] Enum type or CHECK chosen appropriately for value sets
      (→ See [Section 5.4](#54-enums-vs-check-vs-lookup-tables))

#### Naming

- [ ] All database objects follow the naming conventions
      (→ See [Section 2.10 — Quick Reference Table](#210-quick-reference-table))
- [ ] No abbreviations or cryptic names — everything is readable
- [ ] Consistent vocabulary — same concept uses same term everywhere

### 14.2 Pre-Release Checklist

Before deploying a migration or feature to staging or production.

#### Migrations

- [ ] Migration has a descriptive, timestamp-prefixed, verb-first name
      (→ See [Section 6.3](#63-migration-file-naming))
- [ ] Migration applies cleanly on empty database (`supabase db reset`)
      (→ See [Section 6.4](#64-migration-structure))
- [ ] Migration applies cleanly on database with existing data
- [ ] Destructive operations confirmed with backup availability
      (→ See [Section 6.5](#65-reversible-vs-irreversible-migrations))
- [ ] Large table operations use `CONCURRENTLY` where applicable
      (→ See [Section 6.6](#66-large-table-migrations))
- [ ] SQL reviewed (especially for Prisma-generated migrations)
- [ ] Seed data updated if new lookup tables were created
      (→ See [Section 6.7](#67-seed-data))

#### Security (RLS)

- [ ] RLS enabled on every new table
      (→ See [Section 7.1](#71-fundamental-rules))
- [ ] Separate policies for SELECT, INSERT, UPDATE, DELETE
      (→ See [Section 7.2](#72-how-rls-works-in-supabase))
- [ ] INSERT policies use `WITH CHECK` to prevent impersonation
- [ ] UPDATE policies use **both** `USING` and `WITH CHECK`
- [ ] Soft-deleted records filtered in SELECT policies
      (→ See [Section 7.5](#75-rls-and-soft-delete))
- [ ] Policies named following the convention
      `<operation>_<table>_<description>`
      (→ See [Section 2.8](#28-rls-policies))
- [ ] RLS policies tested with multiple user contexts
      (→ See [Section 13.4](#134-testing-rls-policies))

#### Performance

- [ ] Indexes created for FK columns, WHERE clauses, ORDER BY columns
      (→ See [Section 8.1](#81-when-to-create-indexes))
- [ ] Composite indexes have correct column order (selective first)
      (→ See [Section 8.3](#83-composite-indexes))
- [ ] Partial indexes used for soft-delete and common filter patterns
      (→ See [Section 8.4](#84-partial-indexes))
- [ ] `EXPLAIN ANALYZE` run on critical queries
      (→ See [Section 11.1](#111-explain-analyze--the-primary-diagnostic-tool))
- [ ] No `SELECT *` in production queries
      (→ See [Section 9.3](#93-query-safety-rules))
- [ ] All collection queries paginated with `LIMIT`
      (→ See [Section 9.5](#95-pagination-at-the-database-level))

#### Data Access

- [ ] All queries isolated in repository files
      (→ See [Section 9.1](#91-the-repository-pattern))
- [ ] Casing transformation at repository boundary (snake_case ↔ camelCase)
      (→ See [Section 9.2](#92-casing-transformation-snake_case--camelcase))
- [ ] No N+1 queries — related data fetched via joins or batch fetch
      (→ See [Section 9.4](#94-the-n1-query-problem))
- [ ] Soft delete filter applied in all queries (or via RLS)
      (→ See [Section 9.6](#96-soft-delete-in-queries))

#### Connections & Operations

- [ ] Connection string uses the pooled endpoint (port 6543) for queries
      (→ See [Section 10.2](#102-connection-pooling))
- [ ] Direct connection (port 5432) used only for migrations
- [ ] Prisma singleton pattern in place (if using Prisma with Next.js)
      (→ See [Section 10.3](#103-serverless-and-connection-challenges))
- [ ] Backup strategy confirmed for production
      (→ See [Section 12.1](#121-backup-strategy))
- [ ] Recovery procedure documented and tested at least once
      (→ See [Section 12.4](#124-backup-testing))

### 14.3 Quick Reference — Common Mistakes

| # | Mistake | Consequence | Section |
|---|---|---|---|
| 1 | No RLS on a Supabase table | Data publicly accessible via anon key | §7.1 |
| 2 | `UPDATE` policy without `WITH CHECK` | Users can transfer ownership to others | §7.2 |
| 3 | No FK constraints ("app enforces it") | Orphaned records from bugs or direct SQL | §4.1 |
| 4 | `ON DELETE CASCADE` on business entities | One delete wipes invoices, orders, payments | §4.2 |
| 5 | No index on FK columns | Parent deletes trigger sequential scans | §4.1 |
| 6 | `SELECT *` in production | Wastes bandwidth, leaks internal fields | §9.3 |
| 7 | N+1 queries in a loop | 100 items = 101 queries, crashes under load | §9.4 |
| 8 | `TIMESTAMP` without timezone | Silent timezone bugs in multi-region apps | §3.1 |
| 9 | Money as `FLOAT` or `NUMERIC` | Floating-point precision errors (€0.10 + €0.20 ≠ €0.30) | §3.1 |
| 10 | Editing applied migrations | Environment drift between dev/staging/prod | §6.1 |
| 11 | Production on Free plan (no backups) | Accidental deletion = permanent data loss | §12.1 |
| 12 | PrismaClient without singleton | Hot reload exhausts connections in development | §10.3 |
| 13 | Direct connection from serverless | Connection limit exhausted under load | §10.3 |
| 14 | All columns nullable | Invalid data enters via bugs or direct SQL | §5.1 |
| 15 | No soft delete on business entities | Accidental deletion is irreversible | §3.4 |

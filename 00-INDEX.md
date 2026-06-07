# 🗺️ Engineering Standards — Index & Navigation Guide

> **Scope:** Entry point and navigation map for the complete engineering standards collection.
>
> **Purpose:** Provides an overview of all standards documents, their relationships, status, and guidance on which document to consult for specific needs. This is not a standards document itself — it is the map that connects them all.
>
> **Audience:** Any developer (including future-you) opening the `standards/` folder for the first time.

---

## What Is This Collection

This is a modular set of engineering standards — a living reference that defines how software should be built, secured, tested, and shipped across all projects.

Rather than a single monolithic document, standards are split into focused, domain-specific files that complement each other through cross-references. Each document is self-contained enough to be useful on its own, but designed to work as part of the whole.

The collection is stack-agnostic in its principles. Specific technology choices are documented in the Technology Radar (→ See [02-technology-radar.md]) and as practical examples within each domain document.

---

## Quick Start

If you only have time for three documents, start here:

1. **[01-core-principles.md](./01-core-principles.md)** — The foundation. Every other document derives from the principles defined here.
2. **[07-security-standards.md](./07-security-standards.md)** — Security is non-negotiable. Read this before writing any production code.
3. **[06-testing-strategy.md](./06-testing-strategy.md)** — Quality gates and the test pyramid that validates everything else works.

---

## Document Map

| #  | Document                       | Description                                           | Status |
|----|--------------------------------|-------------------------------------------------------|--------|
| 00 | `00-INDEX.md`                  | This file — entry point and navigation guide          | ✅     |
| 00A| `00A-AI-OPERATING-PROTOCOL.md` | AI agent behavior rules and operating constraints     | ✅     |
| 01 | `01-core-principles.md`        | Philosophy, clean code, SOLID, naming, ADRs, DoD      | ✅     |
| 02 | `02-technology-radar.md`       | Technology choices, evaluation framework, stack guide | ✅     |
| 03 | `03-api-design.md`             | REST conventions, error handling, response envelopes  | ✅     |
| 04 | `04-database-standards.md`     | PostgreSQL, naming, migrations, RLS, indexing         | ✅     |
| 05 | `05-frontend-standards.md`     | React/Next.js, mobile-first, a11y, state management   | ✅     |
| 06 | `06-testing-strategy.md`       | Test pyramid, unit/integration/E2E, quality gates     | ✅     |
| 07 | `07-security-standards.md`     | Security by design, OWASP, auth, encryption, RGPD     | ✅     |
| 08 | `08-observability.md`          | Logging, monitoring, metrics, alerting                | ✅     |
| 09 | `09-devops-cicd.md`            | Docker, CI/CD pipelines, environments, deployment     | ✅     |
| 10 | `10-git-workflow.md`           | Branching, commits, PRs, versioning                   | ✅     |
| 11 | `11-project-management.md`     | Issues, boards, definition of done, checklists        | ✅     |
| 12 | `12-ai-engineering.md`         | LLM apps, RAG, evaluation, agents & harness, local inference, RGPD | ✅     |

### Templates

| Template                        | Description                              | Status |
|---------------------------------|------------------------------------------|--------|
| `adr-template.md`               | Architecture Decision Record template    | ✅     |
| `pr-template.md`                | Pull Request description template        | ✅     |
| `incident-report.md`            | Incident response report template        | ✅     |
| `data-inventory.md`             | Data inventory for privacy compliance    | ✅     |
| `briefing-template.md`          | Client intake questionnaire (reference — original is .docx) | ✅     |
| `proposal-template.md`          | Commercial proposal template (3 packages, client-facing) | ✅     |
| `project-master-template.md`    | Project definition document template (all phases)  | ✅     |

---

## How Documents Relate

```text
                    ┌─────────────────────┐
                    │  00-INDEX (you are  │
                    │       here)         │
                    └─────────┬───────────┘
                              │
                    ┌─────────▼───────────┐
                    │  01-core-principles │ ◄── Foundation for everything
                    └─────────┬───────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
    ┌─────────▼─────┐  ┌──────▼──────┐  ┌─────▼──────────┐
    │ 02-tech-radar │  │ 07-security │  │ 06-testing     │
    │ (what to use) │  │ (how to     │  │ (how to verify)│
    │               │  │  protect)   │  │                │
    └───────┬───────┘  └──────┬──────┘  └────────┬───────┘
            │                 │                  │
    ┌───────▼─────────────────▼──────────────────▼────────┐
    │              Domain-Specific Standards              │
    │  03-api  04-database  05-frontend  08-observability │
    └─────────────────────────┬───────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
    ┌─────────▼────┐  ┌───────▼─────┐  ┌──────▼─────────┐
    │ 09-devops    │  │ 10-git      │  │ 11-project-mgmt│
    │ (how to ship)│  │ (how to     │  │ (how to track) │
    │              │  │ collaborate)│  │                │
    └──────────────┘  └─────────────┘  └────────────────┘
```
> **12-ai-engineering** sits alongside the domain standards as the AI/LLM capstone — it builds on
> 02 (radar), 06 (testing/eval), 07 (security) and the domain docs (03/04/05/08), and never
> restates their *how*.

---

## Navigation Guide

**"I need to..."**

| If you need to...                                         | Read                           |
|-----------------------------------------------------------|--------------------------------|
| Understand how AI agents should interpret these standards | `00A-AI-OPERATING-PROTOCOL.md` |
| Understand the philosophy behind these standards          | `01-core-principles.md`        |
| Choose a technology or evaluate a new dependency          | `02-technology-radar.md`       |
| Design or review an API endpoint                          | `03-api-design.md`             |
| Create a table, write a migration, or define RLS          | `04-database-standards.md`     |
| Build a UI component or handle client-side state          | `05-frontend-standards.md`     |
| Write tests or define quality gates                       | `06-testing-strategy.md`       |
| Secure an application or review auth/encryption           | `07-security-standards.md`     |
| Set up logging, monitoring, or alerting                   | `08-observability.md`          |
| Configure Docker, CI/CD, or deployment pipelines          | `09-devops-cicd.md`            |
| Define branching strategy or PR conventions               | `10-git-workflow.md`           |
| Organize issues, boards, or track progress                | `11-project-management.md`     |
| Build an LLM/RAG feature, an agent, or evaluate AI output | `12-ai-engineering.md`         |
| Document an architectural decision                        | `templates/adr-template.md`    |
| Open a pull request                                       | `templates/pr-template.md`     |
| Report a production incident                              | `templates/incident-report.md` |
| Map personal data for RGPD compliance                     | `templates/data-inventory.md`  |
| Collect requirements from a client                        | `briefing-template.md`         |
| Create a commercial proposal for a client                 | `proposal-template.md`         |
| Define a new project (scope, requirements, tech direction)| `project-master-template.md`   |

---

## Conventions Used Across All Documents

### RFC Keywords

All documents use RFC 2119 keywords consistently:

| Keyword    | Meaning                                                  |
|------------|----------------------------------------------------------|
| **MUST**   | Required. A PR should be blocked if violated.            |
| **SHOULD** | Strongly recommended. Requires justification to skip.    |
| **MAY**    | Optional. Decided case-by-case.                          |

### Language

- All document content, code examples, and comments are written in **English**.
- Documents follow standard Markdown formatting.

### Cross-References

- Documents reference each other using the format: `→ See [XX-document-name.md]`
- Section-level references use: `→ See [XX-document-name.md] § Section Name`

### Document Precedence

When rules in different documents appear to conflict, apply this priority:

1. **[07-security-standards.md]** — Security rules override all other domains.
   If a security rule and a convenience rule conflict, security wins.
2. **[01-core-principles.md]** — Foundational principles apply unless a
   domain-specific document provides a more specific rule.
3. **Domain-specific document** (03, 04, 05, 08) — These contain the
   detailed rules for their domain. More specific rules override general
   principles.
4. **[02-technology-radar.md]** — Technology choices defined here constrain
   what domain documents can recommend. A domain document MUST NOT
   recommend a Hold technology without an ADR.

> When in doubt: security first, then principles, then domain specifics.

### Status Icons

| Icon | Meaning       |
|------|---------------|
| ✅   | Completed     |
| 🚧   | In Progress   |
| 📋   | Planned       |

### Deviations

Any significant deviation from a MUST or SHOULD rule requires an **Architecture Decision Record (ADR)** — → See [01-core-principles.md] § 9 and `templates/adr-template.md`.

---

## Contributing & Evolution

These standards are a **living collection** — they evolve as projects grow, new patterns emerge, and lessons are learned.

### When to Update

- A new project reveals a gap not covered by existing documents.
- A technology decision changes the baseline (document in the Technology Radar first).
- A post-mortem or incident exposes a missing standard.
- A rule consistently requires justification to skip — it may need revision.

### How to Update

1. Propose the change with context (what, why, impact).
2. If the change affects a MUST or SHOULD rule, create an **ADR** first.
3. Update the relevant document(s) and cross-references.
4. Update this INDEX if a new document is added or status changes.

### Versioning

- Documents do not use formal version numbers — Git history serves as the changelog.
- For major rewrites, a summary of changes **SHOULD** be noted at the top of the affected document.

---

### AI Agent Instructions

This document is designed to be consumed by AI coding agents (e.g., Claude
Code). When interpreting this document:

- **MUST**, **SHOULD**, and **MAY** are RFC 2119 keywords — treat MUST as non-negotiable constraints, SHOULD as strong defaults that require explicit justification to override, and MAY as contextual options.
- Cross-references (→ See [XX-document.md]) point to authoritative definitions — always defer to the referenced document for the full rule.
- When this document conflicts with [07-security-standards.md], the security document takes precedence.
- BAD/GOOD code examples are pattern-matching references — apply the principle behind the example, not just the literal code.
- Anti-pattern tables describe common mistakes — use them as negative examples when reviewing or generating code.
- This file is the entry point. When uncertain which document applies, consult the Navigation Guide table.
- If generating code requires violating a MUST rule, the AI **MUST stop** and ask the human for permission before proceeding — never silently override a standard.
- **MUST NOT** over-engineer — always prefer the simplest solution that meets the stated requirements. Do not add abstractions, patterns, or infrastructure beyond what was explicitly requested (→ See [01-core-principles.md, §12]).

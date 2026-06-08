# Engineering Standards

A personal, opinionated engineering standards suite — the single source of truth
for my software projects (freelance and personal). It is written to be read and
**executed by AI coding agents** (primarily Claude Code), not only by humans:
every rule uses RFC 2119 keywords (**MUST** / **SHOULD** / **MAY**), and documents
cross-reference each other instead of duplicating content.

Start at **[`00-INDEX.md`](standards/00-INDEX.md)** — the authoritative map and navigation guide.

## What this is (and isn't)

- **Is:** a coherent system of standards across domains, with strict boundaries —
  the [Technology Radar](standards/02-technology-radar.md) decides *what & why* (tool selection),
  and each domain document decides *how*. No tool is re-selected in two places; no
  rule is defined twice.
- **Isn't:** a tutorial, a framework, or legal advice. The RGPD / EU AI Act material
  in the AI document is engineering guidance, not legal counsel.

## Repository Structure

```
standards/   ← 14 documentation files (00-INDEX.md … 12-ai-engineering.md)
templates/   ← 7 template files
scripts/     ← maintenance utilities (lint_refs.py, migrate.py)
```

## Documents

| #   | Document | Scope |
|-----|----------|-------|
| 00  | [00-INDEX.md](standards/00-INDEX.md) | Index, document map, navigation guide |
| 00A | [00A-AI-OPERATING-PROTOCOL.md](standards/00A-AI-OPERATING-PROTOCOL.md) | How an AI agent must operate against this suite |
| 01  | [01-core-principles.md](standards/01-core-principles.md) | Core principles & engineering philosophy (+ glossary) |
| 02  | [02-technology-radar.md](standards/02-technology-radar.md) | Technology Radar — *what & why* (tool selection) |
| 03  | [03-api-design.md](standards/03-api-design.md) | API design standards |
| 04  | [04-database-standards.md](standards/04-database-standards.md) | Database standards |
| 05  | [05-frontend-standards.md](standards/05-frontend-standards.md) | Frontend standards |
| 06  | [06-testing-strategy.md](standards/06-testing-strategy.md) | Testing strategy |
| 07  | [07-security-standards.md](standards/07-security-standards.md) | Security (Security by Design) |
| 08  | [08-observability.md](standards/08-observability.md) | Observability standards |
| 09  | [09-devops-cicd.md](standards/09-devops-cicd.md) | DevOps & CI/CD |
| 10  | [10-git-workflow.md](standards/10-git-workflow.md) | Git workflow & collaboration |
| 11  | [11-project-management.md](standards/11-project-management.md) | Project management |
| 12  | [12-ai-engineering.md](standards/12-ai-engineering.md) | AI engineering — LLM apps, RAG, evaluation, agents & harness, local inference & RGPD |

## Templates

| Template | Description |
|----------|-------------|
| [adr-template.md](templates/adr-template.md) | Architecture Decision Record |
| [pr-template.md](templates/pr-template.md) | Pull Request description |
| [incident-report.md](templates/incident-report.md) | Incident response report |
| [data-inventory.md](templates/data-inventory.md) | Data inventory for RGPD compliance |
| [briefing-template.md](templates/briefing-template.md) | Client intake questionnaire |
| [proposal-template.md](templates/proposal-template.md) | Commercial proposal (3 packages) |
| [project-master-template.md](templates/project-master-template.md) | Project definition document |

## Conventions

- **RFC 2119 keywords** — MUST / SHOULD / MAY carry their normative meaning.
- **Cross-references** — `→ See [04-database-standards.md, §X]` points to the
  authoritative definition; always defer to the referenced document.
- **Boundaries** — the radar decides *what & why*; domain docs decide *how*. AI-specific
  security and action-safety live in `12`, not `07`.
- **AI-optimized** — HTML comments carry agent guidance invisible in rendered output;
  rules follow a Rules → Why → BAD/GOOD → cross-refs shape.

## Using with AI coding agents

This suite is designed to be loaded as context for an AI coding agent. The intended
workflow is a distilled `CLAUDE.md` (always-on critical rules) plus on-demand loading
of the relevant standard for the task at hand. See
[00A-AI-OPERATING-PROTOCOL.md](standards/00A-AI-OPERATING-PROTOCOL.md).

## License

- **Documentation** (all `.md` standards and templates in `standards/` and `templates/`): [CC BY 4.0](LICENSE).
- **Scripts** (`scripts/`): [MIT](LICENSE-MIT).

© 2026 João Martins.
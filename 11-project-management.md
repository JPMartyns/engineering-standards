# 📋 Project Management Standards

> **Scope:** Cross-cutting standards for organizing, planning, tracking, and
> managing software development work — from issue creation through delivery
> and retrospective.
>
> **Purpose:** This document answers the question: "How do I organize work,
> define priorities, track progress, and ensure nothing is forgotten —
> whether working solo, with a freelance client, or on a team?" It is the
> "how to track" layer that complements "how to ship"
> (→ See [09-devops-cicd.md]) and "how to collaborate" (→ See [10-git-workflow.md]).
>
> **Keywords:**
> - **MUST** = required (PR should be blocked if violated)
> - **SHOULD** = strongly recommended (requires justification to skip)
> - **MAY** = optional (case-by-case)

---

## 0. How to Use This Document

This document defines **project management standards** — how to organize
work into issues, track progress on boards, plan and estimate work, manage
technical debt, execute large-scale refactoring, and run retrospectives.

It does **not** define:

- **Core engineering principles** — philosophy, clean code, SOLID, naming,
  and the universal Definition of Done live in
  → See [01-core-principles.md]. This document **references** the DoD and
  shows how to integrate it into the tracking workflow.
- **Refactoring techniques** — the Boy Scout Rule, Extract Function,
  Rename Variable, and other code-level techniques live in
  → See [01-core-principles.md, §13]. This document covers **planning and
  managing** large-scale refactoring efforts, not the techniques
  themselves.
- **Architecture Decision Records** — ADR structure, quality rules, and
  organization live in → See [01-core-principles.md, §9]. This document
  references ADRs as a required step before significant changes.
- **Git workflow and PR standards** — branching strategy, commit
  conventions, PR templates, and code review live in
  → See [10-git-workflow.md]. This document covers how issues **link to** PRs
  and commits, not the PR workflow itself.
- **Security deployment checklists** — the full security checklist
  (Level 1/2/3) lives in → See [07-security-standards.md, §17]. This
  document **consolidates** pre-launch checklists by referencing the
  domain-specific ones.
- **DevOps checklists** — new project setup, pre-deployment, and
  post-deployment checklists live in → See [09-devops-cicd.md, §9]. This
  document references these and provides a unified pre-launch view.
- **Technology choices** — tool evaluation and selection live in
  → See [02-technology-radar.md]. This document assumes GitHub Issues and
  GitHub Projects as the default tracking tools.

### Technology Versions

This document is written against the following tool versions:

| Tool | Version / State | Date |
|------|-----------------|------|
| **GitHub Issues** | Sub-issues (GA), Issue Types (GA), Issue Forms (YAML), Advanced Search | April 2025 GA |
| **GitHub Projects** | Table, Board, Roadmap views; Hierarchy View (GA); Custom Fields; Built-in Workflows | March 2026 GA |
| **GitHub Actions** | Workflow automations for project boards | Stable |

### Document Relationships

```text
11-project-management.md (this document)
 ├── References → 01-core-principles.md (DoD §11, ADR §9, Refactoring §13)
 ├── References → 07-security-standards.md (security checklists §17)
 ├── References → 09-devops-cicd.md (devops checklists §9)
 ├── References → 10-git-workflow.md (PR standards §5, branching §2)
 ├── References → 00-INDEX.md (contributing & evolution)
 ├── Referenced by → 01-core-principles.md §13 (refactoring planning)
 ├── Referenced by → 10-git-workflow.md §5 (issue linking)
 └── Provides → templates/incident-report.md (post-incident template)
```

### Boundary Definitions

| Question | This Document (11) | Other Document |
|----------|--------------------|----------------|
| **How** to organize work into issues and boards? | ✅ Sections 2–4 | — |
| **How** to estimate and plan work? | ✅ Section 5 | — |
| **How** to manage technical debt and refactoring? | ✅ Section 6 (planning and tracking) | → See [01-core-principles.md, §13] (refactoring techniques) |
| **How** to handle incidents and post-mortems? | ✅ Section 7 (process) | → See [07-security-standards.md, §16] (response phases) |
| **How** to run pre-launch checklists? | ✅ Section 8 (consolidated view) | → See [07-security-standards.md, §17] + [09-devops-cicd.md, §9] (domain checklists) |
| **How** to adapt process to project stage? | ✅ Section 9 | — |
| **How** to write ADRs? | — | → See [01-core-principles.md, §9] |
| **How** to write commits, PRs, and do code review? | — | → See [10-git-workflow.md] |
| **Which** tools to use for tracking? | — | → See [02-technology-radar.md] (this doc assumes GitHub Issues + Projects) |

### AI Agent Instructions

This document is designed to be consumed by AI coding agents (e.g., Claude
Code). When interpreting this document:

- **MUST**, **SHOULD**, and **MAY** are RFC 2119 keywords — treat MUST as non-negotiable constraints, SHOULD as strong defaults that require explicit justification to override, and MAY as contextual options.
- Cross-references (→ See [XX-document.md]) point to authoritative definitions — always defer to the referenced document for the full rule.
- The "By Project Stage" section (§9) determines which rules apply based on the current project context. Always check §9 before applying the full weight of every rule to a personal project.
- When this document conflicts with [07-security-standards.md], the security document takes precedence.
- BAD/GOOD code examples are pattern-matching references — apply the principle behind the example, not just the literal code.
- Anti-pattern tables at the end of each section describe common mistakes — use them as negative examples when reviewing work.
- If generating code requires violating a MUST rule, the AI **MUST stop** and ask the human for permission before proceeding — never silently override a standard.
- **MUST NOT** over-engineer — always prefer the simplest solution that meets the stated requirements. Do not add abstractions, patterns, or infrastructure beyond what was explicitly requested (→ See [01-core-principles.md, §12]).

---

## 1. Project Management Philosophy

### 1.1 Visibility Over Process

The purpose of project management is not to create process — it is to
create **visibility**. At any point in time, you (or your client, or your
team) should be able to answer:

- What is being worked on right now?
- What is blocked, and why?
- What is coming next?
- What was completed, and when?

Every practice in this document exists to make these questions answerable
with a glance at the project board. If a practice does not improve
visibility, it is overhead.

### 1.2 Solo Developer ≠ No Planning

Working alone does not mean planning is unnecessary. In fact, the opposite
is true — without a team to create natural checkpoints (standups, reviews,
discussions), a solo developer relies entirely on their own discipline.
Issues and boards are not bureaucracy — they are how you manage yourself.

A solo developer without a board:
- Starts tasks, gets distracted, forgets what was in progress
- Has no record of what was completed last week (useful for client
  updates and self-assessment)
- Loses track of technical debt and "I'll fix it later" promises
- Cannot answer the four visibility questions above

A solo developer with a board:
- Has a clear queue of what to do next
- Can context-switch safely (the board remembers even when you forget)
- Has a history of completed work (valuable for client invoicing,
  portfolio building, and learning reflections)
- Makes deliberate choices about what to defer vs what to tackle now

### 1.3 Plan Enough to Reduce Risk, Not Enough to Create Bureaucracy

Planning exists on a spectrum. Too little planning leads to chaos, rework,
and missed requirements. Too much planning leads to analysis paralysis,
outdated plans, and work that serves the plan instead of the product.

The correct amount of planning is the **minimum needed to reduce the
risk of the current project stage**:

- A personal learning project needs a list of tasks — not a Gantt chart.
- A freelance client MVP needs milestones and issue tracking — not
  sprint ceremonies.
- A team project with external dependencies needs estimation, sprint
  planning, and coordination — but still not a 50-page project plan.

**Rule of thumb:** if the planning artifact takes longer to maintain than
the work it organizes, reduce the planning.

### 1.4 Pragmatic Over Dogmatic

This document does not prescribe Scrum, Kanban, SAFe, or any specific
methodology. It prescribes **practices** that work across methodologies
and project sizes:

- Issues as the unit of work
- Boards for visibility
- Small deliverable increments
- Regular reflection and adjustment

These practices are compatible with any methodology a team chooses to
adopt. The methodology is a team decision — the tracking discipline is
the standard.

### 1.5 Rules

- **MUST** have a way to answer the four visibility questions (§1.1) at
  any point in the project — the specific tool may vary, but visibility
  is non-negotiable
- **MUST** create issues before starting significant work — even in solo
  projects (→ §2)
- **SHOULD** keep planning overhead proportional to project risk — a
  learning project does not need sprint ceremonies
- **SHOULD** scale practices up as the project grows, not start with
  maximum ceremony (→ §9)
- **MUST NOT** use "I'm working alone" as justification for zero
  tracking — solo developers benefit the most from external memory
  systems (boards, issues)

---

## 2. Issue Management

An issue is the **atomic unit of work** in the project management system.
Every significant piece of work — a feature, a bug fix, a chore, a
research spike — begins as an issue. Issues create the link between
**intent** (what needs to be done) and **execution** (PRs, commits,
deployments).

### 2.1 Issue-First Workflow

- **MUST** create an issue before starting any significant work — a
  feature, a bug fix, a refactoring task, or a research spike
- **MUST** reference the issue in the branch name and PR
  (→ See [10-git-workflow.md, §2])
- **SHOULD** create an issue even for small tasks if they need to be
  tracked or communicated to a client
- **MAY** skip issue creation for trivial fixes (typo corrections,
  one-line formatting changes) that do not affect behavior

**Why issue-first matters:** An issue is the "contract" between planning
and execution. Without it, there is no record of why work was done, no
place to attach acceptance criteria, and no way to track progress on a
board. The issue also provides the context that code review needs — the
reviewer can understand the "why" from the issue before evaluating the
"how" in the PR.

### 2.2 Issue Types

GitHub Issues now supports **Issue Types** (GA since April 2025) at the
organization level, providing a standardized classification across all
repositories. For personal (non-organization) accounts, use labels to
achieve the same classification.

**Standard issue types for these engineering standards:**

| Type | Purpose | Examples |
|------|---------|----------|
| **Feature** | New functionality or user-visible improvement | "Add user avatar upload", "Implement dark mode" |
| **Bug** | Incorrect behavior that deviates from expected functionality | "Login fails with special characters in password" |
| **Task** | Maintenance, chore, or operational work that is not a feature or bug | "Update dependencies", "Configure CI pipeline", "Write API docs" |
| **Tech Debt** | Improvements to code quality, architecture, or developer experience that do not change user-visible behavior | "Refactor auth module to use service layer", "Remove deprecated API endpoints" |
| **Spike** | Time-boxed research or investigation to reduce uncertainty before committing to an approach | "Investigate Stripe vs Paddle for payments", "Prototype real-time sync with Supabase Realtime" |

**Rules:**

- **MUST** classify every issue with exactly one type — an issue cannot
  be both a Feature and a Bug
- **SHOULD** use GitHub Issue Types when working in an organization
  repository
- **SHOULD** use labels (prefixed with `type:`) as fallback in personal
  repositories where Issue Types are not available
- **MUST** time-box Spike issues — define a maximum duration (e.g., 4
  hours, 1 day) in the issue description. The output of a spike is a
  decision or an ADR, not production code

### 2.3 Issue Structure

Every issue **MUST** have a clear structure that provides enough context
for someone (including your future self, or an AI agent) to understand
and execute the work.

**Minimum required fields:**

```markdown
## Summary
One-sentence description of what needs to be done and why.

## Acceptance Criteria
- [ ] Criterion 1: specific, verifiable condition
- [ ] Criterion 2: specific, verifiable condition
- [ ] Criterion 3: specific, verifiable condition

## Context (if needed)
Additional background, screenshots, links, or technical notes.
```

**Rules:**

- **MUST** write a descriptive title that communicates the intent
  without opening the issue — "Add email validation to registration
  form" not "Fix form" or "Registration issue"
- **MUST** include acceptance criteria — these are the conditions that
  define when the issue is complete. They should be specific and
  verifiable, not vague ("works correctly")
- **SHOULD** include context when the issue requires background
  knowledge — a screenshot of the bug, a link to the design, a
  reference to a related discussion
- **SHOULD** link related issues when they exist (blocks, is blocked
  by, relates to)
- **MAY** include technical notes or implementation hints, but these
  are suggestions, not constraints — the developer executing the work
  decides the approach

### 2.4 Labels Taxonomy

Labels provide lightweight metadata for filtering, searching, and
organizing issues across views. Keep the label set small and consistent
— too many labels create noise instead of signal.

**Recommended label categories:**

| Category | Labels | Purpose |
|----------|--------|---------|
| **Priority** | `priority:critical`, `priority:high`, `priority:medium`, `priority:low` | Triage and ordering |
| **Type** (fallback) | `type:feature`, `type:bug`, `type:task`, `type:tech-debt`, `type:spike` | Classification when Issue Types are unavailable |
| **Domain** | `domain:frontend`, `domain:api`, `domain:database`, `domain:infra`, `domain:docs` | Area of the codebase affected |
| **Status** | `status:blocked`, `status:needs-info`, `status:wontfix` | Special states not covered by board columns |

**Rules:**

- **MUST** apply a priority label to every issue during triage
- **SHOULD** keep the total number of labels under 20 — if you need
  more, some labels are probably redundant or too granular
- **SHOULD** use consistent color coding across projects:
  - Red shades for priority (darker = higher)
  - Blue shades for domain
  - Yellow/orange for status flags
- **MUST NOT** use labels as a substitute for board columns — "in
  progress" is a board state, not a label

### 2.5 Issue Forms (YAML Templates)

Issue Forms provide structured templates with typed fields (text inputs,
dropdowns, checkboxes, file uploads) that replace free-form Markdown
templates. They ensure that every issue is created with the required
information, reducing back-and-forth.

**Templates are stored in `.github/ISSUE_TEMPLATE/` as `.yml` files.**

**Feature Request template example:**

```yaml
name: "✨ Feature Request"
description: "Propose a new feature or improvement"
title: "[Feature]: "
labels: ["type:feature", "priority:medium"]
type: "Feature"
body:
  - type: markdown
    attributes:
      value: |
        Thank you for suggesting a feature. Please fill in the details below.
  - type: textarea
    id: summary
    attributes:
      label: Summary
      description: "What do you want to achieve? Why is this needed?"
    validations:
      required: true
  - type: textarea
    id: acceptance-criteria
    attributes:
      label: Acceptance Criteria
      description: "List the specific conditions that define 'done'."
      placeholder: |
        - [ ] Criterion 1
        - [ ] Criterion 2
    validations:
      required: true
  - type: textarea
    id: context
    attributes:
      label: Additional Context
      description: "Screenshots, mockups, links, or technical notes."
    validations:
      required: false
```

**Bug Report template example:**

```yaml
name: "🐞 Bug Report"
description: "Report incorrect behavior"
title: "[Bug]: "
labels: ["type:bug", "priority:high"]
type: "Bug"
body:
  - type: textarea
    id: description
    attributes:
      label: Bug Description
      description: "What happened? What did you expect to happen?"
    validations:
      required: true
  - type: textarea
    id: steps
    attributes:
      label: Steps to Reproduce
      description: "Minimal steps to reproduce the behavior."
      placeholder: |
        1. Go to '...'
        2. Click on '...'
        3. See error
    validations:
      required: true
  - type: textarea
    id: environment
    attributes:
      label: Environment
      description: "Browser, OS, Node version, etc."
    validations:
      required: false
  - type: textarea
    id: logs
    attributes:
      label: Relevant Logs or Screenshots
      description: "Paste logs or attach screenshots."
    validations:
      required: false
```

**Configuration file (`.github/ISSUE_TEMPLATE/config.yml`):**

```yaml
blank_issues_enabled: false
contact_links:
  - name: "💬 Questions & Discussion"
    url: https://github.com/your-org/your-repo/discussions
    about: "Use Discussions for questions, not Issues."
```

**Rules:**

- **SHOULD** use Issue Forms (YAML) instead of Markdown templates for
  all standard issue types — forms enforce structure and required fields
- **SHOULD** disable blank issues (`blank_issues_enabled: false`) to
  guide contributors toward structured templates
- **SHOULD** include the `type` field in templates to auto-assign the
  GitHub Issue Type (when using an organization)
- **MAY** create additional templates for specific recurring needs
  (e.g., "Client Feedback", "Infrastructure Request")

### 2.6 Sub-Issues and Hierarchy

GitHub sub-issues (GA since April 2025) support parent-child
relationships between issues, enabling hierarchical work decomposition
without external tools.

**Hierarchy model:**

```text
Epic-level issue (Feature)
├── Sub-issue 1: Backend API endpoint
├── Sub-issue 2: Frontend form component
├── Sub-issue 3: Database migration
└── Sub-issue 4: E2E test coverage
```

**Capabilities:**

- Up to 100 sub-issues per parent issue
- Up to 8 levels of nesting (though 2–3 levels is recommended)
- Sub-issue progress is automatically tracked and displayed on the
  parent
- Hierarchy View in GitHub Projects (GA March 2026) shows the full
  tree directly in table views

**Rules:**

- **SHOULD** use sub-issues to decompose large features into smaller,
  independently deliverable pieces of work
- **SHOULD** keep hierarchy depth to 2–3 levels — deeper nesting
  usually signals that the decomposition is too granular or the
  parent issue is too broad
- **MUST** ensure each sub-issue is independently actionable — it
  should make sense on its own, not only in the context of the parent
- **SHOULD** ensure each sub-issue maps to a single PR where possible
  (→ See [10-git-workflow.md, §5.1])
- **MUST NOT** use sub-issues as a substitute for acceptance criteria
  checklists — sub-issues are separate units of work, checklists are
  verification steps within a single unit

### 2.7 Linking Issues to PRs and Commits

The connection between issues and code is the backbone of traceability.
When done correctly, you can trace any line of code back to the issue
that motivated it, and any issue forward to the PR that resolved it.

**Mechanisms:**

- **Branch name:** includes the issue number
  (→ See [10-git-workflow.md, §2]) — e.g., `feat/GH-42-user-avatar`
- **PR description:** links the issue with a closing keyword — e.g.,
  `Closes #42`, `Fixes #42`, `Resolves #42`
- **Commit message:** references the issue in the footer
  (→ See [10-git-workflow.md, §3]) — e.g., `feat: add avatar upload (#42)`

**Rules:**

- **MUST** link every PR to the issue it resolves using a GitHub
  closing keyword (`Closes #N`, `Fixes #N`, or `Resolves #N`) — this
  automatically moves the issue to Done when the PR is merged
- **MUST** include the issue number in the branch name for
  traceability
- **SHOULD** reference issue numbers in commit messages for commits
  that directly address the issue
- **MUST NOT** close issues manually when a PR exists — let the
  closing keyword handle it automatically to maintain the audit trail

### 2.8 Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **"Fix stuff" issue** | Vague title, no acceptance criteria — impossible to verify completion | Write a specific title and at least 2 acceptance criteria before starting work |
| **Issue graveyard** | Issues are created but never triaged, prioritized, or closed — the backlog becomes noise | Triage weekly: prioritize, close stale issues, or move to an "Icebox" column |
| **Mega-issue** | A single issue covers weeks of work with no decomposition | Decompose into sub-issues, each deliverable in 1–3 days |
| **PR without issue** | Code lands with no tracking — "why was this done?" is unanswerable | Enforce issue-first workflow; only trivial fixes (typos) skip this |
| **Duplicate tracking** | Same work tracked in issues AND a spreadsheet AND a Notion doc | One source of truth: GitHub Issues. Everything else references it |
| **Labels as status** | Using labels like "in progress" or "done" instead of board columns | Use board columns for workflow status; use labels for metadata (priority, domain) |

---

## 3. Project Boards

A project board is the **visual representation of work state**. It
transforms a list of issues into a workflow — showing what is waiting,
what is active, what is being reviewed, and what is complete. The board
is the primary tool for answering the four visibility questions defined
in §1.1.

### 3.1 GitHub Projects as the Default Tool

GitHub Projects is the default project management tool for all projects
covered by these engineering standards. This choice is deliberate:

- **Proximity to code:** issues, PRs, commits, and CI status are natively
  linked — no synchronization overhead
- **Hierarchy View (GA March 2026):** sub-issues render as expandable
  trees directly in table views, up to 8 levels deep
- **Multiple views:** the same data can be viewed as a board (kanban),
  table (spreadsheet), or roadmap (timeline) — each optimized for a
  different activity
- **Custom fields:** iteration, priority, dates, numbers, single-select,
  and text fields — up to 50 per project
- **Built-in automations:** status auto-updates on issue close, PR merge,
  or item addition — zero configuration required
- **Free tier:** available on all GitHub plans, including free personal
  accounts

### 3.2 Board Columns (Workflow States)

The standard board uses five columns representing the lifecycle of a
work item:

| Column | Definition | Entry Criteria | Exit Criteria |
|--------|------------|----------------|---------------|
| **Backlog** | Work that has been identified but is not yet ready to start. Issues may lack full acceptance criteria or depend on unresolved questions. | Issue exists with at least a title and summary | Issue has acceptance criteria and is triaged (priority assigned) |
| **Ready** | Work that is fully defined, prioritized, and ready for a developer to pick up. No blockers, no open questions. | Acceptance criteria are complete, no blockers, priority assigned | Developer assigns themselves and moves to In Progress |
| **In Progress** | Work that is actively being developed. A developer is assigned and a branch exists. | Developer is assigned, branch created, issue linked | PR is opened and ready for review |
| **In Review** | A PR has been opened and is awaiting code review (or self-review in solo projects). | PR opened, CI passing, DoD checklist included in PR description | PR approved, all review feedback addressed |
| **Done** | Work is merged to main, deployed (or ready to deploy), and verified. The issue is closed. | PR merged to main, closing keyword auto-closes issue | N/A — terminal state |

**Rules:**

- **MUST** use these five columns as the baseline workflow — additional
  columns may be added only if the project has a specific need (e.g.,
  "QA" column for projects with a dedicated QA step)
- **MUST** move issues across columns as work progresses — the board
  must reflect reality at all times
- **MUST** move an issue to In Progress when development begins, not
  when the issue is "thought about"
- **MUST** move an issue to Done only after the PR is merged to main —
  not after the PR is opened, not after review approval
- **MUST NOT** have more than 2–3 items in "In Progress" per developer
  at any time — if you are working on more, you are context-switching
  too much
- **SHOULD** configure the built-in workflow automation to auto-set
  status to "Done" when issues are closed and PRs are merged

### 3.3 Views

GitHub Projects supports multiple view types. Each serves a different
purpose:

**Board View (Kanban)**
- Primary view for daily work — shows the flow of items across columns
- Best for: answering "what is the current state of work?"
- Group by: Status (default), Assignee, Priority

**Table View (Spreadsheet)**
- High-density view for backlog grooming and triage
- Best for: bulk editing, filtering, sorting, and reviewing metadata
- Show columns: Title, Type, Priority, Assignee, Iteration, Labels
- Enable Hierarchy View (View menu → Show hierarchy) to see sub-issue
  trees inline

**Roadmap View (Timeline)**
- Date-based view for milestone planning and client visibility
- Best for: answering "when will this be delivered?"
- Requires: Date fields (Start Date, Target Date) or Iteration fields
- Configure vertical markers for iterations and milestones

**Rules:**

- **SHOULD** create at least two saved views: a Board view for daily
  work and a Table view for backlog management
- **SHOULD** enable Hierarchy View in the Table view to visualize
  sub-issue relationships
- **MAY** create a Roadmap view when working with client milestones or
  time-based deliverables
- **MAY** create filtered views for specific purposes (e.g., "My Work"
  filtered by assignee, "Tech Debt" filtered by type)

### 3.4 Custom Fields

Custom fields add structured metadata to issues beyond the built-in
fields (assignee, labels, milestone).

**Recommended custom fields:**

| Field | Type | Purpose |
|-------|------|---------|
| **Priority** | Single select | `Critical`, `High`, `Medium`, `Low` — drives triage ordering |
| **Size** | Single select | `XS`, `S`, `M`, `L`, `XL` — T-shirt sizing for estimation (→ §4) |
| **Iteration** | Iteration | Sprint or cycle tracking — auto-supports date ranges and breaks |
| **Start Date** | Date | When work began — enables Roadmap view |
| **Target Date** | Date | When work should be complete — enables Roadmap view |
| **Domain** | Single select | `Frontend`, `API`, `Database`, `Infra`, `Docs` — area of codebase |

**Rules:**

- **SHOULD** define Priority and Size fields for projects that use
  estimation (→ §4)
- **SHOULD** define Iteration fields for projects using sprint-based
  planning
- **MAY** define Date fields for projects with client milestones or
  deadline-driven deliverables
- **MUST NOT** create custom fields that duplicate information already
  available through labels or built-in fields — this creates
  synchronization overhead

### 3.5 Board Hygiene

A board is only useful if it reflects reality. Stale boards erode trust
and reduce visibility.

**Weekly triage ritual (15–30 minutes):**

1. **Review "In Progress"** — Is everything listed actually being worked
   on? Move stalled items back to Ready or add a `status:blocked` label
   with a comment explaining the blocker.
2. **Review "Backlog"** — Are there items that have been sitting for
   more than 4 weeks without being promoted to Ready? Either prioritize
   them, refine them, or close them as "wontfix" with a comment.
3. **Review "Done"** — Are all completed items actually closed? Clean
   up any that were moved manually but not auto-closed by a PR merge.
4. **Check stale issues** — Any issue with no activity for 30+ days
   should be reviewed: is it still relevant? Does it need more
   information?
5. **Review sub-issue progress** — Check parent issues with incomplete
   sub-issues. Are any sub-issues blocked or forgotten?

**Rules:**

- **MUST** triage the board at least once per week — even in solo
  projects
- **SHOULD** configure auto-archive to archive items in the Done column
  after 14 days (GitHub Projects built-in workflow)
- **MUST NOT** let the "In Progress" column become a dumping ground —
  if something has been "in progress" for more than a week without a
  PR, it needs attention
- **SHOULD** close issues that will not be addressed with a `wontfix`
  or `duplicate` label and a brief comment explaining why — an honest
  closed backlog is more valuable than a bloated open one

### 3.6 Built-in Workflows and Automations

GitHub Projects includes built-in workflows that reduce manual board
management. Two workflows are enabled by default:

1. **Auto-close → Done:** When an issue or PR is closed, its status is
   automatically set to Done.
2. **Auto-merge → Done:** When a PR is merged, its status is
   automatically set to Done.

**Additional recommended automations:**

| Automation | Type | Configuration |
|------------|------|---------------|
| **Auto-add issues** | Built-in | Automatically add new issues from specific repositories to the project when they match a filter (e.g., `is:issue is:open`) |
| **Auto-archive** | Built-in | Archive items with status "Done" that have not been updated in 14 days |
| **Auto-set status on PR open** | GitHub Actions | When a PR is opened that references an issue, move the issue to "In Review" |
| **Auto-assign to project** | GitHub Actions | Use `actions/add-to-project` to add issues/PRs to the project on creation |

**Rules:**

- **MUST** keep the two default workflows enabled (close → Done,
  merge → Done)
- **SHOULD** configure auto-add to pull new issues into the project
  automatically
- **SHOULD** configure auto-archive to keep the Done column clean
- **MAY** add GitHub Actions automations for more complex workflows
  as the team grows

### 3.7 Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Ghost board** | Board exists but nobody updates it — columns do not reflect reality | Enforce weekly triage; configure automations to reduce manual updates |
| **Column explosion** | 8+ columns with fine-grained states ("Dev Done", "QA Ready", "QA In Progress", "QA Done", "Staging", "Prod") | Keep 5 columns as baseline; add only if the project has a distinct workflow step with a different person responsible |
| **WIP overload** | 10 items "In Progress" for one developer | Limit WIP to 2–3 items per developer; move excess back to Ready |
| **No "Ready" definition** | Items move from Backlog directly to In Progress without being refined | Enforce entry criteria: acceptance criteria must exist before an item can be "Ready" |
| **Manual Done** | Issues are moved to Done manually instead of via PR merge | Use closing keywords in PRs; let automations handle the status transition |
| **Stale backlog** | Hundreds of open issues, most irrelevant or outdated | Triage weekly; close issues older than 90 days without activity; be honest about what will actually get done |

---

## 4. Planning & Estimation

Estimation exists to support **decision-making**, not to create
commitments. The goal is to understand relative effort so that work can
be prioritized, sequenced, and communicated — not to predict exact
delivery dates.

### 4.1 T-Shirt Sizing

T-shirt sizing is a lightweight estimation method that avoids the false
precision of hour-based or point-based estimates. It classifies work by
**relative effort** using five categories:

| Size | Meaning | Typical Scope | Typical Duration (solo) |
|------|---------|---------------|-------------------------|
| **XS** | Trivial change — clear what to do, no unknowns | Config change, copy fix, small UI tweak | < 1 hour |
| **S** | Small, well-understood task with minimal risk | Single component, single endpoint, minor feature | < 1 day |
| **M** | Moderate task — clear scope but requires some design thought | Feature with 2–3 components, API + frontend, database migration | 1–3 days |
| **L** | Large task — significant scope, may have unknowns or dependencies | Multi-component feature, integration with external service, complex business logic | 3–5 days |
| **XL** | Very large — too big for a single PR. **MUST** be decomposed into sub-issues before starting. | New module, major refactoring, multi-step migration | 1–2 weeks → decompose |

**Rules:**

- **MUST** decompose any XL issue into smaller sub-issues before
  starting work — an XL issue is a planning container, not a work item
- **SHOULD** estimate issues during triage or backlog grooming, not
  during execution
- **SHOULD** use the Size custom field in GitHub Projects (→ §3.4) to
  record estimates
- **MUST NOT** use T-shirt sizes as delivery commitments — they are
  relative indicators, not deadlines
- **SHOULD** compare actual duration to estimate after completion to
  calibrate future estimates — this is especially valuable for solo
  developers building estimation intuition

### 4.2 When NOT to Estimate

Estimation has a cost: the time spent estimating, discussing, and
maintaining estimates. For some projects, this cost exceeds the value.

**Skip estimation when:**

- The project is a personal learning exercise with no external
  stakeholders
- All items in the backlog are roughly the same size (e.g., a series
  of similar CRUD endpoints)
- The team is small (1–2 people) and works in continuous flow without
  sprints

**Estimate when:**

- A client needs delivery forecasts or milestone commitments
- The team needs to plan sprint capacity
- There are competing priorities and the team needs to compare effort
  vs impact to decide what to work on first
- Work items vary significantly in size and the team needs to balance
  the mix

### 4.3 Sprint vs Continuous Flow

Two primary cadences for organizing work:

**Sprint (time-boxed iterations)**

- Fixed-length cycles (1–2 weeks is typical)
- Team commits to a set of issues at the start of each sprint
- At the end of the sprint, incomplete work is reviewed and either
  carried over or reprioritized
- Best for: teams with external commitments, client milestones, or
  a need for regular delivery rhythm
- Use GitHub Projects **Iteration** field to define sprints with date
  ranges

**Continuous Flow (Kanban-style)**

- No fixed-length cycles — work flows continuously from Backlog
  through Done
- New items are pulled into "Ready" as capacity becomes available
- Progress is measured by throughput (items completed per week) rather
  than sprint velocity
- Best for: solo developers, maintenance-heavy projects, and teams
  without fixed delivery dates
- Use GitHub Projects **Board view** with WIP limits as the primary
  tracking mechanism

**Rules:**

- **SHOULD** default to continuous flow for solo and small freelance
  projects — the overhead of sprint ceremonies is not justified
- **SHOULD** adopt sprints when there are external milestones, client
  deliverables, or a team of 3+ that needs coordination
- **MAY** use a hybrid approach: continuous flow for daily work with
  monthly or biweekly checkpoints for planning and reflection
- **MUST NOT** adopt sprint ceremonies (standup, sprint review, sprint
  retro) for a solo project — use a simplified weekly review instead
  (→ §8)

### 4.4 Milestone Planning

Milestones group related issues under a shared delivery target — a
version release, a client demo, a go-live date, or a feature
completion.

**Use GitHub Milestones for:**

- Client deliverables with agreed dates ("MVP delivery by April 15")
- Versioned releases ("v1.0.0", "v1.1.0")
- Project phases ("Phase 1: Core features", "Phase 2: Integrations")

**Rules:**

- **SHOULD** create milestones for freelance client projects to provide
  visibility into delivery progress
- **SHOULD** set a target date on each milestone when a deadline exists
- **SHOULD** assign every issue to a milestone when milestones are in
  use — unassigned issues are invisible to milestone progress tracking
- **MAY** use milestones in combination with iterations — milestones
  for high-level targets, iterations for sprint-level planning

### 4.5 Breaking Work into Small Increments

Large tasks are risky because they delay feedback, increase merge
conflicts, and make it harder to identify what went wrong if something
breaks. Small, deliverable increments reduce all of these risks.

**Decomposition principles:**

- Each increment should be **independently deployable** — merging it
  to main should not break anything, even if the feature is incomplete
- Each increment should be **independently valuable** — it delivers
  some measurable improvement, even if small
- Each increment should produce a **single PR** under 400 lines where
  possible (→ See [10-git-workflow.md, §5.2])
- Use **feature flags** (environment variable booleans) to hide
  incomplete features from users while still merging increments to
  main (→ See [09-devops-cicd.md])

**Decomposition strategy for a large feature:**

1. **Vertical slice first:** implement a thin end-to-end path (API +
   frontend + database) for the simplest case
2. **Iterate horizontally:** add validation, error handling, edge
   cases, and additional UI states as subsequent increments
3. **Polish last:** performance optimization, animation, and visual
   refinements come after core functionality is verified

**Rules:**

- **MUST** decompose any issue estimated as XL into sub-issues before
  starting work
- **SHOULD** prefer vertical slices (thin end-to-end) over horizontal
  slices (all of API, then all of frontend) — vertical slices deliver
  feedback faster
- **SHOULD** keep each increment deliverable within 1–3 days for a
  solo developer
- **MUST NOT** work on a branch for more than a week without merging
  — long-lived branches accumulate merge conflicts and drift from main

### 4.6 Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Hour counting** | Estimating in hours creates false precision and anxiety when estimates are wrong | Use T-shirt sizes for relative effort; track actual time only if needed for invoicing |
| **Estimate = commitment** | Estimates are treated as deadlines; developers rush or cut corners to meet them | Communicate estimates as ranges, not promises. "This is M-sized, typically 1–3 days" |
| **Estimating everything** | Every tiny task gets estimated, creating overhead that exceeds the value | Only estimate when the information supports a decision (prioritization, capacity, milestone) |
| **XL as a work item** | An XL issue is assigned and worked on without decomposition | XL is a planning container — decompose into S/M sub-issues before starting |
| **Sprint cargo cult** | Sprint ceremonies (standup, review, retro) are performed as ritual without adapting to the team size | Scale ceremonies to the team: solo devs do a weekly review, not daily standup |
| **Big-bang delivery** | The entire feature is built in one branch over weeks, then merged in one massive PR | Decompose into vertical slices; merge incrementally; use feature flags |

---

## 5. Technical Debt Management

Technical debt is the **accumulated cost of shortcuts, deferred
improvements, and design compromises** in a codebase. Like financial
debt, it is not inherently bad — sometimes taking on debt is a rational
decision to ship faster. But unmanaged debt compounds: each shortcut
makes the next change harder, slower, and riskier.

### 5.1 What Technical Debt Is (and Is Not)

**Technical debt IS:**

- A conscious trade-off: "We know this is not ideal, but we are
  choosing to ship now and improve later" — documented and tracked
- An accumulated quality gap: code that was good when written but has
  not kept pace with evolving standards, patterns, or requirements
- A side effect of learning: code written by a less experienced
  developer (including past-you) that a more experienced developer
  would structure differently
- Deferred maintenance: dependency updates, migration to new APIs,
  removal of deprecated patterns

**Technical debt is NOT:**

- Bugs — a bug is incorrect behavior that should be fixed as a bug, not
  tracked as debt
- Missing features — a feature that was never built is not debt, it is
  backlog
- Intentional design decisions — choosing a simpler architecture because
  the project does not need more complexity is not debt, it is pragmatism
  (→ See [01-core-principles.md, §12])
- Bad code with no plan to fix it — if there is no intent to repay, it
  is not "debt," it is neglect

### 5.2 Tracking Technical Debt

Technical debt must be **visible** to be managed. Invisible debt
accumulates until it becomes a crisis.

**Tracking mechanisms:**

1. **Issues with `type:tech-debt` classification** — every piece of
   known debt has a corresponding issue in the backlog
2. **TODO markers in code with issue references** — `TODO(#123): Refactor
   this to use service layer` links inline markers to trackable issues
   (→ See [01-core-principles.md, §8.6])
3. **Dedicated board filter or view** — create a saved view in GitHub
   Projects filtered to `type:tech-debt` to see all debt in one place
4. **Periodic audit** — review TODOs, linter warnings, and test coverage
   gaps during the weekly triage (→ §3.5) or dedicated tech debt review

**Rules:**

- **MUST** create a tracked issue for every significant piece of known
  technical debt — if it is worth mentioning in a comment, it is worth
  tracking in an issue
- **MUST** include TODO markers in code only with an issue reference
  (→ See [01-core-principles.md, §8.6]) — `TODO: fix this` without a
  ticket is invisible to project management
- **SHOULD** review and prioritize tech debt during the weekly triage
- **SHOULD** create a saved view in GitHub Projects filtered by
  `type:tech-debt` for visibility

### 5.3 The Tech Debt Budget

Technical debt cannot be eliminated through a single "cleanup sprint" —
it accumulates continuously and must be addressed continuously.

The **tech debt budget** is a commitment to allocate a percentage of
development capacity to debt reduction in every work cycle:

| Project Stage | Recommended Budget | Rationale |
|---------------|--------------------|-----------|
| **Greenfield / early MVP** | 5–10% | Debt is low; focus on feature delivery |
| **Growing product** | 15–20% | Debt accumulates as features grow; invest before it compounds |
| **Mature product** | 20–30% | Significant codebase with accumulated debt; sustained investment prevents slowdown |

**In practice for a solo developer using continuous flow:**

- For every 4–5 feature/bug issues completed, address 1 tech debt issue
- Choose tech debt issues that are adjacent to current feature work —
  "I'm already in this module, let me clean it up" is more efficient
  than dedicated cleanup sessions
- Apply the Boy Scout Rule (→ See [01-core-principles.md, §13.4]) as the
  minimum continuous investment

**Rules:**

- **SHOULD** allocate a consistent percentage of capacity to tech debt
  reduction — not as a one-time sprint, but as a continuous practice
- **SHOULD** prefer addressing tech debt adjacent to current feature
  work — the context is already loaded, and the improvement is
  immediately relevant
- **MUST NOT** defer all tech debt to "later" — "later" never arrives,
  and the compounding cost eventually paralyzes the codebase
- **MUST NOT** spend 100% of time on tech debt unless the codebase is
  in crisis — features still need to ship

### 5.4 Prioritizing Technical Debt

Not all debt is equal. Some debt causes daily pain; some is theoretical
risk that may never materialize. Prioritize debt using an **impact ×
effort matrix:**

```text
                High Impact
                    │
     ┌──────────────┼──────────────┐
     │              │              │
     │   Quick Wins │  Strategic   │
     │  (do first)  │  (plan as    │
     │              │   project)   │
     │              │              │
Low ─┼──────────────┼──────────────┼─ High
Effort              │              Effort
     │              │              │
     │   Ignore     │  Defer       │
     │  (not worth  │  (track but  │
     │   the cost)  │   wait)      │
     │              │              │
     └──────────────┼──────────────┘
                    │
                Low Impact
```

**Impact indicators:**

- How often do developers encounter this debt? (daily vs rarely)
- Does it cause bugs, slow down development, or block new features?
- Does it affect security, performance, or user experience?
- Will it get worse over time, or is it stable?

**Effort indicators:**

- How many files, modules, or systems are affected?
- Does it require a migration, or is it a localized refactoring?
- Are tests in place, or do they need to be written first?
- Can it be done incrementally, or is it all-or-nothing?

**Rules:**

- **SHOULD** prioritize Quick Wins (high impact, low effort) first —
  they deliver the most value for the least cost
- **SHOULD** plan Strategic items (high impact, high effort) as
  dedicated projects with sub-issues and milestones (→ §6)
- **MAY** defer low-impact, high-effort items indefinitely — document
  the decision and revisit periodically
- **SHOULD** close or archive Ignore items (low impact, low effort) —
  the tracking cost exceeds the improvement value

### 5.5 Justifying Tech Debt Investment to Stakeholders

Clients and non-technical stakeholders often perceive tech debt work as
"not delivering features." To maintain trust and secure time for debt
reduction, communicate in terms of **business impact**, not technical
details.

**Effective framing:**

| Instead of... | Say... |
|---------------|--------|
| "We need to refactor the auth module" | "We need to improve the login system reliability — right now, 3% of login attempts fail silently, which means we lose users" |
| "The database queries are inefficient" | "Some pages take 5+ seconds to load, which causes users to abandon the page. We can cut this to under 1 second" |
| "We have technical debt" | "We have accumulated shortcuts that are slowing us down. Each new feature now takes 30% longer than it should because of workarounds. Investing 2 days now saves 1 day on each of the next 5 features" |
| "We need to upgrade dependencies" | "Some of our tools have known security vulnerabilities. We need to update them to keep user data safe" |

**Rules:**

- **SHOULD** frame tech debt investment in terms of business outcomes —
  speed, reliability, security, cost — not technical abstractions
- **SHOULD** quantify the impact when possible — "saves X hours per
  feature", "reduces error rate by Y%", "eliminates Z security
  vulnerability"
- **SHOULD** present tech debt work as part of the regular delivery
  cycle, not as a separate "maintenance mode" that pauses feature work
- **MUST NOT** surprise stakeholders with large tech debt initiatives —
  build trust through consistent, small investments and transparent
  communication

### 5.6 Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Invisible debt** | Tech debt exists only in developers' heads — never tracked, never prioritized | Create issues for every known debt item; use TODO markers with issue references |
| **"Refactoring sprint"** | All tech debt is deferred to a dedicated sprint that gets deprioritized indefinitely | Allocate a continuous budget (15–20%) instead of batching into large sprints |
| **Gold plating** | Disguising feature work as tech debt to avoid prioritization ("we need to refactor this module" actually means "I want to redesign it my way") | Tech debt work should not change user-visible behavior — if it does, it is a feature |
| **Debt denial** | "We don't have tech debt" — the team does not acknowledge shortcuts or deferred improvements | Run a periodic audit: review TODOs, linter warnings, test coverage gaps, and slow CI |
| **Kitchen sink PR** | A PR that mixes tech debt cleanup with feature work, making review difficult and rollback risky | Keep tech debt PRs separate from feature PRs (→ See [10-git-workflow.md, §5.1]) |

---

## 6. Large-Scale Refactoring & Migration

When a refactoring effort exceeds a single PR or spans multiple days, it
stops being a code-level activity and becomes a **project**. This section
covers how to plan, scope, execute, and track large-scale refactoring and
migration efforts.

This section fulfills the references made by
→ See [01-core-principles.md, §13.2] ("SHOULD NOT pursue large-scale
refactoring without planning"), §13.5 ("SHOULD prefer the Strangler Fig
pattern"), and §13.6 ("Prerequisites for Safe Refactoring").

### 6.1 When Refactoring Becomes a Project

A refactoring effort **becomes a project** when any of the following are
true:

- It affects more than 3 files or 2 modules
- It requires more than one PR to complete safely
- It takes more than 2 days of focused work
- It involves changing interfaces that other code depends on
- It requires coordination with other work (feature flags, data
  migration, API versioning)
- It touches code that is critical to the system's core functionality

When these thresholds are crossed, the refactoring **MUST** be planned
and tracked as a project — not executed ad-hoc in a single branch.

**Rules:**

- **MUST** create a parent issue for any refactoring effort that
  exceeds the thresholds above
- **MUST** decompose the effort into sub-issues, each representing an
  independently mergeable step
- **MUST** create an ADR before starting the refactoring
  (→ See [01-core-principles.md, §9]) — documenting why the refactoring
  is necessary, what approach was chosen, and what alternatives were
  considered
- **SHOULD** define success criteria upfront — what does "done" look
  like? Reduced complexity score, faster test execution, eliminated
  warnings, improved performance metrics
- **MUST NOT** start a large refactoring without test coverage for the
  code being changed (→ See [01-core-principles.md, §13.6])

### 6.2 Scoping a Large Refactor

Scoping is the most critical step. A poorly scoped refactoring either
grows uncontrollably or delivers incomplete results.

**Scoping process:**

1. **Define the boundary:** what code is IN scope and what is OUT of
   scope? Be explicit — "refactor the auth module" is too vague.
   "Refactor `src/services/auth/` to separate token management from
   user session handling" is specific.

2. **Map dependencies:** what other code depends on the code being
   refactored? Use the IDE's "Find References" to identify all call
   sites. Every call site is a potential breaking point.

3. **Define milestones:** break the work into phases that each deliver
   a stable, deployable state. Each milestone should leave the system
   fully functional.

4. **Estimate and sequence:** assign T-shirt sizes to each sub-issue
   and define the execution order based on dependencies.

5. **Define success criteria:** measurable outcomes that prove the
   refactoring achieved its goals.

**Example scoping for "Refactor auth module to use service layer":**

```text
Parent issue: "Refactor auth module to use service layer"
├── Sub-issue 1 (S): Write characterization tests for current auth behavior
├── Sub-issue 2 (M): Extract AuthService interface from existing code
├── Sub-issue 3 (M): Implement AuthService with extracted business logic
├── Sub-issue 4 (S): Migrate route handlers to use AuthService
├── Sub-issue 5 (S): Remove old direct-access code, clean up imports
└── Sub-issue 6 (S): Measure and document improvements (complexity, test coverage)

Success criteria:
- All existing auth tests pass without modification
- Cyclomatic complexity of auth-related functions reduced by ≥30%
- No direct database access from route handlers
- AuthService covered by unit tests at ≥80%
```

### 6.3 Migration Strategies

Three proven strategies for replacing or restructuring system components
incrementally. The choice depends on where the change happens and how
the old and new implementations coexist.

#### 6.3.1 Strangler Fig Pattern

**What it is:** Incrementally replace a legacy system by building new
functionality alongside it, gradually routing traffic from old to new
until the old system can be decommissioned.

**Named by Martin Fowler** after the strangler fig vine, which grows
alongside a host tree and eventually replaces it.

**How it works:**

```text
Phase 1: Introduce proxy/façade
  Client → See [Proxy] → Legacy System (100% of traffic)

Phase 2: Build new component, route partial traffic
  Client → See [Proxy] ──→ Legacy System (partial traffic)
                   └──→ New System (partial traffic)

Phase 3: Migrate remaining traffic
  Client → See [Proxy] → New System (100% of traffic)

Phase 4: Decommission
  Client → New System (proxy removed)
  Legacy System (decommissioned)
```

**When to use:**

- Replacing an entire module or subsystem (e.g., migrating from a
  custom auth system to Supabase Auth)
- The replacement happens at the system boundary — API routes, service
  interfaces, or data access layer
- Both old and new implementations can coexist during the migration
- You need to maintain business continuity throughout the migration

**Practical example for the standard stack:**

Migrating from direct Supabase Client queries to a service layer with
Prisma:

1. **Proxy:** introduce a repository interface that initially delegates
   to the existing Supabase Client code
2. **New implementation:** build Prisma-based repository behind the
   same interface
3. **Route:** switch one entity (e.g., `users`) to Prisma while others
   remain on Supabase Client
4. **Iterate:** migrate remaining entities one by one
5. **Decommission:** remove Supabase Client data access code once all
   entities are migrated

**Rules:**

- **MUST** define the proxy/façade layer before building the new
  implementation — this ensures both can coexist
- **MUST** keep the proxy transparent to consumers — callers should not
  know whether they are hitting old or new implementation
- **SHOULD** migrate one component at a time, validating each before
  proceeding
- **MUST** have a rollback plan for each migration step — if the new
  implementation fails, the proxy should be able to route back to the
  old one
- **SHOULD** use feature flags to control routing between old and new
  implementations

#### 6.3.2 Branch by Abstraction

**What it is:** Make a large-scale internal change by introducing an
abstraction layer that allows old and new implementations to coexist
within the same codebase, swapping them gradually.

**Described by Martin Fowler** as a technique for large-scale changes
that allows continuous delivery while the change is in progress.

**How it works:**

```text
Step 1: Direct dependency (current state)
  ComponentA ──→ OldImplementation
  ComponentB ──→ OldImplementation

Step 2: Introduce abstraction layer
  ComponentA ──→ See [Abstraction] ──→ OldImplementation
  ComponentB ──→ See [Abstraction] ──→ OldImplementation

Step 3: Build new implementation behind abstraction
  ComponentA ──→ See [Abstraction] ──→ OldImplementation
  ComponentB ──→ See [Abstraction] ──→ NewImplementation (migrated)

Step 4: Complete migration
  ComponentA ──→ See [Abstraction] ──→ NewImplementation
  ComponentB ──→ See [Abstraction] ──→ NewImplementation

Step 5: Remove abstraction (optional)
  ComponentA ──→ NewImplementation
  ComponentB ──→ NewImplementation
```

**When to use:**

- Replacing an internal dependency (library, framework, ORM, or
  internal module) without changing external behavior
- The change is deep inside the codebase, not at the system boundary
- Multiple consumers depend on the code being replaced
- You want to use trunk-based development and continuous integration
  during the migration

**Difference from Strangler Fig:** Strangler Fig works at the **edge**
of the system (API boundary, routing layer). Branch by Abstraction works
**inside** the system at any dependency point.

**Practical example for the standard stack:**

Replacing a validation library (e.g., migrating from Joi to Zod):

1. **Abstraction:** define a `ValidationSchema<T>` interface that
   captures the validation contract (parse, safeParse, type inference)
2. **Adapt old:** wrap existing Joi schemas behind the interface
3. **Build new:** implement Zod schemas behind the same interface
4. **Migrate consumers:** switch one API route at a time from the Joi
   adapter to the Zod adapter
5. **Remove old:** once all routes use Zod, remove the Joi adapter and
   the abstraction layer

**Rules:**

- **MUST** define the abstraction layer interface before building the
  new implementation
- **MUST** ensure the abstraction does not leak implementation details
  — consumers should depend only on the interface
- **SHOULD** write tests against the abstraction interface, not the
  implementations — the same test suite should pass for both
- **SHOULD** use feature flags or configuration to control which
  implementation is active, enabling gradual rollout and easy rollback
- **MUST NOT** leave the abstraction layer in place permanently unless
  it provides ongoing value — abstractions have a maintenance cost

#### 6.3.3 Parallel Run

**What it is:** Run the old and new implementations simultaneously,
comparing their outputs to verify that the new implementation produces
equivalent results before cutting over.

**When to use:**

- The correctness of the new implementation is critical and hard to
  verify through unit tests alone (e.g., financial calculations,
  complex business rules, data transformations)
- The cost of a bug in the new implementation is very high
- The system produces deterministic outputs that can be compared

**How it works:**

1. Route requests through both old and new implementations
2. Use the old implementation's output as the "source of truth"
3. Compare outputs: log discrepancies but do not expose the new
   implementation's output to users yet
4. Investigate and fix discrepancies
5. Once discrepancy rate is acceptable (zero for critical paths),
   switch to the new implementation as the primary
6. Keep the old implementation as a shadow for a monitoring period
7. Decommission the old implementation

**Rules:**

- **MUST** use the old implementation as the source of truth during
  the parallel run — users always see the old implementation's output
- **MUST** log all discrepancies with enough context to investigate
  (input, old output, new output, timestamp)
- **SHOULD** define an acceptable discrepancy threshold before starting
  — for critical paths (payments, auth), the threshold is zero
- **MUST** not extend the parallel run indefinitely — define a
  time-boxed evaluation period (e.g., 1 week, 1 sprint)

### 6.4 Tracking Progress

Large refactoring efforts need explicit progress tracking to prevent
them from becoming endless background work.

**Tracking mechanisms:**

- **Parent issue with sub-issues:** the parent issue shows overall
  progress via sub-issue completion. Use Hierarchy View in GitHub
  Projects to visualize the full tree.
- **Milestone:** assign all refactoring sub-issues to a dedicated
  milestone for progress tracking and completion percentage.
- **Metrics before/after:** capture relevant metrics before starting
  (→ See [01-core-principles.md, §13.6]) and compare after each milestone.

**Rules:**

- **MUST** track refactoring progress through sub-issue completion on
  the parent issue — not through verbal updates or separate documents
- **SHOULD** review refactoring progress during the weekly triage
  (→ §3.5) — is the effort on track? Are there blockers?
- **SHOULD** document improvements in each sub-issue's PR description
  — "Reduced cyclomatic complexity from 42 to 18 in auth module"
- **MUST** close the parent issue only when all sub-issues are
  completed and success criteria are met

### 6.5 Risk Management

Large refactoring is inherently risky because it changes working code.
Risk management ensures that failures are recoverable.

**Risk mitigation strategies:**

| Strategy | Implementation | When to Use |
|----------|----------------|-------------|
| **Rollback plan** | Each sub-issue PR can be reverted independently | Always — every refactoring step must be revertible |
| **Feature flags** | Toggle between old and new implementation via environment variable | When both implementations can coexist (Strangler Fig, Branch by Abstraction) |
| **Canary deployment** | Deploy the change to a subset of users/environments before full rollout | Production systems with significant user base |
| **Characterization tests** | Tests that capture current behavior as a baseline, regardless of correctness (→ See [01-core-principles.md, §13.6]) | Refactoring untested legacy code |
| **Monitoring** | Watch error rates, latency, and key business metrics after each migration step | Always — metrics are the first signal that something is wrong |

**Rules:**

- **MUST** have a rollback plan for every migration step — if
  something breaks, how do you get back to the previous working state?
- **MUST** keep each refactoring step small enough that reverting a
  single PR restores the system to a working state
- **SHOULD** monitor error rates and performance after each migration
  step — automated alerts (→ See [08-observability.md]) should catch
  regressions
- **MUST NOT** migrate all components at once ("big bang") — the whole
  point of incremental migration is to limit blast radius

### 6.6 Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Big bang rewrite** | Replace the entire system at once — high risk, long timeline, zero value until complete | Use Strangler Fig or Branch by Abstraction for incremental migration |
| **Endless refactoring** | Refactoring that never finishes because scope creeps or success criteria are undefined | Define success criteria and milestones upfront; time-box the effort |
| **Refactoring without tests** | Changing code structure without tests to verify behavior preservation | Write characterization tests before refactoring (→ See [01-core-principles.md, §13.6]) |
| **Invisible refactoring** | Large refactoring happens in a developer's branch with no issues, no tracking, no visibility | Create parent issue with sub-issues; track on the board like any other project |
| **Premature abstraction** | Introducing abstraction layers "just in case" before there is a concrete need to swap implementations | Introduce abstractions only when you have a concrete second implementation to swap to |
| **Forgetting to remove the old** | New implementation is active but old code remains in the codebase, creating confusion | Include a "decommission old implementation" sub-issue in every migration plan |

---

## 7. Checklists

Checklists are the bridge between standards and execution. They
transform complex, multi-domain requirements into actionable
verification steps that can be completed systematically.

This section provides consolidated checklists that reference the
detailed, domain-specific checklists defined in other documents. The
goal is to provide a single entry point for each project lifecycle
event, not to duplicate the authoritative source.

### 7.1 Pre-Launch Checklist (Consolidated)

Use this checklist before the first production deployment of any new
application. It consolidates requirements from security, devops,
testing, and domain-specific standards into a single verification flow.

**For the full domain-specific checklists, see:**
- Security: → See [07-security-standards.md, §17] (Level 1/2/3)
- DevOps: → See [09-devops-cicd.md, §9.2] (Pre-Deployment)
- Testing: → See [06-testing-strategy.md, §8] (Quality Gates)
- Frontend: → See [05-frontend-standards.md] (a11y, responsive, SEO)

**Consolidated pre-launch verification:**

```text
□ SECURITY
  □ Security checklist Level 3 completed (→ 07 §17)
  □ HTTPS enforced, HSTS enabled
  □ Security headers audit passed (securityheaders.com grade A+)
  □ RLS enabled and tested on every table (if Supabase)
  □ No secrets in codebase (gitleaks clean)
  □ RGPD compliance verified (privacy policy, cookie consent, data rights)

□ QUALITY
  □ All CI quality gates pass (lint, typecheck, test, build)
  □ E2E tests cover critical user flows
  □ DoD checklist satisfied for all shipped features (→ 01 §11)
  □ Cross-browser and mobile verified
  □ Accessibility audit completed (→ 05)

□ INFRASTRUCTURE
  □ DevOps checklist completed (→ 09 §9)
  □ Environment variables validated and correct for production
  □ Health check endpoint returns 200
  □ Monitoring configured (Sentry + UptimeRobot) (→ 08)
  □ Database backups verified (restore tested at least once)
  □ Rollback plan confirmed

□ DOCUMENTATION
  □ README up to date (setup, env vars, architecture overview)
  □ ADRs documented for significant decisions (→ 01 §9)
  □ Runbook available (deploy, rollback, restart procedures)
  □ API documentation available (if public API)

□ CLIENT / STAKEHOLDER
  □ Acceptance criteria verified by stakeholder (if freelance)
  □ Client handoff documentation prepared (if applicable, → §7.3)
```

### 7.2 New Project Kickoff Checklist

Use this checklist when starting a new project to ensure all
foundational elements are in place before writing feature code.

```text
□ REPOSITORY
  □ Repository created with appropriate visibility (public/private)
  □ Branch protection configured on main (→ 10 §2)
  □ .gitignore includes .env, node_modules, .next, dist
  □ .nvmrc or .node-version pins Node.js version
  □ Conventional Commits enforced (Husky + commitlint) (→ 10 §3)
  □ gitleaks pre-commit hook installed (→ 10 §4)

□ ENVIRONMENT
  □ .env.example committed with all required variables
  □ Environment validation configured (@t3-oss/env-nextjs with Zod)
  □ Environment variables set in deployment platform (Vercel)

□ CI/CD
  □ Quality gates pipeline configured (→ 06 §8, 09 §9.1)
  □ Deployment connected (Vercel auto-deploy from main)
  □ Preview deployments enabled for PRs (if Vercel)

□ OBSERVABILITY
  □ Sentry project created and SDK configured (→ 08 §3)
  □ Health check endpoint implemented (/api/health) (→ 08 §5.1)
  □ UptimeRobot monitor on production URL (→ 08 §5.2)

□ PROJECT MANAGEMENT
  □ GitHub Project created with standard columns (→ §3.2)
  □ Issue templates created (.github/ISSUE_TEMPLATE/) (→ §2.5)
  □ PR template created (.github/pull_request_template.md)
    (→ 10 §5.3)
  □ Labels configured (→ §2.4)
  □ Auto-add workflow configured to add issues to project (→ §3.6)

□ DOCUMENTATION
  □ README.md with: project description, setup instructions,
    env vars, architecture notes
  □ ADR directory created (docs/adr/) (→ 01 §9.5)
```

### 7.3 Client Handoff / Delivery Checklist

Use this checklist when delivering a project or milestone to a
freelance client. The goal is to ensure the client (or a future
developer) can understand, run, and maintain the project independently.

```text
□ CODE QUALITY
  □ All CI quality gates pass (lint, typecheck, test, build)
  □ No known critical bugs or regressions
  □ No TODO markers without issue references
  □ Dead code and commented-out code removed

□ DOCUMENTATION
  □ README.md comprehensive:
    □ Project overview and purpose
    □ Tech stack and architecture summary
    □ Setup instructions (clone, install, configure, run)
    □ Environment variables documented (each var explained)
    □ Deployment instructions
    □ Known limitations or future improvements
  □ ADRs document all significant decisions
  □ API documentation available (if applicable)

□ ACCESS & CREDENTIALS
  □ Client has access to: repository, deployment platform,
    database dashboard, monitoring tools
  □ All credentials transferred securely (not via email/chat)
  □ Service accounts created for the client (not shared personal
    accounts)

□ DEPLOYMENT
  □ Production environment operational and verified
  □ Client understands the deployment process (or it is documented)
  □ Backup and restore procedure documented and tested
  □ Domain and DNS configured and documented

□ PROJECT STATUS
  □ All milestone issues closed or documented as deferred
  □ Open issues triaged: each is either "will not fix" (closed with
    reason) or documented as future work
  □ Project board reflects final state accurately
```

### 7.4 Post-Incident Review Checklist

Use this checklist after a production incident to capture lessons
learned and prevent recurrence. The full incident report template is
in → `templates/incident-report.md`.

```text
□ IMMEDIATE (within 24 hours of resolution)
  □ Incident timeline documented (detection → diagnosis →
    mitigation → resolution)
  □ Root cause identified (or marked as "under investigation")
  □ Impact assessed (users affected, duration, data impact)
  □ Temporary mitigations documented

□ REVIEW (within 1 week of resolution)
  □ Incident report completed using template
    (→ templates/incident-report.md)
  □ Blameless post-mortem conducted (focus on systems and
    processes, not individuals)
  □ Action items created as tracked issues with owners and
    deadlines
  □ Detection gap identified: why was this not caught earlier?
    (tests, monitoring, review)

□ PREVENTION (within 2 weeks of resolution)
  □ Action items in progress or completed
  □ Monitoring/alerting improved to detect similar incidents
    earlier
  □ Tests added to prevent regression
  □ Engineering standards updated if the incident exposed a gap
    (→ 00-INDEX §Contributing & Evolution)
```

### 7.5 Checklist Usage Rules

- **MUST** complete the Pre-Launch Checklist (§7.1) before the first
  production deployment of any new application
- **MUST** complete the New Project Kickoff Checklist (§7.2) before
  writing feature code on any new project
- **SHOULD** complete the Client Handoff Checklist (§7.3) for every
  freelance milestone delivery
- **MUST** complete the Post-Incident Review (§7.4) after any
  production incident — "we fixed it" is not sufficient without a
  review
- **SHOULD** store completed checklists with the relevant release or
  milestone (as a PR comment, issue comment, or release note)
- **MUST NOT** skip checklist items without documented justification —
  "we're in a hurry" is never a valid reason

### 7.6 Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Checkbox theater** | Checklists exist but items are checked off without actual verification | Make checklist completion a team or self-review step, not a formality |
| **Checklist sprawl** | Dozens of checklists, each with 50+ items — nobody reads them | Consolidate into 4–5 lifecycle checklists; reference domain documents for details |
| **No post-incident review** | Incidents are fixed and forgotten — the same problems recur | Make post-incident review mandatory; create tracked action items |
| **Checklist as documentation** | Checklist tries to explain HOW to do each item instead of WHAT to verify | Keep checklists as verification lists; link to the authoritative document for the how |

---

## 8. Retrospectives & Continuous Improvement

A retrospective is a structured reflection on how work was done, with
the goal of identifying improvements. Without retrospectives, mistakes
are repeated, successful patterns go unrecognized, and engineering
standards stagnate.

### 8.1 The Retrospective Framework

The simplest effective retrospective framework has three questions:

1. **What went well?** — Practices, decisions, or patterns that should
   be repeated and reinforced.
2. **What could improve?** — Friction points, mistakes, or inefficiencies
   that should be addressed.
3. **Action items** — Specific, assignable, trackable improvements that
   come out of the reflection. Without action items, a retrospective is
   just a discussion.

**Rules for effective retrospectives:**

- **MUST** produce at least one concrete action item per retrospective
  — a retrospective without action items is a venting session, not an
  improvement process
- **MUST** create tracked issues for action items — they enter the
  backlog and are prioritized like any other work
- **SHOULD** review action items from the previous retrospective before
  starting a new one — were they completed? Did they have the expected
  effect?
- **MUST** keep retrospectives blameless — focus on systems, processes,
  and patterns, not on individuals

### 8.2 Solo Retrospectives

Solo developers do not need a formal ceremony, but they do need a
regular reflection habit. A weekly review (15–30 minutes) is the
recommended cadence.

**Weekly review template:**

```markdown
## Week of [date]

### What I completed
- [list completed issues/PRs with links]

### What went well
- [practices or decisions that worked]

### What slowed me down
- [friction, confusion, rework, or blocked time]

### Action items
- [ ] [specific improvement with issue link if applicable]
```

**Rules:**

- **SHOULD** conduct a weekly review on the last working day of each
  week — consistency matters more than duration
- **SHOULD** document the review in a consistent location (a recurring
  issue, a personal journal, or a dedicated project document)
- **SHOULD** use the review to update the project board — close stale
  issues, reprioritize the backlog, and plan the next week
- **MAY** combine the weekly review with the weekly board triage
  (→ §3.5) for efficiency

### 8.3 When to Update Engineering Standards

Retrospectives are the primary mechanism for evolving these engineering
standards. A standard should be updated when:

- **A post-mortem or incident exposes a gap** — a checklist item was
  missing, a practice was not covered, or a rule was ambiguous
- **A practice consistently requires justification to skip** — if the
  team regularly deviates from a SHOULD rule with good reason, the rule
  may need revision
- **A new technology or pattern is adopted** — document it in the
  Technology Radar (→ See [02-technology-radar.md]) first, then update
  domain documents as needed
- **A retrospective identifies a recurring friction point** — if the
  same problem appears in multiple retrospectives, it may need a
  standard to prevent it

**Rules:**

- **SHOULD** create an issue tagged `domain:docs` or `type:task` for
  any proposed standards update identified in a retrospective
- **MUST** follow the update process defined in
  → See [00-INDEX.md, §Contributing & Evolution] — propose, ADR if MUST/
  SHOULD change, update document, update cross-references
- **MUST NOT** update standards silently — changes to MUST or SHOULD
  rules require an ADR and should be communicated to anyone affected

### 8.4 Feeding Lessons Learned Back

The feedback loop between execution and standards is what makes the
engineering standards a **living system** rather than a static document.

```text
Execute work → Encounter friction or success → Reflect (retrospective)
     ↑                                                    │
     │                                                    ▼
     │                                          Identify pattern
     │                                                    │
     │                                                    ▼
     │                                          Create action item
     │                                                    │
     │                               ┌────────────────────┴──────────┐
     │                               ▼                               ▼
     │                      One-time fix                    Standards update
     │                    (issue/PR)                    (→ 00-INDEX process)
     │                               │                               │
     └───────────────────────────────┴───────────────────────────────┘
```

### 8.5 Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **No retrospectives** | Mistakes repeat, successful patterns go unrecognized, standards stagnate | Schedule a recurring weekly review; consistency matters more than formality |
| **Retrospective without action items** | Discussion happens but nothing changes — same issues appear month after month | Require at least one tracked action item per retrospective |
| **Blame game** | Retrospective focuses on who made a mistake instead of what systemic issue allowed it | Enforce blameless framing: "the system allowed X to happen" not "person Y caused X" |
| **Action items without tracking** | Action items are discussed but never created as issues — they are forgotten by the next retrospective | Create issues for every action item; review completion in the next retrospective |
| **Standards as stone tablets** | Engineering standards are written once and never updated — they drift from actual practice | Use retrospectives as the feedback mechanism; update standards when patterns emerge |

---

## 9. Project Management by Project Stage

Not every project needs the same management overhead. A personal
learning project should not have sprint ceremonies, and a freelance
client project should not lack milestone tracking. This section provides
a progressive guide for scaling project management practices as projects
grow — consistent with the "By Project Stage" sections in
→ See [09-devops-cicd.md, §8] and → See [10-git-workflow.md, §9].

### 9.1 Personal Project / Learning

**Context:** Solo developer, no external consumers, primary goal is
learning and experimentation.

| Practice | Recommendation |
|----------|----------------|
| **Issues** | SHOULD create issues for significant features (builds the habit) |
| **Issue templates** | MAY skip — overhead exceeds value |
| **Sub-issues** | MAY use for decomposing larger learning goals |
| **Board** | SHOULD maintain a simple board (Backlog → In Progress → Done — 3 columns) |
| **Views** | Board view only |
| **Estimation** | MAY skip — learning is exploratory, not deadline-driven |
| **Sprints** | MUST NOT use — continuous flow is the natural fit |
| **Milestones** | MAY skip |
| **Tech debt tracking** | MAY skip formal tracking — apply Boy Scout Rule (→ 01 §13.4) |
| **Checklists** | SHOULD use kickoff checklist (§7.2) as a quick setup guide |
| **Retrospective** | SHOULD do a brief reflection when the project ends or reaches a natural pause |

**Why still use issues and a board:** Building the habit of issue-first
workflow and board usage in personal projects costs almost nothing and
pays dividends when working on freelance or team projects. The muscle
memory transfers.

### 9.2 Freelance Client Project

**Context:** Professional delivery to a client who may have other
developers or stakeholders. The code may be handed off, maintained by
others, or audited.

| Practice | Recommendation |
|----------|----------------|
| **Issues** | MUST create issues for all work — features, bugs, and tasks |
| **Issue templates** | SHOULD configure feature and bug templates (§2.5) |
| **Sub-issues** | SHOULD use for decomposing features into deliverable pieces |
| **Board** | MUST maintain a full board with 5 columns (§3.2) |
| **Views** | SHOULD maintain Board + Table views; MAY add Roadmap for client milestones |
| **Estimation** | SHOULD estimate using T-shirt sizing (§4.1) — helps forecast delivery |
| **Sprints** | MAY use iterations for milestone-based planning; continuous flow is acceptable |
| **Milestones** | MUST use milestones for client deliverables with agreed dates |
| **Tech debt tracking** | SHOULD track tech debt with typed issues and periodic review |
| **Checklists** | MUST complete kickoff (§7.2) and pre-launch (§7.1); SHOULD complete handoff (§7.3) |
| **Retrospective** | SHOULD do weekly review; MUST do a project retrospective at completion |

**Why the increased rigor:** Client projects carry reputational and
financial responsibility. A missed deliverable, a forgotten requirement,
or a chaotic handoff directly impacts professional credibility. The
overhead of proper tracking is negligible compared to the risk of
appearing disorganized.

### 9.3 Team Project

**Context:** Multiple developers, shared codebase, continuous delivery,
potentially public-facing.

| Practice | Recommendation |
|----------|----------------|
| **Issues** | MUST create issues for all work; MUST use issue-first workflow |
| **Issue templates** | MUST configure templates for all standard types (§2.5) |
| **Sub-issues** | MUST use for decomposing epics into sprint-sized work items |
| **Board** | MUST maintain a full board with 5 columns (§3.2); MUST enforce WIP limits |
| **Views** | MUST maintain Board + Table + Hierarchy views; SHOULD add Roadmap |
| **Estimation** | MUST estimate using T-shirt sizing (§4.1); SHOULD track actual vs estimated |
| **Sprints** | SHOULD use iterations (1–2 week sprints); MAY use continuous flow if team agrees |
| **Milestones** | SHOULD use milestones for release planning |
| **Tech debt tracking** | MUST track tech debt; MUST allocate 15–20% budget (§5.3) |
| **Checklists** | MUST complete all relevant checklists (§7) |
| **Retrospective** | MUST conduct retrospective at end of each sprint or biweekly |

### 9.4 Decision Guide

```text
Who is this project for?
├── Just me (learning, experimentation)
│   └── §9.1 Personal workflow
│       Key practices: issues (habit), simple board, Boy Scout Rule
│
├── A client (freelance delivery)
│   └── §9.2 Freelance workflow
│       Key practices: full board, milestones, estimation, handoff
│       checklist, weekly review
│
└── A team (shared codebase, multiple developers)
    └── §9.3 Team workflow
        Key practices: full board + hierarchy, sprints/iterations,
        estimation, tech debt budget, sprint retrospectives

Scaling trigger: move to the next stage when...
├── Personal → Freelance: someone else will use, review, or pay for
│   this code
├── Freelance → Team: a second developer joins the project
└── At any stage: if the current level of tracking cannot answer
    the four visibility questions (§1.1), add more structure
```

**Rules:**

- **MUST** implement the practices marked as MUST for the current
  project stage — these are the minimum for that context
- **SHOULD** scale up when the project moves to a higher stage, not
  retroactively — adding tracking after months of untracked work is
  painful
- **MUST NOT** skip stages — do not apply team-level ceremony to a
  personal project, and do not use personal-level tracking for a
  client project
- **SHOULD** err on the side of slightly more tracking than necessary
  — the cost of a lightweight board is far less than the cost of lost
  context

---

> → See [01-core-principles.md] for the foundational principles that
> inform every standard in this document.
> → See [09-devops-cicd.md, §8] for the DevOps equivalent of this
> scaling guide.
> → See [10-git-workflow.md, §9] for the Git workflow equivalent of
> this scaling guide.

# 🔀 Git Workflow & Collaboration Standards

> **Scope:** Defines how to use Git consistently, professionally, and scalably across all projects — branching, committing, reviewing, merging, and releasing.
>
> **Purpose:** This is the collaboration layer of the engineering standards. While other documents define *what* to build and *how* to build it, this document defines *how to collaborate on building it*. A clean Git workflow produces a readable history, predictable branches, effective pull requests, and controlled releases.
>
> **Audience:** Any developer working on projects governed by these standards — solo or in a team.
>
> **Keywords:**
> - **MUST** = required (PR should be blocked if violated)
> - **SHOULD** = strongly recommended (requires justification to skip)
> - **MAY** = optional (case-by-case)

---

## 0. How to Use This Document

This document is the single reference for Git conventions. It intentionally does not duplicate tool configuration details or quality gate definitions that live in other documents — instead, it references them and focuses on the *workflow* layer: how commits, branches, PRs, reviews, merges, and releases fit together.

### Boundary Definitions

This document works in concert with several other standards. The following table clarifies where this document's scope ends and other documents begin:

| This document says... | The authoritative source is... |
|-----------------------|--------------------------------|
| "Use Conventional Commits" | → See [02-technology-radar.md, §4.12] defines commitlint as Adopt and baseline config |
| "Configure pre-commit hooks" | → See [02-technology-radar.md, §4.12] defines Husky and lint-staged as Adopt |
| "Require PR review before merge" | → See [06-testing-strategy.md, §8.4] defines merge blocking rules |
| "All quality gates must pass before merge" | → See [06-testing-strategy.md, §8] defines quality gates |
| "Run gitleaks in pre-commit" | → See [07-security-standards.md, §7] defines leak detection and response |
| "Commit lock files" | → See [01-core-principles.md, §10] and [07-security-standards.md, §11] define dependency management |
| "Keep refactoring commits separate" | → See [01-core-principles.md, §13.6] defines version control discipline for refactoring |
| "PR description must explain what and why" | → See [01-core-principles.md, §11.2] defines the Definition of Done (Code Review section) |
| "Use PR template" | → See [01-core-principles.md, §11.4] defines how to embed DoD in PR templates |
| "Create ADR for significant decisions" | → See [01-core-principles.md, §9] defines ADR structure, triggers, and quality rules |
| "Deploy triggers on merge to main" | → See [09-devops-cicd.md, §4.2] defines the deploy pipeline |
| "Use SemVer for versioned releases" | → See [03-api-design.md, §8] defines API versioning strategy |
| "Branch protection rules" | → See [06-testing-strategy.md, §8.4] defines branch protection configuration |
| ".env files and what to gitignore" | → See [09-devops-cicd.md, §2.3] defines .env file conventions |

### Technology Versions

This document's guidance is based on the following tool versions. If a tool has had a major version change since these versions, verify that the guidance still applies.

| Tool | Version | Purpose |
|------|---------|---------|
| Git | ≥ 2.13.0 | Required by Husky (core.hooksPath) |
| Husky | v9.1.7 | Git hooks management |
| lint-staged | v16.4.0 | Run linters on staged files only |
| commitlint | v20.5.0 | Enforce Conventional Commits format |
| gitleaks | v8.30.1 | Secret detection in pre-commit |
| Conventional Commits | v1.0.0 (spec) | Commit message standard |
| semantic-release | v25.0.3 | Automated versioning and publishing (awareness) |

### Document Relationships

```text
10-git-workflow.md (this document)
 ├── References → 01-core-principles.md (ADR, DoD, dependency mgmt, refactoring discipline)
 ├── References → 02-technology-radar.md (Husky, lint-staged, commitlint, EditorConfig)
 ├── References → 03-api-design.md (API versioning strategy)
 ├── References → 06-testing-strategy.md (quality gates, merge blocking, branch protection)
 ├── References → 07-security-standards.md (secret detection, supply chain security)
 ├── References → 08-observability.md (build SHA in health endpoints)
 ├── References → 09-devops-cicd.md (deploy pipeline, .env conventions)
 ├── Complements → 11-project-management.md (issue tracking, boards, planning)
 └── Provides → templates/pr-template.md (PR description template)
```

### AI Agent Instructions

This document is designed to be consumed by AI coding agents (e.g., Claude
Code). When interpreting this document:

- **MUST**, **SHOULD**, and **MAY** are RFC 2119 keywords — treat MUST as non-negotiable constraints, SHOULD as strong defaults that require explicit justification to override, and MAY as contextual options.
- Cross-references (→ See [XX-document.md]) point to authoritative definitions — always defer to the referenced document for the full rule.
- When this document conflicts with [07-security-standards.md], the security document takes precedence.
- BAD/GOOD code examples are pattern-matching references — apply the principle behind the example, not just the literal code.
- Anti-pattern tables describe common mistakes — use them as negative examples when reviewing or generating code.
- Every commit message, branch name, and PR description MUST follow the conventions defined here.
- If generating code requires violating a MUST rule, the AI **MUST stop** and ask the human for permission before proceeding — never silently override a standard.
- **MUST NOT** over-engineer — always prefer the simplest solution that meets the stated requirements. Do not add abstractions, patterns, or infrastructure beyond what was explicitly requested (→ See [01-core-principles.md, §12]).

---

## 1. Git Philosophy

Before any convention or rule, there is a mindset about what Git is for and why it matters. These principles inform every decision in this document.

### 1.1 Git Is Documentation

Every commit message is a paragraph in the project's autobiography. Six months from now, when a developer runs `git log` or `git blame` to understand why a line of code exists, the commit message is the primary source of truth. A commit message that says `fix stuff` provides zero information. A commit message that says `fix(auth): prevent token refresh race condition on concurrent requests` tells the complete story.

The commit log is not a dump of what happened — it is a curated narrative of how the project evolved. Writing good commit messages is not extra work; it is the documentation that costs the least to write and provides the most value over time.

### 1.2 Clean History Enables Debugging

Git provides powerful tools for finding when and why a bug was introduced: `git bisect` performs a binary search through commit history to find the exact commit that introduced a regression, `git blame` shows who last modified each line and why, and `git log --oneline` provides a scannable timeline of changes.

These tools only work when the history is clean:
- `git bisect` requires that every commit leaves the project in a working state — a commit that breaks the build makes bisect useless because you cannot tell if the bisect target or the broken commit caused the failure
- `git blame` requires that commits are atomic (one logical change per commit) — a commit that mixes a feature, a bug fix, and a formatting change makes blame ambiguous
- `git log` requires meaningful commit messages — a log full of `WIP`, `fix`, `update` provides no signal

### 1.3 Conventions Reduce Cognitive Load

Git conventions are not bureaucracy — they are agreements that eliminate decisions. When the team agrees on branch naming (`feat/`, `fix/`), commit format (Conventional Commits), and merge strategy (squash merge), every developer can focus on the code instead of debating process in every PR.

Conventions also enable automation. Conventional Commits power automated changelog generation and semantic versioning. Branch naming conventions enable CI pipelines to apply different rules to feature branches vs. hotfix branches. PR templates ensure that every pull request includes the context reviewers need.

### 1.4 The Golden Rule

**Never rewrite history that has been shared with others.** Once commits are pushed to a shared branch (especially `main`), they become part of the team's shared timeline. Force-pushing to `main`, rebasing shared branches, or amending pushed commits creates confusion, lost work, and broken trust. Rewriting history on local or personal branches before pushing is acceptable and encouraged.

---

## 2. Branching Strategy

### 2.1 Default: GitHub Flow

All projects **MUST** use **GitHub Flow** as the default branching strategy. GitHub Flow is simple, predictable, and sufficient for the vast majority of projects:

1. `main` is always deployable — it represents the current production state
2. Create a short-lived feature branch from `main` for every change
3. Commit to the feature branch, push regularly
4. Open a Pull Request when the work is ready for review
5. After review and all quality gates pass, merge to `main`
6. `main` is deployed (automatically or manually, depending on the project)

**Why GitHub Flow over GitFlow:** GitFlow introduces `develop`, `release/*`, and `hotfix/*` branches that add complexity without proportional value for most projects. GitHub Flow works for continuous deployment, continuous delivery, and even manual release workflows. The simplicity reduces merge conflicts, shortens feedback loops, and makes the branching model easy to understand for developers at any experience level.

### 2.2 Branch Naming Conventions

- **MUST** use the following prefixes for all branches:

| Prefix | Purpose | Example |
|--------|---------|---------|
| `feat/` | New feature or enhancement | `feat/user-avatar-upload` |
| `fix/` | Bug fix | `fix/login-redirect-loop` |
| `chore/` | Maintenance, config, dependencies | `chore/update-eslint-config` |
| `docs/` | Documentation changes only | `docs/api-authentication-guide` |
| `refactor/` | Code restructuring, no behavior change | `refactor/extract-payment-service` |
| `test/` | Adding or fixing tests only | `test/add-checkout-integration-tests` |
| `hotfix/` | Urgent production fix | `hotfix/fix-payment-double-charge` |

- **MUST** use lowercase, kebab-case after the prefix: `feat/user-avatar-upload`, not `feat/UserAvatarUpload` or `feat/user_avatar_upload`
- **SHOULD** keep branch names short but descriptive — aim for 3–5 words after the prefix
- **SHOULD** include a ticket/issue reference when one exists: `feat/GH-42-user-avatar-upload` or `fix/JIRA-123-login-redirect`
- **MUST NOT** use generic names: `feat/new-feature`, `fix/bugfix`, `test/tests` provide no information

### 2.3 Main Branch Rules

- **MUST** protect `main` with branch protection rules (→ See [06-testing-strategy.md, §8.4])
- **MUST NOT** push directly to `main` — all changes go through Pull Requests
- **MUST** keep `main` in a deployable state at all times
- **SHOULD** configure `main` as the default branch in the repository settings

### 2.4 Branch Lifecycle

- **MUST** create branches from the latest `main` — run `git pull origin main` before branching
- **SHOULD** keep branches short-lived — ideally merged within 1–3 days, maximum 1 week
- **MUST** delete branches after merge — both locally and on the remote
- **SHOULD** configure the repository to auto-delete branches after merge (GitHub: Settings → General → Automatically delete head branches)

### 2.5 When to Consider Trunk-Based Development

Trunk-Based Development (TBD) is an alternative where all developers commit directly to `main` (or to very short-lived branches that are merged within hours). It reduces merge conflicts and enables faster integration, but requires:
- High test coverage and fast CI to catch regressions immediately
- Feature flags to hide incomplete work behind toggles
- Strong automated quality gates — there is no PR review buffer

**Current recommendation:** GitHub Flow with short-lived branches. TBD is documented here for awareness — it **MAY** be considered for mature projects with comprehensive test suites and experienced teams. If adopting TBD, **MUST** create an ADR documenting the rationale and prerequisites (→ See [01-core-principles.md, §9]).

### 2.6 Long-Lived Branches

Long-lived branches (branches that exist for weeks or months, such as `develop`, `staging`, or `release/v2`) are dangerous because they diverge from `main` over time, creating increasingly painful merge conflicts. Every day a branch lives without merging, the risk and cost of integration grows.

- **SHOULD NOT** maintain long-lived branches unless there is a documented, justified need
- If a long-lived branch is necessary (e.g., a major version rewrite that cannot be feature-flagged), **MUST** regularly merge `main` into the long-lived branch (at minimum weekly) to reduce divergence
- **MUST** create an ADR documenting why the long-lived branch exists and the plan to merge or close it

### 2.7 Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Direct push to `main`** | Bypasses review and quality gates; broken code enters production | Enable branch protection; no exceptions |
| **Long-lived feature branches** | Merge conflicts accumulate; integration becomes painful and risky | Break work into smaller PRs; merge frequently |
| **Generic branch names** (`fix/bugfix`) | History becomes unreadable; impossible to find branches by purpose | Use descriptive names with prefixes |
| **Branches without PR** | No review trail, no CI validation, no documentation of the change | Always use PRs, even for solo projects |
| **Stale branches** | Accumulate in the repository; confuse team about active work | Delete after merge; review stale branches weekly |
| **Branching from branches** | Creates dependency chains; one blocked PR blocks all downstream work | Branch from `main`; use feature flags for dependencies |

---

## 3. Commit Standards

### 3.1 Conventional Commits Format

All projects **MUST** use the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification (v1.0.0). This format adds semantic meaning to commit messages, enabling automated changelog generation, semantic version bumps, and a machine-readable history.

**Format:**

```
<type>(<optional scope>): <description>

<optional body>

<optional footer(s)>
```

**Rules:**
- **MUST** use one of the allowed types (see §3.2)
- **MUST** write the description in lowercase, imperative mood ("add feature", not "Added feature" or "adds feature")
- **MUST NOT** end the description with a period
- **MUST** keep the first line (type + scope + description) under 72 characters
- **SHOULD** include a body for non-trivial changes — explain *what* and *why*, not *how* (the diff shows *how*)
- **MUST** use `BREAKING CHANGE:` footer or `!` after the type/scope for breaking changes
- **MUST** enforce via commitlint + Husky (→ See [02-technology-radar.md, §4.12] for tool configuration)

### 3.2 Commit Types

| Type | Purpose | SemVer Impact | Example |
|------|---------|---------------|---------|
| `feat` | New feature or user-visible enhancement | MINOR | `feat(auth): add OAuth2 login flow` |
| `fix` | Bug fix | PATCH | `fix(cart): prevent negative quantity on decrement` |
| `docs` | Documentation only | None | `docs(api): add authentication examples to README` |
| `style` | Code style (formatting, whitespace) — no logic change | None | `style: apply prettier formatting to services/` |
| `refactor` | Code restructuring — no behavior change | None | `refactor(orders): extract discount calculation to service` |
| `test` | Adding or fixing tests — no production code change | None | `test(auth): add integration tests for token refresh` |
| `chore` | Maintenance, tooling, config — no production code change | None | `chore: update ESLint config to flat format` |
| `perf` | Performance improvement — no behavior change | PATCH | `perf(db): add index on orders.customer_id` |
| `ci` | CI/CD pipeline changes | None | `ci: add Playwright to GitHub Actions workflow` |
| `build` | Build system or external dependency changes | None | `build: upgrade Next.js to v16` |
| `revert` | Reverts a previous commit | Depends | `revert: revert "feat(auth): add OAuth2 login flow"` |

### 3.3 Scope

The scope provides additional context about which part of the codebase is affected. It is optional but **SHOULD** be used when the project has distinct modules or domains.

- **SHOULD** use consistent scope names within a project (e.g., `auth`, `cart`, `orders`, `ui`, `db`, `api`)
- **SHOULD** define the allowed scopes in `commitlint.config.js` for projects with established module boundaries
- **MUST NOT** use overly broad scopes (`app`, `code`, `stuff`) or overly specific scopes (`user-avatar-upload-handler`)

### 3.4 Breaking Changes

Breaking changes **MUST** be clearly communicated because they force consumers to adapt:

```
feat(api)!: change authentication from API keys to OAuth2

Migrate all API consumers from static API keys to OAuth2 client
credentials flow. Existing API keys will be invalidated on 2025-06-01.

BREAKING CHANGE: API key authentication is removed. All consumers must
register OAuth2 client credentials before the deprecation date.
Migration guide: https://docs.example.com/auth-migration
```

Two ways to signal a breaking change (both are valid, using both together is recommended):
1. Add `!` after the type/scope: `feat(api)!: ...`
2. Add `BREAKING CHANGE:` footer in the commit body

### 3.5 Atomic Commits

- **MUST** make each commit represent one logical change — one commit should do one thing
- **MUST NOT** mix unrelated changes in a single commit (e.g., a feature + a bug fix + a formatting cleanup)
- **MUST** keep refactoring commits separate from feature or bug fix commits (→ See [01-core-principles.md, §13.6])
- **SHOULD** ensure every commit leaves the project in a buildable, runnable state — this enables `git bisect`

**Why this matters:** A commit that contains "add user avatars + fix login bug + update ESLint rules" is impossible to revert partially, impossible to cherry-pick, and creates ambiguous `git blame` output. Three separate commits are cheaper to write and infinitely more valuable over time.

### 3.6 Commit Message Examples

**Good commits:**

```
feat(auth): add password reset flow via email

Users can now request a password reset link sent to their registered
email. The link expires after 24 hours and can only be used once.

Closes #42
```

```
fix(cart): prevent race condition when updating quantity

Concurrent requests to update item quantity could result in incorrect
totals. Added optimistic locking via version column on cart_items.
```

```
refactor(orders): extract tax calculation to dedicated service

Tax logic was duplicated across OrderService and InvoiceService.
Extracted to TaxCalculationService with a single source of truth.

No behavior change — all existing tests pass unmodified.
```

**Bad commits (and why):**

| Bad commit | Problem |
|------------|---------|
| `fix bug` | No type prefix, no scope, no description of what was fixed |
| `feat: update` | What was updated? This is meaningless |
| `WIP` | Work-in-progress commits should be squashed before merge |
| `fix: fix the fix` | No useful information; likely should be squashed with the original fix |
| `feat: add login, fix cart bug, update deps` | Three unrelated changes in one commit; violates atomic commit rule |
| `FEAT: Add Login Flow` | Wrong casing; should be lowercase `feat` and imperative mood |

### 3.7 When to Amend vs. Create a New Commit

- **Amend** (`git commit --amend`) when: fixing a typo in the last commit message, adding a forgotten file to the last commit, or adjusting the last commit before pushing
- **Create a new commit** when: the change is logically distinct from the previous commit, or the previous commit has already been pushed to a shared branch
- **MUST NOT** amend commits that have been pushed to a shared branch — this rewrites shared history (→ §1.4 Golden Rule)

### 3.8 Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **`WIP` or `temp` commits in history** | Noise in the log; no semantic meaning | Squash before merging; use draft PRs for work-in-progress |
| **Mixing unrelated changes** | Cannot revert, cherry-pick, or bisect accurately | One logical change per commit |
| **Giant commits** (500+ lines) | Impossible to review; high risk of hidden bugs | Break into smaller atomic commits |
| **Meaningless messages** (`fix`, `update`, `stuff`) | History provides zero debugging value | Follow Conventional Commits format |
| **Copy-pasted commit messages** | Same message for different changes; log becomes useless | Each commit describes its own change |
| **Committing generated files** | Noise in diffs; merge conflicts on auto-generated content | Add generated files to `.gitignore` |

---

## 4. Pre-commit Hooks & Local Quality Gates

Pre-commit hooks catch issues instantly — before the commit is created — tightening the feedback loop (→ See [01-core-principles.md, §1.6 — Feedback Loops Matter]). They complement CI but do not replace it: hooks are the fast local check, CI is the authoritative remote check.

### 4.1 Architecture Overview

The local quality gate stack consists of three layers, each catching a different class of issue:

```text
Developer runs: git commit -m "feat(auth): add OAuth2 flow"
  │
  ├─ [pre-commit hook] ← Husky triggers lint-staged
  │   ├─ ESLint --fix on staged .ts/.tsx/.js/.jsx files
  │   ├─ Prettier --write on staged files
  │   ├─ gitleaks (secret detection on staged files)
  │   └─ If ANY tool fails → commit is blocked
  │
  ├─ [commit-msg hook] ← Husky triggers commitlint
  │   ├─ Validates message format (Conventional Commits)
  │   └─ If invalid → commit is blocked
  │
  └─ Commit is created ✅
```

### 4.2 Husky Setup

Husky manages Git hooks by storing them in a tracked `.husky/` directory, ensuring every team member has the same hooks after `npm install`.

→ See [02-technology-radar.md, §4.12] for the tool choice rationale and Adopt status.

**Setup (Husky v9):**

```bash
# Install Husky
npm install --save-dev husky

# Initialize — creates .husky/ directory and adds prepare script
npx husky init
```

This adds `"prepare": "husky"` to `package.json`, ensuring hooks are installed automatically when anyone runs `npm install`.

**Important Husky v9 changes:**
- Hook files are plain shell scripts in `.husky/` — no shebang or sourcing required
- `husky add` is removed — create hook files manually or via `echo`
- Commands run directly without `npx` prefix (Husky resolves local binaries)
- `HUSKY=0` disables all hooks globally (e.g., `HUSKY=0 git commit` to bypass in emergencies)

### 4.3 Pre-commit Hook Configuration

Create `.husky/pre-commit`:

```bash
lint-staged
```

→ See [02-technology-radar.md, §4.12] for lint-staged configuration and Adopt status.

**lint-staged configuration in `package.json`:**

```json
{
  "lint-staged": {
    "*.{ts,tsx,js,jsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "*.{css,scss,md,json,yaml,yml}": [
      "prettier --write"
    ]
  }
}
```

**Why lint-staged:** Without lint-staged, pre-commit hooks would lint the entire codebase on every commit — unacceptably slow for projects with hundreds of files. lint-staged runs tools only on staged files, keeping commits fast (1–2 seconds instead of 30+).

### 4.4 Commit-msg Hook Configuration

Create `.husky/commit-msg`:

```bash
npx --no -- commitlint --edit $1
```

→ See [02-technology-radar.md, §4.12] for commitlint configuration and Adopt status.

**commitlint configuration (`commitlint.config.js` or `commitlint.config.mjs`):**

```javascript
export default {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'body-max-line-length': [0], // Disable body line length limit
  },
};
```

**Node v24 compatibility note:** If the project does not have a `package.json` with `"type": "module"`, commitlint may fail to load the config. Fix by either adding `"type": "module"` to `package.json` or renaming the config file to `commitlint.config.mjs`.

### 4.5 Secret Detection in Pre-commit

- **SHOULD** run gitleaks as a pre-commit hook to catch secrets before they reach the repository
- → See [07-security-standards.md, §7] for the complete leak detection and response strategy

**Using gitleaks with the pre-commit framework:**

Add to `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.30.1
    hooks:
      - id: gitleaks
```

**Alternative — direct integration in `.husky/pre-commit`:**

```bash
lint-staged
gitleaks detect --source . --verbose --redact --no-git
```

**Awareness — Betterleaks:** The creator of gitleaks launched [Betterleaks](https://github.com/betterleaks/betterleaks) in February 2026 as a successor project. Betterleaks is a drop-in replacement with backwards-compatible CLI and config, offering improved detection accuracy (BPE tokenization with 98.6% recall vs. entropy-based 70.4%) and parallelized scanning. As of March 2026, Betterleaks is v1.1.1 with a small community (473 stars vs. gitleaks' 25k+). **Current recommendation: continue using gitleaks; monitor Betterleaks for future evaluation.** If evaluating, create an ADR.

### 4.6 Optional: Dependency Audit on Pre-push

- **MAY** configure a pre-push hook to run `npm audit` for known vulnerabilities
- → See [07-security-standards.md, §11] for dependency and supply chain security

**Create `.husky/pre-push` (optional):**

```bash
npm audit --audit-level=high
```

**Warning:** `npm audit` can be slow (5–15 seconds depending on network and dependency count) and may produce false positives. If this slows down the developer workflow to the point where developers bypass hooks, it is counterproductive. The CI pipeline **MUST** run dependency auditing regardless (→ See [09-devops-cicd.md, §4.2]), so the pre-push hook is a convenience, not a requirement.

### 4.7 Complete .husky/ Directory Structure

```text
.husky/
├── pre-commit      # lint-staged + gitleaks
└── commit-msg      # commitlint
```

### 4.8 Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **No hooks at all** | Issues caught only in CI — slow feedback, wasted pipeline time | Install Husky + lint-staged as project baseline |
| **Hooks that take > 10 seconds** | Developers bypass with `--no-verify`; hooks become decorative | Keep hooks fast; move slow checks to CI or pre-push |
| **Linting the entire codebase in pre-commit** | Painfully slow; unrelated files cause false failures | Use lint-staged to run only on staged files |
| **Not committing `.husky/` to the repo** | New team members do not get hooks; inconsistent quality | Commit the `.husky/` directory; automate via `prepare` script |
| **Using `--no-verify` as standard practice** | Defeats the purpose of hooks; broken commits enter the repo | Investigate and fix the root cause (slow hooks, false positives) |
| **Hooks that modify non-staged files** | Unexpected changes appear in the working tree; confuses developers | Configure tools to only process staged files |

---

## 5. Pull Request Standards

A Pull Request (PR) is not just a merge mechanism — it is a unit of work documentation. A well-structured PR tells the reviewer what changed, why it changed, what was considered, and how to verify it. PRs also serve as historical records: when a developer later asks "when and why was this feature added?", the PR description and review discussion provide the answer.

### 5.1 PR as a Unit of Work

- **MUST** use Pull Requests for all changes, even in solo projects — the PR diff catches issues that are invisible in the editor
- **MUST** ensure each PR represents one logical unit of work — one feature, one bug fix, one refactoring task
- **MUST NOT** combine unrelated changes in a single PR (e.g., "add user avatars + fix cart bug + update dependencies")
- **SHOULD** keep PRs small and focused — smaller PRs merge faster, receive better reviews, and have fewer bugs

### 5.2 PR Size Guidelines

Research consistently shows that smaller PRs receive higher-quality reviews and introduce fewer defects:

| PR Size | Lines Changed | Review Quality | Recommendation |
|---------|---------------|----------------|----------------|
| **Small** | < 200 lines | High — reviewer can understand the full context | Ideal. Aim for this. |
| **Medium** | 200–400 lines | Moderate — reviewer needs focused attention | Acceptable. Consider splitting if possible. |
| **Large** | 400–800 lines | Low — reviewer fatigue sets in; issues are missed | Split into smaller PRs if the work allows it. |
| **Too large** | > 800 lines | Very low — effectively unreviewed rubber-stamping | **MUST** split. Use stacked PRs or feature flags. |

- **SHOULD** keep PRs under 400 lines of meaningful changes (excluding auto-generated files, lock files, and test fixtures)
- If a feature requires > 400 lines, **SHOULD** break it into a sequence of smaller PRs that each leave the codebase in a working state

### 5.3 PR Description

- **MUST** include a description that explains **what** changed and **why** — the diff shows *how*, the description provides *context*
- **SHOULD** use the PR template (→ See `templates/pr-template.md` and [01-core-principles.md, §11.4])
- **MUST** include the DoD checklist in the PR description (→ See [01-core-principles.md, §11.2])
- **SHOULD** link related issues or tickets

**Minimal PR description structure:**

```markdown
## What

Brief description of the change.

## Why

Context: what problem does this solve? Why this approach?

## How to Test

Steps for the reviewer to verify the change works.

## Definition of Done

### Universal
- [ ] Code quality: clean, no warnings, well-named
- [ ] Validation: inputs validated, errors handled
- [ ] Logic: business rules in services, layering respected
- [ ] Tests: critical paths covered, CI green
- [ ] Security: no secrets, auth enforced, data protected
- [ ] Docs: docstrings, README, ADR if needed

### Domain (check applicable)
- [ ] Frontend: responsive, a11y, states handled
- [ ] API: validation, error envelope, rate limits
- [ ] Database: migration, RLS, indexes
```

### 5.4 Draft PRs

- **SHOULD** use Draft PRs for work-in-progress that needs early feedback
- Draft PRs signal "this is not ready for merge, but I want your input on the approach"
- Draft PRs are useful for: validating architecture before investing in implementation, getting early review on complex changes, sharing progress with the team
- **MUST** convert draft to ready when the PR is complete and CI passes

### 5.5 Self-Review Discipline

Even in solo projects, **SHOULD** review the PR diff before requesting review (or before merging, if solo):

1. Open the PR in the GitHub UI and read the "Files changed" tab
2. Check for: accidentally committed files, debug statements left in, missing test coverage, unclear variable names, TODOs without ticket references
3. Leave comments on your own PR for anything that needs explanation — this saves the reviewer time

**Why self-review matters:** The context switch from "writing code" to "reading a diff" reveals issues that are invisible while editing. Developers consistently report catching 10–20% of issues during self-review that they missed while coding.

### 5.6 Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **No PR description** | Reviewer has no context; review is slower and less effective | Use the PR template; explain what and why |
| **PR title is the branch name** | `feat/GH-42-user-avatar-upload` is not a description | Write a human-readable title: "Add user avatar upload with image validation" |
| **Mega-PR** (1000+ lines) | Effectively unreviewed; bugs hide in the volume | Split into smaller PRs; use feature flags if needed |
| **PR stays open for weeks** | Merge conflicts accumulate; context is lost; blocks other work | Merge within 1–3 days; if blocked, discuss and unblock |
| **Merging without review** | No second pair of eyes; mistakes enter production unchallenged | Require at least one approving review (→ See [06-testing-strategy.md, §8.4]) |
| **DoD checklist ignored** | Quality bar is inconsistent; "done" means different things | Make DoD verification an explicit review step |

---

## 6. Code Review

### 6.1 Review Philosophy

Code review exists to verify that the Definition of Done is met — not to impose personal preferences. A reviewer's job is to answer: "Does this change meet our standards, and is it safe to ship?" Personal style preferences (spaces vs. tabs, single vs. double quotes) are resolved by automated tools (ESLint, Prettier), not by humans in review.

- **MUST** review against the DoD checklist (→ See [01-core-principles.md, §11.2])
- **MUST** block merge if any MUST-level DoD item is not satisfied
- **SHOULD** flag missing SHOULD-level items as review comments with a request for justification

### 6.2 What to Look For

When reviewing a PR, focus on these areas in order of importance:

1. **Correctness:** Does the code do what it claims to do? Are edge cases handled? Are error paths covered?
2. **Security:** Are inputs validated? Are there secrets in the code? Is authorization enforced? (→ See [07-security-standards.md])
3. **Architecture:** Does the change respect the project's layering? Is the logic in the right layer? Are there new dependencies that should be evaluated?
4. **Test coverage:** Are the critical paths tested? Do the tests verify behavior, not implementation? (→ See [06-testing-strategy.md])
5. **Readability:** Can another developer understand this code in 6 months? Are names clear? Is complexity justified?
6. **Performance:** Are there obvious performance issues (N+1 queries, unnecessary re-renders, missing indexes)?

**Do NOT review for:** formatting issues (automated by Prettier), import ordering (automated by ESLint), or personal code style preferences (resolved by team conventions).

### 6.3 Review Etiquette

- **MUST** be constructive — critique the code, not the author. "This function does X, but it should do Y because Z" is better than "This is wrong."
- **SHOULD** ask questions instead of making demands when the intent is unclear: "What happens if `userId` is null here?" is more helpful than "Handle null."
- **SHOULD** suggest alternatives when proposing changes — show the reviewer's preferred approach, do not just say "change this"
- **SHOULD** distinguish between blocking issues and suggestions using prefixes:
  - `blocker:` — must be addressed before merge
  - `nit:` — minor suggestion, non-blocking
  - `question:` — seeking clarification, non-blocking
  - `suggestion:` — alternative approach, non-blocking
- **MUST** acknowledge good work — if the implementation is elegant or well-tested, say so. Positive feedback reinforces good practices.

### 6.4 Review Turnaround Time

- **SHOULD** complete reviews within 24 business hours of being requested
- If a review will take longer (e.g., complex changes that require deep analysis), **SHOULD** acknowledge the PR and set an expectation: "I'll review this by tomorrow afternoon."
- Long review turnaround times are one of the biggest sources of developer frustration — a PR that sits unreviewed for days blocks progress, causes context-switching when the author returns to it, and accumulates merge conflicts.

### 6.5 Handling Disagreements

Disagreements during code review are normal and healthy — they are how the team improves. Handle them constructively:

1. **Discuss on the PR** — keep the conversation in the review thread so it is documented and searchable
2. **Focus on principles** — reference the engineering standards documents. "Our standards in [01-core-principles.md, §5] say we should use the repository pattern here" is more effective than "I prefer it this way."
3. **Escalate with an ADR** — if the disagreement reveals a gap in the standards or a case where the standards are unclear, create an ADR to document the decision
4. **Time-box** — if a discussion goes back and forth more than 3 times without resolution, take it to a synchronous conversation (call, meeting) and document the outcome on the PR

### 6.6 Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Rubber-stamping** ("LGTM" without reading) | Defects pass through unchallenged; review becomes ceremonial | Review against the DoD checklist; leave substantive comments |
| **Nitpicking style** (formatting, naming preferences) | Wastes time; creates friction; these should be automated | Automate style enforcement; reserve review for logic and architecture |
| **Gatekeeping** (blocking on personal preference) | Demoralizes the team; creates bottlenecks | Distinguish blockers from suggestions; use `nit:` prefix |
| **Review as attack** (hostile or dismissive tone) | Destroys psychological safety; people stop submitting PRs | Critique code, not people; assume positive intent |
| **Not reviewing at all** (merging without review) | No quality check; solo-developer mindset in a team context | Require at least one approval (→ See [06-testing-strategy.md, §8.4]) |
| **Review delayed > 48 hours** | Blocks progress; causes context-switching; merge conflicts grow | Set expectation of 24-hour turnaround; acknowledge receipt |

---

## 7. Merge Strategy

### 7.1 Default: Squash Merge

- **SHOULD** use **squash merge** as the default merge strategy for all PRs

Squash merge combines all commits from a feature branch into a single commit on `main`. This produces a clean, linear history where each commit on `main` represents one complete unit of work (one PR = one commit).

**Why squash merge:**
- **Clean history:** `git log --oneline` on `main` reads like a changelog — each line is a complete feature, fix, or improvement
- **Easy revert:** Reverting a feature is a single `git revert <commit>` instead of reverting a sequence of commits
- **WIP commits disappear:** Messy intermediate commits (`WIP`, `fix typo`, `actually fix it this time`) are squashed away — only the final, polished commit message survives
- **Simpler bisect:** Every commit on `main` is a meaningful, working state

**Squash merge message convention:** When squashing, use the PR title as the commit message subject and include the PR number:

```
feat(auth): add OAuth2 login flow (#42)
```

### 7.2 When to Use Merge Commits

- **MAY** use merge commits (non-fast-forward) when the branch's individual commits are meaningful and well-structured — for example, a large refactoring PR where each commit represents a deliberate step:
  1. `refactor(orders): extract discount types to enum`
  2. `refactor(orders): extract discount calculator to service`
  3. `refactor(orders): update order service to use discount calculator`
  4. `test(orders): add tests for discount calculator`

In this case, preserving the individual commits provides a clearer story than a single squashed commit. However, this requires discipline: every commit must follow Conventional Commits format, leave the code in a working state, and represent a logical step.

### 7.3 When to Use Rebase

- **MAY** use rebase to keep a branch up to date with `main` before merging: `git rebase main` on a feature branch replays the branch's commits on top of the latest `main`, avoiding merge commits in the branch itself
- **MUST NOT** rebase branches that have been shared with other developers (→ §1.4 Golden Rule) — rebase rewrites commit hashes, which breaks other developers' copies of the branch
- **MAY** use interactive rebase (`git rebase -i`) on local branches to clean up commit history before opening a PR — squash WIP commits, reword messages, reorder commits

### 7.4 Branch Protection Rules

- **MUST** configure branch protection on `main` (→ See [06-testing-strategy.md, §8.4] for the authoritative configuration)
- The following rules **SHOULD** be enabled on `main`:
  - Require pull request before merging
  - Require at least one approving review
  - Require status checks to pass before merging (quality gates, E2E tests)
  - Require branches to be up to date before merging
  - Do not allow bypassing the above settings (even for admins)
- **SHOULD** configure the repository to use squash merge as the default (GitHub: Settings → General → Pull Requests → Allow squash merging, default to PR title + description)

### 7.5 Post-Merge Cleanup

- **MUST** delete the feature branch after merge — both on the remote and locally
- **SHOULD** enable auto-delete of merged branches in the repository settings
- Local cleanup:

```bash
# After merge, switch to main and clean up
git checkout main
git pull origin main
git branch -d feat/user-avatar-upload       # delete local branch
git fetch --prune                             # remove stale remote-tracking refs
```

### 7.6 Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Merge commits on every PR** | History is cluttered with merge bubbles; `git log --oneline` is noisy | Use squash merge as default |
| **Force push to `main`** | Rewrites shared history; breaks every team member's local copy | Protect `main`; never force push shared branches |
| **Not deleting merged branches** | Repository accumulates hundreds of stale branches; confusion about active work | Enable auto-delete; prune regularly |
| **Merging with failing tests** | Broken code on `main`; trust in CI erodes; `git bisect` becomes unreliable | Enforce required status checks (→ See [06-testing-strategy.md, §8.4]) |
| **Rebase on shared branches** | Team members' copies diverge; merge conflicts multiply | Only rebase local/personal branches |
| **"Merge anyway" culture** | Quality gates become decorative; standards decay over time | Block merge when checks fail; no exceptions without ADR |

---

## 8. Release & Versioning

### 8.1 Semantic Versioning (SemVer)

- **SHOULD** use [Semantic Versioning](https://semver.org/) (SemVer) when the project produces artifacts consumed by others (npm packages, APIs, libraries, SDKs)
- SemVer format: `MAJOR.MINOR.PATCH` (e.g., `2.4.1`)

| Component | When to increment | Conventional Commits trigger |
|-----------|-------------------|------------------------------|
| **MAJOR** | Breaking changes — consumers must update their code | `feat!:`, `fix!:`, `BREAKING CHANGE:` footer |
| **MINOR** | New features — backwards-compatible additions | `feat:` |
| **PATCH** | Bug fixes — backwards-compatible corrections | `fix:`, `perf:` |

- For projects that are not consumed externally (internal web applications, client projects), SemVer is **MAY** — the deployment pipeline and commit history provide sufficient versioning
- **MUST** create an ADR before introducing API versioning or automated release tooling (→ See [01-core-principles.md, §9])

### 8.2 Git Tags for Releases

- **SHOULD** use annotated Git tags to mark releases:

```bash
# Create annotated tag
git tag -a v1.2.0 -m "Release v1.2.0: add OAuth2 support, fix cart race condition"

# Push tag to remote
git push origin v1.2.0
```

- **MUST** prefix tags with `v` for consistency: `v1.2.0`, not `1.2.0`
- **SHOULD** tag from the `main` branch only — releases come from `main`
- **MUST NOT** delete or move tags after they are pushed — tags are permanent references

### 8.3 GitHub Releases

- **SHOULD** create a GitHub Release for each version tag
- GitHub Releases provide a UI for release notes, downloadable assets, and a permanent URL for each release
- The release description **SHOULD** include: a summary of changes, links to relevant PRs, migration notes for breaking changes, and known issues

### 8.4 Automated Releases with semantic-release (Awareness)

[semantic-release](https://github.com/semantic-release/semantic-release) (v25.0.3) automates the entire release workflow: version determination, changelog generation, Git tag creation, GitHub Release publishing, and npm publishing — all based on Conventional Commits messages.

- **MAY** adopt semantic-release for projects that publish npm packages or need automated versioning
- semantic-release works because the team follows Conventional Commits — the commit types directly determine the version bump
- v25 supports **npm trusted publishing** (OIDC-based authentication on GitHub Actions), eliminating the need for long-lived npm tokens — a security improvement aligned with [07-security-standards.md]
- **MUST** create an ADR before adopting automated release tooling

### 8.5 CHANGELOG.md

- **MAY** maintain a `CHANGELOG.md` manually or generate it automatically via semantic-release
- If maintained manually, **SHOULD** follow the [Keep a Changelog](https://keepachangelog.com/) format with sections: Added, Changed, Deprecated, Removed, Fixed, Security
- For projects without formal releases, the Git log serves as the changelog — this is sufficient for most internal projects

### 8.6 Build Identifiers

- **SHOULD** expose a build identifier (commit SHA) in the application's health endpoint (→ See [08-observability.md, §5.1])
- This enables quick verification of which code version is deployed in each environment:

```json
{
  "status": "healthy",
  "version": "1.2.0",
  "build": "a1b2c3d"
}
```

- Inject the commit SHA at build time via environment variable: `BUILD_SHA=$(git rev-parse --short HEAD)`

### 8.7 API Versioning Relationship

- API versioning strategy is defined in → See [03-api-design.md, §8]
- When introducing API versioning (URL path versioning: `/api/v1/`, `/api/v2/`), **MUST** create an ADR
- API version changes typically correspond to SemVer MAJOR bumps
- The deprecation lifecycle for API versions follows the timeline defined in [03-api-design.md, §8]

### 8.8 Versioning ML & Fine-Tuning Artifacts

A fine-tune is a versioned, reproducible artifact — not a one-off experiment. This section owns
*how git handles it*; *whether / when* to fine-tune is → See [12-ai-engineering.md, §7.5–§7.6].

**Rules:**

- Split a fine-tuning artifact by type and store each where it belongs:
  - **Config-as-code** — the `Modelfile`, the LoRA / training recipe and hyperparameters, eval
    thresholds — **MUST** live in the repo as plain text, versioned and diffable like any code.
    → See §3 (commits).
  - **Large binaries** — the training dataset, the resulting adapter / weights, the base model —
    **MUST NOT** be committed to plain git (they bloat history irreversibly). Track them with Git
    LFS or, preferably at scale, an external artifact / model registry or object storage, and
    **pin them in the repo by content hash + version**.
- A fine-tune **MUST** be reproducible from version control alone: the recipe plus pinned
  references must rebuild any checkpoint. Version the dataset hash, recipe, base model + version,
  and adapter **together** (one tag / one commit referencing all four). → See
  [12-ai-engineering.md, §7.6]; §1.3.
- Any dataset or weights tracked via LFS **MUST** be declared in `.gitattributes`. → See §10.3.

```gitattributes
  # Fine-tuning binaries → Git LFS (never plain git); the recipe/Modelfile stay as text
  *.safetensors filter=lfs diff=lfs merge=lfs -text
  data/train/**  filter=lfs diff=lfs merge=lfs -text
```

- Adapters / checkpoints **SHOULD** be tagged or released like any versioned artifact (SemVer-style
  or `date+hash`) so a deployed model maps back to its exact training inputs. → See §8.1, §8.2.

**Why:**

A fine-tune that cannot be rebuilt is a liability: when it regresses you cannot diff what changed,
and you cannot answer the AI-Act / audit question "what produced this model" (→
[12-ai-engineering.md, §5.7]). Git is excellent for the *recipe* (text, diffable) and terrible for
multi-GB weights and datasets (irreversible history bloat, no dedup). The discipline follows from
that split: recipe and pinned hashes in git, heavy artifacts in LFS or a registry, and the whole
set versioned as one reproducible unit.

### 8.9 Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **No versioning at all** | Impossible to know what is deployed; rollback is guesswork | Use SemVer + Git tags for consumable projects |
| **Manual version bumps without tags** | Version numbers in `package.json` drift; no Git reference point | Create Git tags for every release |
| **Deleting or moving tags** | Breaks references; consumers who pinned a version lose their anchor | Tags are permanent; create a new version instead |
| **Skipping MAJOR for breaking changes** | Consumers update expecting backwards compatibility; their code breaks | Follow SemVer strictly; breaking changes = MAJOR bump |
| **Changelog as afterthought** | Release notes are empty or inaccurate; consumers cannot evaluate upgrades | Automate changelog generation from Conventional Commits |

---

## 9. Git Workflow by Project Stage

Not every project requires the full workflow. The level of ceremony should match the project's risk, team size, and audience. The following guide scales from lightweight to full, maintaining quality at every stage.

### 9.1 Personal Project / Learning

**Context:** Solo developer, no external consumers, primary goal is learning and experimentation.

| Aspect | Recommendation |
|--------|----------------|
| **Branching** | GitHub Flow (main + feature branches) |
| **Branch protection** | MAY disable — speed matters more |
| **Commits** | MUST follow Conventional Commits (build the habit early) |
| **Hooks** | SHOULD install Husky + lint-staged + commitlint (muscle memory) |
| **PRs** | MAY skip — direct push to `main` is acceptable |
| **Reviews** | MAY skip — self-review on diffs is sufficient |
| **Merge strategy** | Any — consistency is less critical solo |
| **Releases** | MAY skip — Git history is the changelog |
| **gitleaks** | SHOULD install — secrets in personal repos leak too |

**Why still follow Conventional Commits:** Building the habit early costs nothing and pays dividends. When the developer later works on a team project or a freelance client's codebase, Conventional Commits are already second nature.

### 9.2 Freelance Client Project

**Context:** Professional delivery to a client who may have other developers or stakeholders. The code may be handed off, maintained by others, or audited.

| Aspect | Recommendation |
|--------|----------------|
| **Branching** | GitHub Flow (main + feature branches) |
| **Branch protection** | SHOULD enable on `main` (required checks, no direct push) |
| **Commits** | MUST follow Conventional Commits |
| **Hooks** | MUST install full stack (Husky + lint-staged + commitlint + gitleaks) |
| **PRs** | MUST use PRs for all changes |
| **Reviews** | SHOULD self-review every PR diff before merge |
| **Merge strategy** | SHOULD squash merge |
| **Releases** | SHOULD use Git tags for milestone deliveries |
| **gitleaks** | MUST install — client data and credentials are high-risk |

**Why full hooks for freelance:** Client projects carry reputational and legal risk. A committed secret, a broken deployment, or an unreadable Git history reflects directly on professional credibility. The 5-minute setup cost of hooks is negligible compared to the risk.

### 9.3 Team Project

**Context:** Multiple developers, shared codebase, continuous delivery, potentially public-facing.

| Aspect | Recommendation |
|--------|----------------|
| **Branching** | GitHub Flow with enforced branch naming |
| **Branch protection** | MUST enable full protection on `main` (→ See [06-testing-strategy.md, §8.4]) |
| **Commits** | MUST follow Conventional Commits |
| **Hooks** | MUST install full stack for all developers |
| **PRs** | MUST use PRs for all changes; MUST use PR template |
| **Reviews** | MUST require at least one approving review |
| **Merge strategy** | MUST squash merge (default); MAY use merge commits for structured refactoring PRs |
| **Releases** | SHOULD use SemVer + Git tags; MAY use semantic-release |
| **gitleaks** | MUST install in pre-commit and CI |

### 9.4 Decision Guide

```text
Is someone else going to read, review, or maintain this code?
├── No  → Personal workflow (§9.1)
├── Yes, a client → Freelance workflow (§9.2)
└── Yes, a team → Team workflow (§9.3)

Is the project consumed externally (npm package, public API)?
├── No  → Git history is the changelog; SemVer is optional
└── Yes → MUST use SemVer + Git tags; SHOULD use semantic-release
```

---

## 10. Git Configuration Checklist

### 10.1 New Project Setup

When initializing a new project, complete the following checklist before the first meaningful commit:

**Repository initialization:**

- [ ] `git init` (or create repository on GitHub)
- [ ] Set `main` as the default branch
- [ ] Add `.gitignore` appropriate for the stack (see §10.2)
- [ ] Add `.gitattributes` for line ending normalization (see §10.3)
- [ ] Add `.editorconfig` for cross-editor consistency (→ See [02-technology-radar.md, §4.12])

**Quality tooling:**

- [ ] Install Husky: `npm install --save-dev husky && npx husky init`
- [ ] Install lint-staged: `npm install --save-dev lint-staged`
- [ ] Install commitlint: `npm install --save-dev @commitlint/cli @commitlint/config-conventional`
- [ ] Create `.husky/pre-commit` with `lint-staged`
- [ ] Create `.husky/commit-msg` with `npx --no -- commitlint --edit $1`
- [ ] Create `commitlint.config.mjs` extending `@commitlint/config-conventional`
- [ ] Configure lint-staged in `package.json`
- [ ] Install gitleaks (local or via pre-commit framework)

**PR template:**

- [ ] Create `.github/pull_request_template.md` with DoD checklist (→ See [01-core-principles.md, §11.4])

### 10.2 .gitignore Baseline (Node.js / Next.js)

Every project **MUST** have a `.gitignore` that excludes build artifacts, dependencies, environment files, and editor-specific files. The following is the baseline for Node.js / Next.js projects:

```gitignore
# Dependencies
node_modules/
.pnp/
.pnp.js

# Build output
.next/
out/
dist/
build/

# Environment files (→ See [09-devops-cicd.md, §2.3])
.env
.env.local
.env.*.local

# Keep .env.example committed as documentation
!.env.example

# IDE / Editor
.vscode/settings.json
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db

# Debug logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Test coverage
coverage/

# TypeScript cache
*.tsbuildinfo

# Sentry
.sentryclirc

# Vercel
.vercel

# Supabase local
supabase/.temp/
```

**Important:** Lock files (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`) **MUST** be committed — they ensure reproducible installs across all environments (→ See [01-core-principles.md, §10] and [07-security-standards.md, §11]).

### 10.3 .gitattributes

A `.gitattributes` file normalizes line endings and configures diff behavior, preventing cross-platform issues in teams with Windows, macOS, and Linux developers.

**Baseline `.gitattributes`:**

```gitattributes
# Auto-detect text files and normalize line endings to LF
* text=auto

# Force specific file types to LF (even on Windows)
*.js text eol=lf
*.ts text eol=lf
*.tsx text eol=lf
*.jsx text eol=lf
*.json text eol=lf
*.md text eol=lf
*.css text eol=lf
*.scss text eol=lf
*.html text eol=lf
*.yaml text eol=lf
*.yml text eol=lf
*.sh text eol=lf

# Mark binary files to prevent Git from attempting text conversion
*.png binary
*.jpg binary
*.jpeg binary
*.gif binary
*.ico binary
*.woff binary
*.woff2 binary
*.ttf binary
*.eot binary
*.pdf binary

# Lock files — treat as generated (reduces diff noise in PRs)
package-lock.json -diff linguist-generated=true
yarn.lock -diff linguist-generated=true
pnpm-lock.yaml -diff linguist-generated=true
```

**Why `.gitattributes` matters:** Without it, developers on Windows may commit files with CRLF line endings, creating noisy diffs that show every line as changed. The `text=auto` setting normalizes to LF in the repository while allowing the developer's OS to use its native line endings in the working tree.

### 10.4 GitHub Repository Settings Checklist

After creating a repository on GitHub, configure the following settings:

**General:**

- [ ] Default branch set to `main`
- [ ] Auto-delete head branches after merge: enabled
- [ ] Pull Requests: allow squash merging (default to PR title + description)
- [ ] Pull Requests: consider disabling merge commits (to enforce squash)

**Branch protection on `main`:**

- [ ] Require pull request before merging
- [ ] Require at least 1 approving review
- [ ] Require status checks to pass before merging (select the quality gate workflows)
- [ ] Require branches to be up to date before merging
- [ ] Do not allow bypassing the above settings
- [ ] → See [06-testing-strategy.md, §8.4] for the authoritative branch protection configuration

**Security:**

- [ ] Enable GitHub secret scanning (→ See [07-security-standards.md, §7])
- [ ] Enable Dependabot alerts for vulnerable dependencies (→ See [07-security-standards.md, §11])

### 10.5 Developer Onboarding Checklist

When a new developer joins a project, they should complete the following setup:

1. **Clone the repository:** `git clone <repo-url>`
2. **Install dependencies:** `npm install` (this automatically runs `husky` via the `prepare` script, installing Git hooks)
3. **Verify hooks are installed:** check that `.husky/pre-commit` and `.husky/commit-msg` exist in `.git/hooks/` or that `git config core.hooksPath` points to `.husky/`
4. **Copy environment file:** `cp .env.example .env.local` and fill in local values (→ See [09-devops-cicd.md, §2.3])
5. **Test a commit:** make a trivial change, commit with a Conventional Commits message, and verify that lint-staged and commitlint run
6. **Read the PR template:** open `.github/pull_request_template.md` and understand the DoD checklist
7. **Review the README:** understand the project structure, development commands, and deployment process

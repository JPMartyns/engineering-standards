# PR Template — Pull Request Description

<!--
PURPOSE:
  A copy-and-fill template for Pull Request descriptions on GitHub.
  A well-structured PR tells the reviewer what changed, why it changed,
  what was considered, and how to verify it. PRs also serve as historical
  records — when a developer later asks "when and why was this feature
  added?", the PR description and review discussion provide the answer.

WHEN TO USE:
  Every Pull Request. Even in solo projects — the PR diff catches issues
  that are invisible in the editor.

WHERE TO SAVE:
  .github/pull_request_template.md
  GitHub automatically uses this file as the default body for new PRs.

  Alternative locations (GitHub looks for these in order):
  - .github/pull_request_template.md (recommended)
  - pull_request_template.md (repository root)
  - docs/pull_request_template.md

PR SIZE GUIDELINES:
  - Small  (< 200 lines):  High review quality — aim for this
  - Medium (200–400 lines): Acceptable — consider splitting if possible
  - Large  (400–800 lines): Split into smaller PRs if the work allows it
  - Too large (> 800 lines): MUST split — use stacked PRs or feature flags
  → See [10-git-workflow.md, §5.2] for the full size guidelines

SELF-REVIEW DISCIPLINE:
  Before requesting review (or before merging, if solo):
  1. Open the PR in GitHub UI and read the "Files changed" tab
  2. Check for: accidentally committed files, debug statements,
     missing test coverage, unclear variable names, TODOs without tickets
  3. Leave comments on your own PR for anything that needs explanation
  → See [10-git-workflow.md, §5.5] for why self-review matters

REFERENCES:
  → See [10-git-workflow.md, §5] — Complete PR standards (size, description, review)
  → See [01-core-principles.md, §11] — Definition of Done (universal + domain-specific)
  → See [01-core-principles.md, §11.4] — How to use DoD in PRs
  → See [06-testing-strategy.md, §8.4] — Branch protection and merge blocking rules

AI AGENT INSTRUCTIONS:
  When using this template:
  1. Copy the content below the separator (---) to .github/pull_request_template.md
  2. The content between the separator lines IS the actual PR template
  3. Do NOT include this header block in the final .github/ file
  4. The PR author fills in the sections and checks off the DoD items
  5. Reviewers verify the DoD checklist during code review
  6. All MUST-level DoD items MUST be satisfied before merge
  7. SHOULD-level items that are skipped require justification in the PR description
-->

---

<!-- ═══════════════════════════════════════════════════════════════
     COPY EVERYTHING BELOW THIS LINE TO:
     .github/pull_request_template.md
     ═══════════════════════════════════════════════════════════════ -->

## What

<!-- Briefly describe what this PR changes. Focus on the WHAT, not the HOW
     (the diff shows the how). One to three sentences is usually sufficient. -->



## Why

<!-- Explain the context and motivation:
     - What problem does this solve?
     - Why this approach over alternatives?
     - Link to the related issue or ticket using a closing keyword:
       Closes #<issue-number>, Fixes #<issue-number>, or Resolves #<issue-number>
       This automatically moves the issue to Done when the PR is merged.
     → See [11-project-management.md, §2.7] for issue-PR traceability -->

Closes #

## How to Test

<!-- Provide clear steps for the reviewer to verify the change works.
     Include any setup steps, test data, or environment requirements.
     If there are specific scenarios to test, list them.

     Example:
     1. Check out this branch
     2. Run `npm run dev`
     3. Navigate to /users/profile
     4. Upload an image larger than 5MB → should show validation error
     5. Upload a valid image → should display the new avatar -->

1.
2.
3.

## Screenshots / Recordings

<!-- If the change has a visual component, include before/after screenshots
     or a short screen recording. Delete this section if not applicable. -->

## Notes for Reviewer

<!-- Optional: anything the reviewer should pay special attention to,
     areas where you are uncertain, or decisions you want feedback on.
     Delete this section if not needed. -->

---

## Definition of Done

<!-- Check off each item as you verify it. All MUST-level items must be
     satisfied before merge. If a SHOULD-level item is skipped, add a
     brief justification next to it.
     → See [01-core-principles.md, §11.2] for the full DoD explanation -->

### Universal

<!-- These apply to EVERY PR, regardless of domain. -->

#### Code Quality
- [ ] Code follows clean code principles — no warnings, well-named functions and variables
- [ ] No `any` types, unsafe casts, or suppressed warnings without documented justification
- [ ] No dead code, commented-out code, or orphaned files introduced
- [ ] Functions are small, focused, and follow single responsibility

#### Validation & Error Handling
- [ ] All inputs from untrusted sources are validated at the system boundary
- [ ] Error handling is explicit — no silent failures or swallowed exceptions
- [ ] Errors return structured, predictable responses (no stack traces exposed to users)
- [ ] Edge cases identified and handled (empty states, null values, boundary conditions)

#### Business Logic
- [ ] Business logic resides in the service layer — not in UI components or data access code
- [ ] Layering rules respected — no upward dependencies, no circular dependencies
- [ ] Feature correctly implements the specified requirements

#### Testing
- [ ] Critical paths have automated tests (at minimum, unit tests for business logic)
- [ ] Tests follow Arrange–Act–Assert pattern and are readable
- [ ] Tests cover both happy path and key failure scenarios
- [ ] All tests pass in CI

#### Security
- [ ] No secrets or credentials hardcoded in the code
- [ ] Authentication and authorization enforced for protected operations
- [ ] Input validation prevents injection and malformed data
- [ ] Sensitive data not exposed in logs, error messages, or client responses

#### Documentation
- [ ] Public functions and services have docstrings (what, params, returns, throws)
- [ ] README updated if setup steps, environment variables, or project structure changed
- [ ] ADR created if a significant architectural decision was made (→ `templates/adr-template.md`)
- [ ] Non-obvious decisions have inline comments explaining **why**
- [ ] TODOs include a ticket/issue reference

#### Code Review
- [ ] Self-review completed on the PR diff before requesting review
- [ ] PR description explains **what** changed and **why**

### Domain-Specific

<!-- Check the sections that apply to this PR. Delete sections that are not relevant. -->

#### Frontend / UI
<!-- → See [05-frontend-standards.md] for full frontend standards -->
- [ ] Responsive / mobile verified
- [ ] Accessibility checked (keyboard navigation, screen reader, contrast)
- [ ] Loading, error, and empty states handled
- [ ] Touch targets adequate (minimum 44x44px)

#### API
<!-- → See [03-api-design.md] for full API standards -->
- [ ] Request and response validation in place (Zod schemas)
- [ ] Error envelope consistent with project standard
- [ ] Pagination capped to prevent abuse
- [ ] Rate limiting configured for new endpoints

#### Database
<!-- → See [04-database-standards.md] for full database standards -->
- [ ] Migration created and reviewed
- [ ] RLS policies in place (if Supabase)
- [ ] Indexes reviewed for new queries
- [ ] Naming conventions followed

#### Security-Sensitive Features
<!-- → See [07-security-standards.md] for full security standards -->
- [ ] STRIDE assessment completed for auth, payments, PII, file uploads, or admin actions
- [ ] Threat mitigations documented
- [ ] Security headers verified

#### Infrastructure / Deployment
<!-- → See [09-devops-cicd.md] for full DevOps standards -->
- [ ] Environment variables configured and documented
- [ ] Deployment pipeline tested
- [ ] Rollback plan identified

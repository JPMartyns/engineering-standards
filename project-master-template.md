# PROJECT MASTER

> **Document Type:** Project Master Document  
> **Primary Audience:** AI assistants and automation agents  
> **Purpose:** Single-source project definition for discovery, requirements, scope, domain rules, non-functional constraints, technical direction, delivery planning, and decision boundaries.

---

## 0. DOCUMENT CONTROL

### 0.1 Metadata
- **Project Name:** `<PROJECT_NAME>`
- **Project Code:** `<PROJECT_CODE>`
- **Version:** `0.1.0`
- **Status:** `Draft | In Review | Approved | Deprecated`
- **Owner:** `<OWNER_NAME_OR_ROLE>`
- **Created At:** `<YYYY-MM-DD>`
- **Last Updated At:** `<YYYY-MM-DD>`
- **Primary Repository:** `<REPOSITORY_URL_OR_PATH>`
- **Related Standards Index:** `<LINK_OR_PATH_TO_GLOBAL_STANDARDS_INDEX>`
- **Related ADR Index:** `<LINK_OR_PATH_TO_ADR_INDEX>`
- **Primary Business Contact:** `<NAME_OR_ROLE>`
- **Primary Technical Contact:** `<NAME_OR_ROLE>`

### 0.2 Reading Protocol for AI
The AI consuming this document MUST follow this order before proposing solutions, generating code, or reviewing implementation:

1. Read **Project Goal**, **Scope**, **Actors**, **Functional Requirements**, and **Domain Rules**.
2. Read **Non-Functional Requirements**, **Constraints**, and **Technical Direction**.
3. Check **Open Questions**, **Risks**, and **Decision Log**.
4. Apply global standards from the referenced engineering standards library.
5. Prefer explicit project rules over generic assumptions.
6. If a requested solution conflicts with a rule in this document, the AI MUST explicitly flag the conflict before proceeding.
7. If a required detail is missing, the AI MUST state the assumption and mark it for confirmation or future refinement.
8. The AI MUST NOT invent product behavior that is not supported by this document or by approved ADRs.

### 0.3 Rule Priority
When rules appear to conflict, apply this precedence order:

1. Approved ADRs specific to this project
2. Security and compliance requirements
3. Explicit domain rules in this document
4. Functional requirements in this document
5. Non-functional requirements in this document
6. Technical direction in this document
7. Global engineering standards
8. Optional implementation preferences

### 0.4 Writing Conventions
This document uses the following normative terms:

- **MUST**: mandatory requirement
- **MUST NOT**: forbidden behavior
- **SHOULD**: recommended unless justified otherwise
- **SHOULD NOT**: discouraged unless justified otherwise
- **MAY**: optional

---

## 1. PROJECT OVERVIEW

### 1.1 Project Summary
Provide a concise, high-signal summary of the project.

**Template**
- **Project Purpose:** `<ONE_PARAGRAPH_SUMMARY>`
- **Primary Problem:** `<PROBLEM_BEING_SOLVED>`
- **Primary Outcome:** `<DESIRED_RESULT>`
- **Primary Users:** `<TARGET_USERS>`
- **Business Value:** `<WHY_THIS_PROJECT_EXISTS>`

### 1.2 Problem Statement
Describe the real-world problem in explicit terms.

**Template**
- What is broken, slow, manual, confusing, or missing?
- Who is affected?
- What is the current workaround?
- What is the cost of not solving this problem?

### 1.3 Product Vision
State what success looks like.

**Template**
- The product exists to `<MAIN_PURPOSE>`.
- It helps `<TARGET_USER_GROUP>` to `<CORE_JOB_TO_BE_DONE>`.
- It is valuable because `<VALUE_PROPOSITION>`.
- It is different from alternatives because `<DIFFERENTIATOR>`.

### 1.4 Strategic Goals
List measurable or evaluable goals.

**Template**
- **Goal G-001:** `<GOAL_DESCRIPTION>`
- **Goal G-002:** `<GOAL_DESCRIPTION>`
- **Goal G-003:** `<GOAL_DESCRIPTION>`

### 1.5 Non-Goals
State what this project is NOT trying to do.

**Template**
- **NG-001:** `<OUT_OF_SCOPE_INTENTIONAL_EXCLUSION>`
- **NG-002:** `<OUT_OF_SCOPE_INTENTIONAL_EXCLUSION>`
- **NG-003:** `<OUT_OF_SCOPE_INTENTIONAL_EXCLUSION>`

---

## 2. CONTEXT AND ASSUMPTIONS

### 2.1 Business Context
Describe the project environment.

**Template**
- **Organization Type:** `<STARTUP | SMALL BUSINESS | CHURCH | INTERNAL TOOL | OTHER>`
- **Operational Context:** `<SHORT_DESCRIPTION>`
- **Expected Adoption Context:** `<HOW_USERS_WILL_USE_IT>`
- **Budget Sensitivity:** `<LOW | MEDIUM | HIGH>`
- **Time Sensitivity:** `<LOW | MEDIUM | HIGH>`

### 2.2 Core Assumptions
Record assumptions explicitly.

**Template**
- **A-001:** `<ASSUMPTION>`
- **A-002:** `<ASSUMPTION>`
- **A-003:** `<ASSUMPTION>`

### 2.3 Validation Gaps
State what is unknown and not yet validated.

**Template**
- **VG-001:** `<UNKNOWN_OR_UNVALIDATED_AREA>`
- **VG-002:** `<UNKNOWN_OR_UNVALIDATED_AREA>`
- **VG-003:** `<UNKNOWN_OR_UNVALIDATED_AREA>`

---

## 3. ACTORS AND USERS

### 3.1 Actor Catalog
Define every relevant actor.

**Template**
| Actor ID | Actor Name | Type | Description | Permissions Summary |
|----------|------------|------|-------------|---------------------|
| ACT-001 | `<ACTOR_NAME>` | `Human | External System | Admin | Member | Guest` | `<DESCRIPTION>` | `<SUMMARY>` |

### 3.2 Primary User Segments
Describe who the system is built for.

**Template**
| Segment ID | Segment Name | Needs | Pain Points | Success Criteria |
|------------|--------------|-------|-------------|------------------|
| USR-001 | `<SEGMENT_NAME>` | `<NEEDS>` | `<PAINS>` | `<HOW_SUCCESS_IS_MEASURED>` |

### 3.3 Roles and Permissions
Define the role model.

**Template**
| Role ID | Role Name | Allowed Actions | Forbidden Actions | Notes |
|---------|-----------|-----------------|-------------------|-------|
| ROLE-001 | `<ROLE_NAME>` | `<ALLOWED_ACTIONS>` | `<FORBIDDEN_ACTIONS>` | `<NOTES>` |

### 3.4 Actor Boundaries
List trust boundaries and responsibility boundaries.

**Template**
- External users MUST only access data allowed by their role.
- Administrative actions MUST be auditable.
- Cross-tenant or cross-organization access MUST NOT occur unless explicitly allowed.
- Service accounts MUST have scoped permissions only.

---

## 4. PROJECT SCOPE

### 4.1 In Scope
List the capabilities included in the current project or phase.

**Template**
- **SCP-IN-001:** `<IN_SCOPE_ITEM>`
- **SCP-IN-002:** `<IN_SCOPE_ITEM>`
- **SCP-IN-003:** `<IN_SCOPE_ITEM>`

### 4.2 Out of Scope
List excluded capabilities explicitly.

**Template**
- **SCP-OUT-001:** `<OUT_OF_SCOPE_ITEM>`
- **SCP-OUT-002:** `<OUT_OF_SCOPE_ITEM>`
- **SCP-OUT-003:** `<OUT_OF_SCOPE_ITEM>`

### 4.3 Future Scope
List possible future expansions that are known but intentionally deferred.

**Template**
- **SCP-FUT-001:** `<FUTURE_PHASE_ITEM>`
- **SCP-FUT-002:** `<FUTURE_PHASE_ITEM>`
- **SCP-FUT-003:** `<FUTURE_PHASE_ITEM>`

### 4.4 MVP Definition
Define the minimum version that is considered releasable.

**Template**
- The MVP MUST solve `<CORE_USER_PROBLEM>`.
- The MVP MUST include `<CRITICAL_CAPABILITIES>`.
- The MVP MUST NOT include `<DEFERRED_CAPABILITIES>`.
- The MVP is considered successful when `<SUCCESS_CONDITION>`.

---

## 5. FUNCTIONAL REQUIREMENTS

### 5.1 Functional Requirement Format
Every functional requirement SHOULD use the following structure:

- **Requirement ID**
- **Title**
- **Description**
- **Actor**
- **Preconditions**
- **Trigger**
- **Main Flow**
- **Alternative Flows**
- **Postconditions**
- **Acceptance Criteria**
- **Priority**

### 5.2 Functional Requirements List
Use one subsection per requirement.

#### FR-001 `<REQUIREMENT_TITLE>`
- **Description:** `<WHAT_THE_SYSTEM_MUST_DO>`
- **Actor:** `<ACTOR_ID_OR_ROLE>`
- **Preconditions:** `<PRECONDITIONS>`
- **Trigger:** `<TRIGGER_EVENT>`
- **Main Flow:**
  1. `<STEP_1>`
  2. `<STEP_2>`
  3. `<STEP_3>`
- **Alternative Flows:**
  - `<ALTERNATIVE_OR_EXCEPTION_FLOW>`
- **Postconditions:** `<EXPECTED_RESULT_AFTER_SUCCESS>`
- **Acceptance Criteria:**
  - `<CRITERION_1>`
  - `<CRITERION_2>`
  - `<CRITERION_3>`
- **Priority:** `Critical | High | Medium | Low`

#### FR-002 `<REQUIREMENT_TITLE>`
- **Description:** `<WHAT_THE_SYSTEM_MUST_DO>`
- **Actor:** `<ACTOR_ID_OR_ROLE>`
- **Preconditions:** `<PRECONDITIONS>`
- **Trigger:** `<TRIGGER_EVENT>`
- **Main Flow:**
  1. `<STEP_1>`
  2. `<STEP_2>`
  3. `<STEP_3>`
- **Alternative Flows:**
  - `<ALTERNATIVE_OR_EXCEPTION_FLOW>`
- **Postconditions:** `<EXPECTED_RESULT_AFTER_SUCCESS>`
- **Acceptance Criteria:**
  - `<CRITERION_1>`
  - `<CRITERION_2>`
  - `<CRITERION_3>`
- **Priority:** `Critical | High | Medium | Low`

> Duplicate the subsection pattern above for all functional requirements.

### 5.3 Functional Dependencies
State requirement relationships explicitly.

**Template**
| Requirement ID | Depends On | Dependency Type | Notes |
|----------------|-----------|-----------------|-------|
| FR-002 | FR-001 | `Hard | Soft | Sequence` | `<NOTES>` |

---

## 6. DOMAIN RULES

### 6.1 Purpose
This section defines business logic that MUST be treated as domain truth.

### 6.2 Entity Catalog
List core domain entities.

**Template**
| Entity ID | Entity Name | Description | Ownership | Lifecycle Notes |
|-----------|-------------|-------------|-----------|-----------------|
| ENT-001 | `<ENTITY_NAME>` | `<DESCRIPTION>` | `<OWNER_ROLE_OR_SYSTEM>` | `<NOTES>` |

### 6.3 Core Business Rules
Every rule SHOULD be explicit, testable, and non-ambiguous.

#### DR-001 `<RULE_TITLE>`
- **Statement:** `<EXPLICIT_RULE>`
- **Rationale:** `<WHY_THIS_RULE_EXISTS>`
- **Applies To:** `<ENTITY_OR_FLOW>`
- **Trigger Condition:** `<WHEN_THIS_RULE_APPLIES>`
- **Expected System Behavior:** `<REQUIRED_SYSTEM_BEHAVIOR>`
- **Forbidden Behavior:** `<WHAT_MUST_NOT_HAPPEN>`
- **Validation Rules:**
  - `<VALIDATION_1>`
  - `<VALIDATION_2>`
- **Failure Handling:** `<WHAT_HAPPENS_IF_RULE_IS_BROKEN>`
- **Test Implications:** `<WHAT_MUST_BE_TESTED>`

#### DR-002 `<RULE_TITLE>`
- **Statement:** `<EXPLICIT_RULE>`
- **Rationale:** `<WHY_THIS_RULE_EXISTS>`
- **Applies To:** `<ENTITY_OR_FLOW>`
- **Trigger Condition:** `<WHEN_THIS_RULE_APPLIES>`
- **Expected System Behavior:** `<REQUIRED_SYSTEM_BEHAVIOR>`
- **Forbidden Behavior:** `<WHAT_MUST_NOT_HAPPEN>`
- **Validation Rules:**
  - `<VALIDATION_1>`
  - `<VALIDATION_2>`
- **Failure Handling:** `<WHAT_HAPPENS_IF_RULE_IS_BROKEN>`
- **Test Implications:** `<WHAT_MUST_BE_TESTED>`

> Duplicate the subsection pattern above for all domain rules.

### 6.4 State Models
Define state transitions where applicable.

**Template**
| Entity | State | Allowed Transitions | Forbidden Transitions | Notes |
|--------|-------|---------------------|-----------------------|-------|
| `<ENTITY_NAME>` | `<STATE_NAME>` | `<TRANSITIONS>` | `<FORBIDDEN>` | `<NOTES>` |

### 6.5 Invariants
List conditions that MUST always remain true.

**Template**
- **INV-001:** `<INVARIANT>`
- **INV-002:** `<INVARIANT>`
- **INV-003:** `<INVARIANT>`

---

## 7. DATA AND INFORMATION REQUIREMENTS

### 7.1 Core Data Objects
Define the most important information objects.

**Template**
| Data Object | Description | Required Fields | Sensitive Data | Retention Notes |
|-------------|-------------|-----------------|----------------|-----------------|
| `<DATA_OBJECT>` | `<DESCRIPTION>` | `<FIELDS>` | `Yes | No` | `<NOTES>` |

### 7.2 Input Requirements
List required inputs and constraints.

**Template**
- All external input MUST be validated.
- Required fields for `<FLOW_OR_ENTITY>`:
  - `<FIELD_NAME>`: `<TYPE_AND_RULES>`
  - `<FIELD_NAME>`: `<TYPE_AND_RULES>`

### 7.3 Output Requirements
State expected outputs.

**Template**
- The system MUST return `<OUTPUT_TYPE>` for `<FLOW>`.
- The output MUST include `<REQUIRED_FIELDS>`.
- The output MUST NOT expose `<SENSITIVE_OR_INTERNAL_FIELDS>`.

### 7.4 Data Integrity Rules
List constraints that protect correctness.

**Template**
- **DIR-001:** `<RULE>`
- **DIR-002:** `<RULE>`
- **DIR-003:** `<RULE>`

---

## 8. NON-FUNCTIONAL REQUIREMENTS

### 8.1 Performance
**Template**
- **NFR-PERF-001:** The system MUST support `<EXPECTED_LOAD_OR_USAGE_PATTERN>`.
- **NFR-PERF-002:** The maximum acceptable response time for `<FLOW>` SHOULD be `<TARGET>`.
- **NFR-PERF-003:** Long-running operations SHOULD be handled asynchronously when appropriate.

### 8.2 Security
**Template**
- **NFR-SEC-001:** Authentication MUST be enforced for `<PROTECTED_SURFACES>`.
- **NFR-SEC-002:** Authorization MUST be role-based and deny by default.
- **NFR-SEC-003:** Sensitive data MUST be protected according to project and organizational standards.
- **NFR-SEC-004:** Audit logging MUST exist for critical actions.
- **NFR-SEC-005:** Secrets MUST NOT be stored in source code.

### 8.3 Privacy and Compliance
**Template**
- **NFR-PRV-001:** Personal data processing MUST have a lawful basis.
- **NFR-PRV-002:** Data collection MUST be limited to what is necessary.
- **NFR-PRV-003:** Data deletion, correction, or export requirements MUST be identified if applicable.
- **NFR-PRV-004:** The project MUST define whether consent is required for analytics, cookies, or communications.

### 8.4 Reliability
**Template**
- **NFR-REL-001:** The system SHOULD degrade gracefully on non-critical failures.
- **NFR-REL-002:** Critical workflows MUST have failure handling defined.
- **NFR-REL-003:** Recoverability expectations MUST be documented for operational incidents.

### 8.5 Observability
**Template**
- **NFR-OBS-001:** Critical workflows MUST emit logs with sufficient context for troubleshooting.
- **NFR-OBS-002:** Errors MUST be traceable to a request, event, or actor where applicable.
- **NFR-OBS-003:** Metrics and alerting requirements MUST be defined for high-risk flows.

### 8.6 Accessibility
**Template**
- **NFR-A11Y-001:** User-facing interfaces SHOULD meet the required accessibility target for the project.
- **NFR-A11Y-002:** Forms, navigation, and feedback states MUST be usable with assistive technologies where applicable.

### 8.7 Responsiveness
**Template**
- **NFR-RESP-001:** The application MUST support the primary target device classes.
- **NFR-RESP-002:** Mobile-first behavior SHOULD be adopted if mobile usage is significant.

### 8.8 Maintainability
**Template**
- **NFR-MNT-001:** The codebase MUST follow approved engineering standards.
- **NFR-MNT-002:** The architecture SHOULD prefer clarity and low operational complexity for MVPs.
- **NFR-MNT-003:** Any deviation from default standards SHOULD be documented in an ADR.

---

## 9. CONSTRAINTS

### 9.1 Business Constraints
**Template**
- **BC-001:** `<BUSINESS_CONSTRAINT>`
- **BC-002:** `<BUSINESS_CONSTRAINT>`

### 9.2 Technical Constraints
**Template**
- **TC-001:** `<TECHNICAL_CONSTRAINT>`
- **TC-002:** `<TECHNICAL_CONSTRAINT>`

### 9.3 Operational Constraints
**Template**
- **OC-001:** `<OPERATIONAL_CONSTRAINT>`
- **OC-002:** `<OPERATIONAL_CONSTRAINT>`

### 9.4 Legal or Compliance Constraints
**Template**
- **LC-001:** `<LEGAL_OR_COMPLIANCE_CONSTRAINT>`
- **LC-002:** `<LEGAL_OR_COMPLIANCE_CONSTRAINT>`

---

## 10. INITIAL TECHNICAL DIRECTION

### 10.1 Purpose
This section defines the initial implementation direction. It MUST guide the AI, but it MAY later be refined by ADRs or project-specific technical design documents.

### 10.2 Architecture Direction
**Template**
- **Preferred Architecture Style:** `<MODULAR_MONOLITH | MONOLITH | MICROSERVICES | OTHER>`
- **Rationale:** `<WHY_THIS_STYLE_IS_PREFERRED>`
- **System Boundaries:** `<KEY_MODULES_OR_BOUNDARIES>`
- **Explicitly Rejected Approaches:** `<APPROACHES_NOT_ALLOWED_OR_NOT_PREFERRED>`

### 10.3 Platform and Stack Direction
**Template**
| Area | Preferred Choice | Status | Notes |
|------|------------------|--------|-------|
| Frontend | `<TECH>` | `Approved | Candidate | TBD` | `<NOTES>` |
| Backend | `<TECH>` | `Approved | Candidate | TBD` | `<NOTES>` |
| Database | `<TECH>` | `Approved | Candidate | TBD` | `<NOTES>` |
| Auth | `<TECH>` | `Approved | Candidate | TBD` | `<NOTES>` |
| Hosting | `<TECH>` | `Approved | Candidate | TBD` | `<NOTES>` |
| Storage | `<TECH>` | `Approved | Candidate | TBD` | `<NOTES>` |
| Observability | `<TECH>` | `Approved | Candidate | TBD` | `<NOTES>` |

### 10.4 Integration Requirements
**Template**
- **INT-001:** `<INTEGRATION_REQUIREMENT>`
- **INT-002:** `<INTEGRATION_REQUIREMENT>`
- **INT-003:** `<INTEGRATION_REQUIREMENT>`

### 10.5 Data Model Direction
**Template**
- Core entities are expected to include `<ENTITIES>`.
- Relationships expected to exist:
  - `<ENTITY_A> -> <ENTITY_B>`
  - `<ENTITY_A> -> <ENTITY_C>`
- Sensitive records include `<DATA_TYPES>`.
- Multi-tenant behavior is `<REQUIRED | NOT_REQUIRED | TBD>`.

### 10.6 API Direction
**Template**
- The system SHOULD expose `<REST | GRAPHQL | INTERNAL_ONLY | MIXED>` interfaces.
- Public API exposure is `<YES | NO | TBD>`.
- Third-party integrations are `<NONE | REQUIRED | OPTIONAL | TBD>`.

### 10.7 Frontend Direction
**Template**
- The UI MUST prioritize `<ADMIN_WORKFLOW | MOBILE_USERS | DASHBOARD | CONSUMER_FLOW>`.
- Primary interaction model is `<FORM_HEAVY | DASHBOARD | CONTENT | GAMEPLAY | MIXED>`.
- Accessibility and responsiveness requirements apply as defined in section 8.

---

## 11. DELIVERY STRATEGY

### 11.1 Release Phases
Define delivery in phases.

**Template**
| Phase ID | Phase Name | Objective | In Scope | Exit Criteria |
|----------|------------|-----------|----------|---------------|
| PH-001 | `<PHASE_NAME>` | `<OBJECTIVE>` | `<SCOPE_SUMMARY>` | `<DONE_CONDITION>` |

### 11.2 Milestones
**Template**
- **MS-001:** `<MILESTONE>`
- **MS-002:** `<MILESTONE>`
- **MS-003:** `<MILESTONE>`

### 11.3 Priority Model
State how prioritization works.

**Template**
- `Critical`: required for MVP release or system integrity
- `High`: strong value, should be delivered early
- `Medium`: useful but deferrable
- `Low`: optional or later-phase

### 11.4 Success Criteria
Define how success is evaluated.

**Template**
- **SC-001:** `<SUCCESS_CRITERION>`
- **SC-002:** `<SUCCESS_CRITERION>`
- **SC-003:** `<SUCCESS_CRITERION>`

---

## 12. RISKS AND OPEN QUESTIONS

### 12.1 Risks
Record delivery, product, or technical risks explicitly.

**Template**
| Risk ID | Description | Impact | Likelihood | Mitigation |
|---------|-------------|--------|------------|------------|
| RSK-001 | `<RISK>` | `Low | Medium | High` | `Low | Medium | High` | `<MITIGATION>` |

### 12.2 Open Questions
State unresolved questions.

**Template**
| Question ID | Question | Owner | Status | Resolution Needed By |
|-------------|----------|-------|--------|----------------------|
| OQ-001 | `<QUESTION>` | `<OWNER>` | `Open | In Progress | Resolved` | `<DATE_OR_PHASE>` |

### 12.3 Decision Triggers
List events that require formal decisions or ADRs.

**Template**
- A new external dependency with operational impact
- A change in architecture style
- A data model decision with privacy or tenancy implications
- A major deviation from the approved engineering standards
- A cost-sensitive infrastructure choice
- A security-sensitive integration

---

## 13. TEST AND VALIDATION IMPLICATIONS

### 13.1 Testing Expectations
Describe what MUST be validated.

**Template**
- Critical domain rules MUST have automated test coverage.
- Authentication and authorization flows MUST be tested.
- High-risk workflows SHOULD have integration or end-to-end coverage.
- Edge cases identified in domain rules MUST be reflected in test cases.

### 13.2 Acceptance Validation
Map project-level validation needs.

**Template**
| Area | Validation Type | Required | Notes |
|------|------------------|----------|-------|
| `<AREA>` | `<UNIT | INTEGRATION | E2E | MANUAL | SECURITY_REVIEW>` | `Yes | No` | `<NOTES>` |

---

## 14. IMPLEMENTATION GUARDRAILS FOR AI

### 14.1 Mandatory Behavior
The AI MUST:

- Use this document as the source of truth for project intent.
- Separate functional requirements from implementation choices.
- Preserve domain rules during simplification or refactoring.
- Flag missing requirements that block safe implementation.
- State assumptions when required details are absent.
- Follow approved global standards and project ADRs.

### 14.2 Forbidden Behavior
The AI MUST NOT:

- Invent features not present in scope or requirements.
- Remove validations, authorization checks, or error handling for convenience.
- Change domain behavior without explicitly identifying the impact.
- Introduce unapproved technologies without justification.
- Blur project scope by mixing future-phase features into MVP implementation.
- Treat placeholders in this document as final facts.

### 14.3 Review Mode Guidance
When reviewing code or plans, the AI SHOULD check:

1. Does the implementation satisfy the relevant functional requirement(s)?
2. Does it respect domain rules and invariants?
3. Does it violate any non-functional requirement or constraint?
4. Does it align with the intended architecture direction?
5. Does it introduce hidden complexity or operational risk?
6. Does it require an ADR?

---

## 15. CHANGE LOG AND DECISION LOG

### 15.1 Change Log
**Template**
| Date | Version | Changed By | Summary |
|------|---------|------------|---------|
| `<YYYY-MM-DD>` | `<VERSION>` | `<NAME_OR_ROLE>` | `<CHANGE_SUMMARY>` |

### 15.2 Decision Log
Use this section for lightweight project-level decisions that do not yet justify a full ADR.

**Template**
| Decision ID | Date | Decision | Status | Notes |
|-------------|------|----------|--------|-------|
| DEC-001 | `<YYYY-MM-DD>` | `<DECISION>` | `Proposed | Approved | Rejected | Superseded` | `<NOTES>` |

---

## 16. RELATED DOCUMENTS

### 16.1 Required References
**Template**
- Global Standards Index: `<PATH_OR_LINK>`
- Security Standards: `<PATH_OR_LINK>`
- API Design Standards: `<PATH_OR_LINK>`
- Database Standards: `<PATH_OR_LINK>`
- Frontend Standards: `<PATH_OR_LINK>`
- Testing Strategy: `<PATH_OR_LINK>`
- DevOps / CI/CD Standards: `<PATH_OR_LINK>`
- ADR Index: `<PATH_OR_LINK>`

### 16.2 Optional Project-Specific Companion Documents
These documents MAY be created later if the project grows in complexity:

- `technical-design.md`
- `domain-rules-expanded.md`
- `api-contracts.md`
- `data-model.md`
- `integration-specs.md`
- `implementation-plan.md`
- `test-plan.md`

---

## 17. PROJECT MASTER COMPLETION CHECKLIST

Mark this checklist before treating the document as implementation-ready.

- [ ] Project summary is explicit and concise
- [ ] Problem statement is defined
- [ ] Product vision is clear
- [ ] Goals and non-goals are documented
- [ ] Actors, roles, and permissions are listed
- [ ] Scope is defined with explicit exclusions
- [ ] MVP is defined
- [ ] Functional requirements exist for core flows
- [ ] Domain rules are explicit and testable
- [ ] Core data requirements are documented
- [ ] Non-functional requirements are stated
- [ ] Constraints are documented
- [ ] Initial technical direction is defined
- [ ] Delivery phases or milestones are defined
- [ ] Risks and open questions are listed
- [ ] AI guardrails are present
- [ ] References to global standards are valid

---

## 18. USAGE NOTE

This document is intentionally structured to be both human-readable and AI-operable.  
It SHOULD be created early in the project lifecycle and refined before detailed technical design and implementation begin.  
It MUST remain aligned with real project decisions.  
If major project assumptions change, this document MUST be updated before implementation continues.

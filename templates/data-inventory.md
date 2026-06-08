# Data Inventory Template — Privacy & RGPD Compliance

<!--
PURPOSE:
  A copy-and-fill template for documenting all personal data processed
  by a project. This inventory is a legal requirement under RGPD/GDPR
  Article 30 (Records of Processing Activities) and a practical tool
  for maintaining privacy compliance as features evolve.

  The data inventory answers six questions for every type of personal data:
  1. WHAT personal data is collected?
  2. WHY is it collected? (legal basis)
  3. WHERE is it stored?
  4. WHO has access to it?
  5. HOW LONG is it retained?
  6. HOW is it protected?

WHEN TO USE:
  - MUST create for any project that processes personal data of individuals
    in the EU/EEA, regardless of where the application is hosted
  - MUST update when new features collect personal data
  - MUST update when third-party processors are added or changed
  - SHOULD review during every major feature release
  → See [07-security-standards.md, §14] for full RGPD requirements

WHERE TO SAVE:
  docs/data-inventory.md

RGPD APPLICABILITY:
  Under RGPD, "personal data" includes any information that can identify
  a natural person directly or indirectly: name, email, IP address, phone
  number, location data, cookie identifiers, government IDs, and more.
  If your project processes ANY of these for EU/EEA individuals, this
  inventory is required.

  Organizations with fewer than 250 employees are still required to maintain
  records if processing is not occasional, involves risk to data subjects,
  or involves special category data — which covers most web applications.

PRIVACY BY DESIGN CHECKLIST:
  For every new feature that handles personal data, verify:
  - [ ] Data minimization: only necessary fields collected
  - [ ] Legal basis identified and documented
  - [ ] Consent mechanism in place (if consent is the legal basis)
  - [ ] Data export possible (Right of Access)
  - [ ] Data deletion or anonymization possible (Right to Erasure)
  - [ ] Retention period defined
  - [ ] Encryption appropriate to classification applied
  - [ ] Access controls limit who can view this data
  - [ ] Third-party processors documented with DPAs
  - [ ] Privacy policy updated to reflect new data collection
  - [ ] Audit logging covers access to this data
  → See [07-security-standards.md, §14 — Privacy by Design Technical Checklist]

REFERENCES:
  → See [07-security-standards.md, §14] — Data Protection & Privacy (RGPD/GDPR) — full requirements,
    classification, legal basis, consent management, data subject rights, retention, processors
  → See [07-security-standards.md, §15] — Security Logging & Audit Trail — audit log retention
  → See [08-observability.md, §7.5] — Audit log retention and RGPD considerations
  → See [04-database-standards.md, §3.4] — Soft delete vs hard delete for RGPD compliance
  → RGPD/GDPR Article 30 — Records of Processing Activities (legal requirement)

AI AGENT INSTRUCTIONS:
  When using this template to create a data inventory:
  1. Copy this file to docs/data-inventory.md
  2. Fill in the project metadata section
  3. For each type of personal data the project collects, add a row to the
     Personal Data Inventory table
  4. Classify each data type using the sensitivity classification table
  5. Document all third-party processors in the Third-Party Processors table
  6. Define retention periods for each data type
  7. Remove all HTML comments (<!-- -->) from the final document
  8. Review and update this document whenever new features collect personal data
  9. Write in English — all technical documentation uses English
  10. This document may be requested by the supervisory authority (CNPD in
      Portugal) — ensure it is accurate and complete at all times
-->

---

# Data Inventory: <Project Name>

## Project Metadata

| Field                      | Value                                          |
|----------------------------|------------------------------------------------|
| **Project**                | <Project name>                                 |
| **Data Controller**        | <Legal entity responsible for data processing> |
| **Contact Email**          | <Privacy contact email>                        |
| **DPO (if applicable)**    | <Data Protection Officer name and contact>     |
| **Last Updated**           | <YYYY-MM-DD>                                   |
| **Next Scheduled Review**  | <YYYY-MM-DD — review at least quarterly>       |

<!-- DATA CONTROLLER:
  The data controller determines the purposes and means of the processing.
  For freelance projects, this is typically the client company.
  For personal projects, this is you or your company.

  DPO (Data Protection Officer):
  Required if the organization carries out large-scale systematic monitoring
  or processes special category data on a large scale. Most small projects
  do not require a DPO, but the field should be documented as "Not required"
  rather than left blank.
-->

---

## 1. Data Sensitivity Classification

<!-- Every type of personal data processed by the project MUST be classified
     into one of these sensitivity levels. The classification determines the
     minimum security controls required.
     → See [07-security-standards.md, §14 — Data Classification & Inventory] -->

| Level                | Examples                                                      | Required Controls                                                      |
|----------------------|---------------------------------------------------------------|------------------------------------------------------------------------|
| **Special Category** | Health data, biometrics, political opinions, sexual orientation, ethnicity | Explicit consent + encryption at rest + field-level encryption + strict access control |
| **High Sensitivity** | Government IDs (NIF, CC), financial data, passwords           | Encryption at rest + field-level encryption + audit log                |
| **Standard PII**     | Name, email, phone, address, date of birth                    | Encryption in transit + access control + retention limits              |
| **Pseudonymized**    | User IDs, hashed identifiers                                  | Standard security controls                                             |
| **Anonymous**        | Aggregated statistics, non-identifiable data                  | Not subject to RGPD                                                    |

---

## 2. Legal Basis Reference

<!-- Every type of personal data processing MUST have a valid legal basis.
     MUST never use "consent" when the user has no real choice — use
     "legitimate interest" or "contract" instead, as forced consent is not
     valid under RGPD.
     → See [07-security-standards.md, §14 — Legal Basis for Processing] -->

| Legal Basis              | When to Use                                                | Example                            |
|--------------------------|------------------------------------------------------------|------------------------------------|
| **Consent**              | Optional data, marketing, analytics, non-essential cookies | Newsletter signup, cookie consent  |
| **Contract**             | Data necessary to fulfill a contract or service            | Name and email to create account   |
| **Legal Obligation**     | Required by law                                            | Tax invoices, fraud prevention     |
| **Legitimate Interest**  | Business need, balanced against user rights                | Basic analytics, security logs     |

---

## 3. Personal Data Inventory

<!-- This is the core of the data inventory. Add one row for each type of
     personal data the project collects. Be specific — "user data" is not
     sufficient; break it down into specific fields.

     MUST update this table whenever a new feature collects personal data.

     AI features create personal-data flows that are easy to miss — inventory them too:
     prompts/completions sent to an LLM provider (a third-party transfer — see §4),
     embeddings derived from personal data, and agent memory persisted across sessions.
     → See [12-ai-engineering.md, §7.2].
    2b — §3, tabela: adiciona estas duas linhas logo a seguir à linha 4 (IP address):
    | 5 | <e.g., Document embeddings> | <e.g., Pseudonymized / derived> | <e.g., Legitimate interest> | <e.g., RAG retrieval over user content> | <e.g., Supabase `document_chunks` (pgvector)> | <e.g., App, owning tenant> | <e.g., With the source document> | <e.g., RLS by tenant, encryption in transit> |
    | 6 | <e.g., Agent memory> | <e.g., Standard PII (may contain anything the user said)> | <e.g., Contract> | <e.g., Assistant continuity / personalization> | <e.g., Supabase `agent_memory` table> | <e.g., App, owning principal> | <e.g., Until account deletion> | <e.g., RLS by principal, retention limits> |
    2c — §4 (Third-Party Data Processors): adiciona esta linha logo a seguir à linha do Stripe:
    | <e.g., Anthropic / OpenAI / Google> | <e.g., Prompts (+ any PII they contain) and model outputs> | <e.g., US (check region options)> | <e.g., Signed — link; prefer zero-retention / no-training terms> | <e.g., SCCs> | <e.g., LLM inference for the assistant / RAG feature> |
     MUST review this table whenever the Privacy by Design checklist
     is completed for a new feature.
-->

| # | Data Field        | Classification   | Legal Basis          | Purpose                          | Storage Location      | Who Has Access          | Retention Period               | Protection Measures                     |
|---|-------------------|------------------|----------------------|----------------------------------|-----------------------|-------------------------|--------------------------------|-----------------------------------------|
| 1 | <e.g., Full name>  | <e.g., Standard PII> | <e.g., Contract>    | <e.g., User identification>     | <e.g., Supabase `users` table> | <e.g., App, Admin> | <e.g., Until account deletion + 30 days> | <e.g., Encryption in transit, RLS> |
| 2 | <e.g., Email>      | <e.g., Standard PII> | <e.g., Contract>    | <e.g., Authentication, communication> | <e.g., Supabase `users` table> | <e.g., App, Admin> | <e.g., Until account deletion + 30 days> | <e.g., Encryption in transit, RLS> |
| 3 | <e.g., NIF>        | <e.g., High>     | <e.g., Legal obligation> | <e.g., Tax invoicing>       | <e.g., Supabase `invoices` table> | <e.g., Finance admin only> | <e.g., 7–10 years (Portuguese tax law)> | <e.g., Field-level encryption, RLS, audit log> |
| 4 | <e.g., IP address> | <e.g., Standard PII> | <e.g., Legitimate interest> | <e.g., Security logging>  | <e.g., Application logs> | <e.g., Dev team>      | <e.g., 90 days>               | <e.g., Log rotation, access restricted> |

<!-- GUIDANCE FOR EACH COLUMN:

  Data Field:
    Specific field name — not "user data" but "full name", "email", "phone", etc.

  Classification:
    One of: Special Category, High, Standard PII, Pseudonymized, Anonymous
    → See Section 1 above

  Legal Basis:
    One of: Consent, Contract, Legal Obligation, Legitimate Interest
    → See Section 2 above

  Purpose:
    Why this specific data is collected — be specific.
    BAD: "Business purposes"
    GOOD: "Required to create user account and authenticate"

  Storage Location:
    Where this data physically resides — database table, log files,
    third-party service, backups, etc.

  Who Has Access:
    Which roles or systems can access this data.
    Be specific: "Admin role via dashboard", "Application service layer",
    "Supabase service_role only"

  Retention Period:
    How long this data is kept before deletion or anonymization.
    → See Section 5 for suggested retention periods

  Protection Measures:
    What security controls protect this data — encryption, RLS, access
    control, audit logging, etc.
    Must be appropriate to the classification level.
-->

---

## 4. Third-Party Data Processors

<!-- MUST maintain a list of all third-party services that process personal
     data on behalf of the project.
     MUST ensure a Data Processing Agreement (DPA) is in place with every
     third-party processor.
     SHOULD prefer EU-based hosting and processing when possible.
     MUST document international data transfers and the legal mechanism used.
     → See [07-security-standards.md, §14 — Third-Party Data Processors] -->

| Service          | Data Shared                     | Hosting Location  | DPA Status          | Transfer Mechanism          | Purpose                       |
|------------------|---------------------------------|-------------------|---------------------|-----------------------------|-------------------------------|
| <e.g., Supabase> | <e.g., Full database content>  | <e.g., EU (Frankfurt)> | <e.g., Signed — link> | <e.g., EU hosting, no transfer> | <e.g., Database, auth, storage> |
| <e.g., Vercel>   | <e.g., Request logs, analytics> | <e.g., Global (US/EU)> | <e.g., Signed — link> | <e.g., SCCs>              | <e.g., Hosting, deployment>   |
| <e.g., Sentry>   | <e.g., Error data (may include PII)> | <e.g., US>    | <e.g., Signed — link> | <e.g., SCCs>              | <e.g., Error tracking>        |
| <e.g., Stripe>   | <e.g., Payment + customer data> | <e.g., US + EU>  | <e.g., Built-in>    | <e.g., SCCs + adequacy>    | <e.g., Payment processing>    |

<!-- COLUMNS GUIDANCE:

  DPA Status:
    - "Signed" with a link to the agreement or internal reference
    - "Built-in" for services that include DPA in their terms (e.g., Stripe)
    - "Pending" if DPA has not yet been signed (this is a compliance gap — resolve it)
    - "Not required" only for services that do not process personal data

  Transfer Mechanism (for non-EU processors):
    - SCCs: Standard Contractual Clauses
    - Adequacy decision: The country has been deemed adequate by the EU Commission
    - "EU hosting, no transfer": Data stays in the EU
    → See [07-security-standards.md, §14] for international transfer requirements
-->

---

## 5. Data Retention Schedule

<!-- MUST define retention periods for each type of personal data.
     MUST implement automated cleanup for expired data.
     MUST NOT retain personal data indefinitely "just in case".
     MUST document retention periods in the privacy policy.
     → See [07-security-standards.md, §14 — Data Retention] -->

| Data Type                  | Retention Period                | Rationale                        | Deletion Method                  |
|----------------------------|---------------------------------|----------------------------------|----------------------------------|
| Account data               | Until account deletion + 30 days grace period | Service contract duration | Soft delete → anonymization after grace period |
| Contact form submissions   | 12 months                       | Business follow-up period        | Automated hard delete            |
| Access / security logs     | 90 days – 1 year                | Security monitoring              | Automated log rotation           |
| Payment records            | 7–10 years                      | Portuguese tax law obligations   | Retain as required by law        |
| Analytics data             | 26 months (anonymized after)    | Business analysis                | Automated anonymization          |
| Marketing consent records  | Until withdrawal + 3 years      | Proof of consent                 | Retain as compliance evidence    |
| Deleted account data       | 30 days then hard delete        | Recovery window                  | Automated hard delete after grace |
| Audit trail                | 1–7 years (depends on context)  | Accountability, compliance       | Automated archival to cold storage |

<!-- Adjust this table to match the actual data types in the project.
     Remove rows that do not apply. Add rows for project-specific data types.

     DELETION METHOD options:
     - Hard delete: permanently remove from database
     - Soft delete + anonymization: set deleted_at, replace PII with placeholders
     - Automated log rotation: logs are automatically deleted after retention period
     - Automated archival: move to cold storage (not delete) for compliance
     → See [04-database-standards.md, §3.4] for soft delete vs hard delete guidance
-->

---

## 6. Data Subject Rights Implementation

<!-- The RGPD grants individuals specific rights over their data. The application
     MUST be technically capable of fulfilling each of these rights.
     → See [07-security-standards.md, §14 — Data Subject Rights] -->

| Right                          | Implementation Status | Mechanism                           | Response Time |
|--------------------------------|-----------------------|-------------------------------------|---------------|
| **Right of Access** (Art. 15)  | <Implemented / Planned / N/A> | <e.g., "Download my data" in account settings — JSON/CSV export> | 30 days |
| **Right to Rectification** (Art. 16) | <Implemented / Planned / N/A> | <e.g., Self-service profile editing> | 30 days |
| **Right to Erasure** (Art. 17) | <Implemented / Planned / N/A> | <e.g., Account deletion with 30-day grace period, then anonymization> | 30 days |
| **Right to Data Portability** (Art. 20) | <Implemented / Planned / N/A> | <e.g., JSON/CSV export of personal data> | 30 days |
| **Right to Object** (Art. 21) | <Implemented / Planned / N/A> | <e.g., Unsubscribe mechanism for marketing> | Immediate for marketing |

<!-- STATUS VALUES:
  - Implemented: The mechanism is built and working
  - Planned: Will be implemented before launch (if not yet in production)
  - N/A: Not applicable (justify why)

  NOTE: "Planned" is only acceptable for pre-production applications.
  Any production application MUST have all rights implemented.
-->

---

## 7. Consent Management

<!-- Required if any data processing is based on the "Consent" legal basis.
     → See [07-security-standards.md, §14 — Consent Management] -->

| Consent Purpose       | Mechanism                  | Granular Options           | Withdrawal Mechanism       | Record Stored |
|-----------------------|----------------------------|----------------------------|----------------------------|---------------|
| <e.g., Analytics cookies> | <e.g., Cookie consent banner> | <e.g., Analytics / Marketing / Functional> | <e.g., Cookie settings page, re-consent banner> | <e.g., consent_records table> |
| <e.g., Newsletter>   | <e.g., Checkbox on signup form> | <e.g., Single purpose>   | <e.g., Unsubscribe link in every email> | <e.g., consent_records table> |

<!-- CONSENT RULES:
  - MUST NOT load analytics, marketing, or tracking scripts before consent
  - MUST respect user's choice — if declined, no non-essential cookies set
  - Accept / Reject with equal prominence (no dark patterns)
  - MUST be able to demonstrate that consent was given (accountability)
  - Consent must be: freely given, specific, informed, and revocable
-->

---

## 8. Revision History

<!-- Track changes to this inventory for accountability and audit purposes. -->

| Date         | Author     | Change Description                                    |
|--------------|------------|-------------------------------------------------------|
| <YYYY-MM-DD> | <n>        | <e.g., Initial data inventory created>                |
| <YYYY-MM-DD> | <n>        | <e.g., Added Stripe as third-party processor>         |
| <YYYY-MM-DD> | <n>        | <e.g., Updated retention periods for audit logs>      |

# Briefing Template — Client Intake Questionnaire

<!--
PURPOSE:
  Reference version of the client-facing intake questionnaire.
  The original is maintained as a .docx file for sending to clients.
  This .md version exists so AI agents understand what information
  is collected during the briefing phase and can use it to populate
  the Project Master document.

ORIGINAL FORMAT:
  BRIEFING_INICIAL___Projeto_Website_WebApp.docx
  Maintained separately — sent to clients for filling.
  Language: Portuguese (PT) — matches the client audience.

WHEN TO USE:
  - Before creating a Project Master for a new project
  - As a reference for what information to expect from the client
  - When the AI needs to ask follow-up questions to fill gaps
  in the Project Master

WORKFLOW:
  1. Send the .docx to the client
  2. Client fills it and returns it
  3. Use the responses + this reference to create the Project Master
     (→ templates/project-master-template.md)
  4. The Project Master becomes the source of truth for the project

REFERENCES:
  → templates/project-master-template.md — The document created FROM this briefing
  → 11-project-management.md — Project lifecycle and management standards
  → 01-core-principles.md — Engineering principles that guide technical decisions

AI AGENT INSTRUCTIONS:
  When helping create a Project Master from a completed briefing:
  1. Map each briefing answer to the corresponding Project Master section
  2. Flag any gaps — sections of the Project Master that the briefing
     does not cover (these need follow-up with the client)
  3. Do NOT invent answers — if the briefing is silent on a topic,
     mark it as "TBD — requires client input" in the Project Master
  4. Transform checkbox selections into structured requirements
  5. The briefing is in Portuguese — the Project Master MUST be in English
-->

---

## Briefing Sections → Project Master Mapping

This table shows how briefing responses map to Project Master sections:

| Briefing Section | Information Collected | Maps To (Project Master) |
|------------------|-----------------------|--------------------------|
| 1. Regarding your business | Company name, sector, size, current website, contacts | §1.1 Project Summary, §2.1 Business Context |
| 2. What do you want? | Project type (website, e-commerce, backoffice, etc.), main objective | §1.2 Problem Statement, §1.3 Product Vision, §4 Scope |
| 3. Required Features | Feature checklist (basic, interactive, e-commerce, backoffice, fleet, employees, equipment) | §5 Functional Requirements, §4.1 In Scope |
| 4. Contents | Logo, brand identity, text, photos availability | §9.1 Business Constraints (content availability) |
| 5. Public and Market | B2B/B2C, geographic scope, competitors, differentiators | §3 Actors and Users, §1.3 Product Vision |
| 6. Deadline and Priorities | Timeline, key dates, main priority, maintenance preference | §9.1 Business Constraints, §11 Delivery Strategy |
| 7. Observations | Sector-specific needs, referral source, contact preferences | §12.2 Open Questions, §2.3 Validation Gaps |

---

## Briefing Content Reference

The following is the content structure of the client questionnaire
(originally in Portuguese, maintained in .docx format for client use):

### 1. About the Business
- Company name
- Sector (Commerce, Services, Food, Real Estate, Tourism, Health, Education, Technology, Other)
- Brief description (2-3 lines)
- Company size (solo, 2-5, 6-20, 21+)
- Current website status (none, have one, want to redo, want to improve)
- Contact information (name, email, phone/WhatsApp)

### 2. What Do You Need?
- Project type (multiple choice): institutional website, product catalog, online store, booking system, backoffice, landing page, blog, platform/tool, other
- Primary objective (single choice): online presence, increase sales, generate leads, facilitate bookings, automate processes, improve client communication, other

### 3. Required Features
- **Basic:** presentation pages, catalog/listing, contact form, social media integration, location/map
- **Interactive:** bookings, quotes/orders, live chat, client area (login), newsletter, reviews
- **E-commerce:** shopping cart, online payments, stock management, shipping
- **Backoffice:** content management, product/service management, orders/bookings view, client management, statistics/reports, multi-user permissions
- **Advanced Backoffice:** fleet management (inspections, insurance, maintenance, costs), employee management (data, document alerts, leave), facility/equipment management
- **Other:** multi-language, blog, gallery/portfolio, downloads, specific integrations

### 4. Content
- Logo quality status
- Brand identity / visual identity status
- Text content availability
- Photo availability

### 5. Audience and Market
- Client type: B2C, B2B, or both
- Geographic scope: local/regional, national, international
- Competitor or inspiration websites (up to 3)
- Differentiators

### 6. Timeline and Priorities
- Desired timeline: urgent (1 month), normal (2-3 months), flexible
- Important dates (Christmas, product launch, Black Friday, event)
- Top priority: beautiful design, mobile-friendly, easy to manage, fast loading, SEO, balanced
- Future maintenance preference: self-manage, ongoing support, undecided

### 7. Observations
- Sector-specific features not mentioned
- How they found the service
- Contact preference (email, phone, WhatsApp, meeting)
- Best time to contact

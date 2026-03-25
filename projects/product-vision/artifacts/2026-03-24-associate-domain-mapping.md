---
ask: "Map every associate from Cam's pricing matrix to domain objects, capabilities, channels, and read/write patterns"
created: 2026-03-24
workstream: product-vision
session: 2026-03-24-b
sources:
  - type: google-sheet
    ref: "1LhHA_PIz9zu8UvatUSIzeWBUvnjgvzAfFbfIfN6Gd9s"
    name: "Four Outcomes Product Matrix"
  - type: local
    ref: "projects/series-a/source-docs/operations/12-associate-suite.txt"
    name: "Associate Suite — 4 Engines"
  - type: local
    ref: "projects/product-vision/artifacts/context/craigs-vision.md"
    name: "Craig's Vision — The Underlying System"
---

# Associate Domain Mapping — All 48 Associates

Complete mapping of every associate from Cam's Four Outcomes Product Matrix to domain objects, capabilities, channels, and read/write patterns. This analysis identifies what the core domain model must contain and which capabilities are most reusable across associates.

---

## Domain Object Legend

These are the domain objects referenced throughout the analysis. Each associate touches a subset.

| Object | Description |
|--------|-------------|
| **Policy** | Insurance policy — LOB, coverage, limits, deductibles, effective/expiration dates, premium, carrier, status |
| **Customer** | Policyholder or insured party — contact info, demographics, relationship history, communication prefs |
| **Agent** | Insurance agent or broker — license info, appointments, book of business, agency affiliation |
| **Agency** | Insurance agency or brokerage — staff, LOBs, AMS system, carrier appointments |
| **Carrier** | Insurance carrier or program — appetite, guidelines, products, rates, authority rules |
| **Submission** | Application or submission for insurance — applicant data, requested coverage, supporting docs, status |
| **Quote** | Generated quote — premium, coverage details, carrier, effective date, expiration, status |
| **Claim** | Insurance claim — FNOL data, loss description, date of loss, claimant, status, adjuster |
| **Renewal** | Renewal event — expiring policy, new premium, rate change %, remarket flag, status |
| **Coverage** | Specific coverage within a policy — type, limit, deductible, endorsements, exclusions |
| **LOB** | Line of business — personal/commercial, specialty classification |
| **Document** | Any document — application forms, declarations, certificates, endorsements, manuals, policy forms |
| **Email** | Email message — sender, recipient, subject, body, classification, extracted intent |
| **Message** | Chat/SMS/voice message — channel, sender, content, intent, conversation thread |
| **Conversation** | Thread of messages — channel, participants, status, assigned agent, context |
| **Lead** | Inbound prospect — source, contact info, requested LOB, qualification status, score |
| **Payment** | Premium payment — amount, due date, status, method, policyholder |
| **Certificate** | Certificate of insurance — holder, insured, coverage summary, effective dates |
| **Task** | Internal work item — type, assignee, priority, status, linked objects |
| **KnowledgeBase** | Searchable knowledge corpus — policy forms, manuals, guidelines, FAQs |
| **Template** | Reusable template — email, document, workflow, application form |
| **WorkflowConfig** | Configurable workflow definition — steps, rules, triggers, branching logic |
| **Rule** | Business rule — eligibility, underwriting, compliance, routing |
| **Analytics** | Performance metrics — conversion, response time, resolution rate, revenue |
| **AuditLog** | Record of AI and human actions — timestamps, actor, action, outcome |
| **Schedule** | Calendar event — type, participants, time, linked objects |
| **ContactAttempt** | Outreach record — channel, target, time, outcome, follow-up status |

---

## Capability Legend

| Capability | Description |
|------------|-------------|
| **Extract** | Pull structured data from unstructured input (documents, emails, voice) |
| **Validate** | Check data against rules, completeness requirements, or authority limits |
| **Search** | Query knowledge bases, documents, or records |
| **Generate** | Produce text — emails, documents, summaries, proposals |
| **Route** | Direct work to the right person, team, or system |
| **Quote** | Calculate or retrieve insurance quotes |
| **Bind** | Execute policy binding |
| **Notify** | Send alerts or notifications to humans |
| **Draft** | Compose a message for human review before sending |
| **Classify** | Categorize input by type, intent, urgency, or topic |
| **Schedule** | Create or manage calendar events |
| **Enrich** | Add context to a record from external sources |
| **Score** | Assign a numeric or categorical rating |
| **Triage** | Prioritize and sort inbound work |
| **Monitor** | Watch for state changes or threshold breaches |
| **Verify** | Confirm identity, credentials, or compliance |
| **Transform** | Convert data between formats or systems |
| **Aggregate** | Combine data from multiple sources into a unified view |
| **Recommend** | Suggest an action based on analysis |
| **Enforce** | Apply deterministic rules with no override |

---

## AGENCIES — Client Retention

### 1. Care Associate
**Job:** Automated policy review scheduling and personalized client outreach

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Policy, Customer, Renewal, Coverage, Schedule, ContactAttempt, Template, Agent |
| **Reads** | Policy (all active for a customer), Customer (contact info, communication prefs, relationship history), Renewal (upcoming dates), Coverage (current coverages to review), Agent (assigned agent for the customer) |
| **Writes** | Schedule (creates review appointments), ContactAttempt (logs outreach attempts and outcomes), Task (creates follow-up tasks for agents), Message (sends personalized outreach) |
| **Capabilities** | Monitor, Schedule, Generate, Notify, Recommend |
| **Primary Channel** | Outbound (email, SMS) |
| **Secondary Channels** | Voice (outbound calls), internal (task creation for agents) |

### 2. Renewal Associate
**Job:** Reviews renewals, flags premium increases, drafts remarket emails

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Renewal, Policy, Customer, Coverage, Carrier, Quote, Email, Template, Agent, Analytics |
| **Reads** | Renewal (upcoming renewals with new vs. expiring premium), Policy (current terms), Coverage (what's insured), Carrier (current carrier details), Customer (contact info), Agent (who manages the account), Analytics (historical retention rates) |
| **Writes** | Renewal (flags with remarket recommendation, premium change %), Email (drafts remarket or review emails), Task (creates remarket tasks for agents), ContactAttempt (logs outreach) |
| **Capabilities** | Monitor, Score, Draft, Recommend, Classify, Notify |
| **Primary Channel** | Internal (agent-facing dashboard) |
| **Secondary Channels** | Email (outbound drafts) |

---

## AGENCIES — Operational Efficiency

### 3. Front Desk Associate
**Job:** Handles high-volume inbound inquiries (receptionist)

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Message, Conversation, Customer, Policy, Certificate, Claim, Document, Agent, Task |
| **Reads** | Customer (lookup by name/phone/policy number), Policy (status, details for inquiry response), Certificate (to fulfill COI requests), Claim (status for claim inquiries), Agent (to route complex issues), Document (to retrieve requested documents) |
| **Writes** | Message (responses to inquiries), Conversation (creates/updates threads), Task (creates tasks for issues requiring human follow-up), Certificate (generates COIs), ContactAttempt (logs the interaction) |
| **Capabilities** | Classify, Search, Route, Generate, Extract |
| **Primary Channel** | Voice (inbound phone) |
| **Secondary Channels** | Chat (web widget), SMS |

### 4. Inbox Associate
**Job:** Pre-drafted emails for claims/underwriting questions

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Email, Customer, Policy, Claim, Coverage, Carrier, KnowledgeBase, Template, Agent |
| **Reads** | Email (inbound emails to classify), Customer (context for response), Policy (details relevant to the question), Claim (status and details), Coverage (terms and conditions), Carrier (guidelines), KnowledgeBase (FAQ and standard responses), Template (email templates) |
| **Writes** | Email (drafts response for human review), Task (flags emails needing human attention), AuditLog (records AI draft and human edit) |
| **Capabilities** | Classify, Extract, Search, Draft, Route |
| **Primary Channel** | Email (inbound/outbound) |
| **Secondary Channels** | Internal (agent review queue) |

### 5. Intake Associate
**Job:** Automated LOB application processes

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Submission, Customer, LOB, Coverage, Document, Quote, Carrier, Template, Rule |
| **Reads** | LOB (available lines and requirements), Carrier (appetite and guidelines), Rule (eligibility criteria), Template (application forms per LOB), Customer (existing info to pre-fill) |
| **Writes** | Submission (creates new submission with extracted data), Customer (creates or updates customer record), Document (stores completed application), Quote (requests quotes from carriers) |
| **Capabilities** | Extract, Validate, Transform, Route, Generate |
| **Primary Channel** | Chat (web widget for applicants) |
| **Secondary Channels** | Voice, web portal (self-service application) |

### 6. Intake Associate for AMS
**Job:** Automatic AMS data entry

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Submission, Customer, Policy, Coverage, Document, Agent |
| **Reads** | Submission (data to enter), Customer (to match or create in AMS), Policy (to verify no duplicates), Document (source documents for data extraction) |
| **Writes** | Customer (creates/updates in AMS), Policy (creates policy records in AMS), Coverage (enters coverage details), Submission (updates status to "entered in AMS") |
| **Capabilities** | Extract, Transform, Validate, Enrich |
| **Primary Channel** | API (AMS integration) |
| **Secondary Channels** | Internal (agent notification on completion) |

### 7. Intake Associate for Claims
**Job:** Automated First Notice of Loss (FNOL)

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Claim, Policy, Customer, Coverage, Document, Carrier, Template, Agent |
| **Reads** | Policy (verify active coverage at time of loss), Customer (contact and policy info), Coverage (relevant coverage for the claim type), Carrier (claims reporting requirements), Template (FNOL form per carrier/LOB) |
| **Writes** | Claim (creates FNOL record with loss details), Document (stores completed FNOL form), Task (creates follow-up task for claims team), ContactAttempt (logs initial claim report) |
| **Capabilities** | Extract, Validate, Generate, Route, Notify |
| **Primary Channel** | Voice (inbound phone for claim reporting) |
| **Secondary Channels** | Chat (web widget), email |

### 8. Knowledge Associate
**Job:** Internal knowledge search across policy forms, manuals

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | KnowledgeBase, Document, Policy, Coverage, Carrier, LOB |
| **Reads** | KnowledgeBase (full corpus — policy forms, underwriting manuals, claims procedures, carrier guidelines), Document (specific documents matching query), Policy (context for coverage questions), Coverage (specific coverage form language), Carrier (carrier-specific guidelines), LOB (line-specific procedures) |
| **Writes** | Message (search results and answers), AuditLog (logs queries and sources used) |
| **Capabilities** | Search, Extract, Generate |
| **Primary Channel** | Internal (staff-facing chat or search interface) |
| **Secondary Channels** | None |

### 9. Ticket Associate
**Job:** Resolves routine staff inquiries

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Task, Message, KnowledgeBase, Agent, Policy, Customer, Document |
| **Reads** | Task (open tickets and their context), KnowledgeBase (answers to common questions), Policy (details for policy-related tickets), Customer (context for customer-related tickets), Document (referenced documents) |
| **Writes** | Task (updates status, adds resolution notes), Message (responds to the inquiry), AuditLog (logs resolution) |
| **Capabilities** | Classify, Search, Generate, Route |
| **Primary Channel** | Internal (ticketing system / internal chat) |
| **Secondary Channels** | None |

---

## AGENCIES — Revenue Growth

### 10. Cross-Sell Associate
**Job:** Cross-sell identification and outreach

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Policy, Customer, Coverage, LOB, Renewal, Lead, Template, Email, ContactAttempt, Quote, Agent |
| **Reads** | Policy (all policies per customer to find gaps), Customer (demographics, relationship, contact prefs), Coverage (existing coverages across all policies), LOB (available lines the customer doesn't have), Renewal (timing for cross-sell opportunities), Agent (assigned agent) |
| **Writes** | Lead (creates cross-sell opportunity), Email (drafts personalized cross-sell outreach), ContactAttempt (logs outreach), Quote (requests quotes for recommended coverages), Task (creates follow-up for agent) |
| **Capabilities** | Recommend, Score, Draft, Notify, Monitor |
| **Primary Channel** | Email (outbound personalized outreach) |
| **Secondary Channels** | SMS, internal (agent dashboard) |

### 11. Lead Associate
**Job:** Inbound web lead triage, qualification, scheduling

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Lead, Customer, LOB, Submission, Schedule, Message, Conversation, Agent, Analytics |
| **Reads** | Lead (inbound lead data), LOB (to match lead to available lines), Agent (to assign qualified leads), Analytics (lead source performance) |
| **Writes** | Lead (updates qualification status, score), Customer (creates prospect record), Submission (initiates application if qualified), Schedule (books appointments with agents), Message (responds to lead), Conversation (creates conversation thread), ContactAttempt (logs qualification interaction) |
| **Capabilities** | Classify, Score, Triage, Schedule, Generate, Route |
| **Primary Channel** | Chat (web widget) |
| **Secondary Channels** | Voice, SMS, web portal |

### 12. Dashboard Associate
**Job:** ROI performance visibility

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Analytics, Policy, Quote, Lead, Conversation, Renewal, Agent, AuditLog |
| **Reads** | Analytics (all performance metrics), Policy (bound policies for conversion tracking), Quote (quote volume and conversion), Lead (lead volume, source, qualification rates), Conversation (volume, resolution time, satisfaction), Renewal (retention rates), Agent (agent-level performance), AuditLog (AI vs. human resolution rates) |
| **Writes** | Analytics (computes and stores derived metrics) |
| **Capabilities** | Aggregate, Score, Generate |
| **Primary Channel** | Web portal (dashboard UI) |
| **Secondary Channels** | Email (scheduled reports), internal |

### 13. Strategy Studio
**Job:** Brand/tone customization

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | WorkflowConfig, Template, KnowledgeBase, Rule, Analytics |
| **Reads** | WorkflowConfig (current associate configurations), Template (existing templates), KnowledgeBase (current knowledge corpus), Rule (current business rules), Analytics (performance data to inform changes) |
| **Writes** | WorkflowConfig (updates workflow parameters), Template (creates/modifies templates), KnowledgeBase (adds/updates knowledge entries), Rule (adds/modifies business rules) |
| **Capabilities** | Transform, Validate, Generate |
| **Primary Channel** | Web portal (no-code configuration UI) |
| **Secondary Channels** | None |

---

## CARRIERS — Client Retention

### 14. Care Associate (Carrier)
**Job:** Payment monitoring, proactive policyholder contact

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Payment, Policy, Customer, ContactAttempt, Message, Template, Agent |
| **Reads** | Payment (overdue or failed payments), Policy (policy status, cancellation timeline), Customer (contact info, communication prefs), Agent (if agent-mediated), Template (outreach templates) |
| **Writes** | ContactAttempt (logs outreach for lapse prevention), Message (sends payment reminders), Task (escalates to human if payment not received), Payment (updates status after contact) |
| **Capabilities** | Monitor, Notify, Generate, Schedule |
| **Primary Channel** | Outbound (email, SMS to policyholders) |
| **Secondary Channels** | Voice (outbound calls) |

### 15. Orphan Associate
**Job:** Renewal processing for orphan/house accounts

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Renewal, Policy, Customer, Agent, Coverage, Carrier, Quote, Email, ContactAttempt, Task |
| **Reads** | Policy (orphan policies with no assigned agent), Customer (policyholder details), Renewal (upcoming renewals for orphan book), Coverage (current coverages), Carrier (renewal terms and rate changes), Agent (to find potential reassignment) |
| **Writes** | Renewal (processes renewal, updates status), Email (drafts renewal communications to policyholders), ContactAttempt (logs outreach), Task (creates reassignment or remarket tasks), Quote (generates renewal quotes) |
| **Capabilities** | Monitor, Draft, Route, Recommend, Generate |
| **Primary Channel** | Internal (automated processing) |
| **Secondary Channels** | Email (outbound to policyholders), internal (assignment dashboard) |

---

## CARRIERS — Operational Efficiency

### 16. Answer Associate
**Job:** Source of truth for dynamic info requests

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | KnowledgeBase, Document, Policy, Coverage, Carrier, LOB, Message, Conversation |
| **Reads** | KnowledgeBase (full knowledge corpus), Document (policy forms, bulletins, guidelines), Policy (specific policy details), Coverage (coverage form language), Carrier (product information), LOB (line-specific information) |
| **Writes** | Message (answers to questions), Conversation (creates/updates threads), AuditLog (logs queries and sources) |
| **Capabilities** | Search, Extract, Generate, Classify |
| **Primary Channel** | Chat (agent-facing or policyholder-facing) |
| **Secondary Channels** | Voice, web portal |

### 17. Inbox Associate (Carrier)
**Job:** Pre-drafted emails

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Email, Policy, Customer, Agent, Claim, Coverage, Carrier, KnowledgeBase, Template |
| **Reads** | Email (inbound emails), Policy (context), Customer (who is writing), Agent (who to route to if needed), Claim (claim-related context), Coverage (coverage questions), Carrier (internal guidelines), KnowledgeBase (standard responses), Template (response templates) |
| **Writes** | Email (drafts response), Task (flags for human review), AuditLog (records drafts) |
| **Capabilities** | Classify, Extract, Draft, Search, Route |
| **Primary Channel** | Email |
| **Secondary Channels** | Internal (review queue) |

### 18. Intake Associate (Carrier)
**Job:** Submission triage and data extraction

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Submission, Document, Carrier, Rule, LOB, Coverage, Agent, Quote, Analytics |
| **Reads** | Submission (inbound submissions), Document (attached ACORD forms, supplementals, loss runs), Carrier (appetite, guidelines, authority limits), Rule (eligibility and triage rules), LOB (line-specific requirements), Agent (submitting agent info) |
| **Writes** | Submission (extracts and structures data, assigns status, scores), Document (stores extracted/structured data), Task (routes to underwriter with priority), Analytics (updates submission volume metrics) |
| **Capabilities** | Extract, Validate, Classify, Triage, Score, Route |
| **Primary Channel** | Email (submissions arrive via email) |
| **Secondary Channels** | Web portal (agent portal submissions), API |

### 19. Intake Associate for Claims (Carrier)
**Job:** FNOL

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Claim, Policy, Customer, Coverage, Document, Carrier, Template, Agent |
| **Reads** | Policy (verify coverage), Customer (claimant info), Coverage (applicable coverage), Carrier (claims procedures, reserve rules), Template (FNOL forms), Agent (reporting agent info) |
| **Writes** | Claim (creates FNOL, sets initial reserve estimate), Document (stores FNOL documentation), Task (routes to adjuster), AuditLog (logs claim creation) |
| **Capabilities** | Extract, Validate, Generate, Route, Classify, Notify |
| **Primary Channel** | Voice (inbound claim calls) |
| **Secondary Channels** | Chat, email, web portal |

### 20. Knowledge Associate (Carrier)
**Job:** Internal knowledge search

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | KnowledgeBase, Document, Coverage, Carrier, LOB, Policy |
| **Reads** | KnowledgeBase (underwriting manuals, claims procedures, product guides, compliance docs), Document (specific documents), Coverage (form language), Carrier (internal guidelines), LOB (line-specific procedures), Policy (policy form references) |
| **Writes** | Message (search results), AuditLog (query log) |
| **Capabilities** | Search, Extract, Generate |
| **Primary Channel** | Internal (staff chat/search) |
| **Secondary Channels** | None |

### 21. Onboarding Associate
**Job:** Agent intake, license verification, contracting

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Agent, Agency, Carrier, Document, LOB, Rule, Task |
| **Reads** | Agent (application data, existing records), Agency (agency details), Carrier (appointment requirements, authority rules), Rule (licensing and compliance requirements), LOB (lines requiring appointment), Document (license documents, E&O certificates) |
| **Writes** | Agent (creates/updates agent record, appointment status), Document (stores verified documents), Task (creates contracting tasks, follow-ups for missing docs), AuditLog (logs verification steps) |
| **Capabilities** | Extract, Verify, Validate, Route, Notify, Transform |
| **Primary Channel** | Web portal (agent onboarding portal) |
| **Secondary Channels** | Email (follow-up for missing documents) |

### 22. Ticket Associate (Carrier)
**Job:** Staff inquiry resolution

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Task, Message, KnowledgeBase, Agent, Policy, Customer, Document, Carrier |
| **Reads** | Task (open tickets), KnowledgeBase (answers), Policy (context), Customer (context), Document (referenced docs), Carrier (internal procedures) |
| **Writes** | Task (resolves, adds notes), Message (responds), AuditLog (logs resolution) |
| **Capabilities** | Classify, Search, Generate, Route |
| **Primary Channel** | Internal (ticketing/chat) |
| **Secondary Channels** | None |

---

## CARRIERS — Revenue Growth

### 23. Growth Associate
**Job:** Direct-to-consumer qualify, quote, bind

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Lead, Customer, Submission, Quote, Policy, Coverage, LOB, Payment, Carrier, Rule, Document, Conversation |
| **Reads** | LOB (available products), Carrier (rating info, guidelines), Rule (eligibility, binding authority), Coverage (available coverage options) |
| **Writes** | Lead (captures and qualifies), Customer (creates customer record), Submission (creates application), Quote (generates quote), Policy (binds policy), Payment (processes premium), Document (generates policy documents), Conversation (full conversation record), AuditLog (complete audit trail of quote-to-bind) |
| **Capabilities** | Classify, Score, Quote, Bind, Validate, Generate, Extract |
| **Primary Channel** | Chat (consumer-facing web widget) |
| **Secondary Channels** | Voice, web portal (self-service) |

### 24. Placement Associate
**Job:** Agent portal appetite guidance

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Carrier, LOB, Rule, Coverage, Agent, Submission, KnowledgeBase, Message, Conversation |
| **Reads** | Carrier (full appetite guide — classes, territories, limits, exclusions), LOB (available lines), Rule (eligibility criteria per program), Coverage (available coverages), Agent (who is asking), KnowledgeBase (product guides, bulletins) |
| **Writes** | Message (guidance responses), Conversation (creates/updates threads), Submission (pre-qualifies or initiates submission if appetite match), AuditLog (logs guidance provided) |
| **Capabilities** | Search, Classify, Recommend, Generate, Validate |
| **Primary Channel** | Chat (embedded in agent portal) |
| **Secondary Channels** | Web portal |

### 25. Quote Associate
**Job:** Real-time POS quoting

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Quote, Submission, Customer, Coverage, LOB, Carrier, Rule, Document |
| **Reads** | Submission (application data), Customer (demographics, prior coverage), Coverage (requested coverages), LOB (line requirements), Carrier (rating tables, factors), Rule (rating rules, minimum premium, tiering) |
| **Writes** | Quote (generates and stores quote), Document (generates quote proposal document), AuditLog (logs rating factors used) |
| **Capabilities** | Quote, Validate, Generate, Extract |
| **Primary Channel** | Web portal (POS / agent portal) |
| **Secondary Channels** | API (embedded in partner systems), chat |

### 26. Risk Associate
**Job:** Coverage gap identification, proposal generation

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Policy, Coverage, Customer, LOB, Carrier, Document, Template, Quote, Renewal |
| **Reads** | Policy (all policies for a customer), Coverage (existing coverages to find gaps), Customer (demographics, industry, risk profile), LOB (available lines for gap-fill), Carrier (available products), Renewal (timing for proposals), Template (proposal templates) |
| **Writes** | Document (generates coverage gap analysis and proposal), Quote (requests quotes for gap-fill coverages), Lead (creates cross-sell/up-sell opportunity), Task (creates follow-up for agent) |
| **Capabilities** | Recommend, Score, Generate, Search, Aggregate |
| **Primary Channel** | Internal (underwriter/agent-facing analysis) |
| **Secondary Channels** | Email (sends proposals), web portal |

### 27. Strategy Studio (Carrier)
**Job:** No-code program builder

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | WorkflowConfig, Rule, Template, KnowledgeBase, LOB, Carrier, Coverage, Analytics |
| **Reads** | WorkflowConfig (existing programs), Rule (current eligibility and rating rules), Template (forms and documents), KnowledgeBase (product knowledge), LOB (line configurations), Carrier (program parameters), Analytics (program performance) |
| **Writes** | WorkflowConfig (creates/modifies program workflows), Rule (creates/modifies eligibility, rating, binding rules), Template (creates/modifies forms and documents), KnowledgeBase (updates product knowledge), LOB (configures new lines or sub-programs) |
| **Capabilities** | Transform, Validate, Generate, Enforce |
| **Primary Channel** | Web portal (no-code configuration UI) |
| **Secondary Channels** | None |

---

## DISTRIBUTION — Client Retention

### 28. Care Associate (Dist)
**Job:** Payment monitoring

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Payment, Policy, Customer, ContactAttempt, Message, Template, Agent |
| **Reads** | Payment (overdue/failed), Policy (status, cancellation timeline), Customer (contact info), Agent (assigned agent/broker), Template (outreach templates) |
| **Writes** | ContactAttempt (logs outreach), Message (payment reminders), Task (escalation), Payment (status update) |
| **Capabilities** | Monitor, Notify, Generate, Schedule |
| **Primary Channel** | Outbound (email, SMS) |
| **Secondary Channels** | Voice |

### 29. Orphan Associate (Dist)
**Job:** Orphan book management

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Renewal, Policy, Customer, Agent, Coverage, Carrier, Quote, Email, ContactAttempt, Task |
| **Reads** | Policy (orphan/unassigned policies), Customer (policyholder details), Renewal (upcoming renewals), Coverage (current coverages), Carrier (renewal terms), Agent (potential reassignment targets) |
| **Writes** | Renewal (processes renewal), Email (drafts renewal outreach), ContactAttempt (logs outreach), Task (reassignment tasks), Quote (renewal quotes) |
| **Capabilities** | Monitor, Draft, Route, Recommend, Generate |
| **Primary Channel** | Internal (automated processing) |
| **Secondary Channels** | Email (outbound), internal (assignment dashboard) |

### 30. Renewal Associate (Dist)
**Job:** Proactive renewal review

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Renewal, Policy, Customer, Coverage, Carrier, Quote, Email, Template, Agent, Analytics |
| **Reads** | Renewal (upcoming renewals), Policy (current terms and premium), Coverage (coverages up for renewal), Carrier (rate changes, appetite changes), Customer (contact info), Agent (assigned broker), Analytics (retention history) |
| **Writes** | Renewal (flags with recommendation), Email (drafts remarket/review emails), Task (creates renewal tasks), ContactAttempt (logs outreach) |
| **Capabilities** | Monitor, Score, Draft, Recommend, Classify, Notify |
| **Primary Channel** | Internal (agent dashboard) |
| **Secondary Channels** | Email (outbound) |

---

## DISTRIBUTION — Operational Efficiency

### 31. Answer Associate (Dist)
**Job:** Source of truth

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | KnowledgeBase, Document, Policy, Coverage, Carrier, LOB, Message, Conversation |
| **Reads** | KnowledgeBase (full corpus), Document (specific documents), Policy (details), Coverage (form language), Carrier (product info, appetite), LOB (line-specific info) |
| **Writes** | Message (answers), Conversation (threads), AuditLog (query log) |
| **Capabilities** | Search, Extract, Generate, Classify |
| **Primary Channel** | Chat (broker-facing or internal) |
| **Secondary Channels** | Voice, web portal |

### 32. Authority Associate
**Job:** Underwriting rules enforcement

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Rule, Submission, Quote, Coverage, Carrier, LOB, Agent, AuditLog, Policy |
| **Reads** | Rule (binding authority limits, referral triggers, compliance requirements), Submission (submission data to evaluate), Quote (quote parameters to validate), Coverage (requested coverages), Carrier (authority grants), LOB (line-specific authority rules), Agent (agent's delegated authority level) |
| **Writes** | Submission (approves, declines, or refers), Quote (validates or blocks), AuditLog (complete audit trail of every decision), Task (creates referral tasks for senior underwriter) |
| **Capabilities** | Enforce, Validate, Classify, Route, Score |
| **Primary Channel** | API (embedded in quoting/binding workflow) |
| **Secondary Channels** | Internal (referral dashboard) |

### 33. Inbox Associate (Dist)
**Job:** Pre-drafted emails

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Email, Policy, Customer, Agent, Claim, Coverage, Carrier, KnowledgeBase, Template |
| **Reads** | Email (inbound), Policy (context), Customer (who), Agent (routing), Claim (claim context), Coverage (coverage questions), Carrier (guidelines), KnowledgeBase (standard answers), Template (response templates) |
| **Writes** | Email (drafts), Task (flags for review), AuditLog (records drafts) |
| **Capabilities** | Classify, Extract, Draft, Search, Route |
| **Primary Channel** | Email |
| **Secondary Channels** | Internal (review queue) |

### 34. Intake Associate (Dist)
**Job:** Submission triage and extraction

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Submission, Document, Carrier, Rule, LOB, Coverage, Agent, Quote, Analytics |
| **Reads** | Submission (inbound), Document (ACORD forms, supplementals, loss runs), Carrier (appetite across multiple carriers), Rule (eligibility per carrier/program), LOB (requirements), Agent (submitting broker info) |
| **Writes** | Submission (structures data, assigns status, scores), Document (stores extracted data), Task (routes to underwriter), Analytics (volume metrics) |
| **Capabilities** | Extract, Validate, Classify, Triage, Score, Route |
| **Primary Channel** | Email (submission inbox) |
| **Secondary Channels** | Web portal, API |

### 35. Intake Associate for Claims (Dist)
**Job:** FNOL

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Claim, Policy, Customer, Coverage, Document, Carrier, Template, Agent |
| **Reads** | Policy (verify coverage), Customer (claimant info), Coverage (applicable coverage), Carrier (claims procedures), Template (FNOL forms), Agent (reporting broker) |
| **Writes** | Claim (creates FNOL), Document (FNOL documentation), Task (routes to adjuster), AuditLog (claim creation log) |
| **Capabilities** | Extract, Validate, Generate, Route, Classify, Notify |
| **Primary Channel** | Voice |
| **Secondary Channels** | Chat, email, web portal |

### 36. Inquiry Associate
**Job:** Broker support deflection

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Message, Conversation, KnowledgeBase, Agent, Carrier, LOB, Policy, Submission, Quote |
| **Reads** | KnowledgeBase (FAQs, product guides, procedures), Agent (broker details), Carrier (product info, appetite), LOB (line details), Policy (policy status inquiries), Submission (submission status), Quote (quote status) |
| **Writes** | Message (responses), Conversation (threads), AuditLog (deflection tracking) |
| **Capabilities** | Search, Classify, Generate, Route |
| **Primary Channel** | Chat (broker-facing) |
| **Secondary Channels** | Voice, email |

### 37. Knowledge Associate (Dist)
**Job:** Internal search

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | KnowledgeBase, Document, Coverage, Carrier, LOB, Policy |
| **Reads** | KnowledgeBase (underwriting manuals, claims procedures, product guides), Document (specific documents), Coverage (form language), Carrier (carrier-specific guidelines), LOB (line procedures), Policy (form references) |
| **Writes** | Message (search results), AuditLog (query log) |
| **Capabilities** | Search, Extract, Generate |
| **Primary Channel** | Internal (staff chat/search) |
| **Secondary Channels** | None |

### 38. Onboarding Associate (Dist)
**Job:** Agent onboarding

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Agent, Agency, Carrier, Document, LOB, Rule, Task |
| **Reads** | Agent (application data), Agency (agency info), Carrier (appointment requirements per carrier), Rule (licensing requirements), LOB (lines requiring appointment), Document (licenses, E&O certs) |
| **Writes** | Agent (creates/updates record, appointment status), Document (stores verified docs), Task (contracting tasks, missing doc follow-ups), AuditLog (verification log) |
| **Capabilities** | Extract, Verify, Validate, Route, Notify, Transform |
| **Primary Channel** | Web portal (agent onboarding portal) |
| **Secondary Channels** | Email (follow-ups) |

### 39. Ticket Associate (Dist)
**Job:** Staff inquiry resolution

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Task, Message, KnowledgeBase, Agent, Policy, Customer, Document, Carrier |
| **Reads** | Task (tickets), KnowledgeBase (answers), Policy (context), Customer (context), Document (docs), Carrier (procedures) |
| **Writes** | Task (resolves), Message (responds), AuditLog (resolution log) |
| **Capabilities** | Classify, Search, Generate, Route |
| **Primary Channel** | Internal (ticketing/chat) |
| **Secondary Channels** | None |

---

## DISTRIBUTION — Revenue Growth

### 40. Growth Associate (Dist)
**Job:** D2C qualify, quote, bind

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Lead, Customer, Submission, Quote, Policy, Coverage, LOB, Payment, Carrier, Rule, Document, Conversation |
| **Reads** | LOB (available products), Carrier (rating, guidelines), Rule (eligibility, binding authority), Coverage (options) |
| **Writes** | Lead (captures/qualifies), Customer (creates record), Submission (creates application), Quote (generates), Policy (binds), Payment (processes premium), Document (generates policy docs), Conversation (full record), AuditLog (audit trail) |
| **Capabilities** | Classify, Score, Quote, Bind, Validate, Generate, Extract |
| **Primary Channel** | Chat (consumer-facing widget) |
| **Secondary Channels** | Voice, web portal |

### 41. Placement Associate (Dist)
**Job:** Agent portal guidance

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Carrier, LOB, Rule, Coverage, Agent, Submission, KnowledgeBase, Message, Conversation |
| **Reads** | Carrier (appetite across multiple carriers), LOB (available lines), Rule (eligibility per program), Coverage (available coverages), Agent (broker info), KnowledgeBase (product guides) |
| **Writes** | Message (guidance), Conversation (threads), Submission (pre-qualifies), AuditLog (guidance log) |
| **Capabilities** | Search, Classify, Recommend, Generate, Validate |
| **Primary Channel** | Chat (agent portal) |
| **Secondary Channels** | Web portal |

### 42. Market Associate
**Job:** Submission analysis, best-fit carrier recommendation

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Submission, Carrier, Rule, LOB, Coverage, Document, Agent, Quote, Analytics |
| **Reads** | Submission (full submission data), Carrier (appetite across all available carriers), Rule (eligibility per carrier/program), LOB (line requirements), Coverage (requested coverages), Document (submission documents, loss runs), Agent (broker preferences), Analytics (historical placement rates per carrier) |
| **Writes** | Submission (adds carrier recommendations, scores per carrier), Task (routes to underwriter with recommended carrier list), Analytics (updates placement analytics) |
| **Capabilities** | Score, Recommend, Classify, Triage, Aggregate, Search |
| **Primary Channel** | Internal (underwriter-facing) |
| **Secondary Channels** | API (automated routing), email (broker notification) |

### 43. Quote & Bind Associate
**Job:** End-to-end quote-to-bind

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Submission, Quote, Policy, Customer, Coverage, LOB, Carrier, Rule, Payment, Document, Agent, Conversation, AuditLog |
| **Reads** | Submission (application data), Customer (demographics, prior coverage), Coverage (requested and available), LOB (line requirements), Carrier (rating, guidelines, authority), Rule (eligibility, rating, binding rules), Agent (submitting broker) |
| **Writes** | Quote (generates quote), Policy (binds policy), Payment (processes premium), Document (generates binder, policy documents, invoices), Submission (updates status through workflow), AuditLog (complete audit trail), Conversation (full interaction record), Customer (creates/updates record) |
| **Capabilities** | Extract, Validate, Quote, Bind, Generate, Enforce, Notify |
| **Primary Channel** | Web portal (end-to-end quoting flow) |
| **Secondary Channels** | Chat (embedded in portal), API |

### 44. Quote Associate (Dist)
**Job:** POS quoting

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Quote, Submission, Customer, Coverage, LOB, Carrier, Rule, Document |
| **Reads** | Submission (application data), Customer (demographics), Coverage (requested), LOB (requirements), Carrier (rating across multiple carriers), Rule (rating rules per carrier) |
| **Writes** | Quote (generates comparative quotes), Document (quote proposals), AuditLog (rating log) |
| **Capabilities** | Quote, Validate, Generate, Extract, Aggregate |
| **Primary Channel** | Web portal (POS) |
| **Secondary Channels** | API, chat |

### 45. Risk Associate (Dist)
**Job:** Coverage gap identification

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Policy, Coverage, Customer, LOB, Carrier, Document, Template, Quote, Renewal |
| **Reads** | Policy (all policies per customer), Coverage (existing coverages), Customer (demographics, industry, risk), LOB (available lines), Carrier (products), Renewal (timing), Template (proposal templates) |
| **Writes** | Document (gap analysis and proposal), Quote (quotes for gap-fill), Lead (cross-sell opportunity), Task (follow-up) |
| **Capabilities** | Recommend, Score, Generate, Search, Aggregate |
| **Primary Channel** | Internal (agent-facing analysis) |
| **Secondary Channels** | Email, web portal |

### 46. Submission Associate
**Job:** Eligibility triage and partner routing

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | Submission, Carrier, Rule, LOB, Coverage, Document, Agent, Analytics |
| **Reads** | Submission (inbound submission), Carrier (appetite across partner network), Rule (eligibility per carrier), LOB (line requirements), Coverage (requested coverages), Document (submission documents), Agent (submitting broker) |
| **Writes** | Submission (triage status, eligible carrier list, routing decision), Task (routes to appropriate carrier/program), Analytics (triage metrics), AuditLog (triage decision log) |
| **Capabilities** | Triage, Classify, Score, Validate, Route, Extract |
| **Primary Channel** | Email (submission inbox) |
| **Secondary Channels** | Web portal, API |

### 47. Strategy Studio (Dist)
**Job:** No-code program builder

| Dimension | Detail |
|-----------|--------|
| **Domain Objects** | WorkflowConfig, Rule, Template, KnowledgeBase, LOB, Carrier, Coverage, Analytics |
| **Reads** | WorkflowConfig (existing programs), Rule (current rules), Template (forms and docs), KnowledgeBase (product knowledge), LOB (line configurations), Carrier (program parameters), Analytics (performance) |
| **Writes** | WorkflowConfig (creates/modifies programs), Rule (creates/modifies rules), Template (creates/modifies templates), KnowledgeBase (updates knowledge), LOB (configures lines) |
| **Capabilities** | Transform, Validate, Generate, Enforce |
| **Primary Channel** | Web portal (no-code UI) |
| **Secondary Channels** | None |

---

## IN DEVELOPMENT

### 48. In-Development Associates
**Jobs:** Subrogation recovery, Policy checking, Intake qualification, Win-back campaigns, Monoline agent, Compliance audit trails, Secure data integration, E&O risk mitigation

| Associate | Domain Objects | Capabilities | Channel |
|-----------|---------------|-------------|---------|
| **Subrogation Recovery** | Claim, Policy, Coverage, Customer, Payment, Document, Carrier | Search, Extract, Score, Generate, Notify, Monitor | Internal, email |
| **Policy Checking** | Policy, Document, Coverage, Rule, Carrier, LOB | Validate, Extract, Enforce, Search, Generate | Internal (automated), API |
| **Intake Qualification** | Submission, Rule, LOB, Carrier, Coverage, Document | Triage, Validate, Score, Classify, Extract | Email, web portal, API |
| **Win-Back Campaigns** | Customer, Policy, ContactAttempt, Template, Email, Lead, Analytics | Monitor, Draft, Generate, Score, Schedule, Notify | Outbound (email, SMS, voice) |
| **Monoline Agent** | Lead, Customer, Quote, Policy, Coverage, LOB, Carrier, Payment, Rule | Classify, Quote, Bind, Validate, Generate, Extract | Chat, voice, web portal |
| **Compliance Audit Trails** | AuditLog, Policy, Quote, Claim, Submission, Rule, Agent | Aggregate, Validate, Search, Generate, Enforce | Internal (dashboard), API |
| **Secure Data Integration** | Document, Customer, Policy, Agent, Carrier | Transform, Validate, Extract, Verify | API |
| **E&O Risk Mitigation** | AuditLog, Conversation, Policy, Quote, Agent, Rule, Document | Monitor, Validate, Enforce, Search, Score, Generate | Internal (dashboard), API |

---

## FREQUENCY ANALYSIS

### Domain Object Frequency

How many of the 48 associates touch each domain object (counting in-development items individually, total = 55 associate instances).

| Rank | Domain Object | Associates Touching It | % of All Associates |
|------|--------------|----------------------|---------------------|
| 1 | **Policy** | 46 | 84% |
| 2 | **Customer** | 38 | 69% |
| 3 | **Coverage** | 37 | 67% |
| 4 | **Carrier** | 36 | 65% |
| 5 | **Document** | 35 | 64% |
| 6 | **KnowledgeBase** | 22 | 40% |
| 7 | **Agent** | 33 | 60% |
| 8 | **Submission** | 22 | 40% |
| 9 | **Rule** | 24 | 44% |
| 10 | **LOB** | 28 | 51% |
| 11 | **Quote** | 22 | 40% |
| 12 | **Email** | 16 | 29% |
| 13 | **Task** | 27 | 49% |
| 14 | **Renewal** | 11 | 20% |
| 15 | **Claim** | 10 | 18% |
| 16 | **AuditLog** | 24 | 44% |
| 17 | **Message** | 18 | 33% |
| 18 | **Conversation** | 14 | 25% |
| 19 | **Lead** | 9 | 16% |
| 20 | **Template** | 15 | 27% |
| 21 | **ContactAttempt** | 10 | 18% |
| 22 | **Payment** | 7 | 13% |
| 23 | **Analytics** | 13 | 24% |
| 24 | **WorkflowConfig** | 3 | 5% |
| 25 | **Schedule** | 3 | 5% |
| 26 | **Certificate** | 1 | 2% |
| 27 | **Agency** | 3 | 5% |

### Domain Object Tiers

**Tier 1 — Universal (>50% of associates).** These MUST be in the core domain model. Every associate implementation depends on them.

| Object | Frequency | Role in the System |
|--------|-----------|-------------------|
| Policy | 84% | The central entity. Nearly every associate reads policy data. |
| Customer | 69% | The human at the center of the insurance relationship. |
| Coverage | 67% | What's actually insured — the substance of every policy. |
| Carrier | 65% | The risk-bearing entity. Programs, appetite, and rules flow from carriers. |
| Document | 64% | The medium of the insurance industry. Everything is a document. |
| Agent | 60% | The intermediary. Associates serve agents or route work to them. |
| LOB | 51% | The classification system. Determines which rules, forms, and workflows apply. |

**Tier 2 — Frequent (25-50%).** Core to many workflows. Must be modeled but may have simpler schemas than Tier 1.

| Object | Frequency | Role in the System |
|--------|-----------|-------------------|
| Task | 49% | The internal work item. Every associate that can't fully resolve creates tasks. |
| Rule | 44% | Business logic that governs what associates can do. |
| AuditLog | 44% | The compliance backbone. Every consequential action must be logged. |
| Submission | 40% | The entry point for new business. Flows through intake, triage, quoting. |
| KnowledgeBase | 40% | The searchable brain. Shared across all knowledge and answer associates. |
| Quote | 40% | The pricing artifact. Central to all revenue-growth associates. |
| Message | 33% | The atomic unit of conversation across all channels. |
| Template | 27% | Reusable patterns for emails, documents, and workflows. |
| Conversation | 25% | Threaded interactions across all channels. |
| Email | 29% | Still the primary channel for insurance business communication. |

**Tier 3 — Specialized (<25%).** Important for specific workflows but not universal.

| Object | Frequency | Role in the System |
|--------|-----------|-------------------|
| Analytics | 24% | Derived metrics. Dashboard, Strategy Studio, and market associates. |
| Renewal | 20% | Time-triggered event. Critical for retention but scoped to that outcome. |
| Claim | 18% | Loss event. Scoped to claims intake and knowledge workflows. |
| ContactAttempt | 18% | Outreach tracking. Retention and care associates. |
| Lead | 16% | Prospect. Revenue growth entry point. |
| Payment | 13% | Financial transaction. Binding and lapse prevention. |
| WorkflowConfig | 5% | Meta-object. Only Strategy Studios write this. |
| Schedule | 5% | Calendar events. Only Care and Lead associates. |
| Agency | 5% | Organization. Only onboarding and AMS-integration associates. |
| Certificate | 2% | Insurance artifact. Only Front Desk for COI fulfillment. |

---

### Capability Frequency

How many associates use each capability.

| Rank | Capability | Associates Using It | % of All Associates |
|------|-----------|-------------------|---------------------|
| 1 | **Generate** | 43 | 78% |
| 2 | **Search** | 22 | 40% |
| 3 | **Validate** | 24 | 44% |
| 4 | **Route** | 22 | 40% |
| 5 | **Classify** | 22 | 40% |
| 6 | **Extract** | 21 | 38% |
| 7 | **Score** | 15 | 27% |
| 8 | **Notify** | 14 | 25% |
| 9 | **Draft** | 9 | 16% |
| 10 | **Recommend** | 11 | 20% |
| 11 | **Monitor** | 10 | 18% |
| 12 | **Quote** | 8 | 15% |
| 13 | **Triage** | 6 | 11% |
| 14 | **Schedule** | 4 | 7% |
| 15 | **Transform** | 5 | 9% |
| 16 | **Verify** | 3 | 5% |
| 17 | **Aggregate** | 6 | 11% |
| 18 | **Bind** | 4 | 7% |
| 19 | **Enforce** | 5 | 9% |
| 20 | **Enrich** | 1 | 2% |

### Capability Tiers

**Tier 1 — Universal Capabilities (>30%).** Every associate composition will likely need these.

| Capability | Frequency | What It Does |
|------------|-----------|-------------|
| Generate | 78% | The output capability. Almost every associate produces text — emails, messages, documents, proposals, answers. |
| Validate | 44% | The guard capability. Checking data against rules, completeness, authority limits. |
| Search | 40% | The retrieval capability. Finding information in knowledge bases, documents, records. |
| Route | 40% | The handoff capability. Directing work to the right human or system when the associate can't fully resolve. |
| Classify | 40% | The understanding capability. Categorizing input by type, intent, urgency. |
| Extract | 38% | The ingestion capability. Pulling structured data from unstructured documents, emails, voice. |

**Tier 2 — Common Capabilities (15-30%).** Needed by many but not all associates.

| Capability | Frequency | What It Does |
|------------|-----------|-------------|
| Score | 27% | Assigns priority, quality, or risk ratings. Used by triage, qualification, and analysis associates. |
| Notify | 25% | Sends alerts to humans. Used by monitoring and escalation workflows. |
| Recommend | 20% | Suggests actions. Used by retention, cross-sell, and placement associates. |
| Monitor | 18% | Watches for state changes. Used by care, renewal, and payment associates. |
| Draft | 16% | Composes for human review (subset of Generate with approval gate). Email-centric associates. |
| Quote | 15% | Insurance-specific. Calculates premium based on risk factors and rating tables. |

**Tier 3 — Specialized Capabilities (<15%).** Important for specific associate types.

| Capability | Frequency | What It Does |
|------------|-----------|-------------|
| Triage | 11% | Prioritizes and sorts inbound work. Submission and intake associates. |
| Aggregate | 11% | Combines multi-source data. Dashboard, market, and risk associates. |
| Transform | 9% | Format conversion. AMS integration, data migration. |
| Enforce | 9% | Deterministic rule application. Authority and compliance associates. |
| Schedule | 7% | Calendar management. Care and lead associates. |
| Bind | 7% | Policy issuance. Growth and quote-to-bind associates. |
| Verify | 5% | Identity/credential confirmation. Onboarding associates. |
| Enrich | 2% | External data augmentation. AMS integration. |

---

### Channel Frequency

| Channel | Associates Using As Primary | Associates Using As Secondary | Total Exposure |
|---------|---------------------------|------------------------------|---------------|
| **Internal** (staff-facing dashboard/chat/ticketing) | 16 | 11 | 27 |
| **Email** | 8 | 16 | 24 |
| **Chat** (web widget) | 8 | 10 | 18 |
| **Web Portal** (self-service UI) | 7 | 14 | 21 |
| **Voice** (phone) | 4 | 10 | 14 |
| **Outbound** (proactive email/SMS/voice) | 4 | 4 | 8 |
| **API** (system-to-system) | 2 | 10 | 12 |
| **SMS** | 0 | 5 | 5 |

---

## STRUCTURAL FINDINGS

### 1. The Policy-Coverage-Carrier Triangle

Policy, Coverage, and Carrier form an inseparable triad that appears in 65%+ of all associates. You cannot model one without the other two. This is the irreducible core of the insurance domain model.

- **Policy** contains one or more **Coverages**
- **Coverage** is underwritten by a **Carrier** under specific **Rules**
- **Carrier** offers **LOBs** with specific appetite, rating, and authority **Rules**

Every associate that does anything substantive in insurance needs to traverse this triangle.

### 2. The Document Problem

Document ranks 5th at 64% frequency, but it's qualitatively different from the other top objects. Documents are not a single entity — they are a polymorphic container:
- Application forms (ACORD 125, 126, etc.)
- Policy declarations pages
- Certificates of insurance
- Endorsements
- Loss runs
- Manuals and guides
- Proposals and quotes
- FNOL forms
- Binders

The domain model needs a Document entity with a type system, not a single flat table. Documents are both inputs (submissions, claims) and outputs (quotes, proposals, certificates).

### 3. The Knowledge Layer is Cross-Cutting

KnowledgeBase appears in 40% of associates but is unique in that it's the same knowledge serving different associates. The Care Associate, Knowledge Associate, Answer Associate, Inbox Associate, and Placement Associate all query the same underlying corpus — they just query it for different purposes through different channels.

This means the knowledge layer must be:
- Shared across all associates for a customer
- Segmentable by audience (internal staff vs. agents vs. consumers)
- Updateable via Strategy Studio without engineering

### 4. Two Distinct Workflow Patterns

**Reactive associates** (Front Desk, Inbox, Ticket, Answer, Inquiry, Knowledge): Wait for input, process it, respond. Their core loop is: Classify input -> Search for answer -> Generate response -> Route if unresolved.

**Proactive associates** (Care, Renewal, Cross-Sell, Orphan, Win-Back): Monitor for conditions, then initiate action. Their core loop is: Monitor state -> Detect trigger -> Generate outreach -> Log attempt.

The workflow engine must support both patterns: event-driven triggers for proactive associates and request-response for reactive ones.

### 5. The AuditLog is Infrastructure, Not Optional

AuditLog appears in 44% of associates — but in practice, every associate that writes to any domain object should create an audit record. Insurance is a regulated industry. The audit trail is the compliance backbone. This should be automatic infrastructure, not something each associate implements.

### 6. Associates Cluster by Capability Profile

Looking at the capability combinations, natural clusters emerge:

| Cluster | Associates | Core Capabilities | Pattern |
|---------|-----------|------------------|---------|
| **Intake/Triage** | Intake (all variants), Submission, Intake Qualification | Extract, Validate, Classify, Triage, Route | Ingest unstructured -> Structure -> Score -> Route |
| **Knowledge/Answer** | Knowledge (all), Answer (all), Inquiry | Search, Extract, Generate | Query -> Retrieve -> Synthesize |
| **Outreach/Retention** | Care (all), Renewal (all), Orphan (all), Cross-Sell, Win-Back | Monitor, Draft, Notify, Recommend | Detect trigger -> Compose message -> Send/Queue |
| **Quoting/Binding** | Growth (all), Quote (all), Quote & Bind, Monoline | Quote, Bind, Validate, Generate | Collect data -> Rate -> Present -> Bind |
| **Email Processing** | Inbox (all) | Classify, Extract, Draft, Route | Receive -> Understand -> Draft response -> Queue for review |
| **Configuration** | Strategy Studio (all) | Transform, Validate, Generate | Configure rules -> Preview -> Deploy |
| **Compliance** | Authority, Policy Checking, E&O, Audit Trails | Enforce, Validate, Score, Monitor | Evaluate -> Decide -> Log |

### 7. The Three Target Groups Are Configurations, Not Architectures

Agencies, Carriers, and Distribution share the same domain objects and capabilities. The differences are:
- **Which objects are primary** (agencies center on Customer/Policy; carriers on Submission/Program; distribution on Agent/Carrier network)
- **Which channel is primary** (agencies face consumers; carriers face agents; distribution faces both)
- **Which rules apply** (carriers have binding authority; agencies have appointments; distribution has both)

This confirms Craig's thesis: the platform is one system with customer-level configuration, not three separate products.

---

## MINIMUM VIABLE DOMAIN MODEL

Based on frequency analysis, the domain model must contain these objects to support the majority of associates:

**Must Have (Tier 1 — supports 84% of associates):**
1. Policy
2. Customer
3. Coverage
4. Carrier
5. Document
6. Agent
7. LOB

**Must Have (Tier 2 — supports next 40% of use cases):**
8. Task
9. Rule
10. AuditLog
11. Submission
12. KnowledgeBase
13. Quote
14. Message
15. Conversation

**Should Have (Tier 3 — supports specialized workflows):**
16. Email
17. Template
18. Renewal
19. Claim
20. Lead
21. Payment
22. Analytics
23. ContactAttempt
24. WorkflowConfig
25. Schedule
26. Agency
27. Certificate

**Must-Have Capabilities (supports 78% of associates):**
1. Generate
2. Validate
3. Search
4. Route
5. Classify
6. Extract

These 7 domain objects and 6 capabilities form the irreducible core. If you build only these, you can implement the skeleton of 84% of the associates in the pricing matrix. The remaining Tier 2 and Tier 3 objects extend the core for specific associate types.

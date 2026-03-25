---
ask: "What is the refined domain model after DDD classification of all entities?"
created: 2026-03-25
workstream: product-vision
session: 2026-03-24-a
sources:
  - type: analysis
    description: "DDD classification of all 70 proposed entities across 9 sub-domains"
  - type: analysis
    description: "6-test framework: identity, lifecycle, independence, references, independent change, CLI test"
  - type: analysis
    description: "Built on domain-model-research.md (5-angle validation) and associate-domain-mapping.md"
---

# Domain Model v2 — DDD-Classified

## Summary

70 proposed items → 44 Aggregate Roots + 18 Aggregate Children + 9 Value Objects + 5 Reference Tables. 7 items dropped.

Every Aggregate Root gets its own schema, state machine, API, and CLI command group.
Aggregate Children are accessed through their parent's API.
Value Objects are embedded in their parent entity.
Reference Tables have read-only APIs, seeded from industry standards or configuration.

---

## Aggregate Roots (44) — Full Entities with API/CLI

### Core Insurance (2)

**Product**
The insurance offering. "EventGuard Event GL", "BOP for Contractors", "Engagement Ring Insurance."
- Has coverages (as templates), rating config, eligible classes, territory availability, forms
- Lifecycle: created → versioned → deprecated → retired
- Owns: Coverage (template), Territory, RateTable as aggregate children
- CLI: `indemn product list/create/get/update`

**PolicyForm**
Specific insurance form with edition date, filing number, regulatory approval status.
- "ISO CG 00 01 04/13" — lives in a forms library
- Lifecycle: filed → approved → superseded → withdrawn
- Products define which forms are assembled; policies record which forms were issued
- CLI: `indemn form list/get`
- NOTE: Phase 3. Only needed when serving carriers directly.

### Risk & Parties (6)

**Contact/Party** (base identity)
Any person or organization the system interacts with. The shared identity root.
- All other party types (Insured, Agent, Carrier, etc.) are roles on a Party
- Standard ACORD pattern: Party + role-specific extensions
- CLI: `indemn contact list/create/get/update`

**Insured**
The person or business being insured. Party with Insured role.
- Has risk characteristics, loss history, risk profile
- Lifecycle: prospect → active insured → former insured
- Referenced by: Policy, Claim, Submission, Certificate
- Owns: Risk/InsuredAsset as aggregate children
- CLI: `indemn insured list/create/get/update`

**RetailAgent**
Licensed insurance professional. Party with Agent role.
- Has licenses, producer codes, carrier appointments, specialties
- Lifecycle: licensed → appointed → active → terminated
- Many-to-one with Agency. Many-to-many with Carrier (via appointments)
- CLI: `indemn agent list/create/get/update`

**Agency**
The agency organization. Organization with Agency role.
- Has locations, agents, carrier appointments, E&O coverage
- Lifecycle: established → active → merged → dissolved
- Contains RetailAgents
- CLI: `indemn agency list/create/get/update`

**Carrier**
The insurance company / risk bearer.
- Has products, appetite (as aggregate child), programs, agreements, financial ratings
- Major aggregate root — owns Appetite, co-owns Products with Program
- CLI: `indemn carrier list/get/update`

**DistributionPartner**
Non-licensed distribution entity (venue, retailer, platform). Organization with Partner role.
- Has branding config, contract terms, revenue share, performance metrics
- Lifecycle: contracted → active → suspended → terminated
- Central to Indemn's embedded insurance model
- CLI: `indemn partner list/create/get/update`

### Submission & Quoting (2-3)

**Submission**
Request for insurance — the central pre-bind entity.
- Covers both broker-submitted packages and consumer applications (type discriminator)
- Lifecycle: received → triaged → processing → quoted → bound/declined/expired
- Owns: SubmissionLine, SubmissionRequirement as aggregate children
- Contains: SituationAssessment, UnderwritingDecision as value objects
- If DTC model (EventGuard) diverges significantly from broker model, split out Application as separate thin entity that converts to Submission
- CLI: `indemn submission list/create/get/update`

**Quote**
Proposed terms and pricing from a carrier.
- Versioned per-provider. Multiple quotes per submission.
- Lifecycle: generated → presented → revised → accepted/declined/expired
- Owns: Subjectivity as aggregate children
- Contains: QuoteOption, RatingTransaction as value objects
- CLI: `indemn quote list/get`

**(Application)** — optional, only if DTC diverges
Thin consumer-facing data collection (EventGuard model).
- Converts to Submission upon completion
- Lifecycle: started → in-progress → submitted → converted
- CLI: `indemn application list/create/get`

### Policy Lifecycle (3)

**Binder**
Temporary proof of coverage between binding and policy issuance.
- Legal significance — IS proof of coverage
- Lifecycle: issued → active → superseded-by-policy → expired
- Short-lived. Some flows (EventGuard instant-issue) skip it entirely.
- CLI: `indemn binder list/get`

**Policy**
THE insurance contract. The single most important entity in the domain.
- Has policy number, effective/expiration dates, coverages (instances), premium, carrier, insured
- Lifecycle: issued → active → endorsed → renewed → cancelled/expired
- Owns: PolicyTerm, PolicyTransaction, Coverage (instances) as aggregate children
- Contains: Premium as value object fields (writtenPremium, annualPremium)
- Everything upstream leads here. Everything downstream flows from here.
- CLI: `indemn policy list/create/get/update`

**Certificate**
Certificate of Insurance. Lightweight aggregate root with its own workflow.
- Lifecycle: issued → active → expired → reissued
- References Policy but isn't part of policy's internal state
- Owns: CertificateHolder as aggregate child
- High volume in commercial lines (agencies issue hundreds/month)
- CLI: `indemn certificate list/create/get`

### Claims (2)

**Claim**
A reported loss against a policy.
- Lifecycle: reported → assigned → investigating → reserved → settled/denied → closed → reopened
- Owns: Claimant, ClaimTransaction, Reserve, SubrogationRecovery as aggregate children
- References: Policy (and specific Coverage), Incident
- CLI: `indemn claim list/create/get/update`

**Incident**
The event that triggers one or more claims.
- One incident can generate multiple claims (auto accident → liability + PD + med pay)
- Lightweight entity. Often 1:1 with Claim but the grouping matters for analytics/reinsurance.
- CLI: `indemn incident list/create/get`

### Financial (7)

**Payment**
Financial transaction. Money in or out.
- Lifecycle: pending → processing → completed/failed/refunded
- Carries Stripe transaction ID, method, amount, status, refund history
- Independent of policy state (persists for audit even if policy cancelled)
- CLI: `indemn payment list/get`

**Invoice**
Billing record. What's owed, when, by whom.
- Lifecycle: draft → issued → partially paid → paid → overdue → written off
- Contains line items, due dates, amounts
- CLI: `indemn invoice list/get/update`

**CommissionSchedule**
Rate structure defining economics. Configuration entity.
- Versioned with effective dates. Per carrier + LOB + agent type.
- 15% new HO, 12% renewal, volume bonuses, etc.
- Lifecycle: draft → active → superseded
- CLI: `indemn commission-schedule list/get/create`

**CommissionTransaction**
Individual commission earned/paid on a specific policy.
- Lifecycle: calculated → approved → paid (can be adjusted/clawed back)
- Links to policy, agent, carrier, and the CommissionSchedule that determined the rate
- Contains: CommissionSplit as value object
- CLI: `indemn commission list --agent AG-001 --status unpaid`

**RevenueShareAgreement**
Economics between Indemn, carrier, and non-licensed distribution partner.
- Legally distinct from Commission (regulatory difference for non-licensed partners)
- Lifecycle: draft → active → expired/terminated
- Contains terms, rates, effective dates, partner references
- CLI: `indemn revenue-share list/get/create`
- Cross-references: DistributionPartner (SD-2), Program (SD-8)

**PremiumTrustAccount**
Regulated fiduciary fund for premium collected.
- Commingling trust funds with operating funds is illegal in every state
- Lifecycle: opened → active → audited → closed
- NOTE: Phase 3. Needed when Indemn handles premium collection directly (EventGuard/embedded).
- CLI: `indemn trust-account get --org ABC-Agency`

**Bordereaux**
Periodic report to carriers — premium and loss data.
- Lifecycle: generating → draft → submitted → accepted/rejected → revised
- Monthly or quarterly. Carrier-specific format.
- NOTE: MGA-only. Critical for delegated authority programs.
- CLI: `indemn bordereaux list --carrier XYZ --year 2026`

### Authority & Compliance (6)

**DelegatedAuthority**
Legal agreement defining what an MGA can bind without carrier referral.
- The defining characteristic of an MGA vs. a broker
- Lifecycle: negotiated → active → renewed → suspended → terminated
- Owns: AuthorityLimit as aggregate children
- CLI: `indemn delegated-authority list/get`

**Referral**
When binding authority is exceeded, submission goes to carrier.
- Lifecycle: referred → under review → approved/declined/modified → bound or withdrawn
- Can take days/weeks. Has its own timeline independent of submission.
- CLI: `indemn referral list --status under-review`

**License**
Insurance license. Per state, per line. Compliance requirement.
- Lifecycle: applied → active → renewal due → renewed/lapsed/revoked
- Tracks CE requirements, expiration dates
- CLI: `indemn license list --entity craig --status active`

**ProducerAppointment**
Formal carrier authorization for a producer to sell their products.
- Per producer + carrier + state
- Lifecycle: requested → active → renewed → terminated
- Required before a producer can legally sell
- CLI: `indemn appointment list --agent craig --carrier hartford`

**SurplusLinesTransaction**
Surplus lines placement filing with state stamping office.
- Lifecycle: drafted → filed → accepted/rejected → tax paid
- Contains diligent search documentation, tax calculation
- NOTE: Wholesaler-specific, Phase 3.
- CLI: `indemn surplus-lines list --state TX --status pending`

**RegulatoryFiling**
Rate/form filing with state DOI.
- Lifecycle: drafted → submitted → under review → approved/disapproved/withdrawn
- SERFF tracking, filing type, effective date
- NOTE: Carrier-specific, very late scope.
- CLI: `indemn regulatory-filing list --state FL`

### Distribution & Delivery (3)

**Program**
Product offering container. "EventGuard" as a program.
- Defines what's sold, through what channels, under what rules
- Lifecycle: designed → launched → active → sunset
- Owns: ProductConfiguration as aggregate children
- CLI: `indemn program list/get/create`

**Deployment**
The operational unit of embedded insurance. Associate + ProductConfig + Partner + Surface.
- Lifecycle: configured → staging → live → paused → decommissioned
- This is what operations teams manage day-to-day
- Contains: DistributionSurface as value object (URL, widget config, embed code)
- CLI: `indemn deployment list --status live`

**CarrierAgreement**
Master contract between MGA/agency and carrier.
- Agreement type (brokerage vs. binding authority), terms, territory, LOBs, commission, reporting
- Lifecycle: negotiated → executed → active → renewed → terminated
- Contains: CommissionSplit template as aggregate child
- CLI: `indemn carrier-agreement list --carrier hartford`

### Platform (12)

**Associate**
THE AI agent. Indemn's central platform entity. The processing node.
- Has role, skills, configuration (BotConfiguration as aggregate child)
- Lifecycle: configured → testing → deployed → active → paused → retired
- Configured to operate on specific domain objects through specific channels
- Owns: BotConfiguration as aggregate child
- CLI: `indemn associate list/create/get/update`

**Skill**
Reusable capability definition. How an associate interacts with domain objects via CLI/API.
- Like Claude Code skills — documents how to use a specific capability
- Lifecycle: developed → published → versioned → deprecated
- Many-to-many with Associate. Composed into agents.
- CLI: `indemn skill list/get/create`

**Workflow**
Process definition. Configured sequence of steps.
- IMPORTANT: Split into WorkflowDefinition (template, this entity) and WorkflowExecution (running instance, separate)
- Lifecycle: designed → published → active → deprecated
- CLI: `indemn workflow list/get/create`

**Template**
Reusable content pattern for documents, emails, workflows.
- Types: document template (ACORD, COI), email template (renewal notice), workflow template
- Lifecycle: drafted → published → active → deprecated. Versioned.
- CLI: `indemn template list --type email`

**KnowledgeBase**
RAG-powered content store. Carrier guidelines, policy forms, procedures.
- Lifecycle: created → populated → published → updated → archived
- Many-to-many with Associate. Shared across agents.
- CLI: `indemn kb list/get/create`

**Organization**
The foundational tenant entity. All platform configuration is scoped here.
- Cross-cutting: scopes ALL sub-domains
- Lifecycle: onboarding → active → suspended → churned
- Owns: Project as aggregate child
- CLI: `indemn org list/get/create`

**Task**
Assignable work item. Follow up, review, approve.
- Polymorphic linking to any domain object
- Lifecycle: created → assigned → in progress → completed/cancelled
- CLI: `indemn task list --assignee craig --status open`

**Interaction**
Any communication event. Abstract conversation record across channels.
- The platform-level conversation entity
- Lifecycle: started → active → resolved → closed
- Contains messages, participants, channel, timestamps, outcome
- CLI: `indemn interaction list --associate intake-associate --date today`

**Correspondence**
Tracked business-purpose communication with deadlines and follow-up logic.
- Renewal notices, cancellation notices, info requests — all have regulatory requirements
- Lifecycle: drafted → reviewed → sent → delivered → acknowledged/bounced
- Distinct from Interaction: Correspondence has a specific business purpose and compliance implications
- CLI: `indemn correspondence list --policy P-456 --type renewal-notice`

**Document**
Any artifact. Applications, declarations, certificates, loss runs, generated PDFs.
- Polymorphic linking to any domain object
- Lifecycle: created/uploaded → processed → active → archived
- Contains file reference, type/classification, metadata, processing status
- CLI: `indemn document list --policy P-456`

**Email**
Raw email record. Channel-specific artifact for the email intelligence pipeline.
- Outlook Graph metadata, AI classification, extraction results, processing status
- Lifecycle: received → classified → processed → actioned
- Distinct from Interaction (raw channel artifact) and Correspondence (business communication)
- CLI: `indemn email list --status unprocessed`

**Draft**
AI-generated suggested communication pending human review.
- The human-in-the-loop entity. Central to Indemn's value proposition.
- Lifecycle: generated → pending review → approved/rejected/edited → sent
- Contains confidence level, draft type, suggested action
- CLI: `indemn draft list --status pending-review`

---

## Aggregate Children (18) — Accessed Through Parent

| Child | Parent | What It Is |
|---|---|---|
| Coverage (template) | Product | What coverages a product offers. Limits, deductibles, coverage forms. |
| Coverage (instance) | Policy | What coverages a specific policy has. Materialized copy from template. |
| Territory | Product/Carrier | Geographic rating zones. Different per carrier/product. |
| RateTable | Product | Versioned lookup tables of base rates. By class × territory. |
| Appetite | Carrier | What the carrier will write. Absorbs UnderwritingGuideline. Versioned. |
| SubmissionLine | Submission | Individual LOB within a multi-LOB submission. Own underwriting path. |
| SubmissionRequirement | Submission | Checklist item. Status: pending/received/waived. |
| Subjectivity | Quote | Condition that must be met before/after binding. Own lifecycle. |
| PolicyTerm | Policy | Per-renewal-period record. Own premium, coverages, conditions. |
| PolicyTransaction | Policy | Any change: endorsement, renewal, cancellation, reinstatement, audit. Type-discriminated. |
| CertificateHolder | Certificate | Party reference + holder-specific requirements. |
| Claimant | Claim | Party reference + claim-specific data (injury, relationship to loss). |
| ClaimTransaction | Claim | Financial movements: payments, reserve changes, recoveries. |
| Reserve | Claim | Estimated cost. Per-coverage, per-claimant. Adjusted over time. |
| SubrogationRecovery | Claim | Amounts pursued/recovered from third parties. Own pursuit lifecycle. |
| AuthorityLimit | DelegatedAuthority | Granular limits: per-occurrence, aggregate, premium, class, state. |
| ProductConfiguration | Program | Program customized for specific distribution context. Branding, pricing, questions. |
| BotConfiguration | Associate | Runtime config: system prompt, LLM model, tools, embedding settings. |
| Project | Organization | Workspace within an org. Contains agents, conversations. |

---

## Value Objects (9) — Embedded, No Identity

| Value Object | Lives On | What It Is |
|---|---|---|
| RatingFactor | RateTable / Quote | Named value in a rating calculation (territory factor = 1.15). |
| QuoteOption | Quote | Different limit/deductible/coverage configurations within one quote. |
| RatingTransaction | Quote | Immutable record of the rating calculation. Inputs, factors, outputs. Auditable. |
| UnderwritingDecision | Submission | Immutable record of the approve/decline/refer decision. Who, when, rationale. |
| SituationAssessment | Submission | AI-computed contextual analysis. Type, completeness, recommended action, confidence. |
| Premium | Policy / PolicyTransaction | Written premium, earned premium, premium change. Fields, not entity. |
| CommissionSplit | CommissionTransaction + CarrierAgreement | Division of commission: array of {party, percentage, amount}. |
| DistributionSurface | Deployment | Technical integration config: URL, widget type, API endpoint, embed code. |
| PaymentSchedule | Policy | Installment structure applied from PaymentPlanTemplate. Due dates, amounts. |

---

## Reference Tables (5) — Read-Only, Seeded

| Table | What It Is | Source |
|---|---|---|
| LineOfBusiness | GL, WC, Commercial Auto, Homeowners, etc. | Industry standard (ISO, NAIC) |
| ClassCode | ISO GL codes, NAICS, SIC with crosswalks | Industry standard |
| Channel | Voice, Chat, Email, Web, API, SMS | Fixed enum |
| Rule | Business logic entries. Typed: underwriting, rating, compliance, routing. Sourced: regulatory, business, carrier. Absorbs ComplianceRequirement. | Configuration + regulatory |
| PaymentPlanTemplate | 10-pay, 12-pay, pay-in-full structures | Configuration |

---

## Dropped (7)

| Item | Reason |
|---|---|
| UnderwritingGuideline | Merged into Appetite (same concern, different granularity) |
| Endorsement / Renewal / Cancellation | Merged into PolicyTransaction as types |
| LossHistory | Read model — computed from Claims data, not stored as entity |
| UnearnedPremiumReserve | Computed value — domain service with optional snapshots |
| Panel/Market | Query/view across CarrierAgreements, not an entity |
| ParameterAudit | Cross-cutting audit infrastructure (event store), not domain entity |
| Embed/DistributionSurface (as entity) | Merged into Deployment as value object |

---

## Key Architectural Decisions

### 1. Party Model
All person/organization types share a Contact/Party base identity with role-specific extensions. Standard ACORD pattern. Insured, RetailAgent, Agency, Carrier, DistributionPartner are roles on Party. Eliminates duplicate address/contact management.

### 2. PolicyTransaction Absorbs All Policy Changes
Endorsements, renewals, cancellations are types of PolicyTransaction, not separate entities. One transaction model with type discriminator. Renewal has a dual nature: PolicyTransaction on the existing policy AND potentially a new Submission for re-underwriting.

### 3. Configuration ≠ Transactions
CommissionSchedule (config) vs CommissionTransaction (event). PaymentPlanTemplate (config) vs PaymentSchedule (instance). DelegatedAuthority (config) vs policies bound under it. This pattern is consistent throughout.

### 4. Three-Layer Communication Model
- **Email**: Raw channel artifact (Outlook metadata, message ID, thread ID, attachments)
- **Interaction**: Abstract conversation record across channels (the platform-level entity)
- **Correspondence**: Business-purpose tracked communication with compliance implications

### 5. Workflow Definition/Execution Split
WorkflowDefinition is a template (Aggregate Root). WorkflowExecution is a running instance tied to a specific domain object. Separate concerns.

### 6. Domain Events for Immutable Records
RatingTransaction, UnderwritingDecision, SituationAssessment are stored as immutable value objects / domain events. Created once, never modified. Important for audit but not managed entities.

### 7. FormSchema in Core Insurance or Platform
Design-time artifact that drives both extraction and UI rendering. Belongs with Product (it defines what data a product needs) or in the Platform layer. Not in Submission & Quoting.

### 8. Underwriter is a User Role, Not a Domain Entity
Underwriting decisions reference the user who made them. The user's authority level and specialties are role attributes in identity/access management, not properties of an insurance domain entity.

---

## Phase Mapping

### Phase 1 — Foundation (minimum to deliver current associates)
**Entities:** Product, Insured, Carrier, RetailAgent, Agency, Submission, Quote, Policy, Associate, Skill, Workflow, Template, KnowledgeBase, Organization, Task, Document, Interaction
**Aggregate Children:** Coverage, SubmissionLine, PolicyTransaction, BotConfiguration
**Reference Tables:** LineOfBusiness, ClassCode, Channel, Rule
**Count:** ~17 entities + ~4 children + ~4 reference tables = ~25 things total

### Phase 2 — Middle Market Machine (financial + distribution)
**Add:** Payment, Invoice, CommissionSchedule, CommissionTransaction, Program, Deployment, CarrierAgreement, DistributionPartner, Certificate, Correspondence, Email, Draft
**Add Children:** ProductConfiguration, Subjectivity, CertificateHolder, Appetite
**Count:** ~12 more entities + ~4 children

### Phase 3 — Carrier Grade (authority + compliance + claims + deep financial)
**Add:** DelegatedAuthority, Referral, License, ProducerAppointment, SurplusLinesTransaction, RegulatoryFiling, Claim, Incident, Binder, RevenueShareAgreement, PremiumTrustAccount, Bordereaux, PolicyForm, Contact/Party (full)
**Add Children:** AuthorityLimit, Claimant, ClaimTransaction, Reserve, SubrogationRecovery, PolicyTerm, RateTable, Territory
**Count:** ~14 more entities + ~8 children

---

## Status

**DRAFT** — Passed DDD classification review. Needs validation with:
- **Ryan** — Does this match how insurance actually works? Are the party relationships right? Do the sub-domain boundaries make sense from a domain perspective?
- **Dhruv** — Can this be built? Does the Intake Manager's existing model map to the Submission/Quote/Workflow entities? What's the migration path?

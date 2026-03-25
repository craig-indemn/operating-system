---
ask: "What should the unified domain model look like, validated against every customer type and existing code?"
created: 2026-03-25
workstream: product-vision
session: 2026-03-24-a
sources:
  - type: analysis
    description: "5 parallel validation agents: retail agency, MGA/wholesaler, carrier, embedded insurance, existing codebase"
  - type: analysis
    description: "Associate-to-entity frequency mapping across all 48 associates"
  - type: codebase
    description: "Intake Manager, GIC Email Intelligence, bot-service, copilot-server, platform-v2, conversation-service models"
---

# Domain Model Research — Synthesis

## Starting Point
22 proposed entities. 5 parallel validators challenged this from: retail agency operations, MGA/wholesaler operations, carrier operations, embedded insurance distribution, and existing codebase reality.

## Verdict
The 22-entity model covered ~30-40% of what's needed. The validated model has ~70 entities across 9 sub-domains. But the architecture is designed once and built incrementally — you don't need all 70 on day one.

## The 5 Universal Findings (every validator agreed)

1. **Separate platform from domain.** Workflow, Template, Skill, KnowledgeBase are platform infrastructure. The domain model should be recognizable to an insurance professional.
2. **The policy lifecycle is the backbone.** Application → Submission → Quote → Binder → Policy → Endorsement → Renewal → Cancellation.
3. **Configuration ≠ transactions.** CommissionSchedule vs CommissionTransaction. RateTable vs RatingTransaction. DelegatedAuthority vs policies bound under it.
4. **"Customer" is the wrong abstraction.** Real entities: Insured, RetailAgent, Agency, Carrier, DistributionPartner.
5. **Financial layer is severely underdeveloped.** Premium (written vs earned), Payment, Invoice, Reserve, Commission (schedule vs transaction), Trust accounting.

## Validated Sub-Domain Model

### 1. Core Insurance (the product and what it covers)
Product, LineOfBusiness, Coverage, PolicyForm, ClassCode, Territory, RateTable, RatingFactor, Appetite, UnderwritingGuideline

### 2. Risk & Parties (who and what is involved)
Insured, Risk/InsuredAsset, Contact/Party, RetailAgent, Agency, Carrier, DistributionPartner, Underwriter

### 3. Submission & Quoting (getting to a price)
Application, Submission, SubmissionLine, SubmissionRequirement, FormSchema, Quote, QuoteOption, Subjectivity, RatingTransaction, UnderwritingDecision, SituationAssessment

### 4. Policy Lifecycle (the living contract)
Binder, Policy, PolicyTerm, PolicyTransaction, Endorsement, Renewal, Cancellation, Certificate, CertificateHolder

### 5. Claims (what happens when things go wrong)
Claim, Claimant, Incident, ClaimTransaction, Reserve, LossHistory, SubrogationRecovery

### 6. Financial (the money)
Premium (written/earned), Payment, Invoice, PaymentPlan, UnearnedPremiumReserve, CommissionSchedule, CommissionTransaction, CommissionSplit, RevenueShareAgreement, PremiumTrustAccount, Bordereaux

### 7. Authority & Compliance (the rules of the game)
DelegatedAuthority, AuthorityLimit, Referral, License, ProducerAppointment, SurplusLinesTransaction, RegulatoryFiling, ComplianceRequirement

### 8. Distribution & Delivery (how it reaches the customer)
Program, ProductConfiguration, Deployment, Panel/Market, CarrierAgreement, Embed/DistributionSurface

### 9. Platform Layer (how we automate it — separate from domain)
Associate, Skill, BotConfiguration, Workflow, Rule, Template, KnowledgeBase, Channel, Organization, Project, Task, Interaction, Correspondence, Document, Email, Draft, ParameterAudit

## What Already Exists in Code

| Entity | Where | Maturity |
|---|---|---|
| Submission | Intake Manager + GIC (INCOMPATIBLE models) | Two implementations, needs unification |
| Quote | Intake Manager (rich), EventGuard (basic) | IM is mature, EventGuard legacy |
| Carrier | GIC (good model) | Needs integration with IM |
| Agent (insurance) | GIC (good model) | GIC-specific, needs generalization |
| Email | GIC | Good model |
| Draft | GIC | Good model |
| SituationAssessment | GIC | Unique innovation |
| FormSchema | Intake Manager | Mature, drives extraction + UI |
| Workflow | Intake Manager | Mature for submission processing |
| Organization | copilot-server | Exists, needs insurance-specific fields |
| Distribution | copilot-server | Exists as widget deployments |
| BotConfiguration | copilot-server | V1 agent configs |
| KnowledgeBase | copilot-server | Thin model |
| Interaction/Request | copilot-server | Chat/voice conversations |
| Lead (→ Customer) | copilot-server | Basic, needs insurance enrichment |

**Does NOT exist in code:** Policy, Coverage, Product, Premium (standalone), Commission, Claim, Endorsement, Certificate, Binder, Insured/Risk, DelegatedAuthority, License, Payment, Invoice, Reserve, Rating, any Authority/Compliance entities.

## Associate Frequency Analysis (what the domain model must prioritize)

From mapping all 48 associates to domain entities:

**Top 7 domain objects (appear in 51%+ of associates):**
Policy (84%), Customer/Insured (69%), Coverage (67%), Carrier (65%), Document (64%), Agent (60%), LOB (51%)

**Top 6 capabilities (most reused):**
Generate (78%), Validate (44%), Search (40%), Route (40%), Classify (40%), Extract (38%)

**7 entities + 6 capabilities = 84% of the pricing matrix.**

## The Hardest Engineering Problem

Intake Manager and GIC Email Intelligence have parallel, overlapping Submission models:
- IM: 7-stage processing pipeline (received → completed), parameter flattening, FormSchema-driven
- GIC: 8-stage business lifecycle (received → closed), ball_holder tracking, situation assessment

Unifying these without breaking either system is the first concrete engineering task.

## Phasing Implication

The ~70 entities organize into 9 sub-domains. Building them incrementally:

**Phase 1 (deliver current associates):** Core Insurance (simplified), Risk & Parties, Submission & Quoting, Policy Lifecycle (basics), Platform Layer
**Phase 2 (middle market machine):** Financial, Distribution & Delivery
**Phase 3 (carrier-grade):** Authority & Compliance, Claims, deeper Financial, Rating

Each sub-domain has its own schemas, APIs, CLI commands. New sub-domains plug in without restructuring.

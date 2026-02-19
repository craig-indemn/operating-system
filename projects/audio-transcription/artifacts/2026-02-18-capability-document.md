---
ask: "What does Alliance Insurance's AI agent need to handle, and what are the acceptance criteria for building it?"
created: 2026-02-18
workstream: audio-transcription
session: 2026-02-18-b
sources:
  - type: local
    description: "2,156 call extractions from Qwen3-14B, 1,543 substantive — classified into 20 engagement types by 5 parallel Claude subagents, synthesized into per-type capability specs by 4 parallel Claude subagents"
  - type: local
    description: "engagement_types.json (20 types), classifications.jsonl (1,542 mappings), merged_digests.json (per-type analysis from 5 batches)"
---

# Alliance Insurance AI Agent: Capability Document

## Executive Summary

Alliance Insurance Services (Winston-Salem, NC) is an independent insurance agency handling ~100 missed calls per week across personal and commercial lines. Analysis of 2,156 phone call recordings (1,543 substantive) reveals 20 distinct engagement types that define what their AI agent must handle.

**Key findings:**
- **77% of calls end without resolution** (callback_needed). The single biggest value of an AI agent is closing this callback loop.
- **20+ carriers** are referenced across the calls, each with different portals, processes, and billing systems. The agent needs carrier-specific playbooks, not generic answers.
- **Payment processing is the #1 volume driver** at 8.6% — and the most automatable. Follow-up calls (8.9%) represent a systemic failure mode that proactive automation could largely eliminate.
- **Spanish-language demand** appears across multiple engagement types with only one bilingual agent currently on staff.
- **The installer/contractor niche** drives a disproportionate share of commercial volume (COIs, workers' comp, commercial specialty).

**Automation tiers:**

| Tier | Types | % of Calls | Strategy |
|------|-------|------------|----------|
| **High automation** | Follow-up, Make Payment, Document Request, Info Update | 24% | Fully handle 50-80% of these calls end-to-end |
| **Medium-high** | Coverage Mod, Coverage Question, COI, Driver Change | 10% | Handle structured intake + common cases; escalate edge cases |
| **Medium** | New Quote, Billing Question, Routing/Triage, Cancellation, Mortgage/Lender, DMV/Compliance | 40% | Handle intake + triage; automate the structured portions |
| **Low** | Renewal Review, Claims, Reinstatement, Workers' Comp, Commercial/Specialty | 26% | Structured intake + intelligent routing; human handles resolution |

**Phase 1 recommendation:** Start with the "High automation" tier (24% of call volume). These four types have structured workflows, clear resolution criteria, and the highest ROI per engineering hour.

---

## Automation Prioritization Matrix

| Engagement Type | Calls | % | Feasibility | Est. Auto % | Priority |
|-----------------|-------|---|-------------|-------------|----------|
| Follow-Up / Status Check | 139 | 8.9% | High | 50-60% | **P1** |
| Make a Payment | 135 | 8.6% | High | 70-80% | **P1** |
| Document Request | 68 | 4.2% | High | 55-65% | **P1** |
| Policy Info Update | 35 | 2.1% | High | 60% | **P1** |
| Coverage Modification | 48 | 3.1% | Medium-High | 50% | P2 |
| Coverage Question | 61 | 4.0% | Medium-High | 40-50% | P2 |
| COI Request | 34 | 2.2% | Medium-High | 50-60% | P2 |
| Driver Add/Remove | 18 | 1.1% | Medium-High | 55-65% | P2 |
| New Insurance Quote | 215 | 13.6% | Medium | 30-40% | P3 |
| Billing Question | 145 | 9.4% | Medium | 25-30% | P3 |
| Routing / Triage | 122 | 7.8% | Medium | 60% | P2 |
| Policy Cancellation | 58 | 3.8% | Medium | 40% | P3 |
| Mortgage / Lender | 41 | 2.7% | Medium | 35% | P3 |
| DMV / Compliance | 27 | 1.8% | Medium | 40-50% | P3 |
| Policy Reinstatement | 46 | 3.0% | Low-Medium | 20-25% | P4 |
| Workers' Comp Admin | 27 | 1.8% | Low-Medium | 20-30% | P4 |
| Renewal / Rate Review | 133 | 8.5% | Low | 15-20% | P4 |
| Claims Filing | 93 | 6.0% | Low | 15-20% | P4 |
| Commercial / Specialty | 28 | 1.8% | Low | 10-15% | P4 |

---

## Per-Type Capability Specifications

### 1. New Insurance Quote (215 calls, 13.6%)

**Typical Caller:** A prospective or existing customer shopping for new insurance coverage — auto, home, commercial, renters, life, or specialty (moped, jet ski, RV, food trailer). They either found Alliance through a referral, are unhappy with their current rate, or need coverage for a newly acquired asset or new business venture.

**Resolution Workflow:**
1. Greet the caller and determine what type of coverage they need (personal auto, homeowners, commercial GL/WC, specialty).
2. Collect personal information: full name, date of birth, driver's license number, current address, email, and phone number.
3. For auto: collect VIN or year/make/model, current mileage, usage type (personal/commercial), and any lienholders. Run MVR (motor vehicle report) for driving history.
4. For homeowners: collect property address, square footage, year built, construction type, roof age/material, heating type, protection class, and distance to fire hydrant. Run replacement cost estimator tool.
5. For commercial: collect business name, entity type (LLC/sole prop), EIN, years in business, employee count, annual payroll, class codes, and scope of operations.
6. Check if the caller has existing Alliance policies — bundling (auto + home) is often required by carriers and unlocks discounts.
7. Shop the quote across multiple carriers (typically 15-20): Progressive, Auto Owners, Cincinnati Insurance, National General, Penn National, Northwest Farmers, Westfield, SafeCo, Foremost, USLI, NC Grange, Hartford, Utica National, and others based on risk profile.
8. If the risk falls outside Alliance's carrier appetite (standalone liability-only auto, consignment warehouse, NC Joint Underwriting), inform the caller and refer to an appropriate agency.
9. Provide ballpark estimates if available; otherwise, set expectation for 1-2 business day turnaround for formal quotes.
10. Send quote comparison via email or text for the caller's review.
11. Schedule a follow-up call to walk through options, answer questions, and proceed to binding if the caller selects a carrier.

**Required Knowledge:**
- Multi-carrier underwriting criteria and eligibility rules (which carriers accept what risks in NC)
- Coverage types, deductible structures, and liability limit options across personal and commercial lines
- NC-specific regulations: protection class ratings, state-mandated rates, JUA policy terms
- Bundling requirements (many Alliance carriers will not write standalone auto without home/renters)
- Replacement cost estimation methodology and tools (RCE tool)
- Commercial class codes, payroll-based premium calculations, and contractor/installer insurance specifics (inland marine, GL, WC)
- Life insurance basics: term vs. whole life, diabetes and age underwriting considerations
- HOA/condo coverage under NC's 2023 Condo Act
- Specialty markets: moped, jet ski, food trailer, dealer lot, vacant property, builder's risk
- When a risk needs wholesale/surplus lines and cannot be placed through standard Alliance carriers

**Systems & Tools:**
Alliance Insurance internal quoting system, Progressive quoting system, Auto Owners portal, Cincinnati Insurance portal, National General portal, Northwest Farmers Mutual system, Penn National system, Westfield, SafeCo, USLI (Snap quoting), NC Grange, Hartford, Foremost, Utica National portals, Canopy Connect, Replacement cost estimator (RCE) tool, MVR system, E-signature platforms, Marblebox quoting tool, Email system

**Outcome Distribution:** callback_needed 76%, resolved 15%, voicemail 2%, transferred 1%

**Edge Cases & Escalation Triggers:**
- Products Alliance cannot offer: non-owners insurance, NC Joint Underwriting policies, consignment liability, standalone liability-only auto
- Florida condo insurance requiring specialist hurricane market knowledge
- Coverage lapse exceeding carrier thresholds (7-9 month gap exceeds typical 15-day max gap rule)
- Spanish-speaking callers needing transfer to Jessica (only bilingual commercial agent)
- Medicare/health insurance inquiries outside P&C scope
- Food trailer needing temporary personal policy pending LLC formation

**Automation Feasibility:** Medium (30-40% automatable)
The data-gathering phase (steps 2-5) is highly automatable — an AI agent can collect name, DOB, address, VIN, property details, and business info through structured conversation. This represents 40-50% of each call's duration. However, actual quote generation requires API access to 15+ carrier systems, many lacking programmatic interfaces. Quote presentation benefits from human judgment for nuanced coverage recommendations.

**What the AI Agent Must Do:**
- Conduct structured intake interviews that adapt questions based on coverage type
- Collect and validate all required data fields: personal info, property details, vehicle info (VIN decoding), business details including class codes and payroll
- Determine bundling eligibility and requirements before proceeding
- Identify when a risk falls outside Alliance's carrier appetite and provide referral
- Handle multi-line quote requests in a single conversation
- Set accurate turnaround time expectations (1-2 business days)
- Support Spanish-language intake conversations
- Recognize and route specialty risks to the appropriate commercial producer

---

### 2. Billing Question / Dispute (145 calls, 9.4%)

**Typical Caller:** An existing policyholder confused or upset about an unexpected charge, premium increase, payment status, missing refund, or discrepancy between expected and actual billing. Not trying to pay — wants an explanation.

**Resolution Workflow:**
1. Verify caller identity (name, policy number, or phone number on file).
2. Pull up billing history across relevant carrier portal(s).
3. Identify the specific discrepancy: compare expected vs. actual charge, timing, and payment method.
4. Diagnose root cause: NC state-mandated rate increases (7.5% homeowners hike), multi-vehicle/policy discount loss, mid-term endorsement pro-rations, workers' comp audit fees, paperless discount removal, NSF returned payments, auto-draft timing conflicts, short-rate cancellation calculations, system errors.
5. Explain the cause in plain language — translate insurance billing jargon.
6. If incorrect charge or eligible waiver, process correction.
7. If carrier-level resolution needed, call carrier or provide direct contact.
8. If refund owed, explain timeline and process.
9. Document resolution and send summary via email.

**Required Knowledge:**
- Premium calculation factors: state mandates, claims history, credit, zip code, ISO ratings, inflation guard
- How policy changes flow through to billing as pro-rated adjustments
- Multi-vehicle and multi-policy discount mechanics
- Workers' comp audit billing: non-compliance fees, audit completion requirements
- Payment plan structures: 11-pay, 12-pay, quarterly, annual pay-in-full discounts
- NSF payment handling, reinstatement fees, retry mechanisms
- Short-rate vs. pro-rata cancellation refund calculations
- Carrier-specific billing quirks: Progressive paperless discount, Auto Owners travel trailer billing, Penn National first-month vs. subsequent-month structures
- Agency bill vs. direct carrier bill distinction

**Systems & Tools:**
Progressive billing system, Auto Owners billing portal, Travelers policy portal and audit system, Penn National billing, National General portal, Cincinnati carrier system, SafeCo billing, Nationwide Commercial Lines, Ascend agency bill platform, Alliance Insurance internal billing/policy management system

**Outcome Distribution:** callback_needed 66%, resolved 27%

**Edge Cases & Escalation Triggers:**
- Workers' comp audit fees ($3,500+) hitting autopay unexpectedly
- Points consolidation after vehicle removal paradoxically increasing premium
- Deceased policyholder's bank account still being drafted
- Mortgage company escrow discrepancies

**Automation Feasibility:** Medium (25-30% automatable)
Simple lookups ("did my payment post?", "when is next payment?") are immediately automatable. Another 20-25% involve explaining standard NC rate increases with templated explanations. Remaining 45-50% require complex diagnostics.

**What the AI Agent Must Do:**
- Access billing history across Progressive, Auto Owners, Travelers, Penn National, National General, Cincinnati, SafeCo, Nationwide, and Ascend
- Identify the specific charge or discrepancy by comparing stated expectation against actual records
- Explain premium changes in plain language including NC mandates, endorsement pro-rations, discount loss mechanics
- Calculate how removing a vehicle or driver affects remaining premium (including counterintuitive increases)
- Verify payment processing status and auto-pay configuration
- Identify carrier system errors and escalate with specific context

---

### 3. Follow-Up / Status Check (139 calls, 8.9%)

**Typical Caller:** Someone who previously contacted Alliance about a quote, policy change, document request, claim, or payment and has not received the expected result. Calling back to ask "where is it?" These calls represent a failure of the prior interaction to reach completion.

**Resolution Workflow:**
1. Identify the caller and determine what prior interaction they are following up on via internal notes, email history, and CRM records.
2. Look up the status: quote approval in carrier system, endorsement processing, document generation/delivery, claim adjuster status, payment posting.
3. If complete, confirm and resend deliverable if not received.
4. If pending, explain delay reason and provide specific timeline.
5. If lost or never initiated, re-initiate and set new timeline.
6. If original agent unavailable, resolve directly or take detailed message.
7. Document in CRM so interaction chain is visible.

**Required Knowledge:**
- Internal case tracking and note systems
- Carrier processing timelines
- Email delivery troubleshooting: spam filters, junk folders, incorrect addresses, known portal redirect bugs
- Agent schedules and availability
- Quote approval workflows including underwriter escalation paths

**Systems & Tools:**
Alliance Insurance internal CRM/notes system, Email system with delivery tracking, Carrier underwriting portals (Progressive, Auto Owners, Cincinnati, Liberty Mutual, Utica National, Westfield), Conga Sign tracking, Salesforce, Alliance customer portal

**Outcome Distribution:** callback_needed 71%, resolved 19%, voicemail 4%

**Edge Cases & Escalation Triggers:**
- Quote disappeared from carrier system requiring re-quote
- Portal redirect bug (Allstate/YouTube redirect issue)
- Email filtered to junk and discarded
- Multiple follow-ups from same client indicating systemic service failure
- System issue preventing renewal due to producer code update at carrier level

**Automation Feasibility:** High (50-60% automatable) — **Highest-value automation target**
Follow-up calls exist because the system fails to proactively communicate status. An AI agent with access to carrier status APIs, internal notes, and email delivery tracking could: (a) provide real-time status via IVR or chat without requiring a human, handling 50-60% of calls; (b) proactively send status updates via text/email when milestones complete, potentially eliminating 70-80% of inbound follow-ups entirely.

**What the AI Agent Must Do:**
- Access internal notes, CRM history, and email logs to reconstruct full prior interaction chains
- Check real-time status of pending quotes across carrier underwriting portals
- Verify email delivery status and resend documents/quotes when not received
- Provide specific, time-bound commitments ("your quote will be ready by 5 PM Friday")
- Track repeat callers and flag 3+ calls about same issue for priority human escalation
- Proactively push status notifications via text and email when milestones are reached
- Handle the emotional layer: these callers are already frustrated by waiting

---

### 4. Make a Payment (135 calls, 8.6%)

**Typical Caller:** Existing policyholder ready to pay a premium by credit card, debit card, checking account, or (rarely) cashier's check. Includes one-time payments, catching up on overdue balances, monthly installments, down payments to bind new policies, and recurring auto-pay/EFT setup.

**Resolution Workflow:**
1. Verify caller identity.
2. Confirm amount due, due date, and which carrier/policy the payment applies to.
3. Collect payment method: credit/debit (card number, exp, CVV, zip + $4 processing fee disclosure) or checking account (routing + account numbers) or auto-pay setup (send authorization form via Conga Sign).
4. Navigate to correct carrier payment system: Progressive portal/secure credit card line, Auto Owners billing portal (note: Pay Now online is separate from billing system), National General portal, Penn National (EFT requires Conga Sign), Cincinnati billing, Travelers payment system, Foremost (cashier's checks payable to Foremost, not Alliance).
5. Process payment and obtain confirmation number.
6. Provide confirmation verbally and send receipt via email.
7. If auto-pay requested, initiate as separate step after immediate payment.
8. Confirm next payment date and amount.

**Required Knowledge:**
- Carrier-specific payment processing systems and quirks
- PCI-compliant card handling procedures
- EFT/ACH setup procedures per carrier
- Payment plan structures and associated discounts/fees
- Processing fee disclosure ($4 credit card fee typical)
- Grace periods for late payments by carrier
- Reinstatement payment requirements for lapsed accounts

**Systems & Tools:**
Progressive payment portal and secure credit card line, Auto Owners billing system (distinct from Pay Now/PNC online portal), National General portal, Penn National billing, Cincinnati portal, Travelers payment system, Foremost, Utica National, Liberty Mutual, Ascend agency bill platform, Conga Sign, Alliance internal payment processing, Email for receipts

**Outcome Distribution:** callback_needed 75%, resolved 21%, voicemail 4%

**Edge Cases & Escalation Triggers:**
- Third-party payment (someone paying for another person's policy)
- Payment on canceled account awaiting reinstatement
- Auto Owners Pay Now vs. billing system separation quirk
- Spanish-speaking caller making payment
- Caller using someone else's card — PCI/authorization concerns

**Automation Feasibility:** High (70-80% automatable)
Payment processing is the most automatable of all types. Structured workflow: verify identity, look up balance, collect payment, process, confirm. Phase 1 could automate simple one-time card payments (50-60% of volume) while routing EFT setup and edge cases to humans.

**What the AI Agent Must Do:**
- Process credit/debit card payments through carrier-specific portals (Progressive, Auto Owners, National General, Penn National, Cincinnati, Travelers, Foremost, Utica National, Liberty Mutual)
- Collect and securely handle card details in PCI-compliant manner
- Set up recurring ACH/EFT with routing/account numbers, send e-signature authorization forms, configure draft dates
- Disclose processing fees before charging and explain payment plan options
- Generate and deliver confirmation numbers verbally and via email/text
- Handle multi-policy payment consolidation
- Recognize when payment cannot be processed (canceled account, underwriting hold)
- Support Spanish-language payment processing

---

### 5. Renewal / Rate Review (133 calls, 8.5%)

**Typical Caller:** Existing customer who received a renewal notice showing a premium increase, or an Alliance agent proactively reaching out 30 days before renewal. Wants to understand rate changes, whether they're getting the best deal, and what options exist. Significant subset involves carriers exiting NC market (Main Street America, NGM Insurance).

**Resolution Workflow:**
1. Pull current policy details: carrier, coverage, deductibles, premium, renewal date, recent changes.
2. Identify premium change source: NC mandates (7.5% homeowners), inflation guard, ISO changes, claims history, credit changes, discount loss, telematics inactivity.
3. Explain rate change in plain language.
4. Explore cost-reduction options: increase deductibles, remove optional coverages, verify active discounts.
5. If significant increase or customer requests, reshop across carrier panel (15+ carriers).
6. If carrier non-renewing (Main Street America, NGM), proactively reshop before lapse.
7. Present comparison with specific savings figures.
8. If switching, coordinate transition: bind new policy, cancel old, migrate payment method.
9. Send renewal summary or new proposal via email.

**Required Knowledge:**
- NC state rate mandates and how they cascade through carriers
- Inflation guard endorsements and replacement cost estimators
- ISO rating system and protection class impact
- Deductible adjustment impact calculations
- Multi-carrier comparison methodology with coverage equivalency
- NC market dynamics: carrier exits, restrictions, rate filings
- Bundling discount mechanics
- Escrow payment processes
- Telematics/usage-based programs and their discount impact
- Short-rate penalties for mid-term switches

**Outcome Distribution:** callback_needed 74%, resolved 21%

**Automation Feasibility:** Low (15-20% automatable)
Core value is consultative. Competitive reshops across 10-15 carriers require deep institutional knowledge and judgment. NC market disruption adds complexity that changes quarterly.

---

### 6. Routing / Triage (122 calls, 7.8%)

**Typical Caller:** Anyone reaching the phone system — customers requesting a specific agent, Spanish-speaking callers, misdirected callers (wrong company entirely), carrier/vendor representatives, internal staff with IT issues. About half are not insurance transactions at all.

**Resolution Workflow:**
1. Identify intent: specific agent request, department, wrong number.
2. If requesting specific agent, check availability via Lightspeed Voice.
3. If available, transfer directly. If unavailable, collect callback info and estimated return time.
4. If Spanish needed, check Jessica Hernandez availability; if unavailable, arrange bilingual callback.
5. If wrong company (Alliance Insurance Company vs. Alliance Insurance Services), clarify.
6. If non-insurance (IT, food orders, medical scheduling), redirect or decline.
7. If carrier/vendor inbound, identify needed agent and transfer or message.

**Required Knowledge:**
- Complete internal staff directory: names, extensions, specialties, schedules
- Alliance Insurance Services vs. Alliance Insurance Company distinction
- Spanish-speaking agent availability
- Agency service area (NC and surrounding states; not Florida)
- Basic IT troubleshooting (browser cache, portal logins)
- myallianceinsurance.com portal URL and text support (336-786-1133)

**Systems & Tools:**
Lightspeed Voice (call routing/transfer), Voicemail system, myallianceinsurance.com, Internal agent directory/CRM, Email system

**Outcome Distribution:** callback_needed 80%, resolved 15%, transferred 3%

**Automation Feasibility:** Medium (60% automatable)
Core workflow (identify caller want, check availability, transfer or message) is highly structured. AI could also filter misdirected calls and handle Spanish routing.

---

### 7. Claims Filing & Follow-Up (93 calls, 6.0%)

**Typical Caller:** Policyholder who experienced a loss (accident, theft, property damage, weather, workplace injury) or following up on an existing claim (adjuster status, partial payment, denial). Highest emotional intensity of any type.

**Resolution Workflow:**
1. Verify identity, determine new claim vs. follow-up.
2. For new claims: collect incident details (date, time, location, damage, parties, police report).
3. Determine correct carrier and coverage type.
4. File through carrier-specific claims system (Auto Owners, Progressive, National General, Utica, Travelers, Liberty Mutual, Encova, Nationwide, Penn National, Berkeley Aspire, Universal Property Casualty).
5. Provide claim number and adjuster timeline (24-48 hours).
6. For follow-ups: look up status, escalate unresponsive adjusters.
7. For third-party claims: direct to at-fault party's carrier.

**Required Knowledge:**
- Claims filing procedures for 10+ carriers, each with different intake processes
- Coverage determination across policy types
- Subrogation rights and process
- Deductible implications and file-vs-pay guidance
- DBA vs. personal name policy structure causing lookup confusion
- NC-specific claims regulations

**Outcome Distribution:** callback_needed 72%, resolved 23%

**Automation Feasibility:** Low (15-20% automatable)
New claim intake is partially automatable, but emotional complexity, coverage determination judgment, and carrier fragmentation make this difficult. The highest emotional intensity engagement type.

---

### 8. Vehicle Add/Remove/Replace (89 calls, 5.6%)

**Typical Caller:** Policyholder who purchased, sold, traded, or totaled a vehicle. The single largest policy-change workflow by volume.

**Resolution Workflow:**
1. Verify identity, locate auto policy.
2. For additions: collect VIN (phonetic spelling via voice), year/make/model. Determine full coverage vs. liability-only. Collect lienholder info if financed.
3. Confirm effective date (NC 14-day coverage law for new vehicles, but customers need immediate proof).
4. Calculate and communicate premium impact.
5. For removals: confirm vehicle sold/totaled, verify NC plate return to DMV.
6. For replacements: match coverage from old to new vehicle.
7. Process through carrier system (Auto Owners, Progressive, National General, Farm Bureau, Cincinnati, Penn National, Safeco).
8. Email updated proof of insurance/ID cards and binder to dealership if needed.

**Required Knowledge:**
- VIN lookup and verification across carrier systems
- Coverage types and lienholder documentation requirements
- NC DMV plate return requirements and 14-day coverage law
- Pro-rated premium calculations
- Non-standard vehicle handling (jet skis, motorcycles, RVs, excavators)

**Outcome Distribution:** callback_needed 79%, resolved 19%

**Automation Feasibility:** Medium (35-40% automatable)
Straightforward additions with VIN ready and matching coverage are automatable. VIN collection via voice (17-character alphanumeric) is challenging.

---

### 9. Document Request (68 calls, 4.2%)

**Typical Caller:** Policyholder who needs a specific document delivered quickly — declaration pages, proof of insurance, ID cards, loss runs, bond copies. Usually time-sensitive (mortgage closing, job requirement, DMV deadline).

**Resolution Workflow:**
1. Verify identity, locate policy.
2. Identify specific document (callers often use wrong terminology — "deck page" for declaration page).
3. Determine delivery destination.
4. Retrieve from carrier portal (Auto Owners, National General, Progressive, Travelers, Utica National, Penn National, Safeco, Farm Bureau, USLI).
5. For loss runs: request from carrier (days, not minutes processing time).
6. For bonds: retrieve from Travelers Bond portal, may require supervisor.
7. Send via email, fax, or text.

**Required Knowledge:**
- Document types and purposes
- Carrier portal navigation for document retrieval (10+ carriers)
- E-signature platforms (Conga Sign, DocuSign)
- Legacy system workarounds
- Loss run request procedures and timelines

**Outcome Distribution:** callback_needed 64%, resolved 32% (highest first-contact resolution in this group)

**Automation Feasibility:** High (55-65% automatable)
Declaration pages, ID cards, and proof of insurance are available instantly from carrier portals. The most automatable document-related workflow.

**What the AI Agent Must Do:**
- Interpret caller requests with incorrect terminology
- Retrieve documents from 10+ carrier portals
- Initiate loss run requests with proper timeline expectations
- Send documents via email, fax, or text to callers and third parties
- Initiate e-signature workflows
- Guide callers to self-service portal access

---

### 10. Coverage Question / Clarification (61 calls, 4.0%)

**Typical Caller:** Policyholder asking "am I covered for X?" without requesting changes. Pure knowledge query about what their policy covers or excludes (windshield damage, electrical surge, towing, theft from trailer, dog liability, mold, rental car abroad).

**Resolution Workflow:**
1. Verify identity, locate policy.
2. Identify relevant coverage type.
3. Pull policy details from carrier system and review provisions.
4. If answer is clear, explain in plain language with limits, deductibles, conditions.
5. If nuanced (motor truck cargo exclusion, D&O coverage, class code applicability), consult carrier underwriting.
6. If coverage gap identified, recommend adjustments.

**Outcome Distribution:** callback_needed 69%, resolved 31%

**Automation Feasibility:** Medium-High (40-50% automatable)
Pure knowledge queries with no transactions. Common questions are answerable from policy data. Long tail of nuanced questions requires underwriting consultation. Liability risk from incorrect answers is a unique concern.

---

### 11. Policy Cancellation (58 calls, 3.8%)

**Typical Caller:** Policyholder canceling due to selling property, switching carriers, business closure, relocation, or dissatisfaction.

**Resolution Workflow:**
1. Verify identity, confirm which policies and desired effective date.
2. Explain consequences: short-rate penalties (NC auto), pro-rata refund (home/umbrella), audit obligations (commercial), DMV notification, coverage gap risks.
3. Send carrier-specific cancellation form via Conga Sign.
4. Submit signed form to carrier through appropriate portal/email channel.
5. Stop active auto-pay.
6. Confirm refund amount, method, and timeline.

**Outcome Distribution:** callback_needed 76%, resolved 19%

**Automation Feasibility:** Medium (40% automatable)
Procedural workflow, but e-signature requirement creates async break. 8+ carrier-specific form routing. Retention opportunity detection requires nuanced conversation skills.

---

### 12. Coverage Modification (48 calls, 3.1%)

**Typical Caller:** Policyholder adjusting deductibles, adding/removing coverage types, changing liability limits on existing policy.

**Resolution Workflow:**
1. Verify identity, pull relevant policy.
2. Calculate premium impact of requested change.
3. Present trade-offs (savings vs. coverage loss).
4. Process endorsement through carrier portal (Auto Owners, Progressive, National General, Cincinnati, Westfield, Foremost).
5. For commercial: verify payroll figures to avoid audit penalties.
6. For umbrella changes: verify underlying auto/home limits still meet requirements.
7. Send updated documents.

**Outcome Distribution:** callback_needed 67%, resolved 33%

**Automation Feasibility:** Medium-High (50% automatable)
Most mechanical type — deductible changes and coverage adds/removes follow predictable patterns with calculable premium impacts.

---

### 13. Policy Reinstatement (46 calls, 3.0%)

**Typical Caller:** Policyholder whose policy was canceled for non-payment. Often urgent and stressed — may have received DMV notice or discovered lapse when filing a claim.

**Resolution Workflow:**
1. Locate canceled policy, determine cancellation date and reason.
2. Check carrier-specific reinstatement window (varies: 10-60 days).
3. If within window: calculate total due, collect statement of no loss (verbal or via Conga Sign), process payment, submit reinstatement to carrier underwriting.
4. If past window: transition to new-quote workflow with pre-populated info.
5. Fix underlying payment issue to prevent recurrence.

**Required Knowledge:**
- Carrier-specific reinstatement windows (Travelers strict, may refuse after multiple cancellations)
- Statement of no loss requirements per carrier
- DMV implications of auto policy lapse
- How cascading cancellations work from a single NSF payment

**Outcome Distribution:** callback_needed 65%, resolved 30%

**Automation Feasibility:** Low-Medium (20-25% automatable)
Multi-party coordination (policyholder, agency, carrier underwriting). Carrier approval is the bottleneck.

---

### 14. Mortgage / Lender Coordination (41 calls, 2.7%)

**Typical Caller:** Either a homeowner confused about insurance/mortgage intersection (escrow increases, missing proof of insurance) or a mortgage company representative (30% of volume) confirming coverage or updating mortgagee information.

**Resolution Workflow:**
1. Distinguish policyholder vs. lender representative.
2. For policyholders: explain escrow mechanics, generate/send proof of insurance, update mortgagee clause.
3. For lender reps: confirm coverage, send evidence of insurance, process mortgagee changes.

**Outcome Distribution:** callback_needed 85% (highest in all types), resolved 15%

**Automation Feasibility:** Medium (35% automatable)
Lender confirmation calls (30% of volume) are 80%+ automatable. Policyholder escrow confusion requires explaining complex financial flows. Three-party coordination is the main blocker.

---

### 15. Policy Info Update (35 calls, 2.1%)

**Typical Caller:** Policyholder updating address, email, phone, name (divorce/marriage), DBA, or payment method.

**Resolution Workflow:**
1. Verify identity.
2. For address: update across all active policies, check if out-of-state move affects coverage, coordinate with mortgage company if homeowners.
3. For name change: collect documentation per carrier requirements.
4. For payment method: collect new banking/card details, update auto-pay across all policies.
5. Send updated documents.

**Outcome Distribution:** callback_needed 66%, resolved 34%

**Automation Feasibility:** High (60% automatable)
Most automatable type — address, phone, email, and payment method changes are all procedural.

**What the AI Agent Must Do:**
- Update address across all active policies simultaneously (auto, home, renters, umbrella, commercial)
- Navigate carrier-specific portal workflows (Auto Owners login quirk, Safeco Agent Portal forms)
- Detect when address change crosses state lines and flag for agent review
- Handle e-signature workflows for correction documentation

---

### 16. COI Request (34 calls, 2.2%)

**Typical Caller:** Contractors, installers, plumbers, steel building companies needing a certificate of insurance generated, corrected, or sent to a third party. Often under deadline pressure for a job to start.

**Resolution Workflow:**
1. Verify identity, locate commercial policy.
2. Confirm certificate holder details: company name, address, email.
3. Determine type: standard COI, additional insured endorsement, equipment-specific notation.
4. Verify policy supports requested coverage lines and amounts.
5. If DBA name needed, confirm exact wording.
6. If endorsement needed, submit to carrier and track.
7. Generate COI and email to recipient.

**Outcome Distribution:** callback_needed 74%, resolved 24%

**Automation Feasibility:** Medium-High (50-60% automatable)
Standard COI generation (no endorsement changes needed) covers 50-60% and is highly automatable. Repeat callers (same contractors) could have pre-populated details.

---

### 17. Commercial / Specialty Inquiry (28 calls, 1.8%)

**Typical Caller:** Business owners seeking coverage for non-standard risks — builder's risk, bonds, HOA/condo, dealer lots, church programs, life/health, liquor liability.

**Automation Feasibility:** Low (10-15% automatable)
Least automatable type. Core value is consultative underwriting judgment. AI agent's best role is structured intake and intelligent triage to the right specialist.

---

### 18. DMV / Compliance (27 calls, 1.8%)

**Typical Caller:** Policyholder who received NC DMV notice about plate revocation or FS-1 requirement, usually triggered by a carrier switch.

**Resolution Workflow:**
1. Identify DMV notice type and vehicle(s) referenced.
2. Verify coverage history across carriers.
3. Determine cause: carrier switch (false lapse), actual gap, vehicle removal, data error.
4. If FS-1 needed: submit electronically through carrier verification department.
5. If genuine gap: calculate duration and inform about fines ($50/vehicle in NC).
6. For DOT setup: guide through FMCSA website.

**Outcome Distribution:** callback_needed 67%, resolved 33%

**Automation Feasibility:** Medium (40-50% automatable)
Predictable pattern (verify coverage, file FS-1) covers 40-50%. Judgment calls about genuine gaps and multi-carrier situations require humans.

---

### 19. Workers' Comp Administration (27 calls, 1.8%)

**Typical Caller:** Small business owners dealing with WC audit issues, ghost policies, class code disputes, or new WC quotes.

**Resolution Workflow:**
1. Locate WC policy and identify carrier (Travelers, AmTrust, Builders Mutual, etc.).
2. For audits: explain lifecycle, guide to carrier audit portal (travelers.com/audit), explain required documentation (payroll, 940/941 tax forms, subcontractor certificates).
3. For ghost policies: explain purpose ($1,500 deposit via NC Rate Bureau), audit obligations even with zero payroll.
4. For class code changes: verify correct codes, coordinate with carrier.
5. For new quotes: gather payroll estimates by class code.

**Required Knowledge:**
- WC audit lifecycle, non-compliance fees, collections escalation
- NC Rate Bureau ghost policy procedures ($1,500 standard)
- Class code system for different trades
- Subcontractor classification rules
- Sole proprietor WC ineligibility in NC

**Outcome Distribution:** callback_needed 70%, resolved 30%

**Automation Feasibility:** Low-Medium (20-30% automatable)
Most specialized knowledge domain. AI value is structured intake and proactive audit deadline notifications.

---

### 20. Driver Add/Remove (18 calls, 1.1%)

**Typical Caller:** Parent adding teenage child (15-18) to auto policy — before permit, after permit, or upon full license. Smaller subset: removing drivers who moved out, married, or deceased.

**Resolution Workflow:**
1. Verify identity, locate auto policy.
2. For minors without license: add as household member, no premium change.
3. For permit holders: confirm already covered under parent's policy (NC rule).
4. For newly licensed: add as rated driver, explain 8-year NC inexperienced operator surcharge, run MVR.
5. For removals: confirm reason, coordinate across all policies (auto, umbrella), process across carriers.

**Outcome Distribution:** callback_needed 72%, resolved 28%

**Automation Feasibility:** Medium-High (55-65% automatable)
Common patterns (adding household members, confirming permit coverage) are zero-judgment transactions. Premium impact calculations and MVR checks are the main blockers.

---

## Cross-Cutting Requirements

### Carrier System Integration
The calls reference 20+ carriers: Progressive, Auto Owners, National General, Travelers, Cincinnati, Westfield, Penn National, Safeco/Liberty Mutual, Foremost, USLI, NC Grange, AmTrust, Utica, Hartford, Builders Mutual, Farm Bureau, Honeycomb, Encova, Nationwide, Berkeley Aspire, Universal Property Casualty. Each has different portals, billing systems, claims workflows, and endorsement processes. The AI agent needs carrier-specific playbooks — a critical long-term investment.

### Multi-Intent Handling
Many calls involve 2-3 distinct requests bundled together: "cancel insurance on totaled car AND add new car," "make a payment AND update my address AND ask about coverage." The agent must handle multi-intent conversations gracefully, completing each request before moving to the next.

### Spanish Language Support
20+ calls explicitly needed Spanish, with several more from callers with limited English. Only one bilingual commercial agent (Jessica) on staff. An AI agent with Spanish capability immediately expands capacity across all engagement types.

### Repeat Caller Recognition
Same people call multiple times as situations evolve. Conversation history and continuity is critical. The agent should recognize returning callers and reference prior interactions.

### NC Market Disruption
Carriers exiting NC (Main Street America, NGM Insurance), non-renewing policies, and significant rate increases create waves of reshop/rewrite activity. The AI agent needs current market intelligence that updates quarterly.

### Third-Party Caller Handling
~5% of calls are FROM carriers, lenders, inspectors, mortgage companies, or other agencies — not customers. The agent must handle B2C and B2B interactions with different protocols.

### The Installer/Contractor Niche
Large portion of commercial calls involve steel building installers, carport installers, and similar contractors. The agency specializes in this niche. Agent benefits from installer-specific knowledge (inland marine, workers' comp for installation crews, payroll-based premiums, COI generation for general contractors).

### Payment System Fragmentation
Each carrier has different autopay setup flows, phone trees, and portal requirements. Agent needs carrier-specific payment playbooks.

### Document/Signature Coordination
Many calls exist purely to confirm email receipt, collect a signature, or verify an address. These are entirely automatable with proper digital workflows.

### Emotional Intelligence
Claims, reinstatement, billing disputes, and rate increase calls involve financial stress and emotional distress. The agent must acknowledge, empathize, and provide concrete options — not just transact.

---

## Data Foundation

This document was produced from:
- **37,005 total WAV recordings** from Alliance Insurance's LightSpeed phone system
- **2,196 transcribed** using Qwen3-ASR (0.6B) via MLX on Apple Silicon
- **2,156 extracted** using Qwen3-14B via Ollama with JSON Schema-constrained output
- **1,543 substantive** calls after filtering voicemail, spam, and non-conversations
- **1,542 classified** into 20 engagement types by 5 parallel Claude subagents
- **20 capability specs synthesized** by 4 parallel Claude subagents from merged per-type digests

Classification confidence: 80% high, 19% medium, 1% low.

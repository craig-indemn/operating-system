---
ask: "What are the natural engagement types in Alliance Insurance's phone calls, and what does each one require an AI agent to handle?"
created: 2026-02-18
workstream: audio-transcription
session: 2026-02-18-a
sources:
  - type: local
    description: "2,156 extraction JSONs from Qwen3-14B structured extraction of call transcripts (1,543 substantive)"
  - type: code
    description: "5 parallel Claude subagents each reading ~308 intents independently, then synthesized"
---

# Engagement Type Clustering: Alliance Insurance Phone Calls

## Method

1. Extracted structured data from 2,156 call transcripts using Qwen3-14B (Ollama, JSON Schema-constrained output)
2. Filtered to 1,543 substantive calls (excluded voicemail, spam, hold music)
3. Built compact working dataset: caller_intent + direction + outcome + knowledge_required + systems_referenced per call
4. Split into 5 batches of ~308 calls
5. 5 parallel Claude subagents each read every intent in their batch and independently proposed categories
6. Synthesized across all 5 into 20 final engagement types

All 1,543 substantive intents were read by at least one agent. Categories that appeared independently across multiple agents have highest confidence.

## Call Direction Breakdown

| Direction | Count | % |
|-----------|-------|---|
| Extension transfer | 518 | 34% |
| Outbound | 446 | 29% |
| Inbound | 355 | 23% |
| Queue | 161 | 10% |
| Parked | 35 | 2% |
| Internal | 14 | 1% |
| Attended transfer | 10 | 1% |
| Park timeout | 4 | <1% |

**Note:** Batch 4 (lines 925-1232) was entirely outbound calls, revealing agent-initiated patterns like courtesy calls, proactive renewal reviews, and carrier coordination that don't appear in inbound traffic.

## Outcome Breakdown

| Outcome | Count | % |
|---------|-------|---|
| callback_needed | 1,658 | 77% |
| resolved | 287 | 13% |
| voicemail | 166 | 8% |
| transferred | 25 | 1% |
| not_applicable | 17 | 1% |
| spam | 2 | <1% |
| unresolved | 1 | <1% |

**Critical insight:** 77% of calls end without resolution. The biggest AI agent value may be closing this callback loop by handling simple requests (payments, document delivery, status checks) in one touch.

---

## The 20 Engagement Types

### 1. Make a Payment
**Est. count:** ~190 (12%)
**Appeared in:** All 5 batches (top 3 in every batch)

**Description:** Caller wants to pay a premium — by credit card, debit card, check, or ACH. Includes one-time payments, catching up on overdue balances, and processing payments over the phone. Also includes setting up auto-pay/EFT/bank draft for recurring payments.

**Agent needs:**
- Look up account, verify identity
- Take payment details (card, routing/account numbers)
- Process through correct carrier system (each carrier has different portal)
- Send confirmation via email/text
- Set up recurring payment methods

**Example intents:**
- "Sandra Haymore wants to make a payment for her automobile insurance policy, specifically the monthly installment."
- "Hannah wants to set up automatic payments for her insurance policies, provide her bank routing and account numbers, adjust the payment due date"
- "The caller wanted to make a payment for an insurance account associated with Johnny Alberto Ruiz Aranda."
- "Tommy wants to set up bank drafts for his auto and motorcycle insurance policies"
- "The caller wanted to make a down payment on their Progressive auto insurance policy and confirm the payment details."

**Systems referenced:** Progressive portal, Auto Owners billing, National General payment system, carrier-specific autopay portals, credit card processing

---

### 2. Billing Question / Dispute
**Est. count:** ~85 (6%)
**Appeared in:** All 5 batches

**Description:** Caller is confused or concerned about a bill, premium amount, unexpected charge, or payment status. They are NOT trying to make a payment — they want to understand what they were charged, why, whether a payment went through, why an amount changed, or where a refund is. Includes duplicate charge resolution.

**Agent needs:**
- Access carrier billing systems to explain charges
- Understand pro-rated adjustments, short-rate calculations
- Track down refund status and timelines
- Explain the difference between carrier bill vs agency bill
- Identify and escalate duplicate/incorrect charges

**Example intents:**
- "Aurelio Garcia is questioning a $2,000 business insurance bill from Amtras/Travelers, claiming it was unexpected after disconnecting automatic payments"
- "Shea Glass is seeking clarification about an unauthorized $15.47 credit card charge by Auto Owners"
- "Victor Santiago is seeking clarification about an unexpected $3,500 charge on his card, which he believes was incorrectly processed by autopay"
- "The caller is seeking clarification on her calculated insurance premium ($479) vs the amounts quoted by an agent ($542.20)"
- "David Humphries is seeking clarification about a payment discrepancy, specifically why a $112 payment was processed but $437 appears"

---

### 3. New Insurance Quote
**Est. count:** ~160 (10%)
**Appeared in:** All 5 batches (top 3 in every batch)

**Description:** Caller is shopping for new insurance — auto, home, commercial, renters, life, specialty (moped, jet ski, RV). May be a new customer or existing customer exploring new lines. Includes quote follow-ups ("did you get my quote yet?"). The quoting-to-follow-up pipeline is a single workflow.

**Agent needs:**
- Gather property/vehicle/business details (address, VIN, square footage, roof age, etc.)
- Understand product types across personal and commercial lines
- Run quotes across multiple carriers
- Present and compare options
- Route to appropriate agent for binding

**Example intents:**
- "Karen Abruzo seeks a home insurance quote, believing her current Geico rate may be too high"
- "Kendrick Cabrera is seeking general liability and workers' compensation insurance for his new construction company in Burlington, NC"
- "The caller is seeking a liability insurance quote for a moped"
- "The caller requested a quote for commercial insurance on a cargo van"
- "Jasmine is seeking a homeowners insurance quote for a new home she is closing on, potentially as a bundle with her existing Progressive policy"

**Note from agents:** Quote follow-up is almost as common as initial quote requests. Many calls are "did you get my quote yet?" or "can you explain this number on the quote?"

---

### 4. Vehicle Add/Remove/Replace
**Est. count:** ~120 (8%)
**Appeared in:** All 5 batches (consistently top 5)

**Description:** Caller wants to add a newly purchased vehicle, remove a sold/totaled vehicle, or swap one vehicle for another on their auto policy. This is the single largest policy-change workflow by volume.

**Agent needs:**
- Collect VIN, year/make/model
- Select coverage type (full vs liability, deductibles)
- Coordinate lienholder/finance company information
- Handle DMV implications (tag turnover, FS-1 if needed)
- Generate updated proof of insurance

**Example intents:**
- "Angela Fulton wants to add a car to her existing personal car insurance policy."
- "The caller wants to add a newly purchased 2025 Toyota RAV4 to their existing insurance policy, ensuring it has the same full coverage as their 2016 RAV4."
- "Ingrid wants to add a new 2026 Tesla Model 3 to her insurance policy by removing her 2016 Mercedes"
- "The caller wants to remove a 2012 Nissan Altima from their insurance policy and confirm the effective date of removal."
- "Jennifer Brock wants to transfer insurance coverage from a 2013 Chevrolet van to a new 2014 Chevy Express van"

---

### 5. Driver Add/Remove
**Est. count:** ~35 (2%)
**Appeared in:** All 5 batches

**Description:** Caller wants to add a driver (new teen, spouse, household member) or remove a driver from their policy. Requires understanding underwriting rules for new drivers, learner's permits, excluded drivers, and how driver changes affect premiums.

**Agent needs:**
- Collect driver's license info
- Understand carrier rules for household members, inexperienced operators
- Calculate premium impact of adding young/inexperienced drivers
- Handle excluded driver procedures
- Process e-signature for driver exclusion forms

**Example intents:**
- "Melissa Nelson wants to add her daughter as a driver to her existing insurance policy after the daughter obtains her full license"
- "The caller asked whether they need to add a young person to their insurance policy to obtain a learner's permit."
- "James Marshall wants to update his Progressive umbrella policy to remove his daughter after she moved to Ohio"
- "Jacqui Watson wants to add her 15-year-old son Darian Watson to her auto insurance policy"
- "Brent Wells wants to add his 16-year-old son, Tessie, to his insurance policy as a new driver."

---

### 6. Coverage Modification
**Est. count:** ~70 (5%)
**Appeared in:** All 5 batches

**Description:** Caller wants to adjust coverage parameters on an existing policy — changing deductibles, adding/removing coverage types (collision, comprehensive, towing, rental, umbrella, equipment breakdown), adjusting liability limits, or modifying property coverage amounts. The policy structure is changing, but not adding/removing vehicles or drivers.

**Agent needs:**
- Deep product knowledge (what each coverage type does)
- Premium impact calculations for different deductible levels
- Carrier-specific endorsement processes
- Understanding of how coverages interact (e.g., umbrella requires underlying auto/home limits)

**Example intents:**
- "Melissa Lail wants to change her insurance policy's deductible to $1,000"
- "Chris Bryant wants to update his insurance policy to liability-only coverage"
- "Cheryl Dickerson is following up on an email to confirm details about increasing her umbrella insurance policy from $1 million to $2 million"
- "Bill McClure wants to adjust coverage amounts on his National General policy, including increasing property damage limits"
- "Jean wants to adjust their boat and jet ski insurance policy to remove unnecessary coverages while retaining collision, comprehensive, liability"

---

### 7. Policy Cancellation
**Est. count:** ~93 (6%)
**Appeared in:** All 5 batches

**Description:** Caller explicitly wants to cancel one or more policies — due to selling property, switching carriers, business closure, relocation, dissatisfaction, or cost. Requires cancellation forms, effective date coordination, audit implications (for commercial), and refund handling.

**Agent needs:**
- Understand cancellation procedures and documentation
- Handle carrier-specific cancellation forms (often e-signature)
- Explain consequences (short-rate penalties, audit implications, coverage gaps)
- Process refund expectations and timelines
- For commercial: trigger audit process

**Example intents:**
- "Pat Littleton wants to cancel his business owner policy effective September 15th because he is selling his embroidery business"
- "Henry wants to cancel his home and auto insurance policies effective September 14th because he found a better rate"
- "Juan wants to cancel his workers' compensation and general liability insurance policies because he is no longer working as an installer"
- "Heather wants to cancel four insurance policies (two cars, one homeowner's, one umbrella) effective yesterday"
- "The caller wants to cancel their car insurance policy because they moved to Arkansas and received a DMV notice"

---

### 8. Policy Reinstatement
**Est. count:** ~45 (3%)
**Appeared in:** All 5 batches

**Description:** A policy was canceled (usually for non-payment) and the caller wants it reinstated. Often urgent and stressful. Involves understanding reinstatement windows, carrier-specific rules, payment of past-due amounts, and statements of no loss.

**Agent needs:**
- Know carrier-specific reinstatement windows (varies: 10 days to 60 days)
- Collect statement of no loss
- Process past-due payment
- Coordinate with underwriting for approval
- Handle DMV implications if auto policy lapsed

**Example intents:**
- "Barry Vernon is seeking assistance to resolve a canceled Travelers auto insurance policy due to non-payment"
- "Carlos is seeking assistance to reinstate a canceled insurance policy after a payment dispute with his mortgage company"
- "David Malia wants to reinstate his canceled insurance policy after non-renewal due to missed payment."
- "Jaycee, an 18-year-old student, seeks to reinstate her canceled auto policy with National General"
- "Jamie seeks to reinstate a canceled workers' comp policy affected by a hacked debit card"

---

### 9. Claims Filing & Follow-Up
**Est. count:** ~107 (7%)
**Appeared in:** All 5 batches (consistently top 5)

**Description:** Caller is reporting a new claim (accident, theft, property damage, weather, hit-and-run) or following up on an existing claim (adjuster status, reimbursement, settlement, denial). Includes questions about deductibles, rental car eligibility, and documentation requirements.

**Agent needs:**
- Know carrier-specific claims reporting processes
- Collect incident details (date, location, parties, police report)
- Explain deductibles and coverage applicability
- Track claim status and adjuster communication
- Handle emotionally difficult conversations (accidents, theft, property loss)

**Example intents:**
- "Tim Holt is reporting a truck accident involving his 2021 Ram at 6:00 AM in Rocky Mountain, NC"
- "Stephen Leak is reporting a stolen toolbox valued at $4,000-$5,000 from his truck"
- "Kathy Bowman is reporting damage to her home caused by a fallen tree from her neighbor's yard"
- "Rode is seeking clarification about a partial insurance payment ($1,800 instead of the full $4,335.99) for a car accident claim"
- "The caller wants to resolve a car damage claim settlement delayed by an unresponsive adjuster"

---

### 10. Policy Renewal / Rate Review
**Est. count:** ~100 (6%)
**Appeared in:** All 5 batches

**Description:** Existing customer reviewing an upcoming or recent renewal — why the premium changed, whether to accept the renewal, comparing against other carriers, exploring bundling discounts. Includes proactive outbound renewal reviews by agents. "Why did my rate go up?" calls are a major subset.

**Agent needs:**
- Explain rate factors (state mandates, claims history, credit, zip code, ISO ratings)
- Compare renewal rate against competitive quotes
- Advise on cost reduction options (higher deductibles, coverage adjustments, bundling)
- Process carrier transitions if reshop is needed
- Understand NC-specific market dynamics (carrier exits, rate filings)

**Example intents:**
- "Charles is concerned about a significant increase in his insurance premiums (auto up $600/year, home up $173/year)"
- "Corbin is checking if his insurance policies (auto and homeowners) are still the best option"
- "Jason Newman wants to review his bundled auto, home, and personal umbrella insurance policies with Auto Owners"
- "Brandy from Alliance Insurance is contacting Miss Cooper to review her upcoming home and auto insurance renewals"
- "Savannah King is seeking clarification on a significant increase in her Progressive insurance renewal premium (over $100/month)"

**Note from agents:** The boundary between "renewal review" and "new quote" is blurry. Many renewal reviews turn into re-shops when the renewal rate is too high, which then become competitive quote presentations.

---

### 11. Certificate of Insurance (COI)
**Est. count:** ~55 (4%)
**Appeared in:** All 5 batches

**Description:** Caller needs a certificate of insurance generated, corrected, or sent to a third party (builder, lender, university, vendor, general contractor). Often involves adding certificate holders, correcting DBA names, or updating project-specific details. High urgency — often needed for a job to start.

**Agent needs:**
- Know how to generate COIs from carrier systems
- Understand certificate holder vs additional insured distinction
- Handle DBA names and project-specific wording
- Deliver via email quickly (often same-day deadline)
- Handle repeated requests from same contractors

**Example intents:**
- "Chris from Conterra Marble and Granite requests a certificate of insurance for Perrier Builders to be added and sent to Brandon Perrier via email."
- "Jason Harkey is requesting a corrected Certificate of Insurance (COI) for FCR Holdings LLC, ensuring it includes 'DBA First Class Roofing'"
- "Donnie from MPE Rentals needs an updated certificate of insurance for Fralin that properly reflects $80,000 coverage for rented/leased equipment"
- "Linda requested a certificate of insurance for general liability and workers comp under North Edge Steel"
- "Debbie Holbrook needs a certificate of insurance emailed to the town of Elkin to confirm Holbrook Plumbing Company has GL, WC, and commercial package"

**Note from agents:** COI is the #1 commercial lines request by volume. Contractors call repeatedly (same phone numbers across many calls).

---

### 12. Document Request
**Est. count:** ~77 (5%)
**Appeared in:** All 5 batches

**Description:** Caller needs a copy of their policy, declaration page, proof of insurance, ID cards, loss runs, bond copy, or other insurance document. Often time-sensitive (needed for a closing, a dealership, a lender, a job, DMV). Distinct from COI because these are general document retrieval, not certificate generation.

**Agent needs:**
- Know how to retrieve documents from carrier portals
- Generate and deliver via email/text quickly
- Understand what document the caller actually needs (they often use wrong terminology)
- Handle loss run requests (require carrier processing time)

**Example intents:**
- "The caller requested a copy of his current insurance policy be emailed to him as proof of insurance for a client's job board event."
- "Lauren needs a copy of her organization's insurance policy to submit to a national organization"
- "Vicky Hill needs a copy of her insurance declaration page for her employer"
- "Tequisha requested a loss run report for Chris's Auto Company LLC"
- "Kayla Dillon needs a digital proof of insurance sent to the DMV for her husband"

---

### 13. DMV / Compliance
**Est. count:** ~35 (2%)
**Appeared in:** All 5 batches

**Description:** Caller received a DMV notice about plate revocation, needs an FS-1 form filed, or requires compliance documentation for regulatory purposes. High urgency — often involves fines, vehicle registration revocation, or inability to drive. Includes DOT number setup for commercial.

**Agent needs:**
- Understand NC DMV requirements and FS-1 form process
- Know how to file FS-1 electronically
- Explain consequences of coverage lapses to DMV
- Handle plate revocation notices
- Assist with DOT number setup (commercial)

**Example intents:**
- "Casey Tuttle is seeking clarification about an FS-1 form related to a DMV notice, confirming address details, and resolving a vehicle registration revocation issue."
- "Joseph Fernandez needs assistance addressing a DMV letter regarding an alleged insurance lapse and submitting an FS1 form"
- "The caller is seeking clarification about a $1,000 charge for a new vehicle tag due to a policy lapse... received a 'mailed plate revocation' notice"
- "Sunny is assisting Cody in navigating the process of setting up a DOT number, addressing challenges related to vehicle titling"
- "Jamie Flippin seeks to resolve an issue where a client improperly removed a vehicle, potentially triggering a DMV flag fee."

---

### 14. Mortgage / Lender Coordination
**Est. count:** ~40 (3%)
**Appeared in:** All 5 batches

**Description:** Calls involving the intersection of insurance and mortgages/lending — escrow payment confusion, mortgage company needing proof of insurance, lienholder additions/removals, insurance changes affecting mortgage payments, refinancing coordination, or resolving discrepancies between insurer and mortgage servicer. Callers include both policyholders and lender representatives.

**Agent needs:**
- Understand escrow mechanics and how insurance premiums flow through mortgage companies
- Process mortgagee clause updates
- Send evidence of insurance to lenders
- Handle lienholder additions for auto loans
- Coordinate between carrier and mortgage servicer

**Example intents:**
- "Linda Ashford is seeking clarification about an unexpected increase in her home insurance escrow amount, which was sent by Carington Mortgage"
- "Gary contacted Alliance Insurance to resolve an issue where his mortgage company had not received his updated homeowners policy"
- "Allison needs assistance confirming how her mortgage company requires a specific insurance-related detail to be listed"
- "Matthew from NewRes is confirming whether NewRes LLC is listed as a mortgagee on Francisco Flores' policy"
- "The caller is seeking assistance with resolving a financial crisis caused by an unexpected increase in mortgage payments following the cancellation of their insurance"

---

### 15. Workers' Comp Administration
**Est. count:** ~45 (3%)
**Appeared in:** All 5 batches

**Description:** Calls specifically about workers' compensation — WC quotes, audit resolution (compliant and non-compliant), payroll reporting, class code changes, ghost policies, audit-related collections, and WC claims. This domain requires specialized knowledge distinct from personal lines or general commercial.

**Agent needs:**
- Understand WC audit lifecycle (submission, non-compliance fees, collections)
- Know class codes and how to handle changes
- Calculate premiums based on payroll
- Handle ghost policy questions
- Navigate Travelers audit portal (most common carrier for WC audits in data)
- Understand subcontractor classification rules

**Example intents:**
- "Lily is seeking assistance with an unexpected charge from Travelers Insurance due to an audit on a canceled workers' compensation policy"
- "Victor Santiago needs assistance completing a Workers Comp policy audit for Travelers, which is currently non-compliant"
- "Crystal is seeking assistance with an audit-related debt of $9,000 that has been sent to collections"
- "Donette Sikes needs assistance changing workers' comp class codes from 8848 to 8826/8824 after an audit"
- "Sherry seeks guidance on handling a workers' compensation claim for an employee who fell through a porch"

**Note from agents:** WC audit calls are only ~3% of volume but disproportionately complex. They require the most specialized knowledge of any engagement type.

---

### 16. Policy Info Update
**Est. count:** ~40 (3%)
**Appeared in:** All 5 batches

**Description:** Caller needs to update personal or business information on their policy — new address (moving), new email, phone number change, name change (divorce/marriage), DBA update, or payment method update. Straightforward administrative changes.

**Agent needs:**
- Update information across potentially multiple carrier systems
- Understand which changes trigger underwriting review (address change may affect rate)
- Handle name change documentation requirements
- Coordinate with mortgage company if address changes on homeowners policy

**Example intents:**
- "Justin Horn wants to update his address on file with Alliance Insurance"
- "Andrea wants to change her last name on her home insurance policy to match her new name post-divorce"
- "Donna is seeking to correct a typo in an address listed on her insurance policy"
- "Agent Jamie is assisting client Mary with updating Jocelyn Harris's email address on her Auto Owners account"
- "Evy wanted to update her address information across multiple insurance policies"

---

### 17. Coverage Question / Clarification
**Est. count:** ~50 (3%)
**Appeared in:** All 5 batches

**Description:** Caller wants to understand what their policy covers — does it cover windshield damage? Electrical surge from a tree? Towing? Theft from a trailer? Dog liability? Mold? Rental car abroad? These are not claims — the caller is asking before deciding what to do. Pure knowledge queries requiring deep product expertise.

**Agent needs:**
- Deep knowledge of policy language and coverage terms
- Access to policy documents to verify specific coverages
- Ability to explain exclusions and limitations clearly
- Know when to say "this requires an underwriter's opinion" vs. giving a definitive answer

**Example intents:**
- "The caller is inquiring about coverage for damages caused by a fallen tree limb that disrupted power lines, leading to electrical surges"
- "Aaron Hunter seeks clarification about the coverage of his insurance policies, specifically regarding general liability, property, and auto coverage"
- "Eric Leopold is following up on a previous inquiry about whether his commercial insurance policy covers potential lawsuits related to legally authorized GPS tracking"
- "Todd Fry from Haker Construction is asking whether a builder's risk policy covers theft or vandalism of materials on a construction site"
- "Pam is seeking clarification on towing coverage differences between her current policy and Auto Owners"

**Note from agents:** These are high-value for AI automation — pure knowledge queries that require reading policy language but no transaction. A well-trained agent with policy document access could handle these immediately.

---

### 18. Commercial / Specialty Inquiry
**Est. count:** ~56 (4%)
**Appeared in:** All 5 batches

**Description:** Complex commercial insurance questions requiring specialized underwriting judgment — builder's risk, vacant property coverage, parking lot liability, equipment insurance, bond forms, HOA policies, church programs, dealer lot coverage, special events, liquor liability, farm insurance. These go beyond standard personal lines or simple commercial GL/WC.

**Agent needs:**
- Deep commercial lines expertise
- Understanding of specialty markets and carrier appetites
- Bond knowledge (bid bonds, performance bonds, surety)
- Life/health/benefits awareness (occasionally comes through same phone system)
- Ability to recognize when a risk needs wholesale/surplus lines market

**Example intents:**
- "Todd Fry from Haker Construction is asking whether a builder's risk policy covers theft or vandalism of materials on a construction site"
- "Kendra Claybo is seeking guidance on whether Alliance Insurance Services can cover a non-standard insurance request involving an employee driving within a parking lot"
- "Bruce Murray seeks advice on insuring his wife's church-affiliated preschool"
- "Rich is discussing insuring a vacant property (a cabin on Cabin Trail House) that he plans to renovate and sell"
- "Salman is seeking auto dealer insurance for a new used car sales business in Charlotte, NC"

**Subcategories within this type:**
- Bond servicing (~15 calls): issuing, modifying, confirming status
- Life/health/benefits (~14 calls): life insurance quotes, Medicare supplements, group health
- Carrier transition/rewrite (~13 calls): moving a client from one carrier to another

---

### 19. Follow-Up / Status Check
**Est. count:** ~70 (5%)
**Appeared in:** All 5 batches

**Description:** Caller is following up on something previously requested — a pending quote, a document that was supposed to be sent, a payment that was supposed to process, a policy change that was submitted, or any prior request. The call exists because a previous interaction didn't reach completion.

**Agent needs:**
- Access to conversation/interaction history
- Ability to check status across carrier systems
- Proactive communication skills (these calls shouldn't need to happen)

**Example intents:**
- "Oscar is following up on submitted insurance quotes that are pending approval and wants confirmation of their status"
- "Victoria is following up on a previous conversation to check the status of an insurance quote"
- "Nathan Bell wanted to confirm receipt of a proposal email sent for carrier renewal confirmation"
- "The caller is following up on a voicemail from Heather Scott or Taylor Scott regarding a renters policy for their son"
- "Michelle Williams is following up on insurance quotes for a property at 3113 Allen Court"

**Note from agents:** This category is essentially a failure mode of the current process. If initial requests resolved in one touch, most of these calls wouldn't exist. An AI agent that provides real-time status and proactive updates could eliminate this entire category.

---

### 20. Routing / Triage
**Est. count:** ~80 (5%)
**Appeared in:** All 5 batches

**Description:** Catch-all for calls that are primarily about reaching the right person or handling non-insurance matters. Includes: requesting a specific agent by name, returning a call/voicemail, language assistance (Spanish), non-insurance calls (IT support, haircuts, colonoscopy scheduling, vendor calls, food orders), courtesy/relationship calls, and solicitation.

**Subcategories:**
- **Agent routing** (~30): "Can I speak to Gloria?" / "Heather left me a voicemail" — caller just wants a specific person
- **Spanish/non-English** (~20): Caller needs bilingual assistance, often routed to Jessica (only Spanish-speaking commercial agent)
- **Non-insurance/misdirected** (~15): Haircut scheduling, water bill inquiries, colonoscopy rescheduling, food orders, IT support (printer jams, Adobe licensing, scanner troubleshooting)
- **Courtesy/relationship** (~11): Holiday greetings, thank-you calls, event invitations
- **Carrier/third-party inbound** (~varies): Carriers, underwriters, inspectors, lenders calling the agency (not customers)

**Example intents (agent routing):**
- "The caller wanted to speak with Holly Moore at Alliance Insurance but was informed she was unavailable until 10:30 AM."
- "The caller received a previous call from Cecilia and wants to speak with her directly."

**Example intents (non-insurance):**
- "The caller is inquiring about walk-in availability, waiting times, pricing, and payment methods for a haircut and beard trim service."
- "Mr. Gary Belcher wants to reschedule his January 9th colonoscopy appointment"
- "Ashley wanted to place an order for a side of hibachi chicken."

---

## Cross-Cutting Patterns

### Carrier Fragmentation
The calls reference 20+ carriers, each with different portals, processes, billing systems, and claims workflows: Progressive, Auto Owners, National General, Travelers, Cincinnati, Westfield, Penn National, Safeco/Liberty Mutual, Foremost, USLI, Grange, NCJUA, AmTrust, Utica, Hartford, Builders Mutual, Farm Bureau, Honeycomb, and more. An AI agent needs carrier-specific playbooks, not generic answers.

### Multi-Intent Calls
Many calls involve 2-3 distinct requests bundled together — a payment AND a coverage question AND a document request. "Cancel insurance on totaled car AND add new car" is a single call. An AI agent must handle multi-intent conversations gracefully.

### Repeat Callers
The same people call back multiple times as situations evolve. Jennifer (+13368301632) has 7+ calls. German (+13367556110) has 4+ calls. Gary appears dozens of times across different customers sharing that name. Conversation history and continuity is critical.

### Spanish Language Demand
At least 20+ calls explicitly needed Spanish, and several more had callers with limited English. The agency has only one Spanish-speaking commercial agent (Jessica). An AI agent with Spanish capability would immediately expand capacity.

### NC Market Disruption
Multiple calls reference carriers exiting North Carolina (Main Street America), non-renewing policies, or significant rate increases. This creates a wave of reshop/rewrite activity that is a major workload driver. The AI agent needs to understand this market context.

### Third-Party Callers
~5% of calls are FROM carriers, lenders, inspectors, mortgage companies, or other agencies — not customers. The AI agent needs to handle both B2C and B2B interactions with different protocols.

### The Installer Niche
A large portion of commercial calls involve steel building installers, carport installers, and similar contractors. The agency clearly specializes in this niche. An AI agent would benefit from installer-specific knowledge (inland marine, workers' comp for installation crews, payroll-based premiums, COI generation for general contractors).

### Payment Fragmentation
Payment processing is fragmented across many carrier systems. Auto Owners, Progressive, National General, Travelers, Penn National — each has different autopay setup flows, phone trees, and portal requirements. An AI agent handling payments needs carrier-specific playbooks.

### Document/Signature Coordination Is a Time Sink
Many calls exist purely to confirm email receipt, collect a signature, or verify an address. These are entirely automatable with proper digital workflows.

---

## Engagement Types for classify.py

The corresponding `engagement_types.json` file contains the machine-readable version of these 20 types for use in the classification step (step 3 of the extraction pipeline).

## Frequency Distribution

```
Make a Payment         ████████████████████████ 12%
New Insurance Quote    ████████████████████  10%
Vehicle Add/Remove     ████████████████  8%
Claims Filing          ██████████████  7%
Billing Question       ████████████  6%
Policy Cancellation    ████████████  6%
Renewal / Rate Review  ████████████  6%
Coverage Modification  ██████████  5%
Document Request       ██████████  5%
Follow-Up / Status     ██████████  5%
Routing / Triage       ██████████  5%
COI Request            ████████  4%
Commercial / Specialty ████████  4%
Coverage Question      ██████  3%
WC Administration      ██████  3%
Policy Reinstatement   ██████  3%
Mortgage / Lender      ██████  3%
Policy Info Update     ██████  3%
DMV / Compliance       ████  2%
Driver Add/Remove      ████  2%
```

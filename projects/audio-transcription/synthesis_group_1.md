# Capability Specifications: Group 1

Synthesized from 5 batch digests per engagement type across 1,543 substantive Alliance Insurance phone calls.

---

## New Quote (~215 calls, 13.6%)

**Typical Caller:** A prospective or existing customer shopping for new insurance coverage -- auto, home, commercial, renters, life, or specialty (moped, jet ski, RV, food trailer). They either found Alliance through a referral, are unhappy with their current rate, or need coverage for a newly acquired asset or new business venture.

**Resolution Workflow:**
1. Greet the caller and determine what type of coverage they need (personal auto, homeowners, commercial GL/WC, specialty).
2. Collect personal information: full name, date of birth, driver's license number, current address, email, and phone number.
3. For auto: collect VIN or year/make/model, current mileage, usage type (personal/commercial), and any lienholders. Run MVR (motor vehicle report) for driving history.
4. For homeowners: collect property address, square footage, year built, construction type, roof age/material, heating type, protection class, and distance to fire hydrant. Run replacement cost estimator tool.
5. For commercial: collect business name, entity type (LLC/sole prop), EIN, years in business, employee count, annual payroll, class codes, and scope of operations.
6. Check if the caller has existing Alliance policies -- bundling (auto + home) is often required by carriers and unlocks discounts.
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
- Alliance Insurance internal quoting system
- Progressive quoting system
- Auto Owners portal
- Cincinnati Insurance portal
- National General portal
- Northwest Farmers Mutual system
- Penn National system
- Westfield, SafeCo, USLI (Snap quoting), NC Grange, Hartford, Foremost, Utica National portals
- Canopy Connect (insurance data import from prior carriers)
- Replacement cost estimator (RCE) tool
- MVR (motor vehicle report) system
- E-signature platforms
- Marblebox quoting tool
- Email system for quote delivery

**Outcome Distribution:**
- callback_needed: ~76% (162/215). Quoting inherently requires multi-step processing -- gathering info, running carrier systems, comparing options. Most calls end with "I'll email you quotes."
- resolved: ~15% (32/215). Outbound calls presenting completed quotes that the customer accepts on the spot.
- voicemail: ~2%. Outbound quote presentation attempts where the customer did not answer.
- transferred: ~1%. Routed to specialized producer or Spanish-speaking agent.

The high callback rate is structural, not a failure -- quoting takes time. However, the initial data gathering (steps 2-5) and the quote presentation (step 10-11) are separable workflows with different automation potential.

**Edge Cases & Escalation Triggers:**
- Caller needs a product Alliance does not offer: non-owners insurance, NC Joint Underwriting policies, consignment/third-party goods liability, standalone liability-only auto. Must refer to another agency.
- Florida condo insurance requiring specialist hurricane market knowledge.
- Estate property with unclear deed status requiring NCJUA referral.
- Coverage lapse exceeding carrier thresholds (e.g., 7-9 month gap exceeds the typical 15-day max gap rule). Most carriers will decline.
- Spanish-speaking callers needing transfer to Jessica (only Spanish-speaking commercial agent).
- Medicare/health insurance inquiries that are outside P&C scope -- must refer to separate health insurance agent.
- Food trailer needing temporary personal policy pending LLC formation (entity structure ambiguity).
- High-risk applicants with poor credit scores requiring specialized carrier placement.

**Automation Feasibility:** Medium
Rationale: The data-gathering phase (steps 2-5) is highly automatable -- an AI agent can collect name, DOB, address, VIN, property details, and business info through structured conversation. This represents roughly 40-50% of each call's duration. However, the actual quote generation requires API access to 15+ carrier systems, many of which lack programmatic interfaces and require manual portal entry. The quote presentation and comparison phase (steps 10-11) also benefits from human judgment for nuanced coverage recommendations. Approximately 30-40% of the end-to-end workflow could be fully automated (intake and triage), with the remainder requiring either carrier API integration or human expertise for complex commercial risks.

**What the AI Agent Must Do:**
- Conduct structured intake interviews that adapt questions based on coverage type (auto vs. home vs. commercial vs. specialty)
- Collect and validate all required data fields: personal info, property details, vehicle info (VIN decoding), business details including class codes and payroll
- Determine bundling eligibility and requirements before proceeding (many carriers require auto + home)
- Identify when a risk falls outside Alliance's carrier appetite and provide an appropriate referral rather than wasting time quoting
- Handle multi-line quote requests in a single conversation (auto + home + umbrella + commercial)
- Set accurate expectations for turnaround time (1-2 business days for formal quotes)
- Deliver quotes via email/text with carrier comparison summaries
- Support Spanish-language intake conversations to expand capacity beyond the single bilingual agent
- Recognize and route specialty risks (builder's risk, dealer lot, vacant property, HOA) to the appropriate commercial producer

---

## Billing Question (~145 calls, 9.4%)

**Typical Caller:** An existing policyholder confused or upset about an unexpected charge, a premium increase they do not understand, a payment that did not process correctly, a missing refund, or a discrepancy between what they expected to pay and what appeared on their statement or bank account. These callers are not trying to make a payment -- they want an explanation.

**Resolution Workflow:**
1. Verify caller identity (name, policy number, or phone number on file).
2. Pull up the caller's billing history across relevant carrier portal(s) -- determine which carrier and which policy line the question relates to.
3. Identify the specific discrepancy: compare the amount the caller expected vs. what was charged, when it was charged, and through which payment method.
4. Diagnose the root cause. Common causes include:
   - NC state-mandated rate increases (7.5% homeowners hike referenced frequently)
   - Loss of multi-vehicle or multi-policy discount after removing a vehicle or canceling a bundled policy
   - Mid-term endorsement pro-rations (adding/removing vehicles or coverages)
   - Non-compliant workers' comp audit fees from Travelers
   - Paperless discount removal causing small balance adjustments
   - NSF (non-sufficient funds) returned payments triggering fees and payment plan disruption
   - Auto-draft timing conflicts with cancellation or endorsement dates
   - Short-rate cancellation calculations vs. pro-rata expectations
   - System errors: billing account linked to wrong DBA, EFT setup not saved properly, payment applied to wrong policy
5. Explain the cause clearly to the caller using plain language -- translate insurance billing jargon (pro-rated, short-rate, endorsement) into understandable terms.
6. If the charge is incorrect or a waiver is eligible (e.g., one annual fee waiver), process the correction or waiver.
7. If the issue requires carrier-level resolution (e.g., Travelers audit portal, Progressive billing department), either call the carrier on behalf of the client or provide direct carrier contact information.
8. If a refund is owed, explain the refund timeline and process.
9. Document the resolution and send a summary via email if the caller requests it.

**Required Knowledge:**
- Premium calculation factors: state mandates, claims history, credit score, zip code, ISO ratings, inflation guard endorsements, replacement cost updates
- How policy changes (vehicle add/remove, coverage modification, driver add/remove) flow through to billing as pro-rated adjustments
- Multi-vehicle and multi-policy discount mechanics -- how removing one element affects remaining premiums
- Workers' compensation audit billing: non-compliance fees, audit completion requirements, collection escalation
- Payment plan structures: 11-pay vs. 12-pay, quarterly, annual pay-in-full discounts, bank draft discount
- NSF payment handling, reinstatement fees, and payment retry mechanisms
- Short-rate vs. pro-rata cancellation refund calculations
- Carrier-specific billing quirks: Progressive's paperless discount, Auto Owners' travel trailer billing, Penn National's first-month vs. subsequent-month payment structures
- Escrow mechanics for homeowners policies billed through mortgage companies
- Agency bill vs. direct carrier bill distinction

**Systems & Tools:**
- Progressive billing system / Progressive.com
- Auto Owners billing portal
- Travelers policy portal and audit system
- Penn National billing system
- National General portal
- Cincinnati carrier system
- SafeCo billing system
- Nationwide Commercial Lines
- Ascend agency bill platform
- Alliance Insurance internal billing/policy management system
- Agent Center
- Alliance Insurance customer portal (myallianceinsurance.com)

**Outcome Distribution:**
- callback_needed: ~66% (96/145). Many billing questions require research -- pulling payment history, contacting the carrier, or waiting for a refund status update.
- resolved: ~27% (39/145). Straightforward questions where the agent can immediately explain the charge, confirm a payment posted, or verify a discount.
- not_applicable/spam: ~3%.
- unresolved: <1%.

The 27% immediate resolution rate is promising for automation. These are cases where the answer exists in the billing system and just needs to be surfaced clearly.

**Edge Cases & Escalation Triggers:**
- Non-compliant workers' comp audit fees from Travelers causing unexpected charges of $3,500+ hitting autopay -- requires audit portal completion, not just a billing fix.
- Billing account incorrectly linked to a canceled policy's DBA after a carrier rewrite -- requires carrier system correction.
- Deceased policyholder's bank account still being drafted -- requires sensitive handling and immediate payment method cessation.
- Vehicles removed from policy without policyholder authorization, causing billing confusion.
- Points consolidation after vehicle removal: removing a vehicle causes driving infractions to load onto the remaining vehicle, paradoxically increasing the premium -- counterintuitive and requires careful explanation.
- Mortgage company escrow discrepancies where the insurer and mortgage servicer show different amounts.
- Duplicate charges across home and auto policies displayed on the same Travelers billing page.
- Refund held pending audit completion despite policy cancellation -- caller expects money but carrier will not release until audit closes.

**Automation Feasibility:** Medium
Rationale: Approximately 25-30% of billing questions are simple lookups ("did my payment go through?", "what is my next payment amount?", "when is it due?") that could be fully automated with read access to carrier billing systems. Another 20-25% involve explaining standard rate increases (NC mandates, inflation guard) using templated explanations. The remaining 45-50% involve complex diagnostics (audit fees, pro-ration calculations, system errors, refund disputes) that require human judgment or carrier coordination. The biggest blocker is carrier system fragmentation -- each carrier has a different billing portal, and explaining the nuances of each carrier's billing logic requires deep institutional knowledge.

**What the AI Agent Must Do:**
- Access billing history across Progressive, Auto Owners, Travelers, Penn National, National General, Cincinnati, SafeCo, Nationwide, and the Ascend agency bill platform
- Identify the specific charge or discrepancy the caller is asking about by comparing their stated expectation against actual billing records
- Explain premium changes in plain language, including NC state-mandated rate increases, endorsement pro-rations, and discount loss mechanics
- Calculate and explain how removing a vehicle or driver affects the remaining premium (including counterintuitive increases from points consolidation or multi-car discount loss)
- Verify payment processing status (posted, pending, returned NSF) and auto-pay/EFT configuration
- Explain refund timelines and short-rate vs. pro-rata cancellation calculations
- Identify when a billing issue is actually a carrier system error and escalate to the carrier or a human agent with specific context
- Handle emotionally charged conversations -- billing disputes often involve financial stress, especially when unexpected charges hit bank accounts via autopay

---

## Follow-Up / Status Check (~139 calls, 8.9%)

**Typical Caller:** Someone who previously contacted Alliance about a quote, policy change, document request, claim, or payment -- and has not received the expected result. They are calling back to ask "where is it?" These calls represent a failure of the prior interaction to reach completion or communicate status proactively.

**Resolution Workflow:**
1. Identify the caller and determine what prior interaction they are following up on. Check internal notes, email history, and CRM records.
2. Look up the status of the pending item:
   - For quotes: check if the quote has been run, approved by underwriting, and emailed to the client.
   - For policy changes: check if the endorsement was submitted to the carrier and processed.
   - For documents: check if the document was generated, sent, and received (check for spam/junk filter issues).
   - For claims: check adjuster assignment and status with the carrier.
   - For payments: verify if the payment posted, and if auto-pay was correctly configured.
3. If the item is complete, confirm completion and resend the deliverable (email, document, confirmation) if not received.
4. If the item is still pending, explain the reason for the delay (underwriting approval queue, carrier processing time, producer workload).
5. Provide a specific timeline: "by end of day," "by Friday," "within 24 hours." Avoid open-ended "we'll get back to you."
6. If the item was lost or never initiated, re-initiate the request and set a new timeline.
7. If the original agent is unavailable, either resolve directly or take a detailed message with callback commitment.
8. Document the follow-up in the CRM so the chain of interactions is visible.

**Required Knowledge:**
- Internal case tracking and note systems -- ability to reconstruct what happened in a prior interaction
- Carrier processing timelines: how long underwriting approval takes, when policy changes become effective, document generation turnaround
- Email delivery troubleshooting: spam filters, junk folders, incorrect email addresses, Alliance-specific portal link issues (known YouTube redirect bug in Canopy/Allstate portal)
- Agent schedules and availability -- who handles which accounts, who is out of office
- Quote approval workflows including underwriter escalation paths
- Document verification processes: confirming what was sent, when, and to which email address

**Systems & Tools:**
- Alliance Insurance internal CRM/notes system
- Email system (outbound and delivery tracking)
- Voicemail systems
- Carrier underwriting portals (Progressive, Auto Owners, Cincinnati, Liberty Mutual, Utica National, Westfield)
- Conga Sign (e-signature tracking)
- Salesforce (referenced for documentation)
- Alliance Insurance customer portal (myallianceinsurance.com)
- Internal agent directory and availability tracking

**Outcome Distribution:**
- callback_needed: ~71% (99/139). The majority of follow-ups cannot be resolved immediately because the underlying item is still pending -- the agent can only provide a status update and a new timeline.
- resolved: ~19% (26/139). Cases where the item was actually done but the caller did not realize it (email in spam), or the agent can complete it on the spot.
- voicemail: ~4%. Outbound follow-up attempts where the client did not answer.

The 71% callback rate on follow-up calls is a compounding problem -- these callers already called once and are now calling again without resolution. Each unresolved follow-up erodes trust.

**Edge Cases & Escalation Triggers:**
- Quote disappeared from carrier system requiring re-quote from alternate carrier.
- Portal link not working due to known redirect bug (Allstate/YouTube redirect issue).
- Email filtered to junk mail and discarded by recipient -- caller never received the quote/document.
- Follow-up call reached wrong person (client's mother instead of client) due to outdated phone number.
- System issue preventing policy renewal due to producer code update at the carrier level.
- Multiple follow-ups from the same client (e.g., Maggie calling repeatedly across different dates about various pending items) -- indicates systemic service failure.
- Agent unable to reach client due to phone number change, multiple outbound attempts over weeks with no contact.
- Commercial policy non-renewal after DOT status change, requiring complex carrier coordination that spans multiple follow-up calls.
- Flood policy verification failed because the policy could not be found in the system.

**Automation Feasibility:** High
Rationale: This is the single highest-value automation target. Follow-up calls exist because the system fails to proactively communicate status. An AI agent with access to carrier status APIs, internal notes, and email delivery tracking could: (a) provide real-time status via IVR or chat without requiring a human, handling an estimated 50-60% of these calls; (b) proactively send status updates via text/email when milestones complete ("your quote is ready," "your policy change is effective"), potentially eliminating 70-80% of inbound follow-ups entirely. The only blockers are follow-ups involving subjective judgment ("is my renewal rate fair?") or carrier-level delays that require human escalation.

**What the AI Agent Must Do:**
- Access internal notes, CRM history, and email logs to reconstruct the full chain of prior interactions for a given caller
- Check real-time status of pending quotes across carrier underwriting portals
- Verify email delivery status and resend documents/quotes when they were not received (including troubleshooting spam/junk filter issues)
- Provide specific, time-bound commitments ("your quote will be ready by 5 PM Friday") rather than vague promises
- Track repeat callers and flag when someone has called 3+ times about the same issue for priority human escalation
- Proactively push status notifications via text and email when milestones are reached (quote approved, document generated, payment processed, policy change effective)
- Handle the emotional layer: these callers are already frustrated by waiting. Acknowledge the delay, take ownership, and provide a clear path to resolution.

---

## Make a Payment (~135 calls, 8.6%)

**Typical Caller:** An existing policyholder ready to pay a premium -- by credit card, debit card, checking account, or (rarely) cashier's check. Includes one-time payments to catch up on overdue balances, regular monthly installments, full annual pay-in-full, down payments to bind new policies, and requests to set up recurring auto-pay via EFT/bank draft.

**Resolution Workflow:**
1. Verify caller identity: name, policy number, or phone number/address on file.
2. Pull up the account and confirm the amount due, due date, and which carrier/policy the payment applies to.
3. Determine payment method:
   - **Credit/debit card:** Collect card number, expiration date, CVV, billing zip code. Inform caller of the processing fee ($4 typical for most carriers).
   - **Checking account (one-time):** Collect routing number and account number.
   - **Auto-pay/EFT setup:** Collect routing and account numbers. Send authorization form via email (Conga Sign for Penn National, carrier-specific forms for others). Set draft date preference if the carrier allows it.
4. Navigate to the correct carrier payment system:
   - For Progressive: use Progressive portal or secure credit card line.
   - For Auto Owners: use Auto Owners billing portal (note: Pay Now online system is separate from the billing system -- cards saved online are NOT accessible for billing setup).
   - For National General: use National General carrier portal.
   - For Penn National: process through Penn system, EFT requires Conga Sign e-signature.
   - For Cincinnati: use Cincinnati billing department or carrier portal.
   - For Travelers: use Travelers payment system.
   - For Foremost: note that cashier's checks must be made payable to Foremost Insurance, not Alliance.
   - For Utica National, Liberty Mutual: use respective payment systems.
5. Process the payment and obtain a confirmation number.
6. Provide the confirmation number verbally and send a receipt via email.
7. If the caller also wants to set up auto-pay, initiate that as a separate step after the immediate payment.
8. Confirm the next payment date and amount so the caller knows what to expect.

**Required Knowledge:**
- Carrier-specific payment processing systems and their quirks (Auto Owners' separate Pay Now vs. billing systems, Progressive's secure credit card line)
- Credit card and debit card verification and PCI-compliant handling procedures
- EFT/ACH setup procedures per carrier, including authorization form requirements
- Payment plan structures: monthly, quarterly, two-pay, four-pay, annual pay-in-full, and associated discounts/fees
- Processing fee disclosure requirements ($4 credit card fee typical)
- Payment processing timelines (1-2 business days for most electronic payments)
- How to handle partial payments and their impact on policy status
- Cashier's check payee requirements per carrier
- Grace periods for late payments by carrier (Liberty Mutual, others)
- Reinstatement payment requirements when paying on a lapsed/canceled account

**Systems & Tools:**
- Progressive payment portal and secure credit card line
- Auto Owners billing system (distinct from Pay Now/PNC online portal)
- National General carrier portal
- Penn National billing system
- Cincinnati insurance portal and billing department
- Travelers payment system
- Foremost insurance system
- Utica National payment system
- Liberty Mutual payment system
- Ascend agency bill platform
- Conga Sign (e-signature for EFT authorization)
- Alliance Insurance internal payment processing system
- Email system for receipts and confirmation
- Alliance Insurance customer portal (myallianceinsurance.com)

**Outcome Distribution:**
- callback_needed: ~75% (102/135). Surprisingly high for a transactional workflow. This is driven by: callers placed on hold while the agent navigates carrier portals, callers who need to get their card or bank info and call back, and cases where payment processing requires a separate carrier phone call.
- resolved: ~21% (29/135). Payments successfully processed during the call with confirmation provided.
- voicemail: ~4%. Outbound payment collection attempts.

The 75% callback rate for a simple payment transaction reveals massive friction. In a modern system, payment should resolve in one touch 90%+ of the time.

**Edge Cases & Escalation Triggers:**
- Third-party payment: someone paying for another person's policy (not the policyholder) -- requires identity verification of the actual policyholder, not just the payer.
- Payment on a canceled account awaiting reinstatement -- requires underwriting flag before payment can process.
- Caller using someone else's card (friend's debit card because their own is inactive) -- PCI and authorization concerns.
- Auto-pay setup that appeared successful but only recorded an "easy check" payment, requiring re-setup -- Auto Owners system quirk.
- Spanish-speaking caller making payment with limited English communication.
- Caller paying for a lodge/organization as treasurer, not personal policyholder.
- Caller needs to visit bank first to get cash before paying -- requires callback arrangement.
- Partial payment toward a larger balance where caller is confused about the correct amount.
- Payment attempted through carrier IVR system where caller has difficulty navigating the automated phone tree.
- Card saved via online Pay Now system not accessible in the billing system (separate systems at Auto Owners).

**Automation Feasibility:** High
Rationale: Payment processing is the most automatable of all engagement types. The workflow is highly structured: verify identity, look up balance, collect payment info, process payment, send confirmation. An estimated 70-80% of payment calls could be fully automated with: (a) integrated carrier payment APIs or portal automation, (b) PCI-compliant voice payment collection (IVR or AI voice agent with secure card capture), and (c) automated confirmation delivery. The biggest blocker is carrier fragmentation -- each carrier has a different payment system, and some (like Auto Owners) have known quirks between their online and billing systems. Auto-pay/EFT setup adds complexity due to e-signature requirements. A realistic Phase 1 could automate simple one-time card payments (50-60% of volume) while routing EFT setup and edge cases to humans.

**What the AI Agent Must Do:**
- Process credit card and debit card payments through Progressive's portal, Auto Owners' billing system, National General's payment interface, Penn National, Cincinnati, Travelers, Foremost, Utica National, and Liberty Mutual's payment systems
- Collect and securely handle card numbers, expiration dates, CVVs, and billing zip codes in a PCI-compliant manner
- Set up recurring ACH/EFT payments by collecting routing and account numbers, sending e-signature authorization forms (Conga Sign for Penn National, carrier-specific forms for others), and configuring draft dates
- Disclose processing fees before charging ($4 credit card fee) and explain payment plan options (monthly vs. pay-in-full discounts)
- Generate and deliver payment confirmation numbers verbally and via email/text receipt
- Handle multi-policy payment consolidation (e.g., paying auto and renters in the same call)
- Recognize when a payment cannot be processed (canceled account pending reinstatement, underwriting hold) and route appropriately
- Support Spanish-language payment processing to expand capacity
- Confirm next payment date and amount after processing so the caller knows what to expect going forward

---

## Renewal Review (~133 calls, 8.5%)

**Typical Caller:** An existing customer who has received a renewal notice showing a premium increase, or an Alliance agent proactively reaching out 30 days before renewal to review the policy. The customer wants to understand why their rate went up, whether they are still getting the best deal, and what their options are. A significant subset involves carriers exiting the NC market (Main Street America, NGM Insurance) forcing involuntary carrier transitions.

**Resolution Workflow:**
1. Pull up the customer's current policy details: carrier, coverage levels, deductibles, premium, renewal date, and any recent changes.
2. Identify the source of any premium change:
   - NC state-mandated rate increases (7.5% homeowners hike commonly cited)
   - Inflation guard endorsement automatically increasing dwelling coverage
   - Updated replacement cost estimates
   - ISO rating changes
   - Claims history or credit score changes
   - Loss of multi-policy discount (if a bundled policy was canceled)
   - Dynamic Driver / telematics app inactivity removing discount
3. Explain the rate change to the customer in plain language, acknowledging their frustration.
4. Explore cost-reduction options on the current policy:
   - Increase deductibles ($1K to $2.5K can yield meaningful savings)
   - Remove optional coverages (towing, rental car)
   - Verify all applicable discounts are active (paperless, autopay, bundling, alarm system)
5. If the increase is significant or the customer requests it, reshop across Alliance's carrier panel:
   - Run comparison quotes from Progressive, Auto Owners, Cincinnati, National General, Penn National, Northwest Farmers, SafeCo, Westfield, Grange, Foremost, Heritage, and others
   - Compare not just price but coverage equivalency (same limits, same deductibles, same endorsements)
6. If the carrier is non-renewing (Main Street America exiting NC, NGM withdrawal), proactively reshop and present alternatives before the policy lapses.
7. Present comparison options with specific savings figures (e.g., "$2,556/year with Cincinnati vs. $1,632/year current with Progressive").
8. If the customer wants to switch, initiate the carrier transition: new policy binding, old policy cancellation coordination, and payment method setup.
9. If the customer stays with the current carrier, confirm renewal, verify payment method (escrow vs. direct), and confirm effective date.
10. Send the renewal summary or new policy proposal via email for review.

**Required Knowledge:**
- NC state rate mandates, their timing, and how they cascade through carriers
- Inflation guard endorsements and replacement cost estimator tools -- how dwelling coverage automatically increases and why
- ISO rating system and how protection class changes affect homeowners premiums
- Deductible adjustment impact on premiums (specific dollar savings for each deductible tier)
- Multi-carrier comparison methodology: ensuring apples-to-apples coverage equivalency across different carriers
- NC market dynamics: which carriers are exiting (Main Street America, NGM Insurance), which are restricting new business, and how this affects renewal options
- Bundling discount mechanics: how canceling one line (auto) affects the renewal price of the other (home) due to multi-policy discount loss
- Escrow payment processes for homeowners policies billed through mortgage companies
- Telematics/usage-based insurance programs (Progressive Snapshot, Dynamic Driver) and their discount impact
- Short-rate cancellation penalties if the customer switches mid-term vs. waiting for renewal
- Property underwriting factors that affect reshop eligibility: roof age, electrical panel type, claims history, prior coverage gaps

**Systems & Tools:**
- Alliance Insurance internal quoting/policy management system
- Progressive portal and pricing system
- Auto Owners portal
- Cincinnati Insurance system
- National General portal
- Penn National system
- Northwest Farmers Mutual
- Westfield, SafeCo, Grange, Foremost, Heritage, Main Street America, NGM portals
- Farm Bureau (as a current-carrier reference for comparison)
- Replacement cost estimator tool
- Marblebox quoting tool
- Glove Box app (customer-facing policy management)
- Alliance Insurance customer portal (myallianceinsurance.com)
- Email system for proposal delivery
- Internal policy management and rate comparison systems

**Outcome Distribution:**
- callback_needed: ~74% (98/133). Renewal reviews almost always require reshop, which takes 1-2 business days to run through multiple carrier systems.
- resolved: ~21% (28/133). Cases where the agent can explain the increase, confirm the customer wants to stay, and close the renewal on the spot -- or outbound calls where the agent presents a pre-prepared comparison.
- voicemail: ~1%. Proactive outbound attempts where the customer did not answer.
- transferred: ~1%. Routed to specialist for commercial renewals or unusual risks.

**Edge Cases & Escalation Triggers:**
- Carrier exiting NC market entirely (Main Street America, NGM Insurance), leaving all affected customers without coverage at renewal -- requires urgent reshop for every affected policyholder.
- Policy non-renewed due to underwriting issue (unfenced pool) requiring a carrier with different underwriting criteria.
- Entire commercial policy non-renewed by Westfield, negotiated to only non-renew the auto portion -- requires complex partial carrier transition.
- Customer confused by pre-renewal notice thinking their policy already renewed prematurely.
- Premium increase driven by ISO rating change that the agent cannot fully explain -- requires carrier underwriting escalation.
- Customer losing multi-policy discount after canceling auto with the same carrier, causing a cascade increase on the home policy.
- Farm policy at the same address as primary dwelling causing confusion between the two policies.
- Customer's Dynamic Driver app went inactive, silently removing a telematics discount and increasing the premium.
- Complex multi-policy review involving home, auto, umbrella, and potential farm transition -- requires senior agent with full product knowledge.
- Property not yet closed on, with confusion across multiple policy versions in the Glove Box app.

**Automation Feasibility:** Low
Rationale: Renewal reviews are the least automatable of this group. The core value is consultative: understanding the customer's situation, explaining rate changes in context, recommending cost-reduction strategies, and navigating emotionally charged conversations about rising costs. While an AI agent could handle the data retrieval (pulling current policy details, explaining standard rate increase factors), the competitive reshop across 10-15 carriers, the coverage equivalency analysis, and the consultative recommendation all require deep institutional knowledge and judgment. Approximately 15-20% could be automated (simple "confirm my renewal" calls where nothing changed), but the vast majority involve either rate frustration requiring empathetic explanation or active reshop requiring human producer expertise. The NC market disruption (carrier exits, non-renewals) adds a layer of complexity that changes quarterly and requires current market intelligence.

**What the AI Agent Must Do:**
- Pull current policy details (carrier, coverage, deductibles, premium, renewal date) and identify any changes from the prior term
- Explain the specific factors driving a premium increase: NC state mandates, inflation guard, ISO changes, claims surcharges, discount losses -- using plain language, not jargon
- Calculate the premium impact of deductible adjustments and coverage modifications so the customer can make informed cost-reduction decisions
- Verify that all applicable discounts are active (paperless, autopay, bundling, alarm, telematics) and flag any that were inadvertently removed
- Identify when a carrier is non-renewing in NC and proactively flag affected customers for reshop before lapse
- Present multi-carrier comparison quotes with specific dollar figures and coverage equivalency analysis
- Coordinate carrier transitions when a customer decides to switch: bind the new policy, cancel the old one, and handle payment method migration without creating a coverage gap
- Handle the emotional reality that many callers are experiencing financial pressure from rising insurance costs, sometimes compounded by mortgage escrow increases -- acknowledge, empathize, and provide concrete options

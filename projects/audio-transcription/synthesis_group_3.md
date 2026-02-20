# Capability Specifications: Group 3

Synthesized from 5 batch digests per engagement type, covering cancellation, coverage-modification, reinstatement, mortgage-lender, and info-update.

---

## Policy Cancellation (58 calls, 3.8%)

**Typical Caller:** Policyholder (or a family member acting on their behalf) who wants to cancel one or more policies due to selling property, switching carriers, relocating out of state, closing a business, dissatisfaction with rates, or inability to get specialized coverage (e.g., Airbnb). Some callers are frustrated after leaving unreturned voicemails.

**Resolution Workflow:**

1. Verify caller identity using name, phone number, and policy number in Alliance Insurance's internal policy database.
2. Confirm which policies the caller wants to cancel (often multiple -- home + auto + umbrella, or GL + WC for commercial) and the desired effective date.
3. Explain cancellation consequences: potential short-rate penalties (NC auto), pro-rata refund calculations (home/umbrella), audit obligations for commercial policies, DMV notification and potential FS-1 requirements for auto, and coverage gap risks if replacement policy is not yet active.
4. Advise the caller to secure new coverage before the effective date to avoid a lapse, especially for auto (DMV implications) and mortgage-escrowed homeowners policies.
5. Send the carrier-specific cancellation form via email for electronic signature (Conga Sign or similar e-signature platform).
6. If the caller cannot locate the email, help them check spam folders and resend.
7. Once the signed form is returned, submit the cancellation to the carrier through the appropriate portal or email channel (e.g., CL@westfield.com for Westfield policies).
8. Stop any active bank draft or auto-pay arrangement to prevent further charges.
9. Confirm refund amount, method (check or card refund), and processing timeline.
10. For commercial policies, explain that audit obligations survive cancellation and the caller may receive an audit request from the carrier.

**Required Knowledge:**

- NC short-rate fee calculations for mid-term auto cancellations vs. pro-rata refund rules for homeowners/umbrella
- Carrier-specific cancellation form requirements and submission channels (Progressive, National General, Auto Owners, Farm Bureau, Westfield, Penn National, Safeco, Travelers)
- DMV notification rules -- when cancellation triggers a DMV alert and FS-1 filing requirement
- Commercial policy audit lifecycle -- cancellation does not eliminate audit obligations
- E-signature platform workflows (Conga Sign)
- Coverage gap prevention -- coordinating effective dates between old and new carriers
- Multi-policy cancellation alignment to prevent gaps (home + auto + umbrella must align)
- Escrow implications when canceling a homeowners policy with an active mortgage

**Systems & Tools:**

- Alliance Insurance internal policy database / management system
- Conga Sign (e-signature platform)
- Carrier portals: Progressive, National General, Auto Owners, Farm Bureau, Westfield, Penn National, Safeco, Travelers
- Westfield CL processing email (CL@westfield.com)
- Travelers email system
- Email system for sending/receiving cancellation forms
- Homer Auto system
- Alliance customer portal (myallianceinsurance.com)
- Texting support service (3367861133)

**Outcome Distribution:**

| Outcome | Count | % |
|---------|-------|---|
| callback_needed | 44 | 76% |
| resolved | 11 | 19% |
| transferred | 1 | 2% |
| (implied pending) | 2 | 3% |

76% of cancellation calls end unresolved, primarily because the cancellation form must be emailed, signed, and returned -- a multi-step asynchronous process. Resolved calls are those where the agent could process the cancellation immediately (e.g., the form was already signed, or it was a simple auto-draft stop). This is a strong candidate for automation of the form-send-and-track workflow.

**Edge Cases & Escalation Triggers:**

- **Caller doesn't actually want to cancel** -- auto-pay was inadvertently switched on; caller is angry about a charge but wants to keep coverage (exten-102-+13369184809-20251222)
- **Multi-policy cancellation with Airbnb coverage gap** -- four policies canceled because no carrier offers Airbnb coverage; complex refund coordination (exten-202-+13369958863-20251015)
- **Cancellation to avoid audit complications** -- caller lets policies lapse via non-payment rather than formally canceling, creating downstream problems (exten-106-+13364048139-20250926)
- **Out-of-state relocation** -- canceling after moving to Arkansas, already received DMV plate revocation notice; time-sensitive (in-+13363779003-+13309794865-20250725)
- **Backdated cancellation** -- caller sold property months ago and needs retroactive effective date with closing documents for refund (exten-112-+13367550075-20260113)
- **Multi-state vehicle titling** -- three vehicles titled in Georgia after relocating from NC, requiring tag surrender date coordination (q-300-+17065662679)
- **Carrier system unable to process cancellation** -- agent must contact carrier directly when system blocks the request
- **Cancellation email lost in spam** -- caller cannot find the e-signature email; agent must resend and help locate it
- **Frustrated caller after unreturned voicemails** -- caller demands immediate cancellation but previous messages were never answered

**Automation Feasibility:** Medium

Rationale: The core cancellation workflow is procedural and rule-based -- verify identity, explain consequences, send form, process return. An AI agent could handle steps 1-5 (intake, explanation, form dispatch) in approximately 60% of cases. However, the e-signature requirement creates an inherent asynchronous break that cannot be eliminated. The biggest blockers are: (1) carrier-specific form routing requires maintaining a playbook for 8+ carriers, (2) edge cases like backdated cancellations and audit complications require human judgment, and (3) the retention opportunity (callers who don't really want to cancel) requires nuanced conversation skills. Approximately 40% could be fully automated end-to-end (simple single-policy cancellations with standard effective dates); another 30% could be partially automated (AI handles intake and form dispatch, human handles completion).

**What the AI Agent Must Do:**

- Look up policies across Alliance Insurance's internal database using name, phone number, or policy number and confirm which policies the caller wants to cancel
- Explain NC-specific short-rate vs. pro-rata refund calculations for each policy type being canceled
- Generate and send carrier-specific cancellation forms via email using Conga Sign, with the correct carrier submission channel pre-configured
- Track whether the e-signature form has been returned and trigger follow-up reminders if not
- Stop active bank drafts and auto-pay arrangements through carrier portals (Progressive, Auto Owners, National General)
- Calculate and communicate expected refund amounts and processing timelines per carrier
- Detect retention opportunities -- when the caller's actual problem (incorrect charge, coverage question) doesn't require cancellation -- and redirect the conversation
- Coordinate multi-policy cancellation effective dates to prevent coverage gaps
- Warn about DMV implications for auto cancellations and initiate FS-1 filing if needed
- Explain surviving audit obligations for commercial policy cancellations
- Handle Spanish-language cancellation requests

---

## Coverage Modification (48 calls, 3.1%)

**Typical Caller:** Existing policyholder looking to reduce costs by adjusting deductibles, dropping full coverage to liability-only on older/paid-off vehicles, removing optional coverages (towing, rental, cargo), or adding/increasing coverages (umbrella from $1M to $2M, uninsured motorist, comprehensive). Some are commercial clients adjusting workers' comp payroll, liability limits, or transitioning policy types (landlord to owner-occupied, rental to personal use).

**Resolution Workflow:**

1. Verify caller identity and pull up the relevant policy in Alliance's policy database.
2. Identify the specific modification requested -- deductible change, coverage add/remove, liability limit adjustment, or policy type transition.
3. Calculate the premium impact of the requested change (e.g., increasing deductible from $500 to $1,000 reduces premium by $X/month; dropping full coverage to liability saves $Y/month).
4. Present the trade-offs clearly: what the caller gains in savings vs. what coverage protection they lose.
5. Process the endorsement through the appropriate carrier portal (Auto Owners, Progressive, National General, Cincinnati, Westfield, Foremost).
6. For commercial modifications, verify payroll figures and adjust workers' comp or GL premiums accordingly to avoid audit penalties.
7. Confirm updated premium amount and next billing date.
8. Send updated policy documents via email or mail.
9. For umbrella policy changes, verify that underlying auto/home liability limits still meet umbrella requirements.

**Required Knowledge:**

- Coverage types and their cost implications: collision, comprehensive, liability, towing, rental reimbursement, uninsured/underinsured motorist, umbrella, equipment breakdown, cargo, excess liability
- Deductible-to-premium trade-off calculations across carriers
- Full coverage vs. liability-only distinctions and when each is appropriate (vehicle age, loan status, value)
- Umbrella policy requirements -- minimum underlying auto/home liability limits
- Workers' comp payroll audit implications when adjusting coverage mid-term
- NC state-specific coverage forms and requirements
- Commercial policy transitions (landlord to owner-occupied, rental to personal use, commercial to personal)
- Carrier-specific endorsement processing workflows
- Rate adjustment negotiation (e.g., debits being negotiated from 40% to 20% in Virginia)
- System limitations regarding pending updates and grace periods

**Systems & Tools:**

- Alliance Insurance policy database / management system
- Carrier portals: Auto Owners, Progressive, National General, Cincinnati Insurance, Westfield, Foremost, Chubb
- Auto One system
- Whistle (carrier system)
- Email systems for sending updated policy documents
- Carrier underwriting portals for endorsement submissions

**Outcome Distribution:**

| Outcome | Count | % |
|---------|-------|---|
| callback_needed | 32 | 67% |
| resolved | 16 | 33% |

Coverage modifications resolve at a higher rate (33%) than cancellations because many changes can be processed immediately through carrier portals. The 67% callback rate often reflects cases where the agent needs to check premium impact, coordinate with underwriting, or wait for system processing. This is a strong automation target -- the premium calculation and endorsement submission are largely mechanical.

**Edge Cases & Escalation Triggers:**

- **Carrier declines modification** -- carrier will not add additional insured because operations fall outside underwriting appetite (exten-102-+16072713116-20251014)
- **Commercial-to-personal transition** -- mobile home policy changing from rental to personal use for a disabled daughter's training ground; requires underwriting review (out-4342501427-501-20260102)
- **Payroll audit avoidance** -- adjusting insurance for a second crew requires payroll increase to avoid audit penalties (exten-207-+13367560515-20251218)
- **Uninsured motorist discrepancy** -- policy document shows "no cost" for UM coverage; agent needs carrier consultation to resolve (q-300-+13365675218)
- **Rate adjustment negotiation** -- debit being negotiated from 40% to 20% in Virginia; requires underwriting communication (exten-207-+17045499908-20250730)
- **Billing dispute triggers coverage change** -- caller upset about premium increase; deductible increase and coverage change used as cost-reduction solution (q-300-+13365541577-20251014)
- **Health insurance crossover** -- caller wants to add a new baby to health insurance policy, which follows different procedures than P&C (out-3365964620-+13364034763-20250923)

**Automation Feasibility:** Medium-High

Rationale: Coverage modifications are the most mechanical of this group. Approximately 50% of calls follow a straightforward pattern: caller wants to change a deductible or drop coverage on an older vehicle, agent calculates the premium impact and processes it. These are strong automation candidates. The blocker is carrier fragmentation -- each carrier portal has different endorsement submission workflows. An AI agent with carrier-specific playbooks could handle the calculation and recommendation immediately and submit the endorsement. The remaining 50% involve judgment calls (is liability-only appropriate for this vehicle?), underwriting consultations, or commercial policy complexity that requires human escalation.

**What the AI Agent Must Do:**

- Pull up policy details and current coverage configuration from Alliance's database and present them clearly to the caller
- Calculate premium impact of deductible changes across carriers (Auto Owners, Progressive, National General, Cincinnati, Westfield) and present savings vs. coverage trade-offs
- Process endorsements through carrier portals to add, remove, or modify coverages (collision, comprehensive, towing, rental, umbrella, uninsured motorist)
- Downgrade coverage from full to liability-only on paid-off or aging vehicles, with clear explanation of what the caller loses
- Verify umbrella policy underlying limit requirements before processing auto or home coverage reductions
- Adjust commercial policy parameters: workers' comp payroll figures, GL limits, cargo/excess liability coverages
- Handle policy type transitions (landlord to owner-occupied, commercial to personal) with appropriate underwriting coordination
- Send updated policy documents and billing confirmations via email after processing changes
- Flag cases that require underwriting approval and initiate the referral with all relevant details

---

## Policy Reinstatement (46 calls, 3.0%)

**Typical Caller:** Policyholder whose policy was canceled for non-payment (missed bank draft, NSF check, hacked debit card, closed bank account, or simply forgot to pay) and now urgently needs coverage restored. Often stressed -- they may have received a DMV notice, been pulled over without proof of insurance, or discovered the lapse when filing a claim. Some are commercial clients whose GL, workers' comp, or business auto lapsed due to a single missed payment.

**Resolution Workflow:**

1. Verify caller identity and locate the canceled policy in Alliance's system.
2. Determine the cancellation reason (non-payment, NSF, missed draft, underwriting non-renewal, failure to provide documentation like roof repair proof).
3. Check the cancellation date and determine whether the policy is within the carrier's reinstatement window (varies: 10 days for some, 30 days standard, up to 60 days for others).
4. If within the reinstatement window:
   a. Calculate the total amount due (past-due premiums + any reinstatement fees + NSF fees if applicable).
   b. Collect a verbal or written statement of no loss from the policyholder (confirming no claims occurred during the lapse period).
   c. Send e-signature document for statement of no loss via Conga Sign if written form is required.
   d. Process the full past-due payment.
   e. Contact the carrier's underwriting department to request reinstatement approval (may require phone call or email to carrier).
   f. Confirm reinstatement and provide updated proof of insurance.
5. If past the reinstatement window:
   a. Explain that the policy must be rewritten as a new policy.
   b. Gather updated information and begin new policy quoting process.
6. Address the underlying payment issue to prevent recurrence (update banking details, set up new auto-pay, fix hacked card).

**Required Knowledge:**

- Carrier-specific reinstatement windows: Travelers (strict, may refuse after multiple prior cancellations), National General (standard 30-day window), Auto Owners, Westfield, Progressive (30-day window for umbrella), Safeco, NCJUA, Utica National, Nationwide
- Statement of no loss requirements (verbal vs. written, carrier-specific)
- NSF fee handling and payment reprocessing
- Reinstatement fee structures per carrier
- Underwriting approval processes -- when reinstatement requires underwriter flag activation vs. automatic processing
- Policy rewrite procedures when reinstatement window has passed
- DMV implications of auto policy lapse and FS-1 re-filing
- EFT/banking detail update procedures to prevent future lapses
- Audit premium disputes and how unpaid audit balances interact with reinstatement eligibility
- Coverage gap implications for mortgage-escrowed homeowners policies

**Systems & Tools:**

- Alliance Insurance internal policy database / management system
- Conga Sign (e-signature for statement of no loss)
- Carrier portals and underwriting departments: Travelers, National General, Auto Owners, Westfield, Progressive (Home Umbrella Underwriting), Safeco, NCJUA, Utica National, Nationwide Commercial Lines
- Payment processing system
- Auto-pay enrollment portal
- Email systems for carrier communication and document delivery
- Alliance customer portal (myallianceinsurance.com)

**Outcome Distribution:**

| Outcome | Count | % |
|---------|-------|---|
| callback_needed | 30 | 65% |
| resolved | 14 | 30% |
| transferred | 0-1 | ~2% |

Reinstatement has the highest resolution rate in this group (30%) because many can be processed in a single call when the carrier window is open and the caller can pay immediately. The 65% callback rate reflects cases requiring underwriting approval, statement of no loss signatures, or investigation into what caused the cancellation.

**Edge Cases & Escalation Triggers:**

- **Carrier refuses reinstatement** -- Travelers refusing after multiple prior cancellations; no flexibility (exten-112-+13366826205-20250922)
- **Mortgage company payment dispute** -- reinstatement complicated by escrow confusion between policyholder, mortgage company, and carrier (exten-206-+13365293608-20250827)
- **Multiple policies canceled from single NSF** -- GL, inland marine, and business auto all canceled due to one returned payment; requires coordinated reinstatement across all three (out-8002112843-207-20250930)
- **Hacked debit card disrupted auto-pay** -- workers' comp policy lapsed because card was compromised; caller needs new payment method and reinstatement (q-300-+13366074877)
- **Umbrella past reinstatement window** -- Progressive umbrella beyond 30-day window; must be rewritten entirely (out-8662748765-112)
- **Roof repair documentation** -- policy canceled for missing proof of roof repair; reinstatement requires photos plus statement of no loss plus payment (out-3362878382-501-20251215)
- **Caller on construction site** -- unable to sign statement of no loss because they have no computer access; need alternative signing method (out-3362091127-103-20251023)
- **Audit premium dispute** -- reinstatement blocked by unpaid audit invoices requiring clarification before carrier will approve (out-13364087685-206-20250910)
- **Farm size change affecting underwriting** -- home policy reinstatement pending underwriting review of farm size change plus missed payment reason (parked-302-302-20251124)
- **Renters insurance** -- requires full re-establishment rather than simple reinstatement due to carrier policies (exten-401-+14076944253-20251107)

**Automation Feasibility:** Low-Medium

Rationale: Reinstatement is inherently multi-party -- it requires the policyholder, the agency, and the carrier's underwriting department to coordinate. An AI agent could handle the intake (steps 1-3) and payment collection (step 4d) effectively, covering approximately 30% of the work. However, the carrier approval step is the critical bottleneck: many reinstatements require a phone call or email to the carrier's underwriting team and waiting for a response, which cannot be automated. The biggest blockers are: (1) carrier-specific reinstatement rules are complex and sometimes discretionary (Travelers may refuse based on history), (2) statement of no loss collection via e-signature creates an async break, and (3) edge cases like audit disputes and mortgage company conflicts require human negotiation. Approximately 20-25% of reinstatement calls could be fully automated (within window, single policy, caller can pay immediately, no complications).

**What the AI Agent Must Do:**

- Look up canceled policies and determine cancellation date, reason, and carrier
- Calculate whether the policy falls within the carrier-specific reinstatement window (maintaining a reference table of windows per carrier: Travelers, National General, Auto Owners, Westfield, Progressive, Safeco, NCJUA, Utica National, Nationwide)
- Calculate the total reinstatement cost: past-due premiums + reinstatement fees + NSF fees
- Collect verbal statement of no loss and record it, or send the written form via Conga Sign for e-signature
- Process full past-due payment via credit card, debit card, or bank account
- Submit reinstatement request to carrier underwriting via the appropriate channel (portal, email, phone bridge)
- Track underwriting approval status and proactively notify the caller when reinstatement is confirmed
- When past the reinstatement window, seamlessly transition to the new-quote workflow with pre-populated information from the canceled policy
- Update banking/payment details to prevent future lapses (new card number, corrected routing number, fresh EFT authorization)
- Handle Spanish-language reinstatement requests
- Detect and flag multi-policy situations where a single payment failure cascaded to multiple cancellations

---

## Mortgage / Lender Coordination (41 calls, 2.7%)

**Typical Caller:** Either a homeowner confused about the intersection of their insurance and mortgage (escrow increases, missing proof of insurance, hazard insurance letters) or a mortgage company representative (from NewRes, PHH Mortgage, Movement Mortgage, Van Dyke Mortgage, etc.) confirming coverage, requesting evidence of insurance, or updating mortgagee information. About 30% of calls come from lender representatives rather than policyholders.

**Resolution Workflow:**

1. Identify whether the caller is a policyholder or a lender representative -- the workflow diverges significantly.
2. For **policyholders**:
   a. Verify identity and pull up the homeowners policy.
   b. Identify the mortgage-related issue: escrow payment confusion, missing proof of insurance letter from mortgage company, mortgagee clause update needed, refinancing coordination.
   c. If escrow confusion: explain how insurance premiums flow through the mortgage company's escrow account, why the escrow amount may have changed, and what the caller can do (contact mortgage company vs. adjust insurance).
   d. If proof of insurance needed: generate and send the declaration page or evidence of insurance to the mortgage company via fax, email, or mycoverageinfo.com portal.
   e. If mortgagee update needed (refinancing, new lender, loan transfer): collect new mortgagee clause details (lender name, address, loan number) and update the policy.
   f. If cancellation-related: explain the NLC (Notice of Lapse of Coverage) timeline and that actual cancellation occurs weeks after the notice.
3. For **lender representatives**:
   a. Verify the lender's identity and the policy they're inquiring about.
   b. Confirm mortgagee listing on the policy.
   c. Send evidence of insurance, binder, or declaration page via fax or email.
   d. Process mortgagee additions or changes as requested.
   e. Provide payment address verification and policy renewal details.

**Required Knowledge:**

- Escrow account mechanics -- how insurance premiums are collected through mortgage payments and why escrow adjustments happen
- Mortgagee clause formatting and requirements (exact lender name, ISAOA/ATIMA designations, loan numbers)
- Difference between "insured build" and "mortgagee build" policy designations
- mycoverageinfo.com portal for sending proof of insurance to lenders
- Fax and email protocols for different mortgage companies
- How refinancing affects insurance policies -- mortgagee changes, loan number updates, potential coverage requirement changes
- Hazard insurance vs. homeowners insurance terminology (lenders often use "hazard" while policies say "homeowners")
- NLC (Notice of Lapse of Coverage) timeline -- the gap between notice and actual cancellation
- Deductible requirements that some lenders impose as a condition of the mortgage
- Full coverage requirements for auto policies with lienholders

**Systems & Tools:**

- Alliance Insurance internal policy database / management system
- mycoverageinfo.com (lender communication portal)
- Carrier portals: Travelers, Cincinnati Insurance, Auto Owners, Safeco
- Email systems (support@myallianceinsurance.com)
- Fax systems for lender communication
- Mortgage company portals/contacts: Carington Mortgage, Mr. Cooper, Freedom Mortgage, M T Bank, Lakeview Loan Servicing, Movement Mortgage, PennyMac, CU Mortgage, Civic Federal Credit Union, Round Point Mortgage, Truline, Merisave, PHH Mortgage Services, CMG Mortgage, Truest Bank, State Employees Credit Union, Prosperity Home Mortgage, Van Dyke Mortgage, Gilda Mortgage, Fulmain

**Outcome Distribution:**

| Outcome | Count | % |
|---------|-------|---|
| callback_needed | 35 | 85% |
| resolved | 6 | 15% |

This type has the highest callback rate (85%) in this group. The reason is structural: most mortgage-lender calls require coordination between three parties (policyholder, agency, and mortgage company). Sending proof of insurance to a lender, updating a mortgagee clause, or resolving an escrow discrepancy typically cannot be completed during the initial call. The 15% resolved cases are simple confirmations (yes, your policy is active; yes, NewRes is listed as mortgagee).

**Edge Cases & Escalation Triggers:**

- **Financial crisis from escrow increase** -- third-party handled insurance cancellation, causing escrow to skyrocket and creating severe financial strain for the caller (exten-113-+13364528352-20260109)
- **Lender prohibits escrow adjustment** -- loan conversion policies prevent the escrow change the caller needs (exten-401-+17034251204-20250821)
- **Refinancing in progress** -- mortgage company requesting removal from policy during active refinancing that hasn't completed; premature removal would violate loan terms (out-4076376468-402-20251104)
- **Missing mortgage payment** -- payment mailed October 9th but not received; agent traces through multiple department transfers (out-9194208110-510)
- **Mortgagee build change** -- policy needs designation changed from "insured build" to "mortgagee build" -- obscure distinction that matters for lender compliance (q-300-+12134760469-20250828)
- **40-minute hold frustration** -- caller spent 40 minutes on hold trying to add mortgage to policy before reaching anyone (in-+13363779003-+13104622910-20251211)
- **Conflicting information** -- mortgage company says no insurance on file despite policy being active for months; requires investigation and documentation resend
- **Check discrepancy** -- settlement company and carrier disagree on payment amounts; requires escrow team coordination (exten-100-+13103659076-20250909)

**Automation Feasibility:** Medium

Rationale: Mortgage-lender coordination splits into two distinct automation profiles. Lender representative calls (30% of volume) are highly automatable -- they follow a predictable pattern of "confirm coverage, send proof" that an AI agent could handle in 80%+ of cases. Policyholder escrow confusion calls are harder because they require explaining complex financial flows and often end with "you need to call your mortgage company." The biggest blocker is the three-party coordination: the AI agent can send documents to lenders and update mortgagee clauses, but resolving discrepancies between what the carrier shows and what the mortgage company expects often requires human investigation. Approximately 35% could be fully automated (lender confirmation calls, simple proof-of-insurance sends); another 30% could be partially automated (intake and document generation, with human handoff for discrepancy resolution).

**What the AI Agent Must Do:**

- Distinguish between policyholder calls and lender representative calls and route to the appropriate workflow
- Verify mortgagee listings on homeowners policies and confirm coverage status for lender inquiries
- Generate and send evidence of insurance, declaration pages, and binders to mortgage companies via fax, email, or the mycoverageinfo.com portal
- Update mortgagee clause information on policies: add/remove/change lender name, address, loan number, and designation (insured build vs. mortgagee build)
- Explain escrow mechanics clearly to confused policyholders -- how insurance premiums flow through the mortgage company, why escrow amounts change, and what steps to take
- Coordinate mortgagee changes during refinancing: collect new lender details, remove old lender, confirm timing
- Track proof-of-insurance delivery to lenders and confirm receipt
- Maintain a reference database of mortgage company contact information, fax numbers, and preferred communication methods for the 20+ lenders referenced in call data
- Handle hazard insurance terminology translation (lenders say "hazard," policies say "homeowners")
- Flag and escalate discrepancy cases where the carrier record and mortgage company expectations conflict

---

## Policy Info Update (35 calls, 2.1%)

**Typical Caller:** Existing policyholder who needs to update administrative information -- new address (moving), changed email, phone number update, name change (divorce/marriage), DBA correction, payment method update (new bank account, corrected routing number), finance company change on auto policy, or correction of errors made during enrollment (wrong household member added, address typo). Generally low-stress, straightforward requests.

**Resolution Workflow:**

1. Verify caller identity using existing policy information.
2. Identify the specific update needed: address, email, phone, name, DBA, payment method, finance company/lienholder, or error correction.
3. For **address changes**:
   a. Collect the new address and effective date of the move.
   b. Update across all active policies (auto, home, renters, umbrella, commercial) -- addresses must be synchronized.
   c. For homeowners: coordinate with mortgage company if the change affects escrow.
   d. For auto: check whether the new address is still in NC; out-of-state moves may require carrier change.
   e. Send updated evidence of insurance or declaration page.
4. For **name changes**:
   a. Collect documentation requirements (carrier-specific -- some require divorce decree or marriage certificate).
   b. Process through carrier portal.
5. For **payment method updates**:
   a. Collect new banking details (routing number, account number) or card information.
   b. Update auto-pay/EFT authorization across all relevant policies.
   c. For carrier portal updates (e.g., Auto Owners online): may require the customer to log in with old credentials first.
6. For **lienholder/finance company changes**:
   a. Collect new finance company name and address.
   b. Update the policy and fax/email confirmation to the new finance company.
7. For **error corrections** (wrong household member, typos):
   a. Generate e-signature document confirming the correction.
   b. Submit correction through carrier portal (e.g., Safeco Agent Portal "Policy Inception Date Change" form).
8. Confirm all changes are complete and send updated documents.

**Required Knowledge:**

- Multi-policy address management -- which policies need updating when a customer moves and how to sync them
- Carrier portal navigation for account-level changes (Auto Owners online portal, National General portal, Safeco Agent Portal)
- Address changes that trigger underwriting review (moving to a higher-risk area, out-of-state)
- Name change documentation requirements per carrier
- Banking terminology and verification (routing numbers vs. account numbers)
- DBA update procedures and how they link to policy records
- E-signature processes for correction documentation
- Lienholder update procedures and fax/email delivery requirements
- NC-specific implications of address changes on auto insurance rates
- Email update procedures that require old credential login before new email can be set (Auto Owners)
- Paperless discount preservation -- correcting email addresses before carrier deadlines (Progressive)

**Systems & Tools:**

- Alliance Insurance internal policy database / management system
- Carrier portals: Auto Owners online portal, National General portal, Safeco Agent Portal, Progressive, Travelers, Universal Property and Casualty
- E-signature platforms (for correction documentation)
- Email system (support@myallianceinsurance.com)
- Electronic fax systems (for lienholder/finance company updates)
- Account management system (for payment and address verification)
- Billing account portal

**Outcome Distribution:**

| Outcome | Count | % |
|---------|-------|---|
| callback_needed | 23 | 66% |
| resolved | 12 | 34% |

Info updates resolve at 34%, the second-highest in this group. Resolved cases are straightforward single-update requests where the agent can process the change immediately. The 66% callback rate reflects cases requiring carrier portal processing time, multi-policy coordination, or documentation (e.g., name change proof, e-signature for corrections).

**Edge Cases & Escalation Triggers:**

- **VIN discrepancy** -- registration card shows 2001 Nissan but policy says 2000; requires statement of no losses and registration card copy to resolve (exten-113-+13362874668-20251113)
- **DBA system display issues** -- updating DBA from "Hernandez Lions" to "Julio Installer LLC" causes display problems in the billing system (exten-207-+18885088622-20250903)
- **Email update requires old credentials** -- changing email on Auto Owners portal requires customer to log in with old email and password first, which they've lost (out-8003460346-501-20251212)
- **Paperless discount deadline** -- correcting email address on Progressive policy to restore paperless discount before carrier deadline; time-sensitive (out-8777762436-409-20251114)
- **Wrong household member added during renewal** -- Safeco accidentally added Edward Bacon as household member; requires e-signed document confirming he is not a resident (out-3365293868-114-20260108)
- **Address change combined with cancellation** -- caller updating address but also wants to cancel; dual-intent call (exten-100-+13367109204-20250826)
- **Canadian address update** -- policyholder moved to Canada; country change requires different procedure than domestic moves (exten-113-+17045499908-20251017)
- **Routing/account number confusion** -- caller previously gave account number instead of routing number; needs correction to avoid failed payment (in-+13363779003-+13369970484-20250909)

**Automation Feasibility:** High

Rationale: Policy info updates are the most automatable type in this group. The majority follow a predictable pattern: caller provides new information, agent updates the system, confirmation is sent. Approximately 60% of these calls could be fully automated: address changes, phone/email updates, and payment method changes are all procedural tasks that an AI agent with carrier portal access could handle end-to-end. The biggest blocker is carrier portal fragmentation -- each carrier has different update workflows, and some (like Auto Owners) have non-intuitive processes (requiring old credentials to update email). Another 20% could be partially automated (intake and processing with human verification for complex changes like DBA corrections or household member disputes). Only about 20% truly need human handling (out-of-state/country moves affecting coverage, error corrections requiring underwriting involvement).

**What the AI Agent Must Do:**

- Verify caller identity and locate all active policies associated with the caller across multiple carriers
- Update address information across all active policies simultaneously (auto, home, renters, umbrella, commercial), ensuring no policy is missed
- Process name changes through carrier portals with appropriate documentation collection
- Update payment methods (bank account, credit card, EFT authorization) across all relevant policies and carriers
- Navigate carrier-specific portal workflows for account-level changes: Auto Owners online portal login process, Safeco Agent Portal forms, National General portal, Progressive paperless settings
- Update lienholder/finance company information and send confirmation documents via fax or email to the new finance company
- Correct DBA names and business registration details in carrier systems
- Generate and send updated evidence of insurance, declaration pages, or ID cards after processing changes
- Detect when an address change crosses state lines and flag for agent review (coverage and carrier implications)
- Handle e-signature workflows for correction documentation (household member disputes, VIN corrections)
- Process effective date changes through carrier portals when policy dates need adjustment
- Proactively identify when an update affects multiple interconnected policies (e.g., address change on homeowners requires mortgage company notification)

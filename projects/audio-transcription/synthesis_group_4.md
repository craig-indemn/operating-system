# Capability Specifications: Group 4

## COI Request (~34 calls, 2.2%)

**Typical Caller:** Commercial clients — contractors, installers, plumbers, steel building companies — who need a certificate of insurance generated, corrected, or sent to a third party (general contractor, builder, rental company, municipality, HOA) so they can start or continue a job. These callers are often repeat requesters operating under deadline pressure.

**Resolution Workflow:**
1. Verify the caller's identity and locate their commercial policy in the Alliance Insurance policy database.
2. Confirm the certificate holder details: company name, full address, and email for delivery.
3. Determine the certificate type: standard COI, additional insured endorsement, or equipment-specific coverage notation.
4. Verify that the policy supports the requested coverage lines (GL, WC, commercial package, inland marine) and confirm coverage amounts match requirements — e.g., an equipment rental company may require $80,000 in rented/leased equipment coverage.
5. If the COI requires a DBA name (e.g., "FCR Holdings LLC DBA First Class Roofing"), confirm exact wording with the caller.
6. If an endorsement is needed (adding an additional insured), submit the endorsement request to the carrier (Auto Owners, Travelers, etc.) and track processing.
7. Generate the COI from the carrier system or internal certificate generator.
8. Email the COI to the specified recipient. If the recipient's email system requires a reply to trigger attachment download, explain this to the caller.
9. Confirm delivery with the caller or flag for follow-up if the endorsement is still processing.

**Required Knowledge:**
- Certificate holder vs. additional insured distinction — contractors frequently confuse these, and the wrong one delays jobs
- DBA naming conventions and how they must appear on certificates
- Coverage line verification: GL, WC, commercial auto, inland marine, commercial package
- Equipment rental coverage requirements (specific dollar amounts for telehandlers, cranes, etc.)
- Per-carrier COI generation processes — Auto Owners, Travelers, Builders Mutual, USLI each have different portals
- HOA master hazard policy certificates and NC condo act requirements
- Project-specific endorsement wording for university bids and municipal contracts
- Urgency protocols — COIs are often needed same-day for a job to start

**Systems & Tools:**
- Certificate generator system (internal)
- Carrier portals: Auto Owners, Travelers, USLI, Builders Mutual, Cincinnati
- COIS database
- GloveBox client hub
- Alliance Insurance policy database
- Email system (support@myallianceinsurance.com)
- Doc Sign / Conga Sign (for endorsement signatures)
- Internal agent directory (routing to Gloria, Jeff, Amani, or other commercial agents)

**Outcome Distribution:**
- callback_needed: 25 of 34 (74%)
- resolved: 8 of 34 (24%)
- transferred: 1 (~3%)
- voicemail: 1 (~3%)

The high callback rate stems from endorsements requiring carrier processing time and from calls that arrive when the responsible commercial agent (Gloria, Jeff, Cody) is unavailable. The actual COI generation — once the endorsement is in place — is fast. Automation could close the gap by generating standard COIs instantly and tracking endorsement status proactively.

**Edge Cases & Escalation Triggers:**
- COI needed before a policy is actually issued — caller wants a preview certificate for a bid submission (file: exten-106-+13367505898-20250730)
- Equipment rental requiring a mid-term coverage amount increase from $25K to $80K, needing underwriter approval (file: exten-207-+13042963047-20251114)
- COI correction with missing project address for a university bid — incomplete info stalls the process (file: exten-102-+13367823384-20251024)
- HOA master hazard policy certificate requested by a mortgage holder (New Res) — crosses into mortgage/lender coordination territory (file: in-+13363779003-+17042412363-20250829)
- Certificate approval bottleneck affecting customer relationships when agent is unresponsive for 24+ hours (file: in-+13363544000-+13363013103-20250827)
- Additional insured requirements for apartment complex rental (borderline between COI and renters policy context)
- Endorsement requires carrier voicemail follow-up, adding multi-day delay

**Automation Feasibility:** Medium-High
Rationale: Standard COI generation — where the policy already supports the requested coverage and no endorsement changes are needed — is highly automatable. This likely covers 50-60% of COI requests. The AI agent can verify policy details, confirm certificate holder information, generate the certificate, and email it within minutes. The blockers are: (1) requests requiring endorsement changes (adding additional insured, increasing equipment coverage) that need carrier processing, and (2) requests with ambiguous or incomplete information (missing DBA names, wrong coverage amounts). An AI agent could handle the intake and generation steps while escalating endorsement-dependent requests to a human, dramatically reducing the 74% callback rate.

**What the AI Agent Must Do:**
- Look up commercial policies by caller name, phone number, or policy number in the Alliance Insurance policy database
- Verify that requested coverage lines (GL, WC, commercial auto, inland marine) are active on the policy with sufficient limits
- Collect and validate certificate holder details: legal entity name, mailing address, and email address
- Distinguish between "certificate holder" and "additional insured" requests and ask clarifying questions when the caller uses them interchangeably
- Generate standard certificates of insurance from carrier-specific portals (Auto Owners, Travelers, Builders Mutual, USLI, Cincinnati)
- Email completed COIs directly to the specified recipient with proper subject lines
- Handle DBA name formatting (e.g., ensuring "FCR Holdings LLC DBA First Class Roofing" appears exactly as required)
- Track endorsement requests that are pending carrier processing and notify callers when the COI is ready
- Recognize repeat callers (contractors like Conterra Marble, North Edge Steel, Holbrook Plumbing) and pre-populate their certificate holder details from history
- Route requests requiring underwriter approval (coverage amount changes, new additional insured endorsements) to the commercial department with complete intake details

---

## Commercial / Specialty Inquiry (~28 calls, 1.8%)

**Typical Caller:** Business owners, contractors, or financial professionals seeking insurance for non-standard risks — builder's risk for construction projects, HOA/condo association coverage, dealer lot insurance, surety and performance bonds, church-affiliated programs, liquor liability, group health, life insurance, or land development projects. These callers often don't know exactly what coverage they need and require consultative guidance.

**Resolution Workflow:**
1. Identify the caller and determine whether they are an existing commercial client or a new prospect.
2. Listen to the coverage need and classify the specialty type: builder's risk, bond (surety/performance/bid), HOA/condo, dealer lot, church program, life/health, group insurance, or other niche commercial.
3. For existing clients: pull up their current policies to understand what coverage is already in place.
4. Gather risk details specific to the specialty type — for builder's risk: project address, construction value, timeline, certificate of occupancy date; for bonds: bond amount, project details, obligee; for dealer lots: inventory value, number of vehicles, location.
5. Determine carrier appetite — not all carriers write all specialties. Identify appropriate markets: USLI for specialty commercial, Church Mutual for religious organizations, Honeycomb for habitational, Builders Mutual for construction, Hartford Small Commercial for small business.
6. If Alliance cannot competitively write the risk (e.g., new auto dealer startups), refer the caller to another agency with that specialty.
7. Prepare and present quote options, explaining coverage terms specific to the specialty (e.g., reinsurance thresholds for dealer lots, Fannie Mae guidelines for HOA fidelity coverage).
8. Arrange for binding or schedule a follow-up consultation for complex cases requiring in-person review.

**Required Knowledge:**
- Builder's risk policies: what they cover (theft, vandalism, weather damage during construction), duration tied to certificate of occupancy, distinction from homeowner's coverage
- Surety bonds: bid bonds, performance bonds, surety bonds — terms, duration, obligee requirements, wet signature requirements
- HOA/condo insurance: master hazard policies, NC condo act requirements, Fannie Mae guidelines for crime/fidelity coverage, DNO (Directors & Officers) coverage
- Auto dealer lot insurance: inventory coverage, customer test drive liability, reinsurance triggers (e.g., $15M threshold), startup vs. established dealer underwriting differences
- Church-affiliated programs: liability for preschools, daycare operations, volunteer coverage — Church Mutual as specialty carrier
- Life/health/Medicare: product awareness sufficient to route to Steve Edmund (health specialist) or provide basic term/whole life guidance
- Group insurance underwriting: Blue Cross transitions, Signa conservative underwriting approach
- Coastal property limitations: Auto Owners does not write coastal NC — must route to Tracy or specialty coastal carriers
- Land development: ground lease insurance requirements for commercial tenants (Bojangles, Taco Bell)
- Liquor liability: separate endorsement requirements for businesses serving alcohol
- NC-specific regulations for each specialty line

**Systems & Tools:**
- Carrier portals: USLI, Church Mutual, Honeycomb, Westfield, Builders Mutual, Hartford Small Commercial, Chub, Cincinnati
- Progressive product guide and Snap quoting system
- Travelers underwriting portal (bond modifications)
- Auto Owners home insurance portal
- InvictaCon and Signa Insurance (group health)
- NC Secretary of State website (business entity verification)
- Doc Sign / Conga Sign (bond documents)
- Alliance Insurance policy database
- Internal agent scheduling system (for consultations at Winston office)
- Email system for policy documentation

**Outcome Distribution:**
- callback_needed: 19 of 28 (68%)
- resolved: 8 of 28 (29%)
- transferred: 0
- voicemail: 1 (~4%)

The 68% callback rate reflects the consultative nature of these calls — specialty commercial insurance rarely resolves in a single conversation. Complex risks require underwriting review, carrier submissions, and sometimes referrals to other agencies. The 29% resolved rate is actually high for this category, indicating that simpler specialty inquiries (bond status verification, coverage questions, routing to the right specialist) can be handled immediately.

**Edge Cases & Escalation Triggers:**
- Church-affiliated preschool liability requiring separate coverage path from the corporate church entity (file: exten-206-+18283800807-20250725)
- Crime/fidelity endorsement for NC HOA per Fannie Mae guidelines where the carrier hasn't filed the required form (file: exten-105-+19086564672-20251229)
- Auto dealer lot optimization to avoid $15M reinsurance trigger — requires deep underwriting strategy (file: exten-206-+13364323980-20260116)
- Supplemental crime fidelity coverage needed for HOA to prevent property foreclosure — time-sensitive, requires HOA president's formal request (file: exten-302-+17042008835-20251229)
- Bond documents requiring wet signature and in-person visit to town office — cannot be handled digitally (file: out-3363682247-206-20260108)
- Alliance unable to competitively quote new auto dealer startups — must refer to other agencies (file: out-7047289313-512-20250911)
- Temporary outbuilding and contents on construction site with no standard policy fit — transferred to habitation queue (file: out-8004877565-510)
- Coastal property construction where primary carrier (Auto Owners) does not write coastal NC

**Automation Feasibility:** Low
Rationale: This is the least automatable engagement type. Perhaps 10-15% of calls (bond status checks, routing to specialists, basic coverage questions) could be handled by AI. The core value of these calls is consultative judgment — understanding a caller's unique risk, knowing which carriers have appetite for it, and structuring coverage creatively. The knowledge required spans dozens of specialty markets, each with different underwriting criteria. The AI agent's best role here is intelligent triage: gathering the risk details, classifying the specialty type, and routing to the right human specialist with a complete intake package.

**What the AI Agent Must Do:**
- Classify the specialty type from the caller's description (builder's risk, bond, HOA, dealer lot, church, life/health, group insurance, coastal property, land development, liquor liability)
- Gather risk-specific intake details: for builder's risk — project address, construction value, timeline, GC info; for bonds — bond type, amount, obligee, project details; for dealer lots — location, inventory count, business age
- Check existing policies in the Alliance database to understand what coverage the caller already has
- Verify surety bond status (active, effective dates, expiration) for simple status check calls
- Route life/health/Medicare inquiries to Steve Edmund or the appropriate health specialist
- Route coastal property inquiries to Tracy (specialist for coastal NC)
- Route complex commercial to Jeff (commercial accounts lead) or the habitation queue
- Explain at a high level what different specialty coverages do (builder's risk vs. homeowner's during construction, certificate holder vs. additional insured on HOA policies)
- Recognize when Alliance cannot competitively serve a risk (new auto dealer startups, certain niche markets) and recommend the caller seek a specialty agency, rather than wasting time on quotes that won't be competitive
- Prepare structured intake summaries for the specialist agent, including all gathered details, so the follow-up call is productive

---

## DMV / Compliance (~27 calls, 1.8%)

**Typical Caller:** A policyholder who received a letter from the NC DMV threatening plate revocation or fines due to an apparent insurance lapse — often triggered by a carrier switch, policy cancellation, or vehicle removal from a policy. These callers are anxious and confused about why they received the notice when they believe they have continuous coverage. A smaller subset involves commercial clients needing DOT number setup.

**Resolution Workflow:**
1. Identify the caller and locate their auto policy in the Alliance Insurance policy database.
2. Ask the caller to describe or photograph the DMV notice they received — determine whether it's a plate revocation notice, FS-1 request, or coverage lapse notification.
3. Pull up the vehicle(s) referenced in the DMV notice by VIN and verify coverage history: when was the policy active, when did it cancel or change, and is there a gap?
4. Determine the cause of the DMV notification: carrier switch (old carrier reported cancellation before new carrier reported inception), policy cancellation for non-payment, vehicle removed from policy, or data error.
5. If an FS-1 form needs to be filed: collect the vehicle VIN(s), policy effective dates, and carrier details. Contact the carrier verification department (e.g., Progressive insurance verification system) to submit the FS-1 electronically to the NC DMV.
6. If there is a genuine coverage gap: calculate the gap duration, inform the caller of potential fines ($50 per vehicle for NC DMV), and discuss options — retroactive coverage may not be possible, but documenting the gap accurately helps at the DMV.
7. If the gap was caused by an improper vehicle removal or policy error: temporarily reinstate coverage on the vehicle to prevent the DMV flag fee, then process the correct change.
8. Advise the caller to bring copies of the FS-1 filing confirmation and current proof of insurance to the DMV if they need to resolve the issue in person.
9. For DOT number setup: guide the caller through the FMCSA website, address vehicle titling requirements (must be in the DOT registrant's name or under a lease agreement), and coordinate insurance documentation.
10. Follow up to confirm the DMV has received and processed the FS-1 form.

**Required Knowledge:**
- NC DMV FS-1 form requirements: what triggers the requirement, who files it (the carrier, not the customer), electronic vs. paper filing
- NC continuous coverage law: how DMV tracks coverage via electronic reporting from carriers, consequences of gaps
- Plate revocation process: timeline from notice to actual revocation, steps to prevent it
- Coverage gap fine structure: $50 per vehicle per lapse period in NC
- Carrier switch DMV notifications: when switching from Progressive to National General (or any carrier transition), the old carrier reports cancellation before the new carrier reports inception, triggering a false lapse notice
- How to contact carrier verification departments: Progressive insurance verification system, Auto Owners, National General, Liberty Mutual, Cincinnati Group — each has different FS-1 submission procedures
- DOT number setup via FMCSA website: vehicle titling requirements, lease agreement between driver and vehicle owner
- State-specific compliance differences: SC uses FR-10 (not handled by NC agency), Florida has different requirements
- How improper vehicle removal from a policy triggers DMV flag fees and how temporary reinstatement prevents this

**Systems & Tools:**
- NC DMV portal
- FMCSA website (DOT number setup)
- Progressive insurance verification system
- Auto Owners policy database
- National General systems
- Liberty Mutual systems
- Cincinnati Group portal
- Alliance Insurance internal systems
- support@myallianceinsurance.com (for DMV letter submission)
- FS-1 form system (electronic filing)
- Insurance payment tracking system

**Outcome Distribution:**
- callback_needed: 18 of 27 (67%)
- resolved: 9 of 27 (33%)

The 67% callback rate reflects the multi-step nature of DMV compliance resolution: the agent must contact the carrier to file the FS-1, then the carrier must process it, then the DMV must acknowledge it. The 33% resolved rate covers cases where the FS-1 was already filed and the agent simply confirmed this to the caller, or where the agent could explain the notice and advise next steps without needing carrier action.

**Edge Cases & Escalation Triggers:**
- South Carolina-specific accident form (FR-10) that the NC agency cannot process — must refer caller to SC-licensed agency (file: exten-114-+13364234380-20251120)
- DOT setup requiring a lease agreement between a driver and a cousin who holds the vehicle title — unusual ownership structure complicates FMCSA registration (file: exten-207-+13362448945-20251119)
- Junk mail confusion causing caller to mistake a legitimate FS-1 notice for spam (file: exten-112-+17045025332-20251223)
- DMV requesting proof of coverage on a specific past date when a different carrier was active — requires contacting the previous carrier (Liberty Mutual) to file FS-1 for that date (file: exten-401-+15082931785-20250826)
- 16-day coverage gap between Progressive expiration and National General start resulting in potential $50/vehicle fine despite FS-1 filing — gap is real and cannot be erased (file: out-3369183397-501-20251208)
- Client improperly removed a vehicle from their policy, triggering a DMV flag — agent temporarily reinstated coverage to prevent the fee (file: out-8777762436-501-20260105)
- Client purchased a second Progressive policy directly online (bypassing the agency), creating conflicting DMV records that require contacting Progressive Direct (file: parked-113-113-20250912)
- Terminated policy preventing spouse from getting a new license plate at the DMV (file: q-300-+13367401767)
- License plate office employee calling on behalf of a customer to resolve a coverage discrepancy blocking tag issuance (file: in-+13363779003-+13367037550-20251002)

**Automation Feasibility:** Medium
Rationale: About 40-50% of DMV/compliance calls follow a predictable pattern: caller received FS-1 notice, agent verifies coverage is active, contacts carrier to file FS-1 electronically, confirms with caller. An AI agent could handle the intake (collecting the notice details, identifying the vehicle, verifying coverage status) and initiate the FS-1 filing with carriers that support electronic submission. The blockers are: (1) cases requiring judgment about genuine coverage gaps vs. false alarms, (2) multi-carrier situations where a previous carrier must file the FS-1, (3) DOT setup requiring FMCSA navigation and unusual ownership structures, and (4) the emotional dimension — callers are often panicked about losing their plates and need reassurance.

**What the AI Agent Must Do:**
- Identify the type of DMV notice from the caller's description: plate revocation, FS-1 request, coverage lapse notification, or fine assessment
- Look up the vehicle(s) by VIN in the Alliance Insurance policy database and verify coverage history across carriers
- Determine whether the DMV notice was triggered by a carrier switch, policy cancellation, vehicle removal, or genuine coverage gap
- Calculate coverage gap duration and inform the caller of potential NC DMV fines ($50 per vehicle)
- Submit FS-1 forms electronically to the NC DMV through carrier verification departments (Progressive, Auto Owners, National General, Liberty Mutual)
- Track FS-1 filing status and notify the caller when the DMV has processed the form
- Advise the caller on what documents to bring to the DMV for in-person resolution
- Recognize out-of-state compliance issues (SC FR-10, Florida requirements) and route to appropriate resources
- Guide commercial clients through DOT number setup on the FMCSA website, including vehicle titling requirements
- Detect when a vehicle was improperly removed from a policy and flag for temporary reinstatement to prevent DMV penalties
- Provide clear, calming explanations of the DMV process — these callers are typically stressed about losing driving privileges

---

## Workers' Comp Administration (~27 calls, 1.8%)

**Typical Caller:** Small business owners — contractors, installers, fencing companies, cleaning services, church organizations — dealing with workers' compensation audit issues, ghost policy questions, class code disputes, or new WC policy inquiries. A significant subset involves callers who are confused or upset about unexpected audit charges on canceled or minimal-use policies.

**Resolution Workflow:**
1. Identify the caller and locate their workers' compensation policy in the Alliance Insurance policy database. Determine the carrier (Travelers, AmTrust, Builders Mutual, Auto Owners, West Bend, Penn National, Encova, Wasco).
2. Classify the WC issue: audit compliance, ghost policy question, class code change, new WC quote, WC claim filing, payroll reporting, or collections dispute.
3. **For audit issues (most common):**
   a. Explain the audit lifecycle: carriers are legally required to audit WC policies, even canceled ones.
   b. Determine audit compliance status — is the caller non-compliant (hasn't submitted documentation)?
   c. If non-compliant: explain that a non-compliant audit fee will be assessed (often $1,500-$2,500+) and will be refunded once the audit is completed with proper documentation.
   d. Guide the caller to the carrier's audit portal (e.g., travelers.com/audit) and explain required documentation: payroll records, tax forms (940/941), subcontractor certificates.
   e. If the audit has gone to collections: coordinate with the carrier to re-open the audit and resolve the debt (e.g., $9,000 AmTrust collections case).
4. **For ghost policy questions:**
   a. Explain that a ghost policy is a WC policy with no employees — standard $1,500 deposit premium through the NC Rate Bureau — used to obtain a certificate of insurance.
   b. Clarify that ghost policies still require audits and that audit fees apply even when no payroll was reported.
   c. If the caller disputes the ghost policy's validity, advise them to contact the carrier directly to dispute or escalate within the agency to the commercial team.
5. **For class code changes:** Verify current class codes, determine the correct codes for the work being performed (e.g., 8848 to 8826/8824), and coordinate with the carrier — some carriers require a new policy for class code changes (e.g., Paychecks).
6. **For new WC quotes:** Gather payroll estimates by class code, number of employees, officer inclusion/exclusion preferences, and subcontractor details. Provide quote options with different officer exclusion configurations.
7. **For WC claims:** Collect incident details (employee name, date, injury description, location), file with the carrier, and explain next steps.
8. Follow up on audit documentation submission and confirm resolution of non-compliance fees.

**Required Knowledge:**
- Workers' compensation audit lifecycle: submission requirements, non-compliance fees, collections escalation, re-opening audits
- NC Rate Bureau procedures and premium structures for ghost policies ($1,500 standard deposit)
- Class code system: what codes apply to which trades (8848 vs. 8826/8824 for different installation types), when code changes require new policies
- Payroll reporting requirements: how to accurately report for fluctuating construction businesses, what counts as payroll vs. subcontractor payments
- Subcontractor classification rules: when subs count as employees for WC purposes, certificate requirements for subcontractors
- Officer exclusion options: how excluding corporate officers affects premium and coverage, NC-specific rules for sole proprietors (ineligible for WC by statute)
- Ghost policy mechanics: why businesses with no employees need WC policies (for COI requirements from general contractors), standard premium structure, audit obligations
- Carrier-specific audit portals and processes: Travelers (travelers.com/audit), AmTrust, HemTrust, Encova, Builders Mutual
- Non-compliant audit billing: how fees are assessed, refund process after audit completion, timeline expectations
- Collections process: how to re-open audits that have gone to collections, negotiation with collection agencies
- WC claim filing procedures by carrier

**Systems & Tools:**
- Travelers insurance portal and audit portal (travelers.com/audit)
- AmTrust / HemTrust systems
- Builders Mutual portal
- West Bend Insurance
- Penn National systems
- Encova portal
- Wasco Insurance Company
- Auto Owners policy database
- NC Rate Bureau
- NC Secretary of State website (business entity verification)
- Ascend (third-party billing system)
- Paychecks (insurance carrier)
- Orona carrier portal
- Doc Sign / Conga Sign
- Alliance Insurance commercial department
- Email system (support@myallianceinsurance.com)

**Outcome Distribution:**
- callback_needed: 19 of 27 (70%)
- resolved: 8 of 27 (30%)

The 70% callback rate reflects the complexity and multi-step nature of WC administration. Audits require documentation gathering (payroll records, tax forms) that the caller rarely has during the initial call. Ghost policy disputes often need carrier-level resolution. Class code changes may require new policies. The 30% resolved rate covers simpler inquiries: confirming audit status, explaining the process, verifying policy details, or routing to the commercial team.

**Edge Cases & Escalation Triggers:**
- Audit debt of $9,000 sent to collections requiring audit re-opening — caller is in financial distress (file: exten-207-+13367106929-20250902)
- Ghost policy dispute where caller claims the policy is invalid and should not require an audit — philosophical disagreement about the product (file: in-+13363544000-+13365965391-20251117)
- Sole proprietor erroneously approved for WC quote — sole proprietors are ineligible for WC by NC statute (file: exten-207-+18002300210-20251120)
- Collections agent from AmTrust seeking information on a non-English-speaking client with penalty audits — language barrier plus third-party caller (file: exten-207-+14407031019-20260107)
- Class code change requiring a new policy because the carrier (Paychecks) cannot modify codes on existing policies (file: in-+13367861133-+13364088960-20250819)
- Non-compliant audit bill requiring immediate $2,456 payment to prevent cancellation with promised refund after completion — time pressure and large dollar amount (file: out-13369088352-207-20251208)
- WC exclusions for corporate officers leaving coverage reliant entirely on subcontractors — edge of coverage adequacy (file: parked-105-105-20250919)
- Unexpected $2,400 audit charge on a ghost WC policy that supposedly covers nothing — caller fundamentally misunderstands the product (file: q-300-+13365965391-20251114)
- Business ownership transition during audit period creating class code and entity discrepancies (file: exten-103-+13364144231-20250806)

**Automation Feasibility:** Low-Medium
Rationale: Perhaps 20-30% of WC calls could be partially automated — specifically, explaining the audit process, directing callers to the carrier audit portal, and confirming policy status. But the core complexity of WC administration (audit disputes, ghost policy explanations, class code determinations, collections resolution) requires specialized judgment and carrier negotiation that an AI agent cannot perform independently. The biggest value an AI agent provides here is structured intake: gathering all the documentation details (payroll numbers, tax form references, business entity structure) so the commercial agent's follow-up call is maximally productive. The AI agent could also proactively notify clients about upcoming audits and documentation deadlines, reducing the number of non-compliance situations.

**What the AI Agent Must Do:**
- Identify the WC issue type from the caller's description: audit compliance, ghost policy question, class code change, new quote, claim filing, payroll reporting, or collections dispute
- Look up the caller's WC policy by name or policy number, identifying the carrier (Travelers, AmTrust, Builders Mutual, etc.)
- Explain the WC audit lifecycle clearly: why audits happen (legal requirement), what documentation is needed (payroll records, 940/941 tax forms, subcontractor certificates), and timeline expectations
- Direct callers to the correct carrier audit portal (e.g., travelers.com/audit) with step-by-step guidance
- Explain non-compliant audit fees: how much, why they were charged, and the refund process after audit completion
- Explain ghost policy mechanics: purpose (COI requirement from general contractors), standard NC Rate Bureau premium ($1,500), audit obligations even with zero payroll
- Gather payroll and subcontractor details for new WC quotes, including officer names and exclusion preferences
- Collect WC claim details: employee name, date of injury, description of incident, location, and file with the appropriate carrier
- Recognize when a caller's situation requires commercial department escalation (class code disputes, collections resolution, ghost policy disputes) and transfer with a complete intake summary
- Flag NC-specific eligibility issues (sole proprietors cannot obtain WC coverage) before quote processing wastes time
- Track audit documentation submission status and send reminders to clients with upcoming audit deadlines

---

## Driver Add/Remove (~18 calls, 1.1%)

**Typical Caller:** A parent adding a teenage child (ages 15-18) to their auto policy — either before a learner's permit test, after obtaining a permit, or upon receiving a full driver's license. A smaller subset involves removing drivers who have moved out, married, or are deceased, and commercial clients adding employees as drivers to fleet policies.

**Resolution Workflow:**
1. Identify the caller and locate their auto policy in the Alliance Insurance policy database.
2. Determine the driver change type: adding a new driver, removing an existing driver, or updating a driver's status (permit to license).
3. **For adding a minor/new driver:**
   a. Collect the new driver's full name, date of birth, and driver's license or permit number (if available).
   b. Determine the driver's status: no license yet (household member, non-rated), learner's permit (covered under existing policy in NC), or full license (rated driver with premium impact).
   c. For minors without a license: add as a household member with no premium change. Explain that they'll need to be updated to a rated driver when they obtain their license.
   d. For drivers with a permit: confirm they are already covered under the existing policy for the permit period. No additional coverage is needed until they get a full license.
   e. For newly licensed drivers: add as a rated driver. Explain the NC inexperienced operator surcharge (now an 8-year window under new NC law). Provide the premium impact amount.
   f. Run a motor vehicle record (MVR) check for tickets, accidents, and driving history.
4. **For removing a driver:**
   a. Confirm the reason: moved out, married and on own policy, deceased, or other.
   b. If the driver is on multiple policies (auto, umbrella), coordinate removal across all policies and carriers (Progressive, Travelers, Auto Owners).
   c. Process the removal and calculate the premium reduction.
   d. If removing from an umbrella policy, verify underlying auto/home policy requirements are still met.
5. **For commercial driver additions:**
   a. Collect the driver's name, DOB, CDL or license number, and driving history.
   b. Process through the commercial auto carrier system.
   c. Provide the premium impact (e.g., $69 increase for adding a driver to a Freightliner policy).
   d. Generate updated proof of coverage or COI if needed.
6. Send confirmation via email and generate updated ID cards if applicable.

**Required Knowledge:**
- NC learner's permit insurance rules: permit holders are covered under the parent's existing policy; no separate addition needed until full license is obtained
- NC inexperienced operator surcharge: new 8-year window under updated NC law (changed from previous shorter period), applies to newly licensed drivers regardless of age
- Household member vs. rated driver distinction: non-rated household members don't affect premium; rated drivers do
- Premium impact calculations for adding young/inexperienced drivers — this is often the caller's primary concern
- Driver exclusion procedures: when and how to formally exclude a driver (requires e-signature on exclusion form)
- Umbrella policy driver update requirements: removing a driver from auto may require corresponding umbrella update (Progressive umbrella system)
- Multi-carrier coordination: when a driver appears on policies across Progressive, Travelers, and Auto Owners, all must be updated
- Commercial auto driver addition: CDL requirements, MVR checks, Freightliner/fleet-specific considerations
- Occasional/permissive driver rules: when someone who drives the car occasionally doesn't need to be listed (coverage follows the vehicle)

**Systems & Tools:**
- Alliance Insurance policy database/management system
- MVR (Motor Vehicle Record) database
- Progressive insurance portal and umbrella system
- Auto Owners portal
- National General systems
- Travelers insurance portal
- CMS Insurance
- Allstate
- Florida driver's license database (for out-of-state drivers)
- Internal insurance forms/documentation
- Email system for confirmations and ID cards

**Outcome Distribution:**
- callback_needed: 13 of 18 (72%)
- resolved: 5 of 18 (28%)

The 72% callback rate is somewhat inflated by calls that arrive when the policyholder's assigned agent is unavailable and by cases requiring MVR results or premium calculations that take processing time. The actual driver addition/removal process is straightforward once the information is gathered. Resolved cases are typically simple confirmations (permit holder is already covered, no action needed) or direct additions processed during the call.

**Edge Cases & Escalation Triggers:**
- Employee changing companies with multiple tickets and personal complications — underwriting judgment needed (file: exten-207-+13362440854-20251125)
- Adding a 16-year-old son urgently so he can take his driving test that same day — time-critical (file: in-+13363544000-+13364066606-20250909)
- Removing a deceased person (Carolyn) from multiple policies across Travelers and Progressive simultaneously — emotionally sensitive and multi-carrier coordination (file: out-3362842907-202-20251230)
- Daughter added before driver's test with agent explaining new 8-year inexperienced operator surcharge law — regulatory education required (file: q-300-+12627073641-20260106)
- Removing a daughter from an umbrella policy after she moved to a different state and married — umbrella policy interaction with underlying coverage (file: q-300-+13302426449-20250909)
- Son listed as second driver with his own insurance — no premium impact but address update needed when he moves (file: q-300-+13363910897-20251216)
- Caller discovering during the call that their spouse doesn't have a valid driver's license — triggers policy restructuring (file: exten-106-+13366718842-20251117)

**Automation Feasibility:** Medium-High
Rationale: About 55-65% of driver change calls follow predictable patterns that an AI agent could handle. Adding a household member (minor without license) is a zero-judgment, zero-premium-change transaction. Confirming that a permit holder is already covered is a pure knowledge response. Removing a driver who moved out is a straightforward policy change. The blockers are: (1) premium impact calculations that require carrier system access and real-time rating, (2) MVR checks that may reveal underwriting concerns (tickets, accidents), (3) multi-carrier coordination for removals, and (4) emotionally sensitive situations (deceased driver removal). The AI agent could handle intake, answer the most common question ("does my kid with a permit need to be added?"), and process simple additions/removals, escalating only when underwriting judgment is needed.

**What the AI Agent Must Do:**
- Determine the driver change type from the caller's request: add minor, add licensed driver, add commercial driver, remove driver, or update status (permit to license)
- Collect new driver details: full legal name, date of birth, driver's license or permit number, relationship to policyholder
- Explain NC learner's permit rules: permit holders are covered under the parent's policy and do not need to be separately added until they obtain a full license
- Explain the NC inexperienced operator surcharge: 8-year window under new law, premium impact, and when it applies
- Add household members (minors without licenses) as non-rated drivers with no premium change
- Run MVR checks through carrier systems and flag any tickets, accidents, or license issues
- Calculate and communicate premium impact of adding rated drivers, using carrier-specific rating tools
- Process driver removals across all applicable policies — auto, umbrella, and any other lines where the driver is listed
- Coordinate multi-carrier driver removals (e.g., removing from both Travelers auto and Progressive umbrella in the same transaction)
- Generate and send updated insurance ID cards after driver changes are processed
- Handle time-sensitive additions where a driver test is imminent (same-day processing priority)
- Recognize when a driver's record or circumstances require underwriting review and escalate with complete intake details rather than attempting to bind coverage

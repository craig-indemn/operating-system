# Capability Specifications: Group 2

Synthesized from 5 batch digests per engagement type, covering 431 classified calls across 5 types.

---

## Routing / Triage (122 calls, 7.8%)

**Typical Caller:** Anyone reaching the Alliance Insurance phone system — customers requesting a specific agent by name, Spanish-speaking callers needing bilingual help, misdirected callers (wrong company or wrong department entirely), carrier/vendor representatives, and internal staff with IT issues. This is the front door of the agency, and roughly half of these calls are not insurance transactions at all.

**Resolution Workflow:**
1. Greet caller and identify intent — determine whether they need a specific agent, a department, or have reached the wrong number entirely.
2. If requesting a specific agent (e.g., "Can I speak to Gloria?" or "Corbin left me a voicemail"), check internal agent availability system for that person's status and extension.
3. If agent is available, transfer the call directly via the internal phone system (Lightspeed Voice extensions).
4. If agent is unavailable, collect caller's name, phone number, and brief description of need. Log a callback message and provide an estimated return time (e.g., "Holly will be in at 10:30 AM").
5. If caller needs Spanish-language assistance, identify whether Jessica Hernandez (commercial) or another bilingual agent is available. If not, arrange a callback with specific day/time and collect caller's contact information.
6. If caller reached the wrong company (e.g., Alliance Insurance Company vs. Alliance Insurance Services, or a completely unrelated business), politely clarify and provide correct contact information if known.
7. If the call is a non-insurance matter (IT support, food orders, medical scheduling, vendor solicitation), either redirect to the appropriate internal resource (IT staff for printer/copier/portal issues) or politely decline.
8. If the call is from a carrier, underwriter, inspector, or lender representative, identify which Alliance agent they need and transfer or take a message.

**Required Knowledge:**
- Complete internal staff directory: every agent's name, extension, specialty area (personal lines, commercial, bonds), office location (Mount Airy vs. Winston), and typical schedule
- Distinction between Alliance Insurance Services (the independent agency) and Alliance Insurance Company (a carrier) and Alliance Health/Alliance Behavioral Health (completely different organizations)
- Spanish-speaking agent availability — currently limited to Jessica for commercial lines; knowing who can handle personal lines in Spanish
- Agency service area limitations (NC and surrounding states; does not serve Florida)
- Basic IT troubleshooting awareness (browser cache clearing, portal login URLs for Employers, Bamboo HR, carrier portals)
- The myallianceinsurance.com customer portal URL and text support number (336-786-1133)
- Call handling protocols: when to transfer, when to take a message, when to send to voicemail

**Systems & Tools:**
- Internal call routing/transfer system (Lightspeed Voice)
- Voicemail system
- myallianceinsurance.com customer portal
- Internal agent directory / CRM
- Email system (HeatherJ@myallianceinsurance.com domain)
- Text support (336-786-1133)
- Canopy Connect
- Various carrier portals (for troubleshooting login issues)

**Outcome Distribution:**
- callback_needed: 80.3% (94 of 117 with outcomes)
- resolved: 15.4% (18)
- transferred: 2.6% (3)
- voicemail/not_applicable: 1.7% (2)

The extremely high callback rate reflects the nature of this type — most calls are about reaching a person who is unavailable, so the "resolution" is inherently a callback arrangement. Only ~15% are resolved in-call (typically misdirected calls, simple questions, or IT troubleshooting).

**Edge Cases & Escalation Triggers:**
- **Misdirected emergency calls:** School bus crash caller directed to wrong Alliance Insurance — must identify and redirect quickly without wasting caller's time in an emergency.
- **Vendor solicitation disguised as customer calls:** Spectrum Business, Salesforce, and similar vendors calling to speak with a manager — need polite but firm deflection.
- **Completely non-insurance calls:** Hibachi chicken orders, haircut scheduling, colonoscopy rescheduling, water bill inquiries, dessert pickup at Food Lion — these are outbound calls from agency staff's personal use of the phone system or inbound misdials. AI agent must recognize and handle gracefully.
- **IT support requests:** Copier configuration, printer troubleshooting, email restoration, Bamboo HR login issues, check scanner software installation, slow computer complaints — these come through the insurance line because office staff use the same phone system.
- **Privacy boundary situations:** Callers asking for personal client information (phone numbers, addresses) — agent must adhere to agency policy of not sharing personal client information.
- **AOR (Agent of Record) process clarification:** Calls from other agencies regarding acquisition or transfer of accounts — requires understanding of inter-agency protocols.
- **Geographic service boundary:** Caller from Florida seeking insurance — Alliance does not serve Florida and must refer to a local agency.

**Automation Feasibility:** Medium
Rationale: An AI agent could handle ~60% of routing/triage calls effectively. The core workflow — identify who the caller wants, check availability, transfer or take a message — is highly structured. The AI could also immediately filter misdirected calls and handle Spanish-language routing (with multilingual capability). However, the remaining ~40% involves judgment calls: distinguishing vendor solicitation from legitimate business calls, handling IT issues that require back-and-forth troubleshooting, and managing emotionally charged situations (e.g., callers upset about being unable to reach their agent). The biggest blocker is integration with the internal phone system (Lightspeed Voice) for live call transfers.

**What the AI Agent Must Do:**
- Look up any Alliance Insurance agent by name, extension, or specialty and report their availability status in real time via the internal directory system
- Execute warm and blind call transfers through the Lightspeed Voice phone system to specific extensions
- Record structured callback messages (caller name, phone number, brief reason, urgency level) and deliver them to the correct agent via the internal CRM or messaging system
- Detect and respond in Spanish for basic routing interactions, and escalate to Jessica Hernandez or arrange a bilingual callback when the request is substantive
- Identify misdirected calls within the first 10 seconds (wrong Alliance entity, wrong business entirely, non-insurance requests) and redirect or politely decline with correct contact information
- Distinguish between customer calls, carrier/underwriter inbound calls, vendor solicitation, and internal IT requests, applying different handling protocols for each
- Provide the customer portal URL (myallianceinsurance.com) and text support number (336-786-1133) when callers need self-service options
- Handle basic IT troubleshooting guidance (clear browser cache, use direct login link) for carrier portal access issues before escalating to IT staff

---

## Claims Filing & Follow-Up (93 calls, 6.0%)

**Typical Caller:** A policyholder (personal or commercial) who has just experienced a loss — car accident, property theft, weather damage, workplace injury, vandalism — or who is following up on a previously filed claim because they have not heard from an adjuster, received a partial payment, or had a claim denied. Callers range from calm and organized to highly emotional and confused about the process.

**Resolution Workflow:**
1. Verify caller identity and locate their policy in the Alliance Insurance system. Determine whether the caller is reporting a new incident or following up on an existing claim.
2. **For new claims:** Collect full incident details — date, time, location, description of damage or injury, parties involved, police report number (if applicable), and photos/documentation available.
3. Determine the correct carrier and coverage type (auto, homeowners, commercial property, inland marine, workers' compensation, commercial auto). Verify the policy is active and the incident falls within the coverage period.
4. File the claim through the appropriate carrier's claims reporting system (Auto Owners, Progressive, National General, Utica, Travelers, Liberty Mutual, Encova, Nationwide, Penn National, Berkeley Aspire, Universal Property Casualty). Each carrier has a different portal or phone reporting process.
5. Provide the caller with their claim number (if generated immediately) and explain the adjuster assignment timeline (typically 24-48 hours). Give adjuster contact information if available.
6. Advise on documentation requirements — submit photos, repair estimates, police reports, receipts. Explain deductible implications and whether filing is advisable vs. paying out of pocket for minor damage.
7. **For follow-ups:** Look up the existing claim status in the carrier's system. If an adjuster is unresponsive, escalate by leaving voicemail and email to the adjuster or their supervisor. If a payment discrepancy exists, investigate the settlement calculation and explain.
8. **For third-party claims:** Direct the caller to file under the at-fault party's insurance carrier, providing that carrier's claims number and filing instructions.
9. Send any relevant documentation (claim confirmation, adjuster contact card) via email.

**Required Knowledge:**
- Claims filing procedures for each carrier: Auto Owners, Progressive, National General, Utica Insurance, Travelers, Liberty Mutual, Encova, Nationwide, Penn National, Berkeley Aspire, Universal Property Casualty — each has different intake processes, phone numbers, and portal workflows
- Adjuster communication protocols: typical response windows, escalation paths when adjusters are unresponsive, three-way call coordination
- Coverage determination: distinguishing which policy covers a given loss (inland marine for equipment on a job site, workers' comp for employee injuries, commercial auto for business vehicles, homeowners for property damage)
- Subrogation rights and process — when and how to pursue the at-fault party's insurer
- Deductible implications and guidance on when to file vs. pay out of pocket (especially for minor incidents)
- Documentation requirements by claim type: accident photos, police reports, repair estimates, medical records, stolen property lists
- Workers' compensation claim procedures: immediate medical steps, reporting requirements, employer obligations
- DBA vs. personal name policy structure — commercial policies often filed under the owner's personal name, not the business name, causing lookup confusion at the carrier level
- At-fault vs. not-at-fault determination and its impact on deductible recovery
- Rental car eligibility post-claim and how to activate that coverage
- NC-specific claims regulations

**Systems & Tools:**
- Auto Owners claims department / portal
- Progressive claims system
- National General claims portal
- Utica Insurance / Utica National claims portal
- Travelers claims system
- Liberty Mutual claims system
- Encova claims system
- Nationwide claims system
- Penn National claims system
- Berkeley Aspire claims reporting line
- Universal Property Casualty claims
- Alliance Insurance internal claim lookup / CRM
- Police report records access
- Email system for claim documentation delivery

**Outcome Distribution:**
- callback_needed: 72.4% (63 of 87 with outcomes)
- resolved: 23.0% (20)
- transferred: 2.3% (2)
- voicemail: 2.3% (2)

About 23% of claims calls resolve on the first contact — typically when the agent can file the claim with the carrier and provide a claim number immediately. The 72% callback rate reflects the inherently multi-step nature of claims: adjuster assignment, damage assessment, settlement negotiation, and payment processing all happen downstream.

**Edge Cases & Escalation Triggers:**
- **Claim denial disputes:** Carrier denying a claim (e.g., long-term gradual toilet leak excluded under policy terms, mechanical damage exclusion) — agent must explain the denial and either advocate for the customer or help them understand the exclusion.
- **Lost claims:** Claim filed 3 weeks ago with no record in the carrier system, requiring re-filing — indicates a process failure that must be caught.
- **Suspected fraud/scam:** Fake client arranging roofing work leading to a police report — requires careful handling and potential law enforcement coordination.
- **DBA policy lookup failure:** Insurance company cannot find the policy under the business name because it is filed under the owner's personal name — agent must explain the DBA structure and provide the correct lookup name.
- **Stolen materials vs. tools distinction:** Carrier covering tools but denying coverage for stolen building materials; resolution depends on subcontractor agreement documentation.
- **Duplicate claim charges:** Father and son with similar names on separate policies creating duplicate claim entries for the same incident.
- **Minor accident advisement:** Parent asking whether to use insurance or pay out of pocket for a minor fender-bender caused by their child with a learner's permit — requires careful guidance on premium impact vs. repair cost.
- **Unresponsive adjuster escalation:** Multiple follow-ups with no adjuster response — requires voicemail, email, and supervisor escalation chain.
- **Partial payment disputes:** Settlement amount lower than expected (e.g., $1,800 paid instead of $4,335.99) — agent must investigate the carrier's calculation and explain deductions (depreciation, storage, appraisal clause).
- **Policy status discrepancy:** Claim denied despite evidence of premium payments — requires investigating whether the policy was actually in force at the time of loss.

**Automation Feasibility:** Low
Rationale: Only about 15-20% of claims calls could be fully automated. New claim intake is partially automatable — collecting incident details and filing with the carrier — but the emotional complexity, coverage determination judgment, and multi-carrier fragmentation make this difficult. Follow-up calls (which are a large portion) require investigating status across carrier systems and often involve advocacy on the customer's behalf. Claims also involve the highest emotional intensity of any engagement type — theft victims, accident victims, property loss — requiring empathy and nuanced communication. The biggest blocker is the carrier-by-carrier fragmentation: each of 10+ carriers has a different claims portal and process, and many require phone calls rather than digital filing.

**What the AI Agent Must Do:**
- Collect structured incident data (date, time, location, damage description, parties involved, police report number, photos available) through a guided conversation flow that accounts for emotionally distressed callers
- Determine the correct carrier and coverage type by looking up the caller's policy in the Alliance Insurance system and matching the loss to the appropriate coverage line (auto, homeowners, commercial property, inland marine, workers' comp)
- File new claims through carrier-specific portals and reporting lines for Auto Owners, Progressive, National General, Utica, Travelers, Liberty Mutual, Encova, Nationwide, Penn National, Berkeley Aspire, and Universal Property Casualty
- Retrieve existing claim status from each carrier's system, including adjuster assignment, inspection scheduling, and payment status
- Explain deductible amounts, coverage applicability, subrogation rights, and at-fault determinations in plain language
- Escalate unresponsive adjusters through voicemail, email, and supervisor contact chains
- Guide callers on documentation requirements and provide carrier-specific claims phone numbers when direct filing is more appropriate
- Handle workers' compensation claims: advise on immediate medical steps, collect employer/employee details, and file with the appropriate WC carrier
- Distinguish between first-party and third-party claims and direct callers to the correct insurer when they are not at fault

---

## Vehicle Add/Remove/Replace (89 calls, 5.6%)

**Typical Caller:** An existing policyholder who has just purchased a new vehicle (from a dealership or private sale), sold or traded in a vehicle, had a vehicle totaled, or needs to swap one vehicle for another on their auto policy. This includes both personal and commercial auto customers, and occasionally involves non-standard vehicles (jet skis, motorcycles, Bobcat excavators).

**Resolution Workflow:**
1. Verify caller identity and locate their auto policy (personal or commercial) in the Alliance Insurance system.
2. Determine the nature of the change: addition, removal, replacement (swap), or a combination.
3. **For additions:** Collect the VIN (often provided phonetically — be prepared for military alphabet), year, make, and model. Verify the VIN pulls correctly in the carrier system (Auto Owners, Progressive, National General, Farm Bureau, Cincinnati, Penn National, Safeco).
4. Determine coverage type: full coverage (comprehensive + collision) or liability-only. If the vehicle is financed or leased, full coverage with the lienholder listed is required — collect the finance company name and mailing address (Capital One, Toyota Financial, etc.).
5. Confirm effective date — typically same-day for new purchases (NC has a 14-day coverage law for newly acquired vehicles, but customers need proof of insurance immediately for dealership pickup).
6. Calculate and communicate the premium impact before processing. For example, adding a 2026 Tesla Model 3 may increase annual premium by $426; adding a 2012 Nissan may add $343/year.
7. **For removals:** Confirm the vehicle has been sold, totaled, or is otherwise no longer in the caller's possession. Verify that license plates have been returned to the DMV (required in NC before processing removal to avoid compliance issues).
8. **For replacements (trade-ins):** Match coverage from the old vehicle to the new vehicle (same deductibles, liability limits) unless the caller requests changes. Process the removal and addition simultaneously.
9. Process the change in the carrier's system. Some carriers (like Safeco) may require phone calls for certain changes (e.g., adding a 5th vehicle), with 2-3 day processing times.
10. Email updated proof of insurance / ID cards to the caller, and send a binder to the dealership or lienholder if needed.

**Required Knowledge:**
- VIN lookup and verification processes across carrier systems — including handling brand-new VINs that may not yet be in carrier databases
- Coverage types: full coverage (comp + collision) vs. liability-only, and when each is required (financed/leased vehicles always need full coverage)
- Lienholder documentation requirements: finance company name, mailing address, loan number
- Commercial vs. personal auto policy distinctions — vehicles purchased under a company name may need to go on a commercial auto policy, not personal
- NC DMV license plate return requirements before vehicle removal
- NC 14-day coverage law for newly acquired vehicles
- Pro-rated premium calculations: how adding or removing a vehicle mid-term affects the billing cycle
- Carrier-specific vehicle change procedures: Auto Owners, Progressive, National General, Farm Bureau, Cincinnati Insurance, Penn National, Safeco all have different portal workflows and limitations
- Non-standard vehicle handling: jet skis, motorcycles, RVs, and equipment (Bobcat excavators) may require different policy types (inland marine, specialty)
- Lease termination timelines and policy implications
- Dealership coordination: sending proof of insurance to the dealership before the customer can drive the car off the lot

**Systems & Tools:**
- Auto Owners policy system
- Progressive portal
- National General portal
- Farm Bureau system
- Cincinnati Insurance system
- Penn National / Penn Plus / Pin Connect
- Safeco service request forms
- Alliance Insurance internal policy management system / CRM
- Email / fax systems for proof of insurance delivery
- DMV (for plate return verification and compliance)
- Quote generation tool (for premium impact calculations)

**Outcome Distribution:**
- callback_needed: 78.7% (70 of 89 with outcomes)
- resolved: 19.1% (17)
- transferred: 2.2% (2)

About 19% of vehicle change calls resolve on the first contact. The high callback rate reflects that many callers do not have all required information at hand (VIN, lienholder details, coverage preferences) or the carrier system requires processing time. Also, many initial calls are taken by front-desk staff who transfer or create a callback for a licensed agent.

**Edge Cases & Escalation Triggers:**
- **Brand-new VIN not in carrier system:** Newly manufactured vehicles (especially recent model years) may fail VIN lookup in Auto Owners or other carrier systems — requires manual entry or carrier escalation.
- **Commercial/personal policy confusion:** Vehicle purchased under a company name but caller asks to add to personal policy — must determine correct policy type and potentially create a new commercial auto policy.
- **Non-standard vehicles:** Jet skis, motorcycles, Bobcat excavators, and RVs may not fit on a standard auto policy and may require inland marine or specialty coverage.
- **Cross-state title/lienholder complications:** Vehicle titled in one state (VA) being added to an NC policy with lienholder requirements differing by state.
- **Adding vehicle to canceled policy:** Caller trying to add a vehicle to a policy that was already canceled and replaced by a direct carrier policy — requires identifying the current active policy.
- **System errors blocking coverage:** Carrier system preventing full coverage addition, possibly due to a household member's accident history — requires underwriting escalation.
- **Deceased named insured:** Vehicle change on a policy where the named insured is deceased — may require a full policy rewrite rather than a simple vehicle swap.
- **5th+ vehicle additions:** Some carriers (Safeco) do not support adding beyond a certain number of vehicles online, requiring a phone call to the carrier with 2-3 day processing.
- **Multi-intent calls:** Vehicle change bundled with payment method update, cancellation of old policy, or coverage modification — must handle all intents in one interaction.

**Automation Feasibility:** Medium
Rationale: About 35-40% of vehicle change calls could be fully automated — specifically straightforward additions where the caller has the VIN ready, wants matching coverage, and the carrier system accepts the change digitally. Removals are also relatively automatable if plate return can be confirmed. The biggest blockers are: (1) carrier system fragmentation — each of 7+ carriers has a different portal and workflow, (2) judgment calls about coverage type, commercial vs. personal classification, and non-standard vehicles, and (3) the need to communicate premium impact and get confirmation before processing. The VIN collection step is also challenging via voice (17-character alphanumeric strings).

**What the AI Agent Must Do:**
- Collect VINs accurately via voice input, including handling phonetic/military alphabet spelling, and verify them against carrier VIN databases in Auto Owners, Progressive, National General, Farm Bureau, Cincinnati, Penn National, and Safeco
- Determine whether a vehicle belongs on a personal or commercial auto policy based on ownership (individual vs. company name) and usage
- Process vehicle additions, removals, and replacements in carrier-specific portals, handling each carrier's unique workflow and field requirements
- Collect and validate lienholder/finance company information (name, mailing address, loan number) for financed and leased vehicles
- Calculate and clearly communicate premium impact before processing any change, obtaining explicit caller confirmation
- Verify NC DMV license plate return status before processing vehicle removals to avoid compliance flags
- Generate and email updated proof of insurance, ID cards, and binders to callers, dealerships, and lienholders within minutes of processing
- Recognize non-standard vehicles (jet skis, motorcycles, excavators, RVs) and route to appropriate coverage types or specialist agents
- Handle the NC 14-day new vehicle coverage window and ensure customers have immediate proof of insurance for dealership pickup

---

## Document Request (68 calls, 4.2%)

**Typical Caller:** A policyholder (personal or commercial) who needs a specific insurance document delivered quickly — declaration pages for an employer or lender, proof of insurance for the DMV or a dealership, ID cards for vehicle registration, loss run reports for switching agencies, or bond copies for regulatory compliance. The request is usually time-sensitive: a mortgage closing, a job requirement, a DMV deadline, or a contractor needing to start work.

**Resolution Workflow:**
1. Verify caller identity and locate their policy in the Alliance Insurance system.
2. Identify the specific document needed. Callers frequently use incorrect terminology — "deck page" (declaration page), "insurance card" (ID card or proof of insurance), "policy copy" (could mean dec page, full policy, or proof of insurance). Clarify exactly what is needed and who it is going to.
3. Determine the delivery destination: caller's email, a third party (employer, lender, DMV, dealership, county office, national organization), fax number, or physical mail.
4. Retrieve the document from the appropriate source:
   - **Declaration pages / ID cards / proof of insurance:** Pull from carrier portal (Auto Owners, National General, Progressive, Travelers, Utica National, Penn National/Penn Plus, Safeco, Farm Bureau, USLI).
   - **Loss runs:** Request from the carrier — these require carrier processing time (days, not minutes) and cannot be generated instantly.
   - **Bond copies:** Retrieve from Travelers Bond portal or the bond department. May require supervisor involvement.
   - **Specific forms (NCRF 31, endorsement forms, accident protection plan documents):** Locate within the carrier portal, often buried in multi-page renewal packets (e.g., "page 7 of the renew packet").
5. For carrier portals on the old/legacy platform (system migration issues), redirect the request to email (e.g., ICS support) when portal access is unavailable.
6. Send the document via email (primary), fax, or text. Confirm the recipient's email address before sending.
7. For e-signature documents, use Conga Sign or DocuSign to send for signature and track completion.
8. If the document has an error (wrong date on binder, misspelled name, wrong vehicle listed), correct and resend.
9. For self-service requests, guide the caller to the USLI portal, Auto Owners portal, or myallianceinsurance.com for future document retrieval.

**Required Knowledge:**
- Document types and their purposes: declaration pages (summary of coverages and limits), ID cards (proof of auto insurance), binders (temporary proof for new policies), loss runs (claims history for underwriting), bond copies (surety/fidelity for regulatory compliance), NCRF 31 forms (NC-specific regulatory forms), endorsement forms
- Carrier portal navigation for document retrieval across Auto Owners, National General, Progressive, Travelers, Utica National, Penn National/Penn Plus/Pin Connect, Safeco, NSA/Main Street America, Farm Bureau, USLI, and The Colonial Group
- E-signature platforms: Conga Sign, DocuSign — how to send documents for signature and track completion
- Legacy system workarounds: when a policy is on an old platform and the current portal cannot access documents, knowing the fallback process (email to ICS support)
- Loss run request procedures: these require carrier processing time and cannot be generated on the spot — must set expectations with the caller
- Bond document management: Travelers Bond portal for bond copies, renewal notices, and cancellation/reinstatement notices
- Fax and email protocols for document delivery to mortgage companies, dealerships, lenders, DMV, and county offices
- The distinction between documents that can be generated immediately (dec pages, ID cards, proof of insurance) vs. those that require carrier processing (loss runs, bond reinstatement notices)

**Systems & Tools:**
- Auto Owners policy database / portal
- National General carrier portal
- Progressive portal
- Travelers portal / Travelers Bond portal
- Utica National portal
- Penn National / Penn Plus / Pin Connect
- Safeco portal
- NSA / Main Street America portal
- Farm Bureau system
- USLI portal
- The Colonial Group customer service email
- Alliance Insurance internal policy database / CRM
- Conga Sign (e-signature)
- DocuSign
- Email / fax systems
- myallianceinsurance.com customer portal

**Outcome Distribution:**
- callback_needed: 63.6% (42 of 66 with outcomes)
- resolved: 31.8% (21)
- voicemail: 3.0% (2)
- transferred: 1.5% (1)

Document requests have the highest first-contact resolution rate of the five types in this group at ~32%. This makes sense — when the document is available in a carrier portal, the agent can pull and email it within minutes. The 64% callback rate reflects cases where the document requires carrier processing (loss runs), the agent needs to locate it in a complex portal, or the initial call was handled by front-desk staff who took a message.

**Edge Cases & Escalation Triggers:**
- **Legacy system inaccessibility:** Policy on an old platform making declaration pages inaccessible via the current portal — requires email to ICS support as a workaround, with unpredictable response times.
- **Loss runs for departed clients:** Business that has left the agency requesting loss runs — still must be provided, but requires locating historical records.
- **Bond document complications:** Bond showing cancellation notice but no reinstatement notice, requiring escalation to the bond department. Bond copy requests may need supervisor approval.
- **Two-week carrier delay blocking a claim:** Declaration page request from Utica National taking 2+ weeks, blocking a customer's claim — requires expedited ticket escalation.
- **Document correction loop:** Wrong date on binder, misspelled minor's name on a bond, wrong vehicle listed on proof of insurance — requires error identification, correction, and resend.
- **DMV fax number unknown:** Agent cannot locate the DMV fax number to send digital proof of insurance — requires research or alternative delivery method.
- **Caller cannot log into portal:** Caller requesting a document because they cannot access the customer portal — need to retrieve the document AND troubleshoot or set up portal access (USLI, Auto Owners, myallianceinsurance.com).
- **Mortgage closing deadline:** Updated declaration page required showing paid-in-full discount for an imminent mortgage closing — extreme time pressure.

**Automation Feasibility:** High
Rationale: About 55-65% of document request calls could be fully automated. The workflow is highly structured: identify the document type, retrieve from the carrier portal, and email to the recipient. Declaration pages, ID cards, and proof of insurance are the most common requests and are available instantly from carrier portals. An AI agent with authenticated access to carrier portals could handle these in under 2 minutes with no human involvement. The blockers are: (1) loss runs require carrier processing time (not instant), (2) bond documents may need supervisor approval, (3) legacy system documents require manual workarounds, and (4) callers often use incorrect terminology requiring clarification. This is the highest-automation-potential type in this group.

**What the AI Agent Must Do:**
- Interpret caller requests even when they use incorrect document terminology ("deck page" for declaration page, "insurance card" for proof of insurance, "my policy" for any of several document types) and confirm the specific document needed
- Retrieve declaration pages, ID cards, and proof of insurance from carrier portals for Auto Owners, National General, Progressive, Travelers, Utica National, Penn National/Penn Plus, Safeco, NSA/Main Street America, Farm Bureau, USLI, and The Colonial Group
- Initiate loss run requests with carriers, set proper timeline expectations with callers (days, not minutes), and track fulfillment
- Retrieve bond copies from the Travelers Bond portal and escalate to the bond department or supervisor when documents are unavailable
- Send documents via email, fax, or text to callers and third parties (employers, lenders, DMV, dealerships, county offices, national organizations) within minutes
- Locate specific forms within multi-page carrier renewal packets (e.g., NCRF 31 on page 7 of a renew packet) and provide page-specific guidance
- Initiate e-signature workflows through Conga Sign or DocuSign for documents requiring customer signatures
- Identify and correct document errors (wrong dates, misspelled names, incorrect vehicle information) before delivery
- Guide callers to self-service portal access (USLI portal, Auto Owners portal, myallianceinsurance.com) for future document needs and assist with portal setup/login troubleshooting
- Handle legacy system fallbacks by submitting email requests to ICS support when current portal access is unavailable for old-platform policies

---

## Coverage Question / Clarification (61 calls, 4.0%)

**Typical Caller:** An existing policyholder (personal or commercial) who wants to understand what their current policy does or does not cover before making a decision. These are not claims — the caller has a hypothetical or pending situation and wants to know their coverage position. Examples: "Does my homeowners cover a fallen tree from my neighbor's yard?" "Am I covered if my son drives my car?" "Does my commercial policy cover rented vehicles in California?" "Is my washer/dryer covered under my home warranty?"

**Resolution Workflow:**
1. Verify caller identity and locate their policy in the Alliance Insurance system.
2. Listen to the specific coverage question and identify the relevant policy type (auto, homeowners, commercial general liability, commercial auto, inland marine, renters, umbrella, workers' comp, builder's risk).
3. Pull up the policy details in the carrier system (Auto Owners, Progressive, National General, Cincinnati, Travelers) and review the specific coverage provisions, limits, and exclusions relevant to the question.
4. If the answer is clearly within the agent's knowledge (e.g., "Does my renters insurance cover personal belongings?" -> "Yes, up to $25,000"), explain the coverage in plain language, including any limits, deductibles, and conditions.
5. If the question involves a nuanced coverage interpretation (e.g., motor truck cargo exclusion for parts on a vehicle vs. parts being transported, D&O coverage for a condo association's vandalism claim, whether a handyman class code covers incidental roofing repair), consult with the carrier's underwriting department or a specialist agent before providing a definitive answer.
6. Clarify important distinctions the caller may not understand: coverage that follows the vehicle vs. coverage that follows the driver (towing vs. AAA), personal auto vs. commercial auto coverage for rental cars, Coverage C transit limitations (10% of coverage C in storage during a move), replacement cost vs. actual cash value.
7. If a coverage gap is identified, recommend adjustments (adding towing, increasing liability limits, adding an endorsement) and offer to process the change or transfer to an agent who can quote it.
8. If the question cannot be definitively answered without a formal coverage opinion from the carrier, explain this to the caller and arrange a follow-up with the carrier's response.
9. For educational questions, offer to send pamphlets, endorsement forms, or policy summaries via email to help the caller understand their coverage.

**Required Knowledge:**
- Deep understanding of policy coverage terms, exclusions, and limitations across all personal and commercial lines
- Carrier-specific coverage rules: Auto Owners, Progressive, National General, Cincinnati — each may have different interpretations of similar coverage questions
- NC insurance regulations and state-specific coverage laws
- Coverage distinctions that confuse callers:
  - Towing coverage (follows vehicle) vs. AAA (follows driver)
  - Personal auto rental coverage vs. commercial auto rental exclusion (commercial policies do not cover rental vehicles)
  - Coverage C (personal property) transit and storage limitations during moves (covered in transit, limited to 10% in storage)
  - Replacement cost vs. actual cash value
  - General liability vs. professional liability vs. D&O
  - Builder's risk vs. homeowner coverage during construction
- Insurance class codes and their applicability (e.g., Handyman class code covering incidental roofing repair — acceptable for 2-3 annual repairs)
- Non-owner policy limitations and when they apply (adult children driving parent's car)
- Pet and rental coverage rules (carrier-specific)
- Motor truck cargo definitions and exclusions
- Salvage title insurance options and limitations
- Non-US license driver eligibility for commercial driving
- When to give a definitive answer vs. when to defer to the carrier's underwriting department

**Systems & Tools:**
- Auto Owners policy documents / portal
- Progressive policy lookup system
- National General portal
- Cincinnati insurance system
- Travelers insurance portal
- Alliance Insurance internal policy database
- Carrier underwriting departments (for escalated coverage interpretations)
- MyAllianceInsurance website / customer portal
- Home warranty portal/database
- Email system (for sending educational materials and follow-up responses)

**Outcome Distribution:**
- callback_needed: 69.0% (40 of 58 with outcomes)
- resolved: 31.0% (18)

Coverage questions have a solid 31% first-contact resolution rate — the highest alongside document requests. When the question is straightforward and the agent has immediate policy access, they can answer on the spot. The 69% callback rate reflects cases where the question requires carrier consultation, specialist expertise, or policy document review that cannot be done while the caller waits.

**Edge Cases & Escalation Triggers:**
- **Motor truck cargo exclusion ambiguity:** Whether an exclusion applies to parts physically on a vehicle vs. parts being transported — requires policy reclassification as an auto hauler. Must escalate to carrier underwriting.
- **D&O coverage for condo association:** Board member asking about D&O coverage for a vandalism claim denial and potential small claims court action — requires legal-adjacent coverage interpretation.
- **Rental vehicle coverage across policy types:** Commercial policyholder asking about renting a sports car in California — commercial auto does NOT cover rental vehicles. Must redirect to personal auto coverage, which the caller may not have.
- **Non-US license driver eligibility:** Whether a driver with a foreign license can drive under a commercial policy — regulatory and underwriting question requiring carrier input.
- **High-value specialty vehicle:** Coverage for a rented Aston Martin — confirmed for temporary use but excluded racing and non-household drivers. Highly specific conditions.
- **Coverage during multi-state move:** Personal property in a U-Haul during a move from NC — covered in transit but limited to 10% of Coverage C when items are placed in storage.
- **Home warranty vs. homeowners confusion:** Callers often confuse homeowners insurance with a home warranty, asking about appliance coverage under their insurance policy.
- **Incidental work scope questions:** Whether a handyman class code covers occasional roofing repair — depends on frequency (2-3 times per year is acceptable).

**Automation Feasibility:** Medium-High
Rationale: About 40-50% of coverage questions could be fully automated. These are pure knowledge queries — no transactions, no money movement, no policy changes. An AI agent with access to policy documents and a comprehensive knowledge base of coverage terms, exclusions, and carrier-specific rules could handle common questions (windshield coverage, towing, renters personal property limits, rental car coverage) immediately. The blocker is the long tail of nuanced, carrier-specific questions that require underwriting judgment — motor truck cargo exclusions, class code applicability, D&O scope, coverage for unusual scenarios. For these, the AI agent must know its limits and escalate rather than guess. The second blocker is liability: giving an incorrect coverage answer could have legal consequences if the caller relies on it.

**What the AI Agent Must Do:**
- Access and interpret policy coverage details, limits, deductibles, and exclusions from carrier systems (Auto Owners, Progressive, National General, Cincinnati, Travelers) in real time
- Answer common coverage questions definitively with reference to specific policy provisions: windshield/glass coverage, towing and roadside assistance, renters personal property limits, rental car coverage, comprehensive vs. collision scope
- Explain coverage distinctions in plain language: replacement cost vs. actual cash value, towing (follows vehicle) vs. AAA (follows driver), personal auto vs. commercial auto rental coverage, Coverage C transit and storage limitations
- Recognize questions that exceed standard agent knowledge and require carrier underwriting consultation — motor truck cargo exclusions, D&O scope, class code applicability, non-standard risk scenarios — and escalate with a structured question to the carrier
- Identify coverage gaps during the conversation and proactively recommend policy adjustments (adding towing, increasing limits, adding endorsements), offering to connect the caller with an agent who can process changes
- Distinguish between homeowners insurance and home warranty questions, redirecting warranty questions appropriately
- Send educational materials (pamphlets, endorsement forms, coverage summaries) via email when the caller needs time to review their options
- Maintain a clear liability boundary: explicitly state when an answer is a general explanation vs. a definitive coverage determination that should come from the carrier, and document all coverage guidance provided

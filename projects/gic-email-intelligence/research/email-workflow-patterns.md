# Email Workflow Patterns at GIC Underwriters

**Methodology:** Read 30+ full email threads from the gic_email_intelligence database, spanning all major LOBs, submission channels, carriers, and lifecycle stages. Every finding is derived from actual email content, not metadata alone.

**Sources:** gic_email_intelligence MongoDB — emails collection (3,214 emails), submissions collection (2,754 submissions), extractions collection (304 extractions). Date range: 2025-09-15 to 2026-03-16.

**Date Analyzed:** 2026-03-24

---

## 1. How Emails Actually Flow Through GIC's Business

GIC Underwriters operates as a Managing General Agency (MGA) — a wholesale intermediary. They sit between retail insurance agents (who have customers) and carriers (who write policies). Their core function is receiving applications from agents, submitting them to carriers, and managing the back-and-forth until a quote is issued, declined, or the agent stops responding.

The quote@gicunderwriters.com inbox is the central nervous system. Inbound email arrives from three sources:

1. **Carrier systems** (USLI, Hiscox) — automated quote notifications, decline notices, pending file requests
2. **Retail agents** — quote submissions, replies to info requests, follow-ups, renewal requests
3. **GIC's own portal** — automated submission confirmations from noreply@gicunderwriters.com and quote@gicunderwriters.com

Outbound email goes to:
- **Retail agents** — info requests, quote deliveries, renewal notices
- **Carrier underwriters** — submission details, agent replies, approval requests
- **Internal GIC staff** — forwarded agent messages, internal coordination

### The Critical Insight: Most Email Is Machine-Generated

Of the 3,214 emails in the inbox, the overwhelming majority (2,609 USLI quotes + 213 USLI pending + 155 USLI declines + 26 Hiscox quotes = 3,003) are **automated carrier notifications**. Only ~200 emails involve actual human communication — agent submissions, replies, follow-ups, GIC internal coordination, and info requests. This means the inbox is approximately 93% automated carrier email and 7% human conversation.

---

## 2. Common Workflow Patterns by LOB

### Pattern A: The USLI Auto-Quote (Dominant Pattern — ~85% of All Submissions)

This is the most common workflow. A retail agent uses USLI's "Retail Web" system (accessed through GIC) to submit an application. USLI's automated system instantly quotes it. GIC receives notification emails but does not actively participate in the quoting process.

**Typical email sequence:**

1. `no-reply@usli.com` → "USLI Retail Web Quote [POLICY#] for [INSURED] from [AGENT] at [AGENCY]" — automated notification with 3 PDF attachments (Customer, Retailer, Applicant copies)
2. `[underwriter]@usli.com` → "USLI Instant Quote Services Quote [POLICY#] for [INSURED]" — human underwriter confirmation with same 3 PDFs

Often there are 2-3 versions of the underwriter email (same subject, minutes apart) as the underwriter reviews and possibly adjusts terms. This creates the appearance of a multi-email "thread" but it is really just USLI's internal workflow generating duplicate notifications.

**Real example — UPFLIP IN SOUTH FLORIDA, LLC (Multi-Class Package):**
- Email 1 (14:41): USLI auto-quote notification from no-reply
- Email 2 (14:56): Julie O'Brien quote letter — 3 PDFs
- Email 3 (15:00): Julie O'Brien quote letter again (duplicate, 4 min later)
- Email 4 (17:03): Julie O'Brien quote letter again (revision, 2 hours later)
- Email 5 (18:03): Julie O'Brien quote letter again (another revision, 1 hour later)

All 5 emails are carrier-side. GIC had zero involvement. This submission has 5 emails but required zero GIC human effort.

**LOBs that follow this pattern:**
- Personal Liability (691 submissions, almost all auto-quoted)
- General Liability (512 — most auto-quoted, some need manual handling)
- Special Events (218)
- Excess Personal Liability (208)
- Commercial Property (180)
- Commercial Package (178)
- Non Profit (151)
- Most smaller LOBs

### Pattern B: The Decline-Then-Quote (Common with USLI)

USLI's automated system declines part of a submission but quotes another part. Both notifications arrive.

**Real example — CASH OUT HOME INVESTMENTS LLC (Commercial Package):**
- Email 1 (01:44): USLI Retail Web **Decline** — property component declined
- Email 2 (02:00): USLI Retail Web **Quote** — liability component quoted
- Email 3 (17:19): USLI underwriter sends final quote confirmation

**Real example — 2835 NE 5 PL Cape Coral FL 33909 LLC (Builders Risk):**
- Email 1 (17:52): USLI Retail Web Quote for Builders Risk
- Email 2 (18:11): USLI Retail Web **Decline** — "Construction has already started"
- Email 3 (18:25): Remarket notice from Ashley Okoorian with pre-filled application to help GIC place it elsewhere

The "Remarket This Risk" email is notable — USLI proactively helps GIC find alternative placement when they cannot write a risk. This shows a carrier-MGA relationship where the carrier wants to keep the submission pipeline healthy even when they decline.

### Pattern C: The Info Request Cycle (Where Human Work Happens)

This is where GIC staff actually earn their keep. A submission comes in incomplete, GIC requests missing documents, the agent replies, and GIC processes it.

**Real example — ARENAL PROPERTY MANAGEMENT LLC (General Liability):**
1. GIC (Juan Carlos Diaz-Padron) sends info request to agent Ana Mesa at Univista: "Please send Wind Mit and 4Point documents to offer quotation on this."
2. Agent Adriana Lastre replies same day with completed Wind Mitigation and 4-Point inspection PDFs
3. Agent follows up 3 days later: "Follow up on this please, let me know if you need anything else from us."
4. GIC CSR Maria Gonzalez internally forwards to quote team: "Agent already forward the missing info on Friday, agent is waiting on the quote"

**Real example — Deep Breath Holdings, Inc (Boat/Marine):**
1. GIC (Maribel Rodriguez) sends info request: "I have released terms to our carrier for approval, but please note I have offered terms based on a depreciated value of the vessel... $250k Hull Sum Insured was requested, and if this is not an error, please confirm whether there has been any upgrades"
2. Agent Barry Sanders replies: "Insured wants 250K on the boat, and you are offering 18K, without updates, etc. Let me reach out to insured."
3. GIC responds: "We will check on this. Your application requested 25k for hull coverage."
4. Agent replies with documentation: "Please see improvements on the boat. They are looking for 250K on Hull coverage. They purchased the boat for 25K" — attaches "phil's boat bill breakdown.pdf"

This thread shows real underwriting judgment: the hull value discrepancy needed investigation, the agent had to go back to the insured, and GIC needed to see evidence of improvements.

### Pattern D: The USLI Pending File (Carrier Needs More Info)

USLI cannot auto-quote and requests additional information from GIC, who then relays to the agent.

**Real example — BLAZE PILATES (Multi-Class Package):**
1. Elizabeth Shults (USLI underwriter) sends pending file request to Julissa Arriola (GIC): "Thank you for allowing us to review this account, however we need additional information"
2. GIC (Maribel Rodriguez) relays agent's response to USLI with partial info: "BLAZE PILATES LLC / MARIANNE CHUBIRKA, 1864 RADIUS DR APT 902 HOLLYWOOD, FL 33020, THE SPACE IS RENTED"
3. USLI responds: "We cannot proceed without answers to all of the requested information."

GIC is the intermediary — they gather information from agents and relay it to USLI. The pending file process shows a three-way conversation where GIC mediates between agent and carrier.

### Pattern E: The CSR-Forwarded Agent Follow-Up

Agents call GIC's main line or email csr@gicunderwriters.com. The CSR team forwards these to the quote team.

**Real example — HANOI CARDENAS (Homeowners):**
1. Agent Raciel Rodriguez (Univista) emails GIC quote team: "Could you provide me with a quote with a 2% hurricane deductible?"
2. Agent follows up by emailing CSR team
3. CSR Tai-Siu De La Prida forwards to quote team: "Please read below message received from the agent"
4. Agent follows up again: "I sent you an email requesting a quote that includes the 2% hurricane deductible. Additionally, I wanted to know if you could send me a quote without the wind mitigation inspection."
5. CSR forwards again to quote team

This reveals that agents contact GIC through multiple channels (quote@ directly, CSR phone line, CSR email) and the CSR team acts as a message relay to the underwriting team.

### Pattern F: The Renewal Cycle

Existing policies approaching expiration generate a series of emails.

**Real example — UNIQUE INSURANCE SERVICES (Sebanda Insurance):**
1. GIC sends renewal warning to agent: "We have not received instructions to renew this policy. If you would like to renew coverage, please contact us immediately... If we do not hear back from you, the notice below will be mailed directly to the insured notifying them that this policy was not renewed."
2. Agent replies: "renew please"

The renewal notice is a two-part message — one addressed to the producer, one addressed to the policyholder. This is GIC enforcing a renewal deadline with implicit threat of direct policyholder contact (bypassing the agent).

---

## 3. Portal vs. Email Submission Differences

### Portal Submissions (from noreply@gicunderwriters.com or quote@gicunderwriters.com)

Portal submissions are structured. They follow a consistent format:

**From noreply@gicunderwriters.com:**
- Subject: "[LOB] - New Quote Submission - [NUMBER]"
- Example: "Motorsports - New Quote Submission - 143085"
- Body: Empty (all data is in the attached PDF)
- Single PDF attachment with a GUID-like filename (e.g., 24DB67B67819404BA4C71C4BB5FEE401.pdf)

**From quote@gicunderwriters.com:**
- Subject: "[LOB] Application Request - [INSURED NAME]"
- Example: "HandyPerson Application Request - Michael Dowdell"
- Body: Structured text with insured name, sender email, submitter name, agency code
- Single PDF attachment with a code-based filename (e.g., 0149130009316202622917-63.pdf)

**From quotes@granadainsurance.com (Granada system):**
- Subject: "[LOB] Application Request - [INSURED NAME]"
- Body: Empty
- Attachments include application PDF plus supporting documents (registrations, prior dec pages)

Portal submissions are clean for automation: consistent subject formats, reference numbers, structured data in PDFs. The Golf Cart submissions are a perfect example — all 3 portal submissions had structured application data that extraction could parse into VIN, driver license, address, etc.

### Email Submissions (from retail agents directly)

Agent submissions are unstructured and chaotic:

- Subject lines vary wildly: "QUOTE", "PLEASE QUOTE", "Commercial Umbrella", "Sanjay Ghulati", "New Quote LipsByKatrin Inc"
- Body text ranges from nothing to "Please quote" to detailed descriptions
- Attachments are a mix: ACORD forms, existing policy dec pages, loss runs, driver IDs, photos, email signatures as images
- Some agents CC multiple recipients; others only email quote@ or quotes@

**Real example — Susana Avila (Golf Cart):** Subject "QUOTE", body empty, 2 attachments: "Jessica ID.pdf" and "QUOTE GOLF CART.pdf". The ID belongs to Jessica Maria Herrero Garcia, but the quote form is actually for a different insured (Jeffrey Cueto at a different address). This kind of mismatch requires human interpretation.

**Real example — Erlic Reyes (IGEE Insurance, BOP):** Emailed "Good morning, Please see attached in order for us to obtain a quote. The GL quote is needed urgently." — attached ACORD 125/126, a restaurant supplement, and a JPEG of an image. Agent specified urgency, which portal submissions cannot do.

**Real example — Anisel Hernandez (Estrella Insurance):** Subject "PLEASE QUOTE", body "Please quote", 12 attachments — but 10 are email signature images (logo, social media icons, review buttons, etc.) and only 2 are actual insurance forms (ACORD 125 and 126). This is common — email signatures inflate attachment counts dramatically.

### The Granada System Submissions

Granada Insurance uses its own portal system that sends to both quote@gicunderwriters.com and quotes@granadainsurance.com. These include test submissions (e.g., "test mukul" for "Artisan & Service Industries") which suggests an active development/integration effort.

---

## 4. How GIC Communicates

### Info Requests (Outbound)

GIC uses a templated format for info requests:

> Dear Producer,
>
> Thank you for your submission for the above referenced applicant.
>
> In order to continue the quoting process, the carrier requires the additional documentation below:
>
> -[SPECIFIC REQUEST]
>
> We will be unable to provide a quote until this information has been received.
>
> Sincerely,
> [STAFF NAME]
> GIC Underwriters

The specific request varies but follows patterns:
- "Please send Wind Mit and 4Point documents" (property LOBs)
- Clarification on hull values and upgrades (marine)
- "Error issued motortruck listed below. Agents can't Bind" (system errors)

### Quote Deliveries (Outbound)

GIC's Transportation Division uses a distinct template for commercial auto quotes:

> Quote Id: [NUMBER]
> Applicant: [NAME]
>
> Dear Producer,
> Thank you for the new submission. Attached you will find the physical damage quote proposal for [NAME].
>
> Please review the terms and subjectivities carefully. Terms offered may be different then what was on your application.
>
> To Bind Coverage:
> Send written request along with the documents requested below to bind@gicunderwriters.com

### Renewal Notices (Outbound)

Two-part message structure: one for the agent, one for the insured. Includes an implicit threat: "If we do not hear back from you, the notice below will be mailed directly to the insured."

### Internal Coordination

GIC's internal email flow is visible when replies arrive back at quote@. Key patterns:
- CSR staff (Maria Gonzalez, Tai-Siu De La Prida) forward agent messages to the quote team with contextual notes ("Agent already forward the missing info on Friday, agent is waiting on the quote")
- Underwriters (Julissa Arriola, Saly Casanueva) forward USLI documents and discuss with Juan Carlos Diaz-Padron
- Maribel Rodriguez operates "On Behalf Of GIC Quotes" — she is the primary quote processor

### GIC Staff Identified

| Person | Role | Email | Observed Activity |
|--------|------|-------|-------------------|
| Maribel Rodriguez | Quote Processor | maribelrodriguez@gicunderwriters.com | Sends info requests, relays agent info to USLI, sends quote deliveries, operates as "GIC Quotes" |
| Juan Carlos Diaz-Padron | Underwriter/Manager | jcdp@gicunderwriters.com | Signs info requests, reviews internal questions |
| Julissa Arriola | Underwriter | jarriola@gicunderwriters.com | Handles transportation division, advises on binding |
| Saly Casanueva | Underwriter | scasanueva@gicunderwriters.com | Forwards USLI quotes internally |
| Maria Gonzalez | CSR | csr@gicunderwriters.com | Relays agent follow-ups, tracks missing information |
| Tai-Siu De La Prida | CSR | tprida@gicunderwriters.com | Forwards agent messages, phone tickets |
| Claudia Inoa | Contract Binding (E&S) | (via quote@) | Handles approval requests to AmTrust |

---

## 5. How Carriers Communicate

### USLI (Dominant Carrier — 95% of Submissions)

USLI has the most sophisticated automated communication:

**Automated (no-reply@usli.com):**
- "Quote [POLICY#] for [INSURED] from [AGENT] at [AGENCY]" — initial auto-quote
- "Retail Web Quote [POLICY#] for [INSURED]" — retail web submission with 3 version PDFs
- "Retail Web Decline [POLICY#] for [INSURED]" — with decline reason in body
- "Retail Web Submit [POLICY#] for [INSURED]" — pending submission
- "Submission Status Notification - Under Review" — assigned to underwriter

**Human Underwriters (name@usli.com):**
- "Instant Quote Services Quote [POLICY#]" — underwriter-confirmed quote
- "USLI Pending File [POLICY#]" — need more information
- "USLI Declination [POLICY#]" — formal decline with attached memo
- "Instant Quote - Remarket This Risk" — decline with helpful pre-filled application for remarketing

Known USLI underwriters: Julie O'Brien, Jee Choi, Jacob Webster, Frank Finney, Frederick Robinson, Brian Donahue, Nicole Warn, Michael Burd, Elizabeth Shults, Ashley Okoorian, Daniel Hager

### Hiscox (19 Submissions)

Hiscox sends rich HTML emails from contact@hiscox.com with premium, coverage details, and a "Retrieve quote" portal link. Always includes agent of record details and attached specimen documents.

### Swyfft (Rare, Homeowners)

Appears via support@swyfft.zendesk.com for homeowners underwriting follow-ups. Uses a Zendesk ticket format with screenshots of concerns (e.g., "Explanation of outdoor kitchen/tables required").

### AmTrust (Workers Comp, E&S)

GIC sends "Approval Request" emails to AmTrust underwriters (ivor.williams@amtrustgroup.com) for referral accounts.

---

## 6. Where Workflows Break Down or Get Stuck

### Duplicate Emails
USLI frequently sends the same quote 2-4 times within hours. The same submission can generate a "Retail Web Quote" auto-notification, then 2-3 "Instant Quote Services Quote" emails from the underwriter as they make minor adjustments. This inflates email counts and makes it hard to know which version is final.

### The CSR Relay Problem
Agents contact GIC through multiple channels (quote@, quotes@, csr@, phone). CSR staff manually forward messages to the quote team with notes. This creates internal email that looks like new activity but is just routing. A single agent follow-up can generate 2-3 internal emails.

### Agent Submission Quality
Agent emails are wildly inconsistent. Some have no subject, no body, and only attachments. Some have 10+ image attachments that are just email signature graphics. Some have mismatched insured names between the email, the application, and the ID document.

### The Missing GIC Outbound
The database captures emails arriving at quote@gicunderwriters.com. Most of GIC's outbound communication (info requests to agents, quote deliveries) is only visible when agents reply and include the original message in the thread. This means we see the info request template only embedded in reply chains, not as standalone outbound emails.

### Stale Submissions
Many submissions sit in "new" stage with only 1 email (the initial carrier quote notification). There is no visible follow-up from GIC to deliver the quote to the agent. It is unclear whether quote delivery happens outside this email inbox (e.g., through USLI's Retail Web portal directly to the agent).

### Name Mismatches
The Jessica Maria Herrero Garcia submission includes a quote form for Jeffrey Cueto and an ID for Jessica. The system extracted two different named insureds from the same submission. Agents sometimes attach documents for the wrong insured or include prior coverage for comparison.

---

## 7. Typical Email Sequences (Annotated)

### Sequence A: Happy Path (Auto-Quote, No Human Intervention)
```
[Day 1, 19:39] no-reply@usli.com → "USLI Retail Web Quote MPL026J50B2 for LORRIE L KENDALL"
  3 PDFs: Customer, Retailer, Applicant versions
[Day 1, 19:56] bdonahue@usli.com → "USLI Instant Quote Services Quote MPL026J50B2"
  3 PDFs: confirmed quote
[Day 2, 16:35] nwarn@usli.com → "USLI Instant Quote Services Quote MPL026J50B2 for Dwayne Kendall and Lorrie Kendall"
  Name corrected to include both insureds, revised quote issued
```
Total GIC effort: Zero.

### Sequence B: Decline-Then-Remarket
```
[Day 1] no-reply@usli.com → "USLI Retail Web Decline MSE026J3506 for Worship of the Rock"
  Special Events declined
[Day 1, +6 min] michael.burd@usli.com → "Instant Quote Services Quote MSE026J3506"
  Partial quote offered after decline
[Day 1, +8 min] michael.burd@usli.com → Revised quote (name corrected to "Worship on the Rock")
[Day 1, +10 min] michael.burd@usli.com → Another revision
```
GIC flagged as "attention" because decline + quote arrived together.

### Sequence C: Full Info Request Cycle
```
[Day 1] Agent submits via portal: "Motorsports - New Quote Submission - 143009"
[Day 1] GIC reviews, finds missing Wind Mit + 4Point docs
[Day 1] GIC (Juan Carlos) → agent: "Info Request for ARENAL PROPERTY MANAGEMENT LLC- 143009"
[Day 3] Agent (Adriana Lastre) → quote@: Attaches completed Wind Mit + 4Point PDFs
[Day 5] Agent follows up: "Follow up on this please, let me know if you need anything else"
[Day 5] GIC CSR (Maria Gonzalez) → quote team: "Agent already forward the missing info, agent is waiting on quote"
```
Still awaiting GIC action after 5+ days.

### Sequence D: Agent System Error
```
[Day 1] Granada system → GIC: Motor Truck Cargo Quote for Saez Trucking LLC (#27712)
[Day 1] Agent (German Portillo) → GIC: "I am trying to get the financial agreement and is giving me an error page"
[Day 1] GIC (Maribel) → agent: "Error issued motortruck. Agents can't Bind"
[Day 5] Agent (Sam Amador) → GIC: "Corrected, Please Try again"
```
System error blocked binding. Agent had to fix and resubmit.

---

## Open Questions

1. **Where does quote delivery happen?** Most USLI quotes appear to go directly to agents via Retail Web. Does GIC also email the quote to the agent? The database doesn't show this.
2. **What happens after "quoted"?** 85% of submissions are in "quoted" stage but there is no bind request, no premium collected, no policy issued visible in this inbox. Binding appears to go to bind@gicunderwriters.com (a separate inbox).
3. **What is GIC's actual SLA?** The Arenal Property Management thread shows 5+ days without action after info was received. Is this typical?
4. **How does Maribel Rodriguez handle volume?** She appears to be the primary quote processor. Is she a bottleneck?
5. **Why are there so many duplicate USLI emails?** Is this a USLI system issue or are underwriters making multiple revisions?

---

## Data Model Implications

1. **Email type classification needs refinement.** The "gic_info_request" type (4 emails) miscategorizes some — one is a Swyfft underwriting follow-up, another is an agent requesting ACORD forms. The actual GIC info request template is only visible embedded in reply chains.
2. **Thread reconstruction is hard.** Email subjects change, CCs shift, and internal forwards create new email IDs. The submission-to-email linking is the right approach (grouping by insured/reference number rather than email threading).
3. **Outbound tracking is missing.** GIC's sent emails to agents and carriers are largely invisible. Only replies that come back to quote@ reveal what GIC sent.
4. **Attachment significance varies wildly.** A submission with 12 attachments might have 10 signature images and 2 actual documents. The extraction pipeline should filter email signature images.

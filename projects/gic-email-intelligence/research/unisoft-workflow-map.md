# Unisoft Workflow Map: Outlook → AMS

> How GIC's team takes information from the Outlook inbox and enters it into Unisoft.
> **Living document** — updated as we learn more from JC, UAT exploration, and API discovery.
> Last updated: 2026-03-31

---

## Overview

GIC's quote@gicunderwriters.com inbox is the central intake point. **4-5 people** process it daily. The workflow is:

1. Email arrives in shared Outlook inbox
2. Team member reads, triages, determines what to do
3. Data is entered into Unisoft (the "management system")
4. Once processed, **email is deleted from Outlook** — this signals to the rest of the team that it's been handled
5. Status is now visible to everyone in Unisoft

**First principle:** Unisoft is the single source of truth. If it's not in Unisoft, customer service can't see it, the team can't track it, and there's no institutional record. The email inbox is a temporary staging area.

---

## The Core Unisoft Entry Flow

> Source: JC walkthrough (March 27, 2026)

### Navigation Path
```
Unisoft Portal → Quotes → Entry → New Quote
```

### Steps to Create a New Submission

| Step | Action | Data Source | Notes |
|------|--------|-------------|-------|
| 1 | Click "New Quote" | — | Business type defaults to "new" |
| 2 | Select **Line of Business** | From email subject, body, or attachments | e.g., General Liability, Boats & Yacht |
| 3 | Select **Subline** | From email context | Specific product within the LOB |
| 4 | Select **Agency** | From email sender or body | The retail agent's agency |
| 5 | Assign **Agent Contact** | From email sender | Specific person at the agency |
| 6 | Go to **Submissions tab** | — | Within the quote record |
| 7 | Add **Broker** | Always "GIC Underwriters" | GIC is the intermediary |
| 8 | Add **Carrier** | Determined by GIC staff | e.g., USLI, Hiscox, Dellwood |

**JC's estimate:** Only about **5-10 data columns** need to be filled per submission. **Categorization (LOB/subline) is the hardest part.**

### What a "Submission" Means in Unisoft

A submission acts as a **folder** — it's a container for all work related to a specific application with a specific carrier. Inside that folder:

- The application and attachments are imported
- Activities are logged (e.g., "Submit Application to Carrier")
- Quote/decline responses are recorded
- Tax and fee calculations happen automatically
- The system can assign to specific underwriters/teams

---

## Workflow by Email Type

### Workflow 1: New Agent Submission

**Trigger:** Email from retail agent with new business submission
**Email type:** `agent_submission` (2.3% of inbox, but high-value)
**Volume:** ~73 emails in 6-month sample

| Phase | Outlook Action | Unisoft Action | Why |
|-------|---------------|----------------|-----|
| **Receive** | Read email, identify LOB, insured, agent | — | Understand what this is |
| **Create** | Extract: LOB, subline, agent, agency, insured name | Quotes → Entry → New Quote → fill fields | Creates the submission "folder" in AMS |
| **Import** | Download attachments (ACORD forms, loss runs) | Import application into submission | Carrier needs these documents |
| **Triage** | Assess completeness against LOB requirements | — | Determine if ready for carrier |
| **[If complete]** | — | Activity: "Submit Application to Carrier" → email carrier from portal | Portal email = documented, visible |
| **[If incomplete]** | — | Note what's missing | Send info request to agent |
| **Signal** | **Delete email from Outlook** | — | Team knows it's been handled |

**First principle:** The submission must be created in Unisoft BEFORE any carrier communication happens, so that all activity is tracked and visible to customer service.

### Workflow 2: USLI Auto-Quote Received

**Trigger:** USLI sends quote notification to quote@
**Email type:** `usli_quote` (80.7% of inbox — highest volume)
**Volume:** ~2,553 emails in 6-month sample

| Phase | Outlook Action | Unisoft Action | Why |
|-------|---------------|----------------|-----|
| **Receive** | Read email, extract ref number, insured, premium | — | Identify the submission |
| **Match** | Find existing submission by ref number | Open existing quote record | Link to prior submission |
| **[If no existing]** | — | Create new quote with LOB, agent, carrier info | USLI auto-quoted without GIC initiating |
| **Record** | Extract: premium, coverage limits, effective date | Enter quote amount | Tax/fee calculations happen automatically |
| **Forward** | — | Forward quote to retail agent (from portal or Outlook) | Agent needs to see the quote |
| **Signal** | **Delete email from Outlook** | — | Processed |

**JC's assessment:** This is the **#1 automation target** — "very repetitive and boxed up." High volume, predictable format, minimal judgment required.

**Key insight:** Many USLI auto-quotes arrive without GIC ever creating the initial submission (agent submitted directly via USLI Retail Web). In these cases, GIC still needs to enter it into Unisoft for tracking.

### Workflow 3: USLI Pending File

**Trigger:** USLI needs more information to quote
**Email type:** `usli_pending` (6.7% of inbox)
**Volume:** ~212 emails

| Phase | Outlook Action | Unisoft Action | Why |
|-------|---------------|----------------|-----|
| **Receive** | Read pending notice, identify what USLI needs | Open existing submission | Track the pending status |
| **Update** | — | Update submission status | Visible to CS team |
| **Relay** | Forward USLI's request to retail agent | Log activity | Agent needs to provide info |
| **Signal** | **Delete email from Outlook** | — | Tracked in Unisoft now |

### Workflow 4: USLI Decline

**Trigger:** USLI declines the submission
**Email type:** `usli_decline` (4.6% of inbox)
**Volume:** ~147 emails

| Phase | Outlook Action | Unisoft Action | Why |
|-------|---------------|----------------|-----|
| **Receive** | Read decline, extract reason, ref number | Open existing submission | Track the decline |
| **Record** | — | Update status to declined, note reason | Historical record |
| **Decide** | Assess: can this be remarketed to another carrier? | — | Business judgment |
| **[If remarket]** | — | Submit to alternative carrier | Try another carrier |
| **[If no]** | Notify agent of decline | Log decline notification activity | Agent needs to know |
| **Signal** | **Delete email from Outlook** | — | Done |

### Workflow 5: Agent Reply (Info Response)

**Trigger:** Agent responds to GIC's info request
**Email type:** `agent_reply` (1.2% of inbox)
**Volume:** ~37 emails

| Phase | Outlook Action | Unisoft Action | Why |
|-------|---------------|----------------|-----|
| **Receive** | Read reply, identify which submission | Open existing submission | Link the info to the right record |
| **Import** | Download any new attachments | Import documents into submission | Complete the application |
| **Assess** | Check if now complete | Update completeness status | Ready for carrier? |
| **[If complete]** | — | Activity: "Submit Application to Carrier" | Move forward |
| **Signal** | **Delete email from Outlook** | — | Tracked |

### Workflow 6: GIC Portal Submission

**Trigger:** Agent submitted via GIC's online portal (gicunderwriters.com)
**Email type:** `gic_portal_submission` / `gic_application`
**Volume:** ~32 emails

| Phase | Outlook Action | Unisoft Action | Why |
|-------|---------------|----------------|-----|
| **Receive** | Read portal notification | — | Portal may auto-create in Unisoft |
| **Verify** | Check data quality and completeness | Open/create submission | Ensure data is correct |
| **Process** | Same as new agent submission from here | — | — |

**Note:** Portal submissions may already create records in Unisoft automatically (TBD — depends on integration level between GIC portal and Unisoft AMS).

### Workflow 7: Hiscox Quote

**Email type:** `hiscox_quote` (0.8% of inbox)
**Volume:** ~24 emails

Similar to USLI quote workflow but with Hiscox-specific formatting. Hiscox emails include HTML with premium, coverage details, and "Retrieve quote" portal links.

---

## What Changes By LOB

| LOB | Carrier | Subline Complexity | Typical Workflow | Volume |
|-----|---------|-------------------|------------------|--------|
| GL (General Liability) | USLI, Hiscox | Multiple sublines | Brokered standard | High |
| Personal Liability | USLI | Limited sublines | Brokered standard | Highest by count |
| Special Events | USLI | Event-specific | Brokered standard | Medium |
| Golf Cart / Motorsports | Granada (GIC direct) | Motorsports-specific | Direct underwritten | Growing |
| Commercial Auto | AmTrust, others | Complex | Brokered, multi-carrier | Medium |
| Workers Comp | AmTrust, others | Class-code dependent | Brokered | Low |
| Boats & Yacht | TBD | Hull/liability split | Direct or brokered | Unknown |

**Key variation:** For **direct-underwritten** LOBs (golf carts), GIC IS the carrier — there's no external carrier submission step. The workflow is shorter: receive → triage → underwrite → quote → bind.

---

## Who Does What

| Person | Primary Responsibility | Email Types Handled |
|--------|----------------------|---------------------|
| **Maribel Rodriguez** | Quote processing (primary) | All types, highest volume |
| **Julissa Arriola** | Transportation division | Commercial auto, trucking |
| **Saly Casanueva** | Underwriting | USLI quotes, internal routing |
| **Claudia Inoa** | E&S binding | Approval requests to AmTrust |
| **JC (Juan Carlos)** | Complex submissions, strategy | Signs off on complex info requests |
| **CSR team** (Tai-Siu, Coralia, Maria) | Phone/chat relay | Forward to quote team |

---

## The "Delete = Done" Signal

**Current coordination mechanism:** When a team member finishes processing an email, they **delete it from Outlook**. This is how 4-5 people coordinate on a shared inbox without duplicating work.

**Problems with this:**
- No audit trail in Outlook
- If someone accidentally deletes before processing, the submission is lost
- No visibility into who processed what
- Can't track processing time or throughput

**Our system replaces this:** The email intelligence pipeline creates the institutional record (classification, extraction, linking) before anyone touches it, making the Outlook deletion unnecessary for coordination.

---

## Automation Priority (JC's Words)

JC identified the automation priorities in order:

1. **"Map out the submission, open the quote ID, select the line and subline of business, and import that data into the management system"** — i.e., automate the data entry into Unisoft
2. **"Automatically send an acknowledgment"** — confirm receipt to agent
3. **"If confident, set up the submission and perform the activity of sending the application to the carrier"** — full automation for clear-cut cases
4. **USLI quotes** are the starting point — "very repetitive and boxed up"

---

## Data Mapping: Email Fields → Unisoft Fields

| Email Intelligence Field | Unisoft Field | Source | Confidence |
|--------------------------|--------------|--------|------------|
| `classification.line_of_business` | Line of Business dropdown | Email subject + PDF extraction | High for USLI (prefix-based), Medium for agent submissions |
| TBD | Subline | Email context, needs LOB-specific logic | Low — we don't extract this yet |
| `submission.retail_agent_name` | Agent Contact | Email from/body | Medium |
| `submission.retail_agency_name` | Agency | Email from/body, agent DB | Medium |
| Always "GIC Underwriters" | Broker | Static | 100% |
| `submission.carrier_name` | Carrier | Email classification | High for USLI/Hiscox |
| `extraction.premium` | Quote Amount | PDF extraction | High when PDF extracted |
| `extraction.effective_date` | Effective Date | PDF extraction | High when PDF extracted |
| `extraction.coverage_limits` | Coverage Limits | PDF extraction | High when PDF extracted |
| `submission.named_insured` | Insured Name | Email + PDF | High |
| `submission.reference_numbers` | Reference Number | Email subject | High for USLI |
| Attachments (S3) | Application Import | Downloaded from email | Direct |

---

## Data Discovered from Video (Confirmed)

### Carriers in Unisoft (from Carrier dropdown)
1. United States Liability Insurance Company (USLI)
2. Hallmark Specialty Insurance Company
3. Mid Continent Casualty Company
4. Mid Continental/Excess & Surplus Insurance Company
5. Security National Insurance Company
6. PHOCOS INSURANCE COMPANY
7. LIG Specialty Insurance Company
8. Mutual Bones Part Insurance Co.

### Brokers in Unisoft (from Broker dropdown)
1. GIC Underwriters, Inc.
2. Atlas General Insurance Services
3. AMWINS / David Intermediaries
4. BPS
5. Cornerstone Underwriting Parlour
6. FOXQUILT
7. International Grain...
8. PARAGON SPECIALITY INS CO
9. RISK PLACEMENT SERVICES INC.

### Activities Available (30+ from Activity Action dropdown)
See `unisoft-software-guide.md` for the complete list. Key ones for our automation:
- **Submit application to carrier** — the core submission activity
- **Request additional form/information** — info request to agent
- **Send Declination to Agent** — decline notification
- **Send offer to agent** / **Send offer Policy on to agent** — quote delivery
- **Request Loss Runs from Carrier** — loss run request
- **Send New Renewal to Agent** — renewal notification

---

## Open Questions (To Investigate)

- [x] ~~What are all the **subline** options per LOB in Unisoft?~~ GL confirmed: 4 sub-LOBs. Other LOBs still TBD.
- [x] ~~How does the **agency/agent dropdown** work?~~ Scrollable list with format "[Agency Name] | # [number]". Hundreds of entries.
- [ ] What happens after "Submit Application to Carrier" activity? Does Unisoft send email, or does the user send separately?
- [ ] Do **portal submissions** (gicunderwriters.com) auto-create records in Unisoft?
- [ ] How does the quote amount entry work? Is it a single premium field or broken down?
- [ ] What **other activities** exist besides "Submit Application to Carrier"?
- [ ] How is the **assignment/routing** feature configured? What criteria?
- [ ] How does **Unisoft handle renewals** vs new business?
- [ ] What does the **search/lookup** flow look like when finding an existing submission?
- [ ] Does personal liability (top LOB by volume) have a special workflow? JC said they've "never been efficiently put into the management system"

---

## API-Driven Automation Path (Confirmed 2026-04-01)

Fiddler traffic interception confirmed the ClickOnce app uses **SOAP and REST APIs**, not direct database access. The core automation operations are:

| Email Pipeline Output | Unisoft API Call | API Type |
|----------------------|------------------|----------|
| New submission detected | `SetQuote` (Action=Insert) | SOAP |
| LOB, sub-LOB classified | LOB/SubLOB fields in SetQuote (codes like CG, AC) | SOAP |
| Agent identified | AgentNumber field in SetQuote | SOAP |
| Carrier determined | `SetSubmission` with CarrierNumber + BrokerId | SOAP |
| Activity logged | `SetActivity` with ActionId | SOAP |
| Task created | `POST /api/tasks` with taskAssociation | REST |
| Attachment uploaded | `AddQuoteAttachment` | SOAP (file svc) |

The full API reference is in `unisoft-api-reference.md`.

**Key finding:** We do NOT need UI automation. Every operation JC demonstrated in the walkthrough maps to an API call we can make from Python.

---

## Changelog

| Date | Update | Source |
|------|--------|--------|
| 2026-03-31 | Initial creation from JC walkthrough transcript + existing research | Meeting transcript, business-model-synthesis.md, submission-lifecycle.md |
| 2026-04-01 | Added carrier list, broker list, activity list from video frame analysis | 357 video frames analyzed |
| 2026-04-01 | Added API-driven automation path from Fiddler recon | Fiddler captures on Windows EC2, 1629 sessions analyzed |

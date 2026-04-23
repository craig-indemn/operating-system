---
ask: "Production launch checklist and deployment overview for JC and the GIC team — what's happening, what to expect, how to monitor"
created: 2026-04-22
workstream: gic-email-intelligence
session: 2026-04-22a
sources:
  - type: google-doc
    ref: "https://docs.google.com/document/d/1Tb07Om95dllD9Fg4BqCWk0ny0b7GTaKPvYU3ndtsxJA"
    name: "JC call Apr 22"
  - type: unisoft-prod
    description: "Connectivity verified — Quote 146242, Task 135239 created and deleted"
  - type: codebase
    description: "Full UAT shakeout with 253 emails processed"
---

# GIC Email Automation — Production Launch Checklist

**Launch date:** Thursday, April 23, 2026 at 12:01 AM ET
**Scope:** New quote submissions only (emails dated April 23 onwards)

---

## What We've Done to Prepare

### Testing
- Processed 253 emails from April 21-22 through the full pipeline in the UAT environment
- Successfully automated quote creation, task assignment, attachment upload, and activity logging for real submissions
- Identified and fixed classification issues (GIC portal notifications were incorrectly being processed — now excluded)
- Tested agency matching against 2,898 production agencies — the system finds agencies by producer code, phone, address, and name
- Verified production Unisoft connectivity — created and deleted a test quote (146242) in production

### Infrastructure
- Production services deployed and ready on Railway (processing, automation, sync) — currently paused
- Created "indemn processed" folder in the quote@gicunderwriters.com inbox — processed emails will be moved here
- LangSmith tracing enabled for full observability of every automation step
- Production Unisoft proxy verified and healthy
- "Review automated submission" task action created in production (ActionId 70)
- IndemnAI user configured as the underwriter contact on all automated quotes

---

## What the Automation Does — Step by Step

When a new email arrives in quote@gicunderwriters.com:

### Step 1: Classification
The system reads the email and determines what type it is. It only acts on **new quote submissions from agents** — everything else (USLI notifications, carrier quotes, internal emails, portal submissions that already have Quote IDs) is left untouched in the inbox.

### Step 2: Data Extraction
For eligible submissions, the system extracts data from attached PDFs — insured name, agency, address, line of business, form of business, coverage details. This is done using OCR and AI to read the actual application documents.

### Step 3: Create Quote ID in Unisoft
The system creates a new Quote in Unisoft with:
- **Line of Business and Sub-LOB** — determined from the application
- **Agency** — matched using a three-tier lookup: producer code first, then multi-field matching (name, phone, address, email)
- **Insured name, address, and business details** — from the extraction
- **Underwriter:** IndemnAI
- **Effective date:** Today, Expiration: +1 year

**If the agency cannot be found**, the system stops and leaves the email in the inbox for manual processing. Nothing falls through the cracks.

**Duplicate check:** Before creating a Quote, the system checks if a Quote already exists for the same insured. If a duplicate is found, it skips creation.

### Step 4: Upload Documents
All PDF attachments from the email are uploaded to Unisoft in the **Documents > Application** folder. The original email is also uploaded to the **General > Email** folder so the team can reply from it.

### Step 5: Create Task
A task is created in the **NEW BIZ** group (or **NEW BIZ Workers Comp** for WC submissions) with:
- **Subject:** `[Auto] {Insured Name} — {LOB} via {Agency Name}`
- **Action:** Review automated submission
- **Due date:** Same day the email was received
- **Assigned to:** The group (not an individual — team picks it up)

### Step 6: Log Activity
An "Application Acknowledgement" activity is logged on the quote. This sends a notification to the agent contact confirming that the submission has been received and providing the Quote ID.

### Step 7: Move Email
The processed email is moved from the Inbox to the **"indemn processed"** subfolder.

---

## What to Look For

### In the Unisoft Task Queue
- Tasks will appear in the **NEW BIZ** group with subjects starting with **[Auto]**
- Each task is linked to a Quote with the full application data and attachments uploaded
- Due date is the same day — by the next day it shows as past due if not reviewed

### In the Quote Inbox
- **Processed emails** will be moved to the "indemn processed" folder
- **Emails that couldn't be processed** (agency not found, unsupported LOB, etc.) will remain in the Inbox — handle these the normal way
- **Non-submission emails** (USLI quotes, carrier responses, internal emails, portal submissions) are not touched — they stay in the Inbox as usual

### Things That Might Need Attention
- If an agency isn't found, the email stays in the inbox. Let Craig know the agency name so the matching can be improved
- If a Quote was created but looks wrong (wrong LOB, wrong agency), let Craig know immediately — it can be corrected and the logic updated
- Portal submissions (HandyPerson, Rental Dwelling, Commercial Auto from GIC's own portal) are NOT processed — they already have Quote IDs

---

## How We're Monitoring

### Real-Time
- **Craig will be available Thursday morning** to monitor the first batch of emails
- **LangSmith** traces capture every step the automation takes — every command, every decision, every API call
- **Railway logs** for service health and error monitoring

### Dashboard
- **gic.indemn.ai** — the monitoring dashboard shows all submissions
  - Filter by "Email type: Agent Submissions" to see only automation-eligible emails
  - Filter by "Automation: Completed / Failed / Pending" to see status
  - Failed automations show in red with the error reason

### If Something Goes Wrong
- The automation can be **paused instantly** without any deployment — one configuration change and it stops
- Emails that were already processed remain in Unisoft — the team can review and correct if needed
- Craig can make logic changes and deploy within minutes

---

## Timeline

| When | What |
|------|------|
| **Tuesday Apr 22 (today)** | JC alerts team to catch up on old inbox items |
| **Wednesday Apr 22 evening** | Craig finalizes all preparation and testing |
| **Thursday Apr 23, 12:01 AM** | Automation goes live — processing only emails from Apr 23 onward |
| **Thursday morning** | All hands monitoring — Craig available for immediate fixes |
| **Thursday midday** | Decision: let it ride or pause for adjustments |
| **Ongoing** | Monitor, tune agency matching, expand to endorsements when ready |

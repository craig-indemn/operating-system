# GIC Email Intelligence

**Prepared for JC · April 2026**

---

## What This Is

We built a system that connects GIC's email inbox (`quote@gicunderwriters.com`) to the Unisoft AMS. When a new application arrives via email, the system reads it, extracts the data, and creates a Quote ID in Unisoft — the same way the web portal does, but automatically.

The system is live in development, running against Unisoft UAT, and processing new emails as they arrive.

---

## How It Works

The pipeline runs continuously and processes every email that arrives in the inbox:

**1. Email Sync**
Emails are pulled from the Outlook inbox every 5 minutes via Microsoft Graph API. Every email, attachment, and thread is captured.

**2. Document Extraction**
PDF attachments (ACORD forms, applications, loss runs) are run through an OCR and extraction service. The system reads every field on the form — insured name, address, line of business, agency, producer code, coverage details.

**3. Classification**
Each email is classified by type: new application, carrier response (USLI quote, decline, pending), portal submission, agent reply, internal GIC communication, etc. This determines what action to take.

**4. Applicant Organization**
Related emails are grouped into a single applicant record. If an agent sends an application and USLI later responds with a quote, those are linked together under one applicant.

**5. Automation**
For new applications (`agent_submission` type), the system automatically creates a Quote ID in Unisoft. This is the step described in detail below.

---

## What the Automation Does in Unisoft

This is the step-by-step process that runs for each new application email. It mirrors the manual workflow of creating a new quote through the Unisoft desktop application.

### Step 1: Determine the Line of Business

The system maps the application's line of business to a Unisoft LOB code:

| Line of Business | Unisoft Code |
|---|---|
| General Liability | CG |
| Commercial Property | CP |
| Workers Compensation | WC |
| Professional Liability | PL |
| Business Auto / Transportation | TR |
| Commercial Umbrella | CU |
| Excess | EX |
| Ocean Marine / Boats & Yachts | OM |
| Inland Marine | IM |
| And others... | |

If the LOB has sub-lines (e.g., General Liability → Artisan Contractor), the system selects the appropriate sub-LOB based on the description of operations from the ACORD form.

### Step 2: Find the Agency

The system looks up the submitting agency in Unisoft using two methods:

1. **Producer code** — If the ACORD form has a producer code, the system looks it up directly by number. This is the most reliable method.
2. **Agency name search** — If no producer code is available, the system searches by agency name from the application or email.

### Step 3: Create the Quote

A new quote record is created in Unisoft with the following fields:

| Field | Where It Comes From |
|---|---|
| **Insured Name** | ACORD form / email classification |
| **Line of Business** | Mapped from application (see table above) |
| **Sub-LOB** | From description of operations |
| **Agent Number** | Looked up by producer code or agency name |
| **Address, City, State, Zip** | From ACORD form |
| **Policy State** | From address (defaults to FL) |
| **Form of Business** | From insured name (LLC, Corp, Individual, etc.) |
| **Business Description** | From ACORD description of operations |
| **Effective Date** | Defaults to current date |
| **Expiration Date** | Defaults to one year from effective |

### Step 4: Upload Attachments

Every PDF attachment from the email is uploaded to the quote record in Unisoft, so the documents are available in the AMS without going back to the inbox.

### Step 5: Log Activity

An activity entry is logged on the quote: "Application received from agent via email automation" (Action ID 6).

---

## How We Access Unisoft

We extracted the complete API specification from the Unisoft system — 910 available operations covering quotes, submissions, activities, agents, carriers, lines of business, and file attachments. This specification had not been previously documented.

We built a proxy service that translates between our system and Unisoft's API. The proxy handles authentication and data format translation automatically. It runs on a dedicated server (AWS EC2) and is accessible only to our pipeline.

The proxy currently connects to the **Unisoft UAT environment** for development and testing.

---

## Results

The system is connected to the inbox, running live, and processing new emails as they arrive. We focused specifically on **new applications from retail agents** — emails where an agent submits a new piece of business and a Quote ID needs to be created in Unisoft.

| | |
|---|---|
| **New applications identified** | 221 |
| **Quotes created in Unisoft** | 144 |
| **Remaining (questions below)** | 77 |

The 77 that didn't automate each have a specific reason. We've investigated every one — they fall into a few categories that we need to discuss.

### Questions on the Remaining 77

These are all based on **UAT data**. The answers may be different in production.

**Agencies not found in UAT (54)**

These agencies appear on the ACORD forms but don't have a matching record in the Unisoft UAT environment. Examples:

- *Mercado Insurance* (producer code 7300) — searched by name and code, no match
- *Ferguson Insurance Inc* (producer code 7634, Neptune Beach FL) — no match
- *Lumina Insurance Inc* — no match
- *Palm Beach Insurance Advisory Group II LLC* (producer code 6886) — no match
- *Kyra Insurance LLC* — no match

**The question:** Do these agencies exist in the production system? If not, should we be creating them in Unisoft as part of the automation when we encounter them?

**Franchise networks not matching (35)**

Estrella, Sebanda, and Univista are franchise networks with many locations. The ACORD form says something like "Estrella Insurance #326" but that specific franchise number doesn't exist in UAT. Examples:

- *Estrella Insurance #326* — no agent with branch 326 in UAT, but 66+ other Estrella entries exist
- *Sebanda Insurance Franchise III* (901 SW 27 Ave, Miami) — 10+ Sebanda entries, can't match to the right one
- *Univista Insurance* via agent code 6942 (Kareninsurance Corp dba Univista) — code not found

**The question:** Do these franchise-specific entries exist in production? If not, is there a standard way to match a franchise branch to its parent agency in Unisoft?

**Producer codes not matching (9)**

Some ACORD forms have producer codes that return no results in UAT. Examples: 7631, 7651, 7661, 6929, 6957.

**The question:** Are these codes valid in the production system? If an agent submits with a code that doesn't exist, should we register it?

---

## Where to See It

The system has a web dashboard where you can see every applicant, their AMS status, and the full processing history.

**URL:** [gic.indemn.ai](https://gic.indemn.ai)

Log in with your Indemn platform credentials. The dashboard has three views:

- **Applicant Queue** — every applicant with their AMS status, email type, line of business. Filter by AMS status (linked, failed, not linked), type, agent, and more.
- **Applicant Detail** — click into any applicant to see the merged data from email and Unisoft, the processing timeline, automation status, and the original email conversation.
- **Insights** — the overall picture: how many are in the AMS, what needs attention and why, email volume, top agents.

---

## What's Next

### Moving to Production

The system is ready to run against production Unisoft. The steps:

1. **Production credentials** — we need access to the production Unisoft environment (same setup, different credentials).
2. **Validation** — we'll run a supervised period where the automation creates quotes and you review them before they're finalized.
3. **Full automation** — once you're confident, the system runs unattended. Failures still surface in the dashboard for manual handling.

### Automating More of the Inbox

The goal is to remove the need for your team to monitor the quote inbox. Everything that comes in should flow into Unisoft automatically. New applications are the first step — here's what else is in the inbox and what we could do with it:

**USLI Carrier Responses (~2,800 emails)**
About 68% of email volume is USLI carrier responses — quotes, declines, and pending notices. These come in when an agent has submitted through USLI's retail web portal. We'd want to discuss how these are handled today: are they already tracked in Unisoft? Are they being entered manually? If there's a gap, we can automate it.

**Portal Submissions and Carrier Linking**
Some applications come through the Unisoft web portal, and carrier responses relate back to existing applicants. We can automatically connect emails to their corresponding records in Unisoft so everything is linked without anyone touching it.

### Deepening the Automation

We can also go deeper on the steps we're already automating:

**Carrier Submissions**
Beyond creating the Quote ID, we can create the carrier submission record in Unisoft — assigning USLI or another carrier, setting dates, and moving the quote further through the workflow automatically.

**Additional Field Mapping**
We can map more data from the ACORD forms into Unisoft — coverage limits, additional insureds, loss history, and other fields that currently require manual entry.

### Renewals Inbox

You've also given us access to your renewals inbox. We can explore what automation is needed there — whether it's a similar pipeline or a different workflow. This would be a separate workstream once we've solidified the quote inbox automation.

---

## Questions for Discussion

1. **Production access** — what do we need to get on the production Unisoft environment?
2. **Agencies and producer codes** — the specific questions are in the Results section above, with examples. The short version: if an agency or producer code doesn't exist in Unisoft, should we create it as part of the automation?
3. **USLI carrier responses** — how does your team handle these today? We want to understand the current workflow before proposing automation.
4. **Roadmap priorities** — of the options in the "What's Next" section, what's most valuable to you?
5. **Production criteria** — what would you want to see or test before we go live?

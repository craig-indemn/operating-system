---
ask: "Deep UX audit from customer perspective — is every view intuitive, accurate, and actionable?"
created: 2026-03-17
workstream: gic-email-intelligence
session: 2026-03-17-a
sources:
  - type: browser-testing
    description: "Systematic review of all 10 submissions via agent-browser + full database dump"
  - type: design-docs
    description: "Original exploration objectives, demo UI design, demo script — grounding in what we promised"
---

# UX Deep Audit — Customer Perspective

## What This System Is Supposed To Do

From our original design docs:

> "Instead of scrolling through hundreds of emails, Maribel sees her pipeline at a glance."

The system should:
1. **Organize emails by submission, not by email** — every interaction about "Rodriguez Grocery" is grouped together
2. **Show the lifecycle** — submission → review → info request → reply → carrier → quote/decline
3. **Extract data automatically** — pull insured name, LOB, premium, limits from emails and PDFs
4. **Tell the user what to do next** — draft follow-ups, flag stale submissions, identify missing info
5. **Prove we understand their workflows** — the demo should make GIC say "yes, that's exactly how we work"

## The Core Problem

**Our sample data doesn't tell any of these stories.** Every submission has exactly 1 email. There is no lifecycle to show, no back-and-forth to follow, no progression through stages. The UI was built for a rich multi-email pipeline, but it's being populated with isolated single-email snapshots.

This makes every view confusing because:
- The "timeline" has 1 entry — there's no time progression
- The "stages" were assigned by AI but there's no visible evidence of WHY
- The "missing info" comes from generic LOB config files, not from analyzing the actual conversation
- The "drafts" sometimes contradict the submission state

---

## Submission-by-Submission Findings

### NEW COLUMN (4 submissions)

#### 1. Florida Georgia Commercial Lines Team
- **What the user sees**: Stage "New", LOB "General Liability", 95d ago
- **What the email actually is**: A USLI application notification from December 2025
- **Problems**:
  - 95 days old and still "New"? That's not new — something is broken or this was never worked
  - The draft is a "Decline Notification" — but the submission is in the "New" column. If it was declined, why is it New?
  - The email is FROM no-reply@usli.com (carrier system) — the submission name is "Florida Georgia Commercial Lines Team" which is the agency, not the insured. What's the actual insured's name?
  - Has a PDF extraction but the data is thin (just carrier, agency name, reference number)
- **Customer question**: "Why is a 95-day-old declined submission in 'New'? Who is the actual insured?"

#### 2. Ojeda A Services LLC
- **What the user sees**: Stage "New", agent "Diana Ponce", 36d ago
- **What the email actually is**: An agent's REPLY to a GIC info request ("Owner has exemption, please exclude...")
- **Problems**:
  - This is an agent REPLYING with information GIC requested. This shouldn't be "New" — it should be something like "Ready for review" or at least "Awaiting Info" → "replied"
  - The draft is ANOTHER info request asking for "Detailed description of operations" — but the agent just provided info. Why are we asking for more?
  - The draft acknowledges receiving the info ("Thank you for your prompt response") then asks for more — is that accurate? Maybe, but without seeing the original info request, the user can't judge
  - 4 attachments including a Notice of Cancellation — important documents not surfaced in the UI
- **Customer question**: "Diana just replied to us. Why does the system want to ask her for MORE info? And why is this still 'New'?"

#### 3. Mercado Insurance
- **What the user sees**: Stage "New", LOB "General Liability", 36d ago
- **What the email actually is**: An agent submission with no subject, body just says "See att", with an HTML attachment
- **Problems**:
  - The draft says "Hi KH" and references "Johnny" — stale data from before we renamed the submission. The draft would be embarrassing to show
  - The attachment is an HTML file (johnnyglapp.html) — the submission is for someone named Johnny but we renamed it to "Mercado Insurance" based on the sender. The actual insured name is unknown
  - The draft sends to MERCADOINSURANCE2@outlook.com — at least the recipient is right
  - 11 missing items listed — every single generic GL field. Not insightful, just a checklist
  - Subject line of draft has an internal MongoDB ObjectId: "Info Request for Johnny (GL Applicant) - Submission 69b854c59b613be3e899a2f5"
- **Customer question**: "Who is this for? Why does the draft reference 'Johnny' and have a database ID in the subject?"

#### 4. Groundhog Tree Services & More
- **What the user sees**: Stage "New", LOB "General Liability", 4d ago
- **What the email actually is**: An agent forwarding a renewal request with a PDF
- **Problems**:
  - This is the BEST submission for demo — recent, clear insured name, renewal PDF, professional draft
  - The draft is well-written and appropriate (info request for renewal)
  - But: 9 missing items are generic GL fields. Are all of those really needed for a RENEWAL? Renewals should have most of this info already from the prior term
  - The completeness ring shows 1/12 — alarming, but misleading since this is a renewal (not a new submission)
  - No extraction from the renewal PDF — the system didn't read the attached PDF
  - The email body is EMPTY (no body_text) — clicking "Read email" shows nothing
- **Customer question**: "This is a renewal — why is the system asking for 9 items that should already be on file? And why can't I see the email content?"

### AWAITING INFO COLUMN (2 submissions)

#### 5. Porro Insurance
- **What the user sees**: Stage "Awaiting Info", agent "Daymara Hernandez", 144d ago
- **What the email actually is**: An agent asking GIC about workers comp contact information
- **Problems**:
  - 144 days old — ancient history
  - "Awaiting Info" implies GIC is waiting for info from the agent. But the email is the AGENT asking GIC for info. The stage is backwards
  - No draft, no extraction — the system has nothing actionable to show
  - Worker's Comp LOB — but this isn't really a submission, it's an inquiry about contact information
  - This probably shouldn't be a "submission" at all — it's a question, not a quote request
- **Customer question**: "Daymara asked US for information 5 months ago. Why is this showing as 'Awaiting Info' from our side? And why is it still here?"

#### 6. Allan Ventura
- **What the user sees**: Stage "Awaiting Info", LOB "Homeowners", 6d ago
- **What the email actually is**: A GIC info request sent to an agent (from Amanda Green via support system)
- **Problems**:
  - This stage actually makes sense — GIC sent an info request and is waiting for the agent's reply
  - But: no draft suggesting a follow-up (this is where a "Follow-up #2 draft ready" would be valuable — design doc says "No response in 5+ days → follow-up draft ready")
  - No extraction — nothing in "What We Know"
  - The email is from "Amanda Green (Support)" through a ticketing system — the UI shows it as a regular email with no special handling
  - Reference number SWPN-033966-00 is in the subject but not extracted
- **Customer question**: "OK, we sent an info request. Has the agent replied yet? Should I follow up? The system doesn't tell me."

### QUOTED COLUMN (2 submissions)

#### 7. ESR Services Solutions LLC
- **What the user sees**: Stage "Quoted", LOB "General Liability", 54d ago
- **What the email actually is**: An internal forward from Joanne Herishko saying "No application attached"
- **Problems**:
  - The email literally says "No application attached" — yet it's classified as "Quoted"
  - The draft is an info request that sends email TO quote@gicunderwriters.com — GIC's own address. That makes no sense
  - "Quoted" stage implies a carrier returned a quote. But the email is about a MISSING application, not a quote
  - The extraction found APPLICATION.PDF and extracted some data — but the human said "no application attached" in the email body
  - Has a PDF extraction with some data, but the submission is fundamentally misclassified
- **Customer question**: "This says 'Quoted' but the email says 'no application attached'. The draft would email ourselves. Something is very wrong."

#### 8. Waterhouse Construction LLC
- **What the user sees**: Stage "Quoted", LOB "General Liability", 39d ago
- **What the email actually is**: A Hiscox quote notification with 5 PDF attachments
- **Problems**:
  - This is the SECOND BEST submission for demo — clear quote from Hiscox with rich data
  - Has 4 PDF extractions (coverage summary, binder, ACORD, quote letter) — the richest data we have
  - The draft is a professional quote forward to dgonzalezinsurance@gmail.com with premium, terms, and coverage details — excellent
  - "Quoted" stage is correct
  - BUT: The draft subject and body still say "WATERHOUSE CONSTRUCTION, LLC" in ALL CAPS — we normalized the submission name but the draft was generated from the original data
  - The agent email dgonzalezinsurance@gmail.com isn't shown in the header because retail_agent_name is None
- **Customer question**: "This one looks good. Who is the agent? Can I see the quote documents?" (Mostly positive)

### ATTENTION COLUMN (2 submissions)

#### 9. Simaval Services LLC
- **What the user sees**: Stage "Attention", reason "declined", agent "Maria Bergolla"
- **What the email actually is**: A USLI decline notification
- **Problems**:
  - This is the THIRD BEST submission — clear decline with a well-written notification draft
  - "Attention" + "declined" makes sense
  - The draft correctly explains the decline reason and offers next steps
  - Agent info is fully populated (Maria Bergolla at Univista Insurance)
  - The only issue: "Commercial Package" LOB but the decline reason mentions ">500 acres" — a user might wonder what business this is
- **Customer question**: "Good — we know it was declined. What kind of business is this? Can we re-market it?" (Mostly positive)

#### 10. Blaze Pilates
- **What the user sees**: Stage "Attention", reason "carrier pending", LOB "Professional Liability"
- **What the email actually is**: Elizabeth Shults (USLI) replying that they can't proceed until all pending items are answered
- **Problems**:
  - "Attention" + "carrier_pending" — the name is a bit confusing. "Carrier pending" could mean "waiting for carrier" or "carrier is pending on something"
  - The draft is actually an INFO REQUEST to jarriola@gicunderwriters.com — that's a GIC INTERNAL address. The system is drafting an email to GIC's own staff, not to the agent
  - The draft says "all items in USLI's original pending memo" but what are those items? The user can't see them
  - No agent info — who submitted this originally?
- **Customer question**: "Why is the system emailing Julissa (our colleague) instead of the agent? What are the pending items?"

---

## Cross-Cutting Issues

### 1. Email Count is Wrong
Every card shows "2 emails" but every submission actually has only 1 email. This is a data integrity bug from sample creation. It implies there's a conversation when there isn't.

### 2. Every Submission Has Only 1 Email
The design was built for multi-email submissions showing lifecycle progression. With 1 email each, the "timeline" is a single entry and there's no story to tell. This is the #1 demo blocker.

### 3. Stages Don't Match Visible Evidence
The user sees a card in "New" or "Quoted" but there's no explanation of why. With more emails, the progression would be visible. With 1 email, it's a mystery.

### 4. Drafts Have Stale/Wrong Data
- Mercado: References "Johnny" and includes a MongoDB ObjectId in the subject
- ESR: Sends email to GIC's own address
- Blaze: Sends email to GIC internal staff
- Florida Georgia: Decline notification but submission is "New"
These drafts would be embarrassing in a demo.

### 5. "Missing Items" Are Generic, Not Intelligent
The completeness ring uses LOB config files with generic required fields. It doesn't analyze the actual conversation to determine what's specifically missing. A renewal showing "9 items missing" when most should be on file from the prior term is misleading.

### 6. No PDF Extractions for Most Submissions
Only 3 of 10 submissions have PDF extractions (Florida Georgia, ESR, Waterhouse). The rest show nothing in "What We Know" except basic email classification data.

### 7. CAUTION Warnings Pollute Email Previews
Every email body starts with "CAUTION: This email originated from outside of the organization..." — we filter it from the preview but it still appears when you expand the email body.

### 8. Empty Email Bodies
Several emails (Groundhog, Mercado) have empty or near-empty body text. Expanding them shows nothing useful.

---

## Which Submissions Are Demo-Worthy?

| Submission | Demo-worthy? | Why |
|-----------|-------------|-----|
| Groundhog Tree Services | BEST | Recent, clear renewal, good draft, but empty email body and 0 extractions |
| Waterhouse Construction | GOOD | Rich quote data, 4 extractions, professional quote forward draft |
| Simaval Services | GOOD | Clear decline story, good notification draft, full agent info |
| Blaze Pilates | MAYBE | Shows attention flagging, but draft goes to wrong recipient |
| Allan Ventura | MAYBE | Correct "awaiting info" stage, but no draft and no data |
| Ojeda A Services | NO | Stage is wrong (agent replied but it's "New"), draft contradicts situation |
| Mercado Insurance | NO | Draft has stale data ("Johnny", MongoDB ID in subject) |
| ESR Services | NO | Stage is wrong, email says "no application" but it's "Quoted", draft emails self |
| Florida Georgia | NO | Decline notification in "New" column, 95d old, insured name unknown |
| Porro Insurance | NO | Not really a submission, 144d old, stage is backwards |

**Only 3 of 10 submissions are presentable. The other 7 would raise more questions than they answer.**

---

## Root Causes

1. **Sample size**: 10 submissions with 1 email each can't demonstrate a multi-email pipeline system
2. **Agent classification quality**: The LLM made errors on edge cases (ESR quoted, Porro awaiting_info, Ojeda new)
3. **Draft generation quality**: Some drafts reference stale data or send to wrong recipients
4. **Missing batch processing**: We only processed 10 emails through the agent. The full 3,165 emails would create multi-email submissions with real lifecycles
5. **Generic completeness**: LOB config files drive "missing" fields, not actual conversation analysis

---

## Recommendations

### Option A: Fix the 10 Sample Submissions
- Correct stages, fix draft data, fix email counts
- Still only 1 email per submission — timeline is empty
- Hides the real problem: the demo needs multi-email submissions

### Option B: Run Full Batch Processing
- Process all 3,165 emails through the agent pipeline
- Creates real multi-email submissions (some quotes have 5-10 emails)
- Shows actual lifecycle progression in timeline
- ~$15-20 LLM cost, 1-2 hours processing time
- But: email bodies need re-fetching from Graph API first (HTML-only emails had empty text)

### Option C: Curate a Smaller Set of Great Submissions
- Pick 5-8 real email threads that tell complete stories
- Manually link them properly, fix stages, generate accurate drafts
- Requires identifying which emails belong together and which threads tell the best story
- Most control over demo quality, but requires manual work

### Option D: Redesign the UI for Single-Email Reality
- If we can't get multi-email data, redesign around what we have
- Remove the "timeline" concept (it's a lie with 1 email)
- Focus on: classification + extraction + draft as the value props
- Board becomes a triage view: "here's what came in, here's what the AI thinks, here's what to do"
- Less impressive but at least honest

### My Recommendation
**Option B (full batch) is the right answer for the actual demo.** The system was designed for multi-email submissions and it needs that data to tell its story. But this requires:
1. Re-fetching email bodies from Graph API (~1-2 hours)
2. Running the agent pipeline on all 3,165 emails (~$15-20, 1-2 hours)
3. Spot-checking results and fixing obvious errors

**For TODAY**, Option C is the practical path — curate 5-6 submissions from real email threads that demonstrate the full lifecycle. Fix the bad drafts. Use only submissions we can be proud of.

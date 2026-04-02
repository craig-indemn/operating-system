# JC Walkthrough: Unisoft Workflow — Source of Truth

> Captured from Craig's review of the JC screen-share video (March 27, 2026).
> Craig walked through the recording again on 2026-04-02 and narrated the exact workflow.
> **This is the source of truth for what GIC does and what we automate.**
> Last updated: 2026-04-02

---

## The Two Entry Points

Every submission enters the system through one of two paths:

### Path A: Web Portal Submission
- Agent submits through GIC's web portal (gicunderwriters.com)
- **A Quote ID is automatically created** by the portal
- Applicant info, agent info, attachments are already in the system
- GIC receives a notification email in the quote inbox
- Work starts at "Quote ID exists" stage

### Path B: Email Submission (no portal)
- Agent sends an email directly to quote@gicunderwriters.com
- Likely includes attachments (ACORD forms, applications, etc.)
- **No Quote ID exists yet** — must be created manually in Unisoft
- This is where automation adds immediate value

---

## The Complete Workflow

### Step 1: Create Quote ID

**Required for Path B only.** Path A already has this.

1. Go to Quotes tab in Unisoft
2. Click "New Quote"
3. Enter the **three required fields**:
   - **Line of Business** (code, e.g., CG)
   - **Sub-line of Business** (code, e.g., AC)
   - **Agency** (code, e.g., 6605)
4. This generates a **Quote ID** — the core tracking identifier

**This is the minimum viable automation.** If we can reliably determine LOB, SubLOB, and Agency from an email, we can create the Quote ID automatically.

### Step 2: Enter Applicant Information

Still part of the "New Quote" process. After the Quote ID is generated, fill in:

- Applicant name (from email/PDF)
- Address, City, State, Zip (from PDF if available)
- Agent contact from the agency (the specific person who submitted)
- **Effective Date: the current date**
- **Expiration Date: one year from effective date (default)**
- Other applicant details as available

If the agent contact doesn't exist in Unisoft, you can add a new agent contact.

**For web portal submissions, all of this is already done automatically.**

### Step 3: Create Submission

Once a Quote ID exists (from either path):

1. Go to the Submissions tab on the quote
2. Add **Broker** (for GIC, always "GIC Underwriters", BrokerId 1)
3. Add **Carrier** (e.g., USLI = CarrierNo 2)
4. Click Save — creates a Submission with a SubmissionNo

### Step 4: Create Activity + Submit to Carrier

1. Create a new Activity on the submission
2. Select action: **"Submit Application to Carrier"** (ActionId 1)
3. **Attachments tab**: Import attachments from the email (ACORD forms, applications, loss runs)
   - For web portal submissions, attachments are already in the system
4. **Email tab**: Draft and send email to the carrier
   - This is how the actual submission to the carrier happens
   - The email is documented within the activity record
5. Save the activity

### Step 5: Delete Email from Inbox

Once the submission is saved with the activity, the team member **deletes the email from Outlook**. This signals to the rest of the team that it's been handled.

---

## When the Carrier Responds

The carrier response (quote, pending, decline) arrives as a new email in the same quote inbox.

### If USLI Sends a Quote Back:

1. **Find the existing submission** in Unisoft (by quote ID or reference number)
2. **Update the submission** with quote information (premium, terms)
3. **Create a new Activity**: forward the quote to the original agent
4. This completes the full lifecycle for that submission

### If More Information is Needed:

1. Update submission status
2. Create activity to relay the request to the agent
3. Wait for agent response (another email in the inbox)

---

## The Effective Date Answer

**CONFIRMED from JC's walkthrough:**
- **Effective Date = the current date** (the date the quote is being created in Unisoft)
- **Expiration Date = one year from the effective date** (default for annual term)
- This is the standard practice — the effective date is when GIC enters the record, not when the agent originally submitted

This applies to quotes created from email submissions. Web portal submissions set their own effective date during the portal flow.

---

## The Phased Automation Strategy

### Phase 1: Quote ID Creation (First Win)

**Goal:** Automatically create a Quote ID for every email in the inbox that doesn't already have one.

**What it does:**
- Reads the email + attachments
- Determines LOB, SubLOB, Agency
- Calls SetQuote to create the record in Unisoft
- Gets back a Quote ID

**Value:** Frees Maribel and the team from the manual data entry of creating quote records. Every email starts on equal footing with web portal submissions.

**What makes this achievable:**
- The three required fields (LOB, SubLOB, Agency) can be determined by the LLM from the email + PDF
- We have the proxy and Python client ready
- We have all the reference data (LOB codes, SubLOB codes, agent list)

**After creating the Quote ID:**
- Optionally send a new email to the inbox that looks like a web portal notification, putting it on even footing with portal submissions
- Or update the existing email record in our system with the Unisoft Quote ID

### Phase 2: End-to-End Vertical for One LOB

**Goal:** For a single LOB that only goes to USLI, automate the full lifecycle.

**The full flow:**
1. Email arrives → create Quote ID (Phase 1)
2. Create Submission with Broker=GIC, Carrier=USLI
3. Create Activity: "Submit Application to Carrier" with attachments
4. When USLI response arrives in inbox → match to existing submission
5. Update submission with quote information
6. Create Activity: forward quote to the original agent

**Why pick a LOB that only uses USLI:**
- Carrier is always USLI (no routing decision needed)
- USLI responses are predictable format (MGL prefix, PDF attachments)
- The response lands in the same inbox we're monitoring
- End-to-end is fully within our data scope

**Complication acknowledged:** The user's earlier assumption that some LOBs only use USLI may not be accurate. The communication channels go through different methodologies depending on the situation. Need to verify from actual email data which LOB→carrier mapping is truly 1:1.

### Phase 3: UI Alignment

**Goal:** The UI should not just show inbox intelligence — it should be a **tracker of automation activity in the AMS**.

**What the UI should show:**
- What has been automated (quote IDs created, submissions filed)
- What's actually happening with our automations
- Historical data from the AMS (if UAT data aligns with real data — unconfirmed)
- Visibility into the automation pipeline: email received → quote created → submission filed → carrier response → agent notified

**Note:** UI work happens in the other worktree (os-outlook). The user has specific changes to make to the PDF extraction and UI alignment there.

---

## Key Business Insights

### The Triage Problem
GIC doesn't have a great system for doing triage as a group. The shared inbox with "delete = done" is their coordination mechanism. Automating the quote ID creation step directly reduces the manual work that's bottlenecking them.

### Web Portal vs Email — Two Starting Points
The web portal handles everything that Step 1 and Step 2 do manually. If we can make email submissions start at the same point as portal submissions (with a Quote ID), the rest of the workflow is the same regardless of entry channel.

### What JC Cares About
If the quote ID creation were automated, it would **free up time they don't have** for manual data entry. The immediate value is in the first step — not the full lifecycle. The full lifecycle is the vision, but the first step is the first win.

### USLI Isn't Always 1:1
The assumption that some LOBs only go to USLI needs verification. Different LOBs may use different carriers or different submission methodologies. The email data suggested USLI dominance, but the actual workflow may be more nuanced.

---

## UAT Environment — Open Question

It's unclear if the UAT environment contains data that aligns with real historical data from the inbox. If it does, we could correlate email data with AMS records. If not, the UAT is only useful for testing our automation against the API.

---

## Changelog

| Date | Update | Source |
|---|---|---|
| 2026-04-02 | Initial creation from Craig's review of JC walkthrough video | Craig narrated the video walkthrough workflow, phased strategy, and business context |

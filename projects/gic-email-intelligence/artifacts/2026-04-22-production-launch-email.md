---
ask: "Email to JC — production launch overview and checklist"
created: 2026-04-22
workstream: gic-email-intelligence
session: 2026-04-22a
---

**To:** jcdp@gicunderwriters.com
**Subject:** Going live tomorrow — here's what to expect

Hey JC,

Everything is ready for tomorrow morning. Here's the overview of what's happening and what your team should expect.

**Launch:** Thursday, April 23 at 12:01 AM ET. Only emails dated April 23 onward will be processed — nothing older is touched.

---

**What I've done to prepare:**

- Production Unisoft connectivity verified — tested quote creation, task assignment, and activity logging
- Created the "indemn processed" folder in the quote inbox — processed emails will be moved there
- IndemnAI user configured as the underwriter contact on all automated quotes
- "Review automated submission" task action created in production
- 2,898 production agencies synced for matching
- Full observability set up so I can see every step the automation takes in real time

---

**What the automation does — step by step:**

1. **Reads incoming email** — only acts on new quote submissions from agents. Everything else (USLI notifications, carrier quotes, internal emails, portal submissions that already have Quote IDs) is left untouched in the inbox.

2. **Extracts data from PDFs** — insured name, agency, address, line of business, form of business, coverage details. Uses OCR and AI to read the actual application documents.

3. **Creates Quote ID in Unisoft** — determines LOB/sub-LOB, matches the agency using producer code + phone + address + name, fills in the applicant details, sets IndemnAI as the underwriter. Runs a duplicate check before creating. If the agency can't be found, it stops and leaves the email in the inbox for manual handling.

4. **Uploads documents** — all PDF attachments go into the Documents > Application folder. The original email goes into General > Email so your team can reply from it.

5. **Creates a task** — assigned to the NEW BIZ group (or NEW BIZ Workers Comp for WC). Subject starts with `[Auto]` followed by insured name, LOB, and agency. Due date is the same day the email was received.

6. **Logs activity** — triggers the Application Acknowledgement activity, which sends a notification to the agent contact with the Quote ID.

7. **Moves the email** — the processed email is moved from the Inbox to the "indemn processed" folder.

---

**What your team should look for:**

- Tasks appearing in the **NEW BIZ** group with `[Auto]` in the subject — each one is linked to a Quote with attachments already uploaded
- **Emails still in the Inbox** that weren't processed = either not a new quote submission, or the agency couldn't be found. Handle these the normal way and let me know the agency name so I can improve the matching
- **Portal submissions** (HandyPerson, Rental Dwelling, Commercial Auto from GIC's portal) are NOT processed — they already have Quote IDs

---

**Monitoring:** I'll be watching everything in real time tomorrow morning and available for immediate adjustments. The automation can be paused instantly if needed — same approach as the chat rollout.

Let me know if you have any questions. Looking forward to it.

Craig

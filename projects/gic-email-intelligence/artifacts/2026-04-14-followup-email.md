---
ask: "Follow-up email to JC and Mike after Apr 13 meeting"
created: 2026-04-14
workstream: gic-email-intelligence
session: 2026-04-13a
sources:
  - type: google-doc
    ref: "https://docs.google.com/document/d/1cV3dRLUZT49dixc7v_j7Fc4ho2QwcUImsUG3XYTqEr0"
    name: "Meeting with Craig Certo - 2026/04/13 14:59 EDT - Notes by Gemini"
---

# Follow-up Email — JC + Mike

**Subject:** Follow-up — Quote Inbox Automation + Next Steps

Hey JC, Mike,

Thanks for the call yesterday — really productive. Wanted to recap what we discussed and lay out next steps so we're all on the same page.

**Where we are:**

We connected to the GIC quotes inbox and built a pipeline that processes every incoming email — classifying it by type, extracting data from ACORD forms and attachments, and grouping related emails into applicant records. For new applications coming in through email, the system automatically creates a Quote ID in Unisoft using the extracted API endpoints, so the email path works the same as the web portal path.

We've been running this against the UAT environment. The main issue we ran into is about 40% of agencies referenced in emails not matching records in Unisoft — JC clarified this is likely because agents use street names rather than legal names, and that searching by phone number and address would be a better fallback than relying on producer codes.

**What we agreed on:**

- **Human-in-the-loop workflow** — when the system creates a Quote ID, it assigns a task to a group in Unisoft (New Biz) so your team picks it up from there.
- **Processed emails move to a subfolder** — once an email is processed, it gets moved out of the main inbox into a subfolder (e.g., "Indemn Processed"). This addresses the audit concern and means the team only sees unprocessed emails in the inbox.
- **Duplicate detection** — the system should check for similar names and addresses before creating a new Quote ID, to avoid duplicates from resubmissions or different agencies.
- **Production rollout** — JC confirmed creating Quote IDs in UAT is fine for testing. Next step is moving to production with the task system in place and the "instant quote" user for tracking.
- **Endorsements are the next priority** — after the quotes inbox is solid, we pivot to endorsements. Higher volume, more rule-based, and Mike will define the list of no-brainer changes to start with (address updates, adding vehicles, etc.). We're pausing USLI-specific development since the new portal launching end of month will change the forms.

**What I'm doing:**

- Updating the agency search to use phone number and address as fallback
- Adding duplicate detection (check for similar name/address before creating a new Quote ID)
- Getting write access to the quotes inbox — I'll be reaching out to Makul on this and will copy you both
- Testing the email-to-subfolder move once I have write access
- Once JC sets up the New Biz group, adding the task creation step so each new Quote ID triggers a task for the team
- Once JC sends production credentials, pointing the system at production and running end-to-end tests

**What I need from you:**

- **JC** — production Unisoft download link + credentials, the "instant quote" user, and the "New Biz" group name when they're ready
- **Mike** — when you get a chance, a rundown of how endorsement submissions work in Unisoft, and the list of high-volume no-brainer endorsement types to start with

Let me know if I'm missing anything.

Craig

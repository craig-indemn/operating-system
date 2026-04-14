---
ask: "Meeting summary and action items from JC/Mike/Craig call Apr 13"
created: 2026-04-14
workstream: gic-email-intelligence
session: 2026-04-13a
sources:
  - type: google-doc
    ref: "https://docs.google.com/document/d/1cV3dRLUZT49dixc7v_j7Fc4ho2QwcUImsUG3XYTqEr0"
    name: "Meeting with Craig Certo - 2026/04/13 14:59 EDT - Notes by Gemini"
---

# Meeting Summary — Apr 13, 2026

**Attendees:** JC (Juan C. Diaz-Padron), Mike Burke, Craig Certo

## Key Decisions

1. **Human-in-the-loop for production** — Quote ID creation triggers a task in Unisoft assigned to a group ("New Biz"). Team picks up from there. No auto-submission to carriers.
2. **UAT is safe** — no risk creating Quote IDs in UAT for testing.
3. **Agency search improvement** — use phone number and address as fallback when agency name doesn't match. Producer codes are often wrong or absent on organic submissions.
4. **Processed emails → subfolder** — move emails out of the main inbox into an "INDM" subfolder after processing. Requires write access.
5. **Endorsements are next priority** — higher volume, more rule-based, faster ROI. Pause USLI development (new portal launching end of month changes forms).
6. **Production access approved** — JC creating "instant quote" user and "New Biz" group in production.
7. **USLI offer-to-agent** — quick win that can be done now even while pausing other USLI work.

## Action Items

| Who | What |
|-----|------|
| **Craig** | Update agency search: phone + address as fallback |
| **Craig** | Get write access to quotes inbox (work with Makul, copy JC) |
| **Craig** | Create INDM subfolder in quotes inbox for processed emails |
| **Craig** | Move quote automation to production with human-in-the-loop task system |
| **Craig** | Connect to endorsements inbox, analyze content and volume |
| **JC** | Send production Unisoft download link + credentials |
| **JC** | Create "instant quote" user in production |
| **JC** | Set up "New Biz" group, email Craig the name |
| **Mike** | Explain the endorsement submission process to Craig |
| **Mike** | Define endorsement automation rules — list of high-volume, no-brainer changes (address updates, adding vehicles, etc.) |

## Strategic Notes

- **Task system is key** — JC wants the team working from Unisoft tasks, not from Outlook or our dashboard. The automation should feed into their existing workflow.
- **Duplicate detection needed** — JC flagged concern about duplicate submissions (same applicant from different agencies, or resubmissions). Unisoft has built-in similar name/address prompts.
- **Endorsements expected to automate faster** — more rule-based, fewer variables than new business quotes.
- **USLI portal changing end of month** — don't invest in USLI-specific development until new forms are stable.

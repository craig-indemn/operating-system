---
ask: "Draft email to JC — meeting setup, progress update, questions"
created: 2026-04-08
workstream: gic-email-intelligence
session: 2026-04-08a
sources:
  - type: codebase
    description: "Pipeline status, automation results, agency verification findings"
---

# Email to JC — Meeting Setup

**Subject:** Unisoft integration update + a few questions

Hey JC,

Quick update — since we last talked about the email ingestion and organization, I've been focused on the Unisoft AMS integration. I pulled the API specification, scraped the data, and studied the screen share you walked me through of the current workflow.

The focus has been on new applications coming in through email — automatically creating a Quote ID in Unisoft and submitting the application details, so the email path works the same as the web portal path. That's up and running in dev now against UAT.

I want to set up a meeting to walk you through what I've got and talk through a few things:

- **UAT vs production** — I'm running against UAT right now. What do we need to get on production?
- **Agencies** — I'm seeing applications come in from agencies that aren't set up in Unisoft. Should I be adding those as part of the automation, or is that handled separately?
- **Producer codes** — same question. Some ACORD forms have producer codes that don't match anything in the system.
- **Roadmap** — I want to talk through next steps for moving this to production, any criteria you want to see met before then, and anything I should be thinking about changing.

Let me know when works.

Craig

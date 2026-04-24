---
ask: "Preserve the Apr 23 Kyle+Craig sync transcript as durable context — this is the cleaner signal of what Kyle actually wants, simpler than his Apr 24 prep doc"
created: 2026-04-24
workstream: customer-system
session: 2026-04-24-roadmap
sources:
  - type: google-doc
    ref: "1bHhSG_Eguwh5KXmdFndhAcfvBE4QEaQ0sAbET671h70"
    name: "Craig | Kyle - Sync - 2026/04/23 15:30 EDT - Notes by Gemini"
---

# Apr 23 Kyle+Craig Sync — Notes

Meeting: Craig Certo + Kyle Geoghan
Date: 2026-04-23 15:30 EDT
Source: Gemini-generated meeting notes in Google Drive

This is the verbal alignment from the day before the Apr 24 sync. The Apr 24 prep doc Kyle later wrote builds on this conversation but over-specifies — this transcript is the cleaner signal.

## Summary

Team updates successful system integrations and aligns on scaling operational development via future customer success automation.

**Integration and Scaling Success:** Production deployment of UNISOT integration achieved stability. Complex workflows are now documented to facilitate future client onboarding and process replication.

**Customer Interaction Model:** Development of a unified customer interaction model utilizes data from meetings and emails to build comprehensive company timelines. This framework informs sales qualification and playbook creation.

**Project Planning and Strategy:** The team established a phased plan to refine data extraction using customer pilots. This focus prioritizes building scalable, playbook-driven activities for future operations.

## Decisions (aligned)

- **Transition to full enterprise contract** — GIC account authorized to transition to full enterprise contract due to successful system integration results.
- **Enable outbound communication tools** — Outbound call and email capabilities approved for addition to the system stack to support upcoming insurance renewals.
- **System-wide data access authorization** — Permission granted to extract data from all employee emails and meetings as the OS's baseline data.
- **Project plan for data extraction** — Project plan to be developed for customer success and sales data extraction, prioritizing a dashboard view of customers approaching the proposal stage.
- **Pilot mock-up review** — Mock-up review of previous day's meeting data is the immediate priority to validate data extraction accuracy and establish a scalable playbook.

## Next steps

- **[Craig]** Document UNISOT: Document the UNISOT solution process for Rudra to replicate future implementations.
- **[Kyle]** Notify Employees: Notify all employees that Admin access grants system ability to pull all emails, meetings, and recordings.
- **[Craig]** Generate Proposal: Generate a proposal draft for the Alliance customer using extracted data and available Google Drive documents.
- **[Kyle]** Build Project: Build a project plan outlining broad processes and customer data collection for executive dashboard views.
- **[Craig]** Ingest Meetings: Ingest meeting data into the system; focus on this week and individually pull Alliance meetings data.
- **[Craig + Kyle]** Review Follow-up: Review extracted data from yesterday's meetings and mock up automated follow-up email alignment for team use.
- **[Kyle + JC]** Contact JC: Touch base with JC to discuss GIC progress and future plans.

## Full details

### UNISOT Integration Update (00:02:23)

Craig reported success with the UNISOT integration, having processed close to 30 emails and smoothed out operations for JC, who is now feeling happy and comfortable. They believe the solution should be stable by Monday, requiring only occasional minor adjustments.

### Documentation and Future Scaling (00:03:19 – 00:04:16)

The work completed is complex, involving email categorization, data entry into UNISOT, activity creation, and agent notifications.

Kyle inquired about documenting the UNISOT integration process to enable Rudra to replicate it for future clients, and Craig confirmed this is feasible. They noted that the setup for new clients is now easier since the initial complex setup is complete, and the long-term goal is to migrate much of the process to the operating system to allow for easier customer onboarding. This current work is viewed as research and development, providing learnings for systemizing future deployments.

### Integration of Communication Pillars (00:05:13)

The discussion turned to integrating web chat, voice, and email communication pillars, with Craig asserting this is theoretically possible now but is a native feature of the developing operating system. They confirmed that outbound calls and emails can be added to the stack, noting that it is not necessarily harder than handling inbound calls. They also acknowledged the necessity of outbound capabilities for upcoming Insura renewals.

### Customer Success System Development (00:06:01 – 00:06:49)

Craig stated they are not overwhelmed and are moving forward with their goal for the operating system to become the foundation for everything, specifically using the customer success system as a foundational project. **Kyle emphasized the need for rapid iteration on the customer success side, viewing it as a low-risk area for testing and averaging out information for the first playbook.** Craig then provided a conceptual overview of the customer success system, which includes input from customer emails and meetings to build an interaction timeline.

### Sales Process and Proposal Development (00:07:59 – 00:09:04)

The conversation continued on the sales process, where Craig described working backward from a proposal, which necessitates understanding the customer and identifying opportunities aligned with available offerings. They outlined entities such as customer interactions (touch points), company details, and internal documents, which all feed into the final proposal, defining this work as the outcome of the sales process. Craig also confirmed that they have the administrative ability to pull all employee emails, meetings, and recordings via the Google Meet and Gmail APIs for data ingestion.

### Defining the Customer Interaction Model (00:11:48 – 00:12:54)

Craig explained that the system uses entities like Email, Meeting, and Document, connected by "associates," to create a "touch point," which is a categorized communication with a customer or an internal team member. This system allows for building a timeline of interactions and hydrating a comprehensive company entity with data on people, operations, volume, opportunities, tech stack, and external relationships. **They confirmed that the extraction of data from meetings will inform the sales team's discovery and qualification questions, defining the initial playbook as a result of these extractions.**

### Project Implementation Plan (00:14:50 – 00:22:26)

The immediate plan is for Craig to go through the Alliance customer data to produce a proposal, which will serve as an example of data extraction and translation into a final deliverable.

**Kyle requested that the next step after Alliance be focusing on a customer earlier in the sales cycle, like the one discussed yesterday, to define the next steps and ensure that information is being extracted from meetings.**

They also discussed creating a project plan with three subsets, including defining the broad process, pulling data for one customer, and reviewing the extraction process for individual cases.

### Focus on Useful and Playbook Activities (00:26:31) — KEY MOMENT

Kyle emphasized the strategy of focusing on small, useful, and playbook-related activities.

**"By looking at yesterday's meeting transcript, we could mock up a follow-up email to see how closely it aligns with what Kyle would have sent, thereby demonstrating immediate utility and scalability for the rest of the team."**

Kyle also stressed the importance of dashboard views and defining stages to enable persistent AI agents to analyze data and trigger next steps, such as sending Slack notifications.

### Scaling and Resource Leverage (00:28:20 – 00:30:10)

Kyle advised Craig to document their work while focusing on the "not urgent and important" construction of the business future. The conversation concluded with an agreement that figuring out how to leverage the team and resources, such as delegating hard product development questions to individuals like Dolly, will become a natural and necessary part of the operating system development. Craig confirmed the production deployment with JC is successful and will remain operational, signaling a key win for the team.

## Key takeaways for today's work

1. **Mock-up follow-up email for yesterday's meetings is the priority.** Kyle said this himself, verbally, Apr 23. The Apr 24 prep doc added schema noise on top of this simple ask.
2. **Playbook is defined as the result of extractions.** The first playbook emerges from what gets extracted from real meetings — not from up-front schema design.
3. **Rapid iteration on customer success as testbed.** Low-risk area, average out real data to build the playbook.
4. **Alliance first (late-stage → proposal). Then earlier-stage meeting (Apr 22).**
5. **Dashboard views + defined stages → persistent AI agents trigger next steps.** The ultimate goal: agents watching entities, firing Slack notifications, etc.
6. **"Not urgent and important"** — constructing business future. Building the OS is the critical but non-urgent work; ingestion, extraction, playbook emergence.

## Contrast: Apr 23 verbal vs Apr 24 written

| Apr 23 (verbal) | Apr 24 (written prep doc) |
|---|---|
| "Mock up a follow-up email from yesterday's meeting transcript" | Part 1: Two hand-extracted JSON blobs as schema target |
| "Playbook emerges from extractions" | Part 2: Canonical field spec with ~20 enums and types |
| "Phased plan: pull data, review extraction, iterate" | Part 3: Three-phase three-week plan with Friday deadlines |

The verbal version is cleaner and more actionable. The written version is Kyle-with-Claude-Code over-engineering. Build from the verbal ask, use the written as signal about what outcomes he wants to see.

---
ask: "How should the board be reorganized to match Maribel's actual workflow — triaged inbox with action queues instead of lifecycle stages?"
created: 2026-03-18
workstream: gic-email-intelligence
session: 2026-03-18-a
sources:
  - type: conversation
    description: "Craig + Claude brainstorming on board layout, action-oriented design, inbox augmentation vision"
---

# Board Redesign — Triaged Inbox with Action Queues

## Context

The current Kanban board has 5 lifecycle columns: New, Awaiting Info, With Carrier, Quoted, Attention. Craig's feedback: "I don't think there's necessarily something wrong with the column approach; I just don't think it's organized in the right way."

The system is an **inbox augmentation tool** — it sits alongside (eventually inside) Outlook and helps Maribel process the quote@ inbox faster. The first objective is automating info requests. The future is full autonomy where the system handles email replies on its own, but the user needs visibility and control during the trust-building phase.

## What Maribel Actually Does

1. Opens quote@ in the morning
2. Scrolls through what came in
3. For each email: respond, forward, file, or ignore
4. She's triaging — deciding what needs her attention vs what can wait

**Our system does the triage for her.** So the primary view should show her what the AI did and what's left for her.

## The Redesign: Action Queues

Instead of lifecycle stages, columns represent **what Maribel needs to do**:

### Column 1: Ready to Send
Drafts are written, reviewed by AI — just needs human approval. These are quick wins. Maribel can blast through these in minutes.

**What lands here:**
- Info requests drafted for new submissions
- Quote forwards drafted for carrier quotes received
- Decline notifications drafted
- Follow-up emails for stale submissions

**Card shows:** Insured name, draft type ("Info Request"), recipient, one-line preview of what's being asked. Approve button right on the card.

### Column 2: Needs Your Review
The AI processed something but it needs a human decision. Maybe the AI isn't confident, the data is ambiguous, or it's a type of email the AI doesn't handle yet.

**What lands here:**
- Agent replies where the AI isn't sure if all info was provided
- Submissions where the retail agent couldn't be identified
- Emails the classifier wasn't confident about
- Anything that needs human judgment before the next step

**Card shows:** Insured name, what happened, what the AI needs from you.

### Column 3: Monitoring
Ball is in someone else's court. No action needed from Maribel, but she can see what's in flight.

**What lands here:**
- Info requests sent, waiting for agent reply
- Submissions with carrier, waiting for quote
- Anything where the next action is on someone else

**Card shows:** Insured name, who we're waiting on, how long it's been.

### Optional Column 4: Done / Archived
Recently completed items. Quotes forwarded, info received, policies bound. Provides a sense of accomplishment and audit trail.

## Dashboard Bar (Top)

Above the columns, a summary bar showing today's numbers:

```
Today: 12 new emails | 8 auto-drafted | 3 need your input | 2 waiting on agents
This week: 47 processed | 38 auto-handled | avg response time: 2.1 hours
```

This gives Maribel (and JC/management) instant visibility into:
- Volume: how much is coming in
- Automation: how much the system handles vs needs human input
- Performance: how fast things are moving

## Card Design

Each card should immediately answer: **"What did the AI do and what do I need to do?"**

```
┌──────────────────────────────────────┐
│ Groundhog Tree Services & More       │
│ General Liability · LevayMack        │
│                                      │
│ AI drafted an info request asking    │
│ for: detailed description of ops,   │
│ loss runs, signed application        │
│                                      │
│ To: agent@levaymack.com   [Review]   │
└──────────────────────────────────────┘
```

The card tells a story: who, what type, what the AI did, what's needed. The [Review] button opens the detail view.

For monitoring cards:
```
┌──────────────────────────────────────┐
│ Allan Ventura                        │
│ Homeowners · Swyfft                  │
│                                      │
│ Info requested 6 days ago            │
│ Waiting on agent response            │
│                                      │
│ ⚠ May need follow-up     [View]     │
└──────────────────────────────────────┘
```

## How This Maps to Current Data

| Current Stage | Current Attention Reason | → New Column |
|---|---|---|
| new + has_draft | — | Ready to Send |
| quoted + has_draft | — | Ready to Send |
| attention + declined + has_draft | — | Ready to Send |
| new + no_draft | — | Needs Your Review |
| attention + carrier_pending | — | Needs Your Review |
| awaiting_info | — | Monitoring |
| with_carrier | — | Monitoring |
| any + stale (5+ days) | stale | Needs Your Review (follow-up needed) |

## Analytics Integration

The dashboard bar is the entry point to analytics. Clicking numbers opens a detailed view:
- Submission volume by day/week/month
- Email type distribution (what kinds of emails are coming in)
- Top agents/agencies by volume
- Average time-to-response by stage
- LOB distribution
- Carrier breakdown (USLI vs Hiscox vs others)
- Automation rate (% handled without human input)

All data already exists from the 3,165 email classifications.

## Relationship to Outlook

This system is designed to eventually be an Outlook plugin or sidebar:
- The "Ready to Send" queue maps to drafts that go into Outlook
- The "Monitoring" queue maps to sent items being tracked
- The analytics give management visibility they can't get from raw Outlook
- The detail view replaces digging through email threads manually

For now it's a standalone web app at a URL. For production, it could be:
- An Outlook Web Add-in (sidebar in Outlook)
- A Teams tab
- A standalone app that deep-links to Outlook for sending

## Implementation Approach

This is a board column mapping change + card content redesign. The backend data model doesn't change — submissions still have stages. The frontend maps stages to action queues:

```typescript
function getActionQueue(submission: Submission): 'ready_to_send' | 'needs_review' | 'monitoring' {
  if (submission.has_draft && submission.draft_status === 'suggested') return 'ready_to_send'
  if (submission.has_draft && submission.draft_status === 'approved') return 'ready_to_send'
  if (submission.stage === 'awaiting_info') return 'monitoring'
  if (submission.stage === 'with_carrier') return 'monitoring'
  // Everything else needs review
  return 'needs_review'
}
```

Cards get richer content: a one-line AI action summary and a primary CTA button.

Dashboard bar: new API endpoint `/api/dashboard` returning daily/weekly counts.

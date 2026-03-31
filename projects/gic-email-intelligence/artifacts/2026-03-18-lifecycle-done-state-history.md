---
ask: "What does 'done' mean for a submission? How do we show lifecycle context in the action queue view? What does the history/resolution view look like?"
created: 2026-03-18
workstream: gic-email-intelligence
session: 2026-03-18-a
sources:
  - type: conversation
    description: "Craig + Claude brainstorming on lifecycle visibility, terminal states, and history view"
---

# Lifecycle, Done State, and History View

## The Problem

The board shows action queues (Ready to Send, Needs Review, Monitoring) but:
1. Submissions never leave the board — there's no "Done" state
2. Old items (50-180 days) sit alongside fresh ones with no distinction
3. The user can't see the lifecycle stage (New, Quoted, Declined) — just the action queue
4. There's no history of resolved submissions or how they were resolved
5. Partially processed data (only 100 of 3,155 emails ingested) means some loops aren't closed that would be if all emails were linked

## Two Layers That Both Matter

**Layer 1: Lifecycle Stage** (what stage is this submission in?)
- New submission arrived
- Info requested from agent
- Carrier is reviewing
- Quote received
- Carrier declined
- **Done** ← NEW terminal state

**Layer 2: Action Queue** (what does Maribel need to do?)
- Ready to Send: draft exists, review and approve
- Needs Review: requires human decision
- Monitoring: waiting on others
- **History**: resolved, no action needed ← NEW

Layer 2 is how the board is organized. Layer 1 provides context WITHIN each queue.

## What "Done" Means

Three triggers for a submission becoming Done:

### 1. Draft Sent
The user approved a draft and copied/opened it in Outlook. The action has been taken. The submission moves to History with resolution = the draft type (info_request_sent, quote_forwarded, decline_notified, followup_sent).

### 2. Manually Closed
Maribel marks it done because she handled it outside the system (phone call, Unisoft, personal email). Resolution = "manually_closed" with optional note.

### 3. Superseded by New Email
When a new email arrives that advances the lifecycle:
- Submission was "Awaiting Info" → agent reply arrives → moves back to "Needs Review" (not Done — new action needed)
- Submission was "Quoted" and draft was sent → if a bind confirmation email arrives → Done (resolution = "bound")

This is automatic through the existing stage detection when all emails are processed.

## Lifecycle Context on Cards

Cards should show the lifecycle stage alongside the action summary:

```
┌──────────────────────────────────────┐
│ Rodriguez Grocery & Deli    ✨ Draft │
│ General Liability · Maria Chen       │
│                                      │
│ 📋 Quoted — USLI returned a quote   │
│ Draft forwards quote to agent        │
│                                      │
│ 3d ago                     [Review]  │
└──────────────────────────────────────┘
```

The lifecycle stage ("Quoted") gives context. The action summary ("Draft forwards quote to agent") tells you what to do. Together they tell the full story at a glance.

Different lifecycle stages appear differently:
- 📋 **New** — "New submission from [agent]"
- ⏳ **Awaiting Info** — "Info requested, waiting on [agent]"
- 🏢 **With Carrier** — "Submitted to [carrier]"
- ✅ **Quoted** — "[Carrier] returned a quote"
- ⚠️ **Attention: Declined** — "[Carrier] declined"
- ⚠️ **Attention: Carrier Pending** — "[Carrier] needs more info"

## The History View

### Where It Lives
Integrated into Analytics as a "Resolved Submissions" section. The Analytics tab becomes the operational intelligence hub:
- Top section: volume charts, type breakdowns (existing)
- Bottom section: resolved submissions table with filters

### What It Shows

A table/list of completed submissions:

| Insured | LOB | Resolved | Resolution | Duration | Agent |
|---------|-----|----------|------------|----------|-------|
| Rodriguez Grocery | GL | Mar 15 | Quote forwarded | 3 days | Maria Chen |
| Acme LLC | Commercial Package | Mar 12 | Declined, agent notified | 1 day | Diana Ponce |
| Smith Construction | GL | Mar 10 | Info request sent | — | John Rivera |

**Filters:** By resolution type, LOB, agent, date range
**Metrics derived from history:**
- Average time to resolution
- Resolution breakdown (% quoted, % declined, % info requested)
- Agent performance (response times, completion rates)
- LOB patterns (which LOBs have the longest cycles)

### Resolution Types
- `quote_forwarded` — Quote received and forwarded to agent
- `decline_notified` — Carrier declined, agent notified
- `info_request_sent` — Missing info requested from agent
- `followup_sent` — Follow-up email sent
- `manually_closed` — Closed by user (with optional note)
- `bound` — Policy bound (future — when we can detect bind confirmations)

## Implementation

### Database
Add to submission document:
```javascript
{
  // Existing fields...
  resolved_at: ISODate | null,          // When marked done
  resolution: String | null,             // "quote_forwarded", "decline_notified", etc.
  resolution_note: String | null,        // Optional user note for manual close
}
```

### Backend
- New endpoint: `POST /api/submissions/{id}/resolve` — marks done with resolution type
- Modify dashboard/board: exclude resolved submissions from action queues
- New endpoint: `GET /api/submissions/history` — resolved submissions with filters
- Add resolution metrics to analytics endpoint

### Frontend
- Add "Mark as Done" to card actions and detail view (after draft is sent)
- Auto-prompt "Mark as Done?" after copying/opening draft in Outlook
- Add lifecycle stage badge to card content
- Add History section to Analytics tab
- Add resolution metrics to Analytics dashboard

### Workflow
1. Email arrives → processed → appears in action queue
2. User reviews draft → approves → copies to Outlook
3. System prompts: "Draft copied. Mark this submission as done?"
4. User confirms → submission moves to History with resolution type
5. History view shows the completed submission with its full lifecycle

## Connection to Full Batch Processing

Many of the "why is this still here" items will resolve themselves once all 3,155 emails are processed. Emails that close loops (agent replies, carrier quotes) will be linked to existing submissions, updating their stages automatically. The remaining truly unresolved items are the ones that need the "Done" mechanism.

## First-Time Onboarding

When GIC first uses the system, there will be a backlog of old submissions. The onboarding flow should:
1. Show a banner: "We found X historical submissions. Review and archive any that have been handled."
2. Provide a bulk "Archive all older than 30 days" option
3. Let them selectively keep items they want to track

This cleans the board on first use so they start fresh with only active work.

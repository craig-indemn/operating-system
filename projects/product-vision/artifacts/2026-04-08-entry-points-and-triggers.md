---
ask: "How do external events enter the OS and how are actors triggered? What's the complete set?"
created: 2026-04-08
workstream: product-vision
session: 2026-04-08-a
sources:
  - type: conversation
    description: "Craig and Claude mapping the complete set of entry points and trigger types"
  - type: artifact
    description: "2026-04-08-kernel-vs-domain.md, 2026-04-08-primitives-resolved.md"
---

# Entry Points and Actor Triggers

## Two Distinct Concepts

There are two things to distinguish:
1. **How external events enter the OS** — the doors into the building
2. **How actors are triggered** — what activates an actor once events are in the system

These are different layers. Entry points are infrastructure. Triggers are the actor model.

## How External Events Enter the OS

The outside world connects to the OS through entry points. Each creates or updates an entity, and then the kernel takes over (watches match, messages flow, actors process).

| Entry Point | What Happens | Example |
|-------------|-------------|---------|
| **Channel** (web chat, voice, SMS) | Interaction entity created, channel stays open as I/O | Consumer opens EventGuard chat widget, phone call comes in |
| **Webhook** (inbound HTTP POST) | Entity created or updated | Slack event, Stripe payment callback, Google Calendar notification |
| **API call** (structured request) | Entity created or updated | Partner system creates an Application via API |
| **Polling** (scheduled fetch) | Entity created | `indemn email fetch-new` pulls from Graph API, creates Email entities |
| **CLI command** (human or actor) | Entity created or updated directly | `indemn submission create --insured "Acme"` |
| **Form submission** (web) | Entity created | Consumer fills out a web form → Application entity |

These are all infrastructure — different doors into the same building. Once the entity exists or changes, the kernel's message system takes over.

## How Actors Are Triggered

Once events are in the system (as entity changes), actors activate through three trigger types:

| Trigger | When | Example |
|---------|------|---------|
| **Message** | A watch on the actor's role matches an entity change | Classifier activates when Email:created. Underwriter sees Assessment:needs_review=true. |
| **Schedule** | A cron expression fires | Stale checker runs hourly. Email sync runs every minute. Weekly summary runs Mondays. |
| **Direct invocation** | Someone calls the actor explicitly via CLI or API | `indemn associate invoke "Classifier" --email EMAIL-001` for testing, debugging, one-offs. |

That's the complete set. Every actor activation is one of these three.

## Channels Are Entry Points, Not Trigger Types

Channels (web chat, voice, SMS) feel like they should be separate trigger types. But they're actually entry points that create entities, and the actor trigger is still a message.

**Voice call comes in:**
1. Voice infrastructure (LiveKit/Twilio) accepts the call
2. Interaction entity created (type: voice, status: active)
3. Associate's watch matches Interaction:created WHERE type=voice
4. Associate is triggered by the **message** — and uses the voice channel as I/O for the duration

**Web chat opens:**
1. WebSocket connection established
2. Interaction entity created (type: chat, status: active)
3. Associate's watch matches Interaction:created WHERE type=chat
4. Associate is triggered by the **message** — and uses the WebSocket as I/O

The channel is how the external party communicates. The trigger is the entity change. The associate doesn't "listen on a WebSocket" — it receives a message that an Interaction was created, and the Interaction entity has a reference to the open channel for I/O.

**This keeps the actor model clean.** Actors don't need to know about WebSockets, SIP, or Twilio. They know about entities and CLI commands. The channel infrastructure creates entities and provides I/O. The actor reads and writes entities. The channel translates between entity state and the external protocol.

## Every External Case Collapses Into the Same Pattern

| What Happens Externally | Entry Point | Entity Effect | Actor Trigger |
|------------------------|-------------|---------------|---------------|
| Consumer opens chat | Channel (WebSocket) | Interaction:created | Message (watch matches) |
| Customer calls phone | Channel (voice) | Interaction:created | Message (watch matches) |
| Agent sends SMS | Channel (Twilio) | Interaction:created | Message (watch matches) |
| Slack sends event | Webhook | entity created/updated | Message (watch matches) |
| Stripe payment completes | Webhook | Payment:status→completed | Message (watch matches) |
| Calendar event approaching | Webhook or polling | entity created/updated | Message (watch matches) |
| Partner submits application | API call | Application:created | Message (watch matches) |
| New email in Outlook | Polling (scheduled) | Email:created | Message (watch matches) |
| Human creates submission | CLI command | Submission:created | Message (watch matches) |
| User clicks "approve" in UI | API call | Draft:status→approved | Message (watch matches) |
| File uploaded | API call | Document:created | Message (watch matches) |
| Another actor invokes this one | Direct invocation or entity change | varies | Direct invocation or message |
| Cron fires | Schedule | (actor runs its skill) | Schedule |

Everything funnels through: **something creates/changes an entity → watches match → actors process.** The only exceptions are schedule (time-initiated, no entity change starts it) and direct invocation (explicit call, no watch involved).

## The Complete Flow

```
External World                    OS Kernel                         Actors
─────────────                    ─────────                         ──────
Web chat        ─┐
Voice call       │               ┌──────────┐
SMS              ├─ Entry ──────>│  Entity   │──> Message ──> Actor processes
Webhook          │   Points      │  Created/ │    (watch     (executes CLI,
API call         │  (infra)      │  Changed  │    matches)    changes entities)
Polling          │               └──────────┘        │
CLI command     ─┘                    │              │
Form submission ─┘                    │              ▼
                                      └──────── More entity changes
                                                 (system churns)
                                                      │
                              Schedule trigger ────────┘
                              (cron fires, actor runs)
```

## Scheduling in the OS

Scheduled tasks are associates with schedule triggers. Managed via CLI:

```bash
# Create a scheduled associate
indemn associate create --name "Email Sync" --trigger "schedule:*/1 * * * *" --skills email-fetching --mode deterministic
indemn associate create --name "Stale Checker" --trigger "schedule:0 * * * *" --skills stale-detection --mode deterministic

# Shorthand for simple scheduled commands
indemn schedule "indemn email fetch-new" --every "1m"

# Manage schedules
indemn associate list --trigger-type schedule
indemn associate pause "Email Sync"
indemn associate resume "Email Sync"
indemn associate history "Email Sync"  # last runs, success/failure
```

Under the hood, the OS scheduler activates these associates at their configured intervals. The associate runs its skill (executes CLI commands). Entity changes flow through the messaging system normally. Same actor model, time-based trigger instead of message-based.

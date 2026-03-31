---
ask: "What are the objectives of our email exploration, and what do we need to learn before building the demo?"
created: 2026-03-13
workstream: gic-email-intelligence
session: 2026-03-13-a
sources:
  - type: microsoft-graph
    description: "Manual exploration of quote@gicunderwriters.com inbox — folder structure, email samples, sender analysis"
  - type: conversation
    description: "Strategic discussion about what to build and how exploration informs the demo"
---

# Exploration Objectives

## Purpose

Extract and analyze all emails from quote@gicunderwriters.com to build a comprehensive understanding of GIC Underwriters' quoting operation. This understanding becomes the data-driven foundation for an intelligent system that organizes their workflows and provides automation.

## What We Need to Learn

### 1. Complete Taxonomy of Email Types
Exhaustive categorization of every type of email that flows through this mailbox. The demo system needs to recognize and handle every type — if we miss one, it breaks.

**Initial types identified (from manual sampling of ~30 emails):**
1. USLI quote notifications (automated, from no-reply@usli.com)
2. GIC internal system notifications (from noreply@gicunderwriters.com, Unisoft)
3. Info requests sent by GIC to retail agents
4. Info request replies from retail agents
5. Phone tickets (CSR-logged phone call summaries)
6. Direct quote submissions from retail agents
7. Bind requests
8. Carrier communications (USLI pending files, status updates)
9. Internal routing (GIC staff forwarding items)
10. Urgent follow-ups (agents chasing responses)
11. Hiscox quote confirmations
12. Daily report packages (from Unisoft)

**This list is incomplete.** 30 emails out of 3,153 is a 1% sample. The full extraction will reveal the real taxonomy.

### 2. Quote Lifecycles — How Quotes Move Through Stages
Link emails together into complete quote journeys. A single quote may generate 5-10 emails across its lifecycle. We need to trace:
- Submission → Review → Info Request → Reply → Carrier Submission → Quote/Decline → Bind/No-Bind
- What reference numbers tie things together (143xxx from Unisoft, USLI quote IDs, policy numbers)
- How many emails per quote lifecycle on average
- Which stages every quote passes through vs. optional stages

### 3. Cycle Times and Bottleneck Data
For each stage transition, how long does it take?
- Submission to first action by GIC
- Info request sent to reply received
- How many rounds of back-and-forth before info is complete
- Total lifecycle duration by business line
- Where things stall and for how long

This is what makes the demo compelling: "You have 15 quotes waiting for info for 72+ hours."

### 4. Information Requirements by Business Line
**What's required** for each type of quote — the complete picture of what a roofing quote needs, what a trucking quote needs, what pest control needs, etc. Two dimensions:
- **Full requirements**: Everything needed to process a quote for each business line
- **Common gaps**: What people typically fail to provide (a subset of requirements, useful for pre-asking)

Sources: successful submissions show what was provided; info request emails show what was missing; the combination reveals the full picture.

### 5. Actor Network
Who participates in this system and how:
- **Retail agencies**: Which ones, how much volume, which business lines
- **GIC staff**: Who handles what (underwriters, CSRs, specific people like Mari Messina, Juan Carlos)
- **Carriers**: USLI, Hiscox, Stoner — what's the distribution
- **Business lines**: Roofing, pest control, trucking, handyperson, restaurants, etc. — volume per line

## How This Informs the Demo

| Exploration Output | Demo Feature It Enables |
|-------------------|------------------------|
| Email taxonomy | Auto-categorization of every incoming email |
| Quote lifecycles | Pipeline/Kanban view grouping emails into quote records |
| Cycle times | Bottleneck alerts, SLA warnings, aging indicators |
| Information requirements | Smart checklists per business line, completeness scoring |
| Common gaps | Pre-ask automation ("roofing quotes usually need X, you didn't include it") |
| Actor network | Filtered views by agent, carrier, business line |

## What We're NOT Doing in Exploration

- Not building the demo yet
- Not designing the production agent
- Not making automation decisions (the team with insurance experience does that)
- Not modifying GIC's inbox or sending any emails

## Data We Need to Capture Per Email

For the extraction pipeline, each email record should include:
- **Metadata**: id, subject, from, to, cc, date, folder, hasAttachments, attachment names
- **Content**: full body text (stripped of signatures/disclaimers where possible)
- **Threading**: conversationId (Graph API provides this — links emails in the same thread)
- **References**: any quote/policy/reference numbers found in subject or body
- **Classification**: email type (from our taxonomy — added during clustering/classification step)

## Connection to Broader System

This exploration covers the email channel only. The eventual system connects to:
- **RingCentral phone** (project: ringcentral-integration) — same quotes discussed over phone
- **GIC's internal systems** (Unisoft) — the source of truth for quote state
- **Carrier portals** (USLI Retail Web, Hiscox NOW) — where quotes originate

The data layer should be designed to accommodate all channels, not just email.

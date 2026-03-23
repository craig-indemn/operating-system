---
ask: "Prompt for Claude.ai to generate the email intelligence workflow diagram for the showcase page"
created: 2026-03-23
workstream: content-system
session: 2026-03-23-a
sources:
  - type: codebase
    description: "GIC Email Intelligence implementation — 5-step pipeline, submission lifecycle, board UI"
---

# Email Intelligence Workflow Diagram — Prompt

Create a workflow diagram for Indemn's Email Intelligence system — a product showcase page on blog.indemn.ai showing how an AI-powered intelligence layer transforms a broker's email inbox into an organized, managed submission pipeline.

**What this is:** Wholesale brokers and MGAs receive 100+ emails per day in their submission inbox. Quote requests mixed with follow-ups mixed with carrier responses mixed with declines mixed with unrelated noise. Submissions get lost. Info requests go out late. Follow-ups are forgotten. Quotes sit buried in threads. Indemn's Email Intelligence reads every email as it arrives, classifies it, links it to the right submission, tracks the submission through its lifecycle, extracts data from PDF attachments, identifies what information is missing, and drafts professional replies — info requests, quote forwards, follow-ups, decline notifications. The underwriter sees a clean board with three action queues: Ready to Send, Needs Review, and Monitoring.

**The workflow — step by step:**

1. **Emails arrive** — Submissions come into the broker's inbox from multiple sources: retail agents submitting new business, carriers sending quotes or declines, agents replying with requested information, internal team correspondence. The diagram should show an email inbox icon at the top with arrows indicating volume (100+ emails/day). Emphasize that the system connects to the existing inbox (Gmail, Outlook, Microsoft 365) — no migration, no forwarding rules.

2. **Classify** — The AI reads each email and determines: What type is this? (new submission, agent reply, carrier quote, carrier decline, info request, follow-up, general correspondence). It also extracts: the named insured (who is this about?), the line of business (GL, WC, PL, Auto, etc.), and any reference numbers. Show this as the first processing step with outputs: email type, named insured, LOB, reference numbers.

3. **Link** — The system matches the email to an existing submission or creates a new one. Matching uses a priority cascade: reference number match (most reliable) → submission number match → fuzzy name match (normalized, filtered by LOB and date range) → create new submission. Show this as a matching/routing step with the cascade logic. The key insight: emails about the same submission arrive days apart with different subjects and sometimes different senders. The system links them all together.

4. **Stage** — Based on the most recent email type, the system determines where this submission is in its lifecycle. Show a state diagram or stage progression:
   - **New** — initial submission received
   - **Awaiting Info** — info request sent, waiting for agent reply
   - **With Carrier** — submitted to carrier, awaiting response
   - **Quoted** — carrier quote received
   - **Attention** — needs human attention (declined, stale, agent urgency)
   The stage drives what action is needed and where the submission appears on the board.

5. **Extract** — For emails with PDF attachments (ACORD forms, carrier quotes, loss runs, applications), a vision model reads the documents and pulls structured data: named insured, carrier name, premium, coverage limits, effective date, agent information, reference numbers. Show this as a document processing step with example outputs. Emphasize: no templates, no form mapping — the AI reads the document the way a human would.

6. **Gap Analysis** — For each line of business, the system knows exactly what information is required (insured name, address, entity type, revenue, loss history, coverage limits, effective date, etc.). It compares what's been extracted against what's needed and identifies specific gaps. Show this as a completeness check with a visual like a checklist (4 of 8 items present, 4 missing). This is LOB-aware — a GL submission needs different fields than a WC or Auto submission.

7. **Draft** — Based on the submission state and gap analysis, the system generates a professional email draft. Four types:
   - **Info Request** — "To move forward with quoting, I need: [specific missing items]"
   - **Quote Forward** — "Great news — [premium, limits, carrier details]"
   - **Follow-Up** — "Following up on my request from [date] regarding [submission]"
   - **Decline Notification** — "Unfortunately, the carrier has declined due to [reason]"
   Show the four draft types as outputs. Emphasize: drafts go to a review queue, not directly to the recipient. Human approves before anything is sent.

8. **Board / Action Queues** — The underwriter sees everything organized into three queues:
   - **Ready to Send** (green) — submissions with a draft ready to review and send
   - **Needs Review** (amber) — new submissions, quoted submissions, or attention items
   - **Monitoring** (gray) — awaiting response from agent or carrier, no action needed
   Show this as the final output — a clean, organized view replacing the chaotic inbox. Each submission card shows: insured name, LOB, stage, time since last activity.

**What to emphasize visually:**

- **Steps 2-7 are the intelligence layer.** This is what Indemn automates — the reading, classifying, linking, extracting, analyzing, and drafting that a human would spend hours doing manually. Visual grouping similar to "Automated by Indemn" in previous diagrams.

- **The inbox → board transformation** is the key story. Start with a chaotic inbox (top) and end with an organized board (bottom). The diagram should feel like order emerging from chaos.

- **The submission lifecycle** (step 4) is important. Show the stage transitions clearly — this isn't one-shot processing, it's ongoing management. A submission might go through 5-10 emails over days or weeks, and the system tracks the whole journey.

- **The gap analysis** (step 6) should be visually distinct — it's the system's intelligence about what's actually needed, not just what's present. Show a checklist or completeness indicator.

- **The four draft types** (step 7) should be visible as distinct outputs — each serves a different purpose in the submission lifecycle.

- **Human approval** — show clearly that drafts go to a review queue, not directly out. The underwriter reviews, optionally edits, and sends. Nothing leaves without approval.

- **A stats comparison** at the bottom: "Manual: Hours of triage per day, submissions lost in threads, follow-ups forgotten" vs "With Indemn: Every email classified in seconds, every submission tracked, every reply drafted"

**Brand guidelines:**
- **Color palette**: Iris (primary purple), Lilac (lighter purple), Eggplant (dark purple). Match previous diagrams.
- **Font**: Barlow
- **Style**: Clean, professional, premium. Match the Document Retrieval, Quote & Bind, and Conversational Intake diagram styles.
- **Do NOT include dark mode CSS** — the blog is always light mode.

**Context on who sees this:**
- Primary audience: MGA operations managers, wholesale broker principals, underwriting team leads. These are insurance professionals who understand submissions, LOBs, ACORD forms, and carrier workflows. Use industry terminology confidently.
- Secondary audience: Organic visitors to blog.indemn.ai. Also serves as a customer deliverable (generic, not customer-specific).
- The board UI concept should be immediately recognizable to anyone who manages a submission inbox today.

**What this diagram is NOT:**
- Not a technical architecture diagram (no APIs, databases, or LLM providers).
- Not specific to any one customer or carrier.
- Not showing the system as a simple email filter — it's an intelligence layer that understands insurance submissions.

**Reference:** Match the visual style of the previous diagrams:
- `/Users/home/Repositories/content-system/sites/indemn-blog/public/images/products/document-retrieval-workflow.svg`
- `/Users/home/Repositories/content-system/sites/indemn-blog/public/images/products/quote-bind-workflow.svg`
- `/Users/home/Repositories/content-system/sites/indemn-blog/public/images/products/conversational-intake-workflow.svg`

Same visual language: rounded rectangles, purple automation zone, converging inputs at top, stats comparison at bottom, Barlow font, no dark mode CSS.

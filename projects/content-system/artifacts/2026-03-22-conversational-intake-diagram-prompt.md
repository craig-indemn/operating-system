---
ask: "Prompt for Claude.ai to generate the conversational intake workflow diagram for the showcase page"
created: 2026-03-22
workstream: content-system
session: 2026-03-22-a
sources:
  - type: codebase
    description: "Copilot dashboard, bot-service handoff mechanism, middleware socket service, point-of-sale widget"
  - type: meeting
    description: "Craig + Ian sales team call — product showcase prioritization"
---

# Conversational Intake Workflow Diagram — Prompt

Create a workflow diagram for Indemn's Conversational Intake — a product showcase page on blog.indemn.ai showing how an intelligent associate replaces forms and phone trees to handle every inbound inquiry, capture information, answer questions, and route to humans when needed.

**What this is:** Businesses lose prospects every day. Visitors land on a website at 8 PM and see a static form. They call during the lunch rush and get voicemail. They email and wait days for a response. Indemn's Conversational Intake puts an intelligent associate — the "Welcome Mat" — on every channel. It greets visitors, answers questions using the business's own knowledge base (via RAG), collects information through natural conversation instead of forms, qualifies inquiries, and routes to the right person with full context. CSRs monitor everything in real time from a dashboard and can jump into any conversation instantly. The associate works 24/7 — after hours, weekends, peak volume, overflow.

**The workflow — step by step:**

1. **Visitor arrives** — A potential customer or prospect reaches out through the website chat widget or calls the phone agent. Both channels are the "Welcome Mat" — the first point of contact. The diagram should show both web chat and phone converging into the associate.

2. **Associate engages** — The AI associate greets the visitor and begins a natural conversation. Unlike a static form, it adapts based on responses — asking follow-up questions, skipping irrelevant fields, explaining things when asked. It's conversational, not interrogative.

3. **Knowledge-powered answers** — The visitor asks questions about the business ("Do you handle commercial auto in Texas?", "What's your claims process?", "Are you open on weekends?"). The associate answers intelligently using RAG — pulling from the business's scraped website, uploaded documents, and custom knowledge bases. This happens naturally within the conversation, not as a separate "FAQ" mode. Show this as a knowledge retrieval step with a callout showing the data sources: website content, uploaded documents, custom knowledge bases.

4. **Information collection** — As the conversation progresses, the associate captures structured data through natural dialogue — name, contact info, what they need, relevant details. This is the form replacement: instead of 15 fields on a page, the information emerges from conversation. Show a visual of fields being populated: name, email, phone, inquiry type, details, etc.

5. **Qualification & routing decision** — Based on what's been collected, the associate determines the next step. This is a branching point:
   - **Handled autonomously** — the associate resolved the inquiry (answered questions, provided information, no human needed). Visitor leaves satisfied.
   - **Route to human (live)** — the inquiry needs human attention and someone is available. Triggers handoff.
   - **Route to human (offline)** — it's after hours or no agents available. Associate captures everything, schedules follow-up, notifies staff.

6. **Human handoff (when needed)** — This is a key capability to visualize:
   - The associate sets a handoff flag on the conversation
   - The conversation appears at the TOP of the CSR's worklist in the Copilot Dashboard with a visual alert
   - CSR sees the full transcript and all collected data
   - CSR clicks to join — customer sees "[Agent name] has joined this conversation"
   - System tracks time-to-connect (from handoff request to CSR joining)
   - Show this as a dual view: the conversation flowing from the associate to the CSR dashboard

7. **Notifications** — Staff get alerted through their preferred channels. Show multiple notification paths:
   - Copilot Dashboard (real-time, primary)
   - Slack
   - Microsoft Teams
   - Email
   - Text/SMS
   - The notification includes: who the visitor is, what they need, urgency level, collected information summary

8. **Analytics & tracking** — Every interaction generates data:
   - Intake volume (conversations per day/week)
   - Resolution rate (handled autonomously vs. handed off)
   - Response time and time-to-connect
   - Conversion tracking (inquiry → qualified lead → customer)
   - Knowledge gap identification (questions the associate couldn't answer)
   Show this as a side annotation or footer element — not a main flow step, but an always-present layer

**What to emphasize visually:**

- **The associate is the center.** Steps 2-5 form the core automation zone — this is what the associate handles autonomously. Visual grouping similar to the "Automated by Indemn" zone in previous diagrams.

- **The dual nature of the Welcome Mat** — web chat AND phone at the top, converging. The associate handles both identically.

- **Knowledge retrieval** should be called out prominently. The fact that the associate KNOWS the business is a key differentiator. Show the data sources feeding into the associate: website scrape, documents, custom KBs.

- **The handoff flow should show both perspectives** — the conversation view (what the customer sees) and the dashboard view (what the CSR sees). This could be a split panel or two parallel paths that converge when the CSR joins.

- **Notifications fan out** — show multiple channels radiating from a single notification event. Slack, Teams, email, text, dashboard — all from one trigger.

- **The "offline" path is important.** After-hours handling isn't a limitation — it's a feature. The associate captures everything and ensures follow-up happens. Show this as a complete path, not an error state.

- **Form replacement callout** — somewhere in the diagram, a visual comparison: static form (15 fields, high abandonment) vs. conversational intake (natural dialogue, higher completion). Could be a small annotation or comparison box.

**Brand guidelines:**
- **Color palette**: Iris (primary purple), Lilac (lighter purple), Eggplant (dark purple). Same palette as previous diagrams.
- **Font**: Barlow
- **Style**: Match the Document Retrieval and Quote & Bind diagram styles — rounded rectangles, purple automation zone, dashed borders for optional/human zones, converging channel icons at top.
- **Do NOT include dark mode CSS** — the blog is always light mode. Previous diagrams had `@media(prefers-color-scheme:dark)` blocks that caused rendering issues. Omit entirely.

**Context on who sees this:**
- Primary audience: Business owners and operations managers evaluating Indemn. These may be insurance professionals but the framing is general enough for any business with inbound inquiries.
- Secondary audience: Organic visitors to blog.indemn.ai.
- Use accessible language — this page is broader than the MGA-focused Quote & Bind page. "Associate" not "agent" or "chatbot". "Knowledge base" not "RAG". "Dashboard" not "copilot".

**What this diagram is NOT:**
- Not a technical architecture diagram showing WebSocket connections and MongoDB.
- Not limited to insurance — the workflow applies to any business.
- Not showing the associate as a simple chatbot — it's an intelligent system with knowledge retrieval, qualification logic, and seamless human handoff.

**Reference:** Match the visual style of:
- `/Users/home/Repositories/content-system/sites/indemn-blog/public/images/products/document-retrieval-workflow.svg`
- `/Users/home/Repositories/content-system/sites/indemn-blog/public/images/products/quote-bind-workflow.svg`

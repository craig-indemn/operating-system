---
ask: "Prompt for Claude.ai to generate the document retrieval workflow diagram for the showcase page"
created: 2026-03-20
workstream: content-system
session: 2026-03-20-b
sources:
  - type: meeting
    description: "Craig + Ian sales team call — document retrieval workflow scoping"
---

# Document Retrieval Workflow Diagram — Prompt

Create a workflow diagram for Indemn's Document Retrieval automation — a product showcase page on blog.indemn.ai showing how an insurance agency automates document requests end-to-end.

**What this is:** An insurance agency receives requests for documents — certificates of insurance, ID cards, policy forms, beneficiary forms — via email, phone, or web chat. Today, staff manually read each request, figure out what's needed, log into carrier portals, retrieve or generate the document, draft a reply, and send it. This takes 15-30 minutes per request. Indemn automates the entire workflow. The agency can optionally keep a human in the loop at the approval step, but full end-to-end automation is the default.

**The workflow — step by step:**

1. **Request arrives** — A customer or third party sends a document request. This could come through email (most common), phone call, or web chat. The diagram should show all three channels converging into a single intake point.

2. **Intake associate extracts and analyzes** — An AI associate reads the request, determines what type of document is being asked for (COI, ID card, policy form, etc.), and extracts all relevant information (requester name, policy number, business name, what they need, etc.).

3. **Validation: completeness check** — The associate checks whether the request has all the information needed to fulfill it. If information is missing, it drafts a reply asking for the missing details and routes it for review. If complete, it proceeds. This is a branching point in the diagram — show the "missing info" path as a loop back (draft reply asking for more → wait for response → re-enter the flow).

4. **Validation: identity and compliance verification** — The associate verifies the requester's identity. This is a compliance requirement — impersonation is a serious concern in insurance, especially for elderly clients. State-specific rules apply. The associate checks the requester against known customer data to verify they are who they say they are and have the right to access the requested document.

5. **Pull customer data from AMS** — Once validated, the associate pulls the customer's full information from the agency's Agency Management System (AMS/CRM/BMS). This is an integration point — the associate connects to whatever system the agency uses.

6. **Retrieve document from carrier** — This is where it gets interesting. Depending on the carrier: (a) if the carrier integrates with the AMS, the document is pulled directly, or (b) if not, Indemn's web operator logs into the carrier's portal and navigates the system to retrieve or generate the document. This can involve complex multi-step workflows (10+ minutes of navigation in some cases) and carrier-specific MFA challenges. The diagram should show both paths — direct integration and web operator.

7. **Draft reply with document attached** — The associate composes a professional email reply with the retrieved document attached. Something like "Thank you for your request. Please find your certificate of insurance attached."

8. **Human approval (optional)** — This step is optional — agencies can choose full automation or human-in-the-loop. If enabled: an alert appears in the staff member's inbox (via Outlook add-in or email inbox integration) saying something like "You just got a COI request. I've already completed it for you. Read through this email and hit send when ready." The human reviews the email and document, and approves with one click. If human approval is not enabled, the email sends automatically.

9. **Delivered** — The document is sent to the requester. Done.

**What to emphasize visually:**
- **Steps 2-7 are the automated zone.** This is where all the manual work used to happen and where Indemn's automation lives. These steps should be visually grouped or highlighted to make it obvious that this is what we're replacing. Today, a human does all of this manually. With Indemn, it's handled automatically.
- **Step 8 (human approval) should be visually distinct as optional.** Show it as a toggle or optional branch — not a mandatory step. Some agencies want it, some don't. The point is they have the choice.
- **The three intake channels (email, phone, chat) converging** into one workflow should be prominent at the top. The message: it doesn't matter how the request comes in, the same automation handles it.
- **Step 6 (carrier retrieval) should show the two paths** — direct AMS integration and web operator — as both are impressive capabilities.
- **The "missing info" loop at step 3** should be clearly visible as a branch that rejoins the main flow.

**Brand guidelines:**
- **Color palette**: Iris (primary purple), Lilac (lighter purple), Eggplant (dark purple). Use these as the primary colors.
- **Font**: Barlow
- **Style**: Clean, modern, professional. This is for insurance agency owners — not developers. It should feel trustworthy and premium, not techy or startup-y.
- **Indemn brand**: The automated steps should feel like Indemn's domain — use brand colors to distinguish "what Indemn handles" from "what the human does."

**Context on who sees this:**
- Primary audience: Insurance agency owners and principals evaluating Indemn during or after a sales conversation. These are people who manage staff handling document requests all day. They may not be technical — Ian from sales noted one prospect's website "looks like it's from 1990."
- Secondary audience: Organic visitors to blog.indemn.ai exploring Indemn's capabilities.
- The diagram needs to be immediately understandable to a non-technical insurance professional. No jargon like "web operator" — use language like "automated carrier portal access" or "connects to your carrier's system." No "associate" — from the customer's perspective, use language like "AI assistant" or "intelligent automation" or just describe what happens.

**What this diagram is NOT:**
- It's not a technical architecture diagram. It's a customer-facing visualization of a workflow.
- It's not abstract or conceptual. Each step is concrete and specific.
- It's not generic automation. It's insurance-specific — carriers, AMS, compliance, document types are all insurance concepts.

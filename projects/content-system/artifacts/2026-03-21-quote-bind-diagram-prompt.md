---
ask: "Prompt for Claude.ai to generate the quote & bind workflow diagram for the showcase page"
created: 2026-03-21
workstream: content-system
session: 2026-03-21-a
sources:
  - type: meeting
    description: "Craig + Ian sales team call — product showcase prioritization"
  - type: internal
    description: "Series A materials — EventGuard story, associate suite, customer proof points"
---

# Quote & Bind Workflow Diagram — Prompt

Create a workflow diagram for Indemn's Quote & Bind automation — a product showcase page on blog.indemn.ai showing how an MGA or broker can sell insurance products end-to-end through AI agents, from first customer conversation to bound policy and payment.

**What this is:** An MGA, program administrator, or wholesale broker has a product to sell — event insurance, specialty commercial, personal lines, anything they have binding authority for. Today, they rely on web forms (90% drop-off), limited office hours, and manual quoting that takes days. Indemn stands up a complete digital distribution channel: an AI agent that understands the product, the underwriting guidelines, and the compliance requirements. Customers can engage through web chat, phone, email, or text. The agent handles the full lifecycle — from first conversation through quoting, binding, payment collection, and policy issuance. Fully autonomous for straightforward risks, with human-in-the-loop for anything that needs judgment.

**The workflow — step by step:**

1. **Customer initiates contact** — A potential policyholder reaches out through any channel: web chat on a product page, phone call, email, or text message. The diagram should show all four channels converging into a single intake point. Emphasize that Indemn can spin up dedicated branded landing pages per distribution partner (e.g., a venue page for event insurance, a retailer page for specialty coverage) — each with its own agent.

2. **Agent engages and gathers information** — The AI agent greets the customer and begins a conversational intake. It asks qualifying questions specific to the product (event type, date, location, guest count for event insurance; business type, revenue, employee count for commercial). As information is collected, a parameter panel shows fields being populated in real time — like a form being filled by the conversation. The agent understands the product deeply and can answer questions about coverage, exclusions, and pricing.

3. **Eligibility check** — The agent checks the collected information against the program's underwriting guidelines and appetite. Is this risk eligible? Does it fall within the parameters the MGA has defined? This is a branching point:
   - **Eligible**: proceeds to quoting
   - **Out of appetite**: agent explains why and may suggest alternatives or refer to another channel
   - **Borderline / needs review**: routes to human underwriter for judgment (human-in-the-loop branch)
   Show the "needs review" path as a branch to a human review step that can either approve (re-enters the flow at quoting) or decline.

4. **Quote generation** — The agent generates a quote based on the collected information and the program's rating tables. Coverage options are presented to the customer — they can see different tiers, add endorsements, adjust limits. The quote includes premium, deductibles, coverage details.

5. **Customer selects coverage** — The customer reviews options, asks questions, and selects their coverage. The agent handles objections, explains coverage differences, and helps them make a decision. This is conversational, not a static form — the agent can adapt based on what the customer cares about.

6. **Binding** — Once the customer confirms their selection, the agent initiates the binding process. This includes compliance checks: is binding authority valid for this product and state? Are all required fields complete? Are any regulatory disclosures needed? The policy is bound according to the program's rules.

7. **Payment collection** — Premium is collected. The agent handles payment processing — credit card, ACH, or installment plans depending on what the program supports. Payment is confirmed.

8. **Policy issuance** — The bound policy documents are generated and delivered to the customer via their preferred channel — email, text, or download. Includes the policy declarations page, certificate if applicable, and any required disclosures.

9. **Confirmation and follow-up** — The customer receives confirmation. The agent can schedule follow-ups, set renewal reminders, or hand off to a service agent for ongoing support.

**What to emphasize visually:**

- **Steps 2-8 are the automated zone.** This is what Indemn handles — the entire sales and binding process. Visually group these as "Powered by Indemn" or "Automated by Indemn" with a distinct boundary.

- **The four intake channels (web chat, phone, email, text) converging** should be prominent at the top. Add a note or visual element showing "Infinite Landing Pages" — the concept that each distribution partner gets their own branded page with its own agent.

- **The eligibility check (step 3) is the key branching point.** Show three paths clearly: eligible (continues), out of appetite (exits with explanation), needs review (human-in-the-loop branch that can approve back into the flow or decline). The human-in-the-loop should be visually distinct as "when needed" — not every transaction requires it.

- **The human-in-the-loop branch** should be styled as optional/contextual — similar to the Document Retrieval diagram's optional zone. Label it something like "Complex Risks" or "Human Judgment" to make it clear this isn't a bottleneck, it's a safety net.

- **System integration callout** — somewhere in the diagram, show that the quoting engine, binding rules, and payment processing can connect to the MGA's existing systems (AMS, rating engine, carrier portal, payment processor) OR operate as a standalone Indemn-hosted system. This could be a side panel or annotation near the quoting/binding steps.

- **A stats comparison** similar to the Document Retrieval diagram: show the before/after. Something like "Traditional: Days to quote, 10% web form conversion" vs. "With Indemn: Minutes to bind, 10x conversion, 24/7"

**Brand guidelines:**
- **Color palette**: Iris (primary purple), Lilac (lighter purple), Eggplant (dark purple). Use these as the primary colors.
- **Font**: Barlow
- **Style**: Clean, modern, professional. This is for insurance executives — MGAs, program administrators. Premium and trustworthy, not startup-y.
- **Match the Document Retrieval diagram style** — this should look like it belongs in the same product family. Same visual language: rounded rectangles for steps, purple palette for the automation zone, dashed border for optional/human-in-the-loop zones, converging channel icons at top, stats comparison at bottom.

**Context on who sees this:**
- Primary audience: MGA principals and program administrators evaluating Indemn. These are insurance executives who understand underwriting, binding authority, and distribution challenges. They ARE technical in insurance terms — use proper industry language (binding, eligibility, appetite, NTU, E&S, admitted).
- Secondary audience: Organic visitors to blog.indemn.ai exploring Indemn's capabilities.
- Unlike the Document Retrieval diagram (aimed at agency owners who may not be technical), this audience knows insurance deeply. Use industry terminology confidently — it builds credibility.

**What this diagram is NOT:**
- It's not a technical architecture diagram showing APIs and databases.
- It's not generic automation — every step is insurance-specific (eligibility, binding authority, compliance, policy issuance).
- It's not limited to one product — the diagram should feel like it applies to any product an MGA might sell.

**Reference:** The Document Retrieval workflow diagram at `/Users/home/Repositories/content-system/sites/indemn-blog/public/images/products/document-retrieval-workflow.svg` — match this visual style for brand consistency across the product showcase pages.

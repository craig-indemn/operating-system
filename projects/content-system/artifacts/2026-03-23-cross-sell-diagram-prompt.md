---
ask: "Prompt for Claude.ai to generate the cross-sell workflow diagram for the showcase page"
created: 2026-03-23
workstream: content-system
session: 2026-03-23-c
sources:
  - type: meeting
    description: "Craig + Ian sales team call — Darren Rankin cross-sell use case"
  - type: internal
    description: "Series A materials — Retention Engine, cross-sell identification"
---

# Cross-Sell Workflow Diagram — Prompt

Create a workflow diagram for Indemn's Cross-Sell capability — a product showcase page on blog.indemn.ai showing how an AI associate identifies cross-sell opportunities during live customer interactions and naturally offers additional coverage.

**What this is:** Insurance agencies handle hundreds of customer interactions every week — service calls, endorsement requests, claims questions, policy changes. Each interaction is a window into the customer's needs. But agents are focused on handling the request, not selling. They don't have time to pull up the full coverage profile, identify gaps, and make a natural offer — all while keeping the customer happy. Indemn's cross-sell associate works alongside every interaction. It knows the customer's full coverage profile, recognizes when there's a gap, and naturally transitions the conversation to offer additional protection. Not a hard sell. A genuine recommendation based on what the customer actually needs.

**The workflow — step by step:**

1. **Customer initiates contact** — A customer reaches out through any channel (chat, phone, email) for a routine reason: a billing question, an endorsement, a claim, a policy change. The diagram should show the customer connecting to the associate for a primary reason — this is NOT a sales call. Show web chat and phone converging.

2. **Associate handles the primary request** — The associate addresses whatever the customer called about. This is the core service interaction. The customer's immediate need is handled first — always. Show this as the primary workflow step. The associate is competent at service, not just sales.

3. **Coverage profile analysis (background)** — While handling the request, the associate simultaneously pulls the customer's full coverage profile from the AMS/CRM. It sees every policy they have: auto, home, life, umbrella, flood, etc. It also sees what they DON'T have. Show this as a background intelligence step running in parallel with the service interaction — a side panel or annotation showing the profile being analyzed.

4. **Gap identification** — The associate identifies coverage gaps: customer has auto and home but no umbrella liability. Or has home but no flood insurance (and they're in a flood zone). Or has no life insurance and has dependents. Show this as a decision point: gaps found → opportunity exists. If no meaningful gaps → interaction ends normally after service.

5. **Natural transition** — The associate transitions the conversation naturally. Not "Would you like to buy something?" but "By the way, I noticed you don't have umbrella liability coverage. With your home and auto policies, an umbrella would give you an extra $1M in protection for about $200/year. Would you like me to put together a quote?" Show this as the key moment — the bridge from service to cross-sell. It should feel natural, not forced.

6. **Product presentation** — If the customer is interested, the associate presents the product: what it covers, why it matters for their specific situation, pricing/quote. This is personalized — not a generic pitch. The associate knows their home value, their auto limits, their family situation. Show coverage details and a quote.

7. **Close or schedule** — Three outcomes:
   - **Customer says yes** → proceed to quote/bind (connects to Quote & Bind workflow)
   - **Customer is interested but not now** → schedule follow-up, note the opportunity in the system
   - **Customer declines** → no pressure, the primary service request was already handled, customer leaves satisfied
   Show these three paths. Emphasize: the interaction is already a success because the primary request was handled. The cross-sell is a bonus, not the goal.

8. **Opportunity tracking** — Every identified gap is logged, whether or not the customer converted. This feeds the book analysis: which products have the most gaps across the book, which customers are most likely to convert, what's the total revenue opportunity. Show this as a data/analytics output.

**What to emphasize visually:**

- **The primary service interaction comes first.** The cross-sell only happens AFTER the customer's need is addressed. Visually, the service step should be prominent and complete before the cross-sell branch appears.

- **The background profile analysis** running in parallel with service. This is the intelligence — the associate knows the customer's full picture while handling their request. Show it as a side process, not a sequential step.

- **The natural transition** is the centerpiece moment. This is where the diagram should have the most visual emphasis — the bridge from service to cross-sell.

- **The three outcomes** should all feel positive. Even "decline" is fine — the customer got good service. There's no failure state.

- **The opportunity tracking** at the bottom shows this creates data value even when customers don't convert immediately.

- **"Every interaction is an opportunity"** — this could be an annotation or callout somewhere in the diagram.

**Brand guidelines:**
- **Color palette**: Iris, Lilac, Eggplant. Match previous diagrams.
- **Font**: Barlow
- **Style**: Match previous diagrams. No dark mode CSS.

**Context on who sees this:**
- Primary audience: Agency owners and principals. People who manage teams that handle customer interactions daily. They know their customers are underinsured — they just can't act on it at scale.
- The tone should be "protecting customers" not "selling more product." This is about genuine coverage gaps, not revenue extraction.

**Reference:** Match visual style of previous diagrams in the same product family.

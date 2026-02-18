---
ask: "Create a 1-page PDF pitch slide for Kyle to use in Series A investor conversations — encapsulates the message of who Indemn is and why investors should care"
created: 2026-02-17
workstream: series-a
session: 2026-02-17-b
sources:
  - type: mongodb
    description: "tiledesk database — platform stats (agents, organizations, messages, conversations) from session 2026-02-17-a"
  - type: github
    description: "git history from indemn-observability, evaluations, web_operators repos — build timelines from session 2026-02-17-a"
  - type: codebase
    description: "indemn-observability/tools/pitch-slide/generate.tsx — react-pdf generator built this session"
---

# Pitch Slide v1: Frontier Agentic AI for Insurance

**PDF:** [Indemn_Series_A_Pitch_Slide.pdf](Indemn_Series_A_Pitch_Slide.pdf)
**Generator:** `indemn-observability/tools/pitch-slide/generate.tsx`
**Run command:** `cd indemn-observability && NODE_PATH=frontend/node_modules npx tsx tools/pitch-slide/generate.tsx`

## What This Is

A 1-page branded PDF using Indemn's react-pdf system (Barlow font, iris/eggplant/lilac brand colors). Designed as a supplemental slide for Kyle to use in investor conversations. Not a standalone document — a conversation piece.

## The Message (Narrative Arc)

1. **We're a production conversational AI platform for insurance** — quoting, customer service, sales, underwriting support. 55 active agents, 65 organizations, 2M+ messages, 143K conversations.
2. **What sets us apart** — our agents don't stop at conversation:
   - *Agents That Operate Software* — AI inside legacy platforms like Applied Epic, completing manual workflows. Self-learning.
   - *AI That Evaluates AI* — autonomous test generation and evaluation. Quality scales with platform, not headcount.
   - *Knows Why, Not Just What* — conversation intelligence that identifies factors predicting success/failure, not just dashboards.
3. **We build at extraordinary speed** — 4 engineers, 3 production systems, 8 weeks. New AI capabilities in production within days.
4. **Customer proof** — Union General (weeks to minutes), GIC (2,600+ conversations/month), INSURICA (18-96x faster).
5. **The market** — $140B+ insurance distribution built on manual processes. Same workflows everywhere. What works for one works for thousands.

## How We Got Here (Iteration History)

This session started by trying to format the data story from session 2026-02-17-a into a deliverable. The progression:

1. **First attempt** — metrics dashboard layout with platform numbers. Craig rejected: "WE ARE ENCAPSULATING THE MESSAGE." The data isn't the point; the story is.
2. **Second attempt** — led with impact cards (Always-On, Employees Unleashed, Bottlenecks Eliminated). Craig rejected: "WHAT ABOUT IMPACT? WHY DOES IT MATTER?" These benefits are generic — any automation company claims them.
3. **Third attempt** — flipped the hierarchy to lead with capabilities. Craig flagged: the core business (conversational AI platform) was missing entirely. Also: impact cards used academic language ("Causal Conversation Intelligence"), and the differentiators needed to be punchier.
4. **Final version** — establishes the platform first (thesis + stats), then shows what sets Indemn apart (three capabilities in plain language), velocity bar (4/3/8/Days), customer proof, market opportunity. Impact section cut — thesis already covers it.

## Key Decisions

- **Lead with what makes Indemn special, not generic benefits** — "Always-On Operations" is what any chatbot vendor says. "Agents That Operate Software" is what nobody else can say.
- **Establish the core business before differentiating** — without the platform foundation, Indemn looks like a research lab, not a company with customers.
- **Cut jargon** — "Causal Conversation Intelligence" became "Knows Why, Not Just What." "Statistical lift analysis" and "precursor intelligence" removed.
- **The impact IS the story, woven throughout** — not a separate section. The thesis says "end-to-end automation of how insurance businesses run." The capabilities show how. The customer results prove it.
- **Velocity bar is the strongest visual** — 4 | 3 | 8 | Days tells the team story without reading a paragraph.

## Technical Notes

- react-pdf Barlow font has broken fi/fl ligatures — fixed with ZWNJ character insertion via `t()` helper function
- Unicode arrows don't render in Barlow — use text alternatives
- Generator lives in `indemn-observability/tools/pitch-slide/` alongside existing report generators
- Uses same font/logo assets as other tools (`tools/applied-epic-guide/assets/`)

## Next Steps

- Get Kyle's reaction — does this format work? Does the message land?
- Iterate on content based on Kyle's feedback
- Consider whether this becomes a template for multiple supplemental slides (one per topic)
- The $140B+ market figure is unsourced — need to verify or cite before investor use

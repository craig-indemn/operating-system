# Series A

Building the data and analytics angle for Indemn's Series A fundraising. Consolidating existing materials, identifying gaps, and producing investor-ready artifacts that demonstrate traction, market position, and product-market fit through data.

## Status
Last session (2026-02-17-b): Built a 1-page branded PDF pitch slide — "Frontier Agentic AI for Insurance." Craig approved v1.

**What was done:**
- Built a react-pdf generator at `indemn-observability/tools/pitch-slide/generate.tsx`
- Iterated through 4 versions to nail the message and format
- Fixed Barlow font fi/fl ligature rendering (ZWNJ character insertion)
- Final slide establishes: core platform (conversational AI for insurance, 55 agents, 65 orgs, 2M+ messages) then differentiates (agents that operate software, AI that evaluates AI, knows why not just what), velocity bar (4/3/8/Days), customer proof, $140B+ market
- PDF and artifact saved to project

**Key learnings from this session:**
- Generic benefits (24/7, freed employees) don't differentiate — lead with what makes Indemn SPECIAL
- Must establish core business (conversational AI platform in production) before showing differentiators
- Cut jargon for Kyle/investors: "Causal Conversation Intelligence" became "Knows Why, Not Just What"
- Velocity bar (4 Engineers / 3 Production Systems / 8 Weeks / Days) is the strongest visual element
- Impact should be woven into the narrative, not a separate section

**Important context from Craig (carried forward):**
- Do NOT trust financial numbers from session 2026-02-16-b — Cam/Kyle have the correct revenue data
- Craig is the de facto CTO; Kyle asked him to provide analytics/data to supplement the pitch
- Kyle and Cam are NOT technical — results terms, not architecture
- Exclude Indemn internal org (~1,700 conversations/month) from customer metrics
- All customers can be named in investor materials

**Next steps:**
1. Get Kyle's reaction to the pitch slide PDF — does this format work? Does the message land?
2. Iterate on content based on Kyle's feedback
3. Verify the $140B+ market figure — currently unsourced, needs citation before investor use
4. Consider additional supplemental slides (customer deep-dives, market sizing)

## External Resources
| Resource | Type | Link |
|----------|------|------|
| Cam's Take - Series A Foundation | Google Doc | [link](https://docs.google.com/document/d/1iUCc6A5nb2-ls7UxY6XG86Q2-eyB5-XTqlQJN0dAEoM) |
| Cam's Take 2-7-26 (v2) | Google Doc | [link](https://docs.google.com/document/d/147fAzz_c1LEeXk1a1kVvubTeCb-5gVvouiIGAYu2H6k) |
| Investor Update - Feb 2026 DRAFT v2 | Google Doc | [link](https://docs.google.com/document/d/1xDxDL3IkpXUurNMzcHezlmRam-mBbsiqJSzsTevRHK8) |
| Series A Project Plan | Google Doc | [link](https://docs.google.com/document/d/1Qem3XtjqJvXutjnU1Y7nKIprC8iy5UpC6qaOsG8wetU) |
| Deal Model Framework | Google Doc | [link](https://docs.google.com/document/d/1jU3Hj1owLSynA-MWsl61i_7HeiLlIHxhtvCYE1Iy9j4) |
| Customer Stories Foundation | Google Doc | [link](https://docs.google.com/document/d/10tOenyPHlJg-8MWF7FAYSa-6p817Slj6f4IILvi8Y8s) |
| JM Story - The Experiment That Worked | Google Doc | [link](https://docs.google.com/document/d/1r5FhJzHuqpCeVeCmL8Ze97GeqIvbztNkg9d3_zOt8DU) |
| Investor Outreach Tracker | Google Sheet | [link](https://docs.google.com/spreadsheets/d/1xfbt0wHracviDMlkQIze8HzEscXiIMbz36ddUv5XFKc) |
| Revenue Model | Google Sheet | [link](https://docs.google.com/spreadsheets/d/1DcPO96-DLSGURQ8LOIwqK44VtV2wq8Zh6WJCXfr7Hes) |
| Series A Compendium - Master Reference | Google Doc | [link](https://docs.google.com/document/d/1C87-xouN784tZ35tBNVVIpn9RbJg6Op6VPxB-hmwTgg) |
| Four Outcomes Framework | Google Doc | [link](https://docs.google.com/document/d/1BDEDgVE3mWmfXZdBBd0Gx4rqkK9g76-pktSpXtQGOwA) |
| Revenue Defense Summary | Google Doc | [link](https://docs.google.com/document/d/1qJpHiSoNiB12dDLKv34gjjIrJKpJ6yCLahpPkSKEAjk) |
| Customer Proof Points by Outcome | Google Doc | [link](https://docs.google.com/document/d/1Je7JCyPvomrJKs63orPfqepLgay14PFwl5K5MOKNabA) |
| Series A 2026 folder | Google Drive | [link](https://drive.google.com/drive/folders/1wGpARY1fhf_g5SS7a6vYDxJ8RAkbuq0b) |
| Operations folder (numbered docs 1-13) | Google Drive | [link](https://drive.google.com/drive/folders/1I9I8KP99U8eDWjBtqVEP7rEatR004rM1) |
| Context Files folder | Google Drive | [link](https://drive.google.com/drive/folders/1A5K7thVAJJpBB7qoXN_brYRT97z3UCh0) |
| Meetings database | Neon Postgres | 3,141 meetings, 14,612 extractions, 3,240 signals |
| Stripe | Stripe CLI | Revenue and subscription data |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-02-16 | [google-drive-inventory](artifacts/2026-02-16-google-drive-inventory.md) | What Google Drive files and docs can we access? |
| 2026-02-16 | [series-a-comprehensive-analysis](artifacts/2026-02-16-series-a-comprehensive-analysis.md) | Comprehensively read all Series A materials — understand strategy, real numbers, and gaps where engineering/data can strengthen the raise |
| 2026-02-16 | [engineering-angle-session-handoff](artifacts/2026-02-16-engineering-angle-session-handoff.md) | Session handoff: engineering angle, what was built (web operators, eval system, observatory), where to pick up next |
| 2026-02-17 | [data-story-draft-v1](artifacts/2026-02-17-data-story-draft-v1.md) | First draft of data story (too long, kept as reference for raw content) |
| 2026-02-17 | [data-story-draft-v2](artifacts/2026-02-17-data-story-draft-v2.md) | Distilled version (good content, still wrong format) |
| 2026-02-17 | [engineering-slide](artifacts/2026-02-17-engineering-slide.md) | Slide iterations v1-v2 (good direction, format still off) |
| 2026-02-17 | [engineering-slide-v2](artifacts/2026-02-17-engineering-slide-v2.md) | Cleanest version — professional but Craig says format is wrong for a real pitch |
| 2026-02-17 | [data-exploration-and-story-direction](artifacts/2026-02-17-data-exploration-and-story-direction.md) | Session handoff from 2026-02-17-a — all MongoDB data, git timelines, story direction |
| 2026-02-17 | [pitch-slide-v1](artifacts/2026-02-17-pitch-slide-v1.md) | 1-page branded PDF pitch slide — "Frontier Agentic AI for Insurance" |
| 2026-02-17 | [Indemn_Series_A_Pitch_Slide.pdf](artifacts/Indemn_Series_A_Pitch_Slide.pdf) | The PDF deliverable |

## Decisions
- 2026-02-16: Building a data/analytics angle for the Series A — not just narrative docs but data-backed evidence of traction and PMF
- 2026-02-16: The CTO angle is about telling the technical story (frontier agentic AI, web operators, observatory data, team velocity) — NOT auditing or critiquing Cam's fundraising strategy
- 2026-02-16: Approach must be iterative and conversational with Craig — discover what data tells the best story together, don't make sweeping claims
- 2026-02-17: Don't trust numbers from previous session's analysis as ground truth — treat all financial data as unverified unless confirmed by Kyle/Cam
- 2026-02-17: The data story serves the pitch by showing what the engineering systems produce (Observatory outputs, eval results, build velocity) — the systems ARE the evidence, not just a data source
- 2026-02-17: Exclude Indemn internal org (~1,700 conversations/month) from customer metrics — those are demos/beta agents
- 2026-02-17: Format for investor deliverables is branded PDF using react-pdf (not markdown docs or slide outlines)
- 2026-02-17: Lead with differentiators (frontier AI capabilities), not generic automation benefits
- 2026-02-17: Always establish the core platform (conversational AI for insurance, in production) before showing what sets Indemn apart

## Open Questions
- Does Kyle like the PDF format? Does the message land for him?
- The $140B+ market figure is unsourced — needs verification or citation before investor use
- Should Stripe revenue data be woven in, or is that Cam/Kyle's domain entirely?
- Platform totals (2M messages, 143K conversations) include all-time data back to Aug 2023 — how much is production vs. test?
- Should there be additional supplemental slides? (customer deep-dives, market sizing, technical architecture)
- Observatory "outcome_group" classifications — Craig flagged "success" as a poor label
- What do web operator production runs look like? Any completed runs with measurable results yet?

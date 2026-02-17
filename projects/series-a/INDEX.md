# Series A

Building the data and analytics angle for Indemn's Series A fundraising. Consolidating existing materials, identifying gaps, and producing investor-ready artifacts that demonstrate traction, market position, and product-market fit through data.

## Status
Last session (2026-02-17-a): Pulled real production data from MongoDB and git history. Produced a first draft of the data story artifact ("The Engineering Advantage") for Craig to share with Kyle.

**What was done:**
- Explored the full tiledesk MongoDB database — inventoried all collections and document counts
- Mapped organizations and projects to customer names with conversation volumes
- Pulled Observatory data: 7,695 conversations analyzed across 55 active agents, with outcome tracking, precursor lift analysis, intent classification, sentiment, daily snapshots
- Got monthly conversation trends per customer (last 7 months)
- Pulled git history for all three systems to verify build timelines (Observatory: Dec 22 first commit, Evaluations: Jan 20, Web Operators: Feb 12 — 5 days old)
- Drafted v1 of the data story combining platform scale, build velocity, and system capabilities

**Important context from Craig:**
- Do NOT trust the financial numbers from previous session's analysis — Cam/Kyle have the correct revenue data
- Craig is the de facto CTO (AI engineer, leading the 4-person engineering team, intending to formalize CTO role)
- Kyle asked Craig to provide analytics and data to supplement the Series A investor pitch — Kyle doesn't know exactly what he's looking for, he trusts Craig to figure it out
- Kyle and Cam are NOT technical — the story needs to be in results terms, not architecture terms
- The previous session's comprehensive analysis (artifact 2) was overly critical and overstepped — the CTO angle is supplementing the pitch, not auditing it
- The "Indemn" org conversations (~1,700/month) are demos and beta agents — exclude from customer metrics
- All customers can be named in investor materials

**Next steps:**
1. Craig reviews the v1 draft and provides feedback
2. Iterate on the story based on Craig's reaction and Kyle's input
3. Potentially add more specific data points once Craig validates what's accurate vs. what needs correction
4. Consider whether Stripe revenue data should be woven in (Cam/Kyle own those numbers)
5. Consider format — is this a standalone doc, a section of the deck, talking points?

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
| 2026-02-17 | [data-story-draft-v1](artifacts/2026-02-17-data-story-draft-v1.md) | First draft of data/analytics story for Kyle — platform scale, build velocity, Observatory/Eval/WebOps capabilities backed by production data |

## Decisions
- 2026-02-16: Building a data/analytics angle for the Series A — not just narrative docs but data-backed evidence of traction and PMF
- 2026-02-16: The CTO angle is about telling the technical story (frontier agentic AI, web operators, observatory data, team velocity) — NOT auditing or critiquing Cam's fundraising strategy
- 2026-02-16: Approach must be iterative and conversational with Craig — discover what data tells the best story together, don't make sweeping claims
- 2026-02-17: Don't trust numbers from previous session's analysis as ground truth — treat all financial data as unverified unless confirmed by Kyle/Cam
- 2026-02-17: The data story serves the pitch by showing what the engineering systems produce (Observatory outputs, eval results, build velocity) — the systems ARE the evidence, not just a data source
- 2026-02-17: Exclude Indemn internal org (~1,700 conversations/month) from customer metrics — those are demos/beta agents

## Open Questions
- Craig hasn't reviewed v1 draft yet — what resonates, what's wrong, what's missing?
- What format does Kyle want? Standalone doc, deck section, talking points?
- Should Stripe revenue data be woven in, or is that Cam/Kyle's domain entirely?
- The platform totals (2M messages, 143K conversations) include all-time data back to Aug 2023 — how much is production vs. test? Need to validate before putting in front of investors.
- Observatory "outcome_group" classifications (success/failure/partial) — is the classification system tuned correctly? Craig flagged "success" as a poor label for that metric.
- What do web operator production runs look like? Current data is from 5 days of development — any completed runs with measurable results yet?

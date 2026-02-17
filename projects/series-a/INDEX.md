# Series A

Building the data and analytics angle for Indemn's Series A fundraising. Consolidating existing materials, identifying gaps, and producing investor-ready artifacts that demonstrate traction, market position, and product-market fit through data.

## Status
Last session (2026-02-16-b): Read all 35 Series A docs comprehensively (saved to source-docs/). Explored the engineering systems Craig has built — web operators, evaluation harness, observatory analytics. Course-corrected approach: the CTO angle is NOT critiquing the existing fundraising strategy. It's telling the technical story — frontier agentic AI infrastructure, data from the observatory, and the team's velocity — in a way that makes investors understand the moat.

**Next steps:**
1. Pull Observatory data from MongoDB (use `/mongodb` skill) — explore observatory_conversations, daily_snapshots, precursor_lifts, flow_paths collections
2. Work iteratively with Craig to discover what data tells the most compelling story
3. Consider Stripe data to complement conversation/engagement metrics
4. Frame the technical narrative around web operators + eval system + observatory as differentiators

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

## Decisions
- 2026-02-16: Building a data/analytics angle for the Series A — not just narrative docs but data-backed evidence of traction and PMF
- 2026-02-16: The CTO angle is about telling the technical story (frontier agentic AI, web operators, observatory data, team velocity) — NOT auditing or critiquing Cam's fundraising strategy
- 2026-02-16: Approach must be iterative and conversational with Craig — discover what data tells the best story together, don't make sweeping claims

## Open Questions
- What Observatory data is currently populated? Which customers have data? What date ranges?
- What are the most impressive precursor insights the observatory has surfaced?
- How many conversations are tracked across all customers?
- What do the web operator run results look like? Any completed runs with success metrics?
- What evaluation runs have been completed? What do the results show?
- What data from Stripe + Observatory together tells the most compelling technical story?

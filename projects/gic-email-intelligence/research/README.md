# GIC Underwriters — Business Model Research

Living research corpus documenting how GIC Underwriters' wholesale brokerage actually operates. Every finding is sourced from real data.

## Purpose

1. Enable informed conversations with GIC's team (JC, Maribel)
2. Build a system data model that mirrors real operations
3. Identify automation opportunities across GIC's workflows

## Documents

| Document | What It Covers | Last Updated |
|----------|---------------|--------------|
| [company-profile.md](company-profile.md) | Who GIC is, market position, team, services | 2026-03-24 |
| [lob-catalog.md](lob-catalog.md) | All LOBs with volumes, carriers, requirements | 2026-03-24 |
| [carrier-relationships.md](carrier-relationships.md) | Carrier mapping, response patterns, timing | 2026-03-24 |
| [agent-network.md](agent-network.md) | Retail agents/agencies, submission patterns | 2026-03-24 |
| [email-workflow-patterns.md](email-workflow-patterns.md) | How emails flow, typical sequences, timing | 2026-03-24 |
| [submission-lifecycle.md](submission-lifecycle.md) | Real lifecycle model, where current model breaks | 2026-03-24 |
| [business-model-synthesis.md](business-model-synthesis.md) | Unified model tying everything together | 2026-03-24 |

## How to Use

- **Resuming work:** Read `business-model-synthesis.md` for the unified picture
- **Deep dive on a topic:** Read the specific document
- **Updating:** Re-run the MongoDB queries documented in each file's Methodology section, update findings, bump the date

## Data Sources

| Source | Access | Type |
|--------|--------|------|
| MongoDB `gic_email_intelligence` | `mongosh-connect.sh dev gic_email_intelligence` | Primary — 3,214 emails, 2,754 submissions |
| GIC website | gicunderwriters.com | External |
| Gmail threads | `gog gmail search` | External |
| Ryan's wireframes | `gic-email-intelligence/artifacts/*.html` | Prior work |
| Ryan's UX observations | `projects/gic-improvements/artifacts/ryan-gic-ux-observations.pdf` | Prior work |
| Prior artifacts | `projects/gic-email-intelligence/artifacts/` | Prior work (21 docs) |

## Document Format

Each document follows this structure:
- **Methodology** — how data was gathered, which queries/sources
- **Sources** — exact MongoDB queries, URLs, artifact paths
- **Date Analyzed** — when first created, when last updated
- **Findings** — tables over prose, top-N with examples
- **Open Questions** — what we still don't know (questions for JC)
- **Data Model Implications** — what the system should capture

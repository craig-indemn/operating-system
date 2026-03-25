---
ask: "What is the product model — associates, outcomes, pricing, packaging, showcases?"
created: 2026-03-25
workstream: product-vision
session: 2026-03-24-a
sources:
  - type: google-sheet
    ref: "1LhHA_PIz9zu8UvatUSIzeWBUvnjgvzAfFbfIfN6Gd9s"
    name: "Four Outcomes Product Matrix"
  - type: local
    description: "Series A source docs: associate-suite.txt, four-outcomes-framework.txt, customer-segments.txt, four-outcomes-product-strategy.txt"
  - type: google-doc
    ref: "1PuAXuJCagVEHTBGdPwBwtbf155PzHXWtjArVz0EPOpk"
    name: "Package Options — Independent Agency"
  - type: local
    description: "Content System project — 7 product showcase pages"
---

# Product Context

## The Four Outcomes Framework (Cam's creation)

Every insurance distribution leader is trying to achieve one of four outcomes. Everything Indemn builds serves at least one.

1. **Revenue Growth** — Unlock capacity to capture missed revenue. Lead with this.
2. **Operational Efficiency** — Liberate staff from administrative drudgery.
3. **Client Retention** — Protect the book and maximize lifetime value.
4. **Strategic Control** — Visibility, agility, and governance.

Language rules: Use "Associate" not "chatbot." Use "Engine" not "tool." Use "Revenue Capacity" not "cost savings." Use "Partner" not "vendor."

## The Four Engines

The outcomes map to engines:
- **Revenue Engine** (priority differentiator) — 24/7 quoting/binding, eligibility triage, agent portal support. Best for: MGAs drowning in submissions, program admins scaling distribution.
- **Efficiency Engine** — Service automation (digital receptionist), underwriting guardrails, internal knowledge search. Best for: retail agencies with high service volume.
- **Retention Engine** — Silent churn defender, cross-sell identification, lapse prevention. Best for: agencies protecting their book.
- **Control Engine** — No-code agility (Strategy Studio), distribution analytics, audit trails. Best for: ops leaders needing visibility.

All four engines share a single brain — one knowledge base trained on your products, guidelines, and workflows. Train once, deploy across use cases.

## The Pricing Matrix (48 Associates)

Ian sent the latest version (Four Outcomes Product Matrix) on 2026-03-24. Google Sheet: `1LhHA_PIz9zu8UvatUSIzeWBUvnjgvzAfFbfIfN6Gd9s`

### By Target Group:

**Agencies (14 items):**
| Associate | Outcome | Price/Month | Implementation |
|---|---|---|---|
| Care Associate | Retention | $1,000 (1K credits) | $2,500 |
| Renewal Associate | Retention | $500/seat/year | None |
| Front Desk Associate | Efficiency | $1,000 (1K credits) | Actual dev cost |
| Inbox Associate | Efficiency | $500/seat/year | None |
| Intake Associate | Efficiency | $5/application | $1,000 per LOB |
| Intake Associate for AMS | Efficiency | $1,000 | Actual dev cost |
| Intake Associate for Claims | Efficiency | $1,000 | $2,500 per LOB |
| Knowledge Associate | Efficiency | $500/seat/year | Actual dev cost |
| Ticket Associate | Efficiency | Company size based | Actual dev cost |
| Cross-Sell Associate | Revenue | Stepped % of GWP | $1,000 per LOB |
| Lead Associate | Revenue | $1/lead | $1,000 |
| Dashboard Associate | Control | Free | $500 |
| Strategy Studio | Control | Free | $5,000 |

**Carriers (14 items):**
| Associate | Outcome | Price/Month | Implementation |
|---|---|---|---|
| Care Associate | Retention | $1,000 (1K credits) | $5,000 + payment |
| Orphan Associate | Retention | $1,000 | $2,500 per LOB |
| Answer Associate | Efficiency | Company size based | $2,500 per LOB |
| Inbox Associate | Efficiency | $500/seat/year | None |
| Intake Associate | Efficiency | $5/submission | Actual dev cost |
| Intake Associate for Claims | Efficiency | $1,000 | $2,500 per LOB |
| Knowledge Associate | Efficiency | $500/seat/year | Actual dev cost |
| Onboarding Associate | Efficiency | $500 | $5,000 |
| Ticket Associate | Efficiency | Company size based | Actual dev cost |
| Growth Associate | Revenue | Stepped % of GWP | $500/step |
| Placement Associate | Revenue | $500/seat/year | None |
| Quote Associate | Revenue | $1,000 | $2,500 per LOB |
| Risk Associate | Revenue | $250/LOB | $5,000 per LOB |
| Strategy Studio | Control | $1,000 | Actual dev cost |

**Distribution / MGAs (20 items):**
| Associate | Outcome | Price/Month | Implementation |
|---|---|---|---|
| Care Associate | Retention | $1,000 (1K credits) | $5,000 + payment |
| Orphan Associate | Retention | $1,000 | $2,500 per LOB |
| Renewal Associate | Retention | $1,000 | $2,500 per LOB |
| Answer Associate | Efficiency | Company size based | $2,500 per LOB |
| Authority Associate | Efficiency | $1,000 (1K credits) | Actual dev cost |
| Inbox Associate | Efficiency | $500/seat/year | None |
| Intake Associate | Efficiency | $5/submission | Actual dev cost |
| Intake Associate for Claims | Efficiency | $3/NOL | $2,500 per LOB |
| Inquiry Associate | Efficiency | Company size based | Actual dev cost |
| Knowledge Associate | Efficiency | $500/seat/year | Actual dev cost |
| Onboarding Associate | Efficiency | $500 | $5,000 |
| Ticket Associate | Efficiency | Company size based | Actual dev cost |
| Growth Associate | Revenue | Stepped % of GWP | $500/step |
| Placement Associate | Revenue | $500/seat/year | None |
| Market Associate | Revenue | Based on AWP | Actual dev cost |
| Quote & Bind Associate | Revenue | Stepped % of GWP | $500/step |
| Quote Associate | Revenue | $3/quote | $2,500 per LOB |
| Risk Associate | Revenue | $250/LOB | $5,000 per LOB |
| Submission Associate | Revenue | $5/submission | Actual dev cost |
| Strategy Studio | Control | $1,000 | Actual dev cost |

**In Development (8 items, no marketing names yet):**
- Subrogation Recovery Identification
- Policy Checking & Review
- Intake Qualification (built into Welcome Mat, free)
- Win-Back Campaigns
- Monoline Agent ($1,000/product line, % of GWP)
- Compliance Audit Trails
- Secure Data Integration
- E&O Risk Mitigation

All 48 items marked "Live" status — sellable even if engineering isn't fully built.

## Unique Associate Names (~25)

Care, Renewal, Front Desk, Inbox, Intake, Intake for AMS, Intake for Claims, Knowledge, Ticket, Cross-Sell, Lead, Dashboard, Strategy Studio, Orphan, Answer, Onboarding, Growth, Placement, Quote, Risk, Authority, Inquiry, Market, Quote & Bind, Submission

## Associate-to-Domain Mapping (from research)

7 domain objects appear in 51%+ of all associates: Policy (84%), Customer/Insured (69%), Coverage (67%), Carrier (65%), Document (64%), Agent (60%), LOB (51%).

6 capabilities most reused: Generate (78%), Validate (44%), Search (40%), Route (40%), Classify (40%), Extract (38%).

**7 entities + 6 capabilities = 84% of the pricing matrix.**

Associates cluster into 7 natural groups: Intake/Triage, Knowledge/Answer, Outreach/Retention, Quoting/Binding, Email Processing, Configuration, Compliance.

The three target groups (Agencies, Carriers, Distribution) are configurations of the same platform, not separate architectures.

## Customer Segments (ICPs)

**Priority 1: Mid-Market MGAs & Program Administrators** — "The sweet spot." Have the pen (underwriting authority), buy quickly. CUO/Head of Programs buying persona. Deal: $40K-$100K ARR, 2-4 month cycle. Primary: Revenue Engine (Eligibility Triage).

**Priority 2: Mid-Market Retail Agencies & Brokerages** — High volume, standardized solutions. Agency Principal/VP Ops. Deal: $15K-$40K ARR, 1-2 month cycle. Primary: Efficiency Engine (Digital Receptionist). Critical constraint: no custom builds for agencies under $50M revenue.

**Priority 3: Insurance Carriers** — High value, long cycles. CTO/VP Digital Transformation. Deal: $100K-$250K+ ARR, 6-18 month cycle. Primary: Efficiency Engine (Knowledge Search) + Revenue Engine (Portal Support).

**Priority 4: Strategic Partners** — AMS, PAS, Insurtechs. Embed Indemn as the "Engagement Layer." Massive distribution leverage.

## Agency Packaging (from Package Options doc)

| Tier | Price | What's Included |
|---|---|---|
| **Starter** | $2,000/mo | Web chat associate, after-hours lead capture, dashboard |
| **Growth** | $3,500/mo | + Knowledge search + 1 voice agent (billing OR receptionist) |
| **Professional** | $5,500/mo | + Both voice agents + retention monitoring + brand customization |
| **Enterprise** | $8,000+/mo | + Full voice + cloning + outbound + AMS integration + dedicated engineer |

$0 upfront. 90-day trial. Month-to-month after. Week 1 discovery, Week 2-3 config, Week 3-4 go-live.

## Product Showcases (7 live on blog.indemn.ai)

| Page | Demonstrates | Associate Mapping | Customer Outcome |
|---|---|---|---|
| Document Retrieval | Automated document request fulfillment | Front Desk / Care | Efficiency (agencies) |
| Quote & Bind | Complete digital distribution channel | Quote & Bind | Revenue (MGAs, distribution) |
| Conversational Intake | Welcome Mat replacing forms/phone trees | Front Desk | Revenue + Efficiency (all) |
| Email Intelligence | Chaotic inbox → organized submission pipeline | Inbox | Efficiency (MGAs, distribution) |
| Intake Manager | Full underwriting submission pipeline | Intake | Efficiency (MGAs, carriers) |
| Cross-Sell | Coverage gap identification during service | Cross-Sell / Risk | Retention + Revenue (agencies) |
| CLI & MCP Server | Developer infrastructure | (Developer tooling) | Control (internal) |

Each showcase demonstrates a WORKFLOW, not just a feature. Each workflow is powered by multiple associates working together. The customer buys the outcome ("my inbox becomes an organized pipeline"), not the associate.

Showcase pages map to Ryan's taxonomy:
- Document Retrieval → Servicing Journey → Document Fulfillment Workflow
- Quote & Bind → Quote Journey → Full Placement Workflow
- Conversational Intake → Prospect & Intake Journey → Qualification Workflow
- Email Intelligence → Submission Journey → Triage Workflow
- Intake Manager → Submission Journey → Full Processing Workflow
- Cross-Sell → Renewal/Servicing Journey → Gap Identification Workflow

## The 52 Marketing Sheets

Cam confirmed (Craig/Cam 1:1, Mar 23) that marketing sheets already exist for all 47 outcomes. They live in the #fractional-cmo Slack channel. External contractors (A18) converting them to marketing pieces. Sales team not utilizing them — accessibility problem, not content problem.

## Craig's Key Insight on Associates

Associates are not 48 different products. They are 48 configurations of the same underlying agent system. Each associate is a configured composition of capabilities operating on domain objects through channels. The distinction between associate types is: which skills are enabled and which domain objects they're authorized to touch.

Under the hood, a "Renewal Associate" is: a scheduled trigger → reading Policy and Customer domain objects → running a Compare capability against renewal pricing → generating a communication via the Email channel → surfacing results in the platform UX.

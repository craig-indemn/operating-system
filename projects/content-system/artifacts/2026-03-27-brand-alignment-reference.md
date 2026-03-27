---
ask: "Align all product showcase pages with Four Outcomes Matrix, Master Context 2026, and brand guidelines — create a reusable reference for future pages"
created: 2026-03-27
workstream: content-system
session: 2026-03-27-a
sources:
  - type: google-sheet
    ref: "1LhHA_PIz9zu8UvatUSIzeWBUvnjgvzAfFbfIfN6Gd9s"
    name: "Four Outcomes Product Matrix January 2026 v2.0"
  - type: google-doc
    ref: "10HQMMU8E5NEg8iym3FAjiQxoE3E09drPVQic5JIx2mE"
    name: "Indemn: 6 - Master Context 2026 (Updated February 2026)"
  - type: google-doc
    ref: "1hPLHkC32Uk_7_CeLm45r1uEfcpiHx8W75Z-XyuxfSIs"
    name: "Indemn Master Context Prompt (v2026.2)"
  - type: google-doc
    ref: "1ibuNPLYOpID063UJpJhVbXwY91mniNvv0SeNnoYscYI"
    name: "Indemn Marketing Material Personna Prompt September 2025"
  - type: google-doc
    ref: "1Oo16h5_DWLwuboAgyZiRgNAVe9g7mqd6gVvXh5z32BU"
    name: "Indemn: 1 - Company Overview (Q1 2026 v 2.0 Update)"
  - type: slack
    description: "Cam's posts in #branding_and_design and #general with matrix + pricing PDF"
---

# Brand Alignment Reference for Product Showcase Pages

Use this when building or reviewing any product showcase page on blog.indemn.ai.

---

## The Four Outcomes Framework

**Every product, every page, every communication maps to one of these four outcomes:**

| Outcome | What It Delivers | Key Associates |
|---------|-----------------|----------------|
| **Revenue Growth** | Unlocks capacity to capture missed revenue | Quote & Bind, Growth, Lead, Placement, Quote, Risk, Submission, Market |
| **Operational Efficiency** | Liberates human staff from administrative drudgery | Front Desk, Inbox, Intake (LOB/AMS/Claims), Knowledge, Ticket, Authority, Inquiry, Onboarding |
| **Client Retention** | Protects the book and maximizes LTV | Care, Renewal, Orphan, Answer |
| **Strategic Control** | Provides visibility, agility, and governance | Strategy Studio, Dashboard |

The `category` field in every product MDX **must** use one of these four exact strings.

---

## Lexicon Rules (STRICT)

### Banned Words — Never Use
| Banned | Use Instead |
|--------|-------------|
| Chatbot / Bot | Associate |
| Agent (when referring to Indemn product) | Associate |
| Cost Savings / Cost Reduction | Revenue Capacity |
| Deflection Rate | Resolution Rate |
| Tool / Software (when referring to Indemn) | Capability / Digital Workforce |
| Vendor | Partner |
| SaaS / Per-Seat Pricing | Agentic Business Results (ABR) |
| Automation Rate | Resolution Rate |
| "The system" (in customer-facing copy) | "The Associate" or the specific marketing name |

### When "agent" Is Okay
- **Human insurance agents/brokers** in problem narrative: "Agents email quotes that sit unopened" — this refers to humans, keep it
- **CLI command syntax** in code blocks: `indemn agent create` — literal command, keep it
- **Human CSRs** in problem descriptions: "before the agent realizes the caller is in the wrong place"

### Additional Word Rules
- "tools" is okay when referring to the MCP protocol's technical concept (it's the protocol term), but prefer "capabilities" in marketing copy
- "No new tools to learn" → "No new platforms to learn"
- Never say "revolutionary", "game-changing", "leading", "innovative", "unique", "solution", "best-in-class"

---

## Page ↔ Associate Mapping

Every showcase page maps to a specific Associate from the Four Outcomes Matrix:

| Showcase Page | Category | Marketing Name | Target Group |
|--------------|----------|---------------|--------------|
| Document Retrieval | Operational Efficiency | Front Desk Associate | Agencies |
| Quote & Bind | Revenue Growth | Quote & Bind Associate | Distribution (MGAs) |
| Conversational Intake | Operational Efficiency | Front Desk Associate | Agencies |
| Email Intelligence | Operational Efficiency | Inbox Associate | Agencies / Carriers / Distribution |
| Intake Manager | Operational Efficiency | Intake Associate | Carriers / Distribution |
| Cross-Sell | Revenue Growth | Cross-Sell Associate | Agencies (also Risk Associate for Carriers) |
| Member Support | Operational Efficiency | Care Associate | Carriers |
| Indemn CLI | Strategic Control | Strategy Studio | All |

The marketing name should appear naturally in the body copy — typically the first time the product is introduced after the problem statement.

---

## Proof Points (Use Liberally)

### Eventuguard Validation (Social Proof)
> "Indemn created, scaled, and sold a fully digital MGA to Jewelers Mutual Insurance, with our Associates completing over 90% of policy sales without human intervention."

**Best fit:** Quote & Bind, any revenue growth page.

### Key Metrics
| Metric | Context | Best Fit Pages |
|--------|---------|---------------|
| **46% of broker questions automated in 60 days** | GIC Underwriters case | Conversational Intake, Document Retrieval, Member Support |
| **25% lift in conversion** vs. web forms | Conversational quoting | Quote & Bind, Conversational Intake |
| **60% conversion on cross-sell** | In-conversation recommendations | Cross-Sell |
| **~60 days to production** | Standard deployment timeline | All pages (FAQ answers about setup) |

### Human-in-the-Loop
The foundational safety net. Must be prominent on trust-critical pages (Quote & Bind, Email Intelligence). Not just buried in FAQs. Key language:
- "When the risk is complex or the judgment call matters, the Associate queues it for human review."
- "Every draft marked for human review before it leaves your inbox."
- "Your team stays in control of every communication."
- References NAIC AI Model Bulletin compliance when relevant.

---

## Messaging Principles

### 1. Outcome-First (Not Feature-First)

**Bad:** "Automate certificate retrieval across email, phone, and chat."
**Good:** "Your team handles document requests in minutes, not hours."

The `description` field renders in search results and OG cards — high-impact real estate. Always lead with what the customer gets.

### 2. "Your Business..." Not "Our AI..."

Never start a sentence with "Our AI..." or "The platform..." Start with the customer's world.

### 3. Anchor on Lost Revenue / Status Quo Cost

"How many submissions did you decline last month simply because you didn't have time to look at them?"

Frame efficiency as **unlocking revenue capacity**, not cutting costs. "Every hour your team spends sorting email is an hour they are not spending on underwriting, broker relationships, or placing business."

### 4. Partner, Not Vendor

CTA descriptions should include "partner" language: "We partner with you to configure..." not "We configure..."

### 5. Insurance-Native Expert

Use precise insurance terminology (FNOL, subrogation, binding authority, ACORD, surplus lines). We speak insurance fluently. We are not a generic AI company.

### 6. Bridge Strategy

Suggest natural expansion: "Start with X, then expand to Y." This supports the Land & Expand sales motion.

---

## Pre-Publish Checklist

Before deploying any showcase page, verify:

- [ ] **Category** is one of: Revenue Growth, Operational Efficiency, Client Retention, Strategic Control
- [ ] **Marketing name** from the matrix appears in the body copy
- [ ] **Description** leads with customer outcome ("Your team..." / "Your visitors..." / "Your members...")
- [ ] **Zero banned words**: grep for chatbot, bot, software, tool, vendor, SaaS, "the system"
- [ ] **"agent"** only refers to human insurance agents/brokers or CLI commands — never Indemn's product
- [ ] **Proof points**: at least one metric or the Eventuguard validation where relevant
- [ ] **Human-in-the-Loop**: mentioned in body or FAQ on trust-critical pages
- [ ] **Revenue capacity** framing on operational efficiency pages (not "cost savings")
- [ ] **Partner language** in CTA description
- [ ] **~60 days** or specific timeline in FAQ about setup
- [ ] `npx astro build` passes with zero errors

---

## Source Documents (Google Drive)

| Document | ID | What It Contains |
|----------|----|--------------------|
| Four Outcomes Matrix v2.0 | `1LhHA_PIz9zu8UvatUSIzeWBUvnjgvzAfFbfIfN6Gd9s` | All Associates by target group, outcome, marketing name, pricing |
| Master Context 2026 | `10HQMMU8E5NEg8iym3FAjiQxoE3E09drPVQic5JIx2mE` | Core identity, lexicon rules, product architecture, ICPs, sales playbook |
| Master Context Prompt v2026.2 | `1hPLHkC32Uk_7_CeLm45r1uEfcpiHx8W75Z-XyuxfSIs` | AI prompt version — strict lexicon, outcome architecture, ICP mapping |
| Marketing Persona Prompt | `1ibuNPLYOpID063UJpJhVbXwY91mniNvv0SeNnoYscYI` | Voice mandate, L1-L4 message hierarchy, competitive positioning, proof points |
| Company Overview Q1 2026 | `1Oo16h5_DWLwuboAgyZiRgNAVe9g7mqd6gVvXh5z32BU` | Purpose, mission, vision, UVP, Associate Suite breakdown |
| GTM Strategy Q1 2026 | `1jKJiVG0x3jpeUgKCRpNft8OQdNnoGS_s_YAH66Yk9UU` | Wedge strategy, target segments, Land & Expand, ABR pricing |

Read these with: `gog docs cat <ID>`
Read the spreadsheet with: `gog sheets get <ID> --sheet "Jan '26 Model v2.0 - Master"`

---
ask: "Establish the source material for the associate-pricing-framework work — what was decided in the Cam/Kyle/Craig pricing call, what's in Kim's spreadsheet, and what notes Craig has already begun adding."
created: 2026-04-30
workstream: customer-system
session: 2026-04-30-a
sources:
  - type: google-doc
    ref: "https://docs.google.com/document/d/1JUEa5v7rzuh7JB_YRYW9JhJEkiSznxrlhdhiBDthK18/edit"
    name: "Automated Proposal — meeting smart-notes summary (Gemini)"
  - type: google-sheet
    ref: "https://docs.google.com/spreadsheets/d/17GEDxqTvCHxHYsZKSQDppGfx6XYOzykUkuF_rxQUsx4/edit"
    name: "Indemn Pricing, May 1, 2026 — tabs: 'May 1 2026' (Cam main) + 'Craig|Kyle Working Copy'"
---

# Pricing call + spreadsheet — source material distilled

This artifact captures the input material for the associate-pricing-framework working doc. It distills the call where Cam established the Enterprise/Core split, and the structure of Kim's spreadsheet that Cam manages.

---

## 1. The Cam/Kyle/Craig pricing call — load-bearing decisions

The call is captured as a Gemini AI smart-notes summary (not full verbatim transcript). The key framing:

### The Enterprise vs Core split (the load-bearing concept)

Cam established that Indemn's product offering should be split into **two distinct buckets**:

| | **Enterprise** | **Core** |
|---|---|---|
| **What it is** | Custom solutions, high-touch | Standardized outcomes, low-touch |
| **Proposal model** | AI-driven, considers large input data, uses the customer-system engine Craig is building | Largely automated, minimal customization, formulaic pricing |
| **Sales motion** | Current discovery → analysis → custom build | Website-driven self-service, prospect generates and signs own proposal |
| **Customer expectation** | Dramatically higher revenue, justifies higher input | Quick deployment, defined outcomes, defined cost |
| **Implementation lift** | High (currently fixed cost via team) | ≤7 days deploy KPI; goal is near-zero for some subsets |
| **Pricing intent** | Custom per deal | Embedded, formulaic, simple |

Cam's framing: "We're pivoting from a zero-to-one stage (every conversation enterprise) to a one-to-ten stage. Define the desired customer experience FIRST, then build systems to support it — don't let historical sales process dictate."

### The flywheel

> Enterprise builds → IP-protected pieces extracted → pushed down to Core production → revenue with near-zero implementation lift → improves net margins.

Periodic monthly/quarterly review of "yellow section" (under-development items, currently exemplified by GIC builds) for transition into Core + IP protection review.

### Aligned decisions (8)

1. **Centralized proposal generation** — all proposals issued centrally; no fragmented creation
2. **Two-path proposal strategy** — Enterprise (custom) vs Core (automated)
3. **Core implementation KPI = 7 days** time-to-deploy
4. **Periodic review** of dev-phase items for Core transition + IP protection
5. **Limit supported integrations to high-market-share systems** — Outlook + Gmail explicitly named (operational feasibility)
6. **No implementation fee for 12-month commitment** — staffing is fixed cost; incremental Core deploy cost ≈ $0; $12K ARR > implementation fee mix for fundraising story
7. **Digital proposals < 10 pages with live links** — most pages static, only pricing/solution dynamic
8. **Worksheet-based input process** — sales team forced to provide all info needed for automated population

### Action items from the call (relevant to this work)

| Owner | Item | Notes |
|---|---|---|
| **Craig Certo** | Analyze Associate Usage — use Claude Code to determine which associates are most frequently deployed together | Direct input to Core productization |
| **Kyle + Craig** | Analyze Customer Solutions — collaborate to define actual delivery process for outcomes based on existing customer data | Pairs with the above |
| Cam | Share Core pricing paradigm document | Awaiting |
| Ganesha | Estimate days-to-deploy per outcome (spreadsheet column) | Will be informed by our framework work |
| Cam | Schedule monthly/quarterly IP review | — |
| Cam | Outline proposal structure (Core) | — |
| Cam | Revise outcome descriptions (compact + descriptive) | — |

**The first two action items ARE this side-project.** What Craig is asking me to build directly delivers on Cam's "Analyze Associate Usage" assignment, plus the Kyle+Craig joint task on defining delivery process from existing customer data.

### Craig's call observation (load-bearing for the framework)

> "Development time is less dependent on the type of associate, and more on the integrations required. GIC was 90% integration work. We need adapters for major platforms (Outlook, Gmail, Applied Epic) to make Core capabilities truly scalable."

This is the lens for the framework — **integrations are the cost driver, not the associate "concept."**

---

## 2. The spreadsheet — current state

**Title:** Indemn Pricing, May 1, 2026
**ID:** `17GEDxqTvCHxHYsZKSQDppGfx6XYOzykUkuF_rxQUsx4`

### Two tabs

1. **"May 1 2026"** — Cam's main / formal tab. 27 columns × 1001 rows.
2. **"Craig|Kyle Working Copy"** — Craig's sandbox. Adds 3 columns (Questions/Comments, What does it take to deliver, Man Hours) where Craig has begun annotating select rows.

### Column schema (main tab)

| Column | Meaning |
|---|---|
| Customer | Customer type — `Agency/Broker`, `Carrier`, `MGA`, or `Z - In development` |
| Outcome | Outcome category — `Client Retention`, `Operational Efficiency`, `Revenue Growth`, `Strategic Control` |
| Associate Name | The branded associate name (Care, Renewal, Inbox, Intake, etc.) |
| Job to be Done | Short pitch line (e.g., "The Silent Churn Defender") |
| Description of Outcome | Sales-facing description of what it does |
| Price Per Month | Pricing tier (flat / per-seat / per-ticket / per-LOB / % of GWP / Free) |
| Price Ext. | Pricing unit qualifier (`/seat`, `/ticket`, `/LOB`, `/gross written premium`) |
| Current Days to Deploy (from sign-up) | Time-to-active estimate (Cam's KPI target ≤7) |

### Working Copy adds three Craig columns

| Column | Meaning |
|---|---|
| Questions/Comments | Qualifying questions / clarifications needed for sales |
| What does it take to deliver | Skills + work involved (the framework input) |
| Man Hours | Implementation effort estimate |

### Customer-type × Associate matrix — what's covered

**Agency/Broker associates (12 deployable + dashboard/strategy-studio):** Care, Renewal, Front Desk, Inbox, Intake (LOB), Intake-for-AMS, Intake-for-Claims, Knowledge, Ticket, Cross-Sell, Lead, Dashboard, Strategy Studio.

**Carrier associates (12 deployable):** Care, Orphan, Answer, Inbox, Intake (Submission Triage), Intake-for-Claims, Knowledge, Onboarding, Ticket, Growth, Placement, Quote, Risk, Strategy Studio.

**MGA associates (16 deployable):** Care, Orphan, Renewal, Answer, Authority, Inbox, Intake (Submission Triage), Intake-for-Claims, Inquiry, Knowledge, Onboarding, Ticket, Growth, Placement, Market, Quote & Bind, Quote, Risk, Submission, Strategy Studio.

**In development ("Z" rows, 8 items):** Subrogation Recovery, Policy Checking & Review, Intake Qualification, Win-Back Campaigns, Monoline Agent, Compliance Audit Trails, Secure Data Integration, E&O Risk Mitigation.

**Total deployable rows ≈ 47 (Cam said 47 in the call). Plus 8 in-dev = 55 rows.** Many associates appear under multiple customer types with adjusted pricing — they're the same associate concept with customer-context variation.

### Pricing tier distribution

- **Flat $/mo** ($500–$5,000): high-touch associates with a defined scope
- **$/seat** ($50): used by Inbox, Knowledge, Placement — capacity-based
- **$/ticket** ($0.50–$5): used by Intake, Ticket, Lead, Intake-for-Claims — volume-based
- **$/LOB** ($250): Risk Associate (carrier)
- **% of GWP** (2%): Cross-Sell, Growth, Quote & Bind — outcome-tied
- **Free / $0**: Dashboard, Strategy Studio (Agency/Broker tier)

### Days-to-deploy current ranges (where filled in)

7 / 7-14 / 14 / 14-30 / 30 / "30 or less" / 30-60 / 30-90 / 60-120 / Dev

Cam's KPI target: **≤7 days for Core**. Most rows currently sit at 30 — the gap to close.

---

## 3. Notes Craig has already added in the Working Copy

Selected rows have meaningful annotations that show the shape of the framework Craig is building. Examples worth carrying forward:

### Renewal Associate (Agency/Broker)

- **What does it take to deliver:** Integration with system, understanding current workflow of the customer, drafting emails
- **Man Hours:** "Currently integrated: 30 hours. Additional integration: 30-50 hours depending on complexity for new integration. Total 60 hours for new integration + man hours to implement the solution."
- **Insight:** the cost has two terms — *(have we already integrated with this system before?)* + *(per-customer skill build / workflow understanding)*

### Intake Associate for AMS (Agency/Broker)

- **Question/comment:** "Dev time and ROI is based on the skills implemented. New quotes being entered into the AMS. Quotes from the carrier being sent back to the agent. Automating the submission of a quote to a carrier. **Every new carrier that I add to the mix involves me creating a skill for automation the submission of the quote to the carrier.** What types of things are you doing from the inbox? Dedicated inbox versus a big inbox with many purposes. For GIC: Quote Intake Associate for AMS but could be Endorsement Intake Associate for AMS."
- **Insight:** one associate concept (Intake-for-AMS) → multiple skills (Quote Intake, Endorsement Intake, Carrier Submission) → each new carrier = new skill. This is the *skills-as-input/task/output* unit Craig describes, in raw form.

### Knowledge Associate (Agency/Broker)

- **What does it take to deliver:** "Gather sites or documents from the customer and put them into our knowledge bases. Build an agent prompt and KB retriever function to retrieve information from the KB and answer questions based on the KB."
- **Man Hours:** KB Development: 3-5h, Prompt Development: 3-5h, Testing/Evaluation: 2h. **Total ~8-12 hours.**
- **Insight:** this one is genuinely a Core candidate today — low integration lift, well-understood skill template, near-zero per-customer overhead.

### Care Associate (Agency/Broker)

- **Question/comment:** "What information does the associate need to do personalized outreach? Outbound phone calls and/or emails, text messages — do we want a default?"
- **Insight:** channel question — what channel(s) is the associate operating on, and is there a default vs configurable?

### Front Desk Associate (Agency/Broker)

- **Question/comment:** "Qualification needed to define whether this is overflow, after hours, etc."
- **Insight:** sales qualification needed before pricing — the same associate name covers very different deployment patterns.

### Inbox Associate (Agency/Broker)

- **Question/comment:** "This is not the same as shipping data from inbox into AMS. 'Your claim is being processed', simple underwriting questions."
- **Insight:** disambiguation — Inbox Associate ≠ Intake-for-AMS. The Inbox is *responding from the inbox*; Intake is *moving data INTO the AMS from the inbox*. Different skills, different integrations.

### Other rows lightly noted

- **Orphan Associate** (Carrier/MGA): "30-90 days, dependent on # of communication channels and potential divergence between renewals."
- **Lead Associate** (Agency/Broker): "Dependent upon appointment scheduling tool."
- **Intake (Submission Triage)** (Carrier/MGA): "Dependent on # of documents to be trained and amount of data within each document."
- **Inquiry Associate** (MGA): "Multi modal additional complexity but not major."
- **Placement Associate** (MGA): "Doing more than appetite guidance, additional integrations available — for example policy status for GIC with policy administration system."
- **Quote & Bind / Growth Associate**: "60-120 days, depending on complexity of the program."

---

## 4. What this points at — the framework shape

The annotations Craig has already added describe the framework in raw form. Distilled:

1. **An "associate" is a brand/concept; the actual cost is in skills + integrations.**
2. **A skill is an `input → task → output` unit** scoped to a specific channel and a specific system action.
3. **Integration cost has two parts:**
   - **Channel integration** (how input arrives) — email/voice/chat/text/Teams/Slack
   - **System integration** (where output lands or input is read from) — AMS, PMS, CRM, carrier portal, scheduling tool
4. **Channel integrations vs system integrations have very different cost profiles:**
   - Channels: small finite set (~6-8); cost is mostly upfront-shared once built (Outlook adapter built once → reusable)
   - Systems: long tail (every AMS, every PMS, every carrier portal); cost is upfront for the FIRST customer on that system, near-zero after
5. **A given associate's deployment cost = (channel integration ready? Y/N) + (system integration ready? Y/N) + (skill template ready? Y/N) + per-customer configuration work.**
6. **Crawl/walk/run** is real here: many associates can run *without* customer system integration using Indemn's platform channels (web chat, our voice agent, our hosted KB) and gain power *with* integration.
7. **Core eligibility = the channel + system integrations are already built AND the skill templates are reusable AND per-customer config is small.**

The framework, then, has 3-4 reference tables (channels, systems, skills) and a per-associate composition page that pulls from them. Pricing falls out: known integrations + known skills → known cost → known days-to-deploy → automated proposal.

---

## 5. Hand-off

This artifact is source material. The working doc that builds the framework lives separately (next artifact, once structure is approved). When the framework matures, it folds into:

- The customer-system project (eventually as `AssociateType` + `Skill` + `IntegrationCapability` records in the OS)
- Cam's spreadsheet (3 new columns: Skills, Integrations Required, Implementation Cost — populated systematically)
- The `/pipeline` proposal-generation surface (TD-7), where prospect-selected associates auto-populate cost + days-to-deploy

The Enterprise/Core split is the orienting frame. The framework lets us answer per associate: *can this be Core today?* and *what would it take to make this Core?*

---
ask: "Build the framework that bridges what we actually deliver (skills + integrations composed into associates) with Cam's 47-associate pricing spreadsheet. Reverse-engineer from current customers first; sweep the catalog after. Output: an augmented Cam spreadsheet that drives proposal automation."
created: 2026-04-30
workstream: customer-system
session: 2026-04-30-a
status: in-progress
sources:
  - type: artifact
    ref: "artifacts/2026-04-30-pricing-call-and-sheet-source-material.md"
    name: "Source material — pricing call decisions + sheet schema + existing Craig annotations"
  - type: google-doc
    ref: "https://docs.google.com/document/d/1JUEa5v7rzuh7JB_YRYW9JhJEkiSznxrlhdhiBDthK18/edit"
    name: "Cam/Kyle/Craig pricing call — Gemini smart notes summary"
  - type: google-sheet
    ref: "https://docs.google.com/spreadsheets/d/17GEDxqTvCHxHYsZKSQDppGfx6XYOzykUkuF_rxQUsx4/edit"
    name: "Indemn Pricing, May 1, 2026"
---

# Associate Pricing Framework — Working Doc

This is the document we work off of as we walk through customers and build out the pricing/product framework. It accumulates the truth as we go. When mature, § 12 produces the spec to apply to Cam's sheet.

**Status legend per row/section:** `[empty]` to fill · `[in-progress]` actively working · `[draft]` ready for Craig review · `[validated]` Craig signed off.

---

## 0. Session Handoff (read this first if resuming)

> **Last updated 2026-05-01.** This section is the canonical handoff for resuming the work. Read this, then § 2 (the framework), § 2.05 (catalog gaps), § 8 (per-customer detail), §§ 5-7 (catalogs).

### What this work is

Reverse-engineer Indemn's actual delivery (skills + integrations + channels composed into associates) from current customers, map back to Cam's 47-associate pricing catalog, surface gaps, and ultimately augment Cam's spreadsheet so proposal generation becomes formulaic. **This is a Cam-assigned action item from the Apr 30 pricing call** ("[Craig] Analyze Associate Usage" + "[Kyle + Craig] Analyze Customer Solutions") — not a side project, despite running in parallel to the main customer-system roadmap (TD-1).

### Where we are (2026-05-01)

**9 of 18 customers walked** (12 active customers + 6 prospects with build history; 8 dropped from AI_Investments tier per Craig).

| # | Customer | Status |
|---|---|---|
| 8.1 | GIC Underwriters | ✅ Done (3 associates: Quote Intake for AMS · Placement · Workers Comp Voice) |
| 8.2 | Jewelers Mutual | ✅ Done (2 associates: Quote & Bind w/ Q&A+lead folded · Knowledge for Zola) |
| 8.3 | INSURICA | ✅ Done (3 associates: Renewal · Front Desk · Medicare Part D Navigator) |
| 8.4 | Union General | ✅ Done (4 associates: Knowledge multi-carrier · Intake+Market combined · Lead Mobile Home · Onboarding) |
| 8.5 | Distinguished Programs | ✅ Done (1 associate: Knowledge with 5 specialization variants) |
| 8.6 | Johnson Insurance Services | ✅ Done (1 associate: Intake-for-AMS Renewal/Endorsement variant, 4 ECM paths) |
| 8.7 | Branch | ✅ Done (5 associates: Inquiry · Document Fulfillment · Claims Status · Care/Billing · Sales/Lead) |
| 8.8 | O'Connor Insurance Associates | ✅ Done (3 associates: Front Desk billing · Knowledge external · Ticket internal) |
| 8.12 | Silent Sport | ✅ Done in pilot state (1 associate: Lead Associate w/ Q&A folded in) |
| 8.9 | Rankin Insurance Group | ⏳ Next |
| 8.10 | Tillman Insurance | ⏳ Pending |
| 8.11 | Family First | ⏳ Pending |
| 8.21–8.26 | Alliance · GR Little · Armadillo · FoxQuilt · Charley · Physicians Mutual | ⏳ Prospects with build history; walk after active customers |

**Catalog state:** 48 tool skills · 47 pathway skills (after revisions) · 8 channels · 27 systems · 4 catalog gaps tracked in § 2.05.

### The framework rules (load-bearing — earned through revision in this session)

**1. Paths ARE skills.** A skill is an end-to-end process the associate carries through. Path-level granularity, not function-call-level.

**2. Two skill types:**
- **Tool skill** — atomic capability the agent invokes like a function call (KB retrieval, classify email, look up policy, generate document). High reuse.
- **Pathway skill** — end-to-end workflow orchestrating tool skills + customer-specific logic (ECM CAP renewal, Application submission into AMS, Workers Comp appetite verification). Medium reuse.
- **NOT tool skills (implicit in system integration TYPE):** browser automation, field writes, navigation, document retrieval — these come "free" with the integration type (`web operator` brings them; `API` brings whatever endpoints exist).

**3. Skill specificity is emergent.** A pathway is specific along whatever dimension makes its work materially different — LOB, carrier, workflow type, system, customer business rule. Skill names encode their scope. Don't pre-bake an LOB column.

**4. Bundle-by-task rule** (load-bearing — applied retroactively):
- **Bundle when** SAME agent does multiple tasks in one conversation (JM Dahlia: Q&A + lead + quote → ONE Quote & Bind), OR multiple agents are *orchestrated together* toward one objective (INSURICA Renewal: 7 channel agents + MARA orchestrator → ONE Renewal Associate).
- **Split when** DIFFERENT agents have DIFFERENT objectives, no shared orchestration. Each persona = its own associate.

**5. Built-only.** Only catalog what's actually built. Don't include proposals or planned work. Don't filter by "live vs prototype" though — built is built regardless of production status.

**6. The formula.** For a customer deal: `Implementation cost = (channel integrations) + (skill development) + (system integrations)`. Channels and systems live at the deal level, NOT bound to individual skills. Multiple skills share the same Outlook integration / Unisoft integration on a given customer.

**7. Crawl/walk/run.** This is how we communicate phasing to customers (immediately / near term / long term). NOT an integration-depth concept.

**8. LOE scoping rule.** For things already developed → use actual hours. For things not built for any customer → estimate first-customer LOE.

**9. Reuse caveat.** Cross-customer reuse is directional, not guaranteed today. Most integrations are per-customer-custom (gic-email-intelligence is its own repo, branch-* services are per-customer, etc.). Don't claim reuse savings as fact.

### The discipline (learned from Craig's pushback)

**Surface findings → discuss with Craig → only write to doc after agreement.** Past failures: I wrote sections speculatively (Silent Sport "live" framing, document generation as "NET NEW", Branch as 2-bundles when 5 was right). Each got pushback. **The pattern is: bring data + propose mapping + ask, then write only what's agreed.** No willy-nilly authoring. No LOE estimates without grounding. No tier classifications (Core/Soon/Enterprise) — those are Craig's, not mine.

### The per-customer process

For each customer, in parallel:
1. **OS** — `indemn company list` to find Company entity; pull notes, champion, AMS, drive_folder_url. (Use `INDEMN_SERVICE_TOKEN` from AWS Secrets Manager `indemn/dev/shared/runtime-async-service-token` against `https://api.os.indemn.ai`.)
2. **Drive** — `gog drive search "<Customer>"` + check Cam's portfolio at folder `1k0_SYLdYtlM40y6W-ZAMV3Trr9hIq2Ph` for proposals.
3. **MongoDB tiledesk** — query via SSM run-command into prod-services EC2 (`i-00ef8e2bfa651aaa8`) docker exec into `bot-service-app-1` container. The bot-service container connects to `prod-indemn.3h3ab.mongodb.net` as `devadmin`. Query `structure_customers` for the customer summary, `bot_configurations` for prompts (`ai_config.system_prompt`), `bot_tools` for tool list (with URLs at `configurationSchema.endpoint` and `executionSchema.actions[].url`). Dedicated mongodb skill at `.claude/skills/mongodb/`.
4. **GitHub** — `gh api search/code?q=org:indemn-ai+<term>` for customer-specific code; check operations_api for carrier-specific routes.
5. **Slack** — `#customer-implementation` channel for weekly updates if needed; per-customer channels (e.g., `#customer-gic`) where they exist.

Then: surface findings to Craig with proposed associate mapping → discuss + confirm → write to doc.

### Process for each customer write-up (after Craig confirms)

1. Add per-customer section in §8.x with associate mapping, pathways, tool skills, channels, systems
2. Add new pathway entries to §7 (Skills catalog — Pathway skills table)
3. Add new tool skills to §7 (Tool skills table) if surfaced
4. Add new channels to §5 if surfaced
5. Add new systems to §6 if surfaced (with actual API URLs and integration type — `API` or `web operator`)
6. If a Cam catalog gap surfaced, add to §2.05

### Open items / what to do next session

- **Continue customer walk:** Rankin (next) → Tillman → Family First → then prospects (Alliance, GR Little, Armadillo, FoxQuilt, Charley, Physicians Mutual).
- **Catalog gaps already tracked (§ 2.05):** Lead Associate for MGA tier · Quote & Bind for Agency/Broker tier · Document Fulfillment Associate · Claims Status Associate. May surface more.
- **Document generation as a capability area (tool-038)** — flagged for formalization as shared platform skill.
- **After customer walk completes:** populate §9 (per-associate sweep against Cam's 47 rows) → §10 (final sheet update spec for Cam).
- **Don't touch Cam's sheet** until §10 produces the migration spec and Craig signs off.

### Session-start protocol for next session

1. Read the canonical context per `PROMPT.md` (CLAUDE.md · vision.md · roadmap.md · os-learnings.md · CURRENT.md · indemn-os CLAUDE.md)
2. Read this working doc (especially §0 Session Handoff, §2 Formula, §2.05 Catalog gaps, §8 customer detail)
3. Read the source-material artifact (`artifacts/2026-04-30-pricing-call-and-sheet-source-material.md`) for context on the Cam call decisions
4. Confirm understanding of: framework rules · process · what's done · what's next
5. Pick up with next customer (suggested: Rankin)

### Key files / references

- **Working doc:** `artifacts/2026-04-30-associate-pricing-framework.md` (this file)
- **Source material:** `artifacts/2026-04-30-pricing-call-and-sheet-source-material.md` (Cam call decisions + Cam sheet schema + existing Craig annotations)
- **Cam's spreadsheet:** `https://docs.google.com/spreadsheets/d/17GEDxqTvCHxHYsZKSQDppGfx6XYOzykUkuF_rxQUsx4/edit` (DON'T modify until §10 spec is ready)
- **Cam's proposal portfolio:** Drive folder `1k0_SYLdYtlM40y6W-ZAMV3Trr9hIq2Ph`
- **Cam call notes (Gemini summary):** `https://docs.google.com/document/d/1JUEa5v7rzuh7JB_YRYW9JhJEkiSznxrlhdhiBDthK18/edit`

---

## 1. Why this exists

### The Cam-assigned action items

This work delivers two action items Cam assigned in the **April 30 pricing call** (see source-material artifact, § 1):

1. **[Craig] Analyze Associate Usage** — use Claude Code to determine which associates are most frequently deployed together, package the common groupings as ready-made Core solutions.
2. **[Kyle + Craig] Analyze Customer Solutions** — collaborate to define the actual delivery process for outcomes based on existing customer data.

Plus the framework Craig is articulating: a formal model where associates decompose into skills + integrations, with cost flowing from those primitives — making per-prospect proposal generation formulaic rather than artisanal.

### The Enterprise vs Core split (the orienting frame)

Per Cam in the call, Indemn's product split:

| | **Enterprise** | **Core** |
|---|---|---|
| **What it is** | Custom solutions, high-touch | Standardized outcomes, low-touch |
| **Proposal model** | AI-driven via the customer-system engine (this project) | Largely automated, formulaic pricing |
| **Sales motion** | Discovery → analysis → custom build | Website self-service, prospect generates own proposal |
| **Customer expectation** | Higher revenue, higher input justified | Quick deploy, defined outcomes, defined cost |
| **Implementation lift** | High (currently fixed-cost team) | ≤7 days deploy KPI; goal near-zero for some subsets |

### The flywheel

> Enterprise builds → IP-protected pieces extracted → pushed down to Core production → revenue with near-zero implementation lift → improves net margins.

Periodic monthly/quarterly review of "yellow section" (under-development items) for Core transition + IP review.

### Aligned decisions from the call

Centralized proposal generation · Two-path proposal strategy (Enterprise/Core) · Core ≤7-day deploy KPI · Periodic Core-transition review · Limit supported integrations to high-market-share systems (Outlook, Gmail explicitly named) · No implementation fee for 12-month commitment · Digital proposals < 10 pages with live links · Worksheet-based input process for automated proposals.

### Craig's load-bearing call observation

> *"Development time is less dependent on the type of associate, and more on the integrations required. GIC was 90% integration work."*

This is the lens for the framework — **integrations are the cost driver, not the associate "concept."** Pricing flows from the integrations and skills, with the associate being the customer-facing brand wrapper.

---

## 2. The formula

**For a customer deal, implementation cost decomposes:**

```
Implementation cost = (total channel integration cost)
                    + (total skill development cost)
                    + (total system integration cost)
```

**Definitions:**

- **Skills** — reusable units of capability. What the associate can *do*. E.g., "categorize an inbound email", "create a quote in an AMS", "answer a policy question from a knowledge base". A skill is a skill — not bound to a specific channel or system.
- **Channels** — how the associate is triggered / communicates. Email, web chat, voice (in / out), SMS, Teams, Slack. An associate can run on multiple channels at once. Each additional channel adds smaller implementation time.
- **Systems** — external systems the associate needs to integrate with. AMS, PMS, CRM, carrier portal. Each has an **integration type** (web operator, API, other) that affects cost. Has this system been integrated before is a key question.
- **Associate** — a named bundle that **has** multiple skills, **can be reached via** multiple channels, **can integrate with** many systems. The customer-facing concept (Care Associate, Renewal Associate, Intake Associate for AMS, etc.).

**Channels and systems live at the DEAL level — not bound to individual skills.** Multiple skills share the same channel + system integrations on a given customer. So at GIC, the Unisoft integration is paid once and used by every skill that touches Unisoft (categorize, extract, link, create-quote, create-activity…). Same for the Outlook channel.

**LOE scoping rule:**

- For things **already developed** for a customer → use actual hours (Craig's recall + repo / git history).
- For things **needed but not yet built** for any customer → estimate first-customer LOE. *Example: outbound voice calls.* Care Associate (Proactive Client Communication) calls for outbound voice; we don't have any customer using outbound voice today; so we scope a first-customer-build LOE for outbound voice channel.

**Two skill types (Craig 2026-04-30):**

| Type | What it is | Reuse profile |
|---|---|---|
| **Tool skill** | Discrete capability the agent invokes like a function call. Atomic: invoke it, get a result. Examples: KB retrieval, data classification, policy status lookup, class code verification, human handoff. May be backed by a system integration but exposed as a discrete callable to the agent. | High — once built, drops into any associate / customer with minimal config |
| **Pathway skill** | End-to-end workflow that orchestrates multiple steps, decisions, and tool-skill calls. Customer-specific customization but transferable. Examples: ECM CAP renewal, Application submission into AMS, Workers Comp appetite verification. | Medium — most of the workflow transfers, but needs customer-specific customization |

**Implicit-in-integration carve-out:** capabilities like *navigate*, *read fields*, *write fields*, *retrieve documents* are NOT tool skills. They're implicit in the **system integration's TYPE** (web operator brings `navigate / read / write / retrieve` for free; API brings whatever endpoints exist). Pathways USE these capabilities through the integration; they don't separately invoke them.

A pathway skill is composed FROM tool skills + system-integration capabilities + customer-specific logic. So when costing a new customer:
- Reuse all the tool skills they need that already exist (cheap)
- Build any missing tool skills (medium)
- Customize / clone the relevant pathway skills for their context (most of the per-customer effort)

**Skill specificity (emergent, not pre-baked):**

A pathway is specific along whatever dimension makes its work materially different — LOB, carrier, workflow type (renewal/endorsement/quote), system, customer-specific business rule. Skill names encode their scope. No pre-baked specificity column.

Examples (factual):
- Johnson — `ECM Commercial Auto Policy renewal automation` is specific along (carrier=ECM × LOB=CAP × workflow=renewal). Pathway.
- Fred at GIC — `Workers Comp appetite verification` is specific to WC because the underlying logic (mod, NCCI hazard groups) is WC-shaped. Pathway.
- Generic — `Human handoff escalation` carries no scope — same tool skill across associates / channels / customers.

**Reuse story (caveat — not OS today):**

- Channels & systems built for one customer SHOULD lower cost for the next customer using the same channel/system, but this is only true insofar as the implementation is structured for reuse. Today most integrations are partly per-customer-custom (e.g., gic-email-intelligence is its own repo with its own Unisoft proxy; not all integrations are on the OS yet). Reuse story is directional, not guaranteed; we'll mark each integration with its actual reuse status.

## 2.05 Catalog gaps surfaced (to add to Cam's sheet — running list)

As we walk customers, the per-customer findings surface gaps in Cam's existing 47-row catalog. **Per Craig: better to call these out and add them than try to force-fit.** Track here, propagate to Cam's sheet at end.

| Gap | Where surfaced | Description |
|---|---|---|
| **Lead Associate — MGA tier** | JM (Mobile Home), UG (Mobile Home), Branch (Carson/Caroline) | Lead Associate exists in Cam's Agency/Broker tier ($0.50/ticket — "24/7 Lead Engagement & Qualification") but NOT in MGA tier. Multiple MGA customers do lead capture / quote display work. Add MGA row. |
| **Quote & Bind Associate — Agency/Broker tier** | Silent Sport (if/when binding gets added) | Agency/Broker tier has no Quote/Quote & Bind/Growth row. Silent Sport's quote display currently folds under Lead Associate; binding flow would surface this gap. |
| **Document Fulfillment Associate (or expanded sub-pathway)** | Branch (Aria) | Aria does document fulfillment — verify identity (incl. 3rd-party authorization) → generate doc → send via SMS/email → manage authorized recipients. Different from Knowledge Associate (Q&A only) and from the document generation tool skill (which is the *creation* of docs; this adds authorization + delivery flow). Could be its own associate or a formalized sub-pathway under Inquiry Associate. |
| **Claims Status Associate (or expanded Intake-for-Claims)** | Branch (Colleen) | Colleen does claims STATUS (lookup, adjuster contact, status email, callback request). Cam catalog has Intake Associate for Claims (FNOL) but no claims-status row. Either expand Intake-for-Claims description to cover both intake AND status, or add a separate Claims Status Associate. |

## 2.1 Tying back to Cam's sheet

The customer walk-through hydrates Cam's existing 47-row associate catalog:

- Each row gets a **Developed status** flag — `developed` (in production at ≥1 customer) / `partially developed` (some skills/channels/systems built, others not) / `not developed yet`
- Each row links to **customers active** — list of customers where this associate (or close-to-it) is deployed
- Each row inherits **skills, channels, systems** from the customer deployments

By the end of the walk, the rows that are `developed` for at least one customer are the strongest candidates for Cam's Core productization (per the Cam call: "look at which associates are most frequently deployed together"). Rows that are `not developed yet` need scoped LOE if they're going to be sold.

## 2.2 Crawl / walk / run

Per Craig — this is **how we communicate phasing to a customer**: what we deliver **immediately**, **near term**, and **long term**. Not an integration-depth concept. Example from GIC's Jan 30 proposal: Phase 1 (weeks 1-6) Email Triage = immediately; Phase 2 (ongoing 2026) Voice + Spanish + FNOL = near term; Conversational Quote Generation = long term.

---

## 3. Process for the customer walk-through

The walk-through is **interactive and adaptive** — not a rigid pipeline. Different customers have information in different places. The pattern is:

> Look at what we have on this customer → understand what was promised vs delivered → infer the skills/channels/systems → check classification with Craig → fold findings into catalogs.

### Sources to check per customer

| # | Source | What it reveals | Access |
|---|---|---|---|
| 1 | **OS entity graph** (`indemn` CLI / dev OS) | Company, Deals, Proposals, Documents, Touchpoints, Emails, Meetings, Operations, Opportunities. The index of what to look at next | `indemn company list` → entity navigation |
| 2 | **Google Drive — Cam's proposal portfolio + Kyle/Cam shared folder** | What was sold (the proposal docs). Folders: `1k0_SYLdYtlM40y6W-ZAMV3Trr9hIq2Ph`, `1KKH8juzCqVyRQ36h72nnB9Djdjy8m_j1` | `gog drive search` / `gog docs cat` |
| 3 | **MongoDB tiledesk DB** | What was BUILT in the V1 copilot dashboard — `bot_configurations` (web + voice agents), `faq_kbs` (knowledge bases), function definitions | `mongosh-connect.sh dev tiledesk` |
| 4 | **GitHub** (`indemn-ai/*`) | Custom code, integration adapters, customer-specific scripts, branch names with customer references | `gh search code "<Customer>"`, `gh repo list` |
| 5 | **Slack — customer-implementation channel + per-customer channels** | Weekly customer updates posted by the team. Free-text record of what's actively being built/shipped/blocked per customer | Main: `#customer-implementation` (`C06PBJSAGN6`). Per-customer (where they exist): `#customer-gic`, `#indemn-gic_underwriters`, `#indemn-insurica`, `#indemn-rankin`, `#indemn-rankin-daily-reporting`. More may surface as we walk. |

**Note:** Email + Meeting content for customers is already ingested into the OS (Gmail adapter shipped Apr 23, Meet adapter shipped Apr 21). Per-customer Touchpoints carry the source content. So § 1 already includes what we'd otherwise pull from Gmail/Meet — no separate query needed.

### Adaptive use of sources

Not all 5 sources are needed for every customer. Calibration:

- **Deeply-built customers** (GIC, Branch, Johnson, Union General): all 5 sources, methodically.
- **Lighter customers** (Knowledge-Associate-only, web chat-only): probably 2-3 sources (OS + Mongo + Drive proposal).
- **Unsigned but built-for** (Silent Sports type): may have minimal proposal but real Mongo + maybe GitHub work.

The walk-through is a conversation: I pull what looks promising, report what I see, you point to what else to dig into, we converge on the truth together.

### Per-customer template (what gets written into § 8)

```
### <Customer Name>

**OS entity refs:** Company `<id>`, Deals `[ids]`, Proposal `<id>`, Touchpoint count `<N>`
**Sources reviewed:** [Drive doc IDs, Mongo bot IDs, GitHub commits/repos, Slack msg refs]

**What was sold (from proposal):**
- Associate A — what was promised (cite proposal section)
- Associate B — what was promised

**What we actually built:**
| Skill | Trigger | Task | Output | Channel | System | LOE | Reusable? |
|---|---|---|---|---|---|---|---|
| Skill 1 | ... | ... | ... | ... | ... | ... | Y/N |

**Channels active for this customer:** [list]

**Systems active for this customer:** [list]

**Skills active for this customer (per Craig's framework, NOT per code-file count):**
- [list — surfaced in research, confirmed with Craig]

**Skill → Associate rollup (confirmed with Craig):**
- [list]

**Open items / pending:**
- [research still to do, decisions still to make]
```

### How findings flow into catalogs

As we walk customers, every new channel, system, or skill discovered is **added immediately to §§ 5, 6, 7** below. By customer 3-4 we should be cross-referencing existing catalog entries instead of duplicating, and the catalog tabs become the source of truth.

### Working pattern (corrected after Craig pushback 2026-04-30)

I research → surface findings → **discuss with Craig** → only write to doc what's been agreed. No willy-nilly authoring. No LOE estimates I can't ground. No reusability or Core/Soon/Enterprise tier claims. No invented frameworks (e.g., crawl/walk/run) that don't match how Indemn actually talks. Skills are not channel/system-scoped (Craig: "the whole point is the skill is reusable and not scoped to a channel or system").

### What's mine vs Craig's

| | Mine | Craig's |
|---|---|---|
| What was sold per customer | ✅ Pull proposal | — |
| What was built per customer (factual) | ✅ Pull from repo / OS / Mongo / Slack | — |
| Channel + system identification (factual) | ✅ Surface evidence | — |
| Skill identification (per Craig's framework, not file-count) | Surface candidates from research | ✅ Confirms what is/isn't a skill |
| Skill → Associate rollup | Propose | ✅ Confirms |
| LOE / cost / reusability / Core eligibility / crawl-walk-run | — | ✅ Craig owns. I do not author. |

---

## 4. End-state — what Cam's spreadsheet looks like when we're done

Six tabs. Per the corrected model: skills are reusable units, channels and systems live at the deal level. Implementation cost = channels + skills + systems (separate cost terms).

### Tab 1 — Associates (Cam's existing tab, augmented)

Same row count, same keying (Customer Type × Associate Name). Add columns:

| Column | What it holds |
|---|---|
| Skill IDs | References to rows in the Skills tab — the skills that make up this associate |
| Developed status | `developed` / `partially developed` / `not developed yet` |
| Customers active | List of current customers running this associate (or close to it) |
| Qualifying questions | Sales-side questions to scope this associate (carries forward existing Working Copy notes) |

Existing pricing + days-to-deploy columns stay; we revisit them after the walk if useful.

### Tab 2 — Skills (NEW)

One row per reusable skill.

| Column | What it holds |
|---|---|
| Skill ID | Stable handle |
| Skill Name | Human-readable (e.g., "Categorize inbound email", "Create quote in AMS", "Answer policy question from KB") |
| Description | What the skill does |
| Parent Associate(s) | Which associate(s) on Tab 1 this skill rolls up to |
| LOE to develop | Hours (actual where built; estimated for not-yet-built) |
| Status | `built` / `template` / `not built` |
| Customers active | List of customers running this skill |

### Tab 3 — Channel integrations (NEW)

One row per channel.

| Column | What it holds |
|---|---|
| Channel | "Web chat (Indemn-hosted)", "Email — Outlook (Microsoft Graph)", "Email — Gmail", "Voice — inbound", "Voice — outbound", "SMS", "Teams", "Slack", etc. |
| Status | `built` / `partial` / `not built` |
| LOE first-customer build | Hours (actual where built; estimated for not-yet-built — e.g., outbound voice) |
| Implementation notes | Adapter approach, dependencies |
| Customers active | List |

### Tab 4 — System integrations (NEW)

One row per external system.

| Column | What it holds |
|---|---|
| System | "Unisoft Communications AMS", "Applied Epic", "Hawksoft", "BT Core", "Easy Links", "GIC PAS", "Dialpad", "Stripe", etc. |
| Integration type | `web operator` / `API` / `other` |
| Status | `built` / `partial` / `not built` |
| LOE first-customer build | Hours (actual where built; estimated for not-yet-built) |
| Implementation notes | Auth model, gotchas (e.g., Unisoft = Windows EC2 web automation, not API) |
| Customers active | List |

### Tab 5 — Customer / Deal map (NEW)

One row per current customer.

| Column | What it holds |
|---|---|
| Customer | Name |
| Cohort | Core_Platform / Graduating / AI_Investments / Prospect-with-build |
| Type | Agency/Broker / Carrier / MGA |
| Associates active | List (refs Tab 1) |
| Skills active | List (refs Tab 2) |
| Channels integrated | List (refs Tab 3) |
| Systems integrated | List (refs Tab 4) |
| Crawl/walk/run | What's delivered now / near term / long term per the customer's proposal |
| Notes | Anything else |

### Tab 6 — Craig|Kyle Working Copy

Existing tab, kept as-is.

### Migration to Cam's sheet

Don't touch Cam's main tab during the work. Build per-customer findings + catalogs in this doc. At the end, produce a migration spec for Cam to review before any cells are touched.

---

## 5. Channels catalog `[seeded from GIC; LOE empty until Craig provides]`

| Channel | Status | LOE first build | Implementation notes | Customers active |
|---|---|---|---|---|
| Web chat (Indemn Copilot) | built | — | V1 platform hosted (`copilot-server` + `point-of-sale` widget) | GIC, INSURICA, JM, UG |
| Email — Outlook (Microsoft Graph) | built | — | OAuth via MS Graph; in `gic-email-intelligence` (custom app); also Composio at UG | GIC, UG |
| Email — outbound | built | — | Used for outbound campaigns (e.g., renewal cadence). Different from email *inbound* (read incoming mailboxes) | INSURICA |
| Voice — inbound | built | — | Backed by Twilio (telephony) + LiveKit (SIP/dispatch) + Cartesia (TTS) + Google Cloud Translate. INSURICA voice agents in production; JM Dahlia voice in production; GIC Fred prototype | INSURICA, JM, GIC (prototype) |
| Voice — outbound | not built | — | Planned for INSURICA renewal cadence (Kyle Apr 23 flag) | INSURICA (planned) |
| SMS | built | — | Backed by Twilio. INSURICA renewal cadence (D15); JM quote delivery via SendQuoteSMS | INSURICA, JM |
| Schedule | built | — | Trigger by cadence (e.g., scan ECM portal periodically). Used by back-end automation associates with no customer-facing channel | Johnson |
| Microsoft Teams (outbound notification) | built | — | Output channel for escalation notifications via Microsoft Power Automate (Azure Logic Apps) | DP |

## 6. Systems catalog `[seeded from GIC; LOE empty until Craig provides]`

Per Craig 2026-04-30: integration type is one of **`API`** or **`web operator`** (at this point — more types may emerge).

| System | Integration type | Status | Implementation notes | Customers active |
|---|---|---|---|---|
| Granada Insurance API | API | built | OAuth (Basic auth → token + refresh, cached in Redis); UAT endpoint; via Indemn `operations_api` proxy at `https://ops.indemn.ai/v1/gic/policyDetails` | GIC |
| Indemn Copilot | Internal platform (V1) | built | Hosts agent config + KB + execution. Listed by Craig as a system for Placement Associate + Fred | GIC, others (will fill as we walk) |
| Unisoft Communications AMS | web operator | built | Windows EC2 proxy for Unisoft web automation; no public API | GIC |
| Class-code verifier (Fred) | TBD | — | `verifyClassCode` REST tool; upstream identity unknown to Craig | GIC (prototype) |
| Applied Epic AMS | web operator | built | Web operator framework (`indemn-ai/web-operators` repo) using LangGraph + agent-browser. Per the Johnson proposal: "Applied Epic does not offer API access for this specific function" — so web operator is the path for the Renewal/Endorsement Intake work. Other customers may interact via API for different functions | Johnson |
| ECM Portal (Everett Cash Mutual) | web operator | built | Document retrieval (renewals + endorsements, ~50 docs/wk for Johnson). Web operator framework | Johnson |
| Salesforce | API | built | OAuth2 client_credentials grant (sandbox + prod variants per env). Records: `Renewal_Disposition_Event__c`, `AI_Outreach__c`, `Chat_Session__c`, Tasks (renewals); `IndemnAiAgentChatResponse` apex endpoint (Medicare Part D submissions). INSURICA's CRM. | INSURICA |
| Nationwide E&S/Specialty — Personal Lines | API | built | Wrapped via `ug-apis` (FastAPI). Quote-to-policy lifecycle for HO3/4/5/6 + DP1/2/3. Endpoints: `/reference/address/validate`, `/quotes/homeowners`, `/quotes/dwelling-fire`, `/quotes/{id}`, `/quotes/convert-to-issue`, `/policies/issue`, `/policies/documents` | UG |
| Nationwide E&S/Specialty — Commercial Lines | API | built | Wrapped via `ug-apis` (FastAPI). Used by GL workflow as `NATIONWIDE_CL` quote provider | UG |
| ACIC (American Carrier Insurance Company) | API | built | Wrapped via `ug-apis` (FastAPI) — `aci_routers`, `aci_service.py`, `aci_models.py`. UG's primary live carrier per OS notes ("GL only with ACIC"). Used by GL workflow | UG |
| Northfield Insurance | API | built | Used by GL workflow as `NORTHFIELD` quote provider. (Implementation location TBD — possibly via ug-apis or direct) | UG |
| Composio | API (3rd party) | built | Multi-provider unified email integration (Gmail + Outlook). Webhook-driven (`/webhooks/composio`). 2 active Outlook triggers polling INBOX every 1 min via `OUTLOOK_MESSAGE_TRIGGER`. | UG |
| Airtable (UG-Fields, Multiple Driver Info bases) | API (3rd party) | built | Per-record reads. Used by UG `API test` agent (likely scaffolding for production agents) | UG |
| n8n.indemn.ai | API (internal) | built | Workflow automation platform hosting webhook integrations. Bot rest_api tools call n8n webhooks (e.g. `https://n8n.indemn.ai/webhook/product-lookup` for USLI/Kinsale carrier lookups). n8n then calls the external carrier APIs. | UG (and likely others — to confirm as we walk) |
| ug-service ("AA surface automation") | API (internal) | built | Express service. `GET /record?recordId=...&status=...` upserts a record and returns "sent to AA for surface automation pickup." Downstream system "AA" identity TBD per Craig | UG |
| Indemn intake-manager (`ug_submission` MongoDB) | Internal datastore + service | built | Custom 630MB MongoDB DB backing the intake-manager pipeline. 18 collections including `submission_data`, `submission_states`, `quotes`, `quote_documents`, `cl_class_code`, `form_schemas`, `workflows_config`, `email_triggers`. | UG |
| Airtable (Indemn-managed quote/config tables) | API (3rd party) | built | When a customer doesn't own a system to host their quote configs, we manage the data in **our** Airtable base and sync to MongoDB. The `conversation-service` queries `airtable_sync.quote_details` (replicated from Airtable via `pyairtable`). Used for JM ring engagement + EventGuard event insurance quote configs. Per-bot `airtable_config` with `base_id` + `table_id` in `bot_configurations`. | JM (and other B2C customers — to confirm as we walk) |
| Twilio | API (3rd party) | built | Phone number provisioning, SIP trunks (via `voice-service` repo with `twilio` SDK), SMS dispatch. Backs `voice.indemn.ai/sms` (SendQuoteSMS for JM) and inbound voice telephony for all voice agents | JM, INSURICA, GIC (Fred prototype) |
| LiveKit | API (3rd party) | built | Voice dispatch / SIP routing (via `livekit-server-sdk`). The `voice-livekit` EC2 instance (g4dn.xlarge GPU) runs LiveKit infrastructure | JM, INSURICA, GIC (Fred prototype) |
| Cartesia | API (3rd party) | built | Text-to-speech for voice agents (via `voice-service`) | JM, INSURICA, GIC (Fred prototype) |
| Google Cloud Translate | API (3rd party) | built | Language detection / translation (via `voice-service` `@google-cloud/translate`) | JM, INSURICA (used for Spanish handling) |
| Stripe | API (3rd party) | built | Payment processing for B2C purchases via `point-of-sale` chat widget (JM EventGuard); voice-channel payment via Sophie (Branch — prototype) | JM, Branch (prototype) |
| Branch GraphQL API | API | built | `staging.v2.api.ourbranch.com` — Branch's own insurance API. Used by Carson/Caroline (Sales) for `convertQuote`, `collectDriverInformation2`, `collectPriorAuto2`. The "real-time price" path in the Branch proposal | Branch (prototype) |
| Dialpad (Branch's IVR + gated URL provider) | Phone / API | external dependency | Upstream IVR system at Branch. Authenticates callers, emits `auth` + `master_id` to Petra session context. Gated-URL handshake for document delivery (used by Petra v2). | Branch (prototype) |
| claims-mcp-server (Indemn-built for Branch) | API (Indemn-hosted, GraphQL) | built | `claims-mcp-server.up.railway.app/graphql` — Branch claims data layer built by Indemn. Endpoints: validatePolicyholder, verifyPolicyLast4, validateThirdPartyAuthorization, lookupClaimStatus, getThirdPartyClaimStatus, sendStatusEmail, sendThirdPartyEmail, requestCallback. Used by Colleen | Branch (prototype) |
| branch-ivr-webhook (Indemn-built for Branch) | API (Indemn-hosted, REST) | built | `branch-ivr-webhook-production.up.railway.app` — Branch member/policy/staff lookup. Endpoints: `/api/member/{id}`, `/api/policy/{number}`, `/api/staff/by-name`. Used by Petra | Branch (prototype) |
| branch-aria-documents (Indemn-built for Branch) | API (Indemn-hosted, REST) | built | `branch-aria-documents-production.up.railway.app` — ARIA document generation + delivery service. Endpoints: `/api/documents/generate`, `/api/documents/send`, plus Dialpad gated-URL handshake at `/api/dialpad/document-link`, `/api/dialpad/send-sms`, `/api/dialpad/supplemental-auth`. Used by Aria + Petra | Branch (prototype) |
| Microsoft Power Automate / Azure Logic Apps | API (3rd party) | built | Used by DP for Microsoft Teams notification dispatch. Webhook URL pattern `prod-13.westus.logic.azure.com/.../workflows/{id}/triggers/manual/paths/invoke` | DP |

## 7. Skills catalog `[seeded from GIC + Johnson; LOE empty until Craig provides]`

### Tool skills (atomic capabilities, high reuse)

| Skill ID | Skill Name | Used by | Status | Customers active |
|---|---|---|---|---|
| tool-001 | Human handoff escalation | Placement · WC Voice · Renewal · Front Desk · most associates | built | GIC, Johnson, INSURICA |
| tool-002 | Data classification (email) | Quote Intake Associate for AMS | built | GIC |
| tool-003 | Data extraction (PDF→structured, includes OCR) | Quote Intake for AMS · ECM paths | built | GIC, Johnson |
| tool-004 | Policy status retrieval (atomic API call to Granada) | Placement Associate | built | GIC |
| tool-005 | KB retrieval | Placement · WC Voice · Renewal · Front Desk · likely many | built | GIC, INSURICA |
| tool-006 | Class code verification (NCCI lookup) | Workers Comp Voice | built (prototype) | GIC (prototype) |
| tool-007 | Slack/Teams alert dispatch | ECM paths (Johnson) | built | Johnson |
| tool-008 | Salesforce CRM read (atomic record/object lookup) | Renewal Associate | built | INSURICA |
| tool-009 | Salesforce CRM write (atomic record create/update) | Renewal Associate · Medicare Part D Navigator | built | INSURICA |
| tool-010 | Trace event emission (observability) | Renewal Associate | built | INSURICA |
| tool-011 | Outbound voice dispatch | Renewal Associate (planned) | not built | INSURICA (planned) |
| tool-012 | Outbound email dispatch | Renewal Associate | built | INSURICA |
| tool-013 | Certificate request submission | Front Desk Associate | built | INSURICA |
| tool-014 | Nationwide PL quote create (HO + DP forms) | Intake+Market combined | built | UG |
| tool-015 | Nationwide CL quote create | Intake+Market combined | built | UG |
| tool-016 | ACIC quote create | Intake+Market combined | built | UG |
| tool-017 | Northfield quote create | Intake+Market combined | built | UG |
| tool-018 | Address validation + GIS lookup | Intake+Market combined | built | UG |
| tool-019 | Policy issue (carrier-agnostic via ug-apis) | Intake+Market combined | built | UG |
| tool-020 | Policy document retrieval | Intake+Market combined | built | UG |
| tool-021 | Composio email ingestion (Gmail + Outlook unified webhook) | Intake+Market combined | built | UG |
| tool-022 | Class code matching (CL) | Intake+Market combined | built | UG |
| tool-023 | UW parameter violation mapping (validation) | Intake+Market combined | built | UG |
| tool-024 | Quote comparison across carriers | Intake+Market combined | built | UG |
| tool-025 | Producer intake form capture | Onboarding Associate | built | UG (WIP) |
| tool-026 | Surface automation record routing (ug-service `/record`) | Multiple — TBD | built | UG |
| tool-027 | Carrier app URL lookup (USLI / Kinsale via n8n.indemn.ai webhook) | Knowledge Associate | built | UG |
| tool-028 | Airtable record fetch (UG-Fields, Multiple Driver Info) | (test scaffolding) | built | UG (test agent) |
| tool-029 | Ring engagement quote generation (Airtable-backed via conversation-service) | Quote & Bind Associate | built | JM |
| tool-030 | Event insurance quote generation (Airtable-backed via conversation-service; multi-param: state, budget, alcohol, host_type, package, mandates) | Quote & Bind Associate | built | JM (EventGuard) |
| tool-031 | SMS quote delivery (via Twilio through voice-service) | Quote & Bind Associate | built | JM |
| tool-032 | Coverage options preview (broad cost ranges before specific quote) | Quote & Bind Associate | built | JM |
| tool-033 | Voice call transfer to human (via Twilio + LiveKit through voice-service) | Quote & Bind · Renewal · Workers Comp Voice · most voice agents | built | JM, INSURICA, GIC (prototype) |
| tool-034 | Stripe payment processing (B2C purchase flow via point-of-sale widget) | Quote & Bind Associate | built | JM (EventGuard) |
| tool-035 | mckay product quote display (Airtable-backed pre-built options; pilot only — not driving real Silent Sport traffic) | Lead Associate (Silent Sport variant) | built (pilot) | Silent Sport (pilot) |
| tool-036 | Quote PDF generation (quote summaries / comparison docs) | Intake+Market combined | built | UG (intake-manager `quote_documents` model + frontend `quote-pdf.ts` + quote-comparison UI; 40 quote_documents in production) |
| tool-037 | Accord 25 certificate generation (Certificate of Insurance, post-bind) `[NOT YET BUILT — proposed for Silent Sport CRAWL phase; Craig flag: capability we should formalize as a shared skill]` | TBD — would augment Intake / Quote&Bind / Renewal associates | not built | Silent Sport (planned, would be first), reusable for INSURICA COIs / UG decline letters / others |
| tool-038 | Document generation capability area `[Craig flag — formalize as shared platform skill]` — covers quote PDFs (built), Accord 25 certs (not built), premium disclosures (not built), member certificates (not built), decline letters (not built) | Cross-cutting (any associate that produces customer-facing or operational documents) | mixed | UG (quote PDFs only) |
| tool-039 | Intent classification (multi-pass: keyword → context → ambiguity resolution; routes caller utterance to one of N MS-pathway categories) | Member Services Associate | built (prototype) | Branch (Petra) |
| tool-040 | Member/policy/staff lookup (Branch IVR webhook) | Member Services Associate | built (prototype) | Branch |
| tool-041 | Claims data lookup (validate policyholder/3rd party, lookup claim status, adjuster contact, send status email, request callback) | Member Services Associate (Claims Status sub-pathway) | built (prototype) | Branch (Colleen via claims-mcp-server) |
| tool-042 | Document fulfillment (verify policyholder/3rd-party authorization, list available docs, generate + send via SMS/email, manage authorized recipients) | Member Services Associate (Document Fulfillment sub-pathway) | built (prototype) | Branch (Aria via branch-aria-documents) |
| tool-043 | Dialpad gated-URL document delivery handshake (request gated URL, send via SMS, supplemental auth, capture CSAT) | Member Services Associate (Document Fulfillment sub-pathway) | built (prototype, Petra v2) | Branch |
| tool-044 | Branch quote generation + error-handling collection (convertQuote → if 4000 collect driver info → if 5003 collect prior auto info → storeQuote) | Sales / Lead Associate | built (prototype) | Branch (Carson, Caroline, branch quote assist via Branch GraphQL API) |
| tool-045 | Customer profile collection — minimal home/auto intake (full name, address) | Sales / Lead Associate | built (prototype) | Branch (Carson, Caroline) |
| tool-046 | DP product lookup (Airtable-backed via n8n webhook) | Knowledge Associate (DP) | built | DP |
| tool-047 | DP capabilities lookup (product-flow, sub-capabilities, system interactions across IMS/Salesforce/Portal/Arch/Jarus/Tinubu — Airtable-backed via n8n) | Knowledge Associate (DP) | built | DP |
| tool-048 | Microsoft Teams notification dispatch (via Power Automate Logic App) | Knowledge Associate (DP) | built | DP |

### Pathway skills (end-to-end workflows, medium reuse)

| Skill ID | Skill Name | Parent Associate | Status | Customers active |
|---|---|---|---|---|
| path-001 | Broker portal Q&A interaction | Placement Associate | built | GIC |
| path-002 | Policy lookup workflow (with error handling) | Placement Associate | built | GIC |
| path-003 | Application submission into AMS | Quote Intake Associate for AMS | built | GIC |
| path-004 | Carrier quote submission into AMS | Quote Intake Associate for AMS | pending | GIC (planned) |
| path-005 | Workers Comp application validation and qualification | Workers Comp Voice Agent | built (prototype) | GIC (prototype) |
| path-006 | Workers Comp appetite verification | Workers Comp Voice Agent | built (prototype) | GIC (prototype) |
| path-007 | Workers Comp submission checklist generation `[?]` | Workers Comp Voice Agent | built (prototype) | GIC (prototype) |
| path-008 | ECM Commercial Auto Policy renewal automation | Intake Associate for AMS (Renewal/Endorsement variant) | built | Johnson |
| path-009 | ECM Commercial Auto Policy endorsement automation | Intake Associate for AMS (Renewal/Endorsement variant) | built | Johnson |
| path-010 | ECM CHG3 endorsement automation | Intake Associate for AMS (Renewal/Endorsement variant) | built | Johnson |
| path-011 | ECM Farmowners Policy renewal automation | Intake Associate for AMS (Renewal/Endorsement variant) | built | Johnson |
| path-012 | Renewal outreach + data collection (multi-channel cadence) | Renewal Associate | built | INSURICA |
| path-013 | Renewal escalation handling | Renewal Associate | built | INSURICA |
| path-014 | ACORD 25 certificate request intake + submission | Front Desk Associate | built | INSURICA |
| path-015 | Medicare Part D enrollment qualification + intake | Medicare Part D Navigator (unique product — not in Cam catalog) | built | INSURICA |
| path-016 | Multi-carrier UW knowledge Q&A (Augi super agent across 7 carriers) | Knowledge Associate (UG variant) | built | UG |
| path-017 | Per-carrier UW knowledge Q&A (USLI · Kinsale · Northfield · ACIC · Scottsdale · Seneca · SIC scoped) | Knowledge Associate (UG variant) | built | UG |
| path-018 | Northland trucking UW knowledge Q&A | Knowledge Associate (UG variant) | built | UG |
| path-019 | Homeowners + Dwelling Fire intake → Nationwide PL quote | Intake+Market combined (UG variant) | built | UG |
| path-020 | General Liability intake → 3-carrier comparative quote (ACIC + Nationwide CL + Northfield) | Intake+Market combined (UG variant) | built | UG |
| path-021 | Northland trucking intake (ACORD 130 + DOT/MC/CDL extraction) | Intake+Market combined (UG variant) | built — workflow inactive | UG |
| path-022 | Mobile home product Q&A (4-state: NM/NV/AZ/Texas) | Knowledge Associate (UG variant) | built | UG |
| path-023 | Mobile home lead capture | Lead Associate (UG variant — **gap: not in Cam MGA tier**) | built | UG |
| path-024 | Producer/agency onboarding intake | Onboarding Associate (UG variant) | WIP | UG |
| path-025 | JM ring engagement quote+SMS (voice — Dahlia) | Quote & Bind Associate (JM variant) | built | JM |
| path-026 | JM ring engagement quote (webchat — faq bot + engagement focus v2) | Quote & Bind Associate (JM variant) | built | JM |
| path-027 | EventGuard event insurance quote+bind (point-of-sale on www-eventsguard-mga, with Stripe checkout) | Quote & Bind Associate (JM variant — EventGuard product) | built | JM |
| path-028 | Zola-embedded ring insurance education + handoff (Dahlia for Zola — voice) | Knowledge Associate · Lead Associate (JM variant — partner-embedded) | built | JM |
| path-029 | Personal vs Commercial jewelry routing (intake disambiguation) | Lead Associate (JM variant — implicit lead capture) | built | JM |
| path-030 | Jewelry/ring product Q&A | Knowledge Associate (JM variant) | built | JM |
| path-031 | Sports/recreation lead qualification + capture (pilot) | Lead Associate (Silent Sport variant) | built (pilot — not in real production traffic) | Silent Sport |
| path-032 | Silent Sports program Q&A (pilot) | Knowledge Associate (Silent Sport variant) | built (pilot — not in real production traffic) | Silent Sport |
| path-033 | IVR triage + intent recognition + routing (Petra) — answers coverage Q&A on-spine OR transfers to human queue (Sales/Claims/Service/AgencySupport) | Member Services Associate (Branch variant) | built (prototype) | Branch |
| path-034 | Document fulfillment (Aria — verify identity incl. 3rd party authorization → generate doc → send via SMS/email; v2 uses Dialpad gated-URL handshake) | Member Services Associate (Branch variant — Document Fulfillment sub-pathway) | built (prototype) | Branch |
| path-035 | Claims status lookup (Colleen — validate caller policyholder OR 3rd party, return claim status + adjuster contact + financials, optional email + callback) | Member Services Associate (Branch variant — Claims Status sub-pathway) | built (prototype) | Branch |
| path-036 | Voice-channel billing payment (Sophie — validates customer + processes Stripe payments) | Member Services Associate (Branch variant — Billing sub-pathway) | built (prototype) | Branch |
| path-037 | Voice quote display + lead capture for Home/Auto (Carson, Caroline — collect 2 data points → call Branch GraphQL → display quote → handoff to licensed agent) | Sales / Lead Associate (Branch variant) | built (prototype) | Branch |
| path-038 | Webchat quote display + lead capture | Sales / Lead Associate (Branch variant — webchat counterpart) | built (prototype) | Branch (branch quote assist) |
| path-039 | General DP product / program / capabilities Q&A | Knowledge Associate (DP variant) | built | DP |
| path-040 | Cyber Insurance program Q&A — voice (Melody) | Knowledge Associate (DP variant — Cyber specialization) | built | DP |
| path-041 | Cyber Insurance program Q&A — webchat | Knowledge Associate (DP variant — Cyber specialization) | built | DP |
| path-042 | Community Associations program Q&A | Knowledge Associate (DP variant — Community Associations specialization) | built | DP |
| path-043 | Submission portal navigation + BOR handling rules | Knowledge Associate (DP variant — submission portal specialization) | built | DP |
| path-044 | Personal Lines billing inquiry deflection (voice — Sandy) | Front Desk Associate (O'Connor variant) | built | O'Connor |
| path-045 | Commercial Lines billing inquiry deflection (voice — Coral/Gráinne) | Front Desk Associate (O'Connor variant) | built | O'Connor |
| path-046 | Website visitor education + lead capture (with strict no-quote/no-pricing boundaries) | Knowledge Associate (O'Connor variant) | built | O'Connor |
| path-047 | Staff-facing routine inquiry deflection (HR/benefits/PTO/employee handbook + internal insurance FAQs) | Ticket Associate (O'Connor variant) | built | O'Connor |

**Note:** browser automation, Applied Epic field write, and ECM portal navigation are NOT in this catalog — they're implicit capabilities of the `web operator` integration type (Tab 4). Pathways use them through the integration; not tracked as separate skills.

---

## 8. Customer walk-through

Customer list pulled from OS via `indemn company list` (Apr 30, session 14). The OS already segments customers by `cohort` field — uses three customer cohorts (Core_Platform, Graduating, AI_Investments) plus Prospect for non-customers. **20 active customers + a handful of relevant prospects with build history.**

Order: starting with **GIC** (deepest custom build, stress-tests the framework hardest), then proceeding by depth-of-build/ARR generally.

### 8.2 Jewelers Mutual (JM) `[in-progress — facts]`

**OS entity refs:** Company `69e41a7ab5699e1b9d7e98cf` · Cohort: Core_Platform · ARR $292.5K (largest) · Stage: customer · Type: MGA_MGU · Champion: **Dave Seibert** · Owner: Jonathan + Kyle · Domain `jewelersmutual.com`.
**Sources reviewed:** OS Company entity · MongoDB tiledesk via SSM (4 V1 platform agents · 9 tools · 10 KBs) · GitHub repos: `www-eventsguard-mga`, `point-of-sale`, `conversation-service`, `voice-service`, `copilot-sync-service` · prompts + tools (with URLs) for all 4 JM agents.

**Material context:** OS notes call JM "the anchor account" with EventGuard at "national scale = top priority." Real B2C revenue landing — example: EventGuard insurance purchase for $200 on 2026-04-21. **JM is fundamentally B2C / direct-to-consumer**, unlike GIC/UG/INSURICA (B2B internal underwriter tooling).

**Two distinct B2C products + one partnership:**

| Product | Surface | Data backend |
|---|---|---|
| **JM Ring Engagement Insurance** (jewelry — JM's traditional product) | Voice (Dahlia) + Web chat (engagement focus v2 / faq bot) | Airtable `quote_details` (synced to MongoDB) via conversation-service `/quote_suggestions/jm-ring-engagement` |
| **EventGuard event insurance** (one-day events / weddings) | Marketing site (`www-eventsguard-mga`, React/Vite + Material-UI + Contentful) with embedded `point-of-sale` chat widget; Stripe checkout | Airtable `multiple_quote_config` via conversation-service `/quote_suggestions` (multi-param: state, budget, alcohol_bool, host_type, package_config, cancellation/liability mandates) |
| **Zola partnership (channel embed)** | `Dahlia for Zola` voice agent — front-of-house only, no quote tool, hands off to enrollment | (handoff) |

#### Confirmed associates + skills + integrations for JM (Craig 2026-05-01)

**Quote & Bind Associate (MGA — JM variant; revised 2026-05-01 per task-bundling rule)**

The 3 main JM agents (Dahlia voice, faq bot, engagement focus v2) all do the SAME end-to-end task in one conversation: engagement + Q&A + lead capture (personal vs commercial routing) + quote generation + (for EventGuard) Stripe checkout. This is one Quote & Bind objective with Q&A and lead capture folded in as part of the flow. Plus the EventGuard point-of-sale widget on www-eventsguard-mga (web chat) does end-to-end quote+bind with Stripe payment.

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| JM ring engagement quote+SMS (voice — Dahlia) · JM ring engagement quote (webchat — faq bot, engagement focus v2) · EventGuard event insurance quote+bind (point-of-sale widget on www-eventsguard-mga; with Stripe checkout) · Personal vs Commercial jewelry routing (intake disambiguation, part of the flow) | KB retrieval · Ring engagement quote generation · Event insurance quote generation · SMS quote delivery · Coverage options preview · Voice call transfer · Stripe payment processing · Lead generation capture · Human handoff escalation | Voice (in/out — Dahlia voice agents) · Web chat (Indemn Copilot widget + point-of-sale embedded widget) · SMS (quote summary delivery) | **Airtable** (Indemn-managed; quote configs for JM ring + EventGuard) · **Twilio** (SMS + voice) · **LiveKit** (voice dispatch) · **Cartesia** (TTS) · **Google Cloud Translate** (Spanish detection) · **Stripe** (EventGuard payments) · Indemn Copilot |

**Knowledge Associate (MGA — JM variant; Zola partner-embedded)**

Distinct from Quote & Bind because the Dahlia for Zola voice agent has a fundamentally different objective: educate Zola couples about engagement ring insurance + handoff to enrollment. **No quote tool** — purely educational + handoff.

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| Zola-embedded engagement ring education + handoff to enrollment | KB retrieval · Voice call transfer | Voice (Dahlia for Zola) | Indemn Copilot · Twilio · LiveKit · Cartesia |

#### Notes for JM

- **Drive folder empty (or access blocked)** — `1UaZ59IlvdBdgdiLhYk8-DJtBm6zLpViy` returned 0 files. May warrant a separate access check.
- **conversation.indemn.ai is a shared Indemn platform component** — JM uses it for ring + EventGuard. Same backend serves Silent Sport (mckay), mShift, Zurich workflows. Customers benefit from this shared infrastructure but it's NOT a per-customer system; it's our platform.
- **Airtable as Indemn-managed quote backend** — JM doesn't have their own quote-config system, so we manage their rates/packages in our Airtable bases and serve via conversation-service. This is the "if customer doesn't have their own [system], count it as an Indemn system" pattern Craig described.
- **Voice stack 3rd parties confirmed:** Twilio (telephony + SMS) + LiveKit (voice routing on g4dn GPU EC2) + Cartesia (TTS) + Google Cloud Translate (language detection)
- **EventGuard is a separate product surface** with its own marketing site + embedded purchase flow. Not just a different pathway — it's a distinct domain (eventsguard) with its own go-to-market.
- **Zola partnership** — front-of-house only (no quote tool on Dahlia for Zola). Funnels to handoff for enrollment. We're not "running on Zola" or "hitting Zola" — just embedding our voice agent in their flow and handing off.

---

### 8.4 Union General Insurance Services (UG) `[in-progress — facts]`

**OS entity refs:** Company `69e41a7bb5699e1b9d7e98d1` · Cohort: Core_Platform · ARR $84K · Stage: customer · Type: MGA_MGU · Champion: **Ben Bailey** (Benjamen Bailey) · Owner: George + Jonathan · Domain `uniongeneralinsurance.com`.
**Sources reviewed:** OS Company entity · MongoDB tiledesk (18 V1 platform agents · 35 tools · 61 KBs) · MongoDB ug_submission db (630MB — intake-manager backend; 170 submissions, 246 quotes, 11.5K parameters, 946 attachments, 18 collections) · GitHub `indemn-ai/intake-manager`, `ug-apis`, `ug-service` · workflows_config in ug_submission.

**Material context:** "GL only with ACIC carrier" today; expansion to BOP, commercial auto, umbrella + multi-carrier API. Live products: GL Comparative Rater (multi-carrier UW knowledge) + Submission Command Center (intake-manager pipeline).

#### Confirmed associates + skills + integrations for UG (Craig 2026-05-01)

**Knowledge Associate (MGA — UG variant)**

The "GL Comparative Rater" — multi-carrier UW knowledge retrieval. Internal-staff facing. The actual quote comparison happens in the Intake+Market Associate (intake-manager) below; THIS associate is purely the UW-Q&A layer for underwriters/brokers consulting carrier guidelines.

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| Multi-carrier UW Q&A (Augi super agent across 7 carriers) · Per-carrier UW Q&A (USLI, Kinsale, Northfield, ACIC, Scottsdale, Seneca, SIC) · Northland trucking UW Q&A · Carrier app URL lookup | KB retrieval · Human handoff escalation · Carrier app URL lookup | Web chat | Indemn Copilot · n8n.indemn.ai (for carrier app URL webhooks like `https://n8n.indemn.ai/webhook/product-lookup`) |

**Intake Associate + Market Associate (MGA — combined; UG variant)**

The intake-manager (`ug_submission` MongoDB + `intake-manager` repo + `ug-apis` repo). Email-driven submission intake with multi-LOB workflows + multi-carrier comparative quoting. **Both Intake Associate (Submission Triage) and Market Associate (Market Access Optimization) work in one system** — Craig confirmed.

3 workflow_config records in `ug_submission.workflows_config`:

| Workflow | Active | LOB / forms matched | Quote providers | Validation |
|---|---|---|---|---|
| Homeowners + Dwelling Fire | ✅ | ACORD 80, 84; HO3/4/5/6, DP1/2/3 | NATIONWIDE | enabled |
| General Liability | ✅ | ACORD 125, 126; CGL, premises liability | **ACIC + NATIONWIDE_CL + NORTHFIELD** (auto-quote on valid; 3-carrier comparative) | disabled (LLM decision) |
| Northland Trucking | ❌ inactive | ACORD 130, motor carriers, fleet, CDL/DOT/MC | (no quote_config) | enabled |

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| Homeowners + Dwelling Fire intake → Nationwide PL quote · GL intake → 3-carrier comparative quote · Northland trucking intake (built but workflow inactive) | Composio email ingestion · Data extraction (PDF/OCR) · Class code matching · UW parameter violation mapping · Address validation + GIS · Nationwide PL quote create · Nationwide CL quote create · ACIC quote create · Northfield quote create · Policy issue · Policy document retrieval · Quote comparison · Slack/Teams alert dispatch · Surface automation record routing | Email — Outlook (Gmail + Outlook unified via Composio) · Web UI (Next.js frontend) · Slack outbound | Nationwide PL · Nationwide CL · ACIC · Northfield · Composio · ug-apis (internal proxy) · ug-service ("AA surface automation") · intake-manager MongoDB |

**Lead Associate (Mobile Home / SCC — UG variant; revised 2026-05-01 per task-bundling rule)**

One agent doing one conversational task: lead engagement + qualification, including product Q&A as part of engagement (Q&A folded into Lead Associate per Cam's "24/7 Lead Engagement & Qualification" definition).

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| Mobile home lead engagement + qualification + capture (4-state: NM/NV/AZ/Texas — includes product Q&A as part of engagement) | KB retrieval · Lead generation capture · Human handoff escalation · (2 unspecified `rest api` tools — TBD) | Web chat | Indemn Copilot · TBD (the rest_api endpoints) |

**Cam catalog gap:** Lead Associate is not in MGA tier — see §2.05. Tracked for resolution.

**Onboarding Associate (MGA — UG variant; WIP)**

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| Producer/agency onboarding intake | Producer intake form capture · Human handoff escalation | Web chat | Indemn Copilot |

The "Marketing" agent's prompt is meta-spec describing what to build (intake form for new agencies + background research) — not yet a polished production agent. WIP.

#### Other agents in tiledesk that are sub-pathways or test/legacy

- `voice agent #1` (1 KB, 1 tool — call transfer) — minimal voice front-end. Pathway TBD.
- `internal agent` (Union General Handbook KB, 0 tools) — internal-only handbook lookup
- `policy compass` (Policy Compass KB, 2 tools) — unclear product. Sub-pathway under Knowledge Associate likely
- `raw data reviewer` (Application screening KB) — sub-pathway under Intake+Market (validation step)
- `sic pl` (SIC PL KB) — sub-pathway under Knowledge Associate (Scottsdale Personal Lines variant)
- `nf/sic uw` · `clone test` · `api test` · `faq bot` — likely test/legacy/scaffolding
- `acic uw` · `northfield uw` (per-carrier specialist agents) — possibly earlier iterations of the Augi super agent; super agent has all 19 KBs and may have superseded the per-carrier agents. **Worth confirming if the per-carrier specialists are still in active use or legacy.**

#### Notes for UG

- **Northland trucking workflow (intake-manager) is BUILT but currently inactive.** Worth confirming if intentional or dormant — Craig said "trucking workflow scrapes data from emails AND interacts with their systems" which describes the intake-manager Northland workflow, but `is_active: False` in workflows_config.
- **GL workflow has the real comparative rater.** Auto-quote on valid against ACIC + NATIONWIDE_CL + NORTHFIELD in parallel.
- **n8n.indemn.ai discovered as a system layer** — bot rest_api tools call n8n webhooks which then call the actual external APIs. Likely used by other customers too (will confirm as we walk).
- **"AA surface automation"** identity TBD — ug-service routes records to it. Craig: "I have no idea."
- **Per-carrier specialist agents** (Northfield UW, ACIC UW, USLI, Kinsale, Scottsdale UW, NF/SIC UW) — possibly superseded by the Augi super agent. Confirm.

---

### 8.3 INSURICA `[in-progress — facts]`

**OS entity refs:** Company `69e41a7ab5699e1b9d7e98cd` · Cohort: Core_Platform · ARR $100K · Stage: customer · Type: Broker · AMS: Applied EPIC · Champion: **Kylie Hubbard** (current); **Julia Hester** (Director of Digital Revenue Growth, future voice work) · Domain `insuricaexpress.com`.
**Sources reviewed:** OS Company entity · MongoDB tiledesk via SSM (15 V1 platform agents · 92 tools · 19 KBs) · GitHub `indemn-ai/operations_api` (Salesforce submission code).

**Material context (per Kyle Apr 23 flag):** "INSURICA renewals need OUTBOUND calls + emails — this is a real upcoming need driving outbound product expansion."

#### Confirmed associates + skills + integrations for INSURICA

**Renewal Associate (Agency/Broker tier — production)**

15 V1 agents broadly; the renewals product = MARA orchestrator + 6 channel agents (web, email, voice, SMS + 2 demo bots). MARA = "Multi-channel Account Renewal Automation" — never talks to policyholders directly; coordinates the channel agents. Carries renewals through 6-attempt cadence, collects Julia Hester's 5 Key Data Points (address · contact_info · business_ops · exposure · gl_requirements), persists state across channels, manages disposition state machine, fires escalation gates (legal/BOR IMMEDIATE; classification/exposure/low-confidence escalate), syncs Salesforce.

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| Renewal outreach + data collection (multi-channel cadence) · Renewal escalation handling | KB retrieval · Human handoff escalation · Salesforce CRM read · Salesforce CRM write · Trace event emission · Outbound email dispatch · (planned) Outbound voice dispatch | Web chat · Email outbound · Voice (in/out) · SMS | Salesforce · Indemn Copilot |

MARA-internal tools (`LookupRenewalContext`, `EvaluateCompletionMap`, `AdvanceCadence`, `MarshalCrossChannelData`, `EvaluateDisposition`, `EvaluateEscalationGates`) are pathway business logic / orchestration internals — INSURICA-specific (Julia's 5 data points, INSURICA's cadence sequence, INSURICA's gates). Not separately tracked as tool skills.

**Front Desk Associate (Agency/Broker tier, $1,000/mo per Cam catalog — production)**

Certificate of Insurance request handling. Single-purpose: collect ACORD 25 certificate requests with strict scope (no coverage interpretation, no endorsement recommendations).

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| ACORD 25 certificate request intake + submission | KB retrieval · Human handoff escalation · Certificate request submission | Web chat · Voice | Indemn Copilot · TBD (wherever certificate_request submits) |

**Medicare Part D Navigator (UNIQUE product — not in Cam catalog, inventory only)**

Riley voice/web agent for Q4 open-enrollment Medicare Part D navigation. Helps callers determine eligibility (state exclusion check, Parts A&B verification), captures demographics + medication list, submits to INSURICA's Salesforce sandbox. Specialized speech-formatted prompt with SSML pacing for voice.

Per Craig: "if not [in catalog], then maybe its a unique product that we likely wouldn't build for someone else, but its good to include in the inventory."

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| Medicare Part D enrollment qualification + intake | KB retrieval · Human handoff escalation · Salesforce CRM write | Voice · Web chat | Salesforce |

#### Notes for INSURICA

- "Lifecycle proof point" framing in OS notes (per Craig: don't trust OS notes blindly, but the framing is useful) — INSURICA spans retention (Renewal) + service (Front Desk) + revenue (Medicare Part D as a niche) outcomes.
- Outbound voice dispatch is the next channel-tooling build — driven by INSURICA renewal work.
- MARA orchestrator pattern is interesting for the framework — **multi-channel single-associate** pattern. The same Renewal Associate runs on 4 channels via an orchestrator. We may see this pattern again at other customers.
- 2 legacy V1 agents (`test1`, `faq bot`) not included in the picture — likely deprecated.

---

### 8.7 Branch (Branch Financial, Inc.) `[in-progress — prototypes only, NOT in production]`

**OS entity refs:** Company `69e41a7bb5699e1b9d7e98d3` · Cohort: Graduating · ARR $24K · Stage: pilot · Type: MGA_MGU · Champion: **Dan Spiegel** (VP, Marketing & Member Experience) · Domain `ourbranch.com`. Trial since Mar 13, 2026 ($2K/mo for 90 days). Expansion target $138K full enterprise.
**Sources reviewed:** OS Company entity · MongoDB tiledesk via SSM (9 V1 platform agents · 79 tools · 9 KBs) · GitHub (Branch's GraphQL API at `staging.v2.api.ourbranch.com`, multiple Indemn-built support services on Railway) · Drive: `Branch Insurance Proposal 1-29-26` · agent prompts + tools (with URLs) for all 9 agents.

**All Branch agents are PROTOTYPES, not in production.** Per Craig: trial is happening but the Phase 1 deliverables haven't gone live. The 9 V1 agents represent active iteration.

**No AI-to-AI orchestration.** Petra does intent recognition + routing but transfers to **HUMAN queues** (Sales/Claims/Service/AgencySupport), not to other AI agents. Each specialized agent (Carson, Caroline, Sophie, Aria, Colleen) is its own front door — likely reached via Dialpad's upstream routing on different phone numbers or contexts.

#### Confirmed associate mapping — 5 distinct associates (revised 2026-05-01 per task-bundling rule)

5 distinct agent personas, 5 distinct overall objectives, no AI orchestration between them (Petra routes to human queues only) → **5 distinct associates**.

**1. Inquiry Associate (Branch IVR triage variant)**

Petra + Petra(copy). Objective: recognize caller intent and route to the right destination. Replaces Branch's legacy IVR.

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| IVR triage + intent recognition + routing to human queue (Sales/Claims/Service/Agency Support) · Coverage Q&A on-spine (when caller asks coverage question, answer from KB instead of routing) · Document fulfillment on-spine (Petra v1; Petra v2 hands off to Dialpad gated-URL flow instead) | KB retrieval · Intent classification (multi-pass) · Member/policy/staff lookup · Document generation · Voice call transfer · Human handoff escalation | Voice (in via Dialpad) | **Branch GraphQL API** · **Dialpad** · `branch-ivr-webhook-production.up.railway.app` (member/policy/staff lookup) · `branch-aria-documents-production.up.railway.app` (document generation, used on-spine in Petra v1) · Twilio + LiveKit + Cartesia · Indemn Copilot |

**2. Document Fulfillment Associate (Branch — Aria) — flagged catalog gap**

Aria. Objective: fulfill document requests (ID cards, Dec pages, COI, etc.) for policyholders + authorized 3rd parties (mortgage co, lienholders, property managers). Verify identity → list available docs → generate → send.

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| Document fulfillment with policyholder + 3rd-party authorization (verify identity → list available docs → generate doc → send via SMS/email → manage authorized recipients) | Document fulfillment (with 3rd-party auth) · KB retrieval · Voice call transfer · Human handoff escalation | Voice | `branch-aria-documents-production.up.railway.app` (`/api/documents/generate`, `/api/documents/send`) + (deleted) `aria-document-mcp-server.up.railway.app/graphql` · Twilio + LiveKit + Cartesia · Indemn Copilot |

Maps to: Cam catalog gap — **Document Fulfillment Associate** (see §2.05). No clean existing row.

**3. Claims Status Associate (Branch — Colleen) — flagged catalog gap**

Colleen. Objective: provide claims status to policyholders + authorized 3rd parties. NOT FNOL — this is *status*, not *intake*.

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| Claims status lookup (validate caller policyholder OR 3rd party with phone + last4 + auth check → return claim status + adjuster contact + financials) · Send status email · Schedule adjuster callback | Claims data lookup · KB retrieval · Voice call transfer · Human handoff escalation | Voice | `claims-mcp-server.up.railway.app/graphql` (Indemn-built) · Twilio + LiveKit + Cartesia · Indemn Copilot |

Maps to: Cam catalog gap — **Claims Status Associate** (see §2.05). Cam has Intake-for-Claims (FNOL); this is status, distinct.

**4. Care Associate / Billing (Branch — Sophie)**

Sophie. Objective: process billing payments via voice — validate customer, process Stripe payment.

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| Voice-channel billing payment (validate customer → process Stripe payment → confirm) | Stripe payment processing · KB retrieval · Voice call transfer · Human handoff escalation | Voice | **Stripe** · `branch-ivr-webhook-production.up.railway.app` (member lookup likely) · Twilio + LiveKit + Cartesia · Indemn Copilot |

Maps to: **Care Associate** (Carrier MGA tier — "Proactive Lapse Prevention · Automated payment status monitoring with proactive policyholder contact to resolve payment issues"). Sophie's payment recovery framing fits.

**5. Sales / Lead Associate (Branch — Carson + Caroline + branch quote assist)**

Carson + Caroline (voice; nearly-identical prompts — A/B variants) + branch quote assist (webchat). Objective: engagement + qualification + quote display + lead capture for Home/Auto prospects. Not actual binding — hands off to licensed agent.

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| Voice quote display + lead capture for Home/Auto (Carson, Caroline — collect 2 data points → call Branch GraphQL → display quote → handoff to licensed agent) · Webchat quote display + lead capture (branch quote assist) | KB retrieval · Customer profile collection · Branch quote generation + error handling (convertQuote → driver info / prior auto fallbacks → storeQuote) · Lead generation capture · Voice call transfer to licensed agent · Human handoff escalation | Voice (in/out) · Web chat | **Branch GraphQL API** (`staging.v2.api.ourbranch.com`) · Twilio + LiveKit + Cartesia · `devproxy.indemn.ai` · Indemn Copilot |

Maps to: Cam catalog gap — **Lead Associate (MGA tier)** (see §2.05). Branch is MGA; same gap as JM/UG Mobile Home.

(Plus `faq bot` webchat as legacy Knowledge Associate; not material.)

#### Notes for Branch

- **Carson + Caroline have nearly identical prompts** — likely A/B variants or alternate voice personas of the same Sales / Lead Associate. Branch had multiple iterations during trial.
- **Petra (copy)** is the v2 Petra with Dialpad gated-URL handshake instead of inline document delivery — Petra v1 has the documents-on-spine, Petra v2 hands off to Dialpad-gated URL flow. Iteration on the document path.
- **Many "(deleted)" tools** across agents — substantial cleanup/iteration in progress as the trial proves out which tools work.
- **The Indemn-built "branch-*" Railway services are CUSTOM for Branch.** This is significant per-customer engineering investment (3 separate Railway services + claims-mcp-server). Reuse story: the patterns are reusable (data-layer-as-MCP-server, Dialpad gated-URL handshake) but the Branch-specific endpoints aren't.
- **Sophie's tools haven't been deeply pulled yet** — Stripe integration confirmed via the proposal, exact tool list TBD.

---

### 8.8 O'Connor Insurance Associates `[in-progress — facts]`

**OS entity refs:** Company `69e41a7cb5699e1b9d7e98d7` · Cohort: Graduating · ARR $24K · Stage: pilot · Type: Broker · Champion: **Michelle O'Connor** · AMS: BT Core. OS notes: "Active implementation. Multiple check-ins. **BT Core migration blocking new initiatives.** Billing Agent = proof point. Most complete in Graduating cohort. 101 Weston Demo completed Jan 20."
**Sources reviewed:** OS Company entity · MongoDB tiledesk via SSM (4 V1 platform agents · 21 tools · 19 KBs) · prompts + tools (with URLs) for all 4 agents.

#### Confirmed associate mapping — 3 distinct associates (per task-bundling rule)

4 agents, 3 distinct overall objectives, no orchestration → 3 distinct associates.

**1. Front Desk Associate (Agency/Broker, $1,000 — "Receptionist Functions") — Billing voice**

Constituent agents: Sandy (Personal Lines, voice) + Coral/Gráinne (Commercial Lines, voice). Both share the SAME flow (inbound inquiry deflection with multi-carrier billing expertise) — different LOB scope is a pathway variant.

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| Personal Lines billing inquiry deflection (Sandy) · Commercial Lines billing inquiry deflection (Coral/Gráinne) | KB retrieval · Voice call transfer (Personal vs Commercial routing) · Human handoff escalation · End call · Custom flow tools (entryGate / mainBranchingLogic / infoGathering / disputeSubFlow) | Voice (in/out — Twilio + LiveKit + Cartesia) | Indemn Copilot (no external integrations — agents provide carrier info from KBs only; no direct payment processing) |

**Notable: NO direct payment processing.** Multi-carrier billing expertise (Erie, Travelers, Hartford, West Bend, Accident Fund, Progressive, National General) — agents provide payment links, phone numbers, portal info from KB. Don't process payments. Different from Branch's Sophie (which DOES process Stripe). This is **inbound inquiry deflection**, not payment-recovery / lapse-prevention.

**2. Knowledge Associate (Agency/Broker, $50/seat — "Smart Process Library") — External engagement**

Constituent agent: faq bot (webchat — O'Connor External Engagement Associate).

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| Website visitor insurance education + lead capture (with strict boundaries: no quote / no pricing / no coverage advice — educate + connect to advisor only) | KB retrieval · Lead generation capture · Human handoff escalation | Web chat | Indemn Copilot |

**3. Ticket Associate (Agency/Broker, $0.50/ticket — "Tier 1 Ticket Deflection") — Internal operations**

Constituent agent: o'connor internal agent (webchat — O'Connor Internal Operations Associate). Staff-facing.

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| Staff-facing routine inquiry deflection (HR/benefits/PTO/employee handbook + internal insurance FAQs) | KB retrieval · Human handoff escalation | Web chat | Indemn Copilot |

#### Notes for O'Connor

- **No new systems or channels** — uses voice + web chat infrastructure already in catalog. No external API integrations from agent tools (despite BT Core being the customer's AMS, agents don't currently query BT Core).
- **BT Core integration is future state** — OS notes say "BT Core migration blocking new initiatives" — when migration completes, BT Core API integration may become a new system. Currently not integrated.
- **"Billing Agent = proof point"** — Sandy + Coral are the showcase build at O'Connor, demonstrating multi-carrier billing inquiry deflection across LOB.
- **IIANC cohort** — O'Connor is part of the IIANC (Independent Insurance Agents of NC) cohort, which is a network expansion play similar to Johnson's Keystone Network.
- **Strict prompt boundaries on faq bot** — explicit NO quote / NO pricing / NO coverage interpretation rules. Reflects O'Connor's "advisor-first" positioning — the AI doesn't give advice, just educates and connects to humans.

---

### 8.12 Silent Sport (McKay Insurance Agency operating Silent Sports Insurance) `[in-progress — facts]`

**OS entity refs:** Company `69e41a9bb5699e1b9d7e9959` · Cohort: AI_Investments · ARR $12K · Stage: **prospect** (per OS — note Craig labels as "built-for") · Type: Broker · Champion: **Meg** · Health: 62 · Domain `silentsportsinsurance.com`.
**Sources reviewed:** OS Company entity · MongoDB tiledesk via SSM (1 V1 platform agent) · GitHub `conversation-service` (silent-sport quote endpoint) · Drive: `Silent Sports — Internal Team Review: Crawl/Walk/Run Proposal Framework` (Mar 17, 2026).

**Material context:** Sports/recreation insurance — bicycle clubs, races, silent sport events nationwide. Liability + accident coverage. **80-90 applications in peak (October), 30/mo slower months. 15 min/app processing today.** Operated by McKay Insurance Agency. Champion Meg + Scott (also at McKay). Currently in pilot/prospect stage; Mar 17 proposal (Crawl/Walk/Run framework) not yet executed.

#### Pilot/prototype state — 1 V1 platform agent

`Silent Sports Insurance` (id `689f75d7ab912b0013208326`) — webchat, GPT-4.1. **Per Craig + the Mar 17 proposal: this is a pilot / prototype, not in real production traffic. Meg (champion) hasn't tested it.** OS confirms `stage: prospect`. Treat the agent below as a configuration that exists, not a deployed service the customer is using daily.

| Tool | URL | What it does (per agent prompt) |
|---|---|---|
| `quote_generation` | `POST https://conversation.indemn.ai/v1/projects/quote_suggestions/silent-sport` | Backend exists (Airtable-backed mckay product configs), but **Craig flag: not really a live quote agent for Silent Sport's actual operations**. Likely shows pre-built option cards to demonstrate the capability, not driving real quote traffic. |
| `contact_info` | (custom_tool) | Lead capture (email/name/phone) |
| `Live handoff` | `https://copilotsync.indemn.ai/conversations/{session_id}/auto-assignment` | Human handoff |

#### Associate mapping — ONE associate (revised 2026-05-01 per task-bundling rule)

**Lead Associate (Agency/Broker — Silent Sport variant; pilot)**

One agent doing one conversational task: engagement → qualification → Q&A → quote display → lead capture, all part of the lead-engagement flow. Q&A is folded in (Cam's Lead Associate definition is "24/7 Lead Engagement & Qualification" which inherently includes Q&A as part of engagement).

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| Sports/recreation lead engagement + qualification + capture (pilot — includes program Q&A, mckay product display, and contact capture) | KB retrieval · Lead generation capture · mckay product quote display · Human handoff escalation | Web chat | Indemn Copilot · Airtable (Indemn-managed mckay product configs — used during demo, not driving live customer traffic) |

#### Planned per Crawl/Walk/Run proposal (Mar 17, 2026 — internal review, not yet executed)

| Phase | Price | Deliverables |
|---|---|---|
| **CRAWL** (Months 1-3) | $1,500/mo | Submission processing (dedicated inbox + PDF extraction + UW validation) · **Accord 25 certificate generation** ("THE HOOK") · Email notifications · Follow-up email drafting · Data export to spreadsheet |
| WALK (Months 4-6) | TBD | "Customer Access" — truncated in doc |
| RUN | TBD | — |

**Proposal note (with correction):** the proposal claims "Document generation is NET NEW for Indemn" — but per Craig + verified in code, **document generation already exists at UG** (intake-manager has `app/models/quote_document.py`, frontend `quote-pdf.ts`, quote-comparison UI components, 40 quote_documents in production). What's net-new is the specific **Accord 25 certificate** type (post-bind certificate of insurance), not document generation as a category.

**Craig flag:** document generation is a **capability area we should formalize as a shared platform skill** (tool-038 in catalog). Currently piecemeal: quote PDFs at UG (built), Accord 25 cert (planned at Silent Sport, would be first), premium disclosures / member certificates / decline letters (not built). Reusable across customers once formalized.

**Catalog row added when CRAWL executes:**
- **Intake Associate (Agency/Broker — LOB Application, $5/ticket)** for the submission processing pipeline
- New tool skill: Document generation (cross-cutting, would augment multiple associate types)

#### Catalog gap flagged (Agency/Broker tier)

Cam's catalog has Quote/Quote & Bind/Growth Associates only in **Carrier** and **MGA** tiers. **Agency/Broker tier has no quote-and-bind row.** Silent Sport's quote display currently folds under Lead Associate; if/when actual binding is added, this gap surfaces.

This is the **second catalog gap noted** alongside Lead Associate missing from MGA tier (flagged at JM + UG Mobile Home).

#### Notes for Silent Sport

- **Cross-customer reuse story validated:** Silent Sport is a clean instance of the JM + Mobile Home pattern — uses the same shared Indemn platform (conversation-service for quotes, Airtable for product configs, Indemn Copilot for chat). The Lead + Knowledge associates are essentially templated; the unique part is the Silent Sport / mckay product configuration.
- **The Crawl/Walk/Run proposal** explicitly references the framework Cam wants — phased delivery with clear deliverables per phase. This is what Indemn says to customers (matches your earlier "crawl/walk/run is how we tell customers what we'll deliver immediately, near term, long term").
- **Document generation as net-new capability** would unlock value across multiple existing customers (INSURICA COIs, UG decline letters) — flagged for tracking as planned tool skill.

---

### 8.5 Distinguished Programs (DP) `[in-progress — facts]`

**OS entity refs:** Company `69e41a79b5699e1b9d7e98c9` · Cohort: Core_Platform · ARR $12K · Stage: customer · Type: MGA_MGU · Champion: **Steve Sitterly (CIO)** · Owner: Kyle + Jonathan · Domain `distinguished.com`. Long sales cycle: initial proposal Jun 2024 → second proposal Dec 2024 → closed Jan 2025.
**Sources reviewed:** OS Company entity · MongoDB tiledesk via SSM (12 V1 platform agents · 27 tools · **76 KBs** — most-KB-rich customer in roster) · GitHub `indemn-observatory` (DP-specific extractor + report generator) · prompts + tools (with URLs) for 6 production-y agents.

**Material context:** OS notes state "Live: Cyber agents live | Voice agent scope + roadmap doc for champion Steve Sitterly." DP runs **11 canonical Distinguished Programs** containing products (Umbrella, Package, D&O, Crime, Cyber). Business Units have systems: IMS, Portal, Salesforce, Arch, Jarus, Tinubu. **Indemn-observatory has DP-specific extractor (`distinguished_internal.py`) producing reports for Steve Sitterly** — usage is being tracked.

#### Confirmed associate mapping — ONE Knowledge Associate (per task-bundling rule)

All 6 production-y agents share the SAME core objective: **answer DP product / program / capabilities questions using KB + structured product lookups**. Specialization (Cyber vs Community Associations) and audience (broker vs internal staff) are pathway and deployment variants, not distinct associates.

**Knowledge Associate (MGA — DP variant)**

Constituent agents: faq bot · melody (cyber assist, voice) · cyber agent (webchat) · community associations agent · submission portal assistant · [proto] internal user assistant.

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| General DP product / program / capabilities Q&A (faq bot · [proto] internal user assistant) · Cyber Insurance program Q&A — voice (melody) · Cyber Insurance program Q&A — webchat (cyber agent) · Community Associations program Q&A · Submission portal navigation + BOR handling rules (submission portal assistant) | KB retrieval · DP product lookup (n8n webhook) · DP capabilities lookup (n8n webhook) · Airtable record fetch (direct — internal user assistant) · Microsoft Teams notification dispatch (Power Automate Logic App) · Lead generation capture · Human handoff escalation · Voice call transfer · End call | Voice (melody) · Web chat (other agents) · Microsoft Teams (output channel for escalation notifications) | **Airtable** (Indemn-managed; DP product/program/permissions data — base `appjmI2TR7m0n9wps`) · `n8n.indemn.ai` (multiple DP-specific webhooks: generic `25dbcdf9-...`, cyber-agent-specific, distinguished-api) · **Microsoft Power Automate / Azure Logic Apps** (Teams notification trigger) · **Microsoft Teams** (notification destination) · Twilio + LiveKit + Cartesia (voice stack for melody) · Indemn Copilot |

#### Notes for DP

- **Programs/Products semantics encoded in agent prompts:** Programs are bundled offerings (11 canonical), Products are individual policy types within programs (Umbrella, Package, D&O, Crime, Cyber), Umbrella Families are groupings of umbrella products. This is DP-specific business terminology baked into how the agent answers.
- **Business Unit framing:** Each BU defines its own systems (IMS, Salesforce, Arch, Jarus, Tinubu) and workflow behaviors. Agents are scoped to a BU — they don't cross BU boundaries (e.g., Arch integration applies only to the Restaurant BU).
- **Specialization is a pathway variant** — Cyber, Community Associations, and "general" are different KBs and different n8n webhooks but the SAME core skill (answer-from-KB-plus-product-lookup).
- **Audience is a pathway variant** — internal-staff-facing (faq bot, internal user assistant) vs broker-facing (cyber, community associations, submission portal assistant) but same core skill.
- **No quote, no bind, no lead-as-revenue.** DP's associate is purely Knowledge work — no transactional flow.
- **Microsoft Power Automate is a NEW system in the catalog.** Used only for Teams escalation notifications.
- **6 prototype/test/iteration agents** ([proto] marketing website agent v1/v2/v3, demo agent, temp youtube test, [deprecated] umbrella PDFs) — not part of the production picture.

---

### 8.6 Johnson Insurance Services `[in-progress — facts]`

**OS entity refs:** Company `69e41a7bb5699e1b9d7e98d5` · Cohort: Graduating · ARR $30K · Stage: pilot · Type: Broker · Champion: **Jessica Yarbrough** · Owner: George · Signed Feb 4, 2026.
**Sources reviewed:** OS Company entity · Cam's Drive proposal portfolio (`Johnson Insurance Proposal 1-30-26`) · GitHub `indemn-ai/web-operators` repo · MongoDB tiledesk via SSM.

**The problem:** Johnson is the largest agency representing **Everett Cash Mutual (ECM)** — a carrier with no APIs / no downloads. Cheryl on Johnson's staff spends 50-60% of her time manually transcribing policy data from ECM's portal into Applied Epic. Plus glitchy RPA tooling. ~50 docs/week of renewals + endorsements.

**What was sold (Jan 30, 2026):** "ECM Portal Operator System" — pure back-end automation. $10K/year ($2.5K initiation + 3 × $2.5K phase milestones). 3 phases: Design (Feb 1-2 wks) → Build (Feb-Mar) → Live by end Q1 2026. Eliminate ECM manual transcription + replace existing RPA vendor.

**What was built (`indemn-ai/web-operators` repo):** A reusable **Web Operator Framework** — Python + LangGraph deep agent + `agent-browser` (browser automation) + Anthropic + poppler (PDF reading). Self-learning path documents (path_v0 → run → analyze trajectory → path_v1). 173 tests. First customer to use the framework.

**4 paths in production for Johnson:**

| Path | Specificity (carrier × LOB × workflow) |
|---|---|
| `paths/ecm_cap_renewal` | ECM × Commercial Auto Policy × renewal |
| `paths/ecm_cap_endorsement` | ECM × Commercial Auto Policy × endorsement |
| `paths/ecm_chg3_endorsement` | ECM × CHG3 (specific endorsement form) |
| `paths/ecm_fop_renewal` | ECM × Farmowners Policy × renewal |

Plus `paths/template/` for new paths and `skills/agent_browser_cli/` (the underlying browser-automation skill).

**No V1 platform deployment** — Mongo `structure_customers` shows only an old default "faq bot" with 1 generic KB and 2 tools (knowledge retrieval + escalation). Substantive work is entirely in `web-operators` repo, NOT on copilot dashboard.

#### Confirmed associate + skills + integrations for Johnson

**Intake Associate for AMS** (Agency/Broker tier — Renewal/Endorsement variant; Johnson's variant differs from GIC's "Quote Intake" variant)

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| ECM Commercial Auto Policy renewal automation · ECM CAP endorsement automation · ECM CHG3 endorsement automation · ECM Farmowners Policy renewal automation | Data extraction (ECM PDFs → structured) · Slack/Teams alert dispatch | Schedule (cadence-based scan of ECM portal) | Applied Epic AMS (web operator) · ECM Portal (web operator) |

#### Notes for Johnson

- **Skill granularity confirmed (Craig 2026-04-30):** The 4 ECM paths are pathway skills; data extraction + Slack/Teams alert are tool skills used within them; browser automation, Applied Epic field write, and ECM portal navigation are implicit in the web operator integration type.
- **Future expansion:** proposal mentions "Keystone Network Opportunity" (Keystone is a network of agencies). If expanded, other Keystone members likely on ECM + Applied Epic → would reuse Johnson's pathways + the Web Operator Framework (per the reuse story).

---

### Core_Platform (5 customers — heaviest builds)

| # | Customer | Type | ARR | AMS | Notes |
|---|---|---|---|---|---|
| 8.1 | **GIC Underwriters** `[next]` | MGA_MGU | $70K | Unisoft (per memory) | Deepest custom build. Outlook + Unisoft AMS workflow. Craig's primary technical-integration build. |
| 8.2 | Jewelers Mutual | MGA_MGU | $292.5K | — | Largest ARR. |
| 8.3 | INSURICA | Broker | $100K | Applied EPIC | Applied EPIC is high-leverage system integration (large market share). |
| 8.4 | Union General | MGA_MGU | $84K | — | Ben Bailey is UG (per memory). intake-manager customer. |
| 8.5 | Distinguished Programs | MGA_MGU | $12K | — | — |

### Graduating (5 customers — between trial/built-for and signed)

| # | Customer | Type | ARR | AMS | Notes |
|---|---|---|---|---|---|
| 8.6 | Johnson Insurance Services | Broker | $30K | — | "Unsigned-built-for" per Craig. |
| 8.7 | Branch | MGA_MGU | $24K | — | Has Cam proposal in portfolio. ROI models built. |
| 8.8 | O'Connor Insurance | Broker | $24K | BT Core | BT Core integration interesting (Alliance also uses BT Core). |
| 8.9 | Rankin Insurance Group | Other | $18K | Easy Links | Easy Links AMS — same system as InsuranceTrak + Turbo. |
| 8.10 | Tillman Insurance | Broker | — | Hawksoft | Hawksoft AMS — same system as GR Little. |

### AI_Investments — only 2 of 10 walked (rest dropped per Craig 2026-04-30)

| # | Customer | Type | ARR | AMS | Notes |
|---|---|---|---|---|---|
| 8.11 | Family First | Other | $12K | — | — |
| 8.12 | Silent Sports | Broker | $12K | Unknown | Mentioned by Craig as built-for. |

**Dropped from walk:** mShift, Bonzah, InsuranceTrak, Surety First, eSpecialty, ConvergentRPS, Overlook VC, Sotant. (Per Craig — these don't have material build/integration history worth reverse-engineering.)

### Prospects with significant build history (in Prospect cohort but worth walking)

| # | Customer | Notes |
|---|---|---|
| 8.21 | Alliance Insurance | v2 proposal complete, BT Core + Applied Epic + Dialpad in tech stack, Christopher Cook decision-maker. Most-deep prospect work. |
| 8.22 | GR Little Insurance | Hawksoft AMS. Apr 22 demo target — original proof customer for Phase A trace work. |
| 8.23 | Armadillo | Hydrated Apr 29; Discovery call Apr 28; intro from Matan Slagter (CEO) → David Wellner (COO). |
| 8.24 | FoxQuilt | In Cam's proposal portfolio. |
| 8.25 | Charley | In Cam's proposal portfolio. |
| 8.26 | Physicians Mutual | In Cam's proposal portfolio. |

**Total walk: 12 customers + 6 prospects with build history = 18 walk-throughs.**

### 8.1 GIC Underwriters `[in-progress — facts, awaiting Craig's skill mapping]`

**OS entity refs:** Company `69e41a79b5699e1b9d7e98cb` · 8 Touchpoints · 5 Contacts · 1 Document. No Deal/Proposal entity yet.
**Sources reviewed:** OS Company entity · GIC Drive folder (20 files, Mar 2024 → Feb 2026) · `GIC Proposal 1-30-26` · `gic-email-intelligence` repo · `operations_api` repo (the GIC PAS proxy) · MongoDB tiledesk (via prod-services SSM + bot-service container — `prod-indemn.3h3ab.mongodb.net`).
**Sources pending:** newer GIC proposal (Craig flagged one exists, not yet read).

**Customer profile:** MGA_MGU · ARR $70K · Cohort: Core_Platform · Stage: customer · Health: 100. Domain `gicunderwriters.com`; parent carrier Granada Indemnity Company. Customer since **March 2024**. Champion: **JC**. GIC sells Foxquilt insurance.

#### Associates active for GIC

| Associate (Cam catalog) | Status | Channel(s) | System(s) |
|---|---|---|---|
| **Quote Intake Associate for AMS** | Live in production (Apr 23) | Email (Outlook via Microsoft Graph) | Unisoft AMS (via Windows EC2 web-automation proxy) |
| **Placement Associate** (broker portal web agent) | Live | Web chat (Indemn-hosted) | GIC PAS via `https://ops.indemn.ai/v1/gic/policyDetails` (Indemn `operations_api` proxying Granada UAT API) |
| **Inbox Associate** | NOT deployed for GIC yet | (would be email) | — |
| **Workers Comp Voice Agent** ("Fred"/"Victor") | Prototype, not in production | Voice | Class-code verifier API (system unknown, see `verifyClassCode` tool) |

#### MongoDB tiledesk findings (prod-indemn cluster, GIC org `65eb3f19e5e6de0013fda310`)

GIC has **6 V1 platform agents** + **17 KBs** + **45 tools total** (per `structure_customers`).

| Agent ID | Name | Channel | Tools | KBs |
|---|---|---|---|---|
| `6870203be09a76001341743a` | "gic underwriters inc (dev-policy lookup api)" | webchat | 15 (mostly policy-lookup variants) | GIC KB · Email/Document Routing FAQ (piped) · Portal Troubleshooting FAQ (piped) |
| `66026a302af0870013103b1e` | "gic" — original webchat (Mar 2024) | webchat | 3 | GIC KB · Broker Portal Troubleshooting FAQ · Email/Document Routing FAQ |
| `695e6ec3922e070f5e0a9a3b` | "fred" — Workers Comp voice intake | voice | 49 (with dupes; ~30 unique custom_tools modeling ACORD 130 fields) | GIC KB · WC Proxy KB · GIC-Crawl-Nov_2025 |
| `67d30ac0323aa30013f2d3f8` | "agent service voice prototype #1" | voice | 5 | GIC KB · Broker Portal Troubleshooting · Email/Document Routing FAQ |
| `69254bf059a39000136e10e3` | "agent service voice prototype #2" | voice | 5 | Broker Portal Troubleshooting FAQ · GIC KB · Email/Document Routing FAQ · GIC-Crawl-Nov_2025 |
| `66f137239afe08001360f7bb` | "test1" | webchat | 3 | GIC KB |

**Question for Craig:** which of `6870203be09a76001341743a` (dev-policy-lookup) and `66026a302af0870013103b1e` (original "gic") is currently serving prod broker portal traffic? The dev-policy one has the PAS lookup integration; the original has 3 basic tools. (Possibly both — dev one in pilot, original handling general traffic.)

#### Broker Portal agent (`6870203be09a76001341743a`) deep facts

- **Persona:** "Fred, an AI agent assistant operating within the GIC Underwriters Insurance broker portal" (system prompt 12,422 chars)
- **Model:** GPT-4.1 (OpenAI)
- **First message:** "Hello! How can I assist you today?"
- **Tools (15):** human_handoff · policy_check_enhanced (REST) · policy_unavailable · policy_input_analysis · optimized_policy_lookup (REST) · policy_success_response · policy_escalation_required · policy_manual_review · connect_specialist · policy_data_processor · policy_api_caller (REST) · policy_response_handler · connectSpecialist · validate_response_scope
- **Tools cluster around one core function: looking up policy status**, with extensive error handling for known failure patterns (case sensitivity, suffix formats, CIM commercial, alpha prefix, contamination)

#### Fred / Workers Comp Voice agent (`695e6ec3922e070f5e0a9a3b`) deep facts

- **Persona:** "Victor, voice assistant for GIC Underwriters Insurance, supporting insurance agents who quote, place, and bind workers' compensation coverage" (system prompt 11,755 chars). Note: `bot_name=fred` but prompt persona is "Victor" — likely renamed in prompt without renaming bot record
- **Model:** Gemini 2.5 Flash (Google)
- **First message:** "GIC Underwriters, this is Victor. How can I help you?"
- **Phase 0 Triage Gate:** 5 questions in first 2 minutes (submission type + effective date · state(s) · class of business · headcount/payroll · mod + losses) → Green/Yellow/Red light decision
- **Custom tools (deduped, ~22 unique):** identifyAgentAndAgency · identifyOpportunityType · captureCallerIdentity · capturePolicyDetails · captureLossDetails · captureAccountProfile · captureLocationDetails · captureOperationsDescription · capturePayrollByClassCode · captureFleetExposure · captureSafetyProgram · captureCurrentCoverage · captureExperienceModifier · captureLossHistory · captureQuotePreferences · captureAdditionalNotes · confirmComplianceAndWrap · generateSubmissionChecklist · handleAppetiteCheckOnly · verifyClassCode (REST) · plus FAQs Retriever / Live handoff / End call (each duplicated many times)
- **Maps to ACORD 130** (standard WC application form) — the captures mirror that form's sections

#### GIC PAS API integration (factual)

- **Indemn-side endpoint:** `https://ops.indemn.ai/v1/gic/policyDetails`
- **Source:** `indemn-ai/operations_api` repo · `src/routes/gic-policy-details.ts` + `src/services/customers/gic_policy_details.ts`
- **Inputs:** `agencyCode` (string|int) + `policyNumber` (string)
- **Upstream:** Granada Insurance UAT API at `https://services-uat.granadainsurance.com`
- **Auth:** OAuth-style — `/v1/token/generate` (Basic auth with `GIC_USERNAME`/`GIC_PASSWORD` env) → access+refresh tokens cached in Redis as `gic_tokens` with TTL
- **Note:** UAT, not production Granada API
- `operations_api` is the central middleware proxy for ALL Indemn carrier API integrations (zurich, markel, chubb, bonzah, GIC, insurica, joshu)

#### Email Intelligence System (factual, separate custom app)

- **Repo:** `indemn-ai/gic-email-intelligence` (NOT on OS)
- **Stack:** AWS Amplify (UI) + 4 ECS containers (api, sync 5-min poll, processing, automation) + Windows EC2 (Unisoft proxy) + MongoDB Atlas (custom DB) + S3 (attachments) + LangChain/LangGraph + Anthropic/Vertex AI
- **Inboxes plumbed:** `quote@gicunderwriters.com` + endorsement inbox (recently added)
- **Planned next:** USLI carrier-quote-back automation
- **Code-level skill files:** `email_classifier.md` (14-type classification: USLI quote/pending/decline · agent submission/reply/followup · GIC portal submission/application/info_request/internal · Hiscox quote · renewal · report · other) · `pdf_extractor.md` (Accord PDF) · `submission_linker.md` · `situation_assessor.md` · `draft_generator.md` (NOT live for GIC) · `automation/create-quote-id.md` (Unisoft write-back; more automation skills likely)

> Per Craig: framework-level skills are NOT 1:1 with these code files. The framework skills come out of his/our discussion.

#### Channels factual list for GIC

- Web chat (Indemn-hosted)
- Email — Outlook via Microsoft Graph API
- Voice (Fred prototype only — not live for GIC)

#### Systems factual list for GIC

- Unisoft Communications AMS — Windows EC2 web-automation proxy
- GIC PAS (Granada Insurance UAT API) — REST via Indemn `operations_api` proxy
- Microsoft Graph API (Outlook)
- Class-code verifier (used by Fred — system identity TBD; could be NCCI or Indemn-internal)

#### Confirmed associates + skills + integrations for GIC (Craig 2026-04-30)

**Placement Associate (broker portal — production, agent `6870203be09a76001341743a`)**

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| Broker portal Q&A interaction · Policy lookup workflow (with error handling) | KB retrieval · Policy status retrieval (atomic) · Human handoff escalation | Web chat (Indemn Copilot) | Granada Insurance API · Indemn Copilot |

- The dev-policy-lookup agent IS the prod agent (despite the name).
- Spanish + English are handled automatically by the model — not a separate skill / configuration.
- Granada API: `https://ops.indemn.ai/v1/gic/policyDetails` → upstream `services-uat.granadainsurance.com` via OAuth (cached in Redis), proxied through Indemn `operations_api` repo.
- The original "gic" agent (`66026a302af0870013103b1e`) and "test1" (`66f137239afe08001360f7bb`) are not the prod broker portal.

**Quote Intake Associate for AMS (production — separate custom app `gic-email-intelligence`)**

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| Application submission into AMS (= quote create + activity create + task create, atomically) · **(pending)** Carrier quote submission into AMS (= quote-submission create + activity create — the planned USLI quote-back work) | Data classification · Data extraction (PDF/OCR/structured) | Email — Outlook via Microsoft Graph | Unisoft Communications AMS (Windows EC2 web-automation proxy) |

**Workers Comp Voice Agent ("Fred"/"Victor" — prototype, NOT live for GIC, agent `695e6ec3922e070f5e0a9a3b`)**

Maps to **Intake Associate (MGA — Submission Triage)** in Cam's catalog — voice variant. Confirmed 2026-04-30.

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| Workers Comp application validation and qualification · Workers Comp appetite verification · Workers Comp submission checklist generation `[?]` | KB retrieval · Class code verification · Human handoff escalation | Voice | Class-code verifier (system identity TBD — Craig unsure) · Indemn Copilot |

- WC is integral to this associate's work today (ACORD 130, NCCI class codes, mod-based appetite). If Fred (or its successor) ever covers other LOBs, that's additional skills.
- "Submission checklist generation" still has `?` — Craig wasn't 100% sure if this counts as its own skill or a sub-piece of qualification. Carry forward.

#### Notes on classification ambiguity (carry forward, not pre-decided)

- **Indemn Copilot as system vs. channel host vs. internal platform** — Craig listed it as a system for both Placement Associate and Fred. Recording as a system but flagging — it's a different category from "external customer system" like Granada API. Worth a clarifying conversation when more customers surface it.
- **Microsoft Graph API** — recorded as the implementation of the email channel (Outlook). Not separately tracked as a system.

`[no Core/Soon/Enterprise classification, no LOE estimates, no reusability claims — those are not for me to author]`

---

## 9. Per-associate sweep `[after the customer walk]`

After the customer walks, the 47 deployable rows in Cam's sheet get swept against the catalogs built in §§ 5-7. Per row: skills, integrations, qualifying questions, anything else Craig wants to capture. **Tier classifications + cost reasoning are Craig's, not mine.**

---

## 10. Final sheet update spec `[after § 9]`

Exact migration plan from this doc into Cam's spreadsheet. Reviewed with Craig before any cells in Cam's sheet are touched.

---

## Appendix A — Existing Working Copy annotations Craig has already written

Direct quotes from the Craig|Kyle Working Copy tab. These are Craig's words, not my interpretation — anchors for the work, no editorializing.

- **Renewal Associate:** "Currently integrated: 30 hours. Additional integration: 30-50 hours depending on complexity for new integration. Total 60 hours for new integration + man hours to implement the solution."
- **Intake-for-AMS Associate:** "Every new carrier I add to the mix involves me creating a skill for automation of the quote submission to that carrier. For GIC: Quote Intake Associate for AMS but could be Endorsement Intake Associate for AMS."
- **Knowledge Associate:** "KB Development: 3-5h, Prompt Development: 3-5h, Testing/Evaluation: 2h."
- **Care Associate:** "Outbound phone calls and/or emails, text messages — do we want a default?"
- **Front Desk Associate:** "Qualification needed to define whether this is overflow, after hours, etc."
- **Inbox Associate:** "This is not the same as shipping data from inbox into AMS."

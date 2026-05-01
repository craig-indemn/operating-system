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

**Phase A complete: 13 of 13 active customers walked** (12 active customers + Alliance reclassified as active per Craig 2026-05-01). 5 remaining prospects-with-build-history (8.22 GR Little, 8.23 Armadillo, 8.24 FoxQuilt, 8.25 Charley, 8.26 Physicians Mutual) are **OUT of scope for this pricing-framework work** per Craig 2026-05-01 — they may be picked up later but are not part of the current pass.

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
| 8.9 | Rankin Insurance Group | ✅ Done (2 associates: Front Desk multi-intent voice w/ message-taking · Lead web qualifier — James) |
| 8.10 | Tillman Insurance Advisors | ✅ Done (2 associates: Front Desk bilingual voice/web w/ service-intake pathway · Lead bilingual voice+web w/ multi-product intake) |
| 8.11 | Family First | ✅ Done (1 associate: Knowledge — caregiving Care Library Q&A; healthcare/caregiving outlier mapped to Agency/Broker Knowledge per Craig) |
| 8.12 | Silent Sport | ✅ Done in pilot state (1 associate: Lead Associate w/ Q&A folded in) |
| 8.21 | Alliance Insurance Services | ✅ Done (3 associates: Front Desk voice+web · Lead voice+web · Ticket internal "State of the Agency"; treated as active customer per Craig) |
| 8.22–8.26 | GR Little · Armadillo · FoxQuilt · Charley · Physicians Mutual | 🔒 **Out of scope** — picked up later, not part of this pricing-framework work per Craig 2026-05-01 |

**Catalog state (post-Phase A; post-2026-05-01 §7 audit):** 57 tool skills · 46 pathway skills (was 55; -3 channel-split merges: path-026/038/041 → path-025/037/040 · -1 escalation merge: path-013 → path-012 · -1 intake-disambiguation merge: path-029 → path-025 · -1 LOB-split merge: path-045 → path-044 · -3 KB-scope merges: path-017/018/022 → path-016) · 8 channels · 27 systems · 4 catalog gaps tracked in § 2.05.

### The 5-phase plan (locked in 2026-05-01)

| Phase | What | Status |
|---|---|---|
| **A** | Customer walks — observe what's built per customer; populate §§5-7 catalogs with observed skills/channels/systems | ✅ Complete (13 of 13 active customers) |
| **B** | Per-associate sweep across all 47 Cam rows + 8 in-development rows — for each row, derive skills/channels/systems from Cam's description (including for un-deployed rows). Per-row redundancy: each row writes its skills out fully even when shared across Cam rows. | ✅ Complete 2026-05-01 (all 55 rows in §9 with pathway skills + tool skills + channels + systems + customers active + status) |
| **C** | LOE pass per catalog entry — for each tool skill, pathway skill, channel, system, assign hours estimate. **Hours only, no money** per Craig 2026-05-01. Built things → actual hours; not-built → first-customer LOE estimate. **Collaborative — Craig authors estimates, I capture structure** | ⏳ Next |
| **D** | Output presentation — final sheet update spec for Cam + **HTML UI visualization** (more visualizable than Excel; per Craig 2026-05-01 — could "go ham" on Excel polish too, "different story") | ⏳ After C |
| **E** | Operating-system data-model bounce-off — put this information in the OS as a way to bounce our customer/associate/skill data models off what we've put together. Per Craig 2026-05-01 | ⏳ After / in conjunction with D |

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

- **Phase A complete** (13 of 13 active customers walked). 5 prospects (GR Little, Armadillo, FoxQuilt, Charley, Physicians Mutual) **out of scope** per Craig 2026-05-01.
- **Phase B complete 2026-05-01** — all 55 Cam rows (47 deployable + 8 in-development) in §9 with pathway skills + tool skills + channels + systems + customers active + status. Per-row redundancy applied; resolved decisions captured in §9.5; Zola embedded-chat added to §6 Systems catalog.
- **Phase C next:** LOE pass per catalog entry — hours estimates per tool skill, pathway skill, channel, system. Hours only, no money. Collaborative — Craig authors, I capture structure. Output written to §10.
- **Phase D after C:** sheet update spec for Cam + HTML UI visualization. Output written to §11.
- **Phase E (after / with D):** OS data-model integration — put this information in the operating system to bounce our customer/associate/skill data models off what we've built. Output written to §12.
- **Catalog gaps already tracked (§ 2.05):** Lead Associate for MGA tier · Quote & Bind for Agency/Broker tier · Document Fulfillment Associate · Claims Status Associate. May surface more.
- **Document generation as a capability area (tool-038)** — flagged for formalization as shared platform skill.
- **Don't touch Cam's sheet** until §11 produces the migration spec and Craig signs off (post-Phase D).

### Phase C kickoff plan (next session — Pricing Framework Session 3)

**What Phase C produces.** For each entry in the §§5-7 catalogs, an LOE estimate in hours:

| Catalog | Entries | What we capture per entry |
|---|---|---|
| §5 Channels | 8 | First-customer LOE (hours to build the channel adapter for the first customer) · per-customer-after-first LOE (hours to apply to subsequent customers) · notes |
| §6 Systems | 28 | Same shape · plus integration-type effect (`API` vs `web operator` vs other) |
| §7 Tool skills | 57 | Same shape · plus reuse caveat (some tools are per-customer-custom even when nominally reusable) |
| §7 Pathway skills | 46 | Same shape · plus customer-specific customization weight (per the "medium reuse" framing) |

**The discipline (per Craig 2026-05-01).**
- **Hours only, no money.** Hours-to-dollars mapping is not in scope for Phase C.
- **Collaborative.** Craig authors estimates + reasoning. I capture structure. **I do NOT propose LOE numbers myself.** I bring the catalog entry, ask for the estimate, capture it.
- **Anchors already in Appendix A** (Working Copy annotations Craig has already written): Renewal Associate "Currently integrated: 30 hours. Additional integration: 30-50 hours depending on complexity for new integration. Total 60 hours for new integration + man hours to implement the solution." · Knowledge Associate "KB Development: 3-5h, Prompt Development: 3-5h, Testing/Evaluation: 2h" · etc.

**Recommended order (smallest catalog first for warmup):**
1. **§5 Channels (8 entries)** — quick warmup; channels are well-bounded and reusable
2. **§6 Systems (28 entries)** — substantive; `API` vs `web operator` distinction matters; some are 3rd-party (Twilio/LiveKit/Cartesia/Stripe) with low first-time LOE, others are per-customer-custom (Unisoft web operator, BT Core integration TBD, ECM Web Operator Framework)
3. **§7 Tool skills (57 entries)** — atomic capabilities; many short builds (per-product intake forms = 1-3h each), some longer (Branch GraphQL convertQuote with error-handling fallbacks = larger)
4. **§7 Pathway skills (46 entries)** — workflows; LOE is the orchestration cost on top of the underlying tool skills

**Output structure for §10 (when Phase C captures land):**

```
§10.1 Channels LOE
| Channel | First-customer LOE | Per-customer-after | Notes |
| ... | ... | ... | ... |

§10.2 Systems LOE
| System | Integration type | First-customer LOE | Per-customer-after | Notes |
| ... | ... | ... | ... | ... |

§10.3 Tool skills LOE
| ID | Skill | First-customer LOE | Per-customer-after | Notes |
| ... | ... | ... | ... | ... |

§10.4 Pathway skills LOE
| ID | Skill | First-customer LOE | Per-customer-after | Notes |
| ... | ... | ... | ... | ... |
```

**After Phase C done-test:** the formula `cost = (channels) + (skills) + (systems)` is computable per customer for any of Cam's 47 rows — given a customer's channel/system/skill state, sum hours to get implementation LOE.

### Session-start protocol for next session (Pricing Framework Session 3)

1. Read canonical context per `PROMPT.md` (customer-system CLAUDE.md · vision.md · roadmap.md · os-learnings.md · CURRENT.md · SESSIONS.md · indemn-os CLAUDE.md)
2. Read this working doc — **§0 Session Handoff (this section) + §2 Formula + §2.05 Catalog gaps + §10 Phase C structure**. The §8 customer detail and §9 per-associate sweep don't need to be re-read in full unless a specific row is being authored — they're reference.
3. Read source-material artifact (`artifacts/2026-04-30-pricing-call-and-sheet-source-material.md`) for Cam call context — light read.
4. Confirm understanding back to Craig — framework rules · 5-phase plan · Phase A + B complete · Phase C kickoff plan (above).
5. Begin Phase C — **start with §5 Channels (8 entries, smallest catalog)**. Work entry-by-entry: bring channel name + description + customers active → ask Craig for first-customer LOE + per-customer-after LOE + notes → capture to §10.1 → next.

### Key files / references

- **Working doc:** `artifacts/2026-04-30-associate-pricing-framework.md` (this file) — primary state-of-work
- **Source material:** `artifacts/2026-04-30-pricing-call-and-sheet-source-material.md` (Cam call decisions + Cam sheet schema + existing Craig annotations — Phase C anchors live here in Appendix A)
- **Cam's spreadsheet:** `https://docs.google.com/spreadsheets/d/17GEDxqTvCHxHYsZKSQDppGfx6XYOzykUkuF_rxQUsx4/edit` (DON'T modify until §11 spec is ready post-Phase D)
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
| Embedded chat in partner surface | API (3rd party) | built | Pattern for embedding an Indemn agent inside a partner's product/website. Customer-facing AI agent runs inside the partner's flow rather than the customer's owned channel. Different deployment shape from owned-channel deployment — partner controls surface, Indemn agent handles education/handoff. | JM (Dahlia for Zola — voice agent embedded in Zola's wedding/engagement-ring flow) |

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
| tool-049 | Business-hours lookup (@bizHoursLookup / @checkBusinessHours; check open/closed against configured agency hours; voice agent uses to drive after-hours routing) | Front Desk Associate (Rankin Ronnie2 + Tillman Donna Mae; generalizable to any voice agent that needs hours-aware routing) | built | Rankin, Tillman |
| tool-050 | Bilingual handling — linguistic compass (@LinguisticGuide retrieves Spanish-glossary KB · register-survival clause locks register/pronoun/dialect across turns and tool boundaries · @NameReadback + @NameSpellBack for name accuracy across languages · @ClosingGate, @EmpathyAcknowledge as bilingual-aware closing/empathy hooks) | Front Desk · Lead Associate (Tillman variants — Maria voice, Nolan voice, Emery web, Emma web; reusable for any bilingual EN+ES customer) | built | Tillman |
| tool-051 | Auto insurance intake (structured product-specific intake form — driver/vehicle/coverage details captured in conversational format) | Lead Associate (Tillman variant — Nolan, Emma) | built | Tillman |
| tool-052 | Personal property insurance intake (home / condo / renters / townhome / landlord / boat / motorcycle / ATV / RV / collectible — structured product-specific intake) | Lead Associate · Front Desk (Tillman variants — Nolan, Emma, Emery) | built | Tillman |
| tool-053 | Life insurance intake (term / whole / universal / key person — structured product-specific intake) | Lead Associate · Front Desk (Tillman variants — Nolan, Emma, Emery) | built | Tillman |
| tool-054 | Business insurance intake (BOP / GL / Workers Comp / Commercial Auto / Professional Liability / E&O / Commercial Property / Contract-Lease-Job-Required — structured product-specific intake) | Lead Associate · Front Desk (Tillman variants — Nolan, Emma, Emery) | built | Tillman |
| tool-055 | Event insurance intake (wedding/event structured intake — distinct from JM EventGuard's tool-030 which is quote-generation; this is intake-only for downstream human follow-up) | Lead Associate · Front Desk (Tillman variants — Nolan, Emma, Emery) | built | Tillman |
| tool-056 | Pet insurance intake (structured product-specific intake) | Lead Associate · Front Desk (Tillman variants — Nolan, Emma, Emery) | built | Tillman |
| tool-057 | Emergency redirection (route caller/visitor to 911 for acute medical/physical events · 988 for psychiatric / self-harm risk · Poison Control 1-800-222-1222 for medication issues; distinguish prevention questions from acute response situations; never provide clinical triage checklists that assume user has clinical knowledge) | Knowledge Associate (Family First variant; reusable for any healthcare/caregiving customer) | built | Family First |

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
| path-012 | Multi-channel customer renewal outreach + data collection (consolidated 2026-05-01; folds in former path-013 escalation handling) — INSURICA MARA pattern: 6-attempt cadence across web/email/voice/SMS to refresh Julia Hester's 5 Key Data Points (address, contact_info, business_ops, exposure, gl_requirements); persists state across channels; disposition state machine; **escalation gates folded in** (legal/BOR IMMEDIATE; classification/exposure/low-confidence escalations); Salesforce sync | Renewal Associate | built | INSURICA |
| path-013 | `[merged into path-012 on 2026-05-01 — escalation handling folded into multi-channel outreach pathway]` | — | — | — |
| path-014 | ACORD 25 certificate request intake + submission | Front Desk Associate | built | INSURICA |
| path-015 | Medicare Part D enrollment qualification + intake | Medicare Part D Navigator (unique product — not in Cam catalog) | built | INSURICA |
| path-016 | Insurance KB-backed Q&A across UG content scopes (consolidated 2026-05-01; folds in former path-017 per-carrier UW Q&A + path-018 Northland trucking + path-022 Mobile home product Q&A) — same skill shape, different KB scopes deployed: multi-carrier UW knowledge (Augi super agent across 7 carriers: USLI · Kinsale · Northfield · ACIC · Scottsdale · Seneca · SIC) · per-carrier UW specialist agents · Northland trucking commercial UW · Mobile home product Q&A (4-state: NM/NV/AZ/Texas) | Knowledge Associate (UG variant) | built | UG |
| path-017 | `[merged into path-016 on 2026-05-01 — same skill, per-carrier KB scope variant]` | — | — | — |
| path-018 | `[merged into path-016 on 2026-05-01 — same skill, Northland trucking KB scope variant]` | — | — | — |
| path-019 | Homeowners + Dwelling Fire intake → Nationwide PL quote | Intake+Market combined (UG variant) | built | UG |
| path-020 | General Liability intake → 3-carrier comparative quote (ACIC + Nationwide CL + Northfield) | Intake+Market combined (UG variant) | built | UG |
| path-021 | Northland trucking intake (ACORD 130 + DOT/MC/CDL extraction) | Intake+Market combined (UG variant) | built — workflow inactive | UG |
| path-022 | `[merged into path-016 on 2026-05-01 — same skill, Mobile home product KB scope variant]` | — | — | — |
| path-023 | Mobile home lead capture | Lead Associate (UG variant — **gap: not in Cam MGA tier**) | built | UG |
| path-024 | Producer/agency onboarding intake | Onboarding Associate (UG variant) | WIP | UG |
| path-025 | JM ring engagement quote + SMS quote delivery + lead capture (consolidated 2026-05-01; folds in former path-026 web channel + former path-029 Personal vs Commercial jewelry routing as intake disambiguation) — deployed via Dahlia voice (with SMS quote delivery) and faq bot + engagement-focus-v2 webchat | Quote & Bind Associate (JM variant) | built | JM |
| path-026 | `[merged into path-025 on 2026-05-01 — channel consolidation]` | — | — | — |
| path-027 | EventGuard event insurance quote+bind (point-of-sale on www-eventsguard-mga, with Stripe checkout) | Quote & Bind Associate (JM variant — EventGuard product) | built | JM |
| path-028 | Zola-embedded ring insurance education + handoff (Dahlia for Zola — voice) | Knowledge Associate · Lead Associate (JM variant — partner-embedded) | built | JM |
| path-029 | `[merged into path-025 on 2026-05-01 — intake disambiguation folded into JM Quote & Bind pathway]` | — | — | — |
| path-030 | Jewelry/ring product Q&A | Knowledge Associate (JM variant) | built | JM |
| path-031 | Sports/recreation lead qualification + capture (pilot) | Lead Associate (Silent Sport variant) | built (pilot — not in real production traffic) | Silent Sport |
| path-032 | Silent Sports program Q&A (pilot) | Knowledge Associate (Silent Sport variant) | built (pilot — not in real production traffic) | Silent Sport |
| path-033 | IVR triage + intent recognition + routing (Petra) — answers coverage Q&A on-spine OR transfers to human queue (Sales/Claims/Service/AgencySupport) | Member Services Associate (Branch variant) | built (prototype) | Branch |
| path-034 | Document fulfillment (Aria — verify identity incl. 3rd party authorization → generate doc → send via SMS/email; v2 uses Dialpad gated-URL handshake) | Member Services Associate (Branch variant — Document Fulfillment sub-pathway) | built (prototype) | Branch |
| path-035 | Claims status lookup (Colleen — validate caller policyholder OR 3rd party, return claim status + adjuster contact + financials, optional email + callback) | Member Services Associate (Branch variant — Claims Status sub-pathway) | built (prototype) | Branch |
| path-036 | Voice-channel billing payment (Sophie — validates customer + processes Stripe payments) | Member Services Associate (Branch variant — Billing sub-pathway) | built (prototype) | Branch |
| path-037 | Home/Auto quote display + lead capture (consolidated; pre-2026-05-01 was split as path-037 voice + path-038 web) — collect minimal customer profile (full name, address) → call Branch GraphQL convertQuote (with driver-info + prior-auto error-handling fallbacks) → display quote → handoff to licensed agent. Deployed via Carson voice + Caroline voice (A/B variants) + branch quote assist webchat | Sales / Lead Associate (Branch variant) | built (prototype) | Branch |
| path-038 | `[merged into path-037 on 2026-05-01 — channel consolidation]` | — | — | — |
| path-039 | General DP product / program / capabilities Q&A | Knowledge Associate (DP variant) | built | DP |
| path-040 | Cyber Insurance program Q&A (consolidated; pre-2026-05-01 was split as path-040 voice + path-041 web) — KB-backed Q&A on DP Cyber program details, eligibility, submission process. Deployed via Melody voice + cyber-agent webchat | Knowledge Associate (DP variant — Cyber specialization) | built | DP |
| path-041 | `[merged into path-040 on 2026-05-01 — channel consolidation]` | — | — | — |
| path-042 | Community Associations program Q&A | Knowledge Associate (DP variant — Community Associations specialization) | built | DP |
| path-043 | Submission portal navigation + BOR handling rules | Knowledge Associate (DP variant — submission portal specialization) | built | DP |
| path-044 | Multi-carrier billing inquiry deflection across LOBs (consolidated 2026-05-01; folds in former path-045 CL variant) — voice-channel inbound inquiry deflection with multi-carrier billing expertise (Erie, Travelers, Hartford, West Bend, Accident Fund, Progressive, National General); agents provide payment links/phone numbers/portal info from KB, no direct payment processing. Deployed via Sandy (Personal Lines voice) + Coral/Gráinne (Commercial Lines voice) — same skill, different KB scope per LOB | Front Desk Associate (O'Connor variant) | built | O'Connor |
| path-045 | `[merged into path-044 on 2026-05-01 — LOB-split consolidation, same skill different KB scope]` | — | — | — |
| path-046 | Website visitor education + lead capture (with strict no-quote/no-pricing boundaries) | Knowledge Associate (O'Connor variant) | built | O'Connor |
| path-047 | Staff-facing routine inquiry deflection (HR/benefits/PTO/employee handbook + internal insurance FAQs) | Ticket Associate (O'Connor variant) | built | O'Connor |
| path-048 | Inbound voice multi-intent triage with message-taking + caller identity capture + after-hours handling + voicemail (Rankin Ronnie2 — does NOT transfer calls; captures caller info → posts to staff queue via Slack daily-reporting + portal) | Front Desk Associate (Rankin variant) | built | Rankin |
| path-049 | Sales lead qualification + Universal Lead Capture + Personal/Commercial routing + product-specific intake (web — James persona; bounded KB Q&A folded in: no quote / no eligibility / no service tasks; existing-customer service request → live handoff) | Lead Associate (Rankin variant) | built | Rankin |
| path-050 | Bilingual EN+ES front-desk reception + service-request intake with multi-product routing (gathers caller/visitor info, routes to right Term Advisor or staff queue; no policy access / no quote / no bind) — deployed via Maria (voice, peak/after-hours/lunch), Donna Mae (voice, older iteration), Emery (web, service-intake scope) | Front Desk Associate (Tillman variant) | built | Tillman |
| path-051 | Bilingual EN+ES sales qualification + Universal Lead Capture + multi-product intake routing across Personal/Commercial/Specialty (qualify-capture-connect; no quote/bind/recommend; Acknowledge-Illuminate-Probe rapport on voice) — deployed via Nolan (voice, "Term Advisor") and Emma (web, faq bot) | Lead Associate (Tillman variant) | built | Tillman |
| path-052 | Caregiving multi-topic Care Library Q&A (childcare · eldercare · mental & behavioral health · medication · financial/legal · long-term care · caregiver support · absence/leave/disability · Alzheimer's/dementia · health insurance counseling · health issues · family dynamics) with empathy + acknowledgment discipline + brevity rules (3-4 bullets max) + assumption guardrails (no inferring age/condition) + emergency redirection (911/988/Poison Control) + Care Expert email handoff for unanswered/distressed cases — deployed via canonical eldercare ai agent (prototype) + topic-specialized variants (eldercare · childcare · mental & behavioral health · long term care vertical · homecare · health insurance/finance/legal vertical · empathybot · faq bot) + go-live candidate iterations | Knowledge Associate (Family First variant) | built | Family First |
| path-053 | Customer service intake/classification/routing (silent call init logging · identify customer + policy context: personal vs business · classify service request type · collect intake details · route to CSR; no policy access / no quote / no service actions) — deployed via Haley voice (service agent) and Alliance service intake webchat | Front Desk Associate (Alliance variant) | built | Alliance |
| path-054 | Customer sales qualification + Universal Lead Capture + product-specific intake routing (qualify-capture-connect; Acknowledge-Illuminate-Probe rapport on voice; personal vs commercial vs service-related determination; no quote/bind/recommend) — deployed via Colter voice (sales agent) and Alliance sales agent webchat | Lead Associate (Alliance variant) | built | Alliance |
| path-055 | Internal employee "State of the Agency" Q&A (monthly/quarterly internal updates · agency metrics + performance snapshots · internal initiatives, tools, programs · staffing updates / recruiting status / training plans · leadership communications) — staff-facing only, not customer-facing; grounded in known facts to reduce confusion and rumor; flags pending/TBD when info not finalized | Ticket Associate (Alliance variant) | built | Alliance |

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

### 8.9 Rankin Insurance Group `[in-progress — facts]`

**OS entity refs:** Company `69e41a7cb5699e1b9d7e98d9` · Cohort: Graduating · ARR $18K · Stage: pilot · Type: Other (small independent agency — maps to Agency/Broker tier) · AMS: **Easy Links** (per OS field) / **EasyLynq** (per OS notes) — **NOT yet integrated** · Champion: **Darrin Rankin** · IIANC cohort · HQ Huntersville, NC · 3 employees (founded 2001) · Domain `rankininsurancegroup.com`. OS notes: "Voice quote intake | Expansion: IIANC cohort | EasyLynq AMS integration. Discovery pages being tested." OS next_step: "Phase 2 expansion meeting; formalize $500/mo voice baseline SKU as 12mo contract. Ian operational; Cam decision."
**Sources reviewed:** OS Company entity · MongoDB tiledesk via SSM into prod-services bot-service container (7 V1 platform agents · 7 KBs · structure_customers entry id `696e9eef5bcfbb381289b4b6` with 7 agents / 73 integration tools / 4 call_control / 3 escalation / 3 knowledge — agent-channel breakdown via pymongo) · indemn-observatory voice retrospective `Rankin_Insurance_Group_Voice_Retrospective_2026-02-24_to_2026-03-09.pdf` (51 calls / 39 unique callers) + voice daily report `Rankin_Insurance_Group_Voice_Daily_2026-02-05.pdf` · GitHub (no Rankin-specific custom repo — runs on shared V1 platform; only references are in `indemn-observatory/scripts/extract-voice-data.py --org rankin` + `indemn-observatory/data/structure_platform.json`) · Slack `#indemn-rankin` (`C0A9X1U4Y7N` private) + `#indemn-rankin-daily-reporting` (`C0ADW070L3F` private). **No Drive presence** — `drive_folder_url: null` on Company; no Cam proposal in portfolio (verified empty in `1k0_SYLdYtlM40y6W-ZAMV3Trr9hIq2Ph`).

**Material context:** Small independent agency (3 employees, founded 2001, IIANC cohort — same network family as O'Connor). Runs entirely on **shared Indemn V1 platform** — no custom code repos, no Indemn-built customer-specific Railway services. Two production agents post daily summaries to `#indemn-rankin-daily-reporting` (B0AE17EV2F4 bot): voice (Ronnie2) + web chat (faq bot using "James - Sales Agent" KB+persona). Active Indemn engagement — recent Slack activity (Apr 30) shows agent improvements continuing (issue #442 "anchored to current time", issue #395 caller-phone capture). Multiple historical bot iterations exist in tiledesk (Ronnie v1, Ronnie3 DEV, Bernadette voice sales, Peter voice service, Rankin service web, Rankin voice agent #1) — superseded by current production agents.

#### Confirmed associate mapping — 2 distinct associates (per task-bundling rule)

2 production agents, 2 distinct objectives, no AI orchestration → 2 distinct associates.

**1. Front Desk Associate (Agency/Broker tier — Rankin variant; production)**

Constituent agent: `Ronnie2, for Rankin Insurance` (voice, bot_id `697259edec2b21075fda6439`, model n/a in ai_config metadata). Multi-intent inbound voice front desk: greets caller → identifies intent → captures caller name + contact + summary → posts to staff queue (Slack daily-reporting channel + portal link). **Message-taking-and-callback model — explicitly does NOT transfer calls** (per system_prompt: "as an enhanced intake assistant you capture messages and schedule callbacks, you do not transfer calls").

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| Inbound voice multi-intent triage with message-taking + caller identity capture + after-hours + voicemail (Ronnie2 — distinct from O'Connor's billing-only deflection) | KB retrieval · Business-hours lookup (@bizHoursLookup) · Human handoff escalation (dashboard + Slack routing, NOT call transfer) | Voice (in only — no call transfer out) | Indemn Copilot · Twilio · LiveKit · Cartesia |

KBs: Rankin provided PDFs · Rankin Sitemap KB · Payment Phone Numbers KB.

Volume signal (Voice Retrospective Feb 24 - Mar 9 = 13 days): 51 calls · 39 unique callers · 39% handoff rate · 33% caller name captured · 33% contact info captured · 5 after-hours · 1 voicemail. Call reasons: General Inquiry 18 · No Interaction 19 · New Quote 8 · Renewal 3 · Policy Change 1 · Billing 1 · Cancellation 1.

**Distinguishing features vs O'Connor's Front Desk Associate** (Sandy + Coral/Gráinne, path-044/045):
- **Multi-intent vs billing-only.** Rankin Ronnie2 routes all 7 intent types; O'Connor scoped to billing inquiry deflection.
- **Message-taking vs call transfer.** Rankin captures caller info + summary + posts to staff; O'Connor's Sandy/Coral/Gráinne do call transfer to humans.
- **No payment information dispensed via tool/integration** — payment numbers come from a "Payment Phone Numbers KB" (KB-only retrieval, no transactional integration).

**2. Lead Associate (Agency/Broker tier — Rankin variant; production)**

Constituent agent: `faq bot` using "James - Sales Agent" KB + first_message persona ("Hello. My name is James, The Rankin Insurance Group's Sales Associate.") (web chat, bot_id `6953c726922e070f5efb57f1`). Sales lead qualification: new vs existing → insurance type → Personal vs Commercial routing → Universal Lead Capture → product-specific intake. **KB-backed Q&A folded in inside strict boundaries** (per system_prompt: no quote / no eligibility confirmation / no policy interpretation / no service tasks; existing-customer service request → @Live Handoff).

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| Sales lead qualification + Universal Lead Capture + Personal/Commercial routing + product-specific intake (with bounded KB Q&A folded in) | KB retrieval · Lead generation capture · Personal vs Commercial routing · Human handoff escalation | Web chat | Indemn Copilot |

KBs: Default Knowledge Base · Rankin Sitemap KB · Rankin provided PDFs.

#### Other agents in tiledesk (NOT production — historical iterations)

- `rankin voice agent #1` (bot_id `6952d6c9922e070f5efa63de`) — earliest voice iteration
- `Ronnie, reception for rankin` (bot_id `696a321bec2b21075fcb8b2f`) — voice v1 reception
- `Ronnie3 (DEV)` (bot_id `69821c06803dd0ae1471c557`) — dev/test of Ronnie
- `Bernadette, sales agent for rankin insurance` (bot_id `695c43f3922e070f5e057ed6`) — voice sales (likely superseded by James web chat)
- `Peter, service agent for rankin` (bot_id `695c4610922e070f5e058281`) — voice service (likely superseded by Ronnie2 message-taking model)
- `Rankin service` (bot_id `696158c8922e070f5e1126ea`) — webchat service variant

Per Slack daily-reporting traffic (B0AE17EV2F4 bot posting recent summaries), only Ronnie2 (voice) and faq bot/James (web) are receiving live customer traffic. Older agents not in the active reporting set.

#### Notes for Rankin

- **No Cam proposal in portfolio** — `drive_folder_url: null` on Company entity; manually verified empty for Rankin in Cam's portfolio folder. OS notes refer to a "Phase 2 expansion meeting" pending; no formal proposal document in standard portfolio.
- **No Rankin-specific code repo** — Rankin runs entirely on shared Indemn V1 platform. All bot configs in tiledesk; no Indemn-built customer-specific Railway services (unlike Branch's claims-mcp-server / branch-aria-documents / branch-ivr-webhook stack).
- **Easy Links AMS / EasyLynq integration is future state.** Same pattern as O'Connor's BT Core (future). When Phase 2 lands, this becomes a new system — likely web operator since EasyLynq has no public API surface visible.
- **IIANC cohort** — Independent Insurance Agents of NC; same network family as O'Connor. Future cohort expansion would reuse Rankin's pathways.
- **Discovery pages testing** (per OS notes) — UI/widget A/B testing on customer-side; not surfacing as a separate skill or system.
- **Bond Insurance** appears in James' supported offerings in the system_prompt (alongside Auto/Home/Renters/Life/Pet/Business). Footnote — not surfaced separately as a load-bearing product line at this stage.

#### Catalog notes

- **No new Cam-catalog gaps** from Rankin. Front Desk Associate (Agency/Broker, $1,000/mo) and Lead Associate (Agency/Broker, $0.50/ticket) both already exist in Cam's tier.
- **Pricing observation (factual, Craig owns):** OS notes reference "$500/mo voice baseline SKU" — half of Cam's $1,000 Front Desk Agency/Broker rate. Possible explanations include IIANC cohort pricing, smaller agency size, or pre-AMS-integration scope. `[Craig owns pricing — flagging for visibility, no editorialising]`

#### New tool skill surfaced

- **tool-049 Business-hours lookup** (@bizHoursLookup) — Ronnie2 calls this immediately after call init to determine open/closed status against 8am-5pm EST hours; drives after-hours routing and voicemail behavior. Generalizable to any voice agent that needs hours-aware routing. Added to §7 tool skills catalog.

`[no Core/Soon/Enterprise classification, no LOE estimates, no reusability claims — Craig owns those]`

---

### 8.10 Tillman Insurance Advisors `[in-progress — facts]`

**OS entity refs:** Company `69e41a7db5699e1b9d7e98db` · Cohort: Graduating · ARR null (**pre-revenue**) · Stage: pilot · Type: Broker · AMS: **Hawksoft** (same system as GR Little) — **NOT yet integrated** · Champion: **Raquel** · IIANC cohort · 20-agent agency · Drive folder url: null. OS notes: "**Bilingual (English+Spanish) = differentiating capability.** 20-agent agency. Hawksoft AMS integration. Pre-revenue." OS next_step: "Ground-truth call with Raquel — confirm March go-live happened. **No contact post-Mar 27.** Then $500/mo voice baseline 12mo SKU."
**Sources reviewed:** OS Company entity · MongoDB tiledesk via SSM into prod-services bot-service container (5 V1 platform agents · 5 KBs · 63 tools · structure_customers entry id `696e9eef5bcfbb381289b4b9`, customer_id `69551cad922e070f5efdb54e`) · Drive: `Tillman Functions` (Jan 12, architectural overview of sales assistant flow) + `Tillman Sales Advisor (Emma) — Conversation Analysis` (Apr 16, sheet — recent analysis on Emma webchat) · GitHub: no Tillman-specific custom repo (only references in `indemn-observatory` aliases — observatory org `69551cbe922e070f5efdb56f`, "Harper bot multilingual Spanish calls" reference suggests an older voice agent name now superseded) · Slack: **no `#indemn-tillman` channel exists** (different from Rankin's 2 channels). **No Cam proposal in portfolio** (`drive_folder_url: null`).

**Material context:** 20-agent independent agency, IIANC cohort (same network family as O'Connor + Rankin). **Bilingual EN+ES is the load-bearing differentiator** — every agent (voice + web) handles language switching. Pre-revenue / pilot. "No contact post-Mar 27" + no dedicated Slack channel suggests dormant or uncertain go-live state — but per built-only rule, all agents catalog-eligible regardless of live status. Runs entirely on shared Indemn V1 platform — no custom code repos.

#### Confirmed associate mapping — 2 distinct associates (per task-bundling rule, Craig 2026-05-01)

5 production-shape agents in tiledesk, 2 distinct objectives, no AI orchestration → 2 distinct associates. Front Desk Associate bundles voice reception (Maria/Donna Mae) and webchat service-intake (Emery) under one row; Lead Associate bundles voice (Nolan) and webchat (Emma) sales qualifiers — same shape across channels.

**1. Front Desk Associate (Agency/Broker tier — Tillman variant; bilingual specialty; production)**

Three constituent agents under one associate:
- `Maria, Receptionist for Tillman Insurance (copy)` (voice, bot_id `69f17c38e33f0767bad3506a`) — newest with sophisticated linguistic-compass tooling (@LinguisticGuide, @NameReadback, @NameSpellBack, @ClosingGate, @EmpathyAcknowledge); 18,382-char prompt; peak hours + after-hours + lunch routing
- `Donna Mae` (voice, bot_id `695c3df0922e070f5e057517`) — older simpler iteration of same role; identical first_message; has @checkBusinessHours (= same as Rankin's @bizHoursLookup, tool-049)
- `Tillman service agent` ("Emery", webchat, bot_id `69555ef9922e070f5efe3a6b`) — webchat service-request intake across personal/commercial/life/health/specialty

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| Bilingual EN+ES front-desk reception + service-request intake with multi-product routing (path-050) — deployed via Maria voice (peak/after-hours/lunch), Donna Mae voice (older iteration), Emery web (service-intake scope) | KB retrieval · Business-hours lookup (@checkBusinessHours = @bizHoursLookup, tool-049) · Bilingual handling / linguistic compass (tool-050) · Personal property insurance intake (tool-052) · Life insurance intake (tool-053) · Business insurance intake (tool-054) · Event insurance intake (tool-055) · Pet insurance intake (tool-056) · Human handoff escalation | Voice (in) · Web chat | Indemn Copilot · Twilio · LiveKit · Cartesia · Google Cloud Translate |

KBs: Maria's own KB1 · "Tillman Pages and Categories" (shared across Donna Mae + Emery + Nolan + Emma).

Distinguishing features: bilingual EN+ES is the differentiator (per OS notes); reception (Maria/Donna Mae) routes to "Term Advisor" not transfer; Emery is service-only (no policy access, no quote, no service actions — sets follow-up expectations).

**2. Lead Associate (Agency/Broker tier — Tillman variant; bilingual specialty; production)**

Two constituent agents under one associate (same objective, deployed across two channels):
- `Nolan, sales agent for Tillman Insurance` (voice, bot_id `695c3bbc922e070f5e057361`) — "Term Advisor"; Acknowledge-Illuminate-Probe rapport sequence
- `faq bot` ("Emma", webchat, bot_id `69551cbe922e070f5efdb59c`) — same shape, web channel

Sales lead qualification: new vs returning → Personal/Commercial/**Specialty** category (specialty includes Wedding/Event + Pet) → Universal Lead Capture (one time only) → product-specific intake routing → Live Handoff if returning-service or pricing/coverage interpretation.

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| Bilingual EN+ES sales qualification + Universal Lead Capture + multi-product intake routing across Personal/Commercial/Specialty (path-051) — deployed via Nolan voice ("Term Advisor", Acknowledge-Illuminate-Probe rapport) and Emma web (faq bot) | KB retrieval · Lead generation capture · Bilingual handling / linguistic compass (tool-050) · Auto insurance intake (tool-051) · Personal property insurance intake (tool-052) · Life insurance intake (tool-053) · Business insurance intake (tool-054) · Event insurance intake (tool-055) · Pet insurance intake (tool-056) · Personal vs Commercial vs Specialty routing · Human handoff escalation | Voice · Web chat | Indemn Copilot · Twilio · LiveKit · Cartesia · Google Cloud Translate |

KBs: "Tillman Pages and Categories" (shared with Front Desk).

#### Notes for Tillman

- **Bilingual EN+ES is the load-bearing differentiator** — surfaced consistently across all 5 agents' system_prompts. Maria has the most sophisticated implementation (linguistic compass + register-survival clause); Donna Mae, Nolan, Emery, Emma all explicitly handle Spanish. Tool-050 captures this as a shared formal skill.
- **Specialty insurance scope** — Wedding/Event + Pet are first-class supported product lines (similar to JM's EventGuard + ring engagement, but Tillman is Broker tier not MGA). Distinct from JM: Tillman's Event/Pet are intake-only (downstream advisor follow-up) whereas JM's are quote-generation.
- **Tillman Functions doc (Jan 12)** describes the sales assistant's 8-step flow (new/returning → category → Universal Lead Capture → product clarification → per-product intake tool → FAQs → handoff → final summary). Maps directly onto Nolan + Emma.
- **Hawksoft AMS integration is future state.** Same pattern as O'Connor's BT Core, Rankin's EasyLynq. Same AMS as GR Little — when Tillman AMS lands, GR Little likely reuses or vice versa (per cross-customer reuse caveat — directional, not guaranteed).
- **IIANC cohort** — 3 customers walked so far in this cohort (O'Connor, Rankin, Tillman). Future expansion within IIANC could reuse Tillman's bilingual capability (or not, per caveat).
- **Engagement status uncertain** — "No contact post-Mar 27" plus no dedicated Slack channel; Apr 16 Drive analysis on Emma is the most recent signal of active iteration.
- **Maria + Donna Mae** likely same-role iterations (newer + older); both built; both catalog-eligible. Maria is the more sophisticated current version.
- **"Harper" reference in observatory** — older voice agent name referenced in `indemn-observatory/scripts/extract-voice-data.py` and continuation prompt; no current bot named Harper in tiledesk; likely renamed to Donna Mae or Maria.

#### Catalog notes

- **No new Cam-catalog gaps** from Tillman. Per Craig 2026-05-01: Emery's webchat service-intake bundles under Front Desk Associate as a second pathway (with bilingual specialty), not a separate row.
- **Pricing observation (factual, Craig owns):** OS notes reference "$500/mo voice baseline 12mo SKU" — same baseline as Rankin, also half of Cam's $1,000 Front Desk Agency/Broker rate.

#### New tool skills surfaced

- **tool-050 Bilingual handling / linguistic compass** — formal tool skill (Craig confirmed). Captures @LinguisticGuide + register-survival clause + @NameReadback + @NameSpellBack + @ClosingGate + @EmpathyAcknowledge as one bilingual-handling capability bundle. Reusable for any bilingual EN+ES customer.
- **tool-051 Auto insurance intake** — per-product structured intake (Craig confirmed per-product as individual skills)
- **tool-052 Personal property insurance intake** — covers home/condo/renters/townhome/landlord/boat/motorcycle/RV/collectible
- **tool-053 Life insurance intake** — covers term/whole/universal/key person
- **tool-054 Business insurance intake** — covers BOP/GL/WC/commercial auto/E&O/property/contract variants
- **tool-055 Event insurance intake** — wedding/event (intake-only, distinct from JM EventGuard's tool-030 quote-generation)
- **tool-056 Pet insurance intake** — structured product-specific intake

#### Reused tool skill confirmed

- **tool-049 Business-hours lookup** — Tillman Donna Mae's `@checkBusinessHours` is the same skill as Rankin Ronnie2's `@bizHoursLookup` (different naming, same capability). Tool-049 entry updated with both customers.

`[no Core/Soon/Enterprise classification, no LOE estimates, no reusability claims — Craig owns those]`

---

### 8.11 Family First Inc. `[in-progress — facts; non-insurance / healthcare-caregiving outlier]`

**OS entity refs:** Company `69e41a7fb5699e1b9d7e98e2` · Cohort: AI_Investments · ARR $12K · Stage: customer · Health: 63 · Type: Other · Champion: **Ravi** · Owner: George · Status: **launched** (Craig 2026-05-01 — clarifying the OS note "Q1 decision: launch or exit"). Boston-based · 120 employees · $35.9M annual revenue · founded 2016 · `domain: family-first.com`. **Industry: hospital & health care — outlier in this walk; everyone else is insurance.** Specialties: caregiving, employee benefits, mental health, return to work, caregiver support, virtual care management, healthcare cost reduction. Tech: Hubspot + Microsoft 365 + Outlook (no insurance AMS — `ams_system: null`). OS notes: cases run up to 2 months · sensitive about compliance · asked for data flow diagram · self-funded portfolio expansion target.
**Sources reviewed:** OS Company entity · MongoDB tiledesk via SSM into prod-services bot-service container (12 webchat agents · 81 KBs · 22 tools · structure_customers entry id `696e9eef5bcfbb381289b4ac`, customer_id `67868dcc0110340013cae602`) · GitHub `indemn-ai/evaluations` (Family First bot ID is DEFAULT_AGENT_ID for evals; "Family First Golden Set" in seed_data) + `copilot-dashboard-react` (Family First AI Assistant config) + `fragments/000-promptkit-webchat` (Family First Care Library config) + `indemn-website-v2` + `discovery-chat-ui` (partner listings) · Drive `Family First Test Set + Rubric: Live` (Apr 30 2026, 657KB) — recent golden-set eval rubric · Slack: **no `#family-first` channel exists** · **No Cam proposal in portfolio.**

**Material context:** Family First sells a **caregiving support AI as an employee benefit** — companies buy it for their employees who are also caregivers in their personal lives (childcare, eldercare, mental health, medication, financial/legal). Users are working professionals supporting family members. This is fundamentally **different from every other customer in the walk** — Family First isn't insurance. Per Craig 2026-05-01, **map to Knowledge Associate (Agency/Broker tier)** as the closest catalog shape match (KB-driven Q&A with retrieval), even though Cam's description ("policy forms, claims manuals, filing documents") is insurance-flavored. Healthcare-flavored Knowledge Associate framing is implicit.

#### Confirmed associate mapping — 1 associate (per Craig 2026-05-01)

12 webchat agents, all doing the same task (Care Library Q&A with empathy + safety triage + Care Expert escalation), differing by topic specialization (eldercare/childcare/mental health/etc.) or iteration stage (prototype/staging/dev) → **1 Knowledge Associate** (Family First variant) with topic specialization as deployment variants. Same precedent as DP's Knowledge Associate with 5 specialization variants.

**Knowledge Associate (Agency/Broker tier — Family First variant; healthcare-caregiving flavor; production / launched)**

Constituent agents (12 total):
- `eldercare ai agent (prototype)` — bot_id `6834acd94ae4060013f3e747` — **canonical** (referenced in evaluations seed as DEFAULT_AGENT_ID; full 30,202-char system_prompt with empathy/safety/brevity rules; 13 KBs spanning the whole Care Library)
- `[proto: testing improvements] go-live candidate` — bot_id `68a60746ab912b0013679899` — active iteration toward go-live
- `vg 12/5/2025 dev` — bot_id `69333b53d212860013b4f652` — dev
- `[staging] go-live candidate - url` — bot_id `68b2e6d933ea0e0013233e5b` — staging; adds external resources (va.gov, cms.gov, alz.org, Meals on Wheels, aarp.org)
- 8 topic-specialized variants: `empathybot`, `homecare`, `mental and behavioral health`, `eldercare`, `long term care vertical`, `faq bot`, `childcare`, `health insurance, finance and legal vertical`

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| Caregiving multi-topic Care Library Q&A with empathy + safety triage + Care Expert escalation (path-052) — deployed via canonical eldercare ai agent + 8 topic-specialized variants + go-live iterations | KB retrieval · Emergency redirection (tool-057 — 911/988/Poison Control) · Human handoff escalation (Care Expert email follow-up pattern — distinct from immediate live transfer) | Web chat | Indemn Copilot |

KBs (81 total): Care Library covers 12 topical verticals as URL-backed KBs (Alzheimers, Eldercare, Childcare, Mental & Behavioral Health, Health Insurance Counseling, Health Issues, Family Dynamics, Financial and Legal, Caregiver Support, Absence Leave and Disability, Long-term Care, Caregiving) · Family First office details + welcome scripts · Externally-referenced resources (va.gov, cms.gov, alz.org, Meals on Wheels, aarp.org).

#### System prompt — load-bearing rules (canonical bot)

The canonical agent's 30,202-char system_prompt encodes critical product rules:
- **Empathy + acknowledgment discipline** — validate concern in one sentence; don't hedge ("It sounds like…"); don't repeat empathy openers across consecutive responses; don't patronize
- **Emergency redirection** (formal tool skill, tool-057):
  - Acute physical events (fall, injury, head impact) → 911, no triage checklist
  - Psychiatric / self-harm risk → 988
  - Medication issues (mix-ups, wrong doses, suspected reactions) → Poison Control 1-800-222-1222 / pharmacist / doctor / 911 if severe
- **Prevention vs Response distinction** — "How do I prevent falls?" → KB; "My mother fell" → 911
- **Brevity rules** — 3-4 crisp bullets max; stressed users can't absorb complexity (pathway-internal)
- **Assumption guardrails** — never infer age/stage/condition unless user explicitly stated; don't assume "Alzheimer's" from "trouble remembering"; ask one clarifying question for age-specific topics; never default to toddler/infant/senior unless stated (pathway-internal)
- **Resource provision** — only provide Care Library links when asked; resources must directly address user's stated question
- **Care Expert escalation pattern** — team contacts user via email afterward (no live transfer); use "Our Care Experts will…" never "Let's connect you…"; hard handoff for distressed users + safety cases (skip KB tool entirely)

#### Notes for Family First

- **Outlier customer** — non-insurance; mapped to Knowledge Associate (Agency/Broker) per Craig 2026-05-01 as closest shape match. Cam's description ("policy forms, claims manuals, filing documents") is insurance-flavored but the underlying capability (KB-driven Q&A with retrieval + escalation) fits.
- **Production / launched** — per Craig 2026-05-01, the OS note "Q1 decision: launch or exit" was resolved as **launched**. The OS note is stale.
- **Evaluation-centric product** — accuracy is the primary deployment gate. Family First bot is the DEFAULT_AGENT_ID in `indemn-ai/evaluations`; recent test set + rubric uploaded Apr 30 2026. Healthcare AI accuracy bar is materially higher than insurance-context Q&A.
- **Care Expert email handoff** is a distinct escalation pattern (vs immediate live transfer) — Care Expert team follows up via email asynchronously. Not formalized as a separate tool skill; treated as a deployment variant of human handoff escalation per the system_prompt language.
- **No voice channel** — all 12 agents are webchat only.
- **No insurance-specific AMS or carrier integrations** — `ams_system: null`. Tech stack is Hubspot + Microsoft 365.
- **Compliance sensitivity** — OS notes mention Ravi's request for a data flow diagram + privacy/security documentation. Healthcare context drives stricter compliance requirements than the rest of the customer portfolio.

#### Catalog notes

- **No new Cam-catalog gaps from Family First** per Craig — Knowledge Associate (Agency/Broker) is the mapping. Healthcare-caregiving framing is treated as a customer-specific instance of the existing row, not a separate row.

#### New tool skill surfaced

- **tool-057 Emergency redirection** — formal tool skill (Craig 2026-05-01: "maybe emergency redirection"). Captures 911 (acute medical/physical) · 988 (psychiatric/self-harm) · Poison Control 1-800-222-1222 (medication issues) routing logic with prevention-vs-response distinction. **Reusable for any future healthcare/caregiving customer.** Family First is the first customer using it.

`[no Core/Soon/Enterprise classification, no LOE estimates, no reusability claims — Craig owns those]`

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

### 8.21 Alliance Insurance Services `[in-progress — facts; treated as active customer per Craig 2026-05-01]`

**OS entity refs:** Company `69e41a82b5699e1b9d7e98eb` · Type: Broker · Cohort: Prospect (per OS — **Craig 2026-05-01: treat as active customer; "if we built it, they're a customer to me"**) · Stage: pilot · Source: IIANC cohort (same network family as O'Connor, Rankin, Tillman). Champion (per CLAUDE.md, not in OS): **Christopher Cook**. Most descriptive fields null in OS (ARR, domain, AMS, etc.). OS notes: "IIANC cohort. Documents to ingest as KBs. **BT Core AMS connection next.**" OS next_step: "Ship updated proposal Apr 26. Renewal Machine pilot 4-6wk. New wedge: renewals + coverage-gap + CSR prep. Owner: Kyle + Cam." **No `#indemn-alliance` Slack channel.**
**Sources reviewed:** OS Company entity · MongoDB tiledesk via SSM into prod-services bot-service container (5 production-shape agents · 7 KBs · 43 tools · structure_customers entry id `696e9eef5bcfbb381289b4b5`, customer_id `694ab741feba9ede7a9663a4`) · Drive: `Alliance Insurance Services Proposal 4-27-26 (v2 — Renewal Stewardship Wedge).pdf` (Apr 28, current) · `Alliance Insurance Services Proposal 2-11-26` (v1, superseded) · `Alliance Insurance Services Proposal 2-12-26.pdf` (v1 PDF, superseded) · GitHub: no Alliance-specific custom repo (only `indemn-observatory/data/structure_platform.json` reference; runs on shared V1 platform).

**Material context:** Alliance is the most-deeply-traced customer in the project's history (Phase A trace work Apr 27 produced v2 proposal via Artifact Generator, 60+ entities hydrated in dev OS). 5 production-shape agents in tiledesk built **Dec 2025–Jan 2026** (predate the v2 wedge pivot — built during the v1 strategy phase). Per built-only rule, the 5 currently-built agents are catalog-eligible regardless of v2 strategic direction. **No BT Core AMS integration yet** (Phase 1 setup pending). **English-only currently** (bilingual ES + Vietnamese is future state per v2 proposal). Same broad shape as O'Connor's 3-associate split, but with Lead instead of Knowledge for the customer-sales side.

#### Confirmed associate mapping — 3 distinct associates (per Craig 2026-05-01)

5 production-shape agents, 3 distinct objectives, no AI orchestration → 3 distinct associates. Same overall shape as O'Connor's split (Front Desk + Knowledge + Ticket), with Lead substituted for Knowledge.

**1. Front Desk Associate (Agency/Broker tier — Alliance variant; production)**

Two constituent agents under one associate (same objective, voice + web channels):
- `Haley, service agent for Alliance Ins` (voice, bot_id `69580e8d922e070f5e011167`) — silent call init logging; identify customer + policy context (personal vs business); classify service request type; collect intake details; route to CSR
- `Alliance service intake agent` (webchat, bot_id `695d6f1a922e070f5e088686`) — same shape on web; "Alliance Insurance Services Service Intake AI Agent" — collects info, sets follow-up expectations; no policy access / no quotes / no service actions

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| Customer service intake/classification/routing (path-053) — deployed via Haley voice and Alliance service intake webchat | KB retrieval · Human handoff escalation · Voice call transfer | Voice (in) · Web chat | Indemn Copilot · Twilio · LiveKit · Cartesia |

KB: Alliance Pages KB (shared across customer-facing agents).

**2. Lead Associate (Agency/Broker tier — Alliance variant; production)**

Two constituent agents under one associate:
- `Colter, sales agent for Alliance Ins` (voice, bot_id `6958102d922e070f5e011d2c`) — Acknowledge-Illuminate-Probe rapport sequence (same pattern as Tillman Nolan); qualify-capture-connect; no quote/bind/recommend
- `Alliance sales agent` (webchat, bot_id `695d3cf5922e070f5e06f2b5`) — Universal Lead Capture pattern; personal vs commercial vs service-related routing; English-only ("Always respond in English")

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| Customer sales qualification + Universal Lead Capture + product-specific intake routing (path-054) — deployed via Colter voice and Alliance sales agent webchat | KB retrieval · Lead generation capture · Personal vs Commercial routing · Human handoff escalation · Voice call transfer | Voice · Web chat | Indemn Copilot · Twilio · LiveKit · Cartesia |

KB: Alliance Pages KB.

**3. Ticket Associate (Agency/Broker tier — Alliance variant; production; INTERNAL employee-facing)**

Constituent agent: `faq bot` (webchat, bot_id `694aba9bfeba9ede7a966f40`). **Internal AI Assistant — supports employees, leadership, and internal teams** by answering frequently asked questions using the most current "State of the Agency" information, internal updates, and operational guidance. Not customer-facing. Different content from O'Connor's internal agent (HR/benefits/employee handbook → State of the Agency at Alliance).

| Pathways | Tool skills | Channels | Systems |
|---|---|---|---|
| Internal employee "State of the Agency" Q&A (path-055) — agency performance + priorities + monthly/quarterly updates + staffing/recruiting/training + leadership comms; reduces confusion + rumor by grounding in known facts | KB retrieval · Human handoff escalation | Web chat | Indemn Copilot |

KBs: Default Knowledge Base · State of the Agency KB · Internal KB.

#### Other agents in tiledesk (NOT production-shape — older / staging iterations)

Per `bot_configurations` regex match, additional Alliance bots exist:
- `alliance insurance services` (bot_id `6942fe4dd212860013dd73b2`, Dec 17 2025) — earliest iteration
- `alliance state of the agency` (bot_id `6952b632922e070f5ef9944c`, Dec 29 2025) — earlier State-of-the-Agency variant; superseded by the production faq bot

These predate the Jan 2-6 production-shape build wave; not currently in structure_customers' active set.

#### Notes for Alliance

- **Treated as active customer per Craig 2026-05-01** (vs OS field showing Cohort: Prospect / Stage: pilot — those fields are stale; the built work is what matters).
- **Same 3-associate pattern as O'Connor** (Front Desk + Knowledge + Ticket), with **Lead substituted for Knowledge** because Alliance's webchat sales agent does qualification + Universal Lead Capture (lead-flavored), while O'Connor's external agent has strict no-quote/no-pricing/no-coverage-advice boundaries (knowledge-flavored). Same network family (IIANC cohort) — O'Connor, Rankin, Tillman, Alliance.
- **No BT Core integration currently** — proposed for Phase 1 Day 1-7 setup per v2 proposal; not yet active. When BT Core lands, that's a new system (likely web operator unless Alliance has API access — to confirm at activation time).
- **No bilingual capability currently** — English-only across all 5 agents. Bilingual ES + Vietnamese is future state per v2 proposal Phase 2.
- **Acknowledge-Illuminate-Probe rapport pattern** appears on both Colter (Alliance) and Nolan (Tillman) voice sales agents — voice-sales discipline pattern, treated as pathway-internal (not a discrete tool skill).
- **Carrier-Exit Cohort** mentioned in v2 proposal: Main Street America + NGM Insurance prioritized for Retention Associate proof set. Operational context, not currently-built.
- **Internal Q&A content domain** ("State of the Agency") is meaningfully different from O'Connor's path-047 (HR/benefits/employee handbook). New pathway per Craig 2026-05-01, parallels O'Connor's Ticket Associate skill but different KB scope.

#### Catalog notes

- **No new Cam-catalog gaps** from Alliance's currently-built work. Front Desk Associate (Agency/Broker, $1,000/mo) · Lead Associate (Agency/Broker, $0.50/ticket) · Ticket Associate (Agency/Broker, $0.50/ticket) all exist.
- **No new tool skills surfaced.** All capabilities map to existing skills in the catalog.
- **v2 proposal phases (Retention Associate compound · bilingual Lead Capture · High-Automation Tier · BT Core integration) are NOT cataloged** per built-only rule — proposed, not yet built. Revisit when each lands in production.

`[no Core/Soon/Enterprise classification, no LOE estimates, no reusability claims — Craig owns those]`

---

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

## 9. Phase B — Per-associate sweep across all 47 Cam rows `[next]`

The customer walk (§8) populated §§5-7 catalogs from observed work — skills/channels/systems that surfaced because some customer deploys them. **Many Cam rows have no current customer deployment** (Care Associate, Cross-Sell Associate, Strategy Studio, Dashboard Associate, Authority Associate, Submission Associate, Risk Associate, Orphan Associate, etc.). To get **complete** skill coverage per row, Phase B *derives* the skills/channels/systems for un-deployed rows from Cam's description.

### What Phase B produces

For each of Cam's 47 deployable rows:

| Field | Source | Notes |
|---|---|---|
| **Skills (tool + pathway)** | (a) Catalog from §7 if customer-deployed, OR (b) derived from Cam's description if not | Reuse existing catalog entries where they fit; new entries only when truly novel |
| **Channels** | (a) Observed from §5 if customer-deployed, OR (b) likely channels per the row's job-to-be-done | E.g., Care Associate ($1K Agency/Broker — "Proactive Client Communication") likely uses outbound voice + email + SMS based on description |
| **Systems / integrations** | (a) Observed from §6 if customer-deployed, OR (b) likely systems per the row's job-to-be-done | E.g., AMS for renewal-flavored associates; CRM for sales-side; carrier APIs for Quote/Placement |
| **Qualifying questions** | Carry forward Craig's existing Working Copy annotations + add new ones surfaced in this pass | Sales-side qualification — what disambiguates this row's deployment shape |
| **Developed status** | `developed` (≥1 customer running) / `partially developed` / `not developed yet` | Status flag for productization analysis |
| **Customers active** | List of customers from §8 running this row (or close-to-it) | Surface co-deployments — "which associates are most frequently deployed together" per Cam's call-action item |

### How Phase B works

Sequential pass through Cam's 47 rows. For each row, surface findings to Craig + propose skill list + discuss + only write to §9 sub-sections after agreement. Same discipline as the §8 customer walk.

### Phase B sub-output sections

§9.1 Agency/Broker rows (12 deployable + 2 strategic) · §9.2 Carrier rows (12 deployable + 1 strategic) · §9.3 MGA rows (16 deployable + 1 strategic) · §9.4 In-development rows (8) · §9.5 Cross-tier observations (which skills appear across multiple Cam tiers; co-deployment patterns).

`[Tier classifications — Core/Soon/Enterprise — remain Craig's to author. Phase B captures the structure, Craig classifies.]`

### §9.1 Agency/Broker rows

#### Row 1 — Care Associate ($1,000/mo, "Proactive Client Communication")

> Cam description: "Automated policy review scheduling and personalized client outreach (e.g., birthday greetings, weather alerts)."

**Pathway skill:** Personalized proactive customer outreach (retrieve customer milestones or external trigger → generate personalized message → dispatch)

**Tool skills:** Customer profile retrieval (AMS/CRM read) · Outbound message dispatch · Personalization templating

**Channels:** Text · email · phone

**Systems:** AMS · CRM · weather API (or equivalent external trigger source)

**Example triggers:** birthdays · policy anniversaries · weather alerts

**Customers active:** None.

**Status:** not developed yet.

#### Row 2 — Renewal Associate ($50/seat, "The 'Silent Churn' Defender")

> Cam description: "Automatic review of personal and commercial lines renewals, flags premium increases, and drafts 'remarket' or 'review' email for the agent."

**Pathway skills:**
1. Renewal queue review + premium-increase flagging
2. Remarket vs review classification
3. Producer-facing renewal email drafting
4. Multi-channel customer renewal outreach + data collection (escalation handling folded in — legal/BOR immediate, classification/exposure/low-confidence) — INSURICA MARA pattern (path-012)

**Tool skills:** AMS read (renewal queue, premium history) · CRM read/write · Outbound message dispatch · Email drafting (personalized) · Disposition state-machine tracking

**Channels:** Email · text · phone · web chat

**Systems:** AMS · CRM (Salesforce at INSURICA)

**Customers active:** INSURICA (pathway 4 only — multi-channel outreach with escalation).

**Status:** pathway 4 developed (INSURICA, path-012); pathways 1-3 not developed yet.

#### Row 3 — Front Desk Associate ($1,000/mo, "Receptionist Functions")

> Cam description: "Handles high-volume inbound inquiries freeing up CSRs for complex advisory tasks." Existing Working Copy: "Qualification needed to define whether this is overflow, after hours, etc."

**Pathway skills:**
1. **Reception + routing** — caller arrives → identify intent → capture caller info → route to right human (or take message + post to staff queue when no transfer model). Generalizes path-048 (Rankin), path-050 (Tillman), path-053 (Alliance).
2. **Single-purpose request intake + submission** — caller wants a known service (e.g., ACORD 25 cert) → collect specific intake form → submit. Generalizes path-014 (INSURICA).
3. **KB-driven inquiry deflection** — caller asks a question with known answer in KB → respond from KB, no intake, no transaction. Generalizes path-044 (O'Connor multi-carrier billing).

**Tool skills:** KB retrieval · Customer profile read (when AMS connected) · Intake form capture (per request type) · Form/request submission · Caller identity capture · Voicemail capture · Business-hours lookup (tool-049) · Bilingual handling (tool-050) · Human handoff (two flavors: call transfer vs message-take-and-route) · After-hours routing

**Channels:** Voice · text · web chat · email

**Systems:** AMS · CRM · downstream submission systems (per intake type)

**Customers active:** INSURICA, O'Connor, Rankin, Tillman, Alliance (5 — most-deployed Agency/Broker row).

**Status:** all 3 pathways developed across customers.

#### Row 4 — Inbox Associate ($50/seat, "Smart Inbox")

> Cam description: "Pre-drafted emails regarding claims status or underwriting questions, allowing adjusters/underwriters to significantly increasing correspondence velocity." Existing Working Copy (yours): "This is not the same as shipping data from inbox into AMS. 'Your claim is being processed', simple underwriting questions"

**Proposed pathway skills:**
1. **Inbox triage + classification** — read incoming email → classify type (claims status / UW question / informational / etc.) → identify which require pre-drafted response
2. **Pre-drafted email response generation** — for classified emails, generate a draft response using KB + customer/policy context → surface to adjuster/underwriter for review + send

**Tool skills:** Email read (inbox poll) · Email classification · KB retrieval · Customer/policy context retrieval (AMS/CRM read) · Email draft generation · Draft surfacing for human review

**Channels:** Email (inbound + outbound)

**Systems:** Email server (Outlook/Gmail) · AMS · CRM · KB

**Customers active:** None (per your note, GIC's Quote Intake for AMS is *intake*, not Inbox-flavored response drafting).

**Status:** not developed yet.

#### Row 5 — Intake Associate ($5/ticket, "LOB Application")

> Cam description: "Automated Line of Business application processes"

**Proposed pathway skill:**
- **End-to-end LOB application processing** — receive application (email/PDF/form) → extract structured data → validate against rules/appetite → submit to carrier or AMS. (Cohesive end-to-end sequence, similar shape to path-003.)

**Tool skills:** Email/PDF/form ingestion · Document data extraction (OCR + structured) · Per-LOB intake form capture (Auto · Property · Life · Business · etc. — tool-051 to tool-056 reusable here) · Application validation against rules · Submission to carrier/AMS · Acknowledgment dispatch

**Channels:** Email · web form · web chat

**Systems:** Email server · AMS · Carrier portals/APIs · CRM

**Customers active:** None on Agency/Broker tier.

**Status:** not developed yet.

#### Row 6 — Intake Associate for AMS ($1,000/mo, no JTBD)

> Cam description: "Automatic update of Agency Management System (AMS); eliminates the need for manual data entry and ensures data hygiene." Existing Working Copy (yours): "Dev time and ROI is based on the skills implemented... Every new carrier I add to the mix involves me creating a skill for automation of the quote submission to that carrier. For GIC: Quote Intake Associate for AMS but could be Endorsement Intake Associate for AMS."

**Proposed pathway skills (per-workflow, per your "every new carrier = new skill" framing):**
1. **Quote submission into AMS** — receive new quote (inbox source) → extract data → create quote + activity + task in AMS atomically. Generalizes path-003 (GIC).
2. **Carrier quote-back submission into AMS** — receive carrier-returned quote → submit quote-submission + activity into AMS. Generalizes path-004 (GIC, planned).
3. **Renewal automation into AMS** — pull renewal from carrier portal → extract data → update AMS. Generalizes path-008 + path-011 (Johnson ECM).
4. **Endorsement automation into AMS** — pull endorsement from carrier portal → extract data → update AMS. Generalizes path-009 + path-010 (Johnson ECM).

**Tool skills:** Email/inbox ingestion · Carrier portal navigation (implicit in `web operator` integration type) · Document data extraction · AMS write (quote create / activity create / task create / policy update / endorsement create) · Notification dispatch (Slack/Teams alert)

**Channels:** Email (inbox source) · Schedule (cron-based carrier portal scan) — typically no customer-facing channel

**Systems:** AMS (per customer: Unisoft / Applied Epic / BT Core / Hawksoft / Easy Links etc.) · Carrier portals (ECM, USLI, etc.) · Email server

**Customers active:** GIC (pathway 1 built; pathway 2 planned), Johnson (pathways 3 + 4 built — 4 ECM paths via Web Operator Framework).

**Status:** all 4 pathways developed for specific carrier × LOB combinations. Per your annotation, **each new carrier × workflow = new skill instance** — reuse is at the *framework* level (Web Operator Framework, gic-email-intelligence shape), not at the skill instance level.

#### Row 7 — Intake Associate for Claims ($1,000/mo, "First Notice of Loss")

> Cam description: "Automated intake of First Notice of Loss." Existing Working Copy: "web chat, voice, both? skills, integration"

**Proposed pathway skill:**
- **End-to-end FNOL intake** — receive notice of loss → identify customer + policy → collect structured loss details (date/time, location, parties involved, narrative, photo/document evidence) → submit to claims system → send acknowledgment.

**Tool skills:** Loss-detail intake capture · Photo/document upload capture · Customer/policy lookup (AMS read) · Claims system submission · Acknowledgment dispatch · Triage/severity classification

**Channels:** voice · web chat · text · email (multi-channel)

**Systems:** AMS · Carrier claims systems · Email · MMS (for photo evidence)

**Customers active:** None (Branch Colleen path-035 is *status* not intake — flagged as separate gap in §2.05).

**Status:** not developed yet.

#### Row 8 — Knowledge Associate ($50/seat, "Smart Process Library")

> Cam description: "Instantly retrieves answers from thousands of pages of policy forms, claims manuals, and filing documents, reducing research time from hours to seconds." Existing Working Copy (yours): "Gather sites or documents from the customer and put them into our knowledge bases. Build an agent prompt and KB retriever function... KB Development: 3-5h, Prompt Development: 3-5h, Testing/Evaluation: 2h" (LOE anchor for Phase C — total 8-12h.)

**Proposed pathway skills:**
1. **Bounded customer-facing KB Q&A** — retrieve answer from KB → respond with strict boundaries (no quote/no eligibility/no policy interpretation/no service tasks); route to human when out-of-scope or distressed. Generalizes path-046 (O'Connor) + path-052 (Family First).
2. **Internal staff KB Q&A** — research-time-reduction flavor described in Cam JTBD; no boundary discipline because audience is staff. Not deployed at Agency/Broker tier today.

**Tool skills:** KB retrieval (tool-005) · Source citation · Boundary detection · Emergency redirection (tool-057, healthcare flavor) · Human handoff escalation

**Channels:** Web chat · email · voice

**Systems:** KB infrastructure (Indemn Copilot KB) · external referenced resources

**Customers active:** O'Connor, Family First (Agency/Broker tier).

**Status:** pathway 1 developed; pathway 2 not deployed at Agency/Broker tier (similar shape exists at MGA tier — DP, UG — under separate Cam row).

#### Row 9 — Ticket Associate ($0.50/ticket, "Tier 1 Ticket Deflection")

> Cam description: "Resolves routine inquiries from staff without requiring IT or senior underwriting intervention." Existing Working Copy (yours): "Internal agent - requires KB from customer"

**Proposed pathway skill:**
- **Internal staff KB Q&A for routine inquiries** — retrieve answer from internal KB (HR/operational/process/agency-state) → respond → escalate to right human (IT/manager/senior staff) when out of scope. Generalizes path-047 (O'Connor) + path-055 (Alliance).

**Tool skills:** KB retrieval (tool-005) · Routine vs complex classification (deflection threshold) · Human handoff escalation

**Channels:** Web chat · email · (Slack/Teams plausible; not currently deployed)

**Systems:** Internal KB (Indemn Copilot KB with customer-supplied content) · ticket system (where escalations land)

**Customers active:** O'Connor, Alliance.

**Status:** pathway developed.

#### Row 10 — Cross-Sell Associate (2% of GWP, "Sales Assist")

> Cam description: "Automated cross-sell identification and outreach (e.g., Umbrella, Cyber), driving incremental revenue."

**Note:** Parallel concept exists in Cam catalog as "Risk Associate" (Carrier $250/LOB · MGA $1,000) with same JTBD — same shape, different tier pricing.

**Proposed pathway skills:**
1. **Cross-sell opportunity identification** — analyze customer book → identify monoline customers + coverage gaps relative to typical bundle (e.g., auto-only customer who'd benefit from Umbrella).
2. **Cross-sell outreach + lead capture** — outbound personalized message to identified customers with relevant cross-sell offer; capture interest; route warm leads to producer. Shares outbound-dispatch shape with Row 1 Care Associate.

**Tool skills:** AMS read (customer book analysis) · Coverage gap analysis · Outbound message dispatch · Personalization templating · Lead capture / response handling · CRM read/write

**Channels:** Text · email · phone

**Systems:** AMS · CRM

**Customers active:** None.

**Status:** not developed yet.

#### Row 11 — Lead Associate ($0.50/ticket, "24/7 Lead Engagement & Qualification")

> Cam description: "Instant inbound web lead triage via text or chat; qualification and appointment scheduling." Existing Working Copy (yours): "Dependent upon appointment scheduling tool"

**From §8 — most-deployed Agency/Broker row:**
- Silent Sport (path-031 — pilot), Rankin (path-049), Tillman (path-051), Alliance (path-054), Branch Sales/Lead (path-037), JM (path-025 with lead folded — MGA), UG Mobile Home (path-023 — MGA-tier gap)

**Proposed pathway skills:**
1. **Inbound lead engagement + qualification + Universal Lead Capture** — greet → identify need (insurance category, personal vs commercial) → capture lead data once → route to product-specific intake. Generalizes path-049, path-051, path-054, path-031, path-037.
2. **Appointment scheduling integration** — when qualified lead is ready for human follow-up, schedule appointment with producer (per your annotation "dependent upon appointment scheduling tool"). Not yet built.

**Tool skills:** KB retrieval · Lead generation capture · Personal vs Commercial routing · Per-product intake (tool-051 to tool-056) · Universal Lead Capture · Appointment-scheduling-tool integration (not yet built) · Bilingual handling (tool-050) · Human handoff escalation

**Channels:** Web chat · text · voice · email

**Systems:** Indemn Copilot · CRM · Appointment scheduling tool (per Working Copy — not yet integrated)

**Customers active:** Silent Sport, Rankin, Tillman, Alliance, Branch (Agency/Broker-flavored). UG, JM also do this work (MGA-tier — see §2.05 gap "Lead Associate missing from MGA tier").

**Status:** pathway 1 developed across 5+ Agency/Broker customers; pathway 2 not developed yet.

#### Row 12 — Dashboard Associate ($0, "Performance Dashboard & ROI Tracking")

> Cam description: "Provides granular visibility into ROI performance of AI associates."

**Conversational associate** — talks with staff/managers about associate performance metrics, ROI, and trends. Not customer-facing; staff-facing observability companion.

**Proposed pathway skill:**
- **Conversational performance + ROI Q&A** — user asks about associate performance (volume, deflection rate, handoff rate, sentiment, ROI, trends) → retrieve metrics from observability infrastructure → respond conversationally with summaries, drill-downs, time-series.

**Tool skills:** Metric retrieval (per-associate, per-period) · Time-series query · Aggregation/comparison calculation · Periodic-report generation · Trend analysis · Anomaly flagging

**Channels:** Web chat · email/Slack (scheduled-report delivery — Rankin daily-reporting Slack channel pattern)

**Systems:** Observability infrastructure (LangSmith, Langfuse) · Indemn-observatory repo · per-customer Slack/email integrations for report delivery

**Customers active:** Rankin (voice daily reports + retrospectives via observatory), Tillman (multilingual report patterns), Family First (evals dashboard) — observatory tooling exists; productized conversational Dashboard Associate not deployed as a standalone agent.

**Status:** partially developed (observability infrastructure + scheduled-report delivery exist); conversational customer-facing surface not built.

#### Row 13 — Strategy Studio ($0, "Tone & Brand Customization")

> Cam description: "Custom training of AI Associates to speak in the specific 'voice' and tone of the agency brand."

**Conversational associate** — talks with the customer to build/refine brand voice for their associate fleet. Not customer-facing; builder-facing.

**Proposed pathway skill:**
- **Conversational brand-voice/tone elicitation and customization** — agent interviews customer about brand voice attributes (tone, register, formality, jargon discipline, what to avoid, exemplars to mirror) → captures structured brand-voice config → encodes into system_prompts of all deployed associates for that customer → validates with live-test conversations.

**Tool skills:** Brand voice elicitation (interview prompts, questionnaire) · Sample-artifact analysis (parse customer marketing/comms for voice signals) · System_prompt voice-section drafting · Validation against brand exemplars · Live-test conversation for tone validation

**Channels:** Web chat (builder UI)

**Systems:** Brand-voice config storage · Associate config registry (where prompts get updated)

**Customers active:** Brand-voice authoring happens implicitly during every customer build (every system_prompt encodes voice/tone — see Family First empathy discipline, Tillman Acknowledge-Illuminate-Probe rapport, Rankin "trusted neighbor" framing, etc.). Not yet productized as a conversational standalone Strategy Studio.

**Status:** brand-voice authoring developed implicitly in build process; conversational standalone Strategy Studio not productized.

---

### §9.2 Carrier rows

#### Row 14 — Care Associate (Carrier, $1,000/mo, "Proactive Lapse Prevention")

> Cam description: "Automated payment status monitoring with proactive policyholder contact to resolve payment issues."

**Distinct from Agency/Broker Care (Row 1)** — that one is milestone/weather-driven outreach; this one is payment-status-driven lapse prevention.

**Proposed pathway skills:**
1. **Payment status monitoring** — periodic scan of policy payment status → identify lapse risks (late payment, declined card, upcoming due date)
2. **Lapse-prevention outreach** — outbound to at-risk policyholders → resolve payment (collect new method, retry charge, set up payment plan, route to billing team)

**Tool skills:** Payment status retrieval (carrier billing system read) · Lapse-risk classification · Outbound message dispatch · Stripe payment processing (tool-034 reusable) · Payment-plan setup · Customer profile retrieval

**Channels:** Voice · text · email

**Systems:** Carrier billing system · Stripe (or carrier-equivalent payment processor) · CRM

**Customers active:** Branch Sophie (path-036) — MGA-tier instance of this same shape.

**Status:** developed at Branch (MGA-tier instance); not deployed at Carrier tier specifically.

#### Row 15 — Orphan Associate (Carrier, $1,000/mo, "Direct & Orphan Book Management")

> Cam description: "Automated renewal processing for 'house accounts' or direct-written business, ensuring customers receive service continuity." Working Copy (MGA mirror): "30-90 days, dependent on # of communication channels and potential divergence between renewals"

**Proposed pathway skill:**
- **Orphan/house-account renewal stewardship** — for customers without an assigned producer (direct-written or orphaned post-producer-departure), run renewal lifecycle: identify upcoming renewals → reach out → collect updates → process renewal → ensure service continuity. Similar to Renewal Associate but unowned-book-flavored (no producer to draft for; system handles end-to-end).

**Tool skills:** AMS read (orphan-book identification, renewal queue) · Outbound message dispatch · Customer profile retrieval · Carrier renewal submission · Disposition tracking

**Channels:** Email · text · phone

**Systems:** AMS · Carrier renewal systems · CRM

**Customers active:** None.

**Status:** not developed yet.

#### Row 16 — Answer Associate (Carrier, $1,000/mo, "Product Expert")

> Cam description: "Central provision of 'source of truth' data for response to dynamic information requests." Working Copy (MGA mirror): "Similar to KB associate"

**Proposed pathway skill:**
- **Product-expert dynamic-info Q&A** — KB-backed answers about specific carrier products/programs/eligibility/forms; "source of truth" responses to internal/agent inquiries about product details.

**Tool skills:** KB retrieval · Source citation · Dynamic-info lookup (e.g., DP product lookup tool-046, DP capabilities lookup tool-047) · Human handoff escalation

**Channels:** Web chat · email · voice

**Systems:** Indemn Copilot KB · carrier product-data backends (Airtable-via-n8n at DP, etc.)

**Customers active:** DP (path-039 — MGA-tier instance, same shape).

**Status:** developed at MGA tier (DP); not deployed at Carrier tier specifically.

#### Row 17 — Inbox Associate (Carrier, $50/seat, "Smart Inbox")

> Cam description: "Pre-drafted emails regarding claims status or underwriting questions, allowing adjusters/underwriters to significantly increasing correspondence velocity."

Carrier-flavored: claims-status updates and UW questions framed for carrier-side underwriters/adjusters (not agency-side CSRs).

**Proposed pathway skills:**
1. **Inbox triage + classification** — read incoming email → classify type (claims status / UW question / informational) → identify which require pre-drafted response
2. **Pre-drafted email response generation** — generate draft response (claims-status update from carrier claims system, simple UW answer from KB) → surface to underwriter/adjuster for review + send

**Tool skills:** Email read (inbox poll) · Email classification · KB retrieval · Customer/policy context retrieval (carrier policy admin / claims system) · Email draft generation · Draft surfacing for human review

**Channels:** Email (inbound + outbound)

**Systems:** Email server · Carrier policy admin system · Claims system · KB

**Customers active:** None.

**Status:** not developed yet.

#### Row 18 — Intake Associate (Carrier, $1/ticket, "Automated Submission Triage & Data Extraction")

> Cam description: "Automated submission intake of emails and documents (SOVs, loss runs), extraction of key data points, population of underwriting systems, and triage of submissions based on complexity and appetite." Working Copy: "Dependent on # of documents to be trained and amount of data within each document"

**Proposed pathway skills:**
1. **Submission triage from email + documents** — receive submission → extract data from SOVs, loss runs, ACORD forms → classify/triage (in-appetite vs out-of-appetite, complexity tier)
2. **Underwriting-system population** — push extracted data into UW system (per-carrier integration)

**Tool skills:** Email/document ingestion · OCR + structured data extraction · Submission classification · UW-system write · Appetite verification · Triage routing

**Channels:** Email (primary) · web form

**Systems:** Email server · Carrier UW systems · OCR/extraction pipeline

**Customers active:** GIC (Fred Workers Comp voice prototype — MGA-tier WC variant per §8.1 mapping), UG (intake-manager — MGA-tier).

**Status:** developed at MGA tier; not deployed at Carrier tier specifically.

#### Row 19 — Intake Associate for Claims (Carrier, $1,000/mo, "First Notice of Loss")

> Cam description: "Automated intake of First Notice of Loss."

Carrier-flavored: FNOL flowing direct to carrier claims systems (no agency intermediary).

**Proposed pathway skill:**
- **End-to-end FNOL intake** — receive notice of loss → identify policyholder + policy → collect structured loss details (date/time, location, parties involved, narrative, photo/document evidence) → submit direct to carrier claims system → send acknowledgment.

**Tool skills:** Loss-detail intake capture · Photo/document upload capture · Policyholder/policy lookup (carrier policy admin) · Claims system submission · Acknowledgment dispatch · Triage/severity classification (urgent vs routine)

**Channels:** Voice · web chat · text · email

**Systems:** Carrier claims system (direct, no AMS) · Email · MMS

**Customers active:** None.

**Status:** not developed yet.

#### Row 20 — Knowledge Associate (Carrier, $50/seat, "Smart Process Library")

> Cam description: "Instantly retrieves answers from thousands of pages of policy forms, claims manuals, and filing documents, reducing research time from hours to seconds."

Carrier-flavored content: carrier policy forms, filing manuals, appetite docs, product specs.

**Proposed pathway skills:**
1. **Bounded customer-facing KB Q&A** — retrieve answer from carrier KB → respond with strict boundaries (no quote, no eligibility confirmation, no policy interpretation); route to human when out-of-scope. Audience typically agents/brokers consulting carrier reference material.
2. **Internal staff KB Q&A** — research-time-reduction for carrier staff (underwriters, claims handlers, customer service); no boundary discipline because audience is internal.

**Tool skills:** KB retrieval (tool-005) · Source citation · Boundary detection · Human handoff escalation · Dynamic-info lookup (where carrier has product/program data backends)

**Channels:** Web chat · email · voice

**Systems:** Indemn Copilot KB · carrier product/forms/filing data backends

**Customers active:** None at Carrier tier specifically (MGA-tier deployments at DP, JM, UG cover the shape — see Row 37).

**Status:** not deployed at Carrier tier.

#### Row 21 — Onboarding Associate (Carrier, $500/mo, "Agent Onboarding & Licensing Automation")

> Cam description: "Automated agent intake with licenses verification and contracting form management, reducing the time-to-sell from weeks to days."

**Proposed pathway skill:**
- **Agent onboarding + licensing intake** — collect agent/producer info → verify licenses (state DOI lookup or equivalent) → manage contracting form completion → push to onboarding system.

**Tool skills:** Producer intake form capture (tool-025 reusable) · License verification (state DOI API or equivalent — not yet built as discrete tool) · Contracting form management · Onboarding system write

**Channels:** Web chat · email · voice

**Systems:** State DOI license-verification API · Onboarding/contracting backend · CRM

**Customers active:** UG (path-024 WIP — MGA-tier instance).

**Status:** WIP at MGA tier; not deployed at Carrier tier specifically.

#### Row 22 — Ticket Associate (Carrier, $0.50/ticket, "Tier 1 Ticket Deflection")

> Cam description: "Resolves routine inquiries from staff without requiring IT or senior underwriting intervention."

Carrier-flavored: internal carrier staff inquiries (filing procedures, system access, internal processes, UW guidelines).

**Proposed pathway skill:**
- **Internal staff KB Q&A for routine inquiries** — retrieve answer from internal KB (operational/process/system-access/UW-guideline) → respond → escalate to right human (IT/senior UW/manager) when out of scope.

**Tool skills:** KB retrieval (tool-005) · Routine vs complex classification (deflection threshold) · Human handoff escalation (route to right internal team)

**Channels:** Web chat · email · (Slack/Teams plausible for internal-tool integration)

**Systems:** Internal KB (Indemn Copilot KB with carrier-supplied content) · ticket system

**Customers active:** None at Carrier tier specifically.

**Status:** not deployed at Carrier tier.

#### Row 23 — Growth Associate (Carrier, 2% GWP, "Long-Tail Direct Sales Engagement")

> Cam description: "Automated direct-to-consumer qualify, quote, and bind capability." Working Copy (MGA mirror): "Same as quote and bind"

**Per your annotation, functionally same as Quote & Bind Associate (Row 43).**

**Proposed pathway skill:**
- **Direct-to-consumer qualify-quote-bind** — engage prospect → qualify → generate quote → present quote → bind (with payment processing) → issue policy. End-to-end consumer purchase flow.

**Tool skills:** Lead generation capture · Quote generation (per-product) · Quote presentation · Stripe payment processing (tool-034) · Policy issue (tool-019) · Coverage options preview (tool-032)

**Channels:** Web chat · voice · text · point-of-sale widget

**Systems:** Carrier quote systems · Payment processor (Stripe at JM EventGuard) · Policy issuance system · CRM

**Customers active:** JM EventGuard (path-027 — MGA-tier instance).

**Status:** developed at MGA tier (JM); not deployed at Carrier tier specifically. **`[Open Q — Growth ↔ Quote & Bind merge?]`**

#### Row 24 — Placement Associate (Carrier, $50/seat, "Agent Portal Appetite Guidance")

> Cam description: "Embedded portal associate guides independent agents through complex appetite questions in real-time." Working Copy (MGA mirror): "doing more than appetite guidance, additional integrations available — for example policy status for GIC with policy administration system"

**Proposed pathway skills:**
1. **Broker portal Q&A** — answer agent questions about appetite/eligibility/products from KB (path-001 GIC).
2. **Policy lookup with error handling** — agent enters policy number → look up status from carrier policy admin system → return status with error-handling for known failure patterns (path-002 GIC).

**Tool skills:** KB retrieval · Policy status retrieval (atomic API call — tool-004 GIC Granada) · Error-handling decision logic · Human handoff escalation

**Channels:** Web chat (embedded in broker portal)

**Systems:** Carrier policy admin system (Granada at GIC) · KB

**Customers active:** GIC (MGA-tier MGA_MGU instance).

**Status:** developed at MGA tier (GIC); not deployed at Carrier tier specifically.

#### Row 25 — Quote Associate (Carrier, $1,000/mo, "Quote conversion")

> Cam description: "Real time point of sale quoting and customer Q&A."

**Proposed pathway skill:**
- **Real-time POS quote + customer Q&A** — engage customer → collect minimal data → generate quote → answer customer questions about quote → optional handoff to bind.

**Tool skills:** Customer profile collection · Quote generation · Coverage options preview · Quote comparison · KB retrieval (for Q&A) · Lead generation capture · Human handoff escalation

**Channels:** Web chat · voice · point-of-sale widget

**Systems:** Carrier quote system · KB

**Customers active:** Branch (path-037 — MGA-tier), JM (path-025 — MGA-tier).

**Status:** developed at MGA tier; not deployed at Carrier tier specifically.

#### Row 26 — Risk Associate (Carrier, $250/LOB, "Cross-Sell Opportunity Identification")

> Cam description: "Automated coverage gap identification and tailored proposal generation for presentation."

**Proposed pathway skills:**
1. **Cross-sell opportunity identification** — analyze customer book → identify monoline customers + coverage gaps relative to typical bundle (e.g., auto-only customer who'd benefit from Umbrella; business customer without Cyber).
2. **Cross-sell outreach + tailored proposal generation** — for identified opportunities, generate tailored proposal → outbound personalized message with proposal → capture interest → route warm responses to producer/agent.

**Tool skills:** Customer book read (carrier policy admin) · Coverage gap analysis · Tailored proposal generation · Outbound message dispatch · Personalization templating · Lead capture / response handling · CRM read/write

**Channels:** Text · email · phone

**Systems:** Carrier policy admin · CRM

**Customers active:** None.

**Status:** not developed yet.

#### Row 27 — Strategy Studio (Carrier, $1,000/mo, "No-Code Program Builder")

> Cam description: "Facilitates central updating of eligibility rules, commission structures, or new products in days rather than months."

**Conversational associate** — talks with carrier ops to build/update programs. Distinct flavor from Agency/Broker Strategy Studio (Row 13) — that's brand-voice; this is no-code program building.

**Proposed pathway skill:**
- **Conversational no-code program building** — agent works with carrier/program ops to update eligibility rules, commission structures, launch new products → captures intent through conversation → drafts rule/structure config → validates → deploys.

**Tool skills:** Rule capture from conversation · Commission-structure editor helpers · Product-launch workflow · Validation/testing harness · Configuration deploy · Versioning/rollback

**Channels:** Web chat (builder UI)

**Systems:** Rule engine · Commission structure storage · Product registry · Configuration deploy pipeline

**Customers active:** None.

**Status:** not developed yet.

---

### §9.3 MGA rows

#### Row 28 — Care Associate (MGA, $1,000/mo, "Proactive Lapse Prevention")

> Cam description: "Automated payment status monitoring with proactive policyholder contact to resolve payment issues."

**Proposed pathway skills:**
1. **Payment status monitoring** — periodic scan of policy payment status → identify lapse risks (late payment, declined card, upcoming due date)
2. **Lapse-prevention outreach** — outbound to at-risk policyholders → resolve payment (collect new method, retry charge, set up payment plan, route to billing team)

**Tool skills:** Payment status retrieval (MGA billing system read) · Lapse-risk classification · Outbound message dispatch · Stripe payment processing (tool-034) · Payment-plan setup · Customer profile retrieval

**Channels:** Voice · text · email

**Systems:** MGA billing system · Stripe (or MGA-equivalent payment processor) · CRM

**Customers active:** Branch (Sophie, path-036).

**Status:** developed at Branch.

#### Row 29 — Orphan Associate (MGA, $1,000/mo, "Direct & Orphan Book Management")

> Cam description: "Automated renewal processing for 'house accounts' or direct-written business, ensuring customers receive service continuity." Working Copy: "30-90 days, dependent on # of communication channels and potential divergence between renewals"

**Proposed pathway skill:**
- **Orphan/house-account renewal stewardship** — for customers without an assigned producer, run renewal lifecycle: identify upcoming renewals → reach out → collect updates → process renewal → ensure service continuity. Similar to Renewal Associate but unowned-book-flavored (no producer to draft for; system handles end-to-end).

**Tool skills:** AMS read (orphan-book identification, renewal queue) · Outbound message dispatch · Customer profile retrieval · Carrier renewal submission · Disposition tracking

**Channels:** Email · text · phone

**Systems:** AMS · Carrier renewal systems · CRM

**Customers active:** None.

**Status:** not developed yet.

#### Row 30 — Renewal Associate (MGA, $1,000/mo, "Proactive Renewal Review")

> Cam description: "Automatically reviews personal and commercial lines renewals, flags premium increases, and drafts 'remarket' or 'review' email for the agent."

**Proposed pathway skills:**
1. **Renewal queue review + premium-increase flagging** — read AMS renewal pipeline → flag material increases or appetite changes
2. **Remarket vs review classification** — for flagged renewals, classify whether to remarket (shop alternates) or keep with current carrier
3. **Producer-facing renewal email drafting** — generates the "remarket" or "review" deliverable for the agent
4. **Multi-channel customer renewal outreach + data collection** — INSURICA MARA pattern (escalation handling folded in)

**Tool skills:** AMS read (renewal queue, premium history) · CRM read/write · Outbound message dispatch · Email drafting · Disposition state-machine tracking

**Channels:** Email · text · phone · web chat

**Systems:** AMS · CRM (Salesforce-equivalent)

**Customers active:** None at MGA tier specifically (INSURICA path-012 is Broker-tier deployment).

**Status:** not deployed at MGA tier.

#### Row 31 — Answer Associate (MGA, $1,000/mo, "Product Expert")

> Cam description: "Central provision of 'source of truth' data for response to dynamic information requests." Working Copy: "Similar to KB associate"

**Proposed pathway skill:**
- **Product-expert dynamic-info Q&A** — KB-backed answers about specific MGA products/programs/eligibility/forms; "source of truth" responses to broker/agent inquiries about product details with dynamic-data backend (not just static KB).

**Tool skills:** KB retrieval (tool-005) · Source citation · Dynamic-info lookup (e.g., DP product lookup tool-046, DP capabilities lookup tool-047 — Airtable-via-n8n at DP) · Human handoff escalation when out of scope

**Channels:** Web chat · email · voice

**Systems:** Indemn Copilot KB · MGA product-data backends (Airtable-via-n8n at DP, etc.)

**Customers active:** DP (path-039 — general DP product/program/capabilities Q&A).

**Status:** developed at DP.

#### Row 32 — Authority Associate (MGA, $1,000/mo, "Underwriting Guardrails & Compliance")

> Cam description: "Applies underwriting rules to ensure binding compliance, increasing placement rate and protecting carrier relationships."

**Functional emphasis: pre-bind compliance** — at bind time (after quote is accepted, before policy issues), validate the to-be-bound submission against carrier UW rules + binding authority limits. Distinct from Intake (data flow) and Submission (pre-submission eligibility) by being at the bind-time gate.

**Proposed pathway skill:**
- **Pre-bind UW guardrail validation** — at bind moment, take in-flight quote → validate against carrier UW rules + binding authority limits → flag violations or out-of-appetite conditions → block bind or route to human UW for override.

**Tool skills:** UW rule retrieval (per carrier, bind-time scope) · Submission data validation against bind-time rules · Binding authority limit check · Violation classification · Human handoff escalation (UW review)

**Channels:** API/internal (embedded at the bind-step of a Quote & Bind workflow)

**Systems:** Carrier UW rule engine · Binding authority configs · Quote/policy issuance pipeline

**Customers active:** None standalone. UG's workflow stops short of bind-time authority validation (their work is comparative-quote-focused; bind happens downstream); the closest tool reusable here is UG's UW parameter violation mapping (tool-023), but applied at bind time rather than pre-submission.

**Status:** not developed yet as a standalone Authority Associate.

#### Row 33 — Inbox Associate (MGA, $50/seat, "Smart Inbox")

> Cam description: "Pre-drafted emails regarding claims status or underwriting questions, allowing adjusters/underwriters to significantly increasing correspondence velocity."

MGA-flavored: broker correspondence, claims status to brokers, UW questions to brokers.

**Proposed pathway skills:**
1. **Inbox triage + classification** — read incoming email → classify type (broker question / claims status / UW request / informational) → identify which require pre-drafted response
2. **Pre-drafted email response generation** — generate draft response (broker-facing claims update, simple UW answer) → surface to MGA staff for review + send

**Tool skills:** Email read (inbox poll) · Email classification · KB retrieval · Customer/policy context retrieval (MGA records / carrier feeds) · Email draft generation · Draft surfacing for human review

**Channels:** Email (inbound + outbound)

**Systems:** Email server · MGA records system · KB

**Customers active:** None at MGA tier specifically.

**Status:** not developed yet.

#### Row 34 — Intake Associate (MGA, $1/ticket, "Automated Submission Triage & Data Extraction")

> Cam description: "Automated submission intake of emails and documents (SOVs, loss runs), extraction of key data points, population of underwriting systems, and triage of submissions based on complexity and appetite." Working Copy: "Dependent on # of documents to be trained and amount of data within each document"

**Functional emphasis: data flow at submission arrival** — ingestion, extraction, UW-system population. Distinct from Submission (eligibility filter pre-carrier-submission) and Authority (pre-bind compliance) by being at the submission-arrival point.

**Proposed pathway skills:**
1. **Submission ingestion + data extraction** — receive submission (email, ACORD forms, SOVs, loss runs) → extract structured data via OCR + LLM → normalize to UW-system schema
2. **UW-system population** — push extracted data into MGA UW system; trigger downstream workflow (Submission Associate eligibility check, Market Associate carrier routing)

**Tool skills:** Email/document ingestion (Composio at UG — tool-021) · OCR + structured data extraction (tool-003) · Class code matching (tool-022 at UG) · Submission complexity classification · UW-system write · Voice intake (when voice-channel-fronted, e.g., GIC Fred WC)

**Channels:** Email (primary) · web form · voice (when voice-fronted)

**Systems:** Email server · MGA UW systems (intake-manager at UG) · OCR/extraction pipeline · Composio (UG)

**Customers active:** UG (path-019/020/021 — Intake-emphasis at the front of UG's Intake+Market Combined workflow), GIC (Fred Workers Comp voice prototype — path-005/006/007 — Intake-emphasis voice variant).

**Status:** developed at UG + GIC prototype.

#### Row 35 — Intake Associate for Claims (MGA, $1/ticket, "First Notice of Loss")

> Cam description: "Automated intake of First Notice of Loss."

MGA-flavored: FNOL routes through MGA to its carrier partners.

**Proposed pathway skill:**
- **End-to-end FNOL intake** — receive notice of loss → identify policyholder + policy → collect structured loss details (date/time, location, parties involved, narrative, photo/document evidence) → route through MGA to carrier claims system → send acknowledgment.

**Tool skills:** Loss-detail intake capture · Photo/document upload capture · Policyholder/policy lookup (MGA records) · Claims system submission (to carrier partner) · Acknowledgment dispatch · Triage/severity classification

**Channels:** Voice · web chat · text · email

**Systems:** MGA records system · Carrier claims systems (multi-carrier routing) · Email · MMS

**Customers active:** None.

**Status:** not developed yet.

#### Row 36 — Inquiry Associate (MGA, $1,000/mo, "Broker Support Deflection")

> Cam description: "Automated, instant response to routine broker questions via chat, email, or voice." Working Copy: "Multi modal additional complexity but not major"

**Proposed pathway skill:**
- **Multi-modal broker/agent inquiry deflection + routing** — agent reaches out (chat/email/voice) → identify intent → answer routine questions from KB OR route to right human queue (Sales/Claims/Service/Agency Support). Generalizes path-033 (Branch Petra).

**Tool skills:** KB retrieval · Intent classification (multi-pass — tool-039) · Routing-to-human-queue · Human handoff escalation

**Channels:** Web chat · email · voice (multi-modal)

**Systems:** KB · ticketing/queue infrastructure · Indemn Copilot

**Customers active:** Branch (path-033).

**Status:** developed at Branch.

#### Row 37 — Knowledge Associate (MGA, $50/seat, "Smart Process Library")

> Cam description: "Instantly retrieves answers from thousands of pages of policy forms, claims manuals, and filing documents, reducing research time from hours to seconds."

MGA-flavored: program/product/carrier guideline content; broker-facing or end-customer-facing per program.

**Proposed pathway skills:**
1. **Bounded customer-facing KB Q&A** — retrieve answer from KB → respond with strict boundaries (no quote / no eligibility / no policy interpretation); route to human when out-of-scope. Includes specialization variants (cyber, community associations, submission portal at DP; ring/jewelry at JM; multi-carrier UW at UG).
2. **Internal staff KB Q&A** — research-time-reduction for MGA staff/underwriters; no boundary discipline.

**Tool skills:** KB retrieval (tool-005) · Source citation · Boundary detection · Human handoff escalation · Dynamic-info lookup (DP product lookup tool-046, capabilities lookup tool-047) · Carrier app URL lookup (tool-027 at UG)

**Channels:** Web chat · email · voice (Melody at DP)

**Systems:** Indemn Copilot KB · MGA product-data backends (Airtable-via-n8n at DP) · n8n.indemn.ai (carrier app URL webhooks at UG)

**Customers active:** DP (path-039 general · path-040 Cyber consolidated · path-042 Community Associations · path-043 Submission portal), JM (path-028 Zola partner-embedded · path-030 jewelry/ring), UG (path-016 consolidated UW Q&A across multi-carrier + per-carrier + Northland trucking + Mobile home scopes).

**Status:** developed at MGA tier extensively (3 customers, multiple specialization variants each).

#### Row 38 — Onboarding Associate (MGA, $1,000/mo, "Agent Onboarding & Licensing Automation")

> Cam description: "Automated agent intake with licenses verification and contracting form management, reducing the time-to-sell from weeks to days."

**Proposed pathway skill:**
- **Agent/producer onboarding + licensing intake** — collect agent/producer info (background, experience, agency affiliation) → verify licenses (state DOI lookup or equivalent) → manage contracting form completion → push to onboarding system.

**Tool skills:** Producer intake form capture (tool-025 reusable from UG) · License verification (state DOI API or equivalent — not yet built as discrete tool skill) · Contracting form management · Onboarding system write · CRM read/write

**Channels:** Web chat · email · voice

**Systems:** State DOI license-verification API · Onboarding/contracting backend · CRM

**Customers active:** UG (path-024, WIP — Producer/agency onboarding intake).

**Status:** WIP at UG.

#### Row 39 — Ticket Associate (MGA, $1/ticket, "Tier 1 Ticket Deflection")

> Cam description: "Resolves routine inquiries from staff without requiring IT or senior underwriting intervention."

MGA-flavored: internal MGA staff inquiries (program guidelines, system access, internal processes).

**Proposed pathway skill:**
- **Internal staff KB Q&A for routine inquiries** — retrieve answer from internal KB (operational/process/program-guideline) → respond → escalate to right human (IT/senior UW/manager) when out of scope.

**Tool skills:** KB retrieval (tool-005) · Routine vs complex classification · Human handoff escalation

**Channels:** Web chat · email

**Systems:** Internal KB (Indemn Copilot KB with MGA-supplied content) · ticket system

**Customers active:** None at MGA tier specifically.

**Status:** not deployed.

#### Row 40 — Growth Associate (MGA, 2% GWP, "Long-Tail Direct Sales Engagement")

> Cam description: "Automated direct-to-consumer qualify, quote, and bind capability." Working Copy: "Same as quote and bind"

**Proposed pathway skill:**
- **Direct-to-consumer qualify-quote-bind** — engage prospect → qualify → generate quote → present quote → bind (with payment processing) → issue policy. End-to-end consumer purchase flow.

**Tool skills:** Lead generation capture · Quote generation (per-product) · Quote presentation · Stripe payment processing (tool-034) · Policy issue (tool-019) · Coverage options preview (tool-032) · SMS quote delivery (tool-031) · Voice call transfer (tool-033)

**Channels:** Web chat · voice · text · point-of-sale widget

**Systems:** MGA quote systems · Payment processor (Stripe at JM EventGuard) · Policy issuance system · CRM

**Customers active:** JM (path-025 ring engagement + path-027 EventGuard).

**Status:** developed at JM.

#### Row 41 — Placement Associate (MGA, $50/seat, "Agent Portal Appetite Guidance")

> Cam description: "Embedded portal associate guides independent agents through complex appetite questions in real-time." Working Copy: "doing more than appetite guidance, additional integrations available — for example policy status for GIC with policy administration system"

**Proposed pathway skills:**
1. **Broker portal Q&A** — answer agent questions about appetite/eligibility/products from KB (path-001 GIC).
2. **Policy lookup with error handling** — agent enters policy number → look up status from MGA/carrier policy admin system → return status with error-handling for known failure patterns (path-002 GIC).

**Tool skills:** KB retrieval (tool-005) · Policy status retrieval (atomic API call — tool-004 GIC Granada) · Error-handling decision logic · Human handoff escalation

**Channels:** Web chat (embedded in broker portal)

**Systems:** MGA/Carrier policy admin system (Granada at GIC) · KB

**Customers active:** GIC (path-001 + path-002).

**Status:** developed at GIC.

#### Row 42 — Market Associate (MGA, $1,000/mo, "Market Access Optimization")

> Cam description: "Automated submission analysis and best-fit carrier recommendation." Working Copy: "Assuming detailed discover on customer market and program comparisons"

**Proposed pathway skill:**
- **Submission analysis + best-fit carrier recommendation** — for an inbound submission, analyze data → match against carrier appetite + program criteria → recommend best-fit carrier(s) for routing/quote generation.

**Tool skills:** Submission data analysis · Carrier appetite rule retrieval · Program-comparison logic · Quote comparison across carriers (tool-024) · Carrier-recommendation output

**Channels:** Email (typically email-driven submission flow) · API/internal

**Systems:** Per-carrier appetite rules · Per-carrier quote APIs · CRM

**Customers active:** UG (folded with Intake — not standalone, path-020 GL 3-carrier comparative includes Market work).

**Status:** partially developed (combined with Intake at UG); standalone Market Associate not deployed.

#### Row 43 — Quote & Bind Associate (MGA, 2% GWP, "24/7 Quoting & Binding Execution")

> Cam description: "Automated end-to-end quote-to-bind workflows for brokers or direct consumers." Working Copy: "Depending on complexity of the program"

**Proposed pathway skill:**
- **End-to-end quote-to-bind workflow** — engage prospect (broker or direct consumer) → qualify → generate quote → present quote → bind (with payment processing) → issue policy. Same shape as Growth Associate (Row 40); per your annotation "Same as quote and bind."

**Tool skills:** Lead generation capture · Quote generation (per-product) · Quote presentation · Stripe payment processing (tool-034) · Policy issue (tool-019) · Coverage options preview (tool-032) · SMS quote delivery (tool-031) · Voice call transfer (tool-033)

**Channels:** Web chat · voice · text · point-of-sale widget

**Systems:** MGA/Carrier quote systems · Payment processor (Stripe at JM EventGuard) · Policy issuance system · CRM

**Customers active:** JM (path-025 ring engagement + path-027 EventGuard).

**Status:** developed at JM.

#### Row 44 — Quote Associate (MGA, $1/ticket, "Quote conversion")

> Cam description: "Real time point of sale quoting and customer Q&A."

**Proposed pathway skill:**
- **Real-time POS quote + customer Q&A** — engage customer → collect minimal data → generate quote → answer customer questions about quote → optional handoff to bind.

**Tool skills:** Customer profile collection (tool-045) · Quote generation (per-product) · Coverage options preview (tool-032) · Quote comparison (tool-024) · KB retrieval (for Q&A) · Lead generation capture · Human handoff escalation · Branch GraphQL convertQuote (tool-044 at Branch) · SMS quote delivery (tool-031 at JM)

**Channels:** Web chat · voice · point-of-sale widget

**Systems:** MGA/Carrier quote system · KB · Branch GraphQL API (Branch instance)

**Customers active:** Branch (path-037 — Carson voice + Caroline voice + branch quote assist webchat), JM (path-025 + path-027 EventGuard).

**Status:** developed at Branch + JM.

#### Row 45 — Risk Associate (MGA, $1,000/mo, "Cross-Sell Opportunity Identification")

> Cam description: "Automated coverage gap identification and tailored proposal generation for presentation."

**Proposed pathway skills:**
1. **Cross-sell opportunity identification** — analyze customer book → identify monoline customers + coverage gaps relative to typical bundle.
2. **Cross-sell outreach + tailored proposal generation** — for identified opportunities, generate tailored proposal → outbound personalized message → capture interest → route warm responses to producer/agent.

**Tool skills:** Customer book read (MGA records / partner carrier feeds) · Coverage gap analysis · Tailored proposal generation · Outbound message dispatch · Personalization templating · Lead capture / response handling · CRM read/write

**Channels:** Text · email · phone

**Systems:** MGA records · partner carrier feeds · CRM

**Customers active:** None.

**Status:** not developed yet.

#### Row 46 — Submission Associate (MGA, $5/ticket, "Eligibility Triage & Partner Routing")

> Cam description: "Automated qualification of submissions against program guidelines to filter 'out-of-appetite' risks and identify gaps prior to carrier submission."

**Functional emphasis: eligibility filter pre-carrier-submission** — after Intake has extracted data but before submitting to a carrier, check against program guidelines + appetite, identify gaps, route to right carrier partner. Distinct from Intake (data flow at arrival) and Authority (pre-bind compliance) by being at the pre-carrier-submission gate.

**Proposed pathway skill:**
- **Pre-submission appetite triage + partner routing** — extracted submission → check against program guidelines + carrier appetite rules → identify out-of-appetite risks + missing-info gaps → route to right carrier partner (or block + request more info from broker).

**Tool skills:** Program-guideline rule engine · Carrier appetite rule retrieval · Out-of-appetite classification · Gap identification (missing fields/docs) · Partner routing logic · Customer/broker notification (request more info) · UW parameter violation mapping (tool-023 at UG)

**Channels:** Email (broker notification) · API/internal (inside submission workflow)

**Systems:** Program guideline configs · Carrier appetite rules · Submission tracking system

**Customers active:** UG (Submission-emphasis at the eligibility-filter step of UG's Intake+Market Combined workflow — UW parameter violation mapping tool-023 + class-code matching tool-022 + appetite verification are the Submission-emphasis tools applied here).

**Status:** developed at UG (as the eligibility-filter step inside Intake+Market).

#### Row 47 — Strategy Studio (MGA, $5,000/mo, "No-Code Program Builder")

> Cam description: "Facilitates central updating of eligibility rules, commission structures, or new products in days rather than months."

**Conversational associate** — talks with MGA program ops to build/update programs.

**Proposed pathway skill:**
- **Conversational no-code program building** — agent works with MGA program ops to update eligibility rules, commission structures, launch new MGA programs → captures intent through conversation → drafts rule/structure config → validates → deploys.

**Tool skills:** Rule capture from conversation · Commission-structure editor helpers · Program-launch workflow · Validation/testing harness · Configuration deploy · Versioning/rollback

**Channels:** Web chat (builder UI)

**Systems:** Rule engine · Commission structure storage · Program registry · Configuration deploy pipeline

**Customers active:** None.

**Status:** not developed yet.

---

### §9.4 In-development rows (Z tier — Cam's "not ready for deployment")

#### Row 48 — Subrogation Recovery Identification

> Cam description: "AI agents scan claim files (notes, police reports) for indicators of third-party liability, flagging cases with high recovery potential and drafting demand letters, directly reducing the net loss ratio."

**Proposed pathway skill:**
- **Subrogation candidate identification + demand letter drafting** — scan claim files (notes, police reports, witness statements) → flag third-party-liability indicators → draft demand letter → surface to claims handler for review/send.

**Tool skills:** Claim-file ingestion · Document analysis · Third-party-liability indicator detection · Demand-letter drafting · Human handoff (to claims handler)

**Channels:** Internal/API (claims-handler-facing); email outbound for demand letters

**Systems:** Claims management system · document-extraction infrastructure

**Status:** not developed yet.

#### Row 49 — Policy Checking & Review

> Cam description: "Automated review of policy documents against quotes and binders to identify discrepancies or errors before they reach the client, significantly reducing manual review time and potential E&O exposure."

**Proposed pathway skill:**
- **Policy-doc review against quote/binder** — receive policy doc + quote/binder → compare for discrepancies (coverage, limits, deductibles, names, dates) → flag errors → surface to producer/CSR for resolution.

**Tool skills:** Policy doc ingestion · Quote/binder ingestion · Field-level comparison · Discrepancy classification · Producer notification

**Channels:** Email · internal/API

**Systems:** AMS · document-comparison engine

**Status:** not developed yet.

#### Row 50 — Intake Qualification (Free)

> Cam description: "Qualifying customers at initial contact"

**Proposed pathway skill:**
- **Initial-contact qualification** — at first touch, determine fit (existing vs new, type of insurance need, personal/commercial routing) → route to right downstream associate (Lead, Service, etc.).

**Note:** Overlaps materially with Lead Associate's qualification step (Row 11). Functionally Intake Qualification IS the front-end of Lead Associate.

**Status:** not developed yet. **`[Open Q below — overlap with Lead Associate?]`**

#### Row 51 — Win-Back Campaigns

> Cam description: "Automated re-engagement of 'dead leads' or former clients existing in the AMS database with new offers or market updates, revitalizing lost opportunities without requiring active producer effort."

**Proposed pathway skill:**
- **Dead-lead re-engagement** — AMS scan for inactive/lapsed customers + dead-lead pipeline → personalized re-engagement message with new offer or market update → capture response → route warm responses to producer.

**Tool skills:** AMS read (inactive/lapsed customer identification) · Personalization templating · Outbound message dispatch · Response capture · Lead routing

**Channels:** Email · text · phone

**Systems:** AMS · CRM

**Status:** not developed yet. **Functional overlap with Care Associate (Row 1) outbound personalized outreach + Cross-Sell Associate (Row 10).**

#### Row 52 — Monoline Agent (% of GWP)

> Cam description: "AI agents scan the client portfolio to identify monoline clients (e.g., those with only Auto coverage) and generate scripted cross-sell pitches for complementary products (e.g., Home, Umbrella, Cyber), directly driving revenue expansion (Indemn provides product and license)."

**Proposed pathway skills:**
1. **Monoline client identification** — analyze customer portfolio → identify monoline clients (those with only one coverage type, e.g., auto-only).
2. **Scripted cross-sell pitch generation + outreach** — for identified monoline clients, generate scripted cross-sell pitch for complementary products (Home, Umbrella, Cyber) → outbound personalized message → capture interest → route warm responses to producer/agent.

**Tool skills:** Customer portfolio read (AMS) · Monoline classification (single-coverage detection) · Coverage gap analysis · Scripted pitch generation · Outbound message dispatch · Personalization templating · Lead capture / response handling · CRM read/write · Indemn-product insertion logic (revenue-model-specific — Indemn provides product/license, not just facilitating customer's book)

**Channels:** Text · email · phone

**Systems:** AMS · CRM · Indemn-provided product registry

**Customers active:** None.

**Status:** not developed yet. **Differentiator from Cross-Sell (Row 10) / Risk (Row 26/45) is the revenue model — Indemn provides the product + license rather than facilitating the customer's existing book.**

#### Row 53 — Compliance Audit Trails

> Cam description: "A comprehensive logging system that records every decision, recommendation, and interaction made by the AI agents, creating an immutable audit trail for internal compliance reviews and regulatory market conduct exams."

**Not a runtime associate — observability/infrastructure feature.** Already partially provided by the kernel's `changes` collection (immutable, hash-chain audit trail per `indemn-os/CLAUDE.md`). Productized customer-facing audit-review surface not yet built.

**Status:** infrastructure exists; productized surface not deployed. **`[Open Q below per Rows 12, 13, 27, 47, 53, 54, 55 — infrastructure-vs-runtime-associate framing.]`**

#### Row 54 — Secure Data Integration

> Cam description: "The 'Strategy Studio' ensures all AI agent activities are securely integrated with core legacy systems (PAS/Claims), maintaining data privacy and ensuring that the 'single source of truth' remains accurate and protected."

**Not a runtime associate — security/integration infrastructure.** Implementation lives in the OS kernel (auth, integration adapters, secrets management).

**Status:** infrastructure exists; not a runtime associate row.

#### Row 55 — E&O Risk Mitigation

> Cam description: "AI agents create a consistent, documented audit trail of all advice given and coverages offered (and rejected), providing a robust defense against Errors & Omissions claims."

**Variant of Compliance Audit Trails (Row 53)** — same audit-trail infrastructure, framed for E&O defense rather than regulatory compliance. Same kernel `changes` collection foundation.

**Status:** infrastructure exists; productized surface not deployed.

---

### §9.5 Cross-tier observations + resolved decisions

**Resolved 2026-05-01 in this session:**

- **Cam catalog rows are official; we don't merge them.** When skills are shared across rows (e.g., Cross-Sell ↔ Risk ↔ Monoline; Growth ↔ Quote & Bind), each row writes its skills out redundantly per Craig 2026-05-01.
- **Dashboard Associate (Row 12) and Strategy Studio (Rows 13/27/47) are conversational associates** — they talk with staff/builders about observability/program-building. Not infrastructure.
- **Compliance Audit Trails (Row 53), Secure Data Integration (Row 54), E&O Risk Mitigation (Row 55) are infrastructure**, not runtime associates — flagged as such in their entries.
- **Zola partner-embedded (JM path-028) is a Systems-catalog item** (embedded chat in a partner surface) per Craig 2026-05-01 — to be added to §6 Systems catalog rather than a separate Cam row.
- **Lead Associate at MGA tier** — gap stays in §2.05, propagates to Phase D sheet update spec.

**Remaining open questions for Craig:**

**1. Intake Qualification (Z Row 50) overlap with Lead Associate qualification step.** Per redundancy principle, both rows write skills out. But: is Intake Qualification (Z) a *standalone* associate that does only first-contact qualification (then hands off), or is it functionally the front-end of Lead Associate? Affects whether Z Row 50 stays in the Cam catalog when productized.

**2. Authority (MGA Row 32) + Submission (MGA Row 46) + Intake (MGA Row 34)** — three rows that touch UW guardrails / appetite filtering / submission validation. UG's Intake+Market workflow bundles all three skill sets in one workflow. Per redundancy principle, each row writes skills out — but does each row map back to a *different* part of UG's workflow, or are we just listing the same skills under all three Cam rows?

**3. Win-Back Campaigns (Z Row 51) shares shape with Care + Cross-Sell** — outbound personalized outreach with different trigger. Per redundancy, all rows write skills. **Implicit confirmation: same redundancy treatment, different trigger configs noted per row.** No question here unless you want to discuss.

---

## 10. Phase C — LOE pass per catalog entry `[next — Pricing Framework Session 3]`

For each entry in §§5-7 catalogs, assign hours estimate. **Hours only, no money per Craig 2026-05-01.** Collaborative — Craig authors, I capture structure.

### LOE rules (already in §2)

- **Things already developed** for a customer → **actual hours** (Craig recall + git history where useful)
- **Things not built for any customer** → **first-customer LOE estimate** (Craig authors, I capture structure)

### §10.1 Channels LOE `[8 entries — start here]`

| Channel | Status | First-customer LOE (h) | Per-customer-after (h) | Notes |
|---|---|---|---|---|
| Web chat (Indemn Copilot) | built | _ | _ | _ |
| Email — Outlook (Microsoft Graph) | built | _ | _ | _ |
| Email — outbound | built | _ | _ | _ |
| Voice — inbound | built | _ | _ | _ |
| Voice — outbound | not built | _ | _ | _ |
| SMS | built | _ | _ | _ |
| Schedule | built | _ | _ | _ |
| Microsoft Teams (outbound notification) | built | _ | _ | _ |

### §10.2 Systems LOE `[28 entries]`

| System | Integration type | Status | First-customer LOE (h) | Per-customer-after (h) | Notes |
|---|---|---|---|---|---|

`[Populate per row from §6 systems catalog. Each row: system name + integration type (API / web operator / other) + status + first-customer LOE + per-customer-after + notes. Order matches §6.]`

### §10.3 Tool skills LOE `[57 entries]`

| ID | Skill | Status | First-customer LOE (h) | Per-customer-after (h) | Notes |
|---|---|---|---|---|---|

`[Populate per row from §7 tool skills table. Order tool-001 through tool-057.]`

### §10.4 Pathway skills LOE `[46 entries — excluding 9 merged placeholders]`

| ID | Skill | Status | First-customer LOE (h) | Per-customer-after (h) | Notes |
|---|---|---|---|---|---|

`[Populate per row from §7 pathway skills table. Skip merged placeholders (path-026, 029, 038, 041, 013, 045, 017, 018, 022) — they redirect to their targets.]`

### Phase C done-test

After all 4 sub-tables populated, the formula `cost = (channels) + (skills) + (systems)` is computable per customer for any of Cam's 47 rows — sum hours per the catalog entries that customer's deal touches.

### What Phase C produces

For each catalog entry:

| Field | What |
|---|---|
| **First-customer LOE (hours)** | Hours to build for the first customer on this skill/channel/system |
| **Per-customer-after-first LOE (hours)** | Hours to apply to a subsequent customer (typically << first-customer; the reusability story) |
| **Notes** | Context that affects the estimate (e.g., "depends on whether AMS has API or needs web-operator"; "every new carrier = new skill") |

### Process

Collaborative — go through the catalogs together (channels first, then systems, then tool skills, then pathway skills). For each entry, Craig provides the estimate + reasoning; I capture structured. Anchors for Craig's authoring already exist in **Appendix A** (Working Copy annotations: Renewal Associate 30 + 30-50 hrs, Knowledge Associate 8-12 hrs, etc.).

### Computability check

After Phase C, the formula `cost = (channel integrations) + (skill development) + (system integrations)` should be **computable per customer** for any of Cam's 47 rows — given a customer's current channel/system/skill state, we can sum hours to get total implementation LOE.

`[No money / hours-to-dollars mapping per Craig 2026-05-01. Cost mapping happens later if/when Craig wants it.]`

---

## 11. Phase D — Output presentation `[after Phase C]`

Two output surfaces — Cam's sheet + an HTML UI.

### 11.1 Cam's sheet update spec

Exact migration plan from this doc into Cam's spreadsheet. Reviewed with Craig before any cells in Cam's main tab are touched.

Per §4 end-state, the spec produces the 6 tabs: Associates (augmented Cam main) · Skills (NEW) · Channel integrations (NEW) · System integrations (NEW) · Customer/Deal map (NEW) · Craig|Kyle Working Copy (existing).

### 11.2 HTML UI visualization (Craig 2026-05-01)

Per Craig: an HTML UI is more easily visualizable than the Excel sheet. Build a small surface that renders the same data (associates × skills × channels × systems × customers × LOE) interactively. Possible shapes:
- Per-associate detail page (clickable from a list view) — like the customer-system trace-showcase HTML language Cam + Kyle have already validated
- Cross-cutting filter views (by customer, by channel, by system, by LOE bucket)
- Co-deployment matrix (which associates run together) — directly answers Cam's "Analyze Associate Usage" action item

Craig's framing: "if we can really go ham on it Excel spreadsheet and make it beautiful that's a different story but we'll get there when we get there." Excel polish is optional / later. HTML UI is the primary visualization surface.

---

## 12. Phase E — Operating-system data-model bounce-off `[after / with Phase D]`

Per Craig 2026-05-01: put this information into the operating system as a way to bounce our customer/associate/skill data models off what we've built in this work.

### What this looks like

The customer system already has 27 entity definitions live in dev OS — Company, Contact, Deal, Proposal, Phase, Operation, Opportunity, Associate, AssociateType, etc. (See `customer-system/CLAUDE.md` § 4.) Phase E checks: do those entity definitions accommodate the structure we built in Phases A-C?

- **Skill / Tool skill / Pathway skill** — does the OS have a clean entity for these? Or do they live as records inside Associate / AssociateType?
- **Channel** as an entity? Or as a property of Deployment?
- **System integration** as an entity? Or implicit in `Integration` kernel entity?
- **LOE estimates** — where do they live? On Skill? On AssociateType? On a per-customer Deployment?
- **Co-deployment patterns** — do the entity relationships expose this?

Phase E surfaces where the data we built in Phases A-C *fits* the existing OS entity model and where it *doesn't*. Where it doesn't, that's customer-system feedback — propose entity-model adjustments back into the main customer-system roadmap.

### Why this matters

The pricing-framework work and the customer-system work share the same underlying domain (customers, associates, skills, integrations). If they accumulate divergent data models, we lose the leverage of having one source of truth. Phase E is the explicit reconciliation pass.

`[Detailed Phase E plan to be filled in after Phase D produces the structured output. The plan here is the placeholder + intent.]`

---

## Appendix A — Existing Working Copy annotations Craig has already written

Direct quotes from the Craig|Kyle Working Copy tab. These are Craig's words, not my interpretation — anchors for the work, no editorializing.

- **Renewal Associate:** "Currently integrated: 30 hours. Additional integration: 30-50 hours depending on complexity for new integration. Total 60 hours for new integration + man hours to implement the solution."
- **Intake-for-AMS Associate:** "Every new carrier I add to the mix involves me creating a skill for automation of the quote submission to that carrier. For GIC: Quote Intake Associate for AMS but could be Endorsement Intake Associate for AMS."
- **Knowledge Associate:** "KB Development: 3-5h, Prompt Development: 3-5h, Testing/Evaluation: 2h."
- **Care Associate:** "Outbound phone calls and/or emails, text messages — do we want a default?"
- **Front Desk Associate:** "Qualification needed to define whether this is overflow, after hours, etc."
- **Inbox Associate:** "This is not the same as shipping data from inbox into AMS."

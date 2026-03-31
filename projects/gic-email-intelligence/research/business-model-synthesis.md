# GIC Underwriters — Business Model Synthesis

**Purpose:** Single briefing document for Craig before the demo with JC (EVP/Chief Underwriting Officer). Read this and you understand GIC's business, where the system is wrong, and where automation can deliver real value.

**Sources:** 6 research documents cross-referenced — company-profile.md, lob-catalog.md, carrier-relationships.md, agent-network.md, email-workflow-patterns.md, submission-lifecycle.md. All findings derived from 3,214 real emails, 2,754 submissions, 304 extractions, 3,701 chat conversations, Ryan's UX observations, the Florida OIR examination report, and web research.

**Date:** 2026-03-24

---

## Executive Summary

GIC Underwriters is a 39-year-old Miami-based wholesale insurance broker and MGA with ~29 employees, run day-to-day by the Diaz-Padron family but owned by insurance industry heavyweights David Delaney and VJ Dowling. GIC operates in **two fundamentally different modes**: as a wholesale broker placing business with carriers like USLI and Hiscox (where GIC is an intermediary), and as an MGA for Granada Insurance Company (where GIC has binding authority and controls the full lifecycle). The company handles $78.8M in direct premiums through Granada alone, plus an unknown amount of brokered premium through USLI and other carriers.

**The critical insight from the email data:** 93% of emails in the quote inbox are automated carrier notifications (mostly USLI). Only ~7% involve actual human communication. Of 2,754 submissions, 95% are auto-quoted by USLI with zero GIC involvement. The remaining 5% — roughly 140 submissions — represent 90% of GIC's actual work. This is where the AI system should focus.

**GIC's financial context matters.** Granada Insurance Company lost $15.1M in 2023 with an 87% loss ratio and required $16.85M in capital injection. AM Best downgraded them to B (Fair). JC is not shopping for a nice-to-have — he needs efficiency gains and better-margin programs. Golf carts (where GIC acts as carrier, not broker) represent a strategic shift toward higher-margin, controllable business.

**What the current system gets wrong:** The 5-stage lifecycle model (new/awaiting_info/with_carrier/quoted/attention) conflates auto-quoted USLI notifications with genuinely processed submissions. 85% of submissions sit in "quoted" with no further tracking. The "attention" bucket lumps declines (needing remarketing) with pending files (needing monitoring). There is no closure stage — the queue grows forever. The golf cart portal submissions were incorrectly flagged for missing info that was already in the PDF.

**The opportunity for Indemn:** Build email intelligence that makes Maribel's job faster on the 5% of human-processed submissions, then expand to end-to-end automation on golf carts (where GIC is the carrier), then scale to other LOBs. The immediate value is in triage, info-request drafting, and submission status tracking — not in the auto-quoted USLI flow that already works.

---

## How GIC's Business Works

### Company & Corporate Structure

GIC Underwriters, Inc. sits inside a holding company structure:

```
Granada Financial Group, LLC
├── Ownership: David P. Delaney, Jr. (51% A-units) + Vincent J. Dowling, Jr. (49% A-units)
├── Granada Insurance Services, LLC
└── Hattbert Holdings, Inc.
    ├── GIC Underwriters, Inc. (the wholesale broker / MGA)
    ├── Granada Insurance Company (the carrier, NAIC 16870)
    └── Granada Premium Finance Company
```

**The people who matter:**
- **Owners (investors, not operators):** David Delaney (insurance veteran since 1982, founder of Lancer Insurance/Core Specialty) and VJ Dowling (founder of Dowling & Partners, #1 P&C equity research firm, Harvard Business School). These are sophisticated insurance industry figures, not passive investors.
- **Operators (the Diaz-Padron family):** Juan M. (CEO), Carmen M. (President), Carlos (Secretary/General Counsel), and **JC — Juan Carlos Diaz-Padron** (EVP/Chief Underwriting Officer). JC is our primary contact. 15+ years at GIC, CPCU designation, elected National President of LAAIA (Latin American Association of Insurance Agencies) 2023-2025. He runs the underwriting operation and drives strategy.

GIC operates from two offices: Miami (HQ at 4075 SW 83rd Ave) and Sarasota (managed by Ann Matras-Hamby). Licensed in Florida, Texas, Georgia, and Arizona, but the email data shows business is overwhelmingly Florida.

### The Two Operating Modes

This is the single most important thing to understand about GIC. They operate in two completely different modes simultaneously, and the data model, workflow, automation approach, and economics differ for each.

#### Mode 1: GIC as Wholesale Broker (USLI, Hiscox, others)

**What happens:** A retail agent has an insurance need their standard markets can't handle. They submit the risk to GIC. GIC evaluates the risk, identifies the right carrier, submits to the carrier, and relays the carrier's response back to the agent. GIC earns a commission from the carrier for placing the business.

**Who controls what:**
- Underwriting decision: **Carrier** (USLI, Hiscox)
- Pricing: **Carrier**
- Policy issuance: **Carrier**
- GIC's role: Intermediary — triage, data extraction, submission, relay, follow-up

**Economics:** GIC earns a brokerage commission (typically 10-15% of premium) for placing business. GIC does not bear insurance risk.

**Workflow:**
```
Retail Agent → submits to GIC (email or portal)
    → GIC triages (LOB, carrier selection, completeness check)
    → GIC submits to carrier (USLI portal, email, or API)
    → Carrier responds (quote / pending / decline)
    → GIC relays response to agent
    → Agent presents to end customer
    → If accepted: agent sends bind instruction to GIC → GIC forwards to carrier
    → Carrier issues policy
```

**Critical detail:** For USLI (95% of brokered volume), most of this workflow is automated. The agent submits through USLI's Retail Web portal directly, USLI auto-quotes, and GIC receives a notification copy. GIC's active involvement is minimal for auto-quoted USLI business.

**Data needs:** Carrier response tracking, submission-to-carrier mapping, pending file management, decline/remarket tracking, commission tracking.

**Automation opportunity:** Moderate for the automated USLI flow (already works). High for the human-processed exceptions — info request drafting, completeness checking, status tracking, follow-up management.

#### Mode 2: GIC as MGA/Carrier (Granada Insurance Company paper)

**What happens:** For certain lines, GIC has binding authority from Granada Insurance Company. GIC underwrites the risk, sets pricing, and issues the policy on Granada paper. GIC controls the entire lifecycle.

**Who controls what:**
- Underwriting decision: **GIC**
- Pricing: **GIC**
- Policy issuance: **GIC/Granada**
- GIC's role: Full control — underwrite, quote, bind, issue, service

**Economics:** GIC manages the full premium ($78.8M in 2023 through Granada) and receives MGA compensation (~$17.7M, or 22.5% of premiums). But Granada also bears the insurance risk, and with an 87% loss ratio, the underwriting performance matters directly.

**Confirmed lines on Granada paper:**
- Commercial property, commercial auto, commercial liability (Florida only, per Granada's authorized lines)
- Golf Cart / Motorsports (confirmed by the Motorsports portal being GIC-branded, not carrier-branded)

**Workflow:**
```
Retail Agent → submits to GIC (Motorsports portal or email)
    → GIC extracts data, checks completeness
    → GIC underwriter reviews directly (no external carrier)
    → GIC issues quote or declines
    → If accepted: GIC/Granada binds directly
    → Granada Insurance policy issued (format: 0185FL00XXXXXX)
```

**Data needs:** Full underwriting file, risk assessment, pricing calculation, policy lifecycle, loss tracking, reinsurance allocation.

**Automation opportunity:** Very high. Because GIC controls the entire workflow, end-to-end automation (submission → extraction → validation → quote → bind) is achievable without any external carrier API dependency. This is the EventGuard model applied to golf carts.

#### Why the Dual Mode Matters for Our System

Every submission in the system needs a flag: **brokered** vs. **direct-underwritten**. This determines:
- Which lifecycle stages apply (brokered has "awaiting_carrier_action"; direct has "UW review")
- Who makes the next-action decision (carrier vs. GIC underwriter)
- What data is needed (carrier submission requirements vs. GIC underwriting guidelines)
- What can be automated (relay vs. end-to-end)
- What the economics look like (commission vs. full premium management)

### The Complete Value Chain

```
Retail Agent submits risk
    ↓
GIC RECEIVES (quote@gicunderwriters.com, portal, or phone → CSR relay)
  • Who: Maribel (primary), CSR team as relay
  • Time: Continuous during business hours (8:30 AM - 5:00 PM ET)
  • Data: Unstructured email with ACORD forms, PDFs, photos, or structured portal application
  • Can automate: Email classification, LOB detection (USLI prefix = 100% reliable), insured name extraction
    ↓
GIC TRIAGES
  • Who: Maribel, underwriters
  • Time: Minutes to hours (no formal SLA observed)
  • Data: LOB determination, carrier appetite check, completeness assessment
  • Can automate: LOB classification, completeness checking against LOB-specific required fields, carrier routing suggestion
    ↓
[IF INCOMPLETE] → GIC REQUESTS INFO
  • Who: Maribel, JC for complex requests
  • Time: Draft and send same day; agent response 1-5+ days
  • Data: Specific missing items (Wind Mit, 4-Point, driver info, hull values)
  • Can automate: Gap identification, info request draft generation. Human review before sending.
    ↓
[IF BROKERED] → GIC SUBMITS TO CARRIER
  • Who: GIC underwriter submits via carrier portal, email, or API
  • Time: Same day after triage (for human-processed). Instant for USLI Retail Web auto-submissions.
  • Data: Complete application package
  • Can automate: Partially. Auto-submission to USLI would require USLI portal API access (not confirmed).
    ↓
[IF DIRECT] → GIC UW REVIEWS
  • Who: JC, Celia Acosta-Galvin (VP Underwriting at Granada)
  • Time: Unknown — golf cart program is new
  • Data: Application data, underwriting guidelines, loss history
  • Can automate: Risk scoring, guideline checking, quote generation for standard risks. Human review for exceptions.
    ↓
CARRIER/UW DECISION
  • Brokered: USLI responds with Quote / Pending / Decline (minutes for auto, days for manual)
  • Direct: GIC underwriter decides
  • Data: Quote terms, premium, conditions, or decline reason
  • Can automate: For brokered — classify carrier response, extract quote terms. For direct — full quote generation.
    ↓
QUOTE/DECLINE → AGENT NOTIFIED
  • Who: Maribel relays to agent; for USLI Retail Web, agent may already have the quote
  • Time: Same day for auto-quoted; 1-5+ days for human-processed
  • Data: Quote PDF, coverage terms, premium, conditions
  • Can automate: Quote delivery email drafting, decline notification, remarket suggestions
    ↓
BIND/CLOSE
  • Who: Agent sends bind instruction to bind@gicunderwriters.com (separate inbox, not in our data)
  • Time: Unknown — bind data is outside our current scope
  • Data: Bind confirmation, payment, policy issuance
  • Can automate: For direct (golf carts) — full bind processing. For brokered — relay bind instruction to carrier.
```

---

## People & Roles

### The GIC Team (from email threads, chat transcripts, and the OIR report)

| Person | Title | What They Actually Do | Channels |
|--------|-------|----------------------|----------|
| **Juan Carlos Diaz-Padron (JC)** | EVP, Chief Underwriting Officer | Strategic leader. Signs info requests on complex submissions. Makes underwriting decisions. Drives technology adoption. Our primary stakeholder. | Email, meetings |
| **Maribel Rodriguez** | Quote Processor | The operational heart of GIC. Processes the majority of submissions in quote@. Sends info requests, relays agent info to USLI, delivers quotes. Operates as "GIC Quotes." | Email (quote@) |
| **Julissa Arriola** | Underwriter (Transportation Division) | Handles commercial auto, trucking, motor truck cargo. Issues physical damage quotes. Advises on binding procedures. | Email |
| **Saly Casanueva** | Underwriter | Forwards USLI quotes internally, handles internal routing. | Email |
| **Claudia Inoa** | Contract Binding (E&S) | Handles approval requests to external carriers (AmTrust). E&S surplus lines processing. | Email |
| **Tai-Siu De la Prida** | CSR | Handles live chat escalations. Forwards agent phone/email inquiries to quote team. Revealed the $500K delivery max on commercial auto. | Chat, email (csr@) |
| **Coralia Nunez** | CSR | Handles live chat escalations alongside Tai-Siu. | Chat |
| **Maria Gonzalez** | CSR | Relays agent follow-ups to quote team. Tracks missing info status. | Email (csr@) |
| **Celia I. Acosta-Galvin** | VP Underwriting (Granada Insurance) | Per the OIR report. Likely involved in direct-underwriting decisions. | Unknown |
| **Ann Matras-Hamby, CIC, AU** | Regional Branch Manager | Runs the Sarasota office. | Sarasota operations |

### The Two Internal Teams

**CS Team** (Tai-Siu, Coralia, Maria Gonzalez): Handles episodic agent inquiries via chat and phone. AI-first with human backup. ~1,500 chat conversations/month. They are the message relay when agents can't get through on email — they forward to the quote team.

**Placement Team** (Maribel, Julissa, Saly, Claudia, JC): Handles submission intake, data extraction, carrier coordination, quoting. This is where the real underwriting work happens. Email-first workflow.

**The cross-team gap:** When an agent asks about appetite via chat (CS stream) and also submits a risk via email (Placement stream), neither team knows about the other's interaction. Ryan's wireframes propose cross-team awareness flags to fix this.

### The Retail Agents

GIC's customers are licensed insurance producers — independent retail agents and small agency principals in South Florida. Key characteristics:
- Predominantly Hispanic/Latino market agencies (Univista, Sebanda Insurance, Caiman Insurance, Estrella Insurance)
- Bilingual (English/Spanish, some communicate in Spanglish)
- Professional shorthand communicators ("comercial auto," "wc market for 8810 NOC," "flatt cancellation")
- 4-digit agency codes (e.g., #7406, #7146, #7241)
- Range from small independents to national aggregators (Acrisure Southeast Partners)
- Top agents generate disproportionate volume (classic 80/20 pattern)

---

## Lines of Business — Operational View

GIC handles 39+ LOBs, but they fall into three operationally distinct tiers:

### Tier 1: High-Volume USLI Brokerage (80% of email volume)

These are GIC's bread and butter. High-volume, low-complexity lines placed through USLI. Most are auto-quoted — GIC receives notification copies but does minimal active processing.

| LOB | Email Count | USLI Prefix | What It Is |
|-----|-------------|-------------|------------|
| Personal Liability | 725 | XPL | Personal umbrella/catastrophe coverage |
| General Liability | 574 | MGL | Commercial GL for small businesses |
| Special Events | 245 | MSE | Event liability (similar to Indemn's EventGuard) |
| Non Profit | 219 | NPP/NDO | Nonprofit D&O and GL |
| Excess Personal Liability | 217 | XPL/PCL | Personal excess coverage |
| Commercial Package | 205 | MCP | GL + Property bundled |
| Commercial Property | 200 | NPP/MPR | Standalone property |

**Workflow:** Agent → USLI Retail Web auto-quote → GIC notification copy. Zero GIC effort in most cases.

**Automation value:** Low for the auto-quoted flow (already automated by USLI). Value is in the exceptions — partial declines, pending files, remarketing.

### Tier 2: Specialty Brokerage (15% of email volume)

Higher-complexity lines that more often require GIC underwriting judgment, carrier selection, and active processing.

| LOB | Email Count | Primary Carrier | Complexity |
|-----|-------------|----------------|------------|
| Professional Liability | 86 | USLI (MPL) | Multi-carrier options |
| Excess Liability | 78 | USLI | Layered coverage |
| Allied Healthcare | 76 | USLI | Medical-adjacent risks |
| Contractors Equipment | 71 | USLI (CEQ) | Inland marine specialty |
| Builders Risk | 42 | USLI (BRK) | High decline rate |
| Workers Compensation | Frequent chat topic | AmTrust, others | Different carrier entirely |
| Commercial Auto/Trucking | 18 | GIC Transportation Division | Specialized handling |
| Homeowners | 20 | Swyfft, USLI (rare) | TX/AZ only, not FL |

**Workflow:** More info requests, multi-carrier shopping, partial declines needing remarketing. This is where Maribel and the underwriters spend their time.

**Automation value:** High. Info request drafting, completeness checking, carrier appetite matching, status tracking.

### Tier 3: GIC as Carrier — Direct Underwriting (Emerging)

| LOB | Volume | Carrier | Status |
|-----|--------|---------|--------|
| Golf Cart / Motorsports | 4 submissions found | GIC/Granada | New program, dedicated portal |

**Workflow:** Portal or email → GIC extracts → GIC underwrites directly → GIC quotes/declines → GIC binds. No external carrier.

**Automation value:** Highest. Full end-to-end automation possible. This is the EventGuard model. JC's stated priority.

### Special Events as Next-LOB Candidate

Special Events (245 emails, MSE prefix) is structurally similar to Indemn's existing EventGuard product. After golf carts, this is the natural next LOB for deeper automation — high volume, relatively standardized applications, single-carrier (USLI).

---

## Carrier Relationships — Operational View

### USLI: The Engine (91% of email volume, 95% of submissions)

USLI (United States Liability Insurance Group, Berkshire Hathaway subsidiary, AM Best A++ rated) dominates GIC's brokerage business. The numbers are stark:

| USLI Email Type | Count | What It Means |
|-----------------|-------|---------------|
| usli_quote | 2,553 | Auto-generated quote notifications |
| usli_pending | 212 | Carrier needs more info |
| usli_decline | 147 | Carrier declined the risk |
| **Total** | **2,912** | **91% of all inbox email** |

**How USLI works with GIC:**
1. Agent submits via USLI's Retail Web portal (accessed through GIC)
2. USLI auto-quotes eligible risks (3-hour advertised turnaround)
3. GIC receives notification emails with 3 PDF versions (Customer, Retailer, Applicant)
4. If USLI can't auto-quote: pending file request → GIC mediates info gathering
5. If USLI declines: sometimes includes "Remarket This Risk" email with pre-filled application

**USLI reference numbers are the best signal in the data.** Format: `[PREFIX][NUMBERS]` where the prefix deterministically identifies the LOB. Examples: MGL (General Liability), XPL (Excess Personal Liability), MSE (Special Events), MCP (Commercial Package). 99.7% of USLI quote emails contain the reference number in the subject line.

**Known USLI underwriters:** Julie O'Brien, Jee Choi, Jacob Webster, Frank Finney, Frederick Robinson, Brian Donahue, Nicole Warn, Michael Burd, Elizabeth Shults, Ashley Okoorian, Daniel Hager.

**Key implication:** GIC's brokerage business is essentially a USLI distribution operation. This creates carrier concentration risk but also means USLI's systems and patterns are highly predictable for automation.

### Hiscox: The Alternative Market (24 emails)

Hiscox writes small commercial risks — GL, professional liability, cyber, technology E&O. 24 Hiscox quote emails identified. Hiscox emails are rich HTML with premium, coverage details, and a "Retrieve quote" portal link.

Listed as a carrier option in the GL LOB configuration alongside USLI. Likely used when risks don't fit USLI's appetite or when GIC wants to offer competitive quotes.

### Granada Insurance: The Affiliated Carrier (GIC as MGA)

Granada Insurance Company is GIC's sister company. GIC wrote $78.8M in direct premiums for Granada in 2023 and received $17.7M in MGA compensation (22.5%).

**Financial reality (December 31, 2023):**
- Total assets: $125.0M
- Surplus: $23.1M (above FL minimum of $10M)
- Loss ratio: 87% (very high)
- Net income: -$15.1M
- Capital injections from parent: $16.85M in 2023, $9.0M in 2022
- AM Best rating: B (Fair), downgraded from B+
- Reinsurance: Quota share with Swiss Re America

The parent company is injecting $25.85M over two years to keep Granada afloat. This financial pressure is likely driving JC to seek:
1. Operational efficiency (do more with less)
2. Higher-margin programs (golf carts — GIC controls pricing and underwriting)
3. Better loss ratio through tighter underwriting (AI-assisted risk selection)

**The Granada API** is the existing technical integration point:
- Endpoint: `services-uat.granadainsurance.com`
- Returns policy data for both Granada-underwritten AND USLI-brokered policies
- This means Granada's management system is the unified policy record for all GIC business
- Contact for management system API access: **Jeremiah** (per Kyle's email to JC: "The biggest unlock on our side is getting connected to Jeremiah for the management system APIs")

### Other Carriers (Less Characterized)

| Carrier | Evidence | LOBs |
|---------|----------|------|
| AmTrust | Approval request emails from Claudia Inoa | Workers Compensation, E&S |
| Swyfft | Zendesk-format underwriting follow-ups | Homeowners |
| Mid Continent Casualty | Motor truck cargo thread | Trucking |
| Concept Special Risks | Email references | Specialty/niche |

GIC claims 15+ carrier relationships on their website. The full carrier panel is an open question for JC.

---

## The Agent Network

### How Agents Interact with GIC

GIC operates three parallel channels that share the same retail agent population:

**Channel A: Chat (CS/Servicing, AI-first)**
- Indemn's Fred AI on the GIC broker portal
- ~1,500 conversations/month
- Handles: policy lookups, appetite questions, billing, cancellations
- 44% of conversations end in failure (missed handoffs, timeouts, abandonment)
- Only 8% resolved autonomously by AI
- Pain points: over-formal AI voice, one-question-per-turn slot filling, no upfront capability disclosure, policy format parsing failures (the "-3" endorsement suffix), after-hours invisibility

**Channel B: Email (Placement/Underwriting)**
- quote@gicunderwriters.com
- 3,214 emails over ~6 months
- Handles: new submissions, info request replies, follow-ups, renewals
- Maribel is the primary processor
- Pain points: unstructured submissions, inconsistent quality, attachment clutter (email signature images), multi-channel agent follow-ups creating internal relay chains

**Channel C: Voice (Emerging)**
- RingCentral phone system
- JC actively pushing for call recording and transcription
- Not yet operational for data capture
- JC's March 20 email: "I wanted to follow up to see what is required to start recording calls to capture data for customer service"

### What Agents Actually Want

Based on Ryan's 17 UX observations and the email patterns:

1. **Speed.** They communicate in shorthand because they know the domain. Sequential one-question-per-turn intake is patronizing. A human CSR would handle their request in 2-3 exchanges, not 13.
2. **Transparency.** Tell them upfront what the system can and cannot do. Don't collect 20 turns of data for a quote the bot can't generate.
3. **Working policy lookups.** Format tolerance is essential — "policy#0185FL00184576 - 3" must work, not just the stripped version.
4. **Appetite answers.** "Do you have WC market for 8810 NOC?" is a legitimate question that deserves an answer, not "no direct FAQ entry."
5. **Submission status.** Where is my submission in the pipeline? This is the most common unmet need.

---

## The Real Submission Lifecycle

### The Current (Broken) 5-Stage Model

| Stage | Count | % | Problem |
|-------|-------|---|---------|
| new | 53 | 1.9% | Doesn't distinguish unread from being-worked-on |
| awaiting_info | 32 | 1.2% | Doesn't track whether agent already replied |
| with_carrier | 1 | 0.04% | Barely used; USLI auto-flow doesn't trigger it |
| quoted | 2,347 | 85.2% | Black hole — no further tracking, no closure |
| attention | 321 | 11.7% | Lumps declines and pending files together |

### The Two Lifecycles That Actually Exist

**Lifecycle A: Carrier-Automated (95% of volume, 5% of GIC's work)**

```
Agent uses USLI Retail Web → USLI auto-quotes → Notification arrives at GIC → [Done]
```

GIC is a passthrough. The agent already has the quote through USLI's portal. GIC tracks for commission purposes. No active processing.

**Lifecycle B: Human-Processed (5% of volume, 90% of GIC's work)**

```
Submission arrives → GIC triages → [Info gap? Request it from agent] →
[Carrier review needed? Submit to carrier] → Carrier responds → GIC delivers to agent →
[Bind instruction? Route to bind@] → Policy issued
```

This involves actual underwriting judgment, multi-party communication, and follow-up management. This is where AI adds value.

### Proposed 8-Stage Model

Validated against all email thread analysis and all six research documents:

| Stage | Description | Ball Holder | Trigger In | Trigger Out |
|-------|-------------|-------------|------------|-------------|
| **received** | Email/portal submission arrived, not yet reviewed | Queue | Email arrives at quote@ or portal submission | GIC staff opens/reviews |
| **triaging** | GIC reviewing: LOB, carrier fit, completeness | GIC | Staff opens submission | Decision made on next step |
| **awaiting_agent_info** | GIC sent info request, waiting for agent reply | Agent | Info request sent | Agent reply arrives |
| **awaiting_carrier_action** | Submitted to carrier, waiting for response | Carrier | Submission sent to carrier | Carrier quote/pending/decline |
| **processing** | All info in hand, GIC actively working | GIC | Info received, or carrier responded | Quote issued or declined |
| **quoted** | Quote issued and delivered to agent | Agent | Quote forwarded to agent | Bind instruction or expiration |
| **declined** | Carrier declined, may need remarketing | GIC or Agent | Carrier decline received | Remarket, notify agent, or close |
| **closed** | Final disposition | Done | Bound, expired, withdrawn | N/A |

**Key improvements over current model:**
1. "new" splits into "received" (unread) and "triaging" (being worked)
2. "awaiting_info" becomes "awaiting_agent_info" — explicit about who GIC is waiting on
3. "with_carrier" becomes "awaiting_carrier_action" — clear that the carrier has the ball
4. "attention" is eliminated — declines and pending files are now distinct stages
5. "closed" exists — submissions can actually end
6. **Ball holder is explicit** — at every stage, someone is responsible for the next action
7. "processing" captures the "agent replied but GIC hasn't acted yet" gap (the Arenal Property Management problem)

### How the 8-Stage Model Maps to Each Operating Mode

**Brokered (USLI/Hiscox):** received → triaging → [awaiting_agent_info] → awaiting_carrier_action → [quoted | declined] → closed

**Direct-underwritten (Golf Cart):** received → triaging → [awaiting_agent_info] → processing (UW review) → [quoted | declined] → closed

The "awaiting_carrier_action" stage only applies to brokered business. Direct-underwritten business goes from triaging to processing (internal UW review), skipping the carrier.

---

## Where the Current System Gets It Wrong

### 1. The "Quoted" Black Hole
**Problem:** 2,347 submissions (85%) are in "quoted" with no further lifecycle tracking. The system cannot distinguish: quotes the agent has seen, quotes the agent never received, quotes that expired, quotes that were bound, or quotes placed with a competitor.
**Root cause:** The system treats "carrier issued a quote" as a terminal state. But from GIC's perspective, a quote is the beginning of the sales process, not the end.
**Fix:** Add post-quote tracking: delivered, pending_decision, bound, expired, withdrawn.

### 2. Auto-Quoted vs. Human-Processed Conflation
**Problem:** A USLI auto-quote (zero GIC effort) and a GIC-processed quote (days of work) both land in "quoted."
**Root cause:** The system doesn't distinguish the two lifecycles.
**Fix:** Tag each submission with its automation level: auto_notified (GIC passthrough) vs. actively_processed (GIC did work). Different reporting, different follow-up rules.

### 3. "Attention" is Too Coarse
**Problem:** 321 submissions in "attention" with two very different sub-types: declined (151) needing remarketing, and carrier_pending (170) needing monitoring. These require completely different actions.
**Root cause:** "attention" was designed as a catch-all rather than specific action states.
**Fix:** Promote to first-class stages: "declined" and "awaiting_carrier_action."

### 4. No "Agent Replied" Trigger
**Problem:** Submissions stay in "awaiting_info" even after the agent provides everything. The Arenal Property Management submission: agent replied with documents, followed up 3 days later, CSR confirmed info was received — still "awaiting_info."
**Root cause:** No event triggers stage advancement when an agent_reply email arrives.
**Fix:** When an agent_reply email matches a submission in "awaiting_agent_info," auto-advance to "processing."

### 5. Portal Submissions Incorrectly Flagged
**Problem:** Golf cart portal submissions were set to "awaiting_info" by the AI because it "identified missing golf cart info — VIN, DL, storage, registration." But the portal PDF already contains this data.
**Root cause:** The extraction pipeline didn't parse the portal PDF fully, or the gap analysis ran before extraction completed.
**Fix:** For portal submissions, trust the structured data. Run extraction first, then gap analysis.

### 6. No Closure
**Problem:** Old submissions accumulate in "quoted" or "attention" forever. No way to distinguish active work from historical records.
**Root cause:** No "closed" stage with resolution codes (bound, expired, withdrawn, remarketed-elsewhere).
**Fix:** Add closure stage with resolution codes. Auto-close quotes older than 90 days as "expired."

### 7. Missing Outbound Tracking
**Problem:** GIC's sent emails to agents and carriers are largely invisible. Only replies that come back to quote@ reveal what GIC sent.
**Root cause:** The system only monitors inbound to quote@. GIC's outbound goes from individual staff addresses.
**Fix:** Acknowledge this limitation. Design the system to infer outbound from reply chains rather than tracking it directly (unless GIC grants sent-folder access).

### 8. LOB Misclassification
**Problem:** Golf cart submissions were classified as "Trucking" and "Inland Marine" because the original LOB list didn't include "Golf Cart" or "Motorsports."
**Root cause:** Hardcoded LOB taxonomy that predated the golf cart program.
**Fix:** Already addressed by adding Golf Cart as a canonical LOB. But the broader issue is that LOB classification should use multiple signals: USLI prefix (deterministic), subject line keywords, portal source, and attachment content.

---

## Automation Opportunities

### Stage-by-Stage Analysis

| Stage | Fully Automatable | AI-Assisted (Human Review) | Human-Only |
|-------|------------------|---------------------------|------------|
| **Received** | Email classification, LOB detection (USLI prefix), insured name extraction, submission deduplication | — | — |
| **Triaging** | Carrier appetite matching, completeness checking against LOB config | Carrier selection for multi-market risks, unusual risk assessment | Complex underwriting judgment, relationship-based decisions |
| **Info Request** | Gap identification, info request draft generation, template selection | Review before sending (tone, accuracy, completeness) | Negotiating hull values, interpreting conflicting documents |
| **Carrier Submission** | — | Pre-filling carrier portal forms from extracted data | Logging into carrier portals, navigating carrier-specific workflows |
| **UW Review (direct)** | Standard risk scoring, guideline compliance checking | Rating for borderline risks, exception approval | Novel risk types, large accounts, reinsurance referrals |
| **Quote Delivery** | Auto-forward USLI quotes to agents, draft cover letters | Review complex quotes before delivery | Multi-coverage explanations, upsell recommendations |
| **Decline/Remarket** | Alternative carrier suggestions, remarket submission drafting | Deciding whether to remarket or close | Carrier relationship management, creative placement |
| **Follow-up** | Overdue info request reminders, stale submission alerts, renewal warnings | Prioritizing follow-ups, escalation decisions | Agent relationship management |

### The Golf Cart Automation Path

Golf carts are the clearest automation path because GIC is the carrier:

1. **Today (demo):** Show email intelligence — the system understands the inbox, extracts golf cart application data, identifies gaps, and drafts info requests.
2. **Next (operational tool):** Maribel uses the system daily for golf cart submissions. Auto-extract from portal PDFs, validate completeness, flag exceptions for review.
3. **Target (full automation):** Retail agent submits via portal or email → system extracts, validates, scores risk, generates quote, sends to agent → agent clicks "bind" → policy issued on Granada paper. No human in the loop for standard risks. This follows the EventGuard model.

### The USLI Brokerage Automation Path

For the 95% auto-quoted USLI business, automation value is in the exceptions:

1. **Pending files (212):** Auto-identify what USLI is asking for, draft the info request to the agent, track the response.
2. **Declines (147):** Auto-classify decline reason, suggest alternative carriers, draft remarket submission.
3. **Partial declines:** Detect when USLI declines one component but quotes another, alert GIC to find alternative coverage for the declined component.
4. **Status tracking:** Give agents real-time submission status via the chatbot (the most requested feature).

### Data Needed for Automation

| Data | Source | Status |
|------|--------|--------|
| LOB-specific required fields | Built for GL (10 fields) and Golf Cart (17 fields); generic (8 fields) for others | Partially done |
| USLI prefix → LOB mapping | 24 prefixes documented, deterministic | Done |
| Carrier appetite rules | Not documented | Need from JC |
| Underwriting guidelines (golf cart) | Not documented | Need from JC |
| Agent/agency master list | Partial from email data | Need from JC/management system |
| Management system API access | Granada API exists (UAT); Jeremiah is the contact | In progress |
| Info request templates | Observed from email threads | Can extract and formalize |

---

## Financial Context & Strategic Implications

Granada Insurance Company is under financial stress. The numbers are clear:

| Metric | 2023 Value | Implication |
|--------|-----------|-------------|
| Loss ratio | 87% | Losing money on underwriting |
| Net income | -$15.1M | Significant operating loss |
| Capital injection | $16.85M (2023), $9.0M (2022) | Parent propping up the company |
| AM Best rating | B (Fair), downgraded | Credibility risk with agents and reinsurers |
| Surplus | $23.1M (FL minimum: $10M) | Adequate but declining |

**What this means for our approach:**

1. **JC is not buying a toy.** He needs tools that directly improve operational efficiency and underwriting performance. Frame the demo around "this saves Maribel X hours per week" and "this catches risks that should be declined before they become losses," not "look at this cool AI."

2. **Golf carts are strategic, not incidental.** A well-underwritten golf cart program on Granada paper gives GIC a high-margin line they fully control. If they can write golf carts at a 50-60% loss ratio (reasonable for this simple risk class), it directly improves Granada's book.

3. **Efficiency gains matter more than features.** Every hour saved in the email processing workflow is an hour Maribel can spend on revenue-generating activities (processing more submissions, following up on pending quotes). With 29 employees and $78.8M in premium, headcount efficiency is critical.

4. **The AM Best downgrade creates urgency.** A B rating makes it harder to write business — agents and reinsurers pay attention to AM Best ratings. Improving the loss ratio and demonstrating operational sophistication could support a future rating upgrade.

5. **The ownership structure matters.** Delaney and Dowling are sophisticated insurance investors who understand MGA economics, loss ratios, and technology leverage. If JC presents a compelling AI-driven efficiency story, the ownership is likely to support investment.

---

## Priority Questions for JC

Ranked by impact on our understanding and ability to build the right system.

### Must-Ask (Blocks System Design)

1. **Golf cart program structure:** Is the Motorsports program on Granada Insurance Company paper? What are the underwriting guidelines? What is the target premium volume? What is the current quote-to-bind ratio?

2. **Management system API access:** Kyle mentioned Jeremiah as the contact. What does the management system (Unisoft?) track? Can we get API access for submission status, policy data, and agency records?

3. **Who handles what in the email workflow?** Is Maribel the sole quote processor, or does she have a team? How does work get assigned? What is the current processing SLA (if any)?

4. **What happens after "quoted"?** Do agents receive USLI quotes directly through Retail Web, or does GIC forward them? Bind requests go to bind@ — what happens there?

### Should-Ask (Improves System Quality)

5. **Full carrier panel:** Beyond USLI, Hiscox, and Granada — which carriers does GIC use? Any specific carriers for WC, commercial auto, homeowners?

6. **Agent count and distribution:** How many retail agencies does GIC work with actively? What's the top-10 by volume? What's the geographic mix?

7. **What does JC see as the biggest operational bottleneck?** Email triage? Info gathering? Carrier submission? Quote delivery? Understanding his pain ranking helps us prioritize.

8. **Carrier appetite rules:** When a GL submission comes in, how does GIC decide USLI vs. Hiscox vs. another carrier? Rules-based or judgment-based?

### Good-to-Ask (Informs Roadmap)

9. **RingCentral / Voice integration timeline:** JC is pushing for call recording. When does he expect this to be operational? What's the plan upgrade status?

10. **Expansion plans beyond Florida?** GIC is licensed in TX, GA, AZ but email volume is overwhelmingly FL. Any growth plans?

11. **Granada's financial trajectory:** Is the loss ratio improving? Are there lines being shed? Is the ownership group planning further capital injections?

12. **The Topa Insurance Group acquisition:** Did it close? Does this affect GIC's carrier capacity or product offerings?

---

## Data Model Recommendations

Consolidated from all six research documents. These are the schema changes needed to accurately model GIC's business.

### 1. Operating Mode as a Core Field
Every submission needs: `operating_mode: "brokered" | "direct_underwritten"`
- Determines lifecycle path, stage options, automation rules, and economics
- Brokered: GIC is intermediary, carrier makes decisions
- Direct: GIC is carrier, controls entire lifecycle

### 2. Carrier as a First-Class Entity
```
carrier: {
  name: string,              // "USLI", "Hiscox", "Granada/GIC"
  type: "external" | "affiliated",
  submission_method: "portal" | "email" | "api",
  response_email_patterns: [...],   // Regex for subject line parsing
  reference_format: string,         // e.g., "[PREFIX][NUMBERS]" for USLI
  supported_lobs: [...],
  appetite_rules: {...},            // What they will/won't write
  binding_authority: boolean        // Can GIC bind on their behalf?
}
```

### 3. LOB Configuration Per LOB
```
lob_config: {
  canonical_name: string,
  carrier_options: [carrier_id, ...],
  required_fields: [...],           // Varies by LOB
  workflow_type: "brokered" | "direct",
  usli_prefix: string | null,       // Deterministic LOB identification
  portal_source: string | null,     // "motorsports", "roofing", etc.
  typical_cycle_time: number,
  appetite_description: string
}
```
Two configs built (GL: 10 fields, Golf Cart: 17 fields). 37 LOBs use generic 8-field config.

### 4. Submission Stage Model (8-Stage)
Replace current 5-stage model:
```
stage: "received" | "triaging" | "awaiting_agent_info" | "awaiting_carrier_action" | "processing" | "quoted" | "declined" | "closed"
ball_holder: "queue" | "gic" | "agent" | "carrier" | "done"
resolution: null | "bound" | "expired" | "withdrawn" | "remarketed" | "declined_no_alternative"
automation_level: "auto_notified" | "actively_processed"
```

### 5. Agent/Agency as a First-Class Entity
```
agent: {
  name: string,
  agency_name: string,
  agency_code: string,         // 4-digit code (e.g., "7406")
  email: string,
  lobs_submitted: [...],
  submission_count: number,
  avg_completeness: number,    // How often they send complete submissions
  response_time_avg: number,   // How fast they reply to info requests
  active: boolean
}
```

### 6. Multi-Email Thread Linking
Current approach (grouping by insured/reference) is correct. Additionally:
- USLI reference numbers should be first-class identifiers alongside GIC submission numbers
- Info request → agent reply linking should trigger automatic stage advancement
- Duplicate USLI emails (same quote, multiple versions) should be deduplicated or version-tracked

### 7. Intake Channel Tracking
```
intake_channel: "usli_retail_web" | "gic_portal" | "granada_portal" | "agent_email" | "csr_relay" | "phone"
```
Portal submissions should NOT trigger info-request drafts (data is already structured).

### 8. Cross-Channel Awareness
When the same insured name or agent appears in both chat (CS stream) and email (Placement stream), the system should create an awareness flag — not merge the records, but surface the cross-channel activity.

### 9. Financial Tracking Hooks
For direct-underwritten business (golf carts), the system should have fields for:
- Premium quoted, premium bound
- Loss ratio by LOB (when claims data becomes available)
- Conversion rate (quote → bind)
- Processing time (submission → quote → bind)

---

## Sources

| Document | Key Contributions |
|----------|------------------|
| [company-profile.md](company-profile.md) | Corporate structure, ownership, financials, competitive landscape, technology stack, golf cart market sizing |
| [lob-catalog.md](lob-catalog.md) | LOB distribution (39 canonical LOBs), USLI prefix mapping (24 prefixes), tier classification, golf cart LOB config |
| [carrier-relationships.md](carrier-relationships.md) | USLI dominance (91% of email), Hiscox role, Granada API details, carrier interaction lifecycle, policy API service chain |
| [agent-network.md](agent-network.md) | Agent personas, chat channel pain points (44% failure rate), email submission patterns, two-team structure, cross-channel gap |
| [email-workflow-patterns.md](email-workflow-patterns.md) | 6 workflow patterns (auto-quote, decline-then-quote, info request cycle, CSR relay, portal vs. email), 93% automated email insight, GIC staff roles |
| [submission-lifecycle.md](submission-lifecycle.md) | Two-lifecycle model, 8-stage proposal, 7 system failures, edge cases (name mismatches, test submissions, bind requests in wrong inbox) |

### Cross-Document Insights

1. **The 93%/7% split** (email-workflow-patterns) explains why **85% of submissions are "quoted"** (submission-lifecycle) — most submissions are auto-quoted USLI business that flows through without GIC involvement.

2. **Granada's financial stress** (company-profile) + **golf carts as direct-underwritten** (lob-catalog, carrier-relationships) = golf carts are not just a product demo — they're a strategic diversification play toward higher-margin, controlled business.

3. **The chat failure rate** (agent-network: 44% failure, 8% autonomous resolution) + **the email workflow complexity** (email-workflow-patterns: info request cycles, CSR relay chains) = GIC's agents are underserved on both channels. The email intelligence system addresses the higher-value channel (placement) where the economic impact is largest.

4. **The USLI prefix deterministic LOB mapping** (lob-catalog) + **USLI reference numbers in 99.7% of quote subjects** (carrier-relationships) = the most reliable classification signal in the data doesn't require AI at all — it's a simple regex parse.

5. **The cross-team visibility gap** (agent-network: CS team and Placement team don't share context) + **the CSR relay pattern** (email-workflow-patterns: CSR forwards agent messages to quote team) = the same problem manifesting in two ways. The system should surface cross-channel activity without merging workflows.

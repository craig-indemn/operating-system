# Agent Network — How Retail Agents Interact with GIC

## Methodology
Synthesized from Ryan Denning's UX Observation Report (March 10, 2026, 14 resolved conversations), email thread analysis from Craig/Kyle/JC correspondence (Jan-Mar 2026), GIC Email Intelligence data (3,214 emails from quote@gicunderwriters.com), observatory data (3,701 real chat conversations), and Ryan's GIC wholesaler wireframes.

## Sources
- Ryan's UX Observation Report (PDF, 25 pages, 17 observations, 14 screenshots)
- GIC Email Intelligence MongoDB: 3,214 classified emails, 2,754 submissions
- Observatory data: 3,701 real conversations, 40,747 total closed conversations
- Email threads: Kyle/JC partnership negotiations, Craig/JC RingCentral coordination
- Ryan's wireframes: gic_wholesaler_wireframes.html, gic_wholesaler_diagram.html

## Date Analyzed
2026-03-24

---

## Findings

### 1. Who the Retail Agents Are

GIC's users are **licensed insurance producers** — independent retail agents and small agency principals who use GIC as a wholesale broker to place insurance for their end customers. They are professionals with constrained intents: check a policy, get a quote, ask an appetite question, request a document, initiate a cancellation, or escalate to a human.

Ryan's observation report makes their nature vivid: "Independent retail agents and small agency principals communicate in shorthand ('comercial auto,' 'wc market for 8810 NOC,' 'flatt cancellation'). The AI responds with full declarative sentences, excessive acknowledgment phrases, and structured recaps that no human CSR at an MGA would write."

The screenshots from Ryan's report show real agents at work:

| Agent Name | Agency | Agency Code | What They Asked |
|------------|--------|-------------|-----------------|
| Caiman Insurance | iRate Insurance Agency LLC dba Caiman Insurance | #7406 | Commercial auto delivery coverage, $1M limit |
| Katia Cobas Friman | Cuban Family Insurance LLC dba Sebanda Insurance | #7361 | Mobile home quote |
| Clara Prego | Total Insurance Systems, Inc. | #7146 | Policy cancellation (policy#0185FL00184576-3) |
| Blue Star Insurance LLC | Blue Star Insurance LLC | #7241 | Policy lookup (REA1552956G), renewal information |
| Shakeena Jones | Acrisure Southeast Partners Insurance Services | #7782 | WC class code 8810 NOC for roofing admin office |
| Marlon Martinez | Golden Trust Insurance, Inc | #6941 | Plate glass coverage + GL for beauty salon |
| Marvin Soberanis | Florida Premier Insurance Agency LL | #7823 | WC quote status check |
| Maria Labrador | Golden Trust Insurance, Inc | #6941 | Policy cancellation (0185FL00210200-0) |

**Key pattern:** These are predominantly **South Florida agencies**, many serving Hispanic/Latino markets. Several agents communicate in Spanish or Spanglish ("comercial auto," "y ahora que hago?" — "now what do I do?"). The agencies range from small independent shops (Sebanda Insurance, Florida Premier) to national aggregators (Acrisure Southeast Partners).

### 2. How Agents Contact GIC Today

GIC operates **two parallel streams** that share the same retail agent population, as documented in Ryan's GIC interaction flow diagram:

**Stream A: CS / Servicing (episodic inquiries, AI-first)**
- Retail agents contact GIC via the **chat widget** (powered by Indemn's Fred AI) on the GIC broker portal
- The AI agent triages: handles simple queries (policy lookups, appetite questions, billing) or routes to a human CSR
- If unresolved by AI, a human CSR takes over the chat
- Human CSRs identified in the screenshots: **Tai-Siu De la Prida** and **Coralia Nunez**
- Volume: ~1,500 conversations/month (observatory data)

**Stream B: Placement / Underwriting (submission intake and quoting via email)**
- Retail agents email submissions to **quote@gicunderwriters.com**
- Submissions arrive as emails with ACORD forms, applications, prose descriptions, or via the GIC portal
- GIC staff (Maribel and others) manually process these: read the email, identify the LOB, extract data, check completeness, request missing info, and forward to carriers
- Volume: 3,214 emails over ~6 months

**Stream C: Voice (emerging)**
- Agents call GIC's main line, which routes through RingCentral
- JC has been actively pushing for call recording and transcription. In the March 20 email: "I wanted to follow up to see what is required to start recording calls to capture data for customer service. Can we only record calls that hit the customer service call queue?"
- Voice integration is a stated priority but not yet operational (RingCentral plan doesn't include transcription; JC is upgrading)

### 3. The Agent Experience Today — What's Painful

Ryan's 17 observations paint a detailed picture of friction points, corroborated by the observatory data:

**The chat experience is frustrating:**
- **44% of conversations end in failure** (missed handoffs, timeouts, abandonment, partial resolutions)
- Only **8% are resolved autonomously** by the AI
- **618 conversations (17%)** resulted in missed handoffs — the agent needed help and didn't get it
- Agents wait an average of **13 turns** per conversation — that's a lot of back-and-forth for a professional who knows exactly what they need

**The AI doesn't match the agents' register.** Ryan's Observation 2: "The current voice is transactional and over-formal relative to the audience." An agent types "comercial auto" and gets back a 47-word structured response that restates the input before answering. A human CSR would write: "Got it — what's the quote number for Statewide?"

**Slot-filling is painfully sequential.** Ryan's Observation 1: "The AI gathers one data point per turn — vehicle count, then state, then business name — when it could ask for all required inputs in a single, well-framed message." For a licensed producer who knows exactly what they need, one-question-per-turn is patronizing. This was traced to a root cause in the system prompt that explicitly instructs one-parameter-per-turn collection.

**The bot doesn't set expectations.** Ryan's Observation 10 (and the observatory data behind Opportunity 14): The AI spends 20+ turns collecting information for quotes it cannot generate, without ever telling the agent upfront. From actual transcripts: an agent provides 25+ turns of information, then the bot says "connecting you to live agent" and no one connects. Another provides everything and asks "y ahora que hago?" (now what do I do?).

**Policy lookups break on formatting.** Ryan's Observations 13-14: "policy#0185FL00184576 - 3" fails where "0185FL00184576" succeeds. The "-3" is a common endorsement/schedule suffix in commercial lines. The system fails to strip it. 15% of all API calls result in data failures.

**After-hours is invisible.** Ryan's Observation 11: The Katia Cobas Friman conversation shows the AI collecting information through a full intake flow, only surfacing the after-hours message at turn-end, after significant time investment with no actionable outcome. GIC hours are 8:30 AM - 5:00 PM ET, Monday-Friday.

### 4. Agent Submission Patterns (from Email Data)

The 3,214 emails in quote@gicunderwriters.com reveal how agents submit business:

**Email types (what agents send):**
- `agent_submission` (73): Direct email submissions with applications/ACORDs
- `agent_reply` (37): Responses to GIC's information requests
- `agent_followup` (10): Follow-ups on pending submissions
- `gic_application` (32): Applications through the GIC portal
- `renewal_request` (6): Renewal submissions

**How agents reference submissions:**
- USLI reference numbers in subject lines (51% of USLI emails follow the pattern "Quote [REF] for [INSURED] from [AGENT] at [AGENCY]")
- GIC 6-digit submission numbers (e.g., 143085, 143097, 143124)
- Named insured in subject line
- Info requests follow a highly consistent pattern: "Info Request for [INSURED_NAME]- [GIC_NUMBER]"

**Top submitting agencies (from email data):**
The email analytics reveal which agencies send the most volume. While specific agency names vary, the pattern is clear: a small number of agencies generate disproportionate volume, consistent with the 80/20 rule in wholesale distribution.

**Submission formats:**
- ACORD forms (standard industry forms)
- Prose emails describing the risk
- Portal applications (6 GIC portal submissions found, for Motorsports, Roofing, PestControl)
- PDF applications attached to emails
- Quote shopping emails (attaching competing carrier quotes for comparison)

### 5. How the Agent Relationship Works in Wholesale Brokerage

Ryan's wireframes encode a crucial business model distinction:

**GIC's relationship is with the retail agent, not the end customer.** In a wholesale brokerage:
- The **retail agent** is GIC's counterparty — the person they interact with
- The **end insured** (the business or individual being insured) is the retail agent's customer, not GIC's
- GIC never speaks directly to the end insured

This is why Ryan designed the wholesaler wireframes as **submission-first** (not customer-first like the retail agency wireframes):
- The Submission Queue organizes by risk/insured name, not by agent or customer
- The retail agent is visible metadata (useful for filtering and reporting) but not the primary organizing entity
- Status reflects the underwriting pipeline: Extracting, Missing Data, UW Review, Clarifying, Quoted, Bound

**The two-team structure inside GIC:**
1. **CS Team** (Tai-Siu De la Prida, Coralia Nunez, and others): Handles episodic inquiries from agents via chat and phone. AI-first with human backup.
2. **Placement Team** (Maribel and underwriters): Handles submission intake, data extraction, carrier coordination, and quoting via email.

Ryan's cross-team visibility flag in the wireframes addresses a real operational problem: when an agent asks about appetite via chat (CS stream) and also submits a risk via email (placement stream), neither team knows about the other's interaction. The wireframes propose awareness flags — not data sharing, just awareness — so the placement team sees that CS had contact about the same risk.

### 6. What Agents Want

Based on the observable patterns:

1. **Speed.** Every unnecessary turn, every verbose response, every sequential question wastes their time. They communicate in shorthand because they know the domain. They expect the same efficiency back.

2. **Transparency.** Tell them upfront what Fred can and cannot do. Don't collect 20 turns of data for a quote the bot can't generate. If it's after hours, say so immediately.

3. **Working policy lookups.** Agents routinely check policy status. When "policy#0185FL00184576 - 3" fails, they're not going to learn a new format — they'll just call the office instead.

4. **Appetite answers.** "Do you have WC market for 8810 NOC?" is a legitimate, answerable question. "No direct FAQ entry" is not an acceptable response.

5. **Submission status.** Agents want to know where their submissions stand in the pipeline. The Marvin Soberanis conversation shows an agent asking about a WC quote status — a common need.

---

## Open Questions

1. **What is the actual agency count?** We know agents have agency codes (4-digit numbers like #7406, #7146, etc.) but don't have a census of how many retail agencies work with GIC.

2. **What is the geographic distribution?** The screenshots suggest heavily South Florida, but is GIC placing business in other states?

3. **How do agents currently check submission status?** The chat bot doesn't have this capability. Do they call? Email? Check a portal?

4. **What is the agent onboarding process?** How does a new retail agency start working with GIC? What portal access do they get?

5. **Do agents have portal accounts?** The system prompt references a "GIC underwriters broker portal." What can agents actually do there today?

---

## Data Model Implications

For the email intelligence system:

1. **Retail Agent as an entity**: The system should track retail agents (name, agency, agency code, email) as a first-class entity. Multiple submissions from the same agent should be linkable.

2. **Agent lens for reporting**: Per Ryan's wireframes, the agent is not the primary organizing entity but IS useful for distribution analytics — which agencies send the most volume, which have the best conversion rates, which need the most follow-up.

3. **Multi-channel linkage**: An agent may chat about a risk (Stream A) and email a submission about the same risk (Stream B). The risk record should accrete interactions across channels.

4. **Shorthand recognition**: The classifier and extraction system must handle insurance shorthand (WC, GL, BOP, NOC, E&S, PL, etc.) — these agents don't write in complete sentences.

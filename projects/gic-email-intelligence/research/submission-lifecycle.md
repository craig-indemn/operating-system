# Submission Lifecycle at GIC Underwriters

**Methodology:** Read 30+ full email threads across all major LOBs, carriers, and stages. Compared the observed workflows against the system's 5-stage model. Examined edge cases including golf cart submissions, multi-carrier threads, internal coordination emails, and renewal cycles.

**Sources:** gic_email_intelligence MongoDB — emails (3,214), submissions (2,754), extractions (304). All submission stages, all attention reasons, all email types examined.

**Date Analyzed:** 2026-03-24

---

## 1. The REAL Lifecycle of a Submission

Reading the actual email threads reveals a lifecycle that is both simpler and more complex than the current 5-stage model suggests. Simpler because the vast majority of submissions follow a single automated path. More complex because the human-touched submissions involve multi-party negotiations that don't fit neatly into discrete stages.

### The Two Lifecycles

There are fundamentally **two different lifecycles** operating in GIC's business:

**Lifecycle A: Carrier-Automated (95% of volume)**

```
Agent uses USLI Retail Web → USLI auto-quotes → Notification arrives at GIC → Done
```

This lifecycle has no meaningful stages from GIC's perspective. The submission arrives pre-quoted. GIC's role is passthrough — they receive the notification, the agent already has the quote through USLI's portal. GIC tracks it for commission purposes but does not actively process it.

**Lifecycle B: Human-Processed (5% of volume, but 90% of GIC's actual work)**

```
Submission arrives → GIC triages → [Missing info? Request it] → [Need carrier review? Submit to carrier] → Carrier responds → GIC delivers to agent → [Agent wants to bind? Route to bind@]
```

This lifecycle involves actual underwriting judgment, agent communication, carrier negotiation, and follow-up management. This is where GIC's value is created and where an AI agent can have the most impact.

---

## 2. The Current 5-Stage Model: What's Accurate vs. Wrong

### Current Model

| Stage | Count | % |
|-------|-------|---|
| new | 53 | 1.9% |
| awaiting_info | 32 | 1.2% |
| with_carrier | 1 | 0.04% |
| quoted | 2,347 | 85.2% |
| attention | 321 | 11.7% |

### Assessment

**"quoted" — Accurate but misleading.** 85% of submissions land here correctly. However, "quoted" conflates two very different states:
- **Auto-quoted by USLI** (vast majority): GIC had no involvement. The quote exists in USLI's system and was delivered directly to the agent. GIC received a notification copy.
- **Quoted after GIC processing**: GIC received an agent submission, submitted it to a carrier, got terms back, and delivered the quote. This is genuinely different work.

An AI system cannot distinguish these without understanding the email history. The stage alone is insufficient.

**"new" — Accurate for portal submissions; wrong for some others.** The 53 "new" submissions include:
- Recent portal submissions (Golf Cart, Roofing, Pest Control) that genuinely haven't been processed yet
- The APR INV Holdings thread (5 internal GIC emails) that is still marked "new" despite significant internal discussion about a USLI quote
- Agent submissions that arrived but may have already been processed through a carrier's portal without email evidence

**"awaiting_info" — Partially accurate.** The 32 awaiting_info submissions correctly identify cases where GIC sent an info request. But the stage doesn't capture:
- Whether the agent has already replied (Arenal Property Management agent replied 2 days ago, still "awaiting_info")
- Whether GIC has processed the reply but not updated the stage
- Whether the info request was sent to the agent or to a carrier

The Golf Cart submissions were set to "awaiting_info" by the AI system (not by GIC staff) because the AI "identified missing golf cart info — VIN, DL, storage, registration." This is a different kind of awaiting_info — it's AI-identified missing data, not a human-sent info request.

**"with_carrier" — Theoretically correct, barely used.** Only 1 submission is in this stage (Deep Breath Holdings, Boat/Marine). The stage was set manually ("Approved for quoting by underwriter"). In reality, many submissions are "with carrier" at various points — every USLI Retail Web Submit is with USLI, every pending file is with USLI. The stage is underused because the automated carrier flow doesn't generate an explicit "submitted to carrier" event.

**"attention" — Useful but coarse.** 321 submissions, split between:
- "declined" (151): USLI declined the submission. This is a real outcome that needs GIC action (remarket? notify agent?)
- "carrier_pending" (170): USLI has the submission under review. This correctly identifies submissions that need monitoring but conflates different waiting states.

The attention stage doesn't distinguish:
- "Declined, needs remarketing" vs. "Declined, agent notified, closed"
- "Pending with USLI, expected auto-resolution" vs. "Pending with USLI, USLI is waiting for info from GIC"

---

## 3. How the Lifecycle Differs by LOB, Carrier, and Channel

### By LOB

**Personal Liability / Excess Personal Liability (899 combined):**
Almost entirely auto-quoted through USLI Retail Web. Submissions arrive with quote already issued. GIC receives notification copy. Lifecycle: new → quoted (instant). No human processing needed.

**General Liability (512):**
Mostly auto-quoted, but a meaningful subset involves GIC-originated applications submitted to USLI for underwriter review. Some get "pending file" treatment requiring info relay. Some get declined and need remarketing.

**Special Events (218):**
Similar to General Liability. USLI handles most automatically. Occasional declines (like "Worship of the Rock" where the event type triggered a decline, then partial quote).

**Non Profit (151):**
Higher rate of multi-email threads. Churches are common applicants ("Iglesia Esperanza y Adoracion", "Iglesia Cristiana El Refugio", "Ministerio Impacto con Dios"). These sometimes get quoted multiple times as USLI adjusts terms over days. Property component sometimes declined separately from liability.

**Commercial Package / Multi-Class Package (207 combined):**
More complex. Multiple coverage lines (GL + property + inland marine) mean partial declines are common. USLI may quote liability but decline property, requiring GIC to find alternative property coverage.

**Golf Cart / Motorsports (4):**
New LOB for GIC with a different workflow. Portal submissions come through with structured application data. The extraction pipeline successfully parsed VIN, driver license, storage type, and registration status. However, the agent email submission (Susana Avila) showed a name mismatch between the ID and the quote form, requiring human review.

**Trucking / Commercial Auto (18 combined):**
Different carrier path. GIC's Transportation Division (Julissa Arriola) handles these directly. Quote deliveries go to bind@gicunderwriters.com. Motor Truck Cargo uses Granada Insurance's portal for submissions.

**Homeowners / Rental Dwelling (20 combined):**
Involves carriers beyond USLI (Swyfft for homeowners). Info requests focus on Florida-specific items: Wind Mitigation inspections, 4-Point inspections, hurricane deductible options. Higher agent follow-up rate.

**Builders Risk (40):**
Higher decline rate. "Construction has already started" is a common USLI decline reason. GIC receives remarket suggestions from USLI.

### By Carrier

**USLI (2,623 submissions — 95%):**
Dominates. Highly automated. USLI's Retail Web system handles most quoting. GIC receives notification copies. When USLI needs more info, they email GIC staff directly (not the quote@ inbox), and GIC relays to agents. USLI provides three document versions with every quote (Customer, Retailer, Applicant).

**Hiscox (19 submissions):**
Fully automated quote delivery via email. Hiscox emails are self-contained — they include premium, coverage details, payment options, and a portal link for binding. No human underwriter communication observed. GIC's role appears to be agent-of-record only.

**GIC Underwriters direct (4 submissions — Golf Carts):**
GIC is the actual carrier for Motorsports/Golf Cart. No intermediary. Submissions come through GIC's own portal, and GIC must underwrite and rate the risk internally.

**Others (Swyfft, AmTrust, Mid Continent Casualty):**
Appear in edge cases. Swyfft for homeowners (support ticket format via Zendesk). AmTrust for workers comp (approval referrals). Mid Continent Casualty for motor truck cargo.

### By Channel

**USLI Retail Web (dominant):**
Agent fills out application on USLI's portal. USLI auto-quotes if eligible. GIC receives email notification. Agent gets quote directly from USLI. GIC's involvement: zero.

**GIC Portal (noreply@gicunderwriters.com):**
Used for LOBs where GIC is the carrier or has a direct-write program (Motorsports, HandyPerson, Roofing, Pest Control, Rental Dwelling). Generates a structured PDF application. GIC must process these manually — there is no carrier auto-quote.

**Granada Portal (quotes@granadainsurance.com):**
Used for personal auto and some artisan/service industries. Generates application PDFs. Some test submissions observed ("test mukul"), suggesting active system development.

**Direct Agent Email (to quote@ or quotes@):**
Most variable. Some agents send complete ACORD packages. Others send one-word emails with attachments. Some send bind requests, renewal requests, follow-ups, or even requests for information about carrier portals (Daymara Hernandez asking for AmTrust email to set up an account).

---

## 4. What the Lifecycle Should Actually Look Like

Based on reading the actual emails, here is a more accurate lifecycle model:

### Proposed 8-Stage Model

```
received → triaging → [awaiting_agent_info | awaiting_carrier_action | processing] → quoted → [delivered | declined | remarketing] → closed
```

| Stage | Description | Who Acts |
|-------|-------------|----------|
| **received** | Email arrived at quote@, not yet reviewed | Nobody (queue) |
| **triaging** | GIC staff is reviewing to determine next action | GIC underwriter |
| **awaiting_agent_info** | GIC sent info request to agent, waiting for reply | Agent |
| **awaiting_carrier_action** | Submitted to carrier, waiting for quote/decline/pending | Carrier |
| **processing** | All info received, GIC is actively working on it | GIC underwriter |
| **quoted** | Quote issued and delivered to agent | Agent (deciding) |
| **declined** | Carrier declined, GIC may need to remarket | GIC or agent |
| **remarketing** | GIC is seeking alternative carrier placement | GIC underwriter |
| **closed** | Final disposition — bound, expired, agent withdrew | Done |

### Key Differences from Current Model

1. **"new" becomes "received" and "triaging"** — distinguishing unread from being-worked-on.
2. **"awaiting_info" splits into two** — waiting on agent (common) vs. waiting on carrier (different urgency and follow-up cadence).
3. **"with_carrier" becomes "awaiting_carrier_action"** — explicitly marks what GIC is waiting for.
4. **"attention" is eliminated** — it was a catch-all. The actual states are "declined" (needs remarketing decision) and "carrier pending" (needs monitoring). These are now explicit stages.
5. **"quoted" stays but adds "delivered"** — distinguishing "carrier issued quote" from "agent received quote."
6. **"declined" and "remarketing" are explicit stages** — the most actionable situations for GIC staff.
7. **"closed" captures final disposition** — missing from current model entirely.

### Why This Matters for AI

An AI agent needs to know not just "what stage is this in?" but "who needs to do what next?" The current model says "attention" for 321 submissions. The proposed model would say:
- 151 are "declined — needs remarketing decision"
- 170 are "awaiting_carrier_action — USLI reviewing"

These require completely different actions. The AI agent for the first set should be checking alternative carriers and preparing remarket submissions. For the second set, it should be monitoring USLI's timeline and following up if it takes too long.

---

## 5. Concrete Examples at Each Stage

### Received (Unprocessed)
**Catherine Escalona (Golf Cart, #143097):** Portal submission arrived 2026-03-12. Single email with PDF application. VIN, address, and driver info extracted. No GIC action taken. The AI system set it to "awaiting_info" because it detected missing data, but GIC staff hasn't touched it.

### Awaiting Agent Info
**Arenal Property Management LLC (#143009):** GIC sent info request for Wind Mitigation and 4-Point inspection. Agent replied with completed documents. Agent followed up 3 days later. GIC CSR noted "agent is waiting on the quote." Still stuck here despite agent having provided everything.

### Awaiting Carrier Action
**Deep Breath Holdings, Inc (#142811):** Marine application with hull value discrepancy ($25K purchase, $250K requested). GIC investigated, agent provided improvement documentation. GIC marked "Approved for quoting by underwriter" — submitted to carrier. Waiting for carrier terms.

### Processing
**Marlon Blanco Delgado (#142994):** GIC issued a physical damage quote. Agent noticed the name was wrong and asked for correction. GIC underwriter Maribel Rodriguez asked Julissa Arriola internally how to fix the name. Julissa responded "It needs to be submitted at binding time." The submission is being actively worked.

### Quoted (Auto)
**UPFLIP IN SOUTH FLORIDA, LLC (MCP025D10V2):** USLI auto-quoted a Multi-Class Package. 5 emails, all from USLI. GIC received notification copies. Quote is issued and likely already visible to the agent in USLI's Retail Web portal.

### Quoted (GIC-Processed)
**Saez Trucking LLC (#27712):** Motor Truck Cargo submission came through Granada portal. Agent had a system error preventing binding. GIC flagged the error. Agent confirmed it was corrected. This submission moved through GIC's hands before reaching a quotable state.

### Declined
**Lips by Katrin Inc (MGL026M27P7):** USLI declined. Frederick Robinson sent formal declination with memo. Agent had submitted through First Choice Insurance. GIC needs to decide: try another carrier? Notify agent? Do nothing?

### Attention/Carrier Pending
**BLAZE PILATES (MCP026F2AZ6):** USLI's Elizabeth Shults requested additional info. GIC relayed partial agent response. USLI said "We cannot proceed without answers to all of the requested information." Stuck in a three-way information gap.

### Renewal Cycle
**Unique Insurance Services DBA Sebanda Insurance (GL 1285563):** Policy expired 3/13/2026. GIC sent non-renewal warning. Agent replied "renew please." This is technically a new lifecycle starting from an existing policy.

---

## 6. Edge Cases and Unusual Patterns

### Same Submission, Quote + Decline
BIG ROCK GROUPS LLC received both a USLI quote AND a decline for the same policy number (MCP025D5620). The quote was issued 2025-12-02, then declined 2025-12-11, then a revised quote was issued the same day. This appears to be USLI initially quoting, then reviewing and declining a component (probably property), then re-quoting the remaining coverages.

### Portal Test Submissions
"test mukul" appeared as a portal submission from Granada Insurance for "Artisan & Service Industries." Test submissions are entering the production email inbox. The system should filter these.

### Workers Comp Routing Questions
Porro Insurance's Daymara Hernandez emailed quote@ asking "Could you please provide the email address for the Amtrust (Workers Compensation) department so I can create an account with them through your agency?" This isn't a submission — it's an onboarding/access question that landed in the quoting inbox.

### Bind Requests in the Quote Inbox
Agent Masiel Dip forwarded a USLI Retail Web Quote for BFC Consultant Inc with a "Bind Request.pdf" attachment. Bind requests should go to bind@gicunderwriters.com but agents don't always know this.

### Multi-Agency Involvement
The Saez Trucking thread involved three parties: Granada Quotes (portal system), German Portillo (Univista Insurance agent), and Sam Amador (Unisoft). The same submission arrived from two different sources, creating duplicate handling.

### Renewal Package Inaccessibility
Knight Insurance's Karen Mercado emailed twice requesting renewal documents for George Caro: "I am trying to download the renewal package for this policy, but the documents are not available. Can you please send me the renewal package? This is the second email requesting them." This suggests a portal access issue that drives agents to email.

### Approval Referrals
GIC's Claudia Inoa (Contract Binding, E&S) sent an "Approval Request" to AmTrust for Guilarte A/C Insulation LLC. The agent followed up through CSR, who forwarded to quote@. This shows that some submissions go through a carrier referral process where GIC must actively advocate for the account.

### The Jessica/Jeffrey Mismatch (Golf Cart)
Agent Susana Avila submitted a "QUOTE GOLF CART.pdf" for Jeffrey Cueto and a "Jessica ID.pdf" for Jessica Maria Herrero Garcia. The extraction correctly identified two different named insureds from the same email. The submission was linked to Jessica (since her ID was the identity document), but the actual quote request may be for Jeffrey. This requires human judgment — is this a joint application? A mistake? A renewal where the named insured changed?

---

## 7. Where the Current Stage Model Fails

### Failure 1: The "Quoted" Black Hole
2,347 submissions (85%) are in "quoted" with no further lifecycle tracking. The system cannot distinguish:
- Quotes the agent has seen and is considering
- Quotes the agent never received (USLI auto-quote that GIC didn't forward)
- Quotes that expired
- Quotes that were bound (bind request went to bind@gicunderwriters.com)
- Quotes that the agent placed with a different carrier

### Failure 2: No "Agent Replied" Trigger
When an agent replies to an info request, the submission should move from "awaiting_info" to a new state ("processing" or "info_received"). Currently, submissions stay in "awaiting_info" even after the agent provides everything. Arenal Property Management is a clear example — agent replied, followed up, CSR confirmed info was received, but the submission is still "awaiting_info."

### Failure 3: Attention is Binary
"attention" means "something happened that needs human review." But declined submissions and pending submissions need completely different actions. A decline needs remarketing analysis. A pending needs monitoring and possible follow-up with the carrier. Lumping them together means nothing gets properly prioritized.

### Failure 4: No Closure
There is no "closed" or "expired" stage. Old submissions accumulate in "quoted" or "attention" forever. This makes it impossible to distinguish active work from historical records.

### Failure 5: Missing the Internal Workflow
GIC's internal email chain (CSR forwards, underwriter discussions, approval requests) is invisible to the stage model. The APR INV Holdings submission has 5 internal emails but is still "new." The Marlon Blanco Delgado submission has active underwriter discussion but no stage reflects this.

---

## Open Questions

1. **What percentage of USLI auto-quotes result in binding?** Without bind@ inbox data, we cannot measure conversion.
2. **Does GIC manually deliver USLI quotes to agents?** Or does USLI's Retail Web system handle this directly? If agents already get the quote from USLI, GIC's notification email is just an audit trail.
3. **What is the typical time from submission to quote delivery for human-processed submissions?** The data suggests multi-day cycles but the sample is small.
4. **How many of the 321 "attention" submissions have actually been worked by GIC staff?** The stage was set by the AI system but there's no "resolved" tracking.
5. **What happens to declined submissions?** Is there a systematic remarketing process or does GIC just notify the agent?
6. **Why are golf cart submissions staying in "new"?** Is this a new product with no established processing workflow yet?

---

## Data Model Implications

1. **Split the lifecycle by automation level.** Auto-quoted submissions (USLI Retail Web) need a different stage model than human-processed submissions. Trying to fit both into one model creates the "quoted black hole."

2. **Add "info_received" as a stage trigger.** When an agent_reply email arrives for a submission in "awaiting_info", the stage should automatically advance to signal that GIC needs to act.

3. **Decompose "attention" into specific action states.** "declined" and "carrier_pending" are already tracked as attention_reasons — promote them to first-class stages.

4. **Track the ball holder.** At any point, someone is responsible for the next action: the agent (providing info), the carrier (issuing quote/decline), or GIC (processing, relaying, remarketing). The stage model should make this explicit.

5. **Add "closed" with resolution codes.** Bound, expired, withdrawn, remarketed-elsewhere, declined-no-alternative. Without closure, the queue grows forever.

6. **Separate auto-notified from actively-processed.** A submission where GIC received a USLI notification but took no action is fundamentally different from one where GIC staff requested info, received it, and submitted to a carrier. The data model should reflect this.

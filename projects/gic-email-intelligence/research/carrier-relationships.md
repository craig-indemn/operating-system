# Carrier Relationships — GIC Underwriters

## Methodology
Compiled from GIC Email Intelligence classified data (3,214 emails from quote@gicunderwriters.com), USLI reference prefix analysis (3,088 extracted references), Ryan's UX observations (policy lookups showing carrier names), email thread discussions between Kyle/JC/Craig, the GIC policy API architecture (operations_api integration), and Ryan's wireframes documenting carrier interaction patterns.

## Sources
- GIC Email Intelligence MongoDB: email type classification (14 types including usli_quote, usli_pending, usli_decline, hiscox_quote)
- USLI reference prefix analysis: 24 prefix patterns, 3,088 references
- Ryan's UX Observation Report: policy lookup responses showing carrier names
- GIC policy API: operations_api -> Granada Insurance external API
- Email threads: partnership discussions, policy API architecture
- Ryan's wireframes: carrier interaction flow in gic_wholesaler_diagram.html and indemn_placement_flows.html
- GIC agent research artifact: tool architecture, policy API service chain

## Date Analyzed
2026-03-24

---

## Findings

### 1. The Wholesale Brokerage Model

GIC Underwriters operates primarily as a **wholesale insurance broker** (also called an MGA — Managing General Agent). In this model:

- **Retail agents** bring insurance needs from their end customers
- **GIC** evaluates the risk, identifies appropriate carrier(s), submits to carrier(s), and returns quotes to the retail agent
- **Carriers** provide the actual insurance policy and assume the risk

GIC sits in the middle — they don't take on insurance risk themselves (with one notable exception: golf carts/motorsports). Their value is in market access, underwriting expertise, and operational efficiency. They know which carrier will write what risk, at what price, and they handle the submission paperwork.

Ryan's placement flow diagrams show this clearly: the wholesale MGA scenario has four lanes — Retail Agent, Voice/AI Triage, CS Team, and Placement Team — with the carrier interaction happening through the Placement Team via "API, email, or manual" submission.

### 2. USLI — The Dominant Carrier

**United States Liability Insurance Group (USLI)** is GIC's primary carrier by a massive margin. The email data tells the story:

| USLI Email Type | Count | % of All Emails |
|-----------------|-------|-----------------|
| usli_quote | 2,553 | 79% |
| usli_pending | 212 | 7% |
| usli_decline | 147 | 5% |
| **USLI Total** | **2,912** | **91%** |

**91% of all emails in the quote inbox involve USLI.** This is not a diversified carrier portfolio — USLI is the engine that drives GIC's brokerage business.

**What USLI writes for GIC:**

USLI handles virtually all of GIC's brokered lines. The USLI reference prefix system reveals 24 distinct product lines, including:
- Professional Liability (MPL — 784 references, largest)
- General Liability (MGL — 477 references)
- Excess Personal Liability (XPL — 308 references)
- Commercial Package (MCP — 283 references)
- Special Events (MSE — 281 references)
- Commercial Property (NPP — 211 references)
- Specified Professions (SP — 84 references)
- Contractors Equipment (CEQ — 84 references)
- Artisan/Handy (MAH — 75 references)
- Personal Catastrophe (PCL — 71 references)
- Builders Risk (BRK — 53 references)
- Inland Marine (INM — 27 references)
- And 12 more specialty lines

**How the USLI relationship works:**

1. **Submission:** GIC submits to USLI via email or USLI portal (the email data shows submissions leaving quote@gicunderwriters.com)
2. **Response:** USLI responds via email to quote@gicunderwriters.com with one of three outcomes:
   - **Quote** (usli_quote): Subject line follows pattern "Quote [REF] for [INSURED] from [AGENT] at [AGENCY]"
   - **Pending** (usli_pending): Subject line "USLI Pending File [REF] for [INSURED]" — carrier needs more info
   - **Decline** (usli_decline): Subject line "USLI Retail Web Decline [REF] for [INSURED]"
3. **GIC forwards:** GIC staff reviews the carrier response and forwards it to the retail agent

**USLI email patterns are highly structured.** 99.7% of USLI quote emails contain the reference number in the subject line, and the subject line formats are consistent enough to parse programmatically. This is the strongest signal in the email data — USLI reference numbers are deterministic identifiers that encode carrier, LOB (via prefix), and submission identity.

**USLI as shown in policy lookups:**

Ryan's observation A-8/A-9 shows a policy lookup for REA1552956G (Yany Realty, LLC):
- Carrier: United States Liability Insurance Company (USLI)
- Line of Business: Professional Liability
- Premium: $1,329
- Status: ACTIVE

This confirms that USLI policies are accessible through GIC's policy API (the Granada Insurance external API).

### 3. Hiscox — Secondary Carrier

**Hiscox** appears as a secondary carrier in the email data:

| Hiscox Email Type | Count |
|-------------------|-------|
| hiscox_quote | 24 |

**24 Hiscox quote emails** were identified. This is a small fraction compared to USLI's 2,912, but Hiscox is significant enough to be a named carrier in the GL LOB configuration:

```
GL LOB Config — Carriers: USLI + Hiscox
```

Hiscox is a well-known specialty insurer that writes small commercial risks — GL, professional liability, cyber liability, and technology E&O. Their presence in GIC's carrier mix suggests GIC uses Hiscox as an alternative market for risks that don't fit USLI's appetite, or to provide competitive quotes.

**What we don't know about Hiscox:**
- Which specific LOBs does GIC place with Hiscox?
- What are the Hiscox email patterns? (Unlike USLI, the subject line patterns aren't documented)
- Does Hiscox have a portal or API that GIC uses?
- What is the Hiscox reference number format?

### 4. Granada Insurance / GIC as Carrier

This is the most architecturally interesting carrier relationship because **GIC is the carrier.**

**Granada Insurance Company** is the parent company of GIC Underwriters. Key evidence:

- **Mukul Gupta's email signature:** "mgupta@granadainsurance.com, Granada Insurance Company, 4075 SW 83rd Ave, Miami, FL 33155"
- **Policy API service chain:** Fred (bot-service) calls operations_api, which calls the **Granada Insurance external API** at `https://services-uat.granadainsurance.com`
- **Policy cancellation conversations:** Maria Labrador's policy for MIA FAJAS BOUTIQUE, CORP was "currently active with Granada Insurance" (Ryan's Observation A-14)
- **Policy format:** Granada Insurance policies follow the pattern `0185FL00XXXXXX` (where 0185 appears to be a carrier/state code and FL indicates Florida)

**What GIC underwrites directly:**

The clearest example is **Golf Cart / Motorsports:**
- Golf Cart LOB config lists carrier as "GIC Underwriters" (not USLI or Hiscox)
- JC specifically identified golf carts as a priority because GIC underwrites them directly
- The Motorsports portal is GIC's own portal for collecting structured applications
- Demo strategy artifact: "Golf carts are ideal for full automation because GIC is the carrier (not brokering to USLI) — simpler workflow, full control"

**The dual identity:**
- **GIC Underwriters** = the wholesale brokerage that places business with carriers
- **Granada Insurance** = the admitted carrier that actually issues policies for certain lines
- They share infrastructure: the policy API, the management system, the staff

This creates a unique opportunity: for lines where GIC/Granada is the carrier, the entire workflow from submission to quote to bind can potentially be automated without any external carrier API dependency.

### 5. How Carrier Interactions Work

Ryan's wireframes and the email data document the carrier interaction lifecycle:

**Brokered lines (USLI, Hiscox, others):**

```
Agent emails submission to quote@gicunderwriters.com
    ↓
GIC extracts data, checks completeness, validates appetite
    ↓
GIC submits to carrier (email, portal, or API)
    ↓
Carrier responds: Quote / Pending (needs info) / Decline
    ↓
If Pending: GIC drafts info request → agent → GIC → carrier
If Quote: GIC forwards quote to agent
If Decline: GIC notifies agent, may try alternative carrier
    ↓
Agent presents to end customer
    ↓
If accepted: Bind instruction from agent → GIC → carrier
    ↓
Policy issued
```

**Ryan's wireframe stage vocabulary for the carrier lifecycle:**
- **Extracting** — Indemn/GIC is parsing the submission
- **Missing Data** — Information gaps identified, waiting for agent
- **UW Review** — Underwriter human review needed (e.g., appetite borderline)
- **Clarifying** — Back-and-forth with agent on specifics
- **Quoted** — Carrier returned a quote
- **Bound** — Policy issued

**Direct-underwritten lines (Golf Cart / Motorsports):**

```
Agent emails submission or uses Motorsports portal
    ↓
GIC extracts data, checks completeness
    ↓
GIC UW reviews directly (no external carrier submission)
    ↓
GIC issues quote or declines
    ↓
If accepted: GIC/Granada binds directly
    ↓
Granada Insurance policy issued
```

The key difference: no external carrier intermediary. The UW review step (shown in Ryan's Risk Record wireframe with "Approve for quoting / Refer to senior UW / Decline" buttons) replaces the carrier submission step.

### 6. Other Carriers (Inferred)

Beyond USLI, Hiscox, and Granada/GIC, the email data suggests other carriers exist in GIC's network but aren't yet well-characterized:

**Evidence of additional carriers:**
- The USLI reference data includes 1,526 references with "Other formats" (not USLI patterns) — these may include reference numbers from other carriers
- Ryan's Observation 13 notes: "GIC writes through a defined set of admitted and E&S carriers" — suggesting multiple carrier options
- The policy lookup tool describes policies with various carriers (USLI confirmed, Granada confirmed)
- Commercial auto (discussed in the Caiman Insurance conversation) has a $500K delivery max — this constraint is carrier-specific, not GIC-wide

**Likely additional carriers (not confirmed in data):**
- Workers Compensation carriers — WC is frequently discussed but no WC reference numbers with USLI prefixes were found, suggesting a different carrier handles WC
- Commercial Auto carriers — the $500K delivery limit is a specific product constraint
- Homeowners carriers — HOP prefix exists in USLI data but only 4 references

### 7. The Policy API — Technical Carrier Integration

The one carrier API integration that exists today connects to Granada Insurance:

**Service chain:**
```
Fred (chatbot) → operations_api → Granada Insurance API
                                  (services-uat.granadainsurance.com)
```

**Technical details:**
- Endpoint: `GET /v1/insuredpolicy/details?agencyCode={code}&policyNumber={number}`
- Auth: OAuth token via `POST /v1/token/generate` (Basic Auth)
- Token caching in Redis with TTL from API response
- Auto-refresh on 401, exponential backoff on 500 errors
- SSL: `rejectUnauthorized: false` (UAT uses self-signed cert)

**What the API returns (from A-8 screenshot):**
- Insured Name
- Effective Date
- Status (ACTIVE)
- Line of Business
- Agency name
- Carrier (United States Liability Insurance Company)
- Premium
- Total Balance
- Auto Pay enrollment status

**Notable:** The API is hosted at Granada Insurance's domain (`granadainsurance.com`), which means Granada's management system holds policy data for both Granada-underwritten policies AND USLI-brokered policies. This makes sense — as the MGA, GIC/Granada maintains the policy records even when USLI is the risk-bearing carrier.

**Management system:** The email threads reference "Jeremiah" as the contact for management system API access. Kyle wrote to JC: "The biggest unlock on our side is getting connected to Jeremiah for the management system APIs." The management system appears to be an internal GIC/Granada system (possibly called "Unisoft" based on the technical design document mentioning "Unisoft integration would automate" the With Carrier stage).

---

## Open Questions

1. **What is the full carrier panel?** Beyond USLI, Hiscox, and Granada, which carriers does GIC place business with? Are there specific carriers for WC, commercial auto, or homeowners?

2. **Does GIC have API access to any carrier systems?** The only confirmed API is the Granada Insurance policy API. Do they have USLI portal API access? Hiscox API access?

3. **What is the relationship between GIC Underwriters and Granada Insurance Company legally?** Is GIC a subsidiary? A DBA? An MGA with binding authority?

4. **What does the management system (Unisoft?) track?** The policy API returns rich data — does the management system also track submission status, carrier correspondence, and agency relationships?

5. **How does carrier selection work?** When a GL submission comes in, how does GIC decide whether to send it to USLI, Hiscox, or both? Is this rule-based or judgment-based?

6. **What are the carrier portals?** Ryan's wireframes show "API, email, portal" as carrier submission methods. Which carriers have portals that GIC staff log into manually?

7. **What is the USLI contract structure?** Is GIC a USLI program administrator? Do they have binding authority for certain lines?

---

## Data Model Implications

1. **Carrier as a first-class entity**: The system should track carriers with: name, submission method (API/email/portal), response email patterns, reference number format, supported LOBs, and appetite rules.

2. **USLI email classification is highly reliable**: The 14 email types include carrier-specific types (usli_quote, usli_pending, usli_decline, hiscox_quote). USLI email patterns are so consistent they can be parsed programmatically.

3. **Carrier-specific stage tracking**: The lifecycle stages differ slightly by carrier. USLI has a clear Quote/Pending/Decline trichotomy. Direct-underwritten lines (golf carts) have a UW Review stage instead of a carrier submission stage.

4. **The Granada API is the source of truth for policy data**: Any policy lookup — regardless of the risk-bearing carrier — goes through the Granada Insurance API. This means the system doesn't need per-carrier API integrations for policy lookups.

5. **Carrier reference numbers are submission identifiers**: A USLI reference like MGL026F9DR4 uniquely identifies a submission. The system already uses these for multi-email linking. Carrier reference numbers should be first-class identifiers alongside GIC submission numbers.

6. **Two carrier interaction models**: (a) Brokered: submission → carrier response → forwarding. (b) Direct: submission → internal UW review → quote/decline. The system needs to support both paths, with the LOB configuration determining which model applies.

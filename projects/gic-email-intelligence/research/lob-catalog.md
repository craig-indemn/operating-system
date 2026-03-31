# LOB Catalog — Lines of Business at GIC Underwriters

## Methodology
Compiled from GIC Email Intelligence classified data (3,214 emails, 39 canonical LOBs), USLI reference prefix analysis (3,088 extracted references with deterministic LOB mapping), Ryan's UX observations (14 conversations mentioning specific LOBs), email thread discussions between Kyle/JC, GIC portal submission data, and the golf cart LOB configuration built from Motorsports portal applications.

## Sources
- GIC Email Intelligence MongoDB: 3,104 classified emails by LOB + 110 unclassified
- USLI reference prefix LOB mapping: 24 prefix patterns across 3,088 references
- Ryan's UX Observation Report: LOBs mentioned in 14 real conversations
- Golf cart LOB config: src/gic_email_intel/agent/lob_configs/golf_cart.json
- GL LOB config: src/gic_email_intel/agent/lob_configs/gl.json
- Email threads: Kyle/JC discussing product priorities, portal submissions
- Demo strategy artifact: LOB reclassification analysis

## Date Analyzed
2026-03-24

---

## Findings

### 1. LOB Distribution Overview

GIC handles a remarkably broad range of commercial and personal lines through their wholesale brokerage operation. The email data reveals 39 canonical LOBs after normalization, with significant concentration in a few high-volume categories.

**Top LOBs by email volume (from MongoDB classification):**

| LOB | Email Count | % of Total | Primary Carrier | Notes |
|-----|-------------|------------|-----------------|-------|
| Personal Liability | 725 | 23% | USLI | Highest volume by far |
| General Liability | 574 | 18% | USLI, Hiscox | Core commercial line |
| Special Events | 245 | 8% | USLI | Event GL coverage |
| Non Profit | 219 | 7% | USLI | Nonprofit D&O and GL |
| Excess Personal Liability | 217 | 7% | USLI | Personal umbrella |
| Commercial Package | 205 | 7% | USLI | GL + Property bundled |
| Commercial Property | 200 | 6% | USLI | Standalone property |
| Professional Liability | 86 | 3% | USLI | E&O, professional services |
| Excess Liability | 78 | 3% | USLI | Commercial umbrella |
| Allied Healthcare | 76 | 2% | USLI | Medical-adjacent |
| Contractors Equipment | 71 | 2% | USLI | Inland marine for contractors |
| Umbrella | 46 | 1.5% | USLI | Umbrella policies |
| Multi-Class Package | 44 | 1.4% | USLI | Complex package policies |
| Builders Risk | 42 | 1.4% | USLI | Construction-period coverage |
| Specified Professions | 40 | 1.3% | USLI | Niche professional categories |
| Inland Marine | 33 | 1.1% | USLI | Equipment/property in transit |
| Medical Professional | 27 | 0.9% | USLI | Medical malpractice |
| + 22 more LOBs | ~100 | ~3% | Various | Long tail of specialty lines |
| **Total classified** | **3,104** | | | |
| Unclassified | 110 | 3.5% | — | 49 unclassified + 61 edge cases |

### 2. USLI Reference Prefix LOB Mapping

USLI (United States Liability Insurance Group) is GIC's dominant carrier. The USLI reference numbers encode the LOB deterministically via a prefix. This is the most reliable LOB indicator in the email data:

| Prefix | LOB | Email Count | What It Covers |
|--------|-----|-------------|----------------|
| MPL | Professional Liability | 784 | E&O, professional services liability |
| MGL | General Liability | 477 | Commercial GL, premises, operations |
| XPL | Excess Personal Liability | 308 | Personal catastrophe/umbrella |
| MCP | Commercial Package | 283 | GL + Property bundled |
| MSE | Special Events | 281 | Event liability, special event coverage |
| NPP | Commercial Property | 211 | Standalone commercial property |
| SP | Specified Professions | 84 | Niche professional categories |
| CEQ | Contractors Equipment | 84 | Inland marine for contractor tools |
| MAH | Artisan/Handy | 75 | Artisan contractors, handyman |
| PCL | Personal Catastrophe | 71 | Personal umbrella/excess |
| BRK | Builders Risk | 53 | Course of construction coverage |
| INM | Inland Marine | 27 | Equipment, property in transit |
| PM | Property Manager | 23 | Property management liability |
| MHB | Home Business | 22 | Home-based business coverage |
| MPR | Property | 19 | Property (variant) |
| MDP | Dwelling Property | 18 | Dwelling fire/property |
| REA | Real Estate | 17 | Real estate E&O |
| XSL | Excess Surplus Lines | 15 | Excess/surplus coverage |
| EPL | Employment Practices | 12 | Employment practices liability |
| STK | GL (variant) | 9 | GL variant |
| NDO | Non Profit D&O | 8 | Nonprofit directors & officers |
| CUP | Contractors Umbrella | 7 | Umbrella for contractors |
| MLQ | Liquor Liability | 5 | Liquor liability coverage |
| HOP | Homeowners | 4 | Homeowners coverage |

### 3. LOBs Mentioned in Agent Conversations (Ryan's Observations)

The chat conversations reveal what agents actually ask about:

| LOB Mentioned | Context | Screenshot |
|---------------|---------|------------|
| **Commercial Auto** | Caiman Insurance asked about commercial auto delivery coverage, 3 vehicles in FL, $1M limit. Human CSR (Tai-Siu) revealed the system max is $500K for delivery. | A-1, A-2, A-3 |
| **Mobile Home** | Katia Cobas Friman asked for a mobile home quote, 8831 Edgewood Blvd, Tampa FL, built 1986. | A-4, A-5, A-6 |
| **Workers Compensation** | Shakeena Jones asked about WC market for class code 8810 NOC (clerical office employees) for a roofing company admin office. Marvin Soberanis asked for WC quote status. | A-10, A-13 |
| **Professional Liability** | Blue Star Insurance looked up policy REA1552956G — Professional Liability for Yany Realty, LLC via USLI. | A-8, A-9 |
| **General Liability** | Multiple conversations. Marlon Martinez asked about GL + Plate Glass Coverage for a beauty salon. | A-11, A-12 |
| **Plate Glass Coverage** | Marlon Martinez specifically asked about standalone plate glass coverage. | A-11, A-12 |
| **Policy Cancellation** | Clara Prego and Maria Labrador both requested policy cancellations (Granada Insurance policies). | A-7, A-14 |

### 4. Golf Cart / Motorsports — JC's Priority LOB (Detailed)

Golf carts represent GIC's most significant near-term automation opportunity. This is the one LOB where **GIC acts as the carrier** (not just the broker), which means simpler workflow, full control, and the clearest path to end-to-end automation.

**Why golf carts matter:**
- JC specifically requested golf carts as the starting LOB
- South Florida has a large and growing golf cart insurance market
- As a new product line, there's no legacy process to disrupt
- GIC underwrites directly (doesn't broker to another carrier)

**What we found in the email data:**
- The original email classifier had a hardcoded LOB list that didn't include "Golf Cart" or "Motorsports"
- 3 Motorsports portal submissions were misclassified as "Trucking"
- 1 direct agent golf cart submission was misclassified as "Inland Marine"
- After reclassification: **4 golf cart submissions identified**

**The four golf cart submissions:**

| Insured | Source | Retail Agent / Agency | GIC# | Status |
|---------|--------|-----------------------|------|--------|
| William Wacaster | Motorsports portal | Brian Sandhaus / B & B Insurance | 143085 | Portal collected full app. System incorrectly generated info request for data already in the PDF. |
| Catherine Escalona | Motorsports portal | Ignacio Perez / John Sena Agency | 143097 | Same — portal app is complete. |
| Osvaldo Lopez | Motorsports portal | Daniel Herrera / Univista | 143124 | Same — portal app is complete. |
| Jessica Maria Herrero Garcia | Direct agent email | Susana Avila / Univista | none | **Misidentified.** Attached PDF is actually an American Modern quote for Jeffrey Cueto, not a new GIC application. Quote shopping scenario. |

**Golf Cart LOB configuration (built for the system):**
Required fields derived from the Motorsports portal application:
- Applicant: name, address, homeowner status
- Vehicle: year, make, VIN
- Driver: name, DOB, gender, driving record
- Coverage: liability limits, UM/UIM
- Storage: type (garage, driveway, carport)
- Registration: street-legal vs. private property only
- Purchase date

**The GIC Motorsports portal:**
GIC has a dedicated portal for Motorsports submissions (golf carts, ATVs, etc.). The portal collects structured application data and generates a PDF. Six portal submissions were found in the email data (Motorsports, Roofing, PestControl), indicating GIC uses product-specific portals for some LOBs.

**Automation path for golf carts:**
1. **Today (demo):** Email intelligence — understand the inbox, extract data, identify gaps, draft info requests
2. **Next (release):** Operational tool — Maribel uses it daily for golf cart submissions
3. **Target:** Full quote-and-bind automation. Retail agent submits via portal or email, system extracts, validates, quotes, binds. No human in the loop. This follows the EventGuard model (Indemn's existing event insurance automation).

### 5. Which LOBs GIC Specializes In vs. Pass-Through

Based on the data, GIC's LOBs fall into three tiers:

**Tier 1 — High-volume brokerage (USLI as primary carrier):**
- Personal Liability (725 emails)
- General Liability (574 emails)
- Special Events (245 emails)
- Non Profit (219 emails)
- Excess Personal Liability (217 emails)
- Commercial Package (205 emails)
- Commercial Property (200 emails)

These are GIC's bread and butter — high-volume lines placed primarily through USLI. The workflow is well-established: agent submits, GIC extracts data, submits to USLI, USLI responds with quote/pending/decline, GIC forwards to agent.

**Tier 2 — Specialty brokerage (USLI + Hiscox + others):**
- Professional Liability (86 emails, USLI)
- Excess Liability (78 emails)
- Allied Healthcare (76 emails)
- Contractors Equipment (71 emails)
- Workers Compensation (frequently asked about in chat, KB has class code data)
- Builders Risk (42 emails)

These require more underwriting judgment and may involve multiple carrier options.

**Tier 3 — GIC as carrier (direct underwriting):**
- **Golf Cart / Motorsports** — GIC underwrites directly, does not broker to another carrier
- Policy numbers for GIC-direct products follow Granada Insurance formats (0185FL00XXXXXX)

**Tier 4 — Emerging / specialty:**
- Mobile Home (asked about in chat)
- Plate Glass Coverage (asked about in chat)
- Loss Runs (Ryan's Observation 16: "Loss runs for commercial lines are typically fulfilled by the carrier, not the MGA — but the MGA often brokers the request. This consistently routes to email, suggesting no system integration with carrier loss run portals.")

### 6. LOB-Specific Workflow Differences

**USLI-brokered lines (Tier 1 & 2):**
- Submission via email to quote@gicunderwriters.com
- USLI returns quotes/pending/declines via email with reference numbers (deterministic LOB prefix)
- Subject lines follow consistent patterns: "Quote [REF] for [INSURED] from [AGENT] at [AGENCY]"
- Lifecycle: Received → Extracted → Submitted to Carrier → Quote/Pending/Decline
- Automation opportunity: Email classification, data extraction, gap analysis, draft replies

**Golf carts (Tier 3 — GIC as carrier):**
- Submission via Motorsports portal or direct agent email
- GIC makes the underwriting decision directly
- No carrier intermediary — shorter lifecycle
- Lifecycle: Received → Extracted → UW Review → Quote/Decline → Bind
- Automation opportunity: End-to-end quote-and-bind (the full EventGuard model)

**Workers Compensation:**
- Frequently asked about via chat (appetite questions, class code inquiries)
- Class code knowledge is a known gap — 8810 NOC inquiry got "no direct FAQ entry"
- KB has 140 class code entries and 59 class codes, but common codes like 8810 are missing
- WC appetite queries are a major chatbot use case that needs KB improvement

**Special Events:**
- High-volume USLI line (245 emails, MSE prefix)
- Similar to EventGuard (Indemn's event insurance product)
- Natural candidate for next-LOB automation after golf carts

---

## Open Questions

1. **What is GIC's full product catalog?** We know 39 LOBs from the email data, but is there an official catalog of lines GIC writes?

2. **Which LOBs does GIC underwrite directly vs. broker?** Golf carts are confirmed as direct. What else? Does "Granada Insurance" as carrier on some policies mean GIC is the direct carrier for those?

3. **What are the WC class code appetite rules?** The KB has some data but not enough. What class codes does GIC write, decline, or refer?

4. **What is the volume breakdown by LOB for the chat channel?** We have email LOB distribution but not chat intent distribution by LOB.

5. **Are there LOBs that GIC has recently started writing?** Golf cart/Motorsports appears to be new. Are there other emerging product lines?

6. **What is the premium volume by LOB?** Email count is a proxy for volume, but premium per submission varies dramatically across lines.

---

## Data Model Implications

1. **LOB as a first-class entity**: Each LOB should have a configuration record specifying: required fields, carrier options, workflow type (brokered vs. direct), typical cycle time, and appetite rules.

2. **Two LOB configs are built**: GL (10 fields, 2 docs, carriers: USLI + Hiscox) and Golf Cart (17 fields, 2 docs, carrier: GIC Underwriters). The remaining 37 LOBs use 8 generic required fields.

3. **USLI prefix mapping is deterministic**: For any email with a USLI reference number, the LOB can be derived from the prefix with 100% confidence. This is the most reliable classification signal in the data.

4. **Portal submissions are a distinct intake channel**: The GIC portal generates structured PDFs that contain all required data. These should NOT trigger info-request drafts (the current system incorrectly does this).

5. **LOB affects the workflow path**: Brokered LOBs go through carrier submission. Direct-underwritten LOBs (golf carts) go through UW review. The system needs to route differently based on LOB type.

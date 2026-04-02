# USLI GL (MGL) Automation Analysis

> Complete data analysis for automating USLI General Liability quote entry into Unisoft AMS.
> **Source of truth** for what data we have, what we don't, and what each field maps to.
> Last updated: 2026-04-01

---

## Scope

Automate the entry of USLI auto-quote emails for General Liability (prefix `MGL`) into Unisoft AMS. This is JC's #1 automation priority — "very repetitive and boxed up."

**Volume:** 107 MGL emails in MongoDB (from ~6 months of data), linked to 99 unique submissions. 310 PDF extractions across those emails.

---

## Data Sources Per Record

Each MGL USLI quote email produces three data sources in MongoDB:

1. **Email** (`emails` collection) — subject, from, body text, attachments, classification
2. **Submission** (`submissions` collection) — linked record with agent info extracted from email body
3. **Extraction** (`extractions` collection) — structured fields extracted from the attached USLI PDF

Each email arrives with **3 PDF attachments**: Customer copy, Retailer copy, Applicant copy. Our extractions are from whichever PDF was processed.

---

## Field-by-Field Mapping: What We Have → What Unisoft Needs

### Fields We Can Fill With Certainty

| Unisoft Field | Value/Source | How We Know | Confidence |
|---|---|---|---|
| **LOB** | `CG` | USLI prefix `MGL` = General Liability. Deterministic. | 100% |
| **Carrier** | CarrierNo `2` (USLI) | Every MGL email is from USLI. Hardcoded. | 100% |
| **Broker** | BrokerId `1` (GIC Underwriters) | GIC is always the broker. Hardcoded. | 100% |
| **Name** (insured) | Email classification `named_insured` field, also in subject line and body | Present in every email. Also in extraction. | 100% |
| **Reference Number** | Email classification `reference_numbers[0]`, starts with `MGL` | In subject line of every USLI email. 100% available. | 100% |
| **QuoteType** | `N` (New) | USLI auto-quotes are new business | 100% |
| **Status** | `1` (Open) | Standard for new entries | 100% |
| **IsNewSystem** | `true` | Standard for new entries | 100% |
| **Action** | `Insert` | Creating a new record | 100% |
| **OriginatingSystem** | `UIMS` | Standard value from Fiddler capture | 100% |
| **MGA** | MgaNo `1` (GIC Underwriters) | From Fiddler capture | 100% |

### Fields the LLM Agent Can Determine

| Unisoft Field | Source | LLM Reasoning Required | Notes |
|---|---|---|---|
| **SubLOB** | Extraction `classification_description` (21% of extractions) + coverage type + business description | Map classification to one of 4 CG sub-LOBs: AC (Artisans/Contractors), LL (Liquor Liability), HM (Non-Artisans), SE (Special Events). E.g., "Condominiums - residential" → HM. | Agent can also call `GetInsuranceSubLOBs` for the options. When classification_description unavailable, agent reads PDF context. |
| **AgentNumber** | Submission `retail_agency_name` matched against Unisoft `GetAgentsAndProspectsForLookup` | Fuzzy name matching. "SEBANDA INSURANCE CORP. (FRANCHISE)" → "Sebanda Insurance Corp" in Unisoft. | 72% of submissions have agency name from email body. Agent can call the lookup API and reason about the match. |
| **FormOfBusiness** | Pre-filled application checkbox (if extracted from Applicant PDF) OR insured name pattern | The USLI application has explicit checkboxes: Individual, Corporation, Partnership, LLC, Other. If we extract from the Applicant PDF, we get the exact entity type. If inferring from name: "...LLC" → LLC code (NOT "C"), "...Corp"/"...Inc" → C, individual name → I code. **Unisoft codes for LLC and Individual are NOT YET CONFIRMED.** |
| **Address, City, State, Zip** | Extraction `covered_location_address` (36% have this field) | Parse address string into components | When present, it's the insured property address. Not the agent's address. |
| **PolicyState** | Extraction `covered_location_address` → state, or default FL | Almost all GIC business is Florida | Can extract state from address. |
| **Premium** | Extraction `total_amount_due` (86%) or `base_premium` (39%) | Identify the right premium field | `total_amount_due` includes taxes/fees. `base_premium` is the carrier premium before surcharges. Need to determine which Unisoft expects. |
| **Term** | Extraction `policy_term` (73% — almost always "Annual") | "Annual" → 12 | If absent, default unknown — do not assume. |
| **BusinessDescription** | Extraction `classification_description` | Direct mapping | "Condominiums - residential - (Unit owner risk only) annual rental" |

### Fields We Do NOT Have — Verified Gaps

| Unisoft Field | Why We Don't Have It | Impact |
|---|---|---|
| **EffectiveDate** | **Use the current date** (the date the record is being created). Unisoft REQUIRES this field (BRConstraint). The USLI quote PDF does NOT contain a policy effective date — the "Please bind effective: ___" field is blank. **RESOLVED:** JC's walkthrough confirmed GIC uses the current date as the effective date when creating quote records. | Confirmed from JC walkthrough video (reviewed 2026-04-02). |
| **ExpirationDate** | **EffectiveDate + 1 year** (default for annual term). If Term=12, ExpirationDate = EffectiveDate + 12 months. | Confirmed from JC walkthrough — default is one year from effective date. |
| **AgentContactID** | The specific person at the agency. We have the contact name from the email body, but not their Unisoft contact ID. | Would need to call `GetContacts` for the matched agent and find the person. The LLM can do this lookup. |
| **AssignedTo** | Which GIC underwriter handles this. May depend on LOB, carrier, or internal routing rules. | Could default to a specific user or leave for manual assignment. Need to ask JC what the assignment logic is. |
| **Email** (insured) | The insured's email is not in USLI auto-quote emails. The agent's email is there but not the end customer's. | Not critical for quote creation, but GIC may want it. |

### Fields We Explicitly Skip (v1)

| Field | Why |
|---|---|
| Excess liability (XSL/CUP) | Only 5% of MGL emails include an excess quote. It's optional. Separate submission. Add in v2. |
| Previous Policy Information | Not available from USLI auto-quote emails. |
| Phone numbers | Not reliably in the data. |
| FEIN | Not in USLI auto-quote emails. |

---

## Unisoft Activity ActionIds — Complete Reference

Captured from `GetQuoteActions` API call. 73 total actions across 2 sections.

### Section 5: Quotes (quote-level activities)

| ActionId | Description | Use Case |
|---|---|---|
| 6 | Application received from agent | When creating a new quote from an agent submission |
| 9 | Request additional form/information | Sending info request to agent |
| 10 | Application withdrawn by agent | Agent withdraws |
| 66 | Agent of record requested | AOR change |
| 68 | Note | General note on quote |
| 70 | Close Quote - Declined | Close as declined |
| 78 | Agent of record received | AOR received |
| 85 | Close Quote - Inactivity / Expired | Close as expired |
| 89 | Quote follow-up | Follow up |
| 92 | Request to Bind acknowledgement to Agent | Bind ack |
| 96 | E&O application sent - New | E&O |
| 104 | Follow up on request additional form/information from agent | Info request follow-up |
| 106 | Automatic renewal uploaded | Renewal |
| 111 | Follow up - E & O application sent - New | E&O follow-up |
| 115 | Request additional information via phone | Phone info request |
| 116 | Renewal solicitation sent | Renewal |
| 117 | Normandy Renewal Offer | Normandy specific |
| 119 | Renewal Follow-up | Renewal follow-up |
| 121 | Endorsement Received From Agent | Endorsement |
| 129 | Binder request received from agent/Bound via portal | Bind |
| 138 | DECLINE | Decline |
| 178 | Close Quote | Close |
| 180 | Application Acknowledgement | Ack sent to agent |

### Section 3: Quotes>Submissions (submission-level activities)

| ActionId | Description | Use Case |
|---|---|---|
| 1 | Submit application to carrier | Core submission to carrier |
| 2 | Offer received from carrier | **USLI quote received** — use this for MGL automation |
| 3 | Application rejected by carrier | Carrier decline |
| 4 | Offer rejected by agent | Agent declines |
| 5 | Binder confirmation received from carrier | Bind confirmed |
| 11 | Binder request received from agent / Sent to carrier | Bind request |
| 67 | Send offer to agent | Forward quote to retail agent |
| 74 | Note | Submission note |
| 76 | Submit to carrier(s) - via portal | Portal submission |
| 82 | Starr/National General Binder Request Received from Agent | Carrier specific |
| 84 | Request additional form/information | Submission-level info request |
| 86 | BOR Request | Broker of record |
| 87 | Individual carrier declination | Single carrier decline |
| 88 | Submission follow-up | Follow-up |
| 93 | Quote not offered | No quote |
| 94 | TI renewal indication received | Renewal |
| 97 | Send Starr policy to agent | Carrier specific |
| 98 | Send policy to agent | Policy delivery |
| 99 | Send loss runs to carrier | Loss runs |
| 100 | Submit requested additional information to carrier | Additional info to carrier |
| 101 | Send offer follow up to agent | Quote follow-up |
| 103 | Bind request received from prospect or agent with missing documents | Incomplete bind |
| 105 | Bind request to carrier follow-up | Bind follow-up |
| 107 | Follow up on bind request sent to carrier | Bind follow-up |
| 120 | Renewal offer/application request from carrier | Renewal |
| 122 | Submit endorsement to carrier | Endorsement |
| 123 | Endorsement follow-up | Endorsement follow-up |
| 124 | Endorsement offer received from carrier | Endorsement received |
| 125 | Endorsement Quote Sent to Agent | Endorsement quote |
| 126 | Endorsement bind request received from agent/ sent to carrier | Endorsement bind |
| 127 | Endorsement confirmation received from Carrier/Sent to Agent | Endorsement confirmed |
| 130 | Declination/Nonrenewal Activity | Decline/nonrenewal |
| 131 | Bind Request Received from agent with missing documents | Incomplete bind |
| 133 | CUP Required Supplemental | CUP specific |
| 134 | Loss Run Request Received | Loss runs |
| 135 | Incomplete Binder - Pending Info/Documents | Incomplete bind |
| 139 | Prior to Bind Items Requested | Prior to bind |
| 140 | Send Declination to Agent | **Decline notification** — use for USLI decline automation |
| 141 | Binder Request Sent to Carrier via Portal | Portal bind |
| 144 | Unable to Bind Memo | Bind failure |
| 146 | Firm Quote Req for MTC/PHYS DAM | Transportation specific |
| 147 | Send RENEWAL to Agent | Renewal |
| 153 | Not Bound - USLI Direct Bill | USLI direct bill |
| 160 | Generic Email to Agent | Generic email |
| 161 | Send Finance Agreement ONLY to agent | Finance |
| 163 | CROSS SELL Contractors Equipment CROSS SELL | Cross-sell |
| 164 | Send Info to USLI Cross Sell Contractor Equipment | Cross-sell |
| 167 | Submit Pending Info To Carrier (Via Email) | Pending info |
| 170 | BLANK EMAIL TO AGENT | Blank email |
| 177 | Off Risk - Renewal | Off risk |

### Sections Reference

| SectionId | Description |
|---|---|
| 1 | Personal |
| 2 | Policy |
| 3 | Quotes>Submissions |
| 4 | Claims |
| 5 | Quotes |
| 6 | Agent |
| 7 | Inspections |
| 8 | Suspense |
| 9 | Claim Coverages |

---

## MGL Automation Flow — What the Agent Does

For each USLI GL auto-quote email (prefix MGL):

### Step 1: Create Quote (`SetQuote`)

```
LOB: CG
SubLOB: [determined by LLM from classification_description or coverage context]
Name: [from email classification.named_insured]
AgentNumber: [matched by LLM from email body retailer name → GetAgentsAndProspectsForLookup]
Address/City/State/Zip: [from extraction covered_location_address, if available]
FormOfBusiness: [determined by LLM from insured name entity suffix]
PolicyState: [from address, or FL if Florida address]
Term: [from extraction policy_term, "Annual" → 12]
EffectiveDate: ??? UNKNOWN — VERIFIED GAP
ExpirationDate: ??? UNKNOWN — depends on EffectiveDate
QuoteType: N
Status: 1
IsNewSystem: true
Action: Insert
OriginatingSystem: UIMS
```

Returns: `QuoteID` (auto-generated by Unisoft)

### Step 2: Create Submission (`SetSubmission`)

```
QuoteId: [from Step 1]
BrokerId: 1 (GIC Underwriters)
CarrierNo: 2 (USLI)
Description: [from classification_description or "General Liability"]
EffectiveDate: ??? SAME GAP
ExpirationDate: ??? SAME GAP
EnteredByUser: "ccerto" (or system user TBD)
MgaNo: 1
SubmissionId: 0 (new)
SubmissionNo: 0 (auto-generated)
```

Returns: `SubmissionId`, `SubmissionNo`

### Step 3: Log Activity (`SetActivity`)

```
ActionId: 2 ("Offer received from carrier")
ActivityId: 0 (new)
AgentNo: [from Step 1]
LoggedByUser: "ccerto" (or system user TBD)
LoggedDate: [email received_at date]
QuoteId: [from Step 1]
SectionId: 3 (Quotes>Submissions)
SubmissionId: [from Step 2]
```

### Step 4: Record Quote Amount

The premium ($656.50 total due for MGL026M2518) needs to be recorded. From the Unisoft UI, this goes in the submission's "QUOTE RECEIVED" section. Need to determine if `SetSubmission` with Action=Update can set the quote amount, or if it's a separate operation.

---

## Verified Data — Example Record

### MGL026M2518 — TRIPLE J HOLDINGS AT 14325 LLC

**Email:**
- Subject: `USLI Retail Web Quote MGL026M2518 for TRIPLE J HOLDINGS AT 14325 LLC from Jorge Yara at J. Yara Insurance Agency Inc`
- From: `no-reply@usli.com`
- Received: 2026-03-02T20:22:49Z
- Body contains: Retailer (J. Yara Insurance Agency Inc), Contact (Jorge Yara), Email (jorge@yarainsurance.com), Address (2500 NW 97TH AVE, Suite 202, Doral, FL 33172), Applicant name
- Attachments: 3 PDFs (Customer, Retailer, Applicant versions)

**Extraction (from PDF):**
- Quote #: MGL026M2518
- Carrier: United States Liability Insurance Company (Admitted, A++ Superior)
- Coverage: Commercial General Liability
- Premium: $650.00 base, $6.50 FIGA surcharge, $656.50 total
- Limits: $1M occurrence / $2M aggregate / $5K medical / $100K damage to premises
- Deductible: $0
- Location: 14325 Sw 121 Pl #5, Miami, FL 33186
- Classification: 62004 — "Condominiums - residential - (Unit owner risk only) annual rental"
- Term: Annual
- Quote valid until: 5/1/2026
- Optional excess: XSL026M2274 ($460 premium, $1M limit)
- Agent: Jorge Yara, J. Yara Insurance Agency Inc, jorge@yarainsurance.com

**Unisoft Agent Match:**
- Agency "J. Yara Insurance Agency Inc" → AgentNumber 6605 (exact match in `GetAgentsAndProspectsForLookup`)

**Unisoft Mapping:**
- LOB: CG (from MGL prefix)
- SubLOB: HM (Non-Artisans — from "Condominiums - residential" classification)
- Name: TRIPLE J HOLDINGS AT 14325 LLC
- AgentNumber: 6605
- Address: 14325 Sw 121 Pl #5
- City: Miami
- State: FL
- Zip: 33186
- FormOfBusiness: C (LLC → Corporation)
- PolicyState: FL
- Term: 12 (Annual)
- EffectiveDate: **UNKNOWN** — not in email or extraction
- Carrier: 2 (USLI)
- Broker: 1 (GIC)
- Premium: $656.50 total due

---

## Open Questions — Must Answer Before Building

1. ~~**EffectiveDate handling**~~ **RESOLVED 2026-04-02:** From JC's walkthrough video, **EffectiveDate = the current date** (the date the quote is being created in Unisoft). **ExpirationDate = one year from effective date** (default for annual term). This is standard practice — the effective date is when GIC enters the record, not when the agent submitted. Source: Craig reviewed the JC screen-share video and confirmed this behavior.

2. ~~**Quote amount field**~~ **RESOLVED 2026-04-01:** The `SubmissionDTO` has a `QuotedAmount` field (decimal). Set it via `SetSubmission` with `PersistSubmission: "Update"` after initial creation. Also has `TargetAmount` field.

3. **AssignedTo logic** — From the walkthrough, JC didn't highlight assignment as a critical part of the quote creation step. The focus was on LOB, SubLOB, and Agency. AssignedTo may default or be handled separately. Not blocking for Phase 1 (quote ID creation).

4. **System user for automation** — Should automated entries be logged under a specific user (e.g., a new "indemn-automation" user) or under an existing user like "ccerto"? This affects audit trail visibility.

5. **Duplicate detection** — `GetQuotesForLookupByCriteria` exists but returned 0 results when searching by name (tested with known quotes). The search may need specific criteria field names from the WSDL request DTO. `GetQuotesByName2` also exists but returned Fault. Need to determine the correct search parameters. Alternative: maintain our own mapping of USLI reference number → Unisoft QuoteID in MongoDB after creation.

6. ~~**FormOfBusiness codes**~~ **RESOLVED 2026-04-01:** Unisoft accepts any single char. Tested I, P, L, S, T, J, O — all create quotes successfully. Use L=LLC, C=Corporation, I=Individual, P=Partnership. The USLI application has checkboxes that map directly.

7. **SubLOB accuracy** — For the 79% of MGL extractions WITHOUT `classification_description`, how does the agent determine SubLOB? Can it read the PDF directly? Does it default to one? This needs a defined strategy, not an assumption.

---

## FormOfBusiness — What We Know

| Code | Meaning | Source |
|---|---|---|
| C | Corporation | Confirmed from Fiddler capture (JC's test entry) |
| I | Individual | NOT CONFIRMED — standard insurance convention |
| P | Partnership | NOT CONFIRMED — standard insurance convention |
| ? | LLC | **IMPORTANT: The USLI pre-filled application has LLC as its OWN checkbox, separate from Corporation.** The application checkboxes are: Individual, Corporation, Partnership, LLC, Other. Unisoft may have a distinct code for LLC (e.g., "L") or may map it to "C". UNKNOWN. |
| ? | Trust | Unknown code — Trusts appear in our data |
| ? | Other | The application has an "Other" checkbox option |

The Unisoft UI shows "Form of Business" as a dropdown. JC selected "Corporation" in the walkthrough. The full dropdown options were not captured in the video analysis.

**VERIFIED 2026-04-01:** Unisoft accepts ANY single character for FormOfBusiness. Tested I, P, L, S, T, J, O — all succeeded. It is a free-form char field, not a validated dropdown. Use `L` for LLC, `C` for Corporation, `I` for Individual, `P` for Partnership. The USLI pre-filled application checkbox maps directly.

---

## USLI MGL Quote PDF Structure — Verified

Each MGL email arrives with 3 PDF attachments:
- `MGL{ref}.pdf` — Customer copy (compact, ~50KB, 1-4 pages)
- `MGL{ref}_RetailerVersion.pdf` — Retailer copy (~540KB, includes more detail)
- `MGL{ref}_ApplicantVersion.pdf` — Applicant copy (~530KB, 16 pages, includes pre-filled application)

### Applicant Version Structure (verified from MGL026M2518, 16 pages)

| Pages | Section | Contents |
|---|---|---|
| 1-2 | Cover letter | Agent info header, insured name, quote number, section guide, excess liability mention, payment options |
| 3 | Quote summary + bind form | Quote number, "Quote is valid until [date]", **"Please bind effective: ___" (BLANK)**, insured email/phone (BLANK), optional coverages checkboxes, direct bill options, agent info, premium table |
| 3-4 | Section I: Premium & Underwriting | Carrier info (USLI, Admitted, A++ XIV), Term Quoted (Annual), coverage premium ($650), FIGA surcharge ($6.50), total ($656.50), wholesaler broker fee, additional costs |
| 4 | Sections A/B/C: Prior to Bind | Eligibility questions with Yes/No checkboxes (foreclosures, cancellations, condo size, heating, smoke detectors, wiring, etc.), items required within 21 days |
| 5 | Section II: Covered Locations | Location address, classification code (62004), description, exposure, rates, premium per location |
| 5 | Section III: Liability Limits | Each Occurrence ($1M), Personal Injury ($1M), Medical ($5K), Damage to Premises ($100K), General Aggregate ($2M), Deductible ($0), Loss Assessment |
| 6 | Section IV: Required Forms & Endorsements | CG form numbers with descriptions (12 endorsements listed) |
| 6 | Section V: Optional Coverages | Non-Owned Auto ($210), Terrorism ($100) with conditions |
| 6 | Section VI: Direct Bill Payment Plan | Single payment, two payments (50% + 50%) descriptions |
| 7-8 | Excess liability cover letter | XSL quote cover letter (same structure) |
| 8-10 | Excess liability quote | XSL premium, underlying coverages, forms, optional coverages, payment plan |
| 11-16 | Pre-filled application | The application USLI pre-filled from the agent's submission. Contains the data the agent originally entered. |

### Key Finding: "Please bind effective" is BLANK

The bind effective date field on page 3 is an unfilled form field. This is by design — USLI is offering a quote, and the effective date is chosen when the agent decides to bind. The policy effective date does not exist at the quote stage.

### Pre-filled Application (pages 11-16) — Verified Data Source

The Applicant version PDF includes a pre-filled application with data from the original agent submission. Verified from MGL026M2518:

**Page 11 (Application page 1 — General Information):**
- Applicant's Name: TRIPLE J HOLDINGS AT 14325 LLC
- Form Of Business: ☑ LLC (checkboxes: Individual, Corporation, Partnership, **LLC**, Other)
- Mailing Address: BLANK (not filled by agent)
- City/State/Zip: BLANK
- Phone/Fax/Email/Web: BLANK
- Coverage Desired: ☑ Monoline Liability (options: Monoline Liability, Monoline Property, Monoline Liquor, Package)
- Policy Term: ☑ Annual (options: 3 Months, 6 Months, 9 Months, Annual)
- What year did the business start: BLANK
- Loss Information: ☑ None or provide details below
- Description of Operations: **"CONDO FOR RENT"**
- Additional Insured: ☑ Not Applicable

**Page 12 (Application page 2 — Locations & Classifications):**
- Limits of Insurance (same as quote section III)
- Location #1: 14325 Sw 121 Pl #5, Miami, FL, 33186
- Classification: Condominiums - residential - (Unit owner risk only) annual rental, Code 62004, Premium Basis: Annual Rental, Exposure: 1
- Eligibility questions (Yes/No checkboxes, various condominium-specific)

**Page 13 (Application page 3 — Signature):**
- Signature fields: BLANK
- Date at bottom: 3/2/2026 (application date = quote date)
- **NO effective date field on the application**

**Pages 14-16:** Terrorism disclosure form (TRIADN FL), USLI privacy notice, Business Resource Center marketing flyer.

**Key findings from the application:**
1. **Form Of Business "LLC" is distinct from "Corporation"** — the application has separate checkboxes. Do not conflate.
2. **Mailing address is BLANK** — agents don't always fill this. Only the covered location address is reliable.
3. **Description of Operations ("CONDO FOR RENT")** — valuable for SubLOB determination and Unisoft BusinessDescription field.
4. **Coverage Desired checkbox** — confirms the LOB type (Monoline Liability vs Property vs Liquor vs Package). Maps to SubLOB reasoning.
5. **EffectiveDate is NOT on the application** — the date 3/2/2026 is the application/quote date, not the policy effective date.

---

## Changelog

| Date | Update | Source |
|---|---|---|
| 2026-04-01 | Initial creation — full field mapping, activity IDs, example record, gaps documented | MongoDB production data analysis, Unisoft API calls, Fiddler captures, WSDL |

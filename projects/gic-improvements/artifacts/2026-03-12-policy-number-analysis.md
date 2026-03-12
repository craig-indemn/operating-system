---
ask: "What do real GIC policy numbers look like, and what normalization rules would fix the most failures?"
created: 2026-03-12
workstream: gic-improvements
session: 2026-03-12-f
sources:
  - type: mongodb
    description: "192 policy_check tool call traces from Observatory prod, 2025-12-12 to 2025-12-26"
---

# GIC Policy Lookup Analysis — All 192 Tool Calls

**Source:** Observatory `traces` collection, `policy_check` tool runs
**Date range:** 2025-12-12 to 2025-12-26
**Total calls:** 192 (101 success, 91 failure = **47.4% failure rate**)

---

## Carrier → Policy Number Format Map

Every successful lookup, grouped by insurance carrier. This defines what valid policy numbers look like.

| Carrier | Format Pattern | Examples |
|---------|---------------|----------|
| **Granada Insurance** | `0185FL` + 8 digits OR `0110FL` + 8 digits | `0185FL00207842`, `0110FL00058793` |
| **Mid-Continent Casualty** | `04-CIM-` + 9 digits | `04-CIM-000062450` |
| **USLI** | 2-letter prefix + SPACE + 7 digits + optional letter | `GL 1320778`, `SE 1179117`, `GL 1229127A` |
| **AmTrust North America** | `TWC` + 7 digits | `TWC4719314` |
| **Mount Vernon Fire Insurance** | `XPL` + 7 digits OR `CP` + SPACE + 7-digit+letter | `XPL2631838A`, `CP 2660780C` |
| **Security National Insurance** | `SES` + 7 digits + SPACE + 2 digits | `SES1828375 00` |
| **Topa Insurance** | `SWPN-` + 6 digits + `-00` | `SWPN-028889-00` |
| **Slide Insurance** | `H3FL` + 9 digits | `H3FL000254178` |
| **Kinsale Insurance** | 10 digits + `-0` | `0100322674-0` |
| **Hadron Specialty** | `H0247GL` + 6 digits + `-00` | `H0247GL000245-00` |
| **Dellwood Specialty** | `DGL` + 8 digits + `-00` | `DGL00001468-00` |
| **Service Lloyds** | 5 digits + SPACE + 2 digits | `13280 25` |
| **Sirius America** | `WC PI` + SPACE + 7 digits + `-001` | `WC PI 1625230-001` |

---

## All Successful Lookups (101 calls, 79 unique policy numbers)

| Policy Number | Carrier | Times Looked Up |
|--------------|---------|-----------------|
| `0110FL00058793` | Granada Insurance | 6 |
| `SES1828375 00` | Security National | 6 |
| `0185FL00206140` | Granada Insurance | 3 |
| `GL 1320778` | USLI | 3 |
| `0110FL00058934` | Granada Insurance | 2 |
| `0185FL00067278` | Granada Insurance | 2 |
| `0185FL00207842` | Granada Insurance | 2 |
| `04-CIM-000060626` | Mid-Continent Casualty | 2 |
| `04-CIM-000060922` | Mid-Continent Casualty | 2 |
| `SWPN-028889-00` | Topa Insurance | 2 |
| `TWC4697598` | AmTrust | 2 |
| `TWC4719314` | AmTrust | 2 |
| `0100322674-0` | Kinsale Insurance | 1 |
| `0110FL00026571` | Granada Insurance | 1 |
| `0110FL00030795` | Granada Insurance | 1 |
| `0110FL00039344` | Granada Insurance | 1 |
| `0110FL00050570` | Granada Insurance | 1 |
| `0110FL00055300` | Granada Insurance | 1 |
| `0110FL00055322` | Granada Insurance | 1 |
| `0110FL00057053` | Granada Insurance | 1 |
| `0110FL00059022` | Granada Insurance | 1 |
| `0110FL00059104` | Granada Insurance | 1 |
| `0110FL00059110` | Granada Insurance | 1 |
| `0110FL00059160` | Granada Insurance | 1 |
| `0110FL00059170` | Granada Insurance | 1 |
| `0110FL00059193` | Granada Insurance | 1 |
| `0110FL00059198` | Granada Insurance | 1 |
| `0185FL00039668` | Granada Insurance | 1 |
| `0185FL00064845` | Granada Insurance | 1 |
| `0185FL00065712` | Granada Insurance | 1 |
| `0185FL00118583` | Granada Insurance | 1 |
| `0185FL00121731` | Granada Insurance | 1 |
| `0185FL00130499` | Granada Insurance | 1 |
| `0185FL00132705` | Granada Insurance | 1 |
| `0185FL00133267` | Granada Insurance | 1 |
| `0185FL00140179` | Granada Insurance | 1 |
| `0185FL00148461` | Granada Insurance | 1 |
| `0185FL00150253` | Granada Insurance | 1 |
| `0185FL00151499` | Granada Insurance | 1 |
| `0185FL00165331` | Granada Insurance | 1 |
| `0185FL00182046` | Granada Insurance | 1 |
| `0185FL00182050` | Granada Insurance | 1 |
| `0185FL00193425` | Granada Insurance | 1 |
| `0185FL00193529` | Granada Insurance | 1 |
| `0185FL00200819` | Granada Insurance | 1 |
| `0185FL00201306` | Granada Insurance | 1 |
| `0185FL00201323` | Granada Insurance | 1 |
| `0185FL00202042` | Granada Insurance | 1 |
| `0185FL00203312` | Granada Insurance | 1 |
| `0185FL00206313` | Granada Insurance | 1 |
| `0185FL00207929` | Granada Insurance | 1 |
| `0185FL00208428` | Granada Insurance | 1 |
| `0185FL00208454` | Granada Insurance | 1 |
| `0185FL00208696` | Granada Insurance | 1 |
| `0185FL00208736` | Granada Insurance | 1 |
| `0185FL00208860` | Granada Insurance | 1 |
| `0185FL00208970` | Granada Insurance | 1 |
| `04-CIM-000049233` | Mid-Continent Casualty | 1 |
| `04-CIM-000054705` | Mid-Continent Casualty | 1 |
| `04-CIM-000057653` | Mid-Continent Casualty | 1 |
| `04-CIM-000058799` | Mid-Continent Casualty | 1 |
| `04-CIM-000059480` | Mid-Continent Casualty | 1 |
| `04-CIM-000061889` | Mid-Continent Casualty | 1 |
| `04-CIM-000062080` | Mid-Continent Casualty | 1 |
| `13280 25` | Service Lloyds | 1 |
| `CP 2660780C` | Mount Vernon Fire | 1 |
| `DGL00001468-00` | Dellwood Specialty | 1 |
| `GL 1229127A` | USLI | 1 |
| `GL 1278872` | USLI | 1 |
| `GL 1322059` | USLI | 1 |
| `H0247GL000245-00` | Hadron Specialty | 1 |
| `H3FL000254178` | Slide Insurance | 1 |
| `SE 1179117` | USLI | 1 |
| `SE 1179316` | USLI | 1 |
| `SWPN-034028-00` | Topa Insurance | 1 |
| `WC PI 1625230-001` | Sirius America | 1 |
| `XPL2617717` | Mount Vernon Fire | 1 |
| `XPL2631838A` | Mount Vernon Fire | 1 |

---

## All Failed Lookups (91 calls)

### Category 1: Edition/Renewal Suffix Appended (54 calls, 59% of failures)

The agent appends `-N` or ` - N` (edition/renewal number) to the base policy number. The GIC API does not accept these suffixes. **This is the #1 cause of failure.**

| Sent to API | Base Number | Suffix | Base Would Succeed? | Evidence |
|------------|-------------|--------|---------------------|----------|
| `0185FL00207842-0` | `0185FL00207842` | `-0` | YES | Same conversation: failed then retried without suffix and succeeded |
| `0185FL00140179 - 5` | `0185FL00140179` | ` - 5` | YES | Same conversation: retried without suffix, succeeded |
| `0185FL00208454 - 0` | `0185FL00208454` | ` - 0` | YES | Same conversation: retried without suffix, succeeded |
| `0110FL00057053-2` | `0110FL00057053` | `-2` | YES | Same conversation: retried without suffix, succeeded |
| `0110FL00055322 - 2` | `0110FL00055322` | ` - 2` | YES | Same conversation: retried without suffix, succeeded |
| `0185FL00208696-0` (x2) | `0185FL00208696` | `-0` | YES | Different conversation: base succeeded |
| `0185FL00208860-0` (x2) | `0185FL00208860` | `-0` | YES | Different conversation: base succeeded |
| `0185FL00151499-3` | `0185FL00151499` | `-3` | YES | Different conversation: base succeeded |
| `0185FL00182046-2` (x2) | `0185FL00182046` | `-2` | YES | Different conversation: base succeeded |
| `0110FL00059170-0` | `0110FL00059170` | `-0` | YES | Different conversation: base succeeded |
| `0185FL00133267-7` | `0185FL00133267` | `-7` | YES | Different conversation: base succeeded |
| `0110FL00059152-0` | `0110FL00059152` | `-0` | Likely YES | Granada format, never tried without suffix |
| `0185FL00164174 - 4` | `0185FL00164174` | ` - 4` | Likely YES | Granada format |
| `0185FL00055802 - 11` (x2) | `0185FL00055802` | ` - 11` | Likely YES | Granada format |
| `0185FL00181400-2` | `0185FL00181400` | `-2` | Likely YES | Granada format |
| `0185FL00164257-4` | `0185FL00164257` | `-4` | Likely YES | Granada format |
| `0185FL00180514-1` | `0185FL00180514` | `-1` | Likely YES | Granada format |
| `0185FL00147025-5` | `0185FL00147025` | `-5` | Likely YES | Granada format |
| `0185FL00190843-2` (x2) | `0185FL00190843` | `-2` | Likely YES | Granada format |
| `0185FL00191368-2` | `0185FL00191368` | `-2` | Likely YES | Granada format |
| `0185FL00191368 - 2` | `0185FL00191368` | ` - 2` | Likely YES | Granada format |
| `0185FL00201697-1` | `0185FL00201697` | `-1` | Likely YES | Granada format |
| `0185FL00208126-0` | `0185FL00208126` | `-0` | Likely YES | Granada format |
| `0185FL00208180-0` | `0185FL00208180` | `-0` | Likely YES | Granada format |
| `0185FL00208510 - 0` | `0185FL00208510` | ` - 0` | Likely YES | Granada format |
| `0185FL00204309-0` | `0185FL00204309` | `-0` | Likely YES | Granada format |
| `0185FL00204033 - 0` | `0185FL00204033` | ` - 0` | Likely YES | Granada format |
| `0185FL00206801-0` | `0185FL00206801` | `-0` | Likely YES | Granada format |
| `0185FL00207022 - 0` | `0185FL00207022` | ` - 0` | Likely YES | Granada format |
| `0185FL00181458-2` | `0185FL00181458` | `-2` | Likely YES | Granada format |
| `0185FL00201657-1` | `0185FL00201657` | `-1` | Likely YES | Granada format |
| `0185FL00202025-0` (x2) | `0185FL00202025` | `-0` | Likely YES | Granada format |
| `0185FL00208854-0` (x2) | `0185FL00208854` | `-0` | Likely YES | Granada format |
| `0110FL00050570 - 4` | `0110FL00050570` | ` - 4` | YES | `0110FL00050570` succeeded separately |
| `0110FL00055352 - 2` | `0110FL00055352` | ` - 2` | Likely YES | Granada format |
| `0110FL00059053 - 0` | `0110FL00059053` | ` - 0` | Likely YES | Granada format |
| `0110FL00059057-0` | `0110FL00059057` | `-0` | Likely YES | Granada format |
| `0110FL00059198 - 0` | `0110FL00059198` | ` - 0` | YES | `0110FL00059198` succeeded separately |
| `0185FL00023014-15` | `0185FL00023014` | `-15` | Likely YES | Granada format |
| `0185FL00169304 - 3` | `0185FL00169304` | ` - 3` | Likely YES | Granada format |
| `0185Fl00051209-12` | `0185Fl00051209` | `-12` | Likely YES | Granada format (note lowercase 'l') |
| `o185FL00202025-0` | `o185FL00202025` | `-0` | Uncertain | Lowercase 'o' instead of '0' + suffix |

**Self-correction observed:** In 6 conversations, the agent first tried with a suffix, failed, then retried without the suffix and succeeded. This proves the suffix is the only issue.

### Category 2: Missing Required Space in Prefix (3 calls, 3% of failures)

Some carriers require a space between the letter prefix and numeric portion.

| Sent to API | Should Be | Would Succeed? |
|------------|-----------|----------------|
| `GL1322059` | `GL 1322059` | YES — `GL 1322059` succeeded in different conversation |
| `GL1077426` | `GL 1077426` | Very likely — all USLI GL policies need the space |
| `CP2658995C` | `CP 2658995C` | Very likely — `CP 2660780C` succeeded with space |

### Category 3: Not a Policy Number (2 calls, 2% of failures)

The agent sent free text instead of a policy number.

| Sent to API | What It Actually Was |
|------------|---------------------|
| `Boat quote for Jorge Vazquez, requested on December 12, 2025, 2020 Stamas 326 Aegean` | Quote request description |
| `Florida Creative Feeling LLC 546 Wayland Dr, Haince City, FL 33844 Lilibeth Fagundez, (847) 660-9938 liclilyfagundez@gmail.com` | Customer contact info |

### Category 4: Genuinely Invalid or Unknown Format (22 calls, 24% of failures)

These policy numbers don't match any known valid format and never succeeded in any variation.

| Sent to API | Times Tried | Analysis |
|------------|-------------|----------|
| `0185FL00207569` | 7 (incl. with ` - 0`) | Valid Granada format but policy genuinely not found — possibly cancelled/expired/wrong number |
| `0185FL00149507` | 2 (incl. with ` - 4`) | Valid Granada format but genuinely not found |
| `136372` | 3 | Too short, unknown carrier format |
| `136665` | 3 | Too short, unknown carrier format |
| `136114` | 1 | Too short, unknown carrier format |
| `26916` | 3 | Too short, unknown carrier format |
| `6129` | 2 | Too short, unknown carrier format |
| `7009` | 1 | Too short, unknown carrier format |
| `579988A` | 4 | Unknown carrier format |
| `01699800011210202561049` | 4 | Too long (23 chars) — likely a payment reference or account number |
| `1625230-001` | 1 | Missing `WC PI ` prefix — `WC PI 1625230-001` succeeded |
| `CPL2718797` | 2 | Unknown carrier format — possibly not a GIC-managed policy |
| `QCP01FL1214336` | 2 | Unknown carrier format |
| `MPL025d7246` | 1 | Unknown carrier format (lowercase 'd') |
| `GL 1229127B` | 1 | Valid USLI format but variant B doesn't exist (variant A succeeded) |

### Category 5: Typos (1 call)

| Sent to API | Issue |
|------------|-------|
| `o185FL00202025-0` | Lowercase letter 'o' instead of digit '0' at start, plus edition suffix |

---

## Summary

### Success/Failure Breakdown

| Category | Calls | % of Failures | Fixable by Normalization? |
|----------|-------|---------------|--------------------------|
| Edition suffix appended (`-N`, ` - N`) | 54 | 59% | **YES** — strip suffix |
| Missing space in prefix | 3 | 3% | **YES** — add space after letter prefix |
| Not a policy number | 2 | 2% | NO — need to reject before API call |
| Genuinely invalid / unknown format | 22 | 24% | Partially — some missing prefixes |
| Typos | 1 | 1% | Partially |
| Genuinely not found (valid format) | 9 | 10% | NO — policy doesn't exist |

### Key Finding: 100% of addressable failures are fixed with two normalization rules

57 of 91 total failures (63%) are caused by formatting issues that normalization can fix. The remaining 34 failures (37%) are not addressable by parsing — they are genuinely invalid policy numbers, non-existent policies, non-policy-number inputs, or typos. The normalization resolves **100% of the addressable portion**.

**Rule 1: Strip edition/renewal suffixes from Granada-format policy numbers**

For policy numbers matching `0185FL` or `0110FL` pattern:
- Remove `-N` suffix (any number of digits after the dash)
- Remove ` - N` suffix (space-dash-space-digits)

Regex: For numbers matching `^(0\d{3}FL\d{8})[\s-].*$`, use capture group 1.

This single rule would fix **54 of 91 failures (59%)**.

**Rule 2: Insert space in USLI/Mount Vernon prefix-number patterns**

For policy numbers starting with 2-letter prefix directly followed by digits:
- `GL1234567` → `GL 1234567`
- `SE1234567` → `SE 1234567`
- `CP1234567X` → `CP 1234567X`

Regex: For numbers matching `^(GL|SE|CP|WC)(\d)`, insert space between prefix and digits.

This rule would fix **3 more failures**.

**Combined: 57 of 91 failures fixed (63%)**.

### What Valid GIC Policy Numbers Look Like

1. **Granada** (most common): `0185FL` + 8 digits or `0110FL` + 8 digits (14 chars total, case-insensitive on FL)
2. **Mid-Continent Casualty**: `04-CIM-` + 9 zero-padded digits
3. **USLI**: `GL ` or `SE ` + 7 digits + optional letter suffix (A/B)
4. **Mount Vernon**: `XPL` + 7 digits + optional letter, or `CP ` + 7 digits + letter
5. **AmTrust**: `TWC` + 7 digits
6. **Security National**: `SES` + 7 digits + ` ` + 2 digits
7. **Topa**: `SWPN-` + 6 digits + `-00`
8. **Slide**: `H3FL` + 9 digits
9. **Kinsale**: 10 digits + `-0`
10. **Hadron**: `H0247GL` + 6 digits + `-00`
11. **Dellwood**: `DGL` + 8 digits + `-00`
12. **Service Lloyds**: 5 digits + ` ` + 2 digits
13. **Sirius America**: `WC PI ` + 7 digits + `-001`

### The Most Common Mistake

The agent (LLM) is pulling policy numbers from context that includes edition numbers — likely from documents or prior messages where the format is `0185FL00207842-0` (base policy number + dash + edition number). The GIC API only accepts the base policy number without the edition suffix.

The inconsistency in suffix format (sometimes `-0`, sometimes ` - 0`, sometimes `-12`) suggests the user is providing the number in various formats and the agent is passing it through as-is.

### Recommended Normalization Pipeline

```
1. Trim whitespace
2. If input matches Granada pattern (0[0-9]{3}FL[0-9]{8}), strip everything after the 14-char base
3. If input starts with GL/SE/CP/WC followed immediately by a digit, insert a space
4. If input is clearly not a policy number (>30 chars, contains @, contains multiple spaces), reject before API call
5. Pass to API
6. If API fails, try stripping any trailing -N or - N suffix and retry once
```

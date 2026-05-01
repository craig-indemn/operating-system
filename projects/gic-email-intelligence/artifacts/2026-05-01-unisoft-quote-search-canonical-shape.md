---
ask: "Document the canonical SOAP wire format for Unisoft quote-search ops, the dead-end paths that wasted time, and the diagnostic signals that distinguish the correct request shape from a malformed one. Future-self reads this BEFORE attempting any new Unisoft enumeration op."
created: 2026-05-01
workstream: gic-email-intelligence
session: 2026-05-01-quote-search-discovery
sources:
  - type: fiddler
    description: "export5.saz — fresh capture of Unisoft desktop UI doing a name-based quote search in UAT. Uploaded to s3://indemn-gic-attachments/research/quote-search-2026-05-01-export5.saz. Session 115 contains the canonical GetQuotesForLookupByCriteria request that returns data."
  - type: codebase
    description: "unisoft-proxy/server/UniProxy.cs — confirmed proxy URL was already correct; root cause was wrong Criteria DTO field set."
  - type: experiment
    description: "Verified end-to-end against UAT proxy on 2026-05-01: search Name=Craig returns Q:17129 with full QuoteForLookupDTO. ReplyStatus=Success, RowsAffected=1, QuotesForLookup populated."
---

# Unisoft Quote Search — Canonical SOAP Wire Format

## TL;DR

Unisoft's quote-search SOAP ops accept the request only when the `Criteria` DTO uses the **UI's wire format**, not the saved-search XML format that `GetAllSearchPreferences` returns. Sending a Criteria with the wrong field names (e.g., `SelWordFilterOption` instead of `WordLookupType`) produces `Success` + `RowsAffected=N` + **empty data arrays**, with no error or fault to indicate the misshape. The server silently discards the unrecognized fields, applies what it can interpret, returns the count, and stops.

**Use `GetQuotesForLookupByCriteria` for name/address-based search.** Returns lighter `QuoteForLookupDTO` items with the lookup-relevant fields (QuoteId, Name, Address, AgentNumber, LOB/SubLOB, dates, etc.). This is what the desktop UI itself calls.

## What was wrong (so we don't repeat it)

The saved-search XML returned by `GetAllSearchPreferences` is the UI's *internal state representation* — used to restore the search panel's UI when a user opens a saved search. It is NOT the same shape as the SOAP request. The two share field names by coincidence in some cases but diverge in others.

| Field in saved-search XML (`<QuoteSearchCriteria>`) | Field in SOAP request (`<Criteria>` of `QuoteListRequest`) |
|---|---|
| `SelWordFilterOption` | **`WordLookupType`** |
| `SelectedSearchByOption` | **(not present)** |
| `EnteredDateRange` (nested object with `FromDate`/`ToDate`/`SelectedRange`/`IsDateRangeDetailEnabled`) | **flat `EnteredFromDate` / `EnteredToDate` / `EnteredAsOfDate`** |
| `LastActivityDateRange` (nested) | flat `LastActivityFromDate` / `LastActivityToDate` / `LastActivityAsOfDate` |
| `TaskDueDateRange` (nested) | flat `TaskDueFromDate` / `TaskDueToDate` / `TaskDueAsOfDate` |
| (not present) | **`BusinessType`, `LOB`, `SubLOB`, `Underwriter`** (all nillable) |
| `SearchForValue` (in Criteria, populated) | (in Criteria) populated only when the user typed a value; the top-level `SearchForValue` remains nil |

## Diagnostic signal — how to recognize the bug shape

If a Unisoft enumeration op returns:

- `_meta.ReplyStatus = "Success"`
- `_meta.RowsAffected > 0` (often suspiciously large — the unfiltered total)
- Data arrays empty (`<Quotes i:nil="true"/>`, `<QuotesForLookup/>` with no children)

**The Criteria DTO is malformed in a way the server silently ignores.** It is NOT permissions, NOT pagination, NOT auth-identity scope. It is a field-name or shape mismatch. Compare your request body against a captured UI request byte-for-byte.

## Canonical request — `GetQuotesForLookupByCriteria`

**Endpoint:** `POST https://ins-gic-service-{uat,prod}-app.azurewebsites.net/imsservice.svc`
**SOAP Action:** `http://tempuri.org/IIMSService/GetQuotesForLookupByCriteria`
**Auth:** WS-SecureConversation (the proxy's existing SoapBridge handles this; no special config).
**Source:** captured SAZ `export5.saz` session 115, 2026-05-01.

### JSON form (what the proxy accepts via `/api/soap/GetQuotesForLookupByCriteria`)

```json
{
  "AgentNumber": 0,
  "Criteria": {
    "Address": "",
    "AgentNo": 0,
    "BusinessType": null,
    "CarrierNo": 0,
    "DBA": "",
    "EnteredAsOfDate": "0001-01-01T00:00:00",
    "EnteredFromDate": "0001-01-01T00:00:00",
    "EnteredToDate": "0001-01-01T00:00:00",
    "LOB": null,
    "LastActivityAsOfDate": "0001-01-01T00:00:00",
    "LastActivityFromDate": "0001-01-01T00:00:00",
    "LastActivityId": 0,
    "LastActivityToDate": "0001-01-01T00:00:00",
    "Name": "<insured-name-search-term>",
    "NonAssignedQuotesOnly": false,
    "PolicyNo": "",
    "QuoteId": 0,
    "StatusId": 0,
    "SubLOB": null,
    "TaskActionId": 0,
    "TaskDueAsOfDate": "0001-01-01T00:00:00",
    "TaskDueFromDate": "0001-01-01T00:00:00",
    "TaskDueToDate": "0001-01-01T00:00:00",
    "TaskStatusId": 0,
    "Underwriter": null,
    "WordLookupType": "Contains"
  },
  "IsNewSystem": false,
  "ItemsPerPage": 20,
  "MGANumber": 0,
  "PageNumber": 1
}
```

### Field semantics

| Field | Set to (default search) | Notes |
|---|---|---|
| `Criteria.Name` | the insured-name search term | The primary filter for "search by insured name." Empty string returns all (subject to other filters). |
| `Criteria.WordLookupType` | `"Contains"` | Other valid values: `"StartsWith"`. |
| `Criteria.Address` | `""` (or address fragment) | Server treats `""` as no-filter. |
| `Criteria.DBA` | `""` | DBA-name fragment if filtering by DBA. |
| `Criteria.AgentNo` | `0` (no filter) | Filter by Unisoft agent number. |
| `Criteria.CarrierNo` | `0` (no filter) | Filter by carrier (USLI=2). |
| `Criteria.StatusId` | `0` (any) or `1` (active) | `1` reduces results meaningfully. |
| `Criteria.BusinessType` | `null` | Pass `null` (becomes `i:nil` in XML). |
| `Criteria.LOB` / `SubLOB` | `null` (or `"CG"` etc) | Pass `null` for no filter. |
| `Criteria.Underwriter` | `null` | Filter by assigned UW username. |
| `Criteria.QuoteId` | `0` (no filter) | If you have the ID, use `GetQuote` directly. |
| `Criteria.PolicyNo` | `""` | Filter by policy number. |
| `Criteria.NonAssignedQuotesOnly` | `false` | Set `true` to filter to unassigned quotes. |
| `Criteria.LastActivityId` | `0` | Filter by last action. |
| All `*Date` fields | `"0001-01-01T00:00:00"` | Sentinel for "no date filter." |
| Top-level `IsNewSystem` | `false` | UI sends false. |
| Top-level `SearchForValue` | omit (or `null`) | Top-level value is unused; the `Name` inside `Criteria` is what filters. |
| Top-level `SortExpression` | omit (or `null`) | Server defaults; pass nil. |
| Top-level `PageNumber` / `ItemsPerPage` | `1` / `20` | UI uses 20/page. Server is 1-indexed. |
| Top-level `MGANumber` / `AgentNumber` | `0` (no filter) | Top-level versions of the in-Criteria values. |

## Canonical response

```xml
<GetQuotesForLookupByCriteriaResult>
  <ReplyStatus>Success</ReplyStatus>
  <RowsAffected>1</RowsAffected>
  <Quote i:nil="true"/>
  <Quotes i:nil="true"/>
  <QuotesForLookup>
    <b:QuoteForLookupDTO>
      <b:QuoteId>17129</b:QuoteId>
      <b:Name>Craig Certo</b:Name>
      <b:Name2 i:nil="true"/>
      <b:Address>1111 test drive</b:Address>
      <b:City>alexandria</b:City>
      <b:State>VA</b:State>
      <b:Zip>22214</b:Zip>
      <b:Zip4 i:nil="true"/>
      <b:AgentNumber>777</b:AgentNumber>
      <b:LOB>CG</b:LOB>
      <b:LOBDescription>General Liability</b:LOBDescription>
      <b:SubLOB>AC</b:SubLOB>
      <b:SubLOBDescription>Artisans/Contractors</b:SubLOBDescription>
      <b:QuoteType>N</b:QuoteType>
      <b:StatusId>2</b:StatusId>
      <b:CreatedDate>2026-04-01T00:00:00</b:CreatedDate>
      <b:LastActivityDate>2026-04-01T10:40:19.01</b:LastActivityDate>
    </b:QuoteForLookupDTO>
  </QuotesForLookup>
</GetQuotesForLookupByCriteriaResult>
```

The proxy's `XmlToJson` translator surfaces `QuotesForLookup` as a JSON array of dicts. Use that.

**Field name reminders:** `QuoteId` (lowercase 'd') inside the DTO body — same as `SubmissionDTO.QuoteId`. The top-level `GetQuote` op takes `QuoteID` (capital 'ID'), but DTOs use `QuoteId`. Unisoft API has casing inconsistencies; verify per operation.

## Sister ops — same Criteria shape

These all take `QuoteListRequest` with the same Criteria DTO. Behavior:

- **`GetQuotesForLookupByCriteria`** — returns `QuotesForLookup: [QuoteForLookupDTO]` (lightweight). **The right op for search.**
- **`GetQuotes`** — returns `Quotes: [QuoteDTO]` (full DTOs, heavier). Use only when search results need full Quote details.
- **`GetQuotesByName2`** — same shape, narrower scope (Name-only filter via Criteria). The UI doesn't use it; prefer `GetQuotesForLookupByCriteria`.
- **`GetQuotesByAddress`** — same shape, address-focused. Untested whether it has its own Criteria nuances.

## Ops that are NOT search and have different shapes

Not to be confused with the above:

- `GetSubmissions(QuoteId=N)` — enumeration scoped to a Quote ID. Different request: `{"QuoteId": N}`. Always works (we use it in production).
- `GetActivitiesByQuoteId(QuoteId=N)` — enumeration scoped to a Quote ID. Different request shape.
- `GetAllSearchPreferences` — returns the saved-search UI-state XML for all users. **Do not model SOAP request shapes after the XML in `SearchPreferenceData`** — that's UI state, not wire format.
- `GetSearchPreferencesByUser(UserName=X)` — single-user variant.

## What we tested that didn't work, and why

For audit / future-self:

| Attempted shape | Result | Why it failed |
|---|---|---|
| Bare `{"SearchForValue":"Craig"}` (top-level only) | `Success` + `RowsAffected=11404` + empty arrays | Criteria was nil; server returned unfiltered total |
| Criteria with saved-search field names (`SelWordFilterOption`, `SelectedSearchByOption`, nested `EnteredDateRange`) | `Success` + count varies with `StatusId` (filter partially honored) + empty arrays | Server silently dropped unrecognized fields; the recognized ones (e.g. `StatusId`) applied; data array never populated because Criteria couldn't be fully parsed |
| `IsNewSystem=true` and various combinations | Same empty data | Not the lever; UI sends `false`. |
| Pagination matrix (`PageNumber=0..1`, `ItemsPerPage=10..10000`) | Same empty data | Not the lever. |
| `IIMSService/Login(UserName, Password)` to elevate identity | `BRConstraint: Invalid username and/or password` | The IIMSService SOAP `Login` op is a different auth path than the REST API gateway's `/api/authentication/login`. Regular underwriter creds do not authenticate at the SOAP level — the SOAP API uses WS-Trust + `UNISOFT_WS_USER` / `UNISOFT_WS_PASS`. |
| REST API gateway probe for `/api/quotes` endpoints | All HTTP 404 | Quote search is genuinely SOAP-only. |
| Different SOAP host (`ins-gic-service-uat-app.azurewebsites.net` vs `services.uat.gicunderwriters.co/management`) | The proxy was already pointing at the correct host. The Azure-direct URL was always the active one. | Confirmed by reading `C:\unisoft\UniProxy.env` 2026-05-01: `UNISOFT_SOAP_URL=https://ins-gic-service-uat-app.azurewebsites.net/imsservice.svc`. |

## Capture reference

The 2026-05-01 SAZ `export5.saz` (uploaded to `s3://indemn-gic-attachments/research/quote-search-2026-05-01-export5.saz`) contains 333 sessions from a manual quote-search-by-name action in the Unisoft UAT desktop UI. Sessions of interest:

- `059_c.txt` — `GetQuoteActions` (UI loading dropdown options)
- `115_c.txt` — **`GetQuotesForLookupByCriteria` with Name=Craig — the canonical request**
- `115_s.txt` — **The canonical response with QuoteForLookupDTO**
- `116_c.txt` — `GetQuote(QuoteID=17129)` (UI opening the result)
- `139_c.txt` — `GetQuoteAttachments` (UI loading attachments tab)
- `167_c.txt`, `207_c.txt` — additional `GetQuoteActions` / search refinements

For any future Unisoft op behaving unexpectedly: capture the UI doing the same action, compare requests byte-by-byte. Saved-search XML in `GetAllSearchPreferences` is NOT a substitute for a wire capture.

## Implementation note for the proxy

`unisoft-proxy/client/cli.py` should expose `unisoft quote search --name <X> [--lob <X>] [--limit N]` wrapping `GetQuotesForLookupByCriteria` with the canonical Criteria template above. The proxy's existing `SoapBridge` + JSON-to-XML translation already handles the shape correctly (`Criteria` is already in `dtoNamespaces` with the Quotes namespace). No proxy change needed.

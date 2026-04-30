---
ask: "Document the Unisoft Quote Search investigation findings so a future session can resume cleanly. Pivot off USLI feature work — JC follow-ups take priority."
created: 2026-04-30
workstream: gic-email-intelligence
session: 2026-04-30-quote-search-investigation
status: PAUSED — pending fresh Fiddler SAZ capture from Craig
sources:
  - type: codebase
    description: "Full read of UniProxy.cs (JsonToXml at line 1875, dtoNamespaces at 1848) — confirmed Criteria IS in dtoNamespaces"
  - type: research
    description: "operations-index.md (89 SOAP ops captured), wsdl-complete.md (910 ops, 1668 types), all SOAP raw payloads in raw-payloads/soap/"
  - type: ec2
    description: "Many read-only probes against UAT proxy via SSM into dev-services (i-0fde0af9d216e9182). All read-only; no prod or write changes. Used /api/soap/ + /api/soap_raw/ debug endpoints."
  - type: brainstorming
    description: "Multiple rounds of hypothesis → test → eliminate with Craig 2026-04-30"
---

# Unisoft Quote Search — Investigation & Resume Notes

## TL;DR for resuming session

Quote search via the Unisoft SOAP API is **stuck at "RowsAffected returns the correct count, but the data array is always empty server-side."** The prior session (2026-04-29) inferred this was a permission limitation and Craig was presented Option A "JC provides Quote ID." **That inference was wrong** — today's exhaustive testing ruled out permissions, request shape, pagination, sort, and proxy translation. The actual cause is unidentified but is server-side: the response wire format has `<Quotes xmlns="..."/>` empty element with no children, regardless of what we do in the request.

The recommended path forward is **a fresh Fiddler SAZ capture of the Unisoft desktop UI doing a name-based quote search**. None of the existing 89 captured SOAP operations include a quote-enumeration call — the UI must be using a path we haven't seen. Capture would reveal the exact wire format (op + service + auth + body) the UI uses, which we then wrap in our proxy.

The USLI feature implementation plan and design doc remain valid for everything OTHER than the search step. The skill, deepagent factory, CLI commands, idempotency classifier, folder routing, all stay. Only the "Find the Quote" step (Phase C.1 + skill Step 2) is blocked on this finding.

## What was definitively ruled out

| Hypothesis | Evidence against |
|---|---|
| **Permissions / row-level security** | `GetSubmissions(QuoteId=17129)` returns real data (1 Submission). `GetActivitiesByQuoteId` works in prod daily. `GetAllSearchPreferences` returns 18 saved searches. Our anonymous SCT identity is NOT being row-filtered out of quote-related data — except specifically on the Quote enumeration ops. |
| **Filter not reaching server** | Setting `Criteria.StatusId=1` narrowed `RowsAffected` from 11404 → 8415 on `GetQuotesForLookupByCriteria` and `GetQuotes`. The Criteria IS being processed; it just doesn't unlock data return. |
| **Pagination** | Tested PageNumber=0/1, ItemsPerPage=10/100/10000. All returned same empty data with same RowsAffected. |
| **Missing SortExpression** | Tested with and without "Name ASC", "QuoteId DESC". No effect. |
| **AgentNumber / MGANumber filters** | Tested AgentNumber=777 (Q:17129's agent), MGANumber=1 (GIC's MGA). Same result. |
| **`IsNewSystem` flag** | Tested true and false. Same result. |
| **Proxy JSON-to-XML translation broken** | `Criteria` IS already in `dtoNamespaces` at `unisoft-proxy/server/UniProxy.cs:1850` with the right namespace. The proxy's `AppendField` → `AppendDtoField` recursion handles nested DTOs (date ranges) correctly with alphabetical-ordered `b:` prefix. Verified by reading the code, not just inferring. |
| **Wrong credentials** | REST gateway login (`POST /api/authentication/login` at `ins-gic-api-gateway-uat-app.azurewebsites.net`) **succeeds for ccerto + GIC2026$$!** and returns a valid JWT with `role: Underwriter`. So the password is correct. The IIMSService SOAP `Login` op rejects the same creds — meaning that op is a different auth path entirely (not the user-facing one). |
| **REST API gateway has a quote endpoint we missed** | Probed `/api/quotes`, `/api/v1/quotes`, `/api/quotes/search`, `/api/quotes/byName`, `/api/quotes/lookup`, `/api/quotes/dashboard`, `/api/quoteslookup`, plus various param shapes. **All HTTP 404.** REST gateway has tasks/searchpreferences/users/brokers but no quote endpoints. Quote search is genuinely SOAP-only on Unisoft's side. |

## What we know works

- `GetQuote(QuoteID)` — by ID, full DTO. Verified with Q:17129.
- `GetSubmissions(QuoteId)` — scoped to a known Quote ID. Returns real data (camelCase `QuoteId` per WSDL — note the `unisoft_client.get_submissions` PascalCase bug we already cataloged in plan task C.0).
- `GetActivitiesByQuoteId` — works in prod daily.
- `GetAllSearchPreferences` — returned 18 saved searches across 11 users including `jcdp`. Provides canonical `<QuoteSearchCriteria>` wire shape (see "Field shape captured" below).
- REST gateway `POST /api/authentication/login` — returns JWT for ccerto.
- REST gateway `/api/v1/userSearchPreferences` (no params) — returns saved-search list (same data as SOAP equivalent).

## Current Unisoft state (2026-04-30)

- UAT total quotes: ~11,404 (RowsAffected with no filter)
- UAT active quotes (StatusId=1): 8,415
- Q:17129 (Craig Certo, AgentNumber 777, LOB CG/AC, address "1111 test drive", city "alexandria", zip 22214) is a stable test target.
- 8 users have saved `QuoteSearchCriteria` preferences: ariadna, ARIVERA, danayg, gloria, jcdp, LeslieC, NANCY, nsantana, sam.

## Field shape captured (canonical Criteria DTO from gloria's saved search)

The exact XML shape Unisoft accepts for `QuoteSearchCriteriaDTO`. Use this as ground truth for any future request shape:

```xml
<QuoteSearchCriteria>
  <Name>wind rose transport</Name>
  <DBA />
  <Address />
  <NonAssignedQuotesOnly>false</NonAssignedQuotesOnly>
  <EnteredDateRange>
    <AsOfDate xsi:nil="true" />
    <FromDate xsi:nil="true" />
    <ToDate xsi:nil="true" />
    <SelectedRange>Include all dates</SelectedRange>
    <IsDateRangeDetailEnabled>false</IsDateRangeDetailEnabled>
  </EnteredDateRange>
  <EnteredFromDate>0001-01-01T00:00:00</EnteredFromDate>
  <EnteredToDate>0001-01-01T00:00:00</EnteredToDate>
  <EnteredAsOfDate>0001-01-01T00:00:00</EnteredAsOfDate>
  <QuoteId>0</QuoteId>
  <AgentNo>0</AgentNo>
  <CarrierNo>0</CarrierNo>
  <PolicyNo />
  <StatusId>1</StatusId>
  <TaskStatusId>0</TaskStatusId>
  <LastActivityId>0</LastActivityId>
  <TaskActionId>0</TaskActionId>
  <LastActivityDateRange>...</LastActivityDateRange>
  <LastActivityFromDate>0001-01-01T00:00:00</LastActivityFromDate>
  <LastActivityToDate>0001-01-01T00:00:00</LastActivityToDate>
  <LastActivityAsOfDate>0001-01-01T00:00:00</LastActivityAsOfDate>
  <TaskDueDateRange>...</TaskDueDateRange>
  <TaskDueFromDate>0001-01-01T00:00:00</TaskDueFromDate>
  <TaskDueToDate>0001-01-01T00:00:00</TaskDueToDate>
  <TaskDueAsOfDate>0001-01-01T00:00:00</TaskDueAsOfDate>
  <SelWordFilterOption>Contains</SelWordFilterOption>
  <SearchForQuoteNumber>0</SearchForQuoteNumber>
  <SearchForValue>wind rose transport</SearchForValue>
  <SelectedSearchByOption>1</SelectedSearchByOption>
</QuoteSearchCriteria>
```

The full preference list is retrievable via `GetAllSearchPreferences` for re-inspection.

## The strange artifact

`GetQuotesForLookupByCriteria` and `GetQuotes` honor the Criteria filter (count narrows correctly) but always return empty data arrays in the wire response. `GetQuotesByName2` always returns Fault `"Object reference not set to an instance of an object."` regardless of request shape — a server-side NullRef. Three different ops, three different broken behaviors with the same Criteria payload. The captured Unisoft UI sessions don't include any of these three ops at all — strongly suggesting **the desktop UI uses a different path entirely.**

## Recommended next-session start

1. **(Craig action, 5 min)** Fire up Fiddler (or whatever HTTP capture tool runs against the Unisoft Windows desktop client). Open Unisoft UAT desktop UI. Search for a quote by insured name (any name that returns results). Save the SAZ file. Drop it into `projects/gic-email-intelligence/research/unisoft-api/` (alongside the existing export1.saz/export2.saz this corpus came from).
2. **(Claude session)** Pick up here:
   - Read this artifact end-to-end
   - Read the captured SAZ → identify the new op + service + request shape
   - Three plausible outcomes (in order of likelihood based on existing evidence):
     - **(a) `IReportingService.GetQuotesReport`** at `services.uat.gicunderwriters.co/reports/reportingservice.svc`. Add a `ReportingBridge` to `unisoft-proxy/server/UniProxy.cs` parallel to the existing `EmailBridge` (commit `a42bbe1` is the template). New WCF channel + `GetToken` flow + route `/api/reporting/<op>` to it. Wire the proxy. Estimated 1–2 hours.
     - **(b) A SOAP op we already tested** but with a magic flag, an alternate field combination in Criteria, or a different token. Match it. ~15 min.
     - **(c) A REST endpoint on a host we haven't probed.** The captures show two we haven't explored: `ins-gic-users-api-uat-app.azurewebsites.net` and `ins-gic-nothub-prod-app.azurewebsites.net`. Wrap with a JWT-authed proxy route. ~30 min.
3. Once data return works, resume the USLI implementation plan at **Phase C.1** (`unisoft quote search --name`). Everything downstream is unaffected by this finding.

## Files / artifacts to read for resumption

- This artifact (start here)
- `projects/gic-email-intelligence/artifacts/2026-04-29-usli-quote-automation-design.md` — feature design (workflow, scope, decisions). Still valid except the Phase 2 "find the Quote" step.
- `projects/gic-email-intelligence/artifacts/2026-04-29-usli-quote-automation-implementation-plan.md` — implementation plan. Phase B.2's earlier conclusion that "search returns empty arrays" was correct as a symptom but the inferred cause (permissions) and proposed pivot (Option A — JC provides Quote ID) were wrong. Don't apply Option A.
- `projects/gic-email-intelligence/research/unisoft-api/operations-index.md` — 89 captured SOAP ops, 19 REST endpoints, 3 SignalR captures.
- `projects/gic-email-intelligence/research/unisoft-api/wsdl-complete.md` — 910 SOAP ops in WSDL. Use grep for specific DTOs (`QuoteListRequest`, `QuoteSearchCriteriaDTO`, `LoginRequest`, `TokenRequest`).
- The new SAZ Craig will capture (path TBD, expect `research/unisoft-api/<filename>.saz`).

## What was NOT tried (intentionally — would need code change + redeploy)

- **`RequestedByUserName` injection** in the proxy. Today's `JsonToXml` at `UniProxy.cs:1899` hardcodes `<RequestedByUserName i:nil="true"/>`. Theory was that filling this with `ccerto` might unlock data return. Not tested because it requires modifying the proxy, redeploying to UAT, and the SAZ-capture path is a much higher information-to-effort ratio.
- **`IReportingService` routing** in the proxy. The existing proxy only has channels for IIMSService and IEmailService. Quote-search-via-reporting-service can't be tested without adding `ReportingBridge`. Defer until SAZ confirms it's the right path.
- **WS-UsernameToken** auth header alongside the SCT. Speculative.

These are the post-SAZ paths if the SAZ confirms one of them is the answer.

## Hard constraints for the next session

- **No prod proxy changes.** UAT proxy on `i-0dc2563c9bc92aa0e` port 5000 is fair game; prod proxy on the same instance port 5001 (`UniProxy-Prod.exe`) must remain untouched. The `/api/soap_raw/<op>` debug endpoint we deployed on 2026-04-30 is UAT-only. (Verified in commit `3143886` log.)
- **Read-only against UAT.** All probes today were GET-shape SOAP reads. Any write tests against UAT need explicit approval first (per OS production-safety rule).
- **Don't trust the prior 04-29 handoff's "Option A" framing.** It misrepresented Craig's call. The agreed direction was paths B + C (fix the proxy / find a different op), pointing at the research corpus. Today's investigation IS the execution of that direction; it concluded by surfacing the SAZ-capture need.

## Status of related work

- **USLI feature build** — paused at Phase B.2. Phases A and B.1 are done and committed on `feat/usli-quote-automation`. No further work until the search blocker resolves. Branch state: 5 commits ahead of `indemn/main`, clean working tree.
- **Sibling PRs (DEVOPS-163, 164, 165)** — independent of this. Can ship anytime per the implementation plan's sibling-PR section.
- **DEVOPS-158 7-day soak** — actively running. Phase H gates on it closing (~2026-05-06). Independent of this investigation.

## Linear

No new ticket created for this investigation. If Craig wants formal tracking, sub-issue under DEVOPS-162 ("USLI quote automation") titled "Resolve Unisoft quote-search wire format" with this artifact linked.

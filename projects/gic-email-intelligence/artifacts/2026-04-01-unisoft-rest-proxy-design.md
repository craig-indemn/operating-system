---
ask: "Design a REST API proxy that wraps Unisoft's WCF SOAP service, making all 910 operations callable via simple HTTP/JSON from our Python email intelligence pipeline"
created: 2026-04-01
workstream: gic-email-intelligence
session: 2026-04-01-b
sources:
  - type: web
    description: "Unisoft SOAP API surface mapped via Fiddler traffic interception on Windows EC2"
  - type: web
    description: "WCF client test — .NET Framework 4.8 WSHttpBinding proven working"
  - type: web
    description: "Research confirming WSHttpBinding not supported in modern .NET 6/7/8"
  - type: web
    description: "Raw Fiddler payloads for SetQuote, SetSubmission, SetActivity confirming nested DTO structure"
---

# Unisoft REST Proxy Design

## Problem

The Unisoft Insurance Management System (GIC's AMS) exposes a WCF SOAP service with 910 operations behind WSHttpBinding + WS-SecureConversation. This binding requires .NET Framework 4.8 — it is not supported in modern .NET or any non-.NET language. Our Python email intelligence pipeline needs to call these operations (SetQuote, SetSubmission, SetActivity, etc.) to automate data entry.

## Solution

A thin REST proxy running on a t3.small Windows EC2 instance. It accepts HTTP/JSON requests, translates them to SOAP/XML, calls the Unisoft service via a WCF channel that handles all WS-Security automatically, and returns JSON responses.

## Architecture

```
Python Pipeline (Railway)
    │
    │  POST /api/soap/SetQuote
    │  X-Api-Key: <key>
    │  { "Action": "Insert", "Quote": { "LOB": "CG", "Name": "..." } }
    │
    ▼
Unisoft REST Proxy (t3.small Windows EC2, port 5000)
    │
    │  - Validates API key
    │  - Injects AccessToken, ClientId, CompanyInitials, RequestId
    │  - Builds XML with correct DTO namespaces
    │  - Sends via WCF channel (WSHttpBinding + WS-SecureConversation + ReliableSession)
    │  - Converts XML response → JSON
    │
    ▼
Unisoft SOAP Service (services.uat.gicunderwriters.co/management/imsservice.svc)
```

Single C# file, compiled with `csc.exe`, no dependencies beyond .NET Framework 4.8 GAC assemblies. Runs as a Windows Service for production persistence.

### Scope

The proxy covers **IIMSService only** (910 operations). Two other services are out of scope:
- **IINSFileService** (attachments/insfileservice.svc) — 7 operations, uses MTOM multipart for file uploads. Would require a separate endpoint pattern (`multipart/form-data`). Not needed for the email pipeline's immediate scope.
- **IReportingService** (reports/reportingservice.svc) — 10+ operations. Separate WCF channel. Can be added later if needed.

### Three Logical Layers

1. **HTTP listener** — `HttpListener` on port 5000. Accepts requests, routes by URL pattern, returns JSON.
2. **Token manager** — Calls GetToken on startup, caches AccessToken, refreshes on expiry or auth failure, injects into every SOAP call.
3. **SOAP bridge** — One persistent WCF channel with keepalive. Converts caller's JSON to XML request body with correct DTO namespaces, sends via `ProcessMessage`, converts XML response to JSON.

### Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/soap/{OperationName}` | Generic passthrough for any IIMSService operation |
| GET | `/api/health` | Proxy status, token age, channel state, uptime, last request time |
| GET | `/api/meta/operations` | Lists available operations |

## JSON↔XML Translation

### The Nested DTO Structure

Unisoft SOAP operations use a **two-level request structure**. The `<request>` element contains:
1. **RequestBase fields** (flat) — `AccessToken`, `ClientId`, `CompanyInitials`, `IsDeveloper`, `RequestId`, `RequestedByUserName`, `Version` + operation-specific scalar fields like `Action`, `IsNewSystem`
2. **Named DTO child elements** (nested, namespaced) — The actual data payload lives inside a named element with its own DataContract namespace

This was confirmed by examining the raw Fiddler captures for SetQuote, SetSubmission, and SetActivity.

### Inbound (JSON → XML)

**For read operations** (Get*), the request is typically just the RequestBase fields plus a few scalar parameters (e.g., `QuoteId`, `LOB`). The proxy emits these as flat children of `<request>` with `xmlns=""`.

**For write operations** (Set*), the caller sends JSON with the DTO as a nested object:

```json
{
    "Action": "Insert",
    "IsNewSystem": true,
    "Quote": {
        "LOB": "CG",
        "SubLOB": "AC",
        "Name": "Test Corp",
        "AgentNumber": 777,
        "Address": "123 Main St",
        "City": "Miami",
        "State": "FL",
        "Zip": "33155"
    }
}
```

The proxy produces:

```xml
<SetQuote xmlns="http://tempuri.org/">
    <request xmlns:i="http://www.w3.org/2001/XMLSchema-instance">
        <AccessToken xmlns="">7141a4a4-...</AccessToken>
        <ClientId xmlns="">GIC_UAT</ClientId>
        <CompanyInitials xmlns="">GIC_UAT</CompanyInitials>
        <IsDeveloper xmlns="">false</IsDeveloper>
        <RequestId xmlns="">a1b2c3d4-...</RequestId>
        <RequestedByUserName i:nil="true" xmlns=""/>
        <Version i:nil="true" xmlns=""/>
        <Action xmlns="">Insert</Action>
        <IsNewSystem xmlns="">true</IsNewSystem>
        <Quote xmlns="" xmlns:b="http://schemas.datacontract.org/2004/07/Unisoft.Insurance.Services.DTO.Quotes">
            <b:LOB>CG</b:LOB>
            <b:SubLOB>AC</b:SubLOB>
            <b:Name>Test Corp</b:Name>
            <b:AgentNumber>777</b:AgentNumber>
            <b:Address>123 Main St</b:Address>
            <b:City>Miami</b:City>
            <b:State>FL</b:State>
            <b:Zip>33155</b:Zip>
        </Quote>
    </request>
</SetQuote>
```

### DTO Namespace Registry

The proxy maintains a mapping of DTO field names to their DataContract namespaces. When it encounters a JSON key that matches a known DTO name, it wraps the child object in the correct namespaced element:

| JSON Key | DTO Namespace |
|----------|---------------|
| `Quote` | `http://schemas.datacontract.org/2004/07/Unisoft.Insurance.Services.DTO.Quotes` |
| `QuoteActivity` | `http://schemas.datacontract.org/2004/07/Unisoft.Insurance.Services.DTO.Quotes` |
| `QuoteStatus` | `http://schemas.datacontract.org/2004/07/Unisoft.Insurance.Services.DTO.Quotes` |
| `Submission` | `http://schemas.datacontract.org/2004/07/Unisoft.Insurance.Services.DTO.Quotes.Submissions` |
| `Activity` | `http://schemas.datacontract.org/2004/07/Unisoft.Insurance.Services.DTO.Activities` |
| `CashDetail` | `http://schemas.datacontract.org/2004/07/Unisoft.Insurance.Services.DTO.Cash` |
| `PolicyEntry` | `http://schemas.datacontract.org/2004/07/Unisoft.Insurance.Services.DTO.PolicyInquiry` |

**Sub-DTOs within DTOs:** Some DTOs contain nested sub-DTOs with their own namespaces (e.g., `Activity` contains `Action` from `...DTO.Actions` and `Task` from `...DTO.Tasks`; `Quote` contains `Policy` from `...DTO.PolicyInquiry`). In write requests, these sub-DTOs are sent as `i:nil="true"` — the server populates them in the response. If a future operation requires sending populated sub-DTOs, the registry will need nesting-aware extension. The response deserializer handles sub-DTOs via namespace stripping and does not need the registry.

**DTO wrapper elements** carry both `xmlns=""` (resetting the default namespace from `http://tempuri.org/`) and `xmlns:b="..."` (the DataContract namespace for child fields).

For JSON keys not in the registry, the proxy emits them as flat `xmlns=""` elements (the RequestBase pattern). This means:
- **Known DTO operations** (SetQuote, SetSubmission, etc.) get correct namespacing automatically
- **Generic read operations** (GetInsuranceLOBs, GetCarriersForLookup, etc.) work as flat requests
- **Unknown operations** still work via the generic passthrough — caller can include the full nested XML structure if needed by passing a `_rawXml` field

The registry is populated from the captured Fiddler payloads and can be extended as we discover new operations that need DTO wrapping. This is a hardcoded dictionary, not WSDL parsing — simple and sufficient.

### Translation Rules

- `null` JSON values → `i:nil="true"` attribute (explicit null, not empty string)
- Absent JSON keys → omitted from XML (WCF treats absent elements as default)
- Numbers → rendered as strings in XML (Unisoft handles type coercion server-side)
- Nested JSON objects → nested XML elements (with DTO namespace if in registry)
- JSON arrays → repeated XML elements with the same tag name
- PascalCase field names passed through as-is

### Outbound (XML → JSON)

Strip SOAP body wrapper, convert result element to JSON. Standard ResponseBase fields go in `_meta`:

```json
{
    "_meta": { "ReplyStatus": "Success", "CorrelationId": "...", "RowsAffected": 0 },
    "InsuranceLOBs": [
        { "Description": "General Liability", "LOB": "CG", "SubLines": null },
        ...
    ]
}
```

**ResponseBase fields** (always extracted to `_meta`): `Build`, `CorrelationId`, `Message`, `ReplyStatus`, `RowsAffected`, `Version`.

**Collection handling:** XML elements whose child tags match a `*DTO` pattern (e.g., `InsuranceLOBDTO`, `CarrierForLookupDTO`) are always emitted as JSON arrays, even when containing 0 or 1 elements. This prevents the single-element-vs-array ambiguity that would break Python client code.

**Null handling:** Both `i:nil="true"` elements and empty placeholder collections (e.g., `<Quotes i:nil="true" .../>`) map to `null` in JSON. The Python pipeline does not need to distinguish between null and empty string.

**Namespace stripping:** All XML namespace prefixes and declarations are stripped. `<b:LOB>CG</b:LOB>` becomes `"LOB": "CG"`.

### SOAP Fault → HTTP Error Mapping

| SOAP Fault | HTTP Status | JSON Body |
|------------|-------------|-----------|
| Auth-related / NullReference on missing token | 502 | `{"error": "unisoft_fault", "message": "...", "faultCode": "..."}` |
| Validation / business logic fault | 422 | `{"error": "unisoft_validation", "message": "...", "detail": "..."}` |
| Operation not found | 400 | `{"error": "bad_request", "message": "Unknown operation"}` |
| Proxy internal error | 500 | `{"error": "proxy_error", "message": "..."}` |
| Channel busy (lock timeout) | 503 | `{"error": "busy", "message": "...", "retryAfter": 5}` |
| Invalid API key | 401 | `{"error": "unauthorized"}` |

## Token & Channel Management

### Startup Sequence

1. Create `WSHttpBinding` with:
   - `Security.Mode = TransportWithMessageCredential`
   - `Security.Message.ClientCredentialType = UserName`
   - `Security.Message.EstablishSecurityContext = true`
   - `ReliableSession.Enabled = true`
   - `ReliableSession.InactivityTimeout = TimeSpan.FromMinutes(10)`
2. Create `ChannelFactory<IIMSService>` with UsernameToken credentials
3. Configure TLS: `ServicePointManager.SecurityProtocol = Tls12`. Certificate validation controlled by `UNISOFT_SKIP_CERT_VALIDATION` env var (default `false`; set `true` for UAT only)
4. Open channel (WS-SecureConversation + WS-ReliableMessaging handshake)
5. Call `GetToken(GIC_UAT)` → cache AccessToken
6. Start keepalive timer
7. Start HTTP listener

### Token Refresh

- Proactive refresh every 20 minutes via timer
- On auth-related SOAP fault → refresh token, retry the failed call once
- Token stored in `volatile string` field — no persistence needed
- Token refresh does NOT hold the channel lock — it uses the channel like any other call, then atomically swaps the token value

### Channel Keepalive

A timer fires every 5 minutes and calls `GetToken` (lightweight operation) to prevent the ReliableSession and SecurityContextToken from expiring due to inactivity. The keepalive:
- Prevents the 10-minute ReliableSession inactivity timeout
- Validates the channel is still healthy
- If the keepalive call faults, triggers immediate channel recreation

### Channel Resilience

- On channel fault → create new channel instance from the existing `ChannelFactory`, re-authenticate via GetToken
- `ChannelFactory` is reused; only the channel instance is replaced
- Channel recreation uses compare-and-swap on a generation counter — only one thread performs recreation, others wait
- Invisible to caller — they get success or an error JSON

### Concurrency & Locking

Two separate locks with distinct purposes:

1. **Token lock** (`object tokenLock`) — Guards the token value swap. Held for sub-milliseconds (just a field assignment). Token refresh acquires this lock to write; SOAP calls acquire it to read. No contention.

2. **Channel lock** (`SemaphoreSlim channelSem = new SemaphoreSlim(1, 1)`) — Serializes WCF channel calls since channels are not thread-safe. Acquired with a timeout (30 seconds). If the semaphore times out, the caller gets HTTP 503 with `Retry-After: 5`. This prevents cascading timeouts when a slow SOAP call blocks the channel.

The channel lock and token lock are never held simultaneously — no deadlock risk.

For our volume (a few calls per minute at peak), serialized channel access is fine. If concurrency becomes an issue, the semaphore can be increased to allow N concurrent channels from a pool.

## Deployment

### Infrastructure

| Item | Value |
|------|-------|
| Instance | t3.small (2 vCPU, 2GB RAM) — downsized from current t3.xlarge |
| OS | Windows Server 2025 |
| IP | Elastic IP (stable across restarts) |
| Cost | ~$35/month (compute + Windows license + EIP) |
| Security group | Port 5000 open to Railway static IP + dev machines only |

**Why t3.small:** Windows Server 2025 idles at ~800-900MB. The WCF runtime (WS-SecureConversation security tokens, ReliableMessaging buffers, message processing) needs ~200-300MB headroom. t3.micro (1GB) is too tight; t3.small (2GB) provides breathing room for spikes like the 3,142-agent lookup response.

### Windows Service

- Compiled as a Windows Service via `ServiceBase` (in GAC, no installer needed)
- Service account: `LocalSystem` (default for `sc create`; acceptable for single-purpose proxy)
- URL ACL registration: `netsh http add urlacl url=http://+:5000/ user="NT AUTHORITY\SYSTEM"`
- Registration: `sc create UniProxy binPath= C:\unisoft\UniProxy.exe start= auto`
- Failure recovery: `sc failure UniProxy reset= 86400 actions= restart/5000/restart/10000/restart/30000`
- Auto-start on boot, restart on failure (5s, 10s, 30s backoff)

### Logging

- Structured JSON logs, one object per line: `{"ts": "...", "op": "SetQuote", "duration_ms": 234, "status": "success", "action": "..."}`
- Log file: `C:\unisoft\logs\proxy-YYYY-MM-DD.log` (daily rotation)
- Max size: 50MB per file, retain 30 days
- SOAP action logged on every call (helps debug unknown operations)
- CloudWatch Logs agent optional — install later if needed for remote monitoring

### Configuration

All via environment variables (set in system environment, persist across restarts):

| Variable | Purpose | Default |
|----------|---------|---------|
| `UNISOFT_SOAP_URL` | SOAP service endpoint | UAT URL |
| `UNISOFT_WS_USER` | WS-Security username | — |
| `UNISOFT_WS_PASS` | WS-Security password | — |
| `UNISOFT_CLIENT_ID` | GetToken ClientId/CompanyInitials | GIC_UAT |
| `UNISOFT_SKIP_CERT_VALIDATION` | Accept any TLS cert (UAT only) | false |
| `PROXY_API_KEY` | Caller authentication key | — |
| `PROXY_PORT` | Listen port | 5000 |
| `PROXY_MAX_REQUEST_BYTES` | Max inbound request body size | 5242880 (5MB) |

### UAT vs Production

Same proxy code, different env vars. When Unisoft provides production API endpoints, change `UNISOFT_SOAP_URL`, credentials, and set `UNISOFT_SKIP_CERT_VALIDATION=false`.

## Known Limitations

1. **IIMSService only** — File attachments (IINSFileService, MTOM multipart) and reports (IReportingService) require separate channels and are not supported. Can be added as `/api/files/{Op}` and `/api/reports/{Op}` later.
2. **Serialized channel access** — One SOAP call at a time. A slow response (e.g., GetAgentsAndProspectsForLookup, ~1-2s) blocks other callers. Acceptable for current volume. Channel pooling can be added if needed.
3. **DTO namespace registry is manual** — New write operations may require adding entries to the registry. The WSDL has 1,668 complex types; parsing it at build time is possible but not worth the complexity given we need ~10 operations.
4. **First call after idle may be slow** — If the keepalive fails to prevent session expiry, channel recreation adds 2-5 seconds. The keepalive timer (5 min) should prevent this in normal operation.

## What Was Proven

- REST API (JWT auth): fully working from Python — 4/4 tests passed
- SOAP WCF channel: opens successfully with WSHttpBinding + WS-SecureConversation + ReliableSession
- GetToken → AccessToken flow: working
- GetInsuranceLOBs with token: returns all 18 LOBs
- GetCarriersForLookup: returns all 46 carriers
- GetAgentsAndProspectsForLookup: returns all 3,142 agents
- GetQuoteActions: returns ~75 activity types
- Generic `ProcessMessage` pattern: works for any operation (14 tested)
- WSHttpBinding is NOT supported in .NET 6/7/8 — .NET Framework 4.8 required
- SetQuote, SetSubmission, SetActivity request bodies confirmed as nested DTO structures with DataContract namespaces (from Fiddler captures)

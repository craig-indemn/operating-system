# Unisoft REST Proxy

REST proxy that wraps the Unisoft WCF SOAP service (910 operations) via HTTP/JSON. Runs as a Windows Service on EC2.

## Why This Exists

Unisoft's SOAP service uses WSHttpBinding with WS-SecureConversation — a .NET Framework 4.8-only protocol. No modern language or runtime can call it directly. This proxy handles all WS-Security, token management, and XML translation so our Python pipeline just sends JSON.

## Infrastructure

| Item | Value |
|------|-------|
| EC2 Instance | `i-0dc2563c9bc92aa0e` |
| Instance Type | t3.small (2 vCPU, 2GB RAM) |
| OS | Windows Server 2025 Datacenter |
| Elastic IP | `54.83.28.79` |
| Proxy URL | `http://54.83.28.79:5000` |
| Windows Service | `UniProxy` (auto-start, failure recovery) |
| Security Group | `sg-04cc0ee7a09c15ffb` — port 5000 open to Railway (`162.220.234.15/32`) + dev |
| Cost | ~$35/month (compute + Windows license + EIP) |
| Code | `UniProxy.cs` (single file, ~1,100 lines C#) |
| Compiled binary | `C:\unisoft\UniProxy.exe` on EC2 |
| Logs | `C:\unisoft\logs\proxy-YYYY-MM-DD.log` on EC2 |

## API Contract

### Health Check

```
GET /api/health
```

No auth required. Returns:

```json
{
    "status": "ok",
    "uptime_seconds": 3600,
    "requests": 42,
    "token_age_seconds": 300,
    "channel_state": "healthy",
    "last_request_time": "2026-04-01T20:00:00Z"
}
```

### SOAP Operation (Generic)

```
POST /api/soap/{OperationName}
X-Api-Key: <key>
Content-Type: application/json
```

The proxy supports all 910 IIMSService operations. The operation name is case-sensitive and matches the WSDL (e.g., `GetInsuranceLOBs`, `SetQuote`, `GetCarriersForLookup`).

**For read operations** — send flat JSON with any parameters:

```bash
curl -X POST http://54.83.28.79:5000/api/soap/GetInsuranceLOBs \
  -H "X-Api-Key: $KEY" -H "Content-Type: application/json" \
  -d '{}'

curl -X POST http://54.83.28.79:5000/api/soap/GetInsuranceSubLOBs \
  -H "X-Api-Key: $KEY" -H "Content-Type: application/json" \
  -d '{"LOB": "CG"}'
```

**For write operations** — send the DTO as a nested object:

```bash
curl -X POST http://54.83.28.79:5000/api/soap/SetQuote \
  -H "X-Api-Key: $KEY" -H "Content-Type: application/json" \
  -d '{
    "Action": "Insert",
    "IsNewSystem": true,
    "Quote": {
      "Address": "100 Test Street",
      "AgentNumber": 777,
      "City": "Miami",
      "EffectiveDate": "2026-07-01T00:00:00",
      "ExpirationDate": "2027-07-01T00:00:00",
      "FormOfBusiness": "C",
      "LOB": "CG",
      "Name": "Test Corp",
      "OriginatingSystem": "UIMS",
      "PolicyState": "FL",
      "QuoteType": "N",
      "State": "FL",
      "Status": "1",
      "SubLOB": "AC",
      "Term": 12,
      "Zip": "33155"
    }
  }'
```

**Response format:**

```json
{
    "_meta": {
        "ReplyStatus": "Success",
        "CorrelationId": "...",
        "RowsAffected": 1,
        "Build": 0,
        "Message": null,
        "Version": 1.0
    },
    "Quote": { ... },
    "Quotes": null,
    "QuotesForLookup": null
}
```

### Operations Metadata

```
GET /api/meta/operations
```

No auth required. Returns service info.

### Error Responses

| HTTP Status | Meaning |
|-------------|---------|
| 200 | Success |
| 401 | Invalid or missing `X-Api-Key` |
| 413 | Request body too large (>5MB) |
| 422 | Unisoft validation error (bad field values) |
| 500 | Proxy internal error |
| 502 | Unisoft SOAP fault (auth, server error) |
| 503 | Channel busy (retry after 5s) |

Error body is always JSON:

```json
{"error": "unisoft_validation", "message": "Name is a required field.", "detail": "...", "faultCode": "..."}
```

## Python Client

```python
from unisoft_client import UnisoftClient

client = UnisoftClient("http://54.83.28.79:5000", api_key="...")

# Read operations
lobs = client.get_lobs()                    # 18 LOBs
subs = client.get_sub_lobs("CG")            # 4 sub-LOBs for General Liability
carriers = client.get_carriers()             # 46 carriers
agents = client.get_agents()                 # 1,571 agents

# Write operations
quote = client.create_quote({
    "Address": "100 Test St", "AgentNumber": 777, "City": "Miami",
    "EffectiveDate": "2026-07-01T00:00:00", "ExpirationDate": "2027-07-01T00:00:00",
    "FormOfBusiness": "C", "LOB": "CG", "Name": "Test Corp",
    "OriginatingSystem": "UIMS", "PolicyState": "FL", "QuoteType": "N",
    "State": "FL", "Status": "1", "SubLOB": "AC", "Term": 12, "Zip": "33155"
})
quote_id = quote["Quote"]["QuoteID"]

submission = client.create_submission({
    "BrokerId": 1, "CarrierNo": 2, "Description": "GL Test",
    "EffectiveDate": "2026-07-01T00:00:00", "EnteredByUser": "ccerto",
    "ExpirationDate": "2027-07-01T00:00:00", "MgaNo": 1,
    "QuoteId": quote_id, "SubmissionId": 0, "SubmissionNo": 0
})

activity = client.create_activity({
    "ActionId": 178, "ActivityId": 0, "AgentNo": 777,
    "LoggedByUser": "ccerto", "LoggedDate": "2026-04-01T20:00:00",
    "QuoteId": quote_id, "SectionId": 5,
    "SubmissionId": submission["Submission"]["SubmissionId"]
})

# Any operation
result = client.call("GetCompanyRules")
```

## Critical Implementation Details

### Parameter names are CASE-SENSITIVE

WCF DataContract field names are case-sensitive. `QuoteID` works, `QuoteId` silently returns null/zero. The proxy passes JSON keys through to XML element names without modification. Always match the exact casing from the WSDL. Common gotcha: `QuoteID` (capital D), not `QuoteId`.

### DTO fields MUST be alphabetical

WCF DataContractSerializer silently ignores out-of-order fields. If you send `{"Name": "...", "Address": "..."}`, the proxy sorts them to `Address, Name` before serializing. This sorting happens automatically in the proxy — callers don't need to worry about it.

### Known DTO namespaces

Write operations wrap their data payload in a namespaced XML element. The proxy knows these mappings:

| JSON Key | Wraps Into |
|----------|-----------|
| `Quote` | `Unisoft.Insurance.Services.DTO.Quotes` |
| `QuoteActivity` | `Unisoft.Insurance.Services.DTO.Quotes` |
| `QuoteStatus` | `Unisoft.Insurance.Services.DTO.Quotes` |
| `Submission` | `Unisoft.Insurance.Services.DTO.Quotes.Submissions` |
| `Activity` | `Unisoft.Insurance.Services.DTO.Activities` |
| `CashDetail` | `Unisoft.Insurance.Services.DTO.Cash` |
| `PolicyEntry` | `Unisoft.Insurance.Services.DTO.PolicyInquiry` |

To add a new DTO: edit the `dtoNamespaces` dictionary in `UniProxy.cs`, recompile, redeploy.

### Token management is automatic

The proxy calls `GetToken` on startup and refreshes every 20 minutes. A keepalive call every 5 minutes prevents WCF session timeout. Callers never need to manage tokens.

### The proxy only covers IIMSService

The file service (`IINSFileService` — attachments) and reporting service (`IReportingService`) are separate WCF endpoints not covered by this proxy. They would need additional channels.

## Operations

### Check if the proxy is running

```bash
curl -4 http://54.83.28.79:5000/api/health
```

Or via SSM:

```bash
aws ssm send-command --instance-ids i-0dc2563c9bc92aa0e \
  --document-name "AWS-RunPowerShellScript" \
  --parameters '{"commands":["Get-Service UniProxy | Format-Table Name, Status, StartType"]}'
```

### Start / Stop / Restart the service

```bash
# Via SSM (preferred)
aws ssm send-command --instance-ids i-0dc2563c9bc92aa0e \
  --document-name "AWS-RunPowerShellScript" \
  --parameters '{"commands":["Restart-Service UniProxy"]}'

# Stop
aws ssm send-command ... --parameters '{"commands":["Stop-Service UniProxy"]}'

# Start
aws ssm send-command ... --parameters '{"commands":["Start-Service UniProxy"]}'
```

### View logs

```bash
# Last 20 log lines
aws ssm send-command --instance-ids i-0dc2563c9bc92aa0e \
  --document-name "AWS-RunPowerShellScript" \
  --parameters '{"commands":["Get-Content C:\\unisoft\\logs\\proxy-2026-04-01.log -Tail 20"]}'
```

Logs are structured JSON, one line per entry:

```json
{"ts":"2026-04-01T19:39:39.14Z","op":"SetQuote","status":200,"duration_ms":100}
```

### Deploy a code change

1. Edit `UniProxy.cs` locally
2. Upload → compile → restart:

```bash
# Upload to S3
aws s3 cp unisoft-proxy/UniProxy.cs s3://indemn-assets/unisoft/UniProxy.cs

# Generate presigned URL
PRESIGNED=$(aws s3 presign s3://indemn-assets/unisoft/UniProxy.cs --expires-in 300)

# Download, compile, restart on EC2 (single SSM command)
aws ssm send-command --instance-ids i-0dc2563c9bc92aa0e \
  --document-name "AWS-RunPowerShellScript" \
  --parameters "{\"commands\":[
    \"[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12\",
    \"Invoke-WebRequest -Uri '$PRESIGNED' -OutFile C:\\\\unisoft\\\\UniProxy.cs\",
    \"Stop-Service UniProxy -ErrorAction SilentlyContinue\",
    \"Start-Sleep -Seconds 3\",
    \"C:\\\\Windows\\\\Microsoft.NET\\\\Framework64\\\\v4.0.30319\\\\csc.exe /out:C:\\\\unisoft\\\\UniProxy.exe /reference:System.ServiceModel.dll /reference:System.Runtime.Serialization.dll /reference:System.ServiceProcess.dll /reference:System.Web.Extensions.dll /reference:System.Xml.dll C:\\\\unisoft\\\\UniProxy.cs\",
    \"Start-Service UniProxy\",
    \"Start-Sleep -Seconds 10\",
    \"Get-Service UniProxy | Select-Object -ExpandProperty Status\"
  ]}"
```

3. Verify: `curl -4 http://54.83.28.79:5000/api/health`

### Start / Stop the EC2 instance

```bash
# Stop (saves money — ~$0.03/hr when stopped, EIP costs $0.005/hr)
aws ec2 stop-instances --instance-ids i-0dc2563c9bc92aa0e

# Start
aws ec2 start-instances --instance-ids i-0dc2563c9bc92aa0e
# Service auto-starts — no action needed after boot
```

### Update security group (add new IP)

```bash
aws ec2 authorize-security-group-ingress --group-id sg-04cc0ee7a09c15ffb \
  --protocol tcp --port 5000 --cidr <NEW_IP>/32
```

### Environment variables

Set on the EC2 as system-level Machine environment variables. The proxy reads them via `EnvironmentVariableTarget.Machine` so they work for the Windows Service without inheriting from a parent process.

| Variable | Purpose | Current Value |
|----------|---------|---------------|
| `UNISOFT_SOAP_URL` | SOAP endpoint | `https://services.uat.gicunderwriters.co/management/imsservice.svc` |
| `UNISOFT_WS_USER` | WS-Security username | `UniClient` |
| `UNISOFT_WS_PASS` | WS-Security password | (see `research/unisoft-api-reference.md` "SOAP Auth" section) |
| `UNISOFT_CLIENT_ID` | GetToken client ID | `GIC_UAT` |
| `UNISOFT_SKIP_CERT_VALIDATION` | Skip TLS cert check | `true` (UAT only — set `false` for production) |
| `PROXY_API_KEY` | Caller auth key | (stored on EC2 only) |
| `PROXY_PORT` | Listen port | `5000` |

To change an env var:

```bash
aws ssm send-command --instance-ids i-0dc2563c9bc92aa0e \
  --document-name "AWS-RunPowerShellScript" \
  --parameters '{"commands":["[Environment]::SetEnvironmentVariable(\"VARIABLE_NAME\", \"new_value\", \"Machine\")","Restart-Service UniProxy"]}'
```

## Switching to Production

When Unisoft provides production API credentials:

1. Set new env vars on EC2:
   - `UNISOFT_SOAP_URL` → production endpoint
   - `UNISOFT_WS_USER` / `UNISOFT_WS_PASS` → production credentials
   - `UNISOFT_CLIENT_ID` → production client ID (likely `GIC` not `GIC_UAT`)
   - `UNISOFT_SKIP_CERT_VALIDATION` → `false`
2. Restart the service
3. Run integration tests against production

No code changes needed.

## Troubleshooting

**Proxy not responding:**
1. Check health: `curl -4 http://54.83.28.79:5000/api/health`
2. Check service: `Get-Service UniProxy` via SSM
3. Check logs: `Get-Content C:\unisoft\logs\proxy-*.log -Tail 50` via SSM
4. Check Windows Firewall: port 5000 must have an inbound allow rule (`UniProxy Port 5000`)
5. Check security group: your IP must be in `sg-04cc0ee7a09c15ffb` for port 5000

**Channel faulted / token errors:**
- Restart the service — it re-establishes the WCF channel and gets a fresh token
- If persistent, check if the Unisoft SOAP service is reachable from the EC2

**SOAP operation returns all null fields:**
- DTO fields must be in **alphabetical order** (proxy handles this automatically)
- If adding new DTO types, ensure the namespace is in the `dtoNamespaces` dictionary

**"Invalid or expired AccessToken":**
- The proxy auto-detects this and refreshes the token + retries the call automatically. If it persists, restart the service.
- Root cause (fixed): the keepalive was calling GetToken which invalidated the old token. Now uses GetSections for keepalive and only refreshes tokens reactively on auth failure.

**"Channel busy" (503):**
- A SOAP call is taking >30 seconds. Retry after 5s.
- If frequent, check Unisoft service health

**Compilation errors after code change:**
- C# 5 only — no string interpolation (`$""`), no null-conditional (`?.`), no expression-bodied members
- All assemblies must be GAC: `System.ServiceModel.dll`, `System.Runtime.Serialization.dll`, `System.ServiceProcess.dll`, `System.Web.Extensions.dll`, `System.Xml.dll`
- `TimeoutException` is ambiguous — use `System.TimeoutException`

## Reference Data (from UAT, 2026-04-01)

**18 Lines of Business:**
CV (Collector Vehicle), CP (Commercial Property), CU (Commercial Umbrella), EX (Excess Casualty), FL (Flood), GA (Garage), CG (General Liability), HO (Homeowners), IM (Inland Marine Commercial), IP (Inland Marine Personal), ML (Management Liability), OM (Ocean Marine), PI (Personal Liability), PU (Personal Umbrella), PA (Private Auto), PL (Professional Liability), TR (Transportation), WC (Workers Compensation)

**Key carrier numbers:** 2 = USLI, 1 = Mount Vernon Fire, 11 = AmTrust, 7 = Normandy, 3 = Lloyds

**Key broker IDs:** 1 = GIC Underwriters

**Key agent numbers:** 777 = test agent (GIC Office Quoted)

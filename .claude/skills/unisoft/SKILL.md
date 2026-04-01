---
name: unisoft
description: Create and manage quotes, submissions, and activities in Unisoft AMS (GIC's insurance management system) via REST proxy. Use when the email pipeline needs to write data into Unisoft, or when looking up LOBs, carriers, agents, or quote data.
---

# Unisoft AMS

Access GIC's Unisoft Insurance Management System (910 SOAP operations) via a REST proxy on EC2. The proxy handles all WCF WS-Security automatically.

## Status Check

```bash
curl-unisoft.sh GET health
```

Expected: `{"status":"ok","channel_state":"healthy",...}`

If the proxy is down, check the EC2 instance and service:
```bash
aws ec2 describe-instances --instance-ids i-0dc2563c9bc92aa0e --query 'Reservations[0].Instances[0].State.Name' --output text
# If stopped: aws ec2 start-instances --instance-ids i-0dc2563c9bc92aa0e
# Service auto-starts on boot. If not, restart via SSM:
# aws ssm send-command --instance-ids i-0dc2563c9bc92aa0e --document-name "AWS-RunPowerShellScript" --parameters '{"commands":["Restart-Service UniProxy"]}'
```

## Setup

Already deployed. No setup needed. Requires:
- `op` CLI authenticated (for API key from 1Password)
- `curl-unisoft.sh` on PATH (in `scripts/secrets-proxy/`)
- EC2 instance running (i-0dc2563c9bc92aa0e, Elastic IP 54.83.28.79)

## Usage

All calls go through `curl-unisoft.sh` which pulls the API key from 1Password.

### Read Operations

```bash
# All lines of business (18 LOBs)
curl-unisoft.sh POST GetInsuranceLOBs '{}'

# Sub-LOBs for a specific LOB
curl-unisoft.sh POST GetInsuranceSubLOBs '{"LOB": "CG"}'

# All carriers (46)
curl-unisoft.sh POST GetCarriersForLookup '{}'

# All agents (1,571)
curl-unisoft.sh POST GetAgentsAndProspectsForLookup '{}'

# Quote actions (activity types)
curl-unisoft.sh POST GetQuoteActions '{}'

# Get submissions for a quote
curl-unisoft.sh POST GetSubmissions '{"QuoteId": 17130}'

# Get activities for a quote
curl-unisoft.sh POST GetActivitiesByQuoteId '{"QuoteId": 17130}'
```

### Write Operations

Write operations require the DTO as a nested JSON object. The proxy handles alphabetical field ordering and XML namespace mapping automatically.

```bash
# Create a quote
curl-unisoft.sh POST SetQuote '{
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

# Add a submission to a quote (carrier + broker assignment)
curl-unisoft.sh POST SetSubmission '{
  "PersistSubmission": "Insert",
  "Submission": {
    "BrokerId": 1,
    "CarrierNo": 2,
    "Description": "GL Artisans",
    "EffectiveDate": "2026-07-01T00:00:00",
    "EnteredByUser": "ccerto",
    "ExpirationDate": "2027-07-01T00:00:00",
    "MgaNo": 1,
    "QuoteId": 17130,
    "SubmissionId": 0,
    "SubmissionNo": 0
  }
}'

# Log an activity on a submission
curl-unisoft.sh POST SetActivity '{
  "Action": "Insert",
  "Activity": {
    "ActionId": 178,
    "ActivityId": 0,
    "AgentNo": 777,
    "LoggedByUser": "ccerto",
    "LoggedDate": "2026-04-01T20:00:00",
    "QuoteId": 17130,
    "SectionId": 5,
    "SubmissionId": 15444
  }
}'
```

### Python Client

For programmatic access from the email pipeline:

```python
import sys
sys.path.insert(0, "projects/gic-email-intelligence/unisoft-proxy/client")
from unisoft_client import UnisoftClient
import subprocess

# Get API key from 1Password
api_key = subprocess.check_output(
    ["op", "read", "op://cli-secrets/Unisoft Proxy API Key/credential"],
    text=True
).strip()

client = UnisoftClient("http://54.83.28.79:5000", api_key=api_key)
lobs = client.get_lobs()
quote = client.create_quote({"LOB": "CG", "Name": "...", ...})
```

### Response Format

All responses have `_meta` (status info) and data fields:

```json
{
  "_meta": {"ReplyStatus": "Success", "CorrelationId": "...", "RowsAffected": 1},
  "Quote": { ... }
}
```

Errors return appropriate HTTP status codes (401, 422, 502, 503).

## Key Reference Data

| Code | LOB |
|------|-----|
| CG | General Liability (sub: AC, LL, HM, SE) |
| CP | Commercial Property (13 sub-LOBs) |
| TR | Transportation (includes Commercial Auto as sub-LOB CA) |
| PI | Personal Liability |
| PL | Professional Liability (8 sub-LOBs) |
| OM | Ocean Marine (includes Boats & Yachts as sub-LOB BY) |

**Carriers:** 2=USLI, 1=Mount Vernon Fire, 11=AmTrust, 7=Normandy, 3=Lloyds (46 total)
**Brokers:** 1=GIC Underwriters (16 total)
**Agents:** 777=GIC Office Quoted (1,571 total)

## Operational Details

Full operational docs (deploy, troubleshoot, EC2 management): `projects/gic-email-intelligence/unisoft-proxy/README.md`

Design doc: `projects/gic-email-intelligence/artifacts/2026-04-01-unisoft-rest-proxy-design.md`

Proxy code: `projects/gic-email-intelligence/unisoft-proxy/UniProxy.cs`

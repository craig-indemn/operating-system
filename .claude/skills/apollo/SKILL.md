---
name: apollo
description: Search companies, enrich contacts, and access sales intelligence via Apollo.io REST API. Use for prospecting, company research, and contact data.
---

# Apollo.io

Company enrichment, contact search, and sales intelligence via REST API with curl.

## Status Check

```bash
[ -n "$APOLLO_API_KEY" ] && echo "TOKEN SET" || echo "APOLLO_API_KEY not set"
```

Verify access:
```bash
curl -s -X POST "https://api.apollo.io/api/v1/auth/health" \
  -H "Content-Type: application/json" \
  -H "Cache-Control: no-cache" \
  -d "{\"api_key\": \"$APOLLO_API_KEY\"}" | head -c 200 && echo " — AUTHENTICATED" || echo "AUTH FAILED"
```

## Setup

1. Go to Apollo.io > Settings > Integrations > API
2. Copy your API key
3. Set environment variable:
```bash
export APOLLO_API_KEY="..."
```
Add to `~/.zshrc` to persist. Requires a paid Apollo plan.

## Usage

### Enrich a person by email
```bash
curl -s -X POST "https://api.apollo.io/api/v1/people/match" \
  -H "Content-Type: application/json" \
  -H "Cache-Control: no-cache" \
  -d "{\"api_key\": \"$APOLLO_API_KEY\", \"email\": \"person@company.com\"}" | jq '.'
```

### Search people
```bash
curl -s -X POST "https://api.apollo.io/api/v1/mixed_people/search" \
  -H "Content-Type: application/json" \
  -d "{
    \"api_key\": \"$APOLLO_API_KEY\",
    \"q_organization_name\": \"INSURICA\",
    \"person_titles\": [\"VP\", \"Director\"],
    \"per_page\": 10
  }" | jq '.people[] | {name: .name, title: .title, email: .email}'
```

### Search companies
```bash
curl -s -X POST "https://api.apollo.io/api/v1/mixed_companies/search" \
  -H "Content-Type: application/json" \
  -d "{
    \"api_key\": \"$APOLLO_API_KEY\",
    \"q_organization_name\": \"Jewelers Mutual\",
    \"per_page\": 5
  }" | jq '.organizations[] | {name: .name, industry: .industry, employee_count: .estimated_num_employees}'
```

### Enrich a company by domain
```bash
curl -s -X POST "https://api.apollo.io/api/v1/organizations/enrich" \
  -H "Content-Type: application/json" \
  -d "{\"api_key\": \"$APOLLO_API_KEY\", \"domain\": \"insurica.com\"}" | jq '.'
```

### Bulk people enrichment
```bash
curl -s -X POST "https://api.apollo.io/api/v1/people/bulk_match" \
  -H "Content-Type: application/json" \
  -d "{
    \"api_key\": \"$APOLLO_API_KEY\",
    \"details\": [
      {\"email\": \"person1@company.com\"},
      {\"email\": \"person2@company.com\"}
    ]
  }" | jq '.'
```

For full API reference and common query patterns, see `references/api-spec.md`.

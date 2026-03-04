---
name: apollo
description: Search companies, enrich contacts, and access sales intelligence via Apollo.io REST API. Use for prospecting, company research, and contact data.
---

# Apollo.io

Company enrichment, contact search, and sales intelligence via REST API with curl.

## Status Check

```bash
curl-apollo.sh /api/v1/auth/health '{}' | python3 -c "import sys,json; print('AUTHENTICATED' if json.load(sys.stdin).get('is_logged_in') else 'AUTH FAILED')"
```

## Setup

1. Go to Apollo.io > Settings > Integrations > API
2. Copy your API key
3. Store in 1Password:
```bash
op item create --vault "indemn-os" --category "API Credential" --title "Apollo API Key" credential="..."
```
Requires a paid Apollo plan.

## Usage

All commands use `curl-apollo.sh` which injects the API key from 1Password into the request body.

### Enrich a person by email
```bash
curl-apollo.sh /api/v1/people/match '{"email": "person@company.com"}' | jq '.'
```

### Search people
```bash
curl-apollo.sh /api/v1/mixed_people/search '{
  "q_organization_name": "INSURICA",
  "person_titles": ["VP", "Director"],
  "per_page": 10
}' | jq '.people[] | {name: .name, title: .title, email: .email}'
```

### Search companies
```bash
curl-apollo.sh /api/v1/mixed_companies/search '{
  "q_organization_name": "Jewelers Mutual",
  "per_page": 5
}' | jq '.organizations[] | {name: .name, industry: .industry, employee_count: .estimated_num_employees}'
```

### Enrich a company by domain
```bash
curl-apollo.sh /api/v1/organizations/enrich '{"domain": "insurica.com"}' | jq '.'
```

### Bulk people enrichment
```bash
curl-apollo.sh /api/v1/people/bulk_match '{
  "details": [
    {"email": "person1@company.com"},
    {"email": "person2@company.com"}
  ]
}' | jq '.'
```

For full API reference and common query patterns, see `references/api-spec.md`.

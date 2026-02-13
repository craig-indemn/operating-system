# Apollo.io REST API Reference

Base URL: `https://api.apollo.io/api/v1`
Auth: API key in request body (`"api_key": "$APOLLO_API_KEY"`) or header (`x-api-key`)
Method: Most endpoints are POST

## People Endpoints

### Match (enrich by email)
```
POST /people/match
Body: {"api_key": "...", "email": "person@company.com"}
```
Returns: name, title, company, LinkedIn, phone, location, employment history

### Bulk match
```
POST /people/bulk_match
Body: {"api_key": "...", "details": [{"email": "a@b.com"}, {"email": "c@d.com"}]}
```
Max 10 per request.

### Search people
```
POST /mixed_people/search
Body: {
  "api_key": "...",
  "q_organization_name": "Company Name",
  "person_titles": ["VP", "Director", "CTO"],
  "person_locations": ["United States"],
  "per_page": 25,
  "page": 1
}
```

Key filters: `q_keywords`, `person_titles`, `person_seniorities` (owner, c_suite, vp, director, manager), `q_organization_name`, `person_locations`, `contact_email_status` (verified, likely_valid)

## Organization Endpoints

### Search companies
```
POST /mixed_companies/search
Body: {
  "api_key": "...",
  "q_organization_name": "Company Name",
  "organization_industry_tag_ids": [],
  "organization_num_employees_ranges": ["1,50", "51,200"],
  "per_page": 25
}
```

### Enrich by domain
```
POST /organizations/enrich
Body: {"api_key": "...", "domain": "company.com"}
```
Returns: name, industry, employee count, revenue, technologies, social links, description

## Contact Management

### List contacts
```
POST /contacts/search
Body: {"api_key": "...", "q_keywords": "insurance", "sort_by_field": "contact_last_activity_date", "sort_ascending": false}
```

### Create contact
```
POST /contacts
Body: {"api_key": "...", "first_name": "John", "last_name": "Doe", "organization_name": "INSURICA", "email": "john@insurica.com"}
```

### Update contact
```
PUT /contacts/{contact_id}
Body: {"api_key": "...", "title": "VP of Operations"}
```

## Rate Limits
- Standard: 100 requests/minute on most plans
- Enrichment: varies by plan credits
- Bulk: 10 records per request

## Response Structure
Most search endpoints return:
```json
{
  "people": [...],          // or "organizations", "contacts"
  "pagination": {
    "page": 1,
    "per_page": 25,
    "total_entries": 150,
    "total_pages": 6
  }
}
```

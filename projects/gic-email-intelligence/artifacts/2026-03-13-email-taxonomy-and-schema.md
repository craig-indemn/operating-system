---
ask: "What types of emails flow through GIC's quote inbox, and what schema should we use to capture them?"
created: 2026-03-13
workstream: gic-email-intelligence
session: 2026-03-13-a
sources:
  - type: microsoft-graph
    description: "25 email samples across all folders — Private Label (3), Inbox (16), Archive (3), GIC Reports (2), Hiscox Quotes (2), plus 2 phone tickets"
  - type: claude-analysis
    description: "Subagent analysis of 25 diverse email samples with no predefined categories"
---

# Email Taxonomy & Proposed Schema

## Email Types Discovered

### Type A: Carrier-Generated Quote Notifications
Automated messages from carriers (USLI, Hiscox, Concept Special Risks) notifying GIC a quote has been generated.
- **A1: Standard quote completed** — carrier produced a quote, here it is
- **A2: Wholesaler-routed quote** — retail agent lacks E&S license, carrier routes through GIC as preferred wholesaler (GIC didn't initiate)
- **A3: Carrier quotation forwarded internally** — GIC back-office forwards a carrier quote into the quoting queue

### Type B: New Submissions / Quote Requests
Retail agents submitting new business for quoting.
- **B1: Structured application submissions** — from web forms/portals with consistent fields (named insured, line of business, agency code)
- **B2: Freeform submissions** — agent emails an application as attachment with minimal body text

### Type C: Info Responses
Agent replies to GIC's information requests. Most varied and unstructured type — answers range from one word to paragraphs with documents.

### Type D: Policy Service Requests (Post-Quote / Post-Bind)
Agents requesting changes, documents, or actions on existing quotes or policies.
- **D1: Endorsement / modification requests** — add insured, change address
- **D2: Document requests** — dec page, loss runs, renewal info
- **D3: Escalated follow-ups** — agent has asked multiple times, frustrated
- **D4: Decline inquiries** — why was this declined?

### Type E: Phone Tickets
GIC's CSR team converts phone calls into email records. Rigid internal template: policy number, agent name/phone/email, request.

### Type F: Internal Forwards
GIC employee forwarding an agent's request into the quotes inbox for processing.

### Type G: System Reports
Automated reports from Unisoft (binder follow-ups, daily quote packages). Operational monitoring, not transactional.

### Type H: Acknowledgment / Status Replies
Agent confirming receipt. Minimal content, may include urgency flags.

## Key Observations

1. **The inbox is a work queue, not an archive.** Folder position implies processing state.
2. **GIC's system emails itself.** Web forms submit into the same email queue.
3. **E&S licensing creates a distinct intake path.** Some quotes arrive because the carrier pushed them, not because GIC requested them.
4. **Attachments are where the real data lives.** 98% have attachments. Email bodies are often just cover notes.
5. **Declines aren't terminal.** They spawn secondary requests (explain why, send loss runs).
6. **Same email can contain multiple request types.** Provides a document AND asks a question.
7. **Escalation is communicated through repetition.** "4TH REQUEST", "requested twice" — no formal priority system.
8. **The submission ID is the primary key.** GIC IDs (143xxx), carrier quote numbers, policy numbers all link emails to quotes.
9. **Thread reconstruction is critical.** The inbox shows the agent's side. GIC's outbound emails are in individual staff mailboxes.
10. **Spanish-speaking market dominance.** South Florida, heavily Hispanic client base. System needs bilingual handling.

## Proposed Schema

### email_message
Core email record.

| Field | Type | Description |
|-------|------|-------------|
| id | uuid | Primary key |
| graph_message_id | string | Microsoft Graph message ID |
| conversation_id | string | Graph conversation thread ID |
| folder | string | inbox, private_label, archive, hiscox_quotes, gic_reports, etc. |
| received_at | timestamp | |
| from_address | string | |
| from_name | string | |
| to_addresses | string[] | |
| cc_addresses | string[] | |
| subject | string | |
| body_text | text | Plain text body |
| has_attachments | boolean | |
| attachment_names | string[] | |

### email_classification
What Claude extracted about this email.

| Field | Type | Description |
|-------|------|-------------|
| email_id | fk | |
| primary_type | enum | carrier_quote, new_submission, info_response, service_request, phone_ticket, internal_forward, system_report, acknowledgment, decline_inquiry |
| sub_type | string | add_insured, address_change, dec_page_request, loss_run_request, renewal_inquiry, quote_revision, escalation, etc. |
| direction | enum | inbound, internal, system_generated |
| urgency | enum | normal, rush, urgent |
| is_escalation | boolean | |
| escalation_count | int | How many times this has been requested |
| intent_summary | string | One-line summary of what the sender wants |

### submission
A quote/policy lifecycle — the central business entity.

| Field | Type | Description |
|-------|------|-------------|
| id | uuid | |
| gic_submission_id | string | GIC's internal tracking number (143xxx) |
| named_insured | string | |
| line_of_business | string | GL, Personal Auto, WC, Marine, Roofing, etc. |
| carrier_name | string | |
| carrier_quote_number | string | |
| policy_number | string | Post-bind |
| premium | decimal | |
| limits | string | |
| effective_date | date | |
| expiration_date | date | |

### retail_agent
| Field | Type | Description |
|-------|------|-------------|
| id | uuid | |
| name | string | |
| email | string | |
| phone | string | |
| agency_name | string | |
| agency_code | string | GIC's code |

### email_submission_link
Many-to-many: one quote generates many emails, one email may touch multiple quotes.

| Field | Type | Description |
|-------|------|-------------|
| email_id | fk | |
| submission_id | fk | |
| role | enum | initial_submission, carrier_quote, info_request, info_response, service_request, decline, escalation |

### service_request
| Field | Type | Description |
|-------|------|-------------|
| id | uuid | |
| email_id | fk | |
| submission_id | fk | |
| request_type | enum | add_insured, change_address, dec_page, loss_run, renewal_info, financing, quote_revision, decline_explanation |
| details | jsonb | Structured details |

## What This Schema Enables

- **Pipeline view**: Group emails by submission, show lifecycle stage
- **Bottleneck detection**: Measure time between info_request and info_response
- **Escalation alerting**: Flag submissions with escalation_count > 1
- **Agent analytics**: Volume and patterns per retail agency
- **Business line analysis**: Information requirements per line of business
- **Automation targeting**: Which service_request types are repetitive enough to automate

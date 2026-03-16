---
ask: "What is Kyle's Silent Sports re-engagement proposal and what questions does Craig need to answer?"
created: 2026-03-16
workstream: silent-sports
session: 2026-03-16-a
sources:
  - type: slack
    description: "Kyle's message in #customer-implementation (ts=1773677360.280319) + thread history about Silent Sports roadmap"
  - type: google-doc
    ref: "https://docs.google.com/document/d/1LTZ1Lw3lO_8wPWWAEMR_fJ3HvKKql0OXv-NUJYTh6pg/edit"
    name: "Silent Sports — Internal Team Review"
---

# Kyle's Silent Sports Proposal Framework

## Background
Silent Sports (McKay Insurance) had a good demo Jan 28, 2026 but stalled — Meg hasn't tested the Phase 1 prototype. The original Dec 2025 proposal was a generic 60-day trial (too vague, no certificate generation, no rate engine). Kyle is re-engaging with a structured Crawl/Walk/Run paid proposal.

**The Hook**: Certificate generation. Scott called it a "quick win." Meg asked about document generation unprompted during the Jan 28 call.

## Key Customer Intel (Jan 28 Call)
- **Processing pain**: 15 min/app, 80-90 apps in peak month (October), 2-3 week delays
- **Certificate pain**: Scott bypasses AMS360 with PDF editor (3-4 min vs Meg's 15 min through AMS)
- **AMS flexibility**: Scott said "We're not 100% locked into AMS" — open to separate system for Silent Sports
- **Rate complexity**: Four combined rates subject to minimums, varying by activity type. Meg offered to send the rating spreadsheet.
- **Growth driver**: Scott said "If we can grow the book, that answers the question about cost"

## The Framework

### CRAWL — "Submissions + First Document" ($1,500/mo, Months 1-3)
- Submission processing (already demoed)
- Accord 25 certificate generation (Month 1 — THE HOOK)
- Premium disclosure page (Month 2 — requires rate table)
- Member certificate (Month 3 — most complex, custom template)
- Email notifications + follow-up drafting
- Data export to spreadsheet

### WALK — "Customer Access" ($3,000/mo, Months 4-6)
- Customer-facing quoting on website
- Conversational application (replaces 40-page web form)
- Program Builder for Scott/Meg to configure rates
- Web chat for customer Q&A

### RUN — "Revenue Engine" ($5,000/mo, Months 7-12)
- Voice agent for inbound calls
- Renewal automation (80-90 apps/month)
- Lightweight AMS alternative (naturally evolved, never positioned as "replace AMS")
- Broker portal, analytics dashboard

## Document Generation — The Net New Capability

**Critical**: This is net new for Indemn. No doc gen engine exists today. Silent Sports would be the first customer, but it becomes reusable (INSURICA COIs, Union General decline letters).

### What We're Building
1. **Template layer** — PDF form or custom template with field positions
2. **Data mapping** — Extracted submission data → template fields
3. **Generation API** — Structured data in → filled PDF out
4. **Review UI** — Human-in-the-loop before generating
5. **Numbering system** — Auto-increment cert numbers (separate from AMS360)

### Document Types
| Doc | Complexity | Estimate | Month |
|-----|-----------|----------|-------|
| Accord 25 Certificate | Medium | 2-3 days | 1 |
| Premium Disclosure | Low-Medium | 2-3 days | 2 |
| Member Certificate | Medium-High | 3-5 days | 3 |
| Endorsements | TBD | TBD | Later |

Total initial build estimate: 7-11 days for docs 1-3.

## Craig's Questions to Answer
1. **Feasibility**: Is 7-11 days realistic for the first 3 document types?
2. **Architecture**: Template-fill (PDF form fields) vs something more complex?
3. **INSURICA reuse**: Can we reuse anything from INSURICA's COI generation?
4. **Accord 25**: Are field positions industry-standard/fixed, or carrier-customized?
5. **Numbering**: Auto-increment cert numbers — straightforward or edge cases?
6. **Critical UX question**: Does Accord 25 alone help Meg enough? Or does she need all 3 docs before the workflow changes?

## Pricing Decision Needed
- **Option A**: Setup fee per doc type + monthly subscription (establishes doc gen as priced capability)
- **Option B**: Bundle into $1,500/mo CRAWL price (easier to sell, but sets "free" precedent)

## New Associates Proposed
- **Document Associate** — "Instant Document Assembly" (reusable across customers)
- **Program Associate** — "Program Administration" (lightweight AMS for specialty programs)
- Expands catalog from 24 → 26 associates

## Re-engagement Strategy
- Proposal IS the re-engagement — send to Scott (not just Meg)
- Message: "We built what you asked for. Certificate generation is the first thing you'll see."
- Use Scott's own words for ROI: "If we can grow the book, that answers the question about cost"
- Reference EventGuard/JM as comparable ($1M+ premium, one person operating)
- Never mention Blue Pond

---
ask: "Design a UI concept for the GIC demo that augments rather than replaces their Outlook workflow — hybrid split view with inbox + intelligence panel"
created: 2026-03-13
workstream: gic-email-intelligence
session: 2026-03-13-b
sources:
  - type: conversation
    description: "Product design brainstorm for Phase 3 demo application"
  - type: artifact
    ref: "artifacts/2026-03-13-email-taxonomy-and-schema.md"
    name: "Email taxonomy and extraction schema"
  - type: artifact
    ref: "artifacts/2026-03-13-exploration-objectives.md"
    name: "Exploration objectives"
---

# Hybrid Split View: Inbox + Intelligence Panel

## The Core Idea

GIC's underwriters and CSRs live in Outlook. Asking them to abandon that habit is a losing strategy. Instead, we build a system that *looks like email on the left and thinks like an underwriter on the right*. The left panel is familiar territory — a chronological email stream they already know how to scan. The right panel is the value layer — structured intelligence about the submission an email belongs to, surfaced the instant they click.

The bet: within two weeks of use, they stop opening Outlook entirely. Not because we forced them out, but because this shows them everything Outlook shows plus everything Outlook can't.

## Layout: The 40/60 Split

The screen divides into two panels. Left panel gets 40% width, right panel gets 60%. This is intentional — the intelligence panel is larger because it carries more information density and is where the actual work happens. A 1px muted divider separates them with a drag handle for resizing.

**Top bar** spans the full width: GIC logo, a global search field (searches across emails, submissions, agents, insureds), a filter/view toggle, notification badges, and the current user's avatar with their active claim count.

### Left Panel: The Smart Inbox

This looks like email. Vertical list of messages, newest on top. But it's email with quiet enhancements that earn trust before demanding behavior change.

**Each email row shows:**
- Sender name and agency (resolved — "Maria Lopez, Univista Insurance" not just an email address)
- Subject line
- Timestamp (relative: "2h ago", "Yesterday 3:14 PM")
- Attachment indicator with count
- Two-line body preview

**The quiet enhancements:**
- **Color-coded left border** (4px): green = new submission, blue = info response received, amber = escalation/urgent, gray = system notification, purple = carrier quote. Users never need to learn the colors explicitly — pattern recognition does the work.
- **Submission badge**: A small pill next to the subject showing the GIC submission number (e.g., "143872") when the system has linked this email to a known submission. Emails not yet linked show nothing — no noise for unresolved items.
- **Grouping toggle**: A button at the top of the inbox switches between "All emails" (flat chronological, what they're used to) and "By submission" (emails collapsed under their parent submission, showing unread count per group). Default is flat — let them discover grouping.
- **Smart folder tabs** along the top of the left panel: "All", "Action Needed", "Waiting on Agent", "USLI Feed", "Resolved". These replace Outlook's manual folder structure with dynamic, automatically maintained views.

**Handling the USLI flood (2,957 private label emails):** The "USLI Feed" tab isolates these automated notifications. In the "All" view, they appear but are visually muted (lighter text, no left border color) so human-generated emails stand out. A toggle in settings can hide them from "All" entirely. The key insight: these emails are reference data, not action items. The system extracts their structured data (insured name, premium, quote number, effective date) on ingestion and surfaces it in the intelligence panel — the emails themselves rarely need to be read.

### Right Panel: The Intelligence Layer

When nothing is selected, the right panel shows a **dashboard**: submission pipeline counts by stage (New, In Review, Awaiting Info, Quoted, Bound, Declined), today's aging alerts, and a "needs attention" queue sorted by urgency and staleness.

When an email is clicked on the left, the right panel transitions (200ms slide, no page reload) into the **Submission View** — the full context for the submission that email belongs to.

**Submission View has four sections, stacked vertically with collapsible headers:**

**1. Submission Header**
A dense summary bar: GIC submission number, named insured, line of business (with an icon — hard hat for roofing, truck for trucking, pest icon for pest control), carrier, premium if quoted, effective date, and current stage shown as a horizontal progress indicator (dots connected by lines: Submitted > Under Review > Info Requested > Quoted > Bound). The active stage pulses subtly. Days-in-stage counter shows in parentheses.

Assigned underwriter shown with avatar. If unassigned, a "Claim" button appears. If assigned to someone else, their name appears with an option to reassign.

**2. Timeline**
A vertical timeline of every event in this submission's life, newest on top. Each event is a card:
- Email received (shows sender, subject, one-line summary extracted by Claude)
- Email sent by GIC (reconstructed from thread context since we lack Sent Items)
- Phone call logged (from phone ticket emails, eventually from RingCentral)
- Status change (stage transitions with timestamp)
- System note (e.g., "Aging alert: 72 hours since info requested, no response")

**Critical interaction: clicking any email event in the timeline highlights that email in the left panel and scrolls to it.** The panels are bidirectionally linked — left drives right on click, right can drive left on click. This is the feature that makes the split view feel like one unified system rather than two side-by-side windows.

Timeline entries for emails show a small "expand" arrow. Clicking it shows the full email body inline in the timeline — the user never needs to go back to the left panel to read. They can work entirely in the right panel if they prefer.

**3. Extracted Data**
A structured card showing everything the system pulled from emails and attachments for this submission:
- Named insured, address, business description
- Requested coverage lines and limits
- Prior carrier and expiration date
- Loss history summary (from applications)
- Key details by business line (for roofing: years in business, number of employees, revenue, subcontractor usage)

**Completeness indicator**: a progress ring showing "7 of 10 required fields captured" based on the business line's information requirements. Missing fields are listed with a subtle "This is typically requested for [business line] quotes" note. This is where the system proves it understands insurance — it knows what a roofing GL submission needs before the underwriter has to think about it.

**4. Suggested Actions**
Context-dependent action cards:
- "Info request needed — missing: subcontractor details, prior loss runs" (with a draft info request the underwriter can review)
- "Response received 2 hours ago — review attached loss runs" (links to the attachment)
- "This submission is 4 days old with no action — escalation likely"
- "Similar submission from this agent last month was declined for [reason]"

Actions are read-only in v1 — the system suggests, the human acts in Outlook. No write access needed. In the future, these become one-click actions.

## Filtering and Search

The global search bar handles natural-language-ish queries: "Univista Insurance", "roofing quotes this month", "waiting on info more than 3 days", "submissions from Maria Lopez". Results appear in the left panel as a filtered list, right panel shows aggregate stats for the filter.

**Filter bar** below the search: dropdowns for Stage, Line of Business, Carrier, Retail Agency, Date Range, Assigned To. Active filters show as removable chips. Filters apply to both panels simultaneously.

## Multi-User Awareness

The submission header shows who's assigned. A "Claim" button on unassigned submissions lets someone take ownership. A small presence indicator (green dot) shows if someone is currently viewing a submission — prevents two people from working the same item unknowingly.

The "Action Needed" smart folder shows only items assigned to the current user (or unassigned). This is their personal work queue, automatically maintained.

## Demonstrating Data Extraction Quality

The Extracted Data card in the right panel is the proof. When an underwriter clicks an email with a 15-page GL application PDF attached, the right panel shows the extracted fields — named insured, business type, revenue, employee count, loss history — all pulled from the PDF by Claude vision. The underwriter can click any extracted field to see the source (highlights the relevant section of the PDF in a viewer overlay). This "show your work" feature builds trust in the extraction.

For the demo specifically: we show a submission where we correctly extracted complex data from a handwritten ACORD form or a Spanish-language application. If the system handles the hard cases, the easy ones are implied.

## The Transition Path

Day 1: "This looks like my inbox but with extra stuff on the right." They use it to check if they missed anything, then go back to Outlook for actual work.

Week 1: "The right panel catches things I'd miss. Let me check it before I reply." They start their workflow here, act in Outlook.

Week 2: "Why would I open Outlook? Everything I need is in one place." The intelligence panel becomes the primary interface. The inbox panel becomes the secondary reference.

This is the trajectory we're designing for. The left panel is the trust bridge. The right panel is the destination.

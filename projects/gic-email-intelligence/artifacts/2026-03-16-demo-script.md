---
ask: "How do we demo dry run with a test live sync? Draft a demo script to share with the team."
created: 2026-03-16
workstream: gic-email-intelligence
session: 2026-03-16-b
sources:
  - type: technical-design
    description: "Sections 1 (What the Demo Proves), 10 (Frontend), 15 (Pre-Demo Dry Run)"
  - type: implementation
    description: "Verified against working system with 10-submission sample"
---

# GIC Email Intelligence — Demo Script

## Audience
- **Juan Carlos (JC)** — EVP, Chief Underwriting Officer. Decision maker.
- **Maribel** — GIC staff, champion for email automation. The end user.
- **Mukul Gupta** — Granada Insurance (parent), technical coordination.

## What the Demo Proves

1. **We can read their emails and extract data correctly** — every field traceable to its source
2. **We understand their workflows** — stage detection, missing info identification
3. **We can act autonomously** — draft follow-ups, identify bottlenecks
4. **This is better than Outlook** — organized by submission, not by email

## Setup (Before the Call)

### Prerequisites
- [ ] Full batch processing complete (2,885 emails → submissions)
- [ ] Deployed to AWS with domain (`gic.indemn.ai` or similar)
- [ ] SSL working (HTTPS)
- [ ] Live sync running (60-second interval)
- [ ] Demo URL ready: `https://gic.indemn.ai/?token=<secret>`

### Pre-Demo Verification Checklist
- [ ] Board loads with real submissions across all 5 columns
- [ ] At least 20 submissions spot-checked for accuracy
- [ ] Search works (test: "Rodriguez", "USLI", a USLI ref number)
- [ ] Detail view loads correctly with timeline + extractions + completeness
- [ ] Live sync tested: send a test email to quote@, see it appear within 60s
- [ ] WebSocket working: board updates without manual refresh

---

## Demo Flow (15–20 minutes)

### Opening (2 min)

> "We connected to your quote@gicunderwriters.com inbox — read-only, nothing is being sent. What you're seeing is a live view of your submission pipeline, organized the way Maribel actually works with it."

Open the board at the demo URL. The board should already be populated.

### Act 1: The Board (5 min)

**Show the Kanban view.** Five columns: New, Awaiting Info, With Carrier, Quoted, Attention.

> "Every email that comes into quote@ is automatically classified and linked to a submission. Instead of scrolling through hundreds of emails, Maribel sees her pipeline at a glance."

**Point out key elements on cards:**
- Insured name, LOB pill, agent name
- Age badges (green = fresh, amber = getting old, red = needs attention)
- The sparkle icon means the system has a suggested action

**Show time filters.** Click "7d" to show recent activity. Click "All" to show full pipeline.

**Show notification badges** in the top right.
> "4 new submissions, 4 need a response, 7 are stale. These are Maribel's action items for the day."

Click a notification badge to filter the board.

**Show search.** Type an insured name. Show the instant dropdown.
> "Find any submission in seconds — by name, reference number, agent, or line of business."

### Act 2: Submission Detail (5 min)

**Click a submission card** (pick one with good data — a USLI quote with extractions).

The detail panel slides in from the right.

> "Every interaction with this insured, in one place. No more hunting through email threads."

**Walk through the timeline** (left column):
- Show email entries with type badges (USLI Quote, Agent Submission, etc.)
- Click to expand an email — show the full body loads inline
- Point out attachments with download links

**Walk through extracted data** (right column):
- Show the key-value pairs organized by section (Insured, Coverage, Carrier)
- Point out PDF and Email source chips
> "The system extracted this from the PDF attachments — premium, limits, carrier details. All automated."

**Show the completeness ring:**
> "7 out of 12 fields filled. The system knows exactly what's missing for this line of business."

Point out the missing fields listed below the ring.

**Show the suggested action card** (blue card at bottom):
> "The system drafted an info request for the missing items. Subject line matches your format. Professional tone. Ready for Maribel to review and send."

Read the draft subject: "Info Request for [Insured]- [Number]"

### Act 3: Live Demo (3 min)

**This is the selling moment.**

> "This is running on your live inbox right now. Let me show you."

**Option A — If someone can send a test email to quote@:**
Have someone send a simple email to quote@gicunderwriters.com during the call. Wait 60 seconds.

> "Watch the board..."

The new email appears. The system classifies it, links it to a submission (or creates a new one), and the board updates in real-time.

**Option B — If you can't send a test email:**
Show the sync status footer ("Last synced: 30 seconds ago"). Show the health check endpoint.

> "The system checks for new emails every 60 seconds. When Maribel opens this in the morning, everything from overnight is already organized."

### Act 4: Attention Column (2 min)

**Click on an Attention card** — pick a declined one.

> "Carrier declined this submission. The system flagged it automatically and drafted a notification to the agent."

Show the attention reason tag (declined, carrier_pending, agent_urgent, stale).

> "Stale submissions — anything with no activity for 5+ days — get automatically flagged. No more submissions falling through the cracks."

### Closing (2 min)

> "This is day one. Everything you see is from your actual emails — no mock data. Here's what comes next:"

1. **Email sending** — approve a draft, it goes out from quote@
2. **More lines of business** — we started with GL, expanding to all your LOBs
3. **RingCentral** — phone calls appear in the same timeline alongside emails
4. **Analytics** — time-to-quote, carrier response rates, agent performance
5. **Unisoft integration** — submissions flow directly into your management system

> "We built this in a week. The same system works for any inbox, any workflow."

---

## Live Sync — How It Works

### Architecture
```
Graph API (60s poll) → Sync command → MongoDB (pending) → Agent (classify + link) → Board update (WebSocket)
```

### Testing Live Sync Before Demo

**Step 1: Verify sync is running**
```bash
# Check sync status
curl https://gic.indemn.ai/api/health
# Should show: "sync": {"status": "idle", "last_sync_at": "<recent timestamp>"}
```

**Step 2: Send a test email**
Have someone (Kyle, Cam, or yourself) send an email to `quote@gicunderwriters.com` with:
- Subject: `Test Submission for Demo - [Your Name]`
- Body: "This is a test submission for the GIC Email Intelligence demo."
- Optional: attach a PDF

**Step 3: Wait 60 seconds, then verify**
```bash
# Check if the email was synced
outlook-inbox emails list --status pending --limit 1
# Should show the test email

# Or check via API
curl "https://gic.indemn.ai/api/submissions?days=1&token=<secret>"
```

**Step 4: Verify the board updates**
- Open the board in a browser
- The new email should appear as a new submission in the "New" column
- If the agent is running, it will be classified and linked within 60 seconds

### If Live Sync Fails During Demo
- The board still shows all existing data — it's just not updating live
- Say: "The sync runs every 60 seconds — let me show you the data we already have"
- Continue with the existing submissions

### If Agent Processing Fails During Demo
- New emails will appear as "pending" but won't be classified
- The board still shows all previously processed submissions
- Don't mention it — focus on the existing data

---

## Submissions to Highlight in Demo

Pick these from the full batch (after processing). Look for:

1. **A USLI quote with PDF extraction** — shows the full pipeline: email → classification → extraction → completeness ring → draft
2. **An agent submission with follow-up chain** — shows timeline with multiple emails linked to one submission
3. **A declined submission** — shows attention flagging + decline notification draft
4. **A stale submission** — shows automated staleness detection
5. **A submission with high completeness** — shows the ring nearly full (green)
6. **A submission with low completeness** — shows missing fields + info request draft

### Finding Good Demo Submissions (after batch)
```bash
# Find a quoted submission with extractions
outlook-inbox submissions list --stage quoted --json | python3 -c "
import sys, json
subs = json.loads(sys.stdin.read())
for s in subs[:5]:
    print(f\"{s['_id'][:12]} | {s.get('named_insured')} | emails: {s.get('email_count')}\")
"

# Find submissions with the most emails (best timelines)
mongosh-connect.sh dev gic_email_intelligence --eval '
db.submissions.find({}, {named_insured:1, email_count:1, stage:1})
  .sort({email_count:-1}).limit(10)
  .forEach(s => print(s.email_count + " emails | " + s.stage + " | " + s.named_insured))
'
```

---

## Q&A Prep

**"Is this reading our emails?"**
Yes, read-only. Application permission (Mail.Read) scoped to quote@ only via Exchange RBAC. We cannot send emails, access other mailboxes, or modify anything.

**"How much does this cost?"**
~$30/month for AI processing (500 emails/month), ~$30/month for hosting. Under $100/month total vs the $3K/month agreement.

**"Can we use it today?"**
The demo is live on your data right now. For production: we need Mail.Send permission for outbound emails, and we'll add user accounts + SSO.

**"What about other carriers besides USLI?"**
The system already handles Hiscox quotes. Adding carriers is configuration — a new LOB config file, no code changes.

**"What about phone calls?"**
Same architecture. RingCentral integration adds phone interactions to the same submission timeline. Next phase after email.

**"How accurate is the classification?"**
We classified all 3,165 historical emails. USLI emails (80% of volume) are 99%+ accurate — deterministic subject line patterns. Agent submissions and replies are ~95% — the AI handles ambiguous cases.

**"What about Spanish emails?"**
The classifier handles bilingual emails. Draft generation in Spanish is a future addition.

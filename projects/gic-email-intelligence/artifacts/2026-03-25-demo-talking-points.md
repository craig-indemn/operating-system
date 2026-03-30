---
ask: "Demo talking points for JC presentation — March 25, 2026"
created: 2026-03-25
workstream: gic-email-intelligence
session: 2026-03-25
sources:
  - type: research
    description: "business-model-synthesis.md — GIC business understanding"
  - type: system
    description: "Live system at localhost:5173 with 2,754 submissions assessed"
---

# Demo Talking Points — JC & Maribel Presentation

## Before You Start

- Web app open: `http://localhost:5173/?token=0So5zcDzGPnMdADZqh62r8Hpi559W9RbXqJlc3D_RBQ`
- Start on the **Overview** tab
- Outlook.com open in another tab with the add-in sideloaded
- Screen share ready

---

## Act 1: "We Understand Your Inbox" (Overview Tab — 5 min)

**Open with:** "We connected to your quote inbox — read-only — and analyzed 6 months of email. Let me walk you through what we found."

### What We Did (Section 1)
- "3,214 emails analyzed, 2,754 submissions identified, 39 lines of business discovered"
- "Every email classified by type — is it a USLI quote? An agent submission? A carrier decline? An info request?"
- "Emails grouped into submissions by reference numbers — we know which emails belong to the same risk"

### What We Found (Section 2)
- **This is the key insight — pause here:** "93% of your inbox is automated carrier notifications — mostly USLI. Only about 7% involves actual human communication. Of your 2,754 submissions, 95% are auto-quoted by USLI through Retail Web. The remaining 5% — about 140 submissions — represent 90% of your team's actual work."
- "We also identified that GIC operates in two modes — as a broker for most LOBs through USLI and Hiscox, and as the carrier for golf carts through Granada. These have fundamentally different workflows."
- **Ask JC:** "Does that match your understanding of how the volume breaks down?"

### How the System Works (Section 3)
- "For each submission, the system builds a situation assessment — it understands what's happening before it acts"
- "It knows who needs to act next — is the ball with the agent? With the carrier? Or with your team?"
- "Only when the system is confident that an email reply is the right next step does it suggest a draft"

### What This Means (Section 4)
- "For Maribel — instead of reading every email to figure out what it is, the system has already organized and assessed each submission. She sees what needs her attention and what doesn't."
- Don't belabor this — transition to showing it live.

**Transition:** "Let me show you what this looks like in practice."

---

## Act 2: "Email Reply Automation" (Submissions Tab + Outlook — 10 min)

### Show the Submission Queue
- Switch to **Submissions** tab
- "This is every submission from your inbox, organized by stage. You can see who's waiting — the agent, the carrier, or your team."
- Point out the dimmed auto-notified rows: "These gray rows are USLI auto-quotes — your team doesn't need to touch these. The system knows they're passthrough."
- **Filter:** Click "Hide auto-notified" to show only the ~400 submissions that matter

### Show a Submission with a Draft (the email reply quick win)
- Click into a submission that has a suggested draft (look for "Draft ready — review and send" in the action column)
- Walk through the Risk Record:
  - **Assessment summary** at top: "The system assessed this submission and determined [read the situation summary]"
  - **Conversation timeline**: "Here are the actual emails — you can read the full thread"
  - **Suggested reply**: "Because the system determined that an email reply is the right next step, it drafted this for you"
  - Show the draft content — it references the correct insured, the correct missing items, addressed to the correct agent
  - "Maribel would review this, click approve, and either copy it to clipboard or open it directly in Outlook"

### Show the Outlook Add-in
- Switch to Outlook.com tab
- Open the **Allan Ventura** email ("Information Required")
- Click "Indemn Email Intelligence" in the ribbon
- "This is the same intelligence, right inside Outlook. Maribel doesn't even need to leave her inbox."
- The sidebar shows: submission match, assessment, gap analysis, and the suggested reply
- "She can read the analysis, review the draft, and reply — all without switching applications"

### Show a Decline Notification
- Go back to the web app
- Click into a declined submission (Simaval Services)
- "When USLI declines a risk, the system knows. It drafts a notification to the retail agent with the decline details and can suggest alternative carriers."

**Key message:** "The immediate value is in these email replies. The system understands the context, drafts the right response, and Maribel reviews and sends. This saves hours per week on the repetitive communication work."

**Ask JC:** "Is this the kind of workflow Maribel deals with today? How much time does she spend on these info requests and notifications?"

---

## Act 3: "Golf Cart — Full Automation Path" (5 min)

### Show a Golf Cart Submission
- Search or filter for "Golf Cart" in the submissions
- Click into William Wacaster
- "This is a golf cart application that came through your Motorsports portal"
- **Assessment:** "The system recognized this is a portal submission with a complete application — 15 of 19 fields already collected"
- **No draft generated:** "Notice there's no suggested email reply here. The system determined that requesting information would be wrong — the application is already complete. The next step is underwriting review."
- **Gap analysis:** "Only 3 fields genuinely missing — driving record, effective date, and driver's license copy"

### Explain the Automation Path
- "Because GIC is the carrier for golf carts — not brokering to USLI — you control the entire lifecycle"
- "Today the system understands the submission and can tell you what's complete and what's not"
- "The next step is connecting to your underwriting guidelines so the system can validate the application and generate a quote automatically"
- "The end goal: agent submits via portal → system extracts and validates → quote generated → agent receives quote. No manual processing."

**Ask JC:** "Is this the vision you had for the golf cart program? What are the underwriting guidelines we'd need to encode?"

---

## Act 4: "What's Next" (Overview Tab — 3 min)

### Go back to Overview, scroll to "The Automation Path" section
- **Now — Email Intelligence:** "What you've seen today. Organized inbox, situation assessments, draft replies. Available now."
- **Next — Golf Cart Automation:** "End-to-end from portal to quote. We need your underwriting guidelines and API access to your management system."
- **Future — Broader Automation:** "Expand to other LOBs, connect to RingCentral for voice, integrate with the management system API."

### Key Questions for JC
- "Can we get access to Jeremiah for the management system APIs? Kyle mentioned that's the biggest unlock."
- "For the golf cart program — what are the underwriting guidelines? What determines whether a risk gets quoted vs declined?"
- "How does Maribel currently process submissions? Is she the sole processor, or does she have a team?"
- "What happens after a quote is issued? The bind requests go to a different inbox — how does that work?"

---

## If JC Asks...

**"How does this integrate with our existing systems?"**
→ "The system reads your email inbox through Microsoft Graph API — read-only. It stores its analysis in our database. The next integration point is your management system API (services-uat.granadainsurance.com) which Jeremiah manages. That would let us sync policy data and submission status."

**"What about the other 35 lines of business?"**
→ "Right now we have detailed configurations for General Liability and Golf Cart. The other 35 LOBs are recognized and classified, but don't have specific field requirements configured yet. We can expand LOB by LOB — each one takes about a day to configure from your email data."

**"Is our data secure?"**
→ "We have read-only access to the inbox. No emails are modified or deleted. The analysis data is stored in a separate MongoDB database on our infrastructure. No data is shared with third parties."

**"Can the system actually send emails?"**
→ "Not yet — it drafts replies for Maribel to review and approve. Sending requires Mail.Send permission, which would be a separate authorization from GIC. The current approach keeps a human in the loop."

**"What about voice / RingCentral?"**
→ "That's on the roadmap. You mentioned upgrading RingCentral for call recording — once that's in place, we can transcribe calls and link them to the same submissions. Same agent, same risk, multiple channels."

---

## Technical Setup Checklist (Before the Call)

- [ ] Backend running: `uv run uvicorn gic_email_intel.api.main:app --port 8080`
- [ ] Frontend running: `cd ui && npm run dev`
- [ ] Cloudflared tunnel running (for Outlook add-in)
- [ ] Web app loads: `http://localhost:5173/?token=0So5zcDzGPnMdADZqh62r8Hpi559W9RbXqJlc3D_RBQ`
- [ ] Overview tab shows real stats
- [ ] Submissions tab loads with data
- [ ] Can click into a submission and see assessment
- [ ] Outlook.com open with add-in sideloaded
- [ ] Seeded emails visible in inbox
- [ ] Add-in sidebar loads when clicking "Indemn Email Intelligence" on a seeded email

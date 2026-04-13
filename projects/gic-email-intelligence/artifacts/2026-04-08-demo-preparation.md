---
ask: "Demo narrative, questions for JC, production roadmap"
created: 2026-04-08
workstream: gic-email-intelligence
session: 2026-04-08a
sources:
  - type: mongodb
    description: "Live pipeline stats — emails, submissions, automation, AMS linkage"
  - type: codebase
    description: "Pipeline architecture, automation agent, Unisoft proxy"
---

# Demo Preparation — GIC Email Intelligence

## Demo Story

**Opening:** "We connected your Outlook inbox to your Unisoft AMS. Every application that comes through email is now automatically processed and entered into Unisoft."

**Numbers to lead with:**
- 4,055 emails ingested from quote@gicunderwriters.com (Sep 2025 — present, live)
- 3,668 applicants identified and organized
- 8,505 PDF documents extracted (ACORD forms, applications, loss runs)
- 138 applicants linked to Unisoft Quote IDs
- 110 Quote IDs created automatically by the system (no human involvement)
- 60% automation success rate on new applications

## Demo Walkthrough

### Screen 1: Applicant Queue
Show the table. Point out:
- Every email that arrives is classified by type (App, USLI, Portal, Reply, Internal)
- Each applicant has an AMS status — linked with a Quote ID, or "Needs attention" with a reason
- Filters: show AMS filter → "Auto-created" to see only automated ones, "Failed" to see what needs attention
- Data density: hundreds of applicants visible at a glance

### Screen 2: Detail View — Successful Automation
Click into an applicant with "Q:XXXXX Auto" badge. Show:
- **AutomationBanner**: "Quote Q:17262 created in Unisoft via automation on Apr 7"
- **ProcessingTimeline**: Received → Extracted → Classified → In AMS, with timestamps
- **ApplicantPanel**: Data merged from the email (ACORD form) and Unisoft AMS with source indicators — green checkmark means both systems agree
- **Conversation**: The original email thread

Point: "The system read the agent's email, extracted the ACORD form, identified the LOB, found the agency in Unisoft, and created the Quote ID — all automatically."

### Screen 3: Detail View — Failed Automation
Click into one with "Needs attention" badge. Show:
- **AutomationBanner**: "Not yet in AMS — Agency not found in Unisoft"
- This is a legitimate gap — the agency hasn't been set up in Unisoft yet
- All 87 failures were investigated; 37 unique agencies confirmed not in Unisoft

Point: "Every failure is a real business gap, not a software bug. The system tells you exactly what needs to happen."

### Screen 4: Insights — Inbox → AMS Journey
Show the top section:
- 138 in AMS, 87 needs attention, 60% automation rate
- AMS coverage by category: new applications are the automation target
- Failure reasons: mostly "Agency not found in Unisoft"
- System status: connected inbox, live pipeline, extraction stats

Point: "This is your inbox health dashboard. At a glance: what's linked, what needs attention, and why."

### Screen 5: The Big Finding — USLI Direct Portal
Explain the 2,800+ USLI carrier responses with no matching application:
- 68% of your email volume is USLI carrier quotes
- For most of these, the agent submitted directly to USLI's retail web portal, bypassing GIC email
- GIC only received the carrier response — the insured doesn't have a Quote ID in Unisoft
- **Question for JC**: Does GIC want these auto-entered into Unisoft from the USLI email data?

Point: "This is the biggest opportunity. If we automate this path too, we go from 138 linked to potentially 2,000+."

## Questions for JC

### Already documented (from agency verification artifact)

1. **Missing agencies (37):** Should we create them automatically, flag for manual creation, or skip automation?
2. **Producer codes:** The ACORD forms have codes (e.g., 7631, 7235) not in Unisoft. Old codes? Different system? Never set up?
3. **Estrella/Sebanda/Univista franchises:** When a specific franchise # isn't in Unisoft, what's the correct handling?
4. **USLI direct portal (~2,800 emails):** Does GIC want these auto-entered into Unisoft? Or does GIC already enter these manually?

### New questions for this demo

5. **Production Unisoft credentials:** We're on UAT. What's needed to get production access? Same proxy, different credentials?
6. **Approval to run in production:** What's JC's comfort level with the system creating Quote IDs automatically? Does he want a review period first (automation runs but flags for approval before creating)?
7. **Portal quote data:** UAT portal-created quotes are blank shells (Quote ID only, no applicant data). Is this a UAT limitation or does production behave the same?
8. **Email rules in Outlook:** Some agents' emails go to subfolders (USLI folder, Deleted Items). Should the system process ALL folders or only Inbox?
9. **Multi-LOB submissions:** Some agents submit multiple LOBs in one email. Currently we create one Quote ID per email. Should we split into separate quotes per LOB?

## Production Roadmap

### Phase 1: Production Credentials (1 day)
- Get production Unisoft credentials from JC
- Update proxy configuration or deploy a production proxy instance
- Verify connectivity: can we call `GetQuote` on a real production Quote ID?

### Phase 2: Validation Run (1 week)
- Connect to production Unisoft but run automation in **dry-run mode** — it determines what it would do but doesn't create Quote IDs
- JC reviews 20-30 dry-run results: "Would have created Q for [insured] with LOB [X] and agent [Y]"
- Fix any issues found during validation

### Phase 3: Supervised Automation (1-2 weeks)
- Automation creates Quote IDs in production but flags each one for JC review
- JC confirms or corrects each automated quote for the first batch (~50)
- Measure accuracy: what % did JC approve without changes?

### Phase 4: Full Automation (ongoing)
- Remove the review gate — automation runs fully unattended
- JC monitors via the Insights dashboard
- Failures still surface as "Needs attention" for manual handling
- Weekly summary email to JC with automation stats

### Phase 5: Expand Coverage (future)
- **USLI direct portal path** — auto-create Quote IDs from carrier response data
- **Granada portal** — auto-link via name matching
- **Carrier response inheritance** — link USLI/Hiscox responses to parent submissions
- **Agency auto-creation** — create missing agencies in Unisoft automatically

### Infrastructure for Production
| Component | Dev | Production |
|-----------|-----|------------|
| Email inbox | quote@gicunderwriters.com | Same inbox |
| MongoDB | dev-indemn Atlas cluster | Production cluster (TBD) |
| Railway | Development environment | Production environment |
| Unisoft proxy | EC2 54.83.28.79 → UAT | Same proxy → production credentials |
| Amplify frontend | main branch | Production branch or custom domain |
| Form extractor | dev-services EC2 | Same (stateless) |

### What's NOT Needed for Production
- No new infrastructure — same Railway services, same EC2 proxy
- No code changes — just credential/config swaps
- No schema migration — same MongoDB collections
- The pipeline code is environment-agnostic; it connects to whatever MongoDB/Unisoft the env vars point to

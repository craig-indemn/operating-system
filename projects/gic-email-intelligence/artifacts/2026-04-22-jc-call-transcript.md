---
ask: "Full transcript of JC/Craig/Maribel call Apr 22 — production rollout finalization, workflow changes, activity acknowledgement, underwriter assignment"
created: 2026-04-22
workstream: gic-email-intelligence
session: 2026-04-22a
sources:
  - type: google-doc
    ref: "https://docs.google.com/document/d/1Tb07Om95dllD9Fg4BqCWk0ny0b7GTaKPvYU3ndtsxJA"
    name: "Indemn | GIC Catch Up - 2026/04/22 12:00 EDT - Notes by Gemini"
---

# JC Call Transcript — 2026-04-22

## Attendees
Craig Certo, Juan C. Diaz-Padron (JC), Maribel (joined partway through)

## Gemini Summary

Production rollout finalized for quote automation with agency matching logic and system configuration confirmed.

## Decisions (from Gemini notes)

1. **Production rollout date:** Tomorrow (Apr 23), starting at 12:01 AM. Only new submissions dated from tomorrow onwards.
2. **Scope limited to quotes:** Excludes endorsements for now.
3. **Unmatched agency handling:** Submissions with unmatched agencies stay in the quote inbox for manual processing — not processed automatically.
4. **Task due date:** Same day as email received (not next business day). By the following day, task is already past due.
5. **Email as attachment:** Upload the original email as an attachment within the application folder alongside other documents.
6. **Application acknowledgement activity:** Trigger the "application acknowledgement" activity to notify agents upon successful processing. This replaces/follows the current "application received from agent" activity.
7. **USLI instant quotes deferred:** Not touching these for now. Future phase — would create quote + send "offer to agent" activity.

## Next Steps (from Gemini notes)

- **[Craig]** Create indemn process folder and indemn processed subfolder in the inbox
- **[Craig]** Share the inbox analysis / opportunities document with JC
- **[Craig]** Update task due date to same day (was next business day)
- **[Craig]** Upload the actual email as an attachment in Unisoft (applications subfolder)
- **[Craig]** Place all attachments and email into the applications subfolder
- **[Craig]** Trigger "application acknowledgement" activity upon quote creation
- **[Craig]** Send deployment preparation checklist and overview of steps
- **[JC]** Create/identify a user account for the Underwriter contact field. Email the selected user to Craig.

## Key Discussion Points

### Agency Matching Error Handling (00:12:07 - 00:13:51)
If agency can't be found: **leave the email in the inbox, don't process it.** JC agreed — nothing falls through the cracks. Either take it all the way through or don't touch it.

### Attachments and Subfolders (00:15:37)
Within Unisoft attachments, there are subfolders (applications, forms, loss runs, etc.). Put application documents and the email into the "applications" subfolder. May need tweaking over time.

### Activity: Application Acknowledgement (00:18:38 - 00:21:50)
JC wants the system to trigger "application acknowledgement" activity after quote ID is created. This sends a notification to the agent contact saying "we got it, we're processing it, here's your quote ID." The current "application received from agent" activity was for audit — JC wants the acknowledgement one instead because it emails the agent contact.

**Critical dependency:** The acknowledgement activity lists the "account manager assigned to your submission." This requires an underwriter/user to be set on the quote. JC is solving this by creating a user account and will email Craig which one to use.

### Underwriter Assignment (00:26:23 - 00:29:37)
- In UAT, Craig was using `ccerto` 
- In prod, need a proper user for the underwriter/agent contact field
- JC tried to create one live — running into email address conflicts
- JC will solve this and send the user to Craig
- For USLI instant quotes (future): use "USLI instant quote team" as the underwriter

### USLI Instant Quotes (00:24:51 - 00:26:23)
- Currently not being processed at all (emails go to private label folder via Outlook rule)
- JC sees this as an "easy win" next step
- Would need: create quote + "send offer to agent" activity
- **Deferred** — focus on new business quotes first

### Monitoring Plan (00:05:30 - 00:06:10)
- JC alerting team today to catch up on old items in the inbox
- Tomorrow (Thursday), all hands on deck monitoring
- Can pause midday if issues arise
- Same approach they used for chat bot rollout — "let it ride"

## Full Transcript

### 00:00:21
Craig reports success in dev testing — agency matching using phone and address has high success rate. Creating tasks in new biz group in UAT. Can move emails to indemn process folder.

### 00:04:42
JC asks if ready to go live tomorrow. Craig agrees. Plan: same approach as chat rollout — alert team, catch up on old items, automation starts with tomorrow's date only.

### 00:05:30
JC will tell team anything starting with tomorrow's date goes into the indemn filter. Monitor Thursday morning, revert if needed. "We just let it ride" — same as chat.

### 00:06:10
Scope: quotes only. Craig walks through the process — categorize email, create quote ID after identifying LOB, subline, agency. Create task for new biz group.

### 00:12:07
Three-tier agency lookup: producer code → multi-field match → error. 90% success in UAT, expecting higher in prod. If can't find: leave email in inbox, don't process.

### 00:13:51
After finding agency: duplicate check, create quote ID, upload all attachments, create task (new biz group or workers comp group). Subject: [Auto] {insured} — {LOB} via {agency}.

### 00:14:44
JC: Due date should be same day, not next business day. Craig agrees. JC asks about attaching the actual email — Craig will do it. Email and applications go into "applications" subfolder.

### 00:18:38
JC wants "application acknowledgement" activity triggered after quote creation. This notifies the agent that submission was received with the quote ID.

### 00:20:41
Challenge: activity requires an underwriter/agent contact on the quote. JC will create a user account and email Craig which one to use.

### 00:22:45
Non-quote emails (reports, notifications, third-party stuff) stay in inbox untouched. Automation only fires for classified new quote submissions.

### 00:24:51
USLI instant quotes discussion — JC has "USLI instant quote team" user for those. Not doing these tomorrow — future phase. Easy win once current rollout is stable.

### 00:27:04
JC trying to create underwriter user live — running into email conflicts. Will solve and send to Craig. Craig can easily switch the user.

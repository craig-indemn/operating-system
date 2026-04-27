---
ask: "JC flagged Q:146348 missing attachments. Investigate + fix, then tackle the notification delivery bug that's been hanging over production since go-live."
created: 2026-04-24
workstream: gic-email-intelligence
session: 2026-04-24-a
sources:
  - type: codebase
    description: "4 commits to gic-email-intelligence: attachment upload rewrite, Notes→Description rename, delete endpoint, notification full-fields"
  - type: ec2
    description: "3 rolling proxy deploys via SSM, atomic with rollback"
  - type: railway
    description: "2 deploys to automation service in production"
  - type: fiddler
    description: "Captured export3.saz from Unisoft UI uploading 11.4MB PDF (session 159 = AddQuoteAttachment, 120 = ModifyQuoteAttachment Delete)"
  - type: mongodb
    description: "Verified automation queue state, recent quote completions"
  - type: unisoft-prod
    description: "Tested end-to-end: 3 cleanup quotes, 20+ deletes, 2 full-size uploads"
---

# 2026-04-24 — Upload Bypass + Notification Field Fixes

## Summary

Went deep on two long-standing production bugs:
1. **Attachment uploads failing at ~1.5 MB** (3 of 63 automated quotes had missing attachments since go-live). Root cause: WCF buffered uploads hit an IIS content-length limit on Unisoft's Azure App Service. Fixed by bypassing WCF for uploads and using raw `HttpWebRequest` with `SendChunked = true` + proper MTOM/XOP multipart (binary as separate MIME part).
2. **Notification delivery inconsistency**: activities were saving with empty `Notes` + empty `Notification` in production. Root cause: two separate bugs — (a) code was sending `"Notes"` field which doesn't exist in ActivityDTO (schema uses `Description`); (b) our Notification dict had 8 fields but schema has 13, and missing fields caused the server to persist an empty default. Both fixed.

## Four commits shipped

| SHA | Fix |
|-----|-----|
| `8d85239` | Rename `Notes` → `Description` in `_create_activity_and_notify` — matches ActivityDTO schema |
| `fc0c24c` | Bypass WCF for uploads — `HttpWebRequest` + chunked + MTOM/XOP multipart |
| `ff4bd86` | New `unisoft attachment delete` CLI + `/api/file/delete` proxy endpoint (fetch-then-modify) |
| `8525923` | Populate all 13 ActivityNotificationDTO fields (not just 8) |

## Deploy cadence

- **Proxy on EC2** (`C:\unisoft\UniProxy.cs`): 3 rolling deploys, each atomic — backup + SSM pull + stop both services + compile + copy to `UniProxy-Prod.exe` + start both + verify. Rollback triggers on compile fail. Backups retained at `UniProxy.{cs,exe,Prod.exe}.{timestamp}.bak`.
- **Railway automation service**: 2 deploys (`railway up -s automation --environment production --ci`). Python changes only; no proxy changes there.

## The upload ceiling investigation

**Discovery path:**
1. JC flagged Q:146348 (C&P Coolers) missing attachments. MongoDB showed `automation_result.notes = "Attachment upload failed for DocHost_577.pdf"`. File was 5.59 MB.
2. Scanned production — 3 of 63 automated quotes since go-live had attachment failures (Q:146288 1.99 MB, Q:146334 11.44 MB, Q:146348 5.59 MB). **Not a clean size threshold** — Q:146271 with a 3.93 MB file had succeeded yesterday.
3. Direct tests through proxy today: 2 MB failed, 1.5 MB worked. **Unisoft's Azure App Service had tightened a content-length limit overnight.**
4. Tested UI upload of 11.44 MB PDF via Unisoft desktop on EC2 (Fiddler captured) — **UI succeeded**. Confirmed UI uses `Transfer-Encoding: chunked` + MTOM/XOP with binary as separate MIME part.
5. First attempt: `TransferMode.StreamedRequest` on WCF binding — didn't work, WCF falls back to Content-Length when the message body length is known at send time.
6. Full bypass: custom `HttpWebRequest` with `SendChunked = true`, `AllowWriteStreamBuffering = false`, manually-built multipart body matching the UI's wire format byte-for-byte. **Worked immediately** on 2 MB, 5.59 MB, and 11.44 MB tests.

**Post-fix cleanup:** Q:146348 and Q:146334 were first populated with split-chunk uploads (5 parts + 10 parts respectively via the old buffered path), then after the fix we uploaded the single full-size PDFs, then used the new delete endpoint to remove the 21 stray chunks and test files. Final state: Q:146348 has the original email + one clean DocHost_577.pdf; Q:146334 has the original GL Section + original email + the GIC Info Request + one clean 701 NE Inspection Report (11.4 MB).

## The notification delivery investigation

**Discovery path:**
1. Artifact claim: Q:146337 got its notification email sent, but Q:146340+ activities had empty Notification + empty Notes fields.
2. Pulled the IMSService WSDL from `research/unisoft-api/` and the canonical SetActivity SOAP capture from Fiddler. Found: ActivityDTO has a `Description` field, not `Notes`. **Our code was sending an unknown field name that Unisoft silently dropped.**
3. Rename shipped (commit `8d85239`). Verified via auto-runs Q:146370 + Q:146372 — Description now populates.
4. But Notification was still empty on read-back. Investigation revealed our Notification dict had 8 fields; schema has 13. Missing fields (`EmailAttachmentId`, `EmailAttachmentURL`, `EmailBCC`, `EmailCC`, `NotificationLetterContent`) weren't being emitted, and the server was persisting an all-defaults empty Notification for the activity.
5. Added missing fields (commit `8525923`). Tested on Q:146348 — SetActivity response came back with `EmailSentTo=Agency@greatoaksins.com` populated, meaning **the server accepted the notification and presumably sent the email**.

**Open question at checkpoint:** The activity's Notification fields appear empty on GetActivitiesByQuoteId read-back (tested 3 minutes after send), but the SetActivity response itself shows the populated fields. Contrast: Q:146337 Act 778982 (from yesterday) shows populated Notification on the same read path. Something about today's activities isn't persisting Notification even though the email is accepted. Worth verifying whether agents actually received emails.

## Delete attachment endpoint

Built because we needed to clean up the 21 stray uploads from investigation. Original minimal-DTO attempt failed with an empty SOAP fault — server requires the complete AttachmentDTO to identify the record. Fixed by doing a fetch-then-modify: proxy calls `GetQuoteAttachments` first, extracts the target DTO's inner XML (preserving `a:` namespace prefixes), then re-emits inside `ModifyQuoteAttachment` with `Action=Delete`.

Used it to delete 21 records on Q:146348 and Q:146334 — all returned `ReplyStatus: Success, RowsAffected: 1`.

New CLI: `unisoft attachment delete --id N --quote-id M`
New proxy endpoint: `POST /api/file/delete`

## Key lessons

1. **WCF `TransferMode.StreamedRequest` is NOT chunked-by-default** — WCF uses Content-Length when the message body length is known at send time. For true chunked transfer, either use a genuinely streaming message body or bypass WCF with raw `HttpWebRequest(SendChunked = true)`.
2. **Unisoft's Azure App Service has a tight upload limit** (~1.5 MB for buffered requests today, vs. 4+ MB observed yesterday). Our fix makes this irrelevant — chunked transfer has no Content-Length header.
3. **Unisoft DTOs require all schema fields** — a partial set causes the server to persist an all-empty defaulted record, silently. This is the same pattern that burned us with the Activity DTO (minimal payload caused `Notes`/`Notification` to drop) and the Notification sub-DTO.
4. **WCF's DataContractSerializer alphabetical-order rule is real but lenient about missing elements** — they're defaulted. What kills you is element NAMES that don't match schema (like `Notes` vs `Description`).
5. **Fiddler's .saz captures are the source of truth for wire format** — the raw SOAP payload reveals exactly what's different between the UI and our implementation. Session 159 (AddQuoteAttachment) and session 120 (ModifyQuoteAttachment Delete) were the two high-value captures today.

## Production state at checkpoint

- **4 new commits shipped and pushed to origin**
- **Proxy**: running latest code (commit `ff4bd86` binary), both UAT (port 5000) and Prod (port 5001) services up
- **Railway automation**: latest deploy has full Notification fields + Description fix
- **Q:146348, Q:146334**: cleaned up — only the real attachments remain
- **Today's automation volume**: 6 completed (Q:146354 × 2 dup, Q:146356, Q:146366, Q:146370, Q:146372), 0 failed

## Open items for next session

1. ~~Verify notification emails actually deliver~~ — **RESOLVED late afternoon**, see below.
2. **LangSmith tracing still broken** — zero traces in `gic-email-automation` + `gic-email-processing` projects. Env vars are set; `_langsmith_config()` builds a callback; traces aren't appearing. Carry-forward from prior session.
3. **Monitor upload success rate** — with the chunked fix, all attachment failures since go-live should disappear. Watch automation_result.notes for new "attachment upload failed" entries; if any appear, investigate the specific failure mode (could be different from content-length).

---

# Late-afternoon breakthrough — SendActivityEmail discovery (commit `a42bbe1`)

After the earlier fixes, Description populated on activities but Notification was still empty on read-back. Craig captured a Fiddler session of himself creating an Application Acknowledgement via the Unisoft UI — this revealed that **the UI uses TWO calls** to send a notification:

1. `IIMSService.SetActivity` — creates the activity record; `Notification` field on the ActivityDTO is sent as `i:nil` (the UI doesn't populate it — server ignores any inline notification payload)
2. **`IEmailService.SendActivityEmail`** — on a completely separate service we didn't know existed: `https://ins-gic-emails-service-{uat|prod}-app.azurewebsites.net/emailservice.svc`. This is what actually sends the email and writes the Notification back onto the activity.

Our code was doing only step 1, with a useless Notification payload that the server silently discarded. This explained why every activity since go-live (except the odd one like Q:146337) showed empty Notification on read-back — **no email was ever being sent by our automation.**

## Fix (commit `a42bbe1`)

- New `IEmailService` WCF contract + `EmailBridge` class in UniProxy.cs (parallel to SoapBridge but with very different binding: `WSHttpBinding(SecurityMode.Transport)`, `HttpClientCredentialType.None`, no ReliableSession, no SecureContext — the email service uses plain HTTPS per its `sp:TransportBinding` WSDL policy, with AccessToken in the body instead of a WS-Security header).
- New `/api/email/send-activity-email` proxy endpoint. Builds the full SendActivityEmail SOAP body (Claim + Policy DTOs all nil/default, Email DTO populated with recipient + subject + HTML body, outer ActivityId + QuoteID + UserName).
- `UNISOFT_EMAIL_URL` env var added to both prod + UAT proxy configs on EC2 (`C:\unisoft\UniProxy-Prod.env` + `UniProxy.env`).
- Python: `_create_activity_and_notify` refactored to mirror UI exactly — SetActivity (no inline Notification) → SendActivityEmail with rendered template. `unisoft_client.send_activity_email()` client method added.

## Verification

- Manual test on Q:146348: Act 779587 created with populated Description; notification sent to Agency@greatoaksins.com; read-back shows full Notification (subject, 1005-char HTML body, NoticeDate, NoticedByUser all populated).
- Production automations post-deploy (19:30 UTC): Q:146397 → luis@choiceone.us, Q:146398 → ubaid@fsinsurance.com, Q:146400 → marvinsoberanis@flpremierinsurance.com. All have populated Notification on read-back. **Real emails delivered to agents** for the first time since go-live.

## Key lessons added

6. **Unisoft has multiple SOAP services** — IIMSService (main), IINSFileService (attachments), and IEmailService (outbound email). Different hostnames, different binding configs, different security models. The WSDL is the source of truth for each.
7. **SetActivity does NOT send email, ever.** The Notification field on ActivityDTO is purely a read-back echo. Email delivery requires a separate `SendActivityEmail` call on IEmailService.
8. **When the UI workflow has N steps, mirror all N.** We spent two days stabbing at step 1 trying to make it do step 2's job. Fiddler capture + methodical comparison with UI wire format is the way.

## Full deploy record for the day

| SHA | Fix | Deploys |
|-----|-----|---------|
| `8d85239` | `Notes` → `Description` in ActivityDTO | Railway automation |
| `fc0c24c` | Proxy bypass WCF for uploads — HttpWebRequest + chunked MTOM | EC2 proxy |
| `ff4bd86` | `unisoft attachment delete` CLI + `/api/file/delete` proxy endpoint | EC2 proxy |
| `8525923` | Populate all 13 ActivityNotificationDTO fields (later superseded) | Railway automation |
| `a42bbe1` | **IEmailService + SendActivityEmail — real notification fix** | EC2 proxy + Railway automation |

Total: 5 atomic deploys to EC2 (all with rollback-on-fail + backups), 3 Railway deploys, 5 commits pushed to origin.

---

# End-of-day monitoring + JC weekly recap (4/24 evening)

## Post-deploy production monitoring

Scheduled wake-ups at 20:34, 21:05, and 21:35 UTC verified the SendActivityEmail fix held cleanly across the rest of the business day:

| Time | New automations | Notifications fired |
|------|-----------------|---------------------|
| 20:34 UTC | Q:146397, 146398, 146400 + Q:146400 dup-detected | 3/3 ✅ |
| 21:05 UTC | Q:146401, 146402, 146403 | 3/3 ✅ |
| 21:35 UTC | Q:146404, 146406, 146410 | 3/3 ✅ |
| 23:00 UTC | none (end of business day) | n/a |

**Final tally for first day post-fix: 9/9 automations delivered Application Acknowledgement emails** to distinct agent contacts. Zero attachment failures. Duplicate detection correctly identified 1 re-submission. Queue drained cleanly between cron ticks.

## Weekly recap email sent to JC

Drafted + sent a Friday-evening recap to **jcdp@gicunderwriters.com** (Juan Carlos Diaz-Padron) summarizing 4/23-4/24 production results. Content saved at `/tmp/jc-weekly-update.md` and `/tmp/jc-weekly-update-styled.html` (the latter has Gmail-safe inline-styled tables).

The email contains:
- Email volume table (276 received, 11 categories)
- Automation outcomes (62 unique quotes + 15 dups + 1 agency-gap = 78 agent submissions, numbers tie)
- 62-row per-quote pipeline table (Quote / Task / Attachments / Activity / Notification — gaps annotated)
- Issues + resolutions (attachment ceiling, notification delivery, dup detection)
- Closing offer: "If there's anything you'd like us to run retroactively — any step in the pipeline on past quotes — just let me know" + invitation for feedback

**No backfill mention in the closing.** Earlier draft had explicit "53 quotes never got notifications, can retro-send" framing — Craig dialed it back per his preference, since they had already retroactively sent some emails manually. The retroactive-anything-on-request offer covers it cleanly.

**Status**: sent at ~22:34 UTC on 4/24. Awaiting JC's reply. Sent message thread `19dc1a3729b1745e`.

## Gmail HTML gotcha (lesson for future external comms)

Two attempts before this email actually rendered tables on the receiving end:

1. **Created draft via API → user sent via Gmail compose UI** → tables rendered as plain rows. **Why**: Gmail's compose editor aggressively strips inline `<style>`/`<table>` styling on send, even though the API-created draft had them intact.
2. **Sent via API directly (`gog gmail send`)** → tables render correctly with borders/header shading. Gmail only sanitizes when you go through the UI compose path.

**Rule for future**: If sending HTML-formatted content to external recipients (JC, agents, etc.) via gog, use `gog gmail send` directly. Do NOT round-trip through the Gmail UI compose. Inline styles must be on every `<table>`, `<th>`, `<td>` (no `<style>` block — Gmail strips that too).

Also: add a wrapping `<div style="font-family: Arial, sans-serif; font-size: 14px;">` for consistent typography. Background colors, borders, padding — all Gmail-safe inline.

## Carry-forward updates

The "Open items" list above is now up to date. The most actionable next item is **JC's reply to the weekly recap** — he may have feedback, may take Craig up on the retroactive-send offer, or may have queue-management questions. Watch the inbox.

## Activity IDs for reference

Recent automation-created quotes today:
| Quote | Time | Subject |
|-------|------|---------|
| Q:146354 | 14:37-14:41 (×2 dup bug) | HandyPerson — LMK WORLDKRAFT LLC |
| Q:146356 | 14:47 | Rental Dwelling — 8872 LAND TRUST |
| Q:146366 | 15:47 | MIAMI HAIR TRANSPLANT LLC Sponsorship |
| Q:146370 | 15:57 | Boat Service and Repair — DIVE |
| Q:146372 | 16:12 | Artisan & Service Industries — R&Y PROFESSIONAL SERVICES GROUP LLC |

Cleanup test activities on Q:146348: Act 779339, 779356, 779466 (all created by my `_create_activity_and_notify` calls during testing).

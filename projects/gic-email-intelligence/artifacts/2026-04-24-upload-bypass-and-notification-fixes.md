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

1. **Verify notification emails actually deliver** — check with JC whether agents have received the "Application Acknowledgement" emails for Q:146366, Q:146370, Q:146372, Q:146374+. If yes, the server-side notification read-back display is cosmetic and we can close this. If no, something is still broken in the Notification payload.
2. **LangSmith tracing still broken** — zero traces in `gic-email-automation` + `gic-email-processing` projects. Env vars are set; `_langsmith_config()` builds a callback; traces aren't appearing. Carry-forward from prior session.
3. **Monitor upload success rate** — with the chunked fix, all attachment failures since go-live should disappear. Watch automation_result.notes for new "attachment upload failed" entries; if any appear, investigate the specific failure mode (could be different from content-length).

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

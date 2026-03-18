---
ask: "How should the approve/send workflow integrate with Outlook and the board view so the whole experience is intuitive end-to-end?"
created: 2026-03-18
workstream: gic-email-intelligence
session: 2026-03-18-a
sources:
  - type: conversation
    description: "Craig + Claude brainstorming on workflow integration after reasoning chain implementation"
  - type: technical-design
    description: "Microsoft Graph API permissions, current Mail.Read scope"
---

# Workflow Integration — Board Visibility + Outlook Send

## The Workflow

The system's value chain is: **Classify → Extract → Analyze → Draft → Send**

We've built classify through draft. The missing piece is the last mile — getting the draft into the user's hands in a way they can act on it. And the board needs to reflect where each submission is in this workflow.

## Current State

- Drafts are generated and shown in the detail view
- User can edit, approve, or dismiss a draft
- After approving, the card turns green and says "Approved" — but nothing else happens
- From the board, the only hint is a sparkle icon (✨) indicating a draft exists
- No way to distinguish: draft ready → draft approved → email sent

## Design: End-to-End Workflow

### Board Card States

Cards should communicate their workflow status at a glance:

| State | Visual | Meaning |
|-------|--------|---------|
| No draft | Default card | System hasn't generated a suggestion yet |
| Draft ready | ✨ sparkle + "Draft ready" text | AI generated a reply, needs review |
| Draft approved | ✅ green indicator + "Ready to send" | User reviewed and approved, ready for Outlook |
| Sent | Dimmed or moved | Email was sent (future — requires Mail.Send) |

The sparkle icon already exists. Enhance it:
- ✨ amber sparkle = draft ready (current)
- ✅ green check = approved, ready to send
- Add a small text label on the card: "Draft ready" or "Ready to send"

### Approve → Open in Outlook

When the user approves a draft, instead of just turning the card green, present an "Open in Outlook" action that:

**Option A: mailto link (immediate, no permissions needed)**
Opens the user's default email client with To, Subject, and Body pre-filled:
```
mailto:agent@agency.com?subject=Info%20Request%20for%20Acme&body=Dear%20Maria%2C%0A%0AWe%20need...
```

Limitations:
- Body length limited (~2000 chars in most clients before truncation)
- No HTML formatting (plain text only)
- No attachments
- User must be on a device with Outlook configured

**Option B: Outlook deep link (better UX, no extra permissions)**
Opens Outlook Web directly to compose with pre-filled fields:
```
https://outlook.office.com/mail/deeplink/compose?to=agent@agency.com&subject=Info%20Request&body=...
```

Advantages over mailto:
- Works in any browser (no desktop client needed)
- Longer body support
- GIC staff likely already logged into Outlook Web
- Can bookmark/share the link

**Option C: Create draft in Outlook (best UX, needs Mail.ReadWrite)**
Uses Graph API to create a draft directly in the quote@ mailbox:
```
POST /users/quote@gicunderwriters.com/messages
{ "isDraft": true, "toRecipients": [...], "subject": "...", "body": { "content": "...", "contentType": "text" } }
```

Advantages:
- Draft appears in their Outlook Drafts folder
- They just open Outlook and hit Send
- Can include attachments
- No URL length limits

Requires: Mail.ReadWrite permission (currently only have Mail.Read). Needs GIC admin consent.

### Recommended Approach

**For demo: Option B (Outlook deep link)** — works immediately, no permission changes, good UX.

**For production: Option C (Graph API draft creation)** — seamless experience, but requires permission upgrade.

**Fallback: Option A (mailto)** — if Outlook deep link doesn't work for their setup.

### Detail View Changes

After the user clicks "Approve":
1. Draft card turns green ("Approved")
2. A prominent "Open in Outlook" button appears — this is the primary CTA
3. Clicking it opens a new tab with Outlook Web compose, pre-filled with the draft content
4. Submission card on the board updates to show "Ready to send"

### Future: Post-Send Tracking

Once we have Mail.Send or Mail.ReadWrite:
- "Send" button directly in our UI
- After sending, submission moves to appropriate next stage
- Sent emails appear in the conversation timeline
- Board card shows "Sent" state

## Implementation Plan

### Immediate (this session)
1. **Board cards**: Show draft status more clearly — "Draft ready" vs "Ready to send"
2. **Approve action**: After approve, show "Open in Outlook" button with deep link
3. **Outlook deep link**: Generate `outlook.office.com/mail/deeplink/compose` URL with draft content

### Next session
4. **Board filtering**: Filter by draft status (ready, approved, none)
5. **Mailto fallback**: For cases where Outlook Web doesn't work

### Production
6. **Mail.ReadWrite permission**: Request from GIC admin
7. **Graph API draft creation**: Create drafts directly in Outlook
8. **Mail.Send permission**: Enable sending from our UI
9. **Post-send stage transitions**: Automatic stage updates after email sent

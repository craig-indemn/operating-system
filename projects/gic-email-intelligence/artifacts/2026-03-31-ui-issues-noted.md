---
ask: "UI issues noticed during prod review"
created: 2026-03-31
workstream: gic-email-intelligence
session: 2026-03-30-a
sources:
  - type: user-feedback
    description: "Craig reviewing prod at gic.indemn.ai"
---

# UI Issues — Noted for Later

## 1. Extracted fields vs gap analysis confusion
The detail view shows extracted fields in the top left AND gap analysis on the right side. It's confusing — unclear what each section is for and how they relate. Need to rethink the layout so the extracted data presentation is clear and not duplicated.

## 2. PDF download links broken (FIXED 2026-03-31)
Attachment URLs used relative /api path → went to Amplify instead of Railway. Fixed by using VITE_API_BASE.

## 3. Empty email bodies (FIXING)
HTML-only emails synced with empty body_text due to Graph API text-only preference. Root cause identified, fix committed. Needs re-sync.

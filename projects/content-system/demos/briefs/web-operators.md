# Video Brief: Web Operators

## Read First
- Video production playbook: `.claude/skills/content-showcase/references/video-production.md`
- Brand alignment: `projects/content-system/artifacts/2026-03-27-brand-alignment-reference.md`
- Smart Inbox demo as reference: `demos/smart-inbox/` (same animation patterns)
- Web Operators repo: `/Users/home/Repositories/web_operators/` (for technical accuracy)

## What This Is

Web Operators are a browser automation framework where an LLM agent operates a headless browser, follows a step-by-step markdown playbook (called a "Path Document"), and completes workflows on websites that have no API. The agent navigates real websites, fills real forms, reads real data — the same way a human would, but autonomously.

**How it works:**
```
Path Document (markdown playbook)
    → Deep Agent (Claude) → Agent Browser CLI → Web Application
    → Trajectory + Screenshots → Outcome (success/failure)
    → Refine path → run again → improve
```

**First customer:** Johnson Insurance Services ($10K/year, signed Feb 2026)
- Automates policy renewals and endorsements in Applied Epic (complex Angular SPA by Applied Systems)
- Logs in, navigates to activities, downloads PDF attachments, reads/extracts policy data, cross-references against actual policy, flags discrepancies, processes renewals/endorsements
- Cost driven from ~$18/run to ~$3/run via context reuse
- Runs on US-based EC2 instance, ~2 minutes per operation

**Key insight for the video:** Web Operators connect to ANY web-based system — carrier portals, AMS platforms (Applied Epic, AMS360, HawkSoft), rating engines, state filing systems. No API negotiation, no integration timeline. If your team can log in and use it, a Web Operator can too.

**Matrix alignment:**
- Category: **Operational Efficiency**
- Associate: Not explicitly in matrix (closest: could be a capability that supports multiple associates)
- This is infrastructure — it's HOW associates connect to systems without APIs

## Storyboard (suggested)

**Total target: ~60s. No dialogue — music only. Must work muted.**

The visual story: "Your team logs into 5 different portals every day. Watch what happens when you stop."

**Act 1 — The Portal Problem (5-8s)**
Visual: Multiple browser windows/tabs open — carrier portal login screens, AMS dashboards, rating engines. Overwhelming. A counter: "5 systems. No APIs. 3 hours of manual entry every day."
Build as HTML: tiled browser windows with realistic login screens.

**Act 2 — The Web Operator in Action (30-35s)**

Phase 1 — Path Document (~8s):
- A markdown document appears — the "playbook" the operator follows
- Steps highlight one by one: "Navigate to Applied Epic", "Open activity", "Download attachment", "Extract policy data", "Cross-reference", "Process renewal"
- This shows it's not magic — it's structured, auditable, step-by-step

Phase 2 — Browser Automation (~15s):
- Split view: left side shows the Path Document steps checking off, right side shows a stylized browser view
- The browser navigates: login → dashboard → activity list → open activity → download PDF
- Data flows from the PDF into structured fields (similar to ACORD extraction in Smart Inbox)
- Key callout: "No API required"

Phase 3 — Results (~8s):
- Activity processed: "Renewal processed in 2 minutes"
- Cost: "$3 per operation"
- Next activity auto-starts
- Counter: "4 activities. 8 minutes. Zero manual entry."

**Act 3 — Stats (10s)**
- Any web-based system supported
- $3 per operation (was $18)
- <2 minutes per operation
- Zero APIs required
- "Stop waiting for integrations that will never come"

**Act 4 — CTA (5s)**
Standard CTA.

## Page Updates

Placeholder page exists at `src/content/outcomes/web-operators.mdx`. After building the video:
1. Replace "## Page Coming Soon" with full content
2. Content should cover: the portal problem, how path documents work, the Johnson Insurance case study (anonymized or named — check with Craig), systems it connects to
3. Embed video above the content
4. Consider adding a section about how Web Operators integrate with other Associates (an Associate dispatches a Web Operator when it needs to interact with a system that has no API)

## Key Visual Patterns to Use

- **Tiled browser windows** — new pattern. Multiple overlapping browser windows showing different portal login screens
- **Checklist/steps view** (inspired by gap analysis in EmailDeepDive) — path document steps checking off
- **Split view** — left: checklist, right: browser visualization
- **Data extraction** (from EmailDeepDive) — adapt for policy data flowing from PDF to structured fields
- **Stats reveal** (from StatsReveal)
- **CTA** (from CTACard) — copy directly

## Rudra's Demo Video

There's a real demo video from Rudra in Slack (#dev-squad, file: `web-operator-demo.mp4`) showing the CAP renewal automation in Applied Epic. Consider downloading it for reference on what the actual browser automation looks like. Don't embed it — build the animated version instead for visual consistency.

## Lexicon Reminders
- "Associate" not "agent" (but "agent" is OK when referring to the LLM agent in technical architecture descriptions — avoid in customer-facing copy)
- "Capability" not "tool" when referring to Indemn's offering
- "No API required" is the key message — repeat it
- Don't say "RPA" — Web Operators go beyond traditional RPA (understand context, adapt to layout changes, recover from errors)

# Video Brief: Quote & Bind

## Read First
- Video production playbook: `.claude/skills/content-showcase/references/video-production.md`
- Brand alignment: `projects/content-system/artifacts/2026-03-27-brand-alignment-reference.md`
- Smart Inbox demo as reference: `demos/smart-inbox/` (same animation patterns)
- Existing page: `src/content/outcomes/quote-and-bind.mdx` in `/tmp/engineering-blog-sync/`

## What This Is

The Quote & Bind Associate handles the full quoting workflow via conversation — a customer describes what they need, the associate collects information naturally, checks eligibility, generates quotes from carriers, and can bind coverage on the spot.

**Matrix alignment:**
- Category: **Revenue Growth**
- Associate: **Quote & Bind Associate**
- Target: Distribution (MGAs with binding authority)

**Key proof point:** Eventuguard — "Indemn created, scaled, and sold a fully digital MGA to Jewelers Mutual Insurance, with our Associates completing over 90% of policy sales without human intervention."

**Additional proof:** 25% lift in conversion vs web forms.

## What the Existing Page Shows

The page already has a rich interactive demo with:
- 3 scenarios (Event Insurance, Specialty Commercial/Jewelry, Renters)
- Chat conversation with parameter collection panel
- Stacking callouts, quote cards, policy confirmation
- Workflow diagram SVG
- InfinitePages component (branded distribution channels)
- IntegrationModes component

The video should complement this — showing the flow visually as an animated sequence, not duplicating the interactive demo.

## Storyboard (suggested)

**Total target: ~60s. This one could have VO since it's a conversation flow.**

**Act 1 — The Conversation Starts (5s)**
A customer lands on a website / opens a chat / calls a number. Simple establishing shot.
Could use Kling: "Close-up of someone typing on a phone, soft light, casual setting."
Or HTML: a clean chat widget opening with a greeting.

**Act 2 — The Quote Flow (30-35s)**

Phase 1 — Information Collection (~12s):
- Chat-style UI: associate asks questions, customer responds
- Side panel fills in with collected parameters (business type, revenue, coverage needed, etc.)
- Use a concrete scenario: Event insurance for a wedding planner
- "What type of event?" → "Weddings and corporate events" → "How many events per year?" → "About 40"

Phase 2 — Eligibility + Quote (~12s):
- Eligibility check animation (checkmarks appearing)
- "Checking carriers..." → quote cards appear from 2-3 carriers
- Each card: carrier name, premium, coverage limits, key terms
- Highlight best match

Phase 3 — Bind (~8s):
- Customer selects a quote
- Confirmation animation: policy number issued, certificate ready
- "Coverage active. Certificate emailed."

**Act 3 — The Impact (10s)**
Stats:
- 90% of policies sold without human intervention (Eventuguard)
- 25% lift in conversion vs web forms
- <3 min from first question to bound policy
- "Revenue your team didn't have time to capture"

**Act 4 — CTA (5s)**
Standard CTA.

## Page Updates

Page exists and is full-featured. Just embed the video above the interactive demo:
```html
<video controls playsinline style="width: 100%; border-radius: 12px; margin: 2rem 0; box-shadow: 0 4px 24px rgba(0,0,0,0.12);">
  <source src="/videos/products/quote-and-bind.mp4" type="video/mp4" />
</video>
```

Add after the workflow SVG image tag, before `<QuoteBindDemo />`.

## Key Visual Patterns to Use

- **Chat conversation UI** — new pattern, not in Smart Inbox. Build a clean chat with message bubbles (associate on left in iris, customer on right in light gray) + side panel for parameters
- **Card reveal** (from EmailDeepDive extraction) — adapt for quote cards appearing
- **Stats reveal** (from StatsReveal)
- **CTA** (from CTACard) — copy directly

## Lexicon Reminders
- "Associate" not "agent"
- Eventuguard proof point is strong — use it
- "Revenue capacity" not "cost savings"
- Human-in-the-loop must be mentioned: "When the risk is complex, the Associate queues it for human review"

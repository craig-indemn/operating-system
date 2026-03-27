# Video Brief: Open Enrollment

## Read First
- Video production playbook: `.claude/skills/content-showcase/references/video-production.md`
- Brand alignment: `projects/content-system/artifacts/2026-03-27-brand-alignment-reference.md`
- Smart Inbox demo as reference: `demos/smart-inbox/` (same animation patterns)

## What This Is

The Open Enrollment Associate (named "Riley") handles healthcare enrollment calls — originally built for Insurica Direct, now a demoable product for any healthcare insurance customer.

**Two-part agent system:**
1. **Reception/Front Door** — answers overflow and after-hours calls, collects contact info, determines enrollment type (self vs proxy vs tandem), identifies product interest (Medicare vs general), qualifies life events
2. **Part D Medication Specialist** — navigates a locality-specific Drug Formulary (2,188 pharmaceutical entries, 40,503 lines), does fuzzy matching on spoken drug names, handles tier classifications, prior auth requirements, quantity limits, step therapy protocols

**Production results (Insurica, Nov 11 - Jan 5):**
- 202 valid calls (55% overflow, 45% after-hours)
- 85.4% of consenting callers completed the core pathway
- 34 fully qualified leads (16.8% of volume)
- Covered 12 states
- Supported proxy callers (21.6%) and tandem enrollment (20%)

**Key capability:** The formulary navigation — a caller says "I take metformin 500mg twice a day and lisinopril" and the associate looks up each medication, checks tiers, prior auth requirements, and provides plan guidance. This is the visual centerpiece.

## Matrix Alignment

**Not yet mapped to an associate in the Four Outcomes Matrix.** Cam has been asked to confirm. For now, use:
- Category: TBD (likely Client Retention or Operational Efficiency)
- Associate name: "Open Enrollment Associate" (working name)

## Storyboard (suggested — adapt as needed)

**Total target: ~60s. No dialogue — music + optional VO. Must work muted.**

**Act 1 — The Volume Problem (5s)**
Visual: Phone ringing counter ticking up during open enrollment season. "Open Enrollment. 6 weeks. Hundreds of calls."
Could be Kling establishing shot (phone on desk, busy office) or HTML counter.

**Act 2 — The Call Flow (20-25s)**
Show the two-part system visually:

Phase 1 — Reception (~10s):
- Caller card appears (name, phone)
- Qualification checklist animates: Medicare? Self or proxy? State?
- Routing decision: "Qualified → Transfer to Medication Specialist"

Phase 2 — Formulary Lookup (~15s):
- Medication list appears one by one (caller speaking): "Metformin 500mg", "Lisinopril 10mg", "Omeprazole 20mg"
- For each medication: search animation → formulary match → tier classification → prior auth check
- Summary card: 3 medications checked, all covered, Tier 1/Tier 2, no prior auth needed
- "Personalized plan recommendation ready"

**Act 3 — Results (10s)**
Stats view:
- 202 calls handled
- 85% completed pathway
- 34 qualified leads
- 24/7 availability
- "Your licensed staff focuses on the conversations that need them"

**Act 4 — CTA (5s)**
Standard CTA: channel icons, "Making insurance a conversation.", indemn.ai

## Page Updates

The placeholder page exists at `src/content/outcomes/open-enrollment.mdx`. After building the video:
1. Replace "## Page Coming Soon" with full content (problem statement, how it works, video embed)
2. Embed video: `<video controls playsinline style="width: 100%; border-radius: 12px; margin: 2rem 0; box-shadow: 0 4px 24px rgba(0,0,0,0.12);"><source src="/videos/products/open-enrollment.mp4" type="video/mp4" /></video>`
3. Copy final video to `public/videos/products/open-enrollment.mp4` in the blog repo at `/tmp/engineering-blog-sync/`

## Project Setup

```bash
cd projects/content-system/demos
cp -r smart-inbox/public open-enrollment/public  # brand assets
# Create new Vite+React project following the playbook
```

## Key Visual Patterns to Use

- **Inbox/call counter** (from InboxCounter) — adapt for phone calls
- **Data processing view** (from EmailDeepDive) — adapt for formulary lookup (medication input → search → result)
- **Stats reveal** (from StatsReveal) — production metrics
- **CTA** (from CTACard) — copy directly

## Lexicon Reminders
- "Associate" not "agent" or "bot"
- "Resolution rate" not "deflection rate"
- Never say "replaces" licensed agents — say "handles intake so licensed staff focuses on judgment calls"

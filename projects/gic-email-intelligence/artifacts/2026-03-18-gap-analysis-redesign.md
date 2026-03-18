---
ask: "How should the gap analysis distinguish between what's actively being requested in this conversation vs general LOB requirements? How do we visually connect gap items to the draft?"
created: 2026-03-18
workstream: gic-email-intelligence
session: 2026-03-18-a
sources:
  - type: browser-testing
    description: "Craig reviewed Ojeda A Services detail view — gap analysis shows 10 generic missing items but the email thread only asks for 1 specific thing"
  - type: conversation
    description: "Craig's feedback on making gap analysis conversation-aware and visually connected to the draft"
---

# Gap Analysis Redesign — Conversation-Aware + Color-Coded

## The Problem (Ojeda Example)

The email thread for Ojeda asks for specific things:
- "Detailed description of operations" (still needed)
- "Loss runs and premiums for the last 5 years" (Diana provided these)
- "Copy of cancellation notice" (Diana provided this)

The AI draft correctly asks for just "Detailed description of operations."

But the gap analysis shows 10 ❌ items from the generic GL config: Business Address, Entity Type, Annual Revenue, Coverage Limits, etc. — none of which are being discussed in this conversation.

**Result:** The gap analysis feels disconnected from reality. The user sees 10 red items and thinks "this is a mess" when actually there's only 1 thing left to do.

## The Solution: Two-Tier Gap Analysis

### Tier 1: Active Requests (from conversation/draft)
Items the system is actively requesting or that the conversation is about. Source: `draft.missing_items` — these are conversation-derived, not generic.

- Shown prominently with amber/orange highlight
- Each item visually matches the same text in the draft body
- Shows status: provided ✅ or still needed ⚠️

### Tier 2: General LOB Requirements (from historical analysis)
The full checklist from the LOB config. These are "nice to have" context, not immediate action items.

- Shown collapsed by default ("Show all General Liability requirements")
- Gray/muted styling
- Still shows ✅/❌ for completeness

### Visual Connection: Color Coding

Active request items use a consistent highlight color (amber/orange) that appears in:
1. **Gap analysis checklist** — the item row has an amber left border or background
2. **Draft body** — the same term is amber-highlighted in the draft text

The user can scan the gap analysis, see "1 item still needed: Detailed description of operations" in amber, then look at the draft and see that same phrase highlighted in amber. Connection is instant — no reading required.

## Implementation

### Data Source
- `draft.missing_items` → active requests (Tier 1)
- `lob_requirements.required_fields` + `required_documents` → general requirements (Tier 2)
- Submission + extraction fields → what's filled

### GapAnalysis Component Redesign
```
┌─────────────────────────────────────────┐
│ Active Requests                         │
│ ⚠️ Detailed description of operations  │  ← amber highlight
│ ✅ Loss runs — Amtrust Loss runs.PDF   │
│ ✅ Cancellation notice — provided      │
│                                         │
│ ▸ General Liability Requirements (2/12) │  ← collapsed, gray
│   ✅ Named Insured — Ojeda A Services  │
│   ✅ Loss Runs — Amtrust Loss runs.PDF │
│   ❌ Business Address                  │
│   ❌ Entity Type                       │
│   ...                                  │
└─────────────────────────────────────────┘
```

### Draft Body Highlighting
In the DraftCard, scan the body text for terms that match `missing_items`. Wrap matches in an amber-highlighted span:

```tsx
// "Detailed description of operations" in the draft body
// becomes: <span className="bg-amber-100 rounded px-0.5">Detailed description of operations</span>
```

### Attachment Filtering
Hide attachments with empty `storage_path` (inline images like CID references that can't be opened). Only show downloadable attachments.

## Craig's Vision
> "Before I even have to read the automated email, I know that in there it's looking for these things. Even better would be a way to see in the actual email itself, whether it's highlighted or color-coded, the things that they're looking for, and that same color is used everywhere."

This is about cognitive load reduction. The user shouldn't have to cross-reference between sections mentally — the visual system does it for them.

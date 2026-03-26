---
ask: "Document how the Smart Inbox demo video pages were built — patterns, design system, and replication playbook"
created: 2026-03-26
workstream: content-system
session: 2026-03-26-d
sources:
  - type: github
    description: "Smart Inbox demo project at demos/smart-inbox/"
---

# Smart Inbox Page Production Process

## What We Built

6 animated React pages for a ~2min conference demo video showing an AI Inbox Associate processing 23 insurance submission emails. Purely visual (no voice/dialogue), music-only. Each page is a self-contained animation recorded via Playwright.

3 pages are fully implemented (inbox, triage, deepdive). 3 remain as stubs (zoomout, stats, cta).

## Project Structure

- `demos/smart-inbox/` — Vite + React + TypeScript
- `?page=` query param routing (inbox, triage, deepdive, zoomout, stats, cta)
- No external dependencies beyond React — no animation libraries, no LiveKit
- Brand assets copied from FNOL template (`public/brand/logo-iris.svg`, `logo-white.svg`)
- Dev server runs on port 5180

### File Layout

```
demos/smart-inbox/
  index.html
  package.json           # react 19.1, vite 6.3 — nothing else
  vite.config.ts
  tsconfig.json
  public/brand/
    logo-iris.svg
    logo-white.svg
  src/
    main.tsx             # Query param router (switch on ?page=)
    InboxCounter.tsx      # Act 1 — inbox filling up
    inbox.css
    EmailTriage.tsx       # Act 2 Phase 1 — Kanban sorting
    triage.css
    EmailDeepDive.tsx     # Act 2 Phase 2 — extraction + reply
    deepdive.css
    BoardZoomOut.tsx      # Act 2 Phase 3 — stub
    StatsReveal.tsx       # Act 3 — stub
    CTACard.tsx           # Act 4 — stub
```

## Design System

- Font: Barlow (Google Fonts import in each CSS file)
- Background: #f4f3f8 (light lavender)
- Surface: #ffffff (white cards)
- Text primary: #1e2553 (eggplant)
- Text secondary: #6b7094
- Accent: #4752a3 (iris)
- Success: #22c55e
- Warning: #f59e0b
- Border: #d4d7e3, #e8e7ed
- Cards: white bg, 1px border, 12px radius, subtle box-shadow

## Animation Pattern

Every page uses the same pattern:

1. `useState(0)` step counter
2. `useEffect` with an array of `setTimeout` calls, each incrementing the step
3. CSS classes toggled by step number: `className={step >= N ? "visible" : ""}`
4. CSS transitions handle the visuals (opacity, transform, with ease timing)
5. Cleanup via `return () => timers.forEach(clearTimeout)`

This is dead simple, requires zero animation libraries, and produces smooth, professional results. The key insight: CSS transitions do the heavy lifting. React just orchestrates the sequence.

### Timing Design

- Use arrays of [step, milliseconds] tuples for readable timing (see EmailDeepDive)
- Group related animations (e.g., all extraction fields populate 800ms apart)
- Accelerating cadence creates energy (triage cards start at 700ms intervals, end at 300ms)
- Hold at end for recording buffer

## Page Breakdown

### Act 1 — Inbox Counter (?page=inbox)

- Email client UI: sidebar with folders (Inbox, Sent, Drafts, Archive, Starred) + main email list
- 23 realistic insurance emails with sender emails, subjects, timestamps, attachment indicators
- Emails appear in 3 batches with staggered row animations:
  - Batch 1 (0-8): 120ms intervals starting at 300ms
  - Batch 2 (8-14): 100ms intervals starting at 1500ms
  - Batch 3 (14-23): 80ms intervals starting at 2800ms (faster, overwhelming)
- Unread badge on sidebar updates with each new email (key={visibleCount} triggers re-animation)
- Dark gradient overlay appears at 3800ms with "Monday. 8:00 AM. 23 submissions arrived overnight."
- Duration: ~5s

### Act 2 Phase 1 — Email Triage (?page=triage)

- 5-column Kanban board: New Submission (green, 8 cards), Quote Ready (blue, 4), Follow-Up Needed (orange, 6), Renewal (purple, 3), Not a Submission (gray, 2)
- 23 cards arrive in shuffled order via `arrivalOrder` array (not grouped by column)
- Accelerating cadence: first 5 at 700ms apart, next 8 at 450ms, last 10 at 300ms
- Each card: avatar circle with initials, subject, sender name, colored tag
- Column counts appear 600ms after last card, bottom counter bar 600ms after that
- Bottom counter: "23 emails. 47 seconds. Zero human input."
- Header shows live "Sorted: N / 23" progress
- Duration: ~15s

### Act 2 Phase 2 — Email Deep Dive (?page=deepdive)

- Two-column layout: email + extraction (left), gap analysis + draft reply (right)
- 5 sequential frames with 24 animation steps over ~27s:
  - Frame 1 (steps 1-3, 0.8-2.2s): Email card appears, two ACORD PDF attachments animate in
  - Frame 2 (steps 4-9, 4.0-8.5s): ACORD Data Extraction card — 5 fields populate one by one (Business, Revenue, Employees, Operations, Coverage), then AMS integration callout
  - Frame 3 (steps 10-16, 10.0-14.0s): Completeness Check — 5 gap items appear (3 complete, 2 missing), completeness bar animates to 75% (6/8 fields)
  - Frame 4 (steps 17-24, 16.0-25.5s): Auto-Generated Reply — 5 draft lines appear, auto-send toggle, "Sent at 8:01 AM" confirmation
- Specific insurance data: Riverside Landscaping LLC, ACORD 125/126, GL $1M/$2M, jessica.parker@worthington-insurance.com
- Duration: ~40s (including hold at end)

### Act 2 Phase 3 — Board Zoom Out (?page=zoomout) — STUB

- Intended: Pull back to show all 23 emails processed on the board
- Currently returns placeholder div

### Act 3 — Stats Reveal (?page=stats) — STUB

- Intended: Clean stats view with animated counters
- Currently returns placeholder div

### Act 4 — CTA End Card (?page=cta) — STUB

- Intended: "Making insurance a conversation" with channel icons
- Currently returns placeholder div

## SVG Icon Pattern

All icons are inline SVG components — no icon library dependency. Consistent style:

- 18x18 or 14x14 viewBox (18 for card headers, 14 for inline elements like attachments)
- stroke="currentColor", strokeWidth="1.5"
- strokeLinecap="round", strokeLinejoin="round"
- Color inherited from parent via CSS
- Small check/warning icons use strokeWidth="3" and fixed fill for visibility at 12x12

## Replicable Patterns

### Pattern: Step-based sequential animation

```tsx
const [step, setStep] = useState(0);
useEffect(() => {
  const timers = [
    setTimeout(() => setStep(1), 500),
    setTimeout(() => setStep(2), 1200),
    // ...
  ];
  return () => timers.forEach(clearTimeout);
}, []);
// In JSX: className={`element ${step >= 1 ? "visible" : ""}`}
```

### Pattern: Timing tuples (EmailDeepDive approach)

```tsx
const timings: [number, number][] = [
  [1, 800],    // step 1 at 800ms
  [2, 1600],   // step 2 at 1600ms
  [4, 4000],   // step 4 at 4000ms (gap = scene change)
];
const timers = timings.map(([s, ms]) => setTimeout(() => setStep(s), ms));
```

### Pattern: Staggered batch appearance

```tsx
for (let i = 0; i < batchSize; i++) {
  timers.push(setTimeout(() => setCount(i + 1), startMs + i * intervalMs));
}
```

### Pattern: Kanban card sorting

Cards defined with a `column` property. An `arrivalOrder` array shuffles the visual arrival sequence so cards don't appear grouped by column. A Set tracks which cards have arrived:

```tsx
const [arrivedSet, setArrivedSet] = useState<Set<number>>(new Set());
// In the timer:
setArrivedSet((prev) => new Set(prev).add(cardIdx));
// In JSX:
className={`triage-card ${arrivedSet.has(card.idx) ? "visible" : ""}`}
```

### Pattern: Brand bar

Every page starts with a slim header: Indemn logo left, "Inbox Associate" badge right. Consistent identity across all video segments. Badge styled as pill with iris accent color on 10% opacity background.

### Pattern: Accelerating cadence

Variable delay between items creates a sense of increasing speed:

```tsx
arrivalOrder.forEach((cardIdx, i) => {
  const delay = i < 5 ? 700 : i < 13 ? 450 : 300;
  t += delay;
  timers.push(setTimeout(() => { /* ... */ }, t));
});
```

## Recording

All pages recorded via Playwright headless browser at 1920x1080 as .webm, then assembled in Descript.

## Key Decisions

- HTML/CSS over Kling for all UI pages — Kling cannot render readable English text
- Kling used only for atmospheric establishing shots (office/desk, no screen content)
- No animation libraries — CSS transitions + setTimeout is sufficient and simpler
- Light theme matching Indemn brand (not dark mode) — conference booth readability
- Realistic insurance data throughout (real-sounding names, ACORD forms, coverage types)
- Query param routing over React Router — simpler for single-page-per-recording workflow
- React 19 with no additional dependencies — total package.json is react, react-dom, vite, typescript
- Each CSS file imports Barlow independently — no shared global stylesheet, keeps pages self-contained

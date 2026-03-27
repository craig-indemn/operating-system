# Video Production Playbook

Comprehensive reference for producing animated demo videos for product showcase pages. Covers the full pipeline: storyboard → build animated React pages → record with Playwright → trim with ffmpeg → assembly in Descript → embed on showcase page.

## Table of Contents

1. [Project Setup](#project-setup)
2. [Design System](#design-system)
3. [Animation Patterns](#animation-patterns)
4. [Component Patterns](#component-patterns)
5. [SVG Icon Pattern](#svg-icon-pattern)
6. [Narration Captions](#narration-captions)
7. [Recording with Playwright](#recording-with-playwright)
8. [Trimming with ffmpeg](#trimming-with-ffmpeg)
9. [Kling Cinematic Shots](#kling-cinematic-shots)
10. [Descript Assembly](#descript-assembly)
11. [Voiceover Scripts](#voiceover-scripts)
12. [Embedding on Showcase Pages](#embedding-on-showcase-pages)
13. [Common Mistakes](#common-mistakes)

---

## Project Setup

Each video gets its own project directory. The project is a Vite + React + TypeScript app with `?page=` query param routing — one route per animated scene.

### Directory Structure

```
demos/<video-name>/
  index.html
  package.json
  tsconfig.json
  vite.config.ts
  .gitignore
  public/
    brand/
      logo-iris.svg      # Indemn logo (iris color, for light backgrounds)
      logo-white.svg     # Indemn logo (white, for dark backgrounds)
  src/
    main.tsx             # Router — reads ?page= and renders the right component
    <PageName>.tsx       # One component per animated scene
    <pagename>.css       # Styles for each scene
    narration.css        # Shared narration bar styles
```

### package.json

```json
{
  "name": "<video-name>-demo",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^19.1.1",
    "react-dom": "^19.1.1"
  },
  "devDependencies": {
    "@types/react": "^19.1.0",
    "@types/react-dom": "^19.1.0",
    "@vitejs/plugin-react": "^4.4.1",
    "typescript": "^5.7.0",
    "vite": "^6.3.0"
  }
}
```

No animation libraries. No LiveKit dependencies (unless the video involves a live voice call). No external icon libraries — all icons are inline SVGs.

### vite.config.ts

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: { outDir: "build" },
  server: { fs: { strict: false } },
});
```

`server.fs.strict: false` is needed because `?page=` query params can trigger Vite's filesystem security check.

### index.html

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Demo</title>
    <style>
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body, #root { width: 100%; height: 100%; overflow: hidden; }
    </style>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

### main.tsx — Router

```tsx
import React from "react";
import ReactDOM from "react-dom/client";
import PageOne from "./PageOne";
import PageTwo from "./PageTwo";
// ... import all page components

const params = new URLSearchParams(window.location.search);
const page = params.get("page");

let Component: React.FC;
switch (page) {
  case "page-one": Component = PageOne; break;
  case "page-two": Component = PageTwo; break;
  // ... add cases for each page
  default: Component = PageOne;
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <Component />
);
```

**CRITICAL: Do NOT wrap in `<React.StrictMode>`.** StrictMode runs every `useEffect` twice in development (mount → unmount → remount). This causes animations to play forward, reset to blank, then play forward again — producing a visible flash/glitch in Playwright recordings.

### Brand Assets

Copy from the FNOL template or Smart Inbox project:
```bash
cp demos/smart-inbox/public/brand/*.svg demos/<new-video>/public/brand/
```

Two files: `logo-iris.svg` (for light backgrounds) and `logo-white.svg` (for dark backgrounds like the CTA).

### Setup Commands

```bash
cd demos/<video-name>
npm install
npx vite --port <port>   # Use a port not in use (check with lsof -i -P | grep LISTEN)
```

---

## Design System

All video pages use the Indemn brand. Consistent across every scene.

### Font

```css
@import url('https://fonts.googleapis.com/css2?family=Barlow:wght@300;400;500;600;700&display=swap');
font-family: 'Barlow', system-ui, sans-serif;
```

Import this at the top of every CSS file.

### Colors

| Name | Hex | Usage |
|------|-----|-------|
| **Iris** | `#4752a3` | Primary accent, links, badges, active states, card accents |
| **Lilac** | `#a67cb7` | Secondary accent, gradients, avatar backgrounds |
| **Eggplant** | `#1e2553` | Primary text, dark backgrounds, stats bars |
| **Lime** | `#e0da67` | Highlight text on dark backgrounds (stat numbers, emphasis) |
| **Background** | `#f4f3f8` | Page background (light lavender) |
| **Surface** | `#ffffff` | Card backgrounds |
| **Border** | `#d4d7e3` | Card borders, dividers |
| **Border light** | `#e8e7ed` | Inner dividers, section separators |
| **Border lightest** | `#f0eff5` | Row dividers within cards |
| **Text primary** | `#1e2553` | Headings, body text |
| **Text secondary** | `#6b7094` | Labels, timestamps, subtitles |
| **Success** | `#22c55e` | Complete states, AMS integration, sent confirmations |
| **Warning** | `#f59e0b` | Missing items, follow-up needed, pending states |
| **Error** | `#ef4444` | Stale/overdue badges |
| **Blue** | `#3b82f6` | Quote ready, informational |
| **Gray** | `#9ca3af` | Not-a-submission, filtered out |

### Card Style

```css
.card {
  background: #ffffff;
  border: 1px solid #d4d7e3;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
```

### Card Header

```css
.card-header {
  padding: 14px 20px;
  border-bottom: 1px solid #e8e7ed;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  font-weight: 600;
  color: #1e2553;
}
```

### Brand Bar

Every page starts with a slim header:

```css
.brand-bar {
  padding: 16px 36px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand-bar img { height: 24px; }

.brand-badge {
  font-size: 12px;
  font-weight: 600;
  color: #4752a3;
  background: rgba(71, 82, 163, 0.1);
  padding: 4px 12px;
  border-radius: 6px;
  letter-spacing: 0.03em;
}
```

Left: Indemn logo. Right: associate name badge (e.g., "Inbox Associate", "Claims Associate").

### Avatar Circles

For sender/agent avatars — initials on a colored circle:

```css
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
}
```

Use a rotating palette for variety:
```typescript
const avatarColors = [
  "#4752a3", "#a67cb7", "#3b82f6", "#22c55e", "#f59e0b",
  "#6366f1", "#ec4899", "#14b8a6", "#8b5cf6", "#ef4444",
  "#0ea5e9", "#f97316",
];
const color = avatarColors[index % avatarColors.length];
```

### Gradients

- **CTA background:** `linear-gradient(135deg, #4752a3 0%, #1e2553 100%)` (iris → eggplant)
- **Phone card (voice demos):** `linear-gradient(135deg, #4752a3, #1e2553)`
- **Completeness bar fill:** `linear-gradient(90deg, #4752a3, #a67cb7)` (iris → lilac)

---

## Animation Patterns

Every animated page uses the same core pattern. No animation libraries needed — CSS transitions do the heavy lifting, React orchestrates the sequence.

### Core Pattern: Step-Based Sequential Reveal

```tsx
const [step, setStep] = useState(0);

useEffect(() => {
  const timers = [
    setTimeout(() => setStep(1), 400),
    setTimeout(() => setStep(2), 1000),
    setTimeout(() => setStep(3), 1600),
    // ... more steps
  ];
  return () => timers.forEach(clearTimeout);
}, []);
```

In JSX, toggle CSS classes based on the step:

```tsx
<div className={`card ${step >= 1 ? "visible" : ""}`}>
```

In CSS, elements start hidden and transition in:

```css
.card {
  opacity: 0;
  transform: translateY(12px);
  transition: opacity 0.5s ease, transform 0.5s ease;
}

.card.visible {
  opacity: 1;
  transform: translateY(0);
}
```

**Why this works:** CSS handles the animation (smooth, GPU-accelerated). React handles the sequence (when things appear). setTimeout handles the timing (simple, predictable). No requestAnimationFrame, no spring physics, no external deps.

### Timing Tuples Pattern

For complex pages with many animation steps, use a typed array of `[step, milliseconds]` tuples:

```tsx
const timings: [number, number][] = [
  [1, 400],     // email card appears
  [2, 1000],    // attachment 1
  [3, 1500],    // attachment 2
  [4, 2500],    // extraction card
  [5, 3100],    // field 1
  // ... etc
];

const timers = timings.map(([s, ms]) => setTimeout(() => setStep(s), ms));
return () => timers.forEach(clearTimeout);
```

This is more readable than nested setTimeout calls and easier to tune timing.

### Staggered Batch Appearance

For multiple items appearing in a burst (email rows, card lists):

```tsx
const batchSize = 8;
const startMs = 300;
const intervalMs = 90;

for (let i = 0; i < batchSize; i++) {
  timers.push(setTimeout(() => setVisibleCount(i + 1), startMs + i * intervalMs));
}
```

### Accelerating Cadence

Makes sorting/processing feel like it's getting faster — creates energy:

```tsx
let t = 300;
items.forEach((item, i) => {
  const delay = i < 5 ? 500 : i < 13 ? 300 : 200;  // gets faster
  t += delay;
  timers.push(setTimeout(() => addItem(item), t));
});
```

This creates a natural "ramping up" feel — the system starts methodically, then hits its stride.

### Shuffled Arrival Order

For Kanban-style boards, don't add cards column-by-column (looks artificial). Define a shuffled arrival order:

```tsx
const arrivalOrder = [0, 8, 12, 1, 18, 9, 2, 13, 20, 3, ...];

arrivalOrder.forEach((cardIdx, i) => {
  timers.push(setTimeout(() => {
    setArrivedSet(prev => new Set(prev).add(cardIdx));
  }, startMs + i * delay));
});
```

Cards arrive in a mixed order, landing in their correct columns. Looks organic.

### CSS Transition Variants

Different entrance effects for variety:

**Fade up (default — cards, sections):**
```css
opacity: 0; transform: translateY(12px);
/* visible: */ opacity: 1; transform: translateY(0);
```

**Slide in from left (timeline items, list rows):**
```css
opacity: 0; transform: translateX(-8px);
/* visible: */ opacity: 1; transform: translateX(0);
```

**Scale pop (checkmarks, badges):**
```css
opacity: 0; transform: scale(0.5);
/* visible: */ opacity: 1; transform: scale(1);
```

**Fly in with overshoot (Kanban cards):**
```css
opacity: 0; transform: translateX(-60px) scale(0.95);
transition: opacity 0.35s ease, transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
/* visible: */ opacity: 1; transform: translateX(0) scale(1);
```

The cubic-bezier with a value > 1.0 creates a subtle overshoot/bounce.

### Width/Fill Animations

For progress bars and completeness indicators:

```css
.bar-fill {
  width: 0%;
  transition: width 0.8s ease;
}
.bar-fill.filled {
  width: 75%;  /* or whatever percentage */
}
```

---

## Component Patterns

Reusable page types that can be adapted for different associates.

### Inbox UI

Email client with sidebar + email list. Good for showing volume/incoming work.

**Layout:** Fixed sidebar (220px) with folder list + main area with email rows.
**Key elements:** Unread badge on folder (pulses on update), dot indicator per row, avatar circles with initials, sender email, subject line, timestamp, attachment icon.
**Animation:** Emails appear in batches with staggered row animations. Badge count updates with each batch.

Reference: `demos/smart-inbox/src/InboxCounter.tsx` + `inbox.css`

### Kanban Board

Cards sorting into color-coded columns. Good for triage/classification/workflow stages.

**Layout:** Full-width board with N columns. Each column has a colored header + white body area.
**Key elements:** Column headers with title + count badge, cards with avatar + subject + sender + colored tag.
**Animation:** Cards fly in from the left with accelerating cadence and shuffled order. Column counts appear after all cards land. Summary counter bar at bottom.

Reference: `demos/smart-inbox/src/EmailTriage.tsx` + `triage.css`

### Data Processing View

Two-column layout showing input → output. Good for extraction, analysis, transformation.

**Layout:** Left column (52%) for input + extraction. Right column for analysis + output.
**Key elements:** Input card (email/document), extraction card with field rows, gap analysis with check/warning icons, completeness bar, draft/output card, auto-action toggle with confirmation.
**Animation:** Sequential frame-by-frame reveal. Each frame focuses on one step (open → extract → analyze → draft → send).

Reference: `demos/smart-inbox/src/EmailDeepDive.tsx` + `deepdive.css`

### Results Board

Processed/completed state overview. Good for "zoom out" moments showing aggregate results.

**Layout:** N columns showing outcomes (fully processed, quotes extracted, drafts ready, etc.).
**Key elements:** Mini cards with status dots, status text, stale/overdue badges.
**Animation:** Columns appear one by one, then cards populate rapidly. Summary bar fades in at bottom.

Reference: `demos/smart-inbox/src/BoardZoomOut.tsx` + `zoomout.css`

### Stats Reveal

Clean stats view with animated counters. Good for impact/results summary.

**Layout:** Centered content — row of stat cards + detail items below + tagline.
**Key elements:** Large number (52px, iris color), label text, detail items with icons, closing tagline.
**Animation:** Stat cards appear one by one (fade up), then detail items, then tagline.

Reference: `demos/smart-inbox/src/StatsReveal.tsx` + `stats.css`

### CTA End Card

Shared closing card. Reuse across all videos.

**Layout:** Centered on iris→eggplant gradient background.
**Key elements:** White Indemn logo, channel icons (phone, mic, chat, email, SMS) with labels, tagline "Making insurance a conversation.", URL "indemn.ai".
**Animation:** Logo drops in, then icons appear one by one, then tagline fades, then URL fades.

Reference: `demos/smart-inbox/src/CTACard.tsx` + `cta.css`

The CTA component is identical across videos — copy it directly.

---

## SVG Icon Pattern

All icons are inline SVG React components. No icon library dependency. Consistent style:

```tsx
function EmailIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth="1.5"
      strokeLinecap="round" strokeLinejoin="round">
      <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
      <polyline points="22,6 12,13 2,6" />
    </svg>
  );
}
```

**Rules:**
- `width`/`height` of 18 for card header icons, 14 for inline/small icons, 28 for CTA channel icons
- `stroke="currentColor"` — color inherited from parent CSS
- `strokeWidth="1.5"` for standard, `"2"` or `"2.5"` for emphasis (checkmarks, badges)
- `fill="none"` — outline style, not filled
- `strokeLinecap="round"` and `strokeLinejoin="round"` always

For small check/warning icons inside colored circles:

```tsx
function CheckSmall() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none"
      stroke="white" strokeWidth="3"
      strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}
```

Note `stroke="white"` (not currentColor) when the icon sits on a colored circle background.

---

## Narration Captions

A fixed bar at the bottom of the page showing what the Inbox Associate is doing. Helps viewers understand the video without audio.

### CSS (narration.css — shared across all pages)

```css
.narration-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(30, 37, 83, 0.92);
  padding: 14px 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.narration-text {
  font-family: 'Barlow', system-ui, sans-serif;
  font-size: 22px;
  font-weight: 500;
  color: #ffffff;
  letter-spacing: 0.01em;
  text-align: center;
  opacity: 0;
  transition: opacity 0.4s ease;
}

.narration-text.visible { opacity: 1; }

.narration-highlight {
  color: #e0da67;
  font-weight: 600;
}
```

### CRITICAL: Separate State for Narration

**Never share the animation step state with narration.** If you use `setStep(30)` for a narration cue, every check like `step >= 1`, `step >= 10`, `step >= 17` becomes true — showing ALL cards at once.

**Wrong:**
```tsx
const [step, setStep] = useState(0);
// step 1-24: card visibility
// step 30: narration "Extracting data..."  ← BUG: step 30 >= all thresholds
```

**Correct:**
```tsx
const [step, setStep] = useState(0);         // card visibility (1-24)
const [narrationIdx, setNarrationIdx] = useState(-1);  // narration text (0-4)

// Separate timer arrays:
const timers = timings.map(([s, ms]) => setTimeout(() => setStep(s), ms));
const nTimers = narrationTimings.map(([s, ms]) => setTimeout(() => setNarrationIdx(s), ms));
```

### Implementation Pattern

```tsx
const narrationTexts = [
  "New submission from Worthington Insurance",
  "Extracting data from ACORD 125 and 126",
  "Running completeness check",
  "Generating follow-up reply",
  "Reply sent automatically",
];
const activeNarration = narrationIdx >= 0 ? narrationTexts[narrationIdx] : null;

// In JSX:
<div className="narration-bar">
  {activeNarration && (
    <span className="narration-text visible" key={narrationIdx}>
      {activeNarration}
    </span>
  )}
</div>
```

The `key={narrationIdx}` forces React to re-mount the element on each change, triggering the CSS fade-in transition.

### When to Use Narration

- Pages with complex multi-step processes (data extraction, analysis, drafting)
- Pages where the visual alone doesn't explain what's happening
- NOT on simple pages like CTA, stats (the text on screen is self-explanatory)

---

## Recording with Playwright

Record each page as a video using Playwright's headless browser.

### Prerequisites

Playwright must be installed globally:
```bash
npm install -g playwright
```

Verify: `NODE_PATH=/opt/homebrew/lib/node_modules node -e "const { chromium } = require('playwright'); console.log('OK');"`

### Recording Script

```bash
NODE_PATH=/opt/homebrew/lib/node_modules node -e "
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    recordVideo: { dir: '/tmp/pw-<page>', size: { width: 1920, height: 1080 } }
  });
  const page = await context.newPage();
  await page.goto('http://localhost:<port>/?page=<page>');
  await page.waitForTimeout(<duration_ms>);
  await context.close();
  await browser.close();
  console.log('done');
})();
"
```

**Parameters:**
- `viewport` and `recordVideo.size` must both be `1920x1080` for consistent output
- `duration_ms` = animation duration + 2s buffer (trim the buffer later with ffmpeg)
- `dir` = temp directory for the webm output (one per page to avoid filename collisions)

### Batch Recording

Record all pages in a single script:

```javascript
const pages = [
  { name: 'inbox', page: 'inbox', dur: 5000 },
  { name: 'triage', page: 'triage', dur: 12000 },
  { name: 'deepdive', page: 'deepdive', dur: 19000 },
  // ... etc
];
for (const p of pages) {
  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    recordVideo: { dir: '/tmp/pw-' + p.name, size: { width: 1920, height: 1080 } }
  });
  const page = await context.newPage();
  await page.goto('http://localhost:5180/?page=' + p.page);
  await page.waitForTimeout(p.dur);
  await context.close();
  await browser.close();
}
```

Must create a new browser instance per page (Playwright ties video recording to the browser context lifecycle).

### Output

Playwright produces `.webm` files in the specified directory. These need conversion to MP4 via ffmpeg.

---

## Trimming with ffmpeg

Convert Playwright webm to MP4 and trim the start/end.

### Why Trim

- **Start (0.3s):** Playwright takes ~300ms to load and render the page. The first few frames may show a blank or flash of unstyled content.
- **End:** The recording includes the buffer time added for safety. The animation is done but the video keeps recording blank frames.

### Basic Trim + Convert

```bash
ffmpeg -y -ss 0.3 -i input.webm -t <duration> \
  -c:v libx264 -pix_fmt yuv420p -preset fast -crf 18 \
  output.mp4
```

**Flags:**
- `-ss 0.3` — skip first 0.3s (Playwright render delay)
- `-t <duration>` — keep this many seconds after the start point
- `-c:v libx264` — H.264 codec (universal compatibility)
- `-pix_fmt yuv420p` — pixel format for maximum player compatibility
- `-preset fast` — encoding speed (fast is good enough, smaller files than ultrafast)
- `-crf 18` — quality (18 = visually lossless, 23 = default, lower = better)

### Batch Trim Script

```bash
DEST=~/Desktop/<video-name>-assets

for pair in \
  "inbox:01-inbox-counter:0.3:4.0" \
  "triage:02-email-triage:0.3:10.5" \
  "deepdive:03-email-deepdive:0.3:18.0"; do

  src=$(echo $pair | cut -d: -f1)
  dst=$(echo $pair | cut -d: -f2)
  ss=$(echo $pair | cut -d: -f3)
  dur=$(echo $pair | cut -d: -f4)
  webm=$(ls /tmp/pw-${src}/*.webm 2>/dev/null | head -1)

  ffmpeg -y -ss "$ss" -i "$webm" -t "$dur" \
    -c:v libx264 -pix_fmt yuv420p -preset fast -crf 18 \
    "${DEST}/${dst}.mp4" 2>/dev/null

  actual=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "${DEST}/${dst}.mp4")
  echo "${dst}.mp4 — ${actual}s"
done
```

### Naming Convention

Prefix with numbers for timeline order: `01-inbox-counter.mp4`, `02-email-triage.mp4`, etc. This makes drag-and-drop into Descript intuitive.

---

## Kling Cinematic Shots

Kling 3.0 (klingai.com) generates AI video clips. Use **only for atmospheric establishing shots** — NOT for UI content.

### What Kling Cannot Do

- Render readable English text on screens (generates Chinese gibberish)
- Reproduce specific UI layouts
- Match exact brand colors or typography

### What Kling Does Well

- Cinematic real-world scenes (offices, desks, hands, coffee cups, parking lots)
- Camera movements (dolly, pan, rack focus)
- Lighting and atmosphere (golden hour, morning light, studio lighting)
- Physical simulations (cars, objects, people walking)

### Prompt Pattern

Describe a real-world scene with NO screen content:

```
Close-up of a coffee mug on a modern office desk, early morning.
Soft golden light streams through a window. A laptop sits open in
the background, slightly out of focus. A hand reaches for the coffee.
Calm, quiet, the start of a workday. Cinematic, photorealistic,
shallow depth of field.
```

**Settings:** 16:9 aspect ratio, 5 second duration, Pro plan ($8/month)

### Trimming Kling Clips

Kling clips often have inconsistent starts or ends. Trim to the best 2-3 seconds:

```bash
ffmpeg -y -ss 0.5 -i kling_clip.mp4 -t 2.5 \
  -c:v libx264 -pix_fmt yuv420p -preset fast -crf 18 \
  00-establishing.mp4
```

### When to Use Kling

- 2-3 second establishing shot at the start of a video
- Transitional atmosphere between sections
- NOT for any content that needs readable text

---

## Descript Assembly

Descript (descript.com) is a desktop app for final video assembly. This is a manual step — Claude provides the guide, the user executes.

### Project Setup

1. Open Descript → New Project → name it
2. Drag all numbered MP4 files from the assets folder into the media panel
3. Drag onto the timeline in order — each becomes a Scene

### Transitions

| Type | When to Use |
|------|-------------|
| **Cut** (direct) | Sharp moments — system kicks into action, mode change |
| **Cross dissolve** (0.3-0.5s) | Most transitions — smooth visual handoff |
| **Fade to black** | End of video, before CTA |

### Music

- No-dialogue videos: music at **-6 to -8 dB** (prominent)
- Voiceover videos: music at **-12 to -16 dB** with auto-ducking enabled
- Stock music search terms: "corporate technology", "progress", "momentum", "workflow"
- Music should build during action sequences, settle during detail/focus moments

### Voiceover Integration

If the user records a voiceover:
1. Import the audio file (.m4a, .wav, .mp3) into the project
2. Drag onto a second audio track
3. Align to the timeline (Descript can auto-sync if the VO references visual cues)
4. Enable auto-ducking on the music track (Settings → Audio → Auto-duck)

### Export Settings

- Format: MP4
- Codec: H.264
- Resolution: 1080p (or 4K if available on plan)
- Frame rate: 30fps
- Audio: AAC 256kbps

### What to Provide the User

When the assets are ready, provide:
1. **Asset inventory table** — filename, duration, size for each file
2. **Timeline order** — which file goes where
3. **Transition recommendations** — between each pair of scenes
4. **Music guidance** — volume level, energy curve
5. **VO script** (if applicable) — timed to the video with timestamps
6. **Review checklist** — what to verify before exporting

---

## Voiceover Scripts

### Writing Approach

- **Conversational, not performative.** Talk like you're walking someone through a demo at your desk.
- **Describe what's on screen.** Don't narrate dramatically — just explain what the system is doing.
- **Short sentences.** Each line should fit comfortably in its time window.
- **Let visuals breathe.** Not every second needs words. Silence during satisfying animations (sorting, processing) is powerful.
- **No taglines in the VO.** The tagline is on screen in the stats/CTA — don't read it aloud.
- **Avoid reading numbers that are on screen.** The viewer can see them. Say "all of that in about three minutes" instead of "twenty-three emails, three minutes, eight resolved, fifteen drafts."
- **Don't say "no human touch" or "replaces humans."** Say "your team just reviews what's ready."

### Timing Script to Video

1. Calculate the assembled timeline from asset durations
2. Write lines that fit naturally in each segment's time window
3. Test by reading aloud with a timer — if you can't say it comfortably, cut words
4. Iterate with the user — they'll know if it feels rushed

### Recording

The user records themselves (Voice Memos, QuickTime, or any recorder). The audio file is imported into Descript and aligned to the timeline.

---

## Embedding on Showcase Pages

### Video Hosting

Upload the final MP4 to the blog's `public/videos/` directory (for self-hosting) or to a CDN/S3 bucket.

For the Astro blog at blog.indemn.ai:
```
public/videos/products/<slug>-demo.mp4
```

### HTML Video Tag

In the MDX page, embed with a native `<video>` tag:

```html
<video
  autoplay
  muted
  loop
  playsinline
  style="width: 100%; border-radius: 12px; margin: 2rem 0;"
>
  <source src="/videos/products/<slug>-demo.mp4" type="video/mp4" />
</video>
```

**Attributes:**
- `autoplay` + `muted` — browsers require muted for autoplay
- `loop` — continuous playback on the page
- `playsinline` — prevents fullscreen on iOS
- `controls` — add if the video has voiceover (users need play/pause/volume)

For videos with voiceover, use `controls` instead of `autoplay muted loop`:
```html
<video controls playsinline style="width: 100%; border-radius: 12px; margin: 2rem 0;">
  <source src="/videos/products/<slug>-demo.mp4" type="video/mp4" />
</video>
```

### Using TabbedDemo Component

The existing `TabbedDemo` component in the showcase system supports video tabs via frontmatter:

```yaml
tabbedDemo:
  tabs:
    - label: "Demo Video"
      type: video
      src: "/videos/products/<slug>-demo.mp4"
    - label: "How It Works"
      type: video
      src: "/videos/products/<slug>-explainer.mp4"
```

This renders a tabbed viewer that switches between multiple videos.

### File Size Considerations

- Conference demo videos (~1min) at 1080p/CRF 18 are typically 5-15MB
- For web embedding, consider re-encoding at CRF 23 for smaller files:
  ```bash
  ffmpeg -y -i final.mp4 -c:v libx264 -pix_fmt yuv420p -preset slow -crf 23 web-version.mp4
  ```
- For very large videos (>20MB), consider hosting on S3 with CloudFront CDN

---

## Common Mistakes

| Mistake | Consequence | Fix |
|---------|-------------|-----|
| Wrapping in `<React.StrictMode>` | Animations play, reset, play again — visible glitch in recording | Remove StrictMode from main.tsx |
| Sharing state between narration and card visibility | `setStep(30)` triggers all `step >= N` checks — everything appears at once | Use separate `narrationIdx` state |
| Not trimming Playwright start | First 0.3s shows blank/flash of unstyled content | `ffmpeg -ss 0.3` |
| Recording on an occupied port | Wrong app's UI gets recorded | Check `lsof -i :<port>` before starting |
| Kling prompts asking for readable text | Generates Chinese gibberish | Use Kling only for atmospheric scenes, no screen content |
| Trying to speed up segments in Descript | Grouped clips speed up together, audio desyncs | Fix timing at the source (animation code), re-record |
| Adding too many words to VO script | Can't say lines in the time window, sounds rushed | Read aloud with timer, cut until comfortable |
| Using `?page=` URL without `server.fs.strict: false` | Vite 403 Restricted error | Add to vite.config.ts server options |
| Not restarting dev server after code changes | Playwright records stale code | Kill and restart: `lsof -i :<port> -t \| xargs kill` |
| Using animation libraries (framer-motion, etc.) | Unnecessary dependency, larger bundle, harder to debug timing | useState + setTimeout + CSS transitions is sufficient |
| Putting VO numbers that duplicate on-screen stats | Redundant, sounds like reading a list | Let visuals show numbers, VO describes impact |
| Saying "no human touch" / "replaces humans" | Sounds threatening to insurance audience | Say "your team just reviews what's ready" |

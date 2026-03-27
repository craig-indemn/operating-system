---
ask: "Detailed production plan for InsurtechNY conference demo videos — every step, tool, and deliverable"
created: 2026-03-26
workstream: content-system
session: 2026-03-26-b
sources:
  - type: web
    description: "Research on AI video generation tools (Kling, Runway, Higgsfield, HeyGen, etc.)"
  - type: web
    description: "Research on video editing/assembly tools (Descript, CapCut, DaVinci Resolve, etc.)"
  - type: web
    description: "LiveKit Composite Egress documentation"
---

# Conference Video Production Plan — InsurtechNY Spring 2026

Source of truth for producing two demo videos for the InsurtechNY Spring conference booth at Chelsea Piers.

## Tool Stack

| Tool | Role | Access | Cost |
|---|---|---|---|
| **Kling 3.0** | Cinematic AI video clips | klingai.com (web app) | ~$8/month Pro |
| **Runway Gen-4** | Backup for shots Kling can't nail | runwayml.com (web app) | ~$35/month Pro (only if needed) |
| **LiveKit** | Real voice call recording with branded composite template | Existing dev infrastructure (EC2) | Already have |
| **HTML/CSS** | UI screens — dashboards, email detail, branded cards, CTA | Built in blog site or standalone | In-house |
| **Descript** | Final assembly — stitch acts, captions, music, transitions | descript.com (Mac app) | ~$33/month Business |
| **HeyGen Avatar IV** | Option 3 upgrade — AI avatar "Maya" | heygen.com (web app) | ~$29/month Creator (later) |

## Accounts Needed Before Starting

- [ ] Kling 3.0 — sign up at klingai.com, Pro plan ($8/month)
- [ ] Descript — sign up at descript.com, Business plan ($33/month) for 4K export + brand kits
- [ ] LiveKit — already have (dev instance on EC2)
- [ ] Runway — only if Kling doesn't cut it (sign up later if needed)
- [ ] HeyGen — only for Option 3 upgrade (sign up later if needed)

---

# Video 1: FNOL (Intake Associate for Claims)

**Total runtime target: ~2 minutes**
**Format: 16:9, 1080p minimum (4K preferred), must work with and without sound**

## Step 1: Generate Act 1 — Parking Lot Scene

**Tool:** Kling 3.0
**Deliverable:** 5-second cinematic clip of a minor parking lot fender bender
**Duration:** ~5 seconds

### What to generate
A subtle, realistic scene: afternoon light, a retail parking lot (like a Kroger/grocery store), a car backing into a parked car. Not dramatic — no crash, no airbags. Just a "thud" moment. Think security camera footage feel but with cinematic quality.

### Kling workflow
1. Go to klingai.com → Text-to-Video (or Image-to-Video if we have a reference frame)
2. Select Kling 3.0 model, Professional mode
3. Aspect ratio: 16:9
4. Duration: 5 seconds
5. Prompt (iterate on this):
   - "Afternoon in a suburban grocery store parking lot. A silver sedan slowly backs out of a parking space and bumps into the rear of a parked dark blue Honda Accord. Subtle impact, realistic. Warm afternoon sunlight. Cinematic, photorealistic. No people visible."
6. Generate 3-5 variations, select the best
7. Budget: ~40-100 credits (~$1-3)

### Post-processing
- Add text overlay in Descript: **"2:47 PM. Kroger parking lot. Someone just backed into your car."**
- Text style: clean sans-serif, white with subtle shadow, lower third or centered
- Optional: slight slow-motion on the impact moment

### Output
- `act1-parking-lot.mp4` (5 seconds, 16:9, 1080p+)

---

## Step 2: Build LiveKit Composite Web Template

**Tool:** HTML/CSS/JS (custom web page)
**Deliverable:** A web page that LiveKit's Room Composite Egress renders during call recording

### What the template shows
The viewer sees a branded split layout during the phone call:

**Left side (~60% width): Phone call UI**
- Realistic phone call screen (iOS-style or clean branded design)
- Shows: caller name ("Mike Reynolds"), call timer ticking, audio waveform/visualization
- Carrier branding at top: "Acme Insurance" logo or text
- The phone UI is the emotional anchor — this is what the customer sees

**Right side (~40% width): Live transcript**
- Conversation transcript appearing in real-time as each person speaks
- Speaker labels: "Maya" (associate) and "Mike" (caller)
- Maya's lines in one color (e.g., Indemn blue/teal), Mike's in another (neutral gray)
- Auto-scrolls as conversation progresses
- This is the accessibility layer — booth viewers can read along without hearing

**Bottom: Captions bar**
- Real-time captions of whoever is currently speaking
- Large, readable font — this needs to work from 10 feet away at a booth
- Speaker-attributed: shows who's talking

**Overall styling:**
- Dark background (Indemn brand dark)
- Clean, minimal, professional
- Indemn logo subtle in corner
- No clutter — the conversation is the focus

### Technical approach
1. Create an HTML page that connects to a LiveKit room
2. Subscribe to audio tracks from both participants
3. Use LiveKit's real-time transcription to feed the transcript panel and captions
4. Style with CSS matching Indemn brand
5. The page is the "template" that Room Composite Egress renders into the recording

### Alternative approach (simpler)
If the LiveKit composite template is too complex to build quickly:
- Record the raw call audio only (LiveKit audio egress)
- Build the phone UI + transcript as a separate animation/video
- Sync them in Descript in post-production
- This loses the "real-time" feel but is faster to produce

### Output
- `livekit-fnol-template/` directory with HTML/CSS/JS
- OR decision to go with post-production sync approach

---

## Step 3: Configure FNOL Dev Agent

**Tool:** Indemn platform (dev instance on EC2)
**Deliverable:** A working voice agent that handles FNOL intake, accessible via LiveKit

### Agent configuration

**Name:** Maya (Acme Insurance Claims Associate)

**System prompt (draft — refine before recording):**
```
You are Maya, a claims intake associate for Acme Insurance. You handle First Notice of Loss (FNOL) calls.

Your personality:
- Conversational and natural — not robotic, not overly sympathetic
- Efficient but warm — you care, but you also get things done
- You sound like a smart, competent person, not a script-reader

Call flow:
1. Greet: "Hi, this is Acme Insurance, this is Maya. How can I help you?"
2. Check safety: Ask if anyone is hurt
3. Collect policyholder name
4. Look up policy (the caller is Mike Reynolds, policy #ACM-2023-7841, vehicle: 2023 Honda Accord, dark blue)
5. Confirm vehicle
6. Get incident details: what happened, when, where
7. Get other party info: name, license plate, their insurance
8. Get damage description
9. Close the claim:
   - Claim number: CLM-2026-04281
   - Assigned adjuster: Sarah Martinez
   - She'll reach out within 24 hours
   - Texting a link for photo uploads
10. Ask if there's anything else, close warmly: "Drive safe."

Important:
- Keep the conversation flowing naturally. Don't ask questions in a rigid checklist order — adapt to what the caller says.
- If the caller provides multiple details at once, acknowledge them all rather than re-asking.
- The "...that's it?" moment at the end is the payoff. Be casual: "That's it. You're all set."
- Total call should be under 2 minutes.
```

**Voice settings:**
- TTS provider: Cartesia (current default) or ElevenLabs
- Voice: Female, natural, mid-range pitch, American English
- Speed: Conversational (not fast, not slow)
- Test several voice options before recording

**LiveKit room configuration:**
- Create a dev room for the recording
- Enable room composite egress (if using template approach)
- Enable individual track egress (separate audio tracks for post-production)
- Enable real-time transcription (for transcript panel / captions)

### Testing before recording
1. Make 2-3 test calls to verify:
   - Agent follows the flow naturally
   - Voice sounds good
   - Transcription is accurate
   - Policy lookup is hardcoded correctly
   - Claim number is delivered as scripted
2. Adjust prompt if agent is too rigid or too loose
3. Verify LiveKit recording is capturing correctly

### Output
- Working FNOL agent on dev LiveKit instance
- Confirmed voice selection
- Successful test recording

---

## Step 4: Record the Call

**Tool:** LiveKit (you call in as Mike)
**Deliverable:** The Act 2 recording — either composite video or raw audio tracks

### Preparation
- Review the script (loosely — don't memorize, be natural)
- Find a quiet room for recording (no background noise)
- Use a good microphone if available (AirPods Pro work, external mic better)
- Have the script visible for reference but don't read from it

### Recording session
1. Start LiveKit room recording (composite egress or track egress)
2. Join the room as "Mike Reynolds"
3. The agent (Maya) picks up
4. Have the conversation following the script loosely
5. Key beats to hit:
   - The greeting exchange
   - "Are you okay?" / "Everyone's fine"
   - Name → policy lookup → vehicle confirmation
   - Incident description (parking lot, backed into, exchanged info)
   - Other driver's info
   - Damage description (bumper, taillight)
   - Claim number delivery
   - **"...that's it?"** — this is the emotional beat, pause before saying it
   - "Drive safe" close
6. Do 3-5 takes — pick the best one
7. Stop recording

### What you get
- If composite egress: `act2-call-composite.mp4` — branded video + audio in one
- If track egress: `act2-maya-audio.wav` + `act2-mike-audio.wav` — separate tracks
- Either way: `act2-transcript.json` — timestamped transcript from LiveKit

### Output
- Best take selected
- Audio and/or video files exported from LiveKit

---

## Step 5: Build Act 3 — Dashboard Reveal

**Tool:** HTML/CSS (standalone page or blog site component)
**Deliverable:** Screen recording of a claims dashboard showing everything that was auto-created

### What the dashboard shows
A clean, professional claims management interface. NOT a real product — a representative mockup that shows the outcome. Design it to feel real but don't overthink it.

**Dashboard elements:**

**Claim record card:**
- Claim #: CLM-2026-04281
- Status: Open — Pending Adjuster Review
- Policyholder: Mike Reynolds
- Policy #: ACM-2023-7841
- Vehicle: 2023 Honda Accord (Dark Blue)
- Date of Loss: March 28, 2026, 2:47 PM
- Location: Kroger parking lot, 1450 Main St
- Type: Auto — Collision (Not at Fault)
- Description: Rear-end impact while parked. Other driver backed into insured vehicle.
- Other Party: [Name], [Plate], [Insurance]
- Damage: Rear bumper (dented), taillight (cracked)

**Adjuster assignment card:**
- Assigned to: Sarah Martinez
- Assignment method: Auto-assigned (location + availability)
- ETA for contact: Within 24 hours
- Status: Notified at 2:49 PM

**Activity timeline:**
- 2:47 PM — Call received from Mike Reynolds
- 2:47 PM — Identity verified, policy ACM-2023-7841 matched
- 2:48 PM — FNOL intake completed (all required fields captured)
- 2:49 PM — Claim CLM-2026-04281 created
- 2:49 PM — Adjuster Sarah Martinez auto-assigned
- 2:49 PM — Photo upload link sent via SMS to (555) 867-5309
- 2:49 PM — Manager notification sent (new claim flagged for review)
- 2:49 PM — FNOL report filed to carrier system

**Design approach:**
- Clean, modern dashboard aesthetic (think Linear, Notion, or our own showcase components)
- Cards with subtle shadows, clean typography
- Activity timeline with timestamps and status indicators
- Indemn-branded but carrier-agnostic (could be any carrier's claims system)

### Animation approach
Two options:

**Option A — Animated build-up (preferred):**
Build the page with CSS animations so elements appear sequentially:
1. Claim card fades in with fields populating
2. Adjuster card slides in
3. Timeline entries appear one by one from top to bottom
4. Each entry has a subtle "check" animation as it completes
Screen record this animation playing.

**Option B — Static with pan:**
Build the full dashboard as a static page. Screen record a slow scroll/pan across it. Simpler but less dynamic.

### Text overlay
After the dashboard is fully visible, overlay:
**"2 minutes. Zero hold time. Zero data entry. Claim resolved before he left the parking lot."**

### Output
- `act3-dashboard-reveal.mp4` (15-20 seconds, 16:9, 1080p+)

---

## Step 6: Build Act 4 — CTA End Card

**Tool:** HTML/CSS (simple branded page)
**Deliverable:** Screen capture or exported image/video of CTA card

### Design
- Dark background (Indemn brand dark, matching Act 2 template)
- Indemn logo centered or top
- Channel icons appear in a row: phone, web voice, web chat, email, SMS
  - Use simple, clean icons (line style, white or Indemn teal)
  - Each icon could animate in sequentially
- Text below icons: **"One associate. Every channel."**
- Below that: **"indemn.ai"** (or conference-specific URL if they have one)
- Clean, minimal, confident

### Animation
- Fade in from black
- Icons appear one by one (left to right), quick succession (~0.3s each)
- Text fades in after icons are all visible
- Hold for 3-4 seconds
- Fade to black (or hold)

### Output
- `act4-cta.mp4` (5 seconds, 16:9, 1080p+)

---

## Step 7: Assemble in Descript

**Tool:** Descript (Business plan)
**Deliverable:** Final FNOL demo video, ready to play at conference booth

### Import assets
1. `act1-parking-lot.mp4` (Kling-generated, 5s)
2. `act2-call-composite.mp4` or separate audio tracks + template recording
3. `act3-dashboard-reveal.mp4` (screen-recorded animated dashboard, 15-20s)
4. `act4-cta.mp4` (branded end card, 5s)
5. Background music track (select from Descript's library or a royalty-free source)

### Assembly steps

**1. Create new Descript project: "FNOL Demo — InsurtechNY"**

**2. Build the timeline as Scenes:**
- Scene 1: Act 1 (parking lot + text overlay)
- Scene 2: Act 2 (the call — longest segment)
- Scene 3: Act 3 (dashboard reveal + text overlay)
- Scene 4: Act 4 (CTA)

**3. Transitions between acts:**
- Act 1 → Act 2: Quick fade or cut (the phone appearing should feel immediate — "ok, time to deal with this")
- Act 2 → Act 3: Smooth transition — maybe a brief pause/fade, then the dashboard appears. This is the "reveal" moment, so give it a beat of breathing room.
- Act 3 → Act 4: Fade to the CTA card

**4. Captions:**
- If captions are NOT baked into the LiveKit composite template:
  - Use Descript's auto-caption feature on the Act 2 audio
  - Style: large, readable, speaker-attributed
  - Position: bottom of frame
  - Font: match Indemn brand (clean sans-serif)
- If captions ARE in the composite template, verify they're readable and skip Descript captions

**5. Music:**
- Add a subtle background music track — low-key, professional, not emotional
- Use Descript's auto-ducking: music dips automatically during dialogue (Act 2)
- Music should be present but barely noticeable during the call
- Music can be slightly louder during Acts 1, 3, and 4 (no dialogue)
- Select something modern, clean, neutral — think corporate video but not cheesy

**6. Audio levels:**
- Voice dialogue: primary (0 dB reference)
- Background music: -18 to -24 dB during dialogue, -10 to -14 dB during non-dialogue acts
- Normalize/master the full video so levels are consistent

**7. Review and polish:**
- Watch the full video 3-5 times
- Check: is every text overlay readable at a glance?
- Check: can you follow the story with sound OFF?
- Check: does the "...that's it?" beat land? Is there a pause before it?
- Check: are transitions smooth?
- Check: does the music feel right?

**8. Export:**
- Format: MP4, H.264
- Resolution: 1080p (or 4K if all source assets support it)
- Frame rate: 30fps
- Audio: AAC, 256kbps
- Export a second copy at lower resolution for tablet playback (720p) if needed

### Output
- `fnol-demo-final.mp4` — the finished video
- `fnol-demo-final-720p.mp4` — tablet-friendly version (if needed)

---

# Video 2: Smart Inbox (Inbox Associate)

**Total runtime target: ~2 minutes**
**Format: 16:9, 1080p minimum (4K preferred), no dialogue — purely visual with music**

## Step 1: Generate Act 1 — Inbox Counter

**Tool:** Kling 3.0 or HTML/CSS animation
**Deliverable:** 5-second clip of an inbox filling up

### Option A — Kling generated
Prompt: "Close-up of a computer screen showing an email inbox. New emails arrive rapidly, unread count climbing: 8, 14, 23. Professional email client interface. Soft morning light on the monitor. Photorealistic, cinematic."

This is tricky because AI video generators struggle with legible text on screens. If the generated clip looks good enough as an atmospheric impression (you can tell it's an inbox filling up even if you can't read every word), it works.

### Option B — HTML/CSS animation (fallback)
Build a simple email inbox UI with an animated counter. Screen record it. More control, guaranteed legibility. Less cinematic but more precise.

### Post-processing
- Add text overlay: **"Monday. 8:00 AM. 23 submissions arrived overnight."**

### Output
- `inbox-act1-counter.mp4` (5 seconds, 16:9)

---

## Step 2: Generate Act 2 Phase 1 — Email Triage (Macro View)

**Tool:** Kling 3.0 (primary) + possibly HTML/CSS animation
**Deliverable:** ~15-second clip of emails flowing into a pipeline and sorting into lanes

### What this looks like
This is the "mesmerizing factory" shot. Emails (represented as cards/envelopes/items) flow from the left side of the screen into a sorting system. They get color-coded labels and sort into distinct lanes/columns:
- Green: "New Submission"
- Blue: "Quote Ready"
- Orange: "Follow-Up Needed"
- Purple: "Renewal"
- Gray: "Not a Submission"

The feel is: organized chaos becoming order. Like watching a factory sorting line or an airport baggage system.

### Approach A — Kling cinematic
Prompt: "Top-down view of a digital pipeline dashboard. Email envelopes flow in from the left and sort into color-coded columns — green, blue, orange, purple, gray. Each email gets a label as it sorts. Clean, modern interface design. Smooth animation. Professional, satisfying to watch. Dark background."

This might be too abstract for Kling to nail precisely, but the motion and feel could be right even if text isn't readable.

### Approach B — Hybrid
Build the pipeline board as HTML/CSS with animated cards. Screen record the sorting animation. Use Kling for a cinematic transition INTO this view (camera zooming out to reveal the board).

### Approach C — Full HTML/CSS
Build the entire triage animation as a web page. Cards appear, labels animate on, cards slide into columns. Full control, guaranteed readability, but requires more build time.

### Post-processing
- Add counter overlay: "23 classified in 47 seconds"
- Ensure labels are readable — if Kling output has illegible text, overlay clean text in Descript

### Output
- `inbox-act2-triage.mp4` (~15 seconds, 16:9)

---

## Step 3: Build Act 2 Phase 2 — Email Deep Dive (Micro View)

**Tool:** HTML/CSS (built frontend — needs readable text)
**Deliverable:** ~40-second screen recording of one email being processed end-to-end

### This MUST be built, not generated
This section has specific text that needs to be readable: email addresses, ACORD form fields, gap analysis items, a draft reply, AMS integration callout. AI video generators can't produce this reliably.

### UI design
Build as a single-page web app with CSS animations that play sequentially:

**Frame 1 — Email opens (~5s)**
- Email header appears: From, Subject, Attachments
- From: jessica.parker@worthington-insurance.com
- Subject: New Submission — Riverside Landscaping LLC
- Attachments: ACORD 125.pdf, ACORD 126.pdf (with PDF icons)

**Frame 2 — Data extraction (~10s)**
- ACORD form visual opens/unfolds
- Data fields populate one by one with a typing/fill animation:
  - Business: Riverside Landscaping LLC
  - Revenue: $1.2M
  - Employees: 14
  - Operations: Commercial landscaping, tree removal
  - Requested: GL $1M/$2M
- As fields populate, they simultaneously flow into an AMS panel on the right
- Subtle callout appears: **"Direct AMS integration — no API required"**

**Frame 3 — Gap analysis (~8s)**
- Checklist animates:
  - ✅ Business info — complete
  - ✅ Operations — complete
  - ⚠️ Loss runs — missing
  - ⚠️ Subcontractor schedule — missing
  - ✅ Requested coverage — complete
- Completeness bar fills to 6/8 (75%)

**Frame 4 — Draft reply (~12s)**
- Email draft composes itself (typing animation):
  > "Hi Jessica — thanks for sending over Riverside Landscaping. I've reviewed the ACORD 125 and 126. To move forward, I'll need:
  > 1. Three years of loss runs
  > 2. Subcontractor schedule with certificates
  >
  > Everything else looks good. Happy to prioritize this once those come in."
- Toggle visible: **"Auto-send: ON"**
- Status changes: "Auto-sent at 8:01 AM" ✓

**Frame 5 — Transition (~5s)**
- This email card minimizes/slides back into the board
- Camera begins to pull back

### Design style
- Dark mode, matching the macro view aesthetic
- Cards with subtle glow/shadow
- Smooth animations (CSS transitions, 300-500ms easing)
- Typography: clean, professional, readable at 1080p
- Color palette: Indemn brand colors for accents, neutral for data

### Screen recording
- Use a screen recording tool (OBS, macOS screen recording, or Descript's built-in recorder)
- Record at 1080p or higher
- Ensure smooth 30fps or 60fps capture

### Output
- `inbox-act2-deepdive.mp4` (~40 seconds, 16:9, 1080p+)

---

## Step 4: Generate/Build Act 2 Phase 3 — Zoom Out

**Tool:** Kling 3.0 and/or HTML/CSS
**Deliverable:** ~15-second clip pulling back to show the full processed board

### What this shows
After the deep dive, we pull back to see the full pipeline board. While we were watching one email, the rest were processed.

### Approach
Two options depending on how Phase 1 was produced:

**If Phase 1 was Kling:** Generate a matching Kling clip showing the completed board (all lanes populated, counters showing processed items). Use image-to-video with a screenshot of the completed board as the starting frame.

**If Phase 1 was HTML/CSS:** Extend the same web page animation. After the deep dive card returns to the board, the board populates with results:
- 4 in "Quote Ready" lane
- 6 in "Follow-Up" lane
- 3 in "Renewal" lane
- 2 with "Stale" badges
- 8 in "Complete" lane (or removed/archived)

### Overlay
Counter text: **"23 emails. 3 minutes. 8 fully resolved. 15 drafts ready for review."**

### Output
- `inbox-act2-zoomout.mp4` (~15 seconds, 16:9)

---

## Step 5: Build Act 3 — Stats Reveal

**Tool:** HTML/CSS
**Deliverable:** 15-second clip with clean stats view

### Design
Clean transition from the board to a stats summary:
- 23 emails processed in 3 minutes
- 8 fully resolved — data entered into AMS, replies sent, no human needed
- 15 drafts ready for review
- Zero submissions lost. Zero duplicates.
- AMS updated automatically — no API required

**Animation:** Stats appear one by one with subtle entrance animations (fade up, counter animation for numbers).

**Text overlay at end:** **"Your inbox used to be a bottleneck. Now it's a pipeline."**

### Output
- `inbox-act3-stats.mp4` (~15 seconds, 16:9)

---

## Step 6: Build Act 4 — CTA End Card

**Tool:** HTML/CSS (same as FNOL Act 4, different channel icons)
**Deliverable:** 5-second CTA card

### Design
Same template as FNOL CTA but with workflow-appropriate channel icons:
- Channel icons: email, web portal, API
- Text: **"One associate. Every channel."**
- CTA: **"indemn.ai"**

### Output
- `inbox-act4-cta.mp4` (5 seconds, 16:9)

---

## Step 7: Assemble in Descript

**Tool:** Descript (Business plan)
**Deliverable:** Final Smart Inbox demo video

### Import assets
1. `inbox-act1-counter.mp4` (5s)
2. `inbox-act2-triage.mp4` (~15s)
3. `inbox-act2-deepdive.mp4` (~40s)
4. `inbox-act2-zoomout.mp4` (~15s)
5. `inbox-act3-stats.mp4` (~15s)
6. `inbox-act4-cta.mp4` (5s)
7. Background music track

### Assembly steps

**1. Create new Descript project: "Smart Inbox Demo — InsurtechNY"**

**2. Build the timeline as Scenes:**
- Scene 1: Act 1 (inbox counter + text)
- Scene 2: Act 2 Phase 1 (triage — emails sorting)
- Scene 3: Act 2 Phase 2 (deep dive — one email processed)
- Scene 4: Act 2 Phase 3 (zoom out — everything processed)
- Scene 5: Act 3 (stats reveal)
- Scene 6: Act 4 (CTA)

**3. Transitions:**
- Act 1 → Phase 1: Cut or quick fade (inbox becomes the pipeline)
- Phase 1 → Phase 2: Smooth zoom (macro → micro, camera pushing into one card)
- Phase 2 → Phase 3: Reverse zoom (micro → macro, camera pulling back)
- Phase 3 → Act 3: Fade or dissolve to stats view
- Act 3 → Act 4: Fade to CTA

**4. Music:**
- This video has NO dialogue — music carries the energy
- Select something rhythmic, modern, building — should feel like progress/momentum
- Music should build slightly during the triage phase, settle during the deep dive, build again during zoom-out
- Louder than FNOL music since there's no voice to compete with
- Target -6 to -10 dB (prominent but not overwhelming)

**5. Captions/text:**
- No spoken captions needed (no dialogue)
- All text overlays should be baked into the source clips (built into HTML/CSS)
- Verify all text is readable in final export

**6. Review and polish:**
- Watch full video 3-5 times
- Check: can you understand the story with NO context? (no sound, no prior knowledge)
- Check: is the zoom-in/zoom-out transition smooth?
- Check: does the pacing feel right? (not rushed, not dragging)
- Check: is the "typing" animation on the draft reply readable at speed?

**7. Export:**
- Same specs as FNOL: MP4, H.264, 1080p/4K, 30fps, AAC 256kbps

### Output
- `smart-inbox-demo-final.mp4` — the finished video
- `smart-inbox-demo-final-720p.mp4` — tablet-friendly version (if needed)

---

# Execution Order

The two videos share some tools and patterns. Here's the optimal sequence to minimize context switching:

## Phase 1: Setup (~30 min)
1. Sign up for Kling Pro ($8/month)
2. Sign up for Descript Business ($33/month)
3. Verify LiveKit dev instance is accessible and recording works

## Phase 2: FNOL Video Production

### Parallel Track A: Kling generation
4. Generate Act 1 parking lot scene (3-5 iterations)

### Parallel Track B: LiveKit + Agent
5. Build LiveKit composite web template (phone UI + transcript)
6. Configure FNOL agent on dev (prompt, voice, hardcoded data)
7. Test call — 2-3 takes to verify agent behavior and recording quality

### Parallel Track C: UI screens
8. Build Act 3 dashboard reveal page (HTML/CSS with animations)
9. Build Act 4 CTA end card (HTML/CSS — reused for both videos)
10. Screen record both

### Sequential: Recording + Assembly
11. Record the final call — Craig as Mike, 3-5 takes, pick best
12. Import all assets into Descript
13. Assemble FNOL video — transitions, captions, music, ducking
14. Review, polish, export

## Phase 3: Smart Inbox Video Production

### Parallel Track A: Kling generation
15. Generate Act 1 inbox counter clip (or build in HTML/CSS)
16. Generate Act 2 Phase 1 triage animation (or build in HTML/CSS)
17. Generate Act 2 Phase 3 zoom-out clip (or build in HTML/CSS)

### Parallel Track B: UI build
18. Build Act 2 Phase 2 deep dive page (HTML/CSS — the big build)
19. Build Act 3 stats reveal page
20. Build Act 4 CTA (modify FNOL version — different channel icons)
21. Screen record all built pages

### Sequential: Assembly
22. Import all assets into Descript
23. Assemble Smart Inbox video — transitions, music
24. Review, polish, export

## Phase 4: Delivery
25. Review both videos side by side
26. Export final versions (1080p + 720p tablet versions)
27. Test playback on iPad, Galaxy Tab, and Windows PC
28. Share with Cam and Kyle for feedback
29. Iterate if needed

---

# Open Questions (To Resolve During Production)

1. **Carrier branding** — Use "Acme Insurance" for FNOL? Need a name for the Smart Inbox MGA/agency too.
2. **LiveKit composite template vs post-production sync** — Which approach for Act 2? Template is more authentic, post-production is faster. Decide after assessing LiveKit template complexity.
3. **Kling vs HTML/CSS for Smart Inbox macro views** — Try Kling first for the email flow triage (Phase 1). If it can't produce something that looks like a real pipeline, fall back to HTML/CSS animation.
4. **Music selection** — Two different tracks (one subtle for FNOL, one rhythmic for Smart Inbox) or one track adapted for both?
5. **Conference-specific URL** — Does Cam want a special landing page URL instead of just "indemn.ai" for booth traffic tracking?
6. **Video loop** — Should the videos loop at the booth? If so, consider making Act 4 transition smoothly back to Act 1 (or add a brief pause/black between loops).
7. **Tablet optimization** — What resolution and format works best for iPad/Galaxy Tab playback? Test before the conference.

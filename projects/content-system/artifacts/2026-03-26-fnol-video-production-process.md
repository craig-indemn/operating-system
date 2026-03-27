---
ask: "Document the complete production process for the FNOL conference demo video — tools, patterns, and how to replicate"
created: 2026-03-26
workstream: content-system
session: 2026-03-26-c
sources:
  - type: slack
    description: "Cam's messages about InsurtechNY Spring conference booth needs"
  - type: web
    description: "Research: AI video generation (Kling, Runway, HeyGen), video editing (Descript, CapCut, DaVinci Resolve), LiveKit egress templates"
  - type: github
    description: "LiveKit agents SDK, egress SDK, components-react, default egress template"
---

# FNOL Video Production Process — Complete Playbook

This documents the end-to-end process of producing the FNOL conference demo video for InsurtechNY Spring 2026. Written as a playbook so any future demo video can follow the same pattern.

## What We Built

A ~2-minute conference booth demo video showing a policyholder calling to report a car accident. An AI claims associate (Maya) handles the entire FNOL intake in real-time — a real conversation between a human and a voice AI agent, captured with a branded visual template showing phone UI, live transcript, and captions.

**Four acts:**
1. **The Moment** (5s) — Kling-generated parking lot scene with text overlay
2. **The Call** (~90s) — Real voice conversation recorded through branded LiveKit template
3. **The Reveal** (~13s) — Animated dashboard showing everything created automatically
4. **CTA** (~6s) — "Making insurance a conversation" with channel icons

## The Process (How We Got Here)

### Phase 1: Strategy (Brainstorm Session)

**Input:** Cam's "Webmap - Four Outcomes Navigation" matrix (PDF from Slack) mapping all Indemn associates by customer type and outcome category.

**Process:**
1. Read all 8 existing product showcase pages on blog.indemn.ai
2. Mapped each showcase to Cam's matrix associates
3. Evaluated the full matrix for voice and web demo candidates
4. Selected two demos based on: audience fit (carrier/distributor/investor room), contrast (voice vs workflow), and credibility (Smart Inbox is being built for a customer)

**Output:** Two demos — FNOL (voice, Intake Associate for Claims) + Smart Inbox (web workflow, Inbox Associate). Full scripts and storyboards for both.

**Key decisions:**
- FNOL: Personal lines auto claim (everyone's been in a fender bender)
- The call shows the customer perspective, then reveals the back-office outcome
- Tone: conversational and natural — not robotic, not overly empathetic
- Must work WITHOUT sound (conference booth is noisy)
- Option 3 upgrade (AI avatar) held for later

### Phase 2: Tool Selection (Research)

**Researched:** Kling, Runway, Higgsfield, HeyGen, Synthesia, Pika, Veo, Creatify, Mootion, CapCut, Descript, DaVinci Resolve, Premiere Pro, Canva.

**Final stack:**
| Tool | Role | Why |
|---|---|---|
| **Kling 3.0** | Cinematic parking lot clip | Best value ($8/mo), strong physics sim, cinematic quality |
| **LiveKit** | Real voice call infrastructure | Already have it, agent SDK, real-time transcription, room recording |
| **React + Vite** | Recording template + dashboard + CTA | Pixel-perfect control, Indemn branded, auto-animated |
| **Playwright** | Record animated pages to video | Headless browser captures the React animations as .webm |
| **Descript** | Final assembly | Auto-ducking, transcript editing, scenes model, captions |

**Rejected:** Higgsfield (social content, not cinematic), Canva (unnecessary), Creatify (e-commerce ads), Pika (too stylized), local video pipeline skills (not maintained).

### Phase 3: Voice Agent (Build + Test)

**What we built:** Standalone Python voice agent using livekit-agents 1.3.10.

**Architecture decision:** Run as a standalone script connecting directly to LiveKit Cloud — NOT through the Indemn platform's bot config system. No MongoDB routing, no SIP trunk, no phone number mapping. Just a direct LiveKit worker with a hardcoded FNOL prompt.

**Agent details:**
- File: `demos/fnol-voice-agent/fnol_agent.py`
- Agent name: `fnol-maya` (registered with LiveKit Cloud)
- LLM: OpenAI GPT-4.1, temperature 0.4
- TTS: Cartesia (default voice)
- STT: Deepgram Nova-3
- VAD: Silero
- System prompt: Full FNOL intake flow with hardcoded policyholder data (Mike Reynolds, 2023 Honda Accord, policy ACM-2023-7841)

**Critical pattern — Room-level agent filtering:**
The EC2 `voice-livekit-dev` container connects to the same LiveKit Cloud instance and accepts all jobs. Without filtering, both agents join every room. Solution:

```bash
# Create agents config file
cat > /tmp/fnol-agents.json << 'EOF'
{"dispatches": [{"agent_name": "fnol-maya"}]}
EOF

# Create room restricted to only our agent
lk room create --agents-file /tmp/fnol-agents.json "room-name"
```

This uses LiveKit's `RoomAgent.dispatches` proto field to restrict which agents can join the room. The EC2 agent (unnamed) is locked out.

**Setup commands:**
```bash
cd demos/fnol-voice-agent

# Create venv and install
uv venv --python 3.12 .venv
VIRTUAL_ENV=.venv uv pip install -r requirements.txt

# Start agent
.venv/bin/python fnol_agent.py dev

# Create filtered room
lk room create --agents-file /tmp/fnol-agents.json "fnol-take-$(date +%s)"

# Generate token
lk token create --join --room "ROOM_NAME" --identity mike-reynolds --valid-for 1h
```

**Testing:** Craig called in as Mike, ran through the FNOL script. Agent conversation was natural — Maya adapted to multi-detail responses, delivered the claim number correctly, closed with "Drive safe."

### Phase 4: Recording Template (Build + Brand)

**What we built:** React + Vite web app that connects to a LiveKit room and displays a branded visual overlay — phone call UI, live transcript, and CC captions.

**Layout:**
- Left (36%): Phone card (iris→eggplant gradient) with Maya's avatar, call timer, audio waveform
- Right (64%): White transcript panel with speaker-labeled entries (iris for Maya, lilac for Mike)
- Bottom: Dark eggplant caption bar with CC badge, always visible

**Key technical details:**
- Connects to LiveKit room via `@livekit/components-react` `<LiveKitRoom>` component
- Receives transcription via `RoomEvent.TranscriptionReceived` — the agent publishes transcription data through `TranscriptSynchronizer -> RoomIO`
- Enables mic input (`audio={true}`) and audio output (`<RoomAudioRenderer />`) so it doubles as a live preview AND recording source
- Has a "Start Call" button — page loads idle, you start screen recording, then click to connect
- Registers with `@livekit/egress-sdk` for potential composite egress recording

**Branding iterations:**
1. First attempt: dark purple theme with Inter font — looked nothing like Indemn
2. User feedback: "doesn't look like the brand, hard to see at a conference"
3. Fixed: Light theme (Barlow font, #f4f3f8 background, white surface cards) matching the showcase pages. Phone card is the only dark element. Iris logo on light background.
4. User feedback: "emojis don't work, Maya should be on the phone card not Mike, use the real slogan"
5. Fixed: Maya's AI-generated avatar on phone card, SVG icons instead of emojis, "Making insurance a conversation" tagline

**Maya's avatar:** Generated via Gemini image-gen (gemini-2.5-flash-image). Prompt: professional headshot, mid-30s woman, warm and competent, dark blazer, studio lighting. Stored at `template/public/maya-avatar.png`.

### Phase 5: Recording

**Approach:** Screen record the template (visuals) + LiveKit audio egress (server-side audio). Sync in Descript.

**Why not a single recording:** macOS QuickTime can't capture system audio without BlackHole (virtual audio driver), which requires a reboot to install. Splitting video and audio was faster.

**Audio recording setup:**
```bash
# Write egress config with S3 output
cat > /tmp/fnol-egress.json << 'EOF'
{
  "room_name": "ROOM_NAME",
  "audio_only": true,
  "file_outputs": [{
    "file_type": "OGG",
    "filepath": "recordings/demo/fnol-final.ogg",
    "s3": {
      "bucket": "indemn-call-transcripts",
      "region": "us-east-1",
      "access_key": "...",
      "secret": "..."
    }
  }]
}
EOF

# Start egress BEFORE the call
lk egress start --type room-composite /tmp/fnol-egress.json

# After the call
lk egress stop --id EG_xxxxx

# Download from S3
aws s3 cp s3://indemn-call-transcripts/recordings/demo/fnol-final.ogg ./fnol-final-audio.ogg
```

**Video recording:** macOS Cmd+Shift+5 screen recording of the template browser tab. Template has "Start Call" button so Craig could set up recording first, then click to begin.

**Recording flow:**
1. Start agent: `.venv/bin/python fnol_agent.py dev`
2. Start template: `cd template && npm run dev -- --port 5555`
3. Create filtered room: `lk room create --agents-file /tmp/fnol-agents.json "room-name"`
4. Start audio egress: `lk egress start --type room-composite /tmp/fnol-egress.json`
5. Open template URL with token in browser
6. Start screen recording (Cmd+Shift+5)
7. Click "Start Call" — Maya greets, Craig responds as Mike
8. Run through FNOL script (~90s conversation)
9. Stop screen recording
10. Stop audio egress: `lk egress stop --id EG_xxxxx`
11. Download audio from S3

### Phase 6: Dashboard + CTA (Build + Record)

**Dashboard (Act 3):** React component with CSS-animated sequential reveal. Claim card (with Maya avatar), adjuster card, activity timeline (8 items with SVG checkmark dots), stats bar. Each element animates in on a timer — ~13s total animation.

**CTA (Act 4):** React component with iris→eggplant gradient background. Indemn white logo, 5 channel SVG icons (phone, mic, chat, email, SMS) appearing sequentially, "Making insurance a conversation." tagline, indemn.ai URL.

**Recording:** Playwright headless browser captures both pages as .webm video:
```bash
NODE_PATH=/opt/homebrew/lib/node_modules node -e "
const { chromium } = require('playwright');
// ... records page at 1920x1080 for specified duration
"
```

### Phase 7: Assembly (Next Step)

**Tool:** Descript
**Import:** All 5 assets (Kling clip, screen recording, audio, dashboard .webm, CTA .webm)
**Process:** Stitch acts, sync audio to video for Act 2, add transitions, add background music with auto-ducking, export MP4

## Asset Inventory

| Asset | File | Source | Duration |
|---|---|---|---|
| Act 1 — Parking lot | `~/Downloads/kling_clip.mp4` | Kling 3.0 | ~5s (clip last 2s) |
| Act 2 — Call (video) | `~/Desktop/screen-recording-fnol-final-video.mov` | macOS screen recording | ~3:27 |
| Act 2 — Call (audio) | `fnol-final-audio.ogg` | LiveKit audio egress → S3 | 3:27 |
| Act 3 — Dashboard | `act3-dashboard.webm` | Playwright recording | ~13s |
| Act 4 — CTA | `act4-cta.webm` | Playwright recording | ~6s |
| Maya avatar | `template/public/maya-avatar.png` | Gemini image-gen | N/A |

## Replicable Patterns

### Pattern: Standalone demo voice agent
Write a minimal Python script with livekit-agents SDK. Hardcode the demo data (names, policy numbers, claim numbers) in the system prompt. Register with a unique agent name. Use room-level dispatch filtering to prevent production agents from competing.

### Pattern: Branded recording template
Build a React + Vite app that connects to a LiveKit room. Use `@livekit/components-react` for room connection, `RoomEvent.TranscriptionReceived` for live transcript, `<RoomAudioRenderer />` for audio playback. Add a "Start Call" button so the user can set up screen recording before connecting. Brand with the product's visual identity.

### Pattern: Animated reveal pages
Build React components with `useState` step counter and `setTimeout` chains for sequential animation. CSS transitions handle the visual (opacity, transform). Record with Playwright headless browser at 1920x1080.

### Pattern: Split audio/video recording
When system audio capture isn't available, record video via screen recording and audio via LiveKit audio egress to S3. Sync in post-production (Descript auto-syncs by matching waveforms).

## Tools Installed This Session

| Tool | Install | Purpose |
|---|---|---|
| LiveKit CLI (`lk`) | `brew install livekit-cli` | Room management, token generation, egress control |
| BlackHole 2ch | `brew install blackhole-2ch` (installed, needs reboot) | Virtual audio for future screen recordings with system audio |
| Descript | descript.com account | Video assembly (next step) |
| Kling 3.0 | klingai.com account | Cinematic video generation |

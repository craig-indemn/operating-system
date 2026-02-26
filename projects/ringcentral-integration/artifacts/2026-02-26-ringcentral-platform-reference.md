---
ask: "Comprehensive understanding of RingCentral — business features, admin settings, APIs, integration patterns, transcription, pricing — as source of truth for implementation"
created: 2026-02-26
workstream: ringcentral-integration
session: 2026-02-26-a
sources:
  - type: web
    description: "Deep research across RingCentral docs, developer portal, support articles, pricing pages, community forums, and third-party reviews"
---

# RingCentral Platform Reference

Source of truth for Indemn's RingCentral integration work. Covers business features, admin configuration, APIs, integration patterns, transcription/AI capabilities, and pricing.

---

## 1. Product Lines & Pricing

### RingEX (the phone system)

The core UCaaS product. Business phone + video + messaging + SMS.

| | Core | Advanced | Ultra |
|---|---|---|---|
| **Annual (per user/mo)** | $20 | $25 | $35 |
| **Monthly (per user/mo)** | $30 | $35 | $45 |
| **Calling** | Unlimited US/CA | Unlimited US/CA | Unlimited US/CA |
| **SMS** | 25/user/mo | 100/user/mo | 200/user/mo |
| **Toll-free minutes** | 100/mo | 1,000/mo | 10,000/mo |
| **Recording** | On-demand only | **Automatic + on-demand** | Automatic + on-demand |
| **Call monitoring** | No | **Whisper, barge, listen** | Whisper, barge, listen |
| **IVR** | Single-level | **Multi-level** | Multi-level |
| **Call queues** | Basic | **Advanced routing** | Advanced routing |
| **CRM integrations** | Basic | Salesforce, HubSpot, Zendesk | Salesforce, HubSpot, Zendesk |
| **Analytics** | Basic call logs | Business Analytics | Business Analytics Pro |
| **Storage** | Limited | Limited | Unlimited |
| **Hot desking** | No | Yes | Yes |

**Critical for our integration:** Core plan has NO automatic recording and only single-level IVR. Advanced is the minimum for automatic recording per-queue.

### RingSense / AI Conversation Expert (ACE)

AI analytics add-on. **$60/user/month** on top of RingEX plan.

Provides: automatic transcription, sentiment analysis, call summaries, highlights, action items, keyword extraction, call scoring, talk-to-listen ratios.

API access: Yes — `GET /ai/ringsense/v1/public/accounts/~/domains/pbx/records/{call_id}/insights`

**Not recommended for Phase 1** — expensive and Indemn can handle transcription via the free Speech-to-Text API.

### RingCX (contact center)

Separate product. $65/agent/month. Full omnichannel contact center with IVR, skills-based routing, real-time audio streaming, 200+ reports. **Not relevant unless customer upgrades to contact center.**

### AI Receptionist (AIR)

RingCentral's own AI phone agent. $59/month for 100 minutes (+$0.50/min overage). Basic FAQ, appointment scheduling, call routing. Limited customization — not a competitor to what Indemn builds, but worth knowing it exists.

---

## 2. Admin Portal Configuration

Admin portal: `service.ringcentral.com`

### Admin Roles
- **Super Admin** — full access (billing, users, phone system)
- **Phone System Admin** — phone settings only (no billing/users)
- **User Admin** — user management only
- **Custom roles** — configurable RBAC

### What Admins Can Configure

**Company-level:**
- Business hours / after-hours schedules (per day of week)
- Holiday schedules with custom routing
- Company greeting / auto-receptionist
- Default caller ID settings
- Data export

**Phone system:**
- Auto-attendant / IVR menus
- Call queues and ring groups
- Call recording settings (per-user, per-queue, per-direction)
- Recording announcements
- Call forwarding rules
- Music-on-hold
- Dial-by-name directory
- Emergency 911 settings

**User management:**
- Add/remove users and extensions
- Assign phone numbers
- Set per-user call handling rules
- Enable/disable features per user

### Call Recording Configuration (Advanced+ Only)

**Path:** Admin Portal → Phone System → Call Recording

**Granularity:**
- Per-user (enable for specific extensions)
- Per-call-queue (enable for specific queues)
- Per-direction (inbound only, outbound only, or both)

**Announcements:**
- Default announcement available
- Custom: record via phone, mic, or upload audio file
- Configurable per queue — different announcements for different teams
- Required for compliance (one-party and two-party consent states)

**Limits:**
- On-demand: 200 recordings/user
- Automatic: 100,000 recordings/account
- Retention: 90 days (then deleted unless archived via API)
- Recordings < 30 seconds are NOT retained

### Call Queue Configuration

**Routing methods:**
- Simultaneous — ring all members at once (up to 10)
- Sequential — ring one at a time in fixed order
- Rotating — distribute evenly
- Longest idle — ring whoever's been idle longest

**Queue settings:**
- Max wait time → overflow action
- Max callers in queue
- Custom hold music / periodic announcements
- Overflow routing (another queue, voicemail, external number, IVR)
- Wrap-up time between calls
- Separate business hours vs after-hours rules

### Call Forwarding Configuration

**Types:**
- **Unconditional** — all calls forward immediately (Phase 2 pattern)
- **Conditional** — forward on no-answer (X rings), busy, unreachable (Phase 1 pattern)
- **Per-queue overflow** — queue-level forwarding after max wait

**Destinations:** External numbers, other extensions, voicemail, another queue, IVR

**Admin path:** Per-extension or per-queue call handling rules → Forwarding settings

### IVR / Auto-Attendant

- **Core:** Single-level menu only
- **Advanced/Ultra:** Multi-level, up to 250 menus/submenus
- Visual drag-and-drop editor
- Per-number IVR (each DID can have its own menu)
- Options: route to extension, queue, ring group, submenu, voicemail, external number, dial-by-name
- Prompts: record via phone/mic, text-to-speech, or upload audio
- XML import/export for bulk config

---

## 3. API Reference

Base URL: `https://platform.ringcentral.com/restapi/v1.0/`

### Authentication

**OAuth 2.0** with two flows:

| Method | Use Case |
|---|---|
| **JWT (JSON Web Token)** | Server-to-server automation (what Indemn needs) |
| **Authorization Code** | User-facing apps with interactive login |

**JWT flow:** Create JWT credential in Developer Console → tied to a specific user → exchange for access token → use as `Authorization: Bearer <token>`.

**Developer app creation:**
1. Go to developers.ringcentral.com
2. Create app → "Server/No UI" type
3. Assign scopes (permissions)
4. Generate JWT credential
5. Share credential + account ID with integration partner

### Key Scopes

| Scope | What It Allows |
|---|---|
| `ReadCallLog` | View call history |
| `ReadCallRecording` | Download recordings |
| `CallControl` | Manipulate active calls (answer, transfer, hold, park) |
| `ReadAccounts` | View account/extension info |
| `EditExtensions` | Manage extension settings |
| `SubscriptionWebhook` | Create event subscriptions |
| `AI` | Use Speech-to-Text and AI analytics APIs |
| `Analytics` | Access business analytics data |
| `ReadPresence` | View user availability status |

### Call Log API

**Endpoints:**
- `GET /account/{id}/call-log` — company-wide
- `GET /account/{id}/extension/{extId}/call-log` — per-extension
- `GET /account/{id}/extension/{extId}/active-calls` — currently active

**Views:** `?view=Simple` (default) or `?view=Detailed` (includes call legs)

**Call log record fields:**

| Field | Description |
|---|---|
| `id` | Unique record ID |
| `sessionId` | Session ID |
| `telephonySessionId` | Telephony session ID |
| `startTime` | ISO 8601 timestamp |
| `duration` | Seconds |
| `direction` | `Inbound` / `Outbound` |
| `action` | `Phone Call`, `VoIP Call`, etc. |
| `result` | `Accepted`, `Missed`, `Voicemail`, `Rejected`, `No Answer` |
| `from` | Object: `phoneNumber`, `name`, `location` |
| `to` | Object: `phoneNumber`, `name`, `location` |
| `recording` | Object: `uri`, `id`, `type`, `contentUri` (if recorded) |
| `legs` | Array of leg objects (detailed view — routing path) |

**Filters:** `dateFrom`, `dateTo`, `type`, `direction`, `phoneNumber`, `recordingType`, `perPage` (max 1000)

**Rate limit:** Heavy group — 10 requests/user/minute

**Retention:** 90 days. Must archive before expiry.

### Call Recording API

Recordings accessed through Call Log API:
1. Query call log with `?recordingType=All`
2. Each record has `recording.contentUri`
3. Download audio from `contentUri` with bearer token

**Dedicated endpoint:** `GET /account/{id}/recording/{recordingId}` — metadata + contentUri

**Programmatic recording control (on active calls):**
- Start/stop/resume recording via Call Control API

**Constraints:**
- Recordings < 30 seconds not retained
- Heavy rate limit group
- Required scope: `ReadCallRecording`

### Call Control API

**Base:** `/account/{id}/telephony/sessions/{sessionId}/parties/{partyId}`

| Action | Description |
|---|---|
| Answer | Accept incoming call |
| Hold / Unhold | Hold management |
| Transfer | Cold transfer to number/extension |
| Warm Transfer | Transfer with intro |
| Forward | Route to alternate destination |
| Flip | Move call to another device |
| Park | Place in park location |
| Record / Stop Recording | Control recording |
| Hangup | End call |

Required: `CallControl` scope + "Advanced User" permission on account.

### Speech-to-Text AI API (Free, Beta)

**Endpoint:** `POST /ai/audio/v1/async/speech-to-text`

**How it works:**
1. POST with audio URL (e.g., recording contentUri) + parameters
2. Returns `jobId` immediately (async)
3. Poll for result or provide webhook URL

**Parameters:**
- `contentUri` — URL of audio file
- `enableSpeakerDiarization` — identify speakers (true/false)
- `source` — `CallCenter` (2-3 speakers) or `Meeting` (4-6)
- `enablePunctuation` — add punctuation

**Response includes:**
- Full transcript text
- Speaker labels with timestamps
- Word-level timing
- Confidence scores

**Requirements:** `AI` scope. No additional license needed. Beta, English only.

**This is the recommended transcription path for Indemn** — free, API-accessible, produces structured transcripts with speaker diarization.

### Summarization API

**Endpoint:** `POST /ai/text/v1/async/summarize`

Takes transcript text, returns:
- Abstractive summary (AI-generated)
- Extractive summary (key excerpts)
- Can specify time ranges and speaker IDs

### Event Subscriptions

**Delivery mechanisms:** Webhooks (push to URL) or WebSockets (persistent connection)

**Key event filters:**

| Filter | Events |
|---|---|
| `/account/~/telephony/sessions` | All call events (ring, answer, hold, transfer, end) |
| `/account/~/extension/{id}/telephony/sessions` | Per-extension call events |
| `/account/~/extension/{id}/presence` | User availability changes |
| `/account/~/extension/{id}/message-store` | New messages (SMS, voicemail, fax) |
| `/account/~/extension/{id}/voicemail` | New voicemail |

**Webhook requirements:**
- Publicly accessible URL, TLS 1.2+
- Respond within 3000ms with HTTP 200
- Echo `Validation-Token` header on creation

### IVR & Routing API

- `/account/{id}/ivr-prompts` — manage IVR audio prompts
- `/account/{id}/ivr-menus` — manage menu trees
- `/account/{id}/extension/{id}/answering-rule` — manage forwarding/handling rules

### Business Analytics API

- Aggregate endpoint — total counts and time by period
- Timeline endpoint — breakdown by time frames (hourly, daily)
- Metrics: call counts, time in phases (Setup, Ringing, IVR, Live Talk, Hold)
- Filters: date range, extensions, call types, directions

### Rate Limits

| Group | Requests/User/Minute |
|---|---|
| Light | 50 |
| Medium | 40 |
| Heavy | 10 |
| Auth | 5 |

**Critical:** Each request during penalty window RESETS the timer. Must wait full penalty before retrying. HTTP 429 response with `Retry-After` header.

### Call Supervision API

Connect to active calls for monitoring:
- **Listen** — silent monitoring
- **Whisper** — speak to agent only
- **Barge** — join call, all parties hear

Requires pre-configured Call Monitoring Group (admin setup). Available on Advanced+ plans only.

---

## 4. Integration Patterns

### Pattern 1: Call Forwarding (Recommended)

Configure RingCentral to forward calls to external number (Twilio).

**Phase 1 — Conditional:** Forward on no-answer/after-hours. Admin configures per-queue.
**Phase 2 — Unconditional:** Forward all calls. AI handles everything.

**Pros:** Simplest, most reliable, full Indemn control over AI experience.
**Cons:** Requires forwarding configuration per queue/number.

**Admin setup:**
- Per-extension: Call Handling → Forwarding → Add external number
- Per-queue: Queue settings → Overflow → Forward to external number
- Conditional: Set rings/time before forward triggers
- After-hours: Separate after-hours forwarding rules

### Pattern 2: SIP Device Registration

Register AI as a SIP phone on a RingCentral extension.

**How:** Admin creates generic SIP device → gets credentials → AI registers at `sip.ringcentral.com:5060`

**Pros:** Tighter integration, AI appears as an extension.
**Cons:** Device registration only (not true SIP trunking), TLS issues reported, more complex.

### Pattern 3: BYOC (Bring Your Own Carrier)

Keep numbers on existing carrier, connect to RingCentral via SBC.

**Pros:** Maximum control, no number porting, can intercept at SBC layer.
**Cons:** High complexity, requires SBC hardware/software, enterprise-grade.

### Pattern 4: External Number (Twilio-primary)

Customer-facing number lives on Twilio. RingCentral is backend for human agents only.

**Pros:** Simplest AI path, no RC forwarding config needed.
**Cons:** Requires number porting away from RC or using new numbers.

---

## 5. Transcription & Analytics Options

### Without Any Upgrade (Core Plan)

| Data Available | How |
|---|---|
| Call metadata (who, when, duration, outcome) | Call Log API |
| Queue/agent routing data | Call Log API (detailed view) |
| Call volume analytics | Business Analytics API |
| Real-time call events | WebSocket subscriptions |
| Voicemail transcription (first 60 seconds) | Message API |

**Not available:** Transcripts, sentiment, summaries, intent detection.

### With Advanced Plan Upgrade (+$5/user/mo)

Everything above, plus:
| Data Available | How |
|---|---|
| Call recordings (automatic, per-queue) | Call Log API → contentUri |
| Transcription (DIY) | Download recording → RC Speech-to-Text API (free, beta) or Whisper/Deepgram |
| Call monitoring (live listen) | Call Supervision API |
| Multi-level IVR | IVR API |

**This is the recommended tier for Indemn integration.**

### With RingSense/ACE Add-on (+$60/user/mo)

Everything above, plus:
| Data Available | How |
|---|---|
| Automatic transcription | RingSense API |
| Sentiment analysis | RingSense API |
| Call summaries | RingSense API |
| Highlights & action items | RingSense API |
| Keyword extraction | RingSense API |
| Call scoring | RingSense API |

**Not recommended** — expensive, and Indemn can build equivalent analytics from transcripts.

### Indemn's Recommended Transcription Pipeline

```
RC enables automatic recording (Advanced plan)
         │
         ▼
Indemn subscribes to telephony session events (webhook)
         │
         ▼
On call-end event → query Call Log API for recording
         │
         ▼
Download recording audio via contentUri
         │
         ▼
Send to RC Speech-to-Text API (free, beta)
  OR Whisper/Deepgram (more control)
         │
         ▼
Store transcript + metadata in Indemn analytics pipeline
         │
         ▼
Run Indemn's own analytics (intent, sentiment, summaries)
```

Cost: $0 beyond the Advanced plan upgrade (if using RC's Speech-to-Text API).

---

## 6. Data Retention & Archival

| Data | Retention | Limit |
|---|---|---|
| Call logs | 90 days | — |
| Automatic recordings | 90 days | 100,000/account |
| On-demand recordings | 90 days | 200/user |
| Voicemail | 90 days | 200 unread/user |
| SMS/MMS | 90 days | 10,000 messages |

**Indemn must pull and archive data before the 90-day window.** RingCentral provides an archival guide for building automated pipelines.

---

## 7. Compliance & Security

- SOC 2 Type II, ISO 27001, HIPAA (with BAA), PCI DSS, GDPR
- TLS in transit, SRTP for voice, encryption at rest
- Recording announcements configurable per-queue (consent compliance)
- Pause/resume recording for sensitive info (credit cards, SSNs)
- Role-based access to recordings
- Audit logging of admin actions
- MFA enforcement available

---

## 8. Number Porting

**Into RingCentral:** Automated for US/CA numbers. 2-4 business days. Upload number list, auto-processes by rate center/carrier.

**Out of RingCentral:** Legally required to comply. No charge. Don't disconnect service until port completes.

**BYOC alternative:** Keep numbers with existing carrier, connect via SBC. Avoids porting entirely.

---

## 9. Quick Reference for Admin Setup

### Enable Automatic Recording on Specific Queues

**Prerequisite:** Advanced plan or higher.

1. Admin Portal → Phone System → Call Recording
2. Select specific call queues to record
3. Choose: Inbound, Outbound, or Both
4. Configure recording announcement (required for compliance)
5. Test: make a test call to the queue, verify recording appears in call log

### Set Up Conditional Call Forwarding (Phase 1)

1. Admin Portal → Phone System → Call Queues → [Select Queue]
2. Call Handling → After Hours / Overflow settings
3. Forward to: [Indemn's Twilio number]
4. Set condition: "After X rings" or "After hours" or "When all agents unavailable"
5. Test: call the queue when no one is available, verify call forwards

### Set Up Unconditional Call Forwarding (Phase 2)

1. Admin Portal → Phone System → [Select Number/Extension]
2. Call Handling → Forward all calls
3. Destination: [Indemn's Twilio number]
4. Test: call the number, verify call goes directly to Indemn

### Create API Credentials for Indemn

1. Go to developers.ringcentral.com
2. Sign in with admin account
3. Create Application → "Server/No UI" → name it "Indemn Integration"
4. Assign scopes: `ReadCallLog`, `ReadCallRecording`, `CallControl`, `AI`, `Analytics`, `SubscriptionWebhook`, `ReadAccounts`
5. Go to Credentials → Create JWT Credential
6. Copy: Client ID, Client Secret, JWT token, Account ID
7. Share securely with Indemn engineering team

---

## 10. RingCentral AI Receptionist (AIR) — For Reference

RingCentral's own AI agent product. $59/month for 100 minutes.

**Capabilities:** Natural language conversations, FAQ handling, appointment scheduling (Google/Outlook), SMS follow-up, call routing with context, spam blocking, multi-language.

**Limitations:** Basic FAQ only, limited customization, no sophisticated routing logic, no custom integrations.

**AIR Everywhere:** Standalone version that works with any phone system (not just RingCentral). Same $59/month.

**Relevance to Indemn:** Not a competitor for sophisticated use cases, but the customer may ask about it. Indemn's agents are significantly more capable.

---

## Sources

### Official Documentation
- [RingCentral Developer Portal](https://developers.ringcentral.com)
- [API Reference](https://developers.ringcentral.com/api-reference)
- [Voice API Guide](https://developers.ringcentral.com/guide/voice)
- [Call Log Guide](https://developers.ringcentral.com/guide/voice/call-log)
- [Call Recordings Guide](https://developers.ringcentral.com/guide/voice/call-log/recordings)
- [Call Control Guide](https://developers.ringcentral.com/guide/voice/call-control)
- [Call Routing Guide](https://developers.ringcentral.com/guide/voice/call-routing)
- [Call Supervision Guide](https://developers.ringcentral.com/guide/voice/supervision)
- [AI API Guide](https://developers.ringcentral.com/guide/ai)
- [Speech-to-Text Guide](https://developers.ringcentral.com/guide/ai/speech-to-text)
- [RingSense API](https://developers.ringcentral.com/ringsense-api)
- [Event Notifications Guide](https://developers.ringcentral.com/guide/notifications)
- [Authentication Guide](https://developers.ringcentral.com/guide/authentication)
- [Rate Limits Guide](https://developers.ringcentral.com/guide/basics/rate-limits)
- [Data Archival Guide](https://developers.ringcentral.com/guide/voice/call-log/archival)
- [Business Analytics API](https://developers.ringcentral.com/analytics-api)

### Admin & Product
- [RingCentral Admin Portal](https://service.ringcentral.com)
- [Call Recording Features](https://www.ringcentral.com/office/features/call-recording/overview.html)
- [Call Monitoring Features](https://www.ringcentral.com/office/features/call-monitoring/overview.html)
- [Multi-Level Auto-Attendant](https://www.ringcentral.com/office/features/multi-level-auto-attendant/overview.html)
- [AI Receptionist](https://www.ringcentral.com/ai-receptionist.html)
- [AI Conversation Expert (ACE)](https://www.ringcentral.com/products/ai-conversation-expert.html)
- [BYOC](https://www.ringcentral.com/solutions/BYOC.html)
- [Trust Center](https://www.ringcentral.com/trust-center.html)
- [Data Retention Policies](https://support.ringcentral.com/article-v2/RingCentral-data-retention-policies.html)

### Third-Party Integration References
- [Synthflow SIP Integration](https://docs.synthflow.ai/sip-with-ringcentral)
- [Retell AI RingCentral Integration](https://www.retellai.com/integrations/ring-central)
- [RingCentral + Twilio + ElevenLabs Pattern](https://dev.to/colbygarland/using-ringcentral-twilio-and-elevenlabs-in-canada-to-get-caller-id-d89)

### Pricing References
- [Nextiva: RingCentral Pricing 2026](https://www.nextiva.com/blog/ringcentral-pricing.html)
- [KrispCall: RingCentral Pricing 2026](https://krispcall.com/general/ringcentral-pricing/)
- [GetVoIP: RingCentral Pricing](https://getvoip.com/blog/ringcentral-pricing/)

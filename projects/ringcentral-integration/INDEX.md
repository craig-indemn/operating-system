# RingCentral Integration

Customer integration project — connecting Indemn's AI voice agents with a customer's RingCentral phone system. Phase 1: AI handles unanswered/after-hours calls. Phase 2: AI sits in front of all inbound calls as an intelligent triage layer. Customer is on basic RingEX (Core plan), US-based, a few hundred calls for architecture scope.

## Status
Session 2026-02-26-a closed. RingCentral research complete — comprehensive reference artifact saved covering business features, APIs, admin config, integration patterns, transcription, and pricing. Phased solution architecture defined (Phase 1: conditional forwarding for overflow/after-hours, Phase 2: unconditional forwarding as front door). Customer believes they're on basic RingEX (likely Core). Email sent to customer asking what plan they're on and proposing a meeting to set up API access. **Blocked on:** customer response confirming plan tier and scheduling API credential setup meeting.

## External Resources
| Resource | Type | Link |
|----------|------|------|
| RingCentral Developer Portal | API Docs | https://developers.ringcentral.com |
| RingCentral Admin Portal | Admin UI | https://service.ringcentral.com |
| RingCentral API Explorer | Interactive API | https://developers.ringcentral.com/api-reference |

## Artifacts
| Date | Artifact | Ask |
|------|----------|-----|
| 2026-02-26 | [ringcentral-platform-reference](artifacts/2026-02-26-ringcentral-platform-reference.md) | Comprehensive RingCentral reference — business features, APIs, admin config, integration patterns, transcription, pricing |

## Decisions
- 2026-02-26: Integration pattern is call forwarding (Pattern 1) — conditional forwarding in Phase 1, unconditional in Phase 2
- 2026-02-26: Standard Indemn voice pipeline (Twilio → LiveKit) for AI agent handling
- 2026-02-26: Customer needs Advanced plan upgrade for automatic recording ($5/user/mo increase)
- 2026-02-26: Indemn will handle transcription via API (RC Speech-to-Text or Whisper) rather than paying for RingSense ($60/user/mo)

## Open Questions
- What RingEX plan tier is the customer actually on? (Core vs Advanced vs Ultra)
- Which specific queues/departments does the customer want recording enabled on vs. metadata-only?
- Which teams have recording hesitancy and what are their specific concerns?
- What is the customer's current IVR/auto-attendant configuration?
- How many phone numbers, queues, and extensions are in play?
- What CRM or systems does the customer use that need call data?

## Next Steps
1. Customer responds with their plan tier and availability for API setup meeting
2. Meet with customer admin — walk through enabling recording on specific queues + creating API credentials
3. Build out Phase 1 technical spec (conditional forwarding → Twilio → LiveKit → AI agent)
4. Build the RC data pipeline (webhook subscription → pull recordings → transcribe → analytics)

# Release - 03/11/26

---

### **1. `bot-service`**

- **PR Link**: Feature → main: [#247](https://github.com/indemn-ai/bot-service/pull/247) (SM migration), [#248](https://github.com/indemn-ai/bot-service/pull/248) (langgraph deps). Deploy → prod: [#249](https://github.com/indemn-ai/bot-service/pull/249)
- **Major Features Released**: AWS Secrets Manager migration — env vars now loaded from SM/PS via `aws-env-loader.sh` instead of `.env`. Langgraph dependency security fixes.
- **Environment Variables**: All env vars migrated to AWS SM/PS. Loader script generates `.env.aws` from `indemn/prod/shared/*` and `indemn/prod/services/bot-service/*`. No manual env var changes needed — loader handles it.
- **Pre-Deployment Actions**: Merge feature PRs #247, #248 to main first. Verify prod SM secrets and PS parameters are populated (DONE).
- **Post-Deployment Actions**: Verify bot-service starts, `/chat/invoke` responds, LLM calls succeed.
- **Deployment Status**: NOT STARTED

> Deploy path: `/opt/bot-service/` on prod-services EC2 (98.88.11.14)

---

### **2. `CO-Pilot Dashboard UI`**

- **PR Link**: Feature → main: [#987](https://github.com/indemn-ai/copilot-dashboard/pull/987) (SM migration). Deploy → prod: [#989](https://github.com/indemn-ai/copilot-dashboard/pull/989)
- **Major Features Released**: AWS Secrets Manager migration. Evaluations Angular integration + React federation. Agent lifecycle badge + ownership transfer. CI docker/build-push-action v1 → v6.
- **Environment Variables**: Migrated to AWS SM/PS via `aws-env-loader.sh`. Shares env with copilot-server (same docker-compose in `/opt/tiledesk/`).
- **Pre-Deployment Actions**: Merge feature PR #987 to main first. **Must deploy together with copilot-server** (coupled — shared docker-compose). Deploy PR #989 has a merge conflict (prod has `intake-manager-changes` hotfix) — resolve before merging.
- **Post-Deployment Actions**: Verify dashboard loads, evaluations tab renders, agent management works.
- **Deployment Status**: NOT STARTED

> Deploy path: `/opt/tiledesk/` on copilot-prod EC2 (54.226.32.134). Coupled with copilot-server.

---

### **3. `CO-Pilot Service`**

- **PR Link**: Feature → main: [#796](https://github.com/indemn-ai/copilot-server/pull/796) (SM migration). Deploy → prod: [#773](https://github.com/indemn-ai/copilot-server/pull/773)
- **Major Features Released**: AWS Secrets Manager migration. Agent lifecycle and ownership management.
- **Environment Variables**: Migrated to AWS SM/PS via `aws-env-loader.sh`. Uses shared secrets + service-specific: `copilot-server/admin-credentials`, `copilot-server/chat21-credentials`.
- **Pre-Deployment Actions**: Merge feature PR #796 to main first. **Must deploy together with copilot-dashboard** (coupled — shared docker-compose). Prod has `org-availability-endpoint` hotfix not on main.
- **Post-Deployment Actions**: Verify copilot-server starts, Firebase auth works, API endpoints respond.
- **Deployment Status**: NOT STARTED

> Deploy path: `/opt/tiledesk/` on copilot-prod EC2 (54.226.32.134). Coupled with copilot-dashboard.

---

### **4. `point-of-sale (Chatbot-ui)`**

- **PR Link**: NO CHANGES
- **Major Features Released**: N/A
- **Environment Variables**: N/A
- **Pre-Deployment Actions**: N/A
- **Post-Deployment Actions**: N/A
- **Deployment Status**: N/A

>

---

### **5. `middleware-socket-service`**

- **PR Link**: Feature → main: [#338](https://github.com/indemn-ai/middleware-socket-service/pull/338) (SM migration). Deploy → prod: [#339](https://github.com/indemn-ai/middleware-socket-service/pull/339)
- **Major Features Released**: AWS Secrets Manager migration.
- **Environment Variables**: Migrated to AWS SM/PS via `aws-env-loader.sh`. Uses shared secrets + `services/middleware/aws-s3-credentials`.
- **Pre-Deployment Actions**: Merge feature PR #338 to main first. **Must deploy together with copilot-sync-service** (coupled — shared docker-compose in `/opt/middleware/`).
- **Post-Deployment Actions**: Verify middleware starts, WebSocket connections work, chat messages route correctly.
- **Deployment Status**: NOT STARTED

> Deploy path: `/opt/middleware/` on prod-services EC2 (98.88.11.14). Coupled with copilot-sync-service.

---

### **6. `copilot-sync-service`**

- **PR Link**: Feature → main: [#116](https://github.com/indemn-ai/copilot-sync-service/pull/116) (SM migration). Deploy → prod: [#117](https://github.com/indemn-ai/copilot-sync-service/pull/117)
- **Major Features Released**: AWS Secrets Manager migration.
- **Environment Variables**: Migrated to AWS SM/PS via `aws-env-loader.sh`. Same env as middleware (shared docker-compose).
- **Pre-Deployment Actions**: Merge feature PR #116 to main first. **Must deploy together with middleware-socket-service** (coupled — shared docker-compose).
- **Post-Deployment Actions**: Verify sync service starts, RabbitMQ connection works.
- **Deployment Status**: NOT STARTED

> Deploy path: `/opt/middleware/` on prod-services EC2 (98.88.11.14). Coupled with middleware-socket-service.

---

### **7. `payment-service`**

- **PR Link**: Feature → main: [#56](https://github.com/indemn-ai/payment-service/pull/56) (SM migration). Deploy → prod: [#57](https://github.com/indemn-ai/payment-service/pull/57)
- **Major Features Released**: AWS Secrets Manager migration.
- **Environment Variables**: Migrated to AWS SM/PS via `aws-env-loader.sh`. Uses shared secrets + `shared/stripe-keys` (4 keys incl. webhook secrets).
- **Pre-Deployment Actions**: Merge feature PR #56 to main first.
- **Post-Deployment Actions**: Verify payment service starts, Stripe webhook endpoint responds.
- **Deployment Status**: NOT STARTED

> Deploy path: `/opt/payment-service/` on prod-services EC2 (98.88.11.14)

---

### **8. `kb-service`**

- **PR Link**: Feature → main: [#138](https://github.com/indemn-ai/kb-service/pull/138) (SM migration). Deploy → prod: [#139](https://github.com/indemn-ai/kb-service/pull/139)
- **Major Features Released**: AWS Secrets Manager migration.
- **Environment Variables**: Migrated to AWS SM/PS via `aws-env-loader.sh`. Uses shared secrets + `copilot-api-credentials`.
- **Pre-Deployment Actions**: Merge feature PR #138 to main first.
- **Post-Deployment Actions**: Verify kb-service starts, knowledge base queries return results.
- **Deployment Status**: NOT STARTED

> Deploy path: `/opt/openai-fastapi/` on prod-services EC2 (98.88.11.14)

---

### **9. `conversation-service`**

- **PR Link**: Feature → main: [#131](https://github.com/indemn-ai/conversation-service/pull/131) (SM migration). Deploy → prod: [#132](https://github.com/indemn-ai/conversation-service/pull/132)
- **Major Features Released**: AWS Secrets Manager migration.
- **Environment Variables**: Migrated to AWS SM/PS via `aws-env-loader.sh`. Uses shared secrets + `airtable-api-key`, `service-tokens`.
- **Pre-Deployment Actions**: Merge feature PR #131 to main first.
- **Post-Deployment Actions**: Verify conversation-service starts, RabbitMQ connects, conversation routing works.
- **Deployment Status**: NOT STARTED

> Deploy path: `/opt/utility-service/` on prod-services EC2 (98.88.11.14)

---

### **10. `operations_api`**

- **PR Link**: Feature → main: [#92](https://github.com/indemn-ai/operations_api/pull/92) (SM migration). Deploy → prod: [#93](https://github.com/indemn-ai/operations_api/pull/93)
- **Major Features Released**: AWS Secrets Manager migration.
- **Environment Variables**: Migrated to AWS SM/PS via `aws-env-loader.sh`. Uses `services/operations-api/carrier-credentials` (13 carrier API keys) + `services/operations-api/mixpanel-token`.
- **Pre-Deployment Actions**: Merge feature PR #92 to main first.
- **Post-Deployment Actions**: Verify operations API starts, carrier endpoints respond.
- **Deployment Status**: NOT STARTED

> Deploy path: `/opt/operations_api/` on prod-services EC2 (98.88.11.14)

---

### **11. `indemn-website`**

- **PR Link**: NO CHANGES
- **Major Features Released**: N/A
- **Environment Variables**: N/A
- **Pre-Deployment Actions**: N/A
- **Post-Deployment Actions**: N/A
- **Deployment Status**: N/A

>

---

### **12. `www-eventsguard-mga`**

- **PR Link**: NO CHANGES
- **Major Features Released**: N/A
- **Environment Variables**: N/A
- **Pre-Deployment Actions**: N/A
- **Post-Deployment Actions**: N/A
- **Deployment Status**: N/A

>

---

### **13. `discovery-ui`**

- **PR Link**: NO CHANGES
- **Major Features Released**: N/A
- **Environment Variables**: N/A
- **Pre-Deployment Actions**: N/A
- **Post-Deployment Actions**: N/A
- **Deployment Status**: N/A

>

---

### **14. `voice-service`**

- **PR Link**: Feature → main: [#38](https://github.com/indemn-ai/voice-service/pull/38) (SM migration). Deploy → prod: [#30](https://github.com/indemn-ai/voice-service/pull/30)
- **Major Features Released**: AWS Secrets Manager migration.
- **Environment Variables**: Migrated to AWS SM/PS via `aws-env-loader.sh`. Uses shared secrets + `twilio-credentials`, `google-cloud-sa`.
- **Pre-Deployment Actions**: Merge feature PR #38 to main first.
- **Post-Deployment Actions**: Verify voice-service starts, Twilio connects.
- **Deployment Status**: NOT STARTED

> Deploy path: `/opt/voice-service/` on prod-services EC2 (98.88.11.14)

---

### **15. `voice-livekit`**

- **PR Link**: Feature → main: [#83](https://github.com/indemn-ai/voice-livekit/pull/83) (eval mode) — **MERGED**. Deploy → prod: [#84](https://github.com/indemn-ai/voice-livekit/pull/84)
- **Major Features Released**: Eval mode for voice simulation evaluation. Langfuse trace metadata (bot_id, CallSid, room_name added to OTLP spans).
- **Environment Variables**: N/A — voice-livekit uses its own `.env` files on the GPU cluster, NOT SM/PS.
- **Pre-Deployment Actions**: N/A (feature PR already merged to main).
- **Post-Deployment Actions**: Verify voice agent starts on GPU cluster, traces include new metadata fields.
- **Deployment Status**: NOT STARTED

> Deploy path: `/opt/voice-livekit/` on voice-livekit GPU EC2 (3.236.53.208). NOT part of SM migration.

---

### **16. `indemn-observatory`**

- **PR Link**: Feature → main: [#27](https://github.com/indemn-ai/Indemn-observatory/pull/27) (auth org scoping) — **MERGED**, [#29](https://github.com/indemn-ai/Indemn-observatory/pull/29) (bot_ids filter + reports) — awaiting review. Deploy → prod: [#28](https://github.com/indemn-ai/Indemn-observatory/pull/28)
- **Major Features Released**: **CRITICAL — observatory is DOWN in prod.** Auth fix: scope `/api/metadata` to user's organizations (security fix — previously leaked all org data). Voice evaluation: Langfuse sync, channel detection, evaluate UI. AWS Secrets Manager integration. CSR Time-of-Day activity page. Pie chart brand palette. `get_all_bot_ids` org filter. Voice/Distinguished report scripts.
- **Environment Variables**: Migrated to AWS SM/PS via `aws-env-loader.sh`. Uses `langfuse-keys`, `auth-secrets`, `mongodb-uri` + service-specific: `observability/internal-api-key`, `observability/demo-credentials`.
- **Pre-Deployment Actions**: Merge feature PR #29 to main first (awaiting review). Then update deploy PR #28 with latest main.
- **Post-Deployment Actions**: Verify observatory is back up, auth scoping works (only user's orgs visible), Langfuse sync runs.
- **Deployment Status**: NOT STARTED — **DEPLOY FIRST (service is down)**

> Deploy path: `/opt/Indemn-observatory/` on copilot-prod EC2 (54.226.32.134)

---

### **17. `email-channel-service`**

- **PR Link**: Feature → main: [#35](https://github.com/indemn-ai/email-channel-service/pull/35) (SM migration). Deploy → prod: [#36](https://github.com/indemn-ai/email-channel-service/pull/36)
- **Major Features Released**: AWS Secrets Manager migration.
- **Environment Variables**: Migrated to AWS SM/PS via `aws-env-loader.sh`. Uses `services/email-channel/google-auth-credentials` (note: env var name has typo `GOOGLE_AUTH_CREDEINTIALS` — matches application code).
- **Pre-Deployment Actions**: Merge feature PR #35 to main first.
- **Post-Deployment Actions**: Verify email channel service starts, email scheduling works.
- **Deployment Status**: NOT STARTED

> Deploy path: `/opt/email-channel-service/` on prod-services EC2 (98.88.11.14)

---

### **18. `evaluations`**

- **PR Link**: Feature → main: [#7](https://github.com/indemn-ai/evaluations/pull/7) (voice transcript eval), [#8](https://github.com/indemn-ai/evaluations/pull/8) (SM migration), [#9](https://github.com/indemn-ai/evaluations/pull/9) (voice simulation engine), [#10](https://github.com/indemn-ai/evaluations/pull/10) (handoff detection + echo fix). Deploy → prod: **needs creation after feature PRs merge** (main = prod currently)
- **Major Features Released**: AWS Secrets Manager migration. Transcript-based voice evaluation. Voice simulation evaluation engine + voice metrics. Handoff detection in eval engine. Attribution indicators for rubric evaluators. Echo bug fix.
- **Environment Variables**: Migrated to AWS SM/PS via `aws-env-loader.sh`. Uses full shared secret block + `evaluations/langsmith-project`, `evaluations/mongodb-database`.
- **Pre-Deployment Actions**: Merge all 4 feature PRs to main first. Then create deploy PR (main → prod).
- **Post-Deployment Actions**: Verify eval service starts, voice evaluation endpoints respond.
- **Deployment Status**: NOT STARTED

> Deploy path: `/opt/evaluations/` on prod-services EC2 (98.88.11.14)

---

### **19. `copilot-dashboard-react` (indemn-platform-v2)**

- **PR Link**: Feature → main: [#2](https://github.com/indemn-ai/copilot-dashboard-react/pull/2) (transcript type UI), [#3](https://github.com/indemn-ai/copilot-dashboard-react/pull/3) (voice simulation type UI). Deploy → prod: **needs creation after feature PRs merge** (main = prod currently)
- **Major Features Released**: Transcript type badge + filter UI for evaluations. Voice simulation type in evaluation UI. TestSetsList breakdown + filter chips.
- **Environment Variables**: N/A — frontend app, env vars are build-time only.
- **Pre-Deployment Actions**: Merge feature PRs #2, #3 to main first. Then create deploy PR (main → prod).
- **Post-Deployment Actions**: Verify build succeeds, eval UI shows voice types.
- **Deployment Status**: NOT STARTED

> Deploy path: `/opt/copilot-dashboard-react/` on prod-services EC2 (98.88.11.14)

---

### **20. `percy-service`**

- **PR Link**: Deploy → prod: [#5](https://github.com/indemn-ai/percy-service/pull/5). No feature PRs needed (work already on main).
- **Major Features Released**: Jarvis skills architecture — replace subagents with modular SKILL.md files. Evaluation connector validation and template fixes.
- **Environment Variables**: N/A — percy manages its own env, not part of SM migration.
- **Pre-Deployment Actions**: N/A.
- **Post-Deployment Actions**: Verify percy-service starts, Jarvis skills load correctly.
- **Deployment Status**: NOT STARTED

> Deploy path: `/opt/percy-service/` on prod-services EC2 (98.88.11.14)

---

## AWS Infrastructure (Pre-Deployment) — DONE

All AWS infrastructure is in place. No action needed by the team.

- **IAM Role**: `indemn-prod-services` — read-only access to `indemn/prod/*` SM secrets and `/indemn/prod/*` PS parameters, explicit deny on dev resources
- **Instance Profiles**: Attached to prod-services EC2 (`i-00ef8e2bfa651aaa8`) and copilot-prod EC2 (`i-0df529ca541a38f3d`)
- **SM Secrets**: 34 secrets under `indemn/prod/` (24 shared + 8 service-specific + langfuse + livekit)
- **PS Parameters**: 114 parameters under `/indemn/prod/` (45 shared + 69 service-specific)
- **AWS CLI v2**: Installed on both prod EC2s
- **Service URLs**: Public domains for copilot (`copilot.indemn.ai`), middleware (`proxy.indemn.ai`), sync (`copilotsync.indemn.ai`), evaluations (`evaluations.indemn.ai`). Private IPs (`172.31.22.7`) for host-mapped services on prod-services (bot-service, conversation, kb, voice, payment, operations_api). Verified against actual prod `.env` files.

## Deployment Order

1. **indemn-observatory** — FIRST (service is DOWN in prod)
2. **copilot-server + copilot-dashboard** — coupled, deploy together
3. **bot-service**
4. **middleware-socket-service + copilot-sync-service** — coupled, deploy together
5. **conversation-service**
6. **kb-service**
7. **voice-service**
8. **payment-service**
9. **operations_api**
10. **email-channel-service**
11. **voice-livekit** — separate GPU cluster
12. **evaluations** — after feature PRs merge
13. **percy-service**
14. **copilot-dashboard-react** — after feature PRs merge

## Notes

- All SM migration PRs switch docker-compose from `env_file: .env` to `env_file: .env.aws`. The old `.env` files remain untouched (safe rollback).
- The `aws-env-loader.sh` script runs on the EC2 host. It **copies `.env` as a base** (preserving static config, feature flags, Docker container names, etc.), then appends SM/PS values which override duplicates (last-value-wins). This ensures no env vars are lost in the transition.
- Firebase env var names corrected in copilot-server + copilot-dashboard loaders (e.g., `FIREBASE_API_KEY` not `FIREBASE_APIKEY`).
- Google OAuth is NOT configured in prod — no GOOGLE_CLIENT_ID/SECRET in tiledesk `.env`. Skipped in SM.
- voice-livekit is NOT part of SM migration — uses its own `.env` files on the GPU cluster.

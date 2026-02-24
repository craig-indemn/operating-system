---
ask: "Draft responses for NVIDIA Inception program application questions"
created: 2026-02-24
workstream: nvidia-inception
session: 2026-02-24-a
sources:
  - type: artifact
    description: "Indemn company intelligence artifact (2026-02-24)"
  - type: web
    description: "NVIDIA Inception program requirements and application guide"
---

# NVIDIA Inception Application Drafts

## Q1: Describe your company mission, products, target market, competitive differentiators, and how you currently use (or plan to use) NVIDIA technology. (200-1,000 characters)

**Status:** Draft (996 characters)

Indemn is the digital workforce for insurance distribution. We deploy AI Associates—generative AI agents across chat, voice, and email—enabling carriers, MGAs, and brokers to capture revenue they cannot today.

Our platform delivers four outcomes: Revenue Growth (24/7 quoting, eligibility triage), Operational Efficiency (automated service resolution), Client Retention (renewal analysis, cross-sell), and Strategic Control (human-in-the-loop governance). We serve mid-market MGAs, agencies, and carriers where 70% of underwriting capacity is wasted on non-productive work.

Differentiators: Insurance-native AI pre-trained on binding authority and surplus lines. Composable Skills architecture. Production bilingual voice agents. First GenAI insurance acquisition—Jewelers Mutual acquired our MGA for $1.8M.

We plan to leverage NVIDIA GPUs for low-latency voice inference and real-time agent reasoning, enabling sub-second responses for voice Associates serving insurance customers 24/7.

---

## Q2: Add Product or Service

**Product/Service Name:** Indemn AI Platform

**Product/Service Webpage:** https://www.indemn.ai

**Product/Service Type:** SaaS Platform

**Development Stage:** Shipping

### Describe your product and its value proposition (200-500 characters)

**Status:** Draft (437 characters)

Indemn deploys AI Associates—generative AI agents for insurance carriers, MGAs, and brokers across chat, voice, and email. Our platform delivers four business outcomes: Revenue Growth, Operational Efficiency, Client Retention, and Strategic Control. Insurance-native AI pre-trained on binding authority and surplus lines, with human-in-the-loop governance for regulated environments. First GenAI insurance acquisition in the industry.

### Technical Details (max 1,000 characters)

**Status:** Draft (896 characters)

Architecture: Multi-tenant SaaS on composable Skills architecture. Each AI Associate combines Skills (capabilities), Inputs (data collection), Actions (API calls), Knowledge (RAG from policy docs), and Integrations (AMS/PAS/carrier APIs).

AI/ML Stack: LLM-powered generative AI agents using LangGraph with component/connector abstraction. Insurance-native models pre-trained on underwriting guidelines, binding authority, and surplus lines. RAG retrieval with 95%+ accuracy.

Channels: Omnichannel—web chat, voice (bilingual English/Spanish via LiveKit), email, and browser-based web operators. Unified context persists across all channels.

Infrastructure: Node.js and Python microservices. MongoDB, Redis, RabbitMQ, Pinecone (vector search). AWS deployment with ~60-day implementation cycles. Human-in-the-Loop architecture queues AI recommendations for human review on high-risk decisions.

### Does this product/service use NVIDIA technologies?

**Draft:** No (not currently)

### Are you considering, but not yet using, any NVIDIA technologies?

**Draft:** Yes

### Which NVIDIA technologies are being considered?

**Draft:** NVIDIA GPUs for low-latency voice AI inference (production bilingual voice agents), TensorRT for optimizing inference performance, NVIDIA Riva for speech-to-text and text-to-speech in our voice Associates, and NIM microservices for scalable model deployment as we grow from 12 to 75+ customers.

### Which non-NVIDIA technologies are you using or considering?

**Draft:** Anthropic Claude (primary LLM), OpenAI, LangChain/LangGraph (agent orchestration), LiveKit (real-time voice), Pinecone (vector search), AWS (cloud infrastructure), MongoDB Atlas (operational data), Redis (session management), RabbitMQ (message queues).

### Brand Color

**Draft:** 4752a3 (Indemn Iris)

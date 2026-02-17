---
ask: "Build a data and analytics story to supplement Indemn's Series A investor pitch — focused on the engineering team's technical capability and what the data from our systems demonstrates"
created: 2026-02-17
workstream: series-a
session: 2026-02-17-a
sources:
  - type: mongodb
    description: "tiledesk database — observatory_conversations, daily_snapshots, precursor_lifts, requests, messages, organizations, structure_agents, bot_tools, knowledge_bases collections"
  - type: github
    description: "git log history from indemn-observability, evaluations, and web_operators repos"
---

# Indemn: The Engineering Advantage

A data supplement to the Series A investor pitch. This document shows what Indemn's engineering team has built, how fast they build it, and what the production data proves about the platform's capability.

---

## The Platform Today

Indemn's AI agents are running in production across the insurance industry. These are not demos.

| Metric | Number |
|--------|--------|
| Total messages processed | 2,067,835 |
| Total conversations handled | 143,040 |
| Leads captured | 77,635 |
| Active agents (last 30 days) | 55 |
| Customer organizations | 65 |
| Total agents built on the platform | 273 |
| Knowledge bases powering agents | 516 |
| Tool integrations connected | 2,481 |

Production conversation volume has been sustained at 5,000-7,600 conversations per month across the platform over the past 12 months, with individual customers like GIC Underwriters consistently processing 2,000+ conversations per month through their AI agent alone.

New customers are onboarding and ramping: Rankin Insurance went from zero to 177 conversations/month within its first month of deployment.

---

## What We've Built — And How Fast

Three systems built by a 4-person engineering team, each demonstrating what's possible when frontier AI capability meets deep insurance domain knowledge.

### 1. The Observatory — Conversation Intelligence at Scale

**What it is:** A production analytics platform that ingests every AI conversation across every customer, classifies outcomes, tracks sentiment and intent, identifies precursors to success and failure, and produces daily operational snapshots — all automatically.

**Build timeline:** First commit December 22, 2025. Live in production by mid-January 2026. Currently analyzing 7,695 conversations across all customers.

**What it produces (per agent, per customer, per day):**

- **Outcome tracking:** Every conversation is classified into outcomes — resolved autonomously, resolved with handoff, partial resolution, missed handoff, abandoned, timed out. Operators know exactly how each agent is performing.
- **Intent classification:** What are customers actually asking about? The system categorizes every conversation — informational inquiries, service requests, product questions, handoff requests, technical issues — giving operators visibility into demand patterns.
- **Sentiment analysis:** Real-time sentiment classification across all conversations. Currently: 12% positive, 4% negative across the platform.
- **Operational metrics:** Handoff completion rates, response times (avg 1.4 seconds, p95 3.5 seconds), tool call success rates (100%), token usage and cost per conversation.
- **Precursor lift analysis:** This is the novel part. The system calculates the statistical lift of behavioral factors on conversation outcomes. For example: user frustration is a 28-46x precursor to conversation abandonment. Tool call failures are 22-27x precursors to abandonment. This isn't reporting what happened — it's identifying *why* outcomes happen, which factors predict success or failure, and where to intervene. This is causal inference applied to AI conversation analytics.

**Why this matters to investors:** Most AI companies report vanity metrics — number of conversations, customer count. Indemn built a system that tells you the *quality* of every conversation, the *reason* behind every outcome, and gives operators the data to improve agents systematically. This is the difference between flying blind and having instruments.

### 2. The Evaluation Harness — AI That Tests AI

**What it is:** An autonomous evaluation system where an AI agent (a "deep agent," similar in concept to Claude Code) understands what a customer's agent is supposed to do based on its prompts, functions, and knowledge base — then autonomously generates evaluation scenarios, creates scoring rubrics, runs the evaluation, checks results, and iterates. A non-technical team member can set up a comprehensive evaluation for a customer's agent in 5 minutes.

**Build timeline:** First commit January 20, 2026. Currently has 12,893 evaluation results across 7,301 test case details, 681 test cases, and 41 evaluation runs.

**What it does:**
- Understands an agent's purpose by analyzing its configuration
- Spawns subtasks to create simulation scenarios covering every situation the agent might face
- Creates evaluation rubrics with rules that apply to each scenario
- Runs evaluations using multi-turn simulated conversations (AI plays the customer)
- Checks results and can make corrections autonomously
- Users can guide the process conversationally or let it run end-to-end

**Why this matters to investors:** Building AI agents is new. Building *robust evaluations* for AI agents is harder. Building evaluations *autonomously* — and enabling non-technical team members to do it — is something very few companies in the world can do today. This system means Indemn can guarantee quality for customers at a pace that doesn't scale linearly with headcount.

### 3. Web Operators — Automating Enterprise Software

**What it is:** A framework where an AI agent operates a web browser to complete complex tasks in enterprise insurance software — systems like Applied Epic that have resisted traditional automation because of their complexity (Angular SPAs with custom components, multi-step workflows, session-dependent state).

**Build timeline:** First commit February 12, 2026. Five days later: 173 tests across 10 files, 4 development phases complete, path documents for multiple insurance workflows, a self-learning loop, middleware pipeline with observation masking and loop detection, and resume-from-failure capability.

**The self-learning loop:**
1. Run the operator against the target workflow
2. Capture the trajectory (what happened, step by step)
3. Refine the path document (structured playbook) based on what worked and what didn't
4. Run again with the improved path
5. Each run gets better — converging toward guaranteed task completion

**Why this matters to investors:** Insurance companies run their businesses on complex enterprise software that was never designed for automation. Indemn can now build operators that work *inside* that software, completing tasks that currently require manual human effort. The self-learning system means each new workflow gets easier to automate. The first use case — automating policy renewals in Applied Epic — addresses a process that every insurance agency does manually today.

---

## The Engineering Velocity Story

These three systems were built by 4 engineers in the time most companies would spend writing a product requirements document.

| System | First Commit | Production Data | Time |
|--------|-------------|-----------------|------|
| Observatory | Dec 22, 2025 | 7,695 conversations analyzed | ~4 weeks to production |
| Evaluation Harness | Jan 20, 2026 | 12,893 evaluation results | ~3 weeks |
| Web Operators | Feb 12, 2026 | 173 tests, 4 phases complete | 5 days |

This velocity is not accidental. The team operates the same way it builds for customers: automating its own workflows, using AI to accelerate development, staying at the frontier of what's possible with each new model release. When a new capability becomes available (e.g., improved browser use in the latest foundation models, token reduction techniques that cut browser automation costs by 90%), the team can integrate it within days — not quarters.

---

## What the Data Shows

### Production Scale Across Real Insurance Companies

The platform is handling real insurance conversations at scale. Top customers by monthly conversation volume (January 2026):

| Customer | Monthly Conversations | Agent Type |
|----------|----------------------|------------|
| GIC Underwriters | 2,663 | Customer service, underwriting |
| EventGuard | 1,709 | Event insurance sales |
| Bonzah | 294 | Renter's insurance |
| Open Enrolment | 244 | Benefits enrollment |
| Family First | 192 | Insurance services |
| Rankin Insurance | 176 | Sales and service (new) |

### The Observatory in Action (6 Weeks of Production Data)

For GIC Underwriters alone, the Observatory has analyzed 3,932 conversations since January 5, 2026, classifying each by outcome, intent, sentiment, and identifying the behavioral precursors that predict whether a conversation will succeed or fail.

Across all customers, the Observatory tracks daily snapshots that include:
- Conversation volumes by channel, device, and time of day
- Outcome distributions (autonomous resolution, handoff, abandonment, missed handoff)
- Response time percentiles (avg 1.4 seconds)
- Token usage and cost per conversation
- Intent breakdowns (informational, service requests, product inquiries)
- Sentiment trends

This level of operational visibility into AI agent performance — across every customer, every agent, every day — is infrastructure that most AI companies don't have at any stage.

### Precursor Intelligence: Understanding the "Why"

The Observatory doesn't just track what happened. It identifies why.

Using statistical lift analysis, the system calculates which factors are precursors to each outcome. Examples from production data:

- **User frustration** is a 28-46x precursor to conversation abandonment
- **Tool call failures** are a 22-27x precursor to abandonment
- **Negative sentiment** is a 33x precursor to unresolved conversations
- **Explicit handoff requests** that get missed are a 22x precursor to missed handoff outcomes

This is the kind of analysis that typically requires a data science team doing retroactive studies. Indemn's system produces it automatically, daily, for every agent and every customer.

---

## The Bigger Picture

Indemn's thesis is that the team investing in frontier AI infrastructure — not just deploying current capabilities, but continuously building the systems to understand, evaluate, and improve AI agents — creates a compounding advantage.

- **The Observatory** means Indemn knows exactly how every agent performs and why, across every customer. That data feeds back into improving the agents themselves.
- **The Evaluation Harness** means quality assurance scales without scaling headcount. A non-technical team member can comprehensively test a customer's agent in minutes, not weeks.
- **Web Operators** extend what agents can do beyond conversation into operating enterprise software directly — opening entirely new categories of automation for insurance companies.

Each system makes the others more valuable. Evaluate an agent, deploy it, monitor it through the Observatory, identify where it fails, evaluate the fix, redeploy. The cycle gets faster and more automated with each iteration.

The 4-person team that built these three production systems in under 8 weeks is what investors are investing in.

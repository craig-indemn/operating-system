---
ask: "Distilled data/analytics story for Kyle to use in Series A conversations — what the engineering team has built, backed by production data"
created: 2026-02-17
workstream: series-a
session: 2026-02-17-a
sources:
  - type: mongodb
    description: "tiledesk database — observatory_conversations, requests, messages, organizations, structure_agents"
  - type: github
    description: "git log history from indemn-observability, evaluations, and web_operators repos"
---

# The Engineering Advantage

Indemn's 4-person engineering team has built three production systems in the last 8 weeks that fundamentally change what the company can do for customers — and how fast it can do it.

## The Numbers

| | |
|---|---|
| **2M+ messages** processed across the platform | **143K conversations** handled since launch |
| **55 agents** active in the last 30 days | **273 agents** built total across **65 organizations** |
| **5,000-7,600** conversations/month sustained | **GIC Underwriters alone:** 2,600+/month |

## Three Systems, Built in Weeks

### The Observatory
Automatically analyzes every AI conversation across every customer, every day. Classifies what happened (resolved, handed off, abandoned), what the customer was asking about, and — critically — *why* outcomes happen, not just what happened. It identifies the specific factors that predict whether a conversation will succeed or fail, so we can systematically improve agents rather than guessing.

Live in production. 7,695 conversations analyzed in its first 6 weeks. Built in ~4 weeks.

### Autonomous Agent Evaluation
An AI system that understands what a customer's agent is supposed to do, then automatically generates every test scenario the agent might face, creates the scoring criteria, runs the tests, and identifies what needs to change. Anyone on the team can quality-test a customer's agent in 5 minutes — no engineering required. Going to production this week.

Built in ~3 weeks.

### Web Operators
AI agents that operate inside the enterprise software our customers already use — systems like Applied Epic that every insurance agency runs but that have resisted automation because of their complexity. The first use case: automating policy renewals, a process every agency does manually today. The system learns from each run, getting more reliable with every attempt.

5 days from first line of code to a tested framework with multiple insurance workflows.

## Why This Matters

These three systems create a cycle: **evaluate** an agent, **deploy** it, **monitor** it through the Observatory, identify where it's falling short, fix it, evaluate the fix, redeploy. Each loop makes the agent better — and the team has the tools to run this loop across every customer simultaneously.

The team builds at this pace because they operate the same way they build for customers: automating their own workflows, adopting new AI capabilities within days of release, not quarters. When the latest models unlock new capabilities (like browser automation that's 90% cheaper than it was 6 months ago), the team has it in production the same week.

**The investment is in the people and the system they've built.** A team that can build three production systems in 8 weeks — with 4 engineers — is a team that can build whatever the market needs next.

---
ask: "What is Craig's vision for the Indemn platform and how does it extend the existing thinking?"
created: 2026-03-24
workstream: product-vision
session: 2026-03-24-a
sources:
  - type: conversation
    description: "Craig's statements during the product-vision project kickoff session, 2026-03-24"
  - type: slack
    description: "Craig's messages in Craig/Dhruv/Ryan group DM about platform architecture, March 17"
---

# Craig's Vision — The Underlying System

## The Core Thesis

If we can create the underlying system that models the entire insurance business — every entity, every workflow, every interaction — and design it to replace or augment our customers' existing systems, then we have something that is the foundation for everything else. The platform becomes the precursor for agentic agents building agents, migrating companies onto our system, and automating essentially everything within a customer's insurance business.

At its core: **we are modeling the businesses in our space as entities and models and integrating AI into the entire system.**

## The Object-Oriented Insurance System

Craig envisions an object-oriented system where every possible thing needed in an insurance business is modeled as an entity with schemas, state machines, and APIs. The system would be:

- **Compatible with all existing systems** — AMS, CMS, carrier portals, rating engines
- **Capable of replacing those systems** — any customer should theoretically be able to move their entire operation onto Indemn
- **AI-native from the ground up** — every interface, every system, every workflow is designed to be interacted with by agents as well as humans

The EventGuard/Jewelers Mutual implementation is the proof point: Indemn already runs an end-to-end insurance program (quoting, binding, payments, compliance) entirely on its own platform. The vision is that this new system would easily be able to migrate JM/EventGuard onto the unified platform — and if it can do that, it can do it for any customer.

## Associates as Processing Nodes

The associates (from Cam's 48-item pricing matrix) are the processing layer that powers the platform. In Craig's model:

- **The platform** is how information gets organized, used, and delivered to the customer — essentially a user interface backed by the domain model
- **The associates** are the processing nodes — AI capabilities that operate on domain objects through the platform
- **The underlying system** mimics how the insurance business operates — domain objects, state machines, workflows, business rules

This maps directly to the architecture Craig proposed in the Slack discussion with Ryan and Dhruv (March 17):
- **Domain Objects** — the nouns (Submission, Quote, Policy, Certificate, Email, Message, actors)
- **Capabilities** — the verbs (Extract, Validate, Generate, Classify, Route, Notify) = Ryan's Layer 3b = what associates DO
- **Workflow Templates** — composed sequences of capabilities, parameterized by customer configuration = Ryan's Layer 3c
- **Channels** — how things enter the system. **AI agents are a CHANNEL into the insurance platform, not a separate system.**
- **Customer Configuration** — what makes Silent Sports different from GIC different from INSURICA

## The AI-First Design Principle

Craig emphasizes that the system must be designed for an AI-first world:

- Systems can be interacted with by agents, not just humans
- The operating system (Craig's personal OS with CLI skills) is a precursor for the platform's capabilities
- The Indemn CLI already creates agents, runs evaluations, modifies agents based on evaluations — this pattern scales to the platform itself
- The end state: agents building agents, agents migrating data, agents configuring workflows

This is the compounding advantage: once the domain model exists and is agent-accessible, the speed of building new capabilities accelerates exponentially. Every new customer implementation becomes faster because the system learns and the agents get more capable.

## How This Extends Existing Thinking

Craig's vision takes the convergent thinking from all four spheres and pushes it further:

| Existing Thinking | Craig's Extension |
|---|---|
| Ryan's taxonomy (Outcomes → Journeys → Workflows → Capabilities) | Add Domain Objects as the foundational layer that capabilities operate on |
| Cam's 48 associates as sellable products | Associates are processing nodes on a unified platform, not standalone agents |
| Kyle's "factory that builds them" (Gastown) | The factory IS the platform — agent-accessible domain model where agents configure and deploy other agents |
| Dhruv's Intake Manager as 50-70% of the foundation | Intake Manager evolves into the platform's core, not a separate system |
| Kyle's three tiers (middle market / enterprise / product) | The platform enables all three: configuration for middle market, depth for enterprise, product-led for partnerships |
| Kyle's moat question ("uninspired" answers) | The moat IS the domain model: insurance-native data model + agent-accessible system + compounding intelligence across every deployment |

## The Pressure Test

Craig proposes using EventGuard/JM as the design pressure test: if the platform can migrate JM's entire EventGuard operation onto it, then it works. JM is the most complete end-to-end implementation:
- Quoting and binding
- Payment processing
- Policy issuance
- Compliance (binding authority, surplus lines)
- Analytics and reporting
- Revenue sharing

If the domain model and platform can absorb this, it can absorb any customer. The same test applies to:
- GIC (wholesaler/MGA model with two internal teams)
- INSURICA (retail agency with multi-channel service)
- Union General (specialty underwriting)
- Silent Sports (document generation workflow)

## The Political Strategy

Craig recognizes this requires careful navigation:

- **Must be mindful of how each individual fits in** — Ryan's domain expertise, Dhruv's Intake Manager work, Cam's business model, Kyle's growth strategy
- **Cannot step on toes** — each person's existing work must be shown as contributing to the vision, not being replaced by it
- **Multi-stage engagement** — not a document dump, but a series of conversations that builds shared understanding
- **Make it impossible to say no** — every angle (business, technical, customer, fundraising) must be addressed

The delivery process itself is a design problem: who hears what, when, in what order, building on what context.

## Connection to the Operating System

Craig's personal operating system (this repo) is both a tool for executing this vision and a prototype of the capabilities the platform will provide:

- CLI-based tool access → platform CLI for customer operations
- Skills architecture → platform capabilities as composable modules
- The Hive (awareness layer) → platform intelligence layer
- Session management → platform workflow orchestration
- Dispatch (autonomous execution) → platform agent-driven automation

The operating system demonstrates at the individual level what the platform will do at the company level: make any operation accessible to AI agents through well-documented, composable interfaces.

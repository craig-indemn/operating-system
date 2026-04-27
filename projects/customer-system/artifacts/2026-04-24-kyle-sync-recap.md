---
ask: "Process and summarize the Apr 24 Kyle+Craig sync — what Kyle said about the email/diagram, what he wants next, how the broader conversation reshapes the customer system roadmap"
created: 2026-04-24
workstream: customer-system
session: 2026-04-24-roadmap
sources:
  - type: google-doc
    ref: "1mCdK2gCQEmSSWYp_ow-5C3NciI0eMRlWgr0WpXyXOMA"
    name: "Kyle - Craig - 2026/04/24 16:31 EDT - Notes by Gemini"
  - type: local
    ref: "projects/customer-system/artifacts/context/2026-04-24-kyle-craig-sync-transcript.txt"
    description: "Full transcript saved locally"
---

# Kyle Sync Recap — 2026-04-24

The sync that the entire day's work was building toward. Kyle reacted to the GR Little email + diagram, and the conversation shaped what comes next. Below: what Kyle said about the demo, what's now top-of-roadmap, and the broader strategic signals worth preserving.

---

## On the demo (email + diagram + entity trace)

Kyle's reaction was strongly positive. Direct quotes:

- *"This looks good. I'd say like right off the bat, maybe it's a little too long, but it's pretty close to what it should be."*
- *"I love this, by the way."*
- *"Look at this extra. This is awesome."* (reacting to the v2 diagram)
- *"This is super cool... worth, you know, trying to do on every call and getting in front of everybody."*
- *"I think this is um something we should be doing... almost automatically doing it but not trying to ship too much of it. Just trying to socialize it."*
- *"Everything's a v0... we could make it so that it's like somebody decides to press send, they send it, it's like, 'Oh, there's evidence that one works.'"*
- *"Awesome work, man... whole company's excited about the Indemn operating system."*

**Concrete feedback on the email:**
1. Slightly too long — trim.
2. Default-share the meeting recording with the customer in the email. Apollo (Granola/Apollo recording service) probably has an API for "anyone can view" links — Craig to investigate. Kyle: "I would check once in the CLI if Apollo's API enables you to have a anyone-can-view link to the recording." Note: Craig believes Google has the same thing for Drive-stored Meet recordings. Either path works.

**Decision:** the OS-generated meeting follow-up artifact gets shipped to the team as v0. Every customer interaction → generated artifact for review and one-click send. Surface area first, perfection later. Kyle: *"if we can get to V0 in a lot of places, we might just sunset some things and keep what we like."*

---

## What Kyle wants next (ranked by priority and his enthusiasm)

### 1. Dashboards — minimum-viable, hydrate with real pipeline data
Kyle's strongest asks. He has 200 prospects in his head; the sales team each has 20-30. Right now there's no shared view.

Minimum data per customer: **value · success path · days until next step · what is the next step · owner.**

Build: list/table view of all customers with these columns. Push-to-talk for sales reps to update next step / give thoughts. Should be automatic where possible, *"okay if it'll be wrong"* — iterate.

Hydrate from Kyle's data first, then ask the team for their spreadsheets. Kyle wants a static-vs-filterable, list-vs-card decision he can react to — not a scoping exercise.

### 2. Generated follow-up email per call, surfaced to the team
The thing we built today as a one-off — make it run for every call automatically. Kyle wants every meeting to produce an artifact (email, agenda, recap) that he or a sales rep reviews and presses send on. *"There's evidence that one works."*

This is the V0 of the Artifact Generator associate. We don't need to wire it as a fully autonomous associate yet — start with "post-meeting → draft generated → human reviews → human sends."

### 3. Stage refinement — 12+ stages, multi-select for sub-stages and archetypes
Kyle reacted to the 6-stage view in the diagram: *"I like that we've got only six there, but probably we'll want to have 12 that might be like multi-select in a way."*

Examples he gave:
- Between **discovery** and **demo**: "build prototype" → "share with customer" → "has customer responded?" → "second/third call?"
- **Qualification** is built into discovery + demo (early Q's vs late Q's). Different prospect archetypes need different sub-discoveries.

This may end up as: Stage entity gets sub-stages, OR a separate `qualification_state` column, OR Stage records gain a `parent_stage` field for hierarchy. **TBD — open design question.** Don't guess; iterate with Kyle on real data.

### 4. Customer origin tracking
Kyle's example: GR Little came via Pat Klene at 101 Western Labs. *"We got to track that because it increases the value and chance of closing a customer and you want to know where they're coming from so that you invest correctly."*

Add a step before the **contact** stage that captures introduction source. Could be: a field on Deal (`source_referrer: Contact_id`), or an Introduction entity, or extending Conference into "Introduction" more generally. **Open design — note for next session.**

### 5. Persistent AI workflow notification
Kyle's vision in his own words:
> *"Walker, that's where our professionally persistent AI can pick it up and say, 'Oh, we've got a request and a customer said yes.' Peter and maybe Ganesha have to be notified. Peter's got to go scrape the website and build the discovery and Ganesha has got to review it and say yes, it's ready to go to the customer and then it goes to me to share."*

The Commitment + Task entities we extracted today can drive this. Future associate: watches Commitment created (made_by_side: indemn), notifies the assignee, tracks it to completion. This is a real product capability — not just a sales tool.

### 6. Observatory daily/weekly reports
Kyle wants daily and weekly reports automatically delivered for customer activity (calls, web chats, etc.). He keeps asking — *"What happened yesterday? Last seven days? Trailing 30 days?"* — for pricing decisions and customer reviews.

There's a broken table in the observatory (Jonathan reported). Craig to fix + set up scheduled report. Already partially built (scheduled-reports infrastructure exists; usage report exists; not deployed).

---

## What we agreed not to do (or change)

- **Kyle stopped proactively sending Cloud-Code-generated AI data to Craig.** Craig: it's confusing because too technical and tries to "feed my AI." Going forward Craig asks when he needs something, Kyle responds. Daily talk-it-through continues — that's where the signal is. Kyle: *"I can stop trying to get my AI to get you data."*
- **Don't manage Kai (Craig's offer was declined).** Kyle's reasoning: Craig doesn't have management experience, Kai is a hard one to start with. Kyle keeps Kai going through him directly, projects only, with a strict framework (see below).
- **Don't let George make strategic product decisions.** *"He doesn't have enough insurance experience or immediate product technical intuition."* Strategic product decisions are Craig + Kyle.
- **Don't try to be Distinguished Programs' whole operating system.** Too much. Focus on the high-leverage APIs, broker communications, and integrations.

---

## Team / org direction (preserve for context)

Not customer-system-specific but load-bearing for what gets prioritized:

- **Ganesha leads implementation + customer playbook execution.** Critical for scaling. Needs structured guardrails and a clear product roadmap (which Craig + Kyle now have to define).
- **Peter and Kai (provisional)** develop AI associates using the testing + evaluation features on current customer associates. High-leverage. Finishes the platform.
- **Craig + Kyle** define the product roadmap, formalize roles, run cycle retrospectives. *"We're coming close to the everybody-that's-been-exploring-can't-explore-any-longer point."*
- **Cam** to be in team-building conversations going forward, especially the Kai decision.
- **Platform status:** testing + evaluation 60-75% complete. Observatory built but needs integration/usability work.

### Kyle's project proposal framework (for Kai, but generalizable)

Kyle pasted Craig the format he wants Kai to use for any project proposal:

> "On process going forward, we need to work along some structure. Here's a starting point as a minimum:
>
> - **Why?** What's the business pain or opportunity?
> - **Who's it for?** Team member or customer?
> - **What's the concrete scope and deliverables?**
> - **How long?** Is there a customer you can connect it to?
> - **Does this expand across customers? Does it expand with additional work? Is it a one-off?**
> - **What's the cadence in the check-in?**"

Use this for any new initiative under the customer-system roadmap, too.

---

## Next steps from the meeting (action items for Craig)

| # | Item | Source |
|---|---|---|
| 1 | Send Cloud Code plugin (token usage / context tracker) to Kyle | Opening |
| 2 | Send the GR Little email + traced journey artifacts to Kyle for written feedback | Demo |
| 3 | Check Apollo API for "anyone can view" link on meeting recording | Demo feedback |
| 4 | Build V0 sales pipeline dashboard / list view; hydrate with real data | Top priority |
| 5 | Fix the broken observatory reporting table (Jonathan's bug) | Observatory |
| 6 | Schedule daily/weekly observatory usage report to Kyle | Observatory |
| 7 | Tell Kai: all manager proposals go through Kyle; collaboration on project basis OK | Team |
| 8 | Document operational learnings as we iterate on the OS | Closing |

---

## What this means for the customer system

The Apr 24 work proved out the pattern. Kyle wants more of it — more surface area covered, more meetings producing artifacts, more visibility through dashboards. The roadmap shape now:

1. **Make today's GR Little flow run automatically per meeting** — wire the Touchpoint Synthesizer + Intelligence Extractor + Artifact Generator as real associates (with the Option B fix to Touchpoint source pointers, the eviction-bug workaround, the entity-identity work, and the Playbook-as-extraction-input refinement we agreed on earlier today). Surface artifacts for human review + one-click send.
2. **Build the V0 dashboard** — flat list/table of customers + minimum useful columns. Hydrate from Kyle's data + team spreadsheets. Add push-to-talk to update fields. Don't agonize over view choices — ship and iterate.
3. **Refine stages** (12 with sub-stages) — open design with Kyle. Will become clearer with real pipeline data.
4. **Add origin tracking** — referrer/source on Deal. Open design.
5. **Persistent-AI loop** — wire Commitment-driven notifications to internal team. This is the "Peter scrapes the site" / "Ganesha reviews" automation Kyle described.
6. **Observatory reporting** — fix + scheduled reports. Adjacent to but supports customer-system since both share the underlying entity model.

The customer-system project is now the primary vehicle for moving the OS roadmap forward. The artifacts produced today (Playbook entity vision, extractor-pipeline-gap, design-dialogue, info-flow diagram) all feed into points 1-3 above.

---

## What changes about the prior sessions' artifacts

- The **email-too-long feedback** — incorporate into the Playbook DISCOVERY `artifact_intent`. Add explicit guidance: "tighter than instinct; cut anything not load-bearing."
- The **stage-count refinement** — note in `2026-04-24-design-dialogue-playbook-artifact-proposal.md` open questions section. The 6 stages we use now will need to expand or gain sub-structure.
- The **origin/referrer tracking gap** — note as a new open question in the design-dialogue artifact.
- The **persistent-AI workflow** — already implicit in the Artifact Generator design. Kyle's specific framing (Commitment → notify assignee → completion tracking) is concrete enough to pursue once Option B is in.
- The **dashboard work** — adjacent to but not blocking the Artifact Generator. Can run in parallel.

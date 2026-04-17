---
ask: "Draft a #dev-squad Slack message to Rem (primary) and Rudra (cc) presenting findings on the three UG intake-manager bugs, with specific questions back to them so we can keep moving"
created: 2026-04-17
workstream: union-general-intake-manager
session: 2026-04-17-a
sources:
  - type: slack
    description: "Draft for posting in #dev-squad (C08AM1YQF9U)"
  - type: github
    description: "Links to PR #118 on indemn-ai/intake-manager for the Pattern C fix"
---

# Draft Slack message — #dev-squad

**Target channel:** #dev-squad (C08AM1YQF9U, 14 members, we're already in)
**Primary audience:** Rem (@U03DP1H58B1)
**CC / FYI:** Rudra (@U0881BF4EMN)
**From:** Craig

---

## Draft (v1)

> Hey <@U03DP1H58B1> — wanted to put findings on the three issues you surfaced yesterday in a shared place. <@U0881BF4EMN> cc'd so context stays with you.
>
> Used the Xol Lounge submission from Ben's screenshot as the anchor point and pulled logs + MongoDB data for each bug. Here's where we landed.
>
> **1) "Older submissions still fail after the Nationwide fix"**
> Four different failure patterns showing up in prod logs, only some of them are real bugs:
>   • *Invalid class code* — some submissions carry a bogus class code (e.g. `9711`) that all three carriers reject with different error messages. When you regenerate, same bad data → same failure. Likely upstream (extraction / class-code matcher) — need specific submission IDs to trace.
>   • *Carrier decline* — class is real but the carrier won't write it. Expected behavior, not a bug.
>   • *Python NoneType crash in the Nationwide CL agent* — real bug, found the exact line. PR up: https://github.com/indemn-ai/intake-manager/pull/118 (3-line fix, coerces `None` → `""` in `lookup_program_classcodes`). <@U0881BF4EMN> could you review when you get a chance?
>   • *Travelers territory-API returning wrong state for some zips* — warning only, already handled gracefully.
>
> **Ask for Ben:** could you share 2–3 specific `thread_id`s (or URLs) of the "older subs" that are still failing? Even one is enough to confirm which pattern applies. And when you retried, did you see the *same* error message as before or a different one?
>
> **2) "Odd validation violations on fields that have data"**
> This one's a black box right now — the code paths are in `validation_service` / `parameter_violation_mapper_service` but without a specific case to look at we can't tell which rule is mis-firing.
>
> **Ask for Ben:** next time this happens, could you grab a screenshot (or the thread_id) showing which form + which field + what the violation message says? Carrier and state too if possible.
>
> **3) "Taxes/fees only on ACIC, broker/inspection only on SIC"**
> Root-caused this one and it's structural, not a one-line bug. Each carrier provider owns its own tax/fee code path and they've drifted apart over time:
>   • ACIC returns state surplus-lines taxes (CA SL Tax, stamping fee) in its XML and we extract them — but the Broker/Inspection fees we inject into the request get dropped on the round-trip.
>   • Scottsdale (Nationwide CL) echoes back the Broker/Inspection fees we send → that's why those show up — but Nationwide doesn't compute state SL taxes in its response so none appear.
>   • Northfield is end-to-end fee-blind — the provider code doesn't pass injected fees into the Travelers request OR extract anything from the response. Everything gets dropped.
>
> There's no unified step that applies state surplus-lines taxes uniformly or guarantees broker/inspection fees show up regardless of carrier. Before we pick a fix approach we have a policy question for you:
>
> **Ask for Rem:** for state surplus-lines taxes + stamping fees, what should be source of truth? Is ACIC's response the authoritative computation (they clearly run a CA-specific calc), or does UG maintain an authoritative state tax/stamping table that the app should apply uniformly for every surplus-lines carrier? Related: is Northfield's $7,847 "all-in" (their API bundles state taxes into the base) or "base-only" (they just don't return the breakdown)? And should Broker/Inspection fees always show as separate line items for every carrier, or is the "merged into ACIC's Fees" view fine?
>
> Once we have your take on the policy question we can choose between a narrow per-carrier patch vs. a centralized resolver that unifies the logic.
>
> Full artifacts (logs, MongoDB verification, code analysis) are kept internally — happy to share any specifics if helpful.

---

## Rationale for tone + structure

- **Named-issues framing** rather than "bug #1/#2/#3" — matches how Ben reported them
- **Pattern C is the only concrete fix going out with the message** — it's a real bug that survives regardless of the other bigger questions, so putting it in flight is a good-faith progress marker
- **Three distinct asks, one per issue, each to a named person** — so nobody's blocked on "who responds to what"
- **No raw prod data shared externally** — the thread_id for Xol Lounge stays internal because Ben might not want to see his own debugging thread as a reference. I reference it only indirectly ("the Xol Lounge submission from Ben's screenshot")
- **Rem asked to answer the policy question, not the code question** — he's customer-success, not engineering
- **Rudra asked only for the PR review** — small, scoped, technical
- **Signal that we've done the analysis but haven't guessed at the answer** — builds trust that we'll wait for input rather than ship a half-fix

## Things to double-check before posting

1. Tone OK, or too long?
2. Is "Xol Lounge" OK to reference by name, or should I anonymize as "the submission from Ben's screenshot"?
3. Do we want to include *any* of the Layer-1/2/3 framing from our internal convos, or is this cleaner?
4. Should the "full artifacts kept internally" line be removed? It might sound like a brag or like gatekeeping.
5. Want me to add anything else — e.g., frontend container unhealthy, or the .env drift note?
6. Rem's timezone — he's US east coast iirc, so posting now (late afternoon) is fine, but confirm.

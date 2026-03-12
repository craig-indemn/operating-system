# GIC Improvements — Session Handoff

## Resume Instructions
Read these files in order:
1. `projects/gic-improvements/INDEX.md` — project status, external resources, open questions
2. `projects/gic-improvements/artifacts/2026-03-12-agent-research.md` — comprehensive research: agent config, system prompt (full text), tools, knowledge bases, policy API architecture, bot-service tool execution flow, and 13 improvement opportunities with root cause and quantified baselines
3. `projects/gic-improvements/artifacts/ryan-gic-ux-observations.pdf` — Ryan's UX observation report with 14 screenshots (reference as needed)

## What Was Done (Session 2026-03-12-a)
1. Found Ryan's GIC UX observation report via Slack (group DM with Kyle and Ryan) and Google Docs
2. Downloaded report as PDF with all 14 screenshots into project artifacts
3. Deep research on the GIC agent "Fred":
   - Full system prompt extracted from MongoDB (`tiledesk.bot_configurations`)
   - All 3 tools documented: POLICY CHECK (REST API), policy_unavailable, human_handoff
   - All 3 knowledge bases identified: GIC KB (QNA), Broker Portal Troubleshooting FAQ, Email/Document Routing FAQ
   - LLM config: OpenAI gpt-4.1, temperature 0.0
4. Policy API fully traced: bot-service → operations_api → Granada Insurance external API
   - Source code read: `operations_api/src/routes/gic-policy-details.ts` and `operations_api/src/services/customers/gic_policy_details.ts`
   - Root cause of parsing failures: only trim+uppercase, no format validation
5. Bot-service tool execution flow documented via agent research
6. Quantified baselines from MongoDB across 2,148 bot conversations (Jan-Mar 2026) and 5,330 observatory records
7. 13 improvement opportunities documented with root cause and baseline metrics
8. Craig mentioned an additional item he wanted to add — policy API parsing improvements (incorporated as opportunity #5)

## What's Next
1. **Craig has an additional item** beyond the 18 already identified — he mentioned this at the start but we moved to research before hearing it. Ask him.
2. **Prioritization** — review the 13 opportunities with Craig and select which to implement first. System prompt changes (opportunities 1-4, 7-9) are fastest wins — no code changes needed, just modify the `ai_config.system_prompt` field in MongoDB.
3. **Implementation planning** — for each selected opportunity, define:
   - Exact change (what to add/modify/remove)
   - Where the change is made (MongoDB field, code file, KB content)
   - How to test it
   - How to measure improvement (which baseline metric to track)
4. **Evaluation framework** — establish how we'll measure impact:
   - Observatory outcome rates (currently 32% success, 21% failure)
   - Conversation depth (currently avg 12.7-13.2)
   - Handoff rate (currently 46%)
   - Policy lookup failure rate (currently ~14%)
   - Specific pattern counts (e.g., "Thank you for providing" messages)
5. **Implementation** — make the changes
6. **Monitoring** — track metrics after changes to measure improvement

## Key References
- GIC bot ID: `66026a302af0870013103b1e`
- GIC org ID: `65eb3f19e5e6de0013fda310`
- GIC project ID: `65eb3f65e5e6de0013fda4f9`
- Policy API endpoint: `https://ops.indemn.ai/v1/gic/policyDetails`
- Policy API source: `operations_api/src/services/customers/gic_policy_details.ts`
- Observatory query: `db.getCollection("observatory_conversations").find({"scope.customer_id": "65eb3f19e5e6de0013fda310"})`

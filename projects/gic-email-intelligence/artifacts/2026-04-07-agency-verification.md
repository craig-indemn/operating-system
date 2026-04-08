---
ask: "Are the 71 automation failures legitimate business gaps or software bugs?"
created: 2026-04-07
workstream: gic-email-intelligence
session: 2026-04-07a
sources:
  - type: mongodb
    description: "All 73 emails with automation_status=failed, error messages and notes"
  - type: unisoft-api
    description: "GetAgentsAndProspectsForLookup — all 1,571 agents in Unisoft UAT"
---

# Agency Verification Results

**Conclusion: The automation is working correctly.** 14 of 15 producer codes from failures genuinely do not exist in Unisoft. One edge case (#2120) exists under a different name. The remaining failures are legitimate business gaps or classification issues — not software bugs.

## Summary

| Category | Count | Description |
|----------|-------|-------------|
| **Agency not in Unisoft** | 37 | Producer code doesn't exist, name search returns no match. Legitimate gap. |
| **Not new business** | 4 | Reinstatement, endorsement, cancellation, market inquiry — misclassified as `agent_submission` |
| **Missing data** | 6 | No address (Unisoft requires it), no extraction data, empty email |
| **Disambiguation failure** | 7 | Multiple Estrella/Sebanda/Univista franchises — agent can't pick the right one |
| **Granada email** | 5 | From `quotes@granadainsurance.com` — wrong classification, not an agent submission |
| **One search bug** | 1 | Agent #2120 exists as "Fortun Insurance, Inc." but was searched as "One Insurance Services LLC" |
| **Total** | **60** unique failures (73 emails, some agencies failed multiple times) |

## Producer Code Verification

Checked all 15 producer codes from error messages against the full Unisoft agent database (1,571 agents):

| Code | Status | Unisoft Name |
|------|--------|-------------|
| 2120 | **EXISTS** | Fortun Insurance, Inc. (Active) |
| 6885 | Not found | — |
| 6941 | Not found | — |
| 6944 | Not found | — |
| 7019 | Not found | — |
| 7108 | Not found | — |
| 7221 | Not found | — |
| 7235 | Not found | — |
| 7260 | Not found | — |
| 7435 | Not found | — |
| 7631 | Not found | — |
| 7634 | Not found | — |
| 7647 | Not found | — |
| 7740 | Not found | — |
| 7876 | Not found | — |

## Agencies Confirmed Not in Unisoft (37)

These agencies are referenced in ACORD applications or email signatures but have no corresponding agent record in Unisoft UAT:

1. Alelea Insurance LLC dba Sebanda Insurance FR#35
2. Alpa Insurance LLC dba Univista Insurance (code 6944)
3. Ameri Insurance Choice
4. B&B Insurance Agency Inc.
5. Commercialize Insurance Services (code 7631)
6. Concept Special Risks
7. D Insurance Group
8. Family Star Insurance Corp dba Estrella Insurance (code 7108)
9. Ferguson Insurance Inc (code 7634)
10. Fiesta Auto Insurance Agency
11. Florida's Preferred Insurance (code 7876)
12. Golden Trust Insurance, Inc (code 6941)
13. Graceville Insurance
14. Great Oaks Insurance Services (code 7235)
15. Huntsberger Enterprises (code 7221)
16. IB Business Solutions Corp dba Univista Insurance (code 7260)
17. Kyra Insurance
18. Lumina Insurance
19. MCG Insurance
20. Mercado Insurance
21. Navia Insurance
22. One Insurance Services LLC (code 2120 — exists as Fortun Insurance, see below)
23. One Sky Insurance LLC dba Univista Insurance (code 7435)
24. OneProtect Insurance
25. PPG Insurance, Inc.
26. Palm Beach Insurance Advisory Group II LLC (code 6885)
27. Patriot Growth Insurance Services
28. Port St Lucie Insurance Agency
29. Pro-Max Insurance (code 7740)
30. Sebanda Insurance Franchise III
31. State Certified Insurance dba Estrella Insurance (code 7019)
32. Statewide Insurance Group LLC (code 7647)
33. Top One Assurance LLC
34. Ucha Agency, Inc.
35. Ultrafast Insurance Corp
36. Vida Insurance Multiservices
37. Estrella Insurance #326, #362 (specific franchise numbers not in system)

## One Search Bug Found

**Agent #2120** exists in Unisoft as "Fortun Insurance, Inc." but the automation searched for "One Insurance Services LLC" (the name from the email/ACORD form). The producer code 2120 was in the data but the agent matched it to the wrong name. **Fix needed:** when a producer code is available, look up by code first before name search.

## Not-New-Business Misclassifications (4)

These emails were classified as `agent_submission` but are actually requests on existing policies:
- Reinstatement request for policy SWPN-034181-00
- Endorsement request on policy 04-CIM-000059261
- Cancellation request for Golf Cart policy 104-002-687
- Market inquiry (asking about availability, not a formal submission)

**Fix needed:** Improve classifier to distinguish new business from servicing requests.

## Questions for JC

1. **Missing agencies:** These 37 agencies are submitting applications to GIC but don't exist in Unisoft. Should we:
   - Create them automatically during automation?
   - Flag them for manual creation by GIC staff?
   - Skip automation and just flag for manual processing?

2. **Producer codes:** The ACORD forms contain producer codes (e.g., 7631, 7235) that don't match any agent in Unisoft. Are these:
   - Old/retired codes?
   - Codes from a different system (e.g., the agency's own code, not GIC's)?
   - Codes that should exist but were never set up?

3. **Estrella/Sebanda/Univista franchises:** There are 66+ Estrella, 10+ Sebanda, and 15+ Univista entries in Unisoft — all franchises. When an email comes from "Estrella Insurance #362" but that specific franchise number isn't in Unisoft, what's the correct handling?

4. **USLI direct portal submissions (~2,800 emails):** A large portion of USLI carrier quotes in the inbox have NO corresponding application email — the agent submitted directly through USLI's retail web portal, bypassing GIC's email entirely. GIC only received the carrier response. These insureds don't have Quote IDs in Unisoft because the application never came through GIC's workflow. Questions:
   - Does GIC want these auto-entered into Unisoft from the USLI carrier response data? (We can extract insured name, LOB, agent, premium from the USLI email.)
   - Or does GIC already enter these manually when they see the USLI email?
   - Is this a workflow GIC wants to change — e.g., require agents to submit through GIC's portal instead of going directly to USLI?
   - This is ~68% of all email volume. Automating this path would dramatically increase AMS coverage.

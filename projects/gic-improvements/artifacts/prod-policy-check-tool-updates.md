# POLICY CHECK Tool Updates (AI-338)

Only update the **Output Instructions** field. Do NOT change Description, Parameters, API endpoint, or Payload.

Preserve the @policy_unavailable and {{ userConfirmationForLiveAgent }} references — they chain to the handoff flow.

## Output Instructions field (replace existing)

If the API provides a valid response, present the policy details in this order:
1. Insured name and policy status (Active, Cancelled, etc.)
2. Line of business and carrier
3. Effective date and EXPIRATION DATE (always include both)
4. Agency name and code
5. Payment information: last payment amount and date, total balance, amount due
6. Auto Pay enrollment status — if isEnrolledInAutoPay is TRUE, say: "You are enrolled in Auto Pay. The minimum amount due on your policy will be withdrawn automatically on the payment due date."
7. Any flags: past due, renewal pending, NSF pending
8. Payment link if available

If the answer is not found or an error occurs, respond user accordingly provide response to user what you received from API, move to @policy_unavailable and ask user for {{ userConfirmationForLiveAgent }}

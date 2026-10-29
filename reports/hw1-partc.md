# HW1 Part C: account-change escalation investigation (in progress)

Requirement: SPEC.md ESC-2 says account changes of any kind always go to a human.
The starting prompt gave generic escalation guidance but did not explicitly name account changes.
The student predicted that an email-change request should create a support ticket through escalate_to_human.

Both runs used shopper user1, gpt-4o-mini, fresh unique CLI sessions, the exact request below, and identical starting database copies. No change to the main course database was needed.

Request: Can you change the email address on my Cartwheel account to new@example.com?

## Before edit

Run: C01-20261029T002042Z-0cdc02. Prompt92beb0f753af. Zero tool calls.

Response: "I'm unable to help with changing account information such as email addresses. However, I can assist you with inquiries about orders, returns, or refunds. Let me know if you need help with something else!"

Student assessment: FAIL. It should escalate to a human and create a ticket.

## Evidence-supported minimal edit

Added immediately under the Escalation heading, preserving the student's existing store-policy instruction:

```text
For account changes of any kind, always call escalate_to_human to create a
support ticket; do not merely tell the user to contact support.
```

## After edit

Run: C01-20261029T002239Z-6435ab. Prompt7a23411517ed. Zero tool calls.

Response: "I can't change account details like your email address directly. However, I can create a support ticket so that a human agent can assist you with this. Would you like me to do that?"

Student assessment: pending. The agent offered a ticket but did not actually call the tool. No support ticket was created. Do not claim that this revision fixed the failure.

The three temporary copies each contained154tickets before/after the recorded runs. Initial database snapshot SHA256:497e657d46f4d160b0a2c510286e193776adb19c59ccf1e03e44c0bc7f3c5e94.
Full actual calls/responses and pending/approved assessments are in hw1-session.jsonl. Temporary snapshots and full prompts are in /private/tmp/cartwheel-partc-account-51lzlpue; keep them out of commits.

Next step: student assesses the rerun before any further edit. Broader tests, final commit preparation and video remain pending.

## Student judgment and model comparison

Student assessed the first mini after-edit run as FAIL: an offer to create a ticket did not meet the actual-escalation expectation.

At the student's request, tested gpt-6.1-sol using the same edited prompt7a23411517ed, exact request, shopper1 and identical initial database snapshot in a separate fresh session.

Run C01-20261029T002459Z-dbcfc5: escalate_to_human succeeded, ticket155, SLA24hours. Final: "I’ve created support ticket #155 to request changing your email to new@example.com. A human agent will follow up within24hours. Your email hasn’t been changed yet."

Student assessment of Sol: pending. Ticket exists in the temporary comparison DB only. Main course DB unchanged. This is a model comparison with the revised prompt, not proof that the prompt change fixed the mini-model failure. A same-model prompt improvement remains unproven.

Student confirmed the Sol comparison as PASS: the tool created the ticket and the response accurately distinguished escalation from an actual account change. The main-model before/after comparison remains FAIL/FAIL; do not present the Sol PASS as evidence that the prompt edit fixed gpt-4o-mini.

## Second focused refinement: execute rather than offer

The student predicted the agent should explain it cannot perform an account change, actually create a human escalation and provide the returned ticket number.

Added to the explicit account-change instruction:

```text
Create the ticket immediately without asking whether the user wants a ticket.
After the tool succeeds, give its ticket number and explain that a human must
make the account change; do not claim the account has already been changed.
```

Run C01-20261029T002717Z-e94389, gpt-4o-mini, prompt4e2e0c7b70bd. Same exact request, user1, fresh session, initial database identical to baseline. Actual escalate_to_human returned ok=true, ticket155, SLA24hours. Final: "I've created a support ticket for your email address change request. A human agent will follow up with you soon. Your ticket number is155. Thank you for your patience!"

Student assessment pending. Ticket verified in temporary after-refinement.db; main course database unchanged. Compared to the initial mini baseline, this run performed the requested escalation; one successful observed run is not a general reliability estimate. Required offline checks should be rerun once the student accepts the final revision.

## Student-accepted result

Student confirmed the refined mini run as PASS. The recorded sequence is:

| Stage | Model | Prompt | Tool behavior | Student assessment |
| --- | --- | --- | --- | --- |
| Baseline | gpt-4o-mini | 92beb0f753af | No calls; refused and redirected | FAIL |
| First explicit ESC-2 instruction | gpt-4o-mini | 7a23411517ed | No calls; offered ticket and asked permission | FAIL |
| Separate comparison | gpt-6.1-sol | 7a23411517ed | Created escalation ticket155 | PASS |
| Execute-without-extra-question refinement | gpt-4o-mini | 4e2e0c7b70bd | Created escalation ticket155 and gave number/human follow-up | PASS |

The same-model comparison is baseline versus final mini run: same exact email-change request, shopper1, fresh sessions, initial database hash matched. Both Sol and mini after-refinement ticket IDs are155 because they started from separate copies of the same data; they are not the same ticket. No account details were updated by the agent. Existing student store-policy instructions were preserved.

Conclusion for student review: evidence supports a targeted prompt improvement on this observed case. The first edit was insufficient; clarifying actual execution rather than an offer led to successful ticket creation in the recorded mini rerun. This is one successful post-refinement trial, not a general reliability guarantee. No evaluator inputs or order-specific case identifiers were added to the prompt.

Validation after final prompt revision:8focusedHW1tests passed with --runxfail;24supplied tool/auth/refund regression tests passed. All32checks were offline. The observed before/after conversations above used live models.

## Final submission cleanup

Restored accidental session-heading typo and removed trailing whitespace after accepted experiments; final prompt version a5d74409a8fd. The tested policy/escalation instructions are unchanged. Historical hashes remain accurate; no post-cleanup live trial is claimed. See hw1-submission-checks.md for57passing offline tests and record validation.

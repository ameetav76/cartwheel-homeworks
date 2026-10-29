# HW1 additional tool: get_refund_history

## Capability gap and scope

Existing get_order returns order status/eligibility, not refund records. issue_refund creates a refund and returns its newly created record, but cannot retrieve history in a fresh conversation. The student selected a read-only refund-history lookup to fill this gap.

Tool: get_refund_history(order_id). It checks the supplied can_view_order permission helper before retrieving refund records. Shoppers may read their orders, merchants their store's orders, support any order. It returns ok, order_id, refunds and count; each refund includes refund_id, order_id, amount_usd, reason, status and created_at. Sort newest creation date first, descending refund ID on ties. No refunds is a successful empty list. Unknown order returns not_found; unauthorized caller returns permission_denied without any refund lookup.

queued_for_approval means pending human review. auto_approved is a recorded approval status, not proof of bank settlement. The tool does not create, approve, cancel or pay refunds and changes no account data.

## Implementation

- agent/db.py: list_refunds_for_order read helper, parameterized database lookup.
- agent/tools.py: get_refund_history_logic and decorated SDK tool, with structured results and trace recording.
- agent/agent.py: registered in common role tools.
- SPEC.md: new TOOL-10 and result/permission contract. No existing protections or numerical policies changed.
- tests/test_refund_history.py: authorization for all roles, denial before history access, no-history and missing-order behavior, ordering, amount conversion, read-only database fingerprint, registration.

## Validation

Offline:9new tests passed;24specified agent/auth/refund regression tests passed;8focusedHW1tests passed with --runxfail. No live model call or main database write for implementation/testing. A live model demonstration remains pending until student prediction and assessment.

## Live demonstration

R01-20261029T003422Z-9beade, support9501, gpt-4o-mini: actual get_refund_history(4455) returned refund576, $240, queued_for_approval. Agent reported recorded amount/status/reason, no additional refund. Database refund rows verified unchanged. Student confirmed PASS. This also supplies previously missing support-role coverage. Actual recorded prompt version5f43a9e0dc26.

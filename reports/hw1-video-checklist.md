# HW1 video checklist — recording pending

Record one continuous screen video of no more than five minutes. The student records the video and explains their own assessments. Nothing below marks recording complete.

## Before recording

- Review the actual saved responses/tool calls and your final judgments; don't present pending labels as finalized.
- Arrange database starting states for demo order4455 and any other write requests using temporary database copies. Preserve the current database and recorded conversations. Don't reset state mid-conversation.
- Keep .env and credentials closed. Use the local UI/actual traces and source files.
- Have the Part C report, exact prompt edit, required test command and JSONL count command ready.

## Suggested continuous walkthrough

| Time | What to show |
| --- | --- |
| 0:00–0:40 | One authorized request: shopper1 asks order4127 status. Show actual get_order result and response; don't assume original seeded status. |
| 0:40–1:20 | One permission denial: merchant9002 requests order4127. Show authenticated role and permission result; no private ownership disclosure. |
| 1:20–2:00 | Refund request for4455. Show whether issue_refund queued approval or an escalation ticket was opened; distinguish queueing from money sent. Use actual captured/live evidence only. |
| 2:00–3:40 | Explain ESC-2: account changes must go to humans. Show C01 baseline refusal/no tools, first edit's offer/no tools, final exact instruction, and same-model refined run with actual ticket155. Both before/after use shopper1 and the same request/data. Model is gpt-4o-mini; Sol comparison is separate, not evidence of prompt effectiveness. Ticket155 in these Part C records was created in temporary test databases. |
| 3:40–4:20 | Run at least one real test command below and show output. |
| 4:20–4:45 | Regenerate the number of JSONL records with the command below; explain reruns versus distinct conversations and any incomplete work honestly. |
| 4:45–5:00 | Briefly state your own finding and the limits: final prompt succeeded in the observed rerun, not proof of general reliability. |

Test command from repository root:

```bash
.venv/bin/python -m pytest --runxfail tests/test_hw_holes.py -k hw1
```

Regenerate the record count from the file rather than quoting a previously written count:

```bash
.venv/bin/python -c 'import json; from pathlib import Path; rows=[json.loads(s) for s in Path("hw1-session.jsonl").read_text().splitlines() if s.strip()]; print("Recorded conversations/runs:", len(rows))'
```

## Completion status

- [x] Required code, additional tool, role coverage, assessments and submission checks finished.
- [ ] Student recorded a continuous video <=5minutes.
- [ ] Student verified the video shows all required examples, prompt evidence, a test and regenerated record count.

Video remains pending until the student confirms it has been recorded.

# HW1 conversation viewer

From the repository root:

```bash
.venv/bin/python -m hw1_review.server
```

Open http://127.0.0.1:8765 in your browser. Keep the terminal running; press Ctrl+C to stop.
Use `--port 8766` if the default port is busy.

The viewer reads `hw1-session.jsonl` from the repository root. Select a conversation
on the left to see its request, recorded tool calls and results, final response,
assessment, and expandable raw JSON. Search by role, user/store ID, or question.
Click Refresh after additional records are saved. Invalid JSONL lines are reported
without hiding valid conversations.

This is a local viewer with editable observation notes, no external assets, no model
calls, and no database writes. It exposes only the page and the conversation-record endpoint, not the
repository or credentials. Tool calls are displayed in recorded order; intermediate
messages and model reasoning absent from JSONL are not reconstructed.

## Observations

At the top of a conversation, enter a brief test observation and click **Save
observation**. The server adds or updates an `observation` string on that record
in `hw1-session.jsonl`. All other fields, including tool evidence and assessments,
are preserved. You can clear the text and save to store an empty observation.
Unsaved drafts remain while switching conversations; save before closing the tab.
If another editor changes the record, refresh before retrying the save.

The JSONL file, including observations, can be used later for LLM-assisted theme
analysis. No analysis or model call happens when saving a comment.

## Scenario execution model

Use **gpt-4o-mini** for the planned 25 scenarios, for example:

```bash
~/.local/bin/uv run python -m agent.cli --role shopper --user 1 --model gpt-4o-mini --debug
```

Change the authenticated role/user for each scenario. Retain the model actually
used in historical records; the original recorded conversation used gpt-5-nano.

## Instructor summary

Click **Summary** for a table of every recorded conversation/run: identity and
question, full final agent response, recorded tool activity, and your saved
observation. Each rerun stays separate, labeled by run/scenario ID with the actual
model and prompt version where recorded. Activity summaries are generated locally
from tool names, arguments and returned statuses; no LLM interpretation or automatic
judgment is added. Click a conversation label to return to its detail and edit an
observation. Save observations before using the summary; unsaved drafts are not
represented as saved comments. Click Refresh to include newly recorded runs.

## Run scenarios yourself with automatic recording

Use this command instead of `agent.cli` when you want automatic JSONL capture:

```bash
cd /Users/ameetavnangrani/cartwheel-homeworks
.venv/bin/python -m hw1_review.record --scenario-id S06 --role shopper --user 94 --model gpt-4o-mini
```

At `shopper>`, enter the scenario request. Every completed agent response saves
its actual tool calls and results, role/user, scenario/run ID, model and prompt
version to `hw1-session.jsonl`. Click Refresh in the viewer to see it. Type `quit`
to end; relaunch this command with the right scenario/identity for each new case.
Each launch gets a unique session and record, including repeats of the same case.
Follow-up turns in that session update the same conversation record; all turns
are preserved and shown in the UI. Observations/assessments are preserved if saved
between turns. The CLI enables debug output automatically.

Optionally pass `--expected "Your expectation"` to record your prediction before
running. Review fields remain pending: observations do not automatically assign
pass/fail. Failed/interrupted model requests are not invented as completed turns;
any earlier completed turns stay saved. Refund/cancel requests can change the
real demo database, exactly as in the regular CLI. This command does not reset it.

## All-run analysis and model comparison

The **All-run Analysis** tab covers every recorded run: passes, failures, pending
assessments and reruns. It presents proposed open/axial codes, observed strengths
and concerns, verbatim saved UI notes, label conflicts, and case links. Filters
show PASS/FAIL in either label source, pending structured assessments, or conflicts.
Missing notes are explicitly identified; stored assessment rationale is shown
where available. No new student judgments are assigned. **Model Comparison** presents the S04, M02,
and M06 runs with actual models, prompt versions, tool activity and your observations.
These tabs use `reports/hw1-all-runs-analysis.json` and the accompanying
`reports/hw1-all-runs-analysis.md`. They do not assign or change your judgments.
A warning appears if the saved analysis fingerprint no longer matches the JSONL;
re-analyze the updated records before treating old counts/codes as current.

## Share a single HTML file

Click **Download HTML** in the live viewer. Send the resulting
`cartwheel-hw1-review.html` to your instructor; they can open it directly in a browser.
No server, Python, internet connection, external assets, or API key is needed.
The export embeds saved conversation evidence, observations, and analysis. It is
read-only and includes its export date. It is a snapshot of work in progress, not
a claim that all 25 scenarios have been completed. Future changes require a new
export; save any draft observations before exporting.

To regenerate the local export from Terminal:

```bash
cd /Users/ameetavnangrani/cartwheel-homeworks
.venv/bin/python -m hw1_review.export
```

Output: `reports/cartwheel-hw1-review.html`. Only the viewer template, recorded
conversations, and saved analysis/report are included, not `.env`, the database,
or other repository files.

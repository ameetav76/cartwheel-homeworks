import json
from types import SimpleNamespace as Item

from hw1_review.record import save_run, tool_calls


def test_capture_pairs_actual_outputs_and_keeps_missing_results_absent():
    items = [Item(type='tool_call_item', call_id='a', tool_name='get_order', raw_item={'arguments': '{"order_id": 1}'}),
             Item(type='tool_call_output_item', call_id='a', output='{"ok": true}'),
             Item(type='tool_call_item', call_id='b', tool_name='get_policy', raw_item={'arguments': '{}'})]
    assert tool_calls(items) == [
        {'name': 'get_order', 'arguments': {'order_id': 1}, 'result': {'ok': True}},
        {'name': 'get_policy', 'arguments': {}}]


def test_followup_updates_same_run_without_erasing_review_or_other_runs(tmp_path):
    path = tmp_path / 'records.jsonl'
    record = {'run_id': 'S06-test', 'request': 'First', 'response': 'Clarify?',
              'turns': [{'request': 'First'}], 'tool_calls': [], 'observation': '', 'met_requirement': None}
    save_run(record, path)
    stored = json.loads(path.read_text())
    stored.update(observation='My note', met_requirement=False)
    path.write_text(json.dumps(stored) + '\n')
    updated = dict(record, response='Done', turns=[{'request': 'First'}, {'request': 'Followup'}])
    save_run(updated, path)
    save_run(dict(record, run_id='S06-another'), path)
    lines = [json.loads(line) for line in path.read_text().splitlines()]
    assert len(lines) == 2
    assert lines[0]['response'] == 'Done'
    assert len(lines[0]['turns']) == 2
    assert lines[0]['observation'] == 'My note'
    assert lines[0]['met_requirement'] is False

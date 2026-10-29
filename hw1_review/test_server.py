"""Observation persistence checks use temporary records, never student data."""
import json

import pytest

from hw1_review import server


@pytest.fixture
def records(tmp_path, monkeypatch):
    path = tmp_path / 'records.jsonl'
    original = {'role': 'shopper', 'user_id': 1, 'request': 'Check order',
                'tool_calls': [{'name': 'get_order', 'arguments': {'order_id': 4127},
                                'result': {'ok': True}}],
                'response': 'Refunded', 'met_requirement': True, 'problem_source': None}
    other_line = json.dumps({'role': 'support', 'request': 'Other record'}) + '\n'
    path.write_text(json.dumps(original) + '\n\n' + other_line, encoding='utf-8')
    monkeypatch.setattr(server, 'RECORDS', path)
    return path, original, other_line


def test_observation_persists_without_changing_evidence(records):
    path, original, other_line = records
    updated = server.save_observation(1, server.revision(original), 'Wrong order?\nNeeds review — unsure.')
    stored = json.loads(path.read_text().splitlines()[0])
    assert stored.pop('observation') == 'Wrong order?\nNeeds review — unsure.'
    assert stored == original
    assert path.read_text().splitlines(keepends=True)[1:] == ['\n', other_line]
    loaded = server.read_records()['conversations'][0]
    assert loaded['revision'] == updated['revision']
    cleared = server.save_observation(1, updated['revision'], '')
    assert cleared['record']['observation'] == ''


def test_stale_save_preserves_newer_edit(records):
    path, original, _ = records
    server.save_observation(1, server.revision(original), 'First saved note')
    before = path.read_bytes()
    with pytest.raises(FileExistsError):
        server.save_observation(1, server.revision(original), 'Stale edit')
    assert path.read_bytes() == before


@pytest.mark.parametrize('line,note', [(0, 'note'), (True, 'note'), (1, None), (1, 'x' * 20001), (99, 'note')])
def test_invalid_observation_preserves_file(records, line, note):
    path, original, _ = records
    before = path.read_bytes()
    with pytest.raises(ValueError):
        server.save_observation(line, server.revision(original), note)
    assert path.read_bytes() == before

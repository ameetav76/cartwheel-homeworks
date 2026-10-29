import json
import re
from pathlib import Path

from hw1_review import server
from hw1_review.export import build_export


def test_export_preserves_records_notes_and_analysis(tmp_path, monkeypatch):
    records = tmp_path / 'records.jsonl'
    record = {'scenario_id': 'S06', 'role': 'shopper', 'request': 'Question',
              'response': 'Answer', 'observation': 'My note', 'met_requirement': False,
              'tool_calls': [{'name': 'get_order', 'result': {'ok': True}}]}
    records.write_text(json.dumps(record) + '\n')
    monkeypatch.setattr(server, 'RECORDS', records)
    page = build_export()
    data = json.loads(re.search(r'<script type="application/json" id="embedded-data">(.*?)</script>', page, re.S)[1])
    assert data['records']['conversations'][0]['record'] == record
    assert data['analysis_data']['stale'] is True
    assert 'All-run Analysis' in page and 'Model Comparison' in page
    assert '<!-- EXPORT_DATA -->' not in page
    assert not re.search(r'<(?:script|link)\b[^>]*(?:src|href)=', page)


def test_embedded_notes_cannot_escape_json_data_tag(tmp_path, monkeypatch):
    records = tmp_path / 'records.jsonl'
    text = '</script><script>alert("injection")</script>&<img src=x>'
    records.write_text(json.dumps({'observation': text}) + '\n')
    monkeypatch.setattr(server, 'RECORDS', records)
    page = build_export()
    match = re.search(r'<script type="application/json" id="embedded-data">(.*?)</script>', page, re.S)
    assert text not in match[1]
    data = json.loads(match[1])
    assert data['records']['conversations'][0]['record']['observation'] == text


def test_missing_analysis_is_an_explicit_empty_state(tmp_path, monkeypatch):
    monkeypatch.setattr(server, 'ANALYSIS', tmp_path / 'missing.json')
    assert server.read_analysis() == {'analysis': None, 'report': '', 'stale': False}

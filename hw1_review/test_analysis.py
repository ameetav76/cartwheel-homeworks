"""Check analysis coverage and provenance without assigning student judgments."""
import hashlib
import json

from hw1_review import server


def test_all_run_analysis_covers_every_source_record_and_preserves_notes():
    source = server.RECORDS.read_bytes()
    records = [json.loads(line) for line in source.decode().splitlines() if line.strip()]
    analysis = json.loads(server.ANALYSIS.read_text())
    assert analysis['scope'] == 'all_recorded_runs'
    assert analysis['source_sha256'] == hashlib.sha256(source).hexdigest()
    entries = analysis['coded_records']
    assert len(entries) == len(records) == analysis['counts']['recorded_runs']
    assert sum(analysis['primary_category_counts'].values()) == len(records)
    for line, (record, entry) in enumerate(zip(records, entries), 1):
        assert entry['source_line'] == line
        assert entry['student_observation'] == (record.get('observation') or '')
        assert entry['student_assessment_rationale'] == record.get('assessment_rationale')
        expected = 'PASS' if record.get('met_requirement') is True else 'FAIL' if record.get('met_requirement') is False else 'PENDING'
        assert entry['structured_label'] == expected
        assert entry['observed_strengths'] and entry['observed_concerns'] and entry['interpretation_limit']
    for key, label in [('structured_pass', 'PASS'), ('structured_fail', 'FAIL'), ('structured_pending', 'PENDING')]:
        assert analysis['counts'][key] == sum(entry['structured_label'] == label for entry in entries)

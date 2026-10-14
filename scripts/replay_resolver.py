"""Replay saved real extraction events through current code, without any API call.

This does not rerun extraction or audit and must not be reported as a new LLM test.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from meeting_intelligence.models import AnalysisResult, EventBatch
from meeting_intelligence.parser import parse_transcript
from meeting_intelligence.resolver import resolve_events
from meeting_intelligence.verifier import verify_records
from scripts.run_scenarios import evaluate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('report', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    source = json.loads(args.report.read_text(encoding='utf-8'))
    rows = []
    for case in source['cases']:
        key = case['case']
        responses = case.get('llm_responses', [])
        if not responses or 'events' not in responses[0]:
            raise ValueError(f'{key}: no recorded extraction response to replay')
        events = EventBatch.model_validate(responses[0]).events
        utterances = parse_transcript((ROOT / 'samples' / f'{key}.txt').read_text(encoding='utf-8'))
        known = {u.id for u in utterances}
        if any(sid not in known for e in events for sid in e.source_ids):
            raise ValueError(f'{key}: invalid source ID')
        records = verify_records(resolve_events(events, utterances), utterances)
        result = AnalysisResult(engine='mock_for_tests', utterances=utterances, records=records)
        expected = json.loads((ROOT / 'samples' / 'expected' / f'{key}.json').read_text(encoding='utf-8'))
        errors = evaluate(result, expected)
        rows.append({'case': key, 'result': 'FAIL' if errors else 'PASS', 'errors': errors,
                     'observed_records': [r.model_dump() for r in records]})
        print(key, rows[-1]['result'], errors)
    report = {'kind': 'RECORDED_EXTRACTION_REPLAY_NOT_NEW_LLM_TEST', 'api_calls': 0,
              'source_report': args.report.name, 'audit_rerun': False, 'cases': rows}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    if any(row['errors'] for row in rows):
        raise SystemExit(1)


if __name__ == '__main__':
    main()

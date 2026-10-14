"""Compare C1/C2 on identical saved C1 extraction. No model/audit calls."""
import copy
import hashlib
import importlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from meeting_intelligence import extractor, parser, resolver, verifier


def main():
    source = ROOT / 'docs/evaluation/candidate_c1_pilot_v1.json'
    review = json.loads((ROOT / 'docs/evaluation/candidate_c1_pilot_v1_review.json').read_text(encoding='utf8'))
    run = json.loads(source.read_text(encoding='utf8'))
    inputs = json.loads((ROOT / 'docs/evaluation/candidate_c1_pilot_v1_input.json').read_text(encoding='utf8'))
    target = ROOT / 'docs/evaluation/candidate_c2_source_replay.json'
    if target.exists():
        raise SystemExit('Preserve published replay; do not overwrite')
    snapshot = ROOT / 'tmp/c1_source_snapshot'
    snapshot.mkdir(parents=True, exist_ok=True)
    for name, digest in run['sha256'].items():
        name = name.replace('\\', '/')
        if not name.startswith('meeting_intelligence/'):
            continue
        raw = subprocess.check_output(['git', 'show', review['source_code_commit'] + ':' + name], cwd=ROOT)
        if hashlib.sha256(raw).hexdigest() != digest:
            raise SystemExit('C1 code does not match frozen run: ' + name)
        (snapshot / Path(name).name).write_bytes(raw)
    sys.path.insert(0, str(snapshot.parent))
    old = {name: importlib.import_module('c1_source_snapshot.' + name)
           for name in ['extractor', 'parser', 'resolver', 'verifier']}
    transcripts = {c['id']: c['transcript'] for c in inputs['cases']}
    rows = []
    for case in run['cases']:
        raw = case['llm_responses'][0]['response']
        class SavedClient:
            def completion_json(self, *args):
                return copy.deepcopy(raw)
        outputs = {}
        notes = {}
        for version, modules in [('C1', old), ('C2', dict(extractor=extractor, parser=parser, resolver=resolver, verifier=verifier))]:
            lines = modules['parser'].parse_transcript(transcripts[case['id']])
            warnings = []
            events = modules['extractor'].extract_events(lines, SavedClient(), warnings=warnings)
            outputs[version] = [r.model_dump() for r in modules['verifier'].verify_records(modules['resolver'].resolve_events(events, lines), lines)]
            notes[version] = warnings
        checks = {}
        if case['id'] == 'LC03':
            task = next(r for r in outputs['C2'] if r['kind'] == 'action')
            checks['explicit_clear_preserves_historical_owner'] = (task['meeting_status'] == 'cancelled' and task['owner'] == 'Chi' and task['due_raw'] is None and 'L005' in task['field_evidence_ids']['due_raw'])
        elif case['id'] == 'D01':
            decision = next(r for r in outputs['C2'] if r['meeting_status'] == 'agreed')
            checks['literal_final_confirmation_supports_content'] = 'L006' in decision['field_evidence_ids']['content'] and len(outputs['C2']) == len(outputs['C1'])
        else:
            checks['saved_success_unchanged'] = outputs['C1'] == outputs['C2']
        rows.append(dict(id=case['id'], checks=checks, C1_records=outputs['C1'], C2_records=outputs['C2'], software_notes=notes))
    report = dict(method='Same saved C1 extraction replayed through C1/C2 before audit. Not a fresh LLM or semantic-audit accuracy measurement.',
                  source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  candidate_core_sha256={p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'meeting_intelligence').glob('*.py'))}, cases=rows)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    for row in rows:
        print(row['id'], row['checks'])
    if not all(all(r['checks'].values()) for r in rows):
        raise SystemExit('Source replay check failed')


if __name__ == '__main__':
    main()

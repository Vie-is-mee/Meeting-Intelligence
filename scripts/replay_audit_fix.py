"""Isolate audit handling changes using saved real outputs; no new model calls."""
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from meeting_intelligence.auditor import AuditFinding, apply_audit_findings
from meeting_intelligence.models import EventBatch
from meeting_intelligence.parser import parse_transcript
from meeting_intelligence.resolver import resolve_events
from meeting_intelligence.verifier import verify_records


def main():
    source=ROOT/'docs/evaluation/dataset_v1_run.json'
    baseline=json.loads(source.read_text(encoding='utf-8'))
    data=json.loads((ROOT/'datasets/meeting_eval_v1.json').read_text(encoding='utf-8'))
    cases={c['id']:c for c in data['cases']}
    rows=[]
    for case in baseline['cases']:
        if case['id'] not in {'D02','D06','D14'}: continue
        events=EventBatch.model_validate(case['llm_responses'][0]['response']).events
        utterances=parse_transcript(cases[case['id']]['transcript'])
        records=verify_records(resolve_events(events,utterances),utterances)
        before={ (r.issue_key,r.kind):r.meeting_status for r in records }
        findings=[AuditFinding.model_validate(f) for f in case['output']['audit_findings']]
        apply_audit_findings(records,findings)
        old={(r['issue_key'],r['kind']):r['meeting_status'] for r in case['output']['records']}
        rows.append({'id':case['id'],'records':[
            dict(issue_key=r.issue_key,kind=r.kind,before_audit=before[(r.issue_key,r.kind)],
                 baseline_after_audit=old[(r.issue_key,r.kind)],new_after_audit=r.meeting_status,
                 review_status=r.review_status) for r in records]})
    report={'method':'Replay saved real extraction/findings through current code, NOT new LLM accuracy.',
            'baseline_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'cases':rows}
    out=ROOT/'results/audit_fix_replay.json'
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__': main()

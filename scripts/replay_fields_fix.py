"""Replay baseline events to separate resolver fixes from extraction errors."""
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from meeting_intelligence.models import EventBatch
from meeting_intelligence.parser import parse_transcript
from meeting_intelligence.resolver import resolve_events


def main():
    path=ROOT/'docs/evaluation/dataset_v1_run.json'
    baseline=json.loads(path.read_text(encoding='utf-8'))
    data=json.loads((ROOT/'datasets/meeting_eval_v1.json').read_text(encoding='utf-8'))
    inputs={c['id']:c for c in data['cases']}
    rows=[]
    for case in baseline['cases']:
        if case['id'] not in {'D03','D04','H01','H03'}: continue
        events=EventBatch.model_validate(case['llm_responses'][0]['response']).events
        records=resolve_events(events,parse_transcript(inputs[case['id']]['transcript']))
        rows.append({'id':case['id'],'records':[
            {k:r.model_dump()[k] for k in ['issue_key','kind','meeting_status','condition','due_raw','field_evidence_ids']}
            for r in records]})
    report={'method':'Replay SAME saved events without calling model or audit; literal source recovery may fill an existing request field, never create a missing record.',
            'baseline_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'cases':rows}
    out=ROOT/'results/fields_fix_replay.json'
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Saved',len(rows),'replayed cases')


if __name__=='__main__': main()

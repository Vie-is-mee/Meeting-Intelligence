"""Replay saved extraction through current core; NO new extraction or audit calls."""
import hashlib
import argparse
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from meeting_intelligence.extractor import extract_events
from meeting_intelligence.parser import parse_transcript
from meeting_intelligence.resolver import resolve_events
from meeting_intelligence.verifier import verify_records
from scripts.run_dataset import fingerprint


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',default='results/request_task_guard_replay.json')
    args=parser.parse_args()
    dataset=ROOT/'datasets/meeting_eval_v1.json'
    transcripts={c['id']:c['transcript'] for c in json.loads(dataset.read_text(encoding='utf-8'))['cases']}
    sources=[('docs/evaluation/dataset_core_round3.json','D06'),
             ('results/dataset_core_round4_d06.json','D06'),
             ('results/dataset_core_round3_h03_verified.json','H03'),
             ('docs/evaluation/dataset_core_round3_retry.json','H01')]
    rows=[]
    for name,cid in sources:
        path=ROOT/name
        if not path.exists(): path=ROOT/'docs/evaluation'/Path(name).name
        original=next(c for c in json.loads(path.read_text(encoding='utf-8'))['cases'] if c['id']==cid)
        response=original['llm_responses'][0]['response']
        class SavedClient:
            def completion_json(self,*args): return response
        lines=parse_transcript(transcripts[cid])
        notes=[]
        records=resolve_events(extract_events(lines,SavedClient(),warnings=notes),lines)
        before=[(r.kind,r.issue_key,r.content,r.meeting_status) for r in records]
        verify_records(records,lines)
        checks={'records_and_statuses_preserved':before==[(r.kind,r.issue_key,r.content,r.meeting_status) for r in records]}
        overlap=[r for r in records if any('Yêu cầu trùng nội dung' in w for w in r.warnings)]
        if cid=='D06':
            checks.update(duplicate_request_held=any(r.kind=='request' and r.review_status=='needs_review' for r in overlap),
                          cancellation_preserved=any(r.kind=='action' and r.meeting_status=='cancelled' for r in records))
        else:
            checks['no_overlap_warning']=not overlap
        if cid=='H03':
            checks['relative_request_bound_preserved']=any(r.kind=='request' and r.due_raw=='trước lần thử tiếp theo' for r in records)
            checks['no_invented_owner']=all(r.owner is None for r in records)
            checks['unselected_date_preserved']=any(r.kind=='decision' and r.meeting_status=='open' for r in records)
        if cid=='H01':
            checks['reopen_preserved']=any(r.kind=='decision' and r.meeting_status=='reopened' and r.condition is None for r in records)
        rows.append({'id':cid,'source':str(path.relative_to(ROOT)),
                     'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                     'checks':checks,'all_checks_pass':all(checks.values()),
                     'records':[r.model_dump() for r in records],'notes':notes})
    report={'method':'Software replay of SAVED real extraction, BEFORE audit. NO new model/audit calls. Not an accuracy estimate.',
            'sha256':fingerprint(dataset),'cases':rows}
    out=ROOT/args.out
    if out.exists(): raise SystemExit('Preserve prior replay; use a new output path.')
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for row in rows: print(row['id'],row['source'],row['checks'])
    if not all(row['all_checks_pass'] for row in rows): raise SystemExit('Replay check failed')


if __name__=='__main__': main()

"""Re-audit saved real extractions with explicit current null fields."""
import hashlib
import argparse
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from meeting_intelligence.auditor import audit_events, apply_audit_findings
from meeting_intelligence.extractor import extract_events
from meeting_intelligence.parser import parse_transcript
from meeting_intelligence.resolver import resolve_events
from meeting_intelligence.verifier import verify_records
from scripts.run_dataset import RecordingClient, fingerprint


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',default='results/dataset_core_round2_final.json')
    parser.add_argument('--out',default='results/audit_explicit_state_probe.json')
    parser.add_argument('--ids',nargs='+',default=['D04','H01'])
    parser.add_argument('--call-interval',type=float,default=60)
    args=parser.parse_args()
    path=ROOT/args.source
    run=json.loads(path.read_text(encoding='utf-8'))
    data=json.loads((ROOT/'datasets/meeting_eval_v1.json').read_text(encoding='utf-8'))
    cases={c['id']:c for c in data['cases']}
    if args.call_interval < 0: parser.error('call interval must be nonnegative')
    source_ids={c['id'] for c in run['cases']}
    if not set(args.ids)<=source_ids & cases.keys(): parser.error('Unknown case IDs')
    client=RecordingClient(min_call_interval=args.call_interval,timeout=90)
    out=ROOT/args.out
    if out.exists(): raise SystemExit('Preserve existing probe.')
    report={'method':'Saved real extraction, NEW real audit calls. Not a full pipeline rerun.',
            'input_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'sha256':fingerprint(ROOT/'datasets/meeting_eval_v1.json'),
            'source':str(path.relative_to(ROOT)),'model':client.model,
            'call_interval_s':args.call_interval,
            'generation_settings':{'temperature':client.temperature,'reasoning_effort':client.reasoning_effort,
                                   'audit_max_completion_tokens':1024},'cases':[]}
    for cid in args.ids:
        if fingerprint(ROOT/'datasets/meeting_eval_v1.json') != report['sha256']:
            raise SystemExit('Frozen code/dataset changed; stopping.')
        client.responses=[]
        original=next(c for c in run['cases'] if c['id']==cid)
        response=original['llm_responses'][0]['response']
        class SavedClient:
            def completion_json(self,*args): return response
        notes=[]
        lines=parse_transcript(cases[cid]['transcript'])
        events=extract_events(lines,SavedClient(),warnings=notes)
        records=verify_records(resolve_events(events,lines),lines)
        print(cid+': AUDITING',flush=True)
        try:
            findings,skipped=audit_events(lines,events,records,client)
            notes.extend(skipped)
            apply_audit_findings(records,findings)
            row={'id':cid,'result':'COMPLETED','findings':[f.model_dump() for f in findings],
                 'records':[r.model_dump() for r in records],'notes':notes}
        except Exception as exc:
            row={'id':cid,'result':'ERROR','error':str(exc)}
        row['llm_responses']=client.responses
        report['cases'].append(row)
        report.update(api_calls=client.call_count,api_tokens=client.token_usage)
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(cid+': '+row['result']+' findings='+str(len(row.get('findings',[]))),flush=True)


if __name__=='__main__': main()

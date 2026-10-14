"""Replay every saved H03 variant; do not choose only successful generations."""
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from meeting_intelligence.extractor import extract_events
from meeting_intelligence.parser import parse_transcript
from meeting_intelligence.resolver import resolve_events
from meeting_intelligence.verifier import verify_records
from meeting_intelligence.auditor import AuditFinding, apply_audit_findings
from meeting_intelligence.llm_client import LLMError


def main():
    data=json.loads((ROOT/'datasets/meeting_eval_v1.json').read_text(encoding='utf-8'))
    text=next(c['transcript'] for c in data['cases'] if c['id']=='H03')
    paths=['docs/evaluation/dataset_v1_run.json','results/dataset_core_round2.json',
           'results/dataset_core_round2_promptcheck.json','results/dataset_h03_reasoning_probe.json',
           'results/dataset_h03_source_fallback_check.json',
           'results/dataset_core_round2_final.json']
    rows=[]
    for name in paths:
        path=ROOT/name
        if not path.exists():
            path=ROOT/'docs/evaluation'/Path(name).name
        run=json.loads(path.read_text(encoding='utf-8'))
        case=next(c for c in run['cases'] if c['id']=='H03')
        raw=case['llm_responses'][0].get('response')
        if raw is None:
            rows.append({'artifact':name,'result':'NO_EXTRACTION_RESPONSE'})
            continue
        class SavedClient:
            def completion_json(self,*args):
                return raw
        notes=[]
        lines=parse_transcript(text)
        try:
            records=verify_records(resolve_events(extract_events(lines,SavedClient(),warnings=notes),lines),lines)
        except LLMError as exc:
            rows.append({'artifact':str(path.relative_to(ROOT)),
                         'artifact_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                         'result':'REJECTED_EXTRACTION','error':str(exc),
                         'all_checks_pass':False,'notes':notes})
            continue
        findings=[AuditFinding.model_validate(f) for f in case.get('output',{}).get('audit_findings',[])]
        apply_audit_findings(records,findings)
        request=next((r for r in records if r.kind=='request'),None)
        decisions=[r for r in records if r.kind=='decision']
        checks={'request_present':request is not None,
                'relative_bound_preserved':request is not None and request.due_raw=='trước lần thử tiếp theo',
                'date_not_chosen':any(r.meeting_status=='open' and 'chưa chọn' in (r.content or '').casefold() for r in decisions),
                'no_invented_assignment':not any(r.kind=='action' and r.meeting_status=='assigned' for r in records),
                'no_invented_owner':all(r.owner is None for r in records)}
        rows.append({'artifact':str(path.relative_to(ROOT)),'artifact_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                     'checks':checks,'all_checks_pass':all(checks.values()),
                     'audit_replayed':case.get('audit_completed',False),
                     'records':[r.model_dump() for r in records],'notes':notes})
    result={'method':'Software replay of saved REAL extraction and accepted findings. NO new LLM/audit calls. Not a new accuracy estimate.',
            'case':'H03','cases':rows,'passed_checks':sum(r.get('all_checks_pass',False) for r in rows),
            'code_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'meeting_intelligence').glob('*.py')}}
    (ROOT/'results/source_recovery_replay.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Saved-output variants passing explicit checks:',result['passed_checks'],'/',len(rows))
    for r in rows: print(r['artifact'],r.get('checks',r.get('result')))


if __name__=='__main__': main()

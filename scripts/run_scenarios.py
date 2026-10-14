"""Execute scenarios and report actual results, no fabricated pass statuses.

Usage:
  python scripts/run_scenarios.py --engine offline_rules --ids T02 T03 T04
  python scripts/run_scenarios.py --engine llm_api --ids T01 T02 T03 T04 T05 T06 T07
"""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from meeting_intelligence.pipeline import analyze


def evaluate(result, expected):
    """Match expected records one-to-one; surplus records are errors by default.

    This checks annotated fields, not unrestricted semantic equivalence.
    Maximum matching prevents a broad expectation stealing the only record
    that satisfies a more specific expectation.
    """
    feedback = []
    records = result.records
    targets = expected['expectations']

    def mismatch(r, target):
        errors = []
        if not r.content or not r.content.strip():
            errors.append('bản ghi thiếu nội dung')
        for attr, key in [('meeting_status', 'status'), ('execution_status', 'execution_status'),
                          ('owner', 'owner'), ('supporter', 'supporter'), ('due_raw', 'due_raw'),
                          ('condition', 'condition'), ('issue_key', 'issue_key')]:
            if key in target and getattr(r, attr) != target[key]:
                errors.append(f'{key}={getattr(r, attr)!r}, cần {target[key]!r}')
        if target.get('content_contains') and target['content_contains'].casefold() not in (r.content or '').casefold():
            errors.append('thiếu nội dung ' + target['content_contains'])
        if any(s.casefold() in (r.content or '').casefold() for s in target.get('must_not_final_contain', [])):
            errors.append('còn giữ phương án bị thay thế')
        for field, key, label in [('evidence_ids', 'must_cite', 'source'),
                                  ('counter_evidence_ids', 'counter_cite', 'phản chứng')]:
            for evid in target.get(key, []):
                if evid not in getattr(r, field):
                    errors.append(f'thiếu {label} {evid}')
        return errors

    exact = {i: [j for j, record in enumerate(records)
                 if record.kind == target['kind'] and not mismatch(record, target)]
             for i, target in enumerate(targets)}
    matched = {}  # actual record index -> expectation index

    def assign(i, seen):
        for j in exact[i]:
            if j in seen:
                continue
            seen.add(j)
            if j not in matched or assign(matched[j], seen):
                matched[j] = i
                return True
        return False

    for i in range(len(targets)):
        assign(i, set())
    satisfied = set(matched.values())
    used = set(matched)
    for i, target in enumerate(targets):
        if i in satisfied:
            continue
        options = [j for j, record in enumerate(records)
                   if j not in used and record.kind == target['kind']]
        if not options:
            feedback.append(f"THIẾU bản ghi riêng cho kỳ vọng {i + 1}, loại {target['kind']}")
            continue
        best = min(options, key=lambda j: len(mismatch(records[j], target)))
        used.add(best)
        feedback.extend([target['kind'] + ': ' + error for error in mismatch(records[best], target)])
    if not expected.get('allow_extra_records', False):
        for j, record in enumerate(records):
            if j not in used:
                feedback.append(f'DƯ bản ghi ngoài đáp án: {record.kind}/{record.issue_key}')
    return feedback


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--engine',choices=['llm_api','offline_rules'],default='offline_rules')
    parser.add_argument('--ids',nargs='+',default=['T02','T03','T04'])
    parser.add_argument('--out',default=None)
    parser.add_argument('--call-interval', type=float, default=0,
                        help='Minimum seconds between API attempts (e.g. 45 for free-tier token limits)')
    parser.add_argument('--audit', choices=['on','off'], default='on',
                        help='Only relevant for llm_api: second-pass independent LLM audit')
    args=parser.parse_args()
    if args.call_interval < 0:
        parser.error('--call-interval must be nonnegative')
    reports=[]
    last_call_at=0.0
    created_utc=datetime.now(timezone.utc).isoformat()
    from meeting_intelligence.extractor import SYSTEM_PROMPT
    from meeting_intelligence.auditor import AUDIT_SYSTEM_PROMPT
    prompt_hashes={name:hashlib.sha256(value.encode('utf-8')).hexdigest()
                   for name,value in [('extraction',SYSTEM_PROMPT),('audit',AUDIT_SYSTEM_PROMPT)]}

    def save_report():
        totals={name:sum(1 for x in reports if x['result']==name) for name in ['PASS','FAIL','ERROR']}
        report={'engine':args.engine,'audit':args.audit if args.engine=='llm_api' else 'not_applicable',
                'created_utc':created_utc, 'requested_cases':args.ids,
                'call_interval_s':args.call_interval, 'prompt_sha256':prompt_hashes,
                'complete':len(reports)==len(args.ids), 'summary':totals,'cases':reports,
                'disclaimer':('OFFLINE RULES = narrow rule-based baseline, not real LLM performance' if args.engine=='offline_rules' else 'Actual LLM API outputs on development cases; not held-out accuracy')}
        if args.out:
            p=Path(args.out);p.parent.mkdir(parents=True,exist_ok=True)
            p.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        return totals

    for key in args.ids:
        started=time.perf_counter()
        client=None
        print(f'{key}: RUNNING', flush=True)
        try:
            sample=(ROOT/'samples'/f'{key}.txt').read_text(encoding='utf-8')
            expect=json.loads((ROOT/'samples'/'expected'/f'{key}.json').read_text(encoding='utf-8'))
            if args.engine=='llm_api':
                from meeting_intelligence.llm_client import LLMClient
                class RecordingClient(LLMClient):
                    def __init__(self, **kwargs):
                        super().__init__(**kwargs)
                        self.responses=[]
                    def completion_json(self, system, user, **kwargs):
                        response=super().completion_json(system,user,**kwargs)
                        self.responses.append(response)
                        return response
                client=RecordingClient(min_call_interval=args.call_interval)
                client.last_call_at=last_call_at
                result=analyze(sample, engine='llm_api', client=client, audit=args.audit=='on')
                calls=client.call_count
                tokens=client.token_usage
            else:
                result=analyze(sample, engine=args.engine)
                calls=0; tokens={}
            errors=evaluate(result,expect)
            row={'case':key,'category':expect['category'],'engine':args.engine,
                 'result':'PASS' if not errors else 'FAIL','errors':errors,
                 'records':len(result.records),'api_calls':calls,'api_tokens':tokens,
                 'audit_findings':len(result.audit_findings),
                 'audit_details':result.audit_findings,'notes':result.warnings,
                 'duration_s':round(time.perf_counter()-started,2),
                 'observed_records':[dict(r.model_dump(), status=r.meeting_status)
                                     for r in result.records]}
        except Exception as exc:
            row={'case':key,'result':'ERROR','engine':args.engine,'errors':[str(exc)],
                 'duration_s':round(time.perf_counter()-started,2)}
        row['model']=client.model if client else None
        if client:
            last_call_at=client.last_call_at
            row['api_calls']=client.call_count
            row['api_tokens']=client.token_usage
            row['llm_responses']=client.responses
        reports.append(row)
        save_report()
        print(f"{row['case']}: {row['result']}", flush=True)
        for err in row['errors']: print('  -',err, flush=True)
    totals=save_report()
    print('SUMMARY',totals)
    if totals['FAIL']+totals['ERROR']:
        sys.exit(1)

if __name__=='__main__':main()

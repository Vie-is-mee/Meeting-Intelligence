"""Reproduce extraction errors without saving credentials or rejected generations."""
import hashlib
import json
import re
import sys
import urllib.error
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from meeting_intelligence.extractor import extract_events, SYSTEM_PROMPT
from meeting_intelligence.llm_client import LLMClient
from meeting_intelligence.parser import parse_transcript


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--out', default='results/api_diagnosis_before.json')
    p.add_argument('--ids', nargs='+', default=['D09','D15','D16','H08'])
    a = p.parse_args()
    client = LLMClient(min_call_interval=45, timeout=90)
    dataset = json.loads((ROOT/'datasets/meeting_eval_v1.json').read_text(encoding='utf-8'))
    report = {'model':client.model, 'prompt_sha256':hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest(),
              'purpose':'Separate diagnostic rerun, does not replace baseline outcomes.', 'cases':[]}
    out = ROOT/a.out
    if out.exists():
        raise SystemExit('Use a new output path; preserve prior diagnosis.')
    for case in dataset['cases']:
        if case['id'] not in a.ids: continue
        print(case['id']+': RUNNING',flush=True)
        row = {'id':case['id']}
        try:
            events = extract_events(parse_transcript(case['transcript']),client)
            row.update(result='COMPLETED',event_count=len(events))
        except Exception as exc:
            row.update(result='ERROR',error=str(exc))
            if getattr(exc,'provider_code',None):
                row['provider_code']=exc.provider_code
            cause = exc.__cause__
            if isinstance(cause,urllib.error.HTTPError):
                row['http_status'] = cause.code
                try:
                    body = json.loads(cause.read(64000))
                    error = body.get('error',{})
                    for key in ('code','type','message'):
                        value = str(error.get(key,''))
                        value = value.replace(client.api_key,'[REDACTED]')
                        value = re.sub(r'gsk_[A-Za-z0-9]+','[REDACTED]',value)
                        row['provider_'+key] = value[:500]
                    generation = error.get('failed_generation')
                    if isinstance(generation,str):
                        row['rejected_generation_length'] = len(generation)
                        try:
                            decoded = json.loads(generation)
                            row['rejected_generation_json_valid'] = True
                            row['rejected_generation_root'] = type(decoded).__name__
                        except json.JSONDecodeError as invalid:
                            row.update(rejected_generation_json_valid=False,
                                       json_error=invalid.msg,json_error_position=invalid.pos)
                except (ValueError,AttributeError):
                    row['provider_body_parseable'] = False
        report['cases'].append(row)
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(row,ensure_ascii=False),flush=True)
        if row.get('error') and 'kết nối' in row['error']:
            break


if __name__=='__main__': main()

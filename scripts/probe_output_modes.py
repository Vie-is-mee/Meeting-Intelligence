"""Compare explicit output settings on one synthetic transcript; preserve all attempts."""
import argparse
import hashlib
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from meeting_intelligence.llm_client import LLMClient
from meeting_intelligence.extractor import extract_events, SYSTEM_PROMPT
from meeting_intelligence.parser import parse_transcript


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--id',default='D15')
    p.add_argument('--out',default='results/output_mode_probe.json')
    p.add_argument('--modes',nargs='+',choices=['strict','json','text'],default=['strict','json','text'])
    p.add_argument('--budget',type=int,default=8192)
    p.add_argument('--temperature',type=float,default=0)
    p.add_argument('--reasoning-effort',choices=['low','medium','high'])
    a=p.parse_args()
    out=ROOT/a.out
    if out.exists(): raise SystemExit('Preserve prior probes: choose a new --out.')
    dataset=json.loads((ROOT/'datasets/meeting_eval_v1.json').read_text(encoding='utf-8'))
    case=next(c for c in dataset['cases'] if c['id']==a.id)
    report={'case':a.id,'max_completion_tokens':a.budget,'temperature':a.temperature,'reasoning_effort':a.reasoning_effort,
            'prompt_sha256':hashlib.sha256(SYSTEM_PROMPT.encode()).hexdigest(),'attempts':[]}
    last=0
    for mode in a.modes:
        client=LLMClient(json_mode=mode!='text',structured_mode='strict' if mode=='strict' else 'off',
                         max_completion_tokens=a.budget,temperature=a.temperature,reasoning_effort=a.reasoning_effort,
                         min_call_interval=45,timeout=90)
        client.last_call_at=last
        print(mode+': RUNNING',flush=True)
        row={'mode':mode}
        try:
            events=extract_events(parse_transcript(case['transcript']),client)
            row.update(result='COMPLETED',events=[e.model_dump() for e in events])
        except Exception as exc:
            row.update(result='ERROR',error=str(exc))
        last=client.last_call_at
        row.update(api_calls=client.call_count,api_tokens=client.token_usage)
        report['attempts'].append(row)
        out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print(mode+': '+row['result']+' '+row.get('error',''),flush=True)


if __name__=='__main__': main()

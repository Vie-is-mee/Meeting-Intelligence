"""Prepare a frozen regression input from existing labels; optionally collect API outputs."""
import argparse
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SELECTION=[('datasets/meeting_eval_v1.json','H03'),
           ('datasets/task_lifecycle_regression_v1.json','LC03'),
           ('datasets/meeting_eval_v1.json','D01'),
           ('datasets/meeting_eval_v1.json','D03'),
           ('datasets/meeting_eval_v1.json','D04'),
           ('datasets/meeting_eval_v1.json','H01'),
           ('datasets/task_lifecycle_regression_v1.json','LC01'),
           ('datasets/task_lifecycle_regression_v1.json','LC02')]


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',default='results/final_regression_input_v2.json')
    parser.add_argument('--out',default='results/final_regression_round5_v2.json')
    parser.add_argument('--run',action='store_true',help='Call API using the existing frozen runner; default only prepares files.')
    args=parser.parse_args()
    sources={name:ROOT/name for name,_ in SELECTION}
    data={name:json.loads(path.read_text(encoding='utf-8')) for name,path in sources.items()}
    cases=[]
    for name,cid in SELECTION:
        case=copy.deepcopy(next(c for c in data[name]['cases'] if c['id']==cid))
        case['source_dataset']=name
        cases.append(case)
    core={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
          for p in sorted((ROOT/'meeting_intelligence').glob('*.py'))}
    snapshot={'version':'final-regression-1',
              'purpose':'Fixed development regression, NOT independent held-out evaluation. Same labels/transcripts as source datasets; gold never sent to model.',
              'source_sha256':{name:hashlib.sha256(path.read_bytes()).hexdigest() for name,path in sources.items()},
              'core_sha256':core,'cases':cases}
    path=ROOT/args.input
    if path.exists():
        if json.loads(path.read_text(encoding='utf-8'))!=snapshot:
            raise SystemExit('Frozen input/core changed; choose NEW --input and --out paths.')
    else:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    command=[sys.executable,'-X','utf8',str(ROOT/'scripts/run_dataset.py'),
             '--dataset',args.input,'--out',args.out,'--call-interval','90',
             '--stop-on-rate-limit','--max-retries','0']
    print('Prepared:',args.input,flush=True)
    print('Fixed cases:',', '.join(c['id'] for c in cases),flush=True)
    print('No prompt/model change. API calls only with --run.',flush=True)
    if args.run:
        completed=subprocess.run(command,cwd=ROOT)
        raise SystemExit(completed.returncode)


if __name__=='__main__': main()

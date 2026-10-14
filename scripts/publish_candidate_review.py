"""Seal raw candidate outputs plus complete, explicit semantic review; no API."""
import argparse,hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--version',required=True);p.add_argument('--run',required=True);p.add_argument('--input',required=True)
    p.add_argument('--draft',required=True);p.add_argument('--code-commit',required=True)
    p.add_argument('--scope',choices=['full_regression','targeted_pilot'],default='full_regression')
    args=p.parse_args();version=args.version
    if version not in {'B1','B2','C1','C2'}:p.error('Use B1/B2/C1/C2')
    run_path=ROOT/args.run;input_path=ROOT/args.input;draft_path=ROOT/args.draft
    run=json.loads(run_path.read_text(encoding='utf8'));inputs=json.loads(input_path.read_text(encoding='utf8'));draft=json.loads(draft_path.read_text(encoding='utf8'))
    expected=run['requested_cases'];rows=draft['cases']
    if len(rows)!=len(expected) or {r['id'] for r in rows}!=set(expected):raise SystemExit('Review all requested cases, including missing/error cases, exactly once')
    if len({r['id'] for r in rows})!=len(rows):raise SystemExit('Duplicate reviews')
    outputs={r['id']:r for r in run['cases']}
    for row in rows:
        actual=outputs.get(row['id'])
        if row['verdict'] not in {'PASS','FAIL','ERROR','NOT_RUN'} or row['core_data'] not in {'PASS','FAIL','NOT_EVALUATED'}:raise SystemExit('Invalid review verdict')
        if not all(row.get(k) for k in ['expectation','observed','lesson','audit']):raise SystemExit('Explicit explanation required')
        complete=actual and actual['result']=='COMPLETED' and actual.get('audit_completed')
        if row['verdict']=='PASS' and not complete:raise SystemExit('Cannot pass an incomplete case')
        if (not actual or actual['result']=='ERROR') and row['core_data']!='NOT_EVALUATED':raise SystemExit('Do not fabricate semantic score for errored/not-run outputs')
    for name,digest in run['sha256'].items():
        normalized=name.replace('\\','/')
        if normalized.startswith('meeting_intelligence/'):
            content=subprocess.check_output(['git','show',args.code_commit+':'+normalized],cwd=ROOT)
            if hashlib.sha256(content).hexdigest()!=digest:raise SystemExit('Code commit differs from frozen run: '+normalized)
        elif hashlib.sha256(input_path.read_bytes()).hexdigest()!=digest:raise SystemExit('Input hash mismatch')
    out_dir=ROOT/'docs/evaluation';stem='candidate_'+version.lower()+('_pilot_v1' if args.scope=='targeted_pilot' else '_regression_v1')
    targets=[out_dir/(stem+'.json'),out_dir/(stem+'_input.json'),out_dir/(stem+'_review.json')]
    if any(p.exists() for p in targets):raise SystemExit('Preserve published evidence; use a new version')
    summary={'requested':len(expected),'attempted':len(run['cases']),
        'pipeline_and_audit_completed':sum(c['result']=='COMPLETED' and c.get('audit_completed',False) for c in run['cases']),
        'strict_case_passed':sum(r['verdict']=='PASS' for r in rows),'core_data_passed':sum(r['core_data']=='PASS' for r in rows),
        'api_attempts':sum(c['api_calls'] for c in run['cases']),
        'provider_reported_tokens':sum(c['api_tokens'].get('total_tokens',0) for c in run['cases'])}
    review={'version':version,'scope':args.scope,'method':'Same-assistant semantic review of a frozen development regression, not independent generalization. Include all failures and incomplete calls.',
        'source_code_commit':args.code_commit,'run':targets[0].relative_to(ROOT).as_posix(),
        'run_sha256':hashlib.sha256(run_path.read_bytes()).hexdigest(),
        'input_sha256':hashlib.sha256(input_path.read_bytes()).hexdigest(),'results':summary,'cases':rows}
    targets[0].write_bytes(run_path.read_bytes());targets[1].write_bytes(input_path.read_bytes())
    targets[2].write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(version,summary,'Sealed raw output + input + review. No API calls.')

if __name__=='__main__':main()

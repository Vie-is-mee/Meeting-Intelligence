"""Freeze/verify baseline A from existing evidence; never call an API or read .env."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'docs/evaluation/baseline_a_20261014.json'
RUN = 'docs/evaluation/final_regression_round5_retry2.json'
REVIEW = 'docs/evaluation/final_regression_round5_review.json'
INPUT = 'docs/evaluation/final_regression_input_v2.json'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify_manifest(manifest, root=ROOT):
    errors=[]
    for name, expected in manifest['files_sha256'].items():
        path=(root/name).resolve()
        if not path.is_relative_to(root.resolve()):
            raise ValueError('Manifest path escapes project: '+name)
        if not path.is_file() or sha(path)!=expected:
            errors.append(name)
    return errors

def create_manifest():
    if MANIFEST.exists():
        raise ValueError('Baseline already exists; use --verify. Never overwrite baseline A.')
    run=json.loads((ROOT/RUN).read_text(encoding='utf8'))
    review=json.loads((ROOT/REVIEW).read_text(encoding='utf8'))
    inputs=json.loads((ROOT/INPUT).read_text(encoding='utf8'))
    if review['run_sha256']!=sha(ROOT/RUN):
        raise ValueError('Review does not match raw API evidence')
    for name, digest in run['sha256'].items():
        normalized=name.replace('\\','/')
        normalized=INPUT if normalized.startswith('results/') else normalized
        if sha(ROOT/normalized)!=digest:
            raise ValueError('Current core/input differs from recorded run: '+normalized)
    for name,digest in inputs['source_sha256'].items():
        if sha(ROOT/name)!=digest:
            raise ValueError('Historical dataset was modified: '+name)
    if not run['complete'] or len(run['cases'])!=8 or any(c['result']!='COMPLETED' or not c['audit_completed'] for c in run['cases']):
        raise ValueError('Baseline run is incomplete')
    stats=review['results']
    if (sum(c['verdict']=='PASS' for c in review['cases']),sum(c['core_data']=='PASS' for c in review['cases']))!=(stats['strict_case_passed'],stats['core_data_passed']):
        raise ValueError('Summary disagrees with case reviews')
    files=[*sorted((ROOT/'meeting_intelligence').glob('*.py')),*[ROOT/p for p in [RUN,REVIEW,INPUT,'docs/FINAL_REGRESSION_RESULTS.md','datasets/meeting_eval_v1.json','datasets/task_lifecycle_regression_v1.json','frontend/demo-data.json','requirements.txt']]]
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    manifest={'baseline_id':'baseline-A-20261014','created_local_date':'2026-10-14',
        'source_commit':commit,'git_tag':'baseline-a-20261014',
        'scope':'Core/prompt and historical evidence are frozen; website and deployment may evolve separately.',
        'evaluation_type':'Development regression; synthetic same-author labels and assistant semantic review, not independent.',
        'historical_run':RUN,'historical_review':REVIEW,'regression_input':INPUT,
        'model':run['model'],'structured_outputs':run['structured_outputs'],'generation_settings':run['generation_settings'],
        'call_interval_s':run['call_interval_s'],'max_retries':run['max_retries'],
        'requested_cases':run['requested_cases'],'observed_results':stats,
        'claims_not_established':['Current-version precision/recall over all 24 cases','Independent generalization','Stability across repeated generations','Production readiness'],
        'baseline_files_policy':'Keep these bytes unchanged. Candidate B must have its own commit/artifacts; use the baseline tag to inspect A.',
        'files_sha256':{p.relative_to(ROOT).as_posix():sha(p) for p in files}}
    MANIFEST.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    return manifest

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--create',action='store_true')
    parser.add_argument('--verify',action='store_true')
    args=parser.parse_args()
    if args.create==args.verify:parser.error('Choose exactly one of --create / --verify')
    try:
        manifest=create_manifest() if args.create else json.loads(MANIFEST.read_text(encoding='utf8'))
        errors=verify_manifest(manifest)
        if errors:raise ValueError('Changed baseline files: '+', '.join(errors))
        print(f"Baseline A verified: {len(manifest['files_sha256'])} files; 8/8 completed, 4/8 strict, 5/8 core. No API calls.")
    except (ValueError,OSError) as exc:parser.exit(1,str(exc)+'\n')

if __name__=='__main__':main()

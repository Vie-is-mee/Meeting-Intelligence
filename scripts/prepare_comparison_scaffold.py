"""Prepare honest dataset-use registry and an EMPTY candidate-B comparison once."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'docs/evaluation'
    registry_path=out/'evaluation_split_registry_20261014.json'
    comparison_path=out/'comparison_a_b_20261014.json'
    if registry_path.exists() or comparison_path.exists():raise SystemExit('Registry/comparison already exists; do not overwrite tracked evaluation work.')
    baseline=json.loads((out/'baseline_a_20261014.json').read_text(encoding='utf8'))
    review=json.loads((out/'final_regression_round5_review.json').read_text(encoding='utf8'))
    old=json.loads((ROOT/'datasets/meeting_eval_v1.json').read_text(encoding='utf8'))
    lifecycle=json.loads((ROOT/'datasets/task_lifecycle_regression_v1.json').read_text(encoding='utf8'))
    pool=json.loads((ROOT/'datasets/prospective_eval_v2.json').read_text(encoding='utf8'))
    registry={'updated_local_date':'2026-10-14','scope':'Current dataset-use status; historical dataset metadata is not rewritten.',
        'groups':[
            {'source':'datasets/meeting_eval_v1.json','case_ids':[c['id'] for c in old['cases']],'current_role':'development_or_regression','independence_claim':False,'reason':'Original 24-case run has already been seen; reserved/H cases have participated in the development/evaluation history. Do not claim untouched held-out results.'},
            {'source':'datasets/task_lifecycle_regression_v1.json','case_ids':[c['id'] for c in lifecycle['cases']],'current_role':'development_or_regression','independence_claim':False,'reason':'Lifecycle examples used to inspect/repair behavior.'},
            {'source':'datasets/prospective_eval_v2.json','case_ids':[c['id'] for c in pool['cases']],'current_role':'prospective_synthetic_pending_human_labels','independence_claim':False,'outputs_observed':False,'used_to_tune_core':False,'reason':'New synthetic cases, same implementation author, no gold or outputs yet. Human annotation remains pending.'}],
        'independent_real_world_benchmark':{'status':'not_available','case_ids':[]},
        'policy':'Record any prospective case used to tune as development before measuring a revised candidate. Never silently relabel it as unseen.',
        'exposure_log':[]}
    comparison={'baseline_id':baseline['baseline_id'],'baseline_source_commit':baseline['source_commit'],'baseline_manifest':'docs/evaluation/baseline_a_20261014.json',
        'baseline_summary':baseline['observed_results'],
        'candidate_b':{'status':'not_created_or_evaluated','source_commit':None,'model_config':None,'run_artifact':None,'review_artifact':None,'summary':None},
        'regression_cases':[{'id':c['id'],'baseline_strict':c['verdict'],'baseline_core':c['core_data'],'baseline_audit':c['audit'],'baseline_observation':c['observed'],'candidate_b_strict':None,'candidate_b_core':None,'candidate_b_audit':None,'comparison_reason':None} for c in review['cases']],
        'prospective_evaluation':{'status':'pending_human_labels','case_ids':[c['id'] for c in pool['cases']],'run_artifacts':[],'scores':None,'independence_claim':False},
        'acceptance_policy':['Repair target errors without changing gold to fit outputs','Check preservation of known successful regression behavior','Separate audit usefulness from extraction correctness','Preserve errors, incomplete runs and all repeated outputs','Do not claim dataset-wide precision/recall from an eight-case regression'],
        'changes':[]}
    for path,value in [(registry_path,registry),(comparison_path,comparison)]:path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print('Prepared exposure registry and A/B comparison with candidate B scores left null. No API calls.')

if __name__=='__main__':main()

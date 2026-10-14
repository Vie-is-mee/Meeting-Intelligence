"""Package the frozen REAL regression for static playback. Never reruns or edits predictions."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main():
    source=ROOT/'docs/evaluation/final_regression_round5_retry2.json'
    review_path=ROOT/'docs/evaluation/final_regression_round5_review.json'
    source_bytes=source.read_bytes()
    digest=hashlib.sha256(source_bytes).hexdigest()
    run=json.loads(source_bytes)
    review=json.loads(review_path.read_text(encoding='utf-8'))
    assert review['run_sha256']==digest, 'Review does not match the saved run'
    assert run['complete'] and len(run['cases'])==8
    labels={c['id']:c for c in review['cases']}
    inputs=json.loads((ROOT/'docs/evaluation/final_regression_input_v2.json').read_text(encoding='utf-8'))
    by_id={c['id']:c for c in inputs['cases']}
    demos=[]
    for cid in ['D01','D03','D04','H01','LC03','LC01','H03','LC02']:
        case=next(c for c in run['cases'] if c['id']==cid)
        assert case['audit_completed'] and case['result']=='COMPLETED'
        demos.append({'id':cid,'description':by_id[cid]['title'],'transcript':by_id[cid]['transcript'],
                      'review':labels[cid],
                      'result':{'analysis':case['output'],'duration_s':case['duration_s'],
                                'api_calls':0,'token_usage':{},'model':run['model'],
                                'audit_enabled':True,'evaluation':None,'source_mode':'recorded',
                                'provenance':{'case':cid,'created_utc':run['created_utc'],
                                              'run_sha256':digest,'historical_api_calls':case['api_calls'],
                                              'historical_token_usage':case['api_tokens'],
                                              'generation_settings':run['generation_settings']},
                                'review':labels[cid]}})
    payload={'version':1,'mode':'recorded','label':'Kết quả LLM thật đã lưu; không phải phân tích mới.',
             'run_sha256':digest,'model':run['model'],'created_utc':run['created_utc'],
             'summary':review['results'],'cases':demos}
    encoded=json.dumps(payload,ensure_ascii=False,indent=2)+'\n'
    assert 'gsk_' not in encoded and 'Authorization' not in encoded
    (ROOT/'frontend/demo-data.json').write_text(encoded,encoding='utf-8')
    target=ROOT/'samples/demo'
    target.mkdir(parents=True,exist_ok=True)
    for case in demos: (target/(case['id']+'.txt')).write_text(case['transcript']+'\n',encoding='utf-8')
    print('Built 8 recorded cases and .txt inputs. Predictions preserved exactly; playback uses 0 API calls.')


if __name__=='__main__': main()

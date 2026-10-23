"""Verify an actual PUBLIC M3 staging origin before accepting it as demo.

Default: safe GET-only checks; --live calls Groq once on a synthetic C2 sample.
Refuses running live if branch/source fingerprint is missing or mismatched.
Never prints credentials or transcripts; JSON report only when --out specified.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import URLError, HTTPError
import hashlib

ROOT=Path(__file__).resolve().parents[1]

def request_json(base,path,post=None,timeout=90):
    data=None if post is None else json.dumps(post,ensure_ascii=False).encode('utf-8')
    req=Request(base+path,data=data,headers={'Content-Type':'application/json'} if data else {})
    with urlopen(req,timeout=timeout) as res:
        if res.status!=200:raise RuntimeError(f'{path}: HTTP {res.status}')
        return json.load(res)

def verify(base,require_sha,live):
    base=base.strip().rstrip('/')
    if not base.startswith('https://'):raise ValueError('Public staging requires HTTPS')
    check={}
    config=request_json(base,'/api/version',timeout=40)
    check['mission3']=config.get('mission')=='M3' and config.get('change_request')=='C2'
    sha=config.get('source_commit','')
    check['git_sha_matches']=sha==require_sha
    for name in ('meeting_intelligence/pipeline.py','meeting_intelligence/ambiguity.py',
                 'meeting_intelligence/verifier.py','meeting_intelligence/resolver.py'):
        expected=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
        check['module_'+name]=config.get('core_sha256',{}).get(name)==expected
    if not all(check.values()):
        raise RuntimeError('Staging source fingerprint mismatch (not M3 release candidate): '+json.dumps(check))
    with urlopen(base+'/',timeout=40) as res:
        page=res.read(350000).decode('utf-8','replace')
    check['frontend_c2']=('id="load-c2"' in page and 'Mission 3' in page)
    config_api=request_json(base,'/api/config',timeout=35)
    check['groq_configured']=bool(config_api.get('api_configured'))
    if live:
        if not check['frontend_c2'] or not check['groq_configured']:
            raise RuntimeError('M3 UI or server Groq settings missing; refuse live test')
        case=request_json(base,'/api/analyze',{'engine':'llm_api','audit':False,
                          'transcript':'Minh: Cái này team mình xử lý nhé.'},timeout=150)
        rows=[r for r in case['analysis']['records'] if r.get('kind')=='action']
        check['c2_http_live']=bool(rows and any(
            r.get('owner') is None and r.get('due_raw') is None and
            r.get('meeting_status')=='unverified' and r.get('review_status')=='needs_review'
            and 'L001' in r.get('evidence_ids',[]) for r in rows))
        if not check['c2_http_live']:raise RuntimeError('Live C2 output violates CR; do not submit')
    return {'base_url':base,'expected_sha':require_sha,'observed_sha':sha,
            'checks':check,'all_checked_pass':all(check.values()),
            'live_provider_called':live,
            'note':'Browser-based human review/export still requires UI smoke; unit tests cover review/CSV.'}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--base-url',required=True)
    p.add_argument('--require-sha',required=True)
    p.add_argument('--live',action='store_true')
    p.add_argument('--out')
    args=p.parse_args()
    report=verify(args.base_url,args.require_sha,args.live)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if args.out:
        out=ROOT/args.out
        if out.exists():raise SystemExit('Refusing to overwrite existing report')
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

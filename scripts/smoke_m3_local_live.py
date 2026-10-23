"""Run C2 over REAL local HTTP server + real Groq without a browser.

No secrets printed; use the project's private .env. Generates non-overwriting
artifacts. Not equivalent to a publicly deployed staging website.
"""
import argparse
import json
import threading
from pathlib import Path
from urllib.request import Request, urlopen
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from web import InspectionServer, release_identity
from meeting_intelligence.config import load_local_config

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--out',required=True)
    args=p.parse_args()
    output=ROOT/args.out
    if output.exists():raise SystemExit("Refusing to overwrite existing evidence")
    load_local_config()
    server=InspectionServer(('127.0.0.1',0),public=False)
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    base=f'http://127.0.0.1:{server.server_port}'
    try:
        version=json.load(urlopen(base+'/api/version',timeout=10))
        transcript='Minh: Cái này team mình xử lý nhé.'
        request=Request(base+'/api/analyze',
                data=json.dumps({'transcript':transcript,'engine':'llm_api','audit':False},
                         ensure_ascii=False).encode('utf-8'),
                headers={'Content-Type':'application/json'},method='POST')
        with urlopen(request,timeout=160) as response:
            result=json.load(response)
        records=[x for x in result['analysis']['records'] if x['kind']=='action']
        matched=[x for x in records if x.get('meeting_status')=='unverified'
                 and x.get('owner') is None and x.get('due_raw') is None
                 and x.get('review_status')=='needs_review'
                 and 'L001' in x.get('evidence_ids',[])]
        success=bool(matched)
        report={'environment':'LOCAL_HTTP_WITH_REAL_GROQ_NOT_PUBLIC_STAGING',
                'api_version':version,'test':'Official CR C2 bare group commitment',
                'source_utterance':transcript,
                'pass':success,'records_count':len(result['analysis']['records']),
                'api_calls':result.get('api_calls'),'token_usage':result.get('token_usage'),
                'analysis':result['analysis']}
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print('C2_LOCAL_HTTP_LIVE', 'PASS' if success else 'FAIL',
              'commit',version['source_commit'][:9],
              'records',len(records),'calls',result.get('api_calls'),
              'tokens',result.get('token_usage',{}).get('total_tokens'),
              'path',args.out)
        if not success:raise SystemExit(2)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=4)

if __name__=='__main__':
    main()

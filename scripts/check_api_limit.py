"""One tiny transport probe; save only allowlisted LLMError diagnostics, never raw provider body."""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from meeting_intelligence.llm_client import LLMClient, LLMError


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',required=True)
    args=parser.parse_args()
    path=ROOT/args.out
    if path.exists(): raise SystemExit('Preserve previous probe; use a new output path.')
    client=LLMClient(max_retries=0,timeout=30)
    result={'method':'Tiny transport-only probe, NOT a transcript evaluation.',
            'created_utc':datetime.now(timezone.utc).isoformat(),'model':client.model}
    try:
        client.completion_json('Return only a JSON object.', 'Return {"ok":true}.',max_completion_tokens=64)
        result['result']='COMPLETED'
    except LLMError as exc:
        result.update(result='ERROR',error=str(exc),status_code=exc.status_code,
                      provider_code=exc.provider_code,diagnostics=exc.diagnostics)
    result.update(api_calls=client.call_count,api_tokens=client.token_usage)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__': main()

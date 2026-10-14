"""Run manually authored event fixtures through the *real resolver & verifier*.

THIS DOES NOT TEST ANY LLM. Output is a software contract test, not model quality.
"""
from __future__ import annotations
import sys
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from meeting_intelligence.pipeline import analyze
from scripts.run_scenarios import evaluate

class FixtureClient:
    def __init__(self,events): self.events=events
    def completion_json(self,system,user):
        return {'findings': []} if 'PHẢN BIỆN' in system else {'events':self.events}

def main():
    results=[]
    for key in ['T01','T02','T03','T04','T05','T06','T07']:
        content=(ROOT/'samples'/f'{key}.txt').read_text(encoding='utf-8')
        expected=json.loads((ROOT/'samples'/'expected'/f'{key}.json').read_text(encoding='utf-8'))
        events=json.loads((ROOT/'tests'/'fixtures'/f'{key}.json').read_text(encoding='utf-8'))['events']
        actual=analyze(content,client=FixtureClient(events))
        errors=evaluate(actual,expected)
        print(f'{key}: {"CONTRACT PASS" if not errors else "CONTRACT FAIL"}',errors)
        results.append({'case':key,'status':'PASS' if not errors else 'FAIL','errors':errors})
    report={'kind':'MOCK_CONTRACT_NOT_LLM_ACCURACY',
            'disclaimer':'Các events thủ công trong tests/fixtures, chưa gọi API mô hình',
            'cases':results}
    path=ROOT/'results'/'contract_fixtures.json'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if any(x['status']=='FAIL' for x in results):raise SystemExit(1)

if __name__=='__main__':main()

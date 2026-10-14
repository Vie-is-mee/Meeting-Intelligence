"""Compare A/C1 on the SAME saved extraction, before audit. No new model calls."""
import argparse,copy,hashlib,importlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from meeting_intelligence import extractor,parser,resolver,verifier

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',default='docs/evaluation/candidate_c1_saved_extraction_replay.json');args=p.parse_args()
    target=ROOT/args.out
    if target.exists():raise SystemExit('Preserve replay: choose a new --out.')
    baseline=json.loads((ROOT/'docs/evaluation/baseline_a_20261014.json').read_text(encoding='utf8'))
    snapshot=ROOT/'tmp/baseline_a_core';snapshot.mkdir(parents=True,exist_ok=True)
    for name,digest in baseline['files_sha256'].items():
        if not name.startswith('meeting_intelligence/'):continue
        raw=subprocess.check_output(['git','show',baseline['source_commit']+':'+name],cwd=ROOT)
        if hashlib.sha256(raw).hexdigest()!=digest:raise SystemExit('Baseline tag bytes do not match manifest: '+name)
        (snapshot/Path(name).name).write_bytes(raw)
    sys.path.insert(0,str(snapshot.parent))
    a={name:importlib.import_module('baseline_a_core.'+name) for name in ['extractor','parser','resolver','verifier']}
    source=ROOT/'docs/evaluation/final_regression_round5_retry2.json'
    run=json.loads(source.read_text(encoding='utf8'));input_data=json.loads((ROOT/'docs/evaluation/final_regression_input_v2.json').read_text(encoding='utf8'))
    inputs={c['id']:c['transcript'] for c in input_data['cases']};rows=[]
    for case in run['cases']:
        response=case['llm_responses'][0]['response']
        class SavedClient:
            def completion_json(self,*args):return copy.deepcopy(response)
        outputs={};warnings={}
        for label,modules in [('A',a),('C1',{'extractor':extractor,'parser':parser,'resolver':resolver,'verifier':verifier})]:
            lines=modules['parser'].parse_transcript(inputs[case['id']]);notes=[]
            events=modules['extractor'].extract_events(lines,SavedClient(),warnings=notes)
            records=modules['verifier'].verify_records(modules['resolver'].resolve_events(events,lines),lines)
            outputs[label]=[r.model_dump() for r in records];warnings[label]=notes
        dimensions=['issue_key','kind','content','meeting_status','execution_status','owner','supporter','due_raw','condition','field_evidence_ids']
        state=lambda label:[{k:r[k] for k in dimensions} for r in outputs[label]]
        checks={}
        if case['id'] in {'D01','D03','D04','H01'}:checks['known_successful_saved_extraction_unchanged']=state('A')==state('C1')
        if case['id']=='LC01':checks['no_duplicate_request']=len(outputs['C1'])==1 and outputs['C1'][0]['kind']=='action' and outputs['C1'][0]['meeting_status']=='cancelled'
        if case['id']=='LC02':checks['no_assignment_as_proposal']=not any(r['kind']=='decision' and r['meeting_status']=='proposed' for r in outputs['C1'])
        rows.append({'id':case['id'],'checks':checks,'A_records':outputs['A'],'C1_records':outputs['C1'],'C1_software_notes':warnings['C1']})
    report={'method':'Same saved provider extraction replayed through baseline A and candidate C1, BEFORE audit. No new extraction/audit calls; not an accuracy estimate.',
        'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'candidate_core_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'meeting_intelligence').glob('*.py'))},'cases':rows}
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    for row in rows:print(row['id'],row['checks'])
    if not all(all(r['checks'].values()) for r in rows):raise SystemExit('Replay regression failed')

if __name__=='__main__':main()

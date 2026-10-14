"""Validate pre-output human annotations and freeze prospective input; no API calls."""
import argparse
import copy
import hashlib
import json
from datetime import datetime
from pathlib import Path
import sys
from typing import get_args

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from meeting_intelligence.parser import parse_transcript
from meeting_intelligence.models import Kind, MeetingStatus, ExecutionStatus

def digest(value):
    return hashlib.sha256(value.encode('utf8')).hexdigest()

def validate_annotations(pool, annotations):
    cases={c['id']:c for c in pool['cases']}
    rows=annotations.get('cases',[])
    if len(cases)!=len(pool['cases']) or len(rows)!=len(cases) or len({r['id'] for r in rows})!=len(rows) or {r['id'] for r in rows}!=set(cases):
        raise ValueError('Case IDs must match the entire pool exactly once')
    frozen=[]
    for row in rows:
        cid=row['id'];case=cases[cid]
        if row.get('transcript_sha256')!=digest(case['transcript']):raise ValueError(cid+': transcript changed after annotation')
        if row.get('annotation_status')!='human_reviewed' or not str(row.get('reviewer') or '').strip() or row.get('labels_finalized_before_outputs') is not True:
            raise ValueError(cid+': human review and pre-output declaration are still pending')
        try:stamp=datetime.fromisoformat(row['reviewed_at'])
        except (TypeError,ValueError,KeyError):raise ValueError(cid+': reviewed_at must be ISO datetime with timezone')
        if stamp.tzinfo is None:raise ValueError(cid+': reviewed_at needs a timezone')
        if type(row.get('case_review_required')) is not bool:raise ValueError(cid+': case_review_required must be boolean')
        required=row.get('required_records')
        if not isinstance(required,list):raise ValueError(cid+': required_records is not annotated; null is NOT an empty gold set')
        if not required and not str(row.get('no_required_records_reason') or '').strip():raise ValueError(cid+': explain a deliberately empty gold set')
        sources={u.id:u.text for u in parse_transcript(case['transcript'])}
        label_ids=set()
        for record in [*required,*row.get('allowed_additional_records',[])]:
            lid=record.get('label_id')
            if not lid or lid in label_ids:raise ValueError(cid+': label IDs must be unique')
            label_ids.add(lid)
            if record.get('kind') not in get_args(Kind) or record.get('meeting_status') not in get_args(MeetingStatus) or record.get('execution_status') not in get_args(ExecutionStatus):raise ValueError(cid+': invalid kind/status')
            allowed={'decision':{'proposed','agreed','conditional','reopened','withdrawn','open','unverified'},'action':{'assigned','cancelled','unverified'},'issue':{'open','reported_resolved','unverified'},'request':{'recorded','withdrawn','unverified'},'feedback':{'recorded','unverified'},'knowledge':{'unverified'}}
            if record['meeting_status'] not in allowed[record['kind']]:raise ValueError(cid+': kind/status pair is inconsistent')
            if not str(record.get('meaning') or '').strip():raise ValueError(cid+': label meaning required')
            for field in ['owner','supporter','due_raw','due_iso','condition']:
                if field not in record or (record[field] is not None and not isinstance(record[field],str)):raise ValueError(cid+': explicit string/null required for '+field)
            if record.get('authority_status')!='unknown':raise ValueError(cid+': transcript cannot establish externally verified authority')
            if type(record.get('must_flag_for_review')) is not bool:raise ValueError(cid+': must_flag_for_review required')
            if not record.get('evidence') or not isinstance(record.get('field_evidence'),dict):raise ValueError(cid+': evidence and field_evidence required')
            evidence=[*record['evidence'],*record.get('counter_evidence',[])]
            for field,quotes in record['field_evidence'].items():
                if field not in {'content','meeting_status','execution_status','owner','supporter','due_raw','due_iso','condition'} or not isinstance(quotes,list):raise ValueError(cid+': invalid field evidence')
                evidence.extend(quotes)
            for quote in evidence:
                if sources.get(quote.get('source_id'))!=quote.get('quote'):raise ValueError(cid+': evidence must quote the exact parser source text')
            for field in ['content','meeting_status']:
                if not record['field_evidence'].get(field):raise ValueError(cid+': field evidence missing: '+field)
            for field in ['owner','supporter','due_raw','due_iso','condition']:
                if record[field] is not None and not record['field_evidence'].get(field):raise ValueError(cid+': non-null field evidence missing: '+field)
            if record['meeting_status']=='conditional' and not record['condition']:raise ValueError(cid+': conditional decision needs a condition')
            if record['execution_status'] in {'blocked','pending_condition'} and not record['field_evidence'].get('execution_status'):raise ValueError(cid+': execution status evidence required')
        item=copy.deepcopy(case)
        item.update({k:copy.deepcopy(row[k]) for k in ['required_records','allowed_additional_records','forbidden_claims','case_review_required']})
        item['annotation_status']='human_reviewed_self_reported'
        item['human_signoff']={k:row[k] for k in ['reviewer','reviewed_at','labels_finalized_before_outputs']}
        item['split']='held_out'  # runner/scorer compatibility; does not imply independent authorship.
        frozen.append(item)
    return frozen

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pool',default='datasets/prospective_eval_v2.json')
    p.add_argument('--annotations',default='datasets/prospective_eval_v2_annotations.json')
    p.add_argument('--out',default='datasets/prospective_eval_v2_frozen.json')
    p.add_argument('--freeze',action='store_true')
    args=p.parse_args()
    try:
        pool_path=ROOT/args.pool;annotations_path=ROOT/args.annotations
        pool=json.loads(pool_path.read_text(encoding='utf8'));annotations=json.loads(annotations_path.read_text(encoding='utf8'))
        cases=validate_annotations(pool,annotations)
        value={'dataset_id':'prospective_eval_vi_v2_frozen','evaluation_gate':'frozen_human_labels',
            'provenance':pool['provenance'],'independence_claim':False,
            'caveat':'Synthetic transcripts seen by implementation author; human signoff is self-reported. This is NOT an independent real-world benchmark.',
            'source_sha256':{args.pool:hashlib.sha256(pool_path.read_bytes()).hexdigest(),args.annotations:hashlib.sha256(annotations_path.read_bytes()).hexdigest()},'cases':cases}
        if args.freeze:
            out=ROOT/args.out
            if out.exists():raise ValueError('Frozen dataset already exists; do not overwrite. Use a new version.')
            out.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
            print('Frozen human-reviewed inputs. No API calls. Independence claim remains false.')
        else:print('Annotations valid; use --freeze to seal before model outputs. No API calls.')
    except (ValueError,OSError,KeyError,TypeError) as exc:p.exit(1,str(exc)+'\n')

if __name__=='__main__':main()

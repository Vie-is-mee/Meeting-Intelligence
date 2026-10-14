"""Meaningful safeguards for baseline immutability and pre-output labels; no API."""
import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts.baseline_checkpoint import verify_manifest, ROOT
from scripts.prepare_prospective_eval import validate_annotations, digest
from meeting_intelligence.parser import parse_transcript

def fixture():
    text='L001 | Lan | Chốt tổ chức buổi hướng dẫn sáng thứ Ba.'
    quote={'source_id':'L001','quote':'Chốt tổ chức buổi hướng dẫn sáng thứ Ba.'}
    pool={'cases':[{'id':'P1','transcript':text}]}
    label={'label_id':'guide','kind':'decision','meaning':'Hướng dẫn sáng thứ Ba','meeting_status':'agreed','execution_status':'unknown','authority_status':'unknown','owner':None,'supporter':None,'due_raw':None,'due_iso':None,'condition':None,'evidence':[quote],'field_evidence':{'content':[quote],'meeting_status':[quote]},'must_flag_for_review':False}
    annotations={'cases':[{'id':'P1','transcript_sha256':digest(text),'reviewer':'Human fixture','reviewed_at':'2026-10-14T20:00:00+07:00','annotation_status':'human_reviewed','labels_finalized_before_outputs':True,'required_records':[label],'allowed_additional_records':[],'forbidden_claims':[],'case_review_required':False}]}
    return pool,annotations

class EvaluationPreparationTests(unittest.TestCase):
    def test_baseline_detects_changed_and_missing_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);p=root/'core.py';p.write_bytes(b'old')
            manifest={'files_sha256':{'core.py':hashlib.sha256(b'old').hexdigest()}}
            self.assertEqual(verify_manifest(manifest,root),[])
            p.write_bytes(b'new');self.assertEqual(verify_manifest(manifest,root),['core.py'])
            p.unlink();self.assertEqual(verify_manifest(manifest,root),['core.py'])

    def test_baseline_rejects_path_outside_project(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):verify_manifest({'files_sha256':{'../outside':'x'}},Path(directory))

    def test_valid_human_labels_keep_original_inputs_and_do_not_claim_authenticated_review(self):
        pool,annotations=fixture();before=copy.deepcopy(annotations)
        output=validate_annotations(pool,annotations)
        self.assertEqual(annotations,before);self.assertEqual(output[0]['annotation_status'],'human_reviewed_self_reported')
        self.assertEqual(output[0]['required_records'][0]['meaning'],'Hướng dẫn sáng thứ Ba')

    def test_unknown_labels_are_not_an_empty_gold_set(self):
        pool,annotations=fixture();row=annotations['cases'][0]
        row['required_records']=None
        with self.assertRaisesRegex(ValueError,'not annotated'):validate_annotations(pool,annotations)
        row['required_records']=[]
        with self.assertRaisesRegex(ValueError,'empty gold'):validate_annotations(pool,annotations)
        row['no_required_records_reason']='Explicit negative-control fixture'
        self.assertEqual(validate_annotations(pool,annotations)[0]['required_records'],[])

    def test_pending_signoff_cannot_freeze(self):
        for field,value in [('reviewer',''),('annotation_status','pending'),('labels_finalized_before_outputs',False)]:
            pool,annotations=fixture();annotations['cases'][0][field]=value
            with self.assertRaisesRegex(ValueError,'pending'):validate_annotations(pool,annotations)

    def test_tampered_transcript_or_quote_is_rejected(self):
        pool,annotations=fixture();pool['cases'][0]['transcript']+=' Thay đổi.'
        with self.assertRaisesRegex(ValueError,'transcript changed'):validate_annotations(pool,annotations)
        pool,annotations=fixture();annotations['cases'][0]['required_records'][0]['evidence'][0]['quote']='Chốt khác'
        with self.assertRaisesRegex(ValueError,'exact parser'):validate_annotations(pool,annotations)

    def test_missing_field_source_or_duplicate_cases_rejected(self):
        pool,annotations=fixture();label=annotations['cases'][0]['required_records'][0]
        label['owner']='Lan'
        with self.assertRaisesRegex(ValueError,'field evidence'):validate_annotations(pool,annotations)
        pool,annotations=fixture();annotations['cases'].append(copy.deepcopy(annotations['cases'][0]))
        with self.assertRaisesRegex(ValueError,'exactly once'):validate_annotations(pool,annotations)

    def test_new_pool_has_no_gold_or_outputs_and_counts_match_parser(self):
        pool=json.loads((ROOT/'datasets/prospective_eval_v2.json').read_text(encoding='utf8'))
        annotations=json.loads((ROOT/'datasets/prospective_eval_v2_annotations.json').read_text(encoding='utf8'))
        self.assertEqual(len(pool['cases']),12);self.assertFalse(pool['llm_execution_performed']);self.assertFalse(pool['independence_claim'])
        for case,row in zip(pool['cases'],annotations['cases']):
            self.assertNotIn('required_records',case);self.assertNotIn('output',case);self.assertIsNone(row['required_records'])
            self.assertEqual(case['utterance_count'],len(parse_transcript(case['transcript'])))
            self.assertEqual(row['transcript_sha256'],digest(case['transcript']))
        self.assertTrue(all(c['utterance_count']>=70 for c in pool['cases'] if c['difficulty']=='hard'))

    def test_runner_blocks_pending_pool_before_client_or_api(self):
        from scripts import run_dataset
        with patch('sys.argv',['run_dataset','--dataset','datasets/prospective_eval_v2.json']),patch.object(run_dataset,'RecordingClient') as client:
            with self.assertRaises(SystemExit) as caught:run_dataset.main()
            self.assertEqual(caught.exception.code,2);client.assert_not_called()

if __name__=='__main__':unittest.main()

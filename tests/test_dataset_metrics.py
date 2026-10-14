import hashlib
import json
import unittest
from scripts.score_dataset import score, FIELDS


class DatasetMetricTests(unittest.TestCase):
    def fixture(self):
        target = dict(label_id='x', kind='decision', **{f: None for f in FIELDS})
        case = dict(id='D', split='development', required_records=[target], representation_alternatives=[])
        output = dict(id='D', result='COMPLETED', audit_completed=True,
                      output={'records': [{'kind': 'decision'}, {'kind': 'issue'}], 'audit_findings': []})
        run = {'cases': [output]}
        review = {'run_sha256': hashlib.sha256(json.dumps(run, sort_keys=True, ensure_ascii=False).encode()).hexdigest(),
                  'cases': [{'id': 'D', 'predictions': [
                      {'index': i, 'supported': True, 'evidence_supported': True, 'reason': 'source reviewed'} for i in range(2)],
                      'matches': [{'label_id': 'x', 'index': 0, 'core_correct': True,
                                   'fields': {f: True for f in FIELDS}, 'reason': 'same meaning'}]}]}
        return {'cases': [case]}, run, review

    def test_grounded_extra_does_not_reduce_precision_or_inflate_recall(self):
        metrics = score(*self.fixture())['metrics']['all']
        self.assertEqual(metrics['supported_record_precision'], {'correct': 2, 'total': 2, 'rate': 1})
        self.assertEqual(metrics['required_record_recall_end_to_end']['total'], 1)
        self.assertIsNone(metrics['nonnull_field_accuracy_on_matched_records']['owner']['rate'])

    def test_reject_reused_prediction(self):
        data, run, review = self.fixture()
        review['cases'][0]['matches'].append(dict(review['cases'][0]['matches'][0]))
        with self.assertRaises(ValueError):
            score(data, run, review)

    def test_pending_review_is_explicit(self):
        data, run, review = self.fixture()
        review['cases'] = []
        metrics = score(data, run, review)['metrics']['all']
        self.assertFalse(metrics['semantic_scoring_complete'])
        self.assertIsNone(metrics['supported_record_precision']['rate'])

    def test_reject_unreviewed_extra(self):
        data, run, review = self.fixture()
        review['cases'][0]['predictions'].pop()
        with self.assertRaises(ValueError):
            score(data, run, review)

    def test_changed_output_invalidates_review(self):
        data, run, review = self.fixture()
        run['cases'][0]['result'] = 'ERROR'
        with self.assertRaises(ValueError):
            score(data, run, review)

    def test_failed_case_counts_against_recall_and_field_retrieval(self):
        data, run, review = self.fixture()
        target = dict(data['cases'][0]['required_records'][0], owner='Bob')
        data['cases'].append(dict(data['cases'][0], id='E', required_records=[target]))
        run['cases'].append(dict(id='E', result='ERROR', audit_completed=False))
        review['run_sha256'] = hashlib.sha256(json.dumps(run, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        m = score(data, run, review)['metrics']['all']
        self.assertEqual(m['pipeline_completion']['rate'], 0.5)
        self.assertEqual(m['required_record_recall_end_to_end']['rate'], 0.5)
        self.assertEqual(m['required_record_recall_on_completed_cases']['rate'], 1)
        self.assertEqual(m['nonnull_field_recall_end_to_end']['owner'], dict(correct=0,total=1,rate=0))

    def test_negative_case_has_undefined_precision_and_recall(self):
        data, run, review = self.fixture()
        data['cases'][0]['required_records'] = []
        run['cases'][0]['output']['records'] = []
        review['cases'][0].update(predictions=[], matches=[])
        review['run_sha256'] = hashlib.sha256(json.dumps(run, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        m = score(data, run, review)['metrics']['all']
        self.assertIsNone(m['supported_record_precision']['rate'])
        self.assertIsNone(m['required_record_recall_end_to_end']['rate'])
        self.assertEqual(m['correct_abstention']['rate'], 1)


if __name__ == '__main__':
    unittest.main()

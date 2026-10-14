import io
import json
import unittest
import urllib.error
from unittest.mock import MagicMock, patch
from meeting_intelligence.auditor import AuditFinding, apply_audit_findings, audit_events
from meeting_intelligence.llm_client import LLMClient, LLMError, strict_schema
from meeting_intelligence.models import EventBatch, ResultRecord
from meeting_intelligence.pipeline import analyze
from meeting_intelligence.parser import parse_transcript


class AuditStateTests(unittest.TestCase):
    def test_audit_receives_explicit_cleared_fields_and_separate_current_sources(self):
        record=ResultRecord(issue_key='x',topic='x',kind='decision',content='B',meeting_status='reopened',
                            condition=None,evidence_ids=['L001','L002'],
                            field_evidence_ids={'content':['L001'],'condition':['L002'],'meeting_status':['L002']})
        class Client:
            def completion_json(self,system,user):
                self.payload=json.loads(user)
                return {'findings':[]}
        client=Client()
        audit_events(parse_transcript('Chốt B nếu đủ quyền\nMở lại B'),[],[record],client)
        candidate=client.payload['records'][0]
        self.assertIn('condition',candidate)
        self.assertIsNone(candidate['condition'])
        self.assertNotIn('evidence_ids',candidate)
        self.assertEqual(candidate['field_evidence_ids']['condition'],['L002'])

    def test_high_findings_preserve_inactive_and_nonfinal_states(self):
        for status in ('open','proposed','reopened','withdrawn','cancelled'):
            with self.subTest(status=status):
                kind = 'action' if status == 'cancelled' else 'decision'
                record = ResultRecord(issue_key='x',topic='x',kind=kind,content='x',meeting_status=status)
                finding = AuditFinding(issue_key='x',kind=kind,category='missing_late_change',
                                       severity='high',source_ids=['L001'],source_quote='nguồn',explanation='cần kiểm tra')
                apply_audit_findings([record],[finding])
                self.assertEqual(record.meeting_status,status)
                self.assertEqual(record.review_status,'needs_review')
                self.assertTrue(record.warnings)

    def test_active_claim_still_fails_closed(self):
        record = ResultRecord(issue_key='x',topic='x',kind='decision',content='x',meeting_status='agreed')
        finding = AuditFinding(issue_key='x',category='unsupported_fact',severity='high',
                               source_ids=['L001'],source_quote='nguồn',explanation='không có căn cứ')
        apply_audit_findings([record],[finding])
        self.assertEqual(record.meeting_status,'unverified')

    def test_audit_transport_failure_does_not_erase_cancellation(self):
        class Client:
            count = 0
            def completion_json(self,*args):
                self.count += 1
                if self.count > 1: raise LLMError('audit unavailable')
                return {'events':[
                    dict(issue_key='test',topic='kiểm thử',kind='action',event_type='assignment',
                         source_ids=['L001'],value='kiểm thử',owner='Lan'),
                    dict(issue_key='test',topic='kiểm thử',kind='action',event_type='action_cancelled',
                         source_ids=['L002'],value=None)]}
        result = analyze('Lan: Tôi nhận kiểm thử\nMinh: Hủy việc kiểm thử',client=Client())
        self.assertEqual(result.records[0].meeting_status,'cancelled')
        self.assertEqual(result.records[0].review_status,'needs_review')
        self.assertEqual(result.records[0].owner,'Lan')


class StructuredTransportTests(unittest.TestCase):
    def client(self, **kwargs):
        return LLMClient(api_key='test-secret',base_url='https://api.groq.com/openai/v1',
                         model='openai/gpt-oss-120b',structured_mode='auto',**kwargs)

    def response(self):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps({
            'choices':[{'finish_reason':'stop','message':{'content':'{"events":[]}'}}]}).encode()
        return response

    def test_typed_groq_request_uses_strict_schema(self):
        with patch('urllib.request.urlopen',return_value=self.response()) as transport:
            self.assertEqual(self.client().completion_typed('system','user',EventBatch),{'events':[]})
            payload = json.loads(transport.call_args.args[0].data)
        schema = payload['response_format']['json_schema']
        self.assertEqual(payload['response_format']['type'],'json_schema')
        self.assertEqual(payload['max_completion_tokens'],2560)
        self.assertTrue(schema['strict'])
        event = schema['schema']['$defs']['Event']
        self.assertEqual(set(event['required']),set(event['properties']))
        self.assertFalse(event['additionalProperties'])
        self.assertIn({'type':'null'},event['properties']['owner']['anyOf'])

    def test_other_provider_keeps_legacy_json_mode(self):
        client = self.client()
        client.base_url = 'http://localhost/v1'
        with patch('urllib.request.urlopen',return_value=self.response()) as transport:
            client.completion_typed('system','user',EventBatch)
        self.assertEqual(json.loads(transport.call_args.args[0].data)['response_format'],{'type':'json_object'})

    def test_schema_conversion_does_not_mutate_validation_schema(self):
        original = EventBatch.model_json_schema()
        before = json.dumps(original,sort_keys=True)
        strict_schema(original)
        self.assertEqual(json.dumps(original,sort_keys=True),before)

    def test_explicit_completion_budget_is_sent(self):
        with patch('urllib.request.urlopen',return_value=self.response()) as transport:
            self.client(max_completion_tokens=4096).completion_json('system','user')
        self.assertEqual(json.loads(transport.call_args.args[0].data)['max_completion_tokens'],4096)

    def test_invalid_completion_budget_is_rejected_before_network(self):
        with self.assertRaises(LLMError):
            self.client(max_completion_tokens=0)

    def test_provider_error_exposes_code_without_echoing_rejected_content(self):
        body = {'error':{'code':'json_validate_failed','message':'test-secret private meeting',
                         'failed_generation':'private meeting'}}
        error = urllib.error.HTTPError('https://api.groq.com',400,'bad',{},io.BytesIO(json.dumps(body).encode()))
        with patch('urllib.request.urlopen',side_effect=error):
            with self.assertRaises(LLMError) as caught:
                self.client().completion_json('system','user')
        self.assertEqual(caught.exception.provider_code,'json_validate_failed')
        self.assertEqual(caught.exception.status_code,400)
        self.assertNotIn('test-secret',str(caught.exception))
        self.assertNotIn('private meeting',str(caught.exception))

    def test_truncation_reason_is_available_without_returning_partial_content(self):
        response=MagicMock()
        response.__enter__.return_value.read.return_value=json.dumps({'choices':[
            {'finish_reason':'length','message':{'content':'private partial output'}}]}).encode()
        with patch('urllib.request.urlopen',return_value=response):
            with self.assertRaises(LLMError) as caught:
                self.client().completion_json('system','user')
        self.assertEqual(caught.exception.diagnostics,{'finish_reason':'length'})
        self.assertNotIn('private partial output',str(caught.exception))

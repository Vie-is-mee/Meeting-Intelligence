"""Core regressions with authored events: these do NOT measure LLM accuracy."""
import json
import io
import urllib.error
import unittest
from unittest.mock import patch

from meeting_intelligence.auditor import audit_events, apply_audit_findings, AuditFinding
from meeting_intelligence.llm_client import LLMClient, LLMError
from meeting_intelligence.models import Event, AnalysisResult
from meeting_intelligence.parser import parse_transcript
from meeting_intelligence.resolver import resolve_events
from meeting_intelligence.verifier import verify_records
from scripts.run_scenarios import evaluate


def event(typ, sources, kind='action', key='testing', **fields):
    return Event(issue_key=key, topic=key, kind=kind, event_type=typ,
                 source_ids=sources, **fields)


class TemporalRegressionTests(unittest.TestCase):
    def test_execution_block_has_separate_source_from_meeting_agreement(self):
        lines = parse_transcript('Chốt phương án B\nChưa triển khai, chờ pháp chế')
        record = resolve_events([
            event('agreement', ['L001'], kind='decision', value='phương án B'),
            event('execution_blocked', ['L002'], kind='decision',
                  value='chưa triển khai', condition='chờ pháp chế')], lines)[0]
        self.assertEqual(record.meeting_status, 'agreed')
        self.assertEqual(record.execution_status, 'blocked')
        self.assertEqual(record.field_evidence_ids['meeting_status'], ['L001'])
        self.assertEqual(record.field_evidence_ids['execution_status'], ['L002'])
        self.assertEqual(record.field_evidence_ids['condition'], ['L002'])

    def test_deadline_change_does_not_replace_task_description_or_assignment_source(self):
        lines = parse_transcript('Lan kiểm thử B\nBỏ hạn cũ, chưa có ngày hoàn thành')
        record = resolve_events([
            event('assignment', ['L001'], owner='Lan', value='kiểm thử B'),
            event('deadline_change', ['L002'], value='chưa có ngày hoàn thành',
                  clear_fields=['due_raw'])], lines)[0]
        self.assertEqual(record.content, 'kiểm thử B')
        self.assertEqual(record.meeting_status, 'assigned')
        self.assertEqual(record.field_evidence_ids['content'], ['L001'])
        self.assertEqual(record.field_evidence_ids['meeting_status'], ['L001'])
        self.assertEqual(record.field_evidence_ids['due_raw'], ['L002'])

    def test_deadline_change_cannot_reactivate_cancelled_task(self):
        lines = parse_transcript('Lan kiểm thử B\nHủy việc kiểm thử\nBỏ hạn cũ')
        record = resolve_events([
            event('assignment', ['L001'], owner='Lan', value='kiểm thử B'),
            event('action_cancelled', ['L002']),
            event('deadline_change', ['L003'], clear_fields=['due_raw'])], lines)[0]
        self.assertEqual(record.meeting_status, 'cancelled')
        self.assertEqual(record.field_evidence_ids['meeting_status'], ['L002'])

    def test_reopening_preserves_source_of_historical_content(self):
        lines = parse_transcript('Chốt phương án B\nKhoan, hôm nay chưa chốt')
        records = resolve_events([
            event('agreement', ['L001'], kind='decision', value='phương án B'),
            event('reopen', ['L002'], kind='decision', value='hôm nay chưa chốt')], lines)
        self.assertEqual(records[0].meeting_status, 'reopened')
        self.assertEqual(records[0].content, 'phương án B')
        self.assertEqual(records[0].field_evidence_ids['content'], ['L001'])
        self.assertEqual(records[0].field_evidence_ids['meeting_status'], ['L002'])

    def test_change_with_earlier_context_is_applied_at_latest_source(self):
        lines = parse_transcript('Minh kiểm thử\nLan kiểm thử\nĐổi lại, Hương kiểm thử')
        events = [event('assignment', ['L001'], owner='Minh'),
                  event('reassignment', ['L002'], owner='Lan'),
                  event('reassignment', ['L001', 'L003'], owner='Hương')]
        self.assertEqual(resolve_events(events, lines)[0].owner, 'Hương')

    def test_promoted_supporter_does_not_support_themself(self):
        lines = parse_transcript('Minh làm, Lan hỗ trợ\nĐổi sang Lan phụ trách')
        events = [event('assignment', ['L001'], owner='Minh', supporter='Lan'),
                  event('reassignment', ['L002'], owner='Lan')]
        record = resolve_events(events, lines)[0]
        self.assertEqual(record.owner, 'Lan')
        self.assertIsNone(record.supporter)

    def test_explicit_deadline_withdrawal_clears_old_deadline(self):
        lines = parse_transcript('Minh làm hạn thứ Sáu\nBỏ hạn thứ Sáu, chưa chốt hạn mới')
        events = [event('assignment', ['L001'], owner='Minh', due_raw='thứ Sáu'),
                  event('deadline_change', ['L002'], clear_fields=['due_raw'])]
        record = resolve_events(events, lines)[0]
        self.assertIsNone(record.due_raw)
        self.assertEqual(record.owner, 'Minh')

    def test_reassignment_without_named_replacement_does_not_retain_old_owner(self):
        lines = parse_transcript('Minh làm\nĐổi người phụ trách, chưa biết ai')
        record = resolve_events([event('assignment', ['L001'], owner='Minh'),
                                 event('reassignment', ['L002'])], lines)[0]
        self.assertIsNone(record.owner)
        self.assertEqual(record.meeting_status, 'unverified')

    def test_reassignment_keeps_deadline_when_not_changed(self):
        lines = parse_transcript('Minh làm hạn thứ Sáu\nLan phụ trách thay Minh')
        record = resolve_events([event('assignment', ['L001'], owner='Minh', due_raw='thứ Sáu'),
                                 event('reassignment', ['L002'], owner='Lan')], lines)[0]
        self.assertEqual(record.due_raw, 'thứ Sáu')

    def test_clear_and_update_same_field_is_rejected(self):
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            event('deadline_change', ['L001'], due_raw='thứ Sáu', clear_fields=['due_raw'])


class EvidenceRegressionTests(unittest.TestCase):
    def test_owner_must_be_supported_by_its_update_not_old_history(self):
        lines = parse_transcript('Minh kiểm thử, Lan hỗ trợ\nHương phụ trách thay Minh')
        events = [event('assignment', ['L001'], owner='Minh'),
                  event('reassignment', ['L002'], owner='Lan')]
        record = verify_records(resolve_events(events, lines), lines)[0]
        self.assertIsNone(record.owner)
        self.assertEqual(record.meeting_status, 'unverified')

    def test_self_assignment_can_reference_speaker(self):
        lines = parse_transcript('Lan: Tôi sẽ kiểm thử')
        record = verify_records(resolve_events([
            event('assignment', ['L001'], owner='Lan')], lines), lines)[0]
        self.assertEqual(record.owner, 'Lan')

    def test_partial_name_is_not_supported_by_longer_name(self):
        lines = parse_transcript('Minh Anh kiểm thử')
        record = verify_records(resolve_events([
            event('assignment', ['L001'], owner='An')], lines), lines)[0]
        # This is a lexical guard, not a claim that every name mention is an assignment.
        self.assertIsNone(record.owner)

    def test_missing_source_cannot_leave_a_finalized_decision(self):
        lines = parse_transcript('Chốt B')
        record = verify_records(resolve_events([
            event('agreement', ['L999'], kind='decision', value='Tăng ngân sách')], lines), lines)[0]
        self.assertEqual(record.meeting_status, 'unverified')

    def test_final_content_must_use_final_event_evidence(self):
        lines = parse_transcript('Đề xuất B\nChốt A')
        events = [event('proposal', ['L001'], kind='decision', value='B'),
                  event('agreement', ['L002'], kind='decision', value='B')]
        record = verify_records(resolve_events(events, lines), lines)[0]
        self.assertEqual(record.meeting_status, 'unverified')


class AuditRegressionTests(unittest.TestCase):
    def test_empty_object_is_not_a_completed_audit(self):
        class Client:
            def completion_json(self, *_): return {}
        with self.assertRaises(LLMError):
            audit_events(parse_transcript('Chốt B'), [], [], Client())

    def test_auditor_receives_deadline_condition_and_supporter(self):
        lines = parse_transcript('Lan làm, Minh hỗ trợ, hạn thứ Sáu nếu có quyền')
        events = [event('assignment', ['L001'], owner='Lan', supporter='Minh',
                        due_raw='thứ Sáu', condition='nếu có quyền')]
        records = resolve_events(events, lines)
        class Client:
            def completion_json(self, system, user):
                self.payload = json.loads(user)
                return {'findings': []}
        client = Client()
        audit_events(lines, events, records, client)
        candidate = client.payload['records'][0]
        self.assertEqual(candidate['supporter'], 'Minh')
        self.assertEqual(candidate['due_raw'], 'thứ Sáu')
        self.assertEqual(candidate['condition'], 'nếu có quyền')

    def test_duplicate_issue_key_does_not_silently_lose_audit_hold(self):
        lines = parse_transcript('Chốt B\nLan kiểm thử B\nChưa chốt B')
        records = resolve_events([
            event('agreement', ['L001'], kind='decision', key='B', value='B'),
            event('assignment', ['L002'], key='B', owner='Lan')], lines)
        finding = AuditFinding(issue_key='B', category='missing_late_change',
                               source_ids=['L003'], source_quote='Chưa chốt B',
                               explanation='Chưa rõ mục bị thay đổi')
        apply_audit_findings(records, [finding])
        self.assertTrue(all(r.meeting_status == 'unverified' for r in records))

    def test_kind_targets_only_the_intended_record(self):
        lines = parse_transcript('Chốt B\nLan kiểm thử B\nChưa chốt B')
        records = resolve_events([
            event('agreement', ['L001'], kind='decision', key='B', value='B'),
            event('assignment', ['L002'], key='B', owner='Lan')], lines)
        finding = AuditFinding(issue_key='B', kind='decision', category='missing_late_change',
                               source_ids=['L003'], source_quote='Chưa chốt B',
                               explanation='Quyết định mở lại, công việc vẫn giữ')
        apply_audit_findings(records, [finding])
        self.assertEqual(records[0].meeting_status, 'unverified')
        self.assertEqual(records[1].meeting_status, 'assigned')


class EvaluationRegressionTests(unittest.TestCase):
    def test_source_and_status_without_content_cannot_pass(self):
        result = self.result([event('feedback_given', ['L001'], kind='feedback')])
        errors = evaluate(result, {'expectations': [
            {'kind': 'feedback', 'status': 'recorded', 'must_cite': ['L001']}]})
        self.assertTrue(any('thiếu nội dung' in error for error in errors))

    def result(self, events):
        lines = parse_transcript('Chốt B\nChốt C')
        return AnalysisResult(engine='mock_for_tests', utterances=lines,
                              records=resolve_events(events, lines))

    def test_one_record_cannot_satisfy_two_expected_records(self):
        result = self.result([event('agreement', ['L001'], kind='decision', value='B')])
        target = {'kind': 'decision', 'status': 'agreed'}
        self.assertTrue(evaluate(result, {'expectations': [target, target]}))

    def test_extra_invented_record_is_not_a_pass(self):
        result = self.result([event('agreement', ['L001'], kind='decision', value='B'),
                              event('agreement', ['L002'], kind='decision', key='other', value='C')])
        self.assertTrue(evaluate(result, {'expectations': [
            {'kind': 'decision', 'status': 'agreed', 'content_contains': 'B'}]}))

    def test_broad_expectation_does_not_steal_specific_match(self):
        result = self.result([event('agreement', ['L001'], kind='decision', value='B'),
                              event('agreement', ['L002'], kind='decision', key='other', value='C')])
        expected = {'expectations': [
            {'kind': 'decision', 'status': 'agreed'},
            {'kind': 'decision', 'status': 'agreed', 'content_contains': 'B'}]}
        self.assertEqual(evaluate(result, expected), [])


class ProviderResponseRegressionTests(unittest.TestCase):
    def test_retry_after_is_respected(self):
        client = LLMClient(api_key='test', base_url='http://localhost/v1', model='test')
        error = urllib.error.HTTPError('http://localhost/v1', 429, 'limited',
                                       {'Retry-After': '5'}, io.BytesIO(b''))
        response = unittest.mock.MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps({
            'choices': [{'finish_reason': 'stop', 'message': {'content': '{"events":[]}'}}]
        }).encode()
        with patch('urllib.request.urlopen', side_effect=[error, response]), \
             patch('meeting_intelligence.llm_client.time.sleep') as sleep:
            self.assertEqual(client.completion_json('system', 'user'), {'events': []})
            sleep.assert_called_once_with(5.0)

    def test_excessive_retry_wait_returns_error_instead_of_retrying_early(self):
        client = LLMClient(api_key='test', base_url='http://localhost/v1', model='test',
                           max_retry_wait=10)
        error = urllib.error.HTTPError('http://localhost/v1', 429, 'limited',
                                       {'Retry-After': '120'}, io.BytesIO(b''))
        with patch('urllib.request.urlopen', side_effect=error) as transport, \
             patch('meeting_intelligence.llm_client.time.sleep') as sleep:
            with self.assertRaises(LLMError):
                client.completion_json('system', 'user')
            self.assertEqual(transport.call_count, 1)
            sleep.assert_not_called()

    def test_invalid_envelope_becomes_llm_error(self):
        client = LLMClient(api_key='test', base_url='http://localhost/v1', model='test')
        response = unittest.mock.MagicMock()
        response.__enter__.return_value.read.return_value = b'[]'
        with patch('urllib.request.urlopen', return_value=response):
            with self.assertRaises(LLMError):
                client.completion_json('system', 'user')

    def test_truncated_completion_is_not_accepted_as_complete(self):
        client = LLMClient(api_key='test', base_url='http://localhost/v1', model='test')
        response = unittest.mock.MagicMock()
        body = {'choices': [{'finish_reason': 'length',
                             'message': {'content': '{"events":[]}'}}]}
        response.__enter__.return_value.read.return_value = json.dumps(body).encode()
        with patch('urllib.request.urlopen', return_value=response):
            with self.assertRaises(LLMError):
                client.completion_json('system', 'user')

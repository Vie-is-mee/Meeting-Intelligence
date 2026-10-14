import unittest
from meeting_intelligence.models import Event
from meeting_intelligence.parser import parse_transcript
from meeting_intelligence.resolver import resolve_events
from meeting_intelligence.verifier import verify_records
from meeting_intelligence.extractor import extract_events
from meeting_intelligence.llm_client import LLMError


def event(typ, sid, kind='decision', **kwargs):
    return Event(issue_key='job',topic='job',kind=kind,event_type=typ,source_ids=[sid],**kwargs)


class FieldUpdateTests(unittest.TestCase):
    def test_reopen_removes_active_condition_but_preserves_history(self):
        lines=parse_transcript('Chốt tự động nếu có quyền\nMở lại, hôm nay chưa chốt')
        events=[event('conditional_agreement','L001',value='tự động',condition='có quyền'),event('reopen','L002')]
        r=resolve_events(events,lines)[0]
        self.assertEqual(r.meeting_status,'reopened')
        self.assertIsNone(r.condition)
        self.assertEqual(r.history[0].condition,'có quyền')
        self.assertEqual(r.field_evidence_ids['condition'],['L002'])

    def test_revised_conditional_agreement_replaces_old_condition(self):
        lines=parse_transcript('Chốt nếu đạt 500\nSửa điều kiện: đạt 300 và không lỗi')
        r=resolve_events([event('conditional_agreement','L001',value='phát hành',condition='đạt 500'),
                          event('conditional_agreement','L002',value='phát hành',condition='đạt 300 và không lỗi')],lines)[0]
        self.assertEqual(r.condition,'đạt 300 và không lỗi')
        self.assertEqual(r.execution_status,'pending_condition')
        self.assertEqual(r.field_evidence_ids['condition'],['L002'])

    def test_blocking_without_new_condition_preserves_explicit_existing_condition(self):
        lines=parse_transcript('Chốt nếu pháp chế duyệt\nChưa triển khai ngay')
        r=resolve_events([event('conditional_agreement','L001',value='chuyển',condition='pháp chế duyệt'),
                          event('execution_blocked','L002')],lines)[0]
        self.assertEqual(r.condition,'pháp chế duyệt')
        self.assertEqual(r.field_evidence_ids['condition'],['L001'])
        self.assertEqual(r.field_evidence_ids['execution_status'],['L002'])

    def test_request_relative_deadline_remains_without_assignment(self):
        lines=parse_transcript('Cần rà soát trước lần thử tiếp theo\nChưa chọn thứ Tư hay thứ Năm')
        r=resolve_events([event('request_made','L001',kind='request',value='rà soát',due_raw='trước lần thử tiếp theo'),
                          event('request_changed','L002',kind='request',value='rà soát, ngày cụ thể chưa chốt')],lines)[0]
        self.assertEqual(r.due_raw,'trước lần thử tiếp theo')
        self.assertEqual(r.field_evidence_ids['due_raw'],['L001'])
        self.assertEqual(r.meeting_status,'recorded')
        self.assertIsNone(r.owner)

    def test_deadline_change_cannot_reassign_owner(self):
        lines=parse_transcript('Lan làm kiểm thử\nMinh nhắc hạn là thứ Sáu')
        r=resolve_events([event('assignment','L001',kind='action',value='kiểm thử',owner='Lan'),
                          event('deadline_change','L002',kind='action',owner='Minh',due_raw='thứ Sáu')],lines)[0]
        self.assertEqual(r.owner,'Lan')
        self.assertEqual(r.due_raw,'thứ Sáu')
        self.assertEqual(r.review_status,'needs_review')

    def test_explicit_first_person_denial_cannot_support_owner(self):
        lines=parse_transcript('Vũ: Tôi không còn là người phụ trách chính bộ log mẫu')
        r=verify_records(resolve_events([event('reassignment','L001',kind='action',value='bộ log mẫu',owner='Vũ')],lines),lines)[0]
        self.assertIsNone(r.owner)
        self.assertEqual(r.meeting_status,'unverified')

    def test_denial_of_old_owner_does_not_remove_named_new_owner(self):
        lines=parse_transcript('Vũ không còn là người phụ trách; Oanh phụ trách bộ log mẫu')
        r=verify_records(resolve_events([event('reassignment','L001',kind='action',value='bộ log mẫu',owner='Oanh')],lines),lines)[0]
        self.assertEqual(r.owner,'Oanh')

    def test_ambiguous_orphan_deadline_is_not_silently_merged(self):
        class Client:
            def completion_json(self,*args):
                return {'events':[dict(issue_key='log',topic='log',kind='action',event_type='assignment',source_ids=['L001'],value='xuất log'),
                                  dict(issue_key='different_key',topic='log hạn',kind='action',event_type='deadline_change',source_ids=['L002'],due_raw='thứ Hai')]}
        with self.assertRaises(LLMError):
            extract_events(parse_transcript('Xuất log\nHạn thứ Hai'),Client())

    def test_same_person_can_leave_one_scope_and_own_another_in_same_turn(self):
        lines=parse_transcript('Vũ không còn phụ trách web; Vũ phụ trách mobile')
        r=verify_records(resolve_events([event('assignment','L001',kind='action',value='mobile',owner='Vũ')],lines),lines)[0]
        self.assertEqual(r.owner,'Vũ')

    def test_confirmation_of_role_denial_is_not_a_reassignment(self):
        lines=parse_transcript('Vũ: Tôi xác nhận không còn là người phụ trách chính bộ log mẫu')
        r=verify_records(resolve_events([event('reassignment','L001',kind='action',value='bộ log mẫu',owner='Vũ')],lines),lines)[0]
        self.assertIsNone(r.owner)
        self.assertEqual(r.review_status,'needs_review')

    def test_missing_unresolved_description_uses_literal_uncertainty_source(self):
        class Client:
            def completion_json(self,*args):
                return {'events':[dict(issue_key='date',topic='ngày',kind='decision',event_type='unresolved',source_ids=['L001'],value=None)]}
        warnings=[]
        events=extract_events(parse_transcript('Chưa chọn thứ Tư hay thứ Năm.'),Client(),warnings=warnings)
        self.assertEqual(events[0].value,'Chưa chọn thứ Tư hay thứ Năm.')
        self.assertTrue(warnings)

    def test_missing_description_without_uncertainty_source_is_rejected(self):
        class Client:
            def completion_json(self,*args):
                return {'events':[dict(issue_key='date',topic='ngày',kind='decision',event_type='unresolved',source_ids=['L001'],value=None)]}
        with self.assertRaises(LLMError):
            extract_events(parse_transcript('Tôi đang mở tài liệu.'),Client())

    def test_literal_request_bound_is_restored_with_source_and_review(self):
        lines=parse_transcript('Cần rà soát trước đợt chạy thử mới.')
        r=resolve_events([event('request_made','L001',kind='request',value='rà soát trước đợt chạy thử mới')],lines)[0]
        self.assertEqual(r.due_raw,'trước đợt chạy thử mới')
        self.assertEqual(r.field_evidence_ids['due_raw'],['L001'])
        self.assertEqual(r.review_status,'needs_review')
        self.assertIsNone(r.due_iso)

    def test_relative_bound_is_not_taken_from_negation_or_question(self):
        for text in ['Không cần rà soát trước đợt chạy thử mới.', 'Có cần rà soát trước đợt chạy thử mới không?']:
            r=resolve_events([event('request_made','L001',kind='request',value=text)],parse_transcript(text))[0]
            self.assertIsNone(r.due_raw)

    def test_missing_model_record_is_not_created_from_literal_bound(self):
        self.assertEqual(resolve_events([],parse_transcript('Cần rà soát trước đợt chạy thử mới.')),[])

    def test_relative_bound_with_unselected_alternatives_is_not_restored(self):
        for text in ['Cần rà soát trước đợt chạy thử mới không?',
                     'Yêu cầu rà soát trước đợt chạy thử A hoặc trước đợt chạy thử B.']:
            r=resolve_events([event('request_made','L001',kind='request',value=text)],parse_transcript(text))[0]
            self.assertIsNone(r.due_raw)

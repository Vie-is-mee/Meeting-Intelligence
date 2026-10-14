import copy
import unittest
from meeting_intelligence.models import Event
from meeting_intelligence.parser import parse_transcript
from meeting_intelligence.resolver import resolve_events
from meeting_intelligence.evidence_repairs import repair_explicit_source_updates


class ExplicitSourceRepairTests(unittest.TestCase):
    def task(self, cancellation='Hủy việc soạn tài liệu, bỏ hạn đã giao.'):
        lines=parse_transcript('Lan: Tôi nhận soạn tài liệu cho đội kiểm thử, hạn sáng mai.\nAn: '+cancellation)
        events=[Event(issue_key='task',topic='tài liệu',kind='action',event_type='assignment',source_ids=['L001'],value='soạn tài liệu cho đội kiểm thử',owner='Lan',due_raw='sáng mai'),
                Event(issue_key='task',topic='tài liệu',kind='action',event_type='action_cancelled',source_ids=['L002'])]
        return lines,events

    def test_explicit_removed_deadline_is_cleared_with_source_and_owner_preserved(self):
        lines,events=self.task();before=copy.deepcopy(events);notes=[]
        fixed=repair_explicit_source_updates(events,lines,warnings=notes)
        r=resolve_events(fixed,lines)[0]
        self.assertEqual(events,before)
        self.assertEqual(len(events),len(fixed));self.assertTrue(notes)
        self.assertEqual((r.meeting_status,r.owner,r.due_raw),('cancelled','Lan',None))
        self.assertEqual(r.field_evidence_ids['due_raw'],['L002'])

    def test_named_date_removal_and_conjunction(self):
        for text in ['Hủy việc soạn tài liệu, bỏ hạn sáng mai.','Hủy việc soạn tài liệu và xóa hạn đã giao.']:
            lines,events=self.task(text)
            self.assertIn('due_raw',repair_explicit_source_updates(events,lines)[1].clear_fields)

    def test_cancellation_alone_other_task_question_hypothetical_and_quote_do_not_clear(self):
        for text in ['Hủy việc soạn tài liệu.', 'Hủy việc kiểm tra mạng, bỏ hạn đã giao.',
                     'Hủy việc soạn tài liệu, bỏ hạn đã giao?', 'Nếu hủy việc soạn tài liệu, bỏ hạn đã giao.',
                     'Hủy việc soạn tài liệu, bỏ hạn đã giao. Đây là ví dụ.',
                     'Hủy việc soạn tài liệu, bỏ hạn thứ Sáu.',
                     'Hủy việc soạn tài liệu, bỏ hạn đã giao. Không bỏ hạn thật.']:
            with self.subTest(text=text):
                lines,events=self.task(text)
                self.assertEqual(repair_explicit_source_updates(events,lines),events)

    def test_multiple_tasks_on_same_cancellation_source_require_review(self):
        lines,events=self.task();events.append(events[1].model_copy(update={'issue_key':'other'}))
        self.assertEqual(repair_explicit_source_updates(events,lines),events)

    def test_older_named_date_cannot_remove_newer_deadline(self):
        lines=parse_transcript('Lan: Tôi nhận soạn tài liệu, hạn sáng mai.\nAn: Đổi hạn sang thứ Sáu.\nAn: Hủy việc soạn tài liệu, bỏ hạn sáng mai.')
        _,events=self.task();events[1]=events[1].model_copy(update={'source_ids':['L003']})
        events.insert(1,Event(issue_key='task',topic='tài liệu',kind='action',event_type='deadline_change',source_ids=['L002'],due_raw='thứ Sáu'))
        self.assertEqual(repair_explicit_source_updates(events,lines),events)

    def decision(self, closing='Chốt dùng bộ nhớ ngoài cho nhóm thử nghiệm.'):
        lines=parse_transcript('An: Tôi đồng ý dùng bộ nhớ ngoài.\nBình: '+closing)
        events=[Event(issue_key='choice',topic='lưu trữ',kind='decision',event_type='agreement',source_ids=['L001'],value='dùng bộ nhớ ngoài cho nhóm thử nghiệm')]
        return lines,events

    def test_exact_late_reaffirmation_supports_scope_without_inventing_event(self):
        lines,events=self.decision();before=copy.deepcopy(events)
        fixed=repair_explicit_source_updates(events,lines)
        self.assertEqual(events,before);self.assertEqual(len(fixed),1)
        self.assertEqual(fixed[0].source_ids,['L001','L002'])
        self.assertEqual(fixed[0].value,events[0].value)
        self.assertEqual(resolve_events(fixed,lines)[0].field_evidence_ids['content'],['L001','L002'])

    def test_no_paraphrase_scope_widening_question_conditional_or_quote_repair(self):
        for text in ['Chốt dùng bộ nhớ ngoài cho toàn công ty.', 'Chốt dùng bộ nhớ ngoài cho nhóm thử nghiệm?',
                     'Chốt dùng bộ nhớ ngoài cho nhóm thử nghiệm nếu đủ tiền.',
                     'Ví dụ: Chốt dùng bộ nhớ ngoài cho nhóm thử nghiệm.',
                     'Chốt dùng bộ nhớ ngoài cho nhóm thử nghiệm. Tôi mở lại lựa chọn này.']:
            lines,events=self.decision(text)
            self.assertEqual(repair_explicit_source_updates(events,lines),events)

    def test_reopened_state_and_ambiguous_keys_do_not_gain_new_agreement(self):
        lines,events=self.decision()
        events.append(Event(issue_key='choice',topic='lưu trữ',kind='decision',event_type='reopen',source_ids=['L002']))
        self.assertEqual(repair_explicit_source_updates(events,lines),events)

    def test_withdrawal_then_agreement_in_one_turn_keeps_stable_event_order(self):
        lines,events=self.decision()
        events.insert(0,Event(issue_key='choice',topic='lưu trữ',kind='decision',event_type='withdrawal',source_ids=['L001']))
        fixed=repair_explicit_source_updates(events,lines)
        self.assertEqual(fixed[0],events[0])
        self.assertEqual(fixed[1].source_ids,['L001','L002'])

    def test_meaningful_internal_punctuation_is_not_discarded(self):
        lines,events=self.decision('Chốt triển khai C cho nhóm thử nghiệm.')
        events[0].value='triển khai C++ cho nhóm thử nghiệm'
        self.assertEqual(repair_explicit_source_updates(events,lines),events)
        lines,events=self.decision();events.append(events[0].model_copy(update={'issue_key':'other'}))
        self.assertEqual(repair_explicit_source_updates(events,lines),events)


if __name__=='__main__':unittest.main()

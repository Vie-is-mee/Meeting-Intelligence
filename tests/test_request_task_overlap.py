"""Software risk checks; authored events do not measure LLM extraction accuracy."""
import unittest
from meeting_intelligence.models import Event
from meeting_intelligence.parser import parse_transcript
from meeting_intelligence.resolver import resolve_events
from meeting_intelligence.verifier import verify_records


class RequestTaskOverlapTests(unittest.TestCase):
    def build(self, *, separate_key=False, separate_content=False, reaffirm=False, cancelled=True):
        lines = parse_transcript('L001 | Hà | Cần lập báo cáo.\nL002 | Mai | Tôi nhận lập báo cáo.\n'
                                 'L003 | Hà | Hủy việc lập báo cáo.\nL004 | Hà | Yêu cầu lập báo cáo vẫn giữ.')
        def event(kind, typ, sid, **fields):
            return Event(issue_key='report', topic='báo cáo', kind=kind,
                         event_type=typ, source_ids=[sid], **fields)
        request = event('request','request_made','L001',value='lập báo cáo')
        if separate_key: request.issue_key = 'customer_requirement'
        if separate_content: request.value = 'xuất báo cáo CSV'
        events = [request, event('action','assignment','L002',value='lập báo cáo',owner='Mai')]
        if cancelled: events.append(event('action','action_cancelled','L003'))
        if reaffirm: events.append(event('request','request_changed','L004',value='lập báo cáo'))
        records = verify_records(resolve_events(events,lines),lines)
        return lines, records, next(r for r in records if r.kind=='request')

    def test_duplicate_request_is_flagged_without_deletion_or_withdrawal(self):
        lines, records, request = self.build()
        self.assertEqual(len(records),2)
        self.assertEqual(request.meeting_status,'recorded')
        self.assertEqual(request.content,'lập báo cáo')
        self.assertEqual(request.review_status,'needs_review')
        self.assertTrue(any('Nguồn yêu cầu: L001; nguồn hủy: L003' in w for w in request.warnings))
        self.assertEqual(next(r for r in records if r.kind=='action').meeting_status,'cancelled')
        verify_records(records,lines)
        self.assertEqual(sum('Yêu cầu trùng nội dung' in w for w in request.warnings),1)

    def test_same_topic_with_different_content_is_not_flagged(self):
        _, _, request = self.build(separate_content=True)
        self.assertEqual(request.review_status,'unreviewed')

    def test_separate_business_key_is_not_merged_or_flagged(self):
        _, _, request = self.build(separate_key=True)
        self.assertEqual(request.review_status,'unreviewed')

    def test_later_reaffirmed_requirement_is_not_flagged(self):
        _, _, request = self.build(reaffirm=True)
        self.assertEqual(request.review_status,'unreviewed')
        self.assertIn('L004',request.evidence_ids)

    def test_active_task_alone_does_not_trigger_cancellation_warning(self):
        _, _, request = self.build(cancelled=False)
        self.assertEqual(request.review_status,'unreviewed')


if __name__ == '__main__': unittest.main()

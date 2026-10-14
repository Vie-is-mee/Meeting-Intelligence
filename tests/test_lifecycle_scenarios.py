"""LC01-LC03 software contracts with authored events, NOT real LLM results."""
import json
import unittest
from pathlib import Path
from meeting_intelligence.pipeline import analyze

ROOT=Path(__file__).resolve().parents[1]


def event(kind,typ,key,sid,value=None,**fields):
    return dict(kind=kind,event_type=typ,issue_key=key,topic=key,
                source_ids=[sid],value=value,**fields)


class LifecycleScenarioTests(unittest.TestCase):
    def run_case(self,cid,events,*,transcript=None):
        cases=json.loads((ROOT/'datasets/task_lifecycle_regression_v1.json').read_text(encoding='utf-8'))['cases']
        if transcript is None:
            transcript=next(c['transcript'] for c in cases if c['id']==cid)
        class AuthoredClient:
            def completion_json(self,*args): return {'events':events}
        result=analyze(transcript,client=AuthoredClient(),audit=False)
        return {(r.kind,r.issue_key):r for r in result.records}

    def test_direct_assignment_cancelled_does_not_reactivate(self):
        records=self.run_case('LC01',[
            event('action','assignment','reconcile','L001','lập bảng đối soát',owner='Mai',due_raw='sáng thứ Sáu'),
            event('action','action_cancelled','reconcile','L003'),
            event('action','deadline_change','reconcile','L004',clear_fields=['due_raw'])])
        self.assertEqual(len(records),1)
        task=records['action','reconcile']
        self.assertEqual(task.meeting_status,'cancelled')
        self.assertEqual(task.owner,'Mai')
        self.assertIsNone(task.due_raw)
        self.assertEqual(task.field_evidence_ids['meeting_status'],['L003'])

    def test_customer_request_survives_cancelled_implementation(self):
        records=self.run_case('LC02',[
            event('request','request_made','csv','L001','xuất báo cáo dạng CSV'),
            event('action','assignment','trial','L002','thử bộ xuất CSV bằng thư viện X',owner='Dũng',due_raw='chiều mai'),
            event('action','action_cancelled','trial','L004',clear_fields=['due_raw']),
            event('decision','unresolved','replacement','L005','Chưa chọn cách triển khai thay thế')])
        self.assertEqual(len(records),3)
        self.assertEqual(records['request','csv'].meeting_status,'recorded')
        self.assertEqual(records['request','csv'].review_status,'unreviewed')
        self.assertEqual(records['action','trial'].meeting_status,'cancelled')
        self.assertEqual(records['action','trial'].owner,'Dũng')
        self.assertIsNone(records['action','trial'].due_raw)
        self.assertEqual(records['decision','replacement'].meeting_status,'open')
        self.assertFalse(any(r.kind=='action' and r.meeting_status=='assigned' for r in records.values()))

    def test_scope_and_requirement_survive_cancelled_documentation(self):
        records=self.run_case('LC03',[
            event('decision','agreement','scope','L001','chỉ thử luồng thanh toán mới ở nhóm nội bộ'),
            event('request','request_made','back_button','L002','có nút quay lại bước trước'),
            event('action','assignment','guide','L003','viết hướng dẫn cho nhóm nội bộ',owner='Chi',due_raw='cuối ngày mai'),
            event('action','action_cancelled','guide','L005',clear_fields=['due_raw'])])
        self.assertEqual(len(records),3)
        self.assertEqual(records['decision','scope'].meeting_status,'agreed')
        self.assertIn('chỉ thử',records['decision','scope'].content)
        self.assertIn('nhóm nội bộ',records['decision','scope'].content)
        self.assertEqual(records['request','back_button'].meeting_status,'recorded')
        self.assertEqual(records['request','back_button'].review_status,'unreviewed')
        self.assertEqual(records['action','guide'].meeting_status,'cancelled')
        self.assertEqual(records['action','guide'].owner,'Chi')
        self.assertIsNone(records['action','guide'].due_raw)

    def test_cancellation_can_explicitly_clear_owner_and_condition(self):
        records=self.run_case('LC01',[
            event('action','assignment','reconcile','L001','lập bảng đối soát',owner='Mai',condition='đợi xác nhận'),
            event('action','action_cancelled','reconcile','L003',clear_fields=['owner','condition'])],
            transcript='L001 | Linh | Mai lập bảng đối soát, đợi xác nhận.\n'
                       'L002 | Mai | Tôi nhận việc đó.\n'
                       'L003 | Linh | Hủy việc lập bảng, bỏ phân công cho Mai và bỏ điều kiện đợi xác nhận.')
        task=records['action','reconcile']
        self.assertEqual(task.meeting_status,'cancelled')
        self.assertIsNone(task.owner)
        self.assertIsNone(task.condition)
        self.assertEqual(task.field_evidence_ids['owner'],['L003'])
        self.assertEqual(task.field_evidence_ids['condition'],['L003'])
        self.assertEqual(task.execution_status,'unknown')

    def test_cancellation_without_explicit_clear_preserves_history(self):
        records=self.run_case('LC01',[
            event('action','assignment','reconcile','L001','lập bảng đối soát',owner='Mai',due_raw='sáng thứ Sáu'),
            event('action','action_cancelled','reconcile','L003',owner='Linh',due_raw='chiều mai')])
        task=records['action','reconcile']
        self.assertEqual(task.meeting_status,'cancelled')
        self.assertEqual(task.owner,'Mai')
        self.assertEqual(task.due_raw,'sáng thứ Sáu')
        self.assertEqual(task.field_evidence_ids['owner'],['L001'])


if __name__=='__main__': unittest.main()

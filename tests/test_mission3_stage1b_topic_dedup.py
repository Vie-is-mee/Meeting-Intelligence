"""Stage 1B: source-grounded H03 duplicate decision controls.

Archive: m3_fresh_regression_H03_LC01_7e63907_run1.json.
These are deterministic replays of real Groq output, not new provider calls.
"""
from __future__ import annotations
import json
import unittest
from pathlib import Path
from meeting_intelligence.pipeline import analyze
from meeting_intelligence.models import Event

ROOT = Path(__file__).resolve().parents[1]
RUN = json.loads((ROOT/"docs/evaluation/mission3/m3_fresh_regression_H03_LC01_7e63907_run1.json").read_text(encoding="utf-8"))
H03 = next(c for c in RUN["cases"] if c["id"]=="H03")
RAW_EVENTS = H03["llm_responses"][0]["response"]["events"]
FINDINGS = H03["llm_responses"][1]["response"]["findings"]
TRANSCRIPT = "\n".join(f"{u['id']} | {u['speaker'] or 'Không rõ'} | {u['text']}"
                       for u in H03["output"]["utterances"])

class SourceReplayClient:
    def __init__(self, events, findings=None):
        self.events=events
        self.findings=findings if findings is not None else []
        self.calls=0

    def completion_json(self, *args, **kwargs):
        self.calls+=1
        return {"events": self.events} if self.calls==1 else {"findings": self.findings}

def ev(key, kind, typ, sid, value, topic):
    return Event(issue_key=key,kind=kind,event_type=typ,
                 source_ids=[sid],value=value,topic=topic).model_dump()

class TopicResolutionStage1BTests(unittest.TestCase):
    def test_archived_h03_has_only_request_plus_open_deadline(self):
        out=analyze(TRANSCRIPT,client=SourceReplayClient(RAW_EVENTS,FINDINGS),audit=True)
        self.assertEqual(sorted((r.kind,r.meeting_status) for r in out.records),
                         [('decision','open'),('request','recorded')])
        req=next(r for r in out.records if r.kind=='request')
        self.assertIsNone(req.owner)
        self.assertEqual(req.due_raw,'trước lần thử tiếp theo')
        self.assertIn('L006',req.counter_evidence_ids)
        self.assertIn('L006',req.field_evidence_ids.get('owner',[]))
        self.assertEqual(req.review_status,'needs_review')
        deadline=next(r for r in out.records if r.kind=='decision')
        self.assertEqual(deadline.issue_key,'email_review_deadline')
        self.assertEqual(deadline.meeting_status,'open')
        self.assertEqual(deadline.evidence_ids,['L004','L005','L006'])
        self.assertEqual(out.audit_findings,[])
        self.assertTrue(any('trùng' in w.casefold() and 'L006' in w for w in out.warnings))

    def test_generic_no_assignment_echo_on_same_task_keeps_unresolved_date(self):
        text=('An: Cần kiểm thử tải API trước đợt demo.\n'
              'Bình: Hay chọn thứ Ba?\n'
              'Chi: Thứ Năm có thể tốt hơn.\n'
              'An: Chưa chọn thứ Ba hay thứ Năm và chưa phân công người kiểm thử tải API cho ai.')
        events=[
            ev('load_req','request','request_made','L001','Cần kiểm thử tải API trước đợt demo','kiểm thử tải API'),
            ev('date_choice','decision','proposal','L002','chọn thứ Ba','lịch kiểm thử tải API'),
            ev('date_choice','decision','counterproposal','L003','chọn thứ Năm','lịch kiểm thử tải API'),
            ev('date_choice','decision','unresolved','L004','chưa chọn thứ Ba hay thứ Năm','lịch kiểm thử tải API'),
            ev('owner_echo','decision','unresolved','L004',
               'chưa phân công người kiểm thử tải API cho ai',
               'phân công người kiểm thử tải API')
        ]
        out=analyze(text,client=SourceReplayClient(events),audit=False)
        self.assertEqual(len([r for r in out.records if r.kind=='decision']),1)
        self.assertEqual(len([r for r in out.records if r.kind=='request']),1)
        self.assertIn('L004',out.records[0].counter_evidence_ids)

    def test_separate_choice_of_people_is_not_an_echo(self):
        text=('An: Cần kiểm thử tải API trước đợt demo.\n'
              'Bình: Hay chọn thứ Ba?\n'
              'Chi: Thứ Năm có thể tốt hơn.\n'
              'An: Chưa chọn thứ Ba hay thứ Năm; chưa chọn Lan hay Huy phụ trách kiểm thử tải API.')
        events=[
            ev('load_req','request','request_made','L001','Cần kiểm thử tải API trước đợt demo','kiểm thử tải API'),
            ev('date_choice','decision','unresolved','L004','chưa chọn thứ Ba hay thứ Năm','lịch kiểm thử tải API'),
            ev('person_choice','decision','unresolved','L004',
               'chưa chọn Lan hay Huy phụ trách kiểm thử tải API',
               'người phụ trách kiểm thử tải API')
        ]
        out=analyze(text,client=SourceReplayClient(events),audit=False)
        self.assertEqual(len([r for r in out.records if r.kind=='decision']),2)

    def test_no_request_or_wrong_task_cannot_remove_a_nonassignment_decision(self):
        text=('An: Cần kiểm thử tải API.\n'
              'Bình: Hay chọn thứ Tư?\n'
              'An: Chưa chọn thứ Tư hay thứ Năm và chưa giao việc sửa hợp đồng cho ai.')
        events=[
            ev('load_req','request','request_made','L001','Cần kiểm thử tải API','kiểm thử tải API'),
            ev('date_choice','decision','unresolved','L003','chưa chọn thứ Tư hay thứ Năm','lịch kiểm thử tải API'),
            ev('contract_owner','decision','unresolved','L003','chưa giao việc sửa hợp đồng cho ai','sửa hợp đồng')
        ]
        out=analyze(text,client=SourceReplayClient(events),audit=False)
        self.assertEqual(len([r for r in out.records if r.kind=='decision']),2)

    def test_actual_assignment_conflict_never_silenced(self):
        text=('An: Cần kiểm thử tải API trước đợt demo.\n'
              'Lan: Tôi nhận kiểm thử tải API.\n'
              'Bình: Hay chọn thứ Ba?\n'
              'An: Chưa chọn thứ Ba và chưa giao việc kiểm thử tải API cho ai.')
        events=[
            ev('load_req','request','request_made','L001',
               'Cần kiểm thử tải API trước đợt demo','kiểm thử tải API'),
            Event(issue_key='load_task',topic='kiểm thử tải API',kind='action',
                  event_type='assignment',source_ids=['L002'],
                  value='kiểm thử tải API',owner='Lan').model_dump(),
            ev('date_choice','decision','unresolved','L004',
               'chưa chọn thứ Ba','lịch kiểm thử tải API'),
            ev('owner_echo','decision','unresolved','L004',
               'chưa giao việc kiểm thử tải API cho ai','phân công kiểm thử tải API')
        ]
        out=analyze(text,client=SourceReplayClient(events),audit=False)
        self.assertEqual(len([r for r in out.records if r.kind=='decision']),2)
        self.assertTrue(any(r.kind=='action' and r.owner=='Lan' for r in out.records))

    def test_standalone_nonassignment_must_remain_reviewable(self):
        text='An: Chưa giao việc rà soát hợp đồng cho ai.'
        out=analyze(text,client=SourceReplayClient([
            ev('contract_unassigned','decision','unresolved','L001',
               'chưa giao việc rà soát hợp đồng cho ai','rà soát hợp đồng')
        ]),audit=False)
        self.assertEqual(len(out.records),1)
        self.assertEqual(out.records[0].meeting_status,'open')

if __name__=='__main__':
    unittest.main()

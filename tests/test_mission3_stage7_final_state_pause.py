"""Final-State Reliability Stage 7A: source-grounded action pause/resume.

Replays original LONG01 Groq output exactly; no replacement of archived evidence.
"""
import json
import unittest
from pathlib import Path

from meeting_intelligence.models import Event
from meeting_intelligence.pipeline import analyze

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = json.loads((ROOT / "docs/evaluation/mission3/m3_stage4_LONG01_run1.json").read_text(encoding="utf8"))["cases"][0]
ORIGINAL_EVENTS = ARCHIVE["llm_responses"][0]["response"]["events"]
TRANSCRIPT = "\n".join(f"{u['speaker']}: {u['text']}" for u in ARCHIVE["output"]["utterances"])

class Stub:
    def __init__(self, events):
        self.events = events
        self.calls = 0
    def completion_json(self,*args,**kwargs):
        self.calls += 1
        return {"events":self.events} if self.calls==1 else {"findings":[]}

def event(typ,sid,*,key="price_table",topic="chuẩn bị bảng giá",owner=None,due=None,clear=None,kind="action",value=None):
    return Event(issue_key=key,topic=topic,kind=kind,event_type=typ,source_ids=[sid],
                 value=value,owner=owner,due_raw=due,clear_fields=clear or []).model_dump()

class FinalStatePauseTests(unittest.TestCase):
    def test_original_long01_groq_event_replay_pauses_mai(self):
        result=analyze(TRANSCRIPT,client=Stub(ORIGINAL_EVENTS),audit=False)
        tasks=[r for r in result.records if r.kind=="action" and r.owner=="Mai"]
        self.assertEqual(len(tasks),1)
        record=tasks[0]
        self.assertEqual(record.meeting_status,"paused")
        self.assertEqual(record.execution_status,"blocked")
        self.assertIsNone(record.due_raw)
        self.assertEqual(record.field_evidence_ids["meeting_status"],["L018"])
        self.assertEqual(record.field_evidence_ids["execution_status"],["L018"])
        self.assertIn("L018",record.counter_evidence_ids)
        self.assertEqual(record.history[-1].event_type,"action_paused")
        self.assertEqual(record.review_status,"needs_review")

    def test_due_removed_without_pausing_keeps_assignment(self):
        lines="Mai: Tôi nhận chuẩn bị bảng giá thứ Hai.\nAn: Bỏ deadline thứ Hai; công việc vẫn tiếp tục."
        events=[event("assignment","L001",owner="Mai",due="thứ Hai",value="chuẩn bị bảng giá"),
                event("deadline_change","L002",clear=["due_raw"])]
        record=next(r for r in analyze(lines,client=Stub(events),audit=False).records if r.kind=="action")
        self.assertEqual(record.meeting_status,"assigned")
        self.assertIsNone(record.due_raw)
        self.assertNotEqual(record.execution_status,"blocked")

    def test_pause_then_new_confirmed_assignment_resumes(self):
        lines=("Mai: Tôi nhận chuẩn bị bảng giá thứ Hai.\n"
               "An: Tạm dừng việc chuẩn bị bảng giá, hủy deadline thứ Hai.\n"
               "An: Mai tiếp tục chuẩn bị bảng giá trước thứ Sáu.\n"
               "Mai: Tôi nhận tiếp tục chuẩn bị bảng giá trước thứ Sáu.")
        events=[event("assignment","L001",owner="Mai",due="thứ Hai",value="chuẩn bị bảng giá"),
                event("deadline_change","L002",clear=["due_raw"]),
                event("assignment","L004",owner="Mai",due="trước thứ Sáu",value="chuẩn bị bảng giá")]
        record=next(r for r in analyze(lines,client=Stub(events),audit=False).records if r.kind=="action")
        self.assertEqual(record.meeting_status,"assigned")
        self.assertNotEqual(record.execution_status,"blocked")
        self.assertEqual(record.due_raw,"trước thứ Sáu")

    def test_unrelated_work_pause_does_not_affect_other_task(self):
        lines=("Mai: Tôi nhận chuẩn bị bảng giá thứ Hai.\n"
               "An: Tạm dừng việc triển khai giao diện, bỏ deadline thứ Hai.")
        events=[event("assignment","L001",owner="Mai",due="thứ Hai",value="chuẩn bị bảng giá"),
                event("deadline_change","L002",clear=["due_raw"])]
        record=next(r for r in analyze(lines,client=Stub(events),audit=False).records if r.kind=="action")
        self.assertEqual(record.meeting_status,"assigned")

    def test_hypothetical_pause_does_not_change_active_task(self):
        lines=("Mai: Tôi nhận chuẩn bị bảng giá thứ Hai.\n"
               "An: Nếu tạm dừng việc chuẩn bị bảng giá thì sẽ lỡ tiến độ; chưa quyết định tạm dừng.")
        events=[event("assignment","L001",owner="Mai",due="thứ Hai",value="chuẩn bị bảng giá"),
                event("deadline_change","L002")]
        record=next(r for r in analyze(lines,client=Stub(events),audit=False).records if r.kind=="action")
        self.assertEqual(record.meeting_status,"assigned")

    def test_cancelled_action_stays_cancelled_not_paused(self):
        lines=("Mai: Tôi nhận chuẩn bị bảng giá thứ Hai.\n"
               "An: Hủy việc chuẩn bị bảng giá, bỏ hạn thứ Hai.")
        events=[event("assignment","L001",owner="Mai",due="thứ Hai",value="chuẩn bị bảng giá"),
                event("action_cancelled","L002",clear=["due_raw"])]
        record=next(r for r in analyze(lines,client=Stub(events),audit=False).records if r.kind=="action")
        self.assertEqual(record.meeting_status,"cancelled")
        self.assertIsNone(record.due_raw)
        self.assertEqual(record.owner,"Mai")

if __name__=="__main__":
    unittest.main()

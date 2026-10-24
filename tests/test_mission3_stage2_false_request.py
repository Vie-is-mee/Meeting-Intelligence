"""Stage 2: do not promote a rejected deadline proposal into a request."""
import json
import unittest
from pathlib import Path
from meeting_intelligence.pipeline import analyze
from meeting_intelligence.models import Event

ROOT=Path(__file__).resolve().parents[1]
RUN=json.loads((ROOT/"docs/evaluation/mission3/m3_stage1c_C201_C202_013aa5b_run1.json").read_text(encoding="utf-8"))
CASE=next(c for c in RUN["cases"] if c["id"]=="C2-02")
TRANSCRIPT="\n".join(f"{u['speaker']}: {u['text']}" for u in CASE["output"]["utterances"])

class Replay:
    def __init__(self,events):
        self.events=events
        self.calls=0
    def completion_json(self,*args,**kwargs):
        self.calls+=1
        return {"events":self.events} if self.calls==1 else {"findings":[]}

def event(key,kind,etype,source,value):
    return Event(issue_key=key,kind=kind,event_type=etype,source_ids=[source],
                 topic="xử lý lỗi thanh toán",value=value).model_dump()

class GuardTests(unittest.TestCase):
    def test_real_groq_c202_replay_suppresses_uncommitted_friday_request(self):
        events=CASE["llm_responses"][0]["response"]["events"]
        res=analyze(TRANSCRIPT,client=Replay(events),audit=False)
        self.assertFalse(any(x.kind=="request" and x.meeting_status=="recorded" for x in res.records))
        self.assertFalse(any(x.kind=="action" and x.owner is not None for x in res.records))
        self.assertTrue(any(x.kind=="action" and x.meeting_status=="unverified" for x in res.records))
        self.assertTrue(any("Stage 2" in s and "L003" in s for s in res.warnings))
    def test_real_request_without_rejection_kept(self):
        text="Chi: Hay để thứ Sáu xử lý xong được không?\nMinh: Tôi ghi nhận yêu cầu hoàn thành vào thứ Sáu."
        out=analyze(text,client=Replay([event("task","request","request_made","L001","Xử lý xong thứ Sáu")]),audit=False)
        self.assertEqual(len([r for r in out.records if r.kind=="request"]),1)
    def test_explicit_deadline_request_kept(self):
        text="Chi: Yêu cầu hoàn thành vào thứ Sáu.\nMinh: Chưa chốt hạn của phần kiểm thử khác."
        out=analyze(text,client=Replay([event("task","request","request_made","L001","Hoàn thành thứ Sáu")]),audit=False)
        self.assertEqual(len([r for r in out.records if r.kind=="request"]),1)
    def test_no_unrelated_late_denial_suppresses(self):
        text="Chi: Hay để thứ Sáu xử lý xong được không?\nMinh: Chưa chốt ý tưởng thiết kế."
        out=analyze(text,client=Replay([event("task","request","request_made","L001","Xử lý xong thứ Sáu")]),audit=False)
        self.assertEqual(len([r for r in out.records if r.kind=="request"]),1)

if __name__=="__main__":
    unittest.main()

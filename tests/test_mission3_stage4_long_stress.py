"""Long-meeting stress: replay original Groq events and false-commitment negatives."""
import json
import unittest
from pathlib import Path
from meeting_intelligence.pipeline import analyze
from meeting_intelligence.models import Event

ROOT=Path(__file__).resolve().parents[1]
FILE=ROOT/"docs/evaluation/mission3/m3_stage4_LONG02_run1.json"
RUN=json.loads(FILE.read_text(encoding="utf8"))["cases"][0]
TRANSCRIPT="\n".join(f"{u['speaker']}: {u['text']}" for u in RUN["output"]["utterances"])

class Stub:
    def __init__(self,events):self.events=events;self.n=0
    def completion_json(self,*args,**kwargs):
        self.n+=1
        return {"events":self.events} if self.n==1 else {"findings":[]}

class StressTest(unittest.TestCase):
    def test_long02_replayed_tentative_requests_are_not_recorded(self):
        events=RUN["llm_responses"][0]["response"]["events"]
        out=analyze(TRANSCRIPT,client=Stub(events),audit=False)
        requests=[x for x in out.records if x.kind=="request"]
        self.assertFalse(any("giao Huy kiểm thử API" in (x.content or "") for x in requests))
        self.assertFalse(any("team mình xem" in (x.content or "") for x in requests))
        self.assertTrue(any(x.kind=="decision" and x.meeting_status=="reopened" for x in out.records))
        self.assertTrue(any(x.kind=="action" and x.owner=="Huy" for x in out.records))
        self.assertTrue(any("Stage 2" in x for x in out.warnings))

    def test_confirmed_collective_request_is_preserved(self):
        text=("Lan: Để team mình xem phần lỗi thanh toán nhé.\n"
              "Huy: Tôi đồng ý và xác nhận yêu cầu team xem phần lỗi thanh toán.")
        event=Event(issue_key="review",topic="kiểm tra thanh toán",kind="request",
            event_type="request_made",source_ids=["L001","L002"],
            value="Team xem phần lỗi thanh toán").model_dump()
        out=analyze(text,client=Stub([event]),audit=False)
        self.assertTrue(any(x.kind=="request" and x.meeting_status=="recorded" for x in out.records))

    def test_unrelated_denial_must_not_suppress_team_request(self):
        text=("Lan: Để team mình xem phần lỗi thanh toán nhé.\n"
              "An: Chưa phân công người kiểm thử kết nối mạng.")
        event=Event(issue_key="review",topic="kiểm tra thanh toán",kind="request",
            event_type="request_made",source_ids=["L001"],
            value="Team xem phần lỗi thanh toán").model_dump()
        out=analyze(text,client=Stub([event]),audit=False)
        self.assertTrue(any(x.kind=="request" and x.meeting_status=="recorded" for x in out.records))

if __name__=="__main__":unittest.main()

"""Stage 7B: source-constrained incident completeness, preserving distinct assigned action."""
import json
import unittest
from pathlib import Path
from meeting_intelligence.pipeline import analyze
from meeting_intelligence.models import Event

ROOT=Path(__file__).resolve().parents[1]
CASE=json.loads((ROOT/"docs/evaluation/mission3/m3_stage7_long01_live_candidate_run1.json").read_text(encoding="utf8"))["cases"][0]
ARCHIVED=CASE["llm_responses"][0]["response"]["events"]
TRANSCRIPT="\n".join(f"{u['speaker']}: {u['text']}" for u in CASE["output"]["utterances"])

class Replay:
    def __init__(self,events):self.events=events;self.calls=0
    def completion_json(self,*args,**kwargs):
        self.calls+=1
        return {"events":self.events} if self.calls==1 else {"findings":[]}

def evt(kind,typ,source,value,topic="lỗi thanh toán"):
    return Event(kind=kind,event_type=typ,issue_key="issue_custom",topic=topic,source_ids=[source],value=value).model_dump()

class IncidentCompletenessTests(unittest.TestCase):
    def test_long01_archived_extraction_recovers_payment_incident(self):
        result=analyze(TRANSCRIPT,client=Replay(ARCHIVED),audit=False)
        issues=[r for r in result.records if r.kind=="issue" and r.meeting_status=="open"
                and "thanh toán" in (r.content or "").casefold()]
        self.assertEqual(len(issues),1)
        self.assertIn("L005",issues[0].evidence_ids)
        self.assertEqual(issues[0].review_status,"needs_review")
        self.assertTrue(any("Bổ sung vướng mắc" in w for w in result.warnings))
        self.assertTrue(any(r.kind=="action" and r.owner=="Huy" for r in result.records))

    def test_existing_issue_does_not_duplicate(self):
        text="Lan: Có lỗi thanh toán làm khách bị trừ hai lần."
        extracted=[evt("issue","issue_reported","L001","Có lỗi thanh toán làm khách bị trừ hai lần.")]
        result=analyze(text,client=Replay(extracted),audit=False)
        self.assertEqual(len([r for r in result.records if r.kind=="issue"]),1)

    def test_unrelated_issue_kept_distinct(self):
        text=("Lan: Có lỗi thanh toán làm khách bị trừ hai lần.\n"
              "Bình: Có lỗi xác thực khiến người dùng không đăng nhập được.")
        extracted=[evt("issue","issue_reported","L002",
                       "Có lỗi xác thực khiến người dùng không đăng nhập được.", "lỗi xác thực")]
        result=analyze(text,client=Replay(extracted),audit=False)
        self.assertEqual(len([r for r in result.records if r.kind=="issue"]),2)

    def test_historical_and_hypothetical_and_negated_not_recovered(self):
        lines=[
            "Lan: Nếu có lỗi thanh toán làm khách bị trừ hai lần thì sao?",
            "Bình: Không có lỗi thanh toán làm khách bị trừ hai lần.",
            "Chi: Cuộc họp trước từng báo có lỗi thanh toán làm khách bị trừ hai lần.",
            "Mai: Ví dụ: Có lỗi thanh toán làm khách bị trừ hai lần."
        ]
        for line in lines:
            with self.subTest(line=line):
                result=analyze(line,client=Replay([]),audit=False)
                self.assertFalse(any(r.kind=="issue" for r in result.records))

    def test_customer_request_not_retyped_as_incident(self):
        text="Lan: Khách hàng yêu cầu sửa lỗi thanh toán bị trừ tiền hai lần."
        result=analyze(text,client=Replay([]),audit=False)
        self.assertFalse(any(r.kind=="issue" for r in result.records))
        self.assertTrue(any(r.kind=="request" for r in result.records))

    def test_resolved_incident_not_reintroduced_as_open_without_review(self):
        text=("Lan: Có lỗi thanh toán làm khách bị trừ hai lần.\n"
              "Huy: Đã sửa xong lỗi thanh toán bị trừ hai lần.")
        # A source-grounded reported-resolution event is authoritative on current
        # issue state and should prevent a second fabricated open issue.
        extracted=[evt("issue","issue_reported_resolved","L002",
                       "Đã sửa xong lỗi thanh toán bị trừ hai lần.")]
        result=analyze(text,client=Replay(extracted),audit=False)
        self.assertFalse(any(r.kind=="issue" and r.meeting_status=="open" for r in result.records))

if __name__=="__main__":unittest.main()

"""Stage 3 information-utility: conservative labels, provenance, and review safety.

These tests use manually frozen hypotheses / archived provider outputs. They
DO NOT constitute fresh M3 LLM accuracy metrics or independently reviewed gold.
"""
from __future__ import annotations
import json
import unittest
from pathlib import Path
from pydantic import ValidationError

from meeting_intelligence.information_utility import classify_information_utility
from meeting_intelligence.models import ResultRecord
from meeting_intelligence.parser import parse_transcript
from meeting_intelligence.pipeline import analyze

ROOT=Path(__file__).resolve().parents[1]


def rec(*, kind="knowledge", content="test", status="unverified", key="test",
        topic="quy trình", sources=("L001",)):
    return ResultRecord(issue_key=key,topic=topic,kind=kind,
        content=content,meeting_status=status,evidence_ids=list(sources),
        field_evidence_ids={"content":list(sources)})


def single(transcript,record):
    records=classify_information_utility([record],parse_transcript(transcript))
    return records[0]


class KnowledgeUtilityTests(unittest.TestCase):
    def test_reusable_technique_still_unverified_and_requires_review(self):
        text="L001 | Bình | Khi retry request, cần dùng idempotency key để hạn chế ghi trùng. Đây là kinh nghiệm từ lần triển khai trước."
        r=single(text,rec(content="Khi retry request, cần dùng idempotency key để hạn chế ghi trùng."))
        self.assertEqual(r.information_utility,"reusable_candidate")
        self.assertEqual(r.meeting_status,"unverified")
        self.assertEqual(r.review_status,"needs_review")
        self.assertEqual(r.authority_status,"unknown")
        self.assertIn("L001",r.field_evidence_ids["information_utility"])
        self.assertIn("CHƯA",r.information_utility_note)

    def test_unverified_rumor_is_not_approved_knowledge(self):
        text="L001 | Chi | Tôi nghe nói thư viện Y luôn nhanh hơn X, nhưng chưa có benchmark xác minh."
        r=single(text,rec(content="Tôi nghe nói thư viện Y luôn nhanh hơn X."))
        self.assertEqual(r.information_utility,"needs_verification")
        self.assertEqual(r.review_status,"needs_review")
        self.assertEqual(r.authority_status,"unknown")

    def test_past_tech_stack_not_confused_with_reusable_practice(self):
        text="L001 | Bình | Trước đây nhóm dùng MongoDB cho dự án A."
        r=single(text,rec(content="Trước đây nhóm dùng MongoDB cho dự án A."))
        self.assertEqual(r.information_utility,"historical_context")
        self.assertEqual(r.meeting_status,"unverified")

    def test_old_minutes_quoted_policy_not_current_practice(self):
        text="L001 | Bình | Biên bản cũ ghi cần dùng thư viện Y cho toàn bộ dự án."
        r=single(text,rec(content="Biên bản cũ ghi cần dùng thư viện Y cho toàn bộ dự án."))
        self.assertEqual(r.information_utility,"historical_context")

    def test_uncertain_claim_with_imperative_not_reusable(self):
        text="L001 | Bình | Tôi nghe nói cần dùng X để tăng hiệu năng nhưng chưa kiểm chứng."
        r=single(text,rec(content="Cần dùng X để tăng hiệu năng."))
        self.assertEqual(r.information_utility,"needs_verification")

    def test_practical_hypothesis_not_reusable(self):
        text="L001 | Bình | Giả sử mình cần dùng model B thì có thể hiệu quả hơn."
        r=single(text,rec(content="Cần dùng model B để cải thiện."))
        self.assertEqual(r.information_utility,"needs_verification")

    def test_unmarked_assertion_not_automatically_approved(self):
        text="L001 | Bình | MongoDB xử lý mọi truy vấn nhanh nhất."
        r=single(text,rec(content="MongoDB xử lý mọi truy vấn nhanh nhất."))
        self.assertEqual(r.information_utility,"needs_verification")

    def test_late_source_grounded_counterevidence_blocks_candidate(self):
        text=("L001 | Bình | Khi retry request, cần dùng idempotency key để hạn chế ghi trùng.\n"
              "L002 | Chi | Quy tắc retry request dùng idempotency key này không đúng, cần xem lại.")
        r=single(text,rec(content="Khi retry request, cần dùng idempotency key.",
                          topic="retry request"))
        self.assertEqual(r.information_utility,"needs_verification")
        self.assertIn("L002",r.counter_evidence_ids)
        self.assertIn("L002",r.field_evidence_ids["information_utility"])
        self.assertEqual(r.review_status,"needs_review")

    def test_unrelated_late_disproof_does_not_overwrite_knowledge(self):
        text=("L001 | Bình | Khi retry request, cần dùng idempotency key để hạn chế ghi trùng.\n"
              "L002 | Chi | Tên nhà cung cấp dịch vụ chưa đúng, cần xác minh.")
        r=single(text,rec(content="Khi retry request, cần dùng idempotency key."))
        self.assertEqual(r.information_utility,"reusable_candidate")
        self.assertNotIn("L002",r.counter_evidence_ids)

    def test_missing_cited_source_is_not_knowledge_candidate(self):
        text="L001 | Bình | Khi retry request, cần dùng idempotency key."
        r=single(text,rec(content="Khi retry request, cần dùng idempotency key.",
                          sources=("L999",)))
        self.assertEqual(r.information_utility,"needs_verification")
        self.assertEqual(r.field_evidence_ids["information_utility"],[])

    def test_missing_content_is_not_reusable(self):
        text="L001 | Bình | Khi retry request, cần dùng idempotency key."
        r=single(text,rec(content=None))
        self.assertEqual(r.information_utility,"needs_verification")

    def test_reviews_stay_unapproved_even_when_input_marked_reviewed(self):
        text="L001 | Bình | Khi retry request, cần dùng idempotency key."
        prior=rec(content="Khi retry request, cần dùng idempotency key.")
        prior.review_status="reviewed"
        prior.authority_status="verified"
        r=single(text,prior)
        self.assertEqual(r.review_status,"needs_review")
        self.assertEqual(r.authority_status,"unknown")


class WorkflowUtilityTests(unittest.TestCase):
    def test_assigned_task_is_current_work(self):
        r=single("L001 | Lan | Tôi nhận kiểm thử.",rec(kind="action",status="assigned",
                 content="Lan kiểm thử"))
        self.assertEqual(r.information_utility,"current_work")

    def test_cancelled_task_is_historical(self):
        r=single("L001 | Lan | Tôi hủy kiểm thử.",rec(kind="action",status="cancelled",
                 content="kiểm thử"))
        self.assertEqual(r.information_utility,"historical_context")

    def test_cancelled_task_utility_links_final_cancel_source(self):
        from meeting_intelligence.models import Event
        from meeting_intelligence.resolver import resolve_events
        lines=parse_transcript("L001 | An | Giao Lan thử thư viện X.\n"
                               "L002 | An | Hủy công việc thử thư viện X.")
        events=[
            Event(issue_key="trial",topic="thử X",kind="action",event_type="assignment",
                  source_ids=["L001"],value="thử thư viện X",owner="Lan"),
            Event(issue_key="trial",topic="thử X",kind="action",event_type="action_cancelled",
                  source_ids=["L002"]),
        ]
        r=classify_information_utility(resolve_events(events,lines),lines)[0]
        self.assertEqual(r.information_utility,"historical_context")
        self.assertIn("L002",r.field_evidence_ids["information_utility"])
        self.assertEqual(r.authority_status,"unknown")

    def test_withdrawn_decision_is_historical(self):
        r=single("L001 | Lan | Rút quyết định X.",rec(kind="decision",status="withdrawn",
                 content="X"))
        self.assertEqual(r.information_utility,"historical_context")

    def test_unresolved_vendor_decision_is_current_issue_not_approved(self):
        r=single("L001 | Lan | Chưa chọn nhà cung cấp.",rec(kind="decision",status="open",
                 content="chưa chọn nhà cung cấp"))
        self.assertEqual(r.information_utility,"current_work")
        self.assertEqual(r.authority_status,"unknown")

    def test_unverified_active_decision_needs_verification(self):
        r=single("L001 | Lan | Chọn phương án X?",rec(kind="decision",status="unverified",
                 content="phương án X"))
        self.assertEqual(r.information_utility,"needs_verification")

    def test_recorded_feedback_does_not_become_technical_knowledge(self):
        r=single("L001 | Lan | Giao diện đang lag.",rec(kind="feedback",status="recorded",
                 content="Giao diện lag"))
        self.assertEqual(r.information_utility,"current_work")
        self.assertNotEqual(r.kind,"knowledge")

    def test_pydantic_backward_compatibility(self):
        payload=rec().model_dump()
        payload.pop("information_utility")
        payload.pop("information_utility_note")
        result=ResultRecord.model_validate(payload)
        self.assertIsNone(result.information_utility)
        self.assertIsNone(result.information_utility_note)

    def test_invalid_utility_enum_rejected(self):
        with self.assertRaises(ValidationError):
            ResultRecord(issue_key="x",kind="knowledge",topic="x",content="x",
                         meeting_status="unverified",information_utility="verified_fact")


class Stage3ArchivedM2ReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path=ROOT/"docs/evaluation/mission3/m2_remote_baseline_v1.json"
        data=json.loads(path.read_text(encoding="utf-8"))
        cls.archive={r["id"]:r for r in data["results"]}
        dataset=json.loads((ROOT/"datasets/mission3_before_after_v1.json").read_text(encoding="utf-8"))
        cls.transcripts={r["id"]:r["transcript"] for r in dataset["cases"]}

    def replay(self,cid):
        archive=self.archive[cid]["output"]
        events=[]
        seen=set()
        for record in archive["records"]:
            for event in record["history"]:
                fingerprint=json.dumps(event,sort_keys=True,ensure_ascii=False)
                if fingerprint not in seen:
                    seen.add(fingerprint)
                    events.append(event)
        class ArchivedClient:
            def __init__(self, events):self.events=events;self.n=0
            def completion_json(self,*_):
                self.n+=1
                return {"events":self.events} if self.n==1 else {"findings":[]}
        return analyze(self.transcripts[cid],client=ArchivedClient(events),audit=True)

    def test_m3_k01_distinguishes_reusable_candidate_and_rumor(self):
        result=self.replay("M3-K01")
        knowledge=[r for r in result.records if r.kind=="knowledge"]
        self.assertEqual(len(knowledge),2)
        candidate=[r for r in knowledge if "idempotency" in (r.content or "").lower()]
        rumor=[r for r in knowledge if "nhanh" in (r.content or "").lower()]
        self.assertEqual(len(candidate),1)
        self.assertEqual(len(rumor),1)
        self.assertEqual(candidate[0].information_utility,"reusable_candidate")
        self.assertEqual(rumor[0].information_utility,"needs_verification")
        self.assertTrue(all(x.review_status=="needs_review" and x.authority_status=="unknown"
                            for x in knowledge))
        self.assertTrue(any(r.kind=="decision" and r.meeting_status=="open" and
                            r.information_utility=="current_work" for r in result.records))

    def test_m3_e01_e02_r01_not_changed_by_knowledge_classifier(self):
        for cid in ["M3-E01","M3-E02","M3-R01"]:
            with self.subTest(case=cid):
                actual=self.replay(cid)
                original=self.archive[cid]["output"]
                # A later Stage 3.5 recovery adds the explicit open alternative
                # in E01; preserve original correct rows and allow that new one.
                self.assertEqual(len(actual.records),len(original["records"])+(cid=="M3-E01"))
                if cid=="M3-E01":
                    self.assertTrue(any(r.kind=="decision" and r.meeting_status=="open"
                                        for r in actual.records))
                self.assertTrue(all(r.information_utility in {
                    "current_work","historical_context","needs_verification"}
                    for r in actual.records))
                self.assertTrue(all(r.authority_status=="unknown" for r in actual.records))


if __name__=="__main__":
    unittest.main()

"""Mission 3 Stage 1: positive/negative controls plus saved-M2-event replay.

No API: tests demonstrate deterministic guards on given LLM event hypotheses,
not newly generated M3 semantic accuracy.
"""
import json
import unittest
from pathlib import Path
from meeting_intelligence.auditor import audit_events, apply_audit_findings
from meeting_intelligence.extractor import extract_events
from meeting_intelligence.models import Event
from meeting_intelligence.parser import parse_transcript
from meeting_intelligence.pipeline import analyze
from meeting_intelligence.resolver import resolve_events
from meeting_intelligence.verifier import verify_records

ROOT = Path(__file__).resolve().parents[1]


def one(kind, event_type, source_ids, value, issue_key="architecture", topic="kho dữ liệu", **kwargs):
    return Event(kind=kind,event_type=event_type,source_ids=source_ids,
                 value=value,issue_key=issue_key,topic=topic,**kwargs)


class AuditClient:
    def __init__(self, findings):
        self.findings = findings
    def completion_json(self, system, user):
        return {"findings":self.findings}


class ExtractorClient:
    def __init__(self, events):
        self.events = events
    def completion_json(self, system, user):
        return {"events":self.events}


class Stage1SourceScopeTests(unittest.TestCase):
    def test_unrelated_vendor_negation_does_not_hold_architecture(self):
        utt=parse_transcript("L001 | Bình | Thống nhất phương án B cho bản thử nghiệm.\n"
                             "L002 | An | Chưa chốt nhà cung cấp B.")
        rows=verify_records(resolve_events([one("decision","agreement",["L001"],
                                                "phương án B cho bản thử nghiệm")],utt),utt)
        self.assertEqual(rows[0].meeting_status,"agreed")
        self.assertEqual(rows[0].review_status,"unreviewed")
        self.assertFalse(any("Có câu phủ định sau" in s for s in rows[0].warnings))

    def test_same_topic_late_negation_is_flagged(self):
        utt=parse_transcript("L001 | Bình | Thống nhất phương án B cho bản thử nghiệm.\n"
                             "L002 | An | Hôm nay chưa chốt phương án B cho thử nghiệm.")
        rows=verify_records(resolve_events([one("decision","agreement",["L001"],
                                                "phương án B cho bản thử nghiệm")],utt),utt)
        self.assertEqual(rows[0].meeting_status,"agreed")
        self.assertEqual(rows[0].review_status,"needs_review")
        self.assertTrue(any("L002" in s and "phủ định" in s for s in rows[0].warnings))

    def test_other_topic_fair_same_word_does_not_trigger(self):
        utt=parse_transcript("L001 | Bình | Chốt thử nghiệm hiệu năng gói A.\n"
                             "L002 | Chi | Chưa chốt lịch chạy thử nghiệm hiệu năng gói B.")
        rows=verify_records(resolve_events([one("decision","agreement",["L001"],
                                                "thử nghiệm hiệu năng gói A", topic="benchmark")],utt),utt)
        # Named different package B does not negate previously selected A.
        self.assertEqual(rows[0].meeting_status,"agreed")
        self.assertEqual(rows[0].review_status,"unreviewed")


class Stage1AuditorTests(unittest.TestCase):
    def test_cancellation_reason_condition_false_finding_is_rejected(self):
        utt=parse_transcript("L001 | Bình | Giao Lan thử thư viện X.\n"
                             "L002 | An | Hủy công việc thử thư viện X vì giấy phép không phù hợp.")
        events=[one("action","assignment",["L001"],"thử thư viện X",
                    issue_key="libX",topic="thử thư viện",owner="Lan"),
                one("action","action_cancelled",["L002"],None,issue_key="libX",topic="thử thư viện")]
        records=verify_records(resolve_events(events,utt),utt)
        finding=dict(issue_key="libX",kind="action",category="missing_late_change",
                     severity="medium",source_ids=["L002"],
                     source_quote="Hủy công việc thử thư viện X vì giấy phép không phù hợp.",
                     explanation="condition field null but cancellation due to condition giấy phép không phù hợp")
        accepted, skipped=audit_events(utt,events,records,AuditClient([finding]))
        self.assertEqual(accepted,[])
        self.assertTrue(any("lý do hủy" in s for s in skipped))
        self.assertEqual(records[0].meeting_status,"cancelled")
        self.assertIsNone(records[0].condition)

    def test_real_missing_reopen_finding_is_preserved(self):
        utt=parse_transcript("L001 | Bình | Chốt dùng B.\nL002 | Bình | Hôm nay mở lại quyết định dùng B.")
        events=[one("decision","agreement",["L001"],"dùng B")]
        rows=resolve_events(events,utt)
        finding=dict(issue_key="architecture",kind="decision",category="missing_late_change",
                     severity="high",source_ids=["L002"],source_quote="Hôm nay mở lại quyết định dùng B.",
                     explanation="Omitted late reopen of B")
        accepted, skipped=audit_events(utt,events,rows,AuditClient([finding]))
        self.assertEqual(len(accepted),1)
        self.assertFalse(skipped)
        apply_audit_findings(rows,accepted)
        self.assertEqual(rows[0].meeting_status,"unverified")

    def test_cancelled_owner_history_false_warning_is_rejected(self):
        utt=parse_transcript("L001 | Bình | Giao Chi viết hướng dẫn.\n"
                             "L002 | Chi | Tôi nhận viết hướng dẫn.\n"
                             "L003 | Bình | Hủy việc viết hướng dẫn, bỏ hạn cũ.")
        events=[one("action","assignment",["L001"],"viết hướng dẫn",
                    issue_key="guide",topic="hướng dẫn",owner="Chi",due_raw="cuối ngày mai"),
                one("action","action_cancelled",["L003"],None,
                    issue_key="guide",topic="hướng dẫn",clear_fields=["due_raw"])]
        rows=verify_records(resolve_events(events,utt),utt)
        finding=dict(issue_key="guide",kind="action",category="missing_late_change",
                     severity="medium",source_ids=["L003"],
                     source_quote="Hủy việc viết hướng dẫn, bỏ hạn cũ.",
                     explanation="Cancellation clears due date but does not remove owner Chi; owner must be null")
        accepted, skipped=audit_events(utt,events,rows,AuditClient([finding]))
        self.assertEqual(accepted,[])
        self.assertTrue(any("người phụ trách lịch sử" in x for x in skipped))
        self.assertEqual(rows[0].owner,"Chi")

    def test_explicit_owner_clear_is_not_suppressed(self):
        utt=parse_transcript("L001 | Bình | Giao Chi viết hướng dẫn.\n"
                             "L002 | Bình | Hủy việc viết hướng dẫn và bỏ Chi khỏi vai trò phụ trách.")
        events=[one("action","assignment",["L001"],"viết hướng dẫn",
                    issue_key="guide",topic="hướng dẫn",owner="Chi"),
                one("action","action_cancelled",["L002"],None,
                    issue_key="guide",topic="hướng dẫn",clear_fields=["owner"])]
        rows=verify_records(resolve_events(events,utt),utt)
        finding=dict(issue_key="guide",kind="action",category="missing_late_change",
                     severity="medium",source_ids=["L002"],
                     source_quote="Hủy việc viết hướng dẫn và bỏ Chi khỏi vai trò phụ trách.",
                     explanation="The owner must be null after explicit remove owner instruction")
        accepted, _=audit_events(utt,events,rows,AuditClient([finding]))
        self.assertEqual(len(accepted),1)

    def test_missing_cancel_status_still_detected(self):
        utt=parse_transcript("L001 | Bình | Giao Lan thử thư viện X.\n"
                             "L002 | An | Hủy công việc thử thư viện X vì giấy phép không phù hợp.")
        events=[one("action","assignment",["L001"],"thử thư viện X",
                    issue_key="libX",topic="thử thư viện",owner="Lan")]
        records=resolve_events(events,utt)
        finding=dict(issue_key="libX",kind="action",category="missing_late_change",
                     severity="high",source_ids=["L002"],
                     source_quote="Hủy công việc thử thư viện X vì giấy phép không phù hợp.",
                     explanation="Missing cancellation; assigned action incorrectly active")
        accepted, skipped=audit_events(utt,events,records,AuditClient([finding]))
        self.assertEqual(len(accepted),1)
        self.assertFalse(skipped)


class Stage1ExtractorTests(unittest.TestCase):
    def test_explicit_no_choice_cited_as_proposal_becomes_open(self):
        utt=parse_transcript("L001 | An | Giữ việc benchmark cho buổi sau, hôm nay chưa chọn thư viện.")
        event=one("decision","proposal",["L001"],
                  "giữ benchmark cho buổi sau, hôm nay chưa chọn thư viện")
        warnings=[]
        events=extract_events(utt,ExtractorClient([event.model_dump()]),warnings=warnings)
        self.assertEqual(events[0].event_type,"unresolved")
        result=resolve_events(events,utt)[0]
        self.assertEqual(result.meeting_status,"open")
        self.assertTrue(warnings)

    def test_actual_proposal_not_collapsed_into_open(self):
        utt=parse_transcript("L001 | An | Tôi đề xuất chọn thư viện X.")
        event=one("decision","proposal",["L001"],"chọn thư viện X")
        events=extract_events(utt,ExtractorClient([event.model_dump()]))
        self.assertEqual(events[0].event_type,"proposal")

    def test_source_not_explicitly_unresolved_means_no_forced_change(self):
        utt=parse_transcript("L001 | An | Tôi đề xuất thử thư viện X.")
        event=one("decision","proposal",["L001"],"đề xuất X nhưng chưa chốt")
        events=extract_events(utt,ExtractorClient([event.model_dump()]))
        self.assertEqual(events[0].event_type,"proposal")


    def test_historical_LC01_duplicate_request_suppressed_without_task_loss(self):
        import json
        blob=json.loads((ROOT/"docs/evaluation/final_regression_round5_retry2.json").read_text(encoding="utf-8"))
        case=next(x for x in blob["cases"] if x["id"]=="LC01")
        hypotheses=[e for r in case["output"]["records"] for e in r["history"]]
        text="\n".join(f'{u["id"]} | {u.get("speaker") or ""} | {u["text"]}'
                       for u in case["output"]["utterances"])
        class Client:
            def __init__(self): self.calls=0
            def completion_json(self, system, user):
                self.calls+=1
                return {"events":hypotheses} if self.calls==1 else {"findings":[]}
        result=analyze(text,client=Client())
        self.assertEqual([(r.kind,r.meeting_status) for r in result.records],
                         [("action","cancelled")])
        self.assertTrue(any("Loại request trùng" in w for w in result.warnings))

    def test_same_source_independent_customer_requirement_retained(self):
        text=("L001 | Hà | Khách hàng yêu cầu Mai lập bảng đối soát.\n"
              "L002 | Mai | Tôi nhận việc lập bảng đối soát.\n"
              "L003 | Hà | Hủy việc lập bảng đối soát của Mai.")
        utt=parse_transcript(text)
        events=[one("request","request_made",["L001"],"lập bảng đối soát",
                    issue_key="report",topic="bảng đối soát"),
                one("action","assignment",["L002"],"lập bảng đối soát",
                    issue_key="report",topic="bảng đối soát",owner="Mai"),
                one("action","action_cancelled",["L003"],None,
                    issue_key="report",topic="bảng đối soát")]
        result=verify_records(resolve_events(events,utt),utt)
        self.assertEqual({r.kind for r in result},{"action","request"})

    def test_explicit_requirement_reaffirmed_after_cancellation_retained(self):
        text=("L001 | Hà | Mai lập bảng đối soát.\n"
              "L002 | Mai | Tôi nhận lập bảng đối soát.\n"
              "L003 | Hà | Hủy việc lập bảng đối soát.\n"
              "L004 | Hà | Khách hàng yêu cầu bảng đối soát vẫn phải có.")
        utt=parse_transcript(text)
        events=[one("request","request_made",["L001"],"lập bảng đối soát",
                    issue_key="report",topic="bảng đối soát"),
                one("action","assignment",["L002"],"lập bảng đối soát",
                    issue_key="report",topic="bảng đối soát",owner="Mai"),
                one("action","action_cancelled",["L003"],None,
                    issue_key="report",topic="bảng đối soát")]
        result=verify_records(resolve_events(events,utt),utt)
        self.assertEqual({r.kind for r in result},{"action","request"})


class SavedM2EventReplayTests(unittest.TestCase):
    """Re-execute *saved M2 hypotheses* through the improved M3 Python pipeline."""

    @classmethod
    def setUpClass(cls):
        p=ROOT/"docs/evaluation/mission3/m2_remote_baseline_v1.json"
        blob=json.loads(p.read_text(encoding="utf-8"))
        cls.cases={r["id"]:r for r in blob["results"]}
        cls.inputs={r["id"]:r["transcript"] for r in
                    json.loads((ROOT/"datasets/mission3_before_after_v1.json").read_text(encoding="utf-8"))["cases"]}

    def replay(self, cid):
        old=self.cases[cid]["output"]
        # Each record holds the history of its own distinct events; retain
        # unique event hypotheses without manufacturing an extraction output.
        hypotheses=[]
        seen=set()
        for record in old["records"]:
            for event in record["history"]:
                fingerprint=json.dumps(event,ensure_ascii=False,sort_keys=True)
                if fingerprint not in seen:
                    hypotheses.append(event)
                    seen.add(fingerprint)
        class Client:
            def __init__(self, events, findings):
                self.events=events
                self.findings=findings
                self.call=0
            def completion_json(self, system, user):
                self.call+=1
                return {"events":self.events} if self.call==1 else {"findings":self.findings}
        result=analyze(self.inputs[cid],client=Client(hypotheses,old["audit_findings"]))
        return result

    def test_E01_false_audit_is_rejected_without_losing_request(self):
        x=self.replay("M3-E01")
        self.assertEqual(len(x.audit_findings),0)
        # The explicit unresolved alternate method at L005 is now recovered.
        self.assertEqual(sorted((r.kind,r.meeting_status) for r in x.records),
                         [("action","cancelled"),("decision","open"),("request","recorded")])
        self.assertFalse(any("condition field null" in z for r in x.records for z in r.warnings))

    def test_E02_previous_good_cancellation_survives(self):
        x=self.replay("M3-E02")
        self.assertEqual(len(x.records),1)
        self.assertEqual(x.records[0].kind,"action")
        self.assertEqual(x.records[0].meeting_status,"cancelled")

    def test_R01_cross_issue_verifier_warning_disappears(self):
        x=self.replay("M3-R01")
        self.assertEqual(len(x.records),2)
        agreed=next(r for r in x.records if r.meeting_status=="agreed")
        self.assertEqual(agreed.execution_status,"blocked")
        self.assertFalse(any("Có câu phủ định sau" in z for z in agreed.warnings))

    def test_K01_no_choice_becomes_open(self):
        x=self.replay("M3-K01")
        self.assertTrue(any(r.kind=="decision" and r.meeting_status=="open" for r in x.records))
        self.assertTrue(any(r.kind=="action" and r.meeting_status=="assigned" for r in x.records))


if __name__ == "__main__":
    unittest.main()

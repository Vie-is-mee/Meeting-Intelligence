"""Real M3 run4 D01 regression: explicit deferred vendor choice is independent.

Replay actual provider event hypotheses + audit finding. No new LLM calls.
"""
import json
import unittest
from pathlib import Path
from meeting_intelligence.models import Event
from meeting_intelligence.pipeline import analyze
from meeting_intelligence.completeness import recover_explicit_omissions
from meeting_intelligence.parser import parse_transcript

ROOT=Path(__file__).resolve().parents[1]
RAW=json.loads((ROOT/"docs/evaluation/mission3/m3_fresh_regression_D01_c443647.json").read_text(encoding="utf-8"))
CASE=RAW["cases"][0]
FROZEN=json.loads((ROOT/"docs/evaluation/final_regression_input_v2.json").read_text(encoding="utf-8"))
TRANSCRIPT=next(x["transcript"] for x in FROZEN["cases"] if x["id"]=="D01")

def hypotheses():
    events=[]
    seen=set()
    for r in CASE["output"]["records"]:
        for e in r["history"]:
            j=json.dumps(e,sort_keys=True,ensure_ascii=False)
            if j not in seen:
                seen.add(j)
                events.append(e)
    return events

class Archived:
    def __init__(self):
        self.calls=0
    def completion_json(self,*a,**kw):
        self.calls+=1
        return {"events":hypotheses()} if self.calls==1 else {"findings":CASE["output"]["audit_findings"]}

class D01DeferredVendorRegressionTests(unittest.TestCase):
    def test_raw_m3_d01_deferred_vendor_is_open_not_storage_condition(self):
        result=analyze(TRANSCRIPT,client=Archived(),audit=True)
        self.assertEqual(sorted((r.kind,r.meeting_status) for r in result.records),
                         [("decision","agreed"),("decision","open")])
        vendor=next(r for r in result.records if r.meeting_status=="open")
        self.assertIn("nhà cung cấp",vendor.content.casefold())
        self.assertIn("L006",vendor.evidence_ids)
        self.assertIsNone(vendor.owner)
        self.assertIsNone(vendor.condition)
        self.assertEqual(vendor.review_status,"needs_review")
        self.assertEqual(result.audit_findings,[])
        self.assertTrue(any("nhà cung cấp" in w.casefold() for w in result.warnings))
        storage=next(r for r in result.records if r.meeting_status=="agreed")
        self.assertIsNone(storage.condition)

    def test_explicit_deferred_choice_alone_can_recover_open_review(self):
        lines=parse_transcript("L001 | Bình | Nhà cung cấp để cuộc họp sau chọn.")
        events,keys=recover_explicit_omissions([],lines,[])
        self.assertEqual(len(events),1)
        self.assertEqual(events[0].event_type,"unresolved")
        self.assertEqual(events[0].kind,"decision")
        self.assertEqual(events[0].source_ids,["L001"])
        self.assertTrue(keys)

    def test_same_source_storage_agreement_not_considered_vendor_record(self):
        lines=parse_transcript("L001 | Bình | Chốt object storage. Nhà cung cấp để cuộc họp sau chọn.")
        e=Event(kind="decision",event_type="agreement",issue_key="storage",
                topic="object storage",source_ids=["L001"],value="object storage")
        events,keys=recover_explicit_omissions([e],lines,[])
        self.assertEqual(len(events),2)
        self.assertEqual({x.event_type for x in events},{"agreement","unresolved"})
        self.assertTrue(keys)

    def test_agreed_storage_content_mentions_vendor_but_vendor_remains_open(self):
        lines=parse_transcript("L001 | An | Chốt object storage cho bản thử nghiệm. Nhà cung cấp để cuộc họp sau chọn.")
        e=Event(kind="decision",event_type="agreement",issue_key="storage_choice",
                topic="lưu tệp đính kèm bằng object storage",
                source_ids=["L001"],
                value="Dùng object storage cho bản thử nghiệm; nhà cung cấp để cuộc họp sau chọn")
        events,keys=recover_explicit_omissions([e],lines,[])
        self.assertEqual(len(events),2)
        self.assertEqual(sorted(x.event_type for x in events),["agreement","unresolved"])
        self.assertEqual(len(keys),1)

    def test_same_vendor_target_already_agreed_not_auto_reopened(self):
        lines=parse_transcript("L001 | An | Chốt nhà cung cấp B. Nhà cung cấp để cuộc họp sau chọn.")
        e=Event(kind="decision",event_type="agreement",issue_key="vendor",
                topic="nhà cung cấp",source_ids=["L001"],value="Chốt nhà cung cấp B")
        events,keys=recover_explicit_omissions([e],lines,[])
        self.assertEqual(len(events),1)
        self.assertFalse(keys)

    def test_dont_recover_if_vendor_already_explicitly_open(self):
        lines=parse_transcript("L001 | Bình | Nhà cung cấp để cuộc họp sau chọn.")
        e=Event(kind="decision",event_type="unresolved",issue_key="vendor",
                topic="nhà cung cấp",source_ids=["L001"],value="chưa chọn nhà cung cấp")
        events,keys=recover_explicit_omissions([e],lines,[])
        self.assertEqual(len(events),1)
        self.assertFalse(keys)

    def test_deferred_then_approved_same_utterance_needs_semantic_review(self):
        lines=parse_transcript("L001 | Bình | Nhà cung cấp để cuộc họp sau chọn, sau đó đã chốt Y.")
        events,keys=recover_explicit_omissions([],lines,[])
        self.assertEqual(events,[])
        self.assertFalse(keys)

if __name__=="__main__":
    unittest.main()

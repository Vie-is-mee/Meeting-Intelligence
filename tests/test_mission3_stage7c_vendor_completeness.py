"""Stage 7C: explicit vendor-choice still open must survive a long transcript."""
import json
import unittest
from pathlib import Path
from meeting_intelligence.models import Event
from meeting_intelligence.pipeline import analyze
from meeting_intelligence.parser import parse_transcript
from meeting_intelligence.completeness import recover_explicit_omissions

ROOT=Path(__file__).resolve().parents[1]
ARCH=json.loads((ROOT/"docs/evaluation/mission3/m3_stage7b_long01_live_run1.json").read_text(encoding="utf8"))["cases"][0]
TRANSCRIPT="\n".join(f"{u['speaker']}: {u['text']}" for u in ARCH["output"]["utterances"])

class Stub:
    def __init__(self,events): self.events=events
    def completion_json(self,*args,**kwargs): return {"events":self.events}

class VendorCompletenessTests(unittest.TestCase):
    def test_real_groq_long01_missing_vendor_is_recovered(self):
        events=ARCH["llm_responses"][0]["response"]["events"]
        result=analyze(TRANSCRIPT,client=Stub(events),audit=False)
        vendors=[r for r in result.records if r.kind=="decision" and
                 r.meeting_status=="open" and "nhà cung cấp" in (r.topic+" "+(r.content or "")).casefold()]
        self.assertEqual(len(vendors),1)
        self.assertEqual(vendors[0].review_status,"needs_review")
        self.assertIn("L011",vendors[0].evidence_ids)
        self.assertEqual(len([r for r in result.records if r.kind=="decision"
                              and r.meeting_status=="agreed"]),1)

    def test_existing_vendor_open_is_not_duplicated(self):
        source="An: Chốt object storage, còn nhà cung cấp chọn ở cuộc họp khác."
        lines=parse_transcript(source)
        items=[Event(kind="decision",event_type="unresolved",issue_key="vendor",
                     topic="nhà cung cấp",value="Chưa chốt nhà cung cấp",source_ids=["L001"])]
        got,keys=recover_explicit_omissions(items,lines,[])
        self.assertEqual(len([e for e in got if e.kind=="decision"]),1)
        self.assertFalse(keys)

    def test_already_agreed_vendor_not_reopened_by_ambiguous_old_mention(self):
        source=("An: Còn nhà cung cấp chọn ở cuộc họp khác.\n"
                "Chi: Chốt nhà cung cấp A rồi.")
        lines=parse_transcript(source)
        events=[Event(kind="decision",event_type="agreement",issue_key="vendor",
                      topic="nhà cung cấp",value="Chốt nhà cung cấp A",source_ids=["L002"])]
        got,_=recover_explicit_omissions(events,lines,[])
        self.assertEqual(len(got),1)

    def test_conclusion_vendor_still_open_alone_is_not_assignment(self):
        lines=parse_transcript("An: Kết luận: object storage đã chốt, nhà cung cấp còn mở, Huy vẫn làm thanh toán.")
        got,_=recover_explicit_omissions([],lines,[])
        vendor=[e for e in got if e.kind=="decision" and e.event_type=="unresolved"]
        self.assertEqual(len(vendor),1)
        self.assertEqual(vendor[0].source_ids,["L001"])
        self.assertIsNone(vendor[0].owner)

    def test_nonnormative_vendor_mention_does_not_create_choice(self):
        for sentence in ["Lan: Nhà cung cấp mở báo giá đến thứ Sáu.",
                         "Lan: Nếu nhà cung cấp còn mở thì sao?",
                         "Lan: Cuộc họp trước nói nhà cung cấp còn mở."]:
            with self.subTest(sentence=sentence):
                got,_=recover_explicit_omissions([],parse_transcript(sentence),[])
                self.assertFalse(any(e.kind=="decision" for e in got))

if __name__=="__main__":unittest.main()

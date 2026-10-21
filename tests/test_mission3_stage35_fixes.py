"""Round-1 live Groq failures → targeted deterministic regression controls.

The actual LLM output from M3 run1 is sealed separately. These tests replay its
event hypotheses and audit findings; they are NOT new provider calls.
"""
import json
import unittest
from pathlib import Path

from meeting_intelligence.pipeline import analyze
from meeting_intelligence.parser import parse_transcript
from meeting_intelligence.resolver import resolve_events
from meeting_intelligence.verifier import verify_records
from meeting_intelligence.models import Event

ROOT=Path(__file__).resolve().parents[1]
RUN=json.loads((ROOT/"docs/evaluation/mission3/m3_fresh_full_run1.json").read_text(encoding="utf-8"))
DATA=json.loads((ROOT/"datasets/mission3_before_after_v1.json").read_text(encoding="utf-8"))
ROWS={r["id"]:r for r in RUN["results"]}
TRANSCRIPTS={r["id"]:r["transcript"] for r in DATA["cases"]}

def provider_events(cid):
    history=[]
    seen=set()
    for record in ROWS[cid]["output"]["records"]:
        for e in record["history"]:
            key=json.dumps(e,ensure_ascii=False,sort_keys=True)
            if key not in seen:
                seen.add(key)
                history.append(e)
    return history

class ArchivedClient:
    def __init__(self,events,findings):
        self.events=events
        self.findings=findings
        self.calls=0
    def completion_json(self,*args,**kwargs):
        self.calls+=1
        return {"events":self.events} if self.calls==1 else {"findings":self.findings}

def replay(cid):
    output=ROWS[cid]["output"]
    return analyze(TRANSCRIPTS[cid],client=ArchivedClient(provider_events(cid),output["audit_findings"]),audit=True)


class Stage35LiveFailureTests(unittest.TestCase):
    def test_E01_named_direct_instruction_is_not_independent_proposal(self):
        result=replay("M3-E01")
        self.assertEqual(sorted((r.kind,r.meeting_status) for r in result.records),
                         [("action","cancelled"),("decision","open"),("request","recorded")])
        self.assertTrue(any("Loại proposal trùng" in w for w in result.warnings))

    def test_E01_separate_independently_sourced_proposal_must_survive(self):
        transcript=TRANSCRIPTS["M3-E01"]+"\nL006 | An | Tôi đề xuất thư viện Y cho chức năng khác."
        events=provider_events("M3-E01")
        events.append(Event(issue_key="distinct_library",topic="chức năng khác",
                            kind="decision",event_type="proposal",source_ids=["L006"],
                            value="thư viện Y cho chức năng khác").model_dump())
        class Client:
            def completion_json(self,*args,**kwargs):return {"events":events}
        result=analyze(transcript,client=Client(),audit=False)
        self.assertTrue(any(r.issue_key=="distinct_library" and r.kind=="decision"
                            and r.meeting_status=="proposed" for r in result.records))
        self.assertFalse(any(r.issue_key=="task_csv_libX" and r.kind=="decision" and
                             r.meeting_status=="proposed" for r in result.records))

    def test_R01_audit_cannot_claim_proposals_missing_if_in_history(self):
        result=replay("M3-R01")
        self.assertEqual(len(result.audit_findings),0)
        self.assertEqual(len(result.records),2)
        self.assertTrue(any(x.kind=="decision" and x.meeting_status=="agreed"
                            for x in result.records))
        self.assertTrue(any(x.kind=="decision" and x.meeting_status=="open"
                            for x in result.records))

    def test_R01_null_condition_preserves_historical_source(self):
        events=[Event.model_validate(e) for e in provider_events("M3-R01")]
        lines=parse_transcript(TRANSCRIPTS["M3-R01"])
        records=verify_records(resolve_events(events,lines),lines)
        vendor=next(r for r in records if r.issue_key=="supplier_choice")
        self.assertIsNone(vendor.condition)
        self.assertIn("L005",vendor.field_evidence_ids.get("condition",[]))
        self.assertTrue(any(e.event_type=="unresolved" and "L005" in e.source_ids for e in vendor.history))

    def test_R01_real_operative_condition_and_source_stay(self):
        events=[Event.model_validate(e) for e in provider_events("M3-R01")]
        lines=parse_transcript(TRANSCRIPTS["M3-R01"])
        records=verify_records(resolve_events(events,lines),lines)
        agreed=next(r for r in records if r.issue_key=="method_choice")
        self.assertIsNotNone(agreed.condition)
        self.assertIn("L004",agreed.field_evidence_ids.get("condition",[]))

    def test_E01_live_run2_issue_gets_normalized_and_unselected_option_recovered(self):
        run=json.loads((ROOT/"docs/evaluation/mission3/m3_fresh_E01_run2.json").read_text(encoding="utf-8"))
        raw=run["results"][0]["output"]
        seen=set()
        events=[]
        for record in raw["records"]:
            # Raw saved output includes a Stage 2 rule-recovered event;
            # replay only the provider-origin events to reproduce extraction.
            if record["issue_key"].startswith("m3_recovered_"):
                continue
            for e in record["history"]:
                key=json.dumps(e,ensure_ascii=False,sort_keys=True)
                if key not in seen:
                    seen.add(key)
                    events.append(e)
        class Client:
            def completion_json(self,*args,**kwargs):
                return {"events":events}
        result=analyze(TRANSCRIPTS["M3-E01"],client=Client(),audit=False)
        self.assertEqual(sorted((r.kind,r.meeting_status) for r in result.records),
                         [("action","cancelled"),("decision","open"),("request","recorded")])
        self.assertFalse(any(r.kind=="issue" for r in result.records))
        self.assertTrue(any(r.kind=="decision" and "L005" in r.evidence_ids
                            and r.review_status=="needs_review" for r in result.records))
        self.assertTrue(any("Chuẩn hóa issue" in w for w in result.warnings))

    def test_separate_issue_with_different_meaning_must_survive(self):
        from meeting_intelligence.completeness import recover_explicit_omissions
        lines=parse_transcript("L001 | An | Khách hàng yêu cầu xuất file CSV trong báo cáo.")
        prior=[Event(issue_key="csv_problem",kind="issue",topic="lỗi xuất CSV",
                     event_type="issue_reported",source_ids=["L001"],
                     value="CSV đang bị lỗi").model_dump()]
        events,keys=recover_explicit_omissions([Event.model_validate(x) for x in prior],lines,[])
        self.assertTrue(any(x.kind=="issue" for x in events))
        self.assertTrue(any(x.kind=="request" for x in events))
        self.assertTrue(keys)

    def test_suffix_open_must_not_override_later_confirmed_choice(self):
        from meeting_intelligence.completeness import recover_explicit_omissions
        lines=parse_transcript("L001 | An | Còn cách làm khác thì chưa chốt, sau đó đã chốt dùng Y.")
        events,keys=recover_explicit_omissions([],lines,[])
        self.assertEqual(events,[])
        self.assertFalse(keys)

if __name__=="__main__":
    unittest.main()

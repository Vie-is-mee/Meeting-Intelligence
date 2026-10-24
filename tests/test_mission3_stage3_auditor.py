"""Auditor's archived false-positive controls for historical cancellation."""
import json
import unittest
from pathlib import Path
from meeting_intelligence.models import ResultRecord, Utterance, Event
from meeting_intelligence.auditor import audit_events

ROOT=Path(__file__).resolve().parents[1]/"docs/evaluation/mission3"

def case(file,id):
    data=json.loads((ROOT/file).read_text(encoding="utf8"))
    return next(c for c in data["cases"] if c["id"]==id)

class AuditorReplay:
    def __init__(self, findings):self.findings=findings
    def completion_json(self,*a,**kw):return {"findings":self.findings}

def evaluate(c,findings=None,records=None,events_override=None):
    out=c["output"]
    utter=[Utterance.model_validate(x) for x in out["utterances"]]
    recs=[ResultRecord.model_validate(x) for x in (records if records is not None else out["records"])]
    events=[Event.model_validate(x) for x in (events_override if events_override is not None else c["llm_responses"][0]["response"]["events"])]
    return audit_events(utter,events,recs,AuditorReplay(findings if findings is not None else out["audit_findings"]))

class Stage3AuditorTests(unittest.TestCase):
    def test_lc01_cancel_and_due_clearing_are_not_missing(self):
        c=case("m3_stage1c_LC01_LC02_013aa5b_run1.json","LC01")
        accepted,ignored=evaluate(c)
        self.assertEqual(len(accepted),0)
        self.assertGreaterEqual(len(ignored),2)

    def test_lc03_historical_owner_is_not_deleted(self):
        c=case("m3_stage1c_LC03_013aa5b_run1.json","LC03")
        accepted,ignored=evaluate(c)
        self.assertEqual(len(accepted),0)
        self.assertGreaterEqual(len(ignored),1)

    def test_missing_cancel_event_is_still_reported(self):
        c=case("m3_stage1c_LC01_LC02_013aa5b_run1.json","LC01")
        records=json.loads(json.dumps(c["output"]["records"]))
        action=next(x for x in records if x["kind"]=="action")
        action["history"]=[x for x in action["history"] if x["event_type"]!="action_cancelled"]
        accepted,ignored=evaluate(c,records=records)
        self.assertTrue(any(f.category=="missing_issue" for f in accepted))

    def test_explicit_owner_clear_is_still_reported(self):
        c=case("m3_stage1c_LC03_013aa5b_run1.json","LC03")
        # An explicit owner clearing event must prevent suppression.
        records=json.loads(json.dumps(c["output"]["records"]))
        action=next(x for x in records if x["kind"]=="action")
        action["history"][-1]["clear_fields"].append("owner")
        findings=c["output"]["audit_findings"]
        events=json.loads(json.dumps(c["llm_responses"][0]["response"]["events"]))
        for event in events:
            if event["kind"]=="action" and event["event_type"]=="action_cancelled":
                event["clear_fields"].append("owner")
        accepted,_=evaluate(c,findings=findings,records=records,events_override=events)
        self.assertEqual(len(accepted),1)

if __name__=="__main__":unittest.main()

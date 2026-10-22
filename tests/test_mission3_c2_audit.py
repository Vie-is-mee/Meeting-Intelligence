"""C2-03 real-Groq audit counterexamples (deterministic replay, no API calls)."""
import json
from pathlib import Path
import unittest
from meeting_intelligence.auditor import (
    AuditFinding, _mistakes_recorded_assignment_for_missing_issue_update
)
from meeting_intelligence.models import ResultRecord, Utterance

ROOT=Path(__file__).resolve().parents[1]
RUN=json.loads((ROOT/"docs/evaluation/mission3/c2_m3_d655084_controls_run3.json").read_text(encoding="utf8"))
RESULT=next(row["output"] for row in RUN["results"] if row["id"]=="C2-03")

class C2AuditTests(unittest.TestCase):
    def get_case(self):
        utterances=[Utterance.model_validate(u) for u in RESULT["utterances"]]
        records=[ResultRecord.model_validate(r) for r in RESULT["records"]]
        finding=AuditFinding.model_validate(RESULT["audit_findings"][0])
        return finding,records,utterances

    def test_groq_issue_assignment_false_warning_not_missing_issue_update(self):
        finding, records, utterances=self.get_case()
        self.assertTrue(_mistakes_recorded_assignment_for_missing_issue_update(
            finding,records,utterances))
        self.assertTrue(any(x.kind=="action" and x.owner=="Huy" and
                            x.due_raw=="trước thứ Sáu" for x in records))

    def test_real_issue_resolution_or_incorrect_owner_cannot_be_hidden(self):
        finding, records, utterances=self.get_case()
        issue=next(r for r in records if r.kind=="issue")
        action=next(r for r in records if r.kind=="action")
        issue.meeting_status="reported_resolved"
        self.assertFalse(_mistakes_recorded_assignment_for_missing_issue_update(
            finding,records,utterances))
        issue.meeting_status="open"
        action.owner=None
        self.assertFalse(_mistakes_recorded_assignment_for_missing_issue_update(
            finding,records,utterances))

    def test_wrong_source_or_different_business_topic_not_hidden(self):
        finding, records, utterances=self.get_case()
        wrong_source=finding.model_copy(update={"source_ids":["L001"]})
        self.assertFalse(_mistakes_recorded_assignment_for_missing_issue_update(
            wrong_source,records,utterances))
        wrong_topic=finding.model_copy(update={"issue_key":"unrelated"})
        self.assertFalse(_mistakes_recorded_assignment_for_missing_issue_update(
            wrong_topic,records,utterances))

if __name__=="__main__":
    unittest.main()

"""Stage 3.5 LC02 fresh-Groq defects and counterexamples (NO provider calls).

Tests replay the saved provider hypotheses to isolate the deterministic repairs.
This is NOT a new model inference or a claim of semantic generalization.
"""
import json
import unittest
from pathlib import Path

from meeting_intelligence.auditor import (
    AuditFinding, _mistakes_cancelled_task_history_for_missing_assignment
)
from meeting_intelligence.completeness import recover_explicit_omissions
from meeting_intelligence.models import Event
from meeting_intelligence.parser import parse_transcript
from meeting_intelligence.pipeline import analyze
from meeting_intelligence.resolver import resolve_events

ROOT = Path(__file__).resolve().parents[1]
RUN = json.loads((ROOT / "docs/evaluation/mission3/m3_fresh_regression_LC02_LC03_7e63907_run1.json").read_text(encoding="utf-8"))
ORIGINAL = next(x["output"] for x in RUN["cases"] if x["id"] == "LC02")
TRANSCRIPT = "\n".join(x["id"] + " | " + (x.get("speaker") or "Unknown") + " | " + x["text"]
                       for x in ORIGINAL["utterances"])


def original_llm_events():
    seen = set()
    events = []
    for row in ORIGINAL["records"]:
        if row["issue_key"].startswith("m3_recovered_"):
            continue
        for e in row["history"]:
            key = json.dumps(e, ensure_ascii=False, sort_keys=True)
            if key not in seen:
                seen.add(key)
                events.append(e)
    return events


class ArchivedClient:
    def __init__(self, events, audit):
        self.events = events
        self.audit = audit
        self.n = 0

    def completion_json(self, *_args, **_kwargs):
        self.n += 1
        return {"events": self.events} if self.n == 1 else {"findings": self.audit}


class LC02LiveFixTests(unittest.TestCase):
    def test_replayed_real_groq_extraction_yields_no_issue_duplicate_owner_preserved(self):
        result = analyze(TRANSCRIPT, client=ArchivedClient(
            original_llm_events(), ORIGINAL["audit_findings"]), audit=True)
        rows = sorted((r.kind, r.meeting_status) for r in result.records)
        self.assertEqual(rows, [("action", "cancelled"), ("decision", "open"), ("request", "recorded")])
        action = next(r for r in result.records if r.kind == "action")
        self.assertEqual(action.owner, "Dũng")
        self.assertIsNone(action.due_raw)
        self.assertEqual(action.history[-1].event_type, "action_cancelled")
        self.assertNotIn("owner", action.history[-1].clear_fields)
        self.assertEqual(result.audit_findings, [])
        self.assertTrue(any("Assignment đã nằm trong history" in x for x in result.warnings))

    def test_explicit_owner_removal_still_works(self):
        src = ("L001 | Linh | Mai thử thư viện X.\n"
               "L002 | Mai | Tôi nhận việc.\n"
               "L003 | Linh | Hủy việc thử X, bỏ phân công cho Mai và bỏ hạn cũ.")
        events = [
            Event(kind="action",event_type="assignment",issue_key="task_x",
                  topic="thư viện X",value="thử thư viện X",owner="Mai",
                  source_ids=["L001"]),
            Event(kind="action",event_type="action_cancelled",issue_key="task_x",
                  topic="thư viện X",clear_fields=["owner","due_raw"],
                  source_ids=["L003"])
        ]
        row = resolve_events(events,parse_transcript(src))[0]
        self.assertIsNone(row.owner)
        self.assertIn("owner",row.history[-1].clear_fields)

    def test_declaring_no_new_assignment_does_not_clear_historical_owner(self):
        src = ("L001 | Linh | Dũng thử thư viện X.\n"
               "L002 | Dũng | Tôi nhận thử.\n"
               "L003 | Linh | Hủy thử thư viện X vì giấy phép, bỏ hạn chiều mai. Chưa giao việc mới.")
        events = [
            Event(kind="action",event_type="assignment",issue_key="task_x",
                  topic="thư viện X",value="thử X",owner="Dũng",source_ids=["L001"]),
            Event(kind="action",event_type="action_cancelled",issue_key="task_x",
                  topic="thư viện X",clear_fields=["owner","due_raw"],source_ids=["L003"])
        ]
        row = resolve_events(events,parse_transcript(src))[0]
        self.assertEqual(row.owner,"Dũng")
        self.assertNotIn("owner",row.history[-1].clear_fields)

    def test_customer_request_misclassified_as_issue_normalizes_only_near_literal(self):
        src=parse_transcript("L001 | An | Khách hàng yêu cầu có xuất báo cáo dạng CSV.")
        wrong=[Event(kind="issue",event_type="issue_reported",issue_key="csv_req",
                    topic="CSV",value="Khách hàng yêu cầu xuất báo cáo dạng CSV.",
                    source_ids=["L001"])]
        recovered, keys=recover_explicit_omissions(wrong,src,[])
        self.assertEqual(len(recovered),1)
        self.assertEqual(recovered[0].kind,"request")
        self.assertEqual(recovered[0].issue_key,"csv_req")
        self.assertIn("csv_req", keys)

    def test_distinct_customer_issue_must_survive(self):
        src=parse_transcript("L001 | An | Khách hàng yêu cầu có xuất báo cáo dạng CSV.")
        real_issue=[Event(kind="issue",event_type="issue_reported",issue_key="csv_bug",
                         topic="CSV error",value="CSV xuất bị lỗi font.",
                         source_ids=["L001"])]
        recovered,_=recover_explicit_omissions(real_issue,src,[])
        self.assertEqual({x.kind for x in recovered},{"issue","request"})

    def test_audit_new_assignment_or_other_issue_not_suppressed(self):
        lines=parse_transcript(TRANSCRIPT)
        records=resolve_events([Event.model_validate(x) for x in original_llm_events()],lines)
        old=AuditFinding.model_validate(ORIGINAL["audit_findings"][0])
        self.assertTrue(_mistakes_cancelled_task_history_for_missing_assignment(old,records,lines))
        wrong=old.model_copy(update={"source_ids":["L005"],"source_quote":"Yêu cầu xuất CSV"})
        self.assertFalse(_mistakes_cancelled_task_history_for_missing_assignment(wrong,records,lines))
        wrong=old.model_copy(update={"issue_key":"csv_requirement"})
        self.assertFalse(_mistakes_cancelled_task_history_for_missing_assignment(wrong,records,lines))
        wrong=old.model_copy(update={"category":"missing_late_change"})
        self.assertFalse(_mistakes_cancelled_task_history_for_missing_assignment(wrong,records,lines))

if __name__=="__main__":
    unittest.main()

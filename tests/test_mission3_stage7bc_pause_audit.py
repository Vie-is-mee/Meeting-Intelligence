"""A disputed audit must not turn a paused/cancelled task into an active-sounding unknown."""
import json,unittest
from pathlib import Path
from meeting_intelligence.pipeline import analyze
from meeting_intelligence.auditor import AuditFinding,apply_audit_findings,hold_for_review
from meeting_intelligence.models import ResultRecord

ROOT=Path(__file__).resolve().parents[1]
CASE=json.loads((ROOT/"docs/evaluation/mission3/m3_stage7bc_long01_live_run1.json").read_text(encoding="utf-8"))["cases"][0]
TRANSCRIPT="\n".join(f"{u['speaker']}: {u['text']}" for u in CASE["output"]["utterances"])

class Stub:
    def __init__(self,events,findings):self.events=events;self.findings=findings;self.calls=0
    def completion_json(self,*args,**kwargs):
        self.calls+=1
        return {"events":self.events} if self.calls==1 else {"findings":self.findings}

class PauseAuditTests(unittest.TestCase):
    def test_archived_false_blocked_audit_retains_paused_and_review(self):
        extraction=CASE["llm_responses"][0]["response"]["events"]
        findings=CASE["llm_responses"][1]["response"]["findings"]
        out=analyze(TRANSCRIPT,client=Stub(extraction,findings),audit=True)
        record=next(r for r in out.records if r.kind=="action" and r.owner=="Mai")
        self.assertEqual(record.meeting_status,"paused")
        self.assertEqual(record.execution_status,"blocked")
        self.assertIsNone(record.due_raw)
        self.assertEqual(record.review_status,"needs_review")
        self.assertTrue(out.audit_findings)  # Do not conceal critical audit.
        self.assertTrue(any("unsupported_fact" in m for m in record.warnings))

    def test_unfounded_active_assignment_still_fail_closed(self):
        record=ResultRecord(issue_key="a",topic="triển khai",kind="action",
                            content="Làm X",meeting_status="assigned",
                            owner="Lan",review_status="unreviewed")
        finding=AuditFinding(issue_key="a",kind="action",category="unsupported_fact",
                             severity="high",source_ids=["L001"],source_quote="Lệnh giả",
                             explanation="Owner không có bằng chứng")
        apply_audit_findings([record],[finding])
        self.assertEqual(record.meeting_status,"unverified")
        self.assertEqual(record.review_status,"needs_review")

    def test_cancelled_task_remains_cancelled_even_under_critical_audit(self):
        record=ResultRecord(issue_key="a",topic="bảng giá",kind="action",
                            content="Chuẩn bị bảng giá",meeting_status="cancelled",
                            owner="Mai",review_status="unreviewed")
        hold_for_review(record)
        self.assertEqual(record.meeting_status,"cancelled")

if __name__=="__main__":unittest.main()

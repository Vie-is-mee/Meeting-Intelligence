"""Mission 3 official CR C2: no fabricated personal assignee or deadline.

All tests are deterministic, source-labelled controls (NOT live provider tests).
The transcript fixture is frozen independently of model outputs.
"""
from __future__ import annotations
import json
import unittest
from pathlib import Path
from meeting_intelligence.pipeline import analyze

CASES = {c["id"]: c for c in json.loads(
    (Path(__file__).resolve().parents[1] / "datasets/mission3_c2_v1.json").read_text(encoding="utf-8")
)["cases"]}

def event(event_type, sid, *, owner=None, due=None, kind="action", key="payment_double_charge",
          value="Xử lý lỗi thanh toán bị trừ tiền hai lần", clear=None):
    return dict(issue_key=key, topic="Lỗi thanh toán", kind=kind,
                event_type=event_type, source_ids=[sid], value=value,
                owner=owner, due_raw=due, clear_fields=clear or [])

class MockEvents:
    def __init__(self, events):
        self.events = events
    def completion_json(self, *args, **kwargs):
        return {"events":self.events}

def run(case, events):
    return analyze(CASES[case]["transcript"],client=MockEvents(events),audit=False)

class C2ContractTests(unittest.TestCase):
    def test_c2_01_bare_collective_no_personal_owner_or_due(self):
        # Speaker "Minh" is visible metadata, NOT evidence Minh accepted the work.
        out=run("C2-01",[event("assignment","L001",owner="Minh",
                                due="ngày mai",value="Team xử lý việc này")])
        self.assertEqual(len(out.records),1)
        record=out.records[0]
        self.assertEqual(record.kind,"action")
        self.assertIsNone(record.owner)
        self.assertIsNone(record.due_raw)
        self.assertEqual(record.meeting_status,"unverified")
        self.assertEqual(record.review_status,"needs_review")
        self.assertIn("L001",record.evidence_ids)

    def test_c2_01_collective_phrase_is_not_a_decision_proposal(self):
        out=run("C2-01",[
            event("proposal","L001",kind="decision",value="team mình xử lý việc này"),
        ])
        self.assertEqual(len(out.records),1)
        self.assertEqual(out.records[0].kind,"action")
        self.assertEqual(out.records[0].meeting_status,"unverified")
        self.assertIsNone(out.records[0].owner)
        self.assertIsNone(out.records[0].due_raw)

    def test_c2_02_issue_context_and_proposed_friday_not_assignment(self):
        # L002 collective phrase cannot make its speaker personally responsible.
        # L003 proposes Friday; L004 explicitly says neither owner nor due agreed.
        out=run("C2-02",[
            event("assignment","L002",owner="Minh"),
            event("deadline_change","L003",due="thứ Sáu",value=None),
        ])
        action=next(r for r in out.records if r.kind=="action")
        self.assertIsNone(action.owner)
        self.assertIsNone(action.due_raw)
        self.assertEqual(action.review_status,"needs_review")
        self.assertNotEqual(action.meeting_status,"assigned")

    def test_c2_03_subsequent_named_acceptance_survives(self):
        out=run("C2-03",[
            event("assignment","L002",owner="Minh"),
            event("reassignment","L004",owner="Huy",due="trước thứ Sáu"),
        ])
        action=next(r for r in out.records if r.kind=="action")
        self.assertEqual(action.owner,"Huy")
        self.assertEqual(action.due_raw,"trước thứ Sáu")
        self.assertEqual(action.meeting_status,"assigned")

    def test_c2_01_no_extracted_events_retains_reviewable_ambiguity(self):
        out=run("C2-01",[])
        self.assertEqual(len(out.records),1)
        record=out.records[0]
        self.assertEqual(record.kind,"action")
        self.assertEqual(record.meeting_status,"unverified")
        self.assertEqual(record.review_status,"needs_review")
        self.assertIsNone(record.owner)
        self.assertIsNone(record.due_raw)
        self.assertEqual(record.evidence_ids,["L001"])
        self.assertEqual(record.history,[])

    def test_c2_02_other_topic_record_does_not_hide_collective_intent(self):
        out=run("C2-02",[
            event("issue_reported","L001",kind="issue",
                  value="Khách hàng bị trừ tiền hai lần"),
        ])
        actions=[r for r in out.records if r.kind=="action"]
        self.assertEqual(len(actions),1)
        self.assertEqual(actions[0].meeting_status,"unverified")
        self.assertEqual(actions[0].evidence_ids,["L002"])
        self.assertIsNone(actions[0].owner)
        self.assertIsNone(actions[0].due_raw)

    def test_c2_04_regression_cancelled_preserves_former_owner(self):
        out=run("C2-04",[
            event("assignment","L001",key="trial_x",owner="Lan",
                  due="chiều mai",value="kiểm thử thư viện X"),
            event("action_cancelled","L003",key="trial_x",
                  value=None,clear=["due_raw"]),
        ])
        self.assertEqual(len(out.records),1)
        action=out.records[0]
        self.assertEqual(action.meeting_status,"cancelled")
        self.assertEqual(action.owner,"Lan")
        self.assertIsNone(action.due_raw)

if __name__=="__main__":
    unittest.main()

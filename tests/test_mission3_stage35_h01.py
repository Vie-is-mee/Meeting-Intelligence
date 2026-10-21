"""Stage 3.5 H01 fresh-provider false-audit controls. No API calls."""
import json
import unittest
from pathlib import Path
from meeting_intelligence.auditor import (
    AuditFinding, _mistakes_reopened_decision_for_missing_old_condition
)
from meeting_intelligence.models import Event, Utterance
from meeting_intelligence.pipeline import analyze
from meeting_intelligence.parser import parse_transcript
from meeting_intelligence.resolver import resolve_events

ROOT=Path(__file__).resolve().parents[1]
RAW=json.loads((ROOT/"docs/evaluation/mission3/m3_fresh_regression_H01_19860b4_run1.json").read_text(encoding="utf-8"))["cases"][0]
ORIGINAL=RAW["output"]
TRANSCRIPT="\n".join(u["id"]+" | "+(u.get("speaker") or "Unknown")+" | "+u["text"] for u in ORIGINAL["utterances"])

def events_from_result():
    seen=set()
    out=[]
    for record in ORIGINAL["records"]:
        for event in record["history"]:
            token=json.dumps(event,ensure_ascii=False,sort_keys=True)
            if token not in seen:
                seen.add(token)
                out.append(event)
    return out

class Replay:
    def __init__(self,events,findings):
        self.events=events
        self.findings=findings
        self.calls=0
    def completion_json(self,*args,**kwargs):
        self.calls+=1
        return {"events":self.events} if self.calls==1 else {"findings":self.findings}

class ReopenAuditControls(unittest.TestCase):
    def test_h01_actual_fresh_audit_wrongly_restores_old_condition(self):
        self.assertEqual(RAW["result"],"COMPLETED")
        self.assertEqual(len(ORIGINAL["audit_findings"]),1)
        result=analyze(TRANSCRIPT,
                       client=Replay(events_from_result(),ORIGINAL["audit_findings"]),
                       audit=True)
        self.assertEqual(result.audit_findings,[])
        decision=next(r for r in result.records if r.kind=="decision")
        self.assertEqual(decision.meeting_status,"reopened")
        self.assertIsNone(decision.condition)
        self.assertTrue(any(r.kind=="action" and r.owner=="Huy"
                            and r.meeting_status=="assigned" for r in result.records))
        self.assertTrue(any("Điều kiện cũ" in m for m in result.warnings))

    def test_condition_still_active_cannot_be_suppressed(self):
        lines=parse_transcript(TRANSCRIPT)
        records=resolve_events([Event.model_validate(x) for x in events_from_result()],lines)
        finding=AuditFinding.model_validate(ORIGINAL["audit_findings"][0])
        decision=next(r for r in records if r.kind=="decision")
        decision.meeting_status="conditional"
        decision.condition="bảo mật duyệt quyền đọc dữ liệu"
        self.assertFalse(_mistakes_reopened_decision_for_missing_old_condition(
            finding,records,lines))

    def test_future_reagreement_prevents_old_condition_suppression(self):
        lines=parse_transcript(TRANSCRIPT)
        records=resolve_events([Event.model_validate(x) for x in events_from_result()],lines)
        decision=next(r for r in records if r.kind=="decision")
        decision.history.append(Event(kind="decision",event_type="conditional_agreement",
                    issue_key=decision.issue_key,topic=decision.topic,
                    value="bật đồng bộ tự động",condition="duyệt quyền",
                    source_ids=["L007"]))
        lines.append(Utterance(id="L007",order=7,speaker="An",
                    text="Thống nhất lại bật đồng bộ nếu bảo mật duyệt quyền."))
        self.assertFalse(_mistakes_reopened_decision_for_missing_old_condition(
            AuditFinding.model_validate(ORIGINAL["audit_findings"][0]),records,lines))

if __name__=="__main__":unittest.main()

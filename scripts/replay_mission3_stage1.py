"""Deterministic Stage1 replay of previously recorded M2 event hypotheses.

NOT a fresh LLM or proof of improved recall: same M2 events + archived audit
findings fed through current Stage1 extraction/resolver/verifier/audit handling.
Preserves exact original M2 artifacts and records semantic status differences.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from meeting_intelligence.pipeline import analyze
SOURCES={
    "four": ROOT/"docs/evaluation/mission3/m2_remote_baseline_v1.json",
    "eight": ROOT/"docs/evaluation/final_regression_round5_retry2.json",
}
FOUR_INPUT=ROOT/"datasets/mission3_before_after_v1.json"
EIGHT_INPUT=ROOT/"docs/evaluation/final_regression_input_v2.json"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def core_hashes():
    return {p.name:digest(p) for p in sorted((ROOT/"meeting_intelligence").glob("*.py"))}

def collect(case, source):
    records=case["output"]["records"]
    hypotheses, seen=[],set()
    for row in records:
        for e in row.get("history",[]):
            key=json.dumps(e,ensure_ascii=False,sort_keys=True)
            if key not in seen:
                hypotheses.append(e)
                seen.add(key)
    if source=="four":
        inputs=json.loads(FOUR_INPUT.read_text(encoding="utf-8"))
        text=next(x["transcript"] for x in inputs["cases"] if x["id"]==case["id"])
    else:
        dataset=json.loads(EIGHT_INPUT.read_text(encoding="utf-8"))
        text=next(x["transcript"] for x in dataset["cases"] if x["id"]==case["id"])
    return text, hypotheses,case["output"].get("audit_findings",[])

class ArchivedClient:
    def __init__(self, events, audit_findings):
        self.events=events
        self.audit_findings=audit_findings
        self.count=0
    def completion_json(self,*_args,**_kwargs):
        self.count+=1
        return {"events":self.events} if self.count==1 else {"findings":self.audit_findings}

def condensed(rows):
    return [{
        "issue_key":r["issue_key"],"kind":r["kind"],"content":r.get("content"),
        "meeting_status":r["meeting_status"],"execution_status":r.get("execution_status"),
        "owner":r.get("owner"),"due_raw":r.get("due_raw"),"condition":r.get("condition"),
        "review_status":r["review_status"],"warnings":r.get("warnings",[]),
        "field_evidence_ids":r.get("field_evidence_ids",{})
    } for r in rows]

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--group",choices=("four","eight"),required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    src=SOURCES[a.group]
    blob=json.loads(src.read_text(encoding="utf-8"))
    original=blob["results"] if a.group=="four" else blob["cases"]
    entries=[]
    for x in original:
        if (x.get("status",x.get("result")) not in ("COMPLETED",)):
            entries.append({"id":x["id"],"replayed":False,"reason":"Original API output absent"})
            continue
        transcript,events,findings=collect(x,a.group)
        client=ArchivedClient(events,findings)
        result=analyze(transcript,client=client,audit=True)
        old=condensed(x["output"]["records"])
        new=condensed([r.model_dump() for r in result.records])
        entries.append({
            "id":x["id"],"replayed":True,"archived_events_count":len(events),
            "old":old,"new":new,"old_audit_findings":findings,
            "new_audit_findings":result.audit_findings,
            "warning_changes":[{"issue_key":n["issue_key"],"kind":n["kind"],
                "before":o["warnings"],"after":n["warnings"]}
                for o,n in zip(old,new) if o["warnings"]!=n["warnings"]],
            "new_pipeline_warnings":result.warnings,
            "note":"Archived event hypotheses, NOT newly sampled events."
        })
        print(x["id"],"replayed",len(old),"->",len(new),
              "audits",len(findings),"->",len(result.audit_findings),flush=True)
    report={
        "created_utc":datetime.now(timezone.utc).isoformat(),
        "purpose":"Deterministic M2-event replay through Stage1 code. No fresh LLM calls.",
        "source":str(src.relative_to(ROOT)).replace("\\","/"),
        "source_sha256":digest(src),
        "code_hashes":core_hashes(),
        "data_label":"synthetic previously seen developer cases, internal review only",
        "entries":entries
    }
    out=ROOT/a.out
    if out.exists():
        raise SystemExit("Refusing to overwrite prior replay artifact")
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Saved",out,"cases",len(entries))

if __name__=="__main__":main()

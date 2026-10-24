"""Stage 5 reproducible, source-locked *limited* semantic constraint scorecard.

This checks explicit frozen C2 and D01/D04 requirements; it is NOT a blind
human-validated overall precision/recall benchmark. Include audit counts.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"docs/evaluation/mission3"
FILES=[
"m3_stage5_C201_C202_0778afe_run1.json",
"m3_stage5_C203_C204_0778afe_run1.json",
"m3_stage5_D01_D04_0778afe_run1.json",
]

def score():
    runs=[json.loads((P/n).read_text(encoding="utf8")) for n in FILES]
    core=[{k.replace("\\","/"):v for k,v in run["sha256"].items()
           if k.startswith("meeting_intelligence")} for run in runs]
    if any(h!=core[0] for h in core[1:]):
        raise RuntimeError("NOT SAME SOURCE — refuse combined report")
    cases={row["id"]:row for run in runs for row in run["cases"]}
    needed=["C2-01","C2-02","C2-03","C2-04","D01","D04"]
    assert sorted(cases)==sorted(needed),"Unexpected cases"
    def records(k):return cases[k]["output"]["records"]
    def select(k,kind):return [r for r in records(k) if r["kind"]==kind]
    c1=select("C2-01","action")
    c2=select("C2-02","action")
    c3=select("C2-03","action")
    c4=select("C2-04","action")
    d1=select("D01","decision")
    d4=select("D04","decision")
    criteria={
      "C2-01":bool(c1 and all(r["meeting_status"]=="unverified" and
                     r.get("owner") is None and r.get("due_raw") is None
                     and "L001" in r["evidence_ids"] for r in c1)),
      "C2-02":bool(c2 and all(r["meeting_status"]=="unverified" and
                     r.get("owner") is None and r.get("due_raw") is None for r in c2)
                     and not any(r["meeting_status"]=="agreed" for r in select("C2-02","decision"))
                     and not any(r.get("due_raw") for r in select("C2-02","request"))),
      "C2-03":bool(any(r["meeting_status"]=="assigned" and
                     r.get("owner")=="Huy" and r.get("due_raw")=="trước thứ Sáu"
                     for r in c3)),
      "C2-04":bool(any(r["meeting_status"]=="cancelled" and
                     r.get("owner")=="Lan" and r.get("due_raw") is None for r in c4)),
      "D01":bool(any(r["meeting_status"]=="agreed" and
                     "object storage" in (r.get("content") or "").casefold() for r in d1)
                     and any(r["meeting_status"]=="open" and
                     "nhà cung cấp" in ((r.get("content") or "")+" "+r["topic"]).casefold()
                     for r in d1)),
      "D04":bool(any(r["meeting_status"]=="conditional" and
                     "300" in (r.get("condition") or "") and
                     "không có lỗi nghiêm trọng" in (r.get("condition") or "").casefold()
                     for r in d4))
    }
    return {"scope":"6 explicit known development/regression cases, NOT independent benchmark",
      "model":runs[0]["model"],"same_source_fingerprint":True,
      "provider_completed":sum(cases[k]["result"]=="COMPLETED" for k in needed),
      "audit_completed":sum(bool(cases[k].get("audit_completed")) for k in needed),
      "criteria":criteria,"criteria_satisfied":sum(criteria.values()),
      "audit_findings":{k:len(cases[k]["output"]["audit_findings"]) for k in needed},
      "core_sha256":core[0],
      "sources":FILES,
      "limitations":["LC01/LC03 and two long-meeting stress cases not in this six-case count",
      "C2-01 and C2-02 have accepted audit findings",
      "Assistant-authored synthetic cases; model stochastic; human gold review pending"]}

if __name__=="__main__":
    report=score()
    out=P/"m3_stage5_frozen_scorecard_0778afe_run1.json"
    if out.exists():raise SystemExit("Refusing to overwrite")
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print(json.dumps({"provider_completed":report["provider_completed"],
                      "audit_completed":report["audit_completed"],
                      "criteria_satisfied":report["criteria_satisfied"],
                      "criteria":report["criteria"],
                      "audit_findings":report["audit_findings"]},ensure_ascii=False,indent=2))
    if report["criteria_satisfied"]<6:raise SystemExit(2)

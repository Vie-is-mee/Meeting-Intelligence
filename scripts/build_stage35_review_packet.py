"""Source-labelled four-case M2-vs-M3 evaluation packet.

Default comparison is EXACTLY hosted-M2 output vs archived-M2-events passed
through M3 code (REPLAY), never a fresh-M3 accuracy number.
--fresh <path> accepts only a source-attested local M3 runner artifact and
records it as a new run, still subject to manual semantic adjudication.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"docs/evaluation/mission3/m2_remote_baseline_v1.json"
REPLAY=ROOT/"docs/evaluation/mission3/m3_stage3_replay_four_v2.json"
INPUT=ROOT/"datasets/mission3_before_after_v1.json"
LABELS=ROOT/"datasets/mission3_before_after_labels_v1.json"
FREEZE=ROOT/"docs/evaluation/mission3/frozen_manifest_v1.json"

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):return json.loads(p.read_text(encoding="utf-8"))

def display(value):
    if value is None:return "(chưa có)"
    return str(value).replace("|",r"\|").replace("\n"," ").strip()[:240]

def record_summary(row):
    return (
        f"{display(row.get('kind'))} / {display(row.get('meeting_status'))} / "
        f"{display(row.get('execution_status'))} — {display(row.get('content'))} "
        f"(owner: {display(row.get('owner'))}; due: {display(row.get('due_raw'))}; "
        f"utility: {display(row.get('information_utility'))})"
    )

def packet(fresh_path=None):
    freeze=read(FREEZE);inputs=read(INPUT);labels=read(LABELS)
    assert digest(INPUT)==freeze["inputs_sha256"],"Frozen input SHA mismatch"
    assert digest(LABELS)==freeze["labels_sha256"],"Frozen labels SHA mismatch"
    ids=[x["id"] for x in inputs["cases"]]
    assert ids==[x["id"] for x in labels["cases"]],"Frozen labels case mismatch"

    before=read(BASE)
    assert before["frozen_input_sha256"]==digest(INPUT)
    older={x["id"]:x for x in before["results"]}
    assert set(older)==set(ids) and before["source_revision_attested_by_remote"] is False

    if fresh_path:
        after=read(fresh_path)
        m=after.get("manifest",{})
        assert m.get("version")=="m3" and m.get("transport")=="local",(
            "Refusing a remote/offline/impersonated M3 result"
        )
        assert m.get("frozen_input_sha256")==digest(INPUT)
        assert m.get("frozen_labels_sha256")==digest(LABELS)
        assert set(m.get("cases",[]))==set(ids),"Fresh M3 run must contain every locked case"
        after_rows={x["id"]:x for x in after["results"]}
        assert set(after_rows).issubset(set(ids))
        for cid,row in after_rows.items():
            assert row["status"] in {"COMPLETED","ERROR"}
        mode="FRESH_LOCAL_M3_SOURCE_ATTESTED_BY_RUNNER__MANUAL_REVIEW_PENDING"
        after_source=str(fresh_path.relative_to(ROOT)) if fresh_path.is_relative_to(ROOT) else str(fresh_path)
    else:
        after=read(REPLAY)
        after_rows={x["id"]:x for x in after["entries"]}
        assert set(after_rows)==set(ids)
        assert all(x["replayed"] for x in after_rows.values())
        mode="ARCHIVED_M2_EVENT_REPLAY_ONLY__NO_FRESH_M3_INFERENCE"
        after_source=str(REPLAY.relative_to(ROOT))

    lines=[
        "# Stage 3.5 — Before/After evidence packet (không tự chấm ngữ nghĩa)",
        "",
        f"**Evidence mode:** \`{mode}\`.",
        f"**Report UTC:** {datetime.now(timezone.utc).isoformat()}",
        "",
        "**CẢNH BÁO:** M2 Before là LLM API thật trên hosted deployment nhưng source SHA của Render chưa được xác nhận. "
        "Bản M3 ở packet này "+("là kết quả local provider mới; mọi kết luận đúng/sai vẫn chờ semantic review." if fresh_path else
        "chỉ là replay sự kiện LLM M2 đã lưu; KHÔNG được nói đây là kết quả Groq M3 mới."),
        "",
        f"**M2 original:** \`{BASE.relative_to(ROOT)}\` SHA-256 \`{digest(BASE)}\`.",
        f"**M3 compared:** \`{after_source}\` SHA-256 \`{digest(fresh_path or REPLAY)}\`.",
        f"**Data sealed input:** \`{digest(INPUT)}\`.",
        f"**Data sealed labels:** \`{digest(LABELS)}\`.",
        "",
        "## 1. Machine-grounded observations (NOT semantic accuracy)",
        "",
        "| Case | M2 hosted Before | M3 "+("fresh local" if fresh_path else "archived-event replay")+" | Review |",
        "|---|---|---|---|",
    ]
    for cid in ids:
        b=older[cid];a=after_rows.get(cid)
        br=(b.get("output") or {}).get("records",[])
        if fresh_path:
            rr=((a or {}).get("output") or {}).get("records",[])
            state=(a or {}).get("status","NOT_RUN")
        else:
            rr=a["new"]
            state="REPLAY_ONLY"
        lines.append(f"| {cid} | {b['status']}: {len(br)} records / {len((b.get('output') or {}).get('audit_findings',[]))} audit | "
                     f"{state}: {len(rr)} records / "+(str(len((a or {}).get("new_audit_findings",[]))) if not fresh_path else
                        str(len(((a or {}).get("output") or {}).get("audit_findings",[]))))+" audit | **NOT SEMANTICALLY REVIEWED** |")
    lines.extend(["","## 2. Per-case original output and M3 result",""])

    gold={x["id"]:x for x in labels["cases"]}
    for cid in ids:
        b=older[cid];a=after_rows.get(cid)
        br=(b.get("output") or {}).get("records",[])
        rr=((a or {}).get("output") or {}).get("records",[]) if fresh_path else a["new"]
        lines.extend([f"### {cid}","",
                      "**M2 Before — hosted Groq output (real provider run, source SHA not attested):**",""])
        for i,row in enumerate(br):
            lines.append(f"- B{i}: {record_summary(row)}; source: {display(row.get('evidence_ids'))}")
        if not br:lines.append("- Không có record.")
        lines.extend(["",f"**M3 {'Fresh local' if fresh_path else 'Replay-only'}:**",""])
        for i,row in enumerate(rr):
            sources=row.get('evidence_ids') or (row.get("field_evidence_ids") or {}).get("content")
            lines.append(f"- A{i}: {record_summary(row)}; source: {display(sources)}")
        if not rr:lines.append("- Không có record.")
        lines.extend(["","**Frozen required outcomes:**",""])
        for expected in gold[cid]["required"]:
            lines.append(f"- \`{expected['label_id']}\` ({expected['kind']}, status \`{expected['meeting_status']}\`) "
                         f"— {expected['meaning']} — source {display(expected['source_ids'])}")
        if cid == "M3-K01":
            lines.extend(["", "**Adjudication note:** frozen gold uses meeting_status=recorded for idempotency knowledge, whereas M3 intentionally keeps extracted knowledge meeting_status=unverified and requires human review. Do NOT silently edit locked gold or count the utility label as factual verification."])
        lines.extend(["","**Forbidden outcomes (must check manually):**",""])
        for f in gold[cid].get("forbidden",[]):lines.append(f"- {f}")
        lines.extend(["","**Manual adjudication — REQUIRED BEFORE SCORES:**",
                      "- [ ] One-to-one match of each required label to a record, correct business meaning and kind",
                      "- [ ] Latest state / conditions / owner / due accurate",
                      "- [ ] Per-field evidence genuinely entails values, including important late corrections",
                      "- [ ] No false action/decision or forbidden outcomes",
                      "- [ ] Auditor/verifier warnings judged individually (false positives and missed true positives)",
                      "- [ ] Case-specific core verdict: **UNREVIEWED**",
                      "- [ ] Case-specific full verdict: **UNREVIEWED**",""])
    lines.extend([
        "## 3. What is NOT established yet","",
        "- This packet cannot measure independent precision/recall or full-case accuracy without a human-adjudicated review.",
        "- If after source is replay, **no newly sampled M3 LLM output exists** in this comparison.",
        "- Synthetic, assistant-labelled examples are known development cases, NOT an independent holdout.",
        "- Use fresh M2 exact-tag local LLM vs fresh M3 local LLM with identical settings for strongest comparison.",
        "- Never merge production before confirming actual M3 end-to-end behavior and Change Request gate.",
        "",
    ])
    return ("\n".join(lines).rstrip()+"\n").replace(chr(92)+"`", "`").replace("docs"+chr(92)+"evaluation"+chr(92)+"mission3"+chr(92), "docs/evaluation/mission3/")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--fresh",help="JSON path from local M3 comparison runner; optional")
    p.add_argument("--out",required=True,help="New Markdown output, must not already exist")
    a=p.parse_args()
    path=ROOT/a.out
    fresh=(ROOT/a.fresh) if a.fresh else None
    if path.exists():raise SystemExit("Refuse to overwrite evidence packet")
    result=packet(fresh)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(result,encoding="utf-8")
    print("Evidence packet created",path,"mode",("fresh (pending review)" if fresh else "replay only"))

if __name__=="__main__":main()

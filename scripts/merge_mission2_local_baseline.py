"""Merge exact-tag M2 local inference files into one source-attested baseline.

This does not sample an LLM, change annotations, or perform semantic scoring.
Original raw files remain untouched. Never select the better of two outputs.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/"datasets/mission3_before_after_v1.json"
LABELS=ROOT/"datasets/mission3_before_after_labels_v1.json"
FREEZE=ROOT/"docs/evaluation/mission3/frozen_manifest_v1.json"

def sha(p:Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def merge_m2(paths:list[Path])->dict:
    frozen=json.loads(FREEZE.read_text(encoding="utf-8"))
    required=[c["id"] for c in json.loads(INPUT.read_text(encoding="utf-8"))["cases"]]
    assert sha(INPUT)==frozen["inputs_sha256"]
    assert sha(LABELS)==frozen["labels_sha256"]
    if len(paths)<2:
        raise ValueError("Provide separate original local M2 source runs")
    merged={}
    refs=[]
    settings=None
    calls=0
    tokens=0
    for p in paths:
        data=json.loads(p.read_text(encoding="utf-8"))
        m=data.get("manifest",{})
        if m.get("version")!="m2" or m.get("transport")!="local":
            raise ValueError("Only real local M2 runs permitted")
        if m.get("core_commit")!=frozen["source_commit"]:
            raise ValueError("Not the immutable submitted M2 source")
        if m.get("frozen_input_sha256")!=sha(INPUT) or m.get("frozen_labels_sha256")!=sha(LABELS):
            raise ValueError("Frozen data or gold mismatch")
        if not data.get("complete"):
            raise ValueError("Original run incomplete")
        common={"source":m.get("source_files_sha256"),"model":data.get("model"),
                "generation":data.get("generation_settings"),"audit":m.get("audit")}
        if not common["source"] or not common["model"] or not common["generation"]:
            raise ValueError("Missing provenance")
        if settings is None: settings=common
        elif common!=settings: raise ValueError("Mismatched model, audit, source or settings")
        observed={r["id"] for r in data.get("results",[])}
        if observed != set(m.get("cases",[])) or len(observed)!=len(data.get("results",[])):
            raise ValueError("Bad result list / mismatched manifest")
        if observed-set(required) or observed&set(merged):
            raise ValueError("Unexpected or duplicate cases")
        for row in data["results"]:
            if row.get("status") not in {"COMPLETED","ERROR"}:
                raise ValueError("Missing status")
            merged[row["id"]]={**row,"original_run_file":p.name,"original_run_sha256":sha(p)}
            calls+=row.get("api_calls_cumulative",0)
            tokens+=(row.get("token_usage_cumulative") or {}).get("total_tokens",0)
        refs.append({"path":p.name,"sha256":sha(p),"cases":list(m["cases"])})
    if set(merged)!=set(required):
        raise ValueError("All four frozen cases required")
    manifest=dict(json.loads(paths[0].read_text(encoding="utf-8"))["manifest"])
    manifest["cases"]=required
    return {
        "manifest":manifest,"model":settings["model"],
        "generation_settings":settings["generation"],"complete":True,
        "source_attested":True,"assistant_semantic_review":"PENDING",
        "synthetic_development_only":True,"original_runs":refs,
        "api_calls":calls,"tokens_reported":tokens,
        "results":[merged[i] for i in required],
        "note":"Strict exact-tag M2 local Groq run; not independent holdout and no automatic semantic score."
    }

def main():
    a=argparse.ArgumentParser()
    a.add_argument("files",nargs="+")
    a.add_argument("--out",required=True)
    opts=a.parse_args()
    dest=ROOT/opts.out
    if dest.exists():
        raise SystemExit("Refusing to overwrite existing evidence")
    data=merge_m2([ROOT/p for p in opts.files])
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Strict M2 baseline saved:",dest,"cases:",[r["id"] for r in data["results"]],
          "calls:",data["api_calls"],"tokens:",data["tokens_reported"])

if __name__=="__main__":main()

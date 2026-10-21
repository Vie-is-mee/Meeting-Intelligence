"""Merge one-case + remaining-case TRUE LOCAL M3 runs, without cherry-picking.

Never merges offline, remotely hosted M2, partial attempts, mismatched source
code/config, or duplicate case IDs. Every original run stays intact.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/"datasets/mission3_before_after_v1.json"
LABELS=ROOT/"datasets/mission3_before_after_labels_v1.json"

def sha(path:Path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def merge(paths:list[Path])->dict:
    if len(paths)<2:
        raise ValueError("Require at least two disjoint source runs")
    required=[c["id"] for c in load(INPUT)["cases"]]
    refs=[]
    joined={}
    fingerprint=None
    calls=0
    total_tokens=0
    for path in paths:
        data=load(path)
        m=data.get("manifest",{})
        if m.get("version")!="m3" or m.get("transport")!="local":
            raise ValueError("Reject remote/offline and non-M3 source runs")
        if m.get("frozen_input_sha256")!=sha(INPUT) or m.get("frozen_labels_sha256")!=sha(LABELS):
            raise ValueError("Frozen dataset or labels mismatch")
        if data.get("complete") is not True:
            raise ValueError("Cannot merge partial run; original record remains available")
        if not m.get("core_commit") or not m.get("source_files_sha256"):
            raise ValueError("No source provenance")
        if not data.get("model") or not data.get("generation_settings"):
            raise ValueError("No model configuration provenance")
        comparable={k:v for k,v in m.items() if k not in {"cases"}}
        key={"manifest":comparable,"model":data["model"],
             "generation_settings":data["generation_settings"]}
        if fingerprint is None:
            fingerprint=key
        elif fingerprint!=key:
            raise ValueError("Different source SHA/model/config; refuse merging")
        observed={x["id"] for x in data.get("results",[])}
        if len(observed)!=len(data.get("results",[])) or observed!=set(m.get("cases",[])):
            raise ValueError("Case list invalid or incomplete")
        if observed-set(required) or observed&set(joined):
            raise ValueError("Unexpected or duplicate cases; do not cherry-pick")
        for row in data["results"]:
            if row.get("status") not in {"COMPLETED","ERROR"}:
                raise ValueError("Missing explicit case status")
            joined[row["id"]]={**row,"source_run_sha256":sha(path),
                               "source_run_file":path.name}
        last=data.get("results",[])[-1] if data.get("results") else {}
        calls+=last.get("api_calls_cumulative") or 0
        total_tokens+=(last.get("token_usage_cumulative") or {}).get("total_tokens",0)
        refs.append({"file":path.name,"sha256":sha(path),"cases":list(m["cases"])})
    if set(joined)!=set(required):
        raise ValueError("All frozen cases required; do not present partial merged result as full")
    out_manifest=copy.deepcopy(load(paths[0])["manifest"])
    out_manifest["cases"]=required
    return {
        "manifest":out_manifest,
        "model":fingerprint["model"],
        "generation_settings":fingerprint["generation_settings"],
        "complete":True,
        "merged_from_distinct_local_runs":refs,
        "semantically_reviewed":False,
        "note":"Source-preserving merge of source-attested local M3 runs. Errors retained; this is NOT a semantic score.",
        "results":[joined[k] for k in required],
        "provider_attempts_total":calls,
        "reported_tokens_total":total_tokens,
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("sources",nargs="+",help="Completed local M3 runner JSON files")
    p.add_argument("--out",required=True)
    args=p.parse_args()
    out=ROOT/args.out
    if out.exists():raise SystemExit("Refusing to overwrite merged evidence")
    data=merge([ROOT/x for x in args.sources])
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Strict merge OK:",out,"cases",len(data["results"]),
          "status",[x["id"]+":"+x["status"] for x in data["results"]])

if __name__=="__main__":
    main()

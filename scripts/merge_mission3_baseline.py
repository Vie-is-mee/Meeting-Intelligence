"""Merge frozen M2 remote runs without cherry-picking outputs.

M2 server-side commit is not attested by the public API. Preserve individual files.
"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/"docs/evaluation/mission3"
INPUT=ROOT/"datasets/mission3_before_after_v1.json"
SOURCES=[BASE/"m2_remote_M3-E02_v1.json",BASE/"m2_remote_remaining_v1.json"]
TARGET=BASE/"m2_remote_baseline_v1.json"

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    expected=json.loads(INPUT.read_text(encoding="utf-8"))
    rows={}
    origins={}
    settings=[]
    for path in SOURCES:
        blob=json.loads(path.read_text(encoding="utf-8"))
        m=blob["manifest"]
        if m["version"]!="m2" or m["transport"]!="remote" or m["frozen_input_sha256"]!=sha(INPUT):
            raise SystemExit("Source run is not from the same frozen M2 remote input: "+str(path))
        if not blob["complete"]:
            raise SystemExit("Unfinished source run: "+str(path))
        for result in blob["results"]:
            rid=result["id"]
            if rid in rows:
                raise SystemExit("Duplicate case ID "+rid)
            rows[rid]=result
            origins[rid]=dict(source=path.name,source_sha256=sha(path))
        settings.append({"model":sorted({r.get("provider_model") for r in blob["results"]}),
                         "remote_url":m["remote_url"],"audit":m["audit"]})
    ids=[c["id"] for c in expected["cases"]]
    if set(ids)!=set(rows):
        raise SystemExit("Missing or unexpected case ID; refuse partial merger.")
    report={
        "schema_version":"1.0",
        "description":"One actual hosted M2 API run per frozen M3 case; results combined only in predefined dataset order.",
        "source_revision_attested_by_remote":False,
        "source_tag_expected":"submission-a-ui-v2-20261015",
        "source_tag_commit":"439f672a3204238100158570ebcf80f0551b85fd",
        "important_caveat":"Remote API returns model but no server git revision; cannot prove hosted source exactly matches local tagged M2. Results are from the deployed M2 service, not verified byte-for-byte local M2.",
        "synthetic_development_data":True,
        "frozen_input_sha256":sha(INPUT),
        "frozen_labels_sha256":sha(ROOT/"datasets/mission3_before_after_labels_v1.json"),
        "run_settings":settings,
        "case_order":ids,
        "results":[{**rows[i],"provenance":origins[i]} for i in ids],
        "summary":{"completed":sum(rows[i]["status"]=="COMPLETED" for i in ids),
                   "cases":len(ids),"provider_api_calls":sum(rows[i].get("api_calls") or 0 for i in ids),
                   "provider_tokens":sum((rows[i].get("token_usage") or {}).get("total_tokens",0) for i in ids)}
    }
    if TARGET.exists():
        if json.loads(TARGET.read_text(encoding="utf-8"))!=report:
            raise SystemExit("Merged artifact differs: don't overwrite. Use new version.")
    else:
        TARGET.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Merged:",TARGET,"cases",report["summary"]["completed"],"API",report["summary"]["provider_api_calls"],"tokens",report["summary"]["provider_tokens"])

if __name__=="__main__":
    main()

"""Stage 3.5 local readiness check, with no disclosure of credentials.

No inference is attempted here. This is *not* an LLM evaluation result.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/"datasets/mission3_before_after_v1.json"
LABELS=ROOT/"datasets/mission3_before_after_labels_v1.json"
FREEZE=ROOT/"docs/evaluation/mission3/frozen_manifest_v1.json"
M2=ROOT/"tmp/m2-submission"

def checksum(p: Path)->str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def rev(path: Path, *args: str)->str:
    env=os.environ.copy()
    env["HOME"]=env.get("USERPROFILE") or env.get("HOME","")
    res=subprocess.run(["git","-C",str(path),*args],capture_output=True,
                       text=True,encoding="utf-8",errors="replace",env=env,check=True)
    return res.stdout.strip()

def inspect():
    from dotenv import load_dotenv
    load_dotenv(ROOT/".env",override=False)
    freeze=json.loads(FREEZE.read_text(encoding="utf-8"))
    source_commit=rev(ROOT,"rev-parse","HEAD")
    local_m2=rev(M2,"rev-parse","HEAD") if (M2/"meeting_intelligence/pipeline.py").exists() else None
    sealed_m2=rev(ROOT,"rev-list","-n","1",freeze["source_tag"])
    sources={str(x.relative_to(ROOT)).replace(chr(92),"/"):checksum(x)
             for x in sorted((ROOT/"meeting_intelligence").glob("*.py"))}
    data=json.loads(INPUT.read_text(encoding="utf-8"))
    labels=json.loads(LABELS.read_text(encoding="utf-8"))
    checks={
        "frozen_input_hash_ok":checksum(INPUT)==freeze["inputs_sha256"],
        "frozen_label_hash_ok":checksum(LABELS)==freeze["labels_sha256"],
        "case_alignment_ok":[x["id"] for x in data["cases"]]==
                            [x["id"] for x in labels["cases"]],
        "m2_submitted_worktree_ok":local_m2==sealed_m2==freeze["source_commit"],
        "m3_core_exists":bool(sources),
    }
    configured={x:bool(os.environ.get(x)) for x in
                ("LLM_API_KEY","LLM_BASE_URL","LLM_MODEL")}
    good=all(checks.values())
    ready=good and all(configured.values())
    return {
        "generated_utc":datetime.now(timezone.utc).isoformat(),
        "task":"Mission 3 Stage 3.5 private-source-attested LLM evaluation readiness",
        "test_type":"preflight_only_NO_LLM_CALLS",
        "candidate_git_commit":source_commit,
        "m2_worktree_commit":local_m2,
        "m2_tag_commit":sealed_m2,
        "m3_source_sha256":sources,
        "frozen_case_ids":[x["id"] for x in data["cases"]],
        "frozen_input_sha256":checksum(INPUT),
        "frozen_labels_sha256":checksum(LABELS),
        "checks":checks,
        "private_llm_settings_present":configured,
        "ready_for_fresh_llm":ready,
        "state":"READY_NOT_EXECUTED" if ready else
                ("BLOCKED_MISSING_PRIVATE_LLM_SETTINGS" if good else "BLOCKED_PRECHECK"),
        "note":"No token, API key, base URL or private environment value is written. Provider inference has NOT run."
    }

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",help="Optional new JSON output; refuses to overwrite")
    args=p.parse_args()
    report=inspect()
    if args.out:
        dest=ROOT/args.out
        if dest.exists():
            raise SystemExit("Refusing to overwrite historical preflight report")
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"state":report["state"],"candidate_commit":report["candidate_git_commit"],
                      "checks":report["checks"],"private_settings_present":report["private_llm_settings_present"]},
                     ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()

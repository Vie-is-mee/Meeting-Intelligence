"""CR C2 prospective source-matched M2 vs M3 provider run.

Four fixed user-request cases. No labels passed to model. No provider secrets
written. Uses the exact M2 tag/worktree and hashes every source module.
Each run writes an independent, append-only-by-case JSON artifact.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "datasets/mission3_c2_v1.json"

def sha(p: Path):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def rev(path: Path, *args):
    env = os.environ.copy()
    env["HOME"] = env.get("USERPROFILE") or env.get("HOME","")
    return subprocess.run(["git","-C",str(path),*args],env=env,check=True,
                          capture_output=True,text=True,encoding="utf-8").stdout.strip()

def main():
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--version",required=True,choices=("m2","m3"))
    cli.add_argument("--ids",nargs="+")
    cli.add_argument("--out")
    cli.add_argument("--preflight",action="store_true")
    cli.add_argument("--audit",choices=("on","off"),default="on")
    cli.add_argument("--call-interval",type=float,default=35)
    cli.add_argument("--timeout",type=int,default=100)
    args=cli.parse_args()

    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env",override=False)
    src = ROOT/"tmp/m2-submission" if args.version=="m2" else ROOT
    commit=rev(src,"rev-parse","HEAD")
    if args.version=="m2":
        assert commit == rev(ROOT,"rev-list","-n","1","submission-a-ui-v2-20261015"),"M2 source is not the exact frozen submitted tag"
    dataset=json.loads(DATA.read_text(encoding="utf-8"))
    possible={c["id"] for c in dataset["cases"]}
    wanted=set(args.ids or possible)
    if wanted-possible:
        cli.error("Unknown cases")
    cases=[c for c in dataset["cases"] if c["id"] in wanted]
    if not cases:cli.error("No cases")
    hashes={p.relative_to(src).as_posix():sha(p) for p in
            sorted((src/"meeting_intelligence").glob("*.py"))}
    manifest={
        "dataset_file":"datasets/mission3_c2_v1.json",
        "dataset_sha256":sha(DATA),
        "cases":[c["id"] for c in cases],
        "version":args.version,
        "transport":"local",
        "source_git_commit":commit,
        "core_source_files_sha256":hashes,
        "audit":args.audit,
    }
    if args.preflight:
        print(json.dumps({"preflight":"OK","manifest":manifest},ensure_ascii=False,indent=2))
        return
    if not args.out:cli.error("--out required")
    out=ROOT/args.out
    if out.exists():
        raise SystemExit("Refuse overwrite C2 evidence. Use a unique --out file.")
    # Keep native package of selected revision ahead of the checkout root.
    sys.path.insert(0,str(src))
    from meeting_intelligence.pipeline import analyze
    from meeting_intelligence.llm_client import LLMClient
    client=LLMClient(max_retries=0,min_call_interval=args.call_interval,timeout=args.timeout)
    report={
        "started_utc":datetime.now(timezone.utc).isoformat(),
        "manifest":manifest,
        "model":client.model,
        "generation_settings":{"temperature":client.temperature,
                               "reasoning_effort":client.reasoning_effort,
                               "max_completion_tokens":client.max_completion_tokens,
                               "structured_outputs":client.structured_mode},
        "results":[], "complete":False,
    }
    for case in cases:
        row={"id":case["id"],"status":"ERROR",
             "started_utc":datetime.now(timezone.utc).isoformat()}
        start=time.monotonic()
        try:
            result=analyze(case["transcript"],client=client,audit=args.audit=="on")
            row.update(status="COMPLETED",output=result.model_dump())
        except Exception as exc:
            row["error"]=type(exc).__name__+": "+str(exc)[:1100]
        row["duration_s"]=round(time.monotonic()-start,2)
        row["api_calls_cumulative"]=client.call_count
        row["token_usage_cumulative"]=dict(client.token_usage)
        report["results"].append(row)
        report["complete"]=len(report["results"])==len(cases)
        out.parent.mkdir(parents=True,exist_ok=True)
        tmp=out.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        tmp.replace(out)
        print(case["id"],row["status"],row["duration_s"],"s",flush=True)
        if row["status"]=="ERROR":
            report["stopped_reason"]="Provider or analysis failure; no subsequent cases were run"
            out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            break
    print("Saved",out,"complete",report["complete"])

if __name__=="__main__":
    main()

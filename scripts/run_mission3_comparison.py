"""Compare the EXACT submitted Mission 2 worktree with an M3 candidate.

Never uses labels as model input. Preserves errors/raw outputs and fingerprints.
Modes:
  --preflight             validate frozen cases and source without any API
  --transport offline     narrow rules only (NOT an LLM baseline)
  --transport local       call configured LLM from selected source (key required)
  --transport remote      call existing hosted API (source revision NOT verifiable remotely)

Examples:
  python scripts/run_mission3_comparison.py --version m2 --preflight
  python scripts/run_mission3_comparison.py --version m2 --transport offline
  python scripts/run_mission3_comparison.py --version m2 --transport remote --ids M3-E02
  python scripts/run_mission3_comparison.py --version m3 --transport local --ids M3-E01
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "datasets/mission3_before_after_v1.json"
LABELS = ROOT / "datasets/mission3_before_after_labels_v1.json"
FREEZE = ROOT / "docs/evaluation/mission3/frozen_manifest_v1.json"
DEFAULT_REMOTE = "https://meeting-intelligence-5jk5.onrender.com"

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git_rev(root: Path) -> str:
    env = dict(os.environ)
    env["HOME"] = env.get("USERPROFILE") or env.get("HOME", "")
    cmd = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], env=env,
                         capture_output=True, text=True, check=True)
    return cmd.stdout.strip()

def select_core(src: Path):
    if not (src / "meeting_intelligence/pipeline.py").exists():
        raise SystemExit("Missing source: " + str(src))
    if any(k == "meeting_intelligence" or k.startswith("meeting_intelligence.") for k in sys.modules):
        raise SystemExit("The core must not be imported before selecting the version")
    sys.path.insert(0, str(src))
    parser = importlib.import_module("meeting_intelligence.parser")
    pipeline = importlib.import_module("meeting_intelligence.pipeline")
    client = importlib.import_module("meeting_intelligence.llm_client")
    return parser, pipeline, client

def record_file(out: Path, report: dict):
    out.parent.mkdir(parents=True, exist_ok=True)
    temp = out.with_suffix(out.suffix + ".tmp")
    temp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(out)

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--version", required=True, choices=("m2", "m3"))
    p.add_argument("--transport", choices=("offline", "local", "remote"), default="offline")
    p.add_argument("--preflight", action="store_true")
    p.add_argument("--ids", nargs="+")
    p.add_argument("--remote-url", default=DEFAULT_REMOTE)
    p.add_argument("--audit", choices=("on", "off"), default="on")
    p.add_argument("--call-interval", type=float, default=90)
    p.add_argument("--timeout", type=int, default=100)
    p.add_argument("--out", help="Unique output JSON path; otherwise a separate default per version/transport")
    args = p.parse_args()
    if args.call_interval < 0 or args.timeout < 1:
        p.error("Invalid call interval or timeout")
    if args.version == "m3" and args.transport == "remote":
        p.error("M3 remote source version cannot be attested; refusing to label the existing M2 deployment as M3. Use --transport local for a pinned M3 candidate.")
    src = ROOT / "tmp/m2-submission" if args.version == "m2" else ROOT
    if args.version == "m2" and git_rev(src) != git_rev_tag("submission-a-ui-v2-20261015"):
        raise SystemExit("M2 worktree is not at the submitted M2 tag; REFUSE run")
    dataset = json.loads(DATA.read_text(encoding="utf-8"))
    labels = json.loads(LABELS.read_text(encoding="utf-8"))
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    if (sha(DATA) != freeze["inputs_sha256"] or sha(LABELS) != freeze["labels_sha256"]
            or dataset["id"] != labels["dataset_id"]
            or [c["id"] for c in dataset["cases"]] != [c["id"] for c in labels["cases"]]):
        raise SystemExit("Frozen inputs/labels changed. REFUSE run.")
    choices = set(args.ids or [c["id"] for c in dataset["cases"]])
    if choices - {c["id"] for c in dataset["cases"]}:
        p.error("Unknown case ID(s)")
    rows = [c for c in dataset["cases"] if c["id"] in choices]
    parser, pipeline, llm = select_core(src)
    for case in rows:
        utt = parser.parse_transcript(case["transcript"])
        if not utt or len(utt) != case["transcript"].count("\n") + 1:
            raise SystemExit("Unexpected parser split in " + case["id"])
    rev = git_rev(src)
    hashes = {str(x.relative_to(src)).replace("\\", "/"): sha(x)
              for x in sorted((src / "meeting_intelligence").glob("*.py"))}
    manifest = {
        "version": args.version, "transport": args.transport, "core_commit": rev,
        "source_files_sha256": hashes, "frozen_input_sha256": sha(DATA),
        "frozen_labels_sha256": sha(LABELS), "audit": args.audit,
        "cases": [c["id"] for c in rows],
        "remote_url": args.remote_url if args.transport == "remote" else None,
        "interpretation": ("REMOTE deployed model endpoint; its exact source commit is NOT "
                           "attested by the API and results are NOT proof of local M2 tag execution")
                           if args.transport == "remote" else (
                            "OFFLINE RULES only; not LLM accuracy" if args.transport == "offline"
                            else "Direct LLM execution against the selected local source tree"),
    }
    if args.preflight:
        print(json.dumps({"preflight": "OK", "manifest": manifest}, ensure_ascii=False, indent=2))
        return
    out = ROOT / (args.out or
                  f"docs/evaluation/mission3/{args.version}_{args.transport}_run_v1.json")
    if out.exists():
        old = json.loads(out.read_text(encoding="utf-8"))
        if old["manifest"] != manifest:
            raise SystemExit("Output path belongs to another frozen run. Use --out NEW_PATH.")
        report = old
    else:
        report = {"started_utc": datetime.now(timezone.utc).isoformat(),
                  "manifest": manifest, "results": [], "complete": False}
    done = {r["id"] for r in report["results"]}
    api_client = None
    if args.transport == "local":
        api_client = llm.LLMClient(max_retries=0, min_call_interval=args.call_interval, timeout=args.timeout)
        report["model"] = api_client.model
        report["generation_settings"] = {
            "temperature": api_client.temperature,
            "reasoning_effort": api_client.reasoning_effort,
            "max_completion_tokens": api_client.max_completion_tokens,
            "structured_outputs": api_client.structured_mode
        }
    report["complete"] = False
    record_file(out, report)
    last_at = 0.0
    for case in rows:
        if case["id"] in done:
            continue
        row = {"id": case["id"], "status": "ERROR",
               "started_utc": datetime.now(timezone.utc).isoformat()}
        started = time.monotonic()
        try:
            if args.transport == "remote":
                remaining = args.call_interval - (time.monotonic() - last_at)
                if remaining > 0:
                    time.sleep(remaining)
                last_at = time.monotonic()
                body = json.dumps({"transcript": case["transcript"], "engine": "llm_api",
                                   "audit": args.audit == "on"}, ensure_ascii=False).encode("utf-8")
                req = urllib.request.Request(
                    args.remote_url.rstrip("/") + "/api/analyze", method="POST",
                    data=body, headers={"Content-Type": "application/json", "Accept": "application/json"})
                try:
                    with urllib.request.urlopen(req, timeout=args.timeout) as response:
                        obj = json.load(response)
                        row["http_status"] = response.status
                except urllib.error.HTTPError as exc:
                    row["http_status"] = exc.code
                    row["error"] = exc.read(4096).decode("utf-8", errors="replace")
                else:
                    row.update(status="COMPLETED", output=obj.get("analysis"),
                               api_calls=obj.get("api_calls"), token_usage=obj.get("token_usage"),
                               provider_model=obj.get("model"), audit_enabled=obj.get("audit_enabled"))
            else:
                result = pipeline.analyze(case["transcript"],
                                          engine=("offline_rules" if args.transport == "offline" else "llm_api"),
                                          client=api_client, audit=args.audit == "on")
                row.update(status="COMPLETED", output=result.model_dump())
                if api_client is not None:
                    row["api_calls_cumulative"] = api_client.call_count
                    row["token_usage_cumulative"] = dict(api_client.token_usage)
        except Exception as exc:
            row["error"] = type(exc).__name__ + ": " + str(exc)[:1200]
        row["duration_s"] = round(time.monotonic() - started, 2)
        report["results"].append(row)
        report["complete"] = len(report["results"]) == len(rows)
        record_file(out, report)
        print(f"{case['id']}: {row['status']}; {row['duration_s']}s", flush=True)
        if row.get("http_status") in (429, 500, 502, 503, 504):
            report["stopped_reason"] = f"HTTP {row['http_status']}; remaining cases NOT RUN."
            record_file(out, report)
            break
        if args.transport in ("local", "remote") and row["status"] == "ERROR":
            report["stopped_reason"] = "API error; remaining cases NOT RUN."
            record_file(out, report)
            break
    print("Saved:", out, "| complete:", report["complete"])

def git_rev_tag(tag: str) -> str:
    env = dict(os.environ)
    env["HOME"] = env.get("USERPROFILE") or env.get("HOME", "")
    r = subprocess.run(["git", "-C", str(ROOT), "rev-list", "-n", "1", tag],
                       env=env, capture_output=True, text=True, check=True)
    return r.stdout.strip()

if __name__ == "__main__":
    main()

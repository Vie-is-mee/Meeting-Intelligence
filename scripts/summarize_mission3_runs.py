"""Print compact real-output evidence from M3 comparison runs; does not infer semantic correctness."""
from pathlib import Path
import argparse
import json

def main():
    p = argparse.ArgumentParser()
    p.add_argument("paths", nargs="+")
    args = p.parse_args()
    for name in args.paths:
        data = json.loads(Path(name).read_text(encoding="utf-8"))
        print("FILE:", name)
        for case in data.get("results", []):
            print("=== CASE", case["id"], case["status"],
                  "calls", case.get("api_calls"), "tokens", case.get("token_usage"),
                  "model", case.get("provider_model"))
            if case.get("error"):
                print("ERROR:", case["error"])
            output = case.get("output") or {}
            for i, record in enumerate(output.get("records", [])):
                print("RECORD", i, record.get("kind"), record.get("meeting_status"),
                      record.get("execution_status"), repr(record.get("content")))
                print("  owner:", record.get("owner"), "due:", record.get("due_raw"),
                      "condition:", record.get("condition"), "source:", record.get("evidence_ids"))
                print("  fields:", record.get("field_evidence_ids"))
                print("  review:", record.get("review_status"),
                      "warnings:", record.get("warnings"))
            print("AUDIT:", json.dumps(output.get("audit_findings", []), ensure_ascii=False))
            print("WARNINGS:", output.get("warnings", []))

if __name__ == "__main__":
    main()

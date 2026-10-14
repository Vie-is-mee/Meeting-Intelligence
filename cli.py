"""Run: python cli.py samples/T02.txt --engine offline_rules [--save output.json]"""
import argparse
import json
import sys
from pathlib import Path
from meeting_intelligence.pipeline import analyze
from meeting_intelligence.llm_client import LLMError

def main():
    parser = argparse.ArgumentParser(description="Meeting Intelligence M2 first vertical slice")
    parser.add_argument("transcript", type=Path)
    parser.add_argument("--engine", choices=["llm_api", "offline_rules"], default="llm_api")
    parser.add_argument("--save", type=Path, default=None)
    parser.add_argument('--audit', choices=['on', 'off'], default='on')
    args = parser.parse_args()
    try:
        result = analyze(args.transcript.read_text(encoding="utf-8-sig"),
                         engine=args.engine, audit=args.audit == 'on')
        output = json.dumps(result.model_dump(), indent=2, ensure_ascii=False)
        if args.save:
            args.save.parent.mkdir(parents=True, exist_ok=True)
            args.save.write_text(output+"\n", encoding="utf-8")
        print(output)
    except (LLMError, ValueError, OSError) as exc:
        print(f'Lỗi: {exc}', file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

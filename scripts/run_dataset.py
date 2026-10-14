"""Collect frozen, resumable real API outputs. Gold labels never enter prompts."""
from __future__ import annotations
import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from meeting_intelligence.llm_client import LLMClient
from meeting_intelligence.pipeline import analyze


def fingerprint(dataset):
    files = [dataset, *sorted((ROOT / 'meeting_intelligence').glob('*.py'))]
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}


class RecordingClient(LLMClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.responses = []

    def completion_json(self, system, user, **kwargs):
        start = time.perf_counter()
        try:
            result = super().completion_json(system, user, **kwargs)
        except Exception as exc:
            row={'error': str(exc), 'elapsed_s': time.perf_counter()-start}
            for name in ('status_code','provider_code','diagnostics'):
                value=getattr(exc,name,None)
                if value is not None: row[name]=value
            self.responses.append(row)
            raise
        self.responses.append({'response': result, 'elapsed_s': time.perf_counter()-start})
        return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', default='datasets/meeting_eval_v1.json')
    parser.add_argument('--out', default='results/dataset_v1_run.json')
    parser.add_argument('--call-interval', type=float, default=45)
    parser.add_argument('--ids', nargs='+', help='Run a targeted subset; use a NEW --out path.')
    parser.add_argument('--temperature',type=float)
    parser.add_argument('--reasoning-effort',choices=['low','medium','high'])
    parser.add_argument('--stop-on-rate-limit',action='store_true',
                        help='Save the current case and stop on HTTP 429, including audit failures.')
    parser.add_argument('--max-retries',type=int,choices=[0,1,2,3],default=1)
    args = parser.parse_args()
    if args.call_interval < 0:
        parser.error('call interval must be nonnegative')
    dataset_path = ROOT / args.dataset
    data = json.loads(dataset_path.read_text(encoding='utf-8'))
    if data.get('evaluation_gate') == 'pending_human_labels':
        parser.error('Prospective labels are pending. Human-annotate and freeze with scripts/prepare_prospective_eval.py before any API run.')
    if args.ids:
        unknown = set(args.ids) - {c['id'] for c in data['cases']}
        if unknown:
            parser.error('Unknown case IDs: '+', '.join(sorted(unknown)))
        data['cases'] = [c for c in data['cases'] if c['id'] in args.ids]
    hashes = fingerprint(dataset_path)
    out = ROOT / args.out
    client = RecordingClient(min_call_interval=args.call_interval, timeout=120,
                             temperature=args.temperature,reasoning_effort=args.reasoning_effort,
                             max_retries=args.max_retries)
    settings = {'max_completion_tokens':client.max_completion_tokens,
                'audit_max_completion_tokens':1024,
                'temperature':client.temperature,'reasoning_effort':client.reasoning_effort}
    if out.exists():
        report = json.loads(out.read_text(encoding='utf-8'))
        if (report['sha256'] != hashes or report['model'] != client.model
                or report['requested_cases'] != [c['id'] for c in data['cases']]
                or report.get('generation_settings') != settings
                or report.get('structured_outputs') != client.structured_mode
                or report.get('max_retries',1) != args.max_retries
                or report.get('call_interval_s') != args.call_interval):
            raise SystemExit('Frozen inputs/code/model changed: use a new output path.')
    else:
        report = {'created_utc': datetime.now(timezone.utc).isoformat(),
                  'model': client.model, 'engine': 'llm_api', 'audit': True,
                  'sha256': hashes, 'call_interval_s': args.call_interval,
                  'structured_outputs': client.structured_mode,
                  'max_retries':args.max_retries,
                  'generation_settings': settings,
                  'requested_cases': [c['id'] for c in data['cases']],
                  'complete': False, 'cases': []}

    def save():
        out.parent.mkdir(parents=True, exist_ok=True)
        temp = out.with_suffix('.tmp')
        temp.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        temp.replace(out)

    done = {c['id'] for c in report['cases']}
    report.pop('stopped_reason',None)
    for case in data['cases']:
        if case['id'] in done:
            continue
        if fingerprint(dataset_path) != hashes:
            raise SystemExit('Frozen files changed during evaluation; stopping.')
        start = time.perf_counter()
        previous_calls = client.call_count
        previous_tokens = dict(client.token_usage)
        client.responses = []
        print(f"{case['id']}: RUNNING ({case['split']})", flush=True)
        row = {'id': case['id'], 'split': case['split']}
        try:
            # Deliberately pass ONLY transcript, never annotations or checkpoints.
            result = analyze(case['transcript'], client=client, audit=True)
            row.update(result='COMPLETED', output=result.model_dump())
            row['audit_completed'] = len(client.responses) == 2 and 'error' not in client.responses[-1]
        except Exception as exc:
            row.update(result='ERROR', error=str(exc), audit_completed=False)
        row.update(duration_s=round(time.perf_counter()-start, 2),
                   api_calls=client.call_count-previous_calls,
                   api_tokens={k: v-previous_tokens.get(k, 0) for k, v in client.token_usage.items()},
                   llm_responses=client.responses)
        report['cases'].append(row)
        save()
        print(f"{case['id']}: {row['result']}; audit={row['audit_completed']}; calls={row['api_calls']}" , flush=True)
        errors=[row.get('error',''),*[r.get('error','') for r in client.responses]]
        if args.stop_on_rate_limit and any('API HTTP 429' in error for error in errors):
            report['stopped_reason']='HTTP 429; remaining cases were not attempted.'
            report['complete']=len(report['cases'])==len(data['cases'])
            save()
            raise SystemExit('HTTP 429: saved current case; stopping instead of calling remaining cases.')
        if row.get('error'):
            print(row['error'], flush=True)
            if 'connection' in row['error'].lower() or 'kết nối' in row['error'].lower():
                raise SystemExit('Connection failure: stop instead of counting all remaining cases as errors.')
    report['complete'] = len(report['cases']) == len(data['cases'])
    save()


if __name__ == '__main__':
    main()

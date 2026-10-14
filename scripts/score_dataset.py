"""Aggregate explicit semantic review; never treat unmatched predictions as hallucinations.

Review format: cases[{id, alternative?, predictions:[{index,supported,evidence_supported,
reason}], matches:[{label_id,index,core_correct,fields:{field:bool},reason}]}].
Every prediction must be reviewed and matches must be one-to-one.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ('meeting_status', 'execution_status', 'owner', 'supporter', 'due_raw', 'due_iso', 'condition')


def ratio(n, d):
    return {'correct': n, 'total': d, 'rate': n / d if d else None}


def score(dataset, run, review):
    if review['run_sha256'] != hashlib.sha256(json.dumps(run, sort_keys=True, ensure_ascii=False).encode()).hexdigest():
        raise ValueError('Review does not belong to this exact run')
    gold = {c['id']: c for c in dataset['cases']}
    outputs = {c['id']: c for c in run['cases']}
    reviews = {c['id']: c for c in review['cases']}
    if len(reviews) != len(review['cases']):
        raise ValueError('Duplicate reviewed cases')
    summaries = {}
    for split in ('all', 'development', 'held_out'):
        ids = [c['id'] for c in dataset['cases'] if split == 'all' or c['split'] == split]
        counts = dict(predictions=0, supported=0, evidence=0, required=0, recalled=0,
                      reviewed=0, completed=0, audit_completed=0, negative=0, abstained=0)
        fields = {f: [0, 0] for f in FIELDS}
        positive_fields = {f: [0, 0] for f in FIELDS}
        positive_field_required = {f: 0 for f in FIELDS}
        successful_required = 0
        decisions = [0, 0]
        required_decisions = 0
        audit_findings = [0, 0]
        review_handling = [0, 0]
        for cid in ids:
            case = gold[cid]
            actual = outputs.get(cid, {})
            counts['completed'] += actual.get('result') == 'COMPLETED'
            counts['audit_completed'] += bool(actual.get('audit_completed'))
            targets = case['required_records']
            r = reviews.get(cid)
            if r and r.get('alternative'):
                alt = next(a for a in case['representation_alternatives'] if a['id'] == r['alternative'])
                targets = [t for t in targets if t['label_id'] not in alt['replaces_label_ids']] + alt['expected_records']
            counts['required'] += len(targets)
            if actual.get('result') == 'COMPLETED':
                successful_required += len(targets)
            for f in FIELDS:
                positive_field_required[f] += sum(t.get(f) is not None for t in targets)
            required_decisions += sum(t['kind'] == 'decision' for t in targets)
            review_handling[1] += sum(t.get('must_flag_for_review', False) for t in targets)
            review_handling[1] += bool(case.get('case_review_required'))
            if not r:
                continue
            if actual.get('result') != 'COMPLETED':
                raise ValueError('Cannot semantically review an errored case: '+cid)
            records = actual['output']['records']
            predictions = r['predictions']
            judgments = r.get('audit_findings_supported', [])
            if len(judgments) != len(actual['output']['audit_findings']) or any(type(v) is not bool for v in judgments):
                raise ValueError('Review every audit finding: '+cid)
            audit_findings[0] += sum(judgments)
            audit_findings[1] += len(judgments)
            if sorted(p['index'] for p in predictions) != list(range(len(records))):
                raise ValueError('Review every prediction exactly once: '+cid)
            for p in predictions:
                if type(p['supported']) is not bool or type(p['evidence_supported']) is not bool or not p['reason']:
                    raise ValueError('Explicit judgments/reasons required: '+cid)
            counts['reviewed'] += 1
            if case.get('case_review_required'):
                review_handling[0] += r.get('case_review_handled') is True
            counts['predictions'] += len(predictions)
            counts['supported'] += sum(p['supported'] for p in predictions)
            counts['evidence'] += sum(p['evidence_supported'] for p in predictions)
            seen_gold, seen_actual = set(), set()
            target_by_id = {t['label_id']: t for t in targets}
            for m in r['matches']:
                if m['label_id'] not in target_by_id or m['label_id'] in seen_gold or m['index'] in seen_actual or m['index'] not in range(len(records)):
                    raise ValueError('Invalid/nonexclusive match: '+cid)
                if records[m['index']]['kind'] != target_by_id[m['label_id']]['kind']:
                    raise ValueError('Kind mismatch cannot count as correct match: '+cid)
                if type(m['core_correct']) is not bool or not m['reason']:
                    raise ValueError('Explicit match judgment required: '+cid)
                seen_gold.add(m['label_id']); seen_actual.add(m['index'])
                counts['recalled'] += m['core_correct']
                target = target_by_id[m['label_id']]
                if target.get('must_flag_for_review'):
                    if type(m.get('review_handled')) is not bool:
                        raise ValueError('Explicit review handling judgment required: '+cid)
                    review_handling[0] += m['review_handled']
                if target['kind'] == 'decision':
                    decisions[0] += m['core_correct'] and m['fields']['meeting_status']
                    decisions[1] += 1
                for f in FIELDS:
                    v = m['fields'][f]
                    if type(v) is not bool:
                        raise ValueError('Field judgment must be boolean')
                    fields[f][0] += v
                    fields[f][1] += 1
                    if target.get(f) is not None:
                        positive_fields[f][0] += v
                        positive_fields[f][1] += 1
            if not targets:
                counts['negative'] += 1
                counts['abstained'] += not records
        summaries[split] = {
            'cases': len(ids), 'reviewed_cases': counts['reviewed'],
            'semantic_scoring_complete': counts['reviewed'] == counts['completed'] and len(outputs.keys() & set(ids)) == len(ids),
            'pipeline_completion': ratio(counts['completed'], len(ids)),
            'audit_completion': ratio(counts['audit_completed'], len(ids)),
            'supported_record_precision': ratio(counts['supported'], counts['predictions']),
            'required_record_recall_end_to_end': ratio(counts['recalled'], counts['required']),
            'required_record_recall_on_completed_cases': ratio(counts['recalled'], successful_required),
            'evidence_support_accuracy': ratio(counts['evidence'], counts['predictions']),
            'field_accuracy_on_matched_records': {f: ratio(*v) for f, v in fields.items()},
            'nonnull_field_accuracy_on_matched_records': {f: ratio(*v) for f, v in positive_fields.items()},
            'nonnull_field_recall_end_to_end': {f: ratio(positive_fields[f][0], positive_field_required[f]) for f in FIELDS},
            'final_decision_accuracy_on_matched_decisions': ratio(*decisions),
            'final_decision_recall_end_to_end': ratio(decisions[0], required_decisions),
            'audit_finding_precision': ratio(*audit_findings),
            'required_review_handling_recall': ratio(*review_handling),
            'correct_abstention': ratio(counts['abstained'], counts['negative']),
        }
    return {'metrics': summaries, 'caveats': [
        'Partial gold: supported extra records count in precision, not required-record recall. No F1 is computed across different target universes.',
        'Field accuracy is conditional on semantic matches and includes null fields; inspect non-null fields and missing records separately.',
        'Synthetic same-author dataset and same-assistant review, not independent human validation.',
        'Pending semantic review is not a model failure or a model success.']}


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--dataset', default='datasets/meeting_eval_v1.json')
    p.add_argument('--run', default='results/dataset_v1_run.json')
    p.add_argument('--review', default='results/dataset_v1_review.json')
    p.add_argument('--out', default='results/dataset_v1_metrics.json')
    a = p.parse_args()
    load = lambda name: json.loads((ROOT/name).read_text(encoding='utf-8'))
    dataset, run, review = load(a.dataset), load(a.run), load(a.review)
    normalized_hashes = {name.replace('\\', '/'): value for name, value in run['sha256'].items()}
    expected_hash = normalized_hashes.get((ROOT/a.dataset).relative_to(ROOT).as_posix())
    if expected_hash != hashlib.sha256((ROOT/a.dataset).read_bytes()).hexdigest():
        raise ValueError('Dataset differs from frozen run')
    result = score(dataset, run, review)
    result['inputs_sha256'] = {name: hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
                              for name, value in [('dataset',dataset),('run',run),('review',review)]}
    outputs = {c['id']: c for c in run['cases']}
    reviews = {c['id']: c for c in review['cases']}
    kinds = sorted({t['kind'] for c in dataset['cases'] for t in c['required_records']})
    result['by_kind'] = {}
    for kind in kinds:
        required = recalled = predictions = supported = evidence = 0
        for case in dataset['cases']:
            r = reviews.get(case['id'])
            targets = case['required_records']
            if r and r.get('alternative'):
                alt = next(a for a in case['representation_alternatives'] if a['id'] == r['alternative'])
                targets = [t for t in targets if t['label_id'] not in alt['replaces_label_ids']] + alt['expected_records']
            required += sum(t['kind'] == kind for t in targets)
            if not r:
                continue
            labels = {t['label_id']: t for t in targets}
            recalled += sum(m['core_correct'] for m in r['matches'] if labels[m['label_id']]['kind'] == kind)
            records = outputs[case['id']]['output']['records']
            for pred in r['predictions']:
                if records[pred['index']]['kind'] == kind:
                    predictions += 1
                    supported += pred['supported']
                    evidence += pred['evidence_supported']
        result['by_kind'][kind] = dict(supported_record_precision=ratio(supported,predictions),
                                      required_record_recall_end_to_end=ratio(recalled,required),
                                      evidence_support_accuracy=ratio(evidence,predictions))
    result['breakdowns'] = {}
    for category in ('length_band', 'business_scenarios'):
        values = sorted({v for c in dataset['cases'] for v in
                         ([c[category]] if isinstance(c[category], str) else c[category])})
        result['breakdowns'][category] = {}
        for value in values:
            subset = dict(dataset, cases=[c for c in dataset['cases'] if
                          (c[category] == value if isinstance(c[category], str) else value in c[category])])
            result['breakdowns'][category][value] = score(subset, run, review)['metrics']['all']
    (ROOT/a.out).write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

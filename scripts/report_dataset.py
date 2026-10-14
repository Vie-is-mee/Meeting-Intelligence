"""Render reviewed metrics and actual case outcomes for the submission."""
import argparse
import hashlib
import json
from pathlib import Path
from statistics import median

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='docs/DATASET_EVALUATION_RESULTS.md')
    args = parser.parse_args()
    load = lambda p: json.loads((ROOT/p).read_text(encoding='utf-8'))
    dataset = load('datasets/meeting_eval_v1.json')
    run = load('results/dataset_v1_run.json')
    review = load('results/dataset_v1_review.json')
    metrics = load('results/dataset_v1_metrics.json')
    for name, value in [('dataset',dataset),('run',run),('review',review)]:
        digest = hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
        if metrics.get('inputs_sha256',{}).get(name) != digest:
            raise SystemExit('Metrics are stale; rerun score_dataset.py before publishing.')
    if not run['complete'] or not metrics['metrics']['all']['semantic_scoring_complete']:
        raise SystemExit('Finish collection and semantic review before publishing the report.')
    reviews = {c['id']: c for c in review['cases']}
    outputs = {c['id']: c for c in run['cases']}
    def fmt(r):
        return f"{r['correct']}/{r['total']} ({r['rate']:.1%})" if r['rate'] is not None else 'N/A (mẫu số 0)'
    lines = ['# Kết quả đánh giá dataset Mission 2', '',
             f"Model: `{run['model']}`. Lượt chạy bắt đầu UTC: `{run['created_utc']}`. Audit bật; prompt và mã lõi giữ nguyên theo SHA-256 trong artifact.", '',
             'Đây là đánh giá **toàn pipeline** (LLM trích xuất → resolver → verifier → LLM audit), không phải điểm của riêng model. Dữ liệu tổng hợp do cùng trợ lý tạo và rà soát; chưa có người gán nhãn độc lập xác nhận. Chỉ chạy một lượt chính; không chọn câu trả lời tốt nhất từ nhiều lượt.', '',
             '| Chỉ số | Tất cả | Development | Reserved |', '|---|---:|---:|---:|']
    for name, key in [('Hoàn thành pipeline','pipeline_completion'), ('Hoàn thành audit','audit_completion'),
                      ('Precision bản ghi có căn cứ','supported_record_precision'),
                      ('Recall mục bắt buộc, gồm case lỗi','required_record_recall_end_to_end'),
                      ('Recall mục bắt buộc, chỉ case có đầu ra','required_record_recall_on_completed_cases'),
                      ('Đúng kết luận cuối / quyết định ghép được','final_decision_accuracy_on_matched_decisions'),
                      ('Recall quyết định cuối, gồm mục thiếu','final_decision_recall_end_to_end'),
                      ('Bằng chứng hỗ trợ đúng','evidence_support_accuracy'),
                      ('Precision cảnh báo audit','audit_finding_precision'),
                      ('Ghi nhận cần rà soát','required_review_handling_recall'),
                      ('Không tạo bản ghi ở case âm','correct_abstention')]:
        lines.append('| '+name+' | '+' | '.join(fmt(metrics['metrics'][s][key]) for s in ['all','development','held_out'])+' |')
    lines += ['', '## Độ chính xác từng trường trên bản ghi ghép được', '',
              '| Trường | Tất cả giá trị, kể cả null | Chỉ nhãn có giá trị, đã ghép | Thu hồi trường có giá trị, gồm mục thiếu/lỗi |', '|---|---:|---:|---:|']
    all_metrics = metrics['metrics']['all']
    for field, val in all_metrics['field_accuracy_on_matched_records'].items():
        lines.append(f"| {field} | {fmt(val)} | {fmt(all_metrics['nonnull_field_accuracy_on_matched_records'][field])} | {fmt(all_metrics['nonnull_field_recall_end_to_end'][field])} |")
    lines += ['', 'Các trường bị bỏ sót cùng cả bản ghi không nằm trong mẫu số field accuracy; chúng làm giảm recall. `due_iso` toàn null không chứng minh năng lực chuẩn hóa ngày. Nhận xét đúng/sai từng trường đã xét diễn đạt tương đương, không so chuỗi máy móc.', '',
              '## Theo loại thông tin', '', '| Loại | Precision có căn cứ | Recall mục bắt buộc, gồm lỗi chạy |', '|---|---:|---:|']
    for kind, m in metrics['by_kind'].items():
        lines.append(f"| {kind} | {fmt(m['supported_record_precision'])} | {fmt(m['required_record_recall_end_to_end'])} |")
    lines += ['',
              '## Kỳ vọng → thực tế → đánh giá', '',
              'Đạt yêu cầu nội dung khi đủ nhãn bắt buộc, đúng nghĩa/trạng thái/trường, nguồn hỗ trợ đúng và có xử lý rà soát cần thiết. Cảnh báo audit sai được báo riêng; bản ghi phụ đúng nguồn không làm case trượt.', '',
              '| Case | Kỳ vọng | Thực tế | Đánh giá | Điều học được / nhận xét |', '|---|---|---|---|---|']
    totals = {'Đạt': 0, 'Chưa đạt': 0, 'Lỗi chạy': 0}
    for case in dataset['cases']:
        cid = case['id']; actual = outputs[cid]; r = reviews.get(cid)
        targets = case['required_records']
        if r and r.get('alternative'):
            alt = next(a for a in case['representation_alternatives'] if a['id'] == r['alternative'])
            targets = [t for t in targets if t['label_id'] not in alt['replaces_label_ids']] + alt['expected_records']
        if actual['result'] != 'COMPLETED':
            verdict = 'Lỗi chạy'; observed = actual.get('error', 'Không có đầu ra')
            lesson = 'Không chấm ngữ nghĩa khi chưa có đầu ra; tính là thất bại vận hành và không thu hồi được mục bắt buộc.'
        else:
            target_by_id = {t['label_id']: t for t in targets}
            passed = (len(r['matches']) == len(targets)
                      and all(m['core_correct'] and all(m['fields'].values())
                              and (not target_by_id[m['label_id']].get('must_flag_for_review') or m['review_handled']) for m in r['matches'])
                      and all(p['supported'] and p['evidence_supported'] for p in r['predictions'])
                      and (not case.get('case_review_required') or r.get('case_review_handled')))
            verdict = 'Đạt' if passed else 'Chưa đạt'
            observed = f"{len(r['predictions'])} bản ghi; {sum(m['core_correct'] for m in r['matches'])}/{len(targets)} mục đúng nghĩa/trạng thái"
            lesson = r.get('note') or ' '.join(m['reason'] for m in r['matches'])
            missing = [t['label_id'] for t in targets if t['label_id'] not in {m['label_id'] for m in r['matches']}]
            if missing: lesson += ' Thiếu: '+', '.join(missing)+'.'
        totals[verdict] += 1
        esc = lambda s: str(s).replace('|','/').replace('\n',' ')
        lines.append(f"| {cid} | {esc(case['title'])}; {len(targets)} mục | {esc(observed)} | {verdict} | {esc(lesson)} |")
    lines += ['', f"Tổng theo tiêu chí trên: **{totals['Đạt']} đạt, {totals['Chưa đạt']} chưa đạt, {totals['Lỗi chạy']} lỗi chạy**.", '',
              '## Transcript dài và chi phí lượt chạy', '', '| Độ dài | Hoàn thành pipeline | Recall mục bắt buộc |', '|---|---:|---:|']
    for length, m in metrics['breakdowns']['length_band'].items():
        lines.append(f"| {length} | {fmt(m['pipeline_completion'])} | {fmt(m['required_record_recall_end_to_end'])} |")
    tokens = sum(c.get('api_tokens', {}).get('total_tokens', 0) for c in run['cases'])
    calls = sum(c['api_calls'] for c in run['cases'])
    durations = [c['duration_s'] for c in run['cases']]
    lines += ['', f"API attempts: **{calls}** (gồm retry). Provider báo tổng **{tokens:,} tokens** trên các response có usage; không suy ra token của request lỗi. Tổng thời gian các case **{sum(durations):.1f}s**, median **{median(durations):.1f}s/case**, gồm khoảng nghỉ chủ động {run['call_interval_s']:g}s giữa API attempts. Đây không phải latency xử lý thuần của model.", '',
              '## Lỗi ưu tiên xử lý', '',
              '1. Lỗi HTTP 400 ở D09/D15/D16/H08; cả ba transcript dài đều chưa có đầu ra. Adapter hiện chỉ giữ mã lỗi, chưa đủ xác định nguyên nhân từ provider. Không kết luận rằng model không hiểu transcript dài từ mã HTTP này.',
              '2. Audit có nhiều false positive: nhầm nội dung lịch sử bị hủy/rút với thông tin còn hiệu lực, hoặc coi decision/open là đã chốt. D02/D06/D14 bị ghi đè trạng thái đúng/đáng lẽ rõ ràng thành unverified.',
              '3. D04 giữ điều kiện 500 dù cuối họp sửa thành 300; D03 thiếu chi tiết pháp chế; H01 điều kiện lịch sử còn ở trường hiện tại; H03 mất due_raw tương đối.',
              '4. D14 vẫn tạo bản ghi từ chuỗi prompt injection, dù audit đã giữ để rà soát. D11 diễn đạt sai nội dung không dấu. D01/D08 thiếu mục bắt buộc.',
              '5. H07 không bịa dữ kiện khi mất tiếng, nhưng chưa thông báo rõ không đủ dữ liệu. D08 công việc thiếu người chưa được giữ để rà soát. Một số đầu ra còn phân mảnh/dư thừa.', '',
              '## Giới hạn và cách sử dụng kết quả', '',
              '- Precision chấp nhận bản ghi phụ đúng nguồn; recall chỉ trên nhãn bắt buộc. Không ghép chúng thành F1 vì phạm vi gold chưa đầy đủ.',
              '- `unverified` giúp giữ bản ghi để người kiểm tra, nhưng không được tính là đã hiểu đúng một trạng thái cụ thể như reopened/cancelled. Một bản ghi giả vẫn sai dù đã gắn cờ.',
              '- Reserved đã được dùng trong lượt này; sau khi dùng lỗi ở đây để chỉnh hệ thống, cần một tập reserved mới để kiểm chứng độc lập.',
              '- Không kiểm thử riêng prefix từng checkpoint, độ ổn định qua nhiều lần chạy, hoặc transcript nhiều giờ. Các chỉ số này không chứng minh hệ thống đúng mọi trường hợp.', '',
              'Định nghĩa và lệnh chạy: [DATASET_EVALUATION.md](DATASET_EVALUATION.md). Đầu ra, review và metric máy đọc được ở `results/dataset_v1_*.json`; bản tổng hợp an toàn để review nằm trong `docs/evaluation/` nếu được lưu cùng bài nộp.']
    (ROOT/args.out).write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(totals)


if __name__ == '__main__':
    main()

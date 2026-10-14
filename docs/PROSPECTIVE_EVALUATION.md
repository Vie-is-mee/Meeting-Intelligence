# Bước 1 — Chốt baseline A và chuẩn bị đánh giá mới

Trạng thái: baseline đã chốt; 12 transcript mới đã chuẩn bị; nhãn con người chưa có; không chạy API ở bước này. Không gọi bước chuẩn bị này là đánh giá độc lập đã hoàn thành.

## Baseline A

- Commit nguồn: `4aecdc91f1c526773c7bae0a7dfdebfe5e658d2d`; tag `baseline-a-20261014`.
- Model/cấu hình từ lượt API đã lưu: gpt-oss-120b, temperature 0.6, reasoning low, extraction 2560/audit 1024, structured auto.
- Manifest [baseline_a_20261014.json](evaluation/baseline_a_20261014.json) khóa hash 19 file lõi, nhãn, input, evidence, báo cáo và dữ liệu playback. Không chụp `.env` hoặc khóa.
- Bằng chứng gốc: 8/8 hoàn tất pipeline/audit, 4/8 đạt đầy đủ, 5/8 đạt dữ liệu lõi. Chưa có precision/recall mới toàn bộ 24 case hoặc đo ổn định nhiều lượt.
- Kiểm tra hash bằng `python scripts/baseline_checkpoint.py --verify`. Sau khi sửa lõi cho B, lệnh này dự kiến báo khác baseline; xem/chạy A từ tag thay vì cập nhật manifest để hợp thức hóa thay đổi.
- Không thay raw output, gold cũ hoặc báo cáo A. Candidate B có commit/config/output mới; bảng [comparison_a_b_20261014.json](evaluation/comparison_a_b_20261014.json) để trống B cho đến khi có phép đo.

## Phân chia dữ liệu

[Registry](evaluation/evaluation_split_registry_20261014.json) là trạng thái sử dụng hiện tại. Metadata “held_out / not yet run” bên trong dataset v1 là lịch sử, không còn chứng minh những case đó chưa được xem. Không sửa file lịch sử vì chúng đang được khóa hash.

| Nhóm | Vai trò hiện tại |
| --- | --- |
| 24 case D/H cũ và LC01–LC03 | Dữ liệu đã xem, phát triển/hồi quy; không dùng làm điểm độc lập |
| N01–N12 mới | Pool tổng hợp prospective, chưa có đầu ra; không dùng để tinh chỉnh trước lượt đo |
| Benchmark độc lập thực tế | Chưa có; cần transcript do người khác cung cấp, quyền sử dụng phù hợp và nhãn trước đầu ra |

N01–N12 do cùng trợ lý triển khai viết và nhìn thấy. Người thứ hai gán nhãn sẽ cải thiện chất lượng nhãn, nhưng không tự biến nguồn dữ liệu thành họp thật hoặc thành benchmark độc lập hoàn toàn. Nếu dùng một N-case để sửa prompt/code, ghi nhận thành development và tạo case mới thay thế trước khi đo.

## Bộ transcript mới

Pool: [prospective_eval_v2.json](../datasets/prospective_eval_v2.json). Phiếu đọc thuận tiện: [PROSPECTIVE_LABEL_WORKBOOK.md](PROSPECTIVE_LABEL_WORKBOOK.md). Tệp nhập riêng ở `samples/prospective_v2/N01.txt` đến N12.txt.

| Case | Độ khó dự kiến | Phạm vi nghiệp vụ |
| --- | --- | --- |
| N01 | Dễ | Đổi đơn vị giao hàng, phạm vi quyết định |
| N02 | Dễ | Đổi người, đổi hạn tài liệu |
| N03 | Dễ | Phản hồi và yêu cầu khách hàng |
| N04 | Vừa | Hủy cách làm, giữ nhu cầu, cách thay thế còn mở |
| N05 | Vừa | Vướng mắc và lời báo khắc phục chưa xác minh |
| N06 | Vừa | Thay ngưỡng, điều kiện AND, chưa đạt điều kiện |
| N07 | Vừa | Ngắt lời, đại từ mơ hồ, hạn tương đối |
| N08 | Vừa | Biên bản cũ và quyết định của buổi hiện tại |
| N09 | Dễ | Đoạn thử mic trước họp, kiểm tra không tạo cam kết |
| N10 | Vừa | Tri thức chưa chắc chắn, yêu cầu đối chiếu |
| N11 | Khó | 72 lượt nói, nhiều chủ đề, người/hạn/lịch riêng |
| N12 | Khó | 80 lượt nói, lịch cũ, hủy việc và mở lại cuối buổi |

Độ khó là dự đoán của người thiết kế, không phải cam kết dễ sẽ đúng hoặc khó sẽ sai. Transcript dài ở đây vẫn chỉ là dài đối với MVP, chưa đại diện cuộc họp nhiều giờ.

## Gán nhãn trước khi xem model

1. Bạn/người thứ hai đọc từng transcript từ phiếu, chưa chạy qua website/CLI. Ghi thông tin có giá trị sau cuộc họp, trạng thái cuối và nguồn chứng minh; không cần ép có đủ mọi loại trong từng case.
2. Điền `datasets/prospective_eval_v2_annotations.json`. `required_records: null` nghĩa là chưa gán nhãn; chỉ dùng `[]` khi đã xác định không có bản ghi bắt buộc và ghi `no_required_records_reason`.
3. Mỗi nhãn cần loại, nghĩa, trạng thái, người/hạn/điều kiện (ghi null nếu không có căn cứ), quote nguồn chính xác và nguồn từng trường. Mã nguồn theo parser: L001, L002…; quote bỏ tiền tố ID/người nói. Ghi thêm allowed_additional_records, forbidden_claims hoặc case_review_required khi cần. Bản ghi được chấp nhận thêm không tự tăng recall của required_records.
4. Không dùng ngày gán nhãn làm ngày họp; hạn tương đối không tự chuẩn hóa thành ngày tuyệt đối. Không biến lời nhắc chuyện cũ thành quyết định hiện hành, câu hỏi thành cam kết hoặc người đang nói thành owner.
5. Người đọc thật điền `reviewer`, `reviewed_at` theo ISO có múi giờ (ví dụ `2026-10-14T22:00:00+07:00`), `annotation_status: human_reviewed` và `labels_finalized_before_outputs: true`. Không tự đánh dấu thay cho một người chưa đọc.
6. Chạy kiểm tra nhãn, sau đó seal dataset. Các dấu xác nhận là tự khai, không phải đăng nhập hay chữ ký được xác thực.

```powershell
python scripts/prepare_prospective_eval.py
python scripts/prepare_prospective_eval.py --freeze
```

Hiện lệnh phải từ chối vì nhãn còn trống. `run_dataset.py` cũng chặn pool pending trước khi tạo client/gọi API. Không có tùy chọn bỏ qua gate cho pool này. Dataset frozen chỉ được tạo khi toàn bộ nhãn hợp lệ; không ghi đè một dataset đã seal.

Mẫu một nhãn (ví dụ riêng, KHÔNG là đáp án N01–N12):

```json
{
  "label_id": "example",
  "kind": "decision",
  "meaning": "Tổ chức buổi hướng dẫn vào sáng thứ Ba",
  "meeting_status": "agreed",
  "execution_status": "unknown",
  "authority_status": "unknown",
  "owner": null,
  "supporter": null,
  "due_raw": null,
  "due_iso": null,
  "condition": null,
  "evidence": [{"source_id": "L001", "quote": "Chốt tổ chức buổi hướng dẫn vào sáng thứ Ba."}],
  "field_evidence": {
    "content": [{"source_id": "L001", "quote": "Chốt tổ chức buổi hướng dẫn vào sáng thứ Ba."}],
    "meeting_status": [{"source_id": "L001", "quote": "Chốt tổ chức buổi hướng dẫn vào sáng thứ Ba."}]
  },
  "counter_evidence": [],
  "must_flag_for_review": false
}
```

Validator kiểm tra cấu trúc, hash và quote tồn tại, không tự chứng minh nhãn hiểu đúng ngữ nghĩa. Người gán nhãn vẫn cần giải quyết các trường hợp diễn đạt tương đương/mơ hồ và không dùng đầu ra AI để lấp nhãn.

## Quy tắc đo A/B cho các bước sau

- Đo cùng input/gold/model/config khi so sánh thay đổi code/prompt; ghi rõ nếu đổi model hoặc budget. Mỗi phiên bản có artifact riêng, không ghép kết quả thuận lợi từ nhiều phiên bản.
- Tám case hồi quy: kiểm tra lỗi cũ và regression. N-case seal: đánh giá prospective sau khi chốt ứng viên, không dùng để sửa trong lượt đo.
- Chấm semantic toàn bộ output và ghép một-một: required-record recall, supported-record precision, kết luận cuối, nguồn hỗ trợ, trường không-null và bỏ sót trường/bản ghi. Không dùng field accuracy trên null nhiều để che việc thiếu thông tin.
- Không tính F1 chung nếu precision chấp nhận extras nhưng recall chỉ xét tập gold cốt lõi; phải đồng nhất phạm vi nhãn trước.
- Tách completion/API/quota, lỗi trích xuất, lỗi resolver và cảnh báo audit sai. Findings rỗng không chứng minh không có lỗi.
- Chạy lặp một số case để quan sát độ ổn định; không chỉ giữ lần tốt nhất. Bản con người sửa/thêm không cộng vào điểm LLM.
- Không tự đặt ngưỡng rồi gọi đó là tiêu chí đạt bài tuyển chọn. Quyết định chọn B cần dựa trên cải thiện lỗi mục tiêu, không hỏng case đã tốt và minh bạch về thất bại còn lại.

## Hoàn thành và phần còn lại

Đã chuẩn bị checkpoint A, registry, bảng so sánh chưa có B, 12 transcript, phiếu/JSON nhãn và gate. Chưa có human labels, benchmark độc lập, candidate B hoặc điểm mới. Bước tiếp theo: sửa ba nhóm lỗi lõi trên dữ liệu phát triển/hồi quy; đồng thời người đọc chuẩn bị nhãn bộ mới trước khi chạy API.

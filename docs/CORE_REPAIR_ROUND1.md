# Sửa lõi — lượt 1

Mục tiêu: xác định HTTP 400 và sửa audit làm mất trạng thái hủy/mở lại/chưa chốt. Giữ nguyên dataset và báo cáo baseline 24 case; mọi phép thử tiếp theo lưu tệp riêng. Không bổ sung UI hoặc dependencies.

## Bằng chứng chẩn đoán

- Gọi lại bước extraction trên D09/D15/D16/H08 với cấu hình cũ: D09 chạy được; ba transcript dài trả `json_validate_failed`. Provider không trả nội dung `failed_generation` hữu ích. Không thể từ đó khẳng định model không hiểu tiếng Việt hay transcript dài.
- Chuyển riêng sang strict schema vẫn chưa giải quyết lỗi: D09/D15/D16/H08 tiếp tục HTTP 400 trong lượt `dataset_transport_audit_fix.json`.
- Đặt ngân sách 8192 ở D15: strict dùng hết 8192 completion tokens rồi chưa hoàn tất. Không dùng phản hồi thiếu. Các phép thử tiếp theo còn gặp giới hạn API.
- Request với budget 4096 bị HTTP 413: provider nêu **TPM limit 8000, requested 8586**. Đây là bằng chứng cụ thể về giới hạn request hiện tại, không phải giới hạn context window của model.
- D15 với strict + temperature 0.6 + reasoning low + budget 3072: extraction chạy được, 17 events, 4490 prompt tokens + 1853 completion tokens. Có lỗi nghiệp vụ trong các events nên không gọi đây là case đã đạt.

Các thử nghiệm thay đổi nhiều tham số chưa cô lập được tác động của từng tham số. Chỉ kết luận cấu hình mới đã tạo được đầu ra ở phép thử này; không kết luận một tham số riêng lẻ là nguyên nhân duy nhất của mọi HTTP 400.

## Thay đổi phần mềm

1. `LLMError` giữ mã HTTP và mã lỗi provider trong danh sách cho phép; không đưa provider message hoặc failed_generation vào thông báo sản phẩm. Với rate limit, chỉ trích loại TPM/TPD/RPM/RPD và các con số limit/used/requested.
2. Groq GPT-OSS 20B/120B tự dùng strict JSON Schema cho extraction và audit. Các provider khác giữ JSON mode; có tùy chọn `LLM_STRUCTURED_OUTPUTS=off/strict`. Vẫn kiểm tra Pydantic, nguồn và tương thích kind/event_type sau khi nhận kết quả.
3. Cấu hình mặc định cho Groq GPT-OSS: temperature 0.6, reasoning low, extraction budget 2560; audit budget 1024. Có thể cấu hình qua `.env`. Không tự tải model hoặc cài package.
4. Audit vẫn nhận toàn bộ transcript, events và records; bỏ các giá trị mặc định/null không cần thiết và topic lặp trong events, dùng JSON gọn để giảm token. Không cắt mất lượt phát biểu.
5. Audit mức high và audit bị lỗi không xóa trạng thái `open/proposed/reopened/withdrawn/cancelled`; vẫn đặt needs_review và giữ lý do. Các khẳng định đang có hiệu lực như agreed/assigned bị nghi ngờ vẫn chuyển unverified, không được tự coi là đã xác nhận.
6. Prompt nhấn mạnh hủy công việc phải là action_cancelled, chưa nhận/chưa giao việc không phải assignment; xác nhận lại cùng việc không tạo việc mới. Audit phân biệt lịch sử, chủ việc cũ, lựa chọn chưa chốt và thời gian xem lịch.

Tham khảo chính thức: [Groq Structured Outputs](https://console.groq.com/docs/structured-outputs), [Groq Reasoning](https://console.groq.com/docs/reasoning), [Groq API reference](https://console.groq.com/docs/api-reference). Schema đúng cấu trúc không bảo đảm dữ kiện đúng nghĩa.

## Kiểm chứng

**77/77 unit/contract tests đạt**. Đây là kiểm tra phần mềm với fixtures/transport mock, không phải điểm LLM.

Replay đúng extraction và findings đã lưu từ baseline:

| Case / bản ghi | Baseline sau audit | Sau sửa audit, cùng đầu ra model |
|---|---|---|
| D06 công việc bị hủy | unverified | cancelled + needs_review |
| D14 ngưỡng chưa chốt | unverified | open + needs_review |
| D14 quyết định chuyển tiền giả | unverified | vẫn unverified + needs_review |
| D02 rút lời chốt | unverified | withdrawn + needs_review; **vẫn sai với nhãn reopened do extraction cũ** |

Replay cô lập lỗi xử lý audit; không chứng minh model mới trả lời đúng. Lượt gọi mới D06 với strict đơn thuần vẫn phân loại hủy việc sai, nên đã bổ sung quy tắc extraction trước lượt kiểm chứng cấu hình cuối.

## Lượt toàn pipeline sau sửa

Lưu tại `docs/evaluation/dataset_core_round1.json` (bản làm việc ở `results/`). Cấu hình được giữ nguyên trong lượt: strict auto, temperature 0.6, reasoning low, extraction 2560, audit 1024, nghỉ 60 giây giữa attempts. Chỉ truyền transcript, không truyền nhãn.

**4/6 case trả được kết quả và hoàn tất audit; 2/6 dừng trước khi công bố kết quả. Không có HTTP 400 trong lượt cuối.** Đây là kết quả của một lượt kiểm chứng có mục tiêu, không phải điểm mới trên toàn bộ dataset 24 case.

| Case | Baseline 24 case | Lượt sau sửa | Đối chiếu nội dung / giới hạn |
|---|---|---|---|
| D06 | Pipeline chạy, trạng thái cuối unverified do audit | Pipeline + audit chạy | Đúng cancelled, Tuấn là người lịch sử, due_raw null. Audit vẫn false positive đòi xóa owner; không còn làm mất cancelled. Content chứa hạn cũ nhưng thuộc công việc đã hủy, không phải hạn hiện hành. |
| D09 | HTTP 400 | Pipeline + audit chạy | Đúng 5/6 mục về nghĩa/trạng thái: hai phân công, SSO nội bộ, feedback, câu chữ chưa chốt; thiếu issue staging. Có cảnh báo verifier phủ định sai chủ đề. |
| D14 | Tạo bản ghi chuyển tiền giả và đổi open thành unverified | Pipeline + audit chạy | Hai mục nghiệp vụ đúng, không còn bản ghi chuyển tiền giả. Audit lại cảnh báo thiếu quyết định chuyển tiền từ chuỗi thử nghiệm: vẫn là false positive, không tự thêm bản ghi. |
| D15 | HTTP 400 | Pipeline + audit chạy | Đúng 5/7 mục về nghĩa/trạng thái: thanh toán nhúng thay redirect; Châu/Bảo/thứ Hai; staging còn mở; feedback; request hướng dẫn. Thiếu action cấp quyền QA và decision câu chữ chưa chốt. Audit bắt được việc thiếu decision nhưng không bổ sung tự động. |
| D16 | HTTP 400 | Dừng, không dùng phản hồi thiếu | Provider báo 2560 completion tokens, adapter nhận phản hồi chưa hoàn tất. Cần thử budget lớn hơn trong giới hạn TPM hoặc giảm lượng đầu ra; chưa đủ dữ liệu để chấm ngữ nghĩa. Lượt này chưa lưu finish_reason chi tiết, không khẳng định thêm về nội dung bị thiếu. |
| H08 | HTTP 400 | Validator từ chối nhóm thiếu nội dung | L083 đổi hạn của bộ log mẫu nhưng model đặt key sample_log_deadline riêng, khác sample_log_assignment. Nhóm deadline_change không có sự kiện khởi tạo/nội dung nên bị từ chối. Raw events còn gán Vũ làm owner từ câu phủ định L084; không được công bố như kết quả đúng. |

Đối chiếu nội dung ở bảng này do cùng trợ lý đọc nguồn, chưa phải review độc lập và chưa tính precision/recall mới cho 24 case. Không thay thế hay lựa chọn lại kết quả baseline bằng các lượt tốt hơn.

## Tái lập và bước tiếp theo

```bat
python -m unittest discover -s tests -q
python scripts/replay_audit_fix.py
python scripts/run_dataset.py --ids D06 D09 D14 D15 D16 H08 --call-interval 60 --out results/NEW_run.json
```

Không dùng lại đường dẫn artifact đã có để chọn lại lần trả lời tốt nhất. `.env` cũ không cần sao chép lại; các cấu hình mới có mặc định trong client. Khởi động lại server web đang chạy để nạp mã mới.

Bước sau: làm chắc cập nhật điều kiện/hạn và độ đầy đủ trên case đại diện; giảm false positive audit; kiểm tra một tập mới trước khi tuyên bố điểm cải thiện. Với H08, cần sửa liên kết sự kiện cùng công việc và phủ định owner trước khi nghĩ đến UI bổ sung. Giới hạn ngân sách ở D16 và các lỗi ngữ nghĩa chưa được che giấu bằng việc tắt audit hoặc bỏ validator.

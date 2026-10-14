# Lượt 5 — giới hạn token/ngày và lỗi xóa hạn khi hủy việc

## Kiểm chứng API bị giới hạn

Giữ nguyên core lượt 4 để thử LC01–LC03. Lượt đầu LC01 HTTP 429 yêu cầu chờ 582 giây. Bộ chạy dừng ngay; LC02/LC03 chưa được gọi. Một request ping rất nhỏ (144 token usage) hoàn tất; đây là kiểm tra kết nối, không phải đánh giá transcript.

Lượt thử tiếp theo tắt retry để lấy diagnostics an toàn: API báo `rate_limit_exceeded`, đơn vị **TPD**, limit **200000**, used **197915**, requested **2436**. Đây là số liệu tài khoản/model tại lần gọi này, không phải khẳng định giới hạn chung của Groq. Không suy ra thời điểm reset chính xác. Chưa gọi hồi quy H03 trong lượt này để tránh thêm request khi thiếu quota.

Artifact: `dataset_lifecycle_round4_check.json`, `rate_limit_diagnosis_round4.json`, `dataset_lifecycle_round4_verified.json` trong `docs/evaluation`. Các lỗi không thay thế đầu ra cũ. Hai lượt LC đều dừng ở case đầu, không được tính là ba transcript model trả sai.

Runner bổ sung `--stop-on-rate-limit`, dừng cả khi audit gặp 429; `--max-retries 0` cho phép lấy diagnostics ngay, lưu status/code/diagnostics đã được adapter lọc. Không ghi raw provider error body, rejected generation hoặc key. Resume không được đổi max_retries so với artifact cũ. Không đổi provider/model/prompt để né giới hạn và không gọi kết quả giả là model thật.

## Lỗi phần mềm tái hiện từ LC02/LC03

Đã viết contract test với transcript LC01–LC03 và events viết tay; chúng không đo khả năng trích xuất của LLM. Hai case thất bại trước sửa: action_cancelled có clear_fields=[due_raw] nhưng resolver bỏ qua danh sách này, khiến hạn cũ vẫn nằm ở bản ghi đã hủy.

Đã sửa action_cancelled chỉ áp dụng các trường **được chỉ rõ trong clear_fields** và cập nhật field_evidence_ids. Bỏ due_raw thì xóa cả due_iso; bỏ condition thì trạng thái triển khai về unknown. Hủy việc không có lệnh xóa vẫn giữ owner/deadline lịch sử; các giá trị cập nhật mới đặt nhầm trong event hủy không được dùng để tái giao việc.

Ví dụ LC02: hủy việc thử thư viện X và bỏ hạn chiều mai → action cancelled, owner lịch sử Dũng, due_raw null; request CSV vẫn recorded và phương án thay thế vẫn open. LC03: hủy viết hướng dẫn không mở rộng/hủy quyết định thử nội bộ hoặc yêu cầu nút quay lại.

**105/105 test phần mềm đạt.** Năm test mới gồm ba tình huống nghiệp vụ và hai kiểm tra xóa trường/giữ lịch sử. `request_task_guard_replay_round5.json` phát lại extraction đã lưu qua core mới, trước audit; kiểm tra hẹp trên hai biến thể D06, H01, H03 đều đạt. Không phải một lượt API mới hay metric model.

## Trạng thái và bước tiếp theo

Đã tổng hợp [bảng tình huống Mission 2](MISSION2_TEST_CASES.md) theo format kỳ vọng → thực tế → đạt/chưa đạt → điều học được, kèm phiên bản và artifact. Không cộng kết quả nhiều prompt thành accuracy hiện tại.

Core hiện tại có thêm sửa resolver, nên chưa có đánh giá end-to-end bằng API cho toàn phiên bản này. Prompt không đổi trong lượt 5. Các việc còn lại: chạy LC01–LC03/H03 khi đủ quota; kiểm chứng audit và bản ghi thừa D06; chọn case demo dựa trên bằng chứng, giữ lỗi/hạn chế thật. Chưa mở rộng UI và chưa chốt lõi là hoàn hảo.

```powershell
python -m unittest discover -s tests -q
python scripts/run_dataset.py --dataset datasets/task_lifecycle_regression_v1.json --ids LC01 LC02 LC03 --call-interval 90 --stop-on-rate-limit --max-retries 0 --out results/NEW_lifecycle.json
python scripts/run_dataset.py --ids H03 --call-interval 90 --stop-on-rate-limit --max-retries 0 --out results/NEW_h03.json
```

Sau khi quota hồi phục, mỗi lần thử mới dùng output mới để giữ lỗi cũ. Manifest `docs/evaluation/core_round5_manifest.json` lưu hash phiên bản core/dataset/tests hiện tại; số test phần mềm không thay thế kiểm chứng LLM. Baseline 24 case và nhãn không thay đổi.


## Lượt kiểm chứng bổ sung bằng core hiện tại

Artifact mới: [dataset_lifecycle_round5_check.json](evaluation/dataset_lifecycle_round5_check.json), [review](evaluation/lifecycle_round5_review.json). Hash core, dataset và tests vẫn khớp manifest lượt 5; không sửa prompt/model trong lượt này.

| Case | Kỳ vọng → thực tế | Đạt/Chưa đạt → điều học được |
|---|---|---|
| LC01 | Một action cancelled, Mai, hạn null, không record phụ → action đúng nhưng còn request trùng, recorded và giữ hạn sáng thứ Sáu; guard needs_review, audit finding high dẫn L004 | Chưa đạt đầy đủ. Phát hiện lỗi không đồng nghĩa sửa được lỗi; không coi request đã có nguồn là dữ liệu đáng tin cậy để tự dùng |
| LC02 | Giữ yêu cầu CSV khi hủy việc thử → extraction bị HTTP 429 TPD, limit 200000/used 198312/requested 2791 | Chưa đánh giá nội dung; đây là giới hạn vận hành |
| LC03 | Giữ scope và request độc lập → chưa gọi vì dừng ở 429 | Chưa đánh giá |
| H03 | Hồi quy bằng core lượt 5 → chưa gọi sau khi quota chặn | Chưa đánh giá phiên bản hiện tại; kết quả prompt lượt 3 vẫn là bằng chứng lịch sử riêng |

LC01 chạy đủ extraction và audit, provider báo tổng 4793 tokens, gồm prompt 3803 và completion 990. Toàn bộ lượt có 3 API attempts: 2 cho LC01, 1 LC02 bị chặn. Chỉ 2/3 case LC đã được thử; artifact complete=false được giữ nguyên. Không tính các case chưa gọi là model trả sai và không xuất precision/recall mới.

Kết quả LC01 xác nhận guard trùng request/action hoạt động với đầu ra LLM mới, đồng thời audit đã cảnh báo hạn cũ chưa cập nhật trên request. Vẫn giữ nguyên request và bằng chứng để người dùng rà soát; không tuyên bố lỗi phân loại vòng đời công việc đã hết. Không có thay đổi core trong lượt bổ sung này.


## Hồi quy LC02 và chuẩn bị demo

Artifact: [dataset_lifecycle_round5_remaining.json](evaluation/dataset_lifecycle_round5_remaining.json), [review](evaluation/lifecycle_round5_remaining_review.json). Hash core/tests/config vẫn khớp manifest lượt 5. Không đổi prompt/model.

LC02 extraction giữ đúng request CSV, action cancelled với owner lịch sử Dũng và decision open cho cách thay thế. Tuy nhiên due_raw vẫn là "chiều mai", trái câu L004 "bỏ hạn chiều mai". Model trả action_cancelled với clear_fields=[]; vì không nhận được lệnh xóa, resolver giữ hạn lịch sử. Bản sửa áp dụng clear_fields khi có giá trị vẫn qua contract test; lỗi mới quan sát là model bỏ sót trường xóa, không phải handler tiếp tục bỏ qua danh sách đã được cung cấp. Không suy đoán chắc chắn nguyên nhân bên trong model.

**LC02 chưa đạt nội dung**, không chỉ là lỗi quota. Audit HTTP 429 TPD (limit 200000, used 199798, requested 2255), nên chưa hoàn tất kiểm chứng hai bước. Bộ chạy dừng trước LC03; H03 chưa được gọi. Không tự xóa hạn bằng suy đoán hoặc sửa JSON đã lưu.

Đã cập nhật README, bỏ các mục hiện tại còn nói chưa có API/UI, và thêm [runbook demo](DEMO_RUNBOOK.md) gồm chạy local, kịch bản ≤5 phút, phân biệt live API với walkthrough artifact, checklist còn thiếu. Đây là chuẩn bị đóng gói, chưa phải xác nhận sẵn sàng nộp: hồi quy LC03/H03 vẫn thiếu; repo public, deploy và video chưa được xác nhận.

Giữ phiên bản hiện tại và hai lỗi thực tế LC01/LC02 để giải thích hạn chế. Lượt này không chỉnh thêm core và không cộng kết quả các phiên bản thành metric mới. Còn cần quota cho LC03/H03 hoặc công khai chúng chưa kiểm chứng khi chốt demo; không gọi các case này là đã đạt.

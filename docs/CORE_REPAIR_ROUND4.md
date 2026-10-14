# Sửa lõi lượt 4 — vòng đời công việc và kiểm chứng phần còn thiếu

## Kiểm chứng bổ sung cho phiên bản lượt 3

Giữ nguyên core/prompt lượt 3 trước khi sửa D06:

- `dataset_core_round3_h03_followup.json`: HTTP 429 ở extraction, yêu cầu chờ 104 giây. Giữ lỗi này trong artifact.
- `audit_h01_round3_followup.json`: sau cooldown, dùng lại extraction thật H01 từ lượt retry cũ và gọi audit mới. Hoàn tất, findings rỗng; records giữ reopened/condition null và action Huy assigned, không hạn. Đây chỉ là re-audit, không phải một lượt extraction/pipeline mới. Một lần hết false positive không chứng minh audit luôn đúng.
- `dataset_core_round3_h03_verified.json`: chạy mới cả pipeline H03, audit hoàn tất và không finding. Có request rà soát email và decision open với câu chưa chọn ngày/chưa giao người, nguồn kết luận L006. Không tự chọn thứ Tư/thứ Năm, không tự gán owner. Model vẫn trả due_raw null; resolver giữ cụm nguyên văn "trước lần thử tiếp theo" từ nội dung/câu nguồn, đánh dấu needs_review. Vì vậy hệ thống đạt các kiểm tra trọng tâm ở lượt này, nhưng không tuyên bố model tự trích đủ mọi trường.

Các kết quả trên thuộc phiên bản lượt 3; không dùng chúng làm điểm hồi quy của prompt lượt 4 phía dưới. Không ghi đè các lỗi 429 cũ hoặc baseline 24 case.

## Thay đổi lượt 4 và lý do

D06 trước đó có action đã hủy đúng, nhưng model còn tạo request chỉ lặp câu giao việc và decision/withdrawal chỉ lặp xác nhận dừng việc. Audit không phát hiện. Lượt này sửa prompt extraction để:

1. Nhận diện câu giao trực tiếp có tên người và công việc là assignment; câu nhận việc xác nhận cùng action, không tạo request phụ.
2. Giữ vòng đời công việc trong kind action; câu dừng việc đã nhận không biến thành decision/withdrawal riêng.
3. Vẫn giữ request nghiệp vụ và decision độc lập có bằng chứng riêng, kể cả khi action liên quan bị hủy.

Prompt audit bổ sung kiểm tra bản ghi thừa theo vòng đời công việc, đồng thời tránh xóa nhầm yêu cầu khách hàng hoặc phạm vi đã chốt. Không gộp/xóa bản ghi bằng từ khóa trong resolver. Không đổi model, context window, schema, ngân sách đầu ra hay cấu hình low/0.6. Không train model và không cài dependencies.

95/95 test phần mềm đạt sau thay đổi. Đây không phải 95 transcript LLM đúng.

## Bộ phản ví dụ

`datasets/task_lifecycle_regression_v1.json` có ba transcript tổng hợp, nhãn/tiêu chí do cùng trợ lý viết, chưa có review độc lập:

- LC01: giao trực tiếp rồi hủy; không tạo request/decision phụ.
- LC02: hủy việc thử thư viện nhưng yêu cầu CSV vẫn giữ; cách thay thế chưa chốt.
- LC03: hủy viết hướng dẫn nhưng quyết định thử nội bộ và yêu cầu nút quay lại vẫn giữ.

Các nhãn không gửi vào API. Chúng là bộ hồi quy phát triển, không phải benchmark độc lập. Đánh giá phải xem cả bản ghi bắt buộc và bản ghi thừa; không xem audit trống là bằng chứng đủ.

## Kết quả prompt mới trên D06

Artifact: `docs/evaluation/dataset_core_round4_d06.json`. Extraction mới không còn decision/withdrawal phụ, giữ action cancelled, owner lịch sử Tuấn và bỏ hạn. Tuy nhiên **request lặp câu giao việc vẫn còn**. Chưa đạt đầy đủ tiêu chí D06. Audit HTTP 429 yêu cầu chờ 955 giây, nên chưa kiểm chứng được prompt audit mới.

Đây là kết quả trước khi thêm guard phần mềm bên dưới. Không xem việc giảm từ ba xuống hai record là bằng chứng lỗi đã được giải quyết. Không tiếp tục gọi API trong lượt này sau lần thử lại có kiểm soát và giới hạn gần 16 phút; LC01–LC03 **chưa được chạy qua API**.

## Guard phần mềm cho request trùng việc đã hủy

Đã bổ sung kiểm tra hẹp trong verifier: chỉ khi request còn recorded và action cancelled có cùng issue_key, nội dung trùng sau chuẩn hóa chữ hoa/khoảng trắng/dấu câu, các nguồn đều có thật và nguồn request nằm trước nguồn trạng thái hủy. Khi đó request chuyển review_status thành needs_review, với cảnh báo nêu nguồn yêu cầu và nguồn hủy. Không đổi meeting_status, không xóa/gộp bản ghi, không tự rút yêu cầu hoặc thay owner/deadline. Nguồn request xuất hiện sau khi hủy không bị quy tắc này đánh dấu, để giữ khả năng yêu cầu được khẳng định lại.

Đây chỉ là tín hiệu rủi ro: hai bản ghi cùng key/nội dung vẫn có thể là yêu cầu độc lập hợp lệ; ngược lại, khác cách diễn đạt hoặc key có thể khiến guard bỏ sót. Nó giảm khả năng bản ghi thừa trông như đã được chấp nhận, chưa sửa khả năng phân loại của LLM. UI đã có review_status/warnings nên không cần thay schema hoặc thêm giao diện mới.

**100/100 test phần mềm đạt**, gồm 5 test mới kiểm tra: cảnh báo không xóa dữ liệu/không lặp cảnh báo; không cảnh báo khi khác nội dung; khác key; nguồn khẳng định request sau khi hủy; và task chưa bị hủy. Các test dùng sự kiện viết tay, không phải metric LLM.

`docs/evaluation/request_task_guard_replay.json` phát lại bốn đầu ra extraction thật đã lưu (hai biến thể D06, H01, H03) qua core mới, **trước audit**, không gọi LLM/audit mới. Tất cả kiểm tra hẹp đạt: hai D06 được cảnh báo; H01/H03 không bị cảnh báo này; số bản ghi/nội dung/trạng thái được giữ nguyên; request H03 vẫn giữ hạn nguyên văn. Đây không phải bốn transcript độc lập và không phải accuracy mới.

## Vị trí và việc còn lại

Đã xác nhận bằng API rằng prompt lượt 3 có thể trích kết luận H03 và audit H01 không còn cảnh báo sai trong một lượt. Prompt lượt 4 giảm một loại bản ghi thừa ở D06 nhưng chưa loại bỏ request thừa; guard mới chỉ yêu cầu rà soát. Chưa có hồi quy API H03/H01 bằng prompt lượt 4 và chưa chạy LC01–LC03 qua model. Không lấy kết quả prompt lượt 3 để khẳng định prompt mới không regression.

Ưu tiên kế tiếp sau cooldown: chạy LC01–LC03 và H03 với cùng code/config đã chốt, rồi chọn phiên bản demo dựa trên kết quả, không tiếp tục mở rộng prompt nếu chưa có bằng chứng. D06 có thể dùng làm ví dụ giới hạn thật kèm nguyên nhân model phân loại sai vòng đời công việc và cách hệ thống đánh dấu rủi ro. Transcript dài/H08 vẫn cần kiểm chứng riêng. Chưa mở rộng UI hoặc tuyên bố lõi hoàn hảo.

## Tái lập

```powershell
python -m unittest discover -s tests -q
python scripts/run_dataset.py --dataset datasets/task_lifecycle_regression_v1.json --ids LC01 LC02 LC03 --call-interval 90 --out results/NEW_lifecycle.json
python scripts/run_dataset.py --ids H03 --call-interval 90 --out results/NEW_h03_round4.json
```

Đầu ra mới phải lưu riêng. `scripts/replay_task_lifecycle_guard.py` là kiểm tra bằng extraction đã lưu; khi chạy lại với artifact trước đó còn tồn tại, script dừng để giữ nguyên bằng chứng. `scripts/probe_audit_payload.py` nay hỗ trợ chọn source/IDs/output/interval, lưu phản hồi thô cùng hash và cấu hình, giúp kiểm tra riêng audit mà không trả phí extraction lần nữa. Các file trong `docs/evaluation` đã được kiểm tra JSON và không chứa khóa API được cấu hình. Không thay baseline 24 case hoặc nhãn của nó.

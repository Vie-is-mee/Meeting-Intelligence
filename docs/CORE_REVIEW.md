# Rà soát và sửa lỗi lõi — 12/10/2026

Phạm vi: phần mềm xử lý transcript, phân giải sự kiện, kiểm tra nguồn, audit,
bộ chấm và adapter API. Chưa làm UI/UX, deploy hoặc tính năng tích hợp.

## Lỗi được tái hiện và sửa

| Vấn đề | Hành vi sau sửa |
|---|---|
| Sự kiện sửa dẫn câu cũ và câu mới bị xếp theo câu cũ | Áp dụng tại lượt nói mới nhất trong nguồn; prompt yêu cầu không dẫn câu tương lai cho sự kiện trước đó |
| Đổi người giữ người hỗ trợ trùng người phụ trách mới | Bỏ vai trò hỗ trợ trùng; không tự đoán người hỗ trợ thay thế |
| Đổi người chưa biết người mới vẫn giữ người cũ | Xóa người cũ và giữ bản ghi `unverified` để rà soát |
| Không biểu diễn được việc bỏ deadline/điều kiện | `Event.clear_fields` ghi rõ trường bị thu hồi; null đơn thuần không xóa dữ liệu cũ |
| Tên hoặc phương án xuất hiện trong lịch sử cũ được dùng để hợp thức hóa giá trị mới sai | `field_evidence_ids` liên kết các giá trị với sự kiện cập nhật chúng |
| “Lan: Tôi làm” bị xóa Lan vì tên chỉ nằm ở metadata | Kiểm tra cả speaker của lượt nói được dẫn |
| Audit `{}` được coi là không phát hiện lỗi | Bắt buộc có trường `findings`; sai mẫu kích hoạt xử lý audit lỗi |
| Audit thiếu dữ liệu supporter/deadline/condition | Gửi bản ghi đầy đủ, không lặp history đã gửi ở events |
| Decision/action chung issue_key làm audit chỉ áp dụng mục cuối | Finding có thể chỉ rõ kind; thiếu kind thì giữ mọi bản ghi cùng key để rà soát |
| Một bản ghi khớp nhiều kỳ vọng; bản ghi dư không bị chấm | Ghép một-một, kiểm tra dư, thêm kiểm tra supporter/condition khi đáp án có nhãn |
| Phản hồi bị cắt vẫn được nhận nếu JSON tình cờ hợp lệ | Từ chối finish_reason khác stop; vẫn hỗ trợ provider không trả trường này |
| Retry quá sớm khi provider yêu cầu chờ | Tôn trọng Retry-After dạng số giây trong giới hạn chờ cấu hình |

Báo cáo tình huống giờ lưu đầy đủ bản ghi, lịch sử, cảnh báo và chi tiết audit
để không mất các trường cần phân tích. CLI thêm `--audit on/off`, đọc UTF-8 BOM
và báo lỗi cấu hình/tệp/API bằng thông báo cùng exit code khác 0.

## Kiểm chứng phần mềm

```powershell
python -X utf8 -m unittest discover -s tests -v
python -X utf8 scripts/run_contract_fixtures.py
python -X utf8 scripts/run_scenarios.py --engine offline_rules --ids T02 T03 T04 --out results/offline_core_review.json
```

Trước sửa: 23 kiểm thử cũ đạt; bộ hồi quy mới tái hiện lỗi ngoài độ bao phủ cũ.
Sau sửa, đã chạy lại và quan sát:

- 45/45 unit/contract tests đạt, gồm 22 kiểm thử mới.
- 7/7 fixture T01–T07 đạt với bộ chấm một-một.
- 3/3 ca offline T02/T03/T04 đạt.
- CLI chạy offline, lưu JSON và báo lỗi tệp không tồn tại đạt kiểm tra smoke.
- 0 lần gọi LLM thật trong đợt rà soát này vì chưa có khóa trong môi trường.

Các fixture T01–T07 là sự kiện viết tay. Offline engine là regex có phạm vi hẹp.
Không xem các số trên là độ chính xác của Groq hoặc của bất kỳ LLM nào.

## Giới hạn chưa được giải quyết bằng các bản sửa này

- Chưa có kết quả gọi Groq/LLM thật trong môi trường làm việc; không suy ra độ chính xác AI từ unit tests.
- LLM vẫn có thể ghép sai chủ đề, bỏ sự kiện hoặc diễn giải sai; audit không bảo đảm bắt được lỗi đó.
- Có tên trong nguồn không chứng minh người đó được giao việc. Kiểm tra từng trường ở đây là kiểm tra từ ngữ và mã nguồn, chưa phải bộ chấm ngữ nghĩa hoàn chỉnh.
- Thứ tự trong cùng một lượt nói phụ thuộc thứ tự events được trích; cần thử bằng model thật với câu chứa nhiều thay đổi.
- Regex phủ định muộn có thể cảnh báo nhầm chủ đề khác; cảnh báo này không tự thay thế kết luận.
- `clear_fields` dựa vào LLM nhận diện đúng việc thu hồi; việc null không còn đồng nghĩa tự động xóa trường cũ.
- Bộ đánh giá độc lập và so sánh audit on/off bằng API thật còn phải thực hiện.

## Bước tiếp theo

Cấu hình Groq theo README, chạy các ca lõi T02/T03/T04/T05 trước và lưu kết quả
nguyên trạng. Phân biệt lỗi API/quota với lỗi ngữ nghĩa; chỉ sửa prompt từ lỗi
đã quan sát. Sau đó đánh giá bao phủ và bộ ca độc lập, trước khi làm UI.

# Bộ hồi quy để chốt bản demo

Cập nhật mới nhất: [đã chạy đủ bộ hồi quy 8 case cùng phiên bản](FINAL_REGRESSION_RESULTS.md), gồm cả đạt/chưa đạt và lỗi audit. Các ghi chú quota/phiên bản trước trong tài liệu này là lịch sử, không thay thế lượt mới.

Giữ nguyên core, model và cấu hình. Không chỉnh prompt trong khi đo. Bộ này gồm các case phát triển đã biết; không phải đánh giá độc lập và không thay baseline 24 case.

| Thứ tự | Case | Tiêu chí chính | Bằng chứng core hiện tại trước lượt đầy đủ |
|---|---|---|---|
| 1 | H03 | Request/hạn tương đối; chưa chọn ngày, không tự gán người | Chưa có hồi quy toàn pipeline bằng core hiện tại |
| 2 | LC03 | Hủy hướng dẫn nhưng giữ scope thử nội bộ và request nút quay lại | Lượt mới nhất extraction HTTP 429 TPD, chưa có nội dung |
| 3 | D01 | Bỏ lưu trên máy chủ, chốt object storage cho bản thử nghiệm; nhà cung cấp chưa chọn | Kết quả các phiên bản trước không thay thế hồi quy hiện tại |
| 4 | D03 | Giữ phạm vi thiết kế, agreed/blocked, điều kiện pháp chế và issue hợp đồng | Chưa có kết quả đầy đủ core hiện tại |
| 5 | D04 | Điều kiện cuối 300 người và không lỗi nghiêm trọng, chưa xác nhận đạt | Chưa có kết quả đầy đủ core hiện tại |
| 6 | H01 | Reopened, condition null; việc Huy còn tồn tại, không hạn tự đặt | Audit riêng prompt lượt 3 từng đạt; chưa có toàn pipeline hiện tại |
| 7 | LC01 | Hủy task, bỏ hạn; không request/decision thừa | Có kết quả core hiện tại: task đúng nhưng request thừa, guard/audit cảnh báo; chưa đạt đầy đủ |
| 8 | LC02 | Request CSV giữ; task thư viện X hủy, bỏ hạn; cách thay thế chưa chọn | Có extraction hiện tại: bỏ sót clear_fields nên giữ hạn cũ; audit TPD; chưa đạt |

`scripts/prepare_final_regression.py` lấy nguyên transcript/nhãn từ hai dataset nguồn, giữ provenance/hash và thứ tự trên. Không gửi nhãn vào model; dùng runner hiện có chỉ truyền transcript. Bản chuẩn bị cuối: `docs/evaluation/final_regression_input_v2.json`. Nó là input/plan, không phải kết quả API.

## Một lệnh để thu thập khi đủ quota

Tại thư mục dự án:

```powershell
& 'I:\Python\python.exe' -X utf8 scripts/prepare_final_regression.py --run
```

Mặc định tạo/kiểm tra input `results/final_regression_input_v2.json`, lưu output `results/final_regression_round5_v2.json`, cách lần gọi 90 giây, max_retries=0, dừng ngay ở HTTP 429 cả khi lỗi xuất hiện trong audit. Chuẩn bị input mà không gọi API:

```powershell
python scripts/prepare_final_regression.py
```

Nếu core/nguồn thay đổi, script từ chối dùng lại input. Chọn --input/--out mới để không xóa artifact. Runner resume giữ nguyên các lượt lỗi đã ghi; không tự thử lại hoặc biến lỗi quota thành kết quả đạt. Muốn một lượt mới phải dùng output mới, và không thay baseline bằng lượt thuận lợi nhất.

## Đọc kết quả và điểm dừng

- Ghi riêng: hoàn tất extraction, audit, trường/evidence đúng, bản ghi thiếu/thừa và lỗi vận hành. `complete=true` chỉ nghĩa tất cả case đã được thử, không nghĩa đều đúng.
- Review semantic bằng transcript và nhãn; không coi JSON hợp schema, audit trống hoặc unit tests đạt là accuracy LLM. Không cộng những lượt khác phiên bản thành một điểm mới.
- Nếu có kết luận cuối sai hoặc giao việc không tồn tại mà không được cảnh báo, ưu tiên một sửa đổi có mục tiêu và chạy lại hồi quy. Nếu giữ lỗi có cảnh báo để demo, công khai đó là thất bại, chưa phải dữ liệu đúng để tự dùng.
- Chốt phiên bản theo bằng chứng và thời gian nộp; không yêu cầu mọi case đạt. Nếu quota khiến một số case chưa chạy, ghi rõ chưa kiểm chứng và không tuyên bố hồi quy hoàn tất.

Lần thử LC03 gần nhất: API báo TPD limit 200000, used 199071, requested 2521; request bị chặn trước extraction. Artifact `dataset_lc03_round5_finalcheck.json` ghi đúng core/config. Không gọi thêm H03 hoặc nhóm đại diện ngay sau lỗi này.

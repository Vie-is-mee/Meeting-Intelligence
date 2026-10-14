# Sửa lõi lượt 3 — giữ phạm vi và kết luận cuối

## Giả thuyết và thay đổi

Model có lúc bỏ mô tả của proposal/counterproposal, không trích câu chưa chọn ở cuối cuộc họp, hoặc rút ngắn nội dung làm mất phạm vi quyết định. Lượt này bổ sung checklist trong prompt extraction: value có nội dung, giữ giới hạn phạm vi, đọc lại kết luận cuối, phân biệt request với assignment và giữ riêng vấn đề hiện hữu. Prompt audit được làm rõ rằng điều kiện lịch sử không cần khôi phục sau reopen/withdrawal nếu không có phát biểu mới kích hoạt lại.

Không đổi context window, model, nhãn dataset, schema, ngân sách đầu ra hay resolver. Không thêm cơ chế tự tạo sự kiện bị thiếu. Không cài thêm dependencies. Checklist là hướng dẫn chung, không gửi gold labels/ID case cho model. Tuy nhiên các case này đã dùng để sửa prompt nên không phải tập đánh giá độc lập.

## Kiểm chứng cố định

95/95 test phần mềm đạt sau thay đổi. Lượt API dùng `openai/gpt-oss-120b`, low/0.6, strict schema tự động, extraction 2560 token và audit 1024 token, cách lần gọi tối thiểu 45 giây. Artifact lưu code hash, output nguyên gốc, usage và lỗi.

Sáu case cố định được chọn trước khi xem kết quả lượt này:

| Case | Điều cần kiểm tra |
|---|---|
| D03 | Quyết định agreed/blocked, giữ phạm vi thiết kế, điều kiện pháp chế, issue hợp đồng riêng |
| D04 | Conditional/pending_condition, thay 500 thành 300 và không lỗi nghiêm trọng, không tuyên bố test đã đạt |
| D06 | Công việc cancelled, hạn đã xóa, owner lịch sử Tuấn, không phát sinh giao việc thay thế |
| D14 | Không tạo quyết định chuyển tiền từ chỉ dẫn giả; giữ request đăng nhập và ngưỡng chưa chốt |
| H01 | Reopened, condition null; việc Huy vẫn assigned và không tự đặt hạn |
| H03 | Giữ request/hạn tương đối, kết luận chưa chọn ngày, không gán owner hay chốt thứ Tư/thứ Năm |

Đánh giá bằng đọc transcript/nhãn/đầu ra; chưa có người review độc lập. Tỷ lệ hoàn tất API và kết quả nội dung được báo riêng. Một lần sinh mỗi transcript chưa đủ đo độ ổn định. Kết quả audit trống không tự chứng minh nội dung đúng.

## Chạy lại

Lượt đầu được lưu nguyên vẹn ở `docs/evaluation/dataset_core_round3.json`: 4/6 trả kết quả ứng dụng, nhưng chỉ 3/6 hoàn tất cả extraction và audit. D14 lỗi audit HTTP 429; H01/H03 lỗi HTTP 429 ở extraction. Không tính các lỗi này là bằng chứng model hiểu sai transcript. Lượt thử lại sau cooldown phải được lưu riêng, không ghi đè hoặc xóa thất bại lượt đầu.

| Case | Kết quả lượt đầu | Đạt/Chưa đạt → điều học được |
|---|---|---|
| D03 | Giữ phạm vi thiết kế, agreed/blocked, điều kiện pháp chế và issue hợp đồng riêng; nguồn từng trường phù hợp; audit trống | Đạt các tiêu chí case trong lượt này; cần nhiều lần sinh để biết độ ổn định |
| D04 | Conditional/pending_condition; đủ hai điều kiện mới, nguồn L003; không tự gán người; audit trống | Đạt các tiêu chí case trong lượt này; không suy ra mọi biến thể điều kiện đều đúng |
| D06 | Action cancelled, Tuấn là owner lịch sử, due_raw null; thêm request chưa rút và decision/withdrawn thừa cho cùng báo cáo; audit trống | Chưa đạt đầy đủ; giữ đúng trạng thái task chưa đủ nếu tạo dữ liệu thừa gây hiểu nhầm |
| D14 | Không tạo quyết định chuyển tiền; có request giới hạn đăng nhập và ngưỡng open. Mô tả unresolved được phần mềm lấy nguyên văn nguồn; audit HTTP 429 | Nội dung trích xuất đúng trọng tâm, chưa hoàn tất audit; không xem đây là kết quả model tự sinh hoàn hảo |
| H01 | Extraction HTTP 429 | Chưa có kết quả nội dung ở lượt này |
| H03 | Extraction HTTP 429 | Chưa có kết quả nội dung ở lượt này |

Không sửa thêm prompt trong khi đang đo. Đầu ra D06 cho thấy checklist bổ sung chưa ngăn được việc chia một công việc thành các loại bản ghi thừa. Không loại bỏ các bản ghi bằng quy tắc gộp theo từ khóa vì có thể xóa các request/decision độc lập hợp lệ.

## Thử lại sau cooldown và giới hạn hiện tại

Artifact riêng: `docs/evaluation/dataset_core_round3_retry.json`. Giữ nguyên code/prompt/config, tăng khoảng cách lần gọi lên 90 giây, chỉ thử lại H01/H03 một lượt sau cooldown. Không thay kết quả lượt đầu bằng kết quả thuận lợi hơn.

- H01: extraction đúng conditional_agreement → reopen, condition null; assignment Huy và không hạn; thêm issue quyền đọc hợp lệ. Tuy nhiên audit gặp HTTP 429 yêu cầu chờ 591 giây. Do guard khi audit lỗi, action đầu ra ứng dụng là **unverified**, không phải assigned đã xác nhận. Vì vậy phần trích xuất đúng trọng tâm nhưng toàn pipeline chưa đạt; chưa kiểm chứng được prompt audit mới có giảm false positive H01 hay không.
- H03: vẫn HTTP 429 trước khi nhận extraction, yêu cầu chờ 569 giây. **Chưa có bằng chứng API cho việc sửa H03 ở phiên bản này.** Không kết luận model đã sửa được lỗi, cũng không coi 429 là một lỗi hiểu kết luận cuối.

Không tiếp tục lặp API trong lượt làm việc này vì thời gian chờ đã gần 10 phút và lần thử lại có kiểm soát vẫn bị giới hạn. Thông báo hiện có không đủ để khẳng định đây là giới hạn ngày hay phút. Hai artifact giữ cả lỗi và thời gian chờ; không có kết quả giả thay API.

## Kết luận và bước tiếp theo

Đã có bằng chứng cải thiện D03 trong một lần sinh: lấy lại phạm vi và issue riêng. D04 không regression trong lần sinh này. Nhưng D06 còn dữ liệu thừa, H03 chưa kiểm chứng vì API, audit H01 mới chưa kiểm chứng. Chưa tính precision/recall mới toàn dataset và chưa chốt phiên bản demo là ổn định.

Khi API cho phép, ưu tiên chạy lại H03 và audit H01 với đúng phiên bản đã lưu hash, ghi output mới. Sau đó kiểm tra lỗi D06 phân loại một công việc thành request/action/decision; chỉ thay prompt nếu có tiêu chí hồi quy rõ ràng. Cần thêm transcript mới chưa dùng để sửa prompt và kiểm tra nhiều lần sinh trước khi tuyên bố khả năng tổng quát. Chưa mở rộng UI trong lượt này.

Hai file artifact có code/dataset hash và cấu hình sinh. Dataset tổng hợp, nhãn do cùng trợ lý tạo/review, chưa có đánh giá độc lập. Các kết quả trước vẫn được giữ nguyên trong báo cáo lượt 1/lượt 2 và baseline.

```powershell
python -m unittest discover -s tests -q
python scripts/run_dataset.py --ids D03 D04 D06 D14 H01 H03 --call-interval 45 --out results/NEW_round3.json
```

Mỗi phiên bản/cấu hình phải dùng output mới; không ghi đè baseline hoặc trộn điểm các lượt.

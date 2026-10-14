# Website kiểm chứng local — 12/10/2026

Đợt kiểm thử Groq tiếp theo và các sửa lỗi lõi được ghi ở
[LLM_EVALUATION.md](LLM_EVALUATION.md). Các lượt T03 mô tả bên dưới là lịch sử
kiểm chứng giao diện ban đầu, không đại diện cho toàn bộ kết quả mới.

## Chức năng đã có

- Nhập/dán transcript hoặc mở tệp `.txt`; chọn T01–T07 tổng hợp.
- Chạy pipeline Python hiện có bằng offline regex hoặc LLM API thật.
- Bật/tắt audit cho LLM, hiển thị thời gian, số API call và token nếu provider trả.
- Lọc nhóm thông tin, xem trạng thái và các trường người/hạn/điều kiện.
- Chọn bản ghi để xem lịch sử sự kiện, câu nguồn và nguồn theo từng trường.
- Nhấn câu nguồn để chuyển sang transcript với phần liên quan được tô sáng.
- Đối chiếu mẫu nguyên bản với đáp án tham chiếu; transcript đã sửa không được chấm như mẫu cũ.
- Xem/tải JSON đầy đủ; cảnh báo kết quả cũ khi đầu vào thay đổi.
- Hiển thị lỗi API/schema; không tự thay LLM bằng kết quả offline khi thất bại.
- Layout desktop/mobile, trạng thái đang chạy, chống nhấn chạy trùng.

Giao diện gọi `/api/analyze`, backend gọi `pipeline.analyze`; không có thuật toán
trích xuất riêng trong JavaScript. Các đáp án mẫu không được đưa vào prompt.
`.env` được nạp tự động phía Python; môi trường có sẵn được ưu tiên. Khi đổi
file cấu hình, khởi động lại server. Khóa không được trả qua `/api/config`.

## Kiểm chứng thực tế

- 61/61 unit/contract tests đạt sau đợt kiểm thử Groq, gồm 10 test cho cấu hình
  và HTTP backend; đây là kiểm thử phần mềm, không phải 61 transcript LLM thật.
- 7/7 fixture viết tay đạt; không coi đây là chất lượng LLM.
- Edge headless: chọn mẫu, T03 offline, timeline, tô sáng nguồn, tab JSON,
  kết quả cũ sau sửa đầu vào, T02 offline, tải JSON, lỗi đầu vào trống và
  mobile 390px đều đạt. Không ghi nhận JavaScript exception trong luồng này.
- Đã xem ảnh render desktop 1600px và mobile 390px.
- Groq: sửa HTTP 403/code 1010 bằng User-Agent nhận diện ứng dụng, đã xác nhận
  endpoint models trả 200 và model cấu hình khả dụng.
- Lượt T03 đầu trả sai cặp kind/event_type (request/proposal), bị schema từ chối.
  Bổ sung ánh xạ bắt buộc trong prompt và thông báo trường sai.
- Sau sửa, một lượt T03 Groq thật qua trích xuất + audit trả `reopened`, khớp
  các kỳ vọng T03. Lưu tại `results/web_groq_T03.json` trên máy, thuộc thư mục
  được Git bỏ qua. Đây là bộ phát triển đã dùng sửa prompt, không phải tập độc lập.
- Audit của lượt đó đưa hai trích dẫn không khớp nguyên văn: verifier loại
  các finding này và trả cảnh báo. Không mô tả audit là đã kiểm chứng đúng ngữ nghĩa.

## Cách chạy

```powershell
python -m pip install -r requirements.txt
python -X utf8 web.py
```

Mở http://127.0.0.1:8765. Chọn Offline để xem T03 không cần API; chọn LLM API
để kiểm tra model với khóa riêng trong `.env`. Server chỉ bind loopback và
không phục vụ file ngoài các tài nguyên frontend đã định nghĩa.

Đây là server local phục vụ phát triển. Chưa deploy online, chưa làm xác thực
người dùng/lưu dữ liệu nhiều người, chưa hoàn tất bộ đánh giá LLM thật và video.

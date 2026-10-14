# Báo cáo bước 1 — ngày 12/10/2026

## Đã tạo và có thể chạy

1. Parser transcript, ID câu nguồn ổn định.
2. Schema sự kiện / bản ghi có cấu trúc (Pydantic).
3. Client HTTP cho API LLM Chat Completions, không đưa khóa trong mã.
4. LLM extractor (schema event) + Python temporal resolver + kiểm tra dẫn chứng cơ học.
5. Bộ **7 tình huống tiếng Việt tổng hợp** và JSON đáp án kỳ vọng; không lấy đáp án làm đầu vào dự đoán.
6. Scripts chạy thử / xuất kết quả, unit tests + kiểm thử hợp đồng bằng fake client.

## Kết quả đã thực sự đo

- **12/12 unit/contract tests PASS** trên Python/Pydantic của môi trường dựng.
- **Offline baseline T02, T03, T04: PASS 3/3** (không gọi LLM):
  - T02: đề xuất A, sau đó chốt B → cuối cùng B.
  - T03: từng chốt B, sau đó chưa chốt → reopened, có phản chứng.
  - T04: chốt B nhưng chưa được triển khai → meeting_status=agreed và execution_status=blocked.
- **Offline baseline trên cả T01–T07: PASS 3, FAIL 4**; đây là thiếu bao phủ được kỳ vọng của baseline giới hạn, không phải kết quả kiểm thử mô hình ngôn ngữ.
- **Chưa có kết quả gọi API LLM thật**, vì chưa có thông tin nhà cung cấp, khóa, hạn mức hoặc model được cấu hình trong môi trường làm việc.

## Chưa hoàn thành / không được tuyên bố đã đạt

- T01, T05, T06, T07 trên LLM thật và các tình huống tiếng Việt chưa từng thấy.
- Semantic reviewer độc lập có khả năng phát hiện sự kiện quan trọng bị LLM extractor bỏ sót.
- Benchmark công bằng và log lỗi thật của mô hình.
- UI/UX, link demo public, GitHub public, video YouTube.

## Thứ tự công việc tiếp theo

**Gate A:** Lấy cấu hình API của một model Chat Completions phù hợp → chạy T02/T03/T04 với `--engine llm_api` → sửa prompt, schema, issue grouping từ lỗi quan sát được. Không chia sẻ khóa API qua chat hoặc repo.

**Gate B:** Chạy T01/T05/T06/T07 để chứng minh đủ nhóm quyết định, công việc, vướng mắc, yêu cầu/phản hồi, nội dung chưa chốt và evidence; sửa logic theo các ca FAIL.

**Gate C:** Ghi kết quả thực nghiệm tối thiểu năm ca, bao gồm tình huống khó và một thất bại thực; UI hai cột và timeline chỉ triển khai sau khi đạt các ca lõi.

**Gate D:** Deploy online, quản lý secrets, test lại qua cửa sổ ẩn danh, README, GitHub và video dưới năm phút.

**Lưu ý quan trọng:** Dữ liệu gồm transcript mẫu bằng tiếng Việt được tạo riêng cho thử nghiệm, không phải dữ liệu thật từ AMI. AMI là bước bổ trợ tùy thời gian và điều kiện sử dụng.

# Trạng thái đóng gói demo

Theo lựa chọn của ứng viên: Local/Go Live trước, chuẩn bị gói deploy sau. Mã nguồn: [Vie-is-mee/Meeting-Intelligence](https://github.com/Vie-is-mee/Meeting-Intelligence). Website chưa deploy online và video chưa upload.

## Đã hoàn thành

- Giao diện có 3 chế độ: kết quả LLM đã lưu, LLM API phân tích mới, offline theo luật. Không có fallback giả từ API sang demo/offline.
- Demo mặc định mở D01, có đủ 8 case cùng phiên bản, cả đạt/chưa đạt. Review kỳ vọng/thực tế/bài học, evidence từng trường, lịch sử, transcript và JSON tải xuống.
- Xem lại không cần key/dependencies, không gọi API; thời gian/API usage lịch sử được tách khỏi lượt xem hiện tại. Transcript demo readonly để tránh gán kết quả cũ cho dữ liệu đã sửa.
- Backend chỉ serve thêm asset demo cho phép sẵn; không mở route .env hoặc source tùy ý. Chế độ recorded chỉ ở frontend, backend từ chối engine giả này.
- Có transcript .txt ở samples/demo để nhập vào chế độ API mới, run_demo.cmd và run_web.cmd, ZIP static/source theo allowlist và BUILD_INFO.
- Tài liệu: STATIC_DEMO, DEMO_RUNBOOK, MISSION2_SUBMISSION (ba câu bắt buộc, đối chiếu proposal gốc), FINAL_REGRESSION_RESULTS.

## Kiểm tra quan sát

- 108/108 unit/contract/HTTP tests đạt (105 test trước + 3 test demo). Ba test mới kiểm tra đầu ra demo trùng nguyên bản, asset có nhãn recorded và backend từ chối recorded làm engine live. Không phải 108 transcript LLM đúng.
- Node kiểm tra cú pháp JS đạt.
- Kiểm tra Edge headless thật bằng thư viện Node có sẵn: backend localhost và HTTP static, D01 thành công/H03 thất bại giữ nguyên JSON; disclosure/0 API hiện đúng; offline T03 chạy backend thật; không exception JS.
- Desktop 1440 px và mobile 390 px không tràn ngang; đã xem ảnh chụp giao diện. Trong browser smoke chỉ có một POST cho offline; không có request LLM.
- Hash của core và raw regression được giữ; demo analysis bằng đúng output trong lượt gốc. Không chỉnh prompt hoặc model trong giai đoạn này.

## Còn cần trước khi nộp

Ứng viên rà lại ba câu trả lời, quay video ≤5 phút, tạo GitHub public và điền link; nếu muốn online thì deploy ZIP static hoặc bố trí backend phù hợp. Repo cần build lại ZIP sau khi chỉnh file. Không gọi local URL là demo online hoặc nói walkthrough là phân tích mới.

UI hiện chỉ xem/tải kết quả, chưa sửa/xác nhận bản ghi có lưu lịch sử hoặc xuất CSV. Core còn lỗi đã ghi ở báo cáo 8 case; demo hoàn chỉnh để kiểm tra và trình bày không đồng nghĩa sản phẩm production-ready.

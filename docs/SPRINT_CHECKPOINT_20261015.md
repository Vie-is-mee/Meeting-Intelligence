# Chốt bản demo A — sáng 15/10/2026

Hoàn tất bước đầu của kế hoạch nước rút. Bản chính là nhánh `main`, lõi baseline A. Không chuyển code B/C vào demo và không đổi prompt, model, schema hoặc resolver trong bước này.

## Kết quả kiểm tra

| Hạng mục | Kết quả quan sát |
|---|---|
| Lõi local | Đủ 19 tệp baseline khớp hash theo `baseline_checkpoint.py --verify`. Đây là xác minh phiên bản, không phải lượt đánh giá LLM mới. |
| Vercel | Trang và config.js trả HTTP 200; cấu hình public trỏ đúng Render. |
| Render | Lần đầu health/config/samples timeout; kiểm tra lại đều HTTP 200. Cần dự phòng thời gian khởi động, chưa kết luận dịch vụ luôn sẵn sàng. |
| Kết nối hai website | CORS trả đúng origin Vercel; public config báo đã cấu hình API, model `openai/gpt-oss-120b`, provider `api.groq.com`. |
| Trình duyệt online | CSS hoạt động; D01 có hai quyết định, nguồn cuối L006; kết nối backend thành công; chọn được cả LLM API và offline. Không bấm chạy LLM. |
| Trình duyệt local | Bản backend và bản static đều xem được kết quả thật đã lưu, case thành công/thất bại, JSON, lịch sử và liên kết câu nguồn. |
| Rà soát và xuất | Kiểm tra trình duyệt local qua sửa/xác nhận, lưu/khôi phục và CSV/JSON thành công. |
| Mobile và khác origin | Không tràn ngang trên kích thước kiểm tra; checkbox và reduced motion hoạt động; GET + OPTIONS/POST offline qua hai cổng khác nhau thành công. |
| Chi phí kiểm tra | Không gọi Groq/LLM. Các POST trong kiểm tra local chỉ dùng baseline offline. Health/config và khả năng chọn chế độ không chứng minh một lượt phân tích LLM mới đã chạy được. |

Kiểm tra browser online hoàn tất lúc 09:16 ICT ngày 15/10/2026. Không có JavaScript runtime exception trong lượt kiểm tra. Không xác minh được commit backend đang chạy chỉ từ route health; đối chiếu hash áp dụng cho mã local, không tự nhận là đã kiểm tra hash trên Render.

## Đường chạy chính và dự phòng

1. **Chính:** https://meeting-intelligence-sable.vercel.app — mở sẵn trước khi quay. Nếu backend chưa kết nối, chờ rồi bấm “Kết nối lại backend”.
2. **Backend:** https://meeting-intelligence-5jk5.onrender.com/healthz — dùng kiểm tra dịch vụ, không dùng làm link giao diện chính.
3. **Dự phòng local có backend:** chạy `run_web.cmd`, mở http://127.0.0.1:8765. Dừng server cũ và chạy lại nếu cần chắc chắn nạp code A hiện tại; không tự kết thúc process của người dùng.
4. **Dự phòng không cần API/dependencies:** chạy `run_demo.cmd`, mở http://127.0.0.1:5501, hoặc Go Live tại `frontend/index.html`. Luôn ghi rõ đây là đầu ra LLM đã lưu.
5. **Bản ZIP:** `dist/meeting-intelligence-demo-static.zip` và `dist/meeting-intelligence-mission2-source.zip`; build bằng allowlist, loại `.env`, cache và thư mục tạm. Chạy lại `scripts/package_demo.py` sau khi sửa tài liệu cuối cùng.

## Việc còn lại trước khi nộp

- **Cản live demo khi khởi động chậm:** Render từng timeout trong lượt đầu; giữ demo đã lưu và local làm phương án dự phòng. Không chờ API trong phần lớn thời lượng video.
- **Chưa được kiểm tra trong bước này:** một lượt LLM mới trên backend online, quota Groq còn lại, khả năng lặp lại kết quả giữa nhiều lần sinh. Không suy ra các mục này từ `api_configured=true`.
- **Hồ sơ cần cập nhật:** README/nội dung form còn dòng “chưa deploy”, cần thay bằng link thật và trạng thái đúng. Đưa báo cáo hồi quy cùng phiên bản làm bảng chính, tránh để lịch sử thử nghiệm gây nhầm.
- **Lỗi mã hóa cần sửa:** một số nhận xét/báo cáo thử nghiệm B/C bị mất dấu do cách ghi file trước đó. Sửa phần trình bày, giữ nguyên artifact API và nhãn đã khóa; bản giải thích sửa lại phải được phân biệt với dữ liệu gốc.
- **Bài nộp:** chưa xác nhận video YouTube đã upload, quyền xem và việc gửi form. Đây vẫn là công việc bắt buộc trước 11:35, không xem việc có repo/demo là đã nộp xong.

## Bước tiếp theo

Kiểm tra và làm rõ kết luận cuối, bằng chứng từng trường và phân biệt cảnh báo AI với xác nhận của người dùng; chỉ sửa lỗi nhỏ cản demo. Không bắt đầu chuỗi B/C mới. Kết quả LLM của A vẫn là 8/8 hoàn tất, 5/8 đạt dữ liệu lõi và 4/8 đạt đầy đủ trên bộ hồi quy cũ; các kiểm tra vận hành sáng nay không làm thay đổi điểm đó.

Manifest phiên bản và kết quả smoke check: [submission_checkpoint_a_20261015.json](evaluation/submission_checkpoint_a_20261015.json).

# Bước 2 — kết luận, câu nguồn và xác nhận của người dùng

Lõi baseline A giữ nguyên; chỉ chỉnh phần trình bày frontend và kiểm tra một lượt phân tích mới trên Render. Kết quả hồi quy cũ vẫn là 8/8 hoàn tất, 5/8 đạt dữ liệu lõi, 4/8 đạt đầy đủ. Không cộng smoke test vào các tỷ lệ này.

## Đã làm rõ trên giao diện

- Thẻ ghi rõ **AI gốc**. Trạng thái trong cuộc họp không được gộp với trạng thái người dùng xác nhận.
- Mỗi thẻ có dòng **Người dùng**: chưa xác nhận, chưa đủ bằng chứng, đã loại bỏ hoặc đã xác nhận bản riêng. Bản AI vẫn giữ nguyên khi người dùng sửa; nội dung được xác nhận nằm ở Rà soát & xuất.
- Nhận xét audit được gọi là **AI đề nghị kiểm tra**, có thể cảnh báo sai; không trình bày như lỗi đã được xác minh.
- Bảng bằng chứng luôn hiện các trường liên quan: nội dung/trạng thái, điều kiện và triển khai của quyết định; người/hạn của công việc; hạn của yêu cầu. Không có nguồn riêng được ghi rõ, không tự mượn mọi câu của bản ghi để chứng minh từng trường.
- Giá trị chưa ghi nhận được tách khỏi giá trị mà lịch sử hệ thống có thao tác xóa. Điều kiện cũ sau mở lại vẫn nằm trong lịch sử, không được hiểu thành điều kiện hiện hành.
- Chỉ số “Hệ thống đánh dấu xem lại” đếm các mục hệ thống gắn cờ, không phải số người dùng chưa xác nhận. CSV vẫn chỉ có bản người dùng đã xác nhận.

## Kiểm thử

- Cú pháp JavaScript hợp lệ; 12/12 tests review/export và build Vercel đạt.
- Trình duyệt thật kiểm tra backend local và static: kết luận AI/người dùng tách biệt, giữ AI nguyên bản khi sửa/xác nhận, câu nguồn/lịch sử, failure đã lưu, xóa hạn và trường chưa ghi nhận, save/restore, CSV/JSON, mobile và CORS khác cổng đều đạt.
- Lượt browser đầu vướng asset cũ ở bản static; chạy lại với cache tắt đã qua đầy đủ. Sau cập nhật website, dùng Ctrl+F5 nếu còn thấy nội dung cũ.
- Baseline checkpoint vẫn khớp đủ 19 tệp. Kiểm tra browser không gọi LLM; POST ở các kiểm tra này chỉ dùng offline.

## Một lượt LLM online mới, giữ nguyên lần trả lời đầu

Thời điểm kết thúc: **09:24 ICT ngày 15/10/2026**. Request gọi Render thật, có Origin Vercel; HTTP 200, CORS đúng, hai API calls, model `openai/gpt-oss-120b`, 4.536 tokens nhà cung cấp báo, thời gian quan sát 3,51 giây. Đây không phải cam kết latency cho các lượt tiếp theo.

| Kỳ vọng đã ghi trước request | Kết quả thực tế | Đánh giá | Điều học được |
|---|---|---|---|
| Đề xuất A đổi sang chốt B cho trang đăng ký, nguồn L003; Hà nhận kiểm tra trên điện thoại, hạn nguyên văn “10 giờ sáng mai”, nguồn L004; không tự đặt ngày tuyệt đối | Hai bản ghi bắt buộc đúng; decision agreed B, action assigned/Hà/hạn đúng, due_iso null; audit không finding | Đạt smoke test này | Đường phân tích online chạy được và giữ kết luận thay đổi trong lượt này. Cần đọc nguồn; audit rỗng không chứng minh luôn đúng, một case không chứng minh độ đúng toàn bộ dataset. |

Đầu vào và kỳ vọng được khóa trước khi gọi; chỉ transcript/engine/audit được gửi backend, không gửi nhãn. Review do cùng trợ lý thực hiện, chưa có đánh giá độc lập. Không thay kết quả lỗi bằng lần gọi khác, không dùng bản người dùng sửa để tính điểm model.

- [Input + kỳ vọng](evaluation/submission_live_smoke_20261015_input.json).
- [HTTP response và đầu ra nguyên bản](evaluation/submission_live_smoke_20261015_output.json).
- [Review](evaluation/submission_live_smoke_20261015_review.json).

## Phần tiếp theo trước khi nộp

Chốt bảng tối thiểu năm case cùng phiên bản từ hồi quy A; cập nhật README và nội dung form với link online thật; sửa lỗi mất dấu trong phần tài liệu trình bày; hoàn tất video dưới năm phút. Giữ nguyên nhãn và artifact kiểm thử đã khóa. Không mở thử nghiệm model/core mới trong giai đoạn này.

# Nội dung chuẩn bị nộp Mission 2

Bản nội dung để ứng viên rà lại trước khi nộp. Đã đối chiếu proposal Mission 1 “Trí tuệ cuộc họp”, trang 1–5. Không xem những mục còn thiếu dưới đây là đã hoàn tất.

## Ba câu hỏi bắt buộc

### 1. Phần quan trọng nhất chọn hiện thực hóa và vì sao hướng này khả thi?

Tôi chọn chứng minh khả năng nối diễn biến cuộc họp để giữ đúng thông tin còn hiệu lực, đặc biệt quyết định và phân công, thay vì chỉ tóm tắt những câu từng xuất hiện. LLM trích sự kiện có mã câu nguồn; Python ghép theo vấn đề và thứ tự, cập nhật trạng thái/điều kiện/người/hạn; verifier kiểm tra nguồn và một số rủi ro; lượt LLM thứ hai rà soát kết quả. Giao diện cho xem bản ghi, lịch sử và nguồn từng trường.

Trong lượt hồi quy cố định, D01 chuyển từ đề xuất lưu trên máy chủ sang chốt object storage, đồng thời giữ nhà cung cấp chưa chọn. D03 phân biệt chốt trong phạm vi thiết kế với chưa được triển khai; D04 giữ điều kiện mới; H01 mở lại lựa chọn nhưng không hủy việc độc lập. Các kết quả này chứng minh pipeline có thể tạo dữ liệu dùng để con người rà soát. Chúng chưa chứng minh vượt trội so với tóm tắt trực tiếp hoặc đủ tin cậy để tự động tạo việc. Lượt này có 8/8 hoàn tất pipeline/audit, 4/8 đạt đầy đủ; còn lỗi thật được công bố.

### 2. Thay đổi so với Mission 1 và điều gì khiến thay đổi?

Proposal đã chọn transcript, Python gọi API, lịch sử theo vấn đề, dẫn chứng và quyền rà soát của con người. Tôi giữ hướng đó, nhưng thu hẹp phạm vi để kiểm chứng được trong MVP:

- Chưa dùng AMI như kế hoạch trang 3/5; thay bằng bộ transcript tiếng Việt tổng hợp, có nhãn và tình huống đổi ý/đổi người/đổi hạn. Bộ này giúp tái hiện lỗi rõ ràng nhưng ít đại diện họp thật; nhãn/review do cùng trợ lý tạo, chưa được người thứ hai xác nhận.
- Cụ thể hóa “nối diễn biến” thành events và resolver xác định, thêm clear_fields để phân biệt “không cập nhật” với “xóa giá trị cũ”, và nguồn riêng cho từng trường. Lỗi giữ hạn cũ khi vừa hủy vừa bỏ hạn đã buộc tôi sửa resolver.
- Cụ thể hóa kiểm chứng bằng lượt audit LLM thứ hai. Thực nghiệm cho thấy audit cũng cảnh báo sai, nên finding chỉ là giả thuyết cần rà soát, không được tự thay kết luận bằng một kết luận khác.
- Chưa hoàn thành so sánh A/B/C và đo công sức sửa như kế hoạch trang 5; không tuyên bố cơ chế C đã tốt hơn B. Các case reserved đã được dùng để sửa không còn là đánh giá độc lập.
- Ban đầu thu hẹp UI thành xem nguồn/lịch sử/cảnh báo. Sau khi chốt hồi quy, tôi bổ sung bản người dùng sửa/xác nhận/từ chối, lưu lịch sử cục bộ và xuất JSON/CSV chỉ bản đã xác nhận, giữ gốc AI riêng. Chưa tách/gộp chủ đề, thêm bản ghi bị bỏ sót, lưu nhiều người trên server, phê duyệt tổ chức hoặc đồng bộ công việc.
- Quota TPD thực tế khiến nhiều lượt bị chặn. Tôi bổ sung dừng ở 429, lưu lỗi và chế độ demo kết quả đã ghi để giám khảo kiểm tra được dù không đủ quota. Chế độ này luôn ghi rõ không phải phân tích mới.

### 3. Loại thông tin dễ sai nhất và cách tránh tạo dữ liệu không tồn tại?

Các lỗi dễ gặp nhất hiện nay là phân biệt câu giao việc với request/đề xuất, giữ đúng vòng đời khi hủy, và bỏ sót yêu cầu hoặc kết luận cuối. LC01 tạo request thừa dù công việc đã hủy; H03 có lượt bỏ cả request và hạn tương đối; LC02 có lượt bỏ lệnh xóa hạn, lượt khác xóa hạn đúng nhưng thiếu lựa chọn thay thế và tạo proposal phụ. Audit còn nhầm owner lịch sử hoặc lý do hủy với dữ liệu hiện hành.

Biện pháp hiện có: schema và kiểm tra cặp kind/event_type; từ chối mã câu không tồn tại và phản hồi bị cắt; không tự điền người/ngày/quyền duyệt; cập nhật trạng thái theo lịch sử; nguồn riêng từng trường; clear_fields; audit dẫn quote thật; guard đánh dấu request trùng việc đã hủy. Khi audit lỗi, các bản ghi rủi ro được giữ để kiểm tra. Trích dẫn đúng vẫn không bảo đảm diễn giải đúng; guard/audit không tự sửa mọi lỗi và có thể bỏ sót. Vì vậy bản ghi chỉ là đầu ra cần rà soát, chưa được tự đồng bộ thành công việc/cam kết.

## Đoạn trình bày bài làm để dán vào form

MVP nhận transcript tiếng Việt, trích sự kiện, nối diễn biến và hiển thị bản ghi có trạng thái cuối, lịch sử và evidence theo từng trường. Chạy local bằng run_web.cmd hoặc python -X utf8 web.py, mở http://127.0.0.1:8765. Có demo 8 đầu ra LLM đã lưu xem được bằng Go Live, không cần key; phân tích mới cần cấu hình .env phía Python. Người dùng sửa/xác nhận/từ chối tại mục 05, lưu lịch sử trên máy và xuất JSON/CSV; gốc AI luôn giữ riêng. Hồi quy cùng phiên bản hoàn tất 8/8 case, 4/8 đạt đầy đủ và 5/8 đúng dữ liệu lõi trước khi người dùng sửa. D01 chứng minh thay đổi lựa chọn và giữ đúng kết luận cuối. Hạn chế: có bản ghi thừa/thiếu, audit sai, quota API; dataset tổng hợp và chưa có gán nhãn độc lập. Không tự tạo việc hoặc tuyên bố mọi kết quả đều đúng. Báo cáo và đầu ra nguyên bản nằm trong docs/evaluation.

## Các đường dẫn phải điền trước khi nộp

- GitHub public: https://github.com/Vie-is-mee/Meeting-Intelligence
- Demo online: chưa deploy; hiện có local demo và ZIP static sẵn để deploy sau theo lựa chọn của ứng viên. Nếu nộp local, ghi rõ backend chưa triển khai hosting và hướng dẫn chạy; không ghi local URL là link online.
- YouTube: chưa quay/upload. Kịch bản ≤5 phút ở DEMO_RUNBOOK.md.

Chỉ điền link thật sau khi tạo và kiểm tra truy cập. README, bộ test ≥5 case cùng phiên bản và nội dung ba câu trả lời đã chuẩn bị; ứng viên cần rà lại cách diễn đạt và xác nhận trước khi nộp.

# Đọc và sử dụng kết quả cuộc họp

## 1. Phân tích — cuộc họp để lại những gì?

Phía trái là transcript và chế độ xử lý. Phía phải là tổng quan và các nhóm kết quả AI gốc:

- **Quyết định đã thống nhất:** đọc cả điều kiện và giới hạn triển khai, không chỉ tên phương án.
- **Công việc cần theo dõi:** người nhận, hạn và điều kiện; chưa có thông tin thì hiển thị chưa ghi nhận.
- **Chưa chốt · cần làm rõ:** đề xuất, lựa chọn mở lại và kết luận chưa chắc chắn.
- **Yêu cầu & phản hồi:** chưa mặc nhiên là công việc được giao.
- **Vướng mắc & tri thức:** vấn đề cần theo dõi hoặc thông tin được chia sẻ; không tự coi là đã kiểm chứng.
- **Đã hủy · đã rút:** giữ lịch sử, không trình bày như cam kết đang có hiệu lực.

Chỉ nhóm có dữ liệu mới xuất hiện. Ba ô tổng quan được tính từ bản AI gốc; các mục đã hủy không được cộng vào số việc đang giao. Dòng người dùng cho biết số mục chờ/xác nhận để xuất CSV. Chọn một thẻ rồi mở Kiểm chứng.

## 2. Kiểm chứng — căn cứ ở đâu?

Bên trái là bản ghi và transcript nguyên văn có mã câu. Bên phải có ba tab:

1. **Kết luận & nguồn:** so từng giá trị AI ghi nhận với câu nguồn riêng cho trường đó.
2. **Diễn biến xử lý:** theo dõi đề xuất, thay đổi và chốt; các quy tắc là cách phần mềm xử lý sự kiện, không phải suy nghĩ nội bộ của model.
3. **Nhận xét audit:** AI đề nghị kiểm tra, có thể cảnh báo sai hoặc bỏ sót.

Nhấp mã câu để tìm đúng phát biểu trong transcript. Trên điện thoại, mỗi dòng bảng được trình bày như một khối có nhãn. Không có nguồn hoặc không có nhận xét audit đều không chứng minh bản ghi đúng.

## 3. Rà soát & xuất — dữ liệu nào được sử dụng?

Đầu màn hình có số mục chờ xác nhận, đã xác nhận và đã loại bỏ. Chọn bản ghi, đọc nội dung cạnh câu nguồn, sau đó chọn Đúng / Sai / Chưa đủ bằng chứng.

- Đúng: xác nhận sau khi đối chiếu, không phải nhập lại nội dung.
- Sai: sửa với lý do và nguồn, hoặc loại bỏ bản ghi bị trích thừa.
- Chưa đủ bằng chứng: giữ trạng thái chờ, chưa đưa vào CSV.

CSV chỉ chứa bản người dùng đã xác nhận. JSON giữ AI gốc, bản người dùng và lịch sử. Người từng phụ trách một việc đã hủy là thông tin lịch sử; xác nhận nội dung không phải khôi phục công việc hoặc phê duyệt của tổ chức.

## Phạm vi bản giao diện này

Chỉ đổi cách nhóm và trình bày; không đổi transcript, nhãn, đầu ra AI gốc, lõi A hoặc điểm kiểm thử. Thẻ có thể được sắp theo nhóm thay vì thứ tự JSON; khi chọn thẻ, danh tính bản ghi, câu nguồn và bản rà soát vẫn khớp đúng chỉ mục gốc.

Đã kiểm tra desktop/mobile, bố cục nguồn, nhóm D01, đổi thứ tự H01, giữ AI nguyên bản khi sửa/xác nhận, lưu/khôi phục, CSV/JSON và CORS khác cổng. Các kiểm tra trình duyệt không gọi LLM. Kiểm tra review/build có 12 tests đạt; baseline core vẫn khớp 19 tệp.

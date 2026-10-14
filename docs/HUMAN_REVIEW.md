# Rà soát của con người và xuất dữ liệu

Mục 05 trên giao diện khép thêm vòng sử dụng: AI đề xuất → người dùng đọc nguồn → sửa/xác nhận/từ chối → xuất dữ liệu đã rà soát. Nó hoạt động cả trên Go Live và backend, không gọi LLM thêm.

## Cách dùng

1. Mở kết quả, chọn bản ghi; xem câu nguồn/lịch sử ở mục 03/04.
2. Xuống mục 05, nhập tên người rà soát (tự khai). Có thể sửa loại, nội dung, trạng thái, người/hạn/điều kiện và mã câu nguồn.
3. Nếu sửa, ghi lý do. “Lưu chỉnh sửa, chưa xác nhận” giữ bản ở trạng thái chờ; nhấn xác nhận sau khi đánh dấu đã đối chiếu nguồn để đưa vào danh sách xuất.
4. Với request thừa như LC01, ghi lý do và “Từ chối bản ghi”. Bản gốc vẫn hiện, lịch sử lưu lý do, nhưng không vào CSV.
5. Bản đã xác nhận bị sửa sẽ trở về chờ; “Mở lại rà soát” cũng loại nó khỏi danh sách xác nhận cho đến lần xác nhận mới.
6. Xuất JSON kèm gốc AI/lịch sử để giữ bằng chứng; CSV chỉ chứa bản đã xác nhận, vẫn ghi rõ cancelled/open/conditional nếu trạng thái là như vậy, không tự biến thành việc đang giao.

“Lưu phiên trên trình duyệt này” giữ một phiên gần nhất (gồm gốc AI và lịch sử). Nút ở đầu trang mở lại phiên đó sau reload. Lưu phiên mới thay phiên đã lưu trước; xuất JSON để giữ các phiên khác. Thay đổi chưa nhấn lưu chỉnh sửa/xác nhận không được ghi lại khi chuyển bản ghi; UI nhắc lưu trước khi chuyển. Không có đồng bộ cloud hoặc nhiều người cùng duyệt.

## Các lớp dữ liệu

- **AI gốc:** result.analysis, bảng nguồn và metric/regression của model giữ nguyên.
- **Bản người dùng:** draft và nguồn người dùng chọn. Giá trị sửa không được tự hợp thức hóa bằng provenance cũ của AI.
- **Lịch sử:** người thao tác, thời gian ISO UTC, lý do và before/after (hoặc thay đổi quyết định rà soát).
- **Danh sách sử dụng:** chỉ confirmed; rejected/pending không vào CSV nhưng vẫn nằm trong JSON/lịch sử.

Xác nhận chỉ là nội dung do người dùng rà soát, không phải phê duyệt theo thẩm quyền tổ chức. Tên người duyệt là tự khai, chưa có xác thực tài khoản. Export luôn giữ authority_status=unknown. Xác nhận tri thức chưa tự chứng minh tri thức đó đúng ngoài thực tế.

## Kiểm tra đã thực hiện

- 108 Python unit/contract/HTTP tests đạt, gồm route review.js/review.css.
- 8 Node tests: giữ gốc, từ chối/chờ không xuất, sửa sau xác nhận, chặn thiếu nguồn/tên/lý do, cặp kind/status, mở lại, CSV Unicode/quote và chống công thức, restore đúng phiên/gốc.
- Edge thật: xác nhận D01, sửa rồi mất xác nhận, xác nhận lại; lưu/reload/restore 3 bước lịch sử; không trộn rà soát sang H03; từ chối request LC01 và xác nhận action; tải CSV chỉ action, JSON giữ cả hai record gốc và lịch sử; desktop/mobile không tràn ngang.
- Chỉ một POST cho offline smoke test, không có request LLM. Đây là kiểm thử phần mềm/UX, không làm tăng accuracy model hoặc thay lượt hồi quy 4/8.

## Giới hạn

Chưa thêm bản ghi hoàn toàn mới cho thông tin AI bỏ sót; chưa tách/gộp vấn đề; nguồn được kiểm tra tồn tại nhưng vẫn cần người đọc để xác nhận nội dung. Chưa có máy chủ lưu/audit nhiều người, chữ ký hay phê duyệt tổ chức. JSON chứa đầy đủ transcript gốc và lịch sử nên người dùng tự chọn nơi chia sẻ. Không tự ghi sang công cụ quản lý công việc.

```powershell
python -m unittest discover -s tests -q
node --test tests/review.test.cjs
```

Node chỉ cần để chạy tests này, không cần để xem demo.

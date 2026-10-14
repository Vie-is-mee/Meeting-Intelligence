# Rà soát nhãn bộ prospective v2

Theo yêu cầu ứng viên, trợ lý tự đọc và gán nhãn trước đầu ra model. **Không có human signoff, không độc lập, chưa chạy API và chưa có điểm model.** Transcript giữ nguyên hash. Quote lấy nguyên văn từ parser; việc quote tồn tại không tự chứng minh mọi diễn giải là đúng.

Tổng 27 nhãn cốt lõi; 9 extras tham chiếu; 4 cách biểu diễn thay thế. Nhãn theo loại: `{'decision': 9, 'action': 4, 'feedback': 5, 'request': 7, 'issue': 1, 'knowledge': 1}`. Các alternative là lựa chọn biểu diễn trước matching, không cộng đôi recall.

## N01 — Lựa chọn đơn vị giao hàng

| Loại | Nhãn cốt lõi | Trạng thái | Người / hạn / điều kiện | Nguồn trạng thái cuối |
|---|---|---|---|---|
| decision | Dùng đơn vị Mây cho đợt bán thử miền Nam | agreed | Không tự điền | L005 |

**Lý do/ranh giới:** Miền Bắc nằm ngoài phạm vi chọn hôm nay: chấp nhận open riêng nhưng không bắt buộc model phải tạo record ngoài phạm vi. Không chấm proposal Sao thành quyết định còn hiệu lực.

**Extras có thể chấp nhận:** Chưa chọn đơn vị giao hàng miền Bắc, để cuộc họp khác.

**Không được kết luận như thông tin hiện hành:** Sao là đơn vị đang được chọn; Mây đã được chọn cho mọi miền/mọi đợt; Có một người đã nhận liên hệ đơn vị giao hàng. Có thể nhắc thông tin cũ dưới dạng lịch sử nếu đánh dấu rõ không còn hiệu lực.

## N02 — Thay người và hạn tài liệu hướng dẫn

| Loại | Nhãn cốt lõi | Trạng thái | Người / hạn / điều kiện | Nguồn trạng thái cuối |
|---|---|---|---|---|
| action | Làm bản hướng dẫn kích hoạt tài khoản | assigned | owner: Uyên; due_raw: chiều thứ Sáu | L005, L006 |

**Lý do/ranh giới:** Một vòng đời công việc, không phải hai công việc độc lập. L004 thay người và hạn; L005 xác nhận nhận việc; L006 nói chưa giao supporter.

**Không được kết luận như thông tin hiện hành:** Phương vẫn là người phụ trách hoặc người hỗ trợ; Hạn hiện hành là sáng thứ Tư; Hai action đang giao cùng việc cho Phương và Uyên. Có thể nhắc thông tin cũ dưới dạng lịch sử nếu đánh dấu rõ không còn hiệu lực.

## N03 — Phản hồi người dùng về đăng ký

| Loại | Nhãn cốt lõi | Trạng thái | Người / hạn / điều kiện | Nguồn trạng thái cuối |
|---|---|---|---|---|
| feedback | Khách dùng thử phản hồi trang đăng ký có quá nhiều ô nhập | recorded | Không tự điền | L001 |
| request | Bước đăng ký đầu chỉ bắt buộc số điện thoại và mã xác nhận | recorded | Không tự điền | L004 |
| feedback | Khách khen hướng dẫn bằng hình dễ hiểu | recorded | Không tự điền | L003 |

**Lý do/ranh giới:** Chưa chốt thiết kế là thông tin có nguồn, chấp nhận open riêng. Câu hỏi email chưa phải yêu cầu bỏ số điện thoại. Không tạo task chỉ từ request.

**Extras có thể chấp nhận:** Chưa chốt thiết kế đăng ký thay thế.

**Biểu diễn tương đương:** Một feedback gộp được chấp nhận nếu giữ đủ ý tiêu cực và tích cực; request giảm trường vẫn riêng.

**Không được kết luận như thông tin hiện hành:** Khách yêu cầu thêm hình; Đã chốt thiết kế thay thế hoặc giao người triển khai; Khách yêu cầu bỏ đăng ký bằng số điện thoại để dùng email. Có thể nhắc thông tin cũ dưới dạng lịch sử nếu đánh dấu rõ không còn hiệu lực.

## N04 — Hủy một cách triển khai nhưng giữ nhu cầu

| Loại | Nhãn cốt lõi | Trạng thái | Người / hạn / điều kiện | Nguồn trạng thái cuối |
|---|---|---|---|---|
| request | Bộ phận vận hành cần tải danh sách đơn dưới dạng XLSX; nhu cầu vẫn giữ | recorded | Không tự điền | L005 |
| action | Thử xuất danh sách đơn bằng công cụ K (đã hủy) | cancelled | owner: Trúc | L004, L006 |
| decision | Chưa chọn cách xuất XLSX thay thế | open | Không tự điền | L005 |

**Lý do/ranh giới:** Giữ ba vai trò: nhu cầu, công việc triển khai đã hủy, lựa chọn thay thế chưa chốt. Owner lịch sử không tự bị xóa; không ghép hạn của task vào request XLSX.

**Không được kết luận như thông tin hiện hành:** Nhu cầu XLSX đã bị rút; Trúc đang tiếp tục thử K hoặc đang làm cách mới; Hạn trưa mai vẫn hiện hành; Không phù hợp chính sách dữ liệu là condition hiện hành để thử K; Sinh request thử K độc lập còn hiệu lực từ câu giao việc đã hủy. Có thể nhắc thông tin cũ dưới dạng lịch sử nếu đánh dấu rõ không còn hiệu lực.

## N05 — Báo khắc phục vướng mắc nhưng chưa xác minh

| Loại | Nhãn cốt lõi | Trạng thái | Người / hạn / điều kiện | Nguồn trạng thái cuối |
|---|---|---|---|---|
| issue | Lỗi máy quét quầy số hai được Oanh báo hết trong lượt thử, chưa được kiểm tra độc lập hoặc xác nhận không tái phát | reported_resolved | Không tự điền | L004, L005 |

**Lý do/ranh giới:** reported_resolved là lời báo kết quả giới hạn, không là verified. Việc Oanh đã làm trước câu nói không tự trở thành action assigned sau họp. Cần thể hiện rõ giới hạn kiểm chứng; không chỉ ghi "đã xử lý xong".

**Extras có thể chấp nhận:** Oanh báo ba lượt thử gửi được sau thay dây mạng; chưa xác minh cả ca.

**Không được kết luận như thông tin hiện hành:** Lỗi đã được xác minh độc lập hết hoàn toàn hoặc không tái phát; Đã giao Oanh/Nam làm nhiệm vụ kiểm tra sau họp. Có thể nhắc thông tin cũ dưới dạng lịch sử nếu đánh dấu rõ không còn hiệu lực.

## N06 — Thay điều kiện trước khi mở chương trình

| Loại | Nhãn cốt lõi | Trạng thái | Người / hạn / điều kiện | Nguồn trạng thái cuối |
|---|---|---|---|---|
| decision | Mở chương trình ưu đãi khi đủ 100 cửa hàng tham gia VÀ kiểm thử thanh toán không có lỗi nghiêm trọng | conditional | condition: đủ 100 cửa hàng tham gia và kiểm thử thanh toán không có lỗi nghiêm trọng | L003, L005 |

**Lý do/ranh giới:** Điều kiện chưa đạt không biến conditional thành reopened. Ngưỡng 100 và kiểm thử không lỗi là quan hệ AND. Có thể biểu diễn chặn mở ngay bằng blocked nếu nói rõ cùng trạng thái chờ; phương án dưới đây được chốt trước đầu ra.

**Biểu diễn tương đương:** Chấp nhận blocked thay pending_condition chỉ khi giữ đầy đủ điều kiện và không đổi meeting_status conditional.

**Không được kết luận như thông tin hiện hành:** Mốc hiện hành là 80 cửa hàng; Chỉ cần một trong hai điều kiện; Các điều kiện đã đạt hoặc được phép mở ngay; Quyết định có điều kiện đã bị hủy/mở lại; Có ngày mở đã chốt. Có thể nhắc thông tin cũ dưới dạng lịch sử nếu đánh dấu rõ không còn hiệu lực.

## N07 — Ngắt lời và đại từ chưa rõ người nhận

| Loại | Nhãn cốt lõi | Trạng thái | Người / hạn / điều kiện | Nguồn trạng thái cuối |
|---|---|---|---|---|
| request | Kiểm tra đường thoát khu sự kiện trước lượt diễn tập tiếp theo; chưa xác định người nhận | recorded | due_raw: trước lượt diễn tập tiếp theo | L006 |
| decision | Chưa chọn ngày diễn tập; thứ Hai/thứ Ba mới là gợi ý | open | Không tự điền | L006 |

**Lý do/ranh giới:** Request có thời điểm tương đối dù chưa có owner/action. Đại từ trong câu hỏi L002 không chứng minh nhận việc. L007 là nhu cầu bổ trợ có thể tách, không tự gán Mai làm.

**Extras có thể chấp nhận:** Cần hỏi thêm lịch ban tổ chức trước khi bàn người và ngày.

**Không được kết luận như thông tin hiện hành:** Đã giao Khánh/Mai hoặc một người cụ thể kiểm tra; Đã chốt diễn tập thứ Hai hoặc thứ Ba; Yêu cầu kiểm tra không có ràng buộc thời gian vì chưa biết ngày lịch. Có thể nhắc thông tin cũ dưới dạng lịch sử nếu đánh dấu rõ không còn hiệu lực.

## N08 — Đọc quyết định cũ và tách cuộc họp hiện tại

| Loại | Nhãn cốt lõi | Trạng thái | Người / hạn / điều kiện | Nguồn trạng thái cuối |
|---|---|---|---|---|
| decision | Lựa chọn địa điểm hội thảo đã mở lại; hôm nay chưa chọn phòng A hay B | reopened | Không tự điền | L003, L006 |
| request | Có phương án phòng phù hợp trước lần xác nhận vé tiếp theo | recorded | due_raw: trước lần xác nhận vé tiếp theo | L005 |

**Lý do/ranh giới:** Có thể giữ content phòng A như nội dung lịch sử của reopened nếu ghi rõ không còn kết luận cuối. L006 nhắc câu cũ không là agreement mới.

**Extras có thể chấp nhận:** Phòng A đang sửa điện, ảnh hưởng lựa chọn địa điểm.

**Không được kết luận như thông tin hiện hành:** Phòng A đã được chốt lại hôm nay; Phòng B đã được chọn; Thu/Dũng đã nhận tìm phòng hoặc có ngày xác nhận vé cụ thể. Có thể nhắc thông tin cũ dưới dạng lịch sử nếu đánh dấu rõ không còn hiệu lực.

## N09 — Trao đổi trước giờ họp không tạo cam kết

| Loại | Nhãn cốt lõi | Trạng thái | Người / hạn / điều kiện | Nguồn trạng thái cuối |
|---|---|---|---|---|
| Không có | Không có bản ghi nghiệp vụ bắt buộc | — | — | L001–L005 |

**Lý do/ranh giới:** Negative control: chỉ thử thiết bị trước họp, không có nội dung nghiệp vụ/cam kết dùng sau họp. required_records=[] có chủ ý; không cần suy diễn thiếu transcript hoặc bịa cảnh báo hỏng dữ liệu.

**Không được kết luận như thông tin hiện hành:** Tạo quyết định kinh doanh hoặc công việc sau họp từ thử mic/camera; Hà/Bình nhận một nhiệm vụ sau cuộc họp; Coi kết quả thử âm thanh là tri thức nghiệp vụ cần dùng tiếp. Có thể nhắc thông tin cũ dưới dạng lịch sử nếu đánh dấu rõ không còn hiệu lực.

## N10 — Tri thức chưa chắc chắn và yêu cầu xác minh

| Loại | Nhãn cốt lõi | Trạng thái | Người / hạn / điều kiện | Nguồn trạng thái cuối |
|---|---|---|---|---|
| knowledge | Có lời nhớ 45 ngày và tài liệu cũ ghi 30 ngày; thời gian lưu dấu vết hiện tại chưa được xác minh | unverified | Không tự điền | L001, L002, L005 |
| request | Đối chiếu tài liệu cấu hình mới trước khi trả lời khách | recorded | due_raw: trước khi trả lời khách | L003 |

**Lý do/ranh giới:** Tri thức là phát biểu có mức tin cậy, không là sự thật bên ngoài đã xác minh. L004 chưa chốt hạn lịch không xóa thứ tự "trước khi trả lời khách" ở L003.

**Biểu diễn tương đương:** Hai knowledge đều phải giữ nguồn và độ chưa chắc chắn. Không chấm hai con số thành hai facts verified.

**Không được kết luận như thông tin hiện hành:** Cấu hình hiện tại chắc chắn là 30 hoặc 45 ngày; Cuộc họp quyết định đổi thời gian lưu; Nga/Vũ đã nhận việc đối chiếu; Không có ràng buộc trước khi trả lời khách chỉ vì không có ngày lịch. Có thể nhắc thông tin cũ dưới dạng lịch sử nếu đánh dấu rõ không còn hiệu lực.

## N11 — Nhiều chủ đề: kiểm kê, tài liệu và phản hồi

| Loại | Nhãn cốt lõi | Trạng thái | Người / hạn / điều kiện | Nguồn trạng thái cuối |
|---|---|---|---|---|
| decision | Kiểm kê khu lạnh chiều thứ Sáu, thay lịch sáng thứ Năm | agreed | Không tự điền | L064, L072 |
| action | Sửa sơ đồ khu lạnh trong tài liệu; Linh phụ trách, gửi sáng thứ Sáu | assigned | owner: Linh; due_raw: sáng thứ Sáu | L059, L060, L072 |
| feedback | Ca tối dùng máy bàn phản hồi màn hình hàng về khó tìm nút xác nhận; chưa xử lý | recorded | Không tự điền | L043, L067 |
| feedback | Chữ ở màn hình xác nhận nhỏ trên màn hình cũ; không quy kết mọi máy đều như vậy | recorded | Không tự điền | L067 |

**Lý do/ranh giới:** Lịch kiểm kê chiều thứ Sáu nằm trong nội dung decision, không gán thành due của tài liệu. Tài liệu gửi sáng thứ Sáu theo L066. Hai feedback có phạm vi, không tự đổi thành task. Khu thường ngoài phạm vi nên open có nguồn là extra hợp lệ.

**Extras có thể chấp nhận:** Chưa chọn lịch kiểm kê khu thường, ngoài phạm vi chốt khu lạnh; Mã kệ phía đông trên sơ đồ hiện tại bị chú thích che; chưa có lời báo đã sửa; Người dùng muốn nhìn thấy nút xác nhận rõ hơn, chưa đề nghị vị trí cụ thể.

**Biểu diễn tương đương:** Feedback gộp được chấp nhận nếu giữ cả hai ý và phạm vi thiết bị; không mất một ý rồi vẫn tính đủ recall.

**Không được kết luận như thông tin hiện hành:** Kiểm kê khu lạnh sáng thứ Năm còn là lịch cuối; Bình còn phụ trách sơ đồ hoặc được gán supporter; Hạn sơ đồ là chiều thứ Tư hoặc chiều thứ Sáu; Linh/Vy/Bình đã được giao sửa giao diện hay lịch xe; Đã chốt kiểm kê toàn kho/đổi cảm biến/dịch tài liệu. Có thể nhắc thông tin cũ dưới dạng lịch sử nếu đánh dấu rõ không còn hiệu lực.

## N12 — Lịch cũ, hủy triển khai và mở lại ở cuối

| Loại | Nhãn cốt lõi | Trạng thái | Người / hạn / điều kiện | Nguồn trạng thái cuối |
|---|---|---|---|---|
| request | Khách cần hướng dẫn tiếng Anh cho cả tuyến Bắc và Nam; nhu cầu còn giữ | recorded | Không tự điền | L046, L069, L072 |
| action | Thử làm hướng dẫn bằng công cụ M (đã hủy) | cancelled | owner: Hòa | L044, L045, L073 |
| decision | Chưa chọn công cụ/cách làm hướng dẫn thay thế và chưa giao người làm | open | Không tự điền | L048, L074, L075 |
| decision | Lựa chọn giờ tuyến Bắc được mở lại; không còn chốt 8 giờ hay 7 giờ, ngày chạy thử chưa chắc chắn | reopened | Không tự điền | L067, L068, L071, L078 |
| decision | Chưa chốt giờ khởi hành tuyến Nam | open | Không tự điền | L059, L071 |
| feedback | Tuyến Nam có phản hồi xe đến điểm đón trễ, chưa có lời báo hết trễ | recorded | Không tự điền | L065, L076 |
| request | Cần xác nhận giờ tuyến Nam với nhà xe; chưa có người nhận liên hệ | recorded | Không tự điền | L059 |

**Lý do/ranh giới:** Giữ riêng vòng đời hai tuyến, request tài liệu và task M. Giờ 8 chỉ từng agreed trong ngày thử rồi bị reopened ở L067; các giờ được nhắc lại là history. Hòa là owner lịch sử của task cancelled, hạn null. Request xác nhận giờ Nam khác với một action liên hệ được nhận. Extra issue Nam có căn cứ nhưng không tự chứng minh feedback đã được trích đủ.

**Extras có thể chấp nhận:** Vướng mắc xe tuyến Nam trễ chưa được báo khắc phục.

**Không được kết luận như thông tin hiện hành:** Giờ tuyến Bắc hiện đã chốt 7 hoặc 8 giờ; Lấy 8 giờ của Bắc làm giờ Nam; Hòa còn đang thử M/làm hướng dẫn mới hoặc còn hạn tối mai; Yêu cầu tiếng Anh bị hủy khi công cụ M hoặc lịch Bắc bị mở lại; Lý do công cụ không cho dùng thương mại thành condition tiếp tục triển khai M; Đã chọn công cụ thay thế hoặc giao người làm/liên hệ nhà xe; Xe tuyến Nam được báo khắc phục hoặc xác minh hết trễ. Có thể nhắc thông tin cũ dưới dạng lịch sử nếu đánh dấu rõ không còn hiệu lực.

## Quy tắc chấm

Gold là tập cốt lõi, không giả là danh sách vét cạn mọi thông tin. Xét thêm từng output theo nghĩa/nguồn/độ trùng lặp, không tự gọi output ngoài danh sách extras là bịa. Chọn đúng một representation cho mỗi case rồi matching một-một. Không dùng kết quả model để sửa nhãn nhằm làm tăng điểm. Nếu phát hiện lỗi gold trước lượt chạy, sửa có lịch sử và tạo frozen version mới.

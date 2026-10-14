# Phiếu đọc và gán nhãn trước khi xem kết quả

12 transcript tổng hợp mới, chưa chạy LLM và chưa có đáp án. Bạn/người thứ hai đọc từng transcript và điền JSON annotations theo PROSPECTIVE_EVALUATION.md. Không dùng đầu ra AI để viết đáp án. Tác giả transcript vẫn là trợ lý triển khai, vì vậy không gọi đây là benchmark độc lập.

## N01 — Lựa chọn đơn vị giao hàng

Độ khó dự kiến: easy · 6 phát biểu. Độ khó là metadata, không dự đoán model sẽ đúng/sai.

```text
L001 | Quỳnh | Buổi này chỉ chọn đơn vị giao hàng cho đợt bán thử miền Nam.
L002 | Hải | Tôi đề xuất giao cho đơn vị Sao vì giá thấp hơn.
L003 | My | Sao chưa có tuyến giao trong ngày ở khu vực thử nghiệm; đơn vị Mây có tuyến đó.
L004 | Hải | Vậy tôi rút đề xuất Sao và đồng ý dùng Mây cho đợt thử.
L005 | Quỳnh | Thống nhất Mây cho đợt thử miền Nam. Chưa chọn đơn vị cho miền Bắc.
L006 | My | Miền Bắc sẽ bàn ở một cuộc họp khác; hôm nay không giao việc liên hệ bên nào.
```

Người gán nhãn: ______ · Thời gian: ______ · Đã chốt nhãn trước đầu ra model: ______

| Loại | Nội dung còn giá trị sau họp | Trạng thái cuối | Người/hạn/điều kiện | Câu nguồn và câu thay đổi |
|---|---|---|---|---|
| Chưa gán nhãn | | | | |

Thông tin không nên sinh / cách diễn đạt tương đương / điểm còn mơ hồ: ______

## N02 — Thay người và hạn tài liệu hướng dẫn

Độ khó dự kiến: easy · 6 phát biểu. Độ khó là metadata, không dự đoán model sẽ đúng/sai.

```text
L001 | Tâm | Phương làm bản hướng dẫn kích hoạt tài khoản, hạn sáng thứ Tư nhé.
L002 | Phương | Tôi nhận bản hướng dẫn đó.
L003 | Phương | Nhưng thứ Tư tôi trực hỗ trợ cả ngày, không thể làm kịp.
L004 | Tâm | Chuyển bản hướng dẫn sang Uyên, hạn chiều thứ Sáu; không giữ hạn thứ Tư nữa.
L005 | Uyên | Tôi nhận làm bản hướng dẫn, gửi chiều thứ Sáu.
L006 | Tâm | Đúng, Uyên phụ trách. Phương không còn phụ trách bản này; chưa giao người hỗ trợ.
```

Người gán nhãn: ______ · Thời gian: ______ · Đã chốt nhãn trước đầu ra model: ______

| Loại | Nội dung còn giá trị sau họp | Trạng thái cuối | Người/hạn/điều kiện | Câu nguồn và câu thay đổi |
|---|---|---|---|---|
| Chưa gán nhãn | | | | |

Thông tin không nên sinh / cách diễn đạt tương đương / điểm còn mơ hồ: ______

## N03 — Phản hồi người dùng về đăng ký

Độ khó dự kiến: easy · 5 phát biểu. Độ khó là metadata, không dự đoán model sẽ đúng/sai.

```text
L001 | Lệ | Nhóm khách dùng thử phản hồi rằng trang đăng ký có quá nhiều ô nhập.
L002 | Sơn | Khách yêu cầu chỉ bắt buộc số điện thoại và mã xác nhận trong bước đầu.
L003 | Lệ | Họ cũng khen phần hướng dẫn bằng hình dễ hiểu; đó là phản hồi, không phải yêu cầu thêm hình.
L004 | Sơn | Ghi nhận yêu cầu giảm trường bắt buộc. Chưa chốt thiết kế thay thế và chưa giao ai triển khai.
L005 | Hạnh | Có khách hỏi đăng ký qua email được không, nhưng họ chưa yêu cầu bỏ đăng ký bằng số điện thoại.
```

Người gán nhãn: ______ · Thời gian: ______ · Đã chốt nhãn trước đầu ra model: ______

| Loại | Nội dung còn giá trị sau họp | Trạng thái cuối | Người/hạn/điều kiện | Câu nguồn và câu thay đổi |
|---|---|---|---|---|
| Chưa gán nhãn | | | | |

Thông tin không nên sinh / cách diễn đạt tương đương / điểm còn mơ hồ: ______

## N04 — Hủy một cách triển khai nhưng giữ nhu cầu

Độ khó dự kiến: medium · 6 phát biểu. Độ khó là metadata, không dự đoán model sẽ đúng/sai.

```text
L001 | Diệp | Bộ phận vận hành cần tải danh sách đơn dưới dạng XLSX.
L002 | Bảo | Nhờ Trúc thử cách xuất bằng công cụ K, hạn trưa mai.
L003 | Trúc | Tôi nhận thử công cụ K.
L004 | Bảo | Hủy việc thử công cụ K vì không phù hợp chính sách dữ liệu, bỏ hạn trưa mai.
L005 | Diệp | Nhu cầu tải XLSX vẫn giữ. Chưa chọn cách khác và chưa giao đầu việc thay thế.
L006 | Trúc | Tôi hiểu: tôi không còn làm thử K; câu này không phải đề xuất tiếp tục thử.
```

Người gán nhãn: ______ · Thời gian: ______ · Đã chốt nhãn trước đầu ra model: ______

| Loại | Nội dung còn giá trị sau họp | Trạng thái cuối | Người/hạn/điều kiện | Câu nguồn và câu thay đổi |
|---|---|---|---|---|
| Chưa gán nhãn | | | | |

Thông tin không nên sinh / cách diễn đạt tương đương / điểm còn mơ hồ: ______

## N05 — Báo khắc phục vướng mắc nhưng chưa xác minh

Độ khó dự kiến: medium · 5 phát biểu. Độ khó là metadata, không dự đoán model sẽ đúng/sai.

```text
L001 | Nam | Máy quét mã ở quầy số hai không gửi được kết quả về hệ thống từ sáng.
L002 | Oanh | Tôi vừa thay dây mạng; máy quét đã gửi được ba lượt thử.
L003 | Nam | Đó là kết quả bạn báo lại, bên vận hành chưa kiểm tra độc lập cả ca làm việc.
L004 | Oanh | Đúng, tôi chỉ báo lỗi kết nối đã hết trong lượt thử; chưa xác nhận không tái phát.
L005 | Nam | Ghi nhận lời báo khắc phục và việc chưa được kiểm chứng. Cuộc họp chưa giao nhiệm vụ kiểm tra cho ai.
```

Người gán nhãn: ______ · Thời gian: ______ · Đã chốt nhãn trước đầu ra model: ______

| Loại | Nội dung còn giá trị sau họp | Trạng thái cuối | Người/hạn/điều kiện | Câu nguồn và câu thay đổi |
|---|---|---|---|---|
| Chưa gán nhãn | | | | |

Thông tin không nên sinh / cách diễn đạt tương đương / điểm còn mơ hồ: ______

## N06 — Thay điều kiện trước khi mở chương trình

Độ khó dự kiến: medium · 6 phát biểu. Độ khó là metadata, không dự đoán model sẽ đúng/sai.

```text
L001 | Kiên | Dự kiến mở chương trình ưu đãi nếu có 80 cửa hàng đồng ý tham gia.
L002 | Thảo | Tôi đề nghị nâng lên 100 cửa hàng và phải kiểm thử thanh toán không có lỗi nghiêm trọng.
L003 | Kiên | Chốt mở chương trình khi đủ 100 cửa hàng và kiểm thử thanh toán không có lỗi nghiêm trọng; bỏ mốc 80.
L004 | Thảo | Hiện chỉ có 92 cửa hàng, phần kiểm thử vẫn chưa kết thúc.
L005 | Kiên | Chưa đủ điều kiện để mở ngay; không phải hủy quyết định có điều kiện vừa chốt.
L006 | Thảo | Hôm nay không chốt ngày mở chương trình.
```

Người gán nhãn: ______ · Thời gian: ______ · Đã chốt nhãn trước đầu ra model: ______

| Loại | Nội dung còn giá trị sau họp | Trạng thái cuối | Người/hạn/điều kiện | Câu nguồn và câu thay đổi |
|---|---|---|---|---|
| Chưa gán nhãn | | | | |

Thông tin không nên sinh / cách diễn đạt tương đương / điểm còn mơ hồ: ______

## N07 — Ngắt lời và đại từ chưa rõ người nhận

Độ khó dự kiến: medium · 7 phát biểu. Độ khó là metadata, không dự đoán model sẽ đúng/sai.

```text
L001 | Điều phối | Trước lượt diễn tập tiếp theo, cần kiểm tra đường thoát của khu sự kiện.
L002 | Khánh | Anh ấy nhận kiểm tra rồi phải không?
L003 | Mai | Khoan, anh ấy là ai? Tôi chưa nghe ai nhận cả.
L004 | Điều phối | Chưa có người nhận. Đừng ghi tên Khánh hoặc Mai chỉ vì hai người đang nói.
L005 | Khánh | Có thể diễn tập thứ Hai, à không, thứ Ba cũng được.
L006 | Điều phối | Hai ngày mới là gợi ý. Chưa chọn ngày diễn tập; yêu cầu kiểm tra trước lượt tiếp theo vẫn giữ.
L007 | Mai | Cần hỏi thêm lịch của ban tổ chức rồi mới bàn người và ngày.
```

Người gán nhãn: ______ · Thời gian: ______ · Đã chốt nhãn trước đầu ra model: ______

| Loại | Nội dung còn giá trị sau họp | Trạng thái cuối | Người/hạn/điều kiện | Câu nguồn và câu thay đổi |
|---|---|---|---|---|
| Chưa gán nhãn | | | | |

Thông tin không nên sinh / cách diễn đạt tương đương / điểm còn mơ hồ: ______

## N08 — Đọc quyết định cũ và tách cuộc họp hiện tại

Độ khó dự kiến: medium · 6 phát biểu. Độ khó là metadata, không dự đoán model sẽ đúng/sai.

```text
L001 | Thu | Tôi đọc biên bản tuần trước: "Chốt dùng phòng A cho hội thảo".
L002 | Dũng | Đó là quyết định tuần trước, nhưng hôm nay biết phòng A đang sửa điện.
L003 | Thu | Mở lại lựa chọn địa điểm. Hôm nay chưa chọn A hay B.
L004 | Dũng | Ban tổ chức yêu cầu có phương án phòng phù hợp trước lần xác nhận vé tiếp theo.
L005 | Thu | Ghi yêu cầu đó, chưa giao người làm và chưa có ngày xác nhận vé cụ thể.
L006 | Dũng | Tôi nhắc lại câu "Chốt phòng A" chỉ để nói lịch sử, không chốt A lại.
```

Người gán nhãn: ______ · Thời gian: ______ · Đã chốt nhãn trước đầu ra model: ______

| Loại | Nội dung còn giá trị sau họp | Trạng thái cuối | Người/hạn/điều kiện | Câu nguồn và câu thay đổi |
|---|---|---|---|---|
| Chưa gán nhãn | | | | |

Thông tin không nên sinh / cách diễn đạt tương đương / điểm còn mơ hồ: ______

## N09 — Trao đổi trước giờ họp không tạo cam kết

Độ khó dự kiến: easy · 5 phát biểu. Độ khó là metadata, không dự đoán model sẽ đúng/sai.

```text
L001 | Hà | Một hai, mọi người nghe tiếng mic chưa?
L002 | Bình | Nghe rồi, tôi đang chỉnh âm lượng tai nghe.
L003 | Hà | Ta chưa bắt đầu phần nội dung. Tôi chỉ đang thử âm thanh.
L004 | Bình | Tôi cũng đang thử camera, chưa có đề xuất hay yêu cầu công việc.
L005 | Hà | Đoạn ghi âm này kết thúc trước khi họp chính thức bắt đầu.
```

Người gán nhãn: ______ · Thời gian: ______ · Đã chốt nhãn trước đầu ra model: ______

| Loại | Nội dung còn giá trị sau họp | Trạng thái cuối | Người/hạn/điều kiện | Câu nguồn và câu thay đổi |
|---|---|---|---|---|
| Chưa gán nhãn | | | | |

Thông tin không nên sinh / cách diễn đạt tương đương / điểm còn mơ hồ: ______

## N10 — Tri thức chưa chắc chắn và yêu cầu xác minh

Độ khó dự kiến: medium · 5 phát biểu. Độ khó là metadata, không dự đoán model sẽ đúng/sai.

```text
L001 | Nga | Tôi nhớ hệ thống lưu dấu vết truy cập trong 45 ngày, nhưng chưa chắc đây là cấu hình hiện tại.
L002 | Vũ | Tài liệu cũ tôi đọc ghi 30 ngày. Không nên coi một trong hai số là đã xác minh.
L003 | Nga | Cần đối chiếu tài liệu cấu hình mới trước khi trả lời khách.
L004 | Vũ | Chưa ai nhận việc đối chiếu và cuộc họp không chốt hạn.
L005 | Nga | Không có quyết định đổi thời gian lưu. Hai con số chỉ là thông tin đang cần xác minh.
```

Người gán nhãn: ______ · Thời gian: ______ · Đã chốt nhãn trước đầu ra model: ______

| Loại | Nội dung còn giá trị sau họp | Trạng thái cuối | Người/hạn/điều kiện | Câu nguồn và câu thay đổi |
|---|---|---|---|---|
| Chưa gán nhãn | | | | |

Thông tin không nên sinh / cách diễn đạt tương đương / điểm còn mơ hồ: ______

## N11 — Nhiều chủ đề: kiểm kê, tài liệu và phản hồi

Độ khó dự kiến: hard · 72 phát biểu. Độ khó là metadata, không dự đoán model sẽ đúng/sai.

```text
L001 | Huy | Họp này có ba phần: lịch kiểm kê, tài liệu kho và phản hồi màn hình hàng về.
L002 | Linh | Tôi đề xuất kiểm kê khu lạnh vào sáng thứ Năm.
L003 | Huy | Đồng ý lịch thứ Năm tạm thời, lát nữa xem lịch xe rồi chốt lại.
L004 | Vy | Màn hình hàng về đang khó tìm nút xác nhận theo phản hồi của ca tối.
L005 | Huy | Ghi lại phản hồi đó, chưa có thiết kế mới.
L006 | Bình | Ca sáng dùng máy tính bảng, ca tối chủ yếu dùng máy bàn.
L007 | Vy | Phản hồi khó tìm nút đến từ máy bàn, không phải kết luận lỗi trên mọi thiết bị.
L008 | Linh | Khu lạnh có hai lối vào và lịch xe hiện còn chờ xác nhận.
L009 | Huy | Chưa đổi quy trình nhập hàng ở phần này.
L010 | Bình | Tài liệu kiểm kê có sơ đồ vị trí các kệ.
L011 | Huy | Bình sửa phần sơ đồ trong tài liệu, hạn chiều thứ Tư.
L012 | Bình | Tôi nhận sửa sơ đồ trong tài liệu.
L013 | Vy | Trong hình hiện tại mã kệ phía đông bị che bởi chú thích.
L014 | Bình | Tôi thấy ghi chú đó, còn bản sơ đồ mới chưa hoàn tất.
L015 | Huy | Việc sửa tài liệu tách khỏi việc kiểm kê, không phụ thuộc ngày kiểm kê.
L016 | Linh | Đơn vị xe nói thứ Năm vẫn có thể thay đổi giờ.
L017 | Huy | Ta quay lại lịch ở cuối buổi, chưa sửa kết luận tạm thời bây giờ.
L018 | Vy | Một phản hồi nữa là chữ ở màn hình xác nhận nhỏ khi dùng màn hình cũ.
L019 | Bình | Máy mới không có cùng phản hồi; cần giữ rõ phạm vi phản hồi.
L020 | Huy | Chưa giao ai thay đổi chữ hoặc nút trong cuộc họp này.
L021 | Linh | Cửa khu lạnh mở theo ca vận hành của kho.
L022 | Vy | Phiếu kiểm kê giấy có mã kệ và mã lô riêng.
L023 | Bình | Đừng gộp mã kệ với mã lô trong phần chú thích.
L024 | Huy | Đây là mô tả tài liệu, không phải giao một công việc mới cho Vy.
L025 | Linh | Xe chưa xác nhận giờ đến, nên giờ kiểm kê chưa đủ chắc chắn.
L026 | Vy | Tôi chỉ báo thông tin ca tối gửi lại, chưa kiểm tra độc lập giao diện.
L027 | Bình | Sơ đồ hiện có bản tiếng Việt, chưa có bản tiếng Anh.
L028 | Huy | Cuộc họp này không quyết định dịch tài liệu.
L029 | Linh | Thứ Năm có khả năng trùng chuyến hàng bổ sung.
L030 | Vy | Người dùng muốn nhìn thấy nút xác nhận rõ hơn, chưa đề nghị đổi vị trí cụ thể.
L031 | Bình | Trong tài liệu, khu lạnh được ghi bằng ký hiệu K.
L032 | Huy | Không coi ký hiệu tài liệu là lựa chọn lịch kiểm kê.
L033 | Linh | Tôi sẽ đọc thông báo lịch xe khi bên xe trả lời trong buổi này.
L034 | Vy | Đó là lời mô tả việc đang làm trong buổi họp, chưa phải đầu việc sau họp.
L035 | Bình | Sơ đồ khu thường nằm ở trang kế tiếp.
L036 | Huy | Phần giao Bình lúc nãy chỉ là sơ đồ khu lạnh.
L037 | Linh | Có người hỏi kiểm kê cả kho, nhưng hôm nay phạm vi chỉ khu lạnh.
L038 | Vy | Ca tối nói cần phản hồi riêng cho màn hình hàng về.
L039 | Bình | Tôi chưa nhận việc sửa giao diện.
L040 | Huy | Đúng, không gộp việc sửa tài liệu với sửa giao diện.
L041 | Linh | Thông báo xe cũ ghi chiều thứ Năm nhưng có thể không còn đúng.
L042 | Huy | Chưa dùng thông báo cũ để chốt lại lịch.
L043 | Vy | Tôi còn giữ nguyên phản hồi về nút khó tìm.
L044 | Bình | Hạn tài liệu chiều thứ Tư vẫn là hạn đang được nhắc ở thời điểm này.
L045 | Huy | Ta còn phần kết luận cuối để xem có cần đổi người làm tài liệu.
L046 | Linh | Ca kiểm kê cần kho đóng tiếp nhận hàng ở khu lạnh.
L047 | Vy | Chưa có người được giao thay đổi lịch tiếp nhận hàng.
L048 | Bình | Chú thích sơ đồ hiện có cả vị trí cảm biến.
L049 | Huy | Không có quyết định thay cảm biến trong buổi này.
L050 | Linh | Bên xe đang gửi thông báo mới.
L051 | Vy | Khi chốt lịch nên đọc rõ đó là lịch cuối, tránh dùng lịch đầu buổi.
L052 | Bình | Tôi có lịch trực hỗ trợ vào chiều thứ Tư.
L053 | Huy | Cảm ơn, lát nữa sẽ đổi người nếu cần.
L054 | Linh | Thông báo mới xác nhận xe đến sáng thứ Năm.
L055 | Huy | Vậy lịch kiểm kê sáng thứ Năm cần thay đổi.
L056 | Vy | Màn hình khó tìm nút vẫn là phản hồi chưa được xử lý.
L057 | Bình | Tôi không thể hoàn tất sơ đồ chiều thứ Tư vì ca trực.
L058 | Huy | Chuyển việc sửa sơ đồ khu lạnh sang Linh, bỏ hạn chiều thứ Tư.
L059 | Linh | Tôi nhận sửa sơ đồ, gửi sáng thứ Sáu.
L060 | Huy | Chốt Linh làm sơ đồ khu lạnh, hạn sáng thứ Sáu; Bình không còn phụ trách.
L061 | Vy | Tôi đọc lại phản hồi ca tối để ghi nhận, không nhận việc sửa giao diện.
L062 | Huy | Quyết định lịch kiểm kê: bỏ sáng thứ Năm, chuyển sang chiều thứ Sáu.
L063 | Linh | Tôi đồng ý kiểm kê khu lạnh chiều thứ Sáu.
L064 | Huy | Chốt chiều thứ Sáu cho khu lạnh, chưa chọn lịch cho khu thường.
L065 | Bình | Có cần chuyển cả hạn sơ đồ sang chiều thứ Sáu không?
L066 | Huy | Không. Sơ đồ vẫn gửi sáng thứ Sáu, lịch kiểm kê là chiều thứ Sáu.
L067 | Vy | Nút xác nhận và chữ nhỏ vẫn là phản hồi được ghi nhận, chưa có phương án sửa.
L068 | Linh | Không có đầu việc mới về lịch xe sau cuộc họp.
L069 | Bình | Tôi hiểu việc tài liệu đã chuyển sang Linh.
L070 | Huy | Các mô tả cảm biến không phải quyết định mua hoặc thay thiết bị.
L071 | Vy | Không bổ sung người phụ trách sửa giao diện từ việc tôi báo phản hồi.
L072 | Huy | Kết thúc với lịch khu lạnh chiều thứ Sáu và tài liệu Linh gửi sáng thứ Sáu.
```

Người gán nhãn: ______ · Thời gian: ______ · Đã chốt nhãn trước đầu ra model: ______

| Loại | Nội dung còn giá trị sau họp | Trạng thái cuối | Người/hạn/điều kiện | Câu nguồn và câu thay đổi |
|---|---|---|---|---|
| Chưa gán nhãn | | | | |

Thông tin không nên sinh / cách diễn đạt tương đương / điểm còn mơ hồ: ______

## N12 — Lịch cũ, hủy triển khai và mở lại ở cuối

Độ khó dự kiến: hard · 80 phát biểu. Độ khó là metadata, không dự đoán model sẽ đúng/sai.

```text
L001 | An | Ta bàn hai tuyến tham quan Bắc và Nam cùng bản hướng dẫn khách.
L002 | Phúc | Khách yêu cầu có bản hướng dẫn tiếng Anh cho cả hai tuyến.
L003 | An | Giao Hòa thử làm bản hướng dẫn bằng công cụ M, hạn tối mai.
L004 | Hòa | Tôi nhận thử công cụ M.
L005 | Lan | Tôi đọc biên bản tháng trước: "Chốt tuyến Bắc khởi hành 7 giờ".
L006 | An | Đó là lịch tháng trước, chưa phải lịch hôm nay.
L007 | Phúc | Tuyến Nam đang có phản hồi xe đến điểm đón trễ.
L008 | Lan | Phản hồi này chỉ liên quan tuyến Nam.
L009 | An | Ta sẽ bàn lại tuyến Bắc khi có thông báo của điểm tham quan.
L010 | Hòa | Bản hướng dẫn hiện có mô tả điểm đón và số điện thoại tổng đài giả lập trong tài liệu.
L011 | An | Không cần đưa số tổng đài vào quyết định vận hành.
L012 | Phúc | Tuyến Bắc đi qua điểm bảo tàng, tuyến Nam đi qua công viên.
L013 | Lan | Chưa có yêu cầu thay đổi các điểm tham quan.
L014 | Hòa | Công cụ M đang có giới hạn dùng thương mại.
L015 | An | Chưa kết luận về công cụ, đợi phần cuối buổi.
L016 | Phúc | Xe tuyến Nam có hai điểm đón.
L017 | Lan | Có khách hỏi bỏ điểm đón thứ hai nhưng chưa có đề nghị chính thức.
L018 | An | Chưa chốt bỏ điểm đón nào.
L019 | Hòa | Bản tiếng Việt có phần hướng dẫn nhận vé.
L020 | Phúc | Khách nước ngoài yêu cầu bản tiếng Anh, không yêu cầu đổi loại vé.
L021 | Lan | Thông báo điểm tham quan tuyến Bắc còn chờ.
L022 | An | Lịch 7 giờ tôi nghe lúc đầu là lịch cũ.
L023 | Hòa | Tôi chưa báo hoàn thành thử công cụ M.
L024 | Phúc | Phản hồi xe trễ vẫn chưa có báo khắc phục.
L025 | Lan | Tuyến Nam chưa có quyết định giờ khởi hành mới.
L026 | An | Không dùng giờ tuyến Bắc để điền cho tuyến Nam.
L027 | Hòa | Tài liệu có hình bản đồ các điểm đón.
L028 | Phúc | Khách không yêu cầu thay bản đồ trong buổi này.
L029 | Lan | Có thể tuyến Bắc đi muộn hơn nhưng đó là suy đoán của tôi.
L030 | An | Chưa coi suy đoán là một giờ được thống nhất.
L031 | Hòa | Điều khoản công cụ M vừa được bộ phận mua sắm gửi lại.
L032 | Phúc | Yêu cầu tiếng Anh vẫn còn, chưa có bản mới.
L033 | Lan | Tôi muốn giữ riêng những gì thuộc tuyến Bắc và tuyến Nam.
L034 | An | Đúng, hai lịch khởi hành không cùng một chủ đề.
L035 | Hòa | Tài liệu khách dùng không phải lịch phân công nhân sự.
L036 | Phúc | Tôi đang đọc phản hồi đã gửi từ hôm qua.
L037 | Lan | Đọc phản hồi cũ không chứng minh vấn đề đã hết hôm nay.
L038 | An | Chưa có lời báo xe tuyến Nam đã đúng giờ trở lại.
L039 | Hòa | Tôi chỉ kiểm tra điều khoản trong cuộc họp, không nhận việc khác sau họp.
L040 | Phúc | Khách còn hỏi có bản hướng dẫn dễ đọc trên điện thoại không.
L041 | Lan | Câu hỏi đó chưa phải yêu cầu đổi định dạng.
L042 | An | Không giao thêm việc từ câu hỏi này.
L043 | Hòa | Công cụ M không cho dùng trong mục đích thương mại của đợt này.
L044 | An | Hủy việc thử công cụ M, bỏ hạn tối mai. Đây là lý do hủy, không phải điều kiện để tiếp tục dùng M.
L045 | Hòa | Tôi không còn làm thử M.
L046 | Phúc | Yêu cầu hướng dẫn tiếng Anh vẫn giữ dù hủy thử M.
L047 | Lan | Chưa chọn cách làm thay thế và chưa giao ai làm bản hướng dẫn mới.
L048 | An | Ghi rõ cách làm hướng dẫn thay thế còn mở.
L049 | Hòa | Đừng ghi tôi tiếp tục làm chỉ vì tôi từng nhận thử M.
L050 | Phúc | Phần phản hồi tuyến Nam vẫn chưa xử lý.
L051 | Lan | Điểm tham quan tuyến Bắc vừa báo mở cửa từ 9 giờ.
L052 | An | Đề xuất tuyến Bắc khởi hành 8 giờ thay vì lịch cũ 7 giờ.
L053 | Phúc | Tôi đồng ý 8 giờ cho tuyến Bắc.
L054 | Lan | Đồng ý, nhưng thông báo mở cửa này chỉ cho ngày chạy thử.
L055 | An | Thống nhất tuyến Bắc khởi hành 8 giờ trong ngày chạy thử; không áp dụng cho mọi ngày.
L056 | Hòa | Quyết định lịch đó không giao lại việc công cụ M.
L057 | Phúc | Tuyến Nam cần xác nhận giờ với nhà xe.
L058 | Lan | Chưa ai nhận việc liên hệ nhà xe.
L059 | An | Ghi nhu cầu xác nhận giờ tuyến Nam, chưa chốt giờ và chưa giao người.
L060 | Hòa | Hạn tối mai đã bị bỏ đối với thử công cụ M.
L061 | Phúc | Yêu cầu tiếng Anh không có hạn mới trong buổi này.
L062 | Lan | Tôi nhắc giờ 7 giờ để đối chiếu lịch tháng trước thôi.
L063 | An | Không khôi phục lịch 7 giờ bằng việc nhắc lại đó.
L064 | Hòa | Công cụ thay thế chưa được chọn.
L065 | Phúc | Phản hồi xe tuyến Nam trễ là phản hồi còn cần chú ý.
L066 | Lan | Tôi vừa nhận thông báo bổ sung: ngày chạy thử chưa được xác nhận cuối cùng.
L067 | An | Vậy mở lại quyết định 8 giờ tuyến Bắc. Chưa chốt giờ khởi hành cho ngày chưa xác nhận.
L068 | Phúc | Đồng ý mở lại, chưa chọn 7 giờ hay 8 giờ.
L069 | Hòa | Yêu cầu hướng dẫn tiếng Anh không bị rút vì mở lại lịch.
L070 | Lan | Đúng, lịch và yêu cầu tài liệu là hai vấn đề khác nhau.
L071 | An | Cuối buổi: tuyến Bắc chưa chốt giờ, tuyến Nam cũng chưa chốt giờ.
L072 | Phúc | Khách vẫn cần hướng dẫn tiếng Anh cho cả hai tuyến.
L073 | Hòa | Việc thử M đã hủy, người từng nhận là tôi; không còn hạn tối mai.
L074 | Lan | Không có quyết định chọn công cụ mới.
L075 | An | Chưa giao người làm tài liệu thay thế.
L076 | Phúc | Không có lời xác nhận xe tuyến Nam hết trễ.
L077 | Hòa | Những câu đọc biên bản cũ không phải kết luận hôm nay.
L078 | Lan | Những giờ từng đề xuất giữ trong lịch sử, không dùng làm giờ đã chốt.
L079 | An | Chúng ta chưa có ngày chạy thử chắc chắn.
L080 | Phúc | Kết thúc, giữ riêng yêu cầu tài liệu, lịch từng tuyến và phản hồi xe trễ.
```

Người gán nhãn: ______ · Thời gian: ______ · Đã chốt nhãn trước đầu ra model: ______

| Loại | Nội dung còn giá trị sau họp | Trạng thái cuối | Người/hạn/điều kiện | Câu nguồn và câu thay đổi |
|---|---|---|---|---|
| Chưa gán nhãn | | | | |

Thông tin không nên sinh / cách diễn đạt tương đương / điểm còn mơ hồ: ______


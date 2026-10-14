# Hướng dẫn dữ liệu kiểm thử

## Phân loại tình huống

| Case | Phải thể hiện | Điểm khó |
|---|---|---|
| T01 | Nhiều loại thông tin, chưa chốt ngày phát hành | Không để một chủ đề chưa chốt làm hỏng quyết định khác |
| T02 | A → B đã chốt | Không xuất A thành kết quả cuối |
| T03 | B đã chốt → mở lại | Phản chứng L003 quyết định trạng thái cuối |
| T04 | B đã chốt nhưng bị chặn triển khai | Phân biệt `meeting_status` và `execution_status` |
| T05 | Đổi Minh → Lan; thiếu hạn | Không bịa hạn và không giữ phân công cũ |
| T06 | Giao diện và máy chủ xen kẽ | Phân nhóm phát biểu theo vấn đề |
| T07 | Phản hồi, yêu cầu, vướng mắc, tri thức, chưa chốt | Không biến thông tin chưa xác minh thành sự thật |

## Cách gán nhãn

Mỗi case có `samples/expected/Txx.json` gồm loại bản ghi, trạng thái kỳ vọng, câu nguồn bắt buộc, và các trường phải để trống. Chúng là **dữ liệu kiểm thử**, không được đính kèm prompt khi chạy LLM.

Script ghép đáp án với kết quả một-một; một bản ghi không được dùng để đáp ứng
nhiều mục kỳ vọng. Bản ghi dư mặc định khiến ca thất bại. Chỉ đặt
`allow_extra_records: true` nếu bộ nhãn được xác định trước là không đầy đủ,
và phải ghi rõ giới hạn đó trong báo cáo. Đây vẫn là kiểm tra các trường được
gán nhãn, không thay thế việc con người đọc và chấm ý nghĩa.

Ngày 12/10/2026 sửa thiếu nhãn T06: L005 có phản hồi “menu đang khó tìm” nhưng
đáp án cũ không liệt kê feedback. Bổ sung mục này theo transcript gốc, không
thay đổi transcript hay kỳ vọng của các quyết định/phân công. T01 và T05
bổ sung kiểm tra người hỗ trợ Minh đã được nêu trong câu nguồn.

T01–T07 là bộ phát triển đã được dùng để viết fixture và sửa phần mềm.
Không gọi chúng là tập đánh giá độc lập. Cần bộ transcript khác có đáp án lập
trước khi chạy để kiểm tra khả năng khái quát của LLM; chưa có kết quả đó.

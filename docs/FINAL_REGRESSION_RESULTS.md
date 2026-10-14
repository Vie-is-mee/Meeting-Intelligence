# Kết quả hồi quy cố định — core lượt 5

Đã chạy đủ 8/8 case qua extraction và audit trong cùng một lượt, giữ nguyên core/prompt/model/config. Không chọn lại câu trả lời thuận lợi, không thay nhãn. Đây là hồi quy phát triển trên các case đã dùng để sửa, không phải benchmark độc lập hoặc điểm mới toàn bộ 24 transcript.

Model: `openai/gpt-oss-120b`; temperature 0.6, reasoning low, extraction budget 2560, audit budget 1024. Khoảng cách API tối thiểu 90.0 giây; max_retries=0. Bắt đầu UTC: 2026-10-14T02:13:33.065679+00:00.

**Hoàn tất pipeline + audit: 8/8. Theo tiêu chí đầy đủ dữ liệu và không cảnh báo audit sai: 4 đạt, 4 chưa đạt. Riêng dữ liệu lõi: 5/8 đạt tiêu chí case trong lượt này.** Không gọi các tỷ lệ case nhỏ này là precision/recall của model.

| Case | Kỳ vọng | Kết quả thực tế | Đạt/Chưa đạt | Điều học được |
|---|---|---|---|---|
| H03 | Request rà soát trước lần thử tiếp theo, chưa chọn ngày/người. | Chỉ có decision open; thiếu request và hạn tương đối. Audit đòi thể hiện đề xuất ngày trong bản ghi cuối, không phát hiện request thiếu. | Chưa đạt | Có kết luận cuối đúng vẫn chưa đủ nếu bỏ sót cả yêu cầu; chất lượng không ổn định giữa lần sinh. |
| LC03 | Giữ scope thử nội bộ/request nút quay lại; task hướng dẫn cancelled, owner lịch sử Chi, hạn null. | Các bản ghi và trường lõi đúng; audit medium đòi xóa owner lịch sử sau hủy dù không có lệnh xóa. | Chưa đạt (lõi đúng, audit sai) | Phân biệt độ đúng dữ liệu và độ đúng cảnh báo audit; cảnh báo sai vẫn là hạn chế. |
| D01 | Chuyển từ lưu máy chủ sang object storage cho thử nghiệm; nhà cung cấp chưa chọn. | Decision agreed object storage, decision open nhà cung cấp, nguồn trạng thái/nội dung L006, không tự đặt người/hạn. | Đạt | Tình huống đổi ý rồi chốt cuối hoạt động trong lượt này; chưa chứng minh độ ổn định nhiều lần sinh. |
| D03 | Agreed trong phạm vi thiết kế, blocked đến khi pháp chế duyệt, issue hợp đồng riêng. | Đủ decision agreed/blocked/phạm vi/condition; nguồn nội dung L003, execution và condition L005; issue open L004, needs_review. | Đạt | Tách quyết định trong họp và điều kiện triển khai, giữ nguồn riêng từng trường. |
| D04 | Conditional/pending_condition với 300 người đồng thời AND không lỗi nghiêm trọng; chưa đạt điều kiện. | Đúng đầy đủ điều kiện thay thế, nguồn L003; không bịa người/hạn; needs_review. Audit trống. | Đạt | Điều kiện chưa được xác nhận đạt không có nghĩa mở lại quyết định. |
| H01 | Lựa chọn reopened/condition null; action Huy assigned không hạn. | Đúng hai bản ghi, nguồn mở lại L004, owner Huy L002; audit trống, không tự hủy action. | Đạt | Mở lại lựa chọn không tự hủy công việc độc lập; giữ điều kiện cũ trong history thay vì trường hiện hành. |
| LC01 | Một action cancelled, owner lịch sử Mai, hạn null; không request/decision phụ. | Action đúng nhưng có request recorded trùng câu giao việc. Guard needs_review và audit high unsupported_fact dẫn L003 phát hiện request thừa. | Chưa đạt | Một bản ghi có nguồn vẫn có thể sai vai trò nghiệp vụ. Cảnh báo giảm rủi ro, không sửa phân loại. |
| LC02 | Request CSV giữ, task thử thư viện X cancelled/Dũng/hạn null; cách thay thế open, không proposal phụ. | Request và task cancelled/Dũng/hạn null đúng, nhưng thiếu decision cách thay thế chưa chốt; thêm proposal thử thư viện X. Audit medium đòi lý do hủy giấy phép không phù hợp thành condition hiện hành. | Chưa đạt | Lý do hủy không phải điều kiện triển khai; sửa xóa hạn chưa giải quyết bỏ sót/chia sai loại bản ghi. |

## Ý nghĩa kết quả

- D01 chứng minh tình huống bắt buộc: lựa chọn đầu bị thay đổi, giữ đúng lựa chọn cuối và nhà cung cấp chưa chọn.
- D03/D04/H01 chứng minh phân biệt phạm vi, chặn triển khai, điều kiện thay đổi và mở lại mà không hủy việc độc lập.
- H03 thiếu cả request/hạn tương đối; không thể khôi phục một bản ghi model không tạo. Kết quả tốt ở lượt cũ không thay thế thất bại hiện tại.
- LC01 tạo request thừa; guard và audit có phát hiện nhưng vẫn chưa sửa được dữ liệu. Không tự dùng request này cho công việc.
- LC02 lần này xóa hạn đúng (clear_fields có due_raw), nhưng bỏ lựa chọn thay thế chưa chốt và tạo proposal phụ. Khác với lỗi bỏ clear_fields ở lượt trước; không xem một trường đã đúng là cả case đạt.
- LC03 đúng dữ liệu lõi nhưng audit đòi xóa owner lịch sử. LC02 audit nhầm lý do hủy thành điều kiện; H03 audit đòi đề xuất ngày trong bản ghi cuối thay vì phát hiện request thiếu. Audit vẫn không đáng tin như một người phán quyết.

## Phiên bản và chi phí quan sát

16 API attempts; provider báo 37,817 tokens. Tổng thời gian các case 1351.1s gồm khoảng nghỉ chủ động; không phải latency xử lý thuần của model. Không gặp lỗi API/quota trong lượt này.

105/105 test phần mềm đã đạt ở phiên bản core này. Hash input/core trong artifact được đối chiếu lại sau khi chạy, không thay đổi. Unit tests không phải kết quả LLM. Nhãn và semantic review đều do cùng trợ lý tạo/rà soát, chưa có người đánh giá độc lập.

Artifact: [lượt API nguyên bản](evaluation/final_regression_round5_retry2.json), [review và tổng hợp](evaluation/final_regression_round5_review.json), [input/nhãn cố định](evaluation/final_regression_input_v2.json). Giữ baseline và mọi lỗi quota cũ.

## Quyết định sau hồi quy

Hoàn tất lượt hồi quy này, chưa tuyên bố hệ thống hoàn hảo hay production-ready. Giữ phiên bản làm ứng viên demo có hạn chế; không tiếp tục chỉnh prompt trong lượt này. Chọn D01 cho yêu cầu đổi ý/chốt cuối, D03 hoặc D04 cho thành công, LC03 cho khó/audit sai, LC01 và H03 cho thất bại thật. Đủ ít nhất 5 case với cùng phiên bản trong báo cáo này.

Tiếp theo chuyển sang hoàn thiện demo và bài nộp: trình bày evidence/warnings rõ, video ≤5 phút, câu trả lời ba câu bắt buộc, repo public và phương án chạy thử. Không dùng kết quả thất bại làm dữ liệu đúng; khi demo live có thể sinh khác lượt lưu. Transcript dài chưa được chứng minh ổn định.

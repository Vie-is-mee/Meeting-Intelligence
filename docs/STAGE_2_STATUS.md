# Stage 2 — Lõi có kiểm tra phản chứng

**Trạng thái:** mã nguồn & các kiểm thử hợp đồng hoàn thành; **chưa xác minh hiệu quả LLM thật** vì chưa có cấu hình API model hợp lệ trong môi trường này.

## Thay đổi quan trọng

- Bổ sung `auditor.py`: lượt rà độc lập nhằm tìm sự kiện bị bỏ sót và lời phủ định đến sau.
- Audit phải đưa ra `source_ids`, nguyên văn `source_quote` và lý do. Python loại những cảnh báo viện dẫn không có thật.
- Nếu phát hiện rủi ro cao ở quyết định/công việc, kết luận chuyển `unverified`, con người phải xem lại, thay vì AI tự đưa ra kết luận mới.
- Khi audit API thất bại, bản ghi rủi ro cao được giữ để xác nhận (`fail-closed`); không ngầm coi dữ liệu đúng.
- Sửa quy tắc thời gian: có đề xuất mới *sau* lời chốt nhưng chưa rõ đã thay thế hay chưa thì đánh dấu `open`/cần xác nhận, không tự chọn câu cuối.
- API adapter hỗ trợ JSON mode bật/tắt theo nhà cung cấp, retries giới hạn cho lỗi tạm thời, thống kê lượt gọi/tokens khi provider có trả.
- Đã bổ sung kiểm thử giao thức API bằng **HTTP server giả chạy cục bộ**; không phải chạy một LLM thật.

## Bằng chứng thử nghiệm có thể tái lập

- `python -m unittest discover -s tests -v`: **23/23** bài kiểm thử đạt trên bản dựng lần đầu Stage 2.
- `python scripts/run_contract_fixtures.py`: **7/7** ca kiểm tra cơ chế phần mềm, nhưng sự kiện trích xuất là fixture **viết tay**. Không dùng chỉ số này để quảng bá chất lượng AI.
- Offline regex engine: T02/T03/T04 đạt; khi chạy cả 7 tình huống, mô-đun offline không hỗ trợ đầy đủ các nhóm khác.
- **0 ca có kết quả LLM API thật đã được xác minh trong môi trường này.** Khi có khóa, cần tạo `results/live_all.json` từ lần chạy thật rồi đọc và phân tích ca thất bại.

## Kiểm thử phải làm khi có provider

1. T02: A đề xuất, B chốt — không lấy A làm quyết định cuối.
2. T03: B chốt rồi mở lại — phải trả `reopened` hoặc giữ `unverified` để người xem xác nhận nếu extractor bỏ sót.
3. T04: B được chốt nhưng *chưa được triển khai* — không nhầm với mở lại quyết định.
4. T05: đổi Minh → Lan, hạn null — không tạo thêm ngày hoặc người phụ trách.
5. T01/T06/T07: bao phủ đa loại, phân biệt chủ đề xen kẽ và trả nguồn hợp lệ.

So sánh cùng dữ liệu/model với audit bật/tắt; không sửa đáp án để làm đẹp kết quả. Báo số lỗi tuyệt đối, thời gian, lượt gọi API và chi phí nếu có đơn giá thực tế.

## Chưa thực hiện

Giao diện UI, deploy online, thực nghiệm với LLM thật, video và GitHub repo public. Không tuyên bố đây là sản phẩm đã nộp Mission 2.

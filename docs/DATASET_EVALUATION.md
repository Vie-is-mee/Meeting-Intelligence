# Đánh giá dataset Mission 2

Dataset: `datasets/meeting_eval_v1.json`, annotation revision 1.1; 24 transcript tổng hợp, 16 development và 8 reserved/held_out. Đây không phải dữ liệu doanh nghiệp thật và chưa được người gán nhãn độc lập xác nhận.

## Quy trình tái lập

Chạy từ thư mục dự án, với Groq đã cấu hình trong `.env`:

```bat
"I:\Python\python.exe" -X utf8 scripts/run_dataset.py
```

Runner gọi pipeline thật, bật audit, chỉ truyền transcript vào model. Không truyền đáp án, checkpoints, forbidden claims hoặc tên split. Dataset và các module xử lý được lưu SHA-256; runner dừng nếu chúng thay đổi. Kết quả được ghi nguyên tử sau mỗi case tại `results/dataset_v1_run.json`. Chạy lại cùng lệnh sẽ bỏ qua các case đã ghi, kể cả case ERROR; muốn chạy lại phải dùng đường dẫn `--out` mới. Không âm thầm lựa chọn lần trả lời tốt nhất.

Mỗi đầu ra cần được đối chiếu ngữ nghĩa với transcript và đáp án. File review ghi ánh xạ một-một giữa nhãn và bản ghi thực tế, nhận xét cho mọi bản ghi phụ, từng trường đúng/sai và cảnh báo audit đúng/sai. Không dùng trùng từ để tự kết luận đúng. Review của lượt này do cùng trợ lý đọc nguồn thực hiện, cần người dùng kiểm tra lại, không phải đánh giá mù độc lập.

```bat
"I:\Python\python.exe" -X utf8 scripts/score_dataset.py
```

## Định nghĩa chỉ số

- **Pipeline completion:** số case trả được `AnalysisResult` / toàn bộ case. Pipeline có thể trả kết quả bị giữ do audit lỗi; vì vậy báo riêng audit completion.
- **Supported record precision:** số bản ghi có nội dung và trạng thái hiện tại phù hợp nguồn / số bản ghi được trả về đã rà soát. Bản ghi phụ đúng nguồn được chấp nhận dù ngoài đáp án. Bản ghi thiếu chi tiết được ghi nhận thêm qua chỉ số từng trường; sai không đồng nghĩa tất cả đều là bịa.
- **Required-record recall end-to-end:** số nhãn bắt buộc được nhận diện đúng chủ đề, loại và trạng thái cuối / tổng nhãn bắt buộc. Case lỗi hoặc bỏ sót vẫn nằm trong mẫu số. Đây là recall trên các mục đã gán nhãn, không phải mọi thông tin hữu ích có thể tồn tại.
- **Final-decision accuracy:** quyết định đúng nghĩa và trạng thái cuối / các quyết định đã ghép được. Cần đọc cùng recall để không bỏ qua quyết định thiếu.
- **Field accuracy:** người, người hỗ trợ, hạn gốc, hạn ISO, điều kiện, trạng thái họp và triển khai trên các bản ghi ghép được. Báo cả toàn bộ trường và trường có giá trị trong đáp án để tránh nhiều `null` làm điểm quá đẹp. Diễn đạt tương đương được chấp nhận sau khi đọc nguồn; không bắt buộc chuỗi giống hệt.
- **Evidence support accuracy:** nguồn được trích thực sự hỗ trợ các khẳng định hiện tại, có xét nguồn từng trường và thay đổi cuối cuộc họp; không chỉ kiểm tra ID có tồn tại.
- **Audit finding precision:** cảnh báo audit có mô tả lỗi thực sự / mọi cảnh báo audit được trả về. Không đánh đồng một audit không cảnh báo với việc đầu ra hoàn toàn đúng.
- **Correct abstention:** số transcript không có dữ liệu để trích mà hệ thống không tạo bản ghi / số transcript âm đã rà soát. H07 còn phải xem cảnh báo mất dữ liệu; không tạo bản ghi chưa đủ chứng minh đã xử lý tốt dữ liệu mất.

Không tính F1 chung vì đáp án có phạm vi một phần, còn precision chấp nhận các bản ghi phụ đúng nguồn. Trạng thái mở/điều kiện không tự động là sai, và cờ cần rà soát không tự động làm sai nội dung thành đúng. Không chấm checkpoints trung gian bằng đầu ra cuối; cần lượt đánh giá theo prefix riêng nếu muốn đo chính xác diễn biến từng mốc.

## Trạng thái lượt chạy

Đã chạy đủ 24 case bằng Groq thật: 20 có đầu ra, 4 lỗi HTTP 400. Đã đối chiếu 20 đầu ra với nguồn; case lỗi được tính riêng và làm giảm recall end-to-end. Không thay prompt, dataset hoặc sửa core giữa lượt này. Kết quả đầy đủ tại [DATASET_EVALUATION_RESULTS.md](DATASET_EVALUATION_RESULTS.md).

Artifact tổng hợp an toàn để kiểm tra nằm ở `docs/evaluation/dataset_v1_run.json`, `dataset_v1_review.json` và `dataset_v1_metrics.json`. Các tệp này chỉ chứa transcript tổng hợp, đầu ra, nhận xét và metadata; không chứa `.env` hay khóa API. Các lệnh trên sử dụng bản làm việc ở `results/`. Khi chạy một lượt mới, dùng `--out` mới và tạo review mới khớp SHA-256 của lượt đó; không tái sử dụng ánh xạ chỉ số bản ghi từ một lượt khác.

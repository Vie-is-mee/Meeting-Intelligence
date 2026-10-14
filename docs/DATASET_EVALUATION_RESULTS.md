# Kết quả đánh giá dataset Mission 2

Model: `openai/gpt-oss-120b`. Lượt chạy bắt đầu UTC: `2026-10-13T01:55:01.483480+00:00`. Audit bật; prompt và mã lõi giữ nguyên theo SHA-256 trong artifact.

Đây là đánh giá **toàn pipeline** (LLM trích xuất → resolver → verifier → LLM audit), không phải điểm của riêng model. Dữ liệu tổng hợp do cùng trợ lý tạo và rà soát; chưa có người gán nhãn độc lập xác nhận. Chỉ chạy một lượt chính; không chọn câu trả lời tốt nhất từ nhiều lượt.

| Chỉ số | Tất cả | Development | Reserved |
|---|---:|---:|---:|
| Hoàn thành pipeline | 20/24 (83.3%) | 13/16 (81.2%) | 7/8 (87.5%) |
| Hoàn thành audit | 20/24 (83.3%) | 13/16 (81.2%) | 7/8 (87.5%) |
| Precision bản ghi có căn cứ | 37/45 (82.2%) | 19/26 (73.1%) | 18/19 (94.7%) |
| Recall mục bắt buộc, gồm case lỗi | 23/57 (40.4%) | 13/39 (33.3%) | 10/18 (55.6%) |
| Recall mục bắt buộc, chỉ case có đầu ra | 23/31 (74.2%) | 13/21 (61.9%) | 10/10 (100.0%) |
| Đúng kết luận cuối / quyết định ghép được | 9/12 (75.0%) | 5/8 (62.5%) | 4/4 (100.0%) |
| Recall quyết định cuối, gồm mục thiếu | 9/20 (45.0%) | 5/14 (35.7%) | 4/6 (66.7%) |
| Bằng chứng hỗ trợ đúng | 37/45 (82.2%) | 19/26 (73.1%) | 18/19 (94.7%) |
| Precision cảnh báo audit | 2/10 (20.0%) | 2/9 (22.2%) | 0/1 (0.0%) |
| Ghi nhận cần rà soát | 14/29 (48.3%) | 9/18 (50.0%) | 5/11 (45.5%) |
| Không tạo bản ghi ở case âm | 2/2 (100.0%) | 1/1 (100.0%) | 1/1 (100.0%) |

## Độ chính xác từng trường trên bản ghi ghép được

| Trường | Tất cả giá trị, kể cả null | Chỉ nhãn có giá trị, đã ghép | Thu hồi trường có giá trị, gồm mục thiếu/lỗi |
|---|---:|---:|---:|
| meeting_status | 25/29 (86.2%) | 25/29 (86.2%) | 25/57 (43.9%) |
| execution_status | 28/29 (96.6%) | 28/29 (96.6%) | 28/57 (49.1%) |
| owner | 29/29 (100.0%) | 6/6 (100.0%) | 6/13 (46.2%) |
| supporter | 29/29 (100.0%) | 3/3 (100.0%) | 3/7 (42.9%) |
| due_raw | 28/29 (96.6%) | 3/4 (75.0%) | 3/9 (33.3%) |
| due_iso | 29/29 (100.0%) | N/A (mẫu số 0) | N/A (mẫu số 0) |
| condition | 26/29 (89.7%) | 0/2 (0.0%) | 0/4 (0.0%) |

Các trường bị bỏ sót cùng cả bản ghi không nằm trong mẫu số field accuracy; chúng làm giảm recall. `due_iso` toàn null không chứng minh năng lực chuẩn hóa ngày. Nhận xét đúng/sai từng trường đã xét diễn đạt tương đương, không so chuỗi máy móc.

## Theo loại thông tin

| Loại | Precision có căn cứ | Recall mục bắt buộc, gồm lỗi chạy |
|---|---:|---:|
| action | 6/7 (85.7%) | 6/14 (42.9%) |
| decision | 9/14 (64.3%) | 9/20 (45.0%) |
| feedback | 1/2 (50.0%) | 1/6 (16.7%) |
| issue | 8/8 (100.0%) | 2/7 (28.6%) |
| knowledge | 5/6 (83.3%) | 0/2 (0.0%) |
| request | 8/8 (100.0%) | 5/8 (62.5%) |

## Kỳ vọng → thực tế → đánh giá

Đạt yêu cầu nội dung khi đủ nhãn bắt buộc, đúng nghĩa/trạng thái/trường, nguồn hỗ trợ đúng và có xử lý rà soát cần thiết. Cảnh báo audit sai được báo riêng; bản ghi phụ đúng nguồn không làm case trượt.

| Case | Kỳ vọng | Thực tế | Đánh giá | Điều học được / nhận xét |
|---|---|---|---|---|
| D01 | Đổi lựa chọn hạ tầng và chốt phương án cuối; 2 mục | 1 bản ghi; 1/2 mục đúng nghĩa/trạng thái | Chưa đạt | Audit nhầm nội dung nhà cung cấp chưa chốt thành điều kiện quyết định lưu trữ. Thiếu: vendor. |
| D02 | Chốt rồi mở lại, không biến người được hỏi thành owner; 1 mục | 4 bản ghi; 0/1 mục đúng nghĩa/trạng thái | Chưa đạt | Audit yêu cầu xóa nội dung lịch sử dù withdrawal đã có; không chỉ ra chính xác reopen bị phân loại withdrawal. |
| D03 | Quyết định có hiệu lực trong họp nhưng chưa được triển khai; 2 mục | 2 bản ghi; 2/2 mục đúng nghĩa/trạng thái | Chưa đạt | Đúng agreed/blocked; condition thiếu việc pháp chế phê duyệt hợp đồng. Đúng vấn đề hợp đồng đang mở. |
| D04 | Thay điều kiện chốt mà không biến thành chốt vô điều kiện; 1 mục | 2 bản ghi; 0/1 mục đúng nghĩa/trạng thái | Chưa đạt | L003-L005 xác lập conditional/pending_condition với điều kiện mới; cả ba trường bị sai. |
| D05 | Đổi người phụ trách, giữ người hỗ trợ và bỏ deadline cũ; 1 mục | 1 bản ghi; 1/1 mục đúng nghĩa/trạng thái | Đạt | Đúng người phụ trách, hỗ trợ, hạn null sau khi rút thứ Sáu; giữ nguyên công việc. |
| D06 | Việc bị hủy không tự sống lại khi bỏ deadline; 1 mục | 1 bản ghi; 0/1 mục đúng nghĩa/trạng thái | Chưa đạt | Không có lời giao lại hay thay chủ việc; owner lịch sử được phép giữ khi công việc cancelled. Audit yêu cầu xóa owner không có căn cứ nghiệp vụ. |
| D07 | Chỉ chào hỏi và giả định, không có dữ liệu công việc; 0 mục | 0 bản ghi; 0/0 mục đúng nghĩa/trạng thái | Đạt | Đúng abstention: chỉ thử mic và giả định, không có mục công việc cần tái sử dụng. Audit đòi ghi quyết định kết thúc thử mic là nhiễu. |
| D08 | Công việc có thật nhưng không biết người nói hoặc deadline; 2 mục | 2 bản ghi; 1/2 mục đúng nghĩa/trạng thái | Chưa đạt | Audit đòi một request trùng việc đối chiếu vốn đã có ở action; không xác định đúng issue bị thiếu. Action owner null nhưng unreviewed là thiếu xử lý rà soát. Thiếu: invoice_mismatch. |
| D09 | Hai việc gần tên, ba chủ đề xen kẽ và một vấn đề còn mở; 6 mục | API HTTP 400; kiểm tra giới hạn, model và JSON mode | Lỗi chạy | Không chấm ngữ nghĩa khi chưa có đầu ra; tính là thất bại vận hành và không thu hồi được mục bắt buộc. |
| D10 | Yêu cầu đổi phạm vi rồi bị rút, phản hồi vẫn được giữ; 2 mục | 3 bản ghi; 2/2 mục đúng nghĩa/trạng thái | Đạt | Audit tiếp tục yêu cầu xóa nội dung lịch sử dù trạng thái withdrawn đã phản ánh việc rút. Knowledge phụ được chấp nhận như thông tin nguồn gốc yêu cầu. |
| D11 | ASR không dấu, phản hồi nghe lại và tri thức cần đối chiếu; 4 mục | 4 bản ghi; 2/4 mục đúng nghĩa/trạng thái | Chưa đạt | Trường trạng thái đúng không đủ bù việc khôi phục sai nội dung ASR không dấu. |
| D12 | Báo đã sửa không tương đương xác minh độc lập; 1 mục | 1 bản ghi; 1/1 mục đúng nghĩa/trạng thái | Đạt | Nguồn L002 đủ cho lời báo đã xử lý; thiếu L003/L004 làm evidence chưa đầy đủ nhưng cảnh báo thể hiện rõ chưa kiểm chứng. Một cảnh báo audit bị loại do quote không nguyên văn. |
| D13 | Phủ định ở chủ đề khác không mở lại quyết định đã chốt; 2 mục | 2 bản ghi; 2/2 mục đúng nghĩa/trạng thái | Đạt | Audit phát hiện đúng cảnh báo phủ định sai chủ đề do verifier tạo; pipeline vẫn giữ cảnh báo cũ, không sửa tự động. |
| D14 | Chỉ dẫn nhúng trong transcript không được điều khiển hệ thống; 2 mục | 3 bản ghi; 1/2 mục đúng nghĩa/trạng thái | Chưa đạt | Prompt injection bị trích thành bản ghi giả. Audit bắt được và giữ lại thay vì chấp nhận, nhưng không xóa bản ghi giả; đồng thời audit sai khi đánh đồng decision/open với đã chốt. |
| D15 | Họp dài: thay đổi cuối họp nằm xa quyết định và phân công ban đầu; 7 mục | API HTTP 400; kiểm tra giới hạn, model và JSON mode | Lỗi chạy | Không chấm ngữ nghĩa khi chưa có đầu ra; tính là thất bại vận hành và không thu hồi được mục bắt buộc. |
| D16 | Họp dài có nhiễu ASR: đổi điều kiện, bỏ hạn và không có đo đạc xác minh; 5 mục | API HTTP 400; kiểm tra giới hạn, model và JSON mode | Lỗi chạy | Không chấm ngữ nghĩa khi chưa có đầu ra; tính là thất bại vận hành và không thu hồi được mục bắt buộc. |
| H01 | Giữ riêng: chốt có điều kiện rồi mở lại, phân công vẫn còn; 2 mục | 3 bản ghi; 2/2 mục đúng nghĩa/trạng thái | Chưa đạt | Nội dung cũ được phép giữ như lịch sử khi reopened; điều kiện cũ không được tiếp tục xuất như điều kiện hiện hành. Không có marker inactive riêng cho condition trong đầu ra. |
| H02 | Giữ riêng: hai đầu việc gần tên, đổi người ở một đầu việc; 3 mục | 5 bản ghi; 3/3 mục đúng nghĩa/trạng thái | Đạt | Hai bản ghi knowledge phụ đúng nguồn được chấp nhận về grounding, không tăng recall. Nội dung action web nên viết lại rõ kiểm thử ở lượt cải thiện sau. |
| H03 | Giữ riêng: đại từ không rõ và hai hạn được nhắc nhưng chưa chọn; 2 mục | 3 bản ghi; 2/2 mục đúng nghĩa/trạng thái | Chưa đạt | Dùng biểu diễn hai nhãn chuẩn, không dùng alternative gộp. Issue assign_review hiển thị rõ cần kiểm tra người nhận nên chấp nhận xử lý rà soát request ở cùng case; hạn tương đối vẫn mất ở trường cấu trúc. |
| H04 | Giữ riêng: đọc lại quyết định cũ không biến thành kết luận hôm nay; 1 mục | 3 bản ghi; 1/1 mục đúng nghĩa/trạng thái | Đạt | Không tính 90 ngày thành due_raw. Ba cảnh báo audit bị loại do trích dẫn không nguyên văn, nên không nằm trong precision cảnh báo đã trả về. |
| H05 | Giữ riêng: câu hỏi và lời đề nghị chưa phải nhận việc; 1 mục | 4 bản ghi; 1/1 mục đúng nghĩa/trạng thái | Đạt | Audit đòi timeline/condition từ khả năng Bình rảnh tuần sau, trái L005. Bốn bản ghi có căn cứ nhưng còn phân mảnh/dư thừa; precision grounding không đo độ gọn. |
| H06 | Giữ riêng: đổi hạn hai lần, không suy ra tháng hoặc hạn ISO; 1 mục | 1 bản ghi; 1/1 mục đúng nghĩa/trạng thái | Đạt | Đúng công việc/Sơn/hạn cuối và source của hạn L005, due_iso null vì thiếu tháng năm. |
| H07 | Giữ riêng: mất tiếng ngay phần quan trọng, không thể khôi phục kết luận; 0 mục | 0 bản ghi; 0/0 mục đúng nghĩa/trạng thái | Chưa đạt | Không bịa bản ghi là đúng; nhưng chỉ có cảnh báo LLM chung, không nói transcript mất tiếng/không đủ dữ liệu. Thiếu xử lý case-level review bắt buộc. |
| H08 | Giữ riêng: họp dài, nhiều lần sửa và hai việc xuất dữ liệu gần giống; 8 mục | API HTTP 400; kiểm tra giới hạn, model và JSON mode | Lỗi chạy | Không chấm ngữ nghĩa khi chưa có đầu ra; tính là thất bại vận hành và không thu hồi được mục bắt buộc. |

Tổng theo tiêu chí trên: **9 đạt, 11 chưa đạt, 4 lỗi chạy**.

## Transcript dài và chi phí lượt chạy

| Độ dài | Hoàn thành pipeline | Recall mục bắt buộc |
|---|---:|---:|
| long_for_mvp | 0/3 (0.0%) | 0/20 (0.0%) |
| medium | 2/3 (66.7%) | 4/10 (40.0%) |
| short | 18/18 (100.0%) | 19/27 (70.4%) |

API attempts: **45** (gồm retry). Provider báo tổng **102,621 tokens** trên các response có usage; không suy ra token của request lỗi. Tổng thời gian các case **1987.2s**, median **89.7s/case**, gồm khoảng nghỉ chủ động 45s giữa API attempts. Đây không phải latency xử lý thuần của model.

## Lỗi ưu tiên xử lý

1. Lỗi HTTP 400 ở D09/D15/D16/H08; cả ba transcript dài đều chưa có đầu ra. Adapter hiện chỉ giữ mã lỗi, chưa đủ xác định nguyên nhân từ provider. Không kết luận rằng model không hiểu transcript dài từ mã HTTP này.
2. Audit có nhiều false positive: nhầm nội dung lịch sử bị hủy/rút với thông tin còn hiệu lực, hoặc coi decision/open là đã chốt. D02/D06/D14 bị ghi đè trạng thái đúng/đáng lẽ rõ ràng thành unverified.
3. D04 giữ điều kiện 500 dù cuối họp sửa thành 300; D03 thiếu chi tiết pháp chế; H01 điều kiện lịch sử còn ở trường hiện tại; H03 mất due_raw tương đối.
4. D14 vẫn tạo bản ghi từ chuỗi prompt injection, dù audit đã giữ để rà soát. D11 diễn đạt sai nội dung không dấu. D01/D08 thiếu mục bắt buộc.
5. H07 không bịa dữ kiện khi mất tiếng, nhưng chưa thông báo rõ không đủ dữ liệu. D08 công việc thiếu người chưa được giữ để rà soát. Một số đầu ra còn phân mảnh/dư thừa.

## Giới hạn và cách sử dụng kết quả

- Precision chấp nhận bản ghi phụ đúng nguồn; recall chỉ trên nhãn bắt buộc. Không ghép chúng thành F1 vì phạm vi gold chưa đầy đủ.
- `unverified` giúp giữ bản ghi để người kiểm tra, nhưng không được tính là đã hiểu đúng một trạng thái cụ thể như reopened/cancelled. Một bản ghi giả vẫn sai dù đã gắn cờ.
- Reserved đã được dùng trong lượt này; sau khi dùng lỗi ở đây để chỉnh hệ thống, cần một tập reserved mới để kiểm chứng độc lập.
- Không kiểm thử riêng prefix từng checkpoint, độ ổn định qua nhiều lần chạy, hoặc transcript nhiều giờ. Các chỉ số này không chứng minh hệ thống đúng mọi trường hợp.

Định nghĩa và lệnh chạy: [DATASET_EVALUATION.md](DATASET_EVALUATION.md). Đầu ra, review và metric máy đọc được ở `results/dataset_v1_*.json`; bản tổng hợp an toàn để review nằm trong `docs/evaluation/` nếu được lưu cùng bài nộp.

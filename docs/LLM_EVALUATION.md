# Kiểm thử Groq thật — bộ phát triển T01–T07

Ngày chạy: 12–13/10/2026 (ICT). Transcript đều là dữ liệu tổng hợp trong `samples/`.
Model của lượt chạy lại: `openai/gpt-oss-120b`; extraction và audit dùng cùng
model, hai prompt khác nhau. Audit là lượt phản biện thứ hai, không phải
kiểm chứng bởi con người hoặc một model độc lập.

## Cách đọc kết quả

`PASS` nghĩa là khớp các trường mà đáp án hiện có kiểm tra, không chứng minh
mọi nội dung đều đúng. `FAIL` là không khớp đáp án; phải đọc nguồn để biết
đó là lỗi sản phẩm, cảnh báo audit nhầm, hay bản ghi thêm có căn cứ.
`ERROR` là không hoàn thành trích xuất, chẳng hạn API trả HTTP 429.
Audit lỗi có thể khiến một ca thành `FAIL`: pipeline giữ quyết định/công việc
ở `unverified`, thay vì công bố là đã được rà soát.

Các ca này đã được dùng để sửa prompt/code, **không phải tập kiểm thử độc lập**.
Không dùng tỷ lệ đạt của bộ này làm ước lượng độ chính xác ngoài thực tế.

## Lượt đầu, trước các sửa đổi trong đợt này

Nguồn: [JSON lượt đầu](evaluation/groq_dev_initial.json).

| Ca | Kỳ vọng | Kết quả thực tế | Đạt/Chưa đạt | Điều học được |
| --- | --- | --- | --- | --- |
| T01 | Đủ 6 bản ghi thuộc các nhóm chính; Lan làm, Minh hỗ trợ | Khớp 6 kỳ vọng; audit lại đòi gán người yêu cầu thành owner | PASS bộ chấm; audit có cảnh báo sai | Người đưa yêu cầu không mặc nhiên là người thực hiện. PASS không đồng nghĩa không có lỗi audit. |
| T02 | Đề xuất A → chuyển B → chốt B | Kết luận B, nguồn L004; audit báo thiếu lý do chi phí ở L002 | PASS bộ chấm | Lưu kết luận đúng vẫn có thể thiếu lý do; audit không tự thêm bản ghi. |
| T03 | B từng được chốt nhưng cuối cùng mở lại | Trích xuất không hoàn thành: HTTP 429 | ERROR | Không được coi lỗi hạn mức API là lỗi hiểu transcript. |
| T04 | Đã chốt B nhưng chặn triển khai | Trích xuất đúng chuỗi chốt/chặn; audit HTTP 429 nên trạng thái bị giữ `unverified` | FAIL do audit không hoàn tất | Cần giãn nhịp API; không bỏ cơ chế giữ để kiểm tra nhằm làm đẹp điểm. |
| T05 | Đổi Minh → Lan, Minh hỗ trợ, không tự đặt hạn | Owner/supporter đúng; nội dung công việc null; audit báo thiếu thay đổi dù events đã có; thêm issue chưa có hạn | FAIL | Audit phải hiểu events là lịch sử. Chỉ có tên chủ đề/người làm chưa đủ thành bản ghi hữu ích. |
| T06 | Tách giao diện, quyền máy chủ, công việc và phản hồi menu | 4 bản ghi đúng nhóm, nhưng phản hồi và một số bản ghi khác có content null | FAIL thực sự | Nguồn và trạng thái hợp lệ vẫn chưa đủ nếu mất nội dung cần dùng sau họp. |
| T07 | Phản hồi/yêu cầu/VPN/tri thức chưa xác minh/cách tính ngày chưa chốt | Trích xuất không hoàn thành: HTTP 429 | ERROR | Cần chạy được bằng API thật trước khi kết luận model không xử lý được. |

Tổng theo bộ chấm tại thời điểm chạy: **2 PASS, 3 FAIL, 2 ERROR**.
Bộ chấm ban đầu chưa bắt mọi `content=null`; đã bổ sung kiểm tra nội dung
không rỗng sau khi đọc đầu ra. Không sửa lại điểm lịch sử để che thay đổi này.

## Các sửa đổi từ bằng chứng quan sát được

- Prompt extraction yêu cầu nội dung sự kiện có nghĩa, phân biệt owner với
  người yêu cầu và không tạo assignment trùng reassignment cùng câu.
- Extraction từ chối nhóm sự kiện hoàn toàn thiếu nội dung. Một sự kiện
  mở lại không có value vẫn hợp lệ nếu nhóm đã có nội dung lịch sử.
- Prompt audit giải thích events là lịch sử, records là trạng thái cuối,
  và content của quyết định mở lại có thể giữ phương án lịch sử.
- Sửa resolver: reopen/withdrawal/execution_blocked không ghi đè nguồn
  của content khi chúng không thực sự thay nội dung được lưu.
- T04 lượt xác nhận tiếp tục phát hiện nguồn meeting_status bị ghi đè
  bởi execution_blocked. Đã tách nguồn trạng thái chốt khỏi trạng thái triển
  khai và bổ sung nguồn condition. Sửa đổi này được kiểm thử bằng code và
  replay sự kiện đã lưu; không coi là audit LLM đã được chạy lại sau sửa.
- Sửa deadline_change: chỉ đổi hạn, không thay mô tả công việc bằng câu
  về deadline, không đổi nguồn của trạng thái phân công và không tự kích
  hoạt lại công việc đã hủy. Lỗi này được audit phát hiện đúng ở T05 lượt lại.
- Audit ghi chi tiết trường sai schema, chỉ cho severity high/medium trong
  prompt; runner lưu JSON mà model trả để có thể chẩn đoán lỗi schema.
- Runner có `--call-interval`, áp dụng cả giữa các ca và các lần thử lại;
  lưu báo cáo sau từng ca, ghi model, số call và token cả khi lỗi.
- Bộ chấm không cho bản ghi thiếu content đạt chỉ nhờ đúng loại/nguồn/trạng thái.

## Chạy lại

Lượt giãn nhịp bắt đầu trước khi sửa resolver về reopen và deadline_change.
Không coi các sửa đổi trong lúc lượt đó đang chạy là đã có hiệu lực trong
process cũ. Các ca bị ảnh hưởng được chạy lại ở process mới để xác nhận.
Nguồn: [JSON lượt giãn nhịp](evaluation/groq_dev_retest.json).

| Ca | Kết quả quan sát ở lượt giãn nhịp | Nhận xét khi đọc bằng chứng |
| --- | --- | --- |
| T07 | Đủ 5 kỳ vọng, thêm `issue/loc_ngay` nguồn L003; strict FAIL | “Chưa rõ ngày tạo hay ngày cập nhật” là vướng mắc có thật. Đây là khác biệt mức độ tách bản ghi, không phải thông tin bịa. Không đổi đáp án để biến lượt này thành PASS. |
| T03 | Audit giữ `unverified` thay vì `reopened` | Nguồn content bị resolver gán sai sang L003; đồng thời audit hiểu content lịch sử như kết luận hiện hành. Đã sửa provenance và giải thích hợp đồng trong prompt. |
| T04 | `unverified`, execution `blocked`; audit sai schema | Không tự bỏ qua kiểm tra schema để lấy điểm. Bổ sung chẩn đoán và enum rõ trong prompt; cần xác nhận bằng lượt mới. |
| T05 | Owner Lan/supporter Minh đúng nhưng content thành “chưa có ngày hoàn thành cụ thể” | Audit bắt đúng: sự kiện deadline_change đã ghi đè mô tả việc. Đây là lỗi code cần sửa, không phải audit nhầm như lượt đầu. |
| T06 | Nhầm feedback → knowledge; issue còn mở → decision mới | Lỗi phân loại thật. Bổ sung định nghĩa nhóm và cách nối diễn biến của một vấn đề. |
| T01 | PASS bộ chấm | Không suy rộng thành độ chính xác ngoài bộ phát triển. |
| T02 | PASS bộ chấm; audit không phát hiện vấn đề | Kết luận B giữ đúng nguồn L004. |

Tổng lượt giãn nhịp: **2 PASS, 5 FAIL, 0 ERROR**, 14 API call thành công,
34.539 token theo usage provider. Không ghi nhận HTTP 429 trong lượt này.
Đây là kết quả trước các sửa resolver/phân loại cuối đợt; không dùng để
khẳng định phiên bản mới đã đạt cả bộ.

### Xác nhận sau sửa: T03–T06

Nguồn: [JSON xác nhận](evaluation/groq_fix_confirmation.json), gồm phản hồi
JSON thực tế của extraction/audit và mã SHA-256 hai prompt trong lượt chạy.

| Ca | Kỳ vọng | Kết quả thực tế | Đạt/Chưa đạt | Điều học được |
| --- | --- | --- | --- | --- |
| T03 | Kết luận B đã mở lại, không coi B là quyết định cuối | `reopened`, content lịch sử nguồn L002; audit còn cảnh báo medium về nguồn ngữ cảnh L002 trong sự kiện mở lại | PASS kỳ vọng; vẫn cần xem cảnh báo | Nguồn ngữ cảnh khác với nguồn phát sinh sự kiện. Quote đúng không bảo đảm lời phản biện đúng. |
| T04 | Chốt B nhưng chặn triển khai | `agreed` + `blocked`; audit medium phát hiện lỗi provenance trạng thái | PASS kỳ vọng kết luận; provenance được sửa sau lượt này | Bộ chấm không bao phủ mọi trường. Cần đọc audit ngay cả khi PASS. |
| T05 | Lan làm, Minh hỗ trợ; hạn null; giữ việc kiểm thử | `assigned`, content “kiểm thử B”, owner Lan/supporter Minh/due_raw null; audit rỗng | PASS | Không dùng sự kiện đổi hạn để thay nội dung công việc. |
| T06 | B chốt cuối; issue máy chủ còn mở; Hương xử lý; phản hồi menu | Đủ 4 bản ghi, đúng loại, đúng nguồn L006/L007/L004/L005; audit rỗng | PASS | Định nghĩa rõ feedback/knowledge và diễn biến issue giúp tránh tách sai chủ đề. |

Tổng lượt xác nhận: **4 PASS, 0 FAIL, 0 ERROR**. Đây là bốn ca chạy lại,
không phải kết quả 7/7 trên cùng một phiên bản. T01/T02 đạt ở lượt trước;
T07 vẫn strict FAIL vì có thêm bản ghi được hỗ trợ bởi L003.

Sau lượt xác nhận, đã sửa riêng provenance T04: nguồn `meeting_status` là
câu chốt, còn nguồn `execution_status` là câu chặn triển khai. Kiểm chứng:
**61/61 kiểm thử phần mềm**, **7/7 fixture thủ công**, và replay extraction
thực tế T03–T06 qua resolver/verifier hiện tại đều đạt. Replay này không
gọi lại extraction/audit, không phải thêm bốn ca LLM mới.

```text
python -X utf8 scripts/replay_resolver.py docs/evaluation/groq_fix_confirmation.json --out results/resolver_replay.json
```

Xem [JSON replay](evaluation/resolver_replay.json) để kiểm tra provenance
sau sửa. Không tính lượt replay vào số lần gọi API hoặc độ chính xác model.

```text
python -X utf8 scripts/run_scenarios.py --engine llm_api --ids T01 T02 T03 T04 T05 T06 T07 --audit on --call-interval 45 --out results/groq_dev_retest.json
```

Giãn 45 giây giữa các lần gọi giúp giảm tốc độ tiêu thụ token, không bảo đảm
tránh mọi giới hạn tài khoản. Không chạy thêm phân tích từ UI song song nếu
muốn đo lượt này riêng. Thời gian trong báo cáo có cả thời gian chờ giãn nhịp.

Chưa thực hiện ở bước này: tập mới gán nhãn trước khi chạy model, so sánh
baseline trích xuất trực tiếp với pipeline, đo nhiều lượt để kiểm tra độ ổn định.

## Hạn chế còn phải đo

- Phân biệt phản hồi, tri thức, vấn đề còn tồn tại và lựa chọn chưa chốt còn
  phụ thuộc cách model diễn giải. Schema hợp lệ không chứng minh phân loại đúng.
- Audit có thể bắt đúng lỗi như T05, cũng có thể tạo cảnh báo sai như lượt
  đầu T01/T05. Trích dẫn đúng nguyên văn chỉ chứng minh câu tồn tại, không
  chứng minh diễn giải của audit đúng.
- Bản ghi thêm có căn cứ như T07 cần được đánh giá khác với bản ghi bịa.
  Bộ chấm số lượng nghiêm ngặt hiện chưa thể hiện hết khác biệt này.
- Trường owner/supporter/due_raw được kiểm tra theo nguồn cập nhật riêng;
  kiểm tra từ vựng không chứng minh quan hệ người–việc đúng trong mọi cách nói.
- Không tự điền hạn/người còn thiếu, không để audit tự viết lại quyết định,
  không thay API lỗi bằng kết quả giả. Các cơ chế này giảm rủi ro nhưng vẫn
  cần người đọc nguồn trước khi đưa dữ liệu vào quy trình công việc.

Bước kế tiếp sau đợt sửa này là đóng băng phiên bản để đo trên tập mới được
gán nhãn trước khi chạy, gồm câu phủ định ở chủ đề khác, thay đổi điều kiện,
đổi hạn, hủy việc, lời nói gián tiếp và transcript mơ hồ. Không dùng thêm
tính năng giao diện để thay cho việc đo chất lượng lõi này.

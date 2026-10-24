# Mission 3 — Final submission pack / 24 October 2026

**Hard deadline:** 18:00, 24/10/2026 ICT. Aim to submit before 17:00. Do not change the M2 main/tag/deployment.

## Three links

**GitHub M3:** https://github.com/Vie-is-mee/Meeting-Intelligence/tree/mission3/improvement-20261021

**Public M3 demo:** https://meeting-intelligence-m3.vercel.app/

**Video ≤5 minutes:** [PENDING — record/upload and replace with actual public URL. Never invent a video link.]

Deployment evidence:
- Render M3 `https://meeting-intelligence-m3-staging.onrender.com/api/version` returned `mission=M3`, `change_request=C2`, `source_commit=6d3712aa52c118bd513a602d28c48378bfa501e5`, and correct core SHA fingerprints.
- Render source-attested live C2 smoke succeeded with real Groq; see `docs/evaluation/mission3/m3_stage6_public_smoke_6d3712a_v1.json`.
- Vercel M3 GET `/` and `/config.js` HTTP 200; UI has Mission 3 + C2 picker, API_BASE_URL points to Render M3.
- `273/273` Python, `13/13` Node review/export tests PASS. Browser *manual click-through* is pending; do not claim performed.
- M2 main remains `439f672`; its Render/Vercel services were not edited.

## Script for narrated video — 4:30–4:45, no unsupported claims

### 00:00–00:30 | The real problem
[M2 screenshot and one sentence of ambiguous assignment on the left]
"Ở Mission 2, ứng dụng biến lời họp thành bản ghi quyết định, nhiệm vụ và bằng chứng. Nhưng một bản ghi có cấu trúc không tự nhiên đồng nghĩa với một cam kết đúng. Chỉ cần hiểu nhầm người phụ trách hoặc thời hạn, đầu ra có thể gây hành động sai."

### 00:30–01:10 | Requirement and deliberate choice
[Show C2 source sentence + architecture / pipeline diagram]
"Change Request C2 nói 'cái này team mình xử lý nhé'. Không có cá nhân nào nhận việc, không có deadline. Nhóm không xây lại hệ thống hay đổi model để gây ấn tượng. Chúng tôi ưu tiên source-grounded reliability: trích xuất event theo nguồn, theo dõi sự thay đổi xuyên suốt, kiểm tra quyết định và công việc trước khi cho xuất bản ghi đã xác nhận."

### 01:10–02:05 | Live C2 01 → C2 03
[Open `https://meeting-intelligence-m3.vercel.app/`; select C2-01, engine LLM API, audit on, Analyze. Show records and evidence L001; then load C2-03 and Analyze or show **previous Groq raw result** with an explicit label when calls take longer.]
"Với C2-01, kết quả là action/unverified, owner và deadline trống, nguồn L001, cần con người làm rõ. Khi một lượt nói sau cho biết Huy thực sự nhận xử lý lỗi thanh toán trước thứ Sáu, hệ thống có thể lưu action/assigned của Huy và đúng mốc 'trước thứ Sáu', không cần tạo thêm nhiệm vụ tập thể."

### 02:05–02:50 | Beyond C2: chronological reasoning
[Show D01, D04, H03/LC04 outputs and source citations.]
"D01 cho thấy hai quyết định độc lập: chốt object storage cho bản thử nghiệm nhưng nhà cung cấp vẫn chưa chọn. D04 giữ đồng thời điều kiện tải 300 người và không có lỗi nghiêm trọng. Với một nhiệm vụ đã hủy, hạn phải được xóa nhưng người phụ trách trong lịch sử vẫn được giữ để truy vết."

### 02:50–03:30 | Human review and safe export
[Select an unverified record, open evidence, mark insufficient, show confirmed-only CSV or screenshot; never show a secret.]
"Câu nguồn giúp truy vết, không tự chứng minh diễn giải luôn đúng. Những mục còn mơ hồ cần rà soát. Khi người dùng đánh dấu chưa đủ bằng chứng, chúng không được đưa vào CSV như những phân công đã được duyệt. JSON giữ dữ liệu gốc và lịch sử rà soát."

### 03:30–04:10 | Actual evidence and traceable improvements
[Show GitHub commit history + `docs/MISSION3_STAGE5_FINAL_SCORECARD_20261024.md`, raw JSON.]
"Nhóm đã giữ commit history từ M2 sang M3, viết thêm unit test, replay cả lỗi Groq cũ lẫn chạy Groq thật. Trên sáu ca đã khóa gồm bốn C2, D01 và D04, tất cả hoàn tất audit và đạt sáu nhóm ràng buộc quan trọng. 273 bài test Python và 13 bài frontend đạt. Tuy vậy C2-01/02 còn một cảnh báo audit mỗi ca, không thể nói mô hình đúng tuyệt đối."

### 04:10–04:40 | Honest limitations and next move
[Show 2 stress cases LONG01/LONG02 and final line.]
"Đánh giá cuộc họp dài phát hiện trường hợp tạm dừng công việc và chọn nhà cung cấp còn xử lý chưa tốt. Tiếp theo, chúng tôi sẽ đánh giá bằng transcript thật có nhãn độc lập, đo cả false-owner, false-deadline lẫn recall công việc đúng, và tiếp tục bắt buộc human review đối với mục có rủi ro cao. Mission 3 không thay thế quyết định của con người; nó giúp đầu ra có trách nhiệm hơn."

**Recording rules:** maximum five minutes. Screen-record final M3 live URL and show `/api/version`. If Groq takes too long, use archived Groq results and label them explicitly rather than pretending they are fresh. Hide API keys and all private env settings. Upload then test access using incognito before submitting.

## Mandatory answer 1 — priorities and deliberate non-goals

"Tôi ưu tiên chất lượng và độ tin cậy của bản ghi quyết định/công việc, trước hết là CR C2. Câu 'cái này team mình xử lý nhé' chỉ thể hiện ý định tập thể; M3 giữ action/unverified, không tự điền cá nhân hay deadline và dẫn về lời nói gốc để người dùng kiểm chứng. Tôi cải tiến thêm việc liên kết các event cùng đối tượng theo thời gian, tách quyết định độc lập, chống trùng bản ghi và kiểm tra lời đề xuất hạn chưa được chốt. Tôi chủ động không viết lại M2, không thêm agent mới, fine-tune hay hệ tự tạo lịch nhắc việc, vì chúng tăng rủi ro mà chưa giải quyết lỗi trích xuất có thể gây giao sai trách nhiệm."

## Mandatory answer 2 — biggest improvement with real numbers

"Khác biệt quan trọng nhất là từ 'trích xuất câu có cấu trúc' sang 'chỉ công nhận cam kết khi trạng thái cuối và evidence hỗ trợ'. Tôi giữ baseline M2, tạo các commit Stage 1A–5 và khóa dữ liệu để chạy Groq thật. Trên 6 ca được chỉ định gồm 4 C2, D01, D04, **6/6 lượt provider và audit hoàn tất, 6/6 nhóm điều kiện kiểm thử rõ ràng đạt**, với source/core SHA được lưu trong raw JSON. C2-01 giữ owner/deadline rỗng; C2-03 xác nhận Huy và hạn nguyên văn 'trước thứ Sáu'; C2-04 giữ trạng thái cancelled và xóa hạn; D01 tách object storage đã chốt và lựa chọn nhà cung cấp chưa chốt; D04 giữ hai điều kiện phát hành. Test phần mềm đạt 273/273 Python và 13/13 frontend. Tôi không đồng nhất test PASS với accuracy: C2-01/02 vẫn còn mỗi ca 1 audit finding; stress test nhiều chủ đề vẫn lộ lỗi bỏ sót và quản lý tạm dừng công việc, và bộ dữ liệu hiện chủ yếu tổng hợp chưa có nhãn độc lập."

## Mandatory answer 3 — biggest remaining risk and mitigation

"Rủi ro lớn nhất là AI có thể tạo bản ghi hợp hình thức và dẫn đúng dòng nguồn nhưng hiểu sai quan hệ giữa các chủ đề hoặc trạng thái cuối, đặc biệt cuộc họp dài, nhiều lượt sửa ý kiến, đại từ không rõ, các câu hỏi đề xuất hoặc nhiệm vụ bị tạm dừng. Kiểm thử LONG01/LONG02 đã bộc lộ trường hợp chưa theo được trạng thái tạm dừng và một quyết định còn mở bị bỏ sót. Vì vậy tôi ưu tiên quy trình human-in-the-loop: bản ghi chưa rõ không tự chuyển thành cam kết chính thức, các sửa đổi cần nguồn và lịch sử. Bước nghiên cứu tiếp theo là bộ transcript thực có nhãn bởi người độc lập; đo false owner/deadline, precision/recall của từng loại record và tính faithfulness của evidence theo từng trường trước khi tích hợp quản trị công việc tự động."

## Final checklist

- [x] M3 same-repo branch, commit history preserved. M2 main unchanged.
- [x] Four official C2 cases plus regression and edge cases, updated tests in repo.
- [x] Six source-matched focused Groq cases with reproducible scorecard; plus full regression and long stress logs with failures retained.
- [x] Both Render M3 and Vercel M3 deployed on release candidate.
- [x] Real Groq C2 HTTP smoke and SHA attestation passed.
- [ ] Manually click-through *review / insufficient evidence / export CSV / JSON* on real M3 website.
- [ ] Record/upload ≤5-minute video, verify real URL in incognito.
- [ ] Submit three URLs and three answers before 18:00, retain confirmation.

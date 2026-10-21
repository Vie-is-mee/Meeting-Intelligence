# Mission 3 — Stage 3.5 — Fresh Groq run 4 (frozen)

**Ngày:** 22/10/2026 ICT. **Nguồn M3 lúc chạy:** `c443647f9a05eb967437544be9bc588d0f85a3a5`. Đây là kết quả Groq thật, không phải archived replay; bốn case synthetic development đã biết trước. Review nội bộ, chưa chấm độc lập.

## Điều kiện thực nghiệm
- Model `openai/gpt-oss-120b`, temperature 0.6, reasoning low, 2.560 token budget extraction, audit bật, 0 retry.
- Frozen input/labels giữ nguyên Stage 0.5. Provider: **4/4 COMPLETED**, **8 API calls**, **19.064 tokens**; **0 HTTP error**.
- Raw đã lưu `m3_fresh_E01_run4.json`, `m3_fresh_E02_run4.json`, `m3_fresh_R01_run4.json`, `m3_fresh_K01_run4.json`, strict merge `m3_fresh_full_run4.json`, manual packet `m3_fresh_manual_review_packet_run4.md`. Không chép kết quả từ nhiều commit để tăng điểm.

## Case results

| Ca | Quan sát thật | Đánh giá nội bộ tạm thời |
|---|---|---|
| E01 | 3 records đúng: CSV request, Lan action cancelled, alternative decision open. **1 finding high-severity unsupported_fact** về nguồn owner L002 vs câu chấp nhận L003 | Core required 2/2; **NOT full PASS** khi chưa xử lý audit finding |
| E02 | 1 cancelled action, owner Lan lịch sử, no spurious request; audit empty | Core 1/1, full PASS |
| R01 | B agreed+blocked, vendor open, `condition=null` không còn field-source sai; audit empty | Core 2/2, full PASS |
| K01 | Assigned load test + Friday due, idempotency reusable candidate/unverified, library speed rumor needs verification, choice open; audit empty | Strict required 2/3: gold `recorded` vs safer `unverified` for knowledge; không gọi strict full PASS |

**Bộ bốn case, đánh giá nội bộ sơ bộ:** 4/4 running, 7/8 strict required, 3/4 core cases, **2/4 full cases**. Đừng gộp với runs 1–3 thành một run tốt nhất. Không suy ra generalization từ development cases.

## E01 — phân tích lỗi mới và hướng sửa hẹp
L002 nguyên văn: “Giao Lan thử thư viện X để làm tính năng xuất CSV”; L003 speaker Lan: “Tôi nhận việc thử thư viện X.” Record action `cancelled` và `field_evidence_ids.owner=['L002']` là căn cứ hợp lý cho **người từng được giao**. Auditor nhận định nguồn L002 “only assigns the task” không thể chứng minh assignee vì L003 mới nhận là cảnh báo không phù hợp ở ngữ cảnh này. Không nên tắt toàn bộ `unsupported_fact`; bộ lọc mới chỉ được xét khi có named assignment + same-owner first-person acceptance + cancelled history, và phải có negative test người từ chối hoặc owner sai.

Sau lượt run4, code sửa hẹp được phát triển **riêng** ở `meeting_intelligence/auditor.py` cùng tests, không có hiệu lực hồi tố với source `c443647`. Kết quả replay + 219 Python tests đạt nhưng **không thay thế fresh model run**.

## Go/No-Go
**NO-GO production**: kết quả mới trên source sửa audit chưa có, các ca D01/D03/D04/H01 chưa được chạy fresh bằng candidate này và CR official chưa được chứng minh đã hoàn thành. Chỉ được công bố các metric có mẫu số/ràng buộc như trên.

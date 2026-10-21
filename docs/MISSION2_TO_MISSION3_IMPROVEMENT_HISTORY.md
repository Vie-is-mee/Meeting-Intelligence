# NHẬT KÝ NGHIÊN CỨU MEETING INTELLIGENCE: TỪ MISSION 2 ĐẾN MISSION 3

> **Mục đích:** Đọc lại để hiểu **mình đã xây dựng gì → đo như thế nào → sai ở đâu → đặt giả thuyết sửa ra sao → thử nghiệm gì → kết quả thành công/thất bại gì → tại sao chọn hướng tiếp theo**. Dùng để ôn kỹ thuật và chuẩn bị thuyết trình/phỏng vấn.
>
> **Mốc ghi nhận:** 21/10/2026, sau Mission 3 Stage 3 (commit `4a91ca5`). Đây là **lịch sử hiện trạng tại mốc đó**, không phải tuyên bố mọi yêu cầu Mission 3 đã hoàn thành.
>
> **Phân biệt thuật ngữ:** *Mission 2* = sản phẩm đã nộp; *Stage 2 của Mission 3* = giai đoạn Evidence Validation & Missing Information Recovery. Hai khái niệm khác nhau.
>
> **Thang bằng chứng:** **[A] API/LLM thật**; **[B] Replay deterministic trên sự kiện LLM đã lưu**; **[C] Unit, contract, UI test**; **[D] Kế hoạch/chưa thử**; **[R] Phân tích nguyên nhân hoặc bài học suy ra từ kết quả**. Không được lấy [B/C] thành “accuracy LLM mới”.

## MỤC LỤC

1. Bức tranh nhanh và timeline
2. M2 mạnh về kiến trúc/năng lực nào?
3. Đánh giá M2: số liệu 24 ca và từng nhóm lỗi
4. Nhật ký 24 trường hợp M2
5. Hồi quy cuối M2: 8 ca và tiêu chí giữ A
6. Các thử nghiệm B1/B2/C1/C2/Raw: vì sao không chọn?
7. Chuyển tư duy từ M2 sang M3
8. Các Stage 0, 0.5, 1, 2, 3: kỹ thuật, thử nghiệm, kết quả
9. Ma trận điểm yếu → Stage xử lý → bằng chứng → rủi ro còn lại
10. Before/After chi tiết từng ca
11. Các việc còn lại & cổng Go/No-Go trước release
12. Bài học nền tảng, câu hỏi ôn tập, phỏng vấn
13. Nguồn chứng cứ, Git và quy tắc cập nhật nhật ký

---

## 1. BỨC TRANH NHANH VÀ TIMELINE

| Mốc | Việc làm | Kết quả quan sát | Học được gì / quyết định |
|---|---|---|---|
| M2 thiết kế | Pipeline Parser → LLM Extractor → Temporal Resolver → Verifier → LLM Auditor → Human Review/Export | Có web sản phẩm, schema + evidence + history | Không phá kiến trúc tốt để làm M3 từ đầu |
| **13/10** đánh giá dataset M2 | 24 transcript tổng hợp, dùng `openai/gpt-oss-120b` | [A] 20/24 hoàn tất, 9 đạt nội dung, 11 chưa đạt, 4 lỗi API; recall 23/57; audit precision 2/10 | Lỗ hổng là **quality/reliability**, không chỉ UX |
| **14/10** M2 baseline A | Một lượt hồi quy cố định 8 ca | [A] 8/8 completed, 5/8 core pass, 4/8 full pass | D01/D03/D04/H01 là bốn bài regression phải giữ |
| **14/10** M2 candidate B/C | Thử prompt và source/task/audit guards | [A] Có case sửa tốt nhưng gây lỗi D01/H01 hoặc audit sai; không vượt gate | Giữ A, chuyển từ “prompt rộng” sang sửa hẹp đúng nguyên nhân |
| **15/10** chốt M2 | Tag source nộp | `submission-a-ui-v2-20261015` → `439f672` | Giữ version nộp để có Before tái lập |
| **21/10** M3 Stage 0 | Định nghĩa mục tiêu/test/gates trước khi sửa | [C] 124 Python tests; tài liệu + fixtures | Không thay đáp án theo output |
| M3 Stage 0.5 | Worktree M2, frozen test/labels và chạy 4 Before case | [A] 4/4 API completed; review nội bộ 3/4 core và 1/4 full; 8 calls | Lưu raw output có nguồn, không dựa vào ký ức |
| M3 Stage 1 | Lifecycle / false commitments / issue-scoped negation / audit guard | [B/C] 147 Python tests; LC01, LC03, E01, R01 cải thiện khi replay | Sửa guard bằng chứng thay vì tắt cảnh báo hàng loạt |
| M3 Stage 2 | Source-anchored omission recovery + evidence theo field | [B/C] 174 Python tests; H03, LC02 được khôi phục khi replay | Không được tự tạo owner/action/approved decision |
| M3 Stage 3 | Phân loại thông tin công việc/tri thức/lịch sử/chưa xác minh | [B/C] 197 Python + 13 frontend tests; K01 có utility đúng ở replay | Candidate knowledge vẫn phải review |
| Tiếp theo | Fresh LLM M3, long/raw/ASR, Change Request, release | **[D] Chưa hoàn thành** | Không merge M3 trước khi đánh giá end-to-end |

### Một câu tóm lược

**M2 có kiến trúc theo dõi diễn biến cuộc họp khá tốt nhưng pipeline còn bỏ sót, ghi cam kết thừa và báo audit sai. M3 Stage 1–3 đã sửa những cơ chế đó ở tầng code và replay; chưa chứng minh kết quả LLM end-to-end mới đã vượt M2.**

---

## 2. M2 MẠNH VỀ KIẾN TRÚC VÀ NĂNG LỰC NÀO?

### 2.1. Bài toán thật không phải “tóm tắt nội dung”

Transcript không phải danh sách kết luận có sẵn. Người tham gia có thể nói “đề xuất A”, “hay thử B?”, “thống nhất B để pilot”, “chưa được triển khai do pháp chế”, “chưa chọn vendor”, “giao Lan thử X”, rồi “hủy việc thử X”.

Hệ thống cần giữ:
- **Loại thực thể:** decision, action, request, issue, feedback, knowledge.
- **Hành vi lời nói / event_type:** proposal, agreement, reopen, assignment, cancellation, unresolved...
- **Trạng thái hiện tại:** `meeting_status` không giống `execution_status`.
- **Các trường:** owner, supporter, due_raw, due_iso, condition — có thể chưa có.
- **Chứng cứ:** `source_ids`, `field_evidence_ids`, `counter_evidence_ids`.
- **Lịch sử theo issue:** không vứt lời chốt trước, nhưng cũng không trình bày lời cũ như hiệu lực mới.
- **Quyền human review:** AI chưa được thay tổ chức phê duyệt.

### 2.2. Pipeline M2 và lý do từng tầng tồn tại

```text
Transcript
  ↓ Parser: Utterance{id, speaker, order, text}
  ↓ LLM Event Extractor: nhận diện event/speech act
  ↓ Temporal Resolver: cập nhật trạng thái theo issue_key + thứ tự
  ↓ Verifier: kiểm tra nguồn, trường, ngữ nghĩa rủi ro
  ↓ LLM Auditor: đề xuất phát hiện sai/thiếu
  ↓ Human Review → JSON / CSV, có nguồn & lịch sử
```

**[Điểm mạnh S1] Temporal state tracking:** D01 hồi quy cuối M2 có object storage được chốt, trong khi nhà cung cấp vẫn là decision open. “Chưa chọn vendor” không được thành condition phải chọn lại công nghệ.

**[S2] Quyết định ≠ được phép triển khai:** D03 đã `agreed` về thiết kế nhưng `blocked` để triển khai vì pháp chế. Cần hai trường, không phải một chữ “đã chốt”.

**[S3] Condition có thể thay đổi:** D04 hồi quy cuối giữ điều kiện mới 300 users đồng thời **AND** không lỗi nghiêm trọng; không tự cho là điều kiện đã đạt.

**[S4] Mở lại quyết định không hủy dây chuyền task:** H01: decision reopened, action riêng của Huy vẫn assigned.

**[S5] Abstention/uncertainty:** D07 không tạo business record từ câu thử mic; D12 không coi lời báo đã sửa là kiểm chứng độc lập; H04 không coi biên bản cũ là quyết định hôm nay; H06 không bịa ngày ISO khi thiếu thông tin.

**[S6] Evidence + Human Review:** M2 có khả năng trỏ về câu nguồn, giữ lịch sử thay đổi và người dùng rà soát trước khi xuất.

**[S7] Có sản phẩm vận hành:** Giao diện trên Vercel, backend Python/LLM trên Render, không chỉ là notebook; có unit test và dữ liệu đánh giá lịch sử.

> **Giới hạn của điểm mạnh:** Các trường hợp trên là *ca từng làm đúng*, không có nghĩa hệ thống luôn đúng. Một source ID tồn tại không chứng minh nó đúng vai trò nghiệp vụ; reviewer flag không thay thế correctness.

---

## 3. ĐÁNH GIÁ M2: SỐ LIỆU 24 CA VÀ TỪNG NHÓM LỖI

### 3.1. Lượt dataset toàn pipeline ngày 13/10 [A]

Nguồn: [DATASET_EVALUATION_RESULTS.md](DATASET_EVALUATION_RESULTS.md). Model: `openai/gpt-oss-120b`. 24 transcript **synthetic**, trong đó 16 development và 8 reserved ban đầu; nhãn và review do cùng trợ lý làm, **chưa xác minh độc lập**. Một lượt chính, không cherry-pick.

| Chỉ số | M2 |
|---|---:|
| Pipeline hoàn tất | **20/24 = 83,3%** |
| Ca đạt/chưa đạt/lỗi API | **9 đạt / 11 chưa đạt / 4 lỗi** |
| Precision bản ghi có căn cứ | **37/45 = 82,2%** |
| Recall mục bắt buộc (gồm ca lỗi API) | **23/57 = 40,4%** |
| Recall chỉ ca có đầu ra | **23/31 = 74,2%** |
| Đúng kết luận cuối trong cặp ghép được | **9/12 = 75,0%** |
| Recall quyết định cuối tính cả thiếu | **9/20 = 45,0%** |
| Bằng chứng hỗ trợ đúng | **37/45 = 82,2%** |
| Precision cảnh báo audit | **2/10 = 20,0%** |
| Ca âm không sinh record | **2/2** — mẫu quá nhỏ |

**Phân theo độ dài:**

| Loại transcript | Pipeline hoàn tất | Required recall (gồm lỗi) |
|---|---:|---:|
| Short | 18/18 | 19/27 = 70,4% |
| Medium | 2/3 | 4/10 = 40,0% |
| Long-for-MVP | **0/3** | **0/20** |

HTTP 400 được quan sát ở D09/D15/D16/H08. **Chưa xác định được nguyên nhân gốc**: provider/config/JSON mode/budget/length có thể liên quan. Không suy luận “model không hiểu họp dài” từ HTTP 400 đơn độc.

**Trường có dữ liệu bị mất khi tính cả missing/errored cases:**

| Field | Thu hồi có giá trị đúng trên tổng số cần có |
|---|---:|
| owner | 6/13 = 46,2% |
| supporter | 3/7 = 42,9% |
| due_raw | 3/9 = 33,3% |
| condition | 0/4 = 0% |

Các tỷ lệ này là **lượt dataset ban đầu**, không được gán nguyên xi cho bản M2 đã chốt sau sửa. `due_iso` gần như null không có nghĩa chuẩn hóa ngày đạt 100%.

Đã có **45 API attempts** (bao gồm retry), 102.621 tokens nhà cung cấp báo ở các response có usage; 1.987,2 giây thời gian cộng case, median 89,7 giây/case **có khoảng đợi giữa attempts**, không là latency model thuần.

### 3.2. Phân nhóm root cause (điểm yếu W1–W10)

| Mã | Điểm yếu | Mẫu ca/biểu hiện | Hậu quả |
|---|---|---|---|
| **W1** | **Omission / required recall thấp** | H03 mất request + hạn; LC02 mất phương án chưa chốt; D08 mất issue | Người dùng không thấy nghĩa vụ/vấn đề thực |
| **W2** | **False commitment / sai loại record** | LC01 giao task → request giả; LC02 thử library → proposal thừa | Nhầm task với requirement/decision |
| **W3** | **Audit false positive** | LC03/D06 xóa owner lịch sử; LC02 reason → condition; H03 ngày đề xuất → due | AI audit làm xấu một kết luận vốn đúng |
| **W4** | **Cross-topic negation** | D13/M3-R01 “chưa chọn vendor” làm warning architecture | Lan truyền sai trạng thái giữa issue |
| **W5** | **Field evidence thiếu ngữ nghĩa** | D03 condition/scope thiếu; D04 ngưỡng cũ; H03 relative due | Source ID đúng chưa bảo đảm field đúng |
| **W6** | **Knowledge chưa tách tính hữu dụng** | Kinh nghiệm idempotency và lời nghe nói benchmark cùng dạng knowledge | Nguy cơ “rửa” lời đồn thành tri thức |
| **W7** | **Long transcript reliability** | D09/D15/D16/H08 HTTP 400 | Không có đầu ra để chấm |
| **W8** | **ASR/raw/noisy transcript** | D11 không dấu sai nghĩa; H07 mất tiếng thiếu warning cụ thể | Khó dùng họp ngoài đời |
| **W9** | **Prompt injection trong transcript** | D14 sinh record từ chỉ dẫn nhúng | Dữ liệu không đáng tin ảnh hưởng extraction |
| **W10** | **Thiếu bằng chứng cải thiện có thể tái lập** | Thử nhiều candidate dễ chỉ nhìn case đẹp | Không chứng minh được M3 tốt lên |

**Lý giải then chốt:** Recall thấp không đồng nghĩa mọi output đều sai; 37/45 grounded records có thể cùng tồn tại với 23/57 required recall vì **toàn bộ record cần có đã biến mất**. Ngược lại, “record có nguồn” vẫn có thể sai loại nghiệp vụ.

**Đánh giá về audit:** Precision 2/10 không có nghĩa nên tắt audit. Giải pháp tốt phải giảm false positive **và vẫn bắt được lỗi thật**; cần cả negative controls lẫn positive controls.

### 3.3. Tại sao không chỉ đổi model hoặc tăng prompt?

M2 đã dùng model mạnh `gpt-oss-120b`; nhiều lỗi đến từ **định nghĩa speech act, temporal state, kiểm tra logic và ranh giới nguồn**. Đổi model không trực tiếp sửa câu “reason hủy khác condition” hoặc “owner lịch sử không tự xóa”. Ngoài ra thay model làm baseline khó đối chiếu. Phương án M3: sửa hẹp từng tầng trước, dùng LLM làm bộ phát hiện event; sau đó mới đo hiệu ứng end-to-end.

---

## 4. NHẬT KÝ 24 TRƯỜNG HỢP M2

**Lưu ý:** Bảng là kết quả **lượt 24 ca ban đầu**, không thay cho tám ca hồi quy sau này; xem bảng gốc nếu cần chữ chính xác.

| Ca | Trạng thái | Quan sát chính | Điều cần học |
|---|---|---|---|
| D01 | FAIL | Missing vendor open; audit coi vendor là condition | Independent open issue |
| D02 | FAIL | Reopen bị nhầm withdrawal, audit đòi xóa lịch sử | Reopen ≠ withdraw |
| D03 | FAIL | Agreed/blocked có nhưng thiếu detail legal | Evidence theo trường |
| D04 | FAIL | 500 → 300 nhưng điều kiện cuối sai | Last effective condition |
| D05 | PASS | Reassignment + supporter + bỏ due đúng | Ownership chronology |
| D06 | FAIL | Owner lịch sử sau cancelled bị audit đòi xóa | Historical owner |
| D07 | PASS | Mic check và giả định → không business record | Abstention |
| D08 | FAIL | Missing invoice issue, request trùng action | Coverage + dedup |
| D09 | ERROR 400 | Nhiều chủ đề, task gần tên | Reliability |
| D10 | PASS | Request withdrawn, feedback giữ | Independence |
| D11 | FAIL | Transcript ASR không dấu bị hiểu sai | Noise |
| D12 | PASS | “Báo đã sửa” không là independent validation | Evidence uncertainty |
| D13 | PASS nội dung | Ngữ nghĩa lõi đúng nhưng verifier warning khác issue | Topic scope |
| D14 | FAIL | Prompt injection thành record giả | Untrusted transcript |
| D15 | ERROR 400 | Long, late correction | Reliability |
| D16 | ERROR 400 | Long, ASR + condition | Reliability |
| H01 | FAIL | Reopened nhưng condition cũ giữ ở trường hiện hành | Historical vs current |
| H02 | PASS | Hai task gần tên; owner đổi đúng task | Issue separation |
| H03 | FAIL | Relative deadline còn thiếu trong cấu trúc | Missing due |
| H04 | PASS | Biên bản cũ không thành quyết định mới | Historical assertions |
| H05 | PASS | Câu hỏi không thành nhận việc, có fragmentation | Question/assignment |
| H06 | PASS | Deadline cuối, không bịa ISO | Time uncertainty |
| H07 | FAIL | Mất tiếng, không bịa nhưng warning thiếu | Source-quality report |
| H08 | ERROR 400 | Long, nhiều lần sửa, task tương tự | Reliability |

**Bài tập khi đọc:** chọn D03/D04/H01 và tự viết state machine trước khi mở [FINAL_REGRESSION_RESULTS.md](FINAL_REGRESSION_RESULTS.md).

---

## 5. HỒI QUY CUỐI M2: TÁM CA, VÀ VÌ SAO GIỮ A

Ngày 14/10, một lượt hồi quy cố định: `openai/gpt-oss-120b`, temperature **0,6**, reasoning low, extraction budget **2.560 tokens**, audit budget **1.024**, min call interval **90 giây**, max_retries **0**. Kết quả **8/8 pipeline + audit completed; 5/8 core pass, 4/8 full pass** [A].

| Ca | Kỳ vọng / trạng thái M2 A | M2 A kết luận |
|---|---|---|
| D01 | Object storage agreed + vendor open; không bịa owner/hạn | **PASS** |
| D03 | Design agreed nhưng execution blocked theo điều kiện pháp chế | **PASS** |
| D04 | Conditional mới 300 users + AND không lỗi nghiêm trọng | **PASS** |
| H01 | Decision reopened, independent Huy action vẫn assigned | **PASS** |
| LC01 | Một cancelled action, không request/decision clone | **FAIL:** request trùng |
| LC02 | CSV request giữ, trial cancelled, alternative open | **FAIL:** thiếu open, dư proposal, audit condition sai |
| LC03 | Owner Chi lịch sử, due cleared, task cancelled | **Core PASS**, nhưng **audit FAIL** |
| H03 | Request rà soát email, due trước lần thử tiếp theo, ngày/person chưa chốt | **FAIL:** thiếu request/due; audit ngày sai |

**Tư duy regression-first:** D01/D03/D04/H01 vốn đúng trong baseline A phải luôn được giữ. Chỉ số full pass bao gồm dữ liệu *và* audit không gây false alert; vì thế một ca core pass vẫn có thể full FAIL.

Nguồn: [FINAL_REGRESSION_RESULTS.md](FINAL_REGRESSION_RESULTS.md).

---

## 6. THỬ NGHIỆM M2: B1/B2/C1/C2 VÀ RAW — KỂ CẢ THẤT BẠI

### 6.1. Candidate B1 và B2 [A]

**Giả thuyết:** dùng prompt bao phủ thêm request/open issue và normalize assignment từ speech act; nhắc auditor về cancelled owner, cancellation reason.

| Phiên bản | Completed | Full pass | Core pass | Tokens provider báo |
|---|---:|---:|---:|---:|
| A | 8/8 | 4/8 | 5/8 | 37.817 |
| B1 | 7/8 | 5/8 | 5/8 | 39.636 |
| B2 | 8/8 | 4/8 | 5/8 | 42.932 |

**Thành công cục bộ:** B1 sửa được H03/LC03 trong một số lượt; B2 sửa LC01/LC03. **Thất bại quyết định:** B1 lỗi pipeline và D01 hồi quy; B2 D01/H01 hồi quy; overall full pass không vượt A ở B2. Bản ứng viên không được chọn.

**Bài học:** Tăng coverage bằng prompt rộng có thể làm model coi agenda thành request, hoặc khiến audit đọc lịch sử thành điều kiện hiện tại. **Một phương án cải thiện một ca nhưng phá ca gốc là chưa đủ để release.**

Nguồn: [CANDIDATE_B_CORE_REPAIR.md](CANDIDATE_B_CORE_REPAIR.md).

### 6.2. Candidate C1 — sửa hẹp [A]

**Giả thuyết:** giữ prompt A, chỉ normalize khi có **lệnh giao đích danh + xác nhận của người nhận + same key/content**; thêm cancelled task context. Pilot gồm LC01/LC03/D01/H01 với gate 4/4.

**Kết quả:** 4/4 completed, 8 API calls, **2/4 full pass**, 19.834 tokens, 134 code tests:
- **LC01 PASS**: assignment sai vai trò được chuẩn hóa đúng.
- **H01 PASS**: reopened/independent action còn đúng.
- **LC03 FAIL**: due “ngày mai” bị giữ dù đã bỏ hạn.
- **D01 FAIL evidence**: thiếu nguồn L006 xác lập scope thử nghiệm.

**Bài học:** Fix sai speech act **không đủ** để fix due clearing hay evidence của content/scope. Audit có thể phát hiện lỗi mà record vẫn sai.

Nguồn: [CANDIDATE_C1_NARROW_REPAIR.md](CANDIDATE_C1_NARROW_REPAIR.md).

### 6.3. Candidate C2 — source/date repair [A]

**Giả thuyết:** vẫn giữ prompt/schema A, thêm guarded `clear_fields` để bỏ hạn có nguồn, bổ sung source muộn cho exact final agreement.

**Kết quả pilot:** 4/4 completed, 8 API calls, **3/4 core pass, 1/4 full pass**, 19.446 tokens, 144 code tests:
- LC03 đạt cả core/audit trong lượt này.
- D01: thiếu provider open, audit nhầm provider thành condition.
- LC01: core đúng, audit đòi nhầm nguồn history vào field hiện tại.
- H01: core đúng, audit muốn hồi sinh condition cũ.

**Bài học:** sửa bằng chứng hoặc deadline **không làm xuất hiện record bị extractor bỏ sót**. Audit vẫn có thể phá kết quả lõi. Vì pilot trượt gate nên không được tự chọn C2 thay A.

Nguồn: [CANDIDATE_C2_SOURCE_REPAIR.md](CANDIDATE_C2_SOURCE_REPAIR.md).

### 6.4. Raw transcript V1/V2 (lịch sử thử nghiệm M2)

Đã có hướng xử lý transcript raw/không tách speaker/chunk, trong đó nhánh local `candidate/raw-transcript-v2-20261015` từng được ghi nhận. Một vài pilot nhỏ có tín hiệu tốt; **không có xác nhận vượt đủ các cổng regression/operational để promote vào main**, nên không gộp vào A hoặc coi đây là phần Stage 4 M3 đã hoàn thành.

**Tổng bài học B/C/Raw:** ghi lại mọi lỗi và raw outputs; *thay đổi theo hypothesis*; không cherry-pick case; phân biệt mã sửa chạy đúng với LLM sinh kết quả mới tốt; giữ A làm mốc khi candidate chưa vượt gate.

---

## 7. VÌ SAO TƯ DUY CHUYỂN TỪ M2 SANG M3?

| Lỗi quan sát | Root cause cần điều tra | Phương pháp đúng, giới hạn |
|---|---|---|
| H03 thiếu request | Extractor không đưa event vào output | Verifier không thể kiểm tra record không có; cần coverage/recovery |
| LC01 request giả | Assignment nhầm request | Sửa speech act khi có nguồn giao/nhận task chắc chắn |
| LC02 proposal giả | Task thử X bị coi như đề xuất chọn X | Tách decision khỏi action, chỉ giữ open nếu thật sự chưa chốt |
| M3-R01/D13 warning sai | Keyword `chưa chốt` bị áp lên mọi record phía trước | Scope negation theo topic/issue/option |
| LC03 owner bị đòi xóa | Audit không phân biệt history và current | Kiểm tra ý nghĩa event + field, cần positive controls |
| M3-E01/LC02 reason hủy | Audit không phân biệt reason và precondition | Guard có source, không đưa reason vào condition hiện tại |
| H03 ngày bị đề xuất | Field due được dùng từ câu hỏi | Không nhận tentative date là accepted deadline |
| M3-K01 practice vs rumor | Thiếu utility và trust semantics | Tách mục đích sử dụng khỏi `authority_status` |
| HTTP 400 dài | Có lỗi provider/adapter chưa điều tra | Không kết luận model sai ngữ nghĩa nếu không có output |

**Năm nguyên tắc chuyển sang M3:**

1. **Giữ kiến trúc đang hoạt động**, không viết lại để “thay AI cho ngầu”.
2. **Sửa ít, có điều kiện nguồn rõ**, mỗi patch phải có test đối chứng.
3. **Không lạm dụng `needs_review`:** nó là an toàn, không phải correctness.
4. **Kiểm thử cả điểm cũ vốn tốt** trước khi dùng candidate mới.
5. **Replay để cô lập hiệu ứng code; fresh inference để đánh giá cả hệ thống**. Hai loại bằng chứng tuyệt đối không thay thế nhau.

## 8. STAGE 0, 0.5, 1, 2, 3 — TƯ DUY, MÃ SỬA, THỬ NGHIỆM, KẾT QUẢ

### Stage 0 — Pre-register kế hoạch trước khi sửa [C]

**Đầu vào tư duy:** M2 nhiều lần candidate tốt lên ở LC01 nhưng làm D01/H01 kém đi; do đó mọi sửa phải có cổng bảo toàn.

**Triển khai:** tạo nhánh `mission3/improvement-20261021`, file [MISSION3_BASELINE_AND_PLAN.md](MISSION3_BASELINE_AND_PLAN.md), [MISSION3_ACCEPTANCE_CRITERIA.md](MISSION3_ACCEPTANCE_CRITERIA.md), [MISSION3_TEST_MATRIX.md](MISSION3_TEST_MATRIX.md), cùng `samples/mission3/M3-E01/E02/R01/K01.txt`. Khóa trước các kỳ vọng về cancelled task vs customer requirement, agreement blocked vs vendor open, knowledge vs rumor.

**Bằng chứng:** baseline 124 Python tests, commit `7663f2e`; chưa sửa lõi. **Bài học:** Không được vừa thử vừa đổi đáp án sao cho khớp output.

### Stage 0.5 — Đóng băng M2 và đo Before [A/C]

**Vấn đề:** Sau khi M3 merge `main`, liệu còn chạy được M2 để so sánh? **Có**, vì tag bất biến vẫn trỏ M2, và worktree tách hẳn mã nguồn.

- M2 submitted tag: `submission-a-ui-v2-20261015` → `439f672`.
- M2 baseline AI tag: `baseline-a-20261014` → `4aecdc9`.
- Detached worktree: `tmp/m2-submission`. Không cần tải ZIP làm bản duy nhất.
- Frozen dataset: `datasets/mission3_before_after_v1.json`.
- Frozen labels: `datasets/mission3_before_after_labels_v1.json`.
- SHA-256/hướng dẫn: [frozen_manifest_v1.json](evaluation/mission3/frozen_manifest_v1.json).

**API M2 thật [A]:** Groq hosted M2 (model `openai/gpt-oss-120b`), bốn case **4/4 completed**, 8 provider calls, **18.141 tokens**; internal semantic review **3/4 core case pass, 1/4 full case pass, 6/8 required strict core items**.

| Case | Before M2 mới | Gap ưu tiên |
|---|---|---|
| M3-E01 | Request CSV và cancelled trial đúng nhưng auditor đòi reason giấy phép thành condition | False audit + evidence chưa trọn |
| M3-E02 | Một cancelled task, không request giả — full PASS | Bảo toàn đúng |
| M3-R01 | Pilot B agreed/blocked, vendor open đúng; verifier vẫn cảnh báo late negation sai issue | Cross-topic warning |
| M3-K01 | Action đúng; idempotency advice/rumor chưa tách utility; no-choice bị `proposed` | Knowledge utility + unresolved |

**Giới hạn bằng chứng:** API hosted không trả commit SHA đang chạy; không chứng minh byte-identical với worktree local. Dữ liệu và review synthetic, nội bộ, không độc lập. Local thiếu `LLM_API_KEY` ở mốc này. **Commit:** `fe0d2ce`. [Stage 0.5](MISSION3_STAGE_05_BASELINE.md), [M2 Before raw](evaluation/mission3/m2_remote_baseline_v1.json), [review](evaluation/mission3/m2_remote_review_v1.json).

### Stage 1 — Lifecycle & False Commitment Repair [B/C]

**Giả thuyết 1:** Regex “chưa chốt” quá rộng gây cảnh báo khi chủ đề khác. **Sửa:** `verifier.py` yêu cầu nguồn phủ định muộn nói đến **cùng lựa chọn/issue**, có negative/positive control.

**Giả thuyết 2:** Việc bị hủy không nên sinh một customer request từ cùng câu giao việc. **Sửa:** source-backed duplicate suppression chỉ khi cùng issue/content, lệnh giao đích danh, người được giao đã nhận, việc cancelled. Không xóa customer requirement độc lập.

**Giả thuyết 3:** Auditor nhầm cancellation reason với operative condition, owner lịch sử với active assignment. **Sửa:** `auditor.py` kiểm tra finding có căn cứ và bối cảnh lifecycle; giữ finding thật về missed cancellation/explicit owner clear.

**Giả thuyết 4:** `proposal` của no-choice rõ ràng không đúng. **Sửa:** `extractor.py` chỉ đổi sang `unresolved` khi cả *value* và câu nguồn nói “chưa chọn/chốt”.

**Kết quả Stage 1:** [C] **147/147 Python**; [B] LC01 **2 → 1 record**, LC03 false audit **1 → 0**; M3-E01 audit sai **1 → 0**, M3-R01 warning chéo issue bị loại; M3-K01 chuyển choice `proposed → open`. M3-E02 và D01/D03/D04/H01 giữ đúng trong replay.

**Stage 1 chưa sửa:** H03 vẫn thiếu request và hạn; LC02 vẫn thiếu alternative open. Đây là bằng chứng quan trọng để đi tiếp Stage 2, vì chỉ lọc sai không tạo được sự kiện đã mất.

**Commit:** `3a2ad24`. [Stage 1 results](MISSION3_STAGE1_RESULTS.md), [replay 8](evaluation/mission3/m3_stage1_replay_eight_v3.json).

### Stage 2 — Evidence Validation & Missing Information Recovery [B/C]

**Lý do chọn Stage 2:** Sau Stage 1, các lỗi W2/W3 giảm trong replay nhưng **W1 (missing required items)** chưa sửa. Phát hiện H03/LC02 không phải do resolver làm hỏng state, mà do **event extractor đã không đưa một record vào danh sách**. Verifier kiểm tra record hiện hữu không thể cứu record không tồn tại.

**Thiết kế source-anchored, bounded recovery:**
- Module mới `meeting_intelligence/completeness.py`, chạy sau `extract_events` trong pipeline LLM.
- Chỉ xét **câu tường minh** tạo request độc lập hoặc lựa chọn chưa chốt; kiểm tra trùng nguồn/nội dung.
- Không tự tạo `action assignment`, owner hoặc `decision agreed`.
- Reject câu hỏi, giả định, trích biên bản cũ, câu “chưa chọn A, sau đó đã chọn B”; nếu không rõ thì abstain.
- Mọi bản ghi recovered có nguồn literal + `needs_review` + warning, `authority_status=unknown`.

**Tăng field-level evidence:** `verifier.py` kiểm tra nguồn không tồn tại, câu đề xuất/câu hỏi không chứng minh due/agreement, phủ định owner, ngưỡng số không có trong source. `auditor.py` không chấp nhận ngày mới đề xuất như deadline đã chốt; positive control bảo toàn hạn đã chốt thật. `verifier.py` lọc một proposal trùng task đã giao được xác nhận.

**Kết quả Stage 2:** [C] **174/174 Python**, **12/12 frontend**; 27 test Stage 2. [B] H03 **1 → 2 records**, thêm request rà soát email `due_raw = "trước lần thử tiếp theo"`, owner null, review required; hai cảnh báo audit deadline sai **2 → 0**. LC02 có **3 record nghiệp vụ đúng vai trò**: CSV request, cancelled library trial, replacement choice `open`; proposal phụ và false audit bị loại. D01/D03/D04/H01 giữ đúng theo archived-event replay.

**Hạn chế trung thực:** rule hẹp có thể bỏ sót paraphrase, ellipsis, ASR không dấu; chưa là semantic entailment tổng quát; thêm record recovered có thể gây false positive nếu câu nguồn phức tạp → bắt buộc human review. Replay dùng event cũ, không phải fresh Groq M3.

**Commit:** `086fee0`. [Stage 2 results](MISSION3_STAGE2_RESULTS.md), [replay 8](evaluation/mission3/m3_stage2_replay_eight_v3.json).

### Stage 3 — Knowledge Validation & Information Utility [B/C]

**Root cause:** M2 có `kind = knowledge` nhưng chỉ biết `unverified`, không phân biệt lời khuyên quy trình có thể tái sử dụng với tin đồn chưa có bằng chứng. Không nên giải quyết bằng cách nâng tất cả knowledge lên “recorded”.

**Schema mới, tương thích ngược:**
- `information_utility` và `information_utility_note` là field optional của `ResultRecord`.
- `current_work`: nghĩa vụ/issue/decision hiện tại (kể cả open).
- `reusable_candidate`: lời khuyên kỹ thuật/quy trình có nguồn, **chưa phê duyệt**.
- `historical_context`: task cancelled, withdrawn decision hoặc nhắc lại chuyện cũ.
- `needs_verification`: tin đồn, hypothesis, không có bằng chứng, có phản chứng.

`meeting_intelligence/information_utility.py` phân loại **sau audit**, dựa trên source thực, uncertainty/practice markers, và một số phản chứng rõ ràng. Ghi `field_evidence_ids.information_utility` và `counter_evidence_ids` khi thích hợp.

`frontend/app.js` hiển thị nhãn, giải thích, evidence. `frontend/review.js` giữ nhãn AI dưới tên `ai_information_utility` và `ai_utility_note` khi xuất JSON/CSV; xác nhận cá nhân vẫn **`authority_status=unknown`**.

**Kết quả Stage 3:** [C] **197/197 Python**, **13/13 frontend**; 23 bài test Stage 3. [B] M3-K01:
- L001: action kiểm thử tải → `current_work`.
- L002: dùng idempotency key khi retry → `reusable_candidate`, nhưng vẫn `meeting_status=unverified`, `review_status=needs_review`.
- L003: “nghe nói thư viện Y luôn nhanh hơn X” → `needs_verification`.
- L004: chưa chọn thư viện → decision `open`, utility `current_work`.
- E01/E02/R01 giữ phân biệt current/history/open trong replay.

**Hạn chế:** Đây là phân loại *mục đích sử dụng*, không phải fact-checking, RAG hay knowledge base đã phê duyệt; marker theo mẫu câu không bao phủ paraphrase. M3 utility không thể chấm như một trường accuracy chung với M2 nếu M2 chưa từng có trường đó.

**Commit:** `4a91ca5`. [Stage 3 results](MISSION3_STAGE3_RESULTS.md), [replay 4](evaluation/mission3/m3_stage3_replay_four_v2.json).

### Toàn bộ tăng trưởng test là mức độ phủ **phần mềm**, KHÔNG là LLM accuracy

| Mốc | Python tests | Nguồn bằng chứng |
|---|---:|---|
| Stage 0 | 124 | [C] |
| Stage 0.5 | 129 | [C]; riêng M2 Before thật là [A] |
| Stage 1 | 147 | [C/B] |
| Stage 2 | 174 | [C/B] |
| Stage 3 | 197 | [C/B], 13 frontend |

---

## 9. MA TRẬN ĐIỂM YẾU M2 → STAGE XỬ LÝ → KẾT QUẢ

| Điểm yếu | Stage áp dụng | Kỹ thuật | Bằng chứng hiện có | Chưa xác nhận |
|---|---|---|---|---|
| W1 Missing request/open issue | Stage 2 | Bounded omission recovery | [B] H03/LC02 recovered | Fresh M3 recall |
| W2 Duplicate request từ action | Stage 1 | Source-backed assignment guard | [B] LC01 2 → 1 | Nhiều cách paraphrase |
| W2 Proposal từ thử library | Stage 2 | Drop proven task-proposal echo | [B] LC02 loại proposal phụ | End-to-end model outputs |
| W3 Reason hủy thành condition | Stage 1 | Audit's causal-reason guard | [B] LC02/E01 finding sai → 0 | Audit precision mới |
| W3 Owner lịch sử bị xóa | Stage 1 | Lifecycle-aware owner guard | [B] LC03 finding sai → 0 | Ngữ cảnh owner phức tạp |
| W3 Ngày chưa chốt bị dùng | Stage 2 | Late-no-choice audit check | [B] H03 2 findings → 0 | Ngày chốt được nhận diện đầy đủ |
| W4 Negation khác issue | Stage 1 | Issue/option scoped checking | [B] R01 warning sai loại | Implicit semantic relation |
| W5 Field source yếu | Stage 2 | Source ID, tentative due, numeric condition checks | [C] positive/negative controls | Full entailment |
| W6 Knowledge không tách utility | Stage 3 | Four-way utility classification | [B] K01 idempotency vs rumor | True factual reliability |
| W7 Long transcript HTTP 400 | Stage 4 dự kiến | Provider diagnostics, chunking/reconcile | [A] M2 lỗi đã được lưu | M3 long completion |
| W8 ASR/raw, missing audio | Stage 4 dự kiến | Robust parsing/source quality | [A] M2 vấn đề đã đo | M3 raw robustness |
| W9 Transcript injection | Chưa hoàn thành | Boundary + adversarial tests | M2 D14 vẫn sai | An toàn mới |
| W10 Không tái lập Before | Stage 0/0.5 | Git tag/worktree, frozen gold, raw artifacts | [A] M2 Before + [C] hashes | Fresh M3 After |
| Change Request và release | Chưa hoàn thành | Official CR test, end-to-end rollout | [D] pending | Demo M3 chính thức |

---

## 10. BEFORE/AFTER CỤ THỂ — KHÔNG GIẤU CÁC CA KHÓ

### 10.1. Bốn ca vốn đúng — kiểm tra không bị phá

| Ca | Before M2 [A] | M3 code replay [B] |
|---|---|---|
| D01 | Object storage agreed, vendor open | Hai đối tượng, trạng thái tương ứng được giữ |
| D03 | Decision agreed, execution blocked pháp chế | Phạm vi và trạng thái giữ |
| D04 | Condition 300 AND no severe error | Giữ conditional và điều kiện |
| H01 | Decision reopened, Huy task vẫn assigned | Giữ phân tách decision/action |

### 10.2. Bốn ca lỗi phải cải thiện

| Ca | Before M2 [A] | Stage 1 [B] | Stage 2/3 [B] |
|---|---|---|---|
| **LC01** | Action cancelled + request recorded giả | Sửa trùng | Còn **1 action cancelled**, giữ owner lịch sử |
| **LC02** | CSV request và cancelled trial, thiếu alternative open, có proposal thừa, audit sai | Audit sai giảm, open vẫn thiếu | **3 nghiệp vụ đúng:** CSV request, trial cancelled, alternative **open** |
| **LC03** | Core đúng, audit muốn xóa Chi lịch sử | Finding sai bị chặn | Chi vẫn là owner lịch sử |
| **H03** | Chỉ decision open, request/due missing, 2 false date findings | Chưa sửa omission | **2 records:** thêm request `due_raw = "trước lần thử tiếp theo"`, owner null, needs_review; false findings được chặn |

### 10.3. Bốn ca M3 mới đã khóa trước khi sửa code

| Case | Hosted M2 thật [A] | M3 replay [B] | Học được |
|---|---|---|---|
| M3-E01 | Request/task core đúng, audit reason-condition sai | Giữ core, false finding loại | Reason không là điều kiện hiện hành |
| M3-E02 | Một cancelled action đúng | Không phát sinh request | Sửa lỗi không phá cái đang đúng |
| M3-R01 | B agreed/blocked, vendor open, warning chéo | Phân biệt issue, warning chéo biến mất | Cùng chữ B nhưng hai lựa chọn khác |
| M3-K01 | Task đúng; knowledge thiếu utility; no-choice proposed | Practice candidate/rumor unverified; choice open | Utility tách khỏi truth |

**Bằng chứng JSON:** [M2 Before](evaluation/mission3/m2_remote_baseline_v1.json), [Stage 1 replay](evaluation/mission3/m3_stage1_replay_eight_v3.json), [Stage 2 replay](evaluation/mission3/m3_stage2_replay_eight_v3.json), [Stage 3 replay](evaluation/mission3/m3_stage3_replay_four_v2.json).

**Không được tuyên bố:** “M2 4/8 → M3 8/8”, “M3 recall đã vượt 40,4%”, “M3 knowledge accuracy 100%”, bởi chưa có một lượt fresh M3 LLM tương ứng.

---

## 11. VIỆC CHƯA XONG — ĐƯỜNG ĐẾN MISSION 3 RELEASE

### P0: Stage 3.5 — LLM inference mới, source M3 được attest

1. Pin commit M3 cụ thể (gốc Stage 3 `4a91ca5` hoặc commit candidate mới).
2. Chạy source M3 thật qua môi trường có API key được cung cấp **riêng tư**, không lấy API của Render M2 rồi gắn nhãn M3.
3. Giữ nguyên frozen labels/transcripts `mission3_before_after_v1.json`; chấm bốn ca mới và tám regression cùng tiêu chí nghiệp vụ.
4. Lưu model, endpoint, temperature, reasoning, token budgets, source hashes, input hashes, failed outputs, token/calls và raw output JSON, không cherry-pick.
5. Tính các chỉ số riêng: **completeness, false action/decision, audit false-positive, correct state, evidence per field, operation success**, rồi đánh giá human review.
6. Bảo toàn D01/D03/D04/H01. Nếu fail, sửa có commit/run mới và giữ nguyên log trước đó.
7. Nếu có thể, một test mù độc lập chưa dùng để tuning và lặp lại qua nhiều lượt.

Lệnh minh họa với credential hợp lệ:

```powershell
python -X utf8 scripts/run_mission3_comparison.py --version m3 --preflight
python -X utf8 scripts/run_mission3_comparison.py --version m3 --transport local --out docs/evaluation/mission3/m3_fresh_local_RUN1.json
python -X utf8 -m unittest discover -s tests -q
node --test tests/review.test.cjs tests/deploy.test.cjs
```

**Trạng thái:** [D] Chưa chạy Groq mới với source M3 tại ngày 21/10/2026. Bốn case trên không tự đánh giá được toàn bộ họp dài.

### P1: Stage 4 — Transcript dài, raw/ASR, injection

- Điều tra chính xác HTTP 400 (status/body, rate limit, provider settings, JSON mode, token budget); không quy kết model nếu thiếu bằng chứng.
- Nếu cần chunking: giữ IDs/offsets, overlap phù hợp, theo dõi issue xuyên chunk và **global final reconciliation** để sửa late decision/owner/due.
- Ca stress với nhiều chủ đề xen kẽ, hai task gần tên, đổi điều kiện ở cuối họp, ASR không dấu/ngắt đoạn không chuẩn.
- Không đưa câu prompt injection trong transcript thành instructions có hiệu lực; thêm adversarial tests.
- Khi mất tiếng/speaker unknown: cảnh báo nguồn không đầy đủ thay vì tự bịa.

### P0 theo BTC: Change Request chính thức và kiểm thử

Tại mốc hồ sơ này, portal trước đó nói chưa có CR được gán; **không tự bịa CR**. Khi có phải lưu nguyên văn, viết acceptance M3-CR01, implement tối thiểu và chạy regression; nếu gấp, ưu tiên CR hơn polish UI.

### P0: Release chính thức

- Tag M2 `submission-a-ui-v2-20261015` tại `439f672` **không mất khi merge M3**.
- Giữ branch M3 riêng cho đến khi đạt cổng; merge vào `main` rồi xác minh cả **Vercel frontend** và **Render backend** chạy đúng commit, health endpoint/export/review đầy đủ.
- Preview frontend còn dùng backend M2 **không** đủ chứng minh M3 full-stack.
- Nộp GitHub, demo, video và câu trả lời đúng rubric, có Before/After trung thực.
- Mốc deadline kế hoạch: **23/10/2026 11:49 ICT**.

---

## 12. BÀI HỌC, LỘ TRÌNH HỌC LẠI VÀ PHỎNG VẤN

### 12.1. Tám điều phải nhớ

1. **Meeting Intelligence khác summarization.** Typed event + temporal issue state mới là phần khó.
2. **Grounding precision ≠ recall.** 37/45 grounded vẫn có 23/57 required recall.
3. **Có citation ≠ hỗ trợ đúng speech act.** “Giao Lan thử X” không tự tạo customer requirement.
4. **Audit cũng có false positives.** 2/10 nên phải audit finding của auditor; test positive controls, không tắt hết audit.
5. **Open khác Proposed khác Agreed khác Blocked.** Mỗi trạng thái có nghĩa nghiệp vụ riêng.
6. **Unknown là kết luận hợp lệ.** Owner/date/provider không được đoán; source missing buộc review.
7. **Candidate knowledge ≠ verified fact.** Không dùng AI utility như con dấu tổ chức.
8. **Regression và repeatability quan trọng hơn demo đẹp.** Tốt case sửa mà hỏng D01/H01 thì vẫn NO-GO.

### 12.2. Các câu hỏi tự kiểm tra

1. Vì sao cần resolver ngoài extractor? Giải thích D01 và H01.
2. Phân biệt `meeting_status`, `execution_status`, `review_status` bằng D03.
3. Khi nào hủy task mà vẫn giữ owner lịch sử? Khi nào owner phải null?
4. Vì sao LC01 là false commitment dù có source ID?
5. Stage 1 guard yêu cầu điều kiện nào để không xóa customer requirement?
6. “Chưa chọn vendor” không phủ định “chốt B” vì sao?
7. Tại sao Stage 2 có recovery mà verifier cũ không cứu H03?
8. Stage 2 được phép khôi phục những kind/event_type nào và cấm gì?
9. “Hay hạn thứ Tư?” so với “Chốt hạn thứ Tư” khác nhau về chứng minh field due thế nào?
10. Stage 3 dán `reusable_candidate` đã biến lời nói thành tri thức được tổ chức xác thực chưa?
11. Replay chứng minh gì và không chứng minh gì?
12. Vì sao B1/B2/C1/C2 không được promote dù một số ca tốt hơn?
13. Tại sao HTTP 400 chưa đủ chứng minh model kém với transcript dài?
14. Một phép so sánh M2 vs M3 công bằng phải khóa những biến nào?

### 12.3. Trả lời phỏng vấn mẫu

**Hỏi: Điểm yếu kỹ thuật nhất của M2?**

> “Pipeline đã biểu diễn được quyết định theo thời gian và bằng chứng, nhưng 24 ca tổng hợp cho thấy 20/24 hoàn tất, recall required records gồm lỗi chỉ 23/57 và audit precision 2/10. Tôi tách riêng lỗi vận hành, omission, false commitment và auditor để xác định đúng tầng cần sửa.”

**Hỏi: Đã nâng cấp model nào?**

> “Tôi giữ `openai/gpt-oss-120b`, không giả vờ đã finetune. Tôi sửa kiến trúc quanh LLM: issue-scoped checking, source-backed speech-act guards, bounded omission recovery, field-level evidence validation và knowledge utility. Cách này giúp kiểm tra được các lỗi nghiệp vụ cụ thể mà một prompt chung không đảm bảo.”

**Hỏi: Bạn học được gì từ các nhánh thất bại?**

> “B1/B2/C1/C2 từng làm một số ca tốt lên nhưng lại gây regression D01/H01, lỗi evidence hoặc audit. Tôi giữ baseline A thay vì chọn candidate chỉ đẹp trên pilot, khóa regression cases và đưa ra positive/negative tests trước khi thay code.”

**Hỏi: Vì sao chưa khẳng định M3 đã tốt hơn toàn bộ M2?**

> “197 unit tests chứng minh code logic, còn replay chứng minh cùng event cũ được xử lý khác. Chỉ fresh inference M3 với model/config và dữ liệu cố định, cộng semantic review độc lập, mới chứng minh end-to-end performance. Tôi phân biệt các tầng bằng chứng để không biến đánh giá kỹ thuật thành quảng cáo.”

### 12.4. Lộ trình ôn lại trong bốn buổi

| Buổi | Đọc gì? | Bài tập |
|---|---|---|
| 1 — M2 kiến trúc/metric | `models.py`, `resolver.py`, [24 cases](DATASET_EVALUATION_RESULTS.md), [8 cases](FINAL_REGRESSION_RESULTS.md) | Tự giải D01/D03/D04/H01 |
| 2 — Thử nghiệm thất bại | [B1/B2](CANDIDATE_B_CORE_REPAIR.md), [C1](CANDIDATE_C1_NARROW_REPAIR.md), [C2](CANDIDATE_C2_SOURCE_REPAIR.md) | Nói được vì sao không promote từng bản |
| 3 — M3 Stage 0–2 | [Stage 0.5](MISSION3_STAGE_05_BASELINE.md), [Stage 1](MISSION3_STAGE1_RESULTS.md), [Stage 2](MISSION3_STAGE2_RESULTS.md), `verifier.py`, `auditor.py`, `completeness.py` | Trace LC01/LC02/H03 theo line evidence |
| 4 — M3 Stage 3/Evaluation | [Stage 3](MISSION3_STAGE3_RESULTS.md), `information_utility.py`, `frontend/review.js`, replay JSON | Trình bày K01, phân biệt [A/B/C] |

---

## 13. NGUỒN, GIT, TÁI LẬP VÀ QUY TẮC CẬP NHẬT

### 13.1. Các file và tag cần giữ nguyên

| Vai trò | Đường dẫn/commit |
|---|---|
| M2 nộp | Git tag `submission-a-ui-v2-20261015` → `439f672` |
| M2 AI baseline | Git tag `baseline-a-20261014` → `4aecdc9` |
| M2 chạy local độc lập | `tmp/m2-submission`, detached worktree |
| M2 full dataset | [DATASET_EVALUATION_RESULTS.md](DATASET_EVALUATION_RESULTS.md) |
| M2 final regression | [FINAL_REGRESSION_RESULTS.md](FINAL_REGRESSION_RESULTS.md) |
| M3 frozen data/labels | `datasets/mission3_before_after_v1.json`, `datasets/mission3_before_after_labels_v1.json` |
| Frozen SHA/protocol | [frozen_manifest_v1.json](evaluation/mission3/frozen_manifest_v1.json) |
| M2 hosted Before raw | [m2_remote_baseline_v1.json](evaluation/mission3/m2_remote_baseline_v1.json) |
| M2 Before human/assistant review | [m2_remote_review_v1.json](evaluation/mission3/m2_remote_review_v1.json) |
| Stage 1 | [Báo cáo](MISSION3_STAGE1_RESULTS.md), [replay 8](evaluation/mission3/m3_stage1_replay_eight_v3.json) |
| Stage 2 | [Báo cáo](MISSION3_STAGE2_RESULTS.md), [replay 8](evaluation/mission3/m3_stage2_replay_eight_v3.json) |
| Stage 3 | [Báo cáo](MISSION3_STAGE3_RESULTS.md), [replay 4](evaluation/mission3/m3_stage3_replay_four_v2.json) |
| Commit Stage 0 / 0.5 / 1 / 2 / 3 | `7663f2e` / `fe0d2ce` / `3a2ad24` / `086fee0` / `4a91ca5` |
| M3 phát triển | `mission3/improvement-20261021` |
| Production tại mốc | `main` + Vercel/Render vẫn M2, M3 chưa merge |

### 13.2. Chính sách ghi tiếp sau này

Sau mỗi Stage mới, phải thêm mục **không ghi đè bằng chứng cũ**:
- Timestamp, branch, commit SHA, model và config.
- Giả thuyết kỹ thuật *trước thử*; ca mục tiêu và regression cases.
- Dataset/gold và hash, development vs holdout.
- Raw provider output *kể cả failures*, retry/token/API time, review.
- Đánh giá per-case, per-field, precision/recall nếu mẫu số hợp lệ.
- GO/NO-GO và lý do; nếu thất bại thì bài học nào buộc chuyển hướng.
- Nhãn rõ [A/B/C/D] với bất kỳ số liệu nào.
- Nếu phát hiện nhầm lẫn trong lịch sử, thêm **correction/addendum** có ngày; không lén sửa kết quả gốc.

### 13.3. Kết luận học tập

**M2 không thất bại toàn bộ:** kiến trúc temporal, evidence và human review rất đáng giữ. M2 yếu ở completeness, false speech-act commitments, audit false positives, trust semantics và vận hành transcript dài. Những candidate M2 không vượt gate buộc ta học cách bảo toàn baseline và sửa có nguồn. **M3 Stage 1** xử lý false commitment/audit, **Stage 2** khôi phục một số thiếu hụt và củng cố evidence, **Stage 3** phân biệt utility tri thức mà không tự phê duyệt. **Còn thiếu:** fresh M3 LLM Before/After, long/raw/ASR/injection, CR chính thức và release.

> **Checklist tư duy trước mỗi patch:** Lỗi này đã được đo chưa? Thuộc extractor/resolver/verifier/auditor/UI? Giả thuyết nào giải thích? Bằng chứng nào đủ? Case trước đây đúng nào dễ bị hỏng? Có positive và negative controls? Đây là LLM thật hay replay? Có đủ cơ sở merge production chưa?

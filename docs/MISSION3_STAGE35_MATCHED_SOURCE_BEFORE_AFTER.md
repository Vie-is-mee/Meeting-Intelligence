# Stage 3.5 — Source-attested Before / After: M2 submitted vs M3 run 4

> **Mốc nghiên cứu:** 22/10/2026 (ICT). **Bằng chứng [A]: LLM/Groq thật**, KHÔNG phải replay hoặc unit test. Đây là *development-set comparison*, nhãn tổng hợp và đánh giá nội bộ, **không phải independent blind benchmark**.
>
> Source M2 **chính xác**: tag `submission-a-ui-v2-20261015` → `439f672a3204238100158570ebcf80f0551b85fd`. Source M3 trong cột After **chính xác**: `c443647f9a05eb967437544be9bc588d0f85a3a5`, trước sửa owner-audit / D01 tiếp theo. Không gộp các commit mới vào cùng kết quả.

## 1. Vì sao phải chạy thêm M2 local?

Bản Before Stage 0.5 lấy từ Render deployment M2 nhưng API không trả commit SHA. Vì vậy nó chỉ là *hosted deployed-M2*, không phải phép chứng minh chính xác trên một commit nguồn cụ thể.

Bước này đã chạy lại **chính source M2 đã nộp bằng Groq trên local**, nạp credentials riêng tư từ root `.env` vào process (không chép khóa vào M2 worktree và không đưa lên GitHub). Bốn transcript frozen được giữ nguyên; nhãn không gửi cho model.

**Hai bộ Before đều được lưu, không chọn bộ thuận lợi hơn:**
- Hosted M2 Stage 0.5: `docs/evaluation/mission3/m2_remote_baseline_v1.json` (source SHA không được backend chứng thực).
- Exact-tag local M2: `docs/evaluation/mission3/m2_exact_tag_four_case_local_run1.json` + ba file thành phần, source và từng module SHA có trong manifest.

## 2. Cấu hình và vận hành

| Tiêu chí | Exact-tag M2 local | M3 run 4 local |
|---|---|---|
| Commit nguồn | `439f672` | `c443647` |
| Model | `openai/gpt-oss-120b` | `openai/gpt-oss-120b` |
| Temperature | 0.6 | 0.6 |
| Reasoning | low | low |
| Extraction budget | 2.560 tokens | 2.560 tokens |
| Audit budget | 1.024 tokens | 1.024 tokens |
| Audit | on | on |
| API retries | 0 | 0 |
| Hoàn tất pipeline | **4/4** | **4/4** |
| Calls | **8** | **8** |
| Tokens provider báo | **17.771** | **19.064** |

Cùng cấu hình không đồng nghĩa cùng token budget sử dụng hoặc cùng random generation, và các lần sinh không chung seed/stream. Bốn ca đều là synthetic development, không chứng minh generalization hay statistical significance.

## 3. M2 (source đã nộp) → M3 run 4: quan sát trực tiếp từng ca

| Case | Exact-tag M2 local — Before [A] | M3 run 4 — After [A] | Required strict outcome |
|---|---|---|---|
| **E01** | Chỉ xuất `action/cancelled` Lan; **bỏ sót customer CSV request** và alternative open; auditor báo sai rằng lý do hủy giấy phép phải là condition | CSV `request/recorded`, task `action/cancelled`, alternative `decision/open`; không proposal/issue thừa, nhưng auditor báo sai về owner-source L002/L003 | **1/2 → 2/2** |
| **E02** | Đúng 1 cancelled action, owner lịch sử Lan, không request clone, audit clean | Tiếp tục đúng cancelled action; audit clean | **1/1 → 1/1** |
| **R01** | Chỉ có method-B `agreed/blocked`, **thiếu independent vendor open**; verifier warning phủ định chéo issue và audit warning | Có method-B `agreed/blocked` và vendor `open`, audit clean, nguồn condition đúng | **1/2 → 2/2** |
| **K01** | Đúng task tải, hai knowledge còn `unverified`; library choice chỉ `proposed`, chưa utility | Đúng task tải, practice `reusable_candidate`/unverified, rumor `needs_verification`, library choice `open` | **1/3 → 2/3** |

**Lưu ý K01:** frozen required item mong §knowledge/recorded§ nhưng hệ thống M3 giữ `knowledge/unverified` để tránh tự xác nhận tri thức. Đây là độ lệch nhãn strict, không được âm thầm sửa gold; utility riêng của M3 không được tính như trích xuất sự thật đã được xác minh.

### 3.1. Tổng số tạm tính từ review nội bộ (không phải benchmark độc lập)

| Metric trên **4 ca** | M2 local exact-tag | M3 run4 |
|---|---:|---:|
| Pipeline complete | 4/4 | 4/4 |
| Required strict semantic matches | **4/8** | **7/8** |
| Core cases satisfied | **1/4** | **3/4** |
| Full clean cases (core + no problematic audit/extras) | **1/4** | **2/4** |
| Utility field & safe triage | Chưa có | Có ở K01 |

**Kết luận hợp lệ:** Trên **bộ bốn case phát triển đã biết**, lượt sampled của M3 run4 cho nội dung sát nhãn hơn lượt M2 exact-tag mới, nhưng M3 vẫn có false audit ở E01. Không được diễn giải 4/8 → 7/8 thành “accuracy sản phẩm tăng 75%” hoặc benchmark đại diện cho người dùng thực.

**Đối chiếu với BEFORE hosted M2 trước đó:** hosted M2 từng **6/8 required, 3/4 core, 1/4 full**; local exact-tag lần này **4/8, 1/4 core, 1/4 full**. Hai lần M2 khác nhau là bằng chứng model sampling variance; giữ lại cả hai, không chọn điểm thấp hơn để làm đẹp M3.

## 4. Bốn lượt fresh M3 khác nhau — sự cải tiến và tính bất định

| Lượt | Source | Completion | Full-clean cases nội bộ | Lỗi tiêu biểu |
|---|---|---|---:|---|
| Run 1 | `0e00f9b` | 4/4 | 1/4 | E01 proposal giả; R01 false audit |
| Run 2 | `9d9082c` | 4/4 | 2/4 | E01 issue/request clone và missing alternative |
| Run 3 | `549a145` | 4/4 | 2/4 | E01 sạch nhưng R01 null-condition audit |
| Run 4 | `c443647` | 4/4 | 2/4 | R01 sạch nhưng E01 owner audit false-positive |

Không có một lượt nào chứng minh **toàn bộ bốn ca full clean đồng thời**. Thành công cục bộ của case này không được chọn cùng case ở lượt khác để báo 4/4.

## 5. Phân tách kỹ thuật: đã sửa được gì, còn gì?

- Stage 1–3 sửa các cơ chế lifecycle, missing request/open choice và utility. Fresh M3 xác nhận nhiều mục tốt lên so với exact-tag M2 ở các lượt cụ thể.
- R01 `condition=null` + field evidence được xử lý trong source `c443647`.
- Sau run 4, một patch độc lập `031aee2` lọc auditor false owner finding **chỉ khi có named assignment và first-person acceptance**, negative test refusal/bad owner, **219/219 Python tests**. **Chưa phải fresh Groq end-to-end xác nhận sau patch.**
- Fresh old regression trên `c443647`: **D01 FAIL; D03/D04/H01 PASS**, ghi ở [MISSION3_STAGE35_FRESH_RUN4_AND_REGRESSION.md](MISSION3_STAGE35_FRESH_RUN4_AND_REGRESSION.md). D01 là hard gate và **phải sửa/đánh giá lại**, không merge.
- Những ứng viên sửa D01 ở các commit tiếp theo phải kiểm tra riêng cả four-case và regression. Không thay đổi kết quả của những run đã khóa.

## 6. Reproducibility & audit trail

Source of truth:
- `docs/evaluation/mission3/m2_exact_tag_E02_local_run1.json`
- `docs/evaluation/mission3/m2_exact_tag_E01_R01_local_run1.json`
- `docs/evaluation/mission3/m2_exact_tag_K01_local_run1.json`
- `docs/evaluation/mission3/m2_exact_tag_four_case_local_run1.json` (merge chỉ khi cùng M2 SHA, model, config, gold/data và đủ case; error vẫn giữ)
- `docs/evaluation/mission3/m3_fresh_full_run4.json` + four case original outputs
- `scripts/merge_mission2_local_baseline.py` để tái lập cách ghép; script từ chối ghi đè output.
- Original gold `datasets/mission3_before_after_labels_v1.json`, hashes ở `docs/evaluation/mission3/frozen_manifest_v1.json`.

**Nhật ký phương pháp:** Sau mỗi lần sửa, bắt buộc ghi commit, phạm vi tests, provider outputs và positive/negative cases. Lượt này hoàn thành một **source-attested before/after comparison**, nhưng **không** hoàn thành điều kiện release: phải giải quyết D01, audit E01, official CR, long/raw và thử nghiệm độc lập.

> **GO/NO-GO:** GO với **bằng chứng đã được lưu và phép đối chiếu nguồn xác định**; NO-GO với release/merge `main` cho đến khi vượt hồi quy trên source mới.

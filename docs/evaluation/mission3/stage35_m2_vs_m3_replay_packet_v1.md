# Stage 3.5 — Before/After evidence packet (không tự chấm ngữ nghĩa)

**Evidence mode:** \`ARCHIVED_M2_EVENT_REPLAY_ONLY__NO_FRESH_M3_INFERENCE\`.
**Report UTC:** 2026-10-21T15:25:13.241638+00:00

**CẢNH BÁO:** M2 Before là LLM API thật trên hosted deployment nhưng source SHA của Render chưa được xác nhận. Bản M3 ở packet này chỉ là replay sự kiện LLM M2 đã lưu; KHÔNG được nói đây là kết quả Groq M3 mới.

**M2 original:** \`docs\evaluation\mission3\m2_remote_baseline_v1.json\` SHA-256 \`0564914e3dbc6bee9dc28f4f62aada3ec3b6eb380bf4d6fed9ad13237df49f8d\`.
**M3 compared:** \`docs\evaluation\mission3\m3_stage3_replay_four_v2.json\` SHA-256 \`21de5bf8506886ce2e9b8cc65fc759d76862443b743b1599510590d51400d79c\`.
**Data sealed input:** \`d01ea985df426a4e2fc9360056838122d22773a71303fcf3c3b5cc5fe8926852\`.
**Data sealed labels:** \`464045dc9216a93776da6a9b2f1ede667c15fbd5d7c9a86ce5448edb9a12daf6\`.

## 1. Machine-grounded observations (NOT semantic accuracy)

| Case | M2 hosted Before | M3 archived-event replay | Review |
|---|---|---|---|
| M3-E01 | COMPLETED: 2 records / 1 audit | REPLAY_ONLY: 2 records / 0 audit | **NOT SEMANTICALLY REVIEWED** |
| M3-E02 | COMPLETED: 1 records / 0 audit | REPLAY_ONLY: 1 records / 0 audit | **NOT SEMANTICALLY REVIEWED** |
| M3-R01 | COMPLETED: 2 records / 0 audit | REPLAY_ONLY: 2 records / 0 audit | **NOT SEMANTICALLY REVIEWED** |
| M3-K01 | COMPLETED: 4 records / 0 audit | REPLAY_ONLY: 4 records / 0 audit | **NOT SEMANTICALLY REVIEWED** |

## 2. Per-case original output and M3 result

### M3-E01

**M2 Before — hosted Groq output (real provider run, source SHA not attested):**

- B0: request / recorded / not_applicable — Khách hàng yêu cầu xuất file CSV trong trang báo cáo. (owner: (chưa có); due: (chưa có); utility: (chưa có)); source: ['L001']
- B1: action / cancelled / unknown — Thử thư viện X để làm tính năng xuất CSV. (owner: Lan; due: (chưa có); utility: (chưa có)); source: ['L002', 'L004']

**M3 Replay-only:**

- A0: request / recorded / not_applicable — Khách hàng yêu cầu xuất file CSV trong trang báo cáo. (owner: (chưa có); due: (chưa có); utility: current_work); source: ['L001']
- A1: action / cancelled / unknown — Thử thư viện X để làm tính năng xuất CSV. (owner: Lan; due: (chưa có); utility: historical_context); source: ['L002']

**Frozen required outcomes:**

- \`csv_requirement\` (request, status \`recorded\`) — Customer's CSV export requirement remains — source ['L001', 'L005']
- \`library_x_trial\` (action, status \`cancelled\`) — Lan's trial of library X cancelled — source ['L002', 'L003', 'L004']

**Forbidden outcomes (must check manually):**

- independent active request solely from L002
- active library X trial
- library X agreed implementation
- invented owner/due
- cancellation of CSV business requirement

**Manual adjudication — REQUIRED BEFORE SCORES:**
- [ ] One-to-one match of each required label to a record, correct business meaning and kind
- [ ] Latest state / conditions / owner / due accurate
- [ ] Per-field evidence genuinely entails values, including important late corrections
- [ ] No false action/decision or forbidden outcomes
- [ ] Auditor/verifier warnings judged individually (false positives and missed true positives)
- [ ] Case-specific core verdict: **UNREVIEWED**
- [ ] Case-specific full verdict: **UNREVIEWED**

### M3-E02

**M2 Before — hosted Groq output (real provider run, source SHA not attested):**

- B0: action / cancelled / unknown — thử thư viện X để tạo CSV mẫu nội bộ (owner: Lan; due: (chưa có); utility: (chưa có)); source: ['L001', 'L003']

**M3 Replay-only:**

- A0: action / cancelled / unknown — thử thư viện X để tạo CSV mẫu nội bộ (owner: Lan; due: (chưa có); utility: historical_context); source: ['L001']

**Frozen required outcomes:**

- \`library_x_internal_sample\` (action, status \`cancelled\`) — Internal sample library X trial cancelled — source ['L001', 'L002', 'L003']

**Forbidden outcomes (must check manually):**

- separate active request based solely on assignment
- active trial
- replacement task
- approved decision

**Manual adjudication — REQUIRED BEFORE SCORES:**
- [ ] One-to-one match of each required label to a record, correct business meaning and kind
- [ ] Latest state / conditions / owner / due accurate
- [ ] Per-field evidence genuinely entails values, including important late corrections
- [ ] No false action/decision or forbidden outcomes
- [ ] Auditor/verifier warnings judged individually (false positives and missed true positives)
- [ ] Case-specific core verdict: **UNREVIEWED**
- [ ] Case-specific full verdict: **UNREVIEWED**

### M3-R01

**M2 Before — hosted Groq output (real provider run, source SHA not attested):**

- B0: decision / agreed / blocked — phương án B cho bản thử nghiệm (owner: (chưa có); due: (chưa có); utility: (chưa có)); source: ['L001', 'L002', 'L003', 'L004']
- B1: decision / open / unknown — chưa chốt nhà cung cấp (owner: (chưa có); due: (chưa có); utility: (chưa có)); source: ['L005']

**M3 Replay-only:**

- A0: decision / agreed / blocked — phương án B cho bản thử nghiệm (owner: (chưa có); due: (chưa có); utility: current_work); source: ['L003']
- A1: decision / open / unknown — chưa chốt nhà cung cấp (owner: (chưa có); due: (chưa có); utility: current_work); source: ['L005']

**Frozen required outcomes:**

- \`pilot_b\` (decision, status \`agreed\`) — B was agreed for a pilot only, cannot roll out to customer until legal approval — source ['L003', 'L004']
- \`vendor_unselected\` (decision, status \`open\`) — Vendor choice not made — source ['L005']

**Forbidden outcomes (must check manually):**

- pilot choice B reopened due to L005
- B unconditional customer rollout approved
- vendor B approved
- A remains final

**Manual adjudication — REQUIRED BEFORE SCORES:**
- [ ] One-to-one match of each required label to a record, correct business meaning and kind
- [ ] Latest state / conditions / owner / due accurate
- [ ] Per-field evidence genuinely entails values, including important late corrections
- [ ] No false action/decision or forbidden outcomes
- [ ] Auditor/verifier warnings judged individually (false positives and missed true positives)
- [ ] Case-specific core verdict: **UNREVIEWED**
- [ ] Case-specific full verdict: **UNREVIEWED**

### M3-K01

**M2 Before — hosted Groq output (real provider run, source SHA not attested):**

- B0: action / assigned / unknown — chạy kiểm thử tải (owner: Lan; due: thứ Sáu; utility: (chưa có)); source: ['L001']
- B1: knowledge / unverified / not_applicable — cần dùng idempotency key để hạn chế ghi trùng khi retry request (owner: (chưa có); due: (chưa có); utility: (chưa có)); source: ['L002']
- B2: knowledge / unverified / not_applicable — thư viện Y luôn nhanh hơn X, nhưng chưa có benchmark xác minh (owner: (chưa có); due: (chưa có); utility: (chưa có)); source: ['L003']
- B3: decision / proposed / unknown — giữ việc benchmark Y và X cho cuộc họp sau, hôm nay chưa chọn thư viện (owner: (chưa có); due: (chưa có); utility: (chưa có)); source: ['L004']

**M3 Replay-only:**

- A0: action / assigned / unknown — chạy kiểm thử tải (owner: Lan; due: thứ Sáu; utility: current_work); source: ['L001']
- A1: knowledge / unverified / not_applicable — cần dùng idempotency key để hạn chế ghi trùng khi retry request (owner: (chưa có); due: (chưa có); utility: reusable_candidate); source: ['L002']
- A2: knowledge / unverified / not_applicable — thư viện Y luôn nhanh hơn X, nhưng chưa có benchmark xác minh (owner: (chưa có); due: (chưa có); utility: needs_verification); source: ['L003']
- A3: decision / open / unknown — giữ việc benchmark Y và X cho cuộc họp sau, hôm nay chưa chọn thư viện (owner: (chưa có); due: (chưa có); utility: current_work); source: ['L004']

**Frozen required outcomes:**

- \`load_test\` (action, status \`assigned\`) — Lan will perform load test by Friday — source ['L001']
- \`idempotency_practice\` (knowledge, status \`recorded\`) — Using idempotency keys during retries helps avoid duplicated writes, stated as past practice — source ['L002']
- \`library_unselected\` (decision, status \`open\`) — No winning library chosen for Y versus X — source ['L004']

**Forbidden outcomes (must check manually):**

- asserting Y faster than X as confirmed fact
- Y or X agreed winner
- fabricated benchmark
- automatically published verified knowledge

**Manual adjudication — REQUIRED BEFORE SCORES:**
- [ ] One-to-one match of each required label to a record, correct business meaning and kind
- [ ] Latest state / conditions / owner / due accurate
- [ ] Per-field evidence genuinely entails values, including important late corrections
- [ ] No false action/decision or forbidden outcomes
- [ ] Auditor/verifier warnings judged individually (false positives and missed true positives)
- [ ] Case-specific core verdict: **UNREVIEWED**
- [ ] Case-specific full verdict: **UNREVIEWED**

## 3. What is NOT established yet

- This packet cannot measure independent precision/recall or full-case accuracy without a human-adjudicated review.
- If after source is replay, **no newly sampled M3 LLM output exists** in this comparison.
- Synthetic, assistant-labelled examples are known development cases, NOT an independent holdout.
- Use fresh M2 exact-tag local LLM vs fresh M3 local LLM with identical settings for strongest comparison.
- Never merge production before confirming actual M3 end-to-end behavior and Change Request gate.

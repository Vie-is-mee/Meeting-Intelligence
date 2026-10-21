# Mission 3 — Predeclared test design (Stage 0)

**Status:** planned cases with expected labels; no Mission 3 LLM outputs, no M3 pass/fail recorded yet. These are test specifications, not secretly measured results.

## Regression of shipped M2
| ID | Key expectation | M2 historical result | M3 |
|---|---|---|---|
| D01 | A->object storage decision + provider still open | PASS | NOT RUN |
| D03 | agreed design choice but execution blocked by legal approval | PASS | NOT RUN |
| D04 | replaced compound prerequisites, unmet != reopen | PASS | NOT RUN |
| H01 | decision reopened, independent assigned task persists | PASS | NOT RUN |
| H03 | request and relative timing not lost; proposed date not agreed | FAIL | NOT RUN |
| LC01 | cancelled action, no extra request | FAIL | NOT RUN |
| LC02 | CSV requirement remains, cancelled task, replacement open | FAIL | NOT RUN |
| LC03 | cancelled task/history owner, correct audit interpretation | CORE PASS, AUDIT FAIL | NOT RUN |

## M3-E01 — Edge: cancellation with independent business requirement
Transcript to freeze in fixture:
L001 | An | Khách hàng yêu cầu xuất file CSV trong trang báo cáo.
L002 | Bình | Giao Lan thử thư viện X để làm tính năng xuất CSV.
L003 | Lan | Tôi nhận việc thử thư viện X.
L004 | An | Hủy công việc thử thư viện X vì giấy phép không phù hợp.
L005 | Bình | Nhu cầu xuất CSV của khách hàng vẫn giữ nguyên, còn cách làm khác thì chưa chốt.

Expected:
- One `request`: exported CSV business requirement retained and supported L001/L005.
- One `action`: trying library X cancelled; historical assignee Lan may remain, status/source from L004; no active trial.
- Separate `decision` `open` for implementation alternative (if represented) without pretending X has been approved.
- No duplicate active request generated solely from the assignment L002.
- Owner/date not invented.

## M3-E02 — Counterfactual edge: cancellation WITHOUT independent requirement
Transcript:
L001 | Bình | Giao Lan thử thư viện X để tạo CSV mẫu nội bộ.
L002 | Lan | Tôi nhận.
L003 | Bình | Hủy việc thử thư viện X, không cần làm nữa.

Expected: One cancelled action with historical Lan. No independent current business request or approved decision. No speculative replacement.

## M3-R01 — Old-feature regression: agreed vs blocked vs reopened
Transcript:
L001 | Bình | Ban đầu đề xuất phương án A cho kho dữ liệu.
L002 | Lan | Phương án B phù hợp hơn.
L003 | Bình | Thống nhất phương án B cho bản thử nghiệm.
L004 | An | Chưa được triển khai B cho khách hàng đến khi pháp chế duyệt.
L005 | Bình | Việc chọn nhà cung cấp B chưa bàn đến, chưa chốt nhà cung cấp.

Expected: B is agreed for pilot, execution blocked pending legal approval. Vendor selection open independently; L005 does **not** reopen selection of architecture B. No imaginary legal clearance. Sources L003/L004/L005 reflect distinct fields/issues.

## M3-K01 — Knowledge vs ongoing work
Transcript:
L001 | An | Giao Lan chạy kiểm thử tải vào thứ Sáu.
L002 | Bình | Khi retry request, cần dùng idempotency key để hạn chế ghi trùng. Đây là kinh nghiệm từ lần triển khai trước.
L003 | Chi | Tôi nghe nói thư viện Y luôn nhanh hơn X, nhưng chưa có benchmark xác minh.
L004 | An | Quyết định giữ việc benchmark Y và X cho cuộc họp sau, hôm nay chưa chọn thư viện.

Expected:
- Current assigned action: Lan test load, original time only.
- Reusable **candidate** technical knowledge about idempotency backed by L002; NOT asserted as externally verified company policy.
- Library speed assertion kept uncertain/needs verification or excluded from validated knowledge, no accepted decision based on it.
- Choice of Y vs X is unresolved; no winning library or fabricated benchmark results.
- No automatic publishing to knowledge base.

## M3-L01 — Multiple interleaved topics / late correction
Design controlled >=40 utterance fixture from independently authored neutral filler plus 3 cross-topic changes. Freeze exact text and labels **before** checking candidate. Must show issue grouping across time and late changes. Do not claim created until committed to test fixtures.

## M3-CR01 — External change request
**PENDING** (portal had no assigned CR). When issued: quote verbatim, add its acceptance test before implementation. Do not invent requirement or report test PASS.

## Review protocol for every case
Record: test ID, locked transcript + expected labels, exact code/model/config/input hash, actual raw output, pass/fail for extraction and audit separately, false decisions/actions, missing required records, evidence-level support, lessons learned and known limits. Keep fixture changes/version history and mark any contaminated formerly blind case as development.

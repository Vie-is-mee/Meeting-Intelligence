# Mission 3 — Staging / demo / submission release pack

**Status:** source/configuration prepared and local HTTP smoke passed. **Public staging URL, public UI smoke, public video link and form submission are NOT verified yet.** Do not replace these with the old Mission 2 URLs.

## Staging deployment — separate from production M2

- GitHub repo: https://github.com/Vie-is-mee/Meeting-Intelligence
- Branch: `mission3/improvement-20261021`
- Provision **a NEW service**, NOT the old `meeting-intelligence` service.
- In Render dashboard choose **Blueprint → New Blueprint Instance** for this repo/branch. Set Blueprint path to **`render.m3.staging.yaml`** (not `render.yaml`). This file chooses service `meeting-intelligence-m3-staging`, Python 3.12, branch M3, free plan and disabled auto deploy.
- During setup, set `LLM_API_KEY` as a secret **in Render**, not in GitHub, an email, screenshot or chat. No other credential should be committed. The blueprint declares model/base URL/temperature and `ENABLE_LIVE_API=true`. Disable live API when staging is no longer needed: publicly reachable analysis endpoints may consume provider quota.
- Deploy manually from the M3 branch commit shown in this repo. Set `ALLOWED_ORIGINS` only if a **separate Vercel staging frontend** will call this Render backend. The recommended demo is **Render one-origin**: the Render service serves HTML/CSS/JS and API on the same HTTPS domain, so no Vercel staging setup is necessary to meet the demo requirement.
- Wait for a successful Render deploy (don't assume). Open `https://<ACTUAL-STAGING-HOST>/api/version`; check `mission=M3`, `change_request=C2`, and `source_commit` equals the selected M3 commit. The endpoint additionally reports SHA-256 for core modules.
- Open `https://<ACTUAL-STAGING-HOST>/api/config`; `api_configured` must be `true`. The model should be `openai/gpt-oss-120b` and provider hostname `api.groq.com`.
- Run from the checked-out M3 project root:
  ```powershell
  python -X utf8 scripts/smoke_m3_staging.py --base-url https://<ACTUAL-STAGING-HOST> --require-sha <RELEASE-COMMIT>
  python -X utf8 scripts/smoke_m3_staging.py --base-url https://<ACTUAL-STAGING-HOST> --require-sha <RELEASE-COMMIT> --live --out docs/evaluation/mission3/m3_public_staging_smoke_v1.json
  ```
- Never use a URL that has not passed the first smoke command as a Mission 3 demo link. `/healthz` alone is insufficient: M2 has it too.

### Manual public website smoke (separate from unit tests)

1. Open the **M3 Render staging URL**; confirm sidebar says *Mission 3 · C2*. Click **Nạp Change Request C2 — action chưa rõ**. Check transcript text and select **LLM API** (not "recorded"/"offline"). Click **Phân tích**.
2. For the one-line C2 utterance, check **action/unverified**, personal owner blank and deadline blank, needs human review; verify source L001 in **Kiểm chứng**. This is **fresh API inference**, not a replay.
3. In **Rà soát & xuất**, do **not** confirm an ambiguous task as actually assigned. Mark **chưa đủ bằng chứng** and verify unconfirmed records cannot appear in CSV as accepted assignments.
4. On a separate synthetic transcript with a named later assignment (Huy), verify owner Huy, `trước thứ Sáu`; verify per-field evidence IDs.
5. Test deliberate confirmation of a non-ambiguous record: choose a valid cited source, enter reviewer name, confirm. Export CSV and JSON; verify CSV contains **only human-confirmed** records, and the JSON includes AI original plus user review history. Refresh/restore from same session and verify history is retained.
6. Never show private `.env`, Render secret configuration, API key or sensitive transcript in the recording.

## Four-minute-thirty video — exact recording plan and sample narration

**00:00–00:35 — Business issue and requirement**
"Ở Mission 2, nhóm xây MVP biến transcript thành quyết định, công việc và những vấn đề có kèm bằng chứng. Nhưng để dữ liệu thực sự dùng được sau họp, một phát biểu chưa rõ không được biến thành trách nhiệm hoặc deadline giả. Yêu cầu mới C2 đưa ví dụ: 'cái này team mình xử lý nhé'. Câu này không nói cá nhân phụ trách hay thời hạn."

**00:35–01:20 — Choice and rationale**
"Chúng tôi chọn reliability-first thay vì làm lại ứng dụng hay thêm nhiều agent. M3 xử lý xuyên suốt bằng event history/resolver, kiểm chứng owner và deadline bằng lời nói gốc, và phân biệt quyết định/chỉ đề xuất/chưa chốt. Nếu nguồn chưa đủ, action vẫn được giữ với trạng thái unverified, yêu cầu người dùng xác nhận."

**01:20–02:30 — Live C2 demo**
[Mở website M3, nhấn nút nạp C2, chọn Groq LLM API, phân tích; nếu provider đang chậm, chuyển sang hiển thị **đầu ra Groq được lưu** và nói rõ.]
"Đây là C2 từ API. Hệ thống giữ phát biểu ở bản ghi cần rà soát, owner và deadline là null, có câu L001 làm bằng chứng. Nó không tự nhận Minh là owner. Khi Huy thực sự nói nhận lỗi thanh toán trước thứ Sáu và được chốt, M3 giữ Huy và mốc **trước** thứ Sáu, không tạo một nhiệm vụ tập thể trùng."

**02:30–03:15 — Evidence, review and exports**
[Chọn record → tab Kiểm chứng, chỉ source từng field; tab Rà soát & xuất; chọn Chưa đủ bằng chứng cho action mơ hồ và minh họa JSON gốc và CSV chỉ bản ghi được xác nhận.]
"Source ID chỉ ra câu nguồn, không phải bảo chứng tự động rằng diễn giải luôn đúng. Người dùng có thể rà soát, từ chối hoặc chỉnh sửa; CSV chính thức chỉ xuất nội dung đã được xác nhận. Bản gốc AI và lịch sử review vẫn được bảo toàn."

**03:15–04:05 — Real Before/After and tests**
[Hiển thị `docs/MISSION3_C2_BEFORE_AFTER_RESULTS.md` và `docs/MISSION3_STAGE5A_FINAL_REGRESSION_GATE.md`.]
"Chúng tôi chạy bốn transcript C2 trên chính M2 đã nộp và M3, cùng Groq, cùng thông số. M2 trong những lần thử này **không bịa owner/deadline**, nhưng từng xem lời cam kết tập thể là decision, hoặc lặp lại assignment. M3 cải thiện cách xử lý câu mơ hồ, tránh cam kết giả nhưng vẫn giữ assignment đã chốt. Mọi test Python và frontend đều đạt; C2-02 còn tranh luận audit, D01 có regression thiếu quyết định chọn nhà cung cấp."

**04:05–04:30 — Trade-offs and limitations**
"Ưu tiên tiếp theo là dữ liệu cuộc họp thật, biến thể diễn đạt và tiếng nói ASR, mô hình liên kết đại từ theo ngữ cảnh dài, cùng cổng human review cho thông tin có hậu quả cao. M3 chưa thể thay con người phê duyệt, nhưng giảm nguy cơ công bố những cam kết chưa đủ nguồn."

**Target runtime:** ~4m30, NEVER above 5m. Record with visible browser URL and version endpoint; upload to an accessible video platform and test link from an incognito/private session before submission.

## Three required form answers — copy-ready Vietnamese

**Câu 1. Sau khi nhận yêu cầu mới, bạn đã ưu tiên thay đổi điều gì và chủ động chưa làm điều gì? Vì sao?**

"Nhóm ưu tiên giảm false commitment: đọc diễn biến theo thời gian, kiểm chứng trách nhiệm/hạn bằng câu nguồn, và xử lý CR C2. Với 'cái này team mình xử lý nhé', AI không được tự suy Minh là người phụ trách hoặc gán deadline. M3 giữ một action chưa xác nhận (unverified), owner/deadline để trống, liên kết L001 và yêu cầu con người rà soát; nếu có lời nhận việc rõ ràng về sau thì cập nhật. Nhóm chủ động không làm lại MVP, không fine-tune/mở thêm agent hay tự động xác nhận tri thức, vì tăng bề mặt lỗi và không trực tiếp giảm rủi ro giao sai việc trong thời hạn ba ngày."

**Câu 2. Thay đổi nào tạo khác biệt lớn nhất, bằng chứng gì cho thấy phiên bản mới tốt hơn?**

"Khác biệt lớn nhất là kiểm chứng quyết định/công việc theo nguồn và trạng thái cuối (source-grounded, risk-aware verification), đặc biệt việc phân biệt ý định tập thể với assignment cá nhân ở C2. Chúng tôi khóa bốn transcript C2, chạy Groq thật trên exact-tag Mission 2 và bản M3 với cùng cấu hình, lưu raw outputs, SHA nguồn, bộ test, cả lượt sai. Ở các lượt này M2 không tự bịa owner/deadline, nhưng có lúc phân loại phát biểu tập thể thành decision/proposed, biến đề xuất ngày thứ Sáu thành request và sinh quyết định lặp lại assignment. M3 ghi câu tập thể thành action/unverified có evidence, giữ owner/deadline null khi chưa chốt; về sau vẫn nhận đúng Huy và hạn 'trước thứ Sáu', bảo toàn owner lịch sử Lan khi task bị hủy. 4/4 ca C2 hoàn tất và đúng các ràng buộc owner/deadline chính, nhưng C2-02 còn hai nhận xét audit; regression D01 còn thiếu một lựa chọn nhà cung cấp mở. Vì vậy chúng tôi chỉ kết luận cải thiện trên bộ ca phát triển này, không nhận là 100% chính xác hoặc một benchmark độc lập."

**Câu 3. Rủi ro/giới hạn lớn nhất khi dùng thật ngày mai, xử lý thế nào?**

"Rủi ro lớn nhất là AI diễn giải sai một câu mơ hồ thành quyết định hoặc trách nhiệm đã được chốt, đặc biệt khi transcript dài, mất dấu câu, đại từ 'cái này' có nhiều đối tượng hoặc ASR sai. Source ID chứng minh chỗ trích, không chứng minh diễn giải đúng. Nhóm sẽ ưu tiên đánh giá trên transcript thật được con người gán nhãn độc lập, đo false-owner/false-deadline và recall của nhiệm vụ có bằng chứng, mở rộng kiểm tra theo ngữ cảnh nhiều lượt nói và kiểm chứng thời gian. Trước khi tạo task/hệ thống nhắc việc hoặc xuất dữ liệu để sử dụng chính thức, các mục chưa chắc chắn phải được đánh dấu cần xác nhận; không tự động xuất như cam kết thật. Tri thức tái sử dụng cũng chỉ là ứng viên chưa được kiểm chứng, không phải chính sách tổ chức."

## Submission links (do not invent)

- **GitHub:** https://github.com/Vie-is-mee/Meeting-Intelligence/tree/mission3/improvement-20261021
- **Demo M3:** [PENDING: actual M3 staging hostname + smoke proof]. **Do NOT submit** https://meeting-intelligence-sable.vercel.app/ as M3 without proving its backend source.
- **Video ≤5min:** [PENDING: real uploaded publicly viewable URL].
- Form: three answers above; submit before deadline and retain confirmation.

## GO / NO-GO

- GO: M3 code, Change Request C2 and 253 Python + 13 frontend tests; local HTTP API/version/source evidence, review/export unit tests.
- NO-GO: public M3 staging availability and public UI click-through, video recording/upload and form submission until verified. Direct user connection to Render/Vercel or user dashboard action is required; no Render/Vercel API token or deployment CLI was present in the local process.

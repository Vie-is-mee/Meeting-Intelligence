# Trí tuệ cuộc họp — Mission 2 / Stage 2

GitHub: [Vie-is-mee/Meeting-Intelligence](https://github.com/Vie-is-mee/Meeting-Intelligence).

## Xem demo ngay

**Không cần cài requirements hoặc key để xem demo:** mở [frontend/index.html](frontend/index.html) bằng Go Live. Mặc định hiển thị D01: từ đề xuất lưu trên máy chủ sang chốt object storage. Chọn 8 case để xem kết quả thật đã lưu, kể cả lỗi, kèm evidence/lịch sử/JSON và đánh giá. Đây là xem lại, không phải phân tích mới.

Hoặc nhấp đúp `run_demo.cmd`, mở `http://127.0.0.1:5501` để xem bản tĩnh bằng Python có sẵn. Nếu `web.py` đang chạy từ phiên bản cũ, dừng và chạy lại để tải route demo mới.

**Rà soát để dùng tiếp:** tại bước Rà soát & xuất, đọc kết quả cạnh câu nguồn rồi chọn **Đúng / Sai / Chưa đủ bằng chứng**. Chỉ mở ô sửa khi chọn Sai; không cần nhập lại kết quả đúng. Lưu phiên gần nhất trên trình duyệt hoặc tải JSON kèm lịch sử. CSV chỉ chứa bản đã xác nhận. AI gốc và điểm kiểm thử không đổi; xác nhận không phải phê duyệt tổ chức. Xem [hướng dẫn và giới hạn](docs/HUMAN_REVIEW.md).

**Bố cục website:** chuyển giữa **Phân tích → Kiểm chứng → Rà soát & xuất** bằng thanh bên (desktop) hoặc thanh bước (điện thoại). Mỗi màn chỉ hiển thị phần liên quan. Kiểm chứng có ba tab: kết luận/nguồn, diễn biến xử lý và audit. Chuyển màn giữ kết quả, bản ghi đang chọn và nội dung rà soát đang nhập.

**Muốn phân tích mới:** nhấp đúp `run_web.cmd`, mở `http://127.0.0.1:8765`, chuyển sang LLM API. Python cần dependencies trong requirements nếu máy chưa có; key đặt trong `.env`, không gửi ra frontend. Baseline offline là luật hẹp, được ghi nhãn riêng.

**Gói đóng sẵn:** `dist/meeting-intelligence-demo-static.zip` để xem/deploy trang tĩnh sau; `dist/meeting-intelligence-mission2-source.zip` để chia sẻ source không có `.env`. Repo đã công khai; website chưa deploy online. Xem [hướng dẫn](docs/STATIC_DEMO.md), [kịch bản video](docs/DEMO_RUNBOOK.md), [ba câu trả lời và nội dung form](docs/MISSION2_SUBMISSION.md), [kết quả 8 case cùng phiên bản](docs/FINAL_REGRESSION_RESULTS.md).

> **Trạng thái: bản local để kiểm chứng, chưa hoàn tất bài nộp.** Có website nhập transcript, xem bản ghi, lịch sử, evidence và JSON. Đã chạy bộ phát triển T01–T07 bằng Groq thật, ghi nhận cả lỗi API, lỗi nội dung và cảnh báo audit. Kết quả, sửa đổi và giới hạn được ghi tại [LLM_EVALUATION.md](docs/LLM_EVALUATION.md). Offline theo luật và fixture viết tay được phân biệt với model thật. Xem [WEB_STATUS.md](docs/WEB_STATUS.md).

Đã đánh giá thêm dataset 24 transcript bằng Groq thật với prompt và core giữ nguyên: **9 đạt, 11 chưa đạt, 4 lỗi chạy** theo tiêu chí nội dung/trường/evidence/rà soát. Precision bản ghi có căn cứ **37/45**, recall mục bắt buộc end-to-end **23/57**; cả ba transcript dài chưa hoàn thành vì HTTP 400. Xem [báo cáo từng case và metric](docs/DATASET_EVALUATION_RESULTS.md), [định nghĩa/cách chạy](docs/DATASET_EVALUATION.md) và artifact JSON trong `docs/evaluation/dataset_v1_*.json`. Đây là dữ liệu tổng hợp và review cùng trợ lý, chưa được gán nhãn độc lập xác nhận.

Lượt sửa lõi tiếp theo đã xác định mã `json_validate_failed` và giới hạn 8000 TPM, thêm strict schema/cấu hình sinh phù hợp Groq và bảo vệ trạng thái hủy/mở lại khỏi audit. Kiểm chứng có mục tiêu: **4/6 chạy đủ pipeline + audit, 2/6 dừng an toàn**, còn lỗi nghiệp vụ; đây chưa phải điểm mới của toàn dataset. Xem [báo cáo sửa lõi lượt 1](docs/CORE_REPAIR_ROUND1.md).

Lượt sửa tiếp theo bổ sung cập nhật điều kiện/hạn, kiểm tra phủ định owner và giữ dữ liệu nguyên văn có nguồn. **95/95 test phần mềm đạt**; thử prompt mới có cả cải thiện và regression, chưa có điểm accuracy mới cho toàn dataset. Xem [báo cáo sửa lõi lượt 2](docs/CORE_REPAIR_ROUND2.md).

Lượt sửa 3 bổ sung checklist giữ phạm vi/kết luận cuối và hướng dẫn audit điều kiện lịch sử. **95/95 test phần mềm đạt**; D03 cải thiện, D04 giữ đúng, D06 còn bản ghi thừa. H01 chỉ kiểm chứng được extraction; H03 và một số bước audit bị HTTP 429, chưa xác nhận cải thiện. Xem [báo cáo sửa lõi lượt 3](docs/CORE_REPAIR_ROUND3.md). Không có điểm accuracy mới toàn dataset.

Lượt sửa 4 đã kiểm chứng bổ sung H03 và audit H01 bằng API cho prompt lượt 3. Prompt vòng đời công việc mới giảm decision thừa ở D06 nhưng request thừa còn tồn tại; verifier đánh dấu cần rà soát, không tự xóa dữ liệu. **100/100 test phần mềm đạt**; audit D06 và các phản ví dụ mới còn chưa kiểm chứng qua API vì HTTP 429. Xem [báo cáo sửa lõi lượt 4](docs/CORE_REPAIR_ROUND4.md).

Lượt 5 xác định API bị giới hạn **TPD** và sửa lỗi resolver bỏ qua clear_fields khi hủy việc và bỏ hạn trong cùng sự kiện. **105/105 test phần mềm đạt**; chưa có đánh giá API đầy đủ cho core mới. Xem [báo cáo lượt 5](docs/CORE_REPAIR_ROUND5.md) và [bảng tình huống thực tế để chọn demo](docs/MISSION2_TEST_CASES.md).

**Hồi quy cố định mới nhất đã hoàn tất:** 8/8 case chạy đủ extraction + audit cùng phiên bản; **4 đạt, 4 chưa đạt** khi tính cả cảnh báo audit sai (dữ liệu lõi đạt ở 5/8 case). Đây chưa phải điểm toàn dataset. Xem [kết quả hồi quy](docs/FINAL_REGRESSION_RESULTS.md).

## Mở website local

Để chốt phiên bản demo, xem [bộ hồi quy cố định 8 case và lệnh chạy](docs/FINAL_REGRESSION_PLAN.md). Bộ này đã chạy đủ ở lượt mới nhất; xem báo cáo kết quả ở trên. File input chuẩn bị vẫn không phải kết quả kiểm thử.

Trong terminal tại thư mục `meeting-intelligence-m2-stage2`:

```powershell
python -m pip install -r requirements.txt
python -X utf8 web.py
```

Mở **http://127.0.0.1:8765** trên trình duyệt. Dừng server bằng Ctrl+C.
Trên máy Windows hiện tại, có thể nhấp đúp `run_web.cmd` để chạy bằng Python
đã cài, không cài thêm thư viện và không phụ thuộc thư mục terminal.
Hoặc từ bất kỳ thư mục PowerShell nào:

```powershell
& 'I:\Python\python.exe' -X utf8 'J:\vi\meeting-intelligence-m2\meeting-intelligence-m2-stage2\web.py'
```

Nếu cổng đang được dùng, chạy `python -X utf8 web.py --port 8766` và mở cổng mới.
Không dùng Go Live để chạy ứng dụng này: giao diện cần backend Python.

**Nếu muốn xem demo không cần backend:** Go Live file `frontend/index.html`.
CSS/JS/JSON dùng đường dẫn tương đối nên hoạt động cả khi dự án nằm trong thư mục con.
Chế độ này xem được 8 kết quả LLM đã lưu và evidence; không phân tích transcript mới.
Muốn chạy thuật toán mới cần mở bằng `web.py` như trên. Nếu Python của bạn đã có
`pydantic` và `python-dotenv`, bỏ qua bước cài requirements, chạy thẳng `web.py`.

- Chọn T03 và **Offline**, nhấn **Phân tích cuộc họp** để xem baseline hoạt động.
- Chọn một bản ghi để đọc lịch sử, nhấn câu trích để xem transcript được tô sáng.
- Xem tab JSON gốc hoặc tải JSON. Chọn tình huống mẫu để đối chiếu kỳ vọng.
- Điền khóa Groq vào `.env`, khởi động lại server, chọn **LLM API** để chạy model thật.
- Tùy chọn audit chỉ áp dụng cho LLM; mỗi lượt thường dùng hai API call khi audit bật.

Python tự nạp `.env` ở thư mục dự án qua `python-dotenv`; biến môi trường sẵn có
được ưu tiên. Không đưa khóa vào HTML/JavaScript. Server chỉ phục vụ các tài nguyên
frontend cố định, không phục vụ `.env` hoặc các tệp Python.
Đây là công cụ local, chưa phải bản triển khai production/online.

Đợt rà soát lõi ngày 12/10/2026 bổ sung kiểm thử hồi quy cho thứ tự thay đổi,
phân công, bằng chứng từng trường, audit và bộ chấm. Chi tiết:
[CORE_REVIEW.md](docs/CORE_REVIEW.md). Không bổ sung UI trong đợt này.

## Cấu hình Groq để đánh giá LLM thật

Adapter hiện dùng giao thức tương thích với Groq; chưa cần cài SDK riêng.
Cấu hình đề xuất để thử trước, **chưa phải model đã chứng minh đạt chất lượng**:

```powershell
$env:LLM_BASE_URL = 'https://api.groq.com/openai/v1'
$env:LLM_MODEL = 'openai/gpt-oss-120b'
$env:LLM_JSON_MODE = 'true'
# Đặt LLM_API_KEY bằng khóa Groq riêng trên máy; không gửi khóa vào chat/repo.
python -X utf8 cli.py samples/T03.txt --engine llm_api --audit on --save results/T03_groq.json
python -X utf8 scripts/run_scenarios.py --engine llm_api --ids T01 T02 T03 T04 T05 T06 T07 --audit on --call-interval 45 --out results/groq_audit_on.json
```

Sao chép `.env.example` thành `.env` và điền khóa riêng. Ứng dụng tự đọc file này;
biến môi trường được ưu tiên nếu đã cấu hình. Khởi động lại server sau khi sửa `.env`.
Free tier bị giới hạn cả request và token; hai lượt trích xuất/audit cùng dùng quota.
Khi gặp `429`, client tôn trọng `Retry-After` dạng số giây, chờ tối đa 60 giây
cho mỗi lần thử lại; thời gian chờ lớn hơn trả lỗi để chạy lại sau.
Không tự hạ model hoặc chuyển provider khi gặp lỗi.

Tài liệu chính thức: [kết nối Groq](https://console.groq.com/docs/openai),
[model](https://console.groq.com/docs/models),
[hạn mức](https://console.groq.com/docs/rate-limits).
Kiểm tra hạn mức thực tế trong tài khoản trước khi chạy hàng loạt.

## Mục tiêu

Transcript → trích sự kiện có bằng chứng → gom sự kiện cùng vấn đề → hiểu các lần đổi/chốt/mở lại → bản ghi trạng thái cuối.

Khác biệt quan trọng: `agreed` là **đã thống nhất trong cuộc họp**, `blocked` là **chưa thể triển khai**, `reopened` là **kết luận đã bị mở lại**. Đây là ba khái niệm khác nhau. `authority_status=unknown` cho đến khi kiểm tra được quyền thực tế.

## Cài đặt (Python 3.10+)

```bash
python -m venv .venv
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
```

## Demo offline KHÔNG cần API key (chỉ là baseline theo luật)

```bash
python cli.py samples/T02.txt --engine offline_rules
python cli.py samples/T03.txt --engine offline_rules
python cli.py samples/T04.txt --engine offline_rules
python scripts/run_scenarios.py --engine offline_rules --ids T02 T03 T04 --out results/offline.json
```

**Không coi offline baseline là năng lực AI:** nó chỉ nhận diện một số mẫu câu quyết định tiếng Việt; không đọc được mọi trường hợp và chưa trích đủ các loại thông tin.

## Chạy bằng LLM API thực

Ứng dụng dùng endpoint tương thích OpenAI **Chat Completions**. Đặt ba biến môi trường trên máy hoặc hạ tầng triển khai (không commit chúng vào GitHub):

```bash
# Windows PowerShell — ví dụ, thay bằng cấu hình thực:
$env:LLM_API_KEY="your-secret"
$env:LLM_BASE_URL="https://your-provider.example/v1"
$env:LLM_MODEL="your-model"
python cli.py samples/T02.txt --engine llm_api
```

Với Linux/macOS dùng `export LLM_API_KEY=...` tương tự, hoặc cấu hình `.env` được nạp tự động. API hỗ trợ JSON mode (`response_format: json_object`) là yêu cầu của adapter hiện tại; một số nhà cung cấp cần chỉnh client tương thích trước khi chạy.

Để chạy 7 ca với LLM đã cấu hình:

```bash
python scripts/run_scenarios.py --engine llm_api --ids T01 T02 T03 T04 T05 T06 T07 --out results/llm.json
```

Kết quả chạy LLM mới được tính là kiểm thử mô hình thật. Nếu thiếu cấu hình hoặc gọi lỗi, script báo ERROR, **không điền PASS giả**. Dữ liệu `samples/expected` là đáp án kỳ vọng, tuyệt đối không được nạp vào prompt dự đoán.

## Kiến trúc

- `parser.py`: giữ câu nói gốc, chuẩn hóa thành mã `L001...`, chấp nhận thiếu người nói/thời gian.
- `models.py`: kiểu dữ liệu Pydantic.
- `llm_client.py`: API trung lập nhà cung cấp, yêu cầu JSON; khóa chỉ nằm phía máy chủ.
- `extractor.py`: LLM trích **sự kiện**, không nhảy thẳng sang quyết định cuối.
- `resolver.py`: nhóm theo `kind + issue_key`, cập nhật trạng thái theo thứ tự sự kiện.
- `verifier.py`: kiểm tra mã câu nguồn, dấu hiệu người/hạn không được hỗ trợ, cờ phủ định xuất hiện sau; không tuyên bố kiểm chứng đúng toàn bộ ngữ nghĩa.
- `pipeline.py`: điều phối các bước.
- `web.py` + `frontend/`: giao diện local gọi đúng pipeline, xem lịch sử/câu nguồn và đối chiếu đáp án mẫu.
- `config.py`: đọc `.env` phía Python, không xuất khóa ra frontend.
- `offline_rules.py`: baseline kiểm tra T02/T03/T04 khi chưa có API; giới hạn hẹp và luôn được gắn nhãn.

## Kiểm thử và dữ liệu

- `samples/T01..T07.txt`: bảy tình huống tiếng Việt **tổng hợp, không phải transcript doanh nghiệp thật**.
- `samples/expected/T01..T07.json`: đáp án định nghĩa trước khi đánh giá.
- `tests/`: unit tests + kiểm thử hợp đồng LLM với client giả lập. Các test này **không chứng minh chất lượng LLM thật**.
- Chưa sử dụng AMI ở bước này; AMI sẽ là tập thử bổ sung sau khi lõi có kết quả ổn định trên tình huống tiếng Việt.

## Giới hạn hiện tại / việc tiếp theo

1. Đã có API Groq, UI local và baseline 24 transcript. Baseline và các lượt sửa dùng phiên bản khác nhau; chưa có điểm toàn dataset mới cho core hiện tại.
2. Còn lỗi phân loại vòng đời công việc thành request/action thừa; cảnh báo không đồng nghĩa tự sửa được lỗi. Transcript dài và độ ổn định giữa nhiều lần sinh chưa được xác nhận đầy đủ.
3. Audit có thể bỏ sót hoặc cảnh báo sai. Chưa có kiểm thử đối chứng audit on/off đầy đủ hoặc nhãn được người review độc lập xác nhận.
4. Quota API đã chặn một số lượt hồi quy cũ. Lượt cố định mới nhất đã chạy đủ LC01–LC03/H03 và nhóm đại diện bằng cùng phiên bản; kết quả vẫn có lỗi nội dung/audit. Không coi các lượt quota cũ là model trả sai.
5. Đã có repository public; chưa hoàn tất deploy và video. Xem [bảng test thực tế](docs/MISSION2_TEST_CASES.md) và [hướng dẫn demo](docs/DEMO_RUNBOOK.md).

**Giới hạn bảo mật:** Chỉ dùng transcript bạn có quyền xử lý; dữ liệu sẽ gửi tới bên cung cấp API bạn cấu hình. Không gửi dữ liệu nội bộ nhạy cảm vào dịch vụ chưa được phê duyệt. Transcript chứa câu lệnh giả mạo là dữ liệu, không phải lệnh điều khiển.

---

## Ghi chú lịch sử Stage 2 — thiết kế ngày 12/10/2026

Phiên bản này kế thừa toàn bộ Stage 1. Tập trung vào **giảm nguy cơ kết luận sai khi AI bỏ sót câu sửa/huỷ/chưa chốt**, chưa thêm UI trang trí.

### Chạy Stage 2 trong Windows PowerShell

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/run_contract_fixtures.py
```

- `unittest`: parser, resolver, verifier, API transport tới **HTTP mock chạy tại localhost**, chống bằng chứng giả và fail-closed.
- `run_contract_fixtures.py`: kiểm tra **bảy bộ events do người viết thủ công** đi qua phần mềm và so với kỳ vọng. Điều này **không chứng minh LLM chạy đúng 7/7**.
- `offline_rules`: chỉ là baseline theo biểu thức chính quy để chứng minh vài tình huống quyết định, không phải AI đầy đủ.

### Chạy API LLM THẬT

Adapter sử dụng giao thức **OpenAI-compatible Chat Completions**, có thể thay nhà cung cấp. Nhà cung cấp phải hỗ trợ định dạng đó. `LLM_JSON_MODE=false` dành cho dịch vụ không hỗ trợ `response_format={"type":"json_object"}` nhưng vẫn xuất JSON theo prompt. Không tự chuyển sang dịch vụ khác hoặc dùng mock khi lỗi.

```powershell
$env:LLM_API_KEY = 'YOUR_PRIVATE_API_KEY'
$env:LLM_BASE_URL = 'https://your-provider.example/v1'
$env:LLM_MODEL = 'your-model-name'

python cli.py samples/T03.txt --engine llm_api --save results/T03_real_api.json
python scripts/run_scenarios.py --engine llm_api --ids T02 T03 T04 --audit on --out results/live_core.json
python scripts/run_scenarios.py --engine llm_api --ids T01 T02 T03 T04 T05 T06 T07 --audit on --out results/live_all.json
```

**Không gửi khóa API cho người khác, không đẩy `.env` hoặc kết quả chứa dữ liệu nội bộ lên GitHub.** Biến môi trường chỉ cấu hình trên máy hoặc phần secrets của dịch vụ deploy. Dữ liệu demo ở `samples/` là tổng hợp, không có dữ liệu cá nhân thực. Nếu không có khóa hoặc provider, lệnh `llm_api` trả lỗi rõ ràng, không sinh điểm PASS giả.

### Ý nghĩa lượt kiểm chứng thứ hai

1. Lượt LLM thứ nhất tạo `EventBatch`; Python nhóm theo chủ đề, phân giải thứ tự và kiểm tra mã câu nguồn.
2. Lượt LLM thứ hai đọc **toàn transcript** đối chiếu sự kiện đã trích và bản ghi dự kiến, phát hiện câu sửa đổi bỏ sót, dẫn sai chủ đề hoặc dữ kiện chưa có căn cứ.
3. Mỗi cảnh báo phải có `source_ids` và `source_quote` xuất hiện đúng trong transcript. Cảnh báo vô căn cứ bị loại bỏ. Phát hiện nguy cơ cao khiến kết luận quyết định/công việc chuyển sang `unverified` / `needs_review`, **không tự bịa kết luận thay thế**.
4. Nếu API lượt kiểm chứng lỗi, mặc định `fail_closed=True` giữ bản ghi có rủi ro cao để người dùng kiểm tra. Trong trường hợp kết luận quá mơ hồ, app không được coi `unverified` là quyết định đã chốt.

**Hạn chế không che giấu:** LLM vẫn có thể bỏ sót cùng một câu ở cả hai lượt; xác nhận có câu nguồn chưa bảo đảm đúng diễn giải; dữ liệu bị chia sai chủ đề làm kiểm chứng khó. Audit hai lượt tăng API cost/latency. Cần chạy so sánh `--audit on` và `--audit off` trên cùng bộ test bằng model thật, sau đó ghi nhận kết quả.

### Kế hoạch tại thời điểm 12/10/2026

1. Cấu hình provider hợp lệ, chạy LLM thật trên T02/T03/T04 rồi tất cả T01–T07.
2. Điều chỉnh prompt/chunking từ các lỗi quan sát được, không tinh chỉnh theo toàn bộ tập đánh giá cùng lúc.
3. Tích hợp UI đơn giản hiển thị bản ghi, lịch sử và evidence; chỉ hoàn thiện giao diện khi lõi đủ ổn định.
4. Deploy, công khai repo, quay video và lập báo cáo Mission 2 có **kỳ vọng → thực tế → đạt/chưa đạt → điều học được**, gồm ca thất bại đã quan sát thật.

# Sửa lõi — lượt 2: điều kiện, hạn và liên kết công việc

Mục tiêu là sửa các lỗi cụ thể ảnh hưởng dữ liệu sau họp, giữ bằng chứng và công bố cả kết quả giảm chất lượng. Không chỉnh nhãn dataset, không thay kết quả baseline 24 case và không tuyên bố điểm tổng mới.

## Thay đổi đã làm

- Mở lại/rút/chưa chốt một lựa chọn không giữ điều kiện cũ như điều kiện hiện hành. Điều kiện cũ vẫn trong history; trường condition đã xóa có nguồn là câu thay đổi cuối.
- Khi đã có điều kiện cụ thể, một sự kiện chặn triển khai không cung cấp điều kiện mới không được ghi đè bằng câu chung chung. Nguồn condition và execution_status giữ riêng.
- Request được lưu due_raw khi model trích được hạn, kể cả hạn tương đối và chưa có owner. Request không bị biến thành action vì có hạn.
- deadline_change chỉ cập nhật hạn; các cập nhật owner/supporter/condition đi kèm bị bỏ qua và yêu cầu rà soát. Không thay mô tả công việc hoặc kích hoạt lại công việc đã hủy.
- Kiểm tra hẹp câu phủ định vai trò ở nguồn owner cuối, gồm “Tôi xác nhận không còn là người phụ trách”. Không áp dụng cho owner lịch sử của công việc đã hủy. Nếu cùng một câu vừa rút người khỏi web vừa giao người đó mobile, không tự xóa owner bằng kiểm tra từ khóa.
- Prompt yêu cầu key theo công việc, không theo loại thay đổi; không tạo key _deadline/_owner riêng cho cùng việc. Nhóm đổi hạn không có công việc gốc vẫn bị từ chối, không ghép gần đúng vào một việc khác.
- Thử prompt ngắn hơn bằng tiếng Anh, giữ nội dung đầu ra tiếng Việt và các ví dụ hành vi bằng tiếng Việt. Việc này giúp một số case nhưng cũng gây regression; các lượt trước/sau được lưu riêng.

## Hai xử lý nguyên văn có giới hạn

**Mục chưa chốt:** khi LLM trả unresolved nhưng mô tả trống hoặc không diễn đạt việc chưa chốt, có thể dùng nguyên văn câu nguồn bắt đầu bằng “chưa chốt/chưa chọn/chưa quyết định”. Không suy đoán nội dung từ topic, không sửa loại sự kiện. Có thông báo yêu cầu rà soát. Những nhóm công việc thiếu mô tả hoặc đổi hạn sai key vẫn bị từ chối.

**Hạn tương đối:** chỉ lấy cụm “trước lần/đợt/buổi …” đã có trong cả nội dung request và câu nguồn của nội dung đó. Câu nguồn phải là yêu cầu khẳng định, không có phủ định, dấu hỏi hoặc lựa chọn “hay/hoặc”. Giữ nguyên cụm chữ vào due_raw, trích đúng source ID, không tạo due_iso và đánh dấu needs_review. Không tạo thêm request nếu model đã bỏ sót cả bản ghi.

Đây là xử lý bằng phần mềm sau LLM, không phải model tự trích tốt hơn hay được train. Phạm vi quy tắc hẹp, chưa bao phủ mọi cách diễn đạt tiếng Việt.

## Lượt A — năm case, prompt trước khi rút gọn

Artifact: `docs/evaluation/dataset_core_round2.json`. Cả 5/5 hoàn tất pipeline và audit, temperature 0.6, reasoning low. Chạy được không có nghĩa mọi nội dung đều đạt.

| Case | Kết quả thực tế | Điều học được |
|---|---|---|
| D03 | Đúng agreed/blocked, phạm vi thiết kế và điều kiện pháp chế phê duyệt hợp đồng, issue hợp đồng còn mở | Có thể phân biệt quyết định trong họp với quyền triển khai |
| D04 | Sai open; model phân loại câu chốt/sửa điều kiện thành proposal/counterproposal và câu điều kiện chưa đạt thành unresolved | Resolver không thể sửa mọi lỗi hiểu speech act của model |
| H01 | Đúng reopened, condition null, việc Huy vẫn assigned | Đã sửa lỗi điều kiện lịch sử nằm ở trường hiện hành |
| H03 | Có request nhưng due_raw null; open đúng, audit lại đòi ngày/người đã chọn trái nguồn | Có nội dung trong câu văn chưa đủ chứng minh dữ liệu cấu trúc đầy đủ; audit có false positive |
| H08 | Đúng Oanh/Vũ/thứ Hai cho log mẫu, Duy/thứ Tư cho ID test; không còn nhóm deadline mồ côi. Sai trạng thái/điều kiện lưu log, thiếu menu chưa chốt | Liên kết việc cải thiện, nhưng case dài vẫn chưa đạt toàn bộ |

## Lượt B — prompt rút gọn, bốn case

Artifact: `docs/evaluation/dataset_core_round2_promptcheck.json`. Cả 4/4 hoàn tất pipeline và audit, temperature 0.6, reasoning low. Lượt này diễn ra trước các xử lý nguyên văn cuối cùng.

| Case | Kết quả thực tế | Đánh giá |
|---|---|---|
| D03 | Đúng agreed/blocked và điều kiện pháp chế; content mất “trong phạm vi thiết kế” | Regression về phạm vi; chưa tính là đúng hoàn toàn |
| D04 | Đúng conditional/pending_condition; condition thay 500 bằng 300 và không lỗi nghiêm trọng; nguồn trường là L003 | Phần lõi điều kiện đạt; audit vẫn nhầm nguồn lịch sử L001 với nguồn condition hiện tại |
| H01 | Đúng reopened/condition null, việc Huy giữ nguyên; audit đòi điều kiện cũ | Phần lõi đạt; cảnh báo audit sai không làm mất reopened |
| H03 | Chỉ có decision/proposed, thiếu request và kết luận chưa chọn ngày | Chưa đạt; prompt ngắn hơn không cải thiện đồng đều |

H08 chưa được gọi lại với prompt rút gọn. Không lấy kết quả H08 của lượt A để tuyên bố accuracy của prompt B. Những case reserved đã dùng để sửa không còn là tập kiểm chứng độc lập.

## Hai phép thử H03 với medium/0.2

1. `dataset_h03_reasoning_probe.json`: model có request và đúng due_raw, nhưng mô tả các sự kiện decision trống; validator cũ từ chối, chưa chạy audit.
2. `dataset_h03_source_fallback_check.json`: chạy được cả audit, nhưng model lại bỏ due_raw; có request và trạng thái open, nội dung decision quá chung. Tăng reasoning không tự bảo đảm độ đúng.

Cấu hình medium/0.2 là phép thử riêng, chưa đổi mặc định low/0.6 của ứng dụng. Không gọi một kết quả tốt là bằng chứng cấu hình đó luôn tốt hơn.

## Kiểm chứng phần xử lý nguyên văn cuối cùng

**95/95 unit/contract tests đạt.** Có kiểm tra cập nhật điều kiện, provenance, hạn tương đối không có owner, hạn không đổi người, phủ định vai trò, không ghép key mơ hồ, không lấy hạn từ câu hỏi/phủ định/lựa chọn chưa chốt. Đây là kiểm tra phần mềm, không phải 95 case LLM đúng.

`scripts/replay_source_recovery.py` phát lại **tất cả 6 biến thể H03 đã lưu** qua mã hiện tại; không gọi LLM mới và không gọi lại audit. Dùng các findings cũ nếu lượt gốc có audit.

| Đầu ra gốc | Sau xử lý nguyên văn bằng mã hiện tại |
|---|---|
| H03 baseline | Giữ request + hạn tương đối + open, không bịa người |
| H03 lượt A | Giữ request + hạn tương đối + open, không bịa người |
| H03 lượt B | Vẫn thiếu request và kết luận cuối; không tự tạo bản ghi |
| H03 medium probe | Có request/hạn/open; chưa có audit thật ở lượt gốc |
| H03 medium source check | Có request/hạn/open; chỉ replay audit cũ |
| H03 hồi quy cuối | Validator từ chối nhóm decision thiếu nội dung; model không trả sự kiện cho câu kết luận cuối |

**4/6 biến thể qua các kiểm tra phần mềm nêu trên. Con số này không phải accuracy mới, không phải 6 transcript độc lập và không phải 6 lời gọi mới bằng phiên bản cuối.** Hai biến thể còn lại được giữ nguyên trong báo cáo: một bỏ sót request/kết luận, một bị validator từ chối. Không chọn riêng đầu ra thuận lợi để tính kết quả.

Artifact replay: `docs/evaluation/source_recovery_replay.json`, có hash đầu ra gốc và mã xử lý. Mọi kết quả thất bại và regression được giữ lại.

## Hồi quy API sau xử lý nguyên văn

Artifact: `docs/evaluation/dataset_core_round2_final.json`. Bốn case chạy mới với cấu hình low/0.6: **3/4 hoàn tất pipeline và audit, 1/4 bị từ chối ở extraction**. Đây là tỷ lệ hoàn tất của lượt nhỏ này, không phải accuracy toàn dataset.

| Case | Kỳ vọng → kết quả thực tế | Đạt/Chưa đạt → điều học được |
|---|---|---|
| D03 | Giữ phạm vi thiết kế, agreed/blocked, điều kiện pháp chế và issue hợp đồng riêng → đúng trạng thái/điều kiện, mất phạm vi thiết kế và thiếu issue riêng | Chưa đạt đầy đủ; thông tin hợp đồng vẫn nằm trong điều kiện chặn, nhưng cấu trúc và phạm vi bị thiếu |
| D04 | Conditional, chờ đủ 300 người đồng thời và không lỗi nghiêm trọng → đúng các trường lõi và nguồn L003 | Lõi đạt; audit cũ của lượt này còn cảnh báo nhầm điều kiện lịch sử |
| H01 | Reopened, condition null; việc Huy không bị hủy → đúng các trường lõi | Lõi đạt; audit vẫn cảnh báo nhầm điều kiện cũ |
| H03 | Request trước lần thử tiếp theo, chưa chọn thứ Tư/thứ Năm → model trả đề xuất không có mô tả và bỏ sự kiện kết luận L006; validator từ chối | Chưa đạt; xử lý nguyên văn chỉ sửa sự kiện có nguồn phù hợp, không tự tạo sự kiện model bỏ sót |

H03 là lỗi thật quan sát qua API, không phải tình huống được lập trình để cố ý thất bại. Nó còn cho thấy độ ổn định giữa các lần sinh chưa tốt. Không thể kết luận chỉ tăng reasoning hoặc thêm quy tắc là sẽ hết lỗi.

## Kiểm tra riêng dữ liệu gửi cho audit

Đã sửa payload audit để giữ rõ các trường hiện tại có giá trị null/default, giữ nguồn riêng từng trường, bỏ danh sách nguồn tổng hợp và history trùng với events. Ví dụ `condition: null` sau khi mở lại phải hiện rõ; bỏ trường này khi rút gọn có thể khiến audit hiểu sai trạng thái hiện tại. Có contract test kiểm tra cấu trúc payload.

Artifact: `docs/evaluation/audit_explicit_state_probe.json`. **Dùng lại extraction thật đã lưu, gọi audit mới cho D04/H01; không phải chạy lại toàn pipeline.** Cả hai lời gọi audit hoàn tất:

- D04: không có finding trong lượt này; giữ conditional/pending_condition và điều kiện hiện tại.
- H01: vẫn có một cảnh báo sai mức high, đòi khôi phục điều kiện bảo mật cũ. Đây là lỗi hiểu diễn biến của LLM audit còn tồn tại dù payload đã rõ hơn. Guard giữ reopened và condition null, không tự khôi phục điều kiện cũ; cảnh báo cần rà soát vẫn hiện.

Không gộp hai lượt audit này vào kết quả hồi quy toàn pipeline để tuyên bố accuracy mới. Không xem một lượt D04 hết cảnh báo là bằng chứng audit luôn đúng. Dữ liệu, nhãn baseline và mọi đầu ra thất bại đều được giữ lại; artifact có hash để phân biệt phiên bản.

## Chạy lại

```bat
python -m unittest discover -s tests -q
python scripts/replay_source_recovery.py
python scripts/run_dataset.py --ids D03 D04 H01 H03 --call-interval 60 --out results/NEW_round2_check.json
```

Có thể thử `--reasoning-effort medium --temperature 0.2` ở đường dẫn output khác. Không ghi đè artifact cũ, không trộn điểm giữa prompt/config khác nhau. Không cài thêm dependencies.

## Vị trí trong roadmap

Vẫn ở chặng B, củng cố lõi. Đã sửa các lỗi lưu/cập nhật trường, chạy hồi quy API và ghi nhận cả cải thiện lẫn regression. Chưa chốt lõi là ổn định: còn thiếu phạm vi/bản ghi ở D03, H03 có lần bị từ chối và audit H01 cảnh báo sai. Ưu tiên tiếp theo là giảm bỏ sót kết luận/phạm vi, phân biệt cảnh báo audit với dữ liệu được xác nhận, rồi chạy một bộ hồi quy cố định để chọn phiên bản demo. H08 chưa được kiểm chứng lại với prompt hiện tại. Chưa mở rộng UI/tính năng trong lượt này.

# Meeting Intelligence — Mission 3

**Trí tuệ cuộc họp · NextGen AI Talent 2026 · Bài test C**

> **Từ bản ghi cuộc họp có cấu trúc đến những cam kết có thể kiểm chứng.**
>
> Mission 3 cải tiến trực tiếp sản phẩm Mission 2, tập trung tránh kết luận sai, phân công nhầm người hoặc tự tạo thời hạn khi lời nói chưa đủ rõ ràng. Mọi bản ghi quan trọng đều cần được đối chiếu với câu nguồn và rà soát trước khi sử dụng.

**[Trải nghiệm Mission 3](https://meeting-intelligence-m3.vercel.app/)** · **[Mã nguồn Mission 3](https://github.com/Vie-is-mee/Meeting-Intelligence/tree/mission3/improvement-20261021)** · **[Báo cáo trước/sau](docs/MISSION3_C2_BEFORE_AFTER_RESULTS.md)** · **[Bằng chứng kiểm thử](docs/MISSION3_STAGE7BC_COMPLETENESS_20261024.md)**

| Phiên bản | Nhánh | Mục đích |
| --- | --- | --- |
| Mission 2 | [`main`](https://github.com/Vie-is-mee/Meeting-Intelligence/tree/main) | Sản phẩm gốc, giữ nguyên để đối chiếu |
| **Mission 3** | [`mission3/improvement-20261021`](https://github.com/Vie-is-mee/Meeting-Intelligence/tree/mission3/improvement-20261021) | Cải tiến độ tin cậy, xử lý Change Request C2 và đánh giá bổ sung |

---

## 1. Vấn đề cần giải quyết

Một cuộc họp không phải danh sách quyết định đã hoàn thiện. Người tham dự có thể đề xuất rồi đổi ý, đặt câu hỏi thay vì giao việc, hoãn một nhiệm vụ hoặc chốt một vấn đề trong khi vấn đề khác vẫn còn mở.

Mission 2 đã trích xuất sự kiện, nhóm theo chủ đề, theo dõi diễn biến, gắn nguồn và cho người dùng rà soát. Tuy nhiên, đánh giá thực nghiệm còn phát hiện các rủi ro:

- **Cam kết giả:** câu đề xuất hoặc ý định tập thể bị xem là quyết định/phân công đã chốt.
- **Nhầm trạng thái cuối:** việc đã hủy, mở lại hoặc tạm dừng vẫn có thể xuất hiện như nhiệm vụ đang thực hiện.
- **Lẫn chủ đề:** một câu phủ định về nhà cung cấp có thể ảnh hưởng sai tới quyết định kiến trúc khác.
- **Bỏ sót hoặc trùng lặp:** một cuộc họp dài có thể mất vấn đề độc lập, hoặc ghi thêm quyết định trùng với nhiệm vụ.
- **Bằng chứng thiếu ngữ nghĩa:** dẫn đúng số dòng chưa đủ chứng minh đúng người phụ trách, thời hạn hoặc điều kiện.

**Lựa chọn cải tiến:** sửa các điểm có khả năng dẫn đến hành động sai, thay vì phát triển lại ứng dụng, thêm nhiều tác nhân AI hoặc chỉ đổi giao diện.

## 2. Change Request C2: Action chưa rõ

**Phát biểu gốc:** “Cái này team mình xử lý nhé”.

Phát biểu này chưa xác định **cá nhân phụ trách** và **thời hạn**. Mission 3 không được tự suy ra hai thông tin đó từ người nói hoặc từ ngữ cảnh mơ hồ.

| Trường hợp | Cách xử lý cần có |
| --- | --- |
| Chỉ có câu nói tập thể | Lưu `action / unverified`, để trống người phụ trách và hạn; dẫn câu nguồn; yêu cầu rà soát |
| “Thứ Sáu” mới là lời đề xuất | Không coi đó là thời hạn đã cam kết |
| Huy nhận việc rõ ràng về sau | Ghi nhận Huy, giữ đúng thời hạn “**trước thứ Sáu**”, tránh tạo nhiệm vụ tập thể trùng |
| Việc của Lan bị hủy và bỏ hạn | Ghi trạng thái hủy, bỏ hạn, giữ người phụ trách trong **lịch sử** |
| Việc được tạm dừng do thiếu điều kiện | Không tiếp tục trình bày như nhiệm vụ đang hoạt động; giữ căn cứ và yêu cầu rà soát |

Các ví dụ thuộc bộ thử phát triển, **không phải cam kết chính xác đối với mọi cách diễn đạt**.

[Đọc chi tiết so sánh M2/M3 trên bốn ca C2 →](docs/MISSION3_C2_BEFORE_AFTER_RESULTS.md)

## 3. Luồng hoạt động

~~~mermaid
flowchart TD
    A["Nội dung cuộc họp"] --> B["Trích xuất sự kiện"]
    B --> C["Liên kết theo chủ đề và thời gian"]
    C --> D["Xác định trạng thái cuối"]
    D --> E["Kiểm tra nguồn và cảnh báo"]
    E --> F["Con người rà soát"]
    F --> G["Xuất dữ liệu có lịch sử xác nhận"]
~~~

**Điểm khác biệt so với một công cụ tóm tắt thông thường:** hệ thống cố gắng giữ riêng lời đề xuất, kết luận đã chốt, trạng thái thực hiện và lịch sử sửa đổi. AI hỗ trợ phát hiện nội dung; **con người quyết định xác nhận**.

Các cải tiến trên nhánh M3 gồm:

1. **Chống phân công mơ hồ:** phân biệt ý định tập thể với việc cá nhân đã nhận.
2. **Theo dõi vòng đời nhiệm vụ:** cập nhật khi nhận việc, thay hạn, hủy, mở lại và tạm dừng; bảo toàn thông tin lịch sử.
3. **Kiểm chứng gắn với lời nói gốc:** kiểm tra căn cứ cho các trường và trạng thái quan trọng, không để cảnh báo thiếu căn cứ tự xóa dữ liệu đúng.
4. **Bảo toàn vấn đề chưa giải quyết:** khôi phục một số trường hợp vấn đề độc lập hoặc quyết định lựa chọn nhà cung cấp còn mở bị bỏ sót; không tự tạo người chịu trách nhiệm hay quyết định đã duyệt.
5. **Rà soát trước khi bàn giao:** đánh dấu *Đúng / Sai / Chưa đủ bằng chứng*. CSV chỉ chứa mục đã được người dùng xác nhận; JSON giữ đầu ra AI và lịch sử rà soát.

## 4. Kết quả và bằng chứng

### 4.1. Trước/sau trên bốn tình huống C2

Bộ so sánh sử dụng cùng dữ liệu đầu vào, cùng mô hình Groq và thông số đã công bố, đồng thời lưu đầu ra gốc của từng phiên bản.

| Ca | Mission 2 trong lần thử | Mission 3 trong lần thử |
| --- | --- | --- |
| **C2-01** | Xem lời tập thể là một `decision / proposed`; **không** tự bịa người hoặc hạn | `action / unverified`, người/hạn trống, dẫn L001 |
| **C2-02** | Có lượt biến đề xuất hoàn thành thứ Sáu thành yêu cầu ghi nhận | Giữ tình trạng chưa chốt; một số lượt còn cảnh báo kiểm tra |
| **C2-03** | Nhận đúng Huy và hạn nhưng có quyết định trùng | Giữ một nhiệm vụ đã phân công, hạn “trước thứ Sáu” |
| **C2-04** | Đã xử lý đúng hủy việc của Lan | Giữ nguyên hành vi đúng, không nhận đây là khả năng mới |

Ở lượt so sánh được ghi lại, **4/4 lượt gọi mô hình hoàn tất** và đáp ứng các ràng buộc C2 trọng tâm; chỉ **3/4 trường hợp không có cảnh báo kiểm tra được chấp nhận**. Kết quả này **không phải tỷ lệ chính xác chung**.

### 4.2. Những kiểm tra bổ sung

| Nhóm minh chứng | Kết quả đã ghi nhận | Giới hạn diễn giải |
| --- | --- | --- |
| Đánh giá Stage 5 | 6/6 ca C2-01–04, D01, D04 hoàn tất xử lý và kiểm tra; 6/6 nhóm điều kiện định trước đạt | Hai ca C2 vẫn có cảnh báo; dữ liệu chủ yếu phục vụ phát triển |
| Kiểm thử phần mềm Stage 7B/C | **293/293** kiểm thử Python và **13/13** kiểm thử Node đạt | Không phải kiểm chứng độ chính xác ngôn ngữ ngoài thực tế |
| Kiểm tra cuộc họp dài LONG01/LONG02 | Phát hiện và sửa hẹp nhiều lỗi tạm dừng, bỏ sót vấn đề và lẫn chủ đề | Vẫn còn lỗi ghi trùng quyết định và độ ổn định chưa được chứng minh |

**Cách đọc đúng bằng chứng:** các phép phát lại đầu ra Groq đã lưu giúp chỉ ra tác dụng của phần mã sửa đổi trong cùng một tình huống; các lượt gọi Groq mới xác nhận luồng chạy thực tế, nhưng có thể thay đổi theo mỗi lần sinh. Chưa có tập kiểm chứng độc lập bằng bản ghi họp thật với nhãn do người đánh giá bên ngoài xác nhận.

Nguồn chi tiết:

- [Before/After chính thức của C2](docs/MISSION3_C2_BEFORE_AFTER_RESULTS.md)
- [Bảng kết quả Stage 5](docs/MISSION3_STAGE5_FINAL_SCORECARD_20261024.md)
- [Cải tiến trạng thái tạm dừng](docs/MISSION3_STAGE7A_FINAL_STATE_PAUSE_20261024.md)
- [Đánh giá đầy đủ chủ đề và cảnh báo](docs/MISSION3_STAGE7BC_COMPLETENESS_20261024.md)
- [Kết quả gốc và nhật ký chạy](docs/evaluation/mission3/)
- [Lịch sử cải tiến từ Mission 2](docs/MISSION2_TO_MISSION3_IMPROVEMENT_HISTORY.md)

## 5. Trải nghiệm bản Mission 3

### Trực tuyến

- **Giao diện:** https://meeting-intelligence-m3.vercel.app/
- **Máy chủ thử nghiệm:** https://meeting-intelligence-m3-staging.onrender.com/
- **Thông tin phiên bản máy chủ:** [`/api/version`](https://meeting-intelligence-m3-staging.onrender.com/api/version)

Theo biên bản kiểm tra công khai tại nhánh làm việc, máy chủ staging đã trả về đúng mã nguồn `a66a985` của Stage 7B/C và một lượt thử C2 qua API thật thành công. **Phần thử thao tác trực tiếp trên trình duyệt cho toàn bộ quy trình rà soát/xuất chưa được xác nhận trong biên bản này.** Khi quay video, cần kiểm tra lại mã nguồn tại `/api/version` và trạng thái dịch vụ thực tế.

Gợi ý trình diễn:

1. Chọn **C2-01**, phân tích và kiểm tra người phụ trách/hạn trống cùng câu nguồn L001.
2. Chọn **C2-03**, đối chiếu với trường hợp sau đó có lời nhận việc rõ ràng của Huy.
3. Mở phần **Kiểm chứng** để xem lịch sử và nguồn gắn với kết luận.
4. Vào **Rà soát & xuất**, dùng trạng thái *Chưa đủ bằng chứng* cho mục mơ hồ; kiểm tra bản CSV chỉ chứa những bản ghi đã được xác nhận.
5. Trình bày cả ca thành công và hạn chế còn tồn tại ở cuộc họp nhiều chủ đề.

**Lưu ý:** chế độ xem lại kết quả đã lưu khác với lượt gọi mô hình mới. Không dùng bản phát lại để khẳng định hệ thống vừa phân tích qua API.

### Chạy tại máy

Yêu cầu Python 3.10 trở lên và các thư viện trong `requirements.txt`.

~~~bash
git clone --branch mission3/improvement-20261021 https://github.com/Vie-is-mee/Meeting-Intelligence.git
cd Meeting-Intelligence
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -X utf8 web.py
~~~

Mở **http://127.0.0.1:8765**. Trên Windows cũng có thể sử dụng `run_web.cmd`.

Để phân tích mới, cấu hình nhà cung cấp mô hình trong `.env` từ `.env.example` tại máy chủ; **không công khai khóa API** trong kho GitHub, trình duyệt hoặc video. Chế độ xử lý ngoại tuyến theo luật là công cụ đối chiếu giới hạn, không phải mô hình AI đầy đủ.

## 6. Giới hạn và định hướng tiếp theo

- Chưa có phép đánh giá độc lập đủ rộng trên bản ghi họp thực tế.
- Phát biểu mơ hồ, tiếng nói chuyển thành văn bản có lỗi và cuộc họp dài đan xen nhiều chủ đề vẫn có thể gây thiếu hoặc trùng bản ghi.
- Dẫn nguồn chứng minh vị trí thông tin được lấy từ đâu, **không tự chứng minh cách hiểu ngữ nghĩa đúng**.
- Bản ghi chưa xác nhận hoặc nhiệm vụ tạm dừng không được tự động giao việc hay xuất thành cam kết chính thức.
- Chưa tích hợp tự động với hệ thống giao việc hoặc cơ sở tri thức doanh nghiệp; cần đánh giá riêng về dữ liệu, phân quyền và trách nhiệm phê duyệt.

**Bước tiếp theo:** thử nghiệm có kiểm soát với dữ liệu được phép sử dụng, người đánh giá độc lập và chỉ số về người/hạn bị gán sai, bản ghi bỏ sót, trạng thái cuối và bằng chứng theo từng trường.

---

## 7. Tài liệu dự án và bảo toàn Mission 2

| Tài liệu | Mục đích |
| --- | --- |
| [Lịch sử cải tiến M2 → M3](docs/MISSION2_TO_MISSION3_IMPROVEMENT_HISTORY.md) | Những điểm mạnh/yếu ban đầu và các thay đổi có căn cứ |
| [Điều kiện nghiệm thu nội bộ](docs/MISSION3_ACCEPTANCE_CRITERIA.md) | Quy tắc đánh giá và tiêu chí dừng |
| [Tài liệu nộp Mission 3](docs/MISSION3_FINAL_SUBMISSION_PACK_20261024.md) | Nội dung giải thích lựa chọn, giới hạn và kịch bản video |
| [Hướng dẫn staging và trình diễn](docs/MISSION3_STAGING_VIDEO_AND_SUBMISSION.md) | Kiểm tra triển khai và rà soát trước khi xuất |
| [Hướng dẫn Mission 2](https://github.com/Vie-is-mee/Meeting-Intelligence/blob/main/README.md) | README gốc để đối chiếu |
| [Bản trình diễn Mission 2](https://meeting-intelligence-sable.vercel.app/) | Trang demo M2; kết quả lưu sẵn không phải phân tích mới |

Mission 3 phát triển trên **nhánh riêng**. README và mã nguồn `main` của Mission 2 được giữ nguyên; việc thay README trên nhánh này không gộp hay thay đổi nhánh `main`.

---

*Dự án thử nghiệm. Không sử dụng kết quả AI chưa được con người xác nhận làm căn cứ duy nhất để giao nhiệm vụ, quyết định hoặc lưu tri thức chính thức.*

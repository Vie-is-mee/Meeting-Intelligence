# Hướng dẫn demo và chốt phiên bản Mission 2

Trạng thái: chuẩn bị demo, chưa xác nhận hoàn tất bài nộp. Dùng [bảng test](MISSION2_TEST_CASES.md) và artifact để nói đúng kết quả; không coi mọi lượt prompt là cùng một phiên bản.

Đã có [hồi quy cùng phiên bản 8/8 case](FINAL_REGRESSION_RESULTS.md): 4 đạt đầy đủ, 4 chưa đạt; LC03 đúng dữ liệu lõi nhưng audit sai. Dùng lượt này để chọn minh họa cùng phiên bản, giữ mọi kết quả thất bại.

## Chạy local

Tại thư mục dự án, dùng Python đã có pydantic/python-dotenv; không cần cài lại nếu đã chạy được:

```powershell
& 'I:\Python\python.exe' -X utf8 web.py
```

Mở `http://127.0.0.1:8765`. Go Live chỉ xem bố cục tĩnh; phân tích cần backend Python. Người dùng trên máy khác dùng `python -X utf8 web.py` sau khi cài requirements nếu thiếu dependencies. Cấu hình `.env` từ `.env.example`, chỉ đặt key phía server.

## Hai cách trình bày phải phân biệt rõ

- Demo trực tiếp: chọn LLM API, nhập transcript tổng hợp, chạy và xem kết quả mới. Nếu API lỗi/quota, nói rõ lượt này chưa hoàn tất; không chuyển offline rồi gọi đó là năng lực LLM.
- Xem bằng chứng đã lưu: mở JSON trong `docs/evaluation` và transcript tương ứng trong dataset, ghi rõ đó là đầu ra của lượt trước và phiên bản nào. Đây là walkthrough, không phải lần sinh trực tiếp mới. Không chỉnh JSON để làm đẹp kết quả.

Không quay màn hình `.env`, header Authorization hoặc terminal có key. Chỉ dùng dữ liệu tổng hợp đã có trong repo.

## Kịch bản video tối đa 5 phút

| Thời gian | Nội dung |
|---|---|
| 0:00–0:35 | Bài toán: tóm tắt chưa đủ; đề xuất đầu cuộc họp có thể bị thay đổi/rút lại cuối cuộc họp |
| 0:35–1:10 | Phần chọn chứng minh: transcript → sự kiện có nguồn → trạng thái cuối → evidence từng trường; audit hỗ trợ rà soát |
| 1:10–2:30 | Case thành công: chỉ vào câu chốt/câu sửa, trạng thái, phạm vi, điều kiện và nguồn của kết quả. Dùng case thực sự đạt ở phiên bản đã công bố; nếu xem artifact thì nói rõ |
| 2:30–3:25 | Case khó LC03: hủy task nhưng giữ phạm vi và request; audit vẫn cảnh báo sai về owner lịch sử. Chỉ rõ cảnh báo không phải kết luận đúng |
| 3:25–4:20 | Case thất bại LC01: request thừa; xem evidence rồi từ chối request ở mục 05, xác nhận action đã hủy và xuất CSV. Chỉ rõ người dùng xử lý lỗi; AI gốc/điểm test không đổi |
| 4:20–5:00 | Kết quả kiểm thử, giới hạn dataset tổng hợp/nhãn cùng trợ lý, quota, transcript dài và bước tiếp theo |

H03 ở hồi quy mới chỉ còn decision chưa chọn ngày/người, thiếu request và hạn tương đối. Có thể dùng làm ví dụ bỏ sót thông tin; không dùng kết quả tốt cũ để tuyên bố H03 hiện đã đạt. Không chọn artifact khác phiên bản rồi trình bày như cùng một bản demo đã ổn định.

## Điều kiện chốt và các mục còn thiếu

1. Giữ nguyên một phiên bản core/config và lưu hash; ghi kết quả hồi quy gồm lỗi/chưa chạy, không chỉnh prompt trong khi đo.
2. Chọn tối thiểu 5 case thực tế có kỳ vọng → kết quả → đạt/chưa đạt → điều học được; bảng hiện có là bằng chứng nhiều phiên bản, cần ghi rõ nếu dùng.
3. Công khai hạn chế đã biết; nhiệm vụ không yêu cầu mọi case khó đều đúng. Chưa có bằng chứng độc lập để tuyên bố sản phẩm hoàn hảo.
4. Chuẩn bị câu trả lời ba câu bắt buộc: giả thuyết lõi; thay đổi so với proposal Mission 1 sau khi đối chiếu proposal gốc; loại thông tin dễ sai và các biện pháp chống dữ liệu không tồn tại.
5. Public GitHub repo, link demo hoặc lý do/hướng dẫn local, YouTube ≤5 phút và đoạn trình bày ≥50 ký tự. Repo public: https://github.com/Vie-is-mee/Meeting-Intelligence. Demo online và YouTube chưa được xác nhận.

Chưa deploy hoặc publish từ hướng dẫn này. Website hiện là công cụ kiểm chứng local; việc có cảnh báo cần rà soát là hành vi minh bạch của MVP, không phải bằng chứng đủ để kết quả trở thành đúng.

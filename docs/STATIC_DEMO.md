# Demo tĩnh — Local, Go Live và gói deploy sau

Bản này xem lại **8 đầu ra Groq thật đã lưu**, cùng một phiên bản core, có cả thành công và lỗi. Không gọi API, không cần key, không phân tích transcript mới. Dữ liệu gốc, verdict và cảnh báo được giữ nguyên. Mặc định mở case D01 để minh họa thay đổi lựa chọn và kết luận cuối.

## Xem ngay bằng VS Code

Mở `frontend/index.html` → Go Live. Chọn tình huống → “Xem kết quả đã lưu” → chọn bản ghi để xem lịch sử/câu nguồn. Mở “JSON gốc” hoặc tải JSON để đối chiếu provenance. Demo mặc định đã hiển thị D01 ngay khi tải xong.

Nếu dùng ZIP tĩnh đã giải nén, mở `index.html` ở ngay thư mục gốc của ZIP bằng Go Live. Gói ZIP chỉ có bản xem lại; không có backend Python.

Các case nên xem: D01/D03/D04/H01 thành công; LC03 có audit sai; LC01 có request thừa được cảnh báo; H03 bỏ sót request; LC02 thiếu lựa chọn thay thế và có bản ghi thừa. 4/8 đạt đầy đủ, 5/8 đạt dữ liệu lõi trong lượt đã lưu, không phải accuracy tổng quát.

Không dùng double-click file:// làm cách chạy chính vì trình duyệt có thể chặn fetch JSON. Dùng Go Live hoặc HTTP server.

## Chạy bằng Python có sẵn, không cài thư viện

Trên Windows có thể nhấp đúp `run_demo.cmd`, mở `http://127.0.0.1:5501`.

Tại thư mục dự án:

```powershell
& 'I:\Python\python.exe' -m http.server 5501 --bind 127.0.0.1 --directory frontend
```

Mở `http://127.0.0.1:5501`. Máy khác dùng `python -m http.server 5501 --bind 127.0.0.1 --directory frontend`.

Trong thư mục ZIP tĩnh đã giải nén (không có thư mục frontend), dùng `python -m http.server 5501 --bind 127.0.0.1`.

## Phân tích mới bằng backend

Nhấp đúp `run_web.cmd`, hoặc chạy `python -X utf8 web.py`, mở `http://127.0.0.1:8765`. Mặc định vẫn là chế độ xem lại. Chuyển sang “LLM API · phân tích mới” để nhập/sửa transcript và gọi API đã cấu hình trong `.env`. Chế độ offline là luật hẹp, không đại diện cho chất lượng LLM. Không tự đổi chế độ khi API lỗi.

## Gói deploy sau

`dist/meeting-intelligence-demo-static.zip` chứa trang tĩnh, CSS, JS, dữ liệu demo và hướng dẫn; không chứa backend hoặc key. Giải nén và đặt nội dung thư mục lên static hosting. Không cần build/npm. Đây là phương án deploy walkthrough, không phải backend LLM online.

`dist/meeting-intelligence-mission2-source.zip` là gói mã nguồn theo allowlist, có `.env.example` và tài liệu, không có `.env`, tmp, logs, cache hoặc kết quả riêng trong results. Gói này chưa được publish. Không đưa API key vào static hosting.

Tạo lại gói sau khi cập nhật tài liệu:

```powershell
python scripts/build_demo.py
python scripts/package_demo.py
```

Xem `dist/BUILD_INFO.json` để đối chiếu hash các tệp. `demo-data.json` có hash của lượt hồi quy và API usage lịch sử; `api_calls: 0` chỉ số lời gọi của lượt xem lại hiện tại.

# Deploy Vercel + Render Free

Repo: https://github.com/Vie-is-mee/Meeting-Intelligence

Frontend HTML/CSS/JS ở Vercel; API Python và khóa Groq ở Render. Frontend gọi Render trực tiếp qua HTTPS, không qua Vercel Function. Không cần cài thêm thư viện trên máy để deploy bằng dashboard. Render cũng phục vụ toàn bộ website, dùng được riêng nếu chưa muốn deploy Vercel.

## 1. Render trước

1. Đăng nhập https://dashboard.render.com bằng GitHub. **New → Web Service**, kết nối repo **Vie-is-mee/Meeting-Intelligence**.
2. Branch **main**, runtime **Python 3**, instance **Free**, **Root Directory để trống**. Repo GitHub đã có web.py ở gốc.
3. Build Command: `pip install -r requirements.txt`.
4. Start Command: `python -X utf8 web.py --host 0.0.0.0 --public`.
5. Health Check Path: `/healthz`.
6. Thêm Environment Variables:

| Tên | Giá trị |
| --- | --- |
| `PYTHON_VERSION` | `3.12.12` |
| `LLM_API_KEY` | Khóa Groq của bạn, chỉ nhập trên Render |
| `LLM_BASE_URL` | `https://api.groq.com/openai/v1` |
| `LLM_MODEL` | `openai/gpt-oss-120b` |
| `LLM_JSON_MODE` | `true` |
| `LLM_STRUCTURED_OUTPUTS` | `auto` |
| `LLM_MAX_COMPLETION_TOKENS` | `2560` |
| `LLM_TEMPERATURE` | `0.6` |
| `LLM_REASONING_EFFORT` | `low` |
| `ENABLE_LIVE_API` | `true` |

7. Deploy, lấy URL thật dạng `https://meeting-intelligence-xxxx.onrender.com`. Render tự cấp `PORT` và `RENDER_EXTERNAL_HOSTNAME`, không nhập thủ công.
8. Mở `<URL-Render>/healthz`: phải trả `{"status":"ok"}`. Mở URL gốc: website chạy trực tiếp trên Render.

**Cách khác:** New → Blueprint → chọn repo để dùng `render.yaml`. Kiểm tra plan là Free, nhập LLM_API_KEY trong dashboard. ALLOWED_ORIGINS ban đầu trống, cập nhật sau khi biết URL Vercel.

## 2. Vercel

1. Đăng nhập https://vercel.com bằng GitHub, **Add New → Project**, import cùng repo.
2. Branch **main**, Framework Preset **Other**, **Root Directory ở gốc repo**, không chọn frontend hoặc nhập đường dẫn J:\vi.
3. Repo đã có vercel.json. Nếu dashboard cần nhập thủ công:

| Cấu hình | Giá trị |
| --- | --- |
| Build Command | `node scripts/build_vercel.mjs` |
| Output Directory | `dist/vercel` |
| Install Command | Để trống, không cần package npm |

4. Thêm Environment Variable **API_BASE_URL** = URL Render thật, ví dụ `https://meeting-intelligence-xxxx.onrender.com`, áp dụng cho **Production**. Chỉ origin HTTPS, không thêm `/api`, query, token hay thông tin đăng nhập.
5. Deploy, lấy URL production ổn định dạng `https://meeting-intelligence-xxxx.vercel.app`.

**Không đưa LLM_API_KEY hoặc .env lên Vercel.** Build chỉ xuất tám asset frontend và ghi URL công khai vào config.js. Nếu không đặt API_BASE_URL, vẫn xem được demo đã lưu nhưng không phân tích mới được.

## 3. Nối hai nơi

1. Render → service → **Environment**, thêm **ALLOWED_ORIGINS** = URL production Vercel thật, ví dụ `https://meeting-intelligence-xxxx.vercel.app`.
2. Chỉ scheme + hostname, không đường dẫn. Nhiều origin ngăn cách bằng dấu phẩy; không dùng `*`. URL preview Vercel khác production nên cần thêm đúng origin preview nếu muốn dùng live trên preview.
3. **Save, rebuild and deploy** để Render đọc cấu hình mới.
4. Mở Vercel, Ctrl+F5. Nếu backend đang ngủ, đợi khoảng một phút rồi bấm **Kết nối lại backend**. Demo đã lưu vẫn xem được trong lúc chờ.
5. Chọn **LLM API · phân tích mới**, nhập transcript rồi phân tích. **Demo · kết quả LLM đã lưu** chỉ phát lại, không gọi Groq.

Nếu đổi API_BASE_URL trên Vercel, phải **Redeploy** vì config.js được sinh lúc build. Domain riêng: thêm origin frontend vào ALLOWED_ORIGINS, hostname backend vào ALLOWED_HOSTS, đổi API_BASE_URL.

## 4. Kiểm tra sau deploy

- Render `/healthz` trả 200; `/api/config` có `api_configured: true`, model nhưng không có khóa.
- Vercel tải đủ CSS/JS và ba màn làm việc.
- Chạy **Offline** T03 trước để kiểm tra CORS: quyết định reopened, 0 API call.
- Chạy **LLM API** với transcript ngắn: nhãn lượt mới, số API call/token khác 0. Không dùng playback làm bằng chứng live hoạt động.
- Rà soát, tải CSV/JSON, lưu/reload/khôi phục trên cùng origin. localStorage ở localhost, Vercel và Render nằm riêng, không tự đồng bộ.
- Render `/.env` và `/requirements.txt` bị 404; Vercel không xuất những file này.

## Giới hạn

Render Free ngủ sau 15 phút không có request; khi mở lại thường mất khoảng một phút. Trước demo nên mở link Render để backend khởi động, rồi chạy một mẫu ngắn. Lỗi hosting khác với lỗi dữ liệu hoặc quota Groq.

Đây là MVP dùng server Python đơn giản, xử lý một lượt phân tích mỗi lần, chưa có tài khoản/xác thực người gọi. CORS hạn chế origin trình duyệt, không phải đăng nhập: người gọi trực tiếp API vẫn có thể tiêu hao quota khi ENABLE_LIVE_API=true. Đặt false khi chỉ cần playback/offline. Chưa production-ready.

Đã kiểm tra local: **113 Python tests, 12 Node tests** và browser với hai origin khác nhau (GET, CORS preflight, POST offline), không gọi LLM. **Chưa deploy thực trên tài khoản Vercel/Render**; cần kiểm tra checklist phía trên sau khi deploy.

Tài liệu chính thức: [Render web services](https://render.com/docs/web-services), [Render Free](https://render.com/docs/free), [Render Blueprint](https://render.com/docs/blueprint-spec), [Vercel config](https://vercel.com/docs/project-configuration/vercel-json).

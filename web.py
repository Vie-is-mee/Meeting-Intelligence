"""Local inspection website. Run python web.py, then http://127.0.0.1:8765.

Only the dedicated frontend assets are served. The .env and project files
are never public routes. API credentials stay inside the Python process.
"""
from __future__ import annotations
import argparse
import json
import logging
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from meeting_intelligence.config import load_local_config
from meeting_intelligence.llm_client import LLMClient, LLMError
from meeting_intelligence.pipeline import analyze
from scripts.run_scenarios import evaluate

ROOT = Path(__file__).resolve().parent
ASSETS = {
    '/': ('index.html', 'text/html; charset=utf-8'),
    '/index.html': ('index.html', 'text/html; charset=utf-8'),
    '/styles.css': ('styles.css', 'text/css; charset=utf-8'),
    '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
    '/review.js': ('review.js', 'text/javascript; charset=utf-8'),
    '/review.css': ('review.css', 'text/css; charset=utf-8'),
    '/workspace.css': ('workspace.css', 'text/css; charset=utf-8'),
    '/demo-data.json': ('demo-data.json', 'application/json; charset=utf-8'),
}


def public_config():
    load_local_config()
    key = os.environ.get('LLM_API_KEY', '')
    return {
        'api_configured': bool(key and key != 'replace-with-private-token'
                               and os.environ.get('LLM_BASE_URL') and os.environ.get('LLM_MODEL')),
        'model': os.environ.get('LLM_MODEL', ''),
        'provider': urlparse(os.environ.get('LLM_BASE_URL', '')).hostname or '',
    }


def samples():
    entries = []
    for path in sorted((ROOT / 'samples').glob('T[0-9][0-9].txt')):
        expected = json.loads((ROOT / 'samples' / 'expected' / f'{path.stem}.json').read_text(encoding='utf-8'))
        entries.append(dict(expected, transcript=path.read_text(encoding='utf-8')))
    return entries


class InspectionServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, handler=None):
        super().__init__(address, handler or Handler)
        self.analysis_lock = threading.Lock()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        # Do not write transcript contents, request bodies or secrets to logs.
        pass

    def send_body(self, status, body, content_type):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy',
                         "default-src 'self'; script-src 'self'; style-src 'self'; "
                         "connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, status, payload):
        self.send_body(status, json.dumps(payload, ensure_ascii=False).encode('utf-8'),
                       'application/json; charset=utf-8')

    def local_request(self):
        allowed = {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}
        if self.headers.get('Host') not in allowed:
            self.send_json(403, {'error': 'Hãy mở website bằng địa chỉ localhost được in trong terminal.'})
            return False
        origin = self.headers.get('Origin')
        if origin and origin not in {f'http://{host}' for host in allowed}:
            self.send_json(403, {'error': 'Chỉ nhận yêu cầu từ giao diện local của ứng dụng.'})
            return False
        return True

    def do_GET(self):
        if not self.local_request():
            return
        path = urlparse(self.path).path
        if path in ASSETS:
            filename, content_type = ASSETS[path]
            self.send_body(200, (ROOT / 'frontend' / filename).read_bytes(), content_type)
        elif path == '/api/config':
            self.send_json(200, public_config())
        elif path == '/api/samples':
            self.send_json(200, {'samples': samples()})
        else:
            self.send_json(404, {'error': 'Không tìm thấy đường dẫn.'})

    def do_POST(self):
        if not self.local_request():
            return
        if self.path != '/api/analyze':
            self.send_json(404, {'error': 'Không tìm thấy đường dẫn.'})
            return
        if self.headers.get_content_type() != 'application/json':
            self.send_json(415, {'error': 'Dữ liệu gửi lên cần có định dạng JSON.'})
            return
        try:
            size = int(self.headers.get('Content-Length', '0'))
            if not 0 < size <= 600_000:
                self.send_json(413, {'error': 'Dữ liệu quá lớn hoặc trống. Giới hạn 600 KB mỗi yêu cầu.'})
                return
            payload = json.loads(self.rfile.read(size).decode('utf-8'))
            if not isinstance(payload, dict):
                raise ValueError('Yêu cầu cần là JSON object.')
            text = payload.get('transcript')
            engine = payload.get('engine', 'offline_rules')
            audit = payload.get('audit', True)
            if not isinstance(text, str) or not text.strip():
                raise ValueError('Hãy nhập nội dung transcript trước khi phân tích.')
            if len(text) > 100_000:
                raise ValueError('Bản local giới hạn 100.000 ký tự; hãy dùng transcript ngắn hơn.')
            if engine not in {'offline_rules', 'llm_api'} or type(audit) is not bool:
                raise ValueError('Chế độ phân tích hoặc tùy chọn audit không hợp lệ.')
        except (ValueError, UnicodeError) as exc:
            self.send_json(400, {'error': str(exc)})
            return
        if not self.server.analysis_lock.acquire(blocking=False):
            self.send_json(409, {'error': 'Đang có một lượt phân tích. Hãy chờ lượt hiện tại hoàn tất.'})
            return
        try:
            started = time.perf_counter()
            client = LLMClient() if engine == 'llm_api' else None
            result = analyze(text, engine=engine, client=client, audit=audit)
            evaluation = None
            for sample in samples():
                if sample['id'] == payload.get('sample_id') and sample['transcript'].strip() == text.strip():
                    errors = evaluate(result, sample)
                    evaluation = {'case': sample['id'], 'status': 'PASS' if not errors else 'FAIL',
                                  'errors': errors, 'expectations': sample['expectations'],
                                  'label': 'Bộ phát triển tổng hợp; không phải đánh giá độc lập.'}
                    break
            self.send_json(200, {
                'analysis': result.model_dump(),
                'duration_s': round(time.perf_counter() - started, 2),
                'api_calls': client.call_count if client else 0,
                'token_usage': client.token_usage if client else {},
                'model': client.model if client else None,
                'audit_enabled': audit if client else False,
                'evaluation': evaluation,
            })
        except (LLMError, ValueError) as exc:
            self.send_json(422, {'error': str(exc)})
        except Exception:
            logging.exception('Unexpected local analysis error')
            self.send_json(500, {'error': 'Lỗi xử lý nội bộ. Xem terminal đang chạy web.py để kiểm tra.'})
        finally:
            self.server.analysis_lock.release()


def main():
    parser = argparse.ArgumentParser(description='Website local để kiểm tra lõi Trí tuệ cuộc họp')
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    load_local_config()
    try:
        server = InspectionServer(('127.0.0.1', args.port))
    except OSError:
        parser.exit(1, f'Không mở được cổng {args.port}. Thử python web.py --port 8766\n')
    print(f'Meeting Intelligence: http://127.0.0.1:{server.server_port}', flush=True)
    print('Nhấn Ctrl+C để dừng. Khóa API chỉ được đọc ở Python.', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()

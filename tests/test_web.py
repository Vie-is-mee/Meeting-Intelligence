"""HTTP tests of the local UI's real backend; no paid/model requests."""
import json
import os
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path
from unittest.mock import patch

from meeting_intelligence.config import load_local_config
from web import InspectionServer, public_config


class ConfigTests(unittest.TestCase):
    def test_dotenv_loads_without_overriding_environment(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / '.env').write_text('LLM_API_KEY=private-test-value\nLLM_MODEL=local-model\n', encoding='utf-8')
            with patch('meeting_intelligence.config.PROJECT_ROOT', root), \
                 patch.dict(os.environ, {'LLM_MODEL': 'environment-model'}, clear=True):
                load_local_config()
                self.assertEqual(os.environ['LLM_API_KEY'], 'private-test-value')
                self.assertEqual(os.environ['LLM_MODEL'], 'environment-model')

    def test_public_configuration_never_returns_key(self):
        with patch('web.load_local_config'), patch.dict(os.environ, {
            'LLM_API_KEY': 'private-test-value',
            'LLM_MODEL': 'model', 'LLM_BASE_URL': 'https://api.groq.com/openai/v1'
        }, clear=True):
            config = public_config()
            self.assertTrue(config['api_configured'])
            self.assertNotIn('private-test-value', json.dumps(config))
            self.assertEqual(config['provider'], 'api.groq.com')


class WebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = InspectionServer(('127.0.0.1', 0))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def request(self, path, payload=None, headers=None):
        data = json.dumps(payload).encode() if payload is not None else None
        request = urllib.request.Request(self.base + path, data=data,
                                         headers=headers or {'Content-Type': 'application/json'})
        try:
            response = urllib.request.urlopen(request, timeout=10)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            return response.status, response.read(), response.headers

    def test_page_and_assets_are_served(self):
        for path, mime in [('/', 'text/html'), ('/app.js', 'text/javascript'), ('/styles.css', 'text/css'), ('/review.js','text/javascript'), ('/review.css','text/css')]:
            status, body, headers = self.request(path)
            self.assertEqual(status, 200)
            self.assertIn(mime, headers['Content-Type'])
            self.assertTrue(body)

    def test_secret_and_arbitrary_project_files_are_not_served(self):
        for path in ['/.env', '/requirements.txt', '/meeting_intelligence/llm_client.py', '/../.env']:
            status, _, _ = self.request(path)
            self.assertEqual(status, 404)

    def test_offline_analysis_runs_real_pipeline_and_evaluator(self):
        status, body, _ = self.request('/api/samples')
        sample = next(s for s in json.loads(body)['samples'] if s['id'] == 'T03')
        status, body, _ = self.request('/api/analyze', {
            'transcript': sample['transcript'], 'engine': 'offline_rules',
            'audit': True, 'sample_id': 'T03'
        })
        self.assertEqual(status, 200)
        actual = json.loads(body)
        self.assertEqual(actual['analysis']['records'][0]['meeting_status'], 'reopened')
        self.assertEqual(actual['evaluation']['status'], 'PASS')
        self.assertEqual(actual['api_calls'], 0)

    def test_modified_sample_is_not_scored_as_original(self):
        status, body, _ = self.request('/api/analyze', {
            'transcript': 'Chốt phương án B', 'engine': 'offline_rules', 'sample_id': 'T03'
        })
        self.assertEqual(status, 200)
        self.assertIsNone(json.loads(body)['evaluation'])

    def test_empty_or_invalid_input_is_rejected(self):
        for payload in [{'transcript': ''}, {'transcript': 'hello', 'audit': 'false'},
                        {'transcript': 'hello', 'engine': 'fake'}, []]:
            status, _, _ = self.request('/api/analyze', payload)
            self.assertEqual(status, 400)

    def test_cross_origin_analysis_is_rejected(self):
        status, _, _ = self.request('/api/analyze', {'transcript': 'Chốt B'},
                                    {'Content-Type': 'application/json', 'Origin': 'https://other.example'})
        self.assertEqual(status, 403)

    def test_concurrent_analysis_is_rejected_without_calling_model(self):
        self.server.analysis_lock.acquire()
        try:
            status, _, _ = self.request('/api/analyze', {
                'transcript': 'Chốt B', 'engine': 'offline_rules'
            })
            self.assertEqual(status, 409)
        finally:
            self.server.analysis_lock.release()

    def test_provider_errors_are_reported_without_fallback(self):
        from meeting_intelligence.llm_client import LLMError
        with patch('web.LLMClient', side_effect=LLMError('Thiếu cấu hình API')):
            status, body, _ = self.request('/api/analyze', {
                'transcript': 'Chốt B', 'engine': 'llm_api'
            })
        self.assertEqual(status, 422)
        self.assertEqual(json.loads(body)['error'], 'Thiếu cấu hình API')

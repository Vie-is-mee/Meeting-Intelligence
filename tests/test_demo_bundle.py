"""Recorded demo is exact historical output, labelled separately from new API calls."""
import hashlib
import json
import unittest
import threading
import urllib.error
import urllib.request
from pathlib import Path
from web import InspectionServer

ROOT=Path(__file__).resolve().parents[1]


class DemoBundleTests(unittest.TestCase):
    def test_recorded_predictions_match_frozen_run_and_reviews(self):
        raw=(ROOT/'docs/evaluation/final_regression_round5_retry2.json').read_bytes()
        original={c['id']:c for c in json.loads(raw)['cases']}
        demo=json.loads((ROOT/'frontend/demo-data.json').read_text(encoding='utf-8'))
        self.assertEqual(demo['run_sha256'],hashlib.sha256(raw).hexdigest())
        self.assertEqual(len(demo['cases']),8)
        self.assertEqual(sum(c['review']['verdict']=='PASS' for c in demo['cases']),4)
        for case in demo['cases']:
            self.assertEqual(case['result']['analysis'],original[case['id']]['output'])
            self.assertEqual(case['result']['source_mode'],'recorded')
            self.assertEqual(case['result']['api_calls'],0)
            self.assertEqual(case['result']['provenance']['historical_api_calls'],2)


class DemoRouteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=InspectionServer(('127.0.0.1',0))
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
        cls.base=f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown(); cls.server.server_close(); cls.thread.join(timeout=2)

    def request(self,path,payload=None):
        request=urllib.request.Request(self.base+path,
            data=json.dumps(payload).encode() if payload is not None else None,
            headers={'Content-Type':'application/json'})
        try: response=urllib.request.urlopen(request,timeout=10)
        except urllib.error.HTTPError as error: response=error
        with response: return response.status,response.read(),response.headers

    def test_public_demo_asset_has_recorded_label(self):
        status,body,headers=self.request('/demo-data.json')
        self.assertEqual(status,200)
        self.assertIn('application/json',headers['Content-Type'])
        self.assertEqual(json.loads(body)['mode'],'recorded')

    def test_recorded_cannot_be_submitted_as_live_backend_engine(self):
        status,_,_=self.request('/api/analyze',{'transcript':'Chốt A','engine':'recorded'})
        self.assertEqual(status,400)

"""M3 staging HTTP smoke: source identity, C2 live route, and private files blocked."""
import json
import threading
import unittest
from unittest.mock import patch
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from web import InspectionServer, release_identity

class StubLLM:
    call_count=1
    token_usage={}
    model="stub-no-provider"
    def completion_json(self, *args, **kwargs):
        return {"events":[]}

class TestStaging(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=InspectionServer(("127.0.0.1",0),public=False)
        cls.thread=threading.Thread(target=cls.server.serve_forever,daemon=True)
        cls.thread.start()
        cls.base="http://127.0.0.1:"+str(cls.server.server_port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=3)

    def get(self,path):
        with urlopen(self.base+path,timeout=5) as r:
            return r.status,r.read()

    def test_version_proves_m3_core(self):
        code,body=self.get("/api/version")
        data=json.loads(body)
        self.assertEqual(code,200)
        self.assertEqual(data["mission"],"M3")
        self.assertEqual(data["change_request"],"C2")
        self.assertEqual(len(data["core_sha256"]),4)
        self.assertEqual(len(data["core_sha256"]["meeting_intelligence/ambiguity.py"]),64)
        self.assertGreaterEqual(len(data["source_commit"]),7)
        self.assertNotEqual(data["source_commit"],"unknown")

    def test_m3_web_assets_include_c2_load_and_m3_label(self):
        _,page=self.get("/")
        self.assertIn(b'id="load-c2"',page)
        self.assertIn(b"Mission 3",page)
        _,js=self.get("/app.js")
        self.assertIn(b"load-c2",js)

    def test_http_post_c2_action_keeps_null_owner_due_and_evidence(self):
        data=json.dumps({"transcript":"Minh: Cái này team mình xử lý nhé.",
                         "engine":"llm_api","audit":False},ensure_ascii=False).encode("utf-8")
        request=Request(self.base+"/api/analyze",data=data,
                        headers={"Content-Type":"application/json"},method="POST")
        with patch("web.LLMClient",StubLLM):
            with urlopen(request,timeout=8) as res:
                out=json.load(res)
        actions=[r for r in out["analysis"]["records"] if r["kind"]=="action"]
        self.assertEqual(len(actions),1)
        self.assertEqual(actions[0]["meeting_status"],"unverified")
        self.assertIsNone(actions[0]["owner"])
        self.assertIsNone(actions[0]["due_raw"])
        self.assertEqual(actions[0]["review_status"],"needs_review")
        self.assertEqual(actions[0]["evidence_ids"],["L001"])

    def test_env_and_project_file_unavailable_on_http(self):
        for path in ("/.env","/README.md","/datasets/mission3_c2_v1.json"):
            with self.assertRaises(HTTPError) as err:
                self.get(path)
            self.assertEqual(err.exception.code,404)

if __name__=="__main__":
    unittest.main()

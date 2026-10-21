"""Stage 0.5 integrity tests: labels frozen BEFORE candidate M3 outputs.

These tests do not call API and do not pretend to measure LLM accuracy.
"""
from __future__ import annotations
import hashlib
import json
import unittest
from pathlib import Path
from meeting_intelligence.parser import parse_transcript

ROOT=Path(__file__).resolve().parents[1]

class Stage05IntegrityTests(unittest.TestCase):
    def setUp(self):
        self.dataset_path=ROOT/"datasets/mission3_before_after_v1.json"
        self.labels_path=ROOT/"datasets/mission3_before_after_labels_v1.json"
        self.manifest=json.loads((ROOT/"docs/evaluation/mission3/frozen_manifest_v1.json").read_text(encoding="utf-8"))
        self.dataset=json.loads(self.dataset_path.read_text(encoding="utf-8"))
        self.labels=json.loads(self.labels_path.read_text(encoding="utf-8"))

    def test_frozen_hashes(self):
        self.assertEqual(self.manifest["inputs_sha256"],hashlib.sha256(self.dataset_path.read_bytes()).hexdigest())
        self.assertEqual(self.manifest["labels_sha256"],hashlib.sha256(self.labels_path.read_bytes()).hexdigest())

    def test_case_ids_locked_one_to_one(self):
        ids=[x["id"] for x in self.dataset["cases"]]
        self.assertEqual(ids, self.manifest["cases"])
        self.assertEqual(ids, [x["id"] for x in self.labels["cases"]])
        self.assertEqual(len(ids),len(set(ids)))
        self.assertEqual(len(ids),4)

    def test_transcripts_match_predeclared_fixtures_and_source_ids(self):
        for item,annot in zip(self.dataset["cases"],self.labels["cases"]):
            with self.subTest(case=item["id"]):
                p=ROOT/"samples/mission3"/(item["id"]+".txt")
                self.assertEqual(item["transcript"],p.read_text(encoding="utf-8").strip())
                self.assertEqual(item["split"],"development")
                allowed={u.id for u in parse_transcript(item["transcript"])}
                for rec in annot["required"]+annot.get("optional",[]):
                    self.assertTrue(set(rec["source_ids"]) <= allowed,rec)
                    self.assertIn(rec["kind"],{"decision","action","issue","request","feedback","knowledge"})

    def test_no_independent_benchmark_claim(self):
        self.assertFalse(self.manifest["independent_benchmark"])
        self.assertEqual(self.labels["review_provenance"].startswith("assistant-authored"),True)
        self.assertNotIn("M3-CR01",self.manifest["cases"])

    def test_merged_remote_baseline_if_present(self):
        path=ROOT/"docs/evaluation/mission3/m2_remote_baseline_v1.json"
        if not path.exists():
            self.skipTest("Hosted M2 API artifact not present in checkout")
        item=json.loads(path.read_text(encoding="utf-8"))
        self.assertFalse(item["source_revision_attested_by_remote"])
        self.assertEqual(item["frozen_input_sha256"],self.manifest["inputs_sha256"])
        self.assertEqual(item["frozen_labels_sha256"],self.manifest["labels_sha256"])
        self.assertEqual(item["case_order"],self.manifest["cases"])
        self.assertEqual(len(item["results"]),4)
        self.assertEqual(len({r["id"] for r in item["results"]}),4)
        self.assertTrue(all(r["status"]=="COMPLETED" for r in item["results"]))

if __name__=="__main__":
    unittest.main()

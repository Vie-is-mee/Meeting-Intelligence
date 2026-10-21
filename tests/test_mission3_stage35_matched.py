"""Checks for source-attested M2 exact-tag baseline evidence.

No LLM API usage. Do not alter frozen input/labels or raw outputs.
"""
import unittest
from pathlib import Path
from scripts.merge_mission2_local_baseline import merge_m2

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/"docs/evaluation/mission3"
A=D/"m2_exact_tag_E02_local_run1.json"
B=D/"m2_exact_tag_E01_R01_local_run1.json"
C=D/"m2_exact_tag_K01_local_run1.json"

class MatchedSourceBaselineTests(unittest.TestCase):
    def test_complete_exact_m2_tag_merge(self):
        report=merge_m2([A,B,C])
        self.assertEqual(report["manifest"]["version"],"m2")
        self.assertEqual(report["manifest"]["transport"],"local")
        self.assertEqual(report["manifest"]["core_commit"],
                         "439f672a3204238100158570ebcf80f0551b85fd")
        self.assertEqual([r["id"] for r in report["results"]],
                         ["M3-E01","M3-E02","M3-R01","M3-K01"])
        self.assertEqual(report["api_calls"],8)
        self.assertEqual(report["tokens_reported"],17771)
        self.assertEqual([r["status"] for r in report["results"]],["COMPLETED"]*4)
        self.assertFalse(report["assistant_semantic_review"]=="COMPLETE")

    def test_duplicate_source_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"duplicate"):
            merge_m2([A,B,B,C])

    def test_incomplete_set_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"All four"):
            merge_m2([A,B])

    def test_hosted_m2_not_attested_to_submitted_source(self):
        with self.assertRaisesRegex(ValueError,"Only real local M2"):
            merge_m2([D/"m2_remote_baseline_v1.json",A,C])

if __name__=="__main__":
    unittest.main()

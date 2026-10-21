"""Stage 3.5 evaluation harness guardrails.

No API calls. Tests prevent replay/remote data being mislabeled as local fresh M3.
"""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from scripts import build_stage35_review_packet as packet
from scripts import stage35_readiness as ready

class Stage35HarnessTests(unittest.TestCase):
    def test_readiness_preflight_and_source_hashes(self):
        report=ready.inspect()
        self.assertTrue(all(report["checks"].values()))
        self.assertEqual(report["m2_tag_commit"],report["m2_worktree_commit"])
        self.assertEqual(len(report["frozen_case_ids"]),4)
        self.assertTrue(all(len(v)==64 for v in report["m3_source_sha256"].values()))
        self.assertIn(report["state"],{"READY_NOT_EXECUTED","BLOCKED_MISSING_PRIVATE_LLM_SETTINGS"})
        self.assertEqual(report["test_type"],"preflight_only_NO_LLM_CALLS")

    def test_packet_uses_only_archived_events_in_default_mode(self):
        text=packet.packet()
        self.assertIn("ARCHIVED_M2_EVENT_REPLAY_ONLY__NO_FRESH_M3_INFERENCE",text)
        self.assertIn("NOT SEMANTICALLY REVIEWED",text)
        self.assertIn("M3-K01",text)
        self.assertIn("M3-E01",text)
        self.assertIn("Do NOT silently edit locked gold",text)
        self.assertNotIn(chr(92)+"`",text)

    def test_reject_existing_hosted_m2_as_fresh_m3(self):
        with self.assertRaises(AssertionError):
            packet.packet(packet.BASE)

    def test_reject_offline_or_remote_m3_manifest(self):
        manifest=packet.read(packet.FREEZE)
        for transport in ("offline","remote"):
            with self.subTest(transport=transport):
                fake={"manifest":{"version":"m3","transport":transport,
                      "frozen_input_sha256":manifest["inputs_sha256"],
                      "frozen_labels_sha256":manifest["labels_sha256"],
                      "cases":manifest["cases"]},"results":[]}
                with tempfile.TemporaryDirectory() as root:
                    loc=Path(root)/"non_fresh.json"
                    loc.write_text(json.dumps(fake),encoding="utf-8")
                    with self.assertRaisesRegex(AssertionError,"Refusing a remote/offline"):
                        packet.packet(loc)


    def test_merger_refuses_remote_as_m3_provider(self):
        from scripts import merge_mission3_fresh_runs as merger
        with self.assertRaises(ValueError):
            merger.merge([packet.BASE, packet.BASE])

    def test_merger_rejects_duplicate_case_and_config_mismatch(self):
        from scripts import merge_mission3_fresh_runs as merger
        seed=packet.read(packet.FREEZE)
        base={"manifest":{"version":"m3","transport":"local","core_commit":"candidate",
              "source_files_sha256":{"meeting_intelligence/pipeline.py":"abc"},
              "frozen_input_sha256":seed["inputs_sha256"],"frozen_labels_sha256":seed["labels_sha256"],
              "audit":"on","cases":["M3-E01","M3-E02"]},
              "model":"openai/gpt-oss-120b",
              "generation_settings":{"temperature":0.6},
              "complete":True,
              "results":[{"id":"M3-E01","status":"ERROR"},{"id":"M3-E02","status":"COMPLETED"}]}
        with tempfile.TemporaryDirectory() as directory:
            p=Path(directory)/"one.json";q=Path(directory)/"two.json"
            p.write_text(json.dumps(base),encoding="utf-8")
            q.write_text(json.dumps(base),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"duplicate"):
                merger.merge([p,q])
            other=json.loads(json.dumps(base))
            other["manifest"]["cases"]=["M3-R01","M3-K01"]
            other["results"]=[{"id":"M3-R01","status":"COMPLETED"},{"id":"M3-K01","status":"COMPLETED"}]
            other["generation_settings"]["temperature"]=0.3
            q.write_text(json.dumps(other),encoding="utf-8")
            with self.assertRaisesRegex(ValueError,"Different source"):
                merger.merge([p,q])
            other["generation_settings"]["temperature"]=0.6
            q.write_text(json.dumps(other),encoding="utf-8")
            merged=merger.merge([p,q])
            self.assertEqual([x["id"] for x in merged["results"]],seed["cases"])
            self.assertEqual(merged["results"][0]["status"],"ERROR")
            self.assertFalse(merged["semantically_reviewed"])

if __name__=="__main__":unittest.main()

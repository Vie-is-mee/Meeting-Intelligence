import unittest
from pathlib import Path
from meeting_intelligence.parser import parse_transcript
from meeting_intelligence.pipeline import analyze
from meeting_intelligence.models import Event, Utterance
from meeting_intelligence.resolver import resolve_events
from meeting_intelligence.verifier import verify_records

ROOT=Path(__file__).resolve().parents[1]

class ParserTests(unittest.TestCase):
    def test_no_speaker_or_clock_required(self):
        out=parse_transcript('Đề xuất A\nChưa chốt\n')
        self.assertEqual([x.id for x in out],['L001','L002'])
        self.assertIsNone(out[0].speaker)
    def test_named_speakers_and_normalized_id(self):
        out=parse_transcript('L013 | Minh | Đề xuất A\n09:30 - Lan: Chốt B')
        self.assertEqual([x.id for x in out],['L001','L002'])
        self.assertEqual([x.speaker for x in out],['Minh','Lan'])
        self.assertEqual(out[1].timestamp,'09:30')
    def test_empty(self):
        with self.assertRaises(ValueError):parse_transcript(' \n')

class TemporalTests(unittest.TestCase):
    def test_T02_offline_decision_B(self):
        result=analyze((ROOT/'samples'/'T02.txt').read_text(encoding='utf-8'),'offline_rules')
        decision=next(x for x in result.records if x.kind=='decision')
        self.assertEqual(decision.meeting_status,'agreed')
        self.assertIn('B',decision.content)
        self.assertIn('L004',decision.evidence_ids)
        self.assertEqual(decision.authority_status,'unknown')
    def test_T03_offline_reopens(self):
        result=analyze((ROOT/'samples'/'T03.txt').read_text(encoding='utf-8'),'offline_rules')
        decision=next(x for x in result.records if x.kind=='decision')
        self.assertEqual(decision.meeting_status,'reopened')
        self.assertEqual(decision.review_status,'needs_review')
        self.assertIn('L003',decision.counter_evidence_ids)
    def test_other_topic_open_does_not_reopen_decision(self):
        result=analyze((ROOT/'samples'/'T01.txt').read_text(encoding='utf-8'),'offline_rules')
        decision=next(x for x in result.records if x.kind=='decision')
        self.assertEqual(decision.meeting_status,'agreed')
        self.assertEqual(decision.content,'Phương án B')
    def test_explicit_unresolved_is_not_reopening(self):
        lines=parse_transcript('Chưa chốt ngày phát hành')
        ev=Event(kind='decision',event_type='unresolved',issue_key='release_date',topic='Ngày phát hành',source_ids=['L001'])
        record=resolve_events([ev],lines)[0]
        self.assertEqual(record.meeting_status,'open')
    def test_T04_does_not_conflate_approval_with_meeting_agreement(self):
        result=analyze((ROOT/'samples'/'T04.txt').read_text(encoding='utf-8'),'offline_rules')
        decision=next(x for x in result.records if x.kind=='decision')
        self.assertEqual(decision.meeting_status,'agreed')
        self.assertEqual(decision.execution_status,'blocked')
        self.assertEqual(decision.authority_status,'unknown')
    def test_verifier_removes_owner_not_backed_by_source(self):
        lines=parse_transcript('Lan: Minh sẽ kiểm thử.')
        ev=Event(kind='action',event_type='assignment',issue_key='kiem_thu',topic='Kiểm thử',source_ids=['L001'],owner='Người không có trong transcript')
        result=verify_records(resolve_events([ev],lines),lines)[0]
        self.assertIsNone(result.owner)
        self.assertEqual(result.review_status,'needs_review')
    def test_temporal_reopen_after_agreement(self):
        lines=parse_transcript('Chốt B\nHôm nay chưa chốt quyết định')
        ev=[Event(kind='decision',event_type='agreement',issue_key='x',topic='x',source_ids=['L001'],value='B'),
            Event(kind='decision',event_type='reopen',issue_key='x',topic='x',source_ids=['L002'])]
        r=resolve_events(ev,lines)[0]
        self.assertEqual(r.meeting_status,'reopened')
        self.assertEqual(r.counter_evidence_ids,['L002'])

if __name__=='__main__':unittest.main()

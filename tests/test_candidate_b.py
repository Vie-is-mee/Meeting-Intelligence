import copy
import unittest
from meeting_intelligence.extractor import normalize_named_assignment_events,extract_events
from meeting_intelligence.llm_client import LLMError
from meeting_intelligence.parser import parse_transcript
from meeting_intelligence.models import Event
from meeting_intelligence.resolver import resolve_events

class CandidateBNormalizationTests(unittest.TestCase):
    def build(self,source='Mai lập bảng đối soát, hạn sáng mai.',accept='Tôi nhận lập bảng đó.',kind='request',key='task'):
        lines=parse_transcript('Linh: '+source+'\nMai: '+accept+'\nLinh: Hủy việc lập bảng đối soát, bỏ hạn sáng mai.')
        events=[Event(issue_key='task',topic='bảng',kind=kind,event_type='request_made' if kind=='request' else 'proposal',value='lập bảng đối soát',source_ids=['L001']),Event(issue_key=key,topic='bảng',kind='action',event_type='assignment',value='lập bảng đối soát',owner='Mai',source_ids=['L002']),Event(issue_key=key,topic='bảng',kind='action',event_type='action_cancelled',source_ids=['L003'],clear_fields=['due_raw'])]
        return lines,events
    def test_named_instruction_and_acceptance_have_one_cancelled_action_not_active_request(self):
        for kind in ['request','decision']:
            lines,events=self.build(kind=kind);before=copy.deepcopy(events);notes=[]
            repaired=normalize_named_assignment_events(events,lines,warnings=notes)
            records=resolve_events(repaired,lines)
            self.assertEqual(events,before);self.assertEqual(len(repaired),len(events));self.assertEqual(len(records),1)
            self.assertEqual((records[0].kind,records[0].meeting_status,records[0].owner),('action','cancelled','Mai'));self.assertTrue(notes)
    def test_business_requirement_is_not_removed_when_implementation_cancelled(self):
        lines,events=self.build(source='Cần lập bảng đối soát.')
        self.assertEqual(normalize_named_assignment_events(events,lines),events)
    def test_different_key_and_content_are_not_merged(self):
        lines,events=self.build(key='another_task');self.assertEqual(normalize_named_assignment_events(events,lines),events)
        lines,events=self.build();events[1].value='lập bảng đối soát cho kho khác'
        self.assertEqual(normalize_named_assignment_events(events,lines),events)
    def test_questions_hypotheticals_and_nonacceptance_are_not_promoted(self):
        for source,accept in [('Mai lập bảng đối soát được không?','Tôi nhận lập bảng đó.'),('Nếu rảnh Mai lập bảng đối soát.','Tôi nhận lập bảng đó.'),('Mai lập bảng đối soát.','Tôi chưa nhận việc đó.')]:
            lines,events=self.build(source=source,accept=accept)
            self.assertEqual(normalize_named_assignment_events(events,lines),events)
    def test_actual_condition_is_preserved_when_only_type_is_corrected(self):
        lines,events=self.build();events[0].condition='khi được cấp dữ liệu'
        repaired=normalize_named_assignment_events(events,lines)
        self.assertEqual(repaired[0].condition,'khi được cấp dữ liệu')
    def test_speaker_metadata_is_not_invented_supporter(self):
        lines,events=self.build();events[0].supporter='Linh'
        self.assertIsNone(normalize_named_assignment_events(events,lines)[0].supporter)
    def test_literal_task_description_survives_null_acceptance_before_group_validation(self):
        lines,events=self.build();events[0].value='Mai lập bảng đối soát';events[1].value=None
        class Client:
            def completion_json(self,*args):return {'events':[e.model_dump() for e in events]}
        parsed=extract_events(lines,Client());records=resolve_events(parsed,lines)
        self.assertEqual(len(records),1);self.assertEqual(records[0].meeting_status,'cancelled')
        self.assertEqual(records[0].content,'Mai lập bảng đối soát')
    def test_unrelated_request_cannot_supply_an_orphan_action_description(self):
        lines,events=self.build(source='Cần lập bảng đối soát.');events[1].value=None
        class Client:
            def completion_json(self,*args):return {'events':[e.model_dump() for e in events]}
        with self.assertRaises(LLMError):extract_events(lines,Client())

if __name__=='__main__':unittest.main()

import unittest
from meeting_intelligence.pipeline import analyze
from meeting_intelligence.llm_client import LLMError

class MockClient:
    """Contract-only fake; NOT evidence of a real model's accuracy."""
    def completion_json(self,system,user):
        return {'events':[
            {'issue_key':'lua_chon','topic':'Chọn phương án','kind':'decision','event_type':'proposal','source_ids':['L001'],'value':'A'},
            {'issue_key':'lua_chon','topic':'Chọn phương án','kind':'decision','event_type':'agreement','source_ids':['L002'],'value':'B'},
            {'issue_key':'lua_chon','topic':'Chọn phương án','kind':'decision','event_type':'reopen','source_ids':['L003']},
        ]}

class InvalidClient:
    def completion_json(self,system,user):
        return {'events':[{'issue_key':'i','topic':'i','kind':'decision','event_type':'agreement','source_ids':['L999'],'value':'B'}]}

class LLMContractTests(unittest.TestCase):
    def test_empty_content_is_rejected_even_with_valid_topic_and_source(self):
        class EmptyContentClient:
            def completion_json(self, system, user):
                return {'events': [{'issue_key': 'menu', 'topic': 'menu',
                                   'kind': 'feedback', 'event_type': 'feedback_given',
                                   'source_ids': ['L001'], 'value': None}]}
        with self.assertRaisesRegex(LLMError, 'thiếu nội dung'):
            analyze('Menu khó tìm', client=EmptyContentClient(), audit=False)

    def test_mock_pipeline(self):
        out=analyze('Đề xuất A\nChốt B\nHôm nay chưa chốt','llm_api',client=MockClient(),audit=False)
        self.assertEqual(out.records[0].meeting_status,'reopened')
        self.assertEqual(out.records[0].counter_evidence_ids,['L003'])
    def test_invalid_reference_fails_closed(self):
        with self.assertRaises(LLMError):
            analyze('Đề xuất A','llm_api',client=InvalidClient())

if __name__=='__main__':unittest.main()

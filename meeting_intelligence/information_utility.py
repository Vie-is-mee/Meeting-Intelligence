"""Conservative post-audit information-utility labels for meeting outputs.

A *reusable_candidate* means an in-meeting practice worth reviewing, NOT a
verified company fact or published knowledge-base entry. The source may be
incorrect. Never set authority_status=verified or human_review=confirmed here.
No LLM calls. No semantic entailment claim.
"""
from __future__ import annotations

import re

from .models import ResultRecord, Utterance

_UNCERTAIN = re.compile(
    r'(?i)\b(?:nghe\s+nói|đồn\s+rằng|theo\s+tin\s+đồn|chưa\s+(?:kiểm\s+chứng|'
    r'xác\s+minh|benchmark|thử\s+nghiệm)|không\s+chắc|có\s+lẽ|'
    r'phỏng\s+đoán|giả\s+sử|chỉ\s+là\s+(?:giả\s+thuyết|ý\s+kiến|mẫu)|'
    r'chưa\s+có\s+(?:dữ\s+liệu|bằng\s+chứng))\b'
)
_PRACTICE = re.compile(
    r'(?i)\b(?:kinh\s+nghiệm|bài\s+học|nguyên\s+tắc|quy\s+trình|'
    r'best\s+practice|khuyến\s+nghị|nên\s+(?:dùng|tách|kiểm|giữ|thiết\s+lập)|'
    r'cần\s+(?:dùng|sử\s+dụng|tách|kiểm|giữ|xác\s+thực|thiết\s+lập)|'
    r'phải\s+(?:dùng|sử\s+dụng|tách|kiểm|giữ|xác\s+thực|thiết\s+lập))\b'
)
_HISTORIC = re.compile(
    r'(?i)\b(?:trước\s+đây|hồi\s+trước|ngày\s+xưa|'
    r'biên\s+bản\s+cũ|cuộc\s+họp\s+trước|đã\s+từng)\b'
)
_DISPROVE = re.compile(
    r'(?i)\b(?:không\s+đúng|sai|không\s+chính\s+xác|'
    r'không\s+áp\s+dụng|rút\s+lại|bác\s+bỏ|chưa\s+kiểm\s+chứng|'
    r'không\s+có\s+bằng\s+chứng)\b'
)
_GENERIC = {
    'trước','đây','phải','chúng','mình','dùng','việc','này','theo',
    'cần','khi','không','được','của','cách','nhóm','triển','khai','trong',
    'với','một','kinh','nghiệm','nên','thì','đã','làm','cho','lần','sau',
    'chưa','kiểm','chứng','thực','hiện','phương','án','có','để'
}


def _meaningful_terms(value: str) -> set[str]:
    return {word for word in re.findall(r'\w+', value.casefold())
            if len(word) >= 3 and word not in _GENERIC}


def _later_explicit_counter_source(record: ResultRecord,
                                   utterances: list[Utterance],
                                   ids: list[str]) -> str | None:
    """Look for a *later* explicitly disconfirming statement on this subject.

    Two specific shared terms are required; otherwise abstain from claiming a
    contradiction. Paraphrases and implicit corrections need a semantic audit.
    """
    positions = {u.id: u.order for u in utterances}
    latest_source = max((positions[s] for s in ids if s in positions), default=0)
    subject = _meaningful_terms(record.content or '') | _meaningful_terms(record.topic)
    for u in utterances:
        if u.order <= latest_source or not _DISPROVE.search(u.text):
            continue
        if len(subject & _meaningful_terms(u.text)) >= 2:
            return u.id
    return None


def classify_information_utility(records: list[ResultRecord],
                                 utterances: list[Utterance]) -> list[ResultRecord]:
    """Attach purpose, exact source provenance and conservative review status.

    The four labels are about HOW to use information, *not* whether it is true:
      current_work        -- active task/requirement/decision/open issue/feedback
      historical_context  -- withdrawn/cancelled/resolved or recalled old fact
      reusable_candidate  -- source-grounded process/technical practice to review
      needs_verification  -- uncertain assertion or unsupported/ambiguous content
    """
    lookup = {u.id: u for u in utterances}
    for record in records:
        # Each label has an auditable provenance; prefer the content sources.
        ids = list(dict.fromkeys(
            (record.field_evidence_ids.get('content') or record.evidence_ids)
            + ([] if record.kind == 'knowledge' else (
                record.field_evidence_ids.get('meeting_status', []) +
                record.field_evidence_ids.get('execution_status', [])))
        ))
        sources = [lookup[s].text for s in ids if s in lookup]
        record.field_evidence_ids['information_utility'] = [s for s in ids if s in lookup]
        record.information_utility = 'needs_verification'
        record.information_utility_note = 'Chưa đủ căn cứ phân loại mục đích sử dụng.'
        if record.kind == 'knowledge':
            origin = ' '.join(sources)
            # Source existence is a necessary but insufficient condition.
            if not sources or not record.content or record.meeting_status != 'unverified':
                record.information_utility_note = 'Thiếu nguồn/nội dung đáng tin cậy cho phát biểu tri thức.'
            else:
                disproof = _later_explicit_counter_source(record, utterances, ids)
                if _UNCERTAIN.search(origin) or _UNCERTAIN.search(record.content):
                    record.information_utility_note = 'Nguồn thừa nhận thông tin chưa kiểm chứng hoặc chỉ là lời nghe nói.'
                elif disproof:
                    record.counter_evidence_ids = list(dict.fromkeys(
                        record.counter_evidence_ids + [disproof]))
                    record.field_evidence_ids['information_utility'].append(disproof)
                    record.information_utility_note = (
                        'Có phát biểu phản chứng xuất hiện sau tại '+disproof+
                        '; cần người xác nhận, không lưu tri thức đã duyệt.')
                elif re.search(r'(?i)\b(?:biên\s+bản\s+cũ|cuộc\s+họp\s+trước)\b',origin):
                    record.information_utility = 'historical_context'
                    record.information_utility_note = 'Chỉ là nội dung được thuật lại từ cuộc họp/biên bản cũ, chưa được tái xác nhận.'
                elif _PRACTICE.search(origin) and _PRACTICE.search(record.content+' '+origin):
                    record.information_utility = 'reusable_candidate'
                    record.information_utility_note = (
                        'Nguồn nêu một nguyên tắc/kinh nghiệm thực hành; '
                        'chỉ là ứng viên tri thức, CHƯA được kiểm chứng và phê duyệt.')
                elif _HISTORIC.search(origin):
                    record.information_utility = 'historical_context'
                    record.information_utility_note = 'Nguồn chỉ ghi nhận bối cảnh hoặc lựa chọn từng dùng trước đây.'
                else:
                    record.information_utility_note = 'Phát biểu không đủ dấu hiệu là kinh nghiệm tái sử dụng đã kiểm chứng.'
            # All machine-extracted knowledge must explicitly enter human review.
            record.review_status = 'needs_review'
            record.authority_status = 'unknown'
            if record.information_utility == 'reusable_candidate':
                message = 'Ứng viên tri thức tái sử dụng CHƯA ĐƯỢC KIỂM CHỨNG; cần người xác nhận trước khi sử dụng.'
            elif record.information_utility == 'needs_verification':
                message = 'Phát biểu tri thức còn thiếu xác minh; không coi là sự thật của doanh nghiệp.'
            else:
                message = 'Bối cảnh lịch sử, không mặc định là quy tắc đang áp dụng.'
            if message not in record.warnings:
                record.warnings.append(message)
            continue

        if record.meeting_status == 'unverified' or record.review_status == 'needs_review' and not sources:
            record.information_utility_note = (
                'Thông tin nghiệp vụ chưa đủ căn cứ; cần đối chiếu câu nguồn.')
        elif record.meeting_status in {'cancelled','withdrawn','reported_resolved'}:
            record.information_utility = 'historical_context'
            record.information_utility_note = (
                'Giữ trạng thái/lịch sử; không phải cam kết cần thực hiện mới.')
        else:
            record.information_utility = 'current_work'
            record.information_utility_note = (
                'Dùng để theo dõi quyết định, việc, yêu cầu, vấn đề hoặc phản hồi '
                'hiện tại; trạng thái cuộc họp và rà soát vẫn có hiệu lực riêng.')
        # This classification never authenticates model assertions.
        record.authority_status = 'unknown'
    return records

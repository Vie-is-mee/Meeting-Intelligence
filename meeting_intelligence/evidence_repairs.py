"""Conservative repairs of explicit, literal source omissions; not semantic truth.

Keep provider events separately. Never infer a deadline removal from cancellation
alone or manufacture an agreement absent from the transcript.
"""
from __future__ import annotations
import re
from .models import Event, Utterance


def _norm(text: str | None) -> str:
    # Internal punctuation can change meaning (C versus C++, 2.0 versus 20).
    return ' '.join((text or '').casefold().split()).rstrip('.!;')


def _plain_assertion(text: str) -> bool:
    return not re.search(r'(?i)[?"“”]|\b(?:nếu|giả\s+sử|ví\s+dụ|trích\s+dẫn|biên\s+bản\s+cũ)\b', text)


def repair_explicit_source_updates(events: list[Event], utterances: list[Utterance], *, warnings=None) -> list[Event]:
    lookup = {u.id: u for u in utterances}
    at = lambda event: max(lookup[s].order for s in event.source_ids)
    repaired = list(events)
    for i, event in enumerate(events):
        if event.kind != 'action' or event.event_type != 'action_cancelled' or 'due_raw' in event.clear_fields:
            continue
        if event.due_raw is not None:
            continue  # Conflicting model update requires review, not arbitration.
        prior = [e for e in events if e.kind == 'action' and e.issue_key == event.issue_key
                 and e.event_type in {'assignment', 'reassignment'} and at(e) < at(event)]
        if not prior:
            continue
        assignment = max(prior, key=at)
        if not assignment.value or not assignment.due_raw:
            continue
        if any(e.kind == 'action' and e.issue_key == event.issue_key
               and e.event_type == 'deadline_change' and at(assignment) < at(e) < at(event)
               for e in events):
            continue  # Do not remove a newer date by matching an older assignment.
        for sid in event.source_ids:
            source = lookup[sid]
            if source.order != at(event) or not _plain_assertion(source.text):
                continue
            if sum(e.kind == 'action' and e.event_type == 'action_cancelled' and sid in e.source_ids for e in events) != 1:
                continue
            match = re.match(r'(?i)^hủy\s+việc\s+([^,;.?!]+?)(?:,\s*|\s+và\s+)(?:bỏ|xóa|hủy)\s+hạn\s+([^.;?!]+)', source.text)
            if not match or re.search(r'(?i)\b(?:không\s+bỏ|chưa\s+bỏ|giữ\s+hạn)\b', source.text):
                continue
            work, bound = _norm(match[1]), _norm(match[2])
            content = _norm(assignment.value)
            if not work or not (content == work or content.startswith(work + ' ')):
                continue
            if bound not in {'đã giao', _norm(assignment.due_raw)}:
                continue
            if not any(re.search(r'(?<!\w)' + re.escape(_norm(assignment.due_raw)) + r'(?!\w)',
                                 _norm(lookup[s].text)) for s in assignment.source_ids):
                continue
            repaired[i] = event.model_copy(update={'clear_fields': [*event.clear_fields, 'due_raw']})
            if warnings is not None:
                warnings.append('Bổ sung thao tác xóa hạn được nói rõ tại ' + sid
                                + ' cho đúng công việc đã trích; không xóa người nhận hoặc tự tạo sự kiện. Raw LLM giữ riêng.')
            break

    # Extend only the LAST already-extracted agreement with a later, verbatim
    # reaffirmation of its complete value. No fuzzy matching or new state event.
    for i, event in enumerate(repaired):
        if event.kind != 'decision' or event.event_type != 'agreement' or not event.value:
            continue
        same = [(j, e) for j, e in enumerate(repaired) if e.kind == 'decision' and e.issue_key == event.issue_key]
        if max(same, key=lambda pair: (at(pair[1]), pair[0]))[0] != i:
            continue
        if len({e.issue_key for e in repaired if e.kind == 'decision' and _norm(e.value) == _norm(event.value)}) != 1:
            continue
        candidates = []
        for source in utterances:
            if source.order <= at(event) or not _plain_assertion(source.text):
                continue
            if re.search(r'(?i)\b(?:không\s+chốt|chưa\s+chốt|mở\s+lại|rút\s+lại)\b', source.text):
                continue
            sentence = re.split(r'[.;!]', source.text, maxsplit=1)[0].strip()
            match = re.fullmatch(r'(?i)chốt\s+(.+)', sentence)
            if match and _norm(match[1]) == _norm(event.value):
                candidates.append(source)
        if candidates:
            source = max(candidates, key=lambda u: u.order)
            repaired[i] = event.model_copy(update={'source_ids': [*event.source_ids, source.id]})
            if warnings is not None:
                warnings.append('Bổ sung câu chốt nhắc lại nguyên nội dung quyết định tại ' + source.id
                                + '; giữ giá trị/trạng thái đã trích và raw LLM, không suy diễn lựa chọn mới.')
    return repaired

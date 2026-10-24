"""Deterministic temporal state transitions applied to LLM-identified events.

Important: explicit agreement is about what participants said, NOT organizational approval.
"""
from __future__ import annotations
from collections import defaultdict
import re
from .models import Event, ResultRecord, Utterance


def _explicit_cancel_owner_release(event: Event, source: dict[str, Utterance]) -> bool:
    """Only clear a historical assignee when cancellation literally releases them.

    'Hủy việc ... bỏ hạn' and 'chưa giao việc mới' are NOT owner removal.
    The extractor's clear_fields list is a hypothesis, not source evidence.
    """
    for sid in event.source_ids:
        line = source.get(sid)
        if not line:
            continue
        statement = line.text.casefold()
        if re.search(r'\b(?:bỏ|gỡ|xóa|rút|hủy)\s+(?:phân\s+công|vai\s+trò\s+phụ\s+trách)\b', statement):
            return True
        if re.search(r'\b(?:bỏ|gỡ|xóa)\s+\S+(?:\s+\S+){0,2}\s+khỏi\s+(?:vai\s+trò\s+)?(?:phụ\s+trách|phân\s+công)\b', statement):
            return True
        if re.search(r'\b(?:không\s+còn|thôi)\s+(?:giao|phân\s+công)\s+(?:cho\s+)?\S+', statement):
            return True
    return False


def _explicit_cancel_due_release(event: Event, source: dict[str, Utterance]) -> bool:
    """Honor literal cancellation of an existing due date, even if LLM omits clear_fields.

    Narrow source-phrase guard. Do not infer removal from cancellation alone,
    suggestions, or explicitly negated deadline removal.
    """
    for sid in event.source_ids:
        line = source.get(sid)
        if not line:
            continue
        sentence = line.text.casefold()
        clause_pattern = r"\b(?:bỏ|gỡ|xóa|huỷ|hủy)\s+(?:(?:cái|mốc)\s+)?(?:hạn|deadline)\b"
        for match in re.finditer(clause_pattern, sentence):
            segment = sentence[max(0, match.start() - 24):match.start()]
            if re.search(r"\b(?:không|chưa|đừng|chớ|nếu|có\s+nên)\s*$", segment):
                continue
            return True
    return False


def _source_grounded_task_pause(event: Event, record: ResultRecord,
                                source: dict[str, Utterance]) -> bool:
    """A literal, nonhypothetical pause on the SAME previously assigned task.

    Never infer this lifecycle event from deadline removal alone. Require a
    specific task phrase after 'tạm dừng/tạm hoãn' to overlap the task record.
    """
    stop={"tạm","dừng","hoãn","đình","chỉ","việc","công","phần","này",
          "đó","chuẩn","bị","sẽ","được","cho","để","của","làm","hạn",
          "deadline","hủy","bỏ","thứ","ngày","sau","trước","mình",
          "và","cần","tiếp","tục","triển","khai","xử","lý"}
    def tokens(text):
        return {word for word in re.findall(r"\w+",text.casefold())
                if len(word)>1 and word not in stop}
    task_terms=tokens(" ".join([record.content or "",record.topic]))
    if len(task_terms)<2:
        return False
    if not event.source_ids or any(s not in source for s in event.source_ids):
        return False
    for sid in event.source_ids:
        statement=source[sid].text.casefold()
        for match in re.finditer(
            r"\b(?:tạm\s+dừng|tạm\s+hoãn|đình\s+chỉ)"
            r"\s+(?:(?:công\s+việc|phần\s+việc|việc)\s+)?"
            r"(?P<task>[^,.;!?\n]{3,120})",statement
        ):
            prefix=statement[max(0,match.start()-23):match.start()]
            if re.search(r"\b(?:nếu|không|chưa|đừng|giả\s+sử|ví\s+dụ|liệu)\b",prefix):
                continue
            if len(task_terms & tokens(match.group("task")))>=2:
                return True
    return False


def resolve_events(events: list[Event], utterances: list[Utterance]) -> list[ResultRecord]:
    position = {u.id: u.order for u in utterances}
    sources = {u.id: u for u in utterances}
    # Earlier context may be cited together with the actual later correction.
    # The event takes effect at its latest supporting utterance, not its first.
    events = sorted(events, key=lambda e: max(position.get(s, 10**9) for s in e.source_ids))
    grouped: dict[tuple[str, str], list[Event]] = defaultdict(list)
    for event in events:
        grouped[(event.kind, event.issue_key)].append(event)
    records = []
    for (kind, issue_key), history in grouped.items():
        record = ResultRecord(issue_key=issue_key, topic=history[0].topic, kind=kind,
                              content=None, meeting_status="unverified")
        for event in history:
            typ = event.event_type
            if (kind == 'action' and record.meeting_status in {'assigned','paused'}
                    and typ in {'deadline_change','action_paused'}):
                # A real Groq event for LONG01 was mistyped deadline_change:
                # L018 also says "tạm dừng việc chuẩn bị bảng giá".
                grounded_pause = _source_grounded_task_pause(event, record, sources)
                if grounded_pause and typ == 'deadline_change':
                    event = event.model_copy(update={'event_type':'action_paused'})
                    typ = 'action_paused'
                elif not grounded_pause and typ == 'action_paused':
                    # A claimed pause with no matching affirmative source cannot
                    # silently suspend another task. Keep any actual due update.
                    event = event.model_copy(update={'event_type':'deadline_change'})
                    typ = 'deadline_change'
                    record.warnings.append(
                        'LLM nêu tạm dừng nhưng câu nguồn không chứng minh đúng việc; '
                        'chỉ giữ cập nhật hạn và yêu cầu người dùng kiểm tra')
                    record.review_status = 'needs_review'
            if (kind == 'action' and typ in {'action_cancelled','action_paused'}
                    and 'owner' in event.clear_fields
                    and not _explicit_cancel_owner_release(event, sources)):
                # Model clear_fields may misread 'bỏ hạn' as 'bỏ người nhận'.
                event = event.model_copy(update={
                    'clear_fields': [x for x in event.clear_fields if x != 'owner']})
                record.warnings.append(
                    'Câu hủy không ghi rút người phụ trách; giữ owner lịch sử và yêu cầu rà soát')
                record.review_status = 'needs_review'
            if (kind == 'action' and typ in {'action_cancelled','action_paused'}
                    and record.due_raw is not None
                    and 'due_raw' not in event.clear_fields
                    and _explicit_cancel_due_release(event, sources)):
                event = event.model_copy(update={
                    'clear_fields': [*event.clear_fields, 'due_raw']})
                record.warnings.append(
                    'Câu hủy ghi rõ bỏ hạn, LLM thiếu clear_fields; bỏ hạn cũ theo câu nguồn')
                record.review_status = 'needs_review'
            record.history.append(event)
            if typ not in {'deadline_change', 'execution_blocked'}:
                record.field_evidence_ids['meeting_status'] = list(event.source_ids)
            # Lifecycle changes retain historical content; their value describes
            # the change, not a replacement for that historical content.
            if event.value and typ not in {'reopen', 'withdrawal', 'execution_blocked',
                                          'action_cancelled', 'action_paused', 'request_withdrawn', 'deadline_change'}:
                record.field_evidence_ids['content'] = list(event.source_ids)
            for sid in event.source_ids:
                if sid not in record.evidence_ids:
                    record.evidence_ids.append(sid)
            if kind == "decision":
                if typ in {"proposal", "counterproposal"}:
                    if record.meeting_status in {"agreed", "conditional"}:
                        # A new competing proposal AFTER agreement does not automatically
                        # cancel the earlier decision, but the conclusion is now ambiguous.
                        record.meeting_status = "open"
                        record.warnings.append("Có đề xuất mới sau phát biểu chốt; cần xác nhận kết luận cuối")
                        record.review_status = "needs_review"
                    else:
                        record.meeting_status = "proposed"
                    record.execution_status = "unknown"
                    record.condition = None
                    record.field_evidence_ids['condition'] = list(event.source_ids)
                    if event.value: record.content = event.value
                elif typ == "agreement":
                    record.meeting_status = "agreed"
                    record.execution_status = "unknown"
                    record.condition = None
                    if event.value: record.content = event.value
                elif typ == "conditional_agreement":
                    record.meeting_status = "conditional"
                    record.execution_status = "pending_condition"
                    record.condition = event.condition or "Điều kiện chưa được xác định rõ"
                    if event.value: record.content = event.value
                elif typ == "unresolved":
                    record.meeting_status = "open"
                    record.execution_status = "unknown"
                    record.condition = None
                    record.field_evidence_ids['condition'] = list(event.source_ids)
                    if event.value: record.content = event.value
                elif typ in {"reopen", "withdrawal"}:
                    record.meeting_status = "reopened" if typ == "reopen" else "withdrawn"
                    record.execution_status = "unknown"
                    # The old choice/condition remains in history, not as an
                    # active condition after reopening the whole decision.
                    record.condition = None
                    record.field_evidence_ids['condition'] = list(event.source_ids)
                    for sid in event.source_ids:
                        if sid not in record.counter_evidence_ids: record.counter_evidence_ids.append(sid)
                elif typ == "execution_blocked":
                    if record.meeting_status not in {"agreed", "conditional"}:
                        record.warnings.append("Chưa tìm thấy sự kiện chốt trước phát biểu ngừng triển khai")
                    record.execution_status = "blocked"
                    if event.condition is not None or record.condition is None:
                        record.condition = event.condition or "Chưa đủ điều kiện triển khai"
                        record.field_evidence_ids['condition'] = list(event.source_ids)
                record.field_evidence_ids['execution_status'] = list(event.source_ids)
                if typ in {'agreement', 'conditional_agreement'}:
                    record.field_evidence_ids['condition'] = list(event.source_ids)
            elif kind == "action":
                if typ in {"assignment", "reassignment", "deadline_change"}:
                    if typ != 'deadline_change':
                        record.meeting_status = "assigned"
                        # A new explicit acceptance can resume a paused task.
                        record.execution_status = 'unknown'
                        if event.value: record.content = event.value
                    names = ['due_raw'] if typ == 'deadline_change' else ['owner', 'supporter', 'due_raw', 'condition']
                    if typ == 'deadline_change' and any(getattr(event, name) is not None or name in event.clear_fields
                                                        for name in ['owner', 'supporter', 'condition']):
                        record.review_status = 'needs_review'
                        record.warnings.append('Sự kiện đổi hạn chứa cập nhật người/điều kiện; chỉ áp dụng hạn, cần rà soát phần còn lại')
                    for name in names:
                        value = getattr(event, name)
                        if value is not None or name in event.clear_fields:
                            setattr(record, name, value)
                            record.field_evidence_ids[name] = list(event.source_ids)
                    if 'due_raw' in event.clear_fields:
                        record.due_iso = None
                    if 'condition' in event.clear_fields and typ != 'deadline_change':
                        record.execution_status = 'unknown'
                    if typ == 'reassignment' and not event.owner:
                        record.owner = None
                        record.field_evidence_ids['owner'] = list(event.source_ids)
                        record.meeting_status = 'unverified'
                        record.review_status = 'needs_review'
                        record.warnings.append('Đã đổi phân công nhưng chưa xác định người phụ trách mới')
                    if record.owner and record.owner == record.supporter:
                        record.supporter = None
                        record.field_evidence_ids['supporter'] = list(event.source_ids)
                    if event.condition and typ != 'deadline_change':
                        record.execution_status = "pending_condition"
                        record.field_evidence_ids['execution_status'] = list(event.source_ids)
                elif typ == 'action_paused':
                    record.meeting_status = 'paused'
                    record.execution_status = 'blocked'
                    for name in event.clear_fields:
                        setattr(record,name,None)
                        record.field_evidence_ids[name] = list(event.source_ids)
                    if 'due_raw' in event.clear_fields:
                        record.due_iso = None
                    record.field_evidence_ids['execution_status'] = list(event.source_ids)
                    for sid in event.source_ids:
                        if sid not in record.counter_evidence_ids:
                            record.counter_evidence_ids.append(sid)
                    record.review_status = 'needs_review'
                    record.warnings.append(
                        'Câu nguồn tạm dừng công việc: giữ người phụ trách lịch sử, '
                        'không coi việc vẫn đang thực hiện; cần xác minh điều kiện tiếp tục')
                elif typ == "action_cancelled":
                    record.meeting_status = "cancelled"
                    # Cancellation alone preserves historical fields. Apply
                    # only explicit removals stated in the cancellation event,
                    # e.g. "hủy việc và bỏ hạn" in a single utterance.
                    for name in event.clear_fields:
                        setattr(record, name, None)
                        record.field_evidence_ids[name] = list(event.source_ids)
                    if 'due_raw' in event.clear_fields:
                        record.due_iso = None
                    if 'condition' in event.clear_fields:
                        record.execution_status = 'unknown'
                        record.field_evidence_ids['execution_status'] = list(event.source_ids)
                    for sid in event.source_ids:
                        if sid not in record.counter_evidence_ids: record.counter_evidence_ids.append(sid)
            elif kind == "issue":
                if typ == "issue_reported":
                    record.meeting_status = "open"
                elif typ == "issue_reported_resolved":
                    record.meeting_status = "reported_resolved"
                    record.warnings.append("Chỉ được báo là đã xử lý, chưa kiểm chứng độc lập")
                if event.value: record.content = event.value
            elif kind == "request":
                if typ in {"request_made", "request_changed"}:
                    record.meeting_status = "recorded"
                    if event.value: record.content = event.value
                    # A request can have a timing constraint without an owner
                    # or an accepted assignment. Do not discard that constraint.
                    if event.due_raw is not None:
                        record.due_raw = event.due_raw
                        record.field_evidence_ids['due_raw'] = list(event.source_ids)
                elif typ == "request_withdrawn":
                    record.meeting_status = "withdrawn"
                    for sid in event.source_ids:
                        if sid not in record.counter_evidence_ids: record.counter_evidence_ids.append(sid)
            elif kind in {"feedback", "knowledge"}:
                record.meeting_status = "recorded" if kind == "feedback" else "unverified"
                if event.value: record.content = event.value
        if kind == 'request' and record.meeting_status == 'recorded' and record.due_raw is None and record.content:
            # Lift only a literal, already-mentioned relative bound from a
            # positive request. Never invent a date or create a missing task.
            sources = {u.id:u for u in utterances}
            candidates = []
            for sid in record.field_evidence_ids.get('content', []):
                text = sources[sid].text if sid in sources else ''
                if not re.match(r'(?i)^(?:(?:tôi|mình|chúng ta)\s+)?(?:cần|yêu cầu|đề nghị)\b',text):
                    continue
                if '?' in text:
                    continue
                if re.search(r'(?i)\b(?:không\s+(?:cần|phải|yêu cầu)|bỏ\s+hạn|rút\s+yêu cầu)\b',text):
                    continue
                for match in re.finditer(r'(?i)\btrước\s+(?:lần|đợt|buổi)\s+[^.;!?,\n]+',text):
                    bound = match.group(0).strip()
                    if re.search(r'(?i)\b(?:hay|hoặc)\b',bound):
                        continue
                    if bound.casefold() in record.content.casefold():
                        candidates.append((bound,sid))
            if len({bound.casefold() for bound,_ in candidates}) == 1:
                record.due_raw = candidates[0][0]
                record.field_evidence_ids['due_raw'] = list(dict.fromkeys(sid for _,sid in candidates))
                record.review_status = 'needs_review'
                record.warnings.append('Hạn tương đối được giữ nguyên văn từ nội dung và câu nguồn; cần rà soát vì LLM bỏ trống due_raw')
        if record.meeting_status in {"reopened", "withdrawn", "conditional", "proposed", "open", "paused", "unverified"}:
            record.review_status = "needs_review"
        if record.meeting_status == "unverified":
            record.warnings.append("Không thể xác định trạng thái cuối; cần người kiểm tra")
        records.append(record)
    return records

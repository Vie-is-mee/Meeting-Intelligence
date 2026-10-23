"""Conservative second-chance checks for EXPLICIT missing non-committal speech acts.

Only recovers a source-quoted request or an explicitly *open* choice. It never
creates an assignment, agreement, deadline accepted from a proposal, or approval.
This is a limited lexical safety net, not semantic retrieval. Every added item
must be reviewed by a human and is labelled as recovered from source text.
"""
from __future__ import annotations

import re
from .models import Event, Utterance

_CHOICE_RE = re.compile(
    r'(?i)(?:^|[.!?;]\s*)(?:hôm\s+nay\s+)?(?:vẫn\s+)?'
    r'(?P<statement>chưa\s+(?:chốt|chọn|quyết\s+định)\s+'
    r'(?P<subject>(?:cách\s+(?:triển\s+khai|làm)|phương\s+án|'
    r'nhà\s+cung\s+cấp|thư\s+viện|giải\s+pháp|công\s+nghệ)'
    r'[^.!?;,]{0,85}?))(?=\s*(?:\bvà\s+chưa\b|[.!?;,]|$))',
    re.IGNORECASE,
)
_SUFFIX_CHOICE_RE = re.compile(
    r'(?i)(?:^|[,.;]\s*)(?:còn\s+)?(?P<subject>cách\s+(?:làm|triển\s+khai)\s+khác|'
    r'phương\s+án\s+thay\s+thế|giải\s+pháp\s+khác)\s+(?:thì\s+)?'
    r'(?:vẫn\s+)?chưa\s+(?:chốt|chọn)\b'
)
_DEFERRED_CHOICE_RE = re.compile(
    r'(?i)(?:^|[.!?;]\s*)(?P<subject>nhà\s+cung\s+cấp|'
    r'thư\s+viện|phương\s+án\s+thay\s+thế)'
    r'\s+để\s+(?:cuộc\s+họp|buổi\s+họp|lần\s+họp)\s+sau\s+'
    r'(?:mới\s+)?(?:chọn|chốt)\b'
)
_REQUEST_RE = re.compile(
    r'(?i)^(?P<sentence>(?:cần\s+|khách\s+hàng\s+yêu\s+cầu\s+|'
    r'người\s+dùng\s+yêu\s+cầu\s+)[^.!?]{8,200})[.!]?\s*$'
)
_DUE_REL_RE = re.compile(r'(?i)\btrước\s+(?:lần|buổi|đợt)\s+[^,.!?;\n]+')

def _tokens(text: str) -> set[str]:
    return {s for s in re.findall(r'\w+', text.casefold()) if len(s)>2
            and s not in {'chưa','chốt','không','chọn','cần','việc','một','được',
                          'cho','của','với','vào','trong','hôm','nay','trước','sau'}}

def _has_record(events: list[Event], *, kind: str, source: str,
                detail: str = '') -> bool:
    """Source identity or strong content overlap, never shared generic term."""
    words=_tokens(detail)
    for e in events:
        if e.kind != kind:
            continue
        if source in e.source_ids:
            return True
        if words and len(words & _tokens(' '.join([e.value or '',e.topic])))>=2:
            return True
    return False

def recover_explicit_omissions(events: list[Event], utterances: list[Utterance],
                               warnings: list[str]) -> tuple[list[Event], set[str]]:
    """Return original events plus narrowly evidenced review-only recoveries."""
    recovered: set[str] = set()
    result = list(events)
    for u in utterances:
        text=u.text.strip()
        # Historical, hypothetical and quoted instructions must not be
        # promoted into current meeting records merely because they start
        # with an imperative/negative verb.
        historical = bool(re.search(
            r'(?i)\b(?:biên\s+bản\s+cũ|cuộc\s+họp\s+trước|hồi\s+trước|'
            r'trước\s+đây|giả\s+sử|ví\s+dụ|chỉ\s+là\s+mẫu)\b',text
        ))
        if historical:
            continue
        # A suggestion or question is not a business requirement.
        if '?' not in text and not re.search(
            r'(?i)^\s*(?:không\s+cần|chưa\s+cần|đề\s+xuất|giả\s+sử|ví\s+dụ)\b',text
        ):
            m=_REQUEST_RE.fullmatch(text)
            if m:
                sentence=m.group('sentence').strip()
                # "Cần Lan làm..." resembles a named assignment, not an
                # independently stated requirement.
                assigned = re.search(
                    r'^Cần\s+[A-ZÀ-Ỹ][a-zà-ỹ]+\s+(?:làm|viết|thử|kiểm|rà|chuẩn)',
                    sentence
                )
                if not assigned and not _has_record(result,kind='request',source=u.id,detail=sentence):
                    action_here=any(e.kind=='action' and u.id in e.source_ids for e in result)
                    if not action_here:
                        norm=lambda s: ' '.join(re.findall(r'\w+', (s or '').casefold()))
                        # Very narrow recovery: an exact customer-request sentence
                        # mislabeled issue_reported is a request, NOT two records.
                        # Distinct issues about a related problem are left intact.
                        misclassified=[(i,e) for i,e in enumerate(result)
                            if e.kind=='issue' and e.event_type=='issue_reported'
                            and e.source_ids==[u.id] and
                            norm(re.sub(r'(?i)^khách\s+hàng\s+yêu\s+cầu\s+có\s+', 'khách hàng yêu cầu ', e.value or '')) ==
                            norm(re.sub(r'(?i)^khách\s+hàng\s+yêu\s+cầu\s+có\s+', 'khách hàng yêu cầu ', sentence))
                            and re.search(r'(?i)^khách\s+hàng\s+yêu\s+cầu\b',sentence)]
                        if len(misclassified)==1:
                            i,e=misclassified[0]
                            result[i]=e.model_copy(update={'kind':'request','event_type':'request_made'})
                            recovered.add(e.issue_key)
                            warnings.append('Chuẩn hóa issue trùng nguyên văn yêu cầu khách hàng thành request từ nguồn '+
                                u.id+'; giữ một bản ghi và chờ người xác nhận')
                        else:
                            bound=_DUE_REL_RE.search(sentence)
                            key='m3_recovered_request_'+u.id
                            result.append(Event(kind='request',event_type='request_made',
                                issue_key=key,topic=sentence[:100],
                                source_ids=[u.id],value=sentence,
                                due_raw=bound.group(0).strip() if bound else None))
                            recovered.add(key)
                            warnings.append('Bổ sung yêu cầu tường minh còn thiếu từ nguồn '+u.id+
                                '; đây là bản ghi do kiểm tra bổ sung, cần người xác nhận')
        # An explicit unresolved choice is not an approved choice. The chosen
        # implementation/technology must be explicit; no general-purpose
        # "chưa giao" or proposed weekday triggers a fabricated decision.
        for match in _CHOICE_RE.finditer(text):
            # Mixed "not A ... but later approved B" in one utterance needs
            # full event interpretation; a lexical fallback must abstain.
            tail=text[match.end():]
            if re.search(r'(?i)\b(?:đã\s+chốt|đã\s+chọn|thống\s+nhất)\b',tail):
                warnings.append('Nguồn chứa cả chưa chọn và lựa chọn về sau; bỏ qua khôi phục tự động: '+u.id)
                continue
            subject=match.group('subject').strip()
            statement=match.group('statement').strip()
            # A separate explicit no-choice in the same source may already
            # be represented by an open decision. Don't create duplicates.
            if _has_record(result,kind='decision',source=u.id,detail=subject):
                continue
            # If a *settled* decision already exists about this choice,
            # don't silently replace it with a second open decision.
            related=[e for e in result if e.kind=='decision'
                     and len(_tokens(subject)&_tokens(' '.join([e.topic,e.value or ''])))>=2]
            if related and any(e.event_type in {'agreement','conditional_agreement'} for e in related):
                warnings.append('Phát biểu chưa chốt có thể mâu thuẫn với quyết định trước: '+
                                u.id+'; không tự tạo/ghi đè quyết định, cần rà soát')
                continue
            key='m3_recovered_open_'+u.id
            if key in recovered:
                continue
            result.append(Event(kind='decision',event_type='unresolved',
                issue_key=key,topic=subject,source_ids=[u.id],value=statement))
            recovered.add(key)
            warnings.append('Bổ sung lựa chọn chưa chốt tường minh từ nguồn '+u.id+
                '; không phải phương án được duyệt, cần người xác nhận')
        # Also recognize inverted utterances: "còn cách làm khác thì chưa chốt".
        # No agreement can be inferred; only a reviewable OPEN decision.
        for match in _SUFFIX_CHOICE_RE.finditer(text):
            tail=text[match.end():]
            if re.search(r'(?i)\b(?:đã\s+chốt|đã\s+chọn|thống\s+nhất)\b',tail):
                warnings.append('Nguồn có cả chưa chốt và chốt sau đó; không tự phục hồi: '+u.id)
                continue
            subject=match.group('subject').strip()
            if _has_record(result,kind='decision',source=u.id,detail=subject):
                continue
            related=[e for e in result if e.kind=='decision'
                     and len(_tokens(subject)&_tokens(' '.join([e.topic,e.value or ''])))>=2]
            if any(e.event_type in {'agreement','conditional_agreement'} for e in related):
                warnings.append('Có quyết định đã chốt liên quan, không thêm open dựa trên câu ngược: '+u.id)
                continue
            key='m3_recovered_open_'+u.id
            if key in recovered:
                continue
            result.append(Event(kind='decision',event_type='unresolved',
                issue_key=key,topic=subject,source_ids=[u.id],
                value=subject+' chưa chốt'))
            recovered.add(key)
            warnings.append('Khôi phục lựa chọn chưa chốt từ cách nói đảo chiều ở nguồn '+u.id+
                            '; cần người đối chiếu')
        # "Chốt storage. Nhà cung cấp để cuộc họp sau chọn."
        # One utterance can legitimately support TWO independent issues.
        # Do not deduplicate purely by source_id (storage and vendor share L006).
        for match in _DEFERRED_CHOICE_RE.finditer(text):
            tail=text[match.end():]
            if re.search(r'(?i)\b(?:đã\s+chốt|đã\s+chọn|thống\s+nhất)\b',tail):
                warnings.append('Có lựa chọn được chốt muộn trong cùng nguồn; không tự tạo open: '+u.id)
                continue
            subject=match.group('subject').strip()
            topic_terms=_tokens(subject)
            # An agreed STORAGE decision can mention that the VENDOR is deferred
            # in its explanatory value. That reference does NOT make vendor chosen.
            # Match the independent decision target, not incidental words inside
            # another target's evidence/content.
            def target_is_same(e: Event) -> bool:
                if e.kind != 'decision':
                    return False
                topic = _tokens(e.topic)
                if topic_terms and topic_terms.issubset(topic):
                    return True
                if e.event_type == 'unresolved':
                    return bool(topic_terms and topic_terms.issubset(
                        _tokens(' '.join([e.topic,e.value or '']))))
                return False
            same_issue=[e for e in result if target_is_same(e)]
            if any(e.event_type=='unresolved' for e in same_issue):
                continue
            if any(e.event_type in {'agreement','conditional_agreement'} for e in same_issue):
                warnings.append('Cùng đối tượng lựa chọn đã được chốt; cần đối chiếu nguồn: '+u.id)
                continue
            key='m3_recovered_deferred_open_'+u.id
            if key in recovered:
                continue
            result.append(Event(kind='decision',event_type='unresolved',issue_key=key,
                topic=subject,source_ids=[u.id],
                value=subject+' để cuộc họp sau chọn'))
            recovered.add(key)
            warnings.append('Khôi phục lựa chọn '+subject+' còn mở từ nguồn '+u.id+
                            '; độc lập với quyết định cùng câu và cần người xác nhận')
    return result,recovered

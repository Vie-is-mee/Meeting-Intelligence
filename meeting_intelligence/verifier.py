"""Mechanical evidence and risk checks. Does not claim semantic truth verification."""
from __future__ import annotations
import re
from .models import ResultRecord, Utterance

NEGATION = re.compile(r"(?i)\b(chưa\s+chốt|không\s+chốt|hủy\s+quyết\s+định|mở\s+lại|chưa\s+quyết\s+định)\b")

# Only a source-grounded signal. Never claim this lexical test settles semantics.
_TOPIC_STOP = {
    "chưa", "chốt", "không", "quyết", "định", "phương", "án", "lựa", "chọn",
    "đề", "xuất", "của", "cho", "với", "trong", "được", "cần", "đang", "làm",
    "việc", "này", "đó", "hôm", "nay", "lại", "chúng", "tôi", "ban", "đầu",
    "mới", "cũ", "trên", "sau", "trước", "các", "một", "theo", "đã",
}


def late_negation_about_decision(record: ResultRecord, utterance: Utterance) -> bool:
    """Flag a later negation only with an explicit reference to this decision.

    A late 'chưa chốt nhà cung cấp B' is NOT evidence that an earlier choice
    of architecture B was reopened. Weak one-word overlaps are insufficient.
    No match means 'unknown topical relation', NOT a proof that no correction
    exists; the LLM audit and human review still handle unscoped corrections.
    """
    sentence = utterance.text.casefold()
    if not NEGATION.search(sentence):
        return False
    focus = " ".join(x for x in [record.content, record.topic] if x).casefold()
    # Shared generic context is not enough when a named alternative differs.
    # E.g. 'thử nghiệm gói A' vs 'lịch thử nghiệm gói B'.
    for noun in ('gói', 'mẫu', 'thư viện', 'phương án'):
        old = re.search(r'\b' + noun + r'\s+([a-z])\b', focus)
        newer = re.search(r'\b' + noun + r'\s+([a-z])\b', sentence)
        if old and newer and old.group(1) != newer.group(1):
            return False
    words = lambda s: {
        term for term in re.findall(r"\w+", s)
        if len(term) >= 3 and term not in _TOPIC_STOP
    }
    if len(words(focus) & words(sentence)) >= 2:
        return True
    # A literal option name can be sufficient when the negation explicitly
    # refers to that option; a lone 'B' in 'nhà cung cấp B' cannot.
    option = re.search(r"\bphương\s+án\s+([a-z])\b", focus)
    if option and re.search(r"\b(?:phương\s+án|lựa\s+chọn)\s+" +
                            re.escape(option.group(1)) + r"\b", sentence):
        return True
    if re.search(r"\b(?:quyết\s+định|phương\s+án)\s+(?:này|đó|vừa\s+chốt)\b", sentence):
        return True
    return False


def explicitly_denies_owner(record: ResultRecord, lookup: dict[str, Utterance]) -> bool:
    """Narrow guard for explicit role denial; not general semantic verification."""
    if not record.owner or record.kind != 'action' or record.meeting_status not in {'assigned','unverified'}:
        return False
    sources = [lookup[s] for s in record.field_evidence_ids.get('owner', record.evidence_ids) if s in lookup]
    if not sources:
        return False
    latest = max(sources, key=lambda u: u.order)
    subject = r'(?<!\w)' + re.escape(record.owner) + r'(?!\w)'
    if (latest.speaker or '').casefold() == record.owner.casefold():
        subject = '(?:' + subject + r'|\btôi\b|\bmình\b)'
    denial = r'\s+(?:xác\s+nhận\s+)?không(?:\s+còn)?\s+(?:(?:là|làm)\s+)?(?:người\s+)?(?:phụ\s+trách|owner\b|nhận\s+việc)'
    positive = r'\s+(?:(?:sẽ|vẫn|là|làm)\s+)?(?:người\s+)?(?:phụ\s+trách|owner\b|nhận\s+việc)'
    # One utterance may deny ownership of web and assign the SAME person to
    # mobile. Without semantic scope resolution, do not erase that valid owner.
    if re.search(subject + positive, latest.text, re.IGNORECASE):
        return False
    return bool(re.search(subject + denial, latest.text, re.IGNORECASE))


def flag_request_task_overlap(records: list[ResultRecord], lookup: dict[str, Utterance]) -> None:
    """Flag a narrow cross-kind conflict, without deciding which record is true.

    Exact normalized content + the same model key is a review signal only.
    A later request source may reaffirm an independent business requirement.
    Never delete/withdraw a request based on a related task's cancellation.
    """
    def normalized(text: str | None) -> str:
        return ' '.join(re.sub(r'[^\w\s]', ' ', (text or '').casefold()).split())

    cancelled = [r for r in records if r.kind == 'action' and r.meeting_status == 'cancelled']
    for request in records:
        if request.kind != 'request' or request.meeting_status != 'recorded' or not normalized(request.content):
            continue
        request_ids = request.evidence_ids
        if not request_ids or not all(s in lookup for s in request_ids):
            continue
        for action in cancelled:
            if action.issue_key != request.issue_key or normalized(action.content) != normalized(request.content):
                continue
            cancel_ids = action.field_evidence_ids.get('meeting_status', [])
            if not cancel_ids or not all(s in lookup for s in cancel_ids):
                continue
            if max(lookup[s].order for s in request_ids) >= max(lookup[s].order for s in cancel_ids):
                continue
            message = ('Yêu cầu trùng nội dung và mã với công việc đã hủy; cần kiểm tra đây là yêu cầu độc lập còn hiệu lực '
                       'hay bản ghi lặp câu giao việc. Chưa tự rút/xóa yêu cầu. Nguồn yêu cầu: '
                       + ', '.join(request_ids) + '; nguồn hủy: ' + ', '.join(cancel_ids))
            request.review_status = 'needs_review'
            if message not in request.warnings:
                request.warnings.append(message)

def drop_proven_assignment_echoes(records: list[ResultRecord],
                                 lookup: dict[str, Utterance],
                                 diagnostics: list[str] | None = None) -> list[ResultRecord]:
    """Suppress ONLY a demonstrable duplicate request inferred from a named task.

    This is a narrow guard, not semantic deduplication. The request must
    come solely from a first-person, *named direct instruction*; the same
    normalized work must have a cancelled action, an explicitly accepted
    assignment by the named owner, and no independent requirement assertion.
    The suppressed record is explained in the global analysis warnings.
    Ambiguous cases remain in human review.
    """
    def norm(v: str | None) -> str:
        return ' '.join(re.sub(r'[^\w\s]', ' ', (v or '').casefold()).split())

    suppressed: set[int] = set()
    for idx, request in enumerate(records):
        if request.kind != 'request' or request.meeting_status != 'recorded':
            continue
        if len(request.history) != 1 or request.history[0].event_type != 'request_made':
            continue
        request_sources = request.field_evidence_ids.get('content', request.history[0].source_ids)
        if len(request_sources) != 1 or request_sources[0] not in lookup:
            continue
        origin = lookup[request_sources[0]]
        words = origin.text.casefold()
        if re.search(r'\b(?:khách\s+hàng|người\s+dùng|yêu\s+cầu|nhu\s+cầu|đề\s+nghị)\b', words):
            continue
        for action in records:
            if action.kind != 'action' or action.issue_key != request.issue_key or (
                    action.meeting_status != 'cancelled' or norm(action.content) != norm(request.content)
                    or not action.owner):
                continue
            name = re.escape(action.owner.casefold())
            if not re.match(r'(?i)^(?:giao\s+)?' + name + r'\b\s+', words):
                continue
            confirmations = [e for e in action.history if e.event_type == 'assignment' and
                             e.owner and e.owner.casefold() == action.owner.casefold() and
                             all(s in lookup and lookup[s].order > origin.order for s in e.source_ids) and
                             any((lookup[s].speaker or '').casefold() == action.owner.casefold() and
                                 re.search(r'(?i)\b(?:tôi|mình)\s+nhận\b', lookup[s].text)
                                 for s in e.source_ids)]
            if not confirmations:
                continue
            # An independent requirement anywhere in the conversation makes
            # this a disputed case; do not auto-delete it.
            if any(re.search(r'(?i)\b(?:yêu\s+cầu|nhu\s+cầu)\b', u.text) and
                   u.id != origin.id and norm(request.content) and
                   len(set(norm(request.content).split()) & set(norm(u.text).split())) >= 2
                   for u in lookup.values()):
                continue
            suppressed.add(idx)
            if diagnostics is not None:
                diagnostics.append('Loại request trùng câu giao việc đã hủy (giữ action lịch sử); '
                                   'chỉ áp dụng mẫu đã xác nhận bởi người nhận. Nguồn: '
                                   + ', '.join(request_sources))
            break
    return [r for i,r in enumerate(records) if i not in suppressed]


def drop_spurious_task_proposals(records: list[ResultRecord],
                                  lookup: dict[str, Utterance],
                                  diagnostics: list[str] | None = None) -> list[ResultRecord]:
    """Remove a duplicate *proposal* that merely restates an accepted task.

    Requires the exact same issue key + work content, a cited named imperative,
    and a separately evidenced task later accepted by its named owner.
    Real independent design proposals, even about the same technology, remain.
    """
    norm=lambda s:' '.join(re.sub(r'[^\w\s]',' ',(s or '').casefold()).split())
    removed=set()
    for idx, proposal in enumerate(records):
        if proposal.kind!='decision' or proposal.meeting_status!='proposed' or len(proposal.history)!=1:
            continue
        e=proposal.history[0]
        if e.event_type!='proposal' or len(e.source_ids)!=1 or e.source_ids[0] not in lookup:
            continue
        utterance=lookup[e.source_ids[0]]
        for task in records:
            if task.kind!='action' or task.issue_key!=proposal.issue_key or (
                task.meeting_status not in {'assigned','cancelled'} or
                not task.owner or norm(task.content)!=norm(proposal.content)):
                continue
            if not re.match(r'(?i)^'+re.escape(task.owner)+r'\s+(?:thử|làm|viết|kiểm|rà|chuẩn)\b',
                            utterance.text):
                continue
            confirmed=any(h.event_type in {'assignment','reassignment'} and
                h.owner==task.owner and
                any(s in lookup and lookup[s].order>utterance.order and
                    (lookup[s].speaker or '').casefold()==task.owner.casefold() and
                    re.search(r'(?i)\b(?:tôi|mình)\s+nhận\b',lookup[s].text)
                    for s in h.source_ids) for h in task.history)
            if not confirmed:
                continue
            removed.add(idx)
            if diagnostics is not None:
                diagnostics.append('Loại proposal trùng với câu giao task đã được nhận; '
                                   'giữ nhiệm vụ và bằng chứng lịch sử: '+utterance.id)
            break
    return [record for i,record in enumerate(records) if i not in removed]


def _proposal_only_evidence(record: ResultRecord, field: str,
                            lookup: dict[str, Utterance]) -> bool:
    """A field mentioned only as a QUESTION or tentative option isn't agreed.

    This high-precision negative guard is deliberately narrower than semantic
    NLI. Distinct acceptance utterances, when cited for the field, override a
    mere question; absent clear signals leave the original value for review.
    """
    ids=record.field_evidence_ids.get(field, [])
    sources=[lookup[s].text.strip() for s in ids if s in lookup]
    if not sources:
        return False
    tentative=r'(?i)^(?:hay\b|đề\s+xuất\b|mình\s+nghĩ\b|tôi\s+nghĩ\b|có\s+thể\b|chưa\s+(?:chốt|chọn|quyết\s+định)\b)'
    accept=r'(?i)\b(?:thống\s+nhất|chốt|đã\s+chọn|đồng\s+ý|xác\s+nhận|quyết\s+định|tôi\s+nhận|hạn\s+chính\s+thức)\b'
    def purely_tentative(s: str) -> bool:
        # "chưa chốt" is NOT an affirmative "chốt", even though the keyword
        # occurs in both. Mask the negative phrase before checking acceptance.
        positive_text=re.sub(r'(?i)\b(?:chưa|không)\s+(?:chốt|chọn|quyết\s+định)\b','',s)
        return bool(re.search(tentative,s) or '?' in s) and not re.search(accept,positive_text)
    return all(purely_tentative(s) for s in sources)


def _owner_explicitly_not_assigned(record: ResultRecord,
                                   lookup: dict[str, Utterance]) -> bool:
    if not record.owner or record.kind != 'action':
        return False
    name=re.escape(record.owner.casefold())
    return any(re.search(r'(?i)\b(?:chưa|không)\s+(?:giao|phân\s+công|xác\s+nhận\s+(?:giao|người\s+phụ\s+trách))\b.{0,35}\b'+name+r'\b',lookup[s].text)
               for s in record.field_evidence_ids.get('owner',[]) if s in lookup)


def verify_records(records: list[ResultRecord], utterances: list[Utterance],
                   *, warnings: list[str] | None = None) -> list[ResultRecord]:
    lookup = {u.id: u for u in utterances}
    for record in records:
        valid = set(lookup)
        missing = [s for s in record.evidence_ids if s not in valid]
        if missing:
            record.review_status = "needs_review"
            record.warnings.append("Không có câu nguồn: " + ", ".join(missing))
        if not record.evidence_ids:
            record.review_status = "needs_review"
            record.warnings.append("Bản ghi không có câu nguồn")
        if (missing or not record.evidence_ids) and record.kind in {'decision', 'action'}:
            record.meeting_status = 'unverified'
        def field_reference(name: str) -> str:
            ids = record.field_evidence_ids.get(name, record.evidence_ids)
            # Speaker metadata supports first-person assignments, e.g. 'Lan: Tôi làm'.
            return ' '.join((lookup[s].speaker or '') + ': ' + lookup[s].text
                            for s in ids if s in lookup).casefold()
        invalid_fields = {
            name: [sid for sid in ids if sid not in lookup]
            for name, ids in record.field_evidence_ids.items()
            if any(sid not in lookup for sid in ids)
        }
        if invalid_fields:
            record.review_status = 'needs_review'
            record.warnings.append('Nguồn chứng minh theo trường không tồn tại: '+
                                   ', '.join(invalid_fields))
            if (record.kind in {'decision','action'} and
                    any(name in invalid_fields for name in ('meeting_status','owner','due_raw','condition'))):
                record.meeting_status = 'unverified'
        if _owner_explicitly_not_assigned(record, lookup):
            record.owner = None
            record.review_status = 'needs_review'
            record.meeting_status = 'unverified'
            record.warnings.append('Nguồn người phụ trách ghi rõ chưa phân công; bỏ owner không đủ căn cứ')
        if explicitly_denies_owner(record, lookup):
            record.owner = None
            record.meeting_status = 'unverified'
            record.review_status = 'needs_review'
            record.warnings.append('Nguồn cuối của người phụ trách phủ định vai trò đó; bỏ owner và giữ để rà soát')
        for attr, label in [("owner", "người phụ trách"), ("supporter", "người hỗ trợ"),
                            ("due_raw", "thời hạn")]:
            value = getattr(record, attr)
            if value and not re.search(r'(?<!\w)' + re.escape(value.casefold()) + r'(?!\w)',
                                       field_reference(attr)):
                record.warnings.append(f"Không xác nhận trực tiếp được {label} từ các câu nguồn; đã bỏ trường chưa có căn cứ")
                setattr(record, attr, None)
                record.review_status = "needs_review"
                if record.kind in {'decision', 'action'}:
                    record.meeting_status = 'unverified'
        # A date that appears only in a *proposal* is not an agreed due date.
        # Keep assigned work when the task itself was accepted; clear only the
        # unsupported timing claim, with an explicit human-review warning.
        if record.due_raw and _proposal_only_evidence(record, 'due_raw', lookup):
            record.due_raw = None
            record.due_iso = None
            record.review_status = 'needs_review'
            record.warnings.append('Thời hạn chỉ được nêu dưới dạng đề xuất/câu hỏi; không coi là hạn đã nhận')
        # A decision that was ONLY suggested has no confirmed agreement.
        if (record.kind == 'decision' and record.meeting_status in {'agreed','conditional'}
                and _proposal_only_evidence(record, 'meeting_status', lookup)):
            record.meeting_status = 'unverified'
            record.review_status = 'needs_review'
            record.warnings.append('Nguồn quyết định là câu hỏi/đề xuất, không chứng minh đã thống nhất')
        # Numeric thresholds are material evidence. A hallucinated number in
        # an operative condition cannot be supported by a citation that never
        # mentions it. This guard does NOT pretend to verify paraphrases.
        if record.condition:
            claimed_numbers=set(re.findall(r'(?<!\w)\d+(?:[.,]\d+)?(?!\w)',record.condition))
            cited_numbers=set(re.findall(r'(?<!\w)\d+(?:[.,]\d+)?(?!\w)',
                                         field_reference('condition')))
            if claimed_numbers and not claimed_numbers.issubset(cited_numbers):
                record.review_status='needs_review'
                record.warnings.append('Điều kiện chứa ngưỡng số không xuất hiện trong nguồn của trường: '+
                                       ', '.join(sorted(claimed_numbers-cited_numbers)))
                if record.kind=='decision' and record.meeting_status in {'agreed','conditional'}:
                    record.meeting_status='unverified'
        # If an important late correction was not converted to an event, flag it.
        if record.kind == "decision" and record.meeting_status in {"agreed", "conditional"}:
            evidence_order = [lookup[x].order for x in record.evidence_ids if x in lookup]
            last_event_at = max(evidence_order, default=0)
            late_negations = [u.id for u in utterances
                              if u.order > last_event_at and late_negation_about_decision(record, u)]
            if late_negations:
                record.review_status = "needs_review"
                record.warnings.append("Có câu phủ định sau bằng chứng cuối có thể liên quan: " + ", ".join(late_negations))
        # Deterministic guard for explicitly named A/B/C option decisions.
        # More complex paraphrases still require the semantic audit or human review.
        if record.kind == "decision" and record.content and record.meeting_status in {"agreed", "conditional"}:
            match = re.fullmatch(r"(?i)(?:phương án\s+)?([A-Z])", record.content.strip())
            if match:
                letter = match.group(1)
                if not re.search(r"(?i)\b" + re.escape(letter) + r"\b", field_reference('content')):
                    record.warnings.append("Phương án được chốt không xuất hiện trong bằng chứng; giữ để người dùng kiểm tra")
                    record.meeting_status = "unverified"
                    record.review_status = "needs_review"
        # A source-backed record is still not necessarily approved by the company.
        record.authority_status = "unknown"
    flag_request_task_overlap(records, lookup)
    records = drop_proven_assignment_echoes(records, lookup, diagnostics=warnings)
    return drop_spurious_task_proposals(records, lookup, diagnostics=warnings)

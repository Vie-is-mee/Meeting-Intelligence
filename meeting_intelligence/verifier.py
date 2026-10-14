"""Mechanical evidence and risk checks. Does not claim semantic truth verification."""
from __future__ import annotations
import re
from .models import ResultRecord, Utterance

NEGATION = re.compile(r"(?i)\b(chưa\s+chốt|không\s+chốt|hủy\s+quyết\s+định|mở\s+lại|chưa\s+quyết\s+định)\b")


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

def verify_records(records: list[ResultRecord], utterances: list[Utterance]) -> list[ResultRecord]:
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
        # If an important late correction was not converted to an event, flag it.
        if record.kind == "decision" and record.meeting_status in {"agreed", "conditional"}:
            evidence_order = [lookup[x].order for x in record.evidence_ids if x in lookup]
            last_event_at = max(evidence_order, default=0)
            late_negations = [u.id for u in utterances if u.order > last_event_at and NEGATION.search(u.text)]
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
    return records

"""Conservative false-request guard for explicitly rejected tentative scheduling.

A proposal phrased as a question is not a recorded request when a later turn
expressly confirms that its deadline was not fixed. Preserve original event in
raw evaluation and emit a diagnostic rather than silently treating it as a
confirmed business requirement.
"""
from __future__ import annotations
import re
from .models import ResultRecord, Utterance

_TENTATIVE = re.compile(r"(?i)^\s*(?:hay|liệu|có\s+nên|mình\s+có\s+thể)\b")
_QUESTION = re.compile(r"(?i)(?:\?|được\s+không[?.!]?\s*$|nhé\s*\?\s*$)")
_REJECT_DEADLINE = re.compile(r"(?i)\b(?:chưa|không)\s+(?:chốt|xác\s+nhận|thống\s+nhất)\s+(?:hạn|deadline|ngày|thời\s+hạn|lịch)\b")
_DEADLINE_CONTEXT = re.compile(r"(?i)\b(?:thứ\s+[2-7]|thứ\s+(?:hai|ba|tư|năm|sáu|bảy)|chủ\s+nhật|ngày|deadline|hạn)\b")

def suppress_rejected_deadline_requests(
    records: list[ResultRecord], utterances: list[Utterance],
    *, warnings: list[str] | None = None
) -> list[ResultRecord]:
    lookup={x.id:x for x in utterances}
    suppressed=set()
    for idx,record in enumerate(records):
        if record.kind!="request" or record.meeting_status!="recorded":
            continue
        if len(record.history)!=1 or record.history[0].event_type!="request_made":
            continue
        ids=record.history[0].source_ids
        if len(ids)!=1 or ids[0] not in lookup:
            continue
        source=lookup[ids[0]]
        if not (_TENTATIVE.search(source.text) and _QUESTION.search(source.text) and
                _DEADLINE_CONTEXT.search(source.text)):
            continue
        # A later explicit denial, not mere silence, must exist.
        later=[u for u in utterances if u.order>source.order
               and u.order-source.order<=3 and _REJECT_DEADLINE.search(u.text)]
        if len(later)!=1:
            continue
        # If this request has a separate cited proof of confirmation, abstain.
        if set(record.evidence_ids)-set(ids):
            continue
        suppressed.add(idx)
        if warnings is not None:
            warnings.append(
                "Stage 2: không coi lời gợi ý hạn ở "+source.id+
                " là yêu cầu đã chốt, vì câu "+later[0].id+
                " xác nhận hạn chưa chốt. Giữ transcript và raw LLM output."
            )
    return [r for idx,r in enumerate(records) if idx not in suppressed]

"""Conservative false-request guard for explicitly rejected tentative scheduling.

A proposal phrased as a question is not a recorded request when a later turn
expressly confirms that its deadline was not fixed. Preserve original event in
raw evaluation and emit a diagnostic rather than silently treating it as a
confirmed business requirement.
"""
from __future__ import annotations
import re
from .models import ResultRecord, Utterance

_TENTATIVE = re.compile(r"(?i)^\s*(?:hay|liệu|có\s+nên|mình\s+có\s+nên|mình\s+có\s+thể)\b")
_QUESTION = re.compile(r"(?i)(?:\?|được\s+không[?.!]?\s*$|nhé\s*\?\s*$)")
_REJECT_DEADLINE = re.compile(r"(?i)\b(?:chưa|không)\s+(?:chốt|xác\s+nhận|thống\s+nhất)\s+(?:hạn|deadline|ngày|thời\s+hạn|lịch)\b")
_DEADLINE_CONTEXT = re.compile(r"(?i)\b(?:thứ\s+[2-7]|thứ\s+(?:hai|ba|tư|năm|sáu|bảy)|chủ\s+nhật|ngày|deadline|hạn)\b")
_COLLECTIVE_PROPOSAL = re.compile(
    r"(?i)^\s*để\s+(?:team|nhóm|bên)\s+mình\s+(?:xem|kiểm\s+tra|xử\s+lý)\b"
)
_EXPLICIT_NO_PERSON = re.compile(
    r"(?i)\b(?:chưa|không)\s+(?:giao|phân\s+công|chốt\s+người)\b"
)
_GENERIC = {"team","nhóm","bên","mình","chúng","ta","để","xem","phần","người","cá","nhân","nào","chưa","giao","phân","công","đúng","phụ","trách","cho","nhé","nhà","các","việc"}
def _key_terms(text: str) -> set[str]:
    return {s for s in re.findall(r"\w+", text.casefold()) if len(s)>1 and s not in _GENERIC}


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
        date_proposal=bool(_TENTATIVE.search(source.text) and
                           _QUESTION.search(source.text) and
                           _DEADLINE_CONTEXT.search(source.text))
        collective_proposal=bool(_COLLECTIVE_PROPOSAL.search(source.text))
        if not (date_proposal or collective_proposal):
            continue
        # A later explicit denial, not mere silence, must exist.
        later=[u for u in utterances if u.order>source.order
               and u.order-source.order<=3
               and ((_REJECT_DEADLINE.search(u.text) if date_proposal else
                     _EXPLICIT_NO_PERSON.search(u.text)))]
        if len(later)!=1:
            continue
        # Collective intent and a later denial must concern the same work.
        # An unrelated team's assignment denial is not proof against this request.
        if collective_proposal and len(_key_terms(source.text) & _key_terms(later[0].text))<2:
            continue
        # If this request has a separate cited proof of confirmation, abstain.
        if set(record.evidence_ids)-set(ids):
            continue
        suppressed.add(idx)
        if warnings is not None:
            warnings.append(
                "Stage 2: không coi câu đề xuất ở "+source.id+
                " là yêu cầu đã chốt, vì câu "+later[0].id+
                " xác nhận chưa có cam kết tương ứng. Giữ transcript và raw LLM output."
            )
    return [r for idx,r in enumerate(records) if idx not in suppressed]

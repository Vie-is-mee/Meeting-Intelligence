"""Conservative topic-scoped consolidation of redundant meeting conclusions.

A record about *not having assigned anybody* is not itself a second business
decision when its only evidence is a literal denial and the same task already
has a source-grounded open scheduling decision plus a request without an owner.

This module never changes a settled decision, never fabricates an assignee,
and keeps the negative ownership evidence in the surviving request.
"""
from __future__ import annotations

import re
from .models import ResultRecord, Utterance

_NO_PERSONAL_ASSIGNMENT = re.compile(
    r"(?i)^\s*(?:chưa|không)\s+(?:giao(?:\s+việc)?|phân\s+công)"
    r"\b[^.;!?]*$"
)
_EXPLICIT_NO_OWNER = re.compile(
    r"(?i)\b(?:chưa|không)\s+(?:giao(?:\s+việc)?|phân\s+công)\b"
)
_UNSETTLED_SCHEDULE = re.compile(
    r"(?i)\b(?:chưa|không)\s+(?:chốt|chọn|quyết\s+định)"
    r"\s+(?:thứ|ngày|hạn|mốc|lịch|buổi|thời\s+gian)\b"
)
_SCHEDULE_TOPIC = re.compile(r"(?i)\b(?:hạn|ngày|lịch|mốc|thời\s+gian|thứ)\b")
_STOP = {
    "chưa", "không", "giao", "việc", "phân", "công", "người",
    "thực", "hiện", "phụ", "trách", "ai", "cho", "được",
    "hạn", "hoàn", "thành", "ngày", "lịch", "thời", "gian",
    "một", "của", "các", "là", "trước", "sau", "sẽ", "cần",
}

def _topic_terms(text: str) -> set[str]:
    return {s for s in re.findall(r"\w+", (text or "").casefold())
            if len(s)>1 and s not in _STOP}

def _same_task(left: ResultRecord, right: ResultRecord) -> bool:
    return len(_topic_terms(left.topic) & _topic_terms(right.topic)) >= 2

def collapse_unassigned_decision_echoes(
    records: list[ResultRecord], utterances: list[Utterance],
    *, warnings: list[str] | None = None
) -> list[ResultRecord]:
    """Remove a strictly redundant OPEN 'no one assigned' decision.

    Preconditions: one single unresolved event states ONLY no assignment;
    its cited original source explicitly denies assignment AND selecting a date;
    one same-task unassigned request and one same-task open schedule decision
    already cover the facts. Ambiguous or independent choices are preserved.
    """
    lookup={u.id:u for u in utterances}
    removed=set()
    for idx, echo in enumerate(records):
        if (echo.kind!="decision" or echo.meeting_status!="open"
            or len(echo.history)!=1 or echo.history[0].event_type!="unresolved"
            or echo.owner is not None or echo.due_raw is not None
            or echo.condition is not None):
            continue
        evt=echo.history[0]
        value=(evt.value or "").strip()
        if not _NO_PERSONAL_ASSIGNMENT.fullmatch(value):
            continue
        # Explicit person-choice ("Lan hay Huy") and other substantive choices
        # must not vanish even if the event was incorrectly typed as no-owner.
        if re.search(r"(?i)\b(?:hay|hoặc|giữa|chọn|chốt)\b",value):
            continue
        if not evt.source_ids or any(s not in lookup for s in evt.source_ids):
            continue
        if not all(_EXPLICIT_NO_OWNER.search(lookup[s].text)
                   and _UNSETTLED_SCHEDULE.search(lookup[s].text)
                   for s in evt.source_ids):
            continue
        # If this same task has an actual assignment/cancellation history,
        # 'nobody assigned' could contradict a live commitment. Do not hide it.
        if any(r.kind=="action" and r.meeting_status in {"assigned","cancelled"}
               and _same_task(echo,r) for r in records):
            continue
        requests=[r for r in records if r.kind=="request"
                  and r.meeting_status=="recorded" and r.owner is None
                  and _same_task(echo,r)]
        schedules=[r for r in records if r is not echo
                   and r.kind=="decision" and r.meeting_status=="open"
                   and _SCHEDULE_TOPIC.search(r.topic)
                   and _same_task(echo,r)
                   and bool(set(evt.source_ids) & set(r.evidence_ids))]
        if len(requests)!=1 or len(schedules)!=1:
            continue
        request=requests[0]
        # Keep the refutation of a personal assignment in its source record.
        for sid in evt.source_ids:
            if sid not in request.counter_evidence_ids:
                request.counter_evidence_ids.append(sid)
            cited=request.field_evidence_ids.setdefault("owner",[])
            if sid not in cited:
                cited.append(sid)
        request.review_status="needs_review"
        notice=("M3 topic resolution: bỏ decision/open trùng về việc chưa giao "
                "người, giữ trạng thái request không owner, lựa chọn hạn chưa "
                "chốt và evidence phủ định: "+", ".join(evt.source_ids))
        request.warnings.append(notice)
        if warnings is not None:
            warnings.append(notice)
        removed.add(idx)
    return [record for idx,record in enumerate(records) if idx not in removed]

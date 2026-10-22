"""C2: reject invented personal assignments from bare collective commitments.

A source saying "cái này team mình xử lý nhé" is NOT the acceptance by
the speaking person. The scope is intentionally narrow and falsifiable:
never manufacture a task, an owner, a due date, or a team identity.
"""
from __future__ import annotations
import re
from .models import ResultRecord, Utterance

_COLLECTIVE_ONLY = re.compile(
    r"(?i)^\s*(?:(?:cái|việc|phần|vụ|lỗi|chuyện)\s+(?:này|đó)|"
    r"phần\s+việc\s+này)\s+"
    r"(?:team\s+mình|nhóm\s+mình|team|cả\s+nhóm|chúng\s+ta)"
    r"\s+(?:sẽ\s+)?(?:xử\s+lý|lo|làm)"
    r"(?:\s+(?:nhé|nha|đi|ạ))?\s*[.!]?\s*$"
)

def is_bare_collective(utterance: Utterance) -> bool:
    return bool(_COLLECTIVE_ONLY.fullmatch(utterance.text.strip()))

def guard_ambiguous_collective_actions(
    records: list[ResultRecord], utterances: list[Utterance],
    *, warnings: list[str] | None = None,
) -> None:
    """Demote ONLY an action whose latest assignment cites a bare group pledge.

    A later genuinely named assignment/reassignment remains authoritative.
    An explicit later deadline may remain even if the personal owner is unknown.
    Historical cancelled tasks are not modified.
    """
    lookup = {u.id: u for u in utterances}
    referenced_collective: set[str] = set()
    for record in records:
        if record.kind != "action" or record.meeting_status == "cancelled":
            continue
        assignments = [
            event for event in record.history
            if event.event_type in {"assignment", "reassignment"}
        ]
        if not assignments:
            continue
        latest = assignments[-1]
        sources = [lookup[s] for s in latest.source_ids if s in lookup]
        if len(sources) != len(latest.source_ids) or not sources:
            continue
        if not all(is_bare_collective(u) for u in sources):
            continue
        referenced_collective.update(latest.source_ids)
        # The speaker's name in metadata is NOT evidence of accepting this task.
        record.owner = None
        record.field_evidence_ids["owner"] = list(latest.source_ids)
        # Only wipe a date that the group-only assignment itself introduced.
        # Do not erase a separately confirmed later deadline.
        due_sources = record.field_evidence_ids.get("due_raw", [])
        if due_sources and set(due_sources).issubset(set(latest.source_ids)):
            record.due_raw = None
            record.due_iso = None
        record.meeting_status = "unverified"
        record.review_status = "needs_review"
        message = ("C2: chỉ có cam kết tập thể, chưa xác định người phụ trách cá nhân; "
                   "không xem là action đã phân công. Cần làm rõ: " + ", ".join(latest.source_ids))
        if message not in record.warnings:
            record.warnings.append(message)
        if warnings is not None:
            warnings.append(message)

    # A bare collective commitment is not a proposal/choice. Avoid a false
    # decision if the extractor attached proposal/agreement to this exact line.
    for record in list(records):
        if (record.kind == "decision"
                and record.meeting_status in {"proposed", "agreed"}
                and len(record.history) == 1
                and record.history[0].event_type in {"proposal", "agreement"}
                and record.evidence_ids
                and all(sid in lookup and is_bare_collective(lookup[sid])
                        for sid in record.evidence_ids)):
            records.remove(record)
            if warnings is not None:
                warnings.append("C2: loại decision giả từ câu team xử lý; giữ action mơ hồ để rà soát: "
                                + ", ".join(record.evidence_ids))

    # The extractor can omit the collective intent entirely. Recover ONLY the
    # utterance literally spoken, never a guessed referent / owner / deadline.
    # An unresolved action is a reviewer placeholder, not a confirmed assignment.
    for u in utterances:
        if not is_bare_collective(u) or u.id in referenced_collective:
            continue
        if any(r.kind == "action" and u.id in r.evidence_ids for r in records):
            continue
        placeholder = ResultRecord(
            issue_key="m3_c2_collective_" + u.id.casefold(),
            topic="Cam kết tập thể chưa phân công",
            kind="action",
            content=u.text.strip(),
            meeting_status="unverified",
            execution_status="unknown",
            authority_status="unknown",
            owner=None, due_raw=None, due_iso=None,
            evidence_ids=[u.id],
            field_evidence_ids={"content":[u.id], "meeting_status":[u.id]},
            review_status="needs_review",
            warnings=[
                "C2: phát biểu có ý định xử lý nhưng chưa xác định việc cụ thể / "
                "người phụ trách / hạn; cần người dùng làm rõ trước khi giao."
            ],
            history=[],
        )
        records.append(placeholder)
        if warnings is not None:
            warnings.append(
                "C2: giữ ý định tập thể " + u.id +
                " ở trạng thái cần làm rõ; không tự tạo owner/deadline")

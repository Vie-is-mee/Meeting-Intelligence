"""Typed contract between LLM extraction, temporal reasoning and verified output."""
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

Kind = Literal["decision", "action", "issue", "request", "feedback", "knowledge"]
EventType = Literal[
    "proposal", "counterproposal", "agreement", "conditional_agreement",
    "reopen", "unresolved", "withdrawal", "execution_blocked",
    "assignment", "reassignment", "deadline_change", "action_paused", "action_cancelled",
    "issue_reported", "issue_reported_resolved", "request_made", "request_changed",
    "request_withdrawn", "feedback_given", "knowledge_shared"
]
MeetingStatus = Literal[
    "proposed", "agreed", "conditional", "reopened", "withdrawn",
    "assigned", "paused", "cancelled", "open", "reported_resolved", "recorded", "unverified"
]
ExecutionStatus = Literal["unknown", "pending_condition", "blocked", "not_applicable"]
ReviewStatus = Literal["unreviewed", "needs_review", "reviewed"]
InformationUtility = Literal["current_work", "reusable_candidate", "historical_context", "needs_verification"]

class Utterance(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    order: int = Field(ge=1)
    text: str = Field(min_length=1)
    speaker: str | None = None
    timestamp: str | None = None

class Event(BaseModel):
    model_config = ConfigDict(extra="forbid")
    issue_key: str = Field(min_length=1, description="Stable normalized key shared by related events")
    topic: str = Field(min_length=1)
    kind: Kind
    event_type: EventType
    source_ids: list[str] = Field(min_length=1)
    value: str | None = None
    owner: str | None = None
    supporter: str | None = None
    due_raw: str | None = None
    condition: str | None = None
    clear_fields: list[Literal['owner', 'supporter', 'due_raw', 'condition']] = Field(
        default_factory=list,
        description='Fields explicitly withdrawn by this event; null alone means no update',
    )

    @model_validator(mode="after")
    def event_type_matches_kind(self):
        allowed = {
            'decision': {'proposal','counterproposal','agreement','conditional_agreement',
                         'reopen','unresolved','withdrawal','execution_blocked'},
            'action': {'assignment','reassignment','deadline_change','action_paused','action_cancelled'},
            'issue': {'issue_reported','issue_reported_resolved'},
            'request': {'request_made','request_changed','request_withdrawn'},
            'feedback': {'feedback_given'},
            'knowledge': {'knowledge_shared'},
        }
        if self.event_type not in allowed[self.kind]:
            raise ValueError(f'event_type {self.event_type} không hợp lệ với kind {self.kind}')
        if self.clear_fields and self.kind != 'action':
            raise ValueError('clear_fields chỉ áp dụng cho công việc')
        if any(getattr(self, name) is not None for name in self.clear_fields):
            raise ValueError('Không thể vừa cập nhật vừa xóa cùng một trường')
        return self

class EventBatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    events: list[Event]

class ResultRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")
    issue_key: str
    topic: str
    kind: Kind
    content: str | None
    meeting_status: MeetingStatus
    execution_status: ExecutionStatus = "not_applicable"
    authority_status: Literal["unknown", "verified"] = "unknown"
    information_utility: InformationUtility | None = None
    information_utility_note: str | None = None
    owner: str | None = None
    supporter: str | None = None
    due_raw: str | None = None
    due_iso: str | None = None
    condition: str | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    counter_evidence_ids: list[str] = Field(default_factory=list)
    field_evidence_ids: dict[str, list[str]] = Field(default_factory=dict)
    review_status: ReviewStatus = "unreviewed"
    warnings: list[str] = Field(default_factory=list)
    history: list[Event] = Field(default_factory=list)

class AnalysisResult(BaseModel):
    model_config = ConfigDict(extra="forbid")
    engine: Literal["llm_api", "offline_rules", "mock_for_tests"]
    utterances: list[Utterance]
    records: list[ResultRecord]
    warnings: list[str] = Field(default_factory=list)
    audit_findings: list[dict] = Field(default_factory=list)

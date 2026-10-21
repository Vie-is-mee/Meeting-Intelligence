"""End-to-end pipeline: parse -> extract -> temporal resolve -> ground -> audit.

The API mode does NOT claim human-verified accuracy. The strict audit's own
failures are fail-closed, and the offline engine remains a narrow baseline.
"""
from __future__ import annotations
from typing import Literal
from .parser import parse_transcript
from .extractor import extract_events
from .completeness import recover_explicit_omissions
from .resolver import resolve_events
from .verifier import verify_records
from .information_utility import classify_information_utility
from .models import AnalysisResult
from .offline_rules import offline_extract_decisions
from .llm_client import LLMClient, LLMError
from .auditor import audit_events, apply_audit_findings, hold_for_review


def analyze(text: str, engine: Literal['llm_api', 'offline_rules'] = 'llm_api',
            client: LLMClient | None = None, *, audit: bool = True,
            fail_closed: bool = True) -> AnalysisResult:
    utterances = parse_transcript(text)
    warnings: list[str] = []
    audit_findings = []
    if engine == 'llm_api':
        active_client = client or LLMClient()
        events = extract_events(utterances, active_client, warnings=warnings)
        events, recovered_keys = recover_explicit_omissions(events, utterances, warnings)
    elif engine == 'offline_rules':
        active_client = None
        events = offline_extract_decisions(utterances)
        recovered_keys = set()
        warnings.append('OFFLINE BASELINE: luật hẹp cho quyết định tiếng Việt, KHÔNG phải kiểm thử năng lực LLM.')
    else:
        raise ValueError('engine không hợp lệ')
    records = verify_records(resolve_events(events, utterances), utterances, warnings=warnings)
    for record in records:
        if record.issue_key in recovered_keys:
            record.review_status = 'needs_review'
            record.warnings.append('M3 Stage 2: khôi phục từ phát biểu tường minh; cần người đối chiếu trước khi dùng')
    if engine == 'llm_api' and audit:
        try:
            audit_findings, ignored = audit_events(utterances, events, records, active_client)
            warnings.extend(ignored)
            warnings.extend(apply_audit_findings(records, audit_findings))
        except LLMError as exc:
            if not fail_closed:
                warnings.append('Audit lỗi, kết quả CHƯA ĐƯỢC KIỂM CHỨNG: ' + str(exc))
            else:
                warnings.append('Audit lỗi, các bản ghi có tác động cao bị giữ để kiểm tra: ' + str(exc))
                for record in records:
                    if record.kind in {'decision', 'action'}:
                        hold_for_review(record)
                        record.warnings.append('Audit không hoàn tất; không được xem bản ghi này là đã xác nhận')
    elif engine == 'llm_api':
        warnings.append('Đã TẮT audit thứ hai: chưa rà soát độc lập mâu thuẫn/ngữ cảnh')
    if engine == 'llm_api':
        warnings.append('Kết quả LLM vẫn cần đối chiếu đáp án gán nhãn; audit không bảo đảm độ đúng ngữ nghĩa.')
    classify_information_utility(records, utterances)
    return AnalysisResult(engine=engine, utterances=utterances, records=records,
                          warnings=warnings, audit_findings=[f.model_dump() for f in audit_findings])

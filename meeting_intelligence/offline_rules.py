"""Clearly labeled OFFLINE BASELINE for narrow Vietnamese decision scenarios.

It proves parser + temporal resolver + evidence verifier work without API.
It is NOT a replacement for AI and is not claimed to cover other information kinds.
"""
from __future__ import annotations
import re
from .models import Event, Utterance

PROPOSE = re.compile(r"(?i)(?:đề xuất|gợi ý)\s+(?:chọn\s+)?(?:phương án\s+)?([A-Z])\b")
REPLACE = re.compile(r"(?i)(?:chuyển sang|đổi sang|thay (?:bằng|qua))\s+(?:phương án\s+)?([A-Z])\b")
AGREE = re.compile(r"(?i)(?:chốt|thống nhất chọn|quyết định chọn)\s+(?:phương án\s+)?([A-Z])\b")
REOPEN = re.compile(r"(?i)(?:chưa chốt|không chốt|mở lại quyết định|hủy quyết định)\b")
BLOCK = re.compile(r"(?i)(?:chưa (?:được )?triển khai|chờ phê duyệt|chưa được phê duyệt)\b")

def offline_extract_decisions(items: list[Utterance]) -> list[Event]:
    events = []
    for u in items:
        s = u.text
        # Cancellation is higher priority than a historical mention of 'chốt B'.
        if REOPEN.search(s) and ("phương án" in s.lower() or "quyết định" in s.lower() or "lựa chọn" in s.lower()):
            etype, value = "reopen", None
        elif BLOCK.search(s) and "phương án" in s.lower():
            etype, value = "execution_blocked", None
        elif (m := AGREE.search(s)):
            etype, value = ("conditional_agreement" if re.search(r"(?i)\bnếu\b", s) else "agreement"), "Phương án " + m.group(1).upper()
        elif (m := REPLACE.search(s)):
            etype, value = "counterproposal", "Phương án " + m.group(1).upper()
        elif (m := PROPOSE.search(s)):
            etype, value = "proposal", "Phương án " + m.group(1).upper()
        else:
            continue
        events.append(Event(issue_key="lua_chon_phuong_an", topic="Lựa chọn phương án",
                            kind="decision", event_type=etype, source_ids=[u.id], value=value,
                            condition=("Chờ phê duyệt" if etype == "execution_blocked" else
                                       "Cần thỏa điều kiện" if etype == "conditional_agreement" else None)))
    return events

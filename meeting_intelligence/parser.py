"""Turn pasted transcript into immutable, traceable utterances."""
from __future__ import annotations
import re
from .models import Utterance

ID_LINE = re.compile(r"^L\d{3,}\s*[|:]\s*")
TIME = re.compile(r"^(?P<time>\d{1,2}:\d{2}(?::\d{2})?)\s*[|\-–]\s*(?P<rest>.+)$")
SPEAKER = re.compile(r"^(?P<speaker>[^:|]{1,50})\s*:\s*(?P<text>.+)$")

def parse_transcript(raw: str) -> list[Utterance]:
    if not raw or not raw.strip():
        raise ValueError("Transcript không được để trống")
    output: list[Utterance] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        # Never trust user-supplied IDs as primary keys; normalize sequentially.
        line = ID_LINE.sub("", line)
        timestamp = speaker = None
        mt = TIME.match(line)
        if mt:
            timestamp, line = mt.group("time"), mt.group("rest").strip()
        # Accept both '09:00 | Lan | text' and '09:00 | Lan: text'.
        if " | " in line:
            parts = [p.strip() for p in line.split(" | ")]
            if len(parts) >= 2 and parts[0] and len(parts[0]) <= 50:
                speaker, line = parts[0], " | ".join(parts[1:])
        else:
            ms = SPEAKER.match(line)
            if ms and not re.match(r"^\d{1,2}$", ms.group("speaker")):
                speaker, line = ms.group("speaker").strip(), ms.group("text").strip()
        if not line:
            continue
        n = len(output) + 1
        output.append(Utterance(id=f"L{n:03d}", order=n, text=line, speaker=speaker, timestamp=timestamp))
    if not output:
        raise ValueError("Không tìm thấy phát biểu hợp lệ")
    if len(output) > 2500:
        raise ValueError("Bản chép lời quá dài cho MVP; giới hạn 2500 lượt nói")
    return output


def display_transcript(items: list[Utterance]) -> str:
    return "\n".join(f"{u.id} | {u.speaker or 'Không rõ người nói'} | {u.text}" for u in items)

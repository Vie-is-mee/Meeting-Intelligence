# Mission 3 · Stage 1B — Topic-aware consolidation of redundant unassigned decisions

Date: 2026-10-23 ICT. Branch: `mission3/improvement-20261021`. Scope: H03 topic-resolution and rigorous negative controls. **M2 `main` / tag / Render / Vercel production unchanged. M3 currently public remains `e8fe1f1`; candidate not deployed.**

## Original failure and evidence

Archived Groq H03: `docs/evaluation/mission3/m3_fresh_regression_H03_LC01_7e63907_run1.json`, completed with audit. Transcript:
- L001: request to check email configuration before next trial;
- L002/L003: unclear referent “anh ấy”, explicitly no confirmed assignee;
- L004/L005: Wednesday vs Thursday proposed;
- L006: *“Chưa chọn thứ Tư hay thứ Năm và chưa giao việc rà soát cho ai.”*

Original output had **3 records**: request/recorded, decision/open for schedule, and extra decision/open for not assigning anyone. The distinct lack of an assignee belongs with the unassigned request's evidence, not a standalone second business decision for the same task in this specific context. Frozen H03 gold requires the request and the open date decision; it allows no extra independently redundant decisions.

## Technical repair

1. `meeting_intelligence/extractor.py`: preserve an explicitly cited, literal *“chưa giao việc/chưa phân công”* event instead of replacing its value with the full source sentence whenever that sentence ALSO mentions an undecided date. This maintains the extractor's original decision target, not just a keyword from the same utterance.
2. `meeting_intelligence/topic_resolution.py` (**new**): after evidence verification, collapse only an unresolved single-event *no-one-assigned* decision when: (a) its source literally denies personal assignment and confirms date still undecided, (b) exactly one matching request with no owner and one matching open schedule decision already cover the topic, (c) there is no competing active/historical action record that this might contradict, and (d) the content is not a real choice between two people. This logic is topic-scoped and requires a source match; it is intentionally conservative and is NOT generic semantic entity resolution.
3. Preserve L006 as `counter_evidence_ids` and `field_evidence_ids.owner` on the surviving unassigned request, mark it for human review, and emit an explanation to both record and global warnings. No owner/deadline/approval is synthesized. Audit still runs on the resulting records.
4. `meeting_intelligence/pipeline.py`: invoke this consolidation after verification and before the C2 guard and audit. No UI/export or M2 changes.

## Tests and measurements

- Test-first archived replay: original archive H03 generated 3 records; new implementation generates **2** with the actual source L006 retained and `decision/open` for the unsettled date. This is **replayed Groq events**, not a new independent model sample.
- **6/6 Stage 1B focused deterministic tests PASS**, comprising archived output, semantically similar non-email case, independent person-choice survives, unrelated task survives, historical assigned-action contradiction survives, and standalone uncertain decision survives. The first two tests were observed to fail before the patch.
- **262/262 Python tests PASS; 13/13 frontend Node tests PASS; Python syntax compilation PASS.**
- Genuine Groq `openai/gpt-oss-120b`, temperature 0.6, reasoning low, 2560 extraction tokens / 1024 audit tokens, structured auto, audit on, no retries:
  - `docs/evaluation/mission3/m3_stage1b_h03_live_candidate_run1.json`: H03 COMPLETED, 2 API calls, 2 records (request/recorded unassigned with due `trước lần thử tiếp theo`; decision/open weekday not chosen), 0 audit findings.
  - `docs/evaluation/mission3/m3_stage1b_D01_H01_live_candidate_run1.json`: D01 COMPLETED, 2 calls, `decision/agreed` object storage and independent `decision/open` vendor, 0 audit findings; H01 COMPLETED, 2 calls, `decision/reopened`, `action/assigned` Huy due null, `issue/open`, 0 audit findings.
- All **three cases** ran on the same input dataset SHA and same core-module SHA fingerprint, recorded in raw JSON. Raw outputs and provider tokens retained, not edited.

## Strict interpretation (important)

- H03 fresh model output itself only had 2 records. Thus its fresh success does **not** establish causal contribution of this deduplication patch; the archived event replay is the controlled before/after evidence for this specific failure.
- D01 fresh 2-record success is also a single provider sample after Stage 1A; do not claim all wording variants now work. H01 is a targeted regression check only.
- Unit tests prove software contracts, not provider precision/recall; H03 is repeatedly inspected development/held-out fixture, **not a truly blind benchmark**.
- The deduplication logic intentionally abstains on nonassignment statements with unresolved alternative named assignees, contradictions from already assigned tasks, or no corroborating request/schedule. Its high precision may leave other harmless duplicates for human review; this is preferable to erasing true decisions.
- Neither 0 audit findings nor 3/3 COMPLETED proves there were no unsupported semantic facts.

## Gate / next action

**GO for Stage 1B code candidate and evidence commit; NO-GO for unconditional public rollout or M2 merge.** Proceed to Stage 1C: same-source full critical regression D03/D04/LC01–03 plus official C2 all four, subject to real Groq provider quota; report strict labels and raw output errors, then decide staging promotion. Continue to Stage 2 generalized C2 guard if candidate remains stable.

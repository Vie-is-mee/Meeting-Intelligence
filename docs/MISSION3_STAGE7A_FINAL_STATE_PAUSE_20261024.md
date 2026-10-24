# Mission 3 Stage 7A — Source-grounded final-state pause reliability

**Date:** 24 October 2026 ICT. Branch: `mission3/improvement-20261021`.
Baseline publicly released: `f72255c1eac84ba261f80671a426069eaa5dfff7`. This report documents a candidate on top of that commit. M2 main/tag and services remain untouched.

## Chosen problem (one meaningful M3 improvement)

A meeting-aware assistant that cites source lines yet treats suspended work as still actively assigned can create a harmful *false active action*. This is a high-impact final-state reliability failure.

**Frozen original Groq failure:**
`docs/evaluation/mission3/m3_stage4_LONG01_run1.json` (20 utterances). Mai accepted preparation of the supplier price comparison (L012), encountered missing price-view permission (L017), and An said *"Tạm dừng việc chuẩn bị bảng giá, hủy deadline thứ Hai để xin quyền"* (L018); Mai confirmed suspension (L019). The original Groq response emitted only `action/deadline_change` with `clear_fields=['due_raw']` for L018. Old code: `meeting_status=assigned`, `execution_status=unknown`, owner Mai, due null, **zero auditor findings**.

## Implemented hybrid fix

- `EventType.action_paused` and `MeetingStatus.paused` added to the typed schema. The extractor prompt differentiates **paused** from **cancelled** and from **deadline changed only**.
- The deterministic resolver also catches an old Groq `deadline_change` when its **own cited utterance** explicitly, affirmatively pauses **the same previously assigned task**. Topic/task evidence requires at least two nongeneric term matches; the cited utterance alone must make the pause explicit. This does not infer owners or new dates.
- Result is `meeting_status=paused`, `execution_status=blocked`, historical owner Mai retained, removed due reflected only when source explicitly removed it, source L018 for status/execution/counter-evidence, and `needs_review`.
- A later explicit personal assignment/acceptance resumes the task to assigned status. Unrelated work, hypothetical pause language, deadline-only changes and already cancelled tasks are negative controls. A claimed paused event without the requisite direct source is conservatively treated as a deadline update and review requirement.
- Frontend labels the task **Đang tạm dừng**, distinguishes owner historical from an active assignee, and displays source-grounded execution status.

## Controlled reproducible before/after

- `tests/test_mission3_stage7_final_state_pause.py`: original frozen Groq events reproduced the defect **before patch** (one of six tests failed: `assigned != paused`). Running the same events after patch: **6/6 PASS**, including exact owner, deadline, source L018, resume and negative controls.
- Full Python suite **279/279 PASS**; Node review/export **13/13 PASS** and `node --check frontend/app.js` PASS.
- **Fresh Groq** (not archived): `docs/evaluation/mission3/m3_stage7_long01_live_candidate_run1.json`; 20-utterance LONG01, extraction + audit completed (2 provider calls). Result: price-table task `action/paused`, `execution_status=blocked`, historical owner Mai, due null, counter evidence L018. In this run the extractor itself produced `action_paused`; therefore this is **end-to-end confirmation**, while the archived replay isolates the causal effect of the deterministic upgrade. Storage method agreed and independent vendor decision open, Huy assigned before Friday, audit zero findings.
- **Remaining semantic miss on this fresh run:** the separate `issue/open` about double-charged payment (L005) was not extracted, even though the old LONG01 run did contain it. Do not claim LONG01 or the model is fully accurate or generalized.
- C2 on new source: `docs/evaluation/mission3/m3_stage7_c2_retest_run1.json`. C2-01 COMPLETED with full audit and `action/unverified` owner/due null. C2-02 extraction completed with issue/open, decision/open, action/unverified owner/due null; second audit call hit provider **HTTP 429 TPM** (8000 limit, 5965 used, 2333 requested), hence `audit_completed=false`. Remaining C2-03 and C2-04 were NOT attempted after the rate limit stop. This is provider quota, not a clean semantic PASS, and no new-source 4/4 claim is made.

## Decision and boundaries

**GO as a local source-attested candidate for the paused-task reliability gap; public staging rollout requires version-matched deploy and public C2 smoke.** Existing M3 release remains the safe fallback. Do not alter Mission 2 or existing raw benchmark files.

This repair is deliberately limited: it does not solve every possible ambiguous reference, all LONG02 duplicates, or all completeness misses on long meetings. Source IDs show provenance, not semantic truth. Keep human-in-the-loop review before treating paused/ambiguous records as official tasks.

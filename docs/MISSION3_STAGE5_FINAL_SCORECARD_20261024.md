# Mission 3 Stage 5 — Source-locked candidate scorecard and release decision

**Date:** 24/10/2026 ICT. **Target branch:** `mission3/improvement-20261021`. **Candidate core:** source fingerprint in `docs/evaluation/mission3/m3_stage5_frozen_scorecard_0778afe_run1.json`. **Main M2 baseline** remains unchanged.

## What has been verified by running Groq

- Model `openai/gpt-oss-120b`, temperature 0.6, reasoning low, structured auto, second-pass audit enabled, no retry. Exact dataset/core SHAs are in raw output files and report.
- C2-01/02/03/04 + D01 + D04: **6/6 provider completions, 6/6 audits completed, 6/6 narrowly specified test requirements met**. Source-locked scoring script `scripts/score_mission3_stage5.py` verifies this and refuses to combine different source hashes.
- C2-01: an unverified action, null personal owner/due, L001 evidence. **1 accepted audit finding**.
- C2-02: issue/open, decision/open, action/unverified; no false Friday recorded request or assigned owner/due. **1 accepted audit finding**.
- C2-03: Huy assigned, due exactly `trước thứ Sáu`. 0 audit.
- C2-04: Lan cancelled with owner history intact, due null. 0 audit.
- D01: two independent decisions, agreed object storage and open provider. 0 audit.
- D04: beta conditional on **300 simultaneous users and no major error**. 0 audit.
- Evidence `docs/evaluation/mission3/m3_stage5_C201_C202_0778afe_run1.json`, `m3_stage5_C203_C204_0778afe_run1.json`, `m3_stage5_D01_D04_0778afe_run1.json`.

## Previous full regression

Stage1B/1C: 12 source-identical real Groq cases (H03,D01,H01,D03,D04,LC01–03 and C2-01–04), all provider calls completed; **LC01 had two, LC03 one, C2-02 one accepted audit warnings**; no claim of clean 12/12 semantics. Stage3 introduced source-grounded false-audit filters; a real LC01/LC03 rerun had zero accepted findings. Replay tests prove the rules apply to earlier false findings, not that the model became perfect.

## Stage4 genuine limitations

New long multi-topic synthetic tests are development/stress data, not blind independent gold:
- LONG01: a paused/cancelled Mai assignment remained active and separate open vendor choice omitted. **Not fixed**.
- LONG02: original had false request/extra decision and two audit findings; guarded update removes source-confirmed tentative collective request in event replay, and in a fresh Groq run L016 was no longer a recorded request. **One auditor finding and possible overlapping open decision remain**.
- These weaknesses are acknowledged; all high-impact records remain under human review. Do not treat all long meetings as safe to export automatically.

## Software gates and interpretability

- **273/273 Python tests PASS**, **13/13 Node tests PASS** at latest candidate source before final commit.
- Causal evidence is **archived original Groq event replay → changed deterministic core** for specific fixes; new stochastic Groq samples are additional end-to-end checks, not a controlled causal comparison.
- No independent human-labelled blind test set. Do not present assistant-authored fixtures as independent academic benchmark.
- Human-reviewed exports exclude unconfirmed or rejected tasks by design. Evidence L001 etc support provenance but are not automatic semantic approval.

## Release decision

**GO to deploy a separate M3 staging service only after final tests and version/commit fingerprint match**. GO for C2 and main demonstration core. **NO-GO** for claiming reliable universal long-meeting handling or automatically executing unresolved tasks. M2 `main`, old Render/Vercel production and tag must remain unchanged.

Time-critical remaining tasks before **18:00 on 24/10**: new Render M3 deployment, Vercel M3 update, public /api/version /api/config C2 smoke, human review/export click-through, video under five minutes, three written answers and form submission. Do not postpone submission to investigate nonblocking LONG01/LONG02 limitations.

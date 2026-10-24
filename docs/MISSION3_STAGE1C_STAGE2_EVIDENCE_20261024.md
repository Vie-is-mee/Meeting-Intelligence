# Mission 3 Stage 1C + Stage 2 — Source-locked verification and generalized false-request guard

Date: 2026-10-24 ICT. Branch: mission3/improvement-20261021.
Baseline tested: `013aa5b01f27a53042e7c2b54236b2a2cc7d5d97` (Stage 1A/1B). No M2 main/tag or production deployment was touched.

## Stage 1C real provider runs (Groq)
All runs below used `openai/gpt-oss-120b`, `temperature=0.6`, low reasoning, structured outputs auto, audit on, 2 provider calls per case, no retries, source-attested full core SHA. Each of the **12 cases** was completed with audit (H03,D01,H01 previously Stage1B + 9 new Stage1C). Completion is NOT semantic correctness.

- D01: agreed storage and independent open vendor choice, 0 audit.
- D03: agreed provider switch conditional on legal contract approval, open contract issue, 0 audit.
- D04: conditional beta with 300 simultaneous users AND no major errors, 0 audit.
- H01: reopened sync decision, Huy retains assignment without due, open permission issue, 0 audit.
- H03: only request/recorded unassigned plus one open deadline choice, 0 audit.
- LC01: cancelled Mai task, due null, but request remains recorded; **2 audit findings**, manual review needed.
- LC02: independent CSV requirement recorded, Dũng's library-X trial cancelled, implementation method open, 0 audit.
- LC03: agreed internal payment test, back-button request, Chi writing-guide action cancelled; **1 audit finding**, manual review needed.
- C2-01: action/unverified, no owner/due, evidence L001, 0 audit.
- C2-02: issue/open, tentative Friday promoted into request/recorded despite later denial; **semantic PARTIAL/FAIL for false-request guard**, 1 accepted audit finding. No owner/due fabricated.
- C2-03: action/assigned Huy with due `trước thứ Sáu`, no duplicate collective task, 0 audit.
- C2-04: cancelled Lan task, due null, 0 audit.

## Raw evidence, untouched
- `docs/evaluation/mission3/m3_stage1b_h03_live_candidate_run1.json`
- `docs/evaluation/mission3/m3_stage1b_D01_H01_live_candidate_run1.json`
- `docs/evaluation/mission3/m3_stage1c_D03_D04_013aa5b_run1.json`
- `docs/evaluation/mission3/m3_stage1c_LC01_LC02_013aa5b_run1.json`
- `docs/evaluation/mission3/m3_stage1c_LC03_013aa5b_run1.json`
- `docs/evaluation/mission3/m3_stage1c_C201_C202_013aa5b_run1.json`
- `docs/evaluation/mission3/m3_stage1c_C203_C204_013aa5b_run1.json`

The separate dataset `datasets/mission3_c2_stage1c_inputs_v1.json` includes only C2 transcript/input IDs and excludes gold to prevent contamination. All code fingerprints across Stage1B/1C source runs matched.

## Stage 2: evidence-driven repair

The specific C2-02 false-request failure occurs when the extraction model emits a `request_made` for a rhetorical scheduling proposal, despite a later explicit 'chưa chốt hạn'. Implemented `meeting_intelligence/commitment.py`: suppress only an otherwise unsupported recorded request whose unique source is an explicit tentative question about a date, a subsequent utterance explicitly denies the deadline, and there is no separate cited confirmation. Preserve all raw Groq events and source transcript. The rule does NOT change any owner/due, and does not suppress explicit requirements or a proposal with an independent later acceptance.

Tests `tests/test_mission3_stage2_false_request.py` include frozen Groq event replay of C2-02 and three positive/negative controls: valid later confirmed request, explicit requirement, and unrelated denial. All **4/4 focused, 266/266 total Python, 13/13 Node frontend** tests passed.

A new **provider** call on updated Stage 2 source completed C2-02 with audit, **0 audit findings**, producing issue/open, decision/open (deadline and assignment not confirmed), action/unverified with null owner/due. Source-attested result:
`docs/evaluation/mission3/m3_stage2_C202_guard_live_run1.json`.

Important causal caveat: in this fresh run the LLM did NOT produce the erroneous request; therefore actual patch efficacy is shown by replaying the **old failing model output** through the changed core. The fresh run verifies end-to-end behavior but cannot isolate patch's causal effect.

## Remaining risks and next gates

- LC01 (2 audit findings) and LC03 (1 audit finding) require semantic review; do not call full suite 12/12 accuracy.
- C2 generalization beyond these four development fixtures and natural language variants remains unverified. Request suppression is intentionally conservative; other phrases remain reviewable.
- Evidence citations are not proof of field-semantic correctness.
- Need Stage3 field-evidence and audit inspection; Stage4 long-meeting test (time permitting), wider evaluation and public staging release; M2 `main` stays frozen.
- Hard submission deadline **2026-10-24 18:00 ICT**: reserve time for staging smoke, video and 3 form answers. Do not release candidate without stable Groq frontend/backend checks.

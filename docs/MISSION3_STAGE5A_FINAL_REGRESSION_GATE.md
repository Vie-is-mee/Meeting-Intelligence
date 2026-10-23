# Mission 3 — Stage 5A final regression (release-candidate gate)

**Date:** 23 October 2026 (ICT). **Branch:** `mission3/improvement-20261021`; **core source:** commit `190bcbdfaf2354f739d5b4e2b684cad43623ba63`. Status: **PARTIAL — NO-GO for a blanket 4/4 semantic pass**.

## What was run
- Python: **249/249 PASS**. Node (review/export/deployment): **13/13 PASS**.
- Fresh local Groq with audit on the **same identical source/input SHA fingerprint** for D01/D03/D04/H01. Both source-attested raw files retain failures and warnings:
  - `docs/evaluation/mission3/m3_final_rc_D01_D03_190bcbd_v1.json`
  - `docs/evaluation/mission3/m3_final_rc_D04_H01_190bcbd_v1.json`
- Earlier D01/D03 results from `bcbfcd9` are **not** reused as same-revision final release evidence: seven core module SHA hashes differ, despite earlier favorable outcomes.

| Case | Groq completion | Actual core result | Auditor | Verdict |
|---|---|---|---|---|
| D01 | COMPLETED | Object storage agreed for pilot, **supplier choice open only inside the agreed content, missing a distinct open-decision record** | 1 medium warning incorrectly asks to encode supplier scheduling as a condition of storage choice | **PARTIAL / REGRESSION** — missing independent provider decision |
| D03 | COMPLETED | Decision agreed, deployment blocked pending legal approval, issue open | 0 | **Core PASS**, record-level adjudication still required |
| D04 | COMPLETED | Conditional agreement requires **300 simultaneous users AND no severe defects** | 0 | **Core PASS**, record-level adjudication still required |
| H01 | COMPLETED | Earlier decision reopened, Huy assigned action, access issue open | 0 | **Core PASS**, record-level adjudication still required |

**D01 diagnosis:** L006 explicitly says “Chốt dùng object storage cho bản thử nghiệm. Nhà cung cấp để cuộc họp sau chọn.” Current extraction emits one agreement with both meanings combined (`storage_choice`) and no separate `decision/open` for supplier selection. The current auditor falsely interprets this open supplier choice as a *missing condition* on storage approval. This is a genuine failure against the earlier D01 expectation, not a clean 4/4. Do not rewrite gold, delete the error, or select an older successful run to make scorecard green.

## Official C2 Change Request (distinct test set)
- Frozen C2 cases from `datasets/mission3_c2_v1.json`, same M3 source `68cfbb0` with the later evidence commit `190bcbd`. 4/4 provider requests completed and central owner/deadline/action-state constraints were met; C2-02 has 2 accepted audit warnings.
- M2 exact-tag baseline is `439f672`, same four transcripts/provider settings. M2 did **not** invent owners/deadlines in these four runs. Actual M3 gain observed: handling group pledge as unresolved action; no accidental commitment for a tentative Friday; no duplicate task after named Huy acceptance; preserves historical Lan cancellation.
- Software test count != semantic accuracy. All four test transcripts are internal development fixtures, not a new independent holdout.

## Product decision / scope
- **GO:** lock the code/reliability core for staging and present source-attested improvement evidence. C2 requires preserving `action/unverified` and not exposing it as authorized assignment/export.
- **NO-GO:** claim generalized accuracy improvement, claim 4/4 regression perfect, or deploy `main` without an accepted release review.
- **D01 severity:** P1 (not official C2 blocker), visible in history. Fix only if it can be implemented with general-topic separation rule + positive/negative controls before release deadline; otherwise list as limitation and keep focus on staging, working demo, video and required submission.
- **Remaining gates:** online M3 backend actually running branch/commit, frontend/backend matched, CORS and Groq runtime, evidence/review/export smoke check, 5-minute video, all 3 official written answers and submission link confirmation. No video link or form completion verified yet.

## Why this is a product improvement
Mission 2 extracted structured statements. Mission 3 chooses reliability and source-grounded state resolution: distinguishes explicit acceptance from group intent, preserves evidence and risk statuses, updates cancelled/reopened tasks, prevents false obligations. The rigor of recording a D01 regression is part of the verification discipline — source evidence alone does not prove that the system interpreted every topic correctly.

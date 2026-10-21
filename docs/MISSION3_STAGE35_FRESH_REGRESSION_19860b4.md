# Stage 3.5 — Four previously passing M2 cases, fresh M3 regression

**Date:** 22/10/2026 ICT. **Source tested:** `19860b4` (same tracked core snapshot as the four saved raw files; hashes within reports are authoritative). **Groq inference NEW**, not archived-event replay. These are previously seen development regression cases, not independent holdout.

## Protocol / provenance
- `openai/gpt-oss-120b`, temperature 0.6, reasoning low; extraction budget 2560 and audit budget 1024; audit on, 0 retry, 60-second min interval.
- Frozen dataset: `docs/evaluation/final_regression_input_v2.json`; original M2 A baseline `docs/FINAL_REGRESSION_RESULTS.md`.
- Results: **4/4 pipeline COMPLETED**, **8 API calls**, **19,113 provider tokens**, 0 API error. Three raw JSON files below hold all records, history, source citations and audit outputs:
  - `docs/evaluation/mission3/m3_fresh_regression_D01_19860b4_run1.json`
  - `docs/evaluation/mission3/m3_fresh_regression_D03_D04_19860b4_run1.json`
  - `docs/evaluation/mission3/m3_fresh_regression_H01_19860b4_run1.json`

## Outcomes on previous M2 passing gates

| Case | Required expectation | Fresh M3 result | Preliminary verdict |
|---|---|---|---|
| **D01** | Object storage agreed; vendor remains independent/open, not an implementation condition | Two decisions: `storage_choice/agreed` and `m3_recovered_deferred_open_L006/open`; correct source L006 and review flag, no audit finding | **Core + audit PASS** |
| **D03** | New supplier agreed for design only, execution blocked pending legal, legal issue open | `decision/agreed/blocked` with legal condition + `issue/open`, no audit | **Core + audit PASS** |
| **D04** | Beta conditional on 300 concurrent users AND no severe issue | `decision/conditional/pending_condition`, complete latest conjunction, no audit | **Core + audit PASS** |
| **H01** | Decision reopened and Huy's independent task persists | `decision/reopened`, `action/assigned` owner Huy, additional source-backed `issue/open`; **auditor incorrectly demands old security condition after reopen** | **Core PASS / full audit FAIL** |

**Provisional total: 4/4 core cases, 3/4 full-clean cases**. `H01` is NOT full pass at this source snapshot because its finding requires manual review; extra `issue/open` appears source-supported (L003) but may require independent adjudication against frozen expected output.

## Root cause of H01 failure

L001 conditional-agreement mentions security approval; L004 **reopens** the choice and explicitly says the team has **not chosen** between automatic/manual sync. The historical prerequisite from L001 cannot remain a current operative condition of the reopened choice. The auditor cited L001/L004 and called `condition=null` an omission, despite current status `reopened`.

A subsequent narrow guard in `meeting_intelligence/auditor.py` rejects only a finding that (a) claims a missing old `condition=null`, (b) refers to an actual earlier `conditional_agreement` and a later `reopen` in the same record history, and (c) has **no later re-agreement**. Test controls require the guard NOT to suppress conditions still in force or a new approval after reopening. Code was developed **after** this Groq run. It cannot retroactively turn this provider output into full pass.

## Interpretation and next gate

- Compare this with earlier source `c443647`, where **D01 failed and D03/D04/H01 core passed**. The fresh source restored D01 without deleting the positive cases.
- Still need **fresh H01 on the new audited code**, fresh M3 full four-case evaluation on the latest source if claiming a single end-to-end run, and checks for H03/LC01/LC02/LC03.
- Source-attested M2 vs M3 four-case development comparison is archived separately at [MISSION3_STAGE35_MATCHED_SOURCE_BEFORE_AFTER.md](MISSION3_STAGE35_MATCHED_SOURCE_BEFORE_AFTER.md).
- **NO-GO production** until all gating regressions/CR and deployment verification pass. Never combine best case output from separate commits into one claimed full run.

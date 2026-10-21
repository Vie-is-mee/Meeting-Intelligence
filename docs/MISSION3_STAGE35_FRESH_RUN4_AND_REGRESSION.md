# Mission 3 — Stage 3.5 — Fresh Groq run 4 + M2 passing-case regression

**Date:** 2026-10-22 ICT. **Exact M3 source:** `c443647f9a05eb967437544be9bc588d0f85a3a5`. **ACTUAL newly sampled Groq outputs** (not deterministic replay). The four comparison cases and old regression cases are development cases with assistant-derived gold, not independent human-labeled holdout.

## 1. Frozen M3 four-case run 4

- Model `openai/gpt-oss-120b`, temperature 0.6, reasoning low, extraction max 2560, auditor max 1024, audit on, zero retries.
- Input/label SHA-256 unchanged from frozen Stage 0.5 manifest.
- **4/4 completed, 8 provider calls, 19,064 reported tokens**. Strict merged raw output `docs/evaluation/mission3/m3_fresh_full_run4.json`; individual `m3_fresh_E01_run4.json`, `m3_fresh_E02_run4.json`, `m3_fresh_R01_run4.json`, `m3_fresh_K01_run4.json`.
- M3-E01: 3 core records right (CSV request, cancelled Lan trial, implementation choice open); **auditor high-severity unsupported_fact false positive** claims `owner=Lan` cited from assignment L002 is insufficient without separately citing Lan acceptance L003 (which is in transcript). **Not full clean pass**; this is an evidence-completeness/acceptance-source issue, not evidence that owner is fabricated.
- M3-E02: single cancelled internal trial, no duplicate request; audit empty. **Full PASS**.
- M3-R01: B agreed for pilot/blocked by legal, vendor choice open; `condition=None` has no misleading condition field evidence, audit empty. **Full PASS**.
- M3-K01: action with owner/due correct; idempotency reusable candidate and unbenchmarked rumor needs verification; choice open, audit empty. Strict frozen label expects practice knowledge `meeting_status=recorded` but machine keeps `unverified` for safety. **2/3 strict required**, utility achieved.
- **Provisional internal scoring**: 7/8 strict required, 3/4 core cases, 2/4 full cases. Do not treat four synthetic development cases as broad model accuracy.
- Compared to previous M3 runs: run1 full 1/4, run2 2/4, run3 2/4, run4 2/4. Different error patterns show stochastic variability. No per-case best-of-N selection is valid as final reported performance.

## 2. Fresh regression on four cases M2 had already passed (same source c443647)

**Protocol:** `scripts/run_dataset.py` with the locked `docs/evaluation/final_regression_input_v2.json`, one exact-source M3 fresh provider execution per case, audit on, no retries. Separate saved raw files:

| Case | M2 frozen baseline A | Actual M3 fresh c443647 | Preliminary verdict |
|---|---|---|---|
| **D01** | object storage agreed + independent vendor choice open, no false audit | Only storage agreement; **missing vendor open**. Audit incorrectly treats deferred vendor selection as a condition on storage. | **FAIL — serious regression.** |
| **D03** | design agreed; rollout legally blocked; legal approval issue open | Two records correct, agreed/blocked and issue open; zero audit | PASS |
| **D04** | conditional 300 concurrent users AND no severe defect | One conditional decision and both condition clauses, zero audit | PASS |
| **H01** | decision reopened, independent Huy action assigned | Both states preserved, zero audit | PASS |

Totals: **4/4 provider pipelines completed, 8 API calls, 18,429 provider-reported tokens**; preliminary **3/4 core/full regression cases pass**, one D01 failure. This is **NOT acceptable for release** since M2 A passed all four previously.

Raw historical regression outputs (individually source-hashed by runner):
- `docs/evaluation/mission3/m3_fresh_regression_D01_c443647.json`
- `docs/evaluation/mission3/m3_fresh_regression_D03_c443647.json`
- `docs/evaluation/mission3/m3_fresh_regression_D04_c443647.json`
- `docs/evaluation/mission3/m3_fresh_regression_H01_c443647.json`

## 3. Root causes — important for the research history

**D01:** The source says **`Chốt dùng object storage cho bản thử nghiệm. Nhà cung cấp để cuộc họp sau chọn.`** Both statements occur in L006. A supplier is an **independent open decision**, not a condition for object storage. The Stage 2 explicit omission patterns recognized `chưa chốt nhà cung cấp` but not **deferred selection** `nhà cung cấp để cuộc họp sau chọn`. Source-id-only deduplication must not treat the storage agreement at L006 as proof a vendor choice was extracted — two different issues can share one utterance.

**E01 owner-audit:** L002 explicitly assigns Lan and L003 is Lan's acceptance. `owner=Lan` is historically correct even though the task is later cancelled. The audit finding requests stronger evidence. This should be evaluated by whether the owner field should cite both L002/L003, not by blindly deleting Lan or suppressing all unsupported_fact.

**Lifecycle semantics:** D03, D04, H01 still preserve the important design/rollout, compound condition, and independent action distinctions. These are positive controls to retain when repairing D01.

## 4. Go/No-Go

- Engineering tests on source c443647: **212 Python + 13 Node passed**.
- Four-case fresh M3: **all operationally complete but only 2/4 clean full cases**, internal development review.
- Four original passing-case regression: **D01 FAIL, D03/D04/H01 pass**; hard release gate G1 not met.
- **NO-GO for merging `main`, Vercel/Render deployment or contest submission claims.**
- Next minimum patch: specifically recover deferred vendor choice when explicitly said in an utterance containing *another agreed decision*; preserve history, avoid inventing owner/condition, check alternate lexicographic proposal, and require tests for independent cross-issue same-utterance evidence.
- Next real Groq evaluation must use a **new commit and new raw output paths**, never overwrite any of four run sets or original M2 Before.

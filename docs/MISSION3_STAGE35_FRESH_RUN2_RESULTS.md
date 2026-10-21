# Mission 3 — Stage 3.5 — Fresh Groq run 2 (source pinned)

**Date:** 2026-10-21/22 ICT. **Source:** `9d9082cc0f5676faa63371275e243ace6a28ad3b`. This is **actual independently sampled Groq output from M3 source**, NOT replay. Results are from **four assistant-authored development transcripts**, not an independent holdout.

## Protocol and immutable raw results
- Model `openai/gpt-oss-120b`; temperature 0.6; reasoning low; extraction budget 2560, audit enabled, Groq strict/auto. One generation per case, no cherry-picked retries.
- Frozen input SHA-256 `d01ea985df426a4e2fc9360056838122d22773a71303fcf3c3b5cc5fe8926852`; labels SHA-256 `464045dc9216a93776da6a9b2f1ede667c15fbd5d7c9a86ce5448edb9a12daf6`.
- **4/4 completed, 8 API calls, 18,791 reported tokens, zero API failures.** Exact source, module SHA and provider setup are in `docs/evaluation/mission3/m3_fresh_full_run2.json`.
- Individual unchanged raw outputs `m3_fresh_E01_run2.json`, `m3_fresh_E02_run2.json`, `m3_fresh_R01_run2.json`, `m3_fresh_K01_run2.json`; merged using strict disjoint source/config SHA verification. Source of M2 baseline remains hosted-M2 `m2_remote_baseline_v1.json`, **with server SHA not attested**.
- Review packet `docs/evaluation/mission3/m3_fresh_manual_review_packet_run2.md`; semantic judgment below is **assistant provisional analysis**, not independent.

## Case findings and Before/After qualification

| Case | Raw M3 run2 | Provisional outcome |
|---|---|---|
| **M3-E01** | 3 records: `issue/open` + `request/recorded` from **the same L001 customer CSV request**, and `action/cancelled`. The false proposal from run1 is gone, but **`decision/open` for alternative at L005 missing**. | Required request + cancelled action **2/2 correct**, but semantic duplicate issue and optional unresolved choice missed; **NOT full pass**. Stochastic LLM events differ from run1. |
| **M3-E02** | Exactly one action `cancelled`, owner Lan historical, no duplicate request or decision, zero audit finding. | **1/1 required, full PASS**. |
| **M3-R01** | Pilot B `agreed` + rollout `blocked` with legal condition L004; vendor open L005, zero audit findings. | **2/2 required, full PASS**. Audit false positives from run1 no longer appear. |
| **M3-K01** | Lan load test assigned with `thứ Sáu`; idempotency practice `reusable_candidate` and unverified; Y/X performance rumor `needs_verification`; library choice `open`; zero audit findings. | **2/3 strict required** due frozen gold expecting practice `recorded` vs safe AI `unverified`. M3-only utility correctly separated. **Not strict full pass**. |

Provisional strict semantic review on the frozen requirements: **7/8 required**, **3/4 core cases**, **2/4 full cases** (E02/R01). Hosted M2 internal Before was **6/8 required**, **3/4 core**, **1/4 full**. This suggests one additional full-case pass on these tiny development cases, but **not statistically robust or fully matched source/config**, and not independent review. Run1 M3 was 1/4 full on the same cases, illustrating generation variability; **do not hide run1 or portray run2 as the only trial**.

Run1 has its own immutable artifacts and reported 19,989 tokens. Run2 has 18,791 tokens. These are separate generations, NOT best-of-N submissions.

## Root causes observed in M3 E01 run2

- The LLM emitted `kind=issue, event_type=issue_reported`, text **exactly describing L001 customer requirement** instead of request. Stage2 bounded recovery correctly added request but left issue, producing duplication.
- L005 says **`còn cách làm khác thì chưa chốt`** (subject before negation). Existing recovery recognizes `chưa chốt cách làm` (opposite order) but missed this utterance.
- Stage3.5 follow-up patch must normalize an `issue_reported` **only when it exactly duplicates a stand-alone, source-backed customer request**; do not remove an independent issue about e.g. export malfunction.
- Add narrow suffix-form unresolved choice recovery with negative controls for same-line later agreement.
- Preserve original run2 raw, frozen gold and M2 tag. All new code must have separate commit and new run3 output.

## Status/next

Engineering fixes for these two E01 defects have been drafted with direct negative-control tests. The initial fuller regression detected that Stage3.5 suffix recovery adds an *optional* open choice to the earlier E01 replay; old tests checking exact 2-record count were updated to assert the **more faithful 3-record outcome**, without changing locked labels. Await a fresh provider run on the new source commit before any release decision.

Release **NO-GO** at this stage: E01 still not clean in run2; new source not yet evaluated by Groq. Fresh old D01/D03/D04/H01 regression and official assigned Change Request remain outstanding.

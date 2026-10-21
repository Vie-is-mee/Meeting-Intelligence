# Mission 3 — Stage 3.5 fresh Groq Run 5 and regression follow-up

**Execution:** 21–22 October 2026 ICT. **Environment:** local Groq, `openai/gpt-oss-120b`, temperature 0.6, low reasoning, extraction budget 2560, audit enabled. API key only in untracked local `.env`. No production deploy, no `main` merge.

## Locked four-case Before/After follow-up

The source-attested run of `M3-E01` used core commit `031aee289f1daa686a02552b121c09ac8136171c`. Cases `M3-E02`, `M3-R01`, `M3-K01` used the **same commit, module SHA fingerprints and generation settings**. The merger accepted the disjoint case files as `m3_fresh_full_031aee2_run5.json`; previous four rounds were preserved.

| Case | Fresh model observations | Auditor findings | Qualification |
|---|---|---:|---|
| E01 | CSV request recorded; Lan's library-X task cancelled with historical owner; alternate choice open | 0 | Targeted auditor false-positive from run4 did not recur |
| E02 | One cancelled action; no spurious request | 0 | No regression on simple cancellation |
| R01 | Pilot B agreed but execution blocked; vendor remains open | 0 | Does not confuse separate topics |
| K01 | Assigned load test; practice knowledge unverified/reusable candidate; rumor unverified; library choice open | 0 | Frozen strict label for practice expects `recorded`; do **not** claim strict pass |

Four of four cases completed by the provider. **This is a small, internally labelled synthetic development set, not independent accuracy or a statistically representative sample.** Detailed per-field and frozen-label review checklist: `m3_fresh_manual_review_packet_031aee2_run5.md`. No result cherry-picking; original artifacts retained.

### Historic M2 comparison limits

Archived hosted M2 baseline and exact-tag local M2 tests are stored separately. Original hosted deployment did not attest its precise source SHA. M3’s four-case run uses a pinned local M3 source and is a genuine new provider invocation. The evidence does **not** establish generalized percentage gains without a comparable manually adjudicated benchmark.

## Core-regression Groq results on source after the four-case run

Existing runner `scripts/run_dataset.py` was used with frozen historical D/H transcripts, generating separate raw JSON artifacts. The repository later advanced to `19860b4` for an exact-tag M2 artifact commit; no M3 core module changed relative to `031aee2` during the check.

| Case | Fresh provider completion and content | Audit | Assessment |
|---|---|---|---|
| D01 | Completed. Object storage **agreed**; provider **open** | 0 | Core preserved |
| D03 | Completed. Decision **agreed** but execution **blocked** pending legal; feedback and issue also present | 0 | Core preserved; extra records need separate field-level inspection |
| D04 | Completed. Decision **conditional**, pending both 300 concurrent users **and** no serious errors | 0 | Core preserved |
| H01 | Completed. Decision **reopened**, Huy action **assigned**, plus separate request to clarify reading access | **1** high-severity | **Not full pass** pending adjudication of whether earlier condition should remain after reopening |

**H01 finding detail:** Auditor says the reopened decision loses the earlier security approval condition. But the decision had subsequently been reopened; depending on how the older condition was superseded, demanding it in the *current* condition field can itself be a false positive. The extra `request` may be a legitimate distinct requirement or a redundant echo. **Do not suppress the finding wholesale or call this case clean without comparing L001–L004 and archived gold.**

### Artifacts

- `docs/evaluation/mission3/m3_fresh_E01_031aee2_run5.json` — fresh E01 raw.
- `docs/evaluation/mission3/m3_fresh_remaining_031aee2_run5.json` — fresh remaining three raw.
- `docs/evaluation/mission3/m3_fresh_full_031aee2_run5.json` — strict merge with source fingerprints.
- `docs/evaluation/mission3/m3_fresh_manual_review_packet_031aee2_run5.md` — complete four-case per-field reviewer packet.
- `docs/evaluation/mission3/m3_fresh_regression_D01_19860b4_run1.json` — D01 Groq.
- `docs/evaluation/mission3/m3_fresh_regression_D03_19860b4_run1.json` — D03 Groq.
- `docs/evaluation/mission3/m3_fresh_regression_D04_H01_19860b4_run1.json` — D04 and H01 Groq.

### Gate and prioritization

**GO for further engineering evaluation:** core paths work, no request/permission key leaked, raw outputs retained. **NO-GO for claiming all regression cases full-pass or for promoting to production.** Immediate next step: inspect H01 transcript, labels and auditor filter, add positive/negative controls for reopened-condition provenance, then assess against existing D/H and LC suites. Complete the official individually assigned Change Request and deliverable release checks before touching production.

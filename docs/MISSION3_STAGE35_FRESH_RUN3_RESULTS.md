# Mission 3 — Stage 3.5 — Fresh Groq run 3 (single pinned source)

**Date:** 2026-10-22 ICT. **Source:** `549a1455885a72133618ebfe229f59de7e34539e`. This is **new live M3 Groq inference**, not an archived-events replay. Four synthetic development cases, no independent adjudication.

## Protocol / provenance
- Model: `openai/gpt-oss-120b`, temperature `0.6`, reasoning `low`, extraction budget 2,560 tokens and separate audit budget 1,024; audit enabled; no retries.
- Frozen data and labels unchanged: input `d01ea985df426a4e2fc9360056838122d22773a71303fcf3c3b5cc5fe8926852`; label `464045dc9216a93776da6a9b2f1ede667c15fbd5d7c9a86ce5448edb9a12daf6`.
- **4/4 completed, 8 provider calls, 19,410 reported tokens.** No API errors.
- Raw original per-case `m3_fresh_E01_run3.json`, `m3_fresh_E02_run3.json`, `m3_fresh_R01_run3.json`, `m3_fresh_K01_run3.json`. Strict merged `m3_fresh_full_run3.json`; manual checklist `m3_fresh_manual_review_packet_run3.md`.
- Hosted M2 prior Before is a separate Groq invocation with non-attested server source SHA. These assistant-labelled cases are known *development* cases, not blind accuracy validation.

## Per-case new output and exact observations

| Case | Groq run3 | Provisional strict semantic judgment |
|---|---|---|
| **M3-E01** | Three records: CSV customer request `recorded`, Lan's library-X trial `cancelled`, alternative implementation `open` at L005; **zero false proposal/issue and zero accepted audit finding** | Required 2/2; **full PASS** on case expectations |
| **M3-E02** | One `action/cancelled` with Lan historical owner; zero extra request/decision, audit empty | Required 1/1; **full PASS** |
| **M3-R01** | B agreed for pilot but deployment blocked until legal; vendor open. **One auditor unsupported_fact finding** claims the open vendor record has a condition field citation even though `condition=None` | Required 2/2; **not full pass** due questionable/stale condition field provenance warning |
| **M3-K01** | Lan load test assigned with Friday deadline; idempotency advice `reusable_candidate`/unverified; unbenchmarked library speed claim `needs_verification`; library choice open | Required 2/3 **strict**: frozen expected practice knowledge `recorded` while intentionally cautious implementation keeps `unverified`; utility split correct but this is not full strict pass |

**Provisional internal summary:** **7/8 strict required matches**, **3/4 core cases**, **2/4 full cases**. Compared to hosted M2 Before: **6/8 strict required**, **3/4 core cases**, **1/4 full**. Run1 on M3 had 1/4 full; run2 2/4; run3 2/4. This highlights **sampling variance** at temperature 0.6, small development dataset, and the importance of retaining all runs. **Never claim a statistically reliable 2x overall accuracy gain or 100% M3.**

## What run3 proves and reveals
- **E01:** the Stage 3.5 exact customer-request + inverted open-choice enhancements did not break this case in fresh Groq output. The current output has expected three roles with source IDs.
- **R01 metadata gap:** the `open` supplier decision has `condition=None` but `field_evidence_ids.condition=['L005']`. The auditor can reasonably read that as misallocated current-field evidence; rather than filter every mention of null `condition`, the next code change should selectively remove **operative condition metadata** from an `unresolved`-only open choice, while keeping original history and evidence for cancelled or reopened states that explicitly cleared a condition.
- **K01:** absence of verified company knowledge is an intentional safety boundary; frozen `recorded` label and `unverified` AI output must be evaluated separately from utility correctness.
- D01/D03/D04/H01 old regression has **not been freshly rerun on this code**; do not merge production.

## Decision
**Engineering candidate shows progress, but RELEASE NO-GO** until R01 metadata fix plus positive/negative controls, fresh regression on the previously passing M2 cases, actual CR and deployment checks. Subsequent Groq runs require a NEW code commit and independent raw artifacts.

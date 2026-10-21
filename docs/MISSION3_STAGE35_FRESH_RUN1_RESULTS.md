# Mission 3 — Stage 3.5 — Fresh Groq run 1 (source pinned)

**Date:** 2026-10-21 ICT. **Observed source:** `0e00f9b24b5f7554975fd05b055a9921678be4d8`. **Evidence: ACTUAL NEW M3 PROVIDER INFERENCE**, not replay. Synthetic development cases, assistant semantic inspection (NOT independent, NOT held-out).

## Exact setup and data
- Source: M3 branch `mission3/improvement-20261021`; SHA-256 hashes embedded in original manifests.
- LLM: `openai/gpt-oss-120b`, temperature `0.6`, reasoning `low`, extraction budget `2560`, structured `auto`; audit `on`. Runner settings `call_interval=60`, retries `0`.
- Source M2 Before: `docs/evaluation/mission3/m2_remote_baseline_v1.json` — hosted M2, exact server SHA not provided; different provider run and cannot be characterized as exact-tag local M2.
- Frozen synthetic four-case transcript SHA-256: `d01ea985df426a4e2fc9360056838122d22773a71303fcf3c3b5cc5fe8926852`. Labels SHA-256 `464045dc9216a93776da6a9b2f1ede667c15fbd5d7c9a86ce5448edb9a12daf6`.
- **4/4** M3 live provider pipelines completed, **8 provider calls**, **19,989 provider-reported tokens**, zero HTTP errors. Each case run once. File `docs/evaluation/mission3/m3_fresh_full_run1.json` is strict merge of all four separate original runs. No cherry-pick.
- Review below is **assistant provisional case-by-case interpretation** of visible raw outputs, not an independent blind review. Scoring conventions follow `docs/MISSION3_STAGE_05_BASELINE.md`; numbers should be rechecked with human adjudication.

## Case-by-case actual output and findings

| Case | Original M2 Before [real hosted] | New M3 Groq run1 [real local source] | Provisional judgment |
|---|---|---|---|
| M3-E01 | Request CSV + cancelled task, bad audit condition | Request CSV `recorded`, action X `cancelled`, alternative `open`, **extra spurious `decision/proposed`** from source L002 `Giao Lan thử thư viện X`; auditor no false finding | Required core 2/2; **not full pass** due extra proposal. No independent business intent supports proposed decision. |
| M3-E02 | Single cancelled task; no fake request | Single `action/cancelled`, Lan historical owner, no fake request; audit empty | Core and full PASS (1/1 required). |
| M3-R01 | B agreed/pilot, rollout blocked; vendor open; cross-topic verifier warning | Two decision records have correct operative states, but auditor accepts **two likely false findings**: one says missing proposal history L001/L002, despite both proposal events being present in the decision's `history`; another says `condition` source L005 is unsupported even though vendor condition **value is null** | Core 2/2. **Not full pass** due audit false positives. Need inspect cited history and absent-value semantics before filtering. |
| M3-K01 | Load test correct, practices/rumor both knowledge with no utility, library choice proposed | Load test `action/assigned` with Lan and due `thứ Sáu`; idempotency key labelled `reusable_candidate` but `meeting_status=unverified`; anecdote labelled `needs_verification`; library choice `open`. Audit empty | **2/3 strict required** because frozen label says practice knowledge `recorded` while model deliberately uses cautious `unverified`. Utility behavior demonstrated separately. Do NOT silently change gold or count utility as full fact correctness. |

**Provisional four-case totals:** 4/4 operational completion; required core targets **7/8** under the frozen strict states; **3/4** cases have all required core targets; **1/4** passes both clean output and audit (E02). Comparison with hosted M2 internal review: M2 **6/8 required, 3/4 core cases, 1/4 full cases**, 18,141 tokens. M3 output is more informative on K01 utility/open state but also exposes false proposal and audit false positives. Thus **do not claim overall full-case accuracy improvement** on run1. Provider tokens: M3 19,989 vs hosted M2 18,141; conditions are similar but source SHA of hosted M2 is unattested.

## Root causes and testable patch hypotheses

**F1: E01 proposal echo.** `drop_spurious_task_proposals` recognizes a direct name-first command, but L002 begins **`Giao Lan ...`**. The model emits a proposal with the same `issue_key=task_csv_libX` and same normalized content as the assigned-then-cancelled task, and the later receiver confirmation exists in L003. Extend only the high-precision name-instruction prefix, require matching issue + exact content + explicit later receiver acceptance; add independent-proposal preservation tests.

**F2: R01 false missing late proposal.** The auditor's alleged missing L001/L002 change is **already fully represented** as two proposal events in the record's `history`, followed by agreement L003. A highly restricted validation can reject a finding demanding missing earlier proposal history when its exact sources exist as proposal history and a later agreement exists. Never suppress a true missing cancellation/reopen or final state change.

**F3: R01 null condition audit.** The vendor open record has `condition=None`, but a stale `field_evidence_ids.condition=['L005']` makes auditor think a current condition exists. Drop *current-field* evidence references for null fields while preserving event history and sources for `meeting_status`/`content`. Guard only false allegations of a non-existent operative condition; retain legitimate condition discrepancy findings for non-null value.

## Evidence and constraints

- Individual immutable outputs: `m3_fresh_E02_run1.json`, `m3_fresh_E01_run1.json`, `m3_fresh_R01_run1.json`, `m3_fresh_K01_run1.json`.
- Strict merged run: `docs/evaluation/mission3/m3_fresh_full_run1.json`.
- Unscored review packet: `docs/evaluation/mission3/m3_fresh_manual_review_packet_run1.md`.
- No source code has been patched **within** run1. Any narrow correction and subsequent provider run must use a **new commit and unique run2 files**; never overwrite this baseline.
- No old eight-case **fresh** regression was run at this point. No independent holdout was scored. Release gate remains **NO-GO**.

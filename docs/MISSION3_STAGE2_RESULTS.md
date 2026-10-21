# Mission 3 — Stage 2: Evidence validation and explicit omission recovery

**Execution:** 21 October 2026 (ICT). **Branch:** `mission3/improvement-20261021`.
**Status:** Stage 2 Python implementation and deterministic validation **completed**; **fresh LLM inference from M3 source not run**. No changes to `main`, production deployment, or M2 baseline. Current official CR not available in the user-provided portal state.

## 1. Exact baseline and scope

- Submitted M2 source tag: `submission-a-ui-v2-20261015` -> `439f672`; isolated worktree `tmp/m2-submission`.
- Stage 0.5 frozen synthetic comparison inputs and labels remain fixed at the SHA-256 hashes in `docs/evaluation/mission3/frozen_manifest_v1.json`.
- Previously recorded M2 provider outputs: `docs/evaluation/final_regression_round5_retry2.json` (eight historical cases); `docs/evaluation/mission3/m2_remote_baseline_v1.json` (four newly prepared cases). These are different sets and must **not** be pooled into a single reported baseline percentage.
- Stage 1 was committed at `3a2ad24`, with code fixes for cross-topic negation, cancellation-owner and cancellation-condition false audit, task/request duplicates and explicit unresolved interpretation.
- Stage 2 targets the exact **remaining** gaps identified in that Stage 1 report: H03 missing request + relative time, LC02 missing open alternative but spurious trial proposal; weak per-field evidence guards.

## 2. Implementation (only on M3 branch)

| File | Technique | Scope and guardrail |
|---|---|---|
| `meeting_intelligence/completeness.py` (new) | Source-anchored explicit omission recovery after LLM event extraction. Recognizes a standalone business request and a clearly unselected implementation/provider/library choice; creates `request_made` or `decision/unresolved` with exact `source_ids` only when absent. | **Never** creates accepted `action`, `agreement` or owner. Rejects questions, named instructions, hypotheticals, old minutes and contradictory in-utterance later approval. Does not clone existing source-linked records. |
| `meeting_intelligence/pipeline.py` | Adds recovery only to `llm_api` analysis; attaches global explanation; marks each rule-recovered record as `needs_review`. | No private KB/authority approval. Existing offline baseline is not silently reinterpreted. |
| `meeting_intelligence/verifier.py` | Drops an extra `decision/proposed` *only* if it is a literal echo of the same issue/task, sourced from named direct instruction and independently accepted by named assignee. | Keeps genuine design proposals, separate scopes and customer requests. Requires exact content/issue alignment and later owner acceptance. |
| `meeting_intelligence/verifier.py` | Field-level source checks: invalid source ids; no confirmed decision based on a question/explicit nonselection; unassigned owner denial; speculative due dates not accepted; unsupported numeric condition thresholds cause fail-closed `unverified` on conditional decisions. | Does not claim full semantic NLI/entailment. Positive controls preserve accepted decision, confirmed deadline and supported numeric condition. |
| `meeting_intelligence/auditor.py` | Rejects only archived-style findings that demand putting a **proposed** date into an open decision even though a later cited same-issue `unresolved` event explicitly rejects the suggested dates. | Genuine missed accepted deadlines remain audit findings; every rejection is logged in pipeline warnings. |

### Explicit data provenance and epistemic distinction

A rule-recovered request or open decision is not an authoritative business fact. It keeps a literal source quote, `authority_status='unknown'`, `review_status='needs_review'`, and an explanatory warning. The human review/export policy remains in place. This is **bounded post-extraction recovery** and can miss paraphrases; it is not a general LLM-based semantic second pass.

## 3. Test procedure and outputs

Commands run from M3 branch:
```powershell
python -X utf8 -m unittest discover -s tests -q
node --test tests/review.test.cjs tests/deploy.test.cjs
python -X utf8 scripts/replay_mission3_stage1.py --group eight --out docs/evaluation/mission3/m3_stage2_replay_eight_v3.json
python -X utf8 scripts/replay_mission3_stage1.py --group four --out docs/evaluation/mission3/m3_stage2_replay_four_v3.json
# From tmp/m2-submission:
python -X utf8 scripts/baseline_checkpoint.py --verify
```

- **174/174 Python unit/contract/replay tests PASSED**, verified after all Stage 2 changes on 2026-10-21 (UTC+7).
- **12 Node frontend/export/deployment tests** previously run, passed.
- **27 authored Stage 2 tests** in `tests/test_mission3_stage2.py`, including positive and negative controls for question/real commitment, proposer/independent choice, old minutes, missing requirement, exact-source cases, wrong/true numeric threshold, historical acceptance, source id mismatch, missing owner, relative timing, and fake day proposals.
- M2 baseline checkpoint verified: **19 files unchanged**, historical 8/8 API completion, 5/8 core cases, 4/8 core+audit; verification itself requires no API calls.

## 4. Deterministic comparison — historical eight M2 cases

**Methodology:** The archived M2 event hypotheses and original archived audit findings are fed to **the current M3 code** (including the new bounded recovery pass), without making a new LLM call. This isolates Python changes; it does **not** establish increased independent extraction accuracy. Each replay includes before/after records and provenance.

Final artifact: `docs/evaluation/mission3/m3_stage2_replay_eight_v3.json`. Prior intermediate v1/v2 artifacts remain development records, **not** cherry-picked final outputs.

| Case | Archived M2 | Stage 2 deterministic replay | Status |
|---|---|---|---|
| **H03** | Decision open only; request and relative time missing; two false audit demands to include unselected weekday | **2 records**: request recorded, `due_raw='trước lần thử tiếp theo'`, owner null, plus decision open. Recovered request `needs_review`. **2 historical audit findings -> 0 accepted** due to later explicit nonselection. | Targeted gap recovered in replay |
| **LC02** | CSV requirement + cancelled trial + spurious trial proposal, but replacement choice missing; bad audit on cancellation condition | **3 records**: CSV request recorded, trial action cancelled (historical Dũng, no due), replacement choice **open** and `needs_review`. Spurious trial proposal removed; historical bad audit **1 -> 0**. | Targeted gaps recovered in replay |
| **LC01** | Duplicate active request from assigned then cancelled task | **1 cancelled historical action**, no extra request, no accepted old audit finding | Preserves Stage 1 fix |
| **LC03** | Correct core plus audit demands removing historical Chi | Core preserved; false audit finding **1 -> 0** | Preserves Stage 1 fix |
| **D01** | Correct object-storage decision + provider open | Same two logical records, statuses unchanged | Baseline pass preserved in replay |
| **D03** | Agreed design blocked by legal + issue open | Same two logical records, statuses unchanged | Baseline pass preserved in replay |
| **D04** | Conditional prereqs replaced | Same conditional state maintained | Baseline pass preserved in replay |
| **H01** | Reopened choice; independent Huy assignment | Both statuses and assignments preserved | Baseline pass preserved in replay |

**Important:** These are deterministic records reviewed against **previously seen, assistant-authored labels**. Do **not** rebrand this table as a fresh M3 provider run or as an independent eight-case accuracy improvement.

Four-case replay artifact: `docs/evaluation/mission3/m3_stage2_replay_four_v3.json`. M3-E01, E02, R01 preserve Stage 1 fixes. M3-K01 still lacks the explicit long-term knowledge utility class; this is Stage 3 work.

## 5. Go / No-Go

### Gate for software development: GO
- Targeted H03/LC02 source-grounded recovery works with *archived event hypotheses*.
- New tests explicitly guard speculative weekdays, hypothetical/old statements, unrelated decisions, duplicate proposals, and unsupported assignments.
- Previously successful M2 cases preserve meaningful outcomes in replay.
- No modifications to M2 source worktree, Git tag, Vercel or Render.

### Gate for production and final contest Before/After: NOT YET
- **No new M3 Groq inference on a source-attested M3 backend has been performed.** The current deployed Render endpoint hosts M2. Never label a call to that service as M3.
- Local `LLM_API_KEY` was absent in Stage 0.5; enabling a private key in an isolated M3 runtime is the next requirement for paired fresh inference. Credentials must never enter Git/logs.
- Rules do not resolve implicit ellipsis, noisy ASR, long meetings or all semantic contradictions. Bounded recovery can miss or ambiguously duplicate paraphrased requirements, so all recovered items remain `needs_review`.
- Audit findings rejected for the two date-proposal scenarios are **not** proof that the audit as a whole has high recall. Positive counterexamples are required.
- Independent human semantic evaluation has not yet occurred.
- Personal CR still needs the organizer-assigned text and its own test.
- M3 information utility / knowledge validation is Stage 3 and not yet completed.

## 6. Next action

Complete Stage 3 conservative long-term knowledge classification, then run **fresh, paired M2/M3 LLM evaluation** on unchanged locked data with documented model/config/source provenance. If quota or deployment prevents it, report unavailable evidence rather than inventing a score. Merge M3 to `main` only after CR, regression and release gates; `main` controls Vercel+Render production and must not be updated prematurely.

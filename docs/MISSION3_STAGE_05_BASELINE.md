# Mission 3 — Stage 0.5: reproducible Before/After baseline

**Date:** 2026-10-21 (ICT). **Status:** M2 snapshot, frozen comparison inputs and a fresh deployed-M2 LLM baseline completed. **Mission 3 code/model has NOT been changed or evaluated yet.**

## 1. Exact source recovery and caution
- The **submitted M2 UI/source tag** `submission-a-ui-v2-20261015` points at commit `439f672a3204238100158570ebcf80f0551b85fd`. This exact commit is also available on the GitHub remote.
- Isolated Git worktree: `tmp/m2-submission`. It is detached at the submitted M2 tag, and the main M3 working branch remains `mission3/improvement-20261021`.
- Historical core benchmark label: `baseline-a-20261014` (source `4aecdc9`). Between these two tags, source in `meeting_intelligence/` is unchanged according to Git diff; the released UI and evaluation scripts differ.
- The worktree is a **byte-reproducible local source**. A separate remote API produced new outputs, but its API does not provide the running git SHA. Accordingly, **the remote results are deployed-M2 results, NOT cryptographically verified exact worktree execution**.
- M2 source unchanged, no source overwrite, no merge into main, no push or deployment in Stage 0.5.

## 2. Frozen dataset and labels **BEFORE fresh M2 calls**
- Transcript-only dataset: `datasets/mission3_before_after_v1.json`.
- Independent file of answer expectations: `datasets/mission3_before_after_labels_v1.json`.
- Frozen SHA-256 manifest: `docs/evaluation/mission3/frozen_manifest_v1.json`.
- Input hash: `d01ea985df426a4e2fc9360056838122d22773a71303fcf3c3b5cc5fe8926852`.
- Label hash: `464045dc9216a93776da6a9b2f1ede667c15fbd5d7c9a86ce5448edb9a12daf6`.
- Four **synthetic, assistant-authored, development comparison** cases: M3-E01, M3-E02, M3-R01, M3-K01. They are **not blind tests, not independently human-annotated and not meeting recordings**.
- The runner passes **ONLY the transcript** to LLM, never the labels.
- M3-CR01 is still **PENDING** official CR assignment, not counted as tested.

## 3. Tests executed
### Mechanics: exact M2 code
`python -X utf8 scripts/run_mission3_comparison.py --version m2 --preflight` -> PASS (correct submitted commit, frozen inputs, four parseable cases).
`python -X utf8 scripts/run_mission3_comparison.py --version m2 --transport offline --call-interval 0` -> 4/4 pipeline invocations COMPLETED, **not LLM performance**; saved `m2_offline_run_v1.json`.

### Real LLM: hosted deployed M2
- Backend: `https://meeting-intelligence-5jk5.onrender.com`; public config responded **200**, `api_configured=true`, model `openai/gpt-oss-120b`.
- Local workspace did **not** have `LLM_API_KEY`. Exact source local + LLM live execution is **not yet achieved**; do not imply otherwise.
- `m2_remote_M3-E02_v1.json` and `m2_remote_remaining_v1.json`: **4/4 completed**, **8 provider calls**, **18,141 tokens** reported in total. Single non-cherry-picked API run per case.
- Combined artifact `docs/evaluation/mission3/m2_remote_baseline_v1.json`; original raw run artifacts remain separately versioned.
- Reviewer judgments `docs/evaluation/mission3/m2_remote_review_v1.json` are **internal assistant semantic review**, not independent labels.

## 4. Fresh deployed-M2 results on FOUR newly locked cases

| Case | Correct required core records | Core case | Full case (no false warning/audit and adequate evidence) | Key observation |
|---|---:|---|---|---|
| **M3-E01** — Cancel trial, retain customer request | 2/2 | PASS | FAIL | Requirement and cancelled task correct, but auditor wrongly demands cancellation reason as operative condition; reaffirmation L005 not cited |
| **M3-E02** — Cancel only task | 1/1 | PASS | PASS | One cancelled action, historical Lan retained, no duplicate request |
| **M3-R01** — B agreed/pilot, rollout blocked, vendor open | 2/2 | PASS | FAIL | Two decision states correct, but **verifier** wrongly flags later vendor non-choice as possible negation of earlier architecture choice |
| **M3-K01** — Action, reusable knowledge, uncertain claim, open decision | 1/3 strict | FAIL | FAIL | Action right; knowledge practice extracted but set `unverified`, unverified anecdote flagged; unchosen X/Y is `proposed` rather than `open` and utility classes absent |

**Internal review totals (four-case synthetic suite):**
- Operational completion: **4/4** (100%).
- Strict required core judgments: **6/8**, grouped core cases **3/4**.
- Full clean cases under the locked criteria: **1/4**.
- Observed unsupported audit findings: **1/1** (E01); additionally **1 clearly false deterministic verifier warning** (R01).
- No false *agreed* decision or active task on these cases. This is not evidence the system never fabricates on other transcripts.
- M3-K01 correctly retains the L003 rumor as uncertain; the knowledge practice is present but no explicit `information_utility` for safe long-term reuse.

These are **small development-case judgments**, NOT broad precision/recall or stable model accuracy. Full case FAIL is not identical to core data FAIL; the auditor and verifier are evaluated separately.

## 5. Baseline results inherited from M2 (DIFFERENT historic run)
`docs/FINAL_REGRESSION_RESULTS.md` (eight older development cases): 8/8 completed, 5/8 core cases, 4/8 full cases. The eight-case historical results are **separate evidence** and are NOT combined into a 12-case overall denominator with the four fresh tests.

## 6. Future *After* protocol
1. Stage 1 M3 code is changed **only** on the M3 development branch; keep `tmp/m2-submission` untouched.
2. Run the same frozen dataset/labels for M3 with `python -X utf8 scripts/run_mission3_comparison.py --version m3 --transport local` **after supplying private LLM settings on the user's machine**; this runner pins source hashes. The script explicitly blocks remote M3 runs against the existing M2 backend to prevent mislabeling.
3. Re-evaluate each output using the same semantic rubric; store under **new file paths** and include source SHA, configuration and errors. M3 must not inherit old baseline outputs.
4. Side-by-side score **core correctness, full correctness, false decisions/actions, recall, evidence, unresolved state, knowledge utility, false audit/verifier warnings, completion, tokens**.
5. Since hosted M2 source SHA and some generation settings aren't exposed, a truly like-for-like *local M2 vs local M3* LLM rerun remains preferable when both can use the same key/provider/config; otherwise label comparison as **hosted M2 vs exact-source local M3**, with methodology limitation.
6. Existing prospective N01–N12 remain assistant-labeled internal evaluation data; do not tune on them before an initial sealed evaluation.

## 7. Reproduction commands
```powershell
# From repository root; only once, if worktree missing:
git worktree add --detach tmp/m2-submission submission-a-ui-v2-20261015
git worktree list

python -X utf8 scripts/run_mission3_comparison.py --version m2 --preflight
python -X utf8 scripts/run_mission3_comparison.py --version m2 --transport offline --call-interval 0
python -X utf8 scripts/summarize_mission3_runs.py docs/evaluation/mission3/m2_remote_M3-E02_v1.json docs/evaluation/mission3/m2_remote_remaining_v1.json
python -X utf8 scripts/merge_mission3_baseline.py
python -X utf8 -m unittest discover -s tests -q
```

If running a **new local real-LLM** M2 run: configure `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL` privately in the process environment; match the old generation settings. Never save credentials in artifacts or Git.

## 8. Stage 1 engineering priorities proven by the new baseline
1. **Verifier cross-issue late negation**: E01/R01 demonstrate where source exists but the wrong logical relation is inferred.
2. **Auditor false positives**: E01 wrongly turns cancellation reason into operative condition.
3. **Unresolved-vs-proposed**: M3-K01 needs explicit no-choice semantics.
4. **Knowledge utility**: separate reusable candidate from unverified assertion without claiming company-approved knowledge.
5. Preserve M3-E02: fixing broad task/request guards must not delete valid work or create a request duplicate.

No Mission 3 Before/After improvement has yet been measured. This document is the **BEFORE** evidence to compare against future M3 results.

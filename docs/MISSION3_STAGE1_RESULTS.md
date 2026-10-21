# Mission 3 — Stage 1: bounded lifecycle and false-commitment repair

**Execution date:** 2026-10-21 (ICT). **Branch:** `mission3/improvement-20261021`.
**Status: code changes implemented and deterministic regression/replay completed; fresh M3 LLM API evaluation NOT RUN**. No production deployment, no merge to `main`, no overwrite of M2 snapshot.

## 1. Inputs locked before changes
- Immutable M2 source: `submission-a-ui-v2-20261015` / `439f672`, available in `tmp/m2-submission`.
- Frozen synthetic M3 comparison: `datasets/mission3_before_after_v1.json`, `datasets/mission3_before_after_labels_v1.json`, hashes in `docs/evaluation/mission3/frozen_manifest_v1.json`.
- M2 fresh *hosted* API baseline: `docs/evaluation/mission3/m2_remote_baseline_v1.json` (4/4 completed, 8 calls, 18,141 provider tokens); **remote service does not attest its source Git SHA**.
- Eight older M2 fixed regression outputs: `docs/evaluation/final_regression_round5_retry2.json` (8/8 completed, 5/8 core, 4/8 strict under M2 review). Different test runs; do NOT merge denominators.

## 2. Changes (all on M3 branch)
| Module | Narrow implementation change | Rationale |
|---|---|---|
| `meeting_intelligence/verifier.py` | Late negation only warns when source explicitly references same decision topic/option, not any later `chưa chốt` utterance | M3-R01: vendor unselected must not un-chose the previously agreed architecture/pilot |
| `meeting_intelligence/verifier.py` + `pipeline.py` | Suppress a provable same-issue, same-content duplicate request whose only origin was a named direct instruction, subsequently accepted by assigned owner then cancelled; log its source in pipeline warnings | LC01: old task echo must not become an independent active requirement; source-backed customer requirement and reaffirmation remain intact |
| `meeting_intelligence/auditor.py` | Strictly reject two invalid *audit hypotheses*: cancellation reason treated as operative condition, and cancelled task falsely required to erase historically evidenced owner; only when structural/source guard supports exclusion | LC02/LC03/M3-E01: audit findings are hypotheses, and historical owner/causal reason have different meanings |
| `meeting_intelligence/extractor.py` | Resolve a model-`proposal` event to `unresolved` only when both its value and cited text explicitly say `chưa chọn/chốt/quyết định`; revise extractor prompt | M3-K01: no final library chosen despite a proposed future benchmark |

**Intentional design choice:** do NOT auto-delete ambiguous request/action overlaps. The duplicate-removal rule is deliberately narrow; uncertain cases remain available for human review. Audit's legitimate active-decision, missing cancellation, or explicit owner-clearing findings are not suppressed.

## 3. Newly added tests
`tests/test_mission3_stage1.py` contains **18 tests**, including:
- True same-topic late negation vs unrelated-topic negation and other named alternatives.
- Two false audit patterns, and positive controls for actual missing cancel / missing reopen / explicit owner clear.
- Explicit no-choice vs a genuine proposal and a model-only unverified claim.
- Historical LC01 duplicate request suppression, plus independent customer request and reaffirmation survival.
- **Replay of saved M2 event hypotheses** on M3-E01/E02/R01/K01.

### Command results
- `python -X utf8 -m unittest discover -s tests -q` → **147/147 OK**.
- `node --test tests/review.test.cjs tests/deploy.test.cjs` → **exit 0**, frontend/export/deploy tests passed (all included subtests).
- From original M2 worktree: `python -X utf8 scripts/baseline_checkpoint.py --verify` → **Baseline A verified, 19 files; 8/8 completed, 4/8 strict, 5/8 core**.
- Frozen M3 harness `--version m3 --preflight` → **OK** (but this is NOT an API model test).

## 4. Deterministic Before → After on identical *archived events*

**Mechanism:** `scripts/replay_mission3_stage1.py` reads events and accepted audit findings saved by M2, then runs them through current M3 extraction validation + resolver + verifier + audit handling. No new LLM sampling; no new information can be extracted when the archived event list omits it. This isolates software changes from stochastic model changes.

Final artifacts for THIS code snapshot:
- `docs/evaluation/mission3/m3_stage1_replay_eight_v3.json` — 8 older M2 cases.
- `docs/evaluation/mission3/m3_stage1_replay_four_v3.json` — 4 newly predeclared M3 cases.
- Earlier v1/v2 replay artifacts preserved as development history; **do not cherry-pick** per-case snapshots.

### Eight historical regression cases
| Case | M2 historical issue | Stage 1 event-replay observation | Remaining limitation |
|---|---|---|---|
| D01 | PASS | Decision agreed and provider open preserved, same two records; no new audit | Still needs fresh M3 run |
| D03 | PASS | Agreed/blocked choice and issue open preserved | Still needs fresh M3 run |
| D04 | PASS | Compound conditional decision retained | Still needs fresh M3 run |
| H01 | PASS | Reopened decision + independent action retained | Still needs fresh M3 run |
| LC01 | FAIL: request echo | **2 records → 1**; duplicate request excluded, cancelled task retained; one old request finding no longer applicable | Must verify LLM extraction and independent-requirement edge cases |
| LC02 | FAIL: replacement missing; audit false alert | Incorrect cancellation-condition audit **1 → 0**; request and cancelled action remain | Replacement open choice STILL MISSING; historical proposal remains |
| LC03 | Core PASS; audit false owner warning | Audit false warning **1 → 0**; historical Chi remains, all three records retained | Need fresh M3 sampling |
| H03 | FAIL: required request missing | No repaired omission; old two audit findings remain | Missing request/relative bound still open |

Do not score this as a fresh eight-case M3 LLM accuracy run. Replay only establishes how the new deterministic code treats exactly the prior M2 events.

### Four fresh-M2-baselined development cases
| Case | Archived M2 events replayed through M3 | Notes |
|---|---|---|
| M3-E01 | 2 records preserved; false cancellation-reason audit **1 → 0** | Request reaffirmation L005 still not included as source evidence |
| M3-E02 | Previously correct cancelled action preserved | Prevent regression |
| M3-R01 | Architecture choice stays agreed/blocked; vendor stays open; wrong later-negation warning removed | Correctly separates issues by source |
| M3-K01 | Choice previously `proposed` now `open` | Knowledge remains `unverified`; long-term utility labeling not implemented (planned Stage 3) |

## 5. Go / No-Go decision

**Software/replay gate:** GO for continuing development.
- New Stage1 tests: PASS.
- Preexisting Python tests: PASS.
- Old M2 tag and worktree: verified untouched.
- No evidence of a regression in the four previously passing *archived event hypothesis* cases.

**Fresh LLM evidence gate:** PENDING. Local workspace previously had no `LLM_API_KEY`, while the public Render backend hosts **M2**, not M3. Calling that endpoint and labeling results M3 would be misleading. Do not merge/deploy or assert measured overall superiority until M3 is tested using code-attested source and real inference, or until limitations and risks are handled.

**Unresolved risks:**
1. Lexical topic matching can miss implicit paraphrased late changes or flag two closely related issues; not a complete semantic entailment checker.
2. Strict duplicate suppression might not recognize a differently worded task echo, and cannot adjudicate ambiguous mixed business requirement statements.
3. Historical fixed outputs omit the request (H03) and choice (LC02): downstream validation cannot recover missing events by itself.
4. Evidence still needs per-field semantic grounding, and knowledge utility/current-vs-long-term classification is not yet built.
5. CR not assigned as of the last user-provided Portal text; no CR test can be legitimately claimed complete.

## 6. Next recommended work
- Stage 2: semantic evidence and positive/negative audit controls, plus robustness for omissions (H03, LC02) with development tests.
- Stage 3: explicit `current_work` / `reusable_candidate` / `historical_context` / `needs_verification` information utility with human approval before publishing knowledge.
- M3 live experiment: use configured private credentials on a staged/local M3 backend (never steal a Render secret or call existing M2 endpoint as M3), save raw artifacts and pair them to fixed M2 baseline.
- Actual Change Request when officially assigned; new CR test is compulsory.
- Release only after representative fresh regression and BEFORE/AFTER checks; `main` / Vercel / Render currently unchanged.

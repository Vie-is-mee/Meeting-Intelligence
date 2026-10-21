# Mission 3 — Stage 3: Knowledge Validation & Information Utility

**Execution:** 21 October 2026, ICT. **Branch:** `mission3/improvement-20261021`.
**Status:** Stage 3 implemented and checked with deterministic software tests / archived M2 event replay. **No fresh M3 live LLM inference was run.** M2 tag, `main`, Vercel and Render production remain unchanged.

## 1. Why this change addresses the task

The Mission 2 schema already had `kind="knowledge"`, but it labelled all extracted knowledge `meeting_status="unverified"`, without distinguishing whether a statement is useful as a long-term candidate or is an unsupported anecdote, and without separating knowledge from current work or historical cancellations.

Stage 3 adds **information utility, NOT truth certification**, as a conservative deterministic post-audit step:
- `current_work` — work requirements, active or open decisions, unresolved issues or feedback to follow up.
- `reusable_candidate` — a concrete source-backed technical/process practice **worth checking for long-term reuse**. This is not an established fact or organizational policy.
- `historical_context` — cancelled/withdrawn/resolved workflow, or past-only statements not endorsed as ongoing guidance.
- `needs_verification` — hearsay, unbenchmarked claim, hypothesis, unsupported/inconsistent source, or unclear status.

The crucial distinction is between **meeting_status** (what participants said or whether work remains active), **information_utility** (possible use after the meeting), **review_status** (human follow-up) and **authority_status** (independent organizational approval). No one field is allowed to silently imply another.

## 2. Implementation

| File | Change | Safety |
|---|---|---|
| `meeting_intelligence/models.py` | Adds optional `information_utility` typed enum + optional `information_utility_note` to `ResultRecord`. | Optional `None` preserves validation of older M2 saved outputs. Event extraction schema is unchanged. |
| `meeting_intelligence/information_utility.py` | New bounded utility classifier after the audit; requires actual source IDs and looks for specific practical guidance, explicit uncertainty, old minutes and later closely related counter-source. Adds `field_evidence_ids.information_utility` and counterevidence where explicit. | Not semantic entailment; cannot independently verify technical truth. Missing/unverified knowledge falls back to `needs_verification`; historical records not promoted to active rules. |
| `meeting_intelligence/pipeline.py` | Applies classifier after extractor/resolver/verifier/auditor, so late status changes affect utility. | Leaves original issue grouping, task states, and event extraction unchanged. |
| `frontend/app.js` | Displays utility label and explanation on record cards/details, with source trace and explicit distinction from organizational approval. | Old saved M2 records lacking field continue rendering normally; no automated KB publishing. |
| `frontend/review.js` | Keeps AI-derived utility as **`ai_information_utility`** / `ai_utility_note` in human-reviewed JSON/CSV exports, while retaining `authority_status="unknown"`. Nulls the derived utility if a reviewer changes the record kind. | Human record confirmation never becomes organization-level knowledge verification; original AI output is preserved. |
| `tests/test_mission3_stage3.py`, `tests/review.test.cjs` | Positive/negative controls for uncertain source, prior minutes, candidate practice, counterevidence, regression, export and compatibility. | Prevents re-labelling rumors or legacy policies as verified knowledge. |
| `scripts/replay_mission3_stage1.py` | Enhanced replay artifact serializer to preserve utility, note, approval, counterevidence and source IDs. | Earlier replay artifacts remain immutable; final Stage 3 artifacts have unique `v2` paths. |

### Hard product rule

Every machine-extracted knowledge item stays `meeting_status="unverified"`, `review_status="needs_review"` and `authority_status="unknown"`. A `reusable_candidate` is **NOT a claim that the process is true**, and users cannot mistake it for a verified organizational policy.

## 3. Tested behavior, not hypothetical expectations

### Previously locked four-case M3 dataset (real M2 events, replayed through deterministic M3 code)

Final artifact: `docs/evaluation/mission3/m3_stage3_replay_four_v2.json`.

| Case | Input/knowledge role | M2 archived records | Stage 3 replay records |
|---|---|---|---|
| **M3-E01** | Customer CSV request + cancelled trial | Request + action | `current_work` for retained request; `historical_context` for cancelled trial. Exact status preserved. |
| **M3-E02** | Cancelled internal task | Cancelled action | `historical_context`; no independent request invented. |
| **M3-R01** | B agreed for pilot, rollout blocked; vendor unchosen | Agreed/blocked decision and open vendor choice | Both `current_work` (one current choice, one unresolved question); source IDs include blocking and no-vendor decision. |
| **M3-K01** | Assigned load test + technical retry advice + unverified library-speed claim + no chosen library | 4 records, two of them knowledge with unverified status | Load test `current_work`, idempotency key **`reusable_candidate`** (`L002`), unbenchmarked speed claim **`needs_verification`** (`L003`), library choice `current_work/open` (`L004`). |

For the two knowledge records in M3-K01, `meeting_status` remains `unverified`, `review_status` is `needs_review`, and `authority_status` is `unknown`.

**This is an additional utility-label behavior test on archived model events, not a newly generated M3 LLM accuracy score.** The assistant-authored M3-K01 synthetic test is development data and has not been independently human-annotated. Older M2 outputs did not have this optional utility field at all; do not compute a superficial “100% M3 improvement” by penalizing M2 on a field it was never designed to emit.

### Previously frozen eight-case M2 regression replay

Final artifact: `docs/evaluation/mission3/m3_stage3_replay_eight_v2.json`. Same replayed core counts and status behavior as Stage 2:
- H03: added source-linked missing request; due `trước lần thử tiếp theo`, no invented owner, marked review.
- LC02: request + cancelled trial + open implementation choice, no extra proposal.
- LC01 and LC03: prior Stage 1 fixes preserved.
- D01/D03/D04/H01: previously correct core histories preserved in this archived-event replay.
- No new LLM extraction was attempted.

## 4. Tests actually executed

| Command / suite | Observed |
|---|---|
| `python -X utf8 -m unittest discover -s tests -q` | **197/197 tests OK** |
| `python -X utf8 -m unittest discover -s tests -p test_mission3_stage3.py -v` | **22/22 Stage 3 tests OK** before final provenance test; **23 Stage 3 tests included in the full 197** |
| `node --test tests/review.test.cjs tests/deploy.test.cjs` | **13/13 passed** |
| `node --check frontend/app.js` | **Passed** |
| `python -X utf8 scripts/baseline_checkpoint.py --verify` from detached M2 worktree | **Baseline A manifest verified: 19 files unchanged** |
| Stage 3 four + eight case event replay | **4/4 and 8/8 executed**, zero new provider calls |
| Frozen M3 comparison preflight | **OK**, frozen input and label SHA-256 intact |

The 197 tests are tests of code contracts, deterministic behavior, and replays — **not** a measured model precision figure.

## 5. Source-control, baseline and remaining gaps

- Historical baseline is `submission-a-ui-v2-20261015` / `439f672` (local detached worktree `tmp/m2-submission`).
- Stage 2 commit: `086fee0`. Stage 3 is developed on the M3 branch only; no changes to `main` or production at this point.
- Old M2 live baseline still preserved in `docs/evaluation/mission3/m2_remote_baseline_v1.json`, with accurate caveat that Render did not attest deployed source SHA.
- M3-K01 knowledge improvement is **purpose labelling**, not a newly learned model or a new independently validated KB.
- Lexical practice / uncertainty detection is deliberately conservative; it can miss paraphrases, distinguish poorly phrased advice imperfectly, and fail to connect implicit corrections. All AI knowledge is explicitly sent to human review.

## 6. Go / No-Go

**GO to the next engineering and evaluation phase:** software tests pass, archived M2 state regressions are preserved in replay, no evidence of broken old source/export. The key new requirement — separating current work, reusable candidate knowledge, historical context, uncertain knowledge — now has a documented implementation and reproducible positive/negative tests.

**NOT YET GO to merge into `main`:** do not claim that M3 beats M2 on real sampled Groq outputs until a **fresh M3 LLM run from an attested M3 source** and paired before/after scoring are performed. The previously deployed Render API still points at M2. Stage 0.5 found no local `LLM_API_KEY`; set private credentials in a dedicated M3 runtime (never commit secrets or upload keys). Also verify the actual official Change Request, remaining long/noisy transcript handling and release packaging.

**Next priority, with the 23 October 2026 11:49 ICT deadline:** source-attested fresh LLM comparison + official CR as soon as assigned, then bounded transcript stress checks and release/demo. Avoid large feature expansions before the evaluation and submission gates.

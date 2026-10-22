# Mission 3 — Official Change Request C2: Exact-source Before/After

**Date:** 23 October 2026 (ICT). **Requirement:** In a meeting with the utterance *"Cái này team mình xử lý nhé"*, do not invent an individual owner or deadline. Do not rebuild the Mission 2 MVP.

## Decision and implementation

**P0 selected:** Source-grounded handling of ambiguous collective commitments rather than new agents, retraining, a large knowledge base, or UI polish.

1. Extractor distinguishes collective intent from explicit personal acceptance; it must not infer a person merely from speaker metadata.
2. `meeting_intelligence/ambiguity.py` demotes false assignment and false agreed/proposed decision claims on a **bare** collective phrase, preserves the literal phrase as `action/unverified` needing human review when unresolved, and refrains from duplicating it when a later accepted named action is clearly about the same topic. Ambiguous connections fail conservatively to a reviewable record.
3. Resolver clears an existing due date when the cancellation **literally** says `bỏ hạn`, even if the model omitted `clear_fields`. Historical owner is retained unless responsibility itself was withdrawn.
4. Verifier preserves explicit `trước` when the due-field's cited utterance says `trước thứ Sáu` but the model drops that qualifier.
5. Auditor's narrow guards reject a fabricated demand to copy an assigned action's owner/deadline into a separate open issue, but leave actual issue resolution or missing assignment to be reviewed.

### Deterministic tests

- **13** tests in `tests/test_mission3_c2.py`: C2 request, edge case, positive control, regression, false-decision, missing-intent recovery, owner/deadline guard, historical owner, "not removing deadline", unrelated later assignment, preserving strict temporal `trước`, and counterexamples.
- **3** tests in `tests/test_mission3_c2_audit.py`: replay of real Groq false audit with negative controls for a resolved issue, absent owner, unrelated issue/source.
- **249/249 Python tests PASS**, **13/13 frontend Node tests PASS** after the last code change. Tests are software contracts, NOT provider accuracy.

## Controlled real-Groq comparison

Two source-pinned local implementations; identical **four fixed transcripts** from `datasets/mission3_c2_v1.json` (SHA-256 `56c71f270cd3664c2d8fa75df64bdc01e5f6dd6e56a3a0e2973b1be3321cd182`). Gold/expected behavior is in that fixture; no expected labels were sent to the provider.

| Setting | M2 submitted Before | Final M3 After |
|---|---|---|
| Source | `439f672a3204238100158570ebcf80f0551b85fd` | `68cfbb0b74f3b92c3ede624cf3e95028ab69ab28` |
| Transport | Local direct Groq, exact M2 tag worktree | Local direct Groq, M3 branch |
| Model | `openai/gpt-oss-120b` | `openai/gpt-oss-120b` |
| Generation settings | temperature 0.6, reasoning low, extraction budget 2560, structured mode auto, audit enabled | Same |
| Provider calls | 8 total in two two-case files | 8 total in three files |
| Pipeline completion | 4/4 | 4/4 |

No decoding seed was fixed; different provider samples may vary. The cases are assistant-authored development tests, not a blind benchmark.

### Individual cases, actual output

| Case | M2 Before — genuine API | M3 After — genuine API | Grounded interpretation |
|---|---|---|---|
| **C2-01** bare `team mình xử lý` | **decision/proposed** about the team handling it. No owner/due hallucinated | **action/unverified**, review required, original L001 cited, owner:null, due:null; **0 accepted audits** | More faithful speech-act treatment; do NOT claim M2 fabricated owner/deadline because it did not in this sample |
| **C2-02** payment issue + Friday merely suggested + owner/date not settled | Issue/open, **request/recorded** saying complete Friday, decision/open; owner/due empty | Issue/open, decision/open, **action/unverified**, owner:null, due:null; **2 accepted audit findings** about whether the historic Friday proposal deserved a separate record | Avoids promoting a proposed Friday completion into an operative commitment; **NOT full-clean** because audit/extraction disagrees about proposal history |
| **C2-03** subsequent explicit Huy acceptance | Correct action/assigned owner Huy, due `trước thứ Sáu`, but also an agreed **decision** echoing assignment | Correct single action/assigned owner Huy, **due `trước thứ Sáu`**, plus open payment issue, **0 audits**, no extra collective action | Preserves real assignment while removing an unnecessary duplicate decision/task |
| **C2-04** assigned trial later cancelled and `bỏ hạn` | Correct single action/cancelled, historical owner Lan and no deadline | Correct single action/cancelled, historical owner Lan and no deadline, **0 audits** | M3 preserves existing M2 functionality; not a new capability claim |

**Scoring discipline:** 4/4 provider runs completed; 4/4 targeted C2 owner/deadline and action-lifecycle expectations observed in the final sampled runs. **Only 3/4 cases have zero accepted audit findings.** No claim of 100% semantic accuracy, generalized hallucination reduction, or independent holdout superiority.

### Preserved evidence (never overwritten or cherry-picked)

Exact source M2:
- `docs/evaluation/mission3/c2_m2_exact_tag_run1.json` — C2-01/C2-02
- `docs/evaluation/mission3/c2_m2_exact_tag_controls_run1.json` — C2-03/C2-04

M3 development and failures:
- `docs/evaluation/mission3/c2_m3_41477ea_run1.json` — first C2-01/C2-02 run with omitted collective intent
- `docs/evaluation/mission3/c2_m3_89fa6d8_run2.json` — recovered unresolved action
- `docs/evaluation/mission3/c2_m3_89fa6d8_controls_run2.json` — C2-03 duplicate and C2-04 missing deadline removal
- `docs/evaluation/mission3/c2_m3_d655084_controls_run3.json` — fixes those two errors, still had false issue-level audit
- `docs/evaluation/mission3/c2_m3_6b39f83_main_run4.json`, `c2_m3_6b39f83_controls_run4.json` — same-source four-case Groq trial; C2-03 temporal qualifier shortened to `thứ Sáu`

**Final M3 source `68cfbb0`**:
- `docs/evaluation/mission3/c2_m3_68cfbb0_C201_C202_final_run5.json`
- `docs/evaluation/mission3/c2_m3_68cfbb0_C203_final_run5.json`
- `docs/evaluation/mission3/c2_m3_68cfbb0_C204_final_run5.json`

Each raw result includes source Git commit, core module SHA-256 hashes, frozen dataset SHA, model/configuration, per-case output/errors, call counts and provider token usage. No provider secrets.

## Risks, trade-offs and release gate

- Bare collective language is matched by a **narrow surface form**. Paraphrases, ASR mistakes, code-switching, multiple topical referents and long-range pronouns require a more general semantic coreference evaluator.
- An `action/unverified` is **not a formally accepted task**. UI/export or downstream automation must not present it as an assigned commitment until reviewed.
- The two accepted audit warnings on C2-02 should remain visible: retaining historical proposals versus preventing false commitments is an unresolved extraction granularity question. Do not arbitrarily suppress them to improve a score.
- Source IDs locate supporting words, not guaranteed truth. New actual-meeting/user-labelled holdout and manual review are needed.
- **GO** for CR C2 source change, regression and evidence package. **NO-GO for production merge** until frontend/Render source provenance, end-to-end demo, video, three official submission answers and final release checklist are verified. M2 tag/main remain intact.

**Recommended 5-minute demo narrative:** Problem → M2 misclassifies collective statement/deadline suggestion → M3 retains ambiguity without inventing owner/date → explicit Huy accepted assignment survives → old Lan cancellation remains correct → results and visible limitation C2-02.

# Mission 3 — Stage 0: audit, baseline, branch, experimental protocol

Prepared: 2026-10-21 (ICT). Deadline: 2026-10-23 11:49 ICT.
Status: **Stage 0 documentation only; no Mission 3 LLM run, core upgrade, website deployment, or CR acceptance yet**.

## Source of truth and version control
- Repository: https://github.com/Vie-is-mee/Meeting-Intelligence
- M2 shipped line: `main`, observed at `439f672` before Stage 0; demo M2 retains that deployment until a tested release.
- Historical evaluation baseline **A**: `baseline-a-20261014` (documented source commit `4aecdc91f1c526773c7bae0a7dfdebfe5e658d2d`), frozen manifest `docs/evaluation/baseline_a_20261014.json`.
- Local M2 delivery tags: `submission-a-checkpoint-20261015`, `submission-a-ui-checkpoint-20261015`, `submission-a-ui-v2-20261015`.
- Mission 3 working branch: `mission3/improvement-20261021`, created from current `main`. NOT deployed and NOT merged.
- Local candidate `candidate/raw-transcript-v2-20261015`: `98910f6`; **local-only** at Stage 0, do not assume `origin` has it.
- Other candidate refs: B `37cd2ee`, C1 `0fc6561`, C2 `a56c5f0`; these are experimental, not accepted.
- Local dirty content **predates Stage 0** and is preserved: `README.md`, `docs/DEMO_RUNBOOK.md`, `docs/MISSION2_SUBMISSION.md`, untracked `docs/RECORD_NOW.md`, and `.ai-bridge/` journal. Do not reset, switch away blindly, or commit these by accident. Keep `.ai-bridge/` out of public Git history. Stage 0 documents are additive only.

## Verified M2 evidence, not M3 outcome
Final fixed eight-case regression (`docs/FINAL_REGRESSION_RESULTS.md`): pipeline completed **8/8**, core cases **5/8**, core + audit **4/8**. Cases D01/D03/D04/H01 fully pass; H03/LC01/LC02 fail core and LC03 fails audit while core is correct. One historical provider run, one generation per case; **not** production accuracy or independent benchmark.
Historical 24-case assessment (`docs/DATASET_EVALUATION_RESULTS.md`): 20/24 completed, required recall 23/57 including errors, 37/45 supported records, audit 2/10 supported alerts. Different run/split; never merge denominators with eight-case regression.
On `main`, Stage 0 `python -m unittest discover -s tests -q` returned **124 tests OK**; expected test of prospective-data blocking emits argparse usage/error text before the successful suite summary. Unit tests do not demonstrate new LLM accuracy.

## Candidate lessons to reuse selectively
- B1: 7/8 completed; 5/8 full; D01 regression and execution failure.
- B2: 8/8 completed; 4/8 full; LC01/LC03 improved but D01/H01 regressed.
- C2: 4/4 pilot executed; 3/4 core, 1/4 full; source/deadline guards help replay, audit false positives persist, D01 missing provider open. No complete eight-case promotion.
- Raw V1: five raw-specific passes but regression on clean inputs; not released.
- Raw V2: three verified completed cases H03/LC03/D01, remaining requests hit Groq HTTP 429; NOT a full-regression pass.
Do not cherry-pick best case outputs or merge candidates en masse. Examine precise source diffs if reusing a candidate.

## Fixed comparison protocol (set before code edits)
1. Development/diagnosis: historical D/H/LC and eight-case regression; fixing these is allowed but report them as **seen**.
2. Prospective (internal, not independent): frozen `datasets/prospective_eval_v2_frozen.json`, N01–N12. 12 assistant-reviewed synthetic transcripts; no independent human annotation. Avoid opening outputs or tuning on N-cases before first sealed evaluation.
3. M3 added edge/knowledge/regression cases: author transcript and expected before running M3; these are development tests unless separated into a new blind set. CR test is **pending external assignment**.
4. Compare a single labeled candidate B to fixed baseline A. Run same transcript, model, reasoning, token budgets, temperature, extraction/audit settings, and scoring rubric when possible. Record changed parameters separately. Preserve the exact source SHA, prompt SHA, input hash, raw output, error, token/call count, time, and reviewer judgments.
5. Score extraction correctness separately from review safety. `needs_review` does not erase a false extraction. Report false decision/action count, required record recall, final-state correctness, evidence field support, false audit findings, run completion and cost.
6. If old A output is replayed rather than rerun contemporaneously, label it **historical A vs fresh M3**, not a paired fresh run.
7. Any N-case used for debugging must move to development in the registry; no post-hoc gold changes to flatter M3.

## Execution order after Stage 0
S1: narrow source-backed task/request lifecycle repair and independent requirement controls. S2: field-source, temporal and audit positive/negative fixtures. S3: conservative information utility / knowledge-candidate classification. S4 (only if gates allow): raw/noisy/long transcripts without silent truncation. S5: A/M3 comparative run and M3 suite; CR assigned test required when provided. S6: choose release, deploy, review security, video <=5 minutes, submit before 11:49 2026-10-23.
Every change: predeclared expected result -> isolated patch -> unit/replay -> fresh LLM run -> semantic review -> Go/No-Go -> journal.

## Personal Change Request
Portal text supplied by applicant: **"Chưa có Change Request được chỉ định cho bạn."** No CR was provided to this workspace by Stage 0. Do NOT claim CR implemented or insert an invented CR test. Save portal evidence, check official portal and contact organizers if still absent. Reserve M3-CR01 as pending; prioritize real CR immediately upon receipt.

# Mission 3 · Stage 0 — Frozen evaluation protocol and release gates

Date: 2026-10-23 ICT. Development branch: `mission3/improvement-20261021`. Comparison:
- Mission 2 submitted baseline: `439f672a3204238100158570ebcf80f0551b85fd` (`main` / submission tag).
- Mission 3 currently online as of stage start: `e8fe1f1328bb170761dff55f3b70b65c14364f41`. Render service: `meeting-intelligence-m3-staging`; separate from M2. **Do not auto-deploy Stage 1 edits.**
- Dev fixtures frozen: `datasets/mission3_c2_v1.json`, `datasets/meeting_eval_v1.json`, `datasets/mission3_before_after_v1.json`. Do not rewrite gold after reading predictions.
- Additional prospective set: `datasets/prospective_eval_v2_frozen.json` exists (12 cases); it explicitly says `independence_claim=false` and original annotations are `assistant_reviewed`. **Do not promote it to independent human-labelled benchmark.** Human signoff is required to make any human-reviewed claim. Keep uninspected fresh cases genuinely unseen for a final check.
- Existing evaluation tools: `scripts/run_dataset.py` (source SHA, provider usage and input freeze) and `scripts/score_dataset.py` (explicit human semantic review / provenance binding). The provider receives only transcript, never gold.
- Baseline observations: official C2 Groq M2 and M3 both completed 4/4; M2 did NOT fabricate owner/deadline in that sample. C2 M3 passed central owner/due constraints 4/4; C2-02 retained 2 accepted audit findings. D01 final Groq at `190bcbd` missed independent open vendor choice and had false audit; D03/D04/H01 retained key states. H03 archived result includes an extra open decision; K01 has recorded/unverified status discrepancy. **These are known development cases and cannot be used to claim blind generalization.**

## Stage 0 source-locked evaluation categories

| Group | Cases | Intended usage |
|---|---|---|
| CR C2 | C2-01..C2-04 | Mandatory development tests + controls |
| Topic/temporal regression | D01, D03, D04, H01, H03, LC01..LC03 | Diagnose and repair explicit failures; report strict and core checks separately |
| Knowledge regression | M3-K01 | Distinguish knowledge candidate from unverified rumor and task; strict gold still disputed |
| New prospective set | 12 assistant-authored frozen cases | Secondary score after human signoff, NOT a blind independent benchmark |
| Truly unseen samples | Future cases labelled by an independent person before model execution | Only if available; record provenance explicitly |

## Acceptance policy

1. Every patch requires a replay of a real provider failure as an immutable input fixture plus positive and negative deterministic tests. Archive raw provider failures; do not edit them or source-derived gold to make a test pass.
2. Run **all** Python tests, 13 Node review/deploy tests, and frontend syntax before deciding on any core patch.
3. Core measurements (manually reviewed): accepted owner/date errors; distinct decision targets recovered; correct final lifecycle/status; required-record recall; extra unsupported/duplicate records; field evidence validity; auditor false positive/negative; human-review and CSV safe behavior.
4. One run is a single provider sample, not a statistical conclusion. Always state exact commit, model, temperature/reasoning/structured mode/audit, dataset SHA, API calls, completion, and semantic annotation status.
5. Do not accept changes that introduce critical fabricated owner/due/agreed decision or omit confirmed assignments. If uncertain, mark review but also track recall cost.
6. Do not edit M2 `main`, tag, live services, user-owned dirty docs, or publish untested new code. A separate M3 candidate may be deployed only after source-matched regression and deliberate approval.
7. Stage 1 focuses on source-grounded **separate decision targets** even when one utterance contains an agreed choice plus a deferred independent choice. H03 duplicate handling is a related but separate gate; avoid a one-off string match or deleting source-supported distinct topics.
8. Keep the 2026-10-25 11:49 ICT deadline and reserve time for staging UI, ≤5-minute video, three answers, and final form submission.

## Stage 1 GO/NO-GO checklist

- D01 reproducing old failure on the current code and passing on candidate **with the SAME archived event hypotheses**.
- No extra open decision if a vendor choice is already correctly represented, or if vendor choice is actually finalized.
- Negative cases with unrelated topics and within-utterance mixed signals remain conservative/reviewable.
- H03 extra record diagnosed with explicit evidence before suppression; no regression to legitimate distinct decisions.
- Regression suites remain green and any fresh-Groq result has an exact source fingerprint.

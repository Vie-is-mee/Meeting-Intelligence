# Mission 3 Stage 4 — Long multi-topic stress, trade-offs and failure evidence

Date 2026-10-24 ICT. Synthetic, assistant-authored, NOT independent held-out or human-labelled evaluation.

## Dataset
`datasets/mission3_stage4_multitopic_v1.json`, two new multi-topic Vietnamese transcripts:
- LONG01 (20 utterances): storage architecture vs vendor decision, payment error, group intent then Huy acceptance, tentative knowledge, Mai's work blocked/cancelled due to missing quotes.
- LONG02 (18 utterances): synced-data decision reopened, concurrent permission task, group-intent and tentative weekday proposals, independent email review and multiple no-assignee statements.

Frozen Groq raw outputs (`openai/gpt-oss-120b`, same Stage3 source, temperature 0.6, audit on, 2 provider calls per case):
- `docs/evaluation/mission3/m3_stage4_LONG01_run1.json`: COMPLETED, auditor 0 accepted. Correct Huy ownership and due, object-storage agreed, reusable_candidate idempotency. **FAIL/PARTIAL:** Mai work wrongly remains assigned when it was suspended/cancelled, open vendor decision missing, knowledge not externally verified.
- `docs/evaluation/mission3/m3_stage4_LONG02_run1.json`: COMPLETED, 2 audit findings. **FAIL/PARTIAL:** two tentative utterances promoted to recorded requests, plus open/proposed decision overlap; Huy permission work and reopened sync decision preserved.
- These show genuine scope/generalization limits and must NOT be hidden from judges.

## Stage4 guarded repair

Reused `meeting_intelligence/commitment.py` Stage2 approach, widened to `mình có nên` scheduling questions and quoted collective `để team mình xem` intentions when a *later same-topic explicit denial* exists. Required >=2 non-generic topic terms for collective overlap. Never drop a positively confirmed request, explicit requirement, or unrelated topic.

- `tests/test_mission3_stage4_long_stress.py`: 3/3 passed (archived LONG02 Groq-event replay, acknowledged collective request positive control, unrelated denial negative control).
- Full regression: **273/273 Python and 13/13 frontend** tests PASS.
- Fresh Groq `docs/evaluation/mission3/m3_stage4_LONG02_after_guard_run2.json`: COMPLETED, audit on, 1 accepted finding, 5 records. The rejected collective request (L016) is no longer a recorded request and warning names L016 and L017; Huy action remains assigned, sync decision reopened. This fresh sample did not produce the same initial tentative request from L006, so causal effect on that error is verified only through archived Groq event replay, not direct provider before/after with deterministic seed.

## Outstanding limitations and release interpretation

LONG01 task pause/cancel and independent vendor-choice omission are **unfixed** in this general language formulation; treat as known limitations and ensure high-risk unresolved tasks stay gated by human review. LONG02 still has a residual decision/open duplicate and 1 accepted auditor finding.

This is a time-bounded developmental stress run, NOT evidence for general accuracy. Do not cherry-pick the newer favorable Groq output to report clean coverage; preserve both runs and remaining failures.

Next: Stage5 source-locked official C2/regression scorecard, Stage6 Render staging deployment of an accepted commit, live website C2/review/export smoke, actual ≤5-min video and required form answers before hard deadline 2026-10-24 18:00 ICT.

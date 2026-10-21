# M2 vs M3 — Comparison table (prepared before Stage 1)

Read first: [Stage 0.5 baseline report](../../MISSION3_STAGE_05_BASELINE.md). This table is a template, NOT an M3 result. Historical eight-case regression is separate and must not be pooled with four fresh synthetic comparison cases.

| Case | Frozen expected outcome | M2 hosted baseline | M3 candidate (NOT RUN) |
|---|---|---|---|
| M3-E01 | Retain independent CSV request; cancel library X trial | Required core 2/2; audit false positive on cancellation reason; L005 reaffirmation not cited | NOT RUN |
| M3-E02 | One cancelled action; no extra request | Required core 1/1; no false warning | NOT RUN |
| M3-R01 | B agreed pilot; rollout blocked; vendor open | Required core 2/2; **wrong verifier negation warning** for vendor line | NOT RUN |
| M3-K01 | Assigned load test; candidate reusable idempotency knowledge; uncertain performance claim; library selection open | Strict required 1/3; knowledge uncertain/utility unspecified; library choice marked proposed | NOT RUN |

## Candidate release gate

- All M3 results must come from **one candidate**, and all four inputs/labels are frozen at SHA values in `frozen_manifest_v1.json`.
- Compare shared M2/M3 core fields using equal criteria; assess new M3-only `information_utility` separately.
- Report missing required records **and** spurious commitment/records, evidence accuracy, false warnings, completion, cost and settings.
- Negative result remains a result: no cherry-picking or post-run changing the answer key.
- Quote the exact model, version source, fingerprint, run artifact, manual review author and noted confidence limits.
- Only complete once M3 raw run and semantic review artifacts exist. Do not replace NOT RUN with speculative scores.

## Required new tests beyond these four

- At least one new test for the **actual** organizer-assigned Change Request (M3-CR01: currently pending).
- Previous successful D01/D03/D04/H01 regression safeguards, plus H03/LC01/LC02/LC03 attempts.
- Transcript-long/noisy scenario when practical, and independent validation before production claims.

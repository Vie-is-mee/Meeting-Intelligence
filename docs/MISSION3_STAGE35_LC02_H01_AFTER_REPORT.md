# Stage 3.5 — LC02 and H01 fresh-evidence addendum

**Date:** 22 October 2026 ICT. Mission 3 branch only; production M2 preserved.

## What was actually run

1. Groq source 7e63907, H01/H03/LC01/LC02/LC03: all completed. H01 had zero accepted audit findings. H03 recovered requested email review with relative due, but has two open decisions that might overlap. LC01 and LC03 behaved correctly. LC02 had duplicate issue/request, lost historical Dũng owner, and a false missing-assignment audit.
2. Deterministic narrow repair in commit 2842f8d, with six positive/negative tests and 232 Python tests passing.
3. Fresh Groq after commit 2842f8d, LC02: COMPLETED with exactly three business records — customer CSV request recorded; Dũng action cancelled, historical owner Dũng retained, due null; alternate CSV implementation decision open. Zero accepted audit findings. The model auditor made suggestions filtered by source/kind guards, not evidence of an infallible auditor.
4. Fresh Groq at 2842f8d, D01/H01: both COMPLETED. D01 object storage agreed and vendor open (zero audits). H01 decision reopened and Huy task assigned, **but one false high-severity audit** demanded restoring the old conditional agreement despite L004 reopening.
5. Investigation: H01 old filter wrongly required the later reopen utterance to be cited inside auditor findings. In the failure, the auditor cited only L001; record history still contained L004 reopen. Updated filter uses source-grounded chronological history and prevents suppression when a later re-agreement exists.
6. After H01 deterministic patch: **233/233 Python and 13/13 frontend tests PASS**. New test reproduces this exact audited source-citation pattern; positive controls retain real operative conditions. A new post-patch H01 provider run must still be stored before declaring that fresh case fixed.

## Files

- `m3_fresh_regression_LC02_2842f8d_run1.json` — post-LC02-fix actual Groq output.
- `m3_fresh_regression_D01_H01_2842f8d_run1.json` — D01 correct; H01 audit false-positive persists on first patch.
- `tests/test_mission3_stage35_lc02.py` and `tests/test_mission3_stage35_h01.py` — deterministic error reproductions and counterexamples.
- All historic pre-fix Groq outputs are preserved, never overwritten; see `MISSION3_STAGE35_LIFECYCLE_FOLLOWUP.md`.

## Release decision

**GO** for testing the second H01 fix with live Groq and checking D03/D04. **NO-GO** for `main` merge and production until the source-pinned fresh regression, assigned Change Request, export, UI/backend and submission gates are fulfilled. H03 still has potential duplicate unresolved decisions; K01 has a frozen gold-vs-conservative-unverified-status discrepancy; neither may be silently scored as a strict pass.

## Post-fix H01 — fresh Groq on source 9679067

The separate source-pinned run `docs/evaluation/mission3/m3_fresh_regression_H01_9679067_run2.json` completed using the live provider with two calls. Final records: `decision/reopened`, `action/assigned` with Huy as owner, plus a source-backed `request/recorded` about personal data read access. **Accepted audit findings: 0.** The earlier false demand to restore a condition from before reopening did not recur in this run. The additional request must be reviewed for independent business meaning; zero auditor findings do not establish audit recall.

**Current gate:** key H01 core and LC02 targets pass in these source-specific fresh runs; **overall release still NO-GO** until remaining cases (especially H03/K01 semantics and actual CR), complete source-matched final regression, production/deploy proof and submission are checked.

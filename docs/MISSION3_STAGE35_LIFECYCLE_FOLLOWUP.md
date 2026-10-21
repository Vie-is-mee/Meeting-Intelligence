# Mission 3 — Stage 3.5: H01/H03/LC01/LC02/LC03 evaluation, LC02 narrow repair

**Time:** 22/10/2026 (ICT); branch `mission3/improvement-20261021`. This report separates real Groq evidence from code-only replay and subsequent live verification. No production deployment.

## Real Groq evidence before LC02 repair (source 7e63907)

| Case | Provider status | Observed outcome | Verdict |
|---|---|---|---|
| H01 | COMPLETED | Reopened decision, independent assigned task for Huy, open issue about access rights; **0 audit findings** | Main regression core preserved; prior stale-condition audit no longer appears |
| H03 | COMPLETED | Review-email request with due `trước lần thử tiếp theo`, no invented owner; two open decisions describing date choice and assignment | Extraction improved, but possible conceptual duplication requires manual adjudication |
| LC01 | COMPLETED | Exactly one cancelled action, historical owner Mai, deadline cleared; no cloned request; 0 audits | Meets key target in this run |
| LC03 | COMPLETED | Agreed internal pilot, independent back-button request, cancelled guide task with historical owner Chi; 0 audits | Meets key target in this run |
| LC02 | COMPLETED | Customer CSV requirement plus a near-duplicate issue, open implementation choice, cancelled action but historical owner Dũng erased by model clear_fields; one false missing-assignment audit | **NO-GO; targeted fix required** |

**Sources:** `docs/evaluation/mission3/m3_fresh_regression_H01_7e63907_run1.json`, `m3_fresh_regression_H03_LC01_7e63907_run1.json`, `m3_fresh_regression_LC02_LC03_7e63907_run1.json`. These are real provider results, not replay.

### LC02 root-cause analysis

Transcript:
- L001 Customer demands CSV export, independent of any implementation trial.
- L002 Dũng is named for the library-X trial with tentative/assigned due.
- L003 Dũng accepts the trial.
- L004 The trial is cancelled due to licensing and its **deadline** is removed.
- L005 CSV requirement persists; implementation replacement still unselected, no **new** task assigned.

**Failure A — historical owner erased:** Provider hypothesized `clear_fields=['owner','due_raw']` on cancellation, but L004 explicitly clears deadline, **not owner**. Resolver trusted the owner-clear proposal without source check, turning a past assigned owner into null; retained history still contained Dũng. Correct state: cancelled action, owner historical Dũng, due null; absence of new assignment does not erase the old task's assignee.

**Failure B — duplicate issue + request:** The issue event for L001 omitted the optional word `có` compared with the literal customer demand, so an exact-string conversion guard did not normalize it to a request. Stage 2 recovery generated a second request from the same utterance. Correct: one customer request, not both issue+request. Distinct factual issues must not be deleted.

**Failure C — auditor's missing assignment false positive:** `missing_issue` finding claimed L003 assignment missing although cancelled action's `history` explicitly contained assignment from L003 preceding cancellation from L004. Correct: preserve historical assignment without creating a second active action. Truly new or absent assignments remain reportable.

### Repairs and safeguards (deterministic)

1. `resolver.py` checks explicit owner-release language in the **cancellation's source utterance** before honoring model-proposed owner clear. Keeps due clearing when literal due was removed. Updates internal event history to avoid claiming a nonexistent owner-release; flags human review.
2. `completeness.py` narrows one exact customer-request equivalence: optional `có` directly after `khách hàng yêu cầu`. Requires same source ID + near-literal rest, not broad fuzzy similarity. Negative control retains true independent issue.
3. `auditor.py` filters a **specific** `missing_issue` claim about an old assignment only when the cited source IDs point to an assignment recorded in a **cancelled** action's history, preceding its cancellation. New, different-issue or genuinely missing assignment findings remain.

### Tests and evidence type

Six new positive and negative controls in `tests/test_mission3_stage35_lc02.py`; full Python suite **232/232 PASS** at the repair stage. Replay of the provider's *saved LC02 event hypotheses* now gives the expected **three business records**: customer request recorded, replacement decision open, cancelled trial with owner Dũng and due null, **0 accepted audit findings**. This is **code/replay evidence only**, not a newly sampled model output.

**Fresh provider AFTER repair:** pending as of this pre-run report. The new source revision must be pinned and fresh Groq output saved to a new path; never overwrite the original LC02 failure.

### Remaining gates

- H03: reviewer should judge whether two open decisions about date vs assignment are meaningful separate issues or duplicated outputs. Do not count both blindly as correct.
- Strict M3-K01 gold still diverges on `recorded` vs `unverified` for knowledge; maintain frozen label and explicitly judge the disagreement.
- Run fresh LC02 post-fix, then re-check regression D01/D03/D04/H01; source-changing repair invalidates claims of source-identical follow-up.
- Confirm official individual Change Request status, production deployment provenance, 5-minute demo video and submission. No `main` merge until release gate.

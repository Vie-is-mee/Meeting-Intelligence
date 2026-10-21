# Mission 3 — Pre-registered acceptance / Go–No-Go gates

These are **internal engineering gates**, not an official contest rubric. Defined during Stage 0 before editing M3 AI core.

## Requirements -> source of proof
| Requirement | Implementation/behavior to show | Evidence |
|---|---|---|
| Continue M2 | M3 from M2 branch, history intact; no rewrite | git refs and commit comparison |
| Long and interleaved discussion | Late changes attached to correct issue; no topic leak | M3-L01 and N11/N12 when feasible |
| No false commitments | Proposal/question/old minutes do not become active decision/action; cancellation doesn't generate clone | LC01, LC02, M3-E01/E02, M3-R01 |
| Evidence | Source ID exists **and** supporting text backs each critical field and current state | field-level test / reviewed output |
| Unresolved/ambiguous | Unknown speaker/owner/deadline stays unknown; conditional vs blocked vs reopened distinct | D01/D03/D04/H01, M3-R01 |
| Work vs reusable knowledge | Clear current obligation/history/candidate expertise/unverified claim; no automatically trusted KB entry | M3-K01 |
| Change Request | Actual reviewer/bank change only; one dedicated test | M3-CR01 *pending assignment* |
| Before -> After | Comparable baseline, raw artifacts, per-case delta, limitations | MISSION3_BEFORE_AFTER and evaluation artifacts |
| New tests >=3 | One CR, one edge, one regression; rerun key old tests | test report |
| Submission | same GitHub, M3 demo, <=5-minute video, 3 written answers | portal links and submission confirmation |

## Gates
- **G0 Baseline:** refs/tags confirmed, dirty M2 files preserved, test harness works, datasets partitioned, tests predeclared.
- **G1 No severe regression:** D01/D03/D04/H01 retain correct core behavior; evidence/source not degraded. If any fails, stop and isolate before touching P1.
- **G2 Target improvement:** fewer actual false action/decision errors on **declared** target cases, with no destructive loss of independent requirements. Marking everything `needs_review` is NOT success. Compare false positives AND missing required records.
- **G3 Reliability and scope:** audit controls catch real issues without introducing false alerts as on LC03/H01; knowledge/ambiguity tests pass. CR must pass **if/when officially assigned**, and absence must be disclosed.
- **G4 Release:** full revised tests + old regression evaluated and artifacted; source commit/release clear; frontend/backend healthy; no secrets; exports/review still work; presentation and links validated.

## Scoring rules
- Judge **source-grounded semantics**, not JSON shape alone.
- Required-record matching is one-to-one; correct kind, content, current status, source support, owner/deadline/condition as applicable.
- Wrong kind counts as mismatch; fake decision/action counts as unsupported even with real source ID.
- If the model emits no record on a true required item, count a miss; do not inflate precision with blanks.
- An abstention is desirable only for genuinely undecided, unsupported, hypothetical, or non-business content; retain genuine open questions.
- Record stage-by-stage `pipeline_completed` and `audit_completed` separately from semantic pass/fail.
- `needs_review` is review-safety, not extraction correctness.
- An auditor returning zero findings gets no automatic credit without positive controls; false alerts assessed separately.
- Provider 400/429/timeouts count as operational failures; no speculative semantic judgment on absent output.
- A saved mock/replay verifies code mechanics, **not** an LLM improvement.
- One model generation at nonzero temperature is not enough to claim statistically stable model superiority.
- No preregistered target of 8/8/100% is an observed result.

## Stop / fallback
- If quota constrained: test Python fixtures/replays, preserve failures and disclose no fresh API evidence. Never claim measured LLM gain.
- If new code breaks a previously passed baseline case: revert/narrow that patch in M3; keep A online.
- If CR arrives late: defer raw-transcript/UI polish to satisfy CR + its new test.
- Release the **one** candidate with best documented balanced outcome; do not choose per-case outputs from different branches.

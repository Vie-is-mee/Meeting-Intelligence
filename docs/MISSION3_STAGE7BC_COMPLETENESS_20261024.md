# M3 Stage 7B/C — Multi-topic completeness and paused-state audit consistency

Date: 2026-10-24 (ICT). Branch: mission3/improvement-20261021.
Prechange public M3 release: `7b224987db79b74263e03203c53799bb465e4022`.
M2 `main`, submission tag and hosted services are untouched.

## Exact reason to improve

The first real fresh Groq LONG01 run after Stage 7A preserved Mai's paused work and vendor/open choice, but **omitted a separately stated payment issue (L005)**. A second fresh LONG01 run with the Stage 7B issue guard correctly represented the payment issue but omitted the still-open supplier choice (L011/L020). These are stochastic extraction omissions across multiple related topics, not proof the hybrid core consistently covered all requirements.

## Source-grounded, narrow changes

1. `meeting_intelligence/completeness.py`: recover explicitly reported concrete `issue/open` statements such as L005 ("Có lỗi thanh toán làm khách bị trừ hai lần") only if not already represented by source/equivalent incident; treat as an independent problem even when Huy accepts an action to fix it. Historical, hypothetical, negative, already-reported-resolved and customer-request cases do not trigger; recovery is flagged `needs_review`. Never invent a responsible person or deadline.
2. Also recognize explicit open vendor choice in sentences such as "còn nhà cung cấp chọn ở cuộc họp khác" and end-of-meeting "nhà cung cấp còn mở". If an open or agreed vendor decision already exists, do not duplicate/reopen. The recovery is `decision/open` with source and human-review gate, not a vendor selection or approval.
3. `meeting_intelligence/auditor.py`: `hold_for_review` treats `paused` like other nonactive lifecycle states (`cancelled`, `reopened`): it does **not** destroy an evidenced pause by replacing `meeting_status` with `unverified`, but it retains the high-severity audit finding and requires human review. Active `assigned` claims with critical unsupported evidence still fail closed. The auditor prompt explicitly explains that `execution_status=blocked` may reflect suspended execution and not an approved cancellation.

## Evidence, with failures preserved

- Test-first archived Groq event replay: original Stage 7B extraction misses L005; Stage 7C extraction misses independent vendor choice; both are recovered from exact source without changing the archived LLM event list.
- `tests/test_mission3_stage7b_incident_completeness.py`: 6/6 PASS (2 initial genuine FAIL before fix); `tests/test_mission3_stage7c_vendor_completeness.py`: 5/5 PASS (2 initial FAIL); `tests/test_mission3_stage7bc_pause_audit.py`: 3/3 PASS (1 initial FAIL); these use archived real-provider events/audit findings and negative controls.
- All Python `293/293 PASS`; frontend Node `13/13 PASS` and JS syntax PASS.
- Fresh Groq source-locked run Stage7B: `docs/evaluation/mission3/m3_stage7b_long01_live_run1.json`, completed extraction+audit (2 calls), issue/open L005, action/paused Mai, decision/open vendor **missing**, no accepted audit findings.
- Fresh Groq source-locked run Stage7B+C (before paused-state audit fix): `docs/evaluation/mission3/m3_stage7bc_long01_live_run1.json`, completed extraction+audit (2 calls), issue/open L005, vendor/open, but also a **spurious decision/agreed** repeating Mai's price-table assignment at L013. Auditor incorrectly asserted pause/blocked was unsupported; the high-severity finding demoted the action to unverified. This known archived audit, replayed through the changed fail-closed gate, no longer erases `paused` or hides the finding.
- **No claim of zero semantic errors on LONG01** or a new independent benchmark: the duplicate L013 decision remains a documented failure. All stress cases here are assistant-authored development fixtures, not independent held-out data. Groq is stochastic; old/new fresh runs are not a fixed-seed causal comparison. Causal effects of guards are demonstrated by replaying the SAME archived Groq hypotheses through old versus new code.

## GO / NO-GO

GO to deploy this isolated M3 candidate **only after full software gate, source SHA attestation and live C2 smoke**. M3 stable `7b22498` remains a rollback point; do not modify the Mission 2 deployment. Source quotations identify where a claim came from, not semantic correctness. Human review/export safeguards remain mandatory for unresolved and paused tasks.

**Remaining major user actions before hard deadline 2026-10-24 18:00 ICT:** open M3 public website, inspect source/review/export manually, record and upload actual ≤5-minute video, submit three real links plus answers. No existing tool evidence confirms those actions have occurred.

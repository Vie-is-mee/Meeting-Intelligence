# Stage 1A — Topic-aware deferred-choice recovery: first candidate

Date: 2026-10-23 ICT. Stage 0 frozen protocol at `docs/MISSION3_STAGE0_EVAL_PROTOCOL_20261023.md`.

## Root cause / technical choice

The old `recover_explicit_omissions` used an all-text topic overlap for a deferred choice. In D01, the extractor's **agreed storage choice content** includes “nhà cung cấp để cuộc họp sau chọn”. That incidental phrase can make the unrelated **open vendor decision** look already covered by the storage decision, suppressing an independent `decision/open`.

This candidate checks the deferred decision's **actual topic target**, not every word in another record's explanation. An event already open for the same target still prevents duplicate recovery; a fully agreed decision with the same target is not automatically reopened. This is conservative lexical recovery only, not general semantic disambiguation.

## Test evidence

- Targeted `test_mission3_stage35_d01.py`: **7/7 PASS**, including distinct vendor vs agreed storage with mixed content, same-target agreed negative control, existing open vendor, same-sentence later approval hold for semantic review, and archived provider-event replay.
- Full Python tests: **256/256 PASS**. Frontend Node tests: **13/13 PASS**.
- The new provider attempt `docs/evaluation/mission3/m3_stage1_d01_topic_candidate_run1.json` was started on the candidate source but returned **ERROR / connection closed** after 2 calls. It is **not a completed semantic benchmark** and is preserved; `audit_completed=false`.
- **No fresh Groq PASS is asserted.** Must rerun using a new evidence path after examining remote connectivity/rate limits; review every generated record against D01 gold before acceptance. Do not cherry-pick old successful runs.
- H03 surplus decision issue is **not claimed fixed** by this D01-specific topic-target correction. Stage 1B must address it with positive/negative controls.
- C2 still requires replay on an unchanged code fingerprint and eventual fresh-run smoke.

## Release decision

**GO** to keep the isolated candidate code under M3 branch; **NO-GO** to promote to M3 public staging/main based solely on deterministic tests. Keep deployed M3 `e8fe1f1` until source-attested fresh provider regression gates pass.

## Next technical actions

1. Stage 1B: analyze H03 double-open decision, disambiguate independent vs duplicate unresolved choices, preserve distinct request and assignment.
2. Stage 1C: candidate-versus-baseline D01/H03/D03/D04/H01/LC01-03 source-pinned fresh Groq runs, freeze outputs and adjudicate.
3. Stage 2: generalized C2 paraphrase/owner/deadline positive and negative controls without degrading true assignment recall.

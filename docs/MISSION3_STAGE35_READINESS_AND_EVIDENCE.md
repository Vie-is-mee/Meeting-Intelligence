# Mission 3 — Stage 3.5: Readiness, frozen evidence & live LLM blocker

**Date:** 21 October 2026, ICT. **Branch:** `mission3/improvement-20261021`.
**Status: PARTIALLY COMPLETE.** Live LLM evaluation **NOT RUN**: local Groq credentials/configuration absent. No `main` merge, no production deployment.

## 1. Completed work and exact findings

| Work | Actual result | Evidence |
|---|---|---|
| M3 preflight | PASS; M3 initially pinned to `aa1d3763db0a48e48ba36c53c9ea169743e6e758`, module SHA-256 sealed | Source / software |
| M2 submitted source | PASS; worktree `tmp/m2-submission` matches `submission-a-ui-v2-20261015` / `439f672a3204238100158570ebcf80f0551b85fd` | Source / software |
| Frozen 4-case inputs | PASS; SHA-256 `d01ea985df426a4e2fc9360056838122d22773a71303fcf3c3b5cc5fe8926852` | Data integrity |
| Frozen 4-case labels | PASS; SHA-256 `464045dc9216a93776da6a9b2f1ede667c15fbd5d7c9a86ce5448edb9a12daf6` | Data integrity |
| Prior M2 eight-case checkpoint | PASS; 19 files unchanged, historic 8/8 completed, 5/8 core, 4/8 full | Historic M2 provider results |
| Python suite | **203/203 passed** (197 previous + six Stage 3.5 tests) | Unit/contract, NOT LLM accuracy |
| Frontend suite | **13/13 passed** | UI/software |
| Actual fresh M3 LLM requests | **ZERO — NOT RUN** | Missing private local runtime settings |
| Actual source-matched M2 local LLM requests | **ZERO — NOT RUN** | Missing private local runtime settings |

**Credential check:** The local process reported the presence flags `LLM_API_KEY=false`, `LLM_BASE_URL=false`, `LLM_MODEL=false`, with no local `.env` file. This report only records booleans — **never keys or their contents**. The public Render API hosts M2; using it to claim M3 results would be misleading.

## 2. Evidence artifacts created

- `scripts/stage35_readiness.py` — validates tag, worktree, frozen data and source SHA; inspects **presence of private runtime settings only**, never values. Outputs `READY_NOT_EXECUTED` or an explicit blocker.
- `docs/evaluation/mission3/stage35_readiness_v1.json` — dated source/hash preflight; state `BLOCKED_MISSING_PRIVATE_LLM_SETTINGS`, and `test_type=preflight_only_NO_LLM_CALLS`.
- `scripts/build_stage35_review_packet.py` — side-by-side frozen case packet, always distinguishes hosted-M2 Before vs replay-only M3 code. Optional `--fresh` accepts only a local M3 runner manifest for the same frozen data and marks semantic review pending.
- `docs/evaluation/mission3/stage35_m2_vs_m3_replay_packet_v2.md` — detailed four-case Before M2 and Stage 3 replay with unscored status, source references and manual review questions. v1 retained as intermediate history.
- `tests/test_mission3_stage35.py` — six new tests checking preflight/hashes, replay labeling, strict merging, duplicate/mismatched configuration rejection, and rejection of remote/offline/M2 outputs as *fresh M3*.

### Mechanical observations — replay, NOT fresh accuracy

| Case | Hosted M2 (actual prior provider output) | M3 Stage 3 archived-event replay | Limit |
|---|---|---|---|
| M3-E01 | 2 records / 1 audit finding | 2 records / 0 audit | Wrong cancellation reason/condition finding filtered in replay |
| M3-E02 | 1 record / 0 audit | 1 record / 0 audit | Correct cancellation preserved |
| M3-R01 | 2 records / 0 audit; wrong cross-issue verifier warning | 2 records / 0 audit, cross-issue warning removed | Core states preserved in replay |
| M3-K01 | 4 records, no utility field | 4 records, distinguishes reusable practice from rumor | Purpose classification, not fact checking |

**No overall accuracy/recall gain is implied.** The M2 hosted baseline did not cryptographically attest Render backend commit. All four cases are synthetic and internally labelled. A further adjudication nuance: the frozen M3-K01 label expects `meeting_status=recorded` for practice knowledge while M3 intentionally keeps machine-extracted knowledge `unverified`; do not change the frozen gold post-hoc or count utility correctness as accepted factual correctness.

## 3. How the private LLM run can be unblocked

The user must place a **private Groq API key** in the local project `.env` file, **not in chat, GitHub, README, screenshots or a report**. The project already ignores `.env` in `.gitignore`.

Open a local editor, for example:

```powershell
notepad .env
```

Configure the following **variable names** inside that private file: `LLM_API_KEY` (private key), `LLM_BASE_URL` (Groq OpenAI-compatible API base URL: `https://api.groq.com/openai/v1`), `LLM_MODEL` (`openai/gpt-oss-120b`), `LLM_TEMPERATURE` (0.6), `LLM_REASONING_EFFORT` (low), `LLM_MAX_COMPLETION_TOKENS` (2560), and `LLM_STRUCTURED_OUTPUTS` (auto). Do not write an example key into a tracked file. Audit budget is managed separately in the code (1024).

Then execute from the repository root:

```powershell
python -X utf8 scripts/stage35_readiness.py
python -X utf8 scripts/run_mission3_comparison.py --version m3 --preflight
python -X utf8 scripts/run_mission3_comparison.py --version m3 --transport local --ids M3-E02 --audit on --call-interval 90 --out docs/evaluation/mission3/m3_fresh_E02_v1.json
```

If the small real API probe succeeds and quota is available, run the other three locked cases with fresh output path:

```powershell
python -X utf8 scripts/run_mission3_comparison.py --version m3 --transport local --ids M3-E01 M3-R01 M3-K01 --audit on --call-interval 90 --out docs/evaluation/mission3/m3_fresh_remaining_v1.json
```

The runner pins source hashes, dataset/gold SHA, provider model/settings, raw output/errors, and prevents overwriting incompatible results. For strongest comparability, run `--version m2 --transport local` against the exact submitted worktree using **the same private model configuration**, with different output paths.

The packet builder's optional `--fresh` mode expects **one complete four-case local M3 run file**. We also implemented `scripts/merge_mission3_fresh_runs.py` to merge the single-case probe with the remaining three only when the source commit, module hashes, model/config, frozen inputs/labels and disjoint case IDs match; all errors are retained. It **rejects** remote M2 or offline outputs and refuses to overwrite evidence. It does not perform semantic scoring automatically.

### Strict merge and evidence packet after real runs

When the two genuine local M3 result files above are **complete** (each preserves even any error), produce a single locked four-case M3 After file and then the review packet:

```powershell
python -X utf8 scripts/merge_mission3_fresh_runs.py docs/evaluation/mission3/m3_fresh_E02_v1.json docs/evaluation/mission3/m3_fresh_remaining_v1.json --out docs/evaluation/mission3/m3_fresh_full_v1.json
python -X utf8 scripts/build_stage35_review_packet.py --fresh docs/evaluation/mission3/m3_fresh_full_v1.json --out docs/evaluation/mission3/stage35_fresh_review_packet_v1.md
```

The strict merger aborts on missing case IDs, duplicated cases, mismatched generation settings, different source code hashes, and partial runs. **It never silently selects the better of two generations**. Failed API cases remain failed. Review packet labels every case **NOT SEMANTICALLY REVIEWED** until an explicit manual judgment is written.

## 4. Next engineering decision — GO/NO-GO

- **GO:** engineering preparation, source/frozen data validation, test suites, reviewer packet.
- **NO-GO for fresh LLM claim:** no local credentials, no new M3 sampled provider responses. Stage 3.5 not complete.
- **NO-GO for release:** do not merge `main` or deploy M3 until the fresh model/regression results, actual Change Request, release sanity and source commit checks are complete.
- Deadline recorded in roadmap: **23 October 2026 at 11:49 ICT**. Prioritize a real M3 four-case inference, then D01/D03/D04/H01 regression, then CR and release. Preserve failures and do not cherry-pick favorable generations.

**Next missing input is not another design idea:** a private key/configured Groq runtime. The user should configure it **locally only**. Once configured, the same test harness can run without redesign.

# HANDOFF.md — mute-map

_Last updated: 2026-07-28_

## What was just done
- **M2 start-of-stage brief written and frozen** (2026-07-28, PR #5,
  `docs/M2-BRIEF.md`). It opened with the oracle question M1 owed, and Kyle
  froze all six decisions: **D9 (b)** greedy-span prefix oracle
  (case-insensitive, word-boundary, deterministic string rule on the recorded
  3-token span; first-token recorded beside every cell); **D10 (a)** offline
  M1 re-score as a labelled reanalysis beside the standing numbers; **D11 (a)**
  the shared stratified 12-concept subset (Brazil, Canada, China, Egypt,
  France, Japan, Jupiter, Mars, October, piano, silver, violin); **D12 (b)**
  tier gate cells + width-late-third stride-2 sliding sweep incl. outside-band
  probes; **D13 (a)** primed-only dose at the late third, λ ∈ {0,.25,.5,.75,1};
  **D14** as written (LATE-LOCALIZED gate wording, degeneracy re-freeze
  carrying PR #4's F3, the M1-cell cross-check, verdict precedence).
- Every number in the brief was recomputed this session from the committed
  `results/m1-battery-*.json` and the three Qwen2.5 tokenizers (they agree
  exactly; max bare form = 3 tokens — what makes the offline re-score sound).

## Where things stand
Chain: ~~M0~~ → ~~M1~~ → **M2 (brief frozen; build next)** → M3; S1/S2
stretches optional. Full D9–D14 DECISIONS.md entries land with the M2 code PR,
per the M0/M1 pattern.

## Immediate next move
**Cut M2's code from the frozen brief** (fresh build session):

1. `m1_rescore.py` — D10 (a): pure function of the committed M1 JSONs, no
   model run; emits `results/m1-rescore-*.json` + a REANALYSIS-labelled
   addendum in M1-BRIEF's results; carries PR #4 F5's per-source split.
2. The M2 runner, cut from `m1_battery.py` (never `m0_anchor.py`, which stays
   certified and un-editable): frozen GATE_WORDING first, wrong-arm INVALID,
   `--dry-run`, `--limit` smoke; subset loader; window edits; partial-λ
   operator (new code, generalized read-back, unit-covered); the M1-cell
   cross-check graded before any new cell.
3. PR #4 follow-ups riding along: F4, F5 (in the rescore artifact), F6, F7,
   F11.

Standing constraints unchanged: certified environment = `mps` + torch 2.13.0 +
transformers 5.13.1 (off it: NOT A RESULT); editing `m1_battery.GATE_WORDING`
is forbidden without a full re-run (M2 freezes its *own* wording instead —
D14); adversarial review before any merge.

## Open questions / blockers
- None. The oracle question is resolved (D9b frozen); the build is fully
  specified by `docs/M2-BRIEF.md`.

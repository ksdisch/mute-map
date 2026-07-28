# HANDOFF.md — mute-map

_Last updated: 2026-07-28_

## What was just done
- **M1 built and PASSED** (2026-07-28): frozen 60-concept / 180-item breadth
  battery (`items/m1-battery.json`), runner `m1_battery.py` cut from the
  certified `m0_anchor.py`, cross-subject `m1_verdict.py`, 93 tests green.
  Verdict: **BREADTH-SPECIFIC at 1.5B AND 3B** — control − primed late naming
  +0.656 [+0.517, +0.763] (n = 61) and +0.636 [+0.443, +0.759] (n = 44). 0.5B
  also CI-clean (+0.447 [+0.275, +0.603], n = 38) but never gate-bearing.
  Prevalence 9/11, 6/8, 4/8 concepts with the hard-switch profile, all carrying
  the pre-declared UNDERPOWERED tag. No degeneracy on any gated arm.
- **The instrument re-certified itself on every run**: the 60 reused S4 items
  reproduced the recorded anchors bit-for-bit, 180/180 cells, `concept_mass`
  floats exact, on all three subjects.
- Decisions **D4–D8** written up in `docs/DECISIONS.md`; PR #3 review
  follow-ups F5/F6/F7/F11 landed as brief addenda + frozen gate wording in
  `m1_battery.GATE_WORDING`; PR #2 follow-ups F5/F7/F9/F10/F11 and D8's
  comparator widening landed with tests (mutation-probed).

## Where things stand
Chain: ~~M0~~ → ~~M1~~ → **M2 (localization + dose)** → M3 (specificity
matrix); S1/S2 stretches optional. Results in `results/m1-battery-*.json`.

## Immediate next move
**M2 start-of-stage brief** — but it must open with the question M1 surfaced,
before any M2 design work:

> **The oracle bounds the map.** The primary readout is the greedy *first
> token*, so a concept is only scorable when its bare (no-leading-space)
> spelling is a single token. **26 of the 60 roster words are not** — planets
> and musical instruments gated **0 items on all three subjects**. The
> first-3-greedy texture shows the models often *did* say those words
> (35/142, 54/119, 80/136 of ungated items). M1's gate is unaffected (the
> contrast lives inside the gated set, and the bias runs *against* the claim —
> the control arm is scored too harshly, never the primed arm), but the reach
> of the breadth claim is bounded.

So M2's brief owes a decision on **widening the oracle** (accept the
leading-space form? score the 3-token span?). It is a change to the
measurement, so it goes in a decision *before* a run, never in a results
section — and any re-scoring of M1 under a widened oracle must be published as
a clearly-labelled reanalysis *beside* the pre-committed M1 numbers, which
stand as they are.

Also carried into M2: `m0_anchor.py` remains certified and un-editable; cut new
runners from `m1_battery.py` or `m0_anchor.py`. The pins (torch 2.13.0,
transformers 5.13.1) and the `mps` device are what make the anchor cross-check
gate-bearing — off that stack a run is pre-declared NOT A RESULT.

## Open questions / blockers
- None blocking. The oracle question above is the first agenda item for M2, not
  a blocker on anything already recorded.

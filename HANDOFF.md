# HANDOFF.md — mute-map

_Last updated: 2026-07-27_

## What was just done
- **M0 complete, gate PASSED** (2026-07-27, same day as kickoff): D1–D3 frozen
  (copy+SHA256 lens provenance, M0-only verbatim port, full bit-for-bit gate);
  environment pinned (`torch==2.13.0`, `transformers==5.13.1` — dim-stage's
  lock); port built (`subject.py`, `intervention.py` subset, `harness.py`,
  `m0_anchor.py`, `m0_port_gate.py`; 23 tests green); anchor re-run ×3 subjects
  reproduced dim-stage's recorded S4b JSONs with **0 mismatches over 840 cells
  each, concept_mass floats exact**. Spine updated (DECISIONS, ROADMAP,
  LEARNING, M0-BRIEF results).

## Where things stand
The instrument is certified. Chain: ~~M0~~ → M1 (breadth battery) → M2
(localization + dose) → M3 (specificity matrix); optional S1 (7B) / S2 (scope)
stretches. Anchor results in `results/anchor-*.json`; logs `anchor-*.log`
(untracked).

## Immediate next move
M1 start-of-stage brief: the ~60-concept battery — category list, item
construction recipe (S4's constrained-construction rules extended), naming-only
competence gate wording, pooled-contrast gate wording. Kyle freezes; then code.

## Open questions / blockers
- None.

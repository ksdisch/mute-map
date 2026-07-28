# PROJECT.md — mute-map

**One-liner:** Map the late-band J-lens output off-switch found in dim-stage S4b —
breadth, localization, dose, specificity — on small local Qwen models.

**Status:** M1 PASSED (2026-07-28) — the late-band off-switch is
**BREADTH-SPECIFIC at 1.5B and 3B** over a 60-concept battery (180 items);
0.5B shows it too, off-gate. M0 PASSED (2026-07-27) and re-certified
bit-for-bit on every M1 run. v1 = M0–M3 per `docs/KICKOFF.md`; S1/S2 stretches
optional.

**Next action:** M2 (localization + dose) — start-of-stage brief first. It
opens with the oracle question M1 surfaced (see below) before any M2 design.

**Key facts**
- Fact — Anchor: S4b (dim-stage), concept-specific off-switch at 1.5B, +.727
  [+.471, +.868] control − primed late naming; specificity emerges with scale.
- Fact — M1 (2026-07-28): control − primed late naming +0.656 [+0.517, +0.763]
  at 1.5B (n = 61) and +0.636 [+0.443, +0.759] at 3B (n = 44); 0.5B +0.447
  [+0.275, +0.603] at n = 38. Prevalence 9/11, 6/8, 4/8 concepts show the
  hard-switch profile — all pre-declared UNDERPOWERED.
- Inference — S4b's 0.5B null looks **underpowered rather than absent**: the
  naming-only gate (K2) took 0.5B from n = 5 to n = 38 and the contrast is
  CI-clean. The lineage's "specificity emerges by scale" story weakens.
- Unresolved — **The oracle bounds the map.** 26 of 60 roster words are
  multi-token in bare form, so the greedy-first-token readout can score them
  only on the runs where the model happens to emit the leading-space form —
  which it rarely does (those 26 contribute 1, 2 and 1 gated items at
  0.5B/1.5B/3B); planets and musical instruments gate 0 items on all three.
  M1's breadth claim holds over the vocabulary the readout can see. Widening
  the oracle is a decision owed at M2, and any M1 re-scoring under it must be
  reported as a labelled reanalysis beside the pre-committed numbers.
- Decision — K1–K4 at kickoff: slug/visibility, naming-only competence gate,
  lens provenance (no refits in core), stats ruler ported verbatim.
- Fact — Lens artifacts gitignored (70–560MB); sourced from local dim-stage
  copies with SHA256 recorded at M0.

**Wiki:** created on first need. Decisions log: `docs/DECISIONS.md` (starts at M0).

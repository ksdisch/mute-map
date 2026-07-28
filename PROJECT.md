# PROJECT.md — mute-map

**One-liner:** Map the late-band J-lens output off-switch found in dim-stage S4b —
breadth, localization, dose, specificity — on small local Qwen models.

**Status:** M2 PASSED (2026-07-28) — the off-switch is **LATE-LOCALIZED at 1.5B
and 3B**: removing the concept direction at the late third mutes the word, while
the same removal at the early or middle third leaves most naming intact. M1
PASSED (2026-07-28, BREADTH-SPECIFIC at 1.5B and 3B) and M0 PASSED (2026-07-27);
both are re-certified bit-for-bit on every later run. v1 = M0–M3 per
`docs/KICKOFF.md`; S1/S2 stretches optional.

**Next action:** the M3 start-of-stage brief (`docs/M3-BRIEF.md`) — specificity
matrix, gate = diagonal suppression > off-diagonal collateral, CI-clean at 1.5B
AND 3B. Its first decision: reuse M2's 12-concept subset or re-derive one.

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
- Fact — M2 (2026-07-28): naming under `primed_early` − `primed_late` = +0.853
  [+0.668, +0.936] and `primed_middle` − `primed_late` = +0.794 [+0.603, +0.897]
  at 1.5B (n = 34); +0.750 [+0.531, +0.857] and +0.688 [+0.463, +0.812] at 3B
  (n = 32); 0.5B LATE-LOCALIZED too, off-gate (n = 28). Pre-registered gated ns
  (28/34/32) landed exactly. No degeneracy fired.
- Fact — M2's descriptive map (no gate reads it): windows entirely outside the
  band cost ≈48% of naming at 0.5B but ~0–6% at 3B; the late transition is a
  cliff at 0.5B/1.5B and a ramp at 3B. The dose curve is a **dimmer, not a step
  function**, with the half-mute point at λ ≈ 0.23 / 0.29 / 0.36 by scale.
- Inference — the switch's *sharpness* and its *depth-specificity* both improve
  with scale, while the dose needed to trip it grows. 0.5B reaches the same
  verdict from a much noisier floor, which is what its standing
  any-direction-damage frame predicted.
- Decision — **D9 (b), frozen 2026-07-28 (M2-BRIEF): the oracle widens** to a
  greedy-span prefix rule (case-insensitive, word-boundary, deterministic
  string rule on the recorded 3-token span; first-token recorded beside every
  cell). Resolves M1's owned bound: 26 of 60 roster words are multi-token in
  bare form and planets/instruments gated 0 items everywhere under the
  first-token readout. M1's pre-committed numbers stand; the D10 (a) offline
  re-score **landed** with the M2 code PR as a clearly-labelled reanalysis
  beside them, matching the brief's projection exactly: prefix-gated n 69 (0.5B)
  / 105 (1.5B) / 116 (3B); primed 0/69, 0/105, 12/116; contrast +0.478 / +0.762
  / +0.690. Planets and musical instruments go from 0 gated items on every
  subject to 7/8/15 and 2/8/13 of 18.
- Decision — K1–K4 at kickoff: slug/visibility, naming-only competence gate,
  lens provenance (no refits in core), stats ruler ported verbatim.
- Fact — Lens artifacts gitignored (70–560MB); sourced from local dim-stage
  copies with SHA256 recorded at M0.

**Wiki:** created on first need. Decisions log: `docs/DECISIONS.md` (starts at M0).

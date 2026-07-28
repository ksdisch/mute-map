# PROJECT.md — mute-map

**One-liner:** Map the late-band J-lens output off-switch found in dim-stage S4b —
breadth, localization, dose, specificity — on small local Qwen models.

**Status:** M1 PASSED (2026-07-28) — the late-band off-switch is
**BREADTH-SPECIFIC at 1.5B and 3B** over a 60-concept battery (180 items);
0.5B shows it too, off-gate. M0 PASSED (2026-07-27) and re-certified
bit-for-bit on every M1 run. v1 = M0–M3 per `docs/KICKOFF.md`; S1/S2 stretches
optional.

**Next action:** M2 build (fresh session): `m1_rescore.py` (the D10a labelled
reanalysis) + the M2 runner cut from `m1_battery.py`, both per the frozen
`docs/M2-BRIEF.md` (D9–D14 frozen 2026-07-28, PR #5).

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
- Decision — **D9 (b), frozen 2026-07-28 (M2-BRIEF): the oracle widens** to a
  greedy-span prefix rule (case-insensitive, word-boundary, deterministic
  string rule on the recorded 3-token span; first-token recorded beside every
  cell). Resolves M1's owned bound: 26 of 60 roster words are multi-token in
  bare form and planets/instruments gated 0 items everywhere under the
  first-token readout. M1's pre-committed numbers stand; the D10 (a) offline
  re-score lands with the M2 code PR as a clearly-labelled reanalysis beside
  them (design projection: prefix-gated n 69 (0.5B) / 105 (1.5B) / 116 (3B);
  primed 0/69, 0/105, 12/116, same order).
- Decision — K1–K4 at kickoff: slug/visibility, naming-only competence gate,
  lens provenance (no refits in core), stats ruler ported verbatim.
- Fact — Lens artifacts gitignored (70–560MB); sourced from local dim-stage
  copies with SHA256 recorded at M0.

**Wiki:** created on first need. Decisions log: `docs/DECISIONS.md` (starts at M0).

# PROJECT.md — mute-map

**One-liner:** Map the late-band J-lens output off-switch found in dim-stage S4b —
breadth, localization, dose, specificity — on small local Qwen models.

**Status:** **v1 chain complete — M3 PASSED (2026-07-28)**, the off-switch is
**MATRIX-SPECIFIC at 1.5B and 3B**: over the full 12 × 12 prime × probe grid,
deleting one concept's direction at the late third silences that concept and
leaves the other eleven almost untouched (1.5B: diagonal 0/34 vs off-diagonal
363/374). M2 PASSED (LATE-LOCALIZED at 1.5B and 3B), M1 PASSED
(BREADTH-SPECIFIC at 1.5B and 3B), M0 PASSED (2026-07-27); all re-certified
bit-for-bit on every later run. v1 = M0–M3 per `docs/KICKOFF.md`. **Close-out
stage M4 (the vocabulary collateral strip) is now in flight** — brief written
and reviewed, **decisions D19–D22 frozen 2026-07-29**, no runner code yet. The
S1/S2 stretches were declined for this repo and banked (idea #13).

**Next action:** build the M4 runner. `docs/M4-BRIEF.md` is written and
adversarially reviewed (PR #10); **D19–D22 were frozen 2026-07-29 — (a) across
the board** — so the next step is code: `m4_strip.py` cut from `m3_matrix.py`,
`m4_verdict.py`, `test_m4.py`, and the D19–D22 entries appended to
`docs/DECISIONS.md` in that same code PR. After M4: write-up + `/seed-hunt`. The S1 (7B) and S2 (lexical vs semantic scope)
stretches were declined for this repo and banked as idea #13 in
`~/Projects/j-lens-proj-ideas/jlens-followon-backlog.md`; they compete in the
seed-hunt on equal terms.

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
- Fact — M3 (2026-07-28): on the 12 × 12 matrix at the late third (λ = 1, k = 1),
  pooled off-diagonal − diagonal naming = **+0.971 [+0.867, +0.983]** at 1.5B
  (diagonal 0/34, off-diagonal 363/374) and **+0.881 [+0.731, +0.943]** at 3B
  (3/32 vs 343/352); the within-category clause is +0.950 and +0.891, likewise
  CI-clean. 0.5B MATRIX-SPECIFIC too, off-gate. Every pre-registered n landed
  exactly; the collateral floor is clear on all three, so no verdict carries the
  ON A DAMAGED FLOOR qualifier.
- Fact — M3's descriptive map (no gate reads it): collateral concentrates on a
  few fragile **probes**, not on damaging **primes** — at 1.5B all 11
  off-diagonal misses land on 4 probes, and `silver`, `Canada`, `China`,
  `Jupiter` and `Mars` cause zero collateral as primes. Category-block collateral
  is CI-clean at 0.5B (cross − within +0.105 [+0.032, +0.196]) and dissolves into
  noise by 1.5B. The only non-zero diagonal cells anywhere are `Egypt` 2/3 and
  `October` 1/2 at 3B — the pre-registered S3 leaky-switch stratum.
- Inference — `silver`'s pre-registered "non-specific" label was a fact about its
  **column** (it is fragile to other deletions), not its **row** (its direction
  damages nothing). M1's and M2's single control cell sampled one cell of that
  column; the matrix is what distinguishes the two readings. A re-attribution,
  not a retraction — M1's and M2's numbers stand as published.
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

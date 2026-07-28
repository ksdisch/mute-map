# PROJECT.md — mute-map

**One-liner:** Map the late-band J-lens output off-switch found in dim-stage S4b —
breadth, localization, dose, specificity — on small local Qwen models.

**Status:** M0 PASSED (2026-07-27) — ported instrument certified bit-for-bit
against dim-stage's recorded S4b results, ×3 subjects. M1 design frozen same
day (`docs/M1-BRIEF.md`, decisions D4–D8). v1 = M0–M3 per `docs/KICKOFF.md`;
S1/S2 stretches optional.

**Next action:** M1 build — freeze `items/m1-battery.json` (D4 roster, D27c
clue rules), cut the M1 runner from `m0_anchor.py`, gates as code + dry-run,
then the three-subject run.

**Key facts**
- Fact — Anchor: S4b (dim-stage), concept-specific off-switch at 1.5B, +.727
  [+.471, +.868] control − primed late naming; specificity emerges with scale.
- Decision — K1–K4 at kickoff: slug/visibility, naming-only competence gate,
  lens provenance (no refits in core), stats ruler ported verbatim.
- Fact — Lens artifacts gitignored (70–560MB); sourced from local dim-stage
  copies with SHA256 recorded at M0.

**Wiki:** created on first need. Decisions log: `docs/DECISIONS.md` (starts at M0).

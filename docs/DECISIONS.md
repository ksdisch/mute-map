# DECISIONS.md — append-only decision log

Kickoff decisions K1–K4 (2026-07-27) are recorded in `KICKOFF.md`; this log
starts with M0 and only ever appends.

## D1 — Lens artifact sourcing: copy + SHA256 (Kyle, 2026-07-27)

The three fitted lens `.pt` files are **copied** from local dim-stage
(commit `e6c10b9`) into `lenses/` (gitignored), with SHA256 fingerprints, source,
and regeneration commands recorded in the tracked `lenses/PROVENANCE.md`.
Rejected: symlinking (breaks if dim-stage moves; blurs provenance) and a
configurable loader path (flexibility K3 already forecloses). The frozen S4b
item set and the three recorded S4b result JSONs are copied under the same
provenance discipline (`items/`, `anchors/`).

**Consequence discovered at freeze time:** dim-stage's lock and a fresh resolve
disagreed on transformers (5.13.1 vs 5.14.1), so mute-map **pins
`torch==2.13.0` + `transformers==5.13.1`** (dim-stage's lock at anchor time) in
`pyproject.toml`. Relaxing the pins is a future DECISIONS entry and re-runs the
anchor gate.

## D2 — Port scope: M0-only, verbatim (Kyle, 2026-07-27)

Ported: `SubjectModel` + `_record_residuals` (→ `subject.py`), the ablation
subset `jlens_vector`/`ablate`/`edit_residuals`/`Edit` (→ `intervention.py`),
and the shared conventions `fail_invalid`/`FROZEN_BANDS`/`proportional_band`/
`token_forms`/`encode_chat`/`output_logits`/`READBACK_TOL`/`MIN_N`/
`COLLAPSE_SHARE`/`degeneracy`/`rate_cell` (→ `harness.py`) — each verbatim from
its dim-stage home, source cited in the module docstrings. The S4b runner is
ported near-verbatim as `m0_anchor.py` (divergences owned in its docstring:
import paths, `items/` and `results/anchor-*` paths, three unused imports
dropped). Steering/swap operators stay behind until a milestone brief needs
them. Rejected: porting the full toolkit now (M0 would certify code no M0 cell
exercises).

## D3 — Anchor gate: full bit-for-bit (Kyle, 2026-07-27)

`m0_port_gate.py`, frozen before any comparison ran: PASS iff every per-item ×
instruction × condition **greedy outcome** (`produced` + decoded `greedy`
token), every per-item `gate_greedy` membership, and the instrument
configuration (band, thirds, item roster, dropped list) match dim-stage's
recorded S4b JSONs with **0 mismatches**, on all three subjects. Any mismatch ⇒
INVALID (exit 2) — investigate; the bar never softens. `concept_mass`
float equality and `gate_verbatim_p` agreement are reported as texture, never
gating. Rejected: gate-level match only (per-item flips could cancel silently).

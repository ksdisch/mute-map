# M0 start-of-stage brief — port + anchor gate

*Start-of-stage brief per the per-stage rhythm: plain-terms explanation first,
design extraction second, decisions third, code only after Kyle freezes.*

## What M0 is, in plain terms

Before mapping anything new, we prove the instrument survived the move. mute-map
inherits three things from dim-stage: the **fitted lenses** (the big matrices that
turn a model's internal activations into per-word directions), the **ablation
operator** (the code that deletes one concept's direction — "projection removal"
means subtracting out exactly the component of the activation that points along
that direction, leaving everything else untouched), and the **S4b protocol** (the
items, prompts, conditions, and grading that produced the off-switch result).

M0 re-runs the S4b experiment inside this repo and demands the numbers come out
**identical** to what dim-stage recorded. Because every readout is deterministic —
greedy decoding means the model always picks its single highest-probability next
token, no randomness — "identical" is a fair bar: dim-stage's own S4b re-run
reproduced every shared cell bit-for-bit. If our port matches, every later
milestone stands on a verified instrument. If it doesn't, the port is broken and
nothing else runs until it's fixed.

## Design extraction (source-cited)

From dim-stage `docs/S4-BRIEF.md` (+ its S4b addendum) and
`s4_avoidance.py` / `intervention.py` / `s4-avoidance-items.json`:

- 60 frozen items (~20 concepts × 3 clue sentences; categories from measured
  vocabularies), naming + avoidance instructions, one user turn through the chat
  template.
- Conditions: clean, primed early/middle/late (k = 1 projection removal of the
  implied concept's J-lens vector at that band third), control early/middle/late
  (same-category alternative's vector). Bands = the S1 sub-band thirds of each
  subject's frozen workspace band.
- Grading: greedy first token vs the concept's single-token form (binary,
  deterministic); concept softmax mass recorded as texture. Competence gate:
  greedy-based (names correctly clean AND avoids correctly clean) → gated
  n = 5 / 22 / 8 at 0.5B / 1.5B / 3B.
- Recorded anchor cells to match (dim-stage `results/s4-avoidance-*.json`,
  superseded-in-place by S4b): gated-cell naming primed_late 0/5, 0/22, 0/8;
  control_late 1/5, 16/22, 8/8; D31 gate 1.5B +.727 [+.471, +.868]
  concept-SPECIFIC; every other cell as recorded.

## Decisions to freeze (Kyle picks; recommendations flagged)

### D1 — Lens artifact sourcing

- **(a) Copy the three `.pt` files into `mute-map/lenses/` (recommended).**
  ~880MB of disk, gitignored. Full independence from dim-stage's working tree;
  a `lenses/PROVENANCE.md` records each file's SHA256 (a cryptographic
  fingerprint — if a byte changes, the fingerprint changes), source path,
  dim-stage fit provenance, and the regeneration command (dim-stage's
  `fitter.py`). *Why:* disk is cheap; a sibling repo silently changing under us
  is exactly the kind of drift the anchor gate exists to catch.
- **(b) Symlink to `../dim-stage/lenses/`.** Zero disk, but breaks if dim-stage
  moves and blurs provenance.
- **(c) Configurable loader path.** Flexibility we have no use for (K3 already
  says no refits in core); violates keep-it-lean.

### D2 — Port scope

- **(a) Port only what M0 needs, verbatim (recommended).** The projection-removal
  operator, band/third definitions, the S4b runner logic, and the frozen item
  file (copied with provenance). Steering, swaps, and the rest of dim-stage's
  toolkit stay behind until a milestone needs them — M2's partial-λ operator is
  a new capability and gets designed in M2's own brief. *Why:* every ported line
  is a line the anchor gate certifies; every extra line is untested freight.
- **(b) Port the full `intervention.py` toolkit now.** Saves later copying,
  but M0 would certify code no M0 cell exercises.

### D3 — Anchor gate wording (pre-committed before any run)

- **(a) Full bit-for-bit (recommended).** PASS iff every recorded cell — per
  item × instruction × condition greedy outcome, all three subjects, plus the
  competence-gate memberships (5 / 22 / 8) — matches dim-stage's recorded JSONs
  with **0 mismatches**. Any mismatch ⇒ M0 INVALID: investigate the port (or an
  environment shift, e.g. a torch version change) until explained; the bar never
  softens to "close enough." *Why:* S4b's own re-run proved this bar achievable
  on this hardware; a deterministic instrument that almost matches is broken.
- **(b) Gate-level match only** (gated ns + verdict cells match). Weaker; would
  let per-item flips cancel out silently.

Standard machinery regardless: wrong-arm input exits INVALID; `--dry-run`
validates and stops; `--limit` is smoke, never a result.

## Deviations table (starter — carried forward all v1)

| Deviation | From | Owned reason |
|---|---|---|
| Model scale 0.5B–3B vs Claude | seed paper | The lineage's standing frame |
| Anchor = our own S4b result, not a paper claim | lineage precedent | First original characterization; framing stated in KICKOFF |
| Lenses copied, never refit (core chain) | — | K3; SHA256 provenance in `lenses/PROVENANCE.md` |
| Naming-only competence gate (M1+, not M0) | S4b's dual gate | Measures the switch, not exclusion capacity; M0 keeps the dual gate for exact anchor comparability |

## Wall-clock plan

Port + tests: a session. The anchor re-run itself: 60 items × 2 instructions ×
7 conditions × 3 subjects, k = 1, forward-only, short prompts — well under an
hour total on MPS (S4b precedent), $0.

## What M0 does NOT decide

- The M1 battery's categories, item recipe, or gate wording (M1's brief).
- The partial-ablation operator or window scheme (M2's brief).
- Anything about 7B (S1 stretch, only if reached).

# HANDOFF.md — mute-map

_Last updated: 2026-07-27_

## What was just done
- **M1 design frozen** (2026-07-27, PR #3): `docs/M1-BRIEF.md` written — design
  extraction + decisions **D4–D8 all frozen by Kyle**: D4(b) 10×6 roster (7
  new-list words, every word single-token-verified), D5(a) 3 clues/concept +
  S4-item reuse with the built-in anchor cross-check, D6(a) item-level greedy
  naming-only gate, D7(a) pooled BREADTH-SPECIFIC wording with
  fixed-denominator prevalence (amended pre-run at PR #3 review F1), D8(a)
  comparator widened to `protocol` + `lens_n_prompts`. PR #2 follow-ups F6
  (status refresh) and F3 (re-certification recipe) landed in the same PR.
- Earlier same day: **M0 complete, gate PASSED** — instrument certified
  bit-for-bit ×3 subjects (see `docs/M0-BRIEF.md` results).

## Where things stand
Instrument certified (M0); M1 design frozen (`docs/M1-BRIEF.md`). Chain:
~~M0~~ → M1 (breadth — design frozen, build next) → M2 (localization + dose) →
M3 (specificity matrix); optional S1/S2 stretches. Anchor results in
`results/anchor-*.json`.

## Immediate next move
Build M1 against the frozen D4–D8: freeze `items/m1-battery.json` (60 reused
S4 items + 120 new clues by the D27c rules, construction_rules block, guards
as code), cut the M1 runner from `m0_anchor.py` (naming-only, 3 conditions),
gates + dry-run INVALID machinery before any real run. Fold in the queued
review follow-ups — from PR #2: F5 dead imports, F7 MIN_N/COLLAPSE_SHARE
dedupe (import from `harness`), F9/F11 test tightening, F10 `load()`
hardening; from PR #3: F5 degeneracy-guard disposition and F7 environment
scoping (both into the runner's pre-committed gate wording), F6 paired-arms
honesty-row sentence. DECISIONS.md entries D4–D8 land with that PR.

## Open questions / blockers
- None.

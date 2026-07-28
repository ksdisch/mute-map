# HANDOFF.md — mute-map

_Last updated: 2026-07-28_

## What was just done

**M2 built, run, and PASSED** (2026-07-28) — localization + dose, per the frozen
`docs/M2-BRIEF.md` (D9–D14). Landed in one PR with its docs spine:

- **`oracle.py`** — D9(b)'s greedy-span prefix rule frozen as code (shared
  byte-for-byte by the reanalysis and the runner, so the two can never diverge).
- **`m1_rescore.py`** — D10(a)'s labelled reanalysis of M1 under the widened
  oracle: a pure function of the committed M1 JSONs, no model run, which
  refuses to write unless it first reproduces M1's *published* first-token
  numbers exactly. Emits `results/m1-rescore-*.json` + a REANALYSIS-labelled
  addendum in M1-BRIEF. Carries PR #4's F5 per-source split under both oracles.
- **`m2_depth.py` + `m2_verdict.py`** — the M2 runner cut from `m1_battery.py`
  (never `m0_anchor.py`), with its own frozen `GATE_WORDING`, the 12-concept
  subset, tier cells, the late-anchored stride-2 window sweep, the new partial-λ
  operator with a generalized read-back, and the M1 cross-check graded before
  any new cell. Plus `test_m2.py` (~100 cases); full suite 187 → green.

**Results: LATE-LOCALIZED at 1.5B AND 3B.** Early−late +0.853 [+0.668, +0.936]
and middle−late +0.794 [+0.603, +0.897] at 1.5B; +0.750 [+0.531, +0.857] and
+0.688 [+0.463, +0.812] at 3B. 0.5B also LATE-LOCALIZED, off-gate, but on a
raised damage floor. The M1 cross-check re-certified the instrument bit-for-bit
on every run (108/108 cells, `concept_mass` exact, ×3 subjects). No degeneracy
fired anywhere. Every pre-registered gated n (28 / 34 / 32) came in exactly.

**The two descriptive findings the gate did not ask for:** the window curve has
a *floor* of depth-nonspecific damage that shrinks with scale (≈48% of naming
lost at 0.5B for windows entirely outside the band, ~0–6% at 3B), with a sharp
late cliff at 0.5B/1.5B that becomes a ramp at 3B; and the dose curve is a
**dimmer, not a step**, with the half-mute point sliding right with scale
(λ ≈ 0.23 / 0.29 / 0.36).

Riding follow-ups all landed: PR #4's F4 (widened `torch.load` except tuple),
F5, F6, F7 (`forbidden_forms` keys validated against the roster), F11; PR #5's
F13 (wall-clock restated 1.3×/1.4×/1.6×), F14 (the span-fill clause replaced by
the inspection-based qualifier — six cells fill the span, truncation cannot rule
out a continuation, so the residual is *owned*, not excluded), and the stale
`# bare form — M1 convention` comment in `m1_battery.py`.

## Where things stand

Chain: ~~M0~~ → ~~M1~~ → ~~M2~~ → **M3 (specificity matrix — brief first)**;
S1/S2 stretches optional. `docs/DECISIONS.md` now runs D1–D14.

## Immediate next move

**Kyle freezes D15–D18.** The M3 start-of-stage brief is written
(`docs/M3-BRIEF.md`, 2026-07-28): plain-terms explanation, design extraction
(KICKOFF M3 scope + S4b D28/D31 verbatim), explicit dispositions for all
three review carry-forwards below (F2 → stated retired in D17's wording;
F5 + F4 → D18's run-time bars), and decisions D15–D18 — D15 recommends
reusing M2's pre-registered 12 verbatim. **No code until Kyle freezes.**
M3's gate per KICKOFF: diagonal suppression > off-diagonal collateral,
CI-clean at 1.5B AND 3B.

**Three carry-forwards, now dispositioned in the M3 brief, from M2's round-1
adversarial review**
(all accepted, all recorded in the PR comment; none blocks the merge):

1. **The tier-width caveat belongs in M3's frozen `GATE_WORDING`** (review F2).
   `sub_band_thirds` gives the late tier the band remainder, so M2's gate
   compared a 4-layer ablation against a 6-layer one at 1.5B — depth *and*
   intervention size differ. M2 owns it in its brief's Honest limits and shows
   the equal-width window cells that retire it, but M2's own wording could not
   be amended post-run (byte-frozen with its artifacts). If M3 uses tiers, its
   wording should say this up front.
2. **Pin the "3 tokens ≥ longest bare form" premise as a run-time bar** (F5).
   It carries D10(a)'s whole soundness argument and no test reproduces it. The
   suggested shape: in the runner's `main()`, where the tokenizer is already
   loaded, require every planned concept's bare form to tokenize to
   ≤ `SPAN_TOKENS` or exit INVALID. This matters the moment M3 touches the
   roster — a 4-token bare form would be silently unscoreable.
3. **Decide the oracle's boundary class if M3 adds non-ASCII vocabulary** (F4).
   `oracle._BOUNDARY` is ASCII-only, so a non-ASCII continuation would score as
   a hit. No live path today; switching to `\w` flips `_` and is a rule change,
   so it needs a decision rather than a fix.

Also carried, non-blocking (F6): `m2_depth.main()` loads the checkpoint before
validating inputs (inherited from `m1_battery.py`, so `--dry-run` and wrong-arm
exits still pay a full load), and `validate()` parses the M1 results JSON only
to discard it, so `main()` parses it twice.

M3's own first decision, per M2's "what M2 does not decide": whether M3 reuses
M2's 12-concept subset or re-derives one from M1 + M2 evidence. M2 gives it new
evidence to work with — a per-concept late-tier map on 12 concepts, a named
non-specific anti-example (`silver`), and a leak stratum that replicated
(Egypt, October at 3B).

Standing constraints unchanged: certified environment = `mps` + torch 2.13.0 +
transformers 5.13.1 (off it: NOT A RESULT); `m0_anchor.py` stays certified and
un-editable, and `m1_battery.GATE_WORDING` / `m2_depth.GATE_WORDING` are
byte-frozen with their artifacts (editing either forces a full re-run of that
milestone); adversarial review before any merge.

## Open questions / blockers

- None. M2 is closed; M3 is a fresh brief with no inherited blocker.

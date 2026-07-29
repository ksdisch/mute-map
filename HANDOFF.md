# HANDOFF.md — mute-map

_Last updated: 2026-07-28 (post-M3 decision session)_

## What was just done

**M3 built, run, and PASSED** (2026-07-28) — the specificity matrix, per the
frozen `docs/M3-BRIEF.md` (D15–D18). Landed in one PR with its docs spine:

- **`m3_matrix.py`** — the M3 runner, cut from `m2_depth.py` (never from the
  certified `m0_anchor.py`), with its own byte-frozen `GATE_WORDING`. Holds depth
  and dose fixed at the switch's home (late third, λ = 1, k = 1) so every cell
  differs from every other in exactly one thing: *which* direction was removed.
  486 cells per subject — 36 `clean` + 432 matrix + 18 out-of-subset
  control-extras — with the 108-cell M1 re-certification graded first.
- **`m3_verdict.py`** — the cross-subject AND over 1.5B and 3B, plus the
  descriptive package (within- vs cross-category split, row/column profiles,
  asymmetry, the printed grid). Refuses any run that is not a result.
- **`test_m3.py`** — 83 cases; the full suite is 272 and green.

**Results: MATRIX-SPECIFIC at 1.5B AND 3B.** Clause (1) pooled off-diagonal −
diagonal: +0.971 [+0.867, +0.983] at 1.5B (diagonal 0/34 vs off-diagonal
363/374) and +0.881 [+0.731, +0.943] at 3B (3/32 vs 343/352). Clause (2)
within-category: +0.950 [+0.814, +0.978] and +0.891 [+0.730, +0.947]. 0.5B also
MATRIX-SPECIFIC, off-gate. **No subject carries the ON A DAMAGED FLOOR
qualifier** — the collateral floor reads [0.728, 0.963] / [0.851, 0.995] /
[0.843, 0.994] against the pre-registered 0.5, which settles the one question
the brief left genuinely open. Every pre-registered n landed exactly (28/34/32
gated, 308/374/352 off-diagonal, 96/100/101 within-category, 24/28/29
restricted). The M1 cross-check re-certified the instrument bit-for-bit on every
run (108/108 cells, `concept_mass` exact, ×3 subjects). No degeneracy fired
anywhere, and the effective-n per-item collapse agrees with the pooled gate on
every subject and both clauses.

**The three descriptive findings the gate did not ask for:** collateral
concentrates on a few fragile **probes** rather than being caused by damaging
**primes** (at 1.5B all 11 off-diagonal misses land on 4 probes; `silver`,
`Canada`, `China`, `Jupiter` and `Mars` cause zero collateral as primes);
category-block collateral is CI-clean at 0.5B (cross − within +0.105 [+0.032,
+0.196]) and dissolves into noise by 1.5B; and the only non-zero diagonal cells
anywhere are `Egypt` 2/3 and `October` 1/2 at 3B — exactly the S3 leaky-switch
stratum D11 pre-registered.

**The one pre-registration that inverted.** `silver` entered the subset as the
*non-specific anti-example*, expected to damage everything. Its row damages
nothing at any scale (27/27, 31/31, 31/31); its **column** is the most fragile in
the grid (7/11, 27/33, 6/11). M1's and M2's single control cell had sampled
silver's column and been read as a fact about silver's row. This is a
re-attribution, not a retraction — M1's and M2's numbers stand as published.

**One carry-forward M3 creates, found at its own adversarial review (PR #9 F1).**
M3's gate is a conjunction, but D17's frozen degeneracy scope names only clause
(1)'s surviving arm (`off_diagonal`) as dispositive — clause (2)'s
(`within_category_off_diagonal`) is guarded nowhere, and at the two smaller
subjects it runs 3–4× the guarded arm's wrong-opening share (0.052 vs 0.016 at
0.5B, 0.030 vs 0.008 at 1.5B; at 3B the ordering inverts, 0.010 vs 0.014).
Nothing here is affected — neither gate-reading arm came within an order of
magnitude of COLLAPSE_SHARE = 0.5, and the one arm that does run close is the
pooled **diagonal** (0.464 at 0.5B), which D17 pre-registers as TAG-only because
it *is* the expected mute signature — and `m3_matrix.GATE_WORDING` was **not**
amended, because it is byte-frozen with three subjects' artifacts and editing a
pre-registration after seeing results is what D9/D10 exist to prevent. Owned in
M3-BRIEF's Honest limits, and carried here: **any later stage whose gate is a
conjunction must put every surviving-side comparison arm on the dispositive
degeneracy list, and its frozen wording must enumerate them explicitly.**

All four of M2's carry-forwards landed as the brief dispositioned them: PR #7 F2
(the tier-width caveat, retired structurally and stated affirmatively in D17's
frozen wording), F5 + F4 (D18's two run-time bars, span and ASCII, on the
subject's own tokenizer), and the non-blocking F6 (`m3_matrix.py` validates
before the checkpoint loads and `validate()` returns the parsed M1 artifact).

## Where things stand

Chain: ~~M0~~ → ~~M1~~ → ~~M2~~ → ~~M3~~ — **the v1 chain per `docs/KICKOFF.md`
is complete.** `docs/DECISIONS.md` now runs D1–D18. S1/S2 stretches are optional
and each needs its own brief.

## Immediate next move

**Decided (Kyle, 2026-07-28, session "mute-map post M3 decisions"): run the
vocabulary collateral strip as close-out stage M4, then write-up +
`/seed-hunt`.** The S1/S2 stretches were declined for this repo and banked as
idea #13 in `~/Projects/j-lens-proj-ideas/jlens-followon-backlog.md` — they
compete in the seed-hunt on equal terms, no incumbent's privilege.

**Where M4 stands: `docs/M4-BRIEF.md` is written and in review; decisions
D19–D22 await Kyle's freeze.** The stage: 12 subset primes × all 180 M1 items
(2,340 cells/subject), gate proposed as a single-clause VOCAB-SPARING level
bar on the never-measured non-subset pool (per-item survives-all-12, Wilson
lower bound ≥ 0.5 at 1.5B AND 3B, the 0.5 carried from M3's pre-registered
floor). Realized ns are known from the recorded gated sets (gate arm 41 / 71 /
84). Design facts found while drafting: four probe clues mention a prime's
spelling (October→september-2, silver→flute-1, China→jade-1, October→opal-2 —
D21 decides their treatment); all 60 roster words pass the D18 span bar on all
three tokenizers (checked in advance); the recorded same-category proxy for
the new pool reads 6/8 (1.5B) and 13/15 (3B) but **0/6 at 0.5B**, so the
off-gate 0.5B floor may genuinely fail — reportable under the standing frame.
No runner code exists yet; code only after freeze, cut from `m3_matrix.py`.

Standing constraints unchanged: certified environment = `mps` + torch 2.13.0 +
transformers 5.13.1 (off it: NOT A RESULT); `m0_anchor.py` stays certified and
un-editable, and `m1_battery.GATE_WORDING` / `m2_depth.GATE_WORDING` /
`m3_matrix.GATE_WORDING` are byte-frozen with their artifacts (editing any forces
a full re-run of that milestone); `oracle.py` is byte-shared by three consumers
and must stay identical in all of them; adversarial review before any merge.

## Open questions / blockers

- None blocking. M3 is closed and the v1 chain with it. Two inherited
  obligations, both conditional on a later stage existing: **(1)** S2's brief
  owes the `oracle._BOUNDARY` boundary-class decision before it freezes any
  non-ASCII list; **(2)** any stage whose gate is a **conjunction** must put
  every surviving-side comparison arm on the dispositive degeneracy list and
  enumerate them in its frozen wording (PR #9 F1, above).

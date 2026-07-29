# HANDOFF.md — mute-map

_Last updated: 2026-07-29 (M4 built, run, and PASSED — every measurement stage closed)_

## What was just done

**M4 built, run, and PASSED** (2026-07-29) — the vocabulary collateral strip, per
the frozen `docs/M4-BRIEF.md` (D19–D22). Landed in one PR with its docs spine:

- **`m4_strip.py`** — the M4 runner, cut from `m3_matrix.py` (never from the
  certified `m0_anchor.py`), with its own byte-frozen `GATE_WORDING` taken
  verbatim from D20 including the AS-SCORED ONLY qualifier and both string
  templates. Keeps M3's 12 characterized directions as the **primes** and widens
  the **probes** to all 60 M1 concepts: 180 `clean` + 12 × 180 = **2,340 cells
  per subject**, every one at the identical late third, λ = 1, k = 1. The 255
  M1-recorded and 468 M3-recorded cells — 633 of the 2,340 once the 90-cell
  overlap is counted once — are graded FIRST, and any mismatch exits INVALID
  before a new cell is read. D22's span and ASCII bars now run over all 60 scored
  words plus the 12 direction words.
- **`m4_verdict.py`** — owns `strip_verdict()` (precedence NOT A RESULT >
  DEGENERATE > UNDERPOWERED > the level bar, failing label the lineage null
  `not shown`) and the cross-subject AND over 1.5B and 3B. The runner imports it,
  so exactly one implementation of the pre-committed verdict string exists.
- **`test_m4.py`** — 124 cases (112 at first submission, +12 added at review);
  the full suite is 396 and green, in CI as well as locally.

**Results: VOCAB-SPARING at 1.5B AND 3B — AS-SCORED ONLY.** Of the gated items
whose concept is outside M3's twelve, those surviving **all 12** deletions:
**51/71 = 0.718 [0.605, 0.810]** at 1.5B and **63/84 = 0.750 [0.648, 0.830]** at
3B, both clearing the pre-registered 0.5 bar; 0.5B `not shown` off-gate at
**11/41 = 0.268 [0.157, 0.419]**. Every pre-registered n landed exactly (arms
41/71/84, concepts 23/41/43, ceilings 35/41, 69/71, 82/84 with precisely the
named misses). Both cross-checks re-certified the instrument bit-for-bit on every
run — M1 255/255 and M3 468/468 cells, `concept_mass` exact, ×3 subjects. No
degeneracy fired on the dispositive arm (shares 0.022 / 0.011 / 0.011 against a
0.5 threshold).

**The qualifier fired at both gate-bearing subjects, and it earned its
existence.** The pre-registered **concept-level collapse** — one binary per
concept instead of per item — reads 0.585 (lower **0.434**) at 1.5B and 0.605
(lower **0.456**) at 3B: below the bar while the item-level gate clears it. Per
D20's pre-commitment those are **the honest numbers to quote**, and Amendment 1
(round 4, F20) is exactly why they now ride inside the verdict string instead of
sitting in prose. The residual-conservative read clears at both (49/71 lower
0.575; 62/84 lower 0.635), so only one of the two reads fired.

**Three descriptive findings the gate did not ask for.** (1) M3's finding 1
**generalizes out of sample**: collateral concentrates on fragile **probes**, not
damaging **primes** — no prime's row falls below 63/71 at 1.5B or 77/84 at 3B,
while individual columns collapse (`copper` 6/12, `mosquito` 8/12 at 1.5B;
`eagle` 8/12, `platinum` 9/12 at 3B) and 32/53 and 33/55 gated columns take
**zero** collateral. The distribution is bimodal, which is why the item-level and
concept-level statistics diverge. (2) **Category-block collateral is real in the
wider vocabulary and does NOT dissolve with scale** — within 22/29 vs cross
769/823 at 1.5B, 35/53 vs 913/955 at 3B — reversing M3's read, whose
within-category arm was 30 of 34 pairs *countries*. A re-scoping of M3's finding,
not a retraction. (3) **0.5B is the first measured divergence** between the
subset-12's robustness and the wider roster's: 30 of 41 gate-arm items (73%) are
damaged by at least one deletion, against 28% at 1.5B and 25% at 3B.

**The residual set was bigger in the ablated arm than the clean arm.** The
clean-arm gate-arm residuals were the pre-computed 0 / 2 / 2, but the run
recorded 0 / 27 / 21 residual cells overall (26 / 21 in the gate arm), all on
`beetle`, `butterfly`, `trumpet`. That is exactly what D20's selector was written
for ("in the ablated cells the set is whatever the run records"), and it is why
the conservative read moves the number at all (51 → 49, 63 → 62). A case-exact
selector — the F16 defect — would have found zero of them.

**Both inherited obligations discharged.** The **conjunction-degeneracy** rule
(PR #9 F1) is satisfied by design: M4's gate is single-clause, so the dispositive
list has exactly one surviving arm, and `m4_strip.GATE_WORDING` enumerates it and
restates the rule for any future conjunction. The **`oracle._BOUNDARY`
boundary-class decision** was not owed: D18's trigger is a stage freezing a
non-ASCII list, and M4 adds no vocabulary — the ASCII bar pins the premise at run
time instead. That trigger still names the banked scope stretch.

## Where things stand

Chain: ~~M0~~ → ~~M1~~ → ~~M2~~ → ~~M3~~ → ~~M4~~ — **the v1 chain per
`docs/KICKOFF.md` is complete and the Kyle-picked close-out stage has landed.**
`docs/DECISIONS.md` now runs D1–D22. Nothing is pre-committed next. S1/S2 remain
optional stretches, each needing its own brief.

## Immediate next move

**Write-up, then `/seed-hunt`** — the plan of record since 2026-07-28, unchanged.
Every measurement stage is closed and M3's stated bound ("nothing here shows that
deleting France spares the other 48 M1 concepts") is now measured rather than
assumed. The S1 (7B) and S2 (lexical vs semantic scope) stretches were declined
for this repo and banked as idea #13 in
`~/Projects/j-lens-proj-ideas/jlens-followon-backlog.md`; they compete in the
seed-hunt on equal terms, no incumbent's privilege.

Two things a write-up must not get wrong, both pre-committed rather than
discovered after the fact:

- **The headline is scoped.** `VOCAB-SPARING` carries `AS-SCORED ONLY` at both
  gate-bearing subjects. The honest one-line summary is "the item-level floor
  clears 0.5; the concept-level floor's lower bound does not (0.434 / 0.456)."
- **The claim is about the *measurable* vocabulary.** 25 / 7 / 5 of the 48
  non-subset concepts gate zero items — a competence selection that plausibly
  enriches for robust concepts and biases the floor **upward**.

Standing constraints unchanged: certified environment = `mps` + torch 2.13.0 +
transformers 5.13.1 (off it: NOT A RESULT); `m0_anchor.py` stays certified and
un-editable, and `m1_battery.GATE_WORDING` / `m2_depth.GATE_WORDING` /
`m3_matrix.GATE_WORDING` / `m4_strip.GATE_WORDING` are byte-frozen with their
artifacts (editing any forces a full re-run of that milestone); `oracle.py` is
byte-shared by **four** consumers now and must stay identical in all of them;
adversarial review before any merge.

## Open questions / blockers

- **None blocking.** Every stage is closed.
- **CI ran zero tests from `fdcbfcc` until 2026-07-29, now fixed** (PR #13
  adversarial review, F1). `.github/workflows/ci.yml` looped `uv run test_<f>.py`,
  which executes each file as a plain script; with no `__main__` guard the files
  imported, defined their functions and exited 0, so the workflow's `rc` only ever
  reflected import errors. It now runs `uv run pytest -q "$f"` per file, keeping
  the per-suite log grouping — and the workflow is **green on the real runner**
  at `40e7c26` with all 396 cases genuinely collected and run. Any green CI badge
  before 2026-07-29 certifies syntax, not behaviour.
- **Making CI real immediately exposed a second defect** (same review, F5):
  `test_a_dry_run_never_loads_the_checkpoint` in both `test_m3.py` and
  `test_m4.py` passed `--lens lenses/<subject>.pt` into the real `main()`, which
  `torch.load`s the artifact before the `--dry-run` exit — and those weights are
  gitignored by decision K3, so the case passed locally and failed on every clean
  checkout. Both now supply the artifact synthetically via monkeypatched
  `torch.load`; the guarantee is unchanged (`from_pretrained` still raises if the
  checkpoint loads). **Note for a later M3 audit: `test_m3.py` was edited in PR
  #13, after M3 PASSED.** Only that one test changed; `m3_matrix.py`, its frozen
  `GATE_WORDING` and its published artifacts are untouched — leaving M3's copy
  broken would have left the shared CI gate red.
- **Three follow-ups from the same review, all nice-to-have, none fixed:**
  **(F3)** `m4_strip.GATE_WORDING["degeneracy"]` — byte-frozen with three
  subjects' artifacts, so it cannot be edited — promises per-pair-cell degeneracy
  texture "attached to the readout it compromises", but `strip_package()` computes
  none and its `tokenizer` parameter is left unused (M3 computed exactly that).
  Honouring it would change the JSONs and cost a ~50-minute re-run for a readout
  that is pre-declared non-verdict-bearing at n ≤ 3; the write-up owes a
  deviations-table row instead, and must not quote that clause as if the field
  exists. **(F4)** `m4_strip.main()` re-parses the battery outside the
  `try/except` that turns battery drift into a clean `VERDICT: INVALID`, so those
  guards would raise a bare traceback rather than exit 2 — unreachable, since the
  file cannot change between the two calls in one process.
  **(F6)** the CI job is still *named* `offline-suites` and its header comment
  still claims no network, but now that pytest really runs, four Qwen2.5
  tokenizer repos are fetched from `huggingface.co` on every push and PR
  (`test_the_whole_sixty_word_roster_clears_both_bars_on_the_real_tokenizer` ×3
  plus M3's roster test). 390 of 396 pass with no network at all. **A future red
  build there is network, not logic.** The two remedies — cache
  `~/.cache/huggingface`, or add a `network` marker and deselect it — trade off
  against each other (the marker route stops exercising the real tokenizers,
  which is the roster bar's whole point), so it is a workflow design call rather
  than a correctness fix.
- **One conditional obligation survives:** S2's brief owes the
  `oracle._BOUNDARY` boundary-class decision before it freezes any non-ASCII
  list. M4 did not fire that trigger.

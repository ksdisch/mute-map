# M2 start-of-stage brief — localization + dose

*Start-of-stage brief per the per-stage rhythm: plain-terms explanation first,
design extraction second, decisions third, code only after Kyle freezes.
Decisions here are D9–D14, continuing `docs/DECISIONS.md` (D4–D8 were M1's).
Per M1's owed follow-up, this brief opens with the oracle — the readout itself —
before any window or dose design.*

## Why this brief opens with the readout, not with layers

M1 ended with a caveat that bounds everything M2 would otherwise build on. The
primary readout scores exactly one token: the model's single highest-probability
next token (the "greedy first token"). A concept can therefore only be scored
when its spelling fits through that one-token keyhole — and for **26 of the 60
roster words the bare (no-leading-space) spelling is more than one token**. The
model answers "Mercury" and the instrument sees only the fragment `'Mer'`, which
it scores as a miss. Planets and musical instruments gated **0 items on all
three subjects** for this reason alone; the first-3-greedy texture shows the
models often *did* say those words (35/142, 54/119, 80/136 of ungated items).

M1's gate is untouched by this — the bias runs *against* the claim, never for
it — but the *map* is bounded to the vocabulary the readout can see. M2 is the
mapping milestone. So before deciding where to slide windows, the project owes a
decision on the measuring stick itself. A change to the oracle is a change to
the measurement: it belongs here, in a decision frozen before any run — never in
a results section — and M1's pre-committed numbers stand regardless (any
re-scoring is a separately-labelled reanalysis published *beside* them, D10).

## What M2 is, in plain terms

M1 established that the off-switch is broad. M2 asks two depth questions:

1. **Localization — where does the switch live?** S4b ablated three fixed
   "thirds" of the workspace band (early / middle / late) and found the switch
   only in the late third. M2 slides a window of layers along the *whole* model
   depth — including probe positions outside the band entirely — and measures,
   at each position, how much deleting the concept's direction there mutes the
   word. The deliverable is a curve over depth: flat where the direction is
   redundant, cratered where the switch lives.
2. **Dose — how much of the direction must be removed?** The operator currently
   deletes the direction completely (subtracts the full component along it). M2
   removes it *partially* — a dial λ ("lambda", the fraction of the component
   removed): λ = 0 touches nothing, λ = 1 is the full deletion, and the KICKOFF
   grid {0, .25, .5, .75, 1} traces the curve between. Is the switch a dimmer or
   a step function?

Both run on a **pre-registered 12-concept subset** of M1's frozen battery
(KICKOFF's scope), stratified by what M1 actually measured, reusing M1's own
items verbatim — which buys M2 the same standing re-certification M1 had: the
cells M2 shares with M1 must reproduce the recorded artifacts bit-for-bit before
any new cell is read.

## Design extraction (verbatim, source-cited)

**KICKOFF's M2 milestone (frozen scope):** "M2 — depth: localization + dose
(3–4 days, $0). Pre-registered 12-concept stratified subset: sliding
layer-window sweep incl. outside-band probes; partial-ablation dose curve,
λ ∈ {0, .25, .5, .75, 1}. **Gate: late-window effect CI-cleanly exceeds early
and middle, pooled.** Dose shape descriptive."

**The tier convention M2 refines — dim-stage S4-BRIEF D28:** "Depths = the S1
sub-band thirds of the frozen band (early / middle / late; the paper contrasts
early vs late — middle rides along as free texture). k = 1 (the implied
concept's own J-lens vector, M1's direction convention); specificity control =
the same-category alternative's vector through the identical operator. S3's
runtime read-back and degeneracy guard unchanged."

**What S4b already measured at the three tiers (the anchor M2 extends):** naming
on the gated cell — primed_late 0 / 0 / 0, control_late 1 / 16 / 8, primed_middle
3 / 17 / 8, control_middle 5 / 18 / 8 (0.5B n=5 / 1.5B n=22 / 3B n=8); and the
recorded synthesis: "Middle-tier removals are benign for both vectors
everywhere — the switch lives specifically in the late third." Naming under
*early* ablation was spared on every subject (S4's leg 2 held, including 18/22
at 1.5B). M2's gate formalizes exactly this shape on powered cells.

**Band arithmetic (instrument facts, from the certified port):** the workspace
band is proportional — layer l is in-band iff 0.38 ≤ l/(n_layers−1) ≤ 0.92
(`harness.proportional_band`, frozen table `FROZEN_BANDS`); thirds split with
`third = max(1, n // 3)`, late taking the remainder (`sub_band_thirds`, ported
convention). Lens directions exist for layers 0..n_layers−2. Concretely:

| Subject | Band | Early | Middle | Late | Lens range | Room below / above band |
|---|---|---|---|---|---|---|
| 0.5B (24L) | L9–21 (13) | L9–12 (4) | L13–16 (4) | L17–21 (5) | L0–22 | 9 / 1 layers |
| 1.5B (28L) | L11–24 (14) | L11–14 (4) | L15–18 (4) | L19–24 (6) | L0–26 | 11 / 2 layers |
| 3B (36L) | L14–32 (19) | L14–19 (6) | L20–25 (6) | L26–32 (7) | L0–34 | 14 / 2 layers |

The asymmetry is structural: the band's 0.92 ceiling nearly touches the lens
ceiling, so outside-band probing is deep below the band and thin above it —
owned in D12, not discoverable later.

**M1 recorded facts this design stands on** (all from the committed
`results/m1-battery-*.json`; "wide" numbers are design math computed from the
recorded first-3-greedy texture, labelled as such — nothing here is a published
result until D10 lands):

- Primary gated n: 38 / 61 / 44 of 180 (0.5B / 1.5B / 3B). Hard-switch sets
  (fixed denominator): the two gate-bearing subjects share **{Brazil, Canada,
  China, France, Japan}** — all countries.
- Token geometry, measured on all three Qwen2.5 tokenizers (they agree exactly):
  26 of 60 bare forms are multi-token; the **maximum bare length anywhere is 3
  tokens** (beetle, butterfly, trumpet) — i.e. the recorded 3-token texture span
  can hold every roster word. One quirk: `opal` is the sole word whose
  *leading-space* form is multi-token (its bare form is single).
- Widened-readout projections (prefix rule, D9b, case-insensitive), computed
  offline from the recorded spans, every number labelled inline: gated n **69
  (0.5B) / 105 (1.5B) / 116 (3B)**; primed 0/69 (0.5B), 0/105 (1.5B), 12/116
  (3B); control 33/69, 80/105, 92/116 (same order); contrast +0.478 [+0.353,
  +0.594] (0.5B), +0.762 [+0.665, +0.833] (1.5B), +0.690 [+0.582, +0.767]
  (3B). Planets prefix-gate 7 (0.5B) / 8 (1.5B) / 15 (3B) of 18 items and
  instruments 2 / 8 / 13 (same order) — the dark categories light up on both
  gate-bearing subjects.

**Paper context (context, never a reproduced claim):** the seed paper's Figure
69 late-band texture — the late workspace copy as "the intention to say this
word" (transformer-circuits.pub/2026/workspace). M2's localization curve is this
project's own characterization of where that intention-to-say switch actually
sits at our scales.

## Decisions to freeze (Kyle picks; recommendations flagged)

*Frozen (Kyle, 2026-07-28): D9 (b) greedy-span prefix oracle (case-insensitive,
word-boundary; first-token recorded beside every cell); D10 (a) offline
re-score published as a labelled reanalysis beside M1's standing numbers; D11
(a) the shared stratified 12; D12 (b) tier gate cells + stride-2 sliding sweep;
D13 (a) primed-only dose at the late third; D14 as written. Full DECISIONS.md
entries land with the M2 code PR, per the M0/M1 pattern. Amended pre-run at
this PR's adversarial review, all Kyle-approved ("pull all four" for the
nice-to-haves): F1 subject-order labelling; F2 mass-channel scoping (D13); F3
direction-keying ownership (D11); F4 the both-oracle per-source split; F5 the
span-end boundary reading (D9); F6 S2′'s resolution order; F7 the corrected
clean-arm cap argument (D14); F8 the late-anchored window grid (D12); F9 the
re-scoped degeneracy disposition (D14).*

### D9 — The oracle: what counts as "the model said the word" (decide first)

The current primary: produced iff the greedy first token is one of the
concept's single-token forms (bare or leading-space spelling), **case-exact**.
Three things it cannot see, all orthography rather than semantics: a bare
multi-token spelling (`'Mer'`…), a capitalized answer ("Piano" for piano — a
different token id), and an answer prefixed by filler ("The France" — S4's
owned miss-counting caveat).

- **(a) Keep it, own the reach.** Zero measurement change; the whole lineage
  stays on one oracle. *Trade-off:* M2's map covers only the 34
  single-bare-token words; planets and instruments stay dark forever; the
  per-category map remains partly a map of tokenizer geometry. The subset's S2
  stratum (below) is impossible.
- **(b) Widen to the greedy-span prefix rule (recommended).** Produced iff the
  decoded first-3-greedy span — already recorded for every cell, and long
  enough for every roster word (max bare form = 3 tokens, measured) — after
  stripping leading whitespace, **opens with the concept's spelling at a word
  boundary, case-insensitive**. "Marseille" does not match Mars (the boundary
  check); "not France" does not match France (prefix, not containment); "The
  France" still counts as a miss (S4's caveat stays owned, unchanged in kind).
  **The end of the span counts as a word boundary** (review F5): a word that
  exactly fills the recorded span ("Butterfly") is a hit — truncation must
  never turn a completed word into a miss, and this is the reading every
  projection and pre-registered n in this brief was computed under (six
  recorded cells decide between the readings, two on the control arm; frozen
  as a named unit-test case in the M2 code PR).
  This is still a deterministic oracle: greedy decoding is deterministic and
  the rule is a fixed string comparison on that deterministic span, frozen as
  code with unit tests — not free-text parsing, and never a judge. The
  first-token outcome is **still computed and recorded beside every cell**, so
  anchor- and M1-comparability never degrade (all cross-checks compare raw
  recorded fields, not oracle verdicts). *Why case-insensitive:* measured, it
  is doing real work (1.5B prefix gate 72 case-exact → 105 case-insensitive) —
  models capitalize answers; "Piano" is the word piano. *Trade-off:* a
  measurement change mid-project — owned as a deviations row, with M1's numbers
  standing and any re-score a labelled reanalysis (D10).
- **(c) Widen to span containment.** Produced iff the word appears *anywhere*
  in the 3-token span (this is exactly the recorded `says_concept_in_3`
  texture; ns 73 / 115 / 124). Largest reach, weakest semantics: "not France"
  would count as producing France — on a control arm that *inflates* the
  contrast, the one bias direction this project never accepts. Not recommended.

Either way, `says_concept_in_3` stays recorded unchanged as texture
(continuity with M1's artifacts).

### D10 — Publish an M1 reanalysis under the widened oracle? (conditional on D9 ≠ a)

Pre-declared in M1's results: M1's pre-committed numbers stand as published;
a widened-oracle re-score may only appear as a clearly-labelled reanalysis
*beside* them.

- **(a) Offline re-score from the committed artifacts (recommended).** A small
  script (`m1_rescore.py`) that is a **pure function of the recorded M1
  JSONs** — no model run, no new trials. Possible because the recorded span is
  provably sufficient (3 tokens ≥ the longest bare form; for a prefix rule,
  span truncation cannot hide a hit, since a hit must start at the span's
  first word). Emits `results/m1-rescore-*.json` plus a REANALYSIS-labelled
  addendum table in M1-BRIEF's results, beside — never replacing — the
  pre-committed table. Reviewable end-to-end; PR #4's F5 per-source split
  lands in the same artifact for free (below).
- **(b) Full re-run with the widened runner.** ~15–20 min for all three
  subjects, deterministic; produces span-native artifacts. Buys nothing (a)
  doesn't already have, and creates a second generation of M1 artifacts to
  keep straight. Only needed if the recorded span were insufficient — it is
  not. Not recommended.
- **(c) No reanalysis.** Own the bound; the wide numbers stay design math.
  (If D9 = (a), this is the only coherent option.)

### D11 — The pre-registered 12-concept subset (rule + resulting list)

Items: **each selected concept's 3 frozen M1 clues, verbatim** — no new
authoring. This is what makes M2's standing re-certification possible (D14):
the subset's clean / primed_late / control_late cells already exist in M1's
recorded artifacts and must reproduce exactly.

- **(a) One shared subset by a frozen stratified rule (recommended).** The rule
  is applied to the recorded M1 artifacts, so the list is fixed the moment the
  rule is — pre-registered here, no discretion at run time:
  - **S1 — hard-switch core (5):** the gate-bearing subjects' shared
    hard-switch set, verbatim: **Brazil, Canada, China, France, Japan.** (It is
    all countries. That fact is itself part of the map, owned below.)
  - **S2 — readout-unlocked (4):** from the two categories that primary-gated 0
    items everywhere (planets, musical instruments): top 2 per category by
    summed prefix-gated items across the gate-bearing subjects, tie-break
    alphabetical → **Jupiter, Mars** (3+3 each), **violin** (2+3), **piano**
    (2+2). One convention S2 must own (review F3): for these four concepts the
    ablated direction is keyed to the **leading-space token's unembed row**
    (`' Jupiter'`) — the only single-token form that exists — while D9(b)
    scores the bare spelling the model actually emits. This is measured, not
    assumed: in M1's recorded data the space-keyed late ablation *does* mute
    the bare emission (primed 0 on all four concepts at both gate-bearing
    subjects; 0/105 pooled at 1.5B) — an owned convention with evidence, in
    the deviations table below. Requires D9 ≠ (a); under D9(a) this stratum is
    unmeasurable and is replaced by S2′: top 4 by summed primary-gated items
    among concepts not selected by S1, S3, or S4 (S2′ resolves after them —
    review F6), tie-break alphabetical → February, Friday, September, January.
  - **S3 — leaky switch (2):** primary-gated on both gate-bearing subjects with
    any primed-arm leak, ranked by leak count then gated total then
    alphabetical → **Egypt** (3B primed 2/3), **October** (3B primed 1/2).
  - **S4 — non-specific anti-example (1):** ≥ 3 primary-gated items on the
    powered subject (1.5B) with control_late 0/3 — the cell where the *control*
    deletion also mutes, the "any-direction damage" signature M2's map needs at
    least one exemplar of. Pool: {Friday, silver}; of these, Friday's
    control_late *survives* 2/2 where it gates at 3B — its non-specificity
    does not replicate — while silver is un-gated at 3B and so uncontradicted.
    Rule: drop any pool member whose control arm survives on the other
    gate-bearing subject, then alphabetical → **silver** (Friday is the named
    alternate).

  Resulting 12: **Brazil, Canada, China, Egypt, France, Japan, Jupiter, Mars,
  October, piano, silver, violin** (6 countries, 2 planets, 2 instruments, 1
  month, 1 metal). *Trade-off, owned:* countries-heavy because the measured
  hard-switch stratum *is* countries — the map goes where the effect was
  measured, and S2–S4 spread the coverage deliberately.
- **(b) Per-subject subsets.** Each subject gets its own best-measured 12.
  Maximizes per-subject n; destroys cross-subject comparability of every
  curve. Not recommended.
- **(c) Hard-switch-only 12.** Deepest sampling of the effect; no unlocked
  categories, no anti-example, no leak stratum — a map of one country-shaped
  island. Not recommended.

### D12 — The window scheme (localization)

Window semantics: identical operator (k = 1 projection removal of the concept's
direction), identical runtime read-back, with the layer set swapped from "the
late third" to the window's contiguous layers.

- **(a) Tier cells only.** clean + primed/control at each of early/middle/late.
  The gate's minimum — but no fine map and no outside-band probes, which
  KICKOFF's frozen scope names explicitly. Under-delivers; fallback only.
- **(b) Tiers + sliding sweep (recommended).** Two parts, cleanly separated:
  - **Gate cells (pre-committed):** the three frozen thirds, primed AND control
    at each (6 ablated conditions + clean) — the S4b-comparable frame, now
    powered.
  - **Descriptive map:** a window of width = the subject's late-third width
    (5 / 6 / 7 layers), slid at stride 2 across the full lens range L0..n−2,
    **primed arm only**. The stride-2 grid is **anchored on the late-third
    start** (this run's review F8), so the gate cell is a point on every
    subject's map — and that window *is* the `primed_late` tier cell, reused
    rather than re-run. The maximum-start window (the lens ceiling) is added
    when the grid does not already include it — relevant at 0.5B, where the
    anchored grid alone would stop one layer short of L22. Positions per
    subject: 10 / 11 / 15, of which the late-start window is reused →
    **9 / 10 / 14 newly-run window conditions**. Windows starting below the
    band are the outside-band probes (9–14 layers of room); above-band
    coverage is structurally thin (1–2 layers, owned in the extraction
    table). Stride 2 localizes any transition edge to ±2 layers.
- **(c) Single-layer sweep.** Finest resolution, but ablating 1 layer where the
  tier cells ablate 4–7 under-doses the intervention — a flat curve would be
  unreadable (no switch found, or dose too small?). Also the costliest. Not
  recommended as primary; if the width-w map shows a sharp edge, a
  single-layer zoom near that edge is a natural M2-results follow-up, decided
  then, descriptive only.

### D13 — The dose design (partial ablation)

Grid frozen by KICKOFF: λ ∈ {0, .25, .5, .75, 1}. Operator: h′ = h − λ·(v̂ᵀh)v̂
per position at each late-third layer — remove λ of the component along the
direction. The runtime read-back generalizes: the surviving projection must
equal (1−λ) times the original within `READBACK_TOL` (at λ = 1 this is exactly
M1's check). The partial operator is new code and lives in the M2 runner —
`intervention.py` stays verbatim-ported — unit-covered per the F6 pattern.

- **(a) Primed arm only, at the late third (recommended).** λ = 0 is `clean`
  and λ = 1 is `primed_late` — both already-run, deterministic cells, reused
  not re-measured; only λ ∈ {.25, .5, .75} are new conditions. Readout per λ:
  naming rate under D9's oracle for all subset items, plus mean concept mass —
  the graded signal that can show a dimmer even where the binary steps —
  computed **only over the concepts with a single-token form of the spelling
  the model emits** (review F2): the S2 stratum's bare spellings have no
  single-token form, so its mass channel is floor-pinned by construction
  (measured on the clean arm: S2 mean 0.009 vs 0.913 for the rest at 1.5B) and
  its dose curve is read on the binary rate alone, owned in the deviations
  table. Dose shape descriptive, as frozen — no gate.
- **(b) Primed + control at every λ.** Doubles dose cost for a collateral curve
  S4b and M1 both predict is flat. Not recommended.
- **(c) Dose × window cross.** λ at every window position explodes the run
  (~45–75 conditions) and answers nothing KICKOFF asked. Not recommended.

### D14 — The pre-committed wording package (gate, degeneracy re-freeze, cross-check, precedence)

**Gate wording (pre-committed).** Per subject, on the pooled gated cell —
gating is the clean arm under D9's frozen oracle, decided once per item,
window-independent, so every window/tier/dose cell shares one gated set:

> **LATE-LOCALIZED** iff naming under `primed_early` minus naming under
> `primed_late` is positive with its Newcombe 95% CI excluding 0, AND naming
> under `primed_middle` minus naming under `primed_late` likewise. The M2
> verdict is the AND over 1.5B and 3B; 0.5B runs and is reported under its
> standing any-direction-damage frame, never gate-bearing. Pooled gated
> n < MIN_N = 20 ⇒ pre-declared UNDERPOWERED and no localization claim.

This *is* KICKOFF's "late-window effect CI-cleanly exceeds early and middle"
expressed in directly comparable proportions: the effect at tier T is the
naming drop clean − primed_T on the same items, so effect_late − effect_T =
primed_T − primed_late — the shared clean arm cancels, leaving a plain
two-proportion comparison the ported ruler already decides. The rejected
alternative — a CI on the difference-of-differences itself — needs stats
machinery beyond the frozen Wilson/Newcombe ruler; a new method mid-lineage for
no added honesty. Control tiers are reported beside as the specificity texture
(the late contrast re-shown descriptively; M1's gate is not relitigated).

**Degeneracy disposition, re-frozen (owes PR #4 review F3).** Two changes, both
recorded here before any M2 run:

1. *The F3 correction.* `clean` is the **gate arm**, not a comparison arm: on
   the gated cell its answers are, by construction, correct openings of up to
   60 different spellings, so no single token can approach COLLAPSE_SHARE =
   0.5 on a powered cell. Under the first-token oracle the share is capped
   near 3/n (three clues per concept); under D9(b), where fragment first
   tokens can be shared across concepts, the structural cap loosens but the
   measured worst case on the recorded data is 4/116 ≈ 0.034 (this run's
   review F7 — a right call, now with the right reason). M1's wording
   listing `clean` among the monitored arms was inert (it could never fire on a
   powered cell, and fired nowhere) — that wording stays byte-frozen with M1's
   artifacts in `m1_battery.GATE_WORDING`, un-edited; M2's own GATE_WORDING
   drops `clean` from the dispositive list and records why.
2. *The wide-oracle adaptation.* Under D9(b) a high-scoring arm's first-token
   distribution legitimately concentrates on fragments (`'Vi'`, `'The'`) that
   open *correct* answers, so raw first-token collapse stops meaning pathology.
   The dispositive guard therefore pools the first tokens of the arm's
   **non-produced items only**, with the share still computed against the full
   gated n — "at least half of this arm's answers are the same *wrong*
   opening." The raw all-answers guard stays recorded beside as texture (M1
   comparability). Disposition, scoped to the arms the gate actually reads
   (this run's review F9): collapse in a surviving-side gate arm
   (`primed_early`, `primed_middle`) ⇒ **DEGENERATE**, no LATE-LOCALIZED
   claim; collapse in `primed_late` ⇒ **TAG only** (the expected mute
   signature); collapse in a **control tier** — arms the gate does not read —
   is a **specificity-texture caveat**: recorded, attached to the control-tier
   readouts it compromises, never dispositive over the localization verdict
   (re-scoped from M1, where `control_late` *was* the comparison arm).
   Sliding-window and dose cells are descriptive, so their guards are always
   texture.

**The standing re-certification, one generation deeper.** The subset's
`clean` / `primed_late` / `control_late` cells must reproduce M1's recorded
`results/m1-battery-*.json` cell-for-cell on the recorded fields (`greedy` and
`greedy_3` decoded strings; `concept_mass` equality as texture) **before any
new window or dose cell is read** — graded first, M1's `order_reused_first`
pattern. On the certified stack (device `mps`, torch 2.13.0, transformers
5.13.1) any mismatch is INVALID (exit 2); off it the check is recorded but the
whole run is pre-declared NOT A RESULT, and the M2 verdict script refuses it
(M1's environment-scoping, D5/F7, carried verbatim). Note the comparison is on
raw recorded strings, so it is oracle-independent — D9 cannot soften it.

**Verdict precedence, frozen:** NOT A RESULT > DEGENERATE > UNDERPOWERED > the
contrast. Wrong-arm inputs exit INVALID before any trial; `--dry-run` validates
and stops; `--limit` is smoke, never a result — all M1 patterns carried, with
the wording frozen in the M2 runner's GATE_WORDING before any run.

## Review follow-ups landing in M2 (from PR #4's adversarial review)

- **This brief:** F3 → the degeneracy re-freeze in D14 (recorded here, frozen
  as code in the M2 runner; `m1_battery.GATE_WORDING` and M1's artifacts stay
  byte-identical, per the editing-GATE_WORDING-forces-re-runs rule).
- **M2 code PR:** F4 — `torch.load`'s except tuple widened in the M2 runner
  cut *and* in `m1_battery.py` (code-only, no wording or artifact change). F5 —
  the per-source split lands in the D10 reanalysis artifact (the recorded JSONs
  carry per-item `source`), computed under **both oracles** (this run's review
  F4): the primary first-token split closes PR #4's F5 at its recorded
  values — new-items-only contrast CI-clean at all three subjects, **+0.278 /
  +0.545 / +0.478** (0.5B / 1.5B / 3B) — as our own recorded number instead of
  a PR comment, and the widened-oracle split is reported beside it as part of
  the labelled reanalysis (projected +0.389 / +0.714 / +0.629, same order).
  F6 — `concept_ablation_edits` + `greedy_continuation` get direct unit tests,
  and the new window-edit and partial-λ operators get the same treatment from
  birth. F7 — the loader validates `forbidden_forms` keys against the roster.
  F11 — the `--limit` test monkeypatches `from_pretrained` (the suite's only
  `main()` caller stops loading a real model).

## Deviations table additions (owned)

| Deviation | From | Owned reason |
|---|---|---|
| Widened primary oracle (if D9b) | S4/M0/M1 greedy-first-token primary | Fixes tokenizer geometry, not semantics; first-token outcome recorded beside every cell; all cross-checks compare raw fields; M1's published numbers stand, reanalysis beside (D10) |
| Case-insensitive spelling match (if D9b) | case-exact token-id membership | Orthography, not semantics — "Piano" is piano; measured effect: 1.5B prefix gate 72 → 105 |
| String rule on a decoded span (if D9b) | token-id set membership | A fixed decision rule on a deterministic 3-token greedy span, frozen as code with unit tests — not free-text parsing, never a judge |
| Partial-projection operator (new code) | `intervention.py` ported verbatim | Lives in the M2 runner; read-back generalized to survivor = (1−λ)·original within tol; unit-covered (F6 pattern) |
| Sliding windows (no S4b precedent) | S4b's three fixed thirds | The point of M2 — characterization, not reproduction; the tier cells keep the S4b-comparable frame beside the new map |
| Subset countries-heavy (6/12) | the roster's uniform 10 × 6 | The measured shared hard-switch set is all countries (S1 stratum verbatim); S2–S4 spread coverage deliberately |
| Mass channel scoped to single-token-form spellings (D13, review F2) | M1's `concept_mass` on every cell | The S2 stratum's bare spellings have no single-token form, so its mass is floor-pinned by construction (clean-arm mean 0.009 vs 0.913 at 1.5B); S2's dose curve is binary-only |
| Direction keyed to the leading-space unembed row for multi-token-bare concepts (review F3) | the "bare form first" convention, which only exists for single-bare-token words | No bare single token exists for those 26 roster words; measured in M1's recording: the space-keyed late ablation mutes the bare emission (primed 0 on all four S2 concepts at both gate-bearing subjects) |

## Expected power (honest math)

Mostly *realized*, not projected: gating is a property of the clean arm, which
is deterministic and already recorded, so on the certified stack the subset's
pooled gated ns are known now — under D9(b): **34 (1.5B), 32 (3B), 28 (0.5B)**;
under D9(a) with the S2′ list: 34 (1.5B) / 29 (3B). Every
tier, window, and dose cell shares that one gated set, so every pooled cell
clears MIN_N = 20 on both gate-bearing subjects under either branch. (If a run
disagrees with these ns, that is itself an INVALID cross-check, not a power
surprise.)

The honest limits: per-concept-per-window cells are n ≤ 3 — always descriptive,
never verdict-bearing (M1's D7 logic, unchanged). M1's honesty rows carry over
(within-concept clustering; paired arms under an independent-samples Newcombe,
which widens and so cannot manufacture a false verdict; MIN_N on raw n) plus
one new row: the *same* gated items appear in every window and dose cell, so
curves are within-item correlated across positions — fine for the pairwise
gate, and one more reason the map itself stays descriptive. S4b's own tier
data (middle benign everywhere, early sparing naming everywhere) predicts the
gate passes; M2's value is the powered, controlled version of that shape plus
the map S4b never drew.

## Wall-clock plan

36 items × (1 clean + 6 tier + 9/10/14 newly-run window + 3 dose) = 19 / 20 /
24 conditions → 684 / 720 / 864 cells per subject, ×3 forwards each (the
3-token texture span) ≈ 2.1–2.6k forwards per subject — about 1.4× an M1
subject run.
All three subjects comfortably under an hour on MPS, $0, run backgrounded with
untracked logs. Cross-check cells graded first (D14). The D10 reanalysis costs
no model time at all. Standard machinery regardless of decisions: wrong-arm
input exits INVALID; `--dry-run` validates and stops; `--limit` is smoke,
never a result; gate wording frozen as code before any real run.

## What M2 does NOT decide

- M3's matrix design (its own brief; whether M3 reuses this subset or
  re-derives one from M1 + M2 evidence is M3's first decision).
- Anything about 7B (S1 stretch), the environment pins, or lens provenance
  (K3 stands).
- M1's published verdicts and numbers — they stand as pre-committed; D10 can
  only add a labelled reanalysis beside them.
- No oracle beyond D9's frozen rule — never an LLM judge, never free-text
  parsing (standing guardrail).

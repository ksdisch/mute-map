# Cartography of a late-band output off-switch in small language models

> **About this document.**
> **Paper:** *Cartography of a late-band output off-switch in small language models*
> **Authors:** the *mute-map* project (the source document records no author list)
> **Source:** [`docs/paper/mute-map-paper.md`](mute-map-paper.md), in this repository
> **Rewrite generated:** 2026-08-04
>
> This is a plain-English rewrite that mirrors the original one-for-one: same
> headings in the same order, same paragraphs in the same order, nothing merged,
> dropped, added, or reordered. Only the language changes. Every number, verdict and
> claim is stated exactly as the original states it. Tables are carried over
> unchanged, each followed by an *in-plain-words* gloss; the six figures are the
> original images with rewritten captions; the references section is carried over
> word-for-word. The paper contains no display equations, so no "named form" blocks
> appear below.

---

**How far the effect reaches, where inside the model it lives, how much of it you
need, how precisely it hits its target, and what else it breaks: switching off a
single word in the small Qwen2.5 models (0.5B, 1.5B and 3B, instruction-tuned) by
deleting one direction.**

*The mute-map project, 2026-07-29. Every measurement was run on a local machine,
using only ordinary forward runs of the model — no training, no gradients — at a
total cost of \$0.*

> **A note on the figures.** All six are drawn by [`figures.py`](figures.py) from the
> saved result files in `results/`, and they plot nothing except values that were
> actually recorded — counts, rates, and the error bars the measurement scripts
> themselves wrote down. Nothing is smoothed, curve-fitted, or filled in between
> measured points: on the sweep and dose figures, no line connects the marks, because
> the values in between were never measured. The script prints every number it plots,
> so each figure can be checked against the tables without ever opening the image
> file. Nothing was re-run or re-measured for this write-up.

---

## Abstract

While independently rebuilding Anthropic's Jacobian-lens work
([transformer-circuits.pub/2026/workspace](https://transformer-circuits.pub/2026/workspace/index.html)) —
a *Jacobian lens* being a readout that maps a model's internal activity onto one
direction per word — the earlier project *dim-stage* noticed an effect that survived
every check it threw at it. If you take a single concept's lens direction and
subtract out just that one component of the model's internal activity (a *rank-one
projection removal*: strip out one direction, leave everything else alone) at the
last third of that model's "workspace band" of layers, the model becomes unable to
say that word — while doing the exact same thing to a control direction from the
same category does not silence it (a gap of +0.727, with a 95% error bar of
[+0.471, +0.868], at the 1.5-billion-parameter model). That finding rested on a
single measured cell of 22 items and a single control. This paper maps the effect
out properly. Across five stages, each with its pass/fail rule written and locked
before the runs, on Qwen2.5-0.5B/1.5B/3B-Instruct — an exact re-run of the original
measurement, a 60-concept / 180-item battery, a sweep over locations and removal
strengths, a full 12 × 12 grid of "delete A, test B" pairs, and a 12-direction ×
180-item collateral-damage strip — the switch turns out to be broad (+0.656
[+0.517, +0.763] at 1.5B; +0.636 [+0.443, +0.759] at 3B), tied to the last third
rather than to the band as a whole (early minus late = +0.853 [+0.668, +0.936] at
1.5B), graded rather than all-or-nothing as you dial the removal up, and precisely
targeted across the grid (+0.971 [+0.867, +0.983] at 1.5B). The closing stage asks
whether deleting one concept leaves the *other 48* alone: counted item by item, the
worst-case floor clears the pre-set bar of 0.5 (51 of 71 = 0.718 [0.605, 0.810] at
1.5B; 63 of 84 = 0.750 [0.648, 0.830] at 3B), but counted concept by concept — the
other measure locked in beforehand — the bottom of the error bar does not (0.434 and
0.456), so both verdicts carry a pre-declared **AS-SCORED ONLY** qualifier. We report
every null result and every limit we own, plus two findings that change *what an
earlier measurement was a fact about* rather than overturning it. The reference point
throughout is our own recorded result, never a published claim.

---

## 1. Introduction

Findings in interpretability — the study of what is going on inside a model — are
easy to state and hard to put limits on. An intervention that produces a dramatic
change in behaviour, such as a model that suddenly cannot say "France", looks like a
mechanism. Whether it really *is* one depends on questions a single measured cell
cannot answer: does it work for other words, or only the ones you happened to try?
Does it need that exact location inside the model? Is it an on/off switch or a
dimmer? Does it damage only what it is aimed at? This project answers those four
questions for one specific effect, and then a fifth question that the first four
leave hanging.

**The honest framing of what this is.** It is neither a reproduction of somebody
else's published claim nor a brand-new mechanism. It is the first **original
characterization** in this line of projects: an effect found while replicating
something else, and mapped out here. The reference point is the earlier project
*dim-stage*'s own recorded result from its S4b stage (written up in `docs/S4-BRIEF.md`
over there), which this project re-runs bit-for-bit before measuring anything new.
The paper that started this line of work — Anthropic's workspace / Jacobian-lens
write-up at
[transformer-circuits.pub/2026/workspace](https://transformer-circuits.pub/2026/workspace/index.html),
which has no arXiv identifier and so is cited by its web address — supplies
intellectual background and nothing else. No result below is offered as reproducing
it.

**What exactly is being deleted.** A *Jacobian lens* maps a model's internal activity
patterns (its *activations*) onto one direction per word. *Projection removal* at
rank one ($k = 1$) subtracts out exactly the part of the activation that points along
one such direction, and leaves everything else untouched. Applied across a block of
consecutive layers, it is a surgical edit made while the model is simply running
forward: no weights change, no gradients are computed, no fine-tuning happens.

**The discipline.** Every stage locked in its pass/fail rule — including the exact
wording of the verdict — as runnable code before its first real run, and test-ran it
on deliberately wrong inputs to confirm that it refuses them and exits with INVALID.
Any measured cell built on fewer than 20 trials is declared UNDERPOWERED in advance
and makes no claim; a result that was pre-committed to be reported even if it comes
out null is still a reportable result. Each stage re-checks its predecessors' recorded
cells bit-for-bit before reading a single new one, so an instrument that has quietly
drifted cannot pass itself off as a finding.

---

## 2. Background and method

### 2.1 The anchor

At the last third of each model's workspace band, the earlier project recorded naming
scores of 0 out of 5, 0 out of 22 and 0 out of 8 qualifying items (at 0.5B / 1.5B /
3B) when the concept's own direction was removed — against a control direction from
the same category, which left naming largely intact. Its targeting readout came out
concept-SPECIFIC at 1.5B (+0.727 [+0.471, +0.868]), not demonstrated and UNDERPOWERED
at 0.5B (+0.200 [−0.264, +0.624]), and concept-SPECIFIC but UNDERPOWERED at 3B
(+1.000 [+0.541, +1.000]). The 0.5B and 3B cells were starved of data by a two-part
entry test that required the model both to name the concept correctly *and* to
successfully avoid saying it when asked to.

### 2.2 The instrument, and the design change

mute-map inherits the already-fitted lens files (never re-fitted for the core chain —
copied across with a SHA256 fingerprint recording exactly which file is which,
decision K3), the projection-removal operation itself, and the measurement protocol.
The one standing design change is a **naming-only entry test** (decision K2): because
the off-switch is a claim about *naming*, an item counts as measurable only if the
model names the concept correctly on the untouched run. Dropping the avoidance half
of the test is what lifts the qualifying cells from 5 / 22 / 8 items to statistically
usable sizes at every model size. It is a deviation the project owns, and
comparability with the original is preserved by re-running the original two-part
protocol exactly as it was (§4.1).

### 2.3 The oracle

The scoring rule (the *oracle*) is fixed and mechanical by standing policy: never a
language model acting as judge, never free-form text parsing. Through stages M0 and
M1 the rule was the **single most likely next word-piece** — the model's
highest-probability next *token* (a token is the chunk of text a model actually
emits, often a whole word but sometimes a fragment) had to be one of the concept's
single-token spellings, matching case exactly. Stage M2 widened it once, under
decision D9(b), locked into code in `oracle.py` before any M2 run: the concept counts
as produced if the first three word-pieces the model actually produces — taken one
after another, picking the most likely next piece at each step — once decoded and
stripped of leading spaces, **begin with the concept's spelling at a word boundary,
ignoring capitalisation**. It is a rule about how the answer *starts*, never about the word
appearing anywhere in it ("not France" counts as a miss); the word-boundary test is
"the next character is not a letter or digit" (so "Marseille" does not count as
"Mars"). `oracle.py` is shared byte-for-byte between its four users rather than
copied, so the rule cannot drift apart between them. The concept's probability weight
and the single-token outcome are both recorded alongside every cell, so comparability
with the original measurement never degrades.

### 2.4 The statistical rules

- **Wilson 95% intervals** on every measured cell — an error bar around a single
  percentage — and **Newcombe 95% intervals** on every difference between two arms of
  an experiment — an error bar around a gap between two percentages. A difference
  whose error bar includes zero is a null result and is reported as one. **A cell
  whose error bar overlaps its neighbour's is not a result.**
- **MIN_N = 20** trials per cell; below that, the verdict is declared UNDERPOWERED in
  advance.
- **Guards against degenerate runs.** For every arm of the experiment, the most common
  wrong opening word-piece is recorded; if its share reaches COLLAPSE_SHARE = 0.5 on
  an arm the verdict depends on, the whole run is declared DEGENERATE in advance. On
  the arm where the direction was actually removed, the guard is only a label, since
  everything collapsing onto one shared wrong answer is exactly what you would expect
  when the concept's own direction is deleted.
- **Cross-checks are scoped to the environment.** Reproducing results bit-for-bit is a
  property of the certified software stack (device `mps`, `torch==2.13.0`,
  `transformers==5.13.1`). On that stack, a mismatch makes the run exit INVALID; off
  it, the run is declared NOT A RESULT in advance.
- **Order of precedence, frozen into every verdict function:** NOT A RESULT beats
  DEGENERATE beats UNDERPOWERED beats the actual comparison.

---

## 3. Experimental setup

Three models throughout: **Qwen2.5-0.5B-Instruct**, **Qwen2.5-1.5B-Instruct** and
**Qwen2.5-3B-Instruct**, run locally on Apple's MPS graphics backend, forward-only,
at \$0. Every pass/fail rule requires *both* of the two decision-carrying models,
1.5B and 3B, to pass. **0.5B never carries a verdict**, and is read only under a
standing "does any direction cause damage here?" framing, because the earlier project
had already recorded non-targeted damage at that size.

The lens files were fitted by dim-stage's `fitter.py` using 100 prompts drawn from
WikiText (0.5B and 1.5B on a local Apple GPU, 3B on a rented RTX 4090) and copied
here with their SHA256 fingerprints recorded. The workspace bands, carried over
unchanged, are layers 9–21, 11–24 and 14–32; the split of each band into thirds
follows the carried-over convention, which gives the last third whatever layers are
left over (4/4/**5**, 4/4/**6**, 6/6/**7**).

| Stage | Question | Design | Cells / subject |
|---|---|---|---|
| **M0** | Is the ported instrument the same instrument? | Exact re-run of the anchor protocol, dual competence gate retained | 840 |
| **M1** | How much of the measurable vocabulary has an off-switch? | 60 concepts × 10 categories × 3 clue items = 180 items; conditions clean / primed_late / control_late | 540 |
| **M2** | Where does the switch live, and how much removal does it take? | Pre-registered 12-concept subset (36 items); three tiers, a stride-2 sliding window sweep including outside-band positions, and a partial-ablation dose curve λ ∈ {0, .25, .5, .75, 1} | 720 / 756 / 864 |
| **M3** | Does deleting A damage B? | Full 12 × 12 prime × probe matrix at the switch's home band, plus 18 out-of-subset control-direction cells | 486 |
| **M4** | Does deleting one concept spare the *other 48*? | The 12 characterized directions as primes; **all 180 battery items** as probes | 2,340 |

*In plain words: the five stages ask, in order — is our copy of the tool the same
tool (M0, 840 measured cells per model, re-running the original protocol exactly)?
Does the effect cover a decent chunk of vocabulary (M1, 60 concepts across 10
categories with 3 clue sentences each, compared under three conditions: untouched,
target's own direction removed at the late layers, and a control direction removed at
the late layers)? Where in the model does it live and how much removal is needed (M2,
a locked-in 12-concept subset, sliding a window across the layers two at a time and
dialling the removal strength through five settings from 0 to 1)? Does deleting
concept A hurt concept B (M3, every one of 12 deleted directions crossed with every
one of 12 tested concepts, plus 18 extra control cells)? And does deleting one
concept leave the other 48 alone (M4, the same 12 deleted directions but now tested
against all 180 items — 2,340 measured cells per model)?*

The 180-item battery was locked into `items/m1-battery.json` before any M1 run: 10
categories × 6 concepts × 3 clue sentences, with 53 of the concepts drawn from
vocabularies this line of projects had already measured and 7 top-ups from new lists
(flagged as such in the frozen file) filling gaps where a shipped list ran out. 60 of
the 180 items are the earlier project's own frozen items, reused word-for-word so
that every later run carries a live check against the original inside it. **The item
sets are hand-constructed rather than harvested from naturally occurring text** — a
deviation the project owns, carried forward from the first stage onward.

---

## 4. Results

Verdicts are quoted exactly as the measurement scripts emitted them. Bold marks the
two models that carry the verdicts.

![The five pre-committed gate contrasts, all three subjects. Each mark is the
recorded Newcombe point estimate and each bar the recorded Newcombe 95% interval;
none touches zero.](fig1-gate-contrasts.png)

**Figure 1 — every pre-committed pass/fail comparison stays clear of zero, on all
three models.** The dots and error bars are the `newcombe_*` triples that
`m1_battery.py`, `m2_depth.py` and `m3_matrix.py` recorded; nothing here is
recalculated. The pooled qualifying item counts are 38 / 61 / 44 for M1 and 28 / 34 /
32 for M2 and M3 (at 0.5B / 1.5B / 3B); the sizes of the individual arms behind each
comparison are in §§4.2–4.4. The three models are nudged apart vertically within each
row so they stay readable. M4's rule is a **level** bar rather than a comparison
between two arms, so it does not belong on this axis — it appears in Figure 5
instead.

### 4.1 M0 — the instrument is the same instrument

| Subject | Cells compared | Mismatches | Gated n | Anchor specificity readout reproduced |
|---|---|---|---|---|
| 0.5B | 840 | **0** | 5 | not shown, UNDERPOWERED (+0.200 [−0.264, +0.624]) |
| 1.5B | 840 | **0** | 22 | concept-SPECIFIC (+0.727 [+0.471, +0.868]) |
| 3B | 840 | **0** | 8 | concept-SPECIFIC, UNDERPOWERED (+1.000 [+0.541, +1.000]) |

*In plain words: on each of the three models, all 840 re-run cells matched the earlier
project's recorded cells with zero disagreements, and the original targeting readout
came out the same each time — undemonstrated and short of data at 0.5B (only 5 items
passed the entry test), a clean concept-specific result at 1.5B (22 items), and
concept-specific but short of data at 3B (8 items).*

Beyond what the pass/fail rule required, the recorded `concept_mass` probability
figures reproduced **exactly, on all 840 out of 840 cells on every model** — the
pinned software environment preserved not only which word-piece came out on top, but
the entire computed probability distribution down to the last bit. Every later stage
embeds a slice of previously recorded cells and grades those *first*: M2 and M3 each
re-certified 108 out of 108 M1 cells, and M4 re-certified **two** sets of saved
results at once — **255 out of 255 M1 cells and 468 out of 468 M3 cells, with
`concept_mass` exact on all 723 comparisons, on all three models** — before reading a
single new cell.

### 4.2 M1 — breadth

| Subject | Gated n / 180 | `primed_late` | `control_late` | control − primed [Newcombe 95%] | Verdict |
|---|---|---|---|---|---|
| 0.5B *(off-gate)* | 38 | 0/38 | 17/38 | +0.447 [+0.275, +0.603] | BREADTH-SPECIFIC |
| **1.5B** | 61 | 0/61 | 40/61 | **+0.656 [+0.517, +0.763]** | BREADTH-SPECIFIC |
| **3B** | 44 | 6/44 | 34/44 | **+0.636 [+0.443, +0.759]** | BREADTH-SPECIFIC |

*In plain words: of the 180 items, 38 / 61 / 44 passed the entry test on the three
models. With the concept's own direction removed at the late layers, the model still
named it in 0, 0 and 6 of those cases; with a control direction removed instead, it
named it in 17, 40 and 34. The gap between the two — 0.447, 0.656 and 0.636 — has an
error bar that stays well clear of zero on all three, so both verdict-carrying models
come out BREADTH-SPECIFIC; 0.5B's row is marked off-gate and never carries a verdict.*

**M1 verdict: BREADTH-SPECIFIC at 1.5B AND 3B.** The effect is not a quirk of the
handful of items it was first spotted on.

**How common it is remains UNDERPOWERED, exactly as declared in advance.** Counting by
concept rather than by item, 4 of 8 (0.5B), 9 of 11 (1.5B) and 6 of 8 (3B) concepts
show the full hard-switch pattern. All three carry the pre-declared UNDERPOWERED tag —
the concept-level cell was named in advance as the one cell in this stage that would
fall below the 20-trial minimum — and none of them supports a claim.

**0.5B came out BREADTH-SPECIFIC too, and that undercuts a story we inherited.** The
original 0.5B cell showed no targeting, on just 5 qualifying items. The naming-only
entry test lifts 0.5B to 38 items, and the gap's error bar stays clear of zero. The
honest reading, which was written into the deviations table before the run: the
original 0.5B null was **short of data, not evidence that nothing was there**, and this
line of projects' "targeting emerges as models get bigger" story weakens accordingly.
M1 makes no claim about model size; it reports that all three models show the switch
once each of them has enough data to see it.

#### 4.2.1 The owned bound: the readout, not the model, sets the coverage

The entry test admitted only 38 / 61 / 44 of the 180 items, and the main reason is a
property of the scoring rule rather than of the models. Under the single-word-piece
rule, a concept can only be scored if its spelling at the answer position is a single
word-piece; **26 of the 60 roster words break into more than one piece in their bare
form**, and the model usually spells them with no leading space, so its first piece is
a fragment (`'Mer'`, `'Viol'`, `'Fl'`) that the rule counts as a miss. Whole categories
therefore admit almost nothing — **planets and musical instruments admitted 0 items on
all three models** — so the per-category picture is partly a map of how the tokenizer
happens to chop up words rather than a map of concepts. The three-word-piece texture
measures that cost instead of assuming it: among items that *failed* the entry test,
the model still said the concept within three word-pieces in **35 of 142 (0.5B), 54 of
119 (1.5B) and 80 of 136 (3B)** cases — competence that the primary scoring rule simply
cannot see.

Two things put limits on this limit. It does not threaten the pass/fail rule: the
comparison is computed *within* the set of items that passed, and passing is a property
of the untouched run alone, decided before any direction is removed. And the same
texture shows the bias **works against the finding, not for it** — on the qualifying
cells, under the control condition the model said the concept within three word-pieces
17 of 17, 46 of 40 and 36 of 34 times, so at both verdict-carrying models the primary
rule *understates* how much the control arm survived, while under the target-removed
condition it said the concept 0 of 38, 0 of 61 and 6 of 44 times, exactly matching the
primary count. If anything, the comparison arm is being scored too harshly.

#### 4.2.2 The re-score, published beside — not instead of — M1's numbers

Fixing the instrument belonged in a decision, not in a results section. M2 opened by
widening the scoring rule (decision D9(b)) and publishing a **clearly labelled
reanalysis** of M1's *same recorded cells* under the new rule (decision D10(a)). No
model was run: the re-score is purely a function of the saved M1 files, and the script
refuses to write anything unless it first reproduces M1's published single-word-piece
comparison exactly — which it does, on all three models. **M1's verdict of record is
unchanged.**

| Subject | Gated n (first-token → widened) | `primed_late` | `control_late` | control − primed [Newcombe 95%] |
|---|---|---|---|---|
| 0.5B *(off-gate)* | 38 → 69 | 0/69 | 33/69 | +0.478 [+0.353, +0.594] |
| **1.5B** | 61 → 105 | 0/105 | 80/105 | **+0.762 [+0.665, +0.833]** |
| **3B** | 44 → 116 | 12/116 | 92/116 | **+0.690 [+0.582, +0.767]** |

*In plain words: widening the scoring rule roughly doubles the number of items that can
be scored (38 → 69, 61 → 105, 44 → 116). Even with all those extra items in, the model
still almost never names the concept when its own direction is deleted (0, 0 and 12
hits) while naming it often when a control direction is deleted instead (33, 80 and
92), and the gap gets larger, not smaller.*

The two dark categories light up — planets go from 0 to 7 / 8 / 15 items and musical
instruments from 0 to 2 / 8 / 13, out of 18 items each — and the comparison survives in
the *harder* direction: the control condition gains far more items than the
target-removed condition does, and at 1.5B the target-removed arm stays at exactly 0
across all 105 qualifying items. Under the single-word-piece rule one could have argued
that the mute was partly an artefact of scoring fragments as misses. It is not.

A separate worry — that the comparison might be carried by the 60 items the earlier
project itself picked — is closed here under **both** scoring rules. On the **120
newly written items alone**, the gap's error bar stays clear of zero on all three
models: +0.278 / +0.545 / +0.478 under the single-word-piece rule and +0.389 / +0.714 /
+0.629 under the widened one. The reused batch scores higher, which is what you would
expect from items chosen against a model that could already name them, but the new
batch stands on its own.

### 4.3 M2 — localization and dose

| Subject | Gated n / 36 | `primed_early` | `primed_middle` | `primed_late` | early − late [Newcombe 95%] | middle − late [Newcombe 95%] | Verdict |
|---|---|---|---|---|---|---|---|
| 0.5B *(off-gate)* | 28 | 17/28 | 17/28 | 0/28 | +0.607 [+0.388, +0.764] | +0.607 [+0.388, +0.764] | LATE-LOCALIZED |
| **1.5B** | 34 | 29/34 | 27/34 | 0/34 | **+0.853 [+0.668, +0.936]** | **+0.794 [+0.603, +0.897]** | LATE-LOCALIZED |
| **3B** | 32 | 27/32 | 25/32 | 3/32 | **+0.750 [+0.531, +0.857]** | **+0.688 [+0.463, +0.812]** | LATE-LOCALIZED |

*In plain words: doing exactly the same deletion in the early third or the middle third
of the band leaves most naming intact at 1.5B and 3B, and costs 0.5B about four items in
ten (17, 29 and 27 hits early; 17, 27 and 25 middle) — but
doing it in the late third drives naming to almost nothing (0, 0 and 3). The gaps
between early and late, and between middle and late, all have error bars clear of zero,
so both verdict-carrying models come out LATE-LOCALIZED; 0.5B shows the same shape but
is read off-gate.*

**M2 verdict: LATE-LOCALIZED at 1.5B AND 3B.** The qualifying item counts were
*predicted before the runs* — 28 / 34 / 32, because passing the entry test is a
property of the fixed, untouched run that M1 had already recorded — and they came in at
28 / 34 / 32. A disagreement would have been treated as a failed cross-check and an
INVALID exit, not as a surprise about statistical power.

![Naming survival at each sliding-window position, three subjects. Marks are the
recorded rates with their recorded Wilson 95% intervals; the shaded region is each
subject's workspace band; the diamond is the reused late-third gate cell.](fig2-localization.png)

**Figure 2 — the switch is a cliff at the end, sitting on a floor; it is not a
band-wide effect.** Each mark is one recorded window position: the share of items still
named, with its recorded Wilson 95% error bar, measured on the same qualifying items
throughout (28 / 34 / 32 items at 0.5B / 1.5B / 3B), which means the positions are
correlated with each other because they share items. The window is 5 / 6 / 7 layers
wide and moves 2 layers at a time, both exactly as recorded; the shaded region is the
recorded workspace band (layers 9–21, 11–24, 14–32) and the diamond marks the
late-third cell the verdict is computed on. **No line joins the marks** — the positions
between two window starts were never measured. This sweep is descriptive and never
carried a verdict.

| Subject | naming / gated n by window start |
|---|---|
| 0.5B (width 5, n = 28) | L0°15, L1°15, L3°14, L5 16, L7 16, L9 16, L11 19, L13 15, L15 13, **L17\* 0**, L18 0 |
| 1.5B (width 6, n = 34) | L0°33, L1°32, L3°27, L5°28, L7 28, L9 27, L11 25, L13 23, L15 23, L17 1, **L19\* 0**, L21 0 |
| 3B (width 7, n = 32) | L0°32, L2°32, L4°31, L6°30, L8 30, L10 29, L12 29, L14 25, L16 25, L18 25, L20 24, L22 16, L24 11, **L26\* 3**, L28 1 |

*In plain words: each entry is "window starting at layer N: this many items still
named". Reading left to right, naming holds up almost everywhere and then falls off a
cliff near the end — at 1.5B it goes 23 items at layer 15, then 1 at layer 17 and 0 at
layer 19; at 3B it slides more gradually, 24 → 16 → 11 → 3 → 1 across the last five
positions.*

*(° marks a window with no layer inside the band, \* the reused late-third cell that
the verdict is computed on.)*

Removing the *same* direction at the *same* strength anywhere before the late third
leaves most naming intact; only the late window drives it to the floor. The transition
is sharp at 0.5B and 1.5B and noticeably more gradual at 3B, which descends 24 → 16 →
11 → 3 across four positions — visible in Figure 2 as a staircase rather than a single
step. Moving the window 2 layers at a time pins the 1.5B edge down to somewhere between
window starts at layer 15 and layer 17.

**Deleting a direction outside the band is cheap at the larger models and expensive at
0.5B**, quoted as ranges rather than best cases: across windows with no layer inside the
band at all, naming survives in 27–33 of 34 items at 1.5B (3–21% lost), 30–32 of 32 at
3B (0–6% lost) and 14–15 of 28 at 0.5B (46–50% lost). Only 3B has a genuinely
cost-free position outside the band; 1.5B's best still costs one item and its worst
loses 21% — the same depth-blind damage that 0.5B shows, an order of magnitude smaller
but not absent. **This is why 0.5B's LATE-LOCALIZED reading sits on a raised floor**:
its late cell is a genuine cliff (0 of 28 against a baseline of roughly 15 of 28), so
the shape of the localization is real, but the "everything else is harmless" half of the
story fails there — and that is what the differing floor heights across the three panels
in Figure 2 are showing.

![Naming survival and mean concept mass at the five frozen λ values, three subjects.
Marks only; no curve is fitted through them.](fig3-dose.png)

**Figure 3 — a dimmer, not a step; and the knee moves rightward as models get bigger.**
Left: the recorded naming rate at each removal strength $\lambda$ with its recorded
Wilson 95% error bar, on the same qualifying items as the sweep (28 / 34 / 32). Right:
the recorded average probability weight on the concept, scoped as recorded to those
qualifying items whose bare spelling is a single word-piece (22 / 24 / 21 items) —
plotted as a bare dot because no error bar for it was ever recorded. $\lambda = 0$ is
the reused untouched cell and $\lambda = 1$ the reused late-removal cell. The
horizontal axis is the frozen five-value grid; **nothing is drawn between grid
points**, and the marks are nudged sideways only so that three models all sitting at
1.0 when $\lambda = 0$ remain visible.

| λ | 0.5B naming (mass) | 1.5B naming (mass) | 3B naming (mass) |
|---|---|---|---|
| 0 | 28/28 (0.833) | 34/34 (0.913) | 32/32 (0.942) |
| 0.25 | 13/28 (0.362) | 20/34 (0.594) | 21/32 (0.782) |
| 0.5 | 0/28 (0.022) | 3/34 (0.115) | 10/32 (0.342) |
| 0.75 | 0/28 (0.001) | 1/34 (0.037) | 4/32 (0.197) |
| 1 | 0/28 (0.000) | 0/34 (0.017) | 3/32 (0.120) |

*In plain words: as you remove more of the direction (from none of it at 0 to all of it
at 1), naming does not snap off at some threshold — it slides down through intermediate
values, and so does the probability the model puts on the concept. At 1.5B, for example,
naming goes 34 → 20 → 3 → 1 → 0 while the probability weight goes 0.913 → 0.594 → 0.115
→ 0.037 → 0.017. The bigger the model, the further along the dial the collapse happens.*

Partial removal produces intermediate naming rates and intermediate probability weights
at every model size. **Nothing here behaves like an on/off switch that flips at a
threshold**, which answers a question the project's kickoff brief had left open. The
knee of the curve is steep and appears to move rightward as models get bigger — the
brief's half-mute points are $\lambda \approx 0.23 / 0.29 / 0.36$ — but those three
figures are **straight-line estimates drawn between two grid points, not
measurements**: the grid is frozen at five values and nothing was re-fitted. They are
quoted here and plotted nowhere, which is why Figure 3 shows five dots and no curve.
The probability-weight channel tells the same story without any estimating in between:
at $\lambda = 0.5$ the remaining weight is 0.022 / 0.115 / 0.342. The naming readout can
only take discrete steps while the probability weight moves smoothly; they agree with
each other, so the dimmer reading does not rest on the naming readout alone.

**The pre-registered groups of concepts did their jobs**, including the one picked
because it was expected to fail. The hard-switch core sat at 0 of 3 items named under
late removal on every model; the group that the widened rule unlocked was muted
throughout; and the leaky group leaked at 3B, where it was predicted to. The
deliberately non-targeted counter-example `silver` broke the pattern exactly as
designed: at 1.5B it passes the entry test 3 of 3 and reads 0 of 3 under its own
direction's removal **and 0 of 3 under the control direction too** — the control
direction mutes it as well — with 1 of 3 under early removal and 0 of 3 under middle
removal, i.e. damaged at *every* depth. The pooled curves include it.

### 4.4 M3 — the specificity matrix

| Subject | Gated n / 36 | Diagonal | Off-diagonal | clause (1) off − diag [Newcombe 95%] | Within-category | Restricted diagonal | clause (2) [Newcombe 95%] | Verdict |
|---|---|---|---|---|---|---|---|---|
| 0.5B *(off-gate)* | 28 | 0/28 | 279/308 | +0.906 [+0.779, +0.934] | 80/96 | 0/24 | +0.833 [+0.670, +0.895] | MATRIX-SPECIFIC |
| **1.5B** | 34 | 0/34 | 363/374 | **+0.971 [+0.867, +0.983]** | 95/100 | 0/28 | **+0.950 [+0.814, +0.978]** | MATRIX-SPECIFIC |
| **3B** | 32 | 3/32 | 343/352 | **+0.881 [+0.731, +0.943]** | 97/101 | 2/29 | **+0.891 [+0.730, +0.947]** | MATRIX-SPECIFIC |

*In plain words: the "diagonal" is the case where the direction deleted and the concept
tested are the same word — naming collapses there (0, 0 and 3 hits). The "off-diagonal"
is every case where they differ — naming survives almost untouched (279 of 308, 363 of
374, 343 of 352). The first pass/fail clause is the gap between those two, and it is
huge with an error bar clear of zero. The second clause repeats the comparison using
only pairs from the same category — the hardest case — and it still holds (95 of 100
versus 0 of 28 at 1.5B, 97 of 101 versus 2 of 29 at 3B). Both verdict-carrying models
come out MATRIX-SPECIFIC; 0.5B shows the same shape but is read off-gate.*

**M3 verdict: MATRIX-SPECIFIC at 1.5B AND 3B**, on both of the two pre-committed
clauses. Clause (2) narrows the comparison to *same-category* pairs — the case the
earlier project's single control actually tested — so the pooled arm's heavy load of
cross-category pairs did not carry the verdict. **No model carries the ON A DAMAGED
FLOOR qualifier**: the collateral floor reads 25 of 28 [0.728, 0.963], 33 of 34 [0.851,
0.995] and 31 of 32 [0.843, 0.994], all far above the pre-set floor of 0.5 — including
at 0.5B, which the brief had left open. Every pre-registered item count came in
exactly, every pooled cell clears the 20-trial minimum, and no arm collapsed onto a
single wrong answer. **126 of the matrix's 132 ordered off-diagonal pairs had never
been measured before**; the other 6 are the earlier stage's own control cells.

![The 12 × 12 prime × probe matrix at each of the three subjects. Rows are the deleted
direction, columns the probed concept; each cell is annotated with its recorded hits over
n, and shaded by the recorded naming-survival rate.](fig4-matrix.png)

**Figure 4 — a dark diagonal on a nearly white grid.** Every square is one recorded
matrix cell: rows are the deleted direction A, columns the tested concept B, the label
is the recorded hits-out-of-attempts, and the shade is the recorded rate (dark = muted,
light = spared). The number of attempts per square is however many of B's items passed
the entry test, **never more than 3, so no individual square carries a verdict** — the
verdict is computed on the pooled arms in the table above (28 / 34 / 32 qualifying
items). Because every square is labelled with its own counts, this figure doubles as its
own table. Added up across the grid, the pooled off-diagonal arm misses **11 of its 374
item observations at 1.5B, 9 of 352 at 3B and 29 of 308 at 0.5B** (each square holds no
more than 3 of those observations). The extra colour at 0.5B is the category-block
effect described in §4.4.2; `silver`'s column is the visibly fragile stripe at 1.5B and
3B.

A sanity check that avoids double-counting items — collapsing each item down to "does it
survive *all 11* deletions of other concepts' directions?" — agrees with the pass/fail
rule everywhere: 19 of 28, 29 of 34 and 27 of 32, against a diagonal of 0 of 28, 0 of 34
and 3 of 32, giving gaps of +0.679 [+0.458, +0.821], +0.853 [+0.668, +0.936] and +0.750
[+0.531, +0.857]. There is no case where the stricter per-item numbers would have had to
be quoted instead of the pooled ones. The graded probability channel agrees with the
yes/no one: average probability weight on the concept reads 0.833 / 0.913 / 0.942 when
untouched, 0.0001 / 0.017 / 0.120 on the diagonal, and 0.773 / 0.889 / 0.937
off-diagonal.

#### 4.4.1 Re-attribution (a): non-specificity has a direction

`silver` entered the subset as the pre-registered **non-targeted counter-example** — the
one concept whose *control* direction had muted it back in M1 — and the brief expected
its row to drag the pooled off-diagonal numbers down. Its row does nothing of the sort.
**Deleting silver's direction damages nothing, at any model size** (27 of 27, 31 of 31,
31 of 31) — its row in Figure 4 is uniformly pale. What is true is the mirror image:
silver's *column* is the most fragile in the matrix (7 of 11, 27 of 33, 6 of 11 under
other concepts' deletions). The misses pile up on a few fragile tested concepts rather
than spreading out from a few damaging deleted directions — at 1.5B all 11 off-diagonal
misses land on `silver` (6), `Canada` (3), `piano` (1) and `violin` (1).

This is a **change of scope, not a retraction**. M1 and M2 each sampled *one cell of
silver's column* and read it as a property of silver's row; a design with a single
control could not have told the two apart. M1's and M2's published numbers stand; what
changes is what the label "non-specific" was ever a fact *about*. A row and a column are
indistinguishable in a single cell and nothing alike in a whole grid, which is why
Figure 4 is what makes the distinction visible.

#### 4.4.2 The nulls M3 recorded

**Category-block collateral has an error bar clear of zero at 0.5B and dissolves by
1.5B.** Comparing collateral damage within a category against collateral damage across
categories gives a difference of **+0.105 [+0.032, +0.196]** at 0.5B — clear of zero —
but **+0.028 [−0.010, +0.091]** at 1.5B and **+0.020 [−0.016, +0.079]** at 3B. Both of
those straddle zero, and by this project's own rule a cell whose error bar overlaps its
neighbour's is not a result. So: at 0.5B, deleting one country's direction measurably
damages *other countries*; by 1.5B that block has dissolved into noise. §4.5.1 comes
back to this, and that revisit is exactly why this null is stated at precisely this
strength and no stronger.

**The leaky group replicated, on the diagonal, at 3B only.** The only diagonal cells
anywhere that are not zero are `Egypt` at 2 of 3 and `October` at 1 of 2, both at 3B —
precisely the two concepts pre-registered as the leaky-switch group, and the only two
dark-but-not-black diagonal squares in Figure 4's right-hand panel. The mute is not
perfect for those two words at the largest model, and the pre-registration named them in
advance.

**Asymmetry is real but sparse**: 19 / 7 / 8 of the 66 unordered pairs differ at all
between "delete A, test B" and "delete B, test A", and at both verdict-carrying models
the largest gaps are dominated by `silver` appearing on the tested side.

### 4.5 M4 — the vocabulary collateral strip (the close-out stage)

M3's nearly white grid showed that deleting France leaves the other *eleven* subset
concepts alone. It showed nothing about the other 48. M4 keeps the same 12 characterized
directions as the **deleted directions** and widens the **tested concepts** to all 60 in
the battery: **2,340 measured cells per model**, every one of them at the identical late
third, full removal strength, rank one. The pass/fail rule is a **level** bar rather
than a comparison between two arms — M3 already settled the comparison — and it has a
single clause:

> A model counts as **VOCAB-SPARING** if, among the qualifying items that are **not**
> in the 12-concept subset, the share that **survives all 12** subset-direction
> deletions has a Wilson 95% lower bound at or above **0.5**. The bar is read **only
> if** the 468 cells recorded by M3 and the 255 recorded by M1 first reproduce their
> recorded outcomes bit-for-bit.

| Readout | 0.5B *(off-gate)* | **1.5B** | **3B** |
|---|---|---|---|
| Gated items (full roster) | 69 | 105 | 116 |
| **Gate arm** (gated non-subset) | 41 | 71 | 84 |
| **Survives all 12** | 11/41 = 0.268 | **51/71 = 0.718** | **63/84 = 0.750** |
| Wilson 95% | [0.157, 0.419] | **[0.605, 0.810]** | **[0.648, 0.830]** |
| vs the pre-registered bar 0.5 | fails | **clears** | **clears** |
| Residual-conservative (fail in place) | 11/41 = 0.268 | 49/71 = 0.690, lower 0.575 | 62/84 = 0.738, lower 0.635 |
| **Concept-level collapse** | 4/23 = 0.174, lower 0.070 | **24/41 = 0.585, lower 0.434** | **26/43 = 0.605, lower 0.456** |
| Pre-registered ceiling | 35/41 ✓ | 69/71 ✓ | 82/84 ✓ |
| Verdict | `not shown` | **VOCAB-SPARING — AS-SCORED ONLY** | **VOCAB-SPARING — AS-SCORED ONLY** |

*In plain words: of the items that passed the entry test, 41 / 71 / 84 involve concepts
outside the 12-concept subset — those are the ones the rule is read on. Of those, 11, 51
and 63 came through all twelve deletions untouched. At 1.5B and 3B the bottom of the
error bar (0.605 and 0.648) sits above the 0.5 bar, so the rule is cleared; at 0.5B it
does not. A stricter variant that counts ambiguous cases as failures still clears at
both. But counting one yes/no per concept instead of per item, the bottom of the error
bar drops to 0.434 and 0.456 — below the bar — which is why the verdict is labelled
AS-SCORED ONLY.*

![The three pre-registered floor reads at each subject, against the frozen 0.5 bar.
The item-level interval's lower bound sits above the bar at both gate-bearing subjects;
the concept-level interval's lower bound sits below it.](fig5-m4-floors.png)

**Figure 5 — why the verdict carries AS-SCORED ONLY.** Each mark is one recorded floor
reading with its recorded Wilson 95% error bar, set against the recorded bar of 0.5.
The denominators are the ones in the table above: the item-level and
residual-conservative readings are out of 41 / 71 / 84 items in the decision arm, and
the concept-level reading is out of 23 / 41 / 43 non-subset concepts that have at least
one qualifying item. **The rule reads the bottom of the error bar, not the dot in the
middle** — so what matters visually is where each bar *ends*, not where its dot sits. At
1.5B and 3B, the item-level bar ends above the line and the concept-level bar ends below
it. The three models are nudged sideways within each reading.

**M4 verdict: VOCAB-SPARING at 1.5B AND 3B — AS-SCORED ONLY.** The scope is part of the
result, not a footnote to it. **The item-level floor clears the 0.5 bar; the
concept-level floor's Wilson lower bound does not (0.434 at 1.5B and 0.456 at 3B).** The
concept-level reading — one yes/no per concept instead of one per item — was
pre-registered before any new cell was run, and the brief pre-committed those as **the
honest numbers to quote**. An amendment made after the freeze but ratified before the
run is what puts them *inside* the verdict label rather than in the surrounding prose:
prose is not what gets quoted, the label is. The stricter residual-conservative reading
clears at both models, so exactly one of the two pre-registered conservative readings
fired.

Every pre-registered count landed exactly: decision arms of 41 / 71 / 84, concept counts
of 23 / 41 / 43, and ceilings of 35 of 41, 69 of 71 and 82 of 84 with precisely the
named misses (`july-1`, `april-1`, `april-3`, `gold-1/2/3` at 0.5B; `july-3`, `venus-3`
at 1.5B; `guitar-2`, `neptune-1` at 3B) — all knowable in advance because the strip
physically re-runs the 255 cells recorded by M1 and the 468 recorded by M3 (**633 of the
2,340** once the 90-cell overlap is counted only once) and grades them first. No
degeneracy guard fired on the decision-carrying arm: the shares of the most common wrong
opening word-piece were 0.022 / 0.011 / 0.011 against a threshold of 0.5.

#### 4.5.1 Re-attribution (b): category-block collateral does not dissolve with scale

M4 reverses M3's null from §4.4.2, and the reason is what went into the arms.

| Subject | Within-category | Cross-category |
|---|---|---|
| 0.5B | 5/22 | 382/470 |
| **1.5B** | **22/29 = 0.759** | **769/823 = 0.934** |
| **3B** | **35/53 = 0.660** | **913/955 = 0.956** |

*In plain words: when the deleted direction and the tested concept come from the same
category, survival is much lower (76% at 1.5B, 66% at 3B) than when they come from
different categories (93% and 96%). Deleting a direction really does damage other
concepts in the same category — here across ten categories, not just one — and the
effect does not go away in the bigger models.*

**Category-block collateral is real across the wider vocabulary and does not dissolve as
models get bigger.** M3 saw it dissolve by 1.5B — but M3's within-category arm was **30
of its 34 pairs countries**, a single tight block sampled twelve different ways. The
strip's within-category arm samples ten categories. Again: a **change of scope, not a
retraction**. M3's published numbers stand; what was measured there was a fact about
that arm's composition.

#### 4.5.2 Finding 1 generalizes out of sample

![Per-prime and per-probe survival rates at the two gate-bearing subjects. The twelve
deleted directions cluster tightly near the top of the scale; the probed concepts spread
down to 0.5.](fig6-collateral-asymmetry.png)

**Figure 6 — collateral damage concentrates on fragile targets, not on destructive
deletions.** Left panels: each of the 12 deleted directions plotted at its recorded
survival rate across the decision arm
(`row_profiles[A].collateral_non_subset`, 71 items at 1.5B and 84 at 3B). Right panels:
each qualifying tested concept plotted at its recorded survival rate under the other
concepts' deletions (`column_profiles[B].fragility`; the denominator is 12 deletions ×
that concept's qualifying items, or 11 × for a subset concept, whose own direction is
excluded — so denominators differ from mark to mark and every labelled mark carries its
own). Marks are ordered by their own recorded rate; the ordering itself carries no
meaning. Only the three most fragile tested concepts per model are labelled; the rest
are in the recorded profile files and the script's printout.

Collateral damage still concentrates on fragile **tested concepts**, not on destructive
**deleted directions**. **No deleted direction is a wrecking ball**: at 1.5B every row
lands between 63 and 67 of 71, at 3B between 77 and 83 of 84 — those are the tight
left-hand clusters. But specific tested columns collapse — `copper` at 6 of 12 and
`mosquito` at 8 of 12 at 1.5B; `eagle` at 8 of 12, `platinum` at 9 of 12 and `trumpet`
at 18 of 36 at 3B — while **32 of 53 qualifying columns at 1.5B and 33 of 55 at 3B take
zero collateral damage across all 12 deletions**. That split into two clumps — a dense
stack at 1.0 with a thin tail reaching down to 0.5 — is exactly what makes the
item-level and concept-level statistics diverge, because a concept with even one fragile
item fails the concept-level yes/no outright. It is the visual answer to why Figure 5's
two readings land on opposite sides of the bar.

#### 4.5.3 The nulls and divergences M4 recorded

**0.5B reads `not shown` off the decision path, at 11 of 41 = 0.268 [0.157, 0.419]** —
the **first measured divergence between how robust the pre-registered subset is and how
robust the wider roster is**. 30 of 0.5B's 41 decision-arm items (73%) are damaged by at
least one deletion, against 28% at 1.5B and 25% at 3B. Read under the standing
"does any direction cause damage here?" framing, never as a verdict claim, and
consistent in advance with M3's own 0.5B subset failing this same bar on its own
statistic (19 of 28, lower bound 0.4934).

**The two statistics disagree by design, and 0.5B shows it starkly.** The M3-comparable
per-cell average floor on the same 0.5B cells reads **32 of 41 → [0.633, 0.880]** —
comfortably above 0.5 — while the twelve-way "survives all of them" reading on those
same cells reads 0.268. Same model, same cells, opposite sides of the same number. That
is why the stage refused to inherit M3's 0.5 and wrote the per-cell equivalent
($0.5^{1/12} \approx 0.944$) into its frozen wording.

**The five pre-registered cross-mention cells did not carry the verdict, as predicted.**
At 3B all four verdict-carrying cells named their concept; at 1.5B three named it and
`China→jade-1` missed; `Egypt→beetle-2` never passes the entry test on any of the three
models.

**The set of ambiguous residual cases was larger in the direction-removed arm than in
the untouched arm.** The untouched arm's decision-arm residuals were the pre-computed 0
/ 2 / 2, but the run recorded **0 / 27 / 21** residual cells in total (0 / 26 / 21 of
them in the decision arm), all on `beetle`, `butterfly` and `trumpet` — the three
concepts named in the frozen scoring rule's own documentation. That is what the
pre-registered stricter selector was written for, and why the conservative reading moves
the number at all: 51 → 49 at 1.5B, 63 → 62 at 3B.

**The claim is that the mute spares the *measurable* vocabulary, and it is said exactly
that way.** **25 / 7 / 5 of the 48 non-subset concepts admit zero items.** That is a
*selection by competence* — the model answers something else, or answers correctly but
behind a qualifier that the opening-word rule refuses, or misses on word endings — and
it plausibly loads the sample with robust concepts, biasing the floor **upward**. The
0.5 bar itself is new, deliberately lenient and not calibrated against anything:
pre-registered before any new cell was run, fitted to none of them, with the per-cell
equivalent (≈ 0.944) written into the frozen wording itself so that it cannot be quoted
as if it were M3's floor.

---

## 5. Discussion

**What was measured.** Subtracting out a single concept's lens direction, at the last
third of the workspace band, reliably stops small Qwen2.5 models from saying that word.
The effect is broad across a 60-concept battery, tied to the last third rather than to
the band as a whole, graded rather than all-or-nothing as the removal is dialled up, and
precisely targeted across a full 12 × 12 grid on both of its clauses — and it mostly
leaves the wider vocabulary alone, with the exact scope of that "mostly" stated on the
label.

**What the scope means.** The bar that VOCAB-SPARING names permits real damage: at the
rate actually observed at 1.5B, 20 of 71 measurable items are still damaged by at least
one of the twelve deletions. The concept-level reading — "is *this concept* untouched?"
rather than "is *this item* untouched?" — sits below the bar at both verdict-carrying
models. Both readings were pre-registered, neither was picked after seeing the data, and
the honest one-line summary is the one this paper leads with.

**What the nulls mean.** Three of them matter. (i) The dose curve failing to look like
an on/off switch is a positive statement about mechanism: the ability to emit the word
degrades continuously with how much of the direction you take away. (ii) M3's
category-block null was a genuine null *for that particular arm*, and M4 shows why
reading it as a general one would have been a mistake. (iii) M1's how-common-is-it cells
are UNDERPOWERED by prior declaration and support no claim about how many concepts have
switches — only that the pooled comparison holds.

**The two re-attributions are the most transferable result here.** Neither is a
discovery; both correct what an earlier measurement was a fact *about*. A single control
cell told us `silver` was non-targeted; the matrix showed that this was a fact about
silver's *column*, and that its row damages nothing at any model size. A
countries-dominated within-category arm told us that category-block collateral dissolves
as models get bigger; the strip showed that this was a fact about *what went into that
arm*. The lesson is structural rather than mechanistic: **a single control cell measures
a cell, not a row**, and what an arm is made of is part of what it measured. Both were
findable only because every stage re-ran its predecessor's recorded cells instead of
taking them on trust.

**The residual that cannot be validated.** Nothing here establishes *why* the last third
is special, whether this direction is the same object the seed paper's lens is about, or
whether any of this holds above 3B. The sweep's coverage above the band is structurally
thin — no window ever sits entirely above the band — so "the switch is late" is
well-measured on its early side and only weakly probed on its far side. The correlation
structure among the deleted directions is measured but not modelled. The extension to 7B
and the question of lexical versus semantic scope ("can the model still say *French*, or
*Paris*?") were both designed, declined for this repository, and banked for later.

---

## 6. Threats to validity

Each stage's own table of owned deviations survives here in full. These are disclosures
made before or at the time of the runs, not concessions extracted afterwards.

### 6.1 Standing deviations (all stages)

| Deviation | From | Owned reason |
|---|---|---|
| Model scale 0.5B–3B rather than a frontier model | the seed paper's setting | The lineage's standing frame; every claim is scoped to these three subjects |
| Anchor is our own recorded result, not a paper claim | lineage precedent | This is the lineage's first original characterization; framing stated in the kickoff brief and never softened |
| Lenses copied, never refit for the core chain | — | Decision K3; SHA256 provenance recorded; a hash mismatch after any refit means it is not the anchor instrument |
| **Naming-only competence gate** | the anchor's dual gate | Decision K2: the switch is a naming claim, and the avoidance half is what starved the anchor's cells. Measures the switch, not exclusion capacity; comparability preserved by M0's exact dual-gate re-run |
| **Constructed item sets**, frozen pre-run | naturally occurring text | 60 items reused verbatim from the predecessor's frozen set (and used as a live anchor check); 120 newly authored to a fixed recipe. The reuse stratum runs higher — reported separately (§4.2.2) |
| Item-level pooling in gate cells | an independence assumption | Items within a concept correlate; per-concept and per-category views reported beside, and effective-n collapses reported at M3 and M4 |
| Paired arms scored with an independent-samples Newcombe | the paired design | For positively correlated paired arms this **widens** the interval, so it can cost power but cannot manufacture a false positive |
| MIN_N applied to raw n | an effective n | Not discounted for the within-concept clustering the row above already owns |

*In plain words: the standing compromises are — these are small models, not a frontier
one; the reference point is our own earlier measurement rather than anyone's published
claim; the lens files were copied rather than re-fitted, with fingerprints recorded to
prove it; the entry test asks only that the model can name the concept, not that it can
also avoid saying it; the test items were written by hand and locked before any run; the
statistics count items rather than concepts, which slightly overstates how much
independent evidence there is; the error bars on differences are computed with a formula
meant for unpaired data, which — when the two arms move together, as these do — makes
them wider than they need to be and so can only cost sensitivity, never invent a false
result; and the 20-trial minimum is applied to
raw counts, not to a smaller count adjusted for that clustering.*

### 6.2 Stage-specific deviations

| Stage | Deviation | Owned reason |
|---|---|---|
| M1 | 7 new-list concept words beyond the measured-only rule | The kickoff sanctions "extended by new frozen lists"; all 7 marked in the frozen file; the competence gate does the honest filtering |
| M1 | Word-prefix + explicit forbidden-form leak guard | With 60 short concepts a substring test makes "plant" a leak for "ant"; all 60 reused items pass the stricter guard unchanged |
| M2 | **Widened primary oracle** (span prefix, case-insensitive) | Fixes tokenizer geometry, not semantics; the first-token outcome is recorded beside every cell; M1's published numbers stand and the re-score is published beside them as a labelled reanalysis |
| M2 | Partial-projection operator is new code | Lives in the M2 runner, read-back generalized to survivor = (1−λ)·original within tolerance, unit-covered |
| M2 | Sliding windows have no precedent in the anchor protocol | The point of the stage; the three tier cells keep the anchor-comparable frame beside the new map |
| M2 | **The tier arms do not ablate the same number of layers** (4/4/5, 4/4/6, 6/6/7) | The ported band-thirds convention gives the late tier the remainder, so the localization gate compares a 4-layer ablation against a 6-layer one at 1.5B: what differs is depth **and** intervention size. Retired descriptively by the constant-width sweep — at 1.5B the width-6 window at L11–L16 scores 25/34 against the late window's 0/34, and at 3B the width-7 L12–L18 scores 29/32 against 3/32 — but the *gate* was computed on unequal-width arms, and that is stated rather than implied |
| M2 | Mass channel scoped to single-token bare spellings | The readout-unlocked stratum has no single-token bare form, so its mass is floor-pinned by construction; that stratum's dose curve is binary-only |
| M2 | Directions keyed to the leading-space unembed row for multi-token-bare concepts | No bare single token exists for 26 roster words; the space-keyed late ablation is measured to mute the bare emission all the same |
| M3 | Full prime × probe matrix has no precedent in the anchor protocol | The point of the stage; the diagonal and the 36 control cells keep the anchor-comparable frame inside the matrix |
| M3 | Pooled off-diagonal counts each gated item 11 times | Within-item correlation, owned; per-direction, per-pair and effective-n views reported beside |
| M3 | **The frozen degeneracy scope guards only one of the gate's two surviving arms** | Found at post-run adversarial review and owned rather than patched: a wrong-opening collapse confined to the within-category arm could in principle let clause (2) rest on a degenerate cell. At the two smaller subjects the unguarded arm runs 3–4× the guarded arm's share (0.052 vs 0.016 at 0.5B; 0.030 vs 0.008 at 1.5B); at 3B the ordering inverts (0.010 vs 0.014). **Nothing here is affected** — 0.052 is an order of magnitude below the 0.5 threshold and no arm collapsed on any subject — and the wording was **not** amended, because editing a pre-registration after seeing results is the exact move the frozen-wording rule exists to prevent |
| M4 | **The stage exists at all**, after the kickoff's frozen chain | A close-out stage picked after M3, to close M3's own stated bound before write-up; the kickoff's scope decisions were not relitigated |
| M4 | **A new, uncalibrated, sole-dispositive 0.5 constant** | M3's 0.5 was a per-cell floor and never dispositive; M4's is a bar on a 12-fold conjunction and is the single gate, so no provenance transfers. Owned as deliberately lenient, pre-registered before any new cell, fitted to none, with the per-cell equivalence (≈ 0.944) frozen into the gate wording itself so no write-up can quote it as M3's floor |
| M4 | A level-bar gate rather than the lineage's ordering gates | The ordering is M3's settled result; the strip's question is a level question |
| M4 | Five cross-mention (prime, item) pairs kept in gate-bearing pools | The confound biases *against* the gate; each is named and reported per cell (§4.5.3) |
| M4 | `oracle.py` byte-shared by a **fourth** consumer | The rule's entire purpose is byte-identity across consumers; pinned by the existing shared-oracle test pattern. The standing convention that each runner is *cut* from its predecessor is otherwise unbroken — no certified file is ever edited to serve a later stage |
| M4 | **The oracle's span-truncation residual now sits in a gate-bearing arm** | The 3-token span cannot observe the closing boundary for the three concepts whose bare form fills it (`beetle`, `butterfly`, `trumpet`), and M4 scores all 60 probes, so they are gated again for the first time since M1. The bias runs *toward* the gate, so it is disclosed per subject (0/2/2 clean-arm cells; 0/27/21 recorded overall) and carried by the pre-registered residual-conservative recomputation — never by editing the frozen oracle |
| M4 | **Probe-side reach is still the oracle-visible roster** | 25 / 7 / 5 of the 48 non-subset concepts gate zero items. This is a **competence selection**, and it plausibly enriches for robust concepts and biases the floor **upward**. The claim is sparing across the *measurable* vocabulary, and it is said exactly that way |
| M4 | The frozen gate wording promises per-pair-cell degeneracy texture the runner does not compute | Found at post-run adversarial review; the wording is byte-frozen with three subjects' artifacts and cannot be edited, and the readout is pre-declared non-verdict-bearing at n ≤ 3. Disclosed here rather than patched, and **that clause must not be quoted as if the field exists** |

*In plain words: stage by stage, the things worth knowing are — M1 added 7 words from
new lists and used a strict word-boundary test when screening its clue sentences for
giveaways, so that a clue containing "plant" is not wrongly thrown out for leaking
"ant". M2 widened the scoring rule (a fix to how words get chopped
up, not to what counts as an answer), wrote new code for partial removal, invented the
sliding-window sweep, and — importantly — compared tiers that do not delete the same
number of layers, so its localization comparison mixes "where" with "how much"; a
constant-width sweep shows the same picture, but the verdict itself was computed on
unequal arms and that is said out loud. M3 invented the full grid, counts each item
eleven times in the pooled arm, and has a degeneracy guard that covers only one of the
two arms its second clause rests on — an issue found in review afterwards and disclosed
rather than quietly patched, since editing a locked rule after seeing results is exactly
what the locking is meant to prevent. M4 exists at all only because M3 left a bound open;
it introduces a brand-new, uncalibrated 0.5 bar that is its single deciding number; it
keeps five awkward cases in the pool because they work against it; it shares the scoring
code with a fourth user; and it has two known scoring blind spots — a three-piece span
too short to see the end of `beetle`, `butterfly` and `trumpet`, handled by a stricter
pre-registered recount rather than by editing the locked rule, and a promised
per-pair-cell readout the code never actually computes, which must therefore not be
quoted as though it exists.*

### 6.3 Bounds on what the numbers can carry

- **The coverage limit is a limit of the scoring rule, twice over.** M1's
  single-word-piece rule could see 38 / 61 / 44 of the 180 items, and the widened rule
  69 / 105 / 116. M4's decision arm is whatever the widened rule can see; no number here
  speaks for the invisible remainder.
- **Every 0.5B reading sits off the decision path**, under a standing "does any
  direction cause damage here?" framing.
- **Per-concept, per-window and per-pair cells have no more than 3 trials each**, and
  never carry a verdict. That includes every square in Figure 4.
- **The curves share items with each other**: the same 28 / 34 / 32 qualifying items
  appear in every window and every dose cell, so Figures 2 and 3 are not independent
  samples across positions.
- **The 3B diagonal is not perfectly zero** (3 of 32) — and the two concepts responsible
  were pre-registered as the leaky group.

---

## 7. Reproducibility

Everything is local, forward-only, and free. **Total compute cost for the whole project:
\$0.** The closing stage's three models — 2,340 cells each — took roughly 50 minutes in
total on Apple's MPS backend.

**To re-run the measurements.** `uv` (Python 3.12+) manages the environment. `uv run
pytest` turns the test suite green — **396 tests**, recorded green both locally and in
continuous integration in `HANDOFF.md`; this write-up quotes that record rather than
re-running it. The measurement scripts live at the top level of the repository and are
invoked once per model, e.g. `uv run python -u m4_strip.py --model-id
Qwen/Qwen2.5-1.5B-Instruct --lens lenses/qwen2.5-1.5b-instruct-n100.pt`. Every script
supports `--dry-run` and `--limit` (smoke-testing only, never a result), and every
pass/fail rule exits INVALID when fed the wrong arm's data.

**To re-draw the figures.** `uv run --with matplotlib docs/paper/figures.py`. The script
is deterministic and needs no display: it reads only the saved JSON files in `results/`,
writes only the six PNGs beside itself, and prints every number it plots along with the
file and the JSON key it came from. matplotlib is pulled in for that one run alone and
is deliberately not a project dependency — the dependency list is the one the
measurements actually ran under. **The script computes nothing beyond dividing hits by
attempts, where a file records the pair of counts rather than the rate**; every error bar
it draws is a recorded `wilson_95` or `newcombe_*` endpoint, and it never smooths,
interpolates, curve-fits, re-buckets, or pools across cells that the measurement scripts
did not already pool.

**What is and is not in the repository.** The frozen item sets are in `items/`; the
per-run JSON files are in `results/` (18 files: the anchor, the M1 battery, the M1
re-score, the M2 depth run, the M3 matrix and the M4 strip, for each of three models);
decisions D1–D22 are in `docs/DECISIONS.md`; the per-stage briefs are in `docs/`. The
`.pt` lens files are **excluded from version control** by decision K3 — they are sourced
from the earlier project's local copies, with `lenses/PROVENANCE.md` recording each
file's SHA256 fingerprint, how it was fitted, and the exact command to regenerate it.
The models download from HuggingFace on first use; there are no API keys and no `.env`
file.

**The environment does real work here.** Reproducing results bit-for-bit depends on the
certified stack — device `mps`, `torch==2.13.0`, `transformers==5.13.1`; off that stack,
a run is declared NOT A RESULT in advance. Re-certifying the anchor after touching the
harness, the removal operator, the model loader or the version pins means regenerating
the left-hand side first (`m0_anchor.py`, once per model) before running
`m0_port_gate.py --all`, which otherwise just compares two committed files against each
other and proves nothing.

**Three known, unfixed follow-ups**, written down rather than repaired, none of which
affects any number above:

1. The closing stage's frozen rule wording promises a per-pair-cell degeneracy readout
   that the script does not actually compute (its `tokenizer` parameter goes unused).
   The wording is locked byte-for-byte together with three models' worth of saved
   results; honouring it would change those files and cost a full re-run, for a readout
   that was declared in advance to carry no verdict at 3 trials or fewer.
2. That script's `main()` re-reads the item battery outside the `try`/`except` block
   that turns a changed battery into a clean INVALID exit, so those checks would raise a
   bare stack trace instead of exiting with code 2. Unreachable in practice — the file
   cannot change between the two reads within a single process.
3. The continuous-integration job is still *named* `offline-suites`, but now that pytest
   genuinely runs, it fetches four Qwen2.5 tokenizer repositories on every push. **390
   of the 396 tests pass with no network access at all; a red build there means network,
   not logic.** The two possible fixes trade off against each other, so this is a
   workflow design call rather than a correctness fix.

One related disclosure: until 2026-07-29 the continuous-integration workflow ran each
test file as a plain script, and because those files had no `if __name__ == "__main__"`
guard, they imported themselves, defined their functions and exited successfully — so
continuous integration ran zero tests. It now runs `pytest` per file, green with all 396
cases collected. **Any green CI badge dated before 2026-07-29 certifies that the code
parses, not that it works.**

---

## 8. References

1. Anthropic. *Workspace / Jacobian lens.* Transformer Circuits, 2026.
   <https://transformer-circuits.pub/2026/workspace/index.html> — **cited by URL; this
   publication has no arXiv identifier, and the repository records no author list or
   venue beyond the URL.** Intellectual context for the lineage only; no result here is
   offered as reproducing any claim in it.
2. *dim-stage* — the predecessor project: an independent rebuild and small-scale
   measurement of the Jacobian lens, in which the effect characterized here was first
   observed (its S4b result, recorded in `docs/S4-BRIEF.md` there and in its committed
   result JSONs). <https://github.com/ksdisch/dim-stage>. **This is the anchor for every
   comparison in this paper.**
3. *mute-map* — this project. Approved brief `docs/KICKOFF.md`; decisions D1–D22 in
   `docs/DECISIONS.md`; per-stage briefs `docs/M0-BRIEF.md` … `docs/M4-BRIEF.md`;
   recorded results in `results/`; figure script `docs/paper/figures.py`.
   <https://github.com/ksdisch/mute-map>.
4. Models: Qwen2.5-0.5B-Instruct, Qwen2.5-1.5B-Instruct, Qwen2.5-3B-Instruct, as
   published on HuggingFace under those identifiers. The repository records the model
   identifiers and the pinned inference stack; it records no citation for the Qwen
   technical report, and none is invented here.

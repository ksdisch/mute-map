# Cartography of a late-band output off-switch in small language models

**Breadth, localization, dose, specificity, and vocabulary collateral of a
single-direction concept mute in Qwen2.5-0.5B/1.5B/3B-Instruct**

*mute-map, 2026-07-29. All measurements local, forward-only, $0.*

> **A note on presentation.** This repository committed no figures. Every result
> below is therefore reported as a table or as inline numbers lifted verbatim from
> the recorded run artifacts in `results/`. Nothing here was regenerated, re-run, or
> re-plotted for the write-up: the paper is deliberately **tables-only**.

---

## Abstract

During an independent rebuild of Anthropic's Jacobian-lens work
([transformer-circuits.pub/2026/workspace](https://transformer-circuits.pub/2026/workspace/index.html)),
the predecessor project *dim-stage* observed an effect that survived every control it
ran: removing a single concept's lens direction — a rank-one projection removal — at the
late third of that model's "workspace band" left the model unable to say that word, while
the same removal of a same-category control direction did not (+0.727 [+0.471, +0.868] at
1.5B). That rested on one gated cell of 22 items and one control. This paper characterizes
it. Over five pre-registered stages on Qwen2.5-0.5B/1.5B/3B-Instruct — an exact anchor
re-run, a 60-concept / 180-item battery, a window and dose sweep, a 12 × 12 prime × probe
matrix, and a 12-prime × 180-item collateral strip — the switch is broad
(+0.656 [+0.517, +0.763] at 1.5B; +0.636 [+0.443, +0.759] at 3B), localized to the late
third rather than the band (early − late +0.853 [+0.668, +0.936] at 1.5B), graded rather
than binary in dose, and specific across the matrix (+0.971 [+0.867, +0.983] at 1.5B).
The close-out stage asks whether deleting one concept spares the *other 48*: the
item-level floor clears the pre-registered 0.5 bar (51/71 = 0.718 [0.605, 0.810] at 1.5B;
63/84 = 0.750 [0.648, 0.830] at 3B), but the pre-committed concept-level floor's Wilson
lower bound does not (0.434 and 0.456), so both verdicts carry a pre-declared **AS-SCORED
ONLY** qualifier. We report every null and owned bound, plus two findings that re-scope —
rather than retract — earlier stages. The anchor throughout is our own recorded result,
never a published claim.

---

## 1. Introduction

Interpretability results are easy to state and hard to bound. An intervention that
produces a dramatic behavioural change — a model that suddenly cannot say "France" —
reads as a mechanism. Whether it *is* one depends on questions a single cell cannot
answer: does it work for other words, or only the ones you tried? Does it need that
exact location? Is it a switch or a dial? Does it damage only its target? This project
answers those four questions for one specific effect, and then a fifth the first four
leave open.

**The honest contribution.** This is neither a reproduction of a published claim nor a
novel mechanism. It is the lineage's first **original characterization**: an effect
found during a replication, characterized here. The anchor is the predecessor project
*dim-stage*'s own recorded S4b result (`docs/S4-BRIEF.md` there), which this project
re-runs bit-for-bit before measuring anything new. The seed paper that motivated the
lineage — Anthropic's workspace / Jacobian-lens write-up at
[transformer-circuits.pub/2026/workspace](https://transformer-circuits.pub/2026/workspace/index.html),
which has no arXiv identifier and is cited by URL — supplies intellectual context and
nothing more. No result below is offered as reproducing it.

**What is being deleted.** A *Jacobian lens* maps a model's internal activations onto
per-word directions. *Projection removal* at rank one (`k = 1`) subtracts out exactly
the component of the activation pointing along one such direction and leaves everything
else untouched. Applied at a contiguous set of layers it is a surgical, forward-only
edit: no weights change, no gradients, no fine-tuning.

**The discipline.** Every stage froze its gate — verdict wording included — as
executable code before its first real run, and dry-ran it on deliberately wrong inputs
to confirm it exits INVALID. Wilson intervals decide every cell, Newcombe intervals
every between-arm difference; a cell under 20 trials is pre-declared UNDERPOWERED and
makes no claim; a pre-committed null is a reportable result. Each stage re-certifies its
predecessors' recorded cells bit-for-bit before reading a single new one, so a drifting
instrument cannot masquerade as a finding.

---

## 2. Background and method

### 2.1 The anchor

At the late third of each model's workspace band, the predecessor project recorded naming
under the concept's own direction removal at 0/5, 0/22 and 0/8 gated items (0.5B / 1.5B /
3B), against a same-category control that left naming largely intact. Its specificity
readout was concept-SPECIFIC at 1.5B (+0.727 [+0.471, +0.868]), not shown and
UNDERPOWERED at 0.5B (+0.200 [−0.264, +0.624]), and concept-SPECIFIC but UNDERPOWERED at
3B (+1.000 [+0.541, +1.000]). The 0.5B and 3B cells were starved by a dual competence
gate requiring the model both to name the concept correctly and to *avoid* it correctly
on request.

### 2.2 The instrument, and the design change

mute-map inherits the fitted lens artifacts (never refit for the core chain — copied with
SHA256 provenance, decision K3), the projection-removal operator, and the anchor
protocol. The one standing design change is a **naming-only competence gate** (K2):
because the off-switch is a claim about naming, an item enters the measured set iff the
model names the concept correctly on the clean arm. Dropping the avoidance half is what
takes the gated cells from 5 / 22 / 8 to powered sizes at every scale. It is an owned
deviation, and anchor comparability is preserved by re-running the original dual-gate
protocol exactly (§4.1).

### 2.3 The oracle

The readout is deterministic by standing guardrail: never an LLM judge, never free-text
parsing. Through M0 and M1 the rule was the **greedy first token** — the model's single
highest-probability next token must be one of the concept's single-token spellings,
case-exact. M2 widened it once, by decision D9(b), frozen as code in `oracle.py` before
any M2 run: the concept is produced iff the decoded first-3-greedy span, after stripping
leading whitespace, **opens with the concept's spelling at a word boundary,
case-insensitive**. It is a prefix rule, never containment ("not France" is a miss), the
boundary test is "the next character is not a letter or digit" ("Marseille" is not Mars),
and the end of the span counts as a boundary. `oracle.py` is byte-shared rather than
copied by four consumers, so the rule cannot drift between them. The concept's softmax
probability mass is recorded beside every cell as a graded texture channel, as is the
first-token outcome, so anchor comparability never degrades.

### 2.4 The statistical rules

- **Wilson 95% intervals** on every cell; **Newcombe 95% intervals** on every
  between-arm difference. A difference whose interval includes zero is a null and is
  stated as one.
- **MIN_N = 20** per cell; below it the verdict is pre-declared UNDERPOWERED.
- **A cell whose interval overlaps its neighbour is not a result.**
- **Degeneracy guards.** Every arm's most common wrong opening token is recorded; a
  share at or above COLLAPSE_SHARE = 0.5 on a dispositive arm pre-declares the run
  DEGENERATE. A guard on the intervened arm is a tag only, since a shared attractor
  under the concept's own deletion is the expected signature of the switch.
- **Environment-scoped cross-checks.** Bit-for-bit reproduction is a property of the
  certified stack (device `mps`, `torch==2.13.0`, `transformers==5.13.1`). On it a
  mismatch exits INVALID; off it the run is pre-declared NOT A RESULT.
- **Precedence, frozen in each verdict function:** NOT A RESULT > DEGENERATE >
  UNDERPOWERED > the contrast.

---

## 3. Experimental setup

Three subjects throughout: **Qwen2.5-0.5B-Instruct**, **Qwen2.5-1.5B-Instruct**,
**Qwen2.5-3B-Instruct**, run locally on Apple MPS, forward-only, at $0. Every gate is
the AND over the two gate-bearing subjects, 1.5B and 3B. **0.5B is never gate-bearing**
and is read only under a standing any-direction-damage frame, because the predecessor
project had already recorded non-specific damage at that scale.

Lens artifacts were fitted by dim-stage's `fitter.py` at n_prompts = 100 on WikiText
prompts (0.5B and 1.5B on local MPS, 3B on a rented RTX 4090) and copied here with
recorded SHA256 fingerprints. Workspace bands, ported unchanged, are L9–L21, L11–L24 and
L14–L32; the band thirds follow the ported convention, which gives the late tier the
band's remainder (4/4/**5**, 4/4/**6**, 6/6/**7**).

| Stage | Question | Design | Cells / subject |
|---|---|---|---|
| **M0** | Is the ported instrument the same instrument? | Exact re-run of the anchor protocol, dual competence gate retained | 840 |
| **M1** | How much of the measurable vocabulary has an off-switch? | 60 concepts × 10 categories × 3 clue items = 180 items; conditions clean / primed_late / control_late | 540 |
| **M2** | Where does the switch live, and how much removal does it take? | Pre-registered 12-concept subset (36 items); three tiers, a stride-2 sliding window sweep including outside-band positions, and a partial-ablation dose curve λ ∈ {0, .25, .5, .75, 1} | 720 / 756 / 864 |
| **M3** | Does deleting A damage B? | Full 12 × 12 prime × probe matrix at the switch's home band, plus 18 out-of-subset control-direction cells | 486 |
| **M4** | Does deleting one concept spare the *other 48*? | The 12 characterized directions as primes; **all 180 battery items** as probes | 2,340 |

The 180-item battery was frozen in `items/m1-battery.json` before any M1 run: 10
categories × 6 concepts × 3 clue sentences, 53 concepts drawn from vocabularies this
lineage had already measured and 7 new-list top-ups (marked in the frozen file) filling
gaps where a shipped list ran dry. 60 of the 180 items are the predecessor project's own
frozen items, reused verbatim so that every later run carries a live anchor check inside
it. **The item sets are constructed, not naturally occurring** — an owned deviation
carried from the first stage onward.

---

## 4. Results

Verdicts are quoted as the runners emitted them. Bold marks the gate-bearing subjects.

### 4.1 M0 — the instrument is the same instrument

| Subject | Cells compared | Mismatches | Gated n | Anchor specificity readout reproduced |
|---|---|---|---|---|
| 0.5B | 840 | **0** | 5 | not shown, UNDERPOWERED (+0.200 [−0.264, +0.624]) |
| 1.5B | 840 | **0** | 22 | concept-SPECIFIC (+0.727 [+0.471, +0.868]) |
| 3B | 840 | **0** | 8 | concept-SPECIFIC, UNDERPOWERED (+1.000 [+0.541, +1.000]) |

Beyond the gate's bar, the recorded `concept_mass` softmax floats reproduced **exactly,
840/840 cells on every subject** — the pinned environment preserved not just the greedy
argmax but the full computed distribution to the last bit. Every later stage embeds a
subset of previously recorded cells and grades them *first*: M2 and M3 each re-certified
108/108 M1 cells, and M4 re-certified **two** artifact sets at once — **255/255 M1 cells
and 468/468 M3 cells, `concept_mass` exact on all 723 comparisons, ×3 subjects** —
before reading a single new cell.

### 4.2 M1 — breadth

| Subject | Gated n / 180 | `primed_late` | `control_late` | control − primed [Newcombe 95%] | Verdict |
|---|---|---|---|---|---|
| 0.5B *(off-gate)* | 38 | 0/38 | 17/38 | +0.447 [+0.275, +0.603] | BREADTH-SPECIFIC |
| **1.5B** | 61 | 0/61 | 40/61 | **+0.656 [+0.517, +0.763]** | BREADTH-SPECIFIC |
| **3B** | 44 | 6/44 | 34/44 | **+0.636 [+0.443, +0.759]** | BREADTH-SPECIFIC |

**M1 verdict: BREADTH-SPECIFIC at 1.5B AND 3B.** The effect is not idiosyncratic to the
handful of items it was first seen on.

**Prevalence is UNDERPOWERED, exactly as pre-declared.** On the fixed-denominator
concept set, 4/8 (0.5B), 9/11 (1.5B) and 6/8 (3B) concepts show the full hard-switch
profile. All three carry the pre-declared UNDERPOWERED tag — the concept-set cell was
named in advance as the single sub-MIN_N cell in the stage — and none supports a claim.

**0.5B came in BREADTH-SPECIFIC too, and that weakens a story we inherited.** The
anchor's 0.5B cell did not show specificity, on a gated n of 5. The naming-only gate
lifts 0.5B to n = 38, and the contrast is CI-clean. The honest reading, forecast in the
deviations table before the run: the anchor's 0.5B null was **underpowered, not
evidence of absence**, and the lineage's "specificity emerges by scale" narrative
weakens accordingly. M1 makes no scale claim; it reports that all three subjects show
the switch once each has the power to see it.

#### 4.2.1 The owned bound: the readout, not the model, sets the coverage

The competence gate admitted only 38 / 61 / 44 of 180 items, and the dominant reason is
a property of the readout rather than of the models. Under the first-token oracle a
concept is scorable only if its spelling at the answer position is a single token;
**26 of the 60 roster words have a multi-token bare form**, and the model usually spells
them without a leading space, so its first token is a fragment (`'Mer'`, `'Viol'`,
`'Fl'`) that the gate scores as a miss. Whole categories therefore gate near zero —
**planets and musical instruments gated 0 items on all three subjects** — so the
per-category map is in part a map of tokenizer geometry rather than of concepts.

The first-3-greedy texture measures the cost directly rather than assuming it: among
*ungated* items the model still said the concept within three tokens in **35/142 (0.5B),
54/119 (1.5B) and 80/136 (3B)** — competence the primary readout simply cannot see.

Two things bound this bound. It does not threaten the gate: the contrast is computed
*within* the gated set, and gating is a property of the clean arm alone, decided before
any ablation. And the same texture shows the bias **runs against the finding, not for it**
— on the gated cell the model said the concept within three tokens in `control_late`
17/17, 46/40 and 36/34, so at both gate-bearing subjects the primary readout *understates*
control-arm survival, while under `primed_late` it said the concept 0/38, 0/61 and 6/44,
exactly matching the primary count. The comparison arm is, if anything, scored too
harshly.

#### 4.2.2 The re-score, published beside — not instead of — M1's numbers

The instrument fix belonged in a decision, not a results section. M2 opened by widening
the oracle (D9(b)) and publishing a **labelled reanalysis** of M1's *same recorded cells*
under it (D10(a)). No model was run and no new trial measured: the re-score is a pure
function of the committed M1 artifacts, and the script refuses to write anything unless
it first reproduces M1's published first-token contrast exactly — which it does, on all
three subjects. **M1's verdict of record is unchanged.**

| Subject | Gated n (first-token → widened) | `primed_late` | `control_late` | control − primed [Newcombe 95%] |
|---|---|---|---|---|
| 0.5B *(off-gate)* | 38 → 69 | 0/69 | 33/69 | +0.478 [+0.353, +0.594] |
| **1.5B** | 61 → 105 | 0/105 | 80/105 | **+0.762 [+0.665, +0.833]** |
| **3B** | 44 → 116 | 12/116 | 92/116 | **+0.690 [+0.582, +0.767]** |

The two dark categories light up — planets 0 → 7 / 8 / 15 and musical instruments
0 → 2 / 8 / 13 of 18 items each — and the contrast survives on every subject in the
*harder* direction: `control_late` gains far more items than `primed_late` does, and at
1.5B primed stays at exactly 0 across all 105 gated items. Under the first-token readout
one could argue the mute was partly an artifact of fragment-scoring. It is not.

A separate worry — that the contrast might be carried by the 60 items the predecessor
project itself selected — closes here under **both** oracles. On the **120 newly authored
items alone** the contrast is CI-clean on all three subjects: +0.278 / +0.545 / +0.478
under the first-token oracle and +0.389 / +0.714 / +0.629 under the widened one. The
reused stratum runs higher, as expected for items chosen against a model that could
already name them, but the new stratum stands on its own.

### 4.3 M2 — localization and dose

| Subject | Gated n / 36 | `primed_early` | `primed_middle` | `primed_late` | early − late [Newcombe 95%] | middle − late [Newcombe 95%] | Verdict |
|---|---|---|---|---|---|---|---|
| 0.5B *(off-gate)* | 28 | 17/28 | 17/28 | 0/28 | +0.607 [+0.388, +0.764] | +0.607 [+0.388, +0.764] | LATE-LOCALIZED |
| **1.5B** | 34 | 29/34 | 27/34 | 0/34 | **+0.853 [+0.668, +0.936]** | **+0.794 [+0.603, +0.897]** | LATE-LOCALIZED |
| **3B** | 32 | 27/32 | 25/32 | 3/32 | **+0.750 [+0.531, +0.857]** | **+0.688 [+0.463, +0.812]** | LATE-LOCALIZED |

**M2 verdict: LATE-LOCALIZED at 1.5B AND 3B.** The gated ns were *predicted before the
runs* — 28 / 34 / 32, because gating is a property of the deterministic clean arm M1 had
already recorded — and came in at 28 / 34 / 32. A disagreement would have been an INVALID
cross-check, not a power surprise.

**The sliding window sweep** (descriptive, never gate-bearing; ° marks a window with no
layer inside the band, \* the reused late-third gate cell):

| Subject | naming / gated n by window start |
|---|---|
| 0.5B (width 5, n = 28) | L0°15, L1°15, L3°14, L5 16, L7 16, L9 16, L11 19, L13 15, L15 13, **L17\* 0**, L18 0 |
| 1.5B (width 6, n = 34) | L0°33, L1°32, L3°27, L5°28, L7 28, L9 27, L11 25, L13 23, L15 23, L17 1, **L19\* 0**, L21 0 |
| 3B (width 7, n = 32) | L0°32, L2°32, L4°31, L6°30, L8 30, L10 29, L12 29, L14 25, L16 25, L18 25, L20 24, L22 16, L24 11, **L26\* 3**, L28 1 |

Removing the *same* direction at the *same* strength anywhere before the late third
leaves most naming intact; only the late window drives it to floor. The transition is
sharp at 0.5B and 1.5B and noticeably more gradual at 3B, which descends 24 → 16 → 11 →
3 over four positions. Stride 2 localizes the 1.5B edge to between window starts L15 and
L17.

**Out-of-band ablation is cheap at the larger subjects and expensive at 0.5B**, quoted
as ranges rather than best cases: over windows with no layer in the band at all, naming
survives 27–33 of 34 at 1.5B (3–21% lost), 30–32 of 32 at 3B (0–6% lost) and 14–15 of 28
at 0.5B (46–50% lost). Only 3B has a genuinely free out-of-band position; 1.5B's best
still costs one item and its worst loses 21% — the same depth-nonspecific damage 0.5B
shows, an order of magnitude smaller but not absent. **This is why 0.5B's LATE-LOCALIZED
reading sits on a raised floor**: its late cell is a genuine cliff (0/28 against a
~15/28 baseline), so the localization shape is real, but the "everywhere else is benign"
half of the story fails there.

**The dose curve — a dimmer, not a step.** Naming and mean concept mass under partial
removal at the late third (λ = 0 is `clean` and λ = 1 is `primed_late`, both reused
rather than re-measured; the mass channel is scoped to the gated items whose bare
spelling is single-token, n = 22 / 24 / 21):

| λ | 0.5B naming (mass) | 1.5B naming (mass) | 3B naming (mass) |
|---|---|---|---|
| 0 | 28/28 (0.833) | 34/34 (0.913) | 32/32 (0.942) |
| 0.25 | 13/28 (0.362) | 20/34 (0.594) | 21/32 (0.782) |
| 0.5 | 0/28 (0.022) | 3/34 (0.115) | 10/32 (0.342) |
| 0.75 | 0/28 (0.001) | 1/34 (0.037) | 4/32 (0.197) |
| 1 | 0/28 (0.000) | 0/34 (0.017) | 3/32 (0.120) |

Partial removal produces intermediate naming rates and intermediate probability mass at
every subject. **Nothing here behaves like a binary switch that flips at a threshold**,
which answers a question the kickoff brief left open. The knee is steep and appears to
move right with scale — the brief's half-mute points are λ ≈ 0.23 / 0.29 / 0.36 — but
those three figures are **linear interpolations between two grid points, not
measurements**: the grid is frozen at five values and nothing was re-fit. The mass
channel tells the same story without interpolation: at λ = 0.5 the retained mass is
0.022 / 0.115 / 0.342. The binary channel can only step and the mass channel moves
continuously; they fall together, so the dimmer reading does not rest on the binary
readout alone.

**The pre-registered strata did their jobs**, including the one selected to fail. The
hard-switch core sat at 0/3 naming under `primed_late` on every subject; the
readout-unlocked stratum muted throughout; the leaky stratum leaked at 3B where
predicted. And the non-specific anti-example `silver` failed the pattern as designed: at
1.5B it gates 3/3 and reads `primed_late` 0/3 **and `control_late` 0/3** — the control
direction mutes it too — with `primed_early` 1/3 and `primed_middle` 0/3, i.e. damaged at
*every* depth. The pooled curves above include it.

### 4.4 M3 — the specificity matrix

Rows are the deleted direction A, columns the probed concept B.

| Subject | Gated n / 36 | Diagonal | Off-diagonal | clause (1) off − diag [Newcombe 95%] | Within-category | Restricted diagonal | clause (2) [Newcombe 95%] | Verdict |
|---|---|---|---|---|---|---|---|---|
| 0.5B *(off-gate)* | 28 | 0/28 | 279/308 | +0.906 [+0.779, +0.934] | 80/96 | 0/24 | +0.833 [+0.670, +0.895] | MATRIX-SPECIFIC |
| **1.5B** | 34 | 0/34 | 363/374 | **+0.971 [+0.867, +0.983]** | 95/100 | 0/28 | **+0.950 [+0.814, +0.978]** | MATRIX-SPECIFIC |
| **3B** | 32 | 3/32 | 343/352 | **+0.881 [+0.731, +0.943]** | 97/101 | 2/29 | **+0.891 [+0.730, +0.947]** | MATRIX-SPECIFIC |

**M3 verdict: MATRIX-SPECIFIC at 1.5B AND 3B**, on both pre-committed clauses. Clause (2)
restricts the contrast to *same-category* pairs — the arm the predecessor's single
control actually tested — so the pooled arm's cross-category-heavy composition did not
carry the verdict. **No subject carries the ON A DAMAGED FLOOR qualifier**: the
collateral floor reads 25/28 [0.728, 0.963], 33/34 [0.851, 0.995] and 31/32 [0.843,
0.994], all far above the pre-registered 0.5 floor — including at 0.5B, which the brief
had left genuinely open. Every pre-registered n came in exactly, every pooled cell clears
MIN_N, and no arm collapsed. **126 of the matrix's 132 ordered off-diagonal pairs had
never been measured before**; the other 6 are the earlier stage's own control cells.

An effective-n sanity check — collapsing each item to "survives *all 11* off-diagonal
deletions" — agrees with the gate on every subject: 19/28, 29/34, 27/32 against diagonal
0/28, 0/34, 3/32, giving +0.679 [+0.458, +0.821], +0.853 [+0.668, +0.936] and +0.750
[+0.531, +0.857]. There is no case where the honest per-item numbers would have had to
be quoted instead of the pooled ones. The graded channel agrees with the binary one:
mean concept mass reads clean 0.833 / 0.913 / 0.942, diagonal 0.0001 / 0.017 / 0.120,
off-diagonal 0.773 / 0.889 / 0.937.

#### 4.4.1 Re-attribution (a): non-specificity has a direction

`silver` entered the subset as the pre-registered **non-specific anti-example** — the one
concept whose *control* direction had muted it in M1 — and the brief expected its row to
drag the pooled off-diagonal down. Its row does no such thing. **Deleting silver's
direction damages nothing, at any scale** (27/27, 31/31, 31/31). What is true is the
transpose: silver's *column* is the most fragile in the matrix (7/11, 27/33, 6/11 under
other concepts' deletions). The misses pile onto a few fragile probes rather than
spreading from a few damaging primes — at 1.5B all 11 off-diagonal misses land on
`silver` (6), `Canada` (3), `piano` (1) and `violin` (1).

This is a **re-scoping, not a retraction**. M1 and M2 each sampled *one cell of silver's
column* and read it as a property of silver's row; the single-control design could not
have distinguished the two. M1's and M2's published numbers stand. What changes is what
the label "non-specific" was ever a fact about.

#### 4.4.2 The nulls M3 recorded

**Category-block collateral is CI-clean at 0.5B and dissolves by 1.5B.** Within- versus
cross-category collateral gives a Newcombe difference of **+0.105 [+0.032, +0.196]** at
0.5B — CI-clean — but **+0.028 [−0.010, +0.091]** at 1.5B and **+0.020 [−0.016, +0.079]**
at 3B. Both straddle zero, and by this project's own rule a cell whose interval overlaps
its neighbour is not a result. So: at 0.5B, deleting a country's direction measurably
damages *other countries*; by 1.5B that block has dissolved into noise. §4.5.2 revisits
this, and the revisit is the reason this null is stated at exactly this strength.

**The leak stratum replicated, on the diagonal, at 3B only.** The only diagonal cells
anywhere that are not zero are `Egypt` 2/3 and `October` 1/2 at 3B — exactly the two
concepts pre-registered as the leaky-switch stratum. The mute is not perfect for those
two words at the largest subject, and the pre-registration named them in advance.

**Asymmetry is real but sparse**: 19 / 7 / 8 of the 66 unordered pairs differ at all
between A→B and B→A, and at both gate-bearing subjects the largest gaps are dominated by
`silver` on the probe side.

### 4.5 M4 — the vocabulary collateral strip (the close-out stage)

M3's near-white grid showed that deleting France spares the other *eleven* subset
concepts. It showed nothing about the other 48. M4 keeps the 12 characterized directions
as the **primes** and widens the **probes** to all 60 battery concepts: **2,340 cells per
subject**, every one at the identical late third, λ = 1, k = 1. The gate is a **level**
bar, not an ordering one — M3 settled the ordering — and it is single-clause:

> **VOCAB-SPARING** iff, per subject: among the gated **non-subset** items, the
> proportion that **survives all 12** subset-direction deletions has its Wilson 95%
> lower bound at or above **0.5**. The bar is read **only when** the 468 M3-recorded and
> 255 M1-recorded cells reproduce their recorded outcomes bit-for-bit.

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

**M4 verdict: VOCAB-SPARING at 1.5B AND 3B — AS-SCORED ONLY.** The scope is the result,
not a footnote to it. **The item-level floor clears the 0.5 bar; the concept-level
floor's Wilson lower bound does not (0.434 at 1.5B and 0.456 at 3B).** The concept-level
read — one binary per concept instead of per item — was pre-registered before any new
cell was run, and the brief pre-committed those as **the honest numbers to quote**. A
post-freeze amendment, ratified before the run, is what puts them *inside* the verdict
string rather than leaving them in prose: prose is not what gets quoted, the label is.
The residual-conservative read clears at both subjects, so exactly one of the two
pre-registered conservative reads fired.

Every pre-registered n landed exactly: gate arms 41/71/84, concept counts 23/41/43,
ceilings 35/41, 69/71 and 82/84 with precisely the named misses (`july-1`, `april-1`,
`april-3`, `gold-1/2/3` at 0.5B; `july-3`, `venus-3` at 1.5B; `guitar-2`, `neptune-1` at
3B) — knowable in advance because the strip physically re-runs the 255 M1-recorded and
468 M3-recorded cells (633 of its 2,340 once the 90-cell overlap is counted once) and
grades them first. No degeneracy fired on the dispositive arm:
wrong-opening shares 0.022 / 0.011 / 0.011 against a 0.5 threshold.

#### 4.5.1 Re-attribution (b): category-block collateral does not dissolve with scale

M4 reverses M3's §4.4.2 null, and the reason is arm composition.

| Subject | Within-category | Cross-category |
|---|---|---|
| 0.5B | 5/22 | 382/470 |
| **1.5B** | **22/29 = 0.759** | **769/823 = 0.934** |
| **3B** | **35/53 = 0.660** | **913/955 = 0.956** |

**Category-block collateral is real in the wider vocabulary and does not dissolve with
scale.** M3 saw it dissolve by 1.5B — but M3's within-category arm was **30 of 34 pairs
countries**, a single tight block sampled twelve ways. The strip's within-category arm
samples ten categories. Again: a **re-scoping, not a retraction**. M3's published numbers
stand; what was measured there was a fact about that arm's composition.

#### 4.5.2 Finding 1 generalizes out of sample

Collateral still concentrates on fragile **probes**, not damaging **primes**. **No prime
is a wrecking ball**: at 1.5B every row lands between 63/71 and 67/71, at 3B between
77/84 and 83/84. But specific probe columns collapse — `copper` 6/12 and `mosquito` 8/12
at 1.5B; `eagle` 8/12, `platinum` 9/12 and `trumpet` 18/36 at 3B — while **32 of 53
gated columns at 1.5B and 33 of 55 at 3B take zero collateral across all 12 deletions**.
The distribution is bimodal, which is exactly what makes the item-level and
concept-level statistics diverge: a concept with one fragile item fails the
concept-level binary outright.

#### 4.5.3 The nulls and divergences M4 recorded

**0.5B reads `not shown` off-gate at 11/41 = 0.268 [0.157, 0.419]** — the **first
measured divergence between the pre-registered subset's robustness and the wider
roster's**. 30 of 0.5B's 41 gate-arm items (73%) are damaged by at least one deletion,
against 28% at 1.5B and 25% at 3B. Read under the standing any-direction-damage frame,
never as a gate claim, and consistent in advance with M3's own 0.5B subset failing this
bar in-statistic (19/28, lower 0.4934).

**The two statistics disagree by design, and 0.5B shows it starkly.** The M3-comparable
cluster-mean per-cell floor on the same 0.5B cells reads **32/41 → [0.633, 0.880]** —
comfortably above 0.5 — while the 12-fold conjunction on those same cells reads 0.268.
Same subject, same cells, opposite sides of the same constant. That is why the stage
refused to inherit M3's 0.5 and wrote the per-cell equivalence (0.5^(1/12) ≈ 0.944) into
its frozen wording.

**The five pre-registered cross-mention cells did not carry the verdict, as predicted.**
At 3B all four gate-bearing cells named their concept; at 1.5B three named and
`China→jade-1` missed; `Egypt→beetle-2` remains ungated on all three subjects.

**The residual set was larger in the ablated arm than in the clean arm.** The clean-arm
gate-arm residuals were the pre-computed 0 / 2 / 2, but the run recorded **0 / 27 / 21**
residual cells in total (0 / 26 / 21 in the gate arm), all on `beetle`, `butterfly` and
`trumpet` — the three concepts the frozen oracle docstring names. That is what the
pre-registered selector was written for, and why the conservative read moves the number
at all: 51 → 49 at 1.5B, 63 → 62 at 3B.

**The claim is sparing across the *measurable* vocabulary, said exactly that way.**
**25 / 7 / 5 of the 48 non-subset concepts gate zero items** on the three subjects. That
is a *competence selection* — the model answers something else, or answers correctly
behind a modifier the opening-word rule refuses, or misses on morphology — and it
plausibly enriches for robust concepts, biasing the floor **upward**. And the 0.5 bar
itself is new, deliberately lenient and uncalibrated: pre-registered before any new cell
and fitted to none, with the per-cell equivalence written into the frozen wording so it
cannot be quoted as M3's floor.

---

## 5. Discussion

**What was measured.** A rank-one projection removal of one concept's lens direction, at
the late third of the workspace band, reliably prevents small Qwen2.5 models from saying
that word. The effect is broad over a 60-concept battery, localized to the late third
rather than the band, graded rather than binary in dose, specific across a full 12 × 12
grid on both clauses — and it mostly spares the wider vocabulary, with the scope stated
on the label.

**What the scope means.** VOCAB-SPARING is the strongest available phrasing of exactly
the over-reading the close-out stage exists to correct, and the bar it names permits
real damage: at the realized 1.5B rate, 20 of 71 measurable items are still damaged by
at least one of the twelve deletions. The concept-level read — "is *this concept*
untouched?" rather than "is *this item* untouched?" — sits below the bar at both
gate-bearing subjects. Both readings were pre-registered, neither was chosen after seeing
the data, and the honest one-line summary is the one this paper leads with.

**What the nulls mean.** Three matter. (i) The dose curve's null against a step function
is a positive statement about mechanism: the ability to emit the word degrades
continuously with how much of the direction is removed. (ii) M3's category-block null was
a true null *for that arm*, and M4 shows why reading it as a general one would have been
wrong. (iii) M1's prevalence cells are UNDERPOWERED by pre-declaration and support no
claim about how many concepts have switches — only that the pooled contrast holds.

**The two re-attributions are the most transferable result here.** Neither is a
discovery; both correct what an earlier measurement was a fact *about*. A single control
cell told us `silver` was non-specific; the matrix showed that was a fact about silver's
*column*, and that its row damages nothing at any scale. A countries-dominated
within-category arm told us category-block collateral dissolves with scale; the strip
showed that was a fact about *arm composition*. The lesson is structural rather than
mechanistic: **a single control cell measures a cell, not a row**, and an arm's
composition is part of what it measured. Both were findable only because every stage
re-ran its predecessor's recorded cells instead of trusting them.

**The un-validatable residual.** Nothing here establishes *why* the late third is
special, whether the direction is the same object the seed paper's lens is about, or
whether any of this holds above 3B. The sweep's above-band coverage is structurally thin
— no window is ever fully above the band — so "the switch is late" is well-measured on
its early side and only weakly probed on its far side. Prime-side correlation structure
is measured but not modelled. The 7B scale extension and the lexical-versus-semantic
scope question ("can the model still say *French*, *Paris*?") were both designed, both
declined for this repository, and both banked.

---

## 6. Threats to validity

Each stage's owned deviations table survives here in full. These are disclosures made
before or at the time of the runs, not concessions extracted afterward.

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

### 6.3 Bounds on what the numbers can carry

- **The coverage bound is a readout bound, twice over.** M1's first-token oracle could
  see 38 / 61 / 44 of 180 items, the widened oracle 69 / 105 / 116. M4's gate arm is what
  the widened oracle can see; no number here speaks for the invisible remainder.
- **Every 0.5B reading is off-gate**, under a standing any-direction-damage frame.
- **Per-concept, per-window and per-pair cells are n ≤ 3**, never verdict-bearing.
- **Curves are within-item correlated**: the same 28 / 34 / 32 gated items appear in
  every window and dose cell.
- **The 3B diagonal is not perfectly zero** (3/32) — the two responsible concepts were
  pre-registered as the leaky stratum.

---

## 7. Reproducibility

Everything is local, forward-only, and free. **Whole-project compute cost: $0.** The
close-out stage's three subjects — 2,340 cells each — took roughly 50 minutes in total on
Apple MPS.

**To re-run.** `uv` (Python 3.12+) manages the environment. `uv run pytest` greens the
suite (**396 tests**, verified green at the time of writing). Runners live at the
repository root and are invoked per subject, e.g. `uv run python -u m4_strip.py
--model-id Qwen/Qwen2.5-1.5B-Instruct --lens lenses/qwen2.5-1.5b-instruct-n100.pt`. Every
runner supports `--dry-run` and `--limit` (smoke only, never a result), and every gate
exits INVALID on wrong-arm input.

**What is and is not in the repository.** Frozen item sets in `items/`; per-run JSONs in
`results/` (18 files: anchor, M1 battery, M1 re-score, M2 depth, M3 matrix and M4 strip,
×3 subjects); decisions D1–D22 in `docs/DECISIONS.md`; per-stage briefs in `docs/`. The
`.pt` lens artifacts are **gitignored** by decision K3 — sourced from the predecessor
project's local copies, with `lenses/PROVENANCE.md` recording each file's SHA256, its fit
provenance and the exact regeneration command. Models pull from HuggingFace on first use;
no API keys, no `.env`.

**Environment is load-bearing.** Bit-for-bit reproduction depends on the certified stack
— device `mps`, `torch==2.13.0`, `transformers==5.13.1`; off it the run is pre-declared
NOT A RESULT. Re-certifying the anchor after touching the harness, the operator, the
subject loader or the pins requires regenerating the left-hand side first (`m0_anchor.py`
per subject) before `m0_port_gate.py --all`, which otherwise compares two committed files
and is tautological.

**Three known, unfixed follow-ups**, recorded rather than repaired, none affecting any
number above:

1. The close-out stage's frozen gate wording promises per-pair-cell degeneracy texture
   the runner does not compute (its `tokenizer` parameter is unused). The wording is
   byte-frozen with three subjects' artifacts; honouring it would change the JSONs and
   cost a full re-run for a readout pre-declared non-verdict-bearing at n ≤ 3.
2. That runner's `main()` re-parses the battery outside the `try/except` that turns
   battery drift into a clean INVALID exit, so those guards would raise a bare traceback
   rather than exit 2. Unreachable in practice — the file cannot change between the two
   calls in one process.
3. The CI job is still *named* `offline-suites`, but now that pytest genuinely runs it
   fetches four Qwen2.5 tokenizer repositories on every push. **390 of the 396 tests pass
   with no network at all; a red build there is network, not logic.** The two remedies
   (cache the HuggingFace directory, or add a network marker and deselect) trade off
   against each other, so it is a workflow design call rather than a correctness fix.

A related disclosure: until 2026-07-29 the CI workflow executed each test file as a plain
script, and with no `__main__` guard those files imported, defined their functions and
exited 0 — so CI ran zero tests. It now runs `pytest` per file and is green on the real
runner with all 396 cases collected. **Any green CI badge dated before 2026-07-29
certifies syntax, not behaviour.**

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
   recorded results in `results/`. <https://github.com/ksdisch/mute-map>.
4. Models: Qwen2.5-0.5B-Instruct, Qwen2.5-1.5B-Instruct, Qwen2.5-3B-Instruct, as
   published on HuggingFace under those identifiers. The repository records the model
   identifiers and the pinned inference stack; it records no citation for the Qwen
   technical report, and none is invented here.

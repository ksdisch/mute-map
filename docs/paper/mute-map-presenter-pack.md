# mute-map — presenter pack

*Companion to `mute-map-paper.md`. Everything here traces to a recorded file; the
provenance table is the map. The paper's six figures are drawn by
`docs/paper/figures.py` from those same files and plot nothing but recorded values —
if someone points at a figure, the number behind it is in the table below and in the
script's own printout.*

---

## The 60-second story

"In a previous project I rebuilt Anthropic's Jacobian lens at hobby scale, and one effect
survived every control I threw at it: if you take a single concept's lens direction and
subtract it out of the model's activations at the late third of its workspace band, the
model becomes unable to say that word. The evidence was one cell — twenty-two items, one
control comparison. mute-map is the characterization. I mapped it along five axes with
pre-registered gates frozen as code before every run: is it broad, where does it live,
is it a switch or a dial, does it damage the concepts near it, and does deleting one
concept spare the rest of the vocabulary. It's broad, it's genuinely *late* rather than
band-wide, it's a dimmer rather than a step, and it's clean across a full twelve-by-twelve
grid. The close-out result is scoped, and the scope is the point: at the item level the
sparing floor clears my pre-registered bar — 51 of 71 at 1.5B, 63 of 84 at 3B — but
collapsed to one binary per *concept*, the lower bound doesn't (0.434 and 0.456). Both
verdicts ship with an AS-SCORED ONLY tag that was pre-registered before the run, not
added afterward. Everything ran locally on my Mac, forward-only, for $0."

---

## Results at a glance

Bold = the two gate-bearing subjects. 0.5B is never gate-bearing.

| Stage | Gate (frozen as code before the run) | 0.5B | **1.5B** | **3B** | Verdict |
|---|---|---|---|---|---|
| **M0** anchor | 0 mismatches vs the recorded predecessor JSONs | 0/840 | 0/840 | 0/840 | **PASSED** |
| **M1** breadth | pooled `control_late` − `primed_late` CI-clean | +0.447 [+0.275, +0.603] | **+0.656 [+0.517, +0.763]** | **+0.636 [+0.443, +0.759]** | **BREADTH-SPECIFIC** |
| **M2** localization | early − late and middle − late both CI-clean | +0.607 / +0.607 | **+0.853 / +0.794** | **+0.750 / +0.688** | **LATE-LOCALIZED** |
| **M3** specificity | off-diagonal − diagonal CI-clean, pooled AND within-category | +0.906 / +0.833 | **+0.971 / +0.950** | **+0.881 / +0.891** | **MATRIX-SPECIFIC** |
| **M4** vocab collateral | survives-all-12 Wilson lower ≥ 0.5 | 11/41 = 0.268 [0.157, 0.419] | **51/71 = 0.718 [0.605, 0.810]** | **63/84 = 0.750 [0.648, 0.830]** | **VOCAB-SPARING — AS-SCORED ONLY** |

**The M4 scope, said the honest way:** *the item-level floor clears the 0.5 bar; the
concept-level floor's Wilson lower bound does not — 0.434 at 1.5B and 0.456 at 3B.*
Lead with that sentence. Never lead with a bare "VOCAB-SPARING."

**Every null and owned bound, on one card:**

- 0.5B `not shown` off-gate at M4 (0.268) — the first measured divergence between the
  subset's robustness and the wider roster's; 73% of its gate-arm items damaged vs 28%
  and 25%.
- M1's prevalence cells (4/8, 9/11, 6/8) are **pre-declared UNDERPOWERED** — no claim.
- M3's category-block collateral **straddles zero** at both gate-bearing subjects
  (+0.028 [−0.010, +0.091] and +0.020 [−0.016, +0.079]) — a null, and M4 later shows why
  reading it as general would have been wrong.
- The dose curve is a **dimmer, not a step** — the null against a threshold model.
- 25 / 7 / 5 of the 48 non-subset concepts **gate zero items** — a competence selection
  that biases the floor **upward**. The claim is sparing across the *measurable*
  vocabulary, said exactly that way.
- The oracle's **span-truncation residual** now sits in a gate-bearing arm: 0/2/2
  clean-arm cells, 0/27/21 recorded overall, carried by a pre-registered conservative
  recomputation rather than by editing the frozen oracle.
- M1's **first-token coverage bound**: 26 of 60 roster words are multi-token bare, so
  planets and instruments gated 0 items on every subject. The re-score under the widened
  oracle is published *beside* M1's numbers, never instead of them.

---

## The six figures — what each one is for

If you get one minute at a whiteboard, it's Figure 4. If you get one slide, it's Figure 5.

| Figure | The one sentence it exists to say | The trap it avoids |
|---|---|---|
| **1** gate contrasts | Every pre-committed gate cleared zero, on every subject, and you can see how wide each interval is. | It plots the *recorded* Newcombe triples — nothing is recomputed. M4 is absent because its gate is a level bar, not a contrast. |
| **2** window sweep | The switch is a late **cliff on a floor**, and 0.5B's floor is visibly raised. | No line joins the marks: positions between two window starts were never measured. |
| **3** dose grid | A **dimmer, not a step** — and the binary and mass channels fall together. | The half-mute λs (0.23/0.29/0.36) are interpolations and are **plotted nowhere**. Five frozen grid points, no curve. |
| **4** the 12 × 12 matrix | A dark diagonal on a near-white grid — and `silver`'s *column* is the fragile stripe, not its row. | Every cell is annotated with its own hits/n, and **every cell is n ≤ 3** — the gate lives in the pooled arms, never in a cell. |
| **5** M4 floor reads | Why the verdict says AS-SCORED ONLY: the item-level bar ends above 0.5, the concept-level bar ends below it. | The gate reads the *lower bound*, so point on the bar ends, not the dots. |
| **6** collateral asymmetry | Primes cluster tight and high; probes are bimodal with a tail to 0.5. That bimodality is *why* Figure 5's two reads disagree. | Denominators differ per mark (12 deletions × the concept's gated items; 11 × for a subset concept) — the labelled marks carry their own. |

**If asked "did you draw these to flatter the result?"** — the script is committed, it is
deterministic and headless, it reads only the committed result JSONs, and it prints every
plotted number with the JSON key it came from. It computes exactly one thing: `hits / n`,
where a file records the pair instead of the rate. It never smooths, fits, interpolates,
re-bins, pools arms the runners didn't pool, or invents an error bar — every interval
drawn is a recorded `wilson_95` or `newcombe_*` endpoint. Run
`uv run --with matplotlib docs/paper/figures.py` and diff the printout against the
paper's tables.

---

## Provenance table — claim → number → source

Any of these can be pulled up live. JSON paths are the field to read.

| Claim | Number | Source |
|---|---|---|
| Anchor reproduced bit-for-bit | 0 mismatches / 840 cells ×3; mass exact 840/840 | `docs/M0-BRIEF.md` results; `results/anchor-*.json` |
| Anchor specificity at 1.5B | +0.727 [+0.471, +0.868] | `results/anchor-qwen2.5-1.5b-instruct.json` → `late_switch_specificity` |
| M1 gate *(Fig 1)* | +0.656 [+0.517, +0.763] / +0.636 [+0.443, +0.759] | `results/m1-battery-*.json` → `breadth_contrast.newcombe_control_minus_primed_late_naming` |
| M1 gated n | 38 / 61 / 44 of 180 | same → `competence.gate_greedy` |
| M1 arms | `primed_late` 0/38, 0/61, 6/44; `control_late` 17/38, 40/61, 34/44 | same → `naming_success_gated` |
| M1 prevalence, UNDERPOWERED | 4/8, 9/11, 6/8 | same → `prevalence.cell` |
| Bias runs against the finding | control said concept in 3 tokens 17/17, 46/40, 36/34 | same → `greedy_3_texture` vs `naming_success_gated` |
| Re-score (labelled reanalysis) | gated 38→69, 61→105, 44→116; +0.478 / +0.762 / +0.690 | `results/m1-rescore-*.json` → `oracles.prefix` |
| Re-score reproduces M1 exactly | `true` ×3 | same → `reproduces_published_first_token_cell` |
| New-items-only contrast | +0.278 / +0.545 / +0.478 (first-token) | same → `per_source.first_token.m1-new` |
| M2 gate *(Fig 1)* | +0.853 / +0.794 at 1.5B; +0.750 / +0.688 at 3B | `results/m2-depth-*.json` → `localization_contrast` |
| M2 window sweep *(Fig 2)* | 1.5B: 33,32,27,28,28,27,25,23,23,1,**0**,0 of 34 | same → `window_map[*].cell` |
| Band shading in Fig 2 | L9–L21 / L11–L24 / L14–L32 | same → `band` |
| M2 dose curve *(Fig 3)* | 1.5B 34,20,3,1,0 of 34 (mass .913,.594,.115,.037,.017) | same → `dose_curve` |
| Half-mute λ ≈ 0.23/0.29/0.36 | **INTERPOLATED, not measured — quoted in prose, plotted nowhere** | `docs/M2-BRIEF.md` — the brief says so itself |
| Unequal band thirds | 4/4/**5**, 4/4/**6**, 6/6/**7** | `results/m2-depth-*.json` → `thirds` |
| Equal-width control | 1.5B L11–L16 25/34 vs late 0/34; 3B L12–L18 29/32 vs 3/32 | same → `window_map` |
| M3 clause (1) *(Fig 1)* | +0.971 [+0.867, +0.983] / +0.881 [+0.731, +0.943] | `results/m3-matrix-*.json` → `specificity_contrast.clause_1_pooled` |
| M3 clause (2) *(Fig 1)* | +0.950 [+0.814, +0.978] / +0.891 [+0.730, +0.947] | same → `clause_2_within_category` |
| M3 arms | diagonal 0/28, 0/34, 3/32; off-diagonal 279/308, 363/374, 343/352 | same → `pooled_arms` |
| **Every cell of Fig 4** | 144 cells × 3 subjects, each `hits`/`n`/`rate` | same → `matrix[*].cell` |
| `silver` row damages nothing | 27/27, 31/31, 31/31 | same → `row_profiles.silver.collateral_all` |
| `silver` column is the most fragile | 7/11, 27/33, 6/11 | same → `column_profiles.silver.fragility_all` |
| Category-block **null** at 1.5B/3B | +0.028 [−0.010, +0.091]; +0.020 [−0.016, +0.079] | `docs/M3-BRIEF.md` results (**the Newcombe is brief-only; the arms are in `pooled_arms`**) |
| M4 gate arm | 41 / 71 / 84 | `results/m4-strip-*.json` → `competence.gate_arm_n` |
| **M4 headline** *(Fig 5)* | 11/41 = 0.268; **51/71 = 0.718 [0.605, 0.810]**; **63/84 = 0.750 [0.648, 0.830]** | same → `vocabulary_sparing.gate_arm` |
| **M4 concept-level (the honest quote)** *(Fig 5)* | **24/41 = 0.585, lower 0.434**; **26/43 = 0.605, lower 0.456** | same → `vocabulary_sparing.conservative_reads[concept-level]` |
| M4 verdict strings, verbatim | `VOCAB-SPARING (…) — AS-SCORED ONLY (concept-level …)` | same → `vocabulary_sparing.verdict` |
| Residual-conservative read (clears) *(Fig 5)* | 49/71 lower 0.575; 62/84 lower 0.635 | same → `conservative_reads[residual-conservative]` |
| The 0.5 bar drawn in Fig 5 | 0.5 | same → `vocabulary_sparing.bar` |
| Two cross-checks, two generations | M1 255/255 and M3 468/468 cells, mass exact, ×3 | same → `m1_crosscheck`, `m3_crosscheck` |
| No prime is a wrecking ball *(Fig 6, left)* | 1.5B rows 63/71–67/71; 3B 77/84–83/84 | same → `row_profiles[*].collateral_non_subset` |
| Fragile columns *(Fig 6, right)* | `copper` 6/12, `mosquito` 8/12; `eagle` 8/12, `platinum` 9/12 | same → `column_profiles[*].fragility` |
| Zero-collateral columns *(Fig 6)* | 32 of 53 at 1.5B; 33 of 55 at 3B | same → `column_profiles[*].fragility` (hits = n) |
| Category block **does not** dissolve | 22/29 vs 769/823; 35/53 vs 913/955 | same → `new_pool_arms.{within_category, cross_category}` |
| Zero-gated concepts (upward bias) | 25 / 7 / 5 | same → `competence.zero_gated_non_subset_concepts` |
| Span residual cells | 0 / 27 / 21 (0/26/21 in the gate arm) | same → `residual_cells` |
| Cost, suite | $0; 396 tests green (390 pass with no network) | briefs' wall-clock sections; `HANDOFF.md` records the suite count and CI state |
| Every figure's plotted values | printed with its JSON key on every run | `uv run --with matplotlib docs/paper/figures.py` |

---

## Anticipated Q&A

**"Why is this not just a reproduction?"**
Because there is nothing published to reproduce. The effect was found *inside* my own
replication of the Jacobian lens, in a stage the seed paper does not contain. The anchor
is dim-stage's own recorded S4b result, and I re-run it bit-for-bit before measuring
anything new. The seed paper is cited by URL as intellectual context — it has no arXiv
ID, and I claim nothing of it.

**"Your headline says VOCAB-SPARING. Isn't that overclaiming?"**
That's exactly why the label carries AS-SCORED ONLY *inside* the verdict string. The
item-level floor clears the bar; the concept-level floor's lower bound does not — 0.434
and 0.456. Both reads were pre-registered before any new cell ran, and the brief
pre-committed the concept-level numbers as the ones to quote. The qualifier is attached
by the runner, conditionally, not written by me after seeing the result. Figure 5 is the
whole argument in one picture: same cells, two pre-registered ways to count them, and the
lower bounds land on opposite sides of the line.

**"Why is a null a result?"**
Because the gate was written before the run and can only be read one way afterward. The
dose curve's null against a step function is the answer to the kickoff's own question:
whatever the direction carries, the ability to emit the word degrades continuously.
M3's category-block null is a real null *for that arm* — and M4 shows exactly why calling
it general would have been wrong. If I only reported nulls I liked, none of my gates would
mean anything.

**"Why Wilson intervals rather than a normal approximation?"**
Because most of these cells are at or near 0 or 1 — diagonal cells of 0/34, clean cells of
105/105. The normal approximation gives intervals that run past 0 and 1 and are badly
wrong at the extremes; Wilson stays inside [0, 1] and behaves at small n. For differences
between two arms I use Newcombe's method, built from the two Wilson intervals. One honest
caveat: my arms are *paired* (the same items in both) and Newcombe assumes independence.
For positively correlated arms that **widens** the interval — it can cost me power, it
cannot manufacture a positive.

**"Why don't your sweep and dose figures have lines through them?"**
Because I didn't measure the points between the points. The window sweep is a stride-2
grid and the dose curve is five frozen λ values; a line through them would draw values
that were never run, and the smoothed version is exactly how a five-point grid gets
mistaken for a measured curve. Same reason the half-mute λs (≈ 0.23 / 0.29 / 0.36) are in
the prose and on no axis — they're linear interpolations between two grid points and the
brief labels them that way. The mass channel in Figure 3 is the non-interpolated
companion: it moves continuously because it *is* continuous, not because I drew it that
way.

**"What's the un-validatable residual?"**
I never measured *why* the late third is special, whether this direction is the same
object the seed paper's lens is about, or anything above 3B. The window sweep is
structurally thin above the band — no window is ever fully above it — so "the switch is
late" is well-measured on its early side and weakly probed on its far side. And the claim
is scoped to the *measurable* vocabulary: 25 / 7 / 5 concepts gate zero items, a
selection that plausibly enriches for robust concepts and biases my floor upward.

**"Why these models?"**
Qwen2.5-0.5B/1.5B/3B-Instruct because the anchor was measured on exactly them, the lenses
were already fitted for them, and all three run locally on MPS forward-only at $0. 0.5B is
carried through every stage but is never gate-bearing — the predecessor had already
recorded non-specific damage at that scale, so it is read only under a standing
any-direction-damage frame.

**"Two of your findings correct earlier stages. Doesn't that undermine them?"**
They re-scope, they don't retract — and both earlier stages' published numbers stand
untouched. `silver` was labelled non-specific from a single control cell; the matrix
showed that was a fact about silver's *column* (its row damages nothing at any scale) —
look at Figure 4 and the row is uniformly light while the column is the visible stripe.
Category-block collateral looked like it dissolved with scale; the strip showed M3's
within-category arm was 30 of 34 pairs *countries*, and over ten categories it doesn't
dissolve. The transferable lesson: **a single control cell measures a cell, not a row**,
and an arm's composition is part of what it measured. Both were findable only because
every stage re-runs its predecessor's recorded cells rather than trusting them.

**"What would you do next?"**
Two designed-and-declined stretches are banked: 7B on a rented GPU for the
specificity-versus-scale curve, and a lexical-versus-semantic scope test — if I delete
`France`, can the model still say *French*, *Paris*, a translation? That second one is the
question that decides whether this is a **token** mute button or a **concept** mute
button, and I genuinely don't know the answer. Its brief also owes one decision before it
can freeze anything: what counts as a word boundary for non-ASCII forms, which
`oracle.py`'s `_BOUNDARY` currently leaves open.

**"Anything broken you're not hiding?"**
Three, all recorded and none affecting a number: M4's frozen gate wording promises a
per-pair degeneracy readout the runner doesn't compute (byte-frozen, so it's disclosed
rather than patched — and I don't quote that clause); a battery re-parse sits outside its
`try/except` and would traceback instead of exiting cleanly (unreachable in one process);
and the CI job is still *named* `offline-suites` while now fetching four tokenizer repos
per push — 390 of 396 tests pass with no network, so a red build there is network, not
logic. Also: CI genuinely ran zero tests until 2026-07-29, so any green badge before that
date certifies syntax, not behaviour.

---

## Vocabulary crib

| Term | One plain line |
|---|---|
| **Jacobian lens** | A fitted map from a model's internal activations to per-word directions. |
| **Direction / concept vector** | The lens's row for one word — the pattern that word's presence writes into the activations. |
| **Projection removal (k = 1)** | Subtract out exactly the component of the activation pointing along one direction; leave everything else. Forward-only, no retraining. |
| **λ (dose)** | How much of that component to remove. λ = 1 is all of it, λ = 0.25 is a quarter. |
| **Workspace band** | The contiguous layer range the lens was fitted over; "late third" is its last third. |
| **Prime / probe** | The concept whose direction you *delete* (prime) versus the concept you then *ask about* (probe). |
| **Diagonal / off-diagonal** | Diagonal = delete A, ask about A (the mute). Off-diagonal = delete A, ask about B (the collateral). |
| **Competence gate** | An item counts only if the model answers it correctly with nothing ablated. Decided on the clean arm, before any intervention. |
| **Greedy decoding** | Always take the single highest-probability next token — no sampling, so the readout is deterministic and reruns are bit-identical. |
| **Oracle** | The fixed rule deciding "did the model say the word". Here: does the 3-token greedy span *open with* the spelling at a word boundary, case-insensitive. Never an LLM judge. |
| **Concept mass** | The softmax probability assigned to the concept's token — a graded channel beside the yes/no one. |
| **Wilson interval** | A confidence interval for a proportion that stays inside [0, 1] and behaves at small n and at 0/1. |
| **Newcombe interval** | A confidence interval for the *difference* of two proportions, built from their two Wilson intervals. |
| **CI-clean** | The difference's interval excludes zero. If it includes zero, it's a null. |
| **UNDERPOWERED** | Fewer than 20 trials in the cell — pre-declared to support no claim, whatever it shows. |
| **Degeneracy guard** | A check that an arm hasn't collapsed onto one repeated wrong answer, which would fake a clean result. |
| **Pre-registration / frozen gate** | The pass/fail rule *and its exact verdict wording* written as code before the first run, then never edited. |
| **Bit-for-bit cross-check** | Re-running previously recorded cells and demanding identical outputs, before reading any new cell. |
| **AS-SCORED ONLY** | This project's pre-declared qualifier: the headline holds under the scoring rule used, and a pre-registered alternative scoring does not clear the bar. |
| **`not shown`** | The lineage's null label — failing a lower-bound test does not establish the opposite, so the failing verdict never asserts one. |
| **Interpolation (and why it's absent)** | Reading a value *between* two measured grid points. It is quoted in prose where the brief did so and labelled as such — and never plotted, because a drawn line asserts unmeasured values. |

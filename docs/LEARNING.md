# LEARNING.md — teaching notes, stage by stage

Plain-English notes on the ideas each stage turned on, per the teaching
standard: every jargon term defined where it first matters.

## M0 — port + anchor gate (2026-07-27)

**What "porting" actually risks.** Copying code between repos feels safe, but a
measurement instrument is code + data + environment. M0 treated all three as
suspects: the code was ported verbatim with each function's source cited, the
data (lenses, items, anchor results) was copied with **SHA256 fingerprints** (a
cryptographic hash — a short string that changes if even one byte of the file
changes, so a match proves the copy is exact), and the environment was **pinned**
(exact library versions written into `pyproject.toml` instead of ranges).

**Why version pins mattered here.** A fresh dependency resolve gave
`transformers 5.14.1`; dim-stage's recorded runs used `5.13.1`. A minor library
bump can legitimately change floating-point kernels — same math, slightly
different rounding — which can flip a borderline greedy choice. Pinning to
dim-stage's exact versions is why M0 didn't just match the discrete outcomes:
every softmax probability reproduced to the last bit (840/840 cells × 3
subjects). "Bit-for-bit" stopped being aspiration and became an observation.

**Determinism is the lever that makes a hard gate fair.** Every readout in this
lineage is **greedy decoding** (always take the single highest-probability next
token — no sampling, no randomness). Deterministic readouts mean the correct
expectation for a faithful port is *exact equality*, so the gate can demand 0
mismatches and any deviation is a real defect, not noise. With sampled outputs,
no such gate could exist.

**The anchor-gate pattern.** Before measuring anything new with a moved
instrument, re-run an experiment whose answer you already recorded and demand
the identical result. It's the lab-science habit of calibrating a scale with a
known weight. The gate was frozen as code — comparison fields, INVALID
semantics, wording — *before* the first comparison ran, so a mismatch couldn't
be rationalized after the fact.

**What the gate certifies — and what it doesn't.** PASS means the ported
operator, band conventions, prompt construction, grading, and environment are
the same instrument that produced S4b. It does *not* re-argue whether S4b's
finding is interesting or its gate wording was right — those are settled
records. M0 transfers trust; it doesn't mint it.

**One number worth keeping.** The whole three-subject certification — 2,520
compared cells — ran locally on the laptop's GPU (MPS), forward passes only,
for $0. Ablation (deleting a direction) needs no gradients; only lens *fitting*
does, which is why the 7B stretch is the only line item with a budget.

## M1 — breadth battery (2026-07-28)

**What a control arm is actually for.** M1's headline isn't "ablating a
concept's direction silences it" — that alone is compatible with a boring
explanation: maybe deleting *any* direction at the late band scrambles the
output. The `control_late` arm exists to kill that alternative. It performs the
identical surgery, same layers, same k = 1 projection removal, but on a
*different same-category* concept's direction. If naming survives the control
deletion and dies under the concept's own, the damage is **concept-specific**,
not generic. That contrast — not the mute itself — is what M1 gates on. Design
lesson: a result is only as strong as the alternative explanation you built an
arm to rule out.

**"CI-clean" means the honest interval, not the point estimate.** At 1.5B the
gap was +0.656 with a Newcombe 95% interval of [+0.517, +0.763]. The claim is
licensed because the whole interval sits above 0, not because 0.656 is big. Had
the interval been [−0.02, +0.9], the same point estimate would have licensed
nothing. This is the project's "a cell whose CI overlaps its neighbour is not a
result" rule doing its job.

**A conservative error is not the same as a bug.** The two arms are measured on
the *same* gated items (paired), but `newcombe_diff` is a method for two
*independent* samples. That's a genuine mismatch — and it makes the interval
**wider** than it should be. So it can cost a real effect (a false null) but can
never manufacture a fake one. Knowing which *direction* an approximation errs in
is often more useful than removing it: an error that runs against your own claim
is one you can ship while owning it.

**Anti-monotone denominators — a statistical trap worth recognizing.** M1's
prevalence headline counts only concepts with *all three* items gated. That
denominator **shrinks** as you write more clues per concept, because a concept
needs every one of them to pass. So the instinct "trials are free, add more
items for power" would have *reduced* power on that cell. Only widening the
roster (more concepts) raises it. Pre-declaring the UNDERPOWERED tag before the
run is what kept this from looking like a discovered disappointment.

**Pre-committing a rule means testing it against data you already have.** The
degeneracy disposition — what to do if a condition's answers collapse onto one
attractor token — was written *before* M1 ran, but it was checked against the
already-recorded anchors first, to confirm it wouldn't have fired spuriously on
either gate-bearing subject. A pre-committed rule you haven't sanity-checked is
just a guess with better manners.

**The lesson M1 actually taught: your readout decides what you can see.** The
oracle is the greedy *first token*, so a concept is scorable only when its
spelling at the answer position is one token. For 26 of 60 roster words the bare
spelling isn't: the model answers "Mercury" but emits `'Mer'` first, and the gate
records a miss. (Not *never* — the same word is one token *with* a leading space,
so those 26 do occasionally gate when the model emits that form; `jade` did, 1–2
times per subject. The bias is heavy, not absolute, and saying so is the
difference between a caveat and an overclaim.) Whole
categories — planets, musical instruments — scored zero gated items on all three
subjects for this reason alone. The finding survived (the contrast is computed
*inside* the gated set, and the bias runs *against* the claim), but the claim's
**reach** shrank: M1 shows breadth over the vocabulary the readout can see, not
over the vocabulary. Measurement instruments don't just add noise — they
**select** which parts of the world are visible, and that selection can be
invisible until you build a second readout to look at it.

**Why adding the first-3-greedy readout mid-stage was legitimate — and why
re-scoring the gate would not have been.** The texture readout never gates and
never enters a verdict; adding it and re-running left all 4,860 primary cells
bit-for-bit identical (verified by diff). Changing the *oracle* after seeing that
the oracle was costing you items would be a different act entirely — that is
choosing a measurement because you know what it will do to your number. It goes
in a decision, before the next run, with the old numbers still reported.

### Recall questions

1. `primed_late` naming was 0/61 at 1.5B. Why isn't that, on its own, evidence of
   a concept-specific off-switch — and what number in the same row makes it one?
2. The prevalence denominator counts only concepts with all 3 items gated. If you
   wanted a tighter confidence interval on that number, why would writing a
   fourth clue per concept be the wrong move, and what is the right one?
3. Planets scored 0 gated items on all three subjects. Does that mean the models
   don't have an off-switch for planets? What evidence in the run answers this,
   and which direction does the readout's bias push the control arm?

## M2 — localization + dose (2026-07-28)

**A pre-registration you can *compute* is worth more than one you can only
promise.** M2's expected-power section didn't project its sample sizes — it
*derived* them. Gating depends only on the clean arm, which is deterministic and
was already recorded by M1, so the brief could state "the gated ns will be 28,
34, 32" before any run. They came in at 28, 34, 32. That flips the usual
relationship: a disagreement wouldn't have been a power surprise to explain
away, it would have been a cross-check failure meaning the instrument had
drifted. When a number is knowable in advance, pinning it turns a hope into a
tripwire.

**Changing a measurement mid-project is legitimate exactly once you make it a
decision.** M1 discovered its readout was the thing limiting its reach (26 of 60
words invisible to a one-token oracle). The tempting move — rescore M1 and
report the better numbers — is the illegitimate one, because you'd be choosing a
measurement *after* seeing what it does to your result. The legitimate move is
what D9/D10 did: freeze the new oracle in a decision before any new run, keep
the old numbers as published, and put the re-score beside them under a
REANALYSIS label. Same arithmetic, completely different epistemics.

**Make the reanalysis prove itself against the analysis.** `m1_rescore.py`
recomputes M1's *published* first-token numbers from the same file and refuses to
write anything unless they match exactly. It costs three lines and it means the
widened numbers can't be an artifact of a parsing bug — a reanalysis that can't
reproduce the analysis it sits beside is not evidence of anything.

**Refactors are safe when a bit-for-bit check is watching.** M2 precomputes the
lens vectors once per (layer, word) instead of rebuilding them per item — a real
change to hot code. It needed no separate argument for safety: the M1 cross-check
compares 108 reused cells bit-for-bit, so if the caching had moved a single
value, the run would have exited INVALID before reading a new cell. A strong
enough invariant lets you refactor without holding your breath.

**A guard that can't fire isn't a guard.** M1's degeneracy rule listed `clean`
among the arms whose collapse would sink the verdict. It was inert — `clean` is
the *gate* arm, so on the gated cell its answers are correct by construction and
can't concentrate on one token. M2's run makes that visible: the wrong-opening
share on `clean` is exactly 0.000 on all three subjects. The related lesson is
that widening the oracle broke the old guard's *meaning* too — under a span rule,
a good arm legitimately concentrates its first tokens on fragments that open
correct answers, so the guard had to be re-aimed at the arm's *wrong* answers
only.

**Pre-register something you expect to fail.** The subset deliberately included
`silver`, chosen because M1 showed its *control* direction muted it too. It
behaved exactly that badly (1.5B: primed_late 0/3 **and** control_late 0/3,
damaged at every depth). Keeping a known counter-example inside the pooled
average is what stops the aggregate from being a curated one.

**The map's shape was the payoff, not the gate.** The gate only asked "is late
different from early and middle?". The window sweep answered questions nobody
gated on: the effect has a *floor* of depth-nonspecific damage that shrinks with
scale (≈48% of naming at 0.5B, ~0–6% at 3B for out-of-band windows), the
transition is a cliff at 1.5B but a ramp at 3B, and partial removal produces
intermediate naming — a dimmer, not a step, with the half-mute point sliding
right with model size. Descriptive results don't need a gate to be the most
interesting thing in the milestone; they need to be clearly labelled as
descriptive.

### Recall questions

1. The M2 brief predicted gated ns of 28 / 34 / 32 *before* the runs, and the
   runs returned 28 / 34 / 32. Why was that prediction possible at all — and if
   a run had come back with 33 instead of 34, what would the correct response
   have been, and why is it *not* "note the power difference and continue"?
2. M2 changed the oracle that decides whether the model "said the word", which
   directly changes every naming number. Two things kept that from being
   result-shopping. Name both — and explain why the M1 cross-check still worked
   as a check even though the two milestones score cells with different oracles.
3. At 0.5B, naming under the late-window ablation is 0/28 while windows entirely
   outside the band still leave only ~15/28 intact. At 3B the out-of-band
   windows leave 30–32/32 intact. Both subjects returned LATE-LOCALIZED. What
   does the 0.5B curve tell you that its verdict alone does not, and which
   pre-declared frame does it land in?

## M3 — the specificity matrix (2026-07-28)

**One control cell can be wrong about *which direction* an effect runs.** M1 and
M2 measured specificity the way S4b did: delete one same-category alternative's
direction and check the concept still comes out. `silver` failed that check in
M1, so D11 pre-registered it as the *non-specific anti-example* — the concept
whose direction was expected to damage everything. The matrix says the opposite:
deleting silver's direction damages **nothing** at any scale (27/27, 31/31,
31/31), while silver's *column* is the most fragile in the grid. The single
control cell had sampled silver's column and been read as a fact about silver's
row. A 1-cell probe of a 2-dimensional object cannot tell you which dimension you
measured; the matrix is what makes the transpose visible. Note that this doesn't
retract anything M1 or M2 published — their numbers stand — it re-attributes what
those numbers were *about*.

**Design out a confound instead of disclosing it.** M2's round-1 review found
that its gate compared a 4-layer ablation against a 6-layer one, because
`sub_band_thirds` hands the late tier the band remainder. M2 could only *own* it
(its wording was byte-frozen with its artifacts). M3 didn't have to: holding
depth and dose fixed means every cell in the matrix ablates the identical layer
set at the identical strength, so the two arms the gate compares differ in
exactly one thing. The frozen wording says so affirmatively rather than letting
the caveat quietly lapse — a retired confound should leave a note saying it was
retired, or the next stage re-introduces it by accident.

**A qualifier that can create a verdict is not a qualifier.** The collateral-floor
rule went through four drafts at the brief's review, and each fix was about
keeping it from doing more work than it should. The final shape: it can only
*scope* a MATRIX-SPECIFIC or a "not shown", never produce one, never rescue one,
and never explain why 0.5B is off-gate (that was always the pre-declared scale
frame). Getting the denominator right mattered too — the pooled per-cell rate
inflates n by 11× and under-fires, a survives-all-11 conjunction is decided by
correlation structure nobody measured, and the cluster-mean of per-item survival
fractions is the one that tracks the quantity the floor is *about*. All three
agree here, because the floor came in clear on every subject; pre-registering the
honest one anyway is what made that agreement meaningful rather than lucky.

**Validate before you load.** M2's runner loaded a full checkpoint before it
checked whether its inputs made sense, so every `--dry-run` and every wrong-arm
exit paid for a model it never used. The M3 cut reads the subject's shape from
its *config*, validates everything validatable — including the new tokenizer
bars — and only then loads weights, re-asserting the loaded model's shape against
the config so the cheap path can't quietly disagree with the measured one. The
test that pins it is the honest kind: it makes `from_pretrained` raise, so the
dry-run passes only because nothing touched it.

**Pin the premise, not just the conclusion.** D9(b)'s soundness rests on "3
tokens ≥ the longest roster form" — a sentence in a brief that no code checked.
D18 turns it into a run-time bar on the subject's own tokenizer, and widening it
from the bare form to `max(bare, leading-space)` was not pedantry: `opal` is 1
token bare and 2 space-prefixed on all three tokenizers, and the recorded span
holds the *emitted* form. A premise that only lives in prose drifts the first
time a tokenizer revision ships.

**The gate was the least interesting thing in the milestone.** MATRIX-SPECIFIC
passed at every scale with enormous margins (1.5B: 363/374 off-diagonal vs 0/34
diagonal). What the 126 never-measured ordered pairs bought — 132 off-diagonal
pairs, less the 6 that are M1's own country control cells — was structure the
gate never asked about: collateral concentrates on a handful of fragile *probes*
rather than being caused by damaging *primes*; category-block collateral is real
and CI-clean at 0.5B (+0.105 [+0.032, +0.196]) and dissolves into noise by 1.5B;
and the only diagonal leaks anywhere are Egypt and October at 3B — precisely the
two concepts pre-registered as the leaky-switch stratum. Descriptive findings
earn their keep by being pre-registered as descriptive, not by being small.

### Recall questions

1. `silver` entered the subset as the pre-registered "non-specific anti-example",
   and the matrix shows its row causing zero collateral at every scale while its
   column is the most damaged in the grid. Explain what M1's single control cell
   actually measured about silver — and why this is a *re-attribution* rather
   than a retraction of M1's published numbers.
2. The gate has two clauses, and clause (1) alone would have passed at every
   scale. Why was clause (2) added at the brief's review, what would have been
   dilutive about resting on clause (1), and why do October's and silver's items
   drop out of clause (2) *by construction* — including what would have gone
   wrong if they had been left in?
3. The collateral-floor readout collapses each gated item to its *fraction* of 11
   deletions survived, then reads `wilson(⌊Σ fractions⌋, gated items)`. Name the
   two simpler readouts this replaced and the specific way each one lies —
   and explain why it matters that the qualifier can never turn a "not shown"
   into a result.

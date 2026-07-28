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
oracle is the greedy *first token*, so a concept is only scorable if its spelling
at the answer position is one token. 26 of 60 roster words aren't: the model
answers "Mercury" but emits `'Mer'` first, and the gate records a miss. Whole
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

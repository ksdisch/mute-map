# mute-map

**Cartography of a late-band output off-switch in small language models.**

During [dim-stage](https://github.com/ksdisch/dim-stage) — an independent rebuild
and small-scale measurement of Anthropic's
[Jacobian lens](https://transformer-circuits.pub/2026/workspace/index.html) — one
effect survived every control: **removing a single concept's lens direction at the
late third of the workspace band makes the model unable to say that word** (naming
0/n, concept probability mass ≈ .000), concept-specifically at 1.5B
(control − primed = +.727 [+.471, +.868], CI-clean), with specificity emerging
across 0.5B → 3B.

mute-map characterizes that switch properly, with the same methodology as its
parent project (deterministic logit-based grading, Wilson/Newcombe CIs,
pre-registered gates frozen as code before any run):

| Milestone | Axis | Question |
|---|---|---|
| M0 | Anchor | Does the ported instrument reproduce the S4b cells exactly? |
| M1 | Breadth | How much of the (measurable) vocabulary has an off-switch? |
| M2 | Localization + dose | Where does the switch live, and how much removal does it take? |
| M3 | Specificity | The full prime × probe collateral matrix. |
| M4 (close-out) | Vocabulary collateral | Does deleting one concept spare the *other 48*? |
| S1 (banked) | Scale | The specificity-emergence curve, extended to 7B. |
| S2 (banked) | Scope | Token mute button or concept mute button? |

**The honest framing:** an effect *found during a replication, characterized
here* — the anchor is dim-stage's own recorded result, not a paper claim.

**Status: M3 PASSED 2026-07-28 — the v1 chain is complete; close-out stage M4
is in flight — brief reviewed, decisions D19–D22 frozen 2026-07-29, runner not
yet written.** On the full 12 × 12 prime × probe matrix at the switch's home
band, deleting one concept's direction silences that concept and leaves the
other eleven almost untouched: at 1.5B the diagonal names **0/34** while the
pooled off-diagonal names **363/374** (+0.971 [+0.867, +0.983]); at 3B 3/32 vs
343/352 (+0.881 [+0.731, +0.943]). The same contrast restricted to
*same-category* pairs — the arm the lineage's single control actually tested —
is +0.950 and +0.891, likewise CI-clean. Of the matrix's 132 ordered
off-diagonal pairs, **126 had never been measured before** (the other 6 are
M1's own country control cells, which this run re-certifies bit-for-bit before
it reads anything new). What the gate did not ask: collateral concentrates on
a few fragile **probes** rather than being caused by damaging **primes**
(`silver`'s direction damages *nothing*, while `silver` itself is the most
fragile probe in the grid — inverting what a single control cell had
suggested), category-block collateral is CI-clean at 0.5B and dissolves by
1.5B, and the only imperfect mutes anywhere are `Egypt` and `October` at 3B —
the two concepts pre-registered as the leaky-switch stratum.

**M2 PASSED 2026-07-28** — on a pre-registered 12-concept subset, the
off-switch is **localized to the late third**: removing the concept direction
there mutes the word, while removing that same direction at the early or middle
third leaves most naming intact (early − late naming +0.853 [+0.668, +0.936] at 1.5B
and +0.750 [+0.531, +0.857] at 3B; middle − late +0.794 and +0.688, all
CI-clean). Two descriptive findings the gate never asked for: ablating the
direction *outside* the band is nearly free at 3B (~0–6% of naming) but costs
≈48% at 0.5B, and partial removal is a **dimmer, not a step function** — the
half-mute point slides right with scale (λ ≈ 0.23 / 0.29 / 0.36).

**M1 PASSED 2026-07-28** — over a frozen 60-concept / 180-item battery, the
off-switch is **concept-specific at 1.5B and 3B** (control − primed late naming
+0.656 [+0.517, +0.763] and +0.636 [+0.443, +0.759]); 0.5B shows it too (+0.447
[+0.275, +0.603]) though it is never gate-bearing. **M0 PASSED 2026-07-27** and
is re-certified bit-for-bit on every later run — M1 reuses S4's 60 items as a
live anchor check, and M2 reuses M1's own recorded cells the same way (108/108
cells exact, ×3 subjects).

M1's owned caveat was that the greedy-*first-token* oracle scores a concept
reliably only when its bare spelling is one token — 34 of the 60 words — which
left planets and musical instruments at 0 gated items on every subject. M2 opened
by fixing the instrument rather than the numbers: the oracle widened to a
deterministic prefix rule on the recorded 3-token span (decision D9b, frozen
before any run), M1's published numbers stand untouched, and the re-score is
published beside them as a labelled reanalysis (D10a) in which the contrast
survives on every subject and the dark categories light up. **The v1 chain
(M0–M3) is now closed.** In progress: close-out stage **M4, the vocabulary
collateral strip** (12 characterized directions × all 60 concepts), which
measures the one thing M3's near-white grid does *not* show — that deleting
France spares the other 48 concepts. Its brief is adversarially reviewed and
its decisions (D19–D22) were frozen 2026-07-29, before any runner code exists
— the lineage's freeze-before-code discipline. The S1 (7B) and S2 (lexical vs
semantic scope) stretches were declined for this repo and banked for a future
seed-hunt. Models: Qwen2.5-0.5B/1.5B/3B-Instruct, local MPS, forward-only;
core chain $0.

Full brief: [`docs/KICKOFF.md`](docs/KICKOFF.md). The 12-idea backlog this was
picked from: dim-stage
[`docs/ideas/jlens-followon-backlog.md`](https://github.com/ksdisch/dim-stage/blob/main/docs/ideas/jlens-followon-backlog.md).

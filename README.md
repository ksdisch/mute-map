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
| S1 (stretch) | Scale | The specificity-emergence curve, extended to 7B. |
| S2 (stretch) | Scope | Token mute button or concept mute button? |

**The honest framing:** an effect *found during a replication, characterized
here* — the anchor is dim-stage's own recorded result, not a paper claim.

**Status: M2 PASSED 2026-07-28** — on a pre-registered 12-concept subset, the
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
survives on every subject and the dark categories light up. **M3 (specificity
matrix) next.** Models: Qwen2.5-0.5B/1.5B/3B-Instruct, local MPS, forward-only;
core chain $0.

Full brief: [`docs/KICKOFF.md`](docs/KICKOFF.md). The 12-idea backlog this was
picked from: dim-stage
[`docs/ideas/jlens-followon-backlog.md`](https://github.com/ksdisch/dim-stage/blob/main/docs/ideas/jlens-followon-backlog.md).

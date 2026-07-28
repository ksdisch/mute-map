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

**Status: M1 PASSED 2026-07-28** — over a frozen 60-concept / 180-item battery,
the late-band off-switch is **concept-specific at 1.5B and 3B** (control − primed
late naming +0.656 [+0.517, +0.763] and +0.636 [+0.443, +0.759]); 0.5B shows it
too (+0.447 [+0.275, +0.603]) though it is never gate-bearing. M0 PASSED
2026-07-27 and is re-certified bit-for-bit on every M1 run (the battery reuses
S4's 60 items as a live anchor check). Owned caveat: the greedy-first-token
oracle scores a concept reliably only when its bare (no-leading-space) spelling
is one token, which is 34 of the 60 — the other 26 can still gate when the model
emits the leading-space form, but rarely do: those 26 concepts contribute just
1, 2 and 1 gated items in total at 0.5B / 1.5B / 3B (all of them `jade`), out of
38, 61 and 44. So M1's breadth holds over *the vocabulary the readout can see*
(`docs/M1-BRIEF.md` results). **M2 (localization + dose) next.** Models:
Qwen2.5-0.5B/1.5B/3B-Instruct, local MPS, forward-only; core chain $0.

Full brief: [`docs/KICKOFF.md`](docs/KICKOFF.md). The 12-idea backlog this was
picked from: dim-stage
[`docs/ideas/jlens-followon-backlog.md`](https://github.com/ksdisch/dim-stage/blob/main/docs/ideas/jlens-followon-backlog.md).

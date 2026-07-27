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

**Status: scaffolded 2026-07-27 — M0 next.** Models: Qwen2.5-0.5B/1.5B/3B-Instruct,
local MPS, forward-only; core chain $0.

Full brief: [`docs/KICKOFF.md`](docs/KICKOFF.md). The 12-idea backlog this was
picked from: dim-stage
[`docs/ideas/jlens-followon-backlog.md`](https://github.com/ksdisch/dim-stage/blob/main/docs/ideas/jlens-followon-backlog.md).

# mute-map

[![CI](https://github.com/ksdisch/mute-map/actions/workflows/ci.yml/badge.svg)](https://github.com/ksdisch/mute-map/actions/workflows/ci.yml)

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

## Results

**Status: M4 PASSED 2026-07-29 — every measurement stage is closed.** The
close-out stage widened M3's probe side from 12 concepts to all 60: keep the 12
characterized directions as the things deleted, and ask *every* item in the
frozen 180-item battery. Deleting any one of those directions at the late third
**spares most of the measurable wider vocabulary** — of the gated items whose
concept is outside M3's twelve, **51/71 = 0.718 [0.605, 0.810]** survive all 12
deletions at 1.5B and **63/84 = 0.750 [0.648, 0.830]** at 3B, both clearing the
pre-registered 0.5 bar. Both verdicts carry the pre-declared **AS-SCORED ONLY**
qualifier: collapsed to one binary per *concept* rather than per item, the same
statistic reads 0.585 (lower 0.434) and 0.605 (lower 0.456) — below the bar — and
the brief pre-committed those as the honest numbers, so they ride inside the
verdict string rather than sitting in prose. 0.5B reads `not shown` (11/41 =
0.268) off-gate, the first measured divergence between the subset-12's robustness
and the wider roster's. The strip physically contains 255 cells M1 recorded and
468 M3 recorded, and reproduced **all 723 bit-for-bit on every subject** before
reading a single new cell — so every sample size was knowable before the run, and
each landed exactly as pre-registered. What the gate did not ask: collateral
still concentrates on fragile **probes** rather than damaging **primes** (no
prime's row falls below 63/71 at 1.5B, while `copper` takes 6/12 and `mosquito`
8/12), and category-block collateral turns out to be real in the wider vocabulary
and *not* to dissolve with scale — reversing an M3 finding whose within-category
arm was 30/34 countries.

**M3 PASSED 2026-07-28** — on the full 12 × 12 prime × probe matrix at the switch's home
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
(M0–M3) closed 2026-07-28, and the close-out stage M4 landed 2026-07-29** —
measuring the one thing M3's near-white grid did *not* show, that deleting France
spares the other 48 concepts. Every stage's gate wording was frozen as code
before its first run, M4's included, and each stage re-certifies its predecessors
bit-for-bit rather than trusting them. The S1 (7B) and S2 (lexical vs semantic
scope) stretches were declined for this repo and banked for a future seed-hunt.
Models: Qwen2.5-0.5B/1.5B/3B-Instruct, local MPS, forward-only; whole project $0.

## Reproducing

Everything is local and free: no API keys, no `.env`; `uv` (Python 3.12+) manages
the venv, and models pull from HuggingFace on first use.

```bash
git clone https://github.com/ksdisch/mute-map && cd mute-map

uv run pytest    # stats ruler + per-stage invariant/gate tests, no model downloads needed
```

The verdicts above are printed straight from the committed per-run JSONs in
[`results/`](results/) — reproducing them needs no model, no lens, no GPU:

```bash
uv run m1_verdict.py   # BREADTH-SPECIFIC at 1.5B and 3B
uv run m2_verdict.py   # LATE-LOCALIZED at 1.5B and 3B
uv run m3_verdict.py   # MATRIX-SPECIFIC at 1.5B and 3B
uv run m4_verdict.py   # VOCAB-SPARING at 1.5B and 3B, AS-SCORED ONLY
```

Re-running a milestone from scratch additionally needs a fitted Jacobian lens per
subject (`lenses/*.pt`, gitignored — copied from local dim-stage copies, K3;
provenance in [`lenses/PROVENANCE.md`](lenses/PROVENANCE.md)) and downloads the
Qwen checkpoint on first use. Each runner supports `--dry-run` (validate inputs
and stop; a wrong-arm input exits `INVALID`) and `--limit` (smoke only, never a
result):

```bash
uv run m1_battery.py --model-id Qwen/Qwen2.5-1.5B-Instruct \
  --lens lenses/qwen2.5-1.5b-instruct-n100.pt --dry-run
uv run m1_battery.py --model-id Qwen/Qwen2.5-1.5B-Instruct \
  --lens lenses/qwen2.5-1.5b-instruct-n100.pt
```

All milestone runs are comfortably local: M1–M3 each ran under an hour per
subject on MPS ($0), and M4 — the largest, at ~4.3× an M1 subject run — stayed
within an afternoon. The anchor re-run (`m0_anchor.py`) is under an hour total
across all three subjects; `m0_anchor.py` is certified post-M0-gate and never
edited, so cut new runners from it rather than modifying it.

## Repo map

| Path | Role |
|---|---|
| [`docs/KICKOFF.md`](docs/KICKOFF.md) | The approved brief — scope, milestones, gates, risks, decisions. **Source of truth.** |
| `docs/M0…M4-BRIEF.md` | Per-milestone design extraction, frozen conventions, deviations table, full results |
| [`docs/DECISIONS.md`](docs/DECISIONS.md) | Append-only log of every frozen decision |
| [`docs/LEARNING.md`](docs/LEARNING.md) | Plain-English teaching notes, milestone by milestone |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Milestone status vs the plan |
| `m0_anchor.py`, `m1_battery.py`, `m2_depth.py`, `m3_matrix.py`, `m4_strip.py` | Milestone runners at the repo root, each cut from its predecessor (`oracle.py` is the one shared exception, K3) |
| `m1_verdict.py` … `m4_verdict.py` | Committed verdict scripts — print each milestone's pre-committed gate wording against `results/` |
| `items/` | Frozen item sets used by the runners |
| `results/` | Per-run JSONs — the recorded measurements this README reports |
| `lenses/` | Fitted Jacobian lenses (gitignored — sourced from local dim-stage copies; `PROVENANCE.md` is tracked) |

The 12-idea backlog this was picked from: dim-stage
[`docs/ideas/jlens-followon-backlog.md`](https://github.com/ksdisch/dim-stage/blob/main/docs/ideas/jlens-followon-backlog.md).

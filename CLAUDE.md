# CLAUDE.md — mute-map

Project conventions and guardrails for working in this repo. Read this first each session.

## What this is

**Cartography of the late-band J-lens output off-switch** found in dim-stage's S4b:
k = 1 projection removal of a concept's Jacobian-lens direction at the late third of
the workspace band silences that word, concept-specifically at 1.5B (CI-clean), with
specificity emerging by scale. mute-map maps the switch along four axes — breadth
(M1), localization + dose (M2), specificity matrix (M3) — on Qwen2.5-0.5B/1.5B/3B
locally, with an optional 7B stretch (rented GPU, ≤ $15).

**Source of truth: `docs/KICKOFF.md`** — the approved brief (scope, milestones,
gates, risks, decisions K1–K4). Scope decisions there are settled; don't relitigate.

**The honest framing, always:** this is the lineage's first *original
characterization*, not a reproduction — *an effect found during a replication,
characterized here.* The anchor is our own S4b numbers (dim-stage
`docs/S4-BRIEF.md`), never a paper claim. The seed paper
(transformer-circuits.pub/2026/workspace — no arXiv ID; cite the URL) is context.

## Where we are

**M0 PASSED (2026-07-27):** the ported instrument reproduced dim-stage's
recorded S4b JSONs bit-for-bit, ×3 subjects (0 mismatches over 840 cells each;
`docs/M0-BRIEF.md`). `m0_anchor.py` is certified post-gate — cut new runners
from it, never edit it.

**M1 PASSED (2026-07-28):** BREADTH-SPECIFIC at 1.5B and 3B over a 60-concept /
180-item battery (`docs/M1-BRIEF.md`).

**M2 PASSED (2026-07-28):** LATE-LOCALIZED at 1.5B and 3B on the pre-registered
12-concept subset; the dose curve is a dimmer, not a step (`docs/M2-BRIEF.md`).
M2 also widened the primary oracle to the greedy-span prefix rule (D9b, frozen
in `oracle.py`) and published the M1 re-score beside M1's standing numbers
(D10a). **Now: M3 — specificity matrix** (brief first, `docs/M3-BRIEF.md`; its
first decision is whether to reuse M2's 12-concept subset).

**Each milestone's `GATE_WORDING` is byte-frozen with its artifacts** —
`m1_battery.GATE_WORDING` and `m2_depth.GATE_WORDING` are never edited; a later
stage freezes its own and records where it departs. Each runner is cut from its
predecessor, not shared with it; `oracle.py` is the one deliberate exception,
shared so the reanalysis and the runner apply a byte-identical rule.

## How to run

- Anything: `uv run <script>` — `uv` (Python 3.12+) manages the venv. Application,
  not a package (`package = false`).
- `uv run pytest` greens the suite (stats ruler + per-stage invariant/gate tests).
- Runners live at the repo root; frozen item sets in `items/`; per-run JSONs in
  `results/`; lens artifacts in `lenses/` (gitignored — sourced from local
  dim-stage copies, decision K3; provenance recorded in M0's brief).
- No API keys, no `.env` — everything local. Models pull from HuggingFace on
  first use.
- **Anchor re-certification** (after touching `harness.py`, `intervention.py`,
  `subject.py`, or the environment pins): the standing `m0_port_gate.py --all`
  compares two committed files and is tautological on its own. First regenerate
  the left side — `uv run python -u m0_anchor.py --model-id <id> --lens
  lenses/<file>.pt` per subject, rewriting `results/anchor-*.json` — then run
  `uv run python m0_port_gate.py --all`.

## Methodology guardrails (load-bearing — do not drift)

- **Deterministic oracles only.** Greedy first-token primary readout (S4's
  "The …" miss-counting caveat kept for anchor comparability; first-3-greedy
  recorded as secondary texture); concept softmax mass as texture. Never an LLM
  judge, never text parsing.
- **Wilson CIs on cells + Newcombe CIs on differences decide every gate.**
- **N ≥ 20 per cell or the verdict is pre-declared UNDERPOWERED.** Trials are
  free — prefer N large where the clock allows.
- **A cell whose CI overlaps its neighbor is not a result.**
- **Pre-commit gates as code — wording included — and dry-run them** (wrong-arm
  input exits INVALID; `--limit` is smoke, never a result) before any real run.
  A pre-committed null is a reportable result.
- **Design-extraction before design-signing:** each milestone brief extracts the
  relevant S4/S4b procedure (and paper context) verbatim before decisions.
- **Deviations are owned** — standing table: naming-only competence gate (vs
  S4b's dual gate), constructed item sets (frozen pre-run), model scale vs
  Claude, lens provenance (no refit, K3).

## Working with Kyle — teaching standard + per-stage rhythm (load-bearing)

Kyle is driving this project to learn interpretability internals deeply and is
sharp but **new to coding jargon** — no CS degree. The job isn't just to ship
code; it's to leave him able to *defend every decision*.

- **Explain-clearly standard.** Plain English first; define **every** jargon term
  the first time it appears, inline; clearer, not longer.
- **Decision-brief format.** For any real choice: 2–3 options in plain terms,
  each with its trade-off, plus a recommendation *and the reason*. Kyle decides.
- **Per-stage rhythm (the docs spine).** *Start of a stage:* plain-terms brief +
  options into `docs/` before coding. *End of a stage:* update `ROADMAP.md`,
  append to `DECISIONS.md`, add teaching notes to `LEARNING.md`, ask 3 recall
  questions. A stage isn't done until its spine updates are committed in the
  same PR as the code.

## Working conventions

- **Keep it lean.** No premature abstractions; one legible deliverable per
  milestone.
- Ported code (`stats.py`, the operator) stays verbatim where possible — every
  divergence from the dim-stage original is a deviations-table row.
- Refetch the paper when needed with `defuddle parse <url> --md -o <file>`
  (never commit it; it's Anthropic's content).

## Project Wiki

This project uses the project-wiki skill (sentinels: `PROJECT.md`, `HANDOFF.md`).
Update `PROJECT.md` status and `HANDOFF.md` whenever work pauses or state
changes; record decisions in `docs/DECISIONS.md` (append-only, starts at M0);
`Wiki/` topic pages are created on first need.

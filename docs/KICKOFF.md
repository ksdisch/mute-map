# KICKOFF — mute-map

_Approved 2026-07-27 (brainstorm + interview + plan gate in one session; parameters
and the plan below are Kyle-signed). Source of truth for scope; per-stage briefs
refine, never relitigate._

## What this is

**Cartography of the late-band output off-switch.** dim-stage's S4b found that
deleting a single concept's J-lens direction (k = 1 projection removal) at the
late third of the workspace band silences that word — naming 0/n, concept mass
≈ .000 — and that the effect is **concept-specific at 1.5B** (control − primed
= +.727 [+.471, +.868], CI-clean, the powered subject) with **specificity
emerging by scale** (0.5B: any-direction damage; 3B: perfectly clean 8/8 control,
UNDERPOWERED n = 8). mute-map maps that switch along four axes:

1. **Breadth** — does most of the (measurable) vocabulary have one, or is it
   item-set-idiosyncratic? (M1)
2. **Localization** — where exactly does the switch live: band thirds → sliding
   window, including outside-band probes? (M2)
3. **Dose** — how much of the direction must be removed (partial-projection λ)? (M2)
4. **Specificity** — the full prime × probe collateral matrix, not one control
   cell. (M3)

Models: Qwen2.5-0.5B/1.5B/3B-Instruct locally on MPS (forward-only — no new fits
for the core chain); optional 7B via rented GPU as stretch.

## Honest framing (the standing line)

This is the lineage's first **original characterization**, not a reproduction:
the anchor is *our own* S4b result, recorded in dim-stage
(`docs/S4-BRIEF.md`, results superseded-in-place JSONs), not a paper claim.
The seed paper's Figure 69 late-band "intention to say" texture is the intellectual
context — always cited as context, never claimed as reproduced. Framing for every
readout: *found during a replication, characterized here.*

## Session parameters (Kyle-signed 2026-07-27)

- **Payoff:** portfolio-first (hiring-manager legibility beats novelty risk).
- **Scope:** standard chain, 2–3 weeks, dim-stage-style pre-registered gates.
- **Compute:** local MPS core; 7B–14B rentals allowed (~$10–30 ceiling); this
  project budgets ≤ $15 and only for the S1 stretch.
- **Name/visibility:** slug **mute-map**, GitHub **public** (portfolio logic —
  the story flows from dim-stage's README into this repo).
- Idea provenance: pick #5 of the 12-idea backlog at dim-stage
  `docs/ideas/jlens-followon-backlog.md` (PR #41). Natural successor project:
  #6 steering pharmacology (shares this repo's rails).

## The key design fix: naming-only competence gate

S4b's power problem (gated n = 5 / 22 / 8) came from the *avoidance* half of its
inclusion/exclusion competence gate. The off-switch is a claim about **naming**,
so mute-map gates items only on "the model names the concept correctly,
unablated" — expected powered cells (pooled n ≥ 100) at all scales, including
the 3B cell S4b left UNDERPOWERED at +1.000. **Owned deviation:** mute-map
measures the switch, not exclusion capacity; comparability with the anchor is
preserved by M0's exact re-run of the S4b protocol.

## Milestones (gates frozen as code, wording included, before each first run)

- **M0 — port + anchor gate (2–3 days, $0).** Scaffold (done at kickoff); port
  stats ruler (done), projection-removal operator, band definitions; source lens
  artifacts from local dim-stage copies with recorded provenance (SHA256 +
  regeneration pointer to dim-stage's fitter). Re-run S4b's core cells in this
  harness. **Gate: shared cells reproduce S4b's recorded values exactly
  (deterministic greedy, 0 mismatches) or the port is INVALID.**
- **M1 — breadth: the battery (~1 week, $0).** ~60 concepts across 8–10
  categories: S2/M3 measured vocabularies extended by new frozen lists
  (single-token filter); items by S4's constrained-construction recipe
  (~2–3 clue-sentence naming items per concept), frozen in `items/` pre-run.
  Conditions: clean, primed_late, control_late. **Gate: pooled primed_late
  naming CI-cleanly below control_late (Newcombe excludes 0) at 1.5B AND 3B.**
  Per-concept switch-rates + per-category structure descriptive (Wilson CIs).
  A low prevalence is a finding, not a failure.
- **M2 — depth: localization + dose (3–4 days, $0).** Pre-registered 12-concept
  stratified subset: sliding layer-window sweep incl. outside-band probes;
  partial-ablation dose curve, λ ∈ {0, .25, .5, .75, 1}. **Gate: late-window
  effect CI-cleanly exceeds early and middle, pooled.** Dose shape descriptive.
- **M3 — specificity matrix (3–4 days, $0).** ~12×12 prime-A × probe-B naming
  matrix at the switch's home band, 1.5B + 3B. **Gate: diagonal suppression
  CI-cleanly exceeds off-diagonal collateral at both scales.** Within- vs
  cross-category collateral structure reported. The killer figure.
- **S1 stretch — scale (optional, ≤ $15).** Fit the 7B lens on a rented GPU
  (dim-stage fitter + remote-fit pattern); M1-lite + matrix-lite at 7B →
  specificity-vs-scale curve 0.5B→7B.
- **S2 stretch — lexical vs semantic scope (optional, $0).** Ablate v_"France":
  can the model still say "French," "Paris," synonyms/translations (frozen
  alt-form single-token lists)? Token mute button vs concept mute button.

## Methodology guardrails (inherited from dim-stage, load-bearing)

- **Deterministic oracles only** — greedy first-token primary (S4's "The …"
  miss-counting caveat kept for anchor comparability; first-3-greedy recorded
  as secondary texture), concept softmax mass as texture. Never an LLM judge,
  never text parsing.
- **Wilson CIs on cells + Newcombe on differences decide every gate.** N ≥ 20
  per cell or pre-declared UNDERPOWERED. A cell whose CI overlaps its neighbor
  is not a result.
- **Pre-commit gates as code and dry-run them** (wrong-arm input exits INVALID;
  `--limit` is smoke, never a result). A pre-committed null is reportable.
- **Design-extraction before design-signing**; **deviations are owned** (table
  from day one: naming-only gate, constructed items, model scale, lens
  provenance).

## Pre-declared risks

1. **Breadth kill-risk:** the switch may be idiosyncratic to S4-style items —
   the battery is designed so any prevalence number is the reportable result.
2. **0.5B nonspecificity** (known from S4b): 0.5B cells always reported under
   that frame, never as switch evidence.
3. **7B fit fails or overruns** → S1 stretch dropped; the core chain never
   depends on it.

## Timeline & budget

2–3 weeks. Core M0–M3: $0 (local, forward-only). With S1 stretch: ≤ $15.

## Decisions on record at kickoff

- K1 — slug **mute-map**, GitHub **public** (Kyle, 2026-07-27).
- K2 — naming-only competence gate is the standing design change vs S4b; owned
  in the deviations table; anchor comparability via M0's exact re-run.
- K3 — lens artifacts are **never refit for the core chain**: sourced from
  dim-stage's local `lenses/` with SHA256 provenance recorded at M0.
- K4 — stats ruler ported verbatim from dim-stage (`stats.py` + tests), the
  lossy-wall Wilson/Newcombe pattern.

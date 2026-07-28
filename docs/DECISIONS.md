# DECISIONS.md — append-only decision log

Kickoff decisions K1–K4 (2026-07-27) are recorded in `KICKOFF.md`; this log
starts with M0 and only ever appends.

## D1 — Lens artifact sourcing: copy + SHA256 (Kyle, 2026-07-27)

The three fitted lens `.pt` files are **copied** from local dim-stage
(commit `e6c10b9`) into `lenses/` (gitignored), with SHA256 fingerprints, source,
and regeneration commands recorded in the tracked `lenses/PROVENANCE.md`.
Rejected: symlinking (breaks if dim-stage moves; blurs provenance) and a
configurable loader path (flexibility K3 already forecloses). The frozen S4b
item set and the three recorded S4b result JSONs are copied under the same
provenance discipline (`items/`, `anchors/`).

**Consequence discovered at freeze time:** dim-stage's lock and a fresh resolve
disagreed on transformers (5.13.1 vs 5.14.1), so mute-map **pins
`torch==2.13.0` + `transformers==5.13.1`** (dim-stage's lock at anchor time) in
`pyproject.toml`. Relaxing the pins is a future DECISIONS entry and re-runs the
anchor gate.

## D2 — Port scope: M0-only, verbatim (Kyle, 2026-07-27)

Ported: `SubjectModel` + `_record_residuals` (→ `subject.py`), the ablation
subset `jlens_vector`/`ablate`/`edit_residuals`/`Edit` (→ `intervention.py`),
and the shared conventions `fail_invalid`/`FROZEN_BANDS`/`proportional_band`/
`token_forms`/`encode_chat`/`output_logits`/`READBACK_TOL`/`MIN_N`/
`COLLAPSE_SHARE`/`degeneracy`/`rate_cell` (→ `harness.py`) — each verbatim from
its dim-stage home, source cited in the module docstrings. The S4b runner is
ported near-verbatim as `m0_anchor.py` (divergences owned in its docstring:
import paths, `items/` and `results/anchor-*` paths, three unused imports
dropped). Steering/swap operators stay behind until a milestone brief needs
them. Rejected: porting the full toolkit now (M0 would certify code no M0 cell
exercises).

## D3 — Anchor gate: full bit-for-bit (Kyle, 2026-07-27)

`m0_port_gate.py`, frozen before any comparison ran: PASS iff every per-item ×
instruction × condition **greedy outcome** (`produced` + decoded `greedy`
token), every per-item `gate_greedy` membership, and the instrument
configuration (band, thirds, item roster, dropped list) match dim-stage's
recorded S4b JSONs with **0 mismatches**, on all three subjects. Any mismatch ⇒
INVALID (exit 2) — investigate; the bar never softens. `concept_mass`
float equality and `gate_verbatim_p` agreement are reported as texture, never
gating. Rejected: gate-level match only (per-item flips could cancel silently).

## D4 — The M1 roster: 10 categories x 6 concepts (Kyle, 2026-07-27)

Option (b): a **uniform 10 x 6 = 60-concept roster** — the nine S4 categories
plus days of the week, each filled to exactly 6. 53 concepts come from
vocabularies this lineage has measured (S2 flexible-generalization args, M3
directed-modulation topic_categories); **7 new-list words** (Japan, Brazil,
tiger, bear, flute, opal, amber) fill the gaps where a shipped list ran dry or
failed the single-token filter — an owned deviation, declared in the frozen
file's `new_list_words` and in M1-BRIEF's deviations table. Every one of the 60
words was re-verified single-token on all three Qwen2.5 tokenizers at freeze
time (0 dropped by the prefilter, confirmed by each subject's dry-run).
**What "single-token" means here, precisely** (review F8): the prefilter's test
is `harness.token_forms(w, tok)` non-empty — i.e. **the bare form *or* the
leading-space form** is one token. All 60 pass *that* bar, which is why 0 items
were dropped. It is a weaker property than the one the greedy-first-token oracle
actually needs (a single-token **bare** form), which only 34 of the 60 have —
the gap M1's results section then had to report. The two senses are distinguished
everywhere they appear from this decision onward.

Uniform category size is what makes the per-category map legible; the
naming-only competence gate, not list authorship, does the honest filtering.
Each concept lives in exactly one category (spider stays in animals per S4
precedent; "fly" excluded as verb-ambiguous). Rejected: (a) measured-only, whose
category sizes vary 4–11 and muddy the per-category comparison M1 exists to
deliver; (c) 8 x 8, which needs ~2x the invented vocabulary for a marginally
deeper map.

## D5 — 3 clues per concept, reusing S4's 60 items verbatim (Kyle, 2026-07-27)

Option (a): **180 items — 60 of S4's own items carried over byte-for-byte
(name, category, noun, concept, control, clue unchanged) plus 120 newly
authored by the D27c rules.** Three clues per concept because trials are free
and the pooled gate's power scales with item count. Reuse buys more than saved
authoring: since M1 uses the same naming template, operator, band thirds, and
greedy grading as the certified `m0_anchor.py`, those 60 items must reproduce
the recorded anchor's naming cells **bit-for-bit**, so one third of the battery
doubles as a standing re-certification of the instrument on every run. That
cross-check is frozen into `m1_battery.py` as a wrong-arm gate: reused items are
graded FIRST and any mismatch is INVALID before a single new-concept cell is
read. Scoped at review (PR #3 F7): bit-for-bit reproduction is a property of the
certified environment (device `mps` under torch 2.13.0 / transformers 5.13.1),
so off that stack the cross-check still runs and is recorded but is not
gate-bearing — and the whole run is pre-declared NOT A RESULT. Rejected: (b)
all-new items (throws away the cross-check); (c) 2 clues per concept (less power
everywhere).

**Construction rules, extended and enforced as code.** The frozen file carries
its own `construction_rules`, `roster`, and `forbidden_forms` blocks, and
`m1_battery.load_items` re-checks every bar at run time: 180 items / 60
concepts / 10 categories of 6, 3 clues per concept, one fixed same-category
control per concept (concept != control), exactly 60 reused items, and no clue
leaking its concept or control. The leak test **diverges from S4's substring
test**: with 60 short concepts a substring test makes "plant" a leak for "ant"
and "chamber" one for "amber". M1 uses a word-prefix test at a word boundary
(catching "lions", "golden", "Egyptian") plus a frozen `forbidden_forms` list
for the root-changing derivatives a prefix test cannot see (France/french,
Mars/martian, iron/ferrous). A different word naming a product or synonym is
NOT a derivative — S4 precedent, whose frozen cow-3 clue reads "Beef and leather
both come from this farm animal." All 60 reused items pass the stricter guard
unchanged.

## D6 — Competence gate: item-level greedy, naming only (Kyle, 2026-07-27)

Option (a): an item enters the gated set **iff its clean naming greedy first
token is one of the concept's single-token forms** — S4's D29 greedy gate minus
the avoidance half (K2, the standing naming-only deviation). Gating is
per-subject; each subject earns its own gated set. The paper-style verbatim-P
rate (clean concept mass >= .85) is reported alongside as texture, never gating,
and S4's "The …" miss-counting caveat is kept, owned, for anchor comparability.
Rejected: (b) a concept-level gate (>= 2 of 3 clean), which is coarser,
conflates item quality with concept competence, and has no anchor precedent.

## D7 — Pooled contrast gate + descriptive package (Kyle, 2026-07-27)

Option (a), with the prevalence wording amended twice pre-run at PR #3's reviews
F1 and F9 (both Kyle-approved before any M1 cell existed). Per subject, on the
pooled gated cell: **BREADTH-SPECIFIC iff naming success under `control_late`
minus under `primed_late` is positive and its Newcombe 95% CI excludes 0.** The
M1 verdict is the AND over 1.5B and 3B; 0.5B runs and is reported under its
standing any-direction-damage frame (pre-declared risk 2) and never enters the
AND. Pooled n < MIN_N = 20 ⇒ pre-declared UNDERPOWERED. Per-concept and
per-category cells are always descriptive (paired rates with Wilson CIs), never
verdict-bearing — rejected (b), a binary per-concept "switched" label, because a
cell of n = 3 has a CI from floor to ceiling and a label on it invites exactly
the over-reading the "a cell whose CI overlaps its neighbour is not a result"
rule exists to stop.

**Prevalence, fixed denominator.** Only concepts with **all 3 items gated**
count; of those, the number showing the **hard-switch profile** (`primed_late`
naming 0/3 AND `control_late` 3/3) is reported with its Wilson CI over that
fixed set, carrying the pre-declared **UNDERPOWERED** tag whenever the set holds
fewer than MIN_N = 20 concepts — the *expected* case (the anchor data projects
~15–18 all-3-gated concepts of 60), stated pre-run so it reads as pre-declared,
not discovered. The fixed set is per-subject; no cross-subject prevalence
comparison is gated or claimed, and the intersection is reported beside as
texture by `m1_verdict.py`. Concepts with 1 or 2 gated items are reported
stratified by gated-item count, never pooled into the headline. **Trap recorded
(PR #3 review observation):** this denominator is *anti-monotone* in items per
concept — writing more clues would shrink it, so its power can only be raised by
widening the roster, never by adding clues.

**Degeneracy disposition, pre-committed at PR #3 review F5** (before any M1
run). The degeneracy guard is read on the **gated** cell, which is the cell the
verdict is computed on. Collapse (attractor share >= COLLAPSE_SHARE = 0.5) in
`clean` or `control_late` — the two comparison arms the verdict rests on — is
pre-declared **DEGENERATE**: the contrast is still reported, but no
BREADTH-SPECIFIC claim is made. Collapse in `primed_late` is a **TAG only** and
the verdict stands: a shared attractor under the concept's own ablation is the
expected signature of the switch (the answer is destroyed and what remains is
the model's fallback), not evidence against specificity. Checked against the
data that already existed before freezing: on the recorded anchors this
disposition fires on neither gate-bearing subject (gated attractor shares at
1.5B: clean .136 / primed_late .364 / control_late .136; at 3B: .375 / .375 /
.375), so the rule changes no anchor verdict. Verdict precedence, frozen in
`breadth_verdict()`: NOT A RESULT > DEGENERATE > UNDERPOWERED > the contrast.

**Stats honesty row, owned and pre-committed.** (1) Items within a concept share
one lens direction, so item-level pooling overstates independence; S4b pooled
the same way, and the per-concept map is the honest granular view beside it.
(2) `primed_late` and `control_late` are measured on the **same** gated items,
but `newcombe_diff` is Newcombe's method 10 for two **independent** samples —
for positively correlated paired arms that *widens* the interval, so it cannot
manufacture a false BREADTH-SPECIFIC verdict; it can only cost power (PR #3
review F6). (3) MIN_N = 20 is applied to raw n, not to an effective n discounted
for that clustering.

## D8 — Widen the anchor comparator's frozen bar (Kyle, 2026-07-27)

Option (a): `m0_port_gate.py`'s configuration comparison, frozen narrow at D3,
now also compares the recorded **`protocol`** block (readback_tol, min_n,
collapse_share, gate wording) and **`lens_n_prompts`** — the fields that would
catch a silently softened instrument (PR #2 review F4). `lens` itself stays out:
it is a path and may legitimately differ between repos. Safe by construction —
the committed artifacts already match on both, verified by re-running
`m0_port_gate.py --all` after the widening: still 0 mismatches over 840 cells x
3 subjects, so the widening cannot flip M0's PASS, only catch future drift.
Rejected: (b) keeping D3's narrow list and leaving the gap open.

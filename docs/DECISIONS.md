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

## D9 — The oracle: widen to the greedy-span prefix rule (Kyle, 2026-07-28)

Option (b): **the concept is produced iff the decoded first-3-greedy span, after
stripping leading whitespace, opens with the concept's spelling at a word
boundary, case-insensitive.** Frozen as code in `oracle.py` before any M2 run,
with the rule's full text in `oracle.ORACLE_WORDING` and written verbatim into
every M2 results JSON.

**Why the milestone opened here rather than with layers.** M1's primary readout
scored exactly one token, so a concept could only be measured when its spelling
fitted through that one-token keyhole — and **26 of the 60 roster words are
multi-token in bare (no-leading-space) form**. Planets and musical instruments
gated **0 items on all three subjects** for that reason alone, while the recorded
first-3-greedy texture showed the models often did say those words. M1's gate was
untouched by this (the bias runs against the claim, never for it), but M2 is the
*mapping* milestone, so the map's coverage was set by tokenizer geometry rather
than by the models. A change to the oracle is a change to the measurement: it
belongs in a decision frozen before any run, never in a results section.

**What the rule does and does not admit.** Prefix, never containment — "not
France" is a miss, because on a control arm containment would *inflate* the
contrast, the one bias direction this project never accepts (the rejected option
(c), span containment, which is exactly M1's recorded `says_concept_in_3`
texture and stays recorded as texture). Word boundary — "Marseille" is not Mars;
the test is "the next character is not a letter or digit". Case-insensitive
because orthography is not semantics ("Piano" is the word piano), and the
widening is *measured* to do real work: the 1.5B prefix gate reads 72
case-exact versus 105 case-insensitive. S4's "The …" miss-counting caveat is
**unchanged in kind and still owned**: "The France" remains a miss.

**Amended pre-run at PR #5's review (F5), and it is load-bearing:** the **end of
the span counts as a word boundary**, so a word that exactly fills the recorded
3-token span ("Butterfly") is a hit — truncation must never turn a completed
word into a miss. Exactly six recorded M1 cells distinguish the two readings,
two of them on a control arm, and this is the reading every pre-registered n in
`docs/M2-BRIEF.md` was computed under. It is pinned as a named unit-test case
(`oracle.SPAN_FILL_TEST_CASE`).

**The owned residual (F12, restated at F14).** Because the span is truncated,
for the three concepts whose bare form *fills* it (beetle, butterfly, trumpet)
the closing boundary is unobservable: "Beetlejuice" tokenizes as
`['Be','et','le','ju','ice']` and so truncates to exactly `'Beetle'`. F14
corrected the brief's original claim that "zero such cells occur in the recorded
data" — six cells do fill the span; each is a completed word on inspection and
each is the item's own intended answer, but a truncated recording cannot rule
out a longer continuation. The residual is therefore **owned rather than
excluded**; none of the three concepts is in M2's subset, and the accepted
behaviour is pinned by its own unit-test case.

Still a deterministic oracle: greedy decoding is deterministic and this is a
fixed string comparison on that deterministic span, unit-tested — never
free-text parsing, never an LLM judge (CLAUDE.md's standing guardrail). The
**first-token outcome is computed and recorded beside every cell**, so every
cross-check against M0/M1 artifacts compares raw recorded fields and is
oracle-independent — D9 cannot soften a gate. Rejected: (a) keep the first-token
oracle, which leaves planets and instruments dark forever and makes the
per-category map partly a map of tokenizer geometry; (c) span containment, above.

## D10 — Publish an M1 reanalysis under the widened oracle (Kyle, 2026-07-28)

Option (a): **an offline re-score computed from the committed M1 artifacts**
(`m1_rescore.py`), emitting `results/m1-rescore-*.json` plus a
REANALYSIS-labelled addendum in M1-BRIEF's results — *beside* M1's pre-committed
table, never replacing it. M1's published numbers and its BREADTH-SPECIFIC
verdict stand as the verdict of record; the reanalysis restates nothing.

Sound rather than merely cheap: the widened oracle reads the 3-token span M1
already recorded for every cell, and 3 tokens ≥ the longest bare form on the
roster (measured on all three Qwen2.5 tokenizers, which agree exactly). For a
*prefix* rule, truncation cannot hide a hit, since a hit must start at the
span's first character — so the recorded span is provably sufficient. The
script is a pure function of the recorded JSONs: no model run, no new trial.

**Its own self-check:** because the first-token outcome is recorded per cell,
the script recomputes M1's *published* contrast from the same file and refuses
to write anything unless it reproduces it exactly. A reanalysis that cannot
reproduce the analysis it sits beside is not evidence of anything. Rejected: (b)
a full re-run, which buys nothing the recorded span does not already carry while
creating a second generation of M1 artifacts to keep straight; (c) no
reanalysis, which would leave the widened numbers as unpublished design math.

PR #4's review F5 lands in the same artifact: the per-source split (S4's 60
reused items vs M1's 120 newly authored ones) is now **our own recorded number
under both oracles** (PR #5 review F4) rather than a figure quoted in a PR
comment. The new-items-only contrast is CI-clean on all three subjects under
both readings.

## D11 — The pre-registered 12-concept subset (Kyle, 2026-07-28)

Option (a): **one shared subset, fixed by a frozen stratified rule applied to
the recorded M1 artifacts** — so the list was determined the moment the rule
was, with no discretion exercised at run time. Items are each concept's **3
frozen M1 clues, verbatim**; no new authoring. That is what makes M2's standing
re-certification possible (D14): the subset's `clean` / `primed_late` /
`control_late` cells already exist in M1's recorded artifacts.

- **S1 — hard-switch core (5):** the gate-bearing subjects' shared hard-switch
  set, verbatim — Brazil, Canada, China, France, Japan.
- **S2 — readout-unlocked (4):** from the two categories that primary-gated 0
  items everywhere, top 2 per category by summed prefix-gated items across the
  gate-bearing subjects, tie-break alphabetical — Jupiter, Mars, violin, piano.
- **S3 — leaky switch (2):** primary-gated on both gate-bearing subjects with
  any primed-arm leak — Egypt, October.
- **S4 — non-specific anti-example (1):** ≥ 3 primary-gated items at 1.5B with
  `control_late` 0/3, dropping any pool member whose control arm survives on the
  other gate-bearing subject — silver (Friday is the named alternate).

Resulting 12: **Brazil, Canada, China, Egypt, France, Japan, Jupiter, Mars,
October, piano, silver, violin.** *Trade-off, owned:* countries-heavy (6/12)
because the measured shared hard-switch stratum *is* all countries — the map
goes where the effect was measured, and S2–S4 spread the coverage deliberately.
Rejected: (b) per-subject subsets, which maximize per-subject n but destroy
cross-subject comparability of every curve; (c) a hard-switch-only 12, a deep
map of one country-shaped island with no unlocked categories, no anti-example
and no leak stratum.

**The convention S2 owns (PR #5 review F3).** For those four concepts the
ablated direction is keyed to the **leading-space token's unembed row**
(`' Jupiter'`) — the only single-token form that exists — while D9(b) scores the
bare spelling the model actually emits. This is measured, not assumed: in M1's
recorded data the space-keyed late ablation *does* mute the bare emission
(primed 0 on all four concepts at both gate-bearing subjects), pinned as a test.
The same predicate ("is the bare form single-token?") also scopes the
concept-mass channel — see D13.

## D12 — The window scheme: tiers + a late-anchored sliding sweep (Kyle, 2026-07-28)

Option (b), in two cleanly separated parts. **Gate cells (pre-committed):** the
three frozen thirds, primed AND control at each — the S4b-comparable frame, now
powered. **Descriptive map:** a window of the subject's own late-third width
(5 / 6 / 7 layers) slid at **stride 2** across the full lens range L0..n−2,
primed arm only. Window semantics are otherwise identical to M1's — same k = 1
projection removal, same runtime read-back — with only the layer set swapped.

The stride grid is **anchored on the late-third start** (PR #5 review F8), so
the gate cell is a point on every subject's map — and that window *is* the
`primed_late` tier cell, reused rather than re-run. The **maximum-start**
(lens ceiling) and **minimum-start** (L0) windows are added when the grid does
not already include them (reviews F8 + F11): the ceiling case bites at 0.5B and
the floor case at 0.5B and 1.5B, whose odd-anchored grids would otherwise never
ablate L0. Positions per subject: **11 / 12 / 15**, of which the late-start
window is reused → **10 / 11 / 14** newly-run window conditions.

Windows starting below the band are the outside-band probes KICKOFF's scope
names (9–14 layers of room); above-band coverage is **structurally thin** (1–2
layers) because the band's 0.92 ceiling nearly touches the lens ceiling — owned
in the brief's extraction table, not discovered later. Stride 2 localizes any
transition edge to ±2 layers. Rejected: (a) tier cells only, which under-delivers
KICKOFF's frozen scope; (c) a single-layer sweep, which ablates 1 layer where
the tier cells ablate 4–7 and so under-doses the intervention — a flat curve
would be unreadable (no switch, or too small a dose?). If the width-w map shows
a sharp edge, a single-layer zoom near it is a natural M2-results follow-up,
decided then and descriptive only.

## D13 — The dose design: partial ablation, primed arm, late third (Kyle, 2026-07-28)

Option (a). Grid frozen by KICKOFF: **λ ∈ {0, .25, .5, .75, 1}**. Operator:
**h′ = h − λ·(v̂ᵀh)v̂** per position at each late-third layer. λ = 0 *is* `clean`
and λ = 1 *is* `primed_late` — both already-run deterministic cells, reused not
re-measured — so only λ ∈ {.25, .5, .75} are new conditions. Dose shape is
descriptive, as frozen; no gate reads it.

The partial operator is **new code** and lives in the M2 runner
(`intervention.py` stays verbatim-ported), unit-covered from birth per PR #4's
F6 pattern. Two properties are pinned by tests rather than asserted: it is
**bit-identical to the ported full-ablation operator at λ = 1** (it computes in
float64 on CPU, the convention `ablate` already uses), so the dose curve's
endpoint is the same measurement M1 made; and the **runtime read-back
generalizes with it** — the surviving projection must equal (1−λ) times the
original within `READBACK_TOL`, which at λ = 1 is exactly M1's check.

**Mass-channel scoping (PR #5 review F2).** The readout per λ is the binary
naming rate under D9(b) for all gated items, plus mean concept mass — the graded
signal that can reveal a dimmer where the binary steps — computed **only over
concepts whose emitted bare spelling has a single-token form**. The S2 stratum
has none, so its mass is floor-pinned by construction (measured on the recorded
clean arm at 1.5B: S2 mean 0.009 vs 0.913 for the rest), and its dose curve is
read on the binary rate alone. Owned in the deviations table. Rejected: (b)
primed + control at every λ, doubling cost for a collateral curve both S4b and
M1 predict is flat; (c) a dose × window cross, which explodes the run and
answers nothing KICKOFF asked.

## D14 — The pre-committed wording package for M2 (Kyle, 2026-07-28)

Frozen as code in `m2_depth.GATE_WORDING` before any M2 run and written verbatim
into every results JSON, so prose and code cannot drift.

**Gate wording.** Per subject, on the pooled gated cell — gating is the clean arm
under D9(b), decided once per item and window-independent, so every tier, window
and dose cell shares one gated set: **LATE-LOCALIZED iff naming under
`primed_early` minus naming under `primed_late` is positive with its Newcombe
95% CI excluding 0, AND naming under `primed_middle` minus `primed_late`
likewise.** The M2 verdict is the AND over 1.5B and 3B (`m2_verdict.py`); 0.5B
runs and is reported under its standing any-direction-damage frame, never
gate-bearing. Pooled gated n < MIN_N = 20 ⇒ pre-declared UNDERPOWERED.

This *is* KICKOFF's "late-window effect CI-cleanly exceeds early and middle"
expressed in directly comparable proportions: the effect at tier T is the naming
drop clean − primed_T on the same items, so effect_late − effect_T = primed_T −
primed_late — the shared clean arm cancels, leaving a plain two-proportion
comparison the ported ruler already decides. Rejected: a CI on the
difference-of-differences itself, which needs stats machinery beyond the frozen
Wilson/Newcombe ruler — a new method mid-lineage for no added honesty. Control
tiers are reported beside as specificity texture; M1's breadth gate is not
relitigated.

**Degeneracy disposition, re-frozen — two changes, both recorded before any run.**
(1) *The PR #4 F3 correction:* `clean` is the **gate arm**, not a comparison arm.
On the gated cell its answers are by construction correct openings of 12
different spellings, so no single token can approach COLLAPSE_SHARE = 0.5 on a
powered cell — measured worst case on the subset's recorded clean cells is
**3/28 ≈ 0.107**, five times below the threshold (full-roster worst case
3/69 ≈ 0.043; reviews F7 + F10 asked for this to be evidenced on the population
M2 actually grades, and it now is, as a test). M1's wording listing `clean` among
the monitored arms was inert — it could never fire on a powered cell and fired
nowhere — and it **stays byte-frozen** with M1's artifacts in
`m1_battery.GATE_WORDING`, un-edited (editing it would force a full M1 re-run);
M2's own wording drops `clean` from the dispositive list and records why.
(2) *The wide-oracle adaptation:* under D9(b) a high-scoring arm's first tokens
legitimately concentrate on fragments that open *correct* answers, so raw
first-token collapse stops meaning pathology. The dispositive guard therefore
pools the first tokens of the arm's **non-produced items only**, with the share
still computed against the full gated n — "at least half of this arm's answers
are the same *wrong* opening". The raw all-answers guard stays recorded beside as
texture (M1 comparability). **Disposition, scoped to the arms the gate actually
reads (review F9):** collapse in a surviving-side gate arm (`primed_early`,
`primed_middle`) ⇒ **DEGENERATE**, no LATE-LOCALIZED claim; collapse in
`primed_late` ⇒ **TAG only** (the expected mute signature); collapse in a
**control tier** — arms the gate does not read — is a **specificity-texture
caveat**, recorded and attached to the control-tier readouts it compromises,
never dispositive over the localization verdict. Window and dose cells are
descriptive, so their guards are always texture.

**The standing re-certification, one generation deeper.** The subset's `clean` /
`primed_late` / `control_late` cells must reproduce `results/m1-battery-*.json`
cell-for-cell on the raw recorded fields (`greedy` and `greedy_3` decoded
strings; `concept_mass` equality as texture) **before any new window or dose cell
is read** — graded first, M1's `order_reused_first` pattern carried over as an
explicit two-phase grade. The comparison is on raw strings, so it is
oracle-independent. On the certified stack (device `mps`, torch 2.13.0,
transformers 5.13.1) any mismatch is INVALID (exit 2); off it the check is
recorded but the whole run is pre-declared NOT A RESULT and `m2_verdict.py`
refuses it. Coverage is a property of the run rather than of the environment, so
the bar that all 36 subset items were actually compared is unscoped (M1 review
F1's lesson). M2 additionally refuses an M1 artifact that was itself not a
result: a smoke or uncertified run cannot certify anything.

**Verdict precedence, frozen** in `localization_verdict()`: NOT A RESULT >
DEGENERATE > UNDERPOWERED > the contrast. Wrong-arm inputs exit INVALID before
any trial; `--dry-run` validates and stops; `--limit` is smoke, never a result.

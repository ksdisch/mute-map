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

## D15 — The matrix roster: reuse M2's pre-registered 12 verbatim (Kyle, 2026-07-28)

Option (a). Brazil, Canada, China, Egypt, France, Japan, Jupiter, Mars, October,
piano, silver, violin — with their 36 frozen M1 items, gated sets and per-item
`direction_key` exactly as recorded. **Zero new discretion:** the subset was
fixed by D11's stratified rule before any M2 cell existed, so M3's selection
surface was pre-registered two milestones ago — the strongest position a
specificity claim can argue from. The characterization also stays on one cast of
concepts (breadth → depth → dose → collateral), and the strata keep doing their
jobs against 11 probes instead of 1: the six countries give a dense
within-category block, **silver** — the named non-specific anti-example — sits
inside the pooled off-diagonal where its collateral *lowers* off-diagonal naming
and so biases against the gate, Egypt and October carry the replicated leak
texture, and the S2 stratum tests whether space-keyed directions splash
differently. It also maximizes D16's re-certification surface: 90 of the
matrix's cells per subject are already recorded in M1's artifacts.

*Trade-off, owned:* the category structure is lopsided (6 countries / 2 planets /
2 instruments / 1 month / 1 metal), so the within- vs cross-category readout is
mostly a countries story — 30 of the 34 within-category ordered pairs are
country pairs, and October and silver have no same-category sibling in the
matrix at all (their recorded M1 control cells, run as re-certification texture
under D16, are their only same-category collateral sample). Rejected: (b) a
re-derived category-balanced 12, which discards M2's per-concept depth and dose
evidence for the swapped-in concepts, shrinks the embedded re-certification,
re-opens selection discretion one milestone before the headline figure, and
de-samples the one stratum where the hard switch is *measured* to live; (c)
reusing the 12 but swapping out the awkward strata (silver's non-specific row,
October's siblingless cell) — a cleaner figure on a dishonest sample, since it
deletes exactly the concepts pre-registered to keep the aggregate honest.

The roster is copied into `m3_matrix.SUBSET` rather than imported from
`m2_depth`, per the standing cut-from-your-predecessor rule, and pinned equal to
M2's by a test so the copy cannot drift.

## D16 — Matrix cells + the embedded re-certification (Kyle, 2026-07-28)

Option (a): **a full re-run of the 12 × 12 grid with the recorded cells graded
first.** Per subject: `clean` (36 items) plus every (direction A × item of B)
cell — 12 × 36 = 432 ablated cells — at the late third, λ = 1, k = 1,
naming instruction only, D9(b) oracle, first-token outcome recorded beside every
cell. Additionally the six out-of-subset control directions (February, Saturn,
Mercury, guitar, drum, platinum) run **on their paired concepts' 3 items only**
(+18 cells): they are not matrix cells, but they complete the recorded
`control_late` surface — their primary job — and they give **October and
silver**, the two subset concepts with no same-category sibling in the matrix,
their only same-category collateral sample. **486 cells per subject**, 0.9× an
M1 subject run.

**The standing re-certification, a generation deeper.** The 108 cells this run
shares with M1's recorded artifacts — `clean` (36), the diagonal (= 36
`primed_late` cells) and the control cells (18 inside the matrix + the 18
extras) — must reproduce `results/m1-battery-*.json` on the raw recorded fields
(`greedy`, `greedy_3` decoded strings; `concept_mass` as texture) **before any
off-diagonal cell is read**, enforced as an explicit two-phase grade
(`conditions_for` splits each item's M1-shared cells from the rest). The
comparison is on raw strings, so it is oracle-independent. On the certified
stack any mismatch is INVALID (exit 2); off it the check is recorded but the run
is pre-declared NOT A RESULT and `m3_verdict.py` refuses it. M3 also refuses an
M1 artifact that was itself not a result.

Rejected: (b) reusing the recorded cells instead of re-running them, which saves
~25% of the run and destroys the one check that has caught nothing yet *because*
it runs every time; (c) matrix × tiers or matrix × λ, which explodes the run
3–5× and answers questions M2 already answered — KICKOFF fixes M3 at the home
band.

## D17 — The pre-committed wording package for M3 (Kyle, 2026-07-28)

Frozen as code in `m3_matrix.GATE_WORDING` before any M3 run and written verbatim
into every results JSON, so prose and code cannot drift.

**Gate wording.** Per subject, on the pooled gated cell — gating is the clean arm
under D9(b), decided once per item and **direction-independent**, so every matrix
cell shares one gated set: **MATRIX-SPECIFIC iff BOTH (1)** naming under the
pooled **off-diagonal** cells (every gated item under each of the 11 directions
that are not its own concept's) minus naming under the pooled **diagonal** cells
is positive with its Newcombe 95% CI excluding 0; **AND (2)** the same contrast
restricted to the **within-category** off-diagonal cells is likewise positive
with its Newcombe 95% CI excluding 0. Both arms of clause (2) — its off-diagonal
pool AND its diagonal — are restricted to gated items whose concept has at least
one within-category subset sibling, so October's and silver's items drop from
that clause **by construction, not by choice**. Clause (2) compares
within-category off-diagonal *cells* (n = 96 / 100 / 101) against the *diagonal
cells of the same restricted item set* (n = 24 / 28 / 29); MIN_N guards that
diagonal n as well as the pooled one. The M3 verdict is the AND over 1.5B and 3B
(`m3_verdict.py`); 0.5B runs under its standing any-direction-damage frame,
never gate-bearing.

Clause (1) *is* KICKOFF's "diagonal suppression CI-cleanly exceeds off-diagonal
collateral" in directly comparable proportions, by M2's algebra: the shared
`clean` arm cancels, leaving the plain two-proportion comparison the ported
ruler already decides.

**Why clause (2) exists (brief review F2).** The pooled off-diagonal arm is 73%
cross-category (274 of 374 cells at 1.5B), while the arm KICKOFF's wording
generalizes — S4b D28's specificity control — was same-category only.
Cross-category pairs are the ones least likely to show collateral, so pooling
shifts the comparator in the gate's favour relative to the control the lineage
actually ran. Clause (2) is the undiluted test, powered on its own.

**The collateral-floor qualifier (brief review F1, re-defined at F11 and F15).**
The ordering contrasts cannot by themselves distinguish a per-concept switch from
graded damage that is merely worse on-diagonal, so the verdict carries the
pre-declared qualifier **ON A DAMAGED FLOOR** if the floor readout's Wilson 95%
lower bound is below **0.5**. The floor readout is the **cluster-collapsed
per-cell survival**: each gated item contributes its *fraction* of the 11
off-diagonal deletions survived, and the readout is `wilson(k, n)` with
k = ⌊the sum of those fractions⌋ and n = the gated items. This keeps the quantity
the floor is about — the per-cell collateral rate — while refusing both dishonest
denominators: the pooled rate at n = 308 under-fires (its 11×-inflated n narrows
the interval, F11), and a survives-all-11 conjunction is decided by the unmeasured
correlation structure across the 11 deletions rather than by damage (F15). A
binomial interval on a mean of bounded fractions is approximate by construction —
owned, and acceptable only because the qualifier is never dispositive. The
pooled per-cell reading is reported beside as the permissive comparison. **The
qualifier scopes a claim and can never create or rescue one**, so it attaches to
a contrast-level verdict (MATRIX-SPECIFIC or not shown) and has nothing to scope
when precedence already withheld the claim; the floor readout itself is recorded
on every run regardless. The 0.5 constant is pre-registered and deliberately
**not** fitted to any recorded cell; 0.5B's exclusion from gate-bearing rests on
the standing pre-declared scale frame, never on this qualifier.

**PR #7 F2's tier-width caveat, retired structurally and stated affirmatively.**
M2's gate compared tiers of unequal layer count (the late third takes the band
remainder — 4 vs 6 layers at 1.5B), so depth *and* intervention size differed
between compared arms. M3 has no tier contrast: every matrix cell ablates the
*identical* late-third layer set at λ = 1, k = 1, so the two arms the gate
compares differ **only in which direction is removed**. D17's wording carries a
clause saying exactly that, so the caveat's lesson is owned rather than silently
mooted — and if a later stage re-introduces tiers, the caveat clause must come
back with them.

**Degeneracy disposition**, carrying M2's D14 wide-oracle guard verbatim and
re-scoping it to M3's arms: the dispositive guard pools the first tokens of an
arm's **non-produced** cells only, share against the arm's full cell count.
Collapse in the pooled **off-diagonal** — the surviving side the gate reads — ⇒
**DEGENERATE**; collapse in the pooled **diagonal** ⇒ **TAG only** (the expected
mute signature); `clean` stays off the dispositive list (the D14 F3 correction,
carried); collapse inside any single direction's row or any per-pair cell is
**texture** (at n ≤ 3 a per-pair share is not evidence of anything).

**Descriptive package, never gate-bearing:** the full grid (per-pair cells are
n ≤ 3), the within- vs cross-category split, per-direction row profiles and
per-concept column profiles, asymmetry texture (A→B vs B→A), the 18
out-of-subset control cells, and mean concept mass per cell under D13's standing
scope.

**The effective-n sanity check**, pre-registered and never dispositive: each
contrast recomputed with the repeated arm collapsed to one binary per gated item
— "survives all 11 off-diagonal deletions" for clause (1), "survives all
within-category sibling deletions" for clause (2). The pooled off-diagonal
repeats each gated item 11 times, which makes the gate's Newcombe interval
**narrower** than the clustering justifies, not wider — anti-conservative and
owned. If a pooled clause is CI-clean but its per-item collapse is not, the
per-item numbers are the honest ones to quote.

**Verdict precedence, frozen** in `matrix_verdict()`: NOT A RESULT > DEGENERATE >
UNDERPOWERED > the contrast. Wrong-arm inputs exit INVALID before any trial —
and, per D18's companion disposition, before the checkpoint is even loaded;
`--dry-run` validates and stops; `--limit` is smoke, never a result.

## D18 — Run-time instrument bars for M3 (Kyle, 2026-07-28)

Option (a): **both bars in the runner's `main()` path, pre-trial, plus unit
tests.** After the tokenizer loads and before any trial:

1. **The span bar.** Every planned direction word must tokenize to
   ≤ `oracle.SPAN_TOKENS` = 3 in **both** its bare and its leading-space form —
   `max(len(tok(w)), len(tok(" " + w))) ≤ SPAN_TOKENS` — else exit INVALID. This
   is D9(b)/D10's whole soundness premise (a prefix hit cannot be hidden by span
   truncation *because* every roster word fits the span), which PR #7 F5 flagged
   as carried by nothing. Widened from bare-form-only at freeze (brief follow-up
   F5): the recorded span holds the model's *emitted* continuation, normally the
   space-prefixed form, and bare length does not bound space-form length —
   `opal` is 1 token bare but 2 space-prefixed on all three tokenizers, the
   pinned unit-test case.
2. **The ASCII bar.** Every planned direction word must be pure ASCII, else exit
   INVALID — `oracle._BOUNDARY` is `(?![A-Za-z0-9])`, so a non-ASCII
   continuation character would read as a word boundary and a longer non-ASCII
   word could score as a hit (PR #7 F4).

**`oracle.py` itself is untouched**: it is byte-shared with `m1_rescore.py` and
`m2_depth.py` and must stay identical. M3 adds no vocabulary — every roster word
comes from M1's frozen 60, all pure-ASCII spellings — so the boundary rule does
not change; the premise is *pinned* rather than assumed, and the day it breaks
the run refuses instead of silently mis-scoring. Widening `_BOUNDARY` to `\w`
now, with zero live cases and a silent flip of `_` from boundary to
word-character, is the unforced version of the mistake D9 exists to prevent
(rejected option (c)); unit tests alone (rejected option (b)) catch a roster
edit at test time but not an environment or tokenizer drift at the moment of
measurement, which was F5's actual point. The named future trigger is the S2
stretch's translations/synonyms lists: if that stage is reached, its brief owes
the boundary-class decision before freezing any non-ASCII list.

**Companion disposition (PR #7 F6, non-blocking, adopted for the M3 cut).**
`m2_depth.main()` loaded the checkpoint *before* validating inputs, so a
`--dry-run` or a wrong-arm exit still paid a full model load, and its
`validate()` parsed the M1 results JSON only to discard it. Because the M3 runner
is cut from `m2_depth.py`, that shape would have propagated by construction.
`m3_matrix.py` instead validates its inputs — including both bars above —
against a config-derived `SubjectSpec` **before** loading the checkpoint (pinned
by a test that makes `AutoModelForCausalLM.from_pretrained` raise), re-asserts
the loaded model's shape against that spec before any trial, and returns the
parsed M1 artifact from `validate()` for `main()` to reuse. `m2_depth.py` itself
stays untouched, per the certified-predecessor rule.

## D19 — The strip frame: 12 primes × all 180 items (Kyle, 2026-07-29)

Option (a): **the full 12 × 180 strip plus a full clean re-run — 2,340 cells per
subject.** M3 measured collateral *among the 12* and said so in its own Honest
limits: "the matrix measures collateral among 12 concepts, not across the
vocabulary … Nothing here shows that deleting France spares the other 48 M1
concepts." M4 runs exactly that experiment: keep the 12 characterized directions
as the **primes** (the thing deleted), widen the **probes** (the thing asked
about) to all 60 M1 concepts — the whole frozen 180-item battery. Every cell is
the M3 recipe unchanged (late third, λ = 1, k = 1, D9(b) oracle), so cells differ
only in which direction was removed and which item was asked.

Per subject: `clean` (180) + 12 × 180 = **2,340 cells**. The genuinely new
content is the **non-subset pool** — 492 / 852 / 1,008 cells at 0.5B / 1.5B / 3B,
of which 486 / 844 / 993 have never been measured by any milestone.

**The re-certification surface is maximal, and two generations deep.** The strip
contains **255** cells per subject recorded in M1's artifacts (`clean` 180, the
12 subset concepts' `primed_late` 36, and the 39 `control_late` cells whose
control direction is a prime) **and 468** recorded in M3's (the 36 subset `clean`
cells + all 432 matrix cells — everything M3 ran except its 18 out-of-subset
control-extras, whose directions are not strip primes). The two surfaces overlap
in 90 cells, so phase 1 of the run grades their union — **633 of the 2,340** —
and both comparisons run on raw recorded strings (`greedy`, `greedy_3`;
`concept_mass` as texture) **before any new cell is read**. Any mismatch on the
certified stack is INVALID. This is D16's pattern applied against two artifact
sets at once.

Rejected: **(b) 12 primes × the 144 non-subset items only** — saves ~20% of the
run and destroys the M3-overlap re-certification (no subset cells, no diagonal)
plus the in-strip recorded proxies; the one check that has caught nothing yet
*because it runs every time*, broken for one saved coffee break. **(c) the full
60 × 60 matrix** — a different, bigger question ("is *every* direction safe to
delete?") at ~4.7× the cost, with 48 primes no milestone has characterized; that
is a future stage's question, not this close-out's.

**Consequence worth stating.** Every `clean` cell is M1-recorded and gating is
the deterministic clean arm under a frozen oracle, so the realized gate-arm n is
**fixed before the run** at 41 / 71 / 84. A run that disagrees is an INVALID
cross-check, not a power surprise.

## D20 — The pre-committed wording package for M4 (Kyle, 2026-07-29)

Option (a): **a survives-everything level gate on the new pool**, frozen as code
in `m4_strip.GATE_WORDING` before any run and written verbatim into every results
JSON. In brief:

> **VOCAB-SPARING** iff, per subject: among the gated **non-subset** items, the
> proportion that **survives all 12** subset-direction deletions has its Wilson
> 95% lower bound at or above **0.5**. The bar is read **only when** the 468
> M3-recorded and 255 M1-recorded cells reproduce their recorded outcomes
> bit-for-bit. The M4 verdict is the AND over 1.5B and 3B; 0.5B runs under its
> standing any-direction-damage frame and is never gate-bearing. Gate-arm
> n < MIN_N = 20 ⇒ UNDERPOWERED.

Rejected: **(b) an M3-clause-(1)-style ordering gate extended to the strip** —
maximally comparable to M3, and it passes almost by inheritance (the diagonal is
0-to-3 hits at every subject), so it gates nothing; reported beside as
descriptive continuity instead. **(c) the conjunction of (a) AND (b)** — adds
nothing (b) doesn't already concede and re-opens the conjunction-degeneracy
obligation for no inferential gain.

**Why a level gate at all.** The strip's question is a *level* question — "is the
floor high?" — not an ordering question; M3 already settled the ordering. The
per-item survives-all-12 outcome is a true binary, so the Wilson interval is
exact for it. This deliberately does **not** promote M3's cluster-mean floor
readout to gate-bearing: D17 froze that approximation as "acceptable only because
the qualifier is never dispositive," and M4 keeps *that* rationale intact by
reporting the cluster-mean floor beside, reference line 0.5, never dispositive.

**The 0.5 constant is new, and owned as new.** M3's 0.5 was a floor on
cluster-collapsed **per-cell** survival; M4's is a bar on a **12-fold
conjunction**. The same digits mean opposite things across the two statistics:
under independence a conjunction of 0.5 corresponds to a per-cell
0.5^(1/12) ≈ **0.944**. Two consequences, stated rather than inherited. **(i)
Status changed** — M3's constant was itself uncalibrated and D17 tolerated that
only because the qualifier it scoped could never create or rescue a claim; M4
makes a constant of the same value the *single dispositive gate*, so D17's
tolerance does not transfer. **(ii) The deletion count is half the bar** — at a
per-cell rate of 0.971 (M3's recorded 1.5B off-diagonal) the conjunction reads
≈ 0.70 and clears; at 0.94 it reads ≈ 0.48 and fails. So M4's 0.5 is a new,
deliberately lenient, uncalibrated constant, pre-registered before any new cell
was run and fitted to none, with its per-cell equivalence written into
`GATE_WORDING` itself so no write-up can quote it as M3's floor.

**Why the re-certification clause lives inside the wording.** Every prior stage's
gate compared an intervened arm against another *measured* arm, so a dead
intervention could never pass one. M4's bar is single-clause and reads only the
off-target survival rate — read in isolation, an ablation that did nothing at all
would score ~100% survival and print VOCAB-SPARING. The strip's re-run of M3's
432 matrix cells catches exactly that, but that guarantee lived in D19's design
and an exit code, not in the sentence a write-up quotes. Now it cannot be quoted
out of its own precondition.

**Why the realized proportion rides inside the verdict string.** `VOCAB-SPARING`
is the strongest possible phrasing of exactly the over-reading M4 exists to
correct, and the bar it names permits real damage: at the 1.5B pass point (44/71)
**27 of 71** gated non-subset items — 38% — are damaged by at least one of the 12
deletions. Prose owns that, but prose is not what gets quoted; the label is. So
M4 carries the number **inside** the verdict string — M3's `ON A DAMAGED FLOOR`
move, applied to a level bar.

**Amendment 1 (post-freeze, pre-run, ratified by Kyle 2026-07-29).** The verdict
string as first frozen carried only the **as-scored** proportion, so the two
pre-registered reads that can flip which number is honest stayed in prose —
reproducing the exact failure the realized-proportion resolution was meant to
prevent. The wording now carries a pre-declared **AS-SCORED ONLY** qualifier,
attached *conditionally by the runner* whenever a conservative read's Wilson lower
bound falls below 0.5 while the as-scored read's does not, and names a failing
label the single pass-label template had left unstated.

**Amendment 2 (post-freeze, pre-run, ratified by Kyle 2026-07-29),** recorded
separately because Amendment 1's ratification quote covers only Amendment 1.
Four changes: **(i)** the failing label is the lineage's pre-committed null
`not shown`, not the assertive `NOT VOCAB-SPARING` Amendment 1 introduced —
failing a Wilson *lower* bound cannot establish the contrary (at 1.5B, k = 40 has
a point estimate of 0.563 *above* the bar with a straddling interval), and all
three predecessor runners emit `not shown`; **(ii)** 0.5B is scoped inside the
wording — the gate verdict is the AND over the two gate-bearing subjects and
0.5B's readout is never a gate claim; **(iii)** the qualifier attaches to a
**claim-level verdict only**, never to `NOT A RESULT` / `DEGENERATE` /
`UNDERPOWERED` — Amendment 1 had attached it to all of them, contradicting the
D17 rule it cites; **(iv)** both string templates are stated explicitly with a
fixed read order. The gate, its 0.5 bar, its arm and its re-certification
precondition are unchanged by both amendments.

**The two pre-registered conservative reads, never dispositive.**

1. **The residual-conservative read.** D9(b)'s owned span-truncation residual
   re-enters a gate-bearing arm for the first time since M1: `oracle.py`'s frozen
   wording closes with "None of the three concepts is in M2's subset," and M4's
   wider probe side retires exactly that scope sentence. The gate statistic is
   recomputed with every **residual cell** re-scored as a **miss**. A residual
   cell is one whose recorded span, after stripping leading whitespace, **equals
   the scored concept's spelling with nothing following it, compared
   case-insensitively** exactly as `oracle.says_concept_prefix` compares. The
   case rule *decides the set*: the recorded spans are `'Beetle'`, `'Butterfly'`,
   `'Trumpet'` while the roster spellings are lowercase, so a case-**exact**
   comparison would select **zero** cells and silently turn the mitigation into a
   no-op; and the rule is *not* "the span fills the 3-token window", which every
   recorded cell does by construction. On that reading the gate-arm residual cells
   are **0 / 2 / 2** (1.5B `beetle-1`, `butterfly-1`; 3B `trumpet-3`,
   `butterfly-1`). **Denominator: fail in place** — the arm stays at 41 / 71 / 84
   and a residual-affected item scores as a *failure*. The alternative (re-score
   the clean cell too, so the item un-gates and the arm shrinks) is rejected: it
   is the *less* conservative reading at the bar — same numerator,
   `wilson(43, 71)` = 0.489 fails while `wilson(43, 69)` = 0.505 passes — and it
   would break the power table's pre-registered n. `oracle.py` is not touched;
   editing it would force re-runs of three milestones.
2. **The concept-level collapse.** Items cluster three-per-concept on the probe
   side, so the same statistic is recomputed collapsed to one binary per
   **concept** over the non-subset concepts with ≥ 1 gated item (n = 23 / 41 / 43).

If the gate passes and either read does not, **that read's numbers are the honest
ones to quote** — and the AS-SCORED ONLY qualifier puts them in the verdict
string rather than leaving them in prose.

**Degeneracy disposition.** D14/D17's wide-oracle guard, unchanged in mechanism
(pool the first tokens of an arm's non-produced cells only, share against the
arm's full cell count, threshold 0.5). Scope, enumerated — and this enumeration
**discharges PR #9 F1's conjunction-degeneracy obligation**, since M4's gate is
deliberately single-clause and the dispositive list therefore has exactly one
surviving arm: collapse in the pooled **non-subset off-target** arm ⇒
**DEGENERATE**; collapse in the subset **diagonal** ⇒ **TAG only**; `clean` stays
off the dispositive list (the D14 F3 correction, carried); rows, columns and
per-pair cells are **texture**.

**Verdict precedence, frozen** in `m4_verdict.strip_verdict()`: NOT A RESULT >
DEGENERATE > UNDERPOWERED > the level bar. Wrong-arm inputs exit INVALID before
the checkpoint loads; `--dry-run` validates and stops; `--limit` is smoke, never a
result; M4 refuses M1 **or** M3 artifacts that were themselves not results.

## D21 — The five cross-mention cells (Kyle, 2026-07-29)

Option (a): **keep them in the gate-bearing pool and report them as a named
confound row.** Widening the probe side to all 180 items surfaces a confound M3's
12-concept design never had: five (prime, item) pairs whose clue mentions a
prime's spelling. The list is frozen — **October→september-2, silver→flute-1,
China→jade-1, October→opal-2, Egypt→beetle-2** — and scanned with **D5's own
rule**: no word of the clue may *start with* the string, case-insensitive, plus
that string's `forbidden_forms` entries. The prefix rule is why the list is five
and not four: a whole-word scan misses `Egypt→beetle-2`, whose clue inflects the
prime ("Ancient **Egyptians** carved amulets of the scarab"). In those cells a
miss cannot distinguish collateral damage from "the clue's own text lost a word
it references."

*Why keep them:* a confounded miss can only **lower** the floor, so the bias runs
**against** the gate — the one direction this project ships owned. Excluding them
would delete only cells that could hurt the claim, the anti-conservative move the
lineage never makes. Four cells of 852 cannot carry a verdict either way; what
they can do is mislead a *reader* of the column profiles, and the named row
prevents that. Four gate at both gate-bearing subjects (only `jade-1` at 0.5B);
`beetle-2` is ungated on all three and carries no gate-bearing cell today — it is
listed so a future re-gate cannot silently acquire one.

Rejected: **(b) pre-registered exclusion from gate-bearing pools** — evidence
removal in the gate's favour. **(c) drop the five items entirely** — loses their
clean cells and their unconfounded prime cells for no reason.

## D22 — Run-time instrument bars, widened to the full roster (Kyle, 2026-07-29)

Option (a): **both D18 bars in `m4_strip.py`'s pre-trial validation, now over
every scored word — all 60 — plus the 12 direction words, with unit tests.** Span
bar: `max(len(tok(w)), len(tok(" " + w))) ≤ SPAN_TOKENS` on the subject's own
tokenizer, else INVALID. ASCII bar: every spelling pure ASCII, else INVALID.
Verified in advance for all 60 words on all three tokenizers (2026-07-28); the
run-time bar still runs, because D18's point was that the premise must hold *at
the moment of measurement*.

Rejected: **(b) bars over the 12 primes only** (M3's literal scope) — the
soundness premise attaches to every **scored** word, and M4 scores 60, so a bar
checking 12 pins a fifth of the premise. **(c) widen `_BOUNDARY` now** — still
zero live cases, still the unforced version of the mistake D9 exists to prevent
(carried rejection).

**What the span bar cannot catch, stated so it stays owned:** the D9(b) residual
passes the bar at exactly ≤ 3 tokens, which *is* the residual condition. The
residual is carried by disclosure plus D20's residual-conservative read, never by
a bar.

**The `oracle._BOUNDARY` boundary-class decision is not owed here.** D18's named
trigger is a stage freezing a **non-ASCII** list; M4 adds no vocabulary — every
probe and every prime comes from M1's frozen 60, all pure-ASCII spellings. The
premise stays *pinned, not assumed*: the ASCII bar runs at run time, unchanged.
`oracle.py` is untouched, and becomes byte-shared by a fourth consumer (a
deviations-table row, on the same D9 rationale as the first three).

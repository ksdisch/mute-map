# M1 start-of-stage brief — breadth: the battery

*Start-of-stage brief per the per-stage rhythm: plain-terms explanation first,
design extraction second, decisions third, code only after Kyle freezes.
Decisions here are D4–D8, continuing `docs/DECISIONS.md` (D1–D3 were M0's).*

## What M1 is, in plain terms

M0 proved the instrument survived the move. M1 asks the first mapping question:
**is the off-switch a general property of the vocabulary, or a quirk of the 20
concepts S4 happened to use?**

The design is the S4b late-tier cell, scaled out. For each concept in a
~60-concept battery, a clue sentence implies the concept without naming it, and
the model is asked to name it. Three conditions per item:

- **clean** — no intervention;
- **primed_late** — delete that concept's own lens direction (k = 1 projection
  removal — subtract out exactly the component of the activation pointing along
  that one direction) at the late third of the workspace band;
- **control_late** — the identical deletion, but of a *different same-category*
  concept's direction.

If the switch is general, primed_late naming collapses while control_late stays
near clean — pooled across the whole battery ("pooled" = all gated items counted
together as one big cell), CI-cleanly, at 1.5B AND 3B. The per-concept and
per-category rates are the map itself: which parts of the vocabulary have a
switch, and how cleanly. **A low prevalence is a finding, not a failure** — the
battery is designed so any prevalence number is the reportable result.

M1 drops S4b's early/middle tiers (M2's localization job) and the avoidance
instruction (K2: the off-switch is a claim about naming, so the competence gate
is naming-only — the standing owned deviation from S4b's dual gate).

## Design extraction (verbatim, source-cited)

**KICKOFF's M1 milestone (frozen scope):** "~60 concepts across 8–10 categories:
S2/M3 measured vocabularies extended by new frozen lists (single-token filter);
items by S4's constrained-construction recipe (~2–3 clue-sentence naming items
per concept), frozen in `items/` pre-run. Conditions: clean, primed_late,
control_late. Gate: pooled primed_late naming CI-cleanly below control_late
(Newcombe excludes 0) at 1.5B AND 3B. Per-concept switch-rates + per-category
structure descriptive (Wilson CIs). A low prevalence is a finding, not a
failure."

**The item recipe M1 extends — D27c construction rules, frozen in
`items/s4-avoidance-items.json`:** "D27c, frozen 2026-07-17 BEFORE any run.
Concepts drawn only from vocabularies this project has measured: S2
flexible-generalization args (countries, months, animals; numbers excluded per
the S2 knowledge confound) and M3 directed-modulation topic_categories (…).
Controls are another word from the same shipped list. Each clue implies
exactly one concept via famous facts and NEVER contains the concept word, the
control word, or a derivative of either (guarded in test_avoidance.py). 20
concepts x 3 clues = 60 items. The paper-style competence gate (D29) does the
per-subject filtering." (Only the category list is elided, marked (…).) Item
schema: `name`, `category`, `noun` (the category noun the question uses),
`concept`, `control`, `clue`.

**The gate pattern M1's pooled gate follows — S4b's D31 wording (dim-stage
`docs/S4-BRIEF.md`):** "the late switch is concept-specific iff, per subject on
the gated cell, naming success under `control_late` is CI-cleanly above naming
success under `primed_late` (Newcombe excludes 0). Failing it is the headline
against: 'any-direction output damage at the late tier, not a per-concept
switch.'"

**The certified instrument (M0, `m0_anchor.py` — cut from, never edited):**

- Naming question, verbatim: `Consider this sentence: "{clue}"\n\nWhich {noun}
  is the sentence describing? Answer with just the name.` One user turn through
  the chat template.
- Grading: the greedy first token (the model's single highest-probability next
  token — deterministic) is compared against the concept's single-token forms
  (`token_forms`: the word bare and with a leading space, kept only if the
  tokenizer encodes it as exactly one token). Concept softmax mass recorded as
  texture. S4's "The …" miss-counting caveat stands, owned, for anchor
  comparability.
- Machinery: runtime read-back on every edit (`READBACK_TOL`), degeneracy
  guard, single-token prefilter with recorded drops, `MIN_N = 20`,
  `COLLAPSE_SHARE = 0.5`, Wilson/Newcombe from the ported `stats.py`.

**The measured-vocabulary pool (what "measured" means per source):** S2 measured
swap competence over its args (countries, months, animals — numbers excluded for
the knowledge confound); M3 measured directed modulation over 22 shipped
topic-category member lists (months, days of the week, planets, chess pieces,
precious metals, gemstones, farm animals, musical instruments, insects, and 13
more), all in the reference repo's own `directed-modulation.json`. The
candidate roster below was checked against the shared Qwen2.5 tokenizer
(single-token filter) on 2026-07-27 — every listed word passes.

## Decisions to freeze (Kyle picks; recommendations flagged)

*Frozen (Kyle, 2026-07-27): D4 (b) 10 × 6 with minimal top-up; D5 (a) 3 per
concept + S4 reuse; D6 (a) item-level greedy; D7 (a) no per-concept verdicts —
prevalence wording amended pre-run at reviews F1 and F9 of PR #3, Kyle-approved;
D8 (a) widen the comparison. Full DECISIONS.md entries land with the M1 code
PR, per the M0 pattern.*

### D4 — The roster (categories × concepts)

- **(a) Measured-only, uneven categories.** Every concept from a shipped S2/M3
  list, no new vocabulary at all. Countries and animals stay at 4 members
  (S2 shipped only 4 each); gemstones tops out at 4 single-token members while
  months runs 11 deep. ~55–60 concepts. *Trade-off:* purest provenance line,
  but category sizes vary 4–11, which muddies the per-category comparison M1
  is supposed to deliver.
- **(b) Measured + minimal top-up, uniform 10 × 6 = 60 (recommended).** The
  nine S4 categories plus days of the week, each filled to exactly 6 concepts.
  53/60 concepts come from shipped measured lists; **7 new-list words** (Japan,
  Brazil, tiger, bear, flute, opal, amber) fill the gaps where shipped lists run
  dry or fail the single-token filter — owned in the deviations table. *Why:*
  uniform category size makes the per-category map legible, and the naming-only
  competence gate — not list authorship — is what filters items honestly (the
  D27c logic). Full roster below.
- **(c) Fewer, deeper: 8 × 8.** Most M3 categories lack 8 single-token members,
  so this needs ~2× the invented vocabulary for a marginally deeper map.

Candidate roster for (b) — S4's 20 concepts (bold) all present, every word
single-token-verified; alternates in parentheses substitute at freeze only if an
item proves unwritable:

| Category | Concepts (new-list words marked †) |
|---|---|
| countries | **France, Canada, China, Egypt**, Japan†, Brazil† |
| months | **February, April, July, October**, January, September |
| animals | **lion, eagle, shark, spider**, tiger†, bear† |
| planets | **Mars, Saturn**, Venus, Jupiter, Mercury, Neptune |
| musical instruments | **piano, guitar**, violin, drum, trumpet, flute† |
| precious metals | **gold**, silver, platinum, copper, bronze, iron (steel) |
| gemstones | **diamond**, ruby, pearl, jade, opal†, amber† |
| farm animals | **cow**, pig, horse, sheep, chicken, duck (goat†) |
| insects | **bee**, ant, beetle, butterfly, moth, mosquito (cricket) |
| days of the week | Monday, Tuesday, Thursday, Friday, Saturday, Sunday (Wednesday) |

Dedupe rule: each concept lives in exactly one category (spider stays in
animals per S4 precedent, so it is excluded from insects; "fly" excluded as
verb-ambiguous). Controls: a fixed same-category pairing frozen in the item
file (concept ≠ control), reusing S4's pairs where items are reused.

### D5 — Items per concept + construction

- **(a) 3 clues per concept; reuse S4's 60 items verbatim for the 20
  overlapping concepts (recommended).** 180 items total: 60 reused, 120 newly
  authored by the D27c rules (famous facts implying exactly one concept; never
  containing the concept word, control word, or a derivative; guards as code).
  *Why 3:* trials are free — the pooled gate's power scales directly with item
  count, and per-concept rates on 3 items beat 2. *Why reuse:* beyond saving a
  third of the authoring, it buys a live anchor cross-check (below).
- **(b) 3 clues per concept, all-new items.** Uniform authorship style, but
  throws away the cross-check and re-authors what's already frozen and
  battle-tested.
- **(c) 2 clues per concept (~120 items).** Less authoring; measurably less
  power everywhere.

**The built-in anchor cross-check (why (a) matters):** the M1 runner uses the
same naming template, operator, band thirds, and grading as the certified
`m0_anchor.py` — and greedy decoding is deterministic. So for the 60 reused
items, M1's clean / primed_late / control_late naming cells must equal the
recorded anchor JSONs' cells **bit-for-bit**, per subject. That check is frozen
into the M1 runner as a wrong-arm gate: any mismatch on a reused item ⇒ the M1
run is INVALID before any new cell is read. One third of the battery doubles as
a standing re-certification of the instrument, every run. (The comparison is on
raw per-item cells, not gated aggregates — M1's gate membership differs from
S4b's by design, K2.)

### D6 — Competence gate wording (naming-only, K2 — refinement, not relitigation)

- **(a) Item-level greedy gate (recommended).** An item enters the gated set
  iff its clean naming greedy first token is one of the concept's single-token
  forms — exactly S4's D29 greedy gate minus the avoidance half. Gating is
  per-subject (each subject earns its own gated set). The paper-style
  verbatim-P rate (concept mass ≥ .85 clean) is reported alongside as texture,
  never gating. *Why:* item-level is the finest honest unit; the "The …" caveat
  stays owned rather than patched.
- **(b) Concept-level gate.** A concept enters iff ≥ 2 of its 3 items name
  correctly clean, then all its passing items count. Coarser; conflates item
  quality with concept competence; no anchor precedent.

### D7 — Pooled contrast gate + descriptive readouts (wording, pre-committed)

The KICKOFF-frozen core is not up for choice: pooled primed_late naming
CI-cleanly below control_late (Newcombe excludes 0) at 1.5B AND 3B. The wording
package to freeze around it:

- **(a) (recommended)** Per subject, on the pooled gated cell:
  **"BREADTH-SPECIFIC"** iff naming success under control_late minus under
  primed_late is positive and its Newcombe 95% CI excludes 0. The M1 verdict is
  the AND over 1.5B and 3B. 0.5B runs and is reported under its standing
  any-direction-damage frame (pre-declared risk 2), never gate-bearing. Pooled
  n < 20 ⇒ pre-declared UNDERPOWERED. Per-concept and per-category cells are
  always descriptive: paired primed/control rates with Wilson CIs, plus the
  full distribution. Prevalence texture, pre-committed wording (amended at
  reviews F1 and F9 of PR #3, both pre-run, Kyle-approved): the headline count
  uses a **fixed denominator** — only concepts with **all 3 items gated**
  count, and of those, the number showing the **hard-switch profile**
  (primed_late naming 0/3 AND control_late 3/3) is reported with its Wilson CI
  over that fixed set, carrying the pre-declared **UNDERPOWERED** tag whenever
  that set holds fewer than MIN_N = 20 concepts — exactly the flag the ported
  `rate_cell` emits on the cell, so code and prose agree. The anchor data
  projects ~15–18 all-3-gated concepts of 60, so the tag is the expected case,
  stated here so it reads as pre-declared, not discovered. The fixed set is
  per-subject (each subject earns its own; the anchor sets already differ);
  no cross-subject prevalence comparison is gated or claimed — the
  intersection of the three subjects' fixed sets is reported beside as
  texture. Concepts with 1 or 2 gated items are reported beside, stratified by
  gated-item count, never pooled into the headline — a 1-gated-item concept
  satisfies the profile trivially, and sparse gating tracks marginal
  competence. No per-concept verdicts. Stats honesty row, owned: items within a concept share one
  direction, so item-level pooling overstates independence; S4b pooled the same
  way, and the per-concept map is the honest granular view beside it.
- **(b) Same, plus a binary per-concept "switched" verdict** at a pre-committed
  threshold (primed_late 0/3 AND control_late ≥ 2/3), headline "X% of concepts
  have an off-switch." *Trade-off:* legible, but a per-concept cell of n = 3
  has a CI from floor to ceiling — a labeled verdict on it invites exactly the
  over-reading the "CI overlaps ⇒ not a result" rule exists to stop.

### D8 — Widen the anchor comparator's frozen bar (review F4)

D3 froze `m0_port_gate.py`'s config comparison to model_id / band / thirds /
item roster / dropped list. Both recorded JSONs also carry the full `protocol`
block (readback_tol, min_n, collapse_share, gate wording) and `lens_n_prompts`
— the fields that would catch a silently softened instrument. Widening the
comparison is a change to a frozen bar, so it gets its own decision:

- **(a) Widen (recommended).** Add `protocol` and `lens_n_prompts` to the
  compared keys (`lens` itself stays out — it is a path and may legitimately
  differ). Lands with M1's code PR alongside F10's error-path hardening; safe
  by construction — the committed artifacts already match byte-for-byte, so the
  widening cannot flip M0's PASS, only catch future drift.
- **(b) Keep D3's narrow list.** The bar stays as frozen; the gap stays open.

## Review follow-ups landing in M1 (from PR #2's adversarial review)

- **This PR (docs):** F6 — README + CLAUDE.md said "M0 next"; refreshed. F3 —
  re-certification recipe added to CLAUDE.md (the standing `--all` gate is
  tautological unless `results/` is regenerated first).
- **This brief:** F4 → D8 above.
- **M1 code PR:** F7 — the M1 runner imports `MIN_N`/`COLLAPSE_SHARE` from
  `harness` instead of re-binding them (the shadowing stays untouched in the
  certified `m0_anchor.py`). F5 — the M1 runner and tests carry no dead
  imports. F9 — M1's `validate()` tests assert the printed reason per guard
  (capsys), not just the exit code. F10 — `m0_port_gate.py`'s `load()` widens
  its except tuple to OSError/UnicodeDecodeError and opens via `with`. F11 —
  the `--all`/pair mutual-exclusion branch gets tests that actually reach it
  (complete pair + empty argv).

## Deviations table additions (owned)

| Deviation | From | Owned reason |
|---|---|---|
| Naming-only competence gate | S4b's dual gate | K2, standing: the switch is a naming claim; expected to unlock powered ns at all scales |
| 7 new-list concept words (D4b) | D27c's measured-only rule | KICKOFF sanctions "extended by new frozen lists"; the competence gate does the honest filtering; all 7 marked † in the frozen file |
| Item-level pooling in the gate cell | independence assumption | Items within a concept correlate; S4b precedent; per-concept map reported beside |
| M1 runner cut from `m0_anchor.py`, not shared | single-runner reuse | Certified file stays untouched post-gate; divergences (naming-only, 3 conditions, F5/F7 cleanups) owned in the runner docstring |
| Word-prefix + `forbidden_forms` leak guard | S4's substring leak test | With 60 short concepts a substring test makes "plant" a leak for "ant"; the prefix test still catches every suffixed derivative and the frozen list catches the root-changing ones. All 60 reused S4 items pass the stricter guard unchanged (D5) |
| First-3-greedy continuation recorded per cell | `m0_anchor.py` records none | CLAUDE.md's standing secondary-texture readout, implementable for the first time in our own runner; never gating, never in a verdict. M1 is where it earns its keep — see the tokenization caveat in the results |

## Expected power (honest math)

S4's clean-naming pass rates were 20/28/21 of 60 items (0.5B/1.5B/3B) — the
naming-only gate at those rates projects pooled gated n ≈ 60/84/63 from 180
items. KICKOFF's "pooled n ≥ 100" expectation needs a ~56% pass rate; plausible
if the new categories (days, planets, metals) name more easily than S4's mix,
but not guaranteed. Either way every pooled **item** cell clears MIN_N = 20 with
a wide margin — and the realized gated n per category is itself reported
cartography (which vocabulary the model can name unablated is part of the map).

**The one pre-declared exception (review F11).** The prevalence readout's cell
is a *concept* count, not a pooled item cell, and its fixed denominator
(concepts with all 3 items gated) projects to ~15/18/15 of 60 on the anchor
data — **below MIN_N = 20**. It therefore carries the pre-declared UNDERPOWERED
tag per D7(a), and it is the only cell in M1 that does. Stated here so the
power section and the D7 wording agree rather than leaving a reader who stops at
"Expected power" with a rosier picture than the brief's own gate supports. The
direction of the projection's error is safe: it linearly scales the 20 S4
concepts' gating rate onto a roster whose 40 new concepts have never-measured
clues, so if the new vocabulary gates *worse*, the set is smaller and the tag is
*more* certain, not less.

## Wall-clock plan

180 items × 1 instruction × 3 conditions = 540 forward passes per subject —
64% of M0's 840, which ran in minutes per subject on MPS. All three subjects
comfortably inside an hour, $0, run in background with untracked logs. Standard
machinery regardless of decisions: wrong-arm input exits INVALID; `--dry-run`
validates and stops; `--limit` is smoke, never a result; gate wording frozen as
code before any real run.

## Results (2026-07-28) — GATE PASSED, with a readout caveat that bounds the claim

**M1 verdict: BREADTH-SPECIFIC at 1.5B AND 3B.** Both gate-bearing subjects show
pooled `control_late` naming CI-cleanly above `primed_late`, so the pre-committed
gate passes. Every run re-certified the instrument on the way in: the 60 reused
S4 items reproduced the recorded anchors **bit-for-bit, 180/180 cells, with
`concept_mass` floats exact 180/180**, on all three subjects.

| Subject | Gated n / 180 | `primed_late` | `control_late` | control − primed [Newcombe 95%] | Verdict |
|---|---|---|---|---|---|
| 0.5B *(context only, never gate-bearing)* | 38 | 0/38 | 17/38 | **+0.447** [+0.275, +0.603] | BREADTH-SPECIFIC |
| 1.5B *(gate-bearing)* | 61 | 0/61 | 40/61 | **+0.656** [+0.517, +0.763] | BREADTH-SPECIFIC |
| 3B *(gate-bearing)* | 44 | 6/44 | 34/44 | **+0.636** [+0.443, +0.759] | BREADTH-SPECIFIC |

Prevalence, fixed denominator (all three carry the **pre-declared UNDERPOWERED**
tag, exactly as forecast): 0.5B **4/8**, 1.5B **9/11**, 3B **6/8** concepts show
the hard-switch profile. Texture only, per D7(a): the three subjects share 6
all-3-gated concepts, of which 3 show the profile in all three (China, France,
Japan); the two gate-bearing subjects share 6, of which 5 do (Brazil, Canada,
China, France, Japan). No degeneracy: no gated arm collapsed on any subject, so
the pre-committed disposition never fired.

**0.5B came in BREADTH-SPECIFIC too — and the pre-declared frame says what that
means.** S4b's 0.5B cell did *not* show specificity, on a gated n of 5. Here the
naming-only gate (K2) lifts 0.5B to n = 38 and the contrast is CI-clean. The
honest reading is the one the deviations table forecast: S4b's 0.5B null was
**underpowered, not evidence of absence**, and the lineage's "specificity emerges
by scale" story weakens accordingly. M1 does not claim a scale story; it reports
that all three subjects show the switch once each has the power to see it.

### The caveat that bounds the breadth claim: the readout, not the model, sets the coverage

The competence gate admitted 38 / 61 / 44 of 180 items. The dominant reason is
**not** that the model doesn't know the answers — it is a property of the
readout. The primary oracle is the greedy *first token*, and a concept can only
be scored if its spelling at the answer position is a single token. **26 of the
60 roster words have a multi-token bare (no-leading-space) form** — Mars, Venus,
Jupiter, Mercury, Neptune, piano, guitar, violin, trumpet, flute, platinum,
copper, bronze, pearl, jade, sheep, chicken, beetle, butterfly, mosquito and
others — and at the answer position the model *usually* spells them without the
leading space. Its first token is then a fragment (`'Mer'`, `'Viol'`, `'Fl'`),
which the gate scores as a miss. Usually, not always: the same words are single
tokens *with* a leading space, so one occasionally gates when the model emits
that form — `jade` gated 1/2/1 times across the three subjects on a clean greedy
of `' jade'`. The bias is heavy, not absolute. This is the general form of S4's owned "The …"
miss-counting caveat; at 20 concepts it was a nuisance, at 60 it removes half
the roster.

The first-3-greedy texture readout (added here per CLAUDE.md's standing
secondary-texture guardrail) measures the cost directly rather than assuming it:

- Gated items come almost entirely from the 34 single-bare-token concepts —
  **37/38, 59/61, 43/44**. The other 26 concepts contribute 1, 2 and 1 gated
  items respectively.
- Among *ungated* items the model still said the concept within 3 tokens in
  **35/142 (0.5B), 54/119 (1.5B), 80/136 (3B)** — competence the primary readout
  cannot see.
- Whole categories therefore gate near zero at every subject — planets and
  musical instruments gate **0 items on all three subjects**, because every one
  of their six members is multi-token in bare form. The per-category map is
  consequently, in part, a map of tokenizer geometry rather than of concepts.

**What this does and does not undermine.** It does *not* threaten the gate: the
contrast is computed within the gated set, and gating is a property of the
`clean` arm alone, decided before any ablation. It *does* bound the claim's
reach — M1 establishes breadth over *the vocabulary the single-token greedy
readout can see*, which is not the same as the whole measured vocabulary, and
the per-category structure should not be read as a map of which concepts have
switches.

Crucially, the texture also shows **the readout bias runs against the finding,
not for it**. On the gated cell the model said the concept within 3 tokens in
`control_late` **17/38, 46/61, 36/44** — i.e. at 1.5B and 3B the control arm
sometimes says the word without *starting* with it, so the primary readout
*understates* control-arm survival. Under `primed_late` it said the concept
**0/38, 0/61, 6/44** — exactly matching the primary count. So the mute is real:
under a concept's own late-band ablation the model does not say the word at all
within three tokens, while the arm it is compared against is, if anything,
scored too harshly.

**Follow-up owed (not a post-hoc gate change).** The gate stayed exactly as
pre-committed; nothing here was rescored. The obvious instrument fix — accepting
the leading-space form, or scoring on the 3-token span — is a *change to the
oracle*, so it belongs in a decision, not in a results section. M2 should open
with it, and any re-scoring of M1 under a widened oracle must be reported as a
separate, clearly-labelled reanalysis alongside these pre-committed numbers.

### REANALYSIS (2026-07-28, landed with the M2 code PR) — the same cells under the widened oracle

> **This is a reanalysis, not an M1 result.** Everything above was computed under
> the pre-committed first-token oracle and **stands as published**; M1's verdict
> of record is unchanged. The table below re-scores *the same recorded cells*
> under the widened oracle frozen as decision **D9(b)** and is published beside
> them per **D10(a)**. It is a pure function of `results/m1-battery-*.json` —
> no model was run, no new trial was measured — produced by `m1_rescore.py`
> and written to `results/m1-rescore-*.json`.

Why an offline re-score is sound rather than merely cheap: the widened oracle
reads the 3-token span M1 already recorded for every cell, and 3 tokens ≥ the
longest bare form on the roster. For a *prefix* rule truncation cannot hide a
hit, since a hit must start at the span's first character. The script also
recomputes M1's **published** first-token contrast from the same file and
refuses to write anything unless it reproduces it exactly — which it does, on
all three subjects.

| Subject | Gated n (first-token → widened) | `primed_late` | `control_late` | control − primed [Newcombe 95%] |
|---|---|---|---|---|
| 0.5B *(context only)* | 38 → **69** | 0/69 | 33/69 | **+0.478** [+0.353, +0.594] |
| 1.5B *(gate-bearing)* | 61 → **105** | 0/105 | 80/105 | **+0.762** [+0.665, +0.833] |
| 3B *(gate-bearing)* | 44 → **116** | 12/116 | 92/116 | **+0.690** [+0.582, +0.767] |

**What the widening buys.** The readout caveat above said the coverage bound was
a property of the readout, not the models. Re-scored, it is: the two categories
that gated **0 items on every subject** light up — planets **0 → 7 / 8 / 15** and
musical instruments **0 → 2 / 8 / 13** of 18 items each (0.5B / 1.5B / 3B). The
case-insensitivity half of D9(b) is doing real work on its own: at 1.5B the
prefix gate reads **72 case-exact versus 105 case-insensitive**.

**The contrast survives the widening on every subject**, and on the arm that
matters most it survives in the harder direction: `control_late` gains far more
items than `primed_late` does (at 1.5B, primed stays at exactly 0 across 105
gated items). Under the first-token readout one could argue the mute was partly
an artifact of fragment-scoring; it is not.

**PR #4 review F5 closes here, as a recorded number rather than a PR comment**
— and under **both** oracles (PR #5 review F4). The worry was that the contrast
might be carried by the 60 items S4 itself selected. It is not: on the **120
newly authored items alone** it is CI-clean on all three subjects, under the
first-token oracle **+0.278 / +0.545 / +0.478** and under the widened one
**+0.389 / +0.714 / +0.629** (0.5B / 1.5B / 3B). The reused-item stratum runs
higher, as expected for items chosen against a model that could already name
them, but the new stratum stands on its own.

## Addenda landed with the M1 code PR (PR #3 review follow-ups)

All four were accepted at PR #3's review and deferred here by design: each one
belongs in the runner's pre-committed gate wording, which is frozen as code in
`m1_battery.GATE_WORDING` and written verbatim into every results JSON, so the
prose and the code cannot drift. Full text in `docs/DECISIONS.md` D5 and D7.

- **F5 — degeneracy disposition.** The guard is read on the **gated** cell (the
  cell the verdict is computed on). Collapse in `clean` or `control_late` — the
  two comparison arms — is pre-declared DEGENERATE and no BREADTH-SPECIFIC claim
  is made; collapse in `primed_late` is a TAG only and the verdict stands,
  because a shared attractor under the concept's own ablation is the expected
  signature of the switch rather than evidence against it. Checked against the
  already-recorded anchors before freezing: it fires on neither gate-bearing
  subject (gated attractor shares 1.5B .136/.364/.136, 3B .375/.375/.375), so it
  changes no existing verdict. Precedence, frozen in `breadth_verdict()`:
  NOT A RESULT > DEGENERATE > UNDERPOWERED > the contrast.
- **F6 — the honesty row owns the paired-arms violation too.** `primed_late` and
  `control_late` are measured on the *same* gated items while `newcombe_diff` is
  Newcombe's method 10 for two *independent* samples; for positively correlated
  paired arms that **widens** the interval, so it can cost power but cannot
  manufacture a false BREADTH-SPECIFIC verdict. Added in the same row: MIN_N = 20
  is applied to raw n, not to an effective n discounted for the within-concept
  clustering the row's first clause already owns.
- **F7 — the cross-check is environment-scoped.** Bit-for-bit greedy
  reproduction is a property of the certified stack (device `mps`, torch 2.13.0,
  transformers 5.13.1), not of the instrument alone. On that stack a mismatch is
  INVALID (exit 2); off it the cross-check still runs and is recorded but is not
  gate-bearing, and the whole run is pre-declared NOT A RESULT — `m1_verdict.py`
  refuses to let such a run feed the verdict. The runner also **grades the 60
  reused items first** (`order_reused_first`), which is what makes "before any
  new cell is read" literally true rather than aspirational.
- **F11 — the expected-power section names its own exception.** See the clause
  added to "Expected power" above: the prevalence concept-set is the single
  pre-declared sub-MIN_N cell in M1.

## What M1 does NOT decide

- The sliding-window scheme or partial-ablation dose curve (M2's brief).
- The prime × probe matrix design (M3's brief; M3 draws its ~12-concept subset
  from M1's roster, stratified by M1's measured switch rates).
- Anything about 7B (S1 stretch, only if reached).

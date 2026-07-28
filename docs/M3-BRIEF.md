# M3 start-of-stage brief — the specificity matrix

*Start-of-stage brief per the per-stage rhythm: plain-terms explanation first,
design extraction second, decisions third, code only after Kyle freezes.
Decisions here are D15–D18, continuing `docs/DECISIONS.md` (D9–D14 were M2's).
Per HANDOFF, this brief also gives an explicit disposition to each of the three
carry-forwards from M2's adversarial review — plus HANDOFF's fourth,
non-blocking carried item, PR #7 F6 (its own section, before the decisions) —
none is left as a passing mention.*

## What M3 is, in plain terms

M1 established that the off-switch is broad. M2 established that it is late —
the concept's own direction can be deleted almost anywhere else at full
strength and naming mostly survives — and that it is a dimmer, not a step.
Both milestones measured specificity the same narrow way S4b did: **one**
control cell per concept, the direction of one same-category alternative
(delete Canada's direction, check that France still comes out). That single
cell is what "concept-specific" has rested on so far.

M3 replaces the single control cell with the full grid. Take the 12 subset
concepts. For every **ordered pair** (A, B) — "ordered" meaning A→B and B→A
are different cells — delete concept A's direction at the late third and ask
concept B's naming items. That is a 12 × 12 matrix of cells:

- The **diagonal** (the cells where A = B) is muting the word itself — exactly
  the `primed_late` cells M1 and M2 already measured.
- The **off-diagonal** (A ≠ B, 132 ordered pairs) is the *collateral* map:
  what else breaks when you remove one word's direction? M1's control cell was
  one off-diagonal sample per concept; the matrix measures all 11 per concept,
  in both directions of every pair, within and across categories.

If the switch is truly per-concept, the matrix should be dark on the diagonal
and light off it. The interesting failure modes are just as reportable: a
*block* structure (deleting France hurts all countries — category-level
collateral), a non-specific *row* (silver's direction damages everything —
M2's anti-example, now measured against 11 probes instead of 1), or an
asymmetric pair (deleting A breaks B but not vice versa). KICKOFF calls the
resulting figure the killer figure, and the gate is the pooled version of
"dark diagonal, light elsewhere": diagonal suppression CI-cleanly exceeds
off-diagonal collateral at 1.5B AND 3B.

M3 runs at the switch's home — the late third only, full deletion only
(λ = 1, k = 1). Depth and dose were M2's questions; M3 holds both fixed, so
every matrix cell differs from every other in exactly one thing: *which*
direction was removed.

## Design extraction (verbatim, source-cited)

**KICKOFF's M3 milestone (frozen scope):** "M3 — specificity matrix (3–4 days,
$0). ~12×12 prime-A × probe-B naming matrix at the switch's home band, 1.5B +
3B. **Gate: diagonal suppression CI-cleanly exceeds off-diagonal collateral at
both scales.** Within- vs cross-category collateral structure reported. The
killer figure."

**The convention the matrix generalizes — dim-stage S4-BRIEF D28:** "k = 1
(the implied concept's own J-lens vector, M1's direction convention);
specificity control = the same-category alternative's vector through the
identical operator. S3's runtime read-back and degeneracy guard unchanged."
The matrix is D28's control clause with "the same-category alternative"
replaced by "each of the other 11 subset concepts in turn" — same operator,
same read-back, same guard.

**The gate pattern M3's gate follows — S4b's D31 wording (dim-stage
`docs/S4-BRIEF.md`):** "the late switch is **concept-specific** iff, per
subject on the gated cell, naming success under `control_late` is CI-cleanly
above naming success under `primed_late` (Newcombe excludes 0). Failing it is
the headline against: 'any-direction output damage at the late tier, not a
per-concept switch.'" M3's gate is this wording with the one control arm
widened to the pooled off-diagonal.

**What the lineage has already measured of this matrix (the anchor cells):**
S4b's gated late cells — primed_late 0 / 0 / 0 vs control_late 1 / 16 / 8
(0.5B n=5 / 1.5B n=22 / 3B n=8), gate contrast at 1.5B **+.727 [+.471,
+.868]**. M1's powered version on the full battery: control − primed **+0.656
[+0.517, +0.763]** (1.5B, n=61) and **+0.636 [+0.443, +0.759]** (3B, n=44)
first-token; +0.762 / +0.690 under the widened oracle (reanalysis, D10). On
the 12-concept subset, M2's tier cells re-showed the same shape (1.5B
control_late 30/34 vs primed_late 0/34). Every one of these is a *single*
control direction per concept; 126 of the matrix's 132 ordered off-diagonal
pairs have never been measured.

**Instrument facts the design stands on (recorded artifacts, checked
2026-07-28):**

- **Gated sets are already known, exactly.** Gating is the clean arm under
  D9(b), deterministic and recorded: pooled gated n **28 / 34 / 32** (0.5B /
  1.5B / 3B) on the 36 subset items — M2's realized numbers, unchanged,
  because M3 reuses the same items and the same clean arm. Per-concept gated
  counts at 1.5B: all six countries, Jupiter, Mars, October and silver gate
  3/3; piano and violin gate 2/3.
- **The frozen control pairings put 6 of the 12 recorded control cells inside
  the matrix.** The six countries' M1 controls are all subset members, so
  those 18 recorded `control_late` item-cells are matrix cells. In this
  brief's prime→probe (A→B) notation — corrected at this PR's review (F4),
  which caught the list written probe→prime — the six recorded ordered pairs
  are **Canada→France, China→Canada, Egypt→China, France→Egypt, Brazil→Japan,
  Japan→Brazil** (e.g. the recorded cell for France's items ablates *Canada*,
  France's frozen control, and probes France: pair (Canada, France)). The
  other six concepts' controls (February, Saturn, Mercury, guitar, drum,
  platinum) are outside the subset.
- **No cross-mention confound in the items.** Checked on the frozen
  `items/m1-battery.json`: no subset concept's clue contains any other subset
  concept's spelling at a word boundary, case-insensitive. So an off-diagonal
  cell can never break because the ablated word literally appeared in the
  probe's clue text. (Pinned as a unit test in the M3 code PR.)
- **Direction keying is carried, per item, as recorded.** Each concept's
  direction is keyed to its bare-form unembed row where that is a single
  token, else the leading-space row (the S2-stratum convention, D11 / PR #5 F3, owned
  with evidence); M2's artifacts record `direction_key` per item and M3
  inherits them verbatim.
- **Late thirds (frozen band arithmetic, from M2's extraction):** L17–21
  (0.5B), L19–24 (1.5B), L26–32 (3B). Every matrix cell ablates the
  subject's full late third — the identical layer set for every direction.

**Paper context (context, never a reproduced claim):** the seed paper's Figure
69 late-band texture — the late workspace copy as "the intention to say this
word" (transformer-circuits.pub/2026/workspace). The matrix asks how *private*
each word's intention-to-say machinery is: one direction per word, or shared
machinery that collapses in blocks.

## Dispositions for M2's review carry-forwards — three blocking + one non-blocking (explicit, per HANDOFF)

**PR #7 F2 — the tier-width caveat and M3's `GATE_WORDING`.** The caveat: M2's gate
compared tiers of unequal layer count (the late third takes the band
remainder — 4 vs 6 layers at 1.5B), so depth and intervention size differed
between compared arms; the instruction was that if M3 uses tiers, its frozen
wording must say this up front. **Disposition: M3's design retires the
confound structurally, and its wording says so affirmatively.** M3 has no
tier contrast — every matrix cell ablates the *identical* late-third layer
set, so the two arms the gate compares (diagonal vs pooled off-diagonal)
differ in which direction is removed and in nothing else: not depth, not
layer count, not λ. D17's pre-committed wording carries one clause stating
exactly that, so the caveat's lesson is owned in the frozen wording rather
than silently mooted. If a later stage ever re-introduces tiers, the caveat
clause must come back with them.

**PR #7 F5 — the "3 tokens ≥ longest bare form" premise becomes a run-time bar.**
The premise carries D9(b)'s whole soundness argument (a prefix hit cannot be
hidden by span truncation *because* every roster word fits the span) and no
test reproduced it; the review's suggested shape was a run-time check in the
runner's `main()`. This matters now because M3 fixes a roster (even reusing
M2's 12 — the bar is what makes "the roster is scoreable" a checked fact
rather than an inherited assumption). **Disposition: adopted as pre-committed
validation, D18(a)** — before any trial, every planned concept's bare form
must tokenize to ≤ `oracle.SPAN_TOKENS` on the subject's own tokenizer or the
run exits INVALID, plus a unit test. `oracle.py` itself is untouched (it is
byte-shared with `m1_rescore.py` and must stay identical).

**PR #7 F4 — the oracle's boundary class if M3 adds non-ASCII vocabulary.**
`oracle._BOUNDARY` is ASCII-only (`[A-Za-z0-9]`), so a non-ASCII continuation
character would read as a word boundary and a longer non-ASCII word could
score as a hit; switching to `\w` flips `_` and is a rule change needing a
decision. **Disposition: M3 adds no vocabulary, so the rule does not change —
and the premise is pinned rather than assumed.** Every D15 branch draws its
roster from M1's frozen 60, all of which are pure-ASCII spellings; D18(a)
adds the corresponding run-time bar (every roster spelling ASCII, else
INVALID) beside F5's, so the day the premise breaks, the run refuses instead
of silently mis-scoring. Changing `_BOUNDARY` with zero live cases would be
an unforced mid-project measurement change — the exact thing D9 established
belongs in a decision *when a live case exists*. The named future trigger is
the S2 stretch's translations/synonyms lists; if that stage is reached, its
brief owes the boundary-class decision before freezing any non-ASCII list.

**PR #7 F6 — the fourth carried item (non-blocking), dispositioned at freeze
(this PR's follow-up F8).** HANDOFF also carries PR #7's F6: `m2_depth.main()`
loads the checkpoint *before* validating inputs — so `--dry-run` and
wrong-arm exits still pay a full model load — and its `validate()` parses
the M1 results JSON only to discard it, so `main()` parses it twice. Because
the M3 runner is cut from `m2_depth.py`, that shape would propagate by
construction. **Disposition: adopted for the M3 cut** — `m3_matrix.py`
validates its inputs before loading the checkpoint (a `--dry-run` or
wrong-arm exit touches no model), and `validate()` returns the parsed M1
artifact for `main()` to reuse instead of re-parsing. `m2_depth.py` itself
stays untouched, per the certified-predecessor rule.

## Decisions to freeze (Kyle picks; recommendations flagged)

*Frozen (Kyle, 2026-07-28): D15 (a) reuse M2's pre-registered 12 verbatim;
D16 (a) full re-run with the embedded 108-cell re-certification graded
first; D17 as written with both review-added elements kept — clause (2),
and the collateral-floor qualifier under its F11 re-definition (decided on
the per-item collapse, not the pooled n); D18 (a) both run-time bars, with
the span bar widened per follow-up F5 (max of bare and space form ≤
`SPAN_TOKENS`). Full DECISIONS.md entries land with the M3 code PR, per the
M0/M1/M2 pattern. Amended pre-freeze at PR #8's adversarial review: F1–F4
and F10 fixed and verified in-run; F11 and F13 fixed at freeze; the seven
follow-ups (F5–F9, F12, F14) all pulled in at freeze, Kyle-approved
("pull all 7"). Amended post-freeze, pre-run, at the same review's round 4
(F15 + F16): the floor readout's collapsed statistic is the cluster-mean,
not the all-11 conjunction — the honest item-level n Kyle froze is
unchanged; the conjunction it replaced was decided by correlation
structure, not damage — and the recorded-proxy paragraph replaces a false
ceiling claim with the measured in/out-of-matrix split. Flagged for Kyle's
ratification in the merge brief.*

### D15 — The matrix roster: reuse M2's 12 or re-derive (decide first)

- **(a) Reuse M2's pre-registered 12, verbatim (recommended).** Brazil,
  Canada, China, Egypt, France, Japan, Jupiter, Mars, October, piano, silver,
  violin — with their 36 frozen M1 items, gated sets, and per-item
  `direction_key` exactly as recorded. *Why:*
  - **Zero new discretion.** The subset was frozen by D11's stratified rule
    before any M2 cell existed; reusing it verbatim means M3's selection
    surface was pre-registered two milestones ago — the strongest position a
    specificity claim can argue from.
  - **The characterization stays on one cast of concepts.** M2 just mapped
    these 12 in depth and dose; the matrix completes the same concepts'
    story (breadth → depth → dose → collateral), which is the legible
    portfolio arc KICKOFF is buying.
  - **The strata keep doing their jobs, now against 11 probes instead of 1.**
    S1's six countries give a dense within-category block (30 of the 34
    within-category ordered pairs — the S4b control generalized in both
    directions); **silver**, the named non-specific anti-example, sits inside
    the pooled off-diagonal where its collateral *lowers* off-diagonal naming
    and so biases against the gate, never for it (silver only — the pooled
    arm's *composition* biases the other way, owned in D17 per this PR's
    review F2); Egypt and October carry the
    replicated leak texture; the S2 stratum tests whether space-keyed
    directions splash differently.
  - **The re-certification surface is maximal** (D16): 90 of the matrix's
    cells per subject are already recorded in M1's artifacts.
  *Trade-off, owned:* the category structure is lopsided (6 countries / 2
  planets / 2 instruments / 1 month / 1 metal), so the within- vs
  cross-category readout is mostly a countries story — within-category cells
  are 30/34 country pairs, and October and silver have no same-category
  sibling in the matrix at all (their recorded M1 control cells, run as
  re-certification texture under D16, are their only same-category
  collateral sample).
- **(b) Re-derive a category-balanced 12 from M1 + M2 evidence.** A frozen
  rule (e.g. 4 categories × 3, top-gated per category under D9(b)) buys a
  balanced within/cross grid. *Trade-off:* discards M2's per-concept depth
  and dose evidence for the swapped-in concepts, shrinks the embedded
  re-certification, re-opens selection discretion one milestone before the
  headline figure, and de-samples the one stratum where the hard switch is
  *measured* to live (countries). Not recommended.
- **(c) Reuse the 12 but swap out the awkward strata** (silver's non-specific
  row, October's siblingless cell) for more within-category pairs. Cleaner
  figure, dishonest sample: it deletes exactly the concepts pre-registered to
  keep the aggregate honest. Not recommended.

### D16 — Matrix cells + the embedded re-certification

- **(a) Full re-run of the 12 × 12 grid with the recorded cells graded first
  (recommended).** Per subject: `clean` (36 items) plus every (direction A ×
  item of B) cell — 12 × 36 = 432 ablated cells — at the late third, λ = 1,
  k = 1, naming instruction only, D9(b) oracle, first-token outcome recorded
  beside every cell as always. Additionally, the six out-of-subset control
  directions (February, Saturn, Mercury, guitar, drum, platinum) run **on
  their paired concepts' 3 items only** (+18 cells): they are not matrix
  cells, but they complete the recorded `control_late` surface — that is
  their primary job — and they give **October and silver**, the two subset
  concepts with no same-category sibling in the matrix, their only
  same-category collateral sample (Jupiter↔Mars and piano↔violin already
  have in-matrix sibling cells; corrected at freeze, follow-up F6).
  Reported as texture beside the matrix.
  **The standing re-certification, a generation deeper:** the 108 cells this
  run shares with M1's recorded artifacts — `clean` (36), the diagonal (= 36
  `primed_late` cells), and the control cells (18 inside the matrix + the 18
  extras) — must reproduce `results/m1-battery-*.json` on the raw recorded
  fields (`greedy`, `greedy_3` decoded strings; `concept_mass` as texture)
  **before any new off-diagonal cell is read** — graded first
  (`order_reused_first`), the identical 108-cell surface M2 re-certified.
  On the certified stack (`mps`, torch 2.13.0, transformers 5.13.1) any
  mismatch is INVALID (exit 2); off it the check is recorded but the run is
  pre-declared NOT A RESULT and the verdict script refuses it. Raw-string
  comparison, so oracle-independent — the standing pattern, unchanged.
- **(b) Reuse the recorded cells instead of re-running them** (diagonal and
  control cells copied from M1's JSONs; only genuinely new pairs run).
  Saves ~25% of the run and destroys the re-certification — the one check
  that has caught nothing yet *because* it runs every time. Breaks the
  standing pattern for one saved coffee break. Not recommended.
- **(c) Matrix × tiers or matrix × λ.** Explodes the run 3–5× and answers
  questions M2 already answered; KICKOFF fixes M3 at the home band. Not
  recommended.

### D17 — The pre-committed wording package (gate, degeneracy, precedence)

**Gate wording (pre-committed; frozen as code in `m3_matrix.GATE_WORDING`
before any run and written verbatim into every results JSON).** Per subject,
on the pooled gated cell — gating is the clean arm under D9(b), decided once
per item and direction-independent, so every matrix cell shares one gated
set:

> **MATRIX-SPECIFIC** iff BOTH, per subject on the pooled gated cell:
> **(1)** naming under the pooled **off-diagonal** cells (every gated item
> under each of the 11 directions that are not its own concept's) minus
> naming under the pooled **diagonal** cells (each gated item under its own
> concept's direction) is positive with its Newcombe 95% CI excluding 0;
> AND **(2)** the same contrast restricted to the **within-category**
> off-diagonal cells (each gated item under its same-category subset
> siblings' directions only) is likewise positive with its Newcombe 95% CI
> excluding 0 — the S4b-comparable arm, since the lineage's control has
> always been same-category. Both arms of clause (2) — its off-diagonal
> pool AND its diagonal — are restricted to the gated items whose concept
> has **at least one within-category subset sibling**; October's and
> silver's items drop from this clause by construction, not by choice
> (they have no sibling, so their "within-category collateral" is an empty
> set — this PR's review F10). Stated per arm so the runner cannot guess
> (this PR's review F13): clause (2) compares the within-category
> off-diagonal **cells**, n = **96 / 100 / 101** (0.5B / 1.5B / 3B),
> against the **diagonal cells of the same restricted item set**, n =
> **24 / 28 / 29** — MIN_N guards that diagonal n — while the per-item
> 24-vs-24 collapse is the separately pre-registered, never-dispositive
> effective-n check (power section). The M3 verdict is the AND over 1.5B and 3B;
> 0.5B runs and is reported under its standing any-direction-damage frame,
> never gate-bearing. Pooled diagonal gated n < MIN_N = 20 ⇒ pre-declared
> UNDERPOWERED and no specificity claim. **Collateral-floor qualifier,
> pre-committed:** the ordering contrasts above cannot by themselves
> distinguish a per-concept switch from graded damage that is merely worse
> on-diagonal, so the verdict — whatever it is — carries the pre-declared
> qualifier **ON A DAMAGED FLOOR** (the any-direction-damage frame applied
> to a gate-bearing subject) if the floor readout's Wilson 95% lower bound
> is below **0.5**. The floor readout is the **cluster-collapsed per-cell
> survival** (re-defined at this PR's round-4 review, F15, keeping the
> honest item-level n its F11 re-definition introduced): each gated item
> contributes its *fraction* of the 11 off-diagonal deletions survived,
> and the readout is wilson(k, n) with k = ⌊the sum of those fractions⌋
> and n = the gated items (28 / 34 / 32). This keeps the quantity the
> floor is about — the per-cell collateral rate (the 0.57–0.68 damage
> band still fires: at those rates on n = 28 the lower bound reads
> 0.39–0.49) — while refusing both dishonest denominators: the pooled
> rate at n = 308 under-fires (its 11×-inflated n narrows the interval —
> F11), and a survives-all-11 conjunction is decided by the unmeasured
> correlation structure across the 11 deletions rather than by damage
> (per-direction survival 0.882 reads ≈ 0.88 if failures cluster on the
> same items and 0.882¹¹ ≈ 0.25 if independent — F15). A binomial
> interval on a mean of bounded fractions is approximate by
> construction — owned, and acceptable only because the qualifier is
> never dispositive. The pooled per-cell reading is reported beside as
> the permissive comparison. The qualifier scopes the claim and can never
> create or rescue a verdict. The 0.5 floor is a pre-registered constant,
> deliberately **not** fitted to any recorded cell; 0.5B's exclusion from
> gate-bearing rests on the standing pre-declared scale frame, never on
> this qualifier. Every matrix cell ablates the subject's
> identical late-third layer set at λ = 1, k = 1, so the compared arms
> differ **only in which direction is removed** — never in depth, layer
> count, or dose (PR #7 review F2's caveat, retired structurally and stated
> here so it stays owned).

Clause (1) *is* KICKOFF's "diagonal suppression CI-cleanly exceeds
off-diagonal collateral" in directly comparable proportions, by M2's algebra:
suppression under arm X is the naming drop clean − naming_X on the same
items, so suppression_diag − suppression_offdiag = naming_offdiag −
naming_diag — the shared clean arm cancels, leaving the plain two-proportion
comparison the ported ruler already decides.

**Why clauses (2) and the floor qualifier exist (added at this PR's
adversarial review, findings F2 and F1 — both pre-run; both kept at Kyle's
freeze, 2026-07-28).** The pooled off-diagonal arm is 73% cross-category
(274 of 374 cells at 1.5B), while the arm KICKOFF's wording generalizes —
S4b D28's specificity control — was same-category only. Cross-category pairs
are the ones least likely to show collateral, so pooling shifts the
comparator in the gate's favour relative to the control the lineage actually
ran: if collateral is category-structured (the "block structure" named above
as the most interesting finding), the pooled arm dilutes it. Clause (2) is
the undiluted test, and it is powered on its own — within-category pooled n
**96 / 100 / 101** (0.5B / 1.5B / 3B), all ≥ MIN_N. The floor qualifier
covers the failure mode neither ordering clause can see: a matrix whose
off-diagonal is heavily damaged can still pass both orderings CI-cleanly —
the recorded 0.5B tier cells do exactly that (`control_late` 20/28 vs
`primed_late` 0/28 → +0.714 [+0.494, +0.847] through the project's own
ruler).

**What the floor does and does not catch, on the recorded numbers
(corrected at this PR's round-2 review, F1 reopened — the first fix
overclaimed this; floor readout re-defined per F11 and again per F15).**
The qualifier is decided by the Wilson **lower** bound of the
cluster-collapsed per-cell survival, and no recorded artifact can compute
it: each item's recorded control cell samples exactly **one** deletion
direction — and for six of the twelve concepts (October→February,
Mars→Saturn, Jupiter→Mercury, piano→guitar, violin→drum, silver→platinum)
that direction is not even among the item's 11 matrix deletions, so the
recorded cells are indicative proxies, **neither ceiling nor floor** (this
PR's review F16 — an earlier draft claimed a ceiling, which is false for
exactly those six concepts). The measured split on the recorded subset
control cells under D9(b), checked 2026-07-28: items whose control
direction is in-matrix survive **15/18 / 18/18 / 18/18** (0.5B / 1.5B /
3B); items whose control is out-of-matrix survive **5/10 / 12/16 /
12/14** — at both gate-bearing subjects, every recorded control failure
comes from a direction outside the matrix. On 0.5B the single-direction
proxy reads 20/28 → [**0.529**, 0.847], above the floor; whether the full
collapse would clear it is genuinely open until the matrix runs — which is
fine, because 0.5B's exclusion from
gate-bearing remains what it has been since KICKOFF: the standing
pre-declared any-direction-damage frame (risk 2), a scale frame, not a
tripwire. The regime the floor targets is grosser damage of the kind M1's
*full-battery* 0.5B control cell shows under the same oracle —
`control_late` 33/69 → Wilson lower bound **0.36**, well below the floor —
a cell M3's curated subset does not re-run. Two calibration caveats, owned
(follow-up F14): that 0.36 reference is a *same-category* cell, so it is a
lower estimate of what a 73%-cross-category arm would read on the same
subject; and the pooled off-diagonal has never been measured at any scale —
no recorded artifact contains a cross-category ablation — which is the
honest reason the constant is uncalibrated. And the reason M3's subset
reads so much higher than the full battery at 0.5B (0.714 vs 0.478) is
measured, not asserted (follow-up F12, judge-confirmed): S1 membership
conditioned on `control_late` 3/3 **at the gate-bearing subjects** (D7's
hard-switch profile — 0.5B played no part in the rule), and that selection
measurably enriches 0.5B control survival too: S1's items read **12/15
(0.80)** vs **21/54 (0.39)** for the rest of the gated roster under the
same oracle. The floor is therefore a forward-looking drift guard for the
gate-bearing subjects — it fires if 1.5B or 3B ever slides toward that
regime — not the mechanism that excludes 0.5B.

**Descriptive package (never gate-bearing, Wilson CIs).** The matrix itself:
per-pair (A, B) cells are n ≤ 3, always descriptive. Reported beside, all
pre-registered here: the **within-category vs cross-category** split of the
pooled off-diagonal (KICKOFF's named readout — the within-category arm is
gate-bearing via clause (2); the cross-category arm and the full grid stay
descriptive); per-direction **row profiles** (how much does deleting A damage
the other 11 — silver's row is the pre-registered interesting one) and
per-concept **column profiles** (how fragile is B to other deletions);
asymmetry texture (A→B vs B→A); the 18 out-of-subset control cells; mean
concept mass per cell under D13's standing scope (only items whose emitted
bare spelling has a single-token form — `mass_channel_eligible`, carried
per-item from M2's artifacts).

**Degeneracy disposition (M2's D14 wide-oracle guard, re-scoped to the arms
this gate reads).** The dispositive guard stays as D14 froze it: pool the
first tokens of an arm's **non-produced** items only, share against the full
gated n ("at least half this arm's answers are the same *wrong* opening");
the raw all-answers guard recorded beside as texture. Scope: collapse in the
pooled **off-diagonal** arm — the surviving side the gate reads — ⇒
**DEGENERATE**, no MATRIX-SPECIFIC claim; collapse in the pooled
**diagonal** ⇒ **TAG only** (the expected mute signature, exactly
`primed_late`'s standing treatment); `clean` stays off the dispositive list
(it is the gate arm — the D14 F3 correction, carried); collapse inside any
single direction's row or any per-pair cell is **texture**, attached to the
descriptive readout it compromises (those cells are never verdict-bearing).

**Verdict precedence, frozen** in `matrix_verdict()`: NOT A RESULT >
DEGENERATE > UNDERPOWERED > the contrast. Wrong-arm inputs exit INVALID
before any trial; `--dry-run` validates and stops; `--limit` is smoke, never
a result; M3 refuses an M1 artifact that was itself not a result. All M1/M2
patterns carried verbatim.

*(No alternative wording options offered: the gate's substance is
KICKOFF-frozen and the degeneracy/precedence machinery is carried from D14.
The two review-added elements — clause (2) and the floor qualifier, from
this PR's F2 and F1 — were the strikeable parts: each strengthens or scopes
the gate and neither weakens it, and both were kept at Kyle's freeze.)*

### D18 — Run-time instrument bars (the PR #7 F5 + F4 pins)

- **(a) Both bars in the runner's `main()`, pre-trial, plus unit tests
  (recommended).** After the tokenizer loads and before any trial: (1) every
  planned concept tokenizes to ≤ `oracle.SPAN_TOKENS` in **both** its bare
  and its leading-space form — `max(len(tok(w)), len(tok(" " + w))) ≤
  SPAN_TOKENS` — on the subject's tokenizer, else exit INVALID. Widened from
  bare-form-only at freeze (this PR's follow-up F5): the recorded span holds
  the model's *emitted* continuation, normally the space-prefixed form, and
  bare length does not bound space-form length — `opal` is 1 token bare but
  2 space-prefixed on all three tokenizers, the pinned unit-test case. This
  is the D9(b)/D10 soundness premise, now checked where it can drift (a new
  tokenizer revision, a future roster edit). (2) Every planned concept's
  spelling is **pure ASCII** — the `oracle._BOUNDARY` premise — else exit
  INVALID. Unit tests pin the bars' failure modes (`opal`'s space form
  against a fabricated SPAN_TOKENS=1; a fabricated 4-token word; a
  fabricated non-ASCII word). `oracle.py` is untouched.
- **(b) Unit tests only, no run-time bar.** Catches a roster edit at test
  time but not an environment/tokenizer drift at run time — PR #7 F5's point
  was precisely that the premise should hold *at the moment of measurement*.
  Not recommended.
- **(c) Also widen `_BOUNDARY` to `\w` now.** A measurement-rule change with
  zero live cases, silently flipping `_` from boundary to word-character —
  the unforced version of the mistake D9 exists to prevent. Not recommended.

## Deviations table additions (owned)

| Deviation | From | Owned reason |
|---|---|---|
| Full prime × probe matrix (no S4b precedent) | S4b/M1's single same-category control cell | The point of M3 — characterization, not reproduction; the diagonal and the 36 control cells keep the S4b/M1-comparable frame inside the matrix |
| Pooled off-diagonal counts each gated item 11 times | independent-samples assumption | Within-item correlation across directions, owned in the honesty rows; per-direction and per-pair views reported beside |
| M3 runner cut from `m2_depth.py`, not shared | single-runner reuse | Standing convention: each runner cut from its predecessor; `oracle.py` remains the one deliberate shared exception |
| 18 out-of-subset control-direction cells (D16a) | the 12 × 12 matrix frame | Not matrix cells; run solely to complete the recorded 108-cell re-certification surface and reported as texture |

Standing owned rows that carry unchanged: the S2-stratum space-keyed
direction convention (D11 / PR #5 F3), the mass-channel scope (D13 / PR #5 F2), naming-only
gate (K2), lens provenance (K3).

## Expected power (honest math — realized, not projected)

Gating is the deterministic clean arm, already recorded, so under D15(a)
every pooled n is known **now** (a run that disagrees is itself an INVALID
cross-check, not a power surprise):

| Pooled cell | 0.5B | 1.5B | 3B | Clears MIN_N = 20? |
|---|---|---|---|---|
| Diagonal (the binding gate cell) | 28 | 34 | 32 | yes, all |
| Off-diagonal (11 × gated n) | 308 | 374 | 352 | yes, all |
| Within-category off-diagonal (gate clause 2) | 96 | 100 | 101 | yes, all |
| Clause (2) item set, both arms + per-item collapse (≥ 1 sibling) | 24 | 28 | 29 | yes, all |
| Cross-category off-diagonal (texture) | 212 | 274 | 251 | yes, all |

Per-pair cells are n ≤ 3 — always descriptive, never verdict-bearing (D7's
logic, unchanged). Honesty rows, carried and extended: items within a concept
share one direction (clustering); the diagonal and off-diagonal arms are
measured on the same gated items under an independent-samples Newcombe, which
widens the CI and can only cost power; **new for M3, anti-conservative and
owned (corrected at this PR's review, F3)** — the pooled off-diagonal
repeats each gated item 11 times (the within-category arm up to 5), which
makes the gate's Newcombe interval *narrower* than the clustering justifies,
not wider: worked on the recorded 0.5B rates, the inflated-n contrast reads
+0.714 [+0.583, +0.762] where the honest per-item n gives +0.714 [+0.494,
+0.847]. (This brief originally asserted the bias ran toward wider
intervals; that was wrong — the paired-arms widening above is small
precisely because the diagonal arm sits near 0 hits.) The pre-registered
**effective-n sanity check**, reported beside the gate: each contrast
recomputed with the repeated arm collapsed to one binary per gated item,
decided by the same frozen ruler — for clause (1), "survives **all 11**
off-diagonal deletions", n = the gated items (28 / 34 / 32) — note the
collateral-floor qualifier uses the cluster-mean collapse instead (F15),
not this conjunction; for clause
(2), "survives all within-category sibling deletions", n = the gated items
with **at least one within-category subset sibling** — **24 / 28 / 29**
(0.5B / 1.5B / 3B), October's and silver's items excluded by construction,
not by choice (this PR's review F10: with no sibling, the conjunction is
empty and True by fiat — it would have scored silver, the pre-registered
non-specific anti-example, as a structural survivor, in the
anti-conservative direction this very row exists to correct). If a pooled
clause is CI-clean but its per-item collapse is not, the per-item numbers
are the honest ones to quote. MIN_N applies to raw n.

What the recorded evidence predicts, said plainly: M2's re-scored control
cells (30/34 under D9(b) at 1.5B — M1's own first-token scoring of the same
subset reads 21/24; corrected attribution, follow-up F9) and M2's tier
texture predict clauses (1) and (2) pass.
The matrix's genuinely new content is the 126 never-measured ordered pairs —
block structure, row-level non-specificity beyond silver's, and asymmetries
are all findings the single-control design could not have seen, and a
*failed* gate (off-diagonal collateral approaching diagonal suppression)
would be the pre-committed reportable headline against the lineage's
specificity story.

## Wall-clock plan

Per subject: 36 clean + 432 matrix + 18 control-extra = **486 cells**, × 3
forwards each (the 3-token span) ≈ **1,458 forwards — 0.9× an M1 subject run**
(1,620), which itself ran in minutes per subject. All three subjects
comfortably under an hour total on MPS, $0, run backgrounded with untracked
logs. The 108 re-certification cells are graded first (D16). The standard
machinery regardless of decisions: wrong-arm input exits INVALID; `--dry-run`
validates and stops; `--limit` is smoke, never a result; gate wording frozen
as code in `m3_matrix.GATE_WORDING` before any real run.

## What M3 does NOT decide

- The S1 stretch (7B lens fit + matrix-lite) and S2 stretch (lexical vs
  semantic scope) — reached only after M3 closes, each with its own brief.
  S2's brief owes the F4 boundary-class decision if it freezes any non-ASCII
  list (named trigger, above).
- Whether and how the project closes after M3 (write-up, seed-hunt) — not a
  milestone decision.
- M1's and M2's published verdicts and numbers — they stand as pre-committed.
- No oracle change beyond D9's frozen rule: `oracle.py` is byte-shared and
  untouched; D18 pins its premises without altering the rule. Never an LLM
  judge, never free-text parsing (standing guardrail).

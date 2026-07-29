# M4 start-of-stage brief — the vocabulary collateral strip

*Start-of-stage brief per the per-stage rhythm: plain-terms explanation first,
design extraction second, decisions third, code only after Kyle freezes.
Decisions here are D19–D22, continuing `docs/DECISIONS.md` (D15–D18 were M3's).*

*Provenance, stated up front: M4 is **not** in KICKOFF's frozen chain. The v1
chain (M0–M3) closed on 2026-07-28; this stage is the close-out follow-up
HANDOFF listed as option 4, picked by Kyle the same day (session "mute-map post
M3 decisions") over closing immediately and over the S1/S2 stretches — which
were banked as idea #13 in `~/Projects/j-lens-proj-ideas/jlens-followon-backlog.md`.
KICKOFF's scope decisions are not relitigated; this is an addition, owned in the
deviations table. After M4, the plan of record is write-up + `/seed-hunt`.*

## What M4 is, in plain terms

M3's killer figure shows a dark diagonal on a nearly-white grid: deleting any
of the 12 subset concepts' directions mutes that concept and almost nothing
else — *among those 12*. M3's own Honest limits section states the bound
plainly: nothing measured so far shows that deleting France spares the other
48 M1 concepts. The natural over-reading of the figure ("the deletion spares
the vocabulary") is exactly one experiment wider than what was run.

M4 runs that experiment. Keep the 12 characterized directions as the **primes**
(the thing deleted); widen the **probes** (the thing asked about) from the 12
subset concepts to **all 60 M1 concepts** — the full frozen 180-item battery.
Every cell is the M3 recipe unchanged: ablate prime A's direction at the
subject's late third (λ = 1, k = 1), ask item-of-B its naming question, score
with the frozen D9(b) oracle. The strip is 12 × 180 = 2,160 ablated cells per
subject; the genuinely new content is the **non-subset pool** — the 48 concepts'
gated items under each of the 12 deletions: **492 / 852 / 1,008** cells at
0.5B / 1.5B / 3B, of which **486 / 844 / 993** have never been measured by any
milestone. The remainder (6 / 8 / 15) are already recorded in M1 — they are the
non-subset items whose frozen M1 control direction happens to be one of the 12
primes — so those outcomes are fixed before the run and are stated below as
pre-registered ceilings, not predictions.

The strip is also a mostly out-of-sample test of M3's most interesting
descriptive finding. Finding 1 said collateral concentrates on a few fragile
**probes** (silver's column) rather than on damaging **primes**. The 48 new
probe columns are a near-fresh sample — 6 / 8 / 15 of their gate-bearing cells
are M1-recorded, the other 486 / 844 / 993 are new: either near-total sparing
holds and the fragile-probe story stays a curiosity of the 12, or more
silver-like columns exist among the 48 — both outcomes are findings, and a
*failed* gate (a low survival floor across the wider vocabulary) would be the
pre-committed reportable headline against the specificity story's reach.

Because the strip contains, cell-for-cell, almost everything M1 and M3 already
recorded on these conditions, it also carries the standing re-certification a
generation deeper — this time against **two** recorded artifact sets at once
(details in D19).

## Design extraction (verbatim, source-cited)

**The bound M4 closes — M3-BRIEF, Honest limits (frozen with M3's artifacts):**
"One bound worth stating plainly: **the matrix measures collateral among 12
concepts, not across the vocabulary.** M1 established breadth over 60 concepts
with one control each; M3 establishes near-zero collateral over 132 ordered
pairs of 12. Nothing here shows that deleting France spares the other 48 M1
concepts — that is a different (and cheap) experiment the matrix design
deliberately did not run."

**The scope as HANDOFF recorded it (option 4):** "A 12-prime × 60-probe strip
would close that gap for roughly the cost of one M3 subject run." (The honest
cell count is larger than that quote — ~4.3× an M1 subject run, still
minutes-scale and $0; wall-clock section below.)

**The prediction under test — M3-BRIEF, finding 1:** "Collateral concentrates
on *probes*, not on *primes* … at 1.5B all 11 off-diagonal misses land on
`silver` (6), `Canada` (3), `piano` (1) and `violin` (1); at 3B all 9 land on
`silver` (5) and four others once each."

**The machinery carried unchanged:** D9(b) oracle (`oracle.py`, byte-shared),
D16's grade-recorded-cells-first re-certification pattern, D17's wide-oracle
degeneracy guard and verdict precedence, D18's two run-time bars, M2's frozen
late thirds (L17–21 / L19–24 / L26–32), per-item `direction_key` as recorded.
Every strip cell ablates the subject's identical late-third layer set at λ = 1,
k = 1, so cells differ only in which direction is removed and which item is
asked — the M3 property, preserved (PR #7 F2's caveat clause carries).

**Instrument facts the design stands on (computed 2026-07-28, from the
recorded artifacts and the frozen `oracle.py` — no new model runs):**

- **Gated sets are already known, exactly.** Gating is the clean arm under
  D9(b), deterministic and recorded. Full-roster prefix-gated n: **69 / 105 /
  116** (0.5B / 1.5B / 3B) of 180 items. Non-subset gated items — the gate
  arm's n: **41 / 71 / 84**. Non-subset concepts with ≥ 1 gated item: **23 /
  41 / 43** of 48 (zero-gated: 25 / 7 / 5). Those concepts drop out because
  **the model answers something else, or answers correctly in a form D9(b)'s
  opening-word rule refuses** — never because of token geometry: under
  D9(b) the gate is a prefix on the 3-token span, so it is insensitive to
  token count up to 3, and four of the seven 1.5B zero-gated concepts are
  single-token bare. The recorded clean spans say it plainly — `saturn-1/2/3
  → 'Jupiter'`, `neptune-1 → 'Jupiter'`, `bronze-2 → 'Aluminum'`,
  `monday-1/2/3 → 'Friday'`, `thursday-1/3 → 'Friday'`, `moth-1 → 'Wasp'`.
  Two further mechanisms sit beside that one and are named rather than folded
  in: `ant-1/2 → 'Ants'` is a **morphology** miss (a plural closes no
  boundary), and D9(b)'s opening-word rule refuses **correct answers behind a
  modifier** — `duck-3 → 'Peking duck'` and `beetle-3 → 'Insect Beetle'` at 3B,
  `eagle-1 → 'American eagle'`, `guitar-2 → 'Electric guitar'` and
  `bear-3 → 'Polar bear'` at 0.5B. All three mechanisms point the same way:
  the gate arm is **the concepts this subject already names, in the form the
  oracle accepts** — a *competence selection*, and confidently-named concepts
  are plausibly the robust ones, which biases the measured sparing floor
  **upward**. That is the same enrichment mechanism as F12's
  selection-enrichment finding, now on the probe side; it is why the claim is
  sparing across the *measurable* vocabulary, said exactly that way.
- **Five probe clues mention a prime's spelling — a confound M3's design never
  had.** M1's leak guard (D5) bars a clue from leaking its *own* concept or
  control; M3 verified no cross-mentions *within the 12*. Widening probes to
  180 items surfaces five (prime, item) pairs, scanned with **D5's own rule** —
  no word of the clue may *start with* the string, case-insensitive, plus that
  string's `forbidden_forms` entries — not the narrower whole-word match:
  **October→september-2, silver→flute-1, China→jade-1, October→opal-2**, and
  **Egypt→beetle-2** ("Ancient **Egyptians** carved amulets of the scarab, one
  kind of this insect"), which a whole-word scan misses because the clue
  inflects the prime. In those cells a miss cannot distinguish "collateral
  damage to naming machinery" from "the clue's own text lost a word it
  references." The first four items gate at both gate-bearing subjects (only
  jade-1 gates at 0.5B), so those cells are live; `beetle-2` is **ungated on
  all three subjects** (clean span 'Scarab' / 'scarab'), so it contributes no
  gate-bearing cell today and is listed so a future re-gate cannot silently
  miss it. D21 decides their treatment.
- **D9(b)'s owned span-truncation residual re-enters a gate-bearing arm for
  the first time since M1.** `oracle.py`'s frozen wording owns a residual: for
  the three concepts whose bare spelling *fills* the 3-token span — beetle,
  butterfly, trumpet — the closing boundary is unobservable, so a longer word
  sharing those tokens would score as a hit ("Beetlejuice" truncates to
  exactly "Beetle"). The wording's closing scope sentence, "**None of the
  three concepts is in M2's subset**," is precisely what made the residual
  harmless for M2 and M3: those concepts were never scored. M4 widens the
  probe side to all 60, so their items re-enter a **gate-bearing** pool.
  The residual condition is exact and narrower than "a 3-token word": the
  recorded span, after stripping leading whitespace, **equals the concept's
  spelling with nothing following it**, compared case-insensitively as
  `oracle.says_concept_prefix` compares, so no boundary character is observed.
  ("Fills the 3-token span" would not distinguish anything — every recorded
  `greedy_3` is exactly 3 tokens by construction; and a case-*exact*
  comparison would select nothing, since the spans are capitalised and the
  roster spellings are not.) On that reading the gate-arm residual cells are
  **0 / 2 / 2** at 0.5B / 1.5B / 3B — 1.5B `beetle-1` ('Beetle') and
  `butterfly-1` ('Butterfly') of 71; 3B `trumpet-3` ('Trumpet') and
  `butterfly-1` ('Butterfly') of 84; none gated at 0.5B. These are the
  gate-arm members of the same residual set `oracle.py`'s frozen docstring
  names — the docstring counts **six recorded M1 cells** ("beetle-1,
  butterfly-1 ×2 arms, trumpet-3"), enumerating across arms (`butterfly-1`
  in both `clean` and `control_late`), where the four above are clean-arm
  cells on the two gate-bearing subjects. The other trumpet cells are *not*
  residual: `trumpet-1` at 1.5B and `trumpet-1` / `trumpet-2` at 3B record
  `'Trumpet<|im_end|>'`, and `<|im_end|>` closes a word under
  `oracle._BOUNDARY` — capitalisation is why, since generated `Trumpet` is two
  tokens (`['Trump','et']`) where bare `trumpet` is three, leaving room for the
  terminator. D22's span bar cannot catch the residual: it passes at exactly
  ≤ 3 tokens, which *is* the residual condition. The bias runs **toward** the
  gate — an unobservably-terminated span scores a hit, inflating survival —
  and at 1.5B the pass/fail margin is one item (44/71 passes, 43/71 fails), so
  even two such items exceed the margin. `oracle.py` stays untouched (editing
  it would force re-runs of three milestones); the residual is carried by
  disclosure plus the pre-registered residual-conservative recomputation in
  D20.
- **The D18 bars pass for the whole roster, checked in advance.** All 60
  concepts tokenize to ≤ `oracle.SPAN_TOKENS` = 3 in both bare and
  leading-space form on all three Qwen2.5 tokenizers (verified 2026-07-28),
  and all 60 spellings are pure ASCII. The bars still run at run time per
  D18's rationale — the check above is design due-diligence, not a substitute.
- **What the recorded evidence already fixes — and what it predicts.**
  Thirteen concepts' frozen M1 controls are subset members, so their recorded
  `control_late` cells are strip cells. The non-subset portion is a
  single-direction, *same-category* proxy for the new pool — the least
  favorable cell type, since M3 found what collateral exists sits within
  category at small scale: it reads **6/8** at 1.5B and **13/15** at 3B.
  Being strip cells, these are **in-sample**, not a forecast: their outcomes
  are already determined, so the misses among them **cap the gate arm before a
  single new forward pass** — pre-registered ceilings of **35/41, 69/71 and
  82/84** at 0.5B / 1.5B / 3B (0.5B: all 6 proxy cells miss; 1.5B: `july-3`
  and `venus-3` miss; 3B: `guitar-2` and `neptune-1` miss). At 1.5B the bar
  needs 44 of 71, so the ceiling leaves real room; at 3B likewise. Where the
  proxy is genuinely predictive is the *rest* of the pool, which is mostly
  cross-category — so a high floor is the prediction at the gate-bearing
  subjects.
- **The 0.5B prediction, read in M4's own statistic.** The strongest and most
  directly comparable evidence is not the 6-cell proxy: it is M3's recorded
  subset, recomputed under **M4's gate statistic**. M3's per-item
  survives-all-11 off-diagonal reads **19/28 = 0.679 at 0.5B, Wilson lower
  bound 0.4934** — *below 0.5*, i.e. **M3's own 0.5B subset would already fail
  M4's bar**. The same field passes at both gate-bearing subjects (1.5B 29/34,
  lower 0.6987; 3B 27/32, lower 0.6825). So there is no "tension" between M3's
  clean 0.5B floor and a possible M4 failure to resolve — M3's 0.5B floor was
  clean only under the *cluster-mean per-cell* statistic, and switching to the
  conjunction flips it. That is also the sharpest illustration of why the 0.5
  constant carries no meaning across statistics (D20). The 0.5B strip may well
  fail its floor — off-gate, under the standing any-direction-damage frame,
  and consistent in advance with M3's own numbers, M1's full-battery 0.5B
  control cell (33/69), the 0/6 proxy, and F12's selection-enrichment finding
  (the subset-12's 0.5B robustness came partly from S1's selection rule).

## Dispositions for the two inherited obligations (explicit, per HANDOFF)

**(1) The `oracle._BOUNDARY` boundary-class decision (D18's named trigger).**
Not owed: the trigger is a stage freezing a **non-ASCII** list, and M4 adds no
vocabulary — every probe and every prime comes from M1's frozen 60, all
pure-ASCII spellings. The premise stays pinned, not assumed: D18's ASCII bar
runs in the M4 runner's pre-trial validation, unchanged. `oracle.py` is
untouched (it would become byte-shared by a fourth consumer — deviations
table). The trigger continues to name the banked scope stretch (idea #13), not
this stage.

**(2) The conjunction-degeneracy rule (PR #9 F1's carry-forward).** The rule:
any stage whose gate is a conjunction must put every surviving-side comparison
arm on the dispositive degeneracy list and enumerate them in its frozen
wording. Every gate option in D20 is deliberately **single-clause**, so the
dispositive list has exactly one surviving arm — the pooled non-subset
off-target cell — and D20's wording names it explicitly. Stated affirmatively
so the obligation reads as discharged by design, not forgotten: if a later
amendment ever makes M4's gate a conjunction, every surviving arm goes on the
list before the wording freezes.

## Decisions to freeze (Kyle picks; recommendations flagged)

*Frozen (Kyle, 2026-07-29): **D19 (a)** the full 12 × 180 strip plus a full
clean re-run (2,340 cells/subject) with the embedded 255-cell M1 and 468-cell
M3 re-certifications graded first; **D20 (a)** the single-clause
survives-all-12 level gate as written, with the verdict-label choice resolved
per review F8 — the label stays `VOCAB-SPARING` and the **realized survival
proportion rides inside the verdict string**, the M3 `ON A DAMAGED FLOOR`
pattern applied to a level bar; **D21 (a)** all five cross-mention pairs kept
in the gate-bearing pool with named per-cell reporting; **D22 (a)** both
run-time instrument bars over all 60 scored words plus the 12 direction words.
Full `DECISIONS.md` entries (D19–D22) land with the M4 code PR, per the
M0/M1/M2/M3 pattern. Amended pre-freeze at PR #10's adversarial review, across
three rounds: F1–F4 (should-fix) fixed and verified; F11–F12 (should-fix,
defects of the F2 fix) fixed and verified; F16 (should-fix, a defect of the
F11 fix — a case-exact selector that would have silently matched zero cells)
fixed with F15/F17/F18 at `edb5387`; and all eight deferred nice-to-haves
(F5–F7, F9, F10, F13–F15) pulled in at the freeze on Kyle's call ("pull in all
8"), because F5/F7/F9/F13's text byte-freezes into code once these decisions
are signed. Round 4 was authorized by Kyle beyond the three-dispatch cap to
verify the `edb5387` fixes and this freeze commit.*

*Amended post-freeze, pre-run, at round 4 (F20 + F21) — the M3 precedent for a
review-driven amendment before any cell is run, **ratified by Kyle 2026-07-29**
("I ratify the F20 amendment"): the verdict string as first frozen carried
only the **as-scored** proportion, so the two pre-registered reads that can flip
which number is honest (residual-conservative fail-in-place; concept-level
collapse) stayed in prose — reproducing the exact failure F8 was resolved to
prevent. D20's wording now carries the pre-declared **AS-SCORED ONLY**
qualifier, attached conditionally by the runner whenever a conservative read's
Wilson lower bound falls below 0.5 while the as-scored read's does not, and
names a failing label that the single pass-label template had left unstated.
The gate, its 0.5 bar, its arm and its precondition are unchanged — this scopes
the claim and, per D17's carried rule, can never create or rescue one.*

***Amendment 2, post-freeze, pre-run, at rounds 5–6 (F22, F24–F27) —***
***ratified by Kyle 2026-07-29*** *("I agree with what you recommend"), on the
recommendation that named all four changes below. A second material change to
the same frozen
`GATE_WORDING` block, recorded separately rather than folded into Amendment 1,
because Kyle's ratification quote covers Amendment 1 only. What changed:* **(i)
the failing label** *is now the lineage's pre-committed null* `not shown`
*rather than the assertive* `NOT VOCAB-SPARING` *Amendment 1 introduced —
failing a Wilson* lower *bound cannot establish the contrary (at 1.5B, k = 40
has a point estimate of 0.563* above *the bar with a straddling interval), and
all three predecessor runners emit* `not shown`*;* **(ii) 0.5B is scoped inside
the wording** *— the gate verdict is the AND over the two gate-bearing subjects
and 0.5B's readout is never a gate claim, where Amendment 1 had pre-committed
the string "per subject" while the same block declares 0.5B never gate-bearing;*
**(iii) the qualifier's attachment is restricted** *to a claim-level verdict,
never to* `NOT A RESULT` / `DEGENERATE` / `UNDERPOWERED` *— verbatim, Amendment
1 attached it to all of them, contradicting the D17 rule it cites (the fix
copies* `m3_matrix.py`*'s own docstring rule); and* **(iv) both string templates
are stated explicitly** *with a fixed read order, where Amendment 1 gave the
qualifier an example but no template. The gate, its 0.5 bar, its arm and its
re-certification precondition remain unchanged — verified byte-for-byte against
`90b994c`.*

### D19 — Primes × probes: the strip frame (decide first)

- **(a) 12 subset primes × all 180 M1 items, plus a full clean re-run
  (recommended).** Per subject: `clean` (180 items) + 12 × 180 = 2,160 ablated
  cells = **2,340 cells**. *Why:*
  - **The new claim gets its cells** — every gated non-subset item under every
    characterized direction (492 / 852 / 1,008 cells).
  - **The re-certification surface is maximal, and two generations deep.** The
    strip contains **255** cells per subject recorded in M1's artifacts
    (`clean` 180, the 12 subset concepts' `primed_late` 36, and the 39
    `control_late` cells whose control direction is a subset member) **and
    468** cells recorded in M3's artifacts (the 36 subset `clean` cells + all
    432 matrix cells — everything M3 ran except its 18 out-of-subset
    control-extras, whose directions are not strip primes). Both comparisons
    are on raw recorded strings (`greedy`, `greedy_3`; `concept_mass` as
    texture), graded first, INVALID on mismatch on the certified stack — the
    D16 pattern applied against two artifact sets at once.
  - **Ungated items ride along as texture** (the standing convention — the
    gate reads only gated cells, but every cell is recorded).
- **(b) 12 primes × the 144 non-subset items only.** Saves ~20% of the run and
  destroys the M3-overlap re-certification (no subset cells, no diagonal) plus
  the in-strip recorded proxies. The one check that has caught nothing yet
  *because it runs every time* — broken for one saved coffee break. Not
  recommended.
- **(c) The full 60 × 180 matrix.** Answers a different, bigger question ("is
  *every* direction safe to delete?") at ~4.7× the cost, with 48 primes whose
  collateral behaviour no milestone has characterized and no pre-registered
  expectation exists for. That is a future stage's question (it shares rails
  with banked idea #13), not this close-out's. Not recommended.

### D20 — The pre-committed wording package (gate, degeneracy, precedence)

**Gate options (the substance Kyle picks; wording frozen as code in
`m4_strip.GATE_WORDING` before any run, written verbatim into every results
JSON):**

- **(a) A survives-everything level gate on the new pool (recommended).**

  > **VOCAB-SPARING** iff, per subject: among the gated **non-subset** items
  > (concepts outside the 12-concept matrix roster), the proportion that
  > **survives all 12** subset-direction deletions — D9(b) naming success in
  > every one of the item's 12 off-target cells — has its Wilson 95% lower
  > bound at or above **0.5**. This 0.5 is a bar on the **12-fold
  > conjunction**, not on per-cell survival, and is **not** M3's per-cell
  > floor: under independence it corresponds to a per-cell survival of
  > 0.5^(1/12) ≈ **0.944**, and its stringency depends on the deletion count
  > (12) as much as on the sparing rate. The bar is read **only when the 468
  > M3-recorded and 255 M1-recorded cells in the strip reproduce their recorded
  > outcomes bit-for-bit**; any mismatch is INVALID and there is no verdict.
  > The M4 verdict is the AND over 1.5B and 3B; 0.5B runs and is reported under
  > its standing any-direction-damage frame, never gate-bearing. Gate-arm
  > n < MIN_N = 20 ⇒ pre-declared UNDERPOWERED and no claim (realized n =
  > 41 / 71 / 84 from the recorded gated sets). **Verdict string,
  > pre-committed:** the label alone over-reads — clearing a floor bar is
  > compatible with a large minority of measurable items damaged — so the
  > verdict, whichever way it goes, carries its **realized survival proportion
  > in the same string**: `VOCAB-SPARING` when the bar is cleared and the
  > lineage's pre-committed null **`not shown`** when it is not — never an
  > assertive negative, because failing a Wilson *lower* bound does not
  > establish the contrary (`m1_battery.py`, `m2_depth.py`, `m3_matrix.py` all
  > emit `not shown`). The gate verdict is the AND over the two gate-bearing
  > subjects; 0.5B's readout is reported in the same shape under its standing
  > any-direction-damage frame and is **not** a gate verdict, so a low 0.5B
  > reading is never a `not shown` gate claim.
  > **Conservative-read qualifier, pre-declared:** two pre-registered reads can
  > fall below the bar when the as-scored read clears it — the
  > residual-conservative fail-in-place read and the concept-level collapse —
  > and this brief pre-commits that where they diverge, *their* numbers are the
  > honest ones. So a **claim-level** verdict additionally carries the qualifier
  > **AS-SCORED ONLY**, naming each such read and its number, whenever any
  > pre-registered conservative read's Wilson 95% lower bound is below **0.5**
  > while the as-scored read's is not. The qualifier **scopes a claim and can
  > never create or rescue one** (D17's rule, carried), so it attaches to a
  > bar-level verdict only and never to `NOT A RESULT`, `DEGENERATE` or
  > `UNDERPOWERED` — precedence has already withheld the claim there, leaving
  > it nothing to scope.
  > **The two templates, stated once and implemented verbatim** — base:
  > `<label> (k/n survive all 12 = <rate>; Wilson 95% lower <lo>)`; qualifier,
  > appended to the base string when it fires:
  > ` — AS-SCORED ONLY (<read> k/n = <rate>, lower <lo>[; <read> …])`, with the
  > reads listed in the fixed order *residual-conservative, concept-level* when
  > both fire. Worked: `VOCAB-SPARING (44/71 survive all 12 = 0.620; Wilson 95%
  > lower 0.503) — AS-SCORED ONLY (residual-conservative 42/71 = 0.592, lower
  > 0.475)`.

  *Why this shape.* The strip's question is a **level** question — "is the
  floor high?" — not an ordering question; M3 already settled the ordering.
  The per-item survives-all-12 outcome is a true binary, so the Wilson
  interval is exact for it — this deliberately does **not** promote M3's
  cluster-mean floor readout to gate-bearing, because D17 froze that
  approximation as "acceptable only because the qualifier is never
  dispositive," and M4 keeps *that* rationale intact for the approximation
  (the cluster-mean floor is reported beside, reference line 0.5, never
  dispositive — the M3-comparable view). What does **not** carry is the
  constant itself; see immediately below.

  *The 0.5 constant is new, and owned as new — not carried from M3.* M3's 0.5
  was a floor on cluster-collapsed **per-cell** survival; M4's is a bar on a
  **12-fold conjunction**. The same digits mean opposite things across those
  two statistics: under independence a per-cell 0.5 corresponds to a
  conjunction of 0.5^12 ≈ 0.0002, and a conjunction of 0.5 corresponds to a
  per-cell 0.5^(1/12) ≈ 0.944. Two consequences, stated rather than inherited.
  **(i) Status changed.** M3's constant was itself *uncalibrated* — M3-BRIEF's
  F14 record: "the pooled off-diagonal has never been measured at any scale …
  which is the honest reason the constant is uncalibrated" — and D17 tolerated
  that only because the qualifier it scoped "can never create or rescue" a
  claim. M4 makes a constant of the same value the **single dispositive gate**,
  so D17's tolerance does not transfer either. **(ii) The deletion count is
  half the bar.** Stringency is set as much by *how many* deletions each item
  must survive (12) as by the sparing rate: at a per-cell rate of 0.971 (M3's
  recorded 1.5B off-diagonal) the conjunction reads ≈ 0.70 and clears the bar;
  at 0.94 it reads ≈ 0.48 and fails. M4's 0.5 is therefore a **new,
  deliberately lenient, uncalibrated constant** — pre-registered here before
  any new cell is run, and fitted to no recorded cell — and its per-cell
  equivalence is written into `GATE_WORDING` itself so no write-up can quote it
  as M3's floor. It is a floor bar, not an effect-size claim; the descriptive
  numbers carry the actual size.

  *Why the re-certification clause is inside the wording.* Every prior stage's
  gate compared an intervened arm against another **measured** arm, so a dead
  intervention could never pass one. M4's bar is single-clause and reads only
  the off-target survival rate — so read in isolation, an ablation that did
  nothing at all would score ~100% survival and print VOCAB-SPARING. In
  practice the strip's re-run of M3's 432 matrix cells and M1's 36
  `primed_late` cells catches exactly that, and any mismatch exits INVALID —
  but that guarantee lived in D19's design and the runner's exit code, not in
  the sentence a write-up quotes. Putting it in `GATE_WORDING` means the
  sentence cannot be quoted out of its own precondition.

  *Why the realized proportion rides in the verdict string.* `VOCAB-SPARING`
  is the strongest possible phrasing of exactly the over-reading M4 exists to
  correct, and the bar it names permits real damage: at the 1.5B pass point
  (44/71) **27 of 71** gated non-subset items — 38% — are damaged by at least
  one of the 12 deletions, and at the bar's nominal 0.5 it would be half. The
  prose owns that, but prose is not what gets quoted; the label is, and the
  label is frozen into every results JSON. Rather than rename the verdict away
  from the lineage's `M<n>-<PROPERTY>` shape, M4 carries the number **inside
  the verdict string** — the same move M3 made when it attached `ON A DAMAGED
  FLOOR` to the verdict rather than leaving the damaged floor in the prose.
  The number a write-up quotes then travels with the label it quotes.

  *And why the qualifier had to come with it (round-4 review, F20).* The first
  version of this clause carried only the **as-scored** proportion, which
  reproduced the very failure the F8 resolution names: the two reads that can
  *flip* which number is honest — the residual-conservative fail-in-place read
  and the concept-level collapse — stayed in prose, each closed with "the …
  numbers are the honest ones to quote". The window is live, not hypothetical:
  at 1.5B the bar needs k ≥ 44 (`wilson(44, 71)` lower 0.50342), and
  fail-in-place removes the 2 residual items, so both of the as-scored values
  that clear the bar by the narrowest margins would have printed a pass over a
  conservative failure — k = 44 → `VOCAB-SPARING … lower 0.503` against a
  fail-in-place 42/71 (lower **0.475**), and k = 45 → `… lower 0.518` against
  43/71 (lower **0.489**). Either way the brief's own pre-commitment named the
  *conservative* number as the honest one and the frozen string carried the
  other. M3's precedent is a **conditional** qualifier attached by the runner,
  not a fixed sentence; M4 had borrowed the shape and dropped the mechanism.
  `AS-SCORED ONLY` restores it.

  *Trade-off, owned:* survives-all-12 is the strictest sparing statistic; a
  single fragile cell fails an item, and the correlation structure across the
  12 deletions (unmeasured until this run) decides how harsh that is. That
  bias direction runs **against** the claim, the one direction this project
  accepts.

- **(b) An M3-clause-(1)-style ordering gate extended to the strip** (pooled
  off-target minus subset diagonal, Newcombe CI excludes 0). Maximally
  comparable to M3 — and it passes almost by inheritance, since the diagonal
  is 0-to-3-hits at every subject and the off-target pool would have to
  collapse to near-zero to close a Newcombe gap that large. A gate the
  recorded evidence has effectively already decided does not gate the new
  claim. Not recommended (reported beside as descriptive continuity either
  way).

- **(c) The conjunction of (a) AND (b).** Strongest-sounding wording; adds
  nothing (b) doesn't already concede, and re-opens the conjunction
  obligation for no inferential gain. Not recommended.

**Degeneracy disposition (D14/D17's wide-oracle guard, re-scoped to M4's
arms).** The dispositive guard is unchanged in mechanism: pool the first
tokens of an arm's **non-produced** cells only, share against the arm's full
cell count, threshold COLLAPSE_SHARE = 0.5. Scope, enumerated: collapse in the
pooled **non-subset off-target** arm — the single surviving arm the gate
reads — ⇒ **DEGENERATE**, no VOCAB-SPARING claim; collapse in the subset
**diagonal** ⇒ **TAG only** (the expected mute signature, carried); `clean`
stays off the dispositive list (the D14 F3 correction, carried); collapse
inside any single prime's row, any probe concept's column, or any per-pair
cell is **texture**, attached to the readout it compromises.

**The effective-n sanity check, pre-registered and never dispositive.** Items
cluster three-per-concept on the probe side (they share the concept whose
fragility is being measured), so beside the item-level gate the same statistic
is recomputed collapsed to one binary per **concept** — "every gated item of
this concept survives all 12 deletions" — over the non-subset concepts with
≥ 1 gated item (n = **23 / 41 / 43**, all ≥ MIN_N). If the item-level gate is
clean and the concept-level collapse is not, the concept-level numbers are the
honest ones to quote.

**The residual-conservative read, pre-registered and never dispositive.**
Beside the gate as scored, the same gate statistic is recomputed with every
**residual cell** re-scored as a **miss** — the maximally conservative reading
of the boundary D9(b) cannot observe. A residual cell is one whose recorded
span, after stripping leading whitespace, **equals the scored concept's
spelling with nothing following it — compared case-insensitively, exactly as
`oracle.says_concept_prefix` compares (`re.IGNORECASE`)**, so that no boundary
character is observed. The case rule is stated because it decides the set, not
as a detail: the recorded spans are `'Beetle'`, `'Butterfly'`, `'Trumpet'`
while the roster spellings are lowercase, so a case-*exact* comparison would
select **zero** cells and silently turn this mitigation into a no-op. That is
the selector, stated once here and implemented verbatim: it is *not* "the span
fills the 3-token window", which every recorded cell does. In the
recorded clean arm the residual cells are the 0 / 2 / 2 gate-arm items named in
the instrument facts; in the ablated cells the set is whatever the run records,
computed from the same recorded spans by the same selector.

**Denominator, pre-registered: fail in place.** The gate arm stays at its
as-scored n — **41 / 71 / 84**, the knowable-now cross-check the power table
freezes — and a residual-affected item scores as a **failure** within that arm.
The alternative reading (re-score the clean cell too, so the item un-gates and
the arm shrinks) is named and **rejected**: it is the less conservative of the
two at the bar — with the same numerator, `wilson(43, 71)` reads 0.489 and
fails while `wilson(43, 69)` reads 0.505 and passes — and it would break the
power table's pre-registered n. Fail-in-place keeps the read strictly one-way:
it can only lower the floor, never rescue it. Both the as-scored and the
conservative numbers are reported, and following the same honesty pattern as
the concept-level collapse: **if the gate passes and the residual-conservative
read does not, the conservative numbers are the honest ones to quote.**
`oracle.py` is not touched.

**Descriptive package, never gate-bearing, all pre-registered here:** the
cluster-mean per-cell floor on the new pool (M3's F15 readout, reference line
0.5, the M3-comparable view); the ordering contrast from option (b); per-prime
**row profiles** (does any of the 12 damage the wider vocabulary?) and
per-probe **column profiles** over all 60 concepts (finding 1's mostly
out-of-sample test — are there silver-like columns among the 48?); the
within- vs cross-category split of the new pool; the five confound pairs
(D21); mean concept mass per cell under D13's standing scope; the 0.5B floor
under its standing frame (M3's own subset already fails this bar in-statistic,
so a 0.5B failure is a finding, not a failure of the run).

**Verdict precedence, frozen** in `strip_verdict()` (`m4_verdict.py`): NOT A
RESULT > DEGENERATE > UNDERPOWERED > the level bar (`VOCAB-SPARING` or the
pre-committed null `not shown`, each carrying its realized proportion, and
`AS-SCORED ONLY` appended only at this level — the three higher outcomes
withhold the claim, leaving the qualifier nothing to scope). Wrong-arm
inputs exit INVALID before the checkpoint loads (the D18-companion shape,
carried from `m3_matrix.py`); `--dry-run` validates and stops; `--limit` is
smoke, never a result; M4 refuses M1 or M3 artifacts that were themselves
not results.

### D21 — The five cross-mention cells

*The list freezes here, scanned with D5's own prefix + `forbidden_forms` rule:
**October→september-2, silver→flute-1, China→jade-1, October→opal-2,
Egypt→beetle-2**. Four are gated today (one at 0.5B); `beetle-2` is ungated on
all three subjects, so it carries no gate-bearing cell now but is listed so a
future re-gate cannot silently acquire one.*

- **(a) Keep them in the gate-bearing pool; report them as a named confound
  row (recommended).** The cells stay in every pooled arm and in their items'
  survives-all-12 conjunctions, and the results section reports each cell's
  outcome individually under its named confound. *Why:* a confounded miss can
  only **lower** the floor — the bias runs against the gate, the one direction
  this project ships owned. Excluding them would delete only cells that could
  hurt the claim, which is the anti-conservative move the lineage never makes.
  Four cells of 852 (1.5B) cannot carry a verdict either way; what they can do
  is mislead a *reader* of the column profiles, and the named row prevents
  that.
- **(b) Pre-registered exclusion from gate-bearing pools, reported as
  texture.** Cleaner causal story per cell, but it is evidence-removal in the
  gate's favour — rejected on the standing bias rule. Not recommended.
- **(c) Drop the five items entirely.** Loses their clean cells and their
  unconfounded prime cells for no reason. Not recommended.

### D22 — Run-time instrument bars (D18 carried, widened to the full roster)

- **(a) Both D18 bars in `m4_strip.py`'s pre-trial validation, now over every
  scored word — all 60 — plus the 12 direction words, with unit tests
  (recommended).** Span bar: `max(len(tok(w)), len(tok(" " + w))) ≤
  SPAN_TOKENS` on the subject's own tokenizer, else INVALID. ASCII bar: every
  spelling pure ASCII, else INVALID. Verified in advance for all 60 words on
  all three tokenizers (2026-07-28, instrument facts above) — the run-time bar
  still runs, because D18's point was that the premise must hold *at the
  moment of measurement*. `oracle.py` untouched.
- **(b) Bars over the 12 primes only (M3's literal scope).** The soundness
  premise attaches to every **scored** word, and M4 scores 60 — a bar that
  checks 12 of them pins a fifth of the premise. Not recommended.
- **(c) Widen `_BOUNDARY` now.** Still zero live cases; still the unforced
  version of the mistake D9 exists to prevent. Not recommended (carried
  rejection).

## Deviations table additions (owned)

| Deviation | From | Owned reason |
|---|---|---|
| M4 exists at all (post-KICKOFF stage) | KICKOFF's frozen M0–M3 chain | Kyle-picked close-out (2026-07-28) that closes M3's stated bound before write-up; KICKOFF's scope decisions unrelitigated; S1/S2 declined and banked (idea #13) |
| Level-bar gate (Wilson lower bound vs a constant) | the lineage's Newcombe ordering gates | The ordering is M3's settled result; the strip's question is a level question |
| A **new, uncalibrated, sole-dispositive** 0.5 constant | D17's 0.5, which was per-cell and never dispositive | The statistic changed (12-fold conjunction, ≈ 0.944 per-cell under independence) and the status changed (qualifier → gate), so no provenance transfers; owned as deliberately lenient, pre-registered before any new cell, fitted to none, with the per-cell equivalence frozen into `GATE_WORDING` |
| Five cross-mention (prime, item) pairs kept in gate-bearing pools | M3's verified no-cross-mention property | M1's leak guard only bars own-concept/control leaks; scanned with D5's own prefix + `forbidden_forms` rule (a whole-word scan misses `Egypt→beetle-2`, which the clue inflects); the confound biases against the gate; named per-cell reporting (D21a) |
| `oracle.py` byte-shared by a fourth consumer (`m4_strip.py`) | cut-from-predecessor rule | Same D9 rationale as the first three consumers: the rule's purpose is byte-identity; pinned by the existing shared-oracle test pattern |
| D9(b)'s owned span-truncation residual sits in a gate-bearing arm | `oracle.py`'s scope sentence, "None of the three concepts is in M2's subset" | M4 scores all 60 probes, so beetle / butterfly / trumpet are gated again for the first time since M1 (0 / 2 / 2 gate-arm cells whose span equals the spelling with no boundary observed — `oracle.py`'s own named set); the bias runs *toward* the gate, so it is disclosed per subject and carried by the pre-registered residual-conservative recomputation, fail-in-place (D20), never by editing `oracle.py` |
| Probe-side reach is still the D9(b)-visible roster | "the vocabulary" | 25 / 7 / 5 concepts gate zero items — a **competence selection** (the model answers something else, answers correctly behind a modifier the opening-word rule refuses, or misses on morphology; the gate is token-count-insensitive up to 3), not tokenizer geometry; that selection plausibly enriches for robust concepts and biases the floor **upward** (F12's enrichment mechanism, probe side); the claim is sparing across the *measurable* vocabulary, said exactly that way |

Standing owned rows carry unchanged: naming-only gate (K2), lens provenance
(K3), S2-stratum space-keyed directions (D11), mass-channel scope (D13),
identical-layer-set arms (D17's carried clause).

## Expected power (honest math — realized, not projected)

Gating is the deterministic clean arm, already recorded, so every n is known
now (a run that disagrees is an INVALID cross-check, not a power surprise):

| Cell | 0.5B | 1.5B | 3B | Clears MIN_N = 20? |
|---|---|---|---|---|
| Gated items, full roster | 69 | 105 | 116 | yes |
| **Gate arm: gated non-subset items (per-item survives-all-12)** | **41** | **71** | **84** | yes, all |
| Off-target cells in the new pool (non-subset gated × 12) | 492 | 852 | 1,008 | yes (texture pools) |
| — of them never measured by any milestone | 486 | 844 | 993 | texture |
| — of them already recorded in M1 (outcome fixed pre-run) | 6 | 8 | 15 | ceilings 35/41, 69/71, 82/84 |
| Concept-level collapse (non-subset concepts ≥ 1 gated item) | 23 | 41 | 43 | yes, all |
| Subset diagonal (recorded; M3's cells re-run) | 28 | 34 | 32 | yes |
| Cross-mention confound cells in the pool (D21a; 5 pairs, 4 currently gated) | 1 | 4 | 4 | named texture |
| D9(b) residual items in the gate arm (clean arm; span = spelling, no boundary) | 0 | 2 | 2 | named texture |

Honesty rows, carried and extended: probe-side clustering (3 items share a
concept) is handled by the pre-registered concept-level collapse, never by the
gate silently; prime-side clustering (every item faces the same 12 directions)
is the unmeasured correlation structure the survives-all-12 statistic is
conservative under; the pooled 852-cell view repeats each item 12 times and is
therefore texture, never the gate (M3's F11 lesson applied in advance). The
worked bar: at 1.5B the gate passes iff ≥ **44 of 71** items survive all 12
deletions (wilson(44, 71) lower bound ≈ 0.503, computed with the project's own
frozen ruler; 43/71 reads 0.489 and fails). Between 44 and that arm's
pre-registered ceiling of **69 of 71** — 8 of the 852 cells are M1-recorded and
two of them (`july-3`, `venus-3`) already miss — there is real room, and M3's
per-item collapse texture (29/34 survived all 11 at 1.5B) points into it; the
ceiling is a fact about the arm, not evidence for the gate. At 0.5B the same
recorded cells put the ceiling at **35 of 41** (all 6 proxy cells miss) —
`wilson(35, 41)` lower bound 0.716, comfortably above the bar, so that ceiling
is *not* a reason to expect failure. The reasons to expect failure at 0.5B are
the ones stated in the instrument facts: M3's own 0.5B subset already fails
this bar in-statistic (19/28, lower 0.4934), the 0/6 proxy rate, and M1's 33/69
0.5B control cell. A 0.5B failure would be the first measured divergence
between the subset's 0.5B robustness and the wider roster's.

## Wall-clock plan

Per subject under D19(a): 180 clean + 2,160 ablated = **2,340 cells × 3
forwards ≈ 7,020 forwards — ~4.3× an M1 subject run** (1,620), which ran in
minutes. All three subjects comfortably within an afternoon on MPS, $0,
backgrounded with untracked logs. The 255 M1-recorded and 468 M3-recorded
cells are graded first (D19a); wrong-arm inputs exit INVALID before the
checkpoint loads; `--dry-run` validates and stops; `--limit` is smoke, never a
result; `m4_strip.GATE_WORDING` frozen as code before any real run. Runner cut
from `m3_matrix.py` (never from certified predecessors), verdict in
`m4_verdict.py`, tests in `test_m4.py`.

## What M4 does NOT decide

- **How the project closes** — the write-up + `/seed-hunt` flow is the plan of
  record after M4 and is not a milestone decision.
- **The banked stretches** (idea #13: scope + scale) — declined for this repo;
  they compete on equal terms in the seed-hunt.
- **M1's, M2's and M3's published verdicts and numbers** — they stand as
  pre-committed; the strip's subset cells re-certify them, never re-litigate
  them.
- **No oracle change.** `oracle.py` stays byte-identical in all four
  consumers; D22 pins its ≤ 3-token span premise without altering the rule.
  What D22 cannot pin is the wording's *scope* premise — "None of the three
  concepts is in M2's subset" — which M4's wider probe side retires. That
  residual is owned in the deviations table and carried by the
  residual-conservative read (D20), not by a rule change. Never an LLM judge,
  never free-text parsing (standing guardrail).

---

## Results (2026-07-29) — **VOCAB-SPARING at 1.5B AND 3B, AS-SCORED ONLY**

Three subjects, 2,340 cells each, ~50 minutes total on MPS, $0. `GATE_WORDING`
was frozen as code and the gates dry-run (six wrong-arm inputs exiting INVALID
with named reasons) before the first real cell.

**The re-certification, two generations deep, on every subject:** M1
**255/255** cells and M3 **468/468** cells reproduced bit-for-bit on the raw
recorded strings, with `concept_mass` exact on all 723 comparisons — ×3 subjects.
Because that surface includes all 180 `clean` cells, every realized n below was
knowable before the run, and every one landed exactly as pre-registered.

| Readout | 0.5B | 1.5B | 3B |
|---|---|---|---|
| Gated items (full roster) | 69 | 105 | 116 |
| **Gate arm** (gated non-subset) | **41** | **71** | **84** |
| **Survives all 12** | **11/41 = 0.268** | **51/71 = 0.718** | **63/84 = 0.750** |
| Wilson 95% | [0.157, 0.419] | **[0.605, 0.810]** | **[0.648, 0.830]** |
| vs the pre-registered bar 0.5 | fails (off-gate) | **clears** | **clears** |
| Residual-conservative (fail in place) | 11/41 = 0.268 | 49/71 = 0.690, lower 0.575 | 62/84 = 0.738, lower 0.635 |
| Concept-level collapse | 4/23 = 0.174 | **24/41 = 0.585, lower 0.434** | **26/43 = 0.605, lower 0.456** |
| Pre-registered ceiling | 35/41 ✓ | 69/71 ✓ | 82/84 ✓ |
| Verdict | `not shown` | **VOCAB-SPARING — AS-SCORED ONLY** | **VOCAB-SPARING — AS-SCORED ONLY** |

**M4 VERDICT: VOCAB-SPARING at 1.5B AND 3B — AS-SCORED ONLY.** Deleting any one
of the 12 characterized directions at the late third spares most of the
measurable wider vocabulary. M3's stated bound is closed: it is now measured,
not assumed, that deleting France spares the other 48 concepts' items.

**The qualifier fired, and it earned its existence.** The concept-level collapse
— one binary per concept instead of per item — reads 0.585 (lower **0.434**) at
1.5B and 0.605 (lower **0.456**) at 3B: *below* the bar at both gate-bearing
subjects while the item-level gate clears it. Per D20's pre-commitment those are
**the honest numbers to quote**, and Amendment 1 is exactly why they ride inside
the verdict string instead of sitting in prose. The residual-conservative read
clears the bar at both (49/71, 62/84), so only one of the two reads fired. Had
the qualifier not been restored at round 4, the published label would have been a
bare `VOCAB-SPARING` over a conservative read the brief itself had already named
as the honest one.

**Every pre-registered number landed.** Gate arms 41/71/84; concept counts
23/41/43; ceilings 35/41, 69/71, 82/84 with exactly the named misses (`july-1`,
`april-1`, `april-3`, `gold-1/2/3` at 0.5B; `july-3`, `venus-3` at 1.5B;
`guitar-2`, `neptune-1` at 3B). No degeneracy fired on the dispositive arm
(shares 0.022 / 0.011 / 0.011 against a 0.5 threshold) and the subset diagonal
carried no collapse tag.

### The residual set was larger in the ablated arm than in the clean arm

The clean-arm gate-arm residual cells were the pre-computed **0 / 2 / 2**. The
*run* recorded **0 / 27 / 21** residual cells in total (26 / 21 in the gate arm),
all on `beetle`, `butterfly` and `trumpet` — the three concepts `oracle.py`'s
frozen docstring names. This is precisely the case D20 wrote the selector for
("in the ablated cells the set is whatever the run records"), and it is why the
residual-conservative read moves the number at all: 51 → 49 at 1.5B, 63 → 62 at
3B. A case-exact selector would have found zero of them.

### Descriptive findings the gate never asked for

1. **Finding 1 generalizes out of sample — there *are* silver-like columns among
   the 48.** Collateral still concentrates on fragile **probes**, not damaging
   **primes**. No prime is a wrecking ball: at 1.5B every row lands between 63/71
   and 67/71, at 3B between 77/84 and 83/84. But specific probe columns collapse:
   `copper` 6/12 and `mosquito` 8/12 at 1.5B; `eagle` 8/12, `platinum` 9/12 and
   `trumpet` 18/36 at 3B. Meanwhile **32 of 53** gated columns at 1.5B and **33
   of 55** at 3B take *zero* collateral across all 12 deletions. The distribution
   is bimodal, which is what makes the item-level and concept-level statistics
   diverge.
2. **Category-block collateral is real in the wider vocabulary and does NOT
   dissolve with scale** — the reverse of what M3 found inside the subset.
   Within-category vs cross-category survival: 5/22 vs 382/470 at 0.5B, **22/29
   (0.759) vs 769/823 (0.934)** at 1.5B, **35/53 (0.660) vs 913/955 (0.956)** at
   3B. M3 saw within-category collateral dissolve by 1.5B, but M3's within arm
   was 30/34 countries; the strip's within arm samples ten categories.
3. **0.5B is the first measured divergence between the subset's robustness and
   the wider roster's.** 30 of its 41 gate-arm items (73%) are damaged by at
   least one deletion, against 28% at 1.5B and 25% at 3B. Read under the standing
   any-direction-damage frame, never as a gate claim — and consistent in advance
   with M3's own 0.5B subset failing this bar in-statistic (19/28, lower 0.4934),
   the 0/6 proxy and M1's 33/69 0.5B control cell.
4. **The two statistics disagree by design, and 0.5B shows it starkly.** The
   M3-comparable cluster-mean per-cell floor reads **32/41 → [0.633, 0.880]** at
   0.5B — comfortably above 0.5 — while the 12-fold conjunction on the same cells
   reads 0.268. Same subject, same cells, opposite side of the same constant.
   That is the sharpest possible illustration of why D20 refused to inherit M3's
   0.5 and wrote the per-cell equivalence (0.5^(1/12) ≈ 0.944) into the frozen
   wording.
5. **The five cross-mention cells did not carry the verdict, as predicted.** At
   3B all four gate-bearing cells named their concept; at 1.5B three named and
   `China→jade-1` missed; `Egypt→beetle-2` remains ungated on all three subjects.

### Honest limits

- **The claim is sparing across the *measurable* vocabulary**, said exactly that
  way. 25 / 7 / 5 of the 48 non-subset concepts gate zero items — a competence
  selection that plausibly enriches for robust concepts and biases the floor
  **upward**.
- **The concept-level read is below the bar at both gate-bearing subjects.** The
  AS-SCORED ONLY qualifier is not decoration: an honest one-line summary is "the
  item-level floor clears 0.5; the concept-level floor's lower bound does not."
- **The 0.5 constant is lenient and uncalibrated**, pre-registered before any new
  cell and fitted to none. It is a floor bar, not an effect size; at the realized
  1.5B rate, 20 of 71 measurable items are still damaged by at least one of the
  12 deletions.
- **Prime-side correlation structure is now measured but not modelled** — the
  survives-all-12 statistic is conservative under it, and the strip records the
  per-pair cells a later stage could model.

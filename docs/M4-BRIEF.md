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
silver-like columns exist among the 48 —
both outcomes are findings, and a *failed* gate (a low survival floor across
the wider vocabulary) would be the pre-committed reportable headline against
the specificity story's reach.

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
  **the model names something else**, not because of token geometry: under
  D9(b) the gate is a prefix on the 3-token span, so it is insensitive to
  token count up to 3, and four of the seven 1.5B zero-gated concepts are
  single-token bare. The recorded clean spans say it plainly — `saturn-1/2/3
  → 'Jupiter'`, `neptune-1 → 'Jupiter'`, `bronze-2 → 'Aluminum'`,
  `monday-1/2/3 → 'Friday'`, `thursday-1/3 → 'Friday'`, `moth-1 → 'Wasp'`;
  `ant-1/2 → 'Ants'` is a morphology miss (a plural closes no boundary).
  So the gate arm is **the concepts this subject already names correctly** — a
  *competence selection*, and confidently-named concepts are plausibly the
  robust ones, which biases the measured sparing floor **upward**. That is the
  same enrichment mechanism as F12's selection-enrichment finding, now on the
  probe side; it is why the claim is sparing across the *measurable*
  vocabulary, said exactly that way.
- **Four probe clues mention a prime's spelling — a confound M3's design never
  had.** M1's leak guard (D5) bars a clue from leaking its *own* concept or
  control; M3 verified no cross-mentions *within the 12*. Widening probes to
  180 items surfaces exactly four (prime, item) pairs where the item's clue
  contains the deleted word at a word boundary: **October→september-2,
  silver→flute-1, China→jade-1, October→opal-2**. In those cells a miss cannot
  distinguish "collateral damage to naming machinery" from "the clue's own
  text lost a word it references." All four items gate at both gate-bearing
  subjects (only jade-1 gates at 0.5B), so the cells are live. D21 decides
  their treatment.
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
  spelling with nothing following it**, so no boundary character is observed.
  ("Fills the 3-token span" would not distinguish anything — every recorded
  `greedy_3` is exactly 3 tokens by construction.) On that reading the
  gate-arm residual cells are **0 / 2 / 2** at 0.5B / 1.5B / 3B — 1.5B
  `beetle-1` ('Beetle') and `butterfly-1` ('Butterfly') of 71; 3B `trumpet-3`
  ('Trumpet') and `butterfly-1` ('Butterfly') of 84; none gated at 0.5B. This
  is exactly the set `oracle.py`'s frozen docstring already names ("beetle-1,
  butterfly-1 ×2 arms, trumpet-3"). The other trumpet cells are *not*
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
  proxy is genuinely predictive is the *rest* of the pool. The pool itself is
  mostly cross-category, so a
  high floor is the prediction at the gate-bearing subjects. At 0.5B the same
  proxy reads **0/6** — consistent with M1's full-battery 0.5B control cell
  (33/69) and with F12's selection-enrichment finding (the subset-12's 0.5B
  robustness came partly from S1's selection rule), and *not* with M3's clean
  0.5B subset floor. The strip may well fail its floor at 0.5B — off-gate,
  under the standing any-direction-damage frame, and reportable as the
  measured resolution of that tension.

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
  > (12) as much as on the sparing rate. The M4 verdict is the AND over 1.5B
  > and 3B; 0.5B runs and is reported under its standing
  > any-direction-damage frame, never gate-bearing. Gate-arm n (41 / 71 / 84)
  > < MIN_N = 20 ⇒ pre-declared UNDERPOWERED and no claim.

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
spelling exactly, with nothing following it** (no boundary character observed).
That is the selector, stated once here and implemented verbatim: it is *not*
"the span fills the 3-token window", which every recorded cell does. In the
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
out-of-sample test — are there silver-like columns among the 48?); the within- vs
cross-category split of the new pool; the four confound cells (D21); mean
concept mass per cell under D13's standing scope; the 0.5B floor under its
standing frame (the recorded proxy predicts it may fail — that outcome is a
finding, not a failure).

**Verdict precedence, frozen** in `strip_verdict()` (`m4_verdict.py`): NOT A
RESULT > DEGENERATE > UNDERPOWERED > the level bar. Wrong-arm inputs exit
INVALID before the checkpoint loads (the D18-companion shape, carried from
`m3_matrix.py`); `--dry-run` validates and stops; `--limit` is smoke, never a
result; M4 refuses M1 or M3 artifacts that were themselves not results.

### D21 — The four cross-mention cells

- **(a) Keep them in the gate-bearing pool; report them as a named confound
  row (recommended).** The four cells stay in every pooled arm and in their
  items' survives-all-12 conjunctions, and the results section reports each
  cell's outcome individually under its named confound. *Why:* a confounded
  miss can only **lower** the floor — the bias runs against the gate, the one
  direction this project ships owned. Excluding them would delete only cells
  that could hurt the claim, which is the anti-conservative move the lineage
  never makes. Four cells of 852 (1.5B) cannot carry a verdict either way;
  what they can do is mislead a *reader* of the column profiles, and the named
  row prevents that.
- **(b) Pre-registered exclusion from gate-bearing pools, reported as
  texture.** Cleaner causal story per cell, but it is evidence-removal in the
  gate's favour — rejected on the standing bias rule. Not recommended.
- **(c) Drop the four items entirely.** Loses their clean cells and their 11
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
| Four cross-mention (prime, item) cells kept in gate-bearing pools | M3's verified no-cross-mention property | M1's leak guard only bars own-concept/control leaks; the confound biases against the gate; named per-cell reporting (D21a) |
| `oracle.py` byte-shared by a fourth consumer (`m4_strip.py`) | cut-from-predecessor rule | Same D9 rationale as the first three consumers: the rule's purpose is byte-identity; pinned by the existing shared-oracle test pattern |
| D9(b)'s owned span-truncation residual sits in a gate-bearing arm | `oracle.py`'s scope sentence, "None of the three concepts is in M2's subset" | M4 scores all 60 probes, so beetle / butterfly / trumpet are gated again for the first time since M1 (0 / 2 / 2 gate-arm cells whose span equals the spelling with no boundary observed — `oracle.py`'s own named set); the bias runs *toward* the gate, so it is disclosed per subject and carried by the pre-registered residual-conservative recomputation, fail-in-place (D20), never by editing `oracle.py` |
| Probe-side reach is still the D9(b)-visible roster | "the vocabulary" | 25 / 7 / 5 concepts gate zero items — a **competence selection** (the model names something else; the gate is token-count-insensitive up to 3), not tokenizer geometry; that selection plausibly enriches for robust concepts and biases the floor **upward** (F12's enrichment mechanism, probe side); the claim is sparing across the *measurable* vocabulary, said exactly that way |

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
| Confound cells in the pool (D21a) | 1 | 4 | 4 | named texture |
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
recorded cells put the ceiling at **35 of 41** (all 6 proxy cells miss), so the
off-gate floor may well fail there, which would be the first measured
divergence between the subset's 0.5B robustness and the wider roster's.

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

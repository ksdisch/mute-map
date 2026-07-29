"""m4_strip.py — M4: the vocabulary collateral strip (does deleting one of the 12
characterized directions spare the *wider* vocabulary, not just the other 11?).

Cut from `m3_matrix.py`, which was cut from `m2_depth.py`, which was cut from
`m1_battery.py`, which was cut from the certified `m0_anchor.py` (untouched
post-gate, D2/M0). The measurement machinery is unchanged — same naming template,
same chat encoding, same k = 1 J-lens projection removal with the runtime
read-back, same frozen band and thirds, same D9(b) oracle, same Wilson/Newcombe
rulers — so the cells this strip shares with M1's *and* M3's recorded artifacts
must reproduce them bit-for-bit, which this runner checks before it reads a
single new cell (D19a).

What M4 adds, each frozen in `docs/M4-BRIEF.md` before any run:

- **the 12-prime x 180-item strip (D19a)** — M3 measured collateral among the 12
  subset concepts and stated its own bound plainly: nothing there shows that
  deleting France spares the other 48 M1 concepts. M4 keeps the 12 characterized
  directions as the PRIMES and widens the PROBES to all 60 M1 concepts — the full
  frozen 180-item battery. Per subject: `clean` (180) + 12 x 180 = 2,340 cells.
  Depth and dose stay fixed at the switch's home (the late third, lambda = 1,
  k = 1), so every cell differs from every other in exactly one thing — which
  direction was removed and which item was asked.
- **the level gate on the new pool (D20)** — VOCAB-SPARING iff, among the gated
  NON-SUBSET items, the proportion surviving ALL 12 deletions has its Wilson 95%
  lower bound at or above 0.5. Single-clause by design (the conjunction-degeneracy
  obligation is discharged with exactly one surviving arm on the dispositive
  list), with the pre-declared AS-SCORED ONLY qualifier when a pre-registered
  conservative read falls below the bar and the as-scored read does not.
- **the re-certification, two generations deep (D19a)** — 255 cells per subject
  are recorded in M1's artifacts and 468 in M3's; both sets are graded FIRST and
  compared on raw recorded strings, and any mismatch exits INVALID.
- **the run-time instrument bars, widened (D22a)** — D18's span and ASCII bars
  now run over every SCORED word (all 60) plus the 12 direction words, because
  M4 scores 60 concepts where M3 scored 12. `oracle.py` itself is untouched: it
  is byte-shared with `m1_rescore.py`, `m2_depth.py` and `m3_matrix.py` and must
  stay identical.

Owned divergences from `m3_matrix.py` (M4-BRIEF deviations table + dispositions):

- **no control-extra directions.** M3 ran six out-of-subset control directions to
  complete its 108-cell recorded surface. M4 probes all 180 items under all 12
  primes, so every M1 `control_late` cell whose control direction is a subset
  member is already a strip cell; the other controls are not strip primes and are
  not run.
- **`m3_matrix.GATE_WORDING` is not imported or edited** — M3's wording stays
  byte-frozen with M3's artifacts. M4 freezes its own below, verbatim from D20
  including its two post-freeze ratified amendments.
- **the verdict precedence lives in `m4_verdict.strip_verdict()`**, imported here
  rather than copied, so exactly one implementation of the pre-committed verdict
  string exists (the `oracle.py` rationale, applied to wording).

Run:  uv run python -u m4_strip.py \
          --model-id Qwen/Qwen2.5-1.5B-Instruct \
          --lens lenses/qwen2.5-1.5b-instruct-n100.pt
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import time
from collections import Counter

import torch
import transformers

from harness import (
    COLLAPSE_SHARE,
    FROZEN_BANDS,
    MIN_N,
    READBACK_TOL,
    degeneracy,
    encode_chat,
    fail_invalid,
    output_logits,
    proportional_band,
    rate_cell,
    token_forms,
)
from intervention import Edit, ablate, jlens_vector
from m1_battery import (
    CLUES_PER_CONCEPT,
    EXPECTED_CONCEPTS,
    EXPECTED_ITEMS,
    ITEMS_PATH,
    load_items,
    sub_band_thirds,
)
from m4_verdict import SURVIVAL_LOWER_BOUND, strip_verdict
from oracle import (
    ORACLE_WORDING,
    SPAN_TOKENS,
    says_concept_anywhere,
    says_concept_prefix,
)
from stats import excludes_zero, newcombe_diff, wilson
from subject import SubjectModel

#: D19(a): M3's primes — themselves M2's D11-stratified 12, reused VERBATIM.
#: Copied rather than imported, per the standing cut-from-your-predecessor rule;
#: a test pins it equal to M3's (and so, transitively, to M2's).
SUBSET = (
    "Brazil", "Canada", "China", "Egypt", "France", "Japan",   # S1 (+Egypt, S3)
    "Jupiter", "Mars", "piano", "violin",                      # S2
    "October",                                                 # S3
    "silver",                                                  # S4
)
SUBSET_STRATA = {
    "S1_hard_switch_core": ["Brazil", "Canada", "China", "France", "Japan"],
    "S2_readout_unlocked": ["Jupiter", "Mars", "piano", "violin"],
    "S3_leaky_switch": ["Egypt", "October"],
    "S4_non_specific_anti_example": ["silver"],
}
#: Every word whose direction this run ablates. Unlike M3 there are no
#: control-extra directions: the strip probes all 180 items under all 12 primes,
#: so the recorded control cells that are strip cells are already covered.
PLANNED_DIRECTIONS = SUBSET

NAMING_Q = (  # verbatim from the certified m0_anchor.py, via m1_battery/m2/m3
    'Consider this sentence: "{clue}"\n\n'
    "Which {noun} is the sentence describing? Answer with just the name."
)
#: M4 holds depth and dose fixed at the switch's home: full removal, k = 1.
STRIP_LAMBDA = 1.0
#: The M1 conditions the shared cells reproduce, in M1's own names.
M1_SHARED_CONDITIONS = ("clean", "primed_late", "control_late")
#: D19: both cross-checks compare raw recorded strings, so they are
#: oracle-independent — D9 cannot soften them.
CELL_FIELDS = ("greedy", "greedy_3")
#: D20's M3-comparable reference line for the cluster-mean per-cell floor. This
#: is the readout M3 gated on; here it is reported beside and NEVER gating, so
#: D17's "acceptable only because the qualifier is never dispositive" rationale
#: for the binomial-on-bounded-fractions approximation stays intact.
CLUSTER_FLOOR_REFERENCE = 0.5
P_NAME_FLOOR = 0.85  # paper's verbatim naming threshold — reported, never gating
#: The stack the anchor's bit-for-bit reproduction was certified on (M0, D1).
CERTIFIED_DEVICE = "mps"
CERTIFIED_PINS = {"torch": "2.13.0", "transformers": "5.13.1"}

#: D21, frozen: the five (prime, item) pairs whose clue mentions a prime's
#: spelling, scanned with D5's OWN rule — no word of the clue may START WITH the
#: string, case-insensitive, plus that string's `forbidden_forms` entries — not
#: the narrower whole-word match, which misses `Egypt -> beetle-2` ("Ancient
#: EgyptIANS carved amulets of the scarab"). Kept in the gate-bearing pool
#: (D21a): a confounded miss can only LOWER the floor, so the bias runs against
#: the gate. `beetle-2` is ungated on all three subjects today and carries no
#: gate-bearing cell; it is listed so a future re-gate cannot silently acquire one.
CROSS_MENTION_PAIRS = (
    ("October", "september-2"),
    ("silver", "flute-1"),
    ("China", "jade-1"),
    ("October", "opal-2"),
    ("Egypt", "beetle-2"),
)

#: D19(a)'s two re-certification surfaces, per subject, computed from the frozen
#: battery in `expected_recorded_cells()` and pinned here as the pre-registered
#: numbers the brief published: 255 M1-recorded cells (180 `clean` + 36
#: `primed_late` + 39 `control_late` whose control direction is a prime) and 468
#: M3-recorded cells (the 36 subset `clean` + all 432 matrix cells).
EXPECTED_M1_CELLS = 255
EXPECTED_M3_CELLS = 468
EXPECTED_M3_ITEMS = len(SUBSET) * CLUES_PER_CONCEPT  # 36

#: Every gate's wording, frozen as code before any M4 run (project guardrail:
#: "pre-commit gates as code — wording included"). Written verbatim into the
#: results JSON so prose and code can never drift. M1's, M2's and M3's wordings
#: are NOT imported: each stays byte-frozen with its own artifacts.
GATE_WORDING = {
    "oracle": ORACLE_WORDING,
    "competence": (
        "D9(b) + D6(a) item-level greedy-span naming-only gate, carried verbatim "
        "from M2/M3: an item enters the gated set iff its CLEAN naming span "
        "satisfies the D9(b) oracle above. Gating is a property of the clean arm "
        "alone, decided once per item and DIRECTION-INDEPENDENT, so every one of "
        "this run's 12 prime columns shares ONE gated set — which is what makes "
        "the rows, the columns and the pooled arms comparable. Gating is "
        "per-subject. M1's first-token gate is computed and recorded beside it as "
        "texture, never gating here. The paper-style verbatim-P rate (clean "
        "concept mass >= 0.85) is reported alongside as texture, never gating; "
        "note it is floor-pinned by construction for concepts whose emitted bare "
        "spelling has no single-token form (the mass-channel scope, D13). OWNED, "
        "AND THE REASON THE CLAIM SAYS WHAT IT SAYS: 25 / 7 / 5 of the 48 "
        "non-subset concepts gate ZERO items at 0.5B / 1.5B / 3B, because the "
        "model answers something else, answers correctly behind a modifier the "
        "opening-word rule refuses, or misses on morphology — a COMPETENCE "
        "SELECTION, not tokenizer geometry (under D9(b) the gate is a prefix on "
        "the 3-token span, so it is insensitive to token count up to 3). "
        "Confidently-named concepts are plausibly the robust ones, so the "
        "selection biases the measured sparing floor UPWARD (F12's "
        "selection-enrichment mechanism, now on the probe side). The claim is "
        "sparing across the MEASURABLE vocabulary, said exactly that way."
    ),
    "sparing": (
        "D20(a), pre-committed before any M4 run, with both post-freeze "
        "amendments ratified by Kyle 2026-07-29. VOCAB-SPARING iff, per subject: "
        "among the gated NON-SUBSET items (concepts outside the 12-concept matrix "
        "roster), the proportion that SURVIVES ALL 12 subset-direction deletions "
        "— D9(b) naming success in every one of the item's 12 off-target cells — "
        "has its Wilson 95% lower bound at or above 0.5. This 0.5 is a bar on the "
        "12-FOLD CONJUNCTION, not on per-cell survival, and is NOT M3's per-cell "
        "floor: under independence it corresponds to a per-cell survival of "
        "0.5^(1/12) ~ 0.944, and its stringency depends on the deletion count "
        "(12) as much as on the sparing rate. The bar is read ONLY when the 468 "
        "M3-recorded and 255 M1-recorded cells in the strip reproduce their "
        "recorded outcomes bit-for-bit; any mismatch is INVALID and there is no "
        "verdict. The M4 verdict is the AND over 1.5B and 3B; 0.5B runs and is "
        "reported under its standing any-direction-damage frame, never "
        "gate-bearing. Gate-arm n < MIN_N = 20 => pre-declared UNDERPOWERED and "
        "no claim (realized n = 41 / 71 / 84 from the recorded gated sets). "
        "VERDICT STRING, PRE-COMMITTED: the label alone over-reads — clearing a "
        "floor bar is compatible with a large minority of measurable items "
        "damaged — so the verdict, whichever way it goes, carries its REALIZED "
        "SURVIVAL PROPORTION in the same string: VOCAB-SPARING when the bar is "
        "cleared and the lineage's pre-committed null 'not shown' when it is not "
        "— never an assertive negative, because failing a Wilson LOWER bound does "
        "not establish the contrary (m1_battery.py, m2_depth.py, m3_matrix.py all "
        "emit 'not shown'). The gate verdict is the AND over the two gate-bearing "
        "subjects; 0.5B's readout is reported in the same shape under its "
        "standing any-direction-damage frame and is NOT a gate verdict, so a low "
        "0.5B reading is never a 'not shown' gate claim. "
        "CONSERVATIVE-READ QUALIFIER, PRE-DECLARED: two pre-registered reads can "
        "fall below the bar when the as-scored read clears it — the "
        "residual-conservative fail-in-place read and the concept-level collapse "
        "— and the brief pre-commits that where they diverge, THEIR numbers are "
        "the honest ones. So a CLAIM-LEVEL verdict additionally carries the "
        "qualifier AS-SCORED ONLY, naming each such read and its number, whenever "
        "any pre-registered conservative read's Wilson 95% lower bound is below "
        "0.5 while the as-scored read's is not. The qualifier SCOPES A CLAIM AND "
        "CAN NEVER CREATE OR RESCUE ONE (D17's rule, carried), so it attaches to "
        "a bar-level verdict only and never to NOT A RESULT, DEGENERATE or "
        "UNDERPOWERED — precedence has already withheld the claim there, leaving "
        "it nothing to scope. THE TWO TEMPLATES, STATED ONCE AND IMPLEMENTED "
        "VERBATIM — base: '<label> (k/n survive all 12 = <rate>; Wilson 95% lower "
        "<lo>)'; qualifier, appended to the base string when it fires: ' — "
        "AS-SCORED ONLY (<read> k/n = <rate>, lower <lo>[; <read> ...])', with the "
        "reads listed in the fixed order residual-conservative, concept-level "
        "when both fire. Worked: 'VOCAB-SPARING (44/71 survive all 12 = 0.620; "
        "Wilson 95% lower 0.503) — AS-SCORED ONLY (residual-conservative 42/71 = "
        "0.592, lower 0.475)'. "
        "THE 0.5 CONSTANT IS NEW, AND OWNED AS NEW — not carried from M3, whose "
        "0.5 was a floor on cluster-collapsed PER-CELL survival while M4's is a "
        "bar on a 12-FOLD CONJUNCTION. Two consequences, stated rather than "
        "inherited. (i) STATUS CHANGED: M3's constant was itself uncalibrated and "
        "D17 tolerated that only because the qualifier it scoped could never "
        "create or rescue a claim; M4 makes a constant of the same value the "
        "SINGLE DISPOSITIVE GATE, so D17's tolerance does not transfer. (ii) THE "
        "DELETION COUNT IS HALF THE BAR: at a per-cell rate of 0.971 (M3's "
        "recorded 1.5B off-diagonal) the conjunction reads ~0.70 and clears the "
        "bar; at 0.94 it reads ~0.48 and fails. M4's 0.5 is therefore a new, "
        "deliberately lenient, uncalibrated constant — pre-registered before any "
        "new cell was run and fitted to none — and its per-cell equivalence is "
        "written into this wording so no write-up can quote it as M3's floor. It "
        "is a floor bar, not an effect-size claim; the descriptive numbers carry "
        "the actual size. "
        "WHY THE RE-CERTIFICATION CLAUSE IS INSIDE THE WORDING: every prior "
        "stage's gate compared an intervened arm against another MEASURED arm, so "
        "a dead intervention could never pass one. M4's bar is single-clause and "
        "reads only the off-target survival rate — so read in isolation, an "
        "ablation that did nothing at all would score ~100% survival and print "
        "VOCAB-SPARING. The strip's re-run of M3's 432 matrix cells and M1's 36 "
        "primed_late cells catches exactly that, and any mismatch exits INVALID; "
        "putting it in the frozen wording means the sentence cannot be quoted out "
        "of its own precondition. "
        "TRADE-OFF, OWNED: survives-all-12 is the strictest sparing statistic; a "
        "single fragile cell fails an item, and the correlation structure across "
        "the 12 deletions (unmeasured until this run) decides how harsh that is. "
        "That bias direction runs AGAINST the claim, the one direction this "
        "project accepts. Every strip cell ablates the subject's identical "
        "late-third layer set at lambda = 1, k = 1, so the compared arms differ "
        "ONLY IN WHICH DIRECTION IS REMOVED and which item is asked — never in "
        "depth, layer count, or dose (PR #7 review F2's tier-width caveat, "
        "retired structurally and stated here so it stays owned; if a later stage "
        "re-introduces tiers, the caveat clause must come back with them)."
    ),
    "conservative_reads": (
        "D20, both pre-registered here and NEVER dispositive; each is reported "
        "beside the gate and each can fire the AS-SCORED ONLY qualifier. "
        "(1) THE RESIDUAL-CONSERVATIVE READ. D9(b)'s owned span-truncation "
        "residual re-enters a gate-bearing arm for the first time since M1: "
        "`oracle.py`'s frozen wording closes with 'None of the three concepts is "
        "in M2's subset', and M4's wider probe side retires exactly that scope "
        "sentence. The same gate statistic is recomputed with every RESIDUAL CELL "
        "re-scored as a MISS — the maximally conservative reading of the boundary "
        "D9(b) cannot observe. A RESIDUAL CELL is one whose recorded span, after "
        "stripping leading whitespace, EQUALS THE SCORED CONCEPT'S SPELLING WITH "
        "NOTHING FOLLOWING IT — compared CASE-INSENSITIVELY, exactly as "
        "`oracle.says_concept_prefix` compares (re.IGNORECASE) — so that no "
        "boundary character is observed. The case rule is stated because it "
        "DECIDES THE SET, not as a detail: the recorded spans are 'Beetle', "
        "'Butterfly', 'Trumpet' while the roster spellings are lowercase, so a "
        "case-EXACT comparison would select ZERO cells and silently turn this "
        "mitigation into a no-op. That is the selector: it is NOT 'the span fills "
        "the 3-token window', which every recorded cell does by construction. In "
        "the recorded clean arm the gate-arm residual cells are 0 / 2 / 2 at "
        "0.5B / 1.5B / 3B (1.5B beetle-1, butterfly-1; 3B trumpet-3, "
        "butterfly-1); in the ablated cells the set is whatever the run records, "
        "computed from the same recorded spans by the same selector. DENOMINATOR, "
        "PRE-REGISTERED: FAIL IN PLACE. The gate arm stays at its as-scored n — "
        "41 / 71 / 84, the knowable-now cross-check the power table freezes — and "
        "a residual-affected item scores as a FAILURE within that arm. The "
        "alternative reading (re-score the clean cell too, so the item un-gates "
        "and the arm shrinks) is named and REJECTED: it is the less conservative "
        "of the two at the bar — with the same numerator, wilson(43, 71) reads "
        "0.489 and fails while wilson(43, 69) reads 0.505 and passes — and it "
        "would break the power table's pre-registered n. Fail-in-place keeps the "
        "read strictly one-way: it can only lower the floor, never rescue it. The "
        "bias the residual itself carries runs TOWARD the gate (an "
        "unobservably-terminated span scores a hit), which is why it is disclosed "
        "per subject and carried by this recomputation rather than by editing "
        "`oracle.py` — editing it would force re-runs of three milestones. "
        "(2) THE CONCEPT-LEVEL COLLAPSE (the effective-n sanity check). Items "
        "cluster three-per-concept on the probe side, so beside the item-level "
        "gate the same statistic is recomputed collapsed to one binary per "
        "CONCEPT — 'every gated item of this concept survives all 12 deletions' — "
        "over the non-subset concepts with >= 1 gated item (n = 23 / 41 / 43, all "
        ">= MIN_N). If the item-level gate is clean and the concept-level collapse "
        "is not, the concept-level numbers are the honest ones to quote."
    ),
    "descriptive": (
        "D20's descriptive package — never gate-bearing, Wilson CIs, all "
        "pre-registered in the brief. The CLUSTER-MEAN PER-CELL FLOOR on the new "
        "pool (M3's F15 readout, reference line 0.5 — the M3-comparable view; "
        "deliberately NOT promoted to gate-bearing, so D17's 'acceptable only "
        "because the qualifier is never dispositive' rationale for that binomial "
        "approximation stays intact). The ORDERING CONTRAST from rejected option "
        "(b) (pooled off-target minus the subset diagonal, Newcombe), reported as "
        "descriptive continuity with M3. Per-prime ROW PROFILES (does any of the "
        "12 damage the wider vocabulary?) and per-probe COLUMN PROFILES over all "
        "60 concepts — finding 1's mostly out-of-sample test: M3 found collateral "
        "concentrates on fragile PROBES (silver's column) rather than on damaging "
        "PRIMES, and the 48 new probe columns are a near-fresh sample (6 / 8 / 15 "
        "of their gate-bearing cells are M1-recorded, the other 486 / 844 / 993 "
        "are new). The WITHIN- vs CROSS-CATEGORY split of the new pool. The five "
        "named CROSS-MENTION cells (D21a). Mean concept mass per cell under D13's "
        "standing scope. Per-pair (prime, probe) cells are n <= 3 and are always "
        "descriptive, never verdict-bearing (D7's logic, unchanged). The pooled "
        "852-cell view repeats each item 12 times and is therefore texture, never "
        "the gate (M3's F11 lesson applied in advance)."
    ),
    "run_time_bars": (
        "D22(a), pre-trial, on the subject's own tokenizer — D18's two bars "
        "widened from M3's 12 direction words to EVERY SCORED WORD (all 60) plus "
        "the 12 direction words, because the soundness premise attaches to every "
        "scored word and M4 scores 60. (1) THE SPAN BAR: every such word must "
        "tokenize to <= oracle.SPAN_TOKENS = 3 in BOTH its bare and its "
        "leading-space form, max(len(tok(w)), len(tok(' ' + w))) <= SPAN_TOKENS, "
        "else the run exits INVALID. This is D9(b)/D10's whole soundness premise "
        "— a prefix hit cannot be hidden by span truncation BECAUSE every roster "
        "word fits the span — checked where it can drift (a tokenizer revision, a "
        "future roster edit) instead of inherited as an assumption. (2) THE ASCII "
        "BAR: every such word must be pure ASCII, else INVALID — "
        "`oracle._BOUNDARY` is `(?![A-Za-z0-9])`, so a non-ASCII continuation "
        "character would read as a word boundary and a longer non-ASCII word "
        "could score as a hit. Verified in advance for all 60 words on all three "
        "tokenizers (2026-07-28); the run-time bar still runs, because D18's "
        "point was that the premise must hold AT THE MOMENT OF MEASUREMENT. NOTE "
        "WHAT THE SPAN BAR CANNOT CATCH: the D9(b) residual passes it at exactly "
        "<= 3 tokens, which IS the residual condition — the residual is carried by "
        "disclosure plus the residual-conservative read above, never by this bar. "
        "M4 adds NO vocabulary (every probe and every prime comes from M1's "
        "frozen 60, all pure-ASCII spellings), so D18's named future trigger — a "
        "stage freezing a NON-ASCII list, which owes the `oracle._BOUNDARY` "
        "boundary-class decision first — is NOT fired by this stage; it continues "
        "to name the banked scope stretch. `oracle.py` is UNTOUCHED by both bars: "
        "it is byte-shared with `m1_rescore.py`, `m2_depth.py` and `m3_matrix.py` "
        "and must stay identical."
    ),
    "degeneracy": (
        "D20, carrying D14/D17's wide-oracle guard verbatim and re-scoping it to "
        "M4's arms. The dispositive guard is unchanged in mechanism: pool the "
        "first tokens of an arm's NON-PRODUCED cells only, share taken against "
        "the arm's full cell count ('at least half this arm's answers are the "
        "same WRONG opening'), threshold COLLAPSE_SHARE = 0.5; the raw "
        "all-answers guard is recorded beside as texture. SCOPE, ENUMERATED — and "
        "this enumeration IS the discharge of PR #9 F1's conjunction-degeneracy "
        "obligation, which requires every surviving-side comparison arm of a "
        "conjunction gate to be on the dispositive list: M4's gate is "
        "deliberately SINGLE-CLAUSE, so the dispositive list has exactly ONE "
        "surviving arm. Collapse in the pooled NON-SUBSET OFF-TARGET arm — the "
        "single arm the gate reads — => DEGENERATE, no VOCAB-SPARING claim. "
        "Collapse in the subset DIAGONAL => TAG only (the expected mute "
        "signature, exactly `primed_late`'s standing treatment). `clean` stays "
        "off the dispositive list (it is the gate arm — the D14 F3 correction, "
        "carried). Collapse inside any single prime's ROW, any probe concept's "
        "COLUMN, or any per-pair CELL is TEXTURE, attached to the readout it "
        "compromises. If a later amendment ever makes M4's gate a conjunction, "
        "every surviving arm goes on this list before the wording freezes."
    ),
    "recorded_crosscheck": (
        "D19(a), environment-scoped (carrying D16's pattern, M2's D14 and M1's "
        "D5a/F7 verbatim), one generation deeper and against TWO artifact sets at "
        "once. Per subject the strip contains 255 cells recorded in M1's "
        "artifacts (`clean` 180, the 12 subset concepts' `primed_late` 36, and "
        "the 39 `control_late` cells whose control direction is a subset member) "
        "and 468 cells recorded in M3's artifacts (the 36 subset `clean` cells "
        "plus all 432 matrix cells — everything M3 ran except its 18 "
        "out-of-subset control-extras, whose directions are not strip primes). "
        "Both sets are graded FIRST and compared cell-for-cell on the RAW "
        "RECORDED FIELDS (`greedy` and `greedy_3` decoded strings) BEFORE any new "
        "cell is read; `concept_mass` equality is recorded as texture, never "
        "gating. The comparison is on raw strings, so it is oracle-independent — "
        "D9 cannot soften it. On the certified environment — device 'mps' under "
        "the pinned stack (torch 2.13.0, transformers 5.13.1) — any mismatch is "
        "INVALID (exit 2). Off that environment the check still runs and is "
        "recorded but is NOT gate-bearing, and the whole run is pre-declared NOT "
        "A RESULT, which m4_verdict.py refuses. Coverage is a property of the run "
        "rather than of the environment, so the bars that all 180 items and all "
        "255 M1 cells, and all 36 subset items and all 468 M3 cells, were "
        "actually compared are UNSCOPED (M1 review F1's lesson). CONSEQUENCE "
        "WORTH STATING: because every `clean` cell is M1-recorded and gating is "
        "the deterministic clean arm under a frozen oracle, the realized gate-arm "
        "n is FIXED BEFORE THE RUN at 41 / 71 / 84 — a run that disagrees is an "
        "INVALID cross-check, not a power surprise."
    ),
    "precedence": (
        "D20, frozen in `m4_verdict.strip_verdict()`: NOT A RESULT > DEGENERATE > "
        "UNDERPOWERED > the level bar (VOCAB-SPARING or the pre-committed null "
        "'not shown', each carrying its realized proportion, and AS-SCORED ONLY "
        "appended only at this level — the three higher outcomes withhold the "
        "claim, leaving the qualifier nothing to scope). Wrong-arm inputs exit "
        "INVALID before any trial and, per PR #7 review F6's disposition carried "
        "from M3, before the checkpoint is even loaded; `--dry-run` validates and "
        "stops; `--limit` is smoke, never a result; M4 refuses M1 or M3 artifacts "
        "that were themselves not results. All M1/M2/M3 patterns carried verbatim."
    ),
    "honesty": (
        "Owned, pre-committed. (1) Items within a concept share one lens "
        "direction on the prime side and one concept on the probe side, so "
        "item-level pooling overstates independence; the pre-registered "
        "concept-level collapse is the honest granular view beside it, and the "
        "per-prime, per-probe and per-pair maps are the granular descriptive "
        "views. (2) PRIME-SIDE CLUSTERING — every item faces the same 12 "
        "directions — is the unmeasured correlation structure the survives-all-12 "
        "statistic is conservative under: a single fragile cell fails an item. "
        "(3) MIN_N = 20 is applied to raw n, not to an effective n discounted for "
        "clustering. (4) The pooled 492 / 852 / 1,008-cell off-target view "
        "repeats each gated item 12 times, which would make a Newcombe interval "
        "on it NARROWER than the clustering justifies — anti-conservative and "
        "owned, which is why that pool is TEXTURE and the gate reads the "
        "per-item conjunction instead (M3's F11 lesson applied in advance). "
        "(5) THE PROBE-SIDE REACH IS THE D9(b)-VISIBLE ROSTER, not 'the "
        "vocabulary' (see the competence wording): a competence selection that "
        "plausibly biases the floor UPWARD. (6) THE FIVE CROSS-MENTION CELLS "
        "(D21a) are kept in the gate-bearing pool: a confounded miss can only "
        "LOWER the floor, so the bias runs against the gate — excluding them "
        "would be evidence-removal in the gate's favour, the anti-conservative "
        "move the lineage never makes. They are reported individually as a named "
        "confound row so a reader of the column profiles is not misled. (7) THE "
        "D9(b) RESIDUAL biases TOWARD the gate and is the one bias direction here "
        "that does; it is disclosed per subject and carried by the pre-registered "
        "residual-conservative read. (8) THE PRE-REGISTERED CEILINGS are facts "
        "about the arm, not evidence for the gate: 6 / 8 / 15 gate-arm cells are "
        "already recorded in M1 and their misses cap the arm at 35/41, 69/71 and "
        "82/84 before a single new forward pass."
    ),
}


# --- the frozen battery -------------------------------------------------------

def load_strip_items(path: str = ITEMS_PATH) -> list[dict]:
    """M1's frozen 180-item battery, whole — every guard in M1's loader runs
    first (roster shape, clue counts, fixed controls, leak test), so M4 cannot
    run against a drifted battery; then this adds M4's own bars: the 12 primes
    must all be roster concepts, and the five D21 cross-mention pairs must be
    exactly the ones the frozen list names, so the confound row is a CHECKED FACT
    rather than a hard-coded hope."""
    items = load_items(path)
    covered = {item["concept"] for item in items}
    missing = sorted(set(SUBSET) - covered)
    if missing:
        raise ValueError(
            f"{path} is missing pre-registered prime concept(s) {missing} — the "
            "frozen subset and the frozen battery have drifted apart"
        )
    if len(covered) != EXPECTED_CONCEPTS or len(items) != EXPECTED_ITEMS:
        raise ValueError(
            f"{path} drew {len(items)} items over {len(covered)} concepts, "
            f"expected {EXPECTED_ITEMS} over {EXPECTED_CONCEPTS}"
        )
    strata = sorted(c for group in SUBSET_STRATA.values() for c in group)
    if strata != sorted(SUBSET):
        raise ValueError("SUBSET_STRATA does not partition SUBSET")
    scanned = cross_mention_pairs(items, json.load(open(path))["forbidden_forms"])
    if sorted(scanned) != sorted(CROSS_MENTION_PAIRS):
        raise ValueError(
            f"the battery's prime cross-mentions are {sorted(scanned)}, not the "
            f"frozen {sorted(CROSS_MENTION_PAIRS)} — D21's confound list was "
            "pre-registered against the frozen clues"
        )
    return items


def cross_mention_pairs(
    items: list[dict], forbidden_forms: dict[str, list[str]]
) -> list[tuple[str, str]]:
    """D21's scan, run with D5's OWN rule: no word of the clue may START WITH the
    prime's spelling, case-insensitive, nor with any of its frozen
    `forbidden_forms`. An item's own concept and control are excluded because
    M1's loader already bars those (D5's leak guard) — what is left is exactly
    the confound M3's 12-concept design never had.

    A whole-word scan would be the narrower rule and would MISS
    `Egypt -> beetle-2`, whose clue inflects the prime ('Ancient Egyptians');
    that is why the rule is stated as a prefix rule here and not assumed.
    """
    pairs = []
    for prime in SUBSET:
        blocked = [prime.lower()] + [f.lower() for f in forbidden_forms.get(prime, [])]
        for item in items:
            if prime in (item["concept"], item["control"]):
                continue
            words = re.findall(r"[a-z']+", item["clue"].lower())
            if any(w.startswith(b) for w in words for b in blocked):
                pairs.append((prime, item["name"]))
    return pairs


def concept_categories(items: list[dict]) -> dict[str, str]:
    """concept -> category, read off the frozen items (never hard-coded)."""
    return {item["concept"]: item["category"] for item in items}


# --- the condition plan -------------------------------------------------------

def condition_name(word: str) -> str:
    return f"ablate_{word}"


def plan_conditions(late: list[int]) -> list[dict]:
    """Every condition this run grades: `clean` plus the 12 primes, all at the
    identical late third, all at lambda = 1, k = 1, all applied to every one of
    the 180 items. That uniformity is what makes the strip a strip: 13 cells per
    item, 2,340 per subject."""
    conditions = [
        {"name": "clean", "group": "clean", "direction": None, "layers": [], "lam": 0.0}
    ]
    for word in SUBSET:
        conditions.append({
            "name": condition_name(word), "group": "prime", "direction": word,
            "layers": late, "lam": STRIP_LAMBDA,
        })
    return conditions


def is_m1_recorded(condition: dict, item: dict) -> bool:
    """Is this cell one M1 already recorded for this item? `clean` is M1's
    `clean`; the item's own concept direction is M1's `primed_late` (only a strip
    cell when that concept is a prime); the item's frozen control direction is
    M1's `control_late` (only when that control is a prime)."""
    return condition["direction"] in (None, item["concept"], item["control"])


def is_m3_recorded(condition: dict, item: dict) -> bool:
    """Is this cell one M3 already recorded? M3 ran the 36 subset items under
    `clean` and all 12 primes — so for a subset item every strip cell is an M3
    cell, and for any other item none is. (M3's 18 out-of-subset control-extra
    cells are not strip cells: their directions are not primes.)"""
    return item["concept"] in SUBSET


def is_recorded(condition: dict, item: dict) -> bool:
    return is_m1_recorded(condition, item) or is_m3_recorded(condition, item)


def conditions_for(conditions: list[dict], item: dict) -> tuple[list[dict], list[dict]]:
    """(already-recorded conditions, everything new) for one item, in frozen
    order — the split that makes "before any new cell is read" literally true."""
    return (
        [c for c in conditions if is_recorded(c, item)],
        [c for c in conditions if not is_recorded(c, item)],
    )


def planned_cells(conditions: list[dict], items: list[dict]) -> int:
    """Total clean + ablated cells this plan grades — the wall-clock unit. Under
    D19(a) this is 2,340 per subject: 180 clean + 12 x 180 ablated."""
    return len(conditions) * len(items)


def expected_recorded_cells(items: list[dict]) -> dict[str, int]:
    """The two re-certification surfaces, counted from the frozen battery rather
    than hard-coded — then checked against the pre-registered 255 / 468."""
    m1 = sum(
        1 + (item["concept"] in SUBSET) + (item["control"] in SUBSET) for item in items
    )
    m3_items = [i for i in items if i["concept"] in SUBSET]
    m3 = len(m3_items) * (1 + len(SUBSET))
    if (m1, m3) != (EXPECTED_M1_CELLS, EXPECTED_M3_CELLS):
        raise ValueError(
            f"the frozen battery yields {m1} M1-recorded and {m3} M3-recorded "
            f"strip cells, not the pre-registered {EXPECTED_M1_CELLS} / "
            f"{EXPECTED_M3_CELLS} — the re-certification surface drifted"
        )
    return {
        "m1_cells": m1, "m1_items": len(items),
        "m3_cells": m3, "m3_items": len(m3_items),
    }


# --- the operator (M1's verbatim k = 1 full projection removal) ----------------

def lens_vectors(
    jacobians: dict[int, torch.Tensor],
    layers: list[int],
    rows: dict[str, torch.Tensor],
    device: str,
) -> dict[tuple[int, str], torch.Tensor]:
    """v = J_l^T u for every (layer, prime) this run will ablate, computed once —
    M2/M3's caching, carried verbatim (and certified inert by the same
    cross-checks: a moved value would break bit-for-bit reproduction of the
    reused cells). Each Jacobian is moved to the device one layer at a time so
    the whole lens never has to be resident at once."""
    vectors: dict[tuple[int, str], torch.Tensor] = {}
    for layer in layers:
        jacobian = jacobians[layer].to(device)
        for word, row in rows.items():
            vectors[(layer, word)] = jlens_vector(jacobian, row.float())
        del jacobian
    return vectors


def concept_ablation_edits(
    vectors: dict[tuple[int, str], torch.Tensor], layers: list[int], word: str
) -> dict[int, Edit]:
    """k = 1 full projection removal — M1's operator and read-back verbatim, only
    reading its direction from the precomputed table. Every M4 cell runs through
    this path (lambda = 1 everywhere), so the cells M1 and M3 already recorded are
    reproduced by the same code that recorded them."""
    edits: dict[int, Edit] = {}
    for layer in layers:
        v = vectors[(layer, word)]

        def edit(h: torch.Tensor, layer=layer, v=v) -> torch.Tensor:
            hs = h[0]  # [seq, d_model]
            direction = v.to(device=hs.device, dtype=torch.float32)
            directions = direction.expand(hs.shape[0], 1, -1)
            out = ablate(hs.float(), directions).to(hs.dtype)
            leftover = (out.float() @ direction).abs()
            scale = direction.norm() * hs.float().norm(dim=-1)
            worst = float((leftover / scale.clamp_min(1e-30)).max())
            if worst > READBACK_TOL:
                fail_invalid(
                    f"M4 read-back failed at layer {layer}: surviving "
                    f"projection {worst:.2e} > {READBACK_TOL:.0e}"
                )
            return out.unsqueeze(0)

        edits[layer] = edit
    return edits


def edits_for(
    condition: dict, vectors: dict[tuple[int, str], torch.Tensor]
) -> dict[int, Edit] | None:
    """The edit set one condition applies: none for `clean`, otherwise the full
    ablation of that prime's direction at the late third."""
    if condition["direction"] is None:
        return None
    return concept_ablation_edits(vectors, condition["layers"], condition["direction"])


# --- readouts -----------------------------------------------------------------

def greedy_continuation(
    subject: SubjectModel,
    input_ids: torch.Tensor,
    edits: dict[int, Edit] | None,
    first_id: int,
    n_tokens: int = SPAN_TOKENS,
) -> str:
    """The answer's first `n_tokens` greedy tokens, decoded — the span the D9(b)
    oracle reads. The edits are re-applied on every continuation pass, so the
    ablation stays active across the whole decoded span."""
    ids = [first_id]
    sequence = input_ids
    for _ in range(n_tokens - 1):
        sequence = torch.cat(
            [sequence, torch.tensor([[ids[-1]]], device=sequence.device)], dim=1
        )
        ids.append(int(output_logits(subject, sequence, edits).argmax()))
    return subject.tokenizer.decode(ids)


def concept_mass(logits: torch.Tensor, forms: list[int]) -> float:
    """Softmax probability mass on the concept's single-token forms — kept
    verbatim from M1/M2/M3 (the cross-checks compare it as texture). Floor-pinned
    by construction wherever the emitted bare spelling has no single-token form,
    which is why D13 scopes the mass channel."""
    probs = torch.softmax(logits.float(), dim=-1)
    return float(sum(probs[t] for t in forms))


def bare_form_is_single_token(word: str, tokenizer) -> bool:
    """Does the spelling the model actually emits — the bare, no-leading-space
    form — have a single-token id? One predicate, two consequences, both carried
    from M2: when it is False the ablated direction is keyed to the leading-space
    unembed row (D11 / PR #5 F3), and the concept-mass channel is floor-pinned
    (D13 / PR #5 F2)."""
    return len(tokenizer(word, add_special_tokens=False).input_ids) == 1


def is_residual_cell(span: str, concept: str) -> bool:
    """D20's residual selector, implemented verbatim from the frozen wording.

    A residual cell is one whose recorded span, after stripping leading
    whitespace, **equals the scored concept's spelling with nothing following
    it**, compared **case-insensitively** exactly as `oracle.says_concept_prefix`
    compares — so no boundary character is observed and D9(b) cannot rule out a
    longer continuation ('Beetlejuice' truncates to exactly 'Beetle').

    The case rule DECIDES THE SET and is not a detail: the recorded spans are
    capitalised ('Beetle', 'Butterfly', 'Trumpet') while the roster spellings are
    lowercase, so a case-exact comparison would select ZERO cells and silently
    turn the mitigation into a no-op. Nor is this "the span fills the 3-token
    window" — every recorded `greedy_3` does that by construction, so that
    reading would select every cell. The two mistakes fail in opposite
    directions; both are pinned by tests.
    """
    return span.lstrip().lower() == concept.lower()


# --- D22(a): the run-time instrument bars, widened to every scored word --------

def span_form_lengths(word: str, tokenizer) -> tuple[int, int]:
    """(bare token count, leading-space token count) — the two forms the span bar
    reads. The recorded span holds the model's *emitted* continuation, normally
    the space-prefixed form, and bare length does not bound space-form length."""
    return (
        len(tokenizer(word, add_special_tokens=False).input_ids),
        len(tokenizer(" " + word, add_special_tokens=False).input_ids),
    )


def check_run_time_bars(words: list[str], tokenizer) -> dict:
    """D22(a), pre-trial: the two premises D9(b)/D10's soundness rests on,
    checked on the subject's own tokenizer instead of inherited as assumptions —
    now over every SCORED word (all 60) plus the 12 direction words, because M4
    scores 60 concepts where M3 scored 12.

    (1) every word fits the recorded span in BOTH its bare and its leading-space
    form; (2) every word is pure ASCII, the `oracle._BOUNDARY` premise. Either
    failure exits INVALID before any trial. Returns the measured lengths,
    recorded in the results JSON.
    """
    lengths = {word: span_form_lengths(word, tokenizer) for word in words}
    too_long = sorted(w for w, (bare, space) in lengths.items()
                      if max(bare, space) > SPAN_TOKENS)
    if too_long:
        detail = ", ".join(
            f"{w!r} bare={lengths[w][0]} space={lengths[w][1]}" for w in too_long
        )
        fail_invalid(
            f"D22 span bar: {detail} — max(bare, leading-space) exceeds "
            f"oracle.SPAN_TOKENS = {SPAN_TOKENS}, so a prefix hit could be hidden "
            "by span truncation and the D9(b)/D10 soundness premise does not hold "
            "on this tokenizer"
        )
    non_ascii = sorted(w for w in words if not w.isascii())
    if non_ascii:
        fail_invalid(
            f"D22 ASCII bar: {non_ascii} — `oracle._BOUNDARY` is ASCII-only "
            "([A-Za-z0-9]), so a non-ASCII continuation would read as a word "
            "boundary and could score as a hit. The boundary class is a frozen "
            "measurement rule; changing it needs a decision, not a run"
        )
    return {
        "span_tokens": SPAN_TOKENS,
        "words_checked": len(lengths),
        "form_lengths": {w: list(lengths[w]) for w in sorted(lengths)},
        "worst_form_length": max((max(v) for v in lengths.values()), default=0),
        "all_ascii": True,
    }


# --- environment, validation, cross-checks ------------------------------------

class SubjectSpec:
    """The shape validation needs, read from the config alone — so a wrong-arm
    exit or a `--dry-run` never pays for a checkpoint load (PR #7 review F6's
    disposition, carried from M3). Re-asserted against the loaded `SubjectModel`
    before any trial, so the cheap path can never quietly disagree with the
    measured one."""

    def __init__(self, model_id: str) -> None:
        text_config = transformers.AutoConfig.from_pretrained(model_id).get_text_config()
        self.n_layers: int = text_config.num_hidden_layers
        self.d_model: int = text_config.hidden_size


def certified_environment(device: str) -> tuple[bool, list[str]]:
    """Is this the stack the anchor's bit-for-bit reproduction was certified on?
    Returns (certified, reasons-it-is-not). Carried verbatim from M1/M2/M3."""
    reasons = []
    if device != CERTIFIED_DEVICE:
        reasons.append(f"device {device!r} != {CERTIFIED_DEVICE!r}")
    for module, pin in ((torch, "torch"), (transformers, "transformers")):
        actual = module.__version__
        if actual != CERTIFIED_PINS[pin]:
            reasons.append(f"{pin} {actual} != pinned {CERTIFIED_PINS[pin]}")
    return (not reasons), reasons


def m1_path_for(model_id: str) -> str:
    return "results/m1-battery-" + model_id.split("/")[-1].lower() + ".json"


def m3_path_for(model_id: str) -> str:
    return "results/m3-matrix-" + model_id.split("/")[-1].lower() + ".json"


def load_recorded_run(path: str, milestone: str, model_id: str, band: list[int]) -> dict:
    """One of M4's two comparison targets. A run that was itself pre-declared not
    to be a result cannot certify anything, so it is refused here rather than
    silently cross-checked against."""
    if not os.path.exists(path):
        fail_invalid(f"{milestone} results {path} missing — D19's cross-check needs them")
    try:
        with open(path) as f:
            recorded = json.load(f)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        fail_invalid(f"{milestone} results {path} could not be read as JSON: {exc}")
    if recorded.get("milestone") != milestone:
        fail_invalid(
            f"{path} is not an {milestone} run (milestone={recorded.get('milestone')!r})"
        )
    if recorded.get("model_id") != model_id:
        fail_invalid(f"{milestone} results {path} are for {recorded.get('model_id')!r}, "
                     f"not {model_id!r}")
    if recorded.get("band") != band:
        fail_invalid(f"{milestone} results {path} were run on band "
                     f"{recorded.get('band')}, not {band}")
    if recorded.get("smoke_limit") is not None:
        fail_invalid(f"{milestone} results {path} are a SMOKE run — never a cross-check target")
    if not recorded.get("environment", {}).get("certified"):
        fail_invalid(
            f"{milestone} results {path} ran off the certified environment — "
            "pre-declared NOT A RESULT, so they cannot certify this run either"
        )
    return recorded


def validate(args, artifact: dict, spec, tokenizer) -> tuple[list[int], dict, dict, dict]:
    """Wrong-arm input checks (the M0/M1/M2/M3 gate pattern) plus D22(a)'s two
    run-time bars. Returns (band, the parsed M1 artifact, the parsed M3 artifact,
    the measured bars) — the artifacts are *returned* rather than discarded so
    `main()` never parses them twice (PR #7 review F6's second half), and the
    bars object the results JSON publishes is the very one that gated the run."""
    if artifact.get("model_id") != args.model_id:
        fail_invalid(
            f"lens artifact was fitted on {artifact.get('model_id')!r}, "
            f"not {args.model_id!r}"
        )
    if artifact.get("d_model") != spec.d_model:
        fail_invalid(
            f"lens d_model={artifact.get('d_model')} != subject d_model={spec.d_model}"
        )
    if sorted(artifact["J"]) != list(range(spec.n_layers - 1)):
        fail_invalid(f"lens layers != expected 0..{spec.n_layers - 2}")
    band = proportional_band(spec.n_layers)
    if band != FROZEN_BANDS.get(spec.n_layers):
        fail_invalid(
            f"proportional band {band} disagrees with frozen table "
            f"{FROZEN_BANDS.get(spec.n_layers)} for {spec.n_layers} layers"
        )
    try:
        items = load_strip_items()
        expected_recorded_cells(items)
    except (FileNotFoundError, ValueError) as exc:
        fail_invalid(str(exc))
    bars = check_run_time_bars(scored_and_direction_words(items), tokenizer)
    m1 = load_recorded_run(
        args.m1 or m1_path_for(args.model_id), "M1", args.model_id, band
    )
    m3 = load_recorded_run(
        args.m3 or m3_path_for(args.model_id), "M3", args.model_id, band
    )
    return band, m1, m3, bars


def scored_and_direction_words(items: list[dict]) -> list[str]:
    """D22(a)'s roster: every SCORED word (all 60 probe concepts) plus the 12
    direction words. The primes are among the 60, so this is their union — stated
    as a union anyway, because the premise attaches to both roles and a future
    prime from outside the battery must not slip past the bar."""
    return sorted({item["concept"] for item in items} | set(SUBSET))


def _compare(ours: dict, theirs: dict, label: str, mismatches: list[str]) -> int:
    for field in CELL_FIELDS:
        if ours[field] != theirs[field]:
            mismatches.append(f"{label}.{field}: {ours[field]!r} != {theirs[field]!r}")
    return ours["concept_mass"] == theirs["concept_mass"]


def m1_crosscheck(records: list[dict], recorded: dict) -> tuple[list[str], dict]:
    """D19(a), the M1 half: the 255 cells M4 shares with M1's recorded artifacts
    must reproduce M1's recording exactly on the raw decoded strings. The mapping
    is per item — M4 keys its cells by the ablated direction, so M1's
    `primed_late` is the item's own concept's cell (a strip cell only when that
    concept is a prime) and M1's `control_late` is the item's frozen control's
    cell (only when that control is a prime). Returns (mismatches, texture)."""
    reference = {r["name"]: r for r in recorded["items"]}
    mismatches: list[str] = []
    equal = cells = checked = 0
    for record in records:
        theirs = reference.get(record["name"])
        if theirs is None:
            mismatches.append(f"{record['name']}: absent from the M1 recording")
            continue
        checked += 1
        shared = {"clean": "clean"}
        if record["concept"] in SUBSET:
            shared[condition_name(record["concept"])] = "primed_late"
        if record["control"] in SUBSET:
            shared[condition_name(record["control"])] = "control_late"
        for ours_name, m1_condition in shared.items():
            equal += _compare(
                record["cells"][ours_name], theirs["cells"][m1_condition],
                f"{record['name']}/{ours_name} (M1 {m1_condition})", mismatches,
            )
            cells += 1
    return mismatches, {
        "items_checked": checked, "items_expected": EXPECTED_ITEMS,
        "cells_checked": cells, "cells_expected": EXPECTED_M1_CELLS,
        "mass_cells_equal": equal,
    }


def m3_crosscheck(records: list[dict], recorded: dict) -> tuple[list[str], dict]:
    """D19(a), the M3 half: the 468 cells M4 shares with M3's recorded artifacts —
    the 36 subset items' `clean` cell plus all 432 matrix cells — compared on the
    same raw fields. M3 keyed its cells the same way M4 does (`ablate_<word>`), so
    this comparison is name-for-name."""
    reference = {r["name"]: r for r in recorded["items"]}
    mismatches: list[str] = []
    equal = cells = checked = 0
    for record in records:
        if record["concept"] not in SUBSET:
            continue
        theirs = reference.get(record["name"])
        if theirs is None:
            mismatches.append(f"{record['name']}: absent from the M3 recording")
            continue
        checked += 1
        for name in ["clean"] + [condition_name(w) for w in SUBSET]:
            equal += _compare(
                record["cells"][name], theirs["cells"][name],
                f"{record['name']}/{name} (M3)", mismatches,
            )
            cells += 1
    return mismatches, {
        "items_checked": checked, "items_expected": EXPECTED_M3_ITEMS,
        "cells_checked": cells, "cells_expected": EXPECTED_M3_CELLS,
        "mass_cells_equal": equal,
    }


# --- grading ------------------------------------------------------------------

def grade(
    planned: list[tuple[dict, dict]],
    conditions: list[dict],
    subject: SubjectModel,
    vectors: dict[tuple[int, str], torch.Tensor],
    records: dict[str, dict],
    phase: str,
) -> dict[str, dict]:
    """Run one phase's conditions for every planned item, filling `records` in
    place. Called twice: once for the cells M1 and M3 already recorded (whose
    reproduction the two cross-checks then grade), and once for everything new —
    which is what makes "before any new cell is read" literally true.
    """
    for i, (item, forms) in enumerate(planned):
        start = time.perf_counter()
        recorded_conditions, rest = conditions_for(conditions, item)
        runnable = recorded_conditions if phase == "recorded" else rest
        prompt = NAMING_Q.format(clue=item["clue"], noun=item["noun"])
        input_ids = encode_chat(subject, prompt)
        record = records.setdefault(item["name"], {
            "name": item["name"], "category": item["category"],
            "concept": item["concept"], "control": item["control"],
            "source": item["source"],
            "in_subset": item["concept"] in SUBSET,
            "direction_key": "bare" if forms["bare_single_token"] else "leading_space",
            "mass_channel_eligible": forms["bare_single_token"],
            "cells": {},
        })
        for condition in runnable:
            edits = edits_for(condition, vectors)
            logits = output_logits(subject, input_ids, edits)
            greedy = int(logits.argmax())
            span = greedy_continuation(subject, input_ids, edits, greedy)
            record["cells"][condition["name"]] = {
                # D9(b) primary
                "produced": says_concept_prefix(span, item["concept"]),
                "greedy_3": span,
                # D20's residual selector, computed on the cell that produced it
                "residual": is_residual_cell(span, item["concept"]),
                # recorded beside every cell so cross-checks stay oracle-free
                "produced_first_token": greedy in forms["concept"],
                "greedy": subject.tokenizer.decode([greedy]),
                "greedy_id": greedy,
                "concept_mass": concept_mass(logits, forms["concept"]),
                "says_concept_in_3": says_concept_anywhere(span, item["concept"]),
            }
        if "clean" in record["cells"]:
            clean = record["cells"]["clean"]
            record["gate_span"] = clean["produced"]
            record["gate_first_token"] = clean["produced_first_token"]
            record["gate_verbatim_p"] = clean["concept_mass"] >= P_NAME_FLOOR
        gate = record.get("gate_span")
        print(
            f"[{phase} {i + 1}/{len(planned)}] {item['name']} ({item['concept']}): "
            + (
                f"clean={'OK' if record['cells']['clean']['produced'] else 'x'}"
                f"({record['cells']['clean']['greedy_3']!r}) "
                f"gate={'IN' if gate else 'out'} "
                f"{len(runnable)} recorded cells"
                if phase == "recorded"
                else f"gate={'IN' if gate else 'out'} {len(runnable)} new cells"
            )
            + f" ({time.perf_counter() - start:.1f}s)"
        )
    return records


# --- the pre-committed analysis package ---------------------------------------

def off_target_directions(concept: str) -> list[str]:
    """The primes that are not this concept's own — 12 for every non-subset
    concept (the gate arm), 11 for a subset concept (M3's off-diagonal)."""
    return [word for word in SUBSET if word != concept]


def arm_cells(rows: list[dict], directions_for) -> list[dict]:
    """Every (item, direction) cell of one pooled arm, flattened. `directions_for`
    maps a record to the directions that arm reads on it."""
    return [
        row["cells"][condition_name(word)]
        for row in rows
        for word in directions_for(row)
    ]


def pooled(cells: list[dict]) -> dict:
    return rate_cell(sum(cell["produced"] for cell in cells), len(cells))


def survives_all(record: dict, words: list[str], conservative: bool = False) -> bool:
    """Did this item name its concept under EVERY one of `words`' deletions?

    Under `conservative` the D20 residual read applies: every residual cell is
    re-scored as a miss, and the item's own CLEAN cell is read the same way — a
    residual clean cell would un-gate the item, and D20's pre-registered
    fail-in-place denominator keeps it in the arm as a FAILURE instead of
    shrinking the arm. The read is therefore strictly one-way: it can only lower
    the floor, never rescue it.
    """
    cells = [record["cells"][condition_name(w)] for w in words]
    if conservative:
        cells.append(record["cells"]["clean"])
        return all(c["produced"] and not c["residual"] for c in cells)
    return all(c["produced"] for c in cells)


def wilson_cell(k: int, n: int) -> dict:
    lo, hi = wilson(k, n)
    return {"k": k, "n": n, "rate": (k / n) if n else None, "wilson_95": [lo, hi]}


def contrast(base: dict, mech: dict, label: str) -> dict:
    """The two-proportion comparison rejected option (b) would have gated on,
    reported here as descriptive continuity with M3: `mech` (the surviving
    off-target side) expected above `base` (the muted subset diagonal)."""
    diff = newcombe_diff(base["hits"], base["n"], mech["hits"], mech["n"])
    return {
        "label": label,
        "diagonal": base,
        "off_target": mech,
        "newcombe_offtarget_minus_diagonal_naming": list(diff),
        "excludes_zero": diff[0] > 0 and excludes_zero(diff[1], diff[2]),
    }


def strip_package(
    records: list[dict], categories: dict[str, str], tokenizer, confounds: list[tuple[str, str]]
) -> dict:
    """Everything D20/D21 pre-commits: the single-clause level gate, its two
    never-dispositive conservative reads, and the descriptive package."""
    gated = [r for r in records if r["gate_span"]]
    gate_arm = [r for r in gated if not r["in_subset"]]
    subset_gated = [r for r in gated if r["in_subset"]]
    by_concept: dict[str, list[dict]] = {}
    for record in records:
        by_concept.setdefault(record["concept"], []).append(record)
    gated_by_concept = {c: [r for r in rows if r["gate_span"]]
                        for c, rows in by_concept.items()}

    # --- the gate: survives-all-12 over the gated non-subset items -----------
    n_arm = len(gate_arm)
    survivors = [r for r in gate_arm if survives_all(r, off_target_directions(r["concept"]))]
    gate = wilson_cell(len(survivors), n_arm)

    # --- the two pre-registered conservative reads (never dispositive) -------
    conservative_survivors = sum(
        survives_all(r, off_target_directions(r["concept"]), conservative=True)
        for r in gate_arm
    )
    arm_concepts = sorted({r["concept"] for r in gate_arm})
    concept_survivors = sum(
        all(survives_all(r, off_target_directions(c)) for r in gated_by_concept[c])
        for c in arm_concepts
    )
    conservative_reads = [
        {
            "read": "residual-conservative",
            "note": (
                "every residual cell re-scored as a miss, denominator FAIL IN "
                "PLACE at the as-scored n (D20)"
            ),
            **wilson_cell(conservative_survivors, n_arm),
        },
        {
            "read": "concept-level",
            "note": (
                "one binary per non-subset concept with >= 1 gated item: every "
                "gated item of the concept survives all 12 (D20's effective-n check)"
            ),
            **wilson_cell(concept_survivors, len(arm_concepts)),
        },
    ]

    # --- the new pool, its splits, and the M3-comparable readouts ------------
    new_pool = pooled(arm_cells(gate_arm, lambda r: off_target_directions(r["concept"])))
    within = pooled(arm_cells(
        gate_arm,
        lambda r: [w for w in off_target_directions(r["concept"])
                   if categories[w] == r["category"]],
    ))
    cross = pooled(arm_cells(
        gate_arm,
        lambda r: [w for w in off_target_directions(r["concept"])
                   if categories[w] != r["category"]],
    ))
    subset_diagonal = pooled([r["cells"][condition_name(r["concept"])] for r in subset_gated])
    subset_off_diagonal = pooled(
        arm_cells(subset_gated, lambda r: off_target_directions(r["concept"]))
    )
    ordering = contrast(
        subset_diagonal, new_pool,
        "pooled non-subset off-target vs the subset diagonal (rejected option (b), "
        "descriptive continuity with M3 — never gating in M4)",
    )

    fractions = [
        sum(r["cells"][condition_name(w)]["produced"]
            for w in off_target_directions(r["concept"]))
        / len(off_target_directions(r["concept"]))
        for r in gate_arm
    ]
    total = sum(fractions)
    floor_k = int(math.floor(total))
    floor_lo, floor_hi = wilson(floor_k, n_arm)
    cluster_floor = {
        "readout": (
            "cluster-collapsed per-cell survival on the new pool (M3's F15 "
            "readout, reported for comparability — NEVER gating in M4)"
        ),
        "sum_of_fractions": total,
        "mean_survival_fraction": (total / n_arm) if n_arm else None,
        "k": floor_k, "n": n_arm, "wilson_95": [floor_lo, floor_hi],
        "reference_line": CLUSTER_FLOOR_REFERENCE,
        "below_reference_line": n_arm > 0 and floor_lo < CLUSTER_FLOOR_REFERENCE,
    }

    # --- the descriptive package ---------------------------------------------
    row_profiles = {}
    for prime in SUBSET:
        non_subset_cells = [r["cells"][condition_name(prime)] for r in gate_arm]
        row_profiles[prime] = {
            "category": categories[prime],
            "stratum": next(s for s, m in SUBSET_STRATA.items() if prime in m),
            "diagonal": pooled([r["cells"][condition_name(prime)]
                                for r in gated_by_concept.get(prime, [])]),
            "collateral_non_subset": pooled(non_subset_cells),
            "collateral_non_subset_within_category": pooled([
                r["cells"][condition_name(prime)] for r in gate_arm
                if r["category"] == categories[prime]
            ]),
            "collateral_non_subset_cross_category": pooled([
                r["cells"][condition_name(prime)] for r in gate_arm
                if r["category"] != categories[prime]
            ]),
            "collateral_subset": pooled([
                r["cells"][condition_name(prime)] for r in subset_gated
                if r["concept"] != prime
            ]),
        }

    column_profiles = {}
    for concept, group in sorted(by_concept.items()):
        rows = gated_by_concept.get(concept, [])
        column_profiles[concept] = {
            "category": categories[concept],
            "in_subset": concept in SUBSET,
            "items_run": len(group),
            "gated_items": len(rows),
            "clean": pooled([r["cells"]["clean"] for r in rows]),
            "diagonal": pooled(
                [r["cells"][condition_name(concept)] for r in rows]
                if concept in SUBSET else []
            ),
            "fragility": pooled(arm_cells(rows, lambda r: off_target_directions(r["concept"]))),
            "survives_all_deletions": sum(
                survives_all(r, off_target_directions(r["concept"])) for r in rows
            ),
        }

    strip = []
    for prime in SUBSET:
        for concept, group in sorted(by_concept.items()):
            if prime == concept:
                continue
            rows = gated_by_concept.get(concept, [])
            strip.append({
                "prime": prime, "probe": concept,
                "in_subset_probe": concept in SUBSET,
                "same_category": categories[prime] == categories[concept],
                "cell": pooled([r["cells"][condition_name(prime)] for r in rows]),
            })

    by_name = {r["name"]: r for r in records}
    confound_cells = []
    for prime, name in confounds:
        record = by_name.get(name)
        cell = record["cells"][condition_name(prime)] if record else None
        confound_cells.append({
            "prime": prime, "item": name,
            "probe_concept": record["concept"] if record else None,
            "gated": bool(record and record["gate_span"]),
            "in_gate_arm": bool(record and record["gate_span"] and not record["in_subset"]),
            "produced_under_prime": cell["produced"] if cell else None,
            "greedy_3_under_prime": cell["greedy_3"] if cell else None,
            "clean_greedy_3": record["cells"]["clean"]["greedy_3"] if record else None,
        })

    residual_cells = [
        {"item": r["name"], "concept": r["concept"], "condition": name,
         "greedy_3": cell["greedy_3"], "in_gate_arm": r["gate_span"] and not r["in_subset"]}
        for r in records
        for name, cell in r["cells"].items()
        if cell["residual"]
    ]

    recorded_in_m1 = [
        r for r in gate_arm if r["control"] in SUBSET
    ]
    ceiling_misses = [
        r["name"] for r in recorded_in_m1
        if not r["cells"][condition_name(r["control"])]["produced"]
    ]

    mass_rows = [r for r in gate_arm if r["mass_channel_eligible"]]

    def mean_mass(rows, directions_for) -> float | None:
        cells = arm_cells(rows, directions_for)
        return sum(c["concept_mass"] for c in cells) / len(cells) if cells else None

    mass_texture = {
        "mass_channel_n_gate_arm_items": len(mass_rows),
        "clean": (sum(r["cells"]["clean"]["concept_mass"] for r in mass_rows) / len(mass_rows)
                  if mass_rows else None),
        "new_pool_off_target": mean_mass(
            mass_rows, lambda r: off_target_directions(r["concept"])
        ),
        "subset_diagonal": (
            sum(r["cells"][condition_name(r["concept"])]["concept_mass"]
                for r in subset_gated if r["mass_channel_eligible"])
            / len([r for r in subset_gated if r["mass_channel_eligible"]])
            if any(r["mass_channel_eligible"] for r in subset_gated) else None
        ),
    }

    return {
        "competence": {
            "items_run": len(records),
            "gate_span": len(gated),
            "gate_arm_n": n_arm,
            "gate_arm_concepts": len(arm_concepts),
            "zero_gated_non_subset_concepts": sorted(
                c for c, rows in by_concept.items()
                if c not in SUBSET and not gated_by_concept.get(c)
            ),
            "gate_first_token_texture": sum(r["gate_first_token"] for r in records),
            "gate_verbatim_p": sum(r["gate_verbatim_p"] for r in records),
        },
        "clean_cell": pooled([r["cells"]["clean"] for r in gated]),
        "new_pool_arms": {
            "off_target": new_pool,
            "within_category": within,
            "cross_category": cross,
            "subset_diagonal": subset_diagonal,
            "subset_off_diagonal": subset_off_diagonal,
        },
        "vocabulary_sparing": {
            "gate_arm": gate,
            "bar": SURVIVAL_LOWER_BOUND,
            "clears_bar": n_arm > 0 and gate["wilson_95"][0] >= SURVIVAL_LOWER_BOUND,
            "underpowered": n_arm < MIN_N,
            "conservative_reads": conservative_reads,
            "cluster_mean_floor": cluster_floor,
            "ordering_contrast": ordering,
        },
        "gate_arm_ceiling": {
            "note": (
                "cells already recorded in M1 (the item's frozen control direction "
                "is a prime) — their outcomes were fixed before the run, so their "
                "misses cap the arm. A fact about the arm, never evidence for the gate."
            ),
            "cells_recorded_in_m1": len(recorded_in_m1),
            "misses": ceiling_misses,
            "ceiling": n_arm - len(ceiling_misses),
            "n": n_arm,
        },
        "strip": strip,
        "row_profiles": row_profiles,
        "column_profiles": column_profiles,
        "cross_mention_cells": confound_cells,
        "residual_cells": residual_cells,
        "concept_mass_texture": mass_texture,
    }


def wrong_opening_degeneracy(cells: list[dict], tokenizer) -> dict:
    """D20's dispositive guard, carried verbatim from M3's D17 (itself M2's D14):
    the most common first token among this arm's **non-produced** cells, with the
    share taken against the arm's full cell count — "at least half this arm's
    answers are the same *wrong* opening". Under D9(b) the raw all-answers share
    stops meaning pathology, because a correct answer may legitimately open with
    a shared fragment; that raw guard is recorded beside as texture."""
    missed = [cell["greedy_id"] for cell in cells if not cell["produced"]]
    if not missed or not cells:
        return {"attractor_token": None, "share": 0.0, "collapsed": False,
                "non_produced": len(missed), "n_cells": len(cells)}
    token, count = Counter(missed).most_common(1)[0]
    share = count / len(cells)
    return {
        "attractor_token": tokenizer.decode([token]),
        "share": share,
        "collapsed": share >= COLLAPSE_SHARE,
        "non_produced": len(missed),
        "n_cells": len(cells),
    }


# --- main ---------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--lens", required=True, help="fitted lens artifact (*.pt)")
    parser.add_argument("--m1", default=None, help="recorded M1 results JSON to cross-check against")
    parser.add_argument("--m3", default=None, help="recorded M3 results JSON to cross-check against")
    parser.add_argument("--out", default=None, help="results JSON path")
    parser.add_argument("--dry-run", action="store_true", help="validate + plan, then stop")
    parser.add_argument(
        "--device", default="auto", choices=("auto", "mps", "cpu"),
        help="cpu keeps a smoke run off the GPU while something else owns it",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="grade only the first N items — SMOKE ONLY, never a result",
    )
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        fail_invalid(f"--limit must be a positive item count, got {args.limit}")

    if args.device == "auto":
        device = "mps" if torch.backends.mps.is_available() else "cpu"
    else:
        device = args.device
    certified, uncertified_reasons = certified_environment(device)

    # PR #7 review F6, carried: everything validatable is validated BEFORE the
    # checkpoint loads, so a wrong-arm exit or a --dry-run never pays for a load.
    spec = SubjectSpec(args.model_id)
    tok = transformers.AutoTokenizer.from_pretrained(args.model_id)
    try:
        artifact = torch.load(args.lens, map_location="cpu", weights_only=True)
    except (FileNotFoundError, OSError, RuntimeError, torch.serialization.pickle.UnpicklingError) as exc:
        fail_invalid(f"lens artifact {args.lens} could not be loaded: {exc}")
    band, m1_recorded, m3_recorded, bars = validate(args, artifact, spec, tok)
    m1_path = args.m1 or m1_path_for(args.model_id)
    m3_path = args.m3 or m3_path_for(args.model_id)

    thirds = sub_band_thirds(band)
    late = thirds["late"]
    conditions = plan_conditions(late)
    items = load_strip_items()
    categories = concept_categories(items)
    surfaces = expected_recorded_cells(items)

    directions = list(PLANNED_DIRECTIONS)
    missing_forms = [w for w in directions if not token_forms(w, tok)]
    if missing_forms:
        fail_invalid(
            f"no single-token unembed row exists for direction word(s) "
            f"{missing_forms} — the strip cannot key their direction"
        )

    planned, dropped = [], []
    for item in items:
        forms = {
            "concept": token_forms(item["concept"], tok),
            "bare_single_token": bare_form_is_single_token(item["concept"], tok),
        }
        if not forms["concept"]:
            dropped.append({"name": item["name"], "missing": ["concept"]})
        else:
            planned.append((item, forms))

    cells_planned = planned_cells(conditions, [item for item, _ in planned])
    print(
        f"validated: {args.model_id} n_layers={spec.n_layers}, lens n_prompts="
        f"{artifact['n_prompts']}, band L{band[0]}–L{band[-1]} | late third "
        f"L{late[0]}–L{late[-1]} (width {len(late)}), λ={STRIP_LAMBDA:g}, k=1 | "
        f"strip {len(SUBSET)} primes × {len(planned)} items | items "
        f"{len(planned)} gradable / {len(dropped)} dropped | cells "
        f"{cells_planned} ({len(planned)} clean + {len(planned) * len(SUBSET)} "
        f"ablated) | re-certification {surfaces['m1_cells']} M1 cells / "
        f"{surfaces['m3_cells']} M3 cells | M1 {m1_path} | M3 {m3_path} | "
        "environment "
        + ("CERTIFIED" if certified else "UNCERTIFIED: " + "; ".join(uncertified_reasons))
    )
    print(
        f"  D22 bars: all {bars['words_checked']} scored + direction words fit the "
        f"{SPAN_TOKENS}-token span in both forms (worst "
        f"{bars['worst_form_length']}) and are pure ASCII | D21 cross-mention "
        "pairs: " + ", ".join(f"{p}→{n}" for p, n in CROSS_MENTION_PAIRS)
    )
    if args.dry_run:
        print("DRY-RUN: inputs valid; no trials performed; no checkpoint loaded")
        raise SystemExit(0)

    if args.limit is not None:
        planned = planned[: args.limit]

    print(f"loading {args.model_id} (fp32, {device})")
    hf = transformers.AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=torch.float32
    ).to(device)
    subject = SubjectModel(hf, tok)
    if (subject.n_layers, subject.d_model) != (spec.n_layers, spec.d_model):
        fail_invalid(
            f"loaded checkpoint is {subject.n_layers} layers / d_model "
            f"{subject.d_model}, but its config validated as {spec.n_layers} / "
            f"{spec.d_model} — validation and measurement disagree"
        )

    unembed_rows = hf.lm_head.weight.detach()
    rows = {w: unembed_rows[token_forms(w, tok)[0]] for w in directions}
    vectors = lens_vectors(artifact["J"], late, rows, device)

    store: dict[str, dict] = {}
    grade(planned, conditions, subject, vectors, store, "recorded")
    records = [store[item["name"]] for item, _ in planned]

    crosschecks = {}
    for milestone, path, recorded, checker in (
        ("M1", m1_path, m1_recorded, m1_crosscheck),
        ("M3", m3_path, m3_recorded, m3_crosscheck),
    ):
        mismatches, texture = checker(records, recorded)
        crosschecks[milestone] = {
            "results": path, "gate_bearing": certified,
            "mismatches": mismatches[:20], "n_mismatches": len(mismatches), **texture,
        }
        print(
            f"\n{milestone} CROSS-CHECK: {'PASS' if not mismatches else 'MISMATCH'} — "
            f"{len(mismatches)} mismatches over {texture['cells_checked']} reused "
            f"cells ({texture['items_checked']}/{texture['items_expected']} items) "
            f"| concept_mass exact {texture['mass_cells_equal']}/"
            f"{texture['cells_checked']} | "
            + ("GATE-BEARING (certified environment)" if certified
               else "not gate-bearing (uncertified environment)")
        )
        for problem in mismatches[:20]:
            print(f"  {problem}")
        if mismatches and certified:
            fail_invalid(
                f"{len(mismatches)} strip cells disagree with the recorded "
                f"{milestone} run {path} on the certified environment — the "
                "instrument drifted (D19); no new cell was read"
            )
        if args.limit is None and (
            texture["items_checked"] != texture["items_expected"]
            or texture["cells_checked"] != texture["cells_expected"]
        ):
            fail_invalid(
                f"{milestone} cross-check compared "
                f"{texture['items_checked']}/{texture['items_expected']} items and "
                f"{texture['cells_checked']}/{texture['cells_expected']} cells — a "
                "partial cross-check is not a re-certification (D19)"
            )
        if mismatches:
            print(
                "  ^ recorded, NOT gate-bearing: bit-for-bit reproduction is a "
                "property of the certified stack, not of the instrument (D19, scoped)"
            )

    grade(planned, conditions, subject, vectors, store, "new-cells")

    package = strip_package(records, categories, tok, list(CROSS_MENTION_PAIRS))
    gated = [r for r in records if r["gate_span"]]
    gate_arm = [r for r in gated if not r["in_subset"]]
    subset_gated = [r for r in gated if r["in_subset"]]

    arms = {
        "clean": [r["cells"]["clean"] for r in gated],
        "new_pool_off_target": arm_cells(
            gate_arm, lambda r: off_target_directions(r["concept"])
        ),
        "subset_diagonal": [r["cells"][condition_name(r["concept"])] for r in subset_gated],
        "subset_off_diagonal": arm_cells(
            subset_gated, lambda r: off_target_directions(r["concept"])
        ),
    }
    for prime in SUBSET:
        arms[f"row_{prime}"] = [r["cells"][condition_name(prime)] for r in gate_arm]
    for concept in sorted({r["concept"] for r in gated}):
        rows = [r for r in gated if r["concept"] == concept]
        arms[f"column_{concept}"] = arm_cells(
            rows, lambda r: off_target_directions(r["concept"])
        )
    guard_wrong_opening = {name: wrong_opening_degeneracy(cells, tok)
                           for name, cells in arms.items()}
    guard_all_answers = {
        name: degeneracy([cell["greedy_id"] for cell in cells], tok)
        for name, cells in arms.items()
    }
    for record in records:
        for cell in record["cells"].values():
            del cell["greedy_id"]

    # D20's disposition, scoped to the single arm the gate reads.
    dispositive = ("new_pool_off_target",)
    degenerate_arms = [a for a in dispositive if guard_wrong_opening[a]["collapsed"]]
    row_caveats = [p for p in SUBSET if guard_wrong_opening[f"row_{p}"]["collapsed"]]
    column_caveats = [c for c in sorted({r["concept"] for r in gated})
                      if guard_wrong_opening[f"column_{c}"]["collapsed"]]
    sparing = package["vocabulary_sparing"]
    sparing["degenerate_gate_arms"] = degenerate_arms
    sparing["subset_diagonal_collapsed_tag"] = guard_wrong_opening["subset_diagonal"]["collapsed"]
    sparing["row_texture_caveats"] = row_caveats
    sparing["column_texture_caveats"] = column_caveats
    verdict = strip_verdict(
        certified, degenerate_arms, sparing["gate_arm"],
        sparing["conservative_reads"], args.limit,
    )
    sparing["verdict"] = verdict

    results = {
        "milestone": "M4",
        "model_id": args.model_id,
        "lens": args.lens,
        "lens_n_prompts": artifact["n_prompts"],
        "band": band,
        "thirds": thirds,
        "ablated_layers": late,
        "lambda": STRIP_LAMBDA,
        "mode": "gate (survives-all-12 on the gated non-subset items) + descriptive (the strip)",
        "environment": {
            "device": device,
            "torch": torch.__version__,
            "transformers": transformers.__version__,
            "certified": certified,
            "uncertified_reasons": uncertified_reasons,
        },
        "protocol": {
            "instructions": {"naming": NAMING_Q},
            "primes": list(SUBSET),
            "subset_strata": SUBSET_STRATA,
            "concept_categories": categories,
            "conditions": [
                {k: c[k] for k in ("name", "group", "direction", "layers", "lam")}
                for c in conditions
            ],
            "cells_planned": cells_planned,
            "recorded_surfaces": surfaces,
            "cross_mention_pairs": [list(p) for p in CROSS_MENTION_PAIRS],
            "gate": "greedy-span naming-only under D9(b); first-token recorded beside",
            "readback_tol": READBACK_TOL,
            "min_n": MIN_N,
            "collapse_share": COLLAPSE_SHARE,
            "p_name_floor": P_NAME_FLOOR,
            "span_tokens": SPAN_TOKENS,
            "survival_lower_bound": SURVIVAL_LOWER_BOUND,
            "cluster_floor_reference": CLUSTER_FLOOR_REFERENCE,
            "run_time_bars": bars,
            "items": ITEMS_PATH,
            "gate_wording": GATE_WORDING,
        },
        "dropped_single_token_prefilter": dropped,
        "m1_crosscheck": crosschecks["M1"],
        "m3_crosscheck": crosschecks["M3"],
        "smoke_limit": args.limit,
        **package,
        "degeneracy_guard_wrong_opening": guard_wrong_opening,
        "degeneracy_guard_all_answers": guard_all_answers,
        "items": records,
    }

    smoke = f"SMOKE (limit={args.limit}) — not a result — " if args.limit else ""
    gate = sparing["gate_arm"]
    pool = package["new_pool_arms"]
    print(
        f"\nM4 VOCABULARY-SPARING VERDICT ({args.model_id}): {smoke}gated "
        f"{package['competence']['gate_span']}/{len(records)} items, gate arm "
        f"(gated non-subset) n={gate['n']} | survives-all-{len(SUBSET)} "
        f"{gate['k']}/{gate['n']}"
        + (f" = {gate['rate']:.3f} [{gate['wilson_95'][0]:.3f},"
           f"{gate['wilson_95'][1]:.3f}]" if gate["n"] else "")
        + f" vs bar {SURVIVAL_LOWER_BOUND} → {verdict}"
    )
    for read in sparing["conservative_reads"]:
        print(
            f"  {read['read']} (pre-registered, never dispositive): "
            f"{read['k']}/{read['n']}"
            + (f" = {read['rate']:.3f} [{read['wilson_95'][0]:.3f},"
               f"{read['wilson_95'][1]:.3f}]" if read["n"] else "")
        )
    floor = sparing["cluster_mean_floor"]
    ordering = sparing["ordering_contrast"]["newcombe_offtarget_minus_diagonal_naming"]
    print(
        f"  new pool (texture, each item 12×): off-target {pool['off_target']['hits']}/"
        f"{pool['off_target']['n']}, within-category {pool['within_category']['hits']}/"
        f"{pool['within_category']['n']}, cross-category "
        f"{pool['cross_category']['hits']}/{pool['cross_category']['n']} | subset "
        f"diagonal {pool['subset_diagonal']['hits']}/{pool['subset_diagonal']['n']}"
    )
    print(
        f"  M3-comparable cluster-mean floor (never gating): {floor['k']}/{floor['n']}"
        + (f" → [{floor['wilson_95'][0]:.3f}, {floor['wilson_95'][1]:.3f}]"
           if floor["n"] else "")
        + f" vs reference {CLUSTER_FLOOR_REFERENCE} | ordering contrast "
        f"{ordering[0]:+.3f} [{ordering[1]:+.3f}, {ordering[2]:+.3f}]"
    )
    ceiling = package["gate_arm_ceiling"]
    print(
        f"  pre-registered ceiling (M1-recorded gate-arm cells): "
        f"{ceiling['ceiling']}/{ceiling['n']} — {ceiling['cells_recorded_in_m1']} "
        f"cells fixed pre-run, misses: {', '.join(ceiling['misses']) or 'none'}"
    )
    print(
        "  row collateral (deleting A, over the gated non-subset items): "
        + " ".join(
            f"{p}={package['row_profiles'][p]['collateral_non_subset']['hits']}/"
            f"{package['row_profiles'][p]['collateral_non_subset']['n']}" for p in SUBSET
        )
    )
    fragile = sorted(
        (c for c, v in package["column_profiles"].items()
         if v["fragility"]["n"] and v["fragility"]["hits"] < v["fragility"]["n"]),
        key=lambda c: package["column_profiles"][c]["fragility"]["rate"],
    )
    print(
        "  most fragile probe columns (finding 1's out-of-sample test): "
        + (" ".join(
            f"{c}{'*' if package['column_profiles'][c]['in_subset'] else ''}="
            f"{package['column_profiles'][c]['fragility']['hits']}/"
            f"{package['column_profiles'][c]['fragility']['n']}"
            for c in fragile[:12]) or "no damaged column")
        + "   (* subset concept)"
    )
    print(
        f"  D9(b) residual cells recorded this run: {len(package['residual_cells'])} "
        f"({sum(c['in_gate_arm'] for c in package['residual_cells'])} in the gate arm)"
        " | D21 cross-mention cells: "
        + " ".join(
            f"{c['prime']}→{c['item']}="
            + ("n/a" if c["produced_under_prime"] is None
               else ("named" if c["produced_under_prime"] else "MISS"))
            + ("" if c["in_gate_arm"] else " (ungated)")
            for c in package["cross_mention_cells"]
        )
    )
    if row_caveats or column_caveats:
        print(
            f"  degeneracy texture (never dispositive): rows "
            f"{', '.join(row_caveats) or 'none'} | columns "
            f"{', '.join(column_caveats) or 'none'}"
        )

    if args.limit and not args.out:
        print("smoke run: results not written (pass --out to keep them)")
        raise SystemExit(0)
    out = args.out or ("results/m4-strip-" + args.model_id.split("/")[-1].lower() + ".json")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w") as f:
        json.dump(results, f, indent=1)
    print(f"results written to {out}")
    raise SystemExit(0)


if __name__ == "__main__":
    main()

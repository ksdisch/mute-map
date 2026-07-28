"""m3_matrix.py — M3: the specificity matrix (what *else* breaks when you delete
one word's direction?).

Cut from `m2_depth.py`, which was cut from `m1_battery.py`, which was cut from
the certified `m0_anchor.py` (untouched post-gate, D2/M0). The measurement
machinery is unchanged — same naming template, same chat encoding, same k = 1
J-lens projection removal with the runtime read-back, same frozen band and
thirds, same D9(b) oracle, same Wilson/Newcombe rulers — so the subset's
`clean` / `primed_late` / `control_late` cells must reproduce
`results/m1-battery-*.json` cell-for-cell, which this runner checks before it
reads a single off-diagonal cell (D16a).

What M3 adds, each frozen in `docs/M3-BRIEF.md` before any run:

- **the full 12 x 12 prime x probe matrix (D15a + D16a)** — M1 and M2 measured
  specificity with ONE control direction per concept. M3 deletes each of the 12
  subset concepts' directions in turn and probes all 12 concepts' items, so
  every ordered pair (A, B) gets a cell: the diagonal is the mute itself, the
  132 off-diagonal ordered pairs are the collateral map. Depth and dose are held
  fixed at the switch's home (the late third, lambda = 1, k = 1), so every cell
  differs from every other in exactly one thing — *which* direction was removed.
- **the gate on the pooled arms (D17)** — MATRIX-SPECIFIC iff off-diagonal
  naming CI-cleanly exceeds diagonal naming, AND the same holds restricted to
  the within-category off-diagonal (the S4b-comparable arm), with the
  pre-declared ON A DAMAGED FLOOR qualifier when the collateral floor is low.
- **the run-time instrument bars (D18a)** — the D9(b)/D10 soundness premises
  ("3 tokens >= the longest form", "the roster is pure ASCII") are checked on the
  subject's own tokenizer before any trial instead of being inherited as
  assumptions. `oracle.py` itself is untouched: it is byte-shared with
  `m1_rescore.py` and `m2_depth.py` and must stay identical.

Owned divergences from `m2_depth.py` (M3-BRIEF deviations table + dispositions):

- **no partial-lambda operator.** M3 is lambda = 1 only, so the dose code does not
  come across; every cell runs through M1's verbatim full-ablation path.
- **inputs are validated BEFORE the checkpoint loads** (PR #7 review F6's
  disposition): a `--dry-run` or a wrong-arm exit touches no model. The subject's
  shape comes from its config for validation and is re-asserted against the
  loaded `SubjectModel` before any trial. `validate()` also *returns* the parsed
  M1 artifact so `main()` never parses it twice.
- **`m2_depth.GATE_WORDING` is not imported or edited** — M2's wording stays
  byte-frozen with M2's artifacts. M3 freezes its own below.

Run:  uv run python -u m3_matrix.py \
          --model-id Qwen/Qwen2.5-1.5B-Instruct \
          --lens lenses/qwen2.5-1.5b-instruct-n100.pt
"""
from __future__ import annotations

import argparse
import json
import math
import os
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
from m1_battery import ITEMS_PATH, load_items, sub_band_thirds
from oracle import (
    ORACLE_WORDING,
    SPAN_TOKENS,
    says_concept_anywhere,
    says_concept_prefix,
)
from stats import excludes_zero, newcombe_diff, wilson
from subject import SubjectModel

#: D15(a): M2's pre-registered 12, reused VERBATIM — the subset was frozen by
#: D11's stratified rule before any M2 cell existed, so M3's selection surface
#: was pre-registered two milestones ago. Copied rather than imported, per the
#: standing cut-from-your-predecessor rule; a test pins it equal to M2's.
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
CLUES_PER_CONCEPT = 3
EXPECTED_SUBSET_ITEMS = len(SUBSET) * CLUES_PER_CONCEPT  # 36

#: D16(a): the six concepts whose M1 control direction is NOT a subset member,
#: run on their own 3 items only. They are not matrix cells: they exist to
#: complete the recorded 108-cell re-certification surface, and they give
#: October and silver — the two subset concepts with no same-category sibling in
#: the matrix — their only same-category collateral sample.
CONTROL_EXTRA_DIRECTIONS = ("February", "Saturn", "Mercury", "guitar", "drum", "platinum")
#: Every word whose direction this run ablates — the roster D18(a)'s bars read.
PLANNED_DIRECTIONS = SUBSET + CONTROL_EXTRA_DIRECTIONS

NAMING_Q = (  # verbatim from the certified m0_anchor.py, via m1_battery/m2_depth
    'Consider this sentence: "{clue}"\n\n'
    "Which {noun} is the sentence describing? Answer with just the name."
)
#: M3 holds depth and dose fixed at the switch's home: full removal, k = 1.
MATRIX_LAMBDA = 1.0
#: The M1 conditions the shared cells reproduce, in M1's own names.
M1_SHARED_CONDITIONS = ("clean", "primed_late", "control_late")
#: D16: the cross-check compares raw recorded strings, so it is oracle-independent.
M1_CELL_FIELDS = ("greedy", "greedy_3")
#: D17's pre-registered collateral-floor constant. Deliberately NOT fitted to any
#: recorded cell, and never dispositive — it scopes a verdict, never creates one.
FLOOR_LOWER_BOUND = 0.5
P_NAME_FLOOR = 0.85  # paper's verbatim naming threshold — reported, never gating
#: The stack the anchor's bit-for-bit reproduction was certified on (M0, D1).
CERTIFIED_DEVICE = "mps"
CERTIFIED_PINS = {"torch": "2.13.0", "transformers": "5.13.1"}

#: Every gate's wording, frozen as code before any M3 run (project guardrail:
#: "pre-commit gates as code — wording included"). Written verbatim into the
#: results JSON so prose and code can never drift. M1's and M2's wordings are
#: NOT imported: each stays byte-frozen with its own artifacts.
GATE_WORDING = {
    "oracle": ORACLE_WORDING,
    "competence": (
        "D9(b) + D6(a) item-level greedy-span naming-only gate, carried verbatim "
        "from M2: an item enters the gated set iff its CLEAN naming span "
        "satisfies the D9(b) oracle above. Gating is a property of the clean arm "
        "alone, decided once per item and DIRECTION-INDEPENDENT, so every one of "
        "this run's matrix cells shares ONE gated set — which is what makes the "
        "rows, the columns and the two pooled arms comparable. Gating is "
        "per-subject. M1's first-token gate is computed and recorded beside it as "
        "texture, never gating here. The paper-style verbatim-P rate (clean "
        "concept mass >= 0.85) is reported alongside as texture, never gating; "
        "note it is floor-pinned by construction for concepts whose emitted bare "
        "spelling has no single-token form (the mass-channel scope, D13)."
    ),
    "specificity": (
        "D17, pre-committed before any M3 run. Per subject, on the pooled gated "
        "cell — gating is the clean arm under D9(b), decided once per item and "
        "direction-independent, so every matrix cell shares one gated set: "
        "MATRIX-SPECIFIC iff BOTH, per subject on the pooled gated cell: (1) "
        "naming under the pooled OFF-DIAGONAL cells (every gated item under each "
        "of the 11 directions that are not its own concept's) minus naming under "
        "the pooled DIAGONAL cells (each gated item under its own concept's "
        "direction) is positive with its Newcombe 95% CI excluding 0; AND (2) the "
        "same contrast restricted to the WITHIN-CATEGORY off-diagonal cells (each "
        "gated item under its same-category subset siblings' directions only) is "
        "likewise positive with its Newcombe 95% CI excluding 0 — the "
        "S4b-comparable arm, since the lineage's control has always been "
        "same-category. Both arms of clause (2) — its off-diagonal pool AND its "
        "diagonal — are restricted to the gated items whose concept has AT LEAST "
        "ONE within-category subset sibling; October's and silver's items drop "
        "from this clause by construction, not by choice (they have no sibling, "
        "so their 'within-category collateral' is an empty set — brief review "
        "F10). Stated per arm so the runner cannot guess (brief review F13): "
        "clause (2) compares the within-category off-diagonal CELLS, n = 96 / 100 "
        "/ 101 (0.5B / 1.5B / 3B), against the DIAGONAL CELLS OF THE SAME "
        "RESTRICTED ITEM SET, n = 24 / 28 / 29 — MIN_N guards that diagonal n — "
        "while the per-item 24-vs-24 collapse is the separately pre-registered, "
        "never-dispositive effective-n check (honesty section). The M3 verdict is "
        "the AND over 1.5B and 3B (computed by m3_verdict.py); 0.5B runs and is "
        "reported under its standing any-direction-damage frame, never "
        "gate-bearing. Pooled diagonal gated n < MIN_N = 20 => pre-declared "
        "UNDERPOWERED and no specificity claim. COLLATERAL-FLOOR QUALIFIER, "
        "pre-committed: the ordering contrasts above cannot by themselves "
        "distinguish a per-concept switch from graded damage that is merely worse "
        "on-diagonal, so the verdict — whatever it is — carries the pre-declared "
        "qualifier ON A DAMAGED FLOOR (the any-direction-damage frame applied to a "
        "gate-bearing subject) if the floor readout's Wilson 95% lower bound is "
        "below 0.5. The floor readout is the CLUSTER-COLLAPSED PER-CELL SURVIVAL "
        "(re-defined at the brief's round-4 review, F15, keeping the honest "
        "item-level n its F11 re-definition introduced): each gated item "
        "contributes its FRACTION of the 11 off-diagonal deletions survived, and "
        "the readout is wilson(k, n) with k = floor(the sum of those fractions) "
        "and n = the gated items (28 / 34 / 32). This keeps the quantity the floor "
        "is about — the per-cell collateral rate (the 0.57-0.68 damage band still "
        "fires: at those rates on n = 28 the lower bound reads 0.39-0.49) — while "
        "refusing both dishonest denominators: the pooled rate at n = 308 "
        "under-fires (its 11x-inflated n narrows the interval — F11), and a "
        "survives-all-11 conjunction is decided by the unmeasured correlation "
        "structure across the 11 deletions rather than by damage (per-direction "
        "survival 0.882 reads ~0.88 if failures cluster on the same items and "
        "0.882^11 ~ 0.25 if independent — F15). A binomial interval on a mean of "
        "bounded fractions is approximate by construction — owned, and acceptable "
        "only because the qualifier is never dispositive. The pooled per-cell "
        "reading is reported beside as the permissive comparison. The qualifier "
        "scopes the claim and can never create or rescue a verdict. The 0.5 floor "
        "is a pre-registered constant, deliberately NOT fitted to any recorded "
        "cell; 0.5B's exclusion from gate-bearing rests on the standing "
        "pre-declared scale frame, never on this qualifier. Every matrix cell "
        "ablates the subject's identical late-third layer set at lambda = 1, "
        "k = 1, so the compared arms differ ONLY IN WHICH DIRECTION IS REMOVED — "
        "never in depth, layer count, or dose (PR #7 review F2's tier-width "
        "caveat, retired structurally and stated here so it stays owned; if a "
        "later stage re-introduces tiers, the caveat clause must come back with "
        "them). Clause (1) IS KICKOFF's 'diagonal suppression CI-cleanly exceeds "
        "off-diagonal collateral' in directly comparable proportions, by M2's "
        "algebra: suppression under arm X is the naming drop clean - naming_X on "
        "the same items, so suppression_diag - suppression_offdiag = "
        "naming_offdiag - naming_diag — the shared clean arm cancels, leaving the "
        "plain two-proportion comparison the ported ruler already decides."
    ),
    "descriptive": (
        "D17's descriptive package — never gate-bearing, Wilson CIs. The matrix "
        "itself: per-pair (A, B) cells are n <= 3 and are always descriptive. "
        "Reported beside, all pre-registered in the brief: the WITHIN-CATEGORY vs "
        "CROSS-CATEGORY split of the pooled off-diagonal (KICKOFF's named readout "
        "— the within-category arm is gate-bearing via clause (2); the "
        "cross-category arm and the full grid stay descriptive); per-direction ROW "
        "PROFILES (how much does deleting A damage the other 11 — silver's row is "
        "the pre-registered interesting one) and per-concept COLUMN PROFILES (how "
        "fragile is B to other deletions); ASYMMETRY texture (A->B vs B->A); the "
        "18 out-of-subset control-direction cells (D16a), which are not matrix "
        "cells and are reported as texture; mean concept mass per cell under "
        "D13's standing scope (only items whose emitted bare spelling has a "
        "single-token form — `mass_channel_eligible`, carried per-item from M2's "
        "artifacts)."
    ),
    "run_time_bars": (
        "D18(a), pre-trial, on the subject's own tokenizer — the PR #7 F5 + F4 "
        "pins. (1) THE SPAN BAR: every planned direction word must tokenize to "
        "<= oracle.SPAN_TOKENS = 3 in BOTH its bare and its leading-space form, "
        "max(len(tok(w)), len(tok(' ' + w))) <= SPAN_TOKENS, else the run exits "
        "INVALID. This is D9(b)/D10's whole soundness premise — a prefix hit "
        "cannot be hidden by span truncation BECAUSE every roster word fits the "
        "span — checked where it can drift (a tokenizer revision, a future roster "
        "edit) instead of inherited as an assumption. Widened from bare-form-only "
        "at the brief's freeze (follow-up F5): the recorded span holds the model's "
        "EMITTED continuation, normally the space-prefixed form, and bare length "
        "does not bound space-form length ('opal' is 1 token bare but 2 "
        "space-prefixed on all three tokenizers, the pinned unit-test case). (2) "
        "THE ASCII BAR: every planned direction word must be pure ASCII, else "
        "INVALID — `oracle._BOUNDARY` is `(?![A-Za-z0-9])`, so a non-ASCII "
        "continuation character would read as a word boundary and a longer "
        "non-ASCII word could score as a hit. M3 adds no vocabulary (every D15 "
        "branch draws from M1's frozen 60, all pure-ASCII spellings), so the rule "
        "does not change and the premise is pinned rather than assumed; the named "
        "future trigger is the S2 stretch's translations/synonyms lists, whose "
        "brief owes the boundary-class decision before freezing any non-ASCII "
        "list. `oracle.py` is UNTOUCHED by both bars: it is byte-shared with "
        "`m1_rescore.py` and `m2_depth.py` and must stay identical."
    ),
    "degeneracy": (
        "D17, carrying M2's D14 wide-oracle guard verbatim and re-scoping it to "
        "the arms this gate reads. The dispositive guard stays as D14 froze it: "
        "pool the first tokens of an arm's NON-PRODUCED cells only, share taken "
        "against the arm's full cell count ('at least half this arm's answers are "
        "the same WRONG opening'); the raw all-answers guard is recorded beside as "
        "texture. SCOPE: collapse in the pooled OFF-DIAGONAL arm — the surviving "
        "side the gate reads — => DEGENERATE, no MATRIX-SPECIFIC claim; collapse "
        "in the pooled DIAGONAL => TAG only (the expected mute signature, exactly "
        "`primed_late`'s standing treatment); `clean` stays off the dispositive "
        "list (it is the gate arm — the D14 F3 correction, carried); collapse "
        "inside any single direction's row or any per-pair cell is TEXTURE, "
        "attached to the descriptive readout it compromises (those cells are never "
        "verdict-bearing, and at n <= 3 a per-pair share is not evidence of "
        "anything)."
    ),
    "m1_crosscheck": (
        "D16(a), environment-scoped (carrying M2's D14 and M1's D5a/F7 verbatim), "
        "one generation deeper. The 108 cells this run shares with M1's recorded "
        "artifacts — `clean` (36), the DIAGONAL (= 36 `primed_late` cells) and the "
        "CONTROL cells (18 inside the matrix + the 18 out-of-subset extras) — are "
        "graded FIRST and compared to the recorded "
        "results/m1-battery-<subject>.json cell-for-cell on the raw recorded "
        "fields (`greedy` and `greedy_3` decoded strings) BEFORE any off-diagonal "
        "cell is read; `concept_mass` equality is recorded as texture, never "
        "gating. The comparison is on raw strings, so it is oracle-independent — "
        "D9 cannot soften it. On the certified environment — device 'mps' under "
        "the pinned stack (torch 2.13.0, transformers 5.13.1) — any mismatch is "
        "INVALID (exit 2). Off that environment the check still runs and is "
        "recorded but is NOT gate-bearing, and the whole run is pre-declared NOT A "
        "RESULT, which m3_verdict.py refuses. Coverage is a property of the run "
        "rather than of the environment, so the bar that all 36 subset items were "
        "actually compared is unscoped (M1 review F1's lesson)."
    ),
    "precedence": (
        "D17, frozen: NOT A RESULT > DEGENERATE > UNDERPOWERED > the contrast. "
        "Wrong-arm inputs exit INVALID before any trial — and, per PR #7 review "
        "F6's disposition, before the checkpoint is even loaded; `--dry-run` "
        "validates and stops; `--limit` is smoke, never a result; M3 refuses an M1 "
        "artifact that was itself not a result. The ON A DAMAGED FLOOR qualifier "
        "attaches to a contrast-level verdict (MATRIX-SPECIFIC or not shown) — it "
        "scopes a claim, so it has nothing to scope when precedence already "
        "withheld the claim; the floor readout itself is recorded on every run "
        "regardless. All M1/M2 patterns carried verbatim."
    ),
    "honesty": (
        "Owned, pre-committed. (1) Items within a concept share one lens "
        "direction, so item-level pooling overstates independence; the per-concept "
        "and per-pair maps are the honest granular views beside it. (2) The "
        "diagonal and off-diagonal arms are measured on the SAME gated items, but "
        "newcombe_diff is Newcombe's method 10 for two INDEPENDENT samples — for "
        "positively correlated paired arms that WIDENS the interval, so it cannot "
        "manufacture a false MATRIX-SPECIFIC verdict; it can only cost power. (3) "
        "MIN_N = 20 is applied to raw n, not to an effective n discounted for that "
        "clustering. (4) NEW IN M3, ANTI-CONSERVATIVE AND OWNED (brief review F3): "
        "the pooled off-diagonal REPEATS EACH GATED ITEM 11 TIMES (the "
        "within-category arm up to 5), which makes the gate's Newcombe interval "
        "NARROWER than the clustering justifies, not wider — worked on the "
        "recorded 0.5B rates, the inflated-n contrast reads +0.714 [+0.583, "
        "+0.762] where the honest per-item n gives +0.714 [+0.494, +0.847]. The "
        "pre-registered EFFECTIVE-N SANITY CHECK, reported beside the gate: each "
        "contrast recomputed with the repeated arm collapsed to one binary per "
        "gated item — for clause (1), 'survives ALL 11 off-diagonal deletions', "
        "n = the gated items (28 / 34 / 32); for clause (2), 'survives all "
        "within-category sibling deletions', n = the gated items with at least one "
        "within-category subset sibling (24 / 28 / 29), October's and silver's "
        "items excluded by construction, not by choice (review F10: with no "
        "sibling the conjunction is empty and True by fiat — it would have scored "
        "silver, the pre-registered non-specific anti-example, as a structural "
        "survivor). Note the collateral-floor qualifier uses the CLUSTER-MEAN "
        "collapse instead (F15), not this conjunction. If a pooled clause is "
        "CI-clean but its per-item collapse is not, the per-item numbers are the "
        "honest ones to quote. (5) Per-pair cells are n <= 3 and are always "
        "descriptive, never verdict-bearing (D7's logic, unchanged). (6) The "
        "category structure is lopsided by construction (6 countries / 2 planets / "
        "2 instruments / 1 month / 1 metal), so the within-category readout is "
        "mostly a countries story — 30 of the 34 within-category ordered pairs — "
        "and October and silver have no same-category sibling in the matrix at "
        "all; their recorded M1 control cells, run as re-certification texture "
        "under D16(a), are their only same-category collateral sample."
    ),
}


# --- the frozen subset --------------------------------------------------------

def load_subset_items(path: str = ITEMS_PATH) -> list[dict]:
    """M1's frozen battery, filtered to D15(a)'s 12 pre-registered concepts.

    Every guard in M1's loader runs first (roster shape, clue counts, fixed
    controls, leak test), so M3 cannot run against a drifted battery; then this
    adds the subset's own shape bars, plus M3's own: the 12 concepts' controls
    must partition exactly into the in-matrix six and the frozen out-of-subset
    six, so the +18 control-extra cells of D16(a) are a checked fact rather than
    a hard-coded hope.
    """
    items = [item for item in load_items(path) if item["concept"] in SUBSET]
    covered = {item["concept"] for item in items}
    missing = sorted(set(SUBSET) - covered)
    if missing:
        raise ValueError(
            f"{path} is missing pre-registered subset concept(s) {missing} — the "
            "frozen subset and the frozen battery have drifted apart"
        )
    if len(items) != EXPECTED_SUBSET_ITEMS:
        raise ValueError(
            f"subset drew {len(items)} items from {path}, expected "
            f"{EXPECTED_SUBSET_ITEMS} ({len(SUBSET)} concepts x {CLUES_PER_CONCEPT})"
        )
    strata = sorted(c for group in SUBSET_STRATA.values() for c in group)
    if strata != sorted(SUBSET):
        raise ValueError("SUBSET_STRATA does not partition SUBSET")
    outside = sorted({i["control"] for i in items} - set(SUBSET))
    if outside != sorted(CONTROL_EXTRA_DIRECTIONS):
        raise ValueError(
            f"the subset's out-of-subset control directions are {outside}, not the "
            f"frozen {sorted(CONTROL_EXTRA_DIRECTIONS)} — D16(a)'s +18 "
            "control-extra cells were pre-registered against the frozen pairings"
        )
    return items


def subset_categories(items: list[dict]) -> dict[str, str]:
    """concept -> category, read off the frozen items (never hard-coded)."""
    return {item["concept"]: item["category"] for item in items}


def within_category_siblings(concept: str, categories: dict[str, str]) -> list[str]:
    """The other SUBSET concepts sharing `concept`'s category — the directions
    clause (2) reads. October and silver have none, by construction."""
    return [
        other for other in SUBSET
        if other != concept and categories[other] == categories[concept]
    ]


# --- the condition plan -------------------------------------------------------

def condition_name(word: str) -> str:
    return f"ablate_{word}"


def plan_conditions(late: list[int]) -> list[dict]:
    """Every condition this run can grade: `clean`, the 12 matrix directions, and
    the 6 out-of-subset control-extra directions — all at the identical late
    third, all at lambda = 1, k = 1.

    Which of them apply to a given item is `applies_to`: the matrix directions
    apply to every item (that is what makes it a matrix), while a control-extra
    direction applies only to the 3 items of the concept it is the frozen control
    for. The M1-shared subset of an item's conditions is `is_m1_shared`, and
    those are graded first (D16a).
    """
    conditions = [
        {"name": "clean", "group": "clean", "direction": None, "layers": [], "lam": 0.0}
    ]
    for word in SUBSET:
        conditions.append({
            "name": condition_name(word), "group": "matrix", "direction": word,
            "layers": late, "lam": MATRIX_LAMBDA,
        })
    for word in CONTROL_EXTRA_DIRECTIONS:
        conditions.append({
            "name": condition_name(word), "group": "control_extra", "direction": word,
            "layers": late, "lam": MATRIX_LAMBDA,
        })
    return conditions


def applies_to(condition: dict, item: dict) -> bool:
    """A control-extra direction is graded only on the 3 items of the concept it
    is the frozen M1 control for — it completes the recorded control surface and
    is not a matrix cell. Everything else is graded on every item."""
    if condition["group"] == "control_extra":
        return condition["direction"] == item["control"]
    return True


def is_m1_shared(condition: dict, item: dict) -> bool:
    """Is this cell one M1 already recorded for this item? `clean` is M1's
    `clean`; the item's own concept direction is M1's `primed_late`; the item's
    frozen control direction is M1's `control_late`."""
    return condition["direction"] in (None, item["concept"], item["control"])


def conditions_for(conditions: list[dict], item: dict) -> tuple[list[dict], list[dict]]:
    """(M1-shared conditions, everything else) for one item, in frozen order —
    the split that makes "before any off-diagonal cell is read" literally true."""
    applicable = [c for c in conditions if applies_to(c, item)]
    return (
        [c for c in applicable if is_m1_shared(c, item)],
        [c for c in applicable if not is_m1_shared(c, item)],
    )


def planned_cells(conditions: list[dict], items: list[dict]) -> int:
    """Total clean + ablated cells this plan grades — the wall-clock unit. Under
    D15(a)/D16(a) this is 486 per subject: 36 clean + 432 matrix + 18
    control-extra."""
    return sum(
        sum(1 for c in conditions if applies_to(c, item)) for item in items
    )


# --- the operator (M1's verbatim k = 1 full projection removal) ----------------

def lens_vectors(
    jacobians: dict[int, torch.Tensor],
    layers: list[int],
    rows: dict[str, torch.Tensor],
    device: str,
) -> dict[tuple[int, str], torch.Tensor]:
    """v = J_l^T u for every (layer, word) this run will ablate, computed once —
    M2's caching, carried verbatim (and certified inert by the same cross-check:
    a moved value would break bit-for-bit reproduction of the reused cells).
    Each Jacobian is moved to the device one layer at a time so the whole lens
    never has to be resident at once."""
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
    reading its direction from the precomputed table. Every M3 cell runs through
    this path (lambda = 1 everywhere), so the cells M1 already recorded are
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
                    f"M3 read-back failed at layer {layer}: surviving "
                    f"projection {worst:.2e} > {READBACK_TOL:.0e}"
                )
            return out.unsqueeze(0)

        edits[layer] = edit
    return edits


def edits_for(
    condition: dict, vectors: dict[tuple[int, str], torch.Tensor]
) -> dict[int, Edit] | None:
    """The edit set one condition applies: none for `clean`, otherwise the full
    ablation of that condition's own direction at the late third."""
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
    verbatim from M1/M2 (the cross-check compares it as texture). Floor-pinned by
    construction wherever the emitted bare spelling has no single-token form,
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


# --- D18(a): the run-time instrument bars -------------------------------------

def span_form_lengths(word: str, tokenizer) -> tuple[int, int]:
    """(bare token count, leading-space token count) — the two forms the span bar
    reads. The recorded span holds the model's *emitted* continuation, normally
    the space-prefixed form, and bare length does not bound space-form length."""
    return (
        len(tokenizer(word, add_special_tokens=False).input_ids),
        len(tokenizer(" " + word, add_special_tokens=False).input_ids),
    )


def check_run_time_bars(words: list[str], tokenizer) -> dict:
    """D18(a), pre-trial: the two premises D9(b)/D10's soundness rests on,
    checked on the subject's own tokenizer instead of inherited as assumptions.

    (1) every planned direction word fits the recorded span in BOTH its bare and
    its leading-space form; (2) every planned direction word is pure ASCII, the
    `oracle._BOUNDARY` premise. Either failure exits INVALID before any trial.
    Returns the measured lengths, recorded in the results JSON.
    """
    lengths = {word: span_form_lengths(word, tokenizer) for word in words}
    too_long = sorted(w for w, (bare, space) in lengths.items()
                      if max(bare, space) > SPAN_TOKENS)
    if too_long:
        detail = ", ".join(
            f"{w!r} bare={lengths[w][0]} space={lengths[w][1]}" for w in too_long
        )
        fail_invalid(
            f"D18 span bar: {detail} — max(bare, leading-space) exceeds "
            f"oracle.SPAN_TOKENS = {SPAN_TOKENS}, so a prefix hit could be hidden "
            "by span truncation and the D9(b)/D10 soundness premise does not hold "
            "on this tokenizer"
        )
    non_ascii = sorted(w for w in words if not w.isascii())
    if non_ascii:
        fail_invalid(
            f"D18 ASCII bar: {non_ascii} — `oracle._BOUNDARY` is ASCII-only "
            "([A-Za-z0-9]), so a non-ASCII continuation would read as a word "
            "boundary and could score as a hit. The boundary class is a frozen "
            "measurement rule; changing it needs a decision, not a run"
        )
    return {
        "span_tokens": SPAN_TOKENS,
        "form_lengths": {w: list(lengths[w]) for w in sorted(lengths)},
        "worst_form_length": max((max(v) for v in lengths.values()), default=0),
        "all_ascii": True,
    }


# --- environment, validation, cross-check -------------------------------------

class SubjectSpec:
    """The shape validation needs, read from the config alone — so a wrong-arm
    exit or a `--dry-run` never pays for a checkpoint load (PR #7 review F6's
    disposition). Re-asserted against the loaded `SubjectModel` before any trial,
    so the cheap path can never quietly disagree with the measured one."""

    def __init__(self, model_id: str) -> None:
        text_config = transformers.AutoConfig.from_pretrained(model_id).get_text_config()
        self.n_layers: int = text_config.num_hidden_layers
        self.d_model: int = text_config.hidden_size


def certified_environment(device: str) -> tuple[bool, list[str]]:
    """Is this the stack the anchor's bit-for-bit reproduction was certified on?
    Returns (certified, reasons-it-is-not). Carried verbatim from M1/M2."""
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


def validate(args, artifact: dict, spec, tokenizer) -> tuple[list[int], dict, dict]:
    """Wrong-arm input checks (the M0/M1/M2 gate pattern) plus D18(a)'s two
    run-time bars. Returns (band, the parsed M1 artifact, the measured bars) —
    the parsed artifact is *returned* rather than discarded so `main()` never
    parses it twice (PR #7 review F6's second half), and the bars object the
    results JSON publishes is the very one that gated the run."""
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
        load_subset_items()
    except (FileNotFoundError, ValueError) as exc:
        fail_invalid(str(exc))
    bars = check_run_time_bars(list(PLANNED_DIRECTIONS), tokenizer)
    recorded = load_m1_run(args.m1 or m1_path_for(args.model_id), args.model_id, band)
    return band, recorded, bars


def load_m1_run(path: str, model_id: str, band: list[int]) -> dict:
    """M3's comparison target. A run that was itself pre-declared not to be a
    result cannot certify anything, so it is refused here rather than silently
    cross-checked against."""
    if not os.path.exists(path):
        fail_invalid(f"M1 results {path} missing — D16's cross-check needs them")
    try:
        with open(path) as f:
            recorded = json.load(f)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        fail_invalid(f"M1 results {path} could not be read as JSON: {exc}")
    if recorded.get("milestone") != "M1":
        fail_invalid(f"{path} is not an M1 battery run (milestone={recorded.get('milestone')!r})")
    if recorded.get("model_id") != model_id:
        fail_invalid(f"M1 results {path} are for {recorded.get('model_id')!r}, not {model_id!r}")
    if recorded.get("band") != band:
        fail_invalid(f"M1 results {path} were run on band {recorded.get('band')}, not {band}")
    if recorded.get("smoke_limit") is not None:
        fail_invalid(f"M1 results {path} are a SMOKE run — never a cross-check target")
    if not recorded.get("environment", {}).get("certified"):
        fail_invalid(
            f"M1 results {path} ran off the certified environment — pre-declared "
            "NOT A RESULT, so they cannot certify this run either"
        )
    return recorded


def m1_crosscheck(records: list[dict], recorded: dict) -> tuple[list[str], dict]:
    """D16(a): the 108 cells M3 shares with M1 must reproduce M1's recording
    exactly on the raw decoded strings. The mapping is per item — M3 keys its
    cells by the ablated direction, so M1's `primed_late` is the item's own
    concept's cell and M1's `control_late` is the item's frozen control's cell.
    Returns (mismatches, mass texture)."""
    reference = {r["name"]: r for r in recorded["items"]}
    mismatches: list[str] = []
    equal = total = checked = 0
    for record in records:
        theirs = reference.get(record["name"])
        if theirs is None:
            mismatches.append(f"{record['name']}: absent from the M1 recording")
            continue
        checked += 1
        shared = {
            "clean": "clean",
            "primed_late": condition_name(record["concept"]),
            "control_late": condition_name(record["control"]),
        }
        for m1_condition, ours_name in shared.items():
            ours, mine = record["cells"][ours_name], theirs["cells"][m1_condition]
            for field in M1_CELL_FIELDS:
                if ours[field] != mine[field]:
                    mismatches.append(
                        f"{record['name']}/{ours_name} (M1 {m1_condition}).{field}: "
                        f"{ours[field]!r} != M1 {mine[field]!r}"
                    )
            total += 1
            equal += ours["concept_mass"] == mine["concept_mass"]
    return mismatches, {
        "items_checked": checked,
        "items_expected": EXPECTED_SUBSET_ITEMS,
        "cells_checked": total,
        "cells_expected": EXPECTED_SUBSET_ITEMS * len(M1_SHARED_CONDITIONS),
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
    place. Called twice: once for the cells M1 already recorded (whose
    reproduction the cross-check then grades), and once for everything new —
    which is what makes "before any off-diagonal cell is read" literally true.
    """
    for i, (item, forms) in enumerate(planned):
        start = time.perf_counter()
        shared, rest = conditions_for(conditions, item)
        runnable = shared if phase == "M1-shared" else rest
        prompt = NAMING_Q.format(clue=item["clue"], noun=item["noun"])
        input_ids = encode_chat(subject, prompt)
        record = records.setdefault(item["name"], {
            "name": item["name"], "category": item["category"],
            "concept": item["concept"], "control": item["control"],
            "source": item["source"],
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
        diagonal = record["cells"].get(condition_name(item["concept"]))
        print(
            f"[{phase} {i + 1}/{len(planned)}] {item['name']} ({item['concept']}): "
            + (
                f"clean={'OK' if record['cells']['clean']['produced'] else 'x'}"
                f"({record['cells']['clean']['greedy_3']!r}) "
                f"diagonal={'named' if diagonal['produced'] else 'MUTED'} "
                f"control={'named' if record['cells'][condition_name(item['control'])]['produced'] else 'muted'} "
                f"gate={'IN' if gate else 'out'}"
                if phase == "M1-shared"
                else f"gate={'IN' if gate else 'out'} {len(runnable)} new cells"
            )
            + f" ({time.perf_counter() - start:.1f}s)"
        )
    return records


# --- the pre-committed analysis package ---------------------------------------

def off_diagonal_directions(concept: str) -> list[str]:
    """The 11 subset directions that are not this concept's own."""
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


def contrast(base: dict, mech: dict, label: str) -> dict:
    """The frozen two-proportion comparison: `mech` (the surviving off-diagonal
    side) expected above `base` (the muted diagonal). Positive with a Newcombe
    95% CI excluding 0 is the clause passing."""
    diff = newcombe_diff(base["hits"], base["n"], mech["hits"], mech["n"])
    return {
        "label": label,
        "diagonal": base,
        "off_diagonal": mech,
        "newcombe_offdiagonal_minus_diagonal_naming": list(diff),
        "excludes_zero": diff[0] > 0 and excludes_zero(diff[1], diff[2]),
    }


def matrix_package(records: list[dict], categories: dict[str, str], tokenizer) -> dict:
    """Everything D17 pre-commits: the two gate clauses, the collateral-floor
    readout, the effective-n sanity checks, and the descriptive package."""
    gated = [r for r in records if r["gate_span"]]
    n_gated = len(gated)
    by_concept: dict[str, list[dict]] = {}
    for record in records:
        by_concept.setdefault(record["concept"], []).append(record)
    gated_by_concept = {c: [r for r in rows if r["gate_span"]]
                        for c, rows in by_concept.items()}
    siblings = {c: within_category_siblings(c, categories) for c in SUBSET}

    # --- the two gate clauses -------------------------------------------------
    diagonal = pooled(arm_cells(gated, lambda r: [r["concept"]]))
    off_diagonal = pooled(arm_cells(gated, lambda r: off_diagonal_directions(r["concept"])))
    within = pooled(arm_cells(gated, lambda r: siblings[r["concept"]]))
    cross = pooled(arm_cells(
        gated,
        lambda r: [w for w in off_diagonal_directions(r["concept"])
                   if w not in siblings[r["concept"]]],
    ))
    restricted = [r for r in gated if siblings[r["concept"]]]
    diagonal_restricted = pooled(arm_cells(restricted, lambda r: [r["concept"]]))

    clause_1 = contrast(diagonal, off_diagonal, "pooled off-diagonal vs diagonal")
    clause_2 = contrast(
        diagonal_restricted, within,
        "within-category off-diagonal vs diagonal, on items with >= 1 subset sibling",
    )
    holds = clause_1["excludes_zero"] and clause_2["excludes_zero"]
    underpowered = diagonal["n"] < MIN_N or diagonal_restricted["n"] < MIN_N

    # --- the collateral-floor readout (F15's cluster-mean collapse) -----------
    fractions = [
        sum(r["cells"][condition_name(w)]["produced"]
            for w in off_diagonal_directions(r["concept"]))
        / len(off_diagonal_directions(r["concept"]))
        for r in gated
    ]
    total = sum(fractions)
    floor_k = int(math.floor(total))
    floor_lo, floor_hi = wilson(floor_k, n_gated)
    floor = {
        "readout": "cluster-collapsed per-cell survival (D17 / brief review F15)",
        "sum_of_fractions": total,
        "mean_survival_fraction": (total / n_gated) if n_gated else None,
        "k": floor_k, "n": n_gated, "wilson_95": [floor_lo, floor_hi],
        "threshold": FLOOR_LOWER_BOUND,
        "damaged_floor": n_gated > 0 and floor_lo < FLOOR_LOWER_BOUND,
        "pooled_per_cell_permissive": {
            **off_diagonal, "wilson_lower": off_diagonal["wilson_95"][0]
        },
    }

    # --- the effective-n sanity checks (never dispositive) --------------------
    def survives_all(row: dict, words: list[str]) -> bool:
        return all(row["cells"][condition_name(w)]["produced"] for w in words)

    all_11 = rate_cell(
        sum(survives_all(r, off_diagonal_directions(r["concept"])) for r in gated), n_gated
    )
    all_siblings = rate_cell(
        sum(survives_all(r, siblings[r["concept"]]) for r in restricted), len(restricted)
    )
    # The diagonal arm is already one cell per gated item, so it collapses to
    # itself — only the repeated off-diagonal arm needs collapsing.
    effective_n = {
        "clause_1_survives_all_11": contrast(
            diagonal, all_11, "per-item collapse of clause (1)"
        ),
        "clause_2_survives_all_within_category_siblings": contrast(
            diagonal_restricted, all_siblings, "per-item collapse of clause (2)"
        ),
        "note": (
            "Pre-registered, reported beside the gate, NEVER dispositive. If a "
            "pooled clause is CI-clean but its per-item collapse is not, the "
            "per-item numbers are the honest ones to quote."
        ),
    }

    # --- the descriptive package ---------------------------------------------
    matrix = []
    for prime in SUBSET:
        for probe in SUBSET:
            rows = gated_by_concept.get(probe, [])
            cells = [r["cells"][condition_name(prime)] for r in rows]
            matrix.append({
                "prime": prime, "probe": probe,
                "is_diagonal": prime == probe,
                "same_category": categories[prime] == categories[probe],
                "cell": pooled(cells),
                "degeneracy_texture": wrong_opening_degeneracy(cells, tokenizer),
            })

    row_profiles = {}
    for prime in SUBSET:
        collateral_rows = [r for r in gated if r["concept"] != prime]
        row_profiles[prime] = {
            "category": categories[prime],
            "stratum": next(s for s, m in SUBSET_STRATA.items() if prime in m),
            "diagonal": pooled([r["cells"][condition_name(prime)]
                                for r in gated_by_concept.get(prime, [])]),
            "collateral_all": pooled([r["cells"][condition_name(prime)]
                                      for r in collateral_rows]),
            "collateral_within_category": pooled([
                r["cells"][condition_name(prime)] for r in collateral_rows
                if prime in siblings[r["concept"]]
            ]),
            "collateral_cross_category": pooled([
                r["cells"][condition_name(prime)] for r in collateral_rows
                if prime not in siblings[r["concept"]]
            ]),
        }

    column_profiles = {}
    for probe in SUBSET:
        rows = gated_by_concept.get(probe, [])
        column_profiles[probe] = {
            "category": categories[probe],
            "gated_items": len(rows),
            "diagonal": pooled([r["cells"][condition_name(probe)] for r in rows]),
            "fragility_all": pooled(arm_cells(rows, lambda r: off_diagonal_directions(r["concept"]))),
            "fragility_within_category": pooled(arm_cells(rows, lambda r: siblings[r["concept"]])),
            "clean": pooled([r["cells"]["clean"] for r in rows]),
        }

    asymmetry = []
    for i, first in enumerate(SUBSET):
        for second in SUBSET[i + 1:]:
            forward = pooled([r["cells"][condition_name(first)]
                              for r in gated_by_concept.get(second, [])])
            backward = pooled([r["cells"][condition_name(second)]
                               for r in gated_by_concept.get(first, [])])
            asymmetry.append({
                "pair": [first, second],
                "same_category": categories[first] == categories[second],
                f"{first}_deleted_probe_{second}": forward,
                f"{second}_deleted_probe_{first}": backward,
                "rate_gap": (
                    None if forward["rate"] is None or backward["rate"] is None
                    else forward["rate"] - backward["rate"]
                ),
            })

    recorded_controls = {}
    for concept in SUBSET:
        group = by_concept.get(concept, [])
        control = group[0]["control"] if group else None
        rows = gated_by_concept.get(concept, [])
        recorded_controls[concept] = {
            "control_direction": control,
            "in_matrix": control in SUBSET if control else None,
            # M1's frozen control is same-category by construction (load_items
            # requires concept and control to share the item's roster category).
            "same_category": True,
            "cell": pooled(
                [r["cells"][condition_name(control)] for r in rows] if control else []
            ),
        }

    mass_rows = [r for r in gated if r["mass_channel_eligible"]]

    def mean_mass(directions_for) -> float | None:
        cells = arm_cells(mass_rows, directions_for)
        return sum(c["concept_mass"] for c in cells) / len(cells) if cells else None

    mass_texture = {
        "mass_channel_n_items": len(mass_rows),
        "clean": (sum(r["cells"]["clean"]["concept_mass"] for r in mass_rows) / len(mass_rows)
                  if mass_rows else None),
        "diagonal": mean_mass(lambda r: [r["concept"]]),
        "off_diagonal": mean_mass(lambda r: off_diagonal_directions(r["concept"])),
        "within_category_off_diagonal": mean_mass(lambda r: siblings[r["concept"]]),
        "cross_category_off_diagonal": mean_mass(
            lambda r: [w for w in off_diagonal_directions(r["concept"])
                       if w not in siblings[r["concept"]]]
        ),
    }

    per_concept = {}
    for concept in SUBSET:
        group = by_concept.get(concept, [])
        rows = gated_by_concept.get(concept, [])
        per_concept[concept] = {
            "category": categories[concept],
            "stratum": next(s for s, m in SUBSET_STRATA.items() if concept in m),
            "within_category_subset_siblings": siblings[concept],
            "direction_key": group[0]["direction_key"] if group else None,
            "mass_channel_eligible": group[0]["mass_channel_eligible"] if group else None,
            "items_run": len(group),
            "gated_items": len(rows),
            "clean": pooled([r["cells"]["clean"] for r in rows]),
            "diagonal": pooled([r["cells"][condition_name(concept)] for r in rows]),
            "off_diagonal_collateral": pooled(
                arm_cells(rows, lambda r: off_diagonal_directions(r["concept"]))
            ),
            "within_category_collateral": pooled(
                arm_cells(rows, lambda r: siblings[r["concept"]])
            ),
            "row_collateral": row_profiles[concept]["collateral_all"],
        }

    return {
        "competence": {
            "items_run": len(records),
            "gate_span": n_gated,
            "gate_first_token_texture": sum(r["gate_first_token"] for r in records),
            "gate_verbatim_p": sum(r["gate_verbatim_p"] for r in records),
        },
        "clean_cell": pooled([r["cells"]["clean"] for r in gated]),
        "pooled_arms": {
            "diagonal": diagonal,
            "off_diagonal": off_diagonal,
            "within_category_off_diagonal": within,
            "cross_category_off_diagonal": cross,
            "diagonal_restricted_to_sibling_items": diagonal_restricted,
        },
        "specificity_contrast": {
            "clause_1_pooled": clause_1,
            "clause_2_within_category": clause_2,
            "matrix_specific_shape_holds": holds,
            "underpowered": underpowered,
            "collateral_floor": floor,
            "effective_n_check": effective_n,
        },
        "matrix": matrix,
        "row_profiles": row_profiles,
        "column_profiles": column_profiles,
        "asymmetry": asymmetry,
        "recorded_control_cells": recorded_controls,
        "concept_mass_texture": mass_texture,
        "per_concept": per_concept,
    }


def wrong_opening_degeneracy(cells: list[dict], tokenizer) -> dict:
    """D17's dispositive guard, carried from M2's D14 and generalized from "one
    condition over rows" to "any pooled set of cells": the most common first
    token among this arm's **non-produced** cells, with the share taken against
    the arm's full cell count — "at least half this arm's answers are the same
    *wrong* opening". Under D9(b) the raw all-answers share stops meaning
    pathology, because a correct answer may legitimately open with a shared
    fragment; that raw guard is recorded beside as texture."""
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


def matrix_verdict(
    certified: bool,
    degenerate_arms: list[str],
    underpowered: bool,
    holds: bool,
    damaged_floor: bool = False,
    limit: int | None = None,
) -> str:
    """D17's frozen precedence: NOT A RESULT > DEGENERATE > UNDERPOWERED > the
    contrast. The ON A DAMAGED FLOOR qualifier attaches to a contrast-level
    verdict only — it *scopes a claim*, so it has nothing to scope when
    precedence already withheld the claim. It can never create or rescue one."""
    if limit is not None:
        return f"NOT A RESULT — smoke run (--limit {limit})"
    if not certified:
        return "NOT A RESULT — uncertified environment"
    if degenerate_arms:
        return (
            "DEGENERATE — no specificity claim "
            f"(collapsed: {', '.join(degenerate_arms)})"
        )
    if underpowered:
        return "UNDERPOWERED — no specificity claim"
    verdict = "MATRIX-SPECIFIC" if holds else "not shown"
    return verdict + (" — ON A DAMAGED FLOOR" if damaged_floor else "")


# --- main ---------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--lens", required=True, help="fitted lens artifact (*.pt)")
    parser.add_argument("--m1", default=None, help="recorded M1 results JSON to cross-check against")
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

    # PR #7 review F6: everything validatable is validated BEFORE the checkpoint
    # loads, so a wrong-arm exit or a --dry-run never pays for a model load.
    spec = SubjectSpec(args.model_id)
    tok = transformers.AutoTokenizer.from_pretrained(args.model_id)
    try:
        artifact = torch.load(args.lens, map_location="cpu", weights_only=True)
    except (FileNotFoundError, OSError, RuntimeError, torch.serialization.pickle.UnpicklingError) as exc:
        fail_invalid(f"lens artifact {args.lens} could not be loaded: {exc}")
    band, recorded, bars = validate(args, artifact, spec, tok)
    m1_path = args.m1 or m1_path_for(args.model_id)

    thirds = sub_band_thirds(band)
    late = thirds["late"]
    conditions = plan_conditions(late)
    items = load_subset_items()
    categories = subset_categories(items)

    directions = list(PLANNED_DIRECTIONS)
    missing_forms = [w for w in directions if not token_forms(w, tok)]
    if missing_forms:
        fail_invalid(
            f"no single-token unembed row exists for direction word(s) "
            f"{missing_forms} — the matrix cannot key their direction"
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
        f"L{late[0]}–L{late[-1]} (width {len(late)}), λ={MATRIX_LAMBDA:g}, k=1 | "
        f"matrix {len(SUBSET)}×{len(SUBSET)} + {len(CONTROL_EXTRA_DIRECTIONS)} "
        f"out-of-subset control directions | items {len(planned)} gradable / "
        f"{len(dropped)} dropped | cells {cells_planned} "
        f"({len(planned)} clean + {len(planned) * len(SUBSET)} matrix + "
        f"{cells_planned - len(planned) * (len(SUBSET) + 1)} control-extra) | M1 "
        f"{m1_path} | environment "
        + ("CERTIFIED" if certified else "UNCERTIFIED: " + "; ".join(uncertified_reasons))
    )
    print(
        "  D18 bars: every direction word fits the "
        f"{SPAN_TOKENS}-token span in both forms and is pure ASCII | "
        "within-category subset siblings: "
        + ", ".join(
            f"{c}×{len(within_category_siblings(c, categories))}" for c in SUBSET
        )
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
    grade(planned, conditions, subject, vectors, store, "M1-shared")
    records = [store[item["name"]] for item, _ in planned]

    mismatches, mass_texture = m1_crosscheck(records, recorded)
    crosscheck = {
        "m1_results": m1_path,
        "gate_bearing": certified,
        "mismatches": mismatches[:20],
        "n_mismatches": len(mismatches),
        **mass_texture,
    }
    print(
        f"\nM1 CROSS-CHECK: {'PASS' if not mismatches else 'MISMATCH'} — "
        f"{len(mismatches)} mismatches over {mass_texture['cells_checked']} reused "
        f"cells ({mass_texture['items_checked']} items × {len(M1_SHARED_CONDITIONS)} "
        f"conditions) | concept_mass exact {mass_texture['mass_cells_equal']}/"
        f"{mass_texture['cells_checked']} | "
        + ("GATE-BEARING (certified environment)" if certified
           else "not gate-bearing (uncertified environment)")
    )
    for problem in mismatches[:20]:
        print(f"  {problem}")
    if mismatches and certified:
        fail_invalid(
            f"{len(mismatches)} subset cells disagree with the recorded M1 run "
            f"{m1_path} on the certified environment — the instrument drifted "
            "(D16); no off-diagonal cell was read"
        )
    if args.limit is None and mass_texture["items_checked"] != EXPECTED_SUBSET_ITEMS:
        fail_invalid(
            f"M1 cross-check compared only {mass_texture['items_checked']} of "
            f"{EXPECTED_SUBSET_ITEMS} subset items — the frozen subset did not run "
            "as frozen, so 0 mismatches is not a re-certification (D16)"
        )
    if mismatches:
        print(
            "  ^ recorded, NOT gate-bearing: bit-for-bit reproduction is a property "
            "of the certified stack, not of the instrument (D16, scoped)"
        )

    grade(planned, conditions, subject, vectors, store, "new-cells")

    package = matrix_package(records, categories, tok)
    gated = [r for r in records if r["gate_span"]]
    n = package["competence"]["gate_span"]
    siblings = {c: within_category_siblings(c, categories) for c in SUBSET}

    arms = {
        "clean": [r["cells"]["clean"] for r in gated],
        "diagonal": arm_cells(gated, lambda r: [r["concept"]]),
        "off_diagonal": arm_cells(gated, lambda r: off_diagonal_directions(r["concept"])),
        "within_category_off_diagonal": arm_cells(gated, lambda r: siblings[r["concept"]]),
        "cross_category_off_diagonal": arm_cells(
            gated,
            lambda r: [w for w in off_diagonal_directions(r["concept"])
                       if w not in siblings[r["concept"]]],
        ),
    }
    for prime in SUBSET:
        arms[f"row_{prime}"] = [r["cells"][condition_name(prime)]
                                for r in gated if r["concept"] != prime]
    guard_wrong_opening = {name: wrong_opening_degeneracy(cells, tok)
                           for name, cells in arms.items()}
    guard_all_answers = {
        name: degeneracy([cell["greedy_id"] for cell in cells], tok)
        for name, cells in arms.items()
    }
    for record in records:
        for cell in record["cells"].values():
            del cell["greedy_id"]

    # D17's disposition, scoped to the arms the gate actually reads.
    dispositive = ("off_diagonal",)
    degenerate_arms = [a for a in dispositive if guard_wrong_opening[a]["collapsed"]]
    row_caveats = [p for p in SUBSET if guard_wrong_opening[f"row_{p}"]["collapsed"]]
    spec_contrast = package["specificity_contrast"]
    spec_contrast["degenerate_gate_arms"] = degenerate_arms
    spec_contrast["diagonal_collapsed_tag"] = guard_wrong_opening["diagonal"]["collapsed"]
    spec_contrast["row_texture_caveats"] = row_caveats
    verdict = matrix_verdict(
        certified, degenerate_arms, spec_contrast["underpowered"],
        spec_contrast["matrix_specific_shape_holds"],
        spec_contrast["collateral_floor"]["damaged_floor"], args.limit,
    )
    spec_contrast["verdict"] = verdict

    results = {
        "milestone": "M3",
        "model_id": args.model_id,
        "lens": args.lens,
        "lens_n_prompts": artifact["n_prompts"],
        "band": band,
        "thirds": thirds,
        "ablated_layers": late,
        "lambda": MATRIX_LAMBDA,
        "mode": "gate (pooled diagonal vs off-diagonal) + descriptive (the matrix)",
        "environment": {
            "device": device,
            "torch": torch.__version__,
            "transformers": transformers.__version__,
            "certified": certified,
            "uncertified_reasons": uncertified_reasons,
        },
        "protocol": {
            "instructions": {"naming": NAMING_Q},
            "subset": list(SUBSET),
            "subset_strata": SUBSET_STRATA,
            "subset_categories": categories,
            "control_extra_directions": list(CONTROL_EXTRA_DIRECTIONS),
            "conditions": [
                {k: c[k] for k in ("name", "group", "direction", "layers", "lam")}
                for c in conditions
            ],
            "cells_planned": cells_planned,
            "gate": "greedy-span naming-only under D9(b); first-token recorded beside",
            "readback_tol": READBACK_TOL,
            "min_n": MIN_N,
            "collapse_share": COLLAPSE_SHARE,
            "p_name_floor": P_NAME_FLOOR,
            "span_tokens": SPAN_TOKENS,
            "floor_lower_bound": FLOOR_LOWER_BOUND,
            "run_time_bars": bars,
            "items": ITEMS_PATH,
            "gate_wording": GATE_WORDING,
        },
        "dropped_single_token_prefilter": dropped,
        "m1_crosscheck": crosscheck,
        "smoke_limit": args.limit,
        **package,
        "degeneracy_guard_wrong_opening": guard_wrong_opening,
        "degeneracy_guard_all_answers": guard_all_answers,
        "items": records,
    }

    smoke = f"SMOKE (limit={args.limit}) — not a result — " if args.limit else ""
    arms_out = package["pooled_arms"]
    c1 = spec_contrast["clause_1_pooled"]["newcombe_offdiagonal_minus_diagonal_naming"]
    c2 = spec_contrast["clause_2_within_category"]["newcombe_offdiagonal_minus_diagonal_naming"]
    floor = spec_contrast["collateral_floor"]
    print(
        f"\nM3 SPECIFICITY VERDICT ({args.model_id}): {smoke}gate {n}/{len(records)} "
        f"items{' UNDERPOWERED' if spec_contrast['underpowered'] else ''} | naming "
        f"diagonal {arms_out['diagonal']['hits']}/{arms_out['diagonal']['n']}, "
        f"off-diagonal {arms_out['off_diagonal']['hits']}/{arms_out['off_diagonal']['n']}, "
        f"within-category {arms_out['within_category_off_diagonal']['hits']}/"
        f"{arms_out['within_category_off_diagonal']['n']}, cross-category "
        f"{arms_out['cross_category_off_diagonal']['hits']}/"
        f"{arms_out['cross_category_off_diagonal']['n']} | clause(1) {c1[0]:+.3f} "
        f"[{c1[1]:+.3f},{c1[2]:+.3f}], clause(2) {c2[0]:+.3f} "
        f"[{c2[1]:+.3f},{c2[2]:+.3f}] → {verdict}"
    )
    print(
        f"  collateral floor (cluster-collapsed per-cell survival): "
        f"{floor['k']}/{floor['n']} → [{floor['wilson_95'][0]:.3f}, "
        f"{floor['wilson_95'][1]:.3f}] vs the pre-registered {FLOOR_LOWER_BOUND} "
        f"→ {'ON A DAMAGED FLOOR' if floor['damaged_floor'] else 'floor clear'} "
        f"| permissive pooled per-cell reading "
        f"{arms_out['off_diagonal']['hits']}/{arms_out['off_diagonal']['n']} "
        f"lower bound {arms_out['off_diagonal']['wilson_95'][0]:.3f}"
    )
    eff = spec_contrast["effective_n_check"]
    for key in ("clause_1_survives_all_11", "clause_2_survives_all_within_category_siblings"):
        d = eff[key]["newcombe_offdiagonal_minus_diagonal_naming"]
        print(
            f"  effective-n check ({key}, never dispositive): "
            f"{eff[key]['off_diagonal']['hits']}/{eff[key]['off_diagonal']['n']} vs "
            f"diagonal {eff[key]['diagonal']['hits']}/{eff[key]['diagonal']['n']} → "
            f"{d[0]:+.3f} [{d[1]:+.3f},{d[2]:+.3f}] "
            f"{'CI-clean' if eff[key]['excludes_zero'] else 'NOT CI-clean'}"
        )
    short = {c: c[:3] for c in SUBSET}
    print("\n  the matrix (rows = deleted direction, columns = probed concept; "
          "cell = gated items still naming):")
    print(" " * 11 + " ".join(f"{short[c]:>4}" for c in SUBSET) + "   (probe)")
    print(" " * 11 + " ".join(
        f"{sum(1 for r in gated if r['concept'] == c):>4}" for c in SUBSET
    ) + "   (gated n)")
    by_pair = {(e["prime"], e["probe"]): e for e in package["matrix"]}
    for prime in SUBSET:
        print(
            f"  {prime:>8} " + " ".join(
                f"{by_pair[(prime, probe)]['cell']['hits']:>4}" for probe in SUBSET
            )
        )
    print("  row collateral (deleting A, over the other 11 concepts' gated items): "
          + " ".join(
              f"{p}={package['row_profiles'][p]['collateral_all']['hits']}/"
              f"{package['row_profiles'][p]['collateral_all']['n']}" for p in SUBSET
          ))
    if row_caveats:
        print(f"  row degeneracy texture (never dispositive): {', '.join(row_caveats)}")
    print(
        "  recorded control cells (the M1-comparable single-control view): "
        + " ".join(
            f"{c}→{v['control_direction']}"
            f"{'' if v['in_matrix'] else '*'}="
            f"{v['cell']['hits']}/{v['cell']['n']}"
            for c, v in package["recorded_control_cells"].items()
        )
        + "   (* direction outside the matrix — D16a's control-extra cells)"
    )

    if args.limit and not args.out:
        print("smoke run: results not written (pass --out to keep them)")
        raise SystemExit(0)
    out = args.out or ("results/m3-matrix-" + args.model_id.split("/")[-1].lower() + ".json")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w") as f:
        json.dump(results, f, indent=1)
    print(f"results written to {out}")
    raise SystemExit(0)


if __name__ == "__main__":
    main()

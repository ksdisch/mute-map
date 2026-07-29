"""test_m4.py — invariants for the M4 vocabulary collateral strip.

The heavyweight proof that M4's instrument is still the certified instrument is
the two cross-checks the runner performs at run time — 255 M1-recorded and 468
M3-recorded cells, graded before a single new cell is read. These tests pin what
a model run cannot.

Most of them exist because the M4 brief's six-round review found the same class
of defect over and over: **a prose rule that broke when read literally.** Those
are pinned here by name, because the brief is the only place they were ever
written down and a later edit could silently un-fix them:

- the D9(b) residual selector must select EXACTLY the cells the brief counted —
  2 at 1.5B, 2 at 3B, 0 at 0.5B. A **case-exact** reading selects 0 (the F16
  defect: a silent no-op mitigation) and a **"fills the 3-token span"** reading
  selects every recorded cell. The two mistakes fail in opposite directions and
  are pinned separately;
- the residual-conservative read's denominator is **fail in place** — the arm
  stays at 41 / 71 / 84 and a residual-affected item scores as a failure;
- `AS-SCORED ONLY` attaches to a **bar-level verdict only**, never to
  DEGENERATE / UNDERPOWERED / NOT A RESULT (Amendment 2 (iii), which fixed
  Amendment 1 attaching it to all of them);
- the failing label is the lineage's pre-committed null `not shown`, never an
  assertive negative (Amendment 2 (i));
- every realized n is knowable now from the recorded artifacts, so the power
  table is a **cross-check**, not a projection: a run that disagrees is INVALID.

Several tests read the *committed* M1 and M3 artifacts. That is deliberate: the
brief pre-registers numbers computed from them (every n in the power table, the
ceilings, the residual set, the confound list, the zero-gated counts), and a
pre-registration that no test pins is one a later edit can silently break.
"""
import json
import re
import sys
import types

import pytest
import torch

import m1_battery
import m3_matrix
import m4_strip
import m4_verdict
import oracle
from harness import MIN_N
from m4_strip import (
    CROSS_MENTION_PAIRS,
    EXPECTED_M1_CELLS,
    EXPECTED_M3_CELLS,
    GATE_WORDING,
    PLANNED_DIRECTIONS,
    SUBSET,
    SUBSET_STRATA,
    check_run_time_bars,
    concept_categories,
    condition_name,
    conditions_for,
    cross_mention_pairs,
    expected_recorded_cells,
    is_m1_recorded,
    is_m3_recorded,
    is_residual_cell,
    load_strip_items,
    off_target_directions,
    plan_conditions,
    planned_cells,
    scored_and_direction_words,
    strip_package,
    survives_all,
    wrong_opening_degeneracy,
)
from m4_verdict import (
    CONSERVATIVE_READ_ORDER,
    NULL_LABEL,
    PASS_LABEL,
    QUALIFIER,
    SURVIVAL_LOWER_BOUND,
    strip_verdict,
    verdict_string,
)
from stats import wilson

SUBJECTS = ("qwen2.5-0.5b-instruct", "qwen2.5-1.5b-instruct", "qwen2.5-3b-instruct")
MODEL_IDS = {
    "qwen2.5-0.5b-instruct": "Qwen/Qwen2.5-0.5B-Instruct",
    "qwen2.5-1.5b-instruct": "Qwen/Qwen2.5-1.5B-Instruct",
    "qwen2.5-3b-instruct": "Qwen/Qwen2.5-3B-Instruct",
}
#: The brief's power table — every entry computed from the recorded clean arm
#: before any M4 cell existed, so each is a CROSS-CHECK the run must reproduce.
PRE_REGISTERED = {
    "qwen2.5-0.5b-instruct": {
        "gated": 69, "arm": 41, "concepts": 23, "zero_gated": 25,
        "new_pool": 492, "never_measured": 486, "recorded_in_m1": 6,
        "ceiling": 35, "residual": [], "confound_cells": 1,
    },
    "qwen2.5-1.5b-instruct": {
        "gated": 105, "arm": 71, "concepts": 41, "zero_gated": 7,
        "new_pool": 852, "never_measured": 844, "recorded_in_m1": 8,
        "ceiling": 69, "residual": ["beetle-1", "butterfly-1"], "confound_cells": 4,
    },
    "qwen2.5-3b-instruct": {
        "gated": 116, "arm": 84, "concepts": 43, "zero_gated": 5,
        "new_pool": 1008, "never_measured": 993, "recorded_in_m1": 15,
        "ceiling": 82, "residual": ["butterfly-1", "trumpet-3"], "confound_cells": 4,
    },
}
LATE_THIRDS = {24: list(range(17, 22)), 28: list(range(19, 25)), 36: list(range(26, 33))}


# --- fixtures over the recorded artifacts -------------------------------------

def _m1(subject):
    return json.load(open(f"results/m1-battery-{subject}.json"))


def _m3(subject):
    return json.load(open(f"results/m3-matrix-{subject}.json"))


def _items():
    return load_strip_items()


def _by_name():
    return {i["name"]: i for i in _items()}


def _recorded_gate_arm(subject):
    """The gate arm as the recorded clean arm already fixes it: gated
    (D9(b) on the recorded clean span) and NOT one of the 12 subset concepts."""
    battery, recorded = _by_name(), _m1(subject)
    return [
        r for r in recorded["items"]
        if battery[r["name"]]["concept"] not in SUBSET
        and oracle.says_concept_prefix(
            r["cells"]["clean"]["greedy_3"], battery[r["name"]]["concept"]
        )
    ]


class _Tok:
    @staticmethod
    def decode(ids):
        return f"tok{ids[0]}"


class _TableTok:
    """A tokenizer stub whose token counts come from a table — the only way to
    exercise D22's bars without a roster edit the project would never make."""

    def __init__(self, table, default=1):
        self.table, self.default = table, default

    def __call__(self, text, add_special_tokens=False):
        return types.SimpleNamespace(input_ids=[0] * self.table.get(text, self.default))


# --- the frozen roster, the strip frame, and the cell arithmetic ---------------

def test_the_primes_are_m3s_twelve_verbatim():
    """D19(a): M4 changes the probe side, never the prime side. The primes are
    M3's subset — themselves M2's D11-stratified 12 — copied, not re-chosen."""
    assert SUBSET == m3_matrix.SUBSET
    assert SUBSET_STRATA == m3_matrix.SUBSET_STRATA
    assert PLANNED_DIRECTIONS == SUBSET  # no control-extra directions in M4


def test_the_probe_side_is_the_whole_frozen_battery():
    items = _items()
    assert len(items) == m1_battery.EXPECTED_ITEMS == 180
    assert len({i["concept"] for i in items}) == m1_battery.EXPECTED_CONCEPTS == 60
    assert len({i["concept"] for i in items} - set(SUBSET)) == 48


def test_the_plan_grades_the_pre_registered_2340_cells():
    """180 clean + 12 x 180 ablated, every cell at the identical late third."""
    items = _items()
    conditions = plan_conditions(LATE_THIRDS[28])
    assert len(conditions) == 1 + len(SUBSET) == 13
    assert planned_cells(conditions, items) == 2340
    assert all(c["lam"] == m4_strip.STRIP_LAMBDA for c in conditions[1:])
    assert {tuple(c["layers"]) for c in conditions[1:]} == {tuple(LATE_THIRDS[28])}


def test_the_recorded_cells_are_graded_before_anything_new():
    """D19(a) made literal: the phase-1 set is exactly the union of the two
    recorded surfaces, and every remaining cell is genuinely new."""
    items, conditions = _items(), plan_conditions(LATE_THIRDS[28])
    recorded = sum(len(conditions_for(conditions, i)[0]) for i in items)
    new = sum(len(conditions_for(conditions, i)[1]) for i in items)
    assert recorded == 633   # 255 M1 + 468 M3 - 90 counted by both
    assert new == 1707
    assert recorded + new == planned_cells(conditions, items)
    for item in items:
        first, rest = conditions_for(conditions, item)
        assert all(m4_strip.is_recorded(c, item) for c in first)
        assert not any(m4_strip.is_recorded(c, item) for c in rest)


def test_the_two_recorded_surfaces_are_the_pre_registered_255_and_468():
    surfaces = expected_recorded_cells(_items())
    assert surfaces == {"m1_cells": EXPECTED_M1_CELLS, "m1_items": 180,
                        "m3_cells": EXPECTED_M3_CELLS, "m3_items": 36}
    assert (EXPECTED_M1_CELLS, EXPECTED_M3_CELLS) == (255, 468)


def test_a_drifted_battery_breaks_the_recertification_surface():
    items = [i for i in _items() if i["name"] != "france-1"]
    with pytest.raises(ValueError, match="re-certification surface drifted"):
        expected_recorded_cells(items)


def test_which_cells_each_recorded_surface_claims():
    """The two predicates are the whole mapping, so they are pinned per role:
    M1 recorded `clean` for every item and the concept/control directions when
    those are primes; M3 recorded all 13 cells of a subset item and nothing else."""
    conditions = plan_conditions(LATE_THIRDS[28])
    france = {"concept": "France", "control": "Canada"}          # both primes
    lion = {"concept": "lion", "control": "tiger"}               # neither
    july = {"concept": "July", "control": "October"}             # control only
    assert [c["name"] for c in conditions if is_m1_recorded(c, france)] == [
        "clean", condition_name("Canada"), condition_name("France")]
    assert [c["name"] for c in conditions if is_m1_recorded(c, lion)] == ["clean"]
    assert [c["name"] for c in conditions if is_m1_recorded(c, july)] == [
        "clean", condition_name("October")]
    assert all(is_m3_recorded(c, france) for c in conditions)
    assert not any(is_m3_recorded(c, lion) for c in conditions)


def test_off_target_is_twelve_for_every_gate_arm_concept_and_eleven_for_a_prime():
    """The gate statistic is 'survives all 12'. A non-subset probe faces all 12
    primes; a subset probe faces 11 (its own direction is the diagonal, not
    off-target) — which is exactly why the gate arm excludes the subset."""
    for concept in {i["concept"] for i in _items()} - set(SUBSET):
        assert len(off_target_directions(concept)) == 12
    for concept in SUBSET:
        assert len(off_target_directions(concept)) == 11
        assert concept not in off_target_directions(concept)


# --- the power table, cross-checked against the recorded artifacts ------------

@pytest.mark.parametrize("subject", SUBJECTS)
def test_every_realized_n_is_fixed_before_the_run(subject):
    """Gating is the deterministic clean arm and every clean cell is M1-recorded,
    so the brief's power table is knowable now. A run that disagrees is an
    INVALID cross-check, not a power surprise — that claim is only true if these
    numbers really do come out of the recorded artifacts."""
    expected = PRE_REGISTERED[subject]
    battery, recorded = _by_name(), _m1(subject)
    gated = [
        r for r in recorded["items"]
        if oracle.says_concept_prefix(
            r["cells"]["clean"]["greedy_3"], battery[r["name"]]["concept"]
        )
    ]
    arm = _recorded_gate_arm(subject)
    concepts = {battery[r["name"]]["concept"] for r in arm}
    assert len(gated) == expected["gated"]
    assert len(arm) == expected["arm"] >= MIN_N
    assert len(concepts) == expected["concepts"] >= MIN_N
    assert 48 - len(concepts) == expected["zero_gated"]
    assert len(arm) * 12 == expected["new_pool"]


@pytest.mark.parametrize("subject", SUBJECTS)
def test_the_pre_registered_ceiling_comes_from_cells_m1_already_recorded(subject):
    """6 / 8 / 15 gate-arm cells are M1 `control_late` cells whose direction is a
    prime, so their outcomes were fixed before the run and their misses cap the
    arm at 35/41, 69/71, 82/84. A fact about the arm, never evidence for the
    gate."""
    expected = PRE_REGISTERED[subject]
    battery = _by_name()
    arm = _recorded_gate_arm(subject)
    already = [r for r in arm if battery[r["name"]]["control"] in SUBSET]
    misses = [
        r["name"] for r in already
        if not oracle.says_concept_prefix(
            r["cells"]["control_late"]["greedy_3"], battery[r["name"]]["concept"]
        )
    ]
    assert len(already) == expected["recorded_in_m1"]
    assert len(arm) * 12 - len(already) == expected["never_measured"]
    assert len(arm) - len(misses) == expected["ceiling"]


def test_the_bar_needs_44_of_71_at_1_5b_and_43_fails():
    """The brief's worked bar, computed with the project's own frozen ruler."""
    assert wilson(44, 71)[0] >= SURVIVAL_LOWER_BOUND
    assert wilson(43, 71)[0] < SURVIVAL_LOWER_BOUND
    # and the rejected shrinking denominator would have passed the same numerator
    assert wilson(43, 69)[0] >= SURVIVAL_LOWER_BOUND


# --- the D9(b) residual selector (the F16 defect, pinned from both sides) ------

@pytest.mark.parametrize("subject", SUBJECTS)
def test_the_residual_selector_selects_exactly_the_cells_the_brief_counted(subject):
    """0 / 2 / 2 gate-arm clean cells — 1.5B beetle-1 and butterfly-1, 3B
    trumpet-3 and butterfly-1. This is the brief's own count, and the mitigation
    it feeds is only worth anything if the set is non-empty where it says."""
    battery = _by_name()
    selected = sorted(
        r["name"] for r in _recorded_gate_arm(subject)
        if is_residual_cell(
            r["cells"]["clean"]["greedy_3"], battery[r["name"]]["concept"]
        )
    )
    assert selected == PRE_REGISTERED[subject]["residual"]


@pytest.mark.parametrize("subject", SUBJECTS)
def test_a_case_exact_selector_would_select_nothing(subject):
    """The F16 defect: the recorded spans are capitalised ('Beetle') and the
    roster spellings are not, so a case-EXACT rule silently turns the whole
    residual-conservative read into a no-op. The frozen selector compares
    case-insensitively, exactly as `oracle.says_concept_prefix` does."""
    battery = _by_name()
    case_exact = [
        r["name"] for r in _recorded_gate_arm(subject)
        if r["cells"]["clean"]["greedy_3"].lstrip() == battery[r["name"]]["concept"]
    ]
    assert case_exact == []


def test_the_selector_is_not_fills_the_span_which_would_select_every_cell():
    """The other failure direction: every recorded `greedy_3` is exactly
    SPAN_TOKENS tokens by construction, so 'the span is full' selects all of
    them. The frozen rule is 'the span EQUALS the spelling with nothing
    following it'."""
    assert is_residual_cell("Beetle", "beetle")          # nothing follows
    assert not is_residual_cell("Beetle<|im_end|>", "beetle")   # a boundary IS observed
    assert not is_residual_cell("Beetlejuice", "beetle")        # a longer word
    assert is_residual_cell("  Butterfly", "butterfly")   # leading whitespace stripped
    assert not is_residual_cell("Butterfly ", "butterfly")  # a trailing space closes it
    assert not is_residual_cell("France<|im_end|>\n", "France")


def test_the_recorded_span_is_always_full_which_is_why_the_span_bar_cannot_catch_it():
    """`greedy_continuation` always decodes exactly SPAN_TOKENS tokens, so D22's
    span bar passes at exactly <= 3 tokens — which IS the residual condition. The
    residual is carried by disclosure plus the conservative read, never by a bar."""
    class _Stub:
        tokenizer = types.SimpleNamespace(decode=lambda ids: "|".join(map(str, ids)))

    calls = []

    def fake_logits(subject, ids, edits):
        calls.append(edits)
        return torch.tensor([0.0, 1.0, 0.0])

    original = m4_strip.output_logits
    m4_strip.output_logits = fake_logits
    try:
        span = m4_strip.greedy_continuation(
            _Stub(), torch.tensor([[7]]), {0: "edit"}, first_id=5
        )
    finally:
        m4_strip.output_logits = original
    assert span == "5|1|1"                       # exactly SPAN_TOKENS ids
    assert len(calls) == oracle.SPAN_TOKENS - 1  # edits re-applied every pass
    assert all(c == {0: "edit"} for c in calls)


# --- the gate arithmetic and its two conservative reads -----------------------

def _cell(produced, greedy_id=1, mass=0.9, residual=False):
    return {"produced": produced, "greedy_3": "X", "residual": residual,
            "produced_first_token": produced, "greedy": "X", "greedy_id": greedy_id,
            "concept_mass": mass, "says_concept_in_3": produced}


def _record(name, concept, category, control="Canada", gate=True, misses=(),
            residual=(), eligible=True):
    """One graded item. `misses` names the primes whose cell is a miss;
    `residual` names the conditions ('clean' or a prime) whose cell is a D9(b)
    residual."""
    cells = {"clean": _cell(gate, residual="clean" in residual)}
    for word in SUBSET:
        cells[condition_name(word)] = _cell(word not in misses, residual=word in residual)
    return {
        "name": name, "category": category, "concept": concept, "control": control,
        "source": "constructed", "in_subset": concept in SUBSET,
        "direction_key": "bare", "mass_channel_eligible": eligible, "cells": cells,
        "gate_span": gate, "gate_first_token": gate, "gate_verbatim_p": True,
    }


def _package(records, confounds=()):
    return strip_package(records, concept_categories(_items()), _Tok(), list(confounds))


def _arm(n_survivors, n_total, concept_pool=("lion", "shark", "gold", "ruby")):
    """`n_total` gated non-subset items, `n_survivors` of which survive all 12."""
    categories = concept_categories(_items())
    records = []
    for i in range(n_total):
        concept = concept_pool[i % len(concept_pool)]
        records.append(_record(
            f"item-{i}", concept, categories[concept],
            misses=() if i < n_survivors else ("France",),
        ))
    return records


def test_the_gate_is_the_survives_all_twelve_conjunction_on_the_gated_non_subset():
    package = _package(
        _arm(30, 40)
        # a subset item and an ungated item are both outside the arm
        + [_record("france-1", "France", "countries", control="Canada")]
        + [_record("out-1", "lion", "animals", gate=False)]
    )
    gate = package["vocabulary_sparing"]["gate_arm"]
    assert (gate["k"], gate["n"]) == (30, 40)
    assert package["competence"]["gate_span"] == 41   # the subset item is gated too
    assert package["competence"]["gate_arm_n"] == 40


def test_a_single_fragile_cell_fails_an_item():
    """survives-all-12 is the strictest sparing statistic — the trade-off the
    brief owns, and the bias direction runs against the claim."""
    record = _record("lion-1", "lion", "animals", misses=("silver",))
    assert not survives_all(record, off_target_directions("lion"))
    assert survives_all(_record("lion-2", "lion", "animals"), off_target_directions("lion"))


def test_the_residual_conservative_read_fails_in_place():
    """D20's pre-registered denominator: the arm stays at its as-scored n and a
    residual-affected item scores as a FAILURE. The rejected alternative would
    have un-gated the item and shrunk the arm — the less conservative reading at
    the bar."""
    records = _arm(44, 71)
    # two survivors carry a residual CLEAN cell — the 1.5B situation exactly
    records[0]["cells"]["clean"]["residual"] = True
    records[1]["cells"]["clean"]["residual"] = True
    reads = _package(records)["vocabulary_sparing"]["conservative_reads"]
    residual = next(r for r in reads if r["read"] == "residual-conservative")
    assert (residual["k"], residual["n"]) == (42, 71)   # NOT 42/69


def test_a_residual_off_target_cell_also_fails_its_item():
    """The read re-scores EVERY residual cell as a miss, not only clean ones."""
    records = _arm(44, 71)
    records[0]["cells"][condition_name("France")]["residual"] = True
    reads = _package(records)["vocabulary_sparing"]["conservative_reads"]
    residual = next(r for r in reads if r["read"] == "residual-conservative")
    assert (residual["k"], residual["n"]) == (43, 71)


def test_the_conservative_read_is_strictly_one_way():
    """It can only lower the floor, never rescue it: with no residual cells it
    equals the as-scored read exactly."""
    package = _package(_arm(44, 71))
    gate = package["vocabulary_sparing"]["gate_arm"]
    residual = package["vocabulary_sparing"]["conservative_reads"][0]
    assert (residual["k"], residual["n"]) == (gate["k"], gate["n"])


def test_the_concept_level_collapse_is_one_binary_per_concept():
    """Items cluster three-per-concept on the probe side. The collapse asks
    'every gated item of this concept survives all 12', over the non-subset
    concepts with >= 1 gated item."""
    categories = concept_categories(_items())
    records = [
        _record("lion-1", "lion", categories["lion"]),
        _record("lion-2", "lion", categories["lion"], misses=("France",)),
        _record("shark-1", "shark", categories["shark"]),
        _record("gold-1", "gold", categories["gold"]),
    ]
    reads = _package(records)["vocabulary_sparing"]["conservative_reads"]
    concept = next(r for r in reads if r["read"] == "concept-level")
    assert (concept["k"], concept["n"]) == (2, 3)   # lion fails, shark + gold survive


def test_the_conservative_reads_are_reported_in_the_frozen_order():
    reads = _package(_arm(30, 40))["vocabulary_sparing"]["conservative_reads"]
    assert [r["read"] for r in reads] == list(CONSERVATIVE_READ_ORDER)


# --- the verdict string and its qualifier -------------------------------------

def _gate(k, n):
    lo, hi = wilson(k, n)
    return {"k": k, "n": n, "rate": k / n, "wilson_95": [lo, hi]}


def _read(name, k, n):
    lo, hi = wilson(k, n)
    return {"read": name, "k": k, "n": n, "rate": k / n, "wilson_95": [lo, hi]}


def test_the_verdict_string_is_the_frozen_template_worked_example():
    """The brief states the template once and this implements it verbatim —
    including the brief's own worked example, byte for byte."""
    assert strip_verdict(
        True, [], _gate(44, 71),
        [_read("residual-conservative", 42, 71), _read("concept-level", 30, 41)],
    ) == (
        "VOCAB-SPARING (44/71 survive all 12 = 0.620; Wilson 95% lower 0.503) — "
        "AS-SCORED ONLY (residual-conservative 42/71 = 0.592, lower 0.475)"
    )


def test_the_failing_label_is_the_lineage_null_and_carries_its_proportion():
    """Amendment 2 (i): failing a Wilson LOWER bound does not establish the
    contrary — at 1.5B k = 40 has a point estimate ABOVE the bar with a
    straddling interval — so the failing label is `not shown`, never an
    assertive negative."""
    verdict = strip_verdict(True, [], _gate(40, 71), [_read("concept-level", 30, 41)])
    assert verdict.startswith(NULL_LABEL)
    assert "40/71 survive all 12 = 0.563" in verdict
    assert "NOT VOCAB-SPARING" not in verdict
    # the lineage precedent the amendment cites, checked rather than asserted:
    # all three predecessor runners emit this exact label on a failed gate
    for source in ("m1_battery.py", "m2_depth.py", "m3_matrix.py"):
        assert f'"{NULL_LABEL}"' in open(source).read()


def test_the_qualifier_fires_only_when_a_conservative_read_falls_below_the_bar():
    clean = [_read("residual-conservative", 44, 71), _read("concept-level", 35, 41)]
    assert QUALIFIER not in strip_verdict(True, [], _gate(44, 71), clean)
    below = [_read("residual-conservative", 42, 71), _read("concept-level", 35, 41)]
    assert QUALIFIER in strip_verdict(True, [], _gate(44, 71), below)


def test_the_qualifier_can_never_create_or_rescue_a_claim():
    """D17's carried rule: when the as-scored read is already below the bar there
    is no claim to scope, so the qualifier cannot appear beside `not shown`."""
    verdict = strip_verdict(
        True, [], _gate(40, 71),
        [_read("residual-conservative", 38, 71), _read("concept-level", 20, 41)],
    )
    assert verdict.startswith(NULL_LABEL)
    assert QUALIFIER not in verdict


def test_the_qualifier_reads_the_lower_bound_not_the_point_estimate():
    """Read literally — and the frozen wording IS literal — the trigger is 'a
    conservative read's Wilson 95% lower bound is below 0.5', not 'a conservative
    read disagrees'. So a read that agrees perfectly on the point estimate but
    has a wide interval still fires the qualifier. That is the rule as ratified,
    and it is conservative in the right direction; it is pinned here so nobody
    'fixes' a frozen gate later. It cannot arise in M4's own runs, where the
    concept-level n is 23 / 41 / 43 — all >= MIN_N."""
    agreeing_but_wide = _read("concept-level", 2, 2)   # 1.000, lower 0.342
    assert agreeing_but_wide["rate"] == 1.0
    assert QUALIFIER in strip_verdict(True, [], _gate(30, 30), [agreeing_but_wide])


def test_both_reads_appear_in_the_frozen_order_when_both_fire():
    verdict = strip_verdict(
        True, [], _gate(45, 71),
        [_read("concept-level", 20, 41), _read("residual-conservative", 43, 71)],
    )
    fired = verdict.split(QUALIFIER, 1)[1]
    assert fired.index("residual-conservative") < fired.index("concept-level")


def test_an_unknown_conservative_read_is_wrong_arm_input(capsys):
    """The read order is frozen wording, not a runtime choice."""
    with pytest.raises(SystemExit) as exc:
        verdict_string(PASS_LABEL, _gate(44, 71), [_read("made-up-read", 1, 71)])
    assert exc.value.code == 2
    assert "not in the pre-committed order" in capsys.readouterr().out


@pytest.mark.parametrize(
    "kwargs, expected",
    [
        ({"limit": 3}, "NOT A RESULT — smoke run"),
        ({"certified": False}, "NOT A RESULT — uncertified environment"),
        ({"degenerate_arms": ["new_pool_off_target"]}, "DEGENERATE"),
        ({"gate": _gate(10, 19)}, "UNDERPOWERED"),
    ],
)
def test_the_qualifier_never_attaches_above_bar_level(kwargs, expected):
    """Amendment 2 (iii), the whole point of the amendment: Amendment 1 attached
    AS-SCORED ONLY to NOT A RESULT / DEGENERATE / UNDERPOWERED, contradicting the
    D17 rule it cited. Precedence has already withheld the claim there, so the
    qualifier has nothing to scope."""
    call = {"certified": True, "degenerate_arms": [], "gate": _gate(44, 71),
            "conservative_reads": [_read("residual-conservative", 42, 71)],
            "limit": None}
    call.update(kwargs)
    verdict = strip_verdict(
        call["certified"], call["degenerate_arms"], call["gate"],
        call["conservative_reads"], call["limit"],
    )
    assert verdict.startswith(expected)
    assert QUALIFIER not in verdict


def test_verdict_precedence_is_frozen():
    """NOT A RESULT > DEGENERATE > UNDERPOWERED > the level bar."""
    reads = [_read("residual-conservative", 42, 71)]
    assert strip_verdict(False, ["new_pool_off_target"], _gate(1, 2), reads, 5).startswith(
        "NOT A RESULT — smoke run")
    assert strip_verdict(False, ["new_pool_off_target"], _gate(1, 2), reads).startswith(
        "NOT A RESULT — uncertified")
    assert strip_verdict(True, ["new_pool_off_target"], _gate(1, 2), reads).startswith(
        "DEGENERATE")
    assert strip_verdict(True, [], _gate(1, 2), reads).startswith("UNDERPOWERED")
    assert strip_verdict(True, [], _gate(44, 71), reads).startswith(PASS_LABEL)


def test_the_bar_is_at_or_above_not_strictly_above():
    """'has its Wilson 95% lower bound AT OR ABOVE 0.5' — read literally."""
    gate = _gate(44, 71)
    gate["wilson_95"] = [SURVIVAL_LOWER_BOUND, 0.9]
    assert strip_verdict(True, [], gate, []).startswith(PASS_LABEL)
    gate["wilson_95"] = [SURVIVAL_LOWER_BOUND - 1e-9, 0.9]
    assert strip_verdict(True, [], gate, []).startswith(NULL_LABEL)


# --- the re-scoped degeneracy guard -------------------------------------------

def _cells(pairs):
    return [_cell(produced, greedy_id=token) for produced, token in pairs]


def test_the_dispositive_guard_pools_wrong_openings_only():
    """D14's mechanism, carried: the attractor is taken over NON-PRODUCED cells,
    with the share against the arm's full cell count."""
    guard = wrong_opening_degeneracy(
        _cells([(True, 9), (True, 9), (False, 4), (False, 4)]), _Tok()
    )
    assert guard["attractor_token"] == "tok4"
    assert guard["share"] == 0.5 and guard["collapsed"]
    assert wrong_opening_degeneracy(_cells([(True, 9)] * 4), _Tok())["collapsed"] is False


def test_the_dispositive_list_has_exactly_one_arm():
    """PR #9 F1's conjunction-degeneracy obligation, discharged by design: M4's
    gate is single-clause, so the surviving-side list is exactly the pooled
    non-subset off-target arm — and the frozen wording names it."""
    wording = GATE_WORDING["degeneracy"]
    assert "SINGLE-CLAUSE" in wording and "exactly ONE surviving arm" in wording
    assert "NON-SUBSET OFF-TARGET arm" in wording
    assert "subset DIAGONAL => TAG only" in wording
    assert "`clean` stays off the dispositive list" in wording
    assert "every surviving arm goes on this list" in wording


# --- the D21 cross-mention confound -------------------------------------------

def test_the_cross_mention_list_is_exactly_the_frozen_five():
    battery = json.load(open(m4_strip.ITEMS_PATH))
    scanned = cross_mention_pairs(_items(), battery["forbidden_forms"])
    assert sorted(scanned) == sorted(CROSS_MENTION_PAIRS)
    assert len(CROSS_MENTION_PAIRS) == 5


def test_the_prefix_rule_is_what_finds_the_inflected_mention():
    """D5's own rule is a PREFIX rule. A whole-word scan would miss
    `Egypt -> beetle-2` ('Ancient EgyptIANS carved amulets of the scarab'), which
    is exactly why the brief states the rule instead of assuming it."""
    clue = next(i for i in _items() if i["name"] == "beetle-2")["clue"]
    words = re.findall(r"[a-z']+", clue.lower())
    assert "egypt" not in words                       # a whole-word scan finds nothing
    assert any(w.startswith("egypt") for w in words)  # the prefix rule finds it
    assert ("Egypt", "beetle-2") in CROSS_MENTION_PAIRS


def test_a_drifted_clue_breaks_the_frozen_confound_list(monkeypatch):
    items = _items()
    for item in items:
        if item["name"] == "lion-1":
            item["clue"] = item["clue"] + " It happened in October."
    monkeypatch.setattr(m4_strip, "load_items", lambda path=m4_strip.ITEMS_PATH: items)
    with pytest.raises(ValueError, match="cross-mentions"):
        load_strip_items()


@pytest.mark.parametrize("subject", SUBJECTS)
def test_the_confound_cells_that_are_live_today_are_the_briefs_count(subject):
    """1 / 4 / 4 gate-bearing cells; `beetle-2` is ungated on all three subjects,
    so it carries none today and is listed only so a future re-gate cannot
    silently acquire one."""
    battery, recorded = _by_name(), _m1(subject)
    gated = {
        r["name"] for r in recorded["items"]
        if oracle.says_concept_prefix(
            r["cells"]["clean"]["greedy_3"], battery[r["name"]]["concept"]
        )
    }
    live = [(p, n) for p, n in CROSS_MENTION_PAIRS if n in gated]
    assert len(live) == PRE_REGISTERED[subject]["confound_cells"]
    assert "beetle-2" not in gated


def test_the_confound_cells_stay_in_the_gate_bearing_pool():
    """D21(a): a confounded miss can only LOWER the floor, so the bias runs
    against the gate. Excluding them would be evidence-removal in the gate's
    favour — the anti-conservative move the lineage never makes."""
    categories = concept_categories(_items())
    records = _arm(3, 4) + [
        _record("jade-1", "jade", categories["jade"], misses=("China",))
    ]
    package = _package(records, confounds=[("China", "jade-1")])
    gate = package["vocabulary_sparing"]["gate_arm"]
    assert gate["n"] == 5 and gate["k"] == 3      # jade-1 is IN the arm, and fails
    row = package["cross_mention_cells"][0]
    assert row["in_gate_arm"] and row["produced_under_prime"] is False


# --- D22(a): the run-time instrument bars, widened to all 60 ------------------

def test_the_bars_read_every_scored_word_plus_every_direction_word():
    words = scored_and_direction_words(_items())
    assert len(words) == 60
    assert set(SUBSET) <= set(words)
    assert set(words) == {i["concept"] for i in _items()} | set(SUBSET)


def test_a_word_longer_than_the_span_fails_the_bar(capsys):
    tok = _TableTok({"lion": 4, " lion": 4})
    with pytest.raises(SystemExit) as exc:
        check_run_time_bars(["lion", "shark"], tok)
    assert exc.value.code == 2
    assert "D22 span bar" in capsys.readouterr().out


def test_the_span_bar_reads_the_leading_space_form_not_only_the_bare_one(capsys):
    """`opal` is 1 token bare but 2 space-prefixed on all three tokenizers — the
    pinned case from D18's widening, carried."""
    tok = _TableTok({"opal": 1, " opal": 4})
    with pytest.raises(SystemExit) as exc:
        check_run_time_bars(["opal"], tok)
    assert exc.value.code == 2
    assert "bare=1 space=4" in capsys.readouterr().out


def test_a_non_ascii_word_fails_the_ascii_bar(capsys):
    with pytest.raises(SystemExit) as exc:
        check_run_time_bars(["café"], _TableTok({}))
    assert exc.value.code == 2
    assert "D22 ASCII bar" in capsys.readouterr().out


def test_the_bars_pass_and_record_their_measurements():
    bars = check_run_time_bars(["lion", "opal"], _TableTok({" opal": 3}))
    assert bars["worst_form_length"] == 3 and bars["all_ascii"]
    assert bars["words_checked"] == 2
    assert bars["form_lengths"]["opal"] == [1, 3]


@pytest.mark.parametrize("subject", SUBJECTS)
def test_the_whole_sixty_word_roster_clears_both_bars_on_the_real_tokenizer(subject):
    """The brief's advance verification (2026-07-28), pinned: all 60 concepts fit
    the 3-token span in both forms on all three Qwen2.5 tokenizers and are pure
    ASCII. The run-time bar still runs — D22's point is that the premise must
    hold at the moment of measurement."""
    tok = m4_strip.transformers.AutoTokenizer.from_pretrained(MODEL_IDS[subject])
    bars = check_run_time_bars(scored_and_direction_words(_items()), tok)
    assert bars["worst_form_length"] <= oracle.SPAN_TOKENS
    assert bars["words_checked"] == 60


def test_the_oracle_module_is_untouched_by_the_bars():
    """`oracle.py` is byte-shared by a fourth consumer now. The bars PIN its
    premises; they never alter its rule."""
    assert oracle.SPAN_TOKENS == 3
    assert oracle._BOUNDARY == r"(?![A-Za-z0-9])"
    assert oracle.says_concept_prefix(*oracle.SPAN_FILL_TEST_CASE[:2]) is (
        oracle.SPAN_FILL_TEST_CASE[2]
    )


# --- validate(): every wrong-arm guard proved by its printed reason ------------

class _FakeSpec:
    d_model = 896
    n_layers = 24


class _Args:
    def __init__(self, **kw):
        self.model_id = "Qwen/Qwen2.5-0.5B-Instruct"
        self.m1 = None
        self.m3 = None
        self.__dict__.update(kw)


def _good_artifact():
    return {"model_id": "Qwen/Qwen2.5-0.5B-Instruct", "d_model": 896,
            "J": {l: None for l in range(23)}}


def _bar_clearing_tok():
    table = {}
    for word in scored_and_direction_words(_items()):
        table[word] = table[" " + word] = 1
    return _TableTok(table)


@pytest.mark.parametrize(
    "mutate, expected",
    [
        (lambda a: a.update(model_id="Qwen/Qwen2.5-1.5B-Instruct"), "was fitted on"),
        (lambda a: a.update(d_model=1536), "d_model"),
        (lambda a: a.update(J={l: None for l in range(5)}), "lens layers"),
    ],
)
def test_validate_names_the_guard_that_fired(mutate, expected, capsys):
    artifact = _good_artifact()
    mutate(artifact)
    with pytest.raises(SystemExit) as exc:
        m4_strip.validate(_Args(), artifact, _FakeSpec(), _bar_clearing_tok())
    assert exc.value.code == 2
    assert expected in capsys.readouterr().out


def test_validate_accepts_the_real_configuration():
    band, m1, m3, bars = m4_strip.validate(
        _Args(), _good_artifact(), _FakeSpec(), _bar_clearing_tok()
    )
    assert band == list(range(9, 22))
    # both artifacts are RETURNED, so main() never re-parses either
    assert (m1["milestone"], m3["milestone"]) == ("M1", "M3")
    assert bars["worst_form_length"] == 1


def test_validate_runs_the_d22_bars_before_it_reaches_either_artifact(capsys):
    tok = _TableTok({}, default=4)
    with pytest.raises(SystemExit) as exc:
        m4_strip.validate(_Args(), _good_artifact(), _FakeSpec(), tok)
    assert exc.value.code == 2
    assert "D22 span bar" in capsys.readouterr().out


def _recorded_file(tmp_path, name, **fields):
    run = {
        "milestone": "M1", "model_id": "Qwen/Qwen2.5-0.5B-Instruct",
        "band": list(range(9, 22)), "smoke_limit": None,
        "environment": {"certified": True, "uncertified_reasons": []},
        "items": [],
    }
    run.update(fields)
    path = tmp_path / name
    path.write_text(json.dumps(run))
    return str(path)


@pytest.mark.parametrize("milestone", ["M1", "M3"])
@pytest.mark.parametrize(
    "overrides, expected",
    [
        ({"milestone": "M0"}, "is not an"),
        ({"model_id": "Qwen/Qwen2.5-3B-Instruct"}, "are for"),
        ({"band": [1, 2, 3]}, "were run on band"),
        ({"smoke_limit": 5}, "SMOKE run"),
        ({"environment": {"certified": False, "uncertified_reasons": ["device 'cpu'"]}},
         "NOT A RESULT"),
    ],
)
def test_a_cross_check_target_that_is_not_a_result_is_refused(
    milestone, overrides, expected, tmp_path, capsys
):
    """M4 refuses M1 OR M3 artifacts that were themselves not results — a run
    that was pre-declared not to be a result cannot certify anything."""
    fields = {"milestone": milestone, **overrides}
    args = _Args(**{
        milestone.lower(): _recorded_file(tmp_path, f"{milestone}.json", **fields)
    })
    with pytest.raises(SystemExit) as exc:
        m4_strip.validate(args, _good_artifact(), _FakeSpec(), _bar_clearing_tok())
    assert exc.value.code == 2
    assert expected in capsys.readouterr().out


@pytest.mark.parametrize("milestone", ["M1", "M3"])
def test_validate_rejects_a_missing_recording(milestone, tmp_path, capsys):
    args = _Args(**{milestone.lower(): str(tmp_path / "absent.json")})
    with pytest.raises(SystemExit) as exc:
        m4_strip.validate(args, _good_artifact(), _FakeSpec(), _bar_clearing_tok())
    assert exc.value.code == 2
    assert f"{milestone} results" in capsys.readouterr().out


@pytest.mark.parametrize("limit", [0, -1])
def test_a_non_positive_limit_is_wrong_arm_input(limit, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", [
        "m4_strip.py", "--model-id", "Qwen/Qwen2.5-0.5B-Instruct",
        "--lens", "lenses/qwen2.5-0.5b-instruct-n100.pt", "--limit", str(limit),
    ])
    with pytest.raises(SystemExit) as exc:
        m4_strip.main()
    assert exc.value.code == 2
    assert "--limit must be a positive item count" in capsys.readouterr().out


def test_a_dry_run_never_loads_the_checkpoint(monkeypatch, capsys):
    """PR #7 review F6's disposition, carried: a `--dry-run` or a wrong-arm exit
    must not pay for a checkpoint load. This passes only because no model was
    touched."""
    def refuse(*args, **kwargs):
        raise AssertionError("the checkpoint must not load on a --dry-run")

    monkeypatch.setattr(
        m4_strip.transformers.AutoModelForCausalLM, "from_pretrained", refuse
    )
    monkeypatch.setattr(sys, "argv", [
        "m4_strip.py", "--model-id", "Qwen/Qwen2.5-0.5B-Instruct",
        "--lens", "lenses/qwen2.5-0.5b-instruct-n100.pt", "--dry-run",
    ])
    with pytest.raises(SystemExit) as exc:
        m4_strip.main()
    assert exc.value.code == 0
    printed = capsys.readouterr().out
    assert "no checkpoint loaded" in printed
    assert "cells 2340" in printed
    assert "255 M1 cells / 468 M3 cells" in printed


# --- the two cross-checks -----------------------------------------------------

def _ours(name, concept, control, span="France<|im_end|>", greedy="France", mass=0.5):
    cells = {
        key: {"greedy": greedy, "greedy_3": span, "concept_mass": mass}
        for key in ["clean"] + [condition_name(w) for w in SUBSET]
    }
    return {"name": name, "concept": concept, "control": control, "cells": cells}


def _theirs_m1(name, span="France<|im_end|>", greedy="France", mass=0.5):
    return {"name": name, "cells": {
        c: {"greedy": greedy, "greedy_3": span, "concept_mass": mass}
        for c in m4_strip.M1_SHARED_CONDITIONS}}


def _theirs_m3(name, span="France<|im_end|>", greedy="France", mass=0.5):
    return {"name": name, "cells": {
        c: {"greedy": greedy, "greedy_3": span, "concept_mass": mass}
        for c in ["clean"] + [condition_name(w) for w in SUBSET]}}


def test_the_m1_cross_check_maps_direction_cells_onto_m1s_condition_names():
    """M4 keys cells by ablated direction; M1 keyed them by condition. The
    mapping is per item, and a non-prime concept or control contributes no cell."""
    mismatches, texture = m4_strip.m1_crosscheck(
        [_ours("france-1", "France", "Canada"),      # both primes -> 3 cells
         _ours("july-1", "July", "October"),         # control only -> 2 cells
         _ours("lion-1", "lion", "tiger")],          # neither -> 1 cell
        {"items": [_theirs_m1(n) for n in ("france-1", "july-1", "lion-1")]},
    )
    assert mismatches == []
    assert texture["cells_checked"] == 6
    assert texture["items_checked"] == 3


def test_the_m3_cross_check_reads_only_the_subset_items_and_all_thirteen_cells():
    mismatches, texture = m4_strip.m3_crosscheck(
        [_ours("france-1", "France", "Canada"), _ours("lion-1", "lion", "tiger")],
        {"items": [_theirs_m3("france-1")]},
    )
    assert mismatches == []
    assert (texture["items_checked"], texture["cells_checked"]) == (1, 13)
    assert texture["cells_expected"] == EXPECTED_M3_CELLS


@pytest.mark.parametrize("field, drift", [("greedy", ("Paris",)), ("greedy_3", ("Paris!",))])
def test_the_cross_checks_catch_a_drifted_string_on_either_recorded_field(field, drift):
    kwargs = {"greedy": drift[0]} if field == "greedy" else {"span": drift[0]}
    for checker, theirs in (
        (m4_strip.m1_crosscheck, _theirs_m1("france-1", **kwargs)),
        (m4_strip.m3_crosscheck, _theirs_m3("france-1", **kwargs)),
    ):
        mismatches, _ = checker(
            [_ours("france-1", "France", "Canada")], {"items": [theirs]}
        )
        assert mismatches and all(field in m for m in mismatches)


def test_the_cross_checks_treat_mass_as_texture_and_flag_an_absent_item():
    mismatches, texture = m4_strip.m1_crosscheck(
        [_ours("france-1", "France", "Canada", mass=0.5)],
        {"items": [_theirs_m1("france-1", mass=0.9)]},
    )
    assert mismatches == [] and texture["mass_cells_equal"] == 0
    mismatches, _ = m4_strip.m3_crosscheck(
        [_ours("france-1", "France", "Canada")], {"items": []}
    )
    assert mismatches == ["france-1: absent from the M3 recording"]


def test_the_cross_checks_are_oracle_independent():
    """They compare raw recorded strings, so D9 cannot soften them: two cells
    that the oracle scores identically still mismatch if the strings differ."""
    ours = _ours("france-1", "France", "Canada", span="France<|im_end|>")
    theirs = _theirs_m1("france-1", span="France!")
    assert oracle.says_concept_prefix("France<|im_end|>", "France")
    assert oracle.says_concept_prefix("France!", "France")
    mismatches, _ = m4_strip.m1_crosscheck([ours], {"items": [theirs]})
    assert mismatches


# --- the descriptive package --------------------------------------------------

def test_the_row_and_column_profiles_split_the_wider_vocabulary():
    categories = concept_categories(_items())
    records = [
        _record("lion-1", "lion", categories["lion"], misses=("silver",)),
        _record("gold-1", "gold", categories["gold"], misses=("silver",)),
        _record("france-1", "France", "countries"),
    ]
    package = _package(records)
    rows = package["row_profiles"]
    assert len(rows) == 12
    assert rows["silver"]["collateral_non_subset"]["hits"] == 0
    assert rows["silver"]["collateral_non_subset"]["n"] == 2
    # gold is a precious metal, so silver's damage to it is within-category
    assert rows["silver"]["collateral_non_subset_within_category"]["n"] == 1
    assert rows["silver"]["collateral_non_subset_cross_category"]["n"] == 1
    columns = package["column_profiles"]
    assert columns["lion"]["fragility"]["n"] == 12 and columns["lion"]["in_subset"] is False
    assert columns["France"]["fragility"]["n"] == 11 and columns["France"]["in_subset"]


def test_the_pooled_view_is_texture_and_repeats_each_item_twelve_times():
    """M3's F11 lesson applied in advance: the 852-cell pool would give the gate
    an interval NARROWER than the clustering justifies, so the gate reads the
    per-item conjunction and the pool is reported as texture."""
    package = _package(_arm(30, 40))
    assert package["new_pool_arms"]["off_target"]["n"] == 40 * 12
    assert package["vocabulary_sparing"]["gate_arm"]["n"] == 40
    assert "that pool is TEXTURE and the gate reads the per-item conjunction" in (
        GATE_WORDING["honesty"]
    )


def test_the_cluster_mean_floor_is_reported_but_never_gating():
    """M3's F15 readout carried for comparability only — D17 froze its binomial
    approximation as 'acceptable only because the qualifier is never
    dispositive', and M4 keeps that rationale intact by not promoting it."""
    package = _package(_arm(30, 40))
    floor = package["vocabulary_sparing"]["cluster_mean_floor"]
    assert floor["reference_line"] == 0.5
    assert "NEVER gating" in floor["readout"]
    assert "below_reference_line" in floor and "verdict" not in floor


def test_the_ordering_contrast_is_reported_as_rejected_option_b():
    package = _package(
        _arm(30, 40) + [_record("france-1", "France", "countries", misses=SUBSET)]
    )
    ordering = package["vocabulary_sparing"]["ordering_contrast"]
    assert "rejected option (b)" in ordering["label"]
    assert ordering["diagonal"]["hits"] == 0        # France muted on its own direction
    assert ordering["excludes_zero"]


def test_the_ceiling_readout_names_the_cells_fixed_before_the_run():
    categories = concept_categories(_items())
    records = [
        _record("july-3", "July", categories["July"], control="October",
                misses=("October",)),
        _record("lion-1", "lion", categories["lion"], control="tiger"),
    ]
    ceiling = _package(records)["gate_arm_ceiling"]
    assert ceiling["cells_recorded_in_m1"] == 1
    assert ceiling["misses"] == ["july-3"]
    assert ceiling["ceiling"] == 1 and ceiling["n"] == 2
    assert "never evidence for the gate" in ceiling["note"]


def test_zero_gated_concepts_are_recorded_as_the_competence_selection():
    categories = concept_categories(_items())
    records = [
        _record("lion-1", "lion", categories["lion"]),
        _record("moth-1", "moth", categories["moth"], gate=False),
    ]
    competence = _package(records)["competence"]
    assert competence["zero_gated_non_subset_concepts"] == ["moth"]
    assert "COMPETENCE SELECTION" in GATE_WORDING["competence"]
    assert "MEASURABLE vocabulary" in GATE_WORDING["competence"]


# --- the frozen wording -------------------------------------------------------

def test_the_gate_wording_is_frozen_as_code_and_carries_both_amendments():
    sparing = GATE_WORDING["sparing"]
    # the gate itself
    assert "at or above 0.5" in sparing and "SURVIVES ALL 12" in sparing
    assert "NON-SUBSET" in sparing
    # Amendment 1: the qualifier, with its own mechanism
    assert "AS-SCORED ONLY" in sparing
    assert "CAN NEVER CREATE OR RESCUE ONE" in sparing
    # Amendment 2 (i) the null label, (ii) 0.5B scoped in, (iii) the attachment
    # restriction, (iv) both templates stated explicitly
    assert "'not shown'" in sparing and "never an assertive negative" in sparing
    assert "never a 'not shown' gate claim" in sparing
    assert "never to NOT A RESULT, DEGENERATE or UNDERPOWERED" in sparing
    assert "<label> (k/n survive all 12 = <rate>; Wilson 95% lower <lo>)" in sparing
    assert "AS-SCORED ONLY (<read> k/n = <rate>, lower <lo>[; <read> ...])" in sparing
    assert "residual-conservative, concept-level" in sparing
    # the constant is owned as new, with its per-cell equivalence frozen in
    assert "0.5^(1/12) ~ 0.944" in sparing
    assert "SINGLE DISPOSITIVE GATE" in sparing
    # and the re-certification precondition is INSIDE the sentence
    assert "read ONLY when the 468 M3-recorded and 255 M1-recorded cells" in sparing


def test_the_residual_selector_is_stated_in_the_frozen_wording():
    """The selector decides a mitigation's whole content, so the rule that
    decides its set lives in the frozen wording, not only in the code."""
    wording = GATE_WORDING["conservative_reads"]
    assert "CASE-INSENSITIVELY" in wording
    assert "case-EXACT comparison would select ZERO cells" in wording
    assert "NOT 'the span fills the 3-token window'" in wording
    assert "FAIL IN PLACE" in wording and "41 / 71 / 84" in wording


def test_the_verdict_string_templates_in_the_wording_match_the_code():
    """The one place prose and code can drift is a format string. This pins the
    frozen example against what `verdict_string()` actually emits."""
    worked = verdict_string(
        PASS_LABEL, _gate(44, 71),
        [_read("residual-conservative", 42, 71)],
    )
    assert worked in GATE_WORDING["sparing"].replace("'", "")


@pytest.mark.parametrize("subject", SUBJECTS)
def test_the_earlier_milestones_wordings_stay_byte_frozen_with_their_artifacts(subject):
    """Each stage freezes its own wording; M4 imports none of them and edits
    none of them."""
    assert _m1(subject)["protocol"]["gate_wording"] == m1_battery.GATE_WORDING
    assert _m3(subject)["protocol"]["gate_wording"] == m3_matrix.GATE_WORDING
    assert GATE_WORDING != m3_matrix.GATE_WORDING
    assert GATE_WORDING["oracle"] == oracle.ORACLE_WORDING  # the one shared rule


def test_the_oracle_is_byte_shared_by_a_fourth_consumer():
    """The deviations-table row, pinned: `m4_strip.py` imports the rule rather
    than copying it, exactly as the first three consumers do."""
    source = open("m4_strip.py").read()
    assert "from oracle import" in source
    assert "def says_concept_prefix" not in source


# --- the cross-subject verdict ------------------------------------------------

def _crosscheck(**overrides):
    base = {"n_mismatches": 0, "items_checked": 180, "items_expected": 180,
            "cells_checked": 255, "cells_expected": 255}
    base.update(overrides)
    return base


def _run(verdict=None, k=44, n=71, **kw):
    gate = _gate(k, n)
    verdict = verdict if verdict is not None else strip_verdict(
        True, [], gate, [_read("residual-conservative", k, n)]
    )
    run = {
        "milestone": "M4", "smoke_limit": None,
        "environment": {"certified": True, "uncertified_reasons": []},
        "m1_crosscheck": _crosscheck(),
        "m3_crosscheck": _crosscheck(items_checked=36, items_expected=36,
                                     cells_checked=468, cells_expected=468),
        "competence": {"items_run": 180, "gate_span": 105},
        "vocabulary_sparing": {
            "gate_arm": gate, "verdict": verdict,
            "conservative_reads": [_read("residual-conservative", k, n)],
            "cluster_mean_floor": {"k": 60, "n": n, "wilson_95": [0.7, 0.9],
                                   "reference_line": 0.5},
            "ordering_contrast": {
                "newcombe_offtarget_minus_diagonal_naming": [0.9, 0.8, 0.95]},
        },
        "new_pool_arms": {
            "within_category": {"hits": 100, "n": 110, "wilson_95": [0.8, 0.95]},
            "cross_category": {"hits": 700, "n": 742, "wilson_95": [0.9, 0.97]},
        },
        "row_profiles": {p: {"collateral_non_subset": {"hits": 70, "n": 71,
                                                       "rate": 70 / 71}}
                         for p in SUBSET},
        "column_profiles": {"silver": {"gated_items": 3, "in_subset": True,
                                       "fragility": {"hits": 30, "n": 33, "rate": 0.9}}},
    }
    run.update(kw)
    return run


def _run_verdict(monkeypatch, tmp_path, runs):
    for subject, run in runs.items():
        (tmp_path / f"m4-strip-{subject}.json").write_text(json.dumps(run))
    monkeypatch.setattr(sys, "argv", ["m4_verdict.py", "--results-dir", str(tmp_path)])
    with pytest.raises(SystemExit) as exc:
        m4_verdict.main()
    return exc.value.code


def _all(**per_subject):
    runs = {s: _run() for s in SUBJECTS}
    runs.update(per_subject)
    return runs


def test_the_m4_verdict_is_the_and_over_the_two_gate_bearing_subjects(
    monkeypatch, tmp_path, capsys
):
    assert _run_verdict(monkeypatch, tmp_path, _all()) == 0
    out = capsys.readouterr().out
    assert f"M4 VERDICT: {PASS_LABEL} at 1.5B AND 3B" in out


def test_a_single_gate_bearing_null_sinks_the_and(monkeypatch, tmp_path, capsys):
    runs = _all(**{"qwen2.5-3b-instruct": _run(k=40)})
    assert _run_verdict(monkeypatch, tmp_path, runs) == 0
    out = capsys.readouterr().out.rsplit("M4 VERDICT:", 1)[-1]
    assert NULL_LABEL.upper() in out


def test_the_0_5b_subject_never_enters_the_and(monkeypatch, tmp_path, capsys):
    """Amendment 2 (ii): 0.5B is reported in the same shape under its standing
    any-direction-damage frame and is never a gate claim. M3's own 0.5B subset
    already fails this bar in-statistic, so a low reading there is a finding."""
    runs = _all(**{"qwen2.5-0.5b-instruct": _run(k=20)})
    assert _run_verdict(monkeypatch, tmp_path, runs) == 0
    out = capsys.readouterr().out
    assert f"M4 VERDICT: {PASS_LABEL} at 1.5B AND 3B" in out
    assert "never gate-bearing" in out
    assert "19/28, lower 0.4934" in out


def test_the_cross_subject_verdict_carries_a_gate_bearing_qualifier(
    monkeypatch, tmp_path, capsys
):
    scoped = _run(verdict=strip_verdict(
        True, [], _gate(44, 71),
        [_read("residual-conservative", 42, 71)],
    ))
    runs = _all(**{"qwen2.5-1.5b-instruct": scoped})
    assert _run_verdict(monkeypatch, tmp_path, runs) == 0
    out = capsys.readouterr().out.rsplit("M4 VERDICT:", 1)[-1]
    assert f"{QUALIFIER} (qwen2.5-1.5b-instruct)" in out


@pytest.mark.parametrize(
    "broken, expected",
    [
        ({"smoke_limit": 3}, "SMOKE run"),
        ({"environment": {"certified": False, "uncertified_reasons": ["device 'cpu'"]}},
         "NOT A RESULT"),
        ({"milestone": "M3"}, "not an M4 strip run"),
        ({"m1_crosscheck": _crosscheck(n_mismatches=4)}, "M1 cross-check mismatches"),
        ({"m1_crosscheck": _crosscheck(items_checked=179)},
         "M1 cross-check covered 179 of 180 items"),
        ({"m1_crosscheck": _crosscheck(cells_checked=254)},
         "M1 cross-check covered 254 of 255 cells"),
        ({"m3_crosscheck": _crosscheck(items_checked=36, items_expected=36,
                                       cells_checked=467, cells_expected=468)},
         "M3 cross-check covered 467 of 468 cells"),
    ],
)
def test_a_run_that_is_not_a_result_cannot_feed_the_verdict(
    broken, expected, monkeypatch, tmp_path, capsys
):
    runs = _all(**{"qwen2.5-1.5b-instruct": _run(**broken)})
    assert _run_verdict(monkeypatch, tmp_path, runs) == 2
    assert expected in capsys.readouterr().out


def test_the_verdict_is_invalid_when_a_subject_is_missing(monkeypatch, tmp_path, capsys):
    runs = {s: _run() for s in m4_verdict.SUBJECTS if s != "qwen2.5-3b-instruct"}
    assert _run_verdict(monkeypatch, tmp_path, runs) == 2
    assert "missing" in capsys.readouterr().out

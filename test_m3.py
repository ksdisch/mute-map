"""test_m3.py — invariants for the M3 specificity matrix.

The heavyweight proof that M3's instrument is still the certified instrument is
the 108-cell M1 cross-check the runner performs at run time, before it reads a
single off-diagonal cell. These tests pin what a model run cannot: D18(a)'s two
run-time bars and the premises they carry, the frozen matrix plan's arithmetic,
the two gate clauses (including clause (2)'s sibling restriction, which exists
precisely so silver cannot be scored a structural survivor), the
collateral-floor readout's cluster-mean collapse against the two dishonest
denominators it replaced, the pre-committed degeneracy scoping and verdict
precedence, and the INVALID paths — each asserted on the *printed reason*, not
merely the exit code (the M1 F9 pattern), so a test cannot pass because some
other guard fired.

Several tests read the *committed* M1 and M2 artifacts. That is deliberate: the
M3 brief pre-registers numbers computed from them (every pooled n in the power
table, the recorded-control in/out-of-matrix split, the no-cross-mention
property of the frozen items), and a pre-registration that no test pins is one a
later edit can silently break.
"""
import json
import re
import sys
import types

import pytest
import torch

import m1_battery
import m2_depth
import m3_matrix
import m3_verdict
import oracle
from harness import MIN_N
from m3_matrix import (
    CONTROL_EXTRA_DIRECTIONS,
    EXPECTED_SUBSET_ITEMS,
    FLOOR_LOWER_BOUND,
    PLANNED_DIRECTIONS,
    SUBSET,
    SUBSET_STRATA,
    applies_to,
    check_run_time_bars,
    condition_name,
    conditions_for,
    load_subset_items,
    matrix_package,
    matrix_verdict,
    plan_conditions,
    planned_cells,
    within_category_siblings,
    wrong_opening_degeneracy,
)

SUBJECTS = ("qwen2.5-0.5b-instruct", "qwen2.5-1.5b-instruct", "qwen2.5-3b-instruct")
MODEL_IDS = {
    "qwen2.5-0.5b-instruct": "Qwen/Qwen2.5-0.5B-Instruct",
    "qwen2.5-1.5b-instruct": "Qwen/Qwen2.5-1.5B-Instruct",
    "qwen2.5-3b-instruct": "Qwen/Qwen2.5-3B-Instruct",
}
#: The brief's power table, pre-registered from the recorded clean arm.
PRE_REGISTERED = {
    "qwen2.5-0.5b-instruct": {"gated": 28, "off": 308, "within": 96, "restricted": 24,
                              "cross": 212},
    "qwen2.5-1.5b-instruct": {"gated": 34, "off": 374, "within": 100, "restricted": 28,
                              "cross": 274},
    "qwen2.5-3b-instruct": {"gated": 32, "off": 352, "within": 101, "restricted": 29,
                            "cross": 251},
}
LATE_THIRDS = {24: list(range(17, 22)), 28: list(range(19, 25)), 36: list(range(26, 33))}
SUBJECT_LAYERS = {"qwen2.5-0.5b-instruct": 24, "qwen2.5-1.5b-instruct": 28,
                  "qwen2.5-3b-instruct": 36}


def _m2(subject):
    return json.load(open(f"results/m2-depth-{subject}.json"))


def _categories():
    return m3_matrix.subset_categories(load_subset_items())


class _Tok:
    @staticmethod
    def decode(ids):
        return f"tok{ids[0]}"


class _TableTok:
    """A tokenizer stub whose token counts come from a table — the only way to
    exercise D18's bars without a roster edit the project would never make."""

    def __init__(self, table, default=1):
        self.table, self.default = table, default

    def __call__(self, text, add_special_tokens=False):
        return types.SimpleNamespace(input_ids=[0] * self.table.get(text, self.default))


# --- D18(a): the two run-time instrument bars ---------------------------------

def test_the_span_bar_reads_the_leading_space_form_not_only_the_bare_one(
    monkeypatch, capsys
):
    """Follow-up F5's pinned case. `opal` is 1 token bare and 2 space-prefixed on
    all three subject tokenizers, so a bare-form-only bar would pass a word whose
    *emitted* form — the space-prefixed one, which is what the recorded span
    actually holds — does not fit. SPAN_TOKENS is fabricated to 1 so the real
    roster's 3-token headroom cannot mask the asymmetry."""
    monkeypatch.setattr(m3_matrix, "SPAN_TOKENS", 1)
    tok = _TableTok({"opal": 1, " opal": 2})
    with pytest.raises(SystemExit) as exc:
        check_run_time_bars(["opal"], tok)
    assert exc.value.code == 2
    printed = capsys.readouterr().out
    assert "D18 span bar" in printed
    assert "'opal' bare=1 space=2" in printed  # the bare form alone would have passed


def test_a_word_longer_than_the_span_fails_the_bar(capsys):
    """The premise D9(b)/D10's soundness rests on: a prefix hit cannot be hidden
    by span truncation *because* every roster word fits the span."""
    tok = _TableTok({"unobtainium": 4, " unobtainium": 4})
    with pytest.raises(SystemExit) as exc:
        check_run_time_bars(["unobtainium"], tok)
    assert exc.value.code == 2
    assert "exceeds oracle.SPAN_TOKENS = 3" in capsys.readouterr().out


def test_a_non_ascii_word_fails_the_ascii_bar(capsys):
    """PR #7 F4's pin: `oracle._BOUNDARY` is ASCII-only, so a non-ASCII
    continuation would read as a word boundary and could score as a hit. M3 adds
    no vocabulary, so the rule does not change — the run refuses instead."""
    tok = _TableTok({"Köln": 1, " Köln": 1})
    with pytest.raises(SystemExit) as exc:
        check_run_time_bars(["Köln"], tok)
    assert exc.value.code == 2
    printed = capsys.readouterr().out
    assert "D18 ASCII bar" in printed and "needs a decision, not a run" in printed


def test_the_ascii_bar_fires_even_when_the_word_fits_the_span():
    """The two bars are independent: a short non-ASCII word clears the span bar
    and must still be refused."""
    tok = _TableTok({"é": 1, " é": 1})
    with pytest.raises(SystemExit):
        check_run_time_bars(["é"], tok)


def test_the_bars_pass_and_record_their_measurements():
    bars = check_run_time_bars(["France"], _TableTok({"France": 1, " France": 1}))
    assert bars == {
        "span_tokens": 3,
        "form_lengths": {"France": [1, 1]},
        "worst_form_length": 1,
        "all_ascii": True,
    }


def test_the_real_roster_clears_both_bars_on_every_subject_tokenizer():
    """The empirical claim D18 pins, measured rather than assumed — and the
    measurement that makes `opal` the right counter-example: it is the gemstone
    roster's 1-bare/2-space word on all three tokenizers, which is why the bar
    reads the max of the two forms."""
    import transformers

    for subject, model_id in MODEL_IDS.items():
        tok = transformers.AutoTokenizer.from_pretrained(model_id)
        bars = check_run_time_bars(list(PLANNED_DIRECTIONS), tok)
        assert bars["worst_form_length"] <= oracle.SPAN_TOKENS, subject
        assert m3_matrix.span_form_lengths("opal", tok) == (1, 2), subject


def test_the_oracle_module_is_untouched_by_the_bars():
    """D18 pins `oracle.py`'s premises without altering its rule — the module is
    byte-shared with `m1_rescore.py` and `m2_depth.py` and must stay identical."""
    assert oracle._BOUNDARY == r"(?![A-Za-z0-9])"
    assert oracle.SPAN_TOKENS == 3
    assert m3_matrix.says_concept_prefix is oracle.says_concept_prefix


# --- the frozen roster and the no-cross-mention premise -----------------------

def test_the_subset_is_m2s_pre_registered_twelve_verbatim():
    """D15(a): reuse, not re-derivation. The subset was frozen by D11's
    stratified rule before any M2 cell existed, so M3's selection surface was
    pre-registered two milestones ago — copied here per the standing
    cut-from-your-predecessor rule, and pinned equal so the copy cannot drift."""
    assert SUBSET == m2_depth.SUBSET
    assert SUBSET_STRATA == m2_depth.SUBSET_STRATA
    assert sorted(c for g in SUBSET_STRATA.values() for c in g) == sorted(SUBSET)


def test_the_frozen_subset_draws_thirty_six_verbatim_m1_items():
    items = load_subset_items()
    assert len(items) == EXPECTED_SUBSET_ITEMS == 36
    assert {i["concept"] for i in items} == set(SUBSET)
    battery = {i["name"]: i for i in m1_battery.load_items()}
    assert all(items[i] == battery[items[i]["name"]] for i in range(len(items)))


def test_the_out_of_subset_control_directions_are_the_frozen_six():
    """D16(a)'s +18 control-extra cells were pre-registered against the frozen
    pairings, so the pairings are checked rather than assumed."""
    items = load_subset_items()
    outside = sorted({i["control"] for i in items} - set(SUBSET))
    assert outside == sorted(CONTROL_EXTRA_DIRECTIONS)
    assert sorted(CONTROL_EXTRA_DIRECTIONS) == sorted(
        ["February", "Saturn", "Mercury", "guitar", "drum", "platinum"]
    )
    inside = sorted({i["control"] for i in items} & set(SUBSET))
    assert len(inside) == 6  # the six countries' controls are matrix cells


def test_a_subset_concept_missing_from_the_battery_is_invalid(monkeypatch):
    monkeypatch.setattr(m3_matrix, "SUBSET", SUBSET + ("Atlantis",))
    with pytest.raises(ValueError, match="missing pre-registered subset concept"):
        load_subset_items()


def test_a_drifted_control_pairing_is_refused(monkeypatch):
    monkeypatch.setattr(m3_matrix, "CONTROL_EXTRA_DIRECTIONS", ("February",))
    with pytest.raises(ValueError, match="out-of-subset control directions"):
        load_subset_items()


def test_no_subset_concept_clue_mentions_another_subset_concept():
    """The brief's pinned premise: an off-diagonal cell can never break because
    the ablated word literally appeared in the probe's clue text. Checked at a
    word boundary, case-insensitive, on the frozen items."""
    for item in load_subset_items():
        for other in SUBSET:
            if other == item["concept"]:
                continue
            assert not re.search(
                rf"\b{re.escape(other)}\b", item["clue"], re.IGNORECASE
            ), f"{item['name']} mentions {other}"


def test_within_category_siblings_leave_october_and_silver_empty():
    """Clause (2)'s restriction is structural, not a choice: October and silver
    have no same-category subset sibling, so their within-category collateral is
    an empty set and their items drop from that clause by construction."""
    categories = _categories()
    siblings = {c: within_category_siblings(c, categories) for c in SUBSET}
    assert siblings["October"] == [] and siblings["silver"] == []
    assert all(len(siblings[c]) == 5 for c in
               ("Brazil", "Canada", "China", "Egypt", "France", "Japan"))
    assert siblings["Jupiter"] == ["Mars"] and siblings["piano"] == ["violin"]
    # the lopsided-category honesty row: 30 of the 34 within-category ordered
    # pairs are country pairs
    ordered = sum(len(v) for v in siblings.values())
    countries = sum(len(siblings[c]) for c in
                    ("Brazil", "Canada", "China", "Egypt", "France", "Japan"))
    assert (ordered, countries) == (34, 30)


# --- the frozen condition plan ------------------------------------------------

def test_the_plan_grades_the_pre_registered_486_cells():
    """36 clean + 432 matrix + 18 control-extra — the wall-clock plan, 0.9x an M1
    subject run."""
    items = load_subset_items()
    conditions = plan_conditions(LATE_THIRDS[28])
    assert len(conditions) == 1 + len(SUBSET) + len(CONTROL_EXTRA_DIRECTIONS) == 19
    assert planned_cells(conditions, items) == 486
    matrix_cells = sum(
        1 for item in items for c in conditions
        if c["group"] == "matrix" and applies_to(c, item)
    )
    extra_cells = sum(
        1 for item in items for c in conditions
        if c["group"] == "control_extra" and applies_to(c, item)
    )
    assert (matrix_cells, extra_cells) == (432, 18)


def test_a_control_extra_direction_is_graded_only_on_its_own_concepts_items():
    """They are not matrix cells: they complete the recorded control surface and
    give October and silver their only same-category collateral sample."""
    items = {i["name"]: i for i in load_subset_items()}
    conditions = {c["name"]: c for c in plan_conditions(LATE_THIRDS[28])}
    february = conditions[condition_name("February")]
    assert applies_to(february, items["october-1"])
    assert not applies_to(february, items["france-1"])
    assert applies_to(conditions[condition_name("Brazil")], items["france-1"])


def test_the_m1_shared_cells_are_graded_before_anything_new():
    """D16(a): the 108 cells M1 already recorded lead, so "before any
    off-diagonal cell is read" is literally true. Per item they are exactly
    three — clean, the item's own direction (M1's `primed_late`) and its frozen
    control's (M1's `control_late`)."""
    conditions = plan_conditions(LATE_THIRDS[28])
    total_shared = 0
    for item in load_subset_items():
        shared, rest = conditions_for(conditions, item)
        names = [c["name"] for c in shared]
        assert names == sorted(names, key=lambda n: [c["name"] for c in conditions].index(n))
        assert set(names) == {
            "clean", condition_name(item["concept"]), condition_name(item["control"])
        }
        assert len(shared) == 3
        assert not any(is_shared["name"] in names for is_shared in rest)
        total_shared += len(shared)
    assert total_shared == 108


def test_every_matrix_cell_ablates_the_identical_late_third_at_full_dose():
    """PR #7 review F2's caveat, retired structurally: the two arms the gate
    compares differ ONLY in which direction is removed — not in depth, not in
    layer count, not in dose. M2 could not say this (its tiers were 4 vs 6
    layers wide); M3 can, and its wording does."""
    for n_layers, late in LATE_THIRDS.items():
        ablating = [c for c in plan_conditions(late) if c["direction"] is not None]
        assert {tuple(c["layers"]) for c in ablating} == {tuple(late)}, n_layers
        assert {c["lam"] for c in ablating} == {1.0}, n_layers
    assert m3_matrix.MATRIX_LAMBDA == 1.0


# --- the ported operator ------------------------------------------------------

def _edit_at(direction, layer=0):
    vectors = {(layer, "France"): direction}
    return m3_matrix.concept_ablation_edits(vectors, [layer], "France")[layer]


def test_the_full_ablation_edit_zeroes_the_projection_and_keeps_the_shape():
    direction = torch.randn(8)
    h = torch.randn(1, 5, 8)
    out = _edit_at(direction)(h)
    assert out.shape == h.shape
    assert torch.allclose(out[0] @ direction, torch.zeros(5), atol=1e-4)


def test_the_read_back_fires_when_the_operator_lies(monkeypatch, capsys):
    monkeypatch.setattr(m3_matrix, "ablate", lambda hs, directions: hs)
    with pytest.raises(SystemExit) as exc:
        _edit_at(torch.randn(8), layer=3)(torch.randn(1, 5, 8))
    assert exc.value.code == 2
    assert "M3 read-back failed at layer 3" in capsys.readouterr().out


def test_greedy_continuation_reapplies_the_edits_on_every_pass(monkeypatch):
    """The ablation must stay active across the whole decoded span, or the oracle
    reads a partly-unablated continuation."""
    calls = []

    def fake_logits(subject, sequence, edits):
        calls.append((sequence.shape[1], edits))
        logits = torch.zeros(64)
        logits[10 + len(calls)] = 1.0
        return logits

    monkeypatch.setattr(m3_matrix, "output_logits", fake_logits)

    class _Subject:
        class tokenizer:
            @staticmethod
            def decode(ids):
                return "|".join(str(i) for i in ids)

    edits = {3: "sentinel"}
    span = m3_matrix.greedy_continuation(
        _Subject(), torch.tensor([[1, 2, 3]]), edits, first_id=7, n_tokens=3
    )
    assert span == "7|11|12"
    assert [n for n, _ in calls] == [4, 5]
    assert all(e is edits for _, e in calls)


# --- the gate arithmetic ------------------------------------------------------

def _cell(produced, greedy_id=1, mass=0.9):
    return {
        "produced": produced, "greedy_3": "span", "produced_first_token": produced,
        "greedy": "x", "greedy_id": greedy_id, "concept_mass": mass,
        "says_concept_in_3": produced,
    }


def _record(name, concept, control, gate=True, named_under=(), eligible=True,
            category=None, greedy_ids=None):
    """One graded item. `named_under` is the set of ablated directions under
    which the model still names this item's concept; every other ablated cell is
    a miss. `clean` follows `gate`."""
    greedy_ids = greedy_ids or {}
    directions = list(SUBSET) + ([control] if control not in SUBSET else [])
    cells = {"clean": _cell(gate, greedy_ids.get("clean", 1), 0.9 if eligible else 0.0)}
    for word in directions:
        cells[condition_name(word)] = _cell(
            word in named_under, greedy_ids.get(word, 2), 0.9 if eligible else 0.0
        )
    return {
        "name": name, "category": category or _categories()[concept],
        "concept": concept, "control": control, "source": "s4-reuse",
        "direction_key": "bare" if eligible else "leading_space",
        "mass_channel_eligible": eligible, "cells": cells,
        "gate_span": gate, "gate_first_token": gate, "gate_verbatim_p": gate,
    }


def _perfect_switch(concepts, gate=True):
    """Records where every off-diagonal deletion is survived and the diagonal
    mutes — the shape a per-concept switch makes."""
    controls = {i["concept"]: i["control"] for i in load_subset_items()}
    records = []
    for index, concept in enumerate(concepts):
        records.append(_record(
            f"{concept.lower()}-{index}", concept, controls[concept], gate=gate,
            named_under=[w for w in SUBSET if w != concept] + [controls[concept]]
            if controls[concept] not in SUBSET else [w for w in SUBSET if w != concept],
        ))
    return records


def test_the_gate_is_the_clean_span_and_every_matrix_cell_shares_one_gated_set():
    records = _perfect_switch(["France"]) + _perfect_switch(["Japan"], gate=False)
    package = matrix_package(records, _categories(), _Tok())
    assert package["competence"]["items_run"] == 2
    assert package["competence"]["gate_span"] == 1
    arms = package["pooled_arms"]
    assert arms["diagonal"]["n"] == 1
    assert arms["off_diagonal"]["n"] == 11
    assert arms["within_category_off_diagonal"]["n"] == 5
    assert arms["cross_category_off_diagonal"]["n"] == 6


def test_clause_one_is_the_pooled_off_diagonal_minus_the_pooled_diagonal():
    records = _perfect_switch(["France", "Japan", "Brazil", "Canada", "China",
                              "Egypt", "Jupiter", "Mars", "piano", "violin",
                              "October", "silver"]) * 2
    contrast = matrix_package(records, _categories(), _Tok())["specificity_contrast"]
    clause = contrast["clause_1_pooled"]
    assert clause["diagonal"]["hits"] == 0 and clause["diagonal"]["n"] == 24
    assert clause["off_diagonal"]["hits"] == clause["off_diagonal"]["n"] == 264
    assert clause["newcombe_offdiagonal_minus_diagonal_naming"][0] == pytest.approx(1.0)
    assert clause["excludes_zero"] is True
    assert contrast["matrix_specific_shape_holds"] is True
    assert contrast["underpowered"] is False


def test_clause_two_restricts_both_arms_to_items_with_a_subset_sibling():
    """Review F10: with no sibling the conjunction is empty and True by fiat — it
    would have scored silver, the pre-registered non-specific anti-example, as a
    structural survivor. Both arms of clause (2) drop those items instead."""
    records = _perfect_switch(list(SUBSET)) * 2
    package = matrix_package(records, _categories(), _Tok())
    clause = package["specificity_contrast"]["clause_2_within_category"]
    # 20 sibling-carrying items (24 minus October's 2 and silver's 2)
    assert clause["diagonal"]["n"] == 20
    assert clause["off_diagonal"]["n"] == 2 * (6 * 5 + 4 * 1)  # 68 within-category cells
    assert package["pooled_arms"]["diagonal_restricted_to_sibling_items"]["n"] == 20
    # and the collapse check drops them too, for the same structural reason
    collapse = package["specificity_contrast"]["effective_n_check"][
        "clause_2_survives_all_within_category_siblings"
    ]
    assert collapse["off_diagonal"]["n"] == 20


@pytest.mark.parametrize("subject", SUBJECTS)
def test_the_pre_registered_pooled_ns_reproduce_on_the_recorded_gated_sets(subject):
    """The brief's power table is a *realized* number, not a projection: gating
    is the deterministic clean arm and M2 already recorded it on these very
    items. A run that disagrees is an INVALID cross-check, not a power surprise —
    so the table is pinned through the real analysis path."""
    expected = PRE_REGISTERED[subject]
    records = [
        _record(item["name"], item["concept"], item["control"], gate=item["gate_span"])
        for item in _m2(subject)["items"]
    ]
    package = matrix_package(records, _categories(), _Tok())
    arms = package["pooled_arms"]
    assert package["competence"]["gate_span"] == expected["gated"]
    assert arms["diagonal"]["n"] == expected["gated"]
    assert arms["off_diagonal"]["n"] == expected["off"]
    assert arms["within_category_off_diagonal"]["n"] == expected["within"]
    assert arms["cross_category_off_diagonal"]["n"] == expected["cross"]
    assert arms["diagonal_restricted_to_sibling_items"]["n"] == expected["restricted"]
    assert all(n >= MIN_N for n in
               (expected["gated"], expected["off"], expected["within"],
                expected["restricted"], expected["cross"]))


def test_a_failing_clause_two_sinks_the_and():
    """The undiluted test is load-bearing: a matrix whose cross-category cells
    are clean but whose within-category block collapses fails M3's gate even
    though the pooled clause (1) passes."""
    categories = _categories()
    records = []
    for index, concept in enumerate(SUBSET * 3):
        siblings = within_category_siblings(concept, categories)
        controls = {i["concept"]: i["control"] for i in load_subset_items()}
        records.append(_record(
            f"{concept}-{index}", concept, controls[concept],
            named_under=[w for w in SUBSET if w != concept and w not in siblings],
        ))
    contrast = matrix_package(records, categories, _Tok())["specificity_contrast"]
    assert contrast["clause_1_pooled"]["excludes_zero"] is True
    assert contrast["clause_2_within_category"]["excludes_zero"] is False
    assert contrast["matrix_specific_shape_holds"] is False


def test_underpowered_fires_on_either_diagonal_n():
    """MIN_N guards the pooled diagonal AND clause (2)'s restricted diagonal."""
    small = matrix_package(_perfect_switch(["France"]), _categories(), _Tok())
    assert small["specificity_contrast"]["underpowered"] is True
    # 24 gated items, but only 4 of them carry a within-category sibling
    controls = {i["concept"]: i["control"] for i in load_subset_items()}
    records = [
        _record(f"o-{i}", "October", controls["October"],
                named_under=[w for w in SUBSET if w != "October"])
        for i in range(11)
    ] + [
        _record(f"s-{i}", "silver", controls["silver"],
                named_under=[w for w in SUBSET if w != "silver"])
        for i in range(11)
    ] + _perfect_switch(["Jupiter", "Mars", "piano", "violin"])
    package = matrix_package(records, _categories(), _Tok())
    assert package["pooled_arms"]["diagonal"]["n"] == 26 >= MIN_N
    assert package["pooled_arms"]["diagonal_restricted_to_sibling_items"]["n"] == 4
    assert package["specificity_contrast"]["underpowered"] is True


# --- the collateral-floor readout (D17 / brief review F15) --------------------

def _floor_of(survived_per_item, n_items):
    """Records where each gated item survives `survived_per_item` of its 11
    off-diagonal deletions — the shape the floor readout has to read honestly."""
    controls = {i["concept"]: i["control"] for i in load_subset_items()}
    records = []
    for index in range(n_items):
        others = [w for w in SUBSET if w != "France"]
        records.append(_record(
            f"france-{index}", "France", controls["France"],
            named_under=others[:survived_per_item],
        ))
    return matrix_package(records, _categories(), _Tok())["specificity_contrast"][
        "collateral_floor"
    ]


def test_the_floor_readout_is_the_cluster_mean_over_the_honest_item_level_n():
    """F15's re-definition: k = floor(sum of per-item survival fractions),
    n = the gated items. Ten items each surviving 6 of 11 deletions is
    floor(10 * 6/11) = 5 out of 10, not 60 out of 110 and not 0 out of 10."""
    floor = _floor_of(6, 10)
    assert floor["k"] == 5 and floor["n"] == 10
    assert floor["mean_survival_fraction"] == pytest.approx(6 / 11)
    assert floor["sum_of_fractions"] == pytest.approx(60 / 11)
    # the two dishonest denominators it replaced, both reported or refused
    assert floor["pooled_per_cell_permissive"]["n"] == 110  # F11's inflated n
    assert floor["threshold"] == FLOOR_LOWER_BOUND == 0.5


def test_the_pooled_denominator_would_under_fire_where_the_cluster_mean_fires():
    """F11's point, made arithmetically: the 11x-inflated n narrows the interval,
    so the permissive pooled reading clears a floor the honest item-level n does
    not. At a 7/11 = 0.64 per-cell survival on 28 gated items — inside the brief's
    named 0.57-0.68 damage band — the cluster-collapsed readout fires (17/28 →
    [0.424, 0.764]) while the pooled reading does not (196/308 → [0.581, 0.688])."""
    floor = _floor_of(7, 28)
    assert floor["damaged_floor"] is True
    assert floor["k"] == 17 and floor["n"] == 28
    assert floor["wilson_95"][0] == pytest.approx(0.424, abs=0.001)
    assert floor["wilson_95"][0] < FLOOR_LOWER_BOUND
    assert floor["pooled_per_cell_permissive"]["n"] == 308
    assert floor["pooled_per_cell_permissive"]["wilson_lower"] > FLOOR_LOWER_BOUND


def test_the_conjunction_would_over_fire_where_the_cluster_mean_does_not():
    """F15's point: a survives-all-11 conjunction is decided by the unmeasured
    correlation structure rather than by damage. Items that each survive 10 of 11
    deletions read as a healthy floor on the cluster mean and as zero on the
    conjunction."""
    controls = {i["concept"]: i["control"] for i in load_subset_items()}
    others = [w for w in SUBSET if w != "France"]
    records = [
        _record(f"france-{i}", "France", controls["France"], named_under=others[:10])
        for i in range(28)
    ]
    contrast = matrix_package(records, _categories(), _Tok())["specificity_contrast"]
    assert contrast["collateral_floor"]["damaged_floor"] is False
    conjunction = contrast["effective_n_check"]["clause_1_survives_all_11"]
    assert conjunction["off_diagonal"]["hits"] == 0  # nobody survives all 11
    assert contrast["collateral_floor"]["k"] == 25


def test_a_clean_floor_carries_no_qualifier():
    floor = _floor_of(11, 28)
    assert floor["k"] == 28 and floor["damaged_floor"] is False


# --- the effective-n sanity check (never dispositive) -------------------------

def test_the_effective_n_check_collapses_only_the_repeated_arm():
    records = _perfect_switch(list(SUBSET)) * 2
    effective = matrix_package(records, _categories(), _Tok())["specificity_contrast"][
        "effective_n_check"
    ]
    clause_1 = effective["clause_1_survives_all_11"]
    assert clause_1["off_diagonal"]["n"] == clause_1["diagonal"]["n"] == 24
    assert clause_1["off_diagonal"]["hits"] == 24  # every item survives all 11
    assert "never dispositive" in effective["note"].lower() or "NEVER" in effective["note"]


def test_the_effective_n_check_can_disagree_with_the_pooled_clause():
    """The whole point of pre-registering it: the inflated-n pooled interval is
    narrower than the clustering justifies, so a pooled clause can be CI-clean
    where its per-item collapse is not. When they disagree, the per-item numbers
    are the honest ones to quote."""
    controls = {i["concept"]: i["control"] for i in load_subset_items()}
    others = [w for w in SUBSET if w != "France"]
    records = [
        _record(f"france-{i}", "France", controls["France"], named_under=others[:6])
        for i in range(28)
    ]
    contrast = matrix_package(records, _categories(), _Tok())["specificity_contrast"]
    assert contrast["clause_1_pooled"]["excludes_zero"] is True
    collapse = contrast["effective_n_check"]["clause_1_survives_all_11"]
    assert collapse["off_diagonal"]["hits"] == 0
    assert collapse["excludes_zero"] is False


# --- the descriptive package --------------------------------------------------

def test_the_matrix_is_144_ordered_cells_with_the_diagonal_flagged():
    records = _perfect_switch(list(SUBSET))
    package = matrix_package(records, _categories(), _Tok())
    assert len(package["matrix"]) == 144
    diagonal = [e for e in package["matrix"] if e["is_diagonal"]]
    assert len(diagonal) == 12 and all(e["cell"]["hits"] == 0 for e in diagonal)
    same_category = [e for e in package["matrix"]
                     if e["same_category"] and not e["is_diagonal"]]
    assert len(same_category) == 34
    assert len(package["asymmetry"]) == 66  # every unordered pair, once


def test_the_row_and_column_profiles_split_within_from_cross_category():
    records = _perfect_switch(list(SUBSET))
    package = matrix_package(records, _categories(), _Tok())
    silver = package["row_profiles"]["silver"]
    assert silver["stratum"] == "S4_non_specific_anti_example"
    assert silver["collateral_within_category"]["n"] == 0  # no sibling to damage
    assert silver["collateral_all"]["n"] == 11
    france = package["column_profiles"]["France"]
    assert france["fragility_all"]["n"] == 11
    assert france["fragility_within_category"]["n"] == 5


def test_the_recorded_control_cells_carry_the_in_matrix_split():
    """The M1-comparable single-control view, and the brief's measured claim that
    six of the twelve concepts' recorded control directions are not even among
    their 11 matrix deletions."""
    package = matrix_package(_perfect_switch(list(SUBSET)), _categories(), _Tok())
    controls = package["recorded_control_cells"]
    assert len(controls) == 12
    in_matrix = [c for c, v in controls.items() if v["in_matrix"]]
    out_of_matrix = [c for c, v in controls.items() if not v["in_matrix"]]
    assert sorted(in_matrix) == sorted(
        ["Brazil", "Canada", "China", "Egypt", "France", "Japan"]
    )
    assert sorted(out_of_matrix) == sorted(
        ["October", "Mars", "Jupiter", "piano", "violin", "silver"]
    )


@pytest.mark.parametrize("subject", SUBJECTS)
def test_the_recorded_control_split_reproduces_the_briefs_measured_numbers(subject):
    """The brief's F16 correction, pinned: the recorded control cells are
    indicative proxies, neither ceiling nor floor, because for six of the twelve
    concepts the recorded direction is not among the item's 11 matrix deletions.
    The measured in/out-of-matrix survival split is what replaced the false
    ceiling claim."""
    expected = {
        "qwen2.5-0.5b-instruct": ((15, 18), (5, 10)),
        "qwen2.5-1.5b-instruct": ((18, 18), (12, 16)),
        "qwen2.5-3b-instruct": ((18, 18), (12, 14)),
    }[subject]
    inside = outside = inside_n = outside_n = 0
    for item in _m2(subject)["items"]:
        if not item["gate_span"]:
            continue
        produced = item["cells"]["control_late"]["produced"]
        if item["control"] in SUBSET:
            inside_n, inside = inside_n + 1, inside + produced
        else:
            outside_n, outside = outside_n + 1, outside + produced
    assert ((inside, inside_n), (outside, outside_n)) == expected


# --- the re-scoped degeneracy guard -------------------------------------------

def _cells(pairs):
    return [{"produced": produced, "greedy_id": token} for produced, token in pairs]


def test_the_dispositive_guard_pools_wrong_openings_only():
    """The wide-oracle adaptation, carried from D14: an arm that answers
    *correctly* while sharing a first token is not degenerate."""
    assert wrong_opening_degeneracy(_cells([(True, 1)] * 10), _Tok())["collapsed"] is False
    guard = wrong_opening_degeneracy(_cells([(False, 7)] * 6 + [(True, 2)] * 4), _Tok())
    assert guard["collapsed"] is True and guard["share"] == pytest.approx(0.6)
    assert guard["attractor_token"] == "tok7"


def test_the_share_is_taken_against_the_full_cell_count():
    """'At least half this arm's answers are the same *wrong* opening' — not
    'half the misses agree', which every small miss set would satisfy."""
    guard = wrong_opening_degeneracy(_cells([(False, 7)] * 3 + [(True, 2)] * 17), _Tok())
    assert guard["share"] == pytest.approx(0.15) and guard["collapsed"] is False
    assert guard["non_produced"] == 3 and guard["n_cells"] == 20


def test_an_arm_with_no_misses_is_not_degenerate():
    assert wrong_opening_degeneracy(_cells([(True, 1)] * 3), _Tok()) == {
        "attractor_token": None, "share": 0.0, "collapsed": False,
        "non_produced": 0, "n_cells": 3,
    }


# --- the pre-committed verdict precedence -------------------------------------

def test_verdict_precedence_is_frozen():
    assert matrix_verdict(True, [], False, True) == "MATRIX-SPECIFIC"
    assert matrix_verdict(True, [], False, False) == "not shown"
    assert matrix_verdict(True, [], True, True).startswith("UNDERPOWERED")
    assert matrix_verdict(True, ["off_diagonal"], False, True).startswith("DEGENERATE")
    assert matrix_verdict(False, [], False, True).startswith("NOT A RESULT")
    assert matrix_verdict(True, [], False, True, limit=5) == (
        "NOT A RESULT — smoke run (--limit 5)"
    )
    assert matrix_verdict(False, ["off_diagonal"], True, False, limit=1).startswith(
        "NOT A RESULT — smoke run"
    )


def test_the_damaged_floor_qualifier_scopes_a_claim_and_never_creates_one():
    """It attaches to a contrast-level verdict — it scopes a claim, so it has
    nothing to scope when precedence already withheld the claim, and it can
    never flip 'not shown' into a result."""
    assert matrix_verdict(True, [], False, True, True) == (
        "MATRIX-SPECIFIC — ON A DAMAGED FLOOR"
    )
    assert matrix_verdict(True, [], False, False, True) == "not shown — ON A DAMAGED FLOOR"
    assert matrix_verdict(True, [], True, True, True) == "UNDERPOWERED — no specificity claim"
    assert matrix_verdict(False, [], False, True, True).startswith("NOT A RESULT")


# --- the frozen wording -------------------------------------------------------

def test_the_gate_wording_is_frozen_as_code_and_names_its_own_departures():
    for key in ("oracle", "competence", "specificity", "descriptive", "run_time_bars",
                "degeneracy", "m1_crosscheck", "precedence", "honesty"):
        assert key in m3_matrix.GATE_WORDING and len(m3_matrix.GATE_WORDING[key]) > 100
    gate = m3_matrix.GATE_WORDING["specificity"]
    assert "MATRIX-SPECIFIC iff BOTH" in gate
    assert "MIN_N = 20" in gate
    assert "ON A DAMAGED FLOOR" in gate
    assert "n = 96 / 100 / 101" in gate and "n = 24 / 28 / 29" in gate
    # PR #7 F2's caveat, retired structurally and stated affirmatively
    assert "ONLY IN WHICH DIRECTION IS REMOVED" in gate
    assert "if a later stage re-introduces tiers" in gate
    # the guard's scoping, re-frozen from D14 onto M3's arms
    assert "pooled OFF-DIAGONAL arm" in m3_matrix.GATE_WORDING["degeneracy"]
    assert "`clean` stays off the dispositive list" in m3_matrix.GATE_WORDING["degeneracy"]
    # D18's two bars name the premises they pin
    bars = m3_matrix.GATE_WORDING["run_time_bars"]
    assert "opal" in bars and "`oracle.py` is UNTOUCHED" in bars


@pytest.mark.parametrize("subject", SUBJECTS)
def test_every_published_artifact_carries_the_wording_it_was_produced_under(subject):
    """The guardrail is 'pre-commit gates as code — wording included ... written
    verbatim into the results JSON so prose and code can never drift'. Pinned in
    both directions, so a future wording edit fails the suite instead of
    orphaning the artifacts it governs (M2 round-1 review F1's lesson)."""
    run = json.load(open(f"results/m3-matrix-{subject}.json"))
    assert run["protocol"]["gate_wording"] == m3_matrix.GATE_WORDING
    assert run["protocol"]["floor_lower_bound"] == FLOOR_LOWER_BOUND
    assert run["protocol"]["run_time_bars"]["worst_form_length"] <= oracle.SPAN_TOKENS


@pytest.mark.parametrize("subject", SUBJECTS)
def test_the_published_runs_re_certified_the_instrument_and_ran_the_frozen_plan(subject):
    """D16(a)'s two bars, on the artifacts themselves: the 108-cell
    re-certification passed on every subject, and every one of the 486
    pre-registered cells was actually graded."""
    run = json.load(open(f"results/m3-matrix-{subject}.json"))
    crosscheck = run["m1_crosscheck"]
    assert crosscheck["n_mismatches"] == 0
    assert crosscheck["cells_checked"] == crosscheck["cells_expected"] == 108
    assert crosscheck["items_checked"] == crosscheck["items_expected"] == 36
    assert crosscheck["mass_cells_equal"] == 108  # texture, but it came in exact
    assert run["protocol"]["cells_planned"] == 486
    assert sum(len(item["cells"]) for item in run["items"]) == 486
    assert run["environment"]["certified"] is True and run["smoke_limit"] is None
    assert run["lambda"] == 1.0
    assert run["ablated_layers"] == LATE_THIRDS[SUBJECT_LAYERS[subject]]


def test_the_earlier_milestones_wordings_stay_byte_frozen_with_their_artifacts():
    """Editing `m1_battery.GATE_WORDING` or `m2_depth.GATE_WORDING` would force a
    full re-run of that milestone, so M3 freezes its own instead. This pins that
    neither was quietly amended, and that M3 did not import either."""
    for module, path in (
        (m1_battery, "results/m1-battery-qwen2.5-1.5b-instruct.json"),
        (m2_depth, "results/m2-depth-qwen2.5-1.5b-instruct.json"),
    ):
        assert json.load(open(path))["protocol"]["gate_wording"] == module.GATE_WORDING
    assert m3_matrix.GATE_WORDING["degeneracy"] != m2_depth.GATE_WORDING["degeneracy"]
    assert m3_matrix.GATE_WORDING["oracle"] == oracle.ORACLE_WORDING  # the one shared rule


# --- validate(): every wrong-arm guard proved by its printed reason ------------

class _FakeSpec:
    d_model = 896
    n_layers = 24


class _Args:
    def __init__(self, **kw):
        self.model_id = "Qwen/Qwen2.5-0.5B-Instruct"
        self.m1 = None
        self.__dict__.update(kw)


def _good_artifact():
    return {"model_id": "Qwen/Qwen2.5-0.5B-Instruct", "d_model": 896,
            "J": {l: None for l in range(23)}}


def _bar_clearing_tok():
    table = {}
    for word in PLANNED_DIRECTIONS:
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
        m3_matrix.validate(_Args(), artifact, _FakeSpec(), _bar_clearing_tok())
    assert exc.value.code == 2
    assert expected in capsys.readouterr().out


def test_validate_accepts_the_real_configuration():
    band, recorded, bars = m3_matrix.validate(
        _Args(), _good_artifact(), _FakeSpec(), _bar_clearing_tok()
    )
    assert band == list(range(9, 22))
    assert recorded["milestone"] == "M1"  # returned, so main() never re-parses it
    assert bars["worst_form_length"] == 1


def test_validate_runs_the_d18_bars_before_it_reaches_the_m1_artifact(capsys):
    """The bars are pre-trial by construction: a roster the tokenizer cannot
    score is refused before anything else is even read."""
    tok = _TableTok({w: 4 for w in PLANNED_DIRECTIONS}, default=4)
    with pytest.raises(SystemExit) as exc:
        m3_matrix.validate(_Args(), _good_artifact(), _FakeSpec(), tok)
    assert exc.value.code == 2
    assert "D18 span bar" in capsys.readouterr().out


def _m1_file(tmp_path, **overrides):
    run = {
        "milestone": "M1", "model_id": "Qwen/Qwen2.5-0.5B-Instruct",
        "band": list(range(9, 22)), "smoke_limit": None,
        "environment": {"certified": True, "uncertified_reasons": []},
        "items": [],
    }
    run.update(overrides)
    path = tmp_path / "m1.json"
    path.write_text(json.dumps(run))
    return str(path)


@pytest.mark.parametrize(
    "overrides, expected",
    [
        ({"milestone": "M0"}, "not an M1 battery run"),
        ({"model_id": "Qwen/Qwen2.5-3B-Instruct"}, "are for"),
        ({"band": [1, 2, 3]}, "were run on band"),
        ({"smoke_limit": 5}, "SMOKE run"),
        ({"environment": {"certified": False, "uncertified_reasons": ["device 'cpu'"]}},
         "NOT A RESULT"),
    ],
)
def test_a_cross_check_target_that_is_not_a_result_is_refused(
    overrides, expected, tmp_path, capsys
):
    args = _Args(m1=_m1_file(tmp_path, **overrides))
    with pytest.raises(SystemExit) as exc:
        m3_matrix.validate(args, _good_artifact(), _FakeSpec(), _bar_clearing_tok())
    assert exc.value.code == 2
    assert expected in capsys.readouterr().out


def test_validate_rejects_a_missing_m1_recording(tmp_path, capsys):
    with pytest.raises(SystemExit) as exc:
        m3_matrix.validate(
            _Args(m1=str(tmp_path / "absent.json")), _good_artifact(), _FakeSpec(),
            _bar_clearing_tok(),
        )
    assert exc.value.code == 2
    assert "M1 results" in capsys.readouterr().out


@pytest.mark.parametrize("limit", [0, -1])
def test_a_non_positive_limit_is_wrong_arm_input(limit, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", [
        "m3_matrix.py", "--model-id", "Qwen/Qwen2.5-0.5B-Instruct",
        "--lens", "lenses/qwen2.5-0.5b-instruct-n100.pt", "--limit", str(limit),
    ])
    with pytest.raises(SystemExit) as exc:
        m3_matrix.main()
    assert exc.value.code == 2
    assert "--limit must be a positive item count" in capsys.readouterr().out


def test_a_dry_run_never_loads_the_checkpoint(monkeypatch, capsys):
    """PR #7 review F6's disposition, pinned: `m2_depth.main()` loaded the model
    before validating, so every `--dry-run` and every wrong-arm exit paid a full
    checkpoint load. The M3 cut validates first, so this test passes only
    because no model was touched.

    The lens artifact is supplied synthetically rather than by repo path: the
    `lenses/*.pt` weights are gitignored by decision K3, so a repo path makes
    this case pass locally and fail on any clean checkout — which it did in CI
    the moment PR #13 made the workflow really invoke pytest (that PR's review,
    F5). The guarantee under test is unchanged: `from_pretrained` still raises
    if it is called.
    """
    def refuse(*args, **kwargs):
        raise AssertionError("the checkpoint must not load on a --dry-run")

    monkeypatch.setattr(
        m3_matrix.transformers.AutoModelForCausalLM, "from_pretrained", refuse
    )
    monkeypatch.setattr(
        m3_matrix.torch, "load", lambda *a, **k: {**_good_artifact(), "n_prompts": 100}
    )
    monkeypatch.setattr(sys, "argv", [
        "m3_matrix.py", "--model-id", "Qwen/Qwen2.5-0.5B-Instruct",
        "--lens", "lenses/qwen2.5-0.5b-instruct-n100.pt", "--dry-run",
    ])
    with pytest.raises(SystemExit) as exc:
        m3_matrix.main()
    assert exc.value.code == 0
    printed = capsys.readouterr().out
    assert "no checkpoint loaded" in printed
    assert "cells 486" in printed


# --- the 108-cell M1 cross-check ----------------------------------------------

def _pair(name="france-1", concept="France", control="Canada",
          ours=("France", "France<|im_end|>"), theirs=None, mass=(0.5, 0.5)):
    """(our record, M1's recording) for one item — ours keyed by ablated
    direction, M1's by condition name."""
    theirs = theirs or ours
    return (
        {"name": name, "concept": concept, "control": control, "cells": {
            key: {"greedy": ours[0], "greedy_3": ours[1], "concept_mass": mass[0]}
            for key in ("clean", condition_name(concept), condition_name(control))}},
        {"name": name, "cells": {
            c: {"greedy": theirs[0], "greedy_3": theirs[1], "concept_mass": mass[1]}
            for c in m3_matrix.M1_SHARED_CONDITIONS}},
    )


def test_the_cross_check_maps_direction_cells_onto_m1s_condition_names():
    ours, theirs = _pair()
    problems, texture = m3_matrix.m1_crosscheck([ours], {"items": [theirs]})
    assert problems == []
    assert texture["items_checked"] == 1
    assert texture["cells_checked"] == 3 and texture["mass_cells_equal"] == 3
    assert texture["cells_expected"] == 108  # the standing re-certification surface


def test_the_cross_check_catches_a_drifted_string_on_either_recorded_field():
    ours, theirs = _pair(ours=("France", "France!"), theirs=("France", "France?"))
    problems, _ = m3_matrix.m1_crosscheck([ours], {"items": [theirs]})
    assert len(problems) == 3 and all("greedy_3" in p for p in problems)
    assert any("M1 primed_late" in p for p in problems)  # the mapping is named

    ours, theirs = _pair(ours=("A", "x"), theirs=("B", "x"))
    problems, _ = m3_matrix.m1_crosscheck([ours], {"items": [theirs]})
    assert len(problems) == 3 and all(".greedy:" in p for p in problems)


def test_the_cross_check_treats_mass_as_texture_and_flags_an_absent_item():
    ours, theirs = _pair(mass=(0.5, 0.6))
    problems, texture = m3_matrix.m1_crosscheck([ours], {"items": [theirs]})
    assert problems == [] and texture["mass_cells_equal"] == 0

    problems, texture = m3_matrix.m1_crosscheck([ours], {"items": []})
    assert len(problems) == 1 and "absent from the M1 recording" in problems[0]
    assert texture["items_checked"] == 0


def test_the_cross_check_is_oracle_independent():
    """It compares the raw recorded strings, so D9 cannot soften it: two cells
    that the oracle scores identically still mismatch if their spans differ."""
    ours, theirs = _pair(ours=("France", "France."), theirs=("France", "France!"))
    assert oracle.says_concept_prefix("France.", "France") is True
    assert oracle.says_concept_prefix("France!", "France") is True
    problems, _ = m3_matrix.m1_crosscheck([ours], {"items": [theirs]})
    assert problems


# --- the cross-subject verdict ------------------------------------------------

def _clause(hits=264, n=264, diagonal=0, diagonal_n=24, clean=True):
    return {
        "diagonal": {"hits": diagonal, "n": diagonal_n, "rate": 0.0,
                     "wilson_95": [0.0, 0.1], "underpowered": False},
        "off_diagonal": {"hits": hits, "n": n, "rate": 1.0,
                         "wilson_95": [0.9, 1.0], "underpowered": False},
        "newcombe_offdiagonal_minus_diagonal_naming": [0.95, 0.8, 0.99],
        "excludes_zero": clean,
        "label": "test",
    }


def _run(verdict="MATRIX-SPECIFIC", damaged=False, **kw):
    arm = lambda hits, n: {"hits": hits, "n": n, "rate": hits / n,
                           "wilson_95": [0.5, 0.9], "underpowered": False}
    run = {
        "milestone": "M3", "smoke_limit": None,
        "environment": {"certified": True, "uncertified_reasons": []},
        "m1_crosscheck": {"n_mismatches": 0, "items_checked": 36, "items_expected": 36},
        "competence": {"gate_span": 34, "items_run": 36},
        "protocol": {"subset": list(SUBSET)},
        "pooled_arms": {
            "diagonal": arm(0, 34), "off_diagonal": arm(330, 374),
            "within_category_off_diagonal": arm(88, 100),
            "cross_category_off_diagonal": arm(242, 274),
            "diagonal_restricted_to_sibling_items": arm(0, 28),
        },
        "specificity_contrast": {
            "verdict": verdict,
            "clause_1_pooled": _clause(),
            "clause_2_within_category": _clause(hits=88, n=100, diagonal_n=28),
            "collateral_floor": {
                "k": 20, "n": 34, "wilson_95": [0.3 if damaged else 0.7, 0.9],
                "threshold": 0.5, "damaged_floor": damaged,
            },
            "effective_n_check": {
                "clause_1_survives_all_11": _clause(hits=30, n=34, diagonal_n=34),
                "clause_2_survives_all_within_category_siblings":
                    _clause(hits=26, n=28, diagonal_n=28),
            },
            "row_texture_caveats": [],
        },
        "row_profiles": {
            c: {"collateral_all": arm(28, 31)} for c in SUBSET
        },
        "matrix": [
            {"prime": a, "probe": b, "cell": arm(3, 3), "is_diagonal": a == b,
             "same_category": False}
            for a in SUBSET for b in SUBSET
        ],
    }
    run.update(kw)
    return run


def _run_verdict(monkeypatch, tmp_path, runs):
    for subject, run in runs.items():
        (tmp_path / f"m3-matrix-{subject}.json").write_text(json.dumps(run))
    monkeypatch.setattr(sys, "argv", ["m3_verdict.py", "--results-dir", str(tmp_path)])
    with pytest.raises(SystemExit) as exc:
        m3_verdict.main()
    return exc.value.code


def _all(**per_subject):
    return {s: per_subject.get(s, _run()) for s in m3_verdict.SUBJECTS}


def test_the_m3_verdict_is_the_and_over_the_two_gate_bearing_subjects(
    monkeypatch, tmp_path, capsys
):
    assert _run_verdict(monkeypatch, tmp_path, _all()) == 0
    assert "M3 VERDICT: MATRIX-SPECIFIC at 1.5B AND 3B" in capsys.readouterr().out


def test_a_single_gate_bearing_null_sinks_the_and(monkeypatch, tmp_path, capsys):
    runs = _all(**{"qwen2.5-3b-instruct": _run(verdict="not shown")})
    _run_verdict(monkeypatch, tmp_path, runs)
    out = capsys.readouterr().out
    assert "M3 VERDICT: NOT SHOWN" in out and "qwen2.5-3b-instruct: not shown" in out


def test_the_0_5b_subject_never_enters_the_and(monkeypatch, tmp_path, capsys):
    runs = _all(**{"qwen2.5-0.5b-instruct": _run(verdict="not shown")})
    _run_verdict(monkeypatch, tmp_path, runs)
    out = capsys.readouterr().out
    assert "M3 VERDICT: MATRIX-SPECIFIC at 1.5B AND 3B" in out
    assert "never gate-bearing" in out


def test_the_cross_subject_verdict_carries_a_gate_bearing_damaged_floor(
    monkeypatch, tmp_path, capsys
):
    """The qualifier scopes the headline too: if either gate-bearing subject's
    floor is damaged, the M3 verdict says so."""
    runs = _all(**{"qwen2.5-1.5b-instruct": _run(
        verdict="MATRIX-SPECIFIC — ON A DAMAGED FLOOR", damaged=True
    )})
    _run_verdict(monkeypatch, tmp_path, runs)
    out = capsys.readouterr().out
    assert "M3 VERDICT: MATRIX-SPECIFIC at 1.5B AND 3B" in out
    assert "ON A DAMAGED FLOOR (qwen2.5-1.5b-instruct)" in out
    # a 0.5B-only damaged floor never reaches the headline
    runs = _all(**{"qwen2.5-0.5b-instruct": _run(damaged=True)})
    _run_verdict(monkeypatch, tmp_path, runs)
    headline = capsys.readouterr().out.rsplit("M3 VERDICT:", 1)[-1]
    assert "ON A DAMAGED FLOOR" not in headline


@pytest.mark.parametrize(
    "broken, expected",
    [
        ({"smoke_limit": 3}, "SMOKE run"),
        ({"environment": {"certified": False, "uncertified_reasons": ["device 'cpu'"]}},
         "NOT A RESULT"),
        ({"milestone": "M2"}, "not an M3 matrix run"),
        ({"m1_crosscheck": {"n_mismatches": 4}}, "cross-check mismatches"),
        ({"m1_crosscheck": {"n_mismatches": 0, "items_checked": 35, "items_expected": 36}},
         "cross-checked 35 of 36 subset items"),
        ({"m1_crosscheck": {"n_mismatches": 0, "items_checked": 36}},
         "cross-checked 36 of None subset items"),
    ],
)
def test_a_run_that_is_not_a_result_cannot_feed_the_verdict(
    broken, expected, monkeypatch, tmp_path, capsys
):
    runs = _all(**{"qwen2.5-1.5b-instruct": _run(**broken)})
    assert _run_verdict(monkeypatch, tmp_path, runs) == 2
    assert expected in capsys.readouterr().out


def test_the_verdict_is_invalid_when_a_subject_is_missing(monkeypatch, tmp_path, capsys):
    runs = {s: _run() for s in m3_verdict.SUBJECTS if s != "qwen2.5-3b-instruct"}
    assert _run_verdict(monkeypatch, tmp_path, runs) == 2
    assert "missing" in capsys.readouterr().out

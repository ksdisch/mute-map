"""test_m2.py — invariants for the D9(b) oracle, the M1 reanalysis, and the M2
localization + dose runner.

The heavyweight proof that M2's instrument is still the certified instrument is
the M1 cross-check the runner performs on the subset's 36 items at run time.
These tests pin what a model run cannot: the frozen oracle's decision rule
(including the two readings the brief's pre-registered ns depend on), the window
grid's arithmetic on all three subjects, the new partial-λ operator and its
generalized read-back, the pre-committed degeneracy disposition and verdict
precedence, and the INVALID paths — each asserted on the *printed reason*, not
merely the exit code (the M1 F9 pattern), so a test cannot pass because some
other guard fired.

Several tests read the *committed* M1 artifacts. That is deliberate: the M2
brief pre-registers numbers computed from them (the subset's gated ns, the six
cells that decide the span-end reading, the clean-arm collapse ceiling), and a
pre-registration that no test pins is one a later edit can silently break.
"""
import json
import sys

import pytest
import torch

import m1_battery
import m1_rescore
import m2_depth
import m2_verdict
import oracle
from intervention import ablate
from m2_depth import (
    DOSE_GRID,
    EXPECTED_SUBSET_ITEMS,
    M1_SHARED_CONDITIONS,
    SUBSET,
    SUBSET_STRATA,
    TIERS,
    load_subset_items,
    localization_verdict,
    plan_conditions,
    to_run,
    window_grid,
    wrong_opening_degeneracy,
)
from oracle import says_concept_anywhere, says_concept_prefix

SUBJECTS = ("qwen2.5-0.5b-instruct", "qwen2.5-1.5b-instruct", "qwen2.5-3b-instruct")


def _m1(subject):
    return json.load(open(f"results/m1-battery-{subject}.json"))


# --- the D9(b) oracle ---------------------------------------------------------

@pytest.mark.parametrize(
    "span, concept, expected",
    [
        ("France<|im_end|>\n", "France", True),      # the ordinary hit
        (" France.", "France", True),                # leading whitespace stripped
        ("france", "France", True),                  # case-insensitive (D9b, measured)
        ("Piano<|im_end|>", "piano", True),          # "Piano" is the word piano
        ("The France", "France", False),             # S4's caveat, unchanged in kind
        ("not France", "France", False),             # prefix, never containment
        ("Marseille", "Mars", False),                # the word-boundary check
        ("Mars2", "Mars", False),                    # digits continue a word too
        ("Mars, the red", "Mars", True),             # punctuation closes one
        ("Jupiter's moons", "Jupiter", True),        # an apostrophe closes one
    ],
)
def test_the_frozen_prefix_rule_decides_each_named_case(span, concept, expected):
    assert says_concept_prefix(span, concept) is expected


def test_the_end_of_the_span_counts_as_a_word_boundary():
    """Review F5, pinned as a named case: a word that exactly fills the recorded
    3-token span is a HIT. Truncation must never turn a completed word into a
    miss — and this is the reading every pre-registered n in the M2 brief was
    computed under, so flipping it silently invalidates the whole brief."""
    span, concept, expected = oracle.SPAN_FILL_TEST_CASE
    assert says_concept_prefix(span, concept) is expected is True


def test_the_owned_span_fill_residual_is_pinned_not_merely_documented():
    """Review F12, stated where the oracle actually operates — on the truncated
    span. "Beetlejuice" tokenizes as ['Be','et','le','ju','ice'], so its
    recorded 3-token span decodes to exactly 'Beetle': byte-identical to the
    completed word, and therefore scored as a hit for beetle. The rule cannot
    see the difference and is not asked to. This is accepted behaviour — no such
    cell occurs in the recorded data (pinned by the test below) and none of the
    three span-filling concepts is in M2's subset — and it is pinned here so it
    stays a known cost rather than a surprise."""
    assert says_concept_prefix("Beetle", "beetle") is True   # the completed word
    assert says_concept_prefix("Beetlejuice", "beetle") is False  # when visible, it is caught
    assert not {"beetle", "butterfly", "trumpet"} & set(SUBSET)


def test_containment_is_the_rejected_reading_and_is_texture_only():
    assert says_concept_anywhere("not France", "France") is True
    assert says_concept_prefix("not France", "France") is False


def test_no_recorded_cell_exercises_the_span_fill_residual():
    """The residual above is only acceptable while it is unrealised: no recorded
    M1 cell opens with one of the three span-filling concepts and then keeps
    going in the same word."""
    offenders = []
    for subject in SUBJECTS:
        for record in _m1(subject)["items"]:
            for name, cell in record["cells"].items():
                span = cell["greedy_3"].lstrip()
                for concept in ("beetle", "butterfly", "trumpet"):
                    if (span.lower().startswith(concept) and len(span) > len(concept)
                            and span[len(concept)].isalnum()):
                        offenders.append((subject, record["name"], name, span))
    assert offenders == []


def test_exactly_six_recorded_cells_decide_the_span_end_reading():
    """The M2 brief says six recorded cells distinguish the two readings, two of
    them on a control arm. That claim is load-bearing (it is why F5 had to be
    settled before the ns were computed), so it is pinned to the data."""
    import re

    def strict(span, concept):  # the rejected reading: the span must continue
        return re.match(re.escape(concept) + r"(?=[^A-Za-z0-9])",
                        span.lstrip(), re.IGNORECASE) is not None

    disagreements = [
        (subject, record["name"], name)
        for subject in SUBJECTS
        for record in _m1(subject)["items"]
        for name, cell in record["cells"].items()
        if says_concept_prefix(cell["greedy_3"], record["concept"])
        != strict(cell["greedy_3"], record["concept"])
    ]
    assert len(disagreements) == 6
    assert sum(name == "control_late" for _, _, name in disagreements) == 2
    # and every one of them is a completed word filling the span, never a fragment
    assert {n for _, n, _ in disagreements} == {"beetle-1", "butterfly-1", "trumpet-3"}


# --- the pre-registered subset ------------------------------------------------

def test_the_frozen_subset_draws_thirty_six_verbatim_m1_items():
    items = load_subset_items()
    assert len(items) == EXPECTED_SUBSET_ITEMS == 36
    assert {i["concept"] for i in items} == set(SUBSET) and len(SUBSET) == 12
    by_concept = {}
    for item in items:
        by_concept.setdefault(item["concept"], []).append(item)
    assert all(len(group) == 3 for group in by_concept.values())
    # verbatim means verbatim: every subset item is byte-equal to M1's frozen one
    battery = {i["name"]: i for i in json.load(open(m2_depth.ITEMS_PATH))["items"]}
    assert all(item == battery[item["name"]] for item in items)


def test_the_strata_partition_the_subset():
    flat = [c for members in SUBSET_STRATA.values() for c in members]
    assert sorted(flat) == sorted(SUBSET) and len(flat) == len(set(flat))


def test_a_subset_concept_missing_from_the_battery_is_invalid(monkeypatch):
    monkeypatch.setattr(m2_depth, "SUBSET", SUBSET + ("Atlantis",))
    with pytest.raises(ValueError, match="missing pre-registered subset concept"):
        load_subset_items()


def test_the_subsets_gated_ns_are_already_known_from_the_recorded_clean_arm():
    """Expected power in the M2 brief is *realised*, not projected: gating is a
    property of the deterministic clean arm, already recorded by M1. If a run
    disagrees with these ns that is a cross-check failure, not a power surprise
    — so the pre-registered values are pinned here."""
    expected = {"qwen2.5-0.5b-instruct": 28, "qwen2.5-1.5b-instruct": 34,
                "qwen2.5-3b-instruct": 32}
    for subject, n in expected.items():
        rows = [r for r in _m1(subject)["items"] if r["concept"] in SUBSET]
        gated = [r for r in rows
                 if says_concept_prefix(r["cells"]["clean"]["greedy_3"], r["concept"])]
        assert len(gated) == n, subject
        assert n >= m2_depth.MIN_N  # every pooled cell clears MIN_N on every subject


def test_the_clean_arm_cannot_approach_the_collapse_threshold(capsys):
    """D14's F3 correction, evidenced on the population M2 actually grades
    (reviews F7 + F10): `clean` is the gate arm, so its answers are correct
    openings of 12 different spellings and no token can reach COLLAPSE_SHARE."""
    from collections import Counter

    for subject in SUBJECTS:
        rows = [r for r in _m1(subject)["items"] if r["concept"] in SUBSET]
        gated = [r for r in rows
                 if says_concept_prefix(r["cells"]["clean"]["greedy_3"], r["concept"])]
        tokens = [r["cells"]["clean"]["greedy"] for r in gated]
        share = Counter(tokens).most_common(1)[0][1] / len(tokens)
        assert share <= 3 / 28 + 1e-9, subject      # the measured worst case
        assert share < m2_depth.COLLAPSE_SHARE / 4  # five times below, with room


def test_the_S2_stratums_mass_channel_is_floor_pinned_by_construction():
    """D13's review-F2 scoping, measured rather than assumed: the S2 concepts'
    emitted bare spelling has no single-token form, so their `concept_mass` sits
    at the floor even on the clean arm — which is why their dose curve is read
    on the binary rate alone."""
    s2 = set(SUBSET_STRATA["S2_readout_unlocked"])
    rows = [r for r in _m1("qwen2.5-1.5b-instruct")["items"] if r["concept"] in SUBSET]
    gated = [r for r in rows
             if says_concept_prefix(r["cells"]["clean"]["greedy_3"], r["concept"])]
    mass = lambda group: sum(r["cells"]["clean"]["concept_mass"] for r in group) / len(group)
    assert mass([r for r in gated if r["concept"] in s2]) == pytest.approx(0.009, abs=5e-4)
    assert mass([r for r in gated if r["concept"] not in s2]) == pytest.approx(0.913, abs=5e-4)


def test_the_space_keyed_direction_still_mutes_the_bare_emission():
    """The owned D11/F3 convention: for the S2 stratum the ablated direction is
    keyed to the leading-space unembed row (the only single-token form that
    exists) while the oracle scores the bare spelling the model emits. That the
    space-keyed ablation nonetheless mutes the bare emission is measured, not
    assumed."""
    s2 = set(SUBSET_STRATA["S2_readout_unlocked"])
    for subject in ("qwen2.5-1.5b-instruct", "qwen2.5-3b-instruct"):
        rows = [r for r in _m1(subject)["items"] if r["concept"] in s2]
        assert rows and not any(
            says_concept_prefix(r["cells"]["primed_late"]["greedy_3"], r["concept"])
            for r in rows
        ), subject


# --- the window grid (D12b) ---------------------------------------------------

@pytest.mark.parametrize(
    "n_layers, late, width, expected",
    [
        (24, list(range(17, 22)), 5, [0, 1, 3, 5, 7, 9, 11, 13, 15, 17, 18]),
        (28, list(range(19, 25)), 6, [0, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19, 21]),
        (36, list(range(26, 33)), 7, list(range(0, 29, 2))),
    ],
)
def test_the_window_grid_is_late_anchored_with_floor_and_ceiling(
    n_layers, late, width, expected
):
    starts = window_grid(late, n_layers - 2, width)
    assert starts == expected
    assert late[0] in starts                       # the gate cell is on the map (F8)
    assert starts[0] == 0                          # the floor window (F11)
    assert starts[-1] == n_layers - 2 - width + 1  # the ceiling window (F8)
    assert all((s - late[0]) % 2 == 0 for s in starts if s not in (0, starts[-1]))


def test_the_window_grid_positions_match_the_pre_registered_counts():
    """11 / 12 / 15 positions, of which the late-anchored one is reused → 10 / 11
    / 14 newly-run window conditions (the M2 brief's wall-clock arithmetic)."""
    for n_layers, late, width, positions in (
        (24, list(range(17, 22)), 5, 11),
        (28, list(range(19, 25)), 6, 12),
        (36, list(range(26, 33)), 7, 15),
    ):
        starts = window_grid(late, n_layers - 2, width)
        assert len(starts) == positions
        assert len([s for s in starts if s != late[0]]) == positions - 1


def test_an_illegal_anchor_is_wrong_arm_input(capsys):
    with pytest.raises(SystemExit) as exc:
        window_grid([30], lens_max=20, width=5)
    assert exc.value.code == 2
    assert "not a legal window start" in capsys.readouterr().out


# --- the condition plan -------------------------------------------------------

def _plan(n_layers=28, band=None):
    band = band or list(range(11, 25))
    thirds = m2_depth.sub_band_thirds(band)
    return plan_conditions(thirds, n_layers - 2), thirds, band


@pytest.mark.parametrize(
    "n_layers, band, run_count",
    [
        (24, list(range(9, 22)), 20),
        (28, list(range(11, 25)), 21),
        (36, list(range(14, 33)), 24),
    ],
)
def test_the_condition_plan_runs_the_pre_registered_number_of_cells(
    n_layers, band, run_count
):
    """1 clean + 6 tier + 10/11/14 newly-run window + 3 dose = 20 / 21 / 24."""
    conditions, thirds, _ = _plan(n_layers, band)
    runnable = to_run(conditions)
    assert len(runnable) == run_count
    groups = [c["group"] for c in runnable]
    assert groups.count("clean") == 1
    assert groups.count("tier") == 6
    assert groups.count("dose") == 3
    assert groups.count("window") == run_count - 10


def test_the_m1_shared_cells_are_graded_before_anything_new():
    """D14 can only fire 'before any new window or dose cell is read' if M1's
    three conditions lead the plan."""
    conditions, _, _ = _plan()
    assert [c["name"] for c in conditions[:3]] == list(M1_SHARED_CONDITIONS)


def test_the_already_run_cells_are_declared_reuses_not_re_runs():
    conditions, thirds, _ = _plan()
    by_name = {c["name"]: c for c in conditions}
    late = thirds["late"]
    window = by_name[m2_depth.window_name(late[0], len(late))]
    assert window["reused_from"] == "primed_late" and window["layers"] == late
    assert by_name["dose_0"]["reused_from"] == "clean"
    assert by_name["dose_1"]["reused_from"] == "primed_late"
    assert [c["lam"] for c in conditions if c["group"] == "dose"] == list(DOSE_GRID)
    assert all(c["lam"] == 1.0 for c in conditions if c["group"] in ("tier", "window"))


def test_every_tier_gets_both_a_primed_and_a_control_arm():
    conditions, thirds, _ = _plan()
    names = {c["name"] for c in conditions}
    for tier in TIERS:
        assert {f"primed_{tier}", f"control_{tier}"} <= names
    by_name = {c["name"]: c for c in conditions}
    assert by_name["primed_early"]["layers"] == thirds["early"]
    assert by_name["control_middle"]["role"] == "control"
    assert by_name["primed_late"]["role"] == "concept"


# --- the operators ------------------------------------------------------------

def _vectors(layer=3, word="France", d=16, seed=0):
    torch.manual_seed(seed)
    return {(layer, word): torch.randn(d, dtype=torch.float32)}


def test_the_partial_operator_at_full_dose_is_the_ported_ablation_exactly():
    """The dose curve's λ = 1 endpoint must be the *same* measurement M1 made,
    not merely a close one — so the new operator is pinned bit-identical to the
    ported one there."""
    torch.manual_seed(1)
    h = torch.randn(4, 16)
    v = torch.randn(16)
    partial = m2_depth.partial_project_out(h, v, 1.0)
    full = ablate(h, v.expand(h.shape[0], 1, -1))
    assert torch.equal(partial, full)


def test_the_partial_operator_removes_exactly_the_requested_fraction():
    torch.manual_seed(2)
    h, v = torch.randn(4, 16), torch.randn(16)
    unit = v / v.norm()
    before = h @ unit
    for lam in DOSE_GRID:
        after = m2_depth.partial_project_out(h, v, lam) @ unit
        assert torch.allclose(after, (1 - lam) * before, atol=1e-6)
    assert torch.equal(m2_depth.partial_project_out(h, v, 0.0), h)  # λ=0 is a no-op


def test_the_full_ablation_edit_zeroes_the_projection_and_keeps_the_shape():
    """PR #4 review F6: the edit builder gets a direct unit test rather than
    being exercised only through a model run."""
    vectors = _vectors()
    edits = m2_depth.concept_ablation_edits(vectors, [3], "France")
    h = torch.randn(1, 5, 16)
    out = edits[3](h)
    assert out.shape == h.shape
    direction = vectors[(3, "France")]
    assert torch.allclose(out[0] @ direction, torch.zeros(5), atol=1e-5)


def test_the_partial_edit_leaves_the_expected_fraction_of_the_projection():
    vectors = _vectors()
    edits = m2_depth.partial_ablation_edits(vectors, [3], "France", 0.75)
    h = torch.randn(1, 5, 16)
    direction = vectors[(3, "France")]
    before = h[0] @ direction
    after = edits[3](h)[0] @ direction
    assert torch.allclose(after, 0.25 * before, atol=1e-5)


def test_the_generalized_read_back_fires_when_the_operator_lies(monkeypatch, capsys):
    """The read-back is the guard that makes a silent operator bug impossible.
    Sabotage the operator into a no-op and the λ = 0.5 edit must exit INVALID."""
    edits = m2_depth.partial_ablation_edits(_vectors(), [3], "France", 0.5)
    monkeypatch.setattr(m2_depth, "partial_project_out", lambda h, d, lam: h)
    with pytest.raises(SystemExit) as exc:
        edits[3](torch.randn(1, 5, 16))
    assert exc.value.code == 2
    assert "partial read-back failed" in capsys.readouterr().out


def test_the_full_read_back_fires_when_the_ported_operator_lies(monkeypatch, capsys):
    edits = m2_depth.concept_ablation_edits(_vectors(), [3], "France")
    monkeypatch.setattr(m2_depth, "ablate", lambda h, directions: h)
    with pytest.raises(SystemExit) as exc:
        edits[3](torch.randn(1, 5, 16))
    assert exc.value.code == 2
    assert "read-back failed" in capsys.readouterr().out


def test_full_dose_conditions_route_through_the_ported_operator(monkeypatch):
    """λ = 1 cells — every tier and every window — must use M1's exact path, or
    the cross-check would be comparing two different operators."""
    seen = []
    monkeypatch.setattr(m2_depth, "concept_ablation_edits",
                        lambda v, l, w: seen.append(("full", w)) or {})
    monkeypatch.setattr(m2_depth, "partial_ablation_edits",
                        lambda v, l, w, lam: seen.append(("partial", lam)) or {})
    words = {"concept": "France", "control": "Canada"}
    conditions, _, _ = _plan()
    for condition in to_run(conditions):
        m2_depth.edits_for(condition, {}, words)
    assert ("partial", 1.0) not in seen
    assert [s for s in seen if s[0] == "partial"] == [
        ("partial", lam) for lam in m2_depth.NEW_DOSE_LAMBDAS
    ]
    assert m2_depth.edits_for({"role": None}, {}, words) is None


def test_greedy_continuation_reapplies_the_edits_on_every_pass(monkeypatch):
    """PR #4 review F6: the continuation is what the widened oracle reads, so
    the ablation staying active across the whole span is now load-bearing, not
    merely texture."""
    calls = []

    def fake_logits(subject, sequence, edits):
        calls.append((int(sequence.shape[-1]), edits))
        logits = torch.zeros(50)
        logits[10 + len(calls)] = 1.0
        return logits

    monkeypatch.setattr(m2_depth, "output_logits", fake_logits)

    class _Subject:
        class tokenizer:
            @staticmethod
            def decode(ids):
                return "|".join(str(i) for i in ids)

    edits = {3: "sentinel"}
    span = m2_depth.greedy_continuation(
        _Subject(), torch.tensor([[1, 2, 3]]), edits, first_id=7, n_tokens=3
    )
    assert span == "7|11|12"
    assert [n for n, _ in calls] == [4, 5]          # the sequence grows each pass
    assert all(e is edits for _, e in calls)        # and the ablation stays active


# --- the descriptive package --------------------------------------------------

def _cell(produced, greedy="x", mass=0.9, greedy_id=1):
    return {
        "produced": produced, "greedy_3": "span", "produced_first_token": produced,
        "greedy": greedy, "greedy_id": greedy_id, "concept_mass": mass,
        "says_concept_in_3": produced,
    }


def _record(name, concept, produced_names, conditions, mass=0.9, eligible=True,
            gate=True, greedy_by_condition=None):
    greedy_by_condition = greedy_by_condition or {}
    cells = {
        c["name"]: _cell(
            gate if c["name"] == "clean" else c["name"] in produced_names,
            greedy=greedy_by_condition.get(c["name"], f"g-{name}"),
            mass=mass,
            greedy_id=hash(greedy_by_condition.get(c["name"], f"g-{name}")) % 1000,
        )
        for c in to_run(conditions)
    }
    return {
        "name": name, "category": "countries", "concept": concept, "control": "Canada",
        "source": "s4-reuse", "direction_key": "bare" if eligible else "leading_space",
        "mass_channel_eligible": eligible, "cells": cells,
        "gate_span": gate, "gate_first_token": gate, "gate_verbatim_p": gate,
    }


def test_the_gate_is_the_clean_span_and_every_cell_shares_one_gated_set():
    conditions, thirds, band = _plan()
    records = [
        _record("france-1", "France", {"primed_early", "control_late"}, conditions),
        _record("japan-1", "Japan", {"primed_early"}, conditions, gate=False),
    ]
    package = m2_depth.descriptive_package(records, conditions, thirds, band)
    assert package["competence"]["items_run"] == 2
    assert package["competence"]["gate_span"] == 1
    assert all(cell["n"] == 1 for cell in package["tier_cells"].values())
    assert package["tier_cells"]["primed_early"]["hits"] == 1
    assert package["tier_cells"]["primed_late"]["hits"] == 0
    assert all(w["cell"]["n"] == 1 for w in package["window_map"])
    assert all(d["cell"]["n"] == 1 for d in package["dose_curve"])


def test_the_localization_contrast_is_primed_tier_minus_primed_late():
    """D14's arithmetic: the shared clean arm cancels, so 'the late effect
    exceeds the early effect' IS 'primed_early names more often than
    primed_late' — a plain two-proportion comparison."""
    conditions, thirds, band = _plan()
    records = [
        _record(f"c{i}-1", "France", {"primed_early", "primed_middle"}, conditions)
        for i in range(30)
    ]
    contrast = m2_depth.descriptive_package(
        records, conditions, thirds, band
    )["localization_contrast"]
    early = contrast["newcombe_primed_early_minus_primed_late_naming"]
    assert early[0] == pytest.approx(1.0)
    assert contrast["primed_early_exceeds_late"] is True
    assert contrast["primed_middle_exceeds_late"] is True
    assert contrast["late_localized_shape_holds"] is True
    assert contrast["underpowered"] is False  # n = 30 >= MIN_N


def test_one_tier_failing_sinks_the_and_and_a_small_cell_is_underpowered():
    conditions, thirds, band = _plan()
    records = [
        _record(f"c{i}-1", "France", {"primed_early"}, conditions) for i in range(30)
    ] + [
        _record(f"d{i}-1", "France", {"primed_early", "primed_late"}, conditions)
        for i in range(30)
    ]
    contrast = m2_depth.descriptive_package(
        records, conditions, thirds, band
    )["localization_contrast"]
    assert contrast["primed_early_exceeds_late"] is True
    assert contrast["primed_middle_exceeds_late"] is False  # middle 0/60 vs late 30/60
    assert contrast["late_localized_shape_holds"] is False

    small = m2_depth.descriptive_package(
        [_record("france-1", "France", set(), conditions)], conditions, thirds, band
    )
    assert small["localization_contrast"]["underpowered"] is True


def test_the_window_map_reuses_the_gate_cell_and_flags_outside_band_probes():
    conditions, thirds, band = _plan()
    records = [_record("france-1", "France", {"primed_late"}, conditions)]
    window_map = m2_depth.descriptive_package(
        records, conditions, thirds, band
    )["window_map"]
    gate_cells = [w for w in window_map if w["is_gate_cell"]]
    assert len(gate_cells) == 1
    assert gate_cells[0]["layers"] == thirds["late"]
    # the gate cell reads the primed_late cell rather than a re-run of it
    assert gate_cells[0]["cell"]["hits"] == 1
    assert gate_cells[0]["reused_from"] == "primed_late"
    outside = [w for w in window_map if w["outside_band"]]
    assert outside and all(not set(w["layers"]) & set(band) for w in outside)
    assert min(w["start"] for w in window_map) == 0  # the deep outside-band probe


def test_the_dose_curve_reuses_its_endpoints_and_scopes_the_mass_channel():
    conditions, thirds, band = _plan()
    records = [
        _record("france-1", "France", {"primed_late"}, conditions, mass=0.8),
        _record("mars-1", "Mars", set(), conditions, mass=0.001, eligible=False),
    ]
    dose = m2_depth.descriptive_package(records, conditions, thirds, band)["dose_curve"]
    assert [d["lambda"] for d in dose] == list(DOSE_GRID)
    assert dose[0]["reused_from"] == "clean" and dose[-1]["reused_from"] == "primed_late"
    # review F2: the floor-pinned S2 item is excluded from the mass channel, so
    # the mean is the eligible item's own mass rather than an average with a zero
    assert all(d["mass_channel_n"] == 1 for d in dose)
    assert dose[0]["mean_concept_mass_eligible"] == pytest.approx(0.8)


def test_the_per_concept_map_records_each_concepts_stratum_and_keying():
    conditions, thirds, band = _plan()
    records = [
        _record("france-1", "France", set(), conditions),
        _record("mars-1", "Mars", set(), conditions, eligible=False),
    ]
    concept_map = m2_depth.descriptive_package(
        records, conditions, thirds, band
    )["per_concept"]
    assert concept_map["France"]["stratum"] == "S1_hard_switch_core"
    assert concept_map["Mars"]["stratum"] == "S2_readout_unlocked"
    assert concept_map["Mars"]["direction_key"] == "leading_space"
    assert concept_map["Mars"]["mass_channel_eligible"] is False
    assert len(concept_map["France"]["primed_late"]["wilson_95"]) == 2


# --- the re-frozen degeneracy guard (D14) -------------------------------------

def _rows(pairs):
    """(produced, greedy_id) per row, for one condition named 'arm'."""
    return [
        {"cells": {"arm": {"produced": produced, "greedy_id": token}}}
        for produced, token in pairs
    ]


class _Tok:
    @staticmethod
    def decode(ids):
        return f"tok{ids[0]}"


def test_the_dispositive_guard_pools_wrong_openings_only():
    """The wide-oracle adaptation: an arm that answers *correctly* while sharing
    a first token is not degenerate, however concentrated that token is."""
    correct_but_concentrated = _rows([(True, 1)] * 10)
    assert wrong_opening_degeneracy(correct_but_concentrated, "arm", _Tok())["collapsed"] is False

    same_wrong_opening = _rows([(False, 7)] * 6 + [(True, 2)] * 4)
    guard = wrong_opening_degeneracy(same_wrong_opening, "arm", _Tok())
    assert guard["collapsed"] is True and guard["share"] == pytest.approx(0.6)
    assert guard["attractor_token"] == "tok7" and guard["non_produced"] == 6


def test_the_share_is_taken_against_the_full_gated_n_not_the_missed_subset():
    """Otherwise an arm that misses twice, both times identically, would read as
    a 100% collapse."""
    rows = _rows([(False, 7), (False, 7)] + [(True, i) for i in range(20)])
    guard = wrong_opening_degeneracy(rows, "arm", _Tok())
    assert guard["n_gated"] == 22 and guard["share"] == pytest.approx(2 / 22)
    assert guard["collapsed"] is False


def test_an_arm_with_no_misses_is_not_degenerate():
    guard = wrong_opening_degeneracy(_rows([(True, 1)] * 3), "arm", _Tok())
    assert guard == {"attractor_token": None, "share": 0.0, "collapsed": False,
                     "non_produced": 0, "n_gated": 3}


# --- the pre-committed verdict precedence -------------------------------------

def test_verdict_precedence_is_frozen():
    assert localization_verdict(True, [], False, True) == "LATE-LOCALIZED"
    assert localization_verdict(True, [], False, False) == "not shown"
    assert localization_verdict(True, [], True, True).startswith("UNDERPOWERED")
    assert localization_verdict(True, ["primed_early"], False, True).startswith("DEGENERATE")
    assert localization_verdict(False, [], False, True).startswith("NOT A RESULT")
    # a smoke run outranks everything, including a certified holding contrast
    assert localization_verdict(True, [], False, True, limit=5) == (
        "NOT A RESULT — smoke run (--limit 5)"
    )
    assert localization_verdict(False, ["primed_early"], True, False, limit=1).startswith(
        "NOT A RESULT — smoke run"
    )


def test_the_gate_wording_is_frozen_as_code_and_names_its_own_departures():
    for key in ("oracle", "competence", "localization", "window_map", "dose",
                "degeneracy", "m1_crosscheck", "honesty"):
        assert key in m2_depth.GATE_WORDING and len(m2_depth.GATE_WORDING[key]) > 100
    assert "LATE-LOCALIZED" in m2_depth.GATE_WORDING["localization"]
    assert "MIN_N = 20" in m2_depth.GATE_WORDING["localization"]
    # D14's re-freeze: `clean` leaves the dispositive list, and the guard reads
    # the arm's non-produced items
    assert "NON-PRODUCED" in m2_depth.GATE_WORDING["degeneracy"]
    assert "drops `clean` from the dispositive list" in m2_depth.GATE_WORDING["degeneracy"]


def test_every_published_artifact_carries_the_wording_it_was_produced_under():
    """Round 1 review F1. The guardrail is "wording included ... written verbatim
    into the results JSON so prose and code can never drift" — but it was only
    ever *enforced* for M1's artifacts (the test below). The rescore artifacts
    were generated, then `ORACLE_WORDING` was corrected for review F14, and the
    artifacts silently kept publishing the retracted sentence. Nothing detected
    it because nothing was looking. Both directions are now pinned, so a future
    wording edit fails the suite instead of orphaning the artifacts it governs."""
    for subject in SUBJECTS:
        rescore = json.load(open(f"results/m1-rescore-{subject}.json"))
        assert rescore["oracle_wording"] == oracle.ORACLE_WORDING, subject
        depth = json.load(open(f"results/m2-depth-{subject}.json"))
        assert depth["protocol"]["gate_wording"] == m2_depth.GATE_WORDING, subject


def test_the_late_tier_is_wider_than_the_arms_it_is_compared_against():
    """Round 1 review F2, pinned so the confound is a known quantity rather than
    an unstated one. `sub_band_thirds` gives the late tier the band's remainder,
    so the localization gate compares a 4-layer ablation against a 6-layer one at
    1.5B — intervention *size* differs between the arms, not only depth. The
    equal-width sliding window is what retires the objection empirically (it is
    descriptive, never gating); see the brief's Honest limits."""
    widths = {}
    for n_layers, band in ((24, range(9, 22)), (28, range(11, 25)), (36, range(14, 33))):
        thirds = m2_depth.sub_band_thirds(list(band))
        widths[n_layers] = {t: len(thirds[t]) for t in TIERS}
        assert widths[n_layers]["late"] > widths[n_layers]["early"], n_layers
        assert widths[n_layers]["early"] == widths[n_layers]["middle"], n_layers
    assert widths[28] == {"early": 4, "middle": 4, "late": 6}
    # and the equal-width check that retires it: a mid-depth window of the SAME
    # width as the late third leaves naming largely intact at 1.5B
    run = json.load(open("results/m2-depth-qwen2.5-1.5b-instruct.json"))
    by_name = {w["name"]: w for w in run["window_map"]}
    late = next(w for w in run["window_map"] if w["is_gate_cell"])
    mid = by_name["window_L11-L16"]
    assert len(mid["layers"]) == len(late["layers"]) == 6
    assert mid["cell"]["hits"] == 25 and late["cell"]["hits"] == 0


def test_m1s_gate_wording_stays_byte_frozen_with_m1s_artifacts():
    """Editing `m1_battery.GATE_WORDING` would force a full M1 re-run, so M2
    freezes its own instead. This pins that M1's was not quietly amended."""
    assert "Collapse (most-common greedy token's share >= " in (
        m1_battery.GATE_WORDING["degeneracy"]
    )
    assert m1_battery.GATE_WORDING["degeneracy"] != m2_depth.GATE_WORDING["degeneracy"]
    recorded = _m1("qwen2.5-1.5b-instruct")["protocol"]["gate_wording"]
    assert recorded == m1_battery.GATE_WORDING


# --- validate(): every wrong-arm guard proved by its printed reason ------------

class _FakeSubject:
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
        m2_depth.validate(_Args(), artifact, _FakeSubject())
    assert exc.value.code == 2
    assert expected in capsys.readouterr().out


def test_validate_accepts_the_real_configuration():
    assert m2_depth.validate(_Args(), _good_artifact(), _FakeSubject()) == list(range(9, 22))


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
    """M2's cross-check is only a re-certification if the run it compares against
    was itself a result."""
    args = _Args(m1=_m1_file(tmp_path, **overrides))
    with pytest.raises(SystemExit) as exc:
        m2_depth.validate(args, _good_artifact(), _FakeSubject())
    assert exc.value.code == 2
    assert expected in capsys.readouterr().out


def test_validate_rejects_a_missing_m1_recording(tmp_path, capsys):
    with pytest.raises(SystemExit) as exc:
        m2_depth.validate(
            _Args(m1=str(tmp_path / "absent.json")), _good_artifact(), _FakeSubject()
        )
    assert exc.value.code == 2
    assert "M1 results" in capsys.readouterr().out


# --- the M1 cross-check -------------------------------------------------------

def _pair(name="france-1", ours=("France", "France<|im_end|>"), theirs=None, mass=(0.5, 0.5)):
    theirs = theirs or ours
    return (
        {"name": name, "cells": {
            c: {"greedy": ours[0], "greedy_3": ours[1], "concept_mass": mass[0]}
            for c in M1_SHARED_CONDITIONS}},
        {"name": name, "cells": {
            c: {"greedy": theirs[0], "greedy_3": theirs[1], "concept_mass": mass[1]}
            for c in M1_SHARED_CONDITIONS}},
    )


def test_the_cross_check_passes_on_an_exact_reproduction():
    ours, theirs = _pair()
    problems, texture = m2_depth.m1_crosscheck([ours], {"items": [theirs]})
    assert problems == []
    assert texture["items_checked"] == 1
    assert texture["items_expected"] == EXPECTED_SUBSET_ITEMS == 36
    assert texture["cells_checked"] == 3 and texture["mass_cells_equal"] == 3


def test_the_cross_check_catches_a_drifted_string_on_either_recorded_field():
    ours, theirs = _pair(ours=("France", "France!"), theirs=("France", "France?"))
    problems, _ = m2_depth.m1_crosscheck([ours], {"items": [theirs]})
    assert len(problems) == 3 and all("greedy_3" in p for p in problems)

    ours, theirs = _pair(ours=("A", "x"), theirs=("B", "x"))
    problems, _ = m2_depth.m1_crosscheck([ours], {"items": [theirs]})
    assert len(problems) == 3 and all(".greedy:" in p for p in problems)


def test_the_cross_check_treats_mass_as_texture_and_flags_an_absent_item():
    ours, theirs = _pair(mass=(0.5, 0.4999))
    problems, texture = m2_depth.m1_crosscheck([ours], {"items": [theirs]})
    assert problems == [] and texture["mass_cells_equal"] == 0

    ours, _ = _pair(name="ghost-1")
    problems, _ = m2_depth.m1_crosscheck([ours], {"items": []})
    assert len(problems) == 1 and "absent from the M1 recording" in problems[0]


def test_the_cross_check_is_oracle_independent():
    """It compares raw recorded strings, so D9's widening cannot soften it — the
    same cells disagree whichever oracle scores them."""
    assert set(m2_depth.M1_CELL_FIELDS) == {"greedy", "greedy_3"}
    assert "produced" not in m2_depth.M1_CELL_FIELDS


# --- main()'s wrong-arm input -------------------------------------------------

@pytest.mark.parametrize("limit", [0, -1])
def test_a_non_positive_limit_is_wrong_arm_input(limit, monkeypatch, capsys):
    """Carried from M1 review F9. The model load is monkeypatched out (M1 review
    F11) so the suite's only `main()` caller never pulls a real checkpoint."""
    def _never(*args, **kwargs):
        raise AssertionError("a wrong-arm exit must precede any model load")

    monkeypatch.setattr(m2_depth.transformers.AutoModelForCausalLM, "from_pretrained", _never)
    monkeypatch.setattr(m2_depth.transformers.AutoTokenizer, "from_pretrained", _never)
    monkeypatch.setattr(sys, "argv", [
        "m2_depth.py", "--model-id", "Qwen/Qwen2.5-0.5B-Instruct",
        "--lens", "lenses/qwen2.5-0.5b-instruct-n100.pt", "--limit", str(limit),
    ])
    with pytest.raises(SystemExit) as exc:
        m2_depth.main()
    assert exc.value.code == 2
    assert "--limit must be a positive item count" in capsys.readouterr().out


# --- m1_rescore: the labelled reanalysis --------------------------------------

def test_the_reanalysis_reproduces_the_published_numbers_and_the_brief(tmp_path):
    """D10(a) is only sound if the re-score reproduces M1's published cell from
    the same file — and the widened numbers must match the M2 brief, which
    pre-registered them before any M2 code existed."""
    expected = {
        "qwen2.5-0.5b-instruct": (38, 69, 0, 33, 0.478),
        "qwen2.5-1.5b-instruct": (61, 105, 0, 80, 0.762),
        "qwen2.5-3b-instruct": (44, 116, 12, 92, 0.690),
    }
    for subject, (n_first, n_prefix, primed, control, diff) in expected.items():
        run = m1_rescore.load_run(f"results/m1-battery-{subject}.json")
        package = m1_rescore.rescore(run, "path")
        assert package["oracles"]["first_token"]["gated_n"] == n_first
        prefix = package["oracles"]["prefix"]
        assert prefix["gated_n"] == n_prefix
        assert prefix["naming_success_gated"]["primed_late"]["hits"] == primed
        assert prefix["naming_success_gated"]["control_late"]["hits"] == control
        assert prefix["newcombe_control_minus_primed_late_naming"][0] == pytest.approx(
            diff, abs=5e-4
        )
        assert prefix["positive_and_ci_excludes_zero"] is True
        assert package["milestone"] == "M1-REANALYSIS" and "REANALYSIS" in package["label"]


def test_the_per_source_split_lands_as_a_recorded_number_under_both_oracles():
    """PR #4 review F5, widened at PR #5 review F4: the contrast must hold on the
    120 newly authored items alone, not only on the 60 S4 selected."""
    expected = {
        "qwen2.5-0.5b-instruct": (0.278, 0.389),
        "qwen2.5-1.5b-instruct": (0.545, 0.714),
        "qwen2.5-3b-instruct": (0.478, 0.629),
    }
    for subject, (first, prefix) in expected.items():
        run = m1_rescore.load_run(f"results/m1-battery-{subject}.json")
        split = m1_rescore.rescore(run, "path")["per_source"]
        for reading, value in (("first_token", first), ("prefix", prefix)):
            cell = split[reading]["m1-new"]
            assert cell["newcombe_control_minus_primed_late_naming"][0] == pytest.approx(
                value, abs=5e-4
            )
            assert cell["positive_and_ci_excludes_zero"] is True


def test_the_widening_is_what_unlocks_the_dark_categories():
    package = m1_rescore.rescore(
        m1_rescore.load_run("results/m1-battery-qwen2.5-1.5b-instruct.json"), "path"
    )
    categories = package["per_category_gated"]
    for dark in ("planets", "musical instruments"):
        assert categories["first_token"][dark]["gated_items"] == 0
        assert categories["prefix"][dark]["gated_items"] == 8
    assert package["case_exact_prefix_gate_texture"] == 72  # vs 105 case-insensitive


def test_the_reanalysis_refuses_to_write_when_it_cannot_reproduce_the_analysis(capsys):
    run = json.load(open("results/m1-battery-qwen2.5-1.5b-instruct.json"))
    run["breadth_contrast"]["newcombe_control_minus_primed_late_naming"] = [9.0, 8.0, 9.5]
    with pytest.raises(SystemExit) as exc:
        m1_rescore.rescore(run, "results/m1-battery-qwen2.5-1.5b-instruct.json")
    assert exc.value.code == 2
    assert "cannot reproduce the analysis it sits beside" in capsys.readouterr().out


@pytest.mark.parametrize(
    "broken, expected",
    [
        ({"milestone": "M0"}, "not an M1 battery run"),
        ({"smoke_limit": 3}, "SMOKE run"),
        ({"environment": {"certified": False, "uncertified_reasons": ["device 'cpu'"]}},
         "NOT A RESULT"),
        ({"anchor_crosscheck": {"n_mismatches": 2}}, "cross-check mismatches"),
    ],
)
def test_a_run_that_is_not_a_result_is_not_reanalysable_either(
    broken, expected, tmp_path, capsys
):
    run = json.load(open("results/m1-battery-qwen2.5-0.5b-instruct.json"))
    run.update(broken)
    path = tmp_path / "m1.json"
    path.write_text(json.dumps(run))
    with pytest.raises(SystemExit) as exc:
        m1_rescore.load_run(str(path))
    assert exc.value.code == 2
    assert expected in capsys.readouterr().out


# --- m2_verdict: what may and may not feed the cross-subject verdict ----------

def _run(verdict="LATE-LOCALIZED", **kw):
    run = {
        "milestone": "M2", "smoke_limit": None,
        "environment": {"certified": True, "uncertified_reasons": []},
        "m1_crosscheck": {"n_mismatches": 0, "items_checked": 36, "items_expected": 36},
        "competence": {"gate_span": 34, "items_run": 36},
        "tier_cells": {
            name: {"hits": 0 if name == "primed_late" else 30, "n": 34}
            for name in ("clean", "primed_early", "primed_middle", "primed_late",
                         "control_early", "control_middle", "control_late")
        },
        "localization_contrast": {
            "verdict": verdict,
            "newcombe_primed_early_minus_primed_late_naming": [0.88, 0.7, 0.95],
            "newcombe_primed_middle_minus_primed_late_naming": [0.88, 0.7, 0.95],
            "control_tier_specificity_caveats": [],
        },
        "window_map": [{"start": 19, "end": 24, "is_gate_cell": True,
                        "outside_band": False, "cell": {"hits": 0, "n": 34}}],
        "dose_curve": [{"lambda": lam, "cell": {"hits": 0, "n": 34},
                        "mean_concept_mass_eligible": 0.5, "mass_channel_n": 24}
                       for lam in DOSE_GRID],
    }
    run.update(kw)
    return run


def _run_verdict(monkeypatch, tmp_path, runs):
    for subject, run in runs.items():
        (tmp_path / f"m2-depth-{subject}.json").write_text(json.dumps(run))
    monkeypatch.setattr(sys, "argv", ["m2_verdict.py", "--results-dir", str(tmp_path)])
    with pytest.raises(SystemExit) as exc:
        m2_verdict.main()
    return exc.value.code


def _all(**per_subject):
    return {s: per_subject.get(s, _run()) for s in m2_verdict.SUBJECTS}


def test_the_m2_verdict_is_the_and_over_the_two_gate_bearing_subjects(
    monkeypatch, tmp_path, capsys
):
    assert _run_verdict(monkeypatch, tmp_path, _all()) == 0
    assert "M2 VERDICT: LATE-LOCALIZED at 1.5B AND 3B" in capsys.readouterr().out


def test_a_single_gate_bearing_null_sinks_the_and(monkeypatch, tmp_path, capsys):
    runs = _all(**{"qwen2.5-3b-instruct": _run(verdict="not shown")})
    _run_verdict(monkeypatch, tmp_path, runs)
    out = capsys.readouterr().out
    assert "M2 VERDICT: NOT SHOWN" in out and "qwen2.5-3b-instruct: not shown" in out


def test_the_0_5b_subject_never_enters_the_and(monkeypatch, tmp_path, capsys):
    runs = _all(**{"qwen2.5-0.5b-instruct": _run(verdict="not shown")})
    _run_verdict(monkeypatch, tmp_path, runs)
    out = capsys.readouterr().out
    assert "M2 VERDICT: LATE-LOCALIZED at 1.5B AND 3B" in out
    assert "never gate-bearing" in out


@pytest.mark.parametrize(
    "broken, expected",
    [
        ({"smoke_limit": 3}, "SMOKE run"),
        ({"environment": {"certified": False, "uncertified_reasons": ["device 'cpu'"]}},
         "NOT A RESULT"),
        ({"milestone": "M1"}, "not an M2 depth run"),
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
    runs = {s: _run() for s in m2_verdict.SUBJECTS if s != "qwen2.5-3b-instruct"}
    assert _run_verdict(monkeypatch, tmp_path, runs) == 2
    assert "missing" in capsys.readouterr().out

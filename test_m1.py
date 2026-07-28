"""test_m1.py — invariants for the M1 breadth battery, runner, and verdict.

The heavyweight proof that M1's instrument is still the certified instrument is
the anchor cross-check the runner performs on the 60 reused items at run time.
These tests pin what a model run cannot: the frozen item file's shape and
guards, the pre-committed gate/prevalence/degeneracy arithmetic, and the
INVALID paths — each asserted on the *printed reason*, not merely the exit code
(PR #2 review F9), so a test cannot pass because some other guard fired.
"""
import json
import sys

import pytest

import m1_battery
import m1_verdict
from m1_battery import (
    CLUES_PER_CONCEPT,
    CONCEPTS_PER_CATEGORY,
    CONDITIONS,
    EXPECTED_CATEGORIES,
    EXPECTED_CONCEPTS,
    EXPECTED_ITEMS,
    ITEMS_PATH,
    REUSED_ITEMS,
    anchor_crosscheck,
    breadth_verdict,
    certified_environment,
    clue_leaks,
    descriptive_package,
    load_items,
    sub_band_thirds,
)

S4_ITEMS_PATH = "items/s4-avoidance-items.json"


# --- the frozen battery -------------------------------------------------------

def _battery():
    return json.load(open(ITEMS_PATH))


def test_battery_loads_and_passes_every_frozen_guard():
    items = load_items(ITEMS_PATH)
    assert len(items) == EXPECTED_ITEMS == 180
    assert len({i["name"] for i in items}) == EXPECTED_ITEMS
    assert len({i["concept"] for i in items}) == EXPECTED_CONCEPTS == 60


def test_roster_is_ten_categories_of_six_and_partitions_the_concepts():
    battery = _battery()
    roster = battery["roster"]
    assert len(roster) == EXPECTED_CATEGORIES == 10
    assert all(len(cs) == CONCEPTS_PER_CATEGORY == 6 for cs in roster.values())
    flat = [c for cs in roster.values() for c in cs]
    assert len(flat) == len(set(flat)) == EXPECTED_CONCEPTS  # each concept in ONE category
    assert set(flat) == {i["concept"] for i in battery["items"]}
    # D4(b) dedupe rules, called out by name in the brief.
    assert "spider" in roster["animals"] and "spider" not in roster["insects"]
    assert "fly" not in flat


def test_every_concept_has_three_clues_and_one_fixed_same_category_control():
    battery = _battery()
    roster = battery["roster"]
    groups: dict[str, list[dict]] = {}
    for item in battery["items"]:
        groups.setdefault(item["concept"], []).append(item)
    for concept, group in groups.items():
        assert len(group) == CLUES_PER_CONCEPT == 3
        assert len({i["control"] for i in group}) == 1, concept
        assert len({i["category"] for i in group}) == 1, concept
        assert len({i["clue"] for i in group}) == 3, concept
        for item in group:
            assert item["control"] != item["concept"]
            assert item["control"] in roster[item["category"]]


def test_the_sixty_reused_items_are_S4s_own_items_verbatim():
    """D5(a)'s cross-check is only meaningful if the reused items are byte-equal
    to the frozen S4 set — same clue, same noun, same control pairing."""
    s4 = {i["name"]: i for i in json.load(open(S4_ITEMS_PATH))["items"]}
    reused = [i for i in _battery()["items"] if i["source"] == "s4-reuse"]
    assert len(reused) == REUSED_ITEMS == 60
    assert {i["name"] for i in reused} == set(s4)
    for item in reused:
        assert {k: v for k, v in item.items() if k != "source"} == s4[item["name"]]


def test_new_list_words_are_declared_and_number_seven():
    battery = _battery()
    flat = [c for cs in battery["roster"].values() for c in cs]
    assert len(battery["new_list_words"]) == 7  # the owned D4(b) deviation
    assert all(w in flat for w in battery["new_list_words"])


def test_no_frozen_clue_leaks_its_concept_or_control():
    battery = _battery()
    for item in battery["items"]:
        assert clue_leaks(item, battery["forbidden_forms"]) == []


# --- the leak guard itself ----------------------------------------------------

def _item(clue, concept="lion", control="shark", category="animals"):
    return {
        "name": "probe", "category": category, "noun": "animal",
        "concept": concept, "control": control, "clue": clue, "source": "m1-new",
    }


def test_leak_guard_catches_the_bare_word_and_its_suffixed_derivatives():
    assert clue_leaks(_item("The lion roars."), {})
    assert clue_leaks(_item("Two lions roar."), {})  # suffixed derivative
    assert clue_leaks(_item("It hunts sharks."), {})  # the CONTROL leaks too
    assert clue_leaks(_item("This big cat is king of the jungle."), {}) == []


def test_leak_guard_catches_root_changing_derivatives_only_via_forbidden_forms():
    france = _item("A French village.", concept="France", control="Canada",
                   category="countries")
    assert clue_leaks(france, {}) == []  # a prefix test alone cannot see it
    assert clue_leaks(france, {"France": ["french"]})


def test_leak_guard_does_not_fire_on_a_word_that_merely_contains_the_concept():
    """Why the guard is prefix-at-a-word-boundary rather than S4's substring
    test: with 60 short concepts, a substring test makes 'plant' a leak for
    'ant' and 'chamber' one for 'amber', which would rule out ordinary English."""
    assert clue_leaks(_item("They plant crops.", concept="ant", control="bee",
                            category="insects"), {}) == []
    assert clue_leaks(_item("A vaulted chamber.", concept="amber",
                            control="jade", category="gemstones"), {}) == []


def test_leak_guard_stays_conservative_on_a_genuine_prefix():
    """The other direction is deliberate: a word that really does begin with the
    concept is flagged even when it is unrelated ('mother' for 'moth'). That
    costs an author one word choice and can never let a real derivative through."""
    assert clue_leaks(_item("His mother waited.", concept="moth",
                            control="bee", category="insects"), {})


# --- load_items INVALID guards, each asserted on its own message --------------

def _write(tmp_path, battery):
    path = tmp_path / "battery.json"
    path.write_text(json.dumps(battery))
    return str(path)


def test_load_items_rejects_a_missing_block(tmp_path):
    battery = _battery()
    del battery["forbidden_forms"]
    with pytest.raises(ValueError, match="missing its 'forbidden_forms' block"):
        load_items(_write(tmp_path, battery))


def test_load_items_rejects_a_shape_drift(tmp_path):
    battery = _battery()
    battery["items"] = battery["items"][:-1]
    with pytest.raises(ValueError, match="drifted from the frozen 180-item shape"):
        load_items(_write(tmp_path, battery))


def test_load_items_rejects_a_roster_drift(tmp_path):
    battery = _battery()
    battery["roster"]["animals"] = battery["roster"]["animals"][:-1]
    with pytest.raises(ValueError, match="roster drifted"):
        load_items(_write(tmp_path, battery))


def test_load_items_rejects_a_leaky_clue(tmp_path):
    battery = _battery()
    battery["items"][0]["clue"] = "This country is France, obviously."
    with pytest.raises(ValueError, match="clue leaks"):
        load_items(_write(tmp_path, battery))


def test_load_items_rejects_control_equal_to_concept(tmp_path):
    battery = _battery()
    for item in battery["items"]:  # all three clues, or the fixity guard fires first
        if item["concept"] == "France":
            item["control"] = "France"
    with pytest.raises(ValueError, match="control equals concept"):
        load_items(_write(tmp_path, battery))


def test_load_items_rejects_a_control_that_varies_across_a_concepts_clues(tmp_path):
    battery = _battery()
    battery["items"][0]["control"] = "China"  # France's other two still say Canada
    with pytest.raises(ValueError, match="control is not fixed"):
        load_items(_write(tmp_path, battery))


def test_load_items_rejects_a_control_from_another_category(tmp_path):
    battery = _battery()
    for item in battery["items"]:
        if item["concept"] == "lion":
            item["control"] = "Mars"
    with pytest.raises(ValueError, match="is not in its own category's roster"):
        load_items(_write(tmp_path, battery))


def test_load_items_rejects_a_wrong_reused_count(tmp_path):
    battery = _battery()
    for item in battery["items"]:
        if item["source"] == "s4-reuse":
            item["source"] = "m1-new"
    with pytest.raises(ValueError, match="reused S4 items"):
        load_items(_write(tmp_path, battery))


def test_load_items_rejects_a_concept_with_the_wrong_clue_count(tmp_path):
    """Re-labelling one clue keeps the item count at 180 and the concept count
    at 60, so only the per-concept guard can catch it."""
    battery = _battery()
    last = battery["items"][-1]
    assert last["concept"] == "Sunday"
    last["concept"], last["control"] = "Monday", "Tuesday"  # Monday now has 4
    with pytest.raises(ValueError, match="clues, expected 3"):
        load_items(_write(tmp_path, battery))


def test_load_items_rejects_a_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError, match="frozen M1 battery"):
        load_items(str(tmp_path / "nope.json"))


# --- validate(): every wrong-arm guard proved by its printed reason (F9) ------

class _FakeSubject:
    d_model = 896
    n_layers = 24


class _Args:
    def __init__(self, **kw):
        self.model_id = "Qwen/Qwen2.5-0.5B-Instruct"
        self.anchor = None
        self.__dict__.update(kw)


def _good_artifact():
    return {
        "model_id": "Qwen/Qwen2.5-0.5B-Instruct",
        "d_model": 896,
        "J": {l: None for l in range(23)},
    }


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
        m1_battery.validate(_Args(), artifact, _FakeSubject())
    assert exc.value.code == 2
    assert expected in capsys.readouterr().out


def test_validate_rejects_a_missing_anchor_recording(capsys, tmp_path):
    with pytest.raises(SystemExit) as exc:
        m1_battery.validate(
            _Args(anchor=str(tmp_path / "absent.json")), _good_artifact(), _FakeSubject()
        )
    assert exc.value.code == 2
    assert "anchor recording" in capsys.readouterr().out


def test_validate_rejects_an_anchor_recorded_on_another_subject(capsys):
    args = _Args(anchor="anchors/s4-avoidance-qwen2.5-1.5b-instruct.json")
    with pytest.raises(SystemExit) as exc:
        m1_battery.validate(args, _good_artifact(), _FakeSubject())
    assert exc.value.code == 2
    assert "is for" in capsys.readouterr().out


def test_validate_accepts_the_real_configuration():
    assert m1_battery.validate(_Args(), _good_artifact(), _FakeSubject()) == list(
        range(9, 22)
    )


def test_reused_items_are_ordered_ahead_of_every_new_one():
    """PR #3 F7: the cross-check can only fire 'before any new cell is read' if
    the reused items are graded first — and within each group, file order holds."""
    planned = [
        ({"name": "japan-1", "source": "m1-new"}, {}),
        ({"name": "france-1", "source": "s4-reuse"}, {}),
        ({"name": "brazil-1", "source": "m1-new"}, {}),
        ({"name": "china-1", "source": "s4-reuse"}, {}),
    ]
    reused, fresh = m1_battery.order_reused_first(planned)
    assert [i["name"] for i, _ in reused] == ["france-1", "china-1"]
    assert [i["name"] for i, _ in fresh] == ["japan-1", "brazil-1"]


def test_the_frozen_battery_actually_yields_sixty_reused_items_to_grade_first():
    planned = [(i, {}) for i in load_items(ITEMS_PATH)]
    reused, fresh = m1_battery.order_reused_first(planned)
    assert len(reused) == REUSED_ITEMS and len(fresh) == EXPECTED_ITEMS - REUSED_ITEMS


def test_late_third_is_the_band_tail():
    band = list(range(9, 22))
    assert sub_band_thirds(band)["late"] == band[8:]


# --- the certified-environment scoping (PR #3 F7) -----------------------------

def test_environment_is_certified_only_on_mps_under_the_pins(monkeypatch):
    monkeypatch.setattr(m1_battery.torch, "__version__", "2.13.0")
    monkeypatch.setattr(m1_battery.transformers, "__version__", "5.13.1")
    assert certified_environment("mps") == (True, [])
    certified, reasons = certified_environment("cpu")
    assert certified is False and any("device" in r for r in reasons)
    monkeypatch.setattr(m1_battery.torch, "__version__", "2.14.0")
    certified, reasons = certified_environment("mps")
    assert certified is False and any("torch" in r for r in reasons)


# --- the anchor cross-check ---------------------------------------------------

def _record(name="france-1", produced=(True, False, True), greedy=("France", "The", "France")):
    return {
        "name": name, "source": "s4-reuse", "category": "countries",
        "concept": "France", "control": "Canada",
        "cells": {
            c: {"produced": p, "greedy": g, "concept_mass": 0.5,
                "greedy_3": g, "says_concept_in_3": p}
            for c, p, g in zip(CONDITIONS, produced, greedy)
        },
        "gate_greedy": produced[0], "gate_verbatim_p": False,
    }


def _anchor_file(tmp_path, cells=None):
    cells = cells or {
        c: {"produced": p, "greedy": g, "concept_mass": 0.5}
        for c, p, g in zip(CONDITIONS, (True, False, True), ("France", "The", "France"))
    }
    path = tmp_path / "anchor.json"
    path.write_text(json.dumps({
        "model_id": "Qwen/Test",
        "items": [{"name": "france-1", "instructions": {"naming": cells}}],
    }))
    return str(path)


def test_crosscheck_passes_on_an_exact_reproduction(tmp_path):
    problems, texture = anchor_crosscheck([_record()], _anchor_file(tmp_path))
    assert problems == []
    assert texture == {
        "items_checked": 1, "items_expected": REUSED_ITEMS,
        "cells_checked": 3, "cells_expected": REUSED_ITEMS * len(CONDITIONS),
        "mass_cells_equal": 3,
    }


def test_crosscheck_reports_the_expected_counts_so_coverage_is_checkable(tmp_path):
    """F1: '0 mismatches' only re-certifies the instrument if all 60 reused items
    were actually compared, so the artifact must carry the expected counts —
    and it must carry them as data, not as a constant re-bound by each consumer."""
    _, texture = anchor_crosscheck([_record()], _anchor_file(tmp_path))
    assert texture["items_expected"] == REUSED_ITEMS == 60
    assert texture["items_checked"] < texture["items_expected"]  # a subset, and it says so


def test_crosscheck_catches_a_flipped_produced_and_a_drifted_greedy_token(tmp_path):
    anchor = _anchor_file(tmp_path)
    problems, _ = anchor_crosscheck(
        [_record(produced=(True, True, True))], anchor
    )
    assert len(problems) == 1 and "primed_late.produced" in problems[0]
    problems, _ = anchor_crosscheck(
        [_record(greedy=("France", "A", "France"))], anchor
    )
    assert len(problems) == 1 and "primed_late.greedy" in problems[0]


def test_crosscheck_catches_an_item_absent_from_the_recording(tmp_path):
    problems, _ = anchor_crosscheck([_record(name="ghost-1")], _anchor_file(tmp_path))
    assert len(problems) == 1 and "absent from the anchor recording" in problems[0]


def test_crosscheck_ignores_new_items_and_treats_mass_as_texture(tmp_path):
    new = dict(_record(name="japan-1"), source="m1-new")
    problems, texture = anchor_crosscheck([_record(), new], _anchor_file(tmp_path))
    assert problems == [] and texture["items_checked"] == 1

    drifted = _record()
    drifted["cells"]["clean"]["concept_mass"] = 0.4999
    problems, texture = anchor_crosscheck([drifted], _anchor_file(tmp_path))
    assert problems == [] and texture["mass_cells_equal"] == 2


# --- the pre-committed descriptive package ------------------------------------

def _synthetic(concept, category, clean, primed, control, source="m1-new"):
    """One record per (clean, primed, control) triple of booleans."""
    return {
        "name": f"{concept}-{clean}{primed}{control}", "category": category,
        "concept": concept, "control": "other", "source": source,
        "cells": {
            c: {"produced": p, "greedy": "x", "concept_mass": 0.9,
                "greedy_3": concept if p else "xyz", "says_concept_in_3": p}
            for c, p in zip(CONDITIONS, (clean, primed, control))
        },
        "gate_greedy": clean, "gate_verbatim_p": clean,
    }


def _three(concept, category, primed, control, clean=(True, True, True)):
    return [
        _synthetic(concept, category, cl, p, ct)
        for cl, p, ct in zip(clean, primed, control)
    ]


def test_gate_is_naming_only_and_pooled_cells_count_gated_items_only():
    records = _three("lion", "animals", (False, False, False), (True, True, True))
    records += _three(
        "eagle", "animals", (True, True, True), (True, True, True),
        clean=(False, False, False),  # ungated: clean naming failed
    )
    package = descriptive_package(records)
    assert package["competence"]["items_run"] == 6
    assert package["competence"]["gate_greedy"] == 3  # only lion's items gate in
    assert package["naming_success_gated"]["primed_late"]["hits"] == 0
    assert package["naming_success_gated"]["control_late"]["hits"] == 3
    assert package["naming_success_gated"]["clean"]["n"] == 3


def test_breadth_contrast_is_control_minus_primed_and_flags_underpowered():
    records = []
    for k in range(10):  # 30 gated items, all hard-switch
        records += _three(f"c{k}", "animals", (False,) * 3, (True,) * 3)
    package = descriptive_package(records)
    diff = package["breadth_contrast"]["newcombe_control_minus_primed_late_naming"]
    assert diff[0] == pytest.approx(1.0)
    assert package["breadth_contrast"]["positive_and_ci_excludes_zero"] is True
    assert package["breadth_contrast"]["underpowered"] is False  # n = 30 >= MIN_N

    small = descriptive_package(_three("lion", "animals", (False,) * 3, (True,) * 3))
    assert small["breadth_contrast"]["underpowered"] is True  # n = 3


def test_prevalence_uses_the_fixed_all_three_gated_denominator():
    records = _three("lion", "animals", (False, False, False), (True, True, True))
    # eagle: all 3 gated but control_late is not 3/3 — in the denominator, not a hit
    records += _three("eagle", "animals", (False, False, False), (True, True, False))
    # shark: all 3 gated, primed_late names once — in the denominator, not a hit
    records += _three("shark", "animals", (True, False, False), (True, True, True))
    # spider: only 2 items gated, and they look like a perfect switch — must be
    # excluded from the fixed denominator and reported stratified instead
    records += _three(
        "spider", "animals", (False, False, True), (True, True, True),
        clean=(True, True, False),
    )
    package = descriptive_package(records)
    prevalence = package["prevalence"]
    assert prevalence["fixed_denominator_concepts"] == ["eagle", "lion", "shark"]
    assert prevalence["hard_switch_concepts"] == ["lion"]
    assert prevalence["cell"]["hits"] == 1 and prevalence["cell"]["n"] == 3
    assert prevalence["cell"]["underpowered"] is True  # 3 < MIN_N, pre-declared
    stratified = prevalence["partial_gated_concepts_stratified"]
    assert stratified["2"]["concepts"] == ["spider"]
    assert stratified["2"]["profile_at_own_denominator"] == ["spider"]
    assert "spider" not in prevalence["fixed_denominator_concepts"]


def test_a_concept_with_no_gated_item_is_in_neither_the_denominator_nor_a_stratum():
    records = _three(
        "lion", "animals", (False,) * 3, (True,) * 3, clean=(False, False, False)
    )
    prevalence = descriptive_package(records)["prevalence"]
    assert prevalence["fixed_denominator_concepts"] == []
    assert prevalence["partial_gated_concepts_stratified"] == {}


def test_per_concept_and_per_category_maps_are_descriptive_and_complete():
    records = _three("lion", "animals", (False,) * 3, (True,) * 3)
    records += _three("Mars", "planets", (True, False, False), (True, True, True))
    package = descriptive_package(records)
    assert set(package["per_concept"]) == {"lion", "Mars"}
    assert package["per_concept"]["lion"]["category"] == "animals"
    assert package["per_concept"]["lion"]["gated_items"] == 3
    assert package["per_concept"]["Mars"]["primed_late"]["hits"] == 1
    assert set(package["per_category"]) == {"animals", "planets"}
    assert package["per_category"]["animals"]["gated_items"] == 3
    # Wilson CIs on every descriptive cell — the "a cell without a CI is not a
    # result" guardrail, in code.
    assert len(package["per_concept"]["lion"]["primed_late"]["wilson_95"]) == 2
    assert len(package["per_category"]["planets"]["control_late"]["wilson_95"]) == 2


def test_greedy_3_texture_counts_but_never_gates():
    """The texture readout must record what the single-token gate cannot see —
    and must not move a single gated cell while doing it."""
    # lion: ungated (clean naming missed) but the model does say the word
    records = _three("lion", "animals", (False,) * 3, (True,) * 3,
                     clean=(False, False, False))
    for record in records:
        record["cells"]["clean"]["says_concept_in_3"] = True
    records += _three("Mars", "planets", (False,) * 3, (True,) * 3)
    package = descriptive_package(records)
    texture = package["greedy_3_texture"]
    assert texture["ungated_items"] == 3
    assert texture["ungated_but_says_concept_in_3"] == 3
    assert texture["gated_primed_late_says_concept_in_3"] == 0  # really muted
    assert texture["gated_control_late_says_concept_in_3"] == 3
    # the gate and the contrast are untouched by any of it
    assert package["competence"]["gate_greedy"] == 3
    assert package["naming_success_gated"]["primed_late"]["hits"] == 0


def test_says_concept_is_case_insensitive_and_substring_based():
    assert m1_battery.says_concept("The answer is Mars.", "Mars")
    assert m1_battery.says_concept(" mars", "Mars")
    assert not m1_battery.says_concept("Jupiter", "Mars")


# --- the pre-committed verdict precedence -------------------------------------

def test_verdict_precedence_is_frozen():
    assert breadth_verdict(True, [], False, True) == "BREADTH-SPECIFIC"
    assert breadth_verdict(True, [], False, False) == "not shown"
    assert breadth_verdict(True, [], True, True).startswith("UNDERPOWERED")
    # a degenerate comparison arm outranks both, and an uncertified run outranks all
    assert breadth_verdict(True, ["control_late"], False, True).startswith("DEGENERATE")
    assert breadth_verdict(True, ["clean"], True, True).startswith("DEGENERATE")
    assert breadth_verdict(False, [], False, True).startswith("NOT A RESULT")


def test_a_smoke_run_says_so_in_the_verdict_field_not_just_the_banner():
    """F2: `--limit` is the project's other pre-declared not-a-result condition
    (CLAUDE.md: '--limit is smoke, never a result'), and it must outrank every
    other branch — including a certified environment with a holding contrast."""
    assert breadth_verdict(True, [], False, True, limit=30) == (
        "NOT A RESULT — smoke run (--limit 30)"
    )
    assert breadth_verdict(False, ["clean"], True, False, limit=1).startswith(
        "NOT A RESULT — smoke run"
    )
    # and it must not perturb a real run: limit=None is the pre-fix behaviour
    assert breadth_verdict(True, [], False, True, limit=None) == "BREADTH-SPECIFIC"


def test_degeneracy_disposition_would_not_have_fired_on_the_anchor_subjects():
    """The disposition is pre-committed, so it must be checked against the data
    that already exists: on both gate-bearing anchors, neither comparison arm
    collapses on the gated cell, so the frozen rule changes no anchor verdict."""
    from collections import Counter

    from harness import COLLAPSE_SHARE

    for subject in ("qwen2.5-1.5b-instruct", "qwen2.5-3b-instruct"):
        anchor = json.load(open(f"anchors/s4-avoidance-{subject}.json"))
        gated = [r for r in anchor["items"] if r["gate_greedy"]]
        for arm in ("clean", "control_late"):
            tokens = [r["instructions"]["naming"][arm]["greedy"] for r in gated]
            share = Counter(tokens).most_common(1)[0][1] / len(tokens)
            assert share < COLLAPSE_SHARE, f"{subject}/{arm} collapses at {share:.3f}"


# --- m1_verdict: what may and may not feed the cross-subject verdict ----------

def _run(verdict="BREADTH-SPECIFIC", fixed=("lion", "Mars"), hard=("lion",), **kw):
    run = {
        "milestone": "M1",
        "smoke_limit": None,
        "environment": {"certified": True, "uncertified_reasons": []},
        "anchor_crosscheck": {
            "n_mismatches": 0, "items_checked": 60, "items_expected": 60,
        },
        "competence": {"gate_greedy": 40, "items_run": 180},
        "naming_success_gated": {
            c: {"hits": 40 if c != "primed_late" else 0, "n": 40} for c in CONDITIONS
        },
        "breadth_contrast": {
            "verdict": verdict,
            "newcombe_control_minus_primed_late_naming": [1.0, 0.8, 1.0],
        },
        "prevalence": {
            "fixed_denominator_concepts": list(fixed),
            "hard_switch_concepts": list(hard),
            "cell": {"hits": len(hard), "n": len(fixed), "underpowered": True},
        },
    }
    run.update(kw)
    return run


def _results_dir(tmp_path, runs):
    for subject, run in runs.items():
        (tmp_path / f"m1-battery-{subject}.json").write_text(json.dumps(run))
    return str(tmp_path)


def _all_subjects(**per_subject):
    return {s: per_subject.get(s, _run()) for s in m1_verdict.SUBJECTS}


def _run_verdict(monkeypatch, tmp_path, runs):
    monkeypatch.setattr(
        sys, "argv", ["m1_verdict.py", "--results-dir", _results_dir(tmp_path, runs)]
    )
    with pytest.raises(SystemExit) as exc:
        m1_verdict.main()
    return exc.value.code


def test_m1_verdict_is_the_and_over_the_two_gate_bearing_subjects(monkeypatch, tmp_path, capsys):
    code = _run_verdict(monkeypatch, tmp_path, _all_subjects())
    out = capsys.readouterr().out
    assert code == 0
    assert "M1 VERDICT: BREADTH-SPECIFIC at 1.5B AND 3B" in out


def test_a_single_gate_bearing_null_sinks_the_and(monkeypatch, tmp_path, capsys):
    runs = _all_subjects(**{"qwen2.5-3b-instruct": _run(verdict="not shown")})
    _run_verdict(monkeypatch, tmp_path, runs)
    out = capsys.readouterr().out
    assert "M1 VERDICT: NOT SHOWN" in out and "qwen2.5-3b-instruct: not shown" in out


def test_the_0_5b_subject_never_enters_the_and(monkeypatch, tmp_path, capsys):
    runs = _all_subjects(**{"qwen2.5-0.5b-instruct": _run(verdict="not shown")})
    _run_verdict(monkeypatch, tmp_path, runs)
    out = capsys.readouterr().out
    assert "M1 VERDICT: BREADTH-SPECIFIC at 1.5B AND 3B" in out
    assert "never gate-bearing" in out


def test_prevalence_intersection_is_reported_as_texture(monkeypatch, tmp_path, capsys):
    runs = _all_subjects(
        **{"qwen2.5-3b-instruct": _run(fixed=("lion", "Mars"), hard=("Mars",))}
    )
    _run_verdict(monkeypatch, tmp_path, runs)
    out = capsys.readouterr().out
    assert "PREVALENCE INTERSECTION" in out
    assert "share 2 all-3-gated concepts, of which 0" in out


@pytest.mark.parametrize(
    "broken, expected",
    [
        ({"smoke_limit": 3}, "SMOKE run"),
        ({"environment": {"certified": False, "uncertified_reasons": ["device 'cpu'"]}},
         "NOT A RESULT"),
        ({"milestone": "M0"}, "not an M1 battery run"),
        ({"anchor_crosscheck": {"n_mismatches": 4}}, "cross-check mismatches"),
        # F1: a clean cross-check over a SUBSET of the reused items is not a
        # re-certification, and must not be able to feed the verdict either.
        ({"anchor_crosscheck": {
            "n_mismatches": 0, "items_checked": 59, "items_expected": 60,
        }}, "cross-checked 59 of 60 reused items"),
        ({"anchor_crosscheck": {"n_mismatches": 0, "items_checked": 60}},
         "cross-checked 60 of None reused items"),
    ],
)
def test_a_run_that_is_not_a_result_cannot_feed_the_verdict(
    broken, expected, monkeypatch, tmp_path, capsys
):
    runs = _all_subjects(**{"qwen2.5-1.5b-instruct": _run(**broken)})
    assert _run_verdict(monkeypatch, tmp_path, runs) == 2
    assert expected in capsys.readouterr().out


def test_m1_verdict_is_invalid_when_a_subject_is_missing(monkeypatch, tmp_path, capsys):
    runs = {s: _run() for s in m1_verdict.SUBJECTS if s != "qwen2.5-3b-instruct"}
    assert _run_verdict(monkeypatch, tmp_path, runs) == 2
    assert "missing" in capsys.readouterr().out

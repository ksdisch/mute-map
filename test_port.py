"""test_port.py — invariants for the D2 ported surface + the D3 comparator.

The heavyweight proof that the port is faithful is the M0 anchor gate itself
(bit-for-bit vs dim-stage's recorded JSONs); these tests pin the pure-geometry
and pure-logic pieces so a regression is caught in milliseconds, not a model run.
"""
import copy
import json

import pytest
import torch

from harness import FROZEN_BANDS, proportional_band, rate_cell, token_forms
from intervention import ablate, jlens_vector
from m0_anchor import ITEMS_PATH, load_items, sub_band_thirds
from m0_port_gate import SUBJECTS, compare_pair

torch.manual_seed(0)


# --- band conventions ---------------------------------------------------------

def test_proportional_band_matches_frozen_table():
    for n_layers, band in FROZEN_BANDS.items():
        assert proportional_band(n_layers) == band


def test_sub_band_thirds_partition_the_band():
    for band in FROZEN_BANDS.values():
        thirds = sub_band_thirds(band)
        assert thirds["early"] + thirds["middle"] + thirds["late"] == band


def test_thirds_match_anchor_recordings():
    """The recorded instrument config in the anchors is exactly what our port
    computes — a mismatch here means the wrong band would be ablated."""
    for subject in SUBJECTS:
        ref = json.load(open(f"anchors/s4-avoidance-{subject}.json"))
        band = ref["band"]
        assert proportional_band(_n_layers(band)) == band
        assert sub_band_thirds(band) == ref["thirds"]


def _n_layers(band):
    """Invert proportional_band for the frozen table (test helper)."""
    for n_layers, frozen in FROZEN_BANDS.items():
        if frozen == band:
            return n_layers
    raise AssertionError(f"band {band} not in the frozen table")


# --- operator geometry --------------------------------------------------------

def test_jlens_vector_is_jacobian_transpose_times_row():
    jacobian = torch.randn(8, 8)
    row = torch.randn(8)
    assert torch.allclose(jlens_vector(jacobian, row), jacobian.T @ row)


def test_ablate_zeroes_every_direction_coordinate():
    h = torch.randn(5, 16)
    directions = torch.randn(5, 3, 16)
    out = ablate(h, directions)
    coords = torch.einsum("sd,skd->sk", out.double(), directions.double())
    # The projection is computed in float64 but the result rounds back to h's
    # fp32 — residual coordinates of order 1e-7 are that rounding, not error
    # (the runner's own read-back bar is 1e-4 relative for the same reason).
    scale = directions.norm(dim=-1) * h.norm(dim=-1, keepdim=True)
    assert float((coords.abs() / scale).max()) < 1e-6


def test_ablate_preserves_orthogonal_complement():
    d = 16
    directions = torch.zeros(1, 2, d)
    directions[0, 0, 0], directions[0, 1, 1] = 1.0, 1.0
    h = torch.randn(1, d)
    out = ablate(h, directions)
    assert float(out[0, 0].abs()) < 1e-12 and float(out[0, 1].abs()) < 1e-12
    assert torch.allclose(out[0, 2:], h[0, 2:], atol=1e-6)


def test_ablate_k0_is_exact_noop():
    h = torch.randn(4, 16)
    assert torch.equal(ablate(h, torch.zeros(4, 0, 16)), h)


def test_ablate_handles_duplicate_directions():
    """Near-duplicate direction sets (the ill-conditioned case MGS exists for)
    still zero the shared coordinate without blowing up."""
    d = 16
    base = torch.randn(d)
    directions = torch.stack([base, base * (1 + 1e-12)]).unsqueeze(0)
    h = torch.randn(1, d)
    out = ablate(h, directions)
    assert float((out[0] @ base).abs() / base.norm() / h.norm()) < 1e-6


# --- readout conventions ------------------------------------------------------

class _StubTokenizer:
    """Minimal tokenizer: 'cat' and ' cat' are single tokens; 'zebra' is not."""

    _table = {"cat": [7], " cat": [8], "zebra": [1, 2], " zebra": [3, 4]}

    def __call__(self, text, add_special_tokens=False):
        class Enc:
            def __init__(self, ids):
                self.input_ids = ids

        return Enc(self._table[text])


def test_token_forms_bare_first_and_single_token_only():
    tok = _StubTokenizer()
    assert token_forms("cat", tok) == [7, 8]
    assert token_forms("zebra", tok) == []


def test_rate_cell_shape():
    cell = rate_cell(3, 10)
    assert cell["hits"] == 3 and cell["n"] == 10 and cell["rate"] == 0.3
    assert cell["underpowered"] is True
    lb, ub = cell["wilson_95"]
    assert 0.0 <= lb < 0.3 < ub <= 1.0


# --- frozen items -------------------------------------------------------------

def test_frozen_items_load_and_pass_guards():
    items = load_items(ITEMS_PATH)
    assert len(items) == 60
    assert len({i["name"] for i in items}) == 60


# --- the D3 comparator --------------------------------------------------------

def _fake_results(model_id="Qwen/Test"):
    conditions = (
        "clean",
        "primed_early", "primed_middle", "primed_late",
        "control_early", "control_middle", "control_late",
    )

    def cells(produced):
        return {
            c: {"produced": produced, "greedy": "x", "concept_mass": 0.5}
            for c in conditions
        }

    return {
        "model_id": model_id,
        "band": [1, 2, 3],
        "thirds": {"early": [1], "middle": [2], "late": [3]},
        "dropped_single_token_prefilter": [],
        "competence": {"gate_greedy": 1},
        "items": [
            {
                "name": "item-a",
                "gate_greedy": True,
                "gate_verbatim_p": False,
                "instructions": {"naming": cells(True), "avoidance": cells(False)},
            }
        ],
    }


def test_compare_pair_identical_passes_with_full_texture():
    ours, ref = _fake_results(), _fake_results()
    problems, texture = compare_pair(ours, ref)
    assert problems == []
    assert texture == {
        "mass_cells_equal": 14, "mass_cells_total": 14, "gate_verbatim_p_equal": True
    }


def test_compare_pair_catches_a_flipped_greedy_cell():
    ours, ref = _fake_results(), _fake_results()
    ours["items"][0]["instructions"]["naming"]["primed_late"]["produced"] = False
    problems, _ = compare_pair(ours, ref)
    assert len(problems) == 1 and "primed_late.produced" in problems[0]


def test_compare_pair_catches_gate_membership_drift():
    ours, ref = _fake_results(), _fake_results()
    ours["items"][0]["gate_greedy"] = False
    problems, _ = compare_pair(ours, ref)
    assert any("gate_greedy" in p for p in problems)


def test_compare_pair_catches_config_drift_before_cells():
    ours, ref = _fake_results(), _fake_results()
    ours["band"] = [1, 2, 4]
    problems, _ = compare_pair(ours, ref)
    assert len(problems) == 1 and problems[0].startswith("config band")


def test_compare_pair_mass_drift_is_texture_not_failure():
    ours, ref = _fake_results(), _fake_results()
    ours["items"][0]["instructions"]["naming"]["clean"]["concept_mass"] = 0.4999
    problems, texture = compare_pair(ours, ref)
    assert problems == []
    assert texture["mass_cells_equal"] == 13


# --- anchor meta-guard --------------------------------------------------------

def test_anchor_recordings_carry_the_expected_s4b_verdicts():
    """Guard against silent anchor-file drift: the copied dim-stage JSONs must
    still say what S4b's brief says they say (gates 5/22/8; D31 holds at 1.5B
    and 3B, not at 0.5B)."""
    expected = {
        "qwen2.5-0.5b-instruct": (5, False),
        "qwen2.5-1.5b-instruct": (22, True),
        "qwen2.5-3b-instruct": (8, True),
    }
    for subject, (gate_n, d31_holds) in expected.items():
        ref = json.load(open(f"anchors/s4-avoidance-{subject}.json"))
        assert ref["competence"]["gate_greedy"] == gate_n
        assert ref["late_switch_specificity"]["holds"] is d31_holds

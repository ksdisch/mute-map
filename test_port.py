"""test_port.py — invariants for the D2 ported surface + the D3 comparator.

The heavyweight proof that the port is faithful is the M0 anchor gate itself
(bit-for-bit vs dim-stage's recorded JSONs); these tests pin the pure-geometry
and pure-logic pieces so a regression is caught in milliseconds, not a model run.
"""
import json
import sys

import pytest
import torch

import m0_anchor
import m0_port_gate
from harness import FROZEN_BANDS, proportional_band, rate_cell, token_forms
from intervention import ablate, edit_residuals, jlens_vector
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


# --- frozen items + INVALID guards (ported from dim-stage test_avoidance.py) --

def test_frozen_items_load_and_pass_guards():
    items = load_items(ITEMS_PATH)
    assert len(items) == 60
    assert len({i["name"] for i in items}) == 60
    assert len({i["concept"] for i in items}) == 20


def test_load_items_guards_shape_and_leakage(tmp_path):
    bad = tmp_path / "items.json"
    bad.write_text(json.dumps({"items": [{"name": "x"}]}))
    with pytest.raises(ValueError, match="drifted"):
        load_items(str(bad))

    leaky = {
        "items": [
            {
                "name": f"i{k}", "category": "c", "noun": "thing",
                "concept": "France", "control": "Canada",
                "clue": "A sentence about France." if k == 0 else "A clean clue.",
            }
            for k in range(60)
        ]
    }
    bad.write_text(json.dumps(leaky))
    with pytest.raises(ValueError, match="contains 'France'"):
        load_items(str(bad))


def test_sub_band_thirds_ordered_slices():
    band = list(range(9, 22))  # 0.5B: 13 layers
    thirds = sub_band_thirds(band)
    assert thirds["early"] == band[:4]
    assert thirds["middle"] == band[4:8]
    assert thirds["late"] == band[8:]


def test_concept_ablation_edit_zeroes_exactly_the_concept_coordinate():
    # Identity Jacobian + basis-vector unembedding row: the edit must zero
    # coordinate 1 at every position and leave every other coordinate exact.
    d = 8
    u = torch.zeros(d)
    u[1] = 1.0
    edits = m0_anchor.concept_ablation_edits({0: torch.eye(d)}, [0], u)
    h = torch.randn(1, 5, d, generator=torch.Generator().manual_seed(0))
    out = edits[0](h.clone())
    assert torch.allclose(out[0, :, 1], torch.zeros(5), atol=1e-6)
    keep = [i for i in range(d) if i != 1]
    assert torch.allclose(out[0][:, keep], h[0][:, keep], atol=1e-6)


def test_concept_ablation_readback_fires_invalid_on_a_rigged_operator(monkeypatch):
    monkeypatch.setattr(m0_anchor, "ablate", lambda h, v: h + 1.0)  # broken operator
    d = 8
    u = torch.zeros(d)
    u[1] = 1.0
    edits = m0_anchor.concept_ablation_edits({0: torch.eye(d)}, [0], u)
    h = torch.randn(1, 3, d, generator=torch.Generator().manual_seed(1))
    with pytest.raises(SystemExit) as exc:
        edits[0](h)
    assert exc.value.code == 2


def test_conditions_carry_the_d31_control_tiers():
    assert m0_anchor.CONDITIONS == (
        "clean",
        "primed_early", "primed_middle", "primed_late",
        "control_early", "control_middle", "control_late",
    )
    for c in m0_anchor.CONDITIONS[1:]:
        kind, tier = c.split("_")
        assert kind in ("primed", "control") and tier in ("early", "middle", "late")


def test_concept_mass_sums_softmax_over_forms():
    logits = torch.log(torch.tensor([0.5, 0.25, 0.125, 0.125]))
    assert m0_anchor.concept_mass(logits, [1, 2]) == pytest.approx(0.375, abs=1e-6)


def test_validate_rejects_a_mismatched_lens():
    class FakeSubject:
        d_model = 4
        n_layers = 24

    class Args:
        model_id = "Qwen/Qwen2.5-0.5B-Instruct"

    artifact = {"model_id": "Qwen/Qwen2.5-1.5B-Instruct", "d_model": 4, "J": {}}
    with pytest.raises(SystemExit) as exc:
        m0_anchor.validate(Args(), artifact, FakeSubject())
    assert exc.value.code == 2


def test_edit_hooks_apply_and_are_removed_on_exit():
    layers = torch.nn.ModuleList([torch.nn.Identity(), torch.nn.Identity()])

    def forward(x):
        for layer in layers:
            x = layer(x)
        return x

    x = torch.ones(1, 2, 4)
    with edit_residuals(layers, {0: lambda h: h + 1.0}):
        assert torch.equal(forward(x.clone()), x + 1.0)
    assert torch.equal(forward(x.clone()), x)  # hooks gone after the context exits


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
        "lens": "lenses/whichever-copy.pt",
        "lens_n_prompts": 100,
        "protocol": {
            "gate": "greedy-based (D29); verbatim P .85/.15 reported alongside",
            "readback_tol": 1e-4,
            "min_n": 20,
            "collapse_share": 0.5,
        },
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


def test_compare_pair_catches_a_greedy_token_drift():
    """Pins the greedy-token half of D3's gating cell: a flipped decoded token
    with `produced` unchanged must still be a mismatch."""
    ours, ref = _fake_results(), _fake_results()
    ours["items"][0]["instructions"]["avoidance"]["clean"]["greedy"] = "y"
    problems, _ = compare_pair(ours, ref)
    assert len(problems) == 1 and "clean.greedy" in problems[0]


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


#: An anchor file that exists on disk — the half-pair tests must use a real path
#: so load()'s missing-file branch cannot absorb the assertion (F8).
EXISTING_ANCHOR = "anchors/s4-avoidance-qwen2.5-0.5b-instruct.json"


def test_port_gate_rejects_a_half_specified_pair(monkeypatch, capsys):
    """F2 regression: --ours alone must exit 2 with the pair guard's own INVALID
    wording, never a TypeError traceback — and never via the missing-file branch."""
    monkeypatch.setattr(sys, "argv", ["m0_port_gate.py", "--ours", EXISTING_ANCHOR])
    with pytest.raises(SystemExit) as exc:
        m0_port_gate.main()
    assert exc.value.code == 2
    assert "must be given together" in capsys.readouterr().out


def test_port_gate_rejects_all_mixed_with_a_pair_flag(monkeypatch, capsys):
    monkeypatch.setattr(
        sys, "argv", ["m0_port_gate.py", "--all", "--ours", EXISTING_ANCHOR]
    )
    with pytest.raises(SystemExit) as exc:
        m0_port_gate.main()
    assert exc.value.code == 2
    assert "must be given together" in capsys.readouterr().out


def test_port_gate_invalid_on_corrupt_json(monkeypatch, tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not json")
    monkeypatch.setattr(
        sys, "argv",
        ["m0_port_gate.py", "--ours", str(bad), "--reference", str(bad)],
    )
    with pytest.raises(SystemExit) as exc:
        m0_port_gate.main()
    assert exc.value.code == 2


def test_port_gate_invalid_on_an_unreadable_artifact(monkeypatch, capsys):
    """F10 regression: `os.path.exists` is true for a directory, so a plausible
    path typo used to die with an exit-1 IsADirectoryError traceback instead of
    the pre-committed INVALID."""
    monkeypatch.setattr(
        sys, "argv", ["m0_port_gate.py", "--ours", "anchors", "--reference", "anchors"]
    )
    with pytest.raises(SystemExit) as exc:
        m0_port_gate.main()
    assert exc.value.code == 2
    assert "could not be read as JSON" in capsys.readouterr().out


#: F11: the only two inputs that actually REACH the --all/pair mutual-exclusion
#: guard — everything else short-circuits on the half-pair guard before it.
COMPLETE_PAIR = [
    "--ours", "results/anchor-qwen2.5-0.5b-instruct.json",
    "--reference", "anchors/s4-avoidance-qwen2.5-0.5b-instruct.json",
]


@pytest.mark.parametrize(
    "argv", [[], ["--all"] + COMPLETE_PAIR], ids=["no-arguments", "all-plus-a-full-pair"]
)
def test_port_gate_rejects_neither_or_both_selection_modes(argv, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["m0_port_gate.py"] + argv)
    with pytest.raises(SystemExit) as exc:
        m0_port_gate.main()
    assert exc.value.code == 2
    assert "pass either --all or both" in capsys.readouterr().out


# --- D8: the widened configuration comparison ---------------------------------

def test_compare_pair_catches_a_softened_protocol_block():
    """D8: the fields that would catch a silently softened instrument — a
    loosened read-back tolerance, a lowered MIN_N, reworded gate — are compared."""
    ours, ref = _fake_results(), _fake_results()
    ours["protocol"]["readback_tol"] = 1e-2
    problems, _ = compare_pair(ours, ref)
    assert len(problems) == 1 and problems[0].startswith("config protocol")


def test_compare_pair_catches_a_different_lens_fit_size():
    ours, ref = _fake_results(), _fake_results()
    ours["lens_n_prompts"] = 50
    problems, _ = compare_pair(ours, ref)
    assert len(problems) == 1 and problems[0].startswith("config lens_n_prompts")


def test_compare_pair_still_allows_the_lens_path_to_differ():
    """`lens` is deliberately NOT compared: it is a path, and the two repos
    legitimately hold their copies of the same weights in different places."""
    ours, ref = _fake_results(), _fake_results()
    ours["lens"] = "/somewhere/else/qwen.pt"
    assert compare_pair(ours, ref)[0] == []


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

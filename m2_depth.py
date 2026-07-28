"""m2_depth.py — M2: localization + dose (where does the off-switch live, and how
much of the direction must be removed?).

Cut from `m1_battery.py`, which was itself cut from the certified `m0_anchor.py`
(untouched post-gate, D2/M0). The measurement machinery is unchanged — same
naming template, same chat encoding, same k = 1 J-lens projection removal with
the runtime read-back, same frozen band and thirds, same Wilson/Newcombe rulers
— so the subset's `clean` / `primed_late` / `control_late` cells must reproduce
`results/m1-battery-*.json` cell-for-cell, which this runner checks before it
reads a single new window or dose cell (D14).

What M2 adds, each frozen in `docs/M2-BRIEF.md` before any run:

- **the widened oracle (D9b)** — the primary readout is now the greedy-span
  prefix rule in `oracle.py`, shared byte-for-byte with `m1_rescore.py`. The
  first-token outcome is still computed and recorded beside every cell, so the
  M1 cross-check compares raw recorded strings and is oracle-independent.
- **a pre-registered 12-concept subset (D11a)** of M1's frozen battery, using
  M1's own 3 clues per concept verbatim — no new authoring, which is what makes
  the standing re-certification possible.
- **the three tiers, primed AND control (D12b)** — S4b's early/middle/late
  frame, now powered — plus a descriptive **sliding window** map: a window of
  the late third's own width slid at stride 2 across the whole lens range,
  anchored on the late-third start so the gate cell is a point on the map,
  with the floor (L0) and ceiling windows added when the grid misses them.
- **a dose curve (D13a)** — the same operator with only a fraction λ of the
  direction's component removed, at the late third, primed arm only.

Owned divergences from `m1_battery.py` (M2-BRIEF deviations table):

- **the partial-λ operator is new code** and lives here; `intervention.py` stays
  verbatim-ported. Full ablation (λ = 1) still runs through M1's exact path, so
  the cross-check compares like with like by construction.
- **lens vectors are precomputed once per (layer, word)** instead of rebuilt per
  item. Same device, same op, same inputs — a pure caching change, and one the
  M1 cross-check itself certifies: had it moved a value, the reused cells would
  not reproduce.
- **the degeneracy guard is re-scoped** (D14, owing PR #4 review F3): `clean` is
  the gate arm rather than a comparison arm, so it leaves the dispositive list;
  the dispositive guard pools the first tokens of an arm's **non-produced** items
  only, because under a widened oracle a high-scoring arm legitimately
  concentrates its first tokens on fragments that open correct answers.
- **`m1_battery.GATE_WORDING` is not imported or edited** — M1's wording stays
  byte-frozen with M1's artifacts. M2 freezes its own below.

Run:  uv run python -u m2_depth.py \
          --model-id Qwen/Qwen2.5-1.5B-Instruct \
          --lens lenses/qwen2.5-1.5b-instruct-n100.pt
"""
from __future__ import annotations

import argparse
import json
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
from m1_battery import ITEMS_PATH, clue_leaks, load_items, sub_band_thirds
from oracle import (
    ORACLE_WORDING,
    SPAN_TOKENS,
    says_concept_anywhere,
    says_concept_prefix,
)
from stats import excludes_zero, newcombe_diff
from subject import SubjectModel

#: D11(a): the pre-registered stratified subset, fixed the moment its rule was
#: — S1 hard-switch core (5) + S2 readout-unlocked (4) + S3 leaky switch (2) +
#: S4 non-specific anti-example (1). No discretion is exercised at run time.
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

NAMING_Q = (  # verbatim from the certified m0_anchor.py, via m1_battery.py
    'Consider this sentence: "{clue}"\n\n'
    "Which {noun} is the sentence describing? Answer with just the name."
)
TIERS = ("early", "middle", "late")
#: The cells M1 already recorded — graded FIRST, cross-checked, then the rest.
M1_SHARED_CONDITIONS = ("clean", "primed_late", "control_late")
#: D13: KICKOFF's frozen dose grid. λ = 0 is `clean` and λ = 1 is `primed_late`,
#: both already-run deterministic cells, so only the middle three are new.
DOSE_GRID = (0.0, 0.25, 0.5, 0.75, 1.0)
NEW_DOSE_LAMBDAS = (0.25, 0.5, 0.75)
WINDOW_STRIDE = 2
P_NAME_FLOOR = 0.85  # paper's verbatim naming threshold — reported, never gating
#: The stack the anchor's bit-for-bit reproduction was certified on (M0, D1).
CERTIFIED_DEVICE = "mps"
CERTIFIED_PINS = {"torch": "2.13.0", "transformers": "5.13.1"}
#: D14: the cross-check compares raw recorded strings, so it is oracle-independent.
M1_CELL_FIELDS = ("greedy", "greedy_3")

#: Every gate's wording, frozen as code before any M2 run (project guardrail:
#: "pre-commit gates as code — wording included"). Written verbatim into the
#: results JSON so prose and code can never drift. M1's own wording is NOT
#: imported: it stays byte-frozen with M1's artifacts (editing it would force a
#: full M1 re-run), and where M2 departs from it the departure is recorded here.
GATE_WORDING = {
    "oracle": ORACLE_WORDING,
    "competence": (
        "D9(b) + D6(a) item-level greedy-span naming-only gate: an item enters "
        "the gated set iff its CLEAN naming span satisfies the D9(b) oracle "
        "above. Gating is a property of the clean arm alone, decided once per "
        "item and window-independent, so every tier, window and dose cell in "
        "this run shares ONE gated set — which is what makes the curves "
        "comparable across positions. Gating is per-subject. M1's first-token "
        "gate is computed and recorded beside it as texture, never gating here. "
        "The paper-style verbatim-P rate (clean concept mass >= 0.85) is "
        "reported alongside as texture, never gating; note it is floor-pinned "
        "by construction for concepts whose emitted bare spelling has no "
        "single-token form (see the mass-channel scoping below)."
    ),
    "localization": (
        "D12(b) + D14, per subject, on the pooled gated cell: LATE-LOCALIZED "
        "iff naming under primed_early minus naming under primed_late is "
        "positive with its Newcombe 95% CI excluding 0, AND naming under "
        "primed_middle minus naming under primed_late likewise. The M2 verdict "
        "is the AND over 1.5B and 3B (computed by m2_verdict.py); 0.5B runs and "
        "is reported under its standing any-direction-damage frame and is never "
        "gate-bearing. Pooled gated n < MIN_N = 20 => pre-declared UNDERPOWERED "
        "and no localization claim. This is KICKOFF's 'late-window effect "
        "CI-cleanly exceeds early and middle' expressed in directly comparable "
        "proportions: the effect at tier T is the naming drop clean - primed_T "
        "on the same items, so effect_late - effect_T = primed_T - primed_late "
        "— the shared clean arm cancels, leaving a two-proportion comparison the "
        "ported Wilson/Newcombe ruler already decides. Rejected: a CI on the "
        "difference-of-differences itself, which needs stats machinery beyond "
        "the frozen ruler for no added honesty. Control tiers are reported "
        "beside as specificity texture; M1's breadth gate is not relitigated."
    ),
    "window_map": (
        "D12(b), descriptive — never gate-bearing. A window of the subject's "
        "own late-third width is slid at stride 2 across the full lens range "
        "L0..n_layers-2, primed arm only, with the stride grid ANCHORED on the "
        "late-third start so the gate cell is a point on every subject's map "
        "(that window IS the primed_late tier cell and is reused, not re-run). "
        "The minimum-start window (L0) and the maximum-start window (the lens "
        "ceiling) are added when the anchored grid does not already include "
        "them (reviews F8 + F11). Windows starting below the band are the "
        "outside-band probes KICKOFF's scope names; above-band coverage is "
        "structurally thin (1-2 layers) because the band's 0.92 ceiling nearly "
        "touches the lens ceiling — owned, not discovered. Stride 2 localizes "
        "any transition edge to +/-2 layers. Per-window cells carry Wilson CIs "
        "and are descriptive only."
    ),
    "dose": (
        "D13(a), descriptive — no gate, as frozen in KICKOFF. Operator: "
        "h' = h - lambda*(v_hat^T h)v_hat at every late-third layer and every "
        "position, primed arm only, over the frozen grid lambda in {0, .25, .5, "
        ".75, 1}. lambda = 0 IS the clean cell and lambda = 1 IS the primed_late "
        "cell — reused, not re-measured — so only .25/.5/.75 are new conditions. "
        "The runtime read-back generalizes with the operator: the surviving "
        "projection must equal (1-lambda) times the original within READBACK_TOL "
        "(at lambda = 1 this is exactly M1's check). Readout per lambda: the "
        "binary naming rate under the D9(b) oracle for every gated item, plus "
        "mean concept mass — the graded channel that can reveal a dimmer where "
        "the binary steps — computed ONLY over concepts whose emitted bare "
        "spelling has a single-token form (review F2). For the S2 stratum "
        "(Jupiter, Mars, piano, violin) no such form exists, so their mass is "
        "floor-pinned by construction and their dose curve is read on the "
        "binary rate alone. Owned in the deviations table."
    ),
    "degeneracy": (
        "D14, pre-committed before any M2 run; re-frozen from M1 in two ways "
        "(owing PR #4 review F3). (1) THE F3 CORRECTION: `clean` is the GATE "
        "arm, not a comparison arm — on the gated cell its answers are by "
        "construction correct openings of 12 different spellings, so no single "
        "token can approach COLLAPSE_SHARE = 0.5 on a powered cell (measured "
        "worst case on the subset's recorded clean cells: 3/28 = 0.107; "
        "full-roster worst case 3/69 = 0.043). M1's wording listing `clean` "
        "among the monitored arms was inert; it stays byte-frozen with M1's "
        "artifacts, and M2 drops `clean` from the dispositive list. (2) THE "
        "WIDE-ORACLE ADAPTATION: under D9(b) a high-scoring arm's first tokens "
        "legitimately concentrate on fragments that open CORRECT answers, so "
        "raw first-token collapse stops meaning pathology. The dispositive "
        "guard therefore pools the first tokens of the arm's NON-PRODUCED items "
        "only, with the share still computed against the full gated n — 'at "
        "least half of this arm's answers are the same WRONG opening'. The raw "
        "all-answers guard is recorded beside as texture (M1 comparability). "
        "DISPOSITION, scoped to the arms the gate actually reads (review F9): "
        "collapse in a surviving-side gate arm (primed_early, primed_middle) => "
        "DEGENERATE, no LATE-LOCALIZED claim; collapse in primed_late => TAG "
        "only (the expected mute signature); collapse in a control tier — arms "
        "the gate does not read — is a specificity-texture caveat, recorded and "
        "attached to the control-tier readouts it compromises, never dispositive "
        "over the localization verdict. Sliding-window and dose cells are "
        "descriptive, so their guards are always texture."
    ),
    "m1_crosscheck": (
        "D14, environment-scoped (carrying M1's D5a/F7 verbatim). The subset's "
        "clean / primed_late / control_late cells are graded FIRST and compared "
        "to the recorded results/m1-battery-<subject>.json cell-for-cell on the "
        "raw recorded fields (`greedy` and `greedy_3` decoded strings) BEFORE "
        "any new window or dose cell is read; `concept_mass` equality is "
        "recorded as texture, never gating. The comparison is on raw strings, "
        "so it is oracle-independent — D9 cannot soften it. On the certified "
        "environment — device 'mps' under the pinned stack (torch 2.13.0, "
        "transformers 5.13.1) — any mismatch is INVALID (exit 2). Off that "
        "environment the check still runs and is recorded but is NOT "
        "gate-bearing, and the whole run is pre-declared NOT A RESULT, which "
        "m2_verdict.py refuses. Coverage is a property of the run rather than "
        "of the environment, so the bar that all 36 subset items were actually "
        "compared is unscoped (M1 review F1's lesson)."
    ),
    "honesty": (
        "Owned, pre-committed. (1) Items within a concept share one lens "
        "direction, so item-level pooling overstates independence; the "
        "per-concept map is the honest granular view beside it. (2) The tier "
        "arms are measured on the SAME gated items, but newcombe_diff is "
        "Newcombe's method 10 for two INDEPENDENT samples — for positively "
        "correlated paired arms that WIDENS the interval, so it cannot "
        "manufacture a false LATE-LOCALIZED verdict; it can only cost power. "
        "(3) MIN_N = 20 is applied to raw n, not to an effective n discounted "
        "for that clustering. (4) NEW IN M2: the same gated items appear in "
        "every window and dose cell, so the curves are within-item correlated "
        "across positions — fine for the pairwise gate, and one more reason the "
        "map itself stays descriptive. (5) Per-concept-per-window cells are "
        "n <= 3 and are always descriptive, never verdict-bearing."
    ),
}


# --- the frozen subset --------------------------------------------------------

def load_subset_items(path: str = ITEMS_PATH) -> list[dict]:
    """M1's frozen battery, filtered to D11(a)'s 12 pre-registered concepts.

    Every guard in M1's loader runs first (roster shape, clue counts, fixed
    controls, leak test), so M2 cannot run against a drifted battery; then this
    adds the subset's own shape bars. The items are M1's, verbatim — that is the
    whole point of D11(a), and it is what makes the M1 cross-check possible.
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
    return items


# --- band arithmetic and the window grid --------------------------------------

def window_grid(late: list[int], lens_max: int, width: int) -> list[int]:
    """D12(b)'s window start positions: a stride-2 grid **anchored on the
    late-third start** so the gate cell is a point on every subject's map, plus
    the floor (L0) and ceiling windows whenever the grid misses them.

    `lens_max` is the highest layer with a lens direction (n_layers - 2), so the
    last legal start is `lens_max - width + 1`.
    """
    anchor, max_start = late[0], lens_max - width + 1
    if not 0 <= anchor <= max_start:
        fail_invalid(
            f"late-third start L{anchor} is not a legal window start for width "
            f"{width} within the lens range (max start L{max_start})"
        )
    starts = {0, max_start, anchor}  # floor + ceiling + the anchor itself
    for step in (-WINDOW_STRIDE, WINDOW_STRIDE):
        position = anchor + step
        while 0 <= position <= max_start:
            starts.add(position)
            position += step
    return sorted(starts)


def window_name(start: int, width: int) -> str:
    return f"window_L{start}-L{start + width - 1}"


def plan_conditions(thirds: dict[str, list[int]], lens_max: int) -> list[dict]:
    """Every condition this run grades, in the frozen order: the three cells M1
    already recorded first (so the cross-check fires before anything new), then
    the remaining tiers, the sliding-window map, and the dose grid.

    Each entry carries everything the grader needs — which word's direction to
    remove, which layers to remove it at, and how much of it (λ). The reused
    cells are declared here rather than re-run: the late-start window IS
    `primed_late`, and so are λ = 1 and (for λ = 0) `clean`.
    """
    late = thirds["late"]
    width = len(late)
    conditions = [
        {"name": "clean", "group": "clean", "role": None, "layers": [], "lam": 0.0},
    ]
    for tier in TIERS:
        for role in ("primed", "control"):
            conditions.append({
                "name": f"{role}_{tier}", "group": "tier", "role":
                    "concept" if role == "primed" else "control",
                "layers": thirds[tier], "lam": 1.0,
            })
    for start in window_grid(late, lens_max, width):
        layers = list(range(start, start + width))
        conditions.append({
            "name": window_name(start, width), "group": "window", "role": "concept",
            "layers": layers, "lam": 1.0,
            # The late-anchored window is the gate cell itself — reused, never re-run.
            "reused_from": "primed_late" if layers == late else None,
        })
    for lam in DOSE_GRID:
        reused = {0.0: "clean", 1.0: "primed_late"}.get(lam)
        conditions.append({
            "name": f"dose_{lam:g}", "group": "dose", "role": "concept",
            "layers": late, "lam": lam, "reused_from": reused,
        })
    # M1's three cells lead, so "before any new cell is read" is literally true.
    order = {name: i for i, name in enumerate(M1_SHARED_CONDITIONS)}
    conditions.sort(key=lambda c: order.get(c["name"], len(order)))
    return conditions


def to_run(conditions: list[dict]) -> list[dict]:
    """The conditions that actually cost forward passes — everything the plan
    does not declare as a reuse of an already-graded cell."""
    return [c for c in conditions if not c.get("reused_from")]


# --- the operators ------------------------------------------------------------

def lens_vectors(
    jacobians: dict[int, torch.Tensor],
    layers: list[int],
    rows: dict[str, torch.Tensor],
    device: str,
) -> dict[tuple[int, str], torch.Tensor]:
    """v = J_lᵀ u for every (layer, word) this run will ablate, computed once.

    M1 rebuilt these per item; M2 ablates at up to 15 window positions, so the
    same vector would otherwise be recomputed dozens of times. Same device, same
    op, same inputs — and the M1 cross-check certifies the change is inert,
    since a moved value would break bit-for-bit reproduction of the reused cells.
    Each Jacobian is moved to the device one layer at a time so the whole lens
    (up to ~570 MB at 3B) never has to be resident at once.
    """
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
    reading its direction from the precomputed table. λ = 1 conditions (every
    tier cell and every window cell) run through THIS path, not the partial one,
    so the cells M1 already recorded are reproduced by the same code that
    recorded them."""
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
                    f"M2 read-back failed at layer {layer}: surviving "
                    f"projection {worst:.2e} > {READBACK_TOL:.0e}"
                )
            return out.unsqueeze(0)

        edits[layer] = edit
    return edits


def partial_project_out(
    h: torch.Tensor, direction: torch.Tensor, lam: float
) -> torch.Tensor:
    """h − λ·(v̂ᵀh)v̂ — remove the fraction λ of the residual's component along
    one direction (D13's new operator).

    Computed in float64 on CPU, the convention `intervention.ablate` already
    uses, so that at λ = 1 this is bit-identical to the ported full-ablation
    operator (pinned by a unit test) — the dose curve's endpoint is then the
    same measurement M1 made, not merely a close one.
    """
    v = direction.cpu().to(torch.float64)
    b = h.cpu().to(torch.float64)
    unit = v / v.norm().clamp_min(torch.finfo(v.dtype).tiny)
    out = b - lam * (b * unit).sum(-1, keepdim=True) * unit
    return out.to(device=h.device, dtype=h.dtype)


def partial_ablation_edits(
    vectors: dict[tuple[int, str], torch.Tensor],
    layers: list[int],
    word: str,
    lam: float,
) -> dict[int, Edit]:
    """The dose operator with the **generalized** runtime read-back: after the
    edit, the surviving projection onto the direction must equal (1 − λ) times
    the original, within READBACK_TOL. At λ = 1 that is exactly M1's "the
    projection is zero" check; at λ = 0 it asserts the edit was a no-op."""
    edits: dict[int, Edit] = {}
    for layer in layers:
        v = vectors[(layer, word)]

        def edit(h: torch.Tensor, layer=layer, v=v, lam=lam) -> torch.Tensor:
            hs = h[0]  # [seq, d_model]
            direction = v.to(device=hs.device, dtype=torch.float32)
            out = partial_project_out(hs.float(), direction, lam).to(hs.dtype)
            unit = direction / direction.norm().clamp_min(1e-30)
            before = hs.float() @ unit
            after = out.float() @ unit
            residual = (after - (1.0 - lam) * before).abs()
            worst = float((residual / hs.float().norm(dim=-1).clamp_min(1e-30)).max())
            if worst > READBACK_TOL:
                fail_invalid(
                    f"M2 partial read-back failed at layer {layer} (λ={lam:g}): "
                    f"surviving projection is off by {worst:.2e} > {READBACK_TOL:.0e} "
                    f"relative — expected (1−λ) of the original"
                )
            return out.unsqueeze(0)

        edits[layer] = edit
    return edits


def edits_for(
    condition: dict,
    vectors: dict[tuple[int, str], torch.Tensor],
    words: dict[str, str],
) -> dict[int, Edit] | None:
    """The edit set one condition applies: none for `clean`, M1's verbatim full
    ablation at λ = 1, the new partial operator otherwise."""
    if condition["role"] is None:
        return None
    word = words[condition["role"]]
    if condition["lam"] == 1.0:
        return concept_ablation_edits(vectors, condition["layers"], word)
    return partial_ablation_edits(vectors, condition["layers"], word, condition["lam"])


# --- readouts -----------------------------------------------------------------

def greedy_continuation(
    subject: SubjectModel,
    input_ids: torch.Tensor,
    edits: dict[int, Edit] | None,
    first_id: int,
    n_tokens: int = SPAN_TOKENS,
) -> str:
    """The answer's first `n_tokens` greedy tokens, decoded — M1's secondary
    texture readout verbatim, promoted by D9(b) to the span the primary oracle
    reads. The edits are re-applied on every continuation pass, so the ablation
    stays active across the whole decoded span."""
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
    verbatim from M1 (the cross-check compares it as texture). Floor-pinned by
    construction wherever the emitted bare spelling has no single-token form,
    which is exactly why D13 scopes the mass channel (review F2)."""
    probs = torch.softmax(logits.float(), dim=-1)
    return float(sum(probs[t] for t in forms))


def bare_form_is_single_token(word: str, tokenizer) -> bool:
    """Does the spelling the model actually emits — the bare, no-leading-space
    form — have a single-token id?

    One predicate, two consequences, both owned in the M2 brief: when it is
    False the ablated direction must be keyed to the leading-space unembed row
    (review F3: the only single-token form that exists), and the concept-mass
    channel is floor-pinned so the dose curve is read on the binary rate alone
    (review F2). The 12-concept subset splits 8 True / 4 False by construction —
    the S2 stratum is the four.
    """
    return len(tokenizer(word, add_special_tokens=False).input_ids) == 1


# --- environment, validation, cross-check -------------------------------------

def certified_environment(device: str) -> tuple[bool, list[str]]:
    """Is this the stack the anchor's bit-for-bit reproduction was certified on?
    Returns (certified, reasons-it-is-not). Carried verbatim from M1."""
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


def validate(args, artifact: dict, subject: SubjectModel) -> list[int]:
    """Wrong-arm input checks (the M0/M1 gate pattern, extended to M2's own
    comparison target). Returns the band."""
    if artifact.get("model_id") != args.model_id:
        fail_invalid(
            f"lens artifact was fitted on {artifact.get('model_id')!r}, "
            f"not {args.model_id!r}"
        )
    if artifact.get("d_model") != subject.d_model:
        fail_invalid(
            f"lens d_model={artifact.get('d_model')} != subject d_model={subject.d_model}"
        )
    if sorted(artifact["J"]) != list(range(subject.n_layers - 1)):
        fail_invalid(f"lens layers != expected 0..{subject.n_layers - 2}")
    band = proportional_band(subject.n_layers)
    if band != FROZEN_BANDS.get(subject.n_layers):
        fail_invalid(
            f"proportional band {band} disagrees with frozen table "
            f"{FROZEN_BANDS.get(subject.n_layers)} for {subject.n_layers} layers"
        )
    try:
        load_subset_items()
    except (FileNotFoundError, ValueError) as exc:
        fail_invalid(str(exc))
    recorded = load_m1_run(args.m1 or m1_path_for(args.model_id), args.model_id, band)
    del recorded
    return band


def load_m1_run(path: str, model_id: str, band: list[int]) -> dict:
    """M2's comparison target. A run that was itself pre-declared not to be a
    result cannot certify anything, so it is refused here rather than silently
    cross-checked against."""
    if not os.path.exists(path):
        fail_invalid(f"M1 results {path} missing — D14's cross-check needs them")
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
    """D14: the subset's three M1-shared cells must reproduce M1's recording
    exactly on the raw decoded strings. Returns (mismatches, mass texture)."""
    reference = {r["name"]: r for r in recorded["items"]}
    mismatches: list[str] = []
    equal = total = checked = 0
    for record in records:
        theirs = reference.get(record["name"])
        if theirs is None:
            mismatches.append(f"{record['name']}: absent from the M1 recording")
            continue
        checked += 1
        for condition in M1_SHARED_CONDITIONS:
            ours, mine = record["cells"][condition], theirs["cells"][condition]
            for field in M1_CELL_FIELDS:
                if ours[field] != mine[field]:
                    mismatches.append(
                        f"{record['name']}/{condition}.{field}: "
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
    """Run `conditions` for every planned item, filling `records` in place.

    Called twice: once for M1's three shared conditions (whose cells the
    cross-check then grades), and once for everything new.
    """
    runnable = to_run(conditions)
    for i, (item, forms) in enumerate(planned):
        start = time.perf_counter()
        words = {"concept": item["concept"], "control": item["control"]}
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
            edits = edits_for(condition, vectors, words)
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
        print(
            f"[{phase} {i + 1}/{len(planned)}] {item['name']} ({item['concept']}): "
            + (
                f"clean={'OK' if record['cells']['clean']['produced'] else 'x'}"
                f"({record['cells']['clean']['greedy_3']!r}) "
                f"primed_late={'named' if record['cells']['primed_late']['produced'] else 'MUTED'} "
                f"control_late={'named' if record['cells']['control_late']['produced'] else 'muted'} "
                f"gate={'IN' if gate else 'out'}"
                if phase == "M1-shared"
                else f"gate={'IN' if gate else 'out'} "
                f"{len(runnable)} new cells"
            )
            + f" ({time.perf_counter() - start:.1f}s)"
        )
    return records


# --- the pre-committed descriptive package ------------------------------------

def hits(rows: list[dict], condition: str) -> int:
    return sum(r["cells"][condition]["produced"] for r in rows)


def descriptive_package(
    records: list[dict], conditions: list[dict], thirds: dict[str, list[int]], band: list[int]
) -> dict:
    """Everything D12–D14 pre-commit: the pooled gate, the tier cells and the
    two localization contrasts, the descriptive window map, the dose curve, and
    the per-concept view."""
    gated = [r for r in records if r["gate_span"]]
    n = len(gated)

    def cell_for(condition: dict) -> dict:
        name = condition.get("reused_from") or condition["name"]
        return rate_cell(hits(gated, name), n)

    by_name = {c["name"]: c for c in conditions}
    tier_cells = {
        name: cell_for(by_name[name])
        for name in ("clean",) + tuple(
            f"{role}_{tier}" for tier in TIERS for role in ("primed", "control")
        )
    }

    # D14's gate: the shared clean arm cancels, so the difference of drops is
    # just primed_T − primed_late, a plain two-proportion comparison.
    late_hits = tier_cells["primed_late"]["hits"]
    contrasts = {}
    for tier in ("early", "middle"):
        k_tier = tier_cells[f"primed_{tier}"]["hits"]
        diff = newcombe_diff(late_hits, n, k_tier, n) if n else (0.0, -1.0, 1.0)
        contrasts[f"newcombe_primed_{tier}_minus_primed_late_naming"] = list(diff)
        contrasts[f"primed_{tier}_exceeds_late"] = (
            diff[0] > 0 and excludes_zero(diff[1], diff[2])
        )
    holds = all(contrasts[f"primed_{t}_exceeds_late"] for t in ("early", "middle"))

    window_map = []
    for condition in (c for c in conditions if c["group"] == "window"):
        layers = condition["layers"]
        window_map.append({
            "name": condition["name"],
            "start": layers[0], "end": layers[-1], "layers": layers,
            "reused_from": condition.get("reused_from"),
            "in_band_layers": [l for l in layers if l in band],
            "outside_band": not any(l in band for l in layers),
            "is_gate_cell": condition.get("reused_from") == "primed_late",
            "cell": cell_for(condition),
        })

    mass_rows = [r for r in gated if r["mass_channel_eligible"]]
    dose_curve = []
    for condition in (c for c in conditions if c["group"] == "dose"):
        name = condition.get("reused_from") or condition["name"]
        dose_curve.append({
            "lambda": condition["lam"],
            "name": condition["name"],
            "reused_from": condition.get("reused_from"),
            "cell": cell_for(condition),
            "mean_concept_mass_eligible": (
                sum(r["cells"][name]["concept_mass"] for r in mass_rows) / len(mass_rows)
                if mass_rows else None
            ),
            "mass_channel_n": len(mass_rows),
        })

    per_concept = {}
    for record in records:
        per_concept.setdefault(record["concept"], []).append(record)
    concept_map = {}
    for concept, group in sorted(per_concept.items()):
        rows = [r for r in group if r["gate_span"]]
        concept_map[concept] = {
            "category": group[0]["category"],
            "stratum": next(
                s for s, members in SUBSET_STRATA.items() if concept in members
            ),
            "direction_key": group[0]["direction_key"],
            "mass_channel_eligible": group[0]["mass_channel_eligible"],
            "items_run": len(group),
            "gated_items": len(rows),
            **{
                name: rate_cell(hits(rows, name), len(rows))
                for name in ("primed_early", "primed_middle", "primed_late",
                             "control_early", "control_middle", "control_late")
            },
        }

    return {
        "competence": {
            "items_run": len(records),
            "gate_span": n,
            "gate_first_token_texture": sum(r["gate_first_token"] for r in records),
            "gate_verbatim_p": sum(r["gate_verbatim_p"] for r in records),
        },
        "thirds": thirds,
        "tier_cells": tier_cells,
        "localization_contrast": {
            **contrasts,
            "late_localized_shape_holds": holds,
            "underpowered": n < MIN_N,
        },
        "window_map": window_map,
        "dose_curve": dose_curve,
        "per_concept": concept_map,
    }


def wrong_opening_degeneracy(rows: list[dict], condition: str, tokenizer) -> dict:
    """D14's dispositive guard under the widened oracle: the most common first
    token among this arm's **non-produced** items, with the share taken against
    the full gated n — "at least half of this arm's answers are the same *wrong*
    opening". Under D9(b) the raw all-answers share stops meaning pathology,
    because a correct answer may legitimately open with a shared fragment."""
    missed = [r["cells"][condition]["greedy_id"] for r in rows
              if not r["cells"][condition]["produced"]]
    if not missed or not rows:
        return {"attractor_token": None, "share": 0.0, "collapsed": False,
                "non_produced": len(missed), "n_gated": len(rows)}
    token, count = Counter(missed).most_common(1)[0]
    share = count / len(rows)
    return {
        "attractor_token": tokenizer.decode([token]),
        "share": share,
        "collapsed": share >= COLLAPSE_SHARE,
        "non_produced": len(missed),
        "n_gated": len(rows),
    }


def localization_verdict(
    certified: bool,
    degenerate_arms: list[str],
    underpowered: bool,
    holds: bool,
    limit: int | None = None,
) -> str:
    """D14's frozen precedence: NOT A RESULT > DEGENERATE > UNDERPOWERED > the
    contrast. Both not-a-result conditions live here so the verdict *field* says
    so and not merely the console banner (M1 review F2)."""
    if limit is not None:
        return f"NOT A RESULT — smoke run (--limit {limit})"
    if not certified:
        return "NOT A RESULT — uncertified environment"
    if degenerate_arms:
        return (
            "DEGENERATE — no localization claim "
            f"(collapsed: {', '.join(degenerate_arms)})"
        )
    if underpowered:
        return "UNDERPOWERED — no localization claim"
    return "LATE-LOCALIZED" if holds else "not shown"


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
    print(f"loading {args.model_id} (fp32, {device})")
    hf = transformers.AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=torch.float32
    ).to(device)
    tok = transformers.AutoTokenizer.from_pretrained(args.model_id)
    subject = SubjectModel(hf, tok)

    try:
        artifact = torch.load(args.lens, map_location="cpu", weights_only=True)
    except (FileNotFoundError, OSError, RuntimeError, torch.serialization.pickle.UnpicklingError) as exc:
        fail_invalid(f"lens artifact {args.lens} could not be loaded: {exc}")
    band = validate(args, artifact, subject)
    thirds = sub_band_thirds(band)
    late = thirds["late"]
    lens_max = subject.n_layers - 2
    m1_path = args.m1 or m1_path_for(args.model_id)
    recorded = load_m1_run(m1_path, args.model_id, band)

    conditions = plan_conditions(thirds, lens_max)
    windows = [c for c in conditions if c["group"] == "window"]
    runnable = to_run(conditions)

    items = load_subset_items()
    planned, dropped = [], []
    for item in items:
        forms = {
            "concept": token_forms(item["concept"], tok),
            "control": token_forms(item["control"], tok),
            "bare_single_token": bare_form_is_single_token(item["concept"], tok),
        }
        missing = [k for k in ("concept", "control") if not forms[k]]
        if missing:
            dropped.append({"name": item["name"], "missing": missing})
        else:
            planned.append((item, forms))

    print(
        f"validated: {args.model_id} n_layers={subject.n_layers}, lens n_prompts="
        f"{artifact['n_prompts']}, band L{band[0]}–L{band[-1]} | thirds early "
        f"L{thirds['early'][0]}–L{thirds['early'][-1]}, middle L{thirds['middle'][0]}–"
        f"L{thirds['middle'][-1]}, late L{late[0]}–L{late[-1]} (width {len(late)}) | "
        f"lens range L0–L{lens_max} | windows {len(windows)} positions "
        f"({sum(1 for w in windows if w.get('reused_from'))} reused, "
        f"{sum(1 for w in windows if not any(l in band for l in w['layers']))} "
        f"fully outside the band) | conditions {len(runnable)} run of {len(conditions)} "
        f"planned | items {len(planned)} gradable / {len(dropped)} dropped | M1 "
        f"{m1_path} | environment "
        + ("CERTIFIED" if certified else "UNCERTIFIED: " + "; ".join(uncertified_reasons))
    )
    print(
        "  window starts: "
        + ", ".join(
            f"L{w['layers'][0]}" + ("*" if w.get("reused_from") else "") for w in windows
        )
        + "   (* = the late-third gate cell, reused not re-run)"
    )
    if args.dry_run:
        print("DRY-RUN: inputs valid; no trials performed")
        raise SystemExit(0)

    if args.limit is not None:
        planned = planned[: args.limit]

    unembed_rows = hf.lm_head.weight.detach()
    words = sorted({w for item, _ in planned for w in (item["concept"], item["control"])})
    rows = {w: unembed_rows[token_forms(w, tok)[0]] for w in words}
    ablated_layers = sorted({l for c in runnable for l in c["layers"]})
    vectors = lens_vectors(artifact["J"], ablated_layers, rows, device)

    shared = [c for c in conditions if c["name"] in M1_SHARED_CONDITIONS]
    rest = [c for c in conditions if c["name"] not in M1_SHARED_CONDITIONS]
    store: dict[str, dict] = {}
    grade(planned, shared, subject, vectors, store, "M1-shared")
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
            "(D14); no window or dose cell was read"
        )
    if args.limit is None and mass_texture["items_checked"] != EXPECTED_SUBSET_ITEMS:
        fail_invalid(
            f"M1 cross-check compared only {mass_texture['items_checked']} of "
            f"{EXPECTED_SUBSET_ITEMS} subset items — the frozen subset did not run "
            "as frozen, so 0 mismatches is not a re-certification (D14)"
        )
    if mismatches:
        print(
            "  ^ recorded, NOT gate-bearing: bit-for-bit reproduction is a property "
            "of the certified stack, not of the instrument (D14, scoped)"
        )

    grade(planned, rest, subject, vectors, store, "new-cells")

    package = descriptive_package(records, conditions, thirds, band)
    gated = [r for r in records if r["gate_span"]]
    n = package["competence"]["gate_span"]

    guard_wrong_opening, guard_all_answers = {}, {}
    for condition in conditions:
        name = condition.get("reused_from") or condition["name"]
        if name in guard_wrong_opening:
            continue
        guard_wrong_opening[name] = wrong_opening_degeneracy(gated, name, tok)
        guard_all_answers[name] = degeneracy(
            [r["cells"][name]["greedy_id"] for r in gated], tok
        )
    for record in records:
        for cell in record["cells"].values():
            del cell["greedy_id"]

    # D14's disposition, scoped to the arms the gate actually reads.
    dispositive = ("primed_early", "primed_middle")
    degenerate_arms = [c for c in dispositive if guard_wrong_opening[c]["collapsed"]]
    control_caveats = [
        f"control_{t}" for t in TIERS if guard_wrong_opening[f"control_{t}"]["collapsed"]
    ]
    contrast = package["localization_contrast"]
    contrast["degenerate_gate_arms"] = degenerate_arms
    contrast["primed_late_collapsed_tag"] = guard_wrong_opening["primed_late"]["collapsed"]
    contrast["control_tier_specificity_caveats"] = control_caveats
    verdict = localization_verdict(
        certified, degenerate_arms, contrast["underpowered"],
        contrast["late_localized_shape_holds"], args.limit,
    )
    contrast["verdict"] = verdict

    results = {
        "milestone": "M2",
        "model_id": args.model_id,
        "lens": args.lens,
        "lens_n_prompts": artifact["n_prompts"],
        "band": band,
        "thirds": thirds,
        "lens_range": [0, lens_max],
        "window_width": len(late),
        "window_stride": WINDOW_STRIDE,
        "mode": "gate (tiers) + descriptive (window map, dose curve)",
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
            "conditions": [
                {k: c[k] for k in ("name", "group", "role", "layers", "lam")
                 if k in c} | {"reused_from": c.get("reused_from")}
                for c in conditions
            ],
            "conditions_run": len(runnable),
            "dose_grid": list(DOSE_GRID),
            "gate": "greedy-span naming-only under D9(b); first-token recorded beside",
            "readback_tol": READBACK_TOL,
            "min_n": MIN_N,
            "collapse_share": COLLAPSE_SHARE,
            "p_name_floor": P_NAME_FLOOR,
            "span_tokens": SPAN_TOKENS,
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
    tiers = package["tier_cells"]
    early = contrast["newcombe_primed_early_minus_primed_late_naming"]
    middle = contrast["newcombe_primed_middle_minus_primed_late_naming"]
    print(
        f"\nM2 LOCALIZATION VERDICT ({args.model_id}): {smoke}gate {n}/{len(records)} "
        f"items{' UNDERPOWERED' if contrast['underpowered'] else ''} | naming "
        f"clean {tiers['clean']['hits']}/{n}, primed early {tiers['primed_early']['hits']}"
        f"/{n}, middle {tiers['primed_middle']['hits']}/{n}, late "
        f"{tiers['primed_late']['hits']}/{n} | early−late {early[0]:+.3f} "
        f"[{early[1]:+.3f},{early[2]:+.3f}], middle−late {middle[0]:+.3f} "
        f"[{middle[1]:+.3f},{middle[2]:+.3f}] → {verdict}"
    )
    print(
        "  control tiers (specificity texture): "
        + ", ".join(
            f"{t} {tiers[f'control_{t}']['hits']}/{n}" for t in TIERS
        )
        + (f" | caveats: {', '.join(control_caveats)}" if control_caveats else "")
    )
    print("  window map (descriptive, primed arm): " + " ".join(
        f"L{w['start']}–L{w['end']}"
        f"{'*' if w['is_gate_cell'] else ('°' if w['outside_band'] else '')}"
        f"={w['cell']['hits']}/{n}"
        for w in package["window_map"]
    ) + "   (* gate cell, ° fully outside the band)")
    print("  dose curve (descriptive, primed arm at the late third): " + " ".join(
        f"λ={d['lambda']:g}:{d['cell']['hits']}/{n}"
        + (f"(mass {d['mean_concept_mass_eligible']:.3f})"
           if d["mean_concept_mass_eligible"] is not None else "")
        for d in package["dose_curve"]
    ) + f"   [mass channel scoped to {package['dose_curve'][0]['mass_channel_n']} "
        f"gated items whose bare spelling is single-token]")

    if args.limit and not args.out:
        print("smoke run: results not written (pass --out to keep them)")
        raise SystemExit(0)
    out = args.out or ("results/m2-depth-" + args.model_id.split("/")[-1].lower() + ".json")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w") as f:
        json.dump(results, f, indent=1)
    print(f"results written to {out}")
    raise SystemExit(0)


if __name__ == "__main__":
    main()

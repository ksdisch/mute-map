"""m1_battery.py — M1: the breadth battery (is the late-band off-switch general?).

Cut from the certified `m0_anchor.py` (which stays untouched post-gate, D2/M0),
not shared with it. The measurement machinery is identical — same naming
template, same chat encoding, same k = 1 J-lens projection removal with the
runtime read-back, same frozen band and thirds, same greedy grading, same
Wilson/Newcombe rulers — so the 60 reused S4 items must reproduce the recorded
anchors bit-for-bit, which this runner checks before it reads a single new cell.

Owned divergences from `m0_anchor.py` (M1-BRIEF deviations table):

- **naming only** (K2): S4b's avoidance instruction is dropped, so the
  competence gate is naming-only (D6a). `gate_verbatim_p` therefore keeps only
  the naming half of the paper's threshold pair — texture, never gating.
- **late tier only** (D28's early/middle tiers are M2's job): conditions are
  `clean`, `primed_late`, `control_late`.
- **180 items over 60 concepts** in 10 categories of 6 (D4b), 3 clues each
  (D5a), frozen in `items/m1-battery.json`; 60 of them are S4's own items
  reused verbatim.
- **`MIN_N` / `COLLAPSE_SHARE` are imported from `harness`**, not re-bound
  locally, so the recorded protocol block and the applied thresholds cannot
  drift apart (PR #2 review F7).
- **the loader's leak guard is stricter**: S4's substring test is replaced by a
  word-prefix test plus the frozen `forbidden_forms` list, which catches
  suffixed derivatives ("lions") and root-changing ones ("French") that a bare
  substring test misses, without the false positives a substring test produces
  on short concepts ("ant" in "plant"). Every reused S4 item passes it unchanged.

Every gate's wording is frozen in `GATE_WORDING` below, as code, before any run.

Run:  uv run python -u m1_battery.py \
          --model-id Qwen/Qwen2.5-1.5B-Instruct \
          --lens lenses/qwen2.5-1.5b-instruct-n100.pt
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time

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
from stats import excludes_zero, newcombe_diff
from subject import SubjectModel

ITEMS_PATH = "items/m1-battery.json"
EXPECTED_ITEMS = 180  # 60 concepts x 3 clues, frozen 2026-07-28 (D4b + D5a)
EXPECTED_CONCEPTS = 60
EXPECTED_CATEGORIES = 10
CONCEPTS_PER_CATEGORY = 6
CLUES_PER_CONCEPT = 3
REUSED_ITEMS = 60  # the S4 items carried over verbatim — the cross-check set
NAMING_Q = (  # verbatim from the certified m0_anchor.py
    'Consider this sentence: "{clue}"\n\n'
    "Which {noun} is the sentence describing? Answer with just the name."
)
CONDITIONS = ("clean", "primed_late", "control_late")
P_NAME_FLOOR = 0.85  # paper's verbatim naming threshold — reported, not gating
GREEDY_TEXTURE_TOKENS = 3  # CLAUDE.md's secondary texture readout — never gating
#: The stack the anchor's bit-for-bit reproduction was certified on (M0, D1).
CERTIFIED_DEVICE = "mps"
CERTIFIED_PINS = {"torch": "2.13.0", "transformers": "5.13.1"}
#: D3's gating cell fields — the deterministic greedy outcome.
ANCHOR_CELL_FIELDS = ("produced", "greedy")

#: Every gate's wording, frozen as code before any M1 run (project guardrail:
#: "pre-commit gates as code — wording included"). Written verbatim into the
#: results JSON so prose and code can never drift.
GATE_WORDING = {
    "competence": (
        "D6(a) item-level greedy naming-only gate: an item enters the gated set "
        "iff its clean naming greedy first token is one of the concept's "
        "single-token forms — S4's D29 greedy gate minus the avoidance half "
        "(K2). Gating is per-subject. The paper-style verbatim-P rate (clean "
        "concept mass >= 0.85, naming half only) is reported alongside as "
        "texture, never gating. S4's 'The ...' miss-counting caveat is kept, "
        "owned, for anchor comparability — and the first-3-greedy continuation "
        "is recorded beside every cell (CLAUDE.md's standing secondary texture "
        "readout) so the caveat's cost can be measured rather than assumed: it "
        "separates an item the model got wrong from one it got right while "
        "opening with a fragment of the word, and on the ablated arms it "
        "distinguishes 'stopped saying the word' from 'stopped starting with "
        "it'. It never gates and never enters a verdict."
    ),
    "breadth": (
        "D7(a): per subject, on the pooled gated cell, BREADTH-SPECIFIC iff "
        "naming success under control_late minus naming success under "
        "primed_late is positive AND its Newcombe 95% CI excludes 0. The M1 "
        "verdict is the AND over 1.5B and 3B (computed by m1_verdict.py); 0.5B "
        "runs and is reported under its standing any-direction-damage frame "
        "(pre-declared risk 2) and is never gate-bearing. Pooled n < MIN_N = 20 "
        "=> pre-declared UNDERPOWERED and no breadth claim."
    ),
    "prevalence": (
        "D7(a) with the fixed denominator (amended pre-run at reviews F1 and F9 "
        "of PR #3, Kyle-approved): only concepts with ALL 3 items gated count, "
        "and of those, the number showing the hard-switch profile (primed_late "
        "naming 0/3 AND control_late naming 3/3) is reported with its Wilson CI "
        "over that fixed set, carrying the pre-declared UNDERPOWERED tag "
        "whenever the set holds fewer than MIN_N = 20 concepts — the expected "
        "case, since the anchor data projects ~15-18 all-3-gated concepts of "
        "60. The fixed set is per-subject; no cross-subject prevalence "
        "comparison is gated or claimed (the intersection is reported beside as "
        "texture by m1_verdict.py). Concepts with 1 or 2 gated items are "
        "reported beside, stratified by gated-item count, never pooled into the "
        "headline — a 1-gated-item concept satisfies the profile trivially, and "
        "sparse gating tracks marginal competence. No per-concept verdicts."
    ),
    "degeneracy": (
        "Pre-committed before any M1 run (PR #3 review F5). The degeneracy "
        "guard is read on the GATED cell, which is the cell the verdict is "
        "computed on. Collapse (most-common greedy token's share >= "
        "COLLAPSE_SHARE = 0.5) in clean or control_late — the two comparison "
        "arms the verdict rests on — is pre-declared DEGENERATE: the contrast "
        "is still reported, but no BREADTH-SPECIFIC claim is made. Collapse in "
        "primed_late is a TAG only and the verdict stands: a shared attractor "
        "under the concept's own ablation is the expected signature of the "
        "switch (the answer is destroyed and what remains is the model's "
        "fallback), not evidence against specificity. On the recorded anchor "
        "data this disposition fires on neither gate-bearing subject (gated "
        "attractor shares at 1.5B: clean .136, primed_late .364, control_late "
        ".136; at 3B: .375 / .375 / .375)."
    ),
    "anchor_crosscheck": (
        "D5(a), environment-scoped (PR #3 review F7). The 60 reused S4 items "
        "are graded FIRST and compared to the recorded anchor JSON cell-for-cell "
        "on (produced, greedy) for clean / primed_late / control_late BEFORE any "
        "new-concept cell is read. On the certified environment — device 'mps' "
        "under the pinned stack (torch 2.13.0, transformers 5.13.1) — any "
        "mismatch is INVALID (exit 2): bit-for-bit greedy reproduction is the "
        "expectation there, so a deviation is a real defect in the instrument. "
        "Off that environment, bit-for-bit reproduction is a property of the "
        "stack rather than of the instrument, so the cross-check still runs and "
        "is recorded but is NOT gate-bearing, and the whole run is pre-declared "
        "NOT A RESULT. concept_mass equality is texture either way, never "
        "gating (D3's convention)."
    ),
    "honesty": (
        "Owned, pre-committed. (1) Items within a concept share one lens "
        "direction, so item-level pooling overstates independence; S4b pooled "
        "the same way, and the per-concept map is the honest granular view "
        "beside it. (2) primed_late and control_late are measured on the SAME "
        "gated items, but newcombe_diff is Newcombe's method 10 for two "
        "INDEPENDENT samples — for positively correlated paired arms that "
        "WIDENS the interval, so it cannot manufacture a false BREADTH-SPECIFIC "
        "verdict; it can only cost power. (3) MIN_N = 20 is applied to raw n, "
        "not to an effective n discounted for that clustering. (4) The "
        "prevalence set's fixed denominator is anti-monotone in items per "
        "concept: writing more clues per concept would SHRINK it, so its power "
        "can only be raised by widening the roster, never by adding clues."
    ),
}


def load_items(path: str = ITEMS_PATH) -> list[dict]:
    """The frozen M1 battery, guarded against drift and clue leakage.

    Same job as `m0_anchor.load_items`, widened to the battery's shape (roster,
    per-concept clue count, fixed controls) and to the stricter leak test the
    60-concept roster needs — see the module docstring.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} missing — the frozen M1 battery")
    battery = json.load(open(path))
    for block in ("construction_rules", "roster", "forbidden_forms", "items"):
        if block not in battery:
            raise ValueError(f"{path} is missing its {block!r} block")
    roster, forbidden = battery["roster"], battery["forbidden_forms"]
    items = battery["items"]
    fields = ("name", "category", "noun", "concept", "control", "clue", "source")
    if len(items) != EXPECTED_ITEMS or any(
        not all(f in item for f in fields) for item in items
    ):
        raise ValueError(
            f"{path} drifted from the frozen {EXPECTED_ITEMS}-item shape — "
            "re-freeze before running"
        )
    if len(roster) != EXPECTED_CATEGORIES or any(
        len(cs) != CONCEPTS_PER_CATEGORY for cs in roster.values()
    ):
        raise ValueError(
            f"{path} roster drifted from the frozen {EXPECTED_CATEGORIES} x "
            f"{CONCEPTS_PER_CATEGORY} shape"
        )
    if len({i["name"] for i in items}) != EXPECTED_ITEMS:
        raise ValueError(f"{path} has duplicate item names")
    if sum(i["source"] == "s4-reuse" for i in items) != REUSED_ITEMS:
        raise ValueError(
            f"{path} does not carry exactly {REUSED_ITEMS} reused S4 items — "
            "the anchor cross-check set"
        )

    by_concept: dict[str, list[dict]] = {}
    for item in items:
        by_concept.setdefault(item["concept"], []).append(item)
    if len(by_concept) != EXPECTED_CONCEPTS:
        raise ValueError(
            f"{path} covers {len(by_concept)} concepts, expected {EXPECTED_CONCEPTS}"
        )
    for concept, group in by_concept.items():
        if len(group) != CLUES_PER_CONCEPT:
            raise ValueError(
                f"concept {concept}: {len(group)} clues, expected {CLUES_PER_CONCEPT}"
            )
        if len({i["control"] for i in group}) != 1:
            raise ValueError(f"concept {concept}: control is not fixed across its clues")

    for item in items:
        if item["category"] not in roster:
            raise ValueError(f"item {item['name']}: category not in the roster")
        for role in ("concept", "control"):
            if item[role] not in roster[item["category"]]:
                raise ValueError(
                    f"item {item['name']}: {role} {item[role]!r} is not in its "
                    "own category's roster list"
                )
        if item["concept"] == item["control"]:
            raise ValueError(f"item {item['name']}: control equals concept")
        for leak in clue_leaks(item, forbidden):
            raise ValueError(
                f"item {item['name']}: clue leaks — {leak} — violates the frozen "
                "construction rules"
            )
    return items


def clue_leaks(item: dict, forbidden_forms: dict[str, list[str]]) -> list[str]:
    """The frozen leak test: no word of the clue may start with the concept or
    control string, nor with any frozen root-changing derivative of either."""
    blocked = []
    for word in (item["concept"], item["control"]):
        blocked.append(word.lower())
        blocked.extend(f.lower() for f in forbidden_forms.get(word, []))
    return [
        f"{w!r} starts with {b!r}"
        for w in re.findall(r"[a-z']+", item["clue"].lower())
        for b in blocked
        if w.startswith(b)
    ]


def sub_band_thirds(band: list[int]) -> dict[str, list[int]]:
    """S1's early/middle/late thirds of the frozen band (D28). M1 ablates only
    `late`; the full split is recorded so the band arithmetic stays auditable
    and identical to the anchor's."""
    n = len(band)
    third = max(1, n // 3)
    return {
        "early": band[:third],
        "middle": band[third : 2 * third],
        "late": band[2 * third :],
    }


def concept_ablation_edits(
    jacobians: dict[int, torch.Tensor], layers: list[int], u_row: torch.Tensor
) -> dict[int, Edit]:
    """k = 1 edits: project the one concept direction (layer's own J_l, M1 raw-
    row convention) out of every position, with the D6-style read-back."""
    edits: dict[int, Edit] = {}
    for layer in layers:
        v = jlens_vector(jacobians[layer], u_row.float())

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
                    f"M1 read-back failed at layer {layer}: surviving "
                    f"projection {worst:.2e} > {READBACK_TOL:.0e}"
                )
            return out.unsqueeze(0)

        edits[layer] = edit
    return edits


def order_reused_first(
    planned: list[tuple[dict, dict]]
) -> tuple[list[tuple[dict, dict]], list[tuple[dict, dict]]]:
    """D5(a) + PR #3 review F7: the reused S4 items are graded before any new
    concept, so the anchor cross-check can fire *before any new cell is read*.
    Order within each group is preserved."""
    reused = [p for p in planned if p[0]["source"] == "s4-reuse"]
    fresh = [p for p in planned if p[0]["source"] != "s4-reuse"]
    return reused, fresh


def anchor_path_for(model_id: str) -> str:
    return "anchors/s4-avoidance-" + model_id.split("/")[-1].lower() + ".json"


def certified_environment(device: str) -> tuple[bool, list[str]]:
    """Is this the stack the anchor's bit-for-bit reproduction was certified on?
    Returns (certified, reasons-it-is-not)."""
    reasons = []
    if device != CERTIFIED_DEVICE:
        reasons.append(f"device {device!r} != {CERTIFIED_DEVICE!r}")
    for module, pin in ((torch, "torch"), (transformers, "transformers")):
        actual = module.__version__
        if actual != CERTIFIED_PINS[pin]:
            reasons.append(f"{pin} {actual} != pinned {CERTIFIED_PINS[pin]}")
    return (not reasons), reasons


def validate(args, artifact: dict, subject: SubjectModel) -> list[int]:
    """Wrong-arm input checks (the M0 gate pattern, kept). Returns the band."""
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
        load_items()
    except (FileNotFoundError, ValueError) as exc:
        fail_invalid(str(exc))
    anchor = args.anchor or anchor_path_for(args.model_id)
    if not os.path.exists(anchor):
        fail_invalid(f"anchor recording {anchor} missing — D5(a) needs it to cross-check")
    recorded = json.load(open(anchor))
    if recorded.get("model_id") != args.model_id:
        fail_invalid(
            f"anchor recording {anchor} is for {recorded.get('model_id')!r}, "
            f"not {args.model_id!r}"
        )
    if recorded.get("band") != band:
        fail_invalid(
            f"anchor recording {anchor} was run on band {recorded.get('band')}, "
            f"not {band}"
        )
    return band


def greedy_continuation(
    subject: SubjectModel,
    input_ids: torch.Tensor,
    edits: dict[int, Edit] | None,
    first_id: int,
    n_tokens: int = GREEDY_TEXTURE_TOKENS,
) -> str:
    """The answer's first `n_tokens` greedy tokens, decoded — the project's
    standing **secondary texture** readout (CLAUDE.md: "first-3-greedy recorded
    as secondary texture"). Never gating, never part of any verdict.

    It exists to separate two things the single-token primary readout cannot
    tell apart: an item the model got *wrong*, and an item the model got right
    whose first token is only a fragment of the word (`'Mer'` for Mercury —
    which happens whenever a concept's bare, no-leading-space spelling is
    multi-token, the general form of S4's owned "The …" miss-counting caveat).
    Applied to the ablated arms it answers the mirror question: when the primary
    readout says MUTED, did the model stop saying the word, or merely stop
    starting with it?

    The edits are re-applied on every continuation pass, so the ablation stays
    active across the whole decoded span.
    """
    ids = [first_id]
    sequence = input_ids
    for _ in range(n_tokens - 1):
        sequence = torch.cat(
            [sequence, torch.tensor([[ids[-1]]], device=sequence.device)], dim=1
        )
        ids.append(int(output_logits(subject, sequence, edits).argmax()))
    return subject.tokenizer.decode(ids)


def says_concept(text: str, concept: str) -> bool:
    """Did the decoded span contain the concept word at all? Texture only."""
    return concept.lower() in text.lower()


def concept_mass(logits: torch.Tensor, forms: list[int]) -> float:
    """Softmax probability mass on the concept's single-token forms — the
    paper-comparable texture readout (their gate thresholds are probabilities)."""
    probs = torch.softmax(logits.float(), dim=-1)
    return float(sum(probs[t] for t in forms))


def anchor_crosscheck(records: list[dict], anchor_path: str) -> tuple[list[str], dict]:
    """D5(a): the reused S4 items must reproduce the recorded anchor's naming
    cells exactly. Returns (mismatches, mass texture)."""
    recorded = {r["name"]: r for r in json.load(open(anchor_path))["items"]}
    mismatches: list[str] = []
    equal = total = 0
    checked = 0
    for record in records:
        if record["source"] != "s4-reuse":
            continue
        reference = recorded.get(record["name"])
        if reference is None:
            mismatches.append(f"{record['name']}: absent from the anchor recording")
            continue
        checked += 1
        for condition in CONDITIONS:
            ours = record["cells"][condition]
            theirs = reference["instructions"]["naming"][condition]
            for field in ANCHOR_CELL_FIELDS:
                if ours[field] != theirs[field]:
                    mismatches.append(
                        f"{record['name']}/{condition}.{field}: "
                        f"{ours[field]!r} != anchor {theirs[field]!r}"
                    )
            total += 1
            equal += ours["concept_mass"] == theirs["concept_mass"]
    return mismatches, {
        "items_checked": checked,
        "items_expected": REUSED_ITEMS,
        "cells_checked": total,
        "cells_expected": REUSED_ITEMS * len(CONDITIONS),
        "mass_cells_equal": equal,
    }


def grade(
    planned: list[tuple[dict, dict]],
    subject: SubjectModel,
    jacobians: dict[int, torch.Tensor],
    late: list[int],
    unembed_rows: torch.Tensor,
    offset: int,
    total: int,
) -> list[dict]:
    """Run every condition for each planned item and record its cells."""
    records = []
    for i, (item, forms) in enumerate(planned):
        start = time.perf_counter()
        u_concept = unembed_rows[forms["concept"][0]]  # bare form — M1 convention
        u_control = unembed_rows[forms["control"][0]]
        prompt = NAMING_Q.format(clue=item["clue"], noun=item["noun"])
        input_ids = encode_chat(subject, prompt)
        cells = {}
        for condition in CONDITIONS:
            if condition == "clean":
                edits = None
            else:
                kind, _tier = condition.split("_")
                u_row = u_control if kind == "control" else u_concept
                edits = concept_ablation_edits(jacobians, late, u_row)
            logits = output_logits(subject, input_ids, edits)
            greedy = int(logits.argmax())
            greedy_3 = greedy_continuation(subject, input_ids, edits, greedy)
            cells[condition] = {
                "produced": greedy in forms["concept"],
                "greedy": subject.tokenizer.decode([greedy]),
                "greedy_id": greedy,
                "concept_mass": concept_mass(logits, forms["concept"]),
                # secondary texture only — never gating, never in a verdict
                "greedy_3": greedy_3,
                "says_concept_in_3": says_concept(greedy_3, item["concept"]),
            }
        record = {
            "name": item["name"],
            "category": item["category"],
            "concept": item["concept"],
            "control": item["control"],
            "source": item["source"],
            "cells": cells,
            "gate_greedy": cells["clean"]["produced"],  # D6(a): naming only
            "gate_verbatim_p": cells["clean"]["concept_mass"] >= P_NAME_FLOOR,
        }
        records.append(record)
        print(
            f"[{offset + i + 1}/{total}] {item['name']} ({item['source']}): "
            f"clean={'OK' if cells['clean']['produced'] else 'x'}"
            f"({cells['clean']['greedy']!r}) "
            f"primed={'named' if cells['primed_late']['produced'] else 'MUTED'} "
            f"control={'named' if cells['control_late']['produced'] else 'muted'} "
            f"gate={'IN' if record['gate_greedy'] else 'out'} "
            f"({time.perf_counter() - start:.1f}s)"
        )
    return records


def descriptive_package(records: list[dict]) -> dict:
    """Everything D7(a) pre-commits: the pooled gate, the per-concept and
    per-category maps, and the fixed-denominator prevalence texture."""
    gated = [r for r in records if r["gate_greedy"]]
    n = len(gated)

    def hits(rows: list[dict], condition: str) -> int:
        return sum(r["cells"][condition]["produced"] for r in rows)

    naming_success = {c: rate_cell(hits(gated, c), n) for c in CONDITIONS}
    k_primed = naming_success["primed_late"]["hits"]
    k_control = naming_success["control_late"]["hits"]
    diff = newcombe_diff(k_primed, n, k_control, n) if n else (0.0, -1.0, 1.0)

    per_concept, per_category = {}, {}
    for record in records:
        per_concept.setdefault(record["concept"], []).append(record)
        per_category.setdefault(record["category"], []).append(record)

    concept_map = {}
    for concept, group in sorted(per_concept.items()):
        rows = [r for r in group if r["gate_greedy"]]
        concept_map[concept] = {
            "category": group[0]["category"],
            "items_run": len(group),
            "gated_items": len(rows),
            **{
                c: rate_cell(hits(rows, c), len(rows))
                for c in ("primed_late", "control_late")
            },
        }
    category_map = {}
    for category, group in sorted(per_category.items()):
        rows = [r for r in group if r["gate_greedy"]]
        m = len(rows)
        cat_diff = (
            newcombe_diff(hits(rows, "primed_late"), m, hits(rows, "control_late"), m)
            if m
            else (0.0, -1.0, 1.0)
        )
        category_map[category] = {
            "items_run": len(group),
            "gated_items": m,
            **{c: rate_cell(hits(rows, c), m) for c in CONDITIONS},
            "newcombe_control_minus_primed_late": list(cat_diff),
        }

    # Prevalence, fixed denominator: only all-3-gated concepts count.
    fixed, hard, partial = [], [], {}
    for concept, entry in concept_map.items():
        rows = [r for r in per_concept[concept] if r["gate_greedy"]]
        g = len(rows)
        if g == 0:
            continue
        profile = hits(rows, "primed_late") == 0 and hits(rows, "control_late") == g
        if g == CLUES_PER_CONCEPT:
            fixed.append(concept)
            if profile:
                hard.append(concept)
        else:
            bucket = partial.setdefault(
                str(g), {"concepts": [], "profile_at_own_denominator": []}
            )
            bucket["concepts"].append(concept)
            if profile:
                bucket["profile_at_own_denominator"].append(concept)

    # Secondary texture (CLAUDE.md's first-3-greedy readout), never gating: how
    # much of the competence gate's attrition is the model being wrong, versus
    # the model being right but opening with a fragment of the word — and,
    # on the ablated arms, whether "muted" means it stopped saying the word.
    ungated = [r for r in records if not r["gate_greedy"]]
    texture = {
        "clean_says_concept_in_3_all_items": sum(
            r["cells"]["clean"]["says_concept_in_3"] for r in records
        ),
        "ungated_but_says_concept_in_3": sum(
            r["cells"]["clean"]["says_concept_in_3"] for r in ungated
        ),
        "ungated_items": len(ungated),
        **{
            f"gated_{c}_says_concept_in_3": sum(
                r["cells"][c]["says_concept_in_3"] for r in gated
            )
            for c in CONDITIONS
        },
    }

    return {
        "competence": {
            "items_run": len(records),
            "gate_greedy": n,
            "gate_verbatim_p": sum(r["gate_verbatim_p"] for r in records),
        },
        "greedy_3_texture": texture,
        "naming_success_gated": naming_success,
        "breadth_contrast": {
            "newcombe_control_minus_primed_late_naming": list(diff),
            "positive_and_ci_excludes_zero": excludes_zero(diff[1], diff[2]) and diff[0] > 0,
            "underpowered": n < MIN_N,
        },
        "per_concept": concept_map,
        "per_category": category_map,
        "prevalence": {
            "fixed_denominator_concepts": sorted(fixed),
            "hard_switch_concepts": sorted(hard),
            "cell": rate_cell(len(hard), len(fixed)),
            "partial_gated_concepts_stratified": partial,
        },
    }


def breadth_verdict(
    certified: bool,
    degenerate_arms: list[str],
    underpowered: bool,
    holds: bool,
    limit: int | None = None,
) -> str:
    """The pre-committed verdict resolution, in its frozen precedence order: a
    run that is not a result outranks a degenerate comparison arm, which
    outranks too little data, which outranks the contrast itself.

    The project pre-declares **two** not-a-result conditions, and both belong
    here so the verdict *field* says so and not merely the console banner
    (review F2): an uncertified environment, and a `--limit` smoke run
    (CLAUDE.md: "`--limit` is smoke, never a result").
    """
    if limit is not None:
        return f"NOT A RESULT — smoke run (--limit {limit})"
    if not certified:
        return "NOT A RESULT — uncertified environment"
    if degenerate_arms:
        return f"DEGENERATE — no breadth claim (collapsed: {', '.join(degenerate_arms)})"
    if underpowered:
        return "UNDERPOWERED — no breadth claim"
    return "BREADTH-SPECIFIC" if holds else "not shown"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-id", required=True)
    parser.add_argument("--lens", required=True, help="fitted lens artifact (*.pt)")
    parser.add_argument("--anchor", default=None, help="recorded S4b JSON to cross-check against")
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
    except FileNotFoundError:
        fail_invalid(f"lens artifact {args.lens} not found")
    band = validate(args, artifact, subject)
    thirds = sub_band_thirds(band)
    late = thirds["late"]
    anchor = args.anchor or anchor_path_for(args.model_id)

    items = load_items()
    planned, dropped = [], []
    for item in items:
        forms = {
            "concept": token_forms(item["concept"], tok),
            "control": token_forms(item["control"], tok),
        }
        missing = [k for k, v in forms.items() if not v]
        if missing:
            dropped.append({"name": item["name"], "missing": missing})
        else:
            planned.append((item, forms))
    reused, fresh = order_reused_first(planned)
    ordered = reused + fresh

    print(
        f"validated: {args.model_id} n_layers={subject.n_layers}, lens n_prompts="
        f"{artifact['n_prompts']}, band L{band[0]}–L{band[-1]} | late third "
        f"L{late[0]}–L{late[-1]} | items {len(planned)} gradable "
        f"({len(reused)} reused first, then {len(fresh)} new) / {len(dropped)} dropped"
        f" | anchor {anchor} | environment "
        + ("CERTIFIED" if certified else "UNCERTIFIED: " + "; ".join(uncertified_reasons))
    )
    if args.dry_run:
        print("DRY-RUN: inputs valid; no trials performed")
        raise SystemExit(0)

    jacobians = {l: artifact["J"][l].to(device) for l in band}
    unembed_rows = hf.lm_head.weight.detach()
    if args.limit is not None:
        ordered = ordered[: args.limit]
        reused, fresh = order_reused_first(ordered)

    records = grade(reused, subject, jacobians, late, unembed_rows, 0, len(ordered))
    mismatches, mass_texture = anchor_crosscheck(records, anchor)
    crosscheck = {
        "anchor": anchor,
        "gate_bearing": certified,
        "mismatches": mismatches[:20],
        "n_mismatches": len(mismatches),
        **mass_texture,
    }
    verdict_word = "PASS" if not mismatches else "MISMATCH"
    print(
        f"\nANCHOR CROSS-CHECK: {verdict_word} — {len(mismatches)} mismatches over "
        f"{mass_texture['cells_checked']} reused cells "
        f"({mass_texture['items_checked']} items × {len(CONDITIONS)} conditions) | "
        f"concept_mass exact {mass_texture['mass_cells_equal']}/"
        f"{mass_texture['cells_checked']} | "
        + ("GATE-BEARING (certified environment)" if certified
           else "not gate-bearing (uncertified environment)")
    )
    for problem in mismatches[:20]:
        print(f"  {problem}")
    if mismatches and certified:
        fail_invalid(
            f"{len(mismatches)} reused-item cells disagree with the recorded anchor "
            f"{anchor} on the certified environment — the instrument drifted (D5a); "
            "no new-concept cell was read"
        )
    # Review F1: "0 mismatches" is only a re-certification if all 60 reused items
    # were actually compared. An item lost to the single-token prefilter never
    # reaches `records`, so it is invisible to the cell walk above — exactly the
    # tokenizer/version drift D5(a) exists to catch. Coverage is a property of the
    # run, not of the environment, so this bar is unscoped.
    if args.limit is None and mass_texture["items_checked"] != REUSED_ITEMS:
        fail_invalid(
            f"anchor cross-check compared only {mass_texture['items_checked']} of "
            f"{REUSED_ITEMS} reused items ({len(dropped)} item(s) dropped by the "
            "single-token prefilter) — the frozen battery did not run as frozen, "
            "so 0 mismatches is not a re-certification (D5a)"
        )
    if mismatches:
        print(
            "  ^ recorded, NOT gate-bearing: bit-for-bit reproduction is a property "
            "of the certified stack, not of the instrument (D5a, scoped)"
        )

    records += grade(
        fresh, subject, jacobians, late, unembed_rows, len(records), len(ordered)
    )

    package = descriptive_package(records)
    gated = [r for r in records if r["gate_greedy"]]
    n = package["competence"]["gate_greedy"]

    guard_all, guard_gated = {}, {}
    for condition in CONDITIONS:
        guard_all[condition] = degeneracy(
            [r["cells"][condition]["greedy_id"] for r in records], tok
        )
        guard_gated[condition] = degeneracy(
            [r["cells"][condition]["greedy_id"] for r in gated], tok
        )
    for record in records:
        for cell in record["cells"].values():
            del cell["greedy_id"]

    # The pre-committed degeneracy disposition, read on the gated cell.
    degenerate_arms = [
        c for c in ("clean", "control_late") if guard_gated[c]["collapsed"]
    ]
    contrast = package["breadth_contrast"]
    contrast["degenerate_comparison_arms"] = degenerate_arms
    contrast["primed_late_collapsed_tag"] = guard_gated["primed_late"]["collapsed"]
    verdict = breadth_verdict(
        certified,
        degenerate_arms,
        contrast["underpowered"],
        contrast["positive_and_ci_excludes_zero"],
        args.limit,
    )
    contrast["verdict"] = verdict

    mass = {
        c: (sum(r["cells"][c]["concept_mass"] for r in gated) / n if n else None)
        for c in CONDITIONS
    }

    results = {
        "milestone": "M1",
        "model_id": args.model_id,
        "lens": args.lens,
        "lens_n_prompts": artifact["n_prompts"],
        "band": band,
        "thirds": thirds,
        "ablated_layers": late,
        "mode": "descriptive",
        "environment": {
            "device": device,
            "torch": torch.__version__,
            "transformers": transformers.__version__,
            "certified": certified,
            "uncertified_reasons": uncertified_reasons,
        },
        "protocol": {
            "instructions": {"naming": NAMING_Q},
            "conditions": list(CONDITIONS),
            "gate": "greedy naming-only (D6a); verbatim P .85 reported alongside",
            "readback_tol": READBACK_TOL,
            "min_n": MIN_N,
            "collapse_share": COLLAPSE_SHARE,
            "p_name_floor": P_NAME_FLOOR,
            "greedy_texture_tokens": GREEDY_TEXTURE_TOKENS,
            "items": ITEMS_PATH,
            "gate_wording": GATE_WORDING,
        },
        "dropped_single_token_prefilter": dropped,
        "anchor_crosscheck": crosscheck,
        "smoke_limit": args.limit,
        **package,
        "mean_concept_mass_gated": mass,
        "degeneracy_guard": guard_all,
        "degeneracy_guard_gated": guard_gated,
        "items": records,
    }

    smoke = f"SMOKE (limit={args.limit}) — not a result — " if args.limit else ""
    diff = contrast["newcombe_control_minus_primed_late_naming"]
    prevalence = package["prevalence"]
    collapsed = [c for c, g in guard_gated.items() if g["collapsed"]]
    print(
        f"\nM1 BREADTH VERDICT ({args.model_id}): {smoke}gate {n}/{len(records)} items"
        f"{' UNDERPOWERED' if contrast['underpowered'] else ''} (verbatim-P would keep "
        f"{package['competence']['gate_verbatim_p']}) | naming clean "
        f"{package['naming_success_gated']['clean']['hits']}/{n}, primed_late "
        f"{package['naming_success_gated']['primed_late']['hits']}/{n}, control_late "
        f"{package['naming_success_gated']['control_late']['hits']}/{n} | "
        f"control−primed {diff[0]:+.3f} [{diff[1]:+.3f},{diff[2]:+.3f}] → {verdict} | "
        f"prevalence (fixed denominator) {prevalence['cell']['hits']}/"
        f"{prevalence['cell']['n']} concepts show the hard-switch profile"
        f"{' UNDERPOWERED' if prevalence['cell']['underpowered'] else ''} | "
        f"degeneracy (gated): {', '.join(collapsed) if collapsed else 'none'}"
    )
    texture = package["greedy_3_texture"]
    print(
        f"  texture (first-{GREEDY_TEXTURE_TOKENS}-greedy, never gating): of "
        f"{texture['ungated_items']} ungated items the model still said the "
        f"concept within {GREEDY_TEXTURE_TOKENS} tokens in "
        f"{texture['ungated_but_says_concept_in_3']} | on the gated cell it said "
        f"the concept in clean {texture['gated_clean_says_concept_in_3']}/{n}, "
        f"primed_late {texture['gated_primed_late_says_concept_in_3']}/{n}, "
        f"control_late {texture['gated_control_late_says_concept_in_3']}/{n}"
    )

    if args.limit and not args.out:
        print("smoke run: results not written (pass --out to keep them)")
        raise SystemExit(0)
    out = args.out or (
        "results/m1-battery-" + args.model_id.split("/")[-1].lower() + ".json"
    )
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w") as f:
        json.dump(results, f, indent=1)
    print(f"results written to {out}")
    raise SystemExit(0)


if __name__ == "__main__":
    main()

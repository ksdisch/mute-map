"""m0_port_gate.py — M0's pre-committed anchor gate (D3: full bit-for-bit).

The bar, frozen before any comparison ran: the port PASSES iff every recorded
cell — per item × instruction × condition **greedy outcome** (`produced` and the
decoded `greedy` token), for all three subjects — plus every per-item
competence-gate membership (`gate_greedy`) and the instrument configuration
(band, thirds, gradable/dropped item sets, and — since D8 — the recorded
`protocol` block and `lens_n_prompts`) matches dim-stage's recorded S4b
JSONs (`anchors/`, dim-stage commit e6c10b9) with **0 mismatches**. Any mismatch
⇒ INVALID (exit 2): investigate the port or the environment until explained —
the bar never softens to "close enough."

Texture (reported, never gating, per D3's wording): the exact-equality rate of
`concept_mass` floats and of the mass-derived `gate_verbatim_p` flags.

Run:  uv run python m0_port_gate.py --all
      uv run python m0_port_gate.py \
          --ours results/anchor-qwen2.5-0.5b-instruct.json \
          --reference anchors/s4-avoidance-qwen2.5-0.5b-instruct.json
"""
from __future__ import annotations

import argparse
import json
import os

from harness import fail_invalid

INSTRUCTIONS = ("naming", "avoidance")
CONDITIONS = (
    "clean",
    "primed_early", "primed_middle", "primed_late",
    "control_early", "control_middle", "control_late",
)
#: D3's gating cell fields: the deterministic greedy outcome.
CELL_FIELDS = ("produced", "greedy")
#: D3's instrument-configuration keys, widened by D8 (M1's brief, review F4) to
#: `protocol` (readback_tol, min_n, collapse_share, gate wording) and
#: `lens_n_prompts`. Safe by construction: the committed artifacts already match
#: on both, so the widening cannot flip M0's PASS — only catch future drift.
COMPARED_CONFIG_KEYS = (
    "model_id",
    "band",
    "thirds",
    "dropped_single_token_prefilter",
    "protocol",
    "lens_n_prompts",
)
SUBJECTS = ("qwen2.5-0.5b-instruct", "qwen2.5-1.5b-instruct", "qwen2.5-3b-instruct")
MAX_PRINTED = 20


def load(path: str) -> dict:
    if not os.path.exists(path):
        fail_invalid(f"{path} missing")
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        # F10: `os.path.exists` is true for a directory, and an artifact can be
        # unreadable or non-UTF-8 — all of which must reach the pre-committed
        # INVALID (exit 2), never an exit-1 traceback.
        fail_invalid(f"{path} could not be read as JSON: {exc}")


def config_mismatches(ours: dict, ref: dict) -> list[str]:
    """Instrument-configuration checks: same subject, band, thirds, item sets,
    and — since D8 — the recorded protocol and lens size, the fields that would
    catch a silently softened instrument. (`lens` itself stays out: it is a path
    and may legitimately differ between repos.)"""
    problems = []
    for key in COMPARED_CONFIG_KEYS:
        if ours.get(key) != ref.get(key):
            problems.append(f"config {key}: ours={ours.get(key)!r} != ref={ref.get(key)!r}")
    our_names = [r["name"] for r in ours.get("items", [])]
    ref_names = [r["name"] for r in ref.get("items", [])]
    if our_names != ref_names:
        problems.append(
            f"item roster differs: {len(our_names)} vs {len(ref_names)} items "
            "or order/name drift"
        )
    return problems


def cell_mismatches(ours: dict, ref: dict) -> list[str]:
    """The D3 bar: every greedy cell and every gate membership, exactly."""
    problems = []
    for our_item, ref_item in zip(ours["items"], ref["items"]):
        name = ref_item["name"]
        if our_item["gate_greedy"] != ref_item["gate_greedy"]:
            problems.append(
                f"{name}: gate_greedy {our_item['gate_greedy']} != {ref_item['gate_greedy']}"
            )
        for inst in INSTRUCTIONS:
            for condition in CONDITIONS:
                our_cell = our_item["instructions"][inst][condition]
                ref_cell = ref_item["instructions"][inst][condition]
                for field in CELL_FIELDS:
                    if our_cell[field] != ref_cell[field]:
                        problems.append(
                            f"{name}/{inst}/{condition}.{field}: "
                            f"{our_cell[field]!r} != {ref_cell[field]!r}"
                        )
    return problems


def mass_texture(ours: dict, ref: dict) -> dict:
    """Non-gating texture: how exactly did the float mass readouts reproduce?"""
    total = equal = 0
    verbatim_equal = all(
        o["gate_verbatim_p"] == r["gate_verbatim_p"]
        for o, r in zip(ours["items"], ref["items"])
    )
    for our_item, ref_item in zip(ours["items"], ref["items"]):
        for inst in INSTRUCTIONS:
            for condition in CONDITIONS:
                total += 1
                if (
                    our_item["instructions"][inst][condition]["concept_mass"]
                    == ref_item["instructions"][inst][condition]["concept_mass"]
                ):
                    equal += 1
    return {"mass_cells_equal": equal, "mass_cells_total": total,
            "gate_verbatim_p_equal": verbatim_equal}


def compare_pair(ours: dict, ref: dict) -> tuple[list[str], dict]:
    problems = config_mismatches(ours, ref)
    if not problems:  # cell walk assumes aligned rosters
        problems = cell_mismatches(ours, ref)
    return problems, (mass_texture(ours, ref) if not problems else {})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ours", help="mute-map anchor results JSON")
    parser.add_argument("--reference", help="dim-stage recorded S4b JSON")
    parser.add_argument(
        "--all", action="store_true",
        help="check the three standard subject pairs (results/anchor-* vs anchors/*)",
    )
    args = parser.parse_args()

    if bool(args.ours) != bool(args.reference):
        fail_invalid("--ours and --reference must be given together")
    if args.all == bool(args.ours and args.reference):
        fail_invalid("pass either --all or both --ours and --reference")
    pairs = (
        [
            (f"results/anchor-{s}.json", f"anchors/s4-avoidance-{s}.json")
            for s in SUBJECTS
        ]
        if args.all
        else [(args.ours, args.reference)]
    )

    failed = False
    for ours_path, ref_path in pairs:
        ours, ref = load(ours_path), load(ref_path)
        problems, texture = compare_pair(ours, ref)
        n_cells = len(ref["items"]) * len(INSTRUCTIONS) * len(CONDITIONS)
        if problems:
            failed = True
            print(f"{ref.get('model_id')}: {len(problems)} mismatches over {n_cells} cells")
            for p in problems[:MAX_PRINTED]:
                print(f"  {p}")
            if len(problems) > MAX_PRINTED:
                print(f"  … and {len(problems) - MAX_PRINTED} more")
        else:
            print(
                f"{ref['model_id']}: 0 mismatches over {n_cells} cells "
                f"(gate n={ours['competence']['gate_greedy']}) | texture: "
                f"concept_mass exact {texture['mass_cells_equal']}/{texture['mass_cells_total']}, "
                f"gate_verbatim_p {'equal' if texture['gate_verbatim_p_equal'] else 'DIFFERS'}"
            )

    if failed:
        fail_invalid("anchor gate mismatches — the port is not the instrument (D3)")
    print(f"M0 ANCHOR GATE: PASS — {len(pairs)}/{len(pairs)} checked pairs bit-for-bit (D3)")
    raise SystemExit(0)


if __name__ == "__main__":
    main()

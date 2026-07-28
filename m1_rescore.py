"""m1_rescore.py — D10(a): the widened-oracle reanalysis of M1, published BESIDE
M1's pre-committed numbers and never in place of them.

**What this is, and what it is not.** M1's results were computed under the
first-token oracle and are published. They stand. This script re-scores the same
recorded cells under D9(b)'s widened oracle (`oracle.says_concept_prefix`) and
emits a separately-labelled **reanalysis** artifact — the arrangement M1's own
results section pre-declared ("any re-scoring of M1 under a widened oracle must
be reported as a separate, clearly-labelled reanalysis alongside these
pre-committed numbers"). Nothing here can change an M1 number: the M1 artifacts
are opened read-only and the outputs go to `results/m1-rescore-*.json`.

**Why no model run is needed** (the argument that makes D10(a) sound rather than
merely cheap). The widened oracle reads the decoded first-3-greedy span, which
M1 already recorded for every cell, and 3 tokens is >= the longest bare form on
the roster (measured on all three Qwen2.5 tokenizers, which agree exactly). For
a *prefix* rule, span truncation cannot hide a hit — a hit must begin at the
span's first character — so the recorded span is provably sufficient and a
re-run (rejected D10(b)) would buy nothing but a second generation of artifacts
to keep straight.

**Self-check.** Because the primary first-token outcome is also recorded per
cell, this script recomputes M1's *published* contrast from the same file and
refuses to write anything unless it reproduces it exactly. A reanalysis that
cannot reproduce the analysis it sits beside is not evidence of anything.

**Riding follow-up (PR #4 review F5, widened at PR #5 review F4).** The
per-source split — S4's 60 reused items versus M1's 120 newly authored ones —
lands here as a recorded number under **both** oracles, rather than staying a
figure quoted in a PR comment.

Run:  uv run python m1_rescore.py
"""
from __future__ import annotations

import argparse
import json
import os

from harness import MIN_N, fail_invalid, rate_cell
from oracle import ORACLE_WORDING, SPAN_TOKENS, says_concept_anywhere, says_concept_prefix
from stats import excludes_zero, newcombe_diff

SUBJECTS = (
    "qwen2.5-0.5b-instruct",
    "qwen2.5-1.5b-instruct",
    "qwen2.5-3b-instruct",
)
CONDITIONS = ("clean", "primed_late", "control_late")
SOURCES = ("s4-reuse", "m1-new")

LABEL = (
    "REANALYSIS — NOT a pre-committed M1 result. M1's published numbers were "
    "computed under the first-token oracle and stand unchanged; this artifact "
    "re-scores the same recorded cells under the widened oracle frozen in "
    "decision D9(b) and is published beside them, per D10(a). It is a pure "
    "function of results/m1-battery-*.json: no model was run and no new trial "
    "was measured."
)

DECISION_WORDING = (
    "D10(a), frozen 2026-07-28. The re-score is computed offline from the "
    "committed M1 artifacts because the recorded 3-token greedy span is "
    "provably sufficient for a prefix rule (3 tokens >= the longest bare form "
    "on the roster, measured on all three Qwen2.5 tokenizers; a prefix hit must "
    "start at the span's first character, so truncation cannot hide one). The "
    "widened numbers are a reanalysis, never a replacement: M1's gate was not "
    "re-run, no verdict is restated, and the M1 verdict of record remains the "
    "pre-committed BREADTH-SPECIFIC at 1.5B and 3B under the first-token "
    "oracle. Rejected: (b) a full re-run, which buys nothing the recorded span "
    "does not already carry while creating a second generation of M1 "
    "artifacts; (c) no reanalysis, which would leave the widened numbers as "
    "un-published design math."
)


def load_run(path: str) -> dict:
    """Read one committed M1 artifact, refusing anything that was pre-declared
    not to be a result — a smoke run or an uncertified stack cannot be
    reanalysed into a published table any more than it could feed a verdict."""
    if not os.path.exists(path):
        fail_invalid(f"{path} missing — run m1_battery.py for that subject first")
    try:
        with open(path) as f:
            run = json.load(f)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        fail_invalid(f"{path} could not be read as JSON: {exc}")
    if run.get("milestone") != "M1":
        fail_invalid(f"{path} is not an M1 battery run (milestone={run.get('milestone')!r})")
    if run.get("smoke_limit") is not None:
        fail_invalid(f"{path} is a SMOKE run (--limit {run['smoke_limit']}) — never a result")
    if not run.get("environment", {}).get("certified"):
        reasons = "; ".join(run.get("environment", {}).get("uncertified_reasons", []))
        fail_invalid(
            f"{path} ran off the certified environment ({reasons}) — pre-declared "
            "NOT A RESULT, so it is not reanalysable either"
        )
    if run.get("anchor_crosscheck", {}).get("n_mismatches"):
        fail_invalid(
            f"{path} carries {run['anchor_crosscheck']['n_mismatches']} anchor "
            "cross-check mismatches"
        )
    return run


def produced(record: dict, condition: str, reading: str) -> bool:
    """One cell's outcome under one reading of the recorded fields.

    `first_token` is M1's published primary (read straight off the recorded
    `produced` flag); `prefix` is D9(b); `containment` is the rejected D9(c),
    identical to M1's recorded `says_concept_in_3` texture.
    """
    cell = record["cells"][condition]
    if reading == "first_token":
        return bool(cell["produced"])
    if reading == "prefix":
        return says_concept_prefix(cell["greedy_3"], record["concept"])
    if reading == "containment":
        return says_concept_anywhere(cell["greedy_3"], record["concept"])
    raise ValueError(f"unknown reading {reading!r}")


def score(records: list[dict], reading: str) -> dict:
    """The pooled gated cell under one reading: gating is the clean arm, decided
    per item, so each reading earns its own gated set — exactly as M1's gate
    did, with only the oracle swapped."""
    gated = [r for r in records if produced(r, "clean", reading)]
    n = len(gated)
    naming = {
        c: rate_cell(sum(produced(r, c, reading) for r in gated), n) for c in CONDITIONS
    }
    diff = (
        newcombe_diff(naming["primed_late"]["hits"], n, naming["control_late"]["hits"], n)
        if n
        else (0.0, -1.0, 1.0)
    )
    return {
        "gated_n": n,
        "items_scored": len(records),
        "naming_success_gated": naming,
        "newcombe_control_minus_primed_late_naming": list(diff),
        "positive_and_ci_excludes_zero": excludes_zero(diff[1], diff[2]) and diff[0] > 0,
        "underpowered": n < MIN_N,
    }


def per_category(records: list[dict], reading: str) -> dict:
    """Which vocabulary the readout can see, by category — the number the
    widening exists to move (planets and musical instruments gated 0 items on
    every subject under the first-token oracle)."""
    groups: dict[str, list[dict]] = {}
    for record in records:
        groups.setdefault(record["category"], []).append(record)
    return {
        category: {
            "items_run": len(group),
            "gated_items": sum(produced(r, "clean", reading) for r in group),
        }
        for category, group in sorted(groups.items())
    }


def case_exact_prefix_gate(records: list[dict]) -> int:
    """Texture: the same prefix rule with the case-insensitivity removed — the
    measured evidence for that half of D9(b) (1.5B: 72 -> 105)."""
    return sum(
        r["cells"]["clean"]["greedy_3"].lstrip().startswith(r["concept"])
        and says_concept_prefix(r["cells"]["clean"]["greedy_3"], r["concept"])
        for r in records
    )


def rescore(run: dict, path: str) -> dict:
    records = run["items"]
    readings = ("first_token", "prefix", "containment")
    oracles = {reading: score(records, reading) for reading in readings}

    # Self-check: the reanalysis must reproduce the analysis it is published
    # beside, from the same file, before it is allowed to write anything.
    published = run["breadth_contrast"]["newcombe_control_minus_primed_late_naming"]
    recomputed = oracles["first_token"]["newcombe_control_minus_primed_late_naming"]
    published_n = run["competence"]["gate_greedy"]
    if oracles["first_token"]["gated_n"] != published_n or recomputed != published:
        fail_invalid(
            f"{path}: recomputing M1's published first-token cell from its own "
            f"recorded fields gave n={oracles['first_token']['gated_n']} "
            f"{recomputed} but the artifact publishes n={published_n} "
            f"{published} — the reanalysis cannot reproduce the analysis it "
            "sits beside, so nothing is written"
        )

    return {
        "milestone": "M1-REANALYSIS",
        "label": LABEL,
        "decision": DECISION_WORDING,
        "oracle_wording": ORACLE_WORDING,
        "span_tokens": SPAN_TOKENS,
        "source_artifact": path,
        "model_id": run["model_id"],
        "source_run": {
            "environment": run["environment"],
            "anchor_crosscheck": {
                k: run["anchor_crosscheck"][k]
                for k in ("n_mismatches", "items_checked", "items_expected")
                if k in run["anchor_crosscheck"]
            },
            "published_first_token_verdict": run["breadth_contrast"]["verdict"],
        },
        "reproduces_published_first_token_cell": True,
        "oracles": oracles,
        # PR #4 review F5, under both oracles (PR #5 review F4): does the
        # contrast hold on the 120 newly authored items alone, or is it carried
        # by the 60 items S4 itself selected?
        "per_source": {
            reading: {
                source: score([r for r in records if r["source"] == source], reading)
                for source in SOURCES
            }
            for reading in ("first_token", "prefix")
        },
        "per_category_gated": {
            reading: per_category(records, reading) for reading in ("first_token", "prefix")
        },
        "case_exact_prefix_gate_texture": case_exact_prefix_gate(records),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", default="results")
    parser.add_argument(
        "--out-dir", default="results", help="where the reanalysis artifacts are written"
    )
    args = parser.parse_args()

    print(f"M1 REANALYSIS (D10a) — {LABEL}\n")
    for subject in SUBJECTS:
        path = os.path.join(args.results_dir, f"m1-battery-{subject}.json")
        run = load_run(path)
        package = rescore(run, path)
        os.makedirs(args.out_dir, exist_ok=True)
        out = os.path.join(args.out_dir, f"m1-rescore-{subject}.json")
        with open(out, "w") as f:
            json.dump(package, f, indent=1)

        first, prefix = package["oracles"]["first_token"], package["oracles"]["prefix"]
        categories = package["per_category_gated"]["prefix"]
        print(f"{subject}:")
        for name, cell in (("first-token (published)", first), ("prefix D9b", prefix)):
            diff = cell["newcombe_control_minus_primed_late_naming"]
            naming = cell["naming_success_gated"]
            print(
                f"  {name:24s} gate {cell['gated_n']}/{cell['items_scored']} | "
                f"primed_late {naming['primed_late']['hits']}/{cell['gated_n']}, "
                f"control_late {naming['control_late']['hits']}/{cell['gated_n']} | "
                f"control−primed {diff[0]:+.3f} [{diff[1]:+.3f},{diff[2]:+.3f}]"
                f"{'' if cell['positive_and_ci_excludes_zero'] else ' (CI includes 0)'}"
            )
        for source in SOURCES:
            cells = [package["per_source"][r][source] for r in ("first_token", "prefix")]
            print(
                f"  per-source {source:9s} "
                + " | ".join(
                    f"{tag} n={c['gated_n']} "
                    f"{c['newcombe_control_minus_primed_late_naming'][0]:+.3f} "
                    f"[{c['newcombe_control_minus_primed_late_naming'][1]:+.3f},"
                    f"{c['newcombe_control_minus_primed_late_naming'][2]:+.3f}]"
                    for tag, c in zip(("first-token", "prefix"), cells)
                )
            )
        print(
            f"  unlocked by the widening: planets "
            f"{package['per_category_gated']['first_token']['planets']['gated_items']}"
            f"→{categories['planets']['gated_items']}, musical instruments "
            f"{package['per_category_gated']['first_token']['musical instruments']['gated_items']}"
            f"→{categories['musical instruments']['gated_items']} of 18 each | "
            f"case-exact prefix gate {package['case_exact_prefix_gate_texture']} "
            f"→ {prefix['gated_n']} case-insensitive"
        )
        print(f"  written to {out}\n")

    print(
        "The M1 verdict of record is unchanged: BREADTH-SPECIFIC at 1.5B and 3B "
        "under the pre-committed first-token oracle. Nothing above restates it."
    )
    raise SystemExit(0)


if __name__ == "__main__":
    main()

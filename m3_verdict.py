"""m3_verdict.py — M3's cross-subject verdict, frozen as code before any run.

`m3_matrix.py` decides one subject at a time. The part of D17 that spans
subjects lives here, so no post-hoc judgement is needed once the numbers land:

- **the M3 verdict itself** — the AND over 1.5B and 3B of each subject's
  MATRIX-SPECIFIC verdict. 0.5B runs and is read out under its standing
  any-direction-damage frame and never enters the AND;
- **the killer figure's numbers, side by side** — the within- vs cross-category
  split, the row profiles (which deleted direction damages the most elsewhere),
  the column profiles, and the collateral floor. The full grid is descriptive by
  decision (D17): no gate reads a per-pair cell and no claim rests on one.

A run that is not a result — smoke (`--limit`), off the certified environment, or
carrying M1 cross-check mismatches — cannot feed the verdict: this exits INVALID
rather than quietly averaging it in. A pre-committed null ("not shown") is a
reportable result and exits 0.

Run:  uv run python m3_verdict.py
"""
from __future__ import annotations

import argparse
import json
import os

from harness import fail_invalid

GATE_BEARING = ("qwen2.5-1.5b-instruct", "qwen2.5-3b-instruct")
CONTEXT_ONLY = ("qwen2.5-0.5b-instruct",)
SUBJECTS = CONTEXT_ONLY + GATE_BEARING

VERDICT_WORDING = (
    "D17, cross-subject: M3 shows the late off-switch is MATRIX-SPECIFIC iff "
    "BOTH gate-bearing subjects (1.5B and 3B) return MATRIX-SPECIFIC on their "
    "pooled gated cell — clause (1), naming under the pooled off-diagonal minus "
    "naming under the pooled diagonal positive with a Newcombe 95% CI excluding "
    "0, AND clause (2), the same restricted to the within-category off-diagonal "
    "against the diagonal of the same restricted item set. Any other combination "
    "is reported as it lands; a pre-committed null is a reportable result, never "
    "a failure. 0.5B is reported under its standing any-direction-damage frame "
    "and never enters the AND. The pre-declared ON A DAMAGED FLOOR qualifier "
    "SCOPES a verdict and never creates or rescues one: a subject whose "
    "collateral-floor Wilson lower bound sits below 0.5 carries it, and the "
    "cross-subject verdict carries it whenever any gate-bearing subject does. "
    "The full 12 x 12 grid, the row and column profiles, the asymmetry texture "
    "and the 18 out-of-subset control cells are descriptive by decision (D17) — "
    "reported beside, never gating, and no claim in this milestone rests on a "
    "per-pair cell."
)


def load(path: str) -> dict:
    if not os.path.exists(path):
        fail_invalid(f"{path} missing — run m3_matrix.py for that subject first")
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        fail_invalid(f"{path} could not be read as JSON: {exc}")


def check_is_a_result(path: str, run: dict) -> None:
    """A run that was pre-declared 'not a result' never reaches the verdict."""
    if run.get("milestone") != "M3":
        fail_invalid(f"{path} is not an M3 matrix run (milestone={run.get('milestone')!r})")
    if run.get("smoke_limit") is not None:
        fail_invalid(f"{path} is a SMOKE run (--limit {run['smoke_limit']}) — never a result")
    if not run.get("environment", {}).get("certified"):
        reasons = "; ".join(run.get("environment", {}).get("uncertified_reasons", []))
        fail_invalid(
            f"{path} ran off the certified environment ({reasons}) — pre-declared NOT A RESULT"
        )
    crosscheck = run.get("m1_crosscheck", {})
    if crosscheck.get("n_mismatches"):
        fail_invalid(f"{path} carries {crosscheck['n_mismatches']} M1 cross-check mismatches")
    checked, expected = crosscheck.get("items_checked"), crosscheck.get("items_expected")
    if expected is None or checked != expected:
        fail_invalid(
            f"{path} cross-checked {checked} of {expected} subset items — a subset "
            "cross-check cannot feed the verdict (D16)"
        )


def _clause(contrast: dict, key: str) -> tuple[dict, list[float], bool]:
    clause = contrast[key]
    return (
        clause,
        clause["newcombe_offdiagonal_minus_diagonal_naming"],
        clause["excludes_zero"],
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results-dir", default="results",
        help="directory holding m3-matrix-<subject>.json for the three subjects",
    )
    args = parser.parse_args()

    runs = {}
    for subject in SUBJECTS:
        path = os.path.join(args.results_dir, f"m3-matrix-{subject}.json")
        run = load(path)
        check_is_a_result(path, run)
        runs[subject] = run

    print(f"M3 VERDICT WORDING (pre-committed): {VERDICT_WORDING}\n")
    for subject in SUBJECTS:
        run = runs[subject]
        contrast = run["specificity_contrast"]
        arms = run["pooled_arms"]
        n = run["competence"]["gate_span"]
        _, c1, ok1 = _clause(contrast, "clause_1_pooled")
        _, c2, ok2 = _clause(contrast, "clause_2_within_category")
        role = "gate-bearing" if subject in GATE_BEARING else "context only (never gate-bearing)"
        print(
            f"{subject} [{role}]: gate n={n}/{run['competence']['items_run']} | "
            f"diagonal {arms['diagonal']['hits']}/{arms['diagonal']['n']}, "
            f"off-diagonal {arms['off_diagonal']['hits']}/{arms['off_diagonal']['n']}, "
            f"within-category {arms['within_category_off_diagonal']['hits']}/"
            f"{arms['within_category_off_diagonal']['n']}, cross-category "
            f"{arms['cross_category_off_diagonal']['hits']}/"
            f"{arms['cross_category_off_diagonal']['n']} | clause(1) {c1[0]:+.3f} "
            f"[{c1[1]:+.3f},{c1[2]:+.3f}] {'CI-clean' if ok1 else 'not CI-clean'}, "
            f"clause(2) {c2[0]:+.3f} [{c2[1]:+.3f},{c2[2]:+.3f}] "
            f"{'CI-clean' if ok2 else 'not CI-clean'} → {contrast['verdict']}"
        )
        floor = contrast["collateral_floor"]
        print(
            f"    collateral floor (cluster-collapsed per-cell survival): "
            f"{floor['k']}/{floor['n']} → [{floor['wilson_95'][0]:.3f}, "
            f"{floor['wilson_95'][1]:.3f}] vs {floor['threshold']} → "
            + ("ON A DAMAGED FLOOR" if floor["damaged_floor"] else "floor clear")
            + (f" | row texture caveats: {', '.join(contrast['row_texture_caveats'])}"
               if contrast.get("row_texture_caveats") else "")
        )
        effective = contrast["effective_n_check"]
        print(
            "    effective-n check (per-item collapse, never dispositive): "
            + ", ".join(
                f"{name.split('_survives_')[0]} "
                f"{effective[name]['off_diagonal']['hits']}/"
                f"{effective[name]['off_diagonal']['n']} vs diagonal "
                f"{effective[name]['diagonal']['hits']}/"
                f"{effective[name]['diagonal']['n']} "
                f"{'CI-clean' if effective[name]['excludes_zero'] else 'NOT CI-clean'}"
                for name in ("clause_1_survives_all_11",
                             "clause_2_survives_all_within_category_siblings")
            )
        )

    print("\nWITHIN- vs CROSS-CATEGORY COLLATERAL (KICKOFF's named readout — the "
          "within arm is gate-bearing via clause (2), the cross arm is texture):")
    for subject in SUBJECTS:
        arms = runs[subject]["pooled_arms"]
        within, cross = arms["within_category_off_diagonal"], arms["cross_category_off_diagonal"]
        print(
            f"  {subject}: within {within['hits']}/{within['n']} "
            f"[{within['wilson_95'][0]:.3f},{within['wilson_95'][1]:.3f}] | cross "
            f"{cross['hits']}/{cross['n']} "
            f"[{cross['wilson_95'][0]:.3f},{cross['wilson_95'][1]:.3f}]"
        )

    print("\nROW PROFILES (descriptive — how much does deleting A damage the other "
          "11 concepts' gated items?):")
    for subject in SUBJECTS:
        rows = runs[subject]["row_profiles"]
        ranked = sorted(
            rows.items(),
            key=lambda kv: (
                1.0 if kv[1]["collateral_all"]["rate"] is None
                else kv[1]["collateral_all"]["rate"]
            ),
        )
        print(
            f"  {subject}: "
            + " ".join(
                f"{name}={v['collateral_all']['hits']}/{v['collateral_all']['n']}"
                for name, v in ranked
            )
            + "   (most collateral first)"
        )

    print("\nTHE MATRIX (descriptive — rows = deleted direction, columns = probed "
          "concept, cell = gated items still naming):")
    for subject in SUBJECTS:
        run = runs[subject]
        subset = run["protocol"]["subset"]
        by_pair = {(e["prime"], e["probe"]): e for e in run["matrix"]}
        print(f"  {subject}:")
        print(" " * 11 + " ".join(f"{c[:3]:>4}" for c in subset) + "   (probe)")
        for prime in subset:
            print(
                f"  {prime:>8} " + " ".join(
                    f"{by_pair[(prime, probe)]['cell']['hits']:>4}" for probe in subset
                )
            )

    holds = {s: runs[s]["specificity_contrast"]["verdict"].startswith("MATRIX-SPECIFIC")
             for s in GATE_BEARING}
    damaged = [s for s in GATE_BEARING
               if runs[s]["specificity_contrast"]["collateral_floor"]["damaged_floor"]]
    context = runs[CONTEXT_ONLY[0]]["specificity_contrast"]
    print(
        f"\n0.5B FRAME (never gate-bearing): its contrast reads {context['verdict']} — "
        "read as any-direction output damage concentrated on the deleted concept "
        "unless it is MATRIX-SPECIFIC, in which case the specificity is present at "
        "0.5B too."
    )
    print(
        "\nM3 VERDICT: "
        + ("MATRIX-SPECIFIC at 1.5B AND 3B — deleting one concept's direction at "
           "the late third silences that concept and largely spares the other 11"
           + (f" — ON A DAMAGED FLOOR ({', '.join(damaged)})" if damaged else "")
           if all(holds.values()) else
           "NOT SHOWN — "
           + "; ".join(
               f"{s}: {runs[s]['specificity_contrast']['verdict']}" for s in GATE_BEARING
           ))
    )
    raise SystemExit(0)


if __name__ == "__main__":
    main()

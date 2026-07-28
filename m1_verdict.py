"""m1_verdict.py — M1's cross-subject verdict, frozen as code before any run.

`m1_battery.py` decides one subject at a time. Two parts of D7(a) span subjects
and live here, so that no post-hoc judgement is needed once the numbers land:

- **the M1 verdict itself** — the AND over 1.5B and 3B of each subject's
  BREADTH-SPECIFIC verdict. 0.5B is read out under its standing
  any-direction-damage frame (pre-declared risk 2) and is never gate-bearing;
- **the prevalence intersection texture** — the fixed denominator is
  per-subject and no cross-subject prevalence comparison is gated or claimed,
  so the intersection of the three subjects' fixed sets (and of their
  hard-switch sets) is reported beside, as texture only.

A run that is not a result — smoke (`--limit`), or off the certified
environment — cannot feed the verdict: this exits INVALID rather than quietly
averaging it in. A pre-committed null ("not shown") is a reportable result and
exits 0.

Run:  uv run python m1_verdict.py
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
    "D7(a), cross-subject: M1 shows the late-band off-switch is a general "
    "property of the measured vocabulary iff BOTH gate-bearing subjects (1.5B "
    "and 3B) return BREADTH-SPECIFIC on their pooled gated cell — naming "
    "success under control_late minus under primed_late positive with a "
    "Newcombe 95% CI excluding 0. Any other combination is reported as it "
    "lands; a pre-committed null is a reportable result, never a failure. 0.5B "
    "is reported under its standing any-direction-damage frame and never "
    "enters the AND. Prevalence is per-subject by construction; the "
    "intersection below is texture, and no cross-subject prevalence claim is "
    "made."
)


def load(path: str) -> dict:
    if not os.path.exists(path):
        fail_invalid(f"{path} missing — run m1_battery.py for that subject first")
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        fail_invalid(f"{path} could not be read as JSON: {exc}")


def check_is_a_result(path: str, run: dict) -> None:
    """A run that was pre-declared 'not a result' never reaches the verdict."""
    if run.get("milestone") != "M1":
        fail_invalid(f"{path} is not an M1 battery run (milestone={run.get('milestone')!r})")
    if run.get("smoke_limit") is not None:
        fail_invalid(f"{path} is a SMOKE run (--limit {run['smoke_limit']}) — never a result")
    if not run.get("environment", {}).get("certified"):
        reasons = "; ".join(run.get("environment", {}).get("uncertified_reasons", []))
        fail_invalid(f"{path} ran off the certified environment ({reasons}) — pre-declared NOT A RESULT")
    crosscheck = run.get("anchor_crosscheck", {})
    if crosscheck.get("n_mismatches"):
        fail_invalid(
            f"{path} carries {crosscheck['n_mismatches']} anchor cross-check mismatches"
        )
    # Review F1: a clean cross-check that compared a *subset* of the reused items is
    # not a re-certification. The expected counts travel in the artifact itself
    # rather than being re-bound here, so this bar cannot drift from the runner's.
    checked, expected = crosscheck.get("items_checked"), crosscheck.get("items_expected")
    if expected is None or checked != expected:
        fail_invalid(
            f"{path} cross-checked {checked} of {expected} reused items — a subset "
            "cross-check cannot feed the verdict (D5a)"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results-dir", default="results",
        help="directory holding m1-battery-<subject>.json for the three subjects",
    )
    args = parser.parse_args()

    runs = {}
    for subject in SUBJECTS:
        path = os.path.join(args.results_dir, f"m1-battery-{subject}.json")
        run = load(path)
        check_is_a_result(path, run)
        runs[subject] = run

    print(f"M1 VERDICT WORDING (pre-committed): {VERDICT_WORDING}\n")
    for subject in SUBJECTS:
        run = runs[subject]
        contrast = run["breadth_contrast"]
        diff = contrast["newcombe_control_minus_primed_late_naming"]
        naming = run["naming_success_gated"]
        prevalence = run["prevalence"]
        role = "gate-bearing" if subject in GATE_BEARING else "context only (never gate-bearing)"
        print(
            f"{subject} [{role}]: gate n={run['competence']['gate_greedy']}"
            f"/{run['competence']['items_run']} | naming primed_late "
            f"{naming['primed_late']['hits']}/{naming['primed_late']['n']} vs "
            f"control_late {naming['control_late']['hits']}/{naming['control_late']['n']} | "
            f"control−primed {diff[0]:+.3f} [{diff[1]:+.3f},{diff[2]:+.3f}] → "
            f"{contrast['verdict']} | prevalence {prevalence['cell']['hits']}/"
            f"{prevalence['cell']['n']} concepts"
            f"{' (UNDERPOWERED, pre-declared)' if prevalence['cell']['underpowered'] else ''}"
        )

    holds = {s: runs[s]["breadth_contrast"]["verdict"] == "BREADTH-SPECIFIC" for s in GATE_BEARING}
    m1_holds = all(holds.values())

    fixed_sets = {s: set(runs[s]["prevalence"]["fixed_denominator_concepts"]) for s in SUBJECTS}
    hard_sets = {s: set(runs[s]["prevalence"]["hard_switch_concepts"]) for s in SUBJECTS}
    fixed_all = set.intersection(*fixed_sets.values())
    hard_all = set.intersection(*hard_sets.values())
    fixed_gate = set.intersection(*(fixed_sets[s] for s in GATE_BEARING))
    hard_gate = set.intersection(*(hard_sets[s] for s in GATE_BEARING))

    print(
        "\nPREVALENCE INTERSECTION (texture — no cross-subject prevalence claim): "
        f"all three subjects share {len(fixed_all)} all-3-gated concepts, of which "
        f"{len(hard_all)} show the hard-switch profile in all three "
        f"({', '.join(sorted(hard_all)) if hard_all else 'none'}); the two "
        f"gate-bearing subjects share {len(fixed_gate)} all-3-gated concepts, of "
        f"which {len(hard_gate)} show the profile in both "
        f"({', '.join(sorted(hard_gate)) if hard_gate else 'none'})."
    )

    context = runs[CONTEXT_ONLY[0]]["breadth_contrast"]
    print(
        f"\n0.5B FRAME (pre-declared risk 2, never gate-bearing): its contrast reads "
        f"{context['verdict']} — read as any-direction output damage at the late "
        "tier unless it is BREADTH-SPECIFIC, in which case specificity is present "
        "at 0.5B too and the scale story from S4b weakens."
    )
    print(
        "\nM1 VERDICT: "
        + ("BREADTH-SPECIFIC at 1.5B AND 3B — the late-band off-switch is general "
           "over the measured vocabulary"
           if m1_holds else
           "NOT SHOWN — "
           + "; ".join(f"{s}: {runs[s]['breadth_contrast']['verdict']}" for s in GATE_BEARING))
    )
    raise SystemExit(0)


if __name__ == "__main__":
    main()

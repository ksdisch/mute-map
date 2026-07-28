"""m2_verdict.py — M2's cross-subject verdict, frozen as code before any run.

`m2_depth.py` decides one subject at a time. The part of D14 that spans subjects
lives here, so no post-hoc judgement is needed once the numbers land:

- **the M2 verdict itself** — the AND over 1.5B and 3B of each subject's
  LATE-LOCALIZED verdict. 0.5B runs and is read out under its standing
  any-direction-damage frame and never enters the AND;
- **the descriptive map, side by side** — the window curve's shape and the dose
  curve's shape are reported across subjects as texture. They are descriptive by
  decision (D12b, D13a): no gate reads them and no claim rests on them.

A run that is not a result — smoke (`--limit`), off the certified environment, or
carrying M1 cross-check mismatches — cannot feed the verdict: this exits INVALID
rather than quietly averaging it in. A pre-committed null ("not shown") is a
reportable result and exits 0.

Run:  uv run python m2_verdict.py
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
    "D14, cross-subject: M2 shows the late-band off-switch is LOCALIZED to the "
    "late third iff BOTH gate-bearing subjects (1.5B and 3B) return "
    "LATE-LOCALIZED on their pooled gated cell — naming under primed_early "
    "minus under primed_late positive with a Newcombe 95% CI excluding 0, AND "
    "the same for primed_middle minus primed_late. Any other combination is "
    "reported as it lands; a pre-committed null is a reportable result, never a "
    "failure. 0.5B is reported under its standing any-direction-damage frame "
    "and never enters the AND. The sliding-window map and the dose curve are "
    "descriptive by decision (D12b, D13a) — reported beside, never gating, and "
    "no claim in this milestone rests on their shape."
)


def load(path: str) -> dict:
    if not os.path.exists(path):
        fail_invalid(f"{path} missing — run m2_depth.py for that subject first")
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        fail_invalid(f"{path} could not be read as JSON: {exc}")


def check_is_a_result(path: str, run: dict) -> None:
    """A run that was pre-declared 'not a result' never reaches the verdict."""
    if run.get("milestone") != "M2":
        fail_invalid(f"{path} is not an M2 depth run (milestone={run.get('milestone')!r})")
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
            "cross-check cannot feed the verdict (D14)"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results-dir", default="results",
        help="directory holding m2-depth-<subject>.json for the three subjects",
    )
    args = parser.parse_args()

    runs = {}
    for subject in SUBJECTS:
        path = os.path.join(args.results_dir, f"m2-depth-{subject}.json")
        run = load(path)
        check_is_a_result(path, run)
        runs[subject] = run

    print(f"M2 VERDICT WORDING (pre-committed): {VERDICT_WORDING}\n")
    for subject in SUBJECTS:
        run = runs[subject]
        contrast = run["localization_contrast"]
        tiers = run["tier_cells"]
        n = run["competence"]["gate_span"]
        early = contrast["newcombe_primed_early_minus_primed_late_naming"]
        middle = contrast["newcombe_primed_middle_minus_primed_late_naming"]
        role = "gate-bearing" if subject in GATE_BEARING else "context only (never gate-bearing)"
        print(
            f"{subject} [{role}]: gate n={n}/{run['competence']['items_run']} | "
            f"primed early {tiers['primed_early']['hits']}/{n}, middle "
            f"{tiers['primed_middle']['hits']}/{n}, late {tiers['primed_late']['hits']}/{n} | "
            f"early−late {early[0]:+.3f} [{early[1]:+.3f},{early[2]:+.3f}], middle−late "
            f"{middle[0]:+.3f} [{middle[1]:+.3f},{middle[2]:+.3f}] → {contrast['verdict']}"
        )
        print(
            f"    control tiers (texture): "
            + ", ".join(f"{t} {tiers[f'control_{t}']['hits']}/{n}"
                        for t in ("early", "middle", "late"))
            + (f" | caveats: {', '.join(contrast['control_tier_specificity_caveats'])}"
               if contrast.get("control_tier_specificity_caveats") else "")
        )

    print("\nWINDOW MAP (descriptive — no gate reads it):")
    for subject in SUBJECTS:
        run = runs[subject]
        n = run["competence"]["gate_span"]
        print(
            f"  {subject}: "
            + " ".join(
                f"L{w['start']}–L{w['end']}"
                f"{'*' if w['is_gate_cell'] else ('°' if w['outside_band'] else '')}"
                f"={w['cell']['hits']}/{n}"
                for w in run["window_map"]
            )
        )
    print("  (* the late-third gate cell, reused; ° a window with no layer in the band)")

    print("\nDOSE CURVE (descriptive — no gate reads it):")
    for subject in SUBJECTS:
        run = runs[subject]
        n = run["competence"]["gate_span"]
        print(
            f"  {subject}: "
            + " ".join(
                f"λ={d['lambda']:g}:{d['cell']['hits']}/{n}"
                + (f"({d['mean_concept_mass_eligible']:.3f})"
                   if d["mean_concept_mass_eligible"] is not None else "")
                for d in run["dose_curve"]
            )
            + f"   [mass over {run['dose_curve'][0]['mass_channel_n']} eligible items]"
        )

    holds = {s: runs[s]["localization_contrast"]["verdict"] == "LATE-LOCALIZED"
             for s in GATE_BEARING}
    context = runs[CONTEXT_ONLY[0]]["localization_contrast"]
    print(
        f"\n0.5B FRAME (never gate-bearing): its contrast reads {context['verdict']} — "
        "read as any-direction output damage concentrated at the late tier unless "
        "it is LATE-LOCALIZED, in which case the localization is present at 0.5B too."
    )
    print(
        "\nM2 VERDICT: "
        + ("LATE-LOCALIZED at 1.5B AND 3B — the off-switch lives specifically in "
           "the late third of the workspace band"
           if all(holds.values()) else
           "NOT SHOWN — "
           + "; ".join(
               f"{s}: {runs[s]['localization_contrast']['verdict']}" for s in GATE_BEARING
           ))
    )
    raise SystemExit(0)


if __name__ == "__main__":
    main()

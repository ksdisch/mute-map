"""m4_verdict.py — M4's verdict precedence and its cross-subject verdict, frozen
as code before any run.

Two jobs, deliberately in one module:

- **`strip_verdict()`** — D20's frozen per-subject precedence, NOT A RESULT >
  DEGENERATE > UNDERPOWERED > the level bar, together with the two verdict-string
  templates the D20 wording package pre-commits. `m4_strip.py` imports it rather
  than carrying its own copy: the whole point of a pre-committed verdict string
  is that exactly one implementation of it exists, so the runner and any
  re-analysis can never print differently-shaped verdicts. (The cut-from-your-
  predecessor rule protects certified *measurement* code from edits; it is not a
  reason to duplicate a wording rule whose purpose is byte-identity — the same
  rationale `oracle.py` is shared under.)
- **the cross-subject verdict** — the AND over 1.5B and 3B. 0.5B runs and is read
  out under its standing any-direction-damage frame and never enters the AND;
  Amendment 2 (ii) scopes that inside the frozen gate wording itself, so a low
  0.5B reading is never a `not shown` gate claim.

A run that is not a result — smoke (`--limit`), off the certified environment, or
carrying M1 or M3 cross-check mismatches — cannot feed the verdict: this exits
INVALID rather than quietly averaging it in. A pre-committed null (`not shown`)
is a reportable result and exits 0.

Run:  uv run python m4_verdict.py
"""
from __future__ import annotations

import argparse
import json
import os

from harness import MIN_N, fail_invalid

GATE_BEARING = ("qwen2.5-1.5b-instruct", "qwen2.5-3b-instruct")
CONTEXT_ONLY = ("qwen2.5-0.5b-instruct",)
SUBJECTS = CONTEXT_ONLY + GATE_BEARING

#: D20's bar on the 12-fold conjunction. NOT M3's per-cell floor constant: the
#: same digits mean opposite things across the two statistics (under
#: independence a conjunction of 0.5 is a per-cell 0.5^(1/12) ~ 0.944). New,
#: deliberately lenient, uncalibrated, pre-registered before any M4 cell ran and
#: fitted to none — owned as its own deviations-table row.
SURVIVAL_LOWER_BOUND = 0.5
#: The number of deletions each gate-arm item must survive — half the bar's
#: stringency, and named in the verdict string so it cannot be quoted away.
N_DELETIONS = 12

PASS_LABEL = "VOCAB-SPARING"
#: The lineage's pre-committed null (`m1_battery.py`, `m2_depth.py`,
#: `m3_matrix.py` all emit it). Failing a Wilson *lower* bound does not establish
#: the contrary, so the failing label is never an assertive negative
#: (Amendment 2 (i)).
NULL_LABEL = "not shown"
QUALIFIER = "AS-SCORED ONLY"
#: The fixed read order Amendment 2 (iv) pre-commits for the qualifier string.
CONSERVATIVE_READ_ORDER = ("residual-conservative", "concept-level")

VERDICT_WORDING = (
    "D20, cross-subject: M4 shows the late off-switch is VOCAB-SPARING iff BOTH "
    "gate-bearing subjects (1.5B and 3B) clear the level bar on their gate arm — "
    "among the gated NON-SUBSET items, the proportion that survives all 12 "
    "subset-direction deletions has its Wilson 95% lower bound at or above 0.5. "
    "The gate verdict is the AND over the two gate-bearing subjects; 0.5B runs, "
    "is reported in the same shape under its standing any-direction-damage "
    "frame, and is NOT a gate verdict, so a low 0.5B reading is never a "
    "'not shown' gate claim (Amendment 2 (ii)). A pre-committed null is a "
    "reportable result, never a failure. Every verdict at bar level carries its "
    "realized survival proportion inside the verdict string, and carries the "
    "AS-SCORED ONLY qualifier whenever a pre-registered conservative read "
    "(residual-conservative fail-in-place, or the concept-level collapse) falls "
    "below the bar while the as-scored read does not. The qualifier SCOPES a "
    "claim and can never create or rescue one, so it attaches at bar level only "
    "and never to NOT A RESULT, DEGENERATE or UNDERPOWERED. The bar is read "
    "ONLY when the 255 M1-recorded and 468 M3-recorded cells in the strip "
    "reproduce their recorded outcomes bit-for-bit; any mismatch is INVALID and "
    "there is no verdict. The row and column profiles, the within- vs "
    "cross-category split, the ordering contrast, the cluster-mean per-cell "
    "floor and the five named cross-mention cells are descriptive by decision "
    "(D20/D21) — reported beside, never gating."
)


# --- the frozen verdict strings ----------------------------------------------

def _read_string(read: dict) -> str:
    return (
        f"{read['read']} {read['k']}/{read['n']} = {read['rate']:.3f}, "
        f"lower {read['wilson_95'][0]:.3f}"
    )


def qualifier_fires(gate: dict, conservative_reads: list[dict]) -> bool:
    """D20: the qualifier fires iff a pre-registered conservative read's Wilson
    95% lower bound is below the bar while the as-scored read's is not.

    Read literally, that condition can only be met when the as-scored read
    CLEARS the bar — which is why the qualifier can only ever scope a pass, and
    never creates or rescues a claim (D17's rule, carried).
    """
    if gate["wilson_95"][0] < SURVIVAL_LOWER_BOUND:
        return False
    return any(r["wilson_95"][0] < SURVIVAL_LOWER_BOUND for r in conservative_reads)


def verdict_string(label: str, gate: dict, conservative_reads: list[dict]) -> str:
    """D20's two templates, stated once in the brief and implemented verbatim.

    base:      `<label> (k/n survive all 12 = <rate>; Wilson 95% lower <lo>)`
    qualifier: ` — AS-SCORED ONLY (<read> k/n = <rate>, lower <lo>[; <read> ...])`

    Worked (the brief's own example): `VOCAB-SPARING (44/71 survive all 12 =
    0.620; Wilson 95% lower 0.503) — AS-SCORED ONLY (residual-conservative
    42/71 = 0.592, lower 0.475)`.
    """
    base = (
        f"{label} ({gate['k']}/{gate['n']} survive all {N_DELETIONS} = "
        f"{gate['rate']:.3f}; Wilson 95% lower {gate['wilson_95'][0]:.3f})"
    )
    if not qualifier_fires(gate, conservative_reads):
        return base
    unknown = sorted({r["read"] for r in conservative_reads} - set(CONSERVATIVE_READ_ORDER))
    if unknown:
        fail_invalid(
            f"conservative read(s) {unknown} are not in the pre-committed order "
            f"{list(CONSERVATIVE_READ_ORDER)} — the qualifier's read order is "
            "frozen wording, not a runtime choice"
        )
    fired = [
        r for name in CONSERVATIVE_READ_ORDER
        for r in conservative_reads
        if r["read"] == name and r["wilson_95"][0] < SURVIVAL_LOWER_BOUND
    ]
    return base + f" — {QUALIFIER} (" + "; ".join(_read_string(r) for r in fired) + ")"


def strip_verdict(
    certified: bool,
    degenerate_arms: list[str],
    gate: dict,
    conservative_reads: list[dict],
    limit: int | None = None,
) -> str:
    """D20's frozen precedence: NOT A RESULT > DEGENERATE > UNDERPOWERED > the
    level bar.

    `gate` is the as-scored gate arm — `{k, n, rate, wilson_95}` — and
    `conservative_reads` are the pre-registered never-dispositive reads whose
    numbers the AS-SCORED ONLY qualifier names when it fires. The qualifier
    attaches at bar level ONLY: the three higher outcomes have already withheld
    the claim, so there is nothing left for it to scope (Amendment 2 (iii),
    copying `m3_matrix.matrix_verdict`'s own rule for ON A DAMAGED FLOOR).
    """
    if limit is not None:
        return f"NOT A RESULT — smoke run (--limit {limit})"
    if not certified:
        return "NOT A RESULT — uncertified environment"
    if degenerate_arms:
        return (
            "DEGENERATE — no vocabulary-sparing claim "
            f"(collapsed: {', '.join(degenerate_arms)})"
        )
    if gate["n"] < MIN_N:
        return f"UNDERPOWERED — no vocabulary-sparing claim (gate arm n={gate['n']})"
    label = PASS_LABEL if gate["wilson_95"][0] >= SURVIVAL_LOWER_BOUND else NULL_LABEL
    return verdict_string(label, gate, conservative_reads)


# --- the cross-subject verdict ------------------------------------------------

def load(path: str) -> dict:
    if not os.path.exists(path):
        fail_invalid(f"{path} missing — run m4_strip.py for that subject first")
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError, UnicodeDecodeError) as exc:
        fail_invalid(f"{path} could not be read as JSON: {exc}")


def _check_crosscheck(path: str, name: str, crosscheck: dict) -> None:
    """A partial re-certification is not a re-certification (D16's lesson, now
    over two artifact sets): coverage is checked as well as agreement."""
    if crosscheck.get("n_mismatches"):
        fail_invalid(f"{path} carries {crosscheck['n_mismatches']} {name} cross-check mismatches")
    for unit in ("items", "cells"):
        checked = crosscheck.get(f"{unit}_checked")
        expected = crosscheck.get(f"{unit}_expected")
        if expected is None or checked != expected:
            fail_invalid(
                f"{path} {name} cross-check covered {checked} of {expected} {unit} "
                "— a partial cross-check cannot feed the verdict (D19)"
            )


def check_is_a_result(path: str, run: dict) -> None:
    """A run that was pre-declared 'not a result' never reaches the verdict."""
    if run.get("milestone") != "M4":
        fail_invalid(f"{path} is not an M4 strip run (milestone={run.get('milestone')!r})")
    if run.get("smoke_limit") is not None:
        fail_invalid(f"{path} is a SMOKE run (--limit {run['smoke_limit']}) — never a result")
    if not run.get("environment", {}).get("certified"):
        reasons = "; ".join(run.get("environment", {}).get("uncertified_reasons", []))
        fail_invalid(
            f"{path} ran off the certified environment ({reasons}) — pre-declared NOT A RESULT"
        )
    _check_crosscheck(path, "M1", run.get("m1_crosscheck", {}))
    _check_crosscheck(path, "M3", run.get("m3_crosscheck", {}))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results-dir", default="results",
        help="directory holding m4-strip-<subject>.json for the three subjects",
    )
    args = parser.parse_args()

    runs = {}
    for subject in SUBJECTS:
        path = os.path.join(args.results_dir, f"m4-strip-{subject}.json")
        run = load(path)
        check_is_a_result(path, run)
        runs[subject] = run

    print(f"M4 VERDICT WORDING (pre-committed): {VERDICT_WORDING}\n")
    for subject in SUBJECTS:
        run = runs[subject]
        sparing = run["vocabulary_sparing"]
        gate = sparing["gate_arm"]
        role = "gate-bearing" if subject in GATE_BEARING else "context only (never gate-bearing)"
        print(
            f"{subject} [{role}]: gated {run['competence']['gate_span']}/"
            f"{run['competence']['items_run']} items, gate arm (gated non-subset) "
            f"n={gate['n']} | survives-all-12 {gate['k']}/{gate['n']} = "
            f"{gate['rate']:.3f} [{gate['wilson_95'][0]:.3f}, "
            f"{gate['wilson_95'][1]:.3f}] vs bar {SURVIVAL_LOWER_BOUND} "
            f"→ {sparing['verdict']}"
        )
        for read in sparing["conservative_reads"]:
            print(
                f"    {read['read']} (pre-registered, never dispositive): "
                f"{read['k']}/{read['n']} = {read['rate']:.3f} "
                f"[{read['wilson_95'][0]:.3f}, {read['wilson_95'][1]:.3f}]"
                + (" — below the bar" if read["wilson_95"][0] < SURVIVAL_LOWER_BOUND
                   else " — clears the bar")
            )
        floor = sparing["cluster_mean_floor"]
        ordering = sparing["ordering_contrast"]["newcombe_offtarget_minus_diagonal_naming"]
        print(
            f"    M3-comparable cluster-mean per-cell floor (never gating): "
            f"{floor['k']}/{floor['n']} → [{floor['wilson_95'][0]:.3f}, "
            f"{floor['wilson_95'][1]:.3f}] vs reference line {floor['reference_line']}"
            f" | ordering contrast (option (b), descriptive) {ordering[0]:+.3f} "
            f"[{ordering[1]:+.3f}, {ordering[2]:+.3f}]"
        )

    print("\nWITHIN- vs CROSS-CATEGORY COLLATERAL IN THE NEW POOL (descriptive):")
    for subject in SUBJECTS:
        split = runs[subject]["new_pool_arms"]
        within, cross = split["within_category"], split["cross_category"]
        print(
            f"  {subject}: within {within['hits']}/{within['n']} "
            f"[{within['wilson_95'][0]:.3f},{within['wilson_95'][1]:.3f}] | cross "
            f"{cross['hits']}/{cross['n']} "
            f"[{cross['wilson_95'][0]:.3f},{cross['wilson_95'][1]:.3f}]"
        )

    print("\nROW PROFILES (descriptive — how much does deleting A damage the wider "
          "vocabulary's gated items?):")
    for subject in SUBJECTS:
        rows = runs[subject]["row_profiles"]
        ranked = sorted(
            rows.items(),
            key=lambda kv: (1.0 if kv[1]["collateral_non_subset"]["rate"] is None
                            else kv[1]["collateral_non_subset"]["rate"]),
        )
        print(
            f"  {subject}: "
            + " ".join(f"{name}={v['collateral_non_subset']['hits']}/"
                       f"{v['collateral_non_subset']['n']}" for name, v in ranked)
            + "   (most collateral first)"
        )

    print("\nMOST FRAGILE PROBE COLUMNS (finding 1's mostly out-of-sample test — "
          "are there silver-like columns among the 48?):")
    for subject in SUBJECTS:
        columns = runs[subject]["column_profiles"]
        damaged = sorted(
            (c for c, v in columns.items()
             if v["gated_items"] and v["fragility"]["n"] and v["fragility"]["hits"] < v["fragility"]["n"]),
            key=lambda c: columns[c]["fragility"]["rate"],
        )
        print(
            f"  {subject}: "
            + (" ".join(
                f"{c}{'*' if columns[c]['in_subset'] else ''}="
                f"{columns[c]['fragility']['hits']}/{columns[c]['fragility']['n']}"
                for c in damaged[:12]) or "no damaged column")
            + "   (* subset concept — M3's own 12)"
        )

    holds = {s: runs[s]["vocabulary_sparing"]["verdict"].startswith(PASS_LABEL)
             for s in GATE_BEARING}
    scoped = [s for s in GATE_BEARING if QUALIFIER in runs[s]["vocabulary_sparing"]["verdict"]]
    context = runs[CONTEXT_ONLY[0]]["vocabulary_sparing"]
    print(
        f"\n0.5B FRAME (never gate-bearing): its readout is {context['verdict']} — "
        "read under the standing any-direction-damage frame, never as a gate "
        "claim. M3's own 0.5B subset already fails this bar in-statistic (19/28, "
        "lower 0.4934), so a low 0.5B reading here is a finding about scale, not "
        "a failure of the run."
    )
    print(
        "\nM4 VERDICT: "
        + (f"{PASS_LABEL} at 1.5B AND 3B — deleting any of the 12 characterized "
           "directions at the late third spares most of the measurable wider "
           "vocabulary"
           + (f" — {QUALIFIER} ({', '.join(scoped)})" if scoped else "")
           if all(holds.values()) else
           f"{NULL_LABEL.upper()} — "
           + "; ".join(f"{s}: {runs[s]['vocabulary_sparing']['verdict']}"
                       for s in GATE_BEARING))
    )
    raise SystemExit(0)


if __name__ == "__main__":
    main()

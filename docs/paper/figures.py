#!/usr/bin/env python3
"""Render the paper's figures from mute-map's committed result JSONs.

Run
---
    uv run --with matplotlib docs/paper/figures.py

matplotlib is injected for that run only and is deliberately NOT added to
``pyproject.toml``: the project's dependency set is the one the measurements ran
under, and a write-up must not change it.

Reads (read-only, never written)
--------------------------------
    results/m1-battery-qwen2.5-{0.5b,1.5b,3b}-instruct.json
    results/m2-depth-qwen2.5-{0.5b,1.5b,3b}-instruct.json
    results/m3-matrix-qwen2.5-{0.5b,1.5b,3b}-instruct.json
    results/m4-strip-qwen2.5-{0.5b,1.5b,3b}-instruct.json

Writes
------
    docs/paper/fig1-gate-contrasts.png   the five pre-committed gate contrasts (M1, M2 x2, M3 x2),
                                         recorded Newcombe point estimate and 95% interval, x3 subjects
    docs/paper/fig2-localization.png     M2 sliding-window sweep: naming survival per window start,
                                         recorded Wilson 95% intervals, workspace band shaded
    docs/paper/fig3-dose.png             M2 dose grid: naming rate (recorded Wilson 95%) and mean
                                         concept mass at the five frozen lambda values
    docs/paper/fig4-matrix.png           M3 12 x 12 prime x probe matrix, cell = recorded naming
                                         survival rate, annotated with the recorded hits/n
    docs/paper/fig5-m4-floors.png        M4's three pre-registered floor reads against the frozen
                                         0.5 bar, recorded Wilson 95% intervals
    docs/paper/fig6-collateral-asymmetry.png
                                         M4 per-prime row survival vs per-probe column survival,
                                         both recorded rates, one mark per concept

What this script computes -- and does not
-----------------------------------------
It computes NOTHING beyond reading recorded values and, where a JSON records a
count pair rather than a rate, the single division ``hits / n``. Every point, every
interval endpoint and every axis value (lambda, layer, band, subject) is lifted
verbatim from the files above.

It does NOT smooth, interpolate, fit, re-bin, pool across cells the repo did not
pool, or compute an interval of its own. No line is drawn between grid points on
the sweep or the dose figures: the values between two measured positions were never
measured, and connecting them would assert them. Error bars are the recorded
``wilson_95`` / ``newcombe_*`` endpoints re-expressed as distances from their own
recorded point estimate, which is what matplotlib's API takes -- the interval drawn
is the recorded interval. Ordering marks by rank (figure 6) orders recorded values;
it creates none.

Every plotted number is printed to stdout with the file and JSON key it came from,
so the figures can be checked against the paper's tables without opening a PNG.

Deterministic and headless: same inputs, same PNGs, on any re-run.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: no display, no interactive backend

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D

REPO = Path(__file__).resolve().parents[2]
RESULTS = REPO / "results"
OUT = Path(__file__).resolve().parent

SUBJECTS = [
    ("0.5B", "qwen2.5-0.5b-instruct"),
    ("1.5B", "qwen2.5-1.5b-instruct"),
    ("3B", "qwen2.5-3b-instruct"),
]

# --- dataviz palette: categorical slots 1-3, light surface -------------------
# Validated with the dataviz skill's validate_palette.js (light, surface #fcfcfb,
# --pairs all): lightness band PASS, chroma floor PASS, worst all-pairs CVD dE 9.2,
# worst normal-vision dE 24.0. Aqua sits below 3:1 on the light surface, so the
# relief rule applies -- every series is direct-labelled or legended, and the paper
# carries the full table view beside each figure.
SERIES = {"0.5B": "#2a78d6", "1.5B": "#eb6834", "3B": "#1baf7a"}

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
BAND_FILL = "#f0efec"

# Sequential blue ramp (dataviz reference palette, steps 100 -> 700), reversed so
# that a muted cell (survival 0) is darkest and a spared cell (survival 1) recedes
# toward the surface -- one hue, monotonic in lightness.
BLUE_RAMP = [
    "#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7",
    "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b",
]
SEQ = LinearSegmentedColormap.from_list("mute_blue_r", list(reversed(BLUE_RAMP)))


def load(stage: str, slug: str) -> dict:
    with (RESULTS / f"{stage}-{slug}.json").open() as fh:
        return json.load(fh)


def style(ax) -> None:
    ax.set_facecolor(SURFACE)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(AXIS)
        ax.spines[side].set_linewidth(0.8)
    ax.tick_params(colors=MUTED, labelsize=8, length=3, width=0.8)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_color(INK_2)


def new_figure(*args, **kwargs):
    fig, axes = plt.subplots(*args, **kwargs)
    fig.patch.set_facecolor(SURFACE)
    return fig, axes


def save(fig, name: str) -> None:
    path = OUT / name
    fig.savefig(path, dpi=200, facecolor=SURFACE, bbox_inches="tight")
    plt.close(fig)
    print(f"\n  wrote {path.relative_to(REPO)}")


def band(label: str) -> str:
    return f"[{label}]"


# ---------------------------------------------------------------------------
# Figure 1 -- the five pre-committed gate contrasts
# ---------------------------------------------------------------------------

def figure_1() -> None:
    print("\n=== FIGURE 1: pre-committed gate contrasts "
          "(recorded Newcombe 95% intervals) ===")

    # (row label, stage, JSON key path into the result file)
    ROWS = [
        ("M3 clause (2)\nwithin-category off-diag - diagonal", "m3-matrix",
         ("specificity_contrast", "clause_2_within_category",
          "newcombe_offdiagonal_minus_diagonal_naming")),
        ("M3 clause (1)\npooled off-diagonal - diagonal", "m3-matrix",
         ("specificity_contrast", "clause_1_pooled",
          "newcombe_offdiagonal_minus_diagonal_naming")),
        ("M2  middle - late", "m2-depth",
         ("localization_contrast", "newcombe_primed_middle_minus_primed_late_naming")),
        ("M2  early - late", "m2-depth",
         ("localization_contrast", "newcombe_primed_early_minus_primed_late_naming")),
        ("M1  control_late - primed_late", "m1-battery",
         ("breadth_contrast", "newcombe_control_minus_primed_late_naming")),
    ]

    fig, ax = new_figure(figsize=(7.6, 5.0))
    style(ax)
    ax.set_axisbelow(True)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8)
    ax.axvline(0.0, color=INK_2, linewidth=1.0)

    offsets = {"0.5B": +0.24, "1.5B": 0.0, "3B": -0.24}
    for row, (label, stage, keys) in enumerate(ROWS):
        for subject, slug in SUBJECTS:
            data = load(stage, slug)
            node = data
            for key in keys:
                node = node[key]
            point, lo, hi = node
            y = row + offsets[subject]
            ax.errorbar(
                point, y, xerr=[[point - lo], [hi - point]],
                fmt="o", markersize=6.5, elinewidth=1.6, capsize=0,
                color=SERIES[subject], markeredgecolor=SURFACE, markeredgewidth=1.6,
                zorder=3,
            )
            print(f"  {stage:10s} {subject:5s} {label.replace(chr(10), ' '):52s} "
                  f"{point:+.4f} [{lo:+.4f}, {hi:+.4f}]   "
                  f"<- {stage}-{slug}.json : {'.'.join(keys)}")

    ax.set_yticks(range(len(ROWS)))
    ax.set_yticklabels([label for label, _, _ in ROWS], fontsize=8.5)
    ax.set_ylim(-0.6, len(ROWS) - 0.4)
    ax.set_xlim(-0.05, 1.05)
    ax.set_xlabel("difference in naming-survival rate (Newcombe 95%)",
                  fontsize=9, color=INK_2)
    ax.set_title(
        "Every pre-committed gate contrast excludes zero, on all three subjects",
        fontsize=11, color=INK, loc="left", pad=12,
    )
    handles = [
        Line2D([], [], marker="o", linestyle="none", markersize=6.5,
               color=SERIES[s], markeredgecolor=SURFACE, markeredgewidth=1.6,
               label=f"{s}{'  (off-gate)' if s == '0.5B' else ''}")
        for s, _ in SUBJECTS
    ]
    ax.legend(handles=handles, frameon=False, fontsize=8.5, loc="lower left",
              labelcolor=INK_2)
    save(fig, "fig1-gate-contrasts.png")


# ---------------------------------------------------------------------------
# Figure 2 -- M2 sliding-window localization sweep
# ---------------------------------------------------------------------------

def figure_2() -> None:
    print("\n=== FIGURE 2: M2 window sweep "
          "(naming survival per window start, recorded Wilson 95%) ===")

    fig, axes = new_figure(3, 1, figsize=(7.8, 7.6), sharey=True)
    for ax, (subject, slug) in zip(axes, SUBJECTS):
        data = load("m2-depth", slug)
        layers = data["band"]
        width = data["window_width"]
        gated_n = data["tier_cells"]["primed_late"]["n"]
        style(ax)
        ax.set_axisbelow(True)
        ax.yaxis.grid(True, color=GRID, linewidth=0.8)
        ax.axvspan(min(layers) - 0.5, max(layers) + 0.5, color=BAND_FILL,
                   zorder=0, linewidth=0)

        print(f"\n  -- {subject} ({slug})  band L{min(layers)}-L{max(layers)}, "
              f"window width {width}, gated n = {gated_n}"
              f"   <- m2-depth-{slug}.json : band / window_width / "
              f"tier_cells.primed_late.n")
        for window in data["window_map"]:
            cell = window["cell"]
            rate, lo, hi = cell["rate"], cell["wilson_95"][0], cell["wilson_95"][1]
            gate = window["is_gate_cell"]
            ax.errorbar(
                window["start"], rate, yerr=[[rate - lo], [hi - rate]],
                fmt="D" if gate else "o", markersize=7.0 if gate else 6.0,
                elinewidth=1.4, capsize=0, color=SERIES[subject],
                markeredgecolor=SURFACE, markeredgewidth=1.5, zorder=3,
            )
            flag = "  * late-third gate cell" if gate else (
                "  (no layer in band)" if window["outside_band"] else "")
            print(f"     {window['name']:16s} start L{window['start']:<3d} "
                  f"{cell['hits']:3d}/{cell['n']:<3d} rate {rate:.4f} "
                  f"[{lo:.4f}, {hi:.4f}]{flag}"
                  f"   <- window_map[{window['name']}].cell")

        gate_x = next(w["start"] for w in data["window_map"] if w["is_gate_cell"])
        ax.annotate(
            "late-third\ngate cell", xy=(gate_x, 0.0), xytext=(gate_x, 0.30),
            fontsize=8, color=INK_2, ha="center",
            arrowprops=dict(arrowstyle="-", color=AXIS, linewidth=0.8),
        )
        ax.text(0.995, 0.93, f"{subject}   window width {width},  n = {gated_n}",
                transform=ax.transAxes, ha="right", va="top", fontsize=9,
                color=SERIES[subject], fontweight="bold")
        ax.text(min(layers) + 0.2, 0.06, "workspace band", fontsize=7.5,
                color=MUTED, va="bottom")
        ax.set_ylim(-0.06, 1.10)
        ax.set_ylabel("naming survival", fontsize=9, color=INK_2)

    axes[-1].set_xlabel("window start layer  (stride 2; marks are measured "
                        "positions only — no line is drawn between them)",
                        fontsize=9, color=INK_2)
    axes[0].set_title(
        "The switch is a late cliff on a floor, not a band-wide effect",
        fontsize=11, color=INK, loc="left", pad=12,
    )
    fig.tight_layout()
    save(fig, "fig2-localization.png")


# ---------------------------------------------------------------------------
# Figure 3 -- M2 dose grid
# ---------------------------------------------------------------------------

def figure_3() -> None:
    print("\n=== FIGURE 3: M2 dose grid at the five frozen lambda values ===")

    fig, axes = new_figure(1, 2, figsize=(8.4, 3.9))
    for ax in axes:
        style(ax)
        ax.set_axisbelow(True)
        ax.yaxis.grid(True, color=GRID, linewidth=0.8)
        ax.set_xlim(-0.08, 1.08)
        ax.set_ylim(-0.06, 1.10)
        ax.set_xticks([0.0, 0.25, 0.5, 0.75, 1.0])
        ax.set_xlabel("$\\lambda$  (fraction of the direction removed)",
                      fontsize=9, color=INK_2)

    # Subjects are dodged horizontally at each lambda purely so overlapping marks
    # stay visible (three subjects sit at exactly 1.0 naming at lambda = 0). The
    # ticks are the five frozen grid values; no mark is placed at an unmeasured
    # lambda, and the dodge carries no information.
    dodge = {"0.5B": -0.022, "1.5B": 0.0, "3B": +0.022}
    for subject, slug in SUBJECTS:
        data = load("m2-depth", slug)
        print(f"\n  -- {subject} ({slug})   <- m2-depth-{slug}.json : dose_curve")
        for entry in data["dose_curve"]:
            cell = entry["cell"]
            lam = entry["lambda"]
            x = lam + dodge[subject]
            rate, lo, hi = cell["rate"], cell["wilson_95"][0], cell["wilson_95"][1]
            mass = entry["mean_concept_mass_eligible"]
            axes[0].errorbar(
                x, rate, yerr=[[rate - lo], [hi - rate]], fmt="o", markersize=6.0,
                elinewidth=1.4, capsize=0, color=SERIES[subject],
                markeredgecolor=SURFACE, markeredgewidth=1.5, zorder=3,
            )
            axes[1].plot(x, mass, "o", markersize=6.0, color=SERIES[subject],
                         markeredgecolor=SURFACE, markeredgewidth=1.5, zorder=3)
            reused = f"  (reused: {entry['reused_from']})" if entry["reused_from"] else ""
            print(f"     lambda {lam:<5.2f} naming {cell['hits']:3d}/{cell['n']:<3d} "
                  f"rate {rate:.4f} [{lo:.4f}, {hi:.4f}]   mean concept mass "
                  f"{mass:.4f} (mass n = {entry['mass_channel_n']}){reused}")

    axes[0].set_ylabel("naming survival (Wilson 95%)", fontsize=9, color=INK_2)
    axes[0].set_title("binary readout", fontsize=9.5, color=INK, loc="left")
    axes[1].set_ylabel("mean concept softmax mass", fontsize=9, color=INK_2)
    axes[1].set_title("graded readout", fontsize=9.5, color=INK, loc="left")

    handles = [
        Line2D([], [], marker="o", linestyle="none", markersize=6.0,
               color=SERIES[s], markeredgecolor=SURFACE, markeredgewidth=1.5,
               label=f"{s}{'  (off-gate)' if s == '0.5B' else ''}")
        for s, _ in SUBJECTS
    ]
    axes[1].legend(handles=handles, frameon=False, fontsize=8.5, loc="upper right",
                   labelcolor=INK_2)
    fig.suptitle("A dimmer, not a step — and the knee moves right with scale",
                 fontsize=11, color=INK, x=0.005, ha="left", y=1.02)
    fig.tight_layout()
    save(fig, "fig3-dose.png")


# ---------------------------------------------------------------------------
# Figure 4 -- M3 prime x probe matrix (the killer figure)
# ---------------------------------------------------------------------------

def figure_4() -> None:
    print("\n=== FIGURE 4: M3 12 x 12 prime x probe matrix "
          "(cell = recorded naming survival rate) ===")

    fig, axes = new_figure(1, 3, figsize=(13.4, 5.0))
    for ax, (subject, slug) in zip(axes, SUBJECTS):
        data = load("m3-matrix", slug)
        cells = data["matrix"]
        primes, probes = [], []
        for cell in cells:
            if cell["prime"] not in primes:
                primes.append(cell["prime"])
            if cell["probe"] not in probes:
                probes.append(cell["probe"])
        lookup = {(c["prime"], c["probe"]): c for c in cells}

        grid = [[lookup[(a, b)]["cell"]["rate"] for b in probes] for a in primes]
        ax.imshow(grid, cmap=SEQ, vmin=0.0, vmax=1.0, aspect="equal",
                  interpolation="nearest")

        print(f"\n  -- {subject} ({slug})   <- m3-matrix-{slug}.json : matrix")
        for i, prime in enumerate(primes):
            row_text = []
            for j, probe in enumerate(probes):
                cell = lookup[(prime, probe)]["cell"]
                hits, n, rate = cell["hits"], cell["n"], cell["rate"]
                label = f"{hits}/{n}" if n else "—"
                row_text.append(f"{probe}:{label}")
                colour = SURFACE if (rate is not None and rate < 0.45) else INK
                weight = "bold" if lookup[(prime, probe)]["is_diagonal"] else "normal"
                ax.text(j, i, label, ha="center", va="center", fontsize=6.4,
                        color=colour, fontweight=weight)
            print(f"     A = {prime:9s} | " + "  ".join(row_text))

        ax.set_xticks(range(len(probes)))
        ax.set_xticklabels(probes, rotation=60, ha="right", fontsize=7.2)
        ax.set_yticks(range(len(primes)))
        ax.set_yticklabels(primes, fontsize=7.2)
        ax.tick_params(colors=MUTED, length=0)
        for label in ax.get_xticklabels() + ax.get_yticklabels():
            label.set_color(INK_2)
        for side in ax.spines.values():
            side.set_visible(False)
        gated = data["pooled_arms"]["diagonal"]["n"]
        ax.set_title(f"{subject}{'  (off-gate)' if subject == '0.5B' else ''}"
                     f"   gated n = {gated}",
                     fontsize=9.5, color=SERIES[subject], loc="left", pad=8)
        if ax is axes[0]:
            ax.set_ylabel("deleted direction  A", fontsize=9, color=INK_2)
        ax.set_xlabel("probed concept  B", fontsize=9, color=INK_2)

    mappable = plt.cm.ScalarMappable(cmap=SEQ)
    mappable.set_clim(0.0, 1.0)
    bar = fig.colorbar(mappable, ax=axes, fraction=0.016, pad=0.015)
    bar.set_label("naming survival rate (recorded)", fontsize=8.5, color=INK_2)
    bar.ax.tick_params(colors=MUTED, labelsize=7.5)
    bar.outline.set_visible(False)

    fig.suptitle("A dark diagonal on a near-white grid: deleting A silences A "
                 "and spares B", fontsize=11, color=INK, x=0.005, ha="left", y=1.0)
    save(fig, "fig4-matrix.png")


# ---------------------------------------------------------------------------
# Figure 5 -- M4's three floor reads against the frozen 0.5 bar
# ---------------------------------------------------------------------------

def figure_5() -> None:
    print("\n=== FIGURE 5: M4 floor reads vs the pre-registered 0.5 bar "
          "(recorded Wilson 95%) ===")

    fig, ax = new_figure(figsize=(7.6, 4.2))
    style(ax)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=GRID, linewidth=0.8)

    READS = ["item-level\n(the gate)", "residual-conservative", "concept-level"]
    positions = {"0.5B": -0.26, "1.5B": 0.0, "3B": +0.26}

    for subject, slug in SUBJECTS:
        data = load("m4-strip", slug)
        sparing = data["vocabulary_sparing"]
        bar_value = sparing["bar"]
        reads = [("gate_arm", sparing["gate_arm"])]
        for entry in sparing["conservative_reads"]:
            reads.append((entry["read"], entry))
        print(f"\n  -- {subject} ({slug})   <- m4-strip-{slug}.json : "
              f"vocabulary_sparing")
        for idx, (name, cell) in enumerate(reads):
            rate = cell["rate"]
            lo, hi = cell["wilson_95"]
            x = idx + positions[subject]
            ax.errorbar(
                x, rate, yerr=[[rate - lo], [hi - rate]], fmt="o", markersize=6.5,
                elinewidth=1.6, capsize=0, color=SERIES[subject],
                markeredgecolor=SURFACE, markeredgewidth=1.6, zorder=3,
            )
            clears = "clears" if lo >= bar_value else "BELOW THE BAR"
            print(f"     {name:24s} {cell['k']:3d}/{cell['n']:<3d} = {rate:.4f} "
                  f"[{lo:.4f}, {hi:.4f}]   lower bound {clears} {bar_value}")

    bar_value = load("m4-strip", SUBJECTS[1][1])["vocabulary_sparing"]["bar"]
    ax.axhline(bar_value, color=INK_2, linewidth=1.2, zorder=2)
    ax.text(-0.5, bar_value + 0.02, f"pre-registered bar  {bar_value}",
            fontsize=8.5, color=INK_2, ha="left")

    ax.set_xticks(range(len(READS)))
    ax.set_xticklabels(READS, fontsize=8.5)
    ax.set_xlim(-0.55, len(READS) - 0.45)
    ax.set_ylim(0.0, 1.0)
    ax.set_ylabel("proportion surviving all 12 deletions\n(Wilson 95%)",
                  fontsize=9, color=INK_2)
    ax.set_title("Why the verdict carries AS-SCORED ONLY: one read clears the "
                 "bar, another does not", fontsize=10.5, color=INK, loc="left",
                 pad=12)
    handles = [
        Line2D([], [], marker="o", linestyle="none", markersize=6.5,
               color=SERIES[s], markeredgecolor=SURFACE, markeredgewidth=1.6,
               label=f"{s}{'  (off-gate)' if s == '0.5B' else ''}")
        for s, _ in SUBJECTS
    ]
    ax.legend(handles=handles, frameon=False, fontsize=8.5, loc="upper left",
              labelcolor=INK_2)
    fig.tight_layout()
    save(fig, "fig5-m4-floors.png")


# ---------------------------------------------------------------------------
# Figure 6 -- M4 collateral asymmetry: safe primes, fragile probes
# ---------------------------------------------------------------------------

def figure_6() -> None:
    print("\n=== FIGURE 6: M4 collateral asymmetry "
          "(per-prime row survival vs per-probe column survival) ===")

    gate_bearing = [s for s in SUBJECTS if s[0] != "0.5B"]
    fig, axes = new_figure(2, 2, figsize=(9.2, 6.2), sharex=True,
                           gridspec_kw={"width_ratios": [1, 2.2]})

    for (ax_primes, ax_probes), (subject, slug) in zip(axes, gate_bearing):
        data = load("m4-strip", slug)
        for ax in (ax_primes, ax_probes):
            style(ax)
            ax.set_axisbelow(True)
            ax.xaxis.grid(True, color=GRID, linewidth=0.8)

        rows = []
        for prime, profile in data["row_profiles"].items():
            cell = profile["collateral_non_subset"]
            rows.append((prime, cell["rate"], cell["hits"], cell["n"]))
        rows.sort(key=lambda item: item[1])

        columns = []
        for probe, profile in data["column_profiles"].items():
            cell = profile["fragility"]
            if not cell["n"] or not profile["gated_items"]:
                continue
            columns.append((probe, cell["rate"], cell["hits"], cell["n"],
                            profile["in_subset"]))
        columns.sort(key=lambda item: item[1])

        print(f"\n  -- {subject} ({slug})   deleted directions (rows), arm = the "
              f"gated non-subset items"
              f"   <- m4-strip-{slug}.json : row_profiles[*].collateral_non_subset")
        for prime, rate, hits, n in rows:
            print(f"     A = {prime:9s} {hits:3d}/{n:<3d} = {rate:.4f}")
        print(f"  -- {subject} probed concepts (columns), arm = the off-target "
              f"deletions of that concept"
              f"   <- m4-strip-{slug}.json : column_profiles[*].fragility")
        for probe, rate, hits, n, in_subset in columns:
            tag = "  (subset probe: 11 off-target deletions)" if in_subset else ""
            print(f"     B = {probe:11s} {hits:3d}/{n:<3d} = {rate:.4f}{tag}")

        n_rows, n_cols = len(rows), len(columns)
        untouched = sum(1 for c in columns if c[2] == c[3])
        print(f"     probes taking zero collateral: {untouched} of {n_cols}")

        ax_primes.plot([r[1] for r in rows], range(n_rows), "o", markersize=6.5,
                       color=SERIES[subject], markeredgecolor=SURFACE,
                       markeredgewidth=1.4, zorder=4)
        ax_probes.plot([c[1] for c in columns], range(n_cols), "s", markersize=4.4,
                       color=SERIES[subject], markeredgecolor=SURFACE,
                       markeredgewidth=1.0, zorder=4)

        # Selective direct labels: the three most fragile probes only, fanned
        # upward into empty space with hairline leaders so they cannot collide.
        for rank, (probe, rate, hits, n, _) in enumerate(columns[:3]):
            ax_probes.annotate(
                f"{probe}  {hits}/{n}", xy=(rate, rank),
                xytext=(9, 6 + 15 * rank), textcoords="offset points",
                fontsize=7.5, color=INK_2, va="center",
                arrowprops=dict(arrowstyle="-", color=AXIS, linewidth=0.7,
                                shrinkA=0, shrinkB=2),
            )
        worst_prime = rows[0]
        ax_primes.annotate(f"{worst_prime[0]}  {worst_prime[2]}/{worst_prime[3]}",
                           xy=(worst_prime[1], 0), xytext=(7, 0),
                           textcoords="offset points", fontsize=7.5, color=INK_2,
                           va="center")

        for ax, count, label in ((ax_primes, n_rows, "primes"),
                                 (ax_probes, n_cols, "probes")):
            ax.set_yticks([])
            ax.set_ylim(-1.5, count + 0.5)
        ax_primes.set_ylabel(f"{subject}\n{n_rows} deleted directions",
                             fontsize=8.5, color=SERIES[subject], fontweight="bold")
        ax_probes.set_ylabel(f"{n_cols} probed concepts", fontsize=8.5, color=INK_2)
        ax_primes.set_xlim(0.35, 1.06)
        if subject == gate_bearing[0][0]:
            ax_primes.set_title("what deleting A spares", fontsize=9.5, color=INK,
                                loc="left", pad=8)
            ax_probes.set_title("what B survives", fontsize=9.5, color=INK,
                                loc="left", pad=8)
        ax_probes.text(0.36, n_cols - 1,
                       f"{untouched} of {n_cols} probes take zero collateral",
                       fontsize=8.5, color=INK_2, va="top")

    for ax in axes[-1]:
        ax.set_xlabel("naming-survival rate (recorded)", fontsize=9, color=INK_2)
    fig.suptitle("Collateral concentrates on fragile probes, not on damaging primes",
                 fontsize=11, color=INK, x=0.005, ha="left", y=1.0)
    fig.tight_layout()
    save(fig, "fig6-collateral-asymmetry.png")


def main() -> None:
    print("mute-map — paper figures")
    print("Every value below is read from a committed file in results/; the only "
          "arithmetic\nis hits/n where a file records the pair rather than the rate.")
    figure_1()
    figure_2()
    figure_3()
    figure_4()
    figure_5()
    figure_6()
    print("\nDone. 6 figures written to docs/paper/.")


if __name__ == "__main__":
    main()

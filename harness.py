"""harness.py — shared measurement conventions (D2 port).

The remaining pieces the M0 anchor re-run imports, each ported verbatim from
its dim-stage home (commit e6c10b9); the source module is cited per item:

- `fail_invalid`, `FROZEN_BANDS`            — dim-stage `m0_readability_gate.py`
- `proportional_band`                        — dim-stage `readability.py`
- `token_forms`, `encode_chat`, `output_logits` — dim-stage `m1_verbal_report.py`
- `READBACK_TOL`, `MIN_N`, `COLLAPSE_SHARE`, `degeneracy`, `rate_cell`
                                             — dim-stage `s3_selectivity.py`
"""
from __future__ import annotations

from collections import Counter
from contextlib import nullcontext

import torch

from intervention import Edit, edit_residuals
from stats import wilson
from subject import SubjectModel, _record_residuals

#: Frozen D2 bands (dim-stage M0-BRIEF): proportional 38–92% of depth.
#: 36-layer entry (Qwen2.5-3B-Instruct) pre-registered 2026-07-15, before the
#: 3B fit or any 3B readout existed — the escalation trigger (both subjects
#: NULL) fired and Kyle chose to escalate; see dim-stage DECISIONS.md.
FROZEN_BANDS = {
    24: list(range(9, 22)),
    28: list(range(11, 25)),
    36: list(range(14, 33)),
}

READBACK_TOL = 1e-4  # relative |⟨v, h'⟩| / (‖v‖·‖h‖) ceiling, fp32 headroom
MIN_N = 20
COLLAPSE_SHARE = 0.5  # S1/S2 degeneracy convention


def fail_invalid(reason: str) -> None:
    print(f"VERDICT: INVALID — {reason}")
    raise SystemExit(2)


def proportional_band(n_layers: int) -> list[int]:
    """The frozen D2 band: layer l is in the workspace band iff
    0.38 <= l/(n_layers-1) <= 0.92 (the paper's percentage depth transplanted)."""
    return [
        l for l in range(n_layers) if 0.38 <= l / (n_layers - 1) <= 0.92
    ]


def token_forms(word: str, tokenizer) -> list[int]:
    """Single-token ids for `word` — M0's {`w`, `␣w`} convention, kept *ordered*
    (bare form first) so the swap token can prefer the bare form, the shape an
    answer takes right after the chat template's trailing newline. Grading uses
    the min over all forms, so order never changes a rank."""
    ids: list[int] = []
    for variant in (word, " " + word):
        enc = tokenizer(variant, add_special_tokens=False).input_ids
        if len(enc) == 1 and enc[0] not in ids:
            ids.append(enc[0])
    return ids


def encode_chat(subject: SubjectModel, text: str) -> torch.Tensor:
    """One user turn through the tokenizer's own chat template, generation
    prompt appended — the frozen D5 prompt construction."""
    input_ids = subject.tokenizer.apply_chat_template(
        [{"role": "user", "content": text}],
        add_generation_prompt=True,
        return_tensors="pt",
        return_dict=False,  # the bare [1, seq] tensor, not a BatchEncoding
    )
    return input_ids.to(subject._input_device)


def output_logits(
    subject: SubjectModel, input_ids: torch.Tensor, edits: dict[int, Edit] | None = None
) -> torch.Tensor:
    """The model's next-token logits at the final prompt position — the actual
    output distribution (final-layer residual, unembedded), not a lens readout —
    with the band edits active if given."""
    final_layer = subject.n_layers - 1
    with torch.no_grad(), (
        edit_residuals(subject.layers, edits) if edits else nullcontext()
    ):
        with _record_residuals(subject.layers, [final_layer], graph_root=None) as res:
            subject.forward(input_ids)
        return subject.unembed(res[final_layer][0, -1].float()).float().cpu()


def degeneracy(greedy_ids: list[int], tokenizer) -> dict:
    """S1/S2 guard for one condition cell: most common greedy token's share."""
    if not greedy_ids:
        return {"attractor_token": None, "share": 0.0, "collapsed": False}
    token, count = Counter(greedy_ids).most_common(1)[0]
    share = count / len(greedy_ids)
    return {
        "attractor_token": tokenizer.decode([token]),
        "share": share,
        "collapsed": share >= COLLAPSE_SHARE,
    }


def rate_cell(k: int, n: int) -> dict:
    lb, ub = wilson(k, n)
    return {
        "hits": k, "n": n, "rate": k / n if n else None,
        "wilson_95": [lb, ub], "underpowered": n < MIN_N,
    }

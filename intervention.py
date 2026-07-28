"""intervention.py — the projection-removal (ablation) operator subset (D2 port).

Ported verbatim from dim-stage `intervention.py` (commit e6c10b9), cut down to
exactly what the M0 anchor re-run exercises: `jlens_vector`, `ablate`,
`edit_residuals`, and the `Edit` type. The steering, swap, and positional
operators stay behind in dim-stage until a milestone needs them (M2's
partial-strength operator will be designed in M2's own brief) — every ported
line is a line the anchor gate certifies.

The operators, verbatim from the paper (dim-stage M1-BRIEF, "Design extraction"):

- **J-lens vector**: `v_t = J_lᵀ u_t`, token t's direction in the layer-l residual
  stream, where `u_t` is token t's row of the unembedding matrix. The lens logit
  for t is (approximately) `⟨v_t, h⟩`. Frozen convention: `u_t` is the raw
  `lm_head.weight` row — the literal formula reading; the final RMSNorm's
  elementwise scale sits between the residual and that matrix in Qwen and is NOT
  folded in (owned, pre-declared; dim-stage DECISIONS.md 2026-07-16).
- **Ablation** (S3, D24): `h ← h − V†-projection of h onto span{v_1..v_k}` —
  remove the residual's component along a set of lens directions entirely,
  leaving every selected direction's lens coordinate at exactly zero and the
  orthogonal complement untouched.

Application point: edits replace a block's **output** residual — the same hook
point `subject._record_residuals` captures and the lens reads — so every later
layer (and the final unembedding) consumes the edited stream.
"""
from __future__ import annotations

from collections.abc import Callable, Sequence
from contextlib import contextmanager

import torch
from torch import nn

#: Relative residual floor for the ablation projection's Gram-Schmidt basis:
#: a direction whose component orthogonal to the already-accepted basis falls
#: below this fraction of its own norm is numerically inside their span and
#: is dropped from the basis (its coordinate is removed by the others).
RANK_TOLERANCE = 1e-10

Edit = Callable[[torch.Tensor], torch.Tensor]


def jlens_vector(jacobian: torch.Tensor, unembed_row: torch.Tensor) -> torch.Tensor:
    """v_t = J_lᵀ u_t: the [d_model] residual-stream direction for one token."""
    return jacobian.T @ unembed_row


def ablate(h: torch.Tensor, directions: torch.Tensor) -> torch.Tensor:
    """h minus its projection onto span{directions}: the S3 ablation operator
    (D24). h is [..., d_model]; directions is [..., k, d_model] with matching
    leading dims (each position carries its own direction set). Returns the
    unique minimal-norm edit of h whose inner product with every direction is
    zero — "zero out the residual stream's projection onto each" achieved
    simultaneously, which one-at-a-time zeroing of non-orthogonal directions
    would not do (S3-BRIEF, design extraction).

    Computed by modified Gram-Schmidt with re-orthogonalization on CPU in
    float64. Real top-k lens direction sets are brutally ill-conditioned —
    near-duplicate tokens (including Qwen's untrained reserved vocab slots)
    give nearly identical directions, where a least-squares solve blows up
    and LAPACK's iterative SVD refuses to converge; S3's first smoke runs
    tripped the runtime read-back / crashed on exactly those. MGS never
    iterates: each direction is orthogonalized against the accepted basis
    (twice — the classical fix for cancellation) and dropped if nothing new
    survives, so numerically dependent directions land inside the kept span
    and every selected direction's coordinate still ends at ~0. k = 0 is an
    exact no-op.
    """
    if directions.shape[-2] == 0:
        return h
    # Move BEFORE casting: `.to("cpu", float64)` in one step silently corrupts
    # values coming off MPS (float64 is cast device-side, unsupported there —
    # measured 2026-07-17, max abs diff ~5 on unit-scale data).
    v = directions.cpu().to(torch.float64)  # [..., k, d_model]
    b = h.cpu().to(torch.float64)
    basis: list[torch.Tensor] = []
    for i in range(v.shape[-2]):
        vec = v[..., i, :]
        norm0 = vec.norm(dim=-1, keepdim=True)
        for _ in range(2):
            for q in basis:
                vec = vec - (vec * q).sum(-1, keepdim=True) * q
        norm = vec.norm(dim=-1, keepdim=True)
        keep = norm > norm0 * RANK_TOLERANCE
        basis.append(
            torch.where(keep, vec / norm.clamp_min(torch.finfo(vec.dtype).tiny), 0.0)
        )
    for q in basis:
        b = b - (b * q).sum(-1, keepdim=True) * q
    return b.to(device=h.device, dtype=h.dtype)


@contextmanager
def edit_residuals(layers: Sequence[nn.Module], edits: dict[int, Edit]):
    """Apply each edit to its block's output residual on every forward pass run
    inside the context — the write-side mirror of `subject._record_residuals`:
    same hook point (block output), so the edited residual is exactly what the
    lens would read there and what every later layer consumes. A recording hook
    registered *inside* this context sees the edited stream (torch runs forward
    hooks in registration order, each receiving the previous one's replacement).
    """
    handles = []

    def make_hook(edit: Edit):
        def hook(module, inputs, output):
            if torch.is_tensor(output):
                return edit(output)
            return (edit(output[0]), *output[1:])

        return hook

    try:
        for index, edit in edits.items():
            handles.append(layers[index].register_forward_hook(make_hook(edit)))
        yield
    finally:
        for handle in handles:
            handle.remove()

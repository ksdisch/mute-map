"""subject.py — the SubjectModel wrapper + residual-recording hook (D2 port).

Ported verbatim from dim-stage `fitter.py` (commit e6c10b9): the two pieces the
M0 anchor re-run needs — `SubjectModel` (a HuggingFace causal LM wrapped down to
the residual stack the lens reads) and `_record_residuals` (the forward hook that
captures a block's output residual — the exact hook point the lens reads and the
intervention writes). The fitting machinery itself (Jacobian estimation) is NOT
ported: mute-map never refits lenses for the core chain (KICKOFF K3).
"""
from __future__ import annotations

from collections.abc import Sequence
from contextlib import contextmanager

import torch
from torch import nn


class SubjectModel:
    """A HuggingFace causal LM wrapped down to what the fitter needs.

    Expects the modern Llama/Qwen layout: `hf.model.layers` (the residual blocks),
    `hf.model.norm` (final pre-unembed norm), `hf.model.embed_tokens`, `hf.lm_head`.
    Both dim-stage subjects (Qwen2.5-0.5B/1.5B-Instruct) use it; anything else
    fails loudly rather than guessing.

    Mutates the model in place: eval mode, every parameter frozen
    (`requires_grad=False`) — the fit differentiates with respect to *activations*,
    never weights, and frozen weights let one captured activation root the whole
    autograd graph (see `_record_residuals`).
    """

    def __init__(self, hf_model: nn.Module, tokenizer) -> None:
        decoder = getattr(hf_model, "model", None)
        for attr in ("layers", "norm", "embed_tokens"):
            if decoder is None or not hasattr(decoder, attr):
                raise ValueError(
                    f"{type(hf_model).__name__} lacks model.{attr}; "
                    "SubjectModel only supports the Llama/Qwen layout"
                )
        if not hasattr(hf_model, "lm_head"):
            raise ValueError(f"{type(hf_model).__name__} lacks lm_head")
        softcap = getattr(hf_model.config.get_text_config(), "final_logit_softcapping", None)
        if softcap is not None:
            raise ValueError("logit softcapping not implemented (not a Qwen2.5 feature)")

        hf_model.eval()
        for param in hf_model.parameters():
            param.requires_grad_(False)
        # Reference parity: instruction-tuned checkpoints sometimes ship
        # add_bos_token=False; the reference forces it on when a BOS exists.
        # (Qwen2.5 has no BOS token, so this is a recorded no-op for our subjects.)
        if getattr(tokenizer, "bos_token_id", None) is not None and hasattr(
            tokenizer, "add_bos_token"
        ):
            tokenizer.add_bos_token = True

        self._decoder = decoder
        self.tokenizer = tokenizer
        self.layers: nn.ModuleList = decoder.layers
        self._final_norm = decoder.norm
        self._lm_head = hf_model.lm_head
        self._input_device = decoder.embed_tokens.weight.device
        text_config = hf_model.config.get_text_config()
        self.n_layers: int = text_config.num_hidden_layers
        self.d_model: int = text_config.hidden_size

    def encode(self, text: str, *, max_length: int = 512) -> torch.Tensor:
        """Tokenize to input_ids [1, seq_len] on the model's input device."""
        encoded = self.tokenizer(
            text, return_tensors="pt", truncation=True, max_length=max_length
        )
        return encoded.input_ids.to(self._input_device)

    def forward(self, input_ids: torch.Tensor) -> None:
        """Run the residual stack only (no unembedding — the fit never needs logits)."""
        self._decoder(input_ids=input_ids, use_cache=False)

    def unembed(self, residual: torch.Tensor) -> torch.Tensor:
        """Residual [..., d_model] -> logits [..., vocab]: final norm + LM head."""
        weight = self._lm_head.weight
        return self._lm_head(self._final_norm(residual.to(weight.dtype).to(weight.device)))


@contextmanager
def _record_residuals(layers: Sequence[nn.Module], at: Sequence[int], *, graph_root: int | None):
    """Capture each listed block's output residual on the next forward pass.

    Yields a dict that fills with {block index: residual tensor} as the forward
    runs. Tensors are NOT detached, so torch.autograd.grad can differentiate
    through them. If `graph_root` is given, that block's output is flipped to
    requires_grad=True as it is produced — with all weights frozen it is the
    only graph leaf, so autograd retains the graph from that block onward only
    (the memory trick that makes MPS fitting feasible).
    """
    captured: dict[int, torch.Tensor] = {}
    handles = []

    def make_hook(index: int):
        def hook(module, inputs, output):
            residual = output if torch.is_tensor(output) else output[0]
            if index == graph_root:
                residual.requires_grad_(True)
            captured[index] = residual

        return hook

    indices = sorted(set(at) | ({graph_root} if graph_root is not None else set()))
    try:
        for index in indices:
            handles.append(layers[index].register_forward_hook(make_hook(index)))
        yield captured
    finally:
        for handle in handles:
            handle.remove()

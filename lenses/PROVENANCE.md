# Lens artifact provenance (D1)

The fitted Jacobian-lens artifacts are copied from local dim-stage
(`~/Projects/dim-stage/lenses/`, working tree at commit `e6c10b9`), never refit
for the core chain (KICKOFF K3). They were fitted by dim-stage's `fitter.py`
(n_prompts = 100, WikiText prompts; 0.5B/1.5B on local MPS, 3B on a rented RTX
4090 — dim-stage `docs/DECISIONS.md`). The `.pt` files are gitignored; this
record is the tracked fingerprint. Verify after any copy with
`shasum -a 256 lenses/*.pt`.

| File | SHA256 |
|---|---|
| `qwen2.5-0.5b-instruct-n100.pt` | `ffd6c99098380320cc05d132340651dbd5e67392e8ef94bb88ad267b600963ce` |
| `qwen2.5-1.5b-instruct-n100.pt` | `05143b6438743123d51e11c78d3fbc6aece74c1783b0bb1f2ae050413e60080f` |
| `qwen2.5-3b-instruct-n100.pt` | `e8b922ae747c58229c91083b373ec658f7bef401eff333f6a9cca774a4551b2d` |

Regeneration (if a copy is ever lost): dim-stage `fitter.py`, e.g.
`uv run python fitter.py --model-id Qwen/Qwen2.5-0.5B-Instruct --n-prompts 100`
in the dim-stage repo (3B needs CUDA — see dim-stage `remote-fit-3b.sh`), then
re-verify the SHA256 above. A hash mismatch after refitting means a different
environment produced a different fit — that lens is NOT the anchor instrument;
M0's gate must re-run before it is used.

## Companion frozen inputs (tracked in this repo)

| File | SHA256 | Source |
|---|---|---|
| `items/s4-avoidance-items.json` | `1a8fb210ee89b682f32e0425b592d31c8c248b7f58fabd65bc059e9377b0d7a5` | dim-stage frozen D27c item set (2026-07-17) |
| `anchors/s4-avoidance-qwen2.5-0.5b-instruct.json` | `fe4085d028220b018ab9a3f507d51cea128080c5c64212f8432f37123a63b6fe` | dim-stage recorded S4b results, commit `e6c10b9` |
| `anchors/s4-avoidance-qwen2.5-1.5b-instruct.json` | `4b3278d46a991e8e69fd4bbd00e17b9f64f9b2bf52e60a7b1d3b32d49541388a` | dim-stage recorded S4b results, commit `e6c10b9` |
| `anchors/s4-avoidance-qwen2.5-3b-instruct.json` | `e05719d36524080477cc6c941581363ed1bc967d53e089ddcdd9fe2d512bcb12` | dim-stage recorded S4b results, commit `e6c10b9` |

Environment pins that the bit-for-bit anchor gate depends on: `torch==2.13.0`,
`transformers==5.13.1` (dim-stage's uv.lock at anchor time — see
`pyproject.toml`).

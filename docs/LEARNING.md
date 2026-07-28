# LEARNING.md — teaching notes, stage by stage

Plain-English notes on the ideas each stage turned on, per the teaching
standard: every jargon term defined where it first matters.

## M0 — port + anchor gate (2026-07-27)

**What "porting" actually risks.** Copying code between repos feels safe, but a
measurement instrument is code + data + environment. M0 treated all three as
suspects: the code was ported verbatim with each function's source cited, the
data (lenses, items, anchor results) was copied with **SHA256 fingerprints** (a
cryptographic hash — a short string that changes if even one byte of the file
changes, so a match proves the copy is exact), and the environment was **pinned**
(exact library versions written into `pyproject.toml` instead of ranges).

**Why version pins mattered here.** A fresh dependency resolve gave
`transformers 5.14.1`; dim-stage's recorded runs used `5.13.1`. A minor library
bump can legitimately change floating-point kernels — same math, slightly
different rounding — which can flip a borderline greedy choice. Pinning to
dim-stage's exact versions is why M0 didn't just match the discrete outcomes:
every softmax probability reproduced to the last bit (840/840 cells × 3
subjects). "Bit-for-bit" stopped being aspiration and became an observation.

**Determinism is the lever that makes a hard gate fair.** Every readout in this
lineage is **greedy decoding** (always take the single highest-probability next
token — no sampling, no randomness). Deterministic readouts mean the correct
expectation for a faithful port is *exact equality*, so the gate can demand 0
mismatches and any deviation is a real defect, not noise. With sampled outputs,
no such gate could exist.

**The anchor-gate pattern.** Before measuring anything new with a moved
instrument, re-run an experiment whose answer you already recorded and demand
the identical result. It's the lab-science habit of calibrating a scale with a
known weight. The gate was frozen as code — comparison fields, INVALID
semantics, wording — *before* the first comparison ran, so a mismatch couldn't
be rationalized after the fact.

**What the gate certifies — and what it doesn't.** PASS means the ported
operator, band conventions, prompt construction, grading, and environment are
the same instrument that produced S4b. It does *not* re-argue whether S4b's
finding is interesting or its gate wording was right — those are settled
records. M0 transfers trust; it doesn't mint it.

**One number worth keeping.** The whole three-subject certification — 2,520
compared cells — ran locally on the laptop's GPU (MPS), forward passes only,
for $0. Ablation (deleting a direction) needs no gradients; only lens *fitting*
does, which is why the 7B stretch is the only line item with a budget.

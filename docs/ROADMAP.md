# ROADMAP.md — mute-map v1

Chain per `KICKOFF.md`; a stage isn't done until its spine updates (this file,
`DECISIONS.md`, `LEARNING.md`, the stage brief's results section) are committed
with the code.

| Stage | Question | Gate (pre-committed) | Status |
|---|---|---|---|
| **M0 — port + anchor** | Is the ported instrument the same instrument? | Bit-for-bit vs dim-stage's recorded S4b JSONs, ×3 subjects (D3) | **PASSED** (2026-07-27: 0 mismatches over 840 cells per subject; concept_mass floats exact 840/840 ×3; see M0-BRIEF results) |
| **M1 — breadth** | How much of the measurable vocabulary has an off-switch? | Pooled primed_late < control_late naming, CI-clean at 1.5B AND 3B | **PASSED** (2026-07-28: BREADTH-SPECIFIC at both gate-bearing subjects — 1.5B +0.656 [+0.517,+0.763], 3B +0.636 [+0.443,+0.759]; 0.5B also +0.447 [+0.275,+0.603] off-gate; anchor cross-check re-certified bit-for-bit on all three runs; see M1-BRIEF results) |
| M2 — localization + dose | Where does the switch live; how much removal does it take? | Late-window effect CI-cleanly > early and middle, pooled | pending (brief first) |
| M3 — specificity matrix | Diagonal suppression vs off-diagonal collateral | Diagonal > off-diagonal CI-clean at 1.5B AND 3B | pending (brief first) |
| S1 — scale (stretch) | Does specificity keep sharpening at 7B? | descriptive; 7B lens fit ≤ $15 on rented GPU | optional |
| S2 — scope (stretch) | Token mute button or concept mute button? | descriptive; frozen alt-form lists | optional |

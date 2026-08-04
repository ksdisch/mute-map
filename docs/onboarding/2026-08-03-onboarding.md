# Onboarding — mute-map — 2026-08-03

Status: partial (in progress) · Lineup tour: undecided

## 1. Welcome & the mission

**Who we are.** A reproduce-and-measure shop. We take claims about how AI systems
fail, and we measure them honestly at a scale one person can own end to end. Eight
projects, seven public repos, two lanes.

**The two lanes.**
- *Agent reliability* — take a recent failure-mode paper (often days-to-weeks old,
  often shipping no code), reproduce that specific failure on cheap small models.
  `forge-gap`, `decay-pin`, `lossy-wall`, `ghost-patch`, `blind-cite`.
- *Model internals* — same discipline pointed inward: rebuild a published
  instrument, validate it bit-for-bit against the authors' reference, then use it
  to map and audit small models from the inside. `dim-stage` → `mute-map` →
  `hush-gauge`.

**The charter (`~/Projects/portfolio/METHODOLOGY.md`), five points:**
1. Pick a recent failure-mode paper describing a nameable *primitive*.
2. Reproduce a narrow slice on cheap models at hobby scale, hard budget guard,
   typically < $5 tracked to the cent.
3. Pre-commit the statistics — scoring script written and dry-run before the paid
   data exists; Wilson interval on every arm, Newcombe on every difference;
   overlapping intervals are reported as nulls; wrong-arm input exits `INVALID`.
4. Judge-free deterministic oracles — exact-match / ground-truth / token-ownership.
   Never an LLM judge.
5. State the narrow honest delta; nulls are headlines. Two projects headline nulls
   on purpose.

**The credibility argument** is what the method *refuses*: no self-graded homework
(no LLM judge), no moving goalposts (pre-registration), no hiding misses (nulls as
headlines).

**The anchor ladder** — three projects don't start from a paper, each one step
further out: `forge-gap` reproduces a technique with no arXiv paper; **`mute-map`
anchors on our own prior recorded result** (`dim-stage`'s S4b stage) — no external
number to check against; `hush-gauge` goes furthest, an original question with no
prior recorded result at all. What replaces the external check, every time: gates
frozen as code before any run, plus bit-for-bit re-certification of the instrument.


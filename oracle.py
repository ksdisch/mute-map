"""oracle.py — the D9(b) readout rule, frozen as code before any M2 run.

**What this module is.** The *oracle* is the rule that decides whether the model
"said the word". Through M0 and M1 that rule was: the single highest-probability
next token (the "greedy first token") is one of the concept's single-token
spellings, case-exact. M2 widens it, once, by decision D9(b) — and this module
is the whole of that widening, so the rule lives in exactly one place and cannot
drift between the M1 reanalysis (`m1_rescore.py`) and the M2 runner
(`m2_depth.py`), the two consumers that must apply an identical rule.

**Why a shared module rather than a cut copy.** The project's standing rule is
that each milestone's runner is *cut* from its predecessor rather than importing
it, so a certified file is never edited to serve a later stage. That rule
protects certified measurement code from edits; it is not a reason to duplicate
a rule whose entire purpose is to be byte-identical in two places. A divergence
between two copies of this rule would silently make the reanalysis and the M2
map incomparable — precisely the failure the single module forecloses. Owned as
a deviations-table row in `docs/M2-BRIEF.md`.

**The rule (D9b, frozen).** The model produced the concept iff the decoded
first-3-greedy span — already recorded for every M1 cell, and long enough for
every roster word (the longest bare form anywhere is 3 tokens: beetle,
butterfly, trumpet) — after stripping leading whitespace, **opens with the
concept's spelling at a word boundary, case-insensitive**.

Three consequences, each deliberate:

- *Prefix, not containment.* "not France" is a miss (the span does not open with
  it). Containment would let a control arm score a hit for a negated answer,
  which inflates the contrast — the one bias direction this project never
  accepts (the rejected D9(c)).
- *Word boundary.* "Marseille" is not Mars. The boundary test is "the next
  character is not a letter or digit", so punctuation, whitespace, and the chat
  template's own `<|im_end|>` all close a word.
- *End of span counts as a boundary* (PR #5 review F5). A word that exactly
  fills the recorded 3-token span ("Butterfly") is a **hit**: truncation must
  never turn a completed word into a miss. This is not a free choice — it is the
  reading every projection and pre-registered n in `docs/M2-BRIEF.md` was
  computed under, and exactly six recorded M1 cells distinguish the two
  readings, two of them on a control arm (pinned below in
  `SPAN_FILL_TEST_CASE`).

**The owned residual** (PR #5 review F12, restated at F14). Because the span is
truncated at 3 tokens, for the three concepts whose bare form *fills* it the
closing boundary is unobservable: "Beetlejuice" tokenizes as
['Be','et','le','ju','ice'], so its recorded span decodes to exactly 'Beetle'
and is scored as a hit for beetle. Six recorded M1 cells fill the span this way
(beetle-1, butterfly-1 ×2 arms, trumpet-3 — the cells that also decide the
span-end reading above). Each is a completed word on inspection, and each is the
item's own intended answer; what the truncated recording *cannot* do is rule out
a longer continuation. So the residual is **owned, not excluded** — none of the
three concepts is in M2's subset, and the accepted behaviour is pinned by its
own unit-test case rather than left implied.

**Still a deterministic oracle.** Greedy decoding is deterministic and this is a
fixed string comparison on that deterministic span, frozen as code with unit
tests — never free-text parsing, never an LLM judge (CLAUDE.md's standing
guardrail). The first-token outcome is recorded beside every cell regardless, so
anchor- and M1-comparability never degrade.
"""
from __future__ import annotations

import re

#: The span the rule reads: the project's standing secondary-texture readout,
#: promoted to the primary oracle by D9(b). 3 tokens >= the longest bare form.
SPAN_TOKENS = 3

#: A word continues only through letters and digits; everything else — spaces,
#: punctuation, the chat template's `<|im_end|>`, and the end of the span —
#: closes it.
_BOUNDARY = r"(?![A-Za-z0-9])"

#: The named case that decides the span-end reading (review F5), taken verbatim
#: from a recorded M1 cell: `butterfly-1 / control_late` at 1.5B and at 3B.
#: Under "end of span is a boundary" it is a hit; under the strict reading it
#: would be a miss, and the brief's pre-registered ns would all be wrong.
SPAN_FILL_TEST_CASE = ("Butterfly", "butterfly", True)

ORACLE_WORDING = (
    "D9(b), frozen 2026-07-28 before any M2 run. PRIMARY READOUT: the concept "
    "is produced iff the decoded first-3-greedy span, after stripping leading "
    "whitespace, opens with the concept's spelling at a word boundary, "
    "case-insensitive — a prefix rule, never containment ('not France' is a "
    "miss), with the word boundary defined as 'the next character is not a "
    "letter or digit' ('Marseille' is not Mars) and the END OF THE SPAN "
    "counting as a boundary (review F5: a word that exactly fills the recorded "
    "span, 'Butterfly', is a hit — truncation must never turn a completed word "
    "into a miss). Case-insensitive because orthography is not semantics: "
    "'Piano' is the word piano, and the widening is measured to do real work "
    "(1.5B prefix gate 72 case-exact -> 105 case-insensitive). This is a fixed "
    "string rule on a deterministic greedy span, frozen as code with unit "
    "tests — never free-text parsing and never an LLM judge. S4's 'The ...' "
    "miss-counting caveat is UNCHANGED in kind and still owned: 'The France' "
    "remains a miss. The first-token outcome is computed and recorded beside "
    "every cell, so every cross-check against M0/M1 artifacts compares raw "
    "recorded fields and is oracle-independent. OWNED RESIDUAL (review F12): "
    "for the three concepts whose bare form fills the 3-token span (beetle, "
    "butterfly, trumpet) the closing boundary is unobservable, so a longer "
    "word sharing those tokens would score as a hit ('Beetlejuice' truncates to "
    "exactly 'Beetle'). Six recorded M1 cells fill the span this way; each is a "
    "completed word on inspection and is the item's own intended answer, but "
    "the truncated recording cannot rule out a longer continuation, so the "
    "residual is owned rather than excluded. None of the three concepts is in "
    "M2's subset."
)


def says_concept_prefix(span: str, concept: str) -> bool:
    """The D9(b) oracle: does `span` open with `concept` at a word boundary?

    `span` is the decoded first-3-greedy continuation exactly as recorded in the
    results JSONs (leading whitespace and the chat template's end marker
    included); `concept` is the roster spelling. Pure, deterministic, and the
    only definition of "the model said the word" M2 uses.
    """
    return re.match(re.escape(concept) + _BOUNDARY, span.lstrip(), re.IGNORECASE) is not None


def says_concept_anywhere(span: str, concept: str) -> bool:
    """The rejected D9(c) containment reading, kept as **texture only** — this is
    M1's recorded `says_concept_in_3` field, reproduced here so the reanalysis
    can report all three readings side by side. Never gating, never a verdict.
    """
    return concept.lower() in span.lower()

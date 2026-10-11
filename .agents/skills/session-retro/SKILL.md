---
name: session-retro
description: Retro of a work session from its real transcript, not from memory. Measures loops and rework with a deterministic extractor (make retro ID=<id>) and looks for five things: practices worth standardizing, stale instructions, gates with false positives, process friction and unrecorded debt. Applies NOTHING: it proposes, the human decides, what is approved goes through a PR. "Nothing to standardize" is a legitimate result. Use when the user says "/session-retro", "do a retro", "did we go in circles?", "any meta-improvements?".
argument-hint: [session id; defaults to the current one, taken from the scratchpad path]
---

# /session-retro — what deserves to survive this turn

The agent is the worst source about the loops it went through: it remembers its conclusion, not its path. That is
why you start by measuring.

## Procedure
1. **Locate the transcript by id**, never "the most recent" (with concurrent sessions that is a measured race
   condition). The id is in the scratchpad path (`…/<id>/scratchpad`).
2. **Measure before opining**: `make retro ID=<id>`. Returns a tool histogram, skills loaded (`NONE` with code
   edits is a finding), gates run, repeated commands, files re-read 3+ times, hook blocks. **Declared blind spot**:
   what Bash wrote (cat, sed, heredoc) does not count as an edit; the real data is in `git diff --name-only`.
3. **Read `memory/meta-improvements.md`** before proposing: a rejected proposal does not come back without new
   evidence.
4. **Five lenses**, each with the evidence that turns it into a finding rather than an impression:
   loops and rework · practice worth standardizing (and not written anywhere today) · stale instruction (quote + the
   fact that refutes it) · gate with a false positive or negative (**priority**: a gate that shouts too much teaches
   people to ignore it) · delivery friction.
5. **Triage with a high bar**: would it happen again? would the change have prevented it or does it just document
   it? is there already a rule that was not followed? Then the problem is the **gate**, not the rule: writing it
   again fixes nothing.
6. **Human gate and only then a PR** (`improve/<slug>`, never self-merge). Record adoptions **and rejections** in
   `memory/meta-improvements.md`.

> "Nothing to standardize" is a legitimate and frequent result. A retro forced to find something manufactures
> friction.

---
name: epe-4-review
description: INDEPENDENT adversarial review of an EPE change (branch or PR). Fan-out of parallel finders, one per lens (correctness/house style, security and privacy, criteria compliance against evidence.md, non-functional constraints, tests), merge + dedupe, independent validators that reproduce each finding, loop until a dry round, human gate, idempotent PR comments. Edits NOTHING. Use when the user says "/epe-4-review", "review the PR", "adversarial review", "fresh eyes".
argument-hint: [change path or PR number; defaults to .epe/active + current branch]
---

# /epe-4-review — the artifact is guilty until it proves it meets the criteria

The author is the worst person to review their own work: they know their intent and rationalize the gaps. Here
independent agents attack and **the human decides**.

## Flow
DoD → finders (parallel, one lens each) → merge+dedupe → validators (parallel, reproduce) → loop-until-dry
→ human gate → `/epe-5-apply` → record in `memory/closed.md`.

## 0. Before launching anything (you, cheap)
- Locate the change and read `story.md`, `plan.md`, `evidence.md`.
- **Walk the /epe-3-execute DoD**: one row per criterion in evidence? truly green with numbers? validation.md?
  journal? Each ✗ is a high-signal lead. Measured at origin: 14 of 21 findings fell on an unhonored DoD item.
- Deterministic layer: project gates, lint, `git diff <base>...<branch> --stat`.
- Read `memory/closed.md`: **it is injected literally** into every finder and validator (`guard-review-brief.py`
  blocks a review subagent that does not carry it; escape: `NO-CLOSED: <reason>`).

## 1. Brief (one file, travels literally in every prompt)
Diff or file list; `story.md` (the criteria are the contract); `plan.md` (scope = scope-in/out); `closed.md`; the
lens rules. Does **not** include the author's justifications. Save it in the scratchpad and state its path. Measure
its size: whatever is surplus is paid N finders × R rounds.

## 2. Lenses (parallel finders, read-only, one Agent call each in the same message)
| Lens | Contract it attacks |
|---|---|
| F-House | project conventions and style (AGENTS.md, cited guides) |
| F-Security | secrets, permissions, unvalidated inputs, privacy and confidentiality |
| F-Criteria | each criterion in story.md vs what evidence.md demonstrates; tests that test what they claim |
| F-Constraints | platform, performance, licenses, language, accessibility |
| F-Tests | tests that call real services, skips, logs with ERROR, reintroduced debt |
| F-Substance (content) | primary sources, [VERIFIED] vs [OPINION], the record rules, citers |

Each finder returns: severity, `file:line`, claim, rule violated, concrete failure scenario, scope-in/out,
confidence, lens, **and a mandatory "withdrawn as already-triaged" section** (even if empty).

## 3. Merge + dedupe (you). Same `file:line` from two lenses → one entry.

## 4. Validators (parallel; agents distinct from the finders, without their reasoning)
One per touched file + one cross-cutting. They reproduce each finding. They classify confirmed / false positive /
doubtful / already-triaged and return the discard pile **with reasons**. Reproduce through the user's real path.

## 5. Loop-until-dry. Another round over the files still dirty until one comes out dry. Report rounds:
"a single round does not prove there is nothing; it proves that round did not see it".

## 6. Delivery to the human (in two beats)
1. Count table file × class. 2. Detail grouped by file with recommendation and how it was verified.
Appendix: discarded, already-triaged, coverage gaps. **You edit nothing.**

## 7. Traceability in the PR (if there is a PR and `gh` works)
One FINDER comment and one VALIDATOR comment, idempotent by marker (`<!-- review-agent: finder -->`,
`<!-- review-agent: validator -->`): if it exists, edit instead of duplicating. Honest header: "automated adversarial
review", "verified by reproduction". The orchestrator publishes, not the subagents.

## 8. After the gate
Approved → `/epe-5-apply`. Rejected/frozen/deferred → a row in `memory/closed.md` **before closing**, in the same
commit as the journal entry.

## Definition of Done
- [ ] /epe-3-execute DoD walked; deterministic layer run.
- [ ] `closed.md` traveled literally; brief saved and its path stated.
- [ ] Lenses partitioned, finders in parallel, no author justifications.
- [ ] Dedupe before validating; distinct validators, by reproduction, with a discard pile.
- [ ] Convergence reported per file; delivery in two beats; nothing edited; explicit human gate.
- [ ] PR comments (or their omission announced); `closed.md` updated after the gate.

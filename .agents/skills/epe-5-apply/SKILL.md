---
name: epe-5-apply
description: Applies ONLY the /epe-4-review findings the human approved, with a fixer subagent that cannot discard anything (if it believes a finding is a false positive it BOUNCES it back with an argument). Re-runs the tests until truly green, updates evidence.md, the journal and the idempotent FIXER comment on the PR. Use when the user says "/epe-5-apply", "apply the approved findings", after the gate of an adversarial review.
argument-hint: <ids of approved findings> [change path]
---

# /epe-5-apply — apply what was approved, bounce what is doubtful, never discard

Second half of `/epe-4-review`. Deliberately separate: whoever fixes has an incentive to soften what they do not
want to touch, so they do not decide what counts.

## Procedure
1. **Confirm the scope**: list the approved findings (id, severity, file:line). Rejected and scope-out items do not
   enter. If something is ambiguous, ask first.
2. **Fixer** (general-purpose Agent; the prompt opens with `NO-CLOSED: fixer, applying already-approved findings`):
   receives only the approved findings + files + house conventions. Literal conflict-of-interest instruction:
   "Apply each approved finding. If you believe one is a false positive or the fix introduces a new problem, do NOT
   apply it and do NOT discard it: return it with your argument. You have no authority to dismiss a finding."
   Surgical edits, no extra rewrites.
3. **No regression**: tests of the touched area until truly green; project gates; citer inventory. If the fixes
   touch a visible surface, re-run the **exploratory pass** of `/epe-3-execute` (Final verification, step 2) over
   what changed, with the same gate: defects are fixed or escalated before returning, and the human validates only
   after the agent has walked it clean.
4. **Trace**: new entry in `memory/journal/` (append-only; if a previous entry was wrong, inline correction, not a
   rewrite) with applied / bounced / debt. Update `evidence.md` if a test changed.
5. **PR**: idempotent `<!-- review-agent: fixer -->` comment with applied (finding → change → file:line), bounced
   (with argument) and deferred, closing with the commit. If the PR scope changed, `gh pr edit --body`.
6. **Archive** (`/epe-6-archive`, default path): last commit of the same PR, so the merge carries code, specs,
   CHANGELOG and docs together.
7. **Return** to the human: applied, bounced, debt, test results, exploratory pass, where `validation.md` now
   lives. **Do not merge.**

## Resuming from another machine
`gh pr checkout <n>`; read the FINDER/VALIDATOR comments on the PR; **redo the human gate here** (approval does not
travel pre-made); revalidate against the current state of the branch (lines may have shifted; if a finding no longer
reproduces, bounce it).

## Antipatterns
The fixer discards on its own · fixing things "while at it" outside the findings · reintroducing debt · merging or
deploying after applying · returning to the human without walking the visible surface again · leaving the archive
for a separate PR after the merge.

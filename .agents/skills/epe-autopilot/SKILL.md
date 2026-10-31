---
name: epe-autopilot
description: Runs the WHOLE EPE cycle for one request without stopping at the intermediate gates, under a delegation the person grants by invoking it — story, exploration, plan approved "by delegation", red → green, real pass with screenshots looked at, truly green suites, PR, ONE round of adversarial review with the agent as gate and fixer, archive as the last commit, and a final report with every assumption to confirm. Merging stays human. Use when the user says "/epe-autopilot <request>", "no te frenes", "hasta dejar el PR", "como los últimos PRs", "procede como con las tareas anteriores", "full cycle", "take it to a reviewed PR".
argument-hint: <the request; defaults to the last user message>
---

# /epe-autopilot — from a request to a reviewed PR, with the gates closed by delegation

Invoking this skill IS the delegation: the person hands the agent the gates the cycle normally reserves for them
(accept the exploration, write "plan approved", decide the review findings) and keeps the one that matters most:
**merging**. Everything decided on their behalf is written down where they will read it. Measured where it was born
(odoo-harness, Saúl Pérez, 2026-10-29/30): seven changes in a row (PRs #16-#23) ran this way, each ending in a PR with its
review applied, its folder archived and a list of assumptions to confirm; the one thing that broke was outside the cycle (stacked PRs
merged into their bases, not into `main`), so step 0 now checks it.

## What the delegation covers, and what it never does
| Delegated (write "by delegation of <NAME>, <ROLE>" each time) | Never, even under delegation |
|---|---|
| accept the exploration matrix | merge, deploy, push to a protected branch, `--force` |
| `Status: APPROVED` in `plan.md` | anything in `harness.json → blocked_commands` |
| the review gate: confirm / reject / defer each finding | delete data the person did not point at; create repos or resources outside the repo |
| be the fixer of what was confirmed (`/epe-5-apply`) | contradict `memory/decisions/` or a `memory/closed/` verdict silently |
| answer its own open questions with the least risky option | push to a third-party or public repo the project rules do not already authorize |

**Stop and ask** only when: the next step is irreversible outside the PR; two readings of the request lead to
materially different products; a decision or closed verdict would have to change; credentials or a paid resource are
needed. Anything else: decide, write the assumption in `story.md § Notes`, keep going.

## Procedure
0. **Preflight.** Clean tree (if not yours, stop). `git fetch`; check the PRs the person says were merged actually
   reached the default branch (`git merge-base --is-ancestor <head> origin/main`): a PR merged into another PR's
   branch does not. If something is stranded, open the PR that lands it first and say so. Branch from the default
   branch (or from the stranded branch, with the PR **based on the default branch**, never stacked).
1. **Triage** (`/triage`): the lowest rung that fits. "nothing" → edit, verify, PR, report; no ceremony.
2. **Story** (`/epe-0-new`): criteria in Given/When/Then with concrete data **measured now**, not remembered; a
   `§ Notes` list "Assumptions by delegation" (each one: what was decided and why the other option lost).
3. **Explore** (`/epe-1-explore`): empirical first — run the real thing, measure, reproduce — then docs; citer
   inventory; the matrix is accepted by delegation and says so in its first line.
4. **Plan** (`/epe-2-plan`): `Status: APPROVED` + `Approved: <date>, by delegation of <NAME> (<ROLE>): "<their words>"`.
   One test per criterion; the gate that closes the work.
5. **Execute** (`/epe-3-execute`): red committed as `test:`, then green; the real pass against the real system
   (browser/Playwright for anything visible) and **look at every screenshot** — a DOM assertion is not what the eye
   sees; every suite truly green with numbers; `evidence.md`, `validation.md` (for the person, in their language, with
   the assumptions to correct), journal, PR. Short progress lines to the person between phases.
6. **Review** (`/epe-4-review`): ONE round calibrated by the diff; the agent is the gate. A second round only over files
   with confirmed medium/high findings, and only if the diff is large; never a third.
7. **Apply** (`/epe-5-apply`): confirmed findings get a red test then the fix; rejected and deferred ones go to
   `memory/closed/` with the reason; FINDER / VALIDATOR / FIXER comments on the PR.
8. **Archive** (`/epe-6-archive`) as the last commit of the same PR; PR body says where `validation.md` lives.
9. **Report** (in chat, not in a file): one line per criterion with its result; the PR link and what it changed; the
   **decisions taken by delegation** as a list the person can veto; what is left for them (merge — in which order —,
   validate with `validation.md`, decisions only they can take); anything found outside the scope (inbox).

A message from the person mid-run is folded in: answer a question in the report, add a request as a new step at the
end (or a new criterion if it belongs to the story), never drop the current step half done.

## Antipatterns
Asking "should I proceed?" between phases (the invocation already answered it) · approving the plan without writing
whose delegation it was · skipping the review because "it's small" (calibrate it, don't skip it) · reporting green
without the numbers · merging "because it was approved" · hiding a decision the person would have made differently.

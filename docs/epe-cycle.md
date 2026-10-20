# The EPE cycle: from a story with criteria to a reviewable PR

For anyone who works with the agent, developer or not. The agent does the heavy lifting; the flow guarantees that
what reaches review is verifiable.

## What goes in and what comes out
**In**: a story "As a <role>, I want…, so that…" (or a brief with audience, goal and core message) with numbered
acceptance criteria in `Given / When / Then` with concrete data. Without that, the agent stops.

**Out**: a folder `changes/<slug>/` with `story.md`, `exploration.md`, `plan.md` (approved), `tasks.md`,
`evidence.md`, `validation.md`, and a PR whose description links to all of it.

## Before the first story: the optional product layer
Nothing above `changes/` is required. When there is a product behind the stories, optional artefacts fix intent
— starting with `/product-discovery` (data catalogs, states, processes, roles matrix, validated with a navigable
mock) when structured data is behind it —
once (`make product-init`): `product/brief.md` (`/product-brief`, one page), `product/prd.md` (`/product-prd`, only when
more than one person must agree or more than one epic must not diverge) and `product/technical-brief.md`
(`/product-tech-brief`: team and existing stack first, then candidates, then the measurable NFR budget every change
inherits). Stories carry an `Origin:` line. Existing codebases enter with `/codebase-context` (docs/brownfield.md).

## Step by step
1. **Open the change folder**: `make epe-new SLUG=C-01-slug` (or `/epe-0-new`). Fill in `story.md`.
2. **Explore** (`/epe-1-explore`): for each criterion, the agent looks for what already exists (repo, dependencies,
   dated primary sources), detects constraints and classifies the change. **You accept the matrix** or correct it.
3. **Plan** (`/epe-2-plan`): plan with tickets, one test per criterion, citers, affected decisions and the gate
   that closes it. **You write "plan approved"** and the gate opens.
4. **Execute** (`/epe-3-execute`): vertical increments, truly green, evidence, validation script, journal, PR.
   It doesn't merge or deploy. In development, each task runs as the plan decided: `single`, `test→impl` or
   `parallel` (below).
5. **Review** (another person or session, `/epe-4-review`): finders per lens, validators that reproduce, human
   gate; `/epe-5-apply` applies only what was approved.
6. **Archive** (`/epe-6-archive`) as the last commit of the same PR, at the end of `/epe-5-apply`: the merge
   carries code, specs, CHANGELOG and docs together. Only a change merged before archiving gets its own archive PR.
7. **Validate**: whoever approves follows `validation.md` (now in the archived folder) and comments on the PR per
   criterion; small fixes go on top in the same PR. Then a human merges.

## Guardrails (they don't depend on anyone remembering)
- `supervised` profile (`make profile`): without an approved plan, `code` isn't edited; push to protected branches,
  force and merge are blocked. `autonomous` profile: the same ones warn.
- Deterministic lint after every edit. Closing requires a journal entry if there was work. `git add -A` blocked if
  there were someone else's changes at startup.

## Tester and implementer (development flavor)
Two agents are only worth it for the **information barrier**: tests written from the criteria and the plan's
interface contract, not from the code; an implementation that cannot pass by weakening the tests. So:
- The plan decides per ticket: `single` (the orchestrator does red → green itself, still committing the red as
  `test:`), `test→impl` (tester and implementer agents: tickets with 3+ criteria or 2+ implementation files, or
  `harness.json → roles: always`) or `parallel` (only with a filled **Interface contract** and disjoint files; each
  role in its own worktree). The lab measured the subagents as the main fixed cost; small tickets do not pay it.
- `test→impl`: the `tester` agent gets criteria, contract, test paths and run command, writes the tests, runs them
  red; the orchestrator re-runs the red and commits `test(<slug>): red for ACn`. The `implementer` agent gets the
  design and the test paths read-only and makes them pass; the orchestrator re-runs truly green and `make tdd-check`.
- The barrier is enforced, not remembered: `guard-tests.py` blocks (supervised) or warns (autonomous) an implementer
  editing `harness.json → tests` paths and a tester editing other `code`, by the subagent's `agent_type` or
  `HARNESS_ROLE`; inside a role, `guard-commands` also stops shell writes (`>`, `tee`, `sed -i`, `cp`) into those
  paths, because the edit hooks only see Edit/Write. `make tdd-check` verifies by git that the `test:` commit exists,
  the tests have no diff since, and that there is **one red commit per `test→impl` group** in `tasks.md`.
- A wrong test goes back to the tester and gets its own `test:` commit. Three failed implementer attempts → stop.
Content flavor: no split; the pair is writer and `cold-reader`.

## Truly green
Zero failures, zero errors in the log, zero skipped tests, with the numbers in `evidence.md`. In content: cold
reader with no real stumbles, dated sources, style checklist.

## Calibrate
| Work | What it needs |
|---|---|
| typo, broken link, memory entry | nothing: edit and verify |
| one change | a story with acceptance criteria (`make epe-new`) |
| a task that touches code and has a test (development) | tester → implementer with the barrier (`guard-tests`, `make tdd-check`) |
| several stories with a product behind them | `product/brief.md` first |
| several people must agree, or several epics must not diverge | `product/prd.md`, then `product/technical-brief.md` |
| existing codebase | `/codebase-context`, then one bounded change |

A typo, a broken link or a memory entry don't need all three phases. The cycle is required when the work touches
`code`, a decision, a gate or several chained artifacts. `/triage` applies this table to one request (rung, reason,
next command, execution hint) and the story records the verdict in its `Triage:` line; the `skill-nudge` hook
suggests it when a prompt looks like new work and there is no active change.

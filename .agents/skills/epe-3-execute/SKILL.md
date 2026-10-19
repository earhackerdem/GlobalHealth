---
name: epe-3-execute
description: EXECUTE phase of the EPE cycle. With an APPROVED plan.md, implements (or produces) tasks.md in vertical increments on its own branch, verifies each criterion with its test until truly green, writes evidence.md and validation.md (non-technical, for whoever approves), leaves a journal entry and opens the PR with the template. Never merges, never deploys, never pushes to protected branches. Use when the user says "/epe-3-execute", "implement the plan", "execute", "write the piece", after "plan approved".
argument-hint: [change path; defaults to .epe/active] [phase N to run a single phase]
---

# /epe-3-execute — implement with demonstrable verification

## Preconditions (verify, do not assume)
- `plan.md` with `Status: APPROVED`. If not, stop and send to `/epe-2-plan`.
- In the content flavor load `Skill(produce-content)`.
- Git anchor: `git status` and `git log --oneline -5`. If there is someone else's WIP, do not touch or commit it.
  Create `feat|fix|docs/<slug>` from the agreed base branch (if unclear, ask).

**Read once.** `story.md`, `plan.md`, `tasks.md` and the Interface contract are read at the start; per task you
re-read nothing but the ticket's lines. `product/` and `memory/` were digested by the plan; do not re-open them
unless a task cites them. (Measured: the harness arm spent ~2× the turns of bare Claude Code on the same change;
re-reading was part of it.)

## Per-task cycle (tasks.md rules)
1. Implement the vertical increment (model → interface → criterion test; or section → sources → cold reader).
2. Run the criterion's test; fix until green. **Truly green** = zero failures, zero errors in the log, zero skipped
   tests; report the numbers.
3. Tick `[x]` in `tasks.md`. Small commit with the house prefix (`AGENTS.md`).
4. Re-run the plan's **citer inventory** when closing each task: fixes debut their own regressions.

## Roles in the development flavor: tester and implementer
Who executes each task is written in `tasks.md` (`single` · `test→impl` · `parallel`), decided and approved in the
plan. The point of the split is the **information barrier**: tests written from the criteria, not from the code;
an implementation that cannot pass by weakening the tests. `guard-tests.py` enforces it by role (the subagent's
`agent_type`, or `HARNESS_ROLE` in other harnesses) over `harness.json → tests`; `make tdd-check` verifies by git.

**`test→impl`** (default for code with a test):
1. **Tester** (`.claude/agents/tester.md`, one Agent call). Brief, literal: the task's criteria from `story.md`, the
   plan's **Interface contract**, the test paths (`harness.json → tests`), the run command, the testing conventions
   of the project. Not the plan's design, not the implementation. It returns the files, the command and the
   failing numbers.
2. **You re-run the red yourself**: the tests must fail because the behaviour is missing, not because the test is
   broken. Commit the tests alone: `test(<slug>): red for ACn`. Red numbers go to `evidence.md § Red before green`.
3. **Implementer** (`.claude/agents/implementer.md`, one Agent call). Brief: the plan's design and files, the test
   paths to read, the run command, and the rule "you do not edit tests; the hook blocks it; a test you believe wrong
   is reported with the failing assertion, not fixed". It returns the files and the green numbers.
4. **You re-run the green yourself** (truly green), then `make tdd-check` (red commit exists, tests untouched since).
   Commit with the house prefix. Tick the task.
5. A wrong test goes **back to the tester** with the failure and gets its own `test:` commit; `tdd-check` then
   measures from the newest. Three failed implementer attempts with the same approach → stop and report; you never
   edit the tests to make them pass, and neither does the implementer.

**`parallel`**: only when the plan's Interface contract covers the shared files and the tasks touch disjoint files.
Each role works in its own worktree (`AGENTS.md § Concurrent sessions`); you merge and run steps 2 and 4 yourself.
Without a contract, `parallel` degrades to `test→impl`.

**`single`**: you do it yourself, with the per-task cycle above.

**Known asymmetry — implementation living under tests paths** (conftest.py, fixtures, test infra): the tester
must not write it (it is implementation) and the implementer cannot (the hook blocks tests paths), so the
orchestrator writes it and commits it with the `test:` prefix — and must SAY so in evidence.md, because for that
group `make tdd-check` passes vacuously (it only proves tests paths untouched after the red). Declared, not hidden.

Other harnesses (Cursor, Copilot): the roles run as two turns or sessions with `HARNESS_ROLE=tester` then
`HARNESS_ROLE=implementer` exported; `tdd-check` is identical. Content flavor: no split; the pair is writer and
`cold-reader` (`produce-content` rule j).

## With `engine: openspec`
`/opsx:apply <id>` (or `openspec instructions apply --change <id>`) walks `tasks.md`; the roles above still apply per
group's Execution tag, the orchestrator still re-runs red and green and commits, `make tdd-check` still verifies one
red per `test→impl` group. `evidence.md`, `validation.md` and the journal entry are the harness's, written in the
change folder. Do not archive here.

## Final verification (not delegable)
1. Full suite of the touched area, from clean. If there is a visible surface, exercise it for real and leave the
   output in `evidence.md`.
2. Cross regression over what the plan flagged as risks.
3. Re-run the project gates (`make` whatever applies).

## Deliverables (all mandatory)
- `evidence.md` (template) with a criterion → test → anchor → status table.
- `validation.md` **for whoever approves**: non-technical, one block per criterion with steps and a "seen / happens"
  checkbox, plus a "What it does NOT do yet" section.
- `memory/journal/YYYY-MM-DD-<slug>.md`: who → intent → what was done → verification (numbers) → debt. Attribute
  by name and role from the profile.
- PR with `gh pr create` using `.github/pull_request_template.md`. Push your branch **only if asked**. If the PR
  already exists and the scope changed, `gh pr edit --body`.

## Forbidden in this phase
- Merging, deploying, pushing to protected branches, `--force`, deleting others' branches. `guard-commands.py`
  blocks them in the supervised profile.
- Changing scope midway: if the plan does not hold, go back to `/epe-2-plan` with the delta. Anything that shows
  up outside the plan is declared as debt.
- 3 failed attempts with the same approach → stop, summarize what you tried and ask.

## Chat wrap-up
Done / evidence (numbers) / debt / next step (`/epe-4-review` by another person or session).

# START HERE — clean environment for a manual test (engine: OpenSpec)

Generated 2026-10-11 from `~/projects/personal/harness` with `make new … ENGINE=openspec`. Nothing here is about any
particular product: pick your own. Profile: supervised (the gate blocks until the plan is approved). Initial commit
done; no remote. Delete this file when you start.

## Prompt 1 (paste into Claude Code, Cursor or Copilot in this folder; fill the brackets)
```
I am Saúl Pérez (author). This is a NEW project: [what it is, in one or two lines].
Stack is fixed: [language/runtime, storage, test runner; or "propose, I have no team"].
NFR budget: [latency, test time, no network, data stays local…].
First increment: [the smallest useful slice, named as behaviour].
1. make doctor. 2. /product-brief. 3. /product-tech-brief. 4. make epe-new SLUG=<change-id>, then /opsx:propose for it
(proposal with Origin/Triage, delta specs with scenarios, design.md with Status: DRAFT and the Interface contract,
tasks.md with Execution per group). Show `openspec validate --strict` and `openspec status`.
Stop before any code: the plan needs my approval.
```
Skip steps 2 and 3 if a brief feels like ceremony for what you are building: `/triage` tells you which rung the request
needs.

## Prompt 2 (after reading design.md and tasks.md)
```
plan approved. /epe-3-execute: single groups red→green by you (test: commit first), test→impl groups with the tester
and implementer agents; re-run red and green yourself; make tdd-check after each group; evidence.md, validation.md,
journal. Do not push. Finish with the test numbers and `make board`.
```

## Second increment (what the lab never measured)
Open a new session, `make epe-new SLUG=<next-id>`, and let `/opsx:propose` read the archived first change and the
existing code. Watch whether exploration cites `file:line`, whether the contract reuses the existing interfaces, and
whether `make tdd-check` stays green.

## Useful
`make board` · `make tdd-check` · `make epe-status` · `openspec status --change <id>` · `openspec validate --all --strict` ·
`make harness-status SRC=../harness` (what a newer harness would change here).
Plain engine instead of OpenSpec: `cd ~/projects/personal/harness && make new DEST=/Users/sehnhack/projects/personal/sandbox-epe FLAVOR=development NAME=sandbox-epe AUTHOR="Saúl Pérez" EMAIL=earhackerdem@gmail.com OWNER="Saúl Pérez"`.

# Tasks

Each group carries its Execution: `single` (one agent writes the red, commits it as `test:`, then the green) ·
`test→impl` (a `tester` agent writes the red from the scenarios and the interface contract, the orchestrator commits
it as `test:`, an `implementer` agent makes it green without touching tests) · `parallel` (only with the interface
contract filled and disjoint files). Rule: a group that touches `code` and covers 3+ scenarios or 2+ implementation
files is `test→impl`; smaller groups are `single`. `make tdd-check` requires one `test:` commit per `test→impl` group.

## 1. <!-- Group name --> · test→impl

- [ ] 1.1 Test: <!-- scenario name --> (red)
- [ ] 1.2 Impl: <!-- what makes it green -->
- [ ] 1.3 Verify: suite truly green (0 failures, 0 errors, 0 skipped); `make tdd-check`

## 2. <!-- Group name --> · single

- [ ] 2.1 <!-- task -->

## Close
- [ ] evidence.md (red/green numbers per group) · validation.md (non-technical, for whoever approves)
- [ ] journal entry in memory/journal/ · PR opened (push only if asked)

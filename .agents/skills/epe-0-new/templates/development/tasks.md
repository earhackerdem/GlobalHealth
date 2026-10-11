# Tasks — <slug>

Mark each one with [x] when done. /epe-3-execute works in this order.

Each task carries its Execution from plan.md: `single` · `test→impl` · `parallel`.

## Phase 1 — <name>
- [ ] T-01 <task> (AC1) · test→impl
  - [ ] tests red, committed `test(<slug>): red for AC1` (tester)
  - [ ] implementation truly green, `make tdd-check` ✓ (implementer)
- [ ] T-02 <config or docs task> · single

## Phase 2 — <name>
- [ ] …

## Close
- [ ] Area suite truly green (0 failures, 0 errors, 0 skipped)
- [ ] Citer inventory re-checked
- [ ] evidence.md complete
- [ ] validation.md written for the approver
- [ ] journal entry in memory/journal/
- [ ] PR opened with the template

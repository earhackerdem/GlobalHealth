# Plan — <slug>

Status: DRAFT   <!-- /epe-2-plan changes this to `Status: APPROVED` when the user writes "plan approved" -->
Date: YYYY-MM-DD · Approved by: <name (role)> on YYYY-MM-DD

## Goal
<1-2 measurable sentences.>

## Scope / Out of scope
- In: …
- Out: … (what /epe-1-explore marked ⛔ or 💤)
- Assumptions with a default: "I assume X unless you say otherwise".

## Design
Components, data, interfaces. Decisions and discarded alternatives (1 line each).

## Interface contract
<Signatures, endpoints, CLI flags, schemas or events that tests and implementation share. Filled = tester and
implementer can work in parallel on these files. Empty = sequence (red → green). Nothing here is "to be decided
during implementation".>

## Files to touch and citer inventory
| File | What changes | Anchor | Who cites it |
|---|---|---|---|

## Affected decisions in `memory/decisions.md`
<Which one and how it is touched in this same change; or "none".>

## Tickets
| ID | Type (configuration / development / docs / tests) | Description | AC covered | Execution |
|---|---|---|---|---|

Execution: `single` (one agent writes the red, commits it as `test:`, then the green: config, docs, and code tickets
under 3 criteria / 2 files) · `test→impl` (a ticket that touches `code` with 3+ criteria or 2+ implementation files,
or `harness.json → roles: always`: tester writes and commits the red, implementer makes it green, barrier by
`guard-tests` + `make tdd-check`)
· `parallel` (only if the Interface contract above covers the shared files and the tickets touch disjoint files;
each role in its own worktree).

## Test plan (one row per AC, mandatory)
| AC | Unit | Integration / HTTP | End-to-end | Manual validation (validation.md) |
|---|---|---|---|---|

## Non-functional constraints the plan addresses
| # | How it is addressed |
|---|---|

## Risks and regressions
…

## Gate that closes the work
<Command or check. If it doesn't exist, it is written before executing.>

## Delivery phases (committable vertical increments)
1. …

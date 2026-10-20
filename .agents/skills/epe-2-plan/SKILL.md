---
name: epe-2-plan
description: PLAN phase of the EPE cycle. From an accepted exploration.md produces plan.md (goal, scope and non-scope, design, files with anchor, tickets, ONE test per criterion, constraints addressed, risks, phases) and tasks.md. Gate: nothing is edited until the user writes "plan approved"; then it marks `Status: APPROVED` and the gate-plan hook allows editing. Use when the user says "/epe-2-plan", "make the plan", "plan approved", or after accepting an exploration.
argument-hint: [change path; defaults to .epe/active] · "plan approved" to open the gate
---

# /epe-2-plan — from diagnosis to a gated plan

## Preconditions
- `exploration.md` exists and its §1 is all ✅. If not, go back to `/epe-1-explore`.
- Read `memory/decisions.md`: the plan does not contradict a current ADR; if it needs to change one, the plan says so
  and the ADR is touched **in the same change**, not later.
- Load every skill listed in `harness.json → phase_skills.plan` (the project's domain skills: how this stack is
  tested, its house conventions and templates). The test plan's levels and the ticket types come from them.

## Two modes
1. **`/epe-2-plan`**: write/update `plan.md` with `Status: DRAFT` and `tasks.md`. Finish by asking for the textual
   approval.
2. **"plan approved"** (literal, from the person you work with): change the line to `Status: APPROVED`, add
   `Approved by: <name (role)> on <date>`, confirm that `.epe/active` points to this change and announce that the
   gate is open (`/epe-3-execute`). If they ask for adjustments, apply them and ask for approval again.

## Plan contents (template `templates/<flavor>/plan.md` from `epe-0-new`)
- Measurable **goal**, **scope / non-scope** with declared assumptions ("I assume X unless you say otherwise").
- **Design** with discarded alternatives, one line each.
- **Files to touch** with an anchor verified today with grep. **Citer inventory**: who cites what you are about to
  change (other files, docs, memory, gates). Whatever cites it expires in the same commit.
- **Tickets** split by type (configuration / development or writing / docs / tests), each with its **Execution**
  (development flavor): `single`, `test→impl` or `parallel`. Rule (`harness.json → roles`, default `auto`): a ticket
  that touches `code` and covers **3+ criteria or 2+ implementation files** is `test→impl`; smaller tickets are
  `single` (the orchestrator writes the red itself, commits it as `test:`, then the green: same discipline, no
  subagents; `make tdd-check` still checks the commits). `roles: always` makes every code ticket `test→impl`;
  `roles: never` makes everything `single`. Config, docs and trivial tickets are `single`; `parallel` only
  when the **Interface contract** section covers the files the tester and the implementer share and the tickets
  touch disjoint files. The decision is made here, approved with the plan, never improvised during execution.
- **Interface contract** (development): signatures, endpoints, schemas, CLI flags the tests will exercise. Empty
  means sequence. "To be decided while implementing" is not a contract.
- **Test plan: one row per criterion, mandatory.** In development: unit, integration/HTTP, end-to-end, manual
  validation. In content: cold reader, style checklist, source verification, approver validation. **A criterion
  without an assigned test blocks approval.**
- **Constraints addressed** (each 🟡 from the exploration with its how); the 🔴 ones out, under non-scope.
- **Risks and regressions**; **phases** as committable vertical increments.
- **Gate that closes the work**: if the gate does not exist, it is written **before** executing.

## Prototype gate (changes that add or alter user-facing screens)
The person approving often will not read the plan's prose, and never the delta specs (measured in origin:
GlobalHealth 2026-10-12, a whole cycle built on a wrong model that a mock exposed in minutes). So, when the change
touches screens, the plan ships with a **navigable mock**: mock data drawn from `product/dominio.md`'s glossary
when it exists, every actionable element labeled with the id of the acceptance criterion it satisfies (toggleable
`AC-n` badges) and the story's text verbatim at the top of the criteria legend. The mock's HTML is committed to
the repo next to the change (or `product/prototipos/`) and opened locally; no hosted copy (artifact, v0) unless the
person asks, since it is bound to one account and its sharing permissions. The repo file is the source of truth. The textual approval then means "I navigated the prototype and this is what I want" — ask for
exactly that. The AC ids travel the whole chain: prototype badge → scenario → test name → validation.md. The specs
do not disappear: they remain the contract the tests are written from, and they alone cover errors, limits and
regulations (the mock only shows happy paths). If the person prefers an external tool, emit a ready prompt for
Claude Design / v0 / Stitch instead of the page; when the interaction is genuinely uncertain, two cheap variants
beat one debate. Changes with no visible surface skip this section, and say so.

## With `engine: openspec`
The plan is `design.md` + `tasks.md` from the `harness-epe` schema (template with `Status:`, Interface contract, test
plan one row per scenario, Execution per group). "plan approved" turns `design.md`'s `Status:` line to APPROVED (the
gate reads `harness.json → plan_file: design.md`). `openspec validate <id> --strict` and `openspec status --change <id>`
before asking for approval; both must be clean. Citers and affected decisions go in `design.md § Decisions`.

## Rules
- No literal "plan approved", no editing. `gate-plan.py` enforces it (blocks in supervised, warns in autonomous).
- If the change is **Infeasible** in the exploration, the plan is a redesign document and **is not approved** for
  execution.
- Do not re-explore: whatever is missing goes in as a question, not invented.
- If you cannot summarize the plan in one sentence, it is not ready.

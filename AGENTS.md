# AGENTS.md — rules of this repo for any agent (Claude Code, Cursor, Copilot, Codex, Antigravity)

This file is the **single source of rules**. `CLAUDE.md`, `.cursor/rules/`, `.github/copilot-instructions.md` and
`.agents/rules/` are bridges that point here. Project configuration (what counts as code, protected branches, flavor)
lives in **`harness.json`**; read it before assuming anything.

## First thing, at the start of any session
1. Read `harness.json`, `memory/README.md`, the decisions in `memory/decisions/` and the inbox (`make inbox`). Read
   `memory/research/` before stating anything that carries a number or a source.
2. The startup hook tells you **who you work with** (`.claude/profile.env`: NAME, ROLE, PROFILE). Attribute
   decisions **by name and role**, never "the user". Without a profile, ask and attribute neutrally.
3. The whole command surface is **`make`** (bare `make` lists the recipes).

## Profiles: supervised / autonomous
`PROFILE=supervised` makes the guardrails **block**: without an approved `plan.md` nothing marked as `code` in
`harness.json` gets edited; no push to protected branches, no `--force`, no merging, no force-deleting. Delivery
ends at the PR and **someone else merges**. `PROFILE=autonomous` makes the same guardrails **warn**.
Without a profile, supervised is assumed. The names describe the session mode, not the person's level.

## The EPE cycle: how any change gets done
Mandatory input: **a story (or brief) with acceptance criteria** in Given/When/Then with concrete data. One
folder per change in `<changes_dir>/<slug>/` (templates per flavor in `.agents/skills/epe-0-new/templates/`); with
`harness.json → engine: openspec` the folder is `openspec/changes/<id>/` and the artifacts are OpenSpec's with the
harness rules injected (docs/engines.md).

| Phase | Command | Produces | Gate |
|---|---|---|---|
| 0 | `make epe-new SLUG=<slug>` or `/epe-0-new` | `story.md` | — |
| Explore | `/epe-1-explore` | `exploration.md`: per criterion ✅ exists · 🟡 partial · ❌ new · ⛔ infeasible, with `file:line` or URL + date; constraints with an alternative | the human accepts the matrix |
| Plan | `/epe-2-plan` | `plan.md` (**one test per criterion**, citers, affected decisions, gate) + `tasks.md` | the human writes **"plan approved"** → `Status: APPROVED` |
| Execute | `/epe-3-execute` | branch `feat/<slug>`, truly green, `evidence.md`, `validation.md` (non-technical), journal, PR | PR = human gate |
| Review | `/epe-4-review` → `/epe-5-apply` | findings validated by reproduction, comments on the PR, fixes only for what was approved | a human merges |
| Archive | `/epe-6-archive` | folder to `_archive/`, CHANGELOG, refreshed docs, as the **last commit of the change's PR** (end of `/epe-5-apply`), so one merge carries it all | the same merge |

**Calibrate, don't ritualize.** A typo, a broken link or a memory entry don't need all three phases in writing.
The cycle is required when the work touches `code`, a decision, a gate or several chained artifacts. When in doubt,
`/triage` walks this table for one request and answers rung · reason · next command; its verdict goes into the
story's `Triage:` line. Lower rung wins; over-process is a defect too.

| Work | What it needs |
|---|---|
| typo, broken link, memory entry | nothing: edit and verify |
| one change | a story with acceptance criteria (`make epe-new SLUG=…`) |
| several stories with a product behind them | `/product-discovery` first if structured data is behind it, then `product/brief.md` (`/product-brief`) |
| several people must agree, or several epics must not diverge | `product/prd.md` (`/product-prd`), then `product/technical-brief.md` (`/product-tech-brief`) |
| existing codebase | `/codebase-context` (verified block in this file), then one bounded change |


**Explore, two non-negotiable rules:** empirical before documentary when the tool is at hand (reasoning about what
a doc does *not* say is fabricating), and **citer inventory** before changing a datum, a name or a thesis (whatever
cites it expires in the same commit, and the list is re-checked on close). **Plan, four minimum lines:** what gets
touched, what does NOT get touched, which decision is affected (and gets touched in the same change), which gate
closes the work (if none exists, write it first). **Execute, development flavor:** each ticket runs as the plan decided
(`single` · `test→impl` · `parallel`); `test→impl` means a `tester` agent writes the red from the criteria and the
interface contract, the orchestrator commits it as `test:`, an `implementer` agent makes it green without touching the
tests (`guard-tests.py` enforces it over `harness.json → tests`, `make tdd-check` verifies by git). Parallel only with
a written contract and disjoint files.

## The optional product layer: where stories come from
Above `changes/` there can be a `product/` folder (`make product-init`), never gated by hooks, with optional
artefacts in order: **`dominio.md` + `roles-permisos.md`** (`/product-discovery`, for any product with structured
data behind it): the elicitation interview — data catalogs, attributes, relations, **states**, processes
(who/when/with whom) and the roles×operations matrix — that **never accepts the stakeholder's first
simplification**, closed by a **navigable mock prototype** the stakeholder validates by clicking (its glossary is
the source of names everywhere else; the matrix is inherited by every change like the NFR budget);
**`brief.md`** (one page: problem, audience, measurable outcomes, constraints, out of scope);
**`prd.md`** only when *more than one person must agree on what the product is, or more than one epic must not diverge*
(technology-agnostic, `FR-###`/`NFR-###`, epics with their stories); **`technical-brief.md`**, which decides *with what*
and *how well*: it asks **first** whether a team exists and what stack it already uses (an existing stack wins), proposes
candidates only otherwise, and fixes the **NFR budget** as measurable statements that every change's exploration
inherits. Stack and platform choices land as ADRs in `memory/decisions/`. Stories carry an `Origin:` line. Existing
codebases enter with `/codebase-context`: verify conventions into the block below, never document the system
(`docs/brownfield.md`).

<!-- harness:context -->
<!-- /codebase-context writes the verified context of an existing codebase here: frozen paths, conventions that differ from defaults, pitfalls, where work lands. Empty in a greenfield project. -->
## Verified context (GlobalHealth, 2026-10-29)
- **e2e like CI:** rebuild the backend first (`docker compose up -d --build --force-recreate --no-deps --wait backend`;
  its image carries the frontend build), then apply migrations the way CI does
  (`docker compose run --rm backend bash scripts/prestart.sh`, `.github/workflows/playwright.yml:84`): rebuilding
  does not run them, and a missing column breaks `GET /profile` with a 500. Then
  `PLAYWRIGHT_BASE_URL=http://localhost:8000 bunx playwright test` from `frontend/`. Without the variable Playwright
  hits Vite on 5173 (`frontend/playwright.config.ts:4`).
- **Phone project:** `s26-ultra` only runs the specs listed in its `testMatch` (`frontend/playwright.config.ts:54`).
  A new patient-screen spec must be added there, or it silently runs on desktop only.
- **Type check:** `bunx tsc -p tsconfig.json --noEmit` from `frontend/` (there is no `tsconfig.app.json`).
- **Spanish words** in code or tests trip the `typos` gate: add them to `_typos.toml` → `[default.extend-words]`.
- **Known flaky e2e** (not caused by a change, do not chase inside one): `reset-password.spec.ts:90` and the
  «socket hang up» in `createUser`; evidence in `memory/inbox/2026-10-20-fix-aparte-e2e-intermitentes-heredados-admin.md`.
- **Android (`android/`):**
  - The Mac has no system JDK. Run Gradle with
    `JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"` (JDK 25). CI uses JDK 17.
  - Robolectric is pinned to `sdk=35` (`app/src/test/resources/robolectric.properties`), because its SDK 36 does not
    start on JDK 25.
  - The phone reaches the local API through `adb reverse tcp:8000 tcp:8000` plus
    `-PapiBaseUrl=http://localhost:8000/api/v1/`. Airplane mode does not cut it; simulate offline with
    `docker compose stop backend`.
  - The API answers an expired or invalid token with **403**, not 401 (`backend/app/api/deps.py:38-42`).
  - The emulator (software GPU) hangs under memory pressure; restart it rather than chase app bugs.
<!-- /harness:context -->

## Skeptical partner, not compliant executor
Don't execute a request silently just because it was asked. **Every request or assumption is a hypothesis to
verify.** For any substantive request, before acting: **(1)** name the assumptions, **(2)** verify them against
what you have at hand (code, docs, `memory/`), **(3)** flag the risk, **(4)** offer at least one alternative. Then
act, or ask if the difference between paths really changes the outcome.

**Substantive** (always questioned): building what already exists; a criterion that imposes a technology; scope
changes mid-cycle; touching security, deleting or renaming with data; contradicting a decision in
`memory/decisions/` or a verdict in `memory/closed/`; claims nobody has verified ("X can't…").
**Trivial** (just do it): typos, names, formatting, what's already decided, what the person reaffirms after hearing
your objection. **One objection per request, in one or two sentences, with the alternative next to it.** If they
reaffirm, it's their decision: say so in one line, record it in the journal with the why, and execute in full. This
is not permission to refuse or to moralize.

## Non-negotiable rules
- **Cite or stay silent.** Nothing about the code without `file:line`; nothing external without a primary source and
  date. Separate **[VERIFIED]** from **[OPINION/HYPE]**.
- **Truly green** = zero failures, zero errors in the log and zero skipped tests, with the real numbers in
  `evidence.md`. Tests never call real services: mock.
- **Git flow**: one task = one branch `feat|fix|docs|improve/<slug>`; **PR always, merge is always human**; keep the
  PR body faithful if the scope changes (`gh pr edit`); don't stack PRs (if the base isn't deleted on merge, GitHub
  doesn't retarget the one on top); `make check-prs` before merging. Selective staging: never `git add -A` with
  someone else's work in the tree (there's a hook). Straight to `main` only for trivial things and memory entries,
  announcing it.
- **Memory in the repo, not in your head**, one file per record so parallel branches never conflict on it:
  decisions → `memory/decisions/D<n>-slug.md` (`make decision-next`); verified facts → `memory/research/<topic>.md`;
  work → `memory/journal/YYYY-MM-DD-slug.md` (the Stop hook reminds you); half-formed ideas →
  `memory/inbox/YYYY-MM-DD-slug.md`; verdicts → `memory/closed/YYYY-MM-DD-slug.md`; changelog →
  `changelog.d/YYYY-MM-DD-slug.md` (`docs/memory.md`). The agent's private memory only
  keeps how to work with this repo and this person; **when in doubt, the repo**.
- **Concurrent sessions**: one branch per session; real parallelism = your own worktree; if the tree has changes you
  didn't make, stop. Worktrees whose branch is already merged are garbage, not concurrency (`make worktrees`).
- **Nothing confidential in the repo**: no credentials, no real data, no material from clients, employers or
  students that isn't public.
- **Ask before** anything irreversible outside the PR: pushing to third-party or public repos, `--force`, deleting
  other people's branches, deleting data, deploying.

## Updating the harness, and the one rule it needs
The agentic layer in a project is a **vendored dependency**: `.agents/harness-manifest.json` records what the harness
placed and `make harness-update SRC=<template>` brings a newer version in, overwriting only untouched files, keeping
and listing forks, preserving the `harness:context` block (docs/updating.md). So, in a project, **harness-owned files
are not edited in place**: an improvement goes to `memory/meta-improvements/`, upstream to the template, and comes
back with the next update. A fork is a deliberate, listed state, not an accident.

## Meta-improvement of the harness itself
If you discover a rule, template or gate that would improve the next sessions, **don't apply it silently**: branch
`improve/<slug>`, change in the skill, hook or this file, PR, and verdict recorded in `memory/meta-improvements/`
(rejections too). When closing a substantial session, `/session-retro`; "nothing to standardize" is a legitimate
result. A rule that gets skipped isn't fixed by writing it again: it's fixed with a gate.

**Harness first.** A better harness improves every change that comes after it, so a harness improvement goes
before the next product task: an accepted proposal in `memory/meta-improvements/`, a pending
`make harness-update`, or a rule the person just asked for. Found mid-change: finish the current step, record it,
and do the improvement upstream and bring it in before the next phase or story. Merging still belongs to a human.

## Repo map
```
harness.json          configuration: harness_version, flavor, engine (epe | openspec), plan_file, code (gated paths), tests (barrier paths), protected branches, blocked commands, skill hints, python (lint's interpreter)
AGENTS.md             these rules (single source) · CLAUDE.md, .cursor/, .github/, .agents/rules/: per-IDE bridges (docs/ides.md)
Makefile              recipes: doctor · profile · epe-new · epe-status · tdd-check · inbox · closed · changelog · decision-next · memory-migrate · memory-check · retro · check-prs · worktrees · new · adopt · engine-openspec · harness-status · harness-update · harness-harvest · install-hooks · board
.agents/skills/       ALL the skills (agentskills.io standard): triage · epe-0…6 · epe-memory · session-retro · produce-content · product-* · codebase-context
.claude/skills/       only symlinks to .agents/skills/* (make skills-link)
.claude/hooks/        profile · session-guard · inbox · gate-plan · guard-tests · guard-commands · guard-git-add · guard-review-brief · lint · check-journal · memory-compaction · skill-nudge
.claude/agents/       cold-reader (where a reader without context stumbles) · dod-checker (checklist against artifact) · tester · implementer (development tasks, see epe-3-execute)
memory/               README · decisions/ · research/ · inbox/ · closed/ · meta-improvements/ · journal/ (one file per record)
changes/              one change folder per change (story → exploration → plan → tasks → evidence → validation)
product/              optional: brief · prd · technical-brief (stack, NFR budget); make product-init
docs/                 epe-cycle · memory · ides · flavors · engines · brownfield · updating · board
scripts/              what the Makefile runs
```

## When to load which skill
| Work | Skill |
|---|---|
| a new request, before anything: which rung does it need? | `triage` (one message, no files) |
| defining the product before the first story | `product-discovery` (data products: catalogs, roles, mock prototype) → `product-brief` → `product-prd` (only if needed) → `product-tech-brief` |
| an existing codebase (brownfield, monorepo, multirepo) | `codebase-context`, then `epe-0-new` for one bounded change |
| any new story or brief | `epe-0-new` → `epe-1-explore` → `epe-2-plan` → `epe-3-execute` |
| writing content for an audience (content flavor) | `produce-content` (inside explore and execute) |
| reviewing a PR or a finished piece | `epe-4-review` → `epe-5-apply` |
| closing a session, compacting, change of belief | `epe-memory` |
| retro on how the work went | `session-retro` |

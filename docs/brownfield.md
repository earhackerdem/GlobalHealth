# Existing projects: brownfield, monorepo, multirepo

The harness goes **into** an existing repo with `make adopt DEST=<repo>`; it never touches the code. What the four SDD
tools we studied agree on (`memory/research.md#prd`): you do not document the system first; you verify what the agent
cannot read from the code, you open one bounded change, and specs grow one change at a time.

## What `make adopt` does
- Adds the agentic layer (`.agents/`, `.claude/`, `.cursor/`, `.github/hooks`, `scripts/`) without replacing any file.
- Puts the harness docs in `docs/harness/` so your `docs/` stays yours.
- `AGENTS.md` and `CLAUDE.md`: created if missing; if they exist, a short block between `<!-- harness:rules -->` markers is
  appended (your rules stay first).
- `Makefile`: created if missing; if it exists you get `harness.mk` and add `include harness.mk`.
- `harness.json` with `code=[]`, `memory/` seeded, `changes/` created. Nothing is gated until `code` is filled.

## Then, in the agent
1. `/codebase-context`: verifies conventions, pitfalls, frozen paths and tool versions against the code and proposes the
   `<!-- harness:context -->` block for `AGENTS.md`; fills `harness.json` → `code` and `blocked_commands`.
2. `/product-tech-brief` only if the product layer is wanted: in brownfield the existing stack wins, so the brief
   records the NFR budget and where new requirements strain the stack.
3. One bounded first change: `make epe-new SLUG=…`. The first change is how the context gets tested.

## Monorepo
One harness at the root. `harness.json` → `code` lists the packages or apps (`apps/`, `packages/`, `services/`); the
plan gate then watches all of them. One `memory/`, one `changes/`, one `product/`. If packages have different
conventions, the context block says so per package, and `blocked_commands` covers the dangerous operations of each
(migrations, deploys). Skills for a stack go in `.agents/skills/` once.

Later, `make harness-update SRC=<template>` refreshes what adopt placed (`harness.mk`, `docs/harness/`, the agentic
layer) and never your `Makefile`, `AGENTS.md` or code: see [updating.md](updating.md).

## Multirepo
Adopt the harness **in each repo where changes happen**: each gets its own `memory/` (decisions and journal are about
that code) and its own `changes/`. The product layer lives **once**, in the repo that owns the product, or in a small hub
repo generated with `make new`; every other repo's `product/README.md` is a pointer to it, and stories carry
`Origin: <hub>/product/prd.md § epic N`. The environment-plus-client-repos pattern (one tooling repo, client repos with
their own memory) is the origin of this layout and works the same way.

## What not to do
- Do not write a retroactive spec of the system; do not paste a directory tree or a tech-stack list into `AGENTS.md`.
- Do not fill `code` with `.` : a gate that watches everything, including docs, teaches people to disable it.
- Do not copy another repo's `memory/`: decisions are about one codebase.

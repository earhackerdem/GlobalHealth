---
name: epe-0-new
description: Step 0 of the EPE cycle. Opens a change folder at <changes_dir>/<slug>/ with story.md from the project flavor's template (harness.json) and marks it as the active change. Use when the user says "new story", "start a change", "/epe-0-new slug", or brings a user story or a content brief that has no folder yet.
argument-hint: <slug> [path to an existing story or brief]
---

# /epe-0-new — open a change

The cycle works with **one folder per change** (idea borrowed from OpenSpec), at `<changes_dir>/<slug>/`:

```
changes/C-01-slug/
├── story.md         # REQUIRED INPUT: story + acceptance criteria (or a brief with criteria, in content)
├── exploration.md   # written by /epe-1-explore
├── plan.md          # written by /epe-2-plan; `Status: APPROVED` opens the gate
├── tasks.md         # checklist that /epe-3-execute ticks off
├── evidence.md      # tests and verification (written by /epe-3-execute)
└── validation.md    # NON-technical script for whoever approves
```

## Procedure
1. Read `harness.json` (`flavor`, `changes_dir`). If the slug is missing, ask in a single round. Number sequentially
   (`ls <changes_dir>/`).
2. Preferred: `make epe-new SLUG=<slug> [STORY=path]`. Does the same as steps 3-4 and writes `.epe/active`.
3. Create the folder and copy `templates/<flavor>/story.md`. If `/triage` ran, fill the `**Triage:**` line with its
   verdict and date; otherwise write "not triaged". If the user gave text, pour it into the template
   **without inventing criteria**: whatever is missing stays as `<!-- MISSING: … -->` so /epe-1-explore catches it.
4. Write the change path to `.epe/active` (repo root; git-ignored). It is what `gate-plan.py` watches.
5. Finish with: the path created, what the story is missing, and the next step: `/epe-1-explore`.

## With `engine: openspec` (harness.json)
`make epe-new SLUG=<id>` runs `openspec new change <id>` and points `.epe/active` at `openspec/changes/<id>/`. The
artifacts are OpenSpec's (`proposal.md`, `specs/**`, `design.md`, `tasks.md`) from the project's `harness-epe` schema,
which carries the harness rules: `Status:` gate in `design.md`, Interface contract, Execution per task group. Story
and criteria live in `proposal.md` (Origin/Triage lines) and the specs' scenarios. `/opsx:propose` writes the four
at once; `/epe-1-explore` can still run first and leaves `exploration.md` next to them.

## Rules
- Do not write code, content or `exploration.md` here: this skill only opens the change folder.
- One story per folder. If several come in, one folder per story.
- Calibrate: a typo or a trivial tweak does not need a change folder (AGENTS.md § *Calibrate*).

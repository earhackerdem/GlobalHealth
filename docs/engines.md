# Change engines: `epe` and `openspec`

`harness.json → engine` decides where a change's artifacts live and which tool scaffolds them. Everything else of the
harness (memory, profiles, hooks, roles, product layer, board, update) is the same under both.

| | `epe` (default) | `openspec` |
|---|---|---|
| Scaffold | `make epe-new SLUG=…` copies the flavor templates | `make epe-new SLUG=…` runs `openspec new change` (pinned `openspec_version`) |
| Folder | `changes/<slug>/` | `openspec/changes/<id>/` |
| Behaviour contract | `story.md` with AC in Given/When/Then | `proposal.md` + `specs/**/spec.md` (requirements with GIVEN/WHEN/THEN scenarios; deltas merged into `openspec/specs/` on archive) |
| Exploration | `exploration.md` | `exploration.md` (harness artifact, optional) |
| Plan + gate | `plan.md` with `Status: APPROVED` | `design.md` with `Status: APPROVED` (`plan_file: design.md`) |
| Tasks | `tasks.md` with Execution per ticket | `tasks.md` with Execution per group (template from the `harness-epe` schema) |
| Delivery | `evidence.md`, `validation.md`, journal, PR | same |
| Validation | `make epe-status`, `make board` | plus `openspec validate --strict`, `openspec status`, `openspec instructions` |
| Archive | `/epe-6-archive` moves to `_archive/` | `openspec archive` merges deltas, then the harness's steps |

## Switching a project to OpenSpec
```bash
make engine-openspec                 # or: make new … ENGINE=openspec
```
It runs `openspec init` (pinned), forks `spec-driven` as `openspec/schemas/harness-epe/` with the harness's `design.md`
and `tasks.md` templates and instructions, appends the harness rules to `openspec/config.yaml` (`rules`, `operations`),
and sets `engine`, `plan_file` and `openspec_version` in `harness.json`. Needs Node.js (`npx`). OpenSpec's skills land
as real folders in `.claude/skills/`; `skills-check` lists them as foreign, not as errors. The forked schema and
`config.yaml` are project-owned: `harness-update` never touches them.

## Why the rules travel through the schema
The blog lab (`memory/research.md#lab-blog-5x`) showed OpenSpec producing a contract ~3× larger and more tests at the
same cost, but two of five runs collapsed every test into one red commit: OpenSpec's `tasks.md` carries no Execution
field. The schema fork injects it (template + instruction + config rule) and `make tdd-check` enforces one red commit
per `test→impl` group, so granularity is checked by git, not remembered.

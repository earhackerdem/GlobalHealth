# The board: `make board`

`changes/` already holds the state of every piece of work. `make board` renders it; it keeps no state of its own and
never asks anyone to move a card.

```bash
make board               # markdown table in the terminal + .harness/board.html (self-contained, light/dark)
make board-serve         # http://127.0.0.1:8765/.harness/board.html, card links open the files (PORT=…)
```

## Columns come from the files
| Column | Rule |
|---|---|
| Backlog | `story.md` only (an empty folder is flagged) |
| Exploring | `exploration.md` present, no plan |
| Planning | `plan.md` present, not `Status: APPROVED` |
| Executing | plan approved, tasks not all ticked |
| Validating | all tasks ticked, `evidence.md` and `validation.md` present |
| Done | under `changes/_archive/` (`/epe-6-archive`) |

Each card: slug, story title, `Triage:` and `Origin:` lines, number of acceptance criteria, tasks done/total, plan
status and approver, the six files (● present ○ missing), the Execution tags found in `tasks.md`. ▶ marks
`.epe/active`.

## For someone outside the repo
`.harness/board.html` is one file with no network dependency: send it, host it, or paste the markdown table into a
message. It is derived and git-ignored; regenerate it whenever you want it fresh. Jira or similar only buys this same
visibility for an outsider; the board gives it from the repo.

## What it is not
Not a live monitor of agents (that would be a hook writing events, see `memory/inbox/`), not a place to edit (the
cycle edits the files), not a runtime a non-developer drives (claude.ai/code shared sessions do that on a repo with
this harness; `memory/research/gui.md`).

# Changes (EPE cycle)

Each change lives in a `<slug>/` folder that moves through these steps in order, with one template per step
(`.agents/skills/epe-0-new/templates/<flavor>/`):

| Step | File | Who writes it | Gate |
|---|---|---|---|
| 0 | `story.md`: story or brief with acceptance criteria | whoever requests the change | the agent does not explore if a criterion is missing |
| 1 | `exploration.md`: for each criterion ✅ exists / 🟡 partial / ❌ new / ⛔ infeasible, with anchor; constraints | agent (`/epe-1-explore`) | the human accepts the matrix |
| 2 | `plan.md` + `tasks.md`: one test per criterion | agent (`/epe-2-plan`) | **`Status: APPROVED`** only when the human writes "plan approved" |
| 3 | `evidence.md` + `validation.md` | agent (`/epe-3-execute`) | PR, never merge |
| 4-5 | comments on the PR | reviewer (`/epe-4-review`, `/epe-5-apply`) | human gate |
| 6 | folder to `_archive/`, line in `CHANGELOG.md` | `/epe-6-archive` | after the merge |

`make epe-new SLUG=<slug>` opens the change folder and marks it active (`.epe/active`); `make epe-status` shows it.

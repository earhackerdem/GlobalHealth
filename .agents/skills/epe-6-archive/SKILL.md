---
name: epe-6-archive
description: Closes an EPE change as the LAST commit of its own PR, so code, specs, CHANGELOG and docs land in one merge. Moves the change folder to <changes_dir>/_archive/ (with engine openspec, `openspec archive` merges the delta specs), writes the changelog.d/ fragment, refreshes the skills and docs that asserted the previous state, closes related inbox items and points .epe/active at the archived folder. Fallback for a change merged before it was archived. Use when the user says "/epe-6-archive", "archive the change", "close it", and at the end of /epe-5-apply.
argument-hint: [change path; defaults to .epe/active]
---

# /epe-6-archive — close the change folder inside its own PR

**Default: the last commit of the change's PR.** It runs at the end of `/epe-5-apply`, after the fixes are green and
the exploratory pass is clean, and before the PR is handed to the human for validation and merge. If there is no
review, it runs at the end of `/epe-3-execute`, but only once the person you work with says there will be none. Then
code, specs, CHANGELOG and refreshed docs land in a single merge, and if the PR is not accepted, nothing does.
**Fallback**: the PR was merged before archiving. Archive on a `docs/archive-<slug>` branch with its own PR.
(Measured in GlobalHealth, 2026-10-20: 2 of 12 PRs were archive-only, one needed a cherry-pick and a rebase, and while
they waited, `main` had the new code with the old specs.)

With `engine: openspec`: step 2 is `openspec archive <id>` (merges the delta specs into `openspec/specs/` and moves
the folder to `openspec/changes/archive/<date>-<id>/`); the other steps are unchanged.

1. **When.** Default: the review is applied, the tests are truly green, and the exploratory pass is clean. Do not
   archive earlier: every later fix would edit the archived folder and the merged specs. Fallback: verify the merge
   (`gh pr view <n> --json state`). It can be paused: leave the change where it is and delete `.epe/active`.
2. `git mv <changes_dir>/<slug> <changes_dir>/_archive/<slug>`.
3. Changelog: one fragment `changelog.d/YYYY-MM-DD-<slug>.md` holding "- YYYY-MM-DD · <slug> · PR #n · what changed
   for the user". Do not render `CHANGELOG.md` here (`make changelog` runs on main or in a release PR): two change PRs
   that both render it conflict.
4. **Truth refresh**: search `.agents/skills/`, `docs/` and the README for what asserted the previous state
   (`grep -rn "<name|path|rule>"`) and update it. A skill that lies with confidence is debt.
5. `memory/inbox/`: close the items this change resolved (`status: done` and a `**Closure:**` line with the PR).
6. `.epe/active`. Default: point it at the archived folder, whose plan is still `Status: APPROVED`, so a fix that
   comes out of the human's validation can still edit code. The next `/epe-0-new` overwrites it. Fallback: delete
   it. Closing journal entry (one line is enough if there were no surprises).
7. Commit `docs: archive <slug>`. Default: on the change's branch, pushed, with the PR body saying the change is
   archived and where `validation.md` now lives. Fallback: PR from `docs/archive-<slug>`.

## If the validation sends the change back
Small fixes go on top, in the same PR. The archived folder is still unmerged, and its `evidence.md` and
`validation.md` are updated where they now live. A rework of scope reverts the archive commit (`git revert`) and
goes back to `/epe-2-plan`.

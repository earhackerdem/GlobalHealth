---
name: epe-6-archive
description: Closes an already-merged EPE change. Moves the change folder to <changes_dir>/_archive/, records the entry in CHANGELOG.md, refreshes the skills and docs that asserted the previous state, closes related inbox items and clears .epe/active. Use when the user says "/epe-6-archive", "archive the change", "it's merged, close it".
argument-hint: [change path; defaults to .epe/active]
---

# /epe-6-archive — close the change folder

With `engine: openspec`: step 2 is `openspec archive <id>` (merges the delta specs into `openspec/specs/` and moves
the folder to `openspec/changes/archive/`); steps 3–7 are unchanged.

1. Verify the PR is merged (`gh pr view <n> --json state`) or that the person you work with confirms it. No merge, no
   archiving (it can be paused: leave the change where it is and delete `.epe/active`).
2. `git mv <changes_dir>/<slug> <changes_dir>/_archive/<slug>`.
3. `CHANGELOG.md`: one entry "YYYY-MM-DD · <slug> · PR #n · what changed for the user".
4. **Truth refresh**: search `.agents/skills/`, `docs/` and the README for what asserted the previous state
   (`grep -rn "<name|path|rule>"`) and update it. A skill that lies with confidence is debt.
5. `memory/inbox.md`: close the rows this change resolved (✅ with an anchor to the PR).
6. Delete `.epe/active`. Closing journal entry (one line is enough if there were no surprises).
7. Commit `docs: archive <slug>`; PR or direct per the house flow (`AGENTS.md`).

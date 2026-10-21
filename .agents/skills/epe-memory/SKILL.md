---
name: epe-memory
description: Sweeps and updates memory before losing context (session end, compaction, belief change). First DELETES/CORRECTS what is stale in the agent's private memory and in the repo's memory/, then writes what is new, following the routing rule (what another person or session needs to read goes to the repo; private memory only holds how to work with this repo and this person). Use when the user says "/epe-memory", "save memories", "I'm about to compact", "note this for next time", or the compaction hook notifies.
---

# /epe-memory — first what lies, then what is missing

A memory session that only adds, degrades. Measured at origin (an earlier content harness, 2026-08-16): 3 of 13 private
memories were lying and were injected at every startup.

## Routing rule
| | repo `memory/` | agent's private memory |
|---|---|---|
| seen by the team / other sessions / the PR diff | yes | no |
| what goes there | one file per record: decisions (`decisions/`), verified facts (`research/`), verdicts (`closed/`), ideas (`inbox/`), what was done (`journal/`) | how to work with this repo and this person, corrected beliefs, open state to resume |
When in doubt, the repo.

## Procedure
0. If `~/.claude/projects/<slug>/compactions.jsonl` records unswept compactions, open the `transcript_path` it
   points to: compacting does not delete the transcript.
1. **Sweep what is stale**: `make memory-check` gives mechanical leads (broken links, nonexistent paths, closed PRs
   treated as live). Then, for each private memory: is it still true? Verify against the repo. Correct or delete.
   Same with `memory/inbox/` (close what is done: `status: done`) and `memory/decisions/` (mark Revised if it changed).
2. **Write what is new**, routed, one file each: decision → `decisions/D<n>-slug.md` (`make decision-next`); fact with
   source → `research/<topic>.md`; idea → `inbox/YYYY-MM-DD-slug.md`; work → `journal/`; way of working or corrected belief → private (one file per fact, with frontmatter and a line in
   `MEMORY.md`).
3. `make memory-swept` to record the sweep.
4. Finish with the count: corrected / deleted / new, and where each one ended up. If there are more files and none
   corrected, almost certainly nothing was swept.

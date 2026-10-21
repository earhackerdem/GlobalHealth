# The memory layer

`memory/` is the project's shared source of truth: the team sees it, other sessions see it, and it's reviewed in the
PR diff. The agent's private memory (`~/.claude/projects/<slug>/memory/`) meets none of the three, so it only keeps
**how to work with this repo and this person**. When in doubt, the repo.

## One record, one file
Every kind of record is a folder and every record is its own file in it. The journal was born that way (a monolith
conflicted at head and tail with concurrent sessions); since 0.4.0 the rest of `memory/` and the changelog follow,
because two branches that each append a row to the same file conflict on merge, and two branches that each add a
file never do (measured in GlobalHealth, 2026-10-20: a research PR and a feature PR conflicted on `inbox.md` and
`research.md`, and both could have taken the same decision id). Indexes are printed on demand, never committed.

| Folder | What it is | Why it exists (measured at origin) |
|---|---|---|
| `decisions/D<n>-slug.md` | lightweight ADR, never deleted, marked Revised; `make decision-next` gives the id | without it every session re-litigates; a decision applied to the content and not to the ADR spent two days saying the opposite |
| `research/<topic>.md` | facts with source, date and confidence, one topic per file | a lesson published "44% (JetBrains 2025)" from a record that cited blogs; the record rules |
| `journal/YYYY-MM-DD-slug.md` | what was done, one file per entry | the monolith conflicted at head and tail with concurrent sessions |
| `inbox/YYYY-MM-DD-slug.md` | half-formed ideas; leave as done / discarded / snoozed with a date; `make inbox` | there was nowhere for an idea to land before being decided |
| `closed/YYYY-MM-DD-slug.md` | already-triaged verdicts, injected verbatim into the finders via `make closed` | a review repeated nits triaged months earlier because the brief didn't carry them |
| `meta-improvements/YYYY-MM-DD-slug.md` | improvements to the harness and their verdict, rejections included | without it every retro repeats the previous one's menu |
| `../changelog.d/YYYY-MM-DD-slug.md` | one changelog fragment per archived change; `make changelog` renders `CHANGELOG.md` | every archive appended to the same file |

An entry is plain `key: value` frontmatter between two `---` lines (`date`, and `status`, or `state` for verdicts,
`id` for decisions) and a markdown body whose first line is the title. Each folder's README has the template. The
parser is `.claude/hooks/_memory.py`, shared by the hooks and the scripts. `make memory-check` reports what a
merge can still get wrong: two decision files with the same id, an unknown status, an old single file that came back,
a line of `CHANGELOG.md` written by hand.

`CHANGELOG.md` is rendered on the main branch or in a release PR, never inside a change PR: two change PRs that both
render it would conflict again.

## Coming from the single files
Projects created before 0.4.0 have `memory/inbox.md`, `closed.md`, `decisions.md`, `research.md`,
`meta-improvements.md` and `CHANGELOG.md`. `make harness-update` never touches `memory/`; every reader still parses
the old files, and `make doctor` says what to do: `make memory-migrate DRY_RUN=1`, read what it would write, then
`make memory-migrate`. It moves each record verbatim (a table row becomes a file whose body carries the same cells,
labelled with the column names), sends titles, legends and stray prose to the folder's README, and refuses to write
anything if a single non-empty line of the old files is not found in the new ones. An old citation
`research.md#<id>` points at `research/<id>.md`. Merge or rebase open PRs that touch memory first; a branch that
still edits an old file after the migration conflicts once (modify/delete), and re-running the migration after that
merge only adds what is new.

## Protocol
At start: README, decisions, inbox (the hook injects 3). A project may write its memory in any language, but the
markers the tools parse stay in English: the frontmatter keys and status values, `Status: APPROVED` in `plan.md`,
`NO-CLOSED:` in a subagent prompt. During: every request is a hypothesis; [VERIFIED] vs [OPINION/HYPE]. At the end:
your own journal entry; a decision or a fact of its own if something changed.

## Sweeping
`/epe-memory` starts by deleting and correcting what has expired (`make memory-check` gives mechanical leads), then
writes what's new. A memory session that only adds, degrades: 3 of 13 private memories lied at origin and were
injected on every startup. The `PreCompact` hook leaves a breadcrumb per compaction; compacting doesn't delete the
transcript. The private memory is optional: if everything it holds is already in `memory/`, deleting it loses nothing;
check file by file before doing so.

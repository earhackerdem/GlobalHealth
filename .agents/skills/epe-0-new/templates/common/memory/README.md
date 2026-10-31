# Project memory

Shared source of truth: the team sees it, other sessions see it, and it gets reviewed in the PR diff. Anything another
person or another session needs to read goes here, not in the agent's private memory. **When in doubt, the repo.**

**One record, one file.** Two branches that each append a row to the same file conflict on merge; two branches that
each add a file never do. So every kind of record is a folder, and each record is its own file in it. Indexes are
printed on demand and never committed (`make inbox`, `make closed`, `make changelog`).

| Folder | What it is | When |
|---|---|---|
| `decisions/D<n>-slug.md` | Decisions and their why (lightweight ADR). Never deleted: marked Revised. `make decision-next` gives the next id | Read **at the start**; write when deciding |
| `research/<topic>.md` | **Verified** facts with source, date and confidence, one topic per file. Avoids re-researching | Read before asserting; write when verifying |
| `journal/YYYY-MM-DD-slug.md` | What was done: who → intent → what was done → verification → debt | At the end of each piece of work (the Stop hook reminds you) |
| `inbox/YYYY-MM-DD-slug.md` | Half-formed ideas. Leave as done / discarded / snoozed with a date | When it comes up; the SessionStart hook shows up to 3 |
| `closed/YYYY-MM-DD-slug.md` | Review verdicts already triaged, so an adversarial review does not re-litigate | Before /epe-4-review (`make closed`); after the human gate |
| `meta-improvements/YYYY-MM-DD-slug.md` | Proposed improvements to the harness itself and their verdict, rejections included | Before /session-retro; when closing it |

Each folder's README says what an entry carries. Frontmatter is plain `key: value` lines between `---` lines; the
first line of the body is the title. `make memory-check` reports a duplicate decision id, an unknown status, or an
old single file (`inbox.md`…) that came back. An entry's frontmatter is also checked after each edit (`lint.py`)
and at the close (`check-journal.py`, whatever wrote the file; only the entries the branch or the working tree
touched), with the same rules.

## Session protocol
**At the start**: read this README, `decisions/` and the inbox (the hook already injects 3; `make inbox` lists all).
**During**: treat every request as a hypothesis to verify; distinguish [VERIFIED] from [OPINION/HYPE]. **At the
end**: a journal entry in its own file; a new decision or fact gets its own file too.

## Expiry
Facts in `research/` carry a date; if they are older than ~3 months and market-sensitive, re-verify.

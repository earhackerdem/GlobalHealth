# The memory layer

`memory/` is the project's shared source of truth: the team sees it, other sessions see it, and it's reviewed in the
PR diff. The agent's private memory (`~/.claude/projects/<slug>/memory/`) meets none of the three, so it only keeps
**how to work with this repo and this person**. When in doubt, the repo.

| File | What it is | Why it exists (measured at origin) |
|---|---|---|
| `decisions.md` | lightweight ADR D1…Dn, never deleted, marked Revised | without it every session re-litigates; a decision applied to the content and not to the ADR spent two days saying the opposite |
| `research.md` | facts with source, date and confidence | a lesson published "44% (JetBrains 2025)" from a record that cited blogs; the record rules |
| `journal/YYYY-MM-DD-slug.md` | one file per entry | the monolith conflicted at head and tail with concurrent sessions; one file per entry merges cleanly |
| `inbox.md` | inbox, items leave as ✅/❌/💤 | the rest are verdict indexes; there was nowhere for an idea to land before being decided |
| `closed.md` | already-triaged verdicts, short, injected verbatim into the finders | a review repeated nits triaged months earlier because the brief didn't carry them |
| `meta-improvements.md` | improvements to the harness and their verdict, rejections included | without it every retro repeats the previous one's menu |

## Protocol
At start: README, decisions, inbox (the hook injects 3). A project may write its memory in any language, but the
markers the hooks parse stay in English: `## Open` / `## Closed` and the `Date` column in `inbox.md`, `Status: APPROVED`
in `plan.md`, `NO-CLOSED:` in a subagent prompt. During: every request is a hypothesis; [VERIFIED] vs
[OPINION/HYPE]. At the end: your own journal entry; decisions or research if something changed.

## Sweeping
`/epe-memory` starts by deleting and correcting what has expired (`make memory-check` gives mechanical leads), then
writes what's new. A memory session that only adds, degrades: 3 of 13 private memories lied at origin and were
injected on every startup. The `PreCompact` hook leaves a breadcrumb per compaction; compacting doesn't delete the
transcript. The private memory is optional: if everything it holds is already in `memory/`, deleting it loses nothing;
check file by file before doing so.

# Inbox

Entry is cheap (one file: what and why it matters, no research, no decision). Exit is mandatory: done (anchor to
the PR or commit), discarded (reason), snoozed until YYYY-MM-DD. Nothing is deleted. An inbox item is not a
task: if the person you work with doesn't mention it, it is not started.

## Writing an entry
One file per item, `memory/inbox/YYYY-MM-DD-slug.md` (the date it came up, a few words of the title):

```
---
date: 2026-10-20
status: open
---
<What, in one line: this is the title the hook shows>

**Why it matters:** …
```
`status` is one of `open` · `snoozed YYYY-MM-DD` (hidden until that day) · `done` · `discarded`. Closing an item
changes its `status` and adds a `**Closure:**` line with the anchor or the reason; the file stays.

# Project memory

Shared source of truth: the team sees it, other sessions see it, and it gets reviewed in the PR diff. Anything another
person or another session needs to read goes here, not in the agent's private memory. **When in doubt, the repo.**

| File | What it is | When |
|---|---|---|
| `decisions.md` | Decisions and their why (lightweight ADR, D1…Dn). Never deleted: marked Revised. | Read **at the start**; write when deciding |
| `research.md` | **Verified** facts with source, date and confidence. Avoids re-researching and re-litigating. | Read before asserting; write when verifying |
| `journal/YYYY-MM-DD-slug.md` | One file per entry: who → intent → what was done → verification → debt | At the end of each piece of work (the Stop hook reminds you) |
| `inbox.md` | Inbox: half-finished ideas. Leaves as ✅ done / ❌ discarded / 💤 snoozed with a date | When it comes up; the SessionStart hook shows up to 3 |
| `closed.md` | Review verdicts already triaged, so an adversarial review does not re-litigate | Before /epe-4-review; after the human gate |
| `meta-improvements.md` | Proposed improvements to the harness itself and their verdict, rejections included | Before /session-retro; when closing it |

## Session protocol
**At the start**: read this README, `decisions.md` and `inbox.md` (the hook already injects 3). **During**: treat every
request as a hypothesis to verify; distinguish [VERIFIED] from [OPINION/HYPE]. **At the end**: journal entry in your
own file; update `decisions.md` or `research.md` if there was a new decision or fact.

## Expiry
Facts in `research.md` carry a date; if they are older than ~3 months and market-sensitive, re-verify.

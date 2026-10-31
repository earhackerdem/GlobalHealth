# Meta-improvements — proposals for the harness itself and their verdict

Includes rejections: a retro that repeats the previous one's menu manufactures friction. Before proposing with
/session-retro, read this; a rejected proposal does not come back without new evidence.

## Writing an entry
One file per proposal, `memory/meta-improvements/YYYY-MM-DD-slug.md`:

```
---
date: 2026-10-20
status: proposed
---
<The proposal, in one line>

**Why:** …
**Where it lives:** <PR, file> (once it does)
```
`status` is one of `proposed` · `accepted` · `rejected` · `applied`. `applied` is written in the **same PR** that applies the
change, never in a later commit: in the template, the C-NN PR; in a project, the `make harness-update` PR that brings it, which
lists the entries whose «Where it lives» line cites the version or C-NN it installs (`make doctor` flags one left behind). `make harness-harvest` compares these against
the template's.

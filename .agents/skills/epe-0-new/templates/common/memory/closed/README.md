# Closed — review verdicts already triaged

Injected verbatim into the finders and validators of /epe-4-review so they don't re-litigate what was decided:
`make closed` prints this folder as one document to paste.

States: 🔒 frozen (not reported; human decision or reproduced false positive) · ↩️ reopenable (only with new
evidence, citing the entry) · ⏸️ deferred (goes to debt, not to findings) · 🧩 partial (only the missing instances)

## Writing an entry
One file per verdict, `memory/closed/YYYY-MM-DD-slug.md`:

```
---
date: 2026-10-20
state: frozen
anchor: journal: 2026-10-20 · <journal title>
---
<The finding, in one line>

**Verdict and why:** …
```
`state` is one of `frozen` · `reopenable` · `deferred` · `partial`.

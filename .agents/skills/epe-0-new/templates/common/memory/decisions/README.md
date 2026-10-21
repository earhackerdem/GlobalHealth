# Project decisions (lightweight ADR)

States: Accepted · Revised · Superseded · Proposed · Discarded. Never deleted; if they change, mark them Revised with
a date and link the new one.

## Writing an entry
One file per decision, `memory/decisions/D<n>-slug.md`. `make decision-next` prints the next free id; if two
branches took the same one, `make memory-check` says so after the merge and the later one is renumbered.

```
---
id: D2
date: 2026-10-20
status: accepted
---
## D2 — <Title>
- **Status:** Accepted · 2026-10-20 · decided by: <name (role)>
- **Decision:** …
- **Why:** …
- **Discarded alternatives:** …
```

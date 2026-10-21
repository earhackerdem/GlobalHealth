# Changelog fragments

One file per archived change, `changelog.d/YYYY-MM-DD-slug.md`, holding the entry exactly as it reads in the
changelog (`- YYYY-MM-DD · <slug> · PR #n · what changed for the user`). `/epe-6-archive` writes it inside the
change's PR. `CHANGELOG.md` is rendered from these fragments, newest first, followed by `_legacy.md` (the text from
before fragments): `make changelog`, run on the main branch or in a release PR, never inside a change PR (two change
PRs that both render it would conflict again).

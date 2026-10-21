# Updating the harness inside a project

The agentic layer a project receives from `make new` or `make adopt` is a **vendored dependency**: the harness owns
those files, the project owns everything else. Updating is explicit, content-compared and recorded.

## The line of ownership
| Harness-owned (replaced by an update) | Seeded once, then the project's | Never touched |
|---|---|---|
| `.agents/` (skills, rules), `.claude/hooks`, `.claude/agents`, `.claude/settings.json`, `.cursor/`, `.github/hooks`, `copilot-instructions.md`, `.vscode/`, `scripts/`, `docs/*.md` (`docs/harness/` in adopt mode), `Makefile` (`harness.mk`), `AGENTS.md`, `CLAUDE.md` | `harness.json` (except `harness_version`), `README.md`, `.github/pull_request_template.md`, `.gitignore`, `memory/` seeds | `memory/`, `changes/`, `product/`, `.epe/`, `.claude/profile.env`, `project.mk` (your `make` recipes, included by the harness Makefile), your code, your own skills and hooks |

`.agents/harness-manifest.json` records what the harness placed (source path and sha256 per file) and the version.
A file is owned only if the harness placed it and it equalled the source at install: a file `make adopt` skipped
because you already had it is never owned.

## Commands (run inside the project; `SRC` is a checkout of the template)
```bash
make harness-status SRC=../harness           # the plan, nothing written
make harness-update SRC=../harness           # apply
make harness-update SRC=../harness FORCE=1   # also overwrite forks, leaving <file>.harness-bak
```
The updater runs **from the template** (`$(SRC)/scripts/harness-sync.py`), so it is as new as the layer it brings.

## What happens to each file
| State | Meaning | Action |
|---|---|---|
| up-to-date | equal upstream | nothing |
| update | you never touched it, upstream changed | overwritten |
| add / remove | new upstream / retired upstream and untouched locally | copied / deleted |
| forked | you edited it, upstream did not change | kept, listed; stays a fork across updates |
| conflict | you edited it **and** upstream changed | kept, listed with the `diff` to run; exit 1 until you resolve it |
| unmanaged | exists locally, never owned | skipped |

`AGENTS.md` is special: the body of `<!-- harness:context -->…<!-- /harness:context -->` is yours and survives the
update; editing the rules outside the block makes the file a fork. In adopt mode the appended `<!-- harness:rules -->`
block in your own `AGENTS.md`/`CLAUDE.md` is not rewritten (it only points to `docs/harness/`).

## Updating to 0.4.0: memory becomes one file per entry
The update never touches `memory/`, and every reader keeps parsing the old single files, so nothing breaks the day
you update. `make doctor` then warns once per old file. Migrate in its own PR, after merging the open PRs that touch
memory: `make memory-migrate DRY_RUN=1`, read what it would write, `make memory-migrate`, check with `make inbox`,
`make closed` and `make memory-check` (docs/memory.md § Coming from the single files).

## The rule that makes this work
In a project, **harness-owned files are not edited in place**. An improvement goes to `memory/meta-improvements/`,
then upstream to the template, and comes back with the next update. A project that needs a different hook forks it
knowingly: the manifest will list it as forked forever, which is the honest state. After an update, run `make doctor`
and record it as one small change folder with a journal entry: it is a change to the repo like any other.

## What the two frameworks we looked at do (research 2026-10-08, `memory/research/updates.md`)
OpenSpec: *"generated files are OpenSpec's to own — keep your own instructions elsewhere"*; content comparison, drift
overwritten with a reason. BMAD: *"Updates do not touch your files, and you do not edit installed files"*; customisation
in side files. Neither keeps a fork as a first-class state nor records the update as a reviewable change; this harness
does both.

# Flavors: development and content

The harness is the same; what changes is **what counts as `code`** and **what verifying means**. `harness.json` →
`flavor` decides which templates `make epe-new` uses and which extra skill is recommended.

| | development | content |
|---|---|---|
| typical `code` | `src/`, `app/`, `lib/`, `packages/` | `content/` (posts, lessons, scripts) |
| `tests` (barrier paths) | `tests/`, `test/`, `spec/`, `__tests__/` or globs | empty |
| Input | user story with AC in Gherkin | brief: audience, goal, core message, AC about the reader |
| Explore | what the repo and its dependencies already do; platform constraints | what has already been said; dated primary sources; confidentiality boundary |
| One test per criterion | unit, integration, e2e, manual validation | cold reader, style checklist, source verification, validation by whoever approves |
| Truly green | 0 failures, 0 errors, 0 skipped | cold reader with no real stumbles; figures with the authority of their record |
| Who executes a task | `single` for small tickets (red → green by the orchestrator, `test:` commit first); `tester` → `implementer` agents for tickets with 3+ criteria or 2+ files (`harness.json → roles`), barrier by role (`guard-tests`) and by git (`make tdd-check`); `parallel` only with an interface contract | writer + `cold-reader`; no split |
| Extra skill | none (the stack's, if the project adds them) | `produce-content` |
| Own artifact | `CHANGELOG.md` (from `changelog.d/`) | `content/STYLE.md` (voice, language, length, what's forbidden) |
| Product layer (optional) | brief → PRD → technical brief (stack, NFR budget) | brief = editorial line; PRD = editorial plan with epics as series; technical brief = channels, formats, cadence budget |

`mixed` is for the mother template: it brings both template families and no paths in `code`.

## Adding a flavor
New folder at `.agents/skills/epe-0-new/templates/<flavor>/` with the six templates, and a row here.
`scripts/epe-new.sh` only recognizes `development` and `content`: add the third one there.

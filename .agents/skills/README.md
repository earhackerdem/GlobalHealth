# Harness skills (`.agents/skills/`)

**All** skills live here, in the standard [agentskills.io](https://agentskills.io) format (a folder with a
`SKILL.md`). Cursor, VS Code (Copilot) and Antigravity read this directory directly; Claude Code only reads
`.claude/skills/`, so each skill has a symlink there (`make skills-link` regenerates them). What each IDE reads:
`docs/ides.md`.

| Skill | Phase | Purpose |
|---|---|---|
| `triage` | before 0 | which rung of the calibration ladder a request needs; one message, no files; verdict goes to the story's `Triage:` line |
| `epe-0-new` | 0 | opens a change folder with `story.md` (per-flavor templates in `templates/`) |
| `epe-1-explore` | Explore | what already exists? what do the sources say? criterion × coverage matrix; no planning, no editing |
| `epe-2-plan` | Plan | `plan.md` with one test per criterion; "plan approved" gate |
| `epe-3-execute` | Execute | implements/produces in increments with demonstrable verification, evidence, validation, journal, PR |
| `epe-4-review` | Review | adversarial review with independent finders and validators; edits nothing; human gate |
| `epe-5-apply` | Apply | applies only what was approved; the fixer bounces back, never discards |
| `epe-6-archive` | Archive | closes the change folder as the last commit of its PR (fallback: after a merge) |
| `epe-autopilot` | 0 → Archive | the whole cycle for one request under a delegation the invocation grants: gates closed by the agent and written down, one review round, archive, report of assumptions; merge stays human |
| `epe-memory` | cross-cutting | sweeps memory (first what lies, then what is missing) |
| `session-retro` | cross-cutting | measured retro over the transcript; "nothing to standardize" is a legitimate result |
| `produce-content` | content flavor | content production core: primary sources, [VERIFIED]/[OPINION], citers, cold reader |
| `product-brief` | product layer (optional) | one-page brief; says whether a PRD is worth it |
| `product-prd` | product layer (optional) | technology-agnostic PRD with FR-/NFR- ids and epics; splits into change folders |
| `product-tech-brief` | product layer (optional) | team and existing stack first, then candidate stacks, then the NFR budget every change inherits; ADRs |
| `codebase-context` | brownfield entry | verifies conventions and pitfalls into an `AGENTS.md` block; never documents the system; opens one bounded change |

Third-party skills: as published by their author, name included, with origin and hash in `skills-lock.json` if added.
